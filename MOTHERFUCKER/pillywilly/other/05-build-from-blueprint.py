#!/usr/bin/env python3
"""
Build a video from a blueprint. Downloads assets, generates voiceover,
assembles FableCut timeline.

Usage:
  python3 scripts/pipeline/build-from-blueprint.py TBP-026
  python3 scripts/pipeline/build-from-blueprint.py TBP-026 --skip-voiceover
"""

import json, os, re, subprocess, sys, time, urllib.request, shutil, socket
from pathlib import Path

# Use Tor SOCKS proxy if available for downloads (bypasses Hetzner blocks)
try:
    import socks
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
    socket.socket = socks.socksocket
    TOR_AVAILABLE = True
except:
    TOR_AVAILABLE = False

ROOT = Path(__file__).parent.parent.parent
BLUEPRINTS = ROOT / "tantrafiles" / "blueprints"
FABLECUT = ROOT.parent / "FableCut"
PUBLISHING = ROOT / "content" / "publishing" / "scripts"
MEDIA_DIR = FABLECUT / "media"
MCP_IMPORT = "http://localhost:7777/api/import"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def find_blueprint(bp_id):
    for f in BLUEPRINTS.glob(f"{bp_id.upper()}*.md"):
        return f
    return None

def parse_blueprint(path):
    text = path.read_text()
    bp_id = re.search(r'\* `blueprint_id`: (\S+)', text)
    channel = re.search(r'\* `channel`: (\S+)', text)
    assets = []
    # Extract AST entries (Wikimedia, Met Museum, etc.)
    for m in re.finditer(r'\* `asset_id`: (\S+).*?\n.*?\* `.*?content: (.+?)$', text, re.MULTILINE):
        pass  # complex parsing, handle below
    
    # Simpler: find all URLs in asset manifest section
    in_assets = False
    for line in text.split('\n'):
        if '## Visual Asset Manifest' in line or '### OPEN / SAFEST' in line:
            in_assets = True
            continue
        if in_assets and line.startswith('## '):
            in_assets = False
        if in_assets:
            # Wikimedia  (both upload.wikimedia.org and commons.wikimedia.org)
            m = re.search(r'https?://upload\.wikimedia\.org[^\s\)\]]+', line)
            if m: assets.append(("image", m.group(0)))
            m = re.search(r'https?://commons\.wikimedia\.org/wiki/Special:[^\s\)\]]+', line)
            if m: assets.append(("image", m.group(0)))
            # Direct image URLs from the blueprint
            m = re.search(r'https?://[^\s\)\]]+\.(jpg|jpeg|png|gif|webp)', line, re.IGNORECASE)
            if m and 'wikimedia' in m.group(0).lower() or 'metmuseum' in m.group(0).lower():
                assets.append(("image", m.group(0)))
            # Met Museum
            m = re.search(r'https?://collectionapi\.metmuseum\.org[^\s\)\]]+', line)
            if m: assets.append(("image", m.group(0)))
            # YouTube
            m = re.search(r'(https?://www\.youtube\.com/watch\?v=[^\s&\)\]]+)', line)
            if m: assets.append(("video", m.group(0)))
    
    # Deduplicate
    seen = set()
    unique = []
    for kind, url in assets:
        if url not in seen:
            seen.add(url)
            unique.append((kind, url))
    assets[:] = unique
    
    # Get beats and their narration
    beats = []
    in_beats = False
    for line in text.split('\n'):
        if '## Beat Structure' in line:
            in_beats = True
            continue
        if in_beats and line.startswith('## '):
            in_beats = False
        if in_beats:
            m = re.match(r'\d+\.\s+\*\*(.+?)\*\*\s+\((\d+):(\d+)-(\d+):(\d+)\)\s+—\s+(.+?)(?:\.|$)', line)
            if m:
                beats.append({
                    "title": m.group(1),
                    "role": m.group(6).strip(),
                    "start": int(m.group(2))*60 + int(m.group(3)),
                    "end": int(m.group(4))*60 + int(m.group(5)),
                })
    
    return {
        "id": bp_id.group(1) if bp_id else path.stem,
        "title": re.search(r'^# Research Blueprint \d+: (.+)$', text, re.MULTILINE).group(1).strip() if re.search(r'^# Research Blueprint \d+: (.+)$', text, re.MULTILINE) else path.stem,
        "channel": channel.group(1) if channel else "Tantra Files",
        "assets": assets,
        "beats": beats,
    }

def download_asset(url, dest_dir, index):
    """Download an image asset to the media directory."""
    filename = f"ast_{index:03d}.jpg"
    dest = dest_dir / filename
    if dest.exists():
        log(f"  Already exists: {filename}")
        return filename
    
    try:
        if 'wikimedia.org' in url:
            # Fix Wikimedia URLs
            url = url.replace('/thumb/', '/').split('/800px-')[0] if '800px-' in url else url
            url = re.sub(r'/\d+px-[^/]+$', '', url)
        urllib.request.urlretrieve(url, dest)
        log(f"  Downloaded: {filename}")
        return filename
    except Exception as e:
        log(f"  FAILED: {filename} — {e}")
        return None

