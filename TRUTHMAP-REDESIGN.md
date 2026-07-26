# Truth Map Redesign — Discrimination Cascade

The current F1-F8 engine is useful, but it is not the top of the truth map. It tracks support over features and then projects those features into branch support. That is a Bayesian evidence engine, not a question-selection strategy.

The top layer should be an **epistemic discrimination spine** constrained by the Tractatus Level 0 formalism:

```text
Level 0: S => (0 <-> 1)
  S is the enabling condition for observer/object polarity.
  Level 0 does not say what S is.

Interpretation layer:
  B1-B6 are candidate fillings or operational readings of S.

Discrimination cascade:
  Ask binary questions whose answers eliminate or heavily penalize branches.

Propagation layer:
  Claims, falsifiers, weights, and posteriors decide whether a discriminator
  has enough support to count as answered.
```

This means the top layer is neither a finished metaphysics nor a loose epistemology. It is an **epistemology for selecting metaphysical branch tests**. It asks: which empirical or formal result would most efficiently discriminate between possible occupants of `S`?

---

## 1. Design Principles

### P1. Top questions must be eliminative

A top-level question is valid only if a yes/no answer changes the live branch set. "Is consciousness fundamental?" is not a good top question because branches can reinterpret the word "fundamental." It belongs lower in the cascade after the relevant sense of fundamentality has been fixed.

### P2. Binary does not mean simplistic

Each question must define the binary in operational terms. The question is not "is spacetime fundamental?" in a vague sense. It is "do locality and unitarity appear as derived constraints from a non-spatiotemporal mathematical object in the empirically successful formulation of scattering physics?"

### P3. Evidence must be falsifiable or formally decisive

Top-level nodes can be answered by:

- direct experiment
- formal theorem
- no-go theorem
- robust empirical dissociation
- operational measure that survives adversarial replication

Pure metaphysical preference is not allowed at the top level.

### P4. The goal is branch pruning, not premature convergence

The system should not force one surviving branch unless the evidence actually does that. It should maintain multiple live branches with relative support. Convergence is an asymptotic outcome, not a UI requirement.

### P5. Branch penalties are stronger than feature nudges

A discriminator answer applies a structured branch penalty or survival boost. Ordinary claims still update F1-F8. Discriminator claims update both:

```text
claim -> feature posterior update
claim -> discriminator posterior update
discriminator posterior -> branch mask/penalty
branch support = branch_prior * discriminator_likelihoods * feature_projection
```

---

## 2. Branch Commitments

| Branch | S = | Core vulnerability |
|--------|-----|--------------------|
| B1 Thin Formalism | Minimal formal condition itself | Dies if concrete causal/semantic/phenomenal powers are irreducible to formal structure |
| B2 Physical Realism | Nomological physical reality | Dies or weakens if physical closure, spacetime locality, or microphysical sufficiency fails |
| B3 Platonic/Computational | Mathematical pattern space / Ruliad | Dies or weakens if information fully supervenes on physical implementation |
| B4 Nondual Consciousness-First | Pure awareness / reflexive manifestness | Dies or weakens if consciousness is fully explained by non-conscious physical organization |
| B5 Process Metaphysics | Relational becoming / process | Dies or weakens if process adds no causal structure beyond static state laws |
| B6 Cross-Life Continuity | Trans-instantiation pattern carrier | Dies or weakens if identity cannot persist across substrate discontinuity |

---

## 3. Minimum Cascade

The theoretical minimum for six branches is `ceil(log2(6)) = 3` binary answers, but only if every question splits the live branch set cleanly. Real scientific discriminators do not behave that cleanly. The practical minimum is a **five-question decision tree**, with expected depth 3-4 and worst-case depth 4.

### Tree View

```text
D1. Does information/observer identity fully supervene on physical causal structure?
  YES -> D2
  NO  -> D3

D2. Are macro/process causal powers irreducible to microphysical dynamics?
  NO  -> B2 Physical Realism
  YES -> B5 Process Metaphysics

D3. Is the enabling condition intrinsically phenomenal/reflexive?
  YES -> B4 Nondual Consciousness-First
  NO  -> D4

D4. Is mathematical/pattern structure ontologically real beyond thin formal constraint?
  NO  -> B1 Thin Formalism
  YES -> D5

D5. Can observer identity persist across substrate discontinuity?
  NO  -> B3 Platonic/Computational
  YES -> B6 Cross-Life Continuity
```

This tree is not the only possible ordering. It is the best default because D1 cuts the largest and most scientifically tractable fault line first: physical supervenience.

