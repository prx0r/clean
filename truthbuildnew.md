# Truth Build New - Current Build Notes

## Current Build State

The project has crossed an important threshold: it is no longer just a design
document plus a Bayesian toy runtime. It now has a working gated ingestion path,
an argument-fabric schema, a first real source-text run, and a first EO.

The active shape is:

```text
source / packet
  -> Nyaya gate
  -> argument-fabric rows
  -> numeric runtime only for approved feature/discriminator targets
  -> provenance / delta
  -> EO-ready state of play
```

The engine is still not a metaphysical oracle. It is becoming an auditable
research operating system: source -> claim -> gate -> graph -> posterior movement
or boundary.

## What I Built

### 1. Gate-aware ingestion

`scripts/ingest-packet.py` now runs the Nyaya gate by default before inserting
claims into the runtime.

It now stores:

- `source_spans`
- claim metadata
- `argument_nodes`
- candidate/crux/bridge target edges
- `claim_gate_results`
- `hetvabhasa_checks`
- `tarka_falsifiers`
- optional `formal_status_links`

Only gated claims with runtime targets move the numeric engine:

```text
feature
discriminator
```

Argument-only targets do not move numeric posteriors:

```text
candidate_explanation
crux
bridge
```

This is the right split. It prevents Nanavira-style philosophical argument
claims from being forced into fake feature/discriminator movement.

### 2. Optional argument schema loading

`build_truth_map_db()` now accepts:

```python
build_truth_map_db(seed_claims=False, argument_schema=True)
```

When enabled, it applies:

```text
truthmap-argument-schema.sql
```

This keeps old tests/callers stable while letting ingestion and future state of
play code use the argument-fabric tables.

### 3. Nanavira gated ingestion proof

The second Nanavira run is saved at:

```text
content/information-packets/delta-nanavira-gated.json
```

Result:

```text
claims_seen: 7
runtime_claims_inserted: 0
argument_claims_recorded: 7
gate_results_stored: 7
gate_outcomes:
  accepted: 5
  accepted_with_penalty: 2
```

The key result is exactly what we wanted: Nanavira moved the argument graph, not
the numeric feature/discriminator runtime. No posterior moved because these
claims targeted candidates, cruxes, and bridges rather than D/F targets.

### 4. First EO

Created:

```text
content/essay-objects/eo-reflexivity-structural-local-v1.json
```

Conclusion:

```text
Structural reflexivity is locally strong; universal consciousness is not entailed.
```

This is the first factory-consumable artifact. It is scoped correctly:

- local structural reflexivity strengthened
- universal consciousness underdetermined
- Nanavira-Dharmakirti bridge remains overlap only
- manifestness remains the live crux

### 5. Tests added

Added:

```text
test_ingest_packet.py
```

It proves:

- argument schema can be loaded
- gated amplituhedron ingestion stores gate rows and moves D4
- gated Nanavira ingestion records argument graph rows without runtime movement

The active unittest discovery suite is now 30 tests passing.

## Parallel Work That Landed

The user/parallel pass added important pieces without overwriting the above.

### 1. NNExpr parser imported

New files:

```text
scripts/logic/bnf.py
scripts/logic/fol_lean_bridge.py
```

These came from Sanskritree and support the next formalization step:

- `vyapti`
- `abheda`
- `catuskoti`
- `prasanga`

Next use: the Nyaya gate should parse `claim["nn_expr"]` when present and store
parse status in the argument node payload or a future formal/logic table.

### 2. Legacy tests quarantined

The old broken validation files are now quarantined:

```text
truthengine-test-validation_legacy.py
truthengine-test-validation-v2_legacy.py
```

This is correct. They depended on missing fixtures and should not block active
unittest discovery.

### 3. Ten new argument dossiers seeded

The source-metaphysics directory now includes argument dossiers for:

- manifestation / abhasa
- consciousness
- brain relation
- individuation
- perception / production
- time / recognition
- hard problem
- Plato / Plotinus / idealism
- AI manifestness
- minimal awareness

These are argument-fabric seed material, not scalar question JSON. The question
loader now skips `artifact_type` files that are not old-style truth-map
questions, so these can safely live beside `q-*.json` files.

