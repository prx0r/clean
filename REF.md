# Clean — Project Reference

Research nucleus for the Trika–Consciousness-Science content pipeline. Everything an agent needs to understand the project, its modules, and where to start.

---

## Root Files

| File | Purpose |
|------|---------|
| `ONBOARDING.md` | **Read this first.** Entry point for any new agent. Lists 12 files to read in order to get full context. |
| `RESEARCH_DIRECTIVE.md` | Master agent prompt. Read after ONBOARDING. Defines the research programme, methodology, 72 priority questions, source strategy, essay output structure, quality controls. |
| `GRANULAR-SPEC.md` | Next directive: every component needs a full spec before wiring. Priority order for specs. |
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

---

## hxrmxs/ — Extracted Repository Reference

| File | Purpose |
|------|---------|
| `README.md` | Organized into patterns (15), source materials (20), archived (not useful) |
| `patterns/research-arm.md` | Shadow Model + ThinkTank with Critic agent — hypothesis engine design |
| `patterns/ouroboros.md` | Three-loop architecture (Live/Strategic/Dreaming), Truthcore schema |
| `patterns/vr-proxy.md` | VR proxy mapping for web → VR interaction design |
| `patterns/tpe-data-model.md` | Triangulated Psychological Event — user behavior tracking for feed algorithms |
| `patterns/translation-layer.md` | Archetype discovery for text → audio-visual generation |
| `patterns/monolith-pipeline.md` | 14-phase paper-to-video narrative pipeline |
| `patterns/crp-dual-mode.md` | Dual-mode architecture, journey mechanics, paper classification schema |
| `patterns/stv-music-framework.md` | Symmetry-Valence Theory + geometric music + EEG validation |
| `patterns/mechanisms.md` | Teaching mechanisms per student state |
| `patterns/registers.md` | Register taxonomy for teaching persona |
| `patterns/amupn-profiles.md` | Heterogeneous graph user profiles |
| `patterns/hellokoa-patterns.md` | Golden standard refinement, Super-Graph dual-retrieval |
| `source-materials/` | 20 cross-tradition bridge files ready to become ROs |
| `archived/` | 50+ files (raw chat logs, personal notes, off-topic) |

**Key transfers to our stack:** Ouroboros Dreaming Loop, Critic agent at 4 gates, TPE data model for feed algorithm, VR proxy design principle, Monolith short-form video template.

---

## External Repos (Referenced, Not Cloned)

| Repo | Purpose |
|------|---------|
| `github.com/prx0r/meditate` | Breath + meditation web app prototype. Single-file HTML/JS with breathing visualizer (multi-ring), meditation timer, audio cues, technique library. The embodied practice pipeline precedent — TOs could feed guided meditations into this UI. |
| `github.com/prx0r/geometricengine` | HXRMXS UNO Engine — graph-native pedagogical policy engine. Trained from UNO therapy transcripts. No LLM in the cognition path. The pattern for the Satsang feed algorithm and the user-facing agent. |

## Agent Quickstart

1. **Read `ONBOARDING.md`** — entry point for new agents (recommended reading order)
2. **Read `RESEARCH_DIRECTIVE.md`** — understand the research programme
3. **Read `GRANULAR-SPEC.md`** — understand the current directive
4. **Check `magnum-opus/10-FULL-SPEC.md`** for the complete architecture
5. **Consult `magnum-opus/13-FLAWS.md`** before making architectural decisions
6. **Browse `specs/`** for granular component specs (being built now)
7. **Use `researchsources/100sources.md`** for paper discovery
8. **Access datasets via** `neurodatasets/S3-ACCESS.md`
9. **Find downloaded papers in** `resources/by-scholar/`
10. **Reference the blog codebase** via `magnum-opus/11-BLOGREF.md`

---

## specs/ — Granular Component Specs

| File | Purpose |
|------|---------|
| `RO.md` | Research Object spec — versioned, living knowledge unit. The core. |
| *(More coming — see GRANULAR-SPEC.md for priority order)* |

## Root Files (New)

| File | Purpose |
|------|---------|
| `ONBOARDING.md` | **Entry point.** Read this first as a new agent. |
| `GRANULAR-SPEC.md` | Current directive: spec every component before wiring. |
| `FORCODEX.md` | Setup guide for ChatGPT Codex — MCP servers, Cloudflare access, model strategy |
| `formalsystemnotes.md` | 7 meta-claims (M.1-M.7) with falsifiers. Epistemological foundation. |
| `formalsystemnotes-raw.md` | Raw synthesis: reality is relation, no foundations, hard problems as framing errors |
| `formalsystemnotes2.md` | Concept ontology schema: Framework + Concept entities, 12 categories, mandatory `is_not` |
| `tractatus-conscientiae.md` | Level 0 meta-structure: S ⇒ (0 ↔ 1). Six interpretation branches (B1-B6). |
| `AM0-framework.md` | S/{0,1}/i ontology mapped onto AM0 constructor theory. Truth map by 6 branches. |
| `rasa-institute.md` | Academic press for Indian philosophy & consciousness science |
| `truthengine.md` | Truth engine math: Deutsch vs Bayes, confidence scoring, falsifiers |
| `truthengine-propagation.py` | Propagation engine: Bayesian log-odds updating, paradigm discounting |
| `truthengine-db.py`, `-schema.sql`, `-migrate.py` | Database layer, schema, migration |
| `truthengine-test-validation.py`, `-v2.py` | Validation tests for the propagation engine |
| `truthengine-integration-spec.md` | Cross-stream integration spec: TCEE ⟷ Evidence Fabric |

---

## machinedreams/ — Convergence & Experiments

| File | Purpose |
|------|---------|
| `machinedreams.md` | Core vision: truth map → organism specs → built wetware. Three-stage convergence from understanding to specifying to building. |
| `machinedreams-experimental.md` | Complete experimental stack: $55 slime mould EEG rig, Tier 1-4 equipment progression, PiEEG integration, LH-LLM building requirements, biohacker space alternatives. |

## External References

| Resource | Purpose | Cost |
|----------|---------|------|
| PiEEG (pieeg.com) | Low-cost 8-16ch EEG for human meditation experiments. Research-grade 24-bit ADCs, open-source Python server. | ~$150-300 |
| Slime mould culture | Physarum polycephalum, grows on agar + oat flakes. Aneural cognition model. | ~$20 |
| Evo-2 (Arc Institute) | DNA foundation model for generating biologically viable sequences. | Free / API |
| Adamatzky lab (UWE Bristol) | Leading fungal electrical signaling research. Open datasets. | Contact for raw data |

## tractatus/ — Philosophical Framework

| File | Purpose |
|------|---------|
| `tractatus-conscientiae.md` | Level 0 meta-structure: S ⇒ (0 ↔ 1), six interpretation branches (B1-B6) |
| `tractatus-song-with-no-singer.md` | Human-facing myth of dependent origination, memory and recognition |
| `tractatus-observer-theorem.md` | Formal theorem of contextual distinction, emergent observation, recursive self-inclusion |
| `tractatus-nanavira-abhinavagupta.md` | Comparative analysis of reflexivity — Ñāṇavīra vs Abhinavagupta on vimarśa, prakāśa, svātantrya |
