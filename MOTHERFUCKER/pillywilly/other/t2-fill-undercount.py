#!/usr/bin/env python3
"""Quick fill for under-count phases (2, 9, 11)"""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET, subprocess, tarfile, shutil

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0

def api(url):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HF"}), timeout=20) as r:
                return r.read().decode("utf-8")
        except:
            if a<2: time.sleep(2*(a+1))
            else: return None
    return None

def search(q, n=15):
    p = urllib.parse.urlencode({"db":"pubmed","term":q,"retmax":n,"retmode":"json","sort":"relevance","email":EMAIL})
    time.sleep(DELAY)
    d = api(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{p}")
    return json.loads(d).get("esearchresult",{}).get("idlist",[]) if d else []

def fetch_summary(p):
    if not p: return {}
    p2 = urllib.parse.urlencode({"db":"pubmed","id":",".join(p),"retmode":"json","email":EMAIL})
    time.sleep(DELAY)
    d = api(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{p2}")
    if not d: return {}
    r = {}
    try:
        j = json.loads(d)
        for u, doc in j.get("result",{}).items():
            if u=="uids": continue
            doi=pmc=""
            for a in doc.get("articleids",[]):
                if a.get("idtype")=="doi": doi=a.get("value","")
                if a.get("idtype")=="pmc": pmc=a.get("value","")
            r[u]={"title":doc.get("title",""),"source":doc.get("source",""),"pubdate":doc.get("pubdate",""),"doi":doi,"pmc":pmc,"authors":[a.get("name","") for a in doc.get("authors",[])[:5]]}
    except: pass
    return r

def fetch_abstracts(p):
    if not p: return {}
    p2 = urllib.parse.urlencode({"db":"pubmed","id":",".join(p),"retmode":"xml","rettype":"abstract","email":EMAIL})
    time.sleep(DELAY)
    d = api(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{p2}")
    if not d: return {}
    a = {}
    try:
        root = ET.fromstring(d)
        for art in root.findall(".//PubmedArticle"):
            pe = art.find(".//PMID")
            if pe is None or not pe.text: continue
            pmid=pe.text.strip()
            te = art.find(".//ArticleTitle")
            t = "".join(te.itertext()).strip() if te is not None else ""
            ap = []
            for ae in art.findall(".//AbstractText"):
                txt = "".join(ae.itertext()).strip()
                if txt: ap.append(txt)
            ab = " ".join(ap)
            ye = art.find(".//PubDate/Year")
            if ye is None: ye=art.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            a[pmid]={"title":t,"abstract":ab,"year":year}
    except: pass
    return a

def make_slug(t):
    return re.sub(r'[^a-zA-Z0-9]+','-',t.lower()).strip('-')[:60] or "untitled"

def download_pdf(pmc_id, title):
    if not pmc_id: return None
    pc = pmc_id.replace("PMC","").strip()
    time.sleep(DELAY)
    oa = api(f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pc}")
    if not oa: return None
    try:
        root = ET.fromstring(oa)
        if root.find(".//error") is not None: return None
        rec = root.find(".//record")
        if rec is None: return None
        lnk = rec.find('link[@format="tgz"]')
        if lnk is None: return None
        fh = lnk.get("href")
        if not fh: return None
    except: return None
    hu = fh.replace("ftp://","https://").replace("/pub/pmc/oa_package/","/pub/pmc/deprecated/oa_package/")
    lf = f"/tmp/hf_{pc}.tar.gz"
    try:
        subprocess.run(["curl","-sL","--connect-timeout","20","--max-time","60","-o",lf,hu],check=True,timeout=70)
    except: return None
    if not os.path.exists(lf) or os.path.getsize(lf)<1000: return None
    try:
        dn = f"t2-PMC{pc}_{re.sub(r'[^a-zA-Z0-9]+','_',title)[:35].strip('_')}.pdf"
        dp = os.path.join(LIBRARY, dn)
        with tarfile.open(lf,"r:gz") as tar:
            pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf") and "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name]
            if not pdfs: pdfs=[m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs: return None
            tar.extract(pdfs[0],path="/tmp/he/")
            shutil.move(os.path.join("/tmp/he/",pdfs[0].name),dp)
        r = subprocess.run(["file","-b",dp],capture_output=True,text=True)
        if "PDF document" in r.stdout and os.path.getsize(dp)>5000: return dn
    except: return None
    finally:
        subprocess.run(["rm","-rf","/tmp/he/"])
        if os.path.exists(lf):
            try: os.remove(lf)
            except: pass
    return None

QUERIES = {
    2: {"name":"Breath/Soul","bridge":"Breath-brain coupling, pranayama, cardiorespiratory entrainment, vagal pathways of consciousness.",
        "qs":['("respiration"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND "synchron"[Title/Abstract]) AND 2010:2025[dp]','("breath"[Title/Abstract] AND "consciousness"[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract])) AND 2010:2025[dp]'],
        "terms":["respiration","breathing","breath","cardiorespiratory","vagal","HRV","pranayama","respiratory","autonomic"]},
    9: {"name":"Language","bridge":"Inner speech, mantra meditation, focused attention, semantic cognition, verbal repetition.",
        "qs":['("inner speech"[Title/Abstract] AND "semantic"[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract])) AND 2010:2025[dp]','("mantra"[Title/Abstract] OR "chanting"[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR brain[Title/Abstract]) AND 2010:2025[dp]'],
        "terms":["inner speech","mantra","chanting","semantic","focused attention","verbal repetition","self-talk"]},
    11:{"name":"Body-energy","bridge":"Interoception, heartbeat, insula, allostasis, cardiorespiratory, visceral perception, spiritus.",
        "qs":['("heartbeat"[Title/Abstract] AND "brain"[Title/Abstract] AND "interoception"[Title/Abstract]) AND 2010:2025[dp]','("allostasis"[Title/Abstract] OR "allostatic"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR insula[Title/Abstract]) AND 2010:2025[dp]'],
        "terms":["heartbeat","interoception","allostasis","allostatic","visceral","cardiac","insula","interoceptive"]},
}

CROSS = [("neural",0.3),("brain",0.2),("fMRI",0.4),("EEG",0.4),("cortex",0.3),("mechanism",0.5)]
NOISE = ["clinical trial","pharmacological","case report","rat "," mice ","murine","animal model","surgery","chemotherapy","cancer","virus"]

def score(t,a,terms):
    tx = f"{t} {a}".lower()
    for n in NOISE:
        if n in tx: return 0,"Noise"
    s = sum(3 if te.lower() in tx else 0 for te in terms)
    s += sum(w for te,w in CROSS if te in tx)
    if s>=3.0: return s,f"Excellent (score={s:.1f})"
    elif s>=2.0: return s,f"Good (score={s:.1f})"
    elif s>=1.5: return s,f"Marginal (score={s:.1f})"
    else: return s,f"Low signal (score={s:.1f})"

for pn in [2,9,11]:
    info = QUERIES[pn]
    seen = set()
    for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
        try:
            d = json.load(open(w))
            if d.get("phase_mapping",{}).get("phase")==pn: seen.add(d.get("title","").lower().strip())
        except: pass
    
    cnt = sum(1 for w in glob.glob(f"{WORKS_DIR}/t2-*.json") if json.load(open(w)).get("phase_mapping",{}).get("phase")==pn)
    need = max(0, 50-cnt)
    print(f"\nPhase {pn} ({info['name']}): {cnt} have, {need} need")
    if need<=0: print("  Already at target"); continue
    
    cands = []
    for q in info["qs"]:
        pmids = search(q,12)
        if not pmids: continue
        su = fetch_summary(pmids)
        ab = fetch_abstracts(pmids)
        for pmid in pmids:
            su2 = su.get(pmid,{})
            ab2 = ab.get(pmid,{})
            t = su2.get("title",ab2.get("title",""))
            if not t: continue
            tl=t.lower().strip()
            if tl in seen: continue
            s_val,s_lab = score(t,ab2.get("abstract",""),info["terms"])
            if s_val<2.0: continue
            seen.add(tl)
            cands.append((s_val,{"pmid":pmid,"title":t,"abstract":ab2.get("abstract",""),"year":ab2.get("year",su2.get("pubdate","")[:4]),"journal":su2.get("source",""),"authors":su2.get("authors",[]),"doi":su2.get("doi","")},su2,s_lab))
    
    if not cands: print("  No candidates"); continue
    cands.sort(key=lambda x:x[0],reverse=True)
    sel = cands[:need]
    
    for sc,art,su2,sl in sel:
        pmc = su2.get("pmc","")
        pdf = download_pdf(pmc,art["title"])
        slug = make_slug(art["title"])
        wid = f"work:t2-pubmed-{slug}"
        yr = art["year"]
        try: yr=int(yr)
        except: pass
        wd = {"work_id":wid,"schema_version":2,"title":art["title"],"authors":[{"name":a} for a in art["authors"][:5]] if isinstance(art["authors"],list) else [],"publication":{"year":yr,"type":"article","source":"PubMed/MEDLINE","language":"en","journal":art.get("journal","")},"identifiers":{"pmid":art["pmid"],"doi":art.get("doi","")},"topics":[f"phase-{pn}-{slug[:20]}","frontier_science","bridge_paper"],"tradition":["contemporary_science"],"tier":2,"assets":{"pdf_path":pdf,"source_url":f"https://pubmed.ncbi.nlm.nih.gov/{art['pmid']}/","abstract":art.get("abstract","")[:500]},"provenance":{"access_status":"open","oa_status":"green" if pdf else "unknown","source":"pubmed_t2_search","retrieved_at":time.strftime("%Y-%m-%d")},"phase_mapping":{"phase":pn,"phase_name":info["name"],"bridge_rationale":info["bridge"]},"evaluation":sl}
        with open(f"{WORKS_DIR}/t2-pubmed-{slug}.json","w") as f: json.dump(wd,f,indent=2,ensure_ascii=False)
        abt = art.get("abstract","")
        if len(abt)>500: abt=abt[:500]+"..."
        ed = {"id":f"bridge-pubmed-{slug}","type":"type-b-essay","title":f"Bridge Essay: {art['title'][:80]}","source_work":wid,"phase":f"phase-{pn}","phase_name":info["name"],"tags":["frontier-science","bridge-paper",f"phase-{pn}"],"body":[{"kind":"ai","text":f"This bridge paper connects the esoteric/philosophical concept of **{info['name']}** with mechanistic science from PubMed/MEDLINE."},{"kind":"ai","text":f"**Bridge rationale:** {info['bridge']}"},{"kind":"summary","text":f"**{art['title']}** — {art.get('journal','?')} ({yr}). PMID: {art['pmid']}. DOI: {art.get('doi','')}. {abt}"}],"notes":f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {pn} ({info['name']}). Evaluation: {sl}"}
        with open(f"{ESSAYS_DIR}/bridge-pubmed-{slug}.json","w") as f: json.dump(ed,f,indent=2,ensure_ascii=False)
        icon="📄" if pdf else "📝"
        print(f"  {icon} [{sl}] {art['title'][:60]} ({art.get('journal','?')} {yr})")

print("\nDone! Checking final counts...")
for p in [2,9,11]:
    cnt=sum(1 for w in glob.glob(f"{WORKS_DIR}/t2-*.json") if json.load(open(w)).get("phase_mapping",{}).get("phase")==p)
    print(f"  Phase {p}: {cnt} papers")
