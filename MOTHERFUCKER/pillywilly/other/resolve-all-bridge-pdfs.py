#!/usr/bin/env python3
"""
resolve-all-bridge-pdfs.py — Comprehensive PDF/XML resolution for bridge papers.

For each paper needing a PDF, attempts in order:
1. Publisher direct download (Frontiers, Springer/BMC, eLife, PLoS, Nature/SciRep)
2. EuropePMC API to verify PMC ID
3. efetch XML for PMC papers (full-text NXML)
4. Logs what remains blocked

Usage: python3 scripts/resolve-all-bridge-pdfs.py
"""
import json, os, urllib.request, urllib.parse, time, subprocess, re, glob, sys
import xml.etree.ElementTree as ET

PROJECT = "/root/projects/blog"
WORKS_DIR = f"{PROJECT}/content/works"
ESSAYS_DIR = f"{PROJECT}/content/glossary/essays"
FRONTIER_DIR = f"{PROJECT}/library/frontier"
os.makedirs(FRONTIER_DIR, exist_ok=True)

DELAY = 1.0  # seconds between API calls

# PMIDs we've already tried
SEEN_PMIDS = set()

def log(msg):
    print(msg, flush=True)

def safe_delay():
    time.sleep(DELAY)

def fetch_url(url, retries=2):
    """Fetch URL with retries. Returns (content, content_type) or (None, None)."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                ct = resp.headers.get("Content-Type", "")
                return data, ct
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
    return None, None

def check_pdf(data):
    """Check if content is a valid PDF."""
    if not data or len(data) < 5000:
        return False
    return data[:4] == b"%PDF"

def save_pdf(data, dest_name):
    """Save and verify PDF."""
    dest = f"{FRONTIER_DIR}/{dest_name}"
    with open(dest, "wb") as f:
        f.write(data)
    # Verify
    result = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
    if "PDF document" in result.stdout:
        size_kb = len(data) / 1024
        log(f"  ✅ Saved PDF ({size_kb:.0f} KB): {dest_name}")
        return dest_name
    else:
        os.remove(dest)
        log(f"  ❌ Fake PDF (got: {result.stdout.strip()}): {dest_name}")
        return None

def try_frontiers(doi):
    """Frontiers PDF pattern — confirmed working."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    url = f"https://journal.frontiersin.org/article/{doi_clean}/pdf"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"frontiers-{doi_clean.split('/')[-1]}.pdf"), data
    return None, None

def try_plos_one(doi):
    """PLOS ONE PDF pattern — confirmed working with id BEFORE type."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    url = f"https://journals.plos.org/plosone/article/file?id={doi_clean}&type=printable"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"plos-{doi_clean.split('/')[-1]}.pdf"), data
    return None, None

def try_nature(doi):
    """Nature/SciRep PDF pattern — confirmed working."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    # Extract the part after s41598- or s42003- etc
    suffix = doi_clean.split("/")[-1]
    url = f"https://www.nature.com/articles/{suffix}.pdf"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"nature-{suffix}.pdf"), data
    return None, None

def try_springer_bmc(doi):
    """Springer/BMC PDF pattern — confirmed working."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    url = f"https://link.springer.com/content/pdf/{doi_clean}.pdf"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"springer-{doi_clean.split('/')[-1]}.pdf"), data
    return None, None

def try_elife(doi):
    """eLife PDF pattern — confirmed working."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    article_id = doi_clean.split("/")[-1]
    url = f"https://cdn.elifesciences.org/articles/{article_id}/elife-{article_id}-v1.pdf"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"elife-{article_id}.pdf"), data
    return None, None

def try_biorxiv(doi):
    """bioRxiv PDF pattern."""
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    id_part = "/".join(doi_clean.split("/")[1:])
    url = f"https://www.biorxiv.org/content/10.1101/{id_part}.full.pdf"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"biorxiv-{id_part.replace('/','-')}.pdf"), data
    return None, None

def try_europepmc_pdf(pmc_id):
    """EuropePMC PDF download (may return HTML for non-OA)."""
    pmc_clean = pmc_id.replace("PMC", "")
    url = f"https://www.ebi.ac.uk/europepmc/api/download/PMC{pmc_clean}"
    data, ct = fetch_url(url)
    if data and check_pdf(data):
        return save_pdf(data, f"PMC{pmc_clean}.pdf"), data
    return None, None

