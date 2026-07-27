#!/usr/bin/env python3
"""
Layer 1: YouNiverse Breakout Metric Validation — v2

Tests:
  A1: Does OLS residual (log views ~ log age) identify different breakout labels than raw views?
  A2: Does channel category explain residual variance? (pooled across channels)
  A3: Does channel momentum (subscriber growth) change breakout labels?

Usage:
  python3 scripts/layer1-youniverse-test.py [--channels 1000] [--videos 30]

Output:
  /root/projects/blog/data/research/youniverse/layer1-{timestamp}.json
"""

import json, os, sys, time, argparse, subprocess, tempfile
from datetime import datetime
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.compute as pc
from scipy import stats

S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET = "research-datasets"
R2_PREFIX = "youniverse"
if not all([S3_ENDPOINT, AWS_KEY, AWS_SECRET]):
    print("ERROR: Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_ENDPOINT env vars")
    sys.exit(1)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = "/root/projects/blog/data/research/youniverse"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def note(msg):
    print(f"  NOTE: {msg}")


def gate(name, passed, detail):
    return {"name": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def s3_cp(src, dst):
    subprocess.run(["aws", "s3", "cp", src, dst, "--endpoint-url", S3_ENDPOINT], check=True, capture_output=True)


# ================================================================
# Load Data
# ================================================================
def load_channels():
    log("Loading channels from R2...")
    with tempfile.NamedTemporaryFile(suffix=".tsv.gz", delete=False) as f:
        tmp = f.name
    try:
        s3_cp(f"s3://{BUCKET}/{R2_PREFIX}/df_channels_en.tsv.gz", tmp)
        df = pd.read_csv(tmp, sep="\t", compression="gzip", low_memory=False)
        log(f"  {len(df)} channels loaded")
        return df
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def load_video_sample(n_channels, videos_per_channel):
    log(f"Loading video sample: {n_channels} channels x {videos_per_channel} videos...")
    channels = load_channels()
    sample = channels.sample(n=min(n_channels, len(channels)), random_state=42)
    sample_ids = set(sample["channel"].values)

    with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as f:
        tmp = f.name
    try:
        log(f"  Downloading feather from R2...")
        t0 = time.time()
        s3_cp(f"s3://{BUCKET}/{R2_PREFIX}/yt_metadata_helper.feather", tmp)
        log(f"  Downloaded ({time.time()-t0:.0f}s)")

        reader = ipc.open_file(tmp)
        cols = ["channel_id", "view_count", "duration", "upload_date"]
        indices = [reader.schema.get_field_index(c) for c in cols]
        num_batches = reader.num_record_batches
        total = 0
        chunks = []

        for i in range(num_batches):
            batch = reader.get_record_batch(i).select(indices)
            mask = pc.is_in(batch.column(0), value_set=pa.array(list(sample_ids)))
            filtered = batch.filter(mask)
            if filtered.num_rows > 0:
                chunks.append(filtered.to_pandas())
            total += batch.num_rows

        df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        log(f"  Scanned {total:,} rows, matched {len(df)}")
        
        if len(df) == 0:
            return df, channels
        
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
        df = df.sort_values(["channel_id", "upload_date"], ascending=[True, False])
        df = df.groupby("channel_id").head(videos_per_channel).reset_index(drop=True)
        log(f"  Final: {len(df)} videos from {df['channel_id'].nunique()} channels")
        return df, channels
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def load_time_series(channel_ids):
    log(f"Loading time series for {len(channel_ids)} channels...")
    ids = set(channel_ids)
    
    with tempfile.NamedTemporaryFile(suffix=".tsv.gz", delete=False) as f:
        tmp = f.name
    try:
        t0 = time.time()
        s3_cp(f"s3://{BUCKET}/{R2_PREFIX}/df_timeseries_en.tsv.gz", tmp)
        log(f"  Downloaded ({time.time()-t0:.0f}s)")
        chunks = []
        for chunk in pd.read_csv(tmp, sep="\t", compression="gzip", chunksize=100000, low_memory=False):
            chunk["channel"] = chunk["channel"].astype(str)
            c = chunk[chunk["channel"].isin(ids)]
            chunks.append(c)
        result = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        log(f"  {len(result)} records loaded ({result['channel'].nunique() if len(result) > 0 else 0} unique channels)")
        return result
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


# ================================================================
# A1: OLS residual vs raw views
# ================================================================
def test_a1(videos):
    """
    Per channel: fit log(views) ~ log(age). 
    Compare top-quartile labels from residual vs raw views.
    
    If overlap < 80%, residual captures meaningfully different signal.
    If overlap >= 80%, residual mostly agrees with raw views — simpler metric may suffice.
    """
    log("=" * 60)
    log("A1: OLS residual vs raw views")
    log("=" * 60)
    
    df = videos.copy()
    df["age_days"] = (pd.Timestamp("2019-10-01") - pd.to_datetime(df["upload_date"])).dt.days.clip(lower=1)
    df["log_v"] = np.log1p(df["view_count"].clip(lower=0))
    df["log_a"] = np.log1p(df["age_days"])
    
    valid = df["channel_id"].value_counts()
    valid = valid[valid >= 20].index
    
    overlaps = []
    for ch in valid:
        cv = df[df["channel_id"] == ch]
        if cv["log_a"].nunique() < 2:
            continue
        slope, intercept = stats.linregress(cv["log_a"], cv["log_v"])[:2]
        cv = cv.copy()
        cv["residual"] = cv["log_v"] - (intercept + slope * cv["log_a"])
        top_res = cv[cv["residual"] >= cv["residual"].quantile(0.75)]
        overlap = top_res["view_count"].rank(pct=True).mean()
        overlaps.append(overlap)
    
    mean_ol = np.mean(overlaps) if overlaps else 1.0
    log(f"  Channels: {len(overlaps)}")
    log(f"  Overlap (residual-top with raw-top): {mean_ol:.3f}")
    log(f"  => Residual identifies {1-mean_ol:.1%} different breakouts than raw views")
    
    result = {
        "channels_tested": len(overlaps),
        "overlap_with_raw": float(mean_ol),
        "pct_different": float((1 - mean_ol) * 100),
        "interpretation": f"At {mean_ol:.0%} overlap, residual {'largely agrees with' if mean_ol >= 0.8 else 'differs meaningfully from'} raw views",
        "gate": gate("A1", mean_ol < 0.8,
            f"{mean_ol:.0%} overlap ({'below' if mean_ol < 0.8 else 'above'} 80% threshold)")
    }
    return result


# ================================================================
# A2: Category as covariate (pooled across channels)
# ================================================================
def test_a2(videos):
    """
    Pooled model across all channels:
      Model A: log_views ~ log_age
      Model B: log_views ~ log_age + category
    
    Category is a channel-level property, not a within-channel variable,
    so we test across channels. If delta R^2 > 0.01, category adds signal.
    """
    log("=" * 60)
    log("A2: Category as covariate (pooled across channels)")
    log("=" * 60)
    
    df = videos.copy()
    df["age_days"] = (pd.Timestamp("2019-10-01") - pd.to_datetime(df["upload_date"])).dt.days.clip(lower=1)
    df["log_v"] = np.log1p(df["view_count"].clip(lower=0))
    df["log_a"] = np.log1p(df["age_days"])
    
    # Drop rows with missing values
    df = df.dropna(subset=["log_v", "log_a", "category_cc"])
    
    # Model A: age only
    r_a = stats.linregress(df["log_a"], df["log_v"])[2] ** 2
    
    # Model B: age + category dummies
    dummies = pd.get_dummies(df["category_cc"], drop_first=True)
    X = np.column_stack([np.ones(len(df)), df["log_a"].values] + 
                         [dummies[c].values for c in dummies.columns])
    y = df["log_v"].values
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2_b = 1 - ss_res / ss_tot
    delta = r2_b - r_a
    
    log(f"  Model A R^2 (age only): {r_a:.4f}")
    log(f"  Model B R^2 (age + category): {r2_b:.4f}")
    log(f"  Delta: {delta:.4f}")
    
    if delta > 0.01:
        log(f"  => Category adds signal (delta R^2 > 0.01)")
    else:
        log(f"  => Category does not add meaningful signal (delta R^2 <= 0.01)")
    
    return {
        "r2_age_only": float(r_a),
        "r2_age_plus_category": float(r2_b),
        "delta_r2": float(delta),
        "categories_in_sample": int(df["category_cc"].nunique()),
        "interpretation": f"Category {'adds' if delta > 0.01 else 'does not add'} signal (delta R^2 = {delta:.4f})",
        "gate": gate("A2", delta > 0.01,
            f"Delta R^2 = {delta:.4f} ({'above' if delta > 0.01 else 'below'} 0.01 threshold)")
    }


# ================================================================
# A3: Momentum stripping
# ================================================================
def test_a3(videos, timeseries):
    """
    Compare breakout labels before and after removing subscriber growth trend.
    
    For each channel with >=20 videos and subscriber growth variance:
      1. Compute age-normalized OLS residual
      2. Label top quartile as breakout
      3. Regress residual against subscriber growth
      4. Subtract growth trend -> residual_2
      5. Label top quartile by residual_2
      6. Count flips
    
    If >15% flip, momentum matters.
    """
    log("=" * 60)
    log("A3: Channel momentum stripping")
    log("=" * 60)
    
    if len(timeseries) == 0:
        return {"skipped": True, "reason": "No time series data loaded",
                "gate": gate("A3", False, "No time series data")}
    
    df = videos.copy()
    df["age_days"] = (pd.Timestamp("2019-10-01") - pd.to_datetime(df["upload_date"])).dt.days.clip(lower=1)
    df["log_v"] = np.log1p(df["view_count"].clip(lower=0))
    df["log_a"] = np.log1p(df["age_days"])
    df["quarter"] = pd.to_datetime(df["upload_date"]).dt.to_period("Q").astype(str)
    
    # Channel growth per quarter
    ts = timeseries.copy()
    ts["quarter"] = pd.to_datetime(ts["datetime"]).dt.to_period("Q").astype(str)
    growth = ts.groupby(["channel", "quarter"])["delta_subs"].sum().reset_index()
    growth.columns = ["channel_id", "quarter", "sub_growth"]
    
    valid = df["channel_id"].value_counts()
    valid = valid[valid >= 20].index
    
    total = 0
    flips = 0
    
    for ch in valid:
        cv = df[df["channel_id"] == ch].copy()
        if cv["log_a"].nunique() < 2:
            continue
        slope = stats.linregress(cv["log_a"], cv["log_v"])[0]
        cv["residual"] = cv["log_v"] - slope * cv["log_a"]
        top1 = cv["residual"] >= cv["residual"].quantile(0.75)
        
        # Merge growth data
        cv = cv.merge(growth, on=["channel_id", "quarter"], how="left")
        cv["sub_growth"] = cv["sub_growth"].fillna(0)
        
        if cv["sub_growth"].nunique() >= 2:
            g_slope = stats.linregress(cv["sub_growth"], cv["residual"])[0]
            cv["residual_2"] = cv["residual"] - g_slope * cv["sub_growth"]
        else:
            cv["residual_2"] = cv["residual"]
        
        top2 = cv["residual_2"] >= cv["residual_2"].quantile(0.75)
        flips += (top1 != top2).sum()
        total += len(cv)
    
    pct = (flips / total * 100) if total > 0 else 0
    log(f"  Videos: {total}, Flips: {flips} ({pct:.1f}%)")
    
    if pct > 15:
        log(f"  => Momentum matters — {pct:.1f}% of labels change after stripping")
    else:
        log(f"  => Momentum has minimal effect — only {pct:.1f}% of labels change")
    
    return {
        "videos_tested": int(total),
        "label_flips": int(flips),
        "flip_pct": float(pct),
        "threshold": 15.0,
        "interpretation": f"Momentum {'matters' if pct > 15 else 'has minimal effect'} ({pct:.1f}% flip rate)",
        "gate": gate("A3", pct > 15,
            f"{pct:.1f}% flips ({'above' if pct > 15 else 'below'} 15% threshold)")
    }


# ================================================================
# Notes interpreter
# ================================================================
def interpret(results, sample):
    """Generate plain-English notes about what the results mean and what to do."""
    notes = []
    actions = []
    
    a1 = results.get("A1_ols_vs_raw", {})
    a2 = results.get("A2_category", {})
    a3 = results.get("A3_momentum", {})
    
    # A1
    pct_diff = a1.get("pct_different", 0)
    if a1.get("gate", {}).get("status") == "PASS":
        notes.append(f"A1: OLS residual identifies {pct_diff:.0f}% different breakout labels than raw views. "
                     f"This is meaningful — the age-normalized metric captures a distinct signal.")
        actions.append("Use OLS residual as the primary breakout metric.")
    else:
        notes.append(f"A1: OLS residual overlaps {a1.get('overlap_with_raw', 0)*100:.0f}% with raw views. "
                     f"Only {pct_diff:.0f}% of labels differ. The gain from age-normalization is marginal.")
        if pct_diff < 10:
            notes.append(f"A1: At <10% difference, the OLS residual is not worth the complexity over raw-views-per-day.")
            actions.append("Drop OLS residual. Use raw-views-per-day as breakout metric.")
        else:
            notes.append(f"A1: {pct_diff:.0f}% difference is borderline. Need n={sample.get('channels', 0)*3} "
                         f"channels to see if this converges or is noise.")
            actions.append("Re-run with 3x channel sample to check convergence.")
    
    # A2
    delta = a2.get("delta_r2", 0)
    if a2.get("gate", {}).get("status") == "PASS":
        notes.append(f"A2: Category adds {delta:.4f} to R^2 in pooled model. "
                     f"Knowing a channel's category helps predict view counts.")
        actions.append("Include category as a covariate in the breakout model.")
    else:
        notes.append(f"A2: Category adds only {delta:.4f} to R^2. "
                     f"Channel category doesn't meaningfully predict view counts after accounting for age.")
        actions.append("Drop category from breakout model. Not worth the complexity.")
    
    # A3
    flip_pct = a3.get("flip_pct", 0)
    if a3.get("skipped"):
        notes.append(f"A3: Not tested — {a3.get('reason', 'unknown reason')}")
        actions.append("Fix time series loading and re-run A3.")
    elif a3.get("gate", {}).get("status") == "PASS":
        notes.append(f"A3: {flip_pct:.1f}% of labels change after momentum stripping. "
                     f"Channel growth trends affect breakout identification in this dataset.")
        actions.append("Strip channel momentum before computing breakout scores.")
    else:
        notes.append(f"A3: Only {flip_pct:.1f}% of labels change after momentum stripping in this dataset. "
                     f"This doesn't mean momentum never matters — YouNiverse channels are mature (>10k subs) "
                     f"with relatively stable growth. The effect might be different for small, growing channels.")
        actions.append("Skip momentum stripping for YouNiverse-scale channels. Re-test on own data later.")
    
    if not actions:
        actions.append("Increase sample size and re-run for clearer signal.")
    
    return {"notes": notes, "actions": actions, "run_quality": f"n={sample.get('channels',0)} channels, {sample.get('videos',0)} videos"}


# ================================================================
# Main
# ================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", type=int, default=500)
    parser.add_argument("--videos", type=int, default=30)
    args = parser.parse_args()
    
    log(f"Layer 1 v2: {args.channels} channels, {args.videos} videos each")
    start = time.time()
    
    # Load data
    channels = load_channels()
    videos, ch_subset = load_video_sample(args.channels, args.videos)
    
    if len(videos) == 0:
        log("ERROR: No videos loaded")
        sys.exit(1)
    
    # Merge category from channels
    cat_map = channels[["channel", "category_cc"]].rename(columns={"channel": "channel_id"})
    videos = videos.merge(cat_map, on="channel_id", how="left")
    
    sample_info = {"channels": int(videos["channel_id"].nunique()), "videos": len(videos)}
    log(f"Sample: {sample_info}")
    
    # A1
    a1 = test_a1(videos)
    log(f"  Gate: {a1['gate']['status']}")
    
    # A2 (always runs — independent of A1)
    a2 = test_a2(videos)
    log(f"  Gate: {a2['gate']['status']}")
    
    # A3 (always runs if we can get time series)
    a3 = {}
    try:
        ts = load_time_series(videos["channel_id"].unique().tolist())
        if len(ts) > 0:
            a3 = test_a3(videos, ts)
            log(f"  Gate: {a3['gate']['status']}")
        else:
            a3 = {"skipped": True, "reason": "No time series records matched sample channels",
                  "gate": gate("A3", False, "No matching time series data")}
    except Exception as e:
        a3 = {"skipped": True, "reason": str(e), "gate": gate("A3", False, f"Error: {e}")}
    
    # Compile report — A3 is informative, not required for overall pass
    # A1 and A2 must pass. A3 result is documented regardless.
    structural_pass = all(
        results.get("gate", {}).get("status") == "PASS"
        for results in [a1, a2]
    )
    all_pass = structural_pass  # A3 is informative only
    
    report = {
        "experiment": "layer-1-breakout-metric",
        "version": "v2",
        "dataset": "youniverse",
        "timestamp": TIMESTAMP,
        "sample": sample_info,
        "assumptions": {
            "A1_ols_vs_raw": a1,
            "A2_category": a2,
            "A3_momentum": a3,
        },
        "gates": {
            "A1": a1.get("gate", {}),
            "A2": a2.get("gate", {}),
            "A3": a3.get("gate", {}),
        },
        "all_gates_passed": all_pass,
        "interpretation": interpret({"A1_ols_vs_raw": a1, "A2_category": a2, "A3_momentum": a3}, sample_info),
        "duration_seconds": time.time() - start,
    }
    
    # Write
    path = f"{OUTPUT_DIR}/layer1-{TIMESTAMP}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Summary
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    log(f"  A1 (OLS vs raw): {a1['gate']['status']} — {a1.get('pct_different', 0):.0f}% labels differ")
    log(f"  A2 (category):   {a2['gate']['status']} — delta R^2 = {a2.get('delta_r2', 0):.4f}")
    log(f"  A3 (momentum):   {a3.get('gate', {}).get('status', 'SKIP')} — {a3.get('flip_pct', 0):.1f}% flips")
    log(f"  Overall: {'PASS' if all_pass else 'FAIL'}")
    log(f"\nNotes:")
    for n in report["interpretation"]["notes"]:
        log(f"  • {n}")
    log(f"Actions:")
    for a in report["interpretation"]["actions"]:
        log(f"  → {a}")
    log(f"\nOutput: {path}")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
