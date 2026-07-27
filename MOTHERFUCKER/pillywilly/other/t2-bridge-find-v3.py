#!/usr/bin/env python3
"""
t2-bridge-find-v3.py — Targeted high-signal bridge paper acquisition.
Focuses on: Phase 9 (Language/Mantra), Phase 11 (Body-energy),
Phase 12 (Ritual), Phase 13 (Daimon), Phase 10 (Imaginal), Phase 6 (Dependent-arising).

Each phase gets 10+ creative queries that go beyond standard PubMed search patterns.
Designed to find papers the existing saturation-tier searches missed.
"""
import json, glob, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET

PROJECT = "/root/projects/blog"
WORKS_DIR = f"{PROJECT}/content/works"
ESSAYS_DIR = f"{PROJECT}/content/glossary/essays"
FRONTIER_DIR = f"{PROJECT}/library/frontier"
os.makedirs(FRONTIER_DIR, exist_ok=True)

EMAIL = "hermes@research.local"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DELAY = 1.0

# Track papers we already have to avoid duplicates
EXISTING_PMIDS = set()
EXISTING_TITLES = set()

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
        log(f"    ⚠️ HTTP error: {e}")
        return None

def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        log(f"    ⚠️ XML fetch error: {e}")
        return None

def esearch(query, retmax=20):
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

def efetch_detailed(pmid):
    """Fetch full article details including abstract, DOI, journal."""
    safe_delay()
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "rettype": "xml", "retmode": "xml", "email": EMAIL})
    url = f"{BASE_URL}efetch.fcgi?{params}"
    root = fetch_xml(url)
    if root is None:
        return None
    
    for article in root.findall(".//PubmedArticle"):
        id_el = article.find(".//PMID")
        if id_el is not None and id_el.text == pmid:
            # Title
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""
            
            # Abstract
            parts = []
            for at in article.findall(".//AbstractText"):
                parts.append("".join(at.itertext()))
            abstract = " ".join(parts)
            
            # Year
            ye = article.find(".//PubDate/Year")
            if ye is None:
                ye = article.find(".//PubDate/MedlineDate")
            year = ye.text[:4] if ye is not None and ye.text else ""
            
            # Journal
            journal_el = article.find(".//Journal/Title")
            journal = journal_el.text if journal_el is not None else ""
            
            # DOI
            doi_el = article.find(".//ArticleId[@IdType='doi']")
            doi = doi_el.text if doi_el is not None else ""
            if not doi:
                for aid in article.findall(".//ArticleId"):
                    if aid.get("IdType") == "doi":
                        doi = aid.text
                        break
            
            # Authors
            authors = []
            for auth in article.findall(".//Author"):
                ln = auth.find("LastName")
                fn = auth.find("ForeName")
                if ln is not None:
                    authors.append(f"{ln.text or ''}, {fn.text or ''}" if fn is not None else ln.text or "")
            
            # Keywords
            keywords = []
            for kw in article.findall(".//Keyword"):
                if kw.text:
                    keywords.append(kw.text)
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "year": year,
                "journal": journal,
                "doi": doi,
                "authors": authors,
                "keywords": keywords
            }
    return None

def load_existing():
    """Load all existing PMIDs to avoid duplicates."""
    for wf in glob.glob(f"{WORKS_DIR}/bridge-*.json"):
        with open(wf) as f:
            try:
                data = json.load(f)
                pm = data.get("pmid")
                if pm:
                    EXISTING_PMIDS.add(pm)
                t = data.get("title", "")
                if t:
                    EXISTING_TITLES.add(t.lower().rstrip("."))
            except:
                pass
    for wf in glob.glob(f"{WORKS_DIR}/t2-pubmed-*.json"):
        with open(wf) as f:
            try:
                data = json.load(f)
                pm = data.get("pmid") or data.get("identifiers", {}).get("pmid", "")
                if pm:
                    EXISTING_PMIDS.add(str(pm))
                t = data.get("title", "")
                if t:
                    EXISTING_TITLES.add(t.lower().rstrip("."))
            except:
                pass
    log(f"Loaded {len(EXISTING_PMIDS)} existing PMIDs, {len(EXISTING_TITLES)} titles")

