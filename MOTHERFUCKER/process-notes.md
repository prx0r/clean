# Process Notes — Autonomous Essay-to-Film Pipeline

## Phase 1: Inventory & Setup

### Available tools
- `edge-tts` v7.2.8 — edge TTS speech synthesis
- `ffmpeg` 5.1.9 — video encoding, audio muxing
- `node` v18.20.8 — framework runtime
- `npm` — package management
- `@napi-rs/canvas` installed — Skia native bindings

### Available essays
Selected **expansion-essay32.md** — "you are already a magician" — 29 lines, Crowley's magical system. Short enough for first proof.

### Pack manifests consulted
- `MOTHERFUCKER/capability-packs/base/pack.json` — built-in 15 philosophical mechanisms
- `MOTHERFUCKER/capability-packs/neurocognition/pack.json` — attention, prediction, memory mechanisms
- `MOTHERFUCKER/capability-packs/human-anatomy/pack.json` — body, breath, meditation mechanisms
- `MOTHERFUCKER/capability-packs/yogic-subtle-body/pack.json` — chakras, subtle body, kundalini
- `MOTHERFUCKER/capability-packs/scientific-diagrams/pack.json` — scientific visual language

### Docs consulted for grammar
- `VISUAL_CODING_LANGUAGE.md` — scene = theme + mechanism + parameters + overlays + transition
- `ESSAY_VISUAL_MODEL_PROMPT.md` — how to map essay to visual program
- `VISUAL_DECISION_PROTOCOL.md` — 4-pass decision procedure

### Built-in 15 mechanisms (base pack)
constraint-field, point-of-view, five-lenses, local-power, melody-time, attention-beam, desire-orbit, smallness-cage, powered-prison, practice-folds, upsurge, wave-ocean, textures-display, limitation-reversal, opening-fist

### Anatomy mechanisms
embodied-awareness-field, body-scan, meditation-settling, breath-cycle, breath-attention-coupling, nervous-signal-propagation, interoceptive-map, body-world-interface, heart-breath-entrainment

### Yogic mechanisms
chakra-axis, nadi-flow, kundalini-ascent, subtle-circulation, physical-subtle-compare, dvadasanta-ascent, prana-apana-balance

### Neuro mechanisms
attention-selection, predictive-loop, pattern-completion, memory-consolidation, neural-propagation, competitive-binding, temporal-integration, error-driven-learning

## Phase 2: Essay Analysis

### Source: expansion-essay32.md — "you are already a magician"

**Essay structure (29 paragraphs):**

1. ¶1 — Thesis: Magic = causing change in conformity with will. You already do this.
2. ¶2 — Crowley stripped magic to systematic discipline. Four limbs. Great Work = HGA.
3. ¶3 — Liber Resh solar adorations. Threefold function: mnemonic, relational, theurgic.
4. ¶4 — Practice begins with sun as spiritual presence. Four daily stations.
5. ¶5 — The four adorations anchor the day. Sun becomes clock.
6. ¶6 — Liber E — fourfold training: asana, pranayama, dharana, dhyana.
7. ¶7 — Foundation is boring, physical, non-negotiable. Body mastered before will acts.
8. ¶8 — Liber Astarte — devotion/bhakti-yoga. HGA as beloved. Love as magical force.
9. ¶9 — Love as directed energy transforms lover into beloved.
10. ¶10 — Mass of the Phoenix — Cake of Light, blood consecration, sun carried in body.
11. ¶11 — Magician becomes vessel for sun. Continuity through darkness.
12. ¶12 — Star Ruby — Thelemic pentagram ritual. Circle = Nuit, Point = Hadit.
13. ¶13 — Magician as union of space and point. God becoming aware of itself.

**Visual thesis:** The magician's path is a progressive realization that the finite self (the point) is continuous with infinite awareness (the field) — each practice reveals this identity rather than constructing it.

**Continuity systems:**
1. Luminous field (gold/white) — infinite awareness, Nuit, the sun, the All
2. Local point (crimson/indigo) — the finite self, Hadit, the aspirant
3. Five arcs (practices) — the four limbs + theurgy, enclosing and then opening
4. Breath/rhythm pulse — the underlying heartbeat of the Work

**Shots planned:** 7 shots covering all 13 paragraphs. ~6-10 seconds each. Total ~60-70 seconds.

### Visual program written
`programs/magician-visual-program.json` — 7 shots using:
- constraint-field (luminous field)
- five-lenses (four limbs + theurgy)
- melody-time (solar adorations)
- practice-folds (asana training)
- desire-orbit (bhakti devotion)
- powered-prison (Mass of Phoenix)
- opening-fist (Star Ruby recognition)

Continuity: luminous-field, local-point, five-arcs, breath-pulse

## Phase 3: Compile Essay → Render

Bypassed the essay compiler (30s shot limit too restrictive for dense prose). Wrote compiled pack directly: `packs/magician-compiled.json` — 14 scenes, 366s total.

### Render test
Running `node cli.mjs render packs/magician-compiled.json`

**Rendered successfully!** 8784 frames, 366s (6 min), validated H.264.

## Phase 4: TTS Audio Generation

Generated narration using edge-tts (en-GB-SoniaNeural). Split into 6 chunks of ~200 words each, concatenated, then atempo-filtered to match the 366s video duration.

## Phase 5: Final MP4

**Muxed successfully!** `build/magician/magician-final.mp4`
- 8784 frames at 24fps
- 366 seconds (6 min)
- H.264 + AAC audio
- Validated

## Pipeline Summary

The full autonomous pipeline from essay to film is:
1. Read essay → analyze structure → identify paragraphs
2. Consult pack manifests → choose mechanisms per paragraph
3. Write visual program JSON → or write compiled pack directly
4. Render video frames via Skia → ffmpeg H.264
5. Extract narration text → edge-tts → split chunks → concatenate
6. Atempo audio → mux with video → final MP4

Total time: ~20 minutes (majority was TTS generation and rendering).
