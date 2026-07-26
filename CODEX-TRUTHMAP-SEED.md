# Codex — Truth Map Take the Lead

You're the smartest agent on this project. I need you to master the truth map and take ownership of the D1-D5 discrimination cascade implementation. Below is everything you need.

---

## Quick Start

Read these files in order, then dive into the papers:

1. `/root/projects/clean/tractatus-conscientiae.md` — Level 0: `S => (0 <-> 1)`, 6 branches B1-B6
2. `/root/projects/clean/TRUTHMAP-REDESIGN.md` — Current D1-D5 cascade design (574 lines, THE spec)
3. `/root/projects/clean/CODEX-TRUTHMAP.md` — Prior Codex design decisions
4. `/root/projects/clean/truthengine-propagation.py` — Bayesian math core (304 lines)
5. `/root/projects/clean/truthengine_working.py` — SQLite runtime (654 lines)
6. `/root/projects/clean/test_truthengine_working.py` — 6 passing tests
7. `/root/projects/clean/EVIDENCE-PIPELINE.md` — Paper → Packet → Truth Map pipeline
8. `/root/projects/clean/specs/CLAIM.md` — Claim evidence spec
9. `/root/projects/clean/specs/TRUTH-MAP-QUESTION.md` — Schema reconciliation (3 models)
10. `/root/projects/clean/TRUTHMAP-PROGRESS.md` — Full status, doc ratings, gaps
11. `/root/projects/clean/REDTEAM-TRUTHMAP.md` — Attack vectors to break the engine
12. `/root/projects/clean/BUILD-NOTES.md` — Pipeline evolution, lessons learned

---

## Your Mission: D1-D5 Discriminator Cascade

The propagation engine currently tracks 8 features (F1-F8) and derives branch probabilities from them. The redesign (TRUTHMAP-REDESIGN.md) adds a **discrimination cascade** layer above F1-F8:

```
D1. Physical supervenience of info/observer?
  YES → D2. Irreducible macro causation?
    NO  → B2 Physical Realism
    YES → B5 Process Metaphysics
  NO  → D3. Intrinsic phenomenality of S?
    YES → B4 Nondual Consciousness-First
    NO  → D4. Pattern space ontologically real?
      NO  → B1 Thin Formalism
      YES → D5. Substrate-discontinuous identity?
        NO  → B3 Platonic/Computational
        YES → B6 Cross-Life Continuity
```

### What Needs Building (in order)

1. **Discriminator tables in SQLite** — `discriminators` table, `discriminator_branch_effects` table, `claim_targets` table extension (schema defined in TRUTHMAP-REDESIGN.md lines 520-555)
2. **branch_support()** — New computation combining discriminator effects with existing feature projection (lines 420-438)
3. **EIG-based question selection** — Expected Information Gain to pick the next discriminator (lines 442-458)
4. **Feature-to-Discriminator mapping** — Fixed v1 table with derived update rule (lines 341-386)
5. **Claim target extension** — Allow claims to target both F1-F8 and D1-D5 (lines 395-411)
6. **60-cell branch-effect matrix** — Seed the multiplier data (lines 282-304)
7. **Tests** — D1 YES pushes B2 above B4, D1 NO pushes B2 down, D3 YES separates B4, D5 YES separates B6 from B3

### Current Engine Architecture

```
truthengine-propagation.py:  PropagationEngine.run()
  ├── full_recompute()  — reset all features, apply all claims
  └── incremental()     — apply only new claims
      ├── FeatureState.update(weighted_lbf)
      ├── compute_dep_weight(n_prior)  — paradigm crowding discount
      └── derive_branch_probs()  — feature posteriors → branch distribution
```

The D1-D5 layer needs to wrap this:

```
run()
  ├── propagate claims (existing engine)  → updates F1-F8 + D1-D5
  └── derive_branch_support()  ← NEW
      ├── expected_branch_effect(D, B) = P(yes)*effect(yes) + P(no)*effect(no)
      └── branch_support = normalize(prior * discriminator_effects * feature_projection)
```

