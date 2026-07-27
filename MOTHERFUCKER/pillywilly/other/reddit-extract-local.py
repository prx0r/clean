#!/usr/bin/env python3
"""Local extraction: filter Pushshift parquet files for 30 target subreddits."""
import os, sys, time, json, glob
import pandas as pd
import pyarrow.parquet as pq

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
DATA_DIR = "/mnt/HC_Volume_106423434/pushshift/data"
BATCH_SIZE = 50000

def save_batch(data, prefix, batch_num):
    df = pd.DataFrame(data)
    path = f"/tmp/reddit-{prefix}-{batch_num:04d}.parquet"
    df.to_parquet(path, index=False)
    os.system(f"aws s3 cp {path} s3://research-datasets/reddit/{prefix}/batch-{batch_num:04d}.parquet --endpoint-url {S3_ENDPOINT} > /dev/null 2>&1")
    os.unlink(path)
    return len(df)

def process_submissions():
    print("=== Submissions ===", flush=True)
    files = sorted(glob.glob(f"{DATA_DIR}/RS_*.parquet"))
    print(f"  {len(files)} files total", flush=True)
    batch, batch_num, total = [], 0, 0
    start = time.time()
    for fpath in files:
        table = pq.read_table(fpath, columns=["subreddit", "id", "author", "created_utc", "title", "selftext", "score", "num_comments"])
        df = table.to_pandas()
        matched = df[df["subreddit"].isin(SUBREDDITS)]
        for _, row in matched.iterrows():
            batch.append({
                "subreddit": row["subreddit"], "role": SUBREDDITS[row["subreddit"]],
                "id": row["id"], "author": row["author"], "created_utc": row["created_utc"],
                "title": row["title"], "selftext": row["selftext"],
                "score": row["score"], "num_comments": row["num_comments"],
            })
            if len(batch) >= BATCH_SIZE:
                total += save_batch(batch, "submissions", batch_num)
                batch, batch_num = [], batch_num + 1
                print(f"  {total} rows so far ({time.time()-start:.0f}s)", flush=True)
        del table, df, matched
    if batch:
        total += save_batch(batch, "submissions", batch_num)
    print(f"=== Submissions done: {total} rows ===", flush=True)

if __name__ == "__main__":
    process_submissions()
    stats = {"status": "done", "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open("/tmp/reddit-stats.json", "w") as f:
        json.dump(stats, f)
