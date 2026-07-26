# Magnum Opus — Full System Spec

## Architecture Overview

```
                         ┌──────────────────────────────────────┐
                         │         SOURCE METAPHYSICS           │
                         │  (truth map: solved/unsolved map)    │
                         └──────────────────┬───────────────────┘
                                            │
                         ┌──────────────────▼───────────────────┐
                         │         HYPOTHESIS ENGINE             │
                         │  (perpetual question generation)      │
                         └──────────────────┬───────────────────┘
                                            │
┌───────────────────────────────────────────▼───────────────────────────────────────────┐
│                               FACTORY 1: RESEARCH                                     │
│                                                                                       │
│  Source Material → Works → Research Objects → Essay Objects → Hypothesis Results      │
│                                                                                       │
│  Sub-units:                                                                           │
│  ├── 1a. ACQUIRE — paper/dataset downloading (Hermes acquire skill + S3 datasets)    │
│  ├── 1b. EXTRACT — source → RO creation                                             │
│  ├── 1c. SYNTHESIZE — ROs → EOs (guided enquiries)                                   │
│  ├── 1d. PROBE — hypothesis engine (perpetual question gen)                           │
│  ├── 1e. SANSKRIT — computational linguistics (sanskritree)                           │
│  └── 1f. TRACK — source metaphysics (truth map maintenance)                           │
└──────────┬────────────────────────────────────────────────┬──────────────────────────┘
           │                                                │
           ▼                                                ▼
┌──────────────────────────┐                ┌──────────────────────────┐
│  FACTORY 2: WRITING      │                │  FACTORY 3: VIDEO        │
│                          │                │                          │
│  Essay Object            │                │  Essay Object            │
│    → Thesis              │                │    → Gold Study          │
│    → V7 Draft            │                │    → Rhetorical Map      │
│    → Peer Review         │                │    → Visual Thesis       │
│    → Final Paper         │                │    → Storyboard          │
│    → Publication         │                │    → Render (PIL/Skia)   │
│                          │                │    → Compile (FableCut)  │
│  Sub-units:              │                │    → Upload (YouTube)    │
│  ├── 2a. ACADEMIC        │                │                          │
│  ├── 2b. BLOG            │                │  Sub-units:              │
│  └── 2c. NARRATIVE       │                │  ├── 3a. GOLD DESIGN     │
└──────────┬───────────────┘                │  ├── 3b. PLATINUM RENDER │
           │                                │  ├── 3c. VISIONARY RDR   │
           ▼                                │  └── 3d. FABLECUT COMPILE│
┌──────────────────────────┐                └──────────────────────────┘
│  FACTORY 4: ANALYTICS    │
│                          │
│  Products → Metrics      │
│  → Truth Map Updates     │
│  → New Hypotheses        │
│                          │
│  Sub-units:              │
│  ├── 4a. YOUTUBE ANALYT  │
│  ├── 4b. TRUTH MAP OPS   │
│  └── 4c. FARM INTELLIGENCE
└──────────────────────────┘
```

---

## Module Inventory (From Audit)

### CORE — Active & Essential

