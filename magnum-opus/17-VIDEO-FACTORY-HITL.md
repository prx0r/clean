# Video Factory HITL — Human-in-the-Loop Review System

## The Problem

Current workflow: batch render → watch → tell agent what to change → re-render → repeat. Blind iteration takes ages because there's no way to preview individual scenes, flag specific issues, or iterate granularly.

## The Solution: Dashboard + FableCut + Voicebox

Three tools already exist that together solve this. They just aren't wired together yet.

### 1. Dashboard (exists, needs expansion)

Flask app at `/root/projects/blog/dashboard/server.py`. Currently shows factory jobs, research data, FableCut status. Needs:

- **Render queue** — list of packs/scenes waiting for review
- **Scene preview** — inline video player per scene
- **Comment system** — click a frame, leave a note for the agent
- **Iteration log** — every change logged so agents learn preferences
- **Publish button** — approve → auto-assemble → upload

### 2. FableCut (exists, actively used)

Browser-based non-linear editor at `/root/projects/FableCut/`. Has MCP tools (`fablecut_status`, `fablecut_get_project`, `fablecut_patch_project`, `fablecut_import_media`). AI agent can edit `project.json` and the browser live-reloads within 150ms.

This IS the timeline editor for final assembly. The flow:

```
Scenes rendered (PIL/GLSL) → Imported as media into FableCut
→ Agent arranges timeline → User reviews in browser
→ Agent adjusts based on feedback → Export
```

### 3. Voicebox (new — Qwen3-TTS voice cloning)

Open-source desktop app at `github.com/jamiepine/voicebox`. MIT license. Features:
- Clone voices from seconds of audio via Qwen3-TTS
- Multi-track DAW timeline for composing conversations/podcasts
- REST API for integration
- Everything local, private, offline

For our pipeline: clone a bespoke voice for narration (Attenborough/Fry gravitas), generate TTS via the API, import into FableCut as audio tracks.

### 4. Vast AI GPU

Rent GPU boxes on demand ($0.20-0.40/hr) for:
- GLSL shader rendering (moderngl needs NVIDIA GPU with EGL)
- Voice cloning inference
- Heavy compositing

MCP integration: spin up GPU box → render → transfer output → shut down. Only pay for compute when actively rendering.

---

## The HITL Workflow

```
Agent creates/edits pack
  → Renders preview frames (low-res, quick)
  → Dashboard shows: [Scene 1] [Scene 2] [Scene 3] ...
  → User clicks a scene → watches it → leaves feedback
     "Make the glow warmer. Slow the transition by 1s."
  → Agent reads feedback → adjusts shader/PIL code → re-renders just that scene
  → User reviews again → approve or iterate
  → Approved scenes → FableCut timeline (agent assembles)
  → User reviews full timeline in FableCut browser
  → Adjusts transitions, music, timing in UI
  → Agent logs every decision → trains on preferences
  → Export → Upload → Publish
```

## Feedback Loop

Every user iteration is logged:
```
{
  "scene_id": "time_forgetting_07",
  "original_shader": "width.glsl", 
  "user_comments": ["glow too warm", "transition too fast"],
  "agent_changes": ["reduced glow.r by 0.15", "increased transition_duration to 2.0s"],
  "approved": true,
  "timestamp": "2026-07-26T12:00:00Z"
}
```

Over time, the agent learns:
- Preferred color palettes (you always cool down glow after first review)
- Tempo preferences (you consistently slow transitions in philosophical sections)
- Music pairings (you tend to choose ambient over rhythmic for contemplative content)
- Narration style (you prefer longer pauses between concepts)

## What to Build

### Immediate (Week 1-2)
- [ ] Expand dashboard with render queue view
- [ ] Add scene video preview to dashboard (serve from local MP4s)
- [ ] Add comment/feedback form per scene
- [ ] Wire agent to read feedback and adjust packs

### Short-term (Month 1-2)
- [ ] FableCut integration: pack scenes → auto-timeline → user review
- [ ] Voicebox integration: clone voice → generate TTS → import to FableCut
- [ ] Vast GPU MCP: spin up → render → transfer → shut down
- [ ] Feedback logging system

### Medium-term (Month 3-6)
- [ ] Preference training: agent refines based on logged decisions
- [ ] Auto-music selection: agent learns your taste and proposes tracks
- [ ] Full publish pipeline: review → approve → assemble → upload → done
- [ ] Multi-voice dialogue: clone multiple voices for conversational formats

## Architecture

```
User (reviewer)
  │
  ├── Dashboard (Flask) — review queue, scene previews, comments
  │     └── Feedback DB (D1/SQLite) — every iteration logged
  │
  ├── Agent (Hermes) — reads feedback, adjusts packs, re-renders
  │     ├── GLSL shaders → GPU (Vast AI)
  │     ├── PIL packs → CPU (local)
  │     └── Voicebox API → TTS (local or GPU)
  │
  ├── FableCut (browser editor) — timeline assembly, transitions, export
  │     └── MCP tools → agent edits timeline
  │
  └── Vast GPU (on-demand) — GLSL rendering, heavy compute
        └── MCP → spin up/down per render job
```

## Existing Assets

| Component | Location | Status |
|-----------|----------|--------|
| Dashboard | `/root/projects/blog/dashboard/` | Partial — basic views exist |
| FableCut | `/root/projects/FableCut/` | Active — MCP tools work |
| GLSL shaders (17) | `/root/projects/tantraloka/moderngl/shaders/` | Ported, untested on GPU |
| PIL packs (99) | `/root/projects/tantraloka/goldrender/` | Active — 11 rendered |
| Render harness | `/root/projects/tantraloka/moderngl/render_harness.py` | Active — EGL + HDR |
| Voicebox | `github.com/jamiepine/voicebox` | External — MIT license |
| Deepdive videos (76) | `/root/projects/tantraloka/videos-from-deepdives/` | Published |
| FableCut publish skill | `/root/projects/blog/hermes/skills/publish-video-fablecut/` | Active |
