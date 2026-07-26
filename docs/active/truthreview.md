# Truth Review - Lead-Agent Audit Against the Research Directive

## Executive Verdict

The project has the right architecture now, but the center of gravity is still in
the wrong place operationally.

The original directive does not ask for a generic Bayesian belief engine. It asks
for a research agent that can take one sharp pressure point, reconstruct the best
competing explanations, identify structural correspondence and non-equivalence,
reverse the critique in both directions, generate consequences, and state what
currently survives.

The current build can store many of those pieces. It cannot yet reliably compile
them into the state of play.

For Nanavira vs Abhinavagupta, the "0 posterior movement" result is correct but
incomplete. The Nanavira packet targeted candidates, cruxes, and bridge nodes,
not D/F runtime targets. The system was right not to fake numerical convergence.
What is missing is the argument-level update:

```text
Nanavira strengthens local structural reflexivity.
Nanavira weakens the inference from local reflexivity to universal consciousness.
Abhinavagupta remains live where structural accounts do not explain manifestness.
Dharmakirti remains live where no-self targets owner-substance, not reflexivity.
The bridge between Nanavira difference and Dharmakirti apoha is OVERLAPS, not BRIDGES.
```

That synthesis currently exists in manual EOs and maps. It is not yet computed
from the argument graph.

## Documents Reviewed

Highest-signal docs read for this review:

- `REF.md`
- `ONBOARDING.md`
- `RESEARCH_DIRECTIVE.md`
- `ROADMAP.md`
- `TRUTHMAP-PROGRESS.md`
- `TRUTHMAP-ARGUMENT-FABRIC.md`
- `TRUTHMAP-PURPOSE.md`
- `TRUTHPLAN.md`
- `TRUTHMAP-PRODUCTION-HARDENING.md`
- `TRUTH-TEST.md`
- `CODEX-RESEARCH-SEED.md`
- `VERSIONING-INFRA.md`
- `EVIDENCE-PIPELINE.md`
- `specs/TRUTH-MAP-QUESTION.md`
- `specs/CLAIM.md`
- `specs/RO-v2.md`
- `specs/EO-v2.md`
- `truthadvanced.md`
- `truthbuildnew.md`
- `tractatus-conscientiae.md`
- `tractatus-nanavira-abhinavagupta.md`
- Current source/dossier/packet/EO artifacts under `content/`
- Current implementation files under `scripts/`, `truthengine_working.py`, and tests

Some docs are stale. `ROADMAP.md`, `TRUTHPLAN.md`, `TRUTHMAP-PROGRESS.md`, and
`HANDOVER-SESSION-2026-07-26.md` still say pieces are missing that now exist:
gate-aware ingestion, first EO, NNExpr import, and 30 passing tests. Do not use
those docs as current status without cross-checking code and `truthbuildnew.md`.

## Original Directive, Distilled

The directive asks for a disciplined comparative research machine.

For every serious question, it must do seven things:

1. Formulate one exact pressure point.
2. Define competing claims in their strongest form.
3. Identify the narrowest shared structure.
4. Identify where the comparison breaks.
5. Find the strongest current answer.
6. Reverse the direction of critique.
7. Generate research consequences.

It also requires five levels of inquiry:

- textual and historical reconstruction
- phenomenology
- cognitive and biological mechanism
- formal and physical structure
- metaphysical interpretation

And it starts from 72 priority questions. Only 16 are currently seeded as
truth-map/question or argument-dossier artifacts. The remaining 56 are not yet
represented.

The output standard is not "Trika was right" and not "science refutes Trika."
The required output is calibrated:

```text
what we can responsibly claim
what remains plausible but unproven
what should not be claimed
the next question to investigate
```

## What Is Working Now

### 1. Numeric Runtime

`truthengine_working.py` is a real working runtime.

It supports:

