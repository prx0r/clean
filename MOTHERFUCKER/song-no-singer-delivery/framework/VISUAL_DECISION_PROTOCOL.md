# Deterministic Visual Decision Protocol

This protocol turns an essay into a timed Skia companion whose moving relations correspond to the spoken argument. It is a decision procedure, not a mood-board exercise.

The system has four explicit passes:

1. argument analysis without visuals;
2. visual candidate generation;
3. scored selection and continuity integration;
4. semantic, temporal, and rendered-image audit.

Do not collapse the passes. Choosing an image while summarizing a paragraph makes the first association feel inevitable and produces literal, repetitive films.

## 1. Parse typed source units

Use `extractEssayUnits()` or `compile-essay`. A source unit is one blank-line-delimited block after headings and separators are removed.

- `prose`: spoken narration;
- `quotation`: spoken narration whose rhetorical status must be preserved;
- `list`: spoken narration that usually needs ordered, branching, or comparative geometry;
- `visual-only`: a fenced diagram that informs the image but is not spoken.

Never renumber units after analysis begins. Every unit must be covered exactly once and in order.

## 2. Build a visual-free argument IR

Validate the result against `essay-analysis.schema.json`.

For each beat, state:

- the exact source-unit range;
- the argumentative role;
- one claim that can be true or false;
- the relation being asserted;
- the source state;
- the target state;
- what remains invariant;
- why this beat follows the previous beat;
- the most likely visual misreading;
- forms of literal illustration to exclude.

If the beat cannot be described as a relation or state change, it is not ready for visualization.

### Beat boundaries

Start a new beat when any of these changes:

- argumentative role;
- relation type;
- agent or scale;
- temporal direction;
- claim polarity;
- metaphorical domain;
- continuity-object action;
- visual-only diagram structure.

Keep a beat together when the sentences are evidence for one relation and separating them would remove the causal proof.

Draft duration is:

`duration = ceil_to_frame((spoken_words × 60 / WPM) + tail_padding)`

Every shot must be 1–30 seconds. At 155 WPM with 0.45 seconds of tail padding, use at most 76 spoken words; 45–65 is the normal target. A visual-only unit contributes zero spoken words and must share a shot with spoken material unless `spokenOverride` is explicitly supplied.

## 3. Define continuity systems first

Choose two to nine recurring systems. Each must have:

- one stable semantic meaning;
- one stable base treatment;
- an introduction;
- at least one development, contrast, inversion, or return;
- a final resolution.

A continuity system is not a decorative logo. It is a conserved visual variable. If gold means relational invariance in one chapter, it cannot casually mean danger in another.

Use the smallest set that can carry the whole argument. A useful test is whether removing the system would make two non-adjacent chapters feel unrelated.

## 4. Generate three candidates per beat

Generate candidates only after the argument IR and continuity systems exist.

Each candidate must specify:

- one registered Skia mechanism;
- one visual operator;
- two or more concept-to-mark encodings;
- how time is used as proof;
- the continuity-system handoff;
- a predicted misreading;
- an anti-literal constraint.

Candidates must be structurally different. Changing only colors, labels, or node count does not create a new candidate.

## 5. Enforce relation compatibility

`src/visual-semantics.mjs` is the authority. A mechanism is eligible only if `mechanismRelations[visual]` contains the beat's `relationType`.

| Relation | Strong mechanisms | What motion must prove |
|---|---|---|
| identity across change | `pattern-ensemble`, `morphing-invariant`, `melody-time` | material changes while a relational invariant survives |
| dependency | `dependency-network`, `reciprocal-reeds`, `tuning-network` | influence travels without a privileged root |
| interface / selection | `boundary-gates`, `umwelt-windows`, `attention-beam` | some marks enter, others are excluded or de-emphasized |
| emergence / coordination | `multiscale-agent`, `relational-birth`, `tuning-network` | local rhythms become a larger organized response |
| translation | `memory-relay`, `source-compile-runtime` | the message changes form before a changed receiver uses it |
| feedback | `causal-vortex`, `powered-prison`, `desire-orbit` | the result returns and alters its own cause |
| recursion / inquiry | `recursive-observer`, `practice-folds`, `open-question` | the observing frame becomes part of its own field |
| cessation | `cooling-chain`, `opening-fist` | a branch loses fuel while the functional current continues |
| divergence / convergence | `dialectic-bridge`, `open-question` | shared ground remains while paths separate or meet only at a limited consequence |
| self-modification | `source-compile-runtime`, `powered-prison`, `causal-vortex` | one pass visibly changes the routing of the next |

