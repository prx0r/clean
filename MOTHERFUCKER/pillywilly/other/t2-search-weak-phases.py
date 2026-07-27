#!/usr/bin/env python3
"""
Deep targeted PubMed/MEDLINE search for weak phases.
Phase 7 (Emptiness), Phase 8 (Non-fabrication), Phase 12 (Ritual), Phase 17 (Social Incarnation)
Uses PubMed E-utilities with proper rate limiting.
"""
import json, time, urllib.request, urllib.parse, urllib.error, os, sys, re, glob, xml.etree.ElementTree as ET

WORK_DIR = "/root/projects/blog"
WORKS_DIR = os.path.join(WORK_DIR, "content/works")
ESSAYS_DIR = os.path.join(WORK_DIR, "content/glossary/essays")
FRONTIER_DIR = os.path.join(WORK_DIR, "library/frontier")
os.makedirs(FRONTIER_DIR, exist_ok=True)

# Bridge search configurations per phase
PHASE_SEARCHES = {
    7: {  # Emptiness
        "name": "Emptiness",
        "queries": [
            "((\"ego dissolution\" OR \"self-transcendence\" OR \"self-loss\") AND (\"default mode network\" OR \"posterior cingulate\" OR \"medial prefrontal\")) AND (\"neuroscience\" OR \"brain\" OR \"fMRI\" OR \"neural\")",
            "((\"depersonalization\" OR \"derealization\") AND (\"neuroscience\" OR \"neural correlates\" OR \"brain\") AND (\"self\" OR \"self-processing\"))",
            "((\"mindfulness\" OR \"meditation\") AND (\"self\" OR \"self-awareness\" OR \"self-referential\") AND (\"default mode network\" OR \"DMN\" OR \"neural\") AND (\"dissolution\" OR \"loss\" OR \"transcend\"))",
            "((\"self\" AND \"no-self\" OR \"anatta\" OR \"non-self\") AND (\"brain\" OR \"neuroscience\" OR \"default mode\"))",
            "((\"minimal self\" OR \"minimal phenomenal self\") AND (\"neuroscience\" OR \"brain\" OR \"fMRI\" OR \"predictive processing\"))",
        ],
        "bridge_terms": ["ego dissolution", "self-loss", "self-transcendence", "depersonalization", "default mode network"],
        "bridge_rationale": "Emptiness — dissolution of self, ego, DMN decoupling, non-self in neuroscience."
    },
    8: {  # Non-fabrication
        "name": "Non-fabrication",
        "queries": [
            "((\"spontaneous thought\" OR \"mind-wandering\" OR \"involuntary thought\") AND (\"default mode network\" OR \"creative cognition\" OR \"incubation\" OR \"insight\"))",
            "((\"daydreaming\" OR \"fantasy proneness\" OR \"absorption\") AND (\"brain\" OR \"neural correlates\" OR \"fMRI\" OR \"EEG\"))",
            "((\"spontaneous cognition\" OR \"task-unrelated thought\") AND (\"creativity\" OR \"divergent thinking\" OR \"insight problem solving\"))",
            "((\"default network\" OR \"DMN\") AND (\"creative cognition\" OR \"divergent thinking\" OR \"imagination\") AND (\"brain\" OR \"neural\"))",
        ],
        "bridge_terms": ["spontaneous thought", "mind-wandering", "creative cognition", "default mode network"],
        "bridge_rationale": "Non-fabrication — spontaneous thought, DMN, creative insight, mind-wandering."
    },
    12: {  # Ritual
        "name": "Ritual",
        "queries": [
            "((\"neural synchrony\" OR \"brain-to-brain\" OR \"interpersonal neural synchronization\" OR \"hyperscanning\") AND (\"joint\" OR \"social\" OR \"interpersonal\" OR \"collective\"))",
            "((\"music\" OR \"rhythm\" OR \"drumming\" OR \"chanting\") AND (\"brain entrainment\" OR \"neural entrainment\" OR \"synchronization\" OR \"EEG\" OR \"fMRI\") AND (\"group\" OR \"collective\" OR \"social bonding\"))",
            "((\"collective effervescence\" OR \"collective emotion\" OR \"shared emotion\") AND (\"neuroscience\" OR \"brain\" OR \"physiological synchrony\"))",
            "((\"group cohesion\" OR \"social bonding\" OR \"interpersonal synchrony\") AND (\"oxytocin\" OR \"endorphin\" OR \"neurochemistry\" OR \"brain\"))",
            "((\"ritual\" AND \"neuroscience\") OR (\"prayer\" AND \"brain\" AND \"fMRI\") OR (\"liturgical\" AND \"neural\"))",
        ],
        "bridge_terms": ["neural synchrony", "hyperscanning", "interpersonal synchronization", "brain entrainment"],
        "bridge_rationale": "Ritual — neural synchrony in joint action, music entrainment, collective bonding."
    },
    17: {  # Social Incarnation
        "name": "Social Incarnation",
        "queries": [
            "((\"intersubjectivity\" OR \"interpersonal understanding\" OR \"shared intentionality\") AND (\"brain\" OR \"neuroscience\" OR \"neural\" OR \"fMRI\" OR \"predictive processing\"))",
            "((\"empathy\" OR \"compassion\") AND (\"embodied\" OR \"interoception\" OR \"mirror neuron\" OR \"simulation\") AND (\"brain\" OR \"neural\"))",
            "((\"theory of mind\" OR \"mentalizing\" OR \"social cognition\") AND (\"predictive processing\" OR \"active inference\" OR \"enactive\") AND (\"brain\" OR \"neural\"))",
            "((\"social touch\" OR \"interpersonal\") AND (\"embodied cognition\" OR \"body\" OR \"interoception\") AND (\"brain\" OR \"neural\"))",
        ],
        "bridge_terms": ["intersubjectivity", "embodied empathy", "predictive processing social cognition", "shared intentionality"],
        "bridge_rationale": "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing."
    }
}

