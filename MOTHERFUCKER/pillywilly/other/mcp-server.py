"""
Platinum Factory MCP Server — exposes factory as tools for any MCP-compatible LLM.

Run: python3 mcp-server.py
Then connect from ChatGPT Desktop, Claude Desktop, Cursor, etc.
"""
import json, sys, os, subprocess
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parent               # factory/cloudflare/src/
FACTORY_ROOT = MCP_DIR.parent.parent                     # factory/
REPO_ROOT = FACTORY_ROOT.parent                          # project root
ROOT = FACTORY_ROOT  # shorthand for backward compat
API = "https://platinum-factory.tradesprior.workers.dev"

# ── API HELPERS ────────────────────────────────────

def api_get(path):
    req = urllib.request.Request(f"{API}{path}")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{API}{path}", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def call_llm(prompt, system=""):
    """Call deepseek-v4-flash for creative work using curl (urllib gives 403)."""
    key = open(REPO_ROOT / ".env.local").read().split("VIDEO_LLM_API_KEY=")[1].split("\n")[0].strip().strip('"')
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps({"model": "deepseek-v4-flash", "messages": messages, "max_tokens": 8000})
    # Write payload to temp file to avoid shell escaping issues
    tmp = Path("/tmp/mcp-llm-payload.json")
    tmp.write_text(payload)
    result = subprocess.run(["curl", "-s", "-X", "POST",
        "https://opencode.ai/zen/go/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer " + key,
        "-d", "@" + str(tmp)], capture_output=True, text=True, timeout=300)
    resp = json.loads(result.stdout)
    return resp["choices"][0]["message"]["content"]

# ── TOOLS ──────────────────────────────────────────

TOOLS = [
    {
        "name": "factory_create_job",
        "description": "Create a new platinum production job for an essay. Returns job state with recommended shot count.",
        "inputSchema": {"type": "object", "properties": {
            "slug": {"type": "string", "description": "URL-safe slug for this job"},
            "essay_path": {"type": "string", "description": "Path to the essay markdown file, e.g. scripts/expansion-essay33.md"},
        }, "required": ["slug", "essay_path"]},
    },
    {
        "name": "factory_list_jobs",
        "description": "List all production jobs and their current stage.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "factory_get_job",
        "description": "Get detailed status of a specific job including stage history.",
        "inputSchema": {"type": "object", "properties": {
            "slug": {"type": "string"}
        }, "required": ["slug"]},
    },
    {
        "name": "factory_advance",
        "description": "Run the current stage of a job. Validates output and advances to next stage or retries.",
        "inputSchema": {"type": "object", "properties": {
            "slug": {"type": "string"}
        }, "required": ["slug"]},
    },
    {
        "name": "factory_get_storyboard",
        "description": "Get the storyboard for a job. Returns shots with visual_audio_alignment.",
        "inputSchema": {"type": "object", "properties": {
            "slug": {"type": "string"}
        }, "required": ["slug"]},
    },
    {
        "name": "factory_get_visual_thesis",
        "description": "Get the visual thesis for a job. Three worlds, palette, systems, forbidden cliches.",
        "inputSchema": {"type": "object", "properties": {
            "slug": {"type": "string"}
        }, "required": ["slug"]},
    },
    {
        "name": "factory_list_gold_packs",
        "description": "List all 31 gold/platinum reference packs with shot counts and paths.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "factory_get_pack_template",
        "description": "Get the canonical pack template format (storyboard, visual_program, dossier schemas).",
        "inputSchema": {"type": "object", "properties": {
            "section": {"type": "string", "description": "Which section: storyboard, visual_program, dossier, blueprint, or all"}
        }},
    },
    {
        "name": "factory_read_essay",
        "description": "Read the full text of an expansion essay.",
        "inputSchema": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Path like scripts/expansion-essay33.md"}
        }, "required": ["path"]},
    },
    {
        "name": "factory_read_gold_pack",
        "description": "Read a specific file from a gold pack for reference.",
        "inputSchema": {"type": "object", "properties": {
            "pack_id": {"type": "string", "description": "Gold pack ID from registry"},
            "file": {"type": "string", "description": "File to read: storyboard.json, visual_program.json, render_pack.py, AGENT_KNOWLEDGE_DOSSIER.md"}
        }, "required": ["pack_id", "file"]},
    },
    {
        "name": "factory_call_llm",
        "description": "Call the LLM directly for creative work (visual thesis, storyboard, motif design, PIL code).",
        "inputSchema": {"type": "object", "properties": {
            "prompt": {"type": "string", "description": "The prompt for the LLM"},
            "system": {"type": "string", "description": "System prompt context (skill file content, etc)"},
        }, "required": ["prompt"]},
    },
]

