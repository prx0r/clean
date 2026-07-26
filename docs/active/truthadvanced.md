# Truth Advanced - Lead Agent Review

## Executive Verdict

The project is now two systems that need to be joined.

1. A working evidence runtime:
   source claims -> weighted feature/discriminator updates -> branch support -> provenance/blame reports.

2. A newer argument fabric:
   source spans -> Nyaya gate -> claims -> argument nodes -> supports/attacks/bridges -> candidate status -> state of play.

The first system can compute and explain posterior movement. The second system is the right philosophical architecture, but it is mostly files, schema, and standalone tools. The main missing work is not more theory. It is integration: every claim must pass through the argument gate before the numeric engine can update anything, and every numeric movement must be visible inside the state-of-play graph.

The core purpose is:

```text
Ask pressure-bearing questions about reality.
Build the strongest live candidate explanations.
Try to break them.
Track what survives, what failed, what moved, and what would change our mind.
Use numbers only as audited bookkeeping, not as metaphysical verdicts.
```

## What The Project Is Actually Doing

The truth map is not a truth oracle. It is an adversarial research ledger.

It tracks:

- questions that matter
- candidate explanations
- cruxes where candidates diverge
- claims from texts, papers, arguments, experiments, and practice reports
- validation status for each claim
- weight decomposition for evidence that is allowed to update posteriors
- provenance from source -> claim -> target -> posterior movement
- formal boundaries from Sanskritree/Lean
- current best state of play

The best output is not:

```text
B4 = 0.73, therefore consciousness-first metaphysics is true.
```

The best output is:

```text
On this question, these candidates remain live.
This claim supports candidate A but only in the phenomenological dimension.
This criticism weakens candidate B's universalization step.
This bridge between traditions is only an overlap until formal probes pass.
This experiment would most reduce uncertainty.
```

## Current Architecture

The current architecture has five layers.

| Layer | Current role | Status |
| --- | --- | --- |
| Source layer | stores exact source texts, papers, spans, translations | partial |
| Formal layer | Sanskritree/Lean proof and boundary detection | available, not integrated |
| Argument layer | Nyaya gate, candidates, cruxes, support/attack/bridge edges | designed, partly materialized |
| Evidence layer | Bayesian runtime over F1-F8, D1-D5, B1-B6 | working prototype |
| Reality brief layer | state-of-play synthesis and next tests | designed, not automated |

The correct data flow should be:

```text
SO / paper / text
  -> source spans
  -> extracted claims
  -> Nyaya gate
  -> argument nodes and edges
  -> numeric updates only for approved feature/discriminator targets
  -> provenance trace
  -> state-of-play snapshot
  -> EO / essay / dashboard
```

Right now the actual code path is closer to:

```text
packet claims
  -> ingest-packet.py
  -> truthengine_working.py
  -> posterior movement
```

And the newer argument path is:

```text
packet claims
  -> nyaya-truthmap-gate.py
  -> JSON gate report
  -> manual argument map JSON
```

These paths are parallel. They are not yet one pipeline.

## What Is Working

### 1. The numeric propagation runtime exists

Active files:

- `truthengine-propagation.py`
- `truthengine_working.py`
- `test_truthengine_working.py`
- `scripts/provenance-report.py`

It supports:

- F1-F8 feature posteriors
- D1-D5 discriminator posteriors
- B1-B6 branch support
- direct discriminator targets
- feature-to-discriminator derived mappings
- branch-effect multipliers
- dimension-specific evidence tracks
- dimension-specific paradigm crowding
- convergence diagnostics
- source/target blame traces
- before/after posterior records
- branch support deltas

Important correction: older docs say D1-D5 is missing. That is stale. The current runtime has D1-D5 tables, 60 branch-effect multipliers, feature-to-discriminator mapping, and tests for direct/derived discriminator behavior.

### 2. Provenance/blame is real

`scripts/provenance-report.py` can already answer questions like:

```bash
python scripts/provenance-report.py --source-id arxiv:1312.2007
python scripts/provenance-report.py --target-id D4
python scripts/provenance-report.py --target-id D4 --dimension empirical
```

The runtime can expose:

- claim id
- source id
- target id
- evidence dimension
- `log_bayes_factor`
- `w_rel`
- `w_map`
- `w_aux`
- computed `w_dep`
- `effective_lbf`
- posterior before
- posterior after
- branch support before
- branch support after
- branch support delta

