# Handover — Tantraloka Skia Framework

## Channels

| Channel | Identity | Motif | Style | Content | Location |
|---|---|---|---|---|---|
| **Anakhya** | Sanskrit brand, publishing, academic papers | `semantic-essay` + `logical-argument` | Ivory manuscript, EB Garamond, gold/crimson/indigo | Tantraloka translations, academic papers, deep dives | MOTHERFUCKER |
| **Tantrafiles** | Tantraloka popular explainers, yogi docs | `semantic-essay` (GLSL signature film system) | Warm, devotional-academic, semantic primitives | Essay companions, practice guides, Alan Watts-style gold films | `/root/projects/blog/` — uses SIGNATURE-FILM-SYSTEM from `FATHERFUCKER/` bundles |
| **Ochema** | Sharp comparative metaphysics | `argument-diagram` | Monochrome + status colors, Source Serif 4 | Formal logicvids, proofs, concept maps, debates | MOTHERFUCKER |

Tantrafiles uses the **Signature Film System** from `FATHERFUCKER/integrated-composition-1/beautify-archive/framework/SIGNATURE-FILM-SYSTEM.md` — semantic primitives (Field, Focus, Agent, Boundary, Channel, Attractor, Trace, Witness) and visual verbs (emerge, gather, split, exclude, bind, transmit, recognize). This is the gold format used for existing Alan Watts-style explainers. The blog project (`/root/projects/blog/`) is the production home for this format; the framework (`MOTHERFUCKER/`) is the renderer it calls.

## Video types per channel

| Type | Motif | Length | Platform | Use |
|---|---|---|---|---|
| Explainer | `semantic-essay` | 6-12 min | Website, YouTube | Accessible narrative with abstract visuals |
| Logicvid | `argument-diagram` | 5-10 min | Ochema channel | Formal proofs, comparisons, concept maps |
| Short | `argument-diagram` (vertical) | 15-60s | Instagram, TikTok, YouTube Shorts | Hook / headline / core insight |

## Framework state

| Component | Status |
|---|---|
| Kernel (renderer, motifs, math, primitives, themes, fonts, schema) | ✅ Working |
| 17 capability packs | ✅ Registered |
| 6 style packs | ⚠️ Need registry wiring |
| `semantic-essay` motif | ✅ 15 base mechanisms + pack mechanisms |
| `argument-diagram` motif | ✅ 10 move types (claim, subclaim, refutation, premises, side-by-side, branch, concept-map, converge, divider) |
| `logical-argument` motif | ✅ Text block display |
| Audio reactivity | ⚠️ `env.audio` wired, only constraint-field uses it |
| Style pack resolution | ❌ Not wired — `stylePack` field in scene JSON is ignored |
| Hermes pipeline | ✅ Produces valid films autonomously |
| Vertical shorts | ✅ Render supports any resolution, just change width/height |
| KaTeX fonts | ⚠️ No Sanskrit diacritics, use for math only |
| Source Serif 4 | ✅ Full Sanskrit support, screen-optimized |

## Key files

| File | Location |
|---|---|
| Architecture reference | `MOTHERFUCKER/FRAMEWORK-ARCHITECTURE.md` |
| Agent guide | `MOTHERFUCKER/AGENT-GUIDE.md` |
| Build review | `MOTHERFUCKER/BUILD-REVIEW.md` |
| Future engine spec (parked) | `MOTHERFUCKER/FUTUREENGINE.md` |
| For ChatGPT | `MOTHERFUCKER/FOR_CHATGPT.md` |
| Capability packs | `MOTHERFUCKER/capability-packs/` (17 packs) |
| Style packs | `MOTHERFUCKER/style-packs/` (6 packs) |
| Kernel modules | `MOTHERFUCKER/*.mjs` |
| Extension modules | `MOTHERFUCKER/src/` (geometry, particles, materials, audio) |
| Tests | `MOTHERFUCKER/tests/` |
| Additive engine (separate) | `MOTHERFUCKER/additives/` |
| All git bundles | `FATHERFUCKER/` |
| Music theory + 6D engine | `FATHERFUCKER/6d-vector-engine/` |
| Visual analysis (Albers, Tymoczko, Doczi) | `FATHERFUCKER/visual-analysis/` |
| Transmissions | `FATHERFUCKER/transmissions/` |
| Process notes for skill building | `MOTHERFUCKER/process-notes-skills.md` |

## R2 bucket (blog-video-assets)

All rendered films, test packs, and demos.

## Vast GPU instance

Destroyed. Spin up a new one (`~$0.08/hr` on RTX 3060) when rendering. Install deps: `npm install`, `pip install librosa numpy`. Fonts need symlink: `ln -sf /root/vast-render/assets /root/assets`.

## Next priorities

1. Wire style pack resolution into `renderer.mjs` — `stylePack` field selects theme + material tokens
2. Build vertical short template (1080×1920, big text, 4-5 scenes at 5-8s each)
3. Expand argument-diagram with radial hierarchy layout mode for concept-map
4. Connect audio reactivity to more mechanisms
5. Build Anakhya brand style pack (ivory manuscript, warm gold/crimson/indigo, EB Garamond)
