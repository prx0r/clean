#!/usr/bin/env python3
"""Generate TTS audio + word boundary metadata per scene."""
import asyncio, json, sys
from pathlib import Path
import edge_tts

NARRATION_PATH = Path("narration/narration-scenes.json")
OUTPUT_DIR = Path("build/audio-scenes")
VOICE = "en-GB-SoniaNeural"

async def synthesize(scene):
    sid = scene["id"]
    audio_path = OUTPUT_DIR / f"{sid}.mp3"
    meta_path = OUTPUT_DIR / f"{sid}.boundaries.json"
    tts = edge_tts.Communicate(scene["text"], voice=VOICE, boundary="WordBoundary")
    await tts.save(str(audio_path), str(meta_path))
    # Load boundaries, convert ticks to seconds, add normalized text
    boundaries = []
    with open(meta_path) as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] != "WordBoundary": continue
            text = entry["text"]
            boundaries.append({
                "text": text,
                "normalized": text.lower().strip("„"",.;:!?-'()[]{}"),
                "start": entry["offset"] / 10_000_000,
                "end": (entry["offset"] + entry["duration"]) / 10_000_000,
            })
    with open(meta_path, "w") as f:
        json.dump({"scene": sid, "boundaries": boundaries}, f, indent=2)
    print(f"  {sid}: {len(boundaries)} words, {audio_path.stat().st_size/1024:.0f}KB")

async def main():
    root = Path(__file__).resolve().parent.parent
    narration = json.loads((root / NARRATION_PATH).read_text())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Synthesizing {len(narration)} scenes...")
    for scene in narration:
        await synthesize(scene)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
