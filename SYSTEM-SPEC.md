# System Specification — What We Are Building

## The Goal

We have 72+ research questions (from RESEARCH_DIRECTIVE.md) spanning Trika, consciousness science, neuroscience, and philosophy of mind. We want to answer them systematically.

The system exists to:
1. **Organize** our research materials (papers, translations, datasets)
2. **Produce** content (essays, videos) that answers the questions
3. **Track** what we've learned and what we haven't

---

## The Data Flow (End to End)

```
RESEARCH MATERIALS
  Paper (arxiv PDF)
  Sanskrit text (GRETIL)
  Dataset (OpenNeuro EEG)
       │
       ▼
  SO — Source Object (immutable metadata for one source)
       │
       ├──→ RO — Research Object (themed passage extraction from SO)
       │         │
       │         ├──→ TO — Translation Object (Sanskrit 7-pass translation)
       │         │
       │         ├──→ Claim — atomic evidence unit → TRUTH MAP
       │         │
       │         └──→ EO — Essay Object (one structured tension point, uses multiple ROs)
       │                    │
       │                    ├──→ Factory 2 (Writing) → Essay
       │                    └──→ Factory 3 (Video) → YouTube video
       │
       └──→ TRUTH MAP — tracks all 72+ questions, evidence, and progress
                    │
                    ├──→ Highlights which questions are most underdetermined
                    ├──→ Hypothesis Engine proposes new EOs for gaps
                    └──→ Every published essay/video updates the truth map
```

---

## Each Component's Purpose

### SO — Source Object
**Why:** We need one canonical record for every paper, text, or dataset we use. Metadata, DOI, how to access it. Immutable — never changes after creation.
**Status:** Spec exists (specs/SO.md). Zero instances exist in this project (blog project has 1917 Works that need migration).

### RO — Research Object
**Why:** Raw source material is too unstructured for agents to work with. An RO extracts the relevant passages from an SO, organizes them by theme, and makes them navigable. It's NOT analysis — it's the source material prepared for agent consumption.
**Status:** Spec exists (specs/RO.md). 178 ROs exist in the blog project but not in this project. 43 ready, 110 need work, 34 stubs.

### TO — Translation Object
**Why:** Sanskrit texts need rigorous, auditable translations. The 7-pass DeepSeek pipeline produces translations with confidence scores per verse, alternative scholarly translations, and full reasoning chain.
**Status:** Spec exists (specs/TO.md). Spandakārikā translated at 98.8% accuracy but not formalized as TO.

### EO — Essay Object
**Why:** This is the bridge between research and production. An EO takes one tension point, gathers relevant ROs from both sides (e.g., Trika + cognitive science), states the competing hypotheses, and organizes them into a structured enquiry. Factories then consume EOs to produce essays/videos.
**Status:** Spec exists (specs/EO.md). **Zero EOs exist. This is the critical gap.**

### Truth Map
**Why:** Tracks progress against the 72+ research questions. For each question: what evidence supports it, what contradicts it, how confident we are, what content we've produced, what evidence is still missing. The publish gate forces every piece of content to update at least one question.
**Status:** Engine partially built (F1-F8 propagation), D1-D5 cascade in progress. 6 questions seeded. 66+ need creation.

### Factory 2 (Writing)
**Why:** Takes EOs, produces essays via V7 algorithm. Quote budget gates ensure rigorous sourcing.
**Status:** Blog project has the V7 algorithm and essay pipelines. 1796 essays exist.

### Factory 3 (Video)
**Why:** Takes EOs, produces YouTube videos via 13-stage platinum pipeline (storyboard → PIL/GLSL render → FableCut compile → YouTube).
**Status:** 99 platinum packs exist, 11 rendered, 19 queued. Active pipeline.

### Factory 4 (Analytics)
**Why:** Measures content performance, feeds engagement data back to the truth map as evidence. "People watched this video about question X for 80% of its length" is a data point.
**Status:** Not implemented. YouNiverse pipeline (72.9M videos) exists as research but not integrated.

---

## How They Connect (The Loop)

```
Upstream (inputs):
  SO → RO → Claim → Truth Map
  SO → RO → EO → Factory 2/3 → Content

Downstream (outputs from content):
  Content performance → Analytics → Truth Map updates
  Content claims extracted → Truth Map updates

Research direction:
  Truth Map gaps → Hypothesis Engine → EO proposals → Factory 2/3 → Content

Publish gate:
  Before publishing: "What truth map question does this answer?"
  If none: don't publish
  If answered: include evidence update with the content
```

## Current Status

| Component | Spec | Implementation | In This Project |
|-----------|------|---------------|-----------------|
| SO | specs/SO.md | ❌ Not started | 0 instances |
| RO | specs/RO.md | ❌ Not started | 0 instances (178 in blog project) |
| TO | specs/TO.md | ❌ Not started | 0 instances (Spanda exists raw) |
| EO | specs/EO.md | ❌ **Critical gap** | 0 instances |
| Truth Map | TRUTHMAP-REDESIGN.md | ⚠️ Partial (F1-F8 works, D1-D5 in progress) | 6 questions seeded |
| Factory 2 | magnum-opus docs | ✅ Working in blog project | Not present |
| Factory 3 | magnum-opus docs | ✅ Working | beautify/ queue/ packs |
| Factory 4 | magnum-opus docs | ❌ Not started | Not present |
