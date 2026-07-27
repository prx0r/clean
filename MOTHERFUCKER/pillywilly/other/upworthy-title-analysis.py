#!/usr/bin/env python3
"""
Upworthy Title Analysis — Causal Title Prior from 32k Headline A/B Tests

Claim: Semantic features (question format, specificity, curiosity gap,
second-person, concreteness) predict which headline wins in a pairwise A/B test.

Falsification: Pairwise classifier does not exceed 0.55 accuracy on holdout set
(baseline: 0.50 for random guessing in pairwise comparison).

Data: Upworthy Research Archive (CC0) — 149k rows across 32k A/B tests.
Each test compares multiple headlines for the same content (eyecatcher_id).
"""

import csv, gzip, io, json, os, re, sys, math
from datetime import datetime
from collections import defaultdict
from itertools import combinations

import boto3
import numpy as np

# ── R2 Config ──────────────────────────────────────────────────────────────────
AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
BUCKET = "research-datasets"
if not all([AWS_KEY, AWS_SECRET, S3_ENDPOINT]):
    print("ERROR: Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_ENDPOINT")
    sys.exit(1)

session = boto3.session.Session(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
s3 = session.client("s3", endpoint_url=S3_ENDPOINT)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = "/root/projects/blog/data/research/upworthy"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ── Feature Extraction ─────────────────────────────────────────────────────────

def extract_features(headline):
    h = headline.strip()
    lower = h.lower()
    words = h.split()
    word_count = len(words)
    char_count = len(h)

    features = {
        "word_count": word_count,
        "char_count": char_count,
        "has_question": 1 if "?" in h else 0,
        "has_colon": 1 if ":" in h else 0,
        "has_dash": 1 if "—" in h or "--" in h or "–" in h else 0,
        "has_exclamation": 1 if "!" in h else 0,
        "has_quotes": 1 if '"' in h or "'" in h else 0,
        "has_number": 1 if bool(re.search(r'\d+', h)) else 0,
        "has_you": 1 if bool(re.search(r'\byou\b', lower)) else 0,
        "has_your": 1 if bool(re.search(r'\byour\b', lower)) else 0,
        "has_this": 1 if bool(re.search(r'\bthis\b', lower)) else 0,
        "has_these": 1 if bool(re.search(r'\bthese\b', lower)) else 0,
        "has_why": 1 if bool(re.search(r'\bwhy\b', lower)) else 0,
        "has_how": 1 if bool(re.search(r'\bhow\b', lower)) else 0,
        "has_what": 1 if bool(re.search(r'\bwhat\b', lower)) else 0,
        "has_not": 1 if bool(re.search(r'\bnot\b', lower) or bool(re.search(r"\bn't\b", lower))) else 0,
        "has_never": 1 if bool(re.search(r'\bnever\b', lower)) else 0,
        "has_every": 1 if bool(re.search(r'\bevery\b', lower)) else 0,
        "has_all": 1 if bool(re.search(r'\ball\b', lower)) else 0,
        "has_just": 1 if bool(re.search(r'\bjust\b', lower)) else 0,
        "has_actually": 1 if bool(re.search(r'\bactually\b', lower)) else 0,
        "has_really": 1 if bool(re.search(r'\breally\b', lower)) else 0,
        "first_word_is_verb": 1 if words and words[0].lower() in {
            "see", "watch", "learn", "find", "discover", "stop", "start",
            "try", "make", "get", "use", "take", "put", "give",
            "ask", "tell", "show", "let", "don't", "do",
        } else 0,
        "first_word_is_question_word": 1 if words and words[0].lower() in {
            "what", "why", "how", "when", "where", "who", "which", "whose",
        } else 0,
        "uppercase_ratio": sum(1 for c in h if c.isupper()) / max(char_count, 1),
    }

    features["curiosity_gap"] = 1 if (
        features["has_why"] or features["has_how"] or
        features["has_question"] or features["has_what"]
    ) else 0

    features["urgency"] = 1 if (
        features["has_exclamation"] or
        bool(re.search(r'\b(now|today|yet|still|already|finally|at last)\b', lower))
    ) else 0

    features["specificity"] = 1 if features["has_number"] or features["has_colon"] else 0

    return features


def feature_vector(f):
    return [
        f["word_count"], f["char_count"],
        f["has_question"], f["has_colon"], f["has_dash"], f["has_exclamation"],
        f["has_quotes"], f["has_number"], f["has_you"], f["has_your"],
        f["has_this"], f["has_why"], f["has_how"], f["has_what"],
        f["has_not"], f["has_never"],
        f["has_every"], f["has_all"],
        f["has_just"], f["has_actually"], f["has_really"],
        f["first_word_is_verb"], f["first_word_is_question_word"],
        f["uppercase_ratio"], f["curiosity_gap"], f["urgency"], f["specificity"],
    ]


FEATURE_NAMES = [
    "word_count", "char_count",
    "has_question", "has_colon", "has_dash", "has_exclamation",
    "has_quotes", "has_number", "has_you", "has_your",
    "has_this", "has_why", "has_how", "has_what",
    "has_not", "has_never",
    "has_every", "has_all",
    "has_just", "has_actually", "has_really",
    "first_word_is_verb", "first_word_is_question_word",
    "uppercase_ratio", "curiosity_gap", "urgency", "specificity",
]


# ── Data Loading ───────────────────────────────────────────────────────────────

def load_dataset(key):
    log(f"Loading {key}...")
    resp = s3.get_object(Bucket=BUCKET, Key=key)
    text = resp["Body"].read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    log(f"  Loaded {len(rows)} rows")
    return rows


def parse_tests(rows):
    """Group rows by clickability_test_id, extract pairwise comparisons."""
    tests = defaultdict(list)
    for r in rows:
        test_id = r.get("clickability_test_id", "").strip()
        if not test_id:
            continue
        try:
            impressions = int(r.get("impressions", 0) or 0)
            clicks = int(r.get("clicks", 0) or 0)
        except (ValueError, TypeError):
            continue
        if impressions < 100:
            continue
        headline = (r.get("headline", "") or "").strip()
        if not headline:
            continue
        tests[test_id].append({
            "headline": headline,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": clicks / max(impressions, 1),
            "winner": r.get("winner", "").strip().lower() == "true",
        })

    # Filter to tests with at least 2 variants and clear winner
    valid_tests = {}
    for test_id, variants in tests.items():
        if len(variants) >= 2:
            winners = [v for v in variants if v["winner"]]
            if winners:
                valid_tests[test_id] = variants

    log(f"  Found {len(valid_tests)} valid tests with >=2 variants and a winner")
    return valid_tests


def build_pairs(tests):
    """Build pairwise comparisons: for each test, all combinations of winner vs loser."""
    pairs = []
    for test_id, variants in tests.items():
        winners = [v for v in variants if v["winner"]]
        losers = [v for v in variants if not v["winner"]]
        for w in winners:
            for l in losers:
                pairs.append({
                    "test_id": test_id,
                    "headline_a": w["headline"],
                    "headline_b": l["headline"],
                    "ctr_a": w["ctr"],
                    "ctr_b": l["ctr"],
                    "label": 1,  # A wins
                })
                pairs.append({
                    "test_id": test_id,
                    "headline_a": l["headline"],
                    "headline_b": w["headline"],
                    "ctr_a": l["ctr"],
                    "ctr_b": w["ctr"],
                    "label": 0,  # B wins (i.e., A loses)
                })
    log(f"  Built {len(pairs)} pairwise comparisons")
    return pairs


# ── Simple Count-Based Model ───────────────────────────────────────────────────

def compute_feature_win_rates(pairs):
    """For each feature, compute how often its presence predicts winning."""
    feature_wins = defaultdict(lambda: {"present_win": 0, "present_total": 0,
                                         "absent_win": 0, "absent_total": 0})

    for p in pairs:
        fa = extract_features(p["headline_a"])
        fb = extract_features(p["headline_b"])

        for name in FEATURE_NAMES:
            va = fa[name]
            vb = fb[name]

            if va > vb:
                feature_wins[name]["present_win"] += 1 if p["label"] == 1 else 0
                feature_wins[name]["present_total"] += 1
                feature_wins[name]["absent_win"] += 1 if p["label"] == 0 else 0
                feature_wins[name]["absent_total"] += 1
            elif vb > va:
                feature_wins[name]["present_win"] += 1 if p["label"] == 0 else 0
                feature_wins[name]["present_total"] += 1
                feature_wins[name]["absent_win"] += 1 if p["label"] == 1 else 0
                feature_wins[name]["absent_total"] += 1

    results = {}
    for name in FEATURE_NAMES:
        dw = feature_wins[name]
        pr = dw["present_win"] / max(dw["present_total"], 1)
        ar = dw["absent_win"] / max(dw["absent_total"], 1)
        lift = pr - ar
        results[name] = {
            "present_win_rate": round(pr, 4),
            "absent_win_rate": round(ar, 4),
            "lift": round(lift, 4),
            "n_present": dw["present_total"],
            "n_absent": dw["absent_total"],
        }

    return results


def simple_predict(pairs, feat_names, lift_map):
    """Predict winner based on feature signs. Each feature votes ±1 based on lift sign."""
    correct = 0
    for p in pairs:
        fa = extract_features(p["headline_a"])
        fb = extract_features(p["headline_b"])
        score = 0
        for feat_name in feat_names:
            va = fa[feat_name]
            vb = fb[feat_name]
            if va > vb:
                score += 1 if lift_map[feat_name]["lift"] > 0 else -1
            elif vb > va:
                score -= 1 if lift_map[feat_name]["lift"] > 0 else -1
        pred = 1 if score > 0 else 0
        if pred == p["label"]:
            correct += 1

    return correct / max(len(pairs), 1)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("Upworthy Title Analysis — Causal Title Prior")
    log("=" * 60)

    # Step 1: Load confirmatory dataset
    rows = load_dataset("blueprint/upworthy/upworthy-archive-confirmatory-packages-03.12.2020.csv")

    # Step 2: Parse into tests
    tests = parse_tests(rows)

    # Step 3: Build pairwise comparisons
    pairs = build_pairs(tests)

    # Step 4: Split into train (80%) and holdout (20%) by test_id
    all_test_ids = list(tests.keys())
    np.random.seed(42)
    np.random.shuffle(all_test_ids)
    split_idx = int(len(all_test_ids) * 0.8)
    train_ids = set(all_test_ids[:split_idx])
    holdout_ids = set(all_test_ids[split_idx:])

    train_pairs = [p for p in pairs if p["test_id"] in train_ids]
    holdout_pairs = [p for p in pairs if p["test_id"] in holdout_ids]

    log(f"\nTrain tests: {len(train_ids)}")
    log(f"Holdout tests: {len(holdout_ids)}")
    log(f"Train pairs: {len(train_pairs)}")
    log(f"Holdout pairs: {len(holdout_pairs)}")

    # Step 5: Compute per-feature win rates on TRAIN only
    feature_results = compute_feature_win_rates(train_pairs)

    # Step 6: Sort by lift
    sorted_feats = sorted(feature_results.items(), key=lambda x: abs(x[1]["lift"]), reverse=True)

    log("\n── Feature Win Rates (sorted by |lift|) ──")
    log(f"{'Feature':<30} {'Present Win':>12} {'Absent Win':>12} {'Lift':>8} {'n_present':>10} {'n_absent':>10}")
    log("-" * 82)
    top_features = []
    for name, res in sorted_feats:
        if res["n_present"] >= 1000:
            top_features.append(name)
        sig = " ***" if abs(res["lift"]) > 0.02 else ""
        log(f"{name:<30} {res['present_win_rate']:>12.4f} {res['absent_win_rate']:>12.4f} {res['lift']:>8.4f}{sig} {res['n_present']:>10} {res['n_absent']:>10}")

    # Step 7: Simple voting classifier
    log("\n── Pairwise Classifier ──")
    train_acc = simple_predict(train_pairs, top_features, feature_results)
    holdout_acc = simple_predict(holdout_pairs, top_features, feature_results)
    log(f"Train accuracy: {train_acc:.4f} (baseline: 0.5000)")
    log(f"Holdout accuracy: {holdout_acc:.4f} (baseline: 0.5000)")

    gate_pass = holdout_acc > 0.55
    log(f"\nGate: {'PASS' if gate_pass else 'FAIL'} (threshold: >0.55, got: {holdout_acc:.4f})")

    # Step 8: Per-feature breakdown — how often does each feature decide?
    log("\n── Feature Decision Impact (how often does this feature differ between A and B?) ──")
    impact = {}
    for name in FEATURE_NAMES:
        count = sum(1 for p in holdout_pairs
                     if extract_features(p["headline_a"])[name] != extract_features(p["headline_b"])[name])
        impact[name] = count / max(len(holdout_pairs), 1)
    sorted_impact = sorted(impact.items(), key=lambda x: x[1], reverse=True)
    log(f"{'Feature':<30} {'Decision %':>12}")
    log("-" * 42)
    for name, pct in sorted_impact[:15]:
        log(f"{name:<30} {pct:>12.4f}")

    # Step 9: Save results
    result = {
        "experiment": "upworthy-title-analysis-v1",
        "timestamp": TIMESTAMP,
        "data_source": "upworthy-archive-confirmatory-packages-03.12.2020.csv",
        "sample": {
            "total_rows": len(rows),
            "valid_tests": len(tests),
            "train_tests": len(train_ids),
            "holdout_tests": len(holdout_ids),
            "train_pairs": len(train_pairs),
            "holdout_pairs": len(holdout_pairs),
        },
        "claim": "Semantic features predict pairwise headline winner above chance",
        "falsification": "Holdout accuracy <= 0.55",
        "results": {
            "holdout_accuracy": round(holdout_acc, 4),
            "train_accuracy": round(train_acc, 4),
            "baseline": 0.50,
            "gate": "PASS" if gate_pass else "FAIL",
            "gate_threshold": 0.55,
        },
        "top_features_by_impact": [
            {"feature": name, "decision_rate": round(pct, 4)}
            for name, pct in sorted_impact[:10]
        ],
        "feature_win_rates": {
            name: res for name, res in sorted_feats[:30]
        },
        "interpretation": {
            "what_it_means": None,
            "what_it_does_NOT_mean": None,
        },
        "limitations": [
            "Upworthy headlines (2013-2015 US clickbait) may not transfer to YouTube documentary titles",
            "Within-experiment comparisons are causally valid, but feature effects may be domain-specific",
            "Simple count-based model doesn't capture feature interactions",
            "Only confirmatory dataset used; holdout and exploratory not yet analyzed",
        ],
        "next_steps": [
            "Test on holdout dataset (upworthy-archive-holdout-packages)",
            "Train logistic regression or pairwise neural ranker",
            "Test feature transfer on own channel's title A/B tests once available",
        ],
        "evidence_state": {
            "design_complete": True,
            "data_quality_passed": True,
            "internal_validation_passed": None,
            "temporal_validation_passed": False,
            "replicated": False,
        },
        "operational_status": "shadow",
    }

    result_path = os.path.join(OUTPUT_DIR, f"upworthy-title-analysis-{TIMESTAMP}.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"\nResults saved to {result_path}")

    # Print summary
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Tests analyzed: {len(tests)}")
    log(f"Pairwise comparisons: {len(pairs)}")
    log(f"Holdout accuracy: {holdout_acc:.4f}")
    log(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    log("")
    log("Top features by lift:")
    for name, res in sorted_feats[:5]:
        if res["n_present"] >= 1000:
            log(f"  {name}: lift={res['lift']:+.4f} (present wins {res['present_win_rate']:.1%})")


if __name__ == "__main__":
    main()
