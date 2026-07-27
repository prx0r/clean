# The World Learns Its Own Name

A ten-minute integrated audiovisual essay-film about how pressure in air becomes
meaning. Narration, score, shader, rhythm, silence, and semantic transitions all
follow one time-varying six-dimensional **Meaning State Vector**:

```text
M(t) = [articulation, continuity, deixis,
        resonance, prosody, semantic_density]
```

These values are artistic controls, not measurements of consciousness,
language, brain activity, or rasa.

## The artistic world

The film inhabits a **phononic cathedral**: obsidian liquid glass carrying
spectral pressure, granular breath, caustic refraction, and semantic weather.
One copper breath-thread survives the full composition. It is not replaced by
illustrations. It learns to recur, resonate, accept context, crystallize into
names, fold into inner speech, disclose a sentence-organism, become argument,
reverse the listener, fall silent, and return as shareable speech.

The camera is progressively implicated in the utterance:

```text
witness -> resonator -> predictor -> speaker -> listener-in-the-word
```

No explanatory text is required on screen. Each passage must communicate a
distinct action under silent viewing while remaining one continuous material
world.

## The musical organism

`generate_score.py` writes a deterministic format-1 MIDI score with five music
tracks:

1. Breath Spectrum
2. Vowel Pillars
3. Consonant Glass
4. Syntax Braid
5. Semantic Bloom

The continuity motif is `A2 E3 B3 C#4` (`45, 52, 59, 61`). The film begins with
one available note. Further notes become audible as vibration gains chamber,
name, and sentence structure. The complete four-note organism first exists in
the sentence passage. The score contains 1,166 note events.

## The recognition event

At `08:46`, bounded meaning begins to unfasten. The score reaches its cadence at
`09:00.5` and becomes literally silent from `09:01` through `09:07`. A dark
violet standing wave remains visible without audio-derived motion.

At `09:07`, the copper thread and completed musical motif return together:

> A word is not a container. It is the world arriving in a form it can
> recognize.

At `09:18`, speech returns in full. The insight does not abolish words; it makes
them transparent enough to share a world without pretending to contain it.

## Generate, validate, and render

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
  --frame 547 --width 1280 --height 720 \
  --output build/recognition.png
```

Render an interval:

```bash
python render.py \
  --video --start 526 --end 566 --fps 24 \
  --output build/recognition.mp4
```

The renderer needs ModernGL, Pillow, NumPy, and an EGL-capable OpenGL runtime.
`glsl/film.glsl` is a standalone GLSL 330 entry point after include expansion.

## Directory contract

```text
composition.json         master trajectory and epistemic limits
essay.txt                time-aligned narration
engine.py                shared interpolation and audiovisual timing
generate_score.py        dependency-free MIDI composer
render-audio.py           SoundFont-free procedural audio renderer
score.mid                generated score
score_manifest.json      inspectable score structure
validate.py              semantic, MIDI, timing, and silence hard gates
render.py                still, contact-sheet, and interval renderer
glsl/film.glsl           standalone fragment entry point
glsl/phononic_film.glsl  continuous material world and transformations
glsl/include/*.glsl      local standalone shader dependencies
ARCHITECTURE-ANALYSIS.md system architecture and extension protocol
CREATIVE-PROCESS-NOTES.md stage, state, harmony, and revision rationale
REVIEW.md                perceptual and emotional review record
SOURCES.md               research basis and explicit limits
```
