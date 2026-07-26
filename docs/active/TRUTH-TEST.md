# Truth Engine — Test Protocol

## Philosophy

The engine should pass two kinds of tests:

1. **Known-truth tests** — claims where we know the right answer (amplituhedron → D4 should move). If the engine gets these wrong, something is broken.
2. **Adversarial tests** — pathological inputs designed to break the engine. Edge cases, nonsense claims, conflicting paradigms. The engine should handle these gracefully (not crash, not produce false convergence, not return NaN).

Tests are structured as self-contained Python methods in `test_truthengine_working.py`. Each test is independent — no shared state. Add new tests by writing a method starting with `test_`.

---

## Tests to Run Now (Existing)

```bash
cd /root/projects/clean
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest test_truthengine_working -v
```

Current: 12 tests, all passing.

---

## Tests to Add (Priority)

### P0 — Gate Validation Tests

These test the Nyāya gate directly. Create as `test_nyaya_gate.py`:

```python
# test_nyaya_gate.py

def test_gate_accepts_valid_empirical_claim():
    """A well-formed empirical claim should pass the gate."""
    claim = {
        "claim_text": "fMRI shows DMN decoupling during nondual states",
        "pramana": "pratyaksa",
        "tradition": "neuroscience",
        "falsifier": "If nondual states show no consistent neural signature, this is weakened"
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert result.passed == True
    assert len(result.failures) == 0

def test_gate_rejects_savyabhicara():
    """A claim with known counterexamples should be flagged as inconsistent."""
    claim = {
        "claim_text": "Meditation always produces nondual awareness → meditation proves consciousness is fundamental",
        # savyabhicara: meditation doesn't ALWAYS produce nondual awareness
        "pramana": "anumana",
        "tradition": "contemplative"
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert "savyabhicara" in result.failures

def test_gate_rejects_badhita():
    """A claim contradicted by stronger evidence should be flagged."""
    claim = {
        "claim_text": "Consciousness has no neural correlates → the brain is irrelevant to consciousness",
        # badhita: 50+ years of neuroscience contradicts this
        "pramana": "anumana",
        "tradition": "idealism"
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert "badhita" in result.failures

def test_gate_accepts_textual_claim():
    """A faithful textual report should pass even if the claim itself is questionable."""
    claim = {
        "claim_text": "Plotinus says the body is in the soul, not the soul in the body",
        "pramana": "sabda",
        "tradition": "neoplatonic",
        "claim_type": "faithful_report"  # NOT an evidence assertion
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert result.passed == True
    # Should warn if used as evidence, not if reported faithfully

def test_gate_requires_falsifier():
    """A claim without a falsifier should get a warning."""
    claim = {
        "claim_text": "Consciousness is fundamental",
        "pramana": "sabda",
        "tradition": "trika",
        # no falsifier
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert "missing_falsifier" in result.warnings

def test_gate_requires_tradition_scope():
    """A claim without tradition scope should be flagged."""
    claim = {
        "claim_text": "The self is an illusion",
        "pramana": "anumana",
        # no tradition
    }
    result = nyaya_truthmap_gate.validate(claim)
    assert "missing_tradition" in result.warnings
```

### P0 — Known-Truth Propagation Tests

These test that the engine moves in the right direction for claims we understand:

