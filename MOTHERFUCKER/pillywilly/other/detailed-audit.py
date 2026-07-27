#!/usr/bin/env python3
"""Detailed audit of bridge paper collection."""
import glob, json, os, re
from collections import defaultdict

works = []
for w in sorted(glob.glob('content/works/t2-*.json')):
    try:
        data = json.load(open(w))
        works.append(data)
    except Exception as e:
        print(f"Error loading {w}: {e}")

print(f'Total works: {len(works)}')

# Source breakdown
sources = defaultdict(int)
for w in works:
    src = w.get('provenance', {}).get('source', 'unknown')
    sources[src] += 1
print(f'\n=== Sources ===')
for s, c in sorted(sources.items()):
    print(f'  {s}: {c}')

# Evaluation score breakdown
print(f'\n=== Evaluation Format Check (first 10 with evaluation) ===')
count = 0
for w in works:
    ev = w.get('evaluation', '')
    if ev:
        print(f'  {ev[:80]}')
        count += 1
        if count >= 10:
            break

# Show schema versions
schemas = defaultdict(int)
for w in works:
    schemas[w.get('schema_version', 0)] += 1
print(f'\n=== Schema Versions ===')
for s, c in sorted(schemas.items()):
    print(f'  v{s}: {c}')

# Per-phase detailed
print(f'\n=== Per-Phase Paper Titles (sample) ===')
by_phase = defaultdict(list)
for w in works:
    pm = w.get('phase_mapping', {})
    phase = pm.get('phase', 0)
    by_phase[phase].append(w)

# Check if phases use topics array or phase_mapping
has_phase_mapping = sum(1 for w in works if w.get('phase_mapping'))
has_topics = sum(1 for w in works if w.get('topics'))
print(f'\nWorks with phase_mapping: {has_phase_mapping}')
print(f'Works with topics array: {has_topics}')

# Show titles for under-counted phases
for p in [3, 7, 9, 16, 17]:
    pw = by_phase.get(p, [])
    print(f'\n=== Phase {p} ({len(pw)} papers) ===')
    for w in pw[:5]:
        ev = w.get('evaluation', '')
        print(f'  - {w.get("title","?")[:70]} | eval: {ev[:40]}')

# Show the 7 papers with phase=0
print(f'\n=== Phase 0 (no phase mapping) ===')
for w in by_phase.get(0, []):
    src = w.get('provenance',{}).get('source','')
    print(f'  - {w.get("title","?")[:60]} | source={src}')

# Check existing essays
bridge_essays = glob.glob('content/glossary/essays/bridge-*.json')
print(f'\nBridge essays in glossary: {len(bridge_essays)}')
if bridge_essays:
    print(json.dumps(json.load(open(bridge_essays[0])), indent=2)[:500])

# Check PDF coverage per phase
for p in sorted(by_phase.keys()):
    pw = by_phase[p]
    with_pdf = sum(1 for w in pw if w.get('assets',{}).get('pdf_path') or w.get('assets',{}).get('pdf_file'))
    print(f'Phase {p:2d}: {len(pw):3d} works, {with_pdf:3d} with PDF')
