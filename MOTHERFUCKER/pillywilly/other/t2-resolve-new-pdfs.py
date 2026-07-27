#!/usr/bin/env python3
"""Resolve PDFs for newly acquired papers via Unpaywall + direct publisher download."""
import json, time, urllib.request, urllib.parse, urllib.error, os, re, glob

WORK_DIR = "/root/projects/blog"
WORKS_DIR = os.path.join(WORK_DIR, "content/works")
FRONTIER_DIR = os.path.join(WORK_DIR, "library/frontier")
os.makedirs(FRONTIER_DIR, exist_ok=True)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]

def try_unpaywall(doi):
    url = f"https://api.unpaywall.org/v2/{doi}?email=hermes@research.local"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        best = data.get("best_oa_location", {}) or {}
        return best.get("url_for_pdf", "")
    except:
        return ""

def try_doi_org(doi):
    """Resolve DOI and follow redirect to get publisher URL, then construct PDF."""
    try:
        req = urllib.request.Request(f"https://doi.org/{doi}", headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        final_url = resp.url
        
        # Construct PDF URL based on publisher
        if "frontiersin.org" in final_url:
            match = re.search(r'article/([^/]+)', final_url)
            if match:
                return f"https://www.frontiersin.org/journals/articles/{match.group(1)}/pdf"
        if "mdpi.com" in final_url:
            return final_url.rstrip('/') + '/pdf'
        if "nature.com" in final_url:
            parts = doi.split('/')
            return f"https://www.nature.com/articles/{parts[-1]}.pdf"
        if "springer" in final_url or "link.springer.com" in final_url:
            return f"https://link.springer.com/content/pdf/{doi}.pdf"
        if "plos.org" in final_url or "journals.plos.org" in final_url:
            return f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable"
        if "tandfonline.com" in final_url:
            return f"https://www.tandfonline.com/doi/pdf/{doi}"
        if "sagepub.com" in final_url or "sage" in final_url:
            return f"https://journals.sagepub.com/doi/pdf/{doi}"
        if "oxfordjournals" in final_url or "oup.com" in final_url:
            return f"https://academic.oup.com/doi/pdf/{doi}"
        if "biorxiv.org" in final_url:
            return final_url + ".full.pdf"
        if "wiley.com" in final_url:
            return f"https://onlinelibrary.wiley.com/doi/pdf/{doi}"
        if "elsevier" in final_url or "sciencedirect" in final_url:
            return f"https://www.sciencedirect.com/science/article/pii/{doi.split('/')[-1]}/pdfft"
    except:
        pass
    return ""

def download_pdf(url, filepath):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/pdf,*/*"
        })
        resp = urllib.request.urlopen(req, timeout=30)
        data = resp.read()
        is_pdf = data[:4] == b'%PDF'
        if not is_pdf and data[:4] == b'%P%':
            # Some PDFs start with %PDF-1.x
            is_pdf = b'%PDF' in data[:100]
        if is_pdf:
            with open(filepath, 'wb') as f:
                f.write(data)
            return len(data), True
        return len(data), False
    except Exception as e:
        return 0, False

def main():
    # Get all papers still missing PDFs
    works = sorted(glob.glob(os.path.join(WORKS_DIR, "t2-*.json")))
    todo = []
    for wf in works:
        with open(wf) as f:
            data = json.load(f)
        pdf_path = data.get("assets", {}).get("pdf_path", "")
        if not pdf_path or not os.path.exists(os.path.join(WORK_DIR, pdf_path.lstrip('/'))):
            doi = data.get("identifiers", {}).get("doi", "")
            if doi:
                todo.append((wf, data, doi))
    
    print(f"Papers needing PDFs: {len(todo)}")
    
    downloaded = 0
    failed = 0
    
    for wf, data, doi in todo:
        title = data.get('title', '')[:60]
        phase = data.get('phase_mapping', {}).get('phase', '?')
        pn = data.get('phase_mapping', {}).get('phase_name', '?')
        
        # Try Unpaywall first
        pdf_url = try_unpaywall(doi)
        time.sleep(1.1)
        
        if not pdf_url:
            # Fallback: direct DOI resolution + pattern matching
            pdf_url = try_doi_org(doi)
            time.sleep(0.5)
        
        if not pdf_url:
            print(f"  ⚠️ No URL: Phase {phase:2d} ({pn}): {title}")
            failed += 1
            continue
        
        slug = slugify(f"t2-{title}")
        pdf_path = os.path.join(FRONTIER_DIR, f"{slug}.pdf")
        
        size, is_pdf = download_pdf(pdf_url, pdf_path)
        time.sleep(0.5)
        
        if size > 0 and is_pdf:
            rel_path = f"library/frontier/{slug}.pdf"
            data["assets"]["pdf_path"] = rel_path
            with open(wf, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✅ Phase {phase:2d} ({pn}): {title} — {size/1024:.0f} KB")
            downloaded += 1
        else:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            print(f"  ❌ Phase {phase:2d} ({pn}): {title} — failed (size={size})")
            failed += 1
    
    print(f"\n=== Results ===")
    print(f"Downloaded: {downloaded}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()
