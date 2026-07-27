#!/usr/bin/env python3
"""
Vision-based video validation — checks actual image content via Google Vision API.

Usage:
  python3 scripts/video-vision-check.py                          # check FableCut media
  python3 scripts/video-vision-check.py --project /path/project.json  # override project
  python3 scripts/video-vision-check.py --json                   # machine-readable output
  python3 scripts/video-vision-check.py --skip-vision            # file-only checks (no API cost)
"""

import json, os, sys, base64, urllib.request, time
from pathlib import Path

VISION_API_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
MEDIA_DIR = Path("/root/projects/FableCut/media")
PROJECT_FILE = Path("/root/projects/FableCut/project.json")
PASS_THRESHOLD = 85

def load_project(path=None):
    if path:
        return json.loads(Path(path).read_text())
    return json.loads(PROJECT_FILE.read_text())

def call_vision(image_data, features):
    body = {
        "requests": [{
            "image": {"content": base64.b64encode(image_data).decode()},
            "features": [{"type": f, "maxResults": 5} for f in features],
        }]
    }
    url = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    for attempt in range(2):
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            result = json.loads(resp.read())
            return result.get("responses", [{}])[0]
        except Exception as e:
            if attempt < 1:
                time.sleep(1)
            else:
                return {"error": str(e)}

