"""Spanda v5 — semantic concept→function matching. Clean version."""
import sys, os, json, math, re, asyncio, wave, subprocess

sys.path.insert(0, '/root/projects/blog/scripts/renderer')
from renderer import *
FPS = 6
OUT = '/root/projects/blog/content/publishing/renders/spanda-v5'
os.makedirs(OUT, exist_ok=True)

# ── CONCEPT→FUNCTION MAP ──────────────────────────────────
CONCEPT_MAP = {
    "hidden pulse": "s_hook", "spanda": "s_hook", "fundamental": "s_hook",
    "substrate": "s_hook", "flicker": "s_hook",
    "wheel": "s_wheel", "hub": "s_wheel", "spokes": "s_wheel",
    "dissolution": "s_wheel", "wheel of powers": "s_wheel",
    "six names": "s_six", "six": "s_six", "names": "s_six",
    "vitality": "s_six", "pranana": "s_six",
    "mantra": "s_mantra", "syllable": "s_mantra", "seed": "s_mantra",
    "breath": "s_mantra", "breathe": "s_mantra",
    "perception": "s_perception", "unmesha": "s_perception",
    "nimesha": "s_perception", "opening": "s_perception",
    "closing": "s_perception", "senses": "s_perception",
    "throb": "s_throb", "fish": "s_throb", "belly": "s_throb",
    "pulse": "s_throb", "riverbank": "s_throb",
    "chain": "s_chain", "cascade": "s_chain", "void": "s_chain",
    "link": "s_chain", "middle": "s_chain",
    "play": "s_play", "dance": "s_play", "joy": "s_play",
    "krida": "s_play", "wonder": "s_play", "camatkara": "s_play",
    "recognition": "s_recog", "recognize": "s_recog",
    "know yourself": "s_recog", "awake": "s_recog",
    "expansion": "s_close", "bliss": "s_close", "fully": "s_close",
    "liberated": "s_close", "sixth": "s_close",
    "light": "scene_light_darkness", "dark": "scene_light_darkness",
    "radiance": "scene_light_darkness",
    "wave": "scene_light_wave", "ocean": "scene_light_wave",
    "dissolve": "scene_dissolution",
    "vibration": "scene_vibration", "frequency": "scene_vibration",
    "resonance": "scene_resonance", "tuning": "scene_resonance",
    "tremble": "scene_resonance",
    "inner exertion": "s01_inner_exertion",
    "centre": "s05_the_centre", "heart": "s05_the_centre",
    "cosmic": "s06_cosmic_bliss",
}

def find_function(text):
    t = text.lower()
    best_score = 0
    best_func = "s_hook"
    for concept, func in CONCEPT_MAP.items():
        if concept in t:
            overlap = len(set(concept.split()) & set(t.split()))
            score = overlap / max(len(t.split()), 1) * 100 + 30
            if score > best_score:
                best_score = score
                best_func = func
    # Also check partial word overlap
    for concept, func in CONCEPT_MAP.items():
        common = set(concept.split()) & set(t.split())
        if common:
            score = len(common) / max(len(t.split()), 1) * 100
            if score > best_score:
                best_score = score
                best_func = func
    return best_func

# ── CLEAN NARRATION ────────────────────────────────────────
text = open('/root/projects/blog/scripts/expansion-essay1.md').read()
lines = text.split('\n')
clean = []
for line in lines:
    line = line.strip()
    if line.startswith('#') or line.startswith('---') or line.startswith('>*'):
        continue
    if line.startswith('>'):
        clean.append(line.lstrip('> '))
    elif line:
        clean.append(line)
narration = ' '.join(clean)

# Split into sentences
sentences = re.split(r'(?<=[.!?])\s+', narration)
shots_text = []
for s in sentences:
    s = s.strip()
    if not s or len(s.split()) < 3:
        continue
    if len(s.split()) > 15:
        parts = re.split(r'(?:;\s|,\s*(?:and|but|the|when|where|which|that|because)\s)', s)
        shots_text.extend([p.strip() for p in parts if p.strip() and len(p.strip().split()) > 2])
    else:
        shots_text.append(s)

# Combine very short adjacent shots
combined = []
i = 0
while i < len(shots_text):
    if len(shots_text[i].split()) < 4 and i+1 < len(shots_text):
        combined.append(shots_text[i] + " " + shots_text[i+1])
        i += 2
    else:
        combined.append(shots_text[i])
        i += 1
