#!/usr/bin/env python3
"""Ingest argument dossiers and source maps into the argument fabric.

This script is intentionally separate from `ingest-packet.py`.

- Packets contain atomic claims and go through the Nyaya gate.
- Dossiers contain question scaffolding: candidates, cruxes, falsifiers,
  correspondence notes, and initial state-of-play seeds.

The output is graph-native rows that `state-of-play.py` can evaluate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from truthengine_working import TruthMapSQLiteDB, build_truth_map_db


ALLOWED_EDGE_TYPES = {
    "supports",
    "attacks",
    "rephrases",
    "instantiates",
    "presupposes",
    "contradicts",
    "subsumes",
    "bridges",
    "decomposes_to",
    "targets",
    "falsified_by",
    "outside_formal",
}

ALLOWED_FALSIFIER_TYPES = {
    "prasanga",
    "arthapatti",
    "empirical",
    "formal",
    "philological",
    "phenomenological",
    "semantic",
    "operational",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_id(value: str) -> str:
    return (
        str(value)
        .replace(":", "-")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
        .lower()
    )


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def normalize_falsifier_type(value: str | None) -> str:
    if not value:
        return "operational"
    normalized = str(value).lower()
    if normalized in ALLOWED_FALSIFIER_TYPES:
        return normalized
    return {
        "anumana": "prasanga",
        "anumāna": "prasanga",
        "pratyaksa": "empirical",
        "pratyakṣa": "empirical",
        "sabda": "philological",
        "śabda": "philological",
        "textual": "philological",
        "upamana": "operational",
        "upamāna": "operational",
    }.get(normalized, "operational")


def node_type_for_id(node_id: str) -> str:
    if node_id.startswith("cand:"):
        return "candidate_explanation"
    if node_id.startswith("crux:"):
        return "crux"
    if node_id.startswith("bridge:"):
        return "bridge"
    if node_id.startswith("cl:"):
        return "claim"
    if node_id.startswith("tf:"):
        return "falsifier"
    return "argument"


def ensure_stub_node(
    db: TruthMapSQLiteDB,
    node_id: str,
    *,
    question_id: str | None,
    statement: str | None = None,
    title: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    node_type = node_type_for_id(node_id)
    db.conn.execute(
        """
        INSERT OR IGNORE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, status, payload)
        VALUES (?, ?, ?, ?, ?, 'stub', ?)
        """,
        (
            node_id,
            node_type,
            title or node_id,
            statement or node_id,
            question_id,
            json_text(payload or {"created_by": "ingest-dossier"}),
        ),
    )


def insert_edge(
    db: TruthMapSQLiteDB,
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    edge_type: str,
    *,
    strength: float,
    polarity: int,
    rationale: str,
    payload: dict[str, Any] | None = None,
    verification_status: str = "agent_suggested",
) -> None:
    if edge_type not in ALLOWED_EDGE_TYPES:
        raise ValueError(f"unsupported edge_type: {edge_type}")
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_edges
        (edge_id, source_node_id, target_node_id, edge_type, strength,
         polarity, relation_rationale, verification_status, payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            edge_id,
            source_node_id,
            target_node_id,
            edge_type,
            max(0.0, min(1.0, float(strength))),
            polarity,
            rationale,
            verification_status,
            json_text(payload or {}),
        ),
    )


def insert_candidate(db: TruthMapSQLiteDB, question_id: str, candidate: dict[str, Any]) -> None:
    candidate_id = candidate["candidate_id"]
    payload = {
        "hard_to_vary_core": candidate.get("hard_to_vary_core", []),
        "current_problems": candidate.get("current_problems", []),
        "falsifiers": candidate.get("falsifiers", []),
        "best_case": candidate.get("best_case"),
    }
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, tradition_scope,
         evidence_dimension, pramana, status, payload)
        VALUES (?, 'candidate_explanation', ?, ?, ?, ?, 'phenomenological',
                'anumana', ?, ?)
        """,
        (
            candidate_id,
            candidate.get("name", candidate_id),
            candidate.get("best_case", candidate.get("name", candidate_id)),
            question_id,
            candidate.get("tradition_scope"),
            candidate.get("initial_status", "live"),
            json_text(payload),
        ),
    )

    for index, falsifier in enumerate(candidate.get("falsifiers", []), start=1):
        if isinstance(falsifier, str):
            condition = falsifier
            ftype = "operational"
            status = "untested"
        else:
            condition = str(falsifier.get("condition", ""))
            ftype = normalize_falsifier_type(falsifier.get("type"))
            status = str(falsifier.get("status", "untested"))
        if not condition:
            continue
        falsifier_id = f"tf:{safe_id(candidate_id)}:{index}"
        db.conn.execute(
            """
            INSERT OR REPLACE INTO tarka_falsifiers
            (falsifier_id, candidate_id, falsifier_type, condition, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (falsifier_id, candidate_id, ftype, condition, status),
        )
        db.conn.execute(
            """
            INSERT OR REPLACE INTO argument_nodes
            (node_id, node_type, title, statement, question_id, status, payload)
            VALUES (?, 'falsifier', ?, ?, ?, ?, ?)
            """,
            (
                falsifier_id,
                f"Falsifier for {candidate.get('name', candidate_id)}",
                condition,
                question_id,
                status,
                json_text(
                    {
                        "candidate_id": candidate_id,
                        "falsifier_type": ftype,
                        "status": status,
                    }
                ),
            ),
        )
        insert_edge(
            db,
            f"edge:{safe_id(falsifier_id)}:{safe_id(candidate_id)}:falsified-by",
            falsifier_id,
            candidate_id,
            "falsified_by",
            strength=1.0,
            polarity=-1,
            rationale="Candidate-declared falsifier.",
        )


def pressure_edge_type(text: str) -> tuple[str, int, float]:
    lowered = text.lower()
    if any(word in lowered for word in ("attack", "pressure", "weakest", "must answer", "problem")):
        return "attacks", -1, 0.35
    if any(word in lowered for word in ("support", "likely", "denies", "core distinction")):
        return "supports", 1, 0.25
    return "targets", 0, 0.15


def insert_crux(db: TruthMapSQLiteDB, question_id: str, crux: dict[str, Any]) -> None:
    crux_id = crux["crux_id"]
    payload = {"candidate_pressure": crux.get("candidate_pressure", {})}
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, evidence_dimension,
         pramana, status, payload)
        VALUES (?, 'crux', ?, ?, ?, 'phenomenological', 'anumana', 'open', ?)
        """,
        (
            crux_id,
            crux.get("question", crux_id),
            crux.get("question", crux_id),
            question_id,
            json_text(payload),
        ),
    )
    for candidate_id, pressure in crux.get("candidate_pressure", {}).items():
        ensure_stub_node(db, candidate_id, question_id=question_id)
        edge_type, polarity, strength = pressure_edge_type(str(pressure))
        insert_edge(
            db,
            f"edge:{safe_id(crux_id)}:{safe_id(candidate_id)}:pressure",
            crux_id,
            candidate_id,
            edge_type,
            strength=strength,
            polarity=polarity,
            rationale=str(pressure),
            payload={"relation": "candidate_pressure"},
        )


