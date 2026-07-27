#!/usr/bin/env python3
"""
Timing engine: takes narration audio + essay → frame-accurate project.json.

Pipeline:
  1. Transcribe each voiceover segment with CF Whisper (word-level timestamps)
  2. Map essay beats → SVGs → exact clip timings
  3. Generate emphasis text clips synced to spoken words
  4. Output project.json with frame-level precision

Usage:
  python3 scripts/build-timed-video.py engine-of-consciousness
"""

import json, os, sys, subprocess, tempfile, base64, urllib.request, re, time
from pathlib import Path

ROOT = Path("/root/projects/blog")
FABLECUT = Path("/root/projects/FableCut")
SVG_LIB = "library/svg/spanda"
W = 1920; H = 1080; FPS = 30

CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACCOUNT = "954612afb5a97bb15dddcdc70176813d"
CF_WHISPER = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/openai/whisper-large-v3-turbo"

def transcribe_segment(mp3_path):
    """Get word-level timestamps from CF Whisper."""
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", mp3_path],
                          capture_output=True, text=True, timeout=10)
    duration = float(json.loads(result.stdout)["format"]["duration"])
    
    wav = Path(tempfile.mkdtemp()) / "chunk.wav"
    subprocess.run(["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "16000", "-ac", "1", str(wav)],
                  capture_output=True, timeout=30)
    
    with open(wav, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    req = urllib.request.Request(CF_WHISPER,
        data=json.dumps({"audio": audio_b64, "word_timestamps": True}).encode(),
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
    
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            result = json.loads(resp.read())
            if result.get("success"):
                words = []
                for seg in result["result"].get("segments", []):
                    for w in seg.get("words", []):
                        words.append({
                            "word": w["word"].strip(),
                            "start": round(w["start"], 3),
                            "end": round(w["end"], 3)
                        })
                os.unlink(wav)
                os.rmdir(wav.parent)
                return words, duration
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
    
    os.unlink(wav)
    os.rmdir(wav.parent)
    return [], duration

def find_word(words, text, offset=0):
    """Find a phrase in word-level transcript and return its start/end."""
    text_lower = text.lower().strip()
    full_text = " ".join(w["word"].lower() for w in words)
    
    if text_lower in full_text:
        idx = full_text.index(text_lower)
        char_count = 0
        start_word = None
        end_word = None
        for w in words:
            w_start = char_count
            w_end = char_count + len(w["word"])
            if start_word is None and w_end > idx:
                start_word = w
            if end_word is None and char_count >= idx + len(text_lower):
                end_word = w
                break
            char_count = w_end + 1
        
        if start_word:
            s = start_word["start"] + offset
            e = (end_word["end"] if end_word else start_word["end"]) + offset
            return round(s, 2), round(e, 2)
    
    # Fallback: estimate from position
    approx_start = offset + (full_text.find(text_lower[:5]) / len(full_text)) * (words[-1]["end"] - words[0]["start"]) if len(words) > 1 else offset
    return round(approx_start, 2), round(approx_start + 2, 2)

def build_project(essay_id):
    """Build frame-accurate project for an essay."""
    storyboard_path = ROOT / "content" / "publishing" / "storyboards" / f"{essay_id}.json"
    if not storyboard_path.exists():
        print(f"Storyboard not found: {storyboard_path}")
        return
    
    sb = json.loads(storyboard_path.read_text())
    segments = sb["segments"]
    vo_dir = ROOT / "content" / "publishing" / "voiceover" / essay_id
    
    # Scene mappings: segment_id → (svg_asset, theme, emphasis_phrases)
    scene_map = {
        "seg-01-hook": ("pulse-field", "light",
            ["not your heartbeat", "not your breath", "something more fundamental"]),
        "seg-02-wheel": ("wheel-hub", "light",
            ["wheel of powers", "awareness as center", "sovereignty"]),
        "seg-03-six-names": ("aperture-breath", "light",
            ["six names for one thing", "everyday impulse"]),
        "seg-04-mantra": ("resonance-transfer", "light",
            ["mantra is pulse made sound", "one woven thrum"]),
        "seg-05-perception": ("connect-disconnect", "light",
            ["every perception a pulse", "open — close — open"]),
        "seg-06-fish": ("drum-rings", "light",
            ["whole body one single throb"]),
        "seg-07-time": ("wave-return", "light",
            ["time — breath — spanda — void"]),
        "seg-08-wave": ("ocean-heart", "light",
            ["wave upon wave", "the universe is a drum"]),
        "seg-09-play": ("playful-orbit", "light",
            ["play — wonder — joy in motion"]),
        "seg-10-closing": ("gather-to-center", "light",
            ["when recognition lands"]),
    }
    
    project = {
        "name": sb["episode_title"],
        "width": W, "height": H, "fps": FPS,
        "background": "#ffffff", "revision": 1, "disabledTracks": [],
        "media": [], "clips": [], "markers": []
    }
    
    current_time = 0.0
    
    for seg in segments:
        seg_id = seg["segment_id"]
        mp3_path = vo_dir / f"{seg_id}.mp3"
        
        if not mp3_path.exists():
            current_time += seg.get("end_sec", 0) - seg.get("start_sec", 0)
            continue
        
        # Transcribe with word-level timestamps
        print(f"Transcribing {seg_id}...", flush=True)
        words, duration = transcribe_segment(str(mp3_path))
        if not words:
            print(f"  No words for {seg_id}, skipping")
            current_time += duration
            continue
        
        # Copy to media
        import shutil
        shutil.copy2(mp3_path, FABLECUT / "media" / mp3_path.name)
        
        # Add voiceover
        vo_mid = f"m_vo_{seg_id}"
        project["media"].append({"id": vo_mid, "name": mp3_path.name, "kind": "audio",
            "src": f"/media/{mp3_path.name}", "duration": round(duration, 3)})
        project["clips"].append({"id": f"a_{seg_id}", "mediaId": vo_mid, "kind": "audio",
            "track": "A1", "start": round(current_time, 3), "in": 0,
            "duration": round(duration, 3), "name": seg_id, "props": {"volume": 1}})
        
        # Add SVG scene
        seg_info = scene_map.get(seg_id, ("pulse-field", "light", []))
        svg_asset, theme, emphases = seg_info
        
        svg_file = f"{svg_asset}-01.svg"
        svg_mid = f"m_svg_{seg_id}"
        project["media"].append({"id": svg_mid, "name": svg_file, "kind": "svg",
            "src": f"/{SVG_LIB}/{svg_file}", "width": W, "height": H})
        project["clips"].append({"id": f"v_{seg_id}", "mediaId": svg_mid, "kind": "svg",
            "track": "V1", "start": round(current_time, 3), "in": 0,
            "duration": round(duration, 3), "name": seg_id,
            "props": {"fit": "stretch", "x": 0, "y": 0, "scale": 1, "opacity": 1}})
        
        # Add emphasis text at exact word timestamps
        for phrase in emphases:
            ts, te = find_word(words, phrase, current_time)
            if ts and te:
                text_id = f"t_{seg_id}_{int(ts*10)}"
                project["clips"].append({
                    "id": text_id, "track": "V3", "kind": "text",
                    "start": ts, "in": 0, "duration": round(te - ts, 2),
                    "name": phrase[:20],
                    "props": {
                        "text": phrase,
                        "font": "Playfair Display", "fontSize": 52,
                        "color": "#111111", "align": "center",
                        "x": 0, "y": 360, "bgOpacity": 0, "textShadow": 0
                    }
                })
                print(f"  Text: '{phrase}' at {ts:.2f}s-{te:.2f}s", flush=True)
        
        project["markers"].append({"t": round(current_time, 2), "label": seg_id})
        current_time += duration
    
    # Write project
    out_path = FABLECUT / "project.json"
    out_path.write_text(json.dumps(project, indent=2))
    print(f"\nWritten: {len(project['clips'])} clips, {len(project['media'])} media")
    print(f"Total: {current_time:.1f}s")
    
    # Load into FableCut
    try:
        req = urllib.request.Request("http://localhost:7777/api/project")
        resp = urllib.request.urlopen(req, timeout=5)
        current = json.loads(resp.read())
        project["revision"] = current.get("revision", 0) + 1
    except:
        project["revision"] = 1
    
    try:
        req = urllib.request.Request("http://localhost:7777/api/project",
            data=json.dumps(project).encode(),
            headers={"Content-Type": "application/json"}, method="PUT")
        resp = urllib.request.urlopen(req, timeout=5)
        print(f"Loaded: HTTP {resp.status}")
    except Exception as e:
        print(f"Load: {e}")
    
    return project

if __name__ == "__main__":
    essay = sys.argv[1] if len(sys.argv) > 1 else "engine-of-consciousness"
    build_project(essay)
