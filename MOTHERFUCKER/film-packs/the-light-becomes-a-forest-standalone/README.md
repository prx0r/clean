# The Light Becomes a Forest

A standalone ten-minute audiovisual essay-film asking:

> If consciousness is complete and free, why does it appear as finite living
> beings with boundaries, needs, conflict, care, and biological drives?

The piece does not place narration over an unrelated animation. One authored
trajectory controls narration, a six-part original fugue, procedural
orchestration, GLSL topology, color, motion, musical reactivity, rasa, and the
recognition event.

## The world

The film inhabits a **contrapuntal forest**. One five-lobed white-gold seed
becomes:

```text
radiance → difference → three powers → constraint → metabolism → appetite
→ nested selves → conflict → reciprocity → ecosystem → recognition → abundance
```

Every musical voice has a visual agency: cello becomes earth and root, viola
becomes inner branch, violin becomes leaf, flute becomes wind, oboe becomes
light, and harpsichord becomes river. Their amplitudes deform geometry before
color finishing; audio is structural rather than decorative.

The same seed is recognized through scale and transformation. It returns as
cell membrane, desire-field, multiscale organism, exchange node, leaf, river,
and constellation. No on-screen labels are required.

## Six-dimensional control

All renderers consume:

```text
A(t) = [radiance, localization, appetite,
        reciprocity, fecundity, recognition]
```

These are authored compositional controls, not measurements of consciousness,
biology, value, rasa, or spiritual attainment. Their definitions and mappings
are in `composition.json`.

The visual renderer receives:

```glsl
u_stateA = vec4(radiance, localization, appetite, reciprocity);
u_stateB = vec2(fecundity, recognition);
u_musicA = vec4(bass, inner, upper, continuo);
u_musicB = vec2(tension, subject_presence);
```

It also receives `u`, `t`, `u_audioVolume`, `u_audioBeat`, `u_stage`,
`u_local`, and `u_tattva`.

## The music

`generate_score.py` creates a deterministic format-1 MIDI file with a conductor
track and six musical tracks:

1. Earth Cello
2. Root Viola
3. Leaf Violin
4. Wind Flute
5. Light Oboe
6. River Harpsichord

The original subject is defined by twelve intervals:

```text
0, 7, 5, 3, 2, 0, 2, 3, 5, 3, 2, 0
```

It is developed through tonal answer, inversion, augmentation, diminution,
retrograde, inverse augmentation, stretto, double canon, chorale, and six-part
return. The generated score contains 7,044 note events and 51 explicitly
catalogued subject entries. It evokes Baroque contrapuntal thinking without
copying a Bach melody.

`render-audio.py` is SoundFont-free. It parses the MIDI and synthesizes the six
instrument families with NumPy. A WAV render needs no FFmpeg; other formats use
FFmpeg for encoding.

## Recognition

At 516 seconds the ecosystem begins to unbind. The score gathers into an
augmented chorale, cadences at 539.5, and is literally silent from 540 through
545 seconds. The visual field stays alive without musical features.

At exactly 545 seconds the seed returns with:

> You are not a fragment exiled from the light. You are the light, made local
> enough to care.

At 548 seconds the six-part forest enters. The philosophical sentence is
explicitly presented as Trika's wager, not as a laboratory conclusion.

## Use

From this directory:

```bash
python -m pip install -r requirements.txt
python generate_score.py
python validate.py
python render-audio.py --output build/score.wav
python render.py --contact-sheet
```

Render an exact moment:

```bash
python render.py \
  --frame 545 --width 1280 --height 720 \
  --output build/recognition.png
```

Render a video interval:

```bash
python render.py \
  --video --start 516 --end 568 --fps 24 \
  --output build/recognition.mp4
```

The image renderer requires an OpenGL 3.3-capable runtime. It attempts EGL
first, then the platform default. `glsl/film.glsl` is the entry point and all
includes are local to this pack.

## Directory contract

```text
composition.json          master trajectory, state, rasa, score, and limits
essay.txt                 time-aligned narration
engine.py                 trajectory interpolation and uniform generation
generate_score.py         dependency-free deterministic MIDI composition
render-audio.py           SoundFont-free procedural audio synthesis
render.py                 still, contact-sheet, and video rendering
score.mid                 generated seven-track format-1 MIDI
score_manifest.json       inspectable score analysis and subject catalogue
validate.py               semantic, MIDI, timing, and silence hard gates
glsl/film.glsl            GLSL 330 host contract
glsl/forest_fugue.glsl    continuous twelve-movement visual composition
glsl/include/*.glsl       local shader dependencies
ARCHITECTURE-ANALYSIS.md  engineering and extension protocol
CREATIVE-PROCESS-NOTES.md stage decisions and reusable composition method
REVIEW.md                 perceptual review and revision record
SOURCES.md                research basis and epistemic boundaries
SHA256SUMS                final integrity manifest
```

The directory has no dependency on Git history or on the source repository.
