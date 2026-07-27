#!/usr/bin/env python3
"""Register an essay → RO mapping. Called after each essay is written.
Ensures Hermes never writes duplicate essays from the same RO.

Usage:
  python3 scripts/register-essay.py <ro_id> <essay_id>
  python3 scripts/register-essay.py ro:death-systems-convergence you-died-already
  python3 scripts/register-essay.py --check <ro_id>   # returns true/false
"""

import json, os, sys

ROOT = "/root/projects/blog"
REGISTRY_PATH = os.path.join(ROOT, "content", "factory", "essay-registry.json")

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {"essays": [], "ro_to_essay": {}}

def save_registry(reg):
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(reg, f, indent=2)

def register(ro_id, essay_id):
    reg = load_registry()
    if ro_id not in reg["ro_to_essay"]:
        reg["ro_to_essay"][ro_id] = []
    if essay_id not in reg["ro_to_essay"][ro_id]:
        reg["ro_to_essay"][ro_id].append(essay_id)
    # Also update the RO's outputs[] field
    ro_dir = ro_id.replace("ro:", "ro-")
    ro_path = os.path.join(ROOT, "content", "research-objects", ro_dir, "ro.json")
    if os.path.exists(ro_path):
        with open(ro_path) as f:
            ro = json.load(f)
        if "outputs" not in ro:
            ro["outputs"] = []
        # Check if this essay is already listed
        existing = [o for o in ro["outputs"] if o.get("output_id") == essay_id]
        if not existing:
            ro["outputs"].append({
                "output_id": essay_id,
                "type": "essay",
                "ro_version": ro.get("current_version", "?"),
                "published_at": None
            })
            with open(ro_path, "w") as f:
                json.dump(ro, f, indent=2)
    reg["essays"].append({"ro_id": ro_id, "essay_id": essay_id})
    save_registry(reg)
    print(f"Registered: {ro_id} → {essay_id}")
    return True

def check(ro_id):
    reg = load_registry()
    return ro_id in reg["ro_to_essay"] and len(reg["ro_to_essay"][ro_id]) > 0

def list_unused_ros(ros_list):
    """Given a list of RO IDs, return those without essays."""
    reg = load_registry()
    unused = []
    for ro_id in ros_list:
        if ro_id not in reg["ro_to_essay"] or len(reg["ro_to_essay"][ro_id]) == 0:
            unused.append(ro_id)
    return unused

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 scripts/register-essay.py <ro_id> <essay_id>  # register")
        print("  python3 scripts/register-essay.py --check <ro_id>     # check")
        print("  python3 scripts/register-essay.py --unused <ro_id1> <ro_id2> ...  # filter")
        sys.exit(1)
    
    if sys.argv[1] == "--check":
        result = check(sys.argv[2])
        print(json.dumps({"ro_id": sys.argv[2], "has_essay": result}))
    elif sys.argv[1] == "--unused":
        unused = list_unused_ros(sys.argv[2:])
        print(json.dumps({"unused": unused}))
    else:
        register(sys.argv[1], sys.argv[2])
