# 04 — Essay Objects

Essay Objects are the bridge between research and production. They organize ROs into guided enquiries.

## Definition

An EO is a focused intellectual question + all the source material needed to answer it. It combines multiple ROs, adds minimal connecting commentary, and defines what's known, unknown, and worth investigating.

Unlike an RO (which is source-centric), an EO is **question-centric**.

## Schema

```json
{
  "eo_id": "eo:iccha-jnana-kriya-necessary",
  "schema_version": 1,
  "title": "Is icchā-jñāna-kriyā a Necessary Architecture of Manifestation?",
  "status": "draft",
  "version": "0.1.0",
  "tension_point": "Abhinavagupta posits icchā-jñāna-kriyā as the necessary structure of manifestation. Active inference posits preference-model-policy as the necessary structure of agency. Are these the same architecture described in different languages, or is Trika projecting human agency onto cosmic reality?",
  "primary_ros": [
    "ro:matter-of-wonder",
    "ro:hermeneutics-of-absolute",
    "ro:utpaladeva-ipk"
  ],
  "secondary_sources": [
    {
      "source_id": "ratie_freedom_consciousness",
      "relevance": "Direct treatment of icchā as freedom",
      "location": "by-scholar/ratie/"
    }
  ],
  "hypotheses": [
    {
      "h_id": "H1",
      "claim": "icchā-jñāna-kriyā is structurally isomorphic to preference-model-policy",
      "confidence": "moderate",
      "supporting_ros": ["ro:matter-of-wonder"],
      "challenging_ros": ["ro:utpaladeva-ipk"]
    },
    {
      "h_id": "H2",
      "claim": "The isomorphism breaks at the cosmic/organismic boundary",
      "confidence": "strong",
      "supporting_ros": ["ro:utpaladeva-ipk"]
    }
  ],
  "source_metaphysics": {
    "question": "Is icchā-jñāna-kriyā a necessary architecture?",
    "status": "underdetermined",
    "best_answer": "Strong structural correspondence exists but it's unclear whether Trika's cosmic claim follows from the phenomenological evidence.",
    "last_updated": "2026-07-26"
  },
  "provenance": {
    "parent_ros": ["ro:matter-of-wonder", "ro:hermeneutics-of-absolute"],
    "created_by": "agent/hermes",
    "git_commit": "abc123"
  }
}
```

## How EOs Are Created

1. **Tension point detected** — by hypothesis engine or manual proposal
2. **Relevant ROs identified** — search by topic, tradition, concept
3. **EO drafted** — combines ROs into focused question
4. **Hypotheses extracted** — what competing answers exist
5. **Source metaphysics updated** — question added to truth map
6. **Versioned** — EO added to git

## How EOs Are Used

Factory 2 (Writing) takes an EO → writes a paper
Factory 3 (Video) takes an EO → creates a video
Factory 4 (Analytics) takes an EO → designs an experiment

## EO Lifecycle

```
draft → active → in_production → answered → archived
                                      ↓
                              updates source metaphysics
```

Once answered, the EO updates the truth map and is archived. It can be revisited if new evidence emerges.
