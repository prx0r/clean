#!/usr/bin/env python3
"""
Google Vision labeling pipeline for all art images + thumbnail suitability scoring.

Processes images from public/art/, sends unlabeled ones to Google Vision API,
scores each for thumbnail suitability, and flags top candidates.

Usage:
  python3 scripts/vision-label-art.py                           # label ALL unlabeled images
  python3 scripts/vision-label-art.py --dry-run                 # show what would be labeled
  python3 scripts/vision-label-art.py --max 100                 # label up to 100 images
  python3 scripts/vision-label-art.py --thumbnails-only         # score only, no new labeling
"""

import json, os, sys, time, base64, urllib.request
from pathlib import Path

ROOT = Path('/root/projects/blog')
PUBLIC_ART = ROOT / 'public' / 'art'
GALLERY_META = ROOT / 'content' / 'glossary' / 'art'
THUMBNAIL_DATA = ROOT / 'data' / 'research' / 'layer2' / 'thumbnails-analysis-crosschannel.json'

VISION_API_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
VISION_URL = f'https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}'

# Thumbnail scoring rules (from analysis of 1,879 YouTube thumbnails)
THUMBNAIL_RULES = {
    'boost': {
        'labels': ['graphic', 'illustration', 'design', 'art', 'drawing', 'painting',
                    'digital', 'text', 'font', 'typography', 'poster', 'logo',
                    'icon', 'symbol', 'calligraphy', 'portrait', 'face',
                    'screenshot', 'animation', 'cartoon', 'comics', 'graphics'],
        'colors': ['red', 'yellow', 'gold', 'orange', 'white', 'bright'],
        'objects': ['person', 'face', 'portrait', 'statue', 'figure', 'deity'],
    },
    'penalty': {
        'labels': ['book', 'page', 'paper', 'document', 'textile', 'fabric',
                    'wood', 'wall', 'floor', 'ceiling', 'furniture',
                    'building', 'architecture', 'plant', 'tree', 'flower',
                    'landscape', 'mountain', 'sky', 'cloud', 'water'],
        'colors': ['brown', 'grey', 'gray', 'dark', 'black'],
    }
}

