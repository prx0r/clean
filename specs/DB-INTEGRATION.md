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
  target_question_id TEXT,
  target_feature_ids TEXT NOT NULL,    -- JSON array
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
CREATE INDEX idx_claims_feature ON claims(target_feature_ids);
CREATE INDEX idx_claims_paradigm ON claims(paradigm);
CREATE INDEX idx_claims_created ON claims(created_at);
CREATE INDEX idx_claims_supersedes ON claims(supersedes);
CREATE INDEX idx_q_status ON truth_map_questions(status);
```

---

## 2. PropagationDB Protocol Implementation (Cloudflare D1 Worker)

```python
"""
PropagationDB implementation backed by Cloudflare D1 via REST API.
Designed to run in a Cloudflare Worker context (30s CPU limit).
"""

import json
import os
from typing import Dict, List, Optional
from urllib.request import Request, urlopen

from truthengine_propagation import (
    FeatureState, ClaimRecord, PropagationDB
)


class D1PropagationDB(PropagationDB):
    """
    Connects propagation engine to Cloudflare D1 via Worker API.
    
    The Worker API exposes these endpoints:
      GET  /api/d1/query?sql=...  — run SQL, return JSON rows
      POST /api/d1/execute         — run SQL with params, return changes
    """
    
    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self._feature_cache: Optional[Dict[str, FeatureState]] = None
    
    def _query(self, sql: str, params: Optional[list] = None) -> list:
        url = f"{self.api_base}/api/d1/query"
        body = json.dumps({"sql": sql, "params": params or []}).encode()
        req = Request(url, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })
        with urlopen(req) as resp:
            return json.loads(resp.read())
    
    def _execute(self, sql: str, params: Optional[list] = None) -> dict:
        url = f"{self.api_base}/api/d1/execute"
        body = json.dumps({"sql": sql, "params": params or []}).encode()
        req = Request(url, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })
        with urlopen(req) as resp:
            return json.loads(resp.read())
    
    # ── Feature operations ──
    
    def get_all_features(self) -> List[FeatureState]:
        rows = self._query("SELECT * FROM feature_states ORDER BY feature_id")
        features = []
        for row in rows:
            features.append(FeatureState(
                id=row['feature_id'],
                prior_log_odds=row['prior_log_odds'],
                log_odds_val=row['current_log_odds'],
            ))
        return features
    
    def save_features(self, features: Dict[str, FeatureState]):
        for fid, fs in features.items():
            self._execute(
                """UPDATE feature_states 
                   SET current_log_odds = ?, probability = ?, last_updated = datetime('now')
                   WHERE feature_id = ?""",
                [fs.log_odds, fs.probability, fid]
            )
    
    # ── Claim operations ──
    
    def get_all_claims(self) -> List[ClaimRecord]:
        rows = self._query(
            "SELECT * FROM claims WHERE is_retracted = 0 ORDER BY created_at"
        )
        return [self._row_to_claim(r) for r in rows]
    
    def get_claims_by_ids(self, claim_ids: List[str]) -> List[ClaimRecord]:
        if not claim_ids:
            return []
        placeholders = ','.join('?' for _ in claim_ids)
        rows = self._query(
            f"SELECT * FROM claims WHERE claim_id IN ({placeholders})",
            claim_ids
        )
        return [self._row_to_claim(r) for r in rows]
    
    def _row_to_claim(self, row: dict) -> ClaimRecord:
        return ClaimRecord(
            id=row['claim_id'],
            target_feature_ids=json.loads(row['target_feature_ids']),
            log_bayes_factor=row['log_bayes_factor'],
            w_rel=row['w_rel'],
            w_map=row['w_map'],
            w_aux=row['w_aux'],
            paradigm=row['paradigm'],
            is_retracted=bool(row['is_retracted']),
        )
    
    def count_claims_by_paradigm(self, feature_id: str, paradigm: str) -> int:
        row = self._query(
            """SELECT COUNT(*) as cnt FROM claims 
               WHERE target_feature_ids LIKE ? 
               AND paradigm = ? AND is_retracted = 0""",
            [f'%{feature_id}%', paradigm]
        )
        return row[0]['cnt'] if row else 0
    
    # ── Branch operations ──
    
    def get_branch_feature_profiles(self) -> Dict[str, Dict[str, str]]:
        rows = self._query("SELECT * FROM branch_profiles")
        profiles: Dict[str, Dict[str, str]] = {}
        for row in rows:
            bid = row['branch_id']
            if bid not in profiles:
                profiles[bid] = {}
            profiles[bid][row['feature_id']] = row['level']
        return profiles
    
    def save_branch_probabilities(self, branch_probs: Dict[str, float]):
        for bid, prob in branch_probs.items():
            self._execute(
                "UPDATE branch_probabilities SET probability = ?, last_updated = datetime('now') WHERE branch_id = ?",
                [prob, bid]
            )
```

---

## 3. Orchestration

### Full Recompute (Nightly Dreaming Loop)

```python
def nightly_full_recompute(db: D1PropagationDB):
    """Reset all features to prior, replay all claims, persist."""
    engine = PropagationEngine(db, dep_alpha=0.5)
    result = engine.run()  # new_claim_ids=None → full recompute
    return result
```

### Incremental Update (On Publish)

```python
def on_new_evidence(db: D1PropagationDB, new_claim_ids: List[str]):
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
      const db = new D1PropagationDB(env.API_BASE, env.API_KEY);
      const result = nightly_full_recompute(db);
      await env.AI_GATEWAY.log('nightly_dream', result);
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
    → D1PropagationDB.count_claims_by_paradigm()
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
| Full recompute (1000 claims, 8 features) | ~2-5s | Sequential claim processing |
| Full recompute (10000 claims, 8 features) | ~20-30s | Approaches Worker CPU limit |
| Branch probability derivation | < 50ms | Simple product math |
| Paradigm count query | < 20ms | Indexed LIKE query |

**Mitigation for large recomputes:** If claim count exceeds ~5000, offload full recompute to VPS instead of Worker. Use Worker only for incremental updates.
