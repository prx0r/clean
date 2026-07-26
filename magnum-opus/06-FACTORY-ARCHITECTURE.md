# 06 — Factory Architecture

Four factories, one core. Each factory takes input from the layer above and produces output for the layer below.

## Overview

```
SOURCE METAPHYSICS (truth map)
       │
       ▼
FACTORY 1: RESEARCH
  Input: Source material, datasets, RO updates
  Process: ROs → EOs → hypothesis testing
  Output: EOs, hypothesis results, truth map updates
  Hermes skill: acquire, search, explore
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
FACTORY 2: WRITING                     FACTORY 3: VIDEO
  Input: EOs, truth map                 Input: EOs
  Process: Academic paper pipeline      Process: Storyboard → render
  Output: Papers, essays                Output: YouTube videos
  Hermes skill: write, source-to-essay  Hermes skill: platinum-designer,
                                         platinum-renderer, factory-pipeline
       │
       ▼
FACTORY 4: ANALYTICS
  Input: All factory outputs
  Process: Performance analysis → truth map updates
  Output: Updated confidence scores, new questions
  Hermes skill: deep-analysis
```

## Factory 1: Research (DETAILED)

```
Source Material (PDF, text, book, dataset)
  → Work JSON (structured metadata)
    → Research Object (extracted passages, agent-optimized)
      → Essay Object (question + evidence synthesis)
        → Hypothesis results (experiment outcomes)
          → Source Metaphysics update
```

### Research Tasks

1. **Acquire** — Download papers/datasets via `acquire` skill
2. **Extract** — Create ROs from source material
3. **Synthesize** — Combine ROs into EOs
4. **Probe** — Hypothesis engine generates questions from tension points
5. **Track** — Update source metaphysics with results

### Key Principle

ROs are source-cetric. EOs are question-centric. Never conflate the two.

## Factory 2: Writing

```
Essay Object
  → Thesis statement
    → Outline (v6 algorithm)
      → First draft
        → Peer review (AI)
          → Final paper
            → Publication
```

The v6 algorithm is the writing process specified in the blog project. It needs to be documented and formalized as a Hermes skill.

## Factory 3: Video

```
Essay Object
  → Storyboard (platinum-designer)
    → Scene functions (PIL code)
      → Render (platinum-renderer)
        → Compile (FableCut)
          → Upload (R2 → YouTube)
```

Already built and working in the blog project. The skills `platinum-designer` and `platinum-renderer` handle this pipeline.

## Factory 4: Analytics

```
Products (papers, videos, experiments)
  → Performance metrics
    → Retain/reject analysis
      → Truth map updates
        → New hypothesis generation
```

Not yet built. Needs to be designed and implemented.

## Hermes Integration

Each factory maps to Hermes skills:

| Factory | Hermes Skill |
|---------|--------------|
| Research | `acquire`, `search`, `explore` |
| Writing | `write`, `source-to-essay` |
| Video | `platinum-designer`, `platinum-renderer`, `factory-pipeline` |
| Analytics | `deep-analysis` |

New skills needed:
- `research-object-creator` — Automates RO creation from source material
- `essay-object-creator` — Combines ROs into EOs
- `hypothesis-engine` — Generates questions from truth map
- `source-metaphysics` — Maintains the truth map

## Inter-Factory Communication

Factories communicate via the file system + git:

1. Research writes ROs/EOs to `content/research-objects/` and `content/essay-objects/`
2. Writing reads EOs from `content/essay-objects/` and writes papers to `content/papers/`
3. Video reads EOs and writes videos to `content/video-objects/`
4. Analytics reads everything and writes to `content/source-metaphysics/`

All factories commit to git after completing a unit of work.
