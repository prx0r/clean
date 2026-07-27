#!/usr/bin/env python3
"""Fill remaining partial alternative 17-phase framework phases."""
import glob, json, os, re, sys, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET, subprocess, tarfile, shutil

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0

PARTIAL_PHASES = {
    2: {"name": "Breath/Soul", "have": 15, "want": 50,
        "queries": [
            '(pranayama[Title/Abstract] OR breathwork[Title/Abstract] OR slow breathing[Title/Abstract] OR nasal breathing[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR autonomic[Title/Abstract] OR HRV[Title/Abstract] OR vagal[Title/Abstract]) AND 2005:2025[dp]',
            '(respiration[Title/Abstract] OR respiratory[Title/Abstract] OR cardiorespiratory[Title/Abstract]) AND (meditation[Title/Abstract] OR yoga[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract]) AND 2005:2025[dp] ',
            '(breath[Title/Abstract] AND brain[Title/Abstract] AND (neural[Title/Abstract] OR oscillation[Title/Abstract] OR entrainment[Title/Abstract] OR synchronization[Title/Abstract])) AND 2010:2025[dp]',
            '(vagal tone[Title/Abstract] OR heart rate variability[Title/Abstract] AND respiration[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract]) AND 2010:2025[dp]',
            '(yoga breathing[Title/Abstract] OR nostril breathing[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract] OR autonomic[Title/Abstract]) AND 2000:2025[dp]',
        ],
        "terms": {"pranayama": 5, "breathwork": 4, "slow breathing": 4, "nasal breathing": 3,
                  "breathing": 2, "respiration": 2, "respiratory sinus": 4, "breath": 2,
                  "vagal tone": 4, "heart rate variability": 3, "HRV": 3, "breath-brain": 5,
                  "cardiorespiratory": 4, "yoga breathing": 3, "nostril breathing": 3,
                  "autonomic": 2, "meditation": 1, "heart brain": 2}},
    4: {"name": "Wind/Pride", "have": 15, "want": 50,
        "queries": [
            '(narcissism[Title/Abstract] OR narcissistic[Title/Abstract] OR grandiose[Title/Abstract] OR hubris[Title/Abstract] OR pride[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR prefrontal[Title/Abstract]) AND 2005:2025[dp]',
            '(self-enhancement[Title/Abstract] OR self-aggrandizement[Title/Abstract] OR self-esteem[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(social dominance[Title/Abstract] OR social hierarchy[Title/Abstract] OR social status[Title/Abstract] OR social rank[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR prefrontal[Title/Abstract] OR striatum[Title/Abstract]) AND 2010:2025[dp]',
            '(self-importance[Title/Abstract] OR entitlement[Title/Abstract] OR ego[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR prefrontal[Title/Abstract]) AND 2010:2025[dp]',
            '(pride[Title/Abstract] OR hubris[Title/Abstract]) AND (emotion[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR social[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"narcissism": 5, "narcissistic": 4, "grandiose": 4, "hubris": 5, "pride": 4,
                  "self-enhancement": 4, "self-aggrandizement": 5, "self-esteem": 3,
                  "social dominance": 4, "social hierarchy": 3, "social status": 3,
                  "social rank": 3, "self-importance": 4, "entitlement": 3, "ego": 2,
                  "default mode": 2, "self-referential": 2, "medial prefrontal": 2,
                  "striatum": 2, "competition": 1}},
    5: {"name": "Water/Pleasure", "have": 12, "want": 50,
        "queries": [
            '(flow state[Title/Abstract] OR flow experience[Title/Abstract] OR optimal experience[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '(pleasure[Title/Abstract] OR hedonic[Title/Abstract] OR reward[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR nucleus accumbens[Title/Abstract] OR dopamine[Title/Abstract]) AND 2005:2025[dp]',
            '(aesthetic[Title/Abstract] OR aesthetic experience[Title/Abstract] OR beauty[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroimaging[Title/Abstract]) AND 2005:2025[dp]',
            '(orgasm[Title/Abstract] OR sexual arousal[Title/Abstract] OR sexual pleasure[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroimaging[Title/Abstract]) AND 2005:2025[dp]',
            '(ecstasy[Title/Abstract] OR rapture[Title/Abstract] OR bliss[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract]) AND 2000:2025[dp]',
            '(music[Title/Abstract] AND pleasure[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR reward[Title/Abstract] OR dopamine[Title/Abstract])) AND 2010:2025[dp]',
        ],
        "terms": {"flow state": 5, "flow experience": 5, "optimal experience": 4,
                  "pleasure": 3, "hedonic": 3, "reward": 2, "nucleus accumbens": 3,
                  "dopamine": 2, "peak experience": 5, "aesthetic": 3,
                  "orgasm": 4, "sexual arousal": 3, "ecstasy": 5, "rapture": 5, "bliss": 4,
                  "intrinsic motivation": 3, "liking": 2, "wanting": 2,
                  "music": 2, "beauty": 2, "craving": 1, "desire": 1, "art": 1}},
    6: {"name": "Dependent-arising", "have": 15, "want": 50,
        "queries": [
            '(predictive coding[Title/Abstract] OR predictive processing[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR theory[Title/Abstract] OR cortex[Title/Abstract]) AND 2010:2025[dp]',
            '(free energy principle[Title/Abstract] OR active inference[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cognition[Title/Abstract] OR behavior[Title/Abstract]) AND 2010:2025[dp]',
            '(Bayesian brain[Title/Abstract] OR Bayesian inference[Title/Abstract]) AND (perception[Title/Abstract] OR cognition[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(prediction error[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract] OR learning[Title/Abstract])) AND 2010:2025[dp]',
            '(hierarchical inference[Title/Abstract] OR hierarchical predictive[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract]) AND 2010:2025[dp]',
            '(interoceptive inference[Title/Abstract] OR embodied inference[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR emotion[Title/Abstract] OR self[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": {"predictive coding": 5, "predictive processing": 4, "free energy": 4,
                  "free energy principle": 5, "active inference": 5, "Bayesian brain": 4,
                  "Bayesian inference": 3, "prediction error": 4, "hierarchical inference": 4,
                  "hierarchical predictive": 3, "interoceptive inference": 5,
                  "embodied inference": 4, "belief updating": 3,
                  "precision weighting": 3, "generative model": 3,
                  "bayesian": 2}},
    8: {"name": "Formless/Absorption", "have": 15, "want": 50,
        "queries": [
            '(meditative absorption[Title/Abstract] OR deep meditation[Title/Abstract] OR samadhi[Title/Abstract] OR jhana[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '(altered state[Title/Abstract] OR non-ordinary[Title/Abstract] OR trance[Title/Abstract]) AND (meditation[Title/Abstract] OR hypnotic[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '(gamma[Title/Abstract] OR theta[Title/Abstract] OR alpha[Title/Abstract]) AND meditation[Title/Abstract] AND (coherence[Title/Abstract] OR synchronization[Title/Abstract] OR long-term[Title/Abstract]) AND 2005:2025[dp]',
            '(loving-kindness[Title/Abstract] OR compassion meditation[Title/Abstract] OR metta[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '(transcendental meditation[Title/Abstract] OR zen meditation[Title/Abstract] OR TM meditation[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract]) AND 2000:2025[dp]',
            '(mystical experience[Title/Abstract] OR self-transcendence[Title/Abstract] OR transcendent[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"meditative absorption": 5, "deep meditation": 4, "samadhi": 6, "jhana": 6,
                  "altered state": 3, "non-ordinary": 3, "trance": 3,
                  "gamma": 2, "theta": 2, "alpha": 2, "coherence": 2,
                  "loving-kindness": 4, "compassion meditation": 4, "metta": 4,
                  "transcendental meditation": 4, "zen meditation": 4, "TM meditation": 3,
                  "mystical experience": 3, "self-transcendence": 3, "transcend": 2,
                  "long-term meditator": 2, "expert meditator": 2, "spiritual": 1}},
    9: {"name": "Language/Mantra", "have": 47, "want": 50,
        "queries": [
            '(mantra[Title/Abstract] OR mantra meditation[Title/Abstract] OR OM[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(inner speech[Title/Abstract] OR private speech[Title/Abstract] OR self-talk[Title/Abstract] OR verbal rehearsal[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract] OR frontal[Title/Abstract]) AND 2010:2025[dp]',
            '(chanting[Title/Abstract] OR verbal repetition[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"mantra": 5, "mantra meditation": 5, "OM": 3, "inner speech": 4,
                  "private speech": 4, "self-talk": 3, "verbal rehearsal": 3,
                  "chanting": 4, "verbal repetition": 4, "focused attention": 2,
                  "meditation": 1, "repetitive speech": 3, "language": 1}},
    15: {"name": "Liberation/Enlightenment", "have": 15, "want": 50,
         "queries": [
            '(enlightenment[Title/Abstract] OR awakening[Title/Abstract] OR spiritual awakening[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract] OR experience[Title/Abstract]) AND 2005:2025[dp]',
            '(ego dissolution[Title/Abstract] OR self-loss[Title/Abstract] OR selflessness[Title/Abstract] OR no-self[Title/Abstract] OR anatta[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR psychedelic[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(enlightenment[Title/Abstract] OR spiritual enlightenment[Title/Abstract]) AND (neuroscience[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '(religious experience[Title/Abstract] OR peak experience[Title/Abstract] OR mystical experience[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR neuroscience[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(self-transcendence[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract])) AND 2010:2025[dp]',
            '(nibbana[Title/Abstract] OR nirvana[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract]) AND 2000:2025[dp]',
         ],
         "terms": {"enlightenment": 4, "awakening": 3, "spiritual awakening": 5,
                   "ego dissolution": 5, "self-loss": 5, "selflessness": 4,
                   "no-self": 5, "anatta": 6, "nibbana": 6, "nirvana": 5,
                   "religious experience": 3, "peak experience": 4, "mystical experience": 4,
                   "self-transcendence": 4, "default mode network": 3, "DMN": 2,
                   "psychedelic": 2, "psilocybin": 2, "meditation": 1}},
    16: {"name": "Nondual/Unity", "have": 36, "want": 50,
         "queries": [
            '(nondual[Title/Abstract] OR non-dual[Title/Abstract] OR nondual awareness[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract] OR consciousness[Title/Abstract]) AND 2005:2025[dp]',
            '(oneness[Title/Abstract] OR unity experience[Title/Abstract] OR sense of unity[Title/Abstract] OR oceanic[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(pure awareness[Title/Abstract] OR pure consciousness[Title/Abstract] OR awareness itself[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR consciousness[Title/Abstract]) AND 2005:2025[dp]',
            '(minimal phenomenal experience[Title/Abstract] OR minimal self[Title/Abstract] OR basic self[Title/Abstract]) AND (consciousness[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(self-other[Title/Abstract] AND boundary dissolution[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract])) AND 2005:2025[dp]',
            '(ego dissolution[Title/Abstract] AND transcendence[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR default mode[Title/Abstract])) AND 2010:2025[dp]',
         ],
         "terms": {"nondual": 6, "non-dual": 6, "nondual awareness": 6,
                   "oneness": 5, "unity experience": 5, "sense of unity": 5,
                   "oceanic": 4, "pure awareness": 6, "pure consciousness": 6,
                   "awareness itself": 6, "minimal phenomenal experience": 6,
                   "minimal self": 4, "basic self": 4, "self-other": 3,
                   "boundary dissolution": 5, "ego dissolution": 4,
                   "default mode": 2, "meditation": 2, "psychedelic": 2,
                   "transcend": 2, "self-transcendence": 2}},
}

os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ESSAYS_DIR, exist_ok=True)
os.makedirs(LIBRARY, exist_ok=True)

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Alt17Fill/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if "429" in str(e): time.sleep(5)
            elif attempt < 2: time.sleep(2 * (attempt + 1))
            else: return None
    return None

def search(query, retmax=25):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query,
        "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch_summary(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
        "retmode": "json", "email": EMAIL})
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
                "title": doc.get("title", ""), "source": doc.get("source", ""),
                "pubdate": doc.get("pubdate", ""), "doi": doi, "pmc": pmc,
                "authors": [a.get("name", "") for a in doc.get("authors", [])[:5]],
            }
    except: pass
    return result

def fetch_abstracts(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
        "retmode": "xml", "rettype": "abstract", "email": EMAIL})
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

