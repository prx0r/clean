# Architecture Analysis

## 1. System objective

This project is an integrated ten-minute composition, not a voiceover plus a
shader playlist. One authored semantic trajectory controls:

- the timed narration;
- the six-dimensional conceptual state;
- score density, harmony, rhythm, and orchestration;
- shader topology, material, camera implication, and transition behavior;
- audio-reactive features;
- the exact recognition silence and return.

The central engineering rule is **one clock, one state, several renderers**.
`composition.json` is the authority. Python, MIDI, and GLSL are consumers of
the same authored trajectory.

## 2. Standalone directory

```text
composition.json
essay.txt
engine.py
generate_score.py
render-audio.py
render.py
validate.py
score.mid
score_manifest.json
glsl/
  film.glsl
  phononic_film.glsl
  include/
    primitives.glsl
    visionary.glsl
    cinema.glsl
    signature.glsl
```

The four files in `glsl/include/` are the only shared shader dependencies.
`render.py` searches beside the requesting shader and then in
`glsl/include/`, so the extracted pack does not need the original repository.

Runtime dependencies:

- score generation and validation: Python standard library;
- audio rendering: NumPy; FFmpeg only for FLAC/M4A/MP3/OGG;
- image/video rendering: NumPy, Pillow, ModernGL, and an EGL-capable OpenGL
  runtime;
- raw shader compilation: any GLSL 330 compiler such as `glslangValidator`.

## 3. Data flow

```text
composition.json
      |
      +--> engine.py -------------> per-frame state/uniforms
      |                                  |
      |                                  +--> render.py --> GLSL --> image/video
      |
      +--> generate_score.py -----> score.mid + score_manifest.json
      |                                  |
      |                                  +--> render-audio.py --> WAV/FLAC/etc.
      |
      +--> validate.py -----------> structural and synchronization gates
      |
      +--> essay.txt -------------> narration aligned to the same intervals
```

No renderer owns narrative timing. A stage begins because the corresponding
waypoint says it begins, not because a shader or musical script contains a
second independent chapter list.

## 4. Composition schema

`composition.json` contains 13 waypoints defining 12 semantic intervals over
600 seconds. Each waypoint carries:

- `time`, `id`, `title`, and a unique `visual_verb`;
- a six-number state vector;
- dominant and supporting rasa;
- a tattva-based artistic constraint;
- BPM, chord description, MIDI pitches, and score behavior;
- narration and visual intent metadata.

The final waypoint closes interpolation; it is not a thirteenth scene.

The six axes are ordered:

```text
[articulation, continuity, deixis,
 resonance, prosody, semantic_density]
```

They are compositional controls, not empirical measurements.

### Articulation

Controls how sharply the field separates into edges, phoneme-like marks,
attacks, register differences, and explicit claims.

### Continuity

Controls whether events remain isolated or are carried as one evolving gesture.
It drives shader trails, score overlap, common tones, and narrative carry.

### Deixis

Controls pointing and ownership: how strongly image, harmony, and narration
privilege an object, speaker, centre, “this,” or “I.”

### Resonance

Controls phase agreement among color, pressure fields, score voices, sensory
cues, and the felt fit of an argument.

### Prosody

Controls rhythmic confidence, phrase spacing, travelling fronts, metric
reliability, and rhetorical cadence.

### Semantic density

Controls relational compression: polyphony, interference depth, motif
availability, contextual dependence, and conceptual load.

## 5. Interpolation engine

`engine.py` supplies the same state to tests and rendering.

### Segment selection

`segment_at()` locates the active semantic interval and returns normalized local
time. Film progress and local stage progress remain separate. The shader gets
both:

- `u`: global progress from 0 to 1;
- `u_local`: progress inside the current semantic interval.

### Meaning-aware interpolation

`interpolation_amount()` blends two curves:

- fluid cubic interpolation;
- a later disclosure curve.

High continuity favors fluid morphing. Low continuity delays the new state,
making a change disclose itself as a more discrete event. This prevents every
axis from behaving like an ordinary linear automation lane.

### Tattva constraint

The chosen tattva level is not mapped to a historical color or sound. Its
`constraint` value is interpolated into `u_tattva`, an artistic openness
control. This keeps the cultural reference explicit while avoiding false
technical correspondences.

### Audio proxy uniforms

The shader can be rendered without decoding a waveform. `audio_features()`
derives deterministic `u_audioVolume` and `u_audioBeat` from the same tempo and
state vector. During the formal silence both are forced to exactly zero.

For a production engine with real audio analysis, these two uniforms may be
replaced by measured RMS/onset values, but the formal silence and semantic
state must remain authoritative.

## 6. MIDI generation

`generate_score.py` writes format-1 MIDI without external libraries.

### Track roles

