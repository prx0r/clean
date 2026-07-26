# Truth Next - Red-Team Notes And Build Direction

## Current Assessment

The project now has a first real argument-fabric loop:

```text
dossier/source map -> argument DB -> graph-derived state of play
packet -> Nyaya gate -> argument rows -> optional numeric runtime update
```

The Nanavira/reflexivity case is the first useful acceptance test. The system
can now derive the important local verdict from graph rows:

```text
structural reflexivity strengthened
universal consciousness not entailed
Abhinavagupta pressured at universalization
Abhinavagupta pressures Nanavira at manifestness
Nanavira/Dharmakirti remains OVERLAPS, not BRIDGES
```

That is a real improvement over the previous "0 posterior movement" result.

## What I Just Added

### NNExpr gate parsing

`scripts/nyaya-truthmap-gate.py` now parses `claim["nn_expr"]` when present.

It records:

- parse attempted
- original expression
- normalized expression
- parsed tree
- parse status
- notes

ASCII aliases like this are normalized before parsing:

```text
vyapti(difference,determination)
```

to:

```text
vyāpti(difference,determination)
```

Policy:

- ordinary claims do not need NNExpr
- valid NNExpr adds structured metadata
- invalid NNExpr is visible but does not automatically block ordinary claims
- invalid NNExpr blocks claims requesting formal/bridge status

`scripts/ingest-packet.py` now stores the NNExpr probe in the argument-node
payload.

## Red-Team Findings

### 1. State-of-play scoring is still heuristic

The current candidate pressure/support scores are useful for ranking, but they
are not yet a defensible theory of argument acceptability.

Current rough formula:

```text
edge_strength * gate_multiplier * target_multiplier
```

Risk:

- a weak claim with many edges could look stronger than a single decisive attack
- edge strength still comes from authored maps, not reviewed argument scoring

Current mitigation:

- crux pressure is now separated from direct candidate weakening
- a candidate is not listed as weakened merely because an open crux bears on it
- untested candidate-declared falsifiers are tracked as pending tests, not as
  evidence against the candidate
- only active falsifier statuses such as `tested_failed` count as direct
  pressure

Next fix:

- make weakened require attack on a hard-to-vary core
- reserve defeated for passed-gate attacks on core commitments with no live
  reformulation

### 2. Source-map ingestion is generic now

`scripts/ingest-dossier.py` now supports generic source-map arrays:

```text
structural_correspondences[]
directional_critique_pairs[]
```

When those arrays are present, ingestion writes them directly into the argument
fabric. The existing Nanavira map now declares those arrays explicitly, and the
old Nanavira-specific bridge/correspondence/critique fallback has been removed.

Risk:

- the generic arrays are structurally validated, but the validator does not yet
  prove semantic adequacy
- malformed but superficially complete maps can still encode weak authored
  judgments

Current mitigation:

- add bridge probes and negative controls so correspondence status is computed
  rather than authored
- add reviewer checks for critique pair quality

`scripts/probe-bridge.py` now provides the first conservative bridge classifier.
It keeps Nanavira/Dharmakirti at `OVERLAPS` because the positive implication
probes are unproved.

Next fix:

- connect `scripts/probe-bridge.py` to real Sanskritree/Lean proof output
- persist probe-derived status back into `structural_correspondences`
- make the validator flag declared statuses stronger than probe output

### 3. NNExpr parsing is syntax only

The parser can say:

```text
abheda(duration,invariance) parses
```

It cannot say:

```text
duration and invariance are actually equivalent
```

Risk:

- users may treat parse success as proof
- bridge candidates may be over-trusted if "parsed" is read as "validated"

Current mitigation:

- state-of-play still says OVERLAPS until bridge probes/negative controls pass
- gate stores parsed tree as metadata, not as proof

Next fix:

- add `scripts/probe-bridge.py`
- load negative bridge controls before any bridge upgrade
- require formal or human-reviewed status for `BRIDGES`