---

## 4. Discriminator Specifications

### D1 — Physical Supervenience of Information and Observer Identity

**Binary form:** Does every fact about information content, semantic reference, and observer identity supervene on the complete physical causal state and its lawful evolution?

**YES penalizes:** B1, B3, B4, B6.
**NO penalizes:** B2.

**Branches mostly spared:** B5 can survive either answer if "physical" is process-relational rather than substance-like, but it is pushed toward D2.

**Falsifiable science/formal work:**

- Landauer-style physical constraints on information processing.
- Quantum information and black-hole information arguments.
- Reference-frame and semantic information work: whether meaning is observer-relative or fully specified physically.
- Robust failure of substrate-independent computation would support YES.
- Demonstration of non-physical semantic/information facts with causal consequences would support NO.

**Answered threshold:** posterior >= 0.85 for YES or <= 0.15 for NO, with at least 3 independent evidence clusters.

**Why this is top:** It separates physical realism from almost every non-physical or non-reductive filling of `S`.

---

### D2 — Irreducible Macro/Process Causal Power

**Binary form:** Are there macro-scale or process-level causal powers that are not merely compressed descriptions of microphysical transition dynamics?

**YES penalizes:** B2.
**NO penalizes:** B5.

**Branches mostly spared:** B1/B3 may reinterpret macro causes as formal compression; B4 may treat them as appearances within consciousness.

**Falsifiable science/formal work:**

- Causal emergence results where macro effective information exceeds micro effective information.
- Interventionist causal models comparing micro and macro controllability.
- IIT-style cause-effect power, especially if maximal causal grains are empirically identifiable.
- Downward causation experiments that survive intervention and coarse-graining objections.

**Answered threshold:** posterior >= 0.80 or <= 0.20, plus a coherence check showing the result is not merely epistemic compression.

**Role:** Distinguishes physical realism from process metaphysics after physical supervenience has survived D1.

---

### D3 — Intrinsic Phenomenality of S

**Binary form:** Must the enabling condition for observer/object polarity include intrinsic phenomenal or reflexive manifestness, rather than only third-person structure?

**YES penalizes:** B1, B2, B3, B5.
**NO penalizes:** B4.

**Branches mostly spared:** B6 remains conditional because cross-life continuity could be a pattern-carrier thesis without ultimate consciousness-first ontology.

**Falsifiable science/formal work:**

- Strong evidence that phenomenal consciousness is identical to measurable intrinsic cause-effect structure would weaken B4 unless it still requires intrinsic manifestness.
- Successful illusionist or functional explanation of phenomenal reports without leftover explanatory gap supports NO.
- Stable first-person/third-person bridging laws that require irreducible intrinsicality support YES.
- Split-brain, anesthesia, perturbational complexity, and report/no-report paradigms constrain the substrate claims.

**Answered threshold:** posterior >= 0.90 or <= 0.10, because this node carries high metaphysical load and is vulnerable to verbal equivocation.

**Role:** This replaces the vague question "is consciousness fundamental?" with the sharper issue: is phenomenality built into `S`, or generated/represented downstream?

---

### D4 — Ontological Status of Pattern Space

**Binary form:** Do mathematical or computational patterns have truth-making status independent of any particular physical instantiation or observer convention?

**YES penalizes:** B1, B2.
**NO penalizes:** B3 and B6.

**Branches mostly spared:** B4 can absorb mathematical structure as appearance within consciousness; B5 can absorb it as stable process pattern.

**Falsifiable science/formal work:**

- Amplituhedron/positive geometry style results where locality and unitarity emerge from non-spatiotemporal mathematical structure.
- Universal computation/Ruliad-style derivations that recover physical law without arbitrary fitting.
- No-go results showing multiple incompatible mathematical structures fit the same physics equally well support NO.
- Evidence that information is inseparable from physical implementation supports NO.

**Answered threshold:** posterior >= 0.85 or <= 0.15, with source diversity across physics, computation, and philosophy of mathematics.

**Amplituhedron mapping:** A strong amplituhedron-style result does **not** prove B4. It primarily weakens naive B2 if spacetime locality is treated as fundamental, and strengthens B1/B3-style structural readings. It may also strengthen B5 if the replacement is process-geometric rather than timeless Platonism. It only kills B2 if B2 is defined as fundamental spacetime localism. A modern physical realist can survive by moving to structural physicalism.

---

### D5 — Substrate-Discontinuous Observer Identity

**Binary form:** Can the identity-relevant organization of an observer persist across destruction, replacement, or discontinuity of the original biological substrate?