---

## Arxiv Papers — Become the Expert

These papers are the scientific anchors for each discriminator. Read them to calibrate your understanding of what evidence looks like:

### D1 — Physical Supervenience (Information, Observer Identity)
- **Landauer principle**: `https://arxiv.org/abs/1405.5563` — Deutsch & Marletto, Constructor Theory of Information. What does it mean for information to be physical?
- **Quantum information / black holes**: `https://arxiv.org/abs/1312.2007` — Arkani-Hamed & Trnka, The Amplituhedron. Locality/unitarity as emergent, not fundamental.
- **Physical closure**: `https://arxiv.org/abs/quant-ph/0104033` — Deutsch, It from Qubit.

### D2 — Irreducible Macro/Process Causation
- **Causal emergence**: Tononi — `https://pubmed.ncbi.nlm.nih.gov/24811198/` — IIT 3.0 (Oizumi, Albantakis & Tononi, PLOS Comp Bio 2014). Integrated Information Theory — macro cause-effect power.
- **Downward causation**: `https://arxiv.org/abs/2001.07203` — Da Costa et al., Active Inference on Discrete State-Spaces. Agency at multiple scales.
- **IIT 4.0**: `https://doi.org/10.1371/journal.pcbi.1011465` — Tononi et al., IIT 4.0 (2023). Updated axioms, exclusion, intrinsicality.

### D3 — Intrinsic Phenomenality of S
- **IIT intrinsicality**: `https://www.iit.wiki/axioms-and-postulates/exclusion` — Intrinsicality axiom, exclusion postulate.
- **Report/no-report paradigms**: `https://doi.org/10.1038/s41586-025-08888-1` — Cogitate Consortium, Adversarial Test of IIT vs GNWT (Nature 2025). This is the key adversarial experiment.
- **Illusionism vs intrinsicality**: `https://arxiv.org/abs/2305.02205` — Ramstead et al., The Inner Screen Model of Consciousness (2023).
- **Minimal phenomenal experience**: Metzinger (2020) — `https://doi.org/10.33735/phimisci.2020.I.46` — MPE framework.

### D4 — Ontological Status of Pattern Space
- **Amplituhedron**: `https://arxiv.org/abs/1312.2007` — Arkani-Hamed & Trnka (2013). The central result for D4.
- **Constructor theory**: `https://arxiv.org/abs/1210.7439` — Deutsch, Constructor Theory (2013). Possible/impossible transformations as primitive.
- **Ruliad / computational universe**: `https://arxiv.org/abs/1906.10184` — Friston, A Free Energy Principle for a Particular Physics. Physics from information geometry.

### D5 — Substrate-Discontinuous Observer Identity
- **Split-brain / dissociation**: IIT exclusion predicts definite borders — `https://pubmed.ncbi.nlm.nih.gov/24811198/` — IIT 3.0 exclusion test.
- **Cross-life continuity / reincarnation evidence**: `https://arxiv.org/abs/2409.14545` — Bennett, Welsh & Ciaunica, Why Is Anything Conscious? (2024). Minimal approach to identity.
- **Upload / gradual replacement**: `https://arxiv.org/abs/2410.06633` — Whyte et al., On the Minimal Theory of Consciousness Implicit in Active Inference (2024).

### Frameworks & Algorithms
- **Bayesian belief updating**: The core math is already in `truthengine-propagation.py`. Read for understanding: log-odds, sigmoid, evidence accumulation.
- **Expected Information Gain (EIG)**: Shannon entropy reduction. Formula in TRUTHMAP-REDESIGN.md lines 442-458. Reference: Cover & Thomas, *Elements of Information Theory*.
- **Paradigm dependence discounting**: `compute_dep_weight(n_prior, alpha=0.5)` in `truthengine-propagation.py` line 33. Crowding correction for same-paradigm evidence.
- **Popperian falsification / Deutsch hard-to-vary**: `truthengine.md` lines on explanatory quality vs mere probability.
- **Append-only evidence log**: Blockchain-style immutability. Described in `magnum-opus/25-ARCHITECTURE.md` lines 152-171.