def is_duplicate(pmid, title):
    if pmid and str(pmid) in EXISTING_PMIDS:
        return True
    if title and title.lower().rstrip(".") in EXISTING_TITLES:
        return True
    return False

def is_low_quality(detail):
    """Filter out clinical/engineering noise. Return True if paper should be skipped."""
    if not detail:
        return True
    title = detail.get("title", "").lower()
    abstract = (detail.get("abstract", "") or "").lower()
    
    # Skip clinical case reports, trials with no mechanistic content
    clinical_noise = [
        "case report", "case series", "clinical trial protocol",
        "systematic review protocol", "study protocol",
        "cognitive behavioral therapy", "cognitive-behavioural therapy",
        "randomized controlled trial of treatment",
        "clinical outcomes of",
    ]
    for noise in clinical_noise:
        if noise in title:
            return True
    
    # Skip engineering/technical papers
    eng_noise = [
        "deep learning algorithm for",
        "machine learning for diagnosis",
        "automated detection of",
        "artificial intelligence-based",
        "convolutional neural network for",
    ]
    for noise in eng_noise:
        if noise in title:
            return True
    
    # Skip if no abstract (can't evaluate)
    if not abstract or len(abstract) < 50:
        return True
    
    return False

def score_bridge_quality(detail, phase_concept_keywords):
    """
    Score a paper's bridge quality on 0-100 scale.
    Higher = better bridge between esoteric/philosophical concept and mechanistic science.
    """
    if not detail:
        return 0
    
    title = (detail.get("title", "") or "").lower()
    abstract = (detail.get("abstract", "") or "").lower()
    keywords = [k.lower() for k in detail.get("keywords", [])]
    journal = (detail.get("journal", "") or "").lower()
    
    score = 0
    
    # 1. Mechanistic science indicator (neural, brain, mechanism)
    mech_terms = ["neural", "brain", "cortex", "neuroscience", "neuroimaging", "fmri",
                  "eeg", "mri", "mechanism", "pathway", "circuit", "network",
                  "neurophysiological", "computational", "predictive", "connectivity",
                  "oscillation", "synchrony", "neurobiology"]
    for term in mech_terms:
        if term in title:
            score += 5
        if term in abstract:
            score += 2
    
    # 2. Specific mechanistic methods
    method_terms = ["hyperscanning", "single-neuron", "intracranial", "eeg", "meg",
                    "fmri", "neuroimaging", "tms", "physiological", "autonomic",
                    "heart rate", "heartbeat", "cardiac", "vagal"]
    for term in method_terms:
        if term in title:
            score += 3
        if term in abstract:
            score += 1
    
    # 3. Phase concept keyword match
    for kw in phase_concept_keywords:
        kw_lower = kw.lower()
        if kw_lower in title:
            score += 8
        if kw_lower in abstract:
            score += 3
        if kw_lower in keywords:
            score += 5
    
    # 4. Bridge specificity - does it directly address the philosophical/esoteric concept?
    bridge_terms = [
        "self", "consciousness", "awareness", "experience", "subjective",
        "agency", "ownership", "spirituality", "transcendence", "meditation",
        "mindfulness", "imagination", "imagery", "hallucination", "voice",
        "inner speech", "interoception", "body", "emotion", "social",
        "synchrony", "bonding", "rhythm", "music", "ritual"
    ]
    for term in bridge_terms:
        if term in title:
            score += 4
        if term in abstract:
            score += 1
    
    # 5. Journal quality
    top_journals = ["nature", "science", "neuron", "cell", "pnas", "current biology",
                    "proceedings of the national academy", "journal of neuroscience",
                    "cerebral cortex", "brain", "neuroimage", "human brain mapping",
                    "biological psychiatry", "molecular psychiatry"]
    for tj in top_journals:
        if tj in journal:
            score += 3
            break
    
    # 6. Year - newer is slightly preferred
    year = detail.get("year", "")
    if year:
        try:
            y = int(year)
            if y >= 2020:
                score += 2
            elif y >= 2015:
                score += 1
        except:
            pass
    
    # 7. Penalties
    if "review" in title and "systematic" in title:
        score -= 5  # systematic reviews are less original
    if "meta-analysis" in title:
        score -= 3  # meta-analyses less novel
    if "protocol" in title:
        score -= 10
    
    return max(0, min(100, score))

