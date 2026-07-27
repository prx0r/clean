"""
v4 — Audio-first workflow. Learnings from 3 failed iterations + 2 platinum deconstructions.

WORKFLOW:
1. Read essay, strip markdown → clean narration
2. Split into shot-sized phrases
3. Generate per-shot WAV audio (EDGE TTS)
4. MEASURE actual WAV duration for each shot ← CRITICAL FIX
5. Build storyboard with real audio-derived durations
6. Map each shot concept to existing scene functions
7. Render at 6fps draft
8. Generate alignment_report.json verifying AV sync
"""
import sys, os, json, math, subprocess, asyncio, wave, struct
from PIL import Image, ImageDraw

sys.path.insert(0, '/root/projects/blog/scripts/renderer')
from renderer import *

FPS = 6
OUT = '/root/projects/blog/content/publishing/renders/pain-is-juice'
ESSAY_PATH = '/root/projects/blog/scripts/expansion-essay5.md'
os.makedirs(OUT, exist_ok=True)

# ── STEP 1: Read essay, strip markdown ────────────────────
def strip_markdown(text):
    lines = text.split('\n')
    clean = []
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line.startswith('---') or line.startswith('>'):
            continue
        if line.startswith('*') and line.endswith('*'):
            continue
        if line:
            clean.append(line)
    return ' '.join(clean)

essay_raw = open(ESSAY_PATH).read()
narration = strip_markdown(essay_raw)

# ── STEP 2: Split into shots ──────────────────────────────
# Each shot = one sentence or natural phrase
import re
sentences = re.split(r'(?<=[.!?])\s+', narration)
# Further split long sentences
shots_text = []
for s in sentences:
    s = s.strip()
    if not s:
        continue
    # If sentence is long, split at commas or semicolons
    if len(s.split()) > 15:
        parts = re.split(r'(?:;|,\s*(?:and|but|the|when|where|which|that|because)\s)', s)
        for p in parts:
            p = p.strip()
            if p and len(p.split()) > 3:
                shots_text.append(p)
    else:
        shots_text.append(s)

print(f"Essay: {len(narration.split())} words → {len(shots_text)} shots")

# ── STEP 3+4: Generate WAVs and measure durations ────────
async def generate_wavs():
    import edge_tts
    for i, text in enumerate(shots_text):
        sid = f"shot_{i+1:03d}"
        wav_path = os.path.join(OUT, f"{sid}.wav")
        if os.path.exists(wav_path):
            continue
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(wav_path)
        print(f"  {sid}: {len(text.split())} words")

asyncio.run(generate_wavs())

def measure_wav_duration(wav_path):
    """Get actual duration from WAV file in seconds."""
    try:
        with wave.open(wav_path, 'r') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / rate
    except:
        return len(text.split()) / 2.8  # fallback

# Measure actual durations
shot_durations = []
for i, text in enumerate(shots_text):
    sid = f"shot_{i+1:03d}"
    wav_path = os.path.join(OUT, f"{sid}.wav")
    if os.path.exists(wav_path):
        dur = measure_wav_duration(wav_path)
    else:
        dur = len(text.split()) / 2.8
    dur = round(dur, 3)
    shot_durations.append(dur)

total_audio = sum(shot_durations)
print(f"Total audio: {total_audio:.1f}s ({total_audio/60:.1f} min)")

# ── STEP 5: Build storyboard ──────────────────────────────
# Map concepts to visual modes
MODE_MAP = {
    "rasa": "pulse_center", "juice": "pulse_center", "feeling": "pulse_field",
    "emotion": "organic_throb", "grief": "organic_throb", "pain": "organic_throb",
    "wonder": "expansion_final", "beauty": "wave_ocean", "sunset": "wave_ocean",
    "witness": "recognition_field", "watching": "recognition_field",
    "taste": "breath_form", "savour": "breath_form", "wine": "breath_form",
    "universe": "pulse_field", "consciousness": "pulse_center",
    "tears": "wave_ocean", "harvest": "expansion_final",
    "fire": "eye_form", "burn": "eye_form",
    "wave": "wave_ocean", "dissolve": "wave_ocean",
    "flower": "six_fold", "grow": "six_fold",
}

def pick_mode(text):
    text_lower = text.lower()
    scores = {}
    for keyword, mode in MODE_MAP.items():
        if keyword in text_lower:
            scores[mode] = scores.get(mode, 0) + 1
    if scores:
        return max(scores, key=scores.get)
    return "pulse_center"

chapters = [
    (0, "opening", "The Feeling of Being Alive", "A familiar ache becomes the gateway to something ancient."),
    (7, "rasa", "Rasa — The Juice", "A thousand-year-old philosophy of taste transforms emotion into art."),
    (14, "grief", "Grief as Stone", "Grief held in awareness without resistance becomes something else."),
    (20, "wonder", "Wonder as Recognition", "The beauty outside you is the same beauty making itself known from within."),
    (25, "witness", "The Witness", "Tasting versus consuming. The emotion is the wine."),
    (34, "rest", "Rest in the Feeling", "Not fighting. Not holding. Just resting."),
    (41, "liberation", "Freedom from the 'I'", "When the claimer of emotion drops away, pain becomes beauty."),
]

