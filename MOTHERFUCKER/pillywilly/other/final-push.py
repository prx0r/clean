#!/usr/bin/env python3
"""Final push: fill Phase 16 and Phase 17 to reach 50 each."""
import glob, json, os, re, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET, subprocess, tarfile, shutil

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/3.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except:
            if attempt < 2: time.sleep(2 * (attempt + 1))
            else: return None
    return None

def search(query, retmax=25):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch_summary(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}")
    if not data: return {}
    result = {}
    try:
        parsed = json.loads(data)
        for uid, doc in parsed.get("result", {}).items():
            if uid == "uids": continue
            doi = pmc = ""
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "doi": doi = aid.get("value", "")
                if aid.get("idtype") == "pmc": pmc = aid.get("value", "")
            result[uid] = {"title": doc.get("title",""), "source": doc.get("source",""), "pubdate": doc.get("pubdate",""), "doi": doi, "pmc": pmc,
                "authors": [a.get("name","") for a in doc.get("authors",[])[:5]]}
    except: pass
    return result

def fetch_abstracts(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params}")
    if not data: return {}
    articles = {}
    try:
        root = ET.fromstring(data)
        for article in root.findall(".//PubmedArticle"):
            pmid_el = article.find(".//PMID")
            if pmid_el is None or not pmid_el.text: continue
            pmid = pmid_el.text.strip()
            te = article.find(".//ArticleTitle")
            title = "".join(te.itertext()).strip() if te is not None else ""
            abs_parts = []
            for ae in article.findall(".//AbstractText"):
                txt = "".join(ae.itertext()).strip()
                if txt: abs_parts.append(txt)
            abstract = " ".join(abs_parts)
            ye = article.find(".//PubDate/Year")
            if ye is None: ye = article.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            articles[pmid] = {"title": title, "abstract": abstract, "year": year}
    except: pass
    return articles

def score_text(title, abstract, terms):
    text = f"{title} {abstract}".lower()
    noise = ["clinical trial", "pharmacological", "treatment outcome", "case report", "rat ", " mice ", "murine", "animal model"]
    for n in noise:
        if n in text: return 0, f"Noise: '{n}'"
    cross = [("neural",0.3),("brain",0.2),("fMRI",0.4),("neuroimaging",0.5),("cortex",0.3),("EEG",0.4),("mechanism",0.5)]
    score = sum(w for t, w in terms if t in text)
    score += sum(w for t, w in cross if t in text)
    if score >= 3.5: return score, f"Excellent (score={score:.1f})"
    elif score >= 2.5: return score, f"Good (score={score:.1f})"
    elif score >= 2.0: return score, f"Good (score={score:.1f})"
    elif score >= 1.5: return score, f"Marginal (score={score:.1f})"
    else: return score, f"Low signal (score={score:.1f})"

def download_pmc_pdf(pmc_id, title):
    if not pmc_id: return None
    pmc_clean = pmc_id.replace("PMC","").strip()
    time.sleep(DELAY)
    data = api_call(f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_clean}")
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
    https_url = ftp_href.replace("ftp://","https://").replace("/pub/pmc/oa_package/","/pub/pmc/deprecated/oa_package/")
    local_tgz = f"/tmp/pmc_{pmc_clean}.tar.gz"
    try: subprocess.run(["curl","-sL","--connect-timeout","30","--max-time","120","-o",local_tgz,https_url], check=True, timeout=130)
    except: return None
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000: return None
    try:
        dest_name = f"t2-PMC{pmc_clean}_{re.sub(r'[^a-zA-Z0-9]+','_',title)[:40].strip('_')}.pdf"
        dest_path = os.path.join(LIBRARY, dest_name)
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name]
            if not pdfs: pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs: return None
            tar.extract(pdfs[0], path="/tmp/pmc_extract/")
            shutil.move(os.path.join("/tmp/pmc_extract/", pdfs[0].name), dest_path)
        r = subprocess.run(["file","-b",dest_path], capture_output=True, text=True)
        if "PDF document" in r.stdout and os.path.getsize(dest_path) > 5000:
            subprocess.run(["rm","-rf","/tmp/pmc_extract/"])
            if os.path.exists(local_tgz): os.remove(local_tgz)
            return dest_name
    except: pass
    finally:
        subprocess.run(["rm","-rf","/tmp/pmc_extract/"])
        if os.path.exists(local_tgz):
            try: os.remove(local_tgz)
            except: pass
    return None

