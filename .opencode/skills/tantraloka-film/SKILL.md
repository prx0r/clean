---
name: tantraloka-film
description: |
  Use ONLY when the user asks to create a visual film/essay companion from a philosophical essay using the Tantraloka Skia framework.
  Provides tools for essay analysis, visual program creation, Skia rendering, TTS narration, and final MP4 assembly.
  Works with files under MOTHERFUCKER/.
---

# Tantraloka Skia Essay-Film Framework

Deterministic motion-graphics framework at `MOTHERFUCKER/`. Turns essays into narrated visual films by communicating **relations through motion** — not a slideshow of noun illustrations.

## Non-negotiable order

Do not collapse passes. Choosing a visual while summarizing a paragraph makes the first association feel inevitable and produces literal, repetitive films.

1. Read the complete source.
2. Build a visual-free argument IR (roles, relations, states, invariants).
3. Identify continuity systems and invariants.
4. Select composition structure.
5. Activate capability packs.
6. Generate at least three mechanism candidates per beat.
7. Select by relation preservation and motion proof.
8. Apply geometry, material, motion and style profiles.
9. Route music and narration signals independently.
10. Validate and render review frames.
11. Repair failed mechanisms only.
12. Render final video and mux audio.

## Mechanism selection rubric

Score every candidate on: relation preservation, topology, temporal order, invariant preservation, silent legibility, domain appropriateness, epistemic integrity, novelty relative to adjacent scenes.

Reject any candidate that is merely beautiful and interchangeable.

## Hard failures

- missing pack activation;
- unsupported mechanism;
- unregistered theme;
- non-deterministic output;
- arbitrary symbol substitution;
- biomedical and symbolic models collapsed;
- scene legible only through its title;
- narration printed as caption.

## Planning output

Produce before writing any scene JSON:

```json
{
  "central_claim": "",
  "audience_transformation": {
    "initial_model": "",
    "destabilization": "",
    "recognition": "",
    "aftertaste": ""
  },
  "continuity_systems": [],
  "composition_profile": "",
  "required_capabilities": [],
  "style_profile": "",
  "signal_strategy": {}
}
```

## Available mechanism packs

Read manifests at `MOTHERFUCKER/capability-packs/*/pack.json`.

**Base** (15): constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist

**Human-anatomy**: embodied-awareness-field, body-scan, meditation-settling, breath-cycle, breath-attention-coupling, nervous-signal-propagation, interoceptive-map, body-world-interface, heart-breath-entrainment

**Neurocognition**: attention-selection, predictive-loop, pattern-completion, memory-consolidation, neural-propagation, competitive-binding, temporal-integration, error-driven-learning

**Invariant-composition**: transformation-invariance, carrier-transfer, causal-memory, derivative-trajectory, lead-lag-counterpoint, conservation-filter, semantic-transition, polyphonic-identity, recognition-transaction, climax-assimilation, structural-homology, constraint-tournament

**PathKit-geometry**: lotus-unfold, yantra-construction, mandala-entry

## Pack types

| Type | What it answers |
|---|---|
| Capability pack | What relation or domain can be shown? |
| Style pack | How should it feel? |
| Composition pack | Why does this event follow the previous? |
| Signal pack | Which audio/narration feature controls which visual? |

Never place all four responsibilities in one theme.

## Scene format

```json
{
  "id": "sc01",
  "title": "Beat name (2-80 chars)",
  "subtitle": "Interpretive sentence (2-140 chars)",
  "term": "IAST term (1-50 chars)",
  "devanagari": "देवनागरी",
  "motif": "semantic-essay",
  "duration": 6.0,
  "params": { "visual": "mechanism-id", "caption": "Short label" },
  "styleProfile": null,
  "materialProfile": null,
  "motionProfile": null,
  "signalRouting": null
}
```

## Render

```bash
cd MOTHERFUCKER
# Base mechanisms:
node cli.mjs render packs/pack.json --out build/film.mp4
# Custom packs (with capabilityPack field):
node -e "import('./tools/render-pack.mjs').then(m=>m.main('./packs/pack.json'))"
```

## TTS + Mux

```bash
edge-tts --voice en-GB-SoniaNeural -f narration.txt --write-media chunk.mp3
ffmpeg -f concat -safe 0 -i concat.txt -c copy full.mp3
ffmpeg -i video.mp4 -i full.mp3 -c:v copy -filter:a "atempo=RATIO" -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

## Narration rules

When narration is dense: reduce particle emission, simplify background motion, preserve main explanatory geometry, keep continuity objects present.
When narration withdraws: allow the visual process to complete, do not automatically fade to black.

## Reference docs

- `MOTHERFUCKER/VISUAL_DECISION_PROTOCOL.md` — 4-pass protocol
- `MOTHERFUCKER/VISUAL_CODING_LANGUAGE.md` — grammar
- `MOTHERFUCKER/ESSAY_VISUAL_MODEL_PROMPT.md` — agent prompt
- `MOTHERFUCKER/agent-guide/agent-skill/SKILL.md` — improved skill
- `MOTHERFUCKER/infinite_learned_film_pack/visual_program.json` — validated 44-shot example
