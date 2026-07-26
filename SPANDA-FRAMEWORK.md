# Spanda Framework v1 — The Unified Synthesis

## The Single Axiom

**Reality is vibration. Consciousness is not a thing — it is a pulse.**

From Dyczkowski's translation of Tantraloka, Āhnika 7:

> *"The rhythm of sensory activity, the pulse of conjunction and separation of the senses with their objects, is essentially the pulse — spanda — of consciousness."*

From Tymoczko's *A Geometry of Music* (2011):

> *"Chords are points in a geometric space (orbifold). Voice leading is a continuous path between these points."*

These are the same statement. The pulse of sensory activity (spanda) IS the voice leading path through geometric space. Sound, color, form, and feeling are all the same vibration at different frequencies.

---

## The 6D Spanda Vector

A 6-dimensional vector that fully describes any moment of experience:

| Dim | Name | Source | What it measures | Range |
|-----|------|--------|------------------|-------|
| D₁ | Chord Geometry | Tymoczko | Geometric distance between successive chords in orbifold space | 0 (static) → 1 (maximal movement) |
| D₂ | Voice Leading | Tymoczko | Smoothness of note-to-note transitions | 0 (jagged) → 1 (smooth) |
| D₃ | Harmonic Flow | Tymoczko | Consistency of tonal center via PageRank centrality | 0 (wandering) → 1 (stable) |
| D₄ | Consonance | QRI/STV | Symmetry of frequency ratios (Pythagorean consonance) | 0 (dissonant) → 1 (consonant) |
| D₅ | Regularity | QRI | Temporal symmetry / rhythmic stability | 0 (irregular) → 1 (regular) |
| D₆ | Entropy | QRI | Combined structural + harmonic information content | 0 (simple) → 1 (complex) |

**The 6D vector IS the spanda state at a given moment.** The entire experience — sound, color, form, feeling — is encoded in these 6 numbers.

---

## The Tattvic Overtones

The 36 tattvas of Tantraloka ARE the harmonic series. Each tattva is an overtone of consciousness:

| Tattva | Level | Harmonic Ratio | Consonance | Visual Quality |
|--------|-------|----------------|------------|----------------|
| Śiva | 36 | 1:1 (fundamental) | 1.0 | Pure light, no geometry |
| Śakti | 35 | 2:1 (octave) | 0.95 | Single waveform |
| Sadāśiva | 34 | 3:2 (perfect fifth) | 0.88 | Horizon line (I-This) |
| Īśvara | 33 | 4:3 (perfect fourth) | 0.82 | Directional ray |
| Śuddhavidyā | 32 | 5:4 (major third) | 0.78 | Single geometric form |
| Māyā | 31 | 6:5 (minor third) | 0.72 | Frame, boundary |
| ... | ... | ... | ... | ... |
| Pṛthvī | 1 | complex (dissonant) | 0.10 | Dense, textured, complex |

The tattvic level maps directly to D₄ (consonance). Śiva = D₄=1.0. Earth = D₄≈0.1.

---

## The Rasa Modes as 6D Regions

Each rasa is a region of 6D space:

| Rasa | D₁ | D₂ | D₃ | D₄ | D₅ | D₆ | Emotion |
|------|-----|-----|-----|-----|-----|-----|---------|
| Śānta | 0.2 | 0.9 | 0.9 | 0.9 | 0.9 | 0.2 | Peace |
| Adbhuta | 0.5 | 0.6 | 0.8 | 0.7 | 0.5 | 0.5 | Wonder |
| Vīra | 0.6 | 0.5 | 0.6 | 0.6 | 0.6 | 0.5 | Heroic |
| Śṛṅgāra | 0.3 | 0.8 | 0.7 | 0.8 | 0.6 | 0.3 | Love |
| Hāsya | 0.5 | 0.4 | 0.5 | 0.6 | 0.7 | 0.4 | Comic |
| Karuṇā | 0.3 | 0.6 | 0.6 | 0.5 | 0.4 | 0.4 | Compassion |
| Raudra | 0.8 | 0.2 | 0.2 | 0.2 | 0.2 | 0.8 | Fury |
| Bhayānaka | 0.7 | 0.3 | 0.2 | 0.3 | 0.3 | 0.7 | Terror |
| Bībhatsa | 0.6 | 0.3 | 0.3 | 0.3 | 0.3 | 0.6 | Disgust |

