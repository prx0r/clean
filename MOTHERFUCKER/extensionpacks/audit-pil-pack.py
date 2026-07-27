#!/usr/bin/env python3
"""Inventory Pillow visual packs without executing them.

This is deliberately an AST audit, not an automatic converter. It separates
duplicated renderer infrastructure from visual mechanisms that can expand the
Skia capability library.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any


INFRASTRUCTURE_TERMS = {
    "background",
    "rgba_layer",
    "load_font",
    "centered_text",
    "glow_circle",
    "glow_line",
    "partial_polyline",
    "smoothstep",
    "ease",
    "ease_out",
    "pulse",
    "seal",
    "render_scene",
    "render_all",
    "render_video",
    "concat",
    "contact_sheet",
    "validate",
}

CLUSTERS = {
    "quantitative-and-evidence": (
        "rate", "plot", "matrix", "grid", "count", "ladder", "taxonomy",
        "evidence", "spectrum", "comparison", "measure",
    ),
    "boundary-and-selection": (
        "barrier", "wall", "gate", "filter", "membrane", "veil", "aperture",
        "boundary", "lens", "percept",
    ),
    "sequence-and-time": (
        "time", "sequence", "cycle", "clock", "window", "memory", "breath",
        "mantra", "runtime", "chain",
    ),
    "network-and-causality": (
        "network", "causal", "feedback", "loom", "reed", "dependency",
        "receiver", "propagation", "coordination",
    ),
    "nested-scale-and-containment": (
        "egg", "nested", "world", "body", "cosmic", "scale", "shell",
        "chamber", "layer", "cutaway",
    ),
    "field-and-transformation": (
        "field", "wave", "tunnel", "landscape", "morph", "transform",
        "condensation", "descent", "ascent", "flow", "current",
    ),
    "radial-and-generative": (
        "ring", "orbit", "wheel", "mandala", "cosmogram", "bindu", "triangle",
        "lotus", "flame", "direction", "compass",
    ),
    "observer-and-recognition": (
        "observer", "attention", "recognition", "mirror", "self", "point",
        "view", "perspective", "world-model",
    ),
}


def literal(node: ast.AST | None) -> Any:
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        if isinstance(node, ast.Name):
            return {"$name": node.id}
        try:
            return {"$expr": ast.unparse(node)}
        except Exception:
            return {"$expr": type(node).__name__}


def assignment_name(node: ast.Assign | ast.AnnAssign) -> str | None:
    target = node.target if isinstance(node, ast.AnnAssign) else (node.targets[0] if node.targets else None)
    return target.id if isinstance(target, ast.Name) else None


def scene_fields(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Scene":
            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
            return fields
    return []


def visual_registry(tree: ast.Module) -> dict[str, str]:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        if assignment_name(node) != "VISUALS":
            continue
        value = node.value
        if not isinstance(value, ast.Dict):
            continue
        result = {}
        for key, renderer in zip(value.keys, value.values):
            key_value = literal(key)
            if not isinstance(key_value, str):
                continue
            result[key_value] = renderer.id if isinstance(renderer, ast.Name) else ast.unparse(renderer)
        return result
    return {}


def palette_constants(tree: ast.Module) -> dict[str, list[int]]:
    colors: dict[str, list[int]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        name = assignment_name(node)
        value = literal(node.value)
        if (
            name
            and name.isupper()
            and isinstance(value, tuple)
            and len(value) in (3, 4)
            and all(isinstance(channel, int) and 0 <= channel <= 255 for channel in value)
        ):
            colors[name] = list(value)
    return colors


def scenes(tree: ast.Module, fields: list[str]) -> list[dict[str, Any]]:
    records = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "Scene":
            continue
        record = {}
        for index, argument in enumerate(node.args):
            key = fields[index] if index < len(fields) else f"arg{index}"
            record[key] = literal(argument)
        for keyword in node.keywords:
            if keyword.arg:
                record[keyword.arg] = literal(keyword.value)
        records.append(record)
    return records


def cluster(values: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {name: [] for name in CLUSTERS}
    grouped["uncategorized"] = []
    for value in sorted(set(values)):
        haystack = value.lower().replace("_", " ").replace("-", " ")
        matches = [
            name for name, terms in CLUSTERS.items()
            if any(term in haystack for term in terms)
        ]
        if not matches:
            grouped["uncategorized"].append(value)
        else:
            for name in matches:
                grouped[name].append(value)
    return {name: members for name, members in grouped.items() if members}


def audit(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf8")
    tree = ast.parse(source, filename=str(path))
    fields = scene_fields(tree)
    scene_records = scenes(tree, fields)
    registry = visual_registry(tree)
    function_names = [
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    infrastructure = sorted({
        name for name in function_names
        if name in INFRASTRUCTURE_TERMS
        or any(term in name for term in ("render", "ffmpeg", "contact", "validate", "background"))
    })
    mechanism_values = list(registry)
    for scene in scene_records:
        for key in ("visual", "technique", "mode"):
            value = scene.get(key)
            if isinstance(value, str):
                mechanism_values.append(value)
    scene_index = []
    for index, scene in enumerate(scene_records, start=1):
        scene_index.append({
            "index": index,
            "id": scene.get("id"),
            "title": scene.get("title"),
            "visual": scene.get("visual"),
            "mode": scene.get("mode"),
            "group": scene.get("group"),
            "technique": scene.get("technique"),
            "tags": scene.get("tags", []),
            "duration": scene.get("duration"),
        })
    return {
        "file": path.name,
        "path": str(path.resolve()),
        "sceneDataclassFields": fields,
        "sceneCount": len(scene_records),
        "palette": palette_constants(tree),
        "visualRegistry": registry,
        "functionCount": len(function_names),
        "duplicatedInfrastructure": infrastructure,
        "mechanismClusters": cluster(mechanism_values),
        "sceneIndex": scene_index,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Pillow .py files to inspect")
    parser.add_argument("--out", type=Path, help="Write JSON to this path")
    args = parser.parse_args()
    reports = [audit(path) for path in args.paths]
    clusters = Counter()
    for report in reports:
        for name, members in report["mechanismClusters"].items():
            clusters[name] += len(members)
    output = {
        "version": "1.0",
        "method": "Python AST inspection; source files are never executed.",
        "classificationRule": (
            "Renderer infrastructure stays in the Skia kernel. Palette and chrome become style tokens. "
            "Relation-bearing visuals become mechanisms. Small changes become parameters or presets. "
            "One-off compositions remain examples."
        ),
        "totals": {
            "files": len(reports),
            "scenes": sum(report["sceneCount"] for report in reports),
            "uniqueVisualRegistryKeys": len({
                key for report in reports for key in report["visualRegistry"]
            }),
            "clusterMemberships": dict(sorted(clusters.items())),
        },
        "files": reports,
    }
    payload = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
