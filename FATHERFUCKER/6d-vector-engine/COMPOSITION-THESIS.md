# The Unified Composition Thesis

## One Pipeline, One Emotional Source, Two Outputs

The insight: **Visuals and music are the same thing in different media.** Both express the same emotional/archetypal source. They shouldn't be generated separately and synced afterward — they should emerge from the same coordinates.

---

## The Complete Pipeline

```
ESSAY TEXT (the raw material)
  │
  ├──→ Research Object (themed passages)
  ├──→ Truth Map (what questions does this answer?)
  └──→ Emotional Arc (valence, arousal, tension over time)
        │
        ▼
    EMOTIONAL COORDINATES (5D vector per scene)
        │
        ├── Valence (-1 to 1)    — positive/negative
        ├── Arousal (-1 to 1)    — calm/excited  
        ├── Control (-1 to 1)    — in control/overwhelmed
        ├── Transcendence (-1 to 1) — mundane/spiritual
        └── Tension (0 to 1)     — relaxed/tense
        │
        ├── MAPS TO RASA MODE (nearest archetype)
        │     ┌──────────────┬───────────┬──────────┐
        │     │ Valence High │ Arousal Hi│ → Vīra  │
        │     │ Valence High │ Arousal Lo│ → Śānta │
        │     │ Valence Low  │ Arousal Hi│ → Raudra│
        │     │ Tension High │ Control Lo│ → Bhaya │
        │     └──────────────┴───────────┴──────────┘
        │
        ├──► VISUAL PIPELINE                    ├──► AUDIO PIPELINE
        │                                         │
        ├── Spanda (pulse frequency)               ├── Tempo (BPM)
        │   = arousal × tempo_range                │   = arousal × 120 + 60
        │                                         │
        ├── Tattva (visual density)                ├── Harmonic complexity
        │   = 1 - transcendence                    │   = valence × 5 + 3
        │   (Śiva = transparent, Earth = dense)    │   (simple → complex chords)
        │                                         │
        ├── Sādhāraṇīkaraṇa (universalization)     ├── Voice leading
        │   = tension arc                          │   = control × smoothness
        │   (specific → abstract over time)        │   (jerky → smooth transitions)
        │                                         │
        ├── Curl flow (prana movement)             ├── Melodic motion
        │   = arousal × noise_field                │   = conjuct melodic M₁(v)
        │   (fast flow = high energy)              │   (stepwise → leaps)
        │                                         │
        ├── RD pattern (nāḍī growth)               ├── Chord spacing / voicing
        │   = tension × feed_kill_rate             │   = density_to_voicing M₅(v)
        │   (coral → maze → spots)                 │   (tight → spread)
        │                                         │
        ├── Rasa color palette                     ├── Timbre / orchestration
        │   = rasa_mode → signature_colors         │   = timbre_vector matching
        │   (śānta = pearl/white)                  │   (strings → brass)
        │                                         │
        ├── Camatkāra climax                       ├── Cadence / resolution
        │   = peak transcendence moment            │   = authentic cadence
        │   (geometry → pure light)                │   (V7 → I resolution)
        │                                         │
        ├── SignatureTiming (4-stage arc)          ├── Phrase structure
        │   = enter/disclose/transform/resolve     │   = golden ratio phrases
        │   (matches sādhāraṇīkaraṇa)              │   (Fibonacci lengths)
        │                                         │
        └── Audio reactivity                       └── Visual reactivity
            = narration → u_audioVolume                = chord changes → scene transitions
```

---

## The 8 Mapping Functions

Every visual parameter has a direct musical analog. Both are driven by the same 5 emotional coordinates.

