#!/usr/bin/env python3
"""
Quality improvement: Delete low-scoring papers from weak phases,
then re-run acquisition to fill with better ones.
"""
import glob, json, os, sys

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"

def delete_phase_papers(phase_num, max_to_keep=10):
    """Delete low-scoring papers from a phase, keeping only the best max_to_keep."""
    works = glob.glob(f"{WORKS_DIR}/t2-*.json")
    
    # Find papers in this phase
    phase_papers = []
    for w in works:
        try:
            data = json.load(open(w))
        except:
            continue
        pm = data.get("phase_mapping", {})
        if pm and pm.get("phase") == phase_num:
            eval_text = data.get("evaluation", "")
            # Determine score value
            if "Excellent" in eval_text:
                score = 5
            elif "Good" in eval_text:
                score = 3
            elif "Marginal" in eval_text:
                score = 1
            else:
                score = 0  # Low/Noise
            phase_papers.append((score, w, data))
    
    # Sort by score descending
    phase_papers.sort(key=lambda x: x[0], reverse=True)
    
    # Keep the best max_to_keep
    keep = phase_papers[:max_to_keep]
    delete = phase_papers[max_to_keep:]
    
    print(f"Phase {phase_num}: {len(phase_papers)} total papers")
    print(f"  Keeping: {len(keep)} papers (score >= {keep[-1][0] if keep else 'N/A'})")
    print(f"  Deleting: {len(delete)} papers")
    
    for score, w_path, data in delete:
        title = data.get("title", "?")[:60]
        eval_text = data.get("evaluation", "?")
        slug = os.path.basename(w_path).replace("t2-", "").replace(".json", "")
        essay_path = f"{ESSAYS_DIR}/bridge-{slug}"
        # Also check for pubmed variant
        essay_path2 = f"{ESSAYS_DIR}/bridge-pubmed-{slug.replace('pubmed-', '')}"
        
        print(f"  Delete: [{score}] {title[:60]} ({eval_text[:20]})")
        
        # Delete work JSON
        try:
            os.remove(w_path)
        except:
            pass
        
        # Delete matching essay(s)
        for ep in [essay_path, essay_path2]:
            for ext in [".json"]:
                f = f"{ep}{ext}"
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
    
    return len(phase_papers) - len(keep)  # number deleted

if __name__ == "__main__":
    phases_to_fix = [17, 7, 3, 9, 16]  # Worst quality phases
    for p in phases_to_fix:
        deleted = delete_phase_papers(p, max_to_keep=15)
        if deleted > 0:
            print(f"  → {deleted} papers deleted from Phase {p}")
        print()