def publishers_direct(doi, journal):
    """Try publisher direct download based on journal name."""
    journal_lower = journal.lower()
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")

    if "frontiers" in journal_lower:
        return try_frontiers(doi)
    if "plos" in journal_lower or "plos one" in journal_lower:
        return try_plos_one(doi)
    if "scientific reports" in journal_lower or "nature" in journal_lower:
        return try_nature(doi)
    if "springer" in journal_lower or "bmc" in journal_lower or "biomed central" in journal_lower:
        return try_springer_bmc(doi)
    if "elife" in journal_lower:
        return try_elife(doi)
    if "biorxiv" in journal_lower or "medrxiv" in journal_lower:
        return try_biorxiv(doi)
    return None, None

def get_epmc_info(pmid):
    """Get PMC ID and OA status from EuropePMC API."""
    safe_delay()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=(ext_id:{pmid})&format=json"
    try:
        data, _ = fetch_url(url)
        if data:
            results = json.loads(data).get("resultList", {}).get("result", [])
            if results:
                r = results[0]
                pmcid = r.get("pmcid", "")
                is_oa = r.get("isOpenAccess", "N") == "Y"
                has_pdf = r.get("hasPDF", "N") == "Y"
                title = r.get("title", "")
                doi = r.get("doi", "")
                return pmcid, is_oa, has_pdf, title, doi
    except:
        pass
    return None, False, False, "", ""

def fetch_efetch_xml(pmcid):
    """Get full-text NXML via efetch. Works for ALL PMC papers regardless of OA status."""
    pmc_clean = pmcid.replace("PMC", "")
    safe_delay()
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_clean}&retmode=xml"
    try:
        data, _ = fetch_url(url)
        if data and len(data) > 2000:
            fname = f"PMC{pmc_clean}.nxml"
            dest = f"{FRONTIER_DIR}/{fname}"
            with open(dest, "wb") as f:
                f.write(data)
            size_kb = len(data) / 1024
            log(f"  ✅ Saved NXML ({size_kb:.0f} KB): {fname}")
            return fname
    except Exception as e:
        log(f"  ❌ efetch XML failed: {e}")
    return None

def update_work_json(work_path, pdf_file=None, nxml_file=None, pmc_id=None):
    """Update work JSON with download results."""
    with open(work_path) as f:
        data = json.load(f)
    
    changes = []
    if pdf_file:
        data["pdf_file"] = pdf_file
        if "assets" in data:
            data["assets"]["pdf_path"] = pdf_file
        changes.append(f"pdf_file={pdf_file}")
    if nxml_file:
        data["nxml_file"] = nxml_file
        changes.append(f"nxml_file={nxml_file}")
    if pmc_id:
        data["pmc_id"] = pmc_id
    
    if changes:
        with open(work_path, "w") as f:
            json.dump(data, f, indent=2)
        log(f"  📝 Updated work JSON: {', '.join(changes)}")

