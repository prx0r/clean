#!/usr/bin/env python3
"""
VPS Render Worker — claims render tasks from the factory and executes them.
Uses `requests` library for reliable Bearer token auth.

Run:
  pip install requests boto3
  R2_KEY=xxx R2_SECRET=xxx RENDER_TOKEN=dev-token python3 scripts/vps-render-worker.py
"""
import json, os, subprocess, sys, time
from pathlib import Path

import requests
import boto3
from botocore.config import Config

API = os.environ.get("FACTORY_API", "https://platinum-factory.tradesprior.workers.dev")
TOKEN = os.environ.get("RENDER_TOKEN", "").strip()
WORK_DIR = Path("/tmp/platinum-render-tasks")
WORK_DIR.mkdir(parents=True, exist_ok=True)

if not TOKEN:
    print("FATAL: RENDER_TOKEN not set")
    sys.exit(1)

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "PlatinumRenderer/1.0",
})

s3 = boto3.client("s3",
    endpoint_url=os.environ.get("R2_ENDPOINT", "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com"),
    aws_access_key_id=os.environ.get("R2_KEY", ""),
    aws_secret_access_key=os.environ.get("R2_SECRET", ""),
    config=Config(signature_version="s3v4"))


def api_get(path):
    r = session.get(f"{API}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(path, data):
    r = session.post(f"{API}{path}", json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def fail_task(tid, code, msg):
    api_post(f"/render-tasks/{tid}/complete", {"status": "failed", "error": f"[{code}] {msg}"})
    print(f"  ❌ {code}: {msg[:100]}")


def execute(task):
    tid = task["task_id"]
    manifest = json.loads(task.get("input_manifest_json", "{}"))
    # Try render_code_r2 (new), then render_script.r2_key (legacy)
    r2k = manifest.get("render_code_r2", "")
    if not r2k and isinstance(manifest.get("render_script"), dict):
        r2k = manifest["render_script"].get("r2_key", "")

    if not r2k:
        fail_task(tid, "NO_SCRIPT", f"no render_code_r2/render_script in manifest keys: {list(manifest.keys())}")
        return

    td = WORK_DIR / tid
    td.mkdir(parents=True, exist_ok=True)
    sp = td / "render_pack.py"

    try:
        s3.download_file("factory-assets", r2k, str(sp))
    except Exception as e:
        fail_task(tid, "DOWNLOAD_FAILED", str(e))
        return

    # Extract render_pack_py from code_review.json wrapper
    try:
        with open(sp) as f:
            data = json.load(f)
        code = data.get("render_pack_py") or data.get("render_script") or data.get("code") or ""
        if code:
            with open(td / "render_pack.py", "w") as f:
                f.write(code)
            sp = td / "render_pack.py"
    except json.JSONDecodeError:
        pass  # Already a raw .py file

    # Syntax check
    r = subprocess.run([sys.executable, "-m", "py_compile", str(sp)],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        fail_task(tid, "SYNTAX_ERROR", r.stderr[:300])
        return

    # Execute with heartbeats
    proc = subprocess.Popen([sys.executable, str(sp)], cwd=str(td),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while proc.poll() is None:
        try:
            api_post(f"/render-tasks/{tid}/heartbeat", {})
        except Exception:
            pass
        time.sleep(20)

    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        fail_task(tid, "RENDER_FAILED", stderr[-500:] if stderr else "unknown")
        return

    # Find and upload outputs
    mp4s = sorted(td.rglob("*.mp4"))
    if not mp4s:
        fail_task(tid, "NO_OUTPUT", "renderer produced no MP4 files")
        return

    # Upload to slug-based path so video endpoint can serve it
    slug = manifest.get("slug", tid)
    stage = manifest.get("stage", "draft_render")
    output_dir = manifest.get("outputDir", f"renders/{slug}")

    outputs = {"shots_rendered": 0, "files": []}
    for mp4 in mp4s:
        if mp4.stem in ("draft", "final", "shot"):
            dst = f"{output_dir}/{mp4.name}"
        else:
            dst = f"{output_dir}/{mp4.name}"
        try:
            s3.upload_file(str(mp4), "factory-assets", dst)
            outputs["shots_rendered"] += 1
            outputs["files"].append(dst)
        except Exception as e:
            print(f"  ⚠ upload failed for {mp4.name}: {e}")

    # Upload contact sheets and motion strips to preview path
    for png in td.rglob("*.png"):
        try:
            s3.upload_file(str(png), "factory-assets", f"{output_dir}/preview/{png.name}")
        except Exception:
            pass

    api_post(f"/render-tasks/{tid}/complete", {"status": "completed", "outputs": outputs})
    print(f"  ✅ {outputs['shots_rendered']} files")


def main():
    print(f"VPS Render Worker starting...")
    print(f"  API: {API}")
    print(f"  Token: {TOKEN[:8]}...")
    print()

    while True:
        try:
            resp = session.get(f"{API}/render-tasks/claim", timeout=30)
            if resp.status_code == 409:
                time.sleep(2)
                continue
            resp.raise_for_status()
            task = resp.json()
            if task.get("task_id"):
                execute(task)
            else:
                print(".", end="", flush=True)
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"\n  ⚠ {e}")
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopped.")
            break


if __name__ == "__main__":
    main()
