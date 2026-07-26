# Truth Map Redesign — Discrimination Cascade

Don't stress-test the SQLite runtime. That's grunt work. Instead, think about whether the truth map's epistemological structure is correct.

## The Problem

The current engine tracks 8 features (F1-F8) → derives 6 branch probabilities. But this structure doesn't ask the hardest questions first. It doesn't discriminate between branches efficiently. Questions like "Is consciousness fundamental?" are bad top-level discriminators because multiple branches can answer "yes" with different interpretations.

## What It Should Be

A **discrimination cascade** grounded in the formal philosophy:

```
Tractatus Level 0 (S ⇒ (0 ↔ 1))
  ↓
6 branches (B1-B6) — each fills S differently
  ↓
Top-level binary questions — each answer eliminates ≥1 branch
  ↓
Lower-level questions — Bayesian nuance for what remains
  ↓
Claim evidence — falsifiable science at every level
```

The key design principle: **each top-level question should be chosen to rule out the maximum number of branches.** Like binary search — the question that eliminates the most possibilities is the best next question.

## The 6 Branches (from tractatus-conscientiae.md)

| Branch | What S is | Key commitments |
|--------|-----------|----------------|
| B1 | Formal/structural | Thin Formalism — reality is mathematical structure |
| B2 | Physical matter | Physical Realism — matter is fundamental |
| B3 | Platonic/computational | Platonic Idealism — pattern-space is real and non-physical |
| B4 | Consciousness | Nondual Consciousness-First — consciousness is the ground |
| B5 | Process/relation | Process Metaphysics — relation is more fundamental than substance |
| B6 | Cross-life continuity | Rebirth/Continuity — identity persists across life instances |

## Candidate High-Level Binary Questions

These should be questions where:
- The answer is falsifiable by real science (not just philosophical preference)
- The answer eliminates or strongly penalizes ≥1 branch
- The answer is actually binary (yes/no is meaningful)

### Q1: Does information content supervene entirely on physical structure?
- **Yes** → penalizes B3 (Platonic computationalism — patterns don't exist independently)
- **No** → penalizes B1, B2 (structure is not enough)
- **Falsifiable by:** Landauer's principle, quantum error correction bounds, whether Shannon information in a black hole is fully determined by its physical state

### Q2: Can a purely physical system have intrinsic causal powers beyond those described by its microphysics?
- **No** → penalizes B4, B5, B6 (consciousness, process, continuity require more than physics)
- **Yes** → penalizes B2 (physicalism's sufficiency is wrong)
- **Falsifiable by:** whether true causal emergence exists (integrated information, downward causation experiments)

### Q3: Does the amplituhedron (or similar geometric object) show that space-time is not fundamental?
- **Yes** → penalizes B2 (physicalism loses its stage)
- **No** → penalizes B3, B4, B5 (depending on what replaces spacetime)
- **Falsifiable by:** Arkani-Hamed's research programme — if the amplituhedron reduces to standard QFT in all regimes, spacetime stands

### Q4: Can a single physical system support two independent conscious subjects?
- **Yes** → penalizes B4 (consciousness is not substrate-bound)
- **No** → penalizes B6 (cross-life continuity requires independence from substrate)
- **Falsifiable by:** split-brain experiments, IIT's exclusion postulate, Grimes' integrated information measurements

### Q5: Does the universe have a preferred temporal direction that is not reducible to statistical asymmetry?
- **Yes** → penalizes B1, B3 (formal/computational views where time is emergent)
- **No** → penalizes B5 (process metaphysics requires temporal directedness)
- **Falsifiable by:** whether the arrow of time reduces to the second law of thermodynamics, Wheeler-DeWitt equation interpretations

## Design Task

Given the 6 branches, the tractatus Level 0 foundation, and the constraint that falsifiable science must bear on each question:

1. **Design the optimal discrimination cascade** — what is the shortest sequence of binary questions that separates the 6 branches? What's the minimum number of yes/no answers needed to identify which branch is correct?

2. **For each question, specify:**
   - The exact binary form
   - Which branches it penalizes for each answer
   - The falsifiable science that bears on it (specific experiments, predictions, or formal results)
   - What confidence threshold in the truth engine counts as "answered" for this question

3. **Map the result to the current truth engine code.** How does the discrimination cascade integrate with `truthengine-propagation.py`? Does the engine need restructuring, or does the cascade sit above it as a question-selection layer?

4. **Address the tension:** The tractatus Level 0 says S ⇒ (0 ↔ 1) is ontologically neutral. But the truth map must eventually converge on one filling of S. Is that even the right goal? Or should the system maintain multiple live branches with relative support scores (as it does now)?

Output your design as `TRUTHMAP-REDESIGN.md` in the clean project root.
