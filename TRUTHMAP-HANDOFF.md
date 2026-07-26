# Truth Map Handoff For Next Agent

Date: 2026-07-26

This handoff describes the current Truth Map engine state, what was built, why it matters, what is still risky, and the next granular development steps.

## Project Purpose

The project is not trying to prove "reality is X" by force of posterior math. It is trying to support serious, refutation-led inquiry into questions like:

- Is consciousness fundamental?
- Is reflexive awareness intrinsic or constructed?
- What does brain dependence falsify, and what does it not falsify?
- Where do Abhinavagupta, Dharmakirti, Nanavira, IIT, neuroscience, and mathematical physics genuinely meet or break apart?

The right standard is Popper/Deutsch-like:

- ask hard-to-vary questions
- state candidate explanations
- identify cruxes and falsifiers
- track evidence provenance
- expose interpretive assumptions
- treat unresolved boundaries as findings, not failures

The engine should make the current state of play inspectable. It should not hide contested interpretation behind clean-looking decimals.

## Current Architecture

The active loop now has four layers:

```text
source text / paper
  -> extracted claims
  -> Nyaya gate and NNExpr metadata
  -> argument fabric rows
  -> graph-derived state of play
  -> optional numeric truth-map update when safe
```

Main components:

- `truthengine_working.py`
  Numeric propagation engine, multi-dimension tracking, contribution trace, and optional argument-schema bootstrap.

- `truthmap-argument-schema.sql`
  Additive argument-fabric schema: source spans, argument nodes/edges, gate results, fallacy checks, falsifiers, formal links, bridge controls, structural correspondences, critique pairs, and state-of-play snapshots.

- `scripts/nyaya-truthmap-gate.py`
  Conservative claim gate using Nyaya-style fallacy checks, falsifier requirements, tradition scope, formal/bridge caution, and NNExpr parse metadata.

- `scripts/ingest-packet.py`
  Packet ingestion. Runs the gate, stores provenance/gate rows, stores argument nodes, and only updates runtime posteriors when the gate permits it.

- `scripts/ingest-dossier.py`
  Dossier and source-map ingestion. Builds candidates, cruxes, falsifiers, structural correspondences, critique pairs, and argument edges.

- `scripts/state-of-play.py`
  Deterministic graph-derived synthesis. Produces current best answer, live/defeated candidates, cruxes, bidirectional critiques, unresolved correspondences, and high causal-power edges.
  Candidate weakening/defeat now requires confirmed falsifiers or explicit attacks on hard-to-vary core commitments.

- `scripts/provenance-report.py`
  Query layer for contribution/blame reports from propagation traces.

- `scripts/probe-bridge.py`
  Conservative bridge probe wrapper. Reads source-map bridge tests and negative controls; never upgrades to `BRIDGES` without bidirectional proof and passing negative controls.

- `scripts/validate-objects.py`
  Object validator for EOs, ROs, dossiers, typo traps, duplicate IDs, and missing falsifiers.

## What Was Built

### 1. Gate-integrated packet ingestion

`ingest-packet.py` no longer has to bypass the Nyaya gate. It can:

- apply the argument schema through `build_truth_map_db(..., argument_schema=True)`
- validate every claim with the gate
- store `claim_gate_results`
- store `hetvabhasa_checks`
- store `tarka_falsifiers`
- store `argument_nodes`
- preserve source-span metadata
- block posterior updates for hollow/refuted/non-updating claims
- still record non-updating argument claims for state-of-play use

Why this matters:

The engine can now say "this claim matters dialectically but should not move a posterior." That is essential for philosophical/scientific boundary cases.

### 2. NNExpr parsing inside the gate

`scripts/nyaya-truthmap-gate.py` now parses `claim["nn_expr"]` when present.

It stores:

- attempted status
- original expression
- normalized expression
- parsed tree
- parse status
- parse notes

ASCII aliases such as `vyapti(...)` are normalized to parser-compatible forms.

Policy:

- ordinary claims do not require NNExpr
- invalid NNExpr is visible but not automatically blocking for ordinary claims
- invalid NNExpr blocks claims asking for formal or bridge status
- parse success is metadata, not proof

Why this matters:

This prevents "bridge candidate" claims from getting upgraded just because they sounded formal. Syntax is not validation.

### 3. Nanavira/reflexivity argument fabric

The Nanavira source text now has a working path:

```text
Nanavira source text
  -> information packet
  -> gate results
  -> argument dossier/source map
  -> state-of-play synthesis
```