| Module | Status | Purpose | Key Files |
|--------|--------|---------|-----------|
| `factory/` | ✅ ACTIVE | 13-stage platinum video pipeline | `MANUAL.md`, `PROCESS-MAP.md`, `cloudflare/src/mcp-server.py`, `controllers/platinum_controller.py` |
| `hermes/skills/core/` | ✅ ACTIVE | AI agent skills (acquire, search, explore, synth, publish, factory-pipeline) | `acquire/SKILL.md`, `factory-pipeline/SKILL.md`, `publish/SKILL.md` |
| `hermes/plugins/factory/` | ✅ ACTIVE | MCP tools for video pipeline | `plugin.yaml`, `tools/clean.py`, `tools/render.py` |
| `content/` | ✅ ACTIVE | All content: 1917 works, 178 ROs, 1796 essays, 363 storyboards | `research-objects/`, `works/`, `publishing/` |
| `content/schemas/` | ✅ ACTIVE | Data model definitions | `complete-data-model.md`, `work.schema.json` |
| `content/factory/` | ✅ ACTIVE | Factory operational data | `index.json`, `queue.json`, `essay-registry.json` |
| `scripts/renderer/` | ✅ ACTIVE | PIL-based rendering engine | `renderer.py`, `SYSTEM.md`, scene scripts p01-p19 |
| `scripts/engines/` | ✅ ACTIVE | Research analytics (headline, breakout, youniverse) | `headline_score.py`, `breakout_v2.py`, `predict_views.py` |
| `essayglobal/essaygen/` | ✅ ACTIVE | Essay generation (V7 algorithm) | `v7algorithm.md`, `essayguide.md`, `thesismaster.md` |
| `operations/` | ✅ ACTIVE | Ops reference (31 docs) | `COMPLETE-REFERENCE.md`, `current-state-handover.md` |
| `src/` | ✅ ACTIVE | Next.js web app (27 routes) | `app/`, `lib/`, `pipeline/` |
| `sourcematerial/` | ✅ ACTIVE | Curated source texts (trika, platonic, sufi) | `trika/README.md`, `matter-of-wonder/` |
| `scholars/` | ✅ ACTIVE | Scholar paper collections | `corbin/`, `ficino/`, `ibn_arabi/`, `shaw/` |
| `workers/` | ✅ ACTIVE | Cloudflare API proxies | `proxy-worker.ts`, `youtube-proxy.ts` |
| `visual-library/` | ✅ ACTIVE | Reusable scene code library | `catalog/scenes.json`, `core_scenes.py`, multiple packs |
| `scene-system/` | ⚠️ PARTIAL | Scene catalog + index | `build.py`, `catalog/scenes.json`, `primitives/_index.json` |
| `farm-template/` | ⚠️ PARTIAL | Farm deployment scaffold (stubs) | `docs/01-SETUP.md`, `src/index.ts` |
| `hermes-army/` | ⚠️ PARTIAL | Multi-worker scaling design | `hermescloudflare.md` |
| `hypothetical-integrated/` | ⚠️ PARTIAL | Integrated system design | `00-ARCHITECTURE.md` through `05-CONTEMPLATIVE-ASSISTANT.md` |
| `dashboard/` | ⚠️ PARTIAL | Operator cockpit Flask app | `server.py`, `static/index.html` |
| `visionary-renderer/` | ⚠️ PARTIAL | Next-gen Skia/Three.js renderer | `ARCHITECTURE.md`, `render-three-spanda.mjs` |
| `dataset/` | ⚠️ PARTIAL | Raw experiment data | `raw/deities-25/`, `raw/cirthan/` |
| `data/` | ✅ ACTIVE | Research pipeline outputs | `research/layer2/`, `research/youniverse/` |
| `pipelines/` | ✅ ACTIVE | Research dataset pipelines | `youniverse/`, `global-trending/`, `hermes-alchemy.md` |
| `exemplars/` | ✅ ACTIVE | Gold-standard video analyses | `gold-standards/alan-watts-analysis.json` |
| `video-templates/` | ✅ ACTIVE | Video production templates | `gold-standards/`, `modules/` |
| `sanskritree/` | ✅ ACTIVE | Computational Sanskrit linguistics | 47 source files, 351MB DB, 98.8% accuracy |
| `geometricengine/` | ✅ ACTIVE | UNO therapy graph engine | `src/train.py`, `src/pathway.py` |
| `archive/v1-pipeline/` | ❌ ARCHIVED | Old pipeline (DO NOT USE) | `ARCHIVE-MANIFEST.md` |

### SUPPORTING — Active but Tangential

| Module | Status | Purpose |
|--------|--------|---------|
| `science/` | active | Scientific paper reviews and topic analyses |
| `agents/` | active | Agent configuration files |
| `blueprints/` | partial | Source text blueprints |
| `notes/` | active | Scratchpad (~62 files) |
| `reviews/` | active | External critiques |
| `tests/` | partial | Evals and test suite |
| `gowan-papers/` | partial | Gowan paper collection |
| `tantrafiles/` | partial | Tantra-specific blueprints |
| `media/` | active | Images, texts, videos |
| `resources/` | partial | Reference resources |
| `synthesis-essays/` | partial | Synthesis essay collection |
| `tetrahermesideacatalogue/` | partial | Idea catalogue |
| `hermes/blueprints/` | partial | Design blueprints |
| `hermes/goals/` | partial | Goal tracking |
| `hermes/docs/` | partial | Documentation |
| `hermes/notes/` | active | Handover notes (handover0-2) |

