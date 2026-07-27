#!/usr/bin/env python3
"""
Extended search for phases that need more high-quality papers.
Uses niche sub-topic queries when standard queries exhaust candidates.
"""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, subprocess, tarfile

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.2

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

def search(query, retmax=20):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch(pmids):
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
            if pmid_el is None: continue
            pmid = pmid_el.text.strip()
            te = article.find(".//ArticleTitle")
            title = "".join(te.itertext()).strip() if te is not None else ""
            abs_parts = []
            for ae in article.findall(".//AbstractText"):
                abs_parts.append("".join(ae.itertext()).strip())
            abstract = " ".join(abs_parts)
            ye = article.find(".//PubDate/Year")
            if ye is None: ye = article.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            je = article.find(".//Journal/Title")
            journal = je.text.strip() if je is not None else ""
            doi_el = article.find('.//ArticleId[@IdType="doi"]')
            doi = doi_el.text.strip() if doi_el is not None else ""
            articles[pmid] = {"title": title, "abstract": abstract, "year": year, "journal": journal, "doi": doi}
    except: pass
    return articles

def esummary(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}")
    if not data: return {}
    try:
        result = {}
        parsed = json.loads(data)
        for uid, doc in parsed.get("result", {}).items():
            if uid == "uids": continue
            doi = ""; pmc = ""
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "doi": doi = aid.get("value", "")
                if aid.get("idtype") == "pmc": pmc = aid.get("value", "")
            result[uid] = {"doi": doi, "pmc": pmc, "source": doc.get("source", ""), "pubdate": doc.get("pubdate", "")}
        return result
    except: return {}

def download_pdf(pmc_id, title):
    if not pmc_id: return None
    pmc_clean = pmc_id.replace("PMC", "")
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_clean}"
    time.sleep(DELAY)
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
        subprocess.run(["curl", "-sL", "-o", local_tgz, https_url], check=True, timeout=120)
    except: return None
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000: return None
    try:
        dest_name = f"t2-pubmed-pmc{pmc_clean}_{re.sub(r'[^a-zA-Z0-9]+', '_', title)[:50].strip('_')}.pdf"
        dest_path = os.path.join(LIBRARY, dest_name)
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = sorted([m for m in tar.getmembers() if m.name.endswith(".pdf") and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name], key=lambda m: m.size, reverse=True)
            if not pdfs: pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs: return None
            tar.extract(pdfs[0], path="/tmp/pmc_extract/")
            src = os.path.join("/tmp/pmc_extract/", pdfs[0].name)
            if os.path.exists(src):
                import shutil
                shutil.move(src, dest_path)
        os.remove(local_tgz)
        subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
            return dest_name
    except:
        if os.path.exists(local_tgz): os.remove(local_tgz)
    return None