def make_slug(title):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:60]
    return s or "untitled"

# Phase 16 niche queries - broader terms
PHASE16_TERMS = [("self-transcendence",1.5),("transcendence",1.2),("mystical experience",1.5),("mystical",0.8),("numinous",1.5),("awe",0.8),("cosmic consciousness",1.8),("oceanic",1.0),("unity consciousness",1.2),("transcendent",0.8),("spiritual",0.3),("sacred",0.5),("near-death",0.8),("meditation",0.3)]

PHASE16_QUERIES = [
    '("near-death experience"[Title/Abstract] OR "near death"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "neuroscience"[Title/Abstract]) AND 2005:2025[dp]',
    '("spiritual experience"[Title/Abstract] OR "spiritual"[Title/Abstract] AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "prayer"[Title/Abstract] OR "psychedelic"[Title/Abstract])) AND 2005:2025[dp]',
    '("transcendence"[Title/Abstract] AND ("self"[Title/Abstract] OR "experience"[Title/Abstract])) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2005:2025[dp]',
    '("unity"[Title/Abstract] OR "oneness"[Title/Abstract] OR "nondual"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "experience"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2005:2025[dp]',
    '("meditation"[Title/Abstract] AND "self-transcendence"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
]

# Phase 17 - one more paper needed
PHASE17_TERMS = [("second-person",1.5),("intersubjectivity",1.5),("embodied empathy",1.5),("shared intentionality",1.2),("social cognition",0.6),("empathy",0.5),("mirror neuron",0.8),("social touch",1.0),("affective touch",1.0),("joint attention",1.0)]

PHASE17_QUERIES = [
    '("empathy"[Title/Abstract] AND "brain"[Title/Abstract] AND ("embodied"[Title/Abstract] OR "interoception"[Title/Abstract] OR "insula"[Title/Abstract])) AND 2005:2025[dp]',
    '("joint attention"[Title/Abstract] OR "shared attention"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
    '("social interaction"[Title/Abstract] AND "predictive coding"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
]

seen_titles = set()
for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
    try: seen_titles.add(json.load(open(w)).get("title","").lower().strip())
    except: pass