---

## Factory 1: Research — Detailed Spec

### 1a. ACQUIRE — Source & Dataset Acquisition

**Input:** DOI, URL, title, dataset ID
**Output:** Work JSON + PDF in library/
**Hermes skill:** `acquire`

**Pipeline:**
```
DOI/Title → Crossref/OpenAlex metadata → Find OA copy → Download PDF → Validate → Create Work JSON
Dataset ID → OpenNeuro S3 → Download subject(s) → Create Dataset Record
```

**Data Sources:**
- Papers: OpenAlex, Unpaywall, Crossref, institutional repositories
- Datasets: OpenNeuro S3 (`s3://openneuro.org/{DS_ID}/ --no-sign-request`), NeuroVault, Zenodo, OSF
- Already known datasets: ds001787 (EEG meditation), ds006644 (DMT+meditation fMRI), ds004640 (consciousness), ds005365 (breathwork altered states)

**Status:** ✅ Paper acquisition works. Dataset acquisition method confirmed but needs formalization as Hermes skill.

### 1b. EXTRACT — Source → Research Object

**Input:** Work JSON + PDF text
**Output:** Research Object (RO) in content/research-objects/
**Hermes skill needed:** `research-object-creator` (NEW)

**Pipeline:**
```
Work JSON → Extract passages by theme → Organize into RO body → Link to source → Version in git
```

**Rules:**
- Passages are direct quotes or close paraphrases — no original analysis
- Every passage links to its source by source_id
- One coherent body of material per RO
- RO is agent-navigable — structured for quick comprehension

**Status:** 178 ROs exist. 43 ready, 110 need work, 34 stubs. The `curate` skill exists but is manual. Need automated RO creation from Works.

### 1c. SYNTHESIZE — ROs → Essay Objects

**Input:** Multiple ROs + research question
**Output:** Essay Object (EO) in content/essay-objects/
**Hermes skill needed:** `essay-object-creator` (NEW)

**Pipeline:**
```
Research question → Identify relevant ROs → Combine passages → Add hypotheses → Update truth map → Version
```

**EO Schema:**
```json
{
  "eo_id": "eo:question-slug",
  "title": "Research question title",
  "tension_point": "The exact unresolved tension",
  "primary_ros": ["ro:source-1", "ro:source-2"],
  "hypotheses": [{"h_id": "H1", "claim": "...", "confidence": "moderate"}],
  "source_metaphysics": {"status": "underdetermined", "best_answer": "..."}
}
```

**Status:** ❌ Not implemented. This is the critical gap between current ROs and factory output.

### 1d. PROBE — Hypothesis Engine

**Input:** Source metaphysics truth map
**Output:** EO proposals + truth map updates
**Hermes skill needed:** `hypothesis-engine` (NEW)

**Pipeline:**
```
Scan truth map → Find underdetermined questions → Rank by depth/freshness/priority → Generate EO proposals → Submit
```

**Anti-staleness:**
- Novelty scoring against existing EOs
- Diversity sampling across traditions
- Random offsets in ranking
- Meta-questions: "what are we not asking?"
- Re-open answered questions when new evidence appears

**Cron:** Daily scan, weekly generation cycle.

**Status:** ❌ Not implemented.

### 1e. SANSKRIT — Computational Linguistics

**Input:** Sanskrit text (GRETIL)
**Output:** Token analysis, morphological data, lexical senses
**Subsystem:** `sanskritree/`

**Current State:** 47 source files, 351MB SQLite DB, 136K token analyses, 6K lexemes, 98.8% accuracy on Spanda/Vijnanabhairava. Five works covered including Tantraloka.

**Integration:** Feed Sanskrit analysis results as additional RO passages for Trika-related EOs.

**Status:** ✅ Active, independent. Needs integration with RO pipeline.

### 1f. TRACK — Source Metaphysics

**Input:** All factory outputs + external evidence
**Output:** Living truth map
**Hermes skill needed:** `source-metaphysics` (NEW)