| # | Visual Parameter | → | Musical Parameter | Math |
|---|---|---|---|---|
| **M₁** | Movement speed | → | Conjunct melodic motion | `M₁(v) = (1 - chaos) × speed_norm` |
| **M₂** | Geometric alignment | → | Harmonic consistency | `M₂(v) = alignment × 12` (chord quality) |
| **M₃** | Intensity stability | → | Voice-leading efficiency | `M₃(v) = (alignment + stability) / 2` |
| **M₄** | Color hue | → | Pitch circulation / key | `M₄(v) = hue × 12/360` (circle of fifths) |
| **M₅** | Particle density | → | Chord spacing / voicing | `M₅(v) = density × 4 + 2` (notes per chord) |
| **M₆** | Chaos level | → | Rhythmic complexity | `M₆(v) = chaos × 16` (Euclidean pulses) |
| **M₇** | Brightness | → | Spectral centroid / timbre | `M₇(v) = brightness × 8000 Hz` |
| **M₈** | Tension arc | → | Harmonic rhythm / cadence | `M₈(v) = tension × phrase_length` |

---

## The Combined Output

A single pack produces, for each frame:

```
FRAME n:
  ├── Visual (GLSL fragment shader)
  │     ├── RD field (nāḍī pattern at frame n)
  │     ├── Curl flow direction vectors
  │     ├── SDF geometry (sushumna, chakras, body)
  │     ├── Signature style overlay (nodes, ribbons, echoes)
  │     └── Post-processing (cinemaFinish bloom)
  │
  ├── Audio (generated MIDI / synthesized)
  │     ├── Chord: [root, quality, extensions] from M₂, M₄
  │     ├── Melody: [note, velocity, duration] from M₁, M₃
  │     ├── Rhythm: [pulse pattern] from M₆
  │     ├── Timbre: [instrument, register] from M₇
  │     └── Form: [phrase, cadence] from M₈
  │
  └── Narration (audio file)
        └── Drives u_audioVolume, u_audioBeat for both
```

---

## The GLSL ↔ Audio Bridge

The shader runs on GPU. The audio runs on CPU/DAW. They stay in sync because:

1. **Same random seed** for procedural generation (deterministic)
2. **Same time variable `t`** for frame-accurate synchronization
3. **Same emotional coordinates** for scene-level structure

```glsl
// GLSL side — renders one frame
void main() {
    float t = sceneTime;  // seconds since scene start
    float u = sceneProgress;  // 0→1
    
    // Emotional coordinates from essay analysis
    float valence = 0.7;      // positive
    float arousal = 0.3;      // calm
    float tension = 0.5;       // moderate
    
    // These produce both:
    // Visual: slow ribbons, warm colors, medium density
    // Audio: 90 BPM, major chords, strings
}
```

---

## What We Have vs What's Missing

| Component | Status | File |
|---|---|---|
| Visual pipeline (SDF, flow, signature style) | ✅ Built | `signature.glsl`, `cinema.glsl`, `primitives.glsl` |
| Visual timing (4-stage arc) | ✅ Built | `SignatureTiming` struct |
| Reaction-diffusion (organic growth) | ❌ Missing | ~40 lines GLSL |
| Audio → visual mapping (Tymoczko) | 📄 Spec'd | `universal music thesis.txt` |
| Archetype → emotion mapping | 📄 Spec'd | `translation layer.txt` |
| Audio generation engine | ❌ Missing | JavaScript/Python implementation |
| Unified pipeline (text → emotional arc → AV) | ❌ Missing | The orchestrator |
| Rasa → emotional coordinates mapping | 📄 Partial | `RASAFRAMEWORK.md` |

---

## The Build Order

1. **RD in GLSL** — Gray-Scott reaction-diffusion (40 lines, one afternoon)
2. **RD + flow coupling** — curlFlow pushes RD chemicals (20 lines)
3. **Rasa → emotion mapping table** — 9 rasas → 5D emotion coordinates (one page)
4. **Tymoczko audio engine** — JavaScript class that generates MIDI from visual params (the music thesis implementation)
5. **Archetype detector** — text → emotion → nearest archetype (the translation layer)
6. **Unified orchestrator** — the thing that runs both pipelines from one input
