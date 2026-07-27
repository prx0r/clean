#!/usr/bin/env python3
"""Factory Audit — run all binary validation rules across the pipeline.

Usage:
  python3 scripts/factory-audit.py                    # full audit
  python3 scripts/factory-audit.py --stage works      # works only
  python3 scripts/factory-audit.py --stage ros        # ROs only
  python3 scripts/factory-audit.py --stage essays     # essays only
  python3 scripts/factory-audit.py --stage storyboards
  python3 scripts/factory-audit.py --ro ro:corbin-imaginal-expanded  # single RO
  python3 scripts/factory-audit.py --json             # machine-readable JSON output
"""

import json, os, sys, glob, re

ROOT = "/root/projects/blog"
PASS, FAIL = "PASS", "FAIL"
results = {"passed": 0, "failed": 0, "rules": []}

def rule(code, ok, detail=""):
    results["rules"].append({"code": code, "status": PASS if ok else FAIL, "detail": detail})
    if ok: results["passed"] += 1
    else: results["failed"] += 1

# ── Stage 1: Works ──
def audit_works():
    works_dir = os.path.join(ROOT, "content", "works")
    if not os.path.exists(works_dir): return
    for f in sorted(os.listdir(works_dir)):
        if not f.endswith(".json") or f.startswith("_"): continue
        path = os.path.join(works_dir, f)
        try:
            w = json.load(open(path))
        except: rule("W00", False, f"{f}: invalid JSON"); continue
        wid = w.get("work_id", "")
        rule("W01", bool(re.match(r"^work:[a-z0-9_-]+$", wid)), f"{wid}")
        rule("W02", bool(w.get("title")), f"{wid}: title")
        authors = w.get("authors", [])
        if isinstance(authors, list):
            rule("W03", len(authors) > 0 and all(isinstance(a, dict) and a.get("name") for a in authors), f"{wid}: {len(authors)} authors")
        else:
            rule("W03", False, f"{wid}: authors is {type(authors).__name__}, expected list")
        topics = w.get("topics", [])
        rule("W04", len(topics) >= 1, f"{wid}: {len(topics)} topics")
        tradition = w.get("tradition", [])
        rule("W05", len(tradition) >= 1 or w.get("analysis", {}).get("quality_score") is not None, f"{wid}")
        summary = w.get("analysis", {}).get("summary", "")
        rule("W06", len(summary) >= 10, f"{wid}: summary={len(summary)}c")
        pdf = w.get("assets", {}).get("pdf_path")
        rule("W07", not pdf or os.path.exists(os.path.join(ROOT, pdf)), f"{wid}: pdf={pdf}")
        qs = w.get("analysis", {}).get("quality_score")
        rule("W08", qs is None or qs >= 0.3, f"{wid}: quality={qs}")

