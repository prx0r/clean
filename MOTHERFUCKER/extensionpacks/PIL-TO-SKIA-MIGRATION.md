# PIL-to-Skia Capability Migration

## The central rule

Do not convert a monolithic PIL pack into a monolithic Skia pack. Mine it.

The PIL file contains five different things mixed together:

1. renderer infrastructure;
2. house style;
3. drawing primitives;
4. reusable semantic mechanisms;
5. essay-specific scenes.

Only the fourth category directly expands essay reasoning capacity. The other
categories go to their own layers.

## Migration worksheet

Complete one row for every candidate scene:

| Field | Required answer |
| --- | --- |
| Source | File, scene title/id and source function |
| Claim | What does the scene prove? |
| Relation | Which registered relation is visible? |
| Source state | What exists before the motion? |
| Target state | What exists after the motion? |
| Preserves | What remains invariant? |
| Marks | Nodes, paths, regions, axes, labels |
| Channels | Position, containment, direction, shape, scale, color, rhythm |
| Motion proof | What cannot be communicated by the mature still? |
| Nearest mechanism | Existing mechanism and the important difference |
| Decision | Token, primitive, mechanism, parameter, preset, example or reject |
| Provenance | Stable source reference |

## Example: barrier scenes

The attached biological pack contains classical stopping, tunnelling,
wavefunction decay, barrier width, particle mass, double wells, enzyme
architecture and gates.

They should not become one mechanism per scene.

| Source idea | Migration |
| --- | --- |
| White scientific background and concept color | `scienceBlue` theme |
| Axes, ticks and measurement cursor | Technical primitives inside the science runtime |
| Classical stop versus finite penetration | `barrier-tunnelling` mechanism |
| Width and mass comparisons | Parameters or presets on barrier/plot mechanisms |
| Double well | `energy-landscape` mechanism |
| Enzyme channel and proton gate | `molecular-gate` mechanism |
| Evidence caution | `evidence-ladder` mechanism |
| Final synthesis composition | Worked example combining mechanisms |

## Example: temporal scenes

| Source idea | Migration |
| --- | --- |
| Field of events becoming ordered | `simultaneity-sequence` |
| Present aperture moving across events | `moving-time-window` |
| Possible futures narrowing | `branching-future` |
| Past trace interpreted in the present | Existing `memory-relay`, possibly with a temporal preset |
| Attention excluding alternatives | Existing `attention-beam` or `boundary-gates` |
| Clock used only as an icon | Reject |

## Porting order

1. Run `tools/audit-pil-pack.py`.
2. Create the worksheet.
3. Resolve the intended parent pack.
4. Deduplicate against parent mechanisms.
5. Add missing primitives only when two or more mechanisms need them.
6. Implement mechanism renderers in logical Skia coordinates.
7. Declare metadata in `pack.json`.
8. Add a minimal demo scene for every new mechanism.
9. Add deterministic and permission-boundary tests.
10. Render a contact sheet and inspect at full and thumbnail size.
11. Render a short MP4 proof and validate it with FFprobe.
12. Promote the pack only after the acceptance gates pass.

## What not to port

- frame-directory pipelines;
- per-file FFmpeg concatenation;
- hard-coded system fonts;
- unstable per-frame noise;
- copied border and footer functions;
- long narration embedded in renderers;
- visual names that differ only by essay noun;
- scene-specific coordinates with no parameter contract.

## Promotion path

A project-local mechanism may become shared after:

- two different essays use it successfully;
- its domain nouns can be parameterized;
- its relation contract stays the same across both uses;
- it passes alternate-theme and low-resolution tests;
- its name describes geometry or relation, not the first essay.

