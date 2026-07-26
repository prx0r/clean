# Anakhra Render — Full Pipeline Spec

## The Dream

User loads an AI-built pack. Watches the video. Pauses at any timestamp. Says "make this glow warmer" or "slow the transition." The agent adjusts the code and re-renders that single scene while the user keeps watching. By the end of the video, 7 frames are flagged with proposed changes. User clicks through them, sees side-by-side before/after, approves or iterates. Each version saved. Timeline assembly at the end.

## What Already Exists (Do Not Rebuild)

### 1. studio.tantrafiles.xyz — Video Review Dashboard ✅

**Location:** `/root/projects/tantrafiles-hub/` — deployed on Cloudflare Pages + Workers + D1 + R2

**Already has:**
- Video list from R2 index
- HTML5 video player with controls
- Comments per video with star ratings
- Author name, timestamps
- Status tracking (draft/review/approved)
- R2 video serving via signed URLs
- D1 for feedback storage

**What it's missing (add, don't rebuild):**
- Timestamp capture on pause (HTML5 video `currentTime`)
- Scene-level feedback (not just video-level comments)
- Side-by-side version comparison
- Agent response display ("agent changed X because Y")
- Parameter sliders for live shader tweaking

### 2. FableCut — Timeline Editor ✅

**Location:** `/root/projects/FableCut/` — runs on VPS at port 7777

**Already has:**
- Browser-based non-linear timeline (Premiere-style)
- 7 tracks (4 video + 3 audio)
- Transitions, filters, keyframes
- MCP tools: `fablecut_get_project`, `fablecut_patch_project`, `fablecut_import_media`
- Project.json editing with live reload (~150ms)
- REST API for agent integration
- Export via ffmpeg
- Token-efficient editing (compact mode, patch ops)

**What it's missing:**
- Integration with our pack pipeline (FableCut was abandoned because packs now render one-shot)
- Actually, FableCut becomes the **final assembly timeline** — after scenes are approved individually, FableCut arranges them, adds transitions, music, exports final MP4

### 3. Goldrender — Pack Pipeline ✅

**Location:** `/root/projects/tantraloka/goldrender/` + `moderngl/`

**Already has:**
- 99 pack scripts (PIL + GLSL)
- `batch_render.py` orchestrator
- Scene-by-scene rendering with individual MP4 output
- Audio analysis (librosa) for reactive visuals
- Narration timeline JSON export
- GLSL shader pipeline (17 shaders, GPU-ready)
- LYGIA shader library integrated
- Preview mode (4 stills per scene)

### 4. Cloudflare Factory Plan ✅

**Location:** `/root/projects/blog/operations/cloudflare-factory-plan.md`

**Already designed:**
- Workers API for job queue
- D1 for state + feedback
- R2 for video storage
- Queues for async render dispatch
- Vectorize for scene similarity search
- Workers AI for FLUX, LLaVA, Whisper, BGE

---

## The Integrated Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER (reviewer)                           │
│                                                                  │
│  Opens studio.tantrafiles.xyz → sees queue of rendered packs    │
│  Clicks a pack → video plays in browser                         │
│  Pauses at timestamp → feedback panel opens                     │
│  Types: "make the glow warmer" → submits                        │
│                                                                  │
│  Feedback goes to D1 → agent picks it up                        │
│  Agent finds the scene → adjusts shader param                   │
│  Re-renders single scene → uploads new version to R2            │
│  Studio shows: "scene updated" with before/after comparison     │
│                                                                  │
│  User reviews the change → approves or iterates                 │
│  Each version saved in D1 with shader params logged             │
│  Approved scenes → FableCut timeline → final export → publish   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
┌─────────────────────┐     ┌──────────────────────────────────────┐
│   User (browser)    │     │          Cloudflare Edge              │
│                     │     │                                      │
│  studio.tantrafiles │────→│  Workers API                         │
│  .xyz               │     │    ├── GET /api/videos              │
│                     │     │    ├── GET /api/videos/:id          │
│  ─ Video player     │     │    ├── POST /api/videos/:id/feedback │
│  ─ Comments         │     │    ├── POST /api/render              │
│  ─ Parameter UI     │     │    └── POST /api/agent              │
│  ─ Version browser  │     │                                      │
│  ─ Timeline (Fable) │     │  D1 (feedback, state, versions)      │
│                     │     │  R2 (videos, scenes, shader params)  │
└─────────────────────┘     └──────────────┬───────────────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │     Agent (Hermes)       │
                              │                          │
                              │  Reads feedback from D1  │
                              │  Edits pack/shader code  │
                              │  Re-renders single scene │
                              │  Uploads to R2           │
                              │  Updates D1 status       │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │     Render GPU (Vast)    │
                              │                          │
                              │  GLSL shader rendering   │
                              │  PIL text/title overlay   │
                              │  ffmpeg assembly          │
                              │  Upload to R2             │
                              └──────────────────────────┘