If no registered mechanism fits, write a new mechanism and register its supported relations. Never force a convenient mechanism onto an incompatible claim.

## 6. Score candidates

Score every candidate from 0–100:

| Criterion | Weight | Test |
|---|---:|---|
| semantic topology | 25 | Does the geometry encode the same entities and relation as the claim? |
| motion proof | 15 | Does time demonstrate the claim rather than add ambient movement? |
| continuity handoff | 15 | Does the shot advance a declared continuity system? |
| misread resistance | 15 | Would a viewer infer the intended relation without the full caption? |
| caption independence | 10 | Could the main relation survive if title and subtitle vanished? |
| style fit | 10 | Does it preserve the manuscript border, palette, spacing, glow, and type hierarchy? |
| distinctness | 10 | Is it structurally distinct from neighboring shots while remaining part of the film? |

Reject any candidate below 80. Also reject regardless of score if:

- the mechanism–relation pair is unregistered;
- the visual operator cannot perform the argumentative role;
- the shot requires the full narration as on-screen text;
- motion can be removed without losing meaning;
- the candidate contradicts a continuity system;
- it literalizes a metaphor in a way the essay explicitly rejects.

Tie-break in this order: semantic topology, misread resistance, continuity handoff, lower complexity, then registry order. Record two to four rejected alternatives and why they lost.

## 7. Write and validate the v2 program

Validate against `essay-visual-program-v2.schema.json`, then run:

```bash
node src/cli.mjs audit-essay programs/example.json
node src/cli.mjs compile-essay programs/example.json --out build/example
```

Every shot must include:

- `claim`, `relationType`, `sourceState`, `targetState`, `preserves`;
- `semanticRole`, `visualOperator`;
- `visualEncoding`;
- `motionProof`, `misreadRisk`, `antiLiteral`;
- `continuityObject`, `continuityAction`;
- `candidateAudit`;
- the selected `visual` and parameters.

Paragraph ranges must cover every source unit exactly once with no gaps or overlap. Exact narration timing, if supplied, must contain every shot; draft and exact timing may not be mixed silently.

## 8. Run four audits

### Semantic

- Is every mechanism compatible with its relation?
- Does each source-to-target transformation match the claim?
- Does `preserves` identify the invariant rather than repeat the target?
- Is the visual useful rather than merely associated with the subject?

### Continuity

- Is every system introduced before use?
- Does each return change meaning or context?
- Is every system resolved?
- Do neighboring shots hand off at least one mark, direction, rhythm, or boundary?

### Diversity

- No four consecutive shots use the same mechanism.
- A chapter with four or more shots uses at least two mechanisms.
- Repetition is allowed only when repeated structure is the argument.
- Parameter changes must alter visible structure, not merely satisfy metadata.

### Caption independence

Render one representative frame from every shot with text hidden. A reviewer should be able to identify the relation class—loop, boundary, comparison, translation, emergence, or cessation—even if they cannot recite the prose.

## 9. Render audit

Before the full film:

1. render every registered mechanism once;
2. render the essay contact sheet;
3. inspect title and subtitle overflow;
4. inspect border continuity and safe areas;
5. inspect Devanāgarī shaping;
6. inspect three transition pairs from each major chapter;
7. render a low-resolution motion proof for complex loop, recursion, and cessation shots.

After the full render, validate codec, dimensions, frame rate, duration, frame count, non-empty frames, FFmpeg status, and storyboard/video agreement within one frame.

## Failure modes and repairs

| Failure | Cause | Repair |
|---|---|---|
| attractive but interchangeable shots | candidates came from topic nouns | rewrite every beat as source state → relation → target state |
| diagrams work only with captions | marks are labels, not encodings | map each concept to position, connection, direction, rhythm, shape, or opacity |
| film feels like unrelated cards | continuity was chosen per shot | declare conserved systems before candidate generation |
| abstract prose becomes circles everywhere | geometry was selected by style | select by registered relation compatibility |
| movement feels ambient | no motion proof | state what becomes impossible to prove in a still |
| disagreement is falsely resolved | synthesis bias | preserve shared ground and divergence in separate channels |
| cessation looks like destruction | target state is under-specified | keep the functional current moving while only ownership cools |
| memory looks like file retrieval | archive metaphor is literalized | visibly transform the trace before a changed receiver interprets it |

The process is complete only when the program, compiler, semantic auditor, contact sheet, and MP4 agree about what every shot is doing.
