# START HERE — Project Context & Exploration Log

This document captures the complete state of the codebase as of the July 28, 2026 deep-dive session. Everything we explored, every file location, all findings. Read this to get from zero to productive.

---

## 0. SESSION LOG — How This Context Was Built

This section recounts the actual exploration path so you understand how we arrived at each finding.

### Phase 1: Top-Down Orientation
User started with `cd root/projects/clean`, then asked to read `magnum opus and handover and reference docs`. We read:
- `magnum-opus/README.md` + directory listing (31 files)
- `TRUTHREF.md` — current truth map state
- `TRUTHMAP-HANDOFF.md` (634 lines) — engine state
- `HERMES-TRUTHMAP-HANDOFF.md` (725 lines) — two-loop system
- `docs/active/HANDOVER-SESSION-2026-07-26.md` (179 lines) — session handover
- `resources/docs/SESSION-HANDOVER-2026-07-26.md` (99 lines) — composition handover
- `HANDOVER-GLSL.md` (72 lines) — GLSL pipeline

### Phase 2: Deep Dive — All Video Engines
User then said `deepdive all files and get to know them intimately especially the video engines, all the skia stuff we have been refining`. We launched parallel explorations reading:
- All `beautify/` packs, `beautify-archive/lib/` GLSL libraries, `render_harness.py`, scene mappings
- `queue/`, `queue2/`, `queue3/`, `queue4/` — 79 total PIL packs
- `MOTHERFUCKER/README.md`, `HANDOVER.md`, `FRAMEWORK-ARCHITECTURE.md`, `VISUAL_ENGINE_PHASES.md`, `VISUAL_CODING_LANGUAGE.md`, `AGENT-GUIDE.md`, `FUTUREENGINE.md`, `FRAMEWORK-READINESS.md`, `BUILD-REVIEW.md`, `devnext.md`
- `MOTHERFUCKER/renderer.mjs`, `motifs.mjs`, `math.mjs`, `primitives.mjs`, `semantic-visuals.mjs`, `composition.mjs`, `theme.mjs`, `fonts.mjs`, `cli.mjs`, `schema.mjs`, `visual-semantics.mjs`, `visual-auditor.mjs`, `visual-assets.mjs`, `analysis.mjs`, `essay-program.mjs`, `program-builder.mjs`, `systems-visuals.mjs`, `visual-auditor.mjs`
- All `src/` extension modules (geometry/ 7 files, particles/ 5, materials/ 3, audio/ 2, capabilities/ 1, top-level 8)
- `FATHERFUCKER/README.md`, `skia-capabilities.md`, `6d-vector-engine/` (composition.json, engine.py, TRANSMISSION-1 through 5)
- `scene-pack.schema.json`, `packs/hrdaya-original.json`, `packs/logicvid-04.json`
- `infinite_learned_film_pack/ESSAY_TO_VISUAL_WORKFLOW.md` and `PRODUCTION_BLUEPRINT.md`
- `package.json` at root and in MOTHERFUCKER/

### Phase 3: Exhaustive MOTHERFUCKER Audit
User asked to `explore all of motherfucker folder and all files in it and report back`. We delegated a comprehensive agent task that recursively listed and read every file in MOTHERFUCKER/ including all subdirectories: capability-packs/ (18 packs), style-packs/ (6 files), extensionpacks/ (12 files with broken stubs), agent-guide/ (25+ files), tools/ (9), tests/ (7), programs/ (5), infinite_learned_film_pack/ (7 files), song-no-singer-delivery/ (output + framework copy), build/ (14 subdirs). This discovered the **critical import stub bug** in extensionpacks/.

### Phase 4: Hermes Agent Check
User asked: `check out hermes agent and related files test if u can speak to it`. We found Hermes v0.18.2 installed, read its config (`~/.hermes/config.yaml`), listed all 102 skills, tested `hermes -z "Respond with OK"` which returned OK, read key skill files (`tantraloka-film`, `truthmap-research`, `truthmap-enquiry`, `factory-pipeline`, `publish-video-fablecut`, etc.), and discovered that no dedicated logicvid skill was created.