- F1-F8 features
- D1-D5 discriminators
- B1-B6 branch support
- 60 discriminator branch-effect multipliers
- feature-to-discriminator derived mappings
- direct feature and discriminator targets
- three runtime evidence dimensions: empirical, phenomenological, contemplative
- dimension-specific paradigm crowding
- convergence diagnostics
- source/target contribution traces
- ranked blame by target

The current test suite passes:

```text
30 tests passing
```

This includes known-truth tests for amplituhedron -> D4, IIT -> D3, brain
damage -> D3-no pressure, dimension divergence, crowding, adversarial LBF and
zero-weight cases, gate validation, and gated packet ingestion.

### 2. Provenance and Blame Foundation

`scripts/provenance-report.py` and `PropagationEngine.contribution_trace()` can
already expose:

- source id
- claim id
- claim text
- target id
- target type
- evidence dimension
- `log_bayes_factor`
- `w_rel`
- `w_map`
- `w_aux`
- computed `w_dep`
- effective LBF
- posterior before/after
- branch support before/after/delta

This is the seed of "git blame for beliefs." It works for numeric targets.

It does not yet rank causal power inside the argument graph. A Nanavira claim
that strengthens a candidate but has no D/F target currently has no comparable
candidate-delta trace.

### 3. Nyaya Gate

`scripts/nyaya-truthmap-gate.py` is a working pre-ingestion gate.

It checks or infers:

- tradition scope
- pramana
- evidence dimension
- target presence
- hetu
- sadhya
- vyapti statement and confidence
- falsifier status
- hetvabhasa defects
- tarka falsifiers
- optional Sanskritree formal probe

Gate outcomes are:

- `accepted`
- `accepted_with_penalty`
- `needs_review`
- `hollow`
- `outside_formal`
- `refuted`

The gate is now wired into `scripts/ingest-packet.py` by default.

### 4. Argument-Fabric Schema

`truthmap-argument-schema.sql` exists and is loadable through:

```python
build_truth_map_db(seed_claims=False, argument_schema=True)
```

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

This is the right family of tables. The missing part is a deterministic compiler
that fills and evaluates them from dossiers, ROs, EOs, maps, and packets.

### 5. Gate-Aware Packet Ingestion

`scripts/ingest-packet.py` now does the correct default thing:

```text
packet claim
  -> Nyaya gate
  -> source_span row
  -> claim metadata row
  -> argument node row
  -> argument target edges
  -> gate result rows
  -> runtime update only if gate permits and target is feature/discriminator
```

This is why the Nanavira run produced:

```text
claims_seen: 7
runtime_claims_inserted: 0
argument_claims_recorded: 7
gate_results_stored: 7
gate_outcomes:
  accepted: 5
  accepted_with_penalty: 2
```

That is correct. Nanavira's packet moved the argument fabric, not the numeric
runtime.

### 6. Nanavira Source Pipeline

Nanavira now exists as:

- `content/source-texts/nanavira-fundamental-structure/SO.json`
- full source text files
- `content/research-objects/ro-nanavira-fundamental-structure/ro.json`
- `content/information-packets/nanavira-fundamental-structure-claims.json`
- `content/information-packets/delta-nanavira-gated.json`
- `content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.nanavira-map.json`
- EO artifacts for the reflexivity debate

This is the first real end-to-end source case.

### 7. Question/Dossier Seeds

There are 16 real seeded question artifacts:

- 6 original scalar truth-map questions
- 10 argument-style dossiers from the research directive

There is also one Nanavira source map. It is not itself one of the 72 questions.

### 8. NNExpr Parser and Formal Bridge Skeleton

`scripts/logic/bnf.py` and `scripts/logic/fol_lean_bridge.py` are imported from
Sanskritree.

They can parse or bridge forms like:

- `vyapti(...)`
- `sambandha(...)`
- `abheda(...)`
- `catuskoti(...)`
- `prasanga(...)`
- `apoha(...)`

They are not yet wired into the gate or bridge-probe flow.

### 9. State-of-Play Script Exists, But Is Not The Real Synthesizer Yet

`scripts/state-of-play.py` exists and can print a readable report for
`q:reflexivity-intrinsic-or-constructed`.

