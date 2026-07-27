#!/usr/bin/env python3
"""
Gold Standard Video Templates.

Capture a high-quality FableCut project as a reusable "gold standard" template,
then apply it to new storyboards to reproduce the same pacing, structure, and
animation patterns.

Usage:
  # Capture the current FableCut project as a gold standard
  python3 scripts/gold-standard.py --capture --name abhinavagupta-v1

  # List saved gold standards
  python3 scripts/gold-standard.py --list

  # Apply a gold standard to a new storyboard
  python3 scripts/gold-standard.py --apply abhinavagupta-v1 --storyboard new-storyboard

  # Preview what a gold standard looks like
  python3 scripts/gold-standard.py --show abhinavagupta-v1
"""

import json, sys, shutil
from pathlib import Path

ROOT = Path('/root/projects/blog')
GOLD_DIR = ROOT / 'video-templates' / 'gold-standards'
STORYBOARDS = ROOT / 'content' / 'publishing' / 'storyboards'
FABLECUT_DIR = Path('/root/projects/FableCut')
PROJECT_FILE = FABLECUT_DIR / 'project.json'
MEDIA_DIR = FABLECUT_DIR / 'media'

GOLD_DIR.mkdir(parents=True, exist_ok=True)

def capture(name):
    """Capture the current FableCut project as a gold standard template."""
    if not PROJECT_FILE.exists():
        print(f'No project file at {PROJECT_FILE}')
        return False
    
    proj = json.loads(PROJECT_FILE.read_text())
    v1 = [c for c in proj['clips'] if c['track'] == 'V1']
    a1 = [c for c in proj['clips'] if c['track'] == 'A1']
    
    # Extract the structural blueprint
    gold = {
        'name': name,
        'captured_from': proj.get('name', 'unknown'),
        'captured_at': str(Path(__file__).stat().st_mtime),
        
        # Structural fingerprint
        'num_segments': len(a1),
        'num_sub_beats': len(v1),
        'total_duration_sec': round(max((c.get('start',0) + c.get('duration',0)) for c in proj['clips'])),
        
        # Pacing fingerprint: how long each V1 clip lasts
        'pacing': [{
            'order': i,
            'duration_sec': round(c.get('duration', 0), 1),
            'start_sec': round(c.get('start', 0), 1),
            'media_type': _detect_media_type(c, proj),
        } for i, c in enumerate(v1)],
        
        # Animation fingerprint: which Ken Burns styles were used
        'animation_sequence': [_extract_ken_burns(c) for c in v1],
        
        # Module distribution
        'module_counts': _count_modules(v1, proj),
        
        # Image type distribution (what kinds of images were used)
        'image_type_pattern': _extract_image_pattern(v1, proj),
        
        # Global settings
        'global': {
            'width': proj.get('width', 1280),
            'height': proj.get('height', 720),
            'fps': proj.get('fps', 25),
            'background': proj.get('background', '#000'),
            'filter_preset': _detect_filter(proj),
        },
        
        # Music/SFX tracks
        'audio_tracks': _extract_audio_tracks(proj),
    }
    
    # Save
    path = GOLD_DIR / f'{name}.json'
    path.write_text(json.dumps(gold, indent=2))
    print(f'✅ Gold standard saved: {path}')
    print(f'   Name: {name}')
    print(f'   Captured from: {gold["captured_from"]}')
    print(f'   Segments: {gold["num_segments"]}, Sub-beats: {gold["num_sub_beats"]}')
    print(f'   Duration: {gold["total_duration_sec"]}s ({gold["total_duration_sec"]/60:.1f}min)')
    print(f'   Module breakdown: {json.dumps(gold["module_counts"])}')
    return True

def _detect_media_type(clip, proj):
    """Detect if a clip is image, quote card, video, etc."""
    media = next((m for m in proj['media'] if m['id'] == clip.get('mediaId')), None)
    if not media:
        if clip.get('kind') == 'text':
            return 'quote_card'
        return 'unknown'
    return media.get('kind', 'unknown')

