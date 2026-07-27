# GLSL Framework — Nanavira Time + Abhinavagupta Rasa

## The Idea

Two GLSL header files that encode philosophical structure directly into the shader language.

### nanavira.glsl — Temporal Logic

Nanavira's dynamic aspect describes moments that accelerate in infinite converging series, with three hierarchy levels (eternal invariant, regular interval, accelerating series), and the "squaring" of relative weights.

```glsl
// A thing endures for an infinity of moments, then transforms.
// Each moment is itself an infinite accelerating series.
// The present advances into the future and gains a dimension.

float nanaviraTime(float t, float hierarchyLevel) {
    // t = linear time
    // hierarchyLevel: 0 = eternal (O), 1 = regular (moments), 2 = accelerating (within moment)
    // Returns: the "lived" moment value according to Nanavira's hierarchy
    
    if (hierarchyLevel == 0.0) {
        return 0.0; // O is invariant — no change at this level
    }
    if (hierarchyLevel == 1.0) {
        return fract(t); // regular intervals — one unit per moment
    }
    // Level 2: accelerating series — each moment is a fraction of the previous
    // From Dynamic Aspect §5: "if each successive moment is a definite fraction
    // of its predecessor, the whole infinite series will come to an end"
    float acceleration = 0.5; // each moment half the previous
    float moment = 0.0;
    float scale = 1.0;
    for (int i = 0; i < 8; i++) {
        moment += sin(t * scale) / pow(2.0, float(i+1));
        scale *= 2.0;
    }
    return moment;
}

// From §8: Intensity/weight distribution
// 'this' has twice the intensity of 'that' (2:1 proportion)
// Consciousness of a thing while it endures is constant
vec3 nanaviraWeight(vec3 thisColor, vec3 thatColor, float thisIntensity) {
    float clamped = clamp(thisIntensity, 0.0, 1.0);
    float totalWeight = clamped * 2.0 / 3.0 + (1.0 - clamped) * 1.0 / 3.0;
    return mix(thatColor, thisColor, totalWeight);
}

// From §12: "However much the relative weights of the three 'that'
// may vary among themselves, the weight of 'this' remains constant"
float nanaviraInvariant(float thisWeight, vec3 thatWeights) {
    return thisWeight; // invariant regardless of distribution
}
```

### rasa.glsl — Aesthetic Visual Language

Abhinavagupta's rasa theory (from Nāṭyaśāstra + Abhinavagupta's commentary) defines 9 aesthetic emotions, each with a color, movement quality, and temporal feel.

```glsl
// The 9 Rasas mapped to visual palettes and motion qualities
// Based on Abhinavagupta's aesthetic theory

const vec3 RASA_SRINGARA = vec3(0.90, 0.30, 0.40);  // Love — rose/crimson, flowing
const vec3 RASA_HASYA   = vec3(0.95, 0.85, 0.30);  // Comedy — gold/yellow, bouncy
const vec3 RASA_KARUNA  = vec3(0.40, 0.50, 0.70);  // Compassion — blue-grey, sinking
const vec3 RASA_RAUDRA  = vec3(0.85, 0.15, 0.10);  // Fury — blood red, explosive
const vec3 RASA_VIRA    = vec3(0.80, 0.50, 0.15);  // Heroic — amber/orange, rising
const vec3 RASA_BAYANAKA= vec3(0.20, 0.20, 0.25);  // Terror — void black, jagged
const vec3 RASA_BIBHATSA= vec3(0.40, 0.55, 0.30);  // Disgust — olive/green, writhing
const vec3 RASA_ADBHUTA = vec3(0.50, 0.70, 1.00);  // Wonder — cyan/blue, expanding
const vec3 RASA_SANTA   = vec3(0.85, 0.90, 0.95);  // Peace — pearl/white, dissolving

// Motion quality per rasa
struct RasaMotion {
    float speed;       // 0=static, 1=explosive
    float turbulence;  // 0=smooth, 1=chaotic
    float direction;   // 0=inward (contemplative), 1=outward (expressive)
};

RasaMotion rasaMotion(int rasaIndex) {
    RasaMotion m[9] = RasaMotion[](
        RasaMotion(0.3, 0.2, 0.4),  // śṛṅgāra — flowing, gentle
        RasaMotion(0.5, 0.6, 0.5),  // hāsya — bouncy, light
        RasaMotion(0.2, 0.3, 0.3),  // karuṇā — sinking, heavy
        RasaMotion(0.9, 0.8, 0.8),  // raudra — explosive, outward
        RasaMotion(0.6, 0.4, 0.7),  // vīra — rising, expanding
        RasaMotion(0.8, 0.9, 0.2),  // bhayānaka — jagged, contracting
        RasaMotion(0.4, 0.7, 0.3),  // bībhatsa — writhing, unstable
        RasaMotion(0.7, 0.5, 0.9),  // adbhuta — expanding, wonder
        RasaMotion(0.1, 0.1, 0.1)   // śānta — still, dissolving
    );
    return m[rasaIndex];
}

// Generate palette from a primary rasa + transition to secondary
vec3 rasaBlend(vec3 primary, vec3 secondary, float blend, float time) {
    return mix(primary, secondary, 0.5 + 0.5 * sin(time * blend));
}
```