```python
# Add to test_truthengine_working.py

def test_amplituhedron_moves_d4_toward_yes():
    """The amplituhedron paper shows locality/unitarity emerge from positive geometry.
    This should move D4 (pattern space truthmaking) toward YES."""
    c = claim("cl:test-amplituhedron-d4", ["D4"], 0.6, "hep_physics")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    before = engine.run()
    db.add_claim(c)
    after = engine.run(new_claim_ids=[c.id])
    assert after["discriminators"]["D4"] > before["discriminators"]["D4"]

def test_iit_supports_d3_intrinsic_phenomenality():
    """IIT's intrinsicality axiom bears on D3 (intrinsic phenomenality).
    It should move D3 toward YES."""
    c = claim("cl:test-iit-d3", ["D3"], 0.5, "iit")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    before = engine.run()
    db.add_claim(c)
    after = engine.run(new_claim_ids=[c.id])
    assert after["discriminators"]["D3"] > before["discriminators"]["D3"]

def test_brain_damage_moves_d3_toward_no():
    """Brain damage systematically altering consciousness bears on D3.
    If D3 asks 'is phenomenality intrinsic?', brain dependence pressures NO."""
    c = claim("cl:test-brain-damage-d3", ["D3"], -0.5, "neuroscience")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    before = engine.run()
    db.add_claim(c)
    after = engine.run(new_claim_ids=[c.id])
    assert after["discriminators"]["D3"] < before["discriminators"]["D3"]

def test_opposing_claims_produce_low_convergence():
    """Two claims from different traditions pointing opposite ways should produce low convergence."""
    trika = claim("cl:test-trika-f1", ["F1"], 0.8, "trika")
    neuro = claim("cl:test-neuro-f1", ["F1"], -0.6, "neuroscience")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(trika)
    db.add_claim(neuro)
    result = engine.run(new_claim_ids=[trika.id, neuro.id])
    # Dimensions should diverge
    convergence = compute_convergence({
        "phenomenological": result["dimension_features"]["F1"]["phenomenological"],
        "empirical": result["dimension_features"]["F1"]["empirical"]
    })
    assert convergence < 0.5  # low convergence = disagreement
```

### P1 — Dimension Tracking Tests

```python
def test_dimension_specific_paradigm_crowding():
    """Trika claims should NOT crowd neuroscience claims in the same dimension track."""
    trika_claim = claim("cl:test-trika-crowd", ["F1"], 0.5, "trika",
                        evidence_dimension="phenomenological")
    neuro_claim = claim("cl:test-neuro-crowd", ["F1"], 0.5, "neuroscience",
                        evidence_dimension="empirical")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(trika_claim)
    r1 = engine.run(new_claim_ids=[trika_claim.id])
    db.add_claim(neuro_claim)
    r2 = engine.run(new_claim_ids=[neuro_claim.id])
    # Both claims should have w_dep=1.0 because they're in different dimensions
    # (even though they target the same feature)

def test_trika_and_neuro_claim_same_dimension_dep_discount():
    """Two claims from same tradition AND same dimension DO get crowding discount."""
    c1 = claim("cl:test-trika-1", ["F1"], 0.5, "trika",
               evidence_dimension="phenomenological")
    c2 = claim("cl:test-trika-2", ["F1"], 0.5, "trika",
               evidence_dimension="phenomenological")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(c1)
    r1 = engine.run(new_claim_ids=[c1.id])
    db.add_claim(c2)
    r2 = engine.run(new_claim_ids=[c2.id])
    # Second claim should have w_dep < 1.0 (crowding discount applied)
    # The posterior should move less than if it were a new paradigm
```

### P1 — Adversarial Tests

```python
def test_extreme_lbf_does_not_overflow():
    """A log_bayes_factor of 1000 should not produce NaN."""
    c = claim("cl:test-extreme", ["F1"], 1000.0, "test")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(c)
    result = engine.run(new_claim_ids=[c.id])
    assert not math.isnan(result["features"]["F1"])
    assert result["features"]["F1"] < 1.0  # clamped by sigmoid

def test_zero_weights_do_not_crash():
    """All weights being zero should not crash the engine."""
    c = ClaimRecord(
        id="cl:test-zero-weights",
        target_feature_ids=["F1"],
        log_bayes_factor=0.5,
        w_rel=0.0, w_map=0.0, w_aux=0.0,
        paradigm="test"
    )
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(c)
    result = engine.run(new_claim_ids=[c.id])
    assert result["features"]["F1"] == 0.40  # should equal prior

def test_nonexistent_target_does_not_crash():
    """A claim targeting a feature that doesn't exist should not crash the engine."""
    c = ClaimRecord(
        id="cl:test-nonexistent",
        target_feature_ids=["F99"],  # F99 doesn't exist
        log_bayes_factor=0.5,
        w_rel=1.0, w_map=1.0, w_aux=1.0,
        paradigm="test"
    )
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    db.add_claim(c)
    result = engine.run(new_claim_ids=[c.id])
    assert result["features"]["F1"] == 0.40  # unchanged

def test_conflicting_identical_paradigm_cluster_does_not_falsely_converge():
    """10 claims from the same paradigm should NOT converge to high confidence.
    The dependence discount should keep the posterior low."""
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    engine.run()
    for i in range(10):
        c = claim(f"cl:test-paradigm-{i}", ["F1"], 0.8, "same_paradigm")
        db.add_claim(c)
        engine.run(new_claim_ids=[c.id])
    result = engine.run()
    # 10 claims from one paradigm should be heavily discounted
    assert result["features"]["F1"] < 0.60  # well below what 10 undiscounted claims would produce
```

