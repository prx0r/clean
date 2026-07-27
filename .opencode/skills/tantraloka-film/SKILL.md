---
name: tantraloka-film
description: |
  Use ONLY when the user asks to create a visual film/essay companion from a philosophical essay using the Tantraloka Skia framework.
  Provides tools for essay analysis, visual program creation, Skia rendering, TTS narration, and final MP4 assembly.
  Works with files under MOTHERFUCKER/.
---

# Tantraloka Skia Essay-Film Pipeline

A deterministic, native-Skia motion-graphics framework for turning philosophical essays into narrated visual films.

## Framework Location

All framework files are under `MOTHERFUCKER/` in the project root.

## Available Pack Manifests (read these to choose mechanisms)

Read the relevant `pack.json` files to see available visual mechanisms:

- `MOTHERFUCKER/capability-packs/base/pack.json` — 15 built-in philosophical mechanisms
- `MOTHERFUCKER/capability-packs/human-anatomy/pack.json` — body, breath, meditation mechanisms
- `MOTHERFUCKER/capability-packs/yogic-subtle-body/pack.json` — chakras, nadis, kundalini
- `MOTHERFUCKER/capability-packs/neurocognition/pack.json` — attention, prediction, memory, learning
- `MOTHERFUCKER/capability-packs/scientific-diagrams/pack.json` — scientific visual base
- `MOTHERFUCKER/capability-packs/comparative-epistemology/pack.json` — epistemological comparisons

## Key Documents (read these for grammar and workflow)

- `MOTHERFUCKER/VISUAL_CODING_LANGUAGE.md` — scene composition grammar
- `MOTHERFUCKER/VISUAL_DECISION_PROTOCOL.md` — 4-pass decision procedure for mapping essay to visuals
- `MOTHERFUCKER/ESSAY_VISUAL_MODEL_PROMPT.md` — agent prompt for visual program generation
- `MOTHERFUCKER/VISUAL_DECISION_PROTOCOL.md` — deterministic visual decision protocol
- `MOTHERFUCKER/extensionpacks/CAPABILITY-PACK-ARCHITECTURE.md` — full architecture

## Built-in 15 Philosophical Mechanisms `MOTHERFUCKER/capability-packs/base/pack.json`

| Mechanism | What it does |
|---|---|
| `constraint-field` | An unbounded luminous field concentrates into a local point |
| `point-of-view` | A centerless field acquires an angle and excluded horizon |
| `five-lenses` | Five restrictions transform universal powers into local capacities |
| `local-power` | Universal radial capacity becomes one finite action |
| `melody-time` | Simultaneity becomes sequence, rhythm, anticipation, memory |
| `attention-beam` | A narrow act of knowing reveals a foreground and produces a dark |
| `desire-orbit` | Fullness localizes as a felt gap and reaching movement |
| `smallness-cage` | The thought "only this" builds a local enclosure |
| `powered-prison` | Luminous power actively constructs and renews its own limits |
| `practice-folds` | Body, breath, mantra, attention retrace folds toward source |
| `upsurge` | A local center reverses into a centerless field |
| `wave-ocean` | A finite wave keeps its contour while revealing continuity |
| `textures-display` | One field differentiates into many sensory textures |
| `limitation-reversal` | A finite condition remains real but loses status as identity |
| `opening-fist` | Five enclosing arcs relax around the luminous field |

## Anatomy Mechanisms `MOTHERFUCKER/capability-packs/human-anatomy/pack.json`

`embodied-awareness-field`, `body-scan`, `meditation-settling`, `breath-cycle`, `breath-attention-coupling`, `nervous-signal-propagation`, `interoceptive-map`, `body-world-interface`, `heart-breath-entrainment`

## Neuro Mechanisms `MOTHERFUCKER/capability-packs/neurocognition/pack.json`

`attention-selection`, `predictive-loop`, `pattern-completion`, `memory-consolidation`, `neural-propagation`, `competitive-binding`, `temporal-integration`, `error-driven-learning`

## Pipeline Steps

### Step 1: Read & Analyze the Essay

Read the source essay markdown. Divide it into paragraphs. For each paragraph, identify:
- The semantic role (thesis, definition, mechanism, analogy, consequence, reversal, recognition, practice, synthesis, coda)
- The continuity objects that persist across shots
- The relation type (identity, dependency, emergence, containment, selection, sequence, feedback, transformation, etc.)

### Step 2: Choose Continuity Systems

