#!/usr/bin/env python3
"""
t2-quality-improvement.py — Replace weakest papers in under-performing phases.
Searches PubMed for high-signal bridge papers, creates work JSONs + essays.
Targets: Phases 3 (Heat/Fire), 7 (Emptiness/Form), 16 (Nondual/Unity),
         17 (Social Incarnation), 14 (Knowledge/Gnosis).

Uses the integer-weighted scoring from the skill (Phase 4a/7h).
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
SEEN_FILE = "/tmp/seen_titles_quality.json"

def log(msg):
    print(msg, flush=True)

def safe_delay():
    time.sleep(DELAY)

def fetch_json(url):
    """Fetch and parse JSON from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log(f"    ⚠️ HTTP error: {e}")
        return None

def fetch_xml(url):
    """Fetch and parse XML from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        log(f"    ⚠️ XML fetch error: {e}")
        return None

def esearch(query, retmax=25):
    """Search PubMed and return PMIDs."""
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
    """Get summaries for a list of PMIDs."""
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
    """Fetch full abstract and metadata for a PMID."""
    safe_delay()
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "xml", "email": EMAIL})
    url = f"{BASE_URL}efetch.fcgi?{params}"
    root = fetch_xml(url)
    if root is None:
        return None
    
    for article in root.findall(".//PubmedArticle"):
        id_el = article.find(".//PMID")
        if id_el is not None and id_el.text == pmid:
            # Abstract
            parts = []
            for at in article.findall(".//AbstractText"):
                parts.append("".join(at.itertext()))
            abstract = " ".join(parts)
            
            # Title
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()) if title_el is not None else ""
            
            # Year
            ye = article.find(".//PubDate/Year")
            if ye is None:
                ye = article.find(".//PubDate/MedlineDate")
            year = ye.text[:4] if ye is not None and ye.text else ""
            
            # Journal
            journal_el = article.find(".//Journal/Title")
            journal = journal_el.text if journal_el is not None else ""
            
            # DOI
            doi = ""
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
            
            # Authors
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
    return None

# Phase-specific bridge scoring
PHASE_SCORING = {
    3: {  # Heat/Fire - subtle energy, inner heat, kundalini
        "high": ["kundalini", "subtle energy", "g-tummo", "tummo", "inner heat",
                 "tantric", "chakra", "yogic", "psychosomatic", "body temperature",
                 "heat generating", "thermoregulation", "thermogenesis"],
        "med": ["metabolic", "mind-body", "energy metabolism", "autonomic",
                "sympathetic", "meditation", "yoga", "breathing", "wim hof"],
        "queries": [
            '("kundalini"[Title/Abstract] OR "subtle energy"[Title/Abstract] OR "psychosomatic"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "physiology"[Title/Abstract]) AND 2000:2025[dp]',
            '("body temperature"[Title/Abstract] OR "thermoregulation"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "yoga"[Title/Abstract]) AND 2000:2025[dp]',
            '("g-tummo"[Title/Abstract] OR "tummo"[Title/Abstract] OR "inner heat"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2000:2025[dp]',
            '("yogic breathing"[Title/Abstract] OR "pranayama"[Title/Abstract]) AND ("autonomic"[Title/Abstract] OR "sympathetic"[Title/Abstract] OR "parasympathetic"[Title/Abstract]) AND 2005:2025[dp]',
            '("wim hof"[Title/Abstract] OR "cold exposure"[Title/Abstract]) AND ("immune"[Title/Abstract] OR "autonomic"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2015:2025[dp]',
            '("metabolic"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
        ],
    },
    7: {  # Emptiness - self-dissolution, depersonalization, DMN decoupling
        "high": ["ego dissolution", "self-loss", "self-transcendence", "depersonalization",
                 "default mode network", "self-referential", "self-boundary", "dissolution",
                 "self-other", "boundary dissolution"],
        "med": ["DMN", "meditation", "mindfulness", "self-awareness", "self-consciousness",
                "dissociation", "derealization", "no-self", "selflessness"],
        "queries": [
            '("depersonalization"[Title/Abstract] OR "derealization"[Title/Abstract]) AND ("self-referential"[Title/Abstract] OR "self-processing"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("ego dissolution"[Title/Abstract] OR "self-loss"[Title/Abstract] OR "self-other"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("self-awareness"[Title/Abstract] OR "self-consciousness"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "prefrontal"[Title/Abstract]) AND 2015:2025[dp]',
            '("self-dissolution"[Title/Abstract] OR "boundary dissolution"[Title/Abstract]) AND ("experience"[Title/Abstract] OR "meditation"[Title/Abstract]) AND 2005:2025[dp]',
            '("ego"[Title/Abstract] AND "dissolution"[Title/Abstract] AND ("psychedelic"[Title/Abstract] OR "psilocybin"[Title/Abstract] OR "meditation"[Title/Abstract])) AND 2015:2025[dp]',
            '("selflessness"[Title/Abstract] OR "no-self"[Title/Abstract] OR "anatta"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2005:2025[dp]',
        ],
    },
    14: {  # Knowledge/Gnosis - insight, noetic, gnostic, intuition
        "high": ["insight", "aha moment", "insight problem", "creative insight",
                 "semantic cognition", "conceptual knowledge", "abstract knowledge",
                 "metacognition", "noetic", "gnostic", "intuitive knowledge",
                 "felt sense", "knowing", "belief updating", "epistemic"],
        "med": ["prediction error", "anterior temporal", "creative", "cognition",
                "default mode", "prefrontal", "knowledge", "intuition"],
        "queries": [
            '("insight"[Title/Abstract] OR "aha moment"[Title/Abstract] OR "insight problem"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2010:2025[dp]',
            '("metacognition"[Title/Abstract] AND ("anterior prefrontal"[Title/Abstract] OR "frontal pole"[Title/Abstract] OR "PFC"[Title/Abstract])) AND 2010:2025[dp]',
            '("semantic cognition"[Title/Abstract] OR "conceptual knowledge"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "ATL"[Title/Abstract] OR "anterior temporal"[Title/Abstract]) AND 2010:2025[dp]',
            '("creative insight"[Title/Abstract] OR "insight"[Title/Abstract] AND "default mode"[Title/Abstract] AND "executive control"[Title/Abstract]) AND 2010:2025[dp]',
            '("belief updating"[Title/Abstract] OR "epistemic"[Title/Abstract] AND "emotion"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("intuition"[Title/Abstract] OR "intuitive"[Title/Abstract]) AND ("decision making"[Title/Abstract] OR "judgment"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
        ],
    },
    16: {  # Nondual/Unity - nondual awareness, oneness, pure consciousness
        "high": ["nondual", "non-dual", "nondual awareness", "oneness", "unity experience",
                 "oceanic", "sense of unity", "pure awareness", "pure consciousness",
                 "awareness itself", "minimal phenomenal experience"],
        "med": ["self-other", "boundary dissolution", "ego dissolution",
                "default mode", "psychedelic", "meditation", "transcend"],
        "queries": [
            '("nondual"[Title/Abstract] OR "non-dual"[Title/Abstract] OR "nondual awareness"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "EEG"[Title/Abstract] OR "brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2005:2025[dp]',
            '("oneness"[Title/Abstract] OR "unity experience"[Title/Abstract] OR "sense of unity"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2005:2025[dp]',
            '("pure consciousness"[Title/Abstract] OR "pure awareness"[Title/Abstract] OR "awareness itself"[Title/Abstract]) AND ("philosophy"[Title/Abstract] OR "neuroscience"[Title/Abstract] OR "meditation"[Title/Abstract]) AND 2000:2025[dp]',
            '("self-transcendence"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "DMN"[Title/Abstract] OR "default mode"[Title/Abstract])) AND 2005:2025[dp]',
            '("oceanic"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "experience"[Title/Abstract])) AND 2000:2025[dp]',
            '("minimal phenomenal experience"[Title/Abstract] OR "minimal self"[Title/Abstract] AND "meditation"[Title/Abstract]) AND 2010:2025[dp]',
            '("breathwork"[Title/Abstract] OR "conscious breathing"[Title/Abstract]) AND ("altered states"[Title/Abstract] OR "mystical experience"[Title/Abstract] OR "transcend"[Title/Abstract]) AND 2015:2025[dp]',
            '("self-transcendence"[Title/Abstract] AND ("autonomic"[Title/Abstract] OR "heart rate"[Title/Abstract] OR "physiology"[Title/Abstract])) AND 2005:2025[dp]',
        ],
    },
    17: {  # Social Incarnation - intersubjectivity, empathy, social
        "high": ["intersubjectivity", "embodied empathy", "shared intentionality",
                 "second-person neuroscience", "social cognition", "empathy",
                 "mirror neuron", "social touch", "affective touch"],
        "med": ["social", "interaction", "joint attention", "TPJ", "medial prefrontal",
                "premotor", "parietal", "insula", "emotional sharing", "compassion"],
        "queries": [
            '("social touch"[Title/Abstract] OR "affective touch"[Title/Abstract]) AND ("insula"[Title/Abstract] OR "somatosensory"[Title/Abstract]) AND ("empathy"[Title/Abstract] OR "social cognition"[Title/Abstract]) AND 2015:2025[dp]',
            '("mirror neuron"[Title/Abstract] AND "empathy"[Title/Abstract] AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract] OR "insula"[Title/Abstract])) AND 2005:2025[dp]',
            '("second-person"[Title/Abstract] OR "intersubjectivity"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
            '("shared intentionality"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "development"[Title/Abstract]) AND 2005:2025[dp]',
            '("compassion"[Title/Abstract] OR "empathy"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "loving-kindness"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("emotional sharing"[Title/Abstract] OR "affective resonance"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
}

def score_paper(title, abstract, phase):
    """Score paper using integer-weighted phase-specific terms."""
    text = (title.lower() + " " + (abstract or ""))
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
    return max(0, score), scoring.get("high", [])

def is_clinical_noise(title, abstract):
    """Check if paper is clinical noise (should be rejected)."""
    text = (title.lower() + " " + (abstract or "").lower())
    bridge_terms = ["consciousness", "neural", "brain", "self", "experience", "awareness",
                    "meditation", "empathy", "emotion", "social", "insight", "knowledge",
                    "nondual", "interoception", "breathing", "mindfulness"]
    has_bridge = any(t in text for t in bridge_terms)
    clin = ["animal model", "rat", "mouse", "mice", "in vitro", "drosophila",
            "zebrafish", "case report", "surgery", "post-operative"]
    return any(c in text for c in clin)

def make_work_id(title):
    """Generate a work ID from the title."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    return f"t2-pubmed-{slug}"

