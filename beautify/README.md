# Beautify — PIL → GLSL Transformation Pipeline

## Process

Each batch: 5 PIL essay packs → ChatGPT → 5 sets of GLSL shaders.

1. **Prepare:** Copy 5 PIL `.py` platinum packs to `beautify/`
2. **Transform:** ChatGPT reads each PIL, produces one `.glsl` per `vis_*` function
3. **Deliver:** ChatGPT pushes GLSL shaders organized per-essay into `beautify/`

## Conventions

| Item | Location |
|------|----------|
| Current batch PIL | `beautify/*.py` |
| Current batch GLSL | `beautify/{essay-name}/glsl/*.glsl` |
| Completed transformations | `beautify-archive/{essay-name}/` |
| Shared GLSL libraries | `beautify-archive/lib/` |
| Render harness | `beautify-archive/lib/render_harness.py` |
| Scene mapping | `beautify-archive/lib/SCENE_MAPPING.md` |
| Style grammars | `beautify-archive/lib/STYLE-GRAMMARS.md` |

## Per-essay Structure

```
beautify/{essay-name}/
├── essay.py          ← Original PIL pack (reference)
└── glsl/
    ├── vis_*.glsl    ← One per visual function
    └── include/      ← Essay-specific GLSL helpers (optional)
```

## Completed Batches

### Batch 1 (5 essays) — archived at `beautify-archive/`

| Essay | PIL Lines | Scenes | Visual Functions | GLSL Style |
|-------|-----------|--------|------------------|------------|
| 01-life-crosses-barriers | 1342 | 54 | 17 | Scientific reference (original rough port) |
| 02-beliefs-create-biology | 1383 | 41 | 18 | Psychobiology — warm crimson/gold, organic particles |
| 03-voice-inside-chest | 1298 | 40 | 17 | Bioluminescent — deep teal/green, neural glow |
| 04-dreams-create-worlds | 1216 | 39 | 22 | Watercolor — soft edge, wet-on-wet blending |
| 05-time-is-produced-by-forgetting | 993 | 77 | 24 | Temporal geometry — ink on vellum, geometric abstraction |

### Batch 2 (current — in beautify/)

| Essay | PIL Lines | Scenes | Visual Functions | Status |
|-------|-----------|--------|------------------|--------|
| 06-death-systems | 802 | 53 | 16 | Awaiting GLSL |
| 07-you-create-reality | 762 | 49 | 16 | Awaiting GLSL |
| 08-spacious-present | 876 | 58 | 19 | Awaiting GLSL |
| 09-nagarjuna-emptiness | 785 | 48 | 16 | Awaiting GLSL |
| 10-the-wave-cassiopaean | 1067 | 33 | 18 | Awaiting GLSL |

## Style Grammar (per Batch 1)

Each pack gets a unique visual language. Batch 1 styles:

- **Psychobiology** — warm organic, crimson/gold, soft particle glows, anatomical framing
- **Bioluminescent** — deep teal backgrounds, cyan/green neural networks, pulsing node particles
- **Watercolor** — soft edge diffusion, pastel washes, organic bleeding, dream-like blending
- **Temporal geometry** — ink-on-vellum, precise linework, geometric abstraction, restrained palette
- **Life crosses barriers** — scientific diagram, white field, clean SDFs, gold/cyan accent

## Testing

Requires NVIDIA GPU with EGL:

```bash
pip install moderngl numpy pillow
python beautify-archive/lib/render_harness.py --pack 06-death-systems --preview
```

Text overlay is handled by the render harness (PIL), not the GLSL shaders.

### Queue Batch 1 (5 essays)

These packs deliberately treat the PIL implementations as conceptual storyboards,
not visual templates. Each pack has its own rendering grammar and all scene shaders
compile through the shared harness.

| Essay | Visual Functions | GLSL Style |
|-------|------------------|------------|
| a-dream-becomes-a-world-when-it-remembers-where-you-were | 15 | Noctilucent palimpsest cartography |
| a-mirror-becomes-sacred-when-it-stops-reflecting-only-you | 18 | Liquid-metal catoptrics and thin-film light |
| a-name-teaches-the-invisible-how-to-answer | 19 | Phononic aurora and cymatic calligraphy |
| a-ritual-object-teaches-matter-to-remember-heaven | 20 | Raymarched numinous mineral relic |
| a-temple-teaches-space-how-to-become-a-body | 21 | Impossible sacred architecture and volumetric light |

See `QUEUE-BATCH-1-ART-DIRECTIONS.md` for the creative and technical audit.