# Scoring function for bridge relevance
def score_paper(paper_data, phase_searches):
    """Score a paper for bridge relevance based on title/abstract keywords."""
    title = (paper_data.get('title', '') or '').lower()
    abstract = (paper_data.get('abstract', '') or '').lower()
    combined = title + ' ' + abstract
    
    score = 0
    
    # Phase-specific bridge terms
    for phase, config in phase_searches.items():
        for term in config.get('bridge_terms', []):
            if term.lower() in combined:
                score += 2
    
    # General bridge-signal terms
    high_signal = ['bridge', 'link', 'connection between', 'implications for', 'mechanism', 
                   'neural basis', 'neural correlates', 'neural mechanism', 'brain mechanism']
    for term in high_signal:
        if term.lower() in combined:
            score += 1
    
    # Penalty for clinical/engineering noise
    noise_terms = ['clinical trial', 'randomized controlled', 'treatment efficacy', 'drug',
                   'segmentation', 'classification', 'algorithm', 'deep learning model',
                   'convolutional', 'tumor', 'lesion', 'pathology', 'diagnosis']
    for term in noise_terms:
        if term.lower() in combined:
            score -= 3
    
    return max(0, score)


def fetch_pubmed_ids(query, max_results=30, retstart=0):
    """Search PubMed and return PMID list."""
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retstart': retstart,
        'retmode': 'json',
        'sort': 'relevance'
    }
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        ids = data.get('esearchresult', {}).get('idlist', [])
        total = data.get('esearchresult', {}).get('count', '0')
        return ids, int(total)
    except Exception as e:
        print(f"  Error searching: {e}")
        return [], 0


def fetch_pubmed_details(pmids):
    """Fetch article details from PubMed."""
    if not pmids:
        return []
    
    params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml',
        'rettype': 'abstract'
    }
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        xml_data = resp.read().decode('utf-8')
        return parse_pubmed_xml(xml_data)
    except Exception as e:
        print(f"  Error fetching details: {e}")
        return []


