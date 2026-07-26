# Truth Changes — Evidence Dimension Architecture

## The Core Problem

The engine currently treats all evidence the same way: one Bayesian posterior per feature, per discriminator. But claims from **Abhinavagupta's phenomenology** and **an fMRI study** are not the same kind of thing. They operate in different epistemic dimensions, with different standards of evidence, different falsification conditions, and different convergence criteria.

Flattening them into one posterior destroys information and creates false precision.

---

## The Solution: Three Dimensions, One Map

Evidence arrives in three distinct dimensions. Each tracks its own posterior. Convergence across dimensions is a separate signal.

### Dimension 1 — Phenomenological/Philosophical
| Property | Value |
|----------|-------|
| **What counts as evidence** | Argument, internal consistency, explanatory scope, tension resolution, counterargument refutation |
| **Weight source** | Philosophical argument analysis by expert agents (or humans) |
| **Falsification** | Internal contradiction, failure to explain known phenomena, successful counterargument |
| **Convergence metric** | Degree of agreement across competing traditions on same question |
| **Key papers** | Tractatus series (our own), Ñāṇavīra, Abhinavagupta, Nanavira |
| **Example claim** | "Anattā and attā both fail without a grammar of reflexivity" (Nanavira) — confidence determined by argumentative structure, not data |

**How it works:** Abhinavagupta argues icchā-jñāna-kriyā is necessary. Buddhists argue it's contingent. The phenomenological track doesn't count citations — it analyzes the logical structure of each position, identifies the key tension points, and tracks which side resolves more of them. This is closer to **formal dialectics** than Bayesian updating.

### Dimension 2 — Empirical/Scientific
| Property | Value |
|----------|-------|
| **What counts as evidence** | Experimental data, replicable results, statistical significance, adversarial tests |
| **Weight source** | `w_rel` × `w_map` × `w_aux` × `w_dep` (existing engine) |
| **Falsification** | Failed replication, negative result in well-powered study |
| **Convergence metric** | Pre-registered prediction accuracy, adversarial collaboration outcomes |
| **Key papers** | IIT 3.0/4.0, Cogitate adversarial test (`10.1038/s41586-025-08888-1`), IIT vs PP adversarial review (`arXiv:2509.00555`) |
| **Example claim** | "40Hz gamma synchrony correlates with integrated information" — lbf=0.6, w_rel=0.75 |

**How it works:** The existing Bayesian engine handles this dimension well. Claims have lbf, weights, paradigm-crowding discounts. The Rosetta Stone paper (`arXiv:2409.20318`) shows how to mathematically bridge this with D3 via predictive processing beliefs.

### Dimension 3 — Contemplative/First-Person
| Property | Value |
|----------|-------|
| **What counts as evidence** | Reproducible first-person verification, intersubjective agreement among practitioners, stability across conditions |
| **Weight source** | Practitioner count, tradition consensus, stability across retreat conditions, EEG correlates where available |
| **Falsification** | Claimed state not reproducible by competent practitioners, no stable EEG signature, conflicts with well-established phenomenological reports |
| **Convergence metric** | Cross-traditional agreement on same state type, teacher-student transmission consistency |
| **Key papers** | Josipovic (`10.1093/nc/niab031`), Laukkonen & Slagter (`10.1016/j.neubiorev.2021.06.021`), Atad et al. (`10.1093/nc/niaf013`), Ward et al. (`10.1093/nc/niaf068`) |
| **Example claim** | "Nondual awareness is available as a reproducible state across traditions" — confidence from ~2000 years of cross-traditional reports |

**How it works:** This is the hardest to formalize. A claim's weight here depends on:
- Number of independent traditions reporting the same state type
- Consistency of description across practitioners within a tradition
- Stability of the state under controlled conditions (retreats, EEG environments)
- Degree of agreement on the state's phenomenology between advanced practitioners

---

## Architecture

### Evidence Dimension Schema

Each claim now has an `evidence_dimension` field. The engine tracks posteriors per dimension, not just per feature.