def insert_initial_snapshot(
    db: TruthMapSQLiteDB,
    question_id: str,
    state: dict[str, Any],
    source_path: Path,
) -> None:
    snapshot_id = f"sop:{safe_id(question_id)}:manual-seed"
    current_best = state.get("current_best_answer") or state.get("summary") or "No state of play available."
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, status, payload)
        VALUES (?, 'state_of_play', 'Manual seed state of play', ?, ?, 'manual_seed', ?)
        """,
        (snapshot_id, current_best, question_id, json_text(state)),
    )
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
            current_best,
            state.get("confidence_language", "manual_seed"),
            json_text(state.get("solved_at_levels", [])),
            json_text([]),
            json_text([]),
            json_text([]),
            json_text(state.get("open_cruxes", [])),
            json_text(state.get("next_tests", [])),
            json_text(state.get("implications", [])),
            json_text({"source": str(source_path), "source_type": "manual_seed"}),
        ),
    )


def ingest_dossier(db: TruthMapSQLiteDB, dossier_path: Path) -> dict[str, int]:
    dossier = load_json(dossier_path)
    if dossier.get("artifact_type") != "argument_fabric_dossier":
        raise ValueError(f"{dossier_path} is not an argument_fabric_dossier")
    question_id = dossier["question_id"]
    counts = {"candidates": 0, "cruxes": 0, "falsifiers": 0, "snapshots": 0}

    for candidate in dossier.get("candidate_explanations", []):
        before = db.conn.total_changes
        insert_candidate(db, question_id, candidate)
        counts["candidates"] += 1
        counts["falsifiers"] += max(0, db.conn.total_changes - before - 1)

    for crux in dossier.get("cruxes", []):
        insert_crux(db, question_id, crux)
        counts["cruxes"] += 1

    state = dossier.get("initial_state_of_play")
    if state:
        insert_initial_snapshot(db, question_id, state, dossier_path)
        counts["snapshots"] += 1

    db.conn.commit()
    return counts


def map_role_to_edge_type(role: str | None, edge_type: str | None = None) -> tuple[str, int]:
    if edge_type:
        normalized = edge_type.lower()
        if normalized == "undercuts":
            return "attacks", -1
        if normalized == "overlaps":
            return "bridges", 0
        if normalized in ALLOWED_EDGE_TYPES:
            return normalized, -1 if normalized in {"attacks", "contradicts", "falsified_by"} else 1
    role = (role or "").lower()
    if "bridge" in role:
        return "bridges", 0
    if "boundary" in role:
        return "outside_formal", 0
    if "risk" in role:
        return "supports", 1
    return "supports", 1


def gate_multiplier(outcome: str | None) -> float:
    return {
        "accepted": 1.0,
        "accepted_with_penalty": 0.55,
        "needs_review": 0.15,
        "hollow": 0.0,
        "outside_formal": 0.25,
        "refuted": 0.0,
    }.get(str(outcome), 0.3)


def insert_claim_mapping(db: TruthMapSQLiteDB, question_id: str, mapping: dict[str, Any]) -> None:
    claim_id = mapping["claim_id"]
    statement = (
        mapping.get("quoted_anchor")
        or mapping.get("nyaya_reading", {}).get("sadhya")
        or claim_id
    )
    payload = {
        "nn_expr": mapping.get("nn_expr"),
        "parse_status": mapping.get("parse_status"),
        "nyaya_reading": mapping.get("nyaya_reading"),
        "gate_outcome": mapping.get("gate_outcome"),
        "argument_role": mapping.get("argument_role"),
        "falsifier": mapping.get("falsifier"),
    }
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, claim_id,
         evidence_dimension, pramana, status, payload)
        VALUES (?, 'claim', ?, ?, ?, ?, 'phenomenological', 'anumana', ?, ?)
        """,
        (
            claim_id,
            claim_id,
            statement,
            question_id,
            claim_id,
            mapping.get("gate_outcome", "mapped"),
            json_text(payload),
        ),
    )

    for target_id in mapping.get("targets", []):
        ensure_stub_node(db, str(target_id), question_id=question_id)
        edge_type, polarity = map_role_to_edge_type(mapping.get("argument_role"))
        if mapping.get("argument_role") == "bridge_candidate":
            edge_type, polarity = "bridges", 0
        strength = 0.45 * gate_multiplier(mapping.get("gate_outcome"))
        insert_edge(
            db,
            f"edge:{safe_id(claim_id)}:{safe_id(target_id)}:{edge_type}",
            claim_id,
            str(target_id),
            edge_type,
            strength=strength,
            polarity=polarity,
            rationale=mapping.get("nyaya_reading", {}).get("vyapti", "Mapped source claim target."),
            payload={
                "source": "nnexpr_mapping",
                "gate_outcome": mapping.get("gate_outcome"),
                "parse_status": mapping.get("parse_status"),
                "argument_role": mapping.get("argument_role"),
            },
        )


