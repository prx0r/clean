# BLOGREF — Complete Blog Codebase Reference

## Purpose

One file that documents every module in /root/projects/blog/, its current state, what it does, its key files, and how it connects to everything else. Nothing hidden.

---

## 1. factory/ — Platinum Video Factory

**Status:** ✅ ACTIVE
**Purpose:** 13-stage state machine for producing "platinum" video essay packs. The core production pipeline.

**Key Files:**
- `MANUAL.md` — Operator manual
- `README.md` — Factory overview
- `PROCESS-MAP.md` — Visual process map
- `stages.json` — Stage definitions
- `controllers/platinum_controller.py` — Python controller
- `cloudflare/src/controller.js` — Cloudflare Worker controller
- `cloudflare/src/mcp-server.py` — MCP server for factory tools
- `cloudflare/db/schema.sql` — Database schema
- `process/THE-PLATINUM-PROCESS.md` — Detailed process docs
- `registry/gold-pack-registry.json` — Gold pack catalog
- `template/` — Factory templates
- `spec/` — Specifications
- `analysis/` — Factory analysis
- `runs/` — Production runs

**Sub-modules:**
- `archive-v1/` — Old pipeline (archived)
- `cloudflare/` — Cloudflare Worker + MCP server + D1 schema
- `controllers/` — Pipeline controllers
- `fixtures/` — Test fixtures
- `gold/` — Gold pack production
- `notes/` — Factory notes
- `process/` — Process documentation
- `registry/` — Gold pack registry
- `renderers/` — Renderer integrations
- `runs/` — Production run outputs
- `spec/` — Specifications
- `template/` — Templates
- `templates/` — More templates
- `validators/` — Validation rules

**Dependencies:** scripts/renderer/, hermes/, content/publishing/, Cloudflare D1/R2

**Connections:** Takes EOs → produces videos. Feeds analytics factory.

---

## 2. hermes/ — AI Agent Framework

**Status:** ✅ ACTIVE
**Purpose:** The Scholar's Apprentice — AI agent with skill-based capabilities.

**Key Files:**
- `SOUL.md` — Hermes identity and purpose
- `AGENTS.md` — Agent configuration
- `HOW_TO_ACTIVATE_HERMES.md` — Usage guide

**Skills (17 directories):**

### Core Skills
- `core/acquire/` — Paper acquisition via OpenAlex/Crossref/Unpaywall
- `core/curate/` — RO management
- `core/explore/` — Cross-silo search
- `core/search/` — Esoteric-to-science concept mapping
- `core/synth/` — Answer synthesis from internal docs
- `core/publish/` — Type B: mechanical paper publishing
- `core/teach/` — TetraHermes teaching pipeline
- `core/navigate/` — Knowledge graph browser
- `core/factory-pipeline/` — 5-stage content pipeline
- `core/cron-acquire/` — Tier 2 auto-acquisition

### Domain Skills
- `daily-research/` — YouTube niche monitoring (75 channels)
- `market-scan/` — Niche gap analysis
- `platinum-designer/` — PASS 1: design packs
- `platinum-renderer/` — PASS 2: render with Zeus
- `yogi-spotlight/` — Yogi content spotlight
- `astrology/deep-analysis/` — Astrology research
- `video/` — Video production
- `publish-video-fablecut/` — FableCut integration
- `writing/` — Art/audio/write
- `site/` — Deploy/art/astrology/daimon/practice
- `ops/` — Operations/deploy
- `daimon/` — Daily-reading, weekly-review
- `practice/` — Recommend-practice, schedule-ritual
- `source-to-essay/` — Content pipeline
- `gdrive-to-r2/` — Google Drive to R2 sync

**Blueprint Plugins:**
- `plugins/factory/` — MCP tools: clean_narration, integrity_check, extract_passages, generate_voiceover, measure_durations, search_scenes, analyze_output

**Other Subdirs:**
- `blueprints/` — Design blueprints
- `docs/` — Documentation
- `goals/` — Goal tracking
- `notes/` — Handover notes (handover0, handover2, handovernew)
- `scripts/` — Utility scripts

**Dependencies:** content/, scripts/, factory/, data/, Cloudflare D1/R2

**Connections:** Central orchestrator. All factories call Hermes.

---

## 3. hermes-army/ — Multi-Agent Scaling Design

