#!/usr/bin/env python3
"""
Visual Director — converts expanded essays into documentary edit decision lists.

Usage:
  python3 scripts/visual-director.py expansion-essay1.md
"""

import sys, json, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
ESSAYS = SCRIPTS
OUT = ROOT / "content" / "publishing" / "storyboards"

# ── Scene grammar: rhetorical function → visual treatment ──────────

VISUAL_GRAMMAR = {
    "hook": {
        "primary": "abstract_diagram",
        "camera": "holds_on_center",
        "art": None,
        "text": "emphasis_phrase",
        "duration_range": (8, 15),
        "transition_out": "fade_to_white",
        "forbidden": ["fast_cuts", "multiple_artworks"],
    },
    "establish": {
        "primary": "manuscript_quote",
        "camera": "slow_push",
        "art": "manuscript_or_portrait",
        "text": "sanskrit_term",
        "duration_range": (12, 20),
        "transition_out": "dissolve",
        "forbidden": ["diagram_before_text"],
    },
    "define": {
        "primary": "diagram_unfold",
        "camera": "pan_across_diagram",
        "art": None,
        "text": "numbered_list",
        "duration_range": (14, 25),
        "transition_out": "cut_to_center",
        "forbidden": ["static_screen"],
    },
    "analogy": {
        "primary": "split_screen",
        "camera": "steady",
        "art": "paired_images",
        "text": "comparison_label",
        "duration_range": (10, 18),
        "transition_out": "dissolve_to_main",
        "forbidden": ["single_image"],
    },
    "quotation": {
        "primary": "quote_card",
        "camera": "holds",
        "art": "manuscript_bg",
        "text": "sanskrit_source",
        "duration_range": (8, 16),
        "transition_out": "fade_through_white",
        "forbidden": ["animation_during_quote"],
    },
    "image_visceral": {
        "primary": "full_bleed_art",
        "camera": "slow_zoom_or_pan",
        "art": "visceral_imagery",
        "text": "minimal_or_none",
        "duration_range": (10, 20),
        "transition_out": "fade_to_black_hold",
        "forbidden": ["text_overlay", "bright_colors"],
    },
    "chain": {
        "primary": "diagram_cascade",
        "camera": "track_through",
        "art": None,
        "text": "sequential_labels",
        "duration_range": (12, 22),
        "transition_out": "dissolve_to_next",
        "forbidden": ["break_chain", "reverse_order"],
    },
    "climax": {
        "primary": "geometric_reveal",
        "camera": "slow_push_to_center",
        "art": None,
        "text": "single_word",
        "duration_range": (10, 18),
        "transition_out": "hold_then_dissolve",
        "forbidden": ["multiple_texts", "distractions"],
    },
    "closing": {
        "primary": "return_to_center",
        "camera": "pull_back",
        "art": "opening_art_if_any",
        "text": "final_phrase",
        "duration_range": (8, 14),
        "transition_out": "fade_to_end",
        "forbidden": ["new_material", "cut_abruptly"],
    },
}


def parse_essay_structure(text):
    """Parse an expanded essay into rhetorical beats."""
    lines = text.strip().split("\n")
    beats = []
    current = {"paragraphs": [], "lines": [], "raw": ""}
    in_quote = False

    for line in lines:
        stripped = line.strip()

        # Track blockquotes
        if stripped.startswith("> "):
            if not in_quote:
                if current["raw"].strip():
                    beats.append(current)
                current = {"paragraphs": [], "lines": [], "raw": "", "is_quote": True}
                in_quote = True
            current["lines"].append(stripped[2:])
            current["raw"] += stripped[2:] + " "
            continue
        else:
            if in_quote and stripped == "":
                in_quote = False
                if current["raw"].strip():
                    beats.append(current)
                current = {"paragraphs": [], "lines": [], "raw": ""}
                continue
            elif in_quote and stripped != "":
                current["lines"].append(stripped)
                current["raw"] += stripped + " "
                continue

        # Handle paragraph breaks
        if stripped == "":
            if current["raw"].strip():
                beats.append(current)
            current = {"paragraphs": [], "lines": [], "raw": ""}
            continue

        current["lines"].append(stripped)
        current["raw"] += stripped + " "

    if current["raw"].strip():
        beats.append(current)

    # Classify beats, then merge adjacent beats with same function
    raw_classified = []
    for i, beat in enumerate(beats):
        text = beat["raw"].strip()
        is_quote = beat.get("is_quote", False)

        if is_quote:
            fn = "quotation"
        elif i == 0:
            fn = "hook"
        elif "Six names for one thing" in text:
            fn = "define"
        elif "tuning fork" in text.lower():
            fn = "analogy"
        elif "belly of the fish" in text.lower() or "female donkey" in text.lower():
            fn = "image_visceral"
        elif "Time → Breath → Spanda → Void" in text:
            fn = "chain"
        elif "Play — krīḍa" in text or "camatkāra" in text:
            fn = "climax"
        elif "last word" in text.lower():
            fn = "closing"
        else:
            fn = "establish"

        raw_classified.append({"type": fn, "text": text, "is_quote": is_quote})

    # Merge: adjacent same-type beats, and absorb quotation into preceding beat
    classified = []
    for item in raw_classified:
        if item["is_quote"] and classified:
            # Append quote text to previous scene
            classified[-1]["text"] += "\n\n" + item["text"]
            classified[-1]["has_quote"] = True
            if "sanskrit_lines" not in classified[-1]:
                classified[-1]["sanskrit_lines"] = []
            classified[-1]["sanskrit_lines"].extend(
                [l for l in item["text"].split("\n") if any('\u0900' <= c <= '\u097F' for c in l)]
            )
        elif classified and classified[-1]["type"] == item["type"] and item["type"] in ("establish",):
            classified[-1]["text"] += "\n\n" + item["text"]
        else:
            classified.append({"type": item["type"], "text": item["text"],
                               "has_quote": item["is_quote"]})

    return classified


