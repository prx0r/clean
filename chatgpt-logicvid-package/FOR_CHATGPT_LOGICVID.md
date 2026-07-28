# ChatGPT — Logicvid Problem & Context

We need your help designing a better "logicvid" system. Here's everything you need to know.

---

## The Rendering Engine

We have a deterministic Skia motion-graphics framework at `/root/projects/clean/MOTHERFUCKER/`. It uses `@napi-rs/canvas` (Skia native bindings for Node.js) to render frames, streams raw RGBA into ffmpeg H.264.

**Key files:**
- `renderer.mjs` — FrameRenderer class + ffmpeg pipe + crossfade support + audio manifest loading
- `motifs.mjs` — motif registry (argument-diagram, semantic-essay, composition, etc.)
- `math.mjs` — deterministic math: lerp, smoothstep, seededRandom, wave, pulse
- `primitives.mjs` — drawGlowOrb, drawRing, drawLabel, drawNode, drawPartialPath, drawArrowHead, drawStyledText
- `theme.mjs` — 3 themes (ivoryManuscript, whiteScientific, midnightVellum)
- `fonts.mjs` — EB Garamond, Noto Serif Devanagari, Source Serif 4, KaTeX fonts
- `schema.mjs` — pack validation
- `scene-pack.schema.json` — JSON Schema for valid scene packs

**Scene pack format:**
```json
{
  "version": "1.0",
  "id": "pack-id",
  "theme": "ivoryManuscript",
  "seed": 12345,
  "render": { "width": 1280, "height": 720, "fps": 24, "sceneDuration": 12, "transitionDuration": 0 },
  "scenes": [
    {
      "id": "sc01",
      "motif": "argument-diagram",
      "duration": 10,
      "params": { "moves": [...] }
    }
  ]
}
```

**The motif system:** The renderer dispatches to motif functions by name. Arguments: `(ctx, t, scene, env)` where `t` is scene progress (0→1) and `env` contains `{theme, seed, width, height, fps, frame, seconds, sceneSeconds, sceneProgress, audio}`.

---

## The v1 Motif That Worked (argument-diagram, 423 lines)

`src/argument-diagram.mjs` — the original logicvid renderer. Clean white background `#fafaf8` with 3 subtle concentric field rings that animate in. **10 move types:**

| Move Type | What It Does |
|-----------|-------------|
| `claim` | Centered text, 34px default, scale-up on entry. Colors: `status: "refuted"` (red), `"resolved"` (green), `"highlight"` (gold) |
| `subclaim` | Smaller text at y=450, with optional drift and arrow |
| `refutation` | Slides in from right, red, dashed underline |
| `divider` | Thin centered line with orb |
| `premises` | Vertical list with numbered dots, conclusion line at end |
| `side-by-side` | Two columns with rings, divider line between them |
| `branch` | 3-way branching from center with curved paths |
| `converge` | Text with slide-up + ring reveal |
| `dialogue` | Alternating left/right conversational turns |
| `concept-map` | Central term with radiating nodes + connecting lines |

**Timing:** Even division — each move gets `smoothstep(i/n, (i+1)/n, t)`. No authored control. This is the original approach and it's reliable but inflexible.

**Known bug in v1 `styledText`:** Center-aligned text with bold `**text**` or italic `*text*` markers only renders the first segment and breaks. Fixed in v5 (see below).

**The v1 pack (`logicvid-04.json`):** 7-scene argument film. Uses the above move types. Scene durations are fixed (10-14s each), no audio sync. 0.5s crossfade transitions. This is the baseline that the user considers "better than what we have now."

---

## What We Tried (v2-v5) and What Went Wrong

### v2 — Authored Timing (`argument-diagram-v2.mjs`)
Added `start`/`end` normalized timing (0-1), `persist: true` for cumulative reasoning, `concept-map` and `pulse-path` move types, text auto-wrapping, Source Serif 4 font. Used in the 9-scene `logicvid-reality-appears.json` pack.