However, it is currently a shallow reporter. It mostly falls back to dossier/EO
JSON. It does not yet compute candidate status from graph edges, gate results,
formal status, crux pressure, or provenance deltas.

That means it can repeat a manually written state of play, but it cannot yet
derive one.

## Key Gaps Against The Research Directive

| Directive requirement | Current status | Gap |
| --- | --- | --- |
| 72 priority questions | 16 seeded | 56 missing |
| 7-step procedure | Captured in docs/EO prose | No procedure compiler |
| Five levels of inquiry | Partly represented | Textual/formal are gate dimensions, not runtime/report levels |
| Strongest competing claims | Present in argument dossiers | Dossiers not ingested into graph as first-class candidates/cruxes |
| Shared structure table | Manual in maps/EOs | No generated correspondence table |
| Where comparison breaks | Manual cruxes/bridge notes | No non-equivalence evaluator |
| Reverse direction of critique | Mostly absent structurally | Need directional critique pairs |
| Testable consequences | Stored as prose/tests/falsifiers | Not fed into priority queue or engine |
| Source baskets A-E | Directive only | No acquisition ledger or basket coverage tracker |
| State-of-play verdict | Manual EO and shallow script | No deterministic synthesis from graph |
| Causal power by evidence | Works for D/F numeric targets | Missing for candidate/crux/bridge impact |
| Bridge probing | Policy and NNExpr parser exist | No production `probe-bridge.py` with negative controls |
| Production validity | Tests pass for runtime/gate/ingest | Object validation and canonical artifact checks missing |

## Main Diagnosis

The engine has three different "state" layers that are not yet reconciled.

### 1. Runtime State

This is the numeric truth-map state:

```text
features -> discriminators -> branch support
```

It is working.

### 2. Argument State

This is the state the directive actually needs:

```text
question -> candidates -> cruxes -> supports/attacks -> bridge status -> consequences
```

It is designed and partially stored, but not computed.

### 3. Editorial State

This is the human-written synthesis:

```text
EO state_of_play
Nanavira map
tractatus essay
manual summaries
```

It is useful, but it is not yet auditable as an engine output.

The next build must make argument state the primary state. Runtime state should
be one evidence view inside the argument fabric, not the center of the system.

## Specific Data/Schema Issues Found

### 1. Duplicate EO Identity

There are two EO artifacts with the same `eo_id`:

- `content/essay-objects/eo-reflexivity-structural-local-v1.json`
- `content/essay-objects/eo-reflexivity-structural-local-v1/eo.json`

They are not identical. This creates canonicality risk. A state-of-play script
may read one or the other depending on traversal order or future loader policy.

Decision needed:

```text
canonical EO path should be directory form:
content/essay-objects/{slug}/eo.json
```

The flat file should become either a migration source, archived artifact, or be
removed after explicit review.

### 2. Nanavira RO Has A Schema Typo

`content/research-objects/ro-nanavira-fundamental-structure/ro.json` uses:

```text
bears_on_quequestions
```

The spec expects:

```text
bears_on_questions
```

Until fixed, automated RO indexing will miss its question links.

### 3. Argument Edge Vocabulary Is Inconsistent

The SQL schema allows:

```text
supports, attacks, rephrases, instantiates, presupposes, contradicts,
subsumes, bridges, decomposes_to, targets, falsified_by, outside_formal
```

The Nanavira source map uses additional relation ideas like:

```text
overlaps, undercuts
```

The state-of-play script and bridge policy also refer to relation statuses like:

```text
OVERLAPS, DIFFERENT, BRIDGES, SUBSUMES, CONTRADICTS
```

This is conceptually fine, but the schema needs one canonical mapping:

```text
formal relation status: OVERLAPS / BRIDGES / SUBSUMES / CONTRADICTS / DIFFERENT
argument edge type: supports / attacks / undercuts / overlaps / targets / ...
```

Do not overload `bridges` to mean every kind of similarity.

### 4. State-of-Play Rows Are Not Populated

