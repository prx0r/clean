#!/usr/bin/env python3
"""Polite topical acquisition: search all fields, 10s apart, AND-joined terms.
   Sources: HAL → Zenodo → DOAJ. No author-specific searching."""
import json, os, urllib.request, urllib.parse, time, hashlib
from pathlib import Path

W, L = "content/works", "/root/.hermes/cron/cron-acquire.log"
STATE = "/root/.hermes/cron/cron-state.json"
UA = "Mailto:tradesprior@gmail.com HermesAcquisition/1.0"
CORE_KEY = "E9FJmcOGujhB0Ls78Tg14PHfyVKNDzSx"

# Real scholars — search author field only on each source
AUTHORS = [
    # Ficino / Renaissance Platonism
    "Anna Corrias","Michael J.B. Allen","Stephen Gersh","Brian Copenhaver",
    "Denis Robichaud","Jacomien Prins","John Finamore","Crystal Addey",
    "Radek Chlup","Edward Butler","Angela Voss","Gregory Shaw",
    "Christopher Celenza","James Hankins","Peter Adamson",
    # Corbin / Islamic imaginal
    "John V. Garner","Lydia Idinopulos","Elliot Wolfson","William Chittick",
    "John Walbridge","Tom Cheetham","Christian Jambet","Pierre Lory",
    "James Winston Morris","Salman Bashier","Roxanne Marcotte",
    "Mohammad Ali Amir-Moezzi","Sajjad Rizvi","Nader El-Bizri",
    # Theurgy / Neoplatonism
    "Polymnia Athanassiadi","John M. Dillon","Dominic O'Meara",
    "Lloyd Gerson","Pauliina Remes","Sara Rappe","Kevin Corrigan",
    "Peter Struck","Anne Sheppard","Algis Uždavinys",
    # Buddhist phenomenology
    "Bhikkhu Analayo","Bhikkhunī Dhammadinnā","Stephen Evans",
    "Sue Hamilton","Peter Harvey","Christian Coseru","Dan Lusthaus",
    "Rupert Gethin","Sonam Kachru","Jan Westerhoff",
    # Soulmaking / imaginal practice
    "James Hillman","Mary Watkins","Robert Romanyshyn",
    "David McMahan","Catherine McGee","Yahel Avigur",
    # Broader context
    "Wouter Hanegraaff","Pierre Hadot","Sarah Iles Johnston",
    "Dorian Greenbaum","Claire Fanger","Moshe Idel",
]

# Topic queries — high-signal only. Removed single generic words and overly broad terms.
TOPICS = [
    # Core imaginal / theurgy — high signal
    "henry corbin imaginal","mundus imaginalis","ficino daimon",
    "iamblichus theurgy","proclus theurgy","plato daimon",
    "Nanananda papanca","vehicle of the soul","ancient theurgy",
    # Platonism / Neoplatonism — specific phrases
    "prisca theologia","platonic theology","neoplatonic contemplation",
    "divine madness","active imagination","anima mundi","world soul",
    "subtle body","astral body","intermediary beings",
    "philosophy as a way of life","imaginal world","barzakh",
    "creative imagination","esoteric hermeneutics",
    "illuminationist philosophy","ishraqi philosophy",
    "henadology","polycentric metaphysics",
    "buddhist phenomenology","papanca","empty fabrication",
    "soulmaking","imaginal practice","erotic knowing",
    "sufi metaphysics","divine self-disclosure",
    "platonic eros","beauty contemplation","henadic consciousness",
    # Magick / occult — specific traditions
    "renaissance magic","natural magic","celestial magic",
    "ceremonial magic","ritual magic",
    "grimoire tradition","solomonic magic","key of solomon",
    "ars goetia","ars theurgia goetia",
    "greek magical papyri","papyri graecae magicae",
    "curse tablets","magical gems","divine names",
    "theurgic union","theurgic ascent",
    # Astrology — named traditions
    "renaissance astrology","hellenistic astrology",
    "judicial astrology","electional astrology",
    "astrological magic","celestial influences",
    "planetary hours","planetary spirits",
    "ptolemy tetrabiblos","firmicus maternus",
    "astrological talismans",
    # Hermeticism — specific texts
    "hermeticism","hermetic philosophy","corpus hermeticum",
    "hermes trismegistus","poimandres",
    # Alchemy — specific concepts
    "alchemical tradition","magnum opus","philosopher stone",
    "prima materia","nigredo","albedo","rubedo",
    "coniunctio","solve et coagula",
    "paracelsus alchemy","spiritual alchemy",
    # Kabbalah
    "kabbalah mysticism","hermetic kabbalah","christian kabbalah",
    "pico della mirandola kabbalah","reuchlin",
    "merkabah mysticism","ecstatic kabbalah",
    # Gnosticism
    "gnostic tradition","gnostic cosmology","valentinian gnosis",
    "nag hammadi","pistis sophia","gnostic demiurge",
    # Sufi / Islamic esotericism
    "islamic esotericism","sufi cosmology","wahdat al-wujud",
    "insan al-kamil","ibn arabi metaphysics",
    "akbarian tradition","mulla sadra philosophy",
    "suhrawardi illuminationist","shiite esotericism",
    # Renaissance / early modern
    "ficinian platonism","pico della mirandola",
    "byzantine platonism","hermetic revival","occult philosophy",
    "agrippa von nettesheim","john dee","giordano bruno",
    "paracelsus medicine","renaissance kabbalah",
    "prisca sapientia","perennial philosophy",
    # Esotericism
    "western esotericism","mystery schools",
    "orphic mysteries","eleusinian mysteries",
    "pythagorean philosophy","neopythagoreanism",
    "traditionalist school","guenon philosophy",
    # Ritual / contemplative
    "contemplative prayer","hesychasm",
    "dream incubation","lectio divina",
    # Psyche
    "archetypal psychology","imaginal psychology",
    "intermediate realm","liminal space",
    "alchemical psychology","jungian alchemy",
    # Elements / cosmos
    "elemental philosophy","cosmic sympathy",
    "sympathetic magic","macrocosm microcosm",
    "great chain of being","emanationist cosmology",
]

