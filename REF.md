# Clean — Project Reference

Research nucleus for the Trika–Consciousness-Science content pipeline. Everything an agent needs to understand the project, its modules, and where to start.

---

## Root Files

| File | Purpose |
|------|---------|
| `RESEARCH_DIRECTIVE.md` | Master agent prompt. Read this first. Defines the research programme, methodology, 72 priority questions, source strategy, essay output structure, quality controls. Every agent should start here. |
| `REF.md` | This file. Project index. |

---

## magnum-opus/ — Full System Architecture

The architectural blueprint for the entire content factory ecosystem. 18 spec files covering vision, flaws, factories, and future platforms.

| File | Purpose |
|------|---------|
| `README.md` | Overview of all 18 spec files |
| `01-VISION.md` | Unified vision: closed-loop epistemology engine |
| `02-AUDIT-SUMMARY.md` | Current state of all blog project assets (1,917 works, 178 ROs, etc.) |
| `03-RESEARCH-OBJECTS.md` | RO system spec: versioned, source-linked, agent-navigable |
| `04-ESSAY-OBJECTS.md` | EO system spec: guided enquiries combining ROs into focused questions |
| `05-SOURCE-METAPHYSICS.md` | Truth map: tracking solved/unsolved questions with evidence weights |
| `06-FACTORY-ARCHITECTURE.md` | Four factories (Research, Writing, Video, Analytics) with sub-units |
| `07-HYPOTHESIS-ENGINE.md` | Perpetual question generation from truth map gaps |
| `08-FARM-INFRA.md` | Cloudflare farm deployment (Worker, D1, R2, Queues) |
| `09-HERMES-ORCHESTRATION.md` | Hermes coordination, skill map, invocation patterns |
| `10-FULL-SPEC.md` | Comprehensive spec: all modules, todos, Cloudflare AI models, workflows |
| `11-BLOGREF.md` | Complete blog codebase reference — every directory documented |
| `12-SANSKRIT-FACTORY.md` | Sanskrit philology factory: 7-pass DeepSeek translation → TO objects |
| `13-FLAWS.md` | Honest risk assessment — 11 identified flaws with severity ratings |
| `14-VISIONARY.md` | Best-case pathways — 8 unbuilt features that could make it legendary |
| `15-GREENSCREEN.md` | Satsang.digital platform thesis — ethical YouTube alternative |
| `16-GTM.md` | Go-to-market strategy for Satsang — phases 0-3 |
| `17-VIDEO-FACTORY-HITL.md` | Human-in-the-loop review system spec (studio + FableCut + Voicebox) |
| `18-ANAKHRARENDER.md` | Complete render pipeline spec — scene review, feedback loop, versioning |

---

## neurodatasets/ — Dataset Access

Reference for accessing neuroscience and meditation datasets for the research programme.

| File | Purpose |
|------|---------|
| `DIRECTIVE.md` | Research directive for dataset acquisition — which databases to query, how |
| `AGENT-DATASOURCE.md` | Working dataset access methods — OpenNeuro S3, NeuroVault, Zenodo, OSF |
| `DATASETS.md` | Log of datasets found, attempted, and their status |
| `S3-ACCESS.md` | CONFIRMED: OpenNeuro S3 direct access with `--no-sign-request` |

**Key discovery:** All OpenNeuro datasets are publicly accessible via S3: `aws s3 sync s3://openneuro.org/{DS_ID}/ ./target/ --no-sign-request --region us-east-1`

Known datasets: ds001787 (EEG meditation), ds006644 (DMT+meditation fMRI), ds007921 (chakra meditation), ds004640 (consciousness), ds005365 (breathwork altered states).

---

## researchers/ — Scholar Profiles

| File | Purpose |
|------|---------|
| `analayo/` | 30 Anālayo papers with MD summaries + 27 downloaded PDFs |
| `future-scholars.md` | 15 priority scholars for future research (Timalsina, Ratié, Torella, etc.) |

---

## researchideas/ — Essay Proposals

| File | Purpose |
|------|---------|
| `ideas1.md` | 20 essay proposals across 4 arcs (grammar of manifestation, ground, individuation, why manifestation) |

---

## researchsources/ — Bibliographies

| File | Purpose |
|------|---------|
| `100sources.md` | 100 ranked sources across 5 categories + 20 full-length books + 5-priority essay sequence |

---

## resources/ — Downloaded Papers

| Location | Contents |
|----------|----------|
| `by-scholar/` | Papers organized by author (analayo, biernacki, metzinger, laukkonen, etc.) |
| `by-scholar/README.md` | Scholar library index |
| `pdfs/full-books/` | Extracted full-book texts (Ferrante, Timalsina, Utpaladeva) |

---

## Agent Quickstart

1. **Read `RESEARCH_DIRECTIVE.md`** — understand the research programme
2. **Check `magnum-opus/10-FULL-SPEC.md`** for the complete architecture
3. **Consult `magnum-opus/13-FLAWS.md`** before making architectural decisions
4. **Use `researchsources/100sources.md`** for paper discovery
5. **Access datasets via** `neurodatasets/S3-ACCESS.md`
6. **Find downloaded papers in** `resources/by-scholar/`
7. **Reference the blog codebase** via `magnum-opus/11-BLOGREF.md`
