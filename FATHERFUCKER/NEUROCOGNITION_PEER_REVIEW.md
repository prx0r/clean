# Neurocognition Pack Peer Review

## Verdict

The pack design is strong and useful, but the current push is not loadable in
the repository layout shown at commit `792f2c7` without integration repairs.

## Critical

1. **Wrong relative imports in `src/neuro-visuals.mjs`.**
   The file lives in `MOTHERFUCKER/src/`, while `math.mjs`, `primitives.mjs`,
   and the other kernel modules live in `MOTHERFUCKER/`. Imports must use
   `../math.mjs` and `../primitives.mjs`.

2. **`Path2D` is used without import.**
   Add:
   ```js
   import { Path2D } from "@napi-rs/canvas";
   ```

3. **`drawGrid` is imported from `primitives.mjs` but the kernel primitive
   module does not export it, and it appears unused.**
   Remove the import or add a genuine primitive implementation.

4. **The five known dynamic registry seams still block activation/rendering.**
   Dynamic theme resolution, dynamic schema validation, dynamic semantic
   relation lookup, metadata discovery, and the missing base pack must be fixed.

## High priority semantic issues

5. **Operator vocabulary drift.**
   The manifest declares operators not present in `visualOperatorsV2`:
   `complete`, `consolidate`, `prune`, `stabilise`, `amplify`, `compete`,
   `bind`, `integrate`, `contain`, `retain`.

   Current manifest validation only checks that an operator array is non-empty,
   so this passes silently. Either normalize to the formal vocabulary or extend
   the central operator ontology deliberately.

6. **`predictive-loop` is too broad as one mechanism.**
   It combines top-down prediction, bottom-up input, comparison, error
   generation, and model revision. It is useful, but should expose phases or
   presets so agents can request:
   - prediction only;
   - comparison/error;
   - full update loop.

7. **`error-driven-learning` risks conflating predictive processing with
   backpropagation.**
   Its provenance and tags should distinguish:
   - biological prediction-error/plasticity;
   - artificial-network gradient backpropagation;
   - generic error-corrective adaptation.

8. **`competitive-binding` needs explicit theory neutrality.**
   Binding by competition is one family of models, not a settled general
   account of consciousness. Keep `epistemicMode: functional-model` and add a
   caveat or `modelFamily` parameter.

## Medium priority implementation concerns

9. `brain-schematic` describes a lateral brain but the current geometry appears
   stylized and near-symmetrical. Label it as a simplified schematic rather
   than canonical neuroanatomy unless verified against a reference.

10. `neural-oscillation` maps named bands to one representative frequency.
    Better expose a range or label the value as illustrative; bands are ranges,
    not single frequencies.

11. `attention-selection` computes aperture radii using
    `55 * apertureSize * 300`; with the default `0.18`, this produces a radius
    near 2,970 logical pixels, vastly larger than the frame. This likely needs a
    direct pixel mapping such as `40 + apertureSize * 260`.

12. `errorSignal` uses a sine wave directly for alpha and radius. Negative pulse
    values can produce negative ring radius or alpha. Normalize with
    `0.5 + 0.5 * wave(...)`.

13. `memoryTrace` divides by `nodes - 1`; the manifest minimum is 2, which is
    safe, but runtime should still clamp direct API calls.

14. Parameter schemas are metadata only. Runtime functions should clamp values
    because renderers may be invoked outside manifest validation.

## Strong points

- Excellent epistemic separation between biomedical schematics,
  computational models, and functional models.
- Assets and mechanisms are sensibly separated.
- Motion proofs are specific and generally meaningful.
- The set is highly relevant to the essay pipeline: attention, prediction,
  memory, propagation, binding, temporal integration, and learning cover a
  major recurring vocabulary.
- Deterministic seeded network and trace generation is the correct approach.
- The selection policy rejects homunculi, static decorative brains, and
  category errors.
