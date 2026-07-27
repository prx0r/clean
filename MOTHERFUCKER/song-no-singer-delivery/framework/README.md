# Tantrāloka Skia Framework

A deterministic, AI-authorable Skia motion-graphics engine for the visual language established by the Pillow packs:

- warm ivory or concept-specific dark fields;
- double manuscript border and four rosette seals;
- crimson, indigo, gold, umber, and restrained secondary color;
- luminous paths, bindus, lotuses, cosmograms, veils, fields, and moving particles;
- EB Garamond for English and IAST;
- Noto Serif Devanagari for shaped Sanskrit;
- a fixed lower-third system for title, explanation, IAST term, and Devanāgarī;
- smooth, deterministic animation with no crawling random texture;
- direct raw-frame streaming from native Skia into H.264 through FFmpeg.

The renderer uses a logical 1280×720 design space and scales vectors and type to the requested output resolution. The included proof pack renders at 1920×1080 and 24 fps. A pack can request up to 8K and 60 fps through the schema.

## Quick start

Requirements:

- Node.js 20 or newer
- FFmpeg and FFprobe

```bash
npm install
npm test
node src/cli.mjs render packs/hrdaya-original.json
```

Outputs are written to `build/<pack-id>/`:

- `<pack-id>.mp4`
- `<pack-id>-contact-sheet.png`
- `<pack-id>-validation.json`

Useful commands:

```bash
# Validate JSON before rendering
node src/cli.mjs validate packs/hrdaya-original.json

# Render a single poster at the scene's representative time
node src/cli.mjs poster packs/hrdaya-original.json --scene hr03

# Render only the pack contact sheet
node src/cli.mjs contact packs/hrdaya-original.json

# Inspect the built-in visual vocabulary
node src/cli.mjs motifs

# Confirm both font families are registered
node src/cli.mjs fonts
```

## Essay-to-film workflow

The framework now accepts a source essay plus an AI-authored visual program. It compiles them into:

- a narration script containing every essay paragraph exactly once;
- a frame-quantized storyboard with spoken passage, timing, semantic role, visual mechanism, continuity object, and rationale for every shot;
- a normal Skia scene pack;
- a contact sheet, validated H.264 MP4, and validation report.

```bash
# Compile the example essay without rendering
npm run compile:essay

# Render the complete narration-timed visual companion
npm run render:essay

# Build and audit the v2 adversarial example
npm run build:song
npm run audit:song

# Use exact shot lengths obtained from final narration
node src/cli.mjs render-essay programs/infinite-learned-visual-program.json \
  --timings path/to/exact-timings.json
```

The draft timing model uses word count plus a per-shot tail, then rounds every boundary to a video frame. Publication timing should come from final narration: provide a JSON object shaped like `{"shots":[{"id":"inf-001","duration":6.125}]}` with one entry for every storyboard shot. The compiler rejects missing, duplicate, unknown, or longer-than-30-second exact timings instead of silently mixing them with estimates.

For new essays, read `VISUAL_DECISION_PROTOCOL.md` and use `ESSAY_VISUAL_MODEL_PROMPT_V2.md`. The v2 workflow first creates a visual-free argument IR, then generates and scores competing candidates, enforces mechanism/relation compatibility, audits continuity lifecycles, and validates the rendered output. The v1 guide and prompt remain for compatibility.

## Architecture

