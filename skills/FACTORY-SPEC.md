# Factory Specifications — Complete

Each factory is a formal stage machine. Input → process → validate → output. If validation fails, error resolution runs (max 3 retries, then quarantine).

---

## Factory 1: Research

**Purpose:** Source material → structured knowledge (ROs) → focused questions (EOs) → truth map

### 1a. ACQUIRE — Source & Dataset Ingestion

**Input:** DOI, URL, title, dataset ID
**Output:** Work JSON + PDF in library/, or Dataset Record
**Hermes skills:** `acquire`, `cron-acquire`, `dataset-acquire` (needed)
**Cloudflare:** Workers API → D1 (works metadata) → R2 (PDF storage)

**Process:**
```
DOI/Title → Crossref/OpenAlex metadata → Find OA copy → Download → Validate PDF → Create Work JSON
Dataset ID → OpenNeuro S3 → Download subject(s) → Create Dataset Record → Index in D1
```

**Validation gates:**
- W01: work_id matches pattern `^work:[a-z0-9_-]+$`
- W02: title is non-empty
- W03: ≥1 author with name
- W04: ≥1 topic
- W05: summary exists (≥10 chars)
- W06: PDF exists on disk (if assets.pdf_path set)
- W07: quality_score ≥ 0.3 or null
- W08: provenance.access_status ∈ allowed enum

**Error resolution:**
- 403 from publisher → try alternative URLs from OpenAlex locations (institutional repos)
- All repos blocked → user-assisted download via Telegram (acquire skill handles this)
- PDF invalid → retry download from different source (max 3)
- Dataset not found → log and skip, flag for manual review

---

### 1b. EXTRACT — Source → Research Object

**Input:** Work JSON + source text
**Output:** Research Object (RO) in content/research-objects/
**Hermes skills:** `curate`, `research-object-creator` (needed)
**Cloudflare:** Workers API → D1 (RO metadata) → R2 (source text)

**Process:**
```
Work JSON + source text → Read source → Extract passages by theme → Organize into RO body → Link passages to source_ids → Version in git
```

