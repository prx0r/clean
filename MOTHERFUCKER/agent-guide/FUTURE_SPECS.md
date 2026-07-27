# Future Specifications

## Visual IR

Introduce a backend-independent visual intermediate representation:

```text
Node
Edge
Path
Field
Emitter
Constraint
Material
Layer
Mask
Operator
Transition
Invariant
SignalRoute
```

Skia, SVG, CanvasKit, GLSL and WebGPU can consume the same IR.

## Pack compiler

Compile:

```text
capability manifests
+ style profile
+ composition profile
+ signal routes
→ resolved scene program
```

## Agent-readable registry

Generate one machine-readable capability index containing:

- mechanism descriptions;
- relation types;
- parameters;
- motion proofs;
- compatible assets;
- style compatibility;
- audio-route compatibility;
- examples;
- known failure modes.

## Visual review agent

Input:

- scene intention;
- frame strip;
- continuity rules;
- audio/narration values.

Output:

- observations;
- failed tests;
- target mechanism;
- proposed parameter patch;
- confidence.

## Timeline checkpoints

Persist particle and temporal state at scene boundaries to permit deterministic
targeted rerenders without replaying the complete film.