**YES penalizes:** B2 and weakens B4 if B4 requires a single universal subject rather than transmissible pattern. It strongly supports B6.
**NO penalizes:** B6.

**Branches mostly spared:** B3 can allow abstract pattern identity without personal continuity; B1 can remain agnostic.

**Falsifiable science/formal work:**

- Upload/gradual replacement thought experiments become operational only if implemented systems preserve memory, agency, and report continuity.
- Empirical evidence for cross-life memory or identity continuity would support YES only if fraud, cryptomnesia, and ordinary transmission are eliminated.
- Split-brain and dissociation cases constrain whether one substrate can host multiple subject streams.
- IIT exclusion predicts definite borders for a conscious substrate; strong confirmation penalizes loose B6 claims.

**Answered threshold:** posterior >= 0.95 or <= 0.05. This is the most extraordinary discriminator and should demand the strictest standard.

**Role:** Separates Platonic/computational pattern realism from actual cross-life continuity. B3 can say "patterns exist"; B6 says identity can ride them across lives or instantiations.

---

## 5. Auxiliary Discriminators

These are not in the shortest tree but should be available for expected-information-gain selection.

### A1 — Spacetime Fundamentality

**Binary form:** Are spacetime locality and unitarity primitive constraints, rather than derived consequences of deeper non-spatiotemporal structure?

**YES supports:** B2.
**NO supports:** B1, B3, possibly B5.

**Key evidence:** amplituhedron, positive geometries, holography, quantum gravity, Wheeler-DeWitt style timeless formulations.

**Caution:** This does not directly decide consciousness-first metaphysics. It only decides whether physical realism must be spacetime-local or can become structural.

### A2 — IIT Exclusion / Definite Subject Borders

**Binary form:** Does conscious experience have a unique maximal physical substrate at a definite spatial and temporal grain?

**YES supports:** B2/IIT-compatible physical ontology, possibly B5 if process-grain wins.
**NO weakens:** IIT-style physical generation and strengthens B4/B6 depending on the failure mode.

**Key evidence:** split-brain, overlapping complexes, perturbational complexity, integrated information estimates, exclusion-postulate tests.

### A3 — Physical Closure

**Binary form:** Is the causal closure of the physical domain empirically complete for all observer behavior and reports?

**YES supports:** B2, weakens B4/B6.
**NO supports:** B4/B6 if the violation is tied to observer facts; otherwise it may support only new physics.

**Caution:** Violating current physics is not enough. The violation must bear on observer/object polarity or identity.

### A4 — Time Direction

**Binary form:** Is temporal becoming ontologically primitive rather than reducible to boundary conditions, entropy gradients, or perspectival records?

**YES supports:** B5.
**NO weakens:** B5 and supports B1/B3.

---

## 6. Integration With Existing Engine

The cascade should sit **above** the current propagation engine. The engine does not need to be replaced. It needs one new layer of data and one new branch scoring step.

### New Objects

```json
{
  "discriminator_id": "D1",
  "question": "Does every fact about information content, semantic reference, and observer identity supervene on the complete physical causal state and its lawful evolution?",
  "answers": ["yes", "no"],
  "status": "open|answered|stale",
  "posterior_yes": 0.5,
  "threshold_yes": 0.85,
  "threshold_no": 0.15,
  "branch_effects": {
    "yes": {"B1": 0.35, "B2": 1.25, "B3": 0.35, "B4": 0.25, "B5": 0.85, "B6": 0.30},
    "no":  {"B1": 1.10, "B2": 0.20, "B3": 1.15, "B4": 1.15, "B5": 1.10, "B6": 1.10}
  }
}
```

`posterior_yes` is computed by the same log-odds update machinery as features. It is a target node, just not one of F1-F8.

### Existing Engine Changes

Minimal code change:

1. Treat discriminators as additional `FeatureState`-like nodes: `D1`-`D5`.
2. Allow claims to target both feature IDs and discriminator IDs.
3. After propagation, compute branch support using:

```text
branch_support(B) =
  normalize(
    branch_prior(B)
    * product_D expected_branch_effect(D, B)
    * feature_projection(B)
  )
```

Where:

```text
expected_branch_effect(D, B) =
  P(D=yes) * effect(D=yes, B)
  + P(D=no) * effect(D=no, B)
```

This avoids hard elimination while evidence is uncertain. Once a discriminator passes its answer threshold, its effect becomes near-mask-like.

### Question Selection

The next top question should be chosen by expected information gain:

