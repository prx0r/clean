# Unified Composition Format — The Single Source of Truth

## The Core Object

```json
{
  "composition_id": "comp:recognition-is-not-in-time",
  "title": "Recognition is Not an Event in Time",
  "duration_seconds": 480,
  "fps": 24,
  
  "emotional_arc": {
    "type": "hero_journey",
    "rasa_progression": ["santa", "adbhuta", "raudra", "karuna", "adbhuta", "santa"],
    "waypoints": [
      {
        "time": 0.0,
        "label": "The question",
        "valence": 0.3,
        "arousal": 0.2,
        "tension": 0.1,
        "transcendence": 0.4,
        "control": 0.5,
        "rasa": "santa",
        "tattva_level": 36,
        "description": "Stillness before inquiry. Śiva tattva — pure potential."
      },
      {
        "time": 0.15,
        "label": "The confusion",
        "valence": -0.2,
        "arousal": 0.4,
        "tension": 0.3,
        "transcendence": 0.2,
        "control": 0.3,
        "rasa": "karuna",
        "tattva_level": 25,
        "description": "The problem appears. Puruṣa tattva — the individual soul facing limitation."
      },
      {
        "time": 0.35,
        "label": "The struggle",
        "valence": -0.5,
        "arousal": 0.7,
        "tension": 0.7,
        "transcendence": 0.1,
        "control": 0.2,
        "rasa": "raudra",
        "tattva_level": 15,
        "description": "Dualistic tension. The nadis are tangled, ida and pingala in conflict."
      },
      {
        "time": 0.55,
        "label": "The still point",
        "valence": 0.1,
        "arousal": 0.1,
        "tension": 0.8,
        "transcendence": 0.6,
        "control": 0.4,
        "rasa": "santa",
        "tattva_level": 30,
        "description": "Maximum tension, but held. The eye of the storm."
      },
      {
        "time": 0.70,
        "label": "THE RECOGNITION",
        "valence": 0.9,
        "arousal": 0.6,
        "tension": 0.1,
        "transcendence": 0.9,
        "control": 0.9,
        "rasa": "adbhuta",
        "tattva_level": 2,
        "camatkara": true,
        "description": "The apex. Consciousness recognizes itself. Camatkāra dissolve."
      },
      {
        "time": 0.85,
        "label": "The consequence",
        "valence": 0.7,
        "arousal": 0.3,
        "tension": 0.2,
        "transcendence": 0.7,
        "control": 0.7,
        "rasa": "vira",
        "tattva_level": 10,
        "description": "What follows from recognition. Integration into daily life."
      },
      {
        "time": 1.0,
        "label": "The return",
        "valence": 0.8,
        "arousal": 0.2,
        "tension": 0.0,
        "transcendence": 0.8,
        "control": 0.8,
        "rasa": "santa",
        "tattva_level": 36,
        "description": "Return to stillness, but transformed. Śiva tattva now includes all."
      }
    ],
    "interpolation": "cubic_spline",
    "camatkara_moment": {"time": 0.70, "duration": 8.0}
  },

  "visual": {
    "signature_style": "night_field",
    "primary_rasa_palette": "adbhuta",
    "nadi": {
      "mode": "coral",
      "feed_rate": 0.0545,
      "kill_rate": 0.062,
      "seed_positions": "chakra",
      "flow_field_strength": 0.3,
      "pulse_frequency": {"min": 0.5, "max": 2.0}
    },
    "chakras": {
      "render": true,
      "style": "vortex",
      "intensity_follows_emotional_arc": true
    },
    "camatkara": {
      "type": "dissolve_to_light",
      "duration_seconds": 8.0,
      "color": [1.0, 0.95, 0.9]
    },
    "tattva_mapping": {
      "mode": "descending_ascending",
      "lowest_point": 15,
      "highest_point": 2
    }
  },

  "audio": {
    "tempo": {"base": 80, "follows_arousal": true, "range": [50, 140]},
    "key": "C",
    "scale": "major",
    "harmonic_complexity": {"follows_tension": true, "range": [3, 8]},
    "instrumentation": {
      "primary": "strings",
      "secondary": "piano",
      "climax": "full_orchestra",
      "follows_emotional_intensity": true
    },
    "voice_leading": {"smoothness_follows_control": true},
    "camatkara": {
      "cadence": "authentic",
      "pedal_tone": "C",
      "duration_seconds": 8.0
    }
  },

  "narrative": {
    "type": "essay",
    "sections": [
      {"time": 0.0, "title": "The Question", "thesis": "Recognition is not an event in time..."},
      {"time": 0.15, "title": "The Problem", "thesis": "We think of awakening as something that happens..."},
      {"time": 0.35, "title": "The Contradiction", "thesis": "But if consciousness is timeless, recognition cannot be in time..."},
      {"time": 0.55, "title": "The Still Point", "thesis": "Consider Nanavira's fundamental structure..."},
      {"time": 0.70, "title": "Recognition", "thesis": "Recognition is not the event. It is the seeing that there never was an event."},
      {"time": 0.85, "title": "What Follows", "thesis": "If recognition is not in time, then what changes?"},
      {"time": 1.0, "title": "The Return", "thesis": "Nothing changes. Everything changes."}
    ],
    "style": "poetic_philosophical",
    "voice": "atenborough"
  },

  "rendering": {
    "glsl_shader": "signature.glsl",
    "glsl_includes": ["primitives", "cinema", "signature", "include/temporal_exposure"],
    "audio_backend": "tonejs",
    "video_output": {"codec": "h264", "resolution": "1920x1080", "fps": 24},
    "renderer": "beautify-archive/lib/render_harness.py"
  }
}
```

