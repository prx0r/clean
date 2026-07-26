# Research Object — Full Spec

A Research Object is a **versioned, living compilation of passages from one or more sources, organized around a specific question or theme.** It is the primary knowledge unit in the system — the thing an agent reads to understand what's known about a topic from a specific source or set of sources.

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "ResearchObject",
  "type": "object",
  "required": [
    "ro_id", "schema_version", "title", "family", "status",
    "current_version", "summary", "sources", "body", "provenance"
  ],
  "properties": {
    "ro_id": {
      "type": "string",
      "pattern": "^ro:[a-z0-9_-]+$",
      "description": "Unique identifier. Format: ro:{slug}"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 1,
      "description": "Schema version for migration tracking"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Human-readable title"
    },
    "subtitle": {
      "type": "string",
      "maxLength": 300
    },
    "family": {
      "type": "string",
      "enum": [
        "thinker-topic",
        "topic-across-thinkers",
        "tradition",
        "theme",
        "literature",
        "comparative",
        "concept-evolution",
        "reception",
        "practice",
        "historical-question",
        "debate",
        "research-map",
        "reading-companion",
        "sourcebook",
        "research-question"
      ],
      "description": "What kind of research object this is"
    },
    "status": {
      "type": "string",
      "enum": ["idea", "stub", "draft", "active", "review", "published", "stale", "archived"],
      "description": "Lifecycle status"
    },
    "current_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version. Bump major on structural changes, minor on additions, patch on fixes."
    },
    "summary": {
      "type": "object",
      "required": ["one_line", "scope", "traditions"],
      "properties": {
        "one_line": { "type": "string", "maxLength": 200 },
        "scope": { "type": "string", "maxLength": 1000 },
        "traditions": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 0
        },
        "methodology": {
          "type": "string",
          "description": "How the passages were selected and organized"
        }
      }
    },
    "scope": {
      "type": "string",
      "enum": ["single_source", "cross_source", "cross_tradition"],
      "description": "Determines quote budget and validation rules"
    },
    "bears_on_questions": {
      "type": "array",
      "items": { "type": "string", "pattern": "^q:[a-z0-9_-]+$" },
      "description": "Truth map questions this RO provides evidence for"
    },
    "sources": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["source_id", "tier", "label"],
        "properties": {
          "source_id": { "type": "string", "pattern": "^work:[a-z0-9_-]+$" },
          "tier": { "type": "integer", "enum": [1, 2, 3] },
          "label": { "type": "string", "minLength": 1 },
          "contribution": {
            "type": "array",
            "items": { "type": "string" },
            "description": "What this source contributes to the RO"
          },
          "status": {
            "type": "string",
            "enum": ["active", "superseded", "retracted"],
            "default": "active"
          }
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
          "passage_id": {
            "type": "string",
            "pattern": "^p_\\d{3}$"
          },
          "section": { "type": "string" },
          "subsection": { "type": "string" },
          "kind": {
            "type": "string",
            "enum": ["source", "commentary", "summary"],
            "description": "source = direct quote, commentary = AI analysis, summary = condensed"
          },
          "text": { "type": "string", "minLength": 1 },
          "source_ids": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1
          },
          "topics": {
            "type": "array",
            "items": { "type": "string" }
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "How confident we are that this passage accurately represents the source"
          },
          "status": {
            "type": "string",
            "enum": ["active", "review", "superseded"],
            "default": "active"
          }
        }
      }
    },
    "coverage": {
      "type": "object",
      "description": "Per-section coverage map for tracking completeness",
      "patternProperties": {
        "^.*$": {
          "type": "object",
          "properties": {
            "status": {
              "type": "string",
              "enum": ["comprehensive", "partial", "empty", "not_applicable"]
            },
            "passage_count": { "type": "integer" },
            "estimated_completeness": {
              "type": "number",
              "minimum": 0,
              "maximum": 1
            },
            "gaps": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["primary_source_path", "git_commit", "last_updated"],
      "properties": {
        "primary_source_path": { "type": "string" },
        "git_commit": {
          "type": "string",
          "description": "Git commit hash when this version was created"
        },
        "last_updated": {
          "type": "string",
          "format": "date-time"
        },
        "last_updated_by": {
          "type": "string",
          "description": "Agent or human that last modified this RO"
        }
      }
    },
    "versions": {
      "type": "array",
      "description": "Version history (append-only)",
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
          "status": {
            "type": "string",
            "enum": ["open", "resolved", "wont_fix"]
          }
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
| R01 | body.length < 5 | Set status = "stub" |
| R02 | Any passage missing source_ids | Reject — every passage must link to a source |
| R03 | scope = "single_source" AND sources.length > 1 | Reject — single_source ROs must have exactly 1 source |
| R04 | scope = "cross_tradition" AND traditions.length < 2 | Reject — must span at least 2 traditions |
| R05 | bears_on_questions contains IDs that don't exist | Auto-create truth map questions with status "unasked" |
| R06 | summary.one_line length > 200 | Truncate |
| R07 | family = "research-question" AND scope != "cross_source" | Reject — research questions require multiple sources |
| R08 | Any passage.kind = "source" AND matched source doesn't exist | Reject — dangling source reference |
| R09 | current_version doesn't increment from previous | Auto-bump patch version |
| R10 | status = "published" AND coverage < 0.3 | Warn — published ROs should have reasonable coverage |

---

## 3. Versioning Behavior

| Event | Version Bump | Example |
|-------|-------------|---------|
| New passage added | Minor | 1.0.0 → 1.1.0 |
| Passage edited for clarity | Patch | 1.0.0 → 1.0.1 |
| Source added or removed | Minor | 1.0.0 → 1.1.0 |
| Schema migration (field added/removed) | Major | 1.0.0 → 2.0.0 |
| Status change (draft → published) | Major | 1.0.0 → 2.0.0 |
| Passage confidence updated | Patch | 1.0.0 → 1.0.1 |
| bears_on_questions changed | Minor | 1.0.0 → 1.1.0 |
| Bulk rewrite of multiple passages | Major | 1.0.0 → 2.0.0 |

History is stored in `versions[]` array. The file itself is the current version. To view history, `git log` on the file.

---

## 4. Storage

```
Path: content/research-objects/ro-{slug}/ro.json
Backend: Git filesystem (local) + D1 (index only)
Indexing: D1 table with ro_id, title, family, status, version, scope, traditions
```

The D1 index allows fast queries:
```sql
SELECT ro_id, title, family, scope, current_version
FROM research_objects
WHERE status = 'published'
  AND bears_on_questions LIKE '%q:consciousness-fundamental%'
ORDER BY current_version DESC
```

Full content is always read from the file. D1 only stores metadata for search and filtering.

---

## 5. Access Patterns

| Operation | Frequency | Path | Cached? |
|-----------|-----------|------|---------|
| Read by agent for EO creation | Daily | File (git) | No |
| Read by Satsang feed | Per user request | D1 index → file | D1 yes, file no |
| Write (new version) | Per RO update | File + D1 | — |
| Search across ROs | Per user search | D1 index | Yes |
| Batch read for propagation | Per computation | D1 claims index | Yes |

---

## 6. Migration Policy

When the schema changes:

1. Bump `schema_version` in the schema definition
2. All existing ROs keep their `schema_version` — they're valid until migrated
3. Migration scripts live in `scripts/migrations/` and run one at a time:

```python
# scripts/migrations/v1_to_v2.py
def migrate(ro: dict) -> dict:
    """Add scope field based on sources count."""
    if 'scope' not in ro:
        ro['scope'] = 'single_source' if len(ro['sources']) <= 1 else 'cross_source'
    ro['schema_version'] = 2
    return ro
```

4. ROs are migrated lazily — only when next accessed for writing
5. A batch migration can be triggered: `python scripts/migrate_ros.py --target-version 2`
