# Logicvid Handover — 2026-07-28

## What We Built

5 versions of the argument-diagram motif in a single session, iterating from a static slideshow to a whisper-timed, instant-rendering argument film engine.

---

## The Evolution

### v1 — Original (`src/argument-diagram.mjs`, 423 lines)
The starting point. Clean white background, 10 move types (claim, subclaim, refutation, branch, converge, divider, premises, side-by-side, dialogue, concept-map). Used even timing: each move gets `1/n` of scene duration. No authored timing control. No persistence. Used in `logicvid-04.json` (the first logicvid pack).

**Key design:** `drawSubtleField()` — 3 concentric rings that pulse slowly. Clean white `#fafaf8` background. Text centered with `styledText()` which had a center-align bug: `if (align === "center") { fillText(part, x, y); break; }` — only renders the first text segment, drops all **bold** and *italic* markers.

### v2 — Authored timing (`src/argument-diagram-v2.mjs`, 76 lines)
Delivered as a zip overlay (`logicvid-reality-appears.zip`). Added `start`/`end` normalized timing (0-1 per scene), `persist: true` for cumulative reasoning, `concept-map` and `pulse-path` move types, text auto-wrapping, per-move color. Also added Source Serif 4 font, `env.seconds`/`env.sceneSeconds` to render context. Used in `logicvid-reality-appears.json`.

**Problems:** overlapping move windows (persist + fadeout caused text pileup), same concentric-ring background every scene, no word-level audio sync.

### v3 — Utterance-based (`src/argument-diagram-v3.mjs`, 320 lines)
Switched from moves to "utterances" with `at` in seconds. 5 background modes (dark-field, clean-white, warm-glow, tension-split, resolve). Typographic hierarchy (say/emphasize/statement/controversial/resolution/term/aside/math). New diagram primitives (triangle, split, stack, flow, scale). No overlap — one utterance at a time.

**Problems:** backgrounds were ugly (black text on dark backgrounds unreadable), custom diagram renderers weren't as sharp as v1 originals, too many utterances per scene (felt like subtitles).

### v4 — Back to v1 sharpness (`src/argument-diagram-v4.mjs`, 326 lines)
Reverted to v1-style clean white background + `drawSubtleField()`. Reused v1's proven renderer designs. Authored `at`/`duration` in seconds. Fewer moves per scene (2-4 anchors). Fade-out at end of move window.

**Problems:** `styledText()` center-align bug still present — **bold** text in centered claims never rendered. Timing estimated by word count, not matched to audio. Text appeared 1-3s after narrator said it.

### v5 — Whisper-timed instant rendering (`src/argument-diagram-v5.mjs`, 192 lines)
**Current. What you just watched.** Stripped all animation: no smoothstep, no scale, no fade-in, no fade-out. Text appears instantly at full opacity when the narrator says it. Uses exact word timestamps from whisper tiny model on each scene's TTS audio. Each move's `at` is the first word's start time from whisper. `duration` is the last word's end time minus the first word's start time.

---

## Critical Bug Found & Fixed

**`styledText()` center-align truncation.** In v1, v2, v3, and v4, the `styledText` function had:
```js
if (align === "center") { ctx.fillText(t, x, y); break; }
```
For centered text with **bold** or *italic* markers, it rendered only the first text segment and broke out of the loop. Everything after the first word with formatting was silently dropped. "Why is any process **manifest** rather than merely occurring?" showed only "Why is any process " on screen. Six of nine scenes had bold markers. The entire v4 render was broken.

**Fixed in v5:** Measure all segments' total width first, render as centered group left-to-right. No break statements.

---

## File Locations

### Motif Files
| File | Lines | Status | Description |
|------|-------|--------|-------------|
| `src/argument-diagram.mjs` | 423 | WORKING | v1 — even timing, 10 move types |
| `src/argument-diagram-v2.mjs` | 76 | WORKING | v2 — authored start/end, persist, concept-map |
| `src/argument-diagram-v3.mjs` | 320 | LEGACY | v3 — utterance-based, too complex |
| `src/argument-diagram-v4.mjs` | 326 | LEGACY | v4 — sharp renderers, buggy styledText |
| `src/argument-diagram-v5.mjs` | 192 | WORKING | v5 — instant rendering, no animation |

### Scene Packs
| File | Motif | Scenes | Status |
|------|-------|--------|--------|
| `packs/logicvid-04.json` | v1 | 7 | WORKING - original |
| `packs/logicvid-04-mono.json` | v1 | 7 | UNTESTED |
| `packs/logicvid-reality-appears.json` | v2 | 9 | WORKING - v2 render |
| `packs/logicvid-v3.json` | v3 | 9 | LEGACY |
| `packs/logicvid-v4.json` | v4 | 9 | LEGACY - broken bold text |
| `packs/logicvid-v5.json` | v5 | 9 | CURRENT - whisper-timed |

