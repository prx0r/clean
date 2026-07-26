# 03 — Research Objects

Research Objects are the foundational knowledge unit. They make source material navigable for agents.

## Definition

An RO is a structured extraction of one coherent body of source material — a book, a paper, a corpus, a tradition. It is NOT an analysis or synthesis. It is the source material organized for agent consumption.

## Schema

```json
{
  "ro_id": "ro:matter-of-wonder",
  "schema_version": 2,
  "title": "The Matter of Wonder: Abhinavagupta's Panentheism and the New Materialism",
  "subtitle": "Loriliai Biernacki's OUP monograph on camatkāra, panentheism, and subjectivity of matter",
  "family": "thinker-topic",
  "status": "active",
  "current_version": "0.1.0",
  "summary": {
    "one_line": "...",
    "scope": "Full monograph (OUP 2023). Covers panentheism, camatkāra, pratibimbavāda.",
    "traditions": ["kashmiri_shaivism", "trika"]
  },
  "sources": [
    {
      "source_id": "biernacki_matter_of_wonder_2023",
      "tier": 1,
      "label": "Biernacki, Loriliai. The Matter of Wonder... OUP, 2023.",
      "contribution": ["camatkara", "panentheism", "pratibimbavada"],
      "status": "active"
    }
  ],
  "body": [
    {
      "passage_id": "p_001",
      "section": "introduction",
      "kind": "source",
      "text": "Extracted passage from source material...",
      "source_ids": ["biernacki_matter_of_wonder_2023"],
      "topics": ["panentheism", "camatkara"],
      "status": "active"
    }
  ],
  "provenance": {
    "primary_source_path": "sourcematerial/matter-of-wonder/",
    "git_commit": "abc123",
    "last_updated": "2026-07-26"
  }
}
```

## Key Rules

1. **Passages are direct quotes or close paraphrases** — not original analysis
2. **Every passage links to its source** — full provenance chain
3. **An RO is one coherent body of material** — don't mix unrelated sources
4. **Don't interpret** — let the source speak. Analysis happens in EOs
5. **Versioned** — when source material updates, RO version bumps

## Quality Scoring

| Score | Criteria |
|-------|----------|
| 6 | ≥10 passages, v0.2.0+, sources linked, well-organized |
| 4-5 | 5-9 passages, good structure, minor gaps |
| 2-3 | <5 passages, needs work, early version |
| 1 | Stub — barely started |

## Current State

153 ROs exist. 43 ready (score ≥4). 110 need work. 34 are stubs.

## Agent Instructions

When asked about a topic, **check the RO first**. Don't go back to raw source material unless the RO doesn't have what you need. If you find something missing, propose an RO update.

Search for ROs by: `grep -rl "ro_id:.*$TOPIC" content/research-objects/`
