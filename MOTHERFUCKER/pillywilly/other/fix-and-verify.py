#!/usr/bin/env python3
"""Fix phase naming inconsistencies and create missing essays."""
import glob, json, os

CW = '/root/projects/blog/content/works'
CE = '/root/projects/blog/content/glossary/essays'

# 1. Normalize phase names in work JSONs
# Phase 9: "Language / Mantra" -> "Language/Mantra"
# Phase 15: "Ecology / Animism" -> "Ecology/Animism"
fixed = 0
for w in glob.glob(f'{CW}/t2-*.json'):
    d = json.load(open(w))
    pm = d.get('phase_mapping', {})
    if pm:
        changed = False
        if pm.get('phase_name') == 'Language / Mantra':
            pm['phase_name'] = 'Language/Mantra'
            changed = True
        if pm.get('phase_name') == 'Ecology / Animism':
            pm['phase_name'] = 'Ecology/Animism'
            changed = True
        if changed:
            with open(w, 'w') as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            fixed += 1
print(f'Fixed phase names: {fixed} works')

# 2. Find works missing essays
work_ids = {}
for w in glob.glob(f'{CW}/t2-*.json'):
    d = json.load(open(w))
    wid = d.get('work_id', '')
    work_ids[wid] = w

essay_source_ids = set()
for e in glob.glob(f'{CE}/*.json'):
    d = json.load(open(e))
    ess = d.get('source_work', '')
    if ess:
        essay_source_ids.add(ess)

missing = [wid for wid in work_ids if wid not in essay_source_ids]
print(f'Works missing essays: {len(missing)}')

# 3. Create missing essays
created = 0
for wid in missing:
    wpath = work_ids[wid]
    d = json.load(open(wpath))
    title = d.get('title', 'Work')
    journal = d.get('publication', {}).get('journal', '')
    year = d.get('publication', {}).get('year', '')
    doi = d.get('identifiers', {}).get('doi', '')
    pmid = d.get('identifiers', {}).get('pmid', '')
    abstract = d.get('assets', {}).get('abstract', '')[:500]
    pm = d.get('phase_mapping', {})
    phase = pm.get('phase', 0)
    phase_name = pm.get('phase_name', 'unknown')
    bridge = pm.get('bridge_rationale', '')
    
    slug = title.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:30]
    
    essay = {
        'id': f'essay-{wid.replace(":", "-")}',
        'type': 'type-b-essay',
        'title': f'Bridge Essay: {title}',
        'source_work': wid,
        'phase': f'phase-{phase}',
        'phase_name': phase_name,
        'concept': bridge,
        'tags': ['frontier-science', 'bridge-paper', f'phase-{phase}'],
        'body': [
            {'kind': 'ai', 'text': f'This bridge paper connects the esoteric/philosophical concept of **{phase_name}** with mechanistic science from PubMed/MEDLINE.'},
            {'kind': 'ai', 'text': f'**Bridge rationale:** {bridge}'},
            {'kind': 'summary', 'text': f'**{title}** - {journal} ({year}). DOI: {doi}. PMID: {pmid}. {abstract}'},
        ],
        'notes': f'Auto-acquired from PubMed/MEDLINE. Phase {phase} ({phase_name}).'
    }
    epath = f'{CE}/essay-{slug}.json'
    if os.path.exists(epath):
        # Avoid duplicates
        epath = f'{CE}/essay-{slug}-{pmid}.json'
    with open(epath, 'w') as f:
        json.dump(essay, f, indent=2, ensure_ascii=False)
    created += 1
    if created <= 5:
        print(f'  Created essay for: {title[:60]}...')

print(f'Created {created} missing essays')

# 4. Final check
work_ids2 = set()
for w in glob.glob(f'{CW}/t2-*.json'):
    d = json.load(open(w))
    work_ids2.add(d.get('work_id', ''))

essay_source_ids2 = set()
for e in glob.glob(f'{CE}/*.json'):
    d = json.load(open(e))
    if d.get('source_work'):
        essay_source_ids2.add(d.get('source_work'))

still_missing = work_ids2 - essay_source_ids2
print(f'Still missing essays: {len(still_missing)}')

# 5. Final phase counts
print('\nFinal phase counts:')
phases = {}
for w in glob.glob(f'{CW}/t2-*.json'):
    d = json.load(open(w))
    pm = d.get('phase_mapping', {})
    p = pm.get('phase', 0) if pm else 0
    pn = pm.get('phase_name', 'none') if pm else 'none'
    key = (p, pn)
    phases[key] = phases.get(key, 0) + 1

for (p, n), c in sorted(phases.items()):
    status = 'OK' if c >= 50 else f'(need {50-c})'
    print(f'  Phase {p:2d} ({n:30s}): {c:3d} {status}')

print(f'\nTotal works: {len(work_ids2)}')
essays_final = len(glob.glob(f'{CE}/*.json'))
print(f'Total essays: {essays_final}')