The current graph-derived verdict is:

```text
Structural reflexivity is strengthened locally.
Universal consciousness is not entailed.
Abhinavagupta is pressured at universalization.
Abhinavagupta pressures Nanavira at manifestness.
Nanavira/Dharmakirti is OVERLAPS, not BRIDGES.
```

Why this matters:

This is the first case where the system does something useful without pretending a metaphysical debate should create naive posterior movement.

### 4. State-of-play red-team fix

The first state-of-play scorer overclaimed. It listed every candidate "Under Pressure" because it treated:

- open cruxes
- declared falsifiers
- direct attacks

as if they were the same kind of negative evidence.

This is now fixed:

- crux pressure is separate from direct pressure
- pending falsifiers are pending tests, not evidence
- only active falsifier statuses such as `tested_failed` count as direct pressure
- candidates are not weakened merely because an open crux bears on them

Why this matters:

This is exactly the pseudo-precision failure mode the project is trying to avoid.

### 5. Generic source-map ingestion

`scripts/ingest-dossier.py` now supports generic source-map arrays:

```text
structural_correspondences[]
directional_critique_pairs[]
```

Ingestion writes those arrays directly. The old Nanavira-specific bridge/critique backfill has been removed; new source maps must carry their own correspondence and critique rows as data.

Why this matters:

The next debate should not require editing Python just to add bridge/correspondence/critique rows.

### 6. Bridge probe wrapper

`scripts/probe-bridge.py` now evaluates source-map bridge logic conservatively.

It returns:

- `BRIDGES` only when bidirectional positive probes are `PROVED` and negative controls do not fail
- `SUBSUMES` when only one positive direction is proved
- `DIFFERENT` when a negative control fails
- `OVERLAPS` when shared structure exists but proof is missing
- `needs_review` when there is no shared structure or useful probe result

The current Nanavira/Dharmakirti bridge evaluates to `OVERLAPS`.

Why this matters:

Bridge upgrades are the most dangerous source of false convergence across traditions. This wrapper creates a testable bottleneck before any future merge.

### 7. Object validation

`scripts/validate-objects.py` catches:

- duplicate EO IDs
- RO typo `bears_on_quequestions`
- missing candidate falsifiers
- malformed argument dossiers

The canonical EO layout is now the directory form:

```text
content/essay-objects/{eo-slug}/eo.json
```

The duplicate flat `eo-reflexivity-structural-local-v1.json` was removed after its stronger/currenter content was copied into the canonical directory EO.

## Tests And Verification

Last verified commands:

```bash
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest discover -v
```

Result:

```text
54 tests OK
```

Compile check:

```bash
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m py_compile \
  scripts/nyaya-truthmap-gate.py \
  scripts/ingest-packet.py \
  scripts/state-of-play.py \
  scripts/ingest-dossier.py \
  scripts/validate-objects.py \
  test_nyaya_gate.py \
  test_state_of_play.py \
  test_ingest_dossier.py \
  test_object_validation.py
```

Result: passed.

Whitespace check:

```bash
git diff --check
```

Result: passed.

Object validator:

```bash
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 scripts/validate-objects.py --json
```

Result: passed with `[]`.

Do not run live extraction unless API/network access is intended. The extraction path requires external calls.

## Current Red-Team Risks

### Weight assignment is still authored

Weights like `w_rel`, `w_map`, `w_aux`, and authored edge strengths are still interpretive judgments. The project mitigates this by making them visible, not by pretending they are objective measurements.

Next required honesty layer:

- reviewer ledger
- disagreement tracking
- weight rationale fields
- acquisition log of searched/rejected sources

### Source selection bias is still mostly invisible

The engine can track ingested evidence, but not yet:

- what was searched
- what was rejected
- what was unavailable
- what tradition/language coverage is missing

This is a major risk for cross-tradition metaphysics.

### Bridge status is now conservatively probed, not formally proved

The system can store:

```text
BRIDGES
SUBSUMES
CONTRADICTS
OVERLAPS
DIFFERENT
```

`scripts/probe-bridge.py` can compute a conservative status from declared probe results and negative controls. It does not run Lean/Sanskritree proofs yet.

Current Nanavira/Dharmakirti status is correctly conservative: `OVERLAPS`.

### NNExpr parsing is only syntax

`abheda(duration,invariance)` parsing does not prove duration and invariance are equivalent.

Do not let UI/reporting phrase parse success as validation.

### State-of-play synthesis is still heuristic, but candidate status is stricter