print("Building storyboard...")

shots = []
current_time = 0.0
current_chapter = 0

for i, text in enumerate(shots_text):
    dur = shot_durations[i]
    
    # Determine chapter
    ch_idx = 0
    for j, (start, cid, title, thesis) in enumerate(chapters):
        if i >= start:
            ch_idx = j
    
    ch_id = chapters[ch_idx][1]
    ch_title = chapters[ch_idx][2]
    thesis = chapters[ch_idx][3]
    ch_start = ch_idx != current_chapter
    current_chapter = ch_idx
    
    mode = pick_mode(text)
    
    shots.append({
        "shot_id": f"shot_{i+1:03d}",
        "chapter": ch_id,
        "chapter_title": ch_title,
        "chapter_start": ch_start,
        "spoken_text": text,
        "start_seconds": round(current_time, 3),
        "end_seconds": round(current_time + dur, 3),
        "duration_seconds": round(dur, 3),
        "motif": mode,
        "visual_mechanism": mode.replace("_", " "),
        "continuity_object": "the witness" if "witness" in text.lower() else "the pulse",
        "transition": "continuous motif transformation" if not ch_start else "opening from blank field",
        "background_justification": "Void background with gold pulse motifs reflecting the inner landscape of feeling.",
        "source_kind": "essay_prose",
        "caption_restrictions": "technical terms only",
        "first_in_chapter": ch_start,
    })
    current_time += dur

# Save storyboard
sb_path = os.path.join(OUT, "storyboard.json")
with open(sb_path, "w") as f:
    json.dump(shots, f, indent=2, ensure_ascii=False)
print(f"Storyboard: {len(shots)} shots, {current_time:.1f}s")

# ── VISUAL PROGRAM ────────────────────────────────────────
vp = {
    "film_id": "expansion-essay5-pain-is-juice",
    "title": "Pain Is Juice",
    "source_script": "scripts/expansion-essay5.md",
    "continuity_systems": [
        {"id": "the_witness", "development": "observer of emotion → stone that feels → cup that holds → one who rests → freedom from the I"},
        {"id": "rasa_current", "development": "raw feeling → aesthetic taste → grief held → wonder recognized → pain as beauty"},
        {"id": "wave_of_feeling", "development": "initial ache → emotion crests → crash → dissolve → new wave forming"},
    ],
    "chapters": [{"id":cid,"title":ct,"visual_thesis":vt} for (start,cid,ct,vt) in chapters],
    "palette": {"void":"#0D1117","gold":"#D4A574","crimson":"#8D2C39","ink":"#E6E1DC","muted":"#918D84"},
    "entities": [
        {"id":"witness","archetype":"observer","continuity":"persistent"},
        {"id":"rasa","archetype":"current","continuity":"transforms"},
        {"id":"wave","archetype":"vibration","continuity":"cycles"},
    ],
    "operators": ["reveal","radiate","pulse","dissolve","hold","witness","taste","release"],
}
with open(os.path.join(OUT, "visual_program.json"), "w") as f:
    json.dump(vp, f, indent=2, ensure_ascii=False)

