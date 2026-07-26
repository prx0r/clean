# Translation Object — Full Spec

A Translation Object (TO) is a **versioned, audited translation of a Sanskrit (or other classical) text produced by the 7-pass DeepSeek pipeline.** Each verse is independently scored for confidence, linked to alternative scholarly translations, and traceable through the full 7-pass reasoning chain.

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "TranslationObject",
  "type": "object",
  "required": [
    "to_id", "schema_version", "text_id", "title", "version",
    "status", "provenance", "translation"
  ],
  "properties": {
    "to_id": {
      "type": "string",
      "pattern": "^to:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 1
    },
    "text_id": {
      "type": "string",
      "pattern": "^text:[a-z0-9_-]+$",
      "description": "Reference to the canonical source text record"
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "title_sanskrit": {
      "type": "string",
      "description": "Title in original script (Devanagari)"
    },
    "title_transliterated": {
      "type": "string",
      "description": "IAST transliteration"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"
    },
    "status": {
      "type": "string",
      "enum": ["draft", "verified", "peer_reviewed", "published", "superseded"]
    },
    "translator": {
      "type": "string",
      "description": "Pipeline or human translator ID"
    },
    "human_reviewer": {
      "type": ["string", "null"]
    },
    "date_completed": {
      "type": "string",
      "format": "date"
    },
    "verses": {
      "type": "object",
      "required": ["total", "translated", "verified"],
      "properties": {
        "total": { "type": "integer" },
        "translated": { "type": "integer" },
        "verified": { "type": "integer" }
      }
    },
    "overall_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": { "type": "string" },
        "date": { "type": "string" },
        "lineage": { "type": "string" },
        "school": { "type": "string" },
        "tradition": { "type": "string" },
        "topics": { "type": "array", "items": { "type": "string" } },
        "related_texts": { "type": "array", "items": { "type": "string" } },
        "language": { "type": "string", "default": "Sanskrit" },
        "script": { "type": "string", "default": "Devanagari" },
        "source": { "type": "string" }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["source_text_version", "pipeline_version", "model"],
      "properties": {
        "source_text_version": { "type": "string" },
        "pipeline_version": { "type": "string" },
        "model": { "type": "string" },
        "pass_log": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pass": { "type": "integer" },
              "date": { "type": "string", "format": "date" },
              "status": { "type": "string", "enum": ["complete", "pending", "failed"] }
            }
          }
        }
      }
    },
    "translation": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["verse_number", "sanskrit", "translation", "confidence"],
        "properties": {
          "verse_number": { "type": "string" },
          "sanskrit": { "type": "string" },
          "transliteration": { "type": "string" },
          "translation": { "type": "string" },
          "alternative_translations": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "translator": { "type": "string" },
                "translation": { "type": "string" },
                "notes": { "type": "string" },
                "source": { "type": "string" }
              }
            }
          },
          "notes": { "type": "string" },
          "key_terms": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "sanskrit": { "type": "string" },
                "translation": { "type": "string" },
                "alternatives": { "type": "array", "items": { "type": "string" } },
                "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
              }
            }
          },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "pass_5_issues": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "concept_map": {
      "type": "object",
      "description": "Key concepts in this text with their philosophical mapping",
      "additionalProperties": {
        "type": "string"
      }
    }
  }
}
```

---

## 2. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| T01 | verses.translated < verses.total | Set status = "draft" |
| T02 | overall_confidence < 0.7 and status = "verified" | Reject — verified TOs need ≥0.7 confidence |
| T03 | Any translation entry has confidence < 0.5 | Warn — low-confidence verses need notes |
| T04 | provenance.pass_log doesn't have 7 passes | Warn — incomplete pipeline |
| T05 | key_terms.confidence is missing for any term | Warn — key terms should have confidence scores |
| T06 | verse_number duplicates | Reject — no duplicate verses |
| T07 | status = "published" and no human_reviewer | Warn — published TOs should have human review |
| T08 | alternative_translations references non-existent scholar | Warn — dangling scholar reference |

---

## 3. Versioning

| Event | Bump |
|-------|------|
| New verse translated | Minor |
| Existing verse corrected | Patch |
| Alternative translation added | Patch |
| Overall confidence recalculated | Patch |
| Schema migration | Major |
| Full re-translation (new pipeline pass) | Major |

---

## 4. Storage

```
Path: content/translation-objects/{slug}/to.json
Backend: Git filesystem
Index: D1 table
```

```sql
CREATE TABLE translation_objects (
  to_id TEXT PRIMARY KEY,
  text_id TEXT NOT NULL,
  title TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  overall_confidence REAL,
  tradition TEXT,
  author TEXT,
  verses_total INTEGER,
  verses_translated INTEGER,
  human_reviewer TEXT,
  date_completed TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_to_text ON translation_objects(text_id);
CREATE INDEX idx_to_status ON translation_objects(status);
CREATE INDEX idx_to_tradition ON translation_objects(tradition);
```

---

## 5. Access Patterns

| Operation | Frequency | Path |
|-----------|-----------|------|
| Read for RO creation | Per research cycle | File |
| Browse by text/tradition | Per scholar visit | D1 |
| Compare alternative translations | Per verse study | File |
| Submit correction | Per scholar contribution | File + D1 |
| Publish new version | Per pipeline completion | File + D1 |

---

## 6. Migration

The existing Spandakārikā v1.0 translation in the blog project needs to be formatted as a TO. Migration script: `scripts/migrations/legacy_translations_to_tos.py`.
