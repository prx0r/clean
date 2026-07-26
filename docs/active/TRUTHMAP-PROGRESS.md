# Truth Map — Progress & Codebase Status

## Quick Start Reading Order

If you're a new agent coming up to speed, read in this order:

```
1. tractatus-conscientiae.md          — Level 0 metaphysics (S => (0 <-> 1))
2. magnum-opus/05-SOURCE-METAPHYSICS.md — Original truth map concept
3. TRUTHMAP-REDESIGN.md               — D1-D5 discrimination cascade (current design)
4. CODEX-TRUTHMAP.md                  — Codex design decisions
5. truthengine.md                     — Math/logic of the engine
6. specs/TRUTH-MAP-QUESTION.md        — Schema reconciliation
7. specs/CLAIM.md                     — Claim evidence spec
8. EVIDENCE-PIPELINE.md               — Pipeline design
9. truthengine-propagation.py         — The actual math code
10. truthengine_working.py             — SQLite runtime
11. test_truthengine_working.py        — Current tests
12. REDTEAM-TRUTHMAP.md               — Attack vectors to break
```

---

## Doc Quality Ratings

### Essential — High Quality, Current
These are the active design documents. Read these.

| File | ★ | Lines | Why |
|------|---|-------|-----|
| `TRUTHMAP-REDESIGN.md` | ★★★★★ | 574 | Current truth map design — D1-D5 cascade, branch-effect matrix, EIG selection. This IS the spec. |
| `CODEX-TRUTHMAP.md` | ★★★★★ | 129 | Codex design decisions. Reference for multiplier bands, mapping rules, extraction policy. |
| `specs/TRUTH-MAP-QUESTION.md` | ★★★★☆ | 288 | Schema reconciliation between 3 conflicting models. Required reading before making data. |
| `specs/CLAIM.md` | ★★★★☆ | 327 | The atomic evidence unit spec. Weight computation, validation rules, extraction guidelines. |
| `EVIDENCE-PIPELINE.md` | ★★★★☆ | 168 | Paper → Information Packet → Truth Map. Pipeline design with test packet. |
| `truthengine.md` | ★★★★☆ | 169 | Math/logic explanation. Bayes + Deutsch hard-to-vary criterion. |
| `tractatus-conscientiae.md` | ★★★★★ | 134 | Level 0 metaphysics. S => (0 <-> 1). Six branches B1-B6. Foundational. |
| `magnum-opus/05-SOURCE-METAPHYSICS.md` | ★★★★☆ | 96 | Original truth map concept. Question taxonomy, status values. Superseded by TRUTHMAP-REDESIGN but good context. |
| `magnum-opus/10-FULL-SPEC.md` | ★★★★☆ | 678 | Full system spec showing where truth map fits in 4-factory model. |
| `magnum-opus/25-ARCHITECTURE.md` | ★★★★☆ | 481 | Engineering blueprint. Data model, 3 loops, TPN feed algorithm, versioning. |
| `magnum-opus/13-FLAWS.md` | ★★★★★ | 205 | Risk assessment. Critical: No EOs exist, truth map staleness, hypothesis engine noise. |
| `BUILD-NOTES.md` | ★★★★☆ | 110 | Pipeline evolution history. Gen 1-3 lessons learned. 3 conflicting schemas identified. |

### Implementation — The Code

| File | ★ | Lines | Why |
|------|---|-------|-----|
| `truthengine-propagation.py` | ★★★★★ | 304 | Math core. sigmoid, log_odds, compute_dep_weight, FeatureState, ClaimRecord, PropagationEngine. Clean, tested. |
| `truthengine_working.py` | ★★★★★ | 654 | SQLite runtime. D1-shaped schema, seed data, build_truth_map_db(), PropagationEngine.run(). Working. |
| `truthengine_d1.py` | ★★★☆☆ | 301 | Cloudflare D1 REST adapter. Python-based. Never tested against real D1. |
| `truthengine-schema.sql` | ★★★★☆ | 118 | SQLite schema migration. Features, claims, evidence tables. |
| `truthengine-migrate.py` | ★★★★☆ | 138 | DB migration script. Creates tables, seeds F1-F8. |
| `truthengine-db.py` | ★★★☆☆ | 155 | Reference code for DB methods. Meant to be merged into a DatabaseManager class. |
| `test_truthengine_working.py` | ★★★★☆ | 147 | 6 unittest tests. All passing. Seeded run, incremental update, paradigm crowding, supersession. |
| `truthengine-test-validation.py` | ★★☆☆☆ | 422 | 12 pytest tests. **BROKEN** — imports `tests.fixtures` which doesn't exist in this repo. |
| `truthengine-test-validation-v2.py` | ★★☆☆☆ | 327 | 9 pytest tests. **BROKEN** — uses nonexistent fixtures `engine_factory`, `indicator_claim_factory`. |
| `scripts/extract-claims.py` | ★★★★☆ | 317 | Claim extraction from arxiv papers. Conservative prompt with lbf caps. Works, needs API key. |
| `scripts/ingest-packet.py` | ★★★★☆ | 125 | Packet ingestion into truth map DB. Records before/after delta. |

