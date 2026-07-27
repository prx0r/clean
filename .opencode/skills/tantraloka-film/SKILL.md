---
name: tantraloka-film
description: |
  Use ONLY when the user asks to create a visual film/essay companion from a philosophical essay using the Tantraloka Skia framework.
  Provides tools for essay analysis, visual program creation, Skia rendering, TTS narration, and final MP4 assembly.
  Works with files under MOTHERFUCKER/.
---

# Tantraloka Skia Essay-Film Framework

Deterministic motion-graphics framework for turning philosophical essays into narrated visual films. Located at `MOTHERFUCKER/`.

## Core Principle

**Illustrate relations, not nouns.** A viewer should be able to infer the logic of each beat from the motion alone. Do not choose visual mechanisms by keyword — choose the mechanism whose geometry demonstrates the passage's proposition.

## The 4-Pass Decision Protocol

Do not collapse passes. Choosing an image while summarizing a paragraph makes the first association feel inevitable.

### Pass 1: Visual-Free Argument Analysis

Read the essay. Remove headings. Number paragraphs 1-N.

For each paragraph, identify WITHOUT naming any visual:
- **Semantic role** — hook, thesis, definition, mechanism, analogy, consequence, objection, reversal, practice, recognition, synthesis, coda
- **Relation type** — identity-across-change, dependency, interface, emergence, containment, selection, sequence, feedback, transformation, cessation, self-modification, etc.
- **Source state** → **Target state**
- **Preserved invariant**
- **Likely misreading** — what a literal illustration would get wrong

### Pass 2: Define Continuity Systems (BEFORE mechanisms)

Choose 2-9 recurring visual systems. Each must have one stable meaning, one stable treatment, and a lifecycle (introduction → development → return → resolution).

### Pass 3: Generate Scored Mechanism Candidates

For each beat, generate 3+ candidates scored by: relation correspondence (30), motion performs the claim (20), domain/scale match (15), continuity handoff (15), legibility (10), novelty (10). Select only candidates scoring ≥72.

### Pass 4: Audit

Every shot needs a rationale stating: what relation, what changes, what persists, why explanatory. Reject "make it beautiful" or "show consciousness."

## Available Mechanisms

Read `MOTHERFUCKER/capability-packs/*/pack.json` for full descriptions and motion proofs.

### Base pack (15 mechanisms, always available)
constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist

### Human-anatomy (requires capabilityPacks: ["human-anatomy"])
embodied-awareness-field, body-scan, meditation-settling, breath-cycle, breath-attention-coupling, nervous-signal-propagation, interoceptive-map, body-world-interface, heart-breath-entrainment

### Neurocognition (requires capabilityPacks: ["neurocognition"])
attention-selection, predictive-loop, pattern-completion, memory-consolidation, neural-propagation, competitive-binding, temporal-integration, error-driven-learning

### Invariant-composition (requires capabilityPacks: ["invariant-composition"])
transformation-invariance, carrier-transfer, causal-memory, derivative-trajectory, lead-lag-counterpoint, conservation-filter, semantic-transition, polyphonic-identity, recognition-transaction, climax-assimilation, structural-homology, constraint-tournament

## Visual Operators (choose one per shot)

reveal, contract, frame, filter, sequence, select, reach, enclose, construct, unfold, invert, differentiate, recontextualize, open

## Scene Format

```json
{
  "id": "sc01",
  "title": "Beat name (2-80 chars)",
  "subtitle": "Interpretive sentence (2-140 chars)",
  "term": "IAST term (1-50 chars)",
  "devanagari": "देवनागरी",
  "motif": "semantic-essay",
  "duration": 6.0,
  "params": { "visual": "mechanism-id", "caption": "Short label" }
}
```

## Render

### Base mechanisms only:
```bash
cd MOTHERFUCKER
node cli.mjs render packs/your-pack.json --out build/film.mp4
```

### Custom packs (capabilityPack field in JSON):
```js
import { loadCapabilityScenePack } from "./src/load-capability-scene-pack.mjs";
import { renderVideo } from "./renderer.mjs";
const pack = await loadCapabilityScenePack("./packs/your-pack.json");
await renderVideo(pack, "build/film.mp4");
```

See `MOTHERFUCKER/tools/test-neuro-pack.mjs` and `MOTHERFUCKER/tools/test-anatomy-pack.mjs` for working examples.

## TTS + Mux

```bash
edge-tts --voice en-GB-SoniaNeural -f narration.txt --write-media chunk.mp3
ffmpeg -f concat -safe 0 -i concat.txt -c copy full.mp3
ffmpeg -i video.mp4 -i full.mp3 -c:v copy -filter:a "atempo=RATIO" -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

## Reference Docs

- `MOTHERFUCKER/VISUAL_DECISION_PROTOCOL.md` — full 4-pass protocol
- `MOTHERFUCKER/VISUAL_CODING_LANGUAGE.md` — composition grammar
- `MOTHERFUCKER/ESSAY_VISUAL_MODEL_PROMPT.md` — agent prompt
- `MOTHERFUCKER/ESSAY_TO_VISUAL_WORKFLOW.md` — end-to-end workflow
- `MOTHERFUCKER/infinite_learned_film_pack/visual_program.json` — validated 44-shot example