def score_paper(phase, title, abstract):
    """Score a paper for bridge relevance to a specific phase."""
    text = f"{title} {abstract}".lower()
    
    noise = ["clinical trial", "pharmacological", "treatment outcome", "case report",
             "rat ", " mice ", "murine", "animal model", "surgery",
             "randomized controlled", "phase 2", "phase 3"]
    for n in noise:
        if n in text: return 0, f"Noise: '{n}'"
    
    # Phase-specific terms
    terms = {
        17: [("second-person", 1.5), ("intersubjectivity", 1.5), ("embodied empathy", 1.5),
             ("shared intentionality", 1.2), ("predictive processing", 0.5),
             ("social cognition", 0.6), ("empathy", 0.5), ("mirror neuron", 0.8),
             ("interoception", 0.5), ("social brain", 0.4), ("social touch", 0.8),
             ("interpersonal", 0.5), ("joint attention", 1.0), ("mentalizing", 0.5)],
        7: [("ego dissolution", 1.5), ("self-loss", 1.5), ("self-transcendence", 1.2),
            ("default mode", 0.8), ("nondual", 1.5), ("non-dual", 1.5),
            ("depersonalization", 0.8), ("self-boundary", 1.0), ("self-referential", 0.5),
            ("meditation", 0.5), ("psychedelic", 0.5), ("mindfulness", 0.4),
            ("self-awareness", 0.5), ("ego", 0.3)],
        3: [("embodied cognition", 1.5), ("grounded cognition", 1.2), ("enactive", 1.5),
            ("extended mind", 1.5), ("situated cognition", 1.2), ("sensorimotor", 0.8),
            ("4e cognition", 1.5), ("predictive processing", 0.6), ("active inference", 0.6),
            ("radical embodied", 1.5), ("ecological psychology", 1.0)],
        9: [("mantra", 1.5), ("mantra meditation", 1.8), ("inner speech", 1.5),
            ("inner voice", 1.2), ("self-talk", 1.0), ("private speech", 0.8),
            ("focused attention", 0.8), ("verbal repetition", 1.0), ("prayer", 0.8),
            ("transcendental meditation", 1.2), ("chanting", 1.5), ("om mantra", 1.5)],
        16: [("self-transcendence", 1.5), ("transcendence", 1.2), ("mystical experience", 1.5),
             ("mystical", 0.8), ("numinous", 1.5), ("awe", 0.8),
             ("cosmic consciousness", 1.8), ("oceanic", 1.0), ("unity consciousness", 1.2),
             ("transcendent", 0.8), ("near-death", 0.8), ("sacred", 0.6)],
    }
    
    score = 0
    for term, weight in terms.get(phase, []):
        if term in text: score += weight
    
    cross = [("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("EEG", 0.4), ("mechanism", 0.5)]
    for term, weight in cross:
        if term in text: score += weight
    
    if score >= 3.5: return 3, f"Excellent (score={score:.1f})"
    elif score >= 2.5: return 2, f"Good (score={score:.1f})"
    elif score >= 1.5: return 1, f"Marginal (score={score:.1f})"
    return 0, f"Low (score={score:.1f})"

def create_work(article, phase_key, info):
    """Create work JSON + essay JSON."""
    title = article["title"]
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:70].strip('-')
    wid = f"t2-pubmed-{slug}"
    
    # Check if exists
    wpath = os.path.join(WORKS_DIR, f"{wid}.json")
    if os.path.exists(wpath):
        return False
    
    work = {
        "work_id": f"work:{wid}",
        "schema_version": 2,
        "title": title,
        "publication": {"year": int(article.get("year","2026")) if article.get("year","0").isdigit() else 2026,
                        "type": "article", "source": "PubMed/MEDLINE", "language": "en",
                        "journal": article.get("journal","")},
        "identifiers": {"pmid": article.get("pmid",""), "doi": article.get("doi","")},
        "topics": [f"phase-{info['phase']}-{info['name'].lower().replace(' ', '-')}", "frontier_science", "bridge_paper"],
        "tradition": ["contemporary_science"], "tier": 2,
        "assets": {"pdf_path": article.get("pdf_path",""), "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid','')}/",
                   "abstract": article.get("abstract","")[:500]},
        "provenance": {"access_status": "open", "oa_status": "green", "source": "pubmed_t2_search", "retrieved_at": "2026-07-12"},
        "phase_mapping": {"phase": info["phase"], "phase_name": info["name"], "bridge_rationale": info["bridge_rationale"]},
        "evaluation": article.get("evaluation","")
    }
    
    with open(wpath, "w") as f:
        json.dump(work, f, indent=2)
    
    essay = {
        "id": f"bridge-pubmed-{slug}",
        "type": "type-b-essay",
        "title": f"Bridge Essay: {title[:80]}",
        "source_work": f"work:{wid}",
        "phase": f"phase-{info['phase']}",
        "phase_name": info["name"],
        "tags": ["frontier-science", "bridge-paper", f"phase-{info['phase']}"],
        "body": [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{info['name']}** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** {info['bridge_rationale']}"},
            {"kind": "ai", "text": f"**Phase context:** {info['concept']}"},
            {"kind": "summary", "text": f"**{title}** — {article.get('journal','')} ({article.get('year','')}). DOI: {article.get('doi','')}. PMID: {article.get('pmid','')}. {article.get('abstract','')[:500]}"},
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-12. Phase {info['phase']} ({info['name']}). Evaluation: {article.get('evaluation','')}"
    }
    
    with open(os.path.join(ESSAYS_DIR, f"bridge-pubmed-{slug}.json"), "w") as f:
        json.dump(essay, f, indent=2)
    
    return True

PHASES = {
    "phase-17-social": {"phase": 17, "name": "Social Incarnation", "concept": "Intersubjectivity — embodied empathy, social predictive processing, second-person neuroscience.", "bridge_rationale": "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing."},
    "phase-7-emptiness": {"phase": 7, "name": "Emptiness", "concept": "Self-dissolution — ego dissolution, DMN decoupling, non-self in neuroscience.", "bridge_rationale": "Emptiness — dissolution of self, DMN decoupling, ego dissolution."},
    "phase-3-4e-cognition": {"phase": 3, "name": "Mind as Computer Critique", "concept": "Mind not a computer — embodied, embedded, enactive, extended cognition.", "bridge_rationale": "4E cognition — embodied, embedded, enactive, extended mind."},
    "phase-9-language": {"phase": 9, "name": "Language/Mantra", "concept": "Mantra meditation, inner speech, focused attention, language as mantra.", "bridge_rationale": "Language as mantra — mantra meditation, inner speech, focused attention."},
    "phase-16-transcendence": {"phase": 16, "name": "Visionary Cosmologies", "concept": "Self-transcendence, mystical experience, numinous, cosmic consciousness.", "bridge_rationale": "Visionary cosmologies — self-transcendence, mystical experience, awe."},
}

# Extended niche queries
EXTENDED = {
    "phase-17-social": [
        '("social touch" OR "affective touch") AND ("insula" OR "somatosensory") AND ("empathy" OR "social cognition") AND 2018:2025[dp]',
        '("predictive processing" OR "predictive coding") AND ("social" OR "intersubjectivity" OR "empathy") AND ("brain" OR "neural") AND 2018:2025[dp]',
        '("shared experience" OR "shared emotions" OR "interpersonal sharing") AND ("neural" OR "brain" OR "fMRI") AND 2018:2025[dp]',
    ],
    "phase-7-emptiness": [
        '("self-awareness" OR "self-consciousness") AND ("meditation" OR "mindfulness") AND ("default mode" OR "prefrontal") AND 2018:2025[dp]',
        '("ego" OR "self-boundary" OR "self-other") AND ("dissolution" OR "transcendence" OR "loss") AND ("brain" OR "neural") AND 2018:2025[dp]',
        '("mindfulness" OR "meditation") AND ("self-referential" OR "narrative self" OR "minimal self") AND ("neural" OR "fMRI") AND 2015:2025[dp]',
    ],
    "phase-3-4e-cognition": [
        '("radical embodied" OR "ecological" OR "affordance") AND ("cognition" OR "perception") AND ("brain" OR "neural" OR "action") AND 2018:2025[dp]',
        '("dynamical systems" OR "complex systems") AND ("cognition" OR "consciousness" OR "brain") AND ("embodied" OR "enactive") AND 2018:2025[dp]',
    ],
    "phase-9-language": [
        '("focused attention" OR "concentrative" OR "absorption") AND ("meditation" OR "prayer") AND ("EEG" OR "fMRI" OR "neural") AND 2015:2025[dp]',
        '("self-talk" OR "private speech" OR "verbal rehearsal") AND ("brain" OR "cortex" OR "frontal") AND ("inner" OR "silent") AND 2015:2025[dp]',
    ],
    "phase-16-transcendence": [
        '("awe" OR "wonder" OR "sublime") AND ("brain" OR "neural" OR "fMRI" OR "experience") AND 2018:2025[dp]',
        '("psychedelic" OR "psilocybin") AND ("mystical" OR "transcendent" OR "awe") AND ("experience" OR "subjective") AND 2018:2025[dp]',
    ],
}

def main():
    for pk in ["phase-17-social", "phase-7-emptiness", "phase-3-4e-cognition", "phase-9-language", "phase-16-transcendence"]:
        info = PHASES[pk]
        phase = info["phase"]
        name = info["name"]
        
        # Count existing
        existing = set()
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try:
                d = json.load(open(w))
                pm = d.get("phase_mapping", {})
                if pm and pm.get("phase") == phase:
                    existing.add(w)
            except: pass
        
        need = 50 - len(existing)
        print(f"\n{'='*60}")
        print(f"Phase {phase}: {name}")
        print(f"Existing: {len(existing)}, Need: {need}")
        
        if need <= 0:
            print("  Already at target")
            continue
        
        seen_titles = set()
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try: seen_titles.add(json.load(open(w)).get("title","").lower().strip())
            except: pass
        
        candidates = []
        queries = EXTENDED.get(pk, [])
        
        for qi, query in enumerate(queries):
            print(f"\n  Extended Query {qi+1}/{len(queries)}...")
            pmids = search(query, retmax=20)
            if not pmids:
                print("    No results")
                continue
            print(f"    Found {len(pmids)} PMIDs")
            
            summaries = esummary(pmids)
            abstracts = fetch(pmids)
            
            for pmid in pmids:
                if len(candidates) >= need * 2: break
                
                ab = abstracts.get(pmid, {})
                title = ab.get("title", "")
                if not title: continue
                
                tl = title.lower().strip()
                if tl in seen_titles: continue
                
                abstract = ab.get("abstract", "")
                year = ab.get("year", summaries.get(pmid, {}).get("pubdate", "")[:4])
                journal = ab.get("journal", summaries.get(pmid, {}).get("source", ""))
                
                sv, sl = score_paper(phase, title, abstract)
                if sv < 2: continue  # Only Good+
                
                seen_titles.add(tl)
                
                doi = summaries.get(pmid, {}).get("doi", "")
                pmc = summaries.get(pmid, {}).get("pmc", "")
                
                candidates.append((sv, {
                    "pmid": pmid, "title": title, "abstract": abstract,
                    "year": year, "journal": journal, "doi": doi, "pmc": pmc,
                    "evaluation": sl, "pdf_path": None
                }))
                print(f"    + [{sl}] {title[:70]}...")
        
        if not candidates:
            print("  No candidates found")
            continue
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        selected = candidates[:min(need, len(candidates))]
        
        print(f"\n  Selected {len(selected)} papers")
        created = 0
        for sv, article in selected:
            # Download PDF
            pdf = download_pdf(article.get("pmc"), article["title"])
            article["pdf_path"] = pdf
            
            success = create_work(article, pk, info)
            if success:
                created += 1
                pdf_text = " [PDF]" if pdf else ""
                print(f"  ✓ {article['title'][:60]}... ({article['journal']} {article['year']}) — {article['evaluation']}{pdf_text}")
        
        print(f"  Phase {phase} complete: {created} new papers (total: {len(existing) + created})")

if __name__ == "__main__":
    main()
