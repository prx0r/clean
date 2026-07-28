# Logicvid — ChatGPT Build Instructions

You are building a complete logicvid (formal philosophy video) system from scratch. Read ALL files in this package before writing any code.

## The Rendering Engine

Files: `renderer.mjs`, `motifs.mjs`, `math.mjs`, `primitives.mjs`, `fonts.mjs`, `theme.mjs`, `schema.mjs`, `scene-pack.schema.json`

This is a deterministic Skia motion-graphics framework (`@napi-rs/canvas`). The renderer:
- Creates a `FrameRenderer` with a canvas of given dimensions
- Renders each scene by calling `motif(ctx, t, scene, env)` where `t` goes 0→1
- Streams raw RGBA frames into ffmpeg H.264
- `env` contains: `{theme, seed, width, height, fps, frame, seconds, sceneSeconds, audio}`

## The Working v1 Motif

File: `argument-diagram.mjs` (423 lines)

This is the ONLY motif that has produced clean, non-overlapping logicvids. It has 10 move types:
- claim, subclaim, refutation, divider, premises, side-by-side, branch, converge, dialogue, concept-map

**Critical bug in v1's `styledText()`:** Center-aligned text with `**bold**` or `*italic*` markers only renders the first segment and drops the rest. The fix (already implemented in v2) is to measure all segments first, calculate total width, then render as a centered group. All rich text must use this approach.

**Known good pack:** `logicvid-04.json` — 7 scenes, clean white background, simple typography.

## The v1 Pack That Works

File: `logicvid-04.json` — 7 scenes, uses the argument-diagram motif. This is the proven baseline. Scene structure:
1. The Question (claim → subclaim → divider → highlight claim)
2. Abhinavagupta (claim → subclaim → divider → side-by-side → subclaim)
3. Formal Proof (premises list → conclusion)
4. QFT vs Spanda (side-by-side → divider → refuted claim)
5. Russellian Monism (side-by-side → divider → claim → subclaim)
6. EM Field Theories (refuted claim → subclaims)
7. Verdict (branch → divider → resolved claim)

## The New Source Pack (Semantic Anchors)

File: `logicvid-reality-appears.source.json` — 9 scenes using semantic anchors:
```json
{"enter": {"after": "manifest"}}
```
These reference words in the TTS narration (`narration-scenes.json`). The compiler `compile-logicvid.py` resolves them to frame numbers using Edge TTS WordBoundary metadata.

## Available Theory (from our research)

- **Albers** (`logicvid/ANALYSIS-ALBERS.md`): Color is relative, not absolute. Color intervals matter more than individual colors. Weber-Fechner: perceptual response is logarithmic. No decorative color — every color carries meaning.
- **Doczi** (`logicvid/ANALYSIS-DOCZI.md`): Fibonacci proportions, golden ratio φ=1.618, 8px grid base. Neighboring parts share proportional limits.
- **Tymoczko** (`logicvid/ANALYSIS-TYMOCZKO.md`): Voice-leading economy, centricity (tonal center), minimal movement between states.

## What Has Failed (and Why)

Read `logicvid-postmortem.md` and `handoverlogicvid.md` for the full history. Key failures:
1. **Text overlap** — moves in different replacement groups render simultaneously because they don't share a slot
2. **Decorative rings** — the user has rejected ALL decorative elements (rings, glows, orbs, concentric circles)
3. **Wrong timing model** — the v2/v3/v4/v5 attempts tried word-level sync without proper tools
4. **StyledText center bug** — bold text in centered claims never rendered (fixed in rich-text.mjs but v1 still has the bug)

## Your Task

Design and produce a COMPLETE working logicvid system. Specifically:

1. **A NEW motif** — Based on v1's proven move types but with:
   - Clean white background. NO rings, glows, orbs, or decorative elements.
   - All rich text properly centered (fix the styledText bug)
   - A simple replacement group system (same slot = same position, entering a new move auto-exits the previous one in the same slot)
   - Support for the 9-scene "Why Does Reality Appear?" argument

2. **A proper scene pack** for the 9-scene argument. Each scene should present ONE clear proposition:
   - Scene 1: side-by-side comparison of "physics describes" vs "leaves question untouched" → THEN claim "Why manifest?"
   - Scene 2: side-by-side "How does a system change?" vs "Why is change present?" → subclaim about QFT → claim "Does not answer second"
   - Scene 3: introduce the three Trika terms one at a time
   - Scene 4: formal premises stacking with conclusion
   - Scene 5: functionalist objection → side-by-side rebuttal
   - Scene 6: QFT vs Spanda comparison
   - Scene 7: three-way branch of live positions
   - Scene 8: epistemic ledger (what each domain contributes)
   - Scene 9: resolution and frontier question

3. **Timing model**: Use `t` (scene progress 0→1) with authored `start`/`end` normalized timing. Scene durations are set from TTS audio length. NO whisper, NO word-level sync, NO absolute seconds. The v1 approach of `smoothstep(i/n, (i+1)/n, t)` works fine for individual scenes. If you need more control, use authored `start`/`end` values like v2 did.

4. **Output format**: Write the scene pack as valid JSON matching `scene-pack.schema.json`. The motif must be registered in `motifs.mjs` as `"logicvid": renderLogicvid`. The renderer already supports custom motifs via the registry.

5. **Font support is already set up**: Source Serif 4 (latin + IAST Sanskrit), EB Garamond, Noto Serif Devanagari, KaTeX fonts. Use `**bold**` and `*italic*` and `$math$` syntax in text.

6. **No animation**: Text should appear at full opacity immediately when its start time is reached. No fade-in, no scale-up, no pop-in.

## Files to Output

1. The motif `.mjs` file (register as `"logicvid"`)
2. The scene pack `.json` file
3. A brief explanation of your design choices

Write clean, working code. The renderer will call `renderLogicvid(ctx, t, scene, env)` for each scene. `t` goes from 0 to 1 across the scene duration.