### 4. RO versioning script

New file:

```text
scripts/version-ro.py
```

It compares RO JSON against `git HEAD`, classifies changes, and bumps:

- major
- minor
- patch

This is the first stack-graph-style versioning primitive: each RO can become an
isolated subgraph that is rebuilt only when its file changes.

## Important Design Notes

### Argument claims and runtime claims are different

Do not collapse this distinction.

Runtime claims:

```text
target feature/discriminator
pass gate
may move posterior
must preserve weight decomposition
```

Argument claims:

```text
target candidate/crux/bridge
pass or fail gate
create graph pressure
do not automatically move posterior
```

This distinction is why Nanavira ingestion now behaves honestly.

### `UNPROVED` is not false

Sanskritree fast/dev probes currently return `UNPROVED` for many English claims.
This means:

```text
not proved by the current formal layer
```

It does not mean:

```text
refuted
```

Only `REFUTED`, `HOLLOW`, or a sustained argument attack should defeat a claim or
candidate.

### The dimensions are still split

Runtime dimensions:

```text
phenomenological
empirical
contemplative
```

Argument/gate dimensions:

```text
phenomenological
empirical
contemplative
formal
textual
analogical
```

Current ingestion maps `formal`, `textual`, and `analogical` to the
phenomenological runtime track only when a numeric update is actually allowed.
The original gate dimension is still stored in the gate/argument rows.

Longer term, we should decide whether runtime gets six dimensions or keeps three
broad posterior tracks plus finer `pramana` metadata.

### The source-metaphysics directory is mixed on purpose

It now contains:

- old scalar `q-*.json` question files
- argument dossiers
- source maps

`seed_questions_from_files()` skips non-question artifacts. Do not undo this.

## Current Verification Commands

Use these as the current build sanity check:

```bash
cd /root/projects/clean
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest discover -v
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m py_compile truthengine_working.py scripts/ingest-packet.py scripts/nyaya-truthmap-gate.py test_ingest_packet.py test_truthengine_working.py test_nyaya_gate.py
python3 -m json.tool content/essay-objects/eo-reflexivity-structural-local-v1.json
python3 -m json.tool content/information-packets/delta-nanavira-gated.json
git diff --check
```

Expected current result:

```text
30 tests passing
```

The user mentioned 27 tests after quarantining legacy files. That was true before
the gated-ingestion tests were added. Current discovery should be 30.

## What To Build Next

### P0 - State-of-play command

Build:

```text
scripts/state-of-play.py
```

Command:

```bash
python scripts/state-of-play.py --question-id q:reflexivity-intrinsic-or-constructed
```

It should query:

- `argument_nodes`
- `argument_edges`
- `claim_gate_results`
- `hetvabhasa_checks`
- `formal_status_links`
- runtime provenance where available

Output:

- current best answer
- live candidates
- weakened candidates
- defeated candidates
- open cruxes
- strongest supports
- strongest attacks
- unresolved bridges
- most causally powerful sources
- next tests

Start rule-based. Do not use an LLM until the graph query is deterministic.

### P0 - EO validation

Add:

```text
scripts/validate-eo.py
test_eo_validation.py
```

Minimum checks:

- 2+ candidates
- all five Nyaya syllogism members exist
- state of play includes `what_would_change_our_mind`
- every candidate has a falsifier
- resolution level is not global metaphysical unless lower levels are settled
- provenance points to existing files

This protects the factory boundary.

### P0 - Wire NNExpr parser into the gate

Now that `scripts/logic/bnf.py` exists, update the gate:

```text
if claim.nn_expr exists:
  parse it
  store parse status
  if parse fails -> needs_review
```

Do not require NNExpr for every claim yet. Require it only for claims that want
formal bridge status.

Add tests:

- valid `vyapti(difference,determination)`
- valid `abheda(duration,invariance)`
- invalid expression gets `needs_review`
- parser acceptance with no returned tree is recorded as boundary, not success

### P1 - T-AIF trust and commitment weights

Use `CODEX-RESEARCH-SEED.md` and T-AIF as the model.

