# Additive Engine — Integration Spec

## Status: Standalone — not yet merged into kernel

The `additives/` directory contains four new engine layers that were spec'd and built by ChatGPT in response to a capability review. They are **not yet integrated** into the main framework. This document describes what they are and how they would be merged.

## Current priority

Get the existing skill producing reliable essay films using the 4-pass decision protocol, continuity systems, and capability packs we already have. The additives should be integrated only after the foundation is solid.

## The four additive layers

### 1. Geometry Engine (`src/geometry/`)
Path2D boolean operations and procedural sacred geometry.

Files: `path-ops.mjs`, `path-utils.mjs`, `lotus-generators.mjs`, `yantra-generators.mjs`, `mandala-generators.mjs`, `flame-generators.mjs`, `symmetry.mjs`

**What it adds:** Path operations (union, intersect, difference, XOR), trimming, dashing, contour morphing, radial/dihedral symmetry, procedural lotus/yantra/mandala/flame construction.

**Integration:** Copy into `MOTHERFUCKER/src/geometry/`. Add `capability-packs/pathkit-geometry/` and `capability-packs/tantric-geometry/`. No kernel changes.

### 2. Particle System (`src/particles/`)
Deterministic particle engine usable by any pack.

Files: `particle-system.mjs`, `emitters.mjs`, `fields.mjs`, `constraints.mjs`, `renderers.mjs`

**What it adds:** Reusable particle kernel with point/line/path/ring/area emitters, flow/curl/orbital/spiral/attractor fields, inside-path/outside-path/within-body constraints, and orb/dash/spark/droplet/petal/bindu renderers.

**Integration:** Copy into `MOTHERFUCKER/src/particles/`. Add `capability-packs/particle-fields/`. Packs declare particle systems in their manifests. No kernel changes.

### 3. Audio Feature Bus (`src/audio/` + `tools/analyse-audio.py`)
Offline librosa analysis → deterministic per-frame feature manifest → Skia routing.

Files: `analyse-audio.py` (Python), `audio-features.mjs` (JS loader + envelope follower), `audio-router.mjs` (declarative feature→visual routing)

**What it adds:** 12 audio channels (RMS, onset, beatPulse, localPulse, harmonicEnergy, percussiveEnergy, spectralCentroid, spectralBandwidth, spectralFlatness, chroma, tonnetz, F0). Attack/release envelope followers. Declarative routing table mapping features to visual parameters.

**Integration:** `analyse-audio.py` is standalone (runs once per audio file, outputs JSON). `audio-features.mjs` loads the manifest. The renderer would need a small change in `renderer.mjs` to pass audio features into the `env` object so mechanisms can read them. This is the only kernel touch-point.

### 4. Materials System (`src/materials/`)
Perceptual color, conic gradients, compositing layers.

Files: `materials.mjs`, `color.mjs` (Oklab), `layer-stack.mjs`

**What it adds:** Oklab perceptual color interpolation, conic gradient helper, radial glow helper, palette ramp generator, layer compositing stack (combine geometry + pigment + glow + particles + text as separate composited layers).

**Integration:** Copy into `MOTHERFUCKER/src/materials/`. No kernel changes. Existing primitives can use these helpers.

### 5. Style Packs (`style-packs/`)
Material/presentation profiles orthogonal to capability packs.

Files: `mineral-manuscript.json`, `ritual-gold.json`, `luminous-subtle-body.json`, `technical-neural.json`, `visionary-midnight.json`, `ash-and-ember.json`

**What it adds:** Named material profiles that can be selected per-project alongside capability packs.

**Integration:** Register as a new resource type. The renderer would need to resolve material profiles into the rendering pipeline. This requires more kernel integration than the other layers.

## Integration order (when ready)

1. **Geometry engine** — zero risk, no kernel changes
2. **Materials system** — zero risk, no kernel changes
3. **Particle system** — zero risk, no kernel changes
4. **Audio feature bus** — minimal kernel change (pass env.audio to mechanisms)
5. **Style packs** — moderate kernel change (material profile resolution)

## Quick test

```bash
cd MOTHERFUCKER/additives/MOTHERFUCKER
npm install
node tools/probe-canvas-capabilities.mjs
pip install -r requirements-audio.txt
python3 tools/analyse-audio.py ../path/to/audio.wav build/features.json
```

## Reference

- `PATHKIT_GEOMETRY_GUIDE.md` — geometry engine usage
- `VISUAL_ENGINE_PHASES.md` — build phases
- `examples/audio-reactive-nadi.mjs` — combined audio+particles+nadi example
- `packs/pathkit-visionary-demo.json` — demo pack using all layers