```json
{
  "claim_id": "cl:abhinavagupta-iccha-jnana-kriya-necessary",
  "claim_text": "icchā-jñāna-kriyā is a necessary architecture of manifestation, not anthropomorphic projection",
  "evidence_dimension": "phenomenological",
  "targets": [
    {"target_id": "D3", "target_type": "discriminator"},
    {"target_id": "F4", "target_type": "feature"}
  ],
  "log_bayes_factor": 0.7,
  "w_rel": 0.85,
  "w_map": 0.75,
  "w_aux": 0.80,
  "paradigm": "trika",
  "reasoning": "Abhinavagupta's argument in Tantraloka establishes icchā-jñāna-kriyā as the necessary structure of manifestation through: (1) showing that agency requires these three moments, (2) demonstrating that the Buddhist alternative (momentariness) cannot account for recognition, (3) linking the structure to the phenomenology of self-awareness. Counterarguments from Buddhist logic weaken but do not refute — the tension point remains active.",
  "falsifier": {
    "type": "phenomenological",
    "condition": "A Buddhist account of recognition that does not presuppose icchā-jñāna-kriyā, demonstrated through first-person verification across traditions",
    "status": "untested"
  }
}
```

### Dimension-Seeded Priors

Each question starts with different priors per dimension:

```json
{
  "question_id": "q:consciousness-fundamental",
  "dimension_priors": {
    "phenomenological": 0.35,
    "empirical": 0.30,
    "contemplative": 0.40
  },
  "conviction_gates": {
    "strongly_supported": {
      "phenomenological": 0.75,
      "empirical": 0.75,
      "contemplative": 0.75,
      "convergence": 0.60
    }
  }
}
```

### Convergence as a First-Class Signal

The key innovation: **convergence across dimensions is its own metric**.

```python
def compute_convergence(dimension_probs: dict) -> float:
    """
    How much the dimensions agree on a question.
    
    1.0 = all three dimensions report the same probability
    0.0 = maximal bounded disagreement, e.g. one track near 1.0
          while the others are near 0.0
    
    Uses bounded variance normalization. This is a diagnostic, not a
    confidence multiplier.
    """
    probs = list(dimension_probs.values())
    if len(probs) < 2:
        return 1.0
    mean = sum(probs) / len(probs)
    variance = sum((p - mean)**2 for p in probs) / len(probs)
    max_variance = (len(probs) - 1) / (len(probs) ** 2)
    return clamp(1.0 - (variance / max_variance), 0.0, 1.0)
```

Convergence tells you:
- **High convergence + high confidence** = robust finding (e.g., "brains are involved in consciousness" — all three dimensions agree)
- **Low convergence** = the interesting frontier ("is consciousness fundamental?" — phenomenological/contemplative say yes, empirical says underdetermined)
- **High convergence + low confidence** = everyone agrees they don't know (underdetermined across all dimensions)

### Adversarial Collaboration Integration

The IIT vs Predictive Processing adversarial collaboration (`arXiv:2509.00555`, `10.1038/s41586-025-08888-1`) is a natural fit:

```
Adversarial Collaboration Result
  ├── IIT prediction: confirmed (p=0.02)
  │     └── Bears on D3 (intrinsic phenomenality): lbf +0.4, empirical dimension
  ├── GNWT prediction: not confirmed (p=0.31)
  │     └── Bears on D3: lbf -0.2, empirical dimension
  └── Adversarial collaboration protocol → protocol_quality metadata
```

Adversarial collaborations do **not** get an automatic hidden `w_aux` bump.
The cited adversarial-collaboration papers justify treating protocol quality as
auditable evidence metadata: preregistered predictions, mutually accepted
theory commitments, independent/lab-crossing execution, data availability, and
publish-any-result commitments. A reviewer can choose to translate that protocol
quality into `w_aux`, but the report must show the decomposition and rationale.

---

## Paper Contribution Tracking

Every paper's contribution to the truth map becomes fully auditable:

```json
{
  "paper_id": "arxiv:1312.2007",
  "title": "The Amplituhedron",
  "dimension": "empirical",
  "claims": [
    {
      "claim_id": "cl:amplituhedron-spacetime-not-fundamental",
      "lbf": 0.6,
      "w_rel": 0.75,
      "w_map": 0.60,
      "w_aux": 0.70,
      "w_dep": 1.0,
      "effective_lbf": 0.189,
      "target": "D4",
      "posterior_delta": "+0.047",
      "branch_effects": {
        "B2": -0.03,
        "B3": +0.07,
        "B1": -0.01
      }
    }
  ],
  "total_evidence_power": 0.189,
  "evidence_power_rank": "#3 of 47 papers ingested"
}
```

---

## Key Changes to the Engine