### Narration
| File | Description |
|------|-------------|
| `narration/narration-scenes.json` | Original 9-scene narration script |
| `build/audio-scenes/lv*.mp3` | Per-scene TTS audio (edge-tts, SoniaNeural) |
| `/tmp/whisper-all/lv*.json` | Whisper word-timestamp JSON for each scene |

### Kernel Patches Applied
- `motifs.mjs` — all 5 argument-diagram variants registered
- `renderer.mjs` — all 5 variants added to clean-scene check (no border/footer)
- `fonts.mjs` — Source Serif 4 font registration added
- Font symlink: `assets/fonts/source-serif-4/SourceSerif4-Variable.ttf` → `node_modules/source-serif/VAR/SourceSerif4Variable-Roman.ttf`

---

## The v5 Approach

### Rendering Philosophy
- **No animation.** Text appears instantly at full opacity when the narrator says it.
- **No fade-in.** `alpha(t)` always returns 1.
- **No scale.** Claims render at full size from frame 1.
- **No fade-out.** Text disappears instantly when its duration window ends.
- **All timing from whisper.** Every move's `at` is the exact second the first word of that phrase is spoken.

### Move Activation
```js
const st = (move.at ?? 0) / dur;     // normalized start
const en = ((move.at ?? 0) + (move.duration ?? 4)) / dur;  // normalized end
if (t < st || t > en) continue;      // outside window → skip
const localT = (t - st) / (en - st); // 0→1 within window
```
`localT` is used only for internal sequencing (premises stacking, concept-map node reveal). No smoothing.

### Diagram Types
- **side-by-side** — left and right columns with divider line. Both sides appear within 0.06s of each other.
- **concept-map** — central term with radiating nodes and connecting lines. Central appears at `t=0.02`, nodes at `t=0.08 + i*0.06`.
- **branch** — multi-way branching from center. Branches appear at `t=0.03 + i*0.06`.
- **premises** — vertical stacking with conclusion line. Premises at `t=0.02 + i*0.08`, conclusion at `t=0.7`.
- **converge** — single centered statement with ring. Text at `t=0.02`.
- **claim** — centered claim with optional strikethrough (refuted) or ring (highlight).
- **subclaim** — smaller text below center.

### Typography
- **Bold** `**text**` — rendered at 700 weight in Source Serif 4
- **Math** `*text*` — rendered in KaTeX Math italic font
- Both work correctly in centered and left-aligned text (fixed in v5)

---

## What's Still Missing / Known Issues

### Word-Level Sync Is Approximate
Whisper tiny is fast but not perfectly accurate. The transcription has errors (e.g., "Abhinavagupta" → "A pin of a Gupta's", "Prakāśa" → "Procursure", "Trika" → "Tricker"). The timestamps are close but may drift by 0.1-0.3s. For perfect sync, use whisperX or a forced aligner like Gentle/montreal-forced-aligner.

### Scene 4 Premises Stack Is Still Long
A1-A5 as text is still a list. The user explicitly said no bullet points or long passages. Should be replaced with visual tokens (circles, shapes that stack into a structure) rather than text lines.

### No KaTeX Rendering
The KaTeX Math font is available and used for *italic* markers, but there's no proper LaTeX rendering (e.g., `\text{spanda} = \text{prakāśa} + \text{vimarśa}` as a formatted equation). The `katex` npm package is installed but we haven't wired `katex.renderToString()` → SVG → canvas.

### No Entrance/Exit Transitions
User explicitly rejected fade-in ("no fade-in BS"). But there's a middle ground between "instant pop" and "fade": the text could slide up 5px, or scale from 0.98→1.0 in 2 frames (0.08s). Anything under 100ms is perceived as instant but feels less jarring than a hard pop.

### Audio Manifest Not Used in v5
v5 motif doesn't read `env.audio` for ring-pulsing or subtle ambient reactivity. Easy to add back if desired.

### v5 Uses Scene Progress (t) Not Raw Seconds
The main loop still normalizes `at`/`duration` to scene progress (`t` going 0→1). This means if the scene's `duration` field doesn't match the actual TTS length, the timing drifts. Currently scene durations are set to match TTS length (from `compile-timed-pack.py` in the v2 build), but if they change, everything shifts.

---

## How to Make Another Logicvid

