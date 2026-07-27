#!/usr/bin/env python3
"""Operator Cockpit — lightweight Flask dashboard for content farm operations."""
import json, os, re, subprocess, glob, urllib.request, time, threading, sys, io
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

ROOT = Path(__file__).parent.parent
_cache = {}
_cache_lock = threading.Lock()
_predictor = None

sys.path.insert(0, str(ROOT / "scripts" / "engines"))

def load_predictor():
    global _predictor
    if _predictor is not None:
        return _predictor
    try:
        from predict_views import ViewsPredictor
        _predictor = ViewsPredictor()
        print(f"Predictor loaded: {_predictor.holdout_auc}", file=sys.stderr)
    except Exception as e:
        print(f"Predictor load failed: {e}", file=sys.stderr)
        return None
    return _predictor

def cached(key, ttl=60):
    def deco(fn):
        def wrapper(*a, **kw):
            now = time.time()
            with _cache_lock:
                if key in _cache and now - _cache[key]["time"] < ttl:
                    return _cache[key]["data"]
            result = fn(*a, **kw)
            with _cache_lock:
                _cache[key] = {"data": result, "time": time.time()}
            return result
        return wrapper
    return deco

app = Flask(__name__, static_folder="static")
CORS(app, origins=[os.environ.get("CORS_ORIGIN", "*")])

SANDBOX = Path("/root/projects/blog/visionary-sandbox")
ROOT = Path("/root/projects/blog")
BLUEPRINTS = ROOT / "tantrafiles" / "blueprints"
LAYER2 = ROOT / "data" / "research" / "layer2"
PUBLISHING = ROOT / "content" / "publishing" / "scripts"
FABLECUT_DIR = ROOT.parent / "FableCut"
HERMES_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
HERMES_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

def parse_blueprint(path):
    text = path.read_text()
    bp_id = re.search(r'\* `blueprint_id`: (\S+)', text)
    title = re.search(r'^# Research Blueprint \d+: (.+)$', text, re.MULTILINE)
    channel = re.search(r'\* `channel`: (\S+)', text)
    runtime = re.search(r'\* `target_runtime_minutes`: (\d+)', text)
    beats = len(re.findall(r'^\d+\.\s+\*\*', text, re.MULTILINE))
    hook = re.search(r'## Charged Hook\n\n(.+?)(?:\n\n)', text, re.DOTALL)
    return {
        "id": bp_id.group(1) if bp_id else path.stem,
        "title": title.group(1).strip()[:80] if title else path.stem,
        "channel": channel.group(1) if channel else "?",
        "runtime": int(runtime.group(1)) if runtime else 20,
        "beats": beats,
        "hook": hook.group(1).strip()[:150] if hook else "",
    }

def pipeline_status(bp_id):
    slug = bp_id.lower()
    base = PUBLISHING / slug
    return {
        "beat_map": base.joinpath("beat-map.md").exists(),
        "fablecut_project": base.joinpath(f"{slug}-fablecut.json").exists(),
        "media_dir": base.joinpath("media").exists(),
    }

@cached("channel_stats", ttl=60)
def channel_stats():
    channels = []
    for f in sorted(LAYER2.glob("analysis_*.json")):
        if "tantra_" in f.name: continue
        with open(f) as fh:
            d = json.load(fh)
        channels.append({
            "name": d["channel"], "subs": d["subs"],
            "median_views": d["median_views"], "analyzed": d["analyzed_videos"],
            "breakout_rate": d.get("breakout_rate", 0),
            "output_per_month": d.get("output_per_month", 0),
        })
    return sorted(channels, key=lambda c: -c["subs"])

# ── SANDBOX ───────────────────────────────────────────────────────────────────

@app.route("/sandbox/")
def sandbox_index():
    return send_from_directory(str(SANDBOX / "dist"), "index.html")

@app.route("/sandbox/<path:path>")
def sandbox_static(path):
    return send_from_directory(str(SANDBOX / "dist"), path)

