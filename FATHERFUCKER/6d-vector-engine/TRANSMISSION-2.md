# Transmission 2

The decisive answer is: **do not build a spring-driven semantic engine, and do not finite-difference inside GLSL.** Build a deterministic, seekable trajectory engine using shape-preserving cubic Hermite interpolation, compute derivatives analytically on the CPU, and derive music uniforms from a precomputed score-feature bus.

Also, an important disclosure: Forest did **not** implement `u_dState`, and its music uniforms were deterministic proxies—not extracted from the actual MIDI. Those were recommendations for the next engine.

## 1. `u_dState`: use PCHIP, not springs

The current Forest engine blends smoothstep, delayed disclosure, and anticipation curves. It exposes only state values. Because one scalar interpolation amount controls all six axes, its derivatives can be discontinuous between intervals and are not suitable as canonical semantic velocities.

Replace that with independent, shape-preserving cubic Hermite trajectories.

Given waypoint values (x_i), times (t_i), interval lengths (h_i=t_{i+1}-t_i), and secants:

```
\Delta_i=\frac{x_{i+1}-x_i}{h_i}
```

compute PCHIP/Fritsch–Carlson tangents. For an interior waypoint:

```python
if delta_prev * delta_next <= 0:
    tangent = 0.0  # genuine reversal or plateau
else:
    w1 = 2.0 * h_next + h_prev
    w2 = h_next + 2.0 * h_prev
    tangent = (w1 + w2) / (
        w1 / delta_prev + w2 / delta_next
    )
```

This gives:

* nonzero velocity through waypoints when an axis continues moving;
* zero velocity at genuine extrema;
* no overshoot outside `[0,1]`;
* deterministic random access at any timestamp;
* exact waypoint hits;
* analytic derivatives.

For normalized segment time (\tau=(t-t_i)/h_i):

```
x(\tau)=h_{00}x_i+h_{10}h_im_i+h_{01}x_{i+1}+h_{11}h_im_{i+1}
```

where:

```text
h00 =  2τ³ - 3τ² + 1
h10 =    τ³ - 2τ² + τ
h01 = -2τ³ + 3τ²
h11 =    τ³ -   τ²
```

Calculate `dx/dt` analytically in the engine. Do not calculate it from adjacent rendered frames.

### Normalization

Raw state velocity in units/second will be small. Define:

```json
"trajectory": {
  "interpolation": "pchip",
  "derivative_order": 1,
  "rate_scale_seconds": 52.0
}
```

Default `rate_scale_seconds` to the median semantic-interval duration.

Then:

```python
d_state_normalized = dx_dt * rate_scale_seconds
```

This means "an axis changing by one complete unit over a typical interval" produces a velocity near `1.0`.

Do not clamp it in the engine. Let validators warn above a chosen bound such as `abs(v) > 3`, and let shaders apply `tanh`, `clamp`, or asymmetric response as artistically required.

### Do we need acceleration?

Not in the standard contract yet.

PCHIP is (C^1): velocity is continuous, but acceleration can change abruptly at waypoints. That is acceptable for semantic direction. If a composition genuinely needs acceleration as meaning, add a C² quintic trajectory with authored velocity/acceleration hints.

Therefore:

```text
Canonical engine: position + velocity
Optional composition extension: acceleration
No universal spring/damper
```

A spring may drive a local visual secondary response—leaf recoil, membrane wobble, camera inertia—but never canonical semantic state. For such secondary motion, `ζ = 0.85` is a reasonable default, with settling time authored per material.

### Why not springs for the master state?

A spring system:

* is history-dependent;
* complicates rendering frames out of order;
* may miss exact waypoint values;
* may leak through formal silence or recognition boundaries;
* turns semantic authoring into parameter tuning.

The master composition must be seekable and exact.

## 2. Formal tournament: typed structural homology

This can be partially formalized but not fully automated. Use automation to reject weak forms and rank candidates; use rendered/audible prototypes for the final decision.

Represent the argument and candidate musical form as typed operator graphs.

Example argument operators for Forest:

```text
independent entry
response changes prior agent
identity survives transformation
simultaneous independent action
different temporal scales
conflict through overlap
exchange of functional roles
coordination without central executive
```

A fugue natively supports nearly all of these. A rondo strongly supports return and contrasting episodes, but weakly supports simultaneous independent agents, role exchange, and decentralized coordination.

Use this score:

```text
H =
  0.25 * operator_coverage
+ 0.20 * relation_preservation
+ 0.15 * temporal_order_preservation
+ 0.15 * identity_under_transformation
+ 0.15 * perceptual_legibility
+ 0.10 * medium_native_necessity
- penalties
```

