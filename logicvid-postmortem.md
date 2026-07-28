# Logicvid Postmortem — 2026-07-28

## What We Tried

5 iterations of the argument-diagram motif in a single session, attempting to build a Whisper-timed, instant-rendering logicvid film.

## What Went Wrong

### 1. No forced alignment tool available
Word-level sync requires aligning known text to audio at the phoneme level. We tried using Whisper tiny timestamps as a substitute. Whisper tiny is a speech-recognition model, not a forced aligner — its word timestamps drift 100-300ms. This is the difference between "word appears when spoken" and "word appears late." We never installed the right tool (`aeneas`, `whisperx`, `gentle`).

### 2. Step-function timing reveals every imperfection
The user wanted instant rendering (no fade, no animation). This means text pops on screen at a specific frame. When the timing is off by even 2 frames (80ms at 24fps), it feels wrong. With v1's smooth transitions, timing errors were hidden by the animation. With instant rendering, every millisecond of misalignment is visible.

### 3. Overengineering the wrong things
We built 5 motif variants, a validation script with 204 checks, per-node timing for concept-maps, and a Whisper pipeline — but we never solved the core problem of getting accurate timestamps. We optimized what we could control and ignored what we couldn't.

### 4. The "circles" distraction
The `drawSubtleField` function and background rings were carried over from v1. In v1 they were subtle (0.04 alpha, animated arc). In later versions they became full static circles. The user's feedback about "2 circles" was a symptom of visual regression across versions — we kept adding visual noise without realizing it.

### 5. Cumulative complexity
v1: 423 lines, 10 move types, simple timing.
v5: 229 lines (after stripping), 7 move types, per-node timing, concept-map, whisper integration, validation schema.

Each version added complexity without fixing the fundamental sync problem. v1 was actually cleaner and more reliable because it didn't try to solve word-level sync.

## What Works (From v1)

- Clean white background
- Simple centered typography
- Even timing per move (`smoothstep(i/n, (i+1)/n, t)`)
- Exact scene durations from audio
- Subtle field lines that animate in (not static circles)
- The 10 move types (claim, subclaim, refutation, branch, converge, divider, premises, side-by-side, dialogue, concept-map)
- 7-scene argument structure with clear progression

## If Someone Tries Again

1. **First, get forced alignment working.** Install aeneas or whisperx in a venv. Verify word timestamps against known audio before writing any rendering code.
2. **Don't build a new motif.** Use the existing v1 motif with authored `start`/`end` timing (like v2 did). The v1 renderers are proven and sharp.
3. **Validate timing before rendering.** Write a script that overlays word timestamps on an audio waveform. Check visually that timestamps match the speech.
4. **Use the existing compile-timed-pack.py approach** — exact scene durations from TTS length, normalized timing within each scene.
5. **Don't mix concerns.** The timing system (when things appear) should be separate from the rendering system (how things look). We fused them and couldn't debug either.

## Current File State

Motifs in `src/`:
- `argument-diagram.mjs` (423 lines) — v1, proven, working
- `argument-diagram-v2.mjs` (76 lines) — v2, authored start/end timing
- `argument-diagram-v3.mjs` (320 lines) — v3, utterance-based, abandoned
- `argument-diagram-v4.mjs` (326 lines) — v4, sharp renderers + broken styledText
- `argument-diagram-v5.mjs` (192 lines) — v5, instant rendering, current

Packs in `packs/`:
- `logicvid-04.json` — v1, original, known good
- `logicvid-v5.json` — current, needs accurate word timestamps

Use `logicvid-04.json` with `argument-diagram` (v1) as the baseline. Don't touch the motif. Just write better packs.
