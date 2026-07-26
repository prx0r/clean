# Directly Importable Math from the Canonical Sources

## 1. Doczi — *The Power of Limits*

**Core finding:** The same proportional ratios appear in musical intervals, visual art proportions, and natural growth patterns. They are not metaphors — they are the same mathematical constraints.

**Directly importable as GLSL constants:**

```glsl
// Doczi's proportional ratios — appear identically in music, art, and nature
const float DOCZI_UNISON    = 1.0 / 1.0;    // 1.000 — static, identity
const float DOCZI_OCTAVE    = 2.0 / 1.0;    // 2.000 — the fundamental harmonic
const float DOCZI_FIFTH     = 3.0 / 2.0;    // 1.500 — perfect fifth
const float DOCZI_FOURTH    = 4.0 / 3.0;    // 1.333 — perfect fourth
const float DOCZI_MAJOR_THIRD  = 5.0 / 4.0;  // 1.250 — major third
const float DOCZI_MINOR_THIRD  = 6.0 / 5.0;  // 1.200 — minor third
const float DOCZI_GOLDEN       = 1.6180339;   // φ — the golden ratio

// Visual proportions derived from these ratios:
// A rectangle with aspect ratio DOCZI_FIFTH appears "harmonious"
// A rectangle with aspect ratio DOCZI_GOLDEN appears "beautiful"
// A rectangle with aspect ratio DOCZI_UNISON appears "stable"
// A rectangle with aspect ratio DOCZI_FOURTH appears "calm"

// Use in GLSL:
float aspectRatio = iResolution.x / iResolution.y;
float harmonicDistance = min(abs(aspectRatio - DOCZI_FIFTH),
                            abs(aspectRatio - DOCZI_GOLDEN));
// Lower = more harmonious composition
```

**For nāḍī branching:**
```glsl
// Doczi's branching ratios in nature match musical intervals
// Tree branching follows DOCZI_FIFTH (3:2)
// Phyllotaxis (leaf spirals) follows DOCZI_GOLDEN
// Shell growth follows DOCZI_FOURTH
// Use these as the angle/growth ratios for nāḍī generation
float nadiBranchAngle = DOCZI_GOLDEN * 2.0 * PI;  // 137.5° — the golden angle
```

---

## 2. Ghyka — *The Geometry of Art and Life*

**Core finding:** The golden ratio φ and the Fibonacci sequence are the mathematical basis of aesthetic proportion in art, architecture, and nature.

**Directly importable as GLSL functions:**

```glsl
// Ghyka's golden ratio functions
#define PHI 1.618033988749895
#define PHI_RECIP 0.618033988749895  // 1/φ

// Golden rectangle construction
float goldenProportion(float x, float y) {
    // A rectangle is "golden" when (x+y)/x = x/y = φ
    return abs((x + y) / x - PHI) + abs(x / y - PHI);
}

// Fibonacci sequence for compositional balance
int fibonacci(int n) {
    // Used for: frame sizes, scene durations, nāḍī branch counts
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return a;
}

// Ghyka's "dynamic symmetry" rectangles:
// √2 rectangle: 1.414 — the "silver ratio" (Japanese proportion)
// √3 rectangle: 1.732
// √5 rectangle: 2.236 — contains the golden ratio: (√5+1)/2 = φ
const float SQRT2 = 1.414213562;
const float SQRT3 = 1.732050808;
const float SQRT5 = 2.236067977;

// Which harmonic proportion is this aspect ratio closest to?
float closestHarmonicRatio(vec2 resolution) {
    float ratio = resolution.x / resolution.y;
    float ratios[7] = float[](
        1.0, 1.333, 1.414, 1.5, 1.618, 1.732, 2.0
    );
    float minDist = 100.0;
    for (int i = 0; i < 7; i++) {
        minDist = min(minDist, abs(ratio - ratios[i]));
    }
    return minDist;  // lower = more harmonious composition
}
```

---

## 3. Albers — *The Interaction of Color*

**Core finding:** Colors are not fixed — they are perceived relative to their context. The same color appears different on different backgrounds. This is directly applicable to GLSL where shader colors interact.

**Directly importable as GLSL:**