**Status:** ⚠️ PARTIAL
**Purpose:** Architecture spec for scaling Hermes into multiple specialized workers.

**Key Files:**
- `hermescloudflare.md` — Full design document

**Architecture:** Each capability (vision, image gen, video gen, audio, LLM) becomes a Cloudflare Worker. Includes AI Gateway caching, Workflows-based video pipeline, cost analysis.

**Dependencies:** hermes/, farm-template/, Cloudflare Workers AI/Queues/Workflows

**Connections:** Visionary design doc. Not implemented.

---

## 4. farm-template/ — Deployable Content Farm

**Status:** ⚠️ PARTIAL (structurally complete, stubs not implemented)
**Purpose:** Template for creating independent Cloudflare Worker-based content farms.

**Key Files:**
- `docs/01-SETUP.md` — Deployment guide
- `docs/02-RESEARCH.md` — Research pipeline guide
- `docs/03-PRODUCTION.md` — Production pipeline guide
- `scripts/create-farm.sh` — Farm creation script
- `src/index.ts` — Worker entry point
- `src/d1/` — Database schemas
- `src/lib/` — Library (stubs: YouTube API, TTS, rendering, publishing all throw "Not implemented")
- `src/research/` — Research modules
- `wrangler.jsonc` — Cloudflare configuration

**Dependencies:** pipelines/, operations/, Cloudflare Workers/D1/R2/Queues

**Connections:** The deployment target for production farms. Never deployed.

---

## 5. content/ — All Content Assets

**Status:** ✅ ACTIVE
**Purpose:** Every piece of structured content in the system.

**Key Files:**
- `_factory-index.json` — Master content index

**Subdirectories:**

| Subdir | Count | Purpose |
|--------|-------|---------|
| `astrology/` | 8 | Astrology references |
| `authors/` | Many | Author metadata |
| `commentaries/` | 741 | Commentary system |
| `comparison-objects/` | 2 | Cross-RO comparisons |
| `concepts/` | 76 | Concept definitions (23 linked to ROs) |
| `essays/` | 1,796 | Essays (220 content, 1,576 bridge) |
| `factory/` | 8 | Factory index, queue, registry |
| `glossary/` | Many | Glossary entries |
| `indexes/` | Many | Search indexes |
| `mythos/` | Many | Mythological references |
| `ontology-engine/` | Many | Ontology data |
| `philosophers/` | Many | Philosopher profiles |
| `publishing/` | 363 | Storyboards, voiceovers, subtitles |
| `research/` | Many | Research notes |
| `research-objects/` | 178 | ROs across 15 families |
| `schemas/` | 3 | complete-data-model.md, schema.sql, work.schema.json |
| `source/` | Many | Source texts |
| `sources/` | 2,035+ | Source material by tradition |
| `synthesis-objects/` | 0 | Not yet created |
| `video-objects/` | 133 | Video metadata + seed images |
| `works/` | 1,917 | Acquired paper metadata |

**RO Families (from _index.json):**
- topic-across-thinkers (17)
- theme (alchemy, daimon, literature)
- thinker-on-topic (ficino, corbin)
- concept-evolution
- comparative
- reception
- tradition
- practice
- historical-question
- debate
- research-map
- reading-companion
- sourcebook
- research-question

**Dependencies:** All other modules consume content.

**Connections:** The data layer. Everything reads from here.

---

## 6. scripts/ — Python/JS Scripts

**Status:** ✅ ACTIVE
**Purpose:** All automation scripts (~231 entries).

**Key Subdirs:**

### engines/ — Research Analytics
- `headline_score.py` — Headline performance predictor
- `predict_views.py` — View prediction model
- `breakout_v2.py` — Breakout detection
- `topic_taxonomy.py` — Topic classification
- `niche_deep_dive.py` — Niche analysis
- `youniverse_patterns.py` — YouNiverse pattern extraction
- `hermes_knowledge.py` — Knowledge base builder
- `blueprint-to-fablecut.py` — Blueprint to FableCut converter

### renderer/ — Video Rendering Engine
- `renderer.py` — Core PIL rendering engine
- `SYSTEM.md` — Renderer system docs
- `spanda_scenes.py` — Spanda scene pack
- `vbt_magnum.py` — VBT magnum opus scenes
- `p01.py` through `p19.py` — Per-pack scene scripts