### Data Files

| File | ★ | Lines | Why |
|------|---|-------|-----|
| `content/source-metaphysics/q-*.json` (6 files) | ★★★☆☆ | 17-21 | Seed truth map questions. Underdetermined, confidence 0.25-0.40. Schema v0 — conflicts with ClaimRecord model. |
| `content/information-packets/test-amplituhedron.json` | ★★★★☆ | 46 | Test packet. Amplituhedron claim targeting D4. Good example of correct schema. |
| `content/information-packets/delta-amplituhedron.json` | ★★★★☆ | 64 | Ingestion delta log. Before/after states. |

### Specs — Well Written, Not Yet Implemented
These are the granular specs. Read before building.

| File | ★ | Lines | What It Specs | Implemented? |
|------|---|-------|---------------|-------------|
| `specs/SO.md` | ★★★★☆ | 221 | Source Object | ❌ Not started |
| `specs/RO.md` | ★★★★☆ | 326 | Research Object | ❌ Not started (exist in blog project) |
| `specs/EO.md` | ★★★★☆ | 302 | Essay Object | ❌ CRITICAL GAP — zero exist |
| `specs/TO.md` | ★★★★☆ | 243 | Translation Object | ❌ Not started |
| `specs/HYPOTHESIS-ENGINE.md` | ★★★★☆ | 322 | Hypothesis Engine | ❌ Not started |
| `specs/DB-INTEGRATION.md` | ★★★★☆ | 266 | DB Integration | ⚠️ Partial (truthengine_d1.py) |

### Outdated / Superseded
These are still useful for context but the design has moved on.

| File | Why Outdated | Replaced By |
|------|-------------|-------------|
| `magnum-opus/02-AUDIT-SUMMARY.md` | Audits blog project, not clean project | BUILD-NOTES.md line 70-78 |
| `magnum-opus/07-HYPOTHESIS-ENGINE.md` | Pre-cascade concept | specs/HYPOTHESIS-ENGINE.md |
| `magnum-opus/03-RESEARCH-OBJECTS.md` | Pre-granular-specs concept | specs/RO.md |
| `magnum-opus/04-ESSAY-OBJECTS.md` | Pre-granular-specs concept | specs/EO.md |
| `magnum-opus/08-FARM-INFRA.md` | Never deployed, architecturally stale | magnum-opus/10-FULL-SPEC.md Cloudflare section |
| `magnum-opus/09-HERMES-ORCHESTRATION.md` | References specific Hermes configs | magnum-opus/10-FULL-SPEC.md |
| `truthengine-integration-spec.md` | Cross-stream TCEE integration — pre-cascade | TRUTHMAP-REDESIGN.md |
| `formalsystemnotes.md` / `formalsystemnotes2.md` / `formalsystemnotes-raw.md` | Raw brainstorming, superseded by tractatus series | tractatus-conscientiae.md |

### Nice-to-Have / Vision
Read these when you need inspiration, not when you need to build.