# ── API ROUTES ──────────────────────────────────────────────────────────────

@app.route("/api/status")
def api_status():
    fablecut_ok = False
    try:
        r = urllib.request.urlopen("http://localhost:7777/", timeout=2)
        fablecut_ok = r.status == 200
    except: pass
    bps = list(BLUEPRINTS.glob("TBP-*.md"))
    return jsonify({
        "fablecut": "running" if fablecut_ok else "stopped",
        "blueprints": len(bps),
        "channels_analyzed": len(list(LAYER2.glob("analysis_*.json"))),
    })

@app.route("/api/blueprints")
def api_blueprints():
    bps = []
    for f in sorted(BLUEPRINTS.glob("TBP-*.md")):
        bp = parse_blueprint(f)
        pipe = pipeline_status(bp["id"])
        bps.append({**bp, "pipeline": pipe})
    return jsonify({"blueprints": bps})

@app.route("/api/blueprints/<bp_id>")
def api_blueprint_detail(bp_id):
    path = BLUEPRINTS / f"{bp_id.upper()}.md"
    if not path.exists():
        for f in BLUEPRINTS.glob(f"{bp_id.upper()}*.md"):
            path = f; break
        else:
            return jsonify({"error": "not found"}), 404
    bp = parse_blueprint(path)
    pipe = pipeline_status(bp["id"])
    # Extract beats
    text = path.read_text()
    beats = []
    for m in re.finditer(r'^(\d+)\.\s+\*\*(.+?)\*\*\s+\((\d+):(\d+)-(\d+):(\d+)\)\s+.*?—\s+(.+)$', text, re.MULTILINE):
        beats.append({"n": m.group(1), "title": m.group(2), "start": f"{m.group(3)}:{m.group(4)}",
                      "end": f"{m.group(5)}:{m.group(6)}", "role": m.group(7).strip()})
    return jsonify({**bp, "pipeline": pipe, "beats": beats})

@app.route("/api/channels")
def api_channels():
    return jsonify({"channels": channel_stats()})

@app.route("/api/channels/<name>")
def api_channel_detail(name):
    for f in LAYER2.glob("analysis_*.json"):
        with open(f) as fh:
            d = json.load(fh)
        if d["channel"].lower() == name.lower():
            return jsonify(d)
    return jsonify({"error": "not found"}), 404

@app.route("/api/predict")
def api_predict():
    title = request.args.get("title", "")
    if not title:
        return jsonify({"error": "provide ?title=..."}), 400
    p = load_predictor()
    if p is None:
        return jsonify({"error": "model not loaded"}), 500
    try:
        result = p.predict(title)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/fablecut/status")
def api_fablecut_status():
    try:
        r = urllib.request.urlopen("http://localhost:7777/", timeout=2)
        return jsonify({"status": "running", "port": 7777, "code": r.status})
    except Exception as e:
        return jsonify({"status": "stopped", "error": str(e)})

@app.route("/api/fablecut/project")
def api_fablecut_project():
    path = FABLECUT_DIR / "project.json"
    if path.exists():
        return jsonify(json.loads(path.read_text()))
    return jsonify({"error": "no project"}), 404