**Problems:** Overlapping move windows caused text pileup (persist + fadeout). Same concentric ring background every scene got repetitive. No word-level audio sync — timing was authored guesses.

### v3 — Utterance-Based (`argument-diagram-v3.mjs`)
Switched from moves to "utterances" with `at` in seconds. Added 5 background modes (dark-field, warm-glow, tension-split, etc.) and new diagram primitives.

**Problems:** Backgrounds were ugly — black text unreadable on dark modes. Custom diagram renderers weren't as sharp as v1's. Too many utterances per scene (felt like subtitles).

### v4 — Sharp Renderers + Bug (`argument-diagram-v4.mjs`)
Reverted to clean white background + v1-style concentric rings. Reused v1's proven renderer designs with authored `at`/`duration` timing. Fewer moves per scene.

**Problems:** `styledText()` center-align bug — **bold** text in centered claims never rendered (only showed text before the first `**`). The entire v4 render was silently broken across 6 of 9 scenes. Timing was estimated by word count, not matched to audio.

### v5 — Instant + Whisper (`argument-diagram-v5.mjs`) — CURRENT
Stripped all animation: no smoothstep, no scale, no fade-in, no fade-out. Text appears instantly at full opacity. Used Whisper tiny word timestamps for exact `at` values. Per-node timing for concept-maps. Clean white background, no circles.

**Problems:** 
1. Whisper tiny timestamps drift 100-300ms. Not accurate enough for frame-perfect word sync.
2. Instant rendering reveals every timing error. v1's smooth transitions hid the drift; step-function rendering exposes it.
3. Couldn't install proper forced alignment tools (aeneas, whisperx, gentle) due to system restrictions.
4. `step(t, 0.02)` thresholds on every renderer meant `t=0` (first frame) was blank for ~0.3s — "even the first frame doesn't work."

---

## The Fundamental Problems to Solve

### Problem 1: Word-Level Audio Sync
We need text to appear exactly when the narrator says it. The TTS is generated with `edge-tts --voice en-GB-SoniaNeural`. We have per-scene MP3 files with known durations. We need word-level timestamps accurate to ~40ms (1 frame at 24fps).

**Available tools:** Python 3.11, librosa, ffmpeg, edge-tts. Cannot install system-level packages (PEP 668). We have whisper (the CLI tool) installed — it gave us phrase-level timestamps and can do word-level but they're not accurate enough.

**Question:** How should we get accurate word timestamps? Should we use librosa onset detection? Run whisper in a venv? Use a different alignment strategy?

### Problem 2: The Right Timing Model
v1 used even timing (`i/n → (i+1)/n`). v2 used authored start/end. v3-v5 used `at` in absolute seconds. None of these solved the sync problem because they all depend on knowing *when* the narrator says each phrase.

**Question:** Should the timing model be:
- (A) Even timing like v1 (simple, reliable, proven)
- (B) Authored start/end in normalized space (flexible, needs good estimates)
- (C) Absolute seconds from forced alignment (ideal but needs accurate timestamps)

### Problem 3: Visual Design
The user wants:
- Clean white background (no circles, no rings, no decorative elements)
- Sharp typography with Source Serif 4 + KaTeX Math fonts
- Bold `**text**` for emphasis, red for refuted, green for resolved, gold for highlight
- Side-by-side, branch, concept-map diagrams — but without decorative rings
- No fade-in, no animation, no scale. Text appears instantly when spoken.
- Max 2-4 moves per scene. Most narration is audio-only. Text only appears to anchor key tensions.

### Problem 4: The styledText Center Bug
The original v1 `styledText()` function has a bug: when `align === "center"`, it renders the first text segment and breaks out of the loop, dropping all subsequent **bold** or *italic* segments. Fixed in v5 by measuring all segments first and rendering as a centered group. This fix should be ported back to v1.

---

## All Relevant File Locations