```text
EIG(D) =
  H(current_branch_distribution)
  - E_answer[H(branch_distribution | answer(D))]
```

Tie-breakers:

1. lower evidence cost
2. stronger falsifier
3. more independent source clusters
4. less semantic ambiguity

This is the binary-search principle made operational.

---

## 7. Answered Thresholds

| Node type | Threshold | Rationale |
|-----------|-----------|-----------|
| Ordinary feature | 0.75 / 0.25 | Useful for Bayesian trend tracking |
| Discriminator | 0.85 / 0.15 | Branch-affecting claims need stronger support |
| Consciousness intrinsicality | 0.90 / 0.10 | High semantic ambiguity |
| Cross-life continuity | 0.95 / 0.05 | Extraordinary claim; high fraud/confound surface |
| Formal theorem/no-go result | theorem-dependent | Use proof validity rather than empirical threshold |

No discriminator counts as answered without:

- at least one falsifier
- at least two independent evidence clusters
- no unresolved high-severity critic objection
- explicit branch-effect mapping

---

## 8. What Happens to F1-F8?

F1-F8 should remain, but they move down one layer.

Current feature states:

| Feature | New role |
|---------|----------|
| F1 consciousness_fundamental | Lower-level support under D3 |
| F2 pattern_space_real | Lower-level support under D4 |
| F3 pattern_space_nonphysical | Lower-level support under D4 |
| F4 relations_ontologically_basic | Lower-level support under D2 |
| F5 information_persists_across_instantiation | Lower-level support under D5 |
| F6 teleology_real | Auxiliary under B4/B5 |
| F7 cross_life_continuity | Lower-level support under D5 |
| F8 physical_law_emergent | Auxiliary under A1/D4 |

The branch layer should stop pretending F1-F8 are independent primitive axes. They are evidence-bearing features underneath discriminators.

---

## 9. Convergence Policy

The truth map should not try to "resolve to one metaphysics" by default. Level 0 is deliberately neutral: `S => (0 <-> 1)` says every coherent ontology must explain the enabling condition of distinction, observer, and observed. It does not guarantee that one current branch is uniquely correct.

Use three output states:

| State | Meaning |
|-------|---------|
| Live plurality | Multiple branches remain within 10x odds of the leader |
| Provisional winner | One branch is >10x the nearest competitor, but at least one top discriminator remains open |
| Converged branch | One branch is >100x the nearest competitor and all branch-separating discriminators on its path are answered |

This prevents false certainty while preserving the aim of truth-seeking.

---

## 10. Immediate Implementation Plan

1. Add `discriminators` table:

```sql
CREATE TABLE discriminators (
  discriminator_id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  prior_log_odds REAL NOT NULL,
  current_log_odds REAL NOT NULL,
  probability_yes REAL NOT NULL,
  threshold_yes REAL NOT NULL,
  threshold_no REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
);
```

2. Add `discriminator_branch_effects` table:

```sql
CREATE TABLE discriminator_branch_effects (
  discriminator_id TEXT NOT NULL,
  answer TEXT NOT NULL CHECK(answer IN ('yes', 'no')),
  branch_id TEXT NOT NULL,
  multiplier REAL NOT NULL,
  PRIMARY KEY (discriminator_id, answer, branch_id)
);
```

3. Extend `claims` targeting:

```sql
CREATE TABLE claim_targets (
  claim_id TEXT NOT NULL,
  target_id TEXT NOT NULL,      -- F1-F8 or D1-D5
  target_type TEXT NOT NULL,    -- feature|discriminator
  PRIMARY KEY (claim_id, target_id)
);
```

4. Replace `derive_all_branch_probs()` with `derive_branch_support()` that combines discriminator effects and feature projections.

5. Keep the existing F1-F8 feature tests, but add cascade tests:

- D1 yes pushes B2 above B4/B3.
- D1 no pushes B2 down.
- D2 yes separates B5 from B2.
- D3 yes separates B4 from B1/B3/B5.
- D5 yes separates B6 from B3.
- uncertain discriminators do not hard-eliminate branches.

---

## 11. Bottom Line

The top truth-map layer is a discrimination cascade over possible fillings of `S`, not a flat Bayesian feature board. The Bayesian engine remains necessary, but it should answer the lower-level question: "given the claims we have, how confident are we in each discriminator answer?"

The system should seek the fastest path to truth by asking the most eliminative falsifiable question available. It should not collapse nuanced metaphysical ambiguity into vague questions like "is consciousness fundamental?" until the operative meaning of "fundamental" has already been determined by sharper branch tests.
