#!/usr/bin/env python3
"""
Detect quotes in storyboard narration and generate FableCut project clips for them.

Usage:
  python3 scripts/generate-quote-cards.py --storyboard abhinavagupta-life
  python3 scripts/generate-quote-cards.py --storyboard abhinavagupta-life --preview
  python3 scripts/generate-quote-cards.py --storyboard abhinavagupta-life --project
"""

import json, re, sys, os
from pathlib import Path

ROOT = Path('/root/projects/blog')
STORYBOARDS = ROOT / 'content' / 'publishing' / 'storyboards'
MODULES = ROOT / 'video-templates' / 'modules'

QUOTE_MODULE = json.loads((MODULES / 'quote-card.json').read_text())

def extract_quotes(narration):
    """Extract attributed quotes from narration.
    
    The narration is wrapped in outer quotes (the whole segment is "spoken").
    Inside, attribution quotes use single quotes: 'text' — or text from source.
    We look for these inner attribution quotes.
    """
    quotes = []
    
    # First, strip the outer wrapping quotes if present
    inner = narration.strip()
    if inner.startswith('"') and inner.endswith('"'):
        inner = inner[1:-1]
    
    total_len = len(inner)
    
    # Look for single-quoted attribution quotes: 'text'
    for m in re.finditer(r"'([^']{15,200})'", inner):
        quote_text = m.group(1)
        
        # Must have attribution nearby (wrote, said, wrote that, etc.)
        before = inner[:m.start()].strip()
        after = inner[m.end():].strip()
        
        # Check if preceded by attribution: he wrote: '...'
        has_attribution = bool(re.search(r'(wrote|said|writes|says|wrote that|according to|described|called it|sealed it with)[^:]*:?\s*$', before[-80:], re.I))
        
        # Check if followed by attribution: '...' he wrote
        if not has_attribution:
            has_attribution = bool(re.search(r'^[^,]*?(wrote|said|writes|says|according to|described|called)', after[:80], re.I))
        
        if not has_attribution:
            continue
        
        # Extract attribution source
        attribution = ''
        src_match = re.search(r'(wrote|said|writes|says|according to|described|called it)\s+([A-Z][^,.]+)', before[-120:], re.I)
        if src_match:
            attribution = src_match.group(2).strip()
        
        quotes.append({
            'text': quote_text[:200],
            'attribution': attribution,
            'position': m.start(),
        })
        before = narration[:m.start()].strip()
        after = narration[m.end():].strip()
        attribution = ''
        # Check if attribution follows the quote: "...quote" — Source
        attr_match = re.search(r'[—\-–]\s*(.+?)(?:\.|$)', after[:100])
        if attr_match:
            attribution = attr_match.group(1).strip()
        # Check if attribution precedes: Source wrote, "...quote"
        if not attribution:
            attr_match = re.search(r'(.+?)\s+(wrote|said|writes|says|writes that)[^"]+$', before)
            if attr_match:
                attribution = attr_match.group(1).strip()
        quotes.append({
            'text': quote_text[:200],
            'attribution': attribution,
            'position': m.start(),
        })
    
    # Also try pulling out specific short phrases that are clearly attributed
    # even if not single-quoted: "He wrote that X" -> X is the attribution
    for m in re.finditer(r'(?:wrote|said|writes)\s+that\s+["\u201c]([^"\u201d]{20,200})["\u201d]', inner):
        if not any(q['text'] == m.group(1) for q in quotes):
            quotes.append({
                'text': m.group(1)[:200],
                'attribution': '',
                'position': m.start(),
            })
    
    return quotes

def find_quote_segments(storyboard):
    """Find segments containing quotes and return their information."""
    segments = storyboard.get('segments', [])
    results = []
    for seg in segments:
        narration = seg.get('narration', '')
        quotes = extract_quotes(narration)
        for q in quotes:
            results.append({
                'segment_id': seg.get('segment_id', '?'),
                'segment_label': seg.get('label', ''),
                'quote': q['text'],
                'attribution': q['attribution'],
                'duration_sec': QUOTE_MODULE['duration_sec']['default'],
            })
    return results

def preview(storyboard_name):
    sb_path = STORYBOARDS / f'{storyboard_name}.json'
    if not sb_path.exists():
        print(f'Storyboard not found: {sb_path}')
        return
    
    storyboard = json.loads(sb_path.read_text())
    quotes = find_quote_segments(storyboard)
    
    if not quotes:
        print(f'No quotes found in "{storyboard_name}"')
        return
    
    print(f'\n=== Quotes Found in "{storyboard_name}" ===')
    print(f'Total: {len(quotes)} quote cards to generate\n')
    
    for i, q in enumerate(quotes):
        print(f'  [{i+1}] {q["segment_label"][:40]}')
        print(f'      "{q["quote"][:80]}..."')
        print(f'      — {q["attribution"] or "(no attribution found)"}')
        print(f'      Duration: {q["duration_sec"]}s')
        print()