def get_pmc_id(pmid):
    """Check if a paper has a PMC ID."""
    safe_delay()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=(ext_id:{pmid})&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("resultList", {}).get("result", [])
            if results:
                return results[0].get("pmcid", "")
    except:
        pass
    return ""

def create_work_json(detail, phase, phase_name, score, bridge_tags):
    """Create a t2-pubmed format work JSON."""
    wid = detail.get("title", "Unknown")[:80]
    wid = re.sub(r'[^a-zA-Z0-9]+', '-', wid).strip('-').lower()[:70]
    work_id = f"t2-pubmed-{wid}"
    
    # Check if already exists
    wpath = f"{WORKS_DIR}/{work_id}.json"
    epath = f"{ESSAYS_DIR}/bridge-pubmed-{wid}.json"
    if os.path.exists(wpath):
        log(f"  ⏭️ Work JSON exists: {work_id}")
        return None, None
    
    authors = [{"name": a} for a in detail.get("authors", [])]
    
    work_data = {
        "work_id": f"work:{work_id}",
        "schema_version": 2,
        "title": detail.get("title", ""),
        "authors": authors,
        "identifiers": {
            "pmid": detail.get("pmid", ""),
            "doi": detail.get("doi", "")
        },
        "publication": {
            "journal": detail.get("journal", ""),
            "year": detail.get("year", "")
        },
        "abstract": detail.get("abstract", ""),
        "phase_mapping": {
            "phase": phase,
            "phase_name": phase_name
        },
        "bridge_tags": bridge_tags,
        "evaluation": f"Quality pass v3 (score={score}) — High-signal bridge paper for {phase_name}.",
        "assets": {
            "pdf_path": None,
            "nxml_path": None
        },
        "tier": 2
    }
    
    with open(wpath, "w") as f:
        json.dump(work_data, f, indent=2)
    log(f"  ✅ Created: {work_id}")
    return work_id, wpath

