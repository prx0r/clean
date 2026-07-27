#!/usr/bin/env python3
"""Thumbnail server — editor + match viewer."""

import json, os, sys, mimetypes, http.server, urllib.parse

THUMBNAIL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "thumbnails"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")

sys.path.insert(0, os.path.dirname(__file__))
from thumbnail_render import render_thumbnail, build_spec, FONT_REGISTRY, TREATMENT_PRESETS

ALCHEMY_DIR = os.path.join(PROJECT_ROOT, "content", "sources", "occult", "alchemy", "emblems")
PUBLIC_ART_DIR = os.path.join(PROJECT_ROOT, "public", "art")

with open("/tmp/art_aggregated_complete.json") as f:
    ALL_ARTWORKS = json.load(f)

def build_image_lookup():
    lookup = {}
    for root, dirs, files in os.walk(ALCHEMY_DIR):
        for f in files:
            if f.endswith(".jpg") and not f.endswith(".json"):
                gallery = os.path.basename(root)
                lookup[f"alchemy_{gallery}_{f.replace('.jpg','')}"] = os.path.join(root, f)
    for root, dirs, files in os.walk(PUBLIC_ART_DIR):
        for f in files:
            if f.endswith((".jpg", ".png", ".jpeg")):
                lookup[f"curated_{f.rsplit('.',1)[0]}"] = os.path.join(root, f)
    for a in ALL_ARTWORKS:
        aid = a["id"]
        rp = a.get("_resolved_path", "")
        if rp and os.path.exists(rp) and aid not in lookup:
            lookup[aid] = rp
    return lookup

IMAGE_LOOKUP = build_image_lookup()

# ---- Domain matching (same as match_art_to_videos.py) ----
DOMAINS = {
    "alchemical": {"concepts": ["Transformation", "Beauty", "Purification", "Sacred Matter", "Conjunction", "Energy", "Union of Opposites", "Stability"], "motifs": ["alchemical_scroll", "laboratory", "mercury", "caduceus", "seven_metals", "green_lion", "vessel", "distillation", "spagyric"], "entities": ["alchemist", "laboratory", "mercury_god", "green_lion", "alembic"], "moods": ["mystical", "contemplative"]},
    "cosmic": {"concepts": ["Cosmology", "Celestial Spheres", "Macrocosm", "Microcosm", "Astrology", "Unity", "Correspondence", "Divine Order"], "motifs": ["cosmos", "macrocosm", "sun", "stars", "astrology", "planetary", "celestial", "mountain"], "entities": ["macrocosm", "microcosm", "astrologer", "zodiac", "planet", "sun_rays"], "moods": ["cosmic", "visionary", "mystical"]},
    "angelic": {"concepts": ["Angel", "Annunciation", "Revelation", "Theophany", "Active Imagination", "Mundus Imaginalis", "Perfect Nature", "Celestial Counterpart", "Guidance"], "motifs": ["angel", "light_ray", "light"], "entities": ["angel"], "moods": ["visionary", "illuminated", "sacred"]},
    "visionary": {"concepts": ["Imagination", "Imaginal World", "Perception", "Theophany", "Creative Imagination", "Vision", "Active Imagination", "Mundus Imaginalis"], "motifs": ["emblem", "symbol", "light", "light_ray"], "entities": ["allegorical_figure"], "moods": ["visionary", "symbolic", "illuminated", "illuminatory"]},
    "illumination": {"concepts": ["Ascent", "Liberation", "Radiant Body", "Theophany", "Light"], "motifs": ["light_ray", "light", "sun"], "entities": ["sun_rays", "light"], "moods": ["illuminated", "illuminatory", "visionary"]},
    "soul": {"concepts": ["Beauty", "Unity", "Divine Love", "Divine Power", "Divine Order", "Perception", "Stability"], "motifs": ["emblem", "symbol", "rose_cross", "rose"], "entities": ["allegorical_figure"], "moods": ["contemplative", "sacred", "mystical"]},
    "death": {"concepts": ["Transformation", "Purification", "Sacred Matter"], "motifs": ["darkness"], "moods": ["austere", "mystical", "contemplative"]},
    "oracle": {"concepts": ["Revelation", "Prophetic Vision", "Angel", "Annunciation", "Divine Power"], "motifs": ["angel", "light_ray"], "entities": ["angel"], "moods": ["visionary", "sacred", "mystical"]},
    "fire": {"concepts": ["Transformation", "Purification", "Sacred Matter", "Energy"], "motifs": ["sun", "light_ray", "light"], "entities": ["sun_rays"], "moods": ["illuminated", "visionary"]},
    "magic": {"concepts": ["Transformation", "Imagination", "Creative Imagination", "Artist Magician", "Himma"], "motifs": ["emblem", "symbol", "circle"], "entities": ["allegorical_figure"], "moods": ["mystical", "visionary"]},
    "dream": {"concepts": ["Imagination", "Imaginal World", "Perception", "Vision", "Active Imagination", "Mundus Imaginalis"], "motifs": ["emblem", "symbol"], "moods": ["visionary", "symbolic"]},
    "buddhist": {"concepts": ["Liberation", "Unity", "Perception"], "moods": ["contemplative", "sacred", "mystical"]},
    "nature": {"concepts": ["Sacred Matter", "Transformation", "Stability"], "motifs": ["earth", "mountain", "tree", "green_lion"], "entities": ["stone", "mountain", "philosophical_tree", "green_lion"], "moods": ["contemplative", "mystical", "austere"]},
    "self": {"concepts": ["Beauty", "Perception", "Unity", "Imagination", "Conjunction"], "motifs": ["emblem", "symbol", "rose_cross", "rose"], "entities": ["allegorical_figure"], "moods": ["contemplative", "mystical"]},
    "god": {"concepts": ["Divine Power", "Divine Love", "Divine Order", "Theophany", "Cosmology"], "motifs": ["light_ray", "light", "sun"], "moods": ["sacred", "visionary", "contemplative"]},
}

