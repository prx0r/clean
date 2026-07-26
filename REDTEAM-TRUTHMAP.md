# Red Team: Break the Truth Map

Goal: Find failures in the propagation engine (`truthengine-propagation.py`) and its SQLite runtime (`truthengine_working.py`).

The engine passed 6 happy-path tests. Now try to break it with pathological inputs, edge cases, and adversarial conditions. For each failure found, decide whether to fix the engine or document the constraint.

## Attack Vectors

### Math Edge Cases
- `log_bayes_factor = ±1000` — does sigmoid overflow? Does the `if x > 709` guard work?
- All weights = 0 (`w_rel = w_map = w_aux = 0`) — does the engine produce NaN? Should it reject zero-weight claims?
- Weighted_lbf underflow — very small numbers multiplied together, does anything disappear?
- Paradigm crowding with 1000 claims from the same paradigm — does w_dep asymptote correctly to ~0? Does it ever produce negative or NaN?
- Negative weights — should these be allowed? What if `w_rel < 0`?

### Logical Pathologies
- Claim bears on features that don't exist (e.g., `target_feature_ids = ["F99"]`)
- Branch profile references a feature that doesn't exist (`BRANCH_PROFILES` has `F99`)
- Question `feature_ids` references features that don't exist
- Supersede a claim that's already superseded (double-supersession chain)
- Both `is_retracted = True` and `superseded_by` is null
- `supersedes` points to a claim_id that doesn't exist
- Empty claims list — does propagation gracefully return priors?
- All claims retracted — should revert to prior state

### Incremental Update
- Run incremental with `new_claim_ids = []` — empty list should be a no-op
- Run incremental with claim IDs that don't exist
- Run incremental, then full recompute — do they match?
- Run incremental twice with the same claim ID (double-counting guard?)
- Interleave: add claim A, incremental A, add claim B, incremental B, full recompute — do increments match full?

### Data Integrity
- Duplicate `claim_id` inserted — does `INSERT OR REPLACE` silently overwrite?
- `claim_features` row without a matching `claims` row (orphaned)
- Question status threshold boundaries: confidence = 0.749 (should be underdetermined), 0.750 (should be strongly_supported)
- Question with zero features — what happens in `save_question_states`?

### Performance
- Time to run 1000 claims through full recompute
- Time to run incremental update with 10 new claims against 1000 existing
- Memory usage with large claim sets (the `_rows_to_claims` grouping creates dicts)

## Instructions

1. Write new test methods in `test_truthengine_working.py` that probe these attack vectors
2. For each test, document:
   - What you expected to happen
   - What actually happened
   - Whether it's a bug to fix or a constraint to document
3. If you find a bug, fix the engine code directly
4. If you find a design constraint, document it in a `REDTEAM-FINDINGS.md` file

Run the tests with:
```bash
PYTHONPYCACHEPREFIX=/tmp/cx-train-pycache python3 -m unittest test_truthengine_working -v
```

Output a summary report of what survived, what broke, and what was fixed.