def _extract_ken_burns(clip):
    """Extract the Ken Burns style from a clip's keyframes."""
    kf = clip.get('keyframes', {})
    scale = kf.get('scale', [])
    if not scale:
        return 'static'
    
    start_v = scale[0].get('v', 1.0)
    end_v = scale[-1].get('v', 1.0)
    
    x = kf.get('x', [])
    y = kf.get('y', [])
    pan_x = x[-1].get('v', 0) - x[0].get('v', 0) if len(x) > 1 else 0
    pan_y = y[-1].get('v', 0) - y[0].get('v', 0) if len(y) > 1 else 0
    
    if start_v == end_v:
        if abs(pan_x) > 15:
            return 'pan_across'
        return 'static'
    
    if end_v > start_v:
        if abs(pan_x) > 10:
            return 'zoom_in_right' if pan_x > 0 else 'zoom_in_left'
        if abs(pan_y) > 5:
            return 'zoom_in_up'
        if end_v - start_v > 0.15:
            return 'push_in_fast'
        return 'zoom_in_slow'
    
    if start_v > end_v:
        if abs(pan_y) > 5:
            return 'pull_back_up'
        return 'zoom_out'
    
    return 'custom'

def _count_modules(clips, proj):
    """Count how many of each module type were used."""
    counts = {'full_bleed_art': 0, 'quote_card': 0, 'portrait_focus': 0, 'detail_zoom': 0, 'other': 0}
    for c in clips:
        mt = _detect_media_type(c, proj)
        if mt == 'quote_card':
            counts['quote_card'] += 1
        elif mt == 'image':
            # Rough classification by duration and position
            dur = c.get('duration', 0)
            start = c.get('start', 0)
            if dur <= 12:
                counts['detail_zoom'] += 1
            elif start < 30:  # near beginning
                counts['full_bleed_art'] += 1
            else:
                counts['portrait_focus'] += 1
        else:
            counts['other'] += 1
    return counts

def _extract_image_pattern(clips, proj):
    """Extract the sequence of image types used."""
    pattern = []
    for c in clips:
        media = next((m for m in proj['media'] if m['id'] == c.get('mediaId')), None)
        if media:
            pattern.append({
                'name': media.get('name', '?'),
                'duration': c.get('duration', 0),
                'start': c.get('start', 0),
            })
    return pattern

def _detect_filter(proj):
    """Detect the filter preset used across clips."""
    for c in proj['clips']:
        fp = c.get('props', {}).get('filterPreset', '')
        if fp:
            return fp
    return 'none'

def _extract_audio_tracks(proj):
    """Extract information about non-narration audio tracks."""
    tracks = []
    audio_clips = [c for c in proj['clips'] if c['track'] not in ('A1', 'V1', 'V2')]
    if audio_clips:
        track_ids = set(c['track'] for c in audio_clips)
        for tid in sorted(track_ids):
            tc = [c for c in audio_clips if c['track'] == tid]
            tracks.append({
                'track': tid,
                'num_clips': len(tc),
                'total_duration': round(sum(c.get('duration', 0) for c in tc)),
            })
    return tracks

def list_gold():
    """List saved gold standards."""
    files = sorted(GOLD_DIR.glob('*.json'))
    if not files:
        print('No gold standards saved yet.')
        print('  Create one: python3 scripts/gold-standard.py --capture --name my-template')
        return
    
    print(f'Gold Standards ({len(files)}):')
    for f in files:
        g = json.loads(f.read_text())
        print(f'  {g["name"]:30s} │ {g["num_sub_beats"]:2d} beats │ {g["total_duration_sec"]}s │ {g["captured_from"][:40]}')

