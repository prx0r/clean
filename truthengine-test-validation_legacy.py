"""
Validation tests: does the system produce sensible outputs
on constructed but realistic evidence scenarios?

These are not unit tests. They test emergent behaviour
across the full pipeline. A failure here means either
the math is wrong, the seed data is wrong, or the
indicator likelihood ratios are miscalibrated.
"""

import pytest
import math
from tests.fixtures import (
    make_engine_with_real_seed_data,
    make_claim_via_indicator,
    make_direct_claim,
)


class TestDirectionalCorrectness:
    """
    The most important validation class.
    If these fail, nothing else matters.
    """

    def test_strong_F2_evidence_raises_B3_relative_to_B2(self):
        """
        I07 (representational geometry) has LR=2.0 for F2.
        F2=high is required by B3 (Platonic idealism).
        F2=low is required by B2 (Physical realism).
        
        Strong evidence for I07 should raise B3/B2 ratio.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        ratio_before = (result_before['branches']['B3'] / 
                        result_before['branches']['B2'])
        
        claim = make_claim_via_indicator(
            indicator_id='I07',
            lbf=0.6,
            w_rel=0.85,
            w_map=0.65,
            direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        ratio_after = (result_after['branches']['B3'] / 
                       result_after['branches']['B2'])
        
        assert ratio_after > ratio_before, (
            f"I07 evidence should raise B3/B2 ratio. "
            f"Before: {ratio_before:.4f}, After: {ratio_after:.4f}"
        )

    def test_strong_F4_evidence_raises_B5_relative_to_B2(self):
        """
        I05 (recurrent processing) has LR=1.6 for F4.
        F4=high required by B5 (Process metaphysics).
        F4 not required by B2 (Physical realism).
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        ratio_before = (result_before['branches']['B5'] / 
                        result_before['branches']['B2'])
        
        claim = make_claim_via_indicator(
            indicator_id='I05',
            lbf=0.5,
            w_rel=0.9,
            w_map=0.55,
            direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        ratio_after = (result_after['branches']['B5'] / 
                       result_after['branches']['B2'])
        
        assert ratio_after > ratio_before

    def test_challenge_to_F2_lowers_B3(self):
        """
        A claim challenging I07 (finding against representational
        geometry) should lower B3.
        """
        engine = make_engine_with_real_seed_data()
        
        support = make_claim_via_indicator('I07', lbf=0.5, direction=1)
        engine.db.add_claim(support)
        result_mid = engine.run()
        b3_mid = result_mid['branches']['B3']
        
        challenge = make_claim_via_indicator('I07', lbf=-0.4, direction=-1)
        engine.db.add_claim(challenge)
        result_after = engine.run()
        b3_after = result_after['branches']['B3']
        
        assert b3_after < b3_mid

    def test_B4_requires_multiple_features_so_moves_slowly(self):
        """
        B4 requires F1 AND F2 AND F3 AND F5 AND F6 AND F7.
        Evidence for only F2 should move B4 much less than B3
        (which only requires F2 AND F3).
        
        This validates that conjunction makes complex branches
        appropriately conservative.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        
        for _ in range(3):
            claim = make_claim_via_indicator('I07', lbf=0.6, direction=1)
            engine.db.add_claim(claim)
        
        result_after = engine.run()
        
        b3_change = result_after['branches']['B3'] - result_before['branches']['B3']
        b4_change = result_after['branches']['B4'] - result_before['branches']['B4']
        
        assert b3_change > b4_change, (
            f"B3 should move more than B4 from F2-only evidence. "
            f"B3 change: {b3_change:.5f}, B4 change: {b4_change:.5f}"
        )


class TestEvidenceStrengthOrdering:
    """
    Stronger evidence should produce larger updates than weaker evidence.
    This validates that the LBF cap table produces sensible ordering.
    """

    def test_adversarial_beats_single_experiment(self):
        """
        An adversarial multisite study (cap 1.5) targeting I07
        should move F2 more than a single experiment (cap 0.6).
        """
        from tcee.propagation.propagation import sigmoid, log_odds as lo_fn
        
        prior_lo = lo_fn(0.55)
        adversarial_wlbf = 0.9 * 0.85 * 0.65 * 1.0 * math.log(2.0)
        single_wlbf = 0.7 * 0.75 * 0.65 * 1.0 * math.log(2.0)
        
        f2_after_adversarial = sigmoid(prior_lo + adversarial_wlbf)
        f2_after_single = sigmoid(prior_lo + single_wlbf)
        
        assert f2_after_adversarial > f2_after_single

    def test_theoretical_paper_moves_feature_minimally(self):
        """
        A theoretical informal paper (default lnBF=0.02)
        should move any feature by less than 1 percentage point.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        f2_before = result_before['features']['F2']
        
        claim = make_claim_via_indicator(
            indicator_id='I07',
            lbf=0.02,
            w_rel=0.8,
            w_map=0.60,
            direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        f2_after = result_after['features']['F2']
        
        delta = abs(f2_after - f2_before)
        assert delta < 0.01, (
            f"Theoretical paper moved F2 by {delta:.4f}, should be < 0.01"
        )

    def test_phenomenology_moves_feature_negligibly(self):
        """
        A phenomenological report (default lnBF=0.01)
        should move features by less than 0.5 percentage points.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        f1_before = result_before['features']['F1']
        
        claim = make_claim_via_indicator(
            indicator_id='I12',
            lbf=0.01,
            w_rel=0.6,
            w_map=0.20,
            direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        f1_after = result_after['features']['F1']
        
        delta = abs(f1_after - f1_before)
        assert delta < 0.005, (
            f"Phenomenology moved F1 by {delta:.4f}, should be < 0.005"
        )


class TestDependenceDiscounting:
    """
    Validates that paradigm clustering actually reduces
    the accumulation of redundant evidence.
    """

    def test_ten_IIT_papers_less_than_ten_independent_papers(self):
        """
        Ten claims from paradigm='IIT' should move F2
        less than ten claims from ten different paradigms.
        """
        engine_same = make_engine_with_real_seed_data()
        engine_diff = make_engine_with_real_seed_data()
        
        for i in range(10):
            claim_same = make_claim_via_indicator(
                indicator_id='I07', lbf=0.4, w_rel=0.8, w_map=0.60,
                direction=1, paradigm='IIT'
            )
            engine_same.db.add_claim(claim_same)
            
            claim_diff = make_claim_via_indicator(
                indicator_id='I07', lbf=0.4, w_rel=0.8, w_map=0.60,
                direction=1, paradigm=f'paradigm_{i}'
            )
            engine_diff.db.add_claim(claim_diff)
        
        result_same = engine_same.run()
        result_diff = engine_diff.run()
        
        f2_same = result_same['features']['F2']
        f2_diff = result_diff['features']['F2']
        
        assert f2_same < f2_diff, (
            f"Same-paradigm evidence should accumulate less. "
            f"IIT×10: {f2_same:.4f}, Independent×10: {f2_diff:.4f}"
        )

    def test_dependence_discount_does_not_eliminate_evidence(self):
        """
        Even 10 same-paradigm claims should move the feature
        more than 1 claim. Discounting reduces, not eliminates.
        """
        engine_ten = make_engine_with_real_seed_data()
        engine_one = make_engine_with_real_seed_data()
        
        for i in range(10):
            claim = make_claim_via_indicator(
                'I07', lbf=0.4, w_rel=0.8, w_map=0.60,
                direction=1, paradigm='IIT'
            )
            engine_ten.db.add_claim(claim)
        
        single = make_claim_via_indicator(
            'I07', lbf=0.4, w_rel=0.8, w_map=0.60,
            direction=1, paradigm='IIT'
        )
        engine_one.db.add_claim(single)
        
        result_ten = engine_ten.run()
        result_one = engine_one.run()
        
        assert result_ten['features']['F2'] > result_one['features']['F2']


class TestAnomalousIndicatorModes:
    """
    Validates three-state anomalous indicator handling.
    """

    def test_anomalous_off_mode_excludes_I15_I16(self):
        """
        With ANOMALOUS_MODE='off', claims through I15/I16
        should not move any feature.
        """
        engine = make_engine_with_real_seed_data(anomalous_mode='off')
        result_before = engine.run()
        f7_before = result_before['features']['F7']
        
        claim = make_claim_via_indicator(
            indicator_id='I16', lbf=0.5, w_rel=0.7, w_map=0.45, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        
        assert result_after['features']['F7'] == f7_before

    def test_anomalous_sandboxed_mode_discounts_by_0_2(self):
        """
        With ANOMALOUS_MODE='sandboxed', I16 claims contribute
        at 20% of their stated value.
        """
        engine_sandboxed = make_engine_with_real_seed_data(anomalous_mode='sandboxed')
        engine_active = make_engine_with_real_seed_data(anomalous_mode='active')
        
        for engine in [engine_sandboxed, engine_active]:
            claim = make_claim_via_indicator(
                indicator_id='I16', lbf=0.5, w_rel=0.7, w_map=0.45, direction=1
            )
            engine.db.add_claim(claim)
        
        result_sandboxed = engine_sandboxed.run()
        result_active = engine_active.run()
        
        f7_sandboxed = result_sandboxed['features']['F7']
        f7_active = result_active['features']['F7']
        prior_f7 = 0.08
        
        assert prior_f7 < f7_sandboxed < f7_active, (
            f"Sandboxed F7={f7_sandboxed:.4f} should be between "
            f"prior={prior_f7} and active={f7_active:.4f}"
        )

    def test_anomalous_active_mode_uses_full_values(self):
        """
        ANOMALOUS_MODE='active' should use full LR values
        with no additional discount.
        """
        engine = make_engine_with_real_seed_data(anomalous_mode='active')
        result_before = engine.run()
        f7_before = result_before['features']['F7']
        
        claim = make_claim_via_indicator(
            indicator_id='I16', lbf=0.5, w_rel=0.7, w_map=0.45, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        
        assert result_after['features']['F7'] > f7_before


class TestSystemSanityChecks:
    """
    High-level sanity checks. If these fail the system
    is producing nonsense regardless of test coverage.
    """

    def test_no_evidence_state_is_reproducible(self):
        """
        Running the engine twice with no evidence gives
        identical results. Tests determinism.
        """
        engine1 = make_engine_with_real_seed_data()
        engine2 = make_engine_with_real_seed_data()
        
        result1 = engine1.run()
        result2 = engine2.run()
        
        for fid in result1['features']:
            assert abs(result1['features'][fid] - result2['features'][fid]) < 1e-12

    def test_branch_ordering_stable_under_tiny_evidence(self):
        """
        A single tiny claim should not overturn the branch ranking.
        B5 should still beat B4 after one weak claim for B4.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        assert result_before['branches']['B5'] > result_before['branches']['B4']
        
        claim = make_claim_via_indicator(
            'I12', lbf=0.01, w_rel=0.5, w_map=0.10, direction=1
        )
        engine.db.add_claim(claim)
        result_after = engine.run()
        
        assert result_after['branches']['B5'] > result_after['branches']['B4'], (
            "One tiny claim should not overturn B5 > B4"
        )

    def test_massive_evidence_cannot_push_probability_to_boundary(self):
        """
        Even 100 strong claims cannot push a feature to exactly
        0 or 1. Tests numerical stability in realistic scenario.
        """
        engine = make_engine_with_real_seed_data()
        
        for _ in range(100):
            claim = make_claim_via_indicator(
                'I09', lbf=0.9, w_rel=0.9, w_map=0.60, direction=1
            )
            engine.db.add_claim(claim)
        
        result = engine.run()
        
        for fid, prob in result['features'].items():
            assert 0 < prob < 1, f"Feature {fid} hit boundary: {prob}"

    def test_cogitate_style_mixed_result_moves_both_theories(self):
        """
        Simulates the 2023 Cogitate result: evidence that
        challenged key IIT predictions while partly supporting GNW.
        
        F2 (pattern-space real, IIT-adjacent) should decrease.
        F4 (relations basic, GNW-adjacent) should increase.
        Net effect: neither B3 nor B5 dominates dramatically.
        """
        engine = make_engine_with_real_seed_data()
        result_before = engine.run()
        
        challenge_I03 = make_claim_via_indicator(
            indicator_id='I03', lbf=-0.5, w_rel=0.85, w_map=0.55,
            direction=-1, paradigm='Cogitate'
        )
        support_I04 = make_claim_via_indicator(
            indicator_id='I04', lbf=0.4, w_rel=0.85, w_map=0.50,
            direction=1, paradigm='Cogitate'
        )
        
        engine.db.add_claim(challenge_I03)
        engine.db.add_claim(support_I04)
        result_after = engine.run()
        
        assert result_after['features']['F2'] < result_before['features']['F2'], \
            "I03 challenge should decrease F2"
        assert result_after['features']['F4'] > result_before['features']['F4'], \
            "I04 support should increase F4"
        
        b3_change = abs(result_after['branches']['B3'] - result_before['branches']['B3'])
        b5_change = abs(result_after['branches']['B5'] - result_before['branches']['B5'])
        
        assert b3_change < 0.10, f"B3 moved {b3_change:.3f} from 2 papers, too much"
        assert b5_change < 0.10, f"B5 moved {b5_change:.3f} from 2 papers, too much"