| File | Responsibility |
| --- | --- |
| `scene-pack.schema.json` | Machine-readable contract for AI-generated packs |
| `essay-analysis.schema.json` | Visual-free contract for source units, claims, relations, and state changes |
| `essay-visual-program-v2.schema.json` | Deterministic contract for candidate evidence, continuity, and semantic correspondence |
| `src/schema.mjs` | Strict runtime checks, including Devanāgarī-vs-IAST mistakes |
| `src/essay-program.mjs` | Paragraph coverage, narration timing, storyboard generation, and pack compilation |
| `src/program-builder.mjs` | Relation language and deterministic expansion of compact beat specifications |
| `src/visual-semantics.mjs` | Registered roles, operators, relations, and mechanism compatibility |
| `src/visual-auditor.mjs` | Semantic correspondence, continuity, diversity, and candidate audits |
| `src/renderer.mjs` | Frame renderer, MP4 stream, posters, contact sheets, validation |
| `src/primitives.mjs` | Border, rosettes, stable paper, glow, lotus, paths, nodes, footer |
| `src/motifs.mjs` | High-level visual metaphors with authored motion behavior |
| `src/semantic-visuals.mjs` | Complete native-Skia semantic mechanism registry |
| `src/systems-visuals.mjs` | Sixteen system-oriented mechanisms for networks, feedback, memory, dialectic, and agency |
| `src/composition.mjs` | Declarative layers for new scenes without JavaScript |
| `src/fonts.mjs` | Portable full-font registration and Skia text configuration |
| `src/math.mjs` | Deterministic random numbers, easing, geometry, sampled Béziers |
| `packs/hrdaya-original.json` | Six-scene original proof pack |
| `AI_AUTHORING_GUIDE.md` | How an AI model should design valid new packs |
| `PROMPT_FOR_VISUAL_MODEL.md` | Ready-to-paste generation prompt |
| `ESSAY_TO_VISUAL_WORKFLOW.md` | Decision process from prose argument to coherent timed film |
| `ESSAY_VISUAL_MODEL_PROMPT.md` | Ready-to-paste prompt for essay visual-program generation |
| `VISUAL_DECISION_PROTOCOL.md` | Normative v2 decision procedure and validation gates |
| `ESSAY_VISUAL_MODEL_PROMPT_V2.md` | Deterministic staged prompt for another visual agent |
| `programs/infinite-learned-visual-program.json` | Complete 44-shot worked example |
| `programs/song-no-singer-visual-program.json` | Complete 88-shot v2 adversarial worked example |
| `programs/song-no-singer-analysis.json` | Visual-free argument IR for the 88-shot worked example |
| `programs/song-no-singer-AUDIT.md` | Test findings, semantic metrics, render verification, and remaining timing status |

## Three AI authoring levels

1. **Essay visual-program mode**  
   A model first writes a visual-free argument IR, then maps each claim to a registered relation, generates three candidates, selects by a 100-point rubric, and preserves continuity systems across the full argument. The compiler verifies complete source-unit coverage and the semantic auditor rejects incompatible geometry.

2. **Built-in motif mode**  
   A model chooses a polished motion system such as `attention-lens` or `return-current`, then supplies restrained parameters. This is the safest route for smaller models.

3. **Declarative composition mode**  
   A model chooses `motif: "composition"` and combines style-locked layers such as glow orbs, lotuses, rings, Bézier flows, grids, polygons, Sanskrit labels, orbiting nodes, and radial terms. The engine still owns the background, border, footer, typography, determinism, and encoding.

Custom JavaScript motifs can be added to `src/motifs.mjs`, but they are not required for ordinary AI generation.

## What the framework fixes

The engine deliberately avoids the failure modes in the original standalone scripts:

- fonts are bundled rather than hard-coded to server paths;
- the complete font files cover both IAST and ordinary Latin;
- Devanāgarī fields are rejected if an AI puts transliteration there;
- paper texture is cached and stable across every frame;
- seeds use a stable hash rather than Python's randomized process hash;
- frames stream directly into FFmpeg instead of filling disk with JPEGs;
- output paths are pack-specific;
- validation asserts codec, dimensions, pixel format, frame rate, frame count, and duration;
- scene changes always trigger a fresh render.

## Font licensing

The included EB Garamond and Noto Serif Devanagari variable fonts come from the official Google Fonts repository and are distributed under the SIL Open Font License. Their license files are preserved beside the font binaries.
