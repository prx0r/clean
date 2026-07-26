# Truth Plan — Loose Direction Guide

## What We Learned

The truth map is not a Bayesian oracle. It never was.

It's an **evidence provenance system** organized around refutation-led questioning.

The engine tracks: what survived criticism, what didn't, what evidence moved which question, and what we should test next. The numbers are secondary — they're visual aids for trends, not metaphysical verdicts.

---

## Core Objects

```
Question → Candidate Explanations → Cruxes → Criticisms → Surviving Answer → Implications

Evidence sits inside this structure as provenance:
  "This criticism was raised by paper X, which bears on question Y via discriminator D3"
```

Everything we've built (D1-D5 cascade, propagation engine, evidence dimensions) is still useful as the **provenance and disagreement detection layer**. It just isn't the point.

---

## Logical Framework Selection

Different claims need different logic. The engine should map claims to the right framework:

| Claim type | Logic | Source |
|---|---|---|
| Empirical evidence | Nyāya pramāṇa (pratyakṣa + anumāna) | Already in TRUTHCHANGES6.md |
| Argument/critique | Nyāya 5-member syllogism + hetvābhāsa | Already specified |
| Paradox/emptiness | Catuskoṭi (FDE, 4-valued) | Not yet implemented |
| Multiple valid views | Jaina syādvāda (7-valued) | Not yet implemented |
| Meaning via exclusion | Dharmakīrti apoha | Partially in sanskritree BNF |
| Cross-perspective critique | Prasaṅga (reductio) | Already in sanskritree BNF |

The NNExpr parser from sanskritree (`bnf.py`, 72 lines) already covers most of these. Import it, don't rebuild it.

---

## Current Architecture (Codex Built This)

The system now has 5 layers:

| Layer | Question | Tool | Output | Failure mode |
|---|---|---|---|---|
| Source | What exactly was said? | Sanskritree / corpus retrieval | source spans, translations, TOs | bad philology |
| Formal | Can this be proved/typed? | Lean / Sanskritree proof engine | PROVED, UNPROVED, HOLLOW, OUTSIDE_FORMAL, REFUTED | too narrow |
| Argument | Does this inference survive criticism? | Nyāya/AIF argument graph | support, attack, crux, defeat status | bad reconstruction |
| Evidence | What evidence exists? | Truth-map Bayesian runtime | dimension/pramāṇa posterior vectors | pseudo-precision |
| Reality Brief | What is our best current answer? | State-of-play synthesis | surviving explanations, implications, next tests | overclaiming |

The argument fabric sits between formal proof and Bayesian evidence tracking. It's the core innovation.

---

## What Exists Now (Updated)

**Engine + Data layer:**
- Propagation engine (F1-F8 + D1-D5, 12 passing tests)
- Evidence dimensions + provenance reports
- 6 seeded questions
- Hetvābhāsa gates (TRUTHCHANGES6.md)

**Argument layer (NEW — Codex):**
- `TRUTHMAP-ARGUMENT-FABRIC.md` (422 lines) — master architecture with 5 layers, design commitments, canonical node types, GraphRAG shape
- `truthmap-argument-schema.sql` (290 lines) — additive SQLite/D1 schema with source_spans, argument_nodes, argument_edges, claim_gate_results, hetvābhāsa_checks, tarka_falsifiers, nigrahasthāna_events, formal_status_links, negative_bridge_controls, state_of_play snapshots
- `scripts/nyaya-truthmap-gate.py` (548 lines) — standalone pre-ingestion gate: infers pramāṇa, evidence_dimension, tradition_scope, checks hetvābhāsa, requires falsifiers, generates tarka falsifiers, optional Sanskritree formal probe
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json` (179 lines) — first flagship dossier with 4 candidates (Abhinavagupta, Dharmakīrti, Ñāṇavīra, higher-order/self-model), cruxes, falsifiers, state of play, next tests

**Sanskritree (available, not yet integrated):**
- NNExpr parser (bnf.py, 72 lines)
- FOL-to-Lean bridge (fol_lean_bridge.py, 125 lines)
- Ground truth JSON (11 files)
- Nyāya Phase 1 engine (phase1_nyaya.py)
- Bridge probe (bridge_probe.py, 131 lines)
- Lean files (Foundation.lean, Sanskrit.lean, IIT.lean, etc.)

---

## What's Still Missing (The Real Bottleneck)

1. **Zero EOs** — nothing for factories to consume. The argument dossier exists but hasn't been converted to an EO.
2. **66 of 72 questions not seeded** — the truth map is mostly empty.
3. **Gate not wired into ingestion** — `nyaya-truthmap-gate.py` is standalone, not called during packet ingestion.
4. **No dashboard** — no UI showing any of this.
5. **No publish gate** — content doesn't update the truth map.
6. **Sanskritree integration not connected** — formal probe exists but not wired into truth map posterior updates.

---

## Suggested Direction (Not Prescriptive)

### P0 — Wire the gate into ingestion
`nyaya-truthmap-gate.py` is standalone. It needs to be called during `ingest-packet.py` so every claim is validated against Nyāya rules before it touches the engine. The gate output should write to `claim_gate_results` table.

### P0 — Create one EO from the reflexivity dossier
The argument dossier exists. Convert it to an actual EO following `specs/EO.md` schema. Structure as 5-member Nyāya syllogism. This proves the pipeline works end to end.

### P1 — Seed 71 more questions
Turn RESEARCH_DIRECTIVE.md into truth map entries with the argument schema. Each question gets candidates, cruxes, falsifiers. The gate already expects this structure — populate it.

### P1 — Ingest 3-5 real papers through the gate
Run `extract-claims.py` → `nyaya-truthmap-gate.py` → engine. Watch posteriors move on real evidence. Validate that the gate catches bad claims.

### P2 — Simple dashboard
HTML page reading content/source-metaphysics/ and the argument fabric tables. Shows questions, surviving candidates, open cruxes, what evidence moved what.

### P3 — Wire Sanskritree formal probe into argument status
When argument nodes have associated Lean types, query Sanskritree proof engine for status. Store result in formal_status_links. HOLLOW/OUTSIDE_FORMAL propagate up as argument constraints.

---

## Design Constraints

- **Show vectors, not fusions.** Never collapse dimensions into one number without showing the disagreement underneath.
- **Falsifiers are required.** Every claim must have at least one falsifier or be marked HOLLOW/hermeneutic_context.
- **Pramāṇa types matter.** Perception, inference, comparison, testimony — they rank differently. Don't weight a śabda claim the same as pratyakṣa.
- **Tradition-scope everything.** Same claim from different traditions = different node. Convergence is a separate metric found by bridge probing.
- **Negative controls mandatory.** Known non-bridges must be ingested from Sanskritree before any bridge probing.
- **The boundary IS the finding.** HOLLOW, OUTSIDE_FORMAL, PARTIAL, UNPROVED are results, not errors.
- **Numbers are downstream.** Bayesian scores only after argument validation. They summarize evidence movement; they don't replace the argument graph.
