#!/usr/bin/env python3
"""
Batch download Tantra-relevant art from museum APIs, label with Google Vision.

Usage:
  python3 scripts/batch-fetch-tantra-art.py --query shiva --max 20
  python3 scripts/batch-fetch-tantra-art.py --query tantra --max 50 --skip-vision
  python3 scripts/batch-fetch-tantra-art.py --all-queries --max 30
  python3 scripts/batch-fetch-tantra-art.py --test               # dry run, no downloads
"""

import json, os, sys, time, urllib.request, urllib.parse, socket, hashlib
from pathlib import Path

ROOT = Path('/root/projects/blog')
PUBLIC_ART = ROOT / 'public' / 'art'
GALLERY_META = ROOT / 'content' / 'glossary' / 'art'
FABLECUT_MEDIA = Path('/root/projects/FableCut/media')

PUBLIC_ART.mkdir(parents=True, exist_ok=True)
GALLERY_META.mkdir(parents=True, exist_ok=True)

# API endpoints
MET_API = 'https://collectionapi.metmuseum.org/public/collection/v1'
MET_IMAGE = 'https://images.metmuseum.org/CRDImages'
CLEVELAND_API = 'https://openaccess-api.clevelandart.org/api/artworks'
CLEVELAND_IMAGE = 'https://openaccess-cdn.clevelandart.org'

VISION_API_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
VISION_URL = f'https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}'

TOR_PROXY = ('localhost', 9050)

RELEVANT_DEPTS = ['asian art', 'arts of africa, oceania, and the americas',
                   'islamic art', 'egyptian art', 'medieval art',
                   'the libraries', 'photographs', 'drawings and prints',
                   'asian', 'south asian', 'southeast asian', 'himalayan']
RELEVANT_CULTURES = ['india', 'tibetan', 'nepalese', 'kashmir', 'hindu', 'buddhist',
                     'jain', 'sri lanka', 'bangladesh', 'pakistan', 'burma',
                     'cambodia', 'thailand', 'indonesia', 'java', 'khmer',
                     'central asia', 'chinese', 'japanese', 'mongolian',
                     'iran', 'persian', 'turkish', 'afghan']

def use_tor():
    try:
        import socks
        socks.set_default_proxy(socks.SOCKS5, *TOR_PROXY)
        socket.socket = socks.socksocket
        return True
    except:
        return False

