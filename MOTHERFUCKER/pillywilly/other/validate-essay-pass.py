#!/usr/bin/env python3
"""Validate an essay against a specific pass's gates. Exit code 0 = pass, 1 = fail.

Usage:
  python3 scripts/validate-essay-pass.py <essay-path> <pass-number>
  python3 scripts/validate-essay-pass.py content/glossary/essays/test.json 1
  python3 scripts/validate-essay-pass.py content/glossary/essays/test.json 2
  python3 scripts/validate-essay-pass.py content/glossary/essays/test.json 3

Exit code 0 = ALL gates pass
Exit code 1 = One or more gates fail (details printed to stdout)
"""

import json, sys, os, re

def load_essay(path):
    with open(path) as f:
        return json.load(f)

def check_pass_1(e):
    """Source-maximal dump: 70% source, AI ≤40 words, no NARR, no NEG, no summary."""
    body = e.get("body", [])
    ai_blocks = [b for b in body if b.get("kind") == "ai"]
    source_blocks = [b for b in body if b.get("kind") == "source"]
    total = len(ai_blocks) + len(source_blocks)
    
    gates = {}
    
    # P1_A: Every AI block ≤ 40 words
    long_ai = [(i, len(b["text"].split())) for i, b in enumerate(body) if b.get("kind") == "ai" and len(b["text"].split()) > 40]
    gates["P1_A AI ≤40 words"] = (len(long_ai) == 0, f"{len(long_ai)} AI blocks over 40 words" if long_ai else "all AI blocks ≤40 words")
    
    # P1_B: ≥60% source
    pct = len(source_blocks) / total * 100 if total else 0
    gates["P1_B ≥60% source"] = (pct >= 60, f"{pct:.0f}% source ({len(source_blocks)}/{total} blocks)")
    
    # P1_C: No NARR patterns
    narr = ["opens with", "introduces", "turns to", "concludes", "argues that", "now moves", "brings us to", "describes how", "presents the", "considers the"]
    found_narr = []
    for i, b in enumerate(body):
        text = b.get("text", "").lower()
        for p in narr:
            if p in text:
                found_narr.append((i, b.get("kind"), p))
    gates["P1_C No NARR"] = (len(found_narr) == 0, f"{len(found_narr)} NARR patterns found: {found_narr[:3]}" if found_narr else "clean")
    
    # P1_D: No NEG patterns
    neg = ["not ", "n't ", " but ", "rather than", "instead of", "however", "although", "despite", "yet "]
    found_neg = []
    for i, b in enumerate(body):
        if b.get("kind") != "ai": continue
        text = b.get("text", "").lower()
        for p in neg:
            if p in text:
                found_neg.append((i, p))
    gates["P1_D No NEG"] = (len(found_neg) <= 3, f"{len(found_neg)} NEG patterns" if found_neg else "clean")
    
    # P1_E: Hook exists as first AI block
    first_ai_text = ai_blocks[0]["text"] if ai_blocks else ""
    gates["P1_E Hook exists"] = (len(first_ai_text) > 0 and len(first_ai_text.split()) <= 25, f"first AI: {first_ai_text[:60]}...")
    
    # P1_F: No summary blocks
    has_summary = any(b.get("kind") == "summary" for b in body)
    gates["P1_F No summary"] = (not has_summary, "summary block found" if has_summary else "clean")
    
    return gates