def show(name):
    """Show the structure of a gold standard."""
    path = GOLD_DIR / f'{name}.json'
    if not path.exists():
        print(f'Gold standard "{name}" not found')
        list_gold()
        return
    
    g = json.loads(path.read_text())
    print(f'\n{"="*60}')
    print(f'Gold Standard: {g["name"]}')
    print(f'{"="*60}')
    print(f'Captured from: {g["captured_from"]}')
    print(f'Duration: {g["total_duration_sec"]}s ({g["total_duration_sec"]/60:.1f} min)')
    print(f'Sub-beats: {g["num_sub_beats"]}')
    print(f'Segments: {g["num_segments"]}')
    print(f'Filter: {g["global"]["filter_preset"]}')
    print(f'Background: {g["global"]["background"]}')
    print(f'\nModule counts: {json.dumps(g["module_counts"], indent=2)}')
    print(f'\nPacing pattern ({len(g["pacing"])} beats):')
    print(f'  Min duration: {min(b["duration_sec"] for b in g["pacing"]):.0f}s')
    print(f'  Max duration: {max(b["duration_sec"] for b in g["pacing"]):.0f}s')
    print(f'  Avg duration: {sum(b["duration_sec"] for b in g["pacing"])/len(g["pacing"]):.0f}s')
    print(f'\nAnimation sequence ({len(g["animation_sequence"])} beats):')
    styles = [a['style'] for a in g['animation_sequence']]
    from collections import Counter
    style_counts = Counter(styles)
    for style, count in style_counts.most_common():
        print(f'  {style}: {count}x')
    
    if g.get('audio_tracks'):
        print(f'\nAudio tracks:')
        for t in g['audio_tracks']:
            print(f'  {t["track"]}: {t["num_clips"]} clips, {t["total_duration"]}s total')