### Other Scripts
- `factory-audit.py` — Pipeline validation
- `build-timed-video.py` — Timed video builder
- `visual-director.py` — Visual direction tool
- `build.mjs` — GitHub Pages deployment
- `engines/` — Research analytics
- `pipeline/` — Pipeline scripts
- `probes/` — System probes
- `skinner-sections/` — Skinner section analysis

**Dependencies:** content/, factory/, scene-system/, visual-library/

**Connections:** The execution layer. Factories call these scripts.

---

## 7. src/ — Next.js Web Application

**Status:** ✅ ACTIVE
**Purpose:** The blogengine website (blog.tantraloka.com or similar).

**Key Files:**
- `app/layout.tsx` — Root layout
- `app/page.tsx` — Home page (feed)
- `app/api/` — API routes
- `lib/db.ts` — Database client
- `lib/ai.ts` — AI Gateway integration
- `lib/essays.ts` — Essay library
- `lib/types.ts` — TypeScript types
- `middleware.ts` — API auth middleware
- `pipeline/` — Chart similarity, compute, experiments, fetch, etc.
- `astrology/` — Astrology engine
- `atlas/` — Atlas visualizations
- `components/` — React components
- `data/` — Static data

**Routes:** /, /elements, /art, /astrology, /atlas, /audio, /birth-chart, /books, /chat, /daimon, /essay, /essays, /glossary, /journal, /login, /meditation, /observatory, /personal, /rituals, /settings, /sources, /spells, /tree-of-life

**Dependencies:** content/, data/, workers/

**Connections:** Public-facing website. Deployed via GitHub Pages + Vercel.

---

## 8. workers/ — Cloudflare Workers

**Status:** ✅ ACTIVE
**Purpose:** API proxying and LLM routing.

**Key Files:**
- `proxy-worker.ts` — OpenCode proxy for LLM API calls
- `youtube-proxy.ts` — YouTube Data API proxy with caching
- `wrangler.toml` — Worker configs

**Dependencies:** src/lib/ai.ts

**Connections:** Routes API calls through Cloudflare for caching and auth.

---

## 9. essayglobal/ — Essay Generation

**Status:** ✅ ACTIVE
**Purpose:** Essay writing methodology and generation system.

**Key Files:**
- `essaygen/essayguide.md` — Complete essay writing guide
- `essaygen/v7algorithm.md` — V7 algorithm (current preferred)
- `essaygen/v6algorithm.md` — V6 algorithm (predecessor)
- `essaygen/perfectessay.md` — Perfect essay template
- `essaygen/essayprocess.md` — Essay writing process
- `essaygen/issuesessay.md` — Issues with essay writing
- `essaygen/antislop.md` — Anti-slop guardrails
- `essaygen/rumiengine.md` — Rumi poetic patterns
- `essaygen/ficinoextraction.md` — Ficino extraction method
- `essaygen/thesismaster.md` — Thesis mastery guide
- `essaygen/newgraph.md` — New knowledge graph methodology
- `essaygen/generate-long-essay.mjs` — Long-form essay generator
- `essaygen/workshop/` — Writing workshop materials
- `blueprints/` — Essay blueprints

**Dependencies:** content/sources/, content/research-objects/, scripts/

**Connections:** Writing Factory uses these algorithms.

---

## 10. operations/ — Operations Reference

**Status:** ✅ ACTIVE
**Purpose:** Complete operations documentation (31 documents).

**Key Files:**
- `COMPLETE-REFERENCE.md` — 538-line project reference
- `current-state-handover.md` — Current state (art + video pipeline)
- `content-production-spec.md` — Content production specification
- `video-creation-spec.md` — Video creation specification
- `render-engine-handover.md` — Render engine handover
- `hermes-video-pipeline.md` — Hermes video pipeline docs
- `ml-pipeline.md` — ML pipeline specs
- `cloudflare-factory-plan.md` — Cloudflare factory deployment
- `dashboard-build-spec.md` — Dashboard build specification
- `dataset-download-handover.md` — Dataset download docs
- `content-farm-infrastructure.md` — Content farm infrastructure spec
- `build-plan.md` — Build plan
- `layer1-handover.md` — Layer 1 handover
- `infrastructure-wishlist.md` — Infrastructure wishlist
- `pipeline-designs/` — Pipeline design docs
- Various channel profiles, building plans, and agent guides