def score_text(text, phase_terms):
    tl = text.lower()
    score = 0
    for term, weight in phase_terms.items():
        if term.lower() in tl: score += weight
    mech = ["neural", "brain", "fmri", "eeg", "neuroimaging", "cortex",
            "mechanism", "network", "connectivity", "neuroscience"]
    score += sum(0.5 for t in mech if t in tl)
    return score

def make_slug(title):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:60]
    return s or "untitled"

def is_clinical_noise(title, abstract):
    t = (title + " " + abstract).lower()
    clin = ["clinical trial", "randomized controlled", "randomized clinical",
            "mouse", "rat ", "mice", "case report", "animal model",
            "pharmacological treatment"]
    return sum(1 for c in clin if c in t) >= 2

def create_work_json(pmid, article, summary, phase_num, phase_name, score):
    slug = f"pubmed-{make_slug(article['title'])}"
    if os.path.exists(f"{WORKS_DIR}/t2-{slug}.json"):
        return None
    work = {
        "work_id": f"work:t2-{slug}",
        "schema_version": 2,
        "title": article["title"],
        "authors": [{"name": a} for a in summary.get("authors", [])],
        "publication": {
            "year": int(article["year"]) if article["year"].isdigit() else 0,
            "journal": summary.get("source", ""),
            "source": "PubMed/MEDLINE",
            "language": "en"
        },
        "identifiers": {"pmid": pmid, "doi": summary.get("doi", "")},
        "topics": [f"phase-{phase_num}-{phase_name.lower().replace('/', '-')}",
                   "frontier_science", "bridge_paper"],
        "assets": {
            "pdf_path": None,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": article["abstract"][:500]
        },
        "provenance": {
            "access_status": "open", "oa_status": "green",
            "source": "pubmed_alt17_acquisition",
            "retrieved_at": time.strftime("%Y-%m-%d")
        },
        "phase_mapping": {
            "phase": phase_num, "phase_name": phase_name,
            "bridge_rationale": f"Bridge paper score={score:.1f}: links {phase_name} concept to mechanistic neuroscience"
        },
        "evaluation": f"Score {int(score)}: {'Excellent' if score >= 10 else 'Good' if score >= 6 else 'Marginal' if score >= 4 else 'Low'} bridge signal"
    }
    fpath = f"{WORKS_DIR}/t2-{slug}.json"
    with open(fpath, "w") as f:
        json.dump(work, f, indent=2)
    
    essay = {
        "id": f"bridge-{slug}",
        "type": "type-b-essay",
        "title": f"Bridge Essay: {article['title'][:80]}",
        "source_work": f"work:t2-{slug}",
        "phase": f"phase-{phase_num}",
        "phase_name": phase_name,
        "tags": ["frontier-science", "bridge-paper", f"phase-{phase_num}"],
        "body": [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{phase_name}** (Phase {phase_num}) with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** Links {phase_name} to mechanistic neuroscience."},
            {"kind": "summary", "text": f"**{article['title']}** — {summary.get('source','')} ({article['year']}). PMID: {pmid}. DOI: {summary.get('doi','')}. {article['abstract'][:500]}"}
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase_num} ({phase_name})."
    }
    with open(f"{ESSAYS_DIR}/bridge-{slug}.json", "w") as f:
        json.dump(essay, f, indent=2)
    
    return fpath

