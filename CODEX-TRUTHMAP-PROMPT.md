# Codex — Truth Map Status & Handover

Read these files in order to get up to speed on the current truth map implementation:

## 1. Architecture & Vision

- `/root/projects/clean/magnum-opus/05-SOURCE-METAPHYSICS.md` — Original truth map concept (question taxonomy, status values, integration with factories)
- `/root/projects/clean/magnum-opus/10-FULL-SPEC.md` — Full system spec showing where truth map fits in the 4-factory model
- `/root/projects/clean/magnum-opus/25-ARCHITECTURE.md` — Engineering blueprint: data model, versioning, propagation engine, 3 loops (live/production/dreaming)

## 2. Latest Truth Map Redesign (Discrimination Cascade)

- `/root/projects/clean/TRUTHMAP-REDESIGN.md` — **The redesign doc.** Replaces flat F1-F8 Bayesian board with a D1-D5 discrimination cascade over 6 branches (B1-B6). Contains the calibrated 60-cell branch-effect matrix, feature-to-discriminator mapping table, EIG-based question selection, convergence policy, and implementation plan with SQL.
- `/root/projects/clean/CODEX-TRUTHMAP.md` — Codex's design decisions from the redesign session. Fixed v1 mapping, derived update rule with ±0.6 cap, conservative extraction prompt with lbf caps, EIG selection tie-breakers.

## 3. Propagation Engine (Current Implementation)

- `/root/projects/clean/truthengine-propagation.py` — Math core: sigmoid, log_odds, `compute_dep_weight`, `FeatureState`, `ClaimRecord`, `PropagationEngine` with full recompute and incremental update modes. 304 lines.
- `/root/projects/clean/truthengine_working.py` — SQLite runtime wrapping the propagation engine. D1-shaped schema, 6 seeded questions (`q:consciousness-fundamental`, `q:brain-filter-or-appearance`, etc.), 8 seed claims, `build_truth_map_db()`, `PropagationEngine.run()` with D1 persistence. 654 lines.
- `/root/projects/clean/test_truthengine_working.py` — 6 passing happy-path tests (seeded run, incremental update, incremental=full recompute, paradigm dependence, paradigm independence, retraction). 147 lines.
- `/root/projects/clean/REDTEAM-TRUTHMAP.md` — Attack vectors for breaking the engine (math edge cases, logical pathologies, incremental consistency, data integrity, performance).

## 4. Evidence Pipeline (Paper → Truth Map)

- `/root/projects/clean/EVIDENCE-PIPELINE.md` — Paper → Information Packet JSON → Review → D1 Ingestion → Delta. Schema for information packets, extract/ingest scripts needed, test with 3 papers at different confidence levels.
- `/root/projects/clean/scripts/` — (check if extract-claims.py and ingest-packet.py exist yet)

## 5. Critical Issues

- **3 conflicting schemas** (`BUILD-NOTES.md` line 109): The actual q-*.json files, the magnum-opus spec, and the ClaimRecord model all disagree on what a truth map question is. This must be resolved before D1-D5 integration.
- **No EOs exist** (FLAWS.md risk #1): The entire architecture hinges on Essay Objects. Zero exist.
- **D1-D5 not yet in engine**: The propagation engine only handles F1-F8 feature states. D1-D5 discriminators, discriminator_branch_effects table, and branch_support() recompute are not implemented.

## Current Task Queue

1. Align the 3 conflicting schemas
2. Add discriminator tables + seed data to engine
3. Implement branch_support() combining discriminator effects + feature projection
4. Extend claim target mapping to support both features and discriminators
5. Add EIG-based next-question selection
6. Write red-team tests for the attack vectors in REDTEAM-TRUTHMAP.md
