# DB Integration — Propagation Engine ↔ D1

Connects the `truthengine-propagation.py` math to live Cloudflare D1 data.

---

## 1. D1 Schema (All Tables)

```sql
-- Truth map questions (metadata + derived state)
CREATE TABLE truth_map_questions (
  question_id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'unasked',
  confidence REAL NOT NULL DEFAULT 0.0,
  feature_ids TEXT NOT NULL DEFAULT '[]',    -- JSON array ["F1","F2",...]
  branches TEXT NOT NULL DEFAULT '[]',       -- JSON array ["B1","B2",...]
  parent_question TEXT,
  best_answer TEXT,
  last_updated TEXT,
  last_updated_by TEXT
);

-- Evidence log (append-only, never edited)
CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY,
  schema_version INTEGER NOT NULL DEFAULT 1,
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  evidence_role TEXT NOT NULL DEFAULT 'primary',
  source_cluster TEXT,
  method_family TEXT,
  target_question_id TEXT,
  log_bayes_factor REAL NOT NULL,
  w_rel REAL NOT NULL DEFAULT 1.0,
  w_map REAL NOT NULL DEFAULT 1.0,
  w_aux REAL NOT NULL DEFAULT 1.0,
  paradigm TEXT,
  claim_text TEXT NOT NULL,
  falsifier TEXT,                      -- JSON or null
  is_retracted INTEGER NOT NULL DEFAULT 0,
  supersedes TEXT,
  superseded_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  extracted_by TEXT,
  FOREIGN KEY (target_question_id) REFERENCES truth_map_questions(question_id)
);

-- Claim-to-feature join table. Required for indexed feature queries.
CREATE TABLE claim_features (
  claim_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  PRIMARY KEY (claim_id, feature_id),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

-- Feature states (computed by propagation engine)
CREATE TABLE feature_states (
  feature_id TEXT PRIMARY KEY,          -- F1..F8
  label TEXT NOT NULL,
  prior_log_odds REAL NOT NULL,
  current_log_odds REAL NOT NULL,
  probability REAL NOT NULL,
  last_updated TEXT NOT NULL
);

-- Branch probabilities (derived from feature posteriors)
CREATE TABLE branch_probabilities (
  branch_id TEXT PRIMARY KEY,           -- B1..B6
  label TEXT NOT NULL,
  probability REAL NOT NULL,
  score_type TEXT NOT NULL DEFAULT 'relative_support',
  last_updated TEXT NOT NULL
);

-- Branch feature profiles (which features each branch depends on)
CREATE TABLE branch_profiles (
  branch_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  level TEXT NOT NULL CHECK(level IN ('high','low','agnostic')),
  PRIMARY KEY (branch_id, feature_id)
);

-- Indexes
CREATE INDEX idx_claims_question ON claims(target_question_id);
CREATE INDEX idx_claims_paradigm ON claims(paradigm);
CREATE INDEX idx_claims_cluster ON claims(source_cluster);
CREATE INDEX idx_claims_created ON claims(created_at);
CREATE INDEX idx_claims_supersedes ON claims(supersedes);
CREATE INDEX idx_claim_features_feature ON claim_features(feature_id);
CREATE INDEX idx_q_status ON truth_map_questions(status);
```

---

## 2. PropagationDB Protocol Implementation (Cloudflare D1 Worker)

The SQLite adapter in `truthengine-db.py` cannot be ported mechanically. SQLite uses `conn.execute()` and row cursors; Cloudflare D1 inside a Worker uses `env.DB.prepare(sql).bind(...).all()` / `.run()` and should be implemented in TypeScript for production Worker execution.

The Python propagation engine remains valid as the reference implementation and offline recompute tool. The production D1 adapter should implement the same 7 protocol operations with these query boundaries:

| Protocol method | D1 boundary | Notes |
|-----------------|-------------|-------|
| `get_all_features()` | Query | One `SELECT` from `feature_states`; hydrate in memory |
| `get_all_claims()` | Query | One joined query from `claims` + `claim_features`; group rows by `claim_id` |
| `get_claims_by_ids(ids)` | Query | One joined query with bound placeholders/chunking |
| `count_claims_by_paradigm(feature_id, paradigm)` | Avoid for batch mode | Keep only for compatibility; use bulk counts below |
| `save_features(features)` | Batched writes | Use D1 batch or prepared statement loop |
| `save_branch_probabilities(scores)` | Batched writes | Persist as `relative_support`, not calibrated posterior |
| `get_branch_feature_profiles()` | Query | One `SELECT` from `branch_profiles`; group by branch |

Claim hydration query:

```sql
SELECT
  c.claim_id,
  c.log_bayes_factor,
  c.w_rel,
  c.w_map,
  c.w_aux,
  c.paradigm,
  c.source_cluster,
  c.method_family,
  c.is_retracted,
  cf.feature_id
FROM claims c
JOIN claim_features cf ON cf.claim_id = c.claim_id
WHERE c.is_retracted = 0
ORDER BY c.created_at, c.claim_id, cf.feature_id;
```

