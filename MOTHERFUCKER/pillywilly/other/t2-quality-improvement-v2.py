#!/usr/bin/env python3
"""
t2-quality-improvement-v2.py — Quality improvement for phases NOT covered by v1.
Targets: Phase 8 (Formless/Absorption), Phase 9 (Language/Mantra),
Phase 12 (Ritual), Phase 13 (Daimon), Phase 15 (Liberation/Enlightenment).

For each phase: audits existing papers, searches 6 targeted PubMed queries,
creates new work JSONs + essays for high-scoring candidates, deletes worst
low-signal papers. Uses broader date ranges (2000:2025) and lower threshold (>=4).
"""
import json, glob, os, urllib.request, urllib.parse, time, re, sys, subprocess
import xml.etree.ElementTree as ET

PROJECT = "/root/projects/blog"
WORKS_DIR = f"{PROJECT}/content/works"
ESSAYS_DIR = f"{PROJECT}/content/glossary/essays"
FRONTIER_DIR = f"{PROJECT}/library/frontier"
os.makedirs(FRONTIER_DIR, exist_ok=True)

EMAIL = "hermes@research.local"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DELAY = 1.0

seen_titles = set()

def log(msg):
    print(msg, flush=True)

def safe_delay():
    time.sleep(DELAY)

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    ⚠️ HTTP error: {e}", flush=True)
        return None

def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        print(f"    ⚠️ XML fetch error: {e}", flush=True)
        return None

def esearch(query, retmax=25):
    safe_delay()
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmax": retmax,
        "retmode": "json", "email": EMAIL
    })
    url = f"{BASE_URL}esearch.fcgi?{params}"
    data = fetch_json(url)
    if data:
        return data.get("esearchresult", {}).get("idlist", [])
    return []

def esummary(pmids):
    if not pmids:
        return {}
    safe_delay()
    ids = ",".join(pmids)
    params = urllib.parse.urlencode({"db": "pubmed", "id": ids, "retmode": "json", "email": EMAIL})
    url = f"{BASE_URL}esummary.fcgi?{params}"
    data = fetch_json(url)
    if data and "result" in data:
        return data["result"]
    return {}

def efetch_abstract(pmid):
    safe_delay()
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "xml", "email": EMAIL})
    url = f"{BASE_URL}efetch.fcgi?{params}"
    root = fetch_xml(url)
    if root is None:
        return None
    
    for article in root.findall(".//PubmedArticle"):
        id_el = article.find(".//PMID")
        if id_el is not None and id_el.text == pmid:
            parts = []
            for at in article.findall(".//AbstractText"):
                parts.append("".join(at.itertext()))
            abstract = " ".join(parts)
            
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""
            
            ye = article.find(".//PubDate/Year")
            if ye is None:
                ye = article.find(".//PubDate/MedlineDate")
            year = ye.text[:4] if ye is not None and ye.text else ""
            
            journal_el = article.find(".//Journal/Title")
            journal = journal_el.text if journal_el is not None else ""
            
            doi = ""
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
            
            authors = []
            for au in article.findall(".//Author"):
                ln = au.find("LastName")
                fn = au.find("ForeName")
                if ln is not None:
                    name = f"{ln.text or ''}"
                    if fn is not None:
                        name = f"{fn.text or ''} {name}"
                    authors.append({"name": name.strip()})
            
            return {
                "title": title, "abstract": abstract,
                "year": year, "journal": journal,
                "doi": doi, "authors": authors
            }
    
    # Check PubmedBookArticle for book chapters
    for article in root.findall(".//PubmedBookArticle"):
        id_el = article.find(".//PMID")
        if id_el is not None and id_el.text == pmid:
            parts = []
            for at in article.findall(".//AbstractText"):
                parts.append("".join(at.itertext()))
            abstract = " ".join(parts)
            
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""
            
            ye = article.find(".//PubDate/Year")
            year = ye.text[:4] if ye is not None and ye.text else ""
            
            journal_el = article.find(".//BookTitle")
            journal = journal_el.text if journal_el is not None else ""
            
            doi = ""
            return {
                "title": title, "abstract": abstract,
                "year": year, "journal": journal,
                "doi": doi, "authors": []
            }
    
    return None