def acquire(phase_num, name, bridge_rationale, queries, terms, target=50):
    existing = sum(1 for w in glob.glob(f"{WORKS_DIR}/t2-*.json")
                  if json.load(open(w)).get("phase_mapping",{}).get("phase") == phase_num)
    need = max(0, target - existing)
    print(f"\nPhase {phase_num}: {name} — Existing: {existing}, Need: {need}")
    if need <= 0: return

    candidates = []
    for qi, query in enumerate(queries):
        if len(candidates) >= need * 2: break
        print(f"  Query {qi+1}/{len(queries)}...")
        pmids = search(query, retmax=25)
        if not pmids: continue
        print(f"    Found {len(pmids)} PMIDs")
        summaries = fetch_summary(pmids)
        abstracts = fetch_abstracts(pmids)
        for pmid in pmids:
            if len(candidates) >= need * 2: break
            summary = summaries.get(pmid, {})
            abd = abstracts.get(pmid, {})
            title = summary.get("title", abd.get("title", ""))
            if not title: continue
            tl = title.lower().strip()
            if tl in seen_titles: continue
            sv, sl = score_text(title, abd.get("abstract",""), terms)
            if sv < 1.5: continue
            seen_titles.add(tl)
            candidates.append((sv, {"pmid": pmid, "title": title, "abstract": abd.get("abstract",""),
                "year": abd.get("year", summary.get("pubdate","")[:4]),
                "journal": summary.get("source",""),
                "authors": summary.get("authors",[]),
                "doi": summary.get("doi","")}, summary, sl))
            print(f"    + [{sl}] {title[:65]}...")
    
    if not candidates: print("  No candidates"); return
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[:min(need, len(candidates))]
    print(f"  Selected {len(selected)} papers")
    
    created = 0
    for sv, article, summary, sl in selected:
        pmc_id = summary.get("pmc", "")
        pdf_name = download_pmc_pdf(pmc_id, article["title"])
        slug = make_slug(article["title"])
        work_id = f"work:t2-pubmed-{slug}"
        pub_year = article["year"]
        try: pub_year = int(pub_year)
        except: pass
        
        work_data = {
            "work_id": work_id, "schema_version": 2,
            "title": article["title"],
            "authors": [{"name": a} for a in article["authors"][:5]],
            "publication": {"year": pub_year, "type": "article", "source": "PubMed/MEDLINE", "language": "en", "journal": article.get("journal","")},
            "identifiers": {"pmid": article["pmid"], "doi": article.get("doi","")},
            "topics": [f"phase-{phase_num}", "frontier_science", "bridge_paper"],
            "tradition": ["contemporary_science"], "tier": 2,
            "assets": {"pdf_path": pdf_name, "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/", "abstract": article.get("abstract","")[:500]},
            "provenance": {"access_status": "open", "oa_status": "green" if pdf_name else "unknown", "source": "pubmed_t2_search", "retrieved_at": time.strftime("%Y-%m-%d")},
            "phase_mapping": {"phase": phase_num, "phase_name": name, "bridge_rationale": bridge_rationale},
            "evaluation": sl,
        }
        with open(f"{WORKS_DIR}/t2-pubmed-{slug}.json", "w") as f: json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        abstract = article.get("abstract","")
        if len(abstract) > 500: abstract = abstract[:500] + "..."
        essay_data = {
            "id": f"bridge-pubmed-{slug}", "type": "type-b-essay",
            "title": f"Bridge Essay: {article['title'][:80]}", "source_work": work_id,
            "phase": f"phase-{phase_num}", "phase_name": name,
            "tags": ["frontier-science", "bridge-paper", f"phase-{phase_num}"],
            "body": [
                {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{name}** with mechanistic science from PubMed/MEDLINE."},
                {"kind": "ai", "text": f"**Bridge rationale:** {bridge_rationale}"},
                {"kind": "summary", "text": f"**{article['title']}** — {article.get('journal','?')} ({pub_year}). PMID: {article['pmid']}. DOI: {article.get('doi','')}. {abstract}"},
            ],
            "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase_num} ({name}). Evaluation: {sl}",
        }
        with open(f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json", "w") as f: json.dump(essay_data, f, indent=2, ensure_ascii=False)
        created += 1
        icon = "📄" if pdf_name else "📝"
        print(f"  {icon} {article['title'][:55]} ({article.get('journal','?')} {pub_year}) — {sl}")
    
    print(f"  Added {created} papers to Phase {phase_num} (total: {existing + created})")

os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ESSAYS_DIR, exist_ok=True)
os.makedirs(LIBRARY, exist_ok=True)

acquire(16, "Visionary Cosmologies",
    "Visionary cosmologies — self-transcendence, mystical experience, numinous, awe, cosmic consciousness.",
    PHASE16_QUERIES, PHASE16_TERMS, target=50)

acquire(17, "Social Incarnation",
    "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing, second-person neuroscience.",
    PHASE17_QUERIES, PHASE17_TERMS, target=50)

print(f"\n{'='*60}")
print("FINAL COUNTS:")
for p in range(1, 18):
    count = sum(1 for w in glob.glob(f"{WORKS_DIR}/t2-*.json")
               if json.load(open(w)).get("phase_mapping",{}).get("phase") == p)
    print(f"  Phase {p:2d}: {count:3d} papers")