```

---

## Database Schema (D1)

```sql
-- Packs (one per video)
CREATE TABLE packs (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT DEFAULT 'draft', -- draft, preview, review, approved, published
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  agent_id TEXT,
  essay_source TEXT,
  duration_seconds REAL
);

-- Scenes within a pack
CREATE TABLE scenes (
  id TEXT PRIMARY KEY,
  pack_id TEXT NOT NULL,
  scene_number INTEGER NOT NULL,
  title TEXT,
  visual_mode TEXT,
  shader_file TEXT,
  duration_seconds REAL,
  status TEXT DEFAULT 'pending', -- pending, reviewed, approved, rejected
  render_version INTEGER DEFAULT 0,
  FOREIGN KEY (pack_id) REFERENCES packs(id)
);

-- Feedback on scenes (user comments at timestamps)
CREATE TABLE feedback (
  id TEXT PRIMARY KEY,
  scene_id TEXT NOT NULL,
  user_id TEXT,
  comment TEXT NOT NULL,
  rating INTEGER,
  timestamp_seconds REAL,        -- where in the video
  agent_response TEXT,            -- what the agent did
  change_summary TEXT,            -- "adjusted glow.r from 0.6 to 0.4"
  resolved INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  resolved_at TEXT,
  FOREIGN KEY (scene_id) REFERENCES scenes(id)
);

-- Render versions (each re-render creates a new version)
CREATE TABLE render_versions (
  id TEXT PRIMARY KEY,
  scene_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  shader_params TEXT,            -- JSON of all params at this version
  r2_key TEXT,                   -- video file in R2
  render_time_seconds REAL,
  agent_notes TEXT,              -- why this version was created
  user_approved INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (scene_id) REFERENCES scenes(id)
);

-- Agent action log (for preference learning)
CREATE TABLE agent_actions (
  id TEXT PRIMARY KEY,
  feedback_id TEXT,
  action_type TEXT,              -- adjust_shader, re_render, change_param
  param_name TEXT,
  old_value TEXT,
  new_value TEXT,
  reasoning TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (feedback_id) REFERENCES feedback(id)
);
```

---

## API Endpoints

### Existing (in studio.tantrafiles.xyz)

```
GET  /api/videos              — list all packs
GET  /api/videos/:id          — pack details + scenes + feedback
POST /api/videos/:id/comments — add feedback (needs timestamp field added)
```

### New Endpoints

```
POST /api/render              — trigger render of specific scene(s)
  Body: { pack_id, scene_ids[], mode: "preview"|"final" }
  Response: { job_id, status }

GET  /api/render/:job_id      — check render status
  Response: { status, r2_key, version }

POST /api/scenes/:id/versions — create new version of a scene
  Body: { shader_params{}, agent_notes }
  Response: { version_id, r2_key }

GET  /api/scenes/:id/versions — list all versions of a scene
  Response: [{ version, r2_key, params, approved, created_at }]

POST /api/agent/respond       — agent posts response to feedback
  Body: { feedback_id, agent_response, change_summary }
  Response: { ok }

