# Architecture Analysis

## 1. Objective and invariant

This project is one ten-minute composition rendered through several media. The
invariant is:

```text
one clock + one semantic state + one musical organism + several renderers
```

`composition.json` is authoritative. Narration, MIDI generation, audio
synthesis, shader geometry, transitions, and validation all consume that
authored timeline. No subsystem contains an independent chapter list.

The central question is not treated as a sequence of illustrated claims.
Instead, each movement performs one cognitive action:

```text
undivided field
  → distinguish
  → localize
  → value
  → coordinate
  → conflict
  → widen care
  → recognize identity through transformation
```

The engineering criterion follows: if a stage cannot be identified by its
motion and relation alone, it has not yet been successfully composed.

## 2. Data flow

```text
composition.json
      |
      +--> engine.py ------------> state, stage, music proxies, uniforms
      |                                  |
      |                                  +--> render.py --> GLSL --> frames
      |
      +--> generate_score.py ----> score.mid + score_manifest.json
      |                                  |
      |                                  +--> render-audio.py --> PCM/audio
      |
      +--> essay.txt ------------> narration aligned to the same intervals
      |
      +--> validate.py ----------> structural and synchronization hard gates
```

The score generator and validator import the same `TempoMap`. Timing is
converted from authored seconds to MIDI ticks once, with the interval BPM active
at that point. This prevents silence, narration, and musical return from
drifting apart.

## 3. The Abundance State Vector

The ordered state is:

```text
A(t) = [radiance, localization, appetite,
        reciprocity, fecundity, recognition]
```

Each dimension has a low/high semantic definition and a separate visual,
musical, and narrative mapping in `composition.json`.

| Axis | Visual control | Musical control | Narrative control |
|---|---|---|---|
| radiance | transmission, negative-space light, common material | upper-partial openness, consonant common tones | how directly awareness is treated as self-manifesting |
| localization | boundary hardness, scale separation, parallax | register identity, voice independence, spatial pan | strength of finite perspective |
| appetite | gradient seeking, contraction, directed growth | dominant pressure, syncopation, chromatic approach | need, preference, and directed concern |
| reciprocity | exchange paths, mutual deformation, entrainment | imitation, suspension exchange, call/response | care, co-regulation, and second-person relation |
| fecundity | branching depth, phyllotaxis, particle and species count | voice count, ornament, sequence, stretto | number of scales and consequences carried |
| recognition | seed recurrence across cell, river, leaf, flock | subject completeness across transformation | felt invariance of the whole before it is named |

The vector is not a lookup table for style. A high value changes causal
behavior. For example, reciprocity increases exchange topology and imitation,
not merely pink saturation. Fecundity increases independent processes but is
counterweighted by recognition so density does not become illegible clutter.

### Interpolation

`engine.py` returns a `FrameState` containing global progress, stage, local
progress, six interpolated values, the tattva openness control, deterministic
audio features, and six musical features.

Interpolation blends a fluid cubic curve with a later disclosure curve. Strong
reciprocity and radiance favor continuity; strong localization delays
disclosure. The result allows a boundary to arrive as an event while exchange
and illumination remain continuous.

## 4. Music leads the image

The score is not an atmospheric bed. It is an original six-part fugue whose
formal development determines the film.

### Voices

| Track | Musical function | Visual agency |
|---|---|---|
| Earth Cello | bass, ground, augmentation | soil depth and roots |
| Root Viola | inner counterpoint | branches and connective membranes |
| Leaf Violin | subject clarity and ornament | leaves, cells, and upper growth |
| Wind Flute | mobile answer | wind, migrating arcs, and travelling exchange |
| Light Oboe | luminous inversion | apertures, seed halos, and recognition |
| River Harpsichord | pulse and continuo | river current and fine branching |

The shader receives four grouped voice-energy controls, tension, and
subject-presence. These alter field coordinates, SDF scale, branching drive,
contour density, and travelling pulses before tone mapping. A muted voice
therefore removes an agency from the visual ecology.

### Fugue grammar

The subject is original to this composition. Its twelve interval values and
twelve rhythmic values are declared in the master data. Transformations include:

- fragment;
- original and answer;
- inversion;
- augmentation and inverse augmentation;
- diminution;
- retrograde;
- stretto;
- double canon;
- chorale gathering;
- simultaneous six-voice return.

`score_manifest.json` records every explicit appearance, stage event counts,
technique, state mapping, and a SHA-256 of `composition.json`. Validation checks
the actual MIDI event graph against that manifest.

### Procedural audio

