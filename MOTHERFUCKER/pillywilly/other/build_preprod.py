"""
Build ALL pre-production files for You Are Made of Light.
Validates each step's output against platinum format.
"""
import json, os, re, sys

OUT = "/root/projects/blog/content/publishing/renders/you-are-made-of-light/v1"
ESSAY_PATH = "/root/projects/blog/scripts/expansion-essay7.md"
os.makedirs(OUT, exist_ok=True)

# ── STEP 1: CLEAN NARRATION ────────────────────────────────
def clean_script(markdown: str) -> str:
    spoken_lines = []
    for line in markdown.splitlines():
        text = line.strip()
        if not text or text == "---":
            continue
        if text.startswith("# "):
            continue
        if text.startswith(">"):
            text = text[1:].strip()
        # Remove markdown emphasis
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        spoken_lines.append(text)
    return "\n\n".join(spoken_lines)

raw = open(ESSAY_PATH).read()
narration = clean_script(raw)
open(f"{OUT}/narration_script.txt", "w").write(narration)
open(f"{OUT}/source_essay.md", "w").write(raw)

word_count = len(narration.split())
print(f"Step 1: Clean narration — {word_count} words")
print(f"  → narration_script.txt, source_essay.md")

# ── STEP 2: SEGMENT INTO SHOTS ─────────────────────────────
sentences = re.split(r'(?<=[.!?])\s+', narration)
shots_text = []
for s in sentences:
    s = s.strip()
    if not s or len(s.split()) < 3:
        continue
    # Only split very long sentences (>28 words)
    if len(s.split()) > 28:
        parts = re.split(r'(?:;\s|,\s*(?:and|but|the|when|however)\s)', s)
        for p in parts:
            p = p.strip()
            if p and len(p.split()) > 3:
                shots_text.append(p)
    else:
        shots_text.append(s)

# Merge short adjacent shots
merged = []
i = 0
while i < len(shots_text):
    if len(shots_text[i].split()) < 5 and i+1 < len(shots_text):
        merged.append(shots_text[i] + " " + shots_text[i+1])
        i += 2
    else:
        merged.append(shots_text[i])
        i += 1
shots_text = merged

print(f"Step 2: Segmentation — {len(shots_text)} shots")

# ── STEP 3: MOTIF SYSTEM ────────────────────────────────────
# Define recurring visual systems from the visual thesis
# Each chapter gets motifs that match the content

CHAPTERS = [
    (0, "prologue", "Prologue", "Three layers of self: body, mind, witness"),
    (3, "ladder", "I. The Ladder", "The 36 tattvas from earth to Śiva"),
    (12, "powers", "II. The Five Powers", "Consciousness, bliss, will, knowledge, action"),
    (20, "descent", "III. Descent and Ascent", "Elements and the return upward"),
    (28, "lattice", "IV. The Lattice", "The structure of 36 interconnected principles"),
    (36, "kancukas", "V. The Kañcukas", "The five coverings that armor the soul"),
    (42, "threshold", "VI. The Threshold", "The 37th and 38th principles beyond naming"),
    (47, "epilogue", "Epilogue", "The ladder dissolves into light"),
]

def get_chapter(idx):
    for start, cid, ctitle, thesis in reversed(CHAPTERS):
        if idx >= start:
            return cid, ctitle, thesis, idx == start
    return "prologue", "Prologue", "", True

def assign_motif(text, idx):
    t = text.lower()
    
    # Prologue
    if idx < 3:
        return ["body_surface", "mind_thought", "witness_center"][idx]
    
    # Ladder — 36 tattvas
    if idx < 12:
        concepts = ["earth_dense", "water_flow", "fire_transform", "air_subtle",
                     "ether_expand", "tattva_emerge", "siva_summit", "consciousness_apex",
                     "descent_begin", "maya_veil", "kancuka_armor", "soul_contracted"]
        return concepts[idx - 3] if (idx - 3) < len(concepts) else "tattva_emerge"
    
    # Five powers
    if idx < 20:
        powers = ["cit_consciousness", "ananda_bliss", "iccha_will",
                   "jnana_knowledge", "kriya_action", "pentad_align",
                   "pentad_merge", "undifferentiated_light"]
        return powers[idx - 12] if (idx - 12) < len(powers) else "pentad_align"
    
    # Descent/Ascent
    if idx < 28:
        return ["descent_body", "descent_mind", "descent_witness",
                "element_earth", "element_water", "element_fire",
                "element_air", "element_ether"][idx - 20]
    
    # Lattice
    if idx < 36:
        return ["lattice_base", "lattice_build", "lattice_connect",
                "lattice_illuminate", "lattice_pulse", "lattice_full",
                "lattice_climb", "lattice_dissolve"][idx - 28]
    
    # Kañcukas
    if idx < 42:
        return ["kala_action", "vidya_knowledge", "raga_attachment",
                "kala_time", "niyati_fate", "kancuka_dissolve"][idx - 36]
    
    # Threshold
    if idx < 47:
        return ["threshold_door", "threshold_cross", "beyond_naming",
                "thirty_seventh", "threshold_dissolve"][idx - 42]
    
    # Epilogue
    return ["ladder_fade", "light_residue", "you_are_light"][min(idx - 47, 2)]

# ── STEP 4: BUILD STORYBOARD ───────────────────────────────
# Duration estimates — will be replaced with real WAV measurements
shots = []
current_time = 0.0
prev_chapter = ""

