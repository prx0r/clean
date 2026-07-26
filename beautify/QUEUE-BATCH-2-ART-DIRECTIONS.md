# Queue Batch 2 — Communication-First Art Directions

This batch contains 122 original fragment shaders across five essays. The source
PIL packs are treated as conceptual scores: they determine what each scene must
communicate, while the shaders invent the visual world, material, motion, and
emotional register.

## What the previous work taught us

The archive packs generally communicated well because individual scenes used
different diagrams, but their visual ambition was limited by literal
storyboarding. Queue Batch 1 moved much further toward authored GPU worlds, yet
the render review exposed a different failure mode:

- The dream, sacred-name, and sacred-mirror packs often placed a new glyph in
  the same sparse nocturnal field. They were coherent and elegant, but too many
  scenes read as stylistic variations rather than new ideas.
- The ritual-object pack achieved convincing material presence, but repeatedly
  relied on one central relic.
- The living-temple pack achieved the strongest depth and volumetric light, but
  its corridor camera and composition became overly stable across the essay.

The lesson is not to abandon continuity. It is to stop letting the continuity
object become a template prison.

## Communication standard

Every scene in this batch was judged against eight questions:

1. **Glance thesis** — can the viewer identify the scene's central relationship
   without narration?
2. **Visual verb** — does the frame visibly gather, split, exclude, remember,
   repair, navigate, or transform?
3. **Causal topology** — are sources, boundaries, channels, conflicts, and goals
   spatially unambiguous?
4. **Emotional register** — do color, density, rhythm, and scale support what the
   idea should feel like?
5. **Continuity without repetition** — does the pack remain one world while each
   scene earns a new composition?
6. **Mature frame** — does the image at `u ≈ 0.72` feel complete enough to hold
   as a cinematic still?
7. **Motion semantics** — does `u` reveal the argument and does `t` animate its
   forces, rather than merely fading or drifting decoration?
8. **Audio restraint** — do `u_audioVolume` and `u_audioBeat` intensify energy
   without substituting brightness for meaning?

## 1. Responsive icon-world

`an-image-becomes-imaginal-when-it-begins-to-answer-you`

An image becomes imaginal by becoming reciprocal. Enamel apertures, thresholds,
gazes, doubles, city-forms, and unresolvable remainders turn a framed picture
into an answering world. Daylight and night states prevent the doorway from
becoming a fixed template. The recurring aperture marks continuity; what appears
through and around it changes the meaning.

**18 visual functions**

## 2. Prismatic attentional aperture

`attention-creates-the-finite-self`

Attention is rendered as a force that edits reality. Salience condenses an open
field; beams privilege one region; identity becomes a tunnel; threat and desire
capture the geometry; notifications fracture it; meditation and rasa restore
width. Color is functional: cyan opens, red captures, gold integrates, and
violet marks the self/world interface.

**26 visual functions**

## 3. Luminous bioelectric tissue

`body-electrical-society`

The body appears as translucent tissue that negotiates. Membranes store voltage,
ion channels write state, gap junctions transmit consensus, and tissue-scale
fields become attractors and anatomical decisions. The pack deliberately avoids
using the neuron as a universal explanation: somatic cells, embryos, polarity,
normalization, and field-to-gene conversion carry the story.

**25 visual functions**

## 4. Porcelain morphogenetic landscape

`body-knows-the-shape`

Glazed living forms navigate an indigo liquid morphospace. Gold contours are
target states rather than decorative halos. Fragments regrow, voltage edits
redirect anatomy, two-headed outcomes preserve cryptic memory, and error paths
return collectives to stable form. The initial pale-field render was rejected;
the darker revision restored hierarchy and made goals, disruptions, and
reintegration legible.

**23 visual functions**

## 5. Kinetic multiscale navigation atlas

`cells-that-solve-problems`

Each cell is a compass moving through a space of possible states. Metabolism is
a cycle, transcription a braid, physiology a wave field, anatomy an assembly,
and behavior a fan of trajectories. Nested borders define the scale of the
self; a cyan compass and gold light cone show what an agent can sense and reach.
The later scenes contrast distributed control with micromanagement, local
defection with organism-level healing, and inherited bodily agency with brains
and humans.

**30 visual functions**

## Technique and review

The shared library follows LYGIA's granular philosophy—small reusable functions
for SDFs, noise, color, easing, and finishing—while every implementation and
composition in this batch is original. Technique review also used:

- [LYGIA](https://lygia.xyz)
- [The Book of Shaders](https://thebookofshaders.com), especially organic noise
  and cellular distance fields
- [Generative Design](https://www.generative-gestaltung.de/2/), especially
  agent motion and systems built from repeated rules

Every shader was compiled with `glslangValidator`. Every pack was rendered
through a headless software WebGL 2 pipeline at the required mature frame
(`u = 0.72`) and reviewed as a complete contact sheet. The final pack was also
rendered at low- and high-revelation states with different time and audio values
to verify that its transformations remain coherent across the animation.

## Review result

The batch is substantially better at balancing literal explanation and authored
art. Recurring visual languages make the essays emotionally continuous, but
the scenes use different visual verbs and causal layouts. Beauty is concentrated
where meaning changes: reciprocity, contraction, consensus, remembered target,
expanded boundary, and reachable future.