**Dependencies:** factory/, hermes/, content/, scripts/, pipelines/

**Connections:** Reference for all operational procedures.

---

## 11. pipelines/ — Research Pipelines

**Status:** ✅ ACTIVE
**Purpose:** Dataset research pipelines and academic methodology.

**Key Files:**
- `README.md` — Pipeline overview
- `hermes-alchemy.md` — 7 Hermetic operations framework
- `the-loom.md` — Self-replicating media foundry vision
- `hermes-operations-manual.md` — Engine definitions E1-E8
- `control-plane-design.md` — Approval gates, TryPost integration
- `r2-dataset-reference.md` — R2 bucket inventory
- `farm-implementation-plan.md` — Farm deployment plan
- `dashboard-stream.md` — Dashboard data stream design
- `research-stream.md` — Research data stream design

**Dataset Pipelines:**
| Pipeline | Data | Status |
|----------|------|--------|
| `youniverse/` | 136k channels, 72.9M videos | ✅ Active |
| `global-trending/` | 104 countries, 726k videos | ✅ Active |
| `yt30m-comments/` | 32M multilingual comments | ✅ Active |
| `regional-audit/` | 915k geolocated search results | ✅ Active |
| `proposals/` | Pipeline proposals | ⚠️ Partial |
| `hermes-army/` | Multi-worker design | ⚠️ Partial |
| `reddit-intelligence/` | Reddit signal extraction | ⚠️ Partial |

**Dependencies:** data/, scripts/engines/, dataset/, R2 (research-datasets)

**Connections:** Provide research intelligence for the Analytics Factory.

---

## 12. data/ — Research Data

**Status:** ✅ ACTIVE
**Purpose:** YouTube intelligence data outputs and research results.

**Key Files:**
- `README.md` — Pipeline spec
- `SCHEMA.json` — Data schema
- `research/layer2/` — Layer 2 research results
- `research/youniverse/` — YouNiverse research outputs
- `research/upworthy/` — Upworthy dataset analysis
- `market/` — Market research reports
- `reports/` — Research reports
- `review/` — Review data
- `yogis/` — Yogi profiles
- `tts-cache/` — TTS audio cache
- `api-usage-log` — API usage tracking
- `hermes-knowledge.json` — Hermes knowledge base
- `thumbnail-candidates.json` — Thumbnail candidates

**Dependencies:** pipelines/, scripts/engines/, dataset/

**Connections:** Data layer for Analytics Factory.

---

## 13. sourcematerial/ — Curated Source Material

**Status:** ✅ ACTIVE
**Purpose:** Primary source texts for the Tantraloka research programme.

**Subdirs:**
- `trika/` — Kashmir Shaivism: Tantraloka 56K-line clean text, Shiva Sutras, Spanda Karika
- `platonic/` — Enneads PDF, Ficino Platonic Theology, Proclus, Theurgy, Iamblichus
- `sufi/` — Ibn Arabi (Fusus), Suhrawardi (Illuminationist), Henry Corbin
- `matter-of-wonder/` — Loriliai Biernacki OUP monograph (RO + 7 extracted passages)
- `hermeneutics-of-absolute/` — Bettina Baumer study (RO + 8 extracted passages)
- `utpaladeva-ipk/` — IPK translation by R. Torella (RO + commentary notes)
- `researchsources/` — 100 ranked sources bibliography

**Dependencies:** content/sources/, scholars/, content/research-objects/

**Connections:** Primary input for the Research Factory.

---

## 14. scholars/ — Scholar Paper Collections

**Status:** ✅ ACTIVE
**Purpose:** Curated paper collections by scholar.

**Subdirs:** corbin/, ficino/, ibn_arabi/, jung/, shaw/, swedenborg/, theurgy/, voss/, astrology/

Each contains papers/ (PDFs), notes/, and READMEs.

**Dependencies:** content/works/, content/research-objects/

**Connections:** Source material for RO creation.

---

## 15. visual-library/ — Scene Code Library

**Status:** ⚠️ PARTIAL
**Purpose:** Reusable visual scene code for video rendering.