def create_essay(work_id, title, phase_name, phase_num, score, bridge_tags, pmid, doi, journal, year, abstract):
    """Create a Type B bridge essay JSON."""
    wid = work_id.replace("work:", "")
    essay_id = f"bridge-pubmed-{'-'.join(wid.split('-')[2:])}" if wid.startswith("t2-pubmed-") else f"bridge-{wid}"
    
    epath = f"{ESSAYS_DIR}/{essay_id}.json"
    if os.path.exists(epath):
        log(f"  ⏭️ Essay exists: {essay_id}")
        return None
    
    body = [
        {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{phase_name}** with mechanistic science from PubMed/MEDLINE."},
        {"kind": "ai", "text": f"**Bridge rationale:** Phase {phase_name} bridge-v3 targeted acquisition."},
        {"kind": "summary", "text": f"**{title}** — {journal} ({year}). PMID: {pmid}. DOI: {doi}. Score: {score}. {abstract[:500]}"}
    ]
    
    essay_data = {
        "id": essay_id,
        "type": "type-b-essay",
        "title": f"Bridge Essay: {title[:80]}",
        "source_work": f"work:{wid}",
        "phase": f"phase-{phase_num}" if isinstance(phase_num, int) else phase_num,
        "phase_name": phase_name,
        "tags": ["frontier-science", "bridge-paper"] + [f"phase-{phase_num}" if isinstance(phase_num, int) else phase_num] + bridge_tags[:3],
        "body": body,
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-12. Phase {phase_name} bridge-v3 targeted search. Score: {score}."
    }
    
    with open(epath, "w") as f:
        json.dump(essay_data, f, indent=2)
    log(f"  ✅ Essay created: {essay_id}")
    return essay_id

def search_phase(phase_num, phase_name, queries, bridge_keywords, bridge_tags_base, min_score=20):
    """
    Search a phase with multiple queries, evaluate and save high-quality papers.
    """
    log(f"\n{'='*70}")
    log(f"Phase {phase_num}: {phase_name}")
    log(f"{'='*70}")
    
    all_pmids = []
    seen_in_phase = set()
    
    for qi, query in enumerate(queries):
        log(f"\n  Query {qi+1}/{len(queries)}: {query[:80]}...")
        pmids = esearch(query, retmax=30)
        new_pmids = [p for p in pmids if p not in EXISTING_PMIDS and p not in seen_in_phase]
        log(f"    Found {len(pmids)} results, {len(new_pmids)} new")
        all_pmids.extend(new_pmids)
        seen_in_phase.update(new_pmids)
    
    log(f"\n  Total unique new candidates: {len(all_pmids)}")
    
    # Filter out batch duplicates
    all_pmids = list(dict.fromkeys(all_pmids))
    
    # Sort by recency? No, fetch and score
    all_pmids = all_pmids[:60]  # Cap candidates to conserve disk space
    
    # Fetch details and score
    candidates = []
    for pmid in all_pmids:
        detail = efetch_detailed(pmid)
        if not detail:
            continue
        
        if is_low_quality(detail):
            continue
        
        score = score_bridge_quality(detail, bridge_keywords)
        detail["bridge_score"] = score
        candidates.append(detail)
        
        log(f"  Score {score:3d}: {detail.get('title', '')[:80]}")
    
    # Sort by score
    candidates.sort(key=lambda x: x["bridge_score"], reverse=True)
    
    # Keep top candidates by quality threshold
    top = [c for c in candidates if c["bridge_score"] >= min_score]
    log(f"\n  High-signal candidates (score >= {min_score}): {len(top)}")
    
    created = 0
    for detail in top[:15]:  # Max 15 per phase per session
        # Create work JSON
        result = create_work_json(
            detail, phase_num, phase_name, detail["bridge_score"],
            bridge_tags_base + [k.lower().replace(" ", "-") for k in detail.get("keywords", [])[:3]]
        )
        if result and result[0]:
            work_id, wpath = result
            # Create essay
            create_essay(
                work_id,
                detail.get("title", ""),
                phase_name,
                phase_num,
                detail["bridge_score"],
                bridge_tags_base,
                detail.get("pmid", ""),
                detail.get("doi", ""),
                detail.get("journal", ""),
                detail.get("year", ""),
                detail.get("abstract", "")
            )
            created += 1
            
            # Try to find PMC ID and download
            pmc_id = get_pmc_id(detail["pmid"])
            if pmc_id:
                log(f"    PMC ID: {pmc_id}")
    
    log(f"\n  Created {created} new works + essays")
    return created

def main():
    log("=" * 70)
    log("T2 Bridge Paper Acquisition v3 — Targeted High-Signal Search")
    log("=" * 70)
    
    load_existing()
    
    total_created = 0
    
    # ═══════════════════════════════════════
    # Phase 9 — Language/Mantra
    # ═══════════════════════════════════════
    phase9_queries = [
        # Inner speech and meditation
        '("inner speech"[Title/Abstract] OR "self-talk"[Title/Abstract] OR "covert speech"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Mantra neurophysiology  
        '("mantra"[Title/Abstract] OR "repetitive speech"[Title/Abstract] OR "verbal repetition"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Articulatory control in meditation
        '("verbal"[Title/Abstract] OR "linguistic"[Title/Abstract] OR "phonological"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract]) AND ("prefrontal"[Title/Abstract] OR "anterior cingulate"[Title/Abstract] OR "default mode"[Title/Abstract]) AND 2010:2025[dp]',
        # Inner speech language networks
        '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract] OR "verbal thought"[Title/Abstract]) AND ("default mode network"[Title/Abstract] OR "language network"[Title/Abstract] OR "Broca"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        # Self-talk and self-regulation
        '("self-talk"[Title/Abstract] OR "self-verbalization"[Title/Abstract] OR "private speech"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract] OR "emotion"[Title/Abstract]) AND 2010:2025[dp]',
        # Mantra and altered states
        '("chanting"[Title/Abstract] OR "sacred sound"[Title/Abstract] OR "devotional"[Title/Abstract] AND "speech"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2010:2025[dp]',
        # Linguistic self in brain
        '("linguistic"[Title/Abstract] OR "narrative"[Title/Abstract] OR "autobiographical"[Title/Abstract]) AND ("self"[Title/Abstract] OR "self-concept"[Title/Abstract] OR "identity"[Title/Abstract]) AND ("medial prefrontal"[Title/Abstract] OR "default mode"[Title/Abstract] OR "temporal pole"[Title/Abstract]) AND 2010:2025[dp]',
        # Tibetan Buddhist meditation brain
        '("tibetan"[Title/Abstract] OR "buddhist"[Title/Abstract] OR "buddhism"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "chanting"[Title/Abstract] OR "prayer"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Inner speech psychopathology - non-clinical voices (daimon bridge)
        '("inner speech"[Title/Abstract] AND ("hallucination"[Title/Abstract] OR "auditory"[Title/Abstract])) AND ("non-clinical"[Title/Abstract] OR "healthy"[Title/Abstract] OR "general population"[Title/Abstract]) AND 2010:2025[dp]',
        # Prayer and brain
        '("prayer"[Title/Abstract] OR "praying"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "neuroimaging"[Title/Abstract]) AND 2010:2025[dp]',
    ]
    
    phase9_keywords = [
        "inner speech", "mantra", "meditation", "language", "verbal",
        "self-talk", "chanting", "prayer", "linguistic self", "broca",
        "articulatory", "phonological", "covert speech"
    ]
    
    phase9_tags = ["inner-speech", "mantra", "language", "verbal-meditation"]
    
    c = search_phase(9, "Language/Mantra", phase9_queries, phase9_keywords, phase9_tags, min_score=18)
    total_created += c
    
    # ═══════════════════════════════════════
    # Phase 11 — Body-energy
    # ═══════════════════════════════════════
    phase11_queries = [
        # Cardiac interoception and self
        '("interoception"[Title/Abstract] OR "interoceptive"[Title/Abstract]) AND ("cardiac"[Title/Abstract] OR "heartbeat"[Title/Abstract] OR "heart rate"[Title/Abstract]) AND ("self"[Title/Abstract] OR "self-awareness"[Title/Abstract] OR "consciousness"[Title/Abstract]) AND 2010:2025[dp]',
        # Vagal pathways to consciousness
        '("vagus"[Title/Abstract] OR "vagal"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "awareness"[Title/Abstract] OR "self"[Title/Abstract] OR "emotion"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
        # Body awareness neural correlates
        '("body awareness"[Title/Abstract] OR "somatic awareness"[Title/Abstract] OR "bodily awareness"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "insula"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Energy body/subtle energy
        '("subtle energy"[Title/Abstract] OR "biofield"[Title/Abstract] OR "life force"[Title/Abstract] OR "prana"[Title/Abstract] OR "qi"[Title/Abstract] OR "chi"[Title/Abstract]) AND ("science"[Title/Abstract] OR "scientific"[Title/Abstract] OR "physiological"[Title/Abstract] OR "measurement"[Title/Abstract]) AND 2010:2025[dp]',
        # Heart rate variability and consciousness
        '("heart rate variability"[Title/Abstract] OR "HRV"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "meditation"[Title/Abstract] OR "emotion regulation"[Title/Abstract] OR "self-regulation"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "prefrontal"[Title/Abstract]) AND 2010:2025[dp]',
        # Interoception and predictive processing
        '("interoception"[Title/Abstract] OR "interoceptive"[Title/Abstract]) AND ("predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2010:2025[dp]',
        # Gut-brain axis and cognition
        '("gut-brain"[Title/Abstract] OR "microbiome-gut-brain"[Title/Abstract] OR "gut microbiota"[Title/Abstract]) AND ("cognition"[Title/Abstract] OR "emotion"[Title/Abstract] OR "behavior"[Title/Abstract] OR "self"[Title/Abstract]) AND ("human"[Title/Abstract]) AND 2018:2025[dp]',
        # Interoceptive accuracy and spirituality
        '("interoceptive accuracy"[Title/Abstract] OR "heartbeat detection"[Title/Abstract] OR "cardioception"[Title/Abstract]) AND ("spirituality"[Title/Abstract] OR "spiritual"[Title/Abstract] OR "transcendence"[Title/Abstract] OR "mystical"[Title/Abstract]) AND 2010:2025[dp]',
        # Somatic markers and intuition
        '("somatic marker"[Title/Abstract] OR "somatic marker hypothesis"[Title/Abstract] OR "somatic state"[Title/Abstract]) AND ("decision"[Title/Abstract] OR "intuition"[Title/Abstract] OR "feeling"[Title/Abstract] OR "emotion"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
    ]
    
    phase11_keywords = [
        "interoception", "body", "energy", "spiritus", "cardiac",
        "vagal", "gut-brain", "body awareness", "heart", "visceral",
        "somatic", "embodied"
    ]
    
    phase11_tags = ["interoception", "body-energy", "spiritus", "embodied-cognition"]
    
    c = search_phase(11, "Body-energy", phase11_queries, phase11_keywords, phase11_tags, min_score=25)
    total_created += c
    
    # ═══════════════════════════════════════
    # Phase 12 — Ritual
    # ═══════════════════════════════════════
    phase12_queries = [
        # Interpersonal neural synchrony
        '("interpersonal neural synchrony"[Title/Abstract] OR "inter-brain"[Title/Abstract] OR "hyperscanning"[Title/Abstract]) AND ("social"[Title/Abstract] OR "group"[Title/Abstract] OR "collective"[Title/Abstract]) AND ("EEG"[Title/Abstract] OR "fNIRS"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2015:2025[dp]',
        # Collective emotion and synchrony
        '("collective"[Title/Abstract] AND ("emotion"[Title/Abstract] OR "emotional"[Title/Abstract]) AND ("synchrony"[Title/Abstract] OR "synchronization"[Title/Abstract] OR "contagion"[Title/Abstract])) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "physiological"[Title/Abstract]) AND 2010:2025[dp]',
        # Music and social bonding
        '("music"[Title/Abstract] AND ("social bonding"[Title/Abstract] OR "social cohesion"[Title/Abstract] OR "affiliation"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "oxytocin"[Title/Abstract] OR "endorphin"[Title/Abstract])) AND 2010:2025[dp]',
        # Rhythmic entrainment
        '("rhythmic entrainment"[Title/Abstract] OR "beat synchronization"[Title/Abstract] OR "movement synchrony"[Title/Abstract]) AND ("social"[Title/Abstract] OR "group"[Title/Abstract] OR "joint"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        # Group meditation brain
        '("group"[Title/Abstract] OR "dyadic"[Title/Abstract] OR "paired"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract]) AND ("synchrony"[Title/Abstract] OR "hyperscanning"[Title/Abstract] OR "interpersonal"[Title/Abstract] OR "inter-brain"[Title/Abstract]) AND 2010:2025[dp]',
        # Collective effervescence neuroscience
        '("collective effervescence"[Title/Abstract] OR "collective ritual"[Title/Abstract] OR "shared experience"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "physiological"[Title/Abstract] OR "autonomic"[Title/Abstract]) AND 2010:2025[dp]',
        # Choral singing brain
        '("choral singing"[Title/Abstract] OR "group singing"[Title/Abstract] OR "choir"[Title/Abstract] OR "community singing"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "oxytocin"[Title/Abstract] OR "synchrony"[Title/Abstract] OR "social"[Title/Abstract]) AND 2010:2025[dp]',
        # Dance and neural synchrony
        '("dance"[Title/Abstract] OR "dancing"[Title/Abstract]) AND ("synchrony"[Title/Abstract] OR "synchronization"[Title/Abstract] OR "hyperscanning"[Title/Abstract] OR "inter-brain"[Title/Abstract]) AND ("EEG"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        # Respiratory synchrony
        '("respiratory"[Title/Abstract] OR "breathing"[Title/Abstract]) AND ("synchronization"[Title/Abstract] OR "synchrony"[Title/Abstract]) AND ("social"[Title/Abstract] OR "group"[Title/Abstract] OR "interpersonal"[Title/Abstract] OR "joint"[Title/Abstract]) AND 2010:2025[dp]',
    ]
    
    phase12_keywords = [
        "ritual", "synchrony", "collective", "group", "social bonding",
        "hyperscanning", "entrainment", "music", "dance", "joint",
        "ceremony", "shared experience", "effervescence"
    ]
    
    phase12_tags = ["ritual", "interpersonal-synchrony", "collective", "hyperscanning"]
    
    c = search_phase(12, "Ritual", phase12_queries, phase12_keywords, phase12_tags, min_score=20)
    total_created += c
    
    # ═══════════════════════════════════════
    # Phase 13 — Daimon
    # ═══════════════════════════════════════
    phase13_queries = [
        # Inner speech agency
        '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract] OR "verbal thought"[Title/Abstract]) AND ("agency"[Title/Abstract] OR "authorship"[Title/Abstract] OR "self-monitoring"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        # Corollary discharge in auditory domain
        '("corollary discharge"[Title/Abstract] OR "efference copy"[Title/Abstract]) AND ("auditory"[Title/Abstract] OR "speech"[Title/Abstract] OR "voice"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "self"[Title/Abstract] OR "agency"[Title/Abstract]) AND 2010:2025[dp]',
        # Voice-hearing in general population
        '("voice-hearing"[Title/Abstract] OR "auditory verbal hallucination"[Title/Abstract] OR "AVH"[Title/Abstract]) AND ("non-clinical"[Title/Abstract] OR "healthy"[Title/Abstract] OR "general population"[Title/Abstract] OR "community"[Title/Abstract]) AND 2010:2025[dp]',
        # Hearing voices network
        '("auditory hallucination"[Title/Abstract] OR "hearing voices"[Title/Abstract]) AND ("temporal cortex"[Title/Abstract] OR "superior temporal"[Title/Abstract] OR "language network"[Title/Abstract] OR "default mode"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "brain"[Title/Abstract] OR "network"[Title/Abstract]) AND 2010:2025[dp]',
        # Inner speech and reality monitoring
        '("reality monitoring"[Title/Abstract] OR "source monitoring"[Title/Abstract] OR "reality discrimination"[Title/Abstract]) AND ("speech"[Title/Abstract] OR "auditory"[Title/Abstract] OR "voice"[Title/Abstract] OR "verbal"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Predictive coding auditory
        '("predictive coding"[Title/Abstract] OR "predictive processing"[Title/Abstract]) AND ("auditory"[Title/Abstract] OR "speech"[Title/Abstract] OR "voice"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "psychosis"[Title/Abstract] OR "schizophrenia"[Title/Abstract]) AND 2010:2025[dp]',
        # Spiritual/daimonic voice-hearing
        '("spiritual"[Title/Abstract] OR "religious"[Title/Abstract] OR "mystical"[Title/Abstract] OR "daimonic"[Title/Abstract]) AND ("voice"[Title/Abstract] OR "auditory"[Title/Abstract] OR "hearing"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "experience"[Title/Abstract]) AND 2000:2025[dp]',
        # Inner speech development
        '("inner speech"[Title/Abstract] OR "private speech"[Title/Abstract] OR "self-directed speech"[Title/Abstract]) AND ("development"[Title/Abstract] OR "children"[Title/Abstract] OR "child"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2000:2025[dp]',
        # Auditory imagery brain
        '("auditory imagery"[Title/Abstract] OR "auditory imagination"[Title/Abstract] OR "musical imagery"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2010:2025[dp]',
    ]
    
    phase13_keywords = [
        "voice-hearing", "inner speech", "daimon", "auditory hallucination",
        "corollary discharge", "agency", "self-monitoring", "inner voice",
        "auditory imagery", "reality monitoring"
    ]
    
    phase13_tags = ["voice-hearing", "inner-speech", "daimon", "auditory-hallucination"]
    
    c = search_phase(13, "Daimon", phase13_queries, phase13_keywords, phase13_tags, min_score=18)
    total_created += c
    
    # ═══════════════════════════════════════
    # Phase 10 — Imaginal
    # ═══════════════════════════════════════
    phase10_queries = [
        # Mental imagery neural basis
        '("mental imagery"[Title/Abstract] OR "visual imagery"[Title/Abstract] OR "motor imagery"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND ("visual cortex"[Title/Abstract] OR "fusiform"[Title/Abstract] OR "prefrontal"[Title/Abstract] OR "parietal"[Title/Abstract]) AND 2018:2025[dp]',
        # Imagination and perception shared code
        '("imagination"[Title/Abstract] AND "perception"[Title/Abstract] AND ("shared"[Title/Abstract] OR "common"[Title/Abstract] OR "overlap"[Title/Abstract] OR "similar"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract])) AND 2018:2025[dp]',
        # Mental imagery and reality monitoring
        '("mental imagery"[Title/Abstract] OR "imagination"[Title/Abstract]) AND ("reality monitoring"[Title/Abstract] OR "reality testing"[Title/Abstract] OR "source monitoring"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Mental imagery in meditation
        '("mental imagery"[Title/Abstract] OR "visualization"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "yoga"[Title/Abstract] OR "tantra"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
        # Imagery vividness and brain
        '("imagery vividness"[Title/Abstract] OR "vividness of imagery"[Title/Abstract] OR "vivid mental imagery"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract] OR "individual differences"[Title/Abstract]) AND 2010:2025[dp]',
        # Hypnagogic imagery
        '("hypnagogic"[Title/Abstract] OR "hypnopompic"[Title/Abstract] OR "dream-like"[Title/Abstract] OR "dream imagery"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
    ]
    
    phase10_keywords = [
        "imagination", "imagery", "mental imagery", "visualization", "visionary",
        "reality monitoring", "perception", "fusiform", "visual cortex"
    ]
    
    phase10_tags = ["mental-imagery", "imagination", "imaginal", "perception"]
    
    c = search_phase(10, "Imaginal", phase10_queries, phase10_keywords, phase10_tags, min_score=20)
    total_created += c
    
    # ═══════════════════════════════════════
    # Phase 6 — Dependent-arising
    # ═══════════════════════════════════════
    phase6_queries = [
        # Predictive coding and time perception
        '("predictive coding"[Title/Abstract] OR "predictive processing"[Title/Abstract]) AND ("time perception"[Title/Abstract] OR "temporal"[Title/Abstract] OR "timing"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2015:2025[dp]',
        # Free energy principle self
        '("free energy principle"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("self"[Title/Abstract] OR "selfhood"[Title/Abstract] OR "ego"[Title/Abstract] OR "minimal self"[Title/Abstract]) AND 2018:2025[dp]',
        # Causal inference perception
        '("causal inference"[Title/Abstract] OR "causal structure"[Title/Abstract] OR "causal learning"[Title/Abstract]) AND ("perception"[Title/Abstract] OR "prediction"[Title/Abstract] OR "Bayesian"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2018:2025[dp]',
        # Predictive processing and meditation
        '("predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract]) AND 2015:2025[dp]',
        # Temporal integration and consciousness
        '("temporal integration"[Title/Abstract] OR "temporal binding"[Title/Abstract] OR "temporal window"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "conscious"[Title/Abstract] OR "awareness"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2015:2025[dp]',
        # Synchronicity and pattern detection
        '("pattern detection"[Title/Abstract] OR "patternicity"[Title/Abstract] OR "apophenia"[Title/Abstract] OR "meaningful patterns"[Title/Abstract] OR "illusory pattern"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2010:2025[dp]',
        # Brain as prediction engine
        '("prediction error"[Title/Abstract] OR "prediction error signal"[Title/Abstract] OR "reward prediction error"[Title/Abstract]) AND ("perception"[Title/Abstract] OR "attention"[Title/Abstract] OR "learning"[Title/Abstract]) AND ("cortex"[Title/Abstract] OR "striatum"[Title/Abstract] OR "midbrain"[Title/Abstract]) AND 2018:2025[dp]',
    ]
    
    phase6_keywords = [
        "predictive processing", "free energy", "active inference", "dependent arising",
        "causality", "prediction", "Bayesian brain", "temporal integration",
        "synchronicity", "pattern detection"
    ]
    
    phase6_tags = ["predictive-processing", "dependent-arising", "free-energy", "causality"]
    
    c = search_phase(6, "Dependent-arising", phase6_queries, phase6_keywords, phase6_tags, min_score=18)
    total_created += c
    
    log(f"\n{'='*70}")
    log(f"SESSION COMPLETE")
    log(f"{'='*70}")
    log(f"Total new works + essays created: {total_created}")
    log(f"Summary by phase:")
    log(f"  Phase 6 (Dependent-arising)")
    log(f"  Phase 9 (Language/Mantra)")
    log(f"  Phase 10 (Imaginal)")
    log(f"  Phase 11 (Body-energy)")
    log(f"  Phase 12 (Ritual)")
    log(f"  Phase 13 (Daimon)")

if __name__ == "__main__":
    main()
