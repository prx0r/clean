# Claim — Full Spec

A Claim is the **atomic unit of evidence** in the truth map. Every piece of content — an RO passage, an essay paragraph, a video timestamp, a dataset result — gets decomposed into claims. Each claim is a structured assertion that bears on one or more truth map features.

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "ClaimRecord",
  "type": "object",
  "required": [
    "claim_id", "schema_version", "source_type", "source_id",
    "target_feature_ids", "log_bayes_factor", "w_rel", "w_map", "w_aux",
    "paradigm", "claim_text"
  ],
  "properties": {
    "claim_id": {
      "type": "string",
      "pattern": "^cl:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 1
    },
    "source_type": {
      "type": "string",
      "enum": ["ro", "eo", "essay", "video", "dataset", "experiment", "translation", "user_report"]
    },
    "source_id": {
      "type": "string",
      "description": "ID of the source entity this claim was extracted from"
    },
    "target_question_id": {
      "type": "string",
      "pattern": "^q:[a-z0-9_-]+$",
      "description": "Which truth map question this claim provides evidence for"
    },
    "target_feature_ids": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "pattern": "^F\\d+$"
      },
      "description": "Which truth map features (F1-F8) this claim bears on"
    },
    "log_bayes_factor": {
      "type": "number",
      "description": "How much this claim moves the posterior. Positive = supports, negative = undermines."
    },
    "w_rel": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Relevance weight — how directly does this claim bear on the features?"
    },
    "w_map": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Mapping quality — how precisely does the evidence map to the claim?"
    },
    "w_aux": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Auxiliary weight — source reliability + specificity composite"
    },
    "paradigm": {
      "type": ["string", "null"],
      "enum": [null, "trika", "IIT", "active_inference", "neuroscience", "phenomenology", "analytic_idealism", "panpsychism", "madhyamaka", "neoplatonism", "sufism", "constructor_theory", "computational", "experimental", "contemplative"],
      "description": "Which paradigm produced this claim. Used for dependence discounting."
    },
    "claim_text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000,
      "description": "Human-readable statement of the claim"
    },
    "falsifier": {
      "type": "object",
      "properties": {
        "condition": {
          "type": "string",
          "description": "Testable condition that would disprove this claim"
        },
        "status": {
          "type": "string",
          "enum": ["untested", "tested_failed", "tested_survived", "unfalsifiable"]
        },
        "last_tested": {
          "type": ["string", "null"],
          "format": "date-time"
        },
        "result": {
          "type": ["string", "null"]
        }
      }
    },
    "is_retracted": {
      "type": "boolean",
      "default": false
    },
    "supersedes": {
      "type": ["string", "null"],
      "description": "claim_id of the claim this replaces"
    },
    "superseded_by": {
      "type": ["string", "null"],
      "description": "claim_id of the claim that replaced this"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "extracted_by": {
      "type": "string",
      "description": "Agent or human that extracted this claim"
    }
  }
}
```

---

## 2. Weight Computation

```
log_bayes_factor: -10 to +10 (signed, 0 = no effect)
  +1.0  = moderately supports
  +3.0  = strongly supports
  +10.0 = nearly decisive
  -1.0  = moderately undermines

w_rel: 0.0 to 1.0
  0.1 = tangentially related
  0.5 = somewhat relevant  
  1.0 = directly bears on the core question

w_map: 0.0 to 1.0
  0.3 = loose analogy or suggestive correspondence
  0.7 = clear structural mapping with some ambiguity
  1.0 = exact formal or empirical correspondence

w_aux: 0.0 to 1.0
  Preprint or single anecdote:         0.3
  Peer-reviewed single study:          0.6
  Meta-analysis or adversarial collab: 0.85
  Primary Sanskrit text (TO):          0.7
  Verified contemplative report:       0.5
  
w_dep: computed by propagation engine
  w_dep = 1.0 / (1.0 + alpha * n_prior)
  where n_prior = number of claims from same paradigm already applied
  alpha = 0.5 (configurable)

effective_weight = w_rel * w_map * w_dep * w_aux * log_bayes_factor
```

---

## 3. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| C01 | target_feature_ids doesn't overlap with question's feature_ids | Warn — claim bears on features the question doesn't track |
| C02 | log_bayes_factor = 0 | Reject — zero-weight claims are noise |
| C03 | paradigm is null and claim is from an LLM | Warn — AI-generated claims should be tagged |
| C04 | is_retracted = true and superseded_by is null | Warn — retracted claims should name their replacement |
| C05 | |log_bayes_factor| > 5 and w_rel < 0.8 | Reject — strong claims need high relevance |
| C06 | No falsifier and paradigm is scientific | Warn — scientific claims should be falsifiable |
| C07 | source_type = "ro" but source RO doesn't exist | Reject — dangling reference |

---

## 4. Storage

Claims live **only in D1** — not in git files. They are append-only.

```sql
CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY,
  schema_version INTEGER NOT NULL DEFAULT 1,
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  target_question_id TEXT,
  target_feature_ids TEXT NOT NULL,       -- JSON array
  log_bayes_factor REAL NOT NULL,
  w_rel REAL NOT NULL,
  w_map REAL NOT NULL,
  w_aux REAL NOT NULL,
  paradigm TEXT,
  claim_text TEXT NOT NULL,
  falsifier TEXT,                          -- JSON object or null
  is_retracted INTEGER NOT NULL DEFAULT 0,
  supersedes TEXT,
  superseded_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  extracted_by TEXT,
  FOREIGN KEY (target_question_id) REFERENCES truth_map_questions(question_id)
);

CREATE INDEX idx_claims_question ON claims(target_question_id);
CREATE INDEX idx_claims_feature ON claims(target_feature_ids);
CREATE INDEX idx_claims_paradigm ON claims(paradigm);
CREATE INDEX idx_claims_source ON claims(source_type, source_id);
CREATE INDEX idx_claims_supersedes ON claims(supersedes);
CREATE INDEX idx_claims_created ON claims(created_at);
```

---

## 5. Access Patterns

| Operation | Frequency | Notes |
|-----------|-----------|-------|
| Insert new claim | Per publish event | Append-only |
| Full recompute (all claims) | Nightly Dreaming Loop | Batch read all non-retracted |
| Incremental update (new claims) | Per evidence entry | Read only new claims + paradigm counts |
| Read claims for a question | Per user request | Filter by target_question_id |
| Supersede a claim | Per correction | Mark old as retracted, insert new |
| Staleness check | Weekly | Find questions with no recent claims |

---

## 6. Extraction Guidelines

Each source type has a claim extraction protocol:

**RO → Claims:** Every passage that states a position on a truth map question produces 1 claim. The `log_bayes_factor` is estimated from the passage's confidence language ("strongly suggests" = +2.0, "may indicate" = +0.5, "contradicts" = -2.0).

**EO → Claims:** Each hypothesis in the EO produces 1 claim. The EO's synthesis of multiple ROs produces an additional claim per tension point.

**Essay → Claims:** The thesis statement and each major supporting argument produce claims. The conclusion produces 1 summary claim.

**Video → Claims:** The video's verbal thesis and each visual metaphor that makes a factual assertion produce claims.

**Dataset → Claims:** Each statistically significant result produces 1 claim with lbf computed from effect size.

---

## 7. Migration

No existing claims to migrate — this is a new entity. The current evidence arrays in q-*.json files should be extracted into the D1 claims table as part of the truth map migration (see TRUTH-MAP-QUESTION.md §7).
