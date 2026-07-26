# Rasa Framework — GLSL as Aesthetic Cognition

## The Core Claim

From Biernacki's *The Matter of Wonder* and the Tantraloka extractions:

> *"The group of principles (tattvas) is made of the aesthetic rapture (camatkāra) of consciousness."* — Tantraloka Vol.1

The 36 tattvas are not things. They are **degrees of wonder**. Śiva is infinite wonder. Earth is contracted wonder. The emanation of reality is an aesthetic process — the rasa (aesthetic delight) of Śiva's inherent freedom manifesting as degrees of intensity.

From Biernacki's analysis: camatkāra is not merely a human response to beauty. It is the **ontological signature of reality itself**. When you experience wonder, you are not having a subjective feeling about an objective world — you are **consciousness recognizing itself** in its own manifestation.

This gives us a radically different foundation for a GLSL framework.

---

## The Framework Structure

Not a color palette. Not a motion library. A **complete visual-philosophical pipeline** where every shader stage encodes a specific stage of aesthetic-spiritual cognition.

### Layer 1: Spanda — The Pulse

The fundamental oscillation. Not audio reactivity — the pulse of consciousness itself.

From Tantraloka Āhnika 7:

> *"The pulsation (spanda) of consciousness is the nature, the root cause of the activity of the senses."*

The base layer of every shader should be a **spanda function** — a pulse that is not a sine wave but the actual structure of conscious rhythm. The three moments: emission (udaya), abiding (sthiti), withdrawal (laya). Every visual pulse follows this three-part structure.

```glsl
// Spanda structure
float spanda(float t, float frequency) {
    // Three moments: udaya (rising), sthiti (abiding), laya (dissolving)
    float phase = fract(t * frequency);
    float udaya = smoothstep(0.0, 0.33, phase);
    float sthiti = smoothstep(0.33, 0.66, phase) - smoothstep(0.66, 1.0, phase);
    float laya = 1.0 - smoothstep(0.66, 1.0, phase);
    return udaya * 0.33 + sthiti * 0.34 + laya * 0.33; // weighted sum
}

// The universal pulsation (sāmānyaspanda) — wave upon wave from the Heart
float samanyaSpanda(vec2 p, float t) {
    return spanda(t + length(p) * 0.5, 1.0);
}
```

### Layer 2: Tattvic Descent — Visual Intensity as Ontological Depth

The 36 tattvas are degrees of camatkāra. Each tattva has a visual density:

| Tattva Range | Visual Quality | Geometry | Color | Intensity |
|---|---|---|---|---|
| Śiva (36) | Pure light, undifferentiated | No geometry, full-screen gradation | White/gold | 1.0 |
| Śakti (35) | Wave, vibration | Single SDF, undulating | Pearl | 0.95 |
| Sadāśiva (34) | "I-this" polarity emerging | Two SDFs, mirroring | Gold/white | 0.90 |
| Īśvara (33) | Will to act | Directional SDFs, arcs | Amber | 0.85 |
| Śuddhavidyā (32) | Pure knowledge | Geometric patterns, grids | Cyan | 0.80 |
| Māyā (31) | Limitation, contraction | Bounded SDFs, frames | Indigo | 0.70 |
| Kalā (30) | Limited power | Segmented SDFs, fragments | Violet | 0.65 |
| ... | ... | ... | ... | ... |
| Pṛthvī (1) | Dense, solid, opaque | Complex SDFs, detailed geometry | Earth tones | 0.10 |

```glsl
// Tattva as visual density
struct TattvaState {
    float density;    // 0.0 (Śiva) to 1.0 (Earth)
    float camatkara;  // 1.0 (Śiva) to 0.0 (Earth) — degree of wonder
    vec3 baseColor;   // Color associated with this tattva
};

TattvaState tattvaAtLevel(int level) {
    // 1 = Earth, 36 = Śiva
    float t = float(level - 1) / 35.0; // 0..1
    return TattvaState(
        1.0 - t,           // density decreases as we go up
        t,                 // camatkāra increases as we go up
        tattvaColor(level) // spectral mapping
    );
}

// A shader that moves "up" the tattvas during a scene
TattvaState currentTattva(float sceneProgress) {
    int level = 1 + int(sceneProgress * 35.0);
    return tattvaAtLevel(clamp(level, 1, 36));
}
```

