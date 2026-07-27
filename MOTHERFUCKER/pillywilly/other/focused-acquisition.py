#!/usr/bin/env python3
"""Focused bridge paper acquisition for under-counted phases (3, 7, 9, 16, 17).
Uses broader queries that worked in diagnostics. Creates work JSONs + essays + PDFs."""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET, subprocess, tarfile, shutil

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
LOG = f"{BASE}/hermes/notes/t2-acquisition-log.md"
EMAIL = "hermes@research.local"
DELAY = 1.0

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/3.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None
    return None

def search(query, retmax=20):
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
            result[uid] = {
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "pubdate": doc.get("pubdate", ""),
                "doi": doi, "pmc": pmc,
                "authors": [a.get("name", "") for a in doc.get("authors", [])[:5]],
            }
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

# Phase definitions
PHASES = {
    3: {"name": "Mind as Computer Critique", "bridge_rationale": "4E cognition — embodied, embedded, enactive, extended mind; critique of computationalism.",
        "queries": [
            '("embodied cognition"[Title/Abstract] OR "grounded cognition"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2005:2025[dp]',
            '("enactive"[Title/Abstract] OR "extended mind"[Title/Abstract]) AND ("cognition"[Title/Abstract] OR "perception"[Title/Abstract]) AND 2005:2025[dp]',
            '("affordance"[Title/Abstract] AND "cognition"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
            '("ecological"[Title/Abstract] AND "perception"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "action"[Title/Abstract])) AND 2010:2025[dp]',
        ],
        "terms": [("embodied cognition",1.5),("grounded cognition",1.2),("enactive",1.5),("extended mind",1.5),("situated cognition",1.2),("sensorimotor",0.8),("4e cognition",1.5),("computationalism",1.0),("radical embodiment",1.5),("ecological",0.5),("affordance",0.8),("dynamical",0.5),("autopoiesis",1.2)]},
    7: {"name": "Emptiness", "bridge_rationale": "Emptiness — dissolution of self, DMN decoupling, ego dissolution, nondual awareness.",
        "queries": [
            '("nondual"[Title/Abstract] OR "non-dual"[Title/Abstract] OR "nondual awareness"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "brain"[Title/Abstract] OR "neuroscience"[Title/Abstract]) AND 2000:2025[dp]',
            '("ego dissolution"[Title/Abstract] OR "self-loss"[Title/Abstract] OR "self-boundary"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
            '("default mode"[Title/Abstract] AND "self"[Title/Abstract] AND ("dissolution"[Title/Abstract] OR "transcendence"[Title/Abstract] OR "meditation"[Title/Abstract])) AND 2010:2025[dp]',
            '("depersonalization"[Title/Abstract] OR "derealization"[Title/Abstract]) AND ("self-referential"[Title/Abstract] OR "self-processing"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": [("ego dissolution",1.5),("self-loss",1.5),("self-transcendence",1.2),("default mode",0.8),("nondual",1.5),("non-dual",1.5),("depersonalization",0.8),("derealization",0.6),("self-boundary",1.0),("self-referential",0.5),("meditation",0.5),("psychedelic",0.5),("mindfulness",0.3),("sense of self",0.6)]},
    9: {"name": "Language/Mantra", "bridge_rationale": "Language as mantra — mantra meditation, inner speech, focused attention, verbal repetition.",
        "queries": [
            '("mantra"[Title/Abstract] OR "mantra meditation"[Title/Abstract]) AND ("EEG"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2000:2025[dp]',
            '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract] OR "self-talk"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
            '("focused attention"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("neural"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract])) AND 2005:2025[dp]',
            '("transcendental meditation"[Title/Abstract] OR "TM meditation"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2000:2025[dp]',
            '("chanting"[Title/Abstract] OR "verbal repetition"[Title/Abstract] OR "silent repetition"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": [("mantra",1.5),("mantra meditation",1.8),("inner speech",1.5),("inner voice",1.2),("self-talk",1.0),("private speech",0.8),("focused attention",0.8),("verbal repetition",1.0),("prayer",0.8),("transcendental meditation",1.2),("chanting",1.2),("repetitive",0.3)]},
    16: {"name": "Visionary Cosmologies", "bridge_rationale": "Visionary cosmologies — self-transcendence, mystical experience, numinous, awe, cosmic consciousness.",
        "queries": [
            '("self-transcendence"[Title/Abstract] OR "transcendence"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "neuroimaging"[Title/Abstract]) AND 2005:2025[dp]',
            '("awe"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "experience"[Title/Abstract])) AND 2010:2025[dp]',
            '("mystical experience"[Title/Abstract] OR "mystical"[Title/Abstract] OR "numinous"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "meditation"[Title/Abstract] OR "psychedelic"[Title/Abstract]) AND 2000:2025[dp]',
            '("spiritual experience"[Title/Abstract] OR "peak experience"[Title/Abstract] OR "oceanic"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": [("self-transcendence",1.5),("transcendence",1.2),("mystical experience",1.5),("mystical",0.8),("numinous",1.5),("awe",0.8),("cosmic consciousness",1.8),("oceanic",1.0),("unity consciousness",1.2),("transcendent",0.8),("spiritual",0.3),("sacred",0.5)]},
    17: {"name": "Social Incarnation", "bridge_rationale": "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing, second-person neuroscience.",
        "queries": [
            '("second-person"[Title/Abstract] OR "intersubjectivity"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
            '("embodied empathy"[Title/Abstract] OR "social touch"[Title/Abstract] OR "affective touch"[Title/Abstract]) AND ("insula"[Title/Abstract] OR "brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("shared intentionality"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
            '("social cognition"[Title/Abstract] AND "predictive processing"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
            '("mirror neuron"[Title/Abstract] AND "empathy"[Title/Abstract] AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract] OR "insula"[Title/Abstract])) AND 2005:2025[dp]',
        ],
        "terms": [("second-person",1.5),("intersubjectivity",1.5),("embodied empathy",1.5),("shared intentionality",1.2),("social cognition",0.6),("empathy",0.5),("mirror neuron",0.8),("interoception",0.5),("social brain",0.4),("social touch",1.0),("affective touch",1.0)]},
}
CROSS = [("neural",0.3),("brain",0.2),("fMRI",0.4),("neuroimaging",0.5),("cortex",0.3),("EEG",0.4),("mechanism",0.5)]
NOISE = ["clinical trial", "pharmacological", "treatment outcome", "case report", "rat ", " mice ", "murine", "animal model", "surgery"]

def score_paper(title, abstract, phase_num):
    text = f"{title} {abstract}".lower()
    for n in NOISE:
        if n in text: return 0, f"Noise: '{n}'"
    score = sum(w for t, w in PHASES[phase_num]["terms"] if t in text)
    score += sum(w for t, w in CROSS if t in text)
    if score >= 3.5: return score, f"Excellent (score={score:.1f})"
    elif score >= 2.5: return score, f"Good (score={score:.1f})"
    elif score >= 2.0: return score, f"Good (score={score:.1f})"
    elif score >= 1.5: return score, f"Marginal (score={score:.1f})"
    else: return score, f"Low signal (score={score:.1f})"

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
    local_tgz = f"/tmp/pmc_{pmc_clean}.tar.gz"
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
            tar.extract(pdfs[0], path="/tmp/pmc_extract/")
            shutil.move(os.path.join("/tmp/pmc_extract/", pdfs[0].name), dest_path)
        result = subprocess.run(["file", "-b", dest_path], capture_output=True, text=True)
        if "PDF document" in result.stdout and os.path.getsize(dest_path) > 5000:
            subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
            if os.path.exists(local_tgz): os.remove(local_tgz)
            return dest_name
    except: pass
    finally:
        subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
        if os.path.exists(local_tgz):
            try: os.remove(local_tgz)
            except: pass
    return None

def make_slug(title):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:60]
    return s or "untitled"

def acquire_phase(phase_num, target=50):
    info = PHASES[phase_num]
    print(f"\n{'='*60}")
    print(f"Phase {phase_num}: {info['name']}")
    print(f"{'='*60}")
    
    existing_count = sum(1 for w in glob.glob(f"{WORKS_DIR}/t2-*.json")
                        if json.load(open(w)).get("phase_mapping",{}).get("phase") == phase_num)
    need = max(0, target - existing_count)
    print(f"Existing: {existing_count}, Need: {need}")
    if need <= 0: print("Already at target"); return 0
    
    seen_titles = set()
    for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
        try: seen_titles.add(json.load(open(w)).get("title", "").lower().strip())
        except: pass
    
    candidates = []
    for qi, query in enumerate(info["queries"]):
        if len(candidates) >= need * 2: break
        print(f"\n  Query {qi+1}/{len(info['queries'])}...")
        pmids = search(query, retmax=20)
        if not pmids: print("    No results"); continue
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
            
            score_val, score_label = score_paper(title, abd.get("abstract", ""), phase_num)
            if score_val < 1.5: continue  # Accept marginal+ for these hard phases
            
            seen_titles.add(tl)
            candidates.append((score_val, {
                "pmid": pmid, "title": title, "abstract": abd.get("abstract", ""),
                "year": abd.get("year", summary.get("pubdate", "")[:4]),
                "journal": summary.get("source", ""),
                "authors": summary.get("authors", []),
                "doi": summary.get("doi", ""),
            }, summary, score_label))
            print(f"    + [{score_label}] {title[:70]}...")
    
    if not candidates: print("  No candidates found"); return 0
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[:min(need, len(candidates))]
    print(f"\n  Selected {len(selected)} papers (from {len(candidates)} candidates)")
    
    details = []
    created = 0
    for score_val, article, summary, score_label in selected:
        pmid = article["pmid"]; title = article["title"]
        pmc_id = summary.get("pmc", "")
        pdf_name = download_pmc_pdf(pmc_id, title)
        if not pdf_name and article.get("doi"):
            doi = article["doi"]
            # Try publisher direct patterns
            if "frontiersin" in article.get("journal", "").lower():
                try:
                    url = f"https://journal.frontiersin.org/article/{doi}/pdf"
                    subprocess.run(["curl", "-sL", "-o", f"{LIBRARY}/t2-{pmid}.pdf", url], timeout=30)
                    r = subprocess.run(["file", "-b", f"{LIBRARY}/t2-{pmid}.pdf"], capture_output=True, text=True)
                    if "PDF document" in r.stdout and os.path.getsize(f"{LIBRARY}/t2-{pmid}.pdf") > 5000:
                        pdf_name = f"t2-{pmid}.pdf"
                except: pass
            elif "springer" in article.get("journal", "").lower() or "biomed" in article.get("journal", "").lower():
                try:
                    url = f"https://link.springer.com/content/pdf/{doi}.pdf"
                    subprocess.run(["curl", "-sL", "-o", f"{LIBRARY}/t2-{pmid}.pdf", url], timeout=30)
                    r = subprocess.run(["file", "-b", f"{LIBRARY}/t2-{pmid}.pdf"], capture_output=True, text=True)
                    if "PDF document" in r.stdout and os.path.getsize(f"{LIBRARY}/t2-{pmid}.pdf") > 5000:
                        pdf_name = f"t2-{pmid}.pdf"
                except: pass
        
        # Create work JSON
        slug = make_slug(title)
        work_id = f"work:t2-pubmed-{slug}"
        pub_year = article["year"]
        try: pub_year = int(pub_year)
        except: pass
        
        work_data = {
            "work_id": work_id, "schema_version": 2,
            "title": title,
            "authors": [{"name": a} for a in article["authors"][:5]] if isinstance(article["authors"], list) else [],
            "publication": {"year": pub_year, "type": "article", "source": "PubMed/MEDLINE", "language": "en", "journal": article.get("journal", "")},
            "identifiers": {"pmid": pmid, "doi": article.get("doi", "")},
            "topics": [f"phase-{phase_num}-{slug[:20]}", "frontier_science", "bridge_paper"],
            "tradition": ["contemporary_science"], "tier": 2,
            "assets": {"pdf_path": pdf_name, "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", "abstract": article.get("abstract", "")[:500]},
            "provenance": {"access_status": "open", "oa_status": "green" if pdf_name else "unknown", "source": "pubmed_t2_search", "retrieved_at": time.strftime("%Y-%m-%d")},
            "phase_mapping": {"phase": phase_num, "phase_name": info["name"], "bridge_rationale": info["bridge_rationale"]},
            "evaluation": score_label,
        }
        work_file = f"{WORKS_DIR}/t2-pubmed-{slug}.json"
        with open(work_file, "w") as f: json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        # Create essay JSON
        abstract = article.get("abstract", "")
        if len(abstract) > 500: abstract = abstract[:500] + "..."
        body = [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{info['name']}** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** {info['bridge_rationale']}"},
            {"kind": "summary", "text": f"**{title}** — {article.get('journal','?')} ({pub_year}). PMID: {pmid}. DOI: {article.get('doi','')}. {abstract}"},
        ]
        essay_data = {
            "id": f"bridge-pubmed-{slug}", "type": "type-b-essay",
            "title": f"Bridge Essay: {title[:80]}", "source_work": work_id,
            "phase": f"phase-{phase_num}", "phase_name": info["name"],
            "tags": ["frontier-science", "bridge-paper", f"phase-{phase_num}"],
            "body": body,
            "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase_num} ({info['name']}). Evaluation: {score_label}",
        }
        essay_file = f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json"
        with open(essay_file, "w") as f: json.dump(essay_data, f, indent=2, ensure_ascii=False)
        
        created += 1
        icon = "📄" if pdf_name else "📝"
        detail = f"  {icon} {title[:60]} ({article.get('journal','?')} {pub_year}) — {score_label}"
        details.append(detail)
        print(detail)
    
    # Log
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## Session: {ts}\n**Phase:** {info['name']} (Phase {phase_num})\n**New papers:** {created}\n\n"
    for d in details: entry += f"- {d}\n"
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f: f.write(entry)
    print(f"\n  Phase {phase_num} complete: {created} new papers (total: {existing_count + created})")
    return created

if __name__ == "__main__":
    os.makedirs(WORKS_DIR, exist_ok=True)
    os.makedirs(ESSAYS_DIR, exist_ok=True)
    os.makedirs(LIBRARY, exist_ok=True)
    
    total = 0
    for phase in [3, 7, 9, 16, 17]:
        added = acquire_phase(phase, target=50)
        total += added
    print(f"\n{'='*60}")
    print(f"ACQUISITION COMPLETE: {total} new papers total")
    
    # Final summary
    print(f"\nUpdated phase counts:")
    for p in range(1, 18):
        count = 0
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try:
                d = json.load(open(w))
                if d.get("phase_mapping",{}).get("phase") == p:
                    count += 1
            except: pass
        print(f"  Phase {p:2d}: {count:3d} papers")
