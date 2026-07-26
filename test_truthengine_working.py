import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from truthengine_working import (
    ClaimRecord,
    EVIDENCE_DIMENSIONS,
    PropagationEngine,
    build_truth_map_db,
    compute_convergence,
    log_odds,
)


ROOT = Path(__file__).resolve().parent
GATE_PATH = ROOT / "scripts" / "nyaya-truthmap-gate.py"
spec = importlib.util.spec_from_file_location("nyaya_truthmap_gate_for_pipeline", GATE_PATH)
nyaya_truthmap_gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nyaya_truthmap_gate
assert spec.loader is not None
spec.loader.exec_module(nyaya_truthmap_gate)


def claim(
    cid,
    feature_ids,
    lbf,
    paradigm,
    question_id="q:consciousness-fundamental",
    w_rel=1.0,
    w_map=1.0,
    w_aux=1.0,
):
    return ClaimRecord(
        id=cid,
        target_feature_ids=feature_ids,
        log_bayes_factor=lbf,
        w_rel=w_rel,
        w_map=w_map,
        w_aux=w_aux,
        paradigm=paradigm,
        target_question_id=question_id,
    )


class TruthEngineWorkingTests(unittest.TestCase):
    def test_seeded_truth_map_runs_against_real_question_files(self):
        db = build_truth_map_db(seed_claims=True)
        result = PropagationEngine(db).run()

        self.assertEqual(result["claims_processed"], 8)
        self.assertEqual(db.count_discriminator_effects(), 60)
        self.assertEqual(set(result["discriminators"]), {"D1", "D2", "D3", "D4", "D5"})
        self.assertEqual(
            set(result["dimension_features"]["F1"]),
            set(EVIDENCE_DIMENSIONS),
        )
        self.assertEqual(
            set(result["dimension_discriminators"]["D3"]),
            set(EVIDENCE_DIMENSIONS),
        )
        self.assertEqual(set(result["dimension_branches"]["B4"]), set(EVIDENCE_DIMENSIONS))
        self.assertIn("D3", result["dimension_convergence"]["discriminators"])
        self.assertLess(result["features"]["F1"], 0.40)
        self.assertGreater(result["features"]["F4"], 0.50)
        self.assertAlmostEqual(sum(result["branches"].values()), 1.0, places=12)
        self.assertEqual(db.branch_state("B3")["score_type"], "relative_support")

        q = db.question_state("q:brain-filter-or-appearance")
        self.assertNotEqual(q["confidence"], 0.30)
        self.assertEqual(q["status"], "underdetermined")

    def test_single_incremental_claim_moves_question_status_and_branch_support(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        b2_before = before["branches"]["B2"]

        c = claim("cl:test-f1-support", ["F1"], 1.0, "independent")
        db.add_claim(c)
        after = engine.run(new_claim_ids=[c.id])

        expected_f1 = 1.0 / (1.0 + math.exp(-(log_odds(0.40) + 1.0)))
        self.assertAlmostEqual(after["features"]["F1"], expected_f1, places=12)
        self.assertLess(after["branches"]["B2"], b2_before)

        q = db.question_state("q:consciousness-fundamental")
        self.assertEqual(q["status"], "plausible")
        self.assertAlmostEqual(q["confidence"], expected_f1, places=12)

    def test_incremental_additive_update_matches_full_recompute(self):
        c1 = claim("cl:test-f2-support", ["F2"], 0.7, "p1")
        c2 = claim("cl:test-f2-second", ["F2"], 0.4, "p2")

        inc_db = build_truth_map_db(seed_claims=False)
        inc_engine = PropagationEngine(inc_db)
        inc_engine.run()
        inc_db.add_claim(c1)
        inc_engine.run(new_claim_ids=[c1.id])
        inc_db.add_claim(c2)
        inc = inc_engine.run(new_claim_ids=[c2.id])

        full_db = build_truth_map_db(seed_claims=False)
        full_db.add_claim(c1)
        full_db.add_claim(c2)
        full = PropagationEngine(full_db).run()

        self.assertAlmostEqual(inc["features"]["F2"], full["features"]["F2"], places=12)
        self.assertAlmostEqual(inc["branches"]["B3"], full["branches"]["B3"], places=12)

    def test_all_supporting_and_all_undermining_claims_move_posterior_sensibly(self):
        support_db = build_truth_map_db(seed_claims=False)
        undermine_db = build_truth_map_db(seed_claims=False)

        for i in range(3):
            support_db.add_claim(claim(f"cl:support-{i}", ["F2"], 0.6, f"p{i}"))
            undermine_db.add_claim(claim(f"cl:undermine-{i}", ["F2"], -0.6, f"p{i}"))

        support = PropagationEngine(support_db).run()
        undermine = PropagationEngine(undermine_db).run()

        self.assertGreater(support["features"]["F2"], 0.55)
        self.assertLess(undermine["features"]["F2"], 0.55)
        self.assertGreater(support["branches"]["B3"], undermine["branches"]["B3"])
        self.assertLess(support["branches"]["B2"], undermine["branches"]["B2"])

    def test_paradigm_crowding_discounts_redundant_sources(self):
        same_db = build_truth_map_db(seed_claims=False)
        diff_db = build_truth_map_db(seed_claims=False)
        one_db = build_truth_map_db(seed_claims=False)

        for i in range(6):
            same_db.add_claim(claim(f"cl:same-{i}", ["F2"], 0.4, "same-school"))
            diff_db.add_claim(claim(f"cl:diff-{i}", ["F2"], 0.4, f"school-{i}"))
        one_db.add_claim(claim("cl:one", ["F2"], 0.4, "same-school"))

        same = PropagationEngine(same_db).run()
        diff = PropagationEngine(diff_db).run()
        one = PropagationEngine(one_db).run()

        self.assertGreater(same["features"]["F2"], one["features"]["F2"])
        self.assertLess(same["features"]["F2"], diff["features"]["F2"])

    def test_supersession_requires_full_recompute_and_removes_old_effect(self):
        db = build_truth_map_db(seed_claims=False)
        db.add_claim(claim("cl:old-positive", ["F1"], 1.2, "lab"))
        positive = PropagationEngine(db).run()

        db.supersede_claim(
            "cl:old-positive",
            {
                "claim_id": "cl:new-negative",
                "question_id": "q:consciousness-fundamental",
                "features": ["F1"],
                "source_type": "ro",
                "source_id": "ro:correction",
                "claim_text": "Correction reverses the earlier positive claim.",
                "log_bayes_factor": -1.2,
                "paradigm": "lab",
            },
        )
        recomputed = PropagationEngine(db).run()

        active_ids = [c.id for c in db.get_all_claims()]
        self.assertEqual(active_ids, ["cl:new-negative"])
        self.assertGreater(positive["features"]["F1"], 0.40)
        self.assertLess(recomputed["features"]["F1"], 0.40)

    def test_direct_d1_yes_claim_boosts_physical_realism_over_structural_rivals(self):
        db = build_truth_map_db(seed_claims=False)
        before = PropagationEngine(db).run()
        db.add_claim_dict(
            {
                "claim_id": "cl:d1-physical-supervenience-direct",
                "targets": [{"target_id": "D1", "target_type": "discriminator"}],
                "source_type": "experiment",
                "source_id": "src:d1-test",
                "claim_text": "Direct test supports physical supervenience of observer facts.",
                "log_bayes_factor": 4.0,
                "w_rel": 1.0,
                "w_map": 1.0,
                "w_aux": 1.0,
                "paradigm": "physical_closure",
            }
        )

        after = PropagationEngine(db).run()

        self.assertGreater(after["discriminators"]["D1"], 0.85)
        self.assertEqual(db.discriminator_state("D1")["status"], "answered")
        self.assertGreater(after["branches"]["B2"], before["branches"]["B2"])
        self.assertGreater(after["branches"]["B2"], after["branches"]["B3"])
        self.assertGreater(after["branches"]["B2"], after["branches"]["B4"])

    def test_new_style_targets_update_features_and_direct_discriminators(self):
        db = build_truth_map_db(seed_claims=False)
        before = PropagationEngine(db).run()
        db.add_claim_dict(
            {
                "claim_id": "cl:amplituhedron-new-targets",
                "targets": [
                    {"target_id": "D4", "target_type": "discriminator"},
                    {"target_id": "F8", "target_type": "feature"},
                ],
                "source_type": "paper",
                "source_id": "arxiv:1312.2007",
                "claim_text": "Positive geometry supports emergent physical law in a restricted scattering domain.",
                "log_bayes_factor": 0.45,
                "w_rel": 0.75,
                "w_map": 0.60,
                "w_aux": 0.70,
                "paradigm": "high_energy_physics",
            }
        )

        after = PropagationEngine(db).run()

        self.assertGreater(after["features"]["F8"], before["features"]["F8"])
        self.assertGreater(after["discriminators"]["D4"], before["discriminators"]["D4"])

    def test_contribution_trace_explains_weight_decomposition_per_source(self):
        db = build_truth_map_db(seed_claims=False)
        db.add_claim_dict(
            {
                "claim_id": "cl:amplituhedron-provenance",
                "targets": [
                    {"target_id": "D4", "target_type": "discriminator"},
                    {"target_id": "F8", "target_type": "feature"},
                ],
                "source_type": "paper",
                "source_id": "arxiv:1312.2007",
                "claim_text": "Locality and unitarity emerge from positive geometry in planar N=4 SYM.",
                "log_bayes_factor": 0.6,
                "w_rel": 0.75,
                "w_map": 0.60,
                "w_aux": 0.70,
                "paradigm": "high_energy_physics",
            }
        )

        trace = PropagationEngine(db).contribution_trace(source_id="arxiv:1312.2007")
        by_target = {row["target_id"]: row for row in trace}

        self.assertAlmostEqual(by_target["D4"]["effective_lbf"], 0.189, places=12)
        self.assertEqual(by_target["D4"]["evidence_role"], "direct")
        self.assertEqual(by_target["D4"]["w_dep"], 1.0)
        self.assertAlmostEqual(by_target["D4"]["posterior_before"], 0.5, places=12)
        self.assertGreater(by_target["D4"]["posterior_after"], 0.5)
        self.assertGreater(by_target["D4"]["branch_support_delta"]["B3"], 0)
        self.assertLess(by_target["D4"]["branch_support_delta"]["B2"], 0)
        self.assertAlmostEqual(by_target["F8"]["effective_lbf"], 0.189, places=12)

        blame = PropagationEngine(db).blame("D4")
        self.assertEqual(blame[0]["source_id"], "arxiv:1312.2007")
        self.assertEqual(blame[0]["evidence_dimension"], "empirical")

    def test_dimension_specific_crowding_does_not_cross_tracks(self):
        db = build_truth_map_db(seed_claims=False)
        for dimension in ("empirical", "phenomenological", "empirical"):
            db.add_claim_dict(
                {
                    "claim_id": f"cl:{dimension}-{len(db.get_all_claims_with_targets())}",
                    "targets": [{"target_id": "D4", "target_type": "discriminator"}],
                    "source_type": "paper",
                    "source_id": f"src:{dimension}",
                    "claim_text": f"{dimension} support for D4",
                    "log_bayes_factor": 1.0,
                    "w_rel": 1.0,
                    "w_map": 1.0,
                    "w_aux": 1.0,
                    "paradigm": "shared-paradigm",
                    "evidence_dimension": dimension,
                }
            )

        trace = PropagationEngine(db).contribution_trace()
        records = [
            row
            for row in trace
            if row["target_id"] == "D4" and row["evidence_role"] == "direct"
        ]

        by_claim = {row["claim_id"]: row for row in records}
        self.assertEqual(
            by_claim["cl:phenomenological-1"]["evidence_dimension"],
            "phenomenological",
        )
        self.assertAlmostEqual(by_claim["cl:empirical-0"]["w_dep"], 1.0, places=12)
        self.assertAlmostEqual(
            by_claim["cl:phenomenological-1"]["w_dep"],
            1.0,
            places=12,
        )
        self.assertAlmostEqual(
            by_claim["cl:empirical-2"]["w_dep"],
            2.0 / 3.0,
            places=12,
        )

    def test_dimension_tracks_can_diverge_and_report_low_convergence(self):
        db = build_truth_map_db(seed_claims=False)
        db.add_claim_dict(
            {
                "claim_id": "cl:d3-empirical-negative",
                "targets": [{"target_id": "D3", "target_type": "discriminator"}],
                "source_type": "experiment",
                "source_id": "src:empirical-d3",
                "claim_text": "Third-person structure appears sufficient in this task.",
                "log_bayes_factor": -4.0,
                "paradigm": "neuroscience",
                "evidence_dimension": "empirical",
            }
        )
        db.add_claim_dict(
            {
                "claim_id": "cl:d3-phenomenological-positive",
                "targets": [{"target_id": "D3", "target_type": "discriminator"}],
                "source_type": "paper",
                "source_id": "src:phenomenological-d3",
                "claim_text": "Reflexive manifestness is required by the argument.",
                "log_bayes_factor": 4.0,
                "paradigm": "phenomenology",
                "evidence_dimension": "phenomenological",
            }
        )

        result = PropagationEngine(db).run()
        d3_dims = result["dimension_discriminators"]["D3"]

        self.assertLess(d3_dims["empirical"], 0.10)
        self.assertGreater(d3_dims["phenomenological"], 0.90)
        self.assertEqual(d3_dims["contemplative"], 0.50)
        self.assertLess(result["dimension_convergence"]["discriminators"]["D3"], 0.50)
        self.assertAlmostEqual(
            compute_convergence(
                {
                    "phenomenological": 0.5,
                    "empirical": 0.5,
                    "contemplative": 0.5,
                }
            ),
            1.0,
            places=12,
        )

    def test_d5_yes_with_identity_features_separates_b6_from_b3(self):
        db = build_truth_map_db(seed_claims=False)
        db.add_claim_dict(
            {
                "claim_id": "cl:d5-direct-identity-continuity",
                "targets": [
                    {"target_id": "D5", "target_type": "discriminator"},
                    {"target_id": "F5", "target_type": "feature"},
                    {"target_id": "F7", "target_type": "feature"},
                ],
                "source_type": "experiment",
                "source_id": "src:d5-test",
                "claim_text": "Operational evidence supports substrate-discontinuous identity continuity.",
                "log_bayes_factor": 6.0,
                "w_rel": 1.0,
                "w_map": 1.0,
                "w_aux": 1.0,
                "paradigm": "identity_continuity",
            }
        )

        after = PropagationEngine(db).run()

        self.assertGreater(after["discriminators"]["D5"], 0.95)
        self.assertGreater(after["branches"]["B6"], after["branches"]["B3"])
        self.assertGreater(after["branches"]["B6"], after["branches"]["B2"])

    def test_amplituhedron_moves_d4_toward_yes_known_truth(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        db.add_claim_dict(
            {
                "claim_id": "cl:test-known-amplituhedron-d4",
                "targets": [{"target_id": "D4", "target_type": "discriminator"}],
                "source_type": "paper",
                "source_id": "arxiv:1312.2007",
                "claim_text": "The amplituhedron derives locality and unitarity from positive geometry.",
                "log_bayes_factor": 0.6,
                "w_rel": 0.75,
                "w_map": 0.60,
                "w_aux": 0.70,
                "paradigm": "high_energy_physics",
                "evidence_dimension": "empirical",
            }
        )

        after = engine.run()

        self.assertGreater(after["discriminators"]["D4"], before["discriminators"]["D4"])
        self.assertGreater(after["dimension_discriminators"]["D4"]["empirical"], 0.5)

    def test_iit_supports_d3_intrinsic_phenomenality_known_truth(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        db.add_claim_dict(
            {
                "claim_id": "cl:test-known-iit-d3",
                "targets": [{"target_id": "D3", "target_type": "discriminator"}],
                "source_type": "paper",
                "source_id": "src:iit-intrinsicality",
                "claim_text": "IIT's intrinsicality axiom supports experience as intrinsic to the system.",
                "log_bayes_factor": 0.5,
                "w_rel": 0.80,
                "w_map": 0.65,
                "w_aux": 0.70,
                "paradigm": "iit",
                "evidence_dimension": "empirical",
            }
        )

        after = engine.run()

        self.assertGreater(after["discriminators"]["D3"], before["discriminators"]["D3"])
        self.assertGreater(after["dimension_discriminators"]["D3"]["empirical"], 0.5)

    def test_brain_damage_moves_d3_toward_no_known_truth(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        db.add_claim_dict(
            {
                "claim_id": "cl:test-known-brain-damage-d3",
                "targets": [{"target_id": "D3", "target_type": "discriminator"}],
                "source_type": "experiment",
                "source_id": "src:brain-damage",
                "claim_text": "Brain damage systematically alters conscious capacities.",
                "log_bayes_factor": -0.5,
                "w_rel": 0.85,
                "w_map": 0.70,
                "w_aux": 0.80,
                "paradigm": "neuroscience",
                "evidence_dimension": "empirical",
            }
        )

        after = engine.run()

        self.assertLess(after["discriminators"]["D3"], before["discriminators"]["D3"])
        self.assertLess(after["dimension_discriminators"]["D3"]["empirical"], 0.5)

    def test_opposing_claims_on_f1_produce_low_dimension_convergence(self):
        db = build_truth_map_db(seed_claims=False)
        db.add_claim_dict(
            {
                "claim_id": "cl:test-trika-f1-positive",
                "targets": [{"target_id": "F1", "target_type": "feature"}],
                "source_type": "text",
                "source_id": "src:trika",
                "claim_text": "Trika argues consciousness is fundamental.",
                "log_bayes_factor": 4.0,
                "paradigm": "trika",
                "evidence_dimension": "phenomenological",
            }
        )
        db.add_claim_dict(
            {
                "claim_id": "cl:test-neuro-f1-negative",
                "targets": [{"target_id": "F1", "target_type": "feature"}],
                "source_type": "experiment",
                "source_id": "src:neuroscience",
                "claim_text": "Neuroscience evidence pressures consciousness-fundamental interpretations.",
                "log_bayes_factor": -4.0,
                "paradigm": "neuroscience",
                "evidence_dimension": "empirical",
            }
        )

        result = PropagationEngine(db).run()

        self.assertLess(result["dimension_convergence"]["features"]["F1"], 0.5)
        self.assertGreater(result["dimension_features"]["F1"]["phenomenological"], 0.90)
        self.assertLess(result["dimension_features"]["F1"]["empirical"], 0.10)

    def test_extreme_lbf_does_not_overflow_or_return_nan(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        engine.run()
        c = claim("cl:test-extreme-lbf", ["F1"], 1000.0, "test")
        db.add_claim(c)

        result = engine.run(new_claim_ids=[c.id])

        self.assertFalse(math.isnan(result["features"]["F1"]))
        self.assertLess(result["features"]["F1"], 1.0)
        self.assertGreater(result["features"]["F1"], 0.999)

    def test_zero_weights_do_not_crash_or_move_prior(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        c = ClaimRecord(
            id="cl:test-zero-weights",
            target_feature_ids=["F1"],
            log_bayes_factor=0.5,
            w_rel=0.0,
            w_map=0.0,
            w_aux=0.0,
            paradigm="test",
        )
        db.add_claim(c)

        result = engine.run(new_claim_ids=[c.id])

        self.assertAlmostEqual(result["features"]["F1"], before["features"]["F1"], places=12)

    def test_nonexistent_feature_target_does_not_crash_or_move_known_features(self):
        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        c = ClaimRecord(
            id="cl:test-nonexistent-feature",
            target_feature_ids=["F99"],
            log_bayes_factor=0.5,
            w_rel=1.0,
            w_map=1.0,
            w_aux=1.0,
            paradigm="test",
        )
        db.add_claim(c)

        result = engine.run(new_claim_ids=[c.id])

        self.assertAlmostEqual(result["features"]["F1"], before["features"]["F1"], places=12)
        self.assertAlmostEqual(result["features"]["F8"], before["features"]["F8"], places=12)

    def test_same_paradigm_claims_are_discounted_below_independent_claims(self):
        same_db = build_truth_map_db(seed_claims=False)
        independent_db = build_truth_map_db(seed_claims=False)

        for i in range(10):
            same_db.add_claim(claim(f"cl:test-same-paradigm-{i}", ["F1"], 0.8, "same_paradigm"))
            independent_db.add_claim(
                claim(f"cl:test-independent-paradigm-{i}", ["F1"], 0.8, f"paradigm_{i}")
            )

        same = PropagationEngine(same_db).run()
        independent = PropagationEngine(independent_db).run()

        self.assertLess(same["features"]["F1"], independent["features"]["F1"] - 0.03)
        self.assertLess(same["features"]["F1"], 0.95)

    def test_packet_gate_ingest_moves_d4_and_blame_attributes_source(self):
        packet_path = ROOT / "content" / "information-packets" / "test-amplituhedron.json"
        packet = json.loads(packet_path.read_text())

        gate_results = [
            nyaya_truthmap_gate.validate(claim, packet["claims"])
            for claim in packet["claims"]
        ]
        self.assertTrue(all(result.can_update_posterior for result in gate_results))

        db = build_truth_map_db(seed_claims=False)
        engine = PropagationEngine(db)
        before = engine.run()
        for packet_claim in packet["claims"]:
            db.add_claim_dict(packet_claim)
        after = engine.run()

        self.assertGreater(after["features"]["F8"], before["features"]["F8"])
        self.assertGreater(after["discriminators"]["D4"], before["discriminators"]["D4"])

        trace = engine.contribution_trace(source_id="ro:amplituhedron")
        by_target = {row["target_id"]: row for row in trace}
        self.assertIn("F8", by_target)
        self.assertIn("D4", by_target)
        self.assertEqual(by_target["D4"]["evidence_role"], "derived_mapping")
        self.assertGreater(by_target["D4"]["posterior_delta"], 0)


if __name__ == "__main__":
    unittest.main()