def create_work_json(article, pmid, phase, phase_name, score, bridge_matches):
    """Create work JSON for a new bridge paper."""
    wid = make_work_id(article["title"])
    # Check for duplicates
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
            "abstract": article["abstract"][:500]
        },
        "provenance": {
            "access_status": "unknown",
            "oa_status": "unknown",
            "source": "pubmed_t2_quality_improvement",
            "retrieved_at": "2026-07-12"
        },
        "phase_mapping": {
            "phase": phase,
            "phase_name": phase_name,
            "bridge_rationale": f"Score {score}: Bridge terms matched: {', '.join(bridge_matches[:5])}"
        },
        "evaluation": f"Score {score}: Quality improvement acquisition",
        "nxml_file": None
    }
    
    path = f"{WORKS_DIR}/{wid}.json"
    with open(path, "w") as f:
        json.dump(work, f, indent=2)
    return wid

def create_essay(wid, work):
    """Create Type B essay JSON."""
    pm = work["phase_mapping"]
    essay = {
        "id": wid,
        "type": "type-b-essay",
        "title": f"Bridge Essay: {work['title'][:80]}",
        "source_work": f"work:{work['work_id']}",
        "phase": f"phase-{pm['phase']}",
        "phase_name": pm["phase_name"],
        "tags": ["frontier-science", "bridge-paper", f"phase-{pm['phase']}"],
        "body": [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{pm['phase_name']}** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** {pm['bridge_rationale']}"},
            {"kind": "summary", "text": f"**{work['title']}** — {work['publication']['journal']} ({work['publication']['year']}). PMID: {work['identifiers']['pmid']}. DOI: {work['identifiers']['doi']}. {work['assets']['abstract'][:500]}"},
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-12. Phase {pm['phase']} quality improvement."
    }
    path = f"{ESSAYS_DIR}/{wid}.json"
    with open(path, "w") as f:
        json.dump(essay, f, indent=2)
    return path

def main():
    log("=" * 70)
    log("QUALITY IMPROVEMENT ACQUISITION")
    log("Targeting: Phases 3, 7, 14, 16, 17")
    log("=" * 70)
    
    phase_names = {
        3: "Heat/Fire", 7: "Emptiness/Form", 14: "Knowledge/Gnosis",
        16: "Nondual/Unity", 17: "Social Incarnation"
    }
    
    # Load existing titles to avoid duplicates
    log("Loading existing titles...")
    for wf in glob.glob(f"{WORKS_DIR}/t2-*.json") + glob.glob(f"{WORKS_DIR}/bridge-*.json"):
        try:
            with open(wf) as f:
                data = json.load(f)
            t = data.get("title", data.get("title", "")).lower().strip()
            if t:
                seen_titles.add(t)
        except:
            pass
    log(f"Loaded {len(seen_titles)} existing titles")
    
    total_new = 0
    
    for phase in [3, 7, 14, 16, 17]:
        scoring = PHASE_SCORING[phase]
        phase_name = phase_names[phase]
        queries = scoring["queries"]
        
        log(f"\n--- Phase {phase}: {phase_name} ---")
        log(f"Running {len(queries)} targeted queries...")
        
        new_papers = 0
        
        for qi, query in enumerate(queries):
            log(f"\n  Query {qi+1}/{len(queries)}")
            
            pmids = esearch(query, retmax=25)
            if not pmids:
                log(f"    No results")
                continue
            log(f"    Found {len(pmids)} PMIDs")
            
            # Get summaries
            summaries = esummary(pmids)
            
            for pmid in pmids:
                if new_papers >= 8:  # Limit per phase
                    break
                
                title = ""
                if pmid in summaries and "result" in summaries:
                    title = summaries[pmid].get("title", "")
                
                # Skip if we've seen this title
                title_lower = title.lower().strip()
                if title_lower in seen_titles:
                    continue
                
                # Fetch full abstract
                article = efetch_abstract(pmid)
                if not article or not article.get("abstract", ""):
                    continue
                
                # Score
                score, bridge_matches = score_paper(
                    article["title"], article["abstract"], phase
                )
                
                # Reject low scores or clinical noise
                if score < 6:
                    continue
                if is_clinical_noise(article["title"], article["abstract"]):
                    continue
                
                seen_titles.add(title_lower)
                
                # Create work JSON
                wid = create_work_json(article, pmid, phase, phase_name, score, bridge_matches)
                if wid is None:
                    log(f"    ⏭️ Duplicate or existing: {article['title'][:60]}")
                    continue
                
                # Create essay
                work_path = f"{WORKS_DIR}/{wid}.json"
                with open(work_path) as f:
                    work_data = json.load(f)
                create_essay(wid, work_data)
                
                log(f"    ✅ Phase {phase} | Score {score} | {article['title'][:70]}")
                new_papers += 1
                total_new += 1
        
        log(f"  → Phase {phase}: {new_papers} new papers acquired")
    
    log(f"\n{'='*70}")
    log(f"TOTAL: {total_new} new bridge papers acquired")
    log(f"{'='*70}")

if __name__ == "__main__":
    main()