shots_text = combined

print(f"Essay: {len(narration.split())} words → {len(shots_text)} shots")

# ── GENERATE WAVs ──────────────────────────────────────────
async def gen_wavs():
    import edge_tts
    for i, text in enumerate(shots_text):
        path = os.path.join(OUT, f"s{i+1:03d}.wav")
        if not os.path.exists(path) or os.path.getsize(path) < 1000:
            await edge_tts.Communicate(text, "en-US-AriaNeural").save(path)

asyncio.run(gen_wavs())

def wav_dur(path):
    try:
        with wave.open(path) as w:
            return w.getnframes() / w.getframerate()
    except:
        return 4.0

durations = [max(3.5, min(12, round(wav_dur(os.path.join(OUT, f"s{i+1:03d}.wav")), 1))) for i in range(len(shots_text))]
print(f"Total: {sum(durations):.0f}s ({sum(durations)/60:.1f} min), avg {sum(durations)/len(durations):.1f}s")

# ── BUILD STORYBOARD ───────────────────────────────────────
chapters = [
    (0, "hook", "The Hidden Pulse"), (10, "wheel", "Wheel of Powers"),
    (22, "six", "Six Names"), (34, "mantra", "Mantra as Pulse"),
    (46, "eye", "Perception as Pulse"), (56, "resonance", "Resonance"),
    (65, "throb", "Belly of the Fish"), (75, "chain", "The Chain"),
    (86, "drum", "The Drum"), (95, "ocean", "Waves of One Pulse"),
    (104, "play", "Play"), (112, "recog", "Recognition"),
]

shots_meta = []
for i, text in enumerate(shots_text):
    ch = max((s for s in chapters if i >= s[0]), key=lambda x: x[0])
    shots_meta.append({
        "text": text, "dur": durations[i], "func": find_function(text),
        "ch": ch[1], "ch_title": ch[2], "ch_start": i == ch[0],
    })

existing = sum(1 for s in shots_meta if s["func"] != "s_hook")
new_funcs = sum(1 for s in shots_meta if s["func"] == "s_hook")
print(f"Existing matches: {existing}, s_hook fallback: {new_funcs}")

# ── SCENE FUNCTIONS ────────────────────────────────────────
from spanda_scenes import s_hook as fn_hook, s_wheel as fn_wheel, s_six as fn_six
from spanda_scenes import s_mantra as fn_mantra, s_perception as fn_eye
from spanda_scenes import s_throb as fn_throb, s_chain as fn_chain
from spanda_scenes import s_play as fn_play, s_recog as fn_recog, s_close as fn_close

FUNCTIONS = {
    "s_hook": fn_hook, "s_wheel": fn_wheel, "s_six": fn_six,
    "s_mantra": fn_mantra, "s_perception": fn_eye, "s_throb": fn_throb,
    "s_chain": fn_chain, "s_play": fn_play, "s_recog": fn_recog,
    "s_close": fn_close,
}

# ── NEW CONCEPT DIAGRAMS ───────────────────────────────────
def diagram_noticing(t, u, idx):
    """A field of faint dots with one bright center — noticing."""
    im = canvas(DARK); d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    for i in range(30):
        ang = i*0.209 + t*0.1; r = 60+i*6
        dot(d, cx+r*math.cos(ang), cy+r*math.sin(ang), 2, MUTED, 0.15)
    dot(d, cx, cy, 6+2*math.sin(t*0.8), GOLD, smoothstep(0.3,0.7,u))
    return im

def diagram_tradition(t, u, idx):
    """Lineage transmission — connected nodes."""
    im = canvas(DARK); d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    nodes = [(cx-120,250),(cx+80,280),(cx-60,420),(cx+100,440),(cx,540)]
    for j,(nx,ny) in enumerate(nodes):
        a = smoothstep(0.1+j*0.08,0.3+j*0.08,u)*0.7
        if a > 0:
            dot(d,nx,ny,5,GOLD,a)
            if j>0: d.line([nodes[j-1],(nx,ny)],fill=rgba(GOLD,a*0.4),width=1)
    dot(d,cx,200,7,GOLD,smoothstep(0,0.3,u))
    return im

