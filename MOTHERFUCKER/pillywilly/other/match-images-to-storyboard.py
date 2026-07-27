#!/usr/bin/env python3
"""
Match images to storyboard beats using proper noun extraction + concept fallback.

Usage:
  python3 scripts/match-images-to-storyboard.py --storyboard abhinavagupta-life
  python3 scripts/match-images-to-storyboard.py --storyboard abhinavagupta-life --project
  python3 scripts/match-images-to-storyboard.py --storyboard abhinavagupta-life --beat-plan abhinavagupta-bizarre-life
  python3 scripts/match-images-to-storyboard.py --analyze-exemplar <path-to-mp4>
"""

import json, re, os, sys, shutil, base64, urllib.request, time
from pathlib import Path

ROOT = Path('/root/projects/blog')
PUBLIC_ART = ROOT / 'public' / 'art'
GALLERY_META = ROOT / 'content' / 'glossary' / 'art'
STORYBOARDS = ROOT / 'content' / 'publishing' / 'storyboards'
FABLECUT_MEDIA = Path('/root/projects/FableCut/media')
PROJECT_FILE = Path('/root/projects/FableCut/project.json')
VISION_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")

# ── ART INDEX ──
def build_art_index():
    index = []
    for f in sorted(PUBLIC_ART.glob('*.*')):
        if f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.gif'):
            continue
        meta = {}
        meta_file = GALLERY_META / f'{f.stem}.json'
        if meta_file.exists():
            try: meta = json.loads(meta_file.read_text())
            except: pass
        
        title = (meta.get('title') or f.stem).lower()
        concepts = [c.lower() for c in (meta.get('concepts') or [])]
        vision_labels = [l.lower() for l in (meta.get('vision_labels') or [])]
        tags = [t.lower() for t in (meta.get('tags') or [])]
        culture = (meta.get('culture') or '').lower()
        artist = (meta.get('artist') or '').lower()
        
        index.append({
            'file': f.name,
            'title': title,
            'concepts': concepts,
            'vision_labels': vision_labels,
            'tags': tags,
            'culture': culture,
            'artist': artist,
            'filename_words': set(re.split(r'[_\-. ]+', f.stem.lower())),
            'size': f.stat().st_size,
        })
    return index

# ── PROPER NOUN EXTRACTION ──
PROPER_NOUN_PATTERNS = [
    # Person names: Capitalized Word followed by capitalized word
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
    # Diacritic names
    r'\b\w+[āīūṛṣṭñṇḍḥ]+\w*\b',
    # Sanskrit/Tibetan terms + deity names (will match against art titles/concepts)
    r'\b(Tantra|Yoga|Sutra|Mantra|Yantra|Mandala|Nataraja|Shiva|Devi|Kali|Durga|Parvati|Lakshmi|Saraswati|Ganesha|Buddha|Bodhisattva|Vajra|Karma|Dharma|Samsara|Nirvana|Moksha|Puja|Homa|Nyasa|Japa|Asana|Pranayama|Dhyana|Samadhi|Vajrayogini|Chakrasamvara|Hevajra|Mahakala|Mahadevi|Bhairava|Bhairavi|Kurukulla|Tara|Matangi|Chinnamasta|Bhudevi|Rudra|Brahma|Vishnu|Harihara|Ardhanari|Gaja|Simha|Nandi|Garuda|Hanuman|Surya|Chandra|Agni|Vayu|Varuna|Yama|Kubera|Indra)\b',
    # Known Indic names
    r'\b(Abhinavagupta|Lakshmanjoo|Ramana|Maharishi|Aurobindo|Vivekananda|Yogananda|Patanjali|Shankara|Ramanuja|Madhva|Nagarjuna|Padmasambhava|Tsongkhapa|Milarepa|Naropa|Marpa|Atisha|Ksemaraja|Utpaladeva|Somananda|Kallata|Vasugupta|Anandamayi|Nisargadatta|Maharaj|Krishna|Bhakti|Vedanta|Advaita|Jnana|Raja|Hatha|Kundalini|Yogini|Siddha|Mahasiddha|Dakini|Naga|Deva|Devi|Rishi|Muni|Swami|Guru|Bhagavan|Acharya|Pandit|Bhakta|Yogi|Mantrin|Tantrika|Shaiva|Shakta|Vaishnava|Kaula|Mishra|Purnananda|Gaudapada|Govinda|Shankara|Vidyaranya|Madhusudana|Raghunatha|Jiva|Rupa|Sanatana|Chaitanya|Nityananda|Advaitananda|Paramahamsa|Brahmendra|Sadasiva|Ramalinga|Ramakrishna|Sarada|Vivekananda|Abhedananda|Sivananda|Chinmayananda|Dayananda|Mahesh|Maharshi|Aurobindo|Mother|Mira|Alfassa|Satprem|Pavitra|Nolini|Amal|Kishore|Jugal|Dilip|Nirodbaran|Champaklal|Nagendra|Mangesh|Mohan|Rajesh|Suresh|Mahesh|Ramesh|Dinesh|Bhupesh|Dharmesh|Prakash|Deepak|Ravi|Shyam|Mohan)\b',
]