1. Write the essay/narration
2. Generate TTS per scene: `edge-tts --voice en-GB-SoniaNeural --text "..." --write-media build/audio-scenes/lvXX.mp3`
3. Run whisper for word timestamps: `whisper build/audio-scenes/lvXX.mp3 --model tiny --language en --word_timestamps True`
4. Read `lvXX.json` segments[].words[].start/end
5. Write scene pack with `"motif": "argument-diagram-v5"`, each move having `at` = first word's start, `duration` = (last word's end - first word's start)
6. Render: `node tools/render-v5.mjs`
7. Mux audio: `ffmpeg -i .../video.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest final.mp4`
8. Upload to R2: `aws s3 cp final.mp4 s3://blog-video-assets/logicvids/...`

### Scene Pattern (Per User Feedback)
- 2-4 anchors per scene max (not 7-9)
- Most narration is audio-only. Text only appears to frame the key tension.
- Each anchor phrase appears **exactly** when the narrator says the first word (whisper timestamp)
- Clean white background, subtle concentric rings
- Side-by-side for comparisons, concept-map for relationships, branch for three-way, premises for formal arguments, claim for key statements, subclaim for qualifiers

---

## R2 Uploads from This Session
- `blog-video-assets/logicvids/logicvid-reality-appears-final.mp4` — v2 render
- `blog-video-assets/logicvids/logicvid-v4-final.mp4` — v4 render (broken bold text)
- `blog-video-assets/logicvids/logicvid-v5-final.mp4` — v5 renders
- `blog-video-assets/logicvids/logicvid-v6-final-*.mp4` — v6: Edge TTS WordBoundary, semantic anchors, replacement groups, frame-native
- `blog-video-assets/logicvids/logicvid-v7-chatgpt-style-*.mp4` — v7: ChatGPT typography from Google Vision analysis

---

## v7 — ChatGPT Style Analysis

### Process
Used Google Vision API (with API key AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc) to analyze a ChatGPT response image (`ideal.png` uploaded to R2 bucket `blog-video-assets/logicvids/`). The image was a peer review of a Tantraloka document.

### What Vision API Detected
- Dimensions: 752x548, PNG
- Background: `#f5f5f5` (near-white, 84.9% of pixels)
- Divider lines: `#c1c1c1` (light gray, 8.2%)
- Secondary text: `#9f9f9f` (medium gray, 5.4%)
- Main text: `#242424` (near-black)
- 15 text blocks with clear hierarchy
- Horizontal divider at y=155
- Headers at y=103-129 (26px tall) and y=489-547 (58px)

### Typographic Techniques Found
1. **Numbered headers** (e.g., "3. New hypotheses produced by your synthesis") — bold, larger, left-aligned
2. **Bold verdict statements** (e.g., "Major revision, with a very strong underlying argument.") — standalone emphasis
3. **Numbered sub-sections** (1., 2., 3.) — clear hierarchical structure
4. **Inline code/notation** (e.g., "M→D B→N→W→R") — visually distinct from prose
5. **Sanskrit/italic terms inline** — italic styling within body text
6. **Thin horizontal divider lines** — separate sections cleanly
7. **Consistent left margin** (~22-30px) throughout
8. **Content width** ~689px on 752px canvas
9. **Monochrome palette** — meaning comes entirely from typography, no color accents

### Applied to Logicvid
| ChatGPT Technique | Logicvid v7 |
|---|---|
| Near-white background | `#fafaf8` (existing) |
| Near-black main text | COLORS.ink from statuses.mjs |
| Medium gray secondary | COLORS.muted for subclaims |
| Thin `#c1c1c1` divider rules | New `divider` move type, `verdict` shows rule above |
| Bold verdict statements | New `verdict` move type — left-aligned, bold, optional rule |
| Left-aligned body text | `"layout": "left"` on claims, subclaims use left alignment |
| Inline bold/italic | Already supported via `**bold**` and `*italic*` in rich-text.mjs |
| Monochrome | Status colors (blue/red/green/gold) reserved for semantic meaning |

### New Move Types
- **`verdict`** — ChatGPT-style bold statement with optional horizontal rule above. Left-aligned. Supports status colors. Used for conclusions and key judgments.
- **`divider`** — Thin horizontal rule at specified y-position. RGB `rgba(193,193,193,0.35)`. Used to separate argument sections.

### Alignment Options
- Claims now support `"layout": "left"` for left-aligned text (ChatGPT style). Default is centered (for emphasis moves).
- Subclaims always left-aligned with 80px margins, body text size.
- Verdict always left-aligned with optional rule.

