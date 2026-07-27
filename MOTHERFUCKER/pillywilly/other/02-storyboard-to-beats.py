#!/usr/bin/env python3
"""
Apply a video template to expand a storyboard into granular sub-beats,
assign image types, generate FableCut project with animations and music.

Usage:
  python3 scripts/apply-template.py --storyboard abhinavagupta-life --template biography
  python3 scripts/apply-template.py --storyboard abhinavagupta-life --template biography --build-fablecut
  python3 scripts/apply-template.py --list-templates
"""

import json, sys, os
from pathlib import Path

ROOT = Path('/root/projects/blog')
TEMPLATES_DIR = ROOT / 'video-templates'
STORYBOARDS_DIR = ROOT / 'content' / 'publishing' / 'storyboards'
FABLECUT_DIR = Path('/root/projects/FableCut')
MEDIA_DIR = FABLECUT_DIR / 'media'

def list_templates():
    for f in sorted(TEMPLATES_DIR.glob('*.json')):
        t = json.loads(f.read_text())
        print(f'  {t["template_id"]:25s} — {t["name"]} ({t["segments"]} segs, ~{t["target_duration_min"]}min)')

def load_template(name):
    path = TEMPLATES_DIR / f'{name}.json'
    if not path.exists():
        path = TEMPLATES_DIR / f'{name}.json'
    if not path.exists():
        print(f'Template not found: {name}')
        sys.exit(1)
    return json.loads(path.read_text())

def expand_storyboard(storyboard, template):
    """Expand storyboard segments into template sub-beats with image types."""
    segments = storyboard.get('segments', [])
    structure = template['segment_structure']
    
    beats = []
    for i, (seg, struct) in enumerate(zip(segments, structure)):
        seg_text = seg.get('narration', '')
        words = seg_text.split()
        total_words = len(words)
        
        for j, sub in enumerate(struct['sub_beats']):
            # Split narration across sub-beats proportionally
            chunk_size = total_words // len(struct['sub_beats'])
            start_word = j * chunk_size
            end_word = start_word + chunk_size if j < len(struct['sub_beats']) - 1 else total_words
            sub_narration = ' '.join(words[start_word:end_word])
            
            beats.append({
                'segment': i + 1,
                'segment_title': struct['title'],
                'segment_role': struct['role'],
                'sub_beat': j + 1,
                'label': sub['label'],
                'image_type': sub['image_type'],
                'duration_sec': sub['duration_sec'],
                'sfx': sub['sfx'],
                'narration': sub_narration,
                'image_search_terms': template['image_type_map'].get(sub['image_type'], {}).get('search', []),
            })
    
    return beats

def print_beat_plan(beats):
    total_dur = sum(b['duration_sec'] for b in beats)
    print(f'\n=== Beat Plan ===')
    print(f'Total sub-beats: {len(beats)}')
    print(f'Total duration: {total_dur}s ({total_dur/60:.1f} min)')
    print(f'Images needed: {len(beats)} (1 per sub-beat)')
    print()
    
    for b in beats:
        seg_marker = f'SEG {b["segment"]}' if b['sub_beat'] == 1 else '   '
        print(f'  {seg_marker}  {b["segment_title"][:30]:30s} │ {b["label"][:25]:25s} │ {b["duration_sec"]:2d}s │ image: {b["image_type"][:25]:25s} │ search: {", ".join(b["image_search_terms"][:3])}')

def main():
    if '--list-templates' in sys.argv:
        list_templates()
        return
    
    storyboard_name = None
    template_name = 'biography'
    build_fablecut = '--build-fablecut' in sys.argv
    
    for a in sys.argv[1:]:
        if a.startswith('--storyboard='):
            storyboard_name = a.split('=', 1)[1]
        elif a.startswith('--template='):
            template_name = a.split('=', 1)[1]
    
    if not storyboard_name:
        print('Usage: python3 scripts/apply-template.py --storyboard <name> --template <name> [--build-fablecut]')
        print('Templates:')
        list_templates()
        return
    
    # Load inputs
    template = load_template(template_name)
    sb_file = STORYBOARDS_DIR / f'{storyboard_name}.json'
    if not sb_file.exists():
        print(f'Storyboard not found: {sb_file}')
        sys.exit(1)
    storyboard = json.loads(sb_file.read_text())
    
    # Expand
    beats = expand_storyboard(storyboard, template)
    print_beat_plan(beats)
    
    # Save beat plan
    plan_path = STORYBOARDS_DIR / f'{storyboard_name}_beats.json'
    plan_path.write_text(json.dumps(beats, indent=2))
    print(f'\nBeat plan saved to {plan_path}')
    
    if build_fablecut:
        print('\n--build-fablecut: would build FableCut project with:')
        print(f'  - {len(beats)} V1 clips with Ken Burns keyframes')
        print(f'  - {len(beats)} A1 clips with narration audio')
        print(f'  - A2 ambient drone track (entire duration)')
        print(f'  - A3 SFX hits at transition points')
        print(f'  - 0.5s crossfades between all clips')
        print(f'  - Channel filter preset: {template["global"]["filter_preset"]}')

if __name__ == '__main__':
    main()
