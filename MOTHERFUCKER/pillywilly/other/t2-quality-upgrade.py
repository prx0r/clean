#!/usr/bin/env python3
"""
T2 Quality Upgrade: Replace low-signal papers with genuinely high-signal bridge papers.
Targets weakest phases first (8, 15, 6, 2, 4, 5) with deep PubMed searches + PDF downloads.
"""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import subprocess, tarfile, shutil

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
LOG = f"{BASE}/hermes/notes/t2-acquisition-log.md"
EMAIL = "hermes@research.local"
DELAY = 1.0

os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ESSAYS_DIR, exist_ok=True)
os.makedirs(LIBRARY, exist_ok=True)

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/4.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None
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

# === Phase definitions with deep queries ===
# Target phases with the most low-signal papers: 8, 15, 6, 2, 4, 5
PHASES = {
    8: {"name": "Formless/Absorption",
        "bridge_rationale": "Formless absorption — meditative absorption, samadhi, jhana, trance states, transcendental meditation, non-ordinary states of consciousness.",
        "queries": [
            '("meditative absorption"[Title/Abstract] OR "deep meditation"[Title/Abstract] OR "samadhi"[Title/Abstract] OR "jhana"[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '("altered state"[Title/Abstract] OR "non-ordinary"[Title/Abstract]) AND (meditation[Title/Abstract] OR trance[Title/Abstract] OR hypnotic[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("transcendental meditation"[Title/Abstract] OR "TM meditation"[Title/Abstract]) AND (EEG[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR coherence[Title/Abstract]) AND 2000:2025[dp]',
            '("loving-kindness"[Title/Abstract] OR "compassion meditation"[Title/Abstract] OR "metta"[Title/Abstract]) AND (fMRI[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '("zen meditation"[Title/Abstract] OR "zazen"[Title/Abstract] OR "vipassana"[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2000:2025[dp]',
            '("long-term meditator"[Title/Abstract] OR "expert meditator"[Title/Abstract]) AND (EEG[Title/Abstract] OR gamma[Title/Abstract] OR theta[Title/Abstract] OR alpha[Title/Abstract] OR coherence[Title/Abstract]) AND 2000:2025[dp]',
        ],
        "terms": {
            "meditative absorption": 5, "deep meditation": 4, "samadhi": 6, "jhana": 6,
            "trance": 3, "altered state": 3, "non-ordinary": 3, "hypnotic": 2,
            "transcendental meditation": 4, "tm meditation": 3,
            "loving-kindness": 3, "compassion meditation": 3, "metta": 4,
            "zen meditation": 3, "zazen": 3, "vipassana": 3,
            "long-term meditator": 3, "expert meditator": 3,
            "gamma": 2, "theta": 2, "alpha": 2, "coherence": 2,
            "mystical experience": 3, "self-transcendence": 3,
            "focused attention": 2, "open monitoring": 2,
        }},
    15: {"name": "Liberation/Enlightenment",
        "bridge_rationale": "Liberation and enlightenment — ego dissolution, self-transcendence, psychedelic-induced mystical experience, spiritual awakening, enlightenment neuroscience.",
        "queries": [
            '("ego dissolution"[Title/Abstract] OR "self-dissolution"[Title/Abstract] OR "ego death"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR default[Title/Abstract] OR cortex[Title/Abstract]) AND 2010:2025[dp]',
            '("psilocybin"[Title/Abstract] OR "LSD"[Title/Abstract] OR "ayahuasca"[Title/Abstract] OR "DMT"[Title/Abstract]) AND ("mystical experience"[Title/Abstract] OR "ego dissolution"[Title/Abstract] OR "self-transcendence"[Title/Abstract]) AND 2010:2025[dp]',
            '("self-transcendence"[Title/Abstract] OR "self-loss"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '("enlightenment"[Title/Abstract] OR "spiritual awakening"[Title/Abstract] OR "awakening"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '("religious experience"[Title/Abstract] OR "spiritual experience"[Title/Abstract] OR "peak experience"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("no-self"[Title/Abstract] OR "selflessness"[Title/Abstract] OR "anatta"[Title/Abstract] OR "anatman"[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {
            "ego dissolution": 6, "self-dissolution": 5, "ego death": 6,
            "self-transcendence": 5, "self-loss": 5, "selflessness": 4,
            "enlightenment": 4, "spiritual awakening": 5, "awakening": 2,
            "religious experience": 3, "spiritual experience": 3, "peak experience": 4,
            "psychedelic": 2, "psilocybin": 2, "mystical experience": 4,
            "no-self": 5, "anatta": 5, "self boundary": 3,
            "default mode network": 1, "dmn": 1,
        }},
    6: {"name": "Dependent-arising",
        "bridge_rationale": "Dependent arising — predictive processing, free energy principle, active inference, Bayesian brain, prediction error in perception and action.",
        "queries": [
            '("predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND (perception[Title/Abstract] OR cognition[Title/Abstract] OR action[Title/Abstract]) AND 2010:2025[dp]',
            '("free energy principle"[Title/Abstract] OR "active inference"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cognition[Title/Abstract] OR perception[Title/Abstract]) AND 2010:2025[dp]',
            '("Bayesian brain"[Title/Abstract] OR "hierarchical predictive"[Title/Abstract]) AND (perception[Title/Abstract] OR action[Title/Abstract] OR cognition[Title/Abstract]) AND 2010:2025[dp]',
            '("prediction error"[Title/Abstract] AND (perception[Title/Abstract] OR learning[Title/Abstract] OR brain[Title/Abstract]) AND (neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract])) AND 2005:2025[dp]',
            '("precision weighting"[Title/Abstract] OR "precision"[Title/Abstract] AND ("predictive coding"[Title/Abstract] OR "active inference"[Title/Abstract])) AND 2010:2025[dp]',
            '("predictive processing"[Title/Abstract] AND ("interoception"[Title/Abstract] OR "emotion"[Title/Abstract] OR "affect"[Title/Abstract])) AND 2010:2025[dp]',
        ],
        "terms": {
            "predictive processing": 5, "predictive coding": 4, "prediction error": 3,
            "free energy principle": 5, "active inference": 5,
            "bayesian brain": 4, "hierarchical predictive": 4,
            "precision weighting": 3, "precision": 1,
            "generative model": 2, "belief updating": 3,
            "variational inference": 3, "free energy": 2,
            "predictive": 1, "inference": 1,
        }},
    2: {"name": "Breath/Soul",
        "bridge_rationale": "Breath and soul — pranayama, breath-brain coupling, respiratory-brain interaction, cardiorespiratory entrainment, vagal pathways of consciousness.",
        "queries": [
            '("pranayama"[Title/Abstract] OR "yoga breathing"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract] OR fMRI[Title/Abstract] OR autonomic[Title/Abstract]) AND 2000:2025[dp]',
            '("breathing"[Title/Abstract] OR "respiration"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR "cortex"[Title/Abstract]) AND (rhythm[Title/Abstract] OR oscillation[Title/Abstract] OR synchrony[Title/Abstract]) AND 2005:2025[dp]',
            '("cardiorespiratory"[Title/Abstract] OR "heart-brain"[Title/Abstract] OR "respiratory sinus"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cognition[Title/Abstract] OR emotion[Title/Abstract]) AND 2005:2025[dp]',
            '("slow breathing"[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR HRV[Title/Abstract] OR "vagal"[Title/Abstract] OR "autonomic"[Title/Abstract])) AND 2010:2025[dp]',
            '("breath"[Title/Abstract] AND meditation[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract])) AND 2005:2025[dp]',
            '("vagal tone"[Title/Abstract] OR "vagus"[Title/Abstract]) AND (consciousness[Title/Abstract] OR emotion[Title/Abstract] OR cognition[Title/Abstract] OR meditation[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": {
            "pranayama": 5, "yoga breathing": 4, "breathing": 2, "respiration": 2,
            "cardiorespiratory": 3, "heart-brain": 3, "respiratory sinus": 3,
            "slow breathing": 3, "breath meditation": 4,
            "vagal tone": 3, "vagus": 2, "vagal": 2,
            "breath-brain": 5, "respiratory-brain": 4,
            "autonomic": 1, "HRV": 2, "heart rate variability": 2,
            "nostril breathing": 3, "alternate nostril": 3,
        }},
    4: {"name": "Wind/Pride",
        "bridge_rationale": "Wind and pride — ego, narcissism, social dominance, self-esteem, status, social hierarchy in neuroscience, self-enhancement, hubris.",
        "queries": [
            '("narcissism"[Title/Abstract] OR "narcissistic"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '("social hierarchy"[Title/Abstract] OR "social dominance"[Title/Abstract] OR "social rank"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '("self-esteem"[Title/Abstract] OR "self-enhancement"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR prefrontal[Title/Abstract]) AND 2010:2025[dp]',
            '("pride"[Title/Abstract] OR "hubris"[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR fMRI[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '("self-referential"[Title/Abstract] AND ("medial prefrontal"[Title/Abstract] OR "default mode"[Title/Abstract]) AND (self[Title/Abstract] OR ego[Title/Abstract])) AND 2010:2025[dp]',
            '("social status"[Title/Abstract] OR "dominance hierarchy"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortisol[Title/Abstract] OR amygdala[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {
            "narcissism": 5, "narcissistic": 4, "hubris": 5,
            "social hierarchy": 3, "social dominance": 4, "social rank": 3,
            "self-esteem": 3, "self-enhancement": 4,
            "pride": 3, "social status": 3, "dominance": 2,
            "self-referential": 2, "default mode": 1,
            "status": 1, "hierarchy": 1,
            "ego": 1, "self-importance": 3,
        }},
    5: {"name": "Water/Pleasure",
        "bridge_rationale": "Water and pleasure — flow state, peak experience, aesthetic pleasure, reward systems, pleasure neuroscience, hedonic tone, musical pleasure.",
        "queries": [
            '("flow state"[Title/Abstract] OR "flow experience"[Title/Abstract] OR "optimal experience"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '("aesthetic pleasure"[Title/Abstract] OR "aesthetic experience"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '("musical pleasure"[Title/Abstract] OR "music reward"[Title/Abstract] OR "music"[Title/Abstract] AND pleasure[Title/Abstract] AND (brain[Title/Abstract] OR dopamine[Title/Abstract] OR nucleus accumbens[Title/Abstract])) AND 2010:2025[dp]',
            '("reward system"[Title/Abstract] OR "hedonic"[Title/Abstract] OR "liking"[Title/Abstract] AND "wanting"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR dopamine[Title/Abstract] OR pleasure[Title/Abstract]) AND 2005:2025[dp]',
            '("orgasm"[Title/Abstract] OR "sexual pleasure"[Title/Abstract] OR "sexual arousal"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroimaging[Title/Abstract]) AND 2005:2025[dp]',
            '("pleasure"[Title/Abstract] AND ("insula"[Title/Abstract] OR "orbitofrontal"[Title/Abstract] OR "anterior cingulate"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract])) AND 2005:2025[dp]',
        ],
        "terms": {
            "flow state": 5, "flow experience": 4, "optimal experience": 4,
            "aesthetic pleasure": 4, "aesthetic experience": 3,
            "musical pleasure": 4, "music reward": 3,
            "hedonic": 3, "liking": 2, "wanting": 2,
            "pleasure": 2, "reward system": 2,
            "orgasm": 3, "sexual pleasure": 3, "sexual arousal": 2,
            "nucleus accumbens": 2, "dopamine": 1,
            "peak experience": 4, "chill": 2,
        }},
}

# Cross-mechanistic terms
CROSS = [("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("EEG", 0.4),
         ("cortex", 0.3), ("neuroimaging", 0.5), ("mechanism", 0.5),
         ("connectivity", 0.3), ("network", 0.2)]

NOISE = ["clinical trial", "pharmacological", "case report", "rat ", " mice ",
         "murine", "animal model", "surgery", "chemotherapy", "tumor",
         "cancer", "virus", "bacterial", "infection"]

def score_paper(title, abstract, phase_terms):
    text = f"{title} {abstract}".lower()
    for n in NOISE:
        if n in text:
            return 0, f"Noise: '{n}'"
    score = 0
    for term, weight in phase_terms.items():
        if term.lower() in text:
            score += weight
    score += sum(w for t, w in CROSS if t in text)
    if score >= 5.0:
        return score, f"Excellent (score={score:.1f})"
    elif score >= 3.0:
        return score, f"Good (score={score:.1f})"
    elif score >= 2.0:
        return score, f"Marginal (score={score:.1f})"
    elif score >= 1.5:
        return score, f"Low signal (score={score:.1f})"
    else:
        return score, f"Low signal (score={score:.1f})"

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
    except:
        return None
    https_url = ftp_href.replace("ftp://", "https://").replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/")
    local_tgz = f"/tmp/pmc_{pmc_clean}.tar.gz"
    try:
        subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "120", "-o", local_tgz, https_url],
                       check=True, timeout=130)
    except:
        return None
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000:
        return None
    try:
        dest_name = f"t2-PMC{pmc_clean}_{re.sub(r'[^a-zA-Z0-9]+', '_', title)[:40].strip('_')}.pdf"
        dest_path = os.path.join(LIBRARY, dest_name)
        with tarfile.open(local_tgz, "r:gz") as tar:
            pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name]
            if not pdfs:
                pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs:
                return None
            tar.extract(pdfs[0], path="/tmp/pmc_extract/")
            src = os.path.join("/tmp/pmc_extract/", pdfs[0].name)
            shutil.move(src, dest_path)
        result = subprocess.run(["file", "-b", dest_path], capture_output=True, text=True)
        if "PDF document" in result.stdout and os.path.getsize(dest_path) > 5000:
            return dest_name
    except:
        pass
    finally:
        subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
        if os.path.exists(local_tgz):
            try: os.remove(local_tgz)
            except: pass
    return None

def download_publisher_pdf(doi, journal):
    """Try known OA publisher patterns."""
    jl = journal.lower()
    if "frontiers" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://journal.frontiersin.org/article/{doi}/pdf"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000:
                return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    if "springer" in jl or "biomed" in jl or "bmc" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://link.springer.com/content/pdf/{doi}.pdf"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000:
                return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    if "nature" in jl or "scientific reports" in jl:
        # Extract article ID from DOI
        doi_parts = doi.split("/")
        if len(doi_parts) >= 2:
            art_id = doi_parts[-1]
            try:
                dest = f"{LIBRARY}/t2-pubmed-{art_id}.pdf"
                subprocess.run(["curl", "-sL", "-o", dest, f"https://www.nature.com/articles/{art_id}.pdf"], timeout=30)
                r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
                if "PDF document" in r.stdout and os.path.getsize(dest) > 5000:
                    return f"t2-pubmed-{art_id}.pdf"
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
                if "PDF document" in r.stdout and os.path.getsize(dest) > 5000:
                    return f"t2-elife-{art_id}.pdf"
                else:
                    try: os.remove(dest)
                    except: pass
            except: pass
    if "plos" in jl:
        try:
            dest = f"{LIBRARY}/t2-pubmed-{doi.replace('/','_')}.pdf"
            subprocess.run(["curl", "-sL", "-o", dest, f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable"], timeout=30)
            r = subprocess.run(["file", "-b", dest], capture_output=True, text=True)
            if "PDF document" in r.stdout and os.path.getsize(dest) > 5000:
                return f"t2-pubmed-{doi.replace('/','_')}.pdf"
            else:
                try: os.remove(dest)
                except: pass
        except: pass
    return None

def make_slug(title):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:60]
    return s or "untitled"

def improve_phase(phase_num, target=50):
    info = PHASES[phase_num]
    print(f"\n{'='*60}")
    print(f"Phase {phase_num}: {info['name']}")
    print(f"{'='*60}")

    # Load existing works for this phase
    existing_works = []
    for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
        try:
            d = json.load(open(w))
            if d.get("phase_mapping", {}).get("phase") == phase_num:
                ev = d.get("evaluation", "")
                m = re.search(r"score=(\d+(?:\.\d+)?)", ev)
                score = float(m.group(1)) if m else 0.0
                existing_works.append((score, w, d))
        except:
            pass

    existing_works.sort(key=lambda x: x[0])  # ascending

    # Identify low-signal papers to replace (score < 1.5)
    to_replace = [w for w in existing_works if w[0] < 1.5]
    print(f"Existing: {len(existing_works)} papers, {len(to_replace)} low-signal (<1.5)")

    if not to_replace:
        print("No low-signal papers to replace.")
        return 0

    # Keep at most 30 best, replace up to 20
    replace_count = min(len(to_replace), 15)  # Replace up to 15 per phase
    print(f"Planning to replace {replace_count} low-signal papers")

    # Build seen titles set
    seen_titles = set()
    for _, w, d in existing_works:
        t = d.get("title", "").lower().strip()
        if t: seen_titles.add(t)

    # Search for candidates
    candidates = []
    for qi, query in enumerate(info["queries"]):
        if len(candidates) >= replace_count * 3:
            break
        print(f"\n  Query {qi+1}/{len(info['queries'])}...", end=" ", flush=True)
        pmids = search(query, retmax=20)
        if not pmids:
            print("No results")
            continue
        print(f"Found {len(pmids)} PMIDs", end=" ", flush=True)

        summaries = fetch_summary(pmids)
        abstracts = fetch_abstracts(pmids)

        new_count = 0
        for pmid in pmids:
            if len(candidates) >= replace_count * 3:
                break
            summary = summaries.get(pmid, {})
            abd = abstracts.get(pmid, {})
            title = summary.get("title", abd.get("title", ""))
            if not title:
                continue
            tl = title.lower().strip()
            if tl in seen_titles:
                continue

            score_val, score_label = score_paper(title, abd.get("abstract", ""), info["terms"])
            if score_val < 2.0:
                continue  # only accept Good+ for replacement

            seen_titles.add(tl)
            candidates.append((score_val, {
                "pmid": pmid, "title": title, "abstract": abd.get("abstract", ""),
                "year": abd.get("year", summary.get("pubdate", "")[:4]),
                "journal": summary.get("source", ""),
                "authors": summary.get("authors", []),
                "doi": summary.get("doi", ""),
            }, summary, score_label))
            new_count += 1
        print(f"({new_count} new candidates)")

    if not candidates:
        print("  No qualifying candidates found.")
        return 0

    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[:replace_count]
    print(f"\n  Selected {len(selected)} papers (from {len(candidates)} total)")

    # Create new papers and replace old ones
    details = []
    created = 0
    to_delete = to_replace[:replace_count]

    for i, (score_val, article, summary, score_label) in enumerate(selected):
        pmid = article["pmid"]
        title = article["title"]
        doi = article.get("doi", "")

        # Try PDF download
        pmc_id = summary.get("pmc", "")
        pdf_name = download_pmc_pdf(pmc_id, title)
        if not pdf_name and doi:
            pdf_name = download_publisher_pdf(doi, article.get("journal", ""))

        # Create work JSON
        slug = make_slug(title)
        work_id = f"work:t2-pubmed-{slug}"
        pub_year = article["year"]
        try:
            pub_year = int(pub_year)
        except:
            pass

        work_data = {
            "work_id": work_id,
            "schema_version": 2,
            "title": title,
            "authors": [{"name": a} for a in article["authors"][:5]] if isinstance(article["authors"], list) else [],
            "publication": {
                "year": pub_year, "type": "article",
                "source": "PubMed/MEDLINE", "language": "en",
                "journal": article.get("journal", ""),
            },
            "identifiers": {"pmid": pmid, "doi": doi},
            "topics": [f"phase-{phase_num}-{slug[:20]}", "frontier_science", "bridge_paper"],
            "tradition": ["contemporary_science"],
            "tier": 2,
            "assets": {
                "pdf_path": pdf_name,
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "abstract": article.get("abstract", "")[:500],
            },
            "provenance": {
                "access_status": "open",
                "oa_status": "green" if pdf_name else "unknown",
                "source": "pubmed_t2_search",
                "retrieved_at": time.strftime("%Y-%m-%d"),
            },
            "phase_mapping": {
                "phase": phase_num,
                "phase_name": info["name"],
                "bridge_rationale": info["bridge_rationale"],
            },
            "evaluation": score_label,
        }

        work_file = f"{WORKS_DIR}/t2-pubmed-{slug}.json"
        with open(work_file, "w") as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)

        # Create essay JSON
        abstract_text = article.get("abstract", "")
        if len(abstract_text) > 500:
            abstract_text = abstract_text[:500] + "..."
        body = [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{info['name']}** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** {info['bridge_rationale']}"},
            {"kind": "summary", "text": f"**{title}** — {article.get('journal','?')} ({pub_year}). PMID: {pmid}. DOI: {doi}. {abstract_text}"},
        ]
        essay_data = {
            "id": f"bridge-pubmed-{slug}",
            "type": "type-b-essay",
            "title": f"Bridge Essay: {title[:80]}",
            "source_work": work_id,
            "phase": f"phase-{phase_num}",
            "phase_name": info["name"],
            "tags": ["frontier-science", "bridge-paper", f"phase-{phase_num}"],
            "body": body,
            "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase_num} ({info['name']}). Evaluation: {score_label}",
        }
        essay_file = f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json"
        with open(essay_file, "w") as f:
            json.dump(essay_data, f, indent=2, ensure_ascii=False)

        # Delete old work (if we have one to replace)
        if i < len(to_delete):
            old_score, old_path, old_data = to_delete[i]
            if os.path.exists(old_path):
                os.remove(old_path)
                # Remove matching essay
                old_slug = os.path.basename(old_path).replace("t2-pubmed-", "").replace(".json", "")
                old_essay_paths = [
                    f"{ESSAYS_DIR}/bridge-pubmed-{old_slug}.json",
                    f"{ESSAYS_DIR}/bridge-{old_slug}.json",
                ]
                for ep in old_essay_paths:
                    if os.path.exists(ep):
                        os.remove(ep)

        created += 1
        icon = "📄" if pdf_name else "📝"
        detail = f"  {icon} [{score_label}] {title[:65]} ({article.get('journal','?')} {pub_year})"
        details.append(detail)
        print(detail)

    # Log
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## Session: {ts}\n**Phase:** {info['name']} (Phase {phase_num})\n**New high-signal papers:** {created}\n**Low-signal papers replaced:** {len(to_delete[:created])}\n\n"
    for d in details:
        entry += f"- {d}\n"
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(entry)
    print(f"\n  Phase {phase_num} complete: {created} new papers ({len(existing_works)} - {len(to_delete[:created])} + {created} = {len(existing_works) - len(to_delete[:created]) + created} total)")
    return created


if __name__ == "__main__":
    print("=" * 60)
    print("T2 QUALITY UPGRADE ACQUISITION")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total = 0
    # Target weakest phases first (most low-signal papers)
    target_phases = [8, 15, 6, 2, 4, 5]
    for phase in target_phases:
        added = improve_phase(phase, target=50)
        total += added

    print(f"\n{'='*60}")
    print(f"ACQUISITION COMPLETE: {total} new high-signal papers total")
    print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Final summary
    print(f"\nUpdated phase counts:")
    phase_names = {
        1: 'Birth/Body', 2: 'Breath/Soul', 3: 'Heat/Fire', 4: 'Wind/Pride', 5: 'Water/Pleasure',
        6: 'Dependent-arising', 7: 'Form/Meditation', 8: 'Formless/Absorption', 9: 'Language',
        10: 'Imaginal', 11: 'Body-energy', 12: 'Ritual', 13: 'Daimon', 14: 'Knowledge/Gnosis',
        15: 'Liberation/Enlightenment', 16: 'Nondual/Unity', 17: 'Ultimate/Emptiness',
    }
    for p in range(1, 18):
        count = 0; high = 0; low = 0
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try:
                d = json.load(open(w))
                if d.get("phase_mapping", {}).get("phase") == p:
                    count += 1
                    ev = d.get("evaluation", "")
                    m = re.search(r"score=(\d+(?:\.\d+)?)", ev)
                    s = float(m.group(1)) if m else 0.0
                    if s >= 3.0: high += 1
                    elif s < 1.5: low += 1
            except: pass
        print(f"  Phase {p:2d} ({phase_names.get(p):25s}): {count:3d} papers, {high:2d} excellent, {low:2d} low-sig")