**Key Files:**
- `catalog/scenes.json` — Master scene index
- `catalog/ingest_packs.py` — Pack ingestion
- `core_scenes.py` — Core scene definitions
- `concept_packs.py` — Concept visualization packs
- `experimental_techniques.py` — Experimental rendering
- `spanda_karika_pack.py` — Spanda Karika scenes
- `vijnana_bhairava_pack.py` — Vijnana Bhairava scenes
- `primitives/` — Empty
- `templates/` — Empty
- `instances/` — Instance tracking
- `previews/` — Scene preview images

**Dependencies:** scripts/renderer/, scene-system/

**Connections:** Scene packs used by the Video Factory renderer.

---

## 16. scene-system/ — Scene Catalog System

**Status:** ⚠️ PARTIAL
**Purpose:** Structured catalog of all visual scenes with primitives and concept mappings.

**Key Files:**
- `build.py` — Catalog compiler
- `ENGINE.md` — Engine documentation
- `primitives/_index.json` — Primitive definitions (dot, line, ring, arrow, card, flower, silhouette, text)
- `catalog/scenes.json` — Compiled scene catalog
- `concepts/` — Concept-to-scene mappings
- `instances/` — Scene instance tracking
- `packs/` — Gold pack outputs
- `templates/` — Scene templates

**Dependencies:** visual-library/, scripts/renderer/, video-templates/

**Connections:** Indexes visual library for agent use.

---

## 17. visionary-renderer/ — Next-Gen Renderer

**Status:** ⚠️ PARTIAL
**Purpose:** GPU-accelerated renderer using Skia (2D) + Three.js (3D), replacing PIL.

**Key Files:**
- `ARCHITECTURE.md` — Renderer architecture
- `render-three-spanda.mjs` — Three.js render test
- `capture-spanda.mjs` — Spanda capture
- `capture-three.mjs` — Three.js capture
- `three-spanda.html` — Three.js HTML canvas
- `src/` — Source code
- `assets/` — Render assets
- `renders/` — Output renders
- `scripts/` — Utility scripts
- `test-scenes/` — Test scene files

**Phase 1 Gates (passing):** Devanagari shaping, SVG layer extraction, deterministic timeline, 20s Spanda render spike.

**Dependencies:** scene-system/, visual-library/, scripts/renderer/

**Connections:** Will eventually replace PIL renderer in Video Factory.

---

## 18. sanskritree/ — Computational Sanskrit

**Status:** ✅ ACTIVE
**Purpose:** Sanskrit computational linguistics engine.

**Stats:** 47 source files, 13 tests (59 passing), 351MB SQLite DB, 40 tables, 136K token analyses, 6K lexemes, 16K morph analysis types, 169K token occurrences, 8.8K passages across 5 works.

**Coverage:** Spandakarika 98%, Vijnanabhairava 99%, Bhagavad Gita 37%.

**Key Files:**
- `docs/AUDIT.md` — System audit
- `docs/CHECKPOINT1_REPORT.md` — Checkpoint 1
- `docs/CHECKPOINT2_REPORT.md` — Checkpoint 2
- `docs/deepsanskrit.md` — DeepSanskrit architecture
- `docs/synthdev.md` — Synth development
- `src/` — Source code
- `texts/gretil_tantraloka.txt` — Tantraloka text
- `texts/gretil_vakyapadiya.txt` — Vakyapadiya text
- `manifests/` — Model manifests
- `references/` — Reference materials

**Dependencies:** content/sources/tantra/, GRETIL text corpus

**Connections:** Independent subsystem. Can feed Sanskrit analysis into Trika ROs.

---

## 19. geometricengine/ — UNO Therapy Engine

**Status:** ✅ ACTIVE (independent)
**Purpose:** Graph-native pedagogical policy engine trained from UNO therapy transcripts. Uses learned edge weights to select teaching pathways without LLM in the cognition path.

**Key Files:**
- `README.md` — Engine overview
- `src/train.py` — Training pipeline
- `src/pathway.py` — Pathway selection
- `src/retrieve.py` — Vector search retrieval
- `src/graph.py` — Graph construction
- `src/weights.py` — Policy weight management
- `src/ingest_uno.py` — UNO data ingestion
- `src/embed.py` — Embedding generation
- `server.py` — API server
- `TESTING.md` — Testing guide
- `data/` — Training data
- `uno/` — UNO transcripts
- `tests/` — Test suite

