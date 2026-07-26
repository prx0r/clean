# Beautify GLSL — Five Visual Grammars

The PIL packs define conceptual choreography only. The GLSL versions deliberately
replace their original paper-white diagram language with five independent worlds.

| Pack | Visual grammar | Motion language | Light and material |
|---|---|---|---|
| 01 · Life Crosses Barriers | Quantum volumetrics | probability mist, barrier caustics, tunnelling filaments | spectral cyan, ultraviolet and proton-gold in deep space |
| 02 · Beliefs Create Biology | Living stained glass | breathing membranes, migrating intentions, cellular refraction | wine-dark cytoplasm, violet glass, gold cognition |
| 03 · Voice Inside the Chest | Abyssal bioluminescent anatomy | peristaltic ribbons, neural plankton, vagal signal tides | black teal, electric cyan, serotonin amber |
| 04 · Dreams Create Worlds | Wet dream-watercolor | pigment blooms, paper diffusion, morphing washes | indigo, rose, moonlit cobalt and translucent pearl |
| 05 · Time Is Produced by Forgetting | Temporal geometry | slicing planes, recursive clocks, gold discontinuities | obsidian, antique gold, cold cyan; ink dissolution at boundaries |

All shaders share `include/primitives.glsl` for deterministic noise, SDF geometry,
antialiasing, glow, compositing and tone mapping. Pack-specific libraries define
materials and motion without changing the common uniform contract:

```glsl
uniform vec2 iResolution;
uniform float u;
uniform float t;
uniform float u_audioVolume;
uniform float u_audioBeat;
```
