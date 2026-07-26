# For Codex — Setup & Workflow Guide

## Overview

Codex is the premium writing model (GPT-5.6). DeepSeek v4 Flash is the workhorse for everything else. This file tells Codex how to connect to the stack and where to apply itself.

## Model Strategy

| Task | Model | Why |
|------|-------|-----|
| PIL/GLSL shader writing | **Codex (GPT-5.6)** | Better at complex code generation |
| Essay writing (long-form) | **Codex (GPT-5.6)** | Better prose, structure, coherence |
| RO/EO creation | **DeepSeek v4 Flash** | Fast, cheap, good enough |
| Research acquisition | **DeepSeek v4 Flash** | High volume, structured output |
| Shader/frame review | **Codex (GPT-5.6)** | Needs visual reasoning |
| Hermes skill execution | **DeepSeek v4 Flash** | Already optimized for this |
| Feedback response | **Codex (GPT-5.6) + DeepSeek** | Codex writes the fix, DeepSeek re-renders |
| Translation (Sanskrit) | **DeepSeek v4 Flash** | Proven 7-pass pipeline works |
| Feed algorithm queries | **No LLM** | Use trained weight graph (GeometricEngine) |

**Rule:** Codex writes the first high-quality version. DeepSeek handles iteration, volume, and automation. Codex seeds the corpus; DeepSeek scales it.

---

## 1. GitHub Access via Sites

Codex Sites connects directly to your GitHub repos. Add these:

| Repo | Purpose |
|------|---------|
| `prx0r/clean` | Research nucleus — truth map, specs, skills, directives |
| `prx0r/GoodGrails_Pipeline` | Bookstore ingestion pipeline (reference for Cloudflare patterns) |
| `prx0r/geometricengine` | Graph-native recommendation engine (reference for feed algorithm) |
| Also in the VPS at `/root/projects/`: `blog`, `tantraloka`, `anakhra-hub`, `FableCut` |

**Sites workflow:**
```
Codex → Sites → open prx0r/clean
  → edit RESEARCH_DIRECTIVE.md
  → edit magnum-opus/15-GREENSCREEN.md
  → commit → push
  → pull on VPS: cd /root/projects/clean && git pull
```

---

## 2. MCP Connection to Cloudflare & VPS

Codex connects to MCP servers for infrastructure access. Register these:

### MCP Server: Cloudflare Factory
```json
{
  "mcpServers": {
    "cloudflare-factory": {
      "command": "node",
      "args": ["/root/projects/blog/factory/cloudflare/src/mcp-server.js"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "your_token",
        "CLOUDFLARE_ACCOUNT_ID": "954612afb5a97bb15dddcdc70176813d"
      }
    }
  }
}
```

**Tools exposed:**
- `factory_status` — check pipeline state
- `factory_create_job` — start new production job
- `factory_advance` — advance job to next stage
- D1 query access
- R2 file read/write

### MCP Server: Anakhra Render
Connect to `studio.tantrafiles.xyz` API via MCP:
```json
{
  "mcpServers": {
    "anakhra": {
      "command": "node",
      "args": ["/root/projects/anakhra-hub/mcp-server.js"]
    }
  }
}
```

**Tools exposed:**
- `render_preview` — render single scene at preview quality
- `render_adjust` — change param, re-render
- `render_approve` — mark scene approved
- `render_full` — render all approved scenes at full quality
- `feedback_poll` — check for unresolved user feedback

### MCP Server: Hermes
```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp"]
    }
  }
}
```

**Tools exposed:**
- `hermes_acquire` — download paper
- `hermes_render_review` — poll feedback, adjust shader, re-render
- `hermes_hypothesis_scan` — run hypothesis engine
- `hermes_truth_map_update` — update evidence weights

---

## 3. Cloudflare Access (Browser/Dashboard)

For Cloudflare management that needs a browser:

**Dashboard:** https://dash.cloudflare.com (login with account email)
**Workers & Pages:** Dashboard → Workers & Pages
**D1:** Dashboard → D1
**R2:** Dashboard → R2
**AI Gateway:** Dashboard → AI Gateway