def fetch_json(url, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TantraFiles/1.0'})
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                print(f'  ⚠ Fetch failed: {url[:80]} — {e}')
                return None

def download_file(url, dest, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TantraFiles/1.0'})
            resp = urllib.request.urlopen(req, timeout=30)
            data = resp.read()
            if len(data) < 1024:
                return None
            dest.write_bytes(data)
            return data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None

def call_vision(image_data):
    body = {
        "requests": [{
            "image": {"content": base64.b64encode(image_data).decode()},
            "features": [
                {"type": "LABEL_DETECTION", "maxResults": 10},
                {"type": "OBJECT_LOCALIZATION", "maxResults": 5},
                {"type": "IMAGE_PROPERTIES", "maxResults": 3},
                {"type": "WEB_DETECTION", "maxResults": 5},
            ],
        }]
    }
    try:
        req = urllib.request.Request(VISION_URL,
            data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json'},
            timeout=15)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        r = result.get("responses", [{}])[0]
        return {
            "labels": [l["description"] for l in r.get("labelAnnotations", [])],
            "objects": [o["name"] for o in r.get("localizedObjectAnnotations", [])],
            "web_entities": [e.get("description","") for e in r.get("webDetection",{}).get("webEntities",[])[:5] if e.get("description")],
            "colors": [
                f"#{c['color']['red']:02x}{c['color']['green']:02x}{c['color']['blue']:02x}"
                for c in r.get("imagePropertiesAnnotation",{}).get("dominantColors",{}).get("colors",[])[:3]
            ],
        }
    except:
        return None

def search_met(query, max_results=50):
    url = f'{MET_API}/search?q={urllib.parse.quote(query)}&hasImages=true'
    data = fetch_json(url)
    if not data or not data.get('objectIDs'):
        print(f'  ⚠ No Met results for "{query}"')
        return []
    ids = data['objectIDs'][:max_results]
    print(f'  📦 Met "{query}": {len(ids)} objects (of {data.get("total",0)} total)')
    results = []
    for i, oid in enumerate(ids):
        obj = fetch_json(f'{MET_API}/objects/{oid}')
        if not obj or not obj.get('primaryImage'):
            continue
        results.append({
            'id': oid,
            'source': 'met',
            'title': obj.get('title', ''),
            'artist': obj.get('artistDisplayName', ''),
            'medium': obj.get('medium', ''),
            'date': obj.get('objectDate', ''),
            'tags': [t['term'] for t in obj.get('tags', [])],
            'department': obj.get('department', ''),
            'culture': obj.get('culture', ''),
            'period': obj.get('period', ''),
            'image_url': obj.get('primaryImage'),
            'image_small': obj.get('primaryImageSmall', obj.get('primaryImage')),
        })
        if (i + 1) % 10 == 0:
            print(f'    ...{i+1}/{len(ids)} ({(i+1)/len(ids)*100:.0f}%)')
    return results

def search_cleveland(query, max_results=50):
    url = f'{CLEVELAND_API}?q={urllib.parse.quote(query)}&limit={max_results}&has_image=1'
    data = fetch_json(url)
    if not data or not data.get('data'):
        print(f'  ⚠ No Cleveland results for "{query}"')
        return []
    artworks = data['data'][:max_results]
    print(f'  📦 Cleveland "{query}": {len(artworks)} artworks')
    results = []
    for a in artworks:
        img_url = None
        if a.get('images') and a['images'].get('web'):
            img_url = a['images']['web'].get('url')
        if not img_url:
            continue
        results.append({
            'id': a.get('id', ''),
            'source': 'cleveland',
            'title': a.get('title', ''),
            'artist': (a.get('creators') or [{}])[0].get('description', '') if a.get('creators') else '',
            'medium': a.get('technique', ''),
            'date': a.get('creation_date', ''),
            'tags': [t for t in (a.get('tags') or [])],
            'culture': (a.get('culture') or [None])[0] if a.get('culture') else '',
            'image_url': img_url,
            'image_small': img_url,
        })
    return results

def download_session(queries, max_per_query=30, skip_vision=False, test_mode=False):
    total_downloaded = 0
    total_errors = 0
    total_vision = 0
    total_skipped = 0
    
    for query, source, label in queries:
        print(f'\n── {label} ({source}: "{query}") ──')
        
        if source == 'met':
            results = search_met(query, max_per_query)
        elif source == 'cleveland':
            results = search_cleveland(query, max_per_query)
        else:
            continue
        
        for i, art in enumerate(results):
            stem = f'{label}_{art["id"]}'
            img_path = PUBLIC_ART / f'{stem}.jpg'
            meta_path = GALLERY_META / f'{stem}.json'
            
            if img_path.exists():
                total_skipped += 1
                if (i + 1) % 10 == 0:
                    print(f'  ⏭ {i+1}/{len(results)} (skipped)')
                continue
            
            if test_mode:
                print(f'  🔍 Would download: {art["title"][:50]} from {art["image_url"][:60]}...')
                total_skipped += 1
                continue
            
            # Download image
            img_data = download_file(art['image_url'], img_path)
            if not img_data:
                total_errors += 1
                print(f'  ❌ {i+1}/{len(results)} FAILED: {art["title"][:40]}')
                continue
            
            # Build metadata
            meta = {
                'title': art['title'],
                'artist': art.get('artist', ''),
                'source': art['source'],
                'source_id': str(art['id']),
                'medium': art.get('medium', ''),
                'date': art.get('date', ''),
                'culture': art.get('culture', ''),
                'period': art.get('period', ''),
                'tags': art.get('tags', []),
                'concepts': [],
                'visual_motifs': [],
                'mood': [],
                'entities_depicted': [],
                'vision_labels': [],
            }
            
            # Google Vision labeling
            vision = None
            if not skip_vision:
                vision = call_vision(img_data)
                if vision:
                    meta['vision_labels'] = vision['labels']
                    meta['visual_motifs'] = vision['objects']
                    meta['web_entities'] = vision['web_entities']
                    meta['dominant_colors'] = vision['colors']
                    total_vision += 1
                time.sleep(0.15)
            else:
                meta['tags'] = art.get('tags', [])
                meta['concepts'] = [t.lower() for t in art.get('tags', [])]
            
            GALLERY_META.joinpath(f'{stem}.json').write_text(json.dumps(meta, indent=2))
            total_downloaded += 1
            
            status = '✅'
            if vision:
                status += f' (vision: {len(vision.get("labels",[]))} labels)'
            print(f'  {status} {i+1}/{len(results)}: {art["title"][:45]}')
            
            # Delay between downloads
            time.sleep(1.5)
        
        # Longer delay between different queries
        time.sleep(3)
    
    # Summary
    print(f'\n{"="*60}')
    print(f'SESSION SUMMARY')
    print(f'{"="*60}')
    print(f'  Downloaded: {total_downloaded} new images')
    print(f'  Already had: {total_skipped} skipped')
    print(f'  Errors: {total_errors}')
    print(f'  Vision labeled: {total_vision}')
    print(f'  Total in library now: {len(list(PUBLIC_ART.glob("*.jpg")))} images')
    print(f'  Total metadata files: {len(list(GALLERY_META.glob("*.json")))}')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Batch download Tantra art')
    parser.add_argument('--query', help='Single query (e.g. shiva)')
    parser.add_argument('--source', choices=['met', 'cleveland', 'all'], default='met')
    parser.add_argument('--max', type=int, default=30, help='Max images per query')
    parser.add_argument('--all-queries', action='store_true', help='Run all predefined queries')
    parser.add_argument('--skip-vision', action='store_true', help='Skip Google Vision labeling')
    parser.add_argument('--test', action='store_true', help='Dry run, no downloads')
    parser.add_argument('--tor', action='store_true', help='Use Tor proxy for downloads')
    args = parser.parse_args()
    
    if args.tor:
        if use_tor():
            print('🌐 Tor proxy enabled')
        else:
            print('⚠ Tor requested but PySocks not installed')
    
    if args.test:
        print('🔍 TEST MODE — no files will be downloaded\n')
    
    if args.all_queries:
        download_session(QUERIES, args.max, args.skip_vision, args.test)
    elif args.query:
        source = 'cleveland' if args.source == 'cleveland' else 'met'
        queries = [(args.query, source, args.query.replace(' ', '_'))]
        download_session(queries, args.max, args.skip_vision, args.test)
    else:
        parser.print_help()

if __name__ == '__main__':
    import base64
    main()
