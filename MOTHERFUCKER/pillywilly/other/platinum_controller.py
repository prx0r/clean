#!/usr/bin/env python3
"""
Platinum Production Controller — State Machine

The controller owns the stage sequence. Hermes may only write the artifact
required by the current state. The controller, not the agent, advances the job.

Usage:
    python3 platinum_controller.py new --essay scripts/expansion-essay15.md --slug my-pack
    python3 platinum_controller.py status --slug my-pack
    python3 platinum_controller.py advance --slug my-pack
    python3 platinum_controller.py retry --slug my-pack
"""

import json, os, sys, subprocess, re, math, enum, argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

FILE_DIR = Path(__file__).resolve().parent              # factory/controllers/
FACTORY_ROOT = FILE_DIR.parent                          # factory/
REPO_ROOT = FACTORY_ROOT.parent                         # project root
JOBS_DIR = Path(__file__).resolve().parent / ".jobs"

# ── STAGE DEFINITION ───────────────────────────────────────────────

class Stage(str, enum.Enum):
    PACK_SETUP = "pack_setup"
    GOLD_STUDY = "gold_study"
    RHETORICAL_MAP = "rhetorical_map"
    VISUAL_THESIS = "visual_thesis"
    MOTIF_MANUFACTURABILITY = "motif_manufacturability"
    STORYBOARD = "storyboard"
    STORYBOARD_REVIEW = "storyboard_review"
    PACK_COMPOSITION = "pack_composition"
    RENDER_PLAN = "render_plan"
    CODE_REVIEW = "code_review"
    DRAFT_RENDER = "draft_render"
    VISUAL_QC = "visual_qc"
    FINAL_RENDER = "final_render"

STAGE_ORDER = [
    Stage.PACK_SETUP,
    Stage.GOLD_STUDY,
    Stage.RHETORICAL_MAP,
    Stage.VISUAL_THESIS,
    Stage.MOTIF_MANUFACTURABILITY,
    Stage.STORYBOARD,
    Stage.STORYBOARD_REVIEW,
    Stage.PACK_COMPOSITION,
    Stage.RENDER_PLAN,
    Stage.CODE_REVIEW,
    Stage.DRAFT_RENDER,
    Stage.VISUAL_QC,
    Stage.FINAL_RENDER,
]

STAGE_DESCRIPTIONS = {
    Stage.PACK_SETUP: "Initialize pack directory with canonical template",
    Stage.GOLD_STUDY: "Study gold/platinum packs, extract signatures",
    Stage.RHETORICAL_MAP: "Read essay, extract transformations per passage",
    Stage.VISUAL_THESIS: "Design visual thesis + 3 candidate visual worlds",
    Stage.MOTIF_MANUFACTURABILITY: "Lint all motifs for drawability (score ≥12/16)",
    Stage.STORYBOARD: "Build per-shot storyboard with visual_audio_alignment",
    Stage.STORYBOARD_REVIEW: "Adversarial review: alignment, diversity, no gold-copy",
    Stage.PACK_COMPOSITION: "Write AGENT_KNOWLEDGE_DOSSIER, STYLE_EVOLUTION, PRODUCTION_BLUEPRINT",
    Stage.RENDER_PLAN: "Plan each shot: primitives, layers, phases, line counts",
    Stage.CODE_REVIEW: "Inspect scene functions: no dispatch, phase count, text ratio",
    Stage.DRAFT_RENDER: "Render low-res preview for visual QC",
    Stage.VISUAL_QC: "Silent-film test + similarity QC + motion check",
    Stage.FINAL_RENDER: "Render final high-res with audio",
}

# Each stage: input artifacts required, output artifacts produced, max retries
TEMPLATE_DIR = FACTORY_ROOT / "template"  # factory/template/

