#!/usr/bin/env python3
"""Verify final phase counts and work-essay parity."""
import glob, json

works = sorted(glob.glob('/root/projects/blog/content/works/t2-*.json'))
essays = sorted(glob.glob('/root/projects/blog/content/glossary/essays/bridge-*.json'))
pdfs = sorted(glob.glob('/root/projects/blog/library/frontier/t2-*.pdf'))

print(f'Total works: {len(works)}')
print(f'Total essays: {len(essays)}')
print(f'Total PDFs: {len(pdfs)}')

print('\nPhase inventory (by phase_mapping.phase):')
phases = {}
for w in works:
    d = json.load(open(w))
    pm = d.get('phase_mapping', {})
    p = pm.get('phase', 0) if pm else 0
    pn = pm.get('phase_name', 'none') if pm else 'none'
    key = (p, pn)
    phases[key] = phases.get(key, 0) + 1

for (p, n), c in sorted(phases.items()):
    status = 'OK' if c >= 50 else f'(need {50-c})'
    print(f'  Phase {p:2d} ({n:30s}): {c:3d} {status}')

# Check work-essay parity
work_ids = set()
for w in works:
    d = json.load(open(w))
    work_ids.add(d.get('work_id',''))
essay_source_ids = set()
for e in essays:
    d = json.load(open(e))
    essay_source_ids.add(d.get('source_work',''))
missing_essays = work_ids - essay_source_ids
missing_works = essay_source_ids - work_ids
if missing_essays:
    print(f'\nWorks missing essays: {len(missing_essays)}')
if missing_works:
    print(f'\nEssays missing works: {len(missing_works)}')
if not missing_essays and not missing_works:
    print('\nAll works have matching essays')

# Phase-specific PDF counts
print('\nPDFs per phase (top 10):')
phase_pdfs = {}
for w in works:
    d = json.load(open(w))
    pm = d.get('phase_mapping', {})
    p = pm.get('phase', 0) if pm else 0
    pn = pm.get('phase_name', 'none') if pm else 'none'
    pdf = d.get('assets', {}).get('pdf_path')
    if pdf:
        key = (p, pn)
        phase_pdfs[key] = phase_pdfs.get(key, 0) + 1
for (p, n), c in sorted(phase_pdfs.items()):
    total = phases.get((p, n), 0)
    print(f'  Phase {p:2d} ({n:30s}): {c:3d}/{total} with PDFs')