def generate_fablecut_clips(storyboard_name):
    """Generate quote card clips and inject them into the FableCut project timeline."""
    sb_path = STORYBOARDS / f'{storyboard_name}.json'
    if not sb_path.exists():
        print(f'Storyboard not found: {sb_path}')
        return
    
    storyboard = json.loads(sb_path.read_text())
    quotes = find_quote_segments(storyboard)
    
    if not quotes:
        print(f'No quotes found')
        return
    
    proj_path = Path('/root/projects/FableCut/project.json')
    if not proj_path.exists():
        print(f'No project file found')
        return
    
    proj = json.loads(proj_path.read_text())
    
    # For each quote, create a text clip on V2 (overlay track)
    quote_clips = []
    for i, q in enumerate(quotes):
        # Find what time this segment occurs in the project
        seg_id = q['segment_id']
        a1_clip = next((c for c in proj['clips'] 
                       if c['track'] == 'A1' and seg_id in c.get('mediaId', '')), None)
        if not a1_clip:
            continue
        
        # Create text clip overlay
        quote_clips.append({
            'id': f'c_quote_{i+1:02d}',
            'mediaId': None,
            'kind': 'text',
            'track': 'V2',  # overlay track
            'start': a1_clip['start'],
            'duration': min(q['duration_sec'], a1_clip['duration']),
            'props': {
                'text': f'"{q["quote"]}"',
                'fontSize': QUOTE_MODULE['layout']['quote_text']['size'],
                'color': QUOTE_MODULE['layout']['quote_text']['color'],
                'font': QUOTE_MODULE['layout']['quote_text']['font'],
                'align': 'center',
                'lineHeight': QUOTE_MODULE['layout']['quote_text']['line_height'],
                'bgColor': QUOTE_MODULE['layout']['background']['color'],
                'bgOpacity': QUOTE_MODULE['layout']['background']['opacity'],
                'uppercase': False,
            },
        })
        
        # If attribution exists, add a second text clip below
        if q['attribution']:
            attr_text = f"— {q['attribution']}"
            quote_clips.append({
                'id': f'c_attr_{i+1:02d}',
                'mediaId': None,
                'kind': 'text',
                'track': 'V2',
                'start': a1_clip['start'] + 1.5,  # slight delay after quote
                'duration': min(q['duration_sec'] - 1.5, a1_clip['duration'] - 1.5),
                'props': {
                    'text': attr_text,
                    'fontSize': QUOTE_MODULE['layout']['attribution']['size'],
                    'color': QUOTE_MODULE['layout']['attribution']['color'],
                    'font': QUOTE_MODULE['layout']['attribution']['font'],
                    'align': 'center',
                    'lineHeight': 1.3,
                    'y': 120,  # offset below center
                },
            })
    
    if not quote_clips:
        print('No quote clips could be placed (timing mismatch)')
        return
    
    # Add to project
    existing_quote_count = len([c for c in proj['clips'] if c['id'].startswith('c_quote_') or c['id'].startswith('c_attr_')])
    if existing_quote_count > 0:
        proj['clips'] = [c for c in proj['clips'] if not c['id'].startswith('c_quote_') and not c['id'].startswith('c_attr_')]
    
    proj['clips'].extend(quote_clips)
    proj['revision'] = proj.get('revision', 0) + 1
    
    proj_path.write_text(json.dumps(proj, indent=2))
    print(f'\nAdded {len(quotes)} quote cards ({len(quote_clips)} clips) to project')
    print(f'Revision: {proj["revision"]}')

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print('Usage:')
        print('  python3 scripts/generate-quote-cards.py --storyboard <name> --preview')
        print('  python3 scripts/generate-quote-cards.py --storyboard <name> --project')
        return
    
    storyboard_name = None
    do_preview = '--preview' in sys.argv
    do_project = '--project' in sys.argv
    
    for a in sys.argv[1:]:
        if a.startswith('--storyboard='):
            storyboard_name = a.split('=', 1)[1]
    
    if not storyboard_name:
        print('Provide --storyboard=<name>')
        return
    
    if do_preview or not do_project:
        preview(storyboard_name)
    if do_project:
        generate_fablecut_clips(storyboard_name)

if __name__ == '__main__':
    main()
