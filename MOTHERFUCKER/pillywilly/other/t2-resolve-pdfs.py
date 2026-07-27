#!/usr/bin/env python3
"""
Resolve PDFs for all T2 bridge papers using Unpaywall + direct publisher URL patterns.
Saves to library/frontier/<doi-slug>.pdf and updates work JSONs.
"""
import glob, json, time, urllib.request, urllib.parse, urllib.error, os, sys, re, hashlib

WORK_DIR = "/root/projects/blog"
WORKS_DIR = os.path.join(WORK_DIR, "content/works")
FRONTIER_DIR = os.path.join(WORK_DIR, "library/frontier")
os.makedirs(FRONTIER_DIR, exist_ok=True)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]

def fetch_pdf_url_via_unpaywall(doi):
    """Try Unpaywall API for PDF URL."""
    url = f"https://api.unpaywall.org/v2/{doi}?email=hermes@research.local"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        best_loc = data.get("best_oa_location", {}) or {}
        pdf_url = best_loc.get("url_for_pdf", "")
        host_type = best_loc.get("host_type", "")
        if pdf_url:
            return pdf_url
        # Fallback: try to construct PDF URL from landing page
        landing = best_loc.get("url_for_landing_page", "") or data.get("doi_url", "")
        if landing:
            return construct_pdf_url(landing, doi)
    except Exception as e:
        return None

def construct_pdf_url(landing_url, doi):
    """Try common publisher PDF URL patterns as fallback."""
    doi_encoded = urllib.parse.quote(doi, safe='')
    
    # Publisher-specific patterns
    if "frontiersin.org" in landing_url or "frontiers" in landing_url:
        # Frontiers: https://www.frontiersin.org/journals/xxx/articles/xxx/pdf
        match = re.search(r'article/([^/]+)', landing_url)
        if match:
            article_id = match.group(1)
            return f"https://www.frontiersin.org/journals/articles/{article_id}/pdf"
    
    if "mdpi.com" in landing_url:
        # MDPI: already provides PDF URLs via Unpaywall usually
        # But try: https://www.mdpi.com/1099-4300/23/6/783/pdf
        match = re.search(r'/[\d]+-[\d]+/[\d]+/[\d]+', landing_url)
        if match:
            return landing_url.rstrip('/') + '/pdf'
    
    if "plos.org" in landing_url or "journals.plos.org" in landing_url:
        match = re.search(r'id=([^&]+)', landing_url)
        if match:
            doi_full = match.group(1)
            return f"https://journals.plos.org/plosone/article/file?id={doi_full}&type=printable"
    
    if "springer.com" in landing_url or "link.springer.com" in landing_url:
        # Try: https://link.springer.com/content/pdf/10.xxx/xxxxx.pdf
        return f"https://link.springer.com/content/pdf/{doi}.pdf"
    
    if "nature.com" in landing_url or "s41467" in doi:
        return f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf"
    
    if "sciencedirect" in landing_url or "elsevier" in landing_url or landing_url.endswith(doi):
        # Many Elsevier papers are not OA, but try
        pass
    
    return None

def download_pdf(url, filepath):
    """Download a PDF from URL to filepath."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/pdf,*/*"
        })
        resp = urllib.request.urlopen(req, timeout=30)
        data = resp.read()
        
        # Check if it's actually a PDF
        is_pdf = data[:4] == b'%PDF'
        
        with open(filepath, 'wb') as f:
            f.write(data)
        return len(data), is_pdf
    except Exception as e:
        return 0, False

def main():
    works = sorted(glob.glob(os.path.join(WORKS_DIR, "t2-*.json")))
    print(f"Total work files: {len(works)}")
    
    results = {"downloaded": 0, "failed": 0, "skipped": 0, "bytes": 0}
    
    for wf in works:
        with open(wf) as f:
            data = json.load(f)
        
        # Check if PDF already resolved
        existing_pdf = data.get("assets", {}).get("pdf_path", "")
        if existing_pdf and os.path.exists(os.path.join(WORK_DIR, existing_pdf.lstrip('/'))):
            results["skipped"] += 1
            continue
        
        doi = data.get("identifiers", {}).get("doi", "")
        title = data.get("title", "")
        phase = data.get("phase_mapping", {}).get("phase", "?")
        phase_name = data.get("phase_mapping", {}).get("phase_name", "?")
        
        if not doi:
            results["failed"] += 1
            continue
        
        pdf_url = fetch_pdf_url_via_unpaywall(doi)
        time.sleep(1.1)  # Rate limit
        
        if not pdf_url:
            results["failed"] += 1
            print(f"  ⚠️ No PDF URL for Phase {phase:2d} ({phase_name}): {title[:60]}")
            continue
        
        # Create safe filename
        slug = slugify(title[:60])
        pdf_path = os.path.join(FRONTIER_DIR, f"t2-{slug}.pdf")
        
        size, is_pdf = download_pdf(pdf_url, pdf_path)
        time.sleep(0.5)
        
        if size > 0 and is_pdf:
            # Update work JSON
            data.setdefault("assets", {})["pdf_path"] = f"library/frontier/t2-{slug}.pdf"
            data.setdefault("assets", {})["source_url"] = pdf_url
            with open(wf, 'w') as f:
                json.dump(data, f, indent=2)
            
            results["downloaded"] += 1
            results["bytes"] += size
            print(f"  ✅ Phase {phase:2d} ({phase_name}): {title[:60]} — {size/1024:.0f} KB")
        else:
            results["failed"] += 1
            if os.path.exists(pdf_path) and size == 0:
                os.remove(pdf_path)
            print(f"  ❌ Phase {phase:2d} ({phase_name}): {title[:60]} — download failed (size={size}, pdf={is_pdf})")
    
    print(f"\n=== Results ===")
    print(f"Downloaded: {results['downloaded']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped (already had PDF): {results['skipped']}")
    print(f"Total bytes: {results['bytes']/1024/1024:.1f} MB")

if __name__ == "__main__":
    main()
