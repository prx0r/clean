# Truth Changes 5 — Refutation-Led Reality Map

## The Core Clarification

Yes: the point of the project is to ask interesting, pressure-bearing questions
about reality and maintain our best current account of what survives.

No: the point is not to prove `reality = branch B4` or let a Bayesian engine
settle metaphysics by arithmetic.

The truth map should answer:

> Given the best arguments, texts, experiments, translations, contemplative
> reports, and formal models we have right now, what explanations remain live,
> what has been weakened, what would change our mind, and what should we test
> next?

That is a Popper/Deutsch project first. Bayesian machinery is useful, but only
as bookkeeping under a stronger criterion: whether an explanation survives
serious attempts to break it.

---

## Diagnosis: What Went Wrong

The old engine direction was not silly. It solved real problems:

- It prevented unsupported claims from floating free.
- It forced every claim to name a target.
- It made before/after belief changes auditable.
- It created a route toward provenance: paper -> claim -> target -> posterior movement.

But it was the wrong center of gravity.

The center of gravity cannot be "assign weights to claims and compute reality."
That creates false precision and hides the real work: reconstructing arguments,
finding cruxes, generating counterexamples, testing semantic ambiguity, and
asking whether a theory is hard to vary.

The engine should serve the research process. It should not replace it.

---

## The New Governing Model

The project should be a **refutation-led explanatory map**.

Core objects:

| Object | Purpose |
|--------|---------|
| Question | The exact problem being investigated |
| Candidate explanation | A serious possible answer |
| Crux | The point where explanations diverge |
| Criticism | A pressure test against a candidate |
| Falsifier | A condition that would defeat or materially weaken the candidate |
| Surviving position | The best current answer after criticism |
| Implication | What the surviving answer would say about broader reality |

The atomic unit is no longer just a weighted claim. The atomic unit is:

```text
question -> candidate explanations -> cruxes -> criticisms -> surviving answer -> implications
```

Claims still exist, but they are evidence inside that larger structure.

---

## What "Best Idea Of Reality Right Now" Means

It means:

1. The best surviving explanations are listed explicitly.
2. Each explanation has known open problems.
3. Each explanation has tests or criticisms that could weaken it.
4. Semantic ambiguity is visible.
5. The system distinguishes local resolution from global metaphysical victory.
6. Broader implications are stated conditionally.

Good output:

```text
Question: Is reflexive awareness intrinsic or constructed?

Current best answer:
Structural reflexivity in human experience is very hard to deny. Ñāṇavīra-style
analysis makes a strong case that experience can include its own occurrence
without requiring a hidden soul-substance. Abhinavagupta can absorb this as
finite vimarśa, but still owes an argument from local reflexivity to universal
consciousness.

Status:
Local phenomenological claim: strong.
Universal metaphysical claim: live but not settled.

What would move it:
A successful account of recognition/reflexivity that does not smuggle in
self-manifestation would weaken Abhinavagupta. A demonstration that all
higher-order/reflexive models presuppose manifestness would strengthen him.
```

Bad output:

```text
B4 probability = 0.73, therefore consciousness-first metaphysics is probably true.
```

---

## Refutation Types

Different questions can be "solved" in different ways. The system needs to mark
which kind of pressure applies.

| Refutation type | What can be defeated |
|-----------------|----------------------|
| Empirical | Operational claims, correlations, causal mechanisms, predictions |
| Formal | Logical structure, entailment, consistency, impossibility results |
| Philological | Misread Sanskrit, wrong attribution, unstable translation, anachronism |
| Phenomenological | Misdescription of experience, missing invariants, failed introspective replication |
| Comparative | A rival theory explains the same problem with fewer movable assumptions |
| Semantic | A question dissolves because key terms were equivocated |
| Pragmatic | A theory cannot generate further research, tests, distinctions, or consequences |

This is why Dharmakīrti vs Abhinavagupta matters. That debate is not "vibes."
It has refutable structure: perception, exclusion, self-awareness, recognition,
reflexivity, and whether a self-manifesting subject is needed. Some local claims
can be defeated by better textual reconstruction or sharper argument.

---

## Deutsch Layer: Explanation Quality

Every candidate explanation should receive a non-probabilistic explanation
profile.

| Field | Question |
|-------|----------|
| Problems solved | What does this explain that rivals struggle with? |
| Hard-to-vary core | Which details cannot be changed without breaking the explanation? |
| Movable parts | Which parts are flexible enough to explain anything? |
| New mysteries added | What unexplained primitives does it introduce? |
| Risky commitments | What could turn out false? |
| Rival pressure | Which competitor currently hurts it most? |
| Research yield | Does it generate tests, distinctions, translations, or models? |

This should be the primary ranking layer.

Bayesian/posterior scores then become secondary:

```text
explanation_state = {
  "hard_to_vary": "high",
  "problems_solved": ["reflexivity", "recognition", "manifestness"],
  "new_mysteries": ["universalisation", "plurality", "brain dependence"],
  "survives_current_criticism": true,
  "posterior_vector": {...},
  "provenance": [...]
}
```

---

## Demote The Engine

The engine should become:

1. A provenance ledger.
2. A disagreement detector.
3. A research-priority machine.
4. A stale-question detector.
5. A way to ask "which evidence moved this view?"

It should not be:

1. A metaphysical oracle.
2. A single-number truth machine.
3. A replacement for argument reconstruction.
4. A replacement for Sanskrit philology.
5. A way to hide interpretive choices behind decimals.

The current dimensional engine is still useful. Its correct role is:

```text
show me which evidence affected which target, in which dimension, under which
assumptions, and where the dimensions diverge
```

That is valuable. It is not final judgment.

---

## Sanskritree Lesson

The Sanskritree redesign is the model: the old factor graph and sense-ranker were
too lossy because philology requires whole-work understanding, context,
commentarial comparison, adversarial review, and revision.

Truth Map needs the same correction.

Bad:

```text
claim extracted -> weight assigned -> posterior updated -> answer produced
```

Better:

```text
source/text/problem assembled
-> strongest reconstruction of each side
-> crux extraction
-> adversarial criticism
-> evidence/provenance log
-> surviving answer with open problems
-> next test/question generated
```

The LLM/research agent should act like a critic-philologist-philosopher using
the database as its library. The database should not pretend to be the
philosopher.

---

## Question Model v2

Each Truth Map Question should become a research dossier, not just a posterior.

```json
{
  "question_id": "q:reflexivity-intrinsic-or-constructed",
  "question": "Is reflexive awareness intrinsic to experience or a constructed higher-order operation?",
  "why_it_matters": "This is the local crux between Buddhist no-self analyses, higher-order theories, and Pratyabhijñā vimarśa.",
  "status": "live_crux",
  "resolution_level": "local_phenomenological",
  "candidate_explanations": [
    {
      "id": "cand:abh-vimarsa",
      "name": "Intrinsic self-manifestation",
      "best_case": "Experience is not merely present; its presence is self-apprehending.",
      "hard_to_vary_core": [
        "manifestness cannot be explained by non-manifest structure",
        "recognition requires reflexive self-presence"
      ],
      "current_problems": [
        "universalisation from local reflexivity",
        "relation to brain dependence",
        "risk of reifying subjectivity"
      ],
      "falsifiers": [
        "A complete account of recognition/reflexivity that does not presuppose self-manifestation"
      ]
    },
    {
      "id": "cand:dharmakirti-apoha-reflexivity",
      "name": "Conditioned reflexivity without Self",
      "best_case": "Reflexivity is a structured feature of cognition, not evidence for an ultimate subject.",
      "hard_to_vary_core": [
        "identity is exclusion/structure, not substance",
        "selfhood is constructed from cognitive operations"
      ],
      "current_problems": [
        "whether manifestness is assumed rather than explained",
        "whether reflexive awareness can be fully non-substantial without becoming eliminative"
      ],
      "falsifiers": [
        "A demonstration that conditioned cognition cannot account for immediate self-presence"
      ]
    }
  ],
  "cruxes": [
    "Does recognition require intrinsic self-manifestation?",
    "Can reflexivity be constructed without presupposing manifestness?",
    "Does local reflexivity license universal metaphysics?"
  ],
  "best_current_answer": "Structural reflexivity is strongly supported; universal consciousness is not entailed.",
  "implications_if_true": [
    "Abhinavagupta is locally right about the structure of experience",
    "Buddhist no-self remains a live challenge to reifying that structure",
    "The consciousness-fundamental question must be split into local manifestness and universalisation"
  ]
}
```

---

## How To Treat Big Questions

"Is consciousness fundamental?" is too broad as a top-level engine question.

Break it into cruxes:

| Crux | What it can decide |
|------|--------------------|
| Is manifestness reducible to third-person structure? | Whether B4 remains live |
| Is reflexivity intrinsic or higher-order/constructed? | Whether vimarśa is needed |
| Can brain dependence be modeled without making consciousness derivative? | Whether idealism survives neuroscience |
| Does universalisation follow from local phenomenology? | Whether Trika gets from experience to Śiva |
| Can physicalism explain phenomenal presence without redefining it away? | Whether physical supervenience survives |
| Can contemplative insight distinguish ontology from self-model plasticity? | Whether nondual reports bear metaphysically |

Then the system can say:

```text
Consciousness-first metaphysics is not proven.
But several narrower claims are currently live:
- manifestness remains underexplained by physical/functionalist accounts
- reflexivity appears structurally deep in experience
- brain dependence strongly constrains any consciousness-first view
- universalisation is the weakest Trika step
```

That is already a useful best-current map of reality.

---

## What Counts As Solved

A question can be marked solved only at a specific resolution level.

