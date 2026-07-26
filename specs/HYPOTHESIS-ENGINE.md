# Hypothesis Engine — Full Spec

The perpetual question generator. Scans the truth map for tension points and generates EO proposals.

---

## 1. EO Proposal Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "HypothesisEngineProposal",
  "type": "object",
  "required": [
    "proposal_id", "generated_at", "source", "trigger",
    "eo_proposal", "status"
  ],
  "properties": {
    "proposal_id": {
      "type": "string",
      "pattern": "^prop:[a-z0-9_-]+$"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "source": {
      "type": "string",
      "enum": ["truth_map_scan", "ro_disagreement", "dataset_available", "user_question", "product_performance", "research_directive", "meta_question"]
    },
    "trigger": {
      "type": "string",
      "description": "What specific condition triggered this proposal"
    },
    "eo_proposal": {
      "type": "object",
      "required": ["title", "tension_point", "primary_ros"],
      "properties": {
        "title": { "type": "string", "maxLength": 200 },
        "tension_point": { "type": "string", "maxLength": 2000 },
        "primary_ros": {
          "type": "array",
          "items": { "type": "string", "pattern": "^ro:[a-z0-9_-]+$" }
        },
        "secondary_ros": {
          "type": "array",
          "items": { "type": "string" }
        },
        "hypotheses": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "claim": { "type": "string" },
              "confidence": { "type": "string", "enum": ["strong", "moderate", "speculative"] },
              "supporting_ros": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "novelty_score": { "type": "number", "minimum": 0, "maximum": 1 },
        "depth_score": { "type": "number", "minimum": 0, "maximum": 1 },
        "traditions": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "critic_review": {
      "type": "object",
      "properties": {
        "falsified": { "type": "boolean" },
        "falsification_reason": { "type": "string" },
        "suggested_revision": { "type": "string" }
      }
    },
    "status": {
      "type": "string",
      "enum": ["proposed", "critic_reviewed", "approved", "rejected", "implemented"]
    }
  }
}
```

---

## 2. Question Sources (Ranked)

The engine scans 5 sources, ranked by priority:

| Priority | Source | Method | Output |
|----------|--------|--------|--------|
| 1 | RO disagreement | Find ROs on the same topic with contradictory claims | Highest-quality tension points |
| 2 | Truth map gaps | Questions with status "underdetermined" or "unasked" that have sufficient ROs | Pipeline-ready EOs |
| 3 | User questions | Questions from Satsang users that don't have existing content | Community-driven research |
| 4 | Dataset availability | New datasets entering the system that can test existing questions | Experimental EOs |
| 5 | Product performance | Content with high engagement → propose follow-up EOs on the same topic | Audience-aligned EOs |

---

## 3. Ranking Algorithm Template

```python
def rank_proposals(proposals: list, existing_eos: list) -> list:
    """Rank EO proposals by composite score."""
    for prop in proposals:
        score = 0.0
        
        # Novelty: how different is this from existing EOs?
        prop.novelty_score = compute_novelty(prop, existing_eos)
        score += 2.0 * prop.novelty_score
        
        # Depth: does the tension point have real substance?
        prop.depth_score = estimate_depth(prop)
        score += 2.0 * prop.depth_score
        
        # Feasibility: do the required ROs exist?
        ro_coverage = count_available_ros(prop.eo_proposal.primary_ros)
        score += 1.5 * ro_coverage
        
        # Freshness: how long since we last proposed on this topic?
        days_since = days_since_last_proposal(prop)
        score += 1.0 * min(1.0, days_since / 30.0)
        
        # Tradition diversity boost
        traditions = get_traditions(prop)
        underrepresented = is_underrepresented(traditions)
        if underrepresented:
            score *= 1.3
        
        prop.score = score
    
    return sorted(proposals, key=lambda p: p.score, reverse=True)
```

---

## 4. RO Disagreement Detection

The highest-quality EO proposals come from **contradictions between ROs**, not from gap scanning alone.

```sql
-- Find ROs that share topics but make contradictory claims
SELECT a.ro_id, b.ro_id, a.topic, a.claim, b.claim
FROM ro_passages a
JOIN ro_passages b ON a.topic = b.topic AND a.ro_id < b.ro_id
WHERE a.inference_direction = 'supports'
  AND b.inference_direction = 'undermines'
  AND a.question_id = b.question_id
```

When two ROs disagree on the same truth map question, that's a tension point worth investigating. The engine should prefer these over simple gap-filling.

---

## 5. Anti-Staleness Measures

| Measure | Implementation |
|---------|---------------|
| Novelty scoring | Cosine similarity between proposed tension_point and all existing EO tension_points |
| Diversity sampling | Track tradition frequency in last 20 proposals. Boost underrepresented traditions by 1.3x |
| Random offset | Add ±5% random noise to scores to prevent deterministic repetition |
| Re-open answered questions | If new claims entered evidence_log for a "strongly_supported" question, re-open it |
| Meta-questions | Every 10th proposal: "what are we not asking?" — uses text analysis of RO corpus to find uncovered topics |

---

## 6. Critic Agent Interface

Before an EO proposal enters production, a Critic agent reviews it:

```python
class CriticAgent:
    """Reviews EO proposals and attempts to falsify the central hypothesis."""
    
    def review(self, proposal: dict) -> dict:
        """Returns critic_review dict."""
        tension = proposal['eo_proposal']['tension_point']
        hypotheses = proposal['eo_proposal'].get('hypotheses', [])
        
        # Check 1: Is the tension point actually a disagreement?
        if not self._is_genuine_tension(tension):
            return {"falsified": True, "reason": "Not a genuine tension — both sides may agree"}
        
        # Check 2: Can any hypothesis be falsified in principle?
        for h in hypotheses:
            if not self._has_falsifier(h):
                return {"falsified": True, "reason": f"Hypothesis {h['claim']} is unfalsifiable"}
        
        # Check 3: Does existing evidence already resolve this?
        existing = self._check_existing_evidence(tension)
        if existing['confidence'] > 0.8:
            return {"falsified": True, "reason": "Question already answered with high confidence"}
        
        return {"falsified": False, "suggested_revision": self._suggest_improvements(proposal)}
```

---

## 7. Storage

```
Path: content/hypothesis-engine/proposals/{proposal_id}.json
Backend: Git filesystem
Index: D1 table (proposal_id, source, status, score, created_at)
```

```sql
CREATE TABLE hypothesis_proposals (
  proposal_id TEXT PRIMARY KEY,
  generated_at TEXT NOT NULL,
  source TEXT NOT NULL,
  trigger TEXT,
  status TEXT NOT NULL DEFAULT 'proposed',
  novelty_score REAL,
  depth_score REAL,
  score REAL,
  critic_falsified INTEGER DEFAULT 0,
  implemented_as TEXT,         -- eo_id if implemented
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 8. Hermes Skill Invocation

```bash
# Daily hypothesis scan
hermes -z "Run hypothesis engine. Scan truth map for underdetermined questions and RO disagreements. Output top 3 EO proposals." --skills hypothesis-engine -m "deepseek-v4-flash"

# Critic review
hermes -z "Review EO proposal prop:iccha-kriya-gap. Attempt to falsify the central hypothesis." --skills critic -m "deepseek-v4-flash"
```

---

## 9. Open Questions for Codex

1. **Autonomy vs garbage:** The FLAWS doc says the engine will produce boring questions on infinite repeat. Is RO disagreement detection + novelty scoring + Critic agent sufficient, or does it need a human veto gate?

2. **Novelty scoring method:** At 200+ EOs, comparing against all existing tension_points becomes expensive. Should we use Cloudflare Vectorize (embedding similarity), or is TF-IDF on keywords sufficient?

3. **Tradition diversity:** Trika has the most ROs and will dominate proposals. Should we implement tradition quotas (guarantee N% proposals from underrepresented traditions) or just boost scores?

4. **Meta-questions:** "What are we not asking?" is a genuinely hard problem. How should the engine identify conceptual gaps that aren't represented anywhere in the truth map?