def parse_pubmed_xml(xml_text):
    """Parse PubMed XML response into structured paper data."""
    papers = []
    
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  XML parse error: {e}")
        return papers
    
    for article_elem in root.findall('.//PubmedArticle'):
        paper = {}
        
        # PMID
        pmid_elem = article_elem.find('.//PMID')
        paper['pmid'] = pmid_elem.text if pmid_elem is not None else ''
        
        # Article metadata
        medline = article_elem.find('.//MedlineCitation/Article')
        if medline is None:
            continue
        
        # Title
        title_elem = medline.find('ArticleTitle')
        paper['title'] = ''.join(title_elem.itertext()) if title_elem is not None else ''
        
        # Abstract
        abstract_parts = []
        for abs_elem in medline.findall('.//AbstractText'):
            label = abs_elem.get('Label', '')
            text = ''.join(abs_elem.itertext())
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        paper['abstract'] = ' '.join(abstract_parts)
        
        # Journal
        journal_elem = medline.find('Journal/Title')
        paper['journal'] = journal_elem.text if journal_elem is not None else ''
        
        # Year
        year_elem = medline.find('.//PubDate/Year')
        if year_elem is None:
            year_elem = medline.find('.//PubDate/MedlineDate')
        paper['year'] = year_elem.text[:4] if year_elem is not None and year_elem.text else ''
        
        # DOI
        doi_elem = article_elem.find('.//ArticleId[@IdType="doi"]')
        if doi_elem is None:
            for aid in article_elem.findall('.//ArticleId'):
                if aid.get('IdType') == 'doi':
                    doi_elem = aid
                    break
        paper['doi'] = doi_elem.text if doi_elem is not None else ''
        
        # Authors
        authors = []
        for author_elem in medline.findall('.//Author'):
            last = author_elem.find('LastName')
            fore = author_elem.find('ForeName')
            if last is not None:
                name = last.text or ''
                if fore is not None:
                    name = f"{fore.text} {name}" if fore.text else name
                authors.append(name)
        paper['authors'] = authors
        
        papers.append(paper)
    
    return papers


def paper_exists(pmids, phase):
    """Check if paper already acquired for this or any phase."""
    existing = set()
    for wf in glob.glob(os.path.join(WORKS_DIR, "t2-*.json")):
        with open(wf) as f:
            try:
                data = json.load(f)
                pmid = data.get('identifiers', {}).get('pmid', '')
                if pmid:
                    existing.add(pmid)
            except:
                pass
    return any(p in existing for p in pmids)


