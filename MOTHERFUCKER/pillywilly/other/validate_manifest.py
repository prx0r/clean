"""Validate a scene manifest against gold standard pacing metrics."""
import json, sys
from pathlib import Path

GOLD = {
    "avg_shot_sec": 7.1,       # Alan Watts gold
    "scene_range": (28, 45),   # 8 reference packs: 28-36s per scene
    "scene_count_range": (8, 19),
    "max_duration": 660,       # 11 min (armor)
}

def validate(manifest_path):
    m = json.loads(Path(manifest_path).read_text())
    scenes = m["scenes"]
    fps = m.get("fps", 2)
    issues = []

    # Scene count
    n = len(scenes)
    lo, hi = GOLD["scene_count_range"]
    if n < lo or n > hi:
        issues.append(f"Scene count {n} outside gold range [{lo}, {hi}]")

    # Scene durations
    for s in scenes:
        d = s["duration"]
        lo_d, hi_d = GOLD["scene_range"]
        if d < lo_d or d > hi_d:
            issues.append(f"  Scene {s['index']} '{s['title']}': {d}s outside gold [{lo_d}, {hi_d}]")

    # Total duration
    total = sum(s["duration"] for s in scenes)
    if total > GOLD["max_duration"]:
        issues.append(f"Total {total}s exceeds max {GOLD['max_duration']}s")

    # Timing continuity (end of scene N should match start of scene N+1)
    for i in range(n - 1):
        if abs(scenes[i]["end"] - scenes[i+1]["start"]) > 0.1:
            issues.append(f"  Gap/overlap between scene {scenes[i]['index']} end ({scenes[i]['end']}) and scene {scenes[i+1]['index']} start ({scenes[i+1]['start']})")

    # Duration match scene manifest total
    manifest_total = m.get("duration_seconds", 0)
    calc_total = sum(s["duration"] for s in scenes)
    if abs(manifest_total - calc_total) > 1:
        issues.append(f"Manifest duration_seconds ({manifest_total}) ≠ sum of scene durations ({calc_total})")

    result = {
        "manifest": manifest_path.name,
        "title": m.get("title", ""),
        "scenes": n,
        "total_seconds": total,
        "fps": fps,
        "issues": issues,
        "pass": len(issues) == 0,
    }

    return result

if __name__ == "__main__":
    for p in sys.argv[1:] or ["spanda_output_pack/scene_manifest.json"]:
        r = validate(Path(p))
        print(f"\n{'✅' if r['pass'] else '❌'} {r['manifest']}: {r['title']}")
        print(f"   {r['scenes']} scenes, {r['total_seconds']}s at {r['fps']}fps")
        if r['issues']:
            for i in r['issues']:
                print(f"   ⚠ {i}")
