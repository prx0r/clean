# Research Object v2 — Full Spec

## Purpose

An RO is a **versioned extraction of passages from one or more sources, organized around a specific question, theme, or thinker.** It makes source material navigable for agents. Unlike an EO (which is structured as a syllogism and tracks competing explanations), an RO is **source-centric** — it faithfully represents what sources say without analysis.

The RO is the **primary input to the truth map.** Claims extracted from RO passages go through the Nyāya gate before entering the propagation engine. ROs also feed directly into EOs — an EO's candidates cite ROs as evidence.

---

## 1. Relationship to Other Objects

```
SO (source object — immutable, one per paper/text)
  │
  └── RO (research object — extracts themed passages from SO)
        │
        ├── truth map: each passage → claim → Nyāya gate → engine
        │
        ├── argument dossier: passages cited as evidence for/against candidates
        │
        └── EO: passages cited in syllogism.hetu.evidence[]
```

Each passage in an RO is a candidate claim that must pass the Nyāya gate before the RO is published. Passages that fail hetvābhāsa are flagged for review, not silently accepted.

---

## 2. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "ResearchObjectV2",
  "type": "object",
  "required": [
    "ro_id", "schema_version", "title", "traditions", "status",
    "current_version", "summary", "sources", "body", "provenance"
  ],
  "properties": {
    "ro_id": {
      "type": "string",
      "pattern": "^ro:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 2
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "subtitle": {
      "type": "string",
      "maxLength": 300
    },
    "traditions": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "description": "Tradition scope. Same concept in different traditions = different RO until a bridge is proved."
    },
    "status": {
      "type": "string",
      "enum": ["idea", "stub", "draft", "active", "review", "published", "stale", "archived"]
    },
    "current_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "summary": {
      "type": "object",
      "required": ["one_line", "scope"],
      "properties": {
        "one_line": { "type": "string", "maxLength": 200 },
        "scope": { "type": "string", "maxLength": 1000 },
        "methodology": { "type": "string", "description": "How passages were selected" }
      }
    },
    "scope": {
      "type": "string",
      "enum": ["single_source", "cross_source", "cross_tradition"],
      "description": "Determines quote budget and validation rules"
    },
    "bears_on_questions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question_id", "relevance"],
        "properties": {
          "question_id": { "type": "string", "pattern": "^q:[a-z0-9_-]+$" },
          "relevance": { "type": "string", "enum": ["direct", "indirect", "background"] },
          "discriminators": {
            "type": "array",
            "items": { "type": "string", "pattern": "^D[1-5]$" },
            "description": "Which discriminators this RO bears on"
          }
        }
      }
    },
    "sources": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["source_id", "label"],
        "properties": {
          "source_id": { "type": "string" },
          "tier": { "type": "integer", "enum": [1, 2, 3] },
          "label": { "type": "string" },
          "tradition_scope": { "type": "string", "description": "Which tradition's reading of this source" },
          "contribution": { "type": "array", "items": { "type": "string" } },
          "status": { "type": "string", "enum": ["active", "superseded", "retracted"] }
        }
      }
    },
    "body": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["passage_id", "kind", "text", "source_ids"],
        "properties": {
          "passage_id": { "type": "string", "pattern": "^p_\\d{3}$" },
          "section": { "type": "string" },
          "subsection": { "type": "string" },
          "kind": {
            "type": "string",
            "enum": ["source", "commentary", "summary"],
            "description": "source = direct quote, commentary = agent analysis, summary = condensed"
          },
          "text": { "type": "string", "minLength": 1 },
          "source_ids": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
          "topics": { "type": "array", "items": { "type": "string" } },
          "pramana": {
            "type": "string",
            "enum": ["pratyaksa", "anumana", "upamana", "sabda"],
            "description": "What kind of evidence this passage represents"
          },
          "hetvabhasa_check": {
            "type": "object",
            "properties": {
              "passed": { "type": "boolean" },
              "failures": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["savyabhicara", "viruddha", "asiddha", "satpratipaksa", "badhita"]
                }
              },
              "notes": { "type": "string" }
            },
            "description": "Result of running this passage through the Nyāya gate"
          },
          "falsifier": {
            "type": "object",
            "properties": {
              "condition": { "type": "string", "description": "What would disprove this passage's claim" },
              "type": { "type": "string", "enum": ["empirical", "formal", "philological", "phenomenological"] },
              "status": { "type": "string", "enum": ["untested", "tested_not_confirmed", "confirmed"] }
            }
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confidence this passage accurately represents the source"
          },
          "status": { "type": "string", "enum": ["active", "review", "superseded"] }
        }
      }
    },
    "coverage": {
      "type": "object",
      "description": "Per-section coverage tracking",
      "patternProperties": {
        "^.*$": {
          "type": "object",
          "properties": {
            "status": { "type": "string", "enum": ["comprehensive", "partial", "empty", "not_applicable"] },
            "passage_count": { "type": "integer" },
            "gaps": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["primary_source_path", "git_commit", "last_updated"],
      "properties": {
        "primary_source_path": { "type": "string" },
        "git_commit": { "type": "string" },
        "last_updated": { "type": "string", "format": "date-time" },
        "last_updated_by": { "type": "string" },
        "gate_version": { "type": "string", "description": "Version of the Nyāya gate used to validate passages" }
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
    },
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "issue_id": { "type": "string" },
          "description": { "type": "string" },
          "status": { "type": "string", "enum": ["open", "resolved", "wont_fix"] }
        }
      }
    }
  }
}
```

---

## 3. The Passage → Truth Map Pipeline

Each passage in an RO body is a candidate claim. Before the RO is published, each passage must go through:

```
RO passage
  → Pramāṇa assignment (what kind of evidence?)
  → Tradition scoping (which tradition's claim is this?)
  → Hetvābhāsa check (which fallacy, if any?)
    → Failed: passage flagged, not ingested into truth map
    → Passed: proceeds
  → Falsifier check (does it have one?)
    → No: warn — claims without falsifiers are weak
    → Yes: stored
  → Claim generated for truth map ingestion
    → target: which question or discriminator?
    → source_id: links back to RO + passage_id
    → pramāṇa, tradition_scope, falsifier carried forward
```

The gate result is stored in `body[].hetvabhasa_check` so every passage is auditable.

---

## 4. Versioning

### Bump Rules

| Event | Bump | Example |
|-------|------|---------|
| New passage added | Minor | 1.0.0 → 1.1.0 |
| Passage edited | Patch | 1.0.0 → 1.0.1 |
| Source added/removed | Minor | 1.0.0 → 1.1.0 |
| bears_on_questions changed | Minor | 1.0.0 → 1.1.0 |
| hetvābhāsa check updated | Patch | 1.0.0 → 1.0.1 |
| Schema migration | Major | 1.0.0 → 2.0.0 |
| Bulk rewrite | Major | 1.0.0 → 2.0.0 |

### Version Propagation

When an RO version changes, downstream objects are notified but not automatically updated:

```
RO v1.0.0 → passages extracted → claims ingested → truth map posteriors
RO v1.1.0 (passage added)
  → New passage → new claim → gate check → truth map update
  → Linked EOs flagged: "RO has new version, review passages"
  → Linked dossiers flagged: "new evidence available for candidate X"
```

Downstream objects (EOs, dossiers) are not auto-updated — they're flagged for human/agent review. This prevents cascade updates from invalidating carefully crafted arguments.

---

## 5. Storage

```
Path: content/research-objects/ro-{slug}/ro.json
Backend: Git filesystem
Index: D1 table
```

```sql
CREATE TABLE research_objects_v2 (
  ro_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  traditions TEXT NOT NULL,       -- JSON array
  status TEXT NOT NULL DEFAULT 'draft',
  version TEXT NOT NULL,
  scope TEXT NOT NULL,
  bears_on_questions TEXT,        -- JSON array of question_ids
  passage_count INTEGER DEFAULT 0,
  gate_pass_rate REAL,            -- fraction of passages that passed hetvābhāsa
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_ro_traditions ON research_objects_v2(traditions);
CREATE INDEX idx_ro_questions ON research_objects_v2(bears_on_questions);
```

Full content is read from the file. D1 stores metadata for search and filtering.

---

## 6. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| R01 | body has fewer than 5 passages | Set status = "stub" |
| R02 | Any passage missing source_ids | Reject |
| R03 | scope = single_source AND sources > 1 | Reject |
| R04 | scope = cross_tradition AND traditions < 2 | Reject |
| R05 | Any passage that failed hetvābhāsa is still ingested | Reject — failed passages must be reviewed first |
| R06 | No falsifier on any passage | Warn — passages without falsifiers are weak claims |
| R07 | bears_on_questions references nonexistent question | Auto-create question with status "unasked" |
| R08 | traditions doesn't match source traditions | Reject — tradition scope must be explicit |
| R09 | status = published AND any passage failed hetvābhāsa | Reject — can't publish ROs with failed claims |
| R10 | Passage with kind = source and no pramāṇa | Warn — every source passage should have a pramāṇa type |

---

## 7. Lifecycle

```
SO acquired
  → Need identified: "this source bears on question Q"
    → RO created: passages extracted around theme X
      → Each passage gated through hetvābhāsa
        → Gate passed: passage enters RO body
        → Gate failed: passage flagged, sent for review
      → RO published
        → Claims extracted → truth map engine
        → Agents can reference RO in EOs and dossiers
        → EOs that cite this RO are flagged for review
```

---

## 8. Key Differences from v1

| v1 | v2 |
|----|----|
| family enum (15 types) | Removed — scope + traditions replace it |
| bears_on_questions as string array | Now object array with relevance + discriminator targets |
| body[].confidence only | Added body[].pramāṇa, body[].hetvābhāsa_check, body[].falsifier |
| No gate integration | Every passage must pass the Nyāya gate |
| traditions as simple string list | traditions scoped at RO level, same concept in different traditions = different RO |
| No version propagation | Version bumps flag downstream EOs/dossiers for review |
| Static coverage | Coverage remains but gate_pass_rate added to D1 index |
