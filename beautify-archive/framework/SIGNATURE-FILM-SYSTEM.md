# From Essay to Signature GLSL Film

## 1. The unit of design is an argument

Do not begin by selecting effects. Begin by reducing the essay to:

1. a one-sentence thesis;
2. a continuity invariant that can physically change;
3. a causal graph of sources, boundaries, channels, attractors, traces, and
   transformations;
4. a five-phase film arc;
5. one visible verb for every unique visual function.

The visual function is not a decorative illustration of a noun. It is a
transition that makes a claim testable at a glance.

## 2. The signature grammar

### Semantic primitives

| Primitive | What it means | Typical geometry |
|---|---|---|
| Field | total possibility or context | fog, particles, paper, manifold |
| Focus | finite selection | aperture, lens, cone, local phase lock |
| Agent | local competence | particle, cell, node, orbit |
| Boundary | exclusion or identity | membrane, shutter, frame, caustic seam |
| Channel | influence or transmission | filament, flowline, waveguide |
| Attractor | stable answer or habit | basin, orbit, crystalline contour |
| Trace | persistence after cause | echo, afterimage, hysteresis path |
| Witness | reflexive awareness | camera reveal, mirror fold, field containing lens |

### Visual verbs

Use exactly one primary verb per scene: `emerge`, `gather`, `split`, `exclude`,
`bind`, `transmit`, `remember`, `predict`, `repair`, `compare`, `dissolve`, or
`recognize`. Secondary motion may support it but must not compete with it.

### Causal topologies

Choose the topology before writing GLSL:

- field → focus;
- source → channel → target;
- visible state ↔ counterfactual state;
- competing attractors;
- distributed consensus;
- part ↔ whole;
- trace → reactivation;
- nested scales;
- paired manifolds;
- sequence inside simultaneity.

If the thesis cannot be drawn as one of these relationships, the scene is not
yet understood.

## 3. Five-phase film arc

1. **Latent** — establish the world and continuity material.
2. **Formation** — show the mechanism that creates the ordinary state.
3. **Stress** — let conflict, error, limit, or comparison deform the system.
4. **Revision** — introduce correction or a wider model.
5. **Integration** — return to earlier matter in a changed, more inclusive form.

Not every visual function appears in chronological order, but each must declare
one of these phases and one scene role: `establish`, `perturb`, `disclose`,
`model`, `contrast`, `deepen`, `reverse`, `test`, `caution`, `integrate`, or
`coda`.

## 4. Essay-type routing

| Essay structure | Preferred film grammar | Avoid |
|---|---|---|
| Mechanism / biology | distributed agents, field constraints, counterfactual target | a literal anatomy slideshow |
| Phenomenology | make the viewer undergo selection, lag, ambiguity, or recognition | explanatory labels as the main content |
| Comparative philosophy | paired manifolds with conserved correspondences | flattening both positions into one palette |
| Temporal argument | shutters, traces, phase, retention, branch topology | a generic clock |
| Causal emergence | phase transition, repetition, crystallization, hysteresis | simple before/after crossfade |
| Ritual / imaginal | reciprocity, material response, thresholds, camera reversal | a new centered glyph in every scene |

## 5. Material selection

Choose one continuity material capable of every required transformation. Write
three tests before implementation:

- Can it carry the essay's mechanism?
- Can it fail or become ambiguous?
- Can its final state retain the history of earlier states?

Color is ontological:

- assign each color to a stable conceptual role;
- use brightness for importance only after topology is readable;
- reserve the highest luminance or chroma for genuine reversals;
- change a role's color only when the essay says its identity changed.

## 6. Motion contract

- `u` advances the claim: formation, rupture, correction, integration.
- `t` keeps forces alive without changing the thesis.
- `u_audioVolume` affects density, pressure, reach, or coherence.
- `u_audioBeat` triggers accents, pulses, phase locks, or branch decisions.

An audio uniform that only multiplies final brightness fails review. A `u`
uniform that only fades the frame fails review.

## 7. Camera contract

Camera and composition are semantic operators:

- push in = enter a model;
- pull back = reveal the model as local;
- orbit = preserve identity across perspectives;
- split = hold incompatible or comparative views;
- reverse direction = revise agency or causality;
- widen aperture = reintegration;
- slit scan = sequence or exclusion.

Across a pack, no more than one third of scenes may use the same composition
family. The continuity object may recur, but its scale, camera relation,
topology, and function must change.

## 8. Inspectable decision records

`film_spec.json` is the visible design rationale. It records the claim,
topology, material, camera, motion semantics, risk, and review target for each
shader. It is evidence future agents can critique and reproduce; it is not a
request for private internal reasoning.

The spec is written before shader implementation and updated when render review
changes a decision.

## 9. Implementation pattern

Each pack contains:

```text
beautify/<slug>/
  film_spec.json
  REVIEW.md
  glsl/
    include/<pack_material>.glsl
    vis_*.glsl
```

Every wrapper is standalone GLSL 330 and includes:

```glsl
#include "primitives.glsl"
#include "visionary.glsl"
#include "cinema.glsl"
#include "signature.glsl"
#include "include/<pack_material>.glsl"
```

The pack include exposes one renderer with a numeric mode. Modes may share
material functions; they may not collapse into palette-swapped copies.

## 10. Production loop

1. Extract every unique source visual function and its narration clusters.
2. Draft thesis, continuity material, causal graph, and five-phase arc.
3. Fill `film_spec.json`; validate it.
4. Implement the material include and wrappers.
5. Audit and compile all wrappers.
6. Render low, mature, and resolved states.
7. Review contact sheets before individual glamour frames.
8. Reject clipping, illegible topology, composition repetition, decorative
   audio, or a final scene that merely repeats the opening.
9. Revise the spec and shader together.
10. Record evidence in `REVIEW.md`, then commit the complete pack.
