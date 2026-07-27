# Tantraloka Skia Framework — Agent Guide

## What This Is

A deterministic motion-graphics framework for turning philosophical essays into narrated visual films. It produces MP4 files at 1280×720, H.264, with optional TTS narration and audio-reactive visuals.

**Not a general video editor.** Not After Effects. Not Three.js. It is an **essay-to-film compiler** with a composable visual mechanism library.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Essay (Markdown)                         │
└───────────────────────────┬──────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  1. Argument IR (roles, relations, states, invariants, no VFX)   │
│  2. Continuity systems (3-6 visual objects with stable meanings) │
│  3. Capability pack selection                                    │
│  4. Mechanism candidates per beat (score ≥72/100)                 │
│  5. Scene pack JSON                                              │
└───────────────────────────┬──────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  renderer.mjs → FrameRenderer → ffmpeg → H.264 MP4               │
│    ↓ env.audio (optional)                                         │
│    ↓ env.theme resolves colors/fonts                              │
│    ↓ renderMotif dispatches to registered motif                   │
└──────────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  edge-tts → narration.mp3 → ffmpeg mux → final MP4               │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Layout

All paths relative to `MOTHERFUCKER/`.

| Path | Purpose |
|---|---|
| `cli.mjs` | CLI entry point |
| `renderer.mjs` | FrameRenderer class, ffmpeg pipe, audio env |
| `motifs.mjs` | Motif registry (semantic-essay, argument-diagram, etc.) |
| `schema.mjs` | Pack JSON validation |
| `theme.mjs` | 3 themes + dynamic registration |
| `fonts.mjs` | EB Garamond + Noto Serif Devanagari |
| `math.mjs` | Deterministic math, seeded PRNG, easing |
| `primitives.mjs` | Drawing primitives (glow, path, label, ring, lotus) |
| `semantic-visuals.mjs` | 15 philosophical mechanisms + constraint-field audio reactivity |
| `src/geometry/` | Path2D boolean ops, lotus/yantra/mandala generators |
| `src/particles/` | Deterministic particle system |
| `src/materials/` | Conic gradients, Oklab color, layer compositing |
| `src/audio/` | Audio feature manifest loader + routing |
| `src/argument-diagram.mjs` | Argument-diagram motif renderer |
| `src/argument-display.mjs` | Logical-argument text block motif |
| `src/load-capability-scene-pack.mjs` | Capability-aware pack loader |
| `capability-packs/*/pack.json` | 17 pack manifests |
| `style-packs/*.json` | 6 material profiles |
| `packs/` | Compiled scene packs |
| `tools/analyse-audio.py` | Librosa feature extraction |
| `tools/render-pack.mjs` | Capability-aware render helper |
| `tools/probe-canvas-capabilities.mjs` | Skia feature probe |
| `extensionpacks/` | Capability pack bridge modules |
| `agent-guide/` | 9 docs, templates, examples |

---

## Three Motif Types

### 1. `semantic-essay` — Abstract Visual Mechanisms

The primary motif. Maps essay paragraphs to visual mechanisms that encode relations through motion.

**Scene format:**
```json
{
  "id": "sc01",
  "title": "Beat name (2-80 chars)",
  "subtitle": "Interpretive sentence (2-140 chars)",
  "term": "IAST term (1-50 chars)",
  "devanagari": "देवनागरी",
  "motif": "semantic-essay",
  "duration": 6.0,
  "params": {
    "visual": "mechanism-id",
    "caption": "Short label"
  }
}
```

**15 base mechanisms** (always available):
constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist

**Packs add more** — see `capability-packs/*/pack.json` for full descriptions with motion proofs.

**No mechanism may be used more than twice in a single film.** The skill enforces this.

### 2. `argument-diagram` — Animated Formal Logic

Clean white screen with centered animated typography. Best for formal philosophy, proofs, comparisons, and structured arguments.