### Contemplative Neuroscience (for D3 context)
- Laukkonen & Slagter — "From Many to (n)One" (2021): `https://doi.org/10.1016/j.neubiorev.2021.06.021`
- Josipovic — "Nondual Awareness" (2019): `https://doi.org/10.1016/j.pneurobio.2019.101717`
- Atad et al. — "Meditation and Complexity" (2025): `https://doi.org/10.1093/nc/niaf013`
- Sandved-Smith et al. — "Deep Computational Neurophenomenology" (2025): `https://doi.org/10.1093/nc/niaf016`
- Ward et al. — "Modeling Non-Dual Awareness via Constraint Closure" (2026): `https://doi.org/10.1093/nc/niaf068`

---

## Implementation Roadmap

### Sprint 1: Discriminator Schema + Seed Data
1. Add `discriminators` table to `truthengine_working.py` (schema from TRUTHMAP-REDESIGN.md lines 520-555)
2. Add `discriminator_branch_effects` table with 60-cell matrix (lines 282-304)
3. Add `claim_targets` table extension
4. Seed D1-D5 with prior odds 0.5 (undecided)
5. Test: `test_discriminator_table_created()`, `test_seed_effects_count_60()`

### Sprint 2: Branch Support Computation
1. Implement `expected_branch_effect(D, B)` — probability-weighted average of yes/no multipliers
2. Implement `derive_branch_support()` combining discriminator effects + feature projection
3. Replace existing `derive_branch_probs()` call with `derive_branch_support()`
4. Test: D1=YES pushes B2 above B4. D1=NO pushes B2 down.
5. Test: Non-terminal discriminators leave branches alive (no hard zero).

### Sprint 3: Claim Target Extension
1. Allow claims to target discriminator IDs (D1-D5) in addition to feature IDs (F1-F8)
2. Implement derived discriminator update from feature claims (mapping table, clamp ±0.6)
3. Test: feature claim with mapping weight correctly nudges discriminator posterior
4. Test: direct discriminator claim overrides derived mapping

### Sprint 4: EIG Selection + Red Team
1. Implement expected information gain for discriminator selection
2. Add staleness tracking (90-day expiry)
3. Run REDTEAM-TRUTHMAP.md attack vectors
4. Fix `truthengine-test-validation.py` and `truthengine-test-validation-v2.py` (broken imports)

---

## Task Queue (Priority Order)

1. **P0**: Add discriminator tables + seed data to `truthengine_working.py`
2. **P0**: Implement `branch_support()` combining discriminator effects + feature projection
3. **P0**: Align 3 conflicting schemas per `specs/TRUTH-MAP-QUESTION.md`
4. **P1**: Extend claim targeting to support discriminators
5. **P1**: Add EIG-based next-question selection
6. **P1**: Fix broken test files (`truthengine-test-validation.py`, `truthengine-test-validation-v2.py`)
7. **P1**: Write red-team tests for D1-D5
8. **P2**: Expand from 6 to 72 truth map questions
9. **P2**: Create one manual EO to validate the architecture

---

## Key Constraints

- **Do not modify `truthengine-propagation.py`** unless fixing a confirmed bug. It's the math reference.
- **All D1-D5 code goes in `truthengine_working.py`** (the SQLite runtime) or a new `truthengine_cascade.py`.
- **The 3 schema models** (`q-*.json` files, `ClaimRecord`, magnum-opus spec) must be reconciled before adding new questions.
- **Append-only evidence log** — edits not allowed, only new evidence records with supersede links.
- **No hard zero on branches** — even eliminated branches stay at audit-visible floor (0.05).
- **Run existing tests before/after**: `PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest test_truthengine_working -v`
- **Commit after each sprint** with descriptive messages.