def download_pdf(pmc, doi, title):
    if not pmc and not doi: return None
    pmc_num = pmc.replace("PMC", "").strip() if pmc else ""
    time.sleep(DELAY)
    # Publisher direct patterns
    if doi:
        dc = doi.replace("doi:", "").strip()
        for pattern, url_tmpl in [
            ("frontiers", f"https://journal.frontiersin.org/article/{dc}/pdf"),
            ("10.1007", f"https://link.springer.com/content/pdf/{dc}.pdf"),
            ("10.1186", f"https://link.springer.com/content/pdf/{dc}.pdf"),
            ("10.1371", f"https://journals.plos.org/plosone/article/file?id={dc}&type=printable"),
            ("10.7554", f"https://cdn.elifesciences.org/articles/{dc.split('.')[-1]}/elife-{dc.split('.')[-1]}-v1.pdf"),
            ("10.1038", f"https://www.nature.com/articles/{dc.split('/')[-1]}.pdf"),
        ]:
            if pattern in dc:
                dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
                try:
                    subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", dest, url_tmpl], timeout=20)
                    if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                        return os.path.basename(dest)
                except: pass
    # OA FTP
    if pmc_num:
        oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_num}"
        time.sleep(DELAY)
        try:
            with urllib.request.urlopen(oa_url, timeout=20) as resp:
                oa_xml = resp.read().decode("utf-8")
            oa_root = ET.fromstring(oa_xml)
            record = oa_root.find(".//record")
            if record is not None:
                for link in record.findall("link"):
                    if link.get("format") == "tgz":
                        ftp_href = link.get("href", "")
                        https_url = ftp_href.replace("ftp://", "https://")
                        dest_tgz = f"/tmp/pmc_{pmc_num}.tar.gz"
                        try:
                            subprocess.run(["curl", "-sL", "-o", dest_tgz, https_url], timeout=60)
                            if os.path.exists(dest_tgz) and os.path.getsize(dest_tgz) > 1000:
                                with tarfile.open(dest_tgz, "r:gz") as tar:
                                    pdf_members = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "Suppl" not in m.name]
                                    if pdf_members:
                                        pdf_fn = f"t2-{pmc_num}-{make_slug(title)}.pdf"
                                        pdf_dest = os.path.join(LIBRARY, pdf_fn)
                                        tar.extract(pdf_members[0], path="/tmp/pmc_extract/")
                                        src = f"/tmp/pmc_extract/{pdf_members[0].name}"
                                        if os.path.exists(src):
                                            shutil.move(src, pdf_dest)
                                            subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
                                            if os.path.exists(pdf_dest) and os.path.getsize(pdf_dest) > 5000:
                                                return pdf_fn
                                subprocess.run(["rm", "-f", dest_tgz])
                        except: pass
        except: pass
    return None