GET  /api/packs/:id/timeline  — get FableCut-compatible timeline JSON
  Response: { media[], clips[], tracks[] }
```

---

## Studio UI Enhancements

### What to Add to studio.tantrafiles.xyz

**1. Timestamp Capture**
```javascript
// Already in HTML5 video API — just need to wire it
player.addEventListener('pause', () => {
  const ts = player.currentTime;
  // Open feedback form with timestamp pre-filled
  document.getElementById('feedbackTimestamp').value = ts;
  // Highlight in timeline
  highlightTimelinePosition(ts);
});
```

**2. Scene List (sidebar)**
Replace "loading videos" with actual scene breakdown:
```
Pack: Time is Produced by Forgetting
├── Scene 1: Opening (approved)          ★★★★☆
├── Scene 2: Contraction (needs review)  ★★★☆☆  ← YOU ARE HERE
├── Scene 3: Sequence (rendering...)     🔄
├── Scene 4: Memory (approved)          ★★★★★
└── Scene 5: Recognition (pending)      —
```
Click any scene → jump to that timestamp. Status badges: pending, rendering, needs_review, approved.

**3. Feedback Form with Timestamp**
```
Timestamp: 00:01:23 (auto-captured on pause)
Rating: ★★★★☆
Comment: "The glow transition feels too abrupt. Can we smooth it?"
[Submit] — agent will pick this up and modify the shader
```

**4. Agent Response Panel**
```
Your feedback: "glow transition too abrupt"
Agent response: "Reduced glow intensity ramp from 0.3 to 1.2s.
                 Changed ease function from linear to easeInOutCubic.
                 New scene version rendered."