### 4. `avacchedaka(duration,level)` exposes a grammar boundary

The imported parser treats `avacchedaka` as unary, but Nanavira uses it like a
binary scoping relation.

Current policy:

- this invalid NNExpr is recorded but does not block the Nanavira claim because
  the claim is argument-level, not a formal/bridge upgrade request

Risk:

- the grammar may be too narrow for Navya-Nyaya-style scoping relations

Next fix:

- decide whether `avacchedaka` should allow binary use
- add parser tests around scoping expressions before changing the grammar

### 5. Duplicate EO identity is resolved

The canonical EO layout is:

```text
content/essay-objects/{eo-slug}/eo.json
```

The duplicate flat EO was removed after copying its stronger/currenter content
into:

```text
content/essay-objects/eo-reflexivity-structural-local-v1/eo.json
```

Risk:

- new EOs could reintroduce flat-file duplicates unless CI runs the validator

Next fix:

- make the object validator part of the normal test/CI command

### 6. No acquisition/reviewer ledger yet

The system still cannot answer:

```text
what did we search?
what did we reject?
who assigned this weight?
which reviewer disagreed?
```

Risk:

- selection bias remains invisible
- weight circularity remains only partially mitigated by provenance

Next fix:

- add `acquisition_runs`
- add `acquisition_candidates`
- add `claim_reviews`
- add reviewer disagreement views before any ML calibration

### 7. Bridge probe exists but is not proof-backed yet

The system can store:

```text
OVERLAPS
BRIDGES
SUBSUMES
CONTRADICTS
DIFFERENT
```

`scripts/probe-bridge.py` can compute a conservative relation from declared
formal probe statuses and negative controls. It does not run Sanskritree/Lean
itself yet.

Risk:

- bridge status can still be authored unless probe output is persisted and
  enforced by validation

Next fix:

- connect Sanskritree `bridge_probe.py` or Lean status output
- persist probe results
- block bridge upgrades when negative controls fail or positive probes are
  missing

## Best Next Build Order

### P0 - Source-map ingestion generalization complete

Implemented now:

```text
generic structural_correspondences[] ingestion
generic directional_critique_pairs[] ingestion
legacy Nanavira fallback remains
```

Still needed:

```text
probe-result persistence instead of authored bridge status
```

### P0 - Tighten state-of-play candidate rules

Change state synthesis so:

- open crux pressure does not automatically mark a candidate weakened
- support/attack on hard-to-vary core is tracked separately
- bridge downgrade affects only candidates that require that bridge
- defeated is impossible without a decisive gate/formal status

### P0 - Resolve canonical EO layout

Pick one canonical EO location and make validators enforce it.

Recommended:

```text
content/essay-objects/{eo-slug}/eo.json
```

### P1 - Bridge probe wrapper persistence

Built:

```text
scripts/probe-bridge.py
test_bridge_probe.py
```

Passing tests:

```text
Nanavira difference vs Dharmakirti apoha -> OVERLAPS
bidirectional proof -> BRIDGES
one-way proof -> SUBSUMES
failed negative control -> DIFFERENT
```

No bridge upgrade until negative controls pass.

### P1 - Acquisition and reviewer ledgers

Add schema and minimal commands:

```text
scripts/log-acquisition.py
scripts/review-claim.py
```

This is the next honesty layer after provenance.

### P2 - EO compiler

Build:

```text
scripts/compile-eo.py --question-id ...
```

It should compile the graph into EO-v2 JSON. It should not write polished prose
yet; it should make a rigorous draft object that humans can edit.

## Red-Team Bottom Line

The graph layer is now useful, but it is still a deterministic scaffold with
authored strengths. The next maturity jump is not more posterior math. It is:

```text
generic source-map ingestion [done]
hard-to-vary candidate status rules
bridge probing with negative controls
reviewer/acquisition ledgers
canonical object validation
```

That is what turns the current prototype into a research agent that can serve
the original directive without hiding interpretive judgment behind numbers.
