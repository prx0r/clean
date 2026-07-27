# Testing and Quality Control

## Unit tests

Test:

- geometry point counts;
- path orientation;
- deterministic random generation;
- audio interpolation;
- route smoothing;
- manifest validation;
- registry activation;
- style resolution.

## Capability probe

Run against the exact installed `@napi-rs/canvas` version.

Never assume a feature is available merely because Skia supports it.

## Golden-frame tests

For each mechanism, render fixed frames using a fixed seed.

```text
0%
25%
55%
82%
100%
```

Store hashes or approved reference images.

Use hash checks only for deterministic regression, not beauty.

## Perceptual tests

### Silent test

Can the relation be inferred without labels?

### Reordering test

Could transition frames be rearranged without changing the apparent event?

If yes, visible causality is weak.

### Continuity test

Does the continuity object survive every permitted transformation?

### Attention test

When narration is dense, does the image become clearer rather than merely
dimmer?

### Audio-off test

Does the visual still have a semantic structure without music?

### Signal-isolation test

Render once with only music routing and once with only narration routing.
Confirm that they control different visual responsibilities.

## Release gates

```json
{
  "schema": "pass",
  "determinism": "pass",
  "capability_activation": "pass",
  "geometry_integrity": 0.9,
  "semantic_legibility": 0.84,
  "transition_causality": 0.82,
  "audio_routing_clarity": 0.8,
  "narration_attention_control": 0.83,
  "rendered_visual_quality": 0.86
}
```
