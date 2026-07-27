#!/usr/bin/env python3
"""Download BPCC Sanskrit parallel data from all configs that contain san_Deva."""
import os, sys
from datasets import load_dataset
import pandas as pd

DATA_DIR = os.environ.get("DATA_DIR", "/mnt/HC_Volume_106423434/raw/bpcc-sanskrit")
HF_TOKEN = os.environ.get("HF_TOKEN")
os.makedirs(DATA_DIR, exist_ok=True)

CONFIGS = ["comparable", "daily", "nllb-filtered", "bpcc-seed-latest", "bpcc-seed-v1", "bpcc-seed-v2"]

for config in CONFIGS:
    print(f"=== {config} ===", flush=True)
    try:
        ds = load_dataset("ai4bharat/BPCC", config, split="san_Deva", streaming=True, token=True)
        batch = []
        total = 0
        for i, row in enumerate(ds):
            batch.append({"src": row["src"], "tgt": row["tgt"], "source": config})
            if len(batch) >= 10000:
                df = pd.DataFrame(batch)
                path = f"{DATA_DIR}/{config}-{total//10000:04d}.parquet"
                df.to_parquet(path, index=False)
                total += len(batch)
                batch = []
                print(f"  {total} rows", flush=True)
        if batch:
            df = pd.DataFrame(batch)
            path = f"{DATA_DIR}/{config}-{total//10000:04d}.parquet"
            df.to_parquet(path, index=False)
            total += len(batch)
        print(f"  Done: {total} rows", flush=True)
    except Exception as e:
        print(f"  Error: {e}", flush=True)

print(f"\nTotal files: {len(os.listdir(DATA_DIR))}", flush=True)
