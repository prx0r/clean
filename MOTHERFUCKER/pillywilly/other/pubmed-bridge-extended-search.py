#!/usr/bin/env python3
"""Extended acquisition for phases that need more papers with fresh queries."""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET, tarfile, subprocess

CONTENT_WORKS = "/root/projects/blog/content/works"
CONTENT_ESSAYS = "/root/projects/blog/content/glossary/essays"
LIBRARY_FRONTIER = "/root/projects/blog/library/frontier"
ACQUISITION_LOG = "/root/projects/blog/hermes/notes/t2-acquisition-log.md"

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OA_SVC = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
EMAIL = "hermes@research.local"
DELAY = 1.0

# Extended phases with new, more specific queries
EXTENDED = {
    "phase-9-language": {
        "phase": 9, "name": "Language/Mantra",
        "concept": "Inner speech, mantra meditation, focused attention, language as mantra.",
        "bridge_rationale": "Language as mantra — inner speech, mantra meditation, semantic cognition, focused attention.",
        "queries": [
            # Inner speech and its neural basis
            '("inner speech"[Title/Abstract] OR "verbal thinking"[Title/Abstract]) AND ("perisylvian"[Title/Abstract] OR "arcuate fasciculus"[Title/Abstract] OR "Broca"[Title/Abstract] OR "Wernicke"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2008:2025[dp]',
            # Semantic cognition (abstract concept grounding)
            '("semantic cognition"[Title/Abstract] OR "abstract concepts"[Title/Abstract] OR "semantic control"[Title/Abstract]) AND ("anterior temporal"[Title/Abstract] OR "inferior frontal"[Title/Abstract] OR "angular gyrus"[Title/Abstract]) AND 2010:2025[dp]',
            # Mantra/chanting/verbal repetition
            '("chanting"[Title/Abstract] OR "chant"[Title/Abstract] OR "repetitive speech"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2005:2025[dp]',
            # Language acquisition and symbol grounding
            '("symbol grounding"[Title/Abstract] OR "lexical processing"[Title/Abstract] OR "word learning"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            # Default mode in mantra/focused attention meditation
            '("focused attention"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("brain network"[Title/Abstract] OR "default mode"[Title/Abstract] OR "frontoparietal"[Title/Abstract])) AND 2010:2025[dp]',
        ],
    },
    "phase-15-ecology": {
        "phase": 15, "name": "Ecology/Animism",
        "concept": "Nature connectedness, biophilia, environmental neuroscience.",
        "bridge_rationale": "Ecology/Animism — nature connectedness, biophilia, environmental neuroscience.",
        "queries": [
            # Environmental neuroscience with neuroimaging
            '("nature"[Title/Abstract] AND "urban"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND ("stress"[Title/Abstract] OR "restoration"[Title/Abstract] OR "attention"[Title/Abstract])) AND 2010:2025[dp]',
            # Blue-green space and brain health
            '("green space"[Title/Abstract] OR "blue space"[Title/Abstract] OR "forest bathing"[Title/Abstract] OR "Shinrin-yoku"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "cognitive"[Title/Abstract] OR "neural"[Title/Abstract] OR "mental health"[Title/Abstract]) AND 2010:2025[dp]',
            # Animals, nature connectedness
            '("human-animal interaction"[Title/Abstract] OR "animal-assisted"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "oxytocin"[Title/Abstract] OR "cortisol"[Title/Abstract]) AND 2015:2025[dp]',
            # Connectedness to nature / nature relatedness
            '("connectedness to nature"[Title/Abstract] OR "nature relatedness"[Title/Abstract] OR "environmental identity"[Title/Abstract]) AND ("psychology"[Title/Abstract] OR "wellbeing"[Title/Abstract] OR "mental"[Title/Abstract]) AND 2010:2025[dp]',
            # Awe and wonder in nature
            '("awe"[Title/Abstract] AND "nature"[Title/Abstract] AND ("emotion"[Title/Abstract] OR "well-being"[Title/Abstract] OR "prosocial"[Title/Abstract])) AND 2015:2025[dp]',
        ],
    },
    "phase-16-transcendence": {
        "phase": 16, "name": "Visionary Cosmologies",
        "concept": "Self-transcendence, mystical experience, awe, numinous.",
        "bridge_rationale": "Visionary cosmologies — self-transcendence, mystical experience, awe, cosmic consciousness.",
        "queries": [
            # Near-death experiences and brain
            '("near-death experience"[Title/Abstract] OR "NDE"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "temporal lobe"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            # Mystical/peak experiences and brain
            '("peak experience"[Title/Abstract] OR "flow state"[Title/Abstract] OR "optimal experience"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2010:2025[dp]',
            # Religious/spiritual experiences neuroscience
            '("religious experience"[Title/Abstract] OR "spiritual experience"[Title/Abstract] OR "prayer"[Title/Abstract] AND "brain"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "neuroimaging"[Title/Abstract]) AND 2005:2025[dp]',
            # Cosmic/unity consciousness
            '("unity"[Title/Abstract] AND "consciousness"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "meditation"[Title/Abstract] OR "psychedelic"[Title/Abstract])) AND 2010:2025[dp]',
            # Awe and self-diminishment
            '("awe"[Title/Abstract] AND "self"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract])) AND 2015:2025[dp]',
        ],
    },
    "phase-17-social": {
        "phase": 17, "name": "Social Incarnation",
        "concept": "Intersubjectivity, embodied empathy, social predictive processing.",
        "bridge_rationale": "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing.",
        "queries": [
            # Social predictive processing
            '("predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("social"[Title/Abstract] OR "empathy"[Title/Abstract] OR "interpersonal"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2015:2025[dp]',
            # Embodied simulation / resonance
            '("embodied simulation"[Title/Abstract] OR "neural resonance"[Title/Abstract] OR "motor resonance"[Title/Abstract]) AND ("empathy"[Title/Abstract] OR "social"[Title/Abstract] OR "action understanding"[Title/Abstract]) AND 2010:2025[dp]',
            # Interoception and social cognition
            '("interoception"[Title/Abstract] OR "interoceptive"[Title/Abstract]) AND ("social cognition"[Title/Abstract] OR "empathy"[Title/Abstract] OR "emotional"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "insula"[Title/Abstract] OR "anterior cingulate"[Title/Abstract]) AND 2015:2025[dp]',
            # Social touch / affective touch
            '("affective touch"[Title/Abstract] OR "social touch"[Title/Abstract] OR "CT afferent"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "insula"[Title/Abstract] OR "social"[Title/Abstract]) AND 2015:2025[dp]',
            # Implicit social cognition / mirror system
            '("mirror neuron"[Title/Abstract] OR "mirror system"[Title/Abstract]) AND ("social cognition"[Title/Abstract] OR "empathy"[Title/Abstract] OR "imitation"[Title/Abstract]) AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-3-4e-cognition": {
        "phase": 3, "name": "Mind as Computer Critique",
        "concept": "Embodied, enactive, extended, situated cognition.",
        "bridge_rationale": "4E cognition — embodied, situated, extended; post-cognitivist neuroscience.",
        "queries": [
            # Predictive processing and embodiment
            '("predictive processing"[Title/Abstract] AND ("embodied"[Title/Abstract] OR "sensorimotor"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("perception"[Title/Abstract] OR "cognition"[Title/Abstract] OR "action"[Title/Abstract])) AND 2015:2025[dp]',
            # Free energy principle and mind
            '("free energy principle"[Title/Abstract] AND ("mind"[Title/Abstract] OR "cognition"[Title/Abstract] OR "consciousness"[Title/Abstract] OR "self"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2015:2025[dp]',
            # Ecological psychology / direct perception
            '("ecological psychology"[Title/Abstract] OR "direct perception"[Title/Abstract] OR "affordance"[Title/Abstract] AND "perception"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2010:2025[dp]',
            # Varieties of embodiment (radical, minimal)
            '("radical embodied"[Title/Abstract] OR "minimal embodied"[Title/Abstract] OR "extended cognition"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognitive science"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-7-emptiness": {
        "phase": 7, "name": "Emptiness",
        "concept": "Self-dissolution, DMN decoupling, ego dissolution, nondual.",
        "bridge_rationale": "Emptiness — self-dissolution, DMN decoupling, ego dissolution, nondual awareness.",
        "queries": [
            # Psychedelic ego dissolution
            '("psilocybin"[Title/Abstract] OR "psychedelic"[Title/Abstract]) AND ("self"[Title/Abstract] OR "ego"[Title/Abstract] OR "default mode"[Title/Abstract] OR "DMN"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2018:2025[dp]',
            # Mindfulness and self-referential processing
            '("mindfulness"[Title/Abstract] AND ("self-referential"[Title/Abstract] OR "default mode"[Title/Abstract] OR "DMN"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract])) AND 2015:2025[dp]',
            # Meditation-induced self-transcendence
            '("meditation"[Title/Abstract] AND "self"[Title/Abstract] AND ("posterior cingulate"[Title/Abstract] OR "mPFC"[Title/Abstract] OR "precuneus"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2015:2025[dp]',
            # Body-awareness and self-boundary
            '("body awareness"[Title/Abstract] OR "interoception"[Title/Abstract] OR "proprioception"[Title/Abstract]) AND ("self"[Title/Abstract] OR "self-boundary"[Title/Abstract] OR "self-other"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "insula"[Title/Abstract]) AND 2015:2025[dp]',
            # Selflessness/self-processing in contemplative neuroscience
            '("selflessness"[Title/Abstract] OR "self-processing"[Title/Abstract] OR "self-referential"[Title/Abstract] AND "meditation"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-8-spontaneous": {
        "phase": 8, "name": "Non-fabrication",
        "concept": "Spontaneous thought, mind-wandering, creative cognition.",
        "bridge_rationale": "Non-fabrication — spontaneous thought, mind-wandering, creative insight, DMN.",
        "queries": [
            # Resting state and spontaneous cognition
            '("resting state"[Title/Abstract] AND "cognition"[Title/Abstract] AND ("default mode"[Title/Abstract] OR "DMN"[Title/Abstract]) AND ("mind-wandering"[Title/Abstract] OR "spontaneous"[Title/Abstract] OR "thought"[Title/Abstract])) AND 2015:2025[dp]',
            # Creative cognition and brain networks
            '("creative"[Title/Abstract] AND "cognition"[Title/Abstract] AND ("default mode"[Title/Abstract] OR "executive network"[Title/Abstract] OR "salience"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2015:2025[dp]',
            # Daydreaming and internal mentation
            '("daydreaming"[Title/Abstract] OR "fantasy"[Title/Abstract] OR "imagination"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2010:2025[dp]',
            # Involuntary autobiographical memory
            '("involuntary memory"[Title/Abstract] OR "autobiographical memory"[Title/Abstract] AND "spontaneous"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "hippocampus"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
}

def count_phase(phase_num):
    seen = set()
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            pm = d.get("phase_mapping", {})
            if pm and pm.get("phase") == phase_num:
                seen.add(w)
        except: pass
    return len(seen)

def api_call(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/2.1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  [WARN] Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [ERROR] HTTP {e.code}")
                if attempt < max_retries - 1: time.sleep(3)
        except Exception as e:
            print(f"  [ERROR] {e}")
            if attempt < max_retries - 1: time.sleep(3)
    return None

def search_pubmed(query, retmax=30):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{ESEARCH}?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch_esummary(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{ESUMMARY}?{params}")
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
            result[uid] = {
                "title": doc.get("title", ""), "source": doc.get("source", ""),
                "pubdate": doc.get("pubdate", ""), "doi": doi, "pmc": pmc,
                "authors": [a.get("name", "") for a in doc.get("authors", [])[:5]],
            }
        return result
    except: return {}

def fetch_abstracts(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{EFETCH}?{params}")
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
                lbl = ae.get("Label", ""); txt = "".join(ae.itertext()).strip()
                abs_parts.append(f"{lbl}: {txt}" if lbl else txt)
            abstract = " ".join(abs_parts)
            ye = article.find(".//PubDate/Year")
            if ye is None: ye = article.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            articles[pmid] = {"title": title, "abstract": abstract, "year": year}
    except: pass
    return articles

def score_paper(title, abstract, phase_key):
    text = f"{title} {abstract}".lower()
    noise = ["clinical trial", "pharmacological", "treatment outcome", "case report",
             "rat ", " mice ", "murine", "animal model", "surgery",
             "randomized controlled", "phase 2", "phase 3"]
    for n in noise:
        if n in text:
            return 0, f"Noise"
    
    # Phase-specific bridge terms (same as main script)
    phase_terms = {
        "phase-9-language": [
            ("inner speech", 1.5), ("semantic cognition", 1.5), ("semantic control", 1.2),
            ("abstract concept", 1.0), ("mantra", 1.5), ("chanting", 1.2),
            ("symbol grounding", 1.0), ("focused attention", 0.8), ("verbal", 0.6),
            ("language", 0.4), ("arcuate", 0.5), ("perisylvian", 0.6),
        ],
        "phase-15-ecology": [
            ("nature connectedness", 1.5), ("biophilia", 1.5), ("green space", 0.8),
            ("forest bathing", 1.0), ("connectedness to nature", 1.5), ("awe", 0.8),
            ("nature", 0.3), ("restoration", 0.5), ("animal-assisted", 0.8),
            ("human-animal", 0.6), ("environmental", 0.4),
        ],
        "phase-16-transcendence": [
            ("near-death", 1.2), ("mystical experience", 1.5), ("self-transcendence", 1.5),
            ("awe", 0.8), ("flow state", 1.0), ("peak experience", 1.2),
            ("religious experience", 1.0), ("spiritual experience", 1.0),
            ("unity consciousness", 1.5), ("numinous", 1.5), ("transcendence", 1.2),
        ],
        "phase-17-social": [
            ("predictive processing", 0.5), ("embodied simulation", 1.5),
            ("affective touch", 1.2), ("social touch", 1.0),
            ("interoception", 0.6), ("mirror neuron", 0.8), ("motor resonance", 1.0),
            ("social cognition", 0.5), ("empathy", 0.5), ("intersubjectivity", 1.5),
            ("premotor", 0.4),
        ],
        "phase-3-4e-cognition": [
            ("predictive processing", 0.6), ("free energy principle", 0.6),
            ("embodied", 0.6), ("enactive", 1.2), ("extended mind", 1.2),
            ("ecological psychology", 1.2), ("affordance", 0.8),
            ("radical embodied", 1.2), ("direct perception", 0.8),
            ("situated cognition", 1.0),
        ],
        "phase-7-emptiness": [
            ("psilocybin", 0.8), ("psychedelic", 0.6), ("ego dissolution", 1.5),
            ("default mode", 0.6), ("self-referential", 0.6), ("mindfulness", 0.5),
            ("meditation", 0.4), ("self", 0.2), ("posterior cingulate", 0.4),
            ("precuneus", 0.4), ("body awareness", 0.5), ("selflessness", 1.0),
            ("nondual", 1.5),
        ],
        "phase-8-spontaneous": [
            ("resting state", 0.5), ("mind-wandering", 1.5), ("daydreaming", 1.2),
            ("creative", 0.5), ("spontaneous thought", 1.5), ("default mode", 0.5),
            ("involuntary memory", 1.2), ("fantasy", 0.6), ("imagination", 0.5),
            ("internal mentation", 1.0), ("autobiographical", 0.4),
        ],
    }
    
    score = 0
    terms = phase_terms.get(phase_key, [])
    for term, weight in terms:
        if term in text:
            score += weight
    
    # Cross-phase boost
    cross = [("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("neuroimaging", 0.5), ("cortex", 0.3)]
    for term, weight in cross:
        if term in text: score += weight
    
    if score >= 2.5: return 3, f"Excellent (score={score:.1f})"
    elif score >= 1.8: return 2, f"Good (score={score:.1f})"
    elif score >= 1.2: return 1, f"Marginal (score={score:.1f})"
    else: return 0, f"Low (score={score:.1f})"

def download_pdf(pmc_id, title):
    if not pmc_id: return None
    pmc_clean = pmc_id.replace("PMC", "")
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', title)[:50].strip('_')
    pdf_basename = f"t2-pubmed-pmc{pmc_clean}_{slug}.pdf"
    pdf_path = f"{LIBRARY_FRONTIER}/{pdf_basename}"
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000: return pdf_basename
    time.sleep(DELAY)
    oa_url = f"{OA_SVC}?id=PMC{pmc_clean}"
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
        subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "120",
                       "-o", local_tgz, https_url], check=True, timeout=130)
    except: return None
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000: return None
    try:
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "MOESM" not in m.name and "Suppl" not in m.name]
            if not pdfs:
                pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs: os.remove(local_tgz); return None
            with tar.extractfile(pdfs[0]) as src, open(pdf_path, "wb") as dst:
                dst.write(src.read())
        os.remove(local_tgz)
        if os.path.getsize(pdf_path) > 5000: return pdf_basename
        else: os.remove(pdf_path); return None
    except:
        if os.path.exists(local_tgz): os.remove(local_tgz)
        return None

def create_slug(title):
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    return '-'.join(slug.split('-')[:15])

def acquire_phase(phase_key, target=50):
    info = EXTENDED[phase_key]
    phase = info["phase"]
    name = info["name"]
    
    existing = count_phase(phase)
    need = max(0, target - existing)
    print(f"\n{'='*60}")
    print(f"Phase {phase}: {name} (extended search)")
    print(f"Existing: {existing}, Need: {need}")
    print(f"{'='*60}")
    
    if need <= 0:
        print(f"  Already at target.")
        return 0
    
    # Load seen titles
    seen_titles = set()
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            seen_titles.add(d.get("title", "").lower().strip())
        except: pass
    
    candidates = []
    for qi, query in enumerate(info["queries"]):
        if len(candidates) >= need * 2:
            break
        if len(candidates) >= 40:
            break
        
        print(f"\n  Query {qi+1}/{len(info['queries'])}...")
        pmids = search_pubmed(query, retmax=30)
        if not pmids:
            print(f"    No results")
            continue
        print(f"    Found {len(pmids)} PMIDs")
        
        summaries = fetch_esummary(pmids)
        abstracts = fetch_abstracts(pmids)
        
        for pmid in pmids:
            if len(candidates) >= need * 2:
                break
            summary = summaries.get(pmid, {})
            abstract_data = abstracts.get(pmid, {})
            title = summary.get("title", abstract_data.get("title", ""))
            if not title: continue
            title_lower = title.lower().strip()
            if title_lower in seen_titles: continue
            
            abstract = abstract_data.get("abstract", "")
            score_val, score_label = score_paper(title, abstract, phase_key)
            if score_val < 1:  # Accept marginal and above
                continue
            
            seen_titles.add(title_lower)
            article = {
                "pmid": pmid, "title": title, "abstract": abstract,
                "year": abstract_data.get("year", summary.get("pubdate", "")[:4]),
                "journal": summary.get("source", ""),
                "authors": summary.get("authors", []), "doi": summary.get("doi", ""),
            }
            candidates.append((score_val, article, summary, score_label))
            print(f"    + [{score_label}] {title[:70]}...")
    
    if not candidates:
        print(f"  No candidates found.")
        return 0
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[:min(need, len(candidates))]
    
    print(f"\n  Selected {len(selected)} papers")
    details = []
    created = 0
    
    for score_val, article, summary, score_label in selected:
        pmid = article["pmid"]; title = article["title"]
        pmc_id = summary.get("pmc", "")
        pdf_path = download_pdf(pmc_id, title) if pmc_id else None
        
        # Create work JSON
        slug = create_slug(title)
        work_id = f"work:t2-pubmed-{slug}"
        doi = article.get("doi", "")
        year = article.get("year", "")
        journal = article.get("journal", "")
        abstract = article.get("abstract", "")[:500]
        
        work_data = {
            "work_id": work_id, "schema_version": 2, "title": title,
            "publication": {
                "year": int(year) if year and year.isdigit() else 0,
                "type": "article", "source": "PubMed/MEDLINE", "language": "en", "journal": journal
            },
            "identifiers": {"pmid": pmid, "doi": doi},
            "topics": [f"phase-{phase}-{name.lower().replace('/', '-').replace(' ', '-')}", "frontier_science", "bridge_paper"],
            "tradition": ["contemporary_science"], "tier": 2,
            "assets": {
                "pdf_path": pdf_path,
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "abstract": abstract
            },
            "provenance": {
                "access_status": "open", "oa_status": "green",
                "source": "pubmed_t2_search", "retrieved_at": time.strftime("%Y-%m-%d")
            },
            "phase_mapping": {"phase": phase, "phase_name": name, "bridge_rationale": info["bridge_rationale"]}
        }
        
        work_file = f"{CONTENT_WORKS}/t2-pubmed-{slug}.json"
        with open(work_file, "w") as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        # Essay JSON
        essay_data = {
            "id": f"essay-{work_id.replace(':', '-')}",
            "type": "type-b-essay",
            "title": f"Bridge Essay: {title}",
            "source_work": work_id,
            "phase": f"phase-{phase}",
            "phase_name": name,
            "concept": info["concept"],
            "tags": ["frontier-science", "bridge-paper", f"phase-{phase}"],
            "body": [
                {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{name}** with mechanistic science from PubMed/MEDLINE."},
                {"kind": "ai", "text": f"**Bridge rationale:** {info['bridge_rationale']}"},
                {"kind": "ai", "text": f"**Phase context:** {info['concept']}"},
                {"kind": "summary", "text": f"**{title}** — {journal} ({year}). DOI: {doi}. PMID: {pmid}. {abstract}"},
            ],
            "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase} ({name})."
        }
        
        essay_file = f"{CONTENT_ESSAYS}/bridge-pubmed-{slug}.json"
        with open(essay_file, "w") as f:
            json.dump(essay_data, f, indent=2, ensure_ascii=False)
        
        created += 1
        detail = f"  ✓ {title[:60]}... ({journal} {year}) — {score_label}"
        if pdf_path: detail += " [PDF]"
        details.append(detail)
        print(detail)
    
    # Log
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n## Session: {ts}\n**Phase:** {name} (extended)\n**New papers:** {created}\n\n"
    for d in details:
        log_entry += f"- {d}\n"
    try:
        with open(ACQUISITION_LOG, "a") as f:
            f.write(log_entry)
    except: pass
    
    print(f"\n  Phase {phase} complete: {created} new papers (total: {existing + created})")
    return created

if __name__ == "__main__":
    os.makedirs(CONTENT_WORKS, exist_ok=True)
    os.makedirs(CONTENT_ESSAYS, exist_ok=True)
    os.makedirs(LIBRARY_FRONTIER, exist_ok=True)
    
    if len(sys.argv) > 1:
        phases_to_run = [a for a in sys.argv[1:] if a in EXTENDED]
    else:
        phases_to_run = list(EXTENDED.keys())
    
    total = 0
    for pk in phases_to_run:
        added = acquire_phase(pk, target=50)
        total += added
    
    print(f"\n{'='*60}")
    print(f"EXTENDED ACQUISITION COMPLETE")
    print(f"Total new papers: {total}")
    print(f"{'='*60}")
    
    # Final inventory
    print(f"\nFinal phase counts:")
    for phase_num in range(1, 18):
        count = count_phase(phase_num)
        status = "✅" if count >= 50 else f"(need {50-count})"
        print(f"  Phase {phase_num:2d}: {count:3d} papers {status}")
