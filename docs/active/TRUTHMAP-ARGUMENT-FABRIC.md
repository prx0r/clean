# Truth Map Argument Fabric

## Purpose

This file defines the next architecture for the truth map: a graph-native,
refutation-led argument fabric that unifies the Sanskritree formal proof layer
with the existing truth-map evidence layer.

The core rule:

> The truth map does not compute reality. It records what explanations survive
> criticism, what would break them, what evidence moved them, and where formal
> proof stops.

The Bayesian runtime remains useful. It becomes a derived view over a richer
argument graph.

---

## System Shape

```text
Source span
  -> Claim
  -> Gate result
  -> Argument node
  -> Support / attack / rephrase / formal-bridge edge
  -> Crux node
  -> Candidate explanation
  -> State of play
  -> Conditional branch implication
```

This is a stricter version of AIF-style argument mapping, extended with:

- Nyaya pramana metadata.
- Hetvabhasa fallacy checks.
- Tarka falsifier generation.
- Nigrahasthana defeat tracking.
- Tradition-scoped terms.
- Sanskritree formal proof status.
- Truth-map posterior vectors and provenance.

---

## Layer Split

| Layer | Question | Main tool | Output | Failure mode |
|-------|----------|-----------|--------|--------------|
| Source layer | What exactly was said? | Sanskritree / corpus retrieval | source spans, translations, TOs | bad philology |
| Formal layer | Can this be proved or typed? | Lean / Sanskritree proof engine | PROVED, UNPROVED, HOLLOW, OUTSIDE_FORMAL, REFUTED | too narrow |
| Argument layer | Does this inference survive criticism? | Nyaya/AIF argument graph | support, attack, crux, defeat status | bad reconstruction |
| Evidence layer | What evidence exists? | truth-map Bayesian runtime | dimension/pramana posterior vectors | pseudo-precision |
| Reality brief layer | What is our best current answer? | state-of-play synthesis | surviving explanations, implications, next tests | overclaiming |

The new fabric sits between formal proof and Bayesian evidence tracking.

---

## Design Commitments

### 1. Claims do not enter the engine naked

Every claim must pass a gate before it can move a truth-map posterior.

Minimum gate:

```text
source_span exists
target exists
tradition_scope exists
epistemic_mode/pramana exists
falsifier exists or claim is marked HOLLOW / hermeneutic_context
hetvabhasa check completed
vyapti/mapping rationale completed
```

Failed claims are not deleted. They become argument-fabric nodes with status
`flagged`, `hollow`, `outside_formal`, or `needs_review`.

### 2. Traditions are scoped, not flattened

The same word in different traditions is a different node until a bridge is
proved or manually accepted.

Bad:

```text
pramana = valid knowledge
```

Good:

```text
term: pramana
scope: nyaya
commitment: factive valid cognition

term: pramana
scope: dharmakirti
commitment: successful cognition via arthakriya
```

Bridge nodes are discovered by relation probing, not assumed by translation.

### 3. Boundary nodes are results

`HOLLOW`, `OUTSIDE_FORMAL`, `PARTIAL`, and `UNPROVED` are not errors. They are
epistemic findings.

Examples:

- A liberation claim may be outside formal proof.
- A text claim may be philologically settled but metaphysically unresolved.
- A consciousness-first implication may be a live candidate, not a theorem.

### 4. Numbers are downstream

Bayesian scores are allowed only after argument validation. They summarize
evidence movement; they do not replace the argument graph.

### 5. Negative controls are mandatory

The system must ingest known non-bridges from Sanskritree before bridge probing.
If it discovers a bridge that is in the negative-control set, the run fails.

---

## Canonical Node Types

| Node type | Meaning |
|-----------|---------|
| `source_span` | Exact text span, paper paragraph, passage, dataset result, or translation fragment |
| `claim` | Atomic assertion extracted from a source span |
| `argument` | Inference from hetu/evidence to sadhya/target |
| `candidate_explanation` | A serious possible answer to a question |
| `crux` | The live divergence point between candidates |
| `criticism` | A pressure test against a claim/candidate |
| `falsifier` | Concrete condition that would weaken or defeat a claim |
| `formal_node` | Imported Sanskritree/Lean proof-engine node |
| `bridge` | Formal or reviewed equivalence/subsumption relation |
| `boundary` | HOLLOW/OUTSIDE_FORMAL/PARTIAL result |
| `state_of_play` | Current best answer and live unresolved points |