def build_edit_decision_list(essay_path):
    """Convert an expanded essay into a documentary edit decision list."""
    text = Path(essay_path).read_text()
    beats = parse_essay_structure(text)

    scenes = []
    total_duration = 0

    for i, beat in enumerate(beats):
        fn = beat["type"]
        grammar = VISUAL_GRAMMAR.get(fn, VISUAL_GRAMMAR["establish"])
        dur_min, dur_max = grammar["duration_range"]
        duration = dur_min + (dur_max - dur_min) * 0.5  # default to midpoint

        scene = {
            "scene_id": f"scene-{i+1:02d}",
            "rhetorical_function": fn,
            "narration_excerpt": beat["text"][:200] + ("..." if len(beat["text"]) > 200 else ""),
            "visual_treatment": grammar["primary"],
            "camera": grammar["camera"],
            "art_requirement": grammar["art"],
            "text_style": grammar["text"],
            "forbidden": grammar["forbidden"],
            "duration_seconds": round(duration, 1),
            "transition_out": grammar["transition_out"],
        }

        if beat.get("sanskrit_lines"):
            scene["sanskrit"] = beat["sanskrit_lines"][:5]

        scenes.append(scene)
        total_duration += duration

    # Build output
    output = {
        "essay": Path(essay_path).name,
        "total_scenes": len(scenes),
        "total_duration_seconds": round(total_duration, 1),
        "estimated_duration": f"{int(total_duration // 60)}m {int(total_duration % 60)}s",
        "scenes": scenes,
    }

    return output


def format_as_readable(edl):
    """Format the EDL as a readable markdown document."""
    lines = [
        f"# {edl['essay']} — Edit Decision List",
        f"**{edl['total_scenes']} scenes · {edl['estimated_duration']}**\n",
    ]

    for i, s in enumerate(edl["scenes"]):
        lines.append(f"---")
        lines.append(f"## Scene {i+1}: {s['rhetorical_function'].title()}")
        lines.append(f"**{s['duration_seconds']}s** — {s['visual_treatment'].replace('_', ' ').title()}")
        lines.append(f"Camera: {s['camera'].replace('_', ' ')}")
        lines.append(f"")
        lines.append(f"Narration:")
        lines.append(f"> {s['narration_excerpt']}")
        lines.append(f"")
        if s.get("sanskrit"):
            lines.append(f"Sanskrit:")
            for sl in s["sanskrit"]:
                lines.append(f"  {sl}")
            lines.append(f"")
        lines.append(f"Art: {s['art_requirement'] or 'none — generative diagram'}")
        lines.append(f"Text: {s['text_style'].replace('_', ' ')}")
        lines.append(f"Forbidden: {', '.join(s['forbidden'])}")
        lines.append(f"Transition: {s['transition_out'].replace('_', ' ')}")
        lines.append(f"")

    return "\n".join(lines)


if __name__ == "__main__":
    essay = sys.argv[1] if len(sys.argv) > 1 else "expansion-essay1.md"
    essay_path = SCRIPTS / essay

    if not essay_path.exists():
        print(f"Essay not found: {essay_path}")
        sys.exit(1)

    edl = build_edit_decision_list(essay_path)
    OUT.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = OUT / f"{essay_path.stem}-edl.json"
    json_path.write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"EDL JSON: {json_path}")

    # Save readable markdown
    md = format_as_readable(edl)
    md_path = OUT / f"{essay_path.stem}-edl.md"
    md_path.write_text(md)
    print(f"EDL Markdown: {md_path}")
    print(f"\n{edl['total_scenes']} scenes · {edl['estimated_duration']}")

    # Print summary
    for i, s in enumerate(edl["scenes"]):
        print(f"  {i+1:2d}. [{s['duration_seconds']:5.1f}s] {s['rhetorical_function']:15s} → {s['visual_treatment']}")
