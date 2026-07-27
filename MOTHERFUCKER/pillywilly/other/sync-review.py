#!/usr/bin/env python3
"""Find all rendered video packs and upload to R2 for review."""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).parent.parent
R2_BUCKET = os.environ.get("R2_BUCKET", "blog-video-assets")
R2_PREFIX = "renders"
R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
REVIEW_INDEX = ROOT / "data" / "review" / "index.json"

def safe_meta(d):
    mf = d / "scene_manifest.json"
    if mf.exists():
        try:
            d2 = json.loads(mf.read_text())
            return d2 if isinstance(d2, dict) else {}
        except: pass
    for sub in d.iterdir():
        if sub.is_dir():
            mf = sub / "scene_manifest.json"
            if mf.exists():
                try:
                    d2 = json.loads(mf.read_text())
                    return d2 if isinstance(d2, dict) else {}
                except: pass
    return {}

packs = []
ref_dir = ROOT / "video-templates" / "animation-references"
if ref_dir.exists():
    for d in ref_dir.iterdir():
        if not d.is_dir(): continue
        mp4s = list(d.rglob("*.mp4"))
        for mp4 in mp4s:
            if mp4.parent.name == "scenes": continue
            vid_id = mp4.relative_to(ref_dir).with_suffix("").name
            meta = safe_meta(d)
            title = meta.get("title", vid_id.replace("_", " ").title())
            scenes = len(meta.get("scenes", []))
            dur = meta.get("duration_seconds", 0)
            packs.append({"id": f"ref-{vid_id}", "title": title, "mp4": mp4, "scenes": scenes or "?", "duration": round(dur) if dur else "?"})

spanda_mp4 = ROOT / "scripts" / "renderer" / "spanda_output_pack" / "spanda_animation.mp4"
if spanda_mp4.exists():
    meta = safe_meta(spanda_mp4.parent)
    packs.append({"id": "spanda", "title": meta.get("title", "Spanda — The Hidden Pulse"), "mp4": spanda_mp4, "scenes": len(meta.get("scenes", [])), "duration": round(meta.get("duration_seconds", 0))})

def upload(r2_key):
    env = os.environ.copy()
    env.update({"AWS_ACCESS_KEY_ID": os.environ.get("R2_ACCESS_KEY", ""), "AWS_SECRET_ACCESS_KEY": os.environ.get("R2_SECRET_KEY", "")})
    r = subprocess.run(["aws", "s3", "cp", str(p["mp4"]), f"s3://{R2_BUCKET}/{r2_key}", "--endpoint-url", R2_ENDPOINT], capture_output=True, text=True, timeout=120, env=env)
    if r.returncode != 0:
        print(f"\n  aws error: {r.stderr.strip()[:100]}", flush=True)
    return r.returncode == 0

index = []
for p in packs:
    r2_key = f"{R2_PREFIX}/{p['id']}/{p['mp4'].name}"
    print(f"Uploading {p['id']}...", end=" ", flush=True)
    if upload(r2_key):
        print("OK", flush=True)
    else:
        print("SKIP", flush=True)
        continue
    index.append({"id": p["id"], "title": p["title"], "mp4Key": r2_key, "duration": p["duration"] if isinstance(p["duration"], (int,float)) else 0, "scenes": p["scenes"] if isinstance(p["scenes"], (int,float)) else 0, "status": "draft", "avgRating": None})

REVIEW_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False))
print(f"\nDone: {len(index)} videos in review index")