| File | ★ | Why |
|------|---|-------|
| `magnum-opus/14-VISIONARY.md` | ★★★★☆ | What legendary looks like. Pathway A-D. Phase 1-3 plan. |
| `magnum-opus/15-GREENSCREEN.md` | ★★★☆☆ | Satsang platform thesis. Ethical YouTube alternative. Distraction from truth map. |
| `magnum-opus/16-GTM.md` | ★★★☆☆ | Go-to-market. Content-first, TO bomb, legitimacy flywheel. |
| `magnum-opus/19-SATSANG-REPUTATION.md` | ★★★☆☆ | Q-score, reputation tiers, research dashboard. |
| `magnum-opus/21-UNSAID.md` | ★★★★☆ | Low-hanging fruit + wild visions. The live translation stream, truth map as game, etc. |
| `magnum-opus/22-TRUTH-MARKET.md` | ★★★☆☆ | Prediction markets on truth map questions. Good idea, far future. |
| `magnum-opus/23-CONVERGENCE.md` | ★★★★☆ | Truth map → organism spec → built wetware. The long game. |
| `magnum-opus/24-PIEEG-INTEGRATION.md` | ★★★☆☆ | Live EEG neurofeedback meditation hardware. Concrete but early. |
| `magnum-opus/17-VIDEO-FACTORY-HITL.md` | ★★★☆☆ | Human-in-the-loop render review. Dashboard + FableCut + Voicebox. |
| `magnum-opus/18-ANAKHRARENDER.md` | ★★★☆☆ | Full render pipeline spec with shader parameter UI. |
| `tractatus-song-with-no-singer.md` | ★★★☆☆ | Human-facing narrative of dependent origination. Beautiful but optional. |
| `tractatus-observer-theorem.md` | ★★★☆☆ | Formal theorem of contextual distinction. Supplementary to tractatus-conscientiae. |
| `tractatus-nanavira-abhinavagupta.md` | ★★★☆☆ | Comparative reflexivity analysis. Supplementary. |

### Distractions / Low Priority for Truth Map Work

| File | Why Low Priority |
|------|-----------------|
| `beautify/*.py` + `queue/*.py` | Video factory render packs. Not relevant to truth map engineering. |
| `beautify-archive/*` | Archived batch 1 render packs. Irrelevant. |
| `HANDOVER-GLSL.md` | GLSL shader pipeline handover. Video factory, not truth map. |
| `HERMES-SKILLS.md` | Stub reference. Blog project details. |
| `machinedreams.md` / `machinedreams-experimental.md` | Convergence vision. Nice but not actionable. |
| `hxrmxs/` | Reference notes from hxrmxs repo. Lot of signal but already extracted into magnum-opus. |
| `hxrmxs-audit.md` / `hxrmxs-extract.md` | Same — already extracted. |
| `neurodatasets/` | Dataset access docs. Actionable only after truth map is running. |
| `researchers/analayo/*.md` | Title-only stubs. No content yet. |
| `rasa-institute.md` | Academic press concept. Far future. |
| `AM0-framework.md` | Ontology-to-constructor-theory mapping. Interesting but not blocking. |

---

## Codebase Organization

### Active Truth Map Pipeline (Order Matters)

```
truthengine-propagation.py       ← Math core (Bayesian engine)
truthengine_working.py           ← SQLite runtime (tested, working)
truthengine_d1.py                ← D1 REST adapter (untested)
truthengine-schema.sql           ← Schema migration
truthengine-migrate.py           ← Migration script
scripts/extract-claims.py        ← Paper → Information Packet
scripts/ingest-packet.py         ← Packet → D1 ingestion
content/source-metaphysics/      ← 6 seed questions
content/information-packets/     ← 1 test packet + 1 delta
test_truthengine_working.py      ← 6 passing tests
```

### What's Missing (Critical Path in Order)

| Priority | What | Why |
|----------|------|-----|
| **P0** | D1-D5 discriminator tables + branch_support() | Engine only handles F1-F8. Cascade not implemented. |
| **P0** | Schema alignment: q-*.json ↔ ClaimRecord ↔ magnum-opus | 3 models disagree. Cannot add data until resolved. |
| **P1** | Fix broken test files (v1, v2) | `tests.fixtures` and pytest fixtures don't exist. |
| **P1** | Create one EO | Zero Essay Objects exist. Architecture cannot be validated. |
| **P2** | SO → content/source-objects/ | Full spec, zero instances. |
| **P2** | Hypothesis Engine | EO proposals, RO disagreement detection, Critic agent. |
| **P3** | 72 truth map questions | Only 6 seeded. 66 more pending from RESEARCH_DIRECTIVE.md. |
| **P3** | Truth map dashboard | HTML page reading content/source-metaphysics/. |
| **P3** | Staleness cron | 90-day expiry check. |

### File Tree (Cleaned)

