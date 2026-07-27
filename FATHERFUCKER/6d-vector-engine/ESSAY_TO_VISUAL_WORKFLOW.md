# Essay to Skia Visual Companion

This workflow turns an essay into a coherent narration-locked film. It is not a keyword-to-icon system. Its job is to identify the essay’s changing relations—contraction, exclusion, sequence, causality, reversal, recognition—and express those relations through a small visual world that evolves with the argument.

The machine-readable contract is `essay-visual-program.schema.json`. The complete worked example is `programs/infinite-learned-visual-program.json`.

## Required outputs

Given one immutable essay, the visual-planning model must produce:

1. one visual thesis;
2. three to six continuity systems;
3. an ordered shot list covering every narration paragraph exactly once;
4. one semantic role, visual operator, visual mechanism, continuity object, and rationale per shot;
5. restrained titles and Sanskrit terms for the existing footer;
6. draft timing or exact narration timing.

The compiler converts that plan into a normal Skia pack, narration script, and exact storyboard. The renderer remains responsible for visual style, typography, border, texture, frame generation, encoding, and validation.

## The governing distinction: illustrate relations, not nouns

Weak visual planning asks, “What picture represents consciousness?” and reaches for an eye, galaxy, brain, or stock mystical symbol.

Strong visual planning asks:

- What changes in this sentence?
- What is being restricted, connected, divided, reversed, or disclosed?
- Which object from the previous beat can undergo that change?
- What must remain visible for the argument to be understood?

For example:

- “Infinity contracts into a viewpoint” is a field-to-frame transformation.
- “Limited knowing creates foreground” is a selection relation.
- “Time makes melody possible” is a sequence mechanism.
- “The boundary remains real but is not final” is a recontextualization, not a deletion.

The visual should demonstrate the proposition even with the footer hidden.

## Stage 1 — Preserve the source

- Never rewrite the essay during visual planning.
- Split it into narration paragraphs after removing Markdown headings and separators.
- Number those paragraphs from 1.
- Every shot receives an inclusive `paragraphs: [first, last]` range.
- Ranges must be contiguous, ordered, nonoverlapping, and cover the complete essay.

The compiler enforces this. Missing prose and duplicated prose are fatal errors.

## Stage 2 — Build the argument map

Read the full essay before assigning visuals. Mark each passage with its argumentative job:

| Semantic role | Function |
| --- | --- |
| `hook` | Creates the initiating tension or image |
| `question` | States the explanatory problem |
| `thesis` | Gives the essay’s central claim |
| `definition` | Introduces a technical distinction |
| `mechanism` | Explains how a process works |
| `analogy` | Transfers a precise relation into a graspable domain |
| `consequence` | Shows what follows from a claim |
| `objection` | Presents the ordinary or rival interpretation |
| `reversal` | Reinterprets an existing fact without denying it |
| `practice` | Converts theory into an ordered operation |
| `recognition` | Changes the containing frame of the argument |
| `synthesis` | Holds earlier elements in one system |
| `coda` | Returns to the opening object with transformed meaning |

Do not make shot boundaries by sentence count alone. A beat ends when its argumentative operation changes.

## Stage 3 — Write one visual thesis

The visual thesis is a single causal sentence explaining how the entire film will behave. It must identify:

- the primary field or substance;
- the structures that transform it;
- the objects that recur;
- what changes at the essay’s main reversal;
- what must remain after the reversal.

Example:

> One luminous field repeatedly localizes into a point, frame, lens, sequence, lack, and causal wall; recognition reopens those structures without erasing their finite form.

If the thesis only lists a palette or aesthetic, it is not a visual thesis.

## Stage 4 — Choose continuity systems

Continuity objects make the film feel like one argument rather than a slideshow. Choose three to six and assign each a stable meaning.

The example film uses:

| Object | Stable meaning |
| --- | --- |
| Gold-white field | Universal awareness or common substance |
| Crimson frame | Active limitation and boundary |
| Indigo local form | Individual perspective |
| Gold current | Continuity between universal and local power |
| Five arcs | Contraction as a reversible gesture |

Rules:

- Reuse the same object when an idea is reconsidered.
- Change the object’s relation, motion, scale, or containment before changing its identity.
- At a reversal, preserve the supposedly negative object and reveal a larger context around it.
- Introduce a new continuity object only when the argument introduces a genuinely new mechanism.

## Stage 5 — Select the visual operator

The operator describes what the animation must do:

| Operator | Use when the passage… |
| --- | --- |
| `reveal` | discloses something already present |
| `contract` | localizes a field or capacity |
| `frame` | creates inside/outside or here/there |
| `filter` | restricts a common source into a specific capacity |
| `sequence` | distributes simultaneity into time |
| `select` | creates foreground through attention |
| `reach` | turns lack into directed movement |
| `enclose` | stabilizes local identity |
| `construct` | actively produces a boundary or causal structure |
| `unfold` | retraces nested layers |
| `invert` | reverses container and contained |
| `differentiate` | produces many textures from one field |
| `recontextualize` | keeps a fact but changes what contains or explains it |
| `open` | relaxes a closure without destroying its parts |