# ── Stage 2: Research Objects ──
def audit_ros(single_ro=None):
    ros_dir = os.path.join(ROOT, "content", "research-objects")
    if not os.path.exists(ros_dir): return
    if single_ro:
        dirs = [os.path.join(ros_dir, f"ro-{single_ro.replace('ro:', '')}")]
    else:
        dirs = sorted([os.path.join(ros_dir, d) for d in os.listdir(ros_dir) if d.startswith("ro-")])
    for d in dirs:
        ro_path = os.path.join(d, "ro.json")
        if not os.path.exists(ro_path): continue
        slug = os.path.basename(d)
        try:
            ro = json.load(open(ro_path))
        except: rule("R00", False, f"{slug}: invalid JSON"); continue
        rid = ro.get("ro_id", "")
        rule("R01", bool(re.match(r"^ro:[a-z0-9_-]+$", rid)), f"{rid}")
        rule("R02", bool(ro.get("title")), f"{rid}")
        rule("R03", ro.get("family") in ("thinker-topic", "topic-across-thinkers", "tradition", "theme", "literature"), f"{rid}: family={ro.get('family')}")
        rule("R04", ro.get("status") in ("idea", "draft", "review", "published", "stale"), f"{rid}: status={ro.get('status')}")
        ol = ro.get("summary", {}).get("one_line", "")
        rule("R05", len(ol) <= 200, f"{rid}: one_line={len(ol)}c")
        rule("R06", len(ro.get("summary", {}).get("traditions", [])) >= 1, f"{rid}: traditions")
        sources = ro.get("sources", [])
        rule("R07", len(sources) >= 1, f"{rid}: {len(sources)} sources")
        body = ro.get("body", [])
        rule("R10", len(body) >= 5, f"{rid}: {len(body)} passages")
        # Passage validation
        bad_ids = [p.get("passage_id") for p in body if not re.match(r"^p_\d{3}$", p.get("passage_id", ""))]
        rule("R11", len(bad_ids) == 0, f"{rid}: bad passage_ids: {bad_ids[:3]}")
        empty = [p for p in body if not p.get("text", "").strip()]
        rule("R12", len(empty) == 0, f"{rid}: {len(empty)} empty passages")
        # Source traceability
        source_ids = {s["source_id"] for s in sources}
        body_sources = {p["source_id"] for p in body if p.get("source_id")}
        orphans = body_sources - source_ids
        rule("R13", len(orphans) == 0, f"{rid}: orphan source refs: {orphans}")
        unused = source_ids - body_sources
        active_unused = [s["source_id"] for s in sources if s.get("status") == "active" and s["source_id"] in unused]
        rule("R23", len(active_unused) == 0, f"{rid}: active sources with 0 passages: {active_unused}")
        # Version
        rule("R17", bool(re.match(r"^\d+\.\d+\.\d+$", str(ro.get("current_version", "")))), f"{rid}: version={ro.get('current_version')}")
        # Coverage
        coverage = ro.get("coverage", {})
        rule("R15", len(coverage) > 0, f"{rid}: coverage entries")
        # Source utilization (R21: ≥50% from Tier 1)
        tier1_count = sum(p.get("source_id") in {s["source_id"] for s in sources if s.get("tier") == 1} for p in body if p.get("source_id"))
        pct = tier1_count / len(body) * 100 if body else 0
        rule("R21", pct >= 50, f"{rid}: {pct:.0f}% from Tier 1 sources")

# ── Stage 3: Essays ──
def audit_essays():
    essays_dir = os.path.join(ROOT, "content", "glossary", "essays")
    if not os.path.exists(essays_dir): return
    for f in sorted(os.listdir(essays_dir)):
        if not f.endswith(".json"): continue
        path = os.path.join(essays_dir, f)
        try:
            e = json.load(open(path))
        except: continue
        eid = e.get("id", f.replace(".json", ""))
        rule("E01", bool(re.match(r"^[a-z0-9_-]+$", str(eid))), f"{eid}")
        rule("E02", bool(e.get("title")), f"{eid}")
        rule("E03", e.get("type") in ("thesis_essay", "condensed_source"), f"{eid}: type={e.get('type')}")
        body = e.get("body", [])
        rule("E05", len(body) >= 5, f"{eid}: {len(body)} blocks")
        total_chars = sum(len(b.get("text", "")) for b in body)
        rule("E06", total_chars >= 1000, f"{eid}: {total_chars}c")
        valid_kinds = {"source", "ai", "summary", "art"}
        bad_kinds = [b.get("kind") for b in body if b.get("kind") not in valid_kinds]
        rule("E07", len(bad_kinds) == 0, f"{eid}: bad kinds: {set(bad_kinds)}")
        rule("E08", all(b.get("text", "").strip() for b in body), f"{eid}: empty blocks")
        # RO traceability
        source_blocks = [b for b in body if b.get("kind") == "source"]
        has_trace = all(b.get("ro_passage_id") for b in source_blocks)
        rule("E09", not source_blocks or has_trace, f"{eid}: {len(source_blocks)} source blocks, {sum(1 for b in source_blocks if b.get('ro_passage_id'))} traced")
        rule("E13", bool(e.get("audioUrl")), f"{eid}: audioUrl={bool(e.get('audioUrl'))}")

