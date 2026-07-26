# DEV25 — Next 5 Steps: Grunt Work → Codex Insight

Handover for Codex (GPT-5.6 high-reasoning). I've done all the file-grubbing, template-drafting, and context-gathering. Below are 5 steps with what's already prepared and exactly where your reasoning is needed.

---

## Step 1: `specs/EO.md` — Essay Object Granular Spec

**Grunt work done:**
- Read all source context: `magnum-opus/04-ESSAY-OBJECTS.md` (EO schema), `10-FULL-SPEC.md` (factory pipeline), `25-ARCHITECTURE.md` (data model), `13-FLAWS.md` (risk: zero EOs exist, critical gap)
- Wrote full `specs/RO.md` as a template (same format: JSON Schema + validation rules + versioning + storage + access + migration)
- Extracted EO schema from `04-ESSAY-OBJECTS.md` lines 12-59

**Delivered:**
- `specs/EO.md` [attached] — full spec with schema, 10 validation rules, versioning table, D1 index SQL, access pattern matrix, migration policy

**Needs Codex insight:**
- Review the `hypotheses[]` structure — is the confidence enum (strong/moderate/speculative) sufficient, or should it use the propagation engine's log-odds?
- The `tension_point` field is the core of an EO — is the current string format enough, or does it need structured fields (claim_a, claim_b, shared_assumptions)?
- Should EO creation trigger automatic truth map question creation, or is that a separate manual step?

---

## Step 2: `specs/TRUTH-MAP-QUESTION.md` — Truth Map Question Spec

**Grunt work done:**
- Identified 3 conflicting schemas currently in the codebase:
  - **Schema A** (actual `q-*.json` files in `content/source-metaphysics/`): flat structure with `confidence`, `evidence_for[]`, `evidence_against[]`, `best_answer`
  - **Schema B** (`magnum-opus/05-SOURCE-METAPHYSICS.md`): adds `scope`, `family`, richer evidence entries
  - **Schema C** (`truthengine.md` + `truthengine-propagation.py`): uses `ClaimRecord(target_feature_ids, log_bayes_factor, w_rel, w_map, w_aux, paradigm)` — completely different model
- Read the 6 actual q-*.json files to see the current state
- Read `truthengine-propagation.py` (276 lines) to understand the propagation math
- Read `truthengine.md` (169 lines) for the Deutsch vs Bayes framework
- Documented the inconsistency in detail with a 3-way comparison table

**Delivered:**
- `specs/TRUTH-MAP-QUESTION.md` [attached] — draft spec with the reconciliation problem clearly stated, proposed unified schema, validation rules

**Needs Codex insight:**
- **The core design question:** The truth map question has 3 incompatible implementations. Which model should win?
  - Option A: Keep q-*.json as the source of truth, adapt propagation engine to consume them
  - Option B: Adopt the ClaimRecord model as primary, generate q-*.json as a view
  - Option C: Hybrid — questions are git files, claims are D1 records, propagation reads both
- The falsifier field: every claim needs a testable falsifier. How should this be structured in the JSON/D1 schema?
- Branch derivation: the current math derives branch probabilities from feature posteriors (product/sigmoid). Is this theoretically sound, or does it conflate independent evidence?

---

## Step 3: `specs/CLAIM.md` — The Atomic Evidence Unit

**Grunt work done:**
- Read `truthengine-propagation.py` lines 74-113 for the ClaimRecord dataclass (id, target_feature_ids, log_bayes_factor, w_rel, w_map, w_aux, paradigm, is_retracted)
- Read `truthengine.md` for the publish gate, append-only rule, staleness check
- Read `magnum-opus/05-SOURCE-METAPHYSICS.md` for the evidence array structure
- Read the actual q-*.json files to see how evidence is currently stored
- Identified that claims exist conceptually everywhere but have zero concrete schema

**Delivered:**
- `specs/CLAIM.md` [attached] — full spec with ClaimRecord JSON schema, weight computation formula, D1 evidence_log table SQL, append-only enforcement, falsifier sub-schema

**Needs Codex insight:**
- The weight tuple (w_rel × w_map × w_dep × w_aux × lbf) is mathematically simple but philosophically loaded. Are the weight factors correctly scoped? Does w_dep (paradigm dependence discount) need dynamic computation based on the current claim pool?
- The `supersedes` chain: when claim B supersedes claim A, should the propagation engine re-run from scratch or just delta-update? The current engine supports both modes — which is correct for the live loop?
- How should claims extracted from AI-generated content (EOs → essays → videos) be weighted differently from claims extracted from peer-reviewed sources?

---

## Step 4: Propagation Engine → D1 Integration

**Grunt work done:**
- Read `truthengine-propagation.py` (276 lines) — full PropagationEngine class, FeatureState, ClaimRecord, derive_branch_probs
- Read `truthengine-db.py`, `truthengine-schema.sql`, `truthengine-migrate.py` (referenced in REF.md but may be incomplete)
- Read `25-ARCHITECTURE.md` §4 Persistence Layer — D1 table list (truth_map, evidence_log, user_profiles, edge_weights, etc.)
- Read `25-ARCHITECTURE.md` §10 Complete Data Flow diagram
- Read `magnum-opus/08-FARM-INFRA.md` for the D1 schema approach

