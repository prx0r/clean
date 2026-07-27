"""
Build pre-production files for expansion-essay34 (You Existed Before the Earth).
Validate against platinum format BEFORE rendering.
"""
import json, re, os, math

OUT = "/root/projects/blog/content/publishing/renders/you-existed-before-earth/v1"
os.makedirs(OUT, exist_ok=True)

# ── 1. VISUAL THESIS ────────────────────────────────────────
# Based on the essay's concepts: consciousness, evolution, imagination, cooperation

visual_thesis = {
    "material_world": "A luminous ivory field where forms condense from and dissolve back into light. Not void — light-as-substance.",
    "spatial_world": "An infinite ivory field with no horizon. Things appear within it, float, transform, and return.",
    "motion_world": ["condense","radiate","weave","dissolve","align","pulse","unfold","converge"],
    "recurring_systems": [
        {
            "id": "field_before_form",
            "development": "empty luminous field → field with seed → field with body → field persists under all transformations",
            "shots": 10
        },
        {
            "id": "attention_lens",
            "development": "oval lens appears → holds multiple times/scales simultaneously → lens resolves to single point",
            "shots": 6
        },
        {
            "id": "consciousness_seed",
            "development": "small gold point → grows → branches → becomes network → returns to point",
            "shots": 8
        },
        {
            "id": "wave_particle",
            "development": "continuous field → ripples → wave peaks → particle condenses → cascade of matter",
            "shots": 8
        },
        {
            "id": "cooperative_network",
            "development": "isolated nodes → connections form → network intensifies → mutual enhancement → one fabric",
            "shots": 8
        },
        {
            "id": "two_stories",
            "development": "two frames side by side → one fades → other solidifies → choice resolved in final image",
            "shots": 5
        }
    ],
    "palette": {
        "ivory": "#F6F2E8",     # shared field (70%)
        "umber": "#3C2F26",     # earth, structure (10%)
        "gold": "#B38B4D",      # consciousness, seed (8%)
        "lapis": "#3B5E7C",     # intelligence, depth (5%)
        "crimson": "#852F47",   # activation, life (5%)
        "teal": "#4A8B7B",      # relation, growth (2%)
    },
    "shape_semantics": {
        "point": "seed, consciousness, source",
        "circle": "field, wholeness, containment",
        "line": "connection, axis, direction",
        "aperture": "threshold, perception, access",
        "branch": "differentiation, unfolding",
        "network": "relation, cooperation, interdependence"
    },
    "forbidden": ["generic galaxy", "random particles", "meditation silhouette", "text duplicating narration", "unmotivated circles"]
}

with open(os.path.join(OUT, "visual_thesis.json"), "w") as f:
    json.dump(visual_thesis, f, indent=2)

# ── 2. NARRATION SCRIPT ─────────────────────────────────────
essay = open("/root/projects/blog/scripts/expansion-essay34.md").read()
lines = essay.split('\n')
clean = []
for line in lines:
    line = line.strip()
    if line.startswith('#') or line.startswith('---'):
        continue
    if line.startswith('>'):
        clean.append(line.lstrip('> '))
    elif line:
        clean.append(line)
narration = ' '.join(clean)

with open(os.path.join(OUT, "narration_script.txt"), "w") as f:
    f.write(narration)

# ── 3. SPLIT INTO SHOTS ─────────────────────────────────────
sentences = re.split(r'(?<=[.!?])\s+', narration)
shot_texts = []
for s in sentences:
    s = s.strip()
    if not s or len(s.split()) < 3:
        continue
    words = len(s.split())
    if words > 18:
        parts = re.split(r'(?:;\s|,\s*(?:and|but|the|when|where|which|that|because|for|if)\s)', s)
        for p in parts:
            p = p.strip()
            if p and len(p.split()) > 3:
                shot_texts.append(p)
            elif p and shot_texts:
                shot_texts[-1] += " " + p
    else:
        shot_texts.append(s)

print(f"Narration: {len(narration.split())} words → {len(shot_texts)} shots")