QUERIES = TOPICS

SOURCES = ["hal","zenodo","core"]

def andify(s):
    """Split multi-word topic into individual AND terms for search"""
    return urllib.parse.quote(" AND ".join(s.split()))
def log(m):
    with open(L,"a") as f: f.write(f"{m}\n")
def exists(w): return any(w[:20] in p.name for p in Path(W).iterdir())
def save(wid,tit,aut,pdf,src):
    Path(W).mkdir(exist_ok=True)
    if Path(W,f"{wid}.json").exists(): return
    json.dump({"work_id":wid,"title":tit[:120],"authors":[{"name":aut}],"tier":2,"assets":{"pdf_path":pdf},"provenance":{"access_status":"open","source":src},"analysis":{"tier":2}}, open(Path(W,f"{wid}.json"),"w"), indent=2)
def dl(url,dest):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA})
        with urllib.request.urlopen(req,timeout=15) as r:
            b=r.read()
        if b[:4]==b'%PDF' and len(b)>5000:
            os.makedirs(os.path.dirname(dest),exist_ok=True); open(dest,"wb").write(b); return True
    except Exception as e: log(f"  ⚠ {e}")
    return False

with open(L,"a") as f: f.write(f"\n{'='*40} PID {os.getpid()} {'='*40}\n")
log(f"Topical search: {len(TOPICS)} topics, 10s apart")

n = 0
if os.path.exists(STATE):
    try:
        with open(STATE) as f:
            n = json.load(f).get("n", 0) + 1  # skip last completed
    except Exception as e: log(f"  ⚠ {e}")
log(f"Resuming at step {n}")

while True:
    try:
        query = QUERIES[n % len(QUERIES)]
        src = SOURCES[n % len(SOURCES)]
        eq = andify(query)
        log(f"\n{src.upper()}: {query}")

        if src == "hal":
            try:
                with urllib.request.urlopen(f"https://api.archives-ouvertes.fr/search/?q={eq}&fq=submitType_s:file&wt=json&fl=title_s,fileMain_s&rows=10",timeout=15) as r:
                    for doc in json.loads(r.read()).get("response",{}).get("docs",[]):
                        t,pdf=(doc.get("title_s") or [""])[0],doc.get("fileMain_s","")
                        if not pdf: continue
                        wid="w:"+hashlib.md5(t.encode()).hexdigest()[:12]
                        if exists(wid): continue
                        fn=f"library/hal/{hashlib.md5(t.encode()).hexdigest()[:12]}.pdf"
                        if dl(pdf,fn): save(wid,t,query,fn,"hal"); log(f"  ✅ {t[:35]}")
            except Exception as e: log(f"  ⚠ {e}")

        elif src == "zenodo":
            try:
                with urllib.request.urlopen(f"https://zenodo.org/api/records?q={eq}&size=10&sort=mostrecent",timeout=15) as r:
                    for hit in json.loads(r.read()).get("hits",{}).get("hits",[]):
                        t=hit.get("metadata",{}).get("title","")
                        for f in hit.get("files",[]):
                            d=f.get("links",{}).get("self","")
                            if not d or ".pdf" not in d: continue
                            wid="w:"+hashlib.md5(t.encode()).hexdigest()[:12]
                            if exists(wid): continue
                            fn=f"library/zenodo/{hashlib.md5(t.encode()).hexdigest()[:12]}.pdf"
                            if dl(d,fn): save(wid,t,query,fn,"zenodo"); log(f"  ✅ {t[:35]}")
            except Exception as e: log(f"  ⚠ {e}")

        elif src == "core":
            try:
                req = urllib.request.Request(f"https://api.core.ac.uk/v3/search/works?q={eq}&page=1&pageSize=5")
                req.add_header("Authorization", f"Bearer {CORE_KEY}")
                req.add_header("User-Agent", UA)
                with urllib.request.urlopen(req,timeout=10) as r:
                    for w in json.loads(r.read()).get("results",[]):
                        t=w.get("title","")
                        pdf=w.get("fullTextUrl","") or w.get("pdfUrl","") or ""
                        if not t or not pdf: continue
                        wid="w:"+hashlib.md5(t.encode()).hexdigest()[:12]
                        if exists(wid): continue
                        fn=f"library/core/{hashlib.md5(t.encode()).hexdigest()[:12]}.pdf"
                        if dl(pdf,fn): save(wid,t,query,fn,"core"); log(f"  ✅ {t[:35]}")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    log(f"  ⚠ CORE rate limited (429)")
                else:
                    log(f"  ⚠ CORE HTTP {e.code}")
            except Exception as e: log(f"  ⚠ {e}")

        n += 1
        with open(STATE, "w") as f: json.dump({"n": n}, f)
        time.sleep(10)

    except Exception as e:
        log(f"CRASH: {e}")
        time.sleep(30)