**Truth Map Schema:**
```json
{
  "question_id": "q:consciousness-fundamental",
  "status": "plausible",
  "confidence": 0.6,
  "evidence_for": [{"source": "ro:matter-of-wonder", "weight": 0.4}],
  "evidence_against": [{"source": "eo:brain-damage", "weight": 0.5}],
  "best_answer": "Plausible but underdetermined.",
  "last_updated": "2026-07-26"
}
```

**Question Statuses:** strongly_supported → plausible → underdetermined → speculative → incompatible → unasked

**Staleness Check:** Questions not updated in 90 days flagged for review.

**Status:** ❌ Not implemented. Initial question catalog exists in ideas1.md and RESEARCH_DIRECTIVE.md but not formalized.

---

## Factory 2: Writing — Detailed Spec

### 2a. ACADEMIC — Academic Paper Pipeline

**Input:** Essay Object
**Output:** Academic paper (PDF + JSON)
**Hermes skill:** `write`

**Pipeline:**
```
EO → Thesis statement → Outline (V7 algorithm) → First draft → Peer review → Revision → Final → Publish
```

**V7 Algorithm** (from essaygen/v7algorithm.md):
- Personal stake in the question
- Rhythmic variation in prose
- Deliberate pattern choice over elimination
- Source material integration via ROs
- Anti-slop guardrails

**Status:** ✅ V7 algorithm exists. Essaygen has complete methodology docs. Need automation from EO to paper.

### 2b. BLOG — Website Essay Pipeline

**Input:** Essay Object or EO output
**Output:** Published web essay
**Hermes skill:** `source-to-essay`

**Pipeline:**
```
EO → Next.js content → Published to blogengine site
```

**Status:** ✅ Next.js app exists with essay routes. Source-to-essay skill exists.

### 2c. NARRATIVE — Video Script Pipeline

**Input:** Essay Object
**Output:** Script with timing + visual cues
**Hermes skill:** `platinum-designer`

**Pipeline:**
```
EO → Gold study → Rhetorical map → Script with visual beats → Voiceover generation
```

**Status:** ✅ Built into the platinum factory pipeline.

---

## Factory 3: Video — Detailed Spec

### 3a. GOLD DESIGN — Storyboard Creation

**Input:** Essay Object
**Output:** Gold pack (storyboard + visual plan)
**Hermes skill:** `platinum-designer`

**Pipeline:**
```
EO → Gold study (read exemplars) → Rhetorical map → Visual thesis → Storyboard → Review
```

**13-stage platinum process:**
1. `gold_study` — Analyze exemplars for structure/pacing
2. `rhetorical_map` — Map argument flow
3. `visual_thesis` — Design visual metaphors for each point
4. `motif_manufacturability` — Can we render these?
5. `storyboard` — Write scene-by-scene breakdown
6. `storyboard_review` — Review against gold standards
7. `pack_composition` — Create production pack
8. `render_plan` — Plan PIL/Skia scenes
9. `code_review` — Review render code
10. `draft_render` — First render
11. `visual_qc` — Quality check frames
12. `final_render` — Full render
13. `delivery` — Deliver to FableCut

**Status:** ✅ Active. The platinum pipeline is the current working production system.

### 3b. PLATINUM RENDER — PIL Rendering

**Input:** Storyboard + scene functions
**Output:** Rendered frames + audio
**Hermes skill:** `platinum-renderer`

**Pipeline:**
```
Storyboard → Scene functions (Python/PIL) → Render frames → Composite with audio → Final video
```

**Status:** ✅ Active. `scripts/renderer/` has the core engine. Scene packs in `visual-library/`.

### 3c. VISIONARY RENDER — Next-Gen (Skia/Three.js)

**Input:** Storyboard
**Output:** Rendered frames (GPU-accelerated)
**Backends:** Skia (2D), Three.js (3D), WebGPU (shaders)

**Current State:** Phase 1 gates complete. Devanagari shaping, SVG extraction, deterministic timeline, 20s Spanda render spike working. Not yet production.

**Status:** ⚠️ Partial. Experimental but promising. Will eventually replace PIL.

### 3d. FABLECUT COMPILE — Final Assembly

