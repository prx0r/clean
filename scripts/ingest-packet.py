#!/usr/bin/env python3
"""
ingest-packet.py — Information Packet → Truth Map Update

Takes a packet JSON, inserts claims into the truth map database,
runs propagation, records before/after delta.

Usage:
    python scripts/ingest-packet.py --packet content/information-packets/ip-arkani-hamed.json
    python scripts/ingest-packet.py --packet ip.json --db truth_map.db
    python scripts/ingest-packet.py --packet ip.json --commit
"""

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
GATE_PATH = ROOT / "scripts" / "nyaya-truthmap-gate.py"

from truthengine_working import (
    EVIDENCE_DIMENSIONS,
    PropagationEngine,
    TruthMapSQLiteDB,
    build_truth_map_db,
)


def load_gate_module():
    spec = importlib.util.spec_from_file_location("nyaya_truthmap_gate", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


nyaya_truthmap_gate = load_gate_module()


def load_packet(path: Path) -> dict:
    return json.loads(path.read_text())


def runtime_dimension(dimension: str) -> str:
    if dimension in EVIDENCE_DIMENSIONS:
        return dimension
    return {
        "formal": "phenomenological",
        "textual": "phenomenological",
        "analogical": "phenomenological",
    }.get(dimension, "phenomenological")


def runtime_targets(claim: dict) -> tuple[list[str], list[str]]:
    features: list[str] = []
    discriminators: list[str] = []
    for target in claim.get("targets", []) or []:
        target_id = target.get("target_id")
        target_type = target.get("target_type")
        if target_type == "feature" and target_id:
            features.append(str(target_id))
        elif target_type == "discriminator" and target_id:
            discriminators.append(str(target_id))
    features.extend(str(x) for x in claim.get("features", []) or [])
    features.extend(str(x) for x in claim.get("target_feature_ids", []) or [])
    discriminators.extend(str(x) for x in claim.get("discriminators", []) or [])
    discriminators.extend(str(x) for x in claim.get("target_discriminator_ids", []) or [])
    return sorted(set(features)), sorted(set(discriminators))


def argument_targets(claim: dict) -> list[dict]:
    allowed = {"candidate_explanation", "crux", "bridge"}
    return [
        target
        for target in claim.get("targets", []) or []
        if target.get("target_id") and target.get("target_type") in allowed
    ]


def safe_id(value: str) -> str:
    return (
        str(value)
        .replace(":", "-")
        .replace("/", "-")
        .replace(" ", "-")
        .lower()
    )


def packet_source_id(packet: dict) -> str:
    source = packet.get("source") or {}
    return (
        source.get("so_id")
        or source.get("source_id")
        or (f"arxiv:{source['arxiv_id']}" if source.get("arxiv_id") else None)
        or packet.get("packet_id", "packet:unknown")
    )


def packet_source_type(packet: dict) -> str:
    source = packet.get("source") or {}
    return str(source.get("type") or "source_text")


def packet_title(packet: dict) -> str:
    source = packet.get("source") or {}
    return str(source.get("title") or packet.get("packet_id", "Untitled packet"))


def source_span_id(claim: dict) -> Optional[str]:
    span = claim.get("source_span")
    if not isinstance(span, dict):
        return None
    if span.get("span_id"):
        return str(span["span_id"])
    return f"span:{safe_id(claim['claim_id'])}"


def store_source_span(db: TruthMapSQLiteDB, claim: dict, packet: dict) -> Optional[str]:
    span = claim.get("source_span")
    if not isinstance(span, dict):
        return None
    span_id = source_span_id(claim)
    locator = " ".join(
        str(part)
        for part in (span.get("file"), span.get("locator"))
        if part
    ) or None
    provenance = {
        "packet_id": packet.get("packet_id"),
        "source": packet.get("source", {}),
        "source_span": span,
    }
    db.conn.execute(
        """
        INSERT OR REPLACE INTO source_spans
        (span_id, source_type, source_id, locator, quote, normalized_text,
         language, tradition_scope, provenance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            span_id,
            claim.get("source_type", packet_source_type(packet)),
            claim.get("source_id", packet_source_id(packet)),
            locator,
            span.get("quote") or claim.get("claim_text", claim["claim_id"]),
            claim.get("claim_text"),
            span.get("language"),
            claim.get("tradition_scope") or claim.get("tradition") or claim.get("paradigm"),
            json.dumps(provenance, sort_keys=True),
        ),
    )
    return span_id


def store_claim_metadata(
    db: TruthMapSQLiteDB,
    claim: dict,
    packet: dict,
    gate_result,
) -> None:
    falsifier = claim.get("falsifier")
    db.conn.execute(
        """
        INSERT OR IGNORE INTO claims
        (claim_id, schema_version, source_type, source_id, evidence_role,
         evidence_dimension, source_cluster, method_family, target_question_id,
         log_bayes_factor, w_rel, w_map, w_aux, paradigm, claim_text, falsifier,
         is_retracted, supersedes, superseded_by, extracted_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim["claim_id"],
            int(claim.get("schema_version", packet.get("schema_version", 1))),
            claim.get("source_type", packet_source_type(packet)),
            claim.get("source_id", packet_source_id(packet)),
            claim.get("evidence_role", "primary"),
            gate_result.evidence_dimension,
            claim.get("source_cluster"),
            claim.get("method_family"),
            claim.get("question_id") or packet.get("target_question_id"),
            float(claim.get("log_bayes_factor", 0.0) or 0.0),
            float(claim.get("w_rel", 1.0) or 0.0),
            float(claim.get("w_map", 1.0) or 0.0),
            float(claim.get("w_aux", 1.0) or 0.0),
            claim.get("paradigm") or gate_result.tradition_scope,
            claim.get("claim_text", claim["claim_id"]),
            json.dumps(falsifier) if falsifier is not None else None,
            int(claim.get("is_retracted", False)),
            claim.get("supersedes"),
            claim.get("superseded_by"),
            claim.get("extracted_by", packet.get("extracted_by", "ingest-packet")),
        ),
    )


def store_argument_node(
    db: TruthMapSQLiteDB,
    claim: dict,
    packet: dict,
    gate_result,
    span_id: Optional[str],
) -> str:
    node_id = f"arg:{claim['claim_id']}"
    payload = {
        "packet_id": packet.get("packet_id"),
        "targets": claim.get("targets", []),
        "source_span": claim.get("source_span"),
        "nn_expr": claim.get("nn_expr"),
        "nnexpr_probe": asdict(gate_result.nnexpr_probe),
        "gate_outcome": gate_result.outcome,
        "adjusted_lbf_cap": gate_result.adjusted_lbf_cap,
    }
    db.conn.execute(
        """
        INSERT OR REPLACE INTO argument_nodes
        (node_id, node_type, title, statement, question_id, claim_id, span_id,
         tradition_scope, evidence_dimension, pramana, status, payload)
        VALUES (?, 'claim', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            node_id,
            claim["claim_id"],
            claim.get("claim_text", claim["claim_id"]),
            claim.get("question_id") or packet.get("target_question_id"),
            claim["claim_id"],
            span_id,
            gate_result.tradition_scope,
            gate_result.evidence_dimension,
            gate_result.pramana,
            gate_result.outcome,
            json.dumps(payload, sort_keys=True),
        ),
    )
    return node_id


def store_argument_targets(
    db: TruthMapSQLiteDB,
    claim_node_id: str,
    claim: dict,
    gate_result,
) -> None:
    for target in argument_targets(claim):
        target_id = str(target["target_id"])
        target_type = str(target["target_type"])
        db.conn.execute(
            """
            INSERT OR IGNORE INTO argument_nodes
            (node_id, node_type, title, statement, tradition_scope, status, payload)
            VALUES (?, ?, ?, ?, ?, 'stub', ?)
            """,
            (
                target_id,
                target_type,
                target.get("label") or target_id,
                target.get("statement") or target_id,
                gate_result.tradition_scope,
                json.dumps({"created_from": claim["claim_id"]}, sort_keys=True),
            ),
        )
        edge_id = f"edge:{safe_id(claim_node_id)}:{safe_id(target_id)}:targets"
        db.conn.execute(
            """
            INSERT OR REPLACE INTO argument_edges
            (edge_id, source_node_id, target_node_id, edge_type, strength,
             polarity, relation_rationale, verification_status, payload)
            VALUES (?, ?, ?, 'targets', 1.0, 1, ?, 'agent_suggested', ?)
            """,
            (
                edge_id,
                claim_node_id,
                target_id,
                "Claim target declared in information packet.",
                json.dumps({"target": target}, sort_keys=True),
            ),
        )


def store_gate_result(db: TruthMapSQLiteDB, claim: dict, gate_result) -> None:
    result_json = nyaya_truthmap_gate.result_to_json(gate_result)
    gate_id = f"gate:{safe_id(claim['claim_id'])}:{safe_id(gate_result.gate_version)}"
    db.conn.execute(
        """
        INSERT OR REPLACE INTO claim_gate_results
        (gate_id, claim_id, gate_version, outcome, can_update_posterior,
         adjusted_lbf_cap, evidence_dimension, pramana, tradition_scope, hetu,
         sadhya, vyapti_statement, vyapti_confidence, falsifier_status,
         failures, reviewer, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            gate_id,
            claim["claim_id"],
            gate_result.gate_version,
            gate_result.outcome,
            int(gate_result.can_update_posterior),
            gate_result.adjusted_lbf_cap,
            gate_result.evidence_dimension,
            gate_result.pramana,
            gate_result.tradition_scope,
            gate_result.hetu,
            gate_result.sadhya,
            gate_result.vyapti_statement,
            gate_result.vyapti_confidence,
            gate_result.falsifier_status,
            json.dumps(result_json["failures"], sort_keys=True),
            "nyaya-truthmap-gate.py",
            gate_result.reasoning,
        ),
    )

    for failure in gate_result.failures:
        check_id = f"hetv:{safe_id(claim['claim_id'])}:{safe_id(failure.fallacy_type)}"
        db.conn.execute(
            """
            INSERT OR REPLACE INTO hetvabhasa_checks
            (check_id, claim_id, fallacy_type, present, severity, rationale)
            VALUES (?, ?, ?, 1, ?, ?)
            """,
            (
                check_id,
                claim["claim_id"],
                failure.fallacy_type,
                failure.severity,
                failure.rationale,
            ),
        )

    for index, falsifier in enumerate(gate_result.tarka_falsifiers, start=1):
        falsifier_id = f"tf:{safe_id(claim['claim_id'])}:{index}"
        db.conn.execute(
            """
            INSERT OR REPLACE INTO tarka_falsifiers
            (falsifier_id, claim_id, falsifier_type, condition, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                falsifier_id,
                claim["claim_id"],
                falsifier.falsifier_type,
                falsifier.condition,
                falsifier.status,
            ),
        )


def store_formal_probe(db: TruthMapSQLiteDB, claim: dict, gate_result, claim_node_id: str) -> None:
    if not gate_result.formal_probe.attempted:
        return
    link_id = f"formal:{safe_id(claim['claim_id'])}:{safe_id(gate_result.gate_version)}"
    db.conn.execute(
        """
        INSERT OR REPLACE INTO formal_status_links
        (link_id, argument_node_id, sanskritree_node_id, formal_status, proof_trace)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            link_id,
            claim_node_id,
            (
                str(gate_result.formal_probe.node_id)
                if gate_result.formal_probe.node_id is not None
                else None
            ),
            gate_result.formal_probe.status,
            json.dumps(asdict(gate_result.formal_probe), sort_keys=True),
        ),
    )