### Phase 5: Logicvid Discovery
User remembered logicvids. We found 8 logicvid packs in `MOTHERFUCKER/packs/`, the `argument-diagram` motif (423 lines, 10 move types) and `logical-argument` motif (278 lines), the reusable pattern in `process-notes-skills.md`, and confirmed they target the Ochema channel with no separate Hermes skill.

### Phase 6: This Document
User asked to create STARTHERE.md recounting the entire process.

---

## 1. INITIAL CONTEXT — The Clean Project

**Root:** `/root/projects/clean/`

This is the unified content factory — a closed-loop epistemology engine with 4 factories (Research, Writing, Video, Analytics). Contains:

- **Truth Map** — refutation-led evidence provenance system (Popper/Deutsch)
- **Skia Video Framework** — deterministic motion-graphics pipeline (`MOTHERFUCKER/`)
- **PIL/GLSL Legacy Pipeline** — beautify pipeline with 79 queue packs
- **Hermes Agent** — orchestrator agent with 102 skills

### Key Top-Level Docs Read

| File | What It Is |
|------|-----------|
| `magnum-opus/README.md` | Architectural blueprint overview (4 factories, truth map, Hermes) |
| `magnum-opus/01-VISION.md` | Unified vision — produce understanding, not content |
| `magnum-opus/02-AUDIT-SUMMARY.md` | Asset inventory: 1917 works, 153 ROs, 1796 essays |
| `magnum-opus/06-FACTORY-ARCHITECTURE.md` | Four factory specs |
| `magnum-opus/09-HERMES-ORCHESTRATION.md` | Hermes as orchestrator, skill map |
| `magnum-opus/10-FULL-SPEC.md` | Full system spec — every module, sub-unit, data flow |
| `magnum-opus/13-FLAWS.md` | Known risks |
| `magnum-opus/21-ANAKHYA.md` | Anakhya channel identity |
| `magnum-opus/22-TANTRAFILES.md` | Tantrafiles channel + beat-map pipeline |
| `magnum-opus/23-OCHEMA.md` | Ochema channel identity (logicvids) |
| `magnum-opus/24-INTELLIGENT-OTHERS.md` | Intelligent Others pack + science viz |
| `magnum-opus/25-SHORTS-PIPELINE.md` | Shorts format, 2-skill system |
| `TRUTHREF.md` | Current truth map state (69 lines) |
| `TRUTHMAP-HANDOFF.md` | 634-line truth map engine handoff |
| `HERMES-TRUTHMAP-HANDOFF.md` | 725-line two-loop system handoff |
| `HANDOVER-GLSL.md` | GLSL pipeline handoff (17 untested shaders) |
| `docs/active/HANDOVER-SESSION-2026-07-26.md` | Session handover with architecture decisions |
| `resources/docs/SESSION-HANDOVER-2026-07-26.md` | Composition/video session handover |
| `HERMES-SKILLS.md` | Complete Hermes skill reference |
| `HERMES-AUTOLOOP.md` | Autonomous loop playbook |
| `HERMESTRUTHMAP.md` | Running audit log for Hermes truth map loops |

---

## 2. TANTRALOKA SKIA FRAMEWORK — MOTHERFUCKER/

**Location:** `/root/projects/clean/MOTHERFUCKER/`

The primary production renderer. Deterministic motion-graphics pipeline built on `@napi-rs/canvas` (Skia native bindings for Node.js). Streams raw RGBA frames into ffmpeg H.264.

### Kernel (16 core .mjs modules)