for i, text in enumerate(shots_text):
    words = len(text.split())
    dur = max(5.0, min(9.5, round(words / 2.8, 1)))
    
    ch_id, ch_title, ch_thesis, ch_start = get_chapter(i)
    motif = assign_motif(text, i)
    
    shots.append({
        "shot_id": f"shot_{i+1:03d}",
        "chapter": ch_id,
        "chapter_title": ch_title,
        "source_kind": "essay_prose",
        "spoken_text": text,
        "start_seconds": round(current_time, 3),
        "end_seconds": round(current_time + dur, 3),
        "duration_seconds": round(dur, 3),
        "motif": motif,
        "visual_mechanism": motif.replace("_", " "),
        "background_justification": "Dark void with gold light forms the substrate; crimson marks life and intensity; lapis indicates depth and intelligence; gold is consciousness itself.",
        "transition": "fade to shared void at audio boundary",
        "continuity_object": "a small gold point of consciousness remains throughout",
        "caption_restrictions": "No sentence subtitles; technical terms only",
        "first_in_chapter": ch_start,
    })
    current_time += dur
    prev_chapter = ch_id

# ── STEP 5: VALIDATE AGAINST PLATINUM FORMAT ───────────────
pt_path = "/root/projects/blog/content/publishing/renders/you_existed_before_earth/you_existed_before_earth_film_pack/storyboard.json"
with open(pt_path) as f:
    pt_shots = json.load(f)

pt_fields = set(pt_shots[0].keys())
my_fields = set(shots[0].keys())
missing = pt_fields - my_fields
extra = my_fields - pt_fields

dur_list = [s['duration_seconds'] for s in shots]
valid = True

print(f"\nStep 5: Storyboard validation")
print(f"  Shots: {len(shots)} (target: 50-70)")
print(f"  Duration: {sum(dur_list):.0f}s ({sum(dur_list)/60:.1f} min)")
print(f"  Avg: {sum(dur_list)/len(dur_list):.1f}s (target: 5-10s)")
print(f"  Range: {min(dur_list):.1f}-{max(dur_list):.1f}s (target: 5.0-10.0s)")
print(f"  Motifs: {len(set(s['motif'] for s in shots))}")
print(f"  Chapters: {len(set(s['chapter'] for s in shots))}")
print(f"  Fields match platinum: {'YES' if not missing else f'NO — missing: {missing}'}")
print(f"  Extra fields: {extra if extra else 'none'}")

# Validate against thresholds
checks = [
    (50 <= len(shots) <= 110, f"Shot count {len(shots)} outside 50-110"),
    (min(dur_list) >= 4.0, f"Min shot {min(dur_list):.1f} < 4.0s"),
    (max(dur_list) <= 10.5, f"Max shot {max(dur_list):.1f} > 10.5s"),
    (sum(dur_list)/len(dur_list) >= 5.0, f"Avg shot {sum(dur_list)/len(dur_list):.1f} < 5.0s"),
    (sum(dur_list)/len(dur_list) <= 9.0, f"Avg shot {sum(dur_list)/len(dur_list):.1f} > 9.0s"),
    (len(missing) == 0, f"Missing fields: {missing}"),
]
for ok, msg in checks:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {msg}")
    if not ok:
        valid = False

# Save storyboard regardless — will update after WAV measurement
with open(f"{OUT}/storyboard.json", "w") as f:
    json.dump(shots, f, indent=2, ensure_ascii=False)

if not valid:
    print("\n⚠ Storyboard has validation issues. Fix before rendering.")

# ── STEP 6: BUILD VISUAL PROGRAM ───────────────────────────
vp = {
    "film_id": "expansion-essay7-you-are-made-of-light",
    "title": "You Are Made of Light",
    "source_script": "scripts/expansion-essay7.md",
    "sync_policy": {
        "method": "Each shot receives its own synthesized WAV. The full narration is the sample-exact concatenation of those WAVs.",
        "visual_lead_seconds": 0.0,
    },
    "continuity_systems": [
        {"id": "ladder_of_light", "development": "dense earth → ascending rungs → translucent structure → pure light at summit"},
        {"id": "five_powers", "development": "consciousness → bliss → will → knowledge → action → merged light"},
        {"id": "descent_through_densities", "development": "earth → water → fire → air → ether → reversal → ascent"},
        {"id": "witness_lattice", "development": "36 points → connections form → lattice pulses → illuminates fully → dissolves"},
        {"id": "threshold", "development": "door at 36th level → opens → 37th appears → 38th beyond → door dissolves"},
    ],
    "chapters": [{"id":cid, "title":ctitle, "visual_thesis":thesis} for start, cid, ctitle, thesis in CHAPTERS],
    "palette": {
        "void": "#0D1117",
        "gold": "#D4A574",
        "crimson": "#8D2C39",
        "lapis": "#2A466E",
        "ink": "#E6E1DC",
        "muted": "#918D84",
    },
    "entities": [
        {"id": "light_point", "archetype": "bindu", "continuity": "persistent"},
        {"id": "ladder", "archetype": "axis", "continuity": "transforms"},
        {"id": "witness", "archetype": "observer", "continuity": "persistent"},
    ],
    "operators": ["ascend","descend","illuminate","pulse","dissolve","condense","expand","reveal","hold"],
}

with open(f"{OUT}/visual_program.json", "w") as f:
    json.dump(vp, f, indent=2, ensure_ascii=False)
print(f"\nStep 6: visual_program.json — {len(vp['continuity_systems'])} continuity systems, {len(vp['chapters'])} chapters")

# Save shot count for next steps
print(f"\n=== Ready for audio generation ===")
print(f"Run: cd /root/projects/blog && python3 scripts/generate-voiceover.mjs --storyboard {OUT}/storyboard.json")
print(f"Or generate per-shot WAVs via Edge TTS")
print(f"Then measure durations and update storyboard.json")
