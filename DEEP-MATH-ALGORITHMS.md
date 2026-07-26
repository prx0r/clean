# Deep Math Algorithms — Directly Importable into GLSL

## 1. Gielis Superformula (Supershape)

**Source:** Johan Gielis, "A generic geometric transformation that unifies a wide range of natural and abstract shapes" (American Journal of Botany, 2003)

**The formula:**
```
r(θ) = (|cos(m·θ/4)/a|^n₂ + |sin(m·θ/4)/b|^n₃)^(-1/n₁)
```

6 parameters produce an enormous range of shapes:
- **m**: symmetry (3=triangle, 4=square, 5=pentagon, etc.)
- **n₁, n₂, n₃**: curvature (0.1 → spiky, 1 → rounded, 5 → pinched)
- **a, b**: size/aspect ratio

```glsl
// Gielis Superformula — ~10 lines of GLSL
float gielis(float theta, float m, float n1, float n2, float n3, float a, float b) {
    float mt4 = m * theta * 0.25;
    float cosTerm = pow(abs(cos(mt4) / a), n2);
    float sinTerm = pow(abs(sin(mt4) / b), n3);
    return pow(cosTerm + sinTerm, -1.0 / n1);
}

// Generates: circles (m=4, n1=n2=n3=2), stars (m=5, n1=0.5), 
// squares (m=4, n1=100), triangles (m=3, n1=100)
// flowers (m=7, n1=0.3, n2=n3=0.8)
// Also approximates many biological forms — cells, leaves, petals

// Map our 6D vector to Gielis parameters:
// D₄ (consonance) → m (symmetry) — more consonant = higher symmetry
// D₂ (VL smoothness) → n₁ (primary curvature)
// D₆ (entropy) → n₂, n₃ (detail curvature)
// D₁ (movement) → a, b (size/aspect)

// In the shader:
float m = 2.0 + D4 * 8.0;     // 2-10 fold symmetry
float n1 = 0.5 + D2 * 4.5;    // 0.5-5.0 curvature
float n2 = 0.3 + D6 * 5.7;    // 0.3-6.0 detail
float n3 = 0.3 + D6 * 5.7;    // same
float a = 0.5 + D1 * 0.5;     // 0.5-1.0
float b = a;                   // keep aspect square
```

---

## 2. L-Systems (Lindenmayer Systems)

**Source:** Aristid Lindenmayer, "Mathematical models for cellular interaction in development" (1968)

**Core idea:** Rewrite strings recursively using production rules. The string is interpreted as turtle graphics commands. Produces fractals, branching structures, plant forms.

**The simplest L-system for nāḍī branching:**
```
Axiom: X
Rules: X → F+[[X]-X]-F[-FX]+X
       F → FF
Interpretation: F=forward, +=left 25°, -=right 25°
                [=push state, ]=pop state
```

```glsl
// L-system renderer in GLSL — generates branching nāḍī network
// Uses string rewriting to produce the branching pattern
// Then interprets the string as turtle graphics commands
// Renders the result as SDF curves

// For real-time GLSL, we don't do string rewriting (too slow).
// Instead: precompute L-system as array of line segments, pass to GLSL.
// OR: use the L-system's fractal dimension directly:

// Fractal dimension of branching:
// D = log(N) / log(1/r) where N = number of branches, r = scaling factor
// For nāḍī system: D = log(72000) / log(1/0.5) ≈ 16.1
// This means 72,000 nadis at 1/2 scale each

// L-system for nāḍī network (precomputed, not real-time):
struct LSegment {
    vec2 start, end;
    float thickness;
    int depth;          // 0 = sushumna, 1 = ida/pingala, 2+ = branching
    int chakraId;       // which chakra this connects to
};

// The branching angle follows Doczi's golden angle: 137.5°
// The length ratio follows Ghyka's Fibonacci: each branch is 0.618 of parent
// The depth limit is 7 (for 72,000 nadis: 3 main × 5 branches × 5 sub × 5 × 5 × 5)

// Simplified: use recursive SDF instead of string rewriting
float nadiSDF(vec2 p, vec2 root, float angle, float length, int depth, float thickness) {
    if (depth <= 0) {
        // Render as SDF capsule
        vec2 tip = root + vec2(cos(angle), sin(angle)) * length;
        return sdCapsule(p, root, tip, thickness);
    }
    
    // Branch at golden angle
    float branchAngle = 137.5 * 3.14159 / 180.0;
    float newLength = length * 0.618;  // φ reciprocal
    
    float d1 = nadiSDF(p, root, angle + branchAngle, newLength, depth - 1, thickness * 0.618);
    float d2 = nadiSDF(p, root, angle - branchAngle, newLength, depth - 1, thickness * 0.618);
    
    return min(d1, d2);  // union of branches
}
```

**Alternative: Reaction-diffusion instead of L-systems.** RD grows organic patterns without explicit programming. Our approach: use RD to grow the nāḍī network, then L-systems or SDFs for the structural backbone (sushumna, chakras). RD is ~40 lines. L-systems are useful for the hierarchy (which chakra connects to which).

---

## 3. Fractal Geometry (Mandelbrot, Julia, IFS)

**Source:** Benoit Mandelbrot, "The Fractal Geometry of Nature" (1982)

