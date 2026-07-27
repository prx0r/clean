#!/usr/bin/env python3
"""RO Monitor — checks all ROs, finds those ready for essay expansion,
and outputs a prioritized queue that Hermes can read.

Run by cron or manually. Outputs to content/factory/ro-queue.json.

Usage:
  python3 scripts/monitor-ros.py              # normal run
  python3 scripts/monitor-ros.py --notify     # also write notification for Hermes
"""

import json, os, re, sys
from datetime import datetime

ROOT = "/root/projects/blog"
ROS_DIR = os.path.join(ROOT, "content", "research-objects")
ESSAYS_DIR = os.path.join(ROOT, "content", "glossary", "essays")
QUEUE_PATH = os.path.join(ROOT, "content", "factory", "ro-queue.json")

def get_existing_essays():
    """Return dict of RO ID -> list of essay IDs from the essay registry."""
    reg_path = os.path.join(ROOT, "content", "factory", "essay-registry.json")
    if os.path.exists(reg_path):
        with open(reg_path) as f:
            reg = json.load(f)
        return reg.get("ro_to_essay", {})
    return {}

def assess_ro(path):
    try:
        r = json.load(open(path))
    except: return None
    
    rid = r.get("ro_id", os.path.basename(os.path.dirname(path)))
    body = r.get("body", [])
    sources = r.get("sources", [])
    status = r.get("status", "draft")
    version = r.get("current_version", "0.0.0")
    family = r.get("family", "?")
    title = r.get("title", "?")
    
    # Skip stubs and already-published
    if status == "stub": return {"id": rid, "ready": False, "reason": "stub", "score": 0, "title": title}
    
    # Calculate readiness score
    score = 0
    reasons = []
    
    if len(body) >= 10:
        score += 3
    elif len(body) >= 7:
        score += 2
    elif len(body) >= 5:
        score += 1
    
    if len(sources) >= 1:
        score += 1
    
    # Version ≥ 0.2.0 suggests it's been revised
    try:
        minor = int(version.split(".")[1])
        if minor >= 2: score += 1
    except: pass
    
    # Check family priority
    high_priority = {"tradition", "thinker-topic", "topic-across-thinkers"}
    if family in high_priority: score += 1
    
    ready = score >= 4
    
    return {
        "id": rid,
        "title": title[:80],
        "passages": len(body),
        "sources": len(sources),
        "version": version,
        "family": family,
        "score": score,
        "ready": ready,
        "reason": "ready" if ready else f"score={score}/6"
    }

def main():
    existing_essays = get_existing_essays()
    ros = []
    
    for d in sorted(os.listdir(ROS_DIR)):
        if not d.startswith("ro-"): continue
        path = os.path.join(ROS_DIR, d, "ro.json")
        if not os.path.exists(path): continue
        ro = assess_ro(path)
        if ro:
            ro["has_essay"] = ro["id"] in existing_essays
            ros.append(ro)
    
    # Sort: ready first (by score), then not ready
    ready = [r for r in ros if r["ready"] and not r["has_essay"]]
    not_ready = [r for r in ros if not r.get("ready") and not r.get("has_essay")]
    already = [r for r in ros if r["has_essay"]]
    
    ready.sort(key=lambda r: -r["score"])
    not_ready.sort(key=lambda r: -r["score"])
    
    queue = {
        "generated": datetime.utcnow().isoformat(),
        "summary": {
            "total_ros": len(ros),
            "ready_for_essay": len(ready),
            "not_ready": len(not_ready),
            "has_essay_already": len(already),
            "stubs": sum(1 for r in ros if r.get("reason") == "stub"),
        },
        "ready_queue": ready,
        "not_ready": not_ready,
        "already_essayed": already[:10],  # sample
    }
    
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)
    
    print(f"RO Queue generated: {len(ready)} ready for essay, {len(not_ready)} not ready, {len(already)} already essayed")
    print()
    if ready:
        print("Top ready ROs:")
        for r in ready[:10]:
            print(f"  [{r['score']}] {r['id']}: {r['title']} ({r['passages']} passages, v{r['version']})")
    
    # Write notification for Hermes if --notify
    if "--notify" in sys.argv and ready:
        notify = {
            "type": "ro_queue_update",
            "count": len(ready),
            "top": [r["id"] for r in ready[:5]],
            "message": f"{len(ready)} ROs ready for essay expansion. Run /write-and-publish on the first one."
        }
        with open(os.path.join(ROOT, "content", "factory", "_hermes-notify.json"), "w") as f:
            json.dump(notify, f, indent=2)
        print(f"\nNotification written for Hermes: {notify['message']}")

if __name__ == "__main__":
    main()