**Validation gates:**
- R01: ≥5 passages (or mark as stub)
- R02: Every passage has source_id linking to a Work
- R03: Passages are direct quotes or close paraphrases (not original analysis)
- R04: RO has a single coherent theme (don't mix unrelated sources)
- R05: All source_ids exist in content/works/
- R06: score ≥ 4 to be marked "ready for essay"

**Error resolution:**
- No passages extracted → check source text quality, retry with different extraction strategy (max 3)
- Source text too short → mark RO as "stub" with note
- Source_ids don't resolve → verify Work exists, recreate if needed
- After 3 failures → quarantine RO, flag for human review

---

### 1c. SYNTHESIZE — ROs → Essay Object

**Input:** Multiple ROs + research question
**Output:** Essay Object (EO) in content/essay-objects/
**Hermes skills:** `synth`, `essay-object-creator` (needed)

**Process:**
```
Research question + relevant ROs → Identify tension points → Extract competing claims → Formulate hypotheses → Write EO → Link to source ROs → Update truth map → Version in git
```

**Validation gates:**
- E01: EO has exactly one research question (not a list)
- E02: ≥2 ROs referenced (EO combines multiple sources)
- E03: Tension point is explicitly stated (what makes this question unresolved)
- E04: ≥2 hypotheses with competing claims
- E05: Every hypothesis links to specific RO passages
- E06: Source metaphysics status is set (not null)
- E07: question_id doesn't duplicate an existing EO question

**Error resolution:**
- Not enough ROs on topic → go back to EXTRACT, create more ROs first
- No clear tension point → question may be settled or underspecified → mark EO as "exploratory" not "active"
- Duplicate question → merge with existing EO or archive duplicate
- After 3 failures → quarantine EO, flag for human review

---

### 1d. PROBE — Hypothesis Engine

**Input:** Source metaphysics truth map
**Output:** EO proposals
**Hermes skills:** `hypothesis-engine` (needed)

**Process:**
```
Cron trigger → Scan truth map for underdetermined questions → Rank by depth/freshness/priority → Generate EO proposal → Check novelty against existing EOs → Submit proposal
```

**Validation gates:**
- H01: Question is underdetermined or unasked in truth map
- H02: ≥2 ROs exist that bear on this question
- H03: Novelty score > 0.5 (question not recently proposed)
- H04: Question aligns with research directive priorities

**Error resolution:**
- No underdetermined questions → expand source material or re-check truth map
- All proposals duplicate existing EOs → increase search breadth (check ROs across traditions)
- Low novelty scores → introduce random offset in ranking
- After 3 cycles with no valid proposals → pause engine, flag for human input

---

### 1e. SANSKRIT — Translation Pipeline

**Input:** Sanskrit text (GRETIL, manuscript)
**Output:** Translation Object (TO) in content/translation-objects/
**Hermes skills:** runs independently via sanskritree pipeline

**Process:**
```
Sanskrit text → Ingest + clean → Catalogue (metadata) → DeepSeek 7-pass translate → Adversarial review → Comparative review → TO created → Linked to Research Factory as source material
```

**Validation gates:**
- T01: Verse coverage ≥ 98% (per text)
- T02: No critical errors in adversarial review
- T03: Confidence ≥ 0.9 on core verses
- T04: All key terms have alternative translations documented

**Error resolution:**
- Coverage < 98% → retry specific failed verses (max 3)
- Adversarial review finds critical errors → return to Pass 5 with specific issues
- Confidence < 0.9 → mark verse as "low confidence," flag for human review

---

## Factory 2: Writing

**Purpose:** EO → written output (paper, essay, script)

### 2a. ACADEMIC — Paper Pipeline

**Input:** Essay Object
**Output:** Academic paper (PDF + JSON)
**Hermes skills:** `write` (TYPE B Paper variant)

**Process:**
```
EO → Thesis statement → Outline (V7 algorithm) → First draft → Peer review → Revision → Final → Publish
```

**Quote budget:** P1 ≤ 40%, final ≤ 25%, max 2 quotes per source

**Validation gates:**
- A01: Abstract ≤ 250 words
- A02: All claims in abstract appear in body
- A03: ≥1 citation per substantive claim
- A04: Peer review completed (via peer-review skill)
- A05: All reviewer issues addressed or rebutted
- A06: Quote budget: ≤ 25% in final, ≤ 2 quotes/source

**Error resolution:**
- Peer review finds blocking issues → return to revision (max 3)
- Quote budget exceeded → reduce quotes, expand original analysis
- After 3 failures → quarantine paper, do not publish

---

### 2b. ESSAY — Public Essay Pipeline

**Input:** Essay Object
**Output:** Published web essay (JSON + audio)
**Hermes skills:** `write` (TYPE A Essay variant), `writing/audio`, `writing/art`

**Process (3-pass with hard quote budget gates):**
```
EO → Pass 1: Source-maximal dump (≤70% quote, ≤1 quote/source) → Validate gate → 
Pass 2: Slop removal + concrete texture (applies to quotes AND commentary) → Validate gate → 
Pass 3: Emotional arc (≤15-20% quote, ≤1 quote/source) → Validate gate → 
Glossary integration → Art matching → Audio generation → Build → Deploy
```

**Validation gates:**
- P1_A: quote_word_count / total_word_count ≤ 0.70
- P1_B: no single source quoted > 70% of total quote word count
- P1_C: ≥1 concrete noun per AI commentary block
- P1_D: hook exists as first non-source block
- P1_E: zero NARR, NEG, or paraphrase blocks
- P1_F: all source_ids exist in content/works/

- P2_A: every abstraction in AI blocks replaced with concrete image
- P2_B: ≥1 unexpected concrete noun per AI block
- P2_C: no neutral summarizer voice (adopt stance)
- P2_D: quoted material passes concreteness test (or removed)
- P2_E: anti-slop checklist passes (0 failures)
- P2_F: stance is consistent throughout

- P3_A: hook → second hook (at 40%) → climax → return structure
- P3_B: ending circles back to opening concretely
- P3_C: ending shares NO key words with last source block
- P3_D: quote_word_count / total_word_count ≤ 0.20
- P3_E: max 1 quote per source
- P3_F: no single quote > 50 words
- P3_G: read aloud test passes (doesn't sound like a lecture)
- P3_H: final word count within target range

**Error resolution:**
- Gate fails → DELETE essay file, retry pass from scratch (max 3 per pass)
- 3 failures on same pass → MOVE essay to quarantine directory (not deploy), flag for human review
- Audio fails → retry with edge-tts fallback
- Build fails → check TypeScript errors, fix, retry

---

### 2c. VIDEO SCRIPT — Narrative Script Pipeline

**Input:** Essay Object
**Output:** Script with timing + visual cues
**Hermes skills:** `platinum-designer`

**Process:**
```
EO → Gold study → Rhetorical map → Script with visual beats → Timing map → Scene assignments
```

**Quote budget:** P1 ≤ 30%, final ≤ 10%, max 1 quote per source

**Validation gates:**
- V01: Script has clear narrative arc (hook → tension → resolution)
- V02: Every scene has a corresponding visual mode or shader reference
- V03: Timestamps sum to target duration ±10%
- V04: Quote budget: ≤ 10% in final, ≤ 1 quote/source
- V05: Read aloud test passes (natural spoken rhythm)

**Error resolution:**
- Script too long → trim scenes, merge beats
- Missing visual modes → return to rhetorical map stage, add visuals
- Quote budget exceeded → narrativize quotes into original prose

---

## Factory 3: Video

**Purpose:** EO/script → rendered video → published

### 3a. GOLD DESIGN — Storyboard Creation

**Input:** Essay Object or Video Script
**Output:** Gold pack (storyboard + visual plan)
**Hermes skills:** `platinum-designer`

**Process:**
```
Script → Gold study (watch exemplars) → Rhetorical map → Visual thesis → Scene-by-scene storyboard → Visual mode assignment → Review
```

**Validation gates:**
- G01: Storyboard has ≥1 visual metaphor per major concept
- G02: Every scene references a renderable visual mode (PIL or GLSL)
- G03: Continuity object persists through all scenes
- G04: Pacing allows 5-10s per scene minimum
- G05: Gold study referenced ≥2 exemplar analyses

**Error resolution:**
- No visual metaphor for concept → return to rhetorical map, brainstorm alternatives
- Unrenderable visual mode → check shader library, create new GLSL shader, or replace mode
- Pacing too fast → redistribute content

---

### 3b. PLATINUM RENDER — Scene Production

**Input:** Storyboard + visual mode assignments
**Output:** Rendered scenes (PIL or GLSL) → composite MP4
**Hermes skills:** `platinum-renderer`, `factory-pipeline`

**Process:**
```
Storyboard → Load pack → For each scene: render frames (PIL on CPU, GLSL on GPU) → Audio analysis → Composite with voiceover + music → ffmpeg assembly → QC
```

**Validation gates:**
- R01: Every frame renders without error
- R02: Total duration within ±5% of target
- R03: Audio sync within ±1 frame
- R04: Visual QC: contact sheet review (4 representative frames tell visual story)
- R05: Continuity check: continuity object persists
- R06: No-narration test: visuals communicate concept without words

**Error resolution:**
- Frame render error → retry with lower resolution or different backend (max 3)
- Audio sync drift → regenerate with drift compensation
- Visual QC fails → return to scene with specific notes
- After 3 failures → skip scene, mark as placeholder, flag for manual render

---

### 3c. SCENE REVIEW — HITL Feedback Loop

**Input:** Rendered scene
**Output:** Approved or revised scene
**Hermes skills:** `scene-review` (needed)
**Cloudflare:** studio.tantrafiles.xyz → D1 (feedback) → R2 (versions)

**Process:**
```
Scene rendered → Uploaded to R2 → Studio shows preview → User pauses at timestamp → Submits feedback → Agent reads feedback → Adjusts shader/params → Re-renders single scene → Uploads new version → User approves or iterates → Each version saved
```

**Validation gates:**
- S01: Every feedback item has a timestamp
- S02: Agent response cites specific parameter change
- S03: New version uploaded before feedback marked resolved
- S04: User approves before scene enters final assembly

**Error resolution:**
- Feedback unclear → agent asks for clarification
- Re-render fails → fall back to previous version, flag issue
- User rejects 3+ times on same scene → escalate (human-to-human), don't auto-iterate

---

### 3d. FABLECUT ASSEMBLY — Final Compilation

**Input:** Approved scenes
**Output:** Final MP4 + YouTube upload
**Hermes skills:** `publish-video-fablecut`

**Process:**
```
Approved scenes → FableCut timeline → Transitions → Music → Color grade → Export MP4 → Upload to YouTube
```

**Validation gates:**
- F01: All scenes present and in order
- F02: No missing audio tracks
- F03: Export completes without error
- F04: Final file > 0 bytes

**Error resolution:**
- Export fails → retry with lower quality preset
- Missing scene → pull from last approved version, flag
- Upload fails → queue for retry (max 3)

---

## Factory 4: Analytics

**Purpose:** Products → metrics → truth map updates → new hypotheses

### 4a. PERFORMANCE TRACK — YouTube + Publication Metrics

**Input:** Published videos + papers
**Output:** Performance metrics in D1
**Hermes skills:** `daily-research`, `deep-analysis`, `performance-track` (needed)

**Process:**
```
Published content → YouTube API / citation data → Gather views, retention, CTR, citations → Store in D1 → Compare against predictions
```

**Validation gates:**
- Perf01: Metrics collected within 24h of publishing
- Perf02: ≥7 days of data before drawing conclusions

---

### 4b. TRUTH MAP UPDATE — Evidence Integration

**Input:** Factory outputs + performance data
**Output:** Updated truth map
**Hermes skills:** `source-metaphysics` (needed)

**Process:**
```
Content published → Extract claims → Map to truth map questions → Update evidence weights → Recompute confidence → Recompute parent questions → Flag staleness
```

**Validation gates:**
- T01: Every claim in content maps to a truth map question
- T02: Evidence weights sum correctly
- T03: Parent question status computed from children

---

### 4c. HYPOTHESIS TEST — Claim Verification

**Input:** EO hypotheses + content performance
**Output:** Updated hypothesis confidence
**Hermes skills:** `hypothesis-test` (needed)

**Process:**
```
EO hypothesis → Content published → Audience engagement measured → Engagement ≠ truth, but audience interest in question is data → Update hypothesis confidence
```

---

## Error Resolution Hierarchy

```
Attempt render/process
  → Success: proceed
  → Failure:
      → Retry (max 3)
        → Success: log retry, proceed
        → Failure on 3rd retry:
            → Quarantine artifact (move to quarantine/, not deploy/)
            → Log error with full trace
            → Flag for human review
            → Process next item (don't block pipeline)
```

## Validation Gate Format

Every gate in every factory follows this schema:

```json
{
  "gate_id": "P1_A",
  "description": "Quote word count ≤ 70% of total",
  "type": "hard",           // hard = blocks pipeline, soft = warning only
  "command": "python3 scripts/validate-quote-budget.py {essay_id} 1",
  "pass_condition": "exit code 0",
  "fail_action": "delete file, retry from scratch (max 3)",
  "escalation": "quarantine after 3 failures",
  "depends_on": []
}
```

This format allows agents to discover gates programmatically rather than having them embedded in prompts.
