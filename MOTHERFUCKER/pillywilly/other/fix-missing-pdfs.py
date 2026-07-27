#!/usr/bin/env python3
"""
Fix missing PDFs for existing bridge paper works.
For each work with a missing PDF, try to find PMC ID via EuropePMC,
then download PDF via OA Service API + HTTPS deprecated path.
"""
import glob, json, os, re, sys, time, subprocess, tarfile, urllib.request, xml.etree.ElementTree as ET

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/2.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None
    return None

def find_pmc_via_europepmc(doi):
    """Find PMC ID from DOI using EuropePMC REST API."""
    if not doi:
        return None
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json"
    time.sleep(0.5)
    data = api_call(url)
    if not data:
        return None
    try:
        parsed = json.loads(data)
        results = parsed.get("resultList", {}).get("result", [])
        if results:
            pmcid = results[0].get("pmcid", "")
            if pmcid and pmcid.startswith("PMC"):
                return pmcid
            return None
    except:
        return None
    return None

def find_pmc_via_esummary(pmid):
    """Find PMC ID from PMID using NCBI ESummary."""
    if not pmid:
        return None
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json&email={EMAIL}"
    time.sleep(DELAY)
    data = api_call(url)
    if not data:
        return None
    try:
        parsed = json.loads(data)
        for uid, doc in parsed.get("result", {}).items():
            if uid == "uids":
                continue
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "pmc":
                    return aid.get("value", "")
    except:
        return None
    return None

def download_pmc_pdf(pmc_id, output_dir):
    """Download PDF via OA Service API + HTTPS deprecated path."""
    pmc_clean = pmc_id.replace("PMC", "").strip()
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_clean}"
    time.sleep(DELAY)
    data = api_call(oa_url)
    if not data:
        return None
    try:
        root = ET.fromstring(data)
        if root.find(".//error") is not None:
            return None
        record = root.find(".//record")
        if record is None:
            return None
        link = record.find('link[@format="tgz"]')
        if link is None:
            return None
        ftp_href = link.get("href")
        if not ftp_href:
            return None
    except Exception as e:
        print(f"    OA parse error: {e}")
        return None
    
    https_url = ftp_href.replace("ftp://", "https://")
    https_url = https_url.replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/")
    
    local_tgz = f"/tmp/pmc_{pmc_clean}.tar.gz"
    try:
        subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "120",
                       "-o", local_tgz, https_url], check=True, timeout=130)
    except:
        return None
    
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000:
        return None
    
    try:
        dest_name = f"PMC{pmc_clean}.pdf"
        dest_path = os.path.join(output_dir, dest_name)
        
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = sorted(
                [m for m in tar.getmembers() if m.name.endswith(".pdf") 
                 and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name],
                key=lambda m: m.size, reverse=True
            )
            if not pdfs:
                pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs:
                os.remove(local_tgz)
                return None
            
            tar.extract(pdfs[0], path="/tmp/pmc_extract/")
            src = os.path.join("/tmp/pmc_extract/", pdfs[0].name)
            if os.path.exists(src):
                import shutil
                shutil.move(src, dest_path)
        
        os.remove(local_tgz)
        subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
        
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
            # Verify it's really a PDF
            result = subprocess.run(["file", "-b", dest_path], capture_output=True, text=True)
            if "PDF document" in result.stdout:
                return dest_name
        
        if os.path.exists(dest_path) and os.path.getsize(dest_path) < 5000:
            os.remove(dest_path)
        return None
    except Exception as e:
        print(f"    Extraction error: {e}")
        return None
    finally:
        if os.path.exists(local_tgz):
            try: os.remove(local_tgz)
            except: pass

def main():
    os.makedirs(LIBRARY, exist_ok=True)
    
    # Load all works
    all_works = sorted(glob.glob(f"{WORKS_DIR}/t2-*.json"))
    print(f"Found {len(all_works)} total works")
    
    # Find works with missing PDFs
    missing = []
    for w in all_works:
        try:
            data = json.load(open(w))
        except:
            continue
        assets = data.get("assets", {})
        pdf_path = assets.get("pdf_path", "")
        if pdf_path:
            pdf_file = os.path.join(LIBRARY, os.path.basename(pdf_path))
            if not os.path.exists(pdf_file):
                missing.append((w, data, pdf_path))
    
    print(f"Works with missing PDFs: {len(missing)}")
    
    # Try to find PMC IDs and download
    fixed = 0
    not_oa = 0
    no_pmc = 0
    failed = 0
    
    for i, (w_path, data, old_pdf_path) in enumerate(missing):
        title = data.get("title", "?")[:60]
        doi = data.get("identifiers", {}).get("doi", "")
        pmid = data.get("identifiers", {}).get("pmid", "")
        
        print(f"\n[{i+1}/{len(missing)}] PMID:{pmid} DOI:{doi}")
        print(f"  Title: {title}")
        
        # Try EuropePMC first (most reliable)
        pmc_id = find_pmc_via_europepmc(doi)
        if pmc_id:
            print(f"  EuropePMC found: {pmc_id}")
        else:
            # Try ESummary as fallback
            pmc_id = find_pmc_via_esummary(pmid)
            if pmc_id:
                print(f"  ESummary found: {pmc_id}")
            else:
                print(f"  No PMC ID found")
                no_pmc += 1
                continue
        
        # Try to download
        result = download_pmc_pdf(pmc_id, LIBRARY)
        if result:
            print(f"  ✅ Downloaded: {result}")
            # Update work JSON
            new_pdf_path = result  # relative to LIBRARY
            data["assets"]["pdf_path"] = new_pdf_path
            with open(w_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            fixed += 1
        else:
            print(f"  ❌ Could not download PDF (not OA or download failed)")
            not_oa += 1
    
    print(f"\n{'='*60}")
    print(f"PDF Fix Results:")
    print(f"  Total missing: {len(missing)}")
    print(f"  Fixed (PDF downloaded): {fixed}")
    print(f"  No PMC ID found: {no_pmc}")
    print(f"  Not OA or download failed: {not_oa}")

if __name__ == "__main__":
    main()