This is the "git blame for beliefs" foundation. It is not a UI yet, but the data exists.

### 3. The Nyaya gate exists as a standalone validator

Active file:

- `scripts/nyaya-truthmap-gate.py`

It checks:

- claim targets
- tradition scope
- pramana
- evidence dimension
- hetu
- sadhya
- vyapti statement
- vyapti confidence
- falsifier presence
- hetvabhasa defects
- tarka falsifier generation
- optional Sanskritree formal probe

Current outcomes:

- `accepted`
- `accepted_with_penalty`
- `needs_review`
- `hollow`
- `outside_formal`
- `refuted`

This is directionally correct. It prevents naked claims from directly moving the engine.

### 4. The argument fabric schema exists

Active file:

- `truthmap-argument-schema.sql`

It adds:

- `source_spans`
- `argument_nodes`
- `argument_edges`
- `claim_gate_results`
- `hetvabhasa_checks`
- `tarka_falsifiers`
- `nigrahasthana_events`
- `formal_status_links`
- `negative_bridge_controls`
- `state_of_play_snapshots`

This is the right schema family. The problem is that the runtime does not yet create or consume these tables.

### 5. The first real source case exists

Nanavira's Fundamental Structure is now represented as:

- source text package
- claim packet
- gate report
- reflexivity source map

Active files:

- `content/source-texts/nanavira-fundamental-structure/`
- `content/information-packets/nanavira-fundamental-structure-claims.json`
- `content/information-packets/nanavira-fundamental-structure-gate-report.json`
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json`
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.nanavira-map.json`

The Nanavira result is a good model:

- five claims accepted
- two claims accepted with penalty
- bridge to Dharmakirti apoha classified as `OVERLAPS`, not merged
- formal probe returned `UNPROVED`, not false
- strongest update is local structural reflexivity, not universal consciousness

That is the right kind of restraint.

## What Is Not Working Yet

### 1. The gate is not wired into ingestion

`scripts/ingest-packet.py` currently inserts claims into the runtime without calling `nyaya-truthmap-gate.py`.

That means production ingestion can still bypass:

- falsifier requirement
- hetvabhasa checks
- pramana inference
- formal boundary status
- `accepted_with_penalty` caps
- `hollow` blocking
- gate provenance

This is the top engineering gap.

### 2. Candidate/crux/bridge targets cannot enter the numeric runtime

The newer Nanavira packet targets:

- `candidate_explanation`
- `crux`
- `bridge`

But `truthengine_working.py` currently only accepts runtime targets of:

- `feature`
- `discriminator`

So the argument-fabric target model is ahead of the runtime model. That is fine, but it must be explicit.

The fix is not to force every candidate/crux into F/D. The fix is:

- feature/discriminator targets go to the numeric evidence runtime
- candidate/crux/bridge targets go to `argument_nodes` and `argument_edges`
- the state-of-play synthesizer reads both

### 3. Evidence dimension schema is split

Runtime dimensions:

```text
phenomenological
empirical
contemplative
```

Gate/argument dimensions:

```text
phenomenological
empirical
contemplative
formal
textual
analogical
```

Nanavira's bridge claim uses `analogical`. That is valid for the argument fabric, but the current runtime would reject it if inserted as a numeric claim.

Recommended distinction:

```text
evidence_dimension = broad posterior track
pramana = epistemic mode
argument_dimension = optional finer argument-layer category
```

For runtime compatibility:

- `formal` can map to `phenomenological` or get its own runtime track later
- `textual` can map to `phenomenological`
- `analogical` can map to `phenomenological` with low caps, or stay argument-only
- `empirical` and `contemplative` remain direct runtime tracks

Do not silently collapse this. Store the original pramana and argument dimension.

### 4. The argument schema is not installed by `build_truth_map_db`

`truthmap-argument-schema.sql` validates as additive SQL, but `build_truth_map_db()` does not apply it.

So the tables exist as a spec, not in the working runtime unless manually loaded.

### 5. Gate reports are files, not database rows

The gate can produce JSON. The schema has `claim_gate_results`. But ingestion does not write:

- gate result row
- hetvabhasa rows
- tarka falsifier rows
- formal status link
- source span rows

Until those are rows, querying will stay awkward and the UI cannot be serious.

### 6. No automated state-of-play synthesis

The system can say what moved numerically. It cannot yet compute:

- which candidates are live
- which are weakened
- which are defeated
- which cruxes are open
- which criticism has the most causal power
- what the current best answer is
- what test would matter next

Those are currently written manually in dossier JSON.

### 7. No EO exists

The EO v2 spec is good. But there is still no actual EO artifact that factory code can consume.

This matters because the EO is where the project becomes useful to humans:

```text
argument fabric -> state of play -> essay/video/research brief
```

Without EOs, the project remains an internal research ledger.

### 8. Sanskritree is available but not truly integrated

The current formal probe can call Sanskritree, but it probes English claim text in fast/dev mode. That is useful as a boundary signal, but not enough for real formal bridging.

Real integration needs:

- tradition-scoped term registry
- NNExpr validation
- Lean type candidates
- bridge axioms
- negative controls
- relation probes
- formal status links stored in the truth-map DB

Current formal `UNPROVED` means:

```text
not proved by the current formal layer
```

It must never be interpreted as:

```text
false
```

### 9. Selection bias is not tracked

The extraction pipeline can ingest a packet, but there is no acquisition ledger for:

- what was searched
- what was excluded
- why a source was ignored
- which traditions are underrepresented
- which papers were seen but considered unrelated

This is a serious epistemic risk. Without an acquisition ledger, absence of evidence is invisible.

### 10. Reviewer disagreement is not tracked

Weights are still judgment calls. The system stores a single accepted weight, but does not yet store:

- reviewer identity
- reviewer alternatives
- disagreements
- calibration history
- weight correction deltas
- confidence intervals or credal ranges

Without this, the numbers remain too smooth.

## The Central Schema Problem

There are now three overlapping claim models:

1. Older `specs/CLAIM.md`:
   feature-only `target_feature_ids`, runtime-oriented.

2. Current runtime:
   `targets[]` for `feature` and `discriminator`, plus legacy feature lists.

3. Argument fabric packets:
   `targets[]` can include `candidate_explanation`, `crux`, and `bridge`.

This should be resolved into Claim v3.

Recommended Claim v3 split:

```json
{
  "claim_id": "cl:...",
  "source_span_id": "span:...",
  "claim_text": "...",
  "tradition_scope": "...",
  "pramana": "anumana",
  "evidence_dimension": "phenomenological",
  "argument_dimension": "analogical",
  "hetu": "...",
  "sadhya": "...",
  "vyapti_statement": "...",
  "falsifier": {...},
  "posterior_targets": [
    {"target_id": "D3", "target_type": "discriminator"}
  ],
  "argument_targets": [
    {"target_id": "cand:...", "target_type": "candidate_explanation"},
    {"target_id": "crux:...", "target_type": "crux"}
  ],
  "weights": {
    "log_bayes_factor": 0.4,
    "w_rel": 0.8,
    "w_map": 0.7,
    "w_aux": 0.6
  }
}
```

Rules:

- `posterior_targets` are allowed to move F/D numeric state after gate approval.
- `argument_targets` create graph nodes/edges and state-of-play pressure.
- A claim can have argument targets only and never touch the posterior runtime.
- Every posterior update must be backed by a gate result.

## What The Engine Should Do Next

### P0 - Build one real ingestion pipeline

Create or upgrade ingestion so the real path is:

```text
load packet
validate packet shape
parse source spans
run Nyaya gate
write source_spans
write claims
write claim_gate_results
write hetvabhasa_checks
write tarka_falsifiers
write argument_nodes
write argument_edges
insert only approved feature/discriminator claims into runtime update path
run propagation
write provenance delta
write state_of_play_snapshot
```

Implementation options:

1. Upgrade `scripts/ingest-packet.py`.
2. Add `scripts/ingest-argument-packet.py` and keep the old script for numeric packets.

I recommend option 2 first. It is less risky and keeps the old working runtime stable.

### P0 - Install argument schema into the runtime DB

`build_truth_map_db()` should optionally apply `truthmap-argument-schema.sql`.

Suggested API:

```python
build_truth_map_db(path=":memory:", seed_claims=True, argument_schema=True)
```

Or:

```python
db.create_argument_schema()
```

Do not make every runtime test depend on argument tables at first. Add separate tests.

### P0 - Add gate-aware insertion

New insertion rule:

```text
If gate outcome is accepted:
  insert/update allowed.

If accepted_with_penalty:
  cap absolute LBF before insertion.

If needs_review:
  write graph node, no posterior update.

If hollow:
  write boundary node, no posterior update.

If outside_formal:
  write boundary/formal link, allow non-formal argument tracking only.

If refuted:
  write attack/defeat node, no support update.
```