**Input:** Rendered scenes + voiceover + music
**Output:** MP4 video + upload to YouTube
**Hermes skills:** `publish-video-fablecut`

**Status:** ✅ Active. Fablecut handles final compilation and YouTube upload.

---

## Factory 4: Analytics — Detailed Spec

### 4a. YOUTUBE ANALYTICS — Performance Tracking

**Input:** YouTube video performance data
**Output:** Metrics on retention, CTR, breakout probability
**Hermes skill:** Connected to `pipelines/youniverse/` + `scripts/engines/`

**Pipeline:**
```
Published video → YouTube API → Performance metrics → Compare against predictions → Update hypothesis evidence
```

**Current Research:** YouNiverse (136k channels, 72.9M videos), breakout methodology, headline scoring (52.54% accuracy v0).

**Status:** ⚠️ Partial. Research pipelines exist but not integrated into a closed feedback loop with production.

### 4b. TRUTH MAP OPS — Evidence Integration

**Input:** Factory outputs + research results
**Output:** Updated truth map
**Process:**
```
Paper published → Extract claims → Map to truth map questions → Update evidence weights → Recompute confidence
Video published → Engagement data → Does popularity correlate with truth? → Update
Experiment run → Results → Update evidence
```

**Status:** ❌ Not implemented.

### 4c. FARM INTELLIGENCE — Market Analysis

**Input:** YouTube search + channel data
**Output:** Opportunity scores, gap analysis, topic recommendations
**Hermes skills:** `daily-research`, `market-scan`

**Pipeline:**
```
YouTube API → Gap analysis → Opportunity scoring → Topic queue → Farm production
```

**Formula:**
```
opportunity = 0.30 * gap_score + 0.25 * language_lag + 0.20 * breakout_rate + 0.15 * google_trends_demand + 0.10 * pageview_velocity
```

**Status:** ⚠️ Partial. Research pipeline designed. Farm template exists but never deployed.

---

## Cloudflare Infrastructure

### Current Deployment

| Service | Purpose | Status |
|---------|---------|--------|
| Factory Worker | Video pipeline state machine | ✅ Deployed |
| Factory D1 | Job state + render tracking | ✅ Deployed |
| Factory MCP Server | Model Context Protocol tools | ✅ Deployed |
| Proxy Worker | LLM API proxying | ✅ Deployed |
| YouTube Proxy | YouTube API with caching | ✅ Deployed |
| R2 (factory-assets) | Video assets storage | ✅ Deployed |
| R2 (research-datasets) | Research data storage | ✅ Deployed |
| R2 (sourcematerial) | Source material backup | ✅ Deployed |
| AI Gateway | LLM caching + routing | ✅ Configured |
| Workflows | Durable video pipeline | ⚠️ Designed, not used |

### Farm Template (Undeplyed)

| Service | Purpose |
|---------|---------|
| Farm D1 | Research data + hypothesis tracking |
| Farm R2 | Asset storage |
| Farm Queue | Pipeline decoupling |
| Farm Cron | Daily/weekly/monthly research |
| Farm Worker | Research orchestration |

### Planned Infrastructure

| Service | Purpose | Priority |
|---------|---------|----------|
| Truth Map D1 | Source metaphysics database | HIGH |
| Hypothesis Queue | Question generation pipeline | HIGH |
| Analytics Worker | Performance data processing | MEDIUM |
| EO Registry D1 | Essay Object index | HIGH |
| Hermes Worker | Agent task queue | MEDIUM |

### Cloudflare AI Models Integration

Cloudflare Workers AI provides access to multiple models that can be integrated:

| Model | Use Case | Factory |
|-------|----------|---------|
| `@cf/meta/llama-3.1-8b-instruct` | Lightweight RO extraction | Research |
| `@cf/mistral/mistral-7b-instruct` | Hypothesis generation | Research |
| `@hf/nousresearch/hermes-2-pro-mistral-7b` | Essay drafting | Writing |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | Thumbnail generation | Video |
| `@cf/bytedance/stable-diffusion-xl-lightning` | Fast thumbnails | Video |
| `@cf/meta/m2m100-1.2b` | Translation for multilingual | Research |