def insert_map_edges(db: TruthMapSQLiteDB, question_id: str, edges: list[dict[str, Any]]) -> None:
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        ensure_stub_node(db, source, question_id=question_id)
        ensure_stub_node(db, target, question_id=question_id)
        edge_type, polarity = map_role_to_edge_type(None, edge.get("edge_type"))
        relation_status = "OVERLAPS" if str(edge.get("edge_type", "")).lower() == "overlaps" else None
        insert_edge(
            db,
            edge["edge_id"],
            source,
            target,
            edge_type,
            strength=float(edge.get("strength", 0.3)),
            polarity=polarity,
            rationale=edge.get("rationale", "Mapped argument edge."),
            payload={
                "original_edge_type": edge.get("edge_type"),
                "relation_status": relation_status,
            },
        )


def insert_structural_correspondence_rows(
    db: TruthMapSQLiteDB,
    question_id: str,
    source_map: dict[str, Any],
) -> None:
    default_sources = [
        value
        for value in (
            source_map.get("source_packet_id"),
            source_map.get("claim_packet"),
            source_map.get("source_metadata"),
        )
        if value
    ]
    for row in source_map.get("structural_correspondences", []) or []:
        bridge_probe_id = row.get("bridge_probe_id")
        if bridge_probe_id:
            db.conn.execute(
                """
                INSERT OR REPLACE INTO argument_nodes
                (node_id, node_type, title, statement, question_id,
                 evidence_dimension, pramana, status, payload)
                VALUES (?, 'bridge', ?, ?, ?, 'analogical', 'upamana', ?, ?)
                """,
                (
                    bridge_probe_id,
                    f"{row['left_term']} / {row['right_term']}",
                    row.get("shared_structure", row["correspondence_id"]),
                    question_id,
                    row.get("status", "needs_review"),
                    json_text(
                        {
                            "correspondence_id": row["correspondence_id"],
                            "important_difference": row.get("important_difference"),
                            "negative_control_status": row.get("negative_control_status"),
                            "source": "structural_correspondences",
                        }
                    ),
                ),
            )
        db.conn.execute(
            """
            INSERT OR REPLACE INTO structural_correspondences
            (correspondence_id, question_id, left_term, left_scope, right_term,
             right_scope, shared_structure, important_difference,
             confidence_language, status, source_ids, bridge_probe_id,
             negative_control_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["correspondence_id"],
                question_id,
                row["left_term"],
                row["left_scope"],
                row["right_term"],
                row["right_scope"],
                row["shared_structure"],
                row["important_difference"],
                row.get("confidence_language", "source-map declared"),
                row.get("status", "needs_review"),
                json_text(row.get("source_ids", default_sources)),
                bridge_probe_id,
                row.get("negative_control_status"),
            ),
        )


def insert_directional_critique_pair_rows(
    db: TruthMapSQLiteDB,
    question_id: str,
    source_map: dict[str, Any],
) -> None:
    for row in source_map.get("directional_critique_pairs", []) or []:
        db.conn.execute(
            """
            INSERT OR REPLACE INTO directional_critique_pairs
            (pair_id, question_id, critic_lens, target_lens, reveals_about_target,
             pressure_type, target_response_required, status,
             supporting_claim_ids, crux_ids)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["pair_id"],
                question_id,
                row["critic_lens"],
                row["target_lens"],
                row["reveals_about_target"],
                row["pressure_type"],
                row["target_response_required"],
                row.get("status", "open"),
                json_text(row.get("supporting_claim_ids", [])),
                json_text(row.get("crux_ids", [])),
            ),
        )