Add actor/tradition tables:

```text
argument_actors
actor_trust_edges
actor_claim_commitments
```

This lets the graph say:

```text
Abhinavagupta is strongly committed to intrinsic vimarsa.
Dharmakirti is strongly committed to apoha / no enduring Self.
Nanavira is committed to structural reflexivity but not universal consciousness.
```

Do not mix this with source reliability. Actor commitment is not the same thing
as evidence quality.

### P1 - Stack-graph-style file indexing

Use `scripts/version-ro.py` as the start.

Needed tables:

```text
file_subgraphs
file_dependencies
subgraph_nodes
subgraph_edges
dirty_dependents
```

Rule:

```text
when SO/RO changes:
  rebuild only that file's subgraph
  mark dependents dirty
  do not auto-recompute EOs unless explicitly requested
```

This matches the stack graph paper and keeps large corpus updates sane.

### P1 - Bridge probing wrapper

Now that NNExpr import exists, wrap Sanskritree bridge probing:

```text
scripts/probe-bridge.py
```

Inputs:

- node A
- node B
- scoped assumptions
- negative controls

Outputs:

- `BRIDGES`
- `SUBSUMES`
- `CONTRADICTS`
- `OVERLAPS`
- `DIFFERENT`

Store the result in `argument_edges` and `formal_status_links`.

Nanavira difference vs Dharmakirti apoha should remain `OVERLAPS` until the
formal tests prove otherwise.

### P1 - Ingest the ten new dossiers

The ten new `*.argument.json` files are currently file artifacts. The next step
is a dossier ingestion script:

```text
scripts/ingest-dossier.py
```

It should create:

- candidate nodes
- crux nodes
- candidate/crux pressure edges
- initial state-of-play snapshot

This is different from claim packet ingestion. Do not force dossiers through the
claim gate unless they contain atomic claims.

### P2 - GraphRAG retrieval

Use the GraphRAG research seed as architecture, but keep storage simple first.

Start with SQLite:

- graph query for exact structured relations
- text search over source spans / claims / candidate statements
- later vector embeddings for fuzzy retrieval

The first useful query:

```text
Given a question, retrieve all candidate cores, live cruxes, gate-approved claims,
penalized bridge claims, and formal boundary nodes.
```

Only after this works should an LLM summarize.

### P2 - Dashboard

Minimum useful screens:

- question page
- candidate page
- source page
- claim page
- target page
- branch page

Every number must link to:

```text
source -> span -> claim -> gate -> target -> weights -> before/after -> branch delta
```

## Known Gotchas

### 1. Shell writes to `/root/projects/clean` may fail in this environment

Use `apply_patch` for repo file creation/edits. Direct shell writes to `/root`
can hit sandbox restrictions.

### 2. `scripts/version-ro.py --mode auto-bump` writes files

That is intended for normal local/pre-commit use, but tests should use temporary
files unless they explicitly verify repo mutation.

### 3. `claims` table now stores argument-only claims too

This is acceptable because numeric propagation reads through `claim_targets`,
which only contains feature/discriminator targets. Argument-only claims have no
runtime targets and do not move the engine.

Do not change propagation to read every row from `claims` directly.

### 4. `argument_nodes` target stubs are intentionally minimal

When packet claims target a candidate/crux/bridge that does not yet exist in the
DB, ingestion creates a stub node. Dossier ingestion should later replace/upgrade
those stubs with full candidate/crux payloads.

### 5. Penalized claims are still usable

`accepted_with_penalty` means:

```text
may update only with capped effect if it has runtime targets
always visible as a penalized argument claim
```

It does not mean rejected.

## Recommended Immediate Order

1. Build `scripts/state-of-play.py`.
2. Add EO validation tests.
3. Wire NNExpr parsing into the gate.
4. Build `scripts/ingest-dossier.py` for the ten new dossiers.
5. Add T-AIF actor/trust/commitment tables.
6. Add stack-graph file dependency tables around RO/SO versioning.
7. Build bridge probing wrapper.
8. Build the first simple dashboard or CLI report.

The project is now in implementation mode. The architecture is good enough to
build against.
