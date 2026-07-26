# Truth Changes 6 — Nyāya Logic as the Evidence Framework

## The Core Insight

The truth map has been trying to solve a problem Nyāya already solved 2000 years ago: **how to systematically evaluate competing claims using different kinds of evidence.**

Nyāya gave us:
- **Pramāṇa** — what counts as valid evidence (4 types)
- **Vyāpti** — how to map from evidence to conclusion (invariable concomitance)
- **Hetvābhāsa** — how to detect bad arguments (5 fallacy types)
- **Nigrahasthāna** — where an argument necessarily fails (points of defeat)
- **Tarka** — how to reason counterfactually (reductio, presupposition)

The truth map's current evidence dimensions, claim weights, and quality gates are ad-hoc versions of these. Nyāya's system is more rigorous and battle-tested. Let's use it.

---

## 1. Pramāṇa — Evidence Dimensions (Replace Our Ad-Hoc 3)

Nyāya defines exactly 4 means of valid knowledge (pramāṇa). They map directly to our evidence dimensions:

| Nyāya pramāṇa | What it is | Maps to truth map | What it covers |
|---|---|---|---|
| **Pratyakṣa** (perception) | Direct sensory or phenomenal givenness | **Empirical** dimension | fMRI data, EEG recordings, behavioral experiments, direct observation |
| **Anumāna** (inference) | Inference from sign (liṅga) to sign-bearer (liṅgin) via vyāpti | **Formal/Dialectical** dimension | Logical arguments, structural correspondences, mathematical proofs, formal models |
| **Upamāna** (comparison) | Knowledge by analogy or structural correspondence | **Analogical** dimension | Cross-tradition mappings (Trika ↔ active inference), structural correspondences |
| **Śabda** (testimony) | Reliable testimony from a trustworthy source | **Textual** dimension | Primary source texts (Tantrāloka, PV III), scholarly translations, expert authority |

This is 4 dimensions, not 3. Our earlier 3 collapsed analogy and testimony into "phenomenological" — wrong. The Nyāya pramāṇas are the correct taxonomy.

```
Example claim assigned to correct pramāṇa:

"Abhinavagupta claims icchā-jñāna-kriyā is necessary"
  → pramāṇa: śabda (testimony) — this is a textual claim about what a source says

"fMRI shows DMN decoupling during nondual states"
  → pramāṇa: pratyakṣa (perception extended by instruments) — empirical

"Icchā↔preference mapping is structurally isomorphic"
  → pramāṇa: upamāna (comparison) — analogical

"If icchā is necessary, then without it agency is impossible"
  → pramāṇa: anumāna (inference) — formal/dialectical
```

### Pramāṇa Hierarchy

Not all pramāṇas are equal. Nyāya ranks them by reliability in case of conflict:

```
Pratyakṣa (perception) — strongest when available
  → Anumāna (inference) — weaker than direct observation
    → Upamāna (comparison) — weaker than inference
      → Śabda (testimony) — weakest, depends on source reliability
```

When evidence conflicts, the higher pramāṇa wins unless it's shown to be defective.