# ── Stage 4: Storyboards ──
def audit_storyboards():
    sb_dir = os.path.join(ROOT, "content", "publishing", "storyboards")
    if not os.path.exists(sb_dir): return
    for f in sorted(os.listdir(sb_dir)):
        if not f.endswith(".json"): continue
        path = os.path.join(sb_dir, f)
        try:
            s = json.load(open(path))
        except: continue
        eid = s.get("episode_id", f)
        segs = s.get("segments", [])
        rule("S04", len(segs) >= 5, f"{eid}: {len(segs)} segments")
        rule("S06", len(segs) > 0 and segs[0].get("rhetorical_role") == "hook", f"{eid}: first={segs[0].get('rhetorical_role') if segs else 'none'}")
        rule("S07", len(segs) > 0 and segs[-1].get("rhetorical_role") == "closing", f"{eid}: last={segs[-1].get('rhetorical_role') if segs else 'none'}")
        has_quote = any(sg.get("rhetorical_role") == "quote" for sg in segs)
        rule("S08", has_quote, f"{eid}: has_quote={has_quote}")
        all_narr = all(sg.get("narration", "").strip() for sg in segs)
        rule("S09", all_narr, f"{eid}: empty narration")

# ── Stage 5: Visual Assignments ──
def audit_video_assignments():
    vo_dir = os.path.join(ROOT, "content", "video-objects")
    if not os.path.exists(vo_dir): return
    for d in sorted(os.listdir(vo_dir)):
        va_path = os.path.join(vo_dir, d, "visual-assignment.json")
        if not os.path.exists(va_path): continue
        try:
            va = json.load(open(va_path))
        except: continue
        vid = va.get("video_id", d)
        segs = va.get("segments", [])
        rule("V01", bool(vid), f"{vid}")
        valid_types = {"artwork", "quote_card"}
        bad_types = [s.get("type") for s in segs if s.get("type") not in valid_types]
        rule("V03", len(bad_types) == 0, f"{vid}: bad types: {set(bad_types)}")
        art_ids = [s.get("artwork_id") for s in segs if s.get("type") == "artwork"]
        # Check artwork exists
        art_dir = os.path.join(ROOT, "content", "glossary", "art")
        missing_art = [a for a in art_ids if not os.path.exists(os.path.join(art_dir, f"{a}.json"))]
        rule("V04", len(missing_art) == 0, f"{vid}: missing artwork: {missing_art}")
        quotes = [s for s in segs if s.get("type") == "quote_card"]
        rule("V05", all(q.get("quote_text", "").strip() for q in quotes), f"{vid}: empty quote text")

if __name__ == "__main__":
    args = sys.argv[1:]
    json_output = "--json" in args

    if "--stage" in args:
        idx = args.index("--stage") + 1
        stage = args[idx] if idx < len(args) else ""
    elif "--ro" in args:
        idx = args.index("--ro") + 1
        ro = args[idx] if idx < len(args) else ""
        audit_ros(single_ro=ro)
    else:
        # Full audit
        if not args or "works" in args or "all" in args: audit_works()
        if not args or "ros" in args or "all" in args: audit_ros()
        if not args or "essays" in args or "all" in args: audit_essays()
        if not args or "storyboards" in args or "all" in args: audit_storyboards()
        if not args or "videos" in args or "all" in args: audit_video_assignments()

    total = results["passed"] + results["failed"]
    pct = results["passed"] / total * 100 if total else 0

    if json_output:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Factory Audit: {results['passed']}/{total} passed ({pct:.0f}%)")
        print(f"{'='*60}")
        for r in results["rules"]:
            mark = "✅" if r["status"] == "PASS" else "❌"
            print(f"  {mark} {r['code']}: {r['detail'][:80]}")
        if results["failed"] > 0:
            print(f"\n{'!'*60}")
            print(f"{results['failed']} FAILED rules")
            print(f"{'!'*60}")
