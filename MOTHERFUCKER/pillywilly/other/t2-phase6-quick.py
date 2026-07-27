#!/usr/bin/env python3
"""Quick Phase 6 (Dependent-arising) targeted search."""
import json, os, urllib.request, urllib.parse, time, xml.etree.ElementTree as ET

PROJECT = "/root/projects/blog"
WORKS_DIR = f"{PROJECT}/content/works"
ESSAYS_DIR = f"{PROJECT}/content/glossary/essays"
EMAIL = "hermes@research.local"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DELAY = 1.0

EXISTING_PMIDS = set()
for wf in __import__('glob').glob(f"{WORKS_DIR}/*.json"):
    with open(wf) as f:
        try:
            d = json.load(f)
            pm = d.get("pmid") or d.get("identifiers", {}).get("pmid", "")
            if pm: EXISTING_PMIDS.add(str(pm))
        except: pass

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Python/3.11"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    ⚠️ {e}")
        return None

def esearch(query, retmax=20):
    time.sleep(DELAY)
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "email": EMAIL})
    data = fetch_json(f"{BASE_URL}esearch.fcgi?{params}")
    return data.get("esearchresult", {}).get("idlist", []) if data else []

def efetch(pmid):
    time.sleep(DELAY)
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "rettype": "xml", "retmode": "xml", "email": EMAIL})
    try:
        req = urllib.request.Request(f"{BASE_URL}efetch.fcgi?{params}", headers={"User-Agent": "Python/3.11"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
        for article in root.findall(".//PubmedArticle"):
            title = "".join(article.find(".//ArticleTitle").itertext()) if article.find(".//ArticleTitle") is not None else ""
            parts = ["".join(at.itertext()) for at in article.findall(".//AbstractText")]
            abstract = " ".join(parts)
            ye = article.find(".//PubDate/Year") or article.find(".//PubDate/MedlineDate")
            year = ye.text[:4] if ye is not None and ye.text else ""
            journal = article.find(".//Journal/Title")
            journal = journal.text if journal is not None else ""
            doi_el = article.find(".//ArticleId[@IdType='doi']")
            doi = doi_el.text if doi_el is not None else ""
            authors = []
            for auth in article.findall(".//Author"):
                ln = auth.find("LastName")
                fn = auth.find("ForeName")
                if ln is not None:
                    authors.append(f"{ln.text or ''}, {fn.text or ''}" if fn is not None else ln.text or "")
            keywords = [kw.text for kw in article.findall(".//Keyword") if kw.text]
            return {"pmid": pmid, "title": title, "abstract": abstract, "year": year, "journal": journal, "doi": doi, "authors": authors, "keywords": keywords}
    except: pass
    return None

def score(detail):
    if not detail: return 0
    t = (detail.get("title","") or "").lower()
    a = (detail.get("abstract","") or "").lower()
    s = 0
    terms = ["predictive", "bayesian", "free energy", "active inference", "prediction error",
             "causal", "temporal", "integration", "binding", "pattern"]
    for w in terms:
        if w in t: s += 6
        if w in a: s += 2
    bridge = ["consciousness", "self", "awareness", "perception", "attention", "meditation", "mindfulness"]
    for w in bridge:
        if w in t: s += 5
        if w in a: s += 1
    return s

# Targeted Phase 6 queries - more specific than the broad ones
queries = [
    '("predictive processing" OR "free energy principle" OR "active inference") AND ("consciousness" OR "self" OR "awareness") AND 2022:2025[dp]',
    '("temporal binding" OR "temporal integration") AND ("consciousness" OR "awareness" OR "self") AND 2020:2025[dp]',
    '("Bayesian brain" OR "predictive coding") AND ("meditation" OR "mindfulness" OR "self" OR "consciousness") AND 2020:2025[dp]',
    '("causal inference" OR "causal learning") AND ("self" OR "agency" OR "body") AND ("brain" OR "neural") AND 2020:2025[dp]',
    '("patternicity" OR "apophenia" OR "meaningful coincidence" OR "synchronicity") AND ("brain" OR "neural" OR "cognition") AND 2000:2025[dp]',
]

all_pmids = []
seen = set()
for q in queries:
    print(f"Query: {q[:60]}...")
    pmids = [p for p in esearch(q) if p not in EXISTING_PMIDS and p not in seen]
    print(f"  {len(pmids)} new results")
    all_pmids.extend(pmids)
    seen.update(pmids)

all_pmids = list(dict.fromkeys(all_pmids))[:30]  # cap
print(f"\nTotal candidates: {len(all_pmids)}")

candidates = []
for pmid in all_pmids:
    detail = efetch(pmid)
    if detail and (detail.get("abstract") or "") and len((detail.get("abstract") or "")) > 50:
        s = score(detail)
        detail["bridge_score"] = s
        if s >= 15:
            candidates.append(detail)
            print(f"  Score {s:2d}: {detail['title'][:70]}")

candidates.sort(key=lambda x: x["bridge_score"], reverse=True)
print(f"\nHigh-signal: {len(candidates)}")

created = 0
for detail in candidates[:8]:
    wid = detail["title"][:70]
    wid = re.sub(r'[^a-zA-Z0-9]+', '-', wid).strip('-').lower()[:65] if 're' in dir() else detail["pmid"]
    import re
    wid = re.sub(r'[^a-zA-Z0-9]+', '-', detail["title"][:70]).strip('-').lower()[:65]
    
    wp = f"{WORKS_DIR}/t2-pubmed-{wid}.json"
    if os.path.exists(wp):
        print(f"  ⏭️ Exists: {wid}")
        continue
    
    authors = [{"name": a} for a in detail.get("authors", [])]
    work = {
        "work_id": f"work:t2-pubmed-{wid}",
        "schema_version": 2, "title": detail["title"], "authors": authors,
        "identifiers": {"pmid": detail["pmid"], "doi": detail.get("doi","")},
        "publication": {"journal": detail.get("journal",""), "year": detail.get("year","")},
        "abstract": detail.get("abstract",""),
        "phase_mapping": {"phase": 6, "phase_name": "Dependent-arising"},
        "bridge_tags": ["predictive-processing", "dependent-arising", "causality"] + [k.lower() for k in detail.get("keywords",[])[:3]],
        "evaluation": f"Quality pass v3 (score={detail['bridge_score']}) — Dependent-arising bridge.",
        "assets": {"pdf_path": None, "nxml_path": None}, "tier": 2
    }
    with open(wp, "w") as f:
        json.dump(work, f, indent=2)
    
    # Essay
    essay = {
        "id": f"bridge-pubmed-{wid}", "type": "type-b-essay",
        "title": f"Bridge Essay: {detail['title'][:80]}",
        "source_work": f"work:t2-pubmed-{wid}",
        "phase": "phase-6", "phase_name": "Dependent-arising",
        "tags": ["frontier-science", "bridge-paper", "phase-6"] + detail.get("keywords",[])[:3],
        "body": [
            {"kind": "ai", "text": "Bridge paper: Dependent-arising meets predictive processing."},
            {"kind": "ai", "text": "**Bridge rationale:** Phase 6 bridge-v3 targeted search."},
            {"kind": "summary", "text": f"**{detail['title']}** — {detail.get('journal','')} ({detail.get('year','')}). PMID: {detail['pmid']}. Score: {detail['bridge_score']}. {detail.get('abstract','')[:500]}"}
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-12. Phase 6 bridge-v3."
    }
    with open(f"{ESSAYS_DIR}/bridge-pubmed-{wid}.json", "w") as f:
        json.dump(essay, f, indent=2)
    print(f"  ✅ Created: t2-pubmed-{wid}")
    created += 1

print(f"\nCreated: {created}")