```
clean/
│
├── Active Truth Map Pipeline (P0)
│   ├── truthengine-propagation.py       ← Bayesian math core
│   ├── truthengine_working.py           ← SQLite runtime
│   ├── truthengine_d1.py                ← D1 REST adapter
│   ├── truthengine-schema.sql           ← Migration SQL
│   ├── truthengine-migrate.py           ← Migration script
│   ├── scripts/
│   │   ├── extract-claims.py           ← Paper → Packet
│   │   └── ingest-packet.py            ← Packet → D1
│   ├── content/
│   │   ├── source-metaphysics/         ← 6 seed questions
│   │   └── information-packets/        ← 1 test packet + delta
│   └── tests/
│       ├── test_truthengine_working.py  ← 6 passing tests
│       ├── truthengine-test-validation.py  ← BROKEN (v1)
│       └── truthengine-test-validation-v2.py ← BROKEN (v2)
│
├── Current Design Docs (read these)
│   ├── tractatus-conscientiae.md        ← Level 0 metaphysics
│   ├── TRUTHMAP-REDESIGN.md             ← D1-D5 cascade (CURRENT SPEC)
│   ├── CODEX-TRUTHMAP.md                ← Codex design decisions
│   ├── truthengine.md                   ← Engine math explanation
│   ├── EVIDENCE-PIPELINE.md             ← Pipeline design
│   ├── REDTEAM-TRUTHMAP.md              ← Attack vectors
│   ├── BUILD-NOTES.md                   ← Pipeline evolution
│   └── TRUTHMAP-PROGRESS.md             ← This file
│
├── Granular Specs (P1-P2)
│   └── specs/
│       ├── SO.md, RO.md, EO.md, TO.md
│       ├── CLAIM.md, HYPOTHESIS-ENGINE.md
│       ├── DB-INTEGRATION.md
│       └── TRUTH-MAP-QUESTION.md
│
├── Architecture Vision (magnum-opus/)
│   ├── 01-VISION.md through 25-ARCHITECTURE.md
│   └── README.md
│
├── Root Docs
│   ├── VISION.md, ROADMAP.md, RESEARCH_DIRECTIVE.md
│   ├── GRANULAR-SPEC.md, ONBOARDING.md, REF.md
│   ├── FORCODEX.md, dev25.md
│   ├── formalsystemnotes*.md
│   ├── tractatus-*.md (3 files)
│   └── machinedreams*.md
│
├── Video Factory (separate concern)       ← Not relevant to truth map
│   ├── beautify/ (5 active packs)
│   ├── beautify-archive/ (5 archived + lib/)
│   └── queue/ (19 queued packs)
│
├── Reference / Research
│   ├── researchers/analayo/
│   ├── researchideas/ideas1.md
│   ├── researchsources/100sources.md
│   ├── resources/by-scholar/
│   ├── neurodatasets/
│   └── hxrmxs/
│
├── Misc
│   ├── skills/
│   ├── CODEX-TRUTHMAP-PROMPT.md
│   └── opencode.json
```

---

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Truth map questions seeded | 6 | 72 (from RESEARCH_DIRECTIVE.md) |
| Essay Objects | 0 | 500+ (from VISIONARY.md) |
| Source Objects | 0 | 1,917 (migrating blog project Works) |
| Passing tests | 6 | 30+ (need D1-D5 + red-team) |
| Broken test files | 2 | 0 |
| Propagation engine features | F1-F8 only | F1-F8 + D1-D5 discriminators |
| Information packets ingested | 0 | 100+ (before ML correction) |
| Branches tracked | B1-B6 | B1-B6 (6 branches, stable) |
| Branch-effect multipliers | 0 | 60 (5 discriminators × 2 answers × 6 branches) |
| Schema conflicts | 3 models | 1 unified model |

---

## Immediate Next Steps (Truth Map)

1. **(P0) Align schemas** — Resolve 3 conflicting models per specs/TRUTH-MAP-QUESTION.md
2. **(P0) Implement D1-D5 discriminator tables** in truthengine_working.py
3. **(P0) Add branch_support()** combining discriminator effects + feature projection
4. **(P1) Fix broken test files** — create fixtures or rewrite with real imports
5. **(P1) Run red-team attack vectors** per REDTEAM-TRUTHMAP.md
6. **(P1) D1-D5 claim extraction** — update extract-claims.py prompt for discriminators
7. **(P2) Expand from 6 to 72 truth map questions**
8. **(P2) Create one manual EO** to validate the architecture
