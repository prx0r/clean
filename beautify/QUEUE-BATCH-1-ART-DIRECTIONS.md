# Queue Batch 1 — Art Directions

This batch contains 93 original fragment shaders across five essays. The PIL
packs define the conceptual beats; the GPU work deliberately invents a different
visual world for each essay.

## Shared standard

- Every scene is an independently addressable fragment shader.
- Every scene responds to `u`, `t`, `u_audioVolume`, and `u_audioBeat`.
- `u` controls conceptual revelation, not just opacity.
- Motion combines continuous time with beat-triggered accents so quiet narration
  remains alive and musical moments can bloom without breaking composition.
- All pack-specific renderers build on `beautify-archive/lib/visionary.glsl`.
- The shared vocabulary includes layered noise, Voronoi fields, spectral palettes,
  Fresnel response, signed-distance geometry, raymarch cameras, glow filaments,
  tonemapping, and analytic antialiasing.

The architecture was informed by LYGIA's composable organization of generative,
SDF, lighting, simulation, and color functions. The implementations here are
original and specialized to these essays.

## 1. Noctilucent palimpsest cartography

`a-dream-becomes-a-world-when-it-remembers-where-you-were`

Memory behaves like luminous geography written on translucent night. Contour
lines drift, paths recur with small mutations, constellations become landmarks,
and erased places remain as atmospheric pressure. The visual system favors
layered spatial memory over literal illustration.

## 2. Liquid-metal sacred catoptrics

`a-mirror-becomes-sacred-when-it-stops-reflecting-only-you`

Reflection is treated as an active optical material. Kaleidoscopic folds,
anisotropic highlights, thin-film spectral shifts, caustic rings, and black
mirror depths turn the frame into a ritual instrument rather than a flat mirror.

## 3. Phononic aurora and cymatic calligraphy

`a-name-teaches-the-invisible-how-to-answer`

Names enter as pressure and resonance. Interference bands, vocal filaments,
cymatic nodes, glyph-like standing waves, and auroral harmonics make language
feel physically capable of organizing the invisible. Audio uniforms affect the
field topology as well as brightness.

## 4. Raymarched numinous relic

`a-ritual-object-teaches-matter-to-remember-heaven`

The object is a changing mineral presence: hollowed octahedral mass, orbiting
bands, procedural gold veins, internal inscriptions, soft shadow, Fresnel edge
light, and emissive apertures. Its geometry and material history unfold with the
essay rather than merely swapping icons.

## 5. Impossible living temple

`a-temple-teaches-space-how-to-become-a-body`

Sacred space becomes a traversable organism. A raymarched corridor of columns,
arches, gates, sanctum shells, city forms, circumambulatory rings, and a luminous
axis is joined by volumetric shafts and resonant fog. Plan-view overlays let the
same architecture become compass, procession, body map, and returning city.

## Review result

The five packs do not share a palette swap or a single scene template. Two use
distinct raymarched worlds; three use separate field grammars. Their common
identity comes from cinematic contrast, sub-pixel structure, restrained bloom,
and animation that advances the argument. Shader compilation is enforced by the
render harness for every scene.
