# Build Review — 27 Jul 2026

## Framework

| Metric | Count |
|---|---|
| Kernel modules | 20 `.mjs` |
| Source modules | 25 (geometry: 7, particles: 5, materials: 3, audio: 2, capabilities: 1, load-capability: 1, core: 6) |
| Capability packs | 17 (base, human-anatomy, yogic-subtle-body, neurocognition, invariant-composition, scientific-diagrams, data-visualization, systems-dynamics, temporal-processes, embodied-phenomenology, textual-scholarship, tantric-cosmology, comparative-epistemology, pathkit-geometry, particle-fields, audio-reactive, tantric-geometry) |
| Style packs | 6 (mineral-manuscript, ritual-gold, luminous-subtle-body, technical-neural, visionary-midnight, ash-and-ember) |
| Tests | 7 (framework: 5, pack integration: 2, added: pathkit-geometry, particles, audio-features) |
| Shipped films | 6 (infinite-learned, song-no-singer, stones-are-watching, corbin-world-between-worlds, 2 compositions) |

## Hermes Film Pipeline — Proven

### Versions

| Version | Essay | Mechanisms | Quality |
|---|---|---|---|
| v3 | Crowley (magician) | 7 unique, 5x wave-ocean | Poor — no diversity |
| v4 | Crowley (magician) | 12 unique, 0 repeats | Good — max-2 rule fixed repetition |
| v5 | Alchemy | 12 unique, 3 packs used | Best — argument IR, geometry+anatomy packs |

### R2 uploads
- `blog-video-assets/hermes-v3.mp4` — first proper Hermes run
- `blog-video-assets/hermes-v4.mp4` — 12 unique, 0 repeats
- `blog-video-assets/hermes-v5.mp4` — Alchemy, geometry+anatomy, argument IR
- `blog-video-assets/hermes-reactive-audio.mp4` — audio-reactive constraint-field demo

## What Works

- ✅ Hermes produces valid scene packs with proper JSON
- ✅ Hermes follows the 12-step protocol (argument IR → continuity → mechanisms → render)
- ✅ Argument IR has roles, relations, source/target states, invariants, misreadings
- ✅ Mechanism diversity enforced by max-2 rule
- ✅ Multi-pack usage (base + geometry + anatomy)
- ✅ Skia renderer on RTX 3060: ~1min for 1000 frames vs ~13min on CPU
- ✅ Audio reactivity wired into renderer env
- ✅ All 7 existing tests pass

## Issues

1. **Audio duration mismatch** — Hermes estimates scene durations from word count at 155wpm, but TTS output is slower. Scene durations need to match actual narration timing.
2. **Audio-reactive video has no audio** — `renderVideo()` produces silent video. Audio must be muxed as a separate step.
3. **Skill enforcement gaps** — Hermes sometimes skips the argument IR step or defaults to keyword matching. The skill needs stricter failure conditions.
4. **PathKit geometry underused** — Only 2 of 3 geometry pack mechanisms were used in v5. Hermes defaults to base pack.
5. **No integration test for the full Hermes pipeline** — Each Hermes run is ad-hoc with manual reviewing.

## Next Priorities

1. Fix audio timing: generate TTS first → analyse → compile durations from actual audio length
2. Add audio mux step to the skill as mandatory
3. Add a `hermes test` command that runs a known essay and validates the output
4. Improve geometry pack usage visibility in the skill
5. Wire audio reactivity into more mechanisms (beyond constraint-field)
