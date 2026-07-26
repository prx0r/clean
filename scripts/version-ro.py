#!/usr/bin/env python3
"""
version-ro.py — Auto-detect RO changes and bump version.

Called by git pre-commit hook or manually:
    python scripts/version-ro.py --file content/research-objects/ro-foo/ro.json

Detects: new passages, edited passages, source changes, question changes.
Auto-bumps: major, minor, or patch based on change type.
"""

import argparse
import json
import sys
from pathlib import Path


def classify_change(old: dict, new: dict) -> str:
    old_passages = {p["passage_id"]: p for p in old.get("body", [])}
    new_passages = {p["passage_id"]: p for p in new.get("body", [])}
    old_sources = {s["source_id"] for s in old.get("sources", [])}
    new_sources = {s["source_id"] for s in new.get("sources", [])}

    changes = set()
    for pid in new_passages:
        if pid not in old_passages:
            changes.add("passage_added")
    for pid in old_passages:
        if pid in new_passages and old_passages[pid] != new_passages[pid]:
            changes.add("passage_edited")
    if old_sources != new_sources:
        changes.add("sources_changed")
    if old.get("bears_on_questions") != new.get("bears_on_questions"):
        changes.add("questions_changed")
    if old.get("status") != new.get("status"):
        changes.add("status_changed")

    # Bulk rewrite: many passages edited at once
    if "passage_edited" in changes and len(changes) > 5:
        return "major"
    if "sources_changed" in changes or "questions_changed" in changes:
        return "minor"
    if "passage_added" in changes:
        return "minor"
    if "passage_edited" in changes:
        return "patch"
    if "status_changed" in changes:
        return "major"
    return "patch"


def bump_version(old: str, change: str) -> str:
    major, minor, patch = map(int, old.split("."))
    if change == "major":
        return f"{major + 1}.0.0"
    if change == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main():
    parser = argparse.ArgumentParser(description="Auto-bump RO version")
    parser.add_argument("--file", required=True, help="Path to RO JSON file")
    parser.add_argument("--mode", choices=["check", "auto-bump"], default="check")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Read current file
    current = json.loads(path.read_text())
    old_version = current.get("current_version", "0.1.0")

    # In check mode, compare against git HEAD if available
    if args.mode == "check":
        import subprocess
        try:
            rel = path.relative_to(Path.cwd())
            result = subprocess.run(
                ["git", "show", f"HEAD:{rel}"],
                capture_output=True, text=True, check=True
            )
            old = json.loads(result.stdout)
            change = classify_change(old, current)
            new_version = bump_version(old_version, change)
            print(f"{path.name}: {old_version} → {new_version} ({change})")
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            print(f"{path.name}: no git history, setting v1.0.0")

    elif args.mode == "auto-bump":
        # Apply version bump to file in-place
        import subprocess
        try:
            rel = path.relative_to(Path.cwd())
            result = subprocess.run(
                ["git", "show", f"HEAD:{rel}"],
                capture_output=True, text=True, check=True
            )
            old = json.loads(result.stdout)
            change = classify_change(old, current)
            new_version = bump_version(old_version, change)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            change = "major"
            new_version = "1.0.0"

        current["current_version"] = new_version
        path.write_text(json.dumps(current, indent=2))
        print(f"{path.name}: bumped to {new_version} ({change})")


if __name__ == "__main__":
    main()