---

## Canonical Edge Types

| Edge type | Meaning |
|-----------|---------|
| `supports` | Source/claim/argument supports target |
| `attacks` | Source/claim/argument weakens target |
| `rephrases` | Same or near-same content in different wording |
| `instantiates` | Concrete case instantiates a general rule |
| `presupposes` | Claim depends on another commitment |
| `contradicts` | Logical or evidential contradiction |
| `subsumes` | One claim entails a weaker claim |
| `bridges` | Two independently scoped nodes share formal structure |
| `decomposes_to` | Claim decomposes into child claims |
| `targets` | Claim bears on feature/discriminator/question/candidate |
| `falsified_by` | Falsifier/criticism defeats a node |
| `outside_formal` | Formal proof engine stopped at a boundary |

---

## Nyaya Gate

The Nyaya gate is a validation layer, not a metaphysical authority.

It uses:

| Nyaya concept | Fabric role |
|---------------|-------------|
| `pramana` | Evidence mode |
| `vyapti` | Mapping rule from evidence to target |
| `hetvabhasa` | Fallacy/defect check |
| `nigrahasthana` | Debate defeat tracking |
| `tarka` | Falsifier generation |
| 5-member inference | EO / argument reconstruction template |

### Pramana Metadata

Do not replace the existing truth-map dimensions blindly. Store both:

```json
{
  "evidence_dimension": "empirical",
  "pramana": "pratyaksa",
  "tradition_scope": "neuroscience"
}
```

Recommended mapping:

| `pramana` | Use |
|-----------|-----|
| `pratyaksa` | Direct observation, instrumentation, phenomenological givenness |
| `anumana` | Inference, formal argument, theorem, model consequence |
| `upamana` | Analogy, structural comparison, cross-tradition bridge candidate |
| `sabda` | Textual testimony, expert testimony, primary source claim |
| `formal_proof` | Lean-checked theorem or type-correct reconstruction |
| `mixed` | Explicitly multi-mode claim; must be split if it affects weight |

### Hetvabhasa Checks

Each claim gets a five-part defect record:

| Defect | Check |
|--------|-------|
| `savyabhicara` | Does hetu fail to imply sadhya because counterexamples exist? |
| `viruddha` | Does hetu actually support the opposite conclusion? |
| `asiddha` | Is hetu itself unestablished? |
| `satpratipaksa` | Is there an equally strong counter-inference? |
| `badhita` | Is the conclusion contradicted by stronger evidence? |

The gate never silently discards evidence. It labels the defect and controls
whether the claim can move posterior state.

### Gate Outcomes

| Outcome | Meaning | Engine effect |
|---------|---------|---------------|
| `accepted` | Claim passes minimum checks | may update runtime |
| `accepted_with_penalty` | Claim is usable but has explicit defects | may update with capped effect |
| `needs_review` | Missing rationale, weak mapping, or unclear scope | no automatic update |
| `hollow` | No falsifier or no truth conditions | no posterior update |
| `outside_formal` | Meaningful but not formalizable | no formal status; may still enter non-formal evidence layer |
| `refuted` | Defeated by contradiction or stronger evidence | can attack candidate/claim |

---

## Sanskritree Integration

Use Sanskritree as a formal-oracle package, not as a replacement truth map.

### Directly Importable Components

| Sanskritree component | Truth-map role |
|----------------------|----------------|
| `proof_engine.algorithm.process_claim` | sayability/decomposition/proof-status gate |
| `proof_engine.bnf.parse_nnexpr` | validate NNExpr syntax before formal probing |
| `proof_engine.fol_lean_bridge` | map Nyaya/Dharmakirti terms to Lean type candidates |
| `proof_engine.bridge_probe` | discover SUBSUMES/BRIDGES/CONTRADICTS/OVERLAPS |
| `proof_engine.ground_truth` | seed primitives, claims, negative controls |
| `proof_engine.validation` | enforce validation-set pass before production |
| `proof_engine.db` | reference proof graph schema |

### Imported Lean Assets

| Lean file | Role |
|-----------|------|
| `Foundation.lean` | basic logic lemmas and set scaffolding |
| `Sanskrit.lean` | Dharmakirti cognition primitives |
| `IIT.lean` | IIT scaffolding and Phi-facing terms |
| `Sanskritree/Core/Entity.lean` | interpretation entities |
| `Sanskritree/Semantics/Relation.lean` | relation axioms |
| `Sanskritree/Decision.lean` | decision layer |
| `Sanskritree/LayerB.lean` | semantic layer |