The adapter groups rows by `claim_id` and emits one `ClaimRecord` per claim with `target_feature_ids` collected from the joined rows.

Bulk dependence counts:

```sql
SELECT
  cf.feature_id,
  c.paradigm,
  COALESCE(c.source_cluster, '') AS source_cluster,
  COALESCE(c.method_family, '') AS method_family,
  COUNT(*) AS claim_count
FROM claims c
JOIN claim_features cf ON cf.claim_id = c.claim_id
WHERE c.is_retracted = 0
  AND cf.feature_id IN (?, ?, ?, ?, ?, ?, ?, ?)
  AND c.paradigm IN (?, ...)
  AND c.claim_id NOT IN (?, ...)
GROUP BY cf.feature_id, c.paradigm, source_cluster, method_family;
```

Use this once per incremental run, not once per feature/paradigm pair. For full recompute, counts should be built in memory while replaying claims from priors.

---

## 3. Orchestration

### Full Recompute (Nightly Dreaming Loop)

```python
def nightly_full_recompute(db):
    """Reset all features to prior, replay all claims, persist."""
    engine = PropagationEngine(db, dep_alpha=0.5)
    result = engine.run()  # new_claim_ids=None → full recompute
    return result
```

This can run against SQLite, a D1-backed admin adapter, or a TypeScript port of the engine. The production Worker should not shell out to Python.

### Incremental Update (On Publish)

```python
def on_new_evidence(db, new_claim_ids: List[str]):
    """Only process new claims, load existing paradigm counts, update."""
    engine = PropagationEngine(db, dep_alpha=0.5)
    result = engine.run(new_claim_ids=new_claim_ids)
    return result
```

### Scheduled Cron (Cloudflare Workers Cron Triggers)

```toml
[triggers]
crons = ["0 2 * * *"]  # 2 AM daily — nightly dream
```

```javascript
// worker/src/index.ts
export default {
  async scheduled(event, env, ctx) {
    if (event.cron === '0 2 * * *') {
      ctx.waitUntil(runTruthMapMaintenance(env));
    }
  }
}
```

---

## 4. Data Flow

```
Publish event (video/essay/RO created)
  → Claims extracted from content
  → INSERT INTO claims (D1)
  → PropagationEngine.run(new_claim_ids=[...])
    → D1PropagationDB.get_claims_by_ids()
    → D1PropagationDB.bulk_dependence_counts()
    → Compute updates
    → D1PropagationDB.save_features()
    → D1PropagationDB.save_branch_probabilities()
  → UPDATE truth_map_questions SET confidence, status
  → Done
```

---

## 5. Performance Considerations

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| Single claim insert | < 10ms | Simple INSERT |
| Incremental update (1-10 claims) | < 100ms | 1-2 queries |
| Full recompute (1000 claims, 8 features) | Expected to fit paid Worker CPU if implemented in TS and batched | Verify with profiling |
| Full recompute (10000 claims, 8 features) | Do not assume it fits default limits | Prefer Queue/Workflow/VPS/offline job |
| Branch support derivation | < 50ms | Simple product math; display-only |
| Bulk dependence count query | One grouped query | Uses `claim_features`, not JSON `LIKE` |

**Mitigation for large recomputes:** If claim count exceeds the profiled Worker budget, offload full recompute to Queues/Workflows, a VPS, or an offline scheduled job. Use Worker requests for incremental updates and maintenance triggers.

---

## 6. Codex Review Conclusions

### SQLite to D1 Gap

The SQLite implementation is a valid reference adapter, but the D1 design must change in three ways:

1. Implement the live adapter in TypeScript with native D1 prepared statements.
2. Replace JSON-array feature storage with `claim_features`.
3. Replace per-feature/per-paradigm count calls with one grouped bulk query.

The original Python REST bridge is acceptable only as an external admin/client pattern. It is not the Worker runtime design.

### Worker Limits

Do not design around an assumed hard 30 second wall clock limit. Current Cloudflare docs distinguish CPU time from wall time: paid Workers default to 30 seconds of CPU and can be configured up to 5 minutes; Cron Triggers have 15 minutes wall time. The spec should still profile against the default budget and keep full recompute off the request path.

### Branch Normalization

Persist branch output as `relative_support`. The validation tests assert directional movement and ranking stability, which this metric can support. They do not establish calibrated branch probabilities.

### Bulk Count Query Design

The engine should grow a new optional protocol method:

```python
def bulk_dependence_counts(
    self,
    feature_ids: list[str],
    paradigms: list[str],
    exclude_claim_ids: list[str],
) -> dict[tuple[str, str, str, str], int]: ...
```

Adapters that do not implement it may fall back to `count_claims_by_paradigm`, but D1 must implement the bulk path.
