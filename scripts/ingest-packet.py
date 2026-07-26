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
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from truthengine_working import (
    PropagationEngine,
    TruthMapSQLiteDB,
    build_truth_map_db,
)


def load_packet(path: Path) -> dict:
    return json.loads(path.read_text())


def ingest_packet(
    db: TruthMapSQLiteDB,
    packet: dict,
    commit: bool = False,
) -> dict:
    """Ingest a packet's claims into the truth map and run propagation."""
    engine = PropagationEngine(db)

    # Record state before
    before = engine.run()

    # Insert claims
    claims_inserted = 0
    for claim in packet.get("claims", []):
        db.add_claim_dict(claim)
        claims_inserted += 1

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
        "claims_inserted": claims_inserted,
        "before": {
            "features": {k: round(v, 6) for k, v in before["features"].items()},
            "branches": {k: round(v, 6) for k, v in before["branches"].items()},
        },
        "after": {
            "features": {k: round(v, 6) for k, v in after["features"].items()},
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
    args = parser.parse_args()

    packet = load_packet(Path(args.packet))
    print(f"Packet: {packet['packet_id']}")
    print(f"Source: {packet['source']['title']}")
    print(f"Claims: {len(packet.get('claims', []))}")

    db = build_truth_map_db(args.db)
    delta = ingest_packet(db, packet, commit=args.commit)

    print(f"\nIngested {delta['claims_inserted']} claims")
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
