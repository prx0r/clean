# Codex: Discriminator Calibration & Pipeline Design

Three things need your reasoning:

## 1. Branch Effect Multipliers

The D1-D5 specs define branch effects like `{"D1": {"yes": {"B1": 0.35, "B2": 1.25, ...}}}`. These are currently guessed. They need to be:

- **Consistent across discriminators** — D1=yes penalizing B4 at 0.25 and D3=yes supporting B4 should not conflict
- **Calibrated to actual science** — how much does the amplituhedron really weaken B2 vs strengthen B1?
- **Asymptotically correct** — when a discriminator passes threshold, the branch multiplier should approach a mask-like value (near 0 for eliminated, high for surviving)

Design the full 5×6 matrix (5 discriminators × 2 answers × 6 branches = 60 multipliers). Justify each one against falsifiable science.

## 2. The Feature-Discriminator Mapping

D1-D5 need lower-level F1-F8 features feeding into them. Currently:
- D3 (intrinsic phenomenality) should be fed by F1 (consciousness_fundamental)
- D4 (pattern space reality) should be fed by F2+F3
- D2 (macro causation) should be fed by F4+F6

But many existing claims target F1-F8, not D1-D5. Design the mapping function: given a claim targeting any feature, how does it propagate up to the relevant discriminator? Should this be a fixed weight table or learned?

## 3. Claim Extraction Prompt

The pipeline I'm building (`scripts/extract-claims.py`) takes a paper and produces an information packet. The core is the LLM prompt that extracts claims with estimated weights. Design this prompt:

- How to read a paper (abstract + intro + conclusion + key results)
- How to identify claims bearing on D1-D5 discriminators
- How to estimate log_bayes_factor, w_rel, w_map, w_aux with reasoning
- How to handle papers that don't bear on any discriminator (flag as auxiliary)
- The exact JSON output schema

The prompt must prevent overclaiming — a paper about quantum gravity doesn't automatically prove or disprove B4.

## 4. Answer Priority

The decision tree (D1→D2/D3→...) is the default, but expected information gain should pick the actual next question. Design the EIG computation: how to calculate H(current_branch_distribution) and E[answer][H(branch_distribution | answer)] using the current discriminator posteriors.

Output your reasoning in a `CODEX-NOTES.md` or directly update `TRUTHMAP-REDESIGN.md` with the calibrated multipliers, mapping function, and prompt template.