**Scene format:**
```json
{
  "motif": "argument-diagram",
  "duration": 12,
  "params": {
    "moves": [
      {"type": "claim", "text": "The claim", "size": 36, "status": "active"},
      {"type": "subclaim", "text": "Supporting text", "y": 400, "size": 18},
      {"type": "refutation", "text": "Objection", "color": "#c4445a"},
      {"type": "divider"},
      {"type": "branch", "branches": [
        {"label": "Position A", "color": "#3b7a9e"},
        {"label": "Position B", "color": "#c4445a"}
      ]},
      {"type": "converge", "text": "Resolution"},
      {"type": "premises", "premises": ["P1.", "P2."], "conclusion": "∴ Conclusion"},
      {"type": "side-by-side", "left": "A", "right": "B"}
    ]
  }
}
```

**No footer, no border, no background texture.** Pure white canvas. This is intentional.

**Status colors:** `active` (ink), `refuted` (red), `resolved` (green), `neutral` (grey), `highlight` (gold). Use `"statusTransition": true` for smooth color animations.

### 3. `logical-argument` — Styled Text Blocks

Document-style layout with section headers, body text, boxed equations, proofs, tables, and citations. Uses the theme system (footer, border, background).

**Block types:** section-header, body, boxed-equation, proof, table, citation, divider

---

## Pack System

### Capability Packs (17)

Packs add mechanisms and assets. They extend a parent pack and inherit its vocabulary.

```
base
├── human-anatomy → yogic-subtle-body
├── neurocognition
├── pathkit-geometry
├── particle-fields
├── audio-reactive
├── tantric-geometry
├── invariant-composition
├── scientific-diagrams → data-visualization
├── systems-dynamics
├── temporal-processes
├── embodied-phenomenology
├── textual-scholarship
├── tantric-cosmology
└── comparative-epistemology
```

**To use a pack's mechanisms** in a scene pack:
```json
{
  "capabilityPacks": ["human-anatomy"],
  "theme": "anatomyIvory",
  "scenes": [
    {"params": {"visual": "breath-cycle"}}
  ]
}
```

### Style Packs (6)

Material/presentation profiles. Not yet resolved at render time — theme selection is manual.

- `mineral-manuscript` — multiply-blended pigment, dark ink, no glow
- `ritual-gold` — gold leaf fragments, warm conic gradients, additive highlights
- `luminous-subtle-body` — screen compositing, blurred underlayers, particle trails
- `technical-neural` — precise paths, cool blue/cyan, sparse labels
- `visionary-midnight` — near-black ground, saturated P3 fields, luminous dust
- `ash-and-ember` — charcoal paths, multiply layers, drifting ash

---

## The Hermes Pipeline (12-Step Protocol)

### Step 1: Read Source Completely
Read the full essay. Identify structure: paragraphs, quotations, lists, visual-only sections.

### Step 2: Output Argument IR (NO VISUALS)
Write to `argument-ir.md`. For each paragraph, state:
- **Semantic role:** hook, thesis, definition, mechanism, analogy, consequence, objection, reversal, practice, recognition, synthesis, coda
- **Relation type:** identity-across-change, dependency, interface, emergence, containment, selection, sequence, feedback, transformation, cessation, self-modification, coordination, differentiation
- **Source state → Target state**
- **Preserved invariant**
- **Likely misreading**

Do not name any visual mechanisms in this step.

### Step 3: Define Continuity Systems
Choose 3-6 recurring visual objects with stable meanings. Each needs:
- One stable semantic meaning
- One stable visual treatment
- A lifecycle: introduction → development → contrast → return → resolution

From the proven infinite-learned film:
```
luminous-field: gold-white — common substance of awareness, never replaced
crimson-frame: enclosing boundary — active limitation
indigo-locality: finite figure — the individual self
gold-current: continuity between universal and local
opening-gesture: five arcs — contraction as reversible gesture
```

### Step 4: Select Composition Profile
Choose the argument structure:
- **Linear:** claim → evidence → conclusion
- **Dialectical:** thesis → antithesis → synthesis
- **Branching:** one premise → multiple competing positions
- **Recognition:** problem → confusion → reversal → insight

Select required capability packs based on the essay's domain.

### Step 5: Activate Capability Packs
For each selected pack, read its `pack.json` manifest for available mechanisms, their motion proofs, and epistemic modes.

### Step 6: Generate 3+ Candidates Per Beat
For each paragraph group, generate at least three mechanism candidates. Score each:

