#!/usr/bin/env python3
"""One-time: resolve each scholar to their verified OpenAlex author ID
   by searching their name + a domain concept filter.
   Saves scripts/verified-authors.json"""
import json, urllib.request, urllib.parse, time
from pathlib import Path

OA = "https://api.openalex.org"
UA = "Mailto:tradesprior@gmail.com HermesAcquisition/1.0"
OUT = Path("scripts/verified-authors.json")

# Group scholars by which OpenAlex concept best finds them
# Concept IDs from OpenAlex: Neoplatonism, Renaissance, Western esotericism, etc.
DOMAINS = {
    "Neoplatonism": ["Anna Corrias","Michael J.B. Allen","Stephen Gersh","Brian Copenhaver",
                     "Angela Voss","Gregory Shaw","John Finamore","Crystal Addey"],
    "Islamic philosophy": ["William Chittick","John Walbridge","John V. Garner","Lydia Idinopulos"],
    "Mysticism": ["Elliot Wolfson","Wouter Hanegraaff","Tom Cheetham"],
    "Buddhism": ["Bhikkhu Analayo","Bhikkhunī Dhammadinnā"],
}

DOMAIN_CONCEPTS = {
    "Neoplatonism": "https://openalex.org/C2775878487",
    "Islamic philosophy": "https://openalex.org/C2777197248",
    "Mysticism": "https://openalex.org/C2776398505",
    "Buddhism": "https://openalex.org/C2778212479",
}

def req(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

result = {}
print("=== Author Disambiguation ===\n")

for domain, scholars in DOMAINS.items():
    concept = DOMAIN_CONCEPTS.get(domain)
    for name in scholars:
        print(f"  {name} ({domain})...")
        time.sleep(1.1)
        try:
            q = urllib.parse.quote(name)
            url = f"{OA}/authors?search={q}&filter=concept.id:{concept}&per_page=3&sort=cited_by_count:desc&select=id,display_name,cited_by_count,works_count,last_known_institutions"
            data = req(url)
            candidates = data.get("results", [])
            if candidates:
                aid = candidates[0]["id"].split("/")[-1]
                insts = candidates[0].get("last_known_institutions", [])
                inst = insts[0].get("display_name","?") if insts else "?"
                print(f"    ✓ {aid} ({candidates[0].get('cited_by_count',0)} cit, {inst})")
                result[name] = aid
            else:
                # Fallback: search without concept filter
                url2 = f"{OA}/authors?search={q}&per_page=3&sort=cited_by_count:desc&select=id,display_name,cited_by_count"
                data2 = req(url2)
                candidates2 = data2.get("results", [])
                if candidates2:
                    aid = candidates2[0]["id"].split("/")[-1]
                    print(f"    ? {aid} (no concept match, using most cited)")
                    result[name] = aid
                else:
                    print(f"    ✗ not found")
        except Exception as e:
            print(f"    ✗ {e}")

OUT.write_text(json.dumps(result, indent=2))
print(f"\nSaved {len(result)} verified authors to {OUT}")