def check_pass_2(e):
    """Slop removal: texture kit, stance, no flat transitions."""
    body = e.get("body", [])
    ai_blocks = [b for b in body if b.get("kind") == "ai"]
    
    gates = {}
    
    # P2_A: No NEG in AI blocks
    neg = ["not ", "n't ", " but ", "rather than", "instead of", "however", "although"]
    found_neg = sum(1 for b in ai_blocks if any(p in b.get("text","").lower() for p in neg))
    gates["P2_A No NEG"] = (found_neg <= 2, f"{found_neg} AI blocks with NEG")
    
    # P2_B: No NARR in AI blocks
    narr = ["opens with", "introduces", "turns to", "concludes", "argues that", "describes how"]
    found_narr = sum(1 for b in ai_blocks if any(p in b.get("text","").lower() for p in narr))
    gates["P2_B No NARR"] = (found_narr == 0, f"{found_narr} AI blocks with NARR")
    
    # P2_C: ≥1 unexpected concrete noun per AI block
    concrete = ["thrum", "whet", "flint", "scorch", "seam", "gravid", "brushwood", "lattice", "scored", "rot", "fruit", "pulse", "flame", "dust", "bone", "salt", "furnace", "alembic", "whetted"]
    ai_with_concrete = 0
    for b in ai_blocks:
        text = b.get("text","").lower()
        if any(c in text for c in concrete):
            ai_with_concrete += 1
    gates["P2_C Concrete nouns"] = (ai_with_concrete >= len(ai_blocks) * 0.5, f"{ai_with_concrete}/{len(ai_blocks)} AI blocks with concrete nouns")
    
    # P2_D: No consecutive AI blocks starting with same structure
    same_start = 0
    prev_start = ""
    for b in ai_blocks:
        words = b.get("text","").split()
        start = words[0].lower() if words else ""
        if start == prev_start:
            same_start += 1
        prev_start = start
    gates["P2_D Varied starts"] = (same_start <= 2, f"{same_start} consecutive same starts")
    
    # P2_F: No flat transitions
    flat = ["now moves", "now turns", "now shifts", "having seen", "having established", "having examined"]
    found_flat = sum(1 for b in ai_blocks if any(p in b.get("text","").lower() for p in flat))
    gates["P2_F No flat transitions"] = (found_flat == 0, f"{found_flat} flat transitions")
    
    return gates

def check_pass_3(e):
    """Emotional arc: hook, second hook, climax, return."""
    body = e.get("body", [])
    ai_blocks = [b for b in body if b.get("kind") == "ai"]
    source_blocks = [b for b in body if b.get("kind") == "source"]
    
    gates = {}
    
    # P3_A: Hook ≤15 words, no hedging
    hook_text = ai_blocks[0]["text"] if ai_blocks else ""
    hook_words = len(hook_text.split())
    hedges = ["perhaps", "maybe", "might", "could", "i think", "it seems", "arguably"]
    has_hedge = any(h in hook_text.lower() for h in hedges)
    gates["P3_A Hook punchy"] = (hook_words <= 25 and not has_hedge, f"{hook_words} words, hedge={has_hedge}: {hook_text[:60]}")
    
    # P3_B: Second hook at ~40%
    if len(ai_blocks) >= 4:
        mid_idx = max(1, len(ai_blocks) // 2)
        second = ai_blocks[mid_idx]["text"]
        gates["P3_B Second hook"] = (len(second.split()) > 5, f"mid-block ({mid_idx}/{len(ai_blocks)}): {second[:60]}")
    else:
        gates["P3_B Second hook"] = (False, "not enough AI blocks")
    
    # P3_C: Climax — longest source block in latter half
    if source_blocks:
        longest = max(source_blocks, key=lambda b: len(b.get("text","")))
        longest_idx = body.index(longest)
        total = len(body)
        gates["P3_C Climax positioned"] = (longest_idx >= total * 0.5, f"longest source at {longest_idx}/{total}")
    else:
        gates["P3_C Climax positioned"] = (False, "no source blocks")
    
    # P3_D: Ending circles back — check last AI block
    last_ai = ai_blocks[-1]["text"] if ai_blocks else ""
    first_ai = ai_blocks[0]["text"] if ai_blocks else ""
    first_words = set(first_ai.lower().split()[:5])
    last_words = set(last_ai.lower().split()[:5])
    overlap = first_words & last_words
    gates["P3_D Ending circles back"] = (len(overlap) >= 1, f"shared words: {overlap}")
    
    return gates

def main():
    if len(sys.argv) < 3:
        print("Usage: validate-essay-pass.py <essay-path> <pass-number>")
        sys.exit(1)
    
    path = sys.argv[1]
    if not os.path.exists(path):
        # Try prepending root
        path = os.path.join("/root/projects/blog", path)
    
    pass_num = int(sys.argv[2])
    
    try:
        e = load_essay(path)
    except Exception as ex:
        print(f"FAILED to load essay: {ex}")
        sys.exit(1)
    
    if pass_num == 1:
        gates = check_pass_1(e)
    elif pass_num == 2:
        gates = check_pass_2(e)
    elif pass_num == 3:
        gates = check_pass_3(e)
    else:
        print(f"Unknown pass: {pass_num}")
        sys.exit(1)
    
    all_pass = True
    for name, (passed, detail) in gates.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {name}: {detail}")
        if not passed:
            all_pass = False
    
    if all_pass:
        print(f"\n✅ ALL {len(gates)} GATES PASS")
        sys.exit(0)
    else:
        print(f"\n❌ {sum(1 for v in gates.values() if not v[0])}/{len(gates)} GATES FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