**Dependencies:** None (self-contained)

**Connections:** Independent. Could be integrated as pedagogical pathway generator for EOs.

---

## 20. exemplars/ — Gold Standard Videos

**Status:** ✅ ACTIVE
**Purpose:** Video exemplar analyses for gold-standard reference.

**Subdirs:**
- `gold-standards/` — JSON analyses: alan-watts, anandamayi-ma, nisargadatta, jesus-himalayas, aoi-pretend-less-intelligent, aoi-western-worldview
- `academy-of-ideas/` — Full exemplar package
- `alan-watts/` — Alan Watts analysis
- `anandamayi-ma/` — Anandamayi Ma analysis
- `eternalised-shadow/` — Eternalised analysis
- `nisargadatta/` — Nisargadatta analysis
- `jesus-himalayas/` — Jesus in the Himalayas analysis
- `gold-standard-videos.zip` — Compressed gold references

**Dependencies:** video-templates/, operations/

**Connections:** Reference for Video Factory gold study stage.

---

## 21. video-templates/ — Video Production Templates

**Status:** ✅ ACTIVE
**Purpose:** Templates and references for video production.

**Subdirs:**
- `animation-references/` — Animation reference materials
- `gold-standards/` — Gold standard templates
- `modules/` — Video production modules

**Dependencies:** exemplars/, factory/

**Connections:** Templates used by Video Factory.

---

## 22. dashboard/ — Operator Cockpit

**Status:** ⚠️ PARTIAL
**Purpose:** Flask dashboard for content farm operations.

**Key Files:**
- `server.py` — 639-line Flask app
- `static/index.html` — Frontend
- `functions/api/[[path]].js` — Serverless API route

**Views:** Factory jobs, research data, FableCut status, art library stats.

**Dependencies:** factory/, scripts/engines/, data/, content/publishing/

**Connections:** Not fully connected to all backend services.

---

## 23. dataset/ — Raw Experiment Data

**Status:** ⚠️ PARTIAL
**Purpose:** Raw dataset storage for the art pipeline.

**Subdirs:**
- `raw/deities-25/` — 8,239 deity images (download stuck)
- `raw/cirthan/` — CIRThan thangka data
- `raw/cytky1/` — CYTKv1 thangka data

**Dependencies:** operations/ (art library pipeline), scripts/ (labeling/ingestion)

**Connections:** Raw data for art pipeline.

---

## 24. notes/ — Personal Research Notes

**Status:** ✅ ACTIVE
**Purpose:** Scratchpad and brainstorming (~62 files).

**Key Files:**
- `factory-spec.md` — Formal 5-stage pipeline spec
- `factory-analytics.md` — YouTube Analytics feedback loop
- `factory-manual.md` — Factory operations manual
- `factory-template.md` — Factory template
- `factory-cleanup.md` — Factory cleanup guide
- `videos-pipeline.md` — Video pipeline notes
- `youtubemaster.md` — YouTube strategy
- `youtubemaster2.md` — YouTube strategy v2
- `handovervideo.md` — Video handover notes
- Various topical notes

**Dependencies:** factory/, content/

**Connections:** Operator reference.

---

## 25. archive/ — Archived Content

**Status:** ❌ ARCHIVED
**Purpose:** Old project iterations.

**Subdirs:**
- `handovers/` — Handover docs 1-10
- `v1-pipeline/` — Old pipeline (DO NOT USE)
- `tetrahermes/` — Old TetraHermes system
- `media/` — Old media files
- `root-files/` — Old root files
- `uncategorized/` — Uncategorized content

**Key Files:**
- `v1-pipeline/ARCHIVE-MANIFEST.md` — Archive explanation
- `v1-pipeline/BREAKTHROUGH.md` — Key insight (preserved)

**Dependencies:** None

**Connections:** Legacy. Reference only.

---

## 26. Tests and Eval

### tests/
**Status:** ⚠️ PARTIAL
**Purpose:** Evaluation and test suite.
**Subdirs:** `eval/` — Evaluation tests

### test-results/
**Status:** ⚠️ PARTIAL
**Purpose:** Test output storage.

---

## 27. Minor Modules