VIDEOS = [
    (1, "The Engine of Consciousness", ["alchemical", "cosmic", "illumination"]),
    (2, "Why You Feel Small", ["cosmic"]),
    (3, "Remember Enlightenment?", ["buddhist", "illumination", "visionary"]),
    (4, "The Path You Didn't Choose", ["alchemical", "visionary"]),
    (5, "Why Pain Is Actually Beautiful", ["alchemical", "death"]),
    (6, "Real as the Mirror", ["self", "visionary"]),
    (7, "How Light Becomes You", ["illumination", "angelic", "god"]),
    (8, "Why Some People Wake Up Overnight", ["illumination", "visionary", "buddhist"]),
    (9, "The Companion You've Had Since Birth", ["angelic", "oracle"]),
    (10, "The Death Everyone Forgets", ["death", "alchemical"]),
    (11, "The Universe Is a Mirror", ["cosmic", "god"]),
    (12, "The World Between Worlds", ["visionary", "angelic", "dream"]),
    (13, "The Secret Life of Matter", ["alchemical", "nature"]),
    (14, "The God Who Needs You", ["god", "angelic"]),
    (15, "The Light That Illuminates Itself", ["illumination", "self"]),
    (16, "The Dream That You Are", ["dream", "visionary"]),
    (17, "When the Gods Speak", ["oracle", "angelic"]),
    (18, "The Body You Cannot See", ["illumination", "alchemical"]),
    (19, "The Battle You Are Fighting", ["alchemical", "self"]),
    (20, "Everything Is Empty", ["buddhist", "cosmic"]),
    (21, "The Eight Limbs", ["buddhist", "alchemical"]),
    (22, "The Mind of the Universe", ["cosmic", "god"]),
    (23, "The Journey Everyone Must Take", ["death", "alchemical", "visionary"]),
    (24, "The Fire You're Already Burning In", ["fire", "alchemical"]),
    (25, "The Forgotten Oracles", ["oracle", "visionary"]),
    (26, "The Reality You Create Every Night", ["dream", "visionary"]),
    (27, "The Law That Explains Everything", ["cosmic", "god"]),
    (28, "The Self You Cannot Find", ["self", "visionary"]),
    (29, "The Self You Become While Sleeping", ["dream", "self"]),
    (30, "The Psyche Has No Walls", ["soul", "self"]),
    (31, "The Two Mountains That See the Same Dawn", ["cosmic", "nature"]),
    (32, "The Art and Science of Causing Change", ["magic", "alchemical"]),
    (33, "The Sun That Knows Itself", ["illumination", "cosmic", "self"]),
    (34, "The Evolution You Haven't Heard Of", ["cosmic", "soul"]),
    (35, "The Prayers That Move the Cosmos", ["cosmic", "angelic", "god"]),
    (36, "The Angel You Already Are", ["angelic", "soul"]),
    (37, "The Dream That Knows You", ["dream", "angelic"]),
    (38, "The Man Who Thought Himself Free", ["buddhist", "self"]),
    (39, "The Journey You're Already On", ["visionary", "alchemical"]),
    (40, "Voices That Speak", ["oracle", "angelic"]),
    (41, "The Companion That Tests You", ["angelic", "death"]),
    (42, "The Voice That Only Says No", ["death", "self"]),
    (43, "The Body You Travel In", ["soul", "alchemical"]),
    (44, "The Operation", ["magic", "alchemical"]),
    (45, "The Daimon in the Spine", ["alchemical", "illumination"]),
    (46, "The Stones That Know", ["nature", "alchemical"]),
    (47, "The Being of Light Before You", ["angelic", "illumination", "god"]),
    (48, "The Bodies You Cannot See", ["illumination", "soul"]),
    (49, "Why the Gods Need You", ["god", "angelic"]),
    (50, "The Stars Are in Your Blood", ["cosmic", "soul"]),
    (51, "The Beauty That Does Not Fade", ["soul", "angelic", "god"]),
    (52, "The God Who Longs to Be Known", ["god", "soul"]),
    (53, "The Soul at the Center of Everything", ["soul", "cosmic"]),
    (54, "The Universe Has a Soul", ["cosmic", "soul"]),
    (55, "Before the Earth Was Earth", ["cosmic", "nature"]),
    (56, "The Choice Before You Were Born", ["soul", "cosmic"]),
]

