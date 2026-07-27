#!/usr/bin/env python3
"""
Blueprint → beat-map.md → FableCut project.json pipeline.
Usage:
  python3 blueprint-to-fablecut.py tantrafiles/blueprints/TBP-026-yogini-temples.md
  → outputs beat-map.md + FableCut project.json
"""

import json, re, os, sys
from pathlib import Path

DATA_DIR = Path("/root/projects/blog/data/research/layer2")
FABLECUT_DIR = Path("/root/projects/FableCut")
BLUEPRINTS_DIR = Path("/root/projects/blog/tantrafiles/blueprints")
OUTPUT_DIR = Path("/root/projects/blog/content/publishing/scripts")

TREATMENT_PRESETS = {
    "Tantra Files": {"bg": "#1a0a00", "accent": "#CC6600", "filter": "golden-imaginal"},
    "Ochema": {"bg": "#0D1117", "accent": "#00D4FF", "filter": "mystical-dark"},
    "Angeliz": {"bg": "#1a0000", "accent": "#8B0000", "filter": "corbin-blue"},
    "Pramāṇa": {"bg": "#1a1a1a", "accent": "#FFD700", "filter": "sepia-classic"},
    "Intelligent Others": {"bg": "#0A0A2E", "accent": "#00FF88", "filter": "mystical-dark"},
}

def parse_blueprint(path):
    with open(path) as f:
        text = f.read()

    # Extract metadata
    bp_id = re.search(r'\* `blueprint_id`: (\S+)', text)
    channel = re.search(r'\* `channel`: (\S+)', text)
    runtime = re.search(r'\* `target_runtime_minutes`: (\d+)', text)
    title_match = re.search(r'^# Research Blueprint \d+: (.+)$', text, re.MULTILINE)
    hook_match = re.search(r'## Charged Hook\n\n(.+?)(?:\n\n)', text, re.DOTALL)

    # Extract beat structure
    beats = []
    beat_section = re.search(r'## Beat Structure.*?\n(.+?)(?:\n##|\Z)', text, re.DOTALL)
    if beat_section:
        for line in beat_section.group(1).split('\n'):
            m = re.match(r'\d+\.\s+\*\*(.+?)\*\*\s+\((\d+):(\d+)-(\d+):(\d+)\)\s+—\s+(.+?)(?:\.|$)', line)
            if m:
                title = m.group(1)
                start_m = int(m.group(2))
                start_s = int(m.group(3))
                end_m = int(m.group(4))
                end_s = int(m.group(5))
                role = m.group(6).strip()
                start_sec = start_m * 60 + start_s
                end_sec = end_m * 60 + end_s
                beats.append({
                    "number": len(beats) + 1,
                    "title": title,
                    "role": role,
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "duration_sec": end_sec - start_sec,
                })

    return {
        "id": bp_id.group(1) if bp_id else "TBP-000",
        "title": title_match.group(1).strip() if title_match else "Untitled",
        "channel": channel.group(1) if channel else "Tantra Files",
        "runtime": int(runtime.group(1)) if runtime else 20,
        "hook": hook_match.group(1).strip()[:200] if hook_match else "",
        "beats": beats,
    }

def generate_beatmap(bp):
    preset = TREATMENT_PRESETS.get(bp["channel"], TREATMENT_PRESETS["Tantra Files"])
    lines = [f"# Beat Map — {bp['id']}: {bp['title']}"]
    lines.append(f"## Scene type: Documentary with artwork + text overlays")
    lines.append(f"## Channel: {bp['channel']} | Filter preset: {preset['filter']}")
    lines.append("")

    for i, beat in enumerate(bp["beats"]):
        ts = f"{beat['start_sec']//60}:{beat['start_sec']%60:02d}-{beat['end_sec']//60}:{beat['end_sec']%60:02d}"
        lines.append(f"BEAT {beat['number']} [{ts}] \"{beat['title']}\"")
        lines.append(f"  ROLE: {beat['role']}")
        lines.append(f"  VISUAL: {preset['bg']} background. Artwork from AST-XXX. Text overlay for key claim.")
        lines.append(f"  AUDIO: Voiceover segment {i+1}. Ambient drone in background.")
        lines.append("")

    return "\n".join(lines)