| File | LOC | Status | What It Does |
|------|-----|--------|-------------|
| `cli.mjs` | 269 | WORKING | CLI: render, poster, contact, validate, compile-essay, render-essay, motifs, fonts, audit |
| `renderer.mjs` | 284 | WORKING | FrameRenderer + ffmpeg pipe + crossfades + audio manifest loading |
| `motifs.mjs` | 552 | WORKING | 9 motif renderers in registry: composition, heart-lattice, attention-lens, phoneme-forge, reflexive-mirror, return-current, closing-heart-seal, semantic-essay, logical-argument + dispatcher to argument-diagram |
| `semantic-visuals.mjs` | 776 | WORKING | 15 philosophical mechanisms (constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist) + dynamic registration API |
| `systems-visuals.mjs` | 807 | WORKING | 16 system-level visual renderers (pattern-ensemble, dependency-network, umwelt-windows, multiscale-agent, boundary-gates, memory-relay, morphing-invariant, reciprocal-reeds, causal-vortex, cooling-chain, dialectic-bridge, tuning-network, source-compile-runtime, recursive-observer, open-question, relational-birth) |
| `primitives.mjs` | 447 | WORKING | 20+ drawing primitives: drawGlowOrb, drawRing, drawLotus, drawLabel, drawNode, drawArrowHead, drawRadialWords, drawSilhouette, drawGlowingPath, drawEllipseRing, drawOrbitingNodes, drawPartialPath, drawRosette, drawBorder, drawFooter, drawBar, pointAlong, logicalScale, clearWithBackground, createStableBackground |
| `composition.mjs` | 264 | WORKING | Declarative layer engine: 12 layer types (orb, ring, ellipse, lotus, label, silhouette, polygon, path, bezier, orbit-nodes, radial-words, grid) |
| `visual-semantics.mjs` | 191 | WORKING | 21 relation types, 16 semantic roles v2, 14 visual operators v2, 6 continuity actions, 13 encoding channels, mechanism-relation registry |
| `visual-auditor.mjs` | 241 | WORKING | Visual correspondence auditing: semantic roles, operators, relations, continuity lifecycles, candidate scoring, diversity metrics, max-2 enforcement |
| `essay-program.mjs` | 312 | WORKING | Essay-to-film compilation pipeline: extractEssayUnits, assertEssayProgram, compileEssayProgram |
| `program-builder.mjs` | 310 | WORKING | BuildDeterministicProgram: validates relations, generates shots with candidate audits for 21 relation types |
| `analysis.mjs` | 103 | WORKING | Essay analysis validation (v1.0) |
| `schema.mjs` | 101 | WORKING | Runtime pack validation (assertPack, packDuration) |
| `math.mjs` | 137 | WORKING | Deterministic math: TAU, lerp, smoothstep, easeInOutCubic, bell, wave, pulse, stagger, hashString, seededRandom, colorToRgb, rgba, mixColor, cubicPoint, sampleCubic, partialPoints, polar, regularPolygon |
| `theme.mjs` | 109 | WORKING | 3 themes (ivoryManuscript, whiteScientific, midnightVellum), LOGICAL_WIDTH=1280, LOGICAL_HEIGHT=720, registerTheme, getTheme |
| `fonts.mjs` | 90 | WORKING | Font registration: EB Garamond, Noto Serif Devanagari, Source Serif 4, KaTeX (11 font files); applyTextStyle, fitText, fontStatus |
| `visual-assets.mjs` | 83 | WORKING | Visual asset registration and overlay rendering with blend modes |
| `index.mjs` | 57 | WORKING | Public API barrel export |
| `schema.mjs` | 101 | WORKING | Runtime pack validation |

### Extensions (21 files in src/)

**Geometry Engine** (`src/geometry/` — 7 files, ALL UNTESTED):
- `path-utils.mjs` (85 LOC) — point, distance, centroid, resamplePolyline, morphPointSets
- `path-ops.mjs` (53 LOC) — Boolean path ops (union, intersect, difference, XOR) — depends on @napi-rs/canvas exposing PathOp
- `symmetry.mjs` (15 LOC) — radialCopies, dihedralCopies
- `lotus-generators.mjs` (49 LOC) — petalPoints, lotusRing, nestedLotus
- `mandala-generators.mjs` (31 LOC) — ringPath, spokePath, mandalaLayers
- `yantra-generators.mjs` (55 LOC) — regularPolygonPoints, trianglePair, sriYantraApprox
- `flame-generators.mjs` (32 LOC) — flameTonguePoints, flameAureole

**Particle Engine** (`src/particles/` — 5 files, WORKING):
- `particle-system.mjs` (50 LOC) — ParticleSystem class: deterministic ECS with emitter, field, constraint, renderer
- `emitters.mjs` (42 LOC) — pointEmitter, ringEmitter, pathEmitter
- `fields.mjs` (44 LOC) — combineFields, radialField, orbitalField, noiseField, pathFollowField
- `constraints.mjs` (22 LOC) — boundsConstraint, pathAttractorConstraint
- `renderers.mjs` (33 LOC) — orbRenderer, trailRenderer, compositeParticleRenderer