def make_work_id(title):
    """Create a file-safe work ID from title."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:80].strip('-')
    return f"t2-pubmed-{slug}"


def make_essay_id(work_id):
    return f"bridge-{work_id.replace('t2-', '')}"


def save_work_json(paper, phase, config):
    """Save work JSON and essay JSON for a paper."""
    work_id = make_work_id(paper['title'])
    essay_id = make_essay_id(work_id)
    slug = re.sub(r'[^a-z0-9]+', '-', paper['title'].lower().strip())[:60].strip('-')
    
    # Work JSON
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
        "identifiers": {
            "pmid": paper.get('pmid', ''),
            "doi": paper.get('doi', '')
        },
        "topics": [f"phase-{phase}-{config['name'].lower().replace(' ', '-')}"],
        "tradition": ["contemporary_science"],
        "tier": 2,
        "assets": {
            "pdf_path": None,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{paper.get('pmid', '')}/"
        },
        "provenance": {
            "access_status": "open",
            "oa_status": "green",
            "source": "pubmed_t2_search",
            "retrieved_at": "2026-07-11"
        },
        "phase_mapping": {
            "phase": phase,
            "phase_name": config['name'],
            "bridge_rationale": config['bridge_rationale']
        }
    }
    
    # Add abstract if present
    if paper.get('abstract'):
        work['assets']['abstract'] = paper['abstract'][:500]
    
    work_path = os.path.join(WORKS_DIR, f"{work_id}.json")
    with open(work_path, 'w') as f:
        json.dump(work, f, indent=2, ensure_ascii=False)
    
    # Essay JSON
    essay = {
        "id": essay_id,
        "title": f"Bridge Paper: {paper['title'][:80]}",
        "author": "Frontier Science / Hermes T2",
        "type": "bridge_essay",
        "source_ids": [work_id],
        "concepts": [f"phase-{phase}", "frontier-science", "bridge-paper"],
        "prerequisites": [],
        "body": [
            {
                "kind": "ai",
                "text": f"This bridge paper connects the esoteric/philosophical concept of **{config['name']}** with mechanistic science from PubMed/MEDLINE."
            },
            {
                "kind": "ai",
                "text": f"**Bridge thesis:** {config['bridge_rationale']}"
            },
            {
                "kind": "ai",
                "text": f"**Phase context:** {', '.join(config['bridge_terms'])}"
            },
            {
                "kind": "summary",
                "text": f"Paper: {paper['title']}\nDOI: {paper.get('doi', 'N/A')}\nAbstract: {paper.get('abstract', 'N/A')[:500]}"
            }
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on 2026-07-11. Phase {phase} ({config['name']})."
    }
    
    essay_path = os.path.join(ESSAYS_DIR, f"{essay_id}.json")
    with open(essay_path, 'w') as f:
        json.dump(essay, f, indent=2, ensure_ascii=False)
    
    return work_id, essay_id


def main():
    results = {}
    
    for phase in [7, 8, 12, 17]:
        config = PHASE_SEARCHES[phase]
        print(f"\n{'='*60}")
        print(f"Phase {phase}: {config['name']}")
        print(f"{'='*60}")
        
        phase_papers = []
        seen_pmids = set()
        
        for qi, query in enumerate(config['queries']):
            print(f"\n  Query {qi+1}: {query[:80]}...")
            
            # Search PubMed
            pmids, total = fetch_pubmed_ids(query, max_results=20)
            print(f"  Found {len(pmids)} results (total: {total})")
            time.sleep(1)
            
            if not pmids:
                continue
            
            # Check which are new
            new_pmids = [p for p in pmids if p not in seen_pmids]
            if not new_pmids:
                print(f"  All already seen, skipping")
                continue
            
            seen_pmids.update(new_pmids)
            
            # Fetch details
            papers = fetch_pubmed_details(new_pmids[:10])  # Limit to 10 per query
            time.sleep(1)
            
            # Score and filter
            for p in papers:
                bridge_score = score_paper(p, PHASE_SEARCHES)
                p['bridge_score'] = bridge_score
                
                # Only keep high-signal papers (score >= 3)
                if bridge_score >= 3:
                    phase_papers.append(p)
                    print(f"  ✅ Score {bridge_score}: {p['title'][:70]}")
                else:
                    print(f"  ⬜ Score {bridge_score}: {p['title'][:70]} (low signal)")
        
        # Sort by score
        phase_papers.sort(key=lambda x: x['bridge_score'], reverse=True)
        
        # Take top papers (up to 5 more needed per phase)
        needed = 5 - len([w for w in glob.glob(os.path.join(WORKS_DIR, "t2-*.json")) 
                         if json.load(open(w)).get('phase_mapping', {}).get('phase') == phase])
        
        if needed <= 0:
            print(f"\n  Phase already has enough papers, skipping new acquisition")
            results[phase] = {"new": 0, "needed": 0}
            continue
        
        selected = phase_papers[:needed]
        print(f"\n  Selecting top {len(selected)} of {len(phase_papers)} candidates")
        
        # Save each paper
        new_count = 0
        for paper in selected:
            # Double check not already saved
            if paper_exists([paper.get('pmid', '')], phase):
                print(f"  ⏭️ Already exists: {paper['title'][:60]}")
                continue
            
            wid, eid = save_work_json(paper, phase, config)
            print(f"  📝 Saved: {wid}")
            new_count += 1
        
        results[phase] = {"new": new_count, "needed": needed}
    
    # Summary
    print(f"\n{'='*60}")
    print("ACQUISITION SUMMARY")
    print(f"{'='*60}")
    for phase in [7, 8, 12, 17]:
        r = results.get(phase, {"new": 0})
        config = PHASE_SEARCHES[phase]
        print(f"Phase {phase} ({config['name']}): +{r['new']} new papers")
    
    print(f"\nDone!")

if __name__ == "__main__":
    main()
