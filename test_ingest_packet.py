import importlib.util
import json
import sys
import unittest
from pathlib import Path

from truthengine_working import PropagationEngine, build_truth_map_db


ROOT = Path(__file__).resolve().parent
INGEST_PATH = ROOT / "scripts" / "ingest-packet.py"

spec = importlib.util.spec_from_file_location("ingest_packet_module", INGEST_PATH)
ingest_packet_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ingest_packet_module
assert spec.loader is not None
spec.loader.exec_module(ingest_packet_module)


def count_rows(db, table):
    row = db.conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])


class IngestPacketTests(unittest.TestCase):
    def test_build_truth_map_db_can_apply_argument_schema(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)

        tables = {
            row["name"]
            for row in db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

        self.assertIn("claim_gate_results", tables)
        self.assertIn("argument_nodes", tables)
        self.assertIn("source_spans", tables)

    def test_gated_amplituhedron_ingest_stores_gate_rows_and_moves_d4(self):
        packet = json.loads(
            (ROOT / "content" / "information-packets" / "test-amplituhedron.json").read_text()
        )
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        before = PropagationEngine(db).run()

        delta = ingest_packet_module.ingest_packet(db, packet)
        after = PropagationEngine(db).run()

        self.assertEqual(delta["claims_seen"], 1)
        self.assertEqual(delta["runtime_claims_inserted"], 1)
        self.assertEqual(delta["argument_claims_recorded"], 1)
        self.assertEqual(delta["gate_results_stored"], 1)
        self.assertEqual(delta["gate_outcomes"], {"accepted": 1})
        self.assertEqual(count_rows(db, "claim_gate_results"), 1)
        self.assertEqual(count_rows(db, "argument_nodes"), 1)
        self.assertGreater(after["features"]["F8"], before["features"]["F8"])
        self.assertGreater(after["discriminators"]["D4"], before["discriminators"]["D4"])

    def test_gated_nanavira_ingest_records_argument_graph_without_runtime_update(self):
        packet = json.loads(
            (
                ROOT
                / "content"
                / "information-packets"
                / "nanavira-fundamental-structure-claims.json"
            ).read_text()
        )
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        before = PropagationEngine(db).run()

        delta = ingest_packet_module.ingest_packet(db, packet)
        after = PropagationEngine(db).run()

        self.assertEqual(delta["claims_seen"], 7)
        self.assertEqual(delta["runtime_claims_inserted"], 0)
        self.assertEqual(delta["argument_claims_recorded"], 7)
        self.assertEqual(delta["gate_results_stored"], 7)
        self.assertEqual(delta["gate_outcomes"]["accepted"], 5)
        self.assertEqual(delta["gate_outcomes"]["accepted_with_penalty"], 2)
        self.assertEqual(count_rows(db, "claim_gate_results"), 7)
        self.assertEqual(count_rows(db, "source_spans"), 7)
        self.assertGreaterEqual(count_rows(db, "argument_nodes"), 14)
        self.assertGreaterEqual(count_rows(db, "argument_edges"), 10)
        self.assertEqual(count_rows(db, "hetvabhasa_checks"), 2)
        self.assertEqual(count_rows(db, "tarka_falsifiers"), 7)
        self.assertEqual(after["features"], before["features"])
        self.assertEqual(after["discriminators"], before["discriminators"])
        self.assertEqual(after["branches"], before["branches"])


if __name__ == "__main__":
    unittest.main()