**Materials System** (`src/materials/` — 3 files):
- `color.mjs` (32 LOC) — hexToRgb, rgbToOklab, oklabToRgb, interpolateOklab (WORKING)
- `layer-stack.mjs` (34 LOC) — LayerStack: offscreen compositing with blend modes (UNTESTED)
- `materials.mjs` (39 LOC) — conicGradient, radialGlow, paletteRamp, 6 materialProfiles (UNTESTED)

**Audio Bus** (`src/audio/` — 2 files, WORKING):
- `audio-features.mjs` (50 LOC) — loadAudioFeatureManifest, sampleAudioFeatures, EnvelopeFollower
- `audio-router.mjs` (28 LOC) — AudioRouter: routes features to visual parameters

**Top-Level Extension Modules** (8 files):
- `argument-diagram.mjs` (423 LOC, WORKING) — 10 move types: claim, subclaim, refutation, branch, converge, divider, premises, side-by-side, dialogue, concept-map. Uses clean white canvas, Source Serif 4, status colors. Supports bold `**text**` and math `*text*` markup, drift animation, statusTransition.
- `argument-display.mjs` (278 LOC, UNTESTED) — Academic argument display: section headers, body, boxed-equation, proof, table, citation, divider with theme system
- `invariant-math.mjs` (220 LOC, WORKING) — expAlpha, expApproach, centroid, signatureDistance, normalizedSimilarity, hermiteScalar, sampleTrajectory, causalTraceSeries
- `invariant-geometry.mjs` (142 LOC, WORKING) — lobedContour, relationalNecklace, carrierGeometry (vessel, lattice, ribbon, wave, branch), topologyThread, transformedSeed
- `invariant-visuals.mjs` (1044 LOC, UNTESTED) — 12 invariant mechanism renderers + 12 asset implementations: continuity-seed, relational-signature, transformation-orbit, carrier-shell, causal-trace, morphing-field, reciprocal-exchange, dialectic-bridge, constraint-tournament, inheritance-graph, encoding-channel, source-sink
- `anatomy-visuals.mjs` (900 LOC, WORKING) — 16 assets (human-standing, body-landmarks, etc.) + 16 mechanisms (embodied-awareness-field, body-scan, meditation-settling, breath-cycle, breath-attention-coupling, nervous-signal-propagation, interoceptive-map, body-world-interface, heart-breath-entrainment, chakra-axis, nadi-flow, kundalini-ascent, subtle-circulation, physical-subtle-compare, dvadasanta-ascent, prana-apana-balance)
- `anatomy-geometry.mjs` (117 LOC, WORKING) — 27 anatomy landmarks, 7 chakra landmarks, 12 dvadasanta stations, bodyFrame, standingBodyPath
- `neuro-visuals.mjs` (775 LOC, UNTESTED) — 8 assets (brain-schematic, neural-network, etc.) + 8 mechanisms (attention-selection, predictive-loop, pattern-completion, memory-consolidation, neural-propagation, competitive-binding, temporal-integration, error-driven-learning)
- `capabilities/pathkit-visuals.mjs` (79 LOC, UNTESTED) — 3 mechanisms (lotus-unfold, yantra-construction, mandala-entry)
- `load-capability-scene-pack.mjs` (12 LOC, WORKING) — loads packs with capability activation

### Capability Packs (18 packs in capability-packs/)

| Pack | Inherits | Mechanisms | Status |
|------|----------|-----------|--------|
| `base/` | — | 15 built-in | WORKING |
| `human-anatomy/` | base | 9 | WORKING — 16 assets, custom theme |
| `yogic-subtle-body/` | human-anatomy | 7 | WORKING — 6 assets |
| `neurocognition/` | base | 8 | UNTESTED — 8 assets, custom theme |
| `invariant-composition/` | systems-dynamics + temporal-processes + comparative-epistemology | 12 | UNTESTED — 12 assets, rich theme |
| `pathkit-geometry/` | base | 3 | UNTESTED |
| `scientific-diagrams/` | base | 0 | Empty root |
| `data-visualization/` | systems-dynamics | 0 | Empty root |
| `systems-dynamics/` | base | 0 | Empty root |
| `temporal-processes/` | base | 0 | Empty root |
| `comparative-epistemology/` | base | 0 | Empty root |
| `embodied-phenomenology/` | base | 0 | Empty root |
| `textual-scholarship/` | base | 0 | Empty root |
| `tantric-cosmology/` | base | 0 | Empty root |
| `intelligent-others/` | base | 0 | Empty root |
| `particle-fields/` | base | 0 | Empty root |
| `audio-reactive/` | base | 0 | Empty root |
| `tantric-geometry/` | pathkit-geometry + particle-fields | 0 | Empty root |