| Criterion | Points |
|---|---|
| Relation correspondence | 30 |
| Motion performs the claim | 20 |
| Domain/scale match | 15 |
| Continuity handoff | 15 |
| Silent legibility | 10 |
| Novelty vs adjacent | 10 |

### Step 7: Select by Relation Preservation
Choose the candidate that best encodes the paragraph's relation. **No mechanism more than twice.** Reject candidates that are merely beautiful and interchangeable.

### Step 8: Apply Profiles
Assign style, material, motion profiles to each scene.

### Step 9: Route Narration Signals
When narration is dense: reduce particle emission, simplify background, preserve explanatory geometry.
When narration withdraws: allow visual process to complete.

### Step 10: Validate
Check every scene at t = 0.00, 0.25, 0.55, 0.82, 1.00.
Hard failures: missing pack activation, unsupported mechanism, unregistered theme, non-deterministic output, arbitrary symbol substitution, biomedical/symbolic collapse, scene legible only through title.

### Step 11: Render
```bash
cd MOTHERFUCKER
node tools/render-pack.mjs packs/pack.json
```

For capability packs, use `render-pack.mjs` — not `cli.mjs render` (which doesn't activate packs).

### Step 12: TTS + Mux
```bash
edge-tts --voice en-GB-SoniaNeural -f narration.txt --write-media chunk.mp3
ffmpeg -f concat -safe 0 -i concat.txt -c copy full.mp3
ffmpeg -i video.mp4 -i full.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

---

## Audio Reactivity

Optional. To activate:

1. Generate TTS first: `edge-tts ... --write-media narration.mp3`
2. Analyse: `python3 tools/analyse-audio.py narration.mp3 features.json`
3. Add to pack: `"audioManifest": "features.json"`
4. Render: mechanisms receive `env.audio` with per-frame `rms`, `onset`, `beatPulse`

Currently only `constraint-field` reads `env.audio` (glow pulses with RMS, rings expand on onset).

---

## Expanding the Framework

### New Mechanism
Add to an existing pack's `pack.json` and its runtime module. The mechanism must declare: `id`, `description`, `relations`, `operators`, `semanticTags`, `motionProof`, `epistemicMode`.

### New Motif
1. Create `src/your-motif.mjs` exporting `renderYourMotif(ctx, t, scene, env)`
2. Register in `motifs.mjs`: `"your-motif": renderYourMotif`
3. Scene uses `"motif": "your-motif"`

### New Pack Type
Build geometry (7 modules), particles (5 modules), materials (3 modules), or audio (2 modules) independently and compose them in the pack manifest. No kernel changes needed.

### Audio → Visual Routing
Add routes in `src/audio/audio-router.mjs`. Each route maps a feature (onset, rms, centroid) to a visual parameter (glow radius, particle emission, colour temperature). Requires `env.audio` to be present.

---

## Key Constraints

- **Determinism:** Same seed + same input = identical output. No Math.random(), Date.now(), or network I/O during render.
- **30s max per scene** (compile-essay enforces this)
- **2 max uses of same mechanism** per film
- **Devanagari must be correct script** — never IAST in the devanagari field
- **Every scene needs a rationale** stating what relation it encodes
- **No narration-as-caption** — the footer shows title/subtitle, not the spoken text

---

## Reference Films

| Film | Location | Scenes | Motif |
|---|---|---|---|
| Infinite Learned | `infinite_learned_film_pack/` | 44 | semantic-essay |
| Song No Singer | `song-no-singer-delivery/` | 88 | semantic-essay |
| Hermes v5 (Alchemy) | `build/hermes-v5/` | 12 | semantic-essay |
| Logicvid 04 | `packs/logicvid-04.json` | 7 | argument-diagram |

---

## Tech Stack

| Component | What |
|---|---|
| Rendering | Skia via @napi-rs/canvas |
| Video | ffmpeg (H.264 yuv420p, raw RGBA stdin) |
| Fonts | EB Garamond (latin) + Noto Serif Devanagari |
| Math | Deterministic, seeded PRNG, no per-frame noise |
| Audio | librosa (offline analysis) + edge-tts |
| Agent | Hermes CLI (`hermes -z`) |
| Pack format | JSON with schema validation |
| Theme | 3 built-in + dynamic registration |