### Layer 3: Sādhāraṇīkaraṇa — The Universalization Pipeline

The process of stripping personal/emotional context so the universal flavor appears. This is the **core visual process**:

| Stage | Visual Action | Shader Implementation |
|---|---|---|
| **Vibhāva** (stimulus) | The scene's thesis appears as specific geometry | SDF renders a concrete form (hand, face, mountain, wave) |
| **Anubhāva** (response) | The geometry reacts, transforms | Audio reactivity, deformation, color shift |
| **Vyabhicāribhāva** (transient states) | Multiple geometry layers interplay | Multiple SDFs blend, compete, dissolve into each other |
| **Sādhāraṇīkaraṇa** (universalization) | Specific geometry dissolves into pure form | SDF domain warps, edges blur, specific → abstract |
| **Rasāsvadana** (tasting) | Pure aesthetic form; consciousness recognizes itself | Uninterrupted beauty, the form "makes sense" emotionally |
| **Camatkāra** (wonder) | The apex — consciousness recognizing itself | Full-screen dissolution into light; the geometry reveals its own structure |

```glsl
// Sādhāraṇīkaraṇa: strip the specific, reveal the universal
float sadharanikarana(float specificForm, float universalForm, float progress) {
    // As progress → 1.0, the specific dissolves into the universal
    return mix(specificForm, universalForm, smoothstep(0.6, 1.0, progress));
}

// Example: a hand (specific) dissolves into a mathematical curve (universal)
float handOrCurve(vec2 p, float progress) {
    float hand = sdHand(p);      // specific: a recognizable hand
    float curve = sdHeart(p);    // universal: the pure form of a heart curve
    return sadharanikarana(hand, curve, progress);
}
```

### Layer 4: The Nine Rasas — Emotional Modes

Each rasa is not a color. It's a **mode of the entire pipeline** — the way spanda, tattvic depth, and universalization interact:

| Rasa | Spanda quality | Tattvic range | Sādhāraṇīkaraṇa arc | Geometry language | Temporal arc |
|---|---|---|---|---|---|
| **Śṛṅgāra** (love) | Flowing, continuous, wave-like | Śakti → Sadāśiva (35-34) | Slow universalization, sustained relish | Curving, embracing SDFs, heart-like | Slow build, long sustain, gentle release |
| **Vīra** (heroic) | Expanding, rising, centrifugal | Īśvara → Śuddhavidyā (33-32) | Building to climax, sudden universalization | Ascending forms, expanding arcs, radial | Build → climax → resolution |
| **Karuṇā** (compassion) | Sinking, dissolving, decelerating | Sadāśiva → Māyā (34-31) | Gentle descent through tattvas, slow dissolve | Dissolving forms, falling shapes, veils | Gentle descent into stillness |
| **Raudra** (fury) | Explosive, jagged, staccato | Māyā → Kalā (31-30) | Sudden shattering, violent universalization | Fractured SDFs, jagged lines, shattering | Explosive burst, aftermath stillness |
| **Hāsya** (comic) | Bouncing, irregular, playful | Śuddhavidyā → Māyā (32-31) | Sudden reversals, unexpected universalization | Distorted SDFs, unexpected blends | Irregular, surprising |
| **Adbhuta** (wonder) | Expanding outward, concentric, revealing | All tattvas simultaneously | Complete universalization, the ground revealed | Concentric waves, unfolding geometry, revelation of structure | Gradual revelation, sustained awe |
| **Bhayānaka** (terror) | Contracting, collapsing, accelerating | All tattvas → Pṛthvī (any → 1) | Rapid contraction, universalization as horror | Inward-spiraling, closing, consuming | Building dread, collapse |
| **Bībhatsa** (disgust) | Writhing, unstable, unpredictable | Lower tattvas (10-1) | Twisted universalization, forms corrupting | Morphing, twisting, unstable | Unsettling, no resolution |
| **Śānta** (peace) | Still, barely perceptible, dissolving | Śiva tattva (36) only | Already universal, nothing to strip | Minimal geometry, negative space, pure field | Still, sustained, dissolving into white |

