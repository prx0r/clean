#!/usr/bin/env python3
"""Audit current bridge paper collection per phase."""
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

# Count by phase_mapping.phase
by_phase = defaultdict(list)
for w in works:
    pm = w.get('phase_mapping', {})
    phase = pm.get('phase', 0)
    by_phase[phase].append(w)

print('\n=== Per-Phase Counts ===')
for phase in sorted(by_phase.keys()):
    pw = by_phase[phase]
    names = sorted(set(w.get('phase_mapping',{}).get('phase_name','') for w in pw))
    eval_scores = []
    for w in pw:
        ev = w.get('evaluation', '')
        m = re.search(r'Score\s+(\d+)', str(ev))
        if m:
            eval_scores.append(int(m.group(1)))
        elif 'Excellent' in str(ev) or 'Good' in str(ev) or 'Marginal' in str(ev) or 'Low' in str(ev):
            eval_scores.append(0)
    avg = sum(eval_scores)/len(eval_scores) if eval_scores else 0
    high = sum(1 for s in eval_scores if s >= 7)
    print(f'Phase {phase:2d}: {len(pw):3d} papers, names={names[:2]}, avg_score={avg:.1f}, high(>=7)={high:3d}, with_eval={len(eval_scores)}')

# Count PDFs
pdfs = glob.glob('library/frontier/*.pdf')
print(f'\nPDFs in library: {len(pdfs)}')

# Count XMLs
xmls = glob.glob('library/frontier/*.xml') + glob.glob('library/frontier/*.nxml')
print(f'XML/NXML in library: {len(xmls)}')

# Essays
essays = glob.glob('content/glossary/essays/bridge-*.json')
print(f'Essays: {len(essays)}')

# Check which works have pdf_file
with_pdf = sum(1 for w in works if w.get('assets',{}).get('pdf_file'))
no_pdf_but_pmc = 0
no_pdf_no_pmc = 0
for w in works:
    assets = w.get('assets', {})
    ids = w.get('identifiers', {})
    if not assets.get('pdf_file'):
        if ids.get('pmc_id') or ids.get('pmc'):
            no_pdf_but_pmc += 1
        else:
            no_pdf_no_pmc += 1
print(f'\nPDF coverage: {with_pdf} have pdf_file, {no_pdf_but_pmc} have PMC but no PDF, {no_pdf_no_pmc} have no PMC')

# Show the phases that are MISSING or under 50
print('\n=== Phases needing attention ===')
all_phases = list(range(1, 18))
for p in all_phases:
    count = len(by_phase.get(p, []))
    if count < 50:
        names = sorted(set(w.get('phase_mapping',{}).get('phase_name','') for w in by_phase.get(p, [])))
        print(f'Phase {p:2d}: {count:3d} papers (needs 50) names={names}')
    else:
        print(f'Phase {p:2d}: {count:3d} papers ✅ (needs 50)')

# List works with no evaluation score
no_eval = [w for w in works if not w.get('evaluation')]
if no_eval:
    print(f'\nWorks with NO evaluation score: {len(no_eval)}')
    for w in no_eval[:5]:
        print(f'  - {w.get("title","?")[:60]} (phase {w.get("phase_mapping",{}).get("phase","?")})')