Define 3-6 visual continuity systems with stable meanings. Example:
```json
{
  "id": "luminous-field",
  "meaning": "Infinite awareness — centerless, unbounded, always present.",
  "treatment": "A gold-white radial field that fills frame or appears as a soft glow."
}
```

### Step 3: Map Paragraphs to Mechanisms

For each paragraph, select a visual mechanism from the pack manifests that best encodes the paragraph's relation. Use the `semantic-essay` motif with `params.visual` set to the mechanism ID.

### Step 4: Create a Compiled Scene Pack (not visual program)

The essay compiler has a 30s-per-shot limit. For dense philosophical prose, write the compiled pack JSON directly.

Format:
```json
{
  "version": "1.0",
  "id": "your-essay-id",
  "title": "Your Essay Title",
  "description": "Visual companion to essay.",
  "theme": "ivoryManuscript",
  "seed": 123456,
  "render": {
    "width": 1280, "height": 720, "fps": 24, "crf": 18,
    "preset": "medium", "sceneDuration": 8, "transitionDuration": 0.5
  },
  "scenes": [
    {
      "id": "sc01",
      "title": "Scene Title",
      "subtitle": "Scene subtitle (2-140 chars)",
      "term": "Sanskrit term",
      "devanagari": "देवनागरी",
      "motif": "semantic-essay",
      "duration": 8.0,
      "params": {
        "visual": "mechanism-id",
        "caption": "Short caption shown on screen"
      }
    }
  ]
}
```

### Step 5: Render the Video

There are two render paths:

**For packs using only built-in mechanisms (base pack):**
```bash
cd MOTHERFUCKER
node cli.mjs render packs/your-pack.json --out build/your-film/your-film.mp4
```

**For packs using custom mechanisms (neurocognition, human-anatomy, invariant-composition):**
The pack JSON must have a `capabilityPacks` array at the top level. Render using a capability-aware loader:

```js
import { loadCapabilityScenePack } from "./src/load-capability-scene-pack.mjs";
import { renderVideo } from "./renderer.mjs";

const pack = await loadCapabilityScenePack("./packs/your-pack.json");
const result = await renderVideo(pack, "build/your-film/your-film.mp4");
```

Or use the included demo render scripts as templates:
```bash
node tools/render-invariant-demo.mjs
node tools/test-neuro-pack.mjs
node tools/test-anatomy-pack.mjs
```

### Step 6: Generate TTS Narration

1. Extract plaintext from the essay markdown (strip headers, citations)
2. Trim to ~1050 words max (fits ~6 min at 180wpm)
3. Split into ~200-word chunks
4. Generate each chunk with edge-tts:
```bash
edge-tts --voice en-GB-SoniaNeural -f chunk.txt --write-media chunk.mp3
```
5. Concatenate chunks:
```bash
ffmpeg -f concat -safe 0 -i concat.txt -c copy narration_full.mp3
```

### Step 7: Mux Audio with Video

Calculate speed ratio = video_duration / audio_duration. Apply atempo filter:
```bash
ffmpeg -i video.mp4 -i narration_full.mp3 -c:v copy \
  -filter:a "atempo=1.11" -c:a aac -map 0:v:0 -map 1:a:0 -shortest \
  final-film.mp4
```

### Step 8: Validate

```bash
node cli.mjs validate packs/your-pack.json
ffprobe final-film.mp4
```

## Tips

- Keep each shot under 28s if possible (the compiler enforces 30s max)
- Use `constraint-field` for opening thesis shots (luminous field + local point)
- Use `opening-fist` or `upsurge` for recognition/climax shots
- Use `melody-time` for sequencing (four stations, four limbs, etc.)
- Use `practice-folds` for discipline/effort/training descriptions
- Use `desire-orbit` for devotion/bhakti/reaching
- Use `powered-prison` or `smallness-cage` for limitation/bondage descriptions
- For continuity, always carry the luminous field and local point through multiple shots
- The `overlays` array can layer assets on top of mechanisms for extra context

## Example: Working Film Packs

- `MOTHERFUCKER/packs/hrdaya-original.json` — 6-scene demo pack
- `MOTHERFUCKER/packs/magician-compiled.json` — 14-scene Crowley essay pack (366s, with TTS)
- `MOTHERFUCKER/infinite_learned_film_pack/` — 44-shot validated film
- `MOTHERFUCKER/film-packs/stones-are-watching/` — 106-shot film