These can replace or augment Hermes calls for specific sub-tasks, reducing latency and cost.

---

## Hermes Coordination

### Skill Map

| Skill | Status | Factory | Purpose |
|-------|--------|---------|---------|
| `acquire` | ✅ | 1a | Paper/dataset download |
| `search` | ✅ | 1 | Research mapping |
| `explore` | ✅ | 1 | Knowledge graph browse |
| `navigate` | ✅ | 1 | Show connections |
| `curate` | ✅ | 1b | RO management (manual) |
| `synth` | ✅ | 1c | Answer from internal docs |
| `publish` | ✅ | 2 | Paper publishing |
| `write` | ✅ | 2 | Academic writing |
| `source-to-essay` | ✅ | 2b | Blog essay pipeline |
| `platinum-designer` | ✅ | 3a | Gold/storyboard design |
| `platinum-renderer` | ✅ | 3b | PIL rendering |
| `factory-pipeline` | ✅ | 3 | 5-stage production pipeline |
| `publish-video-fablecut` | ✅ | 3d | FableCut compilation |
| `daily-research` | ✅ | 4c | YouTube niche monitoring |
| `market-scan` | ✅ | 4c | Gap analysis |
| `deep-analysis` | ✅ | 4 | Data analysis |

### Skills Needed

| Skill | Priority | Factory | Purpose |
|-------|----------|---------|---------|
| `research-object-creator` | HIGH | 1b | Automate RO creation from Works |
| `essay-object-creator` | HIGH | 1c | Combine ROs into EOs |
| `hypothesis-engine` | HIGH | 1d | Perpetual question generation |
| `source-metaphysics` | MEDIUM | 1f | Truth map maintenance |
| `dataset-acquire` | MEDIUM | 1a | OpenNeuro S3 dataset downloads |

### Invocation Examples

```bash
# Research cycle
hermes -z "Create an RO from work:biernacki-matter-of-wonder" --skills research-object-creator,curate -m "deepseek-v4-flash"

# Hypothesis scan
hermes -z "Run hypothesis engine. Check all underdetermined questions and propose new EOs." --skills hypothesis-engine -m "deepseek-v4-flash"

# Full video production
hermes -z "Take EO eo:iccha-jnana-kriya and run through platinum pipeline to final render." --skills platinum-designer,platinum-renderer,factory-pipeline -m "deepseek-v4-flash"

# Truth map update
hermes -z "Update truth map with results from latest factory outputs." --skills source-metaphysics -m "deepseek-v4-flash"

# Full system sync
hermes -z "Run daily research cycle: scan truth map, propose new EOs, check for stale questions, update all metrics." --skills hypothesis-engine,source-metaphysics -m "deepseek-v4-flash"
```

---

## Process Workflows

### Daily Research Cycle

```
[CRON] 06:00 — Hypothesis engine scan
  → Check all underdetermined questions
  → Rank by depth/freshness/priority
  → Generate top 3 EO proposals

[CRON] 07:00 — Dataset check (weekly)
  → Check OpenNeuro for new meditation/consciousness datasets
  → Check Zenodo/OSF for new preprints
  → Update dataset inventory

[AGENT] 08:00 — Review EO proposals
  → Approve/reject/modify proposals
  → Assign priorities to factories
```

### Weekly Production Cycle

```
[MON] Research Factory:
  → Create/update ROs from approved EOs
  → Run Sanskrit analysis if Trika-related
  → Update source metaphysics

[TUE] Writing Factory:
  → Take highest-priority EO
  → Run V7 algorithm → produce paper/essay
  → Peer review → revise → publish

[WED-THU] Video Factory:
  → Take EO → platinum pipeline
  → Gold study → storyboard → render
  → QC → FableCut → upload

[FRI] Analytics Factory:
  → Collect performance data
  → Update truth map evidence
  → Generate new hypothesis proposals
  → Staleness check on truth map
```

### Closed-Loop Learning

```
Video publishes → YouTube analytics → Performance data
    ↓                                              ↓
Truth map updated (engagement ≠ truth, but         Hypothesis engine:
indicates audience interest in question)            "Why did this perform well?"
    ↓                                              ↓
New hypothesis: "This framing resonates"         New EO proposed
    ↓                                              ↓
Next video tests hypothesis                       Cycle continues
```