def apply_gold(gold_name, storyboard_name):
    """Apply a gold standard's structure to a new storyboard."""
    gold_path = GOLD_DIR / f'{gold_name}.json'
    sb_path = STORYBOARDS / f'{storyboard_name}.json'
    
    if not gold_path.exists():
        print(f'Gold standard "{gold_name}" not found')
        return
    if not sb_path.exists():
        print(f'Storyboard "{storyboard_name}" not found')
        return
    
    gold = json.loads(gold_path.read_text())
    storyboard = json.loads(sb_path.read_text())
    segments = storyboard.get('segments', [])
    
    # Calculate how to distribute the gold standard's pacing across new content
    gold_beats = len(gold['pacing'])
    new_segments = len(segments)
    beats_per_segment = max(2, gold_beats // max(new_segments, 1))
    
    # Build the beat plan by matching gold pacing pattern
    beats = []
    anim_idx = 0
    for seg_idx, seg in enumerate(segments):
        for beat_idx in range(beats_per_segment):
            # If we've exhausted the gold animation cycle, loop
            gold_idx = anim_idx % gold_beats
            gold_beat = gold['pacing'][gold_idx]
            gold_anim = gold['animation_sequence'][gold_idx]
            
            beats.append({
                'segment': seg_idx + 1,
                'segment_title': seg.get('label', ''),
                'segment_role': seg.get('rhetorical_role', ''),
                'sub_beat': beat_idx + 1,
                'duration_sec': gold_beat['duration_sec'],
                'animation_style': gold_anim['style'],
                'gold_reference': gold_idx,
            })
            anim_idx += 1
    
    # Print the plan
    print(f'\n=== Applied Gold Standard "{gold_name}" → "{storyboard_name}" ===')
    print(f'Gold had {gold_beats} beats, new video has {len(beats)} beats')
    print(f'Using same pacing pattern and animation sequence\n')
    
    for b in beats[:10]:
        print(f'  SEG {b["segment"]} beat {b["sub_beat"]}: {b["duration_sec"]:2d}s │ {b["animation_style"][:20]:20s} │ {b["segment_title"][:30]}')
    if len(beats) > 10:
        print(f'  ... and {len(beats) - 10} more')
    
    # Save beat plan
    plan_path = STORYBOARDS / f'{storyboard_name}_gold_{gold_name}.json'
    plan_path.write_text(json.dumps(beats, indent=2))
    print(f'\nBeat plan saved to {plan_path}')

def publish_video(name):
    """Save the current video as a published package with all assets."""
    import shutil
    from datetime import datetime
    
    if not PROJECT_FILE.exists():
        print(f'No project file at {PROJECT_FILE}')
        return False
    
    proj = json.loads(PROJECT_FILE.read_text())
    video_title = proj.get('name', 'untitled').lower().replace(' ', '-')[:40]
    slug = f'{name or video_title}-{datetime.now().strftime("%Y%m%d")}'
    
    pub_dir = ROOT / 'content' / 'publishing' / 'videos' / slug
    pub_dir.mkdir(parents=True, exist_ok=True)
    
    print(f'📦 Publishing video: {proj.get("name", "?")}')
    print(f'   → {pub_dir}')
    
    # 1. Save project.json
    (pub_dir / 'project.json').write_text(json.dumps(proj, indent=2))
    print(f'   ✅ project.json')
    
    # 2. Copy all media files
    media_dir = pub_dir / 'media'
    media_dir.mkdir(exist_ok=True)
    media_copied = 0
    for m in proj['media']:
        src_path = m.get('src', '')
        fname = src_path.split('/')[-1] or m.get('name', '')
        src_file = MEDIA_DIR / fname
        if src_file.exists():
            shutil.copy2(src_file, media_dir / fname)
            media_copied += 1
    print(f'   ✅ {media_copied} media files')
    
    # 3. Save storyboard if exists
    storyboards = list(STORYBOARDS.glob('*.json'))
    if storyboards:
        # Find most relevant storyboard
        for sb in storyboards:
            sb_data = json.loads(sb.read_text())
            if sb_data.get('episode_title', '') == proj.get('name', '') or \
               sb_data.get('episode_id', '') in name if name else False:
                (pub_dir / 'storyboard.json').write_text(json.dumps(sb_data, indent=2))
                print(f'   ✅ storyboard.json ({sb.name})')
                break
        else:
            # Just copy latest
            shutil.copy2(storyboards[-1], pub_dir / 'storyboard.json')
            print(f'   ✅ storyboard.json ({storyboards[-1].name})')
    
    # 4. Save gold standard
    gs = GOLD_DIR / f'{name or slug}.json'
    if not gs.exists():
        capture(name or slug)
    else:
        print(f'   ⏭ gold standard already exists')
    
    # 5. Create README
    total_dur = max((c.get('start', 0) + c.get('duration', 0)) for c in proj['clips'])
    v1_count = len([c for c in proj['clips'] if c['track'] == 'V1'])
    a1_count = len([c for c in proj['clips'] if c['track'] == 'A1'])
    
    readme = f"""# {proj.get('name', 'Untitled Video')}

Published: {datetime.now().isoformat()}
Duration: {total_dur:.0f}s ({total_dur/60:.1f} min)
Segments: {a1_count} audio clips, {v1_count} visual clips
Media files: {media_copied}

## Files
- `project.json` — FableCut timeline
- `storyboard.json` — Script with narration
- `media/` — All audio + image files
"""
    (pub_dir / 'README.md').write_text(readme)
    print(f'   ✅ README.md')
    
    print(f'\n📦 Published to: {pub_dir}')
    print(f'   Size: {sum(f.stat().st_size for f in pub_dir.rglob("*") if f.is_file()) / 1024 / 1024:.1f} MB')
    return True

def main():
    args = ' '.join(sys.argv)
    if '--publish' in args:
        name = None
        for a in sys.argv[1:]:
            if a.startswith('--publish='):
                name = a.split('=', 1)[1]
        if name:
            publish_video(name)
        else:
            publish_video(None)
    elif '--capture' in sys.argv:
        name = None
        for a in sys.argv[1:]:
            if a.startswith('--name='):
                name = a.split('=', 1)[1]
        if not name:
            print('Provide --name=<template-name>')
            return
        capture(name)
    elif '--show' in sys.argv:
        name = None
        for a in sys.argv[1:]:
            if a.startswith('--show='):
                name = a.split('=', 1)[1]
        if name:
            show(name)
        else:
            print('Provide --show=<template-name>')
    elif '--apply' in sys.argv:
        gold_name = None
        sb_name = None
        for a in sys.argv[1:]:
            if a.startswith('--apply='):
                gold_name = a.split('=', 1)[1]
            if a.startswith('--storyboard='):
                sb_name = a.split('=', 1)[1]
        if gold_name and sb_name:
            apply_gold(gold_name, sb_name)
        else:
            print('Provide --apply=<gold-name> --storyboard=<name>')
    elif '--help' in sys.argv:
        print(__doc__)
    else:
        list_gold()

if __name__ == '__main__':
    main()
