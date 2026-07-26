# 05 — Source Metaphysics

The truth map. A living graph of every question we're tracking, with status, evidence, and confidence.

## Purpose

Prevents the system from:
- Asking stale questions repeatedly
- Making claims without evidence
- Ignoring counter-evidence
- Wasting production on topics already resolved
- Drifting into circular reasoning

## Core Structure

```json
{
  "question_id": "q:consciousness-fundamental",
  "question": "Is consciousness fundamental to reality?",
  "tags": ["metaphysics", "consciousness", "idealism"],
  "status": "plausible",
  "confidence": 0.6,
  "evidence_for": [
    {
      "source": "ro:matter-of-wonder",
      "claim": "Abhinavagupta's panentheism posits consciousness as the ground of matter",
      "weight": 0.4,
      "type": "phenomenological"
    },
    {
      "source": "eo:hard-problem-solved",
      "claim": "Dual-aspect monism dissolves the hard problem",
      "weight": 0.3,
      "type": "philosophical"
    }
  ],
  "evidence_against": [
    {
      "source": "eo:brain-damage-idealism",
      "claim": "Brain damage systematically alters specific contents — hard for idealism to explain",
      "weight": 0.5,
      "type": "empirical"
    }
  ],
  "best_answer": "Plausible but underdetermined. The hard problem may be dissolved by dual-aspect views, but the structural/mapping problems remain and no decisive experiment exists.",
  "parent_question": null,
  "sub_questions": [
    "q:consciousness-necessary-for-being",
    "q:prakasa-vs-panpsychism",
    "q:brain-filter-or-appearance"
  ],
  "last_updated": "2026-07-26",
  "last_updated_by": "agent/hermes"
}
```

## Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `strongly_supported` | Multiple independent lines of evidence converge | Archive EOs, move to teaching |
| `plausible` | Some evidence but significant counterarguments remain | Active research area |
| `underdetermined` | Evidence exists but doesn't decisively favor any position | Highest priority for new EOs |
| `speculative` | Little evidence, mostly theoretical | Needs more source material |
| `incompatible` | Strong evidence against | Only revisit if new evidence emerges |
| `unasked` | Question identified but not yet investigated | Create RO/EO |

## Question Taxonomy

Questions are organized into a hierarchy:

```
q:consciousness-fundamental
  ├── q:prakasa-vs-panpsychism
  ├── q:brain-filter-or-appearance  
  └── q:consciousness-necessary-for-being
        └── q:ai-can-be-conscious
```

Parent questions aggregate the status of their children. A parent can't be `strongly_supported` if its children are `underdetermined`.

## Integration with Factories

1. **Hypothesis Engine** scans the truth map for `underdetermined` questions
2. Creates EOs for the most promising ones
3. Factories 2-4 produce content from those EOs
4. Results update the truth map
5. Cycle repeats

## Preventing Staleness

Every question has a `last_updated` timestamp. Questions not updated in 90 days are flagged for review. The hypothesis engine can also re-open answered questions if new evidence enters the system.

## Initial Question Catalog

Based on the RESEARCH_DIRECTIVE.md priority list. See `researchsources/100sources.md` and `ideas1.md` for the full set of known questions. These need to be formalized into the source metaphysics.
