# Source Object — Full Spec

A Source Object (SO, called "Work" in the blog project) is the **structured metadata record for a primary source — a paper, book, dataset, or text.** It is immutable after creation: it captures what the source is, where it came from, and how to access it. Every RO, EO, and Claim traces back to an SO.

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "SourceObject",
  "type": "object",
  "required": [
    "so_id", "schema_version", "title", "authors", "provenance"
  ],
  "properties": {
    "so_id": {
      "type": "string",
      "pattern": "^so:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 1
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "subtitle": {
      "type": "string"
    },
    "authors": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": { "type": "string" },
          "author_id": { "type": "string", "pattern": "^author:[a-z0-9_-]+$" }
        }
      }
    },
    "publication": {
      "type": "object",
      "properties": {
        "year": { "type": "integer" },
        "type": {
          "type": "string",
          "enum": ["article", "thesis", "book", "book_chapter", "preprint", "conference", "dataset", "translation", "manuscript"]
        },
        "journal": { "type": "string" },
        "publisher": { "type": "string" },
        "language": { "type": "string", "default": "en" },
        "volume": { "type": "string" },
        "issue": { "type": "string" },
        "pages": { "type": "string" }
      }
    },
    "identifiers": {
      "type": "object",
      "properties": {
        "doi": { "type": ["string", "null"] },
        "arxiv_id": { "type": ["string", "null"] },
        "openalex_id": { "type": ["string", "null"] },
        "isbn": { "type": ["string", "null"] },
        "pmid": { "type": ["string", "null"] }
      }
    },
    "topics": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Subject keywords for discovery"
    },
    "tradition": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Philosophical or cultural tradition (trika, neoplatonism, sufism, etc.)"
    },
    "abstract": {
      "type": "string",
      "maxLength": 5000
    },
    "relations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "predicate": { "type": "string", "enum": ["cites", "supported_by", "contradicts", "builds_on", "reviews", "translation_of"] },
          "target_id": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "assets": {
      "type": "object",
      "properties": {
        "pdf_path": { "type": "string" },
        "text_path": { "type": "string" },
        "source_url": { "type": "string" }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["access_status", "retrieved_at"],
      "properties": {
        "access_status": {
          "type": "string",
          "enum": ["open", "paywalled", "request_only", "rights_check", "not_found"]
        },
        "oa_status": { "type": "string" },
        "license": { "type": ["string", "null"] },
        "host_type": { "type": "string" },
        "sha256": { "type": "string" },
        "page_count": { "type": "integer" },
        "file_size_bytes": { "type": "integer" },
        "retrieved_at": { "type": "string", "format": "date-time" },
        "retrieved_by": { "type": "string" },
        "validation_confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "analysis": {
      "type": "object",
      "properties": {
        "summary": { "type": "string" },
        "argument_type": {
          "type": "string",
          "enum": ["empirical", "formal", "philosophical", "textual", "phenomenological", "review", "mixed"]
        },
        "relevance_score": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "derived_objects": {
      "type": "object",
      "properties": {
        "ros": { "type": "array", "items": { "type": "string" } },
        "eos": { "type": "array", "items": { "type": "string" } },
        "tos": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 2. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| S01 | No doi, arxiv_id, or isbn | Warn — source may be hard to verify |
| S02 | publication.year > current_year + 1 | Reject — invalid publication date |
| S03 | authors is empty | Reject — every SO needs at least one author |
| S04 | assets.pdf_path doesn't point to an existing file | Warn — dangling asset reference |
| S05 | provenance.access_status = "open" and no sha256 | Warn — open sources should have integrity hash |
| S06 | topics is empty | Warn — untagged sources are hard to discover |
| S07 | derived_objects.ros includes IDs that don't exist | Warn — dangling RO reference |

---

## 3. Versioning

SOs are **immutable after creation.** A new version of a source (e.g., a corrected preprint) gets a new SO with a `supersedes` reference to the old one. This ensures the provenance chain is never broken.

| Event | Action |
|-------|--------|
| New source acquired | Create SO v1 |
| Corrected version found | Create SO v2 with supersedes |
| Source retracted | Set provenance.access_status = "rights_check", add note |

---

## 4. Storage

```
Path: content/source-objects/{slug}/so.json
Backend: Git filesystem
Index: D1 table
```

```sql
CREATE TABLE source_objects (
  so_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  author_names TEXT NOT NULL,        -- JSON array
  year INTEGER,
  pub_type TEXT,
  doi TEXT,
  arxiv_id TEXT,
  topics TEXT,                       -- JSON array
  tradition TEXT,                    -- JSON array
  access_status TEXT,
  sha256 TEXT,
  retrieved_at TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_so_arxiv ON source_objects(arxiv_id);
CREATE INDEX idx_so_doi ON source_objects(doi);
CREATE INDEX idx_so_tradition ON source_objects(tradition);
```

---

## 5. Access Patterns

| Operation | Frequency | Path |
|-----------|-----------|------|
| Create SO on paper acquisition | Per paper | File + D1 |
| Read SO for RO creation | Per RO | File |
| Search SOs by arxiv/doi | Per acquisition | D1 |
| List SOs by tradition | Per research cycle | D1 |
| Update derived_objects | Per RO/EO creation | File |
| Supersede (corrected version) | Rare | File + D1 |

---

## 6. Migration

Migrate from existing `content/works/` directory (1,917 Works) in the blog project. The `work_id` format `work:{slug}` becomes `so:{slug}`. Bulk migration script: `scripts/migrations/works_to_sos.py`.
