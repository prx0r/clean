# Framework Review

## Confirmed strengths

- The renderer already loads a precomputed audio manifest and samples it by
  global frame time.
- `argument-diagram` is correctly treated as a clean motif without decorative
  borders or footers.
- Source Serif 4 is the right primary face for mixed English and Sanskrit IAST.
- The ten logical move families are sufficient to construct a complete argument
  rather than a slideshow.
- The subclaim default position has been repaired to avoid the former claim
  overlap.

## Changes supplied here

### Authored move timing

The original motif divides every scene evenly across its moves. The replacement
supports normalized `start` and `end` windows and `persist: true`.

### Persistent argument state

Concept maps, branches and comparisons can remain visible while later claims
arrive. This permits cumulative reasoning.

### Better typography

The replacement measures styled runs, wraps text to a maximum width, preserves
Source Serif for Sanskrit diacritics and reserves KaTeX Math for italic
mathematical variables.

### Audio response

Narration RMS and onset only affect subtle field pressure, ring expansion and
micro-emphasis. Audio never changes the logical topology or overwhelms text.

### Semantic motion

Claims arrive, objections are struck through, branches remain simultaneously
available, premises accumulate, and conclusions emerge only after their
supporting structure.

## Important remaining limitation

Librosa analyzes acoustic performance, not sentence meaning. The current film
uses authored move windows for semantic timing and audio features only for
subtle performance synchronization. Word-level forced alignment would be the
next upgrade, not a requirement for this release.