# ── 4. MOTIF MAP ────────────────────────────────────────────
# Each motif appears 1-3 times with different variants
def assign_motif(text, idx, total):
    """Assign motif based on text content and position in film."""
    t = text.lower()
    
    # Opening (first 8 shots)
    if idx < 3:
        return "field_before_body" if idx == 0 else ("body_condenses" if idx == 1 else "attention_lens")
    
    # Spacious Present (shots 3-12)
    if idx < 12:
        if "time" in t or "past" in t or "present" in t or "future" in t or "was" in t or "is" in t or "will" in t:
            return "time_orbits"
        if "large" in t or "small" in t or "scale" in t or "hold" in t:
            return "scale_equivalence"
        if "flower" in t or "seed" in t or "unfold" in t or "open" in t:
            return "seed_flower"
        return "attention_lens"
    
    # Explosions (shots 12-17)
    if idx < 17:
        if "capacity" in t or "branch" in t:
            return "capacity_branches"
        if "species" in t or "unfold" in t:
            return "species_unfold"
        if "trace" in t or "invisible" in t or "visible" in t:
            return "invisible_trace"
        return "burst_constellation"
    
    # Dream becomes flesh (shots 17-23)
    if idx < 23:
        if "dream" in t or "membrane" in t:
            return "dream_membrane"
        if "inside" in t or "out" in t:
            return "inside_out"
        if "intensity" in t or "crystal" in t:
            return "intensity_crystal"
        if "flesh" in t or "emerged" in t or "physical" in t:
            return "dream_flesh"
        if "land" in t or "settl" in t:
            return "settling"
        return "dream_membrane"
    
    # CU/EE (shots 23-32)
    if idx < 32:
        if "cu" in t or "unit" in t or "consciousness" in t:
            return "cu_pulse"
        if "spark" in t or "desire" in t or "explosive" in t:
            return "desire_spark"
        if "ee" in t or "transition" in t:
            return "ee_transition"
        if "field" in t or "wave" in t or "particle" in t:
            return "wave_field_particle"
        if "cascade" in t or "atom" in t or "molecule" in t or "cell" in t:
            return "matter_cascade"
        return "cu_pulse"
    
    # Everywhere / Space / Ocean (shots 32-41)
    if idx < 41:
        if "everywhere" in t or "grid" in t or "position" in t:
            return "everywhere_grid"
        if "simultaneous" in t or "time" in t:
            return "simultaneous_times"
        if "building" in t or "block" in t:
            return "building_blocks"
        if "space" in t or "manifest" in t:
            return "space_manifest"
        if "ocean" in t or "focus" in t:
            return "ocean_focus"
        return "everywhere_grid"
    
    # Value fulfillment (shots 41-51)
    if idx < 51:
        if "value" in t or "seed" in t:
            return "value_seed"
        if "love" in t or "presence" in t:
            return "loving_field"
        if "variant" in t or "infinite" in t or "potential" in t:
            return "infinite_variants"
        if "mutual" in t or "enhance" in t or "each" in t:
            return "mutual_enhancement"
        if "quality" in t or "rise" in t:
            return "quality_rise"
        return "value_seed"
    
    # Cooperation (shots 51-57)
    if idx < 57:
        if "network" in t or "species" in t:
            return "species_network"
        if "cooperation" in t or "hidden" in t:
            return "hidden_cooperation"
        if "competition" in t or "veil" in t or "belief" in t:
            return "competition_veil"
        if "cosmos" in t or "venture" in t:
            return "cooperative_cosmos"
        return "hidden_cooperation"
    
    # Belief/Body (shots 57-64)
    if idx < 64:
        if "commonwealth" in t or "body" in t:
            return "body_commonwealth"
        if "cell" in t or "role" in t:
            return "cell_roles"
        if "birth" in t or "lattice" in t:
            return "birth_lattice"
        if "thought" in t or "loop" in t:
            return "thought_body_loop"
        if "heredity" in t or "suggestion" in t:
            return "heredity_suggestion"
        if "motivation" in t or "illness" in t:
            return "motivation_loop"
        if "belief" in t or "release" in t:
            return "belief_release"
        return "body_commonwealth"
    
    # Choice (shots 64+)
    if "story" in t or "choice" in t or "frame" in t:
        return "two_stories"
    if "chance" in t or "molecule" in t:
        return "chance_molecules"
    if "chosen" in t or "embodiment" in t:
        return "chosen_embodiment"
    if "dream" in t or "choose" in t:
        return "dream_choice"
    return "two_stories"

# ── 5. BUILD STORYBOARD ─────────────────────────────────────
shots = []
current_time = 0.0
prev_chapter = ""

chapters_order = [
    (0, "opening", "Prologue"), (3, "spacious_present", "I. The Spacious Present"),
    (12, "explosions", "II. Explosions of Consciousness"), (17, "dream_flesh", "III. The Dream Becomes Flesh"),
    (23, "cu_ee", "IV. Intention Materializes"), (32, "everywhere", "V. Everywhere at Once"),
    (41, "value_fulfillment", "VI. Value Fulfillment"), (51, "cooperative", "VII. The Cooperative Venture"),
    (57, "cellular", "VIII. The Body as Commonwealth"), (64, "belief_body", "IX. Belief and the Body"),
    (70, "choice", "X. Two Stories"),
]