**Delivered:**
- `specs/DB-INTEGRATION.md` [attached] — D1 schema SQL for `truth_map_questions`, `evidence_log`, `feature_states`, `branch_probabilities` tables; `PropagationDB` protocol implementation template using Cloudflare D1 client; full recompute vs incremental update orchestration

**Needs Codex insight:**
- The PropagationDB protocol has 7 methods. Which should be D1 queries vs in-memory operations? The D1 Worker has 30s CPU limit — will a full recompute fit?
- Branch normalization: the current code does `∑ raw_probs → normalize`. But branches are not a clean partition (they overlap). Is approximate normalization acceptable, or does this create artifacts?
- The `_load_paradigm_counts` method queries D1 per feature per paradigm. For a full recompute with 1000+ claims, this could be slow. Needs a bulk count query design.

---

## Step 5: Hypothesis Engine Design

**Grunt work done:**
- Read `magnum-opus/07-HYPOTHESIS-ENGINE.md` (63 lines) — full spec: scan truth map, rank by novelty/depth/freshness, generate EO proposals
- Read `13-FLAWS.md` §3 — "Hypothesis Engine Will Generate Garbage" (critical risk: produces same boring questions forever)
- Read `21-UNSAID.md` — "The Research Arm" pattern from hxrmxs (Shadow Model finds clusters, ThinkTank debates, Critic falsifies)
- Read `03-RESEARCH-OBJECTS.md` — RO quality scoring and family taxonomy
- Read `04-ESSAY-OBJECTS.md` — EO structure, lifecycle
- Extracted proposal JSON schema from `07-HYPOTHESIS-ENGINE.md` lines 37-52

**Delivered:**
- `specs/HYPOTHESIS-ENGINE.md` [attached] — proposal schema, ranking algorithm template (novelty scoring against existing EOs, RO disagreement detection, diversity sampling), 5 question sources, anti-staleness measures, Critic agent interface design

**Needs Codex insight:**
- The fundamental tension: the engine needs to be autonomous (no human in the loop) but garbage-free. The FLAWS doc says "constrain by RO disagreement detection, not gap scanning" — is this sufficient, or does it need a Critic agent at the proposal stage?
- Novelty scoring requires comparing a proposed question against ALL existing EOs. At 200+ EOs, this becomes an embedding similarity search. Should we use Cloudflare Vectorize, or a simple TF-IDF on the tension_point field?
- Diversity sampling: how to ensure the engine doesn't just generate Trika questions (because that's where most ROs exist) while ignoring Neoplatonism, Sufism, etc.? Should there be tradition quotas, or a multiplicative boost for underrepresented traditions?

---

## Summary: What I Did vs What Codex Needs To Do

| Step | Grunt (done by me) | Codex reasoning needed |
|------|-------------------|-----------------------|
| 1. EO spec | Full schema, rules, versioning, storage, migration | Hypotheses struct, tension_point format, auto-Q creation |
| 2. Truth Map Question | 3-schema conflict documented, unified proposal | Which model wins, falsifier design, branch derivation soundness |
| 3. Claim spec | Full schema from ClaimRecord, weight math, SQL | Weight factor scoping, supersedes chain behavior, AI-source weighting |
| 4. DB Integration | D1 schema SQL, protocol impl template, recompute orchestration | D1 30s limit feasibility, branch normalization artifacts, bulk count query |
| 5. Hypothesis Engine | Proposal schema, ranking template, question sources, anti-staleness | Autonomy vs garbage, novelty scoring method, tradition diversity |

## Files Referenced

```
content/source-metaphysics/q-*.json         — 6 actual truth map questions
truthengine-propagation.py                  — Propagation engine code (276 lines)
truthengine.md                              — Truth engine math and logic
truthengine-db.py / -schema.sql / -migrate.py — DB layer (may be stubs)
magnum-opus/03-RESEARCH-OBJECTS.md          — RO system spec
magnum-opus/04-ESSAY-OBJECTS.md             — EO system spec
magnum-opus/05-SOURCE-METAPHYSICS.md        — Truth map spec (Schema B)
magnum-opus/07-HYPOTHESIS-ENGINE.md         — Hypothesis engine spec
magnum-opus/10-FULL-SPEC.md                 — Full factory specs
magnum-opus/13-FLAWS.md                     — Risk assessment
magnum-opus/21-UNSAID.md                    — HXRMXS patterns, visions
magnum-opus/25-ARCHITECTURE.md              — Full engineering blueprint
magnum-opus/08-FARM-INFRA.md                — Cloudflare/D1 deployment
specs/RO.md                                 — Completed reference spec (same format)
GRANULAR-SPEC.md                            — Master directive
```