---

## How It Renders

Each renderer reads only what it needs from the composition object:

### GLSL Renderer reads:
```json
{ "emotional_arc": {...}, "visual": {...}, "rendering": {...} }
```
→ Generates 60fps real-time shader with:
- Spanda pulse from `arousal × tempo_range`
- Nāḍī network from `visual.nadi.feed_rate`
- Rasa palette from `primary_rasa_palette`
- Tattvic density from `tattva_level`
- Camatkāra dissolve at `emotional_arc.waypoints[4]`
- Timing from `SignatureTiming(enter, disclose, transform, resolve)`

### Audio Renderer reads:
```json
{ "emotional_arc": {...}, "audio": {...} }
```
→ Generates real-time music with:
- Tempo from `emotional_arc[time].arousal × audio.tempo.range`
- Harmony from `M₂(rasa_mode, tattva_level)` via Tymoczko mapping
- Voice leading from `control` value
- Rhythmic pattern from `tension` value via Euclidean rhythm
- Cadence at `camatkara_moment` via V7 → I resolution
- Timbre from rasa mode (śānta=strings, raudra=brass, etc.)

### Narrative Renderer reads:
```json
{ "narrative": {...}, "emotional_arc": {...} }
```
→ Generates timing-track for TTS/narration with:
- Section titles and thesis statements
- Pacing from emotional arc (slow during śānta, fast during raudra)
- Emphasis at camatkāra moment (pause before, slower delivery)

### Unified Orchestrator reads:
```json
{ "composition_id", "title", "duration_seconds", "fps" }
```
→ Ensures all three renderers start at the same frame and use the same clock.

---

## The Rasa → 6D → Render Pipeline

```
COMPOSITION OBJECT
  │
  ├── emotional_arc[time]
  │     └── [valence, arousal, tension, transcendence, control] → 5D emotion
  │           └── nearest rasa archetype
  │                 ├── visual: rasa colors + motion quality + nāḍī mode
  │                 ├── audio: chord quality + tempo + instrumentation
  │                 └── narrative: pacing + emphasis + silence
  │
  ├── camatkara_moment
  │     ├── visual: SDF dissolve → pure light (8 seconds)
  │     ├── audio: V7 → I authentic cadence (8 seconds)
  │     └── narrative: silence, then the one sentence that matters
  │
  └── tattva_level
        ├── 36 (Śiva): no geometry, undifferentiated light
        ├── 25 (Puruṣa): central point, perspective
        ├── 15 (Mahābhūtas): dense, textured, bounded
        └── 1-5 (Earth): complex geometry, maximum detail
```

---

## What This Enables

| Feature | How |
|---------|-----|
| Synchronized AV | Same emotional arc drives GLSL + audio + narrative timing |
| Deterministic render | Same composition file → same output every time |
| Infinite variation | Change emotional_arc slightly → entirely new film |
| Rasa-driven everything | Śānta section = slow, consonant, minimal, still |
| Camatkāra at will | Flag any moment as the climax — all three media respond |
| Tattvic depth perception | Viewer can "feel" the ontological depth of each section |
| Nāḍī network growth | Network complexity follows emotional intensity |
| One file, three outputs | Write once, render as video, interactive web, or live performance |