[Play Updated Scene] [Compare Side-by-Side] [Approve] [Iterate]
```

**5. Version Browser**
```
Scene 3 — Version History
v1 (draft)    ⬤━━━━━━━━━━━  original
v2 (feedback) ⬤━━━━━━━━━━━  smoother glow (current)
v3 (feedback) ⬤━━━━━━━━━━━  warmer color temp
```
Click any version → plays that version. Side-by-side compare between any two.

**6. Timeline View (FableCut Integration)**
Bottom panel shows FableCut-style timeline with:
- Waveform audio track
- Video track with scene thumbnails
- Transitions between scenes
- User markers (timestamp feedback shown as flags)
- Agent processing indicators

---

## Feedback → Agent → Re-render Loop

### Detailed Flow

```
1. User pauses video at 00:01:23
2. Browser captures: { scene_id: "scene_3", timestamp: 83.0 }
3. User types: "the glow transition feels too abrupt"
4. POST /api/videos/:id/feedback { scene_id, timestamp, comment, rating }
5. D1 stores feedback
6. Agent (Hermes) polls D1 for unresolved feedback (or webhook push)
7. Agent reads feedback + current scene shader params from D1
8. Agent identifies: "u_audioVolume ramp is 0.0→1.0 over 0.3s. User wants smoother."
9. Agent edits shader: `float rampTime = 1.2; float ramp = easeInOutCubic(min(1.0, u / rampTime));`
10. Agent triggers re-render of single scene on GPU
11. New MP4 uploaded to R2 with new version number
12. D1 updated: new render_version row, agent_notes, change_summary
13. Studio polls for update → shows notification: "Scene 3 updated"
14. User sees before/after comparison → approves or iterates
```

### Timeline Integration

After all scenes are approved:
```
15. Agent queries: GET /api/packs/:id/timeline
16. Returns FableCut-compatible JSON with approved scenes
17. Agent calls fablecut_set_project → loads into FableCut
18. User opens FableCut in browser → sees full timeline
19. Can tweak transitions, add music, adjust timing
20. Export from FableCut → final MP4 → publish
```

---

## Shader Parameter Schema

Each scene exposes its tweakable parameters via JSON schema:

```json
{
  "scene_id": "scene_3",
  "shader": "classical_wall.glsl",
  "params": {
    "glow_intensity": {
      "type": "float",
      "default": 0.6,
      "min": 0.0,
      "max": 2.0,
      "description": "Brightness of additive glow"
    },
    "glow_warmth": {
      "type": "float",
      "default": 0.5,
      "min": 0.0,
      "max": 1.0,
      "description": "0=cool white, 1=warm gold"
    },
    "transition_speed": {
      "type": "float",
      "default": 0.3,
      "min": 0.1,
      "max": 3.0,
      "description": "Seconds for glow to reach full intensity"
    },
    "easing_function": {
      "type": "enum",
      "default": "linear",
      "options": ["linear", "easeInOutCubic", "easeOutCubic", "easeInCubic"],
      "description": "Animation curve for transitions"
    },
    "pulse_audio_reactive": {
      "type": "float",
      "default": 0.5,
      "min": 0.0,
      "max": 1.0,
      "description": "How much audio volume affects pulse radius"
    }
  }
}
```

The agent reads this schema and builds a UI from it (range sliders, dropdowns, checkboxes). When the user tweaks a slider, the agent adjusts the uniform value and re-renders.

---

## Tools to Use (Not Rebuild)

| Need | Tool | Why |
|------|------|-----|
| Review dashboard | `studio.tantrafiles.xyz` | Already deployed, just needs timestamp + scene features |
| Timeline editor | `FableCut` | Browser-based, MCP tools, live reload, MIT license |
| Shader live preview | `glslViewer` | CLI tool, hot-reload on file change, GPU rendering |
| Audio analysis | `librosa` | Already integrated in render pipeline |
| Voice cloning | `Voicebox` (Qwen3-TTS) | Desktop app, REST API, multi-track timeline |
| GPU rendering | `moderngl` + `vast.ai` | Headless EGL, on-demand GPU boxes |
| Shader library | `lygia` | Already integrated, 500+ functions |
| Web shader editor | `glsl.app` | Prototyping shaders in browser |
| Vector search | `Cloudflare Vectorize` | Scene similarity, art matching |
| Image gen | `Workers AI FLUX` | Storyboard concept art |
| Queue | `Cloudflare Queues` | Async render job dispatch |
| Storage | `Cloudflare R2` | Video + asset storage, zero egress |

---

## Build Order

### Week 1: Review Loop
- [ ] Add timestamp capture to studio on video pause
- [ ] Add scene list sidebar
- [ ] Add feedback form with timestamp
- [ ] Wire feedback POST to D1
- [ ] Agent polls D1 for feedback → makes change → re-renders → uploads

### Week 2: Version + Compare
- [ ] Render versions table in D1
- [ ] Version browser UI in studio
- [ ] Side-by-side comparison of two versions
- [ ] Approve/reject buttons

### Week 3: FableCut Integration
- [ ] Scene → FableCut timeline export
- [ ] Agent calls fablecut_set_project with approved scenes
- [ ] User reviews timeline in FableCut
- [ ] Final export from FableCut

### Week 4: Parameter UI + Polish
- [ ] Shader parameter schema → auto-generated UI sliders
- [ ] Live tweaking: slider → agent updates uniform → re-render
- [ ] Agent action logging for preference learning
- [ ] GPU box MCP for on-demand rendering

---

## The Golden Path (Happiest Workflow)

1. Hermes agent writes a pack: `time_is_produced_by_forgetting_platinum.py`
2. Agent renders preview → uploads to R2 → creates pack record in D1
3. Studio shows: "New pack ready for review: Time is Produced by Forgetting"
4. User opens studio, watches video
5. At 0:23, pauses: "The glow transition is too abrupt"
6. Submits feedback with 4-star rating
7. Agent sees feedback, identifies param, adjusts shader
8. Re-renders just that scene (~30 seconds on GPU)
9. Studio shows notification: "Scene updated"
10. User compares before/after → approves
11. Repeats for 6 more scenes
12. Agent assembles approved scenes into FableCut timeline
13. User opens FableCut, adds music, tweaks transitions
14. Exports final MP4 → uploaded to YouTube + R2
15. Pipeline complete. User spent 20 minutes reviewing, not 4 hours rendering blind.
