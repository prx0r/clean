# Context for ChatGPT — Tantraloka Skia Framework

## What we need

A fully-timed, audio-synced Logicvid video from the essay "Why Does Reality Appear?" using the argument-diagram motif. The video should have proper typography, animated concept maps, and timing matched to TTS narration.

## Framework architecture (read these files)

| File | What it contains |
|---|---|
| `FRAMEWORK-ARCHITECTURE.md` | Complete architecture reference |
| `src/argument-diagram.mjs` | The argument-diagram motif renderer (move types: claim, subclaim, refutation, premise, side-by-side, branch, converge, concept-map, divider) |
| `renderer.mjs` | FrameRenderer, ffmpeg pipe, audio manifest loading |
| `motifs.mjs` | Motif registry — add new motifs here |
| `fonts.mjs` | Font registration — EB Garamond + Noto Devanagari + Source Serif 4 + KaTeX fonts |
| `math.mjs` | Deterministic math, seeded PRNG, easing functions |
| `primitives.mjs` | Drawing primitives (drawGlowOrb, drawRing, drawNode, drawLabel, drawArrowHead, etc.) |
| `schema.mjs` | Pack JSON schema validation |
| `AGENT-GUIDE.md` | Full agent instructions for the framework |
| `packs/logicvid-04-mono.json` | Previous attempt at the logicvid (has overlapping bugs) |
| `packs/logicvid-moves-demo.json` | Demo of concept-map and dialogue move types |

## Font situation

| Font | Has Sanskrit? | Has math? | Use case |
|---|---|---|---|
| EB Garamond + italic | ✅ Full | Partial | Default for semantic-essay motif |
| Noto Serif Devanagari | ✅ Devanagari script only | ❌ | Devanagari footer text |
| Source Serif 4 | ✅ Full | Partial | Argument-diagram (screen-optimized) |
| KaTeX Main | ❌ No diacritics | ✅ Full | Math equations only |
| KaTeX Math Italic | ❌ No diacritics | ✅ Full | Math variables only |

**Recommendation:** Use Source Serif 4 as the primary font for argument-diagram (it has full Sanskrit diacritic support and is screen-optimized). Use KaTeX fonts only for pure math expressions that don't contain Sanskrit.

## Scene format

```json
{
  "id": "sc01",
  "title": "Scene Title (2-80 chars)",
  "subtitle": "Subtitle (2-140 chars)",
  "term": "IAST term (1-50 chars)",
  "devanagari": "देवनागरी",
  "motif": "argument-diagram",
  "duration": 10.0,
  "params": {
    "moves": [
      {"type": "claim", "text": "**Bold** and *italic* text", "size": 34, "status": "active|refuted|resolved|highlight"},
      {"type": "subclaim", "text": "Supporting text", "y": 430, "size": 20},
      {"type": "divider"},
      {"type": "refutation", "text": "Objection text", "size": 26},
      {"type": "premises", "premises": ["P1.", "P2."], "conclusion": "∴ Conclusion"},
      {"type": "side-by-side", "left": "Left\ncolumn", "right": "Right\ncolumn"},
      {"type": "branch", "branches": [{"label": "Option A"}, {"label": "Option B"}, {"label": "Option C"}]},
      {"type": "concept-map", "central": "Center", "nodes": [
        {"label": "Node 1", "relation": "relation text", "x": -300, "y": -140},
        {"label": "Node 2", "relation": "relation text", "x": 300, "y": -140}
      ]},
      {"type": "converge", "text": "Resolution text\nmultiple lines"}
    ]
  }
}
```

## Overlapping bug fix
`renderSubclaim` default `y` should be 440 (was 410, which overlapped with claims). Also check that claim text never exceeds CY ± 120px range.

## Known issues
1. KaTeX fonts lack Sanskrit diacritics — use Source Serif 4 for mixed text
2. `textOverlays` system doesn't exist yet — text timing is controlled by `smoothstep(i/n, (i+1)/n, t)` which divides scene time equally among moves
3. No audio reactivity yet — `env.audio` is available but unused in argument-diagram
4. Concept-map bezier curves use `(i % 3 - 1) * 30` for deterministic noise — this is fine but could be more organic

## Render pipeline
```bash
cd MOTHERFUCKER
# For base packs:
node cli.mjs render packs/pack.json --out build/output.mp4
# For packs with capabilityPacks:
node -e "import('./tools/render-pack.mjs').then(m=>m.main('./packs/pack.json'))"
```

## Audio pipeline
```bash
edge-tts --voice en-GB-SoniaNeural -f clean_narration.txt --write-media narration.mp3
python3 tools/analyse-audio.py narration.mp3 features.json
# Add "audioManifest": "features.json" to pack JSON
# Render with audio reactivity
ffmpeg -i video.mp4 -i narration.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```