1. **Breath Spectrum** — the copper continuity object in sound.
2. **Vowel Pillars** — slow resonance and formant-like harmony.
3. **Consonant Glass** — transient differentiation.
4. **Syntax Braid** — a four-note identity progressively disclosed.
5. **Semantic Bloom** — appears only after sentence-level integration.

The conductor track carries tempo and chapter markers.

### Continuity motif

```text
A2 E3 B3 C#4
45 52 59 61
```

Semantic density determines how much of this identity can be inferred. The
opening exposes one pitch; the vowel chamber exposes two; naming exposes three;
the sentence organism allows all four. The complete motif returns with the key
sentence at 547 seconds.

### Exact time conversion

`TempoMap` converts authored seconds to ticks using each interval's starting
BPM. The same class is imported by validation and audio rendering, eliminating
tempo-map drift between generation and inspection.

### Silence clipping

Every proposed note is passed through `playable_spans()`. A note crossing the
formal silence is split or clipped before MIDI events are written. Silence is
therefore encoded in the actual event graph rather than asserted only in
metadata.

## 7. Procedural audio rendering

`render-audio.py` parses the generated MIDI itself. It needs no SoundFont and no
General MIDI synthesizer.

The five track names select five procedural timbres:

- stable copper fundamental with granular breath;
- slowly detuned vowel/formant bands;
- brief inharmonic consonant glass;
- compact plucked syntax spectrum;
- wide beating semantic bloom.

The renderer mixes through a temporary disk-backed NumPy array, so the complete
ten-minute film does not require holding an uncompressed stereo master in RAM.
It writes 16-bit stereo WAV directly and invokes FFmpeg only for compressed
formats.

Envelopes terminate inside each MIDI note. There is deliberately no global
reverb tail, because a tail could leak across the six-second aperture.

## 8. Shader architecture

`glsl/film.glsl` is the host contract. It declares uniforms, creates the
`MeaningState`, and calls the film renderer.

`glsl/phononic_film.glsl` owns the artwork:

- a shared obsidian/violet pressure ground;
- one copper breath-thread;
- twelve material transformations;
- causal transition warps;
- state- and audio-driven topology;
- shared film finishing.

The four include libraries provide:

- SDFs, noise, color, easing, and basic glow;
- curl fields, caustics, interference, and spectral functions;
- cinematic projective/log-polar transformations;
- reusable semantic timing and film finishing.

### Stage dispatch

`renderPhononicStage()` maps the current stage number to a drawing function.
The current and next stages are both evaluated near an interval ending, and a
curl-driven material morph blends them. This keeps history visible and prevents
hard slideshow cuts.

### Audio rule

Audio changes field coordinates, contour density, wave topology, phase, and
segmentation before final color treatment. It is not merely multiplied into
exposure.

### Text rule

No explanatory caption is required. Titles exist in JSON and review sheets,
not in the rendered film. A stage must survive silent viewing.

## 9. Recognition event

The event is specified once:

```text
526.0  visual unbinding begins
540.5  cadence
541.0  literal silence begins
547.0  key sentence and motif return
558.0  full transparent speech
```

At 541–547 seconds:

- actual MIDI contains no sounding note interval;
- engine audio uniforms are exactly zero;
- the shader retains a slow violet standing wave driven by time and material
  state, not audio;
- no reverb tail is generated by the procedural audio renderer.

At 547 seconds, the copper line, pearl focus, score motif, and narration all
return together.

## 10. Validation architecture

`validate.py` checks:

- exact duration and waypoint count;
- strict waypoint ordering and unique IDs/visual verbs;
- six values per state, all within `[0,1]`;
- valid rasa names;
- selected conventional tattva level/name pairs;
- narration word count and timed section count;
- existence of core deliverables;
- MIDI format, tracks, division, and well-paired note intervals;
- composition hash in the score manifest;
- manifest event count against parsed MIDI notes;
- motif identity;
- no note crossing the formal silence;
- a note-on exactly at the key sentence;
- zero derived audio features inside silence and return at 547.

Validation parses the MIDI itself. It does not trust the manifest.

## 11. Extension protocol

To build a new composition:

1. Write one exact question and one experiential thesis.
2. Choose a continuity object capable of every required transformation.
3. Define 10–14 semantic intervals with unique causal verbs.
4. Define six axes that are genuinely useful across image, music, and
   narration.
5. Author waypoint values before writing shader detail.
6. Give each stage a silent-viewing action and an audio-only action.
7. Design one recognition event with exact cadence, absence, and return times.
8. Generate score and narration from the same waypoint structure.
9. Implement one material world rather than separate illustrations.
10. Render opening, mature, transition, and recognition frames.
11. Reject repeated composition grammar even when the frames are individually
    attractive.
12. Encode hard timing and epistemic limits in validation.

The reusable architecture is the shared clock, state, tests, and review method.
The subject, palette, geometry, continuity object, score organism, and rasa arc
should be reinvented.

