#!/usr/bin/env python3
"""Conservative bridge-status probe for argument source maps.

This wrapper does not prove bridge relations. It evaluates declared probe
results and negative controls, then returns the strongest relation licensed by
those results. Missing proof defaults to OVERLAPS when shared structure is
declared, never to BRIDGES.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


POSITIVE_PASS = {"PROVED"}
NEGATIVE_PASS = {"NOT_PROVED", "UNPROVED", "REFUTED", "OUTSIDE_FORMAL"}
KNOWN_STATUSES = POSITIVE_PASS | NEGATIVE_PASS | {"PARTIAL", "HOLLOW", "needs_review"}


@dataclass
class ProbeCheck:
    test_id: str
    probe: str
    expected: str
    actual: str
    passed: bool
    role: str
    rationale: str | None = None


@dataclass
class BridgeProbeResult:
    bridge_probe_id: str | None
    left_term: str | None
    right_term: str | None
    status: str
    confidence_language: str
    positive_checks: list[ProbeCheck]
    negative_controls: list[ProbeCheck]
    notes: list[str]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_status(row: dict[str, Any]) -> str:
    status = (
        row.get("actual_status")
        or row.get("status")
        or row.get("formal_status")
        or "UNPROVED"
    )
    status = str(status)
    return status if status in KNOWN_STATUSES else "needs_review"


def check_passed(expected: str, actual: str) -> bool:
    if expected == "PROVED":
        return actual in POSITIVE_PASS
    if expected == "NOT_PROVED":
        return actual in NEGATIVE_PASS
    return actual == expected


def check_role(row: dict[str, Any]) -> str:
    expected = str(row.get("required_status_for_merge", "PROVED"))
    test_id = str(row.get("test_id", ""))
    probe = str(row.get("probe", ""))
    if expected == "NOT_PROVED" or "negative-control" in test_id or "negative" in probe.lower():
        return "negative_control"
    return "positive"


def probe_checks(bridge_logic: dict[str, Any]) -> tuple[list[ProbeCheck], list[ProbeCheck]]:
    positives: list[ProbeCheck] = []
    negatives: list[ProbeCheck] = []
    for row in bridge_logic.get("formal_tests", []) or []:
        expected = str(row.get("required_status_for_merge", "PROVED"))
        actual = normalized_status(row)
        role = check_role(row)
        check = ProbeCheck(
            test_id=str(row.get("test_id", "")),
            probe=str(row.get("probe", "")),
            expected=expected,
            actual=actual,
            passed=check_passed(expected, actual),
            role=role,
            rationale=row.get("rationale"),
        )
        if role == "negative_control":
            negatives.append(check)
        else:
            positives.append(check)
    return positives, negatives


def infer_direction(probe: str) -> str | None:
    if "->" not in probe:
        return None
    left, right = [part.strip() for part in probe.split("->", 1)]
    if not left or not right:
        return None
    return f"{left}->{right}"


def classify_bridge(
    *,
    positives: list[ProbeCheck],
    negatives: list[ProbeCheck],
    has_shared_structure: bool,
) -> tuple[str, list[str]]:
    notes: list[str] = []
    failed_negatives = [check for check in negatives if not check.passed]
    if failed_negatives:
        notes.append("At least one negative control failed; bridge upgrade blocked.")
        return "DIFFERENT", notes

    proved_positive = [check for check in positives if check.passed]
    pending_positive = [check for check in positives if not check.passed]

    directions = {infer_direction(check.probe) for check in proved_positive}
    directions.discard(None)

    if positives and not pending_positive and len(directions) >= 2:
        notes.append("Bidirectional positive probes passed and negative controls did not fail.")
        return "BRIDGES", notes

    if len(proved_positive) == 1:
        notes.append("Only one positive direction passed; relation can at most subsume.")
        return "SUBSUMES", notes

    if has_shared_structure:
        notes.append("Shared structure is declared, but positive bridge probes are unproved or incomplete.")
        return "OVERLAPS", notes

    notes.append("No shared structure or successful probe licenses a relation.")
    return "needs_review", notes


def correspondence_for_bridge(source_map: dict[str, Any], bridge_id: str | None) -> dict[str, Any]:
    rows = source_map.get("structural_correspondences", []) or []
    if bridge_id:
        for row in rows:
            if row.get("bridge_probe_id") == bridge_id:
                return row
    return rows[0] if rows else {}


def evaluate_source_map(source_map: dict[str, Any], bridge_id: str | None = None) -> BridgeProbeResult:
    bridge_logic = source_map.get("bridge_probe_logic") or {}
    correspondence = correspondence_for_bridge(source_map, bridge_id)
    selected_bridge_id = bridge_id or correspondence.get("bridge_probe_id")
    positives, negatives = probe_checks(bridge_logic)
    has_shared_structure = bool(correspondence.get("shared_structure")) or bool(
        (bridge_logic.get("candidate_pair") or {}).get("surface_similarity")
    )
    status, notes = classify_bridge(
        positives=positives,
        negatives=negatives,
        has_shared_structure=has_shared_structure,
    )
    if correspondence.get("status") == "BRIDGES" and status != "BRIDGES":
        notes.append("Declared correspondence is stronger than probe result; keep probe result.")
    return BridgeProbeResult(
        bridge_probe_id=selected_bridge_id,
        left_term=correspondence.get("left_term") or (bridge_logic.get("candidate_pair") or {}).get("nanavira_node"),
        right_term=correspondence.get("right_term") or (bridge_logic.get("candidate_pair") or {}).get("dharmakirti_node"),
        status=status,
        confidence_language=(
            "probe-derived; conservative; no bridge upgrade without bidirectional proof and passing negative controls"
        ),
        positive_checks=positives,
        negative_controls=negatives,
        notes=notes,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe a source-map bridge relation conservatively")
    parser.add_argument("--map", required=True, help="Path to argument_fabric_source_map JSON")
    parser.add_argument("--bridge-id", help="Bridge probe id to evaluate")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    result = evaluate_source_map(load_json(Path(args.map)), bridge_id=args.bridge_id)
    data = asdict(result)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(f"Bridge: {result.bridge_probe_id or '<none>'}")
        print(f"Status: {result.status}")
        for note in result.notes:
            print(f"- {note}")


if __name__ == "__main__":
    main()
