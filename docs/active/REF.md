# Clean — Project Reference

Research nucleus for the Trika–Consciousness-Science pipeline. Everything an agent needs.

---

## Onboarding (Read First)

| Order | File | What It Is |
|-------|------|------------|
| 1 | `ONBOARDING.md` | Entry point. 12 files to read in order. |
| 2 | `RESEARCH_DIRECTIVE.md` | Master research programme: 72 questions, 5-level inquiry, 7-step dialectical procedure. |
| 3 | `tractatus-conscientiae.md` | Level 0 metaphysics: S => (0 <-> 1), six branches B1-B6. |
| 4 | `TRUTHMAP-ARGUMENT-FABRIC.md` | Current architecture: 5 layers, argument graph, Nyāya gate. |

---

## Active Architecture

| File | What It Is |
|------|------------|
| `TRUTHMAP-ARGUMENT-FABRIC.md` | **Current architecture.** 5-layer system: source → formal → argument → evidence → reality brief. 422 lines. |
| `TRUTHCHANGES5.md` | Refutation-led redesign. Dethrones Bayesian oracle. Truth map is an evidence provenance system. |
| `TRUTHCHANGES6.md` | Nyāya logic as evidence framework: 4 pramāṇas, 5 hethābhāsas, 5-member syllogism, tarka falsifiers. |
| `TRUTHPLAN.md` | Direction guide: what exists, what's blocking, priorities, constraints. |
| `TRUTHMAP-PRODUCTION-HARDENING.md` | Production rules: show vectors, don't fuse, falsifiers required, tradition-scope. |
| `TRUTHMAP-PROGRESS.md` | Doc quality ratings, codebase organization, key metrics, gaps. |
| `VERSIONING-INFRA.md` | Automated RO lifecycle: change detection, auto-bump, dependency propagation. |

---

## Engine

| File | What It Is |
|------|------------|
| `truthengine-propagation.py` | Bayesian math core: sigmoid, log_odds, paradigm crowding, PropagationEngine. 304 lines. |
| `truthengine_working.py` | SQLite runtime: F1-F8, D1-D5, B1-B6, 3 evidence dimensions, dimension-specific crowding, convergence, provenance. 984 lines. |
| `truthengine_d1.py` | Cloudflare D1 REST adapter (Python). |
| `test_truthengine_working.py` | 21 runtime tests. |
| `test_nyaya_gate.py` | 6 Nyāya gate tests. |
| `scripts/provenance-report.py` | Blame reports per source/target/dimension. |

---

## Nyāya Gate

| File | What It Is |
|------|------------|
| `scripts/nyaya-truthmap-gate.py` | Pre-ingestion gate: pramāṇa inference, hethābhāsa, falsifier requirements, tradition scope. 548 lines. |
| `scripts/logic/bnf.py` | NNExpr BNF grammar parser: vyāpti, abheda, catuskoṭi, prasaṅga, apoha. 72 lines. From sanskritree. |
| `scripts/logic/fol_lean_bridge.py` | FOL-to-Lean4 bridge: maps Nyāya/Dharmakīrti concepts to Lean types. 125 lines. From sanskritree. |

---

## Argument Fabric Schema

| File | What It Is |
|------|------------|
| `truthmap-argument-schema.sql` | Additive SQLite/D1 schema: source_spans, argument_nodes, argument_edges, claim_gate_results, hethābhāsa_checks, tarka_falsifiers, nigrahasthāna_events, formal_status_links, negative_bridge_controls, state_of_play_snapshots. 290 lines. |

---

## Specs (Current)

| File | What It Is |
|------|------------|
| `specs/EO-v2.md` | EO as Nyāya 5-member syllogism + candidates + state of play. |
| `specs/RO-v2.md` | RO as faithful passage library. Simplified from v1. |

---

## Specs (Legacy — v1)

| File | What It Is |
|------|------------|
| `specs/SO.md` | Source Object spec (221 lines). |
| `specs/RO.md` | Research Object spec v1 (326 lines). Superseded by RO-v2. |
| `specs/EO.md` | Essay Object spec v1 (302 lines). Superseded by EO-v2. |
| `specs/TO.md` | Translation Object spec (243 lines). |
| `specs/CLAIM.md` | Claim spec v1 (327 lines). Partially superseded by runtime. |
| `specs/HYPOTHESIS-ENGINE.md` | Hypothesis Engine spec (322 lines). |
| `specs/DB-INTEGRATION.md` | DB Integration spec (266 lines). |
| `specs/TRUTH-MAP-QUESTION.md` | Schema reconciliation (288 lines). |

---

## magnum-opus/ — Historical Architecture (Pre-Refutation-Led Redesign)

The original architectural blueprint. Still useful for context but superseded by the argument fabric design.

| File | Relevance |
|------|-----------|
| `01-VISION.md` | Vision. Historical. |
| `02-AUDIT-SUMMARY.md` | Blog project audit. Still factual. |
| `03-RESEARCH-OBJECTS.md` | RO concept. Superseded by RO-v2. |
| `04-ESSAY-OBJECTS.md` | EO concept. Superseded by EO-v2. |
| `05-SOURCE-METAPHYSICS.md` | Truth map concept. Superseded by TRUTHMAP-ARGUMENT-FABRIC. |
| `06-FACTORY-ARCHITECTURE.md` | 4-factory model. Still valid for factories. |
| `07-HYPOTHESIS-ENGINE.md` | Hypothesis Engine. Spec updated. |
| `08-FARM-INFRA.md` | Farm deployment. Still valid infra. |
| `09-HERMES-ORCHESTRATION.md` | Hermes coordination. Mostly valid. |
| `10-FULL-SPEC.md` | Comprehensive module inventory. Still useful reference. |
| `11-BLOGREF.md` | Blog codebase reference. Still factual. |
| `12-SANSKRIT-FACTORY.md` | Sanskrit translation pipeline. Still valid. |
| `13-FLAWS.md` | Risk assessment. Still valid. |
| `14-VISIONARY.md` | Best-case pathways. Still aspirational. |
| `15-GREENSCREEN.md` | Platform thesis. Separate concern. |
| `16-GTM.md` | Go-to-market. Separate concern. |
| `17-VIDEO-FACTORY-HITL.md` | Review system. Separate concern. |
| `18-ANAKHRARENDER.md` | Render pipeline. Separate concern. |

---

## Data

| Path | Contents |
|------|----------|
| `content/source-metaphysics/` | 16 question dossiers (6 original + 10 argument-style). |
| `content/information-packets/` | Test amplituhedron packet + Nanavira claims + gate report. |
| `content/source-texts/nanavira-fundamental-structure/` | Full text of both essays + SO metadata. |

---

## Codex Handover

| File | What It Is |
|------|------------|
| `CODEX-TRUTHMAP-SEED.md` | Arxiv papers + engine implementation plan. |
| `CODEX-RESEARCH-SEED.md` | Research seed: T-AIF, GraphRAG, stack graphs. |

---

## Key Metrics

| Metric | Current |
|--------|---------|
| Passing tests | 27 |
| Question dossiers | 16 |
| Source texts imported | 1 (Nanavira) |
| Evidence dimensions | 3 (phenomenological, empirical, contemplative) |
| Discriminators | 5 (D1-D5), 60-cell branch-effect matrix |
| Engine files | `truthengine-propagation.py` + `truthengine_working.py` + `truthengine_d1.py` |
| Gate lines | 548 |
| Zero EOs | Still the critical gap |
