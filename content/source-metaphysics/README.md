# Source Metaphysics — Truth Map

This directory tracks every question the research programme is investigating.

Each file is a JSON object representing a single question with:
- Current status (strongly_supported → plausible → underdetermined → speculative → incompatible)
- Confidence score (0-1)
- Evidence for and against (linked to specific ROs, essays, videos)
- Best provisional answer
- Parent/child question relationships

## Status Values

| Status | Meaning |
|--------|---------|
| `strongly_supported` | Multiple independent lines of evidence converge |
| `plausible` | Some evidence but significant counterarguments remain |
| `underdetermined` | Evidence exists but doesn't decisively favor any position |
| `speculative` | Little evidence, mostly theoretical |
| `incompatible` | Strong evidence against |
| `unasked` | Question identified but not yet investigated |

## How to Update

1. Add a new evidence entry (never edit existing ones — append-only)
2. Recompute confidence from all evidence
3. Update `last_updated` timestamp

Do not delete or modify existing evidence entries. The truth map is append-only.