def download_video(url, dest_dir, index):
    """Download a video clip via yt-dlp."""
    filename = f"clip_{index:03d}.mp4"
    dest = dest_dir / filename
    if dest.exists():
        log(f"  Already exists: {filename}")
        return filename
    
    cookies = "/root/cookies.txt"
    cmd = ["yt-dlp", "-f", "worstvideo[height<=480]+bestaudio", "--merge-output-format", "mp4",
           "-o", str(dest)]
    if os.path.exists(cookies):
        cmd += ["--cookies", cookies]
    cmd.append(url)
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=120)
        if dest.exists():
            log(f"  Downloaded: {filename}")
            return filename
        else:
            log(f"  FAILED: no output file")
            return None
    except Exception as e:
        log(f"  FAILED: {e}")
        return None

def generate_voiceover(beat, out_dir):
    """Generate voiceover for a beat using edge-tts."""
    filename = f"seg-{beat['number']:02d}-{beat['role'].lower()[:10]}.mp3"
    dest = out_dir / filename
    if dest.exists():
        return filename
    
    text = beat.get("narration", beat["title"])
    cmd = ["edge-tts", "--voice", "en-US-AriaNeural", "--text", text, "--write-media", str(dest)]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        if dest.exists():
            return filename
    except:
        pass
    return None

def import_to_fablecut(filename, media_dir):
    """Register a file with FableCut's MCP."""
    filepath = media_dir / filename
    if not filepath.exists():
        return False
    try:
        # FableCut MCP import endpoint
        req = urllib.request.Request(
            "http://localhost:7777/api/import",
            data=json.dumps({"path": str(filepath)}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        # Fallback: just copy to FableCut's media dir
        shutil.copy2(filepath, FABLECUT / "media" / filename)
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: build-from-blueprint.py TBP-NNN [--skip-voiceover]")
        sys.exit(1)
    
    bp_id = sys.argv[1]
    skip_vo = "--skip-voiceover" in sys.argv
    
    path = find_blueprint(bp_id)
    if not path:
        print(f"Blueprint {bp_id} not found")
        sys.exit(1)
    
    bp = parse_blueprint(path)
    slug = bp["id"].lower()
    out_dir = PUBLISHING / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    
    log(f"Building: {bp['id']} — {bp['title']}")
    log(f"Channel: {bp['channel']}")
    log(f"Beats: {len(bp['beats'])}")
    log(f"Assets: {len(bp['assets'])}")
    
    # Step 1: Download assets
    log("\n=== STEP 1: Downloading Assets ===")
    downloaded = []
    for i, (kind, url) in enumerate(bp["assets"]):
        if kind == "image":
            fn = download_asset(url, MEDIA_DIR, i)
        elif kind == "video":
            fn = download_video(url, MEDIA_DIR, i)
        else:
            continue
        if fn:
            downloaded.append(fn)
            import_to_fablecut(fn, MEDIA_DIR)
    log(f"Assets: {len(downloaded)}/{len(bp['assets'])} downloaded")
    
    # Step 2: Generate voiceover
    if not skip_vo:
        log("\n=== STEP 2: Generating Voiceover ===")
        for i, beat in enumerate(bp["beats"]):
            beat["number"] = i + 1
            fn = generate_voiceover(beat, out_dir)
            if fn:
                import_to_fablecut(fn, out_dir)
                log(f"  Beat {i+1}: {fn}")
    else:
        log("\n=== STEP 2: Skipping Voiceover ===")
    
    # Step 3: Generate FableCut project from blueprint
    log("\n=== STEP 3: Generating FableCut Timeline ===")
    result = subprocess.run(
        ["python3", str(ROOT/"scripts/engines/blueprint-to-fablecut.py"), str(path)],
        capture_output=True, text=True, timeout=30)
    log(result.stdout)
    
    # Step 4: Upload to FableCut
    log("\n=== STEP 4: Uploading to FableCut ===")
    project_path = out_dir / f"{slug}-fablecut.json"
    if project_path.exists():
        try:
            # Use MCP set_project
            project_data = json.loads(project_path.read_text())
            req = urllib.request.Request(
                "http://localhost:7777/api/project",
                data=json.dumps(project_data).encode(),
                headers={"Content-Type": "application/json"},
                method="PUT")
            urllib.request.urlopen(req, timeout=5)
            log("  Project loaded into FableCut")
        except Exception as e:
            # Fallback: copy project.json directly
            shutil.copy2(project_path, FABLECUT / "project.json")
            log(f"  Project copied to FableCut (MCP unavailable: {e})")
    
    log(f"\n=== DONE ===")
    log(f"Open dashboard at http://localhost:8766 or FableCut at http://localhost:7777")
    log(f"Media files: {len(downloaded)} assets in {MEDIA_DIR}")

if __name__ == "__main__":
    main()