def compute_domain_score(art, domains):
    score = 0.0
    for domain_name in domains:
        domain = DOMAINS.get(domain_name)
        if not domain: continue
        for concept_field in ["concepts", "visual_motifs", "mood", "entities_depicted"]:
            domain_tags = domain.get(concept_field, [])
            if not domain_tags: continue
            art_tags = [t.strip().lower() for t in art.get(concept_field, []) if t and t.strip()]
            for dt in domain_tags:
                dtl = dt.lower()
                for at in art_tags:
                    if dtl == at: score += 5
                    elif dtl in at or at in dtl: score += 3
        if domain.get("mood_boost"):
            moods = [m.strip().lower() for m in art.get("mood", []) if m and m.strip()]
            if any(m in moods for m in ["mystical", "contemplative"]): score += 1
    return score

def score_image(art, domains):
    score = compute_domain_score(art, domains)
    text_bodies = []
    for field in ["concepts", "visual_motifs", "style", "mood", "entities_depicted"]:
        for item in art.get(field, []):
            item = item.strip()
            if item: text_bodies.append(item.lower())
    palette = art.get("color_palette", [])
    if isinstance(palette, list):
        for p in palette:
            if p and p.strip(): text_bodies.append(p.lower())
    if art.get("title"): text_bodies.append(art["title"].lower())
    if art.get("notes"): text_bodies.append(art["notes"].lower())
    if art.get("composition"): text_bodies.append(art["composition"].lower())
    combined = " ".join(text_bodies)
    keywords = sum([DOMAINS[d].get("concepts", []) + DOMAINS[d].get("motifs", []) + DOMAINS[d].get("moods", []) for d in domains], [])
    for kw in keywords:
        kw_lower = kw.lower()
        count = combined.count(kw_lower)
        if count > 0: score += count * 2
        if kw_lower in combined: score += 1
    has_conc = any(c.strip() for c in art.get("concepts", []))
    has_mot = any(m.strip() for m in art.get("visual_motifs", []))
    has_mood = any(m.strip() for m in art.get("mood", []))
    if has_conc: score += 2
    if has_mot: score += 1
    if has_mood: score += 1
    return round(score, 1)

def compute_matches():
    results = []
    for num, title, domains in VIDEOS:
        scored = [(score_image(art, domains), art) for art in ALL_ARTWORKS]
        scored.sort(key=lambda x: -x[0])
        top = scored[:2]
        entry = {"num": num, "title": title, "matches": []}
        for i, (score, art) in enumerate(top):
            entry["matches"].append({
                "rank": i + 1, "score": score,
                "id": art["id"],
                "image_title": art["title"][:100],
                "path": art.get("_resolved_path", ""),
                "concepts": [c for c in art.get("concepts", []) if c.strip()][:4],
            })
        results.append(entry)
    return results

