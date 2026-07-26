import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from truthengine_working import build_truth_map_db


ROOT = Path(__file__).resolve().parent
INGEST_PATH = ROOT / "scripts" / "ingest-dossier.py"

spec = importlib.util.spec_from_file_location("ingest_dossier_module_for_tests", INGEST_PATH)
ingest_dossier = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ingest_dossier
assert spec.loader is not None
spec.loader.exec_module(ingest_dossier)


def count_rows(db, table):
    row = db.conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])


class IngestDossierTests(unittest.TestCase):
    def test_reflexivity_dossier_ingests_candidates_cruxes_and_snapshot(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        result = ingest_dossier.ingest_dossier(
            db,
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.argument.json",
        )

        self.assertEqual(result["candidates"], 4)
        self.assertEqual(result["cruxes"], 4)
        self.assertEqual(result["snapshots"], 1)
        self.assertEqual(
            count_rows(
                db,
                "argument_nodes WHERE node_type = 'candidate_explanation'",
            ),
            4,
        )
        self.assertEqual(
            count_rows(db, "argument_nodes WHERE node_type = 'crux'"),
            4,
        )
        self.assertGreaterEqual(count_rows(db, "tarka_falsifiers"), 5)

    def test_nanavira_map_ingests_correspondence_and_directional_critiques(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        ingest_dossier.ingest_dossier(
            db,
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.argument.json",
        )
        result = ingest_dossier.ingest_source_map(
            db,
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.nanavira-map.json",
        )

        self.assertEqual(result["claim_mappings"], 7)
        self.assertEqual(count_rows(db, "directional_critique_pairs"), 3)
        self.assertEqual(count_rows(db, "structural_correspondences"), 1)

        correspondence = db.conn.execute(
            """
            SELECT status, important_difference
            FROM structural_correspondences
            WHERE correspondence_id = 'corr:nanavira-difference-dharmakirti-apoha'
            """
        ).fetchone()
        self.assertEqual(correspondence["status"], "OVERLAPS")
        self.assertIn("Treating them as identical would overclaim", correspondence["important_difference"])

        undercut = db.conn.execute(
            """
            SELECT edge_type, polarity
            FROM argument_edges
            WHERE edge_id = 'edge:nanavira-self-similarity-supports-local-reflexivity'
            """
        ).fetchone()
        self.assertEqual(undercut["edge_type"], "attacks")
        self.assertEqual(undercut["polarity"], -1)

    def test_generic_source_map_ingests_declared_correspondences_and_critiques(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        source_map = {
            "schema_version": 1,
            "artifact_type": "argument_fabric_source_map",
            "question_id": "q:test-generic-map",
            "source_packet_id": "packet:test",
            "nnexpr_mappings": [],
            "argument_edges": [],
            "structural_correspondences": [
                {
                    "correspondence_id": "corr:test-overlap",
                    "left_term": "nn:left",
                    "left_scope": "scope:left",
                    "right_term": "nn:right",
                    "right_scope": "scope:right",
                    "shared_structure": "shared test structure",
                    "important_difference": "not the same ontology",
                    "confidence_language": "declared test overlap",
                    "status": "OVERLAPS",
                    "source_ids": ["packet:test"],
                    "bridge_probe_id": "bridge:test",
                    "negative_control_status": "pending_negative_controls",
                }
            ],
            "directional_critique_pairs": [
                {
                    "pair_id": "critique:test",
                    "critic_lens": "scope:left",
                    "target_lens": "scope:right",
                    "reveals_about_target": "target inherits a test gap",
                    "pressure_type": "test_gap",
                    "target_response_required": "answer the generic test gap",
                    "status": "open",
                    "supporting_claim_ids": ["cl:test"],
                    "crux_ids": ["crux:test"],
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "generic-map.json"
            path.write_text(json.dumps(source_map), encoding="utf-8")
            result = ingest_dossier.ingest_source_map(db, path)

        self.assertEqual(result["correspondences"], 1)
        self.assertEqual(result["critique_pairs"], 1)
        self.assertEqual(count_rows(db, "argument_nodes WHERE node_type = 'bridge'"), 1)

        correspondence = db.conn.execute(
            """
            SELECT left_term, status, source_ids
            FROM structural_correspondences
            WHERE correspondence_id = 'corr:test-overlap'
            """
        ).fetchone()
        self.assertEqual(correspondence["left_term"], "nn:left")
        self.assertEqual(correspondence["status"], "OVERLAPS")
        self.assertEqual(json.loads(correspondence["source_ids"]), ["packet:test"])

        bridge = db.conn.execute(
            """
            SELECT node_id, status
            FROM argument_nodes
            WHERE node_id = 'bridge:test'
            """
        ).fetchone()
        self.assertIsNotNone(bridge)
        self.assertEqual(bridge["status"], "OVERLAPS")

        critique = db.conn.execute(
            """
            SELECT critic_lens, target_lens, supporting_claim_ids
            FROM directional_critique_pairs
            WHERE pair_id = 'critique:test'
            """
        ).fetchone()
        self.assertEqual(critique["critic_lens"], "scope:left")
        self.assertEqual(critique["target_lens"], "scope:right")
        self.assertEqual(json.loads(critique["supporting_claim_ids"]), ["cl:test"])


if __name__ == "__main__":
    unittest.main()