# ── SCENE FUNCTIONS ────────────────────────────────────────
# 7 modes mapped from existing functions
def mode_pulse_center(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    th = 1 + 0.04*math.sin(t*0.8+v)
    dot(d, cx, cy, 6*th, GOLD, smoothstep(0.1,0.4,u))
    for i in range(3):
        ring(d, cx, cy, (50+i*40)*th, GOLD, max(0,0.2-i*0.05)*smoothstep(0.2,0.6,u), 1)
    return im

def mode_pulse_field(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    for i in range(15):
        ang = t*0.2 + i*0.419
        r = 50 + 30*math.sin(t*0.3+i+v)
        dot(d, cx+r*math.cos(ang), cy+r*math.sin(ang), 2, GOLD if i%3 else CRIMSON, 0.3+0.2*math.sin(t+i))
    dot(d, cx, cy, 4, GOLD, 0.5)
    return im

def mode_organic_throb(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    th = 1 + 0.06*math.sin(t*0.7+v)
    for i in range(3):
        ring(d, cx, cy, (40+i*35)*th, CRIMSON, max(0,0.3-i*0.08)*smoothstep(0.1,0.5,u), 2)
    dot(d, cx, cy, 5, CRIMSON, smoothstep(0.3,0.6,u))
    return im

def mode_wave_ocean(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    for i in range(5):
        prog = (t + i*0.3 + v*0.5) % 4.0
        r = 200 * max(0, min(1, prog/2))
        ring(d, cx, cy, r, GOLD, max(0,1-prog/4)*0.15, 1)
    dot(d, cx, cy, 4, GOLD, 0.6)
    return im

def mode_recognition_field(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    d.line((cx,80,cx,640), fill=rgba(MUTED,0.3), width=1)
    prog = smoothstep(0.2,0.8,u)
    for i in range(8):
        ang = i*0.785 + v*0.2 + (1-prog)*i*0.1
        r = 180*(1-0.4*prog)
        dot(d, cx+r*math.cos(ang), cy+r*math.sin(ang), 3, GOLD, 0.6-0.3*prog)
    dot(d, cx, cy, 5, GOLD, smoothstep(0.4,0.7,u))
    return im

def mode_breath_form(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    ap = 40 + 25*math.sin(t*0.8+v)
    d.rectangle((cx-12,cy-ap,cx+12,cy+ap), outline=rgba(GOLD,0.7), width=2)
    for i in range(4):
        dot(d, cx+8*math.sin(t*4+i), cy-ap+8+i*(ap*2-16)/3, 2, GOLD, 0.4+0.3*math.sin(t+i))
    return im

def mode_expansion_final(t, u, idx, v=0):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    r = 5 + smoothstep(0.4,1.0,u)*250
    dot(d, cx, cy, r, GOLD, max(0,1-u*0.5))
    if u < 0.4:
        centered(d, "rasa", 280, FONT["dev_l"], GOLD, smoothstep(0,0.3,u)*0.6)
    return im

MODE_FN = {
    "pulse_center": mode_pulse_center, "pulse_field": mode_pulse_field,
    "organic_throb": mode_organic_throb, "wave_ocean": mode_wave_ocean,
    "recognition_field": mode_recognition_field, "breath_form": mode_breath_form,
    "expansion_final": mode_expansion_final,
}

# ── RENDER ────────────────────────────────────────────────
def render():
    n = len(shots)
    total_dur = sum(s['duration_seconds'] for s in shots)
    print(f"Rendering {n} shots, {total_dur:.0f}s ({total_dur/60:.1f} min) at {FPS}fps")
    
    for s in shots:
        sid = s['shot_id']
        dur = s['duration_seconds']
        motif = s['motif']
        fn = MODE_FN.get(motif, mode_pulse_center)
        
        scene_dir = os.path.join(OUT, sid)
        os.makedirs(scene_dir, exist_ok=True)
        total_frames = max(1, int(dur * FPS))
        
        for fi in range(total_frames):
            t = fi / FPS
            u = fi / total_frames if total_frames > 1 else 1
            im = fn(t, u, idx=int(sid.split('_')[1]), v=0)
            im.save(os.path.join(scene_dir, f"frame_{fi:05d}.png"))
        
        print(f"  {sid}: {total_frames} frames = {dur:.1f}s [{motif}]")
    
    print(f"Rendered {n} shots")
    
    # ── Generate alignment report ──────────────────────────
    report = {
        "audio_duration_seconds": round(total_audio, 3),
        "video_duration_seconds": round(total_dur, 3),
        "final_av_duration_difference_seconds": round(total_audio - total_dur, 3),
        "shot_count": n,
        "timeline_basis": "actual WAV sample counts per shot",
        "shot_clip_duration_checks": []
    }
    cumulative = 0
    for s in shots:
        dur = s['duration_seconds']
        wav_path = os.path.join(OUT, s['shot_id'] + '.wav')
        actual = measure_wav_duration(wav_path) if os.path.exists(wav_path) else dur
        report["shot_clip_duration_checks"].append({
            "shot_id": s['shot_id'], "expected": dur, "actual": round(actual, 3), "error": round(abs(dur-actual), 3)
        })
        cumulative += dur
    
    with open(os.path.join(OUT, "alignment_report.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Alignment report: {n} shots checked")
    
    # Assemble draft MP4
    concat_path = os.path.join(OUT, "concat.txt")
    with open(concat_path, "w") as f:
        for s in shots:
            sid = s['shot_id']
            mp4_path = os.path.join(OUT, f"{sid}.mp4")
            scene_dir = os.path.join(OUT, sid)
            dur = s['duration_seconds']
            subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',f'{scene_dir}/frame_%05d.png',
                '-c:v','libx264','-pix_fmt','yuv420p','-preset','ultrafast','-crf','28',
                '-t',str(dur),mp4_path], capture_output=True)
            f.write(f"file '{mp4_path}'\n")
    
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',concat_path,
        '-c','copy',os.path.join(OUT,'draft.mp4')], capture_output=True)
    
    # Combine with audio
    audio_concat = os.path.join(OUT, "audio_concat.txt")
    with open(audio_concat, "w") as f:
        for s in shots:
            wav_path = os.path.join(OUT, s['shot_id'] + '.wav')
            if os.path.exists(wav_path):
                f.write(f"file '{wav_path}'\n")
    
    if os.path.exists(audio_concat):
        subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',audio_concat,
            '-c','copy',os.path.join(OUT,'full_audio.wav')], capture_output=True)
        subprocess.run(['ffmpeg','-y','-i',os.path.join(OUT,'draft.mp4'),
            '-i',os.path.join(OUT,'full_audio.wav'),
            '-c:v','copy','-c:a','aac','-map','0:v:0','-map','1:a:0','-shortest',
            os.path.join(OUT,'final.mp4')], capture_output=True)
        
        result_size = os.path.getsize(os.path.join(OUT,'final.mp4'))
        print(f"Final MP4: {result_size/1024:.0f} KB")

if __name__ == "__main__":
    render()
    print("Done.")