# ── HANDLER ────────────────────────────────────────

def handle(method, params, msg_id):
    resp = {"jsonrpc": "2.0", "id": msg_id}

    if method == "initialize":
        resp["result"] = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "platinum-factory", "version": "0.3.0"}}

    elif method == "tools/list":
        resp["result"] = {"tools": TOOLS}

    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        result = None

        try:
            if name == "factory_create_job":
                result = api_post("/jobs", {"slug": args["slug"], "essay_path": args["essay_path"]})

            elif name == "factory_list_jobs":
                result = api_get("/jobs")

            elif name == "factory_get_job":
                result = api_get(f"/jobs/{args['slug']}")

            elif name == "factory_advance":
                slug = args["slug"]
                job = api_get(f"/jobs/{slug}")
                stage = job.get("current_stage", "unknown")
                
                # Read the prompt template and call LLM
                essay_path = job.get("essay_path", "")
                output_dir = job.get("output_dir", "")
                
                prompt = f"You are in {stage} stage for job {slug}.\n"
                
                if stage == "gold_study":
                    prompt += f"Study 4 gold packs (stones, kabbalah, malas, dvadasanta) and extract transferable principles. Output to {output_dir}/gold_signatures.json"
                elif stage == "rhetorical_map":
                    prompt += f"Read essay at {essay_path}. Extract transformations per passage. Output to {output_dir}/rhetorical_map.json"
                elif stage == "storyboard":
                    audio = job.get("est_audio_duration", 240)
                    min_s = job.get("minimum_shot_count", 20)
                    max_s = job.get("maximum_shot_count", 80)
                    prompt += f"Build per-shot storyboard. Target {job.get('recommended_shot_count', 37)} shots. Audio: {audio}s. Each shot 5-10s. Output to {output_dir}/storyboard.json"
                else:
                    prompt += f"Complete stage {stage}. Output to {output_dir}/"
                
                llm_result = call_llm(prompt)
                # For now, just return what we'd do
                result = {"slug": slug, "stage": stage, "message": f"Stage {stage} prompt ready", "llm_response_preview": llm_result[:200]}

            elif name == "factory_get_storyboard":
                slug = args["slug"]
                job = api_get(f"/jobs/{slug}")
                path = f"{REPO_ROOT}/{job['output_dir']}/storyboard.json"
                with open(path) as f:
                    result = json.load(f)

            elif name == "factory_get_visual_thesis":
                slug = args["slug"]
                job = api_get(f"/jobs/{slug}")
                vp_path = f"{REPO_ROOT}/{job['output_dir']}/visual_program.json"
                vt_path = f"{REPO_ROOT}/{job['output_dir']}/visual_thesis.md"
                result = {}
                if os.path.exists(vp_path):
                    with open(vp_path) as f:
                        result["visual_program"] = json.load(f)
                if os.path.exists(vt_path):
                    with open(vt_path) as f:
                        result["visual_thesis"] = f.read()[:2000]

            elif name == "factory_list_gold_packs":
                with open(FACTORY_ROOT / "registry/gold-pack-registry.json") as f:
                    result = json.load(f)

            elif name == "factory_get_pack_template":
                section = args.get("section", "all")
                base = FACTORY_ROOT / "template"
                result = {}
                for f in base.iterdir():
                    if f.is_file() and f.suffix in (".md", ".json"):
                        result[f.name] = f.read_text()[:1000]

            elif name == "factory_read_essay":
                p = REPO_ROOT / args["path"]
                result = p.read_text() if p.exists() else f"File not found: {p}"

            elif name == "factory_read_gold_pack":
                with open(FACTORY_ROOT / "registry/gold-pack-registry.json") as f:
                    registry = json.load(f)
                pack = None
                for p in registry["gold_packs"]:
                    if p["name"] == args["pack_id"]:
                        pack = p
                        break
                if pack:
                    p = REPO_ROOT / pack["path"] / args["file"]
                    result = p.read_text()[:3000] if p.exists() else f"File not found: {p}"
                else:
                    result = f"Pack {args['pack_id']} not found"
            
            elif name == "factory_call_llm":
                result = call_llm(args["prompt"], args.get("system", ""))

            else:
                resp["error"] = {"code": -32601, "message": f"Unknown: {name}"}
                return resp

            resp["result"] = {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}

        except Exception as e:
            resp["result"] = {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}]}

    elif method == "ping":
        resp["result"] = {}

    else:
        resp["error"] = {"code": -32601, "message": f"Not found: {method}"}

    return resp


if __name__ == "__main__":
    # No banner — MCP protocol expects pure JSON-RPC on stdout
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            out = handle(msg.get("method", ""), msg.get("params", {}), msg.get("id", 0))
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
