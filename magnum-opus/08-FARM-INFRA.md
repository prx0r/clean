# 08 — Farm Infrastructure

The deployment layer. Cloudflare Workers + D1 + R2 + Queues, parameterized by FARM_ID.

## Architecture

```
FARM (one per niche, e.g. "tantra")
  ├── Worker (Cloudflare, edge)
  │   ├── D1 Database (research data, hypotheses, performance)
  │   ├── R2 Bucket (assets, private)
  │   ├── Queue (pipeline decoupling)
  │   └── Cron triggers (daily/weekly/monthly)
  └── Hermes (VPS, orchestrator)
      ├── HTTPS → Worker API
      └── MCP → Factory tools
```

## Current State

The `farm-template/` in the blog project has:
- Worker with D1 schema
- R2 bucket setup
- Queue definitions
- Cron trigger config
- `create-farm.sh` script

**Never deployed.** Needs YouTube API client written and wrangler deploy run.

## Resource Naming

All resources prefixed by FARM_ID:

```
farm-{farm_id}-db        (D1)
farm-{farm_id}-assets    (R2)
farm-{farm_id}-queue     (Queue)
farm-{farm_id}-worker    (Worker)
```

## Farm Responsibilities

1. **Research** — Daily source harvesting, gap analysis, hypothesis tracking
2. **Production** — Video pipeline orchestration
3. **Analytics** — Performance tracking, truth map updates
4. **Intelligence** — YouTube API, Reddit extraction, trend detection

## Deployment

```bash
export FARM_ID="tantra"
npx wrangler d1 create farm-${FARM_ID}-db
npx wrangler r2 bucket create farm-${FARM_ID}-assets
# ... deploy worker
```

See `blog/farm-template/docs/01-SETUP.md` for full deployment guide.

## Relationship to Factories

The Farm is the **infrastructure layer**. The Factories are the **logic layer**.

```
FACTORIES (logic)      FARMS (infrastructure)
  Research Factory   →  farm-{id} research pipeline
  Writing Factory    →  (runs on VPS via Hermes)
  Video Factory      →  farm-{id} production pipeline
  Analytics Factory   →  farm-{id} analytics pipeline
```

One farm can support multiple factories. One factory can span multiple farms (e.g., research factory across all niches).
