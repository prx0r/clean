# PathKit Geometry Guide

The framework can now compute with paths rather than only drawing them.

Included capabilities:

- contour resampling and morphing;
- offset contours;
- boolean operations when exposed by the installed wrapper;
- trimming, dashing, stroking and simplification;
- radial and dihedral symmetry;
- lotus, yantra, mandala, flame and aureole generators;
- perceptual color interpolation;
- offscreen compositing;
- deterministic particles;
- offline audio analysis.

Run `tools/probe-canvas-capabilities.mjs` before assuming all underlying Skia
features are exposed by the installed `@napi-rs/canvas` version.