| Resolution level | Meaning |
|------------------|---------|
| `philological` | We know what the text or author most likely claims |
| `local_argument` | A specific argument succeeds or fails |
| `phenomenological` | A structure of experience is well characterized |
| `empirical_constraint` | A mechanism or correlation is strongly constrained |
| `formal` | A theorem/no-go result decides a possibility claim |
| `branch_relevant` | The result materially changes which metaphysical branches remain live |
| `global_metaphysical` | A whole reality-branch is decisively supported or defeated |

Most real progress will be below `global_metaphysical`. That is fine.

The system should often say:

```text
Solved locally; globally still open.
```

That is not failure. That is intellectual honesty.

---

## New Pipeline

### 1. Ask a pressure-bearing question

Reject broad topics. Use exact explanatory problems.

### 2. Build the live option set

For each question, identify the strongest candidate explanations, not just
evidence for/against one favored answer.

### 3. Extract cruxes

Ask where the candidates actually disagree.

### 4. Run adversarial reconstruction

Each candidate must be steelmanned, then attacked.

### 5. Attach evidence and provenance

Claims enter the append-only evidence log, with dimensions and falsifiers.

### 6. Produce a state-of-play answer

The answer must include:

- best current explanation
- what has been weakened
- what remains unresolved
- what would change the result
- what follows if the answer holds

### 7. Generate the next question

The next question should attack the weakest live crux or highest expected
information gain discriminator.

---

## Required New Files / Objects

### Candidate Explanation Object

```json
{
  "candidate_id": "cand:b4-nondual-consciousness-first",
  "question_id": "q:consciousness-fundamental",
  "name": "Nondual consciousness-first",
  "best_case": "...",
  "hard_to_vary_core": [],
  "movable_parts": [],
  "problems_solved": [],
  "new_mysteries": [],
  "rival_pressures": [],
  "falsifiers": [],
  "current_status": "live|weakened|defeated|merged|underdetermined"
}
```

### Criticism Object

```json
{
  "criticism_id": "crit:brain-damage-against-filter-idealism",
  "target_candidate_id": "cand:brain-as-filter",
  "type": "empirical_constraint",
  "claim": "Specific lesions produce specific content losses; a filter theory must predict the mapping, not merely say the filter is damaged.",
  "force": "strong",
  "reply_required": true,
  "candidate_reply": null,
  "status": "unanswered"
}
```

### State Of Play Object

```json
{
  "question_id": "q:consciousness-fundamental",
  "current_best_answer": "...",
  "confidence_language": "plausible but underdetermined",
  "solved_at_level": ["none"],
  "live_candidates": [],
  "weakened_candidates": [],
  "defeated_candidates": [],
  "open_cruxes": [],
  "next_tests": [],
  "implications": []
}
```

---

## UI: Reality Brief

The public/readable output should be a "Reality Brief", not a dashboard of
floating numbers.

For each major question:

```text
Question
Best current answer
What survives
What is weakened
What would change our mind
Why this matters for the larger map
Evidence provenance
Next best question
```

Numbers can appear, but only under provenance and disagreement views.

---

## Immediate Implementation Plan

### P0 — Create research dossier schema

Add JSON specs for:

- `CandidateExplanation`
- `Criticism`
- `Crux`
- `StateOfPlay`

### P0 — Convert the six seed questions

For each `content/source-metaphysics/q-*.json`, add:

- candidate explanations
- cruxes
- falsification routes
- current best answer with scope level

### P1 — Build one manual flagship dossier

Start with:

```text
q:reflexivity-intrinsic-or-constructed
```

Use Ñāṇavīra, Dharmakīrti, Abhinavagupta, higher-order theories, and minimal
phenomenal experience.

This is the right first target because it is locally solvable in a way the
broader "is consciousness fundamental?" question is not.

### P1 — Make the engine report state, not conclusions

Add a report layer that combines:

- candidate explanation status
- open criticisms
- dimensional posteriors
- convergence/disagreement
- provenance/blame

### P2 — Expected criticism gain

Replace raw expected information gain with:

```text
expected_criticism_gain =
  branch_discrimination
  + candidate_defeat_potential
  + semantic_clarification_value
  + research_yield
  - acquisition_cost
```

The best next question is the one most likely to break or sharpen a live
explanation.

---

## What To Stop Doing

Stop treating "confidence" as the main achievement.

Stop ingesting papers because they are adjacent to a theme.

Stop letting LLM extraction assign decimals without adversarial review.

Stop asking giant questions before splitting them into cruxes.

Stop treating traditions as evidence blobs. Dharmakīrti, Abhinavagupta,
Ñāṇavīra, IIT, active inference, and physicalism are structured explanations
with internal commitments. Model those commitments.

---

## Final Principle

The truth map is not a machine that knows reality.

It is a machine-assisted discipline for asking:

```text
What is the best explanation we currently have?
What exactly would break it?
What rival explains the same thing better?
What follows if this local answer survives?
What should we investigate next?
```

That is the project.