```
/root/projects/clean/
├── STARTHERE.md                              ← Full project exploration log
├── handoverlogicvid.md                       ← Logicvid session handover
├── logicvid-postmortem.md                    ← Postmortem of what went wrong
├── FOR_CHATGPT_LOGICVID.md                   ← This file
│
├── MOTHERFUCKER/
│   ├── renderer.mjs                          ← FrameRenderer + ffmpeg pipe
│   ├── motifs.mjs                            ← Motif registry
│   ├── math.mjs                              ← Deterministic math
│   ├── primitives.mjs                        ← Drawing primitives
│   ├── theme.mjs                             ← Themes
│   ├── fonts.mjs                             ← Font loading (EB Garamond, Noto, Source Serif 4, KaTeX)
│   ├── schema.mjs                            ← Pack validation
│   ├── scene-pack.schema.json                ← JSON Schema
│   ├── cli.mjs                               ← CLI entry point
│   │
│   ├── src/
│   │   ├── argument-diagram.mjs              ← v1 motif (423 lines, proven)
│   │   ├── argument-diagram-v2.mjs           ← v2 motif (authored timing)
│   │   ├── argument-diagram-v3.mjs           ← v3 motif (utterance-based)
│   │   ├── argument-diagram-v4.mjs           ← v4 motif (sharp + buggy)
│   │   ├── argument-diagram-v5.mjs           ← v5 motif (instant, current)
│   │   └── argument-display.mjs              ← logical-argument motif
│   │
│   ├── packs/
│   │   ├── logicvid-04.json                  ← v1 pack (7 scenes, proven)
│   │   ├── logicvid-04-mono.json             ← Monochrome variant
│   │   ├── logicvid-reality-appears.template.json  ← v2 template
│   │   ├── logicvid-v3.json                  ← v3 pack (abandoned)
│   │   ├── logicvid-v4.json                  ← v4 pack (broken bold text)
│   │   └── logicvid-v5.json                  ← v5 pack (current)
│   │
│   ├── tools/
│   │   ├── validate-logicvid.mjs             ← 204-check validation schema
│   │   ├── render-v5.mjs                     ← v5 render script
│   │   ├── build-film.sh                     ← Full TTS+render pipeline
│   │   ├── compile-timed-pack.py             ← Sets durations from TTS audio
│   │   └── analyse-audio.py                  ← Librosa feature extraction
│   │
│   ├── narration/
│   │   ├── narration-scenes.json             ← 9-scene narration script
│   │   └── full-narration.txt                ← Concatenated narration
│   │
│   └── build/audio-scenes/                   ← Per-scene TTS MP3s
│       ├── lv01.mp3 ... lv09.mp3
│
└── docs/
    └── SKIA-FRAMEWORK-MANUAL.md              ← Full Skia framework manual
```

## What We Need From You

Look at the above context, especially:
1. The v1 pack (`logicvid-04.json`) — this is the proven baseline
2. The v1 motif (`src/argument-diagram.mjs`) — the renderers are good
3. The postmortem (`logicvid-postmortem.md`) — what went wrong
4. The Skia framework manual (`docs/SKIA-FRAMEWORK-MANUAL.md`) — rendering capabilities

Then design a NEW approach for the logicvid system that solves:
1. How to get accurate word-level audio sync with the available tools
2. The right timing model (even? authored? aligned?)
3. A clean visual design: white background, no circles, sharp typography, bold/math rendering
4. Fix the styledText center bug in v1
5. A 9-scene pack for "Why Does Reality Appear?" that actually works

The v2 logicvid-reality-appears.zip contained a complete package with:
- `argument-diagram-v2.mjs` (authored timing motif)
- `logicvid-reality-appears.template.json` (9-scene template)
- `narration-scenes.json` (full 9-scene script)
- `build-film.sh`, `compile-timed-pack.py`, `render-logicvid.mjs`
- `apply-logicvid-framework-patch.mjs`

This is on the right track but the timing was wrong because the authored `start`/`end` values didn't match the actual narration rhythm. The motif itself is good — it just needs accurate timing.