ALL_MATCHES = compute_matches()
ASSIGNMENTS_FILE = os.path.join(THUMBNAIL_DIR, "assignments.json")

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE) as f:
            return json.load(f)
    return {}

def save_assignments(data):
    with open(ASSIGNMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---- HTTP handler ----
class ThumbnailHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_response(301)
            self.send_header("Location", "/thumbnails/assigner.html")
            self.end_headers()
            return

        # Serve image by ID
        if parsed.path.startswith("/img/"):
            img_id = parsed.path[5:]
            fpath = IMAGE_LOOKUP.get(img_id)
            if fpath and os.path.exists(fpath):
                self.send_response(200)
                ctype, _ = mimetypes.guess_type(fpath)
                self.send_header("Content-Type", ctype or "image/jpeg")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"Image not found: {img_id}")
            return

        if parsed.path.startswith("/api/"):
            if parsed.path == "/api/config":
                self._send_json({
                    "fonts": {k: v for k, v in sorted(FONT_REGISTRY.items())},
                    "treatments": list(TREATMENT_PRESETS.keys()),
                    "templates": ["landscape_below", "portrait_left", "portrait_right", "square_below"],
                    "videos": [{
                        "title": v["title"], "num": v["num"],
                        "image_id": v["matches"][0]["id"],
                        "caption": v["matches"][0]["concepts"][0] if v["matches"][0]["concepts"] else "",
                        "font_role": "eb_garamond",
                        "treatment_preset": "none",
                        "template_id": "landscape_below",
                        "slug": v["title"].lower().replace(":", "").replace(" ", "-")[:50],
                        "filename": f"{v['title'].lower().replace(':', '').replace(' ', '-')[:50]}.jpg",
                    } for v in ALL_MATCHES],
                })
                return
            elif parsed.path == "/api/matches":
                self._send_json(ALL_MATCHES)
                return
            elif parsed.path == "/api/images":
                images = []
                for a in ALL_ARTWORKS:
                    aid = a["id"]
                    if aid not in IMAGE_LOOKUP:
                        continue
                    images.append({
                        "id": aid,
                        "title": a.get("title", "")[:80],
                        "concepts": [c for c in a.get("concepts", []) if c.strip()][:3],
                        "motifs": [m for m in a.get("visual_motifs", []) if m.strip()][:3],
                        "mood": [m for m in a.get("mood", []) if m.strip()][:3],
                    })
                self._send_json(images)
                return
            elif parsed.path == "/api/assignments":
                self._send_json(load_assignments())
                return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/render":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return
            title = data.get("title", "Untitled")
            image_id = data.get("image_id")
            caption = data.get("caption", "")
            font_role = data.get("font_role", "eb_garamond")
            treatment_preset = data.get("treatment_preset", "none")
            template_id = data.get("template_id", "landscape_below")
            font_size = data.get("font_size")
            if image_id not in IMAGE_LOOKUP:
                self.send_error(404, f"Image not found: {image_id}")
                return
            slug = title.lower().replace(":", "").replace(" ", "-")[:50]
            output_dir = os.path.join(THUMBNAIL_DIR, "editor")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{slug}.jpg")
            spec = build_spec(title, image_id, caption, font_role, template_id, treatment_preset, font_size)
            ok = render_thumbnail(spec, IMAGE_LOOKUP, output_path)
            if not ok:
                self.send_error(500, "Render failed")
                return
            self._send_json({"status": "ok", "path": f"/thumbnails/editor/{slug}.jpg"})
            return
        elif parsed.path == "/api/save-assignments":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return
            save_assignments(data)
            self._send_json({"status": "ok", "count": len(data)})
            return
        self.send_error(404, "Not found")

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = http.server.HTTPServer(("0.0.0.0", port), ThumbnailHandler)
    print(f"Server running at http://localhost:{port}")
    print(f"  Viewer:  http://localhost:{port}/thumbnails/viewer.html")
    print(f"  Editor:  http://localhost:{port}/thumbnails/editor.html")
    print(f"  Matches: http://localhost:{port}/api/matches")
    print(f"Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