```glsl
// Rasa drives the entire visual pipeline
struct RasaMode {
    float spandaSpeed;     // how fast the pulse
    float spandaShape;     // smooth vs jagged vs explosive
    int baseTattva;         // starting tattva level
    int peakTattva;         // where the arc peaks
    float universalizationRate; // how quickly the specific dissolves
    vec3(*colorFn)(float, float); // color response function
};

RasaMode rasaForScene(int sceneIndex) {
    // Each scene in a pack has a dominant rasa
    // The pack as a whole may traverse through rasas
    RasaMode rasas[9] = RasaMode[](
        RasaMode(0.3, 0.2, 34, 35, 0.2, sringaraColor),   // Śṛṅgāra
        RasaMode(0.6, 0.7, 32, 33, 0.5, viraColor),        // Vīra
        RasaMode(0.2, 0.1, 34, 31, 0.3, karunaColor),      // Karuṇā
        RasaMode(0.9, 0.9, 31, 30, 0.8, raudraColor),      // Raudra
        RasaMode(0.5, 0.6, 32, 31, 0.4, hasyaColor),       // Hāsya
        RasaMode(0.4, 0.3, 1, 36, 0.9, adbhutaColor),      // Adbhuta — traverses ALL tattvas
        RasaMode(0.8, 0.8, 30, 1, 0.7, bhayankaColor),     // Bhayānaka
        RasaMode(0.5, 0.5, 10, 1, 0.3, bibhatsaColor),     // Bībhatsa
        RasaMode(0.1, 0.0, 36, 36, 0.0, santaColor)        // Śānta — already at Śiva
    );
    return rasas[clamp(sceneIndex, 0, 8)];
}
```

### Layer 5: Pratibimbavāda — The Reflection Structure

From Tantraloka: all aesthetic savouring is a reflection of the one supreme rasa of consciousness within the mirror of the Lord's freedom.

> *"That is a reflection, like the form of a face in a mirror, like taste (rasa) in saliva, smell in the nose, an erotic touch in the organ of touch, and an echo in the sky."*

The shader itself is a mirror. The geometry is not "real" — it's a reflection of consciousness in the medium of the screen. The viewer is not "seeing" something — they are **tasting their own consciousness reflected back**.

```glsl
// The mirror function: what you see is consciousness reflecting itself
vec3 pratibimba(vec3 sourceColor, vec3 mirrorTint, float reflectionStrength) {
    // Like taste in saliva, smell in nose — the reflection IS the experience
    return mix(sourceColor, sourceColor * mirrorTint, reflectionStrength);
}

// The echo: time as reflection of the timeless
float echo(float t, float decay) {
    float primary = spanda(t, 1.0);
    float reflection = spanda(t + 0.1, 1.0) * decay;
    float re_reflection = spanda(t + 0.2, 1.0) * decay * decay;
    return primary + reflection + re_reflection;
}
```

### Layer 6: Sāmarasya — The Resolution

The final state of any pack should be **sāmarasya** — the equal taste where all differentiated contents are integrated. Not by becoming identical, but by their difference no longer producing conflict.

> *"By abiding in their own innate and spontaneous aesthetic delight (svarasa), they have attained that state of oneness (sāmarasya) with the aesthetic delight of consciousness."*

In GLSL terms: all layers — spanda, tattvas, rasa, reflection — resolve into a single unified field. The final frame of a pack should be visually simple but inexhaustibly deep.

```glsl
// Sāmarasya: all layers resolve
vec3 samarasya(vec3 spandaField, vec3 tattvaColor, vec3 rasaColor, float resolution) {
    float s = smoothstep(0.8, 1.0, resolution);
    vec3 integrated = spandaField * tattvaColor * rasaColor;
    vec3 unified = normalize(integrated) * length(integrated); // normalize preserves difference while unifying
    return mix(integrated, unified, s);
}
```

---

## The Complete Shader Structure

