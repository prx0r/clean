#!/usr/bin/env python3
"""Phase 12 replacement search: find 1 more high-quality ritual/neural synchrony paper."""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, os, re, glob

WORK_DIR = "/root/projects/blog"
WORKS_DIR = os.path.join(WORK_DIR, "content/works")
ESSAYS_DIR = os.path.join(WORK_DIR, "content/glossary/essays")

def fetch_ids(query, max_results=15):
    params = {'db': 'pubmed', 'term': query, 'retmax': max_results, 'retmode': 'json', 'sort': 'relevance'}
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    return data.get('esearchresult', {}).get('idlist', [])

def fetch_details(pmids):
    if not pmids: return []
    params = {'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'xml', 'rettype': 'abstract'}
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
    resp = urllib.request.urlopen(req, timeout=30)
    return parse_xml(resp.read().decode('utf-8'))

def parse_xml(xml_text):
    papers = []
    root = ET.fromstring(xml_text)
    for article_elem in root.findall('.//PubmedArticle'):
        paper = {}
        paper['pmid'] = (article_elem.find('.//PMID') or ET.Element('x')).text or ''
        medline = article_elem.find('.//MedlineCitation/Article')
        if medline is None: continue
        title_elem = medline.find('ArticleTitle')
        paper['title'] = ''.join(title_elem.itertext()) if title_elem is not None else ''
        abstract_parts = []
        for abs_elem in medline.findall('.//AbstractText'):
            abstract_parts.append(''.join(abs_elem.itertext()))
        paper['abstract'] = ' '.join(abstract_parts)
        journal_elem = medline.find('Journal/Title')
        paper['journal'] = journal_elem.text if journal_elem is not None else ''
        year_elem = medline.find('.//PubDate/Year') or medline.find('.//PubDate/MedlineDate')
        paper['year'] = year_elem.text[:4] if year_elem is not None and year_elem.text else ''
        doi_elem = article_elem.find('.//ArticleId[@IdType="doi"]') or article_elem.find('.//ArticleId')
        paper['doi'] = doi_elem.text if doi_elem is not None else ''
        authors = []
        for author_elem in medline.findall('.//Author'):
            last = author_elem.find('LastName')
            fore = author_elem.find('ForeName')
            if last is not None:
                name = f"{fore.text} {last.text}" if fore is not None and fore.text else last.text or ''
                authors.append(name)
        paper['authors'] = authors
        papers.append(paper)
    return papers

def paper_exists_by_pmid(pmid):
    for wf in glob.glob(os.path.join(WORKS_DIR, "t2-*.json")):
        with open(wf) as f:
            try:
                if json.load(f).get('identifiers', {}).get('pmid') == pmid:
                    return True
            except:
                pass
    return False

def save_work(paper):
    slug = re.sub(r'[^a-z0-9]+', '-', paper['title'].lower().strip())[:80].strip('-')
    work_id = f"t2-pubmed-{slug}"
    
    if paper_exists_by_pmid(paper.get('pmid', '')):
        print(f"  Already exists: {paper['title'][:60]}")
        return False

    work = {
        "work_id": f"work:{work_id}",
        "schema_version": 2,
        "title": paper['title'],
        "authors": [{"name": a} for a in paper.get('authors', [])],
        "publication": {
            "year": int(paper['year']) if paper.get('year') and paper['year'].isdigit() else 2026,
            "type": "article",
            "source": "PubMed/MEDLINE",
            "language": "en",
            "journal": paper.get('journal', '')
        },
        "identifiers": {"pmid": paper.get('pmid', ''), "doi": paper.get('doi', '')},
        "topics": ["phase-12-ritual", "frontier_science", "bridge_paper"],
        "tradition": ["contemporary_science"],
        "tier": 2,
        "assets": {
            "pdf_path": None,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{paper.get('pmid', '')}/",
            "abstract": paper.get('abstract', '')[:500]
        },
        "provenance": {"access_status": "open", "oa_status": "green", "source": "pubmed_t2_search", "retrieved_at": "2026-07-11"},
        "phase_mapping": {"phase": 12, "phase_name": "Ritual", "bridge_rationale": "Ritual — neural synchrony in joint action, music entrainment, collective bonding."}
    }
    with open(os.path.join(WORKS_DIR, f"{work_id}.json"), 'w') as f:
        json.dump(work, f, indent=2)
    
    essay_id = f"bridge-pubmed-{slug}"
    essay = {
        "id": essay_id,
        "title": f"Bridge Paper: {paper['title'][:80]}",
        "author": "Frontier Science / Hermes T2",
        "type": "bridge_essay",
        "source_ids": [work_id],
        "concepts": ["phase-12", "frontier-science", "bridge-paper"],
        "prerequisites": [],
        "body": [
            {"kind": "ai", "text": "This bridge paper connects the esoteric/philosophical concept of **Ritual** with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": "**Bridge thesis:** Ritual - neural synchrony in joint action, music entrainment, collective bonding."},
            {"kind": "ai", "text": "**Phase context:** neural synchrony, hyperscanning, interpersonal synchronization, brain entrainment"},
            {"kind": "summary", "text": f"Paper: {paper['title']}\nDOI: {paper.get('doi', 'N/A')}\nAbstract: {paper.get('abstract', 'N/A')[:500]}"}
        ],
        "notes": "Auto-acquired from PubMed/MEDLINE on 2026-07-11. Phase 12 (Ritual)."
    }
    with open(os.path.join(ESSAYS_DIR, f"{essay_id}.json"), 'w') as f:
        json.dump(essay, f, indent=2)
    
    print(f"  Saved: {work_id} (PMID {paper['pmid']})")
    return True

def main():
    queries = [
        '("joint action" OR "joint movement" OR "coordination") AND ("neural synchrony" OR "inter-brain" OR "hyperscanning") AND ("EEG" OR "fNIRS" OR "fMRI") AND ("social" OR "interpersonal" OR "group")',
        '("music" OR "drumming" OR "dance" OR "chanting") AND ("neural entrainment" OR "brain synchronization" OR "interpersonal synchrony") AND ("group" OR "collective" OR "social bonding")',
        '("collective ritual" OR "group ritual" OR "religious ritual") AND ("neuroscience" OR "brain" OR "EEG" OR "synchrony" OR "fMRI")',
    ]
    
    print("=== Phase 12 (Ritual) Replacement Search ===")
    candidates = []
    seen_pmids = set()
    
    for qi, query in enumerate(queries):
        print(f"\nQuery {qi+1}: {query[:80]}...")
        pmids = fetch_ids(query, max_results=12)
        print(f"  Found {len(pmids)} results")
        time.sleep(1)
        
        new_pmids = [p for p in pmids if p not in seen_pmids]
        seen_pmids.update(new_pmids)
        
        if not new_pmids:
            continue
        
        papers = fetch_details(new_pmids)
        time.sleep(1)
        
        for p in papers:
            combined = (p.get('title','') + ' ' + p.get('abstract','')).lower()
            score = sum(1 for t in ['neural synchrony', 'inter-brain', 'hyperscanning', 'joint action',
                                    'entrainment', 'interpersonal', 'music', 'drumming', 'collective',
                                    'synchronization', 'brain-to-brain', 'coordination', 'group'] if t.lower() in combined)
            year = p.get('year', '') or ''
            p['_score'] = score
        
            if score >= 2:
                print(f"  Score {score} ({year}): {p['title'][:70]}")
                candidates.append(p)
            else:
                print(f"  LOW Score {score} ({year}): {p['title'][:70]}")
    
    candidates.sort(key=lambda x: x['_score'], reverse=True)
    
    print(f"\nBest candidates: {len(candidates)}")
    saved = 0
    for p in candidates:
        if saved >= 1:  # Need just 1
            break
        if save_work(p):
            saved += 1
    
    print(f"\nSaved {saved} new Phase 12 papers")

if __name__ == "__main__":
    main()