def extract_proper_nouns(text):
    nouns = set()
    for pat in PROPER_NOUN_PATTERNS:
        for m in re.finditer(pat, text):
            nouns.add(m.group(0).lower())
    return nouns

def extract_concepts(text):
    from collections import Counter
    text_lower = text.lower()
    words = set(re.findall(r'\b[a-z]{3,}\b', text_lower))
    return words - {'the', 'and', 'for', 'was', 'that', 'this', 'with', 'from', 'have', 'had',
                    'not', 'are', 'his', 'her', 'its', 'but', 'all', 'been', 'were', 'they',
                    'their', 'what', 'when', 'where', 'which', 'who', 'how', 'would', 'could',
                    'should', 'there', 'these', 'those', 'about', 'into', 'over', 'after',
                    'being', 'made', 'some', 'them', 'than', 'very', 'just', 'also', 'more',
                    'most', 'much', 'many', 'such', 'only', 'other', 'each', 'both', 'one',
                    'two', 'new', 'first', 'last', 'long', 'great', 'own', 'same', 'old',
                    'another', 'every', 'still', 'even', 'well', 'way', 'time', 'life', 'day',
                    'world', 'year', 'part', 'place', 'end', 'hand', 'head', 'body',
                    'mind', 'heart', 'face', 'word', 'thing', 'man', 'woman', 'child'}

def score_image(art, proper_nouns, concepts, narration):
    """Score how well an image matches narration. Higher = better."""
    score = 0
    
    # Exact proper noun match (BIG boost)
    for pn in proper_nouns:
        if pn in art['title'] or pn in ' '.join(art['filename_words']):
            score += 25
        for c in art['concepts']:
            if pn in c:
                score += 20
        for l in art['vision_labels']:
            if pn in l:
                score += 15
    
    # Concept overlap
    for c in concepts:
        if c in art['title'] or c in ' '.join(art['filename_words']):
            score += 5
        for ac in art['concepts']:
            if c in ac:
                score += 4
        for vl in art['vision_labels']:
            if c in vl:
                score += 3
        for t in art['tags']:
            if c in t:
                score += 2
    
    # Culture match (boost for Indian/Tibetan art)
    if 'india' in art['culture'] or 'tibet' in art['culture'] or 'nepal' in art['culture']:
        score += 3
    
    return score

