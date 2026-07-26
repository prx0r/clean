#!/usr/bin/env python3
"""Deterministic semantic checks for Signature Film System decision records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


PHASES = {"latent", "formation", "stress", "revision", "integration"}
ROLES = {
    "establish", "perturb", "disclose", "model", "contrast", "deepen",
    "reverse", "test", "caution", "integrate", "coda",
}
VERBS = {
    "emerge", "gather", "split", "exclude", "bind", "transmit", "remember",
    "predict", "repair", "compare", "dissolve", "recognize",
}
REQUIRED_SCENE_FIELDS = {
    "shader", "source_visual", "phase", "role", "claim", "verb", "topology",
    "composition", "material_state", "camera", "u_semantics", "t_semantics",
    "audio_volume_semantics", "audio_beat_semantics", "glance_thesis",
    "rationale", "risk", "review_target",
}


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    errors: list[str] = []
    for field in (
        "schema_version", "pack", "source", "thesis", "continuity_material",
        "color_roles", "arc", "scenes",
    ):
        if field not in data:
            errors.append(f"missing top-level field: {field}")

    if errors:
        return errors
    if data["schema_version"] != "1.0":
        errors.append("schema_version must be 1.0")
    if len(data["thesis"]) < 20:
        errors.append("thesis is too short")
    if set(data["arc"]) != PHASES:
        errors.append("arc must contain exactly the five film phases")

    continuity = data["continuity_material"]
    for field in ("name", "initial", "stress", "integrated"):
        if not str(continuity.get(field, "")).strip():
            errors.append(f"continuity_material.{field} is required")

    scenes = data["scenes"]
    if not scenes:
        return errors + ["scenes must not be empty"]

    names: list[str] = []
    sources: list[str] = []
    for index, scene in enumerate(scenes):
        label = f"scene {index + 1}"
        missing = REQUIRED_SCENE_FIELDS - set(scene)
        if missing:
            errors.append(f"{label} missing: {', '.join(sorted(missing))}")
            continue
        if scene["phase"] not in PHASES:
            errors.append(f"{label} has invalid phase")
        if scene["role"] not in ROLES:
            errors.append(f"{label} has invalid role")
        if scene["verb"] not in VERBS:
            errors.append(f"{label} has invalid verb")
        if not scene["shader"].startswith("vis_") or not scene["shader"].endswith(".glsl"):
            errors.append(f"{label} shader must be vis_*.glsl")
        for field in (
            "u_semantics", "t_semantics", "audio_volume_semantics",
            "audio_beat_semantics",
        ):
            if len(scene[field].strip()) < 8:
                errors.append(f"{label} needs meaningful {field}")
        names.append(scene["shader"])
        sources.append(scene["source_visual"])

    for name, count in Counter(names).items():
        if count > 1:
            errors.append(f"duplicate shader: {name}")
    for name, count in Counter(sources).items():
        if count > 1:
            errors.append(f"duplicate source_visual: {name}")

    for phase in PHASES:
        if phase not in {scene.get("phase") for scene in scenes}:
            errors.append(f"unused film phase: {phase}")

    composition_counts = Counter(scene.get("composition") for scene in scenes)
    composition, count = composition_counts.most_common(1)[0]
    if count / len(scenes) > 1 / 3:
        errors.append(
            f"composition family '{composition}' appears in {count}/{len(scenes)} "
            "(maximum is one third)"
        )

    verb_counts = Counter(scene.get("verb") for scene in scenes)
    verb, count = verb_counts.most_common(1)[0]
    if count / len(scenes) > 0.4:
        errors.append(
            f"visual verb '{verb}' appears in {count}/{len(scenes)} "
            "(maximum is 40%)"
        )

    if not any(scene.get("role") == "caution" for scene in scenes):
        errors.append("pack needs at least one caution scene")
    if not any(scene.get("role") in {"integrate", "coda"} for scene in scenes):
        errors.append("pack needs an integration or coda scene")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    errors = validate(args.spec)
    if errors:
        print(f"FAIL {args.spec}")
        for error in errors:
            print(f"  - {error}")
        return 1
    data = json.loads(args.spec.read_text())
    print(
        f"PASS {args.spec}: {len(data['scenes'])} shaders, "
        f"{len(set(s['composition'] for s in data['scenes']))} compositions, "
        f"{len(set(s['verb'] for s in data['scenes']))} visual verbs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
