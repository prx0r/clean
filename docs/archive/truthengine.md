# Truth Engine — The Actual Math and Logic

## The Fundamental Tension: Deutsch vs. Bayes

These two are not the same project, and conflating them is where most systems go wrong.

### Deutsch / Popper — Explanatory Quality

Good explanations are "hard to vary" — the parts of the theory are tightly coupled so that changing any detail destroys the explanation. This is a structural property of theories, not a probabilistic one.

Deutsch's criterion: none of the details about how, say, the Earth rotates around the Sun at a certain angle in a certain orbit can be easily modified without changing the theory's coherence. He's concerned with explanatory quality, not credence.

Key concept: a good explanation is one that could not be easily different and still explain the same data. The more constrained the explanation, the better it is. This is the opposite of "flexible" or "adaptive" explanations which can explain anything — those are worthless.

### Bayes — Credence Updating

Bayesianism is about updating probabilities given evidence. It tells you how confident to be in a proposition, not whether the proposition is a good explanation.

```
P(H|E) = P(E|H) * P(H) / P(E)
```

Bayes handles credence. It does not handle explanatory structure. You can have a high-credence belief that is a terrible explanation (e.g., "the sun rises because of a consistent natural pattern" is a better explanation than "the sun rises because gravity pulls it up each morning" — both might have high Bayesian credence but the second is much harder to vary).

### When They Conflict

A theory can score well on Bayes (high posterior probability given evidence) and poorly on Deutsch (easy to vary, bad explanation). A theory can score well on Deutsch (tightly constrained, hard to vary) and poorly on Bayes (low prior, weak evidence so far).

The truth engine needs both criteria working together. Good explanations should be both hard to vary AND well-supported by evidence.

---

## The Truth Map Scoring Function

### Evidence Weight

Each piece of evidence has a weight (0.0–1.0) representing how much it moves the needle on a question. Weight is computed from:

```
weight = source_reliability * relevance * specificity
```

- `source_reliability`: How trustworthy is the source (0.0–1.0)
- `relevance`: How directly does this evidence bear on the question (0.0–1.0)
- `specificity`: How precisely does it address the question rather than adjacent topics (0.0–1.0)

### Confidence Computation

Confidence is computed from evidence weights, not stored manually:

```
confidence = sum(evidence_for.weight) / (sum(evidence_for.weight) + sum(evidence_against.weight) + 1)
```

The `+1` prevents division by zero and biases toward uncertainty when evidence is sparse.

- 0.4 for vs 0.3 against = 0.4/(0.4+0.3+1) = 0.235 — underdetermined
- 2.0 for vs 0.2 against = 2/(2+0.2+1) = 0.625 — plausible
- 5.0 for vs 0.5 against = 5/(5+0.5+1) = 0.769 — strongly supported

### Explanation Scoring (Deutsch)

```
explanation_score = problems_solved - unfalsifiable_claims_added
```

- `problems_solved`: How many distinct phenomena does this explanation account for?
- `unfalsifiable_claims_added`: How many new untestable assumptions does it introduce?

A higher score is better. This is not a probability — it's a measure of explanatory power.

### Combined Metric

```
truth_score = confidence * explanation_score
```

This combines Bayesian credence with Deutsch explanatory quality. A high-confidence bad explanation scores low. A low-confidence excellent explanation scores medium (more evidence needed). A high-confidence excellent explanation scores highest.

---

## The Falsifier Field

Every claim in the truth map must have a falsifier — a specific, testable condition that would prove the claim wrong. Without a falsifier, the claim is not knowledge in Popper's sense.

```
falsifier:
  condition: "A subject with verified zero prerequisite knowledge of domain D
              correctly explains a depth-3 claim in D, verified by blinded
              expert panel scoring on binary adequate/inadequate scale, N>20"
  status: "untested"
  last_tested: null
  result: null
```

The falsifier field transforms a claim from an assertion into a testable hypothesis. It is the boundary of knowledge (M.4).

---

## The Geometric Engine Integration

The GeometricEngine trains edge weights from transition data:

```
state → action → next_state
```

For the truth map, this becomes:

```
question → evidence_added → confidence_change
```

Training data: every time an RO, essay, or video adds evidence to a truth map question, the transition is recorded. Over time, the graph learns which types of evidence most effectively change confidence for which types of questions. This allows the system to predict "if we add evidence of type X to question Y, confidence will move by approximately Z."

### Recommendation

No LLM in the cognition path. Given a user's current context (what they're watching, what they asked), the graph traverses from the current node to the highest-weighted neighbor. This returns the next content to show. No API call. No latency. No cost.

---

## The Append-Only Rule

Never edit existing evidence in the truth map. Only add new entries. The provenance log tracks every change.

If evidence is outdated, add a new entry with a higher weight and a note superseding the old one. The confidence computation naturally weights newer evidence higher if desired, but the old evidence remains for audit.

This prevents the truth map from silently changing its conclusions without an audit trail. It's the same principle as a blockchain ledger — append-only, immutable history, transparent.

---

## The Publish Gate

Every piece of content (essay, video, RO) must link to ≥1 truth map question before it can be published. This forces every piece of content to answer "what question does this bear on?"

Gate check:
```
content.claims_extracted → truth_map_questions_mapped → evidence_entries_created → publish_allowed
```

If content makes claims that don't map to any truth map question, either:
1. The claims are new → create truth map entry for the question
2. The claims are irrelevant → don't publish (the content has no epistemic value)

---

## The Staleness Check

Questions not updated in 90 days get flagged. The hypothesis engine deprioritizes them. If audience interest drops below threshold for 180 days, they're archived.

```
UPDATE truth_map SET status = 'stale'
WHERE last_updated < datetime('now', '-90 days')
```

---

## Summary

| Component | Purpose | Method |
|-----------|---------|--------|
| Confidence | How sure are we? | Bayesian evidence weighting |
| Explanation Score | How good is the explanation? | Deutsch hard-to-vary criterion |
| Truth Score | Combined quality | confidence * explanation_score |
| Falsifier | Boundary of knowledge | Popperian testable condition |
| Geometric Engine | No-LLM recommendation | Trained weight graph traversal |
| Append-Only Log | Audit trail | Immutable evidence history |
| Publish Gate | Quality control | Claims must map to truth map questions |
| Staleness Check | Freshness | 90-day expiry, archive at 180 |