### 1. Add `evidence_dimension` to Claims
- Values: `phenomenological`, `empirical`, `contemplative`
- Each dimension gets its own posterior per feature/discriminator
- Each dimension has its own `w_dep` paradigm-crowding track (Trika claims don't crowd neuroscience claims)

### 2. Replace Single Branch Score with Dimension-Vector Branch Score
```python
branch_support = {
    "B4": {
        "phenomenological": 0.72,
        "empirical": 0.35,
        "contemplative": 0.80,
        "convergence": 0.62
    }
}
```

### 3. Add Convergence Metric
- Computed per question, per discriminator, per branch
- High convergence accelerates confidence (cross-dimension validation)
- Low convergence flags the question as "active frontier"

### 4. Paradigm Crowding Becomes Dimension-Specific
- `w_dep` computed per dimension per feature
- Phenomenological Trika claims don't crowd empirical neuroscience claims
- Only claims in the same dimension on the same feature experience crowding

### 5. Protocol Metadata for Adversarial Collaborations
- Store `protocol_quality` separately from `w_aux`
- Require flags for preregistration, mutually agreed predictions, independent labs, open data/code, and publish-any-result commitments
- Allow higher `w_aux` only as an explicit reviewed judgment with reasoning
- Keep direct discriminator caps unchanged unless the claim packet records a protocol-specific cap rationale

---

## Current Runtime Status

Implemented in `truthengine_working.py`:

- `claims.evidence_dimension` with migration support and default inference from paradigm.
- Parallel dimension posteriors for F1-F8 features and D1-D5 discriminators.
- Dimension-specific paradigm crowding: same-paradigm claims crowd only inside the same evidence dimension.
- Dimension branch vectors: `dimension_branches[branch_id][dimension]`.
- Convergence diagnostics for features, discriminators, and branches.
- Provenance records include `evidence_dimension`, `w_dep`, effective LBF, posterior before/after, and branch deltas.
- `scripts/provenance-report.py --dimension empirical|phenomenological|contemplative`.

The legacy scalar outputs remain for compatibility, but the production UI should
treat the dimension-vector outputs as the honest view.

---

## Falsifiability Standards by Dimension

| Dimension | Strong positive evidence | Strong negative evidence | What is falsifiable |
|-----------|--------------------------|--------------------------|---------------------|
| Phenomenological/philosophical | A formally explicit argument that resolves named tensions better than competitors under agreed terms | Internal contradiction, scope failure, decisive counterexample, or failure to steelman a live rival position | The argument's coherence, target mapping, scope claim, and translation into opponent vocabulary |
| Empirical/scientific | Preregistered prediction, adequate power, direct measurement/manipulation, replication, open data/code, adversarial protocol | Failed replication, prediction miss in a severe test, confound that breaks target mapping, retraction | The operational prediction and whether it bears on the claimed discriminator/feature |
| Contemplative/first-person | Reproducible state report from trained practitioners, cross-tradition invariance, teacher-student consistency, blinded/state protocol where possible | Competent-practitioner non-reproduction, unstable phenomenology under controls, failed inter-rater agreement | The reproducibility of the reported state and the claimed mapping from state to discriminator/feature |

Physiology can falsify a contemplative claim only when the claim includes a
physiological coupling. It cannot by itself falsify a purely first-person
classification claim.

---

## Implementation Order

1. **(P0) Add `evidence_dimension` to ClaimRecord** — simple enum field
2. **(P0) Split posteriors by dimension** — each feature gets 3 parallel posteriors
3. **(P1) Implement convergence metric** — `compute_convergence()` function
4. **(P1) Dimension-specific paradigm crowding** — separate `w_dep` per dimension
5. **(P2) Branch scores become dimension vectors** — update `derive_branch_support()`
6. **(P2) Add adversarial collaboration trust bonus** — detect adversarial study design
7. **(P3) Per-paper contribution report** — full traceability script

---

## What This Unlocks

- **Abhinavagupta vs Buddhism on self/no-self** — tracked in phenomenological dimension, resolved by argumentative analysis, not fMRI
- **Hard problem** — the D3 (phenomenological) and D2 (empirical) dimensions naturally diverge here; the convergence score captures exactly the tension the hard problem names
- **PiEEG meditation data** — sits at the D2/D3 boundary, feeds both dimensions with different weights
- **Nanavira's reflexivity argument** — pure phenomenological claim, tracked independently from any empirical evidence

The truth map stops pretending it's a pure Bayesian machine and starts being what it actually is: a **multidimensional epistemic tracking system** that makes its assumptions visible at every level.