### P1 - Build state-of-play synthesis

The state-of-play command should answer:

```bash
python scripts/state-of-play.py --question-id q:reflexivity-intrinsic-or-constructed
```

It should output:

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

Initial algorithm can be rule-based. Do not use an LLM until the graph query is deterministic.

Candidate status rule:

```text
defeated:
  a hard-to-vary core is refuted or its required bridge fails, with no viable reformulation

weakened:
  core is pressured, major crux unresolved, or support depends on capped/penalized claims

live:
  candidate still solves at least one central problem and no core defeat is sustained

merged:
  bridge probes or reviewed synthesis show it is not distinct from another candidate
```

### P1 - Convert reflexivity dossier into the first EO

Use:

- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json`
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.nanavira-map.json`
- `specs/EO-v2.md`

The first EO title should be something like:

```text
Structural reflexivity is locally strong; universal consciousness is not entailed.
```

That EO should be the first full end-to-end test of the research pipeline.

### P1 - Implement bridge probing as a real contract

Do not merge terms by embedding similarity or translation.

Bridge test:

```text
same node:
  same scoped type or bidirectional proof under declared bridge axioms

bridges:
  bidirectional implication proved, but scoped assumptions remain visible

subsumes:
  one-way implication proved

contradicts:
  one side implies negation of a hard-to-vary commitment

overlaps:
  shared primitives, no proof

different:
  negative controls show similarity is verbal only
```

Nanavira difference and Dharmakirti apoha are currently `OVERLAPS`.

### P1 - Add source-span ingestion

Every claim should point to a source span row, not just a freeform source id.

Minimum span:

```json
{
  "span_id": "span:nanavira-static-p6",
  "source_type": "source_text",
  "source_id": "so:nanavira-fundamental-structure",
  "locator": "static-aspect.txt paragraph 6",
  "quote": "two things define a thing, namely the difference between them",
  "tradition_scope": "nanavira_phenomenology"
}
```

This prevents hallucinated claim provenance.

### P2 - Add reviewer and acquisition ledgers

Two tables are needed before serious scale:

```text
claim_reviews
acquisition_runs / acquisition_candidates
```

The reviewer ledger makes weights auditable. The acquisition ledger makes selection bias visible.

### P2 - Build the provenance graph UI

Minimum useful UI:

- question page
- candidate page
- source page
- target page
- branch page
- claim page

Every number must have a trace:

```text
source -> span -> claim -> gate -> target -> weight factors -> before/after -> branch delta
```

### P2 - Add red-team test packets

Create packets that should fail or be capped:

- "meditation proves consciousness is fundamental"
- "amplituhedron proves Platonism"
- "brain damage refutes consciousness completely"
- "apoha and Nanavira difference are identical because both say difference"
- "a text says X, therefore X is metaphysically true"

These should verify:

- `asiddha`
- `savyabhicara`
- `badhita`
- `viruddha`
- `satpratipaksa`
- hard cap behavior
- no posterior update for hollow claims

## What Is Missing Conceptually

### 1. A clear standard for "solved"

The system needs resolution levels:

- philological
- semantic
- formal
- local argument
- empirical constraint
- phenomenological
- contemplative reproducibility
- branch relevant
- global metaphysical

Most questions will never be globally solved. But many can be locally solved.

Example:

```text
Nanavira strengthens local structural reflexivity.
He does not settle intrinsic manifestness.
He weakens universalization from local reflexivity.
```

That is a real result.

### 2. Argumentation semantics

The graph needs a deterministic way to aggregate support and attack.

Start simple:

- grounded status: what survives all accepted attacks
- preferred status: strongest coherent candidate set
- skeptical status: only what survives across all reasonable extensions

Do not overbuild this yet. A small rule engine is enough.

### 3. Term registry

The project cannot bridge traditions safely without scoped terms.

Need:

```text
term
scope
definition
source span
commitments
opposed terms
possible bridges
negative controls
Lean/NNExpr candidate
```

Examples:

- `information:landauer`
- `information:iit`
- `information:trika_vimarsa`
- `difference:nanavira`
- `apoha:dharmakirti`
- `prakasa:abhinavagupta`

Same English word never means same node by default.

### 4. Severe tests

