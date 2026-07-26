# Film Review Rubric

## Hard gates

A pack is rejected if any condition is true:

- a source visual function has no shader;
- a shader lacks `u`, `t`, `u_audioVolume`, or `u_audioBeat`;
- audit or compilation fails;
- `u` is only opacity;
- audio is only final brightness;
- more than one third of scenes share one composition family;
- the mature contact sheet contains clipping that erases structure;
- the final scene does not visibly integrate an earlier conflict;
- a caution scene uses exactly the same triumphant grammar as a conclusion.

## Weighted score

Score every scene from 0–5, then convert to the weights below.

| Criterion | Weight |
|---|---:|
| Concept and glance-thesis fit | 25 |
| Visible transformation | 20 |
| Causal topology | 15 |
| Emotional register | 10 |
| Continuity with variation | 10 |
| Composition and technique novelty | 10 |
| Mature-frame quality | 5 |
| Audio semantics | 5 |

Reject a scene below 75/100. Reject a pack below 82/100 mean.

## Three-state render review

| State | Suggested uniforms | Question |
|---|---|---|
| Latent | `u=.18`, low volume, no beat | Is the initial condition readable and alive? |
| Mature | `u=.72`, medium volume, light beat | Is the thesis clear and the frame film-quality? |
| Resolved | `u=.94`, changed `t`, high volume, beat | Does the result preserve history without clipping? |

## Contact-sheet tests

Review the whole pack before isolated frames:

- silhouettes and dominant axes vary;
- wide, medium, macro, split, and field views are represented;
- luminance has an intentional rhythm;
- no more than three adjacent modes use the same dominant hue;
- visual density follows the essay rather than monotonically increasing;
- comparison and caution scenes remain legible at thumbnail size.

## Evidence record

Each `REVIEW.md` records:

- source function count and shader count;
- spec validator result;
- audit and compiler result;
- render dimensions and uniform states;
- contact-sheet findings;
- revisions made after review;
- remaining intentional risks.
