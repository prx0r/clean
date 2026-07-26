#!/usr/bin/env python3
"""
provenance-report.py — belief provenance / blame reports.

Examples:
    python scripts/provenance-report.py --source-id arxiv:1312.2007
    python scripts/provenance-report.py --target-id D4
    python scripts/provenance-report.py --target-id D4 --dimension empirical
    python scripts/provenance-report.py --packet content/information-packets/test-amplituhedron.json --source-id arxiv:1312.2007
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from truthengine_working import PropagationEngine, build_truth_map_db


def load_packet(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report per-claim belief provenance from the truth map"
    )
    parser.add_argument("--db", default=":memory:", help="SQLite DB path")
    parser.add_argument("--packet", help="Optional packet JSON to ingest before reporting")
    parser.add_argument("--source-id", help="Filter to one source, e.g. arxiv:1312.2007")
    parser.add_argument("--claim-id", help="Filter to one claim")
    parser.add_argument("--target-id", help="Filter/rank by one target, e.g. D4 or F8")
    parser.add_argument(
        "--dimension",
        choices=("phenomenological", "empirical", "contemplative"),
        help="Filter to one evidence dimension",
    )
    parser.add_argument(
        "--no-seed-claims",
        action="store_true",
        help="Start without built-in seed claims",
    )
    args = parser.parse_args()

    db = build_truth_map_db(args.db, seed_claims=not args.no_seed_claims)
    if args.packet:
        packet = load_packet(Path(args.packet))
        for claim in packet.get("claims", []):
            db.add_claim_dict(claim)

    engine = PropagationEngine(db)
    if args.target_id and not args.source_id and not args.claim_id:
        records = engine.blame(args.target_id)
    else:
        records = engine.contribution_trace(
            source_id=args.source_id,
            claim_id=args.claim_id,
        )
        if args.target_id:
            records = [row for row in records if row["target_id"] == args.target_id]
    if args.dimension:
        records = [
            row for row in records if row["evidence_dimension"] == args.dimension
        ]

    print(
        json.dumps(
            {
                "query": {
                    "source_id": args.source_id,
                    "claim_id": args.claim_id,
                    "target_id": args.target_id,
                    "dimension": args.dimension,
                },
                "records": records,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
