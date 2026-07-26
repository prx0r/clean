# System Architecture — Complete Engineering Blueprint

## Core Principle

Everything is a directed acyclic graph of claims, organized by the truth map, processed by the factories, and surfaced through Satsang. Every node in every graph is versioned, auditable, and traceable to source.

---

## 1. The Data Model

### 1.1 Primary Entities

```
SO (Source Object) — immutable, one-to-one with primary text/dataset
  │
  ├── RO (Research Object) — versioned extraction from SOs, organized by question
  │     │
  │     ├── EO (Essay Object) — versioned synthesis of ROs, organized as hypothesis + evidence
  │     │     │
  │     │     ├── Essay — published output (factories)
  │     │     └── Video — published output (factories)
  │     │
  │     └── TO (Translation Object) — versioned Sanskrit translation with 7-pass pipeline
  │
  └── Claim — atomic unit of evidence (subject, predicate, object, confidence, source)
        │
        └── Truth Map Question — node in the Bayesian network
              │
              └── Branch (B1-B6) — higher-level interpretation cluster
```

### 1.2 The TPN Structure (The Recommender)

```
UserNode (profile, birth chart, watch history, philosophy page)
  │
  ├── watches → ContentNode (video, essay, RO)
  │     │
  │     ├── links to → TruthMapQuestionNode
  │     │     │
  │     │     └── links to → BranchNode (B1-B6)
  │     │
  │     └── has → EngagementMetrics (watch time, completion, rating)
  │
  ├── asks → Question
  │     │
  │     └── maps to → TruthMapQuestionNode
  │
  └── follows → ScholarNode
        │
        └── produces → ContentNode
```

Edge weights trained from user behavior: P(content_B | content_A, user_profile, context). No LLM in the recommendation path.

---

## 2. The Pipeline (End-to-End)

### 2.1 Paper → Truth Map Update

```
Paper arrives (via cron-acquire or manual)
  → Acquire skill creates Work JSON (metadata + PDF)
  → Extract skill creates SO (structured full text)
  → Agent or human creates RO (themed passages)
  → Claims extracted from RO (subject, predicate, object, confidence)
  → Each claim enters the Propagation Engine as a ClaimRecord:
      ClaimRecord(
        target_feature_ids: ["F1", "F2"],
        log_bayes_factor: computed from evidence weight,
        w_rel: relevance,
        w_map: mapping quality,
        w_aux: source reliability,
        paradigm: "IIT" | "Trika" | "Neuroscience" etc.,
        lbf_confidence: how sure we are of the LBF value
      )
  → PropagationEngine.run() updates feature posteriors
  → Branch probabilities recompute
  → If any question moved from "underdetermined" to "plausible" or higher
    → Hypothesis engine may deprioritize it
```

### 2.2 Question → Content Pipeline

```
User asks question OR hypothesis engine scans truth map
  → Normalize to truth map slug
  → If question has sufficient ROs:
      → Create EO (hypotheses, evidence for/against, tension point)
      → Route to Writing Factory:
          → EO → Essay (3-pass write with quote budget gates)
          → Essay claims extracted → truth map updated
      → Route to Video Factory (optional):
          → Essay → Storyboard → GLSL/PIL render → Composite → YouTube
          → Video claims extracted → truth map updated
  → If question lacks ROs:
      → ACQUIRE mission created → papers acquired → ROs created → proceed
  → If question already answered with high confidence:
      → Return best answer + evidence chain — no content created
```

### 2.3 User Session → Feed Algorithm

```
User opens Satsang
  → Charioteer loads:
      → UserNode (philosophy page, watch history, birth chart)
      → ContentNode graph (all videos, essays, ROs)
      → Edge weights (trained from all user interactions)
  → P(next_content | current_context, user_profile):
      1. Filter by user's topic preferences (hard exclusion)
      2. Prioritize followed scholars and traditions
      3. Mixed-in discovery: content from similar users' watch patterns
      4. Diversity constraint: don't show the same format twice
      5. Freshness boost: content <7 days old gets slight priority
      6. Return ranked list
  → No LLM called. Pure graph traversal.
  → User watches, engages, or skips → edge weights update.
```

---

## 3. Versioning

### 3.1 Git-Based Versioning

```
clean/
├── content/
│   ├── source-metaphysics/
│   │   ├── q-consciousness-fundamental.json    # Each question is one file
│   │   └── q-iccha-jnana-kriya-necessary.json  # Git tracks every change
│   │
│   ├── research-objects/
│   │   └── ro-matter-of-wonder/
│   │       └── ro.json                         # Version field inside
│   │
│   ├── essay-objects/
│   │   └── eo-question-slug.json
│   │
│   └── translation-objects/
│       └── to-spandakarika.json
│
└── resources/
    └── by-scholar/                             # PDFs (git LFS)
```

Every JSON file has a `version` field. Git tracks changes. The RO's `versions[]` array stores the history.

### 3.2 The Append-Only Evidence Log

Truth map evidence entries are never edited — only added. Each entry has:

```json
{
  "evidence_id": "ev_001",
  "source_id": "ro:matter-of-wonder",
  "feature_id": "F1",
  "log_bayes_factor": 0.4,
  "w_rel": 0.85,
  "w_map": 0.65,
  "w_aux": 0.72,
  "paradigm": "trika",
  "timestamp": "2026-07-26T12:00:00Z",
  "supersedes": null,
  "superseded_by": null
}
```

When new evidence replaces old evidence, `supersedes` points to the old ID and `superseded_by` points to the new one. No deletion. Full provenance.

---

## 4. The Persistence Layer

| Data | Store | Format | Access Pattern |
|------|-------|--------|----------------|
| Truth map questions | Git files + D1 | JSON | Read on every page load, write on publish |
| Evidence log | D1 | SQL | Append-only, batch read for propagation |
| User profiles | D1 + JSONB | SQL | Read on every feed request |
| Edge weights (TPN) | D1 | SQL | Read on feed requests, write after each interaction |
| LLM-assisted metadata (w_rel, w_map) | D1 | SQL | Written once per claim |
| Content (ROs, EOs, essays, videos) | Git files | JSON / MP4 | Read by factories, served by R2 |
| Session logs | D1 | SQL | Written after every session, consumed by Dreaming Loop |
| Renditions (videos) | R2 | MP4 | Served directly to users |

---

## 5. The Propagation Engine (Bayesian Core)

```
Input: ClaimRecord{target_feature_ids, log_bayes_factor, w_rel, w_map, w_aux, paradigm}
  → compute_dep_weight(n_prior, paradigm)  # discount for paradigm crowding
  → weighted_lbf = w_rel * w_map * w_dep * w_aux * log_bayes_factor
  → for each target_feature_id:
      feature.log_odds += weighted_lbf
      feature.probability = sigmoid(feature.log_odds)
  → for each branch:
      branch.probability = product of feature probabilities per profile
      normalize so all branches sum to 1.0
  → persist features and branches to D1
  → return delta
```

Full recompute: load all claims from D1, reset features to prior, apply all claims sequentially.
Incremental update: load only new claims, load existing paradigm counts, apply and persist.

---

## 6. The Three Loops

### 6.1 Live Loop (User-Facing)

```
User request comes in
  → Read truth map (fast — file or D1 cache)
  → Read edge weights (D1 — simple SQL query)
  → Compute recommendation (graph traversal, no LLM)
  → Return content
  → Log interaction
```

Latency target: <50ms. No LLM calls in the critical path.

### 6.2 Production Loop (Factory)

```
New claim or question enters
  → Acquire if needed (async — can take minutes)
  → Extract RO (agent-assisted, takes minutes to hours)
  → Create EO (agent-assisted)
  → Route to essay factory (agent writes, ~10-30 min)
  → Route to video factory (render, ~minutes to hours)
  → Each publish triggers truth map update
```

Latency: minutes to hours. LLM calls are fine here.

### 6.3 Dreaming Loop (Nightly)

```
Cron: 2:00 AM
  → Consolidate temporary evidence (promote or discard)
  → Recompute all posteriors from full evidence log
  → Prune stale questions (no updates in 90 days, zero audience interest)
  → Gap analysis: find underdetermined questions with no ROs → generate ACQUIRE missions
  → Re-evaluate past EO proposals:
      - EOs that led to low-engagement content → deprioritize
      - EOs that led to high-engagement content → boost
  → Update edge weights from all user interactions in the last 24 hours
  → Generate daily report: what changed, what moved, what's missing
```

Runs once per 24h. ~5-30 minutes depending on data volume.

---

## 7. The TPN Feed Algorithm (Technical)

### 7.1 Graph Structure

```
Nodes:
  - UserNode(user_id, profile_vector, birth_chart_vector)
  - ContentNode(content_id, feature_vector, branch_id, tradition_tags)
  - TruthMapQuestionNode(question_id, status, confidence)
  - ScholarNode(scholar_id, tradition_tags)

Edges:
  - UserNode → ContentNode: watch (weight = completion_rate)
  - UserNode → ScholarNode: follows (weight = 1.0)
  - ContentNode → TruthMapQuestionNode: bears_on (weight = relevance)
  - ContentNode → ContentNode: co_watch (weight = lift)
  - UserNode → UserNode: similar_profile (weight = cosine_similarity)
```

### 7.2 Inference

```python
def recommend(user_id, k=20):
    user_node = load_user(user_id)
    watched = get_recent_watches(user_id)
    candidate_pool = []

    # 1. Collaborative filtering: what similar users watched
    similar_users = query("""
        SELECT u2.user_id FROM users u1, users u2
        WHERE u1.user_id = ? AND u2.user_id != ?
        ORDER BY cosine_similarity(u1.profile_vector, u2.profile_vector) DESC
        LIMIT 50
    """, (user_id, user_id))
    for similar_user in similar_users:
        candidate_pool.extend(get_top_content(similar_user, k=5))

    # 2. Content-based: expand from recent watches
    for content in watched[-5:]:
        related = query("""
            SELECT content_id FROM content_edges
            WHERE source_id = ? AND edge_type = 'co_watch'
            ORDER BY weight DESC LIMIT 5
        """, (content.id,))
        candidate_pool.extend(related)

    # 3. Diversity filter: ensure mix of formats, traditions, and difficulty
    # 4. Freshness boost: content <7 days old gets +0.1 weight
    # 5. Block list: user's blocked topics are excluded
    # 6. Rank and return top k

    return rank(candidate_pool, user_node)
```

