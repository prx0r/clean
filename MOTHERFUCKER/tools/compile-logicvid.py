#!/usr/bin/env python3
"""Resolve semantic anchors to frame numbers and compile source packs."""
import json, sys
from pathlib import Path

FPS = 24

def load_boundaries(scene_id):
    path = Path("build/audio-scenes") / f"{scene_id}.boundaries.json"
    return json.loads(path.read_text())

def normalize(word):
    return word.lower().strip("„"",.;:!?-'()[]{}")

def resolve_anchor(boundaries, anchor):
    """Resolve a semantic anchor to start/end frames."""
    if anchor is None:
        return 0, None
    word = anchor.get("after", "")
    word_idx = anchor.get("wordIndex")
    edge = anchor.get("edge", "start")
    offset_frames = anchor.get("offsetFrames", 0)
    hold = anchor.get("hold", "scene-end")

    b = boundaries["boundaries"]

    if word_idx is not None:
        entry = b[word_idx] if 0 <= word_idx < len(b) else None
    elif word:
        nw = normalize(word)
        matches = [e for e in b if normalize(e["text"]) == nw]
        if "occurrence" in anchor:
            idx = max(0, min(anchor["occurrence"] - 1, len(matches) - 1))
            entry = matches[idx] if matches else None
        else:
            entry = matches[0] if matches else None
    else:
        entry = None

    if entry is None:
        return 0, None

    t = entry["start"] if edge == "start" else entry["end"]
    frame = round(t * FPS) + offset_frames
    return max(0, frame), hold

def resolve_exit(boundaries, exit_spec, boundaries_list, current_idx):
    """Resolve exit condition: before another move's anchor word."""
    if exit_spec is None:
        return None
    if exit_spec == "scene-end":
        return None
    if isinstance(exit_spec, dict):
        before = exit_spec.get("beforeMove", "")
        for i, m in enumerate(boundaries_list):
            if i <= current_idx: continue
            enter = m.get("enter", {})
            ew = enter.get("after", "")
            if ew and normalize(ew) == normalize(before):
                entry = next((e for e in boundaries["boundaries"]
                            if normalize(e["text"]) == normalize(before)), None)
                if entry:
                    return round(entry["start"] * FPS)
    return None

def compile_scene(scene, boundaries):
    """Compile a scene's moves to frame-native timing."""
    fps = scene.get("render", {}).get("fps", FPS) if "render" in scene else FPS
    moves = scene.get("params", {}).get("moves", scene.get("moves", []))
    compiled = []
    scene_dur_sec = 0

    for i, move in enumerate(moves):
        enter_anchor = move.get("enter")
        exit_anchor = move.get("exit")
        enter_frame, hold = resolve_anchor(boundaries, enter_anchor)
        exit_frame = resolve_exit(boundaries, exit_anchor, moves, i)
        settle_frame = enter_frame + (move.get("transitionFrames", 0) or 0)
        replacement_group = move.get("replacementGroup", "default")
        slot = move.get("slot", "center")
        row = {
            "type": move["type"],
            "text": move.get("text"),
            "left": move.get("left"),
            "right": move.get("right"),
            "branches": move.get("branches"),
            "premises": move.get("premises"),
            "conclusion": move.get("conclusion"),
            "nodes": move.get("nodes"),
            "central": move.get("central"),
            "size": move.get("size"),
            "color": move.get("color"),
            "status": move.get("status"),
            "y": move.get("y"),
            "enterFrame": enter_frame,
            "settleFrame": settle_frame,
            "exitFrame": exit_frame,
            "slot": slot,
            "replacementGroup": replacement_group,
        }
        compiled.append(row)
        # Scene duration is the last word boundary end
        if boundaries["boundaries"]:
            last_word = boundaries["boundaries"][-1]
            sd = round(last_word["end"], 3)
            if sd > scene_dur_sec:
                scene_dur_sec = sd

    return compiled, scene_dur_sec

def main():
    root = Path(__file__).resolve().parent.parent
    packs_dir = root / "packs"
    compiled_dir = packs_dir / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    source_path = packs_dir / "logicvid-reality-appears.source.json"
    if not source_path.exists():
        print(f"Source pack not found: {source_path}")
        sys.exit(1)

    source = json.loads(source_path.read_text())
    compiled_pack = {
        "version": "1.0",
        "id": source["id"],
        "title": source["title"],
        "theme": "ivoryManuscript",
        "seed": source.get("seed", 260727),
        "render": {
            "width": 1280,
            "height": 720,
            "fps": FPS,
            "crf": 16,
            "preset": "medium",
            "sceneDuration": 12,
            "transitionDuration": 0,
        },
        "scenes": [],
    }

    total_frames = 0
    for scene in source["scenes"]:
        sid = scene["id"]
        boundaries = load_boundaries(sid)
        compiled_moves, scene_dur = compile_scene(scene, boundaries)
        scene_frames = round(scene_dur * FPS)
        compiled_scene = {
            "id": sid,
            "title": scene.get("title", ""),
            "subtitle": scene.get("subtitle", ""),
            "term": scene.get("term", ""),
            "devanagari": scene.get("devanagari", ""),
            "motif": "logicvid",
            "duration": scene_dur,
            "frameCount": scene_frames,
            "params": {"moves": compiled_moves},
        }
        compiled_pack["scenes"].append(compiled_scene)
        total_frames += scene_frames

    out_path = compiled_dir / "logicvid-reality-appears.json"
    compiled_pack["render"]["sceneDuration"] = 12
    out_path.write_text(json.dumps(compiled_pack, indent=2, ensure_ascii=False) + "\n")
    print(f"Compiled {len(source['scenes'])} scenes, {total_frames} total frames")
    print(f"Output: {out_path}")

if __name__ == "__main__":
    main()