def insert_map_state_delta(db: TruthMapSQLiteDB, question_id: str, source_map: dict[str, Any], source_path: Path) -> None:
    delta = source_map.get("state_of_play_delta") or {}
    if not delta:
        return
    snapshot_id = f"sop:{safe_id(question_id)}:source-map-{safe_id(source_map.get('source_packet_id', 'map'))}"
    current_best = delta.get("current_best_answer", "Source map updated the state of play.")
    next_tests = source_map.get("next_work", [])
    db.conn.execute(
        """
        INSERT OR REPLACE INTO state_of_play_snapshots
        (snapshot_id, question_id, current_best_answer, confidence_language,
         solved_at_levels, live_candidates, weakened_candidates, defeated_candidates,
         open_cruxes, next_tests, implications, provenance)
        VALUES (?, ?, ?, 'source_map_delta', ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot_id,
            question_id,
            current_best,
            json_text([]),
            json_text([]),
            json_text([]),
            json_text([]),
            json_text(["crux:constructed-reflexivity-presupposes-manifestness", "crux:local-to-universal"]),
            json_text(next_tests),
            json_text([]),
            json_text({"source": str(source_path), "source_type": "source_map"}),
        ),
    )


def ingest_source_map(db: TruthMapSQLiteDB, map_path: Path) -> dict[str, int]:
    source_map = load_json(map_path)
    question_id = source_map["question_id"]
    counts = {"claim_mappings": 0, "edges": 0, "correspondences": 0, "critique_pairs": 0, "snapshots": 0}

    for mapping in source_map.get("nnexpr_mappings", []):
        insert_claim_mapping(db, question_id, mapping)
        counts["claim_mappings"] += 1

    before_edges = db.conn.execute("SELECT COUNT(*) AS count FROM argument_edges").fetchone()["count"]
    insert_map_edges(db, question_id, source_map.get("argument_edges", []))
    after_edges = db.conn.execute("SELECT COUNT(*) AS count FROM argument_edges").fetchone()["count"]
    counts["edges"] += int(after_edges) - int(before_edges)

    before_corr = db.conn.execute("SELECT COUNT(*) AS count FROM structural_correspondences").fetchone()["count"]
    insert_structural_correspondence_rows(db, question_id, source_map)
    after_corr = db.conn.execute("SELECT COUNT(*) AS count FROM structural_correspondences").fetchone()["count"]
    counts["correspondences"] += int(after_corr) - int(before_corr)

    before_pairs = db.conn.execute("SELECT COUNT(*) AS count FROM directional_critique_pairs").fetchone()["count"]
    insert_directional_critique_pair_rows(db, question_id, source_map)
    after_pairs = db.conn.execute("SELECT COUNT(*) AS count FROM directional_critique_pairs").fetchone()["count"]
    counts["critique_pairs"] += int(after_pairs) - int(before_pairs)

    insert_map_state_delta(db, question_id, source_map, map_path)
    counts["snapshots"] += 1 if source_map.get("state_of_play_delta") else 0

    db.conn.commit()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest an argument dossier/source map")
    parser.add_argument("--dossier", type=str, help="Path to *.argument.json")
    parser.add_argument("--map", type=str, help="Path to *.nanavira-map.json or source map")
    parser.add_argument("--db", default=":memory:", help="SQLite DB path")
    parser.add_argument("--no-seed-claims", action="store_true", help="Start without seed runtime claims")
    args = parser.parse_args()

    if not args.dossier and not args.map:
        parser.error("provide --dossier and/or --map")

    db = build_truth_map_db(
        args.db,
        seed_claims=not args.no_seed_claims,
        argument_schema=True,
    )

    result: dict[str, Any] = {}
    if args.dossier:
        result["dossier"] = ingest_dossier(db, Path(args.dossier))
    if args.map:
        result["source_map"] = ingest_source_map(db, Path(args.map))

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