### Style Packs (6 files in style-packs/)

All are JSON stubs (8 lines each). Material profiles exist in `src/materials/materials.mjs` but are never wired into renderer.

- `mineral-manuscript.json`, `ritual-gold.json`, `luminous-subtle-body.json`, `technical-neural.json`, `visionary-midnight.json`, `ash-and-ember.json`

### Scene Packs (15 JSON files in packs/)

| Pack | Motif | Scenes | Status |
|------|-------|--------|--------|
| `hrdaya-original.json` | 6 built-in motifs | 6 | WORKING — proven render |
| `hermes-magician.json` | semantic-essay | 7 | WORKING |
| `magician-compiled.json` | semantic-essay | 14 | WORKING — 366s rendered MP4 |
| `logicvid-04.json` | argument-diagram | 7 | WORKING |
| `logicvid-04-mono.json` | argument-diagram | 7 | UNTESTED |
| `logicvid-04-dynamic.json` | argument-diagram | 4 | UNTESTED |
| `logicvid-04-typography.json` | argument-diagram | 4 | UNTESTED |
| `logicvid-demo.json` | argument-diagram | — | UNTESTED |
| `logicvid-moves-demo.json` | argument-diagram | — | UNTESTED |
| `argument-diagram-color.json` | argument-diagram | — | UNTESTED |
| `argument-diagram-demo.json` | argument-diagram | — | UNTESTED |
| `invariant-composition-demo.json` | semantic-essay | 12 | UNTESTED — requires pack |
| `anatomy-test.json` | semantic-essay | 3 | UNTESTED — requires pack |
| `neuro-test.json` | semantic-essay | 3 | UNTESTED — requires pack |
| `hermes-v6-pack.json` | semantic-essay | 10 | UNTESTED |

### Shipped Films

| Film | Location | Scenes | Runtime |
|------|----------|--------|---------|
| Infinite Learned | `infinite_learned_film_pack/` | 44 | ~11:25 |
| Song No Singer | `song-no-singer-delivery/output/` | 88 | — |
| Hermes v3 (Crowley) | `build/hermes-v3/` | 7 | — |
| Hermes v4 (Crowley) | `build/hermes-v4/` | 12 unique | — |
| Hermes v5 (Alchemy) | `build/hermes-v5/` | 12, 3 packs | — |

### Tests (7 files in tests/)

| File | Status | What It Tests |
|------|--------|-------------|
| `framework.test.mjs` (~100 LOC) | WORKING | Pack loading, IAST rejection, font shaping, deterministic rendering, video validation |
| `audio-features.test.mjs` (8 LOC) | WORKING | Feature interpolation, envelope follower, audio router |
| `particles.test.mjs` (9 LOC) | WORKING | Deterministic particle emission |
| `pathkit-geometry.test.mjs` (11 LOC) | WORKING | Lotus ring, resampling, morphing, sri yantra, signed area |
| `invariant-composition.test.mjs` (40 LOC) | WORKING | Distance signature invariance, exponential memory, hermite scalar |
| `invariant-composition.integration.test.mjs` (27 LOC) | UNTESTED | End-to-end invariant pack activation |
| `capability-packs.integration.test.mjs` (24 LOC) | UNTESTED | Base + neuro pack activation |

### Tools (9 files in tools/)

| File | Status | Purpose |
|------|--------|---------|
| `render-pack.mjs` (23 LOC) | WORKING | Renders capability scene packs |
| `build-song-analysis.mjs` (65 LOC) | WORKING | Builds essay analysis JSON |
| `analyse-audio.py` | UNTESTED | Python audio analysis |
| `probe-canvas-capabilities.mjs` | UNTESTED | Probes Skia capabilities |
| `apply-formal-framework-patch.mjs` | UNTESTED | Framework patching |
| `render-invariant-demo.mjs` | UNTESTED | Renders invariant demo |
| `build-song-program.mjs` | UNTESTED | Builds visual program |
| `export-storyboard.mjs` | UNTESTED | Exports storyboard |
| `test-anatomy-pack.mjs` | UNTESTED | Anatomy pack test |
| `test-neuro-pack.mjs` | UNTESTED | Neuro pack test |

