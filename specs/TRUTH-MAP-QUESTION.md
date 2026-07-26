# Truth Map Question — Full Spec

A Truth Map Question is a **node in the Bayesian belief network** that tracks the system's confidence about a specific proposition, the evidence for and against it, and its relationship to other questions. It is the central epistemic object that everything else serves.

---

## 1. Schema Reconciliation Problem

Three incompatible schemas currently exist in the codebase:

| Aspect | Schema A (actual q-*.json) | Schema B (05-SOURCE-METAPHYSICS.md) | Schema C (truthengine-propagation.py) |
|--------|---------------------------|-------------------------------------|---------------------------------------|
| File | `content/source-metaphysics/q-*.json` | magnum-opus spec | `truthengine-propagation.py` |
| Confidence | Raw float 0-1 | Raw float 0-1 | Computed from log-odds via sigmoid |
| Evidence | `evidence_for[]` with `{source, claim, weight, type}` | Same as A but richer type system | `ClaimRecord` with `log_bayes_factor`, `w_rel/map/aux/dep` |
| Evidence storage | Inline in the JSON file | Inline in the JSON file | Separate D1 table, append-only |
| Status | `underdetermined/plausible/strongly_supported/speculative/incompatible/unasked` | Same | Not stored — derived from confidence |
| Parent/child | Direct references via `parent_question`/`sub_questions[]` | Same hierarchy | Not represented — features linked to branches |
| Feature model | Single question = single node | Single question = single node | Each question is a FeatureState with prior_log_odds |
| Paradigm tracking | None | None | `paradigm` tag on each ClaimRecord |
| Supersession | None — edit in place | None — edit in place | `supersedes` chain, append-only |

---

## 2. Unified Schema (Proposal)

The reconciled model: **questions are git files, claims are D1 records.** The question file stores metadata and derived state. The evidence log in D1 is the source of truth for all weight computations.

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "TruthMapQuestion",
  "type": "object",
  "required": [
    "question_id", "schema_version", "question", "tags",
    "status", "branches", "provenance"
  ],
  "properties": {
    "question_id": {
      "type": "string",
      "pattern": "^q:[a-z0-9_-]+$"
    },
    "schema_version": { "type": "integer", "minimum": 1 },
    "question": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "description": "The exact question being investigated"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "status": {
      "type": "string",
      "enum": ["unasked", "underdetermined", "plausible", "strongly_supported", "speculative", "incompatible"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Computed by propagation engine. Read-only in file."
    },
    "feature_ids": {
      "type": "array",
      "items": { "type": "string", "pattern": "^F\\d+$" },
      "description": "Which truth map features (F1-F8) this question bears on"
    },
    "branches": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^B[1-6]$"
      },
      "description": "Which interpretation branches this question is relevant to"
    },
    "best_answer": {
      "type": "string",
      "maxLength": 1000
    },
    "parent_question": {
      "type": ["string", "null"],
      "pattern": "^q:[a-z0-9_-]+$"
    },
    "sub_questions": {
      "type": "array",
      "items": { "type": "string", "pattern": "^q:[a-z0-9_-]+$" }
    },
    "related_ros": {
      "type": "array",
      "items": { "type": "string" }
    },
    "related_essays": {
      "type": "array",
      "items": { "type": "string" }
    },
    "related_videos": {
      "type": "array",
      "items": { "type": "string" }
    },
    "provenance": {
      "type": "object",
      "required": ["last_updated", "last_updated_by"],
      "properties": {
        "last_updated": { "type": "string", "format": "date-time" },
        "last_updated_by": { "type": "string" },
        "git_commit": { "type": "string" }
      }
    }
  }
}
```

**Claim records live in D1, not in the question file.** Multi-feature targeting must be normalized through `claim_features`; do not query JSON arrays with `LIKE`.

```sql
CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL,           -- FK to truth_map_question
  source_type TEXT NOT NULL,           -- 'ro', 'eo', 'essay', 'video', 'dataset'
  source_id TEXT NOT NULL,
  evidence_role TEXT NOT NULL DEFAULT 'primary',
  paradigm TEXT,                       -- 'trika', 'IIT', 'neuroscience', etc.
  log_bayes_factor REAL NOT NULL,
  w_rel REAL NOT NULL DEFAULT 1.0,    -- relevance
  w_map REAL NOT NULL DEFAULT 1.0,    -- mapping quality
  w_aux REAL NOT NULL DEFAULT 1.0,    -- source reliability
  lbf_confidence REAL NOT NULL DEFAULT 1.0,
  claim_text TEXT,                     -- human-readable claim
  falsifier TEXT,                      -- structured JSON falsifier
  supersedes TEXT,                     -- claim_id this replaces
  superseded_by TEXT,                  -- claim_id that replaced this
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (question_id) REFERENCES truth_map_questions(question_id)
);