**Key resources already deployed:**
- `studio.tantrafiles.xyz` — Cloudflare Pages site (anakhra-hub)
- `tantrafiles.xyz` — main site
- D1: `anakhra-feedback` (anakhra-hub), `tantra-feedback` (studio)
- R2: `anakhra-renders`, `blog-video-assets`, `factory-assets`

**To create new Cloudflare resources via Codex:**
Codex doesn't natively manage Cloudflare infrastructure. Use the terminal:
```bash
npx wrangler d1 create new-database
npx wrangler r2 bucket create new-bucket
npx wrangler pages deploy ./public --project-name my-project
```

---

## 4. Writing Workflow (Codex Does the Premium Work)

### PIL/GLSL Shader Writing

Codex writes the first version of complex shaders and PIL scene functions. DeepSeek handles iteration and tweaks.

```
Codex: Write a GLSL shader that visualizes the 36 tattvas as a descending ladder of consciousness
  → Creates form_tattvas.glsl
  → Tests with glslViewer
  → Commits to repo
  → DeepSeek handles feedback: "make the glow warmer" → adjusts uniform values
```

### Essay Writing (Long-Form)

Codex writes the premium long-form essays for the website and video scripts. DeepSeek handles the high-volume RO-to-essay pipeline.

```
Codex: Write a 3000-word essay on "The Kañcukas as a Theory of Bounded Cognition"
  → Reads relevant ROs
  → Produces polished essay with quote budget (final pass ≤20% source)
  → Commits to content/essays/
  → DeepSeek uses this as seed for related short-form content
```

### Code Review

Codex reviews PIL/GLSL code before rendering. DeepSeek reviews research extraction and data pipelines.

---

## 5. File System Access (VPS)

Codex can't directly access the VPS file system unless connected via:
- **Sites** → GitHub repos (clean, geometricengine, GoodGrails)
- **MCP** → custom MCP server that proxies file access
- **Terminal** → SSH into the VPS

For files outside GitHub repos (tantraloka goldrender packs, blog content), use terminal:
```bash
# Read a file
cat /root/projects/tantraloka/goldrender/time_is_produced_by_forgetting_platinum.py

# Edit via sed or by pulling the repo
# The goldrender packs are in the tantraloka project which may or may not have git
```

---

## 6. Quick Reference

### Essential Commands

```bash
# Deploy anakhra studio
cd /root/projects/anakhra-hub && npx wrangler pages deploy public --project-name anakhra

# Run hypothesis engine
hermes -z "Scan truth map for underdetermined questions and propose new EOs" --skills hypothesis-engine -m "deepseek-v4-flash"

# Poll feedback and respond
hermes -z "Poll for unresolved feedback and respond to all items" --skills render-review -m "deepseek-v4-flash"

# Render a pack
cd /root/projects/tantraloka/goldrender && python3 batch_render.py --pack time_is_produced_by_forgetting --full

# Query D1
npx wrangler d1 execute anakhra-feedback --command "SELECT * FROM feedback WHERE resolved = 0"

# Check studio queue
curl https://studio.tantrafiles.xyz/api/packs
```

### Key Directories

```
/root/projects/clean/                    # Research nucleus (truth map, specs, skills)
/root/projects/tantraloka/goldrender/    # PIL/GLSL render packs (99 packs)
/root/projects/tantraloka/moderngl/      # GLSL shaders (17 shaders)
/root/projects/blog/                     # Blog project (ROs, essays, content)
/root/projects/blog/hermes/skills/       # All Hermes skills
/root/projects/anakhra-hub/              # Studio dashboard (Cloudflare Pages)
/root/projects/FableCut/                 # Browser video editor
```

### MCP Server Reference

The Cloudflare factory MCP server is at:
`/root/projects/blog/factory/cloudflare/src/mcp-server.py`

It exposes tools for the video pipeline. The source file has the full tool list. When connected via MCP, Codex can call these directly without terminal.