def process_single_paper(work_path):
    """Process a single paper: try PDF download, fall back to efetch XML."""
    with open(work_path) as f:
        data = json.load(f)
    
    wid = data.get("id") or data.get("work_id", "")
    title = data.get("title", "")[:80]
    pmid = data.get("pmid") or data.get("identifiers", {}).get("pmid", "")
    doi = data.get("doi") or data.get("identifiers", {}).get("doi", "")
    journal = data.get("journal") or data.get("publication", {}).get("journal", "")
    phase = data.get("phase") or data.get("phase_mapping", {}).get("phase", "")
    
    # Check if already resolved
    pdf = data.get("pdf_file") or data.get("assets", {}).get("pdf_path")
    nxml = data.get("nxml_file")
    if pdf:
        pdf_full = f"{FRONTIER_DIR}/{os.path.basename(pdf)}"
        if os.path.exists(pdf_full):
            return f"  ⏭️ Already has PDF: {pdf}"
    
    log(f"\n📄 {wid}")
    log(f"   {title}")
    log(f"   PMID={pmid} DOI={doi} Journal={journal}")
    
    # Step 1: Try publisher direct download
    if doi:
        pdf_name, pdf_data = publishers_direct(doi, journal)
        if pdf_name:
            update_work_json(work_path, pdf_file=pdf_name)
            return f"  ✅ PDF downloaded: {pdf_name}"
    
    # Step 2: Check EuropePMC for PMC ID
    pmc_id = data.get("pmc_id") or data.get("pmc_id")
    if not pmc_id and pmid:
        log(f"   🔍 Looking up PMC ID via EuropePMC...")
        pmc_id, is_oa, has_pdf, ep_title, ep_doi = get_epmc_info(pmid)
        if pmc_id:
            log(f"   Found PMC ID: {pmc_id} (OA={is_oa}, hasPDF={has_pdf})")
    
    # Step 3: Try efetch XML (works for ALL PMC papers)
    if pmc_id:
        nxml_name = fetch_efetch_xml(pmc_id)
        if nxml_name:
            update_work_json(work_path, nxml_file=nxml_name, pmc_id=pmc_id)
            return f"  ✅ NXML downloaded: {nxml_name}"
        else:
            log(f"   ⚠️ efetch XML returned no content")
    
    # Step 4: Try EuropePMC PDF as last resort
    if pmc_id:
        pdf_name, pdf_data = try_europepmc_pdf(pmc_id)
        if pdf_name:
            update_work_json(work_path, pdf_file=pdf_name, pmc_id=pmc_id)
            return f"  ✅ PDF via EuropePMC: {pdf_name}"
    
    log(f"  ❌ No download method worked")
    return f"  ❌ Blocked (publisher={journal})"

def find_bridge_papers():
    """Find all bridge papers that need PDFs."""
    needs_pdf = []
    
    # Source atlas bridges (older format)
    for wf in glob.glob(f"{WORKS_DIR}/bridge-*.json"):
        needs_pdf.append(wf)
    
    # Phase 16 new papers (v2 format)
    for wf in glob.glob(f"{WORKS_DIR}/t2-pubmed-*.json"):
        with open(wf) as f:
            data = json.load(f)
        pm = data.get("phase_mapping", {})
        phase = pm.get("phase", 0)
        phase_name = pm.get("phase_name", "")
        
        # Only Phase 16 papers
        if phase == 16 or "nondual" in phase_name.lower() or "unity" in phase_name.lower() or "oceanic" in phase_name.lower():
            pdf = data.get("assets", {}).get("pdf_path")
            if not pdf or pdf == "null":
                pdf = data.get("pdf_file")
            if not pdf or pdf == "null":
                needs_pdf.append(wf)
    
    return sorted(set(needs_pdf))

def main():
    log("=" * 70)
    log("Bridge Paper PDF/XML Resolution")
    log("=" * 70)
    
    papers = find_bridge_papers()
    log(f"\nFound {len(papers)} papers needing PDF/XML downloads\n")
    
    results = {"pdf_ok": 0, "nxml_ok": 0, "blocked": 0, "skipped": 0}
    summary = []
    
    for i, wp in enumerate(papers):
        result = process_single_paper(wp)
        summary.append((wp, result))
        if "✅ PDF" in result:
            results["pdf_ok"] += 1
        elif "✅ NXML" in result:
            results["nxml_ok"] += 1
        elif "⏭️" in result:
            results["skipped"] += 1
        else:
            results["blocked"] += 1
    
    log("\n" + "=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log(f"Total papers processed: {len(papers)}")
    log(f"  PDFs downloaded: {results['pdf_ok']}")
    log(f"  NXMLs downloaded: {results['nxml_ok']}")
    log(f"  Blocked: {results['blocked']}")
    log(f"  Already had: {results['skipped']}")
    
    # Save summary
    summary_path = f"{PROJECT}/scripts/resolution-results.json"
    with open(summary_path, "w") as f:
        json.dump({
            "results": results,
            "papers": [(os.path.basename(wp), result) for wp, result in summary]
        }, f, indent=2)
    log(f"\nResults saved to {summary_path}")

if __name__ == "__main__":
    main()
