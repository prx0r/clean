"""Zeus analysis module — pure data, no LLM calls.
Hermes calls this to get structured scene analysis + gold patterns,
then uses its own LLM access to rewrite scenes."""

import re, os, json

GOLD_PACKS_DIR = "/root/projects/blog/content/publishing/imports/packs/unpacked"

def load_gold_patterns():
    """Extract compact patterns from all gold pack render scripts."""
    patterns = []
    for entry in sorted(os.listdir(GOLD_PACKS_DIR)):
        for root, dirs, files in os.walk(os.path.join(GOLD_PACKS_DIR, entry)):
            for f in files:
                if f.endswith(".py") and "render" in f.lower():
                    code = open(os.path.join(root, f)).read()
                    funcs = re.findall(r'def (sc\d+|scene_\w+)\(', code)
                    primitives = set()
                    for p in ["ellipse", "rectangle", "line", "polygon", "arc", "text"]:
                        if p in code: primitives.add(p)
                    colors = len(re.findall(r'[A-Z_]{3,}\s*=\s*\(', code))
                    patterns.append({
                        "name": entry[:30],
                        "scenes": len(funcs),
                        "primitives": sorted(primitives),
                        "colors": colors,
                        "lines": len(code.split('\n')),
                        "sample_funcs": funcs[:3],
                    })
                    break
            break
    return patterns

def analyze_scenes(render_script_path):
    """Analyze each scene function in a render script."""
    code = open(render_script_path).read()
    funcs = re.findall(r'def (sc\d+)\(', code)
    scenes = []
    for fn in funcs:
        start = code.find(f"def {fn}(")
        end = code.find("\ndef ", start + 10)
        if end < 0: end = len(code)
        snippet = code[start:end]
        lines = len(snippet.split('\n'))
        prims = []
        for p in ["ellipse", "rectangle", "line", "polygon", "arc", "text"]:
            if p in snippet: prims.append(p)
        scenes.append({
            "name": fn,
            "lines": lines,
            "primitives": prims,
            "has_motion": "math.sin(t" in snippet or "ease(" in snippet,
        })
    return scenes

def build_elevation_context(render_script_path, essay_path):
    """Return everything the LLM needs to improve the script."""
    gold = load_gold_patterns()
    scenes = analyze_scenes(render_script_path)
    essay = open(essay_path).read()[:2000] if os.path.exists(essay_path) else ""
    code = open(render_script_path).read()
    
    return {
        "gold_patterns": gold,
        "scene_analysis": scenes,
        "essay_snippet": essay,
        "full_code": code,
    }

def critique_context(render_script_path, essay_path):
    """Return analysis with gold comparison for LLM critique."""
    ctx = build_elevation_context(render_script_path, essay_path)
    # Add comparison metrics
    gold_avg = sum(p["lines"] for p in ctx["gold_patterns"]) / max(len(ctx["gold_patterns"]), 1)
    for s in ctx["scene_analysis"]:
        s["vs_gold_avg"] = round(s["lines"] - gold_avg / 10)
        s["needs_work"] = len(s["primitives"]) < 2 or not s["has_motion"]
    return ctx