`render-audio.py` parses the format-1 MIDI without a MIDI library and synthesizes
six timbral families:

- bowed harmonic cello;
- gently beating viola;
- brighter bowed violin;
- breath-shaped flute;
- odd-harmonic oboe;
- short harpsichord pluck.

It writes through a disk-backed NumPy buffer, normalizes to the requested peak,
and creates 16-bit stereo PCM. Envelopes terminate within note spans. There is
no uncontrolled reverb tail because any tail could violate formal silence.

## 5. Visual architecture

`glsl/film.glsl` is the host contract. It declares all uniforms, constructs an
`AbundanceState`, normalizes coordinates, and calls `renderForestFugue()`.

`glsl/forest_fugue.glsl` owns the continuous world:

- a midnight mineral field;
- one five-lobed seed SDF;
- noise-driven living warp;
- Bezier-like sampled branches;
- vein and membrane geometry;
- voice-linked ribbons and travellers;
- twelve semantic stage functions;
- causal crossfades;
- common film finishing.

The local include library provides SDFs, hashes, fBm, curl fields, interference,
caustics, projective transforms, gamut treatment, grain, vignette, and
tone-mapping. The pack contains every include it uses.

### Stage morphing

Near most interval endings, current and next stages are evaluated together.
Curl displacement pushes them through one another before the blend. The result
is transformation of one material world, not a slideshow.

Stage ten is deliberately exceptional. Its crossfade is delayed until after the
545-second returned seed becomes fully legible. Stage eleven contains latent
forest energy at local time zero, so the 548-second cut reads as release rather
than a dropped frame.

## 6. Recognition transaction

Recognition is a transaction across all media:

| Time | Score | Visual | Narration |
|---:|---|---|---|
| 516.0 | augmented chorale begins | ecosystem unbinds into still blue depth | the identity question returns inward |
| 539.5 | cadence | subject traces suspend | language releases its claim to lead |
| 540.0–545.0 | exact MIDI and PCM silence | non-audio field remains alive | no narrated sentence |
| 545.0 | subject and inversion re-enter | one white-gold seed returns | key recognition sentence |
| 548.0 | six-part final exposition | the seed becomes a plural forest | biological and metaphysical claims are separated again |

`playable_spans()` clips or splits every proposed MIDI note around the silence
window. `engine.py` forces `u_audioVolume`, `u_audioBeat`, `u_musicA`, and
`u_musicB` to exact zero inside the window. `validate.py` parses the resulting
MIDI note spans and fails if any span overlaps it.

## 7. Epistemic separation

The composition uses two levels of claim:

1. Biological models describe bounded self-maintenance, allostasis, active
   inference, and multiscale agency.
2. Trika metaphysics interprets limitation as the free localization of
   consciousness.

The film treats their structural resonance as artistically productive. It does
not claim that active inference proves Trika, that the tattvas are brain
modules, that an ecosystem is literally one mind, or that a state-vector value
measures spiritual attainment.

Tattva level contributes an authored openness constraint. It does not assign
historical colors, frequencies, organs, or emotions to tattvas.

## 8. Validation and reproducibility

`validate.py` checks:

- exact 600-second duration;
- six named axes and thirteen ordered waypoints;
- range, rasa, tattva, chord, and unique-verb integrity;
- twelve semantic narration intervals and performance-appropriate word count;
- key-sentence presence and timing;
- required standalone files;
- format-1 MIDI structure, seven tracks, 480 ticks per beat;
- manifest hash and actual note count;
- subject-development coverage;
- literal five-second silence and exact 545-second re-entry;
- zero audio-derived visual features inside silence.

The intended verification sequence is:

```bash
python generate_score.py
python validate.py
python -m py_compile *.py
python render.py --contact-sheet
python render-audio.py --start 538 --end 549 --output build/hinge.wav
```

For clean-room testing, extract the archive into an empty directory and repeat
the sequence. Git metadata is neither present nor required.

## 9. Extension protocol

A future composition should preserve the architecture while replacing the
content:

1. Write one question whose answer requires a transformation, not a list.
2. Choose six continuous controls that affect causal behavior in every medium.
3. Design the musical subject before individual scenes.
4. Give each movement one verb and one perceptual test.
5. Let harmony, voice count, and transformation decide visual topology.
6. Reserve an exact recognition transaction and validate it numerically.
7. Render opening, mature, and transition frames for every stage.
8. Reject any stage that is attractive but semantically interchangeable.
9. Document scientific claims and metaphysical claims separately.
10. Package the entire runtime contract, not only the artwork.
