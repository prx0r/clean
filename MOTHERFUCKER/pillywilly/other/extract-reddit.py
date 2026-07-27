#!/usr/bin/env python3
import os, json, subprocess, tempfile, time
from datasets import load_dataset

SUBREDDITS = [
    "Tantra", "KashmirShaivism", "shaivism", "Shaktism", "AdvaitaVedanta",
    "hinduism", "Vajrayana", "TibetanBuddhism", "Dzogchen", "kundalini",
    "occult", "magick", "GoldenDawnMagicians", "Quareia", "Hermeticism",
    "Thelema", "Theurgy", "Esotericism", "alchemy", "awakened", "spirituality",
    "nonduality", "Meditation", "streamentry", "TheMindIlluminated",
    "HighStrangeness", "Paranormal", "NDE", "Glitch_in_the_Matrix", "AstralProjection"
]

S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
R2_BASE = "s3://research-datasets/reddit"
BATCH_SIZE = 50000

SUBREDDIT_INFO = {
    "Tantra": {"created": 2008, "role": "specialist"},
    "KashmirShaivism": {"created": 2015, "role": "specialist"},
    "shaivism": {"created": 2013, "role": "specialist"},
    "Shaktism": {"created": 2015, "role": "specialist"},
    "AdvaitaVedanta": {"created": 2011, "role": "practitioner"},
    "hinduism": {"created": 2008, "role": "practitioner"},
    "Vajrayana": {"created": 2009, "role": "specialist"},
    "TibetanBuddhism": {"created": 2008, "role": "practitioner"},
    "Dzogchen": {"created": 2009, "role": "specialist"},
    "kundalini": {"created": 2008, "role": "practitioner"},
    "occult": {"created": 2008, "role": "practitioner"},
    "magick": {"created": 2008, "role": "practitioner"},
    "GoldenDawnMagicians": {"created": 2019, "role": "specialist"},
    "Quareia": {"created": 2016, "role": "specialist"},
    "Hermeticism": {"created": 2013, "role": "specialist"},
    "Thelema": {"created": 2009, "role": "practitioner"},
    "Theurgy": {"created": 2012, "role": "specialist"},
    "Esotericism": {"created": 2012, "role": "specialist"},
    "alchemy": {"created": 2008, "role": "practitioner"},
    "awakened": {"created": 2012, "role": "mass"},
    "spirituality": {"created": 2009, "role": "mass"},
    "nonduality": {"created": 2012, "role": "mass"},
    "Meditation": {"created": 2008, "role": "mass"},
    "streamentry": {"created": 2015, "role": "specialist"},
    "TheMindIlluminated": {"created": 2015, "role": "specialist"},
    "HighStrangeness": {"created": 2013, "role": "narrative"},
    "Paranormal": {"created": 2008, "role": "narrative"},
    "NDE": {"created": 2012, "role": "narrative"},
    "Glitch_in_the_Matrix": {"created": 2013, "role": "narrative"},
    "AstralProjection": {"created": 2009, "role": "narrative"},
}

def save_batch(data, prefix, batch_num):
    import pandas as pd
    df = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        tmp = f.name
    df.to_parquet(tmp, index=False)
    dest = f"{R2_BASE}/{prefix}/batch-{batch_num:04d}.parquet"
    subprocess.run(["aws", "s3", "cp", tmp, dest, "--endpoint-url", S3_ENDPOINT], check=True, capture_output=True)
    os.unlink(tmp)
    print(flush=True)f"  batch-{batch_num:04d}: {len(df)} rows -> {dest}")

def extract_submissions():
    print(flush=True)"=== Submissions ===")
    ds = load_dataset("fddemarco/pushshift-reddit", split="train", streaming=True)
    batch, batch_num, total = [], 0, 0
    start = time.time()
    for row in ds:
        if row["subreddit"] not in SUBREDDITS:
            continue
        batch.append({
            "subreddit": row["subreddit"],
            "role": SUBREDDIT_INFO.get(row["subreddit"], {}).get("role", "unknown"),
            "created_year": SUBREDDIT_INFO.get(row["subreddit"], {}).get("created"),
            "id": row["id"], "author": row["author"],
            "created_utc": row["created_utc"],
            "title": row["title"], "selftext": row["selftext"],
            "score": row["score"], "num_comments": row["num_comments"],
        })
        if len(batch) >= BATCH_SIZE:
            save_batch(batch, "submissions", batch_num)
            total += len(batch); batch = []; batch_num += 1
            elapsed = time.time() - start
            print(flush=True)f"  ... {total} rows in {elapsed:.0f}s")
    if batch:
        save_batch(batch, "submissions", batch_num)
        total += len(batch)
    print(flush=True)f"=== Submissions done: {total} rows ===")

def extract_comments():
    print(flush=True)"=== Comments ===")
    ds = load_dataset("fddemarco/pushshift-reddit-comments", split="train", streaming=True)
    batch, batch_num, total = [], 0, 0
    start = time.time()
    for row in ds:
        if row["subreddit"] not in SUBREDDITS:
            continue
        batch.append({
            "subreddit": row["subreddit"],
            "role": SUBREDDIT_INFO.get(row["subreddit"], {}).get("role", "unknown"),
            "id": row["id"], "author": row["author"],
            "created_utc": row["created_utc"],
            "body": row["body"], "score": row["score"],
            "controversiality": row["controversiality"],
            "link_id": row["link_id"],
        })
        if len(batch) >= BATCH_SIZE:
            save_batch(batch, "comments", batch_num)
            total += len(batch); batch = []; batch_num += 1
            elapsed = time.time() - start
            print(flush=True)f"  ... {total} rows in {elapsed:.0f}s")
    if batch:
        save_batch(batch, "comments", batch_num)
        total += len(batch)
    print(flush=True)f"=== Comments done: {total} rows ===")

if __name__ == "__main__":
    if not S3_ENDPOINT:
        print(flush=True)"ERROR: Set S3_ENDPOINT env var"); exit(1)
    extract_submissions()
    extract_comments()
