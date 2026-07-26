# 07 — Hypothesis Engine

The perpetual question generator. Scans the truth map for tension points and generates new EOs.

## How It Works

1. **Scan** the source metaphysics for `underdetermined` or `unasked` questions
2. **Rank** by:
   - How many ROs exist on the topic
   - How deep the tension is (do ROs disagree?)
   - Freshness (how long since last EO was created on this topic)
   - Alignment with research directive priorities
3. **Generate** an EO proposal for the top-ranked question
4. **Submit** for human review (or auto-create if confidence is high)
5. **Track** — ensure the same question isn't proposed twice

## Anti-Staleness Measures

- **Novelty scoring**: every proposed question is checked against all existing EOs
- **Diversity sampling**: don't let one topic dominate — spread across traditions
- **Random offset**: introduce stochasticity in ranking to explore the full space
- **Answer recycling**: if a question was "answered" but new evidence appeared, re-open it
- **Meta-questions**: periodically ask "what are we not asking?" using text analysis of the corpus

## Question Sources

1. **Direct from RESEARCH_DIRECTIVE** — the 72 priority questions
2. **From source metaphysics gaps** — `underdetermined` status questions
3. **From RO disagreements** — when two ROs contradict on the same topic
4. **From dataset availability** — when new datasets enter the system, ask what they can test
5. **From product performance** — when a video or paper gets strong engagement, dive deeper

## Output

The engine outputs EO proposals:

```json
{
  "proposal_id": "prop:iccha-kriya-gap",
  "generated_at": "2026-07-26T12:00:00Z",
  "source": "source_metaphysics_scan",
  "trigger": "question q:iccha-jnana-kriya-necessary is underdetermined",
  "eo_proposal": {
    "title": "Is icchā-jñāna-kriyā a Necessary Architecture of Manifestation?",
    "tension_point": "Abhinavagupta vs active inference — same structure or category error?",
    "primary_ros": ["ro:matter-of-wonder", "ro:utpaladeva-ipk"],
    "novelty_score": 0.85,
    "depth_score": 0.92
  },
  "status": "proposed"
}
```

## Implementation

This is currently NOT IMPLEMENTED. It should be a Hermes skill or cron job that:

1. Reads the source metaphysics truth map
2. Applies the ranking algorithm
3. Generates EO proposals
4. Writes them to `content/hypothesis-engine/proposals/`

Frequency: daily scan, weekly generation cycle.