### P2 — End-to-End Pipeline Test

```python
def test_full_pipeline_paper_to_truth_map():
    """Simulate the full pipeline: paper → extract → gate → ingest → verify."""
    # 1. Paper text
    paper_text = "The amplituhedron shows that locality and unitarity are emergent properties of scattering amplitudes..."

    # 2. Extract claims (simulated)
    claims = extract_claims_from_text(paper_text)  # or load from test-amplituhedron.json

    # 3. Gate each claim
    for claim in claims:
        gate_result = nyaya_truthmap_gate.validate(claim)
        assert gate_result.passed, f"Claim {claim['claim_id']} failed gate: {gate_result.failures}"

    # 4. Ingest into engine
    db = build_truth_map_db(seed_claims=True)
    engine = PropagationEngine(db)
    before = engine.run()
    for claim in claims:
        db.add_claim_dict(claim)
    after = engine.run()

    # 5. Verify: D4 moved toward YES (pattern space truthmaking)
    assert after["discriminators"]["D4"] > before["discriminators"]["D4"]

    # 6. Verify: provenance report shows this paper
    report = generate_provenance_report(source_id="arxiv:1312.2007")
    assert len(report["claims"]) > 0
    assert report["total_evidence_power"] > 0

def test_provenance_blame_is_correct():
    """When we ingest a claim, the provenance report should correctly attribute it."""
    c = claim("cl:test-blame", ["F1"], 0.5, "test", question_id="q:consciousness-fundamental")
    db = build_truth_map_db(seed_claims=False)
    engine = PropagationEngine(db)
    before = engine.run()
    db.add_claim(c)
    after = engine.run(new_claim_ids=[c.id])
    # The provenance report for this claim should show the effective lbf, w_dep, etc.
    report = generate_provenance_report(claim_id="cl:test-blame")
    assert report["effective_lbf"] == 0.5 * 1.0 * 1.0 * 1.0 * 1.0  # all weights = 1.0
    assert report["posterior_delta"] == after["features"]["F1"] - before["features"]["F1"]
```

---

## Review Checklist (For Codex)

After running the test suite, answer:

1. **Does the engine pass all existing tests?** If not, what changed?
2. **Do the new P0 tests pass?** (gate validation, known-truth propagation)
3. **Are there any edge cases not covered?** (the REDTEAM-TRUTHMAP.md attack vectors are a good source)
4. **Does the engine produce plausible results for opposing claims?** (low convergence on known disagreements)
5. **Does the gate distinguish between faithful source reporting and evidence assertion?** (critical for ROs)
6. **Are the dimension tracks independent?** (Trika phenomenology ≠ neuroscience empirical)
7. **Does the convergence metric behave as expected?** (high for aligned claims, low for opposing)

If any of these fail, fix the engine AND add a test that would catch the same failure in the future.

---

## Codex Instructions

Read this file. Then:

1. Run existing tests: `PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest test_truthengine_working -v`
2. Create `test_nyaya_gate.py` with the gate validation tests above
3. Add the known-truth propagation tests to `test_truthengine_working.py`
4. Add the adversarial tests
5. Run the full suite
6. For any test that fails: decide whether to fix the engine or adjust the test expectation
7. Add any NEW tests you discover during this process (edge cases you find)
8. Report back: which tests passed, which failed, what you fixed, what new tests you added
