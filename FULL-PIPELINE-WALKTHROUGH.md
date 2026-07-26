# Full Pipeline Walkthrough: From Essay to Rendered Film

## Starting Point: The Research Directive

We have 72 questions in `RESEARCH_DIRECTIVE.md`. One of them:

> Q41: "Is recognition an event in time or recognition of what was never absent?"

## Step 1: Research → Truth Map

The truth map already has this question:

```json
{
  "question_id": "q:recognition-event-in-time",
  "status": "underdetermined",
  "candidates": [
    {"name": "Event in time (gradual awakening)", "status": "live"},
    {"name": "Recognition of what was never absent (nondual)", "status": "live"}
  ],
  "cruxes": [
    "Can recognition be modeled as a Bayesian belief update?",
    "Does nondual phenomenology match 'never absent' or 'new event'?"
  ]
}
```

## Step 2: Truth Map → EO (Essay Object)

The research agent runs the 7-step dialectical procedure (from RESEARCH_DIRECTIVE):

1. **Pressure point:** Recognition is described as sudden by some traditions, gradual by others. Which is correct?
2. **Competing claims:** Pratyabhijñā says recognition is of what was never absent. Gradualist models say it's a cognitive development.
3. **Shared structure:** Both agree recognition involves a shift in self-understanding.
4. **Where it breaks:** Nondual traditions say nothing new is produced; cognitive models say new understanding IS produced.
5. **Best current answer:** Ñāṇavīra's structural analysis suggests recognition is not in time, but his account needs reconciliation with the phenomenology of sudden insight.
6. **Reverse critique:** What does Pratyabhijñā reveal about cognitive science? What does cognitive science reveal about Pratyabhijñā?
7. **Consequences:** Testable prediction — if recognition is not in time, neural correlates should show a phase shift, not learning curve.

This becomes an EO. We already have one for reflexivity. A new one would be written for recognition.

## Step 3: EO → Composition File

A human or agent writes the composition file. This is the critical creative step:

```json
{
  "composition_id": "comp:recognition-is-not-in-time",
  "title": "Recognition is Not an Event in Time",
  "duration_seconds": 480,
  "emotional_arc": {
    "rasa_progression": ["santa", "karuna", "raudra", "santa", "adbhuta", "santa"],
    "camatkara_moment": 0.72,
    "waypoints": [
      {"time": 0.0,  "label": "Stillness",   "v": [0.2,0.9,0.9,0.9,0.9,0.2], "rasa":"santa",   "tattva":36},
      {"time": 0.15, "label": "The problem",  "v": [0.4,0.7,0.7,0.6,0.5,0.5], "rasa":"karuna",  "tattva":28},
      {"time": 0.30, "label": "The search",   "v": [0.6,0.5,0.5,0.4,0.4,0.7], "rasa":"vira",    "tattva":20},
      {"time": 0.45, "label": "Frustration",  "v": [0.8,0.3,0.3,0.2,0.3,0.8], "rasa":"raudra",  "tattva":12},
      {"time": 0.60, "label": "Surrender",    "v": [0.3,0.7,0.8,0.8,0.7,0.3], "rasa":"santa",   "tattva":30},
      {"time": 0.72, "label": "RECOGNITION",  "v": [0.9,0.6,0.7,0.9,0.6,0.5], "rasa":"adbhuta", "tattva":1, "camatkara":true},
      {"time": 0.85, "label": "Integration",  "v": [0.7,0.7,0.7,0.8,0.7,0.4], "rasa":"vira",    "tattva":8},
      {"time": 1.0,  "label": "Return",       "v": [0.2,0.9,0.9,0.9,0.9,0.2], "rasa":"santa",   "tattva":36}
    ]
  }
}
```

**This composition file IS the film.** It's not a plan for the film. It contains everything needed to render.

## Step 4: Rasa Theory Drives the Aesthetic Experience

Each waypoint's rasa mode determines the *quality* of every channel:

### Śānta (Peace) — sections 0.0 and 0.6 and 1.0
| Channel | Effect |
|---------|--------|
| **Visual** | Minimal geometry. Pearl/white palette. Still or slow-drifting particles. Śiva tattva (36) = no density, pure light. Nāḍī network barely visible, a single central channel. |
| **Audio** | 60 BPM. C major. Open fifths. Strings/pad. Sparse. Long held notes. No percussion. |
| **Narrative** | Slow delivery. Long pauses. Simple language. The thesis stated clearly. |
| **Together** | The viewer rests. Space to think. The essay's question is posed in stillness. |

### Raudra (Fury) — section 0.45
| Channel | Effect |
|---------|--------|
| **Visual** | Complex jagged SDFs. Blood red / ash palette. Dense geometry, Earth tattva (12) = maximum texture. Nāḍī network tangled. Rapid pulse. |
| **Audio** | 140 BPM. C# minor. Diminished chords. Brass/percussion. Polyrhythms. High entropy. |
| **Narrative** | Fast delivery. Sharp emphasis. The contradiction stated forcefully. "But if consciousness is timeless, recognition CANNOT be in time." |
| **Together** | The viewer feels the tension of the paradox. The visuals, music, and argument all say "conflict" simultaneously. |

### Adbhuta (Wonder) + Camatkāra — section 0.72
| Channel | Effect |
|---------|--------|
| **Visual** | All geometry dissolves into pure light in 8 seconds. The nāḍī network collapses to a single point and expands as concentric waves. Śiva tattva (1) = undifferentiated camatkāra. |
| **Audio** | V7 → I authentic cadence over 8 seconds. Full orchestra swell. Pedal tone C. The harmonic tension built over the entire film resolves here. |
| **Narrative** | Silence for 4 seconds. Then one sentence: "Recognition is not the event. It is the seeing that there never was an event." Delivered slowly. |
| **Together** | The viewer doesn't just hear the conclusion. They EXPERIENCE it. The visual dissolve IS recognition. The cadence IS resolution. The sentence names what just happened. |

## Step 5: 6D Vector Renders Each Frame

For every frame, the 6D vector interpolated from waypoints feeds three parallel renderers:

### Visual Renderer (GLSL)
```
6D → Gielis supershape params → geometry shape
6D → Rasa mode → color palette + motion quality
6D → Tattva level → visual density (SDF complexity)
6D → Nāḍī mode (coral/maze/spots) → RD pattern
6D → Curl flow intensity → prana movement
6D → SignatureTiming -> scene arc (enter/disclose/transform/resolve)
```

### Audio Renderer (Tone.js + Tonal.js)
```
6D → Tymoczko M₁-M₈ → chord quality + voice leading + rhythm
6D → Rasa mode → tempo + instrumentation + timbre
6D → Camatkāra flag → cadence type + duration
6D → Tattva level → harmonic complexity
```

### Narrative Renderer (TTS)
```
6D → Rasa mode → delivery speed + emphasis + pauses
6D → Camatkāra flag → 4 seconds of silence before the key sentence
6D → Section label → which paragraph to read
```

## Step 6: Output

The render orchestrator runs:

```
render.py composition.json
  ├── render_frames()     → 11,520 PNGs at 24fps × 480s
  ├── render_audio()      → audio.wav with generated music
  ├── render_narration()  → narration.wav with TTS
  └── ffmpeg compose()    → final_mp4
```

The result is an 8-minute film where:
- The visual density follows the tattvic descent (clear → dense → dissolve)
- The music follows the rasa progression (peace → struggle → fury → surrender → wonder → peace)
- The narration pace follows the emotional tension
- The recognition moment is a single unified event: dissolve + cadence + silence + sentence

**The viewer doesn't need to know any of this.** They just experience a film that builds tension, peaks at a recognition moment, and resolves. The philosophy is encoded in the structure, not explained in the text. That's rasa theory in action — the emotion IS the aesthetic experience, not a description of it.
