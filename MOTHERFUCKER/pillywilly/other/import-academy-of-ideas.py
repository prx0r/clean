#!/usr/bin/env python3

import json, os, re, sys, time, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path('/root/projects/blog')
OUT = ROOT / 'content' / 'research' / 'academy-of-ideas'
OUT.mkdir(parents=True, exist_ok=True)

URL_FILE = '/tmp/aoi-urls.txt'
MAX_ARTICLES = int(os.environ.get('MAX_AOI', '587'))
SLEEP = 1.5

def log(msg):
    print(f'  {msg}', flush=True)

def strip_html(html):
    clean = re.sub(r'<(script|style|nav|header|footer)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'&[a-z]+;', ' ', clean)
    clean = re.sub(r'&amp;', '&', clean)
    clean = re.sub(r'&lt;', '<', clean)
    clean = re.sub(r'&gt;', '>', clean)
    clean = re.sub(r'&quot;', '"', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

def extract_transcript(html):
    clean = strip_html(html)
    start = clean.lower().find('transcript of this video')
    if start < 0:
        return ''
    start += len('transcript of this video')
    
    for end_marker in ['further readings', 'art used in this video', 'be a member', 'comments', 'share this:']:
        end = clean.lower().find(end_marker, start)
        if end > start:
            text = clean[start:end].strip()
            # Remove comment section
            comment_idx = text.lower().find('leave a comment')
            if comment_idx > 0:
                text = text[:comment_idx]
            comment_idx = text.lower().find('comments')
            if comment_idx > 0 and comment_idx < len(text) - 200:
                text = text[:comment_idx]
            return text.strip()
    return ''

def extract_art(html):
    items = []
    # Find art-flex section
    art_start = html.find('class="art-flex"')
    if art_start < 0:
        # Try h3 id="art"
        art_start = html.find('id="art"')
        if art_start < 0:
            return items
        # Find the containing div after h3
        art_start = html.find('<div', art_start)
    
    art_end = html.find('</div>', art_start)
    while art_end > 0:
        next_div = html.find('<div', art_end)
        if next_div > 0 and next_div - art_end < 20:
            art_end = html.find('</div>', next_div)
            if art_end < 0:
                break
        else:
            art_end += 6
            break
    
    art_section = html[art_start:art_end]
    
    imgs = re.findall(r'<img[^>]+src="([^"]*upload\.wikimedia[^"]+)"', art_section)
    alts = re.findall(r'alt="([^"]*)"', art_section)
    links = re.findall(r'href="(https?://commons\.wikimedia[^"]+)"', art_section)
    titles = re.findall(r'title="([^"]*)"', art_section)
    
    for i in range(min(len(imgs), len(links))):
        alt = alts[i] if i < len(alts) else ''
        title = titles[i] if i < len(titles) else ''
        item = {
            'alt': alt.strip(),
            'thumb_url': imgs[i],
            'source_url': links[i],
            'credit': title.strip(),
        }
        items.append(item)
    
    return items

def extract_mp3(html):
    m = re.search(r'href="([^"]*blubrry[^"]*)"', html)
    return m.group(1) if m else ''

def extract_title(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<title>(.*?)</title>', html)
    return m.group(1).strip() if m else ''

def extract_categories(html):
    cats = re.findall(r'<a[^>]*rel="category tag"[^>]*>(.*?)</a>', html)
    return [c.strip() for c in cats]

def art_direct_url(thumb_url):
    """Convert Wikimedia thumbnail URL to full-size image URL."""
    # Thumb: .../thumb/a/ab/Filename.jpg/330px-Filename.jpg
    # Full:  .../a/ab/Filename.jpg
    m = re.search(r'/thumb/(.+?/\d+px-.+)$', thumb_url)
    if m:
        path = m.group(1)
        path = re.sub(r'/d+px-', '/', path)
        return 'https://upload.wikimedia.org/wikipedia/commons/' + path
    return thumb_url

def download_art(art_items, article_dir, slug):
    downloaded = 0
    for i, art in enumerate(art_items):
        url = art_direct_url(art.get('thumb_url', ''))
        if not url:
            continue
        ext = url.rsplit('.', 1)[-1].split('?')[0][:5]
        fname = f'{i:03d}.{ext}'
        out_path = article_dir / 'art' / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        if out_path.exists():
            downloaded += 1
            continue
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) > 1000:
                out_path.write_bytes(data)
                downloaded += 1
                art['local_path'] = str(out_path.relative_to(ROOT))
        except Exception as e:
            pass
        time.sleep(0.3)
    return downloaded

def main():
    with open(URL_FILE) as f:
        urls = [l.strip() for l in f if l.strip()]
    
    log(f'Loaded {len(urls)} URLs, max {MAX_ARTICLES}')
    
    index = []
    done = 0
    art_total = 0
    errors = 0
    
    for url in urls[:MAX_ARTICLES]:
        done += 1
        slug = url.rstrip('/').split('/')[-1]
        
        article_dir = OUT / slug
        if (article_dir / 'article.json').exists():
            log(f'[{done}/{MAX_ARTICLES}] SKIP {slug}')
            with open(article_dir / 'article.json') as f:
                data = json.load(f)
            idx_entry = {k: data.get(k, '') for k in ['slug', 'title', 'date', 'url', 'word_count', 'art_count', 'art_downloaded']}
            idx_entry['art_count'] = len(data.get('art', []))
            index.append(idx_entry)
            continue
        
        log(f'[{done}/{MAX_ARTICLES}] {slug}')
        
        try:
            html = fetch(url)
        except Exception as e:
            log(f'  ERROR fetch: {e}')
            errors += 1
            continue
        
        # Skip members-only
        if 'You must be a member' in html:
            log(f'  SKIP (members-only)')
            continue
        
        title = extract_title(html)
        transcript = extract_transcript(html)
        art_items = extract_art(html)
        mp3 = extract_mp3(html)
        cats = extract_categories(html)
        
        # Extract date from URL
        date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        date = f'{date_match.group(1)}-{date_match.group(2)}' if date_match else ''
        
        word_count = len(transcript.split())
        
        if word_count < 50:
            log(f'  SKIP (no content: {word_count} words)')
            continue
        
        art_dl = download_art(art_items, article_dir, slug)
        art_total += art_dl
        
        data = {
            'slug': slug,
            'title': title,
            'date': date,
            'url': url,
            'categories': cats,
            'transcript': transcript,
            'word_count': word_count,
            'mp3': mp3,
            'art': art_items,
            'art_count': len(art_items),
            'art_downloaded': art_dl,
        }
        
        article_dir.mkdir(parents=True, exist_ok=True)
        with open(article_dir / 'article.json', 'w') as f:
            json.dump(data, f, indent=2)
        with open(article_dir / 'transcript.txt', 'w') as f:
            f.write(transcript)
        
        idx_entry = {k: data.get(k, '') for k in ['slug', 'title', 'date', 'url', 'word_count', 'art_count', 'art_downloaded']}
        index.append(idx_entry)
        
        if done % 10 == 0:
            with open(OUT / 'index.json', 'w') as f:
                json.dump(index, f, indent=2)
            log(f'  Checkpoint: {done} done, {art_total} art, {errors} errors')
        
        time.sleep(SLEEP)
    
    with open(OUT / 'index.json', 'w') as f:
        json.dump(index, f, indent=2)
    
    log(f'\nDONE: {done} articles, {art_total} art downloaded, {errors} errors')
    log(f'Index: {OUT / "index.json"}')

if __name__ == '__main__':
    main()