`state_of_play_snapshots` exists, but current reports are not persisted as
snapshots from the graph.

This blocks time-travel and "what changed since the last source" queries.

### 5. Runtime Claims And Argument Claims Are Still Too Easy To Confuse

`claims` now stores both runtime and argument-only claims. That is acceptable
because numeric propagation uses `claim_targets`.

But production reports must make this visible:

```text
runtime claim: can move F/D posterior
argument claim: can move candidate/crux/bridge status only
```

Nanavira is the canonical example of an argument-only update.

## What The System Should Say About Nanavira vs Abhinavagupta

Current proper verdict:

```text
Structural reflexivity is locally strengthened.
Universal consciousness is not entailed.
Abhinavagupta is pressured at the universalization step, not refuted.
Abhinavagupta pressures Nanavira at manifestness: does structure explain appearing or presuppose it?
Dharmakirti and Nanavira overlap around non-substance determination, but apoha is not identical to Nanavira's difference operation.
Higher-order/self-model accounts remain live where they can operationalize reflexivity, but they remain pressured by manifestness and no-report cases.
```

The engine should eventually derive that from:

- candidate hard-to-vary cores
- accepted and penalized claims
- crux pressure
- bridge relation status
- formal status
- empirical constraints
- unresolved falsifiers

Today, it can only print similar prose if a human has already written it into an
EO or map.

## Required Build Direction

### P0 - Canonicalize Objects And Validation

Build:

```text
scripts/validate-ro.py
scripts/validate-eo.py
scripts/validate-dossier.py
test_object_validation.py
```

Minimum checks:

- one canonical artifact per id
- no duplicate `eo_id`, `ro_id`, or `question_id`
- `bears_on_questions` spelled correctly
- every candidate has a falsifier
- every EO has 2+ candidates
- EO has all five Nyaya syllogism members
- every source id resolves to an SO, RO, packet, or external source stub
- no runtime-target claim bypasses the gate
- argument edge types match the SQL vocabulary
- every non-equivalence/bridge claim has a falsifier or negative-control path

This is not cosmetic. The system cannot become autonomous if its own artifacts
are not canonical.

### P0 - Ingest Dossiers Into The Argument DB

Build:

```text
scripts/ingest-dossier.py
test_ingest_dossier.py
```

It should load `*.argument.json` and create:

- question node
- candidate_explanation nodes
- crux nodes
- candidate hard-to-vary-core payloads
- candidate falsifier rows
- crux pressure edges
- initial state-of-play snapshot marked `manual_seed`

Do not force the entire dossier through the claim gate. Only atomic evidence
claims should be gated. Dossiers are question scaffolds.

### P0 - Replace State-Of-Play Fallback With Graph Synthesis

Upgrade:

```text
scripts/state-of-play.py
test_state_of_play.py
```

The report should be deterministic and graph-derived.

Inputs:

- `argument_nodes`
- `argument_edges`
- `claim_gate_results`
- `hetvabhasa_checks`
- `tarka_falsifiers`
- `formal_status_links`
- `state_of_play_snapshots`
- numeric provenance traces for D/F targets

Outputs:

- best current answer
- live candidates
- weakened candidates
- defeated candidates
- open cruxes
- strongest supports
- strongest attacks
- unresolved bridges
- evidence with highest causal power
- bidirectional critique
- next tests

The fallback to EO/dossier JSON should remain only as a bootstrap mode, clearly
labelled:

```text
source: manual_seed
```

### P0 - Candidate Status Rules

Implement candidate evaluation as rules first, not ML.

Candidate stays live when:

- at least one hard-to-vary core remains unrefuted
- no decisive attack targets its core
- open cruxes remain
- formal status is not REFUTED on its core

Candidate becomes weakened when:

- accepted or penalized attacks target a hard-to-vary core
- bridge probes downgrade a needed equivalence to OVERLAPS or DIFFERENT
- empirical evidence pressures a required mechanism
- its answer depends on a HOLLOW or OUTSIDE_FORMAL core without a narrower reformulation

