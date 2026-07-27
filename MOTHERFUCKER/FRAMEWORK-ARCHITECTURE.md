# Tantraloka Skia Framework — Architecture Reference

## Overview

A deterministic, native-Skia motion-graphics framework for turning philosophical essays into narrated visual films. Extensible through composable capability packs, style profiles, and motif types.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Hermes Agent                          │
│  (autonomous film production via skill-based reasoning)     │
├─────────────────────────────────────────────────────────────┤
│                   Visual Program / Pack JSON                │
│  (scenes × motifs × params × capabilityPacks × styleProfiles)│
├─────────────────────────────────────────────────────────────┤
│                    Motif Registry                           │
│  semantic-essay | logical-argument | composition | ...      │
├─────────────────────────────────────────────────────────────┤
│            Scene Renderer (FrameRenderer)                   │
│  env = { theme, seed, audio, width, height }               │
├─────────────────────────────────────────────────────────────┤
│  Capability Packs  │  Geometry  │  Particles  │  Audio     │
│  (17 packs)         │  Engine   │  Engine     │  Bus       │
├─────────────────────────────────────────────────────────────┤
│             Skia / @napi-rs/canvas Kernel                   │
│  math | primitives | themes | fonts | schema | renderer    │
└─────────────────────────────────────────────────────────────┘
```

## Module Map

### Kernel (20 files, `/MOTHERFUCKER/`)
| Module | Lines | Role |
|---|---|---|
| `cli.mjs` | 269 | CLI: render, poster, contact, validate, compile-essay, render-essay |
| `renderer.mjs` | 264 | FrameRenderer + ffmpeg H.264 streaming + audio manifest loading |
| `motifs.mjs` | 548 | Motif registry + dispatch (semantic-essay, composition, etc.) |
| `semantic-visuals.mjs` | 773 | 15 philosophical mechanisms + constraint-field audio reactivity |
| `primitives.mjs` | 447 | 20 drawing primitives (glow, ring, lotus, label, path, etc.) |
| `composition.mjs` | 264 | Declarative layer engine (12 layer types) |
| `math.mjs` | 137 | Deterministic math: easing, seeded PRNG, trig, color |
| `theme.mjs` | 91 | 3 themes + dynamic theme registration |
| `fonts.mjs` | 73 | EB Garamond + Noto Serif Devanagari |
| `schema.mjs` | 103 | Runtime pack validation |
| `visual-semantics.mjs` | 171 | 21 relation types, 16 semantic roles, 14 visual operators |
| `systems-visuals.mjs` | 807 | System visual renderers |
| `visual-assets.mjs` | 68 | Asset overlay registration + rendering |
| `visual-auditor.mjs` | 241 | Essay/visual correspondence auditing |
| `essay-program.mjs` | 312 | Visual program compilation pipeline |
| `program-builder.mjs` | 310 | Builds scene packs from programs |
| `analysis.mjs` | 103 | Essay analysis |
| `scene-pack.mjs` | — | Pack format definitions |

### Extensions (25 files, `/MOTHERFUCKER/src/`)

**Geometry Engine** (7 modules)
| Module | Purpose |
|---|---|
| `geometry/path-ops.mjs` | Path2D union/intersect/difference/XOR, trim, dash, stroke |
| `geometry/path-utils.mjs` | Path construction utilities |
| `geometry/lotus-generators.mjs` | Parametric radial lotus geometry |
| `geometry/yantra-generators.mjs` | Layered triangle, bindu, enclosure |
| `geometry/mandala-generators.mjs` | Multi-layer mandala construction |
| `geometry/flame-generators.mjs` | Parametric flame/aureole contours |
| `geometry/symmetry.mjs` | Radial and dihedral symmetry |

**Particle Engine** (5 modules)
| Module | Purpose |
|---|---|
| `particles/particle-system.mjs` | Deterministic particle kernel |
| `particles/emitters.mjs` | Point, line, path, ring, area emitters |
| `particles/fields.mjs` | Flow, curl, orbital, spiral, attractor fields |
| `particles/constraints.mjs` | Inside/outside/along/between constraints |
| `particles/renderers.mjs` | Orb, dash, spark, droplet, petal, bindu appearances |

**Materials System** (3 modules)
| Module | Purpose |
|---|---|
| `materials/materials.mjs` | Conic gradients, radial glow, palette ramp |
| `materials/color.mjs` | Oklab perceptual color interpolation |
| `materials/layer-stack.mjs` | Multi-layer compositing (base → pigment → glow → particles → text) |

**Audio Bus** (2 modules)
| Module | Purpose |
|---|---|
| `audio/audio-features.mjs` | Feature manifest loader, envelope follower, per-frame sampling |
| `audio/audio-router.mjs` | Declarative feature → visual parameter routing |

**Argument Display** (new)
| Module | Purpose |
|---|---|
| `argument-display.mjs` | Logical-argument motif: boxed equations, proofs, tables, citations |

## Capability Packs (17)

| Pack | Extends | Mechanisms | Runtime Module |
|---|---|---|---|
| `base` | — | 15 built-in | (built into semantic-visuals.mjs) |
| `human-anatomy` | base | 9 | `src/anatomy-visuals.mjs` |
| `yogic-subtle-body` | human-anatomy | 7 | `src/anatomy-visuals.mjs` |
| `neurocognition` | base | 8 | `src/neuro-visuals.mjs` |
| `invariant-composition` | systems-dynamics + temporal-processes + comparative-epistemology | 12 | `src/invariant-visuals.mjs` |
| `pathkit-geometry` | base | 3 (lotus-unfold, yantra-construction, mandala-entry) | `src/capabilities/pathkit-visuals.mjs` |
| `particle-fields` | base | — | `src/particles/*` |
| `audio-reactive` | base | — | `src/audio/*` |
| `tantric-geometry` | base | — | `src/capabilities/pathkit-visuals.mjs` |
| 8 inheritance roots | base | 0 (policy-only) | — |

## Style Packs (6)

`mineral-manuscript`, `ritual-gold`, `luminous-subtle-body`, `technical-neural`, `visionary-midnight`, `ash-and-ember`

## Motifs

| Motif | Purpose |
|---|---|
| `semantic-essay` | Essay narrative → visual mechanisms (15 philosophical + pack mechanisms) |
| `composition` | Declarative layer stack |
| `heart-lattice` | Breathing bindu-lotus grid |
| `attention-lens` | Particle currents and elliptical lenses |
| `phoneme-forge` | Sanskrit phoneme path → geometry |
| `reflexive-mirror` | Subject/world circulating loop |
| `return-current` | Descending structure reversed by recognition |
| `closing-heart-seal` | Multi-ring cosmogram |
| `logical-argument` (new) | Formal logic display: boxed equations, proofs, tables, citations |

## Hermes Agent Pipeline

### Skill: `tantraloka-film`
Location: `.opencode/skills/tantraloka-film/SKILL.md` / `/root/.hermes/skills/tantraloka-film/SKILL.md`

### Non-negotiable order
1. Read source → output argument IR (roles, relations, states, invariants — no visuals)
2. Define continuity systems (3-6, with lifecycle)
3. Select composition structure and capability packs
4. Generate 3+ mechanism candidates per beat, scored by 8 criteria
5. Select by relation preservation — MAX 2 uses of same mechanism
6. Apply geometry, material, style profiles
7. Render review frames (t=0.00, 0.25, 0.55, 0.82, 1.00)
8. Generate TTS, render final video, mux audio

### Proven outputs
- **hermes-v3**: Crowley, 7 mechanisms, 5x wave-ocean (poor)
- **hermes-v4**: Crowley, 12 mechanisms, 0 repeats (good — max-2 rule)
- **hermes-v5**: Alchemy, 12 mechanisms from 3 packs (best — argument IR, multi-pack)

## File Locations

| Resource | Path |
|---|---|
| Framework root | `/root/projects/clean/MOTHERFUCKER/` |
| Test packs | `MOTHERFUCKER/packs/hrdaya-original.json` |
| Shipped films | `MOTHERFUCKER/infinite_learned_film_pack/` |
| Agent guide | `MOTHERFUCKER/agent-guide/` |
| Build output | `MOTHERFUCKER/build/` |
| Hermes logs | `MOTHERFUCKER/build/hermes-v*/` |
| Extension packs (future) | `MOTHERFUCKER/additives/` |
| FATHERFUCKER (bundles) | `FATHERFUCKER/` |
| Skia docs | `FATHERFUCKER/skia-capabilities.md` |

## Key Documents

| Doc | Content |
|---|---|
| `FRAMEWORK-READINESS.md` | Gap analysis |
| `BUILD-REVIEW.md` | Current status |
| `FUTUREENGINE.md` | Cross-modal style spec (parked) |
| `VISUAL_CODING_LANGUAGE.md` | Composition grammar |
| `VISUAL_DECISION_PROTOCOL.md` | 4-pass decision protocol |
| `ESSAY_VISUAL_MODEL_PROMPT.md` | Agent prompt for visual programs |
| `ANATOMY_PACK.md` | Anatomy pack design |
| `PACK_ROADMAP.md` | Prioritized future packs |
| `agent-guide/` | 9 system docs, templates, examples |