### Boundary Contract

Truth map must store Sanskritree status exactly:

```text
PROVED | UNPROVED | PARTIAL | HOLLOW | OUTSIDE_FORMAL | REFUTED
```

Never convert `PROVED` into "metaphysically true." It means only:

```text
the formalized reconstruction follows under the declared axioms
```

---

## Argument Evaluation

The right computational model is weighted bipolar argumentation, not flat Bayes.

Use the graph as the primary state:

```text
candidate_explanation
  supported by arguments
  attacked by criticisms
  bridged/subsumed/contradicted by formal nodes
  constrained by evidence claims
```

The engine can compute:

- acceptability score for each candidate
- live attackers with no answer
- strongest supporters
- unresolved cruxes
- bridge confidence
- evidence movement
- provenance path

But the UI should show the structure before showing any scalar.

---

## ML Policy

Use ML only as a proposal engine.

Allowed:

- source retrieval
- claim extraction
- argument mining
- support/attack/rephrase edge suggestions
- duplicate claim clustering
- hetvabhasa candidate detection
- tarka falsifier drafting
- GraphRAG subgraph retrieval
- Lean premise retrieval / proof-search assistance
- next-crux ranking

Not allowed:

- final truth decisions
- hidden weight assignment
- automatic bridge acceptance
- automatic tradition merging
- proof acceptance without Lean
- posterior movement from unvalidated claims

Start with retrieval, embeddings, rerankers, and active learning. Do not train a
GNN until there are enough reviewed graph edits to justify it.

---

## GraphRAG Shape

Use three retrieval layers:

```text
L1 canonical topic/question/candidate nodes
L2 extracted claim/argument/crux nodes
L3 exact source-span provenance nodes
```

Preserve, do not collapse:

- Different traditions keep separate term nodes.
- Different claims about the same source stay separate until reviewed.
- Contradictions are edges, not merge conflicts.
- A source span remains attached to every generated answer.

Retrieval query should return a bounded subgraph:

```text
question -> live candidates -> top supporters/attackers -> unresolved cruxes
         -> source spans -> formal statuses -> negative controls
```

---

## Flagship Build Target

First proof-of-concept:

```text
q:reflexivity-intrinsic-or-constructed
```

Candidates:

1. Abhinavagupta / Pratyabhijna: intrinsic self-manifestation.
2. Dharmakirti / Buddhist no-self: conditioned cognition without enduring Self.
3. Nanavira: structural reflexivity without hidden substance.
4. Higher-order / self-model theories: reflexivity as constructed operation.

Cruxes:

- Does recognition require intrinsic self-manifestation?
- Can reflexivity be constructed without presupposing manifestness?
- Does local reflexivity license universal consciousness?
- Does no-self defeat the owner of reflexivity or reflexivity itself?
- Can neuroscience distinguish self-model reflexivity from manifestness?

Expected result:

```text
Local structural reflexivity may become strongly supported.
Universal consciousness remains a separate, weaker step.
Dharmakirti/Nanavira pressure Abhinavagupta exactly at universalization.
Abhinavagupta pressures Buddhist accounts exactly at manifestness.
```

This is the kind of locally solvable result that can update the larger reality
brief without pretending to solve all metaphysics.

---

## New Files Added With This Architecture

| File | Purpose |
|------|---------|
| `TRUTHMAP-ARGUMENT-FABRIC.md` | This architecture |
| `truthmap-argument-schema.sql` | Additive SQLite/D1 schema for argument fabric |
| `scripts/nyaya-truthmap-gate.py` | Standalone pre-ingestion gate for packets/claims |

---

## Research Anchors

- AIF / Argument Web: structured support, attack, rephrase graphs.
- Weighted bipolar argumentation: graph-native support/attack evaluation.
- GraphRAG: provenance-preserving retrieval over source/claim/argument graphs.
- LeanDojo / Pantograph / ReProver: formal proof assistance under Lean verification.
- Sanskritree: tradition-scoped formalization, negative controls, boundary nodes.

The novel part is not any one tool. It is the integration:

```text
Sanskrit philology + Nyaya validation + formal proof boundary +
argument graph + provenance graph + Bayesian trend view + reality brief
```