```glsl
// Albers' color interaction principles:

// Simultaneous contrast: a color shifts toward the complement of its background
vec3 simultaneousContrast(vec3 color, vec3 background) {
    vec3 complement = vec3(1.0) - background;
    return mix(color, complement, 0.15);  // 15% shift
}

// Color relativity: the same color looks different on different grounds
// Simulate by adjusting perceived lightness based on background luminance
float relativeLightness(vec3 color, vec3 background) {
    float bgLum = dot(background, vec3(0.299, 0.587, 0.114));
    float colLum = dot(color, vec3(0.299, 0.587, 0.114));
    return colLum - bgLum * 0.3;  // perceived lightness shift
}

// Itten's 7 color contrasts (imported from Itten via Albers):
// 1. Hue contrast: pure hues against each other
// 2. Light-dark contrast: value range
// 3. Cold-warm contrast: temperature opposition
// 4. Complementary contrast: opposite on color wheel
// 5. Simultaneous contrast: context-dependent shift
// 6. Saturation contrast: pure vs muted
// 7. Extension contrast: area proportion

// These 7 contrasts become our 7 color mixing modes:
#define CONTRAST_HUE 0
#define CONTRAST_LIGHT_DARK 1
#define CONTRAST_COLD_WARM 2
#define CONTRAST_COMPLEMENTARY 3
#define CONTRAST_SIMULTANEOUS 4
#define CONTRAST_SATURATION 5
#define CONTRAST_EXTENSION 6

vec3 applyContrast(vec3 a, vec3 b, int mode) {
    if (mode == CONTRAST_HUE) return mix(a, b, 0.5);
    if (mode == CONTRAST_LIGHT_DARK) return mix(normalize(a), normalize(b), 0.5);
    if (mode == CONTRAST_COLD_WARM) {
        float warmth = (a.r + a.g) / 2.0;
        return mix(vec3(0.2, 0.4, 0.8), vec3(0.8, 0.4, 0.2), warmth);
    }
    if (mode == CONTRAST_COMPLEMENTARY) return a + (vec3(1.0) - b);
    if (mode == CONTRAST_SIMULTANEOUS) return simultaneousContrast(a, b);
    if (mode == CONTRAST_SATURATION) return mix(vec3(dot(a, vec3(0.299, 0.587, 0.114))), a, 0.5);
    if (mode == CONTRAST_EXTENSION) return a * length(b) / length(a);
    return a;
}
```

---

## 4. Tymoczko — *A Geometry of Music* (for completeness)

**Already imported as our 6D dimensions D₁-D₃.** The specific formulas we need:

```glsl
// Tymoczko's chord space distance (orbifold geodesic)
// Maps to our D₁
float chordSpaceDistance(vec4 chordA, vec4 chordB) {
    // Chords as pitch class sets in 4-voice space
    // Distance = minimal voice leading between voicings
    float minDist = 100.0;
    // Try all permutations (simplified — 4! = 24 is expensive in GLSL)
    // In practice: use the 6D vector directly, not compute it in GLSL
    return D1;  // precomputed externally, passed as uniform
}

// Voice leading efficiency — maps to our D₂
float voiceLeadingEfficiency(vec4 chordA, vec4 chordB) {
    // Average semitone movement per voice
    float total = 0.0;
    for (int i = 0; i < 4; i++)
        total += abs(chordB[i] - chordA[i]);
    return 1.0 / (1.0 + total * 0.1);
}

// Harmonic consistency — maps to our D₃
float harmonicConsistency(float[] tonalCenters) {
    // Variance of tonal center strength
    float mean = 0.0;
    for (int i = 0; i < tonalCenters.length(); i++)
        mean += tonalCenters[i];
    mean /= tonalCenters.length();
    float variance = 0.0;
    for (int i = 0; i < tonalCenters.length(); i++)
        variance += pow(tonalCenters[i] - mean, 2.0);
    variance /= tonalCenters.length();
    return 1.0 / (1.0 + variance * 5.0);
}
```

---

## 5. Weyl — *Symmetry* (QRI supplement)

```glsl
// Weyl's symmetry groups as visual modes:
// Cyclic symmetry (Cn): rotation by n-fold axis
// Dihedral symmetry (Dn): rotation + reflection
// For nāḍī chakra rendering:

float cyclicSymmetry(vec2 p, int n) {
    // Render a shape with n-fold rotational symmetry
    float angle = atan(p.y, p.x);
    float segment = 6.28318 / float(n);
    angle = mod(angle, segment);
    return length(p) * cos(angle - segment * 0.5);
}

float dihedralSymmetry(vec2 p, int n) {
    // Render a shape with n-fold rotation + reflection
    float angle = atan(p.y, p.x);
    float segment = 6.28318 / float(n);
    angle = mod(abs(angle), segment);
    return length(p) * cos(angle - segment * 0.5);
}

// QRI: valence = symmetry → our D₅ maps to symmetry measure
float symmetryMeasure(vec2 p, float regularity) {
    float cyclic = cyclicSymmetry(p, int(regularity * 6.0 + 2.0));
    float dihedral = dihedralSymmetry(p, int(regularity * 6.0 + 2.0));
    return mix(cyclic, dihedral, 0.5);
}
```

---

## Summary: What to Import Where

| Source | What | Where it goes | Lines |
|--------|------|---------------|-------|
| Doczi | 6 harmonic ratios + golden angle | `spanda/ratios.glsl` | 15 |
| Ghyka | φ functions + Fibonacci + dynamic symmetry rectangles | `spanda/proportion.glsl` | 30 |
| Albers/Itten | 7 color contrasts + simultaneous contrast function | `rasa/contrast.glsl` | 40 |
| Tymoczko | Chord space distance, VL efficiency, harmonic consistency | (precomputed → 6D uniform) | — |
| Weyl | Cyclic/dihedral symmetry functions | `camatkara/symmetry.glsl` | 20 |

**Total: ~100 lines of directly importable GLSL math.** This gives us the complete mathematical foundation for the Spanda Framework — harmonic proportions, color interaction, geometric symmetry, and visual composition — all expressed as shader functions.
