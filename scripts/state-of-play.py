#!/usr/bin/env python3
"""Generate graph-derived state-of-play reports.

This script is the first deterministic synthesis layer. It does not ask an LLM
to decide what survives. It reads the argument-fabric rows and computes a
transparent report:

- candidate support/pressure
- open cruxes
- unresolved correspondences
- directional critique pairs
- argument causal-power ranking
- next tests

When no DB has been populated yet, it can bootstrap a question graph from the
local dossier/source-map files. That bootstrap is still graph ingestion; the
report is not copied from EO prose.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from truthengine_working import TruthMapSQLiteDB, build_truth_map_db


ACTIVE_FALSIFIER_STATUSES = {
    "accepted",
    "confirmed",
    "observed",
    "passed",
    "satisfied",
    "tested_failed",
    "triggered",
    "validated",
}


def safe_id(value: str) -> str:
    return (
        str(value)
        .replace(":", "-")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
        .lower()
    )


def load_ingest_dossier_module():
    path = ROOT / "scripts" / "ingest-dossier.py"
    spec = importlib.util.spec_from_file_location("ingest_dossier_module", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def json_loads(value: str | None, fallback: Any) -> Any:
    if value is None:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def question_slug(question_id: str) -> str:
    return question_id.replace(":", "-")


def default_dossier_path(question_id: str) -> Path:
    return ROOT / "content" / "source-metaphysics" / f"{question_slug(question_id)}.argument.json"


def default_source_map_paths(question_id: str) -> list[Path]:
    base = ROOT / "content" / "source-metaphysics"
    slug = question_slug(question_id)
    paths = set(base.glob(f"{slug}*.map.json"))
    paths.update(base.glob(f"{slug}*map.json"))
    return sorted(paths)


def bootstrap_question_graph(db: TruthMapSQLiteDB, question_id: str) -> dict[str, Any]:
    ingest = load_ingest_dossier_module()
    result: dict[str, Any] = {"dossier": None, "source_maps": []}

    dossier_path = default_dossier_path(question_id)
    if dossier_path.exists():
        result["dossier"] = ingest.ingest_dossier(db, dossier_path)

    for map_path in default_source_map_paths(question_id):
        result["source_maps"].append(
            {"path": str(map_path), "result": ingest.ingest_source_map(db, map_path)}
        )

    db.conn.commit()
    return result


def graph_has_candidates(db: TruthMapSQLiteDB, question_id: str) -> bool:
    row = db.conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM argument_nodes
        WHERE question_id = ? AND node_type = 'candidate_explanation'
        """,
        (question_id,),
    ).fetchone()
    return bool(row and int(row["count"]) > 0)