The synthesis is deterministic and graph-derived. Candidate weakening/defeat now requires confirmed falsifiers or explicit hard-to-vary-core attack metadata, so generic attacks and open cruxes do not silently defeat candidates.

Still missing:

- undercutter handling
- candidate reformulation lineage
- explicit core commitment nodes
- reviewer status for attack quality

### Repo worktree is dirty

There are many modified, deleted, and untracked files outside the immediate Truth Map changes. Treat them as user/other-agent work unless proven otherwise. Do not revert them casually.

### Security note

Earlier review noted a local origin remote with an embedded GitHub token. Do not print it. Rotate it and change the remote to a tokenless URL if it is still present.

## Next Granular Dev Steps

### P0. Canonical EO layout - done

Decision:

```text
Use directory form as canonical:
content/essay-objects/{eo-slug}/eo.json
```

Completed:

1. Copied the stronger flat EO content into the canonical directory EO.
2. Deleted the duplicate flat EO JSON.
3. Confirmed `scripts/validate-objects.py --json` now returns `[]`.
4. Existing duplicate-ID regression test still guards against this recurring.

Why:

EO compilation and loading must be deterministic. Duplicate IDs break that.

### P0. Convert Nanavira source map to generic arrays - done

File:

```text
content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.nanavira-map.json
```

Completed:

1. Added explicit `structural_correspondences[]`.
2. Added explicit `directional_critique_pairs[]`.
3. Removed Nanavira-specific correspondence/critique fallback code.
4. Added tests for generic ingestion and bridge-node creation.

Why:

The engine should ingest new debates as data, not as custom code.

### P0. Enforce generic source-map validation - done

Implemented in `scripts/validate-objects.py`:

1. Detect `artifact_type == "argument_fabric_source_map"`.
2. Require `question_id`.
3. Require valid `structural_correspondences[]` if bridge/correspondence claims exist.
4. Require valid `directional_critique_pairs[]` if state-of-play delta asserts bidirectional pressure.
5. Validate correspondence `status` enum.
6. Validate critique `status` enum.
7. Add positive and negative tests in `test_object_validation.py`.

Why:

Without validation, generic ingestion exists but malformed maps can silently degrade the graph.

### P0. Add hard-to-vary candidate status rules - first pass done

Current scorer knows support, crux pressure, direct pressure, pending falsifiers, confirmed falsifiers, core attacks, and decisive core attacks.

Implemented edge payload fields:

```json
{
  "targets_core_commitment": true,
  "core_commitment_id": "core:...",
  "attack_gate_status": "accepted",
  "candidate_has_live_reformulation": false
}
```

Candidate status rules:

- `live`: default when not defeated
- `weakened`: direct accepted attack on hard-to-vary core, or tested falsifier failed but reformulation remains
- `defeated`: tested/accepted decisive attack on hard-to-vary core, no live reformulation, no successful undercutter
- `outside_formal`: still tracked as pressure/boundary, not as defeat

Why:

"Under pressure" must mean something stricter than "there is an open question."

Still needed:

- store hard-to-vary core commitments as first-class nodes
- model undercutters explicitly
- track reformulation lineage instead of a single boolean

### P0. Build bridge probe wrapper - first pass done

Created:

```text
scripts/probe-bridge.py
test_bridge_probe.py
```

Inputs:

- left node
- right node
- declared bridge axioms
- negative controls
- optional Sanskritree proof-engine path

Output:

```json
{
  "status": "OVERLAPS|BRIDGES|SUBSUMES|CONTRADICTS|DIFFERENT|needs_review",
  "left_to_right": "PROVED|UNPROVED|REFUTED|OUTSIDE_FORMAL",
  "right_to_left": "PROVED|UNPROVED|REFUTED|OUTSIDE_FORMAL",
  "negative_controls": [...]
}
```

Implemented test cases:

```text
Nanavira difference vs Dharmakirti apoha -> OVERLAPS
bidirectional PROVED + negative controls pass -> BRIDGES
one-way PROVED -> SUBSUMES
negative control fails -> DIFFERENT
declared BRIDGES without proof -> downgraded to OVERLAPS
```

Why:

Bridge upgrades are the most dangerous source of false convergence.

Still needed:

- connect probe rows to real Sanskritree/Lean proof output
- persist probe results into `structural_correspondences`
- make validator warn/error when declared correspondence is stronger than probe result

### P1. Reviewer and acquisition ledgers

Add schema tables:

```text
acquisition_runs
acquisition_candidates
claim_reviews
weight_reviews
reviewer_disagreements
```

Add minimal commands:

```text
scripts/log-acquisition.py
scripts/review-claim.py
scripts/review-weight.py
```

Track:

- query/source acquisition route
- accepted/rejected reason
- reviewer identity or role
- weight assignments and rationale
- disagreement between reviewers

Why:

This is the answer to circular weight assignment and selection bias.

### P1. Expand provenance/blame reporting

Current contribution trace can rank source movement. Expand it into full paper blame:

```text
paper -> claims -> targets -> weights -> effective_lbf -> posterior change -> branch effects
```

Useful commands:

```text
scripts/provenance-report.py --source-id ...
scripts/provenance-report.py --target-id D4
scripts/provenance-report.py --branch-id B3
scripts/provenance-report.py --question-id ...
```

Why:

The provenance graph is not a nice-to-have. It is what makes the system intellectually honest.

### P1. Compile graph-derived EO drafts

Create:

```text
scripts/compile-eo.py
test_compile_eo.py
```

Input:

```text
question_id
state-of-play synthesis
candidate graph
source spans
strongest argument edges
open cruxes
next tests
```

Output:

```text
content/essay-objects/{eo-slug}/eo.json
```

Do not generate polished prose yet. Generate rigorous draft EO JSON that a human can edit.

Why:

This is the moment the system becomes useful as a research assistant rather than just an internal graph.

### P2. Use ML carefully

Good ML uses:

- retrieval over papers/source texts
- candidate claim extraction
- entity/term disambiguation suggestions
- clustering possible duplicate nodes
- finding likely support/attack edges for human review
- active learning for "which source should we inspect next?"

Bad ML uses:

- final bridge merge decisions
- hidden weight assignment
- automatic metaphysical posterior updates
- treating embeddings as ontology

Policy:

ML can propose. The gate, provenance, negative controls, and reviewer ledger decide whether anything updates.

### P2. Production hardening

Needed before treating this as stable:

- schema migrations instead of ad hoc SQL loading
- explicit DB path/env handling
- transaction boundaries around ingestion
- idempotency tests for ingestion
- CLI help examples for every script
- fixture factories for packet/dossier/map tests
- CI command that runs unittest, compile, diff-check, and object validator
- structured logs for ingestion/gate decisions
- no secret/token in remotes or logs

## Recommended Reading Order For Next Agent

1. `TRUTHMAP-HANDOFF.md`
2. `truthnext.md`
3. `docs/active/TRUTHMAP-PURPOSE.md`
4. `docs/active/truthreview.md`
5. `docs/active/truthadvanced.md`
6. `docs/active/TRUTH-TEST.md`
7. `truthmap-argument-schema.sql`
8. `truthengine_working.py`
9. `scripts/nyaya-truthmap-gate.py`
10. `scripts/ingest-packet.py`
11. `scripts/ingest-dossier.py`
12. `scripts/state-of-play.py`
13. `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json`
14. `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.nanavira-map.json`
15. `test_ingest_packet.py`, `test_nyaya_gate.py`, `test_ingest_dossier.py`, `test_state_of_play.py`

## High-Level Path From Here

The project should mature in this order:

```text
canonical objects [done]
  -> generic validated source maps [done]
  -> bridge probes with negative controls [first wrapper done]
  -> hard-to-vary candidate status rules
  -> acquisition/reviewer ledgers
  -> provenance/blame reports
  -> EO compiler
  -> graph UI / research agent loop
```

Why this order:

1. Canonical objects stop identity drift.
2. Generic maps stop debate-specific code from hardening into architecture.
3. Bridge probes prevent false convergence across traditions.
4. Candidate status rules stop "interesting objection" from becoming "defeat."
5. Reviewer/acquisition ledgers expose selection bias and weight circularity.
6. Provenance reports make every belief update traceable.
7. EO compilation gives humans a useful artifact.
8. UI/agent work should wait until the semantics are honest enough to display.

## Bottom Line

The system is now past a toy Bayesian engine. It has a working argument-fabric loop and a first useful case study. The immediate danger is overclaiming: bridge merges, candidate defeat, and numeric weights must remain auditable and conservative.

The next agent should prioritize boring correctness over new theory. Resolve canonical objects, validate generic maps, probe bridges, and make candidate defeat rules stricter. That is what will let the project answer "what is our best current understanding of reality?" without pretending the answer is cleaner than the evidence.
