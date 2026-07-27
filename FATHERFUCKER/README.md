# Formal JavaScript Framework Overlay

This overlay upgrades the current `MOTHERFUCKER/` implementation into a coherent
extensible package without replacing the proven renderer.

## Apply

Copy this directory into the repository root, then run:

```bash
cd MOTHERFUCKER
node tools/apply-formal-framework-patch.mjs
npm test
```

The patch script:

1. wires dynamic themes into the kernel `getTheme()`;
2. makes semantic scene validation accept dynamically registered mechanisms;
3. integrates dynamic mechanism relations into compatibility checks;
4. preserves dynamic mechanism descriptions for discovery;
5. creates a public `index.mjs` entry point;
6. creates the missing `base` capability pack;
7. repairs `src/*-visuals.mjs` imports when those modules import kernel files from
   the wrong directory;
8. imports `Path2D` in `src/neuro-visuals.mjs`;
9. removes the invalid/unused `drawGrid` import from the neurocognition runtime;
10. adds formal expansion-pack roots.

## Pack roots included

- `base`
- `scientific-diagrams`
- `systems-dynamics`
- `temporal-processes`
- `embodied-phenomenology`
- `textual-scholarship`
- `tantric-cosmology`
- `comparative-epistemology`
- `data-visualization`

These roots intentionally contain policy, vocabulary boundaries, and themes
rather than dozens of premature mechanisms. Child packs should add mechanisms
only when topology, state transition, invariant, encoding channels, or motion
proof genuinely differ.

## Important neurocognition review fixes

The current `src/neuro-visuals.mjs` has two module-load issues:

- imports such as `./math.mjs` point to nonexistent `src/math.mjs`; they must
  point to `../math.mjs`;
- `Path2D` is used but not imported.

The manifest also introduces nonstandard operators:
`complete`, `consolidate`, `prune`, `stabilise`, `amplify`, `compete`, `bind`,
`integrate`, `contain`, and `retain`.

The patch does not silently accept vocabulary drift. Prefer mapping these to the
existing formal operators:

| Pack operator | Formal operator |
|---|---|
| complete | emerge / transform |
| consolidate | coordinate / transform |
| prune | cool / select |
| stabilise | coordinate |
| amplify | propagate / transform |
| compete | compare / select |
| bind | coordinate / converge |
| integrate | coordinate / converge |
| contain | frame / enclose |
| retain | recontextualize / sequence |

Add a genuinely new operator only when it changes the visual grammar, not merely
the domain wording.
