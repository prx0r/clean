# Session Handover — 2026-07-26

## What We Accomplished

### Architecture Decisions

1. **The truth map is not a Bayesian oracle.** It's a refutation-led evidence provenance system. The engine tracks what survived criticism, what evidence moved which question, and what to test next. Numbers are summaries, not verdicts. (TRUTHCHANGES5.md)

2. **Nyāya logic is the claim validation framework.** Four pramāṇas (evidence types), five hetvābhāsas (fallacies), five-member syllogism for EO structure, tarka for falsifier generation. Not the ultimate logic — catuskoṭi, syādvāda, and apoha are also available — but Nyāya is the default gate. (TRUTHCHANGES6.md)

3. **The system has 5 layers:** Source → Formal → Argument → Evidence → Reality Brief. The argument fabric (new) sits between formal proof and Bayesian tracking. (TRUTHMAP-ARGUMENT-FABRIC.md)

4. **ROs are just faithful passage libraries.** No gate, no falsifiers, no proving. The gate runs on the USE of a passage in an EO or dossier. An RO is organized by theme, auditable to source, navigable for agents. (RO-v2.md, VERSIONING-INFRA.md)

5. **EOs are structured as Nyāya syllogisms.** Pratijñā → hetu → udāharaṇa → upanaya → nigamana. Plus candidates with status (live/weakened/defeated) and state of play. (EO-v2.md)

6. **Versioning must be automated software, not agent discipline.** Source changes propagate through dependency tracking. Git hooks auto-bump RO versions. D1 tables track dependents. (VERSIONING-INFRA.md)

### Files Created/Updated This Session

| File | Lines | What It Is |
|------|-------|-----------|
| `SIMULATION.md` | ~150 | Full pipeline walkthrough: SO→RO→dialectical→EO→truth map on one question |
| `SYSTEM-SPEC.md` | ~100 | End-to-end architecture with all components, loops, status |
| `TRUTHMAP-PROGRESS.md` | ~200 | Doc quality ratings, codebase organization, key metrics, gaps |
| `TRUTHMAP-PURPOSE.md` | ~100 | Relationship between OG sanskritree (Lean proofs) and current truth map |
| `TRUTHCHANGES6.md` | ~200 | Nyāya logic as evidence framework — pramāṇas, hetvābhāsas, TIPS, 5-member syllogism |
| `TRUTHCHANGES8.md` | ~100 | TO→NNExpr→truth map pipeline: using translations as training data |
| `TRUTHPLAN.md` | ~100 | Direction guide: what exists, what's blocking, priorities, constraints |
| `TRUTHMAP-ARGUMENT-FABRIC.md` | 422 | Master architecture for unified truth map + argument graph (Codex) |
| `truthmap-argument-schema.sql` | 290 | Additive SQLite/D1 schema (Codex) |
| `scripts/nyaya-truthmap-gate.py` | 548 | Pre-ingestion gate with pramāṇa inference, hetvābhāsa, tarka (Codex) |
| `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json` | 179 | First flagship dossier with 4 candidates (Codex) |
| `specs/EO-v2.md` | ~200 | EO as Nyāya 5-member syllogism + candidates + state of play |
| `specs/RO-v2.md` | ~200 | RO as faithful passage library, simplified from v1 |
| `VERSIONING-INFRA.md` | ~150 | Automated RO lifecycle: change detection, auto-bump, dependency propagation |
| `content/source-texts/nanavira-fundamental-structure/` | 3 files | SO + full text of both essays (Static/Dynamic Aspect) |
| `CODEX-TRUTHMAP-SEED.md` | ~100 | Arxiv papers + implementation plan for Codex on D1-D5 cascade |
| `CODEX-TRUTHMAP-PROMPT.md` | ~40 | Quick handover prompt for Codex |

### Codex Work This Session

