import math
import unittest

from truthengine_working import (
    ClaimRecord,
    PropagationEngine,
    build_truth_map_db,
    log_odds,
)


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


if __name__ == "__main__":
    unittest.main()