def candidate_rows(db: TruthMapSQLiteDB, question_id: str) -> list[dict[str, Any]]:
    rows = db.conn.execute(
        """
        SELECT node_id, title, statement, tradition_scope, status, payload
        FROM argument_nodes
        WHERE question_id = ? AND node_type = 'candidate_explanation'
        ORDER BY node_id
        """,
        (question_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["payload"] = json_loads(item.get("payload"), {})
        out.append(item)
    return out


def open_crux_rows(db: TruthMapSQLiteDB, question_id: str) -> list[dict[str, Any]]:
    rows = db.conn.execute(
        """
        SELECT node_id, title, statement, status, payload
        FROM argument_nodes
        WHERE question_id = ? AND node_type = 'crux'
        ORDER BY node_id
        """,
        (question_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def source_gate_multiplier(source_payload: dict[str, Any]) -> float:
    outcome = source_payload.get("gate_outcome")
    return {
        "accepted": 1.0,
        "accepted_with_penalty": 0.55,
        "needs_review": 0.15,
        "outside_formal": 0.25,
        "hollow": 0.0,
        "refuted": 0.0,
    }.get(str(outcome), 0.5)


def target_multiplier(target_type: str) -> float:
    return {
        "candidate_explanation": 1.5,
        "crux": 1.25,
        "bridge": 1.0,
        "claim": 0.75,
    }.get(target_type, 1.0)


def edge_records(db: TruthMapSQLiteDB, question_id: str) -> list[dict[str, Any]]:
    rows = db.conn.execute(
        """
        SELECT
          ae.edge_id,
          ae.source_node_id,
          ae.target_node_id,
          ae.edge_type,
          ae.strength,
          ae.polarity,
          ae.relation_rationale,
          ae.payload AS edge_payload,
          src.node_type AS source_type,
          src.title AS source_title,
          src.statement AS source_statement,
          src.status AS source_status,
          src.payload AS source_payload,
          tgt.node_type AS target_type,
          tgt.title AS target_title,
          tgt.statement AS target_statement,
          tgt.status AS target_status
        FROM argument_edges ae
        JOIN argument_nodes src ON src.node_id = ae.source_node_id
        JOIN argument_nodes tgt ON tgt.node_id = ae.target_node_id
        WHERE COALESCE(src.question_id, tgt.question_id) = ?
        ORDER BY ae.strength DESC, ae.edge_id
        """,
        (question_id,),
    ).fetchall()
    records = []
    for row in rows:
        record = dict(row)
        record["edge_payload"] = json_loads(record.get("edge_payload"), {})
        record["source_payload"] = json_loads(record.get("source_payload"), {})
        record["causal_power"] = (
            float(record["strength"])
            * source_gate_multiplier(record["source_payload"])
            * target_multiplier(record["target_type"])
        )
        records.append(record)
    return records


def candidate_scoreboard(
    candidates: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    scores = {
        candidate["node_id"]: {
            "candidate": candidate,
            "support": 0.0,
            "pressure": 0.0,
            "direct_pressure": 0.0,
            "crux_pressure": 0.0,
            "bridge": 0.0,
            "support_edges": [],
            "pressure_edges": [],
            "bridge_edges": [],
            "pending_falsifiers": [],
        }
        for candidate in candidates
    }

    for edge in edges:
        target_id = edge["target_node_id"]
        if target_id not in scores:
            continue
        if edge["edge_type"] in {"supports", "instantiates", "subsumes"}:
            scores[target_id]["support"] += edge["causal_power"]
            scores[target_id]["support_edges"].append(edge)
        elif edge["edge_type"] in {"attacks", "contradicts", "falsified_by"}:
            if edge["edge_type"] == "falsified_by" and edge["source_type"] == "falsifier":
                source_status = str(edge.get("source_status") or "").lower()
                if source_status not in ACTIVE_FALSIFIER_STATUSES:
                    scores[target_id]["pending_falsifiers"].append(edge)
                    continue
            is_crux_pressure = (
                edge["source_type"] == "crux"
                or edge.get("edge_payload", {}).get("relation") == "candidate_pressure"
            )
            if is_crux_pressure:
                scores[target_id]["crux_pressure"] += edge["causal_power"]
                scores[target_id]["pressure"] += edge["causal_power"] * 0.35
            else:
                scores[target_id]["direct_pressure"] += edge["causal_power"]
                scores[target_id]["pressure"] += edge["causal_power"]
            scores[target_id]["pressure_edges"].append(edge)
        elif edge["edge_type"] == "bridges":
            scores[target_id]["bridge"] += edge["causal_power"]
            scores[target_id]["bridge_edges"].append(edge)
        elif edge["edge_type"] == "outside_formal":
            scores[target_id]["pressure"] += edge["causal_power"] * 0.5
            scores[target_id]["pressure_edges"].append(edge)

    return scores


def correspondence_rows(db: TruthMapSQLiteDB, question_id: str) -> list[dict[str, Any]]:
    rows = db.conn.execute(
        """
        SELECT *
        FROM structural_correspondences
        WHERE question_id = ?
        ORDER BY status, correspondence_id
        """,
        (question_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def critique_rows(db: TruthMapSQLiteDB, question_id: str) -> list[dict[str, Any]]:
    rows = db.conn.execute(
        """
        SELECT *
        FROM directional_critique_pairs
        WHERE question_id = ?
        ORDER BY pressure_type, pair_id
        """,
        (question_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["supporting_claim_ids"] = json_loads(item.get("supporting_claim_ids"), [])
        item["crux_ids"] = json_loads(item.get("crux_ids"), [])
        out.append(item)
    return out


def snapshot_context(db: TruthMapSQLiteDB, question_id: str) -> dict[str, Any]:
    row = db.conn.execute(
        """
        SELECT *
        FROM state_of_play_snapshots
        WHERE question_id = ?
        ORDER BY created_at DESC, snapshot_id DESC
        LIMIT 1
        """,
        (question_id,),
    ).fetchone()
    if not row:
        return {}
    item = dict(row)
    for key in (
        "solved_at_levels",
        "live_candidates",
        "weakened_candidates",
        "defeated_candidates",
        "open_cruxes",
        "next_tests",
        "implications",
    ):
        item[key] = json_loads(item.get(key), [])
    item["provenance"] = json_loads(item.get("provenance"), {})
    return item


def strongest_argument_edges(edges: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    interesting = [
        edge
        for edge in edges
        if edge["source_type"] == "claim"
        and edge["edge_type"] in {"supports", "attacks", "bridges", "outside_formal"}
    ]
    interesting.sort(key=lambda edge: edge["causal_power"], reverse=True)
    return interesting[:limit]


def synthesize_best_answer(
    question_id: str,
    scores: dict[str, dict[str, Any]],
    cruxes: list[dict[str, Any]],
    critiques: list[dict[str, Any]],
    correspondences: list[dict[str, Any]],
) -> str:
    if not scores:
        return "No candidate graph exists yet."

    ranked = sorted(
        scores.values(),
        key=lambda item: (item["support"] + item["bridge"] - item["pressure"]),
        reverse=True,
    )
    top = ranked[0]["candidate"]
    top_title = top.get("title") or top["node_id"]

    open_crux_ids = {crux["node_id"] for crux in cruxes}
    local_to_universal_open = "crux:local-to-universal" in open_crux_ids
    manifestness_open = "crux:constructed-reflexivity-presupposes-manifestness" in open_crux_ids
    has_overlap = any(row["status"] == "OVERLAPS" for row in correspondences)

    parts = [f"{top_title} is the strongest local candidate in the current graph."]
    if "Structural reflexivity" in top_title or "structural" in top_title.lower():
        parts[0] = "Structural reflexivity is locally strengthened by accepted Nanavira argument edges."
    if local_to_universal_open:
        parts.append("Universal consciousness is not entailed while the local-to-universal crux remains open.")
    for critique in critiques:
        if critique["pressure_type"] == "universalization_gap":
            parts.append("Abhinavagupta is pressured at the universalization step, not refuted.")
        if critique["pressure_type"] == "manifestness_gap":
            parts.append("Abhinavagupta pressures Nanavira at manifestness: structural reflexivity may presuppose appearing rather than explain it.")
    if has_overlap:
        parts.append("The Nanavira-Dharmakirti bridge is OVERLAPS, not BRIDGES.")
    if manifestness_open:
        parts.append("The strongest next crux is whether structural reflexivity explains manifestness or presupposes it.")
    return " ".join(dict.fromkeys(parts))


def active_falsifier_edge(edge: dict[str, Any]) -> bool:
    return (
        edge["edge_type"] == "falsified_by"
        and edge["source_type"] == "falsifier"
        and str(edge.get("source_status") or "").lower() in ACTIVE_FALSIFIER_STATUSES
    )


def accepted_core_attack_edge(edge: dict[str, Any]) -> bool:
    payload = edge.get("edge_payload", {}) or {}
    if not payload.get("targets_core_commitment"):
        return False
    if edge["edge_type"] not in {"attacks", "contradicts", "falsified_by"}:
        return False
    gate_status = str(
        payload.get("attack_gate_status")
        or payload.get("gate_outcome")
        or edge.get("source_status")
        or ""
    )
    return gate_status in {
        "accepted",
        "accepted_with_penalty",
        "human_reviewed",
        "lean_verified",
        "tested_failed",
        "PROVED",
    }


def candidate_has_live_reformulation(edge: dict[str, Any]) -> bool:
    payload = edge.get("edge_payload", {}) or {}
    return bool(payload.get("candidate_has_live_reformulation", True))


def candidate_status_pressure(item: dict[str, Any]) -> dict[str, Any]:
    confirmed_falsifiers = [
        edge for edge in item["pressure_edges"] if active_falsifier_edge(edge)
    ]
    core_attacks = [
        edge for edge in item["pressure_edges"] if accepted_core_attack_edge(edge)
    ]
    decisive_core_attacks = [
        edge
        for edge in core_attacks
        if not candidate_has_live_reformulation(edge)
        or bool((edge.get("edge_payload", {}) or {}).get("decisive"))
    ]
    return {
        "confirmed_falsifier_pressure": sum(edge["causal_power"] for edge in confirmed_falsifiers),
        "core_attack_pressure": sum(edge["causal_power"] for edge in core_attacks),
        "decisive_core_attack_pressure": sum(edge["causal_power"] for edge in decisive_core_attacks),
        "confirmed_falsifier_count": len(confirmed_falsifiers),
        "core_attack_count": len(core_attacks),
        "decisive_core_attack_count": len(decisive_core_attacks),
    }


def candidate_status_lists(scores: dict[str, dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    live: list[str] = []
    weakened: list[str] = []
    defeated: list[str] = []
    for candidate_id, item in scores.items():
        candidate = item["candidate"]
        title = candidate.get("title") or candidate_id
        status_pressure = candidate_status_pressure(item)
        decisive_pressure = (
            status_pressure["confirmed_falsifier_pressure"]
            + status_pressure["decisive_core_attack_pressure"]
        )
        if decisive_pressure >= 1.0 and item["support"] == 0:
            defeated.append(title)
        else:
            live.append(title)
            if (
                status_pressure["confirmed_falsifier_pressure"] >= 0.2
                or status_pressure["core_attack_pressure"] >= 0.2
            ):
                weakened.append(title)
    return live, weakened, defeated


def collect_next_tests(
    snapshot: dict[str, Any],
    critiques: list[dict[str, Any]],
    correspondences: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[str]:
    tests: list[str] = []
    tests.extend(snapshot.get("next_tests", []))
    for critique in critiques:
        tests.append(critique["target_response_required"])
    for correspondence in correspondences:
        if correspondence["status"] != "BRIDGES":
            tests.append(
                f"Run bridge probe for {correspondence['left_term']} vs {correspondence['right_term']} with negative controls."
            )
    for candidate in candidates:
        for falsifier in candidate.get("payload", {}).get("falsifiers", []):
            if isinstance(falsifier, dict) and falsifier.get("condition"):
                tests.append(falsifier["condition"])
    out: list[str] = []
    seen: set[str] = set()
    for test in tests:
        if test and test not in seen:
            seen.add(test)
            out.append(test)
    return out[:12]


def persist_generated_snapshot(db: TruthMapSQLiteDB, synthesis: dict[str, Any]) -> str:
    question_id = synthesis["question_id"]
    row = db.conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM state_of_play_snapshots
        WHERE question_id = ? AND snapshot_id LIKE ?
        """,
        (question_id, f"sop:{safe_id(question_id)}:generated-%"),
    ).fetchone()
    index = int(row["count"]) + 1
    snapshot_id = f"sop:{safe_id(question_id)}:generated-{index:03d}"
    db.conn.execute(
        """
        INSERT OR REPLACE INTO state_of_play_snapshots
        (snapshot_id, question_id, current_best_answer, confidence_language,
         solved_at_levels, live_candidates, weakened_candidates, defeated_candidates,
         open_cruxes, next_tests, implications, provenance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot_id,
            question_id,
            synthesis["best_current_answer"],
            synthesis["confidence_language"],
            json.dumps(synthesis["solved_at_levels"], sort_keys=True),
            json.dumps(synthesis["live_candidates"], sort_keys=True),
            json.dumps(synthesis["weakened_candidates"], sort_keys=True),
            json.dumps(synthesis["defeated_candidates"], sort_keys=True),
            json.dumps([crux["node_id"] for crux in synthesis["open_cruxes"]], sort_keys=True),
            json.dumps(synthesis["next_tests"], sort_keys=True),
            json.dumps(synthesis["implications"], sort_keys=True),
            json.dumps(synthesis["provenance"], sort_keys=True),
        ),
    )
    db.conn.commit()
    return snapshot_id


def synthesize_state_of_play(
    db: TruthMapSQLiteDB,
    question_id: str,
    *,
    persist: bool = True,
) -> dict[str, Any]:
    candidates = candidate_rows(db, question_id)
    cruxes = open_crux_rows(db, question_id)
    edges = edge_records(db, question_id)
    scores = candidate_scoreboard(candidates, edges)
    correspondences = correspondence_rows(db, question_id)
    critiques = critique_rows(db, question_id)
    snapshot = snapshot_context(db, question_id)
    strongest = strongest_argument_edges(edges)
    live, weakened, defeated = candidate_status_lists(scores)
    next_tests = collect_next_tests(snapshot, critiques, correspondences, candidates)
    best_answer = synthesize_best_answer(question_id, scores, cruxes, critiques, correspondences)

    synthesis = {
        "question_id": question_id,
        "best_current_answer": best_answer,
        "confidence_language": "graph-derived, locally scoped",
        "solved_at_levels": ["none"],
        "live_candidates": live,
        "weakened_candidates": weakened,
        "defeated_candidates": defeated,
        "candidate_scores": {
            candidate_id: {
                "support": round(item["support"], 6),
                "pressure": round(item["pressure"], 6),
                "direct_pressure": round(item["direct_pressure"], 6),
                "crux_pressure": round(item["crux_pressure"], 6),
                "bridge": round(item["bridge"], 6),
                "pending_falsifier_count": len(item["pending_falsifiers"]),
                "confirmed_falsifier_count": candidate_status_pressure(item)[
                    "confirmed_falsifier_count"
                ],
                "core_attack_count": candidate_status_pressure(item)["core_attack_count"],
                "decisive_core_attack_count": candidate_status_pressure(item)[
                    "decisive_core_attack_count"
                ],
            }
            for candidate_id, item in scores.items()
        },
        "open_cruxes": cruxes,
        "unresolved_correspondences": [
            row for row in correspondences if row["status"] != "BRIDGES"
        ],
        "directional_critiques": critiques,
        "strongest_argument_edges": strongest,
        "next_tests": next_tests,
        "implications": snapshot.get("implications", []),
        "provenance": {
            "source": "argument_graph",
            "candidate_count": len(candidates),
            "edge_count": len(edges),
            "correspondence_count": len(correspondences),
            "critique_pair_count": len(critiques),
        },
    }
    if persist:
        synthesis["snapshot_id"] = persist_generated_snapshot(db, synthesis)
    return synthesis


def format_report(synthesis: dict[str, Any]) -> str:
    lines = [
        f"State of Play: {synthesis['question_id']}",
        "=" * (len(synthesis["question_id"]) + 16),
        "",
        "Best Current Answer:",
        f"  {synthesis['best_current_answer']}",
        "",
    ]

    if synthesis["live_candidates"]:
        lines.append("Live Candidates:")
        for title in synthesis["live_candidates"]:
            lines.append(f"  - {title}")
        lines.append("")

    if synthesis["weakened_candidates"]:
        lines.append("Under Pressure:")
        for title in synthesis["weakened_candidates"]:
            lines.append(f"  - {title}")
        lines.append("")

    if synthesis["open_cruxes"]:
        lines.append("Open Cruxes:")
        for crux in synthesis["open_cruxes"]:
            lines.append(f"  - {crux['node_id']}: {crux['statement']}")
        lines.append("")

    if synthesis["directional_critiques"]:
        lines.append("Bidirectional Critique:")
        for critique in synthesis["directional_critiques"]:
            lines.append(
                f"  - {critique['critic_lens']} -> {critique['target_lens']}: {critique['reveals_about_target']}"
            )
        lines.append("")

    if synthesis["unresolved_correspondences"]:
        lines.append("Unresolved Correspondences:")
        for row in synthesis["unresolved_correspondences"]:
            lines.append(
                f"  - {row['left_term']} / {row['right_term']}: {row['status']} ({row['important_difference']})"
            )
        lines.append("")

    if synthesis["strongest_argument_edges"]:
        lines.append("Highest Causal-Power Argument Edges:")
        for edge in synthesis["strongest_argument_edges"][:6]:
            lines.append(
                f"  - {edge['source_node_id']} -> {edge['target_node_id']} "
                f"[{edge['edge_type']}, power={edge['causal_power']:.3f}]: {edge['relation_rationale']}"
            )
        lines.append("")

    if synthesis["next_tests"]:
        lines.append("Next Tests:")
        for test in synthesis["next_tests"][:8]:
            lines.append(f"  - {test}")
        lines.append("")

    if synthesis.get("snapshot_id"):
        lines.append(f"Snapshot: {synthesis['snapshot_id']}")
        lines.append("")
    return "\n".join(lines)


def open_db(path: str, *, seed_claims: bool = True) -> TruthMapSQLiteDB:
    return build_truth_map_db(path, seed_claims=seed_claims, argument_schema=True)


def generate_report(
    question_id: str,
    *,
    db_path: str = ":memory:",
    bootstrap: bool = True,
    persist: bool = True,
) -> str:
    db = open_db(db_path)
    if bootstrap and not graph_has_candidates(db, question_id):
        bootstrap_question_graph(db, question_id)
    synthesis = synthesize_state_of_play(db, question_id, persist=persist)
    return format_report(synthesis)


def list_question_ids() -> list[str]:
    base = ROOT / "content" / "source-metaphysics"
    ids = []
    for path in sorted(base.glob("*.argument.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        question_id = data.get("question_id")
        if question_id:
            ids.append(str(question_id))
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a graph-derived state-of-play report")
    parser.add_argument("--question-id", help="Question to report on")
    parser.add_argument("--db", default=":memory:", help="SQLite DB path")
    parser.add_argument("--list-questions", action="store_true", help="List dossier-backed questions")
    parser.add_argument("--no-bootstrap", action="store_true", help="Do not ingest local dossier/map files into an empty DB")
    parser.add_argument("--no-persist", action="store_true", help="Do not write generated state_of_play_snapshot")
    parser.add_argument("--json", action="store_true", help="Emit synthesis JSON")
    args = parser.parse_args()

    if args.list_questions:
        for question_id in list_question_ids():
            print(question_id)
        return

    if not args.question_id:
        parser.error("--question-id is required unless --list-questions is used")

    db = open_db(args.db)
    if not args.no_bootstrap and not graph_has_candidates(db, args.question_id):
        bootstrap_question_graph(db, args.question_id)
    synthesis = synthesize_state_of_play(db, args.question_id, persist=not args.no_persist)
    if args.json:
        print(json.dumps(synthesis, indent=2, sort_keys=True))
    else:
        print(format_report(synthesis))


if __name__ == "__main__":
    main()
