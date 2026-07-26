# 01 — Vision

## The Problem

The blog project has accumulated:
- 1,917 Works (acquired papers)
- 153 Research Objects (variable quality)
- 1,796 Essays (mostly bridge/synthesis)
- 363 Storyboards
- Multiple handover docs, factory specs, pipeline attempts
- A farm-template that was designed but never deployed
- A Hermes agent with browser/acquire skills

It's full of useful parts but has no unified architecture. Each piece was built for a specific need, not as part of a coherent system.

## The Solution

A single unified factory system with four production lines, all sharing the same research core:

```
                    ┌─────────────────────────────┐
                    │     HYPOTHESIS ENGINE        │
                    │  (perpetual question gen)    │
                    └──────────┬──────────────────┘
                               │ generates research questions
                               ▼
┌──────────────────────────────────────────────────────┐
│               FACTORY 1: RESEARCH                    │
│  Source → RO → EO → Hypothesis → Experiment Design  │
│  (All git-versioned, provenance-linked)              │
└────────────┬─────────────┬─────────────┬─────────────┘
             │             │             │
             ▼             ▼             ▼
   FACTORY 2:      FACTORY 3:      FACTORY 4:
   WRITING         VIDEO           ANALYTICS
   (papers)        (youtube)       (data science)
```

## The Key Innovation: Source Metaphysics

Every piece of source material, every RO, every EO is mapped against a living truth map:

```
Question: "Is consciousness fundamental?"
  ├── Evidence for: [list of ROs, experiments]
  ├── Evidence against: [list of ROs, experiments]
  ├── Status: [strongly_supported / plausible / underdetermined / incompatible]
  ├── Last updated: [date]
  └── Confidence: [0-1]
```

This prevents:
- Stale questions being re-asked
- The system repeating itself
- Claims without evidence
- Evidence without provenance

## Versioning Chain

```
v1.0 Source Text (immutable primary source)
  → v1.0 Research Object (extracted passages, agent-navigable)
    → v1.0 Essay Object (guided enquiry using ROs)
      → v1.0 Product (paper, video, experiment)
        → updates Source Metaphysics
```

Each layer links back to its parents. Updates propagate forward. The entire chain is git-versioned.

## Guiding Principle

Not "produce content." Produce **understanding** — measured by the truth map, not by view count.

Content is the byproduct of understanding. If the understanding is real, the content will be worth watching.