- D1-D5 discriminator cascade + evidence dimensions fully integrated into propagation engine (12 tests passing)
- `TRUTHMAP-ARGUMENT-FABRIC.md` — 5-layer architecture
- `truthmap-argument-schema.sql` — additive schema
- `scripts/nyaya-truthmap-gate.py` — 548-line pre-ingestion gate
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json` — first dossier
- `TRUTHCHANGES5.md` — refutation-led redesign
- `TRUTHMAP-PRODUCTION-HARDENING.md` — production rules
- `scripts/provenance-report.py` — blame reports
- Corrected: no automatic adversarial collaboration trust bonus (right call)

---

## Current State

### ✅ Working
- Propagation engine (F1-F8 + D1-D5, 12 passing tests)
- Evidence dimensions (phenomenological, empirical, contemplative)
- Nyāya pre-ingestion gate (standalone, 548 lines)
- Argument fabric schema (290 lines SQL)
- First reflexivity dossier (179 lines, 4 candidates)
- Provenance/blame reports
- Nanavira's Fundamental Structure texts imported as SO
- 6 seeded truth map questions

### ❌ Not Working / Missing
- **Zero EOs** — the critical gap. Nothing for factories to consume.
- **66 of 72 questions not seeded** — truth map is mostly empty
- **Gate not wired into ingestion** — standalone, not called during packet ingestion
- **No dashboard** — no UI
- **No publish gate** — content doesn't update truth map
- **Sanskritree not connected** — formal probe exists but not wired
- **NNExpr parser not imported** from sanskritree (bnf.py, fol_lean_bridge.py)
- **Broken test files** — `truthengine-test-validation.py` and v2 import nonexistent fixtures

---

## File Organization

```
clean/
│
├── Active Pipeline
│   ├── truthengine-propagation.py     ← Bayesian math core
│   ├── truthengine_working.py         ← SQLite runtime (F1-F8 + D1-D5 + dimensions)
│   ├── truthengine_d1.py              ← D1 REST adapter
│   ├── truthengine-schema.sql         ← Migration SQL
│   ├── content/source-metaphysics/    ← 6 seed questions + 1 argument dossier
│   ├── content/information-packets/   ← 1 test packet + delta
│   ├── scripts/extract-claims.py      ← Paper → Packet
│   ├── scripts/ingest-packet.py       ← Packet → D1
│   ├── scripts/nyaya-truthmap-gate.py ← Pre-ingestion gate (Codex)
│   ├── scripts/provenance-report.py   ← Blame reports (Codex)
│   └── test_truthengine_working.py    ← 12 passing tests
│
├── Current Design
│   ├── TRUTHMAP-REDESIGN.md           ← D1-D5 cascade (572 lines)
│   ├── TRUTHCHANGES5.md               ← Refutation-led model (Codex)
│   ├── TRUTHCHANGES6.md               ← Nyāya logic framework
│   ├── TRUTHCHANGES8.md               ← TO→NNExpr→truth map
│   ├── TRUTHMAP-ARGUMENT-FABRIC.md    ← 5-layer architecture (Codex)
│   ├── TRUTHMAP-PRODUCTION-HARDENING.md ← Production rules (Codex)
│   ├── truthmap-argument-schema.sql   ← Additive schema (Codex)
│   ├── TRUTHMAP-PROGRESS.md           ← Doc ratings, gaps, metrics
│   ├── TRUTHMAP-PURPOSE.md            ← Relationship to sanskritree
│   ├── TRUTHPLAN.md                   ← Direction guide
│   └── VERSIONING-INFRA.md            ← Auto-versioning design
│
├── Specs (v2 — current design)
│   ├── specs/EO-v2.md                 ← EO as Nyāya syllogism
│   ├── specs/RO-v2.md                 ← RO as faithful passage library
│   └── specs/   (v1 — legacy)         ← SO.md, EO.md, RO.md, TO.md, CLAIM.md, etc.
│
├── Source Material
│   └── content/source-texts/
│       └── nanavira-fundamental-structure/
│           ├── SO.json
│           ├── static-aspect.txt
│           └── dynamic-aspect.txt
│
├── Reference / Research
│   ├── magnum-opus/ (25 files)        ← Architecture vision
│   ├── RESEARCH_DIRECTIVE.md          ← 72 questions, 5 levels, 7-step procedure
│   ├── SIMULATION.md                  ← Walkthrough on one question
│   ├── SYSTEM-SPEC.md                 ← End-to-end architecture
│   ├── tractatus-conscientiae.md      ← Level 0: S => (0 <-> 1)
│   ├── CODEX-TRUTHMAP-SEED.md         ← Arxiv papers + engine implementation plan
│   └── CODEX-TRUTHMAP-PROMPT.md       ← Short handover prompt
│
├── Video Factory (separate concern)
│   ├── beautify/ (5 packs)
│   ├── beautify-archive/ (5 packs + GLSL lib)
│   └── queue/ (19 packs)
│
└── Tests
    ├── test_truthengine_working.py    ← 12 passing
    ├── truthengine-test-validation.py ← BROKEN
    └── truthengine-test-validation-v2.py ← BROKEN
```

---

## Priority Queue for Next Agent

### P0 — Wire the gate into ingestion
`scripts/nyaya-truthmap-gate.py` is standalone. It needs to be called during `ingest-packet.py`. Every claim should go through the gate before touching the engine. Gate output writes to `claim_gate_results` table.

### P0 — Create one EO
The reflexivity dossier exists (`content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json`). Convert it to an actual EO following `specs/EO-v2.md` schema. This proves the pipeline works end to end — dossier → EO → factory → essay/video.

### P1 — Import NNExpr parser from sanskritree
Copy `bnf.py` (72 lines) and `fol_lean_bridge.py` (125 lines) from `/mnt/HC_Volume_106427611/sanskritree/proof_engine/` into `scripts/logic/`. Wire into the Nyāya gate so claims get parsed as Navya-Nyāya expressions.

### P1 — Seed the remaining 71 questions
Turn RESEARCH_DIRECTIVE.md into truth map entries with the argument schema. Each question gets: tension_point, candidates, cruxes, falsifiers, resolution_level. Use the reflexivity dossier as template.

### P1 — Fix broken test files
`truthengine-test-validation.py` and v2 import `tests.fixtures` which doesn't exist in this repo. Create the fixture or remove the imports.

### P2 — Simple dashboard
HTML page reading `content/source-metaphysics/` and argument fabric schema. Shows questions, surviving candidates, open cruxes, evidence provenance.

### P2 — Wire Sanskritree formal probe
When argument nodes have associated Lean types, query sanskritree proof engine for status (PROVED/UNPROVED/HOLLOW). Store result in `formal_status_links`. HOLLOW propagates up as argument constraint.

### P3 — Implement VERSIONING-INFRA.md
Create `scripts/version-ro.py`, `scripts/on-source-update.py`, `ro_index` and `ro_dependents` tables, git pre-commit hook.

---

## Key Constraints

- **Never hide fusion assumptions.** Show dimensional vectors before any collapsed summary.
- **Falsifiers are required on every claim.** If a claim can't state what would disprove it, it's HOLLOW.
- **Tradition-scope everything.** Same word in different traditions = different node until a bridge is proved.
- **The boundary is the finding.** HOLLOW, OUTSIDE_FORMAL, PARTIAL, UNPROVED are results, not errors.
- **Numbers are downstream.** Bayesian scores only after argument validation. They summarize evidence movement; they don't replace the argument graph.
- **ROs don't prove anything.** They're faithful passage libraries. The gate runs on USE, not creation.
