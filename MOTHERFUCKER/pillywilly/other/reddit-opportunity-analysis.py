#!/usr/bin/env python3
"""
Reddit Opportunity Analysis — structured data from clustering.
Produces ranked content opportunities by cross-layer demand.
"""

import json
from pathlib import Path

CLUSTERS_PATH = "data/research/reddit/clusters-v2.json"
OUTPUT_DIR = Path("data/research/reddit")

SUBREDDIT_ROLES = {
    "Tantra": "specialist", "KashmirShaivism": "specialist", "AdvaitaVedanta": "specialist",
    "shaivism": "specialist", "Shaktism": "specialist", "Dzogchen": "specialist",
    "GoldenDawnMagicians": "specialist", "Quareia": "specialist", "Hermeticism": "specialist",
    "Theurgy": "specialist", "Esotericism": "specialist", "alchemy": "specialist",
    "occult": "practitioner", "magick": "practitioner", "hinduism": "practitioner",
    "kundalini": "practitioner", "TibetanBuddhism": "practitioner", "Thelema": "practitioner",
    "TheMindIlluminated": "practitioner", "streamentry": "practitioner",
    "Meditation": "mass", "spirituality": "mass", "awakened": "mass",
    "nonduality": "mass",
    "HighStrangeness": "narrative", "Paranormal": "narrative", "NDE": "narrative",
    "Glitch_in_the_Matrix": "narrative", "AstralProjection": "narrative",
}

POTENTIAL_RO_MAP = {
    "kundalini": "ro:kundalini-awakening",
    "chakras": "ro:chakra-system",
    "consciousness": "ro:consciousness-nonduality",
    "reality": "ro:consciousness-nonduality",
    "nonduality": "ro:consciousness-nonduality",
    "death": "ro:death-afterlife",
    "soul": "ro:death-afterlife",
    "meditation": "ro:meditation-practice",
    "tantra": "ro:tantra-philosophy",
    "tantraloka": "ro:tantraloka-cosmology",
    "abhinavagupta": "ro:abhinavagupta-pratyabhijna",
    "advaita": "ro:advaita-vedanta",
    "kashmir": "ro:kashmir-shaivism",
    "spanda": "ro:spanda-vibration",
    "mantra": "ro:mantra-sound",
    "yantra": "ro:yantra-symbolism",
    "devi": "ro:devi-goddess",
    "shiva": "ro:shiva-bhairava",
    "kali": "ro:kali-tantra",
    "bhairava": "ro:bhairava-tantra",
    "goddess": "ro:devi-goddess",
    "dream": "ro:dream-lucid",
    "lucid": "ro:dream-lucid",
    "astral": "ro:astral-projection",
    "energy": "ro:energy-body",
    "chakra": "ro:chakra-system",
    "breath": "ro:pranayama-breath",
    "pranayama": "ro:pranayama-breath",
    "enlightenment": "ro:enlightenment-liberation",
    "moksha": "ro:enlightenment-liberation",
    "liberation": "ro:enlightenment-liberation",
    "yoga": "ro:yoga-philosophy",
    "sutra": "ro:yoga-sutras",
    "upanishad": "ro:upanishads",
    "bhagavad": "ro:bhagavad-gita",
    "gita": "ro:bhagavad-gita",
    "puranas": "ro:puranas-mythology",
    "veda": "ro:vedas",
    "ritual": "ro:ritual-practice",
    "puja": "ro:ritual-practice",
    "deity": "ro:deity-worship",
    "guru": "ro:guru-tradition",
    "initiation": "ro:initiation-diksha",
    "diksha": "ro:initiation-diksha",
    "samadhi": "ro:samadhi-contemplation",
}

def classify_role(subreddit):
    return SUBREDDIT_ROLES.get(subreddit, "unknown")

def main():
    with open(CLUSTERS_PATH) as f:
        data = json.load(f)

    clusters = data["clusters"]

    # Filter: keep clusters with >= 10 posts and identifiable topic
    clean = [c for c in clusters if c["total_occurrences"] >= 10
             and len(" ".join(c.get("subject_terms", []))) > 3]

    # Enrich with role analysis
    for c in clean:
        subs = c.get("subreddits", [])
        roles_present = set()
        for s in subs:
            r = classify_role(s)
            if r != "unknown":
                roles_present.add(r)
        c["roles_present"] = sorted(roles_present)
        c["has_specialist"] = "specialist" in roles_present
        c["has_mass"] = "mass" in roles_present
        c["translation_gap"] = c["has_specialist"] and c["has_mass"]
        c["layer_span"] = len(roles_present)

        # Map to potential ROs
        all_text = " ".join(c.get("subject_terms", [])) + " " + " ".join(subs)
        matching_ros = set()
        for keyword, ro_id in POTENTIAL_RO_MAP.items():
            if keyword.lower() in all_text.lower():
                matching_ros.add(ro_id)
        c["potential_ros"] = sorted(matching_ros)

        # Opportunity score
        demand = c["total_occurrences"] * c["median_score"]
        c["demand_score"] = round(demand, 1)

    # Rank: translation gap first, then demand, then layer span
    def rank_key(c):
        return (1 if c["translation_gap"] else 0,
                c["layer_span"],
                c["demand_score"])

    clean.sort(key=rank_key, reverse=True)

    # Build output
    output = {
        "generated": "2026-07-21",
        "source": "reddit-clusters-v2",
        "total_questions_analyzed": data["rows_analyzed"],
        "total_clusters_input": data["total_clusters"],
        "total_clusters_clean": len(clean),
        "opportunities": [],
        "translation_gaps": [],
        "all_topics": [],
    }

    for c in clean:
        entry = {
            "size": c["total_occurrences"],
            "median_score": c["median_score"],
            "demand_score": c["demand_score"],
            "terms": c.get("subject_terms", [])[:6],
            "subreddits": c.get("subreddits", []),
            "roles": c["roles_present"],
            "has_specialist": c["has_specialist"],
            "has_mass": c["has_mass"],
            "translation_gap": c["translation_gap"],
            "layer_span": c["layer_span"],
            "potential_ros": c["potential_ros"],
        }
        output["all_topics"].append(entry)

        if c["translation_gap"]:
            output["translation_gaps"].append(entry)

    # Top opportunities: translation gaps ranked by demand
    output["opportunities"] = sorted(
        output["translation_gaps"],
        key=lambda x: -x["demand_score"]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "opportunity-analysis.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {path}")
    print(f"\n=== TRANSLATION GAPS (specialist question appears in mass sub) ===")
    for o in output["opportunities"]:
        ros = ", ".join(o["potential_ros"][:3]) if o["potential_ros"] else "(none mapped)"
        print(f"  {o['terms'][0]:30s} size={o['size']:>4} score={o['median_score']:>4}  ROs: {ros}")

    print(f"\n=== TOP DEMAND (all clusters, ranked by score*size) ===")
    all_by_demand = sorted(output["all_topics"], key=lambda x: -x["demand_score"])
    for o in all_by_demand[:20]:
        tag = " [GAP!]" if o["translation_gap"] else ""
        print(f"  {o['terms'][0]:30s} size={o['size']:>4} score={o['median_score']:>4} layers={o['layer_span']}{tag}")

    print(f"\n=== RO MAPPING SUMMARY ===")
    ro_counts = {}
    for o in output["all_topics"]:
        for ro in o["potential_ros"]:
            ro_counts[ro] = ro_counts.get(ro, 0) + 1
    for ro, count in sorted(ro_counts.items(), key=lambda x: -x[1]):
        print(f"  {ro}: {count} related clusters")

if __name__ == "__main__":
    main()