```glsl
// Mandelbrot set — generates infinitely complex boundary from simple rule
int mandelbrot(vec2 c, int maxIter) {
    vec2 z = vec2(0.0);
    for (int i = 0; i < maxIter; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if (dot(z, z) > 4.0) return i;
    }
    return maxIter;
}
// Color the nāḍī field by iteration count at each point

// Julia set — each point gets its own Mandelbrot
int julia(vec2 z, vec2 c, int maxIter) {
    for (int i = 0; i < maxIter; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if (dot(z, z) > 4.0) return i;
    }
    return maxIter;
}
// The Julia parameter `c` maps to our emotional state
// C = [D₄*2-1, D₃*2-1] maps consonance+flow → Julia seed

// Escape-time coloring gives the "infinite detail" look
// Perfect for the tattvic descent — each zoom level reveals new tattvas

// Iterated Function Systems (IFS) — fractal flames
// Barnsley fern — organic leaf patterns
// Sierpinski triangle — triangular chakra geometry
// Use for: nāḍī detail, chakra ornamentation, background texture
```

---

## 4. Reaction-Diffusion (Gray-Scott Model)

**Source:** Alan Turing, "The Chemical Basis of Morphogenesis" (1952)
**Popularized by:** Karl Sims, "Reaction-Diffusion Tutorial" (1994)

```glsl
// Gray-Scott reaction-diffusion — 30 lines GLSL
// Two chemicals A and B, feed rate f, kill rate k
// Pattern depends only on (f, k):

// Coral growth:     f=0.0545, k=0.062
// Mitosis (cells):  f=0.0367, k=0.0649
// Maze channels:    f=0.029,  k=0.057
// Spots:            f=0.030,  k=0.062
// Worms:            f=0.078,  k=0.061
// Holes:            f=0.050,  k=0.062
// Solitons:         f=0.018,  k=0.051

// Our 6D vector maps feed/kill rates:
// f = 0.02 + D₆ * 0.06    (entropy → feed)
// k = 0.05 + (1-D₄) * 0.02 (consonance → kill)
// D₅ → orientation (anisotropic diffusion direction)
// D₂ → curl flow strength (chemicals drift along flow field)

// Two-pass: simulation pass (update A,B) + render pass (color by A-B)
// 30 lines of GLSL for the simulation
// ~40 lines for the render pass
```

---

## 5. Phyllotaxis (Spiral Patterns)

**Source:** Vogel's model of sunflower spiral (1979)

```glsl
// Vogel's phyllotaxis — golden angle spiral
// Generates seed patterns, chakra distributions, nāḍī endpoints
vec2 phyllotaxis(int n, float spread) {
    float angle = float(n) * 137.508 * 3.14159 / 180.0;  // golden angle in radians
    float radius = spread * sqrt(float(n));
    return vec2(radius * cos(angle), radius * sin(angle));
}

// Use for: chakra positions on the body, nāḍī endpoints on limbs
// 7 chakras at n = [0, 1, 3, 6, 10, 15, 21] (triangular numbers)
// 72,000 nadis at n = [0..71999]

// The golden angle (137.508°) produces optimal packing
// Same angle appears in: sunflowers, pinecones, nautilus shells
// Maps to our tattvic descent — each n is a tattva level
```

---

## 6. Strange Attractors (Chaos Theory)

**Source:** Edward Lorenz (1963), Otto Rössler (1976)

```glsl
// Lorenz attractor — butterfly-shaped strange attractor
// Maps to: prana flow, kundalini path through nadis
vec3 lorenz(vec3 state, float dt, float sigma, float rho, float beta) {
    float dx = sigma * (state.y - state.x);
    float dy = state.x * (rho - state.z) - state.y;
    float dz = state.x * state.y - beta * state.z;
    return state + vec3(dx, dy, dz) * dt;
}
// sigma=10, rho=28, beta=8/3 → classic butterfly
// The path of the attractor IS the kundalini path through the spine
// Render: accumulate past positions as trails = nāḍī channels

// Clifford attractor — 4-parameter chaos
vec2 clifford(vec2 p, float a, float b, float c, float d) {
    return vec2(
        sin(a * p.y) + c * cos(a * p.x),
        sin(b * p.x) + d * cos(b * p.y)
    );
}
// Each (a,b,c,d) gives a different attractor shape
// Maps to: different nāḍī patterns (ida, pingala, sushumna)
```

---

## 7. Cellular Automata

**Source:** Stephen Wolfram, "A New Kind of Science" (2002)

```glsl
// Rule 30 — generates complex patterns from simple 1D rule
// Use for: nāḍī surface texture, background animation
bool rule30(bool left, bool center, bool right) {
    // The 8-bit rule 30: 00011110
    int index = (int(left)<<2 | int(center)<<1 | int(right));
    return bool((30 >> index) & 1);
}

// Conway's Game of Life — 2D cellular automaton
// Use for: particle system on nāḍī surface, "alive" network feeling
// Slower — need compute shader or multi-pass for performance

// Cyclic cellular automata — spiral waves
// Perfect for: chakra vortex animation, prana flow visualization
```

---

## Summary: What to Actually Import

| Algorithm | Lines | Use in our GLSL | Source |
|---|---|---|---|
| **Gielis Superformula** | 10 | Generate organic shapes from 6D vector | Gielis (2003) |
| **Reaction-Diffusion** | 30 | Grow nāḍī networks organically | Turing (1952), Sims (1994) |
| **L-system SDF** | 20 | Structural backbone (sushumna, chakras) | Lindenmayer (1968) |
| **Phyllotaxis** | 5 | Chakra positions, nāḍī endpoints | Vogel (1979) |
| **Mandelbrot/Julia** | 10 | Infinite detail in tattvic descent | Mandelbrot (1982) |
| **Strange Attractors** | 15 | Kundalini path, prana flow | Lorenz (1963), Rössler (1976) |
| **Doczi ratios** | 10 | Harmonic proportions in composition | Doczi (1981) |

**Total: ~100 lines of GLSL. Each does something visually distinct that nothing else in our current pipeline does.** This is the complete math library for the Spanda Framework.
