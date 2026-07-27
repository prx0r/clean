# Audio and Narration Reactivity

## Does audio need to exist first?

There are three valid modes.

### Mode A — React to the final waveform

Use this when visuals must follow the actual performed music, voice, dynamics,
timbre and timing.

```text
render or obtain audio
→ analyze with librosa
→ create audio-feature manifest
→ render visuals using that manifest
→ mux original audio with video
```

This mode requires audio first.

### Mode B — React to score events

Use this when music is generated procedurally and its event data already exists.

```text
generate score events
→ generate score-feature bus
→ render visuals from score features
→ synthesize audio
→ mux
```

This mode does not require the final waveform first. It is cleaner for exact
motif entries, voice transfers and formal events.

### Mode C — Hybrid

Recommended for serious compositions.

```text
score events
    control formal visual events

final waveform features
    control performed pressure, timbre and transients
```

Example:

- score event: the passacaglia ground transfers to flute;
- waveform onset: a visible packet is emitted;
- harmonic energy: the packet trail becomes longer;
- spectral centroid: edges become finer;
- score tension: geometry becomes less stable.

## Narration is a separate signal

Narration should not be treated as another music track.

Use three kinds of narration data:

1. **Presence envelope**  
   Whether speech is active.

2. **Timing structure**  
   Sentence, clause and word boundaries.

3. **Semantic events**  
   Definitions, negations, questions, recognition sentences, quotations and
   epistemic cautions.

### Narration feature bus

```json
{
  "time": 42.5,
  "speechActive": 1,
  "speechDensity": 0.62,
  "sentenceProgress": 0.38,
  "wordOnset": 0,
  "semanticEvent": "definition",
  "emphasis": 0.74,
  "attentionRequest": 0.68
}
```

## Music versus narration routing

A robust pattern:

```text
music proposes
visual complicates
narration reorients
silence permits completion
```

Recommended responsibilities:

| Signal | Visual responsibility |
|---|---|
| Music onset | emission, impact, edge shock |
| Music harmonic energy | sustained field, glow, continuity |
| Music rhythm | packets, breathing, recurrence |
| Music formal event | topology change or carrier transfer |
| Narration presence | reduce visual information density |
| Narration emphasis | focus or selective highlighting |
| Narration question | open geometry or suspend closure |
| Narration negation | remove or invert a candidate |
| Recognition sentence | reveal the prepared invariant |
| Silence | permit visual completion; not automatic blackout |

## Attention arbitration

When narration is dense, visuals should usually clarify rather than compete.

```js
const visualDensity = narration.speechActive
  ? baseDensity * (1 - 0.55 * narration.attentionRequest)
  : baseDensity;

const particleEmission = narration.speechActive
  ? audioEmission * 0.45
  : audioEmission;
```

Do not simply lower all brightness during speech. Reduce new information,
particle count, camera motion or competing labels.

## Recommended routing split

```json
{
  "music": {
    "onset": "particles.emission",
    "harmonicEnergy": "channels.trailPersistence",
    "spectralCentroid": "materials.edgeFineness",
    "beatPulse": "chakra.contraction"
  },
  "narration": {
    "speechDensity": "scene.informationSuppression",
    "emphasis": "attention.focusStrength",
    "semanticEvent": "composition.semanticTrigger"
  }
}
```
