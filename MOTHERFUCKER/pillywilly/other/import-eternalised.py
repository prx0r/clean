#!/usr/bin/env python3

import json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path('/root/projects/blog')
OUT = ROOT / 'content' / 'research' / 'eternalised'
OUT.mkdir(parents=True, exist_ok=True)

URL_FILE = '/tmp/eternalised-urls.txt'
MAX_ARTICLES = int(os.environ.get('MAX_ET', '200'))
SLEEP = 1.0

def log(msg):
    print(f'  {msg}', flush=True)

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

def extract_content(html):
    m = re.search(r'class="entry-content[^"]*"[^>]*>(.*?)(?:<footer|</article)', html, re.DOTALL)
    if not m:
        return ''
    content = m.group(1)
    # Remove gallery/figure blocks for clean text
    text = re.sub(r'<figure[^>]*>.*?</figure>', ' ', content, flags=re.DOTALL)
    text = re.sub(r'<(script|style|nav)[^>]*>.*?</\1>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&#8211;', '-', text)
    text = re.sub(r'&#8217;', "'", text)
    text = re.sub(r'&#038;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_title(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ''

def extract_images(html):
    imgs = re.findall(r'<img[^>]+src="([^"]*wp-content[^"]+)"[^>]*>', html)
    alts = re.findall(r'<img[^>]+alt="([^"]*)"[^>]*src="([^"]*wp-content[^"]+)"', html)
    alt_map = {a[1]: a[0] for a in alts}
    
    items = []
    seen = set()
    for src in imgs:
        if src in seen:
            continue
        seen.add(src)
        items.append({
            'url': src,
            'alt': alt_map.get(src, ''),
        })
    return items

def extract_categories(html):
    cats = re.findall(r'<a[^>]*rel="category tag"[^>]*>(.*?)</a>', html)
    return list(set(c.strip() for c in cats))

def download_image(img_url, article_dir, i):
    ext = img_url.rsplit('.', 1)[-1].split('?')[0][:5]
    fname = f'art_{i:03d}.{ext}'
    out_path = article_dir / 'art' / fname
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    if out_path.exists():
        return True
    
    try:
        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=30).read()
        if len(data) > 1000:
            out_path.write_bytes(data)
            return True
    except Exception:
        pass
    return False

def main():
    with open(URL_FILE) as f:
        urls = [l.strip() for l in f if l.strip() and l.strip() != 'https://eternalisedofficial.com/']
    
    # Filter to only article URLs (skip homepage, about, etc.)
    article_urls = [u for u in urls if re.search(r'/\d{4}/\d{2}/\d{2}/', u)]
    log(f'Loaded {len(article_urls)} article URLs of {len(urls)} total, max {MAX_ARTICLES}')
    
    index = []
    done = 0
    art_total = 0
    errors = 0
    
    for url in article_urls[:MAX_ARTICLES]:
        done += 1
        slug = url.rstrip('/').split('/')[-1]
        
        article_dir = OUT / slug
        if (article_dir / 'article.json').exists():
            log(f'[{done}/{MAX_ARTICLES}] SKIP {slug}')
            with open(article_dir / 'article.json') as f:
                data = json.load(f)
            idx_entry = {k: data.get(k, '') for k in ['slug', 'title', 'date', 'url', 'word_count', 'image_count']}
            idx_entry['image_count'] = len(data.get('images', []))
            index.append(idx_entry)
            continue
        
        log(f'[{done}/{MAX_ARTICLES}] {slug}')
        
        try:
            html = fetch(url)
        except Exception as e:
            log(f'  ERROR fetch: {e}')
            errors += 1
            continue
        
        title = extract_title(html)
        content = extract_content(html)
        images = extract_images(html)
        cats = extract_categories(html)
        
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        date = f'{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}' if date_match else ''
        
        word_count = len(content.split())
        
        if word_count < 100:
            log(f'  SKIP (short: {word_count} words)')
            continue
        
        # Download images
        img_dl = 0
        for i, img in enumerate(images[:20]):  # limit to 20 per article
            if download_image(img['url'], article_dir, i):
                img_dl += 1
                ext = img['url'].rsplit('.', 1)[-1].split('?')[0][:5]
                img['local_path'] = f'content/research/eternalised/{slug}/art/art_{i:03d}.{ext}'
        art_total += img_dl
        
        data = {
            'slug': slug,
            'title': title,
            'date': date,
            'url': url,
            'categories': cats,
            'content': content,
            'word_count': word_count,
            'images': images,
            'images_downloaded': img_dl,
        }
        
        article_dir.mkdir(parents=True, exist_ok=True)
        with open(article_dir / 'article.json', 'w') as f:
            json.dump(data, f, indent=2)
        with open(article_dir / 'content.txt', 'w') as f:
            f.write(content)
        
        idx_entry = {k: data.get(k, '') for k in ['slug', 'title', 'date', 'url', 'word_count', 'images_downloaded']}
        idx_entry['image_count'] = len(images)
        index.append(idx_entry)
        
        if done % 10 == 0:
            with open(OUT / 'index.json', 'w') as f:
                json.dump(index, f, indent=2)
            log(f'  Checkpoint: {done} done, {art_total} images, {errors} errors')
        
        time.sleep(SLEEP)
    
    with open(OUT / 'index.json', 'w') as f:
        json.dump(index, f, indent=2)
    
    log(f'\nDONE: {done} articles, {art_total} images, {errors} errors')
    log(f'Index: {OUT / "index.json"}')

if __name__ == '__main__':
    main()
