# AI Authoring Guide

This guide is the contract between a visual-design model and the Skia renderer. The model should generate a JSON scene pack; it should not generate Pillow, FFmpeg commands, frame loops, borders, footers, font loading, or output paths.

## Design grammar

Every scene inherits:

- a 1280×720 logical composition field;
- protected margins inside the double border;
- a reserved footer beginning at logical y=608;
- an ivory manuscript, white scientific, or midnight vellum field;
- stable paper grain;
- crimson for decisive power or transition;
- indigo for cognition, reflection, or articulation;
- gold for luminosity and source;
- umber for quiet structure;
- full EB Garamond IAST and Noto Serif Devanāgarī shaping.

Keep primary visual content between x=120–1160 and y=95–550. Do not draw over the footer.

## Pack fields

```json
{
  "version": "1.0",
  "id": "lowercase-kebab-id",
  "title": "Human-readable pack title",
  "description": "What the pack explains",
  "theme": "ivoryManuscript",
  "seed": 123456,
  "render": {
    "width": 1920,
    "height": 1080,
    "fps": 24,
    "sceneDuration": 4.8,
    "crf": 16,
    "preset": "medium"
  },
  "scenes": []
}
```

Use `ivoryManuscript` unless darkness is conceptually necessary. Use `whiteScientific` for cognition/science mappings and `midnightVellum` for void, night, threshold, or destructive transformation.

## Built-in motifs

| Motif | Best use | Useful parameters |
| --- | --- | --- |
| `heart-lattice` | heart, source, distributed awareness, microcosm | `centerText`, `density` |
| `attention-lens` | selection, limitation, perception, horizon | `centerText`, `speed` |
| `phoneme-forge` | mantra, mātṛkā, vāc, sound becoming form | `phonemes` |
| `reflexive-mirror` | prakāśa–vimarśa, aham–idam, self/world | palette overrides |
| `return-current` | recognition, ascent, reversal, contemplative return | `nodes` |
| `closing-heart-seal` | synthesis, final cosmogram, pack conclusion | `centerText`, `outerNodes`, `ringWords` |
| `composition` | a genuinely new scene assembled from layers | `layers` array |

Built-in motifs contain continuous motion behavior. A model supplies the meaning and tuned parameters; the engine supplies animation craft.

## Declarative composition layers

When `motif` is `composition`, add between 3 and 14 layers. Avoid stacking every available primitive.

| Layer type | Main fields |
| --- | --- |
| `orb` | `x`, `y`, `radius`, `color`, `core` |
| `ring` | `x`, `y`, `radius`, `color`, `width` |
| `ellipse` | `x`, `y`, `rx`, `ry`, `rotation`, `color` |
| `lotus` | `x`, `y`, `radius`, `petals`, `color`, `fill` |
| `label` | `x`, `y`, `text`, `script`, `size`, `color` |
| `silhouette` | `x`, `y`, `scale`, `color` |
| `polygon` | `x`, `y`, `radius`, `sides`, `rotation`, `color` |
| `path` | `points`, `color`, `width`, `drawStart`, `drawEnd` |
| `bezier` | `p0`, `p1`, `p2`, `p3`, `color`, `particles`, `speed` |
| `orbit-nodes` | `x`, `y`, `count`, `rx`, `ry`, `nodeRadius`, `speed` |
| `radial-words` | `x`, `y`, `words`, `radius`, `size`, `color` |
| `grid` | `x`, `y`, `columns`, `rows`, `spacingX`, `spacingY`, `warp` |

Colors can be palette tokens—`accent`, `secondary`, `luminous`, `structure`, `ink`, `crimson`, `indigo`, `gold`—or six-digit hex colors.

Every layer may use:

```json
{
  "appear": [0.05, 0.3],
  "disappear": [0.9, 1.0],
  "alpha": 0.8,
  "motion": {
    "x": 8,
    "y": 4,
    "scale": 0.04,
    "rotation": 0.02,
    "cycles": 0.8,
    "phase": 0.1
  }
}
```

Animation time is normalized from 0 to 1. Use low amplitudes. Motion should reveal a relationship, not keep every object moving equally.

## Declarative scene example

```json
{
  "id": "ex01",
  "title": "A Field Learns Its Centre",
  "subtitle": "Relation gathers around a luminous reference without becoming a prison.",
  "term": "Madhya",
  "devanagari": "मध्यम्",
  "motif": "composition",
  "layers": [
    {
      "type": "grid",
      "x": 640,
      "y": 292,
      "columns": 11,
      "rows": 7,
      "color": "secondary",
      "warp": 6,
      "alpha": 0.55
    },
    {
      "type": "bezier",
      "p0": {"x": 180, "y": 360},
      "p1": {"x": 390, "y": 120},
      "p2": {"x": 850, "y": 480},
      "p3": {"x": 1100, "y": 280},
      "color": "accent",
      "width": 2,
      "particles": 9
    },
    {
      "type": "orb",
      "x": 640,
      "y": 292,
      "radius": 42,
      "color": "luminous",
      "motion": {"scale": 0.05, "cycles": 0.7}
    },
    {
      "type": "lotus",
      "x": 640,
      "y": 292,
      "radius": 88,
      "petals": 10,
      "color": "accent",
      "motion": {"rotation": 0.02}
    },
    {
      "type": "label",
      "x": 640,
      "y": 297,
      "text": "मध्यम्",
      "script": "devanagari",
      "size": 28,
      "color": "secondary"
    }
  ]
}
```

## Content and typography rules

- `term` is IAST, not Devanāgarī.
- `devanagari` must contain actual Devanāgarī characters.
- Titles should be 2–7 words.
- Subtitles should state one precise relation and remain under 110 characters when possible.
- Do not put English text into a Devanāgarī font.
- Do not add manual footer text as composition layers.
- Use Sanskrit labels sparingly inside the diagram.
- Do not use generic rainbow chakra colors.
- Do not make Māyā evil, materiality a mistake, or recognition an escape from embodiment.
- Do not claim a scene is a direct quotation unless the source is supplied.

## Quality sequence

1. Generate JSON.
2. Run `node src/cli.mjs validate <pack.json>`.
3. Render a contact sheet.
4. Check cropping, density, title length, script correctness, and conceptual clarity.
5. Render the MP4.
6. Accept the pack only when the generated validation report has `"valid": true`.

The complete machine contract is `scene-pack.schema.json`.