---

## Source Metaphysics — Initial Question Catalog

Based on RESEARCH_DIRECTIVE.md, ideas1.md, and the 100sources list. All 72 priority questions need to be formalized as truth map entries. Initial categories:

### Manifestation & Agency (8 questions)
Q1: Is icchā-jñāna-kriyā necessary or anthropomorphic?
Q2: Does manifestation explain Śakti or vice versa?
Q3: Does svātantrya explain manifestation or rename absence of constraint?
Q4–8: Further questions on manifestation, causation, possibility.

### Consciousness & Manifestness (8 questions)
Q9–16: Prakāśa, vimarśa, self-luminosity, minimal phenomenal experience.

### Brain & Embodiment (8 questions)
Q17–24: Brain under idealism, kañcukas as cognitive constraints, interoception.

### Individuation (8 questions)
Q25–32: Subject boundaries, Markov blankets, dissociation, decombination problem.

### Perception & World Appearance (8 questions)
Q33–40: Predictive processing vs idealism, ābhāsa, simulation theory.

### Time & Recognition (8 questions)
Q41–48: Recognition, nondual awareness, insight vs destabilization.

### Hard Problem & Metaphysics (8 questions)
Q49–56: Hard problem, Russellian monism, panpsychism, falsifiability.

### Plato & Plotinus (8 questions)
Q57–64: Goodness, overflow, necessity vs freedom, unity vs plurality.

### AI & Artificial Worlds (8 questions)
Q65–72: AI consciousness, artificial recognition, self-model collapse.

Total: 72 questions. All start as `unasked` or `underdetermined`.

---

## Versioning Strategy

```
v1.0 Source Text (immutable, git LFS for PDFs)
  → v1.0 Work JSON (linked to source)
    → v1.0 Research Object (linked to Works)
      → v1.0 Essay Object (linked to ROs)
        → v1.0 Product (paper/video/experiment)
          → updates Source Metaphysics (versioned)
```

Each layer stores its parent commit hash. Changes propagate:
- Source text updated → Work version bump → RO version bump → EO reviewed
- New RO added → EO can optionally incorporate
- Truth map updates are independent — don't force cascading version bumps

---

## Todo Tracking

### HIGH PRIORITY — Core Infrastructure

- [ ] Create `research-object-creator` Hermes skill
- [ ] Create `essay-object-creator` Hermes skill
- [ ] Create `hypothesis-engine` Hermes skill
- [ ] Create `source-metaphysics` Hermes skill
- [ ] Formalize 72 priority questions as truth map entries
- [ ] Deploy farm-template for "tantra" farm
- [ ] Create EO directory (`content/essay-objects/`)
- [ ] Create truth map directory (`content/source-metaphysics/`)

### MEDIUM PRIORITY — Factory Improvement

- [ ] Automate RO creation from Works (batch upgrade 110 ROs)
- [ ] Connect analytics feedback loop to truth map
- [ ] Dashboard: connect to all backend services
- [ ] Sanskritree: integrate Sanskrit analysis into RO pipeline
- [ ] Visionary renderer: productionize Skia backend
- [ ] Farm template: implement YouTube API client (replace stubs)

### LOW PRIORITY — Nice to Have

- [ ] Geometric engine: explore integration as pedagogical pathway generator for EOs
- [ ] Cloudflare AI models: benchmark vs Hermes for sub-tasks
- [ ] Dataset acquire skill: formalize OpenNeuro S3 download pattern
- [ ] Multi-farm deployment (expand beyond tantra)
- [ ] Automated truth map staleness check cron

### DONE — Already Working

- [x] Paper acquisition pipeline (acquire skill)
- [x] Platinum video pipeline (13 stages)
- [x] Next.js web app (27 routes)
- [x] MCP server for factory tools
- [x] Visual library (scene packs)
- [x] Sanskritree (98.8% accuracy)
- [x] Essaygen V7 algorithm
- [x] Research data pipelines (YouNiverse, etc.)
- [x] Source material curation (trika, platonic, sufi)
- [x] OpenNeuro S3 dataset access confirmed
- [x] Scholar paper collections
