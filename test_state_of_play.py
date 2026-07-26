import importlib.util
import sys
import unittest
from pathlib import Path

from truthengine_working import build_truth_map_db


ROOT = Path(__file__).resolve().parent
INGEST_PATH = ROOT / "scripts" / "ingest-dossier.py"
STATE_PATH = ROOT / "scripts" / "state-of-play.py"

ingest_spec = importlib.util.spec_from_file_location("ingest_dossier_for_state_tests", INGEST_PATH)
ingest_dossier = importlib.util.module_from_spec(ingest_spec)
sys.modules[ingest_spec.name] = ingest_dossier
assert ingest_spec.loader is not None
ingest_spec.loader.exec_module(ingest_dossier)

state_spec = importlib.util.spec_from_file_location("state_of_play_module_for_tests", STATE_PATH)
state_of_play = importlib.util.module_from_spec(state_spec)
sys.modules[state_spec.name] = state_of_play
assert state_spec.loader is not None
state_spec.loader.exec_module(state_of_play)


QUESTION_ID = "q:reflexivity-intrinsic-or-constructed"


class StateOfPlayTests(unittest.TestCase):
    def build_reflexivity_graph(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        ingest_dossier.ingest_dossier(
            db,
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.argument.json",
        )
        ingest_dossier.ingest_source_map(
            db,
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.nanavira-map.json",
        )
        return db

    def insert_attack_graph(
        self,
        *,
        payload=None,
        strength=0.6,
        support=False,
    ):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        candidate = {
            "candidate_id": "cand:test",
            "name": "Test candidate",
            "best_case": "A candidate under attack.",
            "falsifiers": [{"type": "formal", "condition": "break it"}],
        }
        ingest_dossier.insert_candidate(db, "q:test", candidate)
        if support:
            db.conn.execute(
                """
                INSERT OR REPLACE INTO argument_nodes
                (node_id, node_type, title, statement, question_id, status, payload)
                VALUES ('cl:support', 'claim', 'support', 'support', 'q:test', 'accepted', ?)
                """,
                ('{"gate_outcome": "accepted"}',),
            )
            ingest_dossier.insert_edge(
                db,
                "edge:support:candidate",
                "cl:support",
                "cand:test",
                "supports",
                strength=0.4,
                polarity=1,
                rationale="support",
            )
        db.conn.execute(
            """
            INSERT OR REPLACE INTO argument_nodes
            (node_id, node_type, title, statement, question_id, status, payload)
            VALUES ('cl:attack', 'claim', 'attack', 'attack', 'q:test', 'accepted', ?)
            """,
            ('{"gate_outcome": "accepted"}',),
        )
        ingest_dossier.insert_edge(
            db,
            "edge:attack:candidate",
            "cl:attack",
            "cand:test",
            "attacks",
            strength=strength,
            polarity=-1,
            rationale="attack",
            payload=payload or {},
        )
        return db

    def test_reflexivity_state_of_play_is_derived_from_graph(self):
        db = self.build_reflexivity_graph()

        synthesis = state_of_play.synthesize_state_of_play(
            db,
            QUESTION_ID,
            persist=True,
        )

        answer = synthesis["best_current_answer"]
        self.assertIn("Structural reflexivity is locally strengthened", answer)
        self.assertIn("Universal consciousness is not entailed", answer)
        self.assertIn("Abhinavagupta is pressured at the universalization step", answer)
        self.assertIn("Abhinavagupta pressures Nanavira at manifestness", answer)
        self.assertIn("OVERLAPS, not BRIDGES", answer)
        self.assertEqual(3, len(synthesis["directional_critiques"]))
        self.assertEqual(1, len(synthesis["unresolved_correspondences"]))
        self.assertEqual("OVERLAPS", synthesis["unresolved_correspondences"][0]["status"])
        self.assertEqual([], synthesis["weakened_candidates"])
        self.assertEqual(
            2,
            synthesis["candidate_scores"]["cand:abh-vimarsa-intrinsic"][
                "pending_falsifier_count"
            ],
        )
        self.assertEqual(
            0.0,
            synthesis["candidate_scores"]["cand:abh-vimarsa-intrinsic"][
                "direct_pressure"
            ],
        )
        self.assertGreaterEqual(len(synthesis["strongest_argument_edges"]), 4)
        self.assertIn("snapshot_id", synthesis)

        row = db.conn.execute(
            """
            SELECT current_best_answer
            FROM state_of_play_snapshots
            WHERE snapshot_id = ?
            """,
            (synthesis["snapshot_id"],),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(answer, row["current_best_answer"])

    def test_report_text_contains_graph_sections(self):
        db = self.build_reflexivity_graph()
        synthesis = state_of_play.synthesize_state_of_play(
            db,
            QUESTION_ID,
            persist=False,
        )
        report = state_of_play.format_report(synthesis)

        self.assertIn("Bidirectional Critique:", report)
        self.assertIn("Unresolved Correspondences:", report)
        self.assertIn("Highest Causal-Power Argument Edges:", report)
        self.assertIn("cl:nanavira-duration-invariance-abheda", report)
        self.assertNotIn("Under Pressure:", report)

    def test_confirmed_falsifier_counts_as_direct_pressure(self):
        db = build_truth_map_db(seed_claims=False, argument_schema=True)
        candidate = {
            "candidate_id": "cand:test",
            "name": "Test candidate",
            "best_case": "A candidate with confirmed falsifiers.",
            "falsifiers": [
                {"type": "formal", "condition": "first defeat", "status": "tested_failed"},
                {"type": "formal", "condition": "second defeat", "status": "tested_failed"},
            ],
        }
        ingest_dossier.insert_candidate(db, "q:test", candidate)

        synthesis = state_of_play.synthesize_state_of_play(db, "q:test", persist=False)

        self.assertEqual(["Test candidate"], synthesis["defeated_candidates"])
        self.assertEqual(
            1.5,
            synthesis["candidate_scores"]["cand:test"]["direct_pressure"],
        )
        self.assertEqual(
            0,
            synthesis["candidate_scores"]["cand:test"]["pending_falsifier_count"],
        )

    def test_generic_direct_attack_does_not_weaken_without_core_marker(self):
        db = self.insert_attack_graph()

        synthesis = state_of_play.synthesize_state_of_play(db, "q:test", persist=False)

        self.assertEqual(["Test candidate"], synthesis["live_candidates"])
        self.assertEqual([], synthesis["weakened_candidates"])
        self.assertEqual([], synthesis["defeated_candidates"])
        self.assertEqual(0, synthesis["candidate_scores"]["cand:test"]["core_attack_count"])

    def test_core_attack_weakens_candidate_with_live_reformulation(self):
        db = self.insert_attack_graph(
            payload={
                "targets_core_commitment": True,
                "core_commitment_id": "core:test",
                "attack_gate_status": "accepted",
                "candidate_has_live_reformulation": True,
            }
        )

        synthesis = state_of_play.synthesize_state_of_play(db, "q:test", persist=False)

        self.assertEqual(["Test candidate"], synthesis["live_candidates"])
        self.assertEqual(["Test candidate"], synthesis["weakened_candidates"])
        self.assertEqual([], synthesis["defeated_candidates"])
        self.assertEqual(1, synthesis["candidate_scores"]["cand:test"]["core_attack_count"])

    def test_decisive_core_attack_defeats_unreformulated_candidate(self):
        db = self.insert_attack_graph(
            strength=0.7,
            payload={
                "targets_core_commitment": True,
                "core_commitment_id": "core:test",
                "attack_gate_status": "accepted",
                "candidate_has_live_reformulation": False,
            }
        )

        synthesis = state_of_play.synthesize_state_of_play(db, "q:test", persist=False)

        self.assertEqual([], synthesis["live_candidates"])
        self.assertEqual([], synthesis["weakened_candidates"])
        self.assertEqual(["Test candidate"], synthesis["defeated_candidates"])
        self.assertEqual(
            1,
            synthesis["candidate_scores"]["cand:test"]["decisive_core_attack_count"],
        )


if __name__ == "__main__":
    unittest.main()