# ── MATCHING ──
def match_images(art_index, narration_texts, beat_durations=None):
    """Match images to each narration segment. Returns list of (image_file, score)."""
    used = set()
    matches = []
    
    for i, text in enumerate(narration_texts):
        proper_nouns = extract_proper_nouns(text)
        concepts = extract_concepts(text)
        
        scored = []
        for art in art_index:
            if art['file'] in used:
                continue
            s = score_image(art, proper_nouns, concepts, text)
            if s > 0:
                scored.append((s, art))
        
        # Short beats (name drops) can reuse images within a window of 5
        # Long beats need unique images
        allow_reuse = beat_durations and beat_durations[i] < 4
        
        scored.sort(key=lambda x: -x[0])
        
        best = None
        if scored:
            best = scored[0][1]
            if not allow_reuse:
                used.add(best['file'])
        
        matches.append({
            'index': i,
            'proper_nouns': list(proper_nouns),
            'concepts_count': len(concepts),
            'score': scored[0][0] if scored else 0,
            'image': best['file'] if best else None,
            'matched_on': 'proper_noun' if best and any(pn in best['title'] or pn in ' '.join(best['filename_words']) for pn in proper_nouns) else 'concept' if best else 'none',
        })
    
    return matches

def match_storyboard(storyboard_name, beat_plan_name=None, update_project=False):
    """Match images to a storyboard, optionally using a beat plan for durations."""
    art_index = build_art_index()
    print(f'Art index: {len(art_index)} images')
    
    sb_path = STORYBOARDS / f'{storyboard_name}.json'
    sb = json.loads(sb_path.read_text())
    
    # Load beat plan if specified (gives us durations per beat)
    beats = None
    if beat_plan_name:
        bp_path = STORYBOARDS / f'{beat_plan_name}.json'
        if bp_path.exists():
            beats = json.loads(bp_path.read_text())
            print(f'Beat plan: {len(beats)} beats')
    
    segments = sb.get('segments', [])
    if not segments and beats:
        # Use beat plan as the source of narration (split storyboard text across beats)
        pass  # handled below
    
    if beats:
        # Assign durations from beat plan, narrations from storyboard segments
        seg_texts = []
        for seg in segments:
            seg_texts.append(seg.get('narration', seg.get('label', '')))
        
        # Distribute narration across beats
        total_words = sum(len(t.split()) for t in seg_texts)
        beat_durations = [b['duration_sec'] for b in beats]
        
        narration_texts = []
        beat_idx = 0
        for seg_idx, seg_text in enumerate(seg_texts):
            words = seg_text.split()
            beats_in_seg = sum(1 for b in beats if b['segment'] == seg_idx + 1)
            if beats_in_seg == 0:
                continue
            words_per_beat = max(1, len(words) // beats_in_seg)
            for b_idx in range(beats_in_seg):
                chunk = words[b_idx * words_per_beat : (b_idx + 1) * words_per_beat]
                narration_texts.append(' '.join(chunk))
                beat_idx += 1
        
        matches = match_images(art_index, narration_texts)
        
        # Add duration and image info to beats
        for i, m in enumerate(matches):
            if i < len(beats):
                beats[i]['matched_image'] = m['image']
                beats[i]['match_score'] = m['score']
                beats[i]['match_type'] = m['matched_on']
                if i == 0 or True:
                    beats[i]['proper_nouns'] = m['proper_nouns']
    else:
        # Simple segment-level matching (no beat plan)
        narration_texts = [s.get('narration', s.get('label', '')) for s in segments]
        matches = match_images(art_index, narration_texts)
        
        for i, s in enumerate(segments):
            if i < len(matches):
                s['matched_image'] = matches[i]['image']
                s['match_score'] = matches[i]['score']
    
    # Report
    matched = sum(1 for m in matches if m['image'])
    noun_matches = sum(1 for m in matches if m['matched_on'] == 'proper_noun')
    concept_matches = sum(1 for m in matches if m['matched_on'] == 'concept')
    
    print(f'\n=== Matching Results ({storyboard_name}) ===')
    print(f'Total beats: {len(matches)}')
    print(f'Matched: {matched}/{len(matches)}')
    print(f'  By proper noun: {noun_matches}')
    print(f'  By concept: {concept_matches}')
    print(f'  Unmatched: {len(matches) - matched}')
    print()
    
    if beats:
        for i, b in enumerate(beats[:8]):
            dur = b['duration_sec']
            img = b.get('matched_image', '❌ NO MATCH')
            mtype = b.get('match_type', '?')
            score = b.get('match_score', 0)
            blip = '⚡' if dur < 3 else '📷' if dur < 8 else '🖼'
            pns = ', '.join(b.get('proper_nouns', [])[:3])
            print(f'  {blip} beat {i+1:3d}: {dur:5.1f}s {mtype:12s} score={score:3d} {img[:40]:40s} [{pns}]')
    
    # Update FableCut project
    if update_project and beats:
        update_fablecut(beats, storyboard_name)
    
    return beats if beats else matches

def update_fablecut(beats, storyboard_name):
    """Copy matched images to FableCut media and build project."""
    proj = json.loads(PROJECT_FILE.read_text())
    
    # Remove old image media + V1 clips
    proj['media'] = [m for m in proj['media'] if m['kind'] != 'image']
    proj['clips'] = [c for c in proj['clips'] if c['track'] != 'V1']
    
    beat_count = 0
    for i, b in enumerate(beats):
        if not b.get('matched_image'):
            continue
        
        src = PUBLIC_ART / b['matched_image']
        if not src.exists():
            continue
        
        ext = '.jpg'
        dst_name = f'bb_{storyboard_name}_{i:04d}{ext}'
        dst = FABLECUT_MEDIA / dst_name
        
        try:
            shutil.copy2(src, dst)
        except:
            continue
        
        # Calculate start time from previous beats
        start = sum(beats[j]['duration_sec'] for j in range(i))
        dur = b['duration_sec']
        
        # Pick animation style
        anim_idx = beat_count % 4
        if anim_idx == 0:
            kf = {"scale": [{"t": 0, "v": 1.0}, {"t": dur, "v": 1.10, "ease": "linear"}]}
        elif anim_idx == 1:
            kf = {"scale": [{"t": 0, "v": 1.0}, {"t": dur, "v": 1.12}], "x": [{"t": 0, "v": 0}, {"t": dur, "v": 12}]}
        elif anim_idx == 2:
            kf = {"scale": [{"t": 0, "v": 1.12}, {"t": dur, "v": 1.0, "ease": "linear"}]}
        else:
            kf = {"scale": [{"t": 0, "v": 1.0}, {"t": dur, "v": 1.08}], "x": [{"t": 0, "v": -8}, {"t": dur, "v": 8}]}
        
        media_id = f'm_bb_{i:04d}'
        
        proj['media'].append({
            'id': media_id, 'name': dst_name, 'kind': 'image',
            'src': f'/media/{dst_name}', 'duration': dur,
        })
        proj['clips'].append({
            'id': f'c_v1_bb_{i:04d}', 'mediaId': media_id, 'kind': 'image', 'track': 'V1',
            'start': round(start, 1), 'duration': round(dur, 1), 'keyframes': kf,
            'props': {'filterPreset': 'cinematic'},
        })
        beat_count += 1
    
    proj['revision'] = proj.get('revision', 0) + 1
    proj['name'] = f"The Bizarre Life of {storyboard_name.replace('abhinavagupta','Abhinavagupta').replace('-',' ').title()}"
    PROJECT_FILE.write_text(json.dumps(proj, indent=2))
    print(f'\n✅ FableCut project updated: {len(proj["media"])} media, {len(proj["clips"])} clips')
    print(f'   Images placed: {beat_count}')

def main():
    storyboard_name = None
    beat_plan = None
    do_project = False
    
    for a in sys.argv[1:]:
        if a.startswith('--storyboard='):
            storyboard_name = a.split('=', 1)[1]
        elif a.startswith('--beat-plan='):
            beat_plan = a.split('=', 1)[1]
        elif a == '--project':
            do_project = True
    
    if not storyboard_name:
        print('Usage: python3 scripts/match-images-to-storyboard.py --storyboard <name> [--beat-plan <name>] [--project]')
        return
    
    match_storyboard(storyboard_name, beat_plan, do_project)

if __name__ == '__main__':
    main()
