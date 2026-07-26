"""
Validation tests: does the system produce sensible outputs
on constructed but realistic evidence scenarios?

These are not unit tests. They test emergent behaviour
across the full pipeline. A failure here means either
the math is wrong, the seed data is wrong, or the
indicator likelihood ratios are miscalibrated.

Uses fixtures/engine_factory pattern for dependency injection.
"""

import pytest
import math


class TestDirectionalCorrectness:
    """
    The most important validation class.
    If these fail, nothing else matters.
    """

    def test_strong_I07_evidence_raises_B3_relative_to_B2(
        self, engine_factory, indicator_claim_factory
    ):
        """
        I07 (Bioelectric Patterning) has LR=1.5 for F2.
        F2=high is required by B3 (Platonic/Computational).
        F2=low is required by B2 (Physical realism).

        Strong evidence for I07 should raise B3/B2 ratio.
        """
        engine = engine_factory()
        result_before = engine.run()
        ratio_before = result_before["branches"]["B3"] / result_before["branches"]["B2"]

        claim = indicator_claim_factory(
            indicator_id="I07", lbf=0.6, w_rel=0.85, w_map=0.65, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        ratio_after = result_after["branches"]["B3"] / result_after["branches"]["B2"]

        assert ratio_after > ratio_before, (
            f"I07 evidence should raise B3/B2 ratio. "
            f"Before: {ratio_before:.4f}, After: {ratio_after:.4f}"
        )

    def test_strong_I05_evidence_raises_B5_relative_to_B2(
        self, engine_factory, indicator_claim_factory
    ):
        """
        I05 (Nonlocal Correlations) has LR=2.0 for F4.
        F4=high required by B5 (Process metaphysics).
        F4 not required by B2 (Physical realism).
        """
        engine = engine_factory()
        result_before = engine.run()
        ratio_before = result_before["branches"]["B5"] / result_before["branches"]["B2"]

        claim = indicator_claim_factory(
            indicator_id="I05", lbf=0.5, w_rel=0.9, w_map=0.55, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        ratio_after = result_after["branches"]["B5"] / result_after["branches"]["B2"]

        assert ratio_after > ratio_before

    def test_challenge_to_I07_lowers_indicator(
        self, engine_factory, indicator_claim_factory
    ):
        """
        A claim challenging I07 should lower the I07 indicator probability.
        """
        engine = engine_factory()

        support = indicator_claim_factory("I07", lbf=0.5, direction=1)
        engine.db.add_claim(support)
        result_mid = engine.run()
        i07_mid = result_mid["indicators"]["I07"]

        challenge = indicator_claim_factory("I07", lbf=0.5, direction=-1)
        engine.db.add_claim(challenge)
        result_after = engine.run()
        i07_after = result_after["indicators"]["I07"]

        assert i07_after < i07_mid, (
            f"I07 should decrease when challenged: {i07_mid:.4f} -> {i07_after:.4f}"
        )

    def test_B4_requires_multiple_features_so_moves_slowly(
        self, engine_factory, indicator_claim_factory
    ):
        """
        B4 requires F1 AND F2 AND F3 AND F5 AND F6 AND F7.
        Evidence for only F2 should move B4 much less than B3
        (which only requires F2 AND F3).
        """
        engine = engine_factory()
        result_before = engine.run()

        for _ in range(3):
            claim = indicator_claim_factory("I07", lbf=0.6, direction=1)
            engine.db.add_claim(claim)

        result_after = engine.run()

        b3_change = abs(result_after["branches"]["B3"] - result_before["branches"]["B3"])
        b4_change = abs(result_after["branches"]["B4"] - result_before["branches"]["B4"])

        assert b3_change > b4_change * 10, (
            f"B3 should move much more than B4 from F2-only evidence. "
            f"B3 change: {b3_change:.6f}, B4 change: {b4_change:.6f}, "
            f"ratio: {b3_change / max(b4_change, 1e-10):.1f}x"
        )


class TestEvidenceStrengthOrdering:
    """
    Stronger evidence should produce larger updates than weaker evidence.
    """

    def test_adversarial_beats_single_experiment(
        self, engine_factory, indicator_claim_factory
    ):
        """
        An adversarial multisite study (higher w_rel=0.9) targeting I07
        should move F2 more than a single experiment (lower w_rel=0.7).
        """
        engine1 = engine_factory()
        engine2 = engine_factory()

        adv_claim = indicator_claim_factory(
            "I07", lbf=0.6, w_rel=0.9, w_map=0.65, direction=1
        )
        engine1.db.add_claim(adv_claim)
        result_adv = engine1.run()

        single_claim = indicator_claim_factory(
            "I07", lbf=0.6, w_rel=0.7, w_map=0.65, direction=1
        )
        engine2.db.add_claim(single_claim)
        result_single = engine2.run()

        f2_adv = result_adv["features"]["F2"]
        f2_single = result_single["features"]["F2"]

        assert f2_adv > f2_single, (
            f"High-reliability study should move F2 more. "
            f"Adversarial: {f2_adv:.4f}, Single: {f2_single:.4f}"
        )


class TestDependenceDiscounting:
    """
    Validates that paradigm clustering actually reduces
    the accumulation of redundant evidence.
    """

    def test_ten_same_paradigm_papers_less_than_ten_independent_papers(
        self, engine_factory, indicator_claim_factory
    ):
        """
        Ten claims from paradigm='IIT' should move F2
        less than ten claims from ten different paradigms.
        """
        engine_same = engine_factory()
        engine_diff = engine_factory()

        for i in range(10):
            claim_same = indicator_claim_factory(
                indicator_id="I07", lbf=0.4, w_rel=0.8, w_map=0.60,
                direction=1, paradigm="IIT",
            )
            engine_same.db.add_claim(claim_same)

            claim_diff = indicator_claim_factory(
                indicator_id="I07", lbf=0.4, w_rel=0.8, w_map=0.60,
                direction=1, paradigm=f"paradigm_{i}",
            )
            engine_diff.db.add_claim(claim_diff)

        result_same = engine_same.run()
        result_diff = engine_diff.run()

        f2_same = result_same["features"]["F2"]
        f2_diff = result_diff["features"]["F2"]

        assert f2_same < f2_diff, (
            f"Same-paradigm evidence should accumulate less. "
            f"IIT×10: {f2_same:.4f}, Independent×10: {f2_diff:.4f}"
        )

    def test_dependence_discount_does_not_eliminate_evidence(
        self, engine_factory, indicator_claim_factory
    ):
        """
        Even 10 same-paradigm claims should move the feature
        more than 1 claim. Discounting reduces, not eliminates.
        """
        engine_ten = engine_factory()
        engine_one = engine_factory()

        for i in range(10):
            claim = indicator_claim_factory(
                "I07", lbf=0.4, w_rel=0.8, w_map=0.60, direction=1, paradigm="IIT"
            )
            engine_ten.db.add_claim(claim)

        single = indicator_claim_factory(
            "I07", lbf=0.4, w_rel=0.8, w_map=0.60, direction=1, paradigm="IIT"
        )
        engine_one.db.add_claim(single)

        result_ten = engine_ten.run()
        result_one = engine_one.run()

        assert result_ten["features"]["F2"] > result_one["features"]["F2"]


class TestSystemSanityChecks:
    """
    High-level sanity checks. If these fail the system
    is producing nonsense regardless of test coverage.
    """

    def test_no_evidence_state_is_reproducible(self, engine_factory):
        """
        Running the engine twice with no evidence gives
        identical results. Tests determinism.
        """
        engine1 = engine_factory()
        engine2 = engine_factory()

        result1 = engine1.run()
        result2 = engine2.run()

        for fid in result1["features"]:
            assert abs(result1["features"][fid] - result2["features"][fid]) < 1e-12

    def test_branch_ordering_stable_under_tiny_evidence(
        self, engine_factory, indicator_claim_factory
    ):
        """
        A single tiny claim should not overturn the branch ranking.
        B5 should still beat B4 after one weak claim for B4.
        """
        engine = engine_factory()
        result_before = engine.run()
        assert result_before["branches"]["B5"] > result_before["branches"]["B4"]

        claim = indicator_claim_factory(
            "I12", lbf=0.05, w_rel=0.5, w_map=0.10, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()

        assert result_after["branches"]["B5"] > result_after["branches"]["B4"], (
            "One tiny claim should not overturn B5 > B4"
        )

    def test_massive_evidence_cannot_push_probability_to_boundary(
        self, engine_factory, indicator_claim_factory
    ):
        """
        Even 100 strong claims cannot push a feature to exactly
        0 or 1. Tests numerical stability in realistic scenario.
        """
        engine = engine_factory()

        for _ in range(100):
            claim = indicator_claim_factory(
                "I09", lbf=0.5, w_rel=0.9, w_map=0.60, direction=1
            )
            engine.db.add_claim(claim)

        result = engine.run()

        for fid, prob in result["features"].items():
            assert 0 < prob < 1, f"Feature {fid} hit boundary: {prob}"

    def test_mixed_result_moves_indicators_oppositely(
        self, engine_factory, indicator_claim_factory
    ):
        """
        Simulates a mixed result: evidence that
        challenges one theory while supporting another.

        Challenge to I07 (targets F2)
        Support for I04 (targets F4)

        Expected: I07 decreases, I04 increases.
        Neither branch dominates (modest changes).
        """
        engine = engine_factory()
        result_before = engine.run()

        challenge_I07 = indicator_claim_factory(
            indicator_id="I07", lbf=0.5, w_rel=0.85, w_map=0.55,
            direction=-1, paradigm="MixedStudy",
        )

        support_I04 = indicator_claim_factory(
            indicator_id="I04", lbf=0.4, w_rel=0.85, w_map=0.50,
            direction=1, paradigm="MixedStudy",
        )

        engine.db.add_claim(challenge_I07)
        engine.db.add_claim(support_I04)
        result_after = engine.run()

        assert result_after["indicators"]["I07"] < result_before["indicators"]["I07"], (
            "I07 should be challenged (decrease)"
        )
        assert result_after["indicators"]["I04"] > result_before["indicators"]["I04"], (
            "I04 should be supported (increase)"
        )
        assert result_after["features"]["F4"] > result_before["features"]["F4"], (
            "F4 should increase from I04 support"
        )

        b3_change = abs(result_after["branches"]["B3"] - result_before["branches"]["B3"])
        b5_change = abs(result_after["branches"]["B5"] - result_before["branches"]["B5"])

        assert b3_change < 0.10, f"B3 moved {b3_change:.3f} from 2 papers, too much"
        assert b5_change < 0.10, f"B5 moved {b5_change:.3f} from 2 papers, too much"