@app.route("/api/hermes/send", methods=["POST"])
def api_hermes_send():
    data = request.json
    msg = data.get("message", "")
    channel = data.get("channel", "general")
    if not HERMES_TOKEN:
        return jsonify({"error": "Telegram not configured"}), 400
    try:
        r = urllib.request.urlopen(
            f"https://api.telegram.org/bot{HERMES_TOKEN}/sendMessage",
            data=json.dumps({"chat_id": HERMES_CHAT, "text": f"[{channel}] {msg}",
                           "parse_mode": "Markdown"}).encode(),
            timeout=5)
        return jsonify({"ok": True, "response": json.loads(r.read())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate/<bp_id>", methods=["POST"])
def api_generate(bp_id):
    """Run blueprint-to-fablecut pipeline for a blueprint."""
    scripts_dir = ROOT / "scripts" / "engines"
    script = scripts_dir / "blueprint-to-fablecut.py"
    # Find the blueprint file
    bp_path = None
    for f in BLUEPRINTS.glob(f"{bp_id.upper()}*.md"):
        bp_path = f; break
    if not bp_path or not script.exists():
        return jsonify({"error": "blueprint or pipeline not found"}), 404
    try:
        r = subprocess.run(["python3", str(script), str(bp_path)],
                          capture_output=True, text=True, timeout=30)
        return jsonify({"output": r.stdout, "error": r.stderr[:500] if r.returncode != 0 else ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/validate")
def api_validate():
    """Run comprehensive video validation (blueprint + storyboard + vision)."""
    bp_id = request.args.get("blueprint", "")
    sb_slug = request.args.get("storyboard", "")
    try:
        cmd = ["node", str(ROOT / "scripts/validate-video.mjs"), "--json", "--skip-vision"]
        if bp_id:
            cmd.append(f"--blueprint={bp_id}")
        if sb_slug:
            cmd.append(f"--storyboard={sb_slug}")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if r.returncode in (0, 1):
            return jsonify(json.loads(r.stdout))
        return jsonify({"error": r.stderr[:500], "passed": False})
    except Exception as e:
        return jsonify({"error": str(e), "passed": False}), 500

@app.route("/api/analytics/overview")
def api_analytics():
    channels = channel_stats()
    total_views = sum(c["median_views"] * c["analyzed"] for c in channels if c["median_views"])
    top_channels = sorted(channels, key=lambda c: -c["median_views"])[:5]
    return jsonify({"total_estimated_views": total_views,
                    "channels_analyzed": len(channels),
                    "top_channels": top_channels})

# ── R2 proxy ───────────────────────────────────────────────────────────────

@app.route("/api/r2/<path:r2path>")
def api_r2_proxy(r2path):
    import boto3
    s3 = boto3.client("s3", endpoint_url=R2_ENDPOINT,
                       aws_access_key_id=R2_ACCESS_KEY,
                       aws_secret_access_key=R2_SECRET_KEY)
    try:
        head = s3.head_object(Bucket=R2_BUCKET, Key=r2path)
        total = head["ContentLength"]
        content_type = "video/mp4" if r2path.endswith(".mp4") else \
                       "audio/mpeg" if r2path.endswith(".mp3") else \
                       "application/json" if r2path.endswith(".json") else \
                       "image/jpeg" if r2path.endswith((".jpg", ".jpeg")) else \
                       "image/png" if r2path.endswith(".png") else "application/octet-stream"

        range_header = request.headers.get("Range", "")
        if range_header and r2path.endswith(".mp4"):
            match = re.search(r"bytes=(\d+)-(\d*)", range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else total - 1
                obj = s3.get_object(Bucket=R2_BUCKET, Key=r2path, Range=f"bytes={start}-{end}")
                data = obj["Body"].read()
                return Response(data, status=206, headers={
                    "Content-Type": content_type,
                    "Content-Range": f"bytes {start}-{end}/{total}",
                    "Content-Length": str(len(data)),
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "public, max-age=86400",
                })

        obj = s3.get_object(Bucket=R2_BUCKET, Key=r2path)
        return Response(obj["Body"].read(), content_type=content_type, headers={
            "Accept-Ranges": "bytes", "Content-Length": str(total), "Cache-Control": "public, max-age=86400"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# ── REVIEW (video feedback) ────────────────────────────────────────────────

R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
R2_BUCKET = os.environ.get("R2_BUCKET", "blog-video-assets")
R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY", "")
R2_SECRET_KEY = os.environ.get("R2_SECRET_KEY", "")

REVIEW_DIR = ROOT / "data" / "review"
REVIEW_INDEX = REVIEW_DIR / "index.json"
REVIEW_COMMENTS = REVIEW_DIR / "comments"

def ensure_review_dirs():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_COMMENTS.mkdir(parents=True, exist_ok=True)
    if not REVIEW_INDEX.exists():
        REVIEW_INDEX.write_text("[]")

def load_review_index():
    ensure_review_dirs()
    return json.loads(REVIEW_INDEX.read_text())

def save_review_index(index):
    REVIEW_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False))

@app.route("/api/review/videos")
def api_review_videos():
    return jsonify(load_review_index())

@app.route("/api/review/videos/<video_id>")
def api_review_video(video_id):
    index = load_review_index()
    video = next((v for v in index if v["id"] == video_id), None)
    if not video:
        return jsonify({"error": "not found"}), 404
    comments_path = REVIEW_COMMENTS / f"{video_id}.json"
    comments = json.loads(comments_path.read_text()) if comments_path.exists() else []
    video["comments"] = comments
    return jsonify(video)

@app.route("/api/review/videos/<video_id>/comments", methods=["GET", "POST"])
def api_review_comments(video_id):
    comments_path = REVIEW_COMMENTS / f"{video_id}.json"
    if request.method == "GET":
        return jsonify(json.loads(comments_path.read_text()) if comments_path.exists() else [])
    data = request.json
    comment = {
        "id": str(int(time.time() * 1000)),
        "author": data.get("author", "Anonymous"),
        "rating": data.get("rating"),
        "comment": data.get("comment", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    comments = json.loads(comments_path.read_text()) if comments_path.exists() else []
    comments.insert(0, comment)
    comments_path.write_text(json.dumps(comments, indent=2, ensure_ascii=False))
    # Update average rating in index
    if data.get("rating"):
        index = load_review_index()
        for v in index:
            if v["id"] == video_id:
                all_ratings = [c.get("rating") for c in comments if c.get("rating")]
                v["avgRating"] = round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else None
                break
        save_review_index(index)
    return jsonify({"ok": True})

# ── SCENE REVIEW ────────────────────────────────────────────────────────────

SCENE_COMMENTS_DIR = REVIEW_DIR / "scene-comments"

def ensure_scene_dirs():
    SCENE_COMMENTS_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/api/scenes")
def api_scenes():
    inst_dir = ROOT / "visual-library" / "instances"
    if not inst_dir.exists():
        return jsonify([])
    scenes = []
    for f in sorted(inst_dir.glob("*.json")):
        try:
            scenes.append(json.loads(f.read_text()))
        except: pass
    return jsonify(scenes)

@app.route("/api/scenes/<scene_id>")
def api_scene_detail(scene_id):
    inst_dir = ROOT / "visual-library" / "instances"
    for f in inst_dir.glob(f"{scene_id.replace(':','_')}*.json"):
        try:
            sdata = json.loads(f.read_text())
            ensure_scene_dirs()
            cp = SCENE_COMMENTS_DIR / f"{scene_id}.json"
            sdata["comments"] = json.loads(cp.read_text()) if cp.exists() else []
            return jsonify(sdata)
        except: pass
    return jsonify({"error": "not found"}), 404

@app.route("/api/scenes/<scene_id>/comments", methods=["GET", "POST"])
def api_scene_comments(scene_id):
    ensure_scene_dirs()
    cp = SCENE_COMMENTS_DIR / f"{scene_id}.json"
    if request.method == "GET":
        return jsonify(json.loads(cp.read_text()) if cp.exists() else [])
    data = request.json
    comment = {
        "id": str(int(time.time() * 1000)),
        "author": data.get("author", "Thomas"),
        "rating": data.get("rating"),
        "comment": data.get("comment", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    comments = json.loads(cp.read_text()) if cp.exists() else []
    comments.insert(0, comment)
    cp.write_text(json.dumps(comments, indent=2))
    return jsonify({"ok": True})

# ── SCENE CATALOG ───────────────────────────────────────────────────────────

CATALOG_PATH = ROOT / "visual-library" / "catalog" / "scenes.json"

@app.route("/api/catalog")
def api_catalog():
    if not CATALOG_PATH.exists():
        return jsonify({"total_scenes": 0, "scenes": []})
    return jsonify(json.loads(CATALOG_PATH.read_text()))

@app.route("/api/catalog/search")
def api_catalog_search():
    if not CATALOG_PATH.exists():
        return jsonify([])
    catalog = json.loads(CATALOG_PATH.read_text())
    q = request.args.get("q", "").lower().strip()
    scenes = catalog.get("scenes", [])
    if not q:
        return jsonify(scenes[:20])
    terms = q.split()
    results = []
    for s in scenes:
        text = json.dumps(s).lower()
        if all(t in text for t in terms):
            results.append(s)
    return jsonify(results[:30])

@app.route("/api/catalog/instances")
def api_catalog_instances():
    inst_dir = ROOT / "visual-library" / "instances"
    if not inst_dir.exists():
        return jsonify([])
    instances = []
    for f in sorted(inst_dir.glob("*.json")):
        try:
            instances.append(json.loads(f.read_text()))
        except: pass
    return jsonify(instances)

@app.route("/api/catalog/concepts")
def api_catalog_concepts():
    if not CATALOG_PATH.exists():
        return jsonify([])
    catalog = json.loads(CATALOG_PATH.read_text())
    concepts = {}
    for s in catalog.get("scenes", []):
        m = s.get("meaning", {})
        if isinstance(m, str):
            concepts[m.lower()] = concepts.get(m.lower(), 0) + 1
            continue
        for c in m.get("secondary", []) + [m.get("primary", "")]:
            c = str(c).strip().lower()
            if c and len(c) > 3:
                concepts[c] = concepts.get(c, 0) + 1
    sorted_c = sorted(concepts.items(), key=lambda x: -x[1])[:200]
    return jsonify([{"concept": k, "count": v} for k, v in sorted_c])

# ── FINAL PRODUCTION VIDEOS ────────────────────────────────────────────────

FINAL_DIR = ROOT / "data" / "final"
FINAL_INDEX = FINAL_DIR / "index.json"
FINAL_COMMENTS = FINAL_DIR / "comments"
FINAL_SHOTS = FINAL_DIR / "shots"
FINAL_LOGS = FINAL_DIR / "feedback-logs"

def ensure_final_dirs():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_COMMENTS.mkdir(parents=True, exist_ok=True)
    FINAL_SHOTS.mkdir(parents=True, exist_ok=True)
    FINAL_LOGS.mkdir(parents=True, exist_ok=True)
    if not FINAL_INDEX.exists():
        FINAL_INDEX.write_text("[]")

def load_final_index():
    ensure_final_dirs()
    return json.loads(FINAL_INDEX.read_text())

def save_final_index(index):
    FINAL_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False))

def write_feedback_log(video_id, entry):
    """Write human-readable markdown feedback log."""
    ensure_final_dirs()
    log_path = FINAL_LOGS / f"{video_id}.md"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    with open(log_path, "a") as f:
        f.write(f"\n## {timestamp}\n")
        f.write(f"**Author:** {entry.get('author', 'Thomas')}\n")
        if entry.get("rating"):
            f.write(f"**Rating:** {'★' * entry['rating']}{'☆' * (5 - entry['rating'])}\n")
        f.write(f"**Type:** {entry.get('type', 'episode')}\n")
        if entry.get("shot_id"):
            f.write(f"**Shot:** {entry['shot_id']}\n")
        if entry.get("dimension"):
            f.write(f"**Dimension:** {entry['dimension']}\n")
        f.write(f"\n{entry.get('comment', '')}\n")
        f.write("\n---\n")

@app.route("/api/final/videos", methods=["GET", "POST"])
def api_final_videos():
    if request.method == "POST":
        data = request.json
        index = load_final_index()
        video = {
            "id": data.get("id", f"vid-{int(time.time())}"),
            "title": data.get("title", "Untitled"),
            "essay": data.get("essay", ""),
            "channel": data.get("channel", ""),
            "mp4_path": data.get("mp4_path", ""),
            "duration": data.get("duration", 0),
            "shots": data.get("shots", []),
            "status": data.get("status", "draft"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": 1,
        }
        # Check for existing
        for i, v in enumerate(index):
            if v["id"] == video["id"]:
                video["version"] = v.get("version", 0) + 1
                video["created_at"] = v["created_at"]
                index[i] = video
                break
        else:
            index.append(video)
        save_final_index(index)
        return jsonify(video)
    # GET — list all
    index = load_final_index()
    return jsonify(index)

@app.route("/api/final/videos/<video_id>")
def api_final_video(video_id):
    index = load_final_index()
    video = next((v for v in index if v["id"] == video_id), None)
    if not video:
        return jsonify({"error": "not found"}), 404
    # Load episode comments
    comments_path = FINAL_COMMENTS / f"{video_id}.json"
    video["comments"] = json.loads(comments_path.read_text()) if comments_path.exists() else []
    # Load per-shot feedback
    shots_path = FINAL_SHOTS / f"{video_id}.json"
    shot_feedback = json.loads(shots_path.read_text()) if shots_path.exists() else {}
    for s in video.get("shots", []):
        sid = s.get("id", "")
        s["feedback"] = shot_feedback.get(sid, [])
    return jsonify(video)

@app.route("/api/final/videos/<video_id>/feedback", methods=["POST"])
def api_final_video_feedback(video_id):
    ensure_final_dirs()
    data = request.json
    entry = {
        "id": str(int(time.time() * 1000)),
        "author": data.get("author", "Thomas"),
        "type": data.get("type", "episode"),
        "rating": data.get("rating"),
        "dimension": data.get("dimension", ""),
        "comment": data.get("comment", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    # Save to episode comments
    comments_path = FINAL_COMMENTS / f"{video_id}.json"
    comments = json.loads(comments_path.read_text()) if comments_path.exists() else []
    comments.insert(0, entry)
    comments_path.write_text(json.dumps(comments, indent=2, ensure_ascii=False))
    # Write markdown log
    write_feedback_log(video_id, entry)
    # Update avg rating in index
    if data.get("rating"):
        index = load_final_index()
        for v in index:
            if v["id"] == video_id:
                all_ratings = [c.get("rating") for c in comments if c.get("rating")]
                v["avgRating"] = round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else None
                v["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                break
        save_final_index(index)
    return jsonify({"ok": True})

@app.route("/api/final/videos/<video_id>/shots/<shot_id>/feedback", methods=["POST"])
def api_final_shot_feedback(video_id, shot_id):
    ensure_final_dirs()
    data = request.json
    entry = {
        "id": str(int(time.time() * 1000)),
        "author": data.get("author", "Thomas"),
        "rating": data.get("rating"),
        "dimension": data.get("dimension", ""),
        "comment": data.get("comment", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    # Save to per-shot feedback
    shots_path = FINAL_SHOTS / f"{video_id}.json"
    shot_feedback = json.loads(shots_path.read_text()) if shots_path.exists() else {}
    if shot_id not in shot_feedback:
        shot_feedback[shot_id] = []
    shot_feedback[shot_id].insert(0, entry)
    shots_path.write_text(json.dumps(shot_feedback, indent=2, ensure_ascii=False))
    # Write markdown log
    write_feedback_log(video_id, {**entry, "type": "shot", "shot_id": shot_id})
    return jsonify({"ok": True})

@app.route("/api/final/videos/<video_id>/shots/<shot_id>", methods=["PUT"])
def api_final_shot_update(video_id, shot_id):
    data = request.json
    index = load_final_index()
    for v in index:
        if v["id"] == video_id:
            for s in v.get("shots", []):
                if s["id"] == shot_id:
                    s.update(data)
                    s["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    save_final_index(index)
                    return jsonify(s)
    return jsonify({"error": "not found"}), 404

# ── STATIC FILES ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    print(f"Dashboard: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