### Agent Guide (25+ files in agent-guide/)

System maps, audio/narration docs, rendering pipeline, pack taxonomy, testing/QC, tech roadmap, templates, examples, schemas.

### Critical Bug Found

**extensionpacks/ import stubs** — `extensionpacks/semantic-visuals.mjs`, `theme.mjs`, `visual-assets.mjs`, `visual-semantics.mjs` are stub files that shadow the real root modules. `capability-packs.mjs` imports from these stubs instead of `../`. This means `registerSemanticVisual`, `registerTheme`, `registerVisualAsset` all silently fail. **No capability pack actually works at runtime.** The base 15 mechanisms work because they're built into the kernel, not loaded through the pack system.

---

## 3. LOGICVIDS — Argument-Diagram Motif

Logicvids are formal philosophy videos using the `argument-diagram` motif. They belong to the **Ochema** channel (sharp comparative metaphysics).

### Key Files

| File | What It Is |
|------|-----------|
| `src/argument-diagram.mjs` | 423 lines — renderer with 10 move types |
| `src/argument-display.mjs` | 278 lines — styled text block motif |
| `packs/logicvid-04.json` | 7 scenes: Abhinavagupta vs QFT vs Russellian monism |
| `packs/logicvid-04-mono.json` | Monochrome variant with drift animation |
| `packs/logicvid-04-dynamic.json` | Dynamic transitions variant |
| `packs/logicvid-04-typography.json` | Typography test variant |
| `packs/logicvid-demo.json` | Move type demos |
| `packs/logicvid-moves-demo.json` | Move type demos |
| `packs/argument-diagram-color.json` | Color test |
| `packs/argument-diagram-demo.json` | Argument diagram demo |
| `packs/logicvid-reality-appears/` | Subdirectory with full framework copy |
| `process-notes-skills.md` | Reusable logicvid pattern documented |

### 10 Move Types

`claim`, `subclaim`, `refutation`, `premises`, `side-by-side`, `branch`, `converge`, `divider`, `dialogue`, `concept-map`

### Status Colors