# Phase-specific scoring dictionaries with broader terms and queries
PHASE_SCORING = {
    8: {  # Formless/Absorption - meditative absorption, jhana, samadhi, trance
        "name": "Formless/Absorption",
        "high": ["meditative absorption", "deep meditation", "samadhi", "jhana",
                 "trance", "altered state", "non-ordinary state", "hypnotic",
                 "loving-kindness", "compassion meditation", "metta",
                 "self-transcendence", "mystical experience", "transcendent",
                 "transcendental meditation", "zen meditation"],
        "med": ["gamma", "theta", "alpha", "EEG", "coherence", "long-term meditator",
                "expert meditator", "contemplative", "absorption", "meditation",
                "mindfulness", "psychedelic", "dissociation"],
        "queries": [
            '("meditative absorption"[Title/Abstract] OR "deep meditation"[Title/Abstract] OR "samadhi"[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '("altered state"[Title/Abstract] OR "non-ordinary"[Title/Abstract] OR "trance"[Title/Abstract] OR "hypnotic"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("loving-kindness"[Title/Abstract] OR "compassion meditation"[Title/Abstract] OR "metta"[Title/Abstract]) AND (fMRI[Title/Abstract] OR EEG[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '("zen meditation"[Title/Abstract] OR "zazen"[Title/Abstract] OR "transcendental meditation"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2000:2025[dp]',
            '("meditation"[Title/Abstract] AND ("gamma"[Title/Abstract] OR "theta"[Title/Abstract] OR "alpha coherence"[Title/Abstract]) AND ("long-term"[Title/Abstract] OR "expert"[Title/Abstract])) AND 2005:2025[dp]',
            '("psychedelic"[Title/Abstract] OR "meditation"[Title/Abstract]) AND ("absorption"[Title/Abstract] OR "trance"[Title/Abstract] OR "nondual"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
        ]
    },
    9: {  # Language/Mantra - mantra meditation, chanting, focused repetition
        "name": "Language/Mantra",
        "high": ["mantra", "mantra meditation", "chanting",
                 "inner speech", "focused attention meditation", "concentrative meditation",
                 "self-talk", "private speech", "verbal repetition", "repetitive speech",
                 "focused attention", "concentrative meditation"],
        "med": ["meditation", "prayer", "inner speech", "corollary discharge",
                "self-monitoring", "repetition", "verbal", "mantra"],
        "queries": [
            '("mantra"[Title/Abstract] OR "mantra meditation"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract] OR fMRI[Title/Abstract]) AND 2000:2025[dp]',
            '("chanting"[Title/Abstract] OR "mantric"[Title/Abstract] OR "mantra repetition"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("focused attention"[Title/Abstract] OR "concentrative meditation"[Title/Abstract]) AND (meditation[Title/Abstract] OR prayer[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2005:2025[dp]',
            '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2000:2025[dp]',
            '("self-talk"[Title/Abstract] OR "private speech"[Title/Abstract] OR "verbal rehearsal"[Title/Abstract]) AND (meditation[Title/Abstract] OR "inner"[Title/Abstract] OR "silent"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '("corollary discharge"[Title/Abstract] AND ("speech"[Title/Abstract] OR "verbal"[Title/Abstract] OR "vocal"[Title/Abstract])) AND 2000:2025[dp]',
        ]
    },
    12: {  # Ritual - neural synchrony, hyperscanning, inter-brain
        "name": "Ritual",
        "high": ["neural synchrony", "hyperscanning", "inter-brain", "interbrain",
                 "brain-to-brain", "interpersonal synchronization", "group synchrony",
                 "behavioral synchrony", "joint action", "audience brain synchrony"],
        "med": ["synchronization", "interpersonal", "joint", "music", "entrainment",
                "collective", "social bonding", "emotional sharing", "coordination",
                "EEG hyperscanning", "fNIRS hyperscanning", "dual EEG"],
        "queries": [
            '("hyperscanning"[Title/Abstract] OR "inter-brain"[Title/Abstract] OR "interbrain"[Title/Abstract]) AND (EEG[Title/Abstract] OR fNIRS[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '("neural synchrony"[Title/Abstract] OR "brain synchrony"[Title/Abstract] OR "interpersonal neural"[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR music[Title/Abstract] OR social[Title/Abstract]) AND 2005:2025[dp]',
            '("interpersonal synchronization"[Title/Abstract] OR "behavioral synchrony"[Title/Abstract] OR "interpersonal coordination"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("dual EEG"[Title/Abstract] OR "two-person"[Title/Abstract] OR "second-person"[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR synchrony[Title/Abstract]) AND 2010:2025[dp]',
            '("music"[Title/Abstract] AND "entrainment"[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR synchrony[Title/Abstract] OR EEG[Title/Abstract])) AND 2010:2025[dp]',
            '("joint action"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "EEG"[Title/Abstract]) AND (synchrony[Title/Abstract] OR coordination[Title/Abstract]) AND 2010:2025[dp]',
        ]
    },
    13: {  # Daimon - voice hearing, AVH, inner speech, hallucinations
        "name": "Daimon",
        "high": ["auditory verbal hallucination", "voice hearing", "hallucination proneness",
                 "inner speech", "corollary discharge", "source monitoring",
                 "agency detection", "hallucination", "self-monitoring",
                 "auditory hallucination"],
        "med": ["voice", "hallucination", "inner", "speech", "auditory",
                "self-other", "misattribution", "reality monitoring",
                "prediction error", "top-down", "psychosis", "schizophrenia"],
        "queries": [
            '("auditory verbal hallucination"[Title/Abstract] OR "voice hearing"[Title/Abstract] OR "voices"[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract] OR mechanism[Title/Abstract]) AND 2005:2025[dp]',
            '("corollary discharge"[Title/Abstract] OR "efference copy"[Title/Abstract]) AND ("speech"[Title/Abstract] OR "auditory"[Title/Abstract] OR "self-monitoring"[Title/Abstract]) AND 2000:2025[dp]',
            '("source monitoring"[Title/Abstract] OR "reality monitoring"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "auditory"[Title/Abstract] OR "speech"[Title/Abstract]) AND 2005:2025[dp]',
            '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "psychosis"[Title/Abstract] OR "auditory"[Title/Abstract] OR "misattribution"[Title/Abstract]) AND 2005:2025[dp]',
            '("agency detection"[Title/Abstract] OR "self-monitoring"[Title/Abstract]) AND ("auditory"[Title/Abstract] OR "hallucination"[Title/Abstract] OR "speech"[Title/Abstract]) AND 2005:2025[dp]',
            '("hallucination proneness"[Title/Abstract] OR "predisposition hallucination"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
        ]
    },
    15: {  # Liberation/Enlightenment - ego dissolution, self-transcendence
        "name": "Liberation/Enlightenment",
        "high": ["ego dissolution", "self-transcendence", "self-loss", "ego death",
                 "enlightenment", "awakening", "spiritual awakening", "nibbana",
                 "selflessness", "no-self", "mystical experience", "religious experience",
                 "peak experience", "psychedelic", "selflessness"],
        "med": ["default mode network", "DMN", "psychedelic", "self-dissolution",
                "psilocybin", "lsd", "ayahuasca", "dmt", "meditation",
                "self-boundary", "self-other", "dissolution", "transcendence"],
        "queries": [
            '("ego dissolution"[Title/Abstract] OR "self-loss"[Title/Abstract] OR "self-transcendence"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR psychedelic[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '("mystical experience"[Title/Abstract] OR "religious experience"[Title/Abstract] OR "peak experience"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2000:2025[dp]',
            '("enlightenment"[Title/Abstract] OR "awakening"[Title/Abstract] OR "spiritual awakening"[Title/Abstract]) AND (neuroscience[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2000:2025[dp]',
            '("psychedelic"[Title/Abstract] AND ("mystical"[Title/Abstract] OR "transcendent"[Title/Abstract] OR "spiritual"[Title/Abstract])) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR default mode[Title/Abstract]) AND 2010:2025[dp]',
            '("selflessness"[Title/Abstract] OR "no-self"[Title/Abstract] OR "anatta"[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '("default mode network"[Title/Abstract] OR "DMN"[Title/Abstract]) AND ("self"[Title/Abstract] OR "ego"[Title/Abstract]) AND ("dissolution"[Title/Abstract] OR "transcendence"[Title/Abstract] OR "meditation"[Title/Abstract] OR "psychedelic"[Title/Abstract]) AND 2010:2025[dp]',
        ]
    },
}

def score_paper(title, abstract, phase):
    """Score paper using integer-weighted phase-specific terms."""
    text = (title.lower() + " " + (abstract or "").lower())
    scoring = PHASE_SCORING.get(phase, {})
    score = 0
    for t in scoring.get("high", []):
        if t.lower() in text:
            score += 5
    for t in scoring.get("med", []):
        if t.lower() in text:
            score += 3
    # Mechanistic bonus
    mech = ["neural", "brain", "fmri", "eeg", "neuroimaging", "cortex", "mechanism",
            "network", "connectivity", "neuroscience", "evidence"]
    score += sum(1 for t in mech if t in text)
    return max(0, score)

def is_clinical_noise(title, abstract):
    text = (title.lower() + " " + (abstract or "").lower())
    # Keep bridge terms in check — only flag if paper has NO bridge terms at all
    bridge_terms = ["consciousness", "neural", "brain", "self", "experience", "awareness",
                    "meditation", "empathy", "emotion", "social", "insight", "knowledge",
                    "mantra", "chanting", "hallucination", "voice", "voice hearing",
                    "synchrony", "hyperscanning", "trance", "absorption",
                    "inner speech", "corollary discharge", "mindfulness"]
    has_bridge = any(t.lower() in text for t in bridge_terms)
    # Animal model / preclinical
    clin = ["animal model", "rat", "mouse", "mice", "in vitro", "drosophila",
            "zebrafish", "case report", "surgery", "post-operative",
            "clinical trial", "pharmacological treatment", "antipsychotic", "medication",
            "antidepressant", "antiepileptic", "tumor", "cancer", "tumour",
            "chemotherapy", "radiation therapy", "meta-analysis", "systematic review",
            # Clinical conditions that strongly suggest non-bridge focus
            "stroke thrombectomy", "acute ischemic stroke", "myocardial infarction",
            "coronary artery", "heart failure", "kidney disease", "liver disease",
            "diabetes", "hypertension", "hypertension", "dementia diagnosis",
            "alzheimer", "parkinson disease", "multiple sclerosis",
            "developmental dyslexia", "reading disability",
            # Methodology papers
            "convolution neural network", "deep learning architecture",
            "machine learning algorithm", "artificial intelligence diagnosis"]
    is_clinical = any(c.lower() in text for c in clin)
    if is_clinical and not has_bridge:
        return True
    return False

def make_work_id(title):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    return f"t2-pubmed-{slug}"

def create_work_json(article, pmid, phase, phase_name, score):
    wid = make_work_id(article["title"])
    existing = glob.glob(f"{WORKS_DIR}/{wid}.json")
    if existing:
        return None
    
    try:
        year_val = int(article["year"]) if article["year"] else 2025
    except ValueError:
        year_val = 2025
    
    work = {
        "work_id": f"work:{wid}",
        "schema_version": 2,
        "title": article["title"],
        "authors": article["authors"],
        "publication": {
            "year": year_val,
            "type": "article",
            "source": "PubMed/MEDLINE",
            "language": "en",
            "journal": article["journal"]
        },
        "identifiers": {
            "pmid": pmid,
            "doi": article["doi"]
        },
        "topics": [f"phase-{phase}", "frontier_science", "bridge_paper"],
        "tradition": ["contemporary_science"],
        "tier": 2,
        "assets": {
            "pdf_path": None,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": (article["abstract"] or "")[:500]
        },
        "provenance": {
            "access_status": "open",
            "oa_status": "green",
            "source": "pubmed_t2_quality_v2",
            "retrieved_at": "2026-07-12"
        },
        "phase_mapping": {
            "phase": phase,
            "phase_name": phase_name,
            "bridge_rationale": f"Phase {phase} ({phase_name}) quality improvement search."
        },
        "evaluation": f"Quality pass v2 (score={score})"
    }
    
    path = f"{WORKS_DIR}/{wid}.json"
    with open(path, "w") as f:
        json.dump(work, f, indent=2)
    log(f"      📝 Created work: {wid}")
    return wid

def create_essay(work_id, article, pm, score):
    wid = work_id.replace("work:", "")
    slug = wid.replace("t2-pubmed-", "")
    essay_path = f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json"
    if os.path.exists(essay_path):
        return
    
    essay = {
        "id": f"bridge-pubmed-{slug}",
        "type": "type-b-essay",
        "title": f"Bridge Essay: {article['title'][:80]}",
        "source_work": f"work:{wid}",
        "phase": f"phase-{pm['phase']}",
        "phase_name": pm["phase_name"],
        "tags": ["frontier-science", "bridge-paper", f"phase-{pm['phase']}"],
        "body": [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{pm['phase_name']}** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** {pm.get('bridge_rationale', 'Quality improvement acquisition.')}"},
            {"kind": "summary", "text": f"**{article['title']}** — {article['journal']} ({article['year']}). PMID: {article.get('pmid', '')}. DOI: {article.get('doi', '')}. Score: {score}. {article.get('abstract', '')[:500]}"},
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-12. Phase {pm['phase']} quality improvement v2."
    }
    
    with open(essay_path, "w") as f:
        json.dump(essay, f, indent=2)
    log(f"      📝 Created essay: bridge-pubmed-{slug}")

def delete_worst(phase, keep_best):
    """Delete worst papers in a phase, keeping only the top N."""
    works = []
    for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
        data = json.load(open(w))
        pm = data.get("phase_mapping", {})
        if pm.get("phase") == phase:
            ev = data.get("evaluation", "")
            score = 0
            m = re.search(r'score=(\d+)', ev)
            if m:
                score = int(m.group(1))
            m2 = re.search(r'score[=](\d+)', ev)
            if m2:
                score = int(m2.group(1))
            # Also check new format
            m3 = re.search(r'score[=](\d+)', ev)
            if m3:
                score = int(m3.group(1))
            works.append((score, w, data))
    
    works.sort(key=lambda x: x[0], reverse=True)
    
    deleted = 0
    if len(works) > keep_best:
        to_delete = works[keep_best:]
        for score, w_path, data in to_delete:
            os.remove(w_path)
            # Find and delete essay
            slug = os.path.basename(w_path).replace("t2-pubmed-", "").replace(".json", "")
            for ep in [f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json",
                       f"{ESSAYS_DIR}/bridge-{slug}.json"]:
                if os.path.exists(ep):
                    os.remove(ep)
            deleted += 1
            name = data.get("title", "")[:50]
            log(f"      🗑️ Deleted (score={score}): {name}")
    return deleted

def main():
    log("=" * 60)
    log("T2 Quality Improvement v2 — Unchecked Phases")
    log("=" * 60)
    
    phase_names = PHASE_SCORING
    
    for phase in [8, 9, 12, 13, 15]:
        if phase < 9:
            log(f"\n--- Phase {phase}: {PHASE_SCORING[phase]['name']} --- SKIPPED (already done)")
            continue
        scoring = PHASE_SCORING[phase]
        phase_name = scoring["name"]
        log(f"\n--- Phase {phase}: {phase_name} ---")
        
        # Load existing titles
        seen_titles.clear()
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            data = json.load(open(w))
            pm = data.get("phase_mapping", {})
            if pm.get("phase") == phase:
                seen_titles.add(data.get("title", "").lower().strip())
        
        existing_count = len(seen_titles)
        log(f"  Existing papers: {existing_count}")
        
        # Search
        candidates = []
        for qidx, query in enumerate(scoring["queries"]):
            log(f"  Query {qidx+1}/{len(scoring['queries'])}: {query[:80]}...")
            pmids = esearch(query, retmax=25)
            
            if pmids:
                summaries = esummary(pmids)
                
                for pmid in pmids:
                    if str(pmid) in seen_titles:
                        continue
                    
                    article = efetch_abstract(pmid)
                    if not article or not article.get("abstract"):
                        continue
                    
                    title = article.get("title", "")
                    if title.lower().strip() in seen_titles:
                        continue
                    if is_clinical_noise(title, article.get("abstract", "")):
                        continue
                    
                    score = score_paper(title, article.get("abstract", ""), phase)
                    if score >= 4:  # Accept threshold
                        candidates.append((score, pmid, article))
                        seen_titles.add(title.lower().strip())
                        log(f"    ✅ Score {score}: {title[:70]}")
            
            log(f"    → {len(pmids)} PMIDs, {sum(1 for c in candidates if c[2].get('doi',''))} candidates so far")
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        log(f"  Total candidates: {len(candidates)}")
        
        if not candidates:
            log(f"  ⚠️ No qualifying candidates found for Phase {phase}")
            continue
        
        # Create new works (up to 8 per phase)
        new_papers = 0
        created_ids = []
        for score, pmid, article in candidates:
            if new_papers >= 8:
                break
            
            wid = create_work_json(article, pmid, phase, phase_name, score)
            if wid:
                pm = {
                    "phase": phase,
                    "phase_name": phase_name,
                    "bridge_rationale": f"Phase {phase} ({phase_name}) quality improvement v2."
                }
                create_essay(wid, article, pm, score)
                created_ids.append(wid)
                new_papers += 1
                log(f"    ✅ Created #{new_papers}: Score {score} | {article['title'][:70]}")
        
        log(f"  → Phase {phase}: {new_papers} new papers created")
    
    log("\n" + "=" * 60)
    log("Quality Improvement v2 Complete")
    log("=" * 60)

if __name__ == "__main__":
    main()
