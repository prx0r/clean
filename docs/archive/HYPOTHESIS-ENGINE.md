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
| Re-open answered questions | If new claims entered `claims` for a "strongly_supported" question, re-open it |
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

---

## 10. Codex Design Decisions

### Autonomy vs Garbage

RO disagreement detection is necessary but not sufficient. The engine needs a Critic gate at the proposal stage, but not a permanent human veto gate for every proposal.

Use a two-tier policy:

| Proposal Risk | Gate |
|---------------|------|
| Low risk: links existing ROs, has two-sided tension, no publication scheduled | Autonomous Critic approval |
| Medium risk: creates new truth map question or uses derived claims | Critic approval + delayed implementation queue |
| High risk: changes posteriors, starts production, or claims novelty without RO support | Human review required |

This preserves autonomy for research discovery while preventing generated questions from turning directly into published epistemic commitments.

Minimum approval checks:

1. At least two live positions or one explicit missing-position gap.
2. At least one primary RO or source path per live position.
3. No near-duplicate EO above the novelty threshold.
4. At least one falsifier or discriminating question.
5. No direct posterior update from the proposal itself.

### Novelty Scoring Method

At 200+ EOs, do not introduce Cloudflare Vectorize yet. Use deterministic text similarity first:

1. Normalize `tension.summary`, `positions[].claim`, title, and traditions.
2. Compute TF-IDF or BM25 over existing EOs.
3. Penalize exact tradition/topic reuse from the last 20 proposals.
4. Store the top nearest neighbors and similarity scores in the proposal record.

Move to Vectorize only when deterministic similarity produces clear false negatives or the EO count reaches the low thousands. The first implementation benefits more from explainable duplicate detection than semantic recall.

### Tradition Diversity

Use a multiplicative boost, not hard quotas. Quotas can force bad proposals from thin traditions and corrupt the quality signal.

Recommended diversity multiplier:

```python
representation = recent_tradition_count / max(1, total_recent_proposals)
target = corpus_tradition_count / max(1, total_ros)
underrep = max(0.0, target - representation)
diversity_multiplier = min(1.5, 1.0 + underrep)
```

Add a floor rule instead of a quota: if a tradition has enough source material for at least one two-sided EO and has had zero proposals in the last N cycles, force it into the candidate set, then let the ranker and Critic decide.

### Meta-Questions

The engine should identify missing questions by comparing corpus coverage against truth-map coverage, not by asking an LLM to brainstorm in the abstract.

Pipeline:

1. Extract topic/tradition/concept facets from ROs and source objects.
2. Build co-occurrence pairs and triples: `(tradition, concept)`, `(thinker, concept)`, `(concept, question_family)`.
3. Compare against existing truth map questions and EOs.
4. Emit gaps only where there is source support but no corresponding question or only one-sided evidence.
5. Send the gap through Critic as a meta-question proposal.

Meta-question examples should look like:

```json
{
  "trigger": "RO corpus has 8 Sufi references to imaginal perception but no question linking imaginal perception to pattern-space ontology.",
  "missing_axis": ["sufism", "imaginal_perception", "pattern_space"],
  "supporting_ros": ["ro:..."],
  "proposed_question": "Does imaginal perception function as evidence for pattern-space realism?"
}
```

The key constraint: a meta-question must point to a corpus asymmetry, not merely a clever-sounding absent topic.