CREATE TABLE claim_features (
  claim_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  PRIMARY KEY (claim_id, feature_id),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX idx_claims_question ON claims(question_id);
CREATE INDEX idx_claims_paradigm ON claims(paradigm);
CREATE INDEX idx_claims_supersedes ON claims(supersedes);
CREATE INDEX idx_claim_features_feature ON claim_features(feature_id);
```

---

## 3. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| T01 | question doesn't end with "?" | Auto-append "?" |
| T02 | status = "strongly_supported" and confidence < 0.6 | Reject — confidence must match status |
| T03 | feature_ids is empty | Warn — question not linked to any feature |
| T04 | sub_questions includes a question_id that doesn't exist | Auto-create sub-question as "unasked" |
| T05 | parent_question is set AND status is more certain than parent | Warn — child can't be more certain than parent |
| T06 | status changes from answered to active without new evidence | Reject — must have new evidence to reopen |
| T07 | claims entry has no falsifier | Warn — claims without falsifiers are not knowledge |
| T08 | branch probabilities are presented as posterior truth | Reject — branches are relative support scores unless a branch likelihood model exists |

---

## 4. Versioning

Truth map questions are **appended to, never edited.** The question JSON file updates only for:
- Status changes (recomputed by propagation engine)
- best_answer revisions (manual or agent-driven)
- Parent/child relationship changes
- Schema migrations

Evidence entries are **never deleted** — only superseded via the `supersedes` chain.

---

## 5. Storage

```
Path: content/source-metaphysics/q-{slug}.json  (question metadata, git)
D1:   claims table                                (claims, append-only)
D1:   claim_features table                        (claim-to-feature join table)
D1:   feature_states table                         (computed posteriors)
```

```sql
CREATE TABLE truth_map_questions (
  question_id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'unasked',
  confidence REAL NOT NULL DEFAULT 0.0,
  feature_ids TEXT,              -- JSON array
  branches TEXT,                 -- JSON array
  parent_question TEXT,
  best_answer TEXT,
  last_updated TEXT,
  last_updated_by TEXT
);

CREATE TABLE feature_states (
  feature_id TEXT PRIMARY KEY,   -- F1, F2, ..., F8
  prior_log_odds REAL NOT NULL,
  current_log_odds REAL NOT NULL,
  probability REAL NOT NULL,
  last_updated TEXT
);

CREATE TABLE branch_probabilities (
  branch_id TEXT PRIMARY KEY,    -- B1, B2, ..., B6
  probability REAL NOT NULL,
  score_type TEXT NOT NULL DEFAULT 'relative_support',
  last_updated TEXT
);
```

---

## 6. Access Patterns

| Operation | Frequency | Source |
|-----------|-----------|--------|
| Read question metadata | Every page load | File or D1 cache |
| Read all claims for a question | Every propagation run | D1 `claims` + `claim_features` |
| Add new evidence | Per publish | D1 append |
| Recompute confidence | Per evidence entry + nightly | Propagation engine |
| Search across questions | Per user search | D1 |
| Check staleness | Weekly cron | D1 last_updated |

---

## 7. Migration from Current State

The 6 existing q-*.json files need:
1. Add `feature_ids`, `branches`, `provenance.git_commit` fields
2. Remove inline `evidence_for[]` and `evidence_against[]` — migrate to D1 `claims` and `claim_features`
3. Add `schema_version` field
4. Bump to v2 format

Migration script: `scripts/migrations/truth_map_v1_to_v2.py`

---

## 8. Codex Design Decisions

### Winning Model

Use **Option C: hybrid**.

Questions remain git files because they are editorial objects: wording, relationships, tags, and best-answer text need reviewable diffs. Claims live in D1 because they are append-only evidence events that must be queryable by question, feature, source, paradigm, and recency. Feature posteriors are computed state. The old `q-*.json` evidence arrays become migration input and optional read views, not the canonical evidence store.

Canonical ownership:

| Data | Owner |
|------|-------|
| Question wording, parent/child graph, tags | Git JSON |
| Claim text, weights, falsifier, source lineage | D1 `claims` |
| Claim-to-feature mapping | D1 `claim_features` |
| Confidence/status/posteriors | Propagation engine, cached to D1/git |
| Branch support display | Derived from feature states |

### Falsifier Structure

Use a structured falsifier object. A plain string is not enough for validation, scheduling, or later test results.

```json
"falsifier": {
  "type": "empirical|textual|formal|experiential|comparative|operational|none",
  "condition": "Specific condition that would defeat or materially weaken the claim.",
  "observable": "What must be inspected or measured.",
  "method": "How the test is performed.",
  "threshold": "Pass/fail criterion when applicable.",
  "scope": "Which part of the claim the falsifier applies to.",
  "status": "untested|tested_failed|tested_survived|not_currently_testable|unfalsifiable",
  "result_ref": null
}
```

Unfalsifiable claims may be stored for hermeneutic context, but they must not receive high evidential weight. Scientific or operational claims without a falsifier should fail the publish gate unless explicitly marked `not_currently_testable` with a reason.

### Branch Derivation

The current branch calculation is not a true posterior probability model. Branches overlap and features are not independent, so multiplying feature probabilities and normalizing can create artifacts.

Decision: rename the interpretation as **relative branch support**. It is acceptable for ranking and UI, but it must not be used as calibrated probability or fed back into feature updates.

If calibrated branch probabilities are required later, branches must become explicit hypotheses with `P(feature | branch)` likelihood profiles and either a dependency/covariance model or a deliberately naive-Bayes label.