`active` (ink #1a1a1a), `refuted` (red #b33a3a), `resolved` (green #3a7a4a), `neutral` (grey #555555), `highlight` (gold). `statusTransition: true` for smooth color animation.

### Reusable Scene Pattern

```
Scene 1: The Question — claim
Scene 2: First position — premises + conclusion
Scene 3: Comparison — side-by-side or branch
Scene 4: Second position — refutation
Scene 5: Third position — converge or resolved
Scene 6: Verdict — three-way branch + final resolved claim
```

### No Dedicated Hermes Skill

Logicvids use the `argument-diagram` motif within the `tantraloka-film` skill. No separate logicvid skill was created.

---

## 4. LEGACY VIDEO PIPELINES

### PIL/Goldrender Pipeline (beautify/)

**Location:** `/root/projects/clean/beautify/` and `/root/projects/clean/beautify-archive/`

The original Python PIL-based render pipeline. Essay → Python PIL visual functions → frames.

- **25 packs in `beautify/`** — 19 per-essay pack dirs + 6 standalone .py scripts
- **5 archived batches in `beautify-archive/`** — 01 through 05 with GLSL conversions
- **Shared GLSL lib** at `beautify-archive/lib/` — 15 files: primitives.glsl, 5 style grammars, tone mapping (aces, srgb, cinema), bloom, easing
- **GLSL uniform contract:** `iResolution`, `u` (scene progress), `t` (time), `u_audioVolume`, `u_audioBeat`
- **17 GLSL shaders** exist but never GPU-tested — need Vast AI GPU box
- **Render harness** at `beautify-archive/lib/render_harness.py` — compiles and previews

### Queue Packs

| Directory | Packs | Type |
|-----------|-------|------|
| `queue/` | 19 | Platinum .py scripts |
| `queue2/` | 20 | Platinum .py scripts |
| `queue3/` | 20 | Platinum .py scripts |
| `queue4/` | 20 | Platinum .py scripts |

**Total: 79 PIL packs ready for rendering**

### ModernGL/GLSL Pipeline

**Location:** `/root/projects/tantraloka/moderngl/` (external to this repo)

- 17 GLSL fragment shaders at `moderngl/shaders/`
- Render harness at `moderngl/render_harness.py`
- Needs GPU box (Vast AI, ~$0.20-0.40/hr)
- CPU software rendering: ~100s/frame at 320×180
- Blocked on expired Cloudflare token for studio deploy

### FableCut Compilation Pipeline

- Running at `fablecut.tantrafiles.xyz` via Cloudflare tunnel → localhost:7777
- Composition dashboard with instrument selector (fluidsynth), narration preview
- Glass pipeline: essay → storyboard → render (PIL/Skia) → compile (FableCut) → upload (YouTube)
- MCP server: `/root/projects/FableCut/mcp-server.js`

---

## 5. HERMES AGENT

**Version:** v0.18.2
**Location:** `/usr/local/bin/hermes`
**Config:** `~/.hermes/config.yaml`
**Auth:** `~/.hermes/auth.json`, `~/.hermes/.env`
**Provider:** opencode-go (deepseek-v4-flash) via `https://opencode.ai/zen/go/v1`

### All 102 Skills

Skills in `~/.hermes/skills/` (41 directories) + external in `/root/projects/blog/hermes/skills/`.

**Key video/film skills:**

| Skill | Location | What It Does |
|-------|----------|-------------|
| `tantraloka-film` | `~/.hermes/skills/tantraloka-film/` | Skia deterministic essay films — 12-step protocol: argument IR → continuity → pack selection → mechanism candidates → render |
| `factory-pipeline` | `~/.hermes/skills/factory-pipeline/` | Legacy 5-stage pipeline: source → Work → RO → Essay → Storyboard → Video |
| `platinum-designer` | `/root/projects/blog/hermes/skills/platinum-designer/` | PASS 1: storyboard design (PIL era) |
| `platinum-renderer` | `/root/projects/blog/hermes/skills/platinum-renderer/` | PASS 2: PIL code + render (PIL era) |
| `publish-video-fablecut` | both dirs | FableCut: storyboard → TTS → art → timeline → export |
| `manim-video` | `~/.hermes/skills/manim-video/` | Manim math explainer videos |
| `comfyui` | `~/.hermes/skills/comfyui/` | ComfyUI image/video/audio generation |
| `touchdesigner-mcp` | `~/.hermes/skills/touchdesigner-mcp/` | TouchDesigner visual programming |

**Key research skills:**

| Skill | Location | What It Does |
|-------|----------|-------------|
| `truthmap-research` | `~/.hermes/skills/research/truthmap-research/` | Truth Map research loops: contentions → gate → ingest → benchmark → report |
| `truthmap-enquiry` | `~/.hermes/skills/research/truthmap-enquiry/` | Self-contained probe cycle: contention spec → pipeline → auto-EO → 6-blank signal |
| `acquire` | `~/.hermes/skills/acquire/` | Paper acquisition: DOI → Crossref/OpenAlex → OA download → validate |
| `explore` | `~/.hermes/skills/explore/` | Cross-silo search: ROs, works, essays, concepts + gap surfacing |
| `synth` | `~/.hermes/skills/synth/` | Answer synthesis from internal library with citations and gap flags |
| `curate` | `~/.hermes/skills/curate/` | RO management: coverage, gaps, suggestions |
| `navigate` | `~/.hermes/skills/navigate/` | Knowledge graph browser |
| `arxiv` | blog project | arXiv paper search |
| `pubmed-central` | blog project | PubMed paper search |

### MCP Servers Connected

- `cloudflare-docs` — Cloudflare API access
- `fablecut` — via `node /root/projects/FableCut/mcp-server.js`
- `platinum-factory` — via `/root/projects/blog/factory/cloudflare/src/mcp-server.py`

### How the Loop Works (from HERMES-AUTOLOOP.md)

1. **Codex decides** what to investigate, writes claim packet + source map JSON
2. **Codex launches Hermes:** `hermes -z "Mission: ..." --skills truthmap-research -m deepseek-v4-flash --yolo`
3. **Hermes drives** existing tools: gate → ingest → state-of-play → benchmark → report
4. **Codex reviews** Hermes report, fixes road bugs, writes next packet
5. **Log** in HERMESTRUTHMAP.md

### Loops Run So Far

Loop 001-010 completed (documented in HERMESTRUTHMAP.md). Q17 brain-dependence question has NCC + lesion evidence layers. 61 tests passing, 3 contention benchmarks.

---

## 6. CRITICAL STATE SUMMARY

### What Works (Proven)

- Kernel: all 16 modules compile, deterministic rendering pipeline works
- 2 films shipped (Infinite Learned 44 scenes, Song No Singer 88 scenes)
- hrdaya-original (690 frames) and magician-compiled (14 scenes, 366s) rendered
- CLI: render, poster, contact, validate, compile-essay, audit all functional
- 5 of 7 test files pass
- Font shaping: EB Garamond, Noto Serif Devanagari, Source Serif 4, KaTeX
- 3 themes render consistently
- Seeded PRNG gives bit-identical output
- Node modules installed (@napi-rs/canvas 1.0.2, katex, fonts)
- Hermes agent responds and is configured

### What's Broken

1. **extensionpacks/ import stubs** (CRITICAL) — 4 stub files shadow real modules. Capability pack system silently fails.
2. **scene-pack.schema.json motif enum** outdated — missing `semantic-essay`, `logical-argument`, `argument-diagram`
3. **Style packs** are JSON stubs — material profiles never wired into renderer
4. **Audio pipeline** — EnvelopeFollower/AudioRouter unit-tested but never used in actual rendering

### What Exists but Is Untested

- 14 empty capability pack inheritance roots
- 4 fully-implemented packs (invariant-composition 1044 LOC, neurocognition 775 LOC, anatomy 900 LOC, pathkit-geometry 79 LOC) — never runtime-tested
- 6 style packs — never applied
- 8 scene pack JSONs — never rendered
- Boolean path ops in `path-ops.mjs` — may not work depending on @napi-rs/canvas build
- 10 of 12 tool scripts — never run

### Redundancy

- `song-no-singer-delivery/framework/` — full duplicate of MOTHERFUCKER/
- `additives/` — another duplicate subtree
- `pillywilly/` — 424 legacy PIL scripts, not integrated

---

## 7. IMMEDIATE NEXT STEPS (Priority Order)

### P0 — Fix What's Broken (1-2 hours)

1. **Delete extensionpacks/ import stubs** — remove `semantic-visuals.mjs`, `theme.mjs`, `visual-assets.mjs`, `visual-semantics.mjs` from `extensionpacks/`. Update `capability-packs.mjs` lines 5-11 to import from `../` root instead of `./`.
2. **Fix scene-pack.schema.json** — add `semantic-essay`, `logical-argument`, `argument-diagram` to motif enum.

### P1 — Prove Pack System Works (2-4 hours)

3. Render `tools/render-pack.mjs packs/invariant-composition-demo.json`
4. Render `tools/render-pack.mjs packs/anatomy-test.json`
5. Render `tools/render-pack.mjs packs/neuro-test.json`

### P2 — Make Style Packs + Audio Real (4-8 hours)

6. Wire `materialProfiles` into `renderer.mjs` FrameRenderer
7. Wire AudioRouter into render loop

### P3 — Ship a Logicvid (2-3 hours)

8. Render `logicvid-04.json` — or build a new logicvid from scratch using the reusable scene pattern

### P4 — Clean Up (ongoing)

9. Delete duplicate framework copies (song-no-singer-delivery/framework/, additives/)
10. Validate all 13 scene packs
11. Add npm scripts for compile-essay, render-essay, render:pack

---

**This document captures everything discovered during the July 28, 2026 deep-dive session. Use it as the master reference to understand the full codebase without re-exploring.**

Key people/files to know for video work:
- `MOTHERFUCKER/renderer.mjs` → the render engine
- `MOTHERFUCKER/motifs.mjs` → the motif dispatcher
- `MOTHERFUCKER/src/argument-diagram.mjs` → logicvid motif
- `MOTHERFUCKER/packs/logicvid-04.json` → ready-to-render logicvid
- `.hermes/skills/tantraloka-film/SKILL.md` → the Hermes skill for making films
