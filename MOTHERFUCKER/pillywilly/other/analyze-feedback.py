#!/usr/bin/env python3
"""Analyze clip feedback to find prompt patterns that work.

Usage:
    python3 scripts/analyze-feedback.py                        # default
    python3 scripts/analyze-feedback.py --min-ratings 10       # require 10+ ratings
"""

import json, sys, re
from collections import Counter, defaultdict

FEEDBACK_FILE = "content/video-objects/feedback-log.json"
CATALOG_FILE = "content/video-objects/prompts-catalog.json"

def load_feedback(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"No feedback found at {path}")
        return []

def analyze(feedback, min_ratings=5):
    ratings = {"Y": [], "T": [], "N": []}
    by_duration = defaultdict(list)
    keyword_hits = defaultdict(list)
    keyword_misses = defaultdict(list)
    issues = Counter()

    for entry in feedback:
        rid = entry.get("rating")
        notes = (entry.get("notes") or "").lower()
        dur = entry.get("duration", 15)
        cid = entry.get("id", "")
        prompt = entry.get("prompt", "")

        ratings[rid].append(cid)
        by_duration[dur].append(rid)

        # Track common issue keywords
        for kw in ["too fast", "wrong colour", "too slow", "jittery", "blurry",
                     "not clay", "camera", "motion", "too dark", "too bright",
                     "flicker", "distorted", "not what", "wrong colour", "color"]:
            if kw in notes:
                issues[kw] += 1

        # Track prompt keywords that correlate with Y/T/N
        prompt_lower = prompt.lower()
        for kw in ["static", "slow", "single", "simple", "dark", "geometric",
                     "figure", "light", "descend", "rise", "pulse", "bloom"]:
            if kw in prompt_lower:
                if rid == "Y":
                    keyword_hits[kw].append(cid)
                else:
                    keyword_misses.setdefault(kw, []).append(cid)

    print("=" * 60)
    print("FEEDBACK ANALYSIS REPORT")
    print("=" * 60)

    total = len(feedback)
    y_count = len(ratings["Y"])
    t_count = len(ratings["T"])
    n_count = len(ratings["N"])
    print(f"\nTotal ratings: {total}")
    print(f"  Y (Yes):          {y_count} ({y_count/total*100:.0f}%)")
    print(f"  T (Tweak):        {t_count} ({t_count/total*100:.0f}%)")
    print(f"  N (No):           {n_count} ({n_count/total*100:.0f}%)")
    print(f"  Approval rate:    {(y_count+t_count)/total*100:.0f}% (Y+T)")

    if total < min_ratings:
        print(f"\n⚠ Need {min_ratings - total} more ratings for reliable patterns.")
        return

    print(f"\n{'─' * 60}")
    print("PATTERNS BY DURATION")
    print(f"{'─' * 60}")
    for dur in sorted(by_duration.keys()):
        rs = by_duration[dur]
        y = rs.count("Y")
        t = rs.count("T")
        n = rs.count("N")
        score = (y * 2 + t) / max(len(rs), 1) * 10
        print(f"  {dur}s:  Y={y}  T={t}  N={n}  score={score:.0f}/20  ({len(rs)} clips)")

    print(f"\n{'─' * 60}")
    print("MOST COMMON ISSUES")
    print(f"{'─' * 60}")
    for issue, count in issues.most_common(10):
        print(f"  '{issue}': {count} mentions")

    print(f"\n{'─' * 60}")
    print("KEYWORDS CORRELATING WITH Y RATINGS")
    print(f"{'─' * 60}")
    for kw in sorted(keyword_hits.keys(), key=lambda k: len(keyword_hits[k]), reverse=True)[:10]:
        hit = len(keyword_hits[kw])
        miss = len(keyword_misses.get(kw, []))
        total_kw = hit + miss
        if total_kw >= 3:
            rate = hit / total_kw * 100
            print(f"  '{kw}': {rate:.0f}% Y rate ({hit}/{total_kw})")

    print(f"\n{'─' * 60}")
    print("RECOMMENDATIONS")
    print(f"{'─' * 60}")
    
    # Find best duration
    if by_duration:
        best_dur = max(by_duration.keys(), 
                      key=lambda d: sum(1 for r in by_duration[d] if r == "Y") / max(len(by_duration[d]), 1))
        print(f"  Best duration: {best_dur}s (highest Y ratio)")

    # Top keywords
    top_kw = sorted(keyword_hits.keys(), key=lambda k: (len(keyword_hits[k]) / max(len(keyword_hits[k]) + len(keyword_misses.get(k, [])), 1), len(keyword_hits[k])), reverse=True)[:3]
    if top_kw:
        print(f"  Include in prompts: {', '.join(top_kw)}")

    # Top issues to fix
    if issues:
        top_issue = issues.most_common(1)[0]
        print(f"  Most common issue to fix: '{top_issue[0]}' ({top_issue[1]} mentions)")
        print(f"  Review prompts that had this issue and adjust.")

    print()

if __name__ == "__main__":
    min_r = 5
    if "--min-ratings" in sys.argv:
        idx = sys.argv.index("--min-ratings")
        min_r = int(sys.argv[idx + 1])
    fb = load_feedback(FEEDBACK_FILE)
    analyze(fb, min_r)
