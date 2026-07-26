# Onboarding — New Agent Reading Order

Read these in order. Each builds on the previous.

## 1. Project Context

| File | Why |
|------|-----|
| `RESEARCH_DIRECTIVE.md` | Master research programme. 72 questions, 5-level inquiry, 7-step dialectical procedure. Read this first. |
| `tractatus-conscientiae.md` | Level 0 metaphysics: S => (0 <-> 1), six branches B1-B6. Foundational. |
| `VISION.md` | Current vision: refutation-led research ledger, not Bayesian oracle. |

## 2. Current Architecture

| File | Why |
|------|-----|
| `TRUTHMAP-ARGUMENT-FABRIC.md` | **Current architecture.** 5-layer system: source → formal → argument → evidence → reality brief. 422 lines. |
| `truthchanges5.md` | Refutation-led redesign. Dethrones Bayesian oracle. Atomic unit is question → candidates → cruxes → surviving answer. |
| `TRUTHCHANGES6.md` | Nyāya logic framework: 4 pramāṇas, 5 hethābhāsas, 5-member syllogism, tarka falsifiers. |

## 3. Current Specs

| File | Why |
|------|-----|
| `EO-v2.md` | EO as Nyāya 5-member syllogism + candidates + state of play. |
| `RO-v2.md` | RO as faithful passage library. Simplified. |

## 4. What's Built

| File | Why |
|------|-----|
| `TRUTHMAP-PROGRESS.md` | Doc quality ratings, codebase organization, key metrics, gaps. |
| `TRUTHPLAN.md` | Direction guide: what exists, what's blocking, priorities. |
| `ROADMAP.md` | Development phases. Current: Phase 1 (integration). |
| `TRUTH-TEST.md` | Test protocol: 30 tests covering gate, propagation, dimensions, adversarial. |
| `TRUTHMAP-PRODUCTION-HARDENING.md` | Production rules: show vectors, falsifiers required, tradition-scope. |

## 5. Handovers

| File | Why |
|------|-----|
| `truthreview.md` | Latest lead-agent review. Bugs found, build direction, gaps against directive. Read this before building. |
| `truthadvanced.md` | Previous architecture review. Sprint plan. |

## 6. Codex Seeds

| File | Why |
|------|-----|
| `CODEX-RESEARCH-SEED.md` | Relevant papers: T-AIF argument graphs, GraphRAG, stack graphs. |
| `CODEX-TRUTHMAP-SEED.md` | Arxiv papers for truth map calibration + implementation plan. |

## 7. Engine Files (Active Code)

| File | Why |
|------|-----|
| `truthengine-propagation.py` | Bayesian math core: sigmoid, log_odds, paradigm crowding, PropagationEngine. |
| `truthengine_working.py` | SQLite runtime: F1-F8, D1-D5, B1-B6, 3 evidence dimensions, convergence, provenance. |
| `scripts/nyaya-truthmap-gate.py` | Pre-ingestion gate: pramāṇa, hethābhāsa, falsifiers, tradition scope. |
| `scripts/ingest-packet.py` | Gate-aware packet ingestion. |
| `scripts/state-of-play.py` | State-of-play report from dossiers (fallback to JSON, graph-derived coming). |
| `scripts/provenance-report.py` | Blame reports per source/target/dimension. |
| `scripts/logic/bnf.py` | NNExpr BNF grammar parser (from sanskritree). |

## Quick Start

```bash
# Run tests
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest discover -v

# See state of a question
PYTHONPATH=. python3 scripts/state-of-play.py --question-id q:reflexivity-intrinsic-or-constructed

# List all available questions
PYTHONPATH=. python3 scripts/state-of-play.py --question-id ""
```
