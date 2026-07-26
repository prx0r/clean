# Truth Map Production Hardening

The engine must not pretend that metaphysical evidence weights are measurements.
Weights are reviewable judgments. The system is useful only if every posterior can
be traced back to the interpretive choices that produced it.

## Core Risks

| Risk | Failure mode | Production control |
|------|--------------|--------------------|
| Circular weight assignment | The extractor decides relevance and then the engine treats that relevance as objective | Store extractor identity, prompt version, reasoning, reviewer corrections, and weight deltas |
| Paradigm incommensurability | Trika, neuroscience, physics, and philosophy use different evidence norms | Maintain paradigm-lens views; do not collapse disagreement without showing per-lens posteriors |
| Semantic ambiguity | D1-D5 terms are contested, so target mapping is interpretive | Require target-fit reasoning and semantic notes for every discriminator claim |
| No decisive ground truth | Branches may never converge like empirical hypotheses | Present branch support as relative support, never truth probability |
| Selection bias | The corpus reflects what the pipeline acquired and understood | Keep an acquisition ledger with rejected/unrelated papers and search strategy metadata |
| Pseudo-precision | Decimal weights imply more certainty than exists | Always show weight decomposition, uncertainty class, and reviewer disagreement |

## Non-Negotiable UI Rule

Never show a feature, discriminator, or branch number without a provenance path:

```text
source -> claim -> target -> weight factors -> effective_lbf
       -> posterior_before/posterior_after -> branch support movement
```

The numeric posterior is the headline only if the trace is one click away.

## First-Class Provenance Views

### Per-source contribution

Query by `source_id` and show:

- every claim emitted by the source
- direct targets and derived targets
- `log_bayes_factor`, `w_rel`, `w_map`, `w_aux`, computed `w_dep`
- `effective_lbf`
- posterior before and after
- branch support before and after, once branch-delta tracing is added

Current implementation:

```bash
python scripts/provenance-report.py --source-id arxiv:1312.2007
```

### Blame by target

Query by `target_id` and rank records by absolute `effective_lbf`.

This answers:

- Which papers moved D4 most?
- Which claims are carrying B3 support indirectly?
- Which single source would change the map most if retracted?

Current implementation:

```bash
python scripts/provenance-report.py --target-id D4
```

### Reviewer disagreement

Needed next. Add a `claim_reviews` table:

```sql
CREATE TABLE claim_reviews (
  review_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL,
  reviewer_id TEXT NOT NULL,
  reviewer_type TEXT NOT NULL, -- human|agent
  prompt_version TEXT,
  target_id TEXT NOT NULL,
  log_bayes_factor REAL NOT NULL,
  w_rel REAL NOT NULL,
  w_map REAL NOT NULL,
  w_aux REAL NOT NULL,
  uncertainty_class TEXT NOT NULL,
  reasoning TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);
```

The engine can continue using an accepted claim weight, but the UI must show the
review distribution. Later, propagation can run under multiple reviewer lenses.

## Paradigm-Lens Rule

The production engine should expose at least three views:

| View | Meaning |
|------|---------|
| Global support | Current pooled model with dependence discounting |
| Paradigm lens | Recompute using only one paradigm or weighting family |
| Disagreement lens | Show variance between reviewer/paradigm evaluations |

If global support rises while paradigm lenses diverge, the system should report
"live disagreement", not convergence.

## Dimension-Vector Rule

The current runtime now exposes three first-class evidence dimensions:

| Dimension | Role |
|-----------|------|
| `empirical` | Experiments, formal models with operational predictions, adversarial collaborations, replication-sensitive science |
| `phenomenological` | Philosophical argument, semantic clarification, formal dialectic, explanatory scope |
| `contemplative` | Reproducible trained first-person reports, cross-tradition state taxonomies, practice-lineage checks |

Do not collapse these tracks into a single posterior in the production UI.
Display the vector plus convergence:

```json
{
  "D3": {
    "phenomenological": 0.91,
    "empirical": 0.07,
    "contemplative": 0.50,
    "convergence": 0.28
  }
}
```

Low convergence is not a defect. It is often the most important output because
it identifies where the traditions are making different commitments or using
different evidence standards.

## Paper-Informed Design Decisions

The Rosetta Stone paper (`arXiv:2409.20318`) supports the project direction, but
only conditionally: beliefs are useful bridge variables across phenomenology,
behaviour, and neural dynamics. The engine should therefore expose bridge
variables and mappings, not pretend that phenomenological and empirical evidence
are already commensurable.

The IIT/PP/Neurorepresentationalism adversarial review (`arXiv:2509.00555`) and
Cogitate adversarial test (`10.1038/s41586-025-08888-1`) support Bayesian
evidence accumulation in the empirical dimension, especially when predictions
are preregistered and the parties agree in advance what would count as
informative. They do not justify a hidden global trust bump.

Production rule: adversarial collaboration increases auditability before it
increases weight. Store protocol facts first; translate them into `w_aux` only
through an explicit reviewed decision.

Suggested protocol metadata:

```sql
CREATE TABLE evidence_protocols (
  protocol_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  protocol_type TEXT NOT NULL, -- adversarial_collaboration|preregistered|replication|review
  preregistered INTEGER NOT NULL DEFAULT 0,
  mutually_agreed_predictions INTEGER NOT NULL DEFAULT 0,
  independent_labs INTEGER NOT NULL DEFAULT 0,
  open_data INTEGER NOT NULL DEFAULT 0,
  open_code INTEGER NOT NULL DEFAULT 0,
  publish_any_result INTEGER NOT NULL DEFAULT 0,
  protocol_quality REAL,
  reasoning TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## Evidence Fusion Roadmap

The right next mathematical layer is not a bigger flat Bayesian posterior. Use
the current dimension vectors as the production surface, then add one of these
only when reviewer distributions exist:

| Method | Use when | Why |
|--------|----------|-----|
| Credal intervals / imprecise probabilities | Reviewers disagree on weights but agree on target semantics | Shows a posterior range instead of false decimal certainty |
| Dempster-Shafer conflict metrics | Evidence sources assign mass to incompatible or overlapping branch sets | Makes conflict visible without forcing premature normalization |
| Bayesian adversarial collaboration | Empirical theories make explicit competing predictions | Gives a common evidence metric for agreed severe tests |

For now, the engine should output posterior vectors and convergence/disagreement.
Do not fuse dimensions unless the report shows the assumptions that make the
fusion legitimate.

## Acquisition Ledger

Selection bias is not solved by math. Add a ledger for every search/acquisition
run:

```sql
CREATE TABLE acquisition_runs (
  run_id TEXT PRIMARY KEY,
  query TEXT NOT NULL,
  source_system TEXT NOT NULL,
  inclusion_policy TEXT NOT NULL,
  exclusion_policy TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE acquisition_candidates (
  run_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL, -- ingested|unrelated|rejected|pending
  reason TEXT,
  FOREIGN KEY (run_id) REFERENCES acquisition_runs(run_id)
);
```

The absence of evidence must itself be inspectable: what did the pipeline see and
decline to ingest?

## Production Standard

A truth-map update is production-ready only when it has:

1. Source provenance.
2. Claim text.
3. Target-fit reasoning.
4. Weight decomposition.
5. Falsifier or explicit non-testability reason.
6. Reviewer identity.
7. Before/after target movement.
8. Branch movement.
9. Paradigm lens tag.
10. Audit-visible acquisition context.

Anything less is a draft signal, not a belief update.