Candidate becomes defeated only when:

- a core commitment is REFUTED or decisively attacked
- the attack passes gate/formal checks
- no narrower reformulation preserves the candidate's explanatory role
- rival candidates explain the pressure point at least as well

This should be transparent and inspectable. The system should never silently
turn low posterior movement into philosophical defeat.

### P0 - Directional Critique Pairs

The directive's Step 6 is currently the weakest represented piece.

Add a first-class structure:

```text
critique_pair
  question_id
  critic_lens
  target_lens
  reveals_about_target
  pressure_type
  target_response_required
  status
  supporting_claim_ids
  crux_ids
```

Examples:

```text
Nanavira -> Abhinavagupta:
  reveals: local reflexivity does not entail universal consciousness
  pressure_type: universalization_gap

Abhinavagupta -> Nanavira:
  reveals: structural reflexivity may presuppose manifestness
  pressure_type: manifestness_gap

Neuroscience -> Trika:
  reveals: brain dependence constrains any simple consciousness-independent mind claim
  pressure_type: embodiment_constraint

Trika -> neuroscience:
  reveals: modeling/reflexivity accounts may leave first-person manifestness undefined
  pressure_type: explanatory_residue
```

This is the missing data shape for the original directive.

### P1 - Structural Correspondence And Break Tables

Build a `correspondences` object/table:

```text
question_id
left_term
left_scope
right_term
right_scope
shared_structure
important_difference
confidence_language
status
source_ids
bridge_probe_id
negative_control_status
```

This directly implements directive Steps 3 and 4.

For Nanavira vs Dharmakirti:

```text
left: Nanavira difference
right: Dharmakirti apoha
shared: non-substance determination by difference/exclusion
break: structural/phenomenological operation vs semantic/epistemic exclusion
status: OVERLAPS
```

For Nanavira vs Abhinavagupta:

```text
left: structural reflexivity
right: intrinsic self-manifestation
shared: experience can include or reveal its own occurrence
break: constructed/level-relative operation vs intrinsic manifestness
status: live non-equivalence
```

### P1 - Wire NNExpr Into The Gate

Now that `scripts/logic/bnf.py` exists, the gate should parse `claim["nn_expr"]`
when present.

Store:

- parse attempted
- parse status
- parsed tree or error
- tradition scope
- whether formal bridge status may be requested

Policy:

- missing NNExpr is allowed for ordinary claims
- invalid NNExpr on a formal/bridge claim becomes `needs_review`
- parser acceptance without useful tree is a boundary, not success

Add tests:

- valid `vyapti(difference,determination)`
- valid `abheda(duration,invariance)`
- valid `prasanga(...)`
- invalid expression becomes `needs_review`
- bridge claim cannot be upgraded from OVERLAPS to BRIDGES without formal or reviewed evidence

### P1 - Bridge Probing With Negative Controls

Build:

```text
scripts/probe-bridge.py
test_bridge_probe.py
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

The important rule is that lexical similarity and embeddings can propose a
bridge, but cannot accept one.

### P1 - Argument Causal Power

Extend provenance beyond numeric posteriors.

For numeric claims, causal power is:

```text
abs(effective_lbf) and posterior_delta
```

For argument claims, causal power should be:

```text
edge_strength * gate_multiplier * core_target_multiplier * crux_importance
```

Where:

- accepted = full gate multiplier
- accepted_with_penalty = capped/penalized multiplier
- needs_review/hollow = visible but non-updating
- core target > auxiliary target
- a central crux > peripheral crux

This will let the system rank:

```text
which Nanavira claim most strengthened structural reflexivity
which criticism most weakened Abhinavagupta's universalization
which empirical source most pressures Trika
```

### P1 - Persist State-Of-Play Snapshots

Every generated report should write a row to `state_of_play_snapshots` with:

- current best answer
- confidence language
- solved levels
- live/weakened/defeated candidates
- open cruxes
- next tests
- implications
- provenance input hash

Then the system can answer:

```text
what changed after this paper
what changed after this bridge probe
what changed after this criticism was accepted
```

### P1 - Update REF And ROADMAP After Implementation

After P0 fixes, update stale docs:

- `REF.md`
- `ROADMAP.md`
- `TRUTHMAP-PROGRESS.md`

Do not do this before the code is fixed, or the docs will drift again.

### P2 - Seed All 72 Directive Questions

Build:

```text
scripts/seed-research-directive.py
```

This should turn `RESEARCH_DIRECTIVE.md` into canonical question/dossier
artifacts.

Each question needs:

- `question_id`
- exact pressure point
- level coverage
- candidate explanations
- cruxes
- falsifiers
- source baskets needed
- initial status
- next tests

Do not overfill with fake evidence. Seed the question structure first.

### P2 - Acquisition And Reviewer Ledgers

To handle selection bias and weight circularity, add:

- `acquisition_runs`
- `acquisition_candidates`
- `claim_reviews`
- `reviewer_weight_deltas`
- `protocol_metadata`

This supports:

- what was searched
- what was excluded
- whose review changed weights
- which claims are still unreviewed
- reviewer disagreement intervals

No ML calibration should happen before this exists.

### P2 - Research Directive Compiler

Build a command that creates an EO draft from graph state:

```text
scripts/compile-eo.py --question-id q:reflexivity-intrinsic-or-constructed
```

It should produce the directive-required structure:

- title
- exact research question
- why it matters
- best provisional answer
- Trika reconstruction
- scientific/philosophical reconstruction
- structural correspondence table
- hardest point of contention
- where each side is stronger
- where both may be wrong
- testable/formal consequences
- source baskets
- research verdict

For now, generate JSON only. Human writing can come later.

### P3 - GraphRAG And Retrieval

Only after canonical graph ingestion works:

- add text search over source spans, claims, and candidates
- add embeddings for fuzzy retrieval
- add graph-constrained retrieval for multi-hop state-of-play queries
- let an LLM summarize only the retrieved subgraph

The LLM should not decide truth. It should propose:

- candidate edges
- possible criticisms
- possible falsifiers
- missing sources
- draft prose

The graph and validation gates remain authoritative.

### P3 - Dashboard

The first dashboard should be operational, not decorative.

Minimum useful screens:

- question page
- candidate page
- crux page
- source page
- claim page
- bridge page
- state-of-play history
- provenance/blame view

Every displayed answer must link to:

```text
source -> span -> claim -> gate -> edge/target -> status/delta -> state of play
```

## Recommended Immediate Sprint

Do this in order:

1. Add object validators and catch duplicate EO IDs plus RO schema typo.
2. Build `scripts/ingest-dossier.py`.
3. Populate the argument DB from the reflexivity dossier and Nanavira map.
4. Replace `scripts/state-of-play.py` fallback report with graph-derived status.
5. Add `test_state_of_play.py` proving the Nanavira verdict is derived, not copied.
6. Add directional critique pairs for Nanavira <-> Abhinavagupta.
7. Persist a `state_of_play_snapshots` row.

The acceptance test for the sprint:

```text
Given only the reflexivity dossier, Nanavira packet, Nanavira map, and EO inputs,
the system generates a state-of-play report saying:

- structural reflexivity is locally strengthened
- universal consciousness is not entailed
- Abhinavagupta is pressured at universalization
- Abhinavagupta pressures Nanavira at manifestness
- Dharmakirti/Nanavira is OVERLAPS, not BRIDGES
- next tests include formal bridge probes and manifestness/reflexivity tests
```

If that report is manually copied from EO prose, the sprint has failed. If it is
derived from graph rows and rule outputs, the project has reached the first
version of the original directive.

## Research-Engineering Principle Going Forward

Do not optimize for more numbers.

Optimize for this:

```text
Can the system explain why one live answer survives criticism better than its rivals,
showing every source, claim, gate decision, bridge assumption, unresolved crux,
and consequence that led to that answer?
```

That is the original directive in software form.
