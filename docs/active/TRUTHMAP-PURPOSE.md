# Truth Map — Purpose & Relationship to Sanskritree

## The Two Layers

The project has always had two layers. They were built separately and need to be unified.

### Layer 1: Sanskritree (Formal Proof)
**What it does:** Takes Sanskrit philosophical claims and tries to prove them in Lean 4. Outputs PROVED, OUTSIDE_FORMAL, or HOLLOW.

**Where it lives:** `/mnt/HC_Volume_106427611/sanskritree/`

**Key documents:** THESIS.md, proofenginge.md, standards.md, nyayaengine.py

**Its method (7-step algorithm):**
```
STEP 0 — Sayability: Is the claim falsifiable? If not → HOLLOW.
STEP 1 — Library check: Has this been proved elsewhere? Reuse.
STEP 2 — Formalize: Map to Lean type signature.
STEP 3 — Prove: Pantograph/Lean. Success → PROVED.
STEP 4 — Decompose: If unprovable, split into sub-claims. Recurse.
STEP 5 — Propagate: Parent status from children (REFUTED > HOLLOW > PROVED > UNPROVED > PARTIAL).
```

**What it produces:**
- A node graph where every claim has a status (PROVED / UNPROVED / PARTIAL / HOLLOW / OUTSIDE_FORMAL / REFUTED)
- Centre nodes (high reuse_count across traditions — formal primitives discovered, not assumed)
- Divergence nodes (where traditions share structure but differ in axiom commitment)
- Bridges (same Lean type from independent decomposition across traditions — found, not constructed)
- The boundary between formal and non-formal as the finding

**Its key insight:**
> "The goal is honesty, not proofs. HOLLOW and OUTSIDE_FORMAL are correct when the text does not support formalization. The boundary between what can and cannot be formalized is itself a finding."

**Its limitation:** Lean formalization of Sanskrit philosophy is extremely hard. The pipeline works for simple cases (Dharmakīrti's pratyakṣa definition) but struggles with complex metaphysical claims. The "Lean is dead" note in the blog project handover reflects this — the Lean bridge was dropped for production, retained only for Sanskrit philosophical inference validation.

---

### Layer 2: Truth Map (Evidence Tracking)
**What it does:** Tracks what evidence exists for and against each research question. For each question: what supports it, what contradicts it, how confident we are, what content we've produced.

**Where it lives:** `/root/projects/clean/` (this project)

**Key documents:** TRUTHMAP-REDESIGN.md, TRUTHCHANGES.md, specs/CLAIM.md, specs/TRUTH-MAP-QUESTION.md

**Its method:**
```
Paper → SO → RO → Claim → Truth Map (engine tracks claims → features → discriminators → branches)
Question → EO → Essay/Video → Analytics → Truth Map update
```

**What it produces:**
- Per-question confidence across evidence dimensions (phenomenological, empirical, contemplative)
- Convergence scores (how much the dimensions agree)
- Provenance/blame reports (which paper moved which question by how much)
- Per-paper contribution reports

**Its limitation:** The Bayesian math looks precise but the weights are opinions. The engine is useful for tracking trends and organizing evidence, but it can't prove anything.

---

## The Relationship

```
SANSKRITREE (Formal Proof Layer)          TRUTH MAP (Evidence Layer)
─────────────────────────────             ────────────────────────────
Asks: "Can this be proved?"              Asks: "What evidence exists?"
Tool: Lean 4 theorem prover              Tool: Bayesian evidence engine
Output: PROVED / HOLLOW / REFUTED        Output: confidence score per dimension
Scope: Formalizable claims only          Scope: All claims (formal + empirical + phenomenological)
Truth standard: Machine-checkable proof  Truth standard: Weight of evidence + argument
Risk: Too narrow — excludes most claims  Risk: Pseudo-precision from opinion weights

They are complementary:
  sanskritree covers the formal core — what can be proved about pramāṇa, pratyakṣa, etc.
  Truth map covers everything else — empirical studies, phenomenological reports,
  contemplative evidence, philosophical arguments, non-formalizable claims.
```

The two layers share the same structure:
- **Divergence nodes** = tension points where traditions disagree
- **Tradition-scoped claims** = paradigm-specific evidence tracks
- **The boundary as finding** = unresolved non-equivalence is valid output

---

## What the Combined System Looks Like

For a single question, the combined system shows:

```
Q: "Is consciousness fundamental?"

SANSKRITREE (formal):
  ├── Dharmakīrti (PV III): pratyakṣa defined via arthakriyā → PROVED
  ├── Nyāya: pramāṇa as factive → PROVED
  ├── Utpaladeva's bridge: using Dharmakīrti's tools to prove conscious knower → PARTIAL
  └── Abhinavagupta: cit as svaprakāśa → UNPROVED (not formalized)

TRUTH MAP (evidence):
  ├── Phenomenological: Trika texts + Josipovic → confidence 0.6
  ├── Empirical: fMRI/EEG of nondual states → confidence 0.35
  ├── Contemplative: cross-traditional reports → confidence 0.7
  └── Convergence: 0.6 (dimensions diverge — science lags)

The sanskritree layer shows what CAN be formally proved.
The truth map shows what EVIDENCE exists.
Both are honest about their limits.
```

---

## What This Means for the Current Truth Map

The truth map should:

1. **Adopt sanskritree's falsifiability gate.** Every claim should state what would count as evidence against it. If no falsifier can be stated, flag the claim as unfalsifiable (not "unsupported" — structurally different).

2. **Adopt sanskritree's tradition-scoping.** A claim from Trika and a claim from IIT on the same question are different nodes. They get separate confidence tracks. Convergence across traditions is a separate metric.

3. **Adopt sanskritree's divergence tracking.** For each tension point, track exactly where the two traditions diverge — not just "they disagree" but "they disagree on axiom X, which has these consequences."

4. **Adopt sanskritree's boundary-as-finding.** If evidence can't resolve a question, that IS the answer for now. Don't force convergence. Show the unresolved divergence transparently.

5. **Drop the pretense of objectivity.** The OG project never pretended Bayesian weights were objective. It said "the goal is honesty, not proofs." The truth map should adopt the same attitude: confidence numbers are judgments, displayed with their reasoning, never shown without provenance.