# Track which motifs we've seen for variant assignment
motif_variants = {}

for i, text in enumerate(shot_texts):
    words = len(text.split())
    dur = max(5.0, min(9.5, round(words / 2.8, 1)))
    
    # Chapter
    chapter_id = "opening"
    chapter_title = "Prologue"
    for start, cid, ctitle in reversed(chapters_order):
        if i >= start:
            chapter_id, chapter_title = cid, ctitle
            break
    
    first_in = chapter_id != prev_chapter
    prev_chapter = chapter_id
    
    # Motif
    motif = assign_motif(text, i, len(shot_texts))
    motif_variants[motif] = motif_variants.get(motif, 0) + 1
    variant_num = motif_variants[motif]
    
    shot = {
        "shot_id": f"shot_{i+1:03d}",
        "chapter": chapter_id,
        "chapter_title": chapter_title,
        "source_kind": "essay_prose",
        "spoken_text": text,
        "start_seconds": round(current_time, 3),
        "end_seconds": round(current_time + dur, 3),
        "duration_seconds": round(dur, 3),
        "motif": motif,
        "variant": variant_num,
        "visual_mechanism": motif.replace("_", " "),
        "background_justification": "Ivory field sustains one imaginal world; umber, gold, lapis, crimson distinguish form, consciousness, depth and life without resetting the world.",
        "transition": f"fade to shared field at audio boundary",
        "continuity_object": "a small gold consciousness-seed remains throughout",
        "caption_restrictions": "No sentence subtitles; chapter headings only",
        "first_in_chapter": first_in,
    }
    shots.append(shot)
    current_time += dur

# ── 6. VALIDATE AGAINST PLATINUM METRICS ────────────────────
total_shots = len(shots)
total_dur = sum(s['duration_seconds'] for s in shots)
avg_dur = total_dur / total_shots
motif_counts = {}
for s in shots:
    motif_counts[s['motif']] = motif_counts.get(s['motif'], 0) + 1

print(f"\n=== PRE-PRODUCTION VALIDATION ===")
print(f"Shots:       {total_shots} (platinum: 75)")
print(f"Duration:    {total_dur:.0f}s ({total_dur/60:.1f} min) (platinum: 456s / 7.6 min)")
print(f"Avg shot:    {avg_dur:.1f}s (platinum: 6.1s)")
print(f"Min shot:    {min(s['duration_seconds'] for s in shots):.1f}s (platinum: 5.2s)")
print(f"Max shot:    {max(s['duration_seconds'] for s in shots):.1f}s (platinum: 9.4s)")
print(f"Motifs:      {len(motif_counts)} (platinum: 45)")
print(f"Chapters:    {len(set(s['chapter'] for s in shots))} (platinum: 11)")
print()

# Check motif reuse pattern
reuse_1 = [m for m, c in motif_counts.items() if c == 1]
reuse_2 = [m for m, c in motif_counts.items() if c == 2]
reuse_3 = [m for m, c in motif_counts.items() if c >= 3]
print(f"Motifs used once:  {len(reuse_1)} (platinum has many singles)")
print(f"Motifs used twice: {len(reuse_2)} (platinum pattern)")
print(f"Motifs used 3+ times: {len(reuse_3)}")

# ── 7. SAVE ─────────────────────────────────────────────────
with open(os.path.join(OUT, "storyboard.json"), "w") as f:
    json.dump(shots, f, indent=2, ensure_ascii=False)

# Visual program
vp = {
    "film_id": "expansion-essay34-you-existed-before-earth",
    "title": "You Existed Before the Earth",
    "source_script": "scripts/expansion-essay34.md",
    "continuity_systems": visual_thesis["recurring_systems"],
    "chapters": [{"id":cid, "title":ct} for _,cid,ct in chapters_order],
    "palette": visual_thesis["palette"],
    "entities": [
        {"id":"field","archetype":"field","continuity":"persistent"},
        {"id":"seed","archetype":"point","continuity":"grows_and_returns"},
        {"id":"network","archetype":"web","continuity":"intensifies"},
    ],
    "operators": visual_thesis["motion_world"],
}
with open(os.path.join(OUT, "visual_program.json"), "w") as f:
    json.dump(vp, f, indent=2, ensure_ascii=False)

print(f"\nFiles saved to: {OUT}")
print(f"  narration_script.txt ({len(narration.split())} words)")
print(f"  storyboard.json ({total_shots} shots)")
print(f"  visual_program.json")
print(f"  visual_thesis.json")