| Module | Status | Purpose |
|--------|--------|---------|
| `agents/` | active | Agent configuration files |
| `science/` | active | Scientific paper reviews |
| `reviews/` | active | External critiques (including farm-critique-analysis.md) |
| `gowan-papers/` | partial | Gowan paper collection |
| `gowan-papers-extracted/` | partial | Extracted Gowan papers |
| `tantrafiles/` | partial | Tantra-specific blueprints |
| `hypothetical/` | partial | Hypothetical designs |
| `hypothetical-integrated/` | partial | Integrated system design documents |
| `media/` | active | Images, texts, videos |
| `library/` | active | Library of PDFs, ebooks, source-texts, astrology, science |
| `blueprints/` | partial | Source text blueprints |
| `resources/` | partial | Reference resources |
| `synthesis-essays/` | partial | Synthesis essay collection |
| `tetrahermesideacatalogue/` | partial | Idea catalogue |
| `visual-library/` (previews) | partial | Scene preview images |
| `public/` | active | Public assets: art, audio, daimon, lab, symbols, thumbnails, videos |
| `sanskritree/` | active | Also has `references/` subdir |

---

## 28. Configuration & Build Files

| File | Purpose |
|------|---------|
| `package.json` | Node dependencies |
| `next.config.ts` | Next.js configuration |
| `tsconfig.json` | TypeScript configuration |
| `eslint.config.mjs` | ESLint configuration |
| `postcss.config.mjs` | PostCSS configuration |
| `wrangler.jsonc` | Cloudflare Workers config |
| `wrangler.toml` | Cloudflare Workers config (alt) |
| `.env.local` | Local environment variables |
| `.env.example` | Environment template |
| `.dev.vars` | Development variables |
| `cloudflare-env.d.ts` | Cloudflare type definitions |
| `vercel.json` | Vercel deployment config |
| `open-next.config.ts` | OpenNext config |
| `AGENTS.md` | Agent instructions |
| `CLAUDE.md` | Claude configuration |
| `AUDIT.md` | System audit |
| `HANDOVER.md` | Master handover doc |
| `HANDOVER-COMPLETE.md` | Complete handover |
| `HANDOVER-QUICKSTART.md` | Quickstart guide |
| `ULTIMATE_HANDOVER.md` | Ultimate handover reference |
| `THESIS.md` | Thesis document |
| `PROBLEM-STATEMENT.md` | Problem statement |
| `FINALLY.md` | Final notes |
| `README.md` | Project overview |

---

## Dependency Graph

```
hermes (orchestrator)
  ├── factory/ (video pipeline)
  │   ├── scripts/renderer/ (PIL rendering)
  │   ├── visual-library/ (scene packs)
  │   │   └── scene-system/ (scene catalog)
  │   ├── content/publishing/ (storyboards)
  │   ├── workers/ (Cloudflare proxies)
  │   └── Cloudflare (D1, R2, Workers AI)
  │
  ├── hermes/plugins/factory/ (MCP tools)
  │
  ├── content/ (data layer)
  │   ├── research-objects/ (ROs)
  │   ├── works/ (acquired papers)
  │   ├── essays/ (published essays)
  │   └── schemas/ (data models)
  │
  ├── essayglobal/essaygen/ (writing methodology)
  │
  ├── pipelines/ (research intelligence)
  │   └── data/ (research outputs)
  │       └── scripts/engines/ (analytics)
  │
  ├── sourcematerial/ (primary sources)
  ├── scholars/ (paper collections)
  │
  ├── dashboard/ (operator UI)
  │
  └── farm-template/ (deployment target)
      └── hermes-army/ (scaling vision)

Independent subsystems:
  ├── sanskritree/ (Sanskrit NLP)
  ├── geometricengine/ (UNO therapy)
  ├── visionary-renderer/ (next-gen rendering)
  └── src/ (Next.js website)
```

---

## Migration Path to Clean Project

The `clean/` project should eventually contain:

```
clean/
├── RESEARCH_DIRECTIVE.md       # Full agent prompt
├── magnum-opus/                # This architecture spec
├── neurodatasets/              # Dataset access documentation
├── researchers/                # Anālayo papers, future scholars
├── researchideas/              # Essay proposals (ideas1.md)
├── researchsources/            # 100 ranked sources
└── resources/                  # Bibliographies, by-scholar papers
```

The blog project remains the operational codebase. The clean project is the **research nucleus** — pure knowledge, no implementation complexity.