def acquire_phase(phase_num, config):
    name = config["name"]
    have = config["have"]
    want = config["want"]
    need = want - have
    if need <= 0: return 0
    
    print(f"\n{'='*60}")
    print(f"Phase {phase_num}: {name} — have {have}, need {need}")
    print(f"{'='*60}")
    
    seen_titles = set()
    candidates = []
    
    for qi, query in enumerate(config["queries"]):
        if len(candidates) >= need * 2:
            break
        print(f"Query {qi+1}/{len(config['queries'])}: {query[:70]}...")
        pmids = search(query)
        if not pmids: continue
        print(f"  Found {len(pmids)} PMIDs")
        
        summaries = fetch_summary(pmids)
        abstracts = fetch_abstracts(pmids)
        
        for pmid in pmids:
            if pmid not in abstracts or pmid not in summaries: continue
            article = abstracts[pmid]
            summary = summaries[pmid]
            title = article.get("title", "")
            abstract = article.get("abstract", "")
            year = article.get("year", "")
            
            if is_clinical_noise(title, abstract): continue
            if year.isdigit() and int(year) < 2000: continue
            if year.isdigit() and int(year) < 2015:
                if score_text(title + " " + abstract, config["terms"]) < 8: continue
            
            title_key = title.lower().strip()[:80]
            if title_key in seen_titles: continue
            seen_titles.add(title_key)
            
            score = score_text(title + " " + abstract, config["terms"])
            if score >= 4:
                candidates.append((score, pmid, article, summary))
        
        time.sleep(DELAY)
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    created = 0
    for score, pmid, article, summary in candidates:
        if created >= need: break
        result = create_work_json(pmid, article, summary, phase_num, name, score)
        if result:
            created += 1
            print(f"  ✓ [{int(score)}pts] {article['title'][:60]}...")
            pmc = summary.get("pmc", "")
            doi = summary.get("doi", "")
            pdf = download_pdf(pmc, doi, article["title"])
            if pdf:
                try:
                    with open(result) as f: wd = json.load(f)
                    wd["assets"]["pdf_path"] = pdf
                    with open(result, "w") as f: json.dump(wd, f, indent=2)
                except: pass
                print(f"       PDF: {pdf}")
    
    print(f"Created {created} new papers for Phase {phase_num} ({name})")
    return created

# Main
print("=" * 60)
print("PARTIAL PHASE FILL — ALTERNATIVE 17-PHASE FRAMEWORK")
print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

total_created = 0
for pn in sorted(PARTIAL_PHASES.keys()):
    cfg = PARTIAL_PHASES[pn]
    n = acquire_phase(pn, cfg)
    if n: total_created += n

print(f"\n{'='*60}")
print(f"FILL COMPLETE. Total new papers: {total_created}")
print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")