```glsl
#include "lygia/math/decimate.glsl"
#include "lygia/sdf/circle.glsl"

#include "rasa/spanda.glsl"
#include "rasa/tattva.glsl"
#include "rasa/sadharanikarana.glsl"
#include "rasa/palette.glsl"
#include "rasa/mirror.glsl"
#include "rasa/samarasya.glsl"

void main() {
    // 1. Spanda — the pulse
    float pulse = samanyaSpanda(p, t);
    
    // 2. Tattva — ontological depth
    TattvaState tattva = currentTattva(u); // u = scene progress
    
    // 3. Rasa — emotional mode
    RasaMode mode = rasaForScene(currentScene);
    
    // 4. Sādhāraṇīkaraṇa — universalization
    float specific = renderSceneGeometry(p, u);
    float universal = renderUniversalForm(p, u);
    float form = sadharanikarana(specific, universal, u);
    
    // 5. Color = tattva color shaped by rasa
    vec3 col = mode.colorFn(t, pulse) * tattva.baseColor;
    
    // 6. Reflection — the mirror structure
    col = pratibimba(col, vec3(1.0, 0.95, 0.9), 0.3);
    
    // 7. Resolution
    col = samarasya(col, tattva.baseColor, mode.colorFn(t, pulse), u);
    
    fragColor = vec4(col, 1.0);
}
```

---

## How the 36 Tattvas Map to Visual Density

The deepest insight from Biernacki's analysis: the tattvas are not things but **degrees of camatkāra**. This maps directly to a shader parameter: the density of visual detail.

| Śaiva Tattva (36) | Pure wonder, no density, no boundary | Full-screen gradient, undifferentiated light |
|---|---|---|
| Śakti Tattva (35) | Wonder vibrating, first pulse | A single waveform across the screen |
| Sadāśiva Tattva (34) | "I-this" — the first distinction | Two-tone gradient, a horizon line |
| Īśvara Tattva (33) | Agency — direction emerges | A single vector, a ray, a direction |
| Śuddhavidyā Tattva (32) | Pure knowledge — distinction without limitation | A single geometric form, perfect |
| Māyā (31) | Limitation — the frame appears | A border, a frame, a bounded region |
| Kalā (30) | Limited power — fragmentation | Segmented forms, mosaic, fragments |
| Vidyā (29) | Limited knowledge — partial understanding | Partial forms, occluded shapes |
| Rāga (28) | Attachment — desire for specific forms | Organic attraction between forms |
| Kāla (27) | Time — sequence, before/after | Animated forms, trajectory trails |
| Niyati (26) | Necessity — cause and effect | Causal chains, linked forms |
| Puruṣa (25) | Individual soul — the witness | A central point, a perspective |
| Prakṛti (24) | Nature — the field of experience | Textured field, ground |
| Buddhi (23) | Intellect — discrimination | Sharp edges, clear boundaries |
| Ahaṅkāra (22) | Ego — "I" and "mine" | A labeled form, named shape |
| Manas (21) | Mind — discursive thought | Fragmenting, multiple shapes |
| 10 Senses (11-20) | Perception and action | Rays from center to periphery |
| 5 Tanmātras (6-10) | Subtle elements | Sound → touch → sight → taste → smell as visual gradients |
| 5 Mahābhūtas (1-5) | Gross elements | Earth: dense, textured, bounded |

A scene that moves up the tattvas goes from dense specific geometry → fewer, purer forms → undifferentiated light. A scene that moves down goes from pure light → contracting into specific form. This IS the emotional arc — adbhuta (wonder) traverses all 36, from Earth to Śiva.

---

## What This Framework Actually Provides

| Layer | File | What It Does |
|---|---|---|
| Spanda | `rasa/spanda.glsl` | Three-moment pulse (udaya/sthiti/laya), universal pulsation, echo structure |
| Tattva | `rasa/tattva.glsl` | TattvaState struct, tattvaAtLevel(), currentTattva(), tattvaColor() — visual density as ontological depth |
| Sādhāraṇīkaraṇa | `rasa/sadharanikarana.glsl` | The universalization pipeline: vibhāva → anubhāva → vyabhicāribhāva → rasāsvadana |
| Rasa | `rasa/mode.glsl` | RasaMode struct with spandaSpeed, tattvic range, universalization rate, color function |
| Pratibimba | `rasa/mirror.glsl` | Reflection structure, echo time, mirror function |
| Sāmarasya | `rasa/resolve.glsl` | Layer integration, resolution into unified field |

**This is not a color palette. It's a complete visual ontology:** the 36 tattvas as visual density, camatkāra as the aesthetic climax, sādhāraṇīkaraṇa as the universalization arc, rasas as emotional modes that shape the entire pipeline, spanda as the fundamental pulse driving everything.
