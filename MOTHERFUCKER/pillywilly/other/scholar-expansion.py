#!/usr/bin/env python3
"""Scholar expansion: finds co-authors of known scholars, feeds into acquisition.
   Runs independently. Reads/writes scripts/acquisition-queries.txt."""
import json, urllib.request, urllib.parse, random, time, os

OA_KEY = "pCu5xinOa9gt0JarceKUzG"
OA_BASE = "https://api.openalex.org"
LOG = "/root/.hermes/cron/cron-acquire.log"
QUERIES_FILE = "scripts/acquisition-queries.txt"

def log(m):
    with open(LOG,"a") as f: f.write(f"{m}\n")

SEEDS = ["Anna Corrias","Stephen Gersh","Michael J.B. Allen","Brian Copenhaver",
    "John V. Garner","Elliot R. Wolfson","William Chittick","John Walbridge",
    "Lydia Idinopulos","Christopher Celenza","James Hankins","Moshe Idel",
    "Claire Fanger","Polymnia Athanassiadi","John Finamore","Edward Butler",
    "Rob Burbea","Patrick Harpur","Dorian Greenbaum","Mark Dyczkowski",
    "Sarah Iles Johnston","Tom Cheetham","David Abram","Christopher Wallis",
    "Abhinavagupta","Bhartṛhari","Ñāṇavīra Thera","Christopher Wallis Tantra",
    "Dharmakīrti","Dignāga","Patañjali","Frater Acher","Jake Stratton-Kent",
    "Ruth Majercik","Graham Harvey","John Grimes"]

known = set(SEEDS)
if os.path.exists(QUERIES_FILE):
    with open(QUERIES_FILE) as f:
        for line in f:
            name = line.strip()
            if name and not name.startswith("#"):
                known.add(name)

log(f"\n=== SCHOLAR EXPANSION: {len(known)} seeds ===")

while True:
    try:
        seed = random.choice(list(known))
        q = urllib.parse.quote(seed.split(" (")[0].split(" —")[0])
        with urllib.request.urlopen(f"{OA_BASE}/authors?search={q}&api_key={OA_KEY}&per_page=1&select=id,display_name", timeout=10) as r:
            d = json.loads(r.read())
        if not d.get("results"):
            time.sleep(3); continue
        aid = d["results"][0]["id"].split("/")[-1]
        with urllib.request.urlopen(f"{OA_BASE}/works?filter=authorships.author.id:{aid}&per_page=5&sort=cited_by_count:desc&api_key={OA_KEY}&select=authorships,publication_year", timeout=10) as r:
            wk = json.loads(r.read())
        new_found = 0
        for work in wk.get("results", []):
            for au in work.get("authorships",[]):
                name = au.get("author",{}).get("display_name","")
                if not name or name.lower() == seed.lower(): continue
                if name not in known:
                    known.add(name)
                    with open(QUERIES_FILE,"a") as f:
                        f.write(f"{name}\n")
                    new_found += 1
                    log(f"  ➕ {name} (co-author of {seed})")
        if new_found > 0:
            log(f"  Found {new_found} new via {seed}")
        time.sleep(4)
    except Exception as e:
        log(f"  {e}")
        time.sleep(6)
