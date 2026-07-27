#!/usr/bin/env python3
"""
Standalone scene pack generator.

Reads storyboard and visual contract from R2,
calls DeepSeek with rate limiting,
validates response locally,
uploads render_pack.py and code_review.json to R2,
can advance the job if --advance flag is set.

Usage:
  python3 scripts/generate-scene-pack.py <slug> [--advance]
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

API_BASE = os.environ.get("FACTORY_API", "https://platinum-factory.tradesprior.workers.dev")
OPENCODE_KEY = os.environ.get("OPENCODE_API_KEY", "sk-SDjjQ8NtTdpM2OmWl3GXDrPlhcQiLvZln60mSVVcJQ3rkg7trYHQoLKshcKSeg0Y")

# R2 S3-compatible credentials
R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com")
R2_KEY = os.environ.get("R2_KEY", "a86c6cbfdc0fd2725809b7ad414e4e25")
R2_SECRET = os.environ.get("R2_SECRET", "92d535f8d85753504a63c6ac5b408b44b311e658cc7b1759a05ba277149c48d9")

import boto3
from botocore.config import Config

s3 = boto3.client("s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_KEY,
    aws_secret_access_key=R2_SECRET,
    config=Config(signature_version="s3v4"))


def r2_get(key):
    obj = s3.get_object(Bucket="factory-assets", Key=key)
    return obj["Body"].read().decode()


def r2_put(key, body):
    if isinstance(body, str):
        body = body.encode()
    s3.put_object(Bucket="factory-assets", Key=key, Body=body)


def call_deepseek(prompt, max_retries=3):
    """Call DeepSeek with curl (urllib gives 403)."""
    for attempt in range(max_retries):
        try:
            payload = json.dumps({
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "You are a PIL scene function generator. Return only valid Python code."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 8000,
                "temperature": 0.3
            })
            Path("/tmp/deepseek-payload.json").write_text(payload)
            result = subprocess.run(["curl", "-s", "-X", "POST",
                "https://opencode.ai/zen/go/v1/chat/completions",
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {OPENCODE_KEY}",
                "-d", "@/tmp/deepseek-payload.json"], capture_output=True, text=True, timeout=120)
            resp = json.loads(result.stdout)
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            wait = (attempt + 1) * 5
            print(f"  API error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)
    raise RuntimeError("DeepSeek API failed after all retries")


def generate(slug):
    prefix = f"content/publishing/renders/{slug}/v1/"

    print(f"1. Reading artifacts for {slug}...")
    storyboard = json.loads(r2_get(prefix + "storyboard.json"))
    shots = storyboard if isinstance(storyboard, list) else storyboard.get("shots", [])
    print(f"   {len(shots)} shots")

    try:
        contract = json.loads(r2_get(prefix + "visual_contract.json"))
        materials = ", ".join(contract.get("materials", [])[:5])
    except Exception:
        materials = "parchment, ink, gold, lapis, silver"

    print(f"   Materials: {materials}")

    print(f"2. Calling DeepSeek...")
    prompt = f"""Generate PIL scene functions for ALL {len(shots)} shots.

Storyboard:
{json.dumps(shots)[:12000]}

Design each shot using: {materials}
Palette: PARCHMENT=(245,242,238) INK=(40,40,42) GOLD=(180,150,60)
CRIMSON=(160,55,55) LAPIS=(55,75,120) SILVER=(180,188,195)
DARK=(50,52,55) WHITE=(250,248,244) VOID=(26,29,35)

Each function: def scene_sXXX(ctx, t, u):
Three phases: u<0.33 initial, 0.33-0.66 transform, >0.66 resolved
Mature at u=0.72

End with: SCENE_FUNCTIONS = [all function names]
Return ONLY Python code."""

    code = call_deepseek(prompt)

    # Clean response
    clean = code.replace("```python", "").replace("```", "").strip()
    funcs = re.findall(r"def (scene_\w+(?:_\w+)?)", clean)
    if "SCENE_FUNCTIONS" not in clean:
        clean += f'\n\nSCENE_FUNCTIONS = [{", ".join(funcs)}]'

    # Validate
    n_funcs = len(re.findall(r"def scene_", clean))
    n_shots = len(shots)
    print(f"3. Validation: {n_funcs} functions for {n_shots} shots")
    assert n_funcs >= max(3, n_shots // 2), f"Too few functions: {n_funcs} < {n_shots // 2}"

    has_scene = "def scene_" in clean
    has_sc_list = "SCENE_FUNCTIONS" in clean
    print(f"   Has scene functions: {has_scene}")
    print(f"   Has SCENE_FUNCTIONS: {has_sc_list}")

    # Upload
    print(f"4. Uploading to R2...")
    code_review = json.dumps({
        "render_pack_py": clean,
        "code_review_json": {"functions_found": n_funcs, "source": "generate-scene-pack.py"}
    })
    r2_put(prefix + "code_review.json", code_review)
    r2_put(prefix + "render_pack.py", clean)
    print(f"   ✅ {len(clean)} chars, {n_funcs} functions")

    return n_funcs


def advance_job(slug):
    """Call /advance to move past code_review."""
    payload = json.dumps({"slug": slug})
    Path("/tmp/advance-payload.json").write_text(payload)
    result = subprocess.run(["curl", "-s", "-X", "POST",
        f"{API_BASE}/advance",
        "-H", "Content-Type: application/json",
        "-d", "@/tmp/advance-payload.json"], capture_output=True, text=True, timeout=30)
    resp = json.loads(result.stdout)
    r = resp.get("result", resp.get("error", "?"))
    ns = resp.get("next_stage", "?")
    print(f"   /advance: {r} -> {ns}")
    return r == "passed"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/generate-scene-pack.py <slug> [--advance]")
        sys.exit(1)

    slug = sys.argv[1]
    do_advance = "--advance" in sys.argv

    try:
        n = generate(slug)
        print(f"✅ Generation complete: {n} functions")

        if do_advance:
            print("5. Advancing job...")
            if advance_job(slug):
                print("✅ Job advanced past code_review")
            else:
                print("❌ Advance failed")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)
