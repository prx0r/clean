#!/usr/bin/env python3
"""Diagnose why standard queries find no new candidates for hard phases.
Searches PubMed, prints titles + bridge scores, without the seen_titles filter."""
import glob, json, os, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET

BASE = "/root/projects/blog"
DELAY = 1.0
EMAIL = "hermes@research.local"

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

def search_pubmed(query, retmax=15):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    if not data: return []
    try:
        d = json.loads(data)
        return d.get("esearchresult", {}).get("idlist", [])
    except: return []

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
            articles[pmid] = {"title": title, "abstract": abstract}
    except: pass
    return articles

# Phase-specific scoring terms (same as v2 script)
PHASE_SCORING = {
    3: [("embodied cognition", 1.5), ("grounded cognition", 1.2), ("enactive", 1.5),
        ("extended mind", 1.5), ("situated cognition", 1.2), ("sensorimotor", 0.8),
        ("4e cognition", 1.5), ("predictive processing", 0.6), ("active inference", 0.6),
        ("computationalism", 1.0), ("radical embodiment", 1.5), ("ecological", 0.5),
        ("affordance", 0.8), ("dynamical", 0.5), ("autopoiesis", 1.2)],
    7: [("ego dissolution", 1.5), ("self-loss", 1.5), ("self-transcendence", 1.2),
        ("default mode", 0.8), ("nondual", 1.5), ("non-dual", 1.5),
        ("depersonalization", 0.8), ("derealization", 0.6), ("self-boundary", 1.0),
        ("self-referential", 0.5), ("meditation", 0.5), ("psychedelic", 0.5),
        ("mindfulness", 0.3), ("sense of self", 0.6), ("self-awareness", 0.5)],
    9: [("mantra", 1.5), ("mantra meditation", 1.8), ("inner speech", 1.5),
        ("inner voice", 1.2), ("self-talk", 1.0), ("private speech", 0.8),
        ("focused attention", 0.8), ("verbal repetition", 1.0), ("prayer", 0.8),
        ("transcendental meditation", 1.2), ("chanting", 1.2), ("repetitive", 0.3)],
    17: [("second-person", 1.5), ("intersubjectivity", 1.5), ("embodied empathy", 1.5),
        ("shared intentionality", 1.2), ("social cognition", 0.6), ("empathy", 0.5),
        ("mirror neuron", 0.8), ("interoception", 0.5), ("social brain", 0.4),
        ("social touch", 1.0), ("affective touch", 1.0), ("social interaction", 0.3)],
    16: [("self-transcendence", 1.5), ("transcendence", 1.2), ("mystical experience", 1.5),
        ("mystical", 0.8), ("numinous", 1.5), ("awe", 0.8),
        ("cosmic consciousness", 1.8), ("oceanic", 1.0), ("unity consciousness", 1.2),
        ("transcendent", 0.8), ("spiritual", 0.3), ("sacred", 0.5)],
}
CROSS = [("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("neuroimaging", 0.5), ("cortex", 0.3), ("EEG", 0.4), ("mechanism", 0.5)]

def score_text(title, abstract, phase):
    text = f"{title} {abstract}".lower()
    score = sum(w for t, w in PHASE_SCORING.get(phase, []) if t in text)
    score += sum(w for t, w in CROSS if t in text)
    return score

# Load existing titles
seen = set()
for w in glob.glob(f"{BASE}/content/works/t2-*.json"):
    try:
        d = json.load(open(w))
        seen.add(d.get("title", "").lower().strip())
    except: pass

# Broader queries for each phase (no loattrfree filter, broader date range)
BROAD_QUERIES = {
    3: [
        '("embodied cognition"[Title/Abstract] OR "grounded cognition"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2005:2025[dp]',
        '("enactive"[Title/Abstract] OR "extended mind"[Title/Abstract]) AND ("cognition"[Title/Abstract] OR "perception"[Title/Abstract]) AND 2005:2025[dp]',
        '("affordance"[Title/Abstract] AND "cognition"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
        '("ecological"[Title/Abstract] AND "perception"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "action"[Title/Abstract])) AND 2010:2025[dp]',
    ],
    7: [
        '("nondual"[Title/Abstract] OR "non-dual"[Title/Abstract] OR "nondual awareness"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "brain"[Title/Abstract] OR "neuroscience"[Title/Abstract]) AND 2000:2025[dp]',
        '("ego dissolution"[Title/Abstract] OR "self-loss"[Title/Abstract] OR "self-boundary"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
        '("default mode"[Title/Abstract] AND "self"[Title/Abstract] AND ("dissolution"[Title/Abstract] OR "transcendence"[Title/Abstract] OR "meditation"[Title/Abstract])) AND 2010:2025[dp]',
        '("depersonalization"[Title/Abstract] OR "derealization"[Title/Abstract]) AND ("self-referential"[Title/Abstract] OR "self-processing"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
    ],
    9: [
        '("mantra"[Title/Abstract] OR "mantra meditation"[Title/Abstract]) AND ("EEG"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2000:2025[dp]',
        '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract] OR "self-talk"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
        '("focused attention"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("neural"[Title/Abstract] OR "EEG"[Title/Abstract] OR "fMRI"[Title/Abstract])) AND 2005:2025[dp]',
        '("transcendental meditation"[Title/Abstract] OR "TM meditation"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2000:2025[dp]',
    ],
    16: [
        '("self-transcendence"[Title/Abstract] OR "transcendence"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "neuroimaging"[Title/Abstract]) AND 2005:2025[dp]',
        '("awe"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "experience"[Title/Abstract])) AND 2010:2025[dp]',
        '("mystical experience"[Title/Abstract] OR "mystical"[Title/Abstract] OR "numinous"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "meditation"[Title/Abstract] OR "psychedelic"[Title/Abstract]) AND 2000:2025[dp]',
        '("spiritual experience"[Title/Abstract] OR "peak experience"[Title/Abstract] OR "oceanic"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
    ],
    17: [
        '("second-person"[Title/Abstract] OR "intersubjectivity"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
        '("embodied empathy"[Title/Abstract] OR "social touch"[Title/Abstract] OR "affective touch"[Title/Abstract]) AND ("insula"[Title/Abstract] OR "brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        '("shared intentionality"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2005:2025[dp]',
        '("social cognition"[Title/Abstract] AND "predictive processing"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
        '("mirror neuron"[Title/Abstract] AND "empathy"[Title/Abstract] AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract] OR "insula"[Title/Abstract])) AND 2005:2025[dp]',
    ],
}

for phase in [3, 7, 9, 16, 17]:
    print(f"\n{'='*60}")
    print(f"Phase {phase} — Diagnostic Search")
    print(f"{'='*60}")
    
    existing_in_phase = 0
    for w in glob.glob(f"{BASE}/content/works/t2-*.json"):
        try:
            d = json.load(open(w))
            pm = d.get("phase_mapping", {})
            if pm and pm.get("phase") == phase:
                existing_in_phase += 1
        except: pass
    print(f"Existing: {existing_in_phase}")
    
    total_new = 0
    above_2 = 0
    
    for qi, query in enumerate(BROAD_QUERIES.get(phase, [])):
        print(f"\n  Query {qi+1}/{len(BROAD_QUERIES.get(phase, []))}: {query[:80]}...")
        pmids = search_pubmed(query, retmax=15)
        if not pmids:
            print(f"    No results")
            continue
        print(f"    Found {len(pmids)} PMIDs")
        
        abstracts = fetch_abstracts(pmids)
        
        for pmid in pmids:
            ad = abstracts.get(pmid, {})
            title = ad.get("title", "")
            if not title:
                continue
            title_lower = title.lower().strip()
            is_new = title_lower not in seen
            
            abstract = ad.get("abstract", "")
            score = score_text(title, abstract, phase)
            
            icon = "🆕" if is_new else "📌"
            score_label = "🔴 LOW" if score < 1.5 else "🟡 MARGINAL" if score < 2.0 else "🟢 GOOD+"
            
            if is_new:
                total_new += 1
                if score >= 2.0:
                    above_2 += 1
                    print(f"    {icon} [{score_label}] score={score:.1f} — {title[:80]}")
                elif score >= 1.5:
                    print(f"    {icon} [{score_label}] score={score:.1f} — {title[:70]}")
                # Skip printing low-score new papers to keep output manageable
    
    print(f"\n  Summary: {total_new} new papers, {above_2} with score >= 2.0")

print(f"\n{'='*60}")
print("DIAGNOSTIC COMPLETE")
