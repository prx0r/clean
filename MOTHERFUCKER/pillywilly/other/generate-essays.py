#!/usr/bin/env python3
"""Generate Type B essay JSONs for all existing bridge works that lack them."""
import glob, json, os
from datetime import date

def generate_essay(work_data):
    """Generate a Type B essay from a work JSON."""
    wid = work_data.get('work_id', '').replace('work:', '')
    work_id_short = wid.replace('t2-', '')
    
    pm = work_data.get('phase_mapping', {})
    phase = pm.get('phase', '?')
    phase_name = pm.get('phase_name', 'Bridge')
    bridge_rationale = pm.get('bridge_rationale', 'Bridge paper connecting esoteric/philosophical concepts with mechanistic science.')
    
    # Build phase tag from phase_mapping
    if isinstance(phase, int) and phase > 0:
        phase_tag = f"phase-{phase}"
        phase_tag_concept = f"phase-{phase}"
    else:
        phase_tag = "phase-0"
        phase_tag_concept = "phase-0"
    
    title = work_data.get('title', 'Untitled')
    pub = work_data.get('publication', {})
    year = pub.get('year', '')
    journal = pub.get('journal', pub.get('source', ''))
    ids = work_data.get('identifiers', {})
    pmid = ids.get('pmid', ids.get('pmid', ''))
    doi = ids.get('doi', '')
    
    abstract = work_data.get('assets', {}).get('abstract', '')
    if abstract and len(abstract) > 500:
        abstract = abstract[:500] + '...'
    
    # Build body
    body = [
        {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{phase_name}** with mechanistic science from PubMed/MEDLINE."},
        {"kind": "ai", "text": f"**Bridge rationale:** {bridge_rationale}"},
    ]
    
    # Add abstract summary
    summary_parts = [f"**{title}**"]
    if journal:
        summary_parts.append(journal)
    if year:
        summary_parts.append(f"({year})")
    if pmid:
        summary_parts.append(f"PMID: {pmid}")
    if doi:
        summary_parts.append(f"DOI: {doi}")
    if abstract:
        summary_parts.append(f"{abstract}")
    
    body.append({"kind": "summary", "text": ". ".join(summary_parts)})
    
    essay_slug = f"bridge-{work_id_short}"
    
    essay = {
        "id": essay_slug,
        "type": "type-b-essay",
        "title": f"Bridge Essay: {title[:80]}",
        "source_work": f"work:{wid}",
        "phase": phase_tag,
        "phase_name": phase_name,
        "tags": ["frontier-science", "bridge-paper", phase_tag_concept],
        "body": body,
        "notes": f"Auto-generated from existing work JSON on {date.today().isoformat()}. Phase {phase} ({phase_name})."
    }
    
    return essay, essay_slug

os.makedirs('content/glossary/essays', exist_ok=True)

works = sorted(glob.glob('content/works/t2-*.json'))
generated = 0
skipped = 0
errors = 0

for w_path in works:
    try:
        data = json.load(open(w_path))
        wid = data.get('work_id', '').replace('work:', '')
        work_id_short = wid.replace('t2-', '')
        essay_slug = f"bridge-{work_id_short}"
        essay_path = f'content/glossary/essays/{essay_slug}.json'
        
        if os.path.exists(essay_path):
            # Verify existing essay has required fields
            try:
                existing = json.load(open(essay_path))
                if existing.get('body') and existing.get('source_work'):
                    skipped += 1
                    continue
            except:
                pass  # Corrupted, regenerate
        
        essay, slug = generate_essay(data)
        with open(essay_path, 'w') as f:
            json.dump(essay, f, indent=2)
        generated += 1
    except Exception as e:
        print(f"Error processing {w_path}: {e}")
        errors += 1

print(f"Generated: {generated}, Skipped: {skipped}, Errors: {errors}")
print(f"Total essays now: {len(glob.glob('content/glossary/essays/bridge-*.json'))}")