def generate_fablecut_project(bp):
    preset = TREATMENT_PRESETS.get(bp["channel"], TREATMENT_PRESETS["Tantra Files"])
    slug = bp["id"].lower().replace(":", "-")

    media = []
    clips_v1 = []
    clips_a1 = []
    clip_id = 0

    for i, beat in enumerate(bp["beats"]):
        beat_num = i + 1
        seg_name = f"seg-{beat_num:02d}-{beat['role'].lower().replace(' ','-')}"

        # Audio media entry
        media.append({
            "id": f"m_{seg_name}",
            "name": f"{seg_name}.mp3",
            "kind": "audio",
            "src": f"/media/{seg_name}.mp3",
            "duration": beat["duration_sec"],
        })

        # Placeholder artwork
        media.append({
            "id": f"m_art_{slug}_{beat_num}",
            "name": f"art_{slug}_{beat_num}.jpg",
            "kind": "image",
            "src": f"/media/art_{slug}_{beat_num}.jpg",
            "width": 1280,
            "height": 720,
        })

        # V1 clip (artwork)
        clips_v1.append({
            "id": f"c_v1_{beat_num}",
            "mediaId": f"m_art_{slug}_{beat_num}",
            "track": "V1",
            "start": beat["start_sec"],
            "duration": beat["duration_sec"],
            "effects": [{"type": "filter", "name": preset["filter"]}],
        })

        # A1 clip (voiceover)
        clips_a1.append({
            "id": f"c_a1_{beat_num}",
            "mediaId": f"m_{seg_name}",
            "track": "A1",
            "start": beat["start_sec"],
            "duration": beat["duration_sec"],
        })

    project = {
        "name": bp["title"][:60],
        "width": 1280,
        "height": 720,
        "fps": 25,
        "background": preset["bg"],
        "revision": 1,
        "media": media,
        "clips": clips_v1 + clips_a1,
    }

    return project

def main():
    if len(sys.argv) < 2:
        print("Usage: blueprint-to-fablecut.py <blueprint.md>")
        sys.exit(1)

    bp_path = Path(sys.argv[1])
    bp = parse_blueprint(bp_path)
    slug = bp["id"].lower()

    # Generate beat-map
    beatmap = generate_beatmap(bp)
    beatmap_dir = OUTPUT_DIR / slug
    beatmap_dir.mkdir(parents=True, exist_ok=True)
    beatmap_path = beatmap_dir / "beat-map.md"
    with open(beatmap_path, "w") as f:
        f.write(beatmap)
    print(f"Beat map: {beatmap_path}")

    # Generate FableCut project
    project = generate_fablecut_project(bp)
    project_path = beatmap_dir / f"{slug}-fablecut.json"
    with open(project_path, "w") as f:
        json.dump(project, f, indent=2)
    print(f"FableCut project: {project_path}")

    # Summary
    preset = TREATMENT_PRESETS.get(bp["channel"], TREATMENT_PRESETS["Tantra Files"])
    total_sec = sum(b["duration_sec"] for b in bp["beats"])
    print(f"\n=== SUMMARY ===")
    print(f"Blueprint: {bp['id']}: {bp['title']}")
    print(f"Channel: {bp['channel']} | Filter: {preset['filter']}")
    print(f"Duration: {total_sec//60}:{total_sec%60:02d}")
    print(f"Beats: {len(bp['beats'])}")
    print(f"Media entries: {len(project['media'])}")
    print(f"Clips: {len(project['clips'])}")
    print(f"\nTo render: open {FABLECUT_DIR / slug} in FableCut at localhost:7777")

if __name__ == "__main__":
    main()
