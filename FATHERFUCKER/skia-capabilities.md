# Skia Capabilities via @napi-rs/canvas

Our framework uses `@napi-rs/canvas` which wraps Skia's C++ API for Node.js.

## Available rendering primitives (from SkPaint/SkCanvas)

### Blend Modes (SkBlendMode)
Porter-Duff: Clear, Src, Dst, SrcOver, DstOver, SrcIn, DstIn, SrcOut, DstOut, SrcATop, DstATop, Xor, Plus
Lighten/Darken: Modulate, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn, HardLight, SoftLight, Difference, Exclusion, Multiply
Color: Hue, Saturation, Color, Luminosity

### Shaders (SkShader)
- Linear gradient
- Radial gradient
- Two-point conical gradient
- Sweep gradient
- Bitmap pattern (clamp, repeat, mirror)
- Fractal Perlin noise
- Turbulence Perlin noise
- Compose shader

### Mask Filters (SkMaskFilter)
- Blur (for glow, shadow effects)

### Color Filters (SkColorFilter)
- Color matrix (4x5)
- Color table

### Path Effects (SkPathEffect)
- Dash path effect
- Discrete path effect (random chops + displacement)
- Corner path effect (rounding)
- 1D path effect (replicate along path)
- 2D path effect (stamp lattice)
- Compose/Sum path effects

### Transform (SkMatrix)
- 3×3 matrix: translate, rotate, scale, skew, perspective
- Canvas save/restore stack

### Text (SkFont)
- Typeface, size, scale, skew
- MeasureText, getTextBounds, glyph access

## What we already use
- Radial gradients (glow orbs, rings)
- Linear gradients (attention field)
- Blur (glowing paths)
- Matrix transforms (body frame transforms)
- Canvas save/restore

## What we DON'T yet use (useful for style profiles)
- Perlin noise shaders (turbulence/fractal for texture density)
- Blend modes beyond normal alpha (screen, overlay, multiply for compositing)
- Color matrix filters (tone mapping per scene)
- Discrete path effect (randomization controlled by seed + density)
- Dash path effect (parameterized rhythm)
- Sweep/conical gradients (radial color distribution)
- Compose shaders (layered procedural textures)
- Path ops (union, intersection, difference for geometry)

## Style profile integration points
Each 6D vector component could modulate:
- metamorphosis → discrete path effect amount, transform animation speed
- continuity → trace persistence, morph smoothness, material conservation
- centricity → radial gradient strength, lens/attractor pull, figure-ground hierarchy
- coherence → palette concord, phase locking, blend mode selection
- periodicity → dash pattern rhythm, pulse regularity, transition duration
- density → spatial frequency, nesting depth, node count, particle count
