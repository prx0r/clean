# Codex Truth Map Conclusions

This file records the design decisions for discriminator calibration, feature propagation, and claim extraction. The full matrix and implementation details live in `TRUTHMAP-REDESIGN.md`.

---

## 1. Branch Effect Multipliers

The branch-effect matrix is now fixed as a calibrated v1 design:

- 5 discriminators
- 2 answers per discriminator
- 6 branches
- 60 total multipliers

The values use five bands:

| Band | Range | Meaning |
|------|-------|---------|
| Near-mask elimination | 0.05-0.15 | Answer defeats a core branch commitment |
| Severe penalty | 0.20-0.35 | Branch survives only by major reinterpretation |
| Strain | 0.45-0.80 | Branch remains live but loses explanatory fit |
| Neutral-compatible | 0.85-1.05 | Answer is compatible or weakly relevant |
| Survivor boost | 1.10-1.50 | Answer directly supports the branch |

Important correction: "mask-like" does not mean setting a branch to zero. Use a small floor unless a formal contradiction is proven. This keeps eliminated branches auditable and allows later evidence to show that a discriminator was misclassified.

Scientific calibration principle:

- D1 is anchored in physical supervenience, physical closure, information theory, and substrate-dependence.
- D2 is anchored in causal emergence, interventionist causal models, and IIT-style cause-effect power.
- D3 is anchored in intrinsicality, illusionism, report/no-report paradigms, split-brain/anesthesia, and perturbational complexity.
- D4 is anchored in positive geometry/amplituhedron, holography, quantum gravity, and mathematical truthmaking.
- D5 is anchored in substrate discontinuity, split-brain/dissociation, IIT exclusion, and high-confound cross-life continuity evidence.

The amplituhedron does not prove consciousness-first metaphysics. It weakens naive spacetime-local physical realism and supports structural readings; B2 survives if it becomes structural physicalism.

---

## 2. Feature-to-Discriminator Mapping

Use a fixed v1 mapping table, not a learned mapping.

Reason: the mapping encodes the meaning of the ontology. A learned system may later correct calibration residuals, but it should not silently decide that a feature means something else.

Derived update rule:

```text
effective_claim_lbf = log_bayes_factor * w_rel * w_map * w_aux * w_dep
derived_discriminator_lbf =
  clamp(effective_claim_lbf * mapping_weight * polarity, -0.6, 0.6)
```

Rules:

- Direct discriminator targets win over derived feature targets.
- Derived discriminator updates must be tagged `evidence_role = "derived_mapping"`.
- Avoid double-counting: one claim should not update the same discriminator both directly and by derived mapping unless manually approved.
- Learning can start after 100+ reviewed packets and should produce suggested corrections, not overwrite the fixed mapping.

---

## 3. Claim Extraction Prompt

The extraction prompt should be conservative by design.

Required behavior:

- If the paper is unrelated to D1-D5/F1-F8, return `paper_relevance = "unrelated"` and no claims.
- If the paper is background-useful but not a direct truth-map test, return `paper_relevance = "auxiliary"` and either no claims or weak feature-only claims.
- Direct D1-D5 targets are allowed only when the paper directly bears on the discriminator's binary form.
- Abstract-only extraction must cap absolute log Bayes factors unless the abstract states a formal theorem or direct empirical result.
- The reasoning field must include target fit, limits/confounds, and why the weight is not stronger.

Weight caps:

| Relation to truth map | LBF cap |
|-----------------------|---------|
| Direct discriminator test | ±1.2 from abstract; higher only after full-text review |
| Direct feature evidence | ±0.8 |
| Indirect/auxiliary evidence | ±0.35 |
| Pure analogy or speculative discussion | ±0.15 |
| Unrelated | no claim |

---

## 4. Expected Information Gain

The decision tree is a default ordering, not a hard policy. The next discriminator should be selected by expected information gain.

Current branch entropy:

```text
H(B) = -sum_b P(b) * log2(P(b))
```

For each candidate discriminator `D`:

```text
P_yes = discriminator.posterior_yes
P_no = 1 - P_yes

B_yes = normalize(P(B) * effect(D=yes, B))
B_no  = normalize(P(B) * effect(D=no, B))

EIG(D) =
  H(P(B))
  - (P_yes * H(B_yes) + P_no * H(B_no))
```

Tie-breakers:

1. lower evidence cost
2. stronger falsifier
3. more independent evidence clusters
4. less semantic ambiguity
5. higher branch split balance

This lets the system ask the most eliminative available question rather than blindly following D1 -> D2/D3.

---

## 5. Implementation Order

1. Add discriminator tables and branch-effect seed data.
2. Add claim target mapping with per-target weights.
3. Implement branch support as discriminator effects times existing feature projection.
4. Add tests that D1-D5 answers move branches in the expected directions.
5. Run extraction on a small paper set and review every packet before ingestion.
