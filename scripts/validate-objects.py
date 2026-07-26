#!/usr/bin/env python3
"""Validate truth-map repository objects.

This is a draft-production validator for the current file artifacts. It does
not try to be a full JSON Schema implementation yet; it catches the object
integrity problems that block automation:

- duplicate EO IDs
- RO question-link typos
- missing candidate falsifiers
- missing EO syllogism/state-of-play fields
- non-canonical argument dossier shape
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CORRESPONDENCE_STATUSES = {
    "BRIDGES",
    "SUBSUMES",
    "CONTRADICTS",
    "OVERLAPS",
    "DIFFERENT",
    "needs_review",
}
CRITIQUE_PAIR_STATUSES = {
    "open",
    "answered",
    "sustained",
    "rejected",
    "needs_review",
}


@dataclass
class ValidationIssue:
    severity: str
    code: str
    path: str
    message: str


def repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [
            ValidationIssue(
                "error",
                "invalid_json",
                repo_path(path),
                f"Invalid JSON: {exc}",
            )
        ]


def iter_eo_files(root: Path = ROOT) -> list[Path]:
    base = root / "content" / "essay-objects"
    if not base.exists():
        return []
    paths: list[Path] = []
    for child in sorted(base.iterdir()):
        if child.is_file() and child.suffix == ".json":
            paths.append(child)
        elif child.is_dir() and (child / "eo.json").exists():
            paths.append(child / "eo.json")
    return paths


def validate_eo_file(path: Path) -> list[ValidationIssue]:
    data, issues = load_json(path)
    if data is None:
        return issues

    required = ("eo_id", "schema_version", "title", "status", "syllogism", "state_of_play")
    for key in required:
        if key not in data:
            issues.append(
                ValidationIssue("error", "eo_missing_field", repo_path(path), f"EO missing `{key}`")
            )

    syllogism = data.get("syllogism", {})
    for key in ("pratijna", "hetu", "udaharana", "upanaya", "nigamana"):
        if key not in syllogism:
            issues.append(
                ValidationIssue(
                    "error",
                    "eo_missing_syllogism_member",
                    repo_path(path),
                    f"EO syllogism missing `{key}`",
                )
            )

    candidates = data.get("candidates", [])
    if len(candidates) < 2:
        issues.append(
            ValidationIssue("error", "eo_too_few_candidates", repo_path(path), "EO needs 2+ candidates")
        )

    state = data.get("state_of_play", {})
    for key in ("summary", "what_survives", "what_is_weakened", "what_would_change_our_mind"):
        if key not in state:
            issues.append(
                ValidationIssue(
                    "error",
                    "eo_missing_state_of_play_field",
                    repo_path(path),
                    f"EO state_of_play missing `{key}`",
                )
            )

    return issues


def validate_all_eos(root: Path = ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, Path] = {}
    for path in iter_eo_files(root):
        data, load_issues = load_json(path)
        issues.extend(load_issues)
        if data is None:
            continue
        eo_id = data.get("eo_id")
        if eo_id:
            if eo_id in seen:
                issues.append(
                    ValidationIssue(
                        "error",
                        "duplicate_eo_id",
                        repo_path(path),
                        f"Duplicate EO id `{eo_id}` also appears in {repo_path(seen[eo_id])}",
                    )
                )
            else:
                seen[str(eo_id)] = path
        issues.extend(validate_eo_file(path))
    return issues


def validate_ro_file(path: Path) -> list[ValidationIssue]:
    data, issues = load_json(path)
    if data is None:
        return issues

    required = ("ro_id", "schema_version", "title", "status", "current_version", "sources", "body")
    for key in required:
        if key not in data:
            issues.append(
                ValidationIssue("error", "ro_missing_field", repo_path(path), f"RO missing `{key}`")
            )

    if "bears_on_quequestions" in data:
        issues.append(
            ValidationIssue(
                "error",
                "ro_bears_on_questions_typo",
                repo_path(path),
                "RO uses `bears_on_quequestions`; expected `bears_on_questions`",
            )
        )

    if data.get("body") == []:
        issues.append(
            ValidationIssue("error", "ro_empty_body", repo_path(path), "RO body must contain passages")
        )

    return issues


def iter_ro_files(root: Path = ROOT) -> list[Path]:
    base = root / "content" / "research-objects"
    if not base.exists():
        return []
    return sorted(base.glob("*/ro.json"))


def validate_all_ros(root: Path = ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, Path] = {}
    for path in iter_ro_files(root):
        data, load_issues = load_json(path)
        issues.extend(load_issues)
        if data is None:
            continue
        ro_id = data.get("ro_id")
        if ro_id:
            if ro_id in seen:
                issues.append(
                    ValidationIssue(
                        "error",
                        "duplicate_ro_id",
                        repo_path(path),
                        f"Duplicate RO id `{ro_id}` also appears in {repo_path(seen[ro_id])}",
                    )
                )
            else:
                seen[str(ro_id)] = path
        issues.extend(validate_ro_file(path))
    return issues


def validate_dossier_file(path: Path) -> list[ValidationIssue]:
    data, issues = load_json(path)
    if data is None:
        return issues

    if data.get("artifact_type") != "argument_fabric_dossier":
        issues.append(
            ValidationIssue(
                "error",
                "dossier_wrong_artifact_type",
                repo_path(path),
                "Argument dossier must use artifact_type `argument_fabric_dossier`",
            )
        )

    for key in ("question_id", "question", "candidate_explanations", "cruxes"):
        if key not in data:
            issues.append(
                ValidationIssue(
                    "error",
                    "dossier_missing_field",
                    repo_path(path),
                    f"Dossier missing `{key}`",
                )
            )

    for candidate in data.get("candidate_explanations", []):
        candidate_id = candidate.get("candidate_id", "<missing>")
        if not candidate.get("falsifiers"):
            issues.append(
                ValidationIssue(
                    "error",
                    "candidate_missing_falsifier",
                    repo_path(path),
                    f"Candidate `{candidate_id}` has no falsifier",
                )
            )
        if not candidate.get("hard_to_vary_core"):
            issues.append(
                ValidationIssue(
                    "warning",
                    "candidate_missing_hard_to_vary_core",
                    repo_path(path),
                    f"Candidate `{candidate_id}` has no hard_to_vary_core",
                )
            )

    return issues


def iter_dossier_files(root: Path = ROOT) -> list[Path]:
    base = root / "content" / "source-metaphysics"
    if not base.exists():
        return []
    return sorted(base.glob("*.argument.json"))


def validate_all_dossiers(root: Path = ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, Path] = {}
    for path in iter_dossier_files(root):
        data, load_issues = load_json(path)
        issues.extend(load_issues)
        if data is None:
            continue
        question_id = data.get("question_id")
        if question_id:
            if question_id in seen:
                issues.append(
                    ValidationIssue(
                        "error",
                        "duplicate_dossier_question_id",
                        repo_path(path),
                        f"Duplicate dossier question id `{question_id}` also appears in {repo_path(seen[question_id])}",
                    )
                )
            else:
                seen[str(question_id)] = path
        issues.extend(validate_dossier_file(path))
    return issues


def iter_source_map_files(root: Path = ROOT) -> list[Path]:
    base = root / "content" / "source-metaphysics"
    if not base.exists():
        return []
    paths = set(base.glob("*.map.json"))
    paths.update(base.glob("*-map.json"))
    return sorted(paths)


def validate_source_map_file(path: Path) -> list[ValidationIssue]:
    data, issues = load_json(path)
    if data is None:
        return issues

    if data.get("artifact_type") != "argument_fabric_source_map":
        issues.append(
            ValidationIssue(
                "error",
                "source_map_wrong_artifact_type",
                repo_path(path),
                "Source map must use artifact_type `argument_fabric_source_map`",
            )
        )

    for key in ("question_id", "nnexpr_mappings", "argument_edges"):
        if key not in data:
            issues.append(
                ValidationIssue(
                    "error",
                    "source_map_missing_field",
                    repo_path(path),
                    f"Source map missing `{key}`",
                )
            )

    if data.get("bridge_probe_logic") and "structural_correspondences" not in data:
        issues.append(
            ValidationIssue(
                "error",
                "source_map_missing_structural_correspondences",
                repo_path(path),
                "Source map with bridge_probe_logic must declare `structural_correspondences[]`",
            )
        )

    if data.get("state_of_play_delta") and "directional_critique_pairs" not in data:
        issues.append(
            ValidationIssue(
                "error",
                "source_map_missing_directional_critique_pairs",
                repo_path(path),
                "Source map with state_of_play_delta must declare `directional_critique_pairs[]`",
            )
        )

    for index, row in enumerate(data.get("structural_correspondences", []) or [], start=1):
        required = (
            "correspondence_id",
            "left_term",
            "left_scope",
            "right_term",
            "right_scope",
            "shared_structure",
            "important_difference",
            "status",
        )
        for key in required:
            if key not in row:
                issues.append(
                    ValidationIssue(
                        "error",
                        "source_map_correspondence_missing_field",
                        repo_path(path),
                        f"structural_correspondences[{index}] missing `{key}`",
                    )
                )
        status = row.get("status")
        if status is not None and status not in CORRESPONDENCE_STATUSES:
            issues.append(
                ValidationIssue(
                    "error",
                    "source_map_invalid_correspondence_status",
                    repo_path(path),
                    f"structural_correspondences[{index}] has invalid status `{status}`",
                )
            )

    for index, row in enumerate(data.get("directional_critique_pairs", []) or [], start=1):
        required = (
            "pair_id",
            "critic_lens",
            "target_lens",
            "reveals_about_target",
            "pressure_type",
            "target_response_required",
        )
        for key in required:
            if key not in row:
                issues.append(
                    ValidationIssue(
                        "error",
                        "source_map_critique_pair_missing_field",
                        repo_path(path),
                        f"directional_critique_pairs[{index}] missing `{key}`",
                    )
                )
        status = row.get("status", "open")
        if status not in CRITIQUE_PAIR_STATUSES:
            issues.append(
                ValidationIssue(
                    "error",
                    "source_map_invalid_critique_pair_status",
                    repo_path(path),
                    f"directional_critique_pairs[{index}] has invalid status `{status}`",
                )
            )

    return issues


def validate_all_source_maps(root: Path = ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, Path] = {}
    for path in iter_source_map_files(root):
        data, load_issues = load_json(path)
        issues.extend(load_issues)
        if data is None:
            continue
        map_key = data.get("source_packet_id") or str(path)
        question_id = data.get("question_id")
        if question_id and map_key:
            unique_key = f"{question_id}:{map_key}"
            if unique_key in seen:
                issues.append(
                    ValidationIssue(
                        "error",
                        "duplicate_source_map_key",
                        repo_path(path),
                        f"Duplicate source map key `{unique_key}` also appears in {repo_path(seen[unique_key])}",
                    )
                )
            else:
                seen[unique_key] = path
        issues.extend(validate_source_map_file(path))
    return issues


def validate_repo(root: Path = ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_all_eos(root))
    issues.extend(validate_all_ros(root))
    issues.extend(validate_all_dossiers(root))
    issues.extend(validate_all_source_maps(root))
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate truth-map object files")
    parser.add_argument("--root", default=str(ROOT), help="Repository root")
    parser.add_argument(
        "--kind",
        choices=("all", "eo", "ro", "dossier", "source-map"),
        default="all",
        help="Object family to validate",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.root)
    if args.kind == "eo":
        issues = validate_all_eos(root)
    elif args.kind == "ro":
        issues = validate_all_ros(root)
    elif args.kind == "dossier":
        issues = validate_all_dossiers(root)
    elif args.kind == "source-map":
        issues = validate_all_source_maps(root)
    else:
        issues = validate_repo(root)

    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}")

    if any(issue.severity == "error" for issue in issues):
        sys.exit(1)


if __name__ == "__main__":
    main()