The operator is more important than the depicted object. It controls motion logic.

## Stage 6 — Select a semantic visual mechanism

The framework supplies fifteen controlled mechanisms:

| Mechanism | Best for |
| --- | --- |
| `constraint-field` | field-to-point contraction; localization without loss |
| `point-of-view` | here/there, subject/object, frame, excluded horizon |
| `five-lenses` | a common source restricted through several capacities |
| `local-power` | universal capacity expressed as one finite action |
| `melody-time` | sequence, memory, anticipation, temporal articulation |
| `attention-beam` | foreground/background, selection, limited knowing |
| `desire-orbit` | felt lack, attraction, reaching, repeated possession |
| `smallness-cage` | “only this,” exclusive identity, local enclosure |
| `powered-prison` | limitation actively constructed and maintained |
| `practice-folds` | body, breath, mantra, and attention as nested operations |
| `upsurge` | center-to-field inversion and sudden recognition |
| `wave-ocean` | finite form continuous with common substance |
| `textures-display` | one field differentiated into many qualities |
| `limitation-reversal` | conditions retained but released from identity |
| `opening-fist` | contraction understood as a loosening gesture |

Use the mechanism whose geometry proves the passage’s relation. Do not select by superficial keyword.

## Stage 7 — Write the visual rationale

Every shot must contain `visualRationale`. This is an audit trail, not on-screen copy.

A valid rationale states:

1. what relation the spoken passage asserts;
2. what visual transformation expresses it;
3. which continuity object is preserved or changed;
4. why this mechanism is better than a literal illustration.

Weak:

> Use a beautiful glowing animation about consciousness.

Strong:

> Concentric structures compress while retaining the same core and colors, showing localization without loss of substance.

If the rationale cannot explain the motion, the shot is not ready.

## Stage 8 — Control timing

Draft planning:

- target roughly 5–24 seconds per shot;
- keep one argumentative operation per shot;
- use `wordsPerMinute` and `tailPadding`;
- the compiler rounds every duration to a whole video frame;
- split any beat exceeding 30 seconds.

Publication:

1. finalize the exact narration text;
2. record or synthesize the final narration;
3. force-align it into the same shot IDs;
4. produce a timing manifest:

```json
{
  "shots": [
    { "id": "inf-001", "duration": 6.125 },
    { "id": "inf-002", "duration": 8.75 }
  ]
}
```

5. include one exact duration for every storyboard shot;
6. rerun `render-essay --timings exact-timings.json`.

Audio owns the duration. Visuals conform to it. Never stretch a completed movie afterward to chase alignment.

## Stage 9 — Use typography sparingly

The footer is the only persistent text area:

- title: the conceptual beat;
- subtitle: one precise interpretive sentence;
- term: IAST or concise technical term;
- Devanāgarī: the correct Sanskrit script.

Do not render narration captions inside the composition. Internal labels are allowed only when the relation would otherwise be ambiguous—for example `here / there`, `memory / now / anticipation`, or the five kañcuka names.

## Stage 10 — Preserve the established style

The renderer owns:

- ivory manuscript field;
- stable paper texture;
- double border and corner rosettes;
- crimson for decisive boundary or transformation;
- indigo for local structure;
- gold for luminosity and continuity;
- EB Garamond and Noto Serif Devanagari;
- restrained glow and line weight;
- deterministic movement.

The planning model should not invent CSS, fonts, camera filters, backgrounds, or new rendering backends.

## Stage 11 — Quality audit

Reject the program if any answer is “no”:

### Source integrity

- Does the timeline cover every essay paragraph exactly once?
- Is the narration wording unchanged?
- Are quotation and Sanskrit passages preserved?

### Semantic fidelity

- Can each visual be explained as a relation or mechanism?
- Does each analogy preserve the essay’s actual logic?
- Are objections and conclusions visually distinguished?

### Continuity

- Do at least three objects recur across chapters?
- Does the main reversal transform an established object?
- Does the ending return to the opening motif with changed meaning?

### Motion

- Is the main concept expressed by transformation rather than a static label?
- Does movement have one interpretable direction?
- Are textures stable rather than randomly shimmering?

### Restraint

- Are there no full narration captions?
- Is each frame legible at thumbnail scale?
- Are color and glow semantically consistent?

### Technical validity

- Does `compile-essay` pass?
- Does the contact sheet show a coherent visual family?
- Does the rendered MP4 pass codec, dimensions, fps, frame-count, and duration checks?

## Commands

```bash
npm install

# Compile reasoning into storyboard and Skia pack
node src/cli.mjs compile-essay programs/infinite-learned-visual-program.json

# Render draft-timed film
node src/cli.mjs render-essay programs/infinite-learned-visual-program.json

# Render narration-locked film
node src/cli.mjs render-essay programs/infinite-learned-visual-program.json \
  --timings exact-timings.json
```

Generated files live in `build/<film-id>/`.
