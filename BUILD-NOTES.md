# Build Notes — Pipeline Evolution & Lessons Learned

Through 2026-07-26. Everything that was tried, what worked, what didn't, and why.

---

## Stack Evolution (3 Generations)

### Gen 1: Hermes Skills (Manual Agent Workflow)

**What:** `hermes/skills/platinum-designer/SKILL.md` (210 lines) + `platinum-renderer/SKILL.md` (206 lines).

Two hand-crafted agent prompts:
- **Platinum Designer (PASS 1):** Read essay → study 6 gold packs → write agentvision.md → design visual thesis → build per-shot storyboard with `visual_audio_alignment` + `no_narration_test`. Output: planning pack (5 files). NO code. NO rendering.
- **Platinum Renderer (PASS 2):** Receive planning pack → Zeus comparative analysis against gold packs → review each shot (4 quality gates) → write custom PIL scene functions per unique visual mode → render frames → assemble with ffmpeg → produce alignment report + contact sheet + changelog.

**What worked:** Deep creative quality. The no-narration test forced real visual thinking. The gold pack study prevented generic motifs.

**What didn't:** Entirely agent-driven, no automation, slow per-video (hours of agent time), inconsistent output quality depending on LLM state.

**Key insight:** The `visual_audio_alignment.why_this_visual_matches` field was the most important innovation — forces the agent to explain WHY the visual enacts the transformation, not just describe what it looks like.

### Gen 2: Controller.js (Cloudflare Worker Pipeline)

**What:** `factory/cloudflare/src/controller.js` (1012 lines). A state-machine Cloudflare Worker with 12 stages, D1 persistence, R2 artifact storage, MCP server, and a VPS render worker.

**Architecture:**
- 12 stages: pack_setup → gold_study → rhetorical_map → visual_thesis → motif_manufacturability → storyboard → storyboard_review → pack_composition → code_review → draft_render → visual_qc → final_render
- Stages 1-9 run on Cloudflare Worker via Workers AI (qwen3-30b, llama-3.3-70b)
- Stages 10-12 create D1 render tasks for VPS to claim and execute
- Inline GOLD_BIBLE (31 lines) replacing the gold_study LLM call — hardcoded material grammar, spatial grammar, motion verbs, color semantics, continuity patterns, quality tests
- Validation config with per-stage rules (motif minimum score, shot duration bounds, composition repeat limits)
- D1 schema with 13 tables (jobs, job_artifacts, render_tasks, etc.)
- MCP server with 11 tools for external agents (ChatGPT, Claude)

**What worked:** Infrastructure was solid. Job creation, D1 state persistence, R2 artifact loading, render task claim system (atomic UPDATE with heartbeat), video serving endpoint. 9/9 LLM stages ran reliably (~3 min, ~$0.002).

**What didn't:** 
- LLM generated static images, not animations — code_review prompt produced single-frame PIL instead of multi-frame with ffmpeg
- VPS worker never ran autonomously — needed systemd service, never deployed
- D1 claim SQL had a bug (conditional UPDATE subquery didn't return claimed rows)
- No real film produced — only smoke test (4-second, 3-shot clip)
- Stages 10-12 were placeholders: draft_render ran LLM instead of dispatching to VPS, visual_qc had no vision model, final_render was stub
- 1012 lines of JavaScript for a pipeline that never produced a real video

**Key insight from the autopsy (factory/analysis/platinum-master-autopsy.md):**
1. Chapter batching — don't generate all shots in one LLM call
2. Artifact grounding — load actual content into prompts, not file paths
3. Fail closed — validate before advancing, never mark failed stages as passed
4. Immutable artifacts — versioned R2 objects with sha256, never overwrite
5. Freeze renderer runtime — LLM generates only scene functions, not animation infrastructure

### Gen 3: ChatGPT Prompt (Current)

**What:** A single prompt to ChatGPT/Codex that outperformed the entire controller.js pipeline.

**Why it won:** The controller.js spent 1012 lines on infrastructure, state machines, validation gates, D1 operations, artifact loading, MCP tools — but the actual creative work (designing visuals, writing scene code, animating) was still done by an LLM. The infrastructure added complexity without improving output quality. A well-crafted prompt given directly to a capable model skipped all the machinery and produced better results in less time.

**Lesson:** Pipeline infrastructure doesn't improve LLM output quality. It only adds orchestration overhead. Invest in prompt quality, not pipeline complexity.

---

## Current Architecture (2026-07-26)

```
Blog Project (operational)              Clean Project (research nucleus)
├── 111 platinum packs                   ├── magnum-opus/ (26 spec files)
├── 160 ROs                              ├── specs/ (RO, EO, CLAIM, etc.)
├── 1798 essays                          ├── truthengine* (propagation math)
├── 904 art metadata                     ├── beautify/ (GLSL task pack)
├── 152 SVGs                             └── dev25.md (Codex handover)
├── Factory infra (Worker, D1, R2, MCP)
├── Hermes skills (17 working)
├── Essaygen V7 algorithm
├── YouNiverse pipeline (72.9M videos)
├── Truth map seed (6 questions)
└── Visionary renderer (Skia, Phase 1)
```

**Active services:** Hermes Gateway (Telegram), FableCut (port 7777), Thumbnail Server (port 8765), Cron: video-pipeline (every 6h), cron-acquire (daily).

**Codex currently working on:** Truth map validation — propagation engine tests, D1 adapter, evidence flow.

---

## Key Files Created This Session

| File | Lines | What |
|------|-------|------|
| `clean/specs/RO.md` | 326 | Research Object granular spec |
| `clean/specs/EO.md` | 302 | Essay Object granular spec (+ Codex review) |
| `clean/specs/TRUTH-MAP-QUESTION.md` | 288 | Truth map question spec (+ Codex review) |
| `clean/specs/CLAIM.md` | 327 | Claim atomic evidence spec (+ Codex review) |
| `clean/specs/DB-INTEGRATION.md` | 266 | D1 adapter design (+ Codex review) |
| `clean/specs/HYPOTHESIS-ENGINE.md` | 322 | Hypothesis engine spec (+ Codex review) |
| `clean/dev25.md` | 135 | Codex handover doc |
| `clean/ONBOARDING.md` | — | Agent entry point |
| `clean/GRANULAR-SPEC.md` | — | Component spec directive |
| `clean/beautify/` | 5 packs | GLSL beautification task folder |

---

## Hardest Lessons Learned

1. **The EO gap is real.** Zero Essay Objects exist 18 months in. The entire architecture hinges on them. FLAWS.md #1 risk confirmed.
2. **Controller.js was over-engineered.** 1012 lines of pipeline infrastructure outperformed by a single ChatGPT prompt. Infrastructure doesn't improve creative output.
3. **The blog project has the machinery.** 17 working Hermes skills, factory pipeline, Cloudflare infra, 111 packs, 160 ROs. The clean project needs to map and use these, not rebuild them.
4. **Truth map is the missing loop.** Everything produces content. Nothing feeds back into the knowledge base. Without it, the system is a content factory, not an epistemology engine.
5. **Truth map has 3 conflicting schemas.** The actual q-*.json files, the magnum-opus spec, and the propagation engine's ClaimRecord model all disagree on what a truth map question is.
6. **Codex (GPT-5.6) is the premium model for hard problems.** DeepSeek v4 Flash handles volume. Codex handles design decisions, GLSL beauty, and epistemology reasoning.
