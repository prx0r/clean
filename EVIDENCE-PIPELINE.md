# Evidence Pipeline — Paper → Information Packet → Truth Map Update

## Architecture

```
Paper (PDF/text)
  → Hermes skill (extract claims via LLM)
  → Information Packet JSON (versioned, git-stored)
  → Review (human corrects weights if needed)
  → Ingestion (claims → D1, propagation runs)
  → Delta recorded (before/after feature + branch states)
  → Packet committed to git
```

## Information Packet Schema

```json
{
  "packet_id": "ip:arkani-hamed-amplituhedron-2013",
  "schema_version": 1,
  "source": {
    "title": "The Amplituhedron",
    "authors": ["Nima Arkani-Hamed", "Jaroslav Trnka"],
    "arxiv_id": "1312.2007",
    "year": 2013,
    "type": "paper"
  },
  "extracted_by": "deepseek-v4-flash",
  "extracted_at": "2026-07-26T12:00:00Z",
  "version": "1.0.0",
  "status": "draft",
  "claims": [
    {
      "claim_id": "cl:amplituhedron-spacetime-not-fundamental",
      "claim_text": "The amplituhedron shows that locality and unitarity are emergent properties of scattering amplitudes, not fundamental axioms of spacetime.",
      "targets": [
        {"target_id": "D4", "target_type": "discriminator"},
        {"target_id": "F8", "target_type": "feature"}
      ],
      "log_bayes_factor": 0.6,
      "w_rel": 0.75,
      "w_map": 0.6,
      "w_aux": 0.7,
      "paradigm": "high_energy_physics",
      "falsifier": {
        "type": "formal",
        "condition": "A derivation showing the amplituhedron reduces to standard QFT without requiring non-spacetime ontology.",
        "status": "untested"
      },
      "evidence_role": "primary",
      "reasoning": "The amplituhedron eliminates locality and unitarity as axioms, deriving them from positive geometry. This directly weakens naive spacetime-fundamental B2 and strengthens structural B1/B3 readings of D4."
    }
  ],
  "review": {
    "reviewed_by": null,
    "reviewed_at": null,
    "corrections": []
  }
}
```

## Pipeline Steps

### Step 1: Extract

A Hermes skill (or standalone script) takes a paper and produces an information packet:

```bash
python scripts/extract-claims.py \
  --paper arxiv:1312.2007 \
  --output content/information-packets/ip-arkani-hamed-amplituhedron-2013.json
```

The LLM is prompted to:
1. Read the paper abstract + key sections
2. Identify claims that bear on D1-D5 discriminators or F1-F8 features
3. For each claim, estimate log_bayes_factor, w_rel, w_map, w_aux
4. Provide reasoning for each estimate
5. Map to the truth map targets

### Step 2: Review

The packet is a git file. A human (or Codex) reviews the weights and corrects if needed:

```json
"review": {
  "reviewed_by": "codex",
  "reviewed_at": "2026-07-27T10:00:00Z",
  "corrections": [
    {
      "claim_id": "cl:amplituhedron-spacetime-not-fundamental",
      "field": "log_bayes_factor",
      "old_value": 0.6,
      "new_value": 0.45,
      "reason": "Overstated — the amplituhedron covers N=4 SYM only, not general QFT"
    }
  ]
}
```

### Step 3: Ingest

When a packet is approved, claims are inserted into D1, propagation runs, and the delta is recorded:

```python
from truthengine_working import build_truth_map_db, PropagationEngine

db = build_truth_map_db("truth_map.db")
engine = PropagationEngine(db)

# Record state before
before = engine.run()

# Ingest packet claims
for claim in packet["claims"]:
    db.add_claim_dict(claim)

# Run propagation
after = engine.run()

# Record delta
delta = {
    "packet_id": packet["packet_id"],
    "before": before,
    "after": after,
    "feature_deltas": {
        fid: after["features"][fid] - before["features"][fid]
        for fid in before["features"]
    },
    "branch_deltas": {
        bid: after["branches"][bid] - before["branches"][bid]
        for bid in before["branches"]
    }
}
```

### Step 4: Version

The packet is committed to git. The delta log is stored in D1 or as a JSON file.

```
content/information-packets/
├── ip-arkani-hamed-amplituhedron-2013.json       (v1.0.0)
├── ip-arkani-hamed-amplituhedron-2013.json       (v1.0.1 — corrected)
├── ip-tononi-iti-2014.json
├── ip-friston-free-energy-2010.json
└── ip-levin-bioelectric-2021.json
```

## What To Build Now

1. `scripts/extract-claims.py` — takes arxiv ID or PDF path → LLM extraction → information packet JSON
2. `scripts/ingest-packet.py` — takes packet JSON → inserts claims → runs propagation → records delta
3. `content/information-packets/` — directory for versioned packets
4. Test with 3 papers at different confidence levels:
   - Strong falsifiable result (e.g., amplituhedron → bears on D4)
   - Strong empirical study (e.g., IIT exclusion experiment → bears on D3)
   - Philosophical argument (e.g., Chalmers hard problem → bears on D3, lower weights)

## The ML Question

Don't build a neural net yet. The pipeline produces structured, reviewable data. After 100+ corrected packets, you'll have a training set of (paper_text → weight_corrections). Then you can:

- Fine-tune the LLM on corrected weight assignments
- Train a small regressor to predict weights from paper features
- Use the geometric engine (blog project) to learn correction patterns

But premature ML just obscures bad data. First build the pipeline, run 100 papers, correct the errors, and *then* ask whether learning improves the estimates.