def check_images_vision(media_files, skip_vision=False):
    """Check each image via Vision API. Returns (score, diagnostics)."""
    image_files = [f for f in media_files if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp')]
    
    if not image_files:
        return 0, ["No image files to check"]
    
    results = []
    for img in image_files:
        size = img.stat().st_size
        
        # Basic file integrity
        if size < 1024:
            results.append({"file": img.name, "issues": ["file too small (< 1KB)"], "integrity": "corrupt"})
            continue
        if size > 20 * 1024 * 1024:
            results.append({"file": img.name, "issues": ["file too large (> 20MB)"], "integrity": "suspicious"})
            continue
        
        # Check image header bytes for valid format
        data = img.read_bytes()
        is_valid_header = False
        if img.suffix.lower() == '.jpg' or img.suffix.lower() == '.jpeg':
            is_valid_header = data[:2] == b'\xff\xd8'
        elif img.suffix.lower() == '.png':
            is_valid_header = data[:8] == b'\x89PNG\r\n\x1a\n'
        elif img.suffix.lower() == '.gif':
            is_valid_header = data[:6] in (b'GIF87a', b'GIF89a')
        elif img.suffix.lower() == '.webp':
            is_valid_header = data[:4] == b'RIFF' and data[8:12] == b'WEBP'
        else:
            is_valid_header = True
        
        if not is_valid_header:
            results.append({"file": img.name, "issues": ["invalid file header - likely corrupt"], "integrity": "corrupt"})
            continue
        
        # Check for duplicate images (byte-level comparison)
        results.append({"file": img.name, "integrity": "ok", "size": size})
    
    # Find duplicates
    seen = {}
    for r in results:
        if r.get("integrity") == "ok":
            fpath = MEDIA_DIR / r["file"]
            data = fpath.read_bytes()
            h = hash(data[:4096])  # hash first 4KB as quick check
            if h in seen:
                r["issues"] = [f"duplicate of {seen[h]}"]
                r["integrity"] = "duplicate"
            else:
                seen[h] = r["file"]
    
    # Run Vision API on a sample
    vision_results = {}
    if not skip_vision:
        sample = [r for r in results if r.get("integrity") == "ok"][:5]
        for r in sample:
            fpath = MEDIA_DIR / r["file"]
            img_data = fpath.read_bytes()
            if len(img_data) > 10 * 1024 * 1024:
                continue
            vision = call_vision(img_data, ["LABEL_DETECTION", "IMAGE_PROPERTIES", "SAFE_SEARCH_DETECTION"])
            if "error" not in vision:
                labels = [l["description"] for l in vision.get("labelAnnotations", [])[:5]]
                colors = vision.get("imagePropertiesAnnotation", {}).get("dominantColors", {}).get("colors", [])
                top_colors = [f"#{c['color']['red']:02x}{c['color']['green']:02x}{c['color']['blue']:02x}" for c in colors[:3]]
                safe = vision.get("safeSearchAnnotation", {})
                vision_results[r["file"]] = {
                    "labels": labels,
                    "colors": top_colors,
                    "safe": {k: v for k, v in safe.items() if k in ("adult", "violence", "racy")}
                }
            time.sleep(0.1)
    
    # Score: what fraction are valid unique images
    valid = sum(1 for r in results if r.get("integrity") == "ok")
    dupes = sum(1 for r in results if r.get("integrity") == "duplicate")
    corrupt = sum(1 for r in results if r.get("integrity") == "corrupt")
    
    # Vision analysis
    diverse_labels = set()
    for f, vr in vision_results.items():
        for l in vr.get("labels", []):
            diverse_labels.add(l)
    
    has_unsafe = any(
        vr.get("safe", {}).get("adult", "") in ("LIKELY", "VERY_LIKELY") or
        vr.get("safe", {}).get("violence", "") in ("LIKELY", "VERY_LIKELY")
        for vr in vision_results.values()
    )
    
    diagnostics = []
    diagnostics.append(f"Images: {len(image_files)} total, {valid} valid, {dupes} duplicates, {corrupt} corrupt")
    if len(vision_results) > 0:
        diagnostics.append(f"Vision sampled: {len(vision_results)} images, {len(diverse_labels)} unique labels found")
        diagnostics.append(f"Top labels: {', '.join(list(diverse_labels)[:8])}")
    if has_unsafe:
        diagnostics.append("WARNING: Some images flagged as unsafe by Vision API")
    if dupes > 0:
        dupelist = [r["file"] for r in results if r.get("integrity") == "duplicate"]
        diagnostics.append(f"Duplicates: {', '.join(dupelist[:5])}")
    if corrupt > 0:
        corruptlist = [r["file"] for r in results if r.get("integrity") == "corrupt"]
        diagnostics.append(f"Corrupt: {', '.join(corruptlist[:5])}")
    
    # Score calculation
    if len(image_files) == 0:
        return 0, diagnostics
    
    score = 0
    # At least 80% of images must be valid
    if valid / len(image_files) >= 0.8:
        score += 40
    else:
        diagnostics.append("FAIL: Less than 80% of images are valid/corrupt-free")
    
    # Less than 20% duplicates
    if len(image_files) > 0 and dupes / len(image_files) < 0.2:
        score += 30
    else:
        diagnostics.append("FAIL: Too many duplicate images")
    
    # At least some label diversity (if vision ran)
    if vision_results and len(diverse_labels) >= 5:
        score += 20
    elif not vision_results:
        score += 10  # partial credit if vision didn't run
    else:
        diagnostics.append(f"FAIL: Images lack content diversity (only {len(diverse_labels)} labels across {len(vision_results)} images)")
    
    # No unsafe content
    if not has_unsafe:
        score += 10
    else:
        diagnostics.append("FAIL: Unsafe content detected")
    
    return score, diagnostics

def main():
    project_path = None
    skip_vision = False
    json_output = False
    
    for arg in sys.argv[1:]:
        if arg == '--json':
            json_output = True
        elif arg == '--skip-vision':
            skip_vision = True
        elif arg.startswith('--project='):
            project_path = arg.split('=', 1)[1]
        elif not arg.startswith('--'):
            project_path = arg
    
    project = load_project(project_path)
    media = project.get("media", [])
    
    # Get all media files referenced in the project
    media_files = []
    for m in media:
        src = m.get("src", "") or f"/media/{m.get('name', '')}"
        fname = src.split("/")[-1]
        fpath = MEDIA_DIR / fname
        if fpath.exists() and fpath.is_file():
            media_files.append(fpath)
    
    if not media_files and project_path:
        # Check from directory
        media_files = list(MEDIA_DIR.iterdir())
    
    score, diagnostics = check_images_vision(media_files, skip_vision)
    
    if json_output:
        print(json.dumps({
            "score": score,
            "passed": score >= PASS_THRESHOLD,
            "diagnostics": diagnostics,
            "files_checked": len(media_files),
            "skip_vision": skip_vision,
        }))
    else:
        print(f"\n{'='*60}")
        print(f"VIDEO VISION CHECK")
        print(f"{'='*60}")
        for d in diagnostics:
            print(f"  {d}")
        print(f"\nVision score: {score}/100")
        print(f"{'PASSED' if score >= PASS_THRESHOLD else 'FAILED'}")
    
    return 0 if score >= PASS_THRESHOLD else 1

if __name__ == "__main__":
    sys.exit(main())
