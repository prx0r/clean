# Rendering Pipeline

## Minimal audio-reactive pipeline

```bash
python tools/analyse-audio.py \
  audio/music.wav \
  build/features/music.json

node tools/render-with-signals.mjs \
  packs/film.json \
  build/features/music.json \
  build/film.mp4

ffmpeg -i build/film.mp4 -i audio/music.wav \
  -c:v copy -c:a aac -shortest build/film-final.mp4
```

## Music plus narration

Recommended order:

1. finalize or generate the score;
2. synthesize or record narration;
3. force-align narration or export TTS timings;
4. optionally create a premix;
5. analyze music and narration separately;
6. render visuals with both buses;
7. mix audio;
8. mux final audio with rendered video.

Do not analyze only the combined mix if you need music and narration to have
different visual responsibilities.

## Feature sampling

At frame `f`:

```js
const seconds = f / fps;
const audio = sampleAudioFeatures(audioManifest, seconds);
const narration = sampleNarrationFeatures(narrationManifest, seconds);
const score = sampleScoreFeatures(scoreManifest, seconds);
```

Feature manifests make arbitrary frame seeking deterministic.

## Stateful particles and random access

Particles are history-dependent. There are three solutions:

### Sequential render

Render frames in order. Simplest and appropriate for final video.

### Checkpoints

Persist particle state every few seconds. Useful for failed-stage rerenders.

### Analytic particles

Compute particle position from birth time, seed and fields without simulation.
Best for full random access, but more restrictive.

Use sequential rendering first.

## Review render

Before a full film:

```text
opening frame
25% frame
55% frame
82% frame
transition strip
```

For every custom mechanism.

Then render a 15–30 second proof with final audio routing.