**Application to truth map:** When a contemplative claim (śabda — tradition testimony) contradicts an empirical finding (pratyakṣa — fMRI data), the empirical finding weighs heavier *unless* the contemplative claim can show the empirical method is defective (e.g., fMRI can't measure what it claims to measure).

---

## 2. Vyāpti — The Mapping Rule (Replace Feature-to-Discriminator Weights)

In Nyāya inference, the key relation is **vyāpti** (invariable concomitance): the universal relation between the sign (liṅga, hetu) and the inferred property (sādhya).

```
Standard example: "Wherever there's smoke, there's fire"
  vyāpti: smoke → fire (smoke is invariably accompanied by fire)
  hetu: smoke on the hill
  sādhya: fire on the hill
  anumāna: therefore, fire exists on the hill
```

**Our truth map has been trying to encode vyāpti using `w_map` weights without knowing it.**

```
D4 discriminator: "Do mathematical patterns have truth-making status independent of physical instantiation?"

Claim evidence: "Amplituhedron shows spacetime locality is emergent"
  → hetu: amplituhedron evidence
  → sādhya: D4 = YES (patterns are real independent of instantiation)
  → vyāpti: Does amplituhedron evidence ALWAYS imply pattern realism? 
    No, not always — structural physicalism can absorb it.
  → vyāpti_confidence: 0.6 (the mapping is real but has exceptions)
```

This is exactly what our feature-to-discriminator mapping table tries to capture. The Nyāya framework makes it explicit:

```json
{
  "claim_id": "cl:amplituhedron-D4",
  "hetu": "Amplituhedron shows locality/unitarity as emergent from positive geometry",
  "sādhya": "Pattern space has truth-making status (D4 = YES)",
  "vyāpti_statement": "If physical law is derivable from non-spatiotemporal mathematical structure, then mathematical patterns have truth-making status",
  "vyāpti_type": "antarvyāpti | bahirvyāpti",  // internal vs external concomitance
  "vyāpti_confidence": 0.6,
  "vyāpti_violations": [
    "Structural physicalism can absorb amplituhedron without metaphysical Platonism",
    "The amplituhedron covers only N=4 SYM, not all QFT"
  ],
  "pramāṇa": "anumāna"
}
```

---

## 3. Hetvābhāsa — Claim Validation Gates (Replace Ad-Hoc Weighting)

Nyāya classifies exactly 5 types of fallacious reasons (hetvābhāsa). Every claim entering the truth map should be checked against these:

| Fallacy | Sanskrit | What it means | Truth map gate | Example |
|---|---|---|---|---|
| **Inconsistent** | Savyabhicāra | The hetu doesn't always imply the sādhya — counterexamples exist | Check vyāpti for known violations | "Meditation produces nondual awareness → meditation proves consciousness is fundamental" — meditation doesn't always produce nondual awareness (savyabhicāra) |
| **Contradictory** | Viruddha | The hetu proves the opposite of what's claimed | Check if evidence actually supports the counter-claim | "Brain damage alters consciousness → consciousness depends on brain" — this actually supports D3 = NO (intrinsic phenomenality not required), not whatever the claimant wanted |
| **Unproven** | Asiddha | The hetu itself is not established | Check if the evidence is independently verified | "The subtle body exists → reincarnation is real" — the hetu (subtle body) itself is unproven |
| **Counterbalanced** | Satpratipakṣa | Another inference with equal force proves the opposite | Check for equally strong counter-claims | "IIT supports B4 (consciousness-first)" countered by "IIT's physical implementation requirement supports B2 (physical realism)" — both inferences have some support |
| **Contradicted by stronger evidence** | Bādhita | A stronger pramāṇa directly contradicts the conclusion | Check if higher-ranked pramāṇa contradicts | "Trika says consciousness is fundamental (śabda)" vs "fMRI shows brain states correlate perfectly with conscious states (pratyakṣa)" — perception beats testimony when they conflict |

### Gate Implementation

Before any claim enters the truth map engine, run the hetvābhāsa gate:

```python
def hetvabhasa_gate(claim: ClaimRecord) -> GateResult:
    """
    Check a claim against all 5 Nyāya fallacies.
    Returns pass/fail with reasoning.
    """
    failures = []
    
    # 1. Savyabhicāra — is the vyāpti invariable?
    if has_known_counterexamples(claim.hetu, claim.sādhya):
        failures.append(("savyabhicāra", f"{claim.hetu} doesn't always imply {claim.sādhya}"))
    
    # 2. Viruddha — does evidence support the opposite?
    if contradicts_established_evidence(claim.hetu, claim.sādhya):
        failures.append(("viruddha", f"evidence actually supports ¬{claim.sādhya}"))
    
    # 3. Asiddha — is the hetu itself established?
    if not is_established(claim.hetu):
        failures.append(("asiddha", f"{claim.hetu} is not independently established"))
    
    # 4. Satpratipakṣa — is there an equally strong counter-inference?
    if has_equally_strong_counter_inference(claim):
        failures.append(("satpratipakṣa", f"counter-inference with equal force exists"))
    
    # 5. Bādhita — does a stronger pramāṇa contradict?
    if contradicted_by_higher_pramana(claim):
        failures.append(("bādhita", f"stronger evidence type contradicts"))
    
    return GateResult(
        passed=len(failures) == 0,
        failures=failures,
        adjusted_lbf=compute_adjusted_lbf(claim, failures)
    )
```

---

## 4. Nigrahasthāna — Non-Equivalence Tracking

Nigrahasthāna (points of defeat) are where an argument necessarily fails — the debate equivalent of our "non-equivalence" tracking. Nyāya lists 22 types. The key ones for our truth map:

| Nigrahasthāna | Meaning | Maps to |
|---|---|---|
| **Pratijñāhāni** | Abandoning the original thesis | When a tradition retreats from its claim under pressure |
| **Pratijñāntara** | Shifting the thesis | When the claim changes under criticism |
| **Arthāpatti** | Unwanted presupposition | When accepting a claim forces accepting something the proponent doesn't want |
| **Prakaraṇasama** | Begging the question | When the evidence presupposes the conclusion |
| **Sādhyasama** | Proving what needs to be proved | Circular reasoning |

These map to our non-equivalence tracking:

```
Tension point: Trika says consciousness is fundamental

Nigrahasthāna check:
  → Has Trika abandoned the thesis under pressure? (pratijñāhāni) — No
  → Has Trika shifted what "fundamental" means? (pratijñāntara) — Possibly; "fundamental" shifts between context
  → Does consciousness-first force unwanted commitments? (arthāpatti) — Yes: brain dependence problem
  → Does Trika's evidence presuppose its conclusion? (prakaraṇasama) — Partially: experience is used as evidence that experience is fundamental
  → Is the argument circular? (sādhyasama) — Under debate
```

Each tension point in the truth map gets a nigrahasthāna section tracking which defeat mechanisms have been tried and whether they succeeded.

---

## 5. Tarka — Falsifier Generation

Tarka (hypothetical reasoning) is Nyāya's method for testing claims by examining their consequences. It includes:

- **Prasaṅga** (reductio ad absurdum) — "If P, then Q. Q is false/absurd → ¬P"
- **Arthāpatti** (presupposition) — "P presupposes Q. If Q is false, P is false"

We can use tarka to **automatically generate falsifiers** for claims:

```python
def generate_tarka_falsifier(claim: ClaimRecord) -> list[Falsifier]:
    """
    Apply prasaṅga (reductio) to generate what would falsify the claim.
    """
    falsifiers = []
    
    # Prasaṅga: If P, then Q. If ¬Q, then ¬P.
    for consequence in deduce_consequences(claim.claim_text):
        falsifiers.append({
            "type": "prasaṅga",
            "form": f"If {claim.claim_text}, then {consequence}. Show ¬{consequence} → ¬{claim.claim_text}",
            "status": "untested"
        })
    
    # Arthāpatti: P presupposes Q. If ¬Q, then ¬P.
    for presupposition in find_presuppositions(claim.claim_text):
        falsifiers.append({
            "type": "arthāpatti",
            "form": f"{claim.claim_text} presupposes {presupposition}. Show ¬{presupposition} → revise {claim.claim_text}",
            "status": "untested"
        })
    
    return falsifiers
```

Every claim entering the truth map should have at minimum one falsifier generated by tarka.

---

## 6. The 5-Member Syllogism — EO Structure

Nyāya's formal inference has 5 members (avayava). This maps perfectly to the EO structure:

| Member | Sanskrit | Meaning | EO field |
|---|---|---|---|
| 1. Proposition | **Pratijñā** | The claim to be established | EO title / tension point |
| 2. Reason | **Hetu** | The evidence or ground | Primary ROs / claims |
| 3. Example | **Udāharaṇa** | A concrete case demonstrating vyāpti | Structural correspondence table |
| 4. Application | **Upanaya** | Applying the general rule to this case | Directional critique (how this evidence bears on this question) |
| 5. Conclusion | **Nigamana** | Therefore, the proposition is established | Research verdict / best current answer |

```
Example EO structured as Nyāya syllogism:

1. Pratijñā: "Nondual awareness reveals the structure of reality, not merely self-model plasticity"
2. Hetu: "Because it has distinct phenomenology (recognition, not confusion) that cross-traditional reports agree on, and because the hard problem remains unresolved by self-model theories"
3. Udāharaṇa: "Josipovic (2014) shows DMN decoupling + sensory integration during nondual states — a specific neural signature, not absence. Atad (2025) shows trait changes in advanced practitioners. These patterns hold across Trika, Buddhist, and Christian contemplative traditions."
4. Upanaya: "This evidence specifically bears on D3 (intrinsic phenomenality) — if nondual states can be fully explained by self-model plasticity, we would expect confusion or depersonalization, not recognition. The phenomenology of recognition exceeds what self-model collapse predicts."
5. Nigamana: "Therefore, nondual awareness is structurally suggestive of consciousness-first ontology, though the neural correlates data prevents strong confidence."
```

Every EO should be readable (and writable) as a 5-member Nyāya syllogism. If an EO can't be structured this way, it's not a valid EO.

---

## 7. Integration with Existing Engine

### Claim Schema Updates

```json
{
  "claim_id": "cl:example",
  "pramāṇa": "pratyakṣa | anumāna | upamāna | śabda",
  "hetu": "the evidence or reason",
  "sādhya": "what the evidence points to",
  "vyāpti_statement": "the universal concomitance claimed",
  "vyāpti_confidence": 0.0-1.0,
  "hetvābhāsa_check": {
    "passed": true,
    "failures": [],
    "reviewer": null
  },
  "tarka_falsifiers": [
    {"type": "prasaṅga", "form": "...", "status": "untested"},
    {"type": "arthāpatti", "form": "...", "status": "untested"}
  ]
}
```

### Gate Pipeline

```
Paper → SO → RO → Claim

Claim enters:
  → Pramāṇa assignment (which evidence type?)
  → Tarka falsifier generation (what would disprove this?)
  → Hetvābhāsa gate (which fallacy does this commit?)
    → Failed: flagged for review, lbf reduced, not silently accepted
    → Passed: proceeds to engine
  → Vyāpti check (does the evidence actually support the target?)
    → Low vyāpti_confidence → weaker claim
  → Engine ingestion
    → Each pramāṇa type gets its own paradigm-crowding track
    → Dimension posteriors per pramāṇa type
    → Convergence: are the pramāṇas pointing in the same direction?

Question progress:
  → For each tension point:
    → Which nigrahasthāna have been tried?
    → Have any succeeded (forced thesis abandonment)?
    → How many prasaṅga/arthāpatti falsifiers remain untested?
```

---

## 8. What This Changes

| Current truth map | With Nyāya framework |
|---|---|
| 3 ad-hoc evidence dimensions | 4 pramāṇa types with known reliability hierarchy |
| w_map weight guessed by LLM | vyāpti confidence with explicit violation tracking |
| Quality gates are informal | 5 hetvābhāsa types with clear criteria |
| Non-equivalences tracked loosely | 22 nigrahasthāna types for precise defeat tracking |
| Falsifiers rarely generated | tarka generates per claim automatically |
| EO structure invented from scratch | 5-member syllogism as EO template |
| Dimension-specific paradigm crowding | Pramāṇa-specific paradigm crowding — claims from different evidence types don't crowd each other |

---

## 9. Relation to Sanskritree Project

The sanskritree project at `/mnt/HC_Volume_106427611/sanskritree/` already has:

- **nyayaengine.py** (575 lines) — implements the Nyāya engine with falsifiability gate, tradition-scoped terms, divergence tracking
- **nyaya_claims.json** — Nyāya axiom seeds (pramāṇa definition, vyāpti, etc.)
- **THESIS.md** — Formal proof engine architecture (7-step algorithm)
- **proofenginge.md** — Full algorithm with sayability gate, decomposition, propagation
- **review.md** — Peer review identifying 7 critical gaps (G1-G7) including missing Navya-Nyāya templates, FDE for Nāgārjuna, two-negation types, defeated argument tracking

The truth map should **import the Nyāya conceptual framework** from sanskritree without duplicating the Lean formal proof pipeline. Sanskritree asks "can this be proved?" The truth map asks "what evidence exists?" They use the same logic but different tools.

---

## 10. Implementation Order

1. **P0: Pramāṇa field on claims** — Add `pramāṇa` enum to ClaimRecord, update schema
2. **P0: Hetvābhāsa gate** — Implement 5-fallacy check as claim ingestion filter
3. **P1: Tarka falsifier generation** — Generate prasaṅga/arthāpatti falsifiers per claim
4. **P1: Nigrahasthāna tracking on tension points** — Track defeat mechanisms per question
5. **P2: Vyāpti confidence** — Replace ad-hoc w_map with explicit vyāpti violation tracking
6. **P2: 5-member syllogism EO template** — Structure EOs as Nyāya inferential forms
7. **P3: Import sanskritree's Nyāya axioms** — Seed ground truth from sanskritree's nyaya_claims.json
