# Essay Object — Full Spec

An Essay Object is a **versioned synthesis of multiple Research Objects organized around a specific tension point.** It is the bridge between research (ROs) and production (essays, videos, experiments). Unlike an RO (which is source-centric), an EO is **question-centric**.

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "EssayObject",
  "type": "object",
  "required": [
    "eo_id", "schema_version", "title", "status", "current_version",
    "tension_point", "primary_ros", "hypotheses", "provenance"
  ],
  "properties": {
    "eo_id": {
      "type": "string",
      "pattern": "^eo:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 1
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "status": {
      "type": "string",
      "enum": ["idea", "draft", "active", "in_production", "answered", "archived"]
    },
    "current_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "tension_point": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000,
      "description": "The exact unresolved tension that this EO investigates. Must name both sides."
    },
    "primary_ros": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "pattern": "^ro:[a-z0-9_-]+$"
      }
    },
    "secondary_ros": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^ro:[a-z0-9_-]+$"
      }
    },
    "secondary_sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source_id", "relevance"],
        "properties": {
          "source_id": { "type": "string" },
          "relevance": { "type": "string", "maxLength": 500 },
          "location": { "type": "string" }
        }
      }
    },
    "hypotheses": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["h_id", "claim", "confidence"],
        "properties": {
          "h_id": {
            "type": "string",
            "pattern": "^H\\d+$"
          },
          "claim": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1000
          },
          "confidence": {
            "type": "string",
            "enum": ["strong", "moderate", "speculative", "unlikely"]
          },
          "supporting_ros": {
            "type": "array",
            "items": { "type": "string", "pattern": "^ro:[a-z0-9_-]+$" }
          },
          "challenging_ros": {
            "type": "array",
            "items": { "type": "string", "pattern": "^ro:[a-z0-9_-]+$" }
          },
          "falsifier": {
            "type": "string",
            "description": "What evidence would disprove this hypothesis"
          }
        }
      }
    },
    "truth_map_question": {
      "type": "object",
      "properties": {
        "question_id": {
          "type": "string",
          "pattern": "^q:[a-z0-9_-]+$"
        },
        "status": {
          "type": "string",
          "enum": ["unasked", "underdetermined", "plausible", "strongly_supported", "speculative", "incompatible"]
        },
        "best_answer": {
          "type": "string",
          "maxLength": 1000
        },
        "last_updated": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["parent_ros", "created_by", "git_commit", "last_updated"],
      "properties": {
        "parent_ros": {
          "type": "array",
          "items": { "type": "string" }
        },
        "created_by": { "type": "string" },
        "git_commit": { "type": "string" },
        "last_updated": { "type": "string", "format": "date-time" }
      }
    },
    "versions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["version", "date", "changes"],
        "properties": {
          "version": { "type": "string" },
          "date": { "type": "string", "format": "date-time" },
          "changes": { "type": "string" },
          "author": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 2. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| E01 | primary_ros is empty | Reject — every EO needs at least 1 RO |
| E02 | tension_point doesn't name both sides | Reject — must identify competing positions |
| E03 | hypotheses has fewer than 2 entries | Warn — EOs should have at least 2 competing hypotheses |
| E04 | truth_map_question is absent | Warn — EOs should link to a truth map question |
| E05 | Any hypothesis.confidence is "unlikely" with no falsifier | Reject — unlikely claims must state what would prove them wrong |
| E06 | Version doesn't increment | Auto-bump patch |
| E07 | status = "answered" with no truth_map_question.best_answer | Reject — answered EOs must have a best answer |
| E08 | primary_ros includes IDs that don't exist | Warn — dangling RO references |
| E09 | Same h_id appears twice | Reject — duplicate hypothesis IDs |

---

## 3. Versioning Behavior

| Event | Bump |
|-------|------|
| New hypothesis added | Minor |
| Existing hypothesis revised | Patch |
| primary_ros changed | Minor |
| truth_map_question status changed | Minor |
| tension_point rewritten | Major |
| Schema migration | Major |
| Confidence values updated on multiple hypotheses | Patch |

---

## 4. Storage

```
Path: content/essay-objects/{slug}/eo.json
Backend: Git filesystem
Index: D1 table (eo_id, title, status, version, primary_ros[], truth_map_question_id)
```

```sql
CREATE TABLE essay_objects (
  eo_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  version TEXT NOT NULL,
  tension_point TEXT,
  truth_map_question_id TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_eo_status ON essay_objects(status);
CREATE INDEX idx_eo_question ON essay_objects(truth_map_question_id);
```

---

## 5. Access Patterns

| Operation | Frequency | Path |
|-----------|-----------|------|
| Read by Writing Factory | Per production cycle | File |
| Read by Video Factory | Per production cycle | File |
| Read by Hypothesis Engine | Daily scan | D1 index |
| Search across EOs by question | Per user request | D1 index |
| Write (new EO or update) | Per research cycle | File + D1 |
| Batch read for gap analysis | Nightly | D1 index |

---

## 6. Migration Policy

Same as RO: lazy migration on write, `schema_version` tracking, scripts in `scripts/migrations/`.

---

## 7. Codex Design Decisions

### Hypothesis Confidence

The `hypotheses[].confidence` enum is useful for editorial triage, but it is not the epistemic source of truth. Keep it as a human-readable label and treat it as **derived or review-facing state**, not propagation input.

Add claim linkage when a hypothesis enters the truth map:

```json
"hypotheses": [
  {
    "h_id": "H1",
    "claim": "The apparent opposition between X and Y dissolves if Z is true.",
    "confidence": "speculative",
    "claim_ids": ["cl:..."],
    "supporting_ros": ["ro:..."],
    "challenging_ros": ["ro:..."],
    "falsifier": {
      "condition": "What observation, source, or formal argument would defeat this hypothesis",
      "status": "untested"
    }
  }
]
```

The propagation engine owns log-odds, posterior probability, and status. EO confidence may cache a label for UI, but it must be recomputable from linked claims and truth map question state.

### Tension Point Shape

The string `tension_point` is not sufficient as the canonical representation because validation rule E02 cannot reliably prove that both sides are named. Keep `tension_point` as the display summary, but add a structured `tension` object:

```json
"tension": {
  "summary": "A concise statement of the unresolved tension.",
  "positions": [
    {
      "label": "Position A",
      "claim": "The first live interpretation.",
      "ro_refs": ["ro:..."],
      "claim_refs": ["cl:..."]
    },
    {
      "label": "Position B",
      "claim": "The competing live interpretation.",
      "ro_refs": ["ro:..."],
      "claim_refs": ["cl:..."]
    }
  ],
  "shared_assumptions": ["Assumption both sides currently grant."],
  "discriminating_question": "What would decide between these positions?"
}
```

Validation should require at least two `positions[]`, each with either an RO reference or claim reference. The legacy string can be generated from `tension.summary`.

### Truth Map Question Creation

EO creation should automatically create or link a truth map question, but only as an **unasked draft node**. It should not automatically add claims or change posteriors.

Lifecycle:

1. EO proposal accepted.
2. If no matching `truth_map_question` exists, create `q:{slug}` with status `unasked`, linked `feature_ids`, and `branches`.
3. Claims are extracted separately through the publish gate.
4. Propagation runs only after valid claims have been inserted.

This keeps the graph complete without letting speculative EOs become evidence for themselves.
