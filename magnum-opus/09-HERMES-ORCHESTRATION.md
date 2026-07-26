# 09 — Hermes Orchestration

Hermes is the brain. Everything routes through Hermes.

## How Hermes Ties It Together

```
                    ┌──────────────────┐
                    │     HERMES       │
                    │  (orchestrator)  │
                    └──┬────┬────┬────┘
                       │    │    │
              ┌────────┘    │    └────────┐
              ▼             ▼             ▼
        RESEARCH       WRITING        VIDEO
        skills         skills         skills
     ┌─────────┐   ┌─────────┐   ┌──────────┐
     │ acquire │   │  write  │   │platinum- │
     │ search  │   │source-to│   │ designer  │
     │ explore │   │ -essay  │   │platinum- │
     │   RO    │   │         │   │ renderer  │
     │ creator │   │         │   │ factory-  │
     └─────────┘   └─────────┘   │ pipeline  │
                                 └──────────┘
```

## Current Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `acquire` | Download papers, find OA copies | Research |
| `search` | Map concepts to modern research | Research |
| `explore` | Browse knowledge graph | Research |
| `navigate` | Show connections between assets | Research |
| `write` | Academic writing | Writing |
| `source-to-essay` | Content pipeline | Writing |
| `platinum-designer` | Video storyboard design | Video |
| `platinum-renderer` | Video rendering (PIL) | Video |
| `factory-pipeline` | Video production pipeline | Video |
| `deep-analysis` | Data analysis | Analytics |

## Skills Needed

| Skill | Priority | Purpose |
|-------|----------|---------|
| `research-object-creator` | High | Automate RO creation from source |
| `essay-object-creator` | High | Combine ROs into EOs |
| `hypothesis-engine` | High | Perpetual question generation |
| `source-metaphysics` | Medium | Truth map maintenance |
| `dataset-acquire` | Medium | OpenNeuro S3 dataset downloads |

## Invocation Pattern

```bash
# One-shot (Zeus mode)
hermes -z "Create an RO from the source material at path X" --skills research-object-creator -m "deepseek-v4-flash"

# Cron job (hypothesis engine)
hermes -z "Run the hypothesis engine scan and propose new EOs" --skills hypothesis-engine -m "deepseek-v4-flash"

# Pipeline (video production)
hermes -z "Take EO eo:iccha-jnana-kriya and produce a video" --skills platinum-designer,platinum-renderer -m "deepseek-v4-flash"
```

## System Flow

```
[CRON] Hypothesis Engine runs daily
  → Scans source metaphysics for underdetermined questions
  → Generates EO proposals
  → Writes to content/hypothesis-engine/proposals/

[AGENT] Research cycle (daily)
  → Check for new EO proposals
  → Review and approve
  → Research Factory creates/updates ROs
  → Writing Factory produces papers
  → Video Factory produces videos
  → Analytics Factory measures results
  → Source Metaphysics updated

[CRON] Source Metaphysics audit (weekly)
  → Check all questions for staleness
  → Flag outdated entries for review
  → Identify new tension points from RO disagreements
```

## Hermes Config

Provider: `opencode-go`
Model: `deepseek-v4-flash`
Base URL: `https://opencode.ai/zen/go/v1`

The API key is stored in `~/.hermes/.env` as `OPENCODE_GO_API_KEY`. Auth configuration is in `~/.hermes/auth.json`.

## MCP Servers

Hermes connects to MCP servers for external tools:

- `cloudflare-docs` — Cloudflare API access
- `fablecut` — Video compilation
- Blog factory MCP (`mcp-server.py`) — Job creation, advancement, state tracking
