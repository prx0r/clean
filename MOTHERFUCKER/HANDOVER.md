# Handover — Tantraloka Skia Framework

## Channels

| Channel | Identity | Motif | Style | Content | Location |
|---|---|---|---|---|---|
| **Anakhya** | Sanskrit brand, publishing, academic papers | `semantic-essay` + `logical-argument` | Ivory manuscript, EB Garamond, gold/crimson/indigo | Tantraloka translations, academic papers, deep dives | MOTHERFUCKER |
| **Tantrafiles** | Tantraloka popular explainers, yogi docs | Beat-map → `semantic-essay` (signature film system) | Warm, devotional-academic, semantic primitives | Yogi biographies, essay companions, practice guides | `/root/projects/blog/` — beat-map format, uses SIGNATURE-FILM-SYSTEM |
| **Ochema** | Sharp comparative metaphysics | `argument-diagram` | Monochrome + status colors, Source Serif 4 | Formal logicvids, proofs, concept maps, debates | MOTHERFUCKER |
| **Intelligent Others** | Machine consciousness, hybrid life, astrobiology | `argument-diagram` + `concept-map` | Technical-neural style pack (cool blue/cyan, precise paths) | AI consciousness, synthetic biology, exobiology, posthuman | MOTHERFUCKER |

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

### Phase 1 — Foundation fixes (1-2 days)
1. Wire style pack resolution into `renderer.mjs` — `stylePack` field selects theme + material tokens
2. Add `"format": "short"` flag → auto-resolution 1080×1920, text size ×1.5, scene timing ×0.6, suppress footer
3. Build batch short renderer — given a long scene pack, extract 3-5 short packs (hook, insight, punchline), render all vertical
4. Connect audio reactivity to invariant-composition and intelligent-others mechanisms
5. Add HSB color utility to `src/materials/color.mjs` — hue wheel interpolation, not RGB lerp

### Phase 2 — Intelligent Others launch (3-5 days)
6. Build `science-diagram` motif with move types: network (force-directed), field (wave propagation), membrane (cell boundary), tree (phylogenetic), sequence (data track), oscillation (waveform)
7. Wire `intelligent-others` pack to render correctly — test all 9 science-visuals mechanisms
8. Build derivative-trajectory demo (position, velocity, acceleration) — core science viz primitive
9. Port the 20 scientific visualization techniques from `pratyabhijnahrdayam_SOURCE_NOTES.md` as Skia mechanisms (harmonograph, L-system, Lissajous, Voronoi, Clifford attractor, Chladni patterns)

### Phase 3 — Scaling (ongoing)
10. Batch short renderer → produce 5 shorts from each long video
11. YouTube title data integration — short titles use breakout patterns from channel analysis
12. Build Anakhya brand style pack (ivory manuscript, warm gold/crimson/indigo, EB Garamond)
13. Expand argument-diagram concept-map with radial/hierarchy/chain/dialectical layout modes
14. Full Hermes pipeline: research → essay → IR → beat-map → scene pack → render → shorts → publish

## DevNext

Full build notes for meditation motif, sleeper pipeline, voice cloning, music themes, and shorts batch at `MOTHERFUCKER/devnext.md`.

## Key references added this session

| File | Content |
|---|---|
| `magnum-opus/21-ANAKHYA.md` | Anakhya channel identity |
| `magnum-opus/22-TANTRAFILES.md` | Tantrafiles channel + beat-map pipeline |
| `magnum-opus/23-OCHEMA.md` | Ochema channel identity |
| `magnum-opus/24-INTELLIGENT-OTHERS.md` | Intelligent Others pack + science viz refs |
| `magnum-opus/25-SHORTS-PIPELINE.md` | Shorts format, 2-skill system, YouTube title data |
| `capability-packs/intelligent-others/pack.json` | Extends scientific-diagrams + invariant-composition |
| `agent-guide/chatgpt-process-notes/` | 9 ChatGPT process notes + 20 visualization techniques |
| `FOR_CHATGPT.md` | Full framework context for LLM agents |
