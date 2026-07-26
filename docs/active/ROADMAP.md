# Development Roadmap

Ordered by dependency — each phase unlocks the next.

---

## PHASE 0: Foundation (Current)

The core pipeline must work before anything else matters.

### 0.1 Truth Engine (F1-F8 + D1-D5 + dimensions)
**Status:** ✅ Working — propagation, provenance/blame, convergence, 27 passing tests
**What it does:** Bayesian runtime with F1-F8 features, D1-D5 discriminators, B1-B6 branch support, 3 evidence dimensions (phenomenological, empirical, contemplative), dimension-specific paradigm crowding, provenance/blame reports.

### 0.2 Nyāya Gate
**Status:** ✅ Working — 548-line standalone validator
**What it does:** Pramāṇa inference, hethābhāsa fallacy checks, tarka falsifier generation, tradition scope enforcement, falsifier requirement. Python, standalone.

### 0.3 Argument Fabric Schema
**Status:** ✅ Designed — 290 lines SQL
**What it does:** Tables for source_spans, argument_nodes, argument_edges, claim_gate_results, hethābhāsa_checks, tarka_falsifiers, nigrahasthāna_events, formal_status_links, negative_bridge_controls, state_of_play_snapshots.

### 0.4 NNExpr Parser
**Status:** ✅ Imported — `scripts/logic/bnf.py` (72 lines) + `fol_lean_bridge.py` (125 lines)
**What it does:** Parses Navya-Nyāya expressions (vyāpti, abheda, catuskoṭi, prasaṅga, apoha) into structured logical forms. From sanskritree.

### 0.5 Question Dossiers
**Status:** ✅ 16 seeded (6 original + 10 new from RESEARCH_DIRECTIVE.md)
**What it does:** Argument dossiers with candidates, cruxes, falsifiers, state_of_play. Covering manifestation, consciousness, brain, individuation, perception, time, hard problem, Plato/Plotinus, AI.

### 0.6 Nanavira Source Import
**Status:** ✅ Full text imported + claims extracted + gate report + reflexivity map
**What it does:** First real source text through the pipeline. 5 claims accepted, 2 with penalty, bridge to Dharmakīrti apoha classified as OVERLAPS.

### 0.7 Test Suite
**Status:** ✅ 27 tests passing
**What it covers:** Gate validation, known-truth propagation (amplituhedron→D4, IIT→D3, brain damage→D3), dimension tracking, adversarial edge cases, end-to-end packet→gate→ingest→provenance.

### 0.8 Auto-Versioning Script
**Status:** ✅ `scripts/version-ro.py` ready
**What it does:** Automatic RO version bump detection via git diff. Major/minor/patch classification.

---

## PHASE 1: Integration (Next)

Wire the pieces into one working pipeline.

### 1.1 Gate-Aware Ingestion
**Status:** ❌ Not started
**Why:** `ingest-packet.py` bypasses the Nyāya gate. Argument schema tables exist as SQL but aren't loaded by `build_truth_map_db()`.
**Action:** Wire gate into `ingest-packet.py`, make argument schema loadable, prove end-to-end pipeline with Nanavira packet.

### 1.2 State-of-Play Synthesis
**Status:** ❌ Not started
**Why:** The system can track posterior movement but can't compute "which candidates are live, which cruxes are open, what to test next."
**Action:** `scripts/state-of-play.py` — deterministic candidate status rules from argument graph. No LLM.

### 1.3 First EO
**Status:** ❌ Not started — **critical gap**
**Why:** Zero EOs exist. Nothing for factories to consume. The reflexivity dossier is the best candidate.
**Action:** Convert reflexivity dossier + Nanavira map into an EO following `specs/EO-v2.md`.

### 1.4 Sanskritree Bridge Integration
**Status:** ❌ Not started
**Why:** Formal probe exists but NNExpr parsing, Lean types, bridge axioms not wired into argument status.
**Action:** Import term registry, negative controls, bridge probing logic from sanskritree.

---

## PHASE 2: Automation (Weeks 1-4 after Phase 1)

Once the pipeline works, make it fast and visible.

### 2.1 Provenance Graph
**Action:** CLI for per-source blame, per-target ranking, per-question candidate/crux/evidence views.
**Gate:** Phase 1 complete (gate-aware ingestion + state-of-play).

### 2.2 Dashboard
**Action:** HTML page reading `content/source-metaphysics/` and argument DB.
**Gate:** Phase 1 complete.

### 2.3 Reviewer Ledger
**Action:** `claim_reviews` table — weight correction deltas, reviewer identity, disagreement tracking.
**Gate:** 20+ reviewed information packets in the database.

### 2.4 Acquisition Ledger
**Action:** Tables for what was searched, what was excluded, tradition representation.
**Gate:** Phase 1 complete.

### 2.5 Publish Gate
**Action:** Enforce: every video/essay must update at least one truth map question.
**Gate:** EO pipeline running.

---

## PHASE 3: Scale (Month 2+)

### 3.1 Bulk Ingest
**Action:** Embed all 72 questions, find nearest papers from blog project corpus, extract and gate the top matches.

### 3.2 ML Calibration
**Action:** After 100+ reviewed packets, train weight correction model. Not before.

### 3.3 Bridge Probing
**Action:** Automated bridge discovery across traditions with negative controls.

### 3.4 Multi-Logic Engine
**Action:** Catuskoṭi for Nāgārjuna, syādvāda for Jaina claims, prasaṅga for Mādhyamaka critique. Logic dispatched per claim tradition.

---

## Current Blockers

1. **Gate not wired into ingestion** — packets go straight to engine without validation
2. **Zero EOs** — nothing for factories to consume
3. **Argument schema not loaded** — tables exist as SQL, not in runtime DB
4. **No state-of-play synthesis** — can't compute what's live vs weakened automatically
5. **Sanskritree not connected** — formal probe, NNExpr, bridge probing not wired in