Each component is `0–1`.

Definitions:

* **Operator coverage:** How many important argumentative operations have native formal equivalents?
* **Relation preservation:** Does the form preserve who affects whom?
* **Temporal order:** Does the formal sequence reproduce the argument's dependencies?
* **Identity under transformation:** Can the central identity survive the required changes?
* **Perceptual legibility:** Can an audience hear/see the correspondence without explanation?
* **Medium-native necessity:** Does this form do something narration alone cannot?

Penalties:

```text
-0.10 arbitrary symbolic mapping
-0.10 requires narration to explain the formal correspondence
-0.10 repeats the previous composition's form without necessity
-0.10 cannot represent the argument's central contradiction
```

Require written evidence for every score. No unexplained numbers.

Then prototype the two highest candidates as 30–60 second score/visual sketches. The rubric proposes; perception disposes.

So the answer is:

```text
~75% formalizable structural screening
~25% artistic/perceptual judgment after prototyping
```

Do not ask Gemma to choose entirely through intuition, but do not pretend graph matching can determine aesthetic truth.

## 3. Attention budget: soft competitive capacity

Do not impose strict conservation. Sometimes music, image, and narration should all become intense together. But that must be a deliberately bounded overload window.

Separate:

* **presence:** whether a medium remains perceptually available;
* **information density:** how much new structure demands attention.

Silence can have high presence and low density.

Each semantic interval should declare:

```json
"attention": {
  "lead": "music",
  "requests": {
    "music": 0.90,
    "visual": 0.72,
    "narration": 0.38
  },
  "floors": {
    "music": 0.40,
    "visual": 0.12,
    "narration": 0.05
  },
  "capacity": 1.65,
  "overload_capacity": 2.30,
  "overload_window": [0.61, 0.66],
  "allow_void": false
}
```

Allocation algorithm:

```python
requests = clamp01(requests)
floors = minimum(requests, floors)
excess = maximum(requests - floors, 0.0)
room = capacity - sum(floors)

if sum(excess) <= room:
    allocation = requests
else:
    weighted = excess * priorities
    allocation = floors + room * weighted / sum(weighted)
```

If clamping any allocation to its request creates unused room, redistribute it iteratively among the remaining modalities.

Recommended priorities:

```text
lead modality:    1.6
support modality: 1.0
ground modality:  0.7
```

This makes a dense score suppress narration when music is marked as lead, without forcing narration completely off.

### Preventing accidental collapse

Require:

```python
if not allow_void:
    assert max(allocation) >= 0.25
```

The continuity field should usually retain a separate presence floor even when its information density approaches zero.

Both music and narration may intentionally become zero, provided image/presence carries the event. Recognition silence is an example—not an error.

### Converting narration allocation into words

Do not gate finished narration dynamically. Use the attention allocation while writing and timing it:

```python
maximum_words_per_second = 2.4  # 144 wpm
word_budget = (
    interval_duration
    * maximum_words_per_second
    * mean(narration_allocation)
)
```

Add an authored `conceptual_necessity` value if a difficult distinction truly requires language:

```python
narration_request = conceptual_necessity * (
    0.20 + 0.80 * available_attention_headroom
)
```

The 20% floor preserves indispensable explanation. If `conceptual_necessity=0`, narration may disappear completely.

## 4. What Forest actually did with music uniforms

Forest did not parse `score.mid` during visual rendering.

Its engine generated symbolic proxies from:

* beat position;
* the six-dimensional state;
* stage tempo;
* periodic pulses.

It exposed:

```python
music_a = (bass, inner, upper, continuo)
music_b = (tension, subject)
```

These were not one value per instrument.

Broadly:

```text
bass:
one pulse per beat

inner:
one-to-two subdivisions, shifted by reciprocity

upper:
one-to-four subdivisions, controlled by fecundity/localization

continuo:
two-to-four subdivisions

subject:
recognition × bar-shaped envelope

tension:
appetite + localization
- reciprocity - radiance
+ chromatic periodicity
```

This synchronized the shader with the composition's intended musical behavior, but not with each actual MIDI note. It was a deliberate proxy and is now the largest engine-level limitation.

## 5. Next-generation MIDI→GLSL coupling

Do not make the renderer parse MIDI for every frame. The score generator already knows every note and subject entry before serialization.

Have it emit:

```text
score.mid
score_manifest.json
score_events.json
score_features.npz
```

Sample the feature bus at 60 Hz.

### Per-voice energy

Support up to eight semantic voices.

For each note event:

```python
contribution = (
    (velocity / 127.0) ** 1.5
    * symbolic_envelope(note, t)
)
```

For track `j`:

```python
energy_sum = sum(contribution for active notes on track_j)
voice_energy[j] = 1.0 - exp(-energy_sum / compression_j)
```

Pass continuous salience, not a binary active mask.

### Subject presence

The composer must annotate subject/motif entries in the score event graph:

```json
{
  "start": 472.31,
  "end": 477.31,
  "voice": 0,
  "transform": "original",
  "confidence": 1.0
}
```

For each entry use a short raised-cosine or smoothstep entrance and exit:

```python
entry_presence = (
    smoothstep(start, start + attack, t)
    * (1.0 - smoothstep(end - release, end, t))
)
```

Then:

```python
subject_presence = 1.0 - exp(
    -sum(entry.confidence * entry_presence)
)
```

Also calculate:

```python
active_subject_entries = count(entries active at t)

subject_overlap = clamp01(
    (active_subject_entries - 1)
    / max(1, expected_maximum_overlap - 1)
)
```

`u_subjectPresence` answers "how perceptually available is the identity?"

`u_subjectOverlap` answers "how much is the identity interacting with itself?"—important for stretto, canon, multiplicity, and conflict.

### Musical tension

Use a hybrid rather than pretending tension is purely extractable:

```python
music_tension = (
    0.50 * authored_formal_tension
    + 0.30 * active_pitch_dissonance
    + 0.20 * normalized_onset_density
)
```

The score author knows whether a suspension is unresolved, whether a chromatic note is structural, and whether apparent dissonance is actually stable. Pure interval counting cannot know that.

### Audio volume and beat

For draft rendering, derive them symbolically.

For final rendering:

1. generate score events;
2. synthesize/render audio;
3. analyze actual PCM at 60 Hz;
4. write RMS/onset features into the feature bus;
5. enforce silence windows after analysis;
6. render GLSL using that cache.

This gives true audio coupling without losing deterministic timing.

## 6. Standard uniform contract

Yes, standardize the core contract. Do not make every composition reinvent it.

Use:

```glsl
uniform vec2  iResolution;

uniform float u;                  // global normalized progress
uniform float t;                  // seconds
uniform float u_stage;
uniform float u_local;
uniform float u_tattva;

uniform vec4  u_stateA;           // axes 0–3
uniform vec2  u_stateB;           // axes 4–5

uniform vec4  u_dStateA;          // normalized velocity axes 0–3
uniform vec2  u_dStateB;          // normalized velocity axes 4–5

uniform vec4  u_musicVoicesA;     // semantic voices 0–3
uniform vec4  u_musicVoicesB;     // semantic voices 4–7
uniform float u_musicVoiceCount;

uniform float u_musicTension;
uniform float u_subjectPresence;
uniform float u_subjectOverlap;

uniform float u_audioVolume;
uniform float u_audioBeat;
```

Do **not** call the last velocity vector `u_ddB`. Conventionally `dd` means acceleration.

If acceleration is enabled:

```glsl
uniform vec4 u_ddStateA;
uniform vec2 u_ddStateB;
```

Unused voices must be zero. `u_musicVoiceCount` tells the shader how many values are semantically valid.

Every `composition.json` should still enumerate the uniforms under `visual_contract.uniforms`, and add semantic mappings:

```json
"music_voice_mapping": [
  "ground",
  "inner_relation",
  "primary_identity",
  "mobile_answer",
  "illumination",
  "continuo"
]
```

Composition-specific additions remain allowed, but the core contract stays stable.

## Gemma implementation decision

Build this:

```text
Canonical state:
PCHIP position + analytic velocity

Canonical music coupling:
precomputed 60 Hz score feature bus

Attention:
offline soft competitive allocation with lead floors

Formal tournament:
typed-graph rubric followed by prototypes

Acceleration:
optional, not standard

Springs:
local visual secondary motion only

Shader finite differences:
never
```

Acceptance tests should require:

* every trajectory hits every waypoint exactly;
* no axis overshoots `[0,1]`;
* velocity is continuous at ordinary waypoints;
* velocity is zero at authored extrema;
* random-access and sequential rendering return identical states;
* `u_dState` sign correctly distinguishes rising and falling axes;
* all score features are exactly zero during formal silence;
* every annotated subject entry raises `u_subjectPresence`;
* simultaneous entries raise `u_subjectOverlap`;
* unused music voices remain zero;
* regeneration produces byte-identical feature data.

That closes the engine without turning semantic motion into an uncontrolled physical simulation.
