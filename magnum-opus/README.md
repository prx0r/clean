# Magnum Opus — Unified Content Factory

## What This Is

The architectural blueprint for an autonomous content research and production system. Hermes-orchestrated, Cloudflare-deployed, versioned at every layer.

Four factories, one pipeline:

```
Source Material → Research Objects → Essay Objects → Products → Analytics
                        ↓                 ↓
               Hypothesis Engine    Factory 2-4
               (perpetual probing)  (papers, video, data)
```

## Key Files

| File | What It Covers |
|------|----------------|
| `01-VISION.md` | Unified vision, why this exists |
| `02-AUDIT-SUMMARY.md` | Current state of all assets in blog project |
| `03-RESEARCH-OBJECTS.md` | RO system: versioned, source-linked, agent-navigable |
| `04-ESSAY-OBJECTS.md` | EO system: guided enquiries from ROs |
| `05-SOURCE-METAPHYSICS.md` | Truth map: solved/unsolved, hypothesis tracking |
| `06-FACTORY-ARCHITECTURE.md` | The four factories and their pipelines |
| `07-HYPOTHESIS-ENGINE.md` | Perpetual question generation at tension points |
| `08-FARM-INFRA.md` | Cloudflare farm infrastructure spec |
| `09-HERMES-ORCHESTRATION.md` | Hermes as orchestrator |

## Core Insight

The system is a **closed-loop epistemology engine**:

1. Source material enters → becomes Research Objects (canonical references)
2. ROs combine → become Essay Objects (guided enquiries)
3. EOs + hypotheses → become Products (papers, videos, experiments)
4. Products → return data → update the truth map (source metaphysics)
5. Truth map → generates new hypotheses → cycle continues

Everything is git-versioned, linked by provenance, and auditable from product back to primary source.
