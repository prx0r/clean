#!/usr/bin/env python3
"""Phase 12 replacement search - pick high-quality papers."""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, os, re, glob

WORKS_DIR = "content/works"
ESSAYS_DIR = "content/glossary/essays"
os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ESSAYS_DIR, exist_ok=True)

def fetch_ids(query, n=8):
    params = {'db': 'pubmed', 'term': query, 'retmax': n, 'retmode': 'json', 'sort': 'relevance'}
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()).get('esearchresult',{}).get('idlist',[])

def fetch_details(pmids):
    if not pmids: return []
    params = {'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'xml', 'rettype': 'abstract'}
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
    resp = urllib.request.urlopen(req, timeout=30)
    return parse_xml(resp.read().decode('utf-8'))

def parse_xml(text):
    papers = []
    root = ET.fromstring(text)
    for ae in root.findall('.//PubmedArticle'):
        p = {}
        p['pmid'] = (ae.find('.//PMID') or ET.Element('x')).text or ''
        m = ae.find('.//MedlineCitation/Article')
        if m is None: continue
        te = m.find('ArticleTitle')
        p['title'] = ''.join(te.itertext()) if te is not None else ''
        abs_parts = []
        for ab in m.findall('.//AbstractText'):
            abs_parts.append(''.join(ab.itertext()))
        p['abstract'] = ' '.join(abs_parts)
        je = m.find('Journal/Title')
        p['journal'] = je.text if je is not None else ''
        ye = m.find('.//PubDate/Year') or m.find('.//PubDate/MedlineDate')
        p['year'] = ye.text[:4] if ye is not None and ye.text else ''
        de = ae.find('.//ArticleId[@IdType="doi"]')
        p['doi'] = de.text if de is not None else ''
        authors = []
        for au in m.findall('.//Author'):
            last = au.find('LastName')
            fore = au.find('ForeName')
            if last is not None:
                name = f"{fore.text} {last.text}" if fore is not None and fore.text else last.text or ''
                authors.append(name)
        p['authors'] = authors
        papers.append(p)
    return papers

def exists(pmid):
    for wf in glob.glob(f"{WORKS_DIR}/t2-*.json"):
        with open(wf) as f:
            try:
                if json.load(f).get('identifiers',{}).get('pmid') == pmid:
                    return True
            except: pass
    return False

def save(p):
    if exists(p.get('pmid','')): 
        print(f"  Already exists: {p['title'][:60]}")
        return False
    slug = re.sub(r'[^a-z0-9]+', '-', p['title'].lower().strip())[:80].strip('-')
    wid = f"t2-pubmed-{slug}"
    work = {
        "work_id": f"work:{wid}",
        "schema_version": 2,
        "title": p['title'],
        "authors": [{"name": a} for a in p.get('authors',[])],
        "publication": {"year": int(p['year']) if p.get('year') and p['year'].isdigit() else 2026,
                        "type": "article", "source": "PubMed/MEDLINE", "language": "en", "journal": p.get('journal','')},
        "identifiers": {"pmid": p.get('pmid',''), "doi": p.get('doi','')},
        "topics": ["phase-12-ritual", "frontier_science", "bridge_paper"],
        "tradition": ["contemporary_science"], "tier": 2,
        "assets": {"pdf_path": None, "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{p.get('pmid','')}/",
                   "abstract": p.get('abstract','')[:500]},
        "provenance": {"access_status": "open", "oa_status": "green", "source": "pubmed_t2_search", "retrieved_at": "2026-07-11"},
        "phase_mapping": {"phase": 12, "phase_name": "Ritual", "bridge_rationale": "Ritual - neural synchrony in joint action, music entrainment, collective bonding."}
    }
    with open(f"{WORKS_DIR}/{wid}.json", 'w') as f:
        json.dump(work, f, indent=2)
    eid = f"bridge-pubmed-{slug}"
    essay = {
        "id": eid, "title": f"Bridge Paper: {p['title'][:80]}", "author": "Frontier Science / Hermes T2",
        "type": "bridge_essay", "source_ids": [wid],
        "concepts": ["phase-12", "frontier-science", "bridge-paper"], "prerequisites": [],
        "body": [
            {"kind": "ai", "text": "This bridge paper connects Ritual with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": "**Bridge thesis:** Ritual - neural synchrony in joint action, music entrainment, collective bonding."},
            {"kind": "ai", "text": "**Phase context:** neural synchrony, hyperscanning, interpersonal synchronization"},
            {"kind": "summary", "text": f"Paper: {p['title']}\nDOI: {p.get('doi','N/A')}\nAbstract: {p.get('abstract','N/A')[:500]}"}
        ],
        "notes": "Auto-acquired 2026-07-11. Phase 12 (Ritual)."
    }
    with open(f"{ESSAYS_DIR}/{eid}.json", 'w') as f:
        json.dump(essay, f, indent=2)
    print(f"  SAVED: {p['title'][:60]} (PMID {p['pmid']})")
    return True

def main():
    queries = [
        '("interpersonal synchrony" OR "behavioral synchrony") AND ("group cohesion" OR "performance" OR "social bonding") AND ("EEG" OR "hyperscanning" OR "physiological")',
        '("synchrony" OR "synchronization") AND ("dance" OR "music") AND ("neural" OR "brain" OR "EEG" OR "fNIRS") AND ("interpersonal" OR "joint" OR "group")',
        '("gratitude" OR "cooperation") AND ("inter-brain" OR "brain-to-brain" OR "neural synchrony") AND ("EEG" OR "hyperscanning")',
        '("emotional contagion" OR "collective emotion") AND ("ritual" OR "group" OR "collective") AND ("brain" OR "neural" OR "physiological")',
    ]
    
    for qi, q in enumerate(queries):
        print(f"\nQuery {qi+1}: {q[:70]}...")
        pmids = fetch_ids(q, 6)
        print(f"  Found {len(pmids)} PMIDs")
        time.sleep(1)
        if pmids:
            papers = fetch_details(pmids)
            time.sleep(1)
            for p in papers:
                tl = p['title'].lower()
                if any(noise in tl for noise in ['meeting', 'editorial', 'conference', 'cns-20', 'tutorial']):
                    print(f"  SKIP: {p['title'][:60]}")
                    continue
                print(f"  {p['title'][:70]} ({p['year']})")
                save(p)

if __name__ == "__main__":
    main()