STAGE_CONFIG = {
    Stage.PACK_SETUP: {
        "inputs": ["essay_path"],
        "outputs": [
            "README.md", "storyboard.json",
            "visual_program.json", "AGENT_KNOWLEDGE_DOSSIER.md",
            "PRODUCTION_BLUEPRINT.md", "STYLE_EVOLUTION.md",
        ],
        "max_retries": 1,
        "hermes_prompt": "platinum-controller/pack-setup",
    },
    Stage.GOLD_STUDY: {
        "inputs": ["essay_path", "AGENT_KNOWLEDGE_DOSSIER.md"],
        "outputs": ["gold_signatures.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/gold-study",
    },
    Stage.RHETORICAL_MAP: {
        "inputs": ["essay_path", "gold_signatures.json"],
        "outputs": ["rhetorical_map.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/rhetorical-map",
    },
    Stage.VISUAL_THESIS: {
        "inputs": ["essay_path", "rhetorical_map.json", "gold_signatures.json", "AGENT_KNOWLEDGE_DOSSIER.md"],
        "outputs": ["visual_thesis.md", "visual_program.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/visual-thesis",
    },
    Stage.MOTIF_MANUFACTURABILITY: {
        "inputs": ["visual_program.json"],
        "outputs": ["motif_lint_report.json"],
        "max_retries": 3,
        "hermes_prompt": "platinum-controller/motif-lint",
    },
    Stage.STORYBOARD: {
        "inputs": ["rhetorical_map.json", "visual_thesis.md", "visual_program.json"],
        "outputs": ["storyboard.json"],
        "max_retries": 3,
        "hermes_prompt": "platinum-controller/storyboard",
    },
    Stage.STORYBOARD_REVIEW: {
        "inputs": ["storyboard.json", "gold_signatures.json"],
        "outputs": ["storyboard_review.json"],
        "max_retries": 3,
        "hermes_prompt": "platinum-controller/storyboard-review",
    },
    Stage.PACK_COMPOSITION: {
        "inputs": ["storyboard.json", "storyboard_review.json", "visual_program.json"],
        "outputs": ["AGENT_KNOWLEDGE_DOSSIER.md", "STYLE_EVOLUTION.md", "PRODUCTION_BLUEPRINT.md"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/pack-composition",
    },
    Stage.RENDER_PLAN: {
        "inputs": ["storyboard.json", "storyboard_review.json", "AGENT_KNOWLEDGE_DOSSIER.md"],
        "outputs": ["render_plan.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/render-plan",
    },
    Stage.CODE_REVIEW: {
        "inputs": ["render_plan.json", "STYLE_EVOLUTION.md"],
        "outputs": ["render_pack.py", "code_review.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/code-review",
    },
    Stage.DRAFT_RENDER: {
        "inputs": ["render_pack.py", "code_review.json"],
        "outputs": ["scenes/*.mp4", "draft_report.json"],
        "max_retries": 2,
        "hermes_prompt": "platinum-controller/draft-render",
    },
    Stage.VISUAL_QC: {
        "inputs": ["scenes/*.mp4", "storyboard.json"],
        "outputs": ["visual_qc_report.json"],
        "max_retries": 3,
        "hermes_prompt": "platinum-controller/visual-qc",
    },
    Stage.FINAL_RENDER: {
        "inputs": ["visual_qc_report.json"],
        "outputs": ["final.mp4", "alignment_report.json", "contact_sheet.jpg"],
        "max_retries": 1,
        "hermes_prompt": "platinum-controller/final-render",
    },
}


# ── JOB MODEL ──────────────────────────────────────────────────────

def load_job(slug: str) -> dict:
    path = JOBS_DIR / f"{slug}.json"
    if not path.exists():
        print(f"Error: Job '{slug}' not found.")
        sys.exit(1)
    return json.loads(path.read_text())


def save_job(job: dict):
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    path = JOBS_DIR / f"{job['slug']}.json"
    path.write_text(json.dumps(job, indent=2, default=str))


def create_job(slug: str, essay_path: str, output_dir: str) -> dict:
    if not os.path.exists(essay_path):
        print(f"Error: Essay not found at {essay_path}")
        sys.exit(1)

    # Determine rough audio duration from word count (150 wpm)
    word_count = 0
    with open(essay_path) as f:
        text = f.read()
        word_count = len(text.split())
    est_audio_duration = (word_count / 150) * 60  # seconds

    job = {
        "slug": slug,
        "essay_path": essay_path,
        "output_dir": output_dir,
        "created_at": datetime.utcnow().isoformat(),
        "current_stage": Stage.PACK_SETUP.value,
        "stage_history": [],
        "artifacts": {"essay_path": essay_path},
        "retries": {},
        "failed_shots": [],
        "approved_shots": [],
        "production_mode": "film_pack",  # film_pack | animation_pack | hybrid
        "target_shot_duration": 6.5,
        "est_audio_duration": round(est_audio_duration, 1),
        "recommended_shot_count": round(est_audio_duration / 6.5),
        "minimum_shot_count": max(10, round(est_audio_duration / 9.0)),
        "maximum_shot_count": round(est_audio_duration / 4.0) + 10,
    }
    os.makedirs(output_dir, exist_ok=True)
    save_job(job)

    # Copy canonical template into output directory
    if TEMPLATE_DIR.exists():
        import shutil
        for f in TEMPLATE_DIR.iterdir():
            if f.is_file() and f.suffix in (".md", ".json", ".py", ".jpg"):
                dst = Path(output_dir) / f.name
                if not dst.exists():
                    shutil.copy2(f, dst)
        print(f"  Template files copied to {output_dir}")
    return job


# ── STAGE ADVANCEMENT ──────────────────────────────────────────────

def get_stage_index(stage: Stage) -> int:
    return STAGE_ORDER.index(stage)


def current_stage_obj(job: dict) -> Stage:
    return Stage(job["current_stage"])


def next_stage(current: Stage) -> Optional[Stage]:
    idx = get_stage_index(current)
    if idx + 1 < len(STAGE_ORDER):
        return STAGE_ORDER[idx + 1]
    return None


def previous_stage(current: Stage) -> Optional[Stage]:
    idx = get_stage_index(current)
    if idx > 0:
        return STAGE_ORDER[idx - 1]
    return None


def stage_is_complete(job: dict, stage: Stage) -> bool:
    return any(h["stage"] == stage.value and h["status"] == "passed" for h in job["stage_history"])


def all_inputs_present(job: dict, stage: Stage) -> list[str]:
    """Return list of missing required inputs for this stage."""
    config = STAGE_CONFIG[stage]
    missing = []
    output_dir = Path(job["output_dir"])

    for inp in config["inputs"]:
        if inp == "essay_path":
            if not os.path.exists(job.get("essay_path", "")):
                missing.append(inp)
        elif inp.endswith("/*"):
            pattern = inp.replace("/*", "")
            if not list(output_dir.glob(f"{pattern}*")):
                missing.append(inp)
        else:
            artifact_path = output_dir / inp
            if not artifact_path.exists():
                missing.append(inp)

    return missing


def get_retry_count(job: dict, stage: Stage) -> int:
    return job.get("retries", {}).get(stage.value, 0)


def advance_stage(job: dict, status: str = "passed", notes: str = ""):
    stage = current_stage_obj(job)
    job["stage_history"].append({
        "stage": stage.value,
        "status": status,
        "notes": notes,
        "timestamp": datetime.utcnow().isoformat(),
        "attempt": get_retry_count(job, stage) + 1,
    })

    if status == "passed":
        next_st = next_stage(stage)
        if next_st:
            job["current_stage"] = next_st.value
        else:
            job["current_stage"] = "complete"
        job["retries"][stage.value] = 0  # reset retries
    else:
        job["retries"][stage.value] = get_retry_count(job, stage) + 1

    save_job(job)


def fail_stage_permanently(job: dict, reason: str):
    """Mark job as permanently failed at current stage."""
    stage = current_stage_obj(job)
    job["stage_history"].append({
        "stage": stage.value,
        "status": "failed",
        "notes": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "attempt": get_retry_count(job, stage) + 1,
    })
    job["current_stage"] = "failed"
    save_job(job)


# ── VALIDATORS ─────────────────────────────────────────────────────

def validate_stage_output(job: dict, stage: Stage) -> list[str]:
    """Run stage-specific validation. Returns list of errors (empty = pass)."""
    errors = []
    output_dir = Path(job["output_dir"])

    # Check required outputs exist
    config = STAGE_CONFIG[stage]
    for out in config["outputs"]:
        if "/*" in out:
            pattern = out.replace("/*", "")
            if not list(output_dir.glob(f"{pattern}*")):
                errors.append(f"Missing output: {out}")
        else:
            if not (output_dir / out).exists():
                errors.append(f"Missing output: {out}")

    # Stage-specific semantic checks
    if stage == Stage.MOTIF_MANUFACTURABILITY:
        lint_path = output_dir / "motif_lint_report.json"
        if lint_path.exists():
            report = json.loads(lint_path.read_text())
            motifs = report.get("motifs", [])
            if not motifs:
                errors.append("No motifs found in lint report — did not extract from visual_program.json")
            for motif_result in motifs:
                if motif_result.get("score", 0) < 12:
                    errors.append(
                        f"Motif '{motif_result.get('name', '?')}' "
                        f"scored {motif_result.get('score')}/16 "
                        f"(min 12): {motif_result.get('errors', [])}"
                    )

    elif stage == Stage.STORYBOARD:
        sb_path = output_dir / "storyboard.json"
        if sb_path.exists():
            sb = json.loads(sb_path.read_text())
            shots = sb if isinstance(sb, list) else sb.get("shots", [])

            # Timing validation
            mode = job.get("production_mode", "film_pack")
            audio_dur = job.get("est_audio_duration", 240)
            min_shots = job.get("minimum_shot_count", 20)
            max_shots = job.get("maximum_shot_count", 80)

            if len(shots) < min_shots:
                errors.append(f"Shot count {len(shots)} below minimum {min_shots} for ~{audio_dur}s audio")
            if len(shots) > max_shots:
                errors.append(f"Shot count {len(shots)} exceeds maximum {max_shots} for ~{audio_dur}s audio")

            durations = [s.get("duration_seconds", s.get("duration", 0)) for s in shots]
            durations = [d for d in durations if isinstance(d, (int, float)) and d > 0]

            if durations:
                avg_dur = sum(durations) / len(durations)
                max_dur = max(durations)

                if avg_dur > 11:
                    errors.append(f"Average shot duration {avg_dur:.1f}s exceeds 11s max (gold: 5-8s)")
                if max_dur > 20:
                    errors.append(f"Shot with duration {max_dur:.1f}s exceeds 20s absolute max")
                if max_dur > 15:
                    errors.append(f"Shot with duration {max_dur:.1f}s exceeds 15s — needs documented exception")

                # Check total runtime not grossly inflated
                total_dur = sum(durations)
                if total_dur > audio_dur * 1.8:
                    errors.append(f"Total runtime {total_dur:.0f}s is {total_dur/audio_dur:.1f}x audio duration {audio_dur:.0f}s (max 1.8x)")

            # Per-shot field validation
            for s in shots:
                alignment = s.get("visual_audio_alignment", {})
                why = alignment.get("why_it_matches") or alignment.get("why_this_visual_matches") or ""
                if len(why) < 50:
                    errors.append(
                        f"Shot {s.get('shot_id', '?')}: "
                        f"visual_audio_alignment too short ({len(why)} chars, min 50)"
                    )
                motif = s.get("concrete_motif", {})
                if isinstance(motif, str):
                    errors.append(f"Shot {s.get('shot_id', '?')}: motif is a string, not an object")
                elif isinstance(motif, dict):
                    parts = motif.get("drawable_parts", [])
                    if len(parts) < 2:
                        errors.append(
                            f"Shot {s.get('shot_id', '?')}: "
                            f"motif '{motif.get('name', '?')}' has < 2 drawable parts"
                        )

    elif stage == Stage.CODE_REVIEW:
        cr_path = output_dir / "code_review.json"
        if cr_path.exists():
            review = json.loads(cr_path.read_text())
            for issue in review.get("violations", []):
                errors.append(f"Code violation: {issue}")

    elif stage == Stage.VISUAL_QC:
        qc_path = output_dir / "visual_qc_report.json"
        if qc_path.exists():
            report = json.loads(qc_path.read_text())
            if not report.get("pass", False):
                errors.append(f"Visual QC failed: {report.get('summary', 'no summary')}")

    return errors


# ── HERMES INTEGRATION ─────────────────────────────────────────────

def call_llm_direct(prompt: str, system_prompt: str = "") -> str:
    """Call the LLM API directly (no Hermes subprocess overhead)."""
    api_key = open(REPO_ROOT / ".env.local").read().split("VIDEO_LLM_API_KEY=")[1].split("\n")[0].strip().strip('"')
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = json.dumps({
        "model": "deepseek-v4-flash",
        "messages": messages,
        "max_tokens": 8000,
    })
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://opencode.ai/zen/go/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "User-Agent: PlatinumFactory/1.0",
        "-d", data,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode != 0:
        return f"API call failed: {result.stderr[:200]}"
    
    try:
        resp = json.loads(result.stdout)
        return resp["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError) as e:
        return f"API response parse failed: {e}"


def call_hermes_for_stage(job: dict, stage: Stage) -> str:
    """Run the current stage — direct LLM API call (no Hermes subprocess)."""
    prompt = build_stage_prompt(job, stage)
    
    # Load the skill content as system prompt for context
    skill_path = REPO_ROOT / "hermes/skills/platinum-designer/SKILL.md"
    system_prompt = ""
    if skill_path.exists():
        system_prompt = f"You are Hermes, a platinum visual designer. Follow the process below:\n\n{skill_path.read_text()[:4000]}"

    print(f"  Running stage {stage.value} via direct API call...")
    print(f"  {'─'*50}")
    
    result = call_llm_direct(prompt, system_prompt)
    
    # Check if result is an error
    if result.startswith("API call failed") or result.startswith("API response parse failed"):
        print(f"  ✗ {result}")
        return result
    
    print(f"  ✓ Response received ({len(result)} chars)")
    print(f"  {'─'*50}")
    
    # Save the LLM response to the appropriate output file
    output_dir = Path(job["output_dir"])
    config = STAGE_CONFIG[stage]
    
    # Extract JSON from markdown code blocks if present
    import re
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', result, re.DOTALL)
    cleaned = json_match.group(1) if json_match else result
    
    # Try to parse as JSON and save
    try:
        parsed = json.loads(cleaned)
        # Save to first expected output file
        for out in config["outputs"]:
            if out.endswith(".json") and not out.endswith("/*"):
                out_path = output_dir / out
                with open(out_path, "w") as f:
                    json.dump(parsed, f, indent=2)
                print(f"  ✓ Saved to {out}")
                break
    except json.JSONDecodeError:
        # Not JSON — save as markdown/text to first .md output
        for out in config["outputs"]:
            if out.endswith(".md"):
                out_path = output_dir / out
                with open(out_path, "w") as f:
                    f.write(cleaned)
                print(f"  ✓ Saved to {out}")
                break
    
    return result


def build_stage_prompt(job: dict, stage: Stage) -> str:
    """Build the prompt for Hermes for a specific stage."""
    output_dir = job["output_dir"]
    essay_path = job["essay_path"]
    slug = job["slug"]

    base_prompts = {
        Stage.PACK_SETUP: f"""You are in PACK_SETUP stage for slug {slug}.

Your ONLY task: verify the canonical pack template was initialized in {output_dir}.
Check that these files exist:
- README.md, storyboard.json, visual_program.json
- AGENT_KNOWLEDGE_DOSSIER.md, PRODUCTION_BLUEPRINT.md, STYLE_EVOLUTION.md

No modifications needed — the template was copied automatically.
Output a brief verification report as pack_setup_report.json.""",

        Stage.GOLD_STUDY: f"""You are in GOLD_STUDY stage for essay {essay_path} (slug: {slug}).

Your ONLY task: study the gold/platinum packs and extract transferable principles.
Output to {output_dir}/gold_signatures.json.

Requirements:
- Read at least 4 gold packs (stones, kabbalah, malas, dvadasanta)
- For each, extract: transferable_principles[], forbidden_to_copy[], techniques[]
- Do NOT include any scene sequences, motif names, or shot counts from gold packs
- The output is a JSON file with principles ONLY

Read the files at:
- content/publishing/renders/gold-analysis/stones_analysis/stones_are_watching_film_pack/
- content/publishing/imports/packs/unpacked/kabbalah_tree_of_life/
- content/publishing/renders/gold-analysis/malas_three_veils_pack/
- content/publishing/renders/gold-analysis/dvadasanta_axis_pack/""",

        Stage.RHETORICAL_MAP: f"""You are in RHETORICAL_MAP stage for essay {essay_path} (slug: {slug}).

Your ONLY task: read the essay and extract transformations from each passage.
Output to {output_dir}/rhetorical_map.json.

For EACH passage, extract:
- passage_id, text_preview, rhetorical_function, logical_relation
- transformation: {{ subject, operator (VERB), object, through[] }}

The key question is: what transformation does this passage assert? Not what objects are mentioned but what is changing, what causes it, what remains continuous?""",

        Stage.VISUAL_THESIS: f"""You are in VISUAL_THESIS stage for slug {slug}.

Your ONLY task: design the visual thesis for the essay.
Output to {output_dir}/visual_thesis.md and {output_dir}/visual_program.json.

CRITICAL: Generate THREE competing visual worlds (candidate_worlds), not one.
Each world must have different materials, spatial model, motion verbs.
A critic will select or hybridize them.

For the selected world, define:
- material_world, spatial_world, motion_verbs (5-8)
- 4-7 recurring_systems with evolution arcs
- color_semantics with hex codes and meanings (70% neutral, 10-20% secondary, 3-8% accent)
- forbidden_cliches (≥5)
- opening_to_closing_resolution

Reference gold signatures at {output_dir}/gold_signatures.json""",

        Stage.MOTIF_MANUFACTURABILITY: f"""You are in MOTIF_MANUFACTURABILITY stage for slug {slug}.

Your ONLY task: lint every recurring system / motif in the visual thesis for manufacturability.
Output to {output_dir}/motif_lint_report.json.

Read the visual_program.json at {output_dir}/visual_program.json.
Extract ALL recurring_systems and motifs from the candidate worlds.

For EACH motif, score 0-2 on 8 criteria (max 16):
1. Concrete nouns — can it be named as visible objects?
2. Part inventory — 2-8 drawable components?
3. Motion verbs — precise transformations?
4. Material rendering — ink, vellum, glass, smoke, etc?
5. Spatial organisation — radial, axial, nested, diagonal?
6. PIL feasibility — polygons, masks, curves, compositing, blur?
7. Concept specificity — would it be wrong for a different passage?
8. No-text intelligibility — legible when muted?

Output format (EXACT):
{{
  "pass": true/false,
  "overall_score": <number>,
  "max_score": <number>,
  "motifs": [
    {{
      "name": "<motif_name>",
      "score": <0-16>,
      "errors": ["<error description or empty list>"]
    }}
  ]
}}

Minimum pass: 12/16 per motif. Any below 12 → pass=false + errors.""",

        Stage.STORYBOARD: f"""You are in STORYBOARD stage for slug {slug}.

Production mode: {job.get('production_mode', 'film_pack')}
Target per-shot: {job.get('target_shot_duration', 6.5)}s
Audio duration: {job.get('est_audio_duration', 240)}s
Target shot count: {job.get('recommended_shot_count', 37)} (range {job.get('minimum_shot_count', 20)}-{job.get('maximum_shot_count', 80)})

CRITICAL: Output in JSONL format — one JSON object per line, no markdown, no wrapper array.
This allows partial recovery if the response is long.

Output to {output_dir}/storyboard.json.

Read rhetorical map at {output_dir}/rhetorical_map.json
Read visual thesis at {output_dir}/visual_thesis.md

Split the essay into chapters (natural breaks from the rhetorical map).
Design ONE CHAPTER AT A TIME. Each chapter: 6-12 shots.
Each shot 5-10 seconds. Average 5-8s.

For each shot, output ONE LINE of JSONL:
{{"shot_id": "s001", "spoken_passage": "...", "chapter": "1", "duration_seconds": 6.5,
  "visual_mode": "interior_flame",
  "visual_audio_alignment": {{"transformation_asserted": "...", "what_viewer_sees": "...", "why_it_matches": "..."}},
  "concrete_motif": {{"motif_id": "interior_flame", "display_name": "...", "drawable_parts": ["..."], "motion_verbs": ["..."]}},
  "continuity": {{"inherits": [], "transforms": "", "hands_off": []}},
  "bad_first_visual": "...", "rejected_because": "...",
  "no_narration_test": "PASS", "text_required": false}}

HARD RULES:
- JSONL format: one JSON object per line
- Average shot duration 5-8s. No shot >20s.
- motif_id must be gold-style short (interior_flame)
- ≥2 drawable_parts, ≥1 motion_verb
- why_it_matches ≥2 sentences
- text_required false for ≥80% of shots
- No conceptual motif names""",

        Stage.STORYBOARD_REVIEW: f"""You are in STORYBOARD_REVIEW stage for slug {slug}.

Your ONLY task: adversarially review the storyboard.
Output to {output_dir}/storyboard_review.json.

Read the storyboard at {output_dir}/storyboard.json
Read gold signatures at {output_dir}/gold_signatures.json

Check for:
1. Alignment failures — any shot where why_it_matches is unconvincing
2. Abstract motifs — any concrete_motif name that's conceptual not drawable
3. Gold copying — any shot sequence too similar to a gold pack
4. Composition repetition — any composition layout used 3+ times consecutively
5. Text overuse — more than 15% of shots with text_required=true
6. Missing continuity — shots with no inherits or hands_off

For each violation found, record: shot_id, violation_type, severity (fail/warn), explanation.
A shot fails if it has any severity=fail violation.""",

        Stage.PACK_COMPOSITION: f"""You are in PACK_COMPOSITION stage for slug {slug}.

Your ONLY task: write the canoncial pack documentation files.
Output to {output_dir}/.

Read the storyboard at {output_dir}/storyboard.json
Read the review at {output_dir}/storyboard_review.json
Read the visual program at {output_dir}/visual_program.json

Write THREE files:

1. AGENT_KNOWLEDGE_DOSSIER.md — Design brief with:
   - Aim (one sentence)
   - Visual rules (3-5 concrete directives)
   - Guardrails (1-2 interpretation preventions)
   - Style family (colors, materials, composition)
   - New motifs introduced

2. STYLE_EVOLUTION.md — Visual inheritance with:
   - Inheritance chain from gold packs (which principles transfer)
   - New motifs introduced
   - Deprecated clichés
   - Vocabulary shift table

3. PRODUCTION_BLUEPRINT.md — Production spec with:
   - Shot count, runtime, format
   - Chapter structure
   - Key transitions
   - Technical specifications

The template files already exist in {output_dir}/ — UPDATE them with real content.""",

        Stage.RENDER_PLAN: f"""You are in RENDER_PLAN stage for slug {slug}.

Your ONLY task: create a render plan mapping each shot to PIL implementation.
Output to {output_dir}/render_plan.json.

For EACH shot, plan:
- function_name (scene_XXX_motif_name)
- estimated_lines (15-40)
- primitives[] (polygon, bezier, ellipse, etc.)
- layers[] (base, emission, masks, etc.)
- animation_phases[] (each with range[start,end], action, easing, stagger_seconds)
- text_elements[] (empty if possible)
- semantic_risk (what could go wrong visually)

Every shot must have 3+ animation_phases with different easings.
Reference: {output_dir}/gold_signatures.json for technique principles.""",

        Stage.CODE_REVIEW: f"""You are in CODE_REVIEW stage for slug {slug}.

Your ONLY task: write the render_pack.py and review your own code.
Output to {output_dir}/render_pack.py and {output_dir}/code_review.json.

RULES:
- Each scene gets its own function — NO dispatch table
- No render_for_motif() or any motif-name-based dispatch
- 15-40 lines per scene function
- Use the animation_phases from {output_dir}/render_plan.json
- Pure PIL + ffmpeg — no cv2, no numpy beyond basic use
- Colors from the palette in visual_program.json
- Every function must pass the no-narration test

In code_review.json, self-report:
- violations[] — any dispatch tables, excessive text, line count violations
- phase_count — scenes with < 3 animation phases
- text_ratio — percentage of scenes using explanatory text""",

        Stage.DRAFT_RENDER: f"""You are in DRAFT_RENDER stage for slug {slug}.

Your ONLY task: run the render_pack.py and produce a low-res preview.
Output scenes to {output_dir}/scenes/ and report to {output_dir}/draft_report.json.

Run: python3 {output_dir}/render_pack.py render
Also write draft_report.json with: shots_rendered, any errors, total_duration.""",

        Stage.VISUAL_QC: f"""You are in VISUAL_QC stage for slug {slug}.

Your ONLY task: run visual quality control on the rendered scenes.
Output to {output_dir}/visual_qc_report.json.

Tests:
1. Silent-film test — for each shot, can you infer the concept without audio?
   Note each shot that fails and why.
2. Similarity check — are adjacent shots visually distinct?
   Flag consecutive shots that look nearly identical.
3. Motion check — does each shot have meaningful motion?
   Flag static-appearing shots.

Output: {{ pass: bool, summary: str, failures: [], warnings: [] }}""",

        Stage.FINAL_RENDER: f"""You are in FINAL_RENDER stage for slug {slug}.

Your ONLY task: produce the final high-res film with audio.
Output to {output_dir}/final.mp4 and {output_dir}/alignment_report.json.

Steps:
1. Generate per-shot audio with Edge TTS
2. Render at full resolution
3. Mux audio with video
4. Write alignment_report.json with AV drift check
5. Generate contact_sheet.jpg""",
    }

    return base_prompts.get(stage, f"Stage {stage.value} for slug {slug}")


# ── CLI ────────────────────────────────────────────────────────────

def cmd_new(args):
    job = create_job(args.slug, args.essay, args.output)
    print(f"Created job '{job['slug']}'")
    print(f"  Stage: {job['current_stage']}")
    print(f"  Output: {job['output_dir']}")
    print(f"\nNext: python3 {__file__} advance --slug {job['slug']}")


def cmd_status(args):
    job = load_job(args.slug)
    print(f"Job: {job['slug']}")
    print(f"  Current stage: {job['current_stage']}")
    print(f"  Essay: {job['essay_path']}")
    print(f"  Output: {job['output_dir']}")
    print(f"  Created: {job['created_at']}")
    print()

    if job["current_stage"] == "complete":
        print("✓ ALL STAGES COMPLETE")
        return
    if job["current_stage"] == "failed":
        print("✗ JOB FAILED")
        last = job["stage_history"][-1]
        print(f"  At stage: {last['stage']}")
        print(f"  Reason: {last.get('notes', 'unknown')}")
        return

    stage = Stage(job["current_stage"])
    print(f"Current: {STAGE_DESCRIPTIONS[stage]}")
    retries = get_retry_count(job, stage)
    max_r = STAGE_CONFIG[stage]["max_retries"]
    print(f"  Retries: {retries}/{max_r}")

    missing = all_inputs_present(job, stage)
    if missing:
        print(f"  Missing inputs: {missing}")

    print()
    print("History:")
    for h in job["stage_history"]:
        icon = "✓" if h["status"] == "passed" else "✗" if h["status"] == "failed" else "?"
        print(f"  {icon} {h['stage']}: {h['status']} (attempt {h['attempt']})")
        if h.get("notes"):
            print(f"     Notes: {h['notes']}")


def cmd_advance(args):
    job = load_job(args.slug)

    if job["current_stage"] in ("complete", "failed"):
        print(f"Job is already {job['current_stage']}.")
        return

    stage = current_stage_obj(job)
    retries = get_retry_count(job, stage)
    max_r = STAGE_CONFIG[stage]["max_retries"]

    if retries >= max_r:
        fail_stage_permanently(job, f"Max retries ({max_r}) exceeded for {stage.value}")
        print(f"✗ Max retries ({max_r}) exceeded for stage {stage.value}. Job failed.")
        return

    print(f"\n{'='*60}")
    print(f"Stage: {stage.value}")
    print(f"  {STAGE_DESCRIPTIONS[stage]}")
    print(f"  Attempt: {retries + 1}/{max_r}")
    print(f"{'='*60}\n")

    # Check inputs
    missing = all_inputs_present(job, stage)
    if missing:
        print(f"✗ Missing inputs: {missing}")
        print("  Run previous stage first or check output directory.")
        return

    # Call Hermes
    print("  Running stage via direct API call...")
    result = call_hermes_for_stage(job, stage)
    print(f"  Hermes response: {result[:200]}...")

    # Validate outputs
    print("  Validating outputs...")
    errors = validate_stage_output(job, stage)

    if errors:
        print(f"\n✗ Stage {stage.value} FAILED validation:")
        for e in errors:
            print(f"  - {e}")
        advance_stage(job, status="failed", notes="; ".join(errors[:5]))
        print(f"\nRetries left: {max_r - retries - 1}")
        if retries + 1 < max_r:
            print(f"Next: python3 {__file__} retry --slug {job['slug']}")
    else:
        advance_stage(job, status="passed")
        next_st = current_stage_obj(job) if job["current_stage"] != "complete" else None
        print(f"\n✓ Stage {stage.value} PASSED")
        if next_st:
            print(f"  Next stage: {next_st.value}")
            print(f"  Next: python3 {__file__} advance --slug {job['slug']}")
        else:
            print("  ALL STAGES COMPLETE")


def cmd_retry(args):
    job = load_job(args.slug)
    stage = current_stage_obj(job)

    if job["current_stage"] in ("complete", "failed"):
        print(f"Job is {job['current_stage']}. Cannot retry.")
        return

    retries = get_retry_count(job, stage)
    max_r = STAGE_CONFIG[stage]["max_retries"]
    if retries >= max_r:
        print(f"Max retries ({max_r}) already reached for {stage.value}.")
        return

    print(f"Retrying stage {stage.value} (attempt {retries + 1}/{max_r})")
    cmd_advance(args)


def cmd_list_jobs(args):
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    jobs = sorted(JOBS_DIR.glob("*.json"))
    if not jobs:
        print("No jobs found.")
        return
    for jp in jobs:
        job = json.loads(jp.read_text())
        icon = "✓" if job["current_stage"] == "complete" else "✗" if job["current_stage"] == "failed" else "●"
        print(f"{icon} {job['slug']}: {job['current_stage']} ({job.get('essay_path', '?')})")


def main():
    parser = argparse.ArgumentParser(description="Platinum Production Controller")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Create a new production job")
    p_new.add_argument("--slug", required=True)
    p_new.add_argument("--essay", required=True)
    p_new.add_argument("--output", required=True)

    p_status = sub.add_parser("status", help="Show job status")
    p_status.add_argument("--slug", required=True)

    p_advance = sub.add_parser("advance", help="Run current stage and advance")
    p_advance.add_argument("--slug", required=True)

    p_retry = sub.add_parser("retry", help="Retry current stage")
    p_retry.add_argument("--slug", required=True)

    p_list = sub.add_parser("list", help="List all jobs")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "advance":
        cmd_advance(args)
    elif args.command == "retry":
        cmd_retry(args)
    elif args.command == "list":
        cmd_list_jobs(args)


if __name__ == "__main__":
    main()
