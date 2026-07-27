# MOTHERFUCKER — Tantraloka Skia Essay-Film Framework

A deterministic, native-Skia motion-graphics pipeline for turning philosophical essays into narrated, relation-bearing visual films.

---

## Core Framework (`src/` — 16 modules, 4,864 lines)

| Module | Lines | Purpose |
|---|---|---|
| `semantic-visuals.mjs` | 728 | **15 philosophical mechanisms** — constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist |
| `systems-visuals.mjs` | 807 | Additional system-level visual renderers |
| `motifs.mjs` | 548 | **8 motifs** — `composition`, `semantic-essay`, `heart-lattice`, `attention-lens`, `phoneme-forge`, `reflexive-mirror`, `return-current`, `closing-heart-seal` |
| `primitives.mjs` | 447 | 20+ drawing primitives (glow orb, ring, lotus, label, path, arrow, grid, etc.) |
| `renderer.mjs` | 260 | `FrameRenderer` — Skia canvas → ffmpeg H.264 streaming |
| `composition.mjs` | 264 | Declarative layer engine (12 layer types) |
| `cli.mjs` | 269 | CLI: render, poster, contact, validate, motifs, fonts |
| `visual-auditor.mjs` | 241 | Correspondence auditing between essay and visuals |
| `essay-program.mjs` | 312 | Essay program compilation pipeline |
| `program-builder.mjs` | 310 | Builds scene packs from visual programs |
| `analysis.mjs` | 103 | Essay analysis (semantic role extraction) |
| `visual-semantics.mjs` | 171 | **Registry**: 21 relation types, 16 semantic roles, 14 visual operators |
| `math.mjs` | 137 | Deterministic math: easing, seeding, trig, color |
| `schema.mjs` | 103 | Runtime pack validation |
| `theme.mjs` | 91 | 3 themes: ivoryManuscript, whiteScientific, midnightVellum |
| `fonts.mjs` | 73 | EB Garamond + Noto Serif Devanagari registration |

---

## Shipped Films

| Film | Scenes | Runtime | Status |
|---|---|---|---|
| **infinite_learned_film_pack/** | 44 shots, 11 chapters | 11:25 | ✅ Validated MP4, 16,447 frames |
| **song-no-singer-delivery/output/** | 88 scenes | — | ✅ MP4 + timing map + motion QA + contact sheet |
| **film-packs/skia_gold_standard_demo/** | — | — | ✅ Rendered demo + 288 frame PNGs + manifest |
| **film-packs/the-world-learns-its-name-standalone/** | — | — | ✅ Composition JSON + score manifest |
| **film-packs/the-light-becomes-a-forest-standalone/** | — | — | ✅ Composition JSON + score manifest |
| **packs/hrdaya-original.json** | 6 scenes | — | ✅ Renderable demo pack |
| **programs/song-no-singer-analysis.json** | — | — | ✅ Full analysis + visual program (248 KB) |

---

## Tools & Schemas

| Path | Purpose |
|---|---|
| `tools/build-song-analysis.mjs` | Builds essay analysis JSON |
| `tools/build-song-program.mjs` | Builds visual program from analysis |
| `tools/export-storyboard.mjs` | Exports storyboard from program |
| `essay-visual-program.schema.json` | Schema v1 for visual programs |
| `essay-visual-program-v2.schema.json` | Schema v2 with capability packs |
| `essay-analysis.schema.json` | Schema for essay analysis |
| `scene-pack.schema.json` | Schema for compiled scene packs |
| `VISUAL_DECISION_PROTOCOL.md` | Visual decision guide |
| `ESSAY_TO_VISUAL_WORKFLOW.md` | Full essay-to-film workflow |
| `ESSAY_VISUAL_MODEL_PROMPT.md` / `_V2.md` | Agent prompt for visual program generation |

---

## Extension Packs (`extensionpacks/`)

ChatGPT-generated science domain capability pack architecture:
- **9 science mechanisms**: technical-rate-plot, evidence-ladder, phase-space-trajectories, barrier-tunnelling, energy-landscape, molecular-gate, moving-time-window, simultaneity-sequence, branching-future
- **Pack loader** (`capability-packs.mjs`) with inheritance resolver
- **Full spec**: pack manifests, schema, agent prompt, migration guide
- **AST audit tool** (`audit-pil-pack.py`) for mining existing PIL files
- **197 KB inventory** of 371 scenes from 24 PIL files
- ⚠️ Missing bridge modules: `semantic-visuals.mjs`, `theme.mjs` (registerTheme), `visual-semantics.mjs` need import stubs

---

## PIL Source Scripts (`pillywilly/` — 424 files)

| Category | Count | Source |
|---|---|---|
| PIL video render scripts (`pil/`) | 299 | goldrender/, moderngl/, queue* from tantraloka |
| Non-PIL scripts (`other/`) | 125 | data pipelines, analysis, OCR, server/tools |

---

## Assets

| Path | Contents |
|---|---|
| `assets/fonts/eb-garamond/` | EB Garamond Variable + Italic (OFL licensed) |
| `assets/fonts/noto-serif-devanagari/` | Noto Serif Devanagari Variable (OFL licensed) |

---

## Directory Layout

```
MOTHERFUCKER/
├── *.mjs                        # 16 kernel modules
├── *.json                        # 6 schemas & configs
├── *.md                          # 10 docs, workflows, prompts
├── packs/                        # 1 scene pack (hrdaya-original.json)
├── tests/                        # framework.test.mjs
├── assets/fonts/                 # EB Garamond + Noto Devanagari
├── tools/                        # 3 build/export scripts
├── programs/                     # song-no-singer analysis + visual program
├── infinite_learned_film_pack/   # 44-shot film (MP4, storyboard, validation)
├── song-no-singer-delivery/      # 88-scene film + full framework copy
│   ├── framework/                #   (redundant, same as root)
│   └── output/                   #   MP4, timing map, validation
├── film-packs/                   # 3 additional rendered packs
├── extensionpacks/               # ChatGPT science capability proposal
└── pillywilly/                   # 424 PIL python scripts
    ├── pil/                      #   299 PIL video renderers
    └── other/                    #   125 non-PIL scripts
```

---

## Tech Stack

- **Runtime:** Node.js + @aspect-build/aspect-skia (native Skia bindings)
- **Video:** FFmpeg (H.264 yuv420p, raw RGBA stdin)
- **Fonts:** OpenType via Skia
- **Determinism:** Seeded PRNG, no per-frame noise, reproducible output
- **Resolution:** 1280×720 logical, scale-independent