def diagram_speaking(t, u, idx):
    """Sound waves from mouth-like aperture."""
    im = canvas(DARK); d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    d.ellipse((cx-15,cy-5,cx+15,cy+5),outline=rgba(GOLD,0.6),width=2)
    for i in range(4):
        ring(d,cx,cy,25+i*20+5*math.sin(t*3+i),GOLD,max(0,0.3-i*0.06),1)
    return im

def diagram_tuning_fork(t, u, idx):
    """Two forks — struck and resonating — with waves."""
    im = canvas(DARK); d = ImageDraw.Draw(im)
    lx, rx = 500, 780
    for x,y1,y2 in [(lx,280,440),(lx+20,280,440)]:
        d.line([(x,y1),(x,y2)],fill=GOLD,width=3)
    d.arc((lx-25,270,lx+25,300),0,180,fill=GOLD,width=2)
    rx_amp = 1+0.04*math.sin(t*3)*smoothstep(0.3,0.8,u)
    for x,y1,y2 in [(rx-20*rx_amp,280,440),(rx+20*rx_amp,280,440)]:
        d.line([(x,y1),(x,y2)],fill=GOLD,width=3)
    d.arc((rx-25,270,rx+25,300),0,180,fill=GOLD,width=2)
    for x in range(lx+30,rx-30,6):
        dot(d,x,360+20*math.sin((x-lx)*0.08+t*4),2,GOLD,0.3)
    return im

NEW_FUNCS = {
    "diagram_noticing": diagram_noticing,
    "diagram_tradition": diagram_tradition,
    "diagram_speaking": diagram_speaking,
    "diagram_tuning_fork": diagram_tuning_fork,
}

def get_fn(shot):
    fname = shot["func"]
    if fname in FUNCTIONS:
        return FUNCTIONS[fname], f"existing:{fname}"
    return diagram_noticing, "new:noticing"

# ── RENDER ─────────────────────────────────────────────────
print(f"\nRendering {len(shots_meta)} shots...")
for i, s in enumerate(shots_meta):
    sid = f"s{i+1:03d}"
    dur = s["dur"]
    fn, label = get_fn(s)
    sd = os.path.join(OUT, sid)
    os.makedirs(sd, exist_ok=True)
    frames = max(1, int(dur*FPS))
    for fi in range(frames):
        fn(fi/FPS, fi/frames if frames>1 else 1, i).save(os.path.join(sd, f"frame_{fi:05d}.png"))
    if i % 20 == 0:
        print(f"  [{i}/{len(shots_meta)}] {sid}: {frames}fr {dur:.0f}s [{label}]")

# ── ASSEMBLE ───────────────────────────────────────────────
print(f"\nAssembling...")
with open(os.path.join(OUT,"c.txt"),"w") as f:
    for i,s in enumerate(shots_meta):
        sid = f"s{i+1:03d}"
        mp4 = os.path.join(OUT,f"{sid}.mp4")
        sd = os.path.join(OUT,sid)
        subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',f'{sd}/frame_%05d.png',
            '-c:v','libx264','-pix_fmt','yuv420p','-preset','ultrafast','-crf','28',
            '-t',str(s["dur"]),mp4],capture_output=True)
        f.write(f"file '{mp4}'\n")

subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',os.path.join(OUT,'c.txt'),
    '-c','copy',os.path.join(OUT,'draft.mp4')],capture_output=True)

with open(os.path.join(OUT,"ac.txt"),"w") as f:
    for i in range(len(shots_meta)):
        w = os.path.join(OUT,f"s{i+1:03d}.wav")
        if os.path.exists(w): f.write(f"file '{w}'\n")

if os.path.exists(os.path.join(OUT,"ac.txt")):
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',os.path.join(OUT,'ac.txt'),
        '-c','copy',os.path.join(OUT,'full_audio.wav')],capture_output=True)
    subprocess.run(['ffmpeg','-y','-i',os.path.join(OUT,'draft.mp4'),
        '-i',os.path.join(OUT,'full_audio.wav'),
        '-c:v','copy','-c:a','aac','-map','0:v:0','-map','1:a:0','-shortest',
        os.path.join(OUT,'final.mp4')],capture_output=True)
    sz = os.path.getsize(os.path.join(OUT,'final.mp4'))
    print(f"Final MP4: {sz/1024:.0f} KB")

print("Done.")
