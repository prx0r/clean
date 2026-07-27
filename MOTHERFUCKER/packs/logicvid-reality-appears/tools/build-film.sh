#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p build/audio-scenes MOTHERFUCKER/build/logicvid-reality-appears

python3 - <<'PY'
import json, subprocess
from pathlib import Path
entries=json.loads(Path("narration/narration-scenes.json").read_text())
for entry in entries:
    output=Path("build/audio-scenes")/f'{entry["id"]}.mp3'
    subprocess.run([
        "edge-tts","--voice","en-GB-SoniaNeural",
        "--text",entry["text"],"--write-media",str(output)
    ],check=True)
PY

python3 tools/compile-timed-pack.py "$ROOT"

python3 - <<'PY'
import json
from pathlib import Path
entries=json.loads(Path("narration/narration-scenes.json").read_text())
lines=[]
for entry in entries:
    lines.append(f"file '{(Path('build/audio-scenes')/(entry['id']+'.mp3')).resolve()}'")
Path("build/audio-scenes/concat.txt").write_text("\n".join(lines)+"\n")
PY

ffmpeg -y -loglevel error -f concat -safe 0 -i build/audio-scenes/concat.txt \
  -c:a libmp3lame -q:a 2 MOTHERFUCKER/build/logicvid-reality-appears/narration.mp3

python3 MOTHERFUCKER/tools/analyse-audio.py \
  MOTHERFUCKER/build/logicvid-reality-appears/narration.mp3 \
  MOTHERFUCKER/build/logicvid-reality-appears/features.json

node tools/render-logicvid.mjs

ffmpeg -y -loglevel error \
  -i MOTHERFUCKER/build/logicvid-reality-appears/video.mp4 \
  -i MOTHERFUCKER/build/logicvid-reality-appears/narration.mp3 \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 -shortest \
  MOTHERFUCKER/build/logicvid-reality-appears/final.mp4

echo "Built MOTHERFUCKER/build/logicvid-reality-appears/final.mp4"
