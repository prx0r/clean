#!/usr/bin/env python3
import os, time, subprocess, glob

S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
DATA_DIR = "/mnt/HC_Volume_106423434/pushshift/data"

SUBS = "'Tantra','KashmirShaivism','shaivism','Shaktism','AdvaitaVedanta','hinduism'," \
       "'Vajrayana','TibetanBuddhism','Dzogchen','kundalini','occult','magick'," \
       "'GoldenDawnMagicians','Quareia','Hermeticism','Thelema','Theurgy','Esotericism'," \
       "'alchemy','awakened','spirituality','nonduality','Meditation','streamentry'," \
       "'TheMindIlluminated','HighStrangeness','Paranormal','NDE','Glitch_in_the_Matrix','AstralProjection'"

import duckdb
con = duckdb.connect()

# Process one file at a time to keep memory low
files = sorted(glob.glob(f"{DATA_DIR}/RS_*.parquet"))
print(f"=== Submissions: {len(files)} files ===", flush=True)
start = time.time()
total = 0
batch_num = 0

for fpath in files:
    try:
        result = con.execute(f"""
            SELECT subreddit, id, author, created_utc, title, selftext, score, num_comments
            FROM read_parquet('{fpath}')
            WHERE subreddit IN ({SUBS})
        """).fetchdf()
    except Exception as e:
        print(f"  Error {os.path.basename(fpath)}: {e}", flush=True)
        continue

    if len(result) == 0:
        continue

    path = f"/tmp/reddit-batch-{batch_num:04d}.parquet"
    result.to_parquet(path, index=False)
    subprocess.run(["aws", "s3", "cp", path,
        f"s3://research-datasets/reddit/submissions/batch-{batch_num:04d}.parquet",
        "--endpoint-url", S3_ENDPOINT], capture_output=True)
    os.unlink(path)
    total += len(result)
    batch_num += 1
    print(f"  {os.path.basename(fpath)}: {len(result)} rows → batch {batch_num-1:04d} ({total} total, {time.time()-start:.0f}s)", flush=True)

print(f"=== Done: {total} rows in {batch_num} files ===", flush=True)
