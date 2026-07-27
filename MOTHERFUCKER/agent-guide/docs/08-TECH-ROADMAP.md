# Technical Roadmap

## Required now

- `@napi-rs/canvas`;
- FFmpeg;
- Python;
- librosa;
- deterministic JSON feature manifests;
- capability-aware loader;
- offscreen layers;
- particle checkpoints for targeted rerenders.

## Useful next

### Forced alignment

For narration timing:

- WhisperX;
- Montreal Forced Aligner;
- Gentle;
- TTS word-boundary events.

Export one common narration manifest format.

### Score analysis

Use MIDI event data rather than inferred waveform features for:

- motif entries;
- carrier transfers;
- voice count;
- formal boundaries;
- tonal hierarchy.

### Image masks

Support PNG/SVG masks for:

- body silhouettes;
- deity iconography;
- manuscript fragments;
- regional clipping.

### Vector ingestion

- SVG import;
- Lottie/Skottie;
- font glyph outlines;
- traced public-domain iconographic assets.

### Advanced rendering backends

Only after the Skia foundation is proven:

- CanvasKit for more Skia APIs;
- custom Rust/Node bindings;
- WebGPU;
- GLSL backend;
- Three.js for genuine 3D.

The IR should remain backend-independent.
