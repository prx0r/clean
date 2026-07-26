# Review — Time Is Produced by Forgetting

## Evidence

- Source visual functions: 24
- GLSL shaders: 24
- Spec validation: pass; 24 composition records and 10 primary visual verbs
- Static audit: 24/24
- `glslangValidator`: 24/24
- Headless WebGL 2 renders: 24/24 at all three states

Render states:

- latent: `u=.18`, `t=1.1`, volume `.16`, beat `.00`, 240×135;
- mature: `u=.72`, `t=3.6`, volume `.48`, beat `.56`, 240×135;
- resolved: `u=.94`, `t=8.6`, volume `.78`, beat `.90`, 240×135.

## Contact-sheet findings

- The central argument reads directly: simultaneous spectral paths are narrowed
  by cyan shutters into a rail, leaving gold traces behind and open branches
  ahead.
- Desire, fear, boredom, flow, memory, tense, measurement, contraction, music,
  and recognition each deform temporal relation in a distinct way.
- The clock comparison uses a rigid lattice rather than a literal clock face.
- The finitude scene is a quiet abstract terminal horizon with no person,
  victim, injury, or graphic imagery.
- Low-to-high renders show actual changes in access, branching, dilation,
  retention, and field integration.
- High-audio states preserve line detail without white clipping.

## Revisions after render

- The new pack shares its slug with the numbered archive reference pack. The
  harness originally treated every `--pack` value as a substring and therefore
  audited both directories together.
- Updated the harness to prefer an exact normalized pack-name match and retain
  substring matching only as fallback. The final pack result is now reported
  unambiguously as 24/24.

## Intentional risk

Spectral ribbons recur because they are the simultaneous field from which
sequence is produced. Shutters, traces, branches, grids, gaps, braids, gates,
and boundaries repeatedly change their topology so the ribbons carry temporal
history rather than becoming background decoration.
