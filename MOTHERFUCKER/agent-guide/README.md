# Visionary Engine — Agent Guide and Integration Kit

This package explains how to connect PathKit geometry, particles, materials,
audio features, narration timing, capability packs, style packs and
composition-level packs to the current deterministic Skia framework.

It includes:

- a complete operator guide;
- an agent skill;
- integration patches and contracts;
- audio-reactive and narration-reactive examples;
- example capability, style and composition packs;
- testing and review checklists;
- authoring templates;
- future specifications.

## Recommended reading order

1. `docs/01-FOUNDATION-INTEGRATION.md`
2. `docs/02-AUDIO-AND-NARRATION-REACTIVITY.md`
3. `docs/03-RENDERING-PIPELINE.md`
4. `docs/04-EXPANDING-EXISTING-PACKS.md`
5. `docs/05-PACK-TAXONOMY.md`
6. `agent-skill/SKILL.md`

## Core rule

Do not make every visual react to everything.

Assign each signal a semantic responsibility:

- score events determine musical causality;
- waveform features determine performed intensity and timbre;
- narration timings determine verbal attention and semantic emphasis;
- composition packs determine why scenes and transitions occur;
- capability packs determine what can be shown;
- geometry, material, motion and style packs determine how it appears.