---

## The Unified Rendering

A composition is a sequence of 6D vectors over time. Each vector is rendered simultaneously by three parallel renderers:

### Visual Renderer (GLSL)

Reads the 6D vector and maps to:
- **D₁ → movement speed** (curl flow intensity)
- **D₂ → voice leading** = ribbon smoothness 
- **D₃ → harmonic flow** = nāḍī network coherence
- **D₄ → consonance** = tattvic density (Śiva → Earth visual density)
- **D₅ → regularity** = pulse stability (spanda regularity)
- **D₆ → entropy** = geometric complexity (SDF detail level)

Plus rasa-derived: color palette, nāḍī growth mode, timing arc.

### Audio Renderer (Tone.js/Tonal.js)

Reads the 6D vector and maps to:
- **D₁ → modulation index** (FM synthesis complexity)
- **D₂ → portamento** (voice leading smoothness)
- **D₃ → tonal stability** (key centricity)
- **D₄ → chord quality** (consonant → dissonant voicings)
- **D₅ → rhythmic pattern** (Euclidean rhythm regularity)
- **D₆ → harmonic complexity** (extensions, alterations)

Plus rasa-derived: tempo, instrumentation, cadence timing.

### Narrative Renderer (TTS)

Reads the 6D vector and maps to:
- **D₃, D₅ → pacing** (stable = slower delivery)
- **D₁, D₆ → emphasis** (complex = more deliberate)
- **D₄ → tone** (consonant = warmer voice)

Plus rasa-derived: emotional tone, pauses.

---

## The 6D Trajectory as Story

A composition's emotional arc IS a path through 6D space:

```json
{
  "composition": "recognition-is-not-in-time",
  "spanda_trajectory": [
    {"t": 0.0,  "v": [0.2, 0.9, 0.9, 0.9, 0.9, 0.2], "rasa": "santa"},
    {"t": 0.2,  "v": [0.4, 0.7, 0.7, 0.7, 0.6, 0.4], "rasa": "adbhuta"},
    {"t": 0.4,  "v": [0.8, 0.3, 0.3, 0.3, 0.3, 0.8], "rasa": "raudra"},
    {"t": 0.6,  "v": [0.3, 0.8, 0.8, 0.8, 0.7, 0.3], "rasa": "karuna"},
    {"t": 0.75, "v": [0.5, 0.7, 0.8, 0.8, 0.6, 0.4], "rasa": "adbhuta", "camatkara": true},
    {"t": 1.0,  "v": [0.2, 0.9, 0.9, 0.9, 0.9, 0.2], "rasa": "santa"}
  ]
}
```

This is the entire film. 6 numbers per moment. Everything else — the GLSL shader, the musical score, the narration — is a deterministic rendering of this trajectory.

---

## What Already Exists

| Component | File | Status |
|---|---|---|
| 6D vector extraction (Tymoczko + QRI) | `musictheory-3-chordonomicon6d.md` | Spec'd, validated against 666k songs |
| Rasa → 6D mapping | `SPANDA-FRAMEWORK.md` (above) | Defined |
| Tattva → harmonic ratio mapping | `musictheory-4-gemm-optic.md` | Defined from Dyczkowski translations |
| GLSL visual renderer | `signature.glsl` + `cinema.glsl` + `primitives.glsl` | ✅ Working, 39 packs |
| Audio renderer (Tymoczko M₁-M₈) | `COMPOSITION-THESIS.md` | Spec'd, formulas defined |
| Composition format | `COMPOSITION-FORMAT.md` | Spec'd |
| Gielis supershape for geometry | ~20 lines GLSL | ❌ Not yet ported |
| Reaction-diffusion for nāḍī growth | ~40 lines GLSL | ❌ Not yet written |

## The Name

**Spanda Framework**. Not "rasa framework" (too narrow), not "6D framework" (too technical). Spanda means vibration/pulse — the single phenomenon that expresses itself as sound, color, form, and feeling. One name for one framework.