### 7.3 Edge Weight Training

Edge weights are trained from user behavior, not from explicit ratings:

```python
def update_weights(user_id, content_id, engagement_metrics):
    completion = engagement_metrics.completion_rate

    # Co-watch edge: if user watched A then B, increment A→B weight
    previous = get_last_watch(user_id)
    if previous:
        upsert_edge(previous.content_id, content_id, 'co_watch', delta=0.1 * completion)

    # User→Content edge: update preference weight
    upsert_edge(user_id, content_id, 'watch', weight=completion)
```

No explicit ratings needed. Behavior is the signal.

---

## 8. The Charioteer (Real-Time Strategy)

Before serving content, the Charioteer adjusts the feed based on user state:

```python
def charioteer(user_id, current_context) -> dict:
    state = detect_user_state(user_id)
    adjustments = {}

    if state == 'beginner':
        adjustments['max_depth'] = 1
        adjustments['prefer_formats'] = ['video', 'essay']
        adjustments['boost_traditions'] = ['introduction']
    elif state == 'stuck':
        # User watched but didn't engage → try different format
        adjustments['prefer_formats'] = ['audio', 'interactive']
        adjustments['novelty_boost'] = 0.3
    elif state == 'deep_research':
        adjustments['max_depth'] = 5
        adjustments['prefer_formats'] = ['paper', 'translation']
        adjustments['boost_traditions'] = user.favorite_traditions

    return adjustments
```

---

## 9. Deployment Topology

```
┌────────────────────────────────────────────────────┐
│                    Cloudflare                       │
│                                                      │
│  D1: truth_map, edge_weights, user_profiles, logs   │
│  R2: video_renders, art_library, translated_texts   │
│  Pages: studio.tantrafiles.xyz, satsang.digital     │
│  Workers: API routes, video serving, auth           │
│  Queues: async render jobs, nightly dreaming loop   │
│  Cron: DAILY_HYPOTHESIS_SCAN, NIGHTLY_DREAM        │
│  AI Gateway: cached LLM calls, cost tracking        │
│                                                      │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│                    VPS (or your machine)               │
│                                                       │
│  Hermes agent: coordinates factories, runs skills     │
│  Factory pipeline: essaygen, platinum video pipeline  │
│  GLSL renderer: GPU-accelerated shader rendering      │
│  Sanskrit pipeline: 7-pass DeepSeek translation       │
│  Git (clean repo): truth map, ROs, EOs, content       │
│                                                       │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│              User-Facing Layer (Satsang)              │
│                                                       │
│  Web app: feed, philosophy pages, dating, live        │
│  Mobile app: audio-first discovery, meditation timer  │
│  VR app: tradition worlds (Trika, Neoplatonic, etc.)  │
│  PiEEG integration: live EEG biofeedback             │
│  API: truth map queries, content serving, edge weights│
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 10. The Complete Data Flow

```
                    ┌──────────┐
                    │  Paper/  │
                    │ Dataset  │
                    └────┬─────┘
                         ▼
                  ┌──────────────┐
                  │   ACQUIRE    │
                  │  (cron)      │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Work JSON   │
                  │  → SO        │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Extract RO  │
                  │  (claims)    │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐      ┌──────────────────┐
                  │  Propagation │◄─────│  Source          │
                  │  Engine      │      │  Metaphysics     │
                  │  (Bayesian)  │      │  (truth map)     │
                  └──────┬───────┘      └────────┬─────────┘
                         │                       │
                         ▼                       ▼
                  ┌──────────────┐      ┌──────────────────┐
                  │  Question    │◄─────│  Hypothesis      │
                  │  Resolution  │      │  Engine (cron)   │
                  └──────┬───────┘      └──────────────────┘
                         ▼
                  ┌──────────────┐
                  │  Create EO   │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Factories   │
                  │  (essay,     │
                  │   video)     │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Published   │
                  │  Content     │
                  │  → truth map │
                  │  update      │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Satsang     │
                  │  (user       │
                  │  facing)     │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  User        │
                  │  Interaction │
                  │  → edge      │
                  │  weights     │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │  Dreaming    │
                  │  Loop (cron) │
                  │  → prune,    │
                  │  consolidate │
                  └──┬───────┬───┘
                     │       │
                     ▼       ▼
              ┌─────────┐ ┌──────────┐
              │ Updated │ │ ACQUIRE  │
              │ Truth   │ │ Missions │
              │ Map     │ │ (new     │
              │         │ │ papers)  │
              └─────────┘ └──────────┘
```
