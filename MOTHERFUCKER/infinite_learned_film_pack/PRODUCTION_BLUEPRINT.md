# Production Blueprint — The Infinite Learned to Say “I Can’t”

## Production identity

- Source essay: `essays/the-infinite-learned-to-say-i-cant.md`
- Narration rewriting: none
- Visual program: `programs/infinite-learned-visual-program.json`
- Shot count: 44
- Draft runtime: 685.292 seconds / 11:25.292
- Output: one coherent visual-only Skia companion ready to receive narration
- Render: 1280×720, 24 fps, H.264, yuv420p
- Transitions: 0.65-second motif-preserving crossfades inside existing shot intervals

## Chapters

- **I. The Sentence of Limitation:** shots 1–2
- **II. Contraction into Perspective:** shots 3–6
- **III. The Five Lenses:** shots 7–13
- **IV. Time and Knowing:** shots 14–19
- **V. Desire and Smallness:** shots 20–25
- **VI. Power Builds the Boundary:** shots 26–27
- **VII. Practice Follows the Fold:** shots 28–30
- **VIII. The Center Turns Inside Out:** shots 31–33
- **IX. Recognition Without Erasure:** shots 34–37
- **X. The Tantric Reversal:** shots 38–40
- **XI. The Fist Loosens:** shots 41–44

## Continuous visual systems

### Luminous field

Gold-white luminosity represents the common substance of awareness. It is concentrated, filtered, occluded, sequenced, and reopened but never replaced.

### Crimson frame

The frame represents active limitation. It becomes point-of-view, lens, cage, causal wall, and opening gesture.

### Indigo locality

Indigo represents finite structure: the individual figure, selected ray, note, wave, or local ring. Recognition does not erase it.

### Gold current

Gold paths show continuity between universal power and local expression. The same current becomes attention, desire, breath, temporal sequence, and recognition.

### Opening gesture

Five arcs embody contraction as a reversible gesture. They close early, return as questioning, and finally loosen around the same luminous core.

## Visual mechanism families

- field and viewpoint: `constraint-field`, `point-of-view`;
- the five contractions: `five-lenses`, `local-power`;
- time and knowledge: `melody-time`, `attention-beam`;
- desire and smallness: `desire-orbit`, `smallness-cage`;
- active bondage and method: `powered-prison`, `practice-folds`;
- recognition and non-erasure: `upsurge`, `wave-ocean`, `textures-display`;
- final reversal: `limitation-reversal`, `opening-fist`.

## Timing method

The included proof uses draft timing:

- 155 spoken words per minute;
- 0.45 seconds of tail per shot;
- every shot rounded upward to a complete 24 fps frame;
- no shot longer than 30 seconds.

For publication, final narration owns the timeline:

1. record or synthesize the unchanged narration;
2. force-align the final audio to the 44 existing shot IDs;
3. create an exact timing manifest containing every shot;
4. rerun `render-essay` with `--timings`;
5. mux the final narration and the newly conformed video;
6. verify total audio/video difference and shot-boundary alignment.

The compiler rejects incomplete exact timing manifests, so draft and publication timing cannot be mixed silently.

## Commands

```bash
# Compile the essay plan without rendering
node src/cli.mjs compile-essay programs/infinite-learned-visual-program.json

# Render the draft-timed proof
node src/cli.mjs render-essay programs/infinite-learned-visual-program.json

# Render against complete final narration timing
node src/cli.mjs render-essay programs/infinite-learned-visual-program.json \
  --timings exact-timings.json
```

## Publication note

The proof MP4 has no audio because no final narration track was supplied. It is a complete timed visual companion, not a silent final master. The storyboard contains the exact passage assigned to every interval, making final narration conformance mechanical rather than interpretive.