def prepare_runtime_claim(claim: dict, gate_result) -> dict:
    runtime_claim = dict(claim)
    runtime_claim["evidence_dimension"] = runtime_dimension(gate_result.evidence_dimension)
    if gate_result.adjusted_lbf_cap is not None:
        lbf = float(runtime_claim.get("log_bayes_factor", 0.0) or 0.0)
        cap = abs(float(gate_result.adjusted_lbf_cap))
        if abs(lbf) > cap:
            runtime_claim["log_bayes_factor"] = math.copysign(cap, lbf)
    return runtime_claim


def ingest_packet(
    db: TruthMapSQLiteDB,
    packet: dict,
    commit: bool = False,
    gate: bool = True,
    formal_probe: bool = False,
) -> dict:
    """Ingest a packet's claims into the truth map and run propagation."""
    engine = PropagationEngine(db)

    # Record state before
    before = engine.run()

    claims_seen = 0
    runtime_claims_inserted = 0
    argument_claims_recorded = 0
    gate_results_stored = 0
    claims_blocked = 0
    gate_outcomes: dict[str, int] = {}

    claims = packet.get("claims", [])
    if not gate:
        for claim in claims:
            claims_seen += 1
            db.add_claim_dict(claim)
            runtime_claims_inserted += 1
        gate_outcomes["bypassed"] = claims_seen
    else:
        for claim in claims:
            claims_seen += 1
            gate_result = nyaya_truthmap_gate.validate(
                claim,
                claims,
                formal_probe=formal_probe,
            )
            gate_outcomes[gate_result.outcome] = gate_outcomes.get(gate_result.outcome, 0) + 1

            store_claim_metadata(db, claim, packet, gate_result)
            span_id = store_source_span(db, claim, packet)
            claim_node_id = store_argument_node(db, claim, packet, gate_result, span_id)
            store_argument_targets(db, claim_node_id, claim, gate_result)
            store_gate_result(db, claim, gate_result)
            store_formal_probe(db, claim, gate_result, claim_node_id)
            argument_claims_recorded += 1
            gate_results_stored += 1

            features, discriminators = runtime_targets(claim)
            if gate_result.can_update_posterior and (features or discriminators):
                db.add_claim_dict(prepare_runtime_claim(claim, gate_result))
                runtime_claims_inserted += 1
            elif not gate_result.can_update_posterior:
                claims_blocked += 1

    db.conn.commit()

    # Run propagation
    after = engine.run()

    # Compute deltas
    feature_deltas = {}
    for fid in before["features"]:
        feature_deltas[fid] = round(after["features"][fid] - before["features"][fid], 6)

    branch_deltas = {}
    for bid in before["branches"]:
        branch_deltas[bid] = round(after["branches"][bid] - before["branches"][bid], 6)

    delta = {
        "packet_id": packet["packet_id"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "claims_seen": claims_seen,
        "claims_inserted": runtime_claims_inserted,
        "runtime_claims_inserted": runtime_claims_inserted,
        "argument_claims_recorded": argument_claims_recorded,
        "gate_results_stored": gate_results_stored,
        "claims_blocked": claims_blocked,
        "gate_outcomes": gate_outcomes,
        "before": {
            "features": {k: round(v, 6) for k, v in before["features"].items()},
            "discriminators": {k: round(v, 6) for k, v in before["discriminators"].items()},
            "branches": {k: round(v, 6) for k, v in before["branches"].items()},
        },
        "after": {
            "features": {k: round(v, 6) for k, v in after["features"].items()},
            "discriminators": {k: round(v, 6) for k, v in after["discriminators"].items()},
            "branches": {k: round(v, 6) for k, v in after["branches"].items()},
        },
        "feature_deltas": feature_deltas,
        "branch_deltas": branch_deltas,
        "claims_processed": after["claims_processed"],
    }

    # Save question states
    features = {f.id: f for f in db.get_all_features()}
    db.save_question_states(features)

    if commit:
        # In production: write delta to D1 audit log
        pass

    return delta


def main():
    parser = argparse.ArgumentParser(description="Ingest an information packet into the truth map")
    parser.add_argument("--packet", required=True, type=str, help="Path to packet JSON")
    parser.add_argument("--db", type=str, default=":memory:", help="SQLite DB path")
    parser.add_argument("--commit", action="store_true", help="Actually persist changes")
    parser.add_argument("--save-delta", type=str, help="Save delta report to path")
    parser.add_argument("--no-gate", action="store_true", help="Bypass Nyaya gate for legacy debugging")
    parser.add_argument("--formal-probe", action="store_true", help="Run optional Sanskritree formal probe during gating")
    parser.add_argument("--no-seed-claims", action="store_true", help="Start without built-in seed claims")
    args = parser.parse_args()

    packet = load_packet(Path(args.packet))
    print(f"Packet: {packet['packet_id']}")
    print(f"Source: {packet_title(packet)}")
    print(f"Claims: {len(packet.get('claims', []))}")

    db = build_truth_map_db(
        args.db,
        seed_claims=not args.no_seed_claims,
        argument_schema=not args.no_gate,
    )
    delta = ingest_packet(
        db,
        packet,
        commit=args.commit,
        gate=not args.no_gate,
        formal_probe=args.formal_probe,
    )

    print(f"\nSeen {delta['claims_seen']} claims")
    print(f"Runtime claims inserted: {delta['runtime_claims_inserted']}")
    print(f"Argument claims recorded: {delta['argument_claims_recorded']}")
    print(f"Gate results stored: {delta['gate_results_stored']}")
    print(f"Gate outcomes: {json.dumps(delta['gate_outcomes'], sort_keys=True)}")
    print(f"Claims processed by engine: {delta['claims_processed']}")
    print(f"\nFeature deltas:")
    for fid, d in delta["feature_deltas"].items():
        arrow = "↑" if d > 0 else "↓" if d < 0 else "—"
        print(f"  {fid}: {delta['before']['features'][fid]:.4f} → {delta['after']['features'][fid]:.4f}  {arrow} {d:+.6f}")
    print(f"\nBranch deltas:")
    for bid, d in delta["branch_deltas"].items():
        arrow = "↑" if d > 0 else "↓" if d < 0 else "—"
        print(f"  {bid}: {delta['before']['branches'][bid]:.6f} → {delta['after']['branches'][bid]:.6f}  {arrow} {d:+.6f}")

    if args.save_delta:
        Path(args.save_delta).write_text(json.dumps(delta, indent=2))
        print(f"\nDelta saved to {args.save_delta}")


if __name__ == "__main__":
    main()
