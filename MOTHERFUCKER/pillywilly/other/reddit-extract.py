#!/usr/bin/env python3
"""Stream-filter Pushshift Reddit for 30 target subreddits. Uploads filtered Parquet to R2."""
import os, sys, time, json
from datasets import load_dataset
import pandas as pd

SUBREDDITS = {
    "Tantra": "specialist", "KashmirShaivism": "specialist", "shaivism": "specialist",
    "Shaktism": "specialist", "AdvaitaVedanta": "practitioner", "hinduism": "practitioner",
    "Vajrayana": "specialist", "TibetanBuddhism": "practitioner", "Dzogchen": "specialist",
    "kundalini": "practitioner", "occult": "practitioner", "magick": "practitioner",
    "GoldenDawnMagicians": "specialist", "Quareia": "specialist", "Hermeticism": "specialist",
    "Thelema": "practitioner", "Theurgy": "specialist", "Esotericism": "specialist",
    "alchemy": "practitioner", "awakened": "mass", "spirituality": "mass",
    "nonduality": "mass", "Meditation": "mass", "streamentry": "specialist",
    "TheMindIlluminated": "specialist", "HighStrangeness": "narrative",
    "Paranormal": "narrative", "NDE": "narrative", "Glitch_in_the_Matrix": "narrative",
    "AstralProjection": "narrative"
}
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
R2_BASE = "s3://research-datasets/reddit"
BATCH_SIZE = 50000

def save_batch(data, prefix, batch_num):
    df = pd.DataFrame(data)
    path = f"/tmp/reddit-{prefix}-{batch_num:04d}.parquet"
    df.to_parquet(path, index=False)
    dest = f"{R2_BASE}/{prefix}/batch-{batch_num:04d}.parquet"
    os.system(f"aws s3 cp {path} {dest} --endpoint-url {S3_ENDPOINT} > /dev/null 2>&1")
    os.unlink(path)
    return len(df)

def extract_submissions():
    print("=== Submissions ===", flush=True)
    ds = load_dataset("fddemarco/pushshift-reddit", split="train", streaming=True, token=True)
    batch, batch_num, total = [], 0, 0
    start = time.time()
    for row in ds:
        sub = row["subreddit"]
        if sub not in SUBREDDITS:
            continue
        batch.append({
            "subreddit": sub, "role": SUBREDDITS[sub],
            "id": row["id"], "author": row["author"],
            "created_utc": row["created_utc"],
            "title": row["title"], "selftext": row["selftext"],
            "score": row["score"], "num_comments": row["num_comments"],
        })
        if len(batch) >= BATCH_SIZE:
            total += save_batch(batch, "submissions", batch_num)
            batch = []; batch_num += 1
            print(f"  {total} rows in {time.time()-start:.0f}s", flush=True)
    if batch:
        total += save_batch(batch, "submissions", batch_num)
    print(f"=== Submissions done: {total} rows ===", flush=True)

def extract_comments():
    print("=== Comments ===", flush=True)
    ds = load_dataset("fddemarco/pushshift-reddit-comments", split="train", streaming=True, token=True)
    batch, batch_num, total = [], 0, 0
    start = time.time()
    for row in ds:
        sub = row["subreddit"]
        if sub not in SUBREDDITS:
            continue
        batch.append({
            "subreddit": sub, "role": SUBREDDITS[sub],
            "id": row["id"], "author": row["author"],
            "created_utc": row["created_utc"],
            "body": row["body"], "score": row["score"],
            "controversiality": row["controversiality"],
            "link_id": row["link_id"],
        })
        if len(batch) >= BATCH_SIZE:
            total += save_batch(batch, "comments", batch_num)
            batch = []; batch_num += 1
            elapsed = time.time() - start
            print(f"  {total} rows in {elapsed:.0f}s", flush=True)
    if batch:
        total += save_batch(batch, "comments", batch_num)
    print(f"=== Comments done: {total} rows ===", flush=True)

if __name__ == "__main__":
    if not S3_ENDPOINT:
        print("ERROR: Set S3_ENDPOINT"); sys.exit(1)
    extract_submissions()
    extract_comments()
    # Save stats
    stats = {"status": "done", "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open("/tmp/reddit-stats.json", "w") as f:
        json.dump(stats, f)
    print("=== Reddit extraction complete ===", flush=True)
