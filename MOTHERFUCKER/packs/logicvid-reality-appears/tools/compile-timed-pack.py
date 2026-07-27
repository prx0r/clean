#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
template=root/"MOTHERFUCKER/packs/logicvid-reality-appears.template.json"
narration=root/"narration/narration-scenes.json"
audio_dir=root/"build/audio-scenes"
output=root/"MOTHERFUCKER/packs/logicvid-reality-appears.json"

pack=json.loads(template.read_text(encoding="utf-8"))
entries=json.loads(narration.read_text(encoding="utf-8"))
by_id={entry["id"]:entry for entry in entries}

for scene in pack["scenes"]:
    audio=audio_dir/f'{scene["id"]}.mp3'
    result=subprocess.run([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(audio)
    ],capture_output=True,text=True,check=True)
    duration=float(result.stdout.strip())
    scene["duration"]=round(duration,3)
    scene["narration"]=by_id[scene["id"]]["text"]

output.write_text(json.dumps(pack,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(output)