def call_vision(image_data, features=None):
    if not features:
        features = [
            {"type": "LABEL_DETECTION", "maxResults": 15},
            {"type": "FACE_DETECTION", "maxResults": 5},
            {"type": "IMAGE_PROPERTIES", "maxResults": 5},
            {"type": "OBJECT_LOCALIZATION", "maxResults": 5},
            {"type": "SAFE_SEARCH_DETECTION", "maxResults": 1},
            {"type": "WEB_DETECTION", "maxResults": 5},
        ]
    body = {"requests": [{
        "image": {"content": base64.b64encode(image_data).decode()},
        "features": features,
    }]}
    try:
        req = urllib.request.Request(VISION_URL,
            data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json'})
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        return result.get("responses", [{}])[0]
    except Exception as e:
        return {"error": str(e)[:100]}

def score_thumbnail(meta):
    """Score an image's thumbnail suitability 0-100 based on Vision labels."""
    labels = [l.lower() for l in meta.get('vision_labels', [])]
    objects = [o.lower() for o in meta.get('vision_objects', [])]
    web_ents = [e.lower() for e in meta.get('web_entities', [])]
    colors = [c.lower() for c in meta.get('dominant_colors', [])]
    has_face = meta.get('face_count', 0) > 0
    safe = meta.get('safe_search', {})
    
    score = 50  # baseline
    
    all_terms = labels + objects + web_ents
    
    # Boosts
    for rule_label in THUMBNAIL_RULES['boost']['labels']:
        if any(rule_label in t for t in all_terms):
            score += 8
    
    for rule_color in THUMBNAIL_RULES['boost']['colors']:
        if any(rule_color in c for c in colors):
            score += 5
    
    if any('person' in t or 'face' in t or 'portrait' in t for t in all_terms):
        score += 10  # people in thumbnails = engagement
    
    if has_face:
        score += 5  # faces are neutral in breakout but good for engagement
    
    # Penalties
    for rule_label in THUMBNAIL_RULES['penalty']['labels']:
        if any(rule_label in t for t in all_terms):
            score -= 6
    
    for rule_color in THUMBNAIL_RULES['penalty']['colors']:
        if any(rule_color in c for c in colors):
            score -= 4
    
    # Label diversity (more labels = more content to work with)
    score += min(len(labels), 10)  # up to +10 for diverse labels
    
    # Safe search penalty
    if safe.get('adult') in ('LIKELY', 'VERY_LIKELY'):
        score -= 40
    if safe.get('violence') in ('LIKELY', 'VERY_LIKELY'):
        score -= 30
    
    return max(0, min(100, score))

def find_unlabeled():
    """Find all art images missing Vision labels."""
    images = []
    for f in sorted(PUBLIC_ART.glob('*.jpg')):
        meta_path = GALLERY_META / f'{f.stem}.json'
        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except:
                pass
        
        needs_label = not meta.get('vision_labels') and not meta.get('labels')
        images.append({
            'file': f.name,
            'path': f,
            'meta_path': meta_path,
            'meta': meta,
            'needs_label': needs_label,
            'size': f.stat().st_size,
        })
    
    return images

def process_image(img, skip_vision=False):
    """Process a single image: Vision API + thumbnail score."""
    data = img['path'].read_bytes()
    if len(data) > 10 * 1024 * 1024:
        return {'error': 'too large (>10MB)'}
    
    result = {}
    
    if not skip_vision:
        vision = call_vision(data)
        if 'error' in vision:
            return {'error': vision['error']}
        
        # Extract all features
        labels = [l['description'] for l in vision.get('labelAnnotations', [])]
        objects = [o['name'] for o in vision.get('localizedObjectAnnotations', [])]
        web_ents = [e.get('description','') for e in vision.get('webDetection',{}).get('webEntities',[])[:5] if e.get('description')]
        faces = vision.get('faceAnnotations', [])
        colors = vision.get('imagePropertiesAnnotation',{}).get('dominantColors',{}).get('colors',[])
        safe = vision.get('safeSearchAnnotation', {})
        
        result = {
            'vision_labels': labels,
            'vision_objects': objects,
            'web_entities': web_ents,
            'face_count': len(faces),
            'dominant_colors': [f"#{c['color']['red']:02x}{c['color']['green']:02x}{c['color']['blue']:02x}" for c in colors[:3]],
            'safe_search': {k: v for k, v in safe.items() if k in ('adult','violence','racy')},
        }
        
        # Score thumbnail suitability
        result['thumbnail_score'] = score_thumbnail(result)
        result['thumbnail_verdict'] = (
            '⭐ EXCELLENT' if result['thumbnail_score'] >= 80 else
            '👍 GOOD' if result['thumbnail_score'] >= 65 else
            '👎 POOR' if result['thumbnail_score'] >= 40 else
            '❌ UNSUITABLE'
        )
    
    return result

def main():
    dry_run = '--dry-run' in sys.argv
    max_images = None
    for a in sys.argv:
        if a.startswith('--max='):
            max_images = int(a.split('=')[1])
    skip_vision = '--thumbnails-only' in sys.argv
    
    images = find_unlabeled()
    
    if skip_vision:
        # Just score existing metadata
        todo = [i for i in images if not i['meta'].get('thumbnail_score')]
    else:
        todo = [i for i in images if i['needs_label']]
    
    if max_images:
        todo = todo[:max_images]
    
    print(f'Total images: {len(images)}')
    print(f'Need labeling: {len([i for i in images if i["needs_label"]])}')
    if skip_vision:
        print(f'Need thumbnail scoring: {len(todo)}')
    print(f'Processing this session: {len(todo)}')
    
    if dry_run:
        print('\nWould process:')
        for img in todo[:20]:
            print(f'  {img["file"]}')
        if len(todo) > 20:
            print(f'  ... and {len(todo)-20} more')
        return
    
    processed = 0
    errors = 0
    thumbnails = []
    
    for img in todo:
        result = process_image(img, skip_vision)
        
        if 'error' in result:
            errors += 1
            print(f'❌ {img["file"]}: {result["error"]}')
            continue
        
        # Merge with existing metadata
        meta = dict(img['meta'])
        meta.update(result)
        
        # Save
        img['meta_path'].write_text(json.dumps(meta, indent=2))
        processed += 1
        
        # Track good thumbnails
        ts = result.get('thumbnail_score', 0)
        if ts >= 60:
            thumbnails.append((ts, img['file'], result.get('vision_labels',[])[:3]))
        
        print(f'✅ ({processed:3d}) {img["file"][:45]:45s} thumb_score={ts:2d} {result.get("thumbnail_verdict","?")}')
        
        # Rate limiting
        if not skip_vision:
            time.sleep(0.2)
    
    # Summary
    print(f'\n{"="*60}')
    print(f'VISION LABELING SESSION')
    print(f'{"="*60}')
    print(f'  Processed: {processed}')
    print(f'  Errors: {errors}')
    print(f'  API calls: {processed if not skip_vision else 0}')
    
    thumbnails.sort(key=lambda x: -x[0])
    print(f'\n🏆 TOP THUMBNAIL CANDIDATES:')
    for score, file, labels in thumbnails[:20]:
        print(f'  ⭐ {score:2d}  {file[:45]:45s}  {", ".join(labels)}')
    
    # Save thumbnail candidates list
    thumb_list = [{'file': f, 'score': s, 'labels': l} for s, f, l in thumbnails]
    output = '/root/projects/blog/data/thumbnail-candidates.json'
    Path(output).write_text(json.dumps(thumb_list, indent=2))
    print(f'\nThumbnail candidates saved to {output}')

if __name__ == '__main__':
    main()