Popper/Deutsch should be operationalized as:

```text
What would this explanation forbid?
What would make it worse than a rival?
What is its hard-to-vary core?
What is the cheapest live criticism?
Which experiment or argument has maximum expected damage?
```

The current expected-information-gain idea should be expanded from discriminators to candidate defeat.

### 5. ML should be auxiliary only

Useful ML later:

- claim extraction candidate generation
- span retrieval
- duplicate/overlap suggestions
- reviewer-disagreement prediction
- weight correction suggestions after enough reviewed packets
- graph embeddings for search

Do not use ML to decide bridges, defeats, or final state of play without human-visible proof/reasoning. ML can propose; the gate and graph decide.

## What Not To Do

- Do not build a bigger flat Bayesian posterior.
- Do not merge traditions by translation.
- Do not show branch probabilities without provenance.
- Do not treat `UNPROVED` as false.
- Do not let LLM extraction assign weights that become invisible.
- Do not train ML before there are reviewed corrections.
- Do not ingest argument-only claims into numeric targets just to make the engine move.
- Do not let source texts become evidence for metaphysical truth without distinguishing `sabda` from `anumana`.

## Recommended Build Sequence

### Sprint 1 - Gate-aware argument ingestion

Deliverables:

- `scripts/ingest-argument-packet.py`
- argument schema applied to SQLite
- gate report rows stored
- source spans stored
- argument nodes/edges stored
- accepted feature/discriminator claims optionally passed to numeric runtime
- tests using amplituhedron and Nanavira packets

Definition of done:

```text
Nanavira packet ingests without pretending candidate/crux targets are numeric targets.
Analogical bridge claim is stored as argument-only or mapped with explicit cap.
Gate rows are queryable.
No hollow claim can move posterior.
```

### Sprint 2 - State-of-play command

Deliverables:

- `scripts/state-of-play.py`
- candidate status rules
- strongest support/attack ranking
- open crux output
- unresolved bridge output
- state_of_play_snapshot insertion

Definition of done:

```text
The reflexivity question produces a deterministic state-of-play report.
The report agrees with the manual Nanavira map.
```

### Sprint 3 - First EO

Deliverables:

- `content/essay-objects/eo-reflexivity-structural-local-v1.json`
- EO validates against `specs/EO-v2.md`
- EO points to source spans, claims, cruxes, and state-of-play snapshot

Definition of done:

```text
The project can go from source text to EO without hidden reasoning.
```

### Sprint 4 - Sanskritree bridge integration

Deliverables:

- local wrapper around NNExpr parser
- formal_status_links insertion
- bridge_probe wrapper
- negative bridge controls imported
- bridge status update rules

Definition of done:

```text
Nanavira difference vs Dharmakirti apoha remains OVERLAPS unless formal tests prove stronger relation.
```

### Sprint 5 - Provenance graph view

Deliverables:

- source contribution report page or CLI
- target blame report page or CLI
- question page showing candidates/cruxes/evidence movement

Definition of done:

```text
For any target, we can rank the papers/texts that moved it most and inspect the full weight decomposition.
```

### Sprint 6 - Reviewer and acquisition controls

Deliverables:

- claim_reviews table
- acquisition ledger tables
- reviewer-lens report
- disagreement/convergence report

Definition of done:

```text
The system can show when global support rises while paradigms or reviewers diverge.
```

## Current Best Description Of The Engine

The engine is working as a prototype of an epistemic operating system.

Its reliable current claim:

```text
Given structured claims with reviewed weights, it can compute auditable movement across features, discriminators, branches, and evidence dimensions.
```

Its unreliable current claim:

```text
Given arbitrary source material, it can automatically say our best idea of reality.
```

That second claim becomes more credible only after:

- gate-aware ingestion is mandatory
- argument graph rows are first-class
- state-of-play synthesis is automated
- source spans and reviewer judgments are queryable
- bridge probes use negative controls
- EOs exist and can be regenerated from the graph

## Bottom Line

The project is on the right architecture now.

The numeric truth engine should stay, but it should be demoted to a provenance and disagreement subsystem. The real product is the argument fabric plus state-of-play synthesis.

The next serious move is not another redesign. It is this:

```text
Wire source packets -> Nyaya gate -> argument DB -> numeric runtime -> state-of-play snapshot.
```

Once that exists, the system can start answering its real question:

```text
What is our best current account of reality, what survives criticism, and what would break it?
```