## How They Combine

A shader using both frameworks:

```glsl
#include "nanavira.glsl"
#include "rasa.glsl"

void main() {
    // Nanavira drives the temporal structure
    float livedTime = nanaviraTime(t, 2.0); // accelerating series
    
    // Rasa drives the visual palette and motion
    vec3 primaryRasa = RASA_SANTA;     // peace — the contemplative ground
    vec3 transitionRasa = RASA_ADBHUTA; // wonder — the recognition event
    RasaMotion motion = rasaMotion(4);   // vīra — heroic, rising
    
    // Combined: palette shifts with rasa transition
    vec3 col = rasaBlend(primaryRasa, transitionRasa, livedTime, t);
    
    // Motion follows rasa + nanavira hierarchy
    float oscillation = sin(livedTime * 2.0 * 3.14159 * motion.speed);
    col *= 0.8 + 0.2 * oscillation;
    
    // The invariant: consciousness of a thing while it endures is constant
    col = nanaviraWeight(col, vec3(0.0), 0.66); // 'this' has 2/3 weight
    
    fragColor = vec4(col, 1.0);
}
```

## What This Unlocks

| Layer | Current GLSL | With Framework |
|-------|-------------|----------------|
| Time | Linear `t` uniform | Hierarchical, accelerating, invariant — Nanavira's structure |
| Color | Hardcoded palettes | Rasa-driven with transitions — Abhinavagupta's aesthetics |
| Motion | Per-shader manual easing | Structured by rasa qualities + temporal hierarchy |
| Meaning | None | Every visual choice encodes philosophical structure |

The shaders wouldn't just LOOK like they're about consciousness. Their temporal structure would literally BE Nanavira's argument about time made visible.

---

## Implementation Plan

### nanavira.glsl
- `nanaviraTime(t, hierarchy)` — accelerated moment series
- `nanaviraWeight(thisColor, thatColor, intensity)` — 2:1 intensity distribution
- `nanaviraInvariant(weight, others)` — invariance under transformation
- `nanaviraTransform(t, mode)` — column/row/both interchange per §I/12
- `nanaviraIntensity(t)` — intensity distribution over time per §8

### rasa.glsl
- 9 rasa color constants with defined palettes
- `rasaMotion(index)` — motion quality per rasa
- `rasaBlend(primary, secondary, time)` — smooth transitions
- `rasaDominant(float[] weights)` — dominant rasa at current moment
- `rasaContrast(palette1, palette2)` — Abhinavagupta's virodhī (contrast) principle for tension

### Integration
- Place in `beautify-archive/lib/framework/` for shared use
- New packs `#include "framework/nanavira.glsl"` and `#include "framework/rasa.glsl"`
- Old packs can be updated incrementally
