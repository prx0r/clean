# Future Engine — Cross-Modal Style & Composition Layer

## Status: Speculative — parked for later

The 6D vector engine (metamorphosis, continuity, centricity, coherence, periodicity, density) was an experiment in cross-modal style control. Proof of concept exists in `FATHERFUCKER/6d-vector-engine/` — it generated music scores from state vectors and drove GLSL visuals. The visual outputs were not good enough to ship.

## What we learned

- The concept of a shared state space driving visual + music + narrative parameters is valid
- 6D vectors are too few dimensions for reliable visual quality
- The Skia integration path (mapping vectors to path effects, blend modes, densities) is theoretically sound but needs a better parameterization model
- Style profiles (named 6D trajectories like `meditative`, `scientific`, `tantric`) remain a useful abstraction but depend on the vector→renderer mapping being right

## What it would take to revive

1. A better mapping from high-level parameters to low-level Skia renderer knobs
2. Validation that the 6D space produces visually distinguishable and desirable outputs
3. Integration with the capability pack system so style profiles can modulate mechanism parameters per-scene
4. A way to author style profiles without needing to understand the rendering pipeline

## Reference material

- `FATHERFUCKER/6d-vector-engine/` — composition.json, engine.py, generate_score.py, analyses, transmissions
- `FATHERFUCKER/skia-capabilities.md` — Skia blend modes, shaders, filters, path effects available for parameterization
- `MOTHERFUCKER/capability-packs/invariant-composition/` — composition-level visual theorems

## Current priority

Getting the foundation working properly with our existing image/capability packs. The future engine layer should not block shipping the core framework.
