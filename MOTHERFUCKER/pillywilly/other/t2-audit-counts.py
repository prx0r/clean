#!/usr/bin/env python3
"""Quick phase count audit."""
import json, glob

WORKS_DIR = "/root/projects/blog/content/works"

counts = {}
for wf in glob.glob(f"{WORKS_DIR}/t2-pubmed-*.json"):
    with open(wf) as f:
        try:
            d = json.load(f)
            pm = d.get("phase_mapping", {})
            phase = pm.get("phase", 0)
            if phase not in counts:
                counts[phase] = {"total": 0, "with_pdf": 0}
            counts[phase]["total"] += 1
            assets = d.get("assets", {})
            pdf = assets.get("pdf_path") or d.get("pdf_file")
            if pdf and pdf != "null" and pdf != "None":
                counts[phase]["with_pdf"] += 1
        except:
            pass

# Also count bridge works
bridge_counts = {}
for wf in glob.glob(f"{WORKS_DIR}/bridge-*.json"):
    with open(wf) as f:
        try:
            d = json.load(f)
            phase_str = d.get("phase", "")
            if "10" in phase_str:
                bridge_counts[10] = bridge_counts.get(10, 0) + 1
            elif "11" in phase_str:
                bridge_counts[11] = bridge_counts.get(11, 0) + 1
            elif "12" in phase_str:
                bridge_counts[12] = bridge_counts.get(12, 0) + 1
            elif "13" in phase_str:
                bridge_counts[13] = bridge_counts.get(13, 0) + 1
            elif "6" in phase_str:
                bridge_counts[6] = bridge_counts.get(6, 0) + 1
            elif "9" in phase_str:
                bridge_counts[9] = bridge_counts.get(9, 0) + 1
        except:
            pass

phase_names = {
    1: "Birth/Body", 2: "Breath/Soul", 3: "Heat/Fire",
    4: "Wind/Pride", 5: "Water/Pleasure", 6: "Dependent-arising",
    7: "Form/Meditation", 8: "Formless/Absorption", 9: "Language/Mantra",
    10: "Imaginal", 11: "Body-energy", 12: "Ritual",
    13: "Daimon", 14: "Knowledge/Gnosis", 15: "Liberation/Enlightenment",
    16: "Nondual/Unity", 17: "Ultimate/Emptiness"
}

print(f"{'Phase':<5} {'Name':<25} {'Total':<7} {'With PDF':<10}")
print("-" * 50)
for p in range(1, 18):
    c = counts.get(p, {"total": 0, "with_pdf": 0})
    bridges = bridge_counts.get(p, 0)
    total = c["total"] + bridges
    print(f"{p:<5} {phase_names.get(p, 'Unknown'):<25} {total:<7} {c['with_pdf']:<10}")

print(f"\nTotal works: {sum(c['total'] for c in counts.values()) + sum(bridge_counts.values())}")
print(f"Bridge papers: {sum(bridge_counts.values())}")
