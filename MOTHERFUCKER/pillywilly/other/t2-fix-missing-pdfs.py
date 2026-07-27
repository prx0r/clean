#!/usr/bin/env python3
"""
Fix broken PDF references: find PMC IDs for papers with missing PDFs
and download them via OA FTP or publisher direct patterns.
"""
import glob, json, os, re, sys, time, subprocess, tarfile
import urllib.request, urllib.parse, xml.etree.ElementTree as ET

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0

os.makedirs(LIBRARY, exist_ok=True)

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesPDFFix/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None
    return None

def find_pmc_via_esummary(pmid):
    """Find PMC ID from PMID using NCBI ESummary."""
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}")
    if not data: return None
    try:
        parsed = json.loads(data)
        result = parsed.get("result", {})
        for uid, doc in result.items():
            if uid == "uids": continue
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "pmc":
                    return aid.get("value", "")
    except: pass
    return None

def find_pmc_via_europepmc(doi):
    if not doi: return None
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json"
    time.sleep(0.5)
    data = api_call(url)
    if not data: return None
    try:
        parsed = json.loads(data)
        results = parsed.get("resultList", {}).get("result", [])
        if results:
            pmcid = results[0].get("pmcid", "")
            if pmcid and pmcid.startswith("PMC"):
                return pmcid
    except: pass
    return None

def download_pmc_pdf(pmc_id, title):
    if not pmc_id: return None
    pmc_clean = pmc_id.replace("PMC", "").strip()
    time.sleep(DELAY)
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_clean}"
    data = api_call(oa_url)
    if not data: return None
    try:
        root = ET.fromstring(data)
        if root.find(".//error") is not None: return None
        record = root.find(".//record")
        if record is None: return None
        link = record.find('link[@format="tgz"]')
        if link is None: return None
        ftp_href = link.get("href")
        if not ftp_href: return None
    except: return None
    https_url = ftp_href.replace("ftp://", "https://").replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/")
    local_tgz = f"/tmp/pdf_fix_{pmc_clean}.tar.gz"
    try:
        subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "120", "-o", local_tgz, https_url], check=True, timeout=130)
    except: return None
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000: return None
    try:
        dest_name = f"t2-PMC{pmc_clean}_{re.sub(r'[^a-zA-Z0-9]+', '_', title)[:40].strip('_')}.pdf"
        dest_path = os.path.join(LIBRARY, dest_name)
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name]
            if not pdfs: pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs: return None
            tar.extract(pdfs[0], path="/tmp/pdf_extract/")
            src = os.path.join("/tmp/pdf_extract/", pdfs[0].name)
            import shutil
            shutil.move(src, dest_path)
        result = subprocess.run(["file", "-b", dest_path], capture_output=True, text=True)
        if "PDF document" in result.stdout and os.path.getsize(dest_path) > 5000:
            return dest_name
    except: return None
    finally:
        subprocess.run(["rm", "-rf", "/tmp/pdf_extract/"])
        if os.path.exists(local_tgz):
            try: os.remove(local_tgz)
            except: pass
    return None

def download_publisher_pdf(doi, journal):
    jl = journal.lower()
    if "frontiers" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://journal.frontiersin.org/article/{doi}/pdf"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000: return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    if "springer" in jl or "biomed" in jl or "bmc" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://link.springer.com/content/pdf/{doi}.pdf"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000: return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    if "nature" in jl or "scientific reports" in jl:
        doi_parts = doi.split("/")
        if len(doi_parts) >= 2:
            art_id = doi_parts[-1]
            try:
                dest = f"{LIBRARY}/t2-pubmed-{art_id}.pdf"
                subprocess.run(["curl", "-sL", "-o", dest, f"https://www.nature.com/articles/{art_id}.pdf"], timeout=30)
                r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
                if "PDF document" in r.stdout and os.path.getsize(dest) > 5000: return f"t2-pubmed-{art_id}.pdf"
                else:
                    try: os.remove(dest)
                    except: pass
            except: pass
    if "elife" in jl:
        doi_parts = doi.split("/")
        if len(doi_parts) >= 2:
            art_id = doi_parts[-1]
            try:
                dest = f"{LIBRARY}/t2-elife-{art_id}.pdf"
                subprocess.run(["curl", "-sL", "-o", dest, f"https://cdn.elifesciences.org/articles/{art_id}/elife-{art_id}-v1.pdf"], timeout=30)
                r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
                if "PDF document" in r.stdout and os.path.getsize(dest) > 5000: return f"t2-elife-{art_id}.pdf"
                else:
                    try: os.remove(dest)
                    except: pass
            except: pass
    if "plos" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000: return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    return None

def fix_pdfs():
    works = sorted(glob.glob(f"{WORKS_DIR}/t2-*.json"))
    print(f"Total works: {len(works)}")

    fixed = 0
    skipped = 0
    no_pmid = 0
    for w in works:
        try:
            d = json.load(open(w))
        except:
            continue

        pdf = d.get("assets", {}).get("pdf_path", "")
        if not pdf:
            continue

        full_path = os.path.join(LIBRARY, pdf)
        if os.path.exists(full_path) and os.path.getsize(full_path) > 5000:
            continue  # PDF exists, skip

        # Check if already a known-non-existent path
        pmid = d.get("identifiers", {}).get("pmid", "")
        doi = d.get("identifiers", {}).get("doi", "")
        title = d.get("title", "")
        journal = d.get("publication", {}).get("journal", "")

        if not pmid or pmid == "?":
            no_pmid += 1
            continue

        print(f"\nFixing: PMID={pmid} doi={doi} — {title[:60]}...", flush=True)

        # 1. Try publisher direct (fastest, no PMC fetch needed)
        if doi:
            pdf_name = download_publisher_pdf(doi, journal)
            if pdf_name:
                d["assets"]["pdf_path"] = pdf_name
                d["provenance"]["oa_status"] = "green"
                with open(w, "w") as f:
                    json.dump(d, f, indent=2, ensure_ascii=False)
                fixed += 1
                print(f"  ✅ Publisher PDF: {pdf_name}")
                continue

        # 2. Find PMC ID via ESummary
        pmc_id = find_pmc_via_esummary(pmid)
        if not pmc_id and doi:
            pmc_id = find_pmc_via_europepmc(doi)
        if not pmc_id:
            print(f"  ❌ No PMC ID found")
            skipped += 1
            # Clear the broken pdf_file reference
            d["assets"]["pdf_path"] = None
            with open(w, "w") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            continue

        # 3. Download via OA FTP
        pdf_name = download_pmc_pdf(pmc_id, title)
        if pdf_name:
            d["assets"]["pdf_path"] = pdf_name
            d["provenance"]["oa_status"] = "green"
            with open(w, "w") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            fixed += 1
            print(f"  ✅ OA FTP: {pdf_name}")
        else:
            print(f"  ❌ OA download failed (PMC={pmc_id})")
            d["assets"]["pdf_path"] = None
            with open(w, "w") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            skipped += 1

    print(f"\n{'='*50}")
    print(f"PDF Fix Complete: {fixed} fixed, {skipped} skipped (no PDF available), {no_pmid} without PMIDs")
    print(f"{'='*50}")

if __name__ == "__main__":
    fix_pdfs()
