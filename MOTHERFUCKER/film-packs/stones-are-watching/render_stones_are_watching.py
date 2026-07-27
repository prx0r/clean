
from pathlib import Path
import re, math, json, csv, random, shutil, subprocess, wave, zipfile, textwrap
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

ROOT = Path("/mnt/data/stones_are_watching_film_pack")
ROOT.mkdir(parents=True, exist_ok=True)
AUDIO_RAW = ROOT / "audio_raw"
AUDIO_PAD = ROOT / "audio_padded"
VISUAL_DIR = ROOT / "visual_drafts"
SHOT_DIR = ROOT / "shots"
TEMP = ROOT / "temp"
for p in [AUDIO_RAW, AUDIO_PAD, VISUAL_DIR, SHOT_DIR, TEMP]:
    p.mkdir(exist_ok=True)

W, H = 1280, 720
DRAFT_FPS = 8
FINAL_FPS = 24
MIN_DUR = 5.15
MAX_DUR = 9.75
VOICE_SPEED = 145

BG = (244, 238, 225)
INK = (35, 29, 25)
UMBER = (83, 61, 45)
GOLD = (174, 132, 48)
CRIMSON = (126, 39, 49)
LAPIS = (48, 70, 106)
GREEN = (61, 91, 72)
SILVER = (157, 162, 165)
PALE = (221, 211, 193)
WHITE = (251, 248, 240)
BLACK = (20, 18, 18)
WATER = (85, 115, 136)
EARTH = (114, 80, 54)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
TITLE = ImageFont.truetype(FONT_PATH, 28) if FONT_PATH else ImageFont.load_default()
SMALL = ImageFont.truetype(FONT_PATH, 16) if FONT_PATH else ImageFont.load_default()
TINY = ImageFont.truetype(FONT_PATH, 13) if FONT_PATH else ImageFont.load_default()

SOURCE = (ROOT / "source_essay.md").read_text(encoding="utf-8")

def clean_script(md: str) -> str:
    lines = []
    for line in md.splitlines():
        s = line.strip()
        if not s or s == "---":
            continue
        if s.startswith("# "):
            continue
        if s.startswith(">"):
            s = s[1:].strip()
        s = re.sub(r"\*([^*]+)\*", r"\1", s)
        s = re.sub(r"`([^`]+)`", r"\1", s)
        lines.append(s)
    return "\n\n".join(lines)

SCRIPT = clean_script(SOURCE)
(ROOT / "narration_script.txt").write_text(SCRIPT + "\n", encoding="utf-8")

def split_sentences(text):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    out = []
    for pi, p in enumerate(paragraphs):
        # preserve punctuation; split after sentence punctuation
        parts = re.split(r'(?<=[.!?])\s+(?=(?:["“]?[A-Z0-9]))', p)
        for part in parts:
            part = part.strip()
            if part:
                out.append({"text": part, "paragraph": pi})
    return out

def split_long_piece(piece, max_words=24):
    text = piece["text"]
    words = text.split()
    if len(words) <= max_words:
        return [piece]
    # split at punctuation nearest target
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + max_words)
        if end < len(words):
            candidates = []
            for j in range(max(start+10, end-7), min(len(words), end+2)):
                if re.search(r'[,;:—]$', words[j-1]):
                    candidates.append(j)
            if candidates:
                end = min(candidates, key=lambda j: abs(j-(start+max_words)))
        chunks.append({"text": " ".join(words[start:end]), "paragraph": piece["paragraph"]})
        start = end
    return chunks

def make_provisional(text):
    pieces = []
    for s in split_sentences(text):
        pieces.extend(split_long_piece(s, 20))
    # combine very short adjacent pieces, preferably within paragraph
    merged = []
    for p in pieces:
        wc = len(p["text"].split())
        if merged and wc < 9 and merged[-1]["paragraph"] == p["paragraph"] and len((merged[-1]["text"]+" "+p["text"]).split()) <= 21:
            merged[-1]["text"] += " " + p["text"]
        else:
            merged.append(dict(p))
    return merged

def synth(text, path):
    subprocess.run(
        ["espeak", "-s", str(VOICE_SPEED), "-w", str(path), text],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def wav_duration(path):
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / wf.getframerate()

def split_mid(text):
    words = text.split()
    mid = len(words)//2
    candidates = []
    for j in range(max(7, mid-7), min(len(words)-6, mid+8)):
        if re.search(r'[,;:—.!?]["”]?$', words[j-1]):
            candidates.append(j)
    cut = min(candidates, key=lambda x: abs(x-mid)) if candidates else mid
    return " ".join(words[:cut]), " ".join(words[cut:])

def finalize_segments():
    segs = make_provisional(SCRIPT)
    changed = True
    iteration = 0
    while changed and iteration < 12:
        iteration += 1
        changed = False
        durations = []
        for i,s in enumerate(segs):
            p = TEMP / f"probe_{i:03d}.wav"
            synth(s["text"], p)
            durations.append(wav_duration(p))
        new = []
        i = 0
        while i < len(segs):
            s = segs[i]
            d = durations[i]
            if d > MAX_DUR and len(s["text"].split()) > 12:
                a,b = split_mid(s["text"])
                new.append({"text":a, "paragraph":s["paragraph"]})
                new.append({"text":b, "paragraph":s["paragraph"]})
                changed = True
                i += 1
                continue
            if d < MIN_DUR-0.4 and i+1 < len(segs):
                combined = s["text"] + " " + segs[i+1]["text"]
                probe = TEMP / "combine_probe.wav"
                synth(combined, probe)
                cd = wav_duration(probe)
                if cd <= MAX_DUR and (segs[i+1]["paragraph"] == s["paragraph"] or d < 3.5):
                    new.append({"text":combined, "paragraph":s["paragraph"]})
                    changed = True
                    i += 2
                    continue
            new.append(s)
            i += 1
        segs = new
    return segs

SEGMENTS = finalize_segments()

def ensure_audio_bounds(segs):
    out=[]
    counter=0
    for s in segs:
        queue=[dict(s)]
        while queue:
            q=queue.pop(0)
            probe=TEMP/f"bound_{counter:04d}.wav"
            counter += 1
            synth(q["text"], probe)
            d=wav_duration(probe)
            try: probe.unlink()
            except: pass
            if d > MAX_DUR and len(q["text"].split()) > 8:
                a,b=split_mid(q["text"])
                queue.insert(0,{"text":b,"paragraph":q["paragraph"]})
                queue.insert(0,{"text":a,"paragraph":q["paragraph"]})
            else:
                out.append(q)
    return out

SEGMENTS = ensure_audio_bounds(SEGMENTS)

# clean probe files
for p in TEMP.glob("probe_*.wav"):
    p.unlink()
if (TEMP/"combine_probe.wav").exists():
    (TEMP/"combine_probe.wav").unlink()

def chapter_for(text):
    t = text.lower()
    if any(k in t for k in ["13th-century bishop", "albertus magnus", "four causes"]):
        return "I. The Patient Life of Stone"
    if any(k in t for k in ["material of all stone", "earth or some form of water", "mineralizing power", "matter is alive", "world-soul"]):
        return "II. Mineralizing Intelligence"
    if any(k in t for k in ["powers of stones", "substantial form", "magnet attracts", "sapphire", "essential form"]):
        return "III. Form Is Power"
    if any(k in t for k in ["sulphur", "quicksilver", "planets determine", "piṅgalā", "iḍā", "suṣumṇā", "lapis", "spine"]):
        return "IV. The Marriage of Metals"
    if any(k in t for k in ["alphabetical lapidary", "abeston", "adamas", "agathes", "amethystus", "beryllus", "carbunculus", "smaragdus", "saphirus", "magnes", "specific contraction"]):
        return "V. The Living Lapidary"
    if any(k in t for k in ["astrological lapidary", "zodiac", "engraved", "lion on a carbuncle", "serpent on an agate", "woman with a mirror", "fixed point in the heavens", "different frequencies", "new jerusalem", "star tetrahedron"]):
        return "VI. Stone and Star"
    if any(k in t for k in ["field observations", "rhine", "elbe", "freiberg", "swabia", "cologne", "pictures on stones", "field journal"]):
        return "VII. The Bishop in the Mines"
    if any(k in t for k in ["transmute", "alchemy know", "prime matter", "artificial vessels", "alchemist creates", "heat must match"]):
        return "VIII. Art Imitates Nature"
    return "IX. The Intermediate Substance"

def mode_for(text, idx):
    t = text.lower()
    tests = [
        (["watching", "aware", "life proper to stone"], "watching_stones"),
        (["bishop", "book of minerals", "most learned"], "bishop_codex"),
        (["earth or some form of water", "sink in water", "pumice"], "earth_water"),
        (["animal's seed", "seminal", "forming an animal"], "seed_form"),
        (["mineralizing power", "formative intelligence", "world-soul"], "crystal_growth"),
        (["substantial form", "specific form itself", "essential form"], "inner_lattice"),
        (["magnet", "attracting iron"], "magnet_relation"),
        (["sapphire", "cooling"], "cooling_stone"),
        (["sulphur", "father"], "sulphur_fire"),
        (["quicksilver", "mother", "mercury"], "mercury_flow"),
        (["planets determine", "gold is the sun", "silver the moon"], "planetary_metals"),
        (["piṅgalā", "iḍā", "suṣumṇā", "spine"], "subtle_body"),
        (["lapis", "body of light", "completed metal"], "lapis_birth"),
        (["alphabetical lapidary", "twenty chapters", "catalog"], "lapidary_pages"),
        (["abeston", "asbestos", "kindled"], "eternal_fibre"),
        (["adamas", "hard stone", "pierces iron"], "adamant"),
        (["agathes", "agate", "dreams"], "dream_stone"),
        (["amethystus", "amethyst"], "amethyst_vigil"),
        (["carbunculus", "live coal"], "carbuncle_coal"),
        (["smaragdus", "emerald"], "emerald_memory"),
        (["saphirus"], "sapphire_cool"),
        (["specific contraction", "divine name made visible"], "consciousness_condenses"),
        (["engraving", "engraved", "images on specific stones"], "engraving"),
        (["lion on a carbuncle"], "lion_seal"),
        (["serpent on an agate"], "serpent_seal"),
        (["woman with a mirror"], "mirror_seal"),
        (["12 signs", "12 tribes", "12 gates", "12 edges"], "twelvefold"),
        (["stone in your hand and the star", "different frequencies"], "stone_star"),
        (["gold formed in the sands", "rhine", "elbe"], "river_gold"),
        (["silver as a sort of vein", "soft as a firm mush"], "silver_vein"),
        (["fifty serpents"], "serpent_stone"),
        (["onyx", "heads of two young men", "pictures on stones"], "onyx_faces"),
        (["field journal", "his own eyes"], "field_journal"),
        (["colour a red metal with yellow", "appear to be gold"], "false_gold"),
        (["prime matter"], "prime_matter"),
        (["natural vessels", "artificial vessels"], "twin_vessels"),
        (["heat must match the sun"], "solar_furnace"),
        (["electrum", "gold and silver"], "electrum"),
        (["salt of ammon", "sal naphticum", "indian salt", "vitriols", "alums"], "salt_crucible"),
        (["forms remain unfixed", "still becoming"], "unfixed_forms"),
        (["dissolved and coagulated"], "solve_coagula"),
        (["what you are", "intermediate substance", "what you will become"], "human_intermediate"),
        (["fire is already kindled", "vessel is prepared", "nature is waiting"], "final_vessel"),
    ]
    for keys, mode in tests:
        if any(k in t for k in keys):
            return mode
    defaults = ["watching_stones","bishop_codex","inner_lattice","crystal_growth","stone_star"]
    return defaults[idx % len(defaults)]

def continuity_for(mode):
    mapping = {
        "watching_stones":"stone-eye",
        "bishop_codex":"illuminated folio",
        "earth_water":"mineral seed",
        "seed_form":"mineral seed",
        "crystal_growth":"forming crystal",
        "inner_lattice":"substantial lattice",
        "magnet_relation":"relational line",
        "cooling_stone":"blue current",
        "sulphur_fire":"solar current",
        "mercury_flow":"lunar current",
        "planetary_metals":"sevenfold orbit",
        "subtle_body":"central axis",
        "lapis_birth":"completed stone",
        "lapidary_pages":"catalog stone",
        "eternal_fibre":"kindled thread",
        "adamant":"diamond edge",
        "dream_stone":"dream aperture",
        "amethyst_vigil":"violet watch",
        "carbuncle_coal":"living coal",
        "emerald_memory":"green eye",
        "sapphire_cool":"blue eye",
        "consciousness_condenses":"descending name",
        "engraving":"incised line",
        "lion_seal":"solar seal",
        "serpent_seal":"coiled seal",
        "mirror_seal":"reflective seal",
        "twelvefold":"twelvefold wheel",
        "stone_star":"frequency thread",
        "river_gold":"gold grain",
        "silver_vein":"metallic vein",
        "serpent_stone":"living geology",
        "onyx_faces":"natural image",
        "field_journal":"observing eye",
        "false_gold":"surface colour",
        "prime_matter":"dark substrate",
        "twin_vessels":"paired vessel",
        "solar_furnace":"measured heat",
        "electrum":"double metal",
        "salt_crucible":"unfixed salts",
        "unfixed_forms":"mutable lattice",
        "solve_coagula":"dissolving form",
        "human_intermediate":"unfinished figure",
        "final_vessel":"prepared vessel",
    }
    return mapping.get(mode, "mineral thread")

def ease(t): return 3*t*t - 2*t*t*t
def smooth(a,b,t):
    if t <= a: return 0.0
    if t >= b: return 1.0
    u=(t-a)/(b-a)
    return u*u*(3-2*u)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def circle(d,x,y,r,outline=INK,width=2,fill=None):
    d.ellipse((x-r,y-r,x+r,y+r),outline=outline,width=width,fill=fill)
def line(d,pts,fill=INK,width=2):
    d.line(pts,fill=fill,width=width)
def poly(d,pts,outline=INK,width=2,fill=None):
    d.polygon(pts,outline=outline,fill=fill)
    if outline and width>1:
        for i in range(len(pts)):
            d.line([pts[i],pts[(i+1)%len(pts)]],fill=outline,width=width)
def star(d,cx,cy,r1,r2,n=8,phase=0,outline=GOLD,width=2,fill=None):
    pts=[]
    for i in range(n*2):
        a=phase+math.pi*i/n
        r=r1 if i%2==0 else r2
        pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    poly(d,pts,outline=outline,width=width,fill=fill)
def radial(cx,cy,r,n,phase=0):
    return [(cx+r*math.cos(phase+2*math.pi*i/n),cy+r*math.sin(phase+2*math.pi*i/n)) for i in range(n)]

# stable parchment texture
rnd = random.Random(4601)
PARCH = Image.new("RGB",(W,H),BG)
pd = ImageDraw.Draw(PARCH)
for _ in range(2400):
    x=rnd.randrange(W); y=rnd.randrange(H)
    c=mix(PALE,BG,rnd.random())
    rr=1 if rnd.random()<.96 else 2
    pd.ellipse((x-rr,y-rr,x+rr,y+rr),fill=c)
for i in range(18):
    pd.rectangle((i,i,W-1-i,H-1-i),outline=mix(PALE,BG,.45),width=1)

def stone_shape(cx,cy,rx,ry,n=9,phase=0,seed=0):
    rr=random.Random(seed)
    pts=[]
    for i in range(n):
        a=phase+2*math.pi*i/n
        f=.82+.22*rr.random()
        pts.append((cx+rx*f*math.cos(a),cy+ry*f*math.sin(a)))
    return pts

def header(d, chapter, shot_id):
    d.text((48,38), chapter, fill=UMBER, font=SMALL)
    d.text((1175,40), f"{shot_id:02d}", fill=PALE, font=TINY)

def render_frame(mode,t,shot_id,chapter,text):
    im=PARCH.copy()
    d=ImageDraw.Draw(im)
    header(d,chapter,shot_id)
    cx,cy=640,365
    p=ease(t)
    pulse=.5+.5*math.sin(t*2*math.pi)

    if mode=="watching_stones":
        stones=[(310,430,120,75),(610,390,150,92),(955,440,125,80),(760,560,80,48)]
        for i,(x,y,rx,ry) in enumerate(stones):
            pts=stone_shape(x,y,rx,ry,10,seed=shot_id*10+i)
            poly(d,pts,outline=INK,width=3,fill=mix(PALE,EARTH,.28))
            # mineral eye
            if i<3:
                ex=x+10*math.sin(t*1.2+i); ey=y-8
                d.arc((ex-36,ey-17,ex+36,ey+17),195,345,fill=UMBER,width=3)
                d.arc((ex-36,ey-17,ex+36,ey+17),15,165,fill=UMBER,width=3)
                circle(d,ex,ey,6+2*pulse,fill=CRIMSON,outline=CRIMSON,width=1)
        line(d,[(120,610),(1160,610)],fill=PALE,width=2)

    elif mode=="bishop_codex":
        # Gothic codex + mitre-like arch
        d.rectangle((350,165,930,555),outline=INK,width=3,fill=WHITE)
        line(d,[(640,165),(640,555)],fill=UMBER,width=2)
        for side in [0,1]:
            x0=390+side*290
            for j in range(9):
                y=225+j*28
                line(d,[(x0,y),(x0+205-(j%3)*25,y)],fill=GREY if 'GREY' in globals() else UMBER,width=1)
        star(d,640,205,34,14,n=8,phase=t*.15,outline=GOLD,width=2)
        # four causes corners
        for i,pnt in enumerate([(410,190),(870,190),(410,520),(870,520)]):
            circle(d,*pnt,16,outline=[EARTH,WATER,GOLD,CRIMSON][i],width=2)

    elif mode=="earth_water":
        # layered earth and water womb
        d.rectangle((170,185,590,555),fill=mix(EARTH,BG,.15),outline=INK,width=2)
        d.rectangle((690,185,1110,555),fill=mix(WATER,BG,.22),outline=INK,width=2)
        # currents converge
        for k in range(7):
            y=240+k*44
            line(d,[(190,y),(520+25*math.sin(t*2+k),cy)],fill=EARTH,width=2)
            line(d,[(1090,y),(760+25*math.sin(t*2+k),cy)],fill=WATER,width=2)
        seed=stone_shape(cx,cy,80+30*p,60+18*p,9,seed=shot_id)
        poly(d,seed,outline=GOLD,width=3,fill=WHITE)
        star(d,cx,cy,28+18*p,11,n=8,phase=t*.2,outline=CRIMSON,width=2)

    elif mode=="seed_form":
        # embryo-like seed becoming crystal
        circle(d,cx,cy,145,outline=UMBER,width=3,fill=WHITE)
        for i in range(13):
            a=2*math.pi*i/13+t*.1
            r=95*(.3+.7*p)
            circle(d,cx+r*math.cos(a),cy+r*math.sin(a),7,fill=GOLD if i%3==0 else EARTH,outline=None,width=1)
        crystal=[(cx,cy-110*p),(cx+75*p,cy-30*p),(cx+52*p,cy+100*p),(cx-52*p,cy+100*p),(cx-75*p,cy-30*p)]
        poly(d,crystal,outline=CRIMSON,width=3,fill=None)

    elif mode=="crystal_growth":
        # branching mineral dendrites
        bases=[(430,540),(640,560),(850,540)]
        for bi,(bx,by) in enumerate(bases):
            line(d,[(bx,by),(bx,260)],fill=UMBER,width=4)
            levels=int(6*p)+1
            for j in range(levels):
                y=500-j*43
                span=35+j*11
                line(d,[(bx,y),(bx-span,y-25)],fill=GOLD if bi==1 else INK,width=2)
                line(d,[(bx,y),(bx+span,y-25)],fill=GOLD if bi==1 else INK,width=2)
        star(d,cx,215,36,14,n=8,phase=t*.15,outline=CRIMSON,width=2)

    elif mode=="inner_lattice":
        stone=stone_shape(cx,cy,260,180,12,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(PALE,EARTH,.18))
        pts=radial(cx,cy,125,8,phase=t*.08)
        for i in range(8):
            for j in [1,3]:
                line(d,[pts[i],pts[(i+j)%8]],fill=GOLD if j==3 else UMBER,width=2 if j==3 else 1)
        circle(d,cx,cy,18,fill=CRIMSON,outline=CRIMSON,width=1)

    elif mode=="magnet_relation":
        left=stone_shape(430,cy,120,90,9,seed=1)
        right=[(840,310),(940,330),(940,400),(840,420),(810,385),(810,345)]
        poly(d,left,outline=INK,width=3,fill=mix(PALE,EARTH,.22))
        poly(d,right,outline=INK,width=3,fill=SILVER)
        # field lines
        for off in [-80,-45,0,45,80]:
            pts=[]
            for q in range(30):
                u=q/29
                x=520+290*u
                y=cy+off*math.sin(math.pi*u)*(1+.15*math.sin(t*2))
                pts.append((x,y))
            line(d,pts,fill=GOLD if off==0 else UMBER,width=2)
        shift=20*p
        # iron drawn left
        line(d,[(810-shift,350),(810-shift,405)],fill=BLACK,width=8)

    elif mode in ("cooling_stone","sapphire_cool"):
        stone=stone_shape(cx,cy,175,145,10,seed=shot_id)
        poly(d,stone,outline=LAPIS,width=3,fill=mix(WHITE,LAPIS,.22))
        for rr in [70,115,160,210]:
            d.arc((cx-rr,cy-rr,cx+rr,cy+rr),190,350,fill=mix(PALE,WATER,.45),width=2)
        for i in range(9):
            x=cx-160+i*40
            line(d,[(x,210),(x+20*math.sin(t*2+i),500)],fill=WATER,width=1)

    elif mode=="sulphur_fire":
        star(d,cx,cy,160,70,n=12,phase=t*.1,outline=GOLD,width=3)
        flame=[(cx,180),(cx+80,330),(cx+45,530),(cx,470),(cx-45,530),(cx-80,330)]
        poly(d,flame,outline=CRIMSON,width=3,fill=mix(BG,GOLD,.28))
        circle(d,cx,cy,28,fill=CRIMSON,outline=CRIMSON,width=1)

    elif mode=="mercury_flow":
        # lunar mercury ribbons
        circle(d,430,280,86,outline=SILVER,width=3,fill=WHITE)
        circle(d,465,255,86,outline=WHITE,width=1,fill=BG)
        for k in range(7):
            pts=[]
            for q in range(40):
                u=q/39
                x=470+430*u
                y=300+k*35+28*math.sin(u*2*math.pi+t*2+k)
                pts.append((x,y))
            line(d,pts,fill=SILVER if k%2 else WATER,width=3 if k==3 else 2)
        circle(d,900,470,30,fill=SILVER,outline=UMBER,width=2)

    elif mode=="planetary_metals":
        planets=[("☉",GOLD),("☽",SILVER),("♂",CRIMSON),("♀",GREEN),("♃",LAPIS),("♄",UMBER),("☿",WATER)]
        pts=radial(cx,cy,215,7,phase=-math.pi/2+t*.03)
        for (label,col),(x,y) in zip(planets,pts):
            circle(d,x,y,38,outline=col,width=3,fill=WHITE)
            d.text((x-12,y-14),label,fill=col,font=TITLE)
            line(d,[(cx,cy),(x,y)],fill=PALE,width=1)
        stone=stone_shape(cx,cy,75,65,9,seed=7)
        poly(d,stone,outline=GOLD,width=3,fill=mix(PALE,EARTH,.14))

    elif mode=="subtle_body":
        # body with solar/lunar channels
        circle(d,cx,190,28,outline=INK,width=3)
        line(d,[(cx,218),(cx,520)],fill=GOLD,width=5)
        line(d,[(cx,285),(530,380)],fill=INK,width=3)
        line(d,[(cx,285),(750,380)],fill=INK,width=3)
        line(d,[(cx,520),(570,610)],fill=INK,width=3)
        line(d,[(cx,520),(710,610)],fill=INK,width=3)
        for side,col,phase in [(-1,WATER,0),(1,CRIMSON,math.pi)]:
            pts=[]
            for q in range(40):
                u=q/39
                y=240+260*u
                x=cx+side*(45*math.sin(u*4*math.pi+phase+t*.35))
                pts.append((x,y))
            line(d,pts,fill=col,width=4)
        for y in [260,330,400,470]:
            circle(d,cx,y,9,fill=GOLD,outline=GOLD,width=1)

    elif mode=="lapis_birth":
        # paired streams produce luminous stone
        for x,col,sgn in [(480,CRIMSON,1),(800,SILVER,-1)]:
            pts=[]
            for q in range(35):
                u=q/34
                pts.append((x+(cx-x)*u,220+260*u+35*math.sin(u*math.pi)*sgn))
            line(d,pts,fill=col,width=5)
        stone=stone_shape(cx,500,105*p+20,75*p+15,10,seed=4)
        poly(d,stone,outline=GOLD,width=4,fill=mix(WHITE,GOLD,.24))
        star(d,cx,500,45*p,17*p,n=8,phase=t*.2,outline=CRIMSON,width=2)

    elif mode=="lapidary_pages":
        # rotating catalog cabinet
        d.rectangle((230,160,1050,570),outline=INK,width=3,fill=WHITE)
        for row in range(3):
            for col in range(5):
                x=310+col*160; y=245+row*120
                circle(d,x,y,35,outline=[UMBER,LAPIS,GREEN,CRIMSON,GOLD][col],width=2,fill=mix(WHITE,PALE,.25))
                d.text((x-12,y+45),chr(65+row*5+col),fill=UMBER,font=TINY)
        line(d,[(250,200),(1030,200)],fill=PALE,width=2)

    elif mode=="eternal_fibre":
        # asbestos thread in unquenchable flame
        for k in range(9):
            pts=[]
            for q in range(35):
                u=q/34
                x=400+k*55+10*math.sin(q*.6+t*3+k)
                y=550-310*u
                pts.append((x,y))
            line(d,pts,fill=WHITE if k%2 else SILVER,width=3)
        flame=[(cx,155),(cx+190,420),(cx+120,580),(cx,510),(cx-120,580),(cx-190,420)]
        line(d,flame,fill=CRIMSON,width=4)
        star(d,cx,365,100,42,n=9,phase=t*.12,outline=GOLD,width=2)

    elif mode=="adamant":
        diamond=[(cx,175),(825,330),(750,550),(530,550),(455,330)]
        poly(d,diamond,outline=INK,width=4,fill=mix(WHITE,LAPIS,.10))
        for pnt in [(cx,175),(825,330),(750,550),(530,550),(455,330)]:
            line(d,[pnt,(cx,390)],fill=GOLD,width=2)
        # iron bar halted
        line(d,[(270,365),(455-20*p,365)],fill=BLACK,width=12)
        line(d,[(825+20*p,365),(1030,365)],fill=BLACK,width=12)

    elif mode=="dream_stone":
        stone=stone_shape(cx,500,180,85,11,seed=shot_id)
        poly(d,stone,outline=UMBER,width=3,fill=mix(PALE,EARTH,.15))
        # sleeping head and imaginal images
        d.arc((350,420,580,620),180,320,fill=INK,width=4)
        for i,(x,y) in enumerate([(550,330),(690,260),(830,330)]):
            star(d,x,y,35,13,n=6+i,phase=t*.08*i,outline=[LAPIS,GOLD,CRIMSON][i],width=2)
            line(d,[(cx,450),(x,y)],fill=PALE,width=1)

    elif mode=="amethyst_vigil":
        pts=stone_shape(cx,cy,150,180,8,phase=math.pi/8,seed=shot_id)
        poly(d,pts,outline=CRIMSON,width=3,fill=mix(WHITE,(103,70,122),.25))
        circle(d,cx,cy,52,outline=GOLD,width=2)
        for a in [0,math.pi]:
            d.arc((cx-230,cy-100,cx+230,cy+100),180 if a==0 else 0,360 if a==0 else 180,fill=LAPIS,width=3)

    elif mode=="carbuncle_coal":
        stone=stone_shape(cx,cy,170,140,10,seed=shot_id)
        poly(d,stone,outline=BLACK,width=4,fill=(46,35,31))
        for rr,col in [(40,CRIMSON),(75,GOLD),(120,UMBER)]:
            circle(d,cx,cy,rr+8*pulse,outline=col,width=3)
        star(d,cx,cy,30,12,n=8,phase=t*.2,outline=WHITE,width=2)

    elif mode=="emerald_memory":
        stone=stone_shape(cx,cy,170,135,10,seed=shot_id)
        poly(d,stone,outline=GREEN,width=4,fill=mix(WHITE,GREEN,.25))
        # eye / memory lattice
        d.arc((cx-115,cy-45,cx+115,cy+45),195,345,fill=INK,width=3)
        d.arc((cx-115,cy-45,cx+115,cy+45),15,165,fill=INK,width=3)
        circle(d,cx,cy,18,fill=GOLD,outline=GOLD,width=1)
        for i in range(7):
            x=420+i*75
            line(d,[(x,535),(x+20,560)],fill=GREEN,width=2)

    elif mode=="consciousness_condenses":
        # descending wordless glyphs become stone
        for i in range(9):
            y=150+i*35+25*p
            star(d,430+i*52,y,16,6,n=5+(i%3),phase=t*.1+i,outline=GOLD if i%2 else LAPIS,width=1)
            line(d,[(430+i*52,y+18),(cx,480)],fill=PALE,width=1)
        stone=stone_shape(cx,500,150*p+30,70*p+20,11,seed=shot_id)
        poly(d,stone,outline=CRIMSON,width=3,fill=mix(WHITE,EARTH,.22))

    elif mode=="engraving":
        stone=stone_shape(cx,cy,250,170,12,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(WHITE,EARTH,.15))
        # stylus traces a sigil
        sig=[(cx,245),(cx+90,330),(cx+45,470),(cx-45,470),(cx-90,330),(cx,245)]
        n=max(2,int(len(sig)*p))
        line(d,sig[:n],fill=GOLD,width=4)
        sx=int(850-200*p); sy=int(210+220*p)
        line(d,[(sx,sy),(sx+120,sy+150)],fill=INK,width=7)

    elif mode in ("lion_seal","serpent_seal","mirror_seal"):
        stone=stone_shape(cx,cy,245,170,12,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(WHITE,EARTH,.15))
        if mode=="lion_seal":
            circle(d,cx,cy,75,outline=GOLD,width=4)
            for a in [i*math.pi/8 for i in range(16)]:
                line(d,[(cx+82*math.cos(a),cy+82*math.sin(a)),(cx+120*math.cos(a),cy+120*math.sin(a))],fill=CRIMSON,width=3)
            circle(d,cx-25,cy-10,5,fill=INK,outline=INK,width=1)
            circle(d,cx+25,cy-10,5,fill=INK,outline=INK,width=1)
        elif mode=="serpent_seal":
            pts=[]
            for q in range(120):
                u=q/119
                a=u*4*math.pi+t*.2
                r=120*(1-u*.65)
                pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
            line(d,pts,fill=GREEN,width=5)
            circle(d,*pts[-1],8,fill=CRIMSON,outline=CRIMSON,width=1)
        else:
            d.ellipse((cx-105,cy-135,cx+105,cy+135),outline=LAPIS,width=4,fill=WHITE)
            for off in [-35,35]:
                d.arc((cx-55+off,cy-80,cx+55+off,cy+80),80,280,fill=GOLD,width=2)

    elif mode=="twelvefold":
        pts=radial(cx,cy,220,12,phase=-math.pi/2+t*.02)
        for i,pnt in enumerate(pts):
            circle(d,*pnt,24,outline=[GOLD,CRIMSON,LAPIS,UMBER][i%4],width=2,fill=WHITE)
            line(d,[pnt,(cx,cy)],fill=PALE,width=1)
        star(d,cx,cy,105,44,n=6,phase=t*.08,outline=INK,width=3)
        circle(d,cx,cy,18,fill=GOLD,outline=GOLD,width=1)

    elif mode=="stone_star":
        stone=stone_shape(420,440,165,105,10,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(WHITE,EARTH,.16))
        star(d,900,245,80,32,n=8,phase=t*.12,outline=GOLD,width=3)
        for off in [-50,-25,0,25,50]:
            pts=[]
            for q in range(40):
                u=q/39
                x=540+280*u
                y=420+(245-420)*u+off*math.sin(math.pi*u)
                pts.append((x,y))
            line(d,pts,fill=CRIMSON if off==0 else PALE,width=2)

    elif mode=="river_gold":
        # river bands
        for k in range(8):
            pts=[]
            for q in range(50):
                u=q/49
                x=120+1040*u
                y=300+k*34+30*math.sin(u*3*math.pi+t*2+k)
                pts.append((x,y))
            line(d,pts,fill=WATER if k%2 else LAPIS,width=3)
        for i in range(36):
            x=150+(i*83)%980
            y=310+(i*57)%230+10*math.sin(t*3+i)
            circle(d,x,y,3+(i%3),fill=GOLD,outline=GOLD,width=1)

    elif mode=="silver_vein":
        stone=stone_shape(cx,cy,380,210,13,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(PALE,EARTH,.18))
        pts=[]
        for q in range(55):
            u=q/54
            x=300+680*u
            y=cy+65*math.sin(u*4*math.pi+t*.4)
            pts.append((x,y))
        line(d,pts,fill=SILVER,width=14)
        line(d,pts,fill=WHITE,width=4)

    elif mode=="serpent_stone":
        stone=stone_shape(cx,cy,300,180,12,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=mix(PALE,EARTH,.22))
        for i in range(12):
            pts=[]
            base_a=2*math.pi*i/12
            for q in range(28):
                u=q/27
                a=base_a+u*1.6+0.15*math.sin(t*2+i)
                r=50+120*u
                pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
            line(d,pts,fill=GREEN if i%2 else UMBER,width=3)

    elif mode=="onyx_faces":
        stone=stone_shape(cx,cy,300,190,11,seed=shot_id)
        poly(d,stone,outline=BLACK,width=4,fill=(52,47,43))
        for fx in [545,735]:
            circle(d,fx,cy-10,65,outline=WHITE,width=3)
            d.arc((fx-35,cy-10,fx+35,cy+45),190,350,fill=WHITE,width=2)
            circle(d,fx-18,cy-22,4,fill=WHITE,outline=WHITE,width=1)
            circle(d,fx+18,cy-22,4,fill=WHITE,outline=WHITE,width=1)

    elif mode=="field_journal":
        d.rectangle((250,150,1030,565),outline=INK,width=3,fill=WHITE)
        line(d,[(640,150),(640,565)],fill=PALE,width=2)
        # sketches
        stone=stone_shape(450,350,115,75,9,seed=shot_id)
        poly(d,stone,outline=UMBER,width=2,fill=None)
        pts=radial(820,350,95,7,phase=t*.05)
        poly(d,pts,outline=GOLD,width=2,fill=None)
        for j in range(6):
            line(d,[(700,490-j*24),(920-j*10,490-j*24)],fill=UMBER,width=1)
        # observing eye above
        d.arc((550,80,730,145),195,345,fill=INK,width=3)
        d.arc((550,80,730,145),15,165,fill=INK,width=3)

    elif mode=="false_gold":
        # red core, yellow surface peeling
        stone=stone_shape(cx,cy,220,145,11,seed=shot_id)
        poly(d,stone,outline=INK,width=3,fill=CRIMSON)
        overlay=stone_shape(cx+30*p,cy-20*p,205,130,11,seed=shot_id+1)
        poly(d,overlay,outline=GOLD,width=3,fill=mix(GOLD,WHITE,.15))
        # reveal red edge
        line(d,[(420,500),(860,220)],fill=BLACK,width=3)

    elif mode=="prime_matter":
        # forms dissolve into dark substrate
        for i,pnt in enumerate(radial(cx,cy,190,8,phase=t*.04)):
            star(d,pnt[0],pnt[1],34*(1-p)+5,13*(1-p)+2,n=5+i%4,outline=[GOLD,LAPIS,CRIMSON][i%3],width=2)
            line(d,[pnt,(cx,cy)],fill=PALE,width=1)
        circle(d,cx,cy,45+125*p,fill=mix(WHITE,BLACK,p),outline=BLACK,width=2)

    elif mode=="twin_vessels":
        for x,label,col in [(450,"NATURE",EARTH),(830,"ART",GOLD)]:
            body=[(x-105,510),(x-80,300),(x-35,240),(x+35,240),(x+80,300),(x+105,510),(x+60,565),(x-60,565)]
            poly(d,body,outline=INK,width=3,fill=WHITE)
            d.text((x-35,590),label,fill=col,font=TINY)
            level=510-170*p
            d.polygon([(x-88,500),(x-74,level),(x+74,level),(x+88,500),(x+55,548),(x-55,548)],fill=mix(PALE,col,.35))
        arrow_col=GOLD
        line(d,[(555,370),(725,370)],fill=arrow_col,width=3)

    elif mode=="solar_furnace":
        star(d,cx,170,90,38,n=12,phase=t*.1,outline=GOLD,width=3)
        for x in [510,640,770]:
            line(d,[(cx,245),(x,420)],fill=GOLD,width=3)
        body=[(520,550),(540,390),(590,330),(690,330),(740,390),(760,550),(700,600),(580,600)]
        poly(d,body,outline=INK,width=4,fill=WHITE)
        for rr in [35,65,95]:
            circle(d,cx,470,rr+8*pulse,outline=CRIMSON if rr<70 else GOLD,width=3)

    elif mode=="electrum":
        left=stone_shape(545,cy,135,160,10,seed=1)
        right=stone_shape(735,cy,135,160,10,seed=2)
        poly(d,left,outline=GOLD,width=3,fill=mix(WHITE,GOLD,.30))
        poly(d,right,outline=SILVER,width=3,fill=mix(WHITE,SILVER,.35))
        overlap=stone_shape(cx,cy,105,120,10,seed=3)
        poly(d,overlap,outline=CRIMSON,width=3,fill=mix(GOLD,SILVER,.50))

    elif mode=="salt_crucible":
        # crystal salts hovering over basin
        for i in range(18):
            x=300+(i*67)%680
            y=180+(i*43)%220+15*math.sin(t*3+i)
            s=12+(i%4)*4
            pts=[(x,y-s),(x+s,y),(x,y+s),(x-s,y)]
            poly(d,pts,outline=[WHITE,GOLD,LAPIS,CRIMSON][i%4],width=2,fill=mix(WHITE,PALE,.2))
        d.arc((390,390,890,610),180,360,fill=INK,width=4)
        d.line((390,500,890,500),fill=INK,width=3)

    elif mode=="unfixed_forms":
        # shapes continuously halfway between states
        centers=[(420,370),(640,370),(860,370)]
        for i,(x,y) in enumerate(centers):
            n1=5+i; n2=8-i
            pts=[]
            n=12
            for j in range(n):
                a=2*math.pi*j/n
                r1=90*(.75+.25*math.sin(a*n1))
                r2=90*(.75+.25*math.sin(a*n2+t*2))
                r=r1*(1-p)+r2*p
                pts.append((x+r*math.cos(a),y+r*math.sin(a)))
            poly(d,pts,outline=[GOLD,LAPIS,CRIMSON][i],width=3,fill=None)

    elif mode=="solve_coagula":
        # left dissolves, right recrystallizes
        for i in range(30):
            a=2*math.pi*i/30
            r=120*(1-p)+20*p
            x=430+r*math.cos(a)+45*p
            y=cy+r*math.sin(a)
            circle(d,x,y,4,fill=WATER,outline=WATER,width=1)
        crystal=[(850,235),(960,340),(920,520),(780,520),(740,340)]
        scaled=[(850+(x-850)*p,cy+(y-cy)*p) for x,y in crystal]
        poly(d,scaled,outline=GOLD,width=3,fill=mix(WHITE,GOLD,.15))

    elif mode=="human_intermediate":
        # unfinished human composed of mutable tesserae
        circle(d,cx,180,32,outline=INK,width=3)
        line(d,[(cx,212),(cx,500)],fill=INK,width=4)
        line(d,[(cx,290),(520,395)],fill=INK,width=3)
        line(d,[(cx,290),(760,395)],fill=INK,width=3)
        line(d,[(cx,500),(570,610)],fill=INK,width=3)
        line(d,[(cx,500),(710,610)],fill=INK,width=3)
        for i in range(36):
            a=2*math.pi*i/36
            x=cx+120*math.cos(a)*(0.4+0.6*p)
            y=360+220*math.sin(a)*(0.4+0.6*p)
            circle(d,x,y,5,fill=[GOLD,SILVER,CRIMSON,LAPIS][i%4],outline=None,width=1)
        # incomplete outline gap
        d.arc((430,125,850,625),35,325,fill=GOLD,width=2)

    elif mode=="final_vessel":
        # final synthesis: stone, person, furnace, star
        body=[(500,545),(520,330),(575,265),(705,265),(760,330),(780,545),(720,610),(560,610)]
        poly(d,body,outline=INK,width=4,fill=WHITE)
        star(d,cx,150,70,28,n=10,phase=t*.08,outline=GOLD,width=3)
        for x in [590,640,690]:
            line(d,[(cx,220),(x,430)],fill=GOLD,width=2)
        stone=stone_shape(cx,490,95,70,9,seed=shot_id)
        poly(d,stone,outline=CRIMSON,width=4,fill=mix(WHITE,GOLD,.25))
        for rr in [40,80,125]:
            circle(d,cx,490,rr+6*pulse,outline=[CRIMSON,GOLD,PALE][[40,80,125].index(rr)],width=2)
        # open human contour around vessel
        d.arc((300,120,980,680),205,335,fill=UMBER,width=2)

    else:
        star(d,cx,cy,180,75,n=10,phase=t*.1,outline=GOLD,width=3)
        circle(d,cx,cy,28,fill=CRIMSON,outline=CRIMSON,width=1)

    # subtle bottom continuity line
    line(d,[(60,665),(1220,665)],fill=PALE,width=1)
    return im

def make_audio_and_story():
    story=[]
    cursor=0.0
    final_segments=[]
    for i,s in enumerate(SEGMENTS, start=1):
        raw=AUDIO_RAW/f"shot_{i:03d}.wav"
        synth(s["text"],raw)
        raw_d=wav_duration(raw)
        # safeguard: any remaining long segment is an error
        if raw_d > MAX_DUR + .3:
            raise RuntimeError(f"Long segment {i}: {raw_d:.2f}s")
        target=max(MIN_DUR, math.ceil(raw_d*DRAFT_FPS)/DRAFT_FPS)
        # pad and trim exactly
        pad=AUDIO_PAD/f"shot_{i:03d}.wav"
        subprocess.run([
            "ffmpeg","-y","-i",str(raw),
            "-af",f"apad=pad_dur={target+0.5},atrim=0:{target}",
            "-ar","22050","-ac","1",str(pad)
        ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        mode=mode_for(s["text"],i)
        chapter=chapter_for(s["text"])
        entry={
            "shot_id":i,
            "start":round(cursor,3),
            "end":round(cursor+target,3),
            "duration":round(target,3),
            "spoken_passage":s["text"],
            "chapter":chapter,
            "visual_mode":mode,
            "visual_mechanism":mode.replace("_"," "),
            "continuity_object":continuity_for(mode),
            "transition":"motif-preserving dissolve or motion handoff",
            "caption_restriction":"No full narration captions; only brief source term when conceptually necessary.",
            "raw_audio_duration":round(raw_d,3),
        }
        story.append(entry)
        cursor += target
        final_segments.append(s)
    return story

STORY = make_audio_and_story()

def render_shots():
    thumbs=[]
    for entry in STORY:
        i=entry["shot_id"]
        dur=entry["duration"]
        mode=entry["visual_mode"]
        visual_path=VISUAL_DIR/f"shot_{i:03d}_visual.mp4"
        clip_path=SHOT_DIR/f"shot_{i:03d}_{mode}.mp4"
        frames=max(1,round(dur*DRAFT_FPS))
        writer=cv2.VideoWriter(str(visual_path),cv2.VideoWriter_fourcc(*"mp4v"),DRAFT_FPS,(W,H))
        mature=None
        for fi in range(frames):
            t=fi/max(1,frames-1)
            im=render_frame(mode,t,i,entry["chapter"],entry["spoken_passage"])
            if fi==int(frames*.72):
                mature=im.copy()
            frame=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
            writer.write(frame)
        writer.release()
        if mature is None:
            mature=render_frame(mode,.72,i,entry["chapter"],entry["spoken_passage"])
        thumbs.append(mature)
        subprocess.run([
            "ffmpeg","-y","-i",str(visual_path),"-i",str(AUDIO_PAD/f"shot_{i:03d}.wav"),
            "-c:v","libx264","-preset","veryfast","-crf","25","-r",str(FINAL_FPS),
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-shortest",
            "-movflags","+faststart",str(clip_path)
        ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return thumbs

THUMBS=render_shots()

# concatenate shot clips
concat_list=TEMP/"clips.txt"
concat_list.write_text("\n".join(
    f"file '{(SHOT_DIR/f'shot_{e['shot_id']:03d}_{e['visual_mode']}.mp4').as_posix()}'"
    for e in STORY
),encoding="utf-8")
FULL=ROOT/"the_stones_are_watching_you_full_film.mp4"
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_list),
    "-c","copy","-movflags","+faststart",str(FULL)
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

# reference narration from padded wavs
wav_list=TEMP/"wavs.txt"
wav_list.write_text("\n".join(
    f"file '{(AUDIO_PAD/f'shot_{e['shot_id']:03d}.wav').as_posix()}'" for e in STORY
),encoding="utf-8")
NARR=ROOT/"reference_narration.wav"
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(wav_list),
    "-c","copy",str(NARR)
],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

# contact sheet
cols=6
tw,th=320,180
rows=math.ceil(len(THUMBS)/cols)
sheet=Image.new("RGB",(cols*tw,rows*th),WHITE)
sd=ImageDraw.Draw(sheet)
for i,im in enumerate(THUMBS):
    thumb=im.resize((tw,th))
    x=(i%cols)*tw; y=(i//cols)*th
    sheet.paste(thumb,(x,y))
    sd.rectangle((x+5,y+5,x+250,y+28),fill=WHITE)
    sd.text((x+9,y+8),f"{i+1:03d}. {STORY[i]['visual_mode'][:24]}",fill=INK,font=TINY)
CONTACT=ROOT/"contact_sheet.jpg"
sheet.save(CONTACT,quality=91)

# storyboard JSON/CSV
(ROOT/"storyboard.json").write_text(json.dumps({
    "title":"The Stones Are Watching You",
    "source":"scripts/expansion-essay46.md",
    "timing_method":"Per-shot synthesized audio measured by WAV sample count; every shot padded to an exact 1/8-second frame boundary.",
    "shot_count":len(STORY),
    "runtime_seconds":round(STORY[-1]["end"],3),
    "shots":STORY,
},indent=2,ensure_ascii=False),encoding="utf-8")

with (ROOT/"storyboard.csv").open("w",newline="",encoding="utf-8") as f:
    fields=list(STORY[0].keys())
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    w.writerows(STORY)

# visual program
visual_program={
    "schema_version":"2.0-experimental",
    "film_id":"expansion-essay46",
    "title":"The Stones Are Watching You",
    "visual_thesis":"Matter is rendered as patient formative intelligence: stone, seed, lattice, celestial signature, field observation, vessel, and unfinished human form continuously transform into one another.",
    "style":{
        "field":"ivory mineral parchment",
        "materials":["earth","water","stone","silver","tarnished gold","lapis","crimson fire"],
        "continuity_rules":[
            "Stones repeatedly reveal interior lattices rather than acting as inert props.",
            "Gold lines represent formative or celestial causality.",
            "Earth and water begin as elemental fields and return in salts and vessels.",
            "The stone-eye becomes the observing bishop's eye and finally the human unfinished form.",
            "Alchemy is shown as preparation of conditions, not forceful command."
        ],
        "caption_policy":"Narration carries prose. Visuals carry formation, relation, correspondence, and transformation."
    },
    "chapters":{},
    "shots":[]
}
for e in STORY:
    visual_program["chapters"].setdefault(e["chapter"],[]).append(e["shot_id"])
    visual_program["shots"].append({
        "id":f"stone-film-{e['shot_id']:03d}",
        "start":e["start"],"end":e["end"],
        "spoken_passage":e["spoken_passage"],
        "semantic_relation":e["visual_mode"],
        "visual_operator":["reveal","form","correspond","condense","transform"][e["shot_id"]%5],
        "continuity_object":e["continuity_object"],
        "backend":{"current":"pillow","future":["coldtype","blender"]},
    })
(ROOT/"visual_program.json").write_text(json.dumps(visual_program,indent=2,ensure_ascii=False),encoding="utf-8")

runtime=STORY[-1]["end"]
chapter_lines=[]
for ch, ids in visual_program["chapters"].items():
    chapter_lines.append(f"- **{ch}:** shots {ids[0]}–{ids[-1]}")

blueprint=f"""# Production Blueprint — The Stones Are Watching You

## Production identity

- Exact source script: `scripts/expansion-essay46.md`
- Narration rewriting: none
- Shot count: {len(STORY)}
- Runtime: {runtime/60:.2f} minutes
- Shot range: {min(e['duration'] for e in STORY):.2f}–{max(e['duration'] for e in STORY):.2f} seconds
- Output: one coherent narration-locked film plus independently reusable audiovisual clips

## Chapters

{chr(10).join(chapter_lines)}

## Continuous visual systems

### The watching stone
The opening mineral eye establishes stone as patient awareness. It later becomes the bishop's observing eye, the eye-like powers of emerald and sapphire, natural faces in onyx, and finally the unfinished human figure.

### Seed, lattice, and substantial form
Earth and water converge into a mineral seed. The seed grows into a crystal lattice. Later every stone's power is presented as an action of this interior form rather than an emitted magical effect.

### Sulphur, Quicksilver, and the central axis
Solar fire and lunar flow remain distinct, enter a sevenfold planetary system, then become paired bodily channels converging in the completed lapis.

### Stone and star
Engraved seals, the twelvefold wheel, and the stone-star frequency line develop one correspondence system. Celestial causality descends into material form without reducing either pole to metaphor.

### Field observation
The abstract theory moves into rivers, veins, serpents, onyx faces, and an open field journal. The observing eye preserves continuity from the introduction.

### Vessel and unfinished matter
False gold is stripped back to prime matter. Natural and artificial vessels are compared. Electrum and salts remain mutable. The concluding human figure is treated as an intermediate substance entering the prepared vessel.

## Timing correction

This film does not use estimated words-per-minute timestamps.

Each shot has its own WAV file. The WAV sample count determines its exact visual duration. Audio is padded to an exact 1/{DRAFT_FPS}-second frame boundary, and the corresponding visual clip is rendered to that same duration before muxing.

This prevents the systematic visual lead found in the earlier Corbin film.

## Publication workflow

The included eSpeak narration is a timing reference. For publication:

1. record or generate the final narration from `narration_script.txt`;
2. force-align it against the exact text;
3. conform the shot boundaries in `storyboard.json`;
4. preserve 12–24 frame visual handles when rerendering;
5. assemble the rendered clips, archival art, and final audio in FableCut.
"""
(ROOT/"PRODUCTION_BLUEPRINT.md").write_text(blueprint,encoding="utf-8")

# probe alignment
def probe(path, selector):
    out=subprocess.check_output([
        "ffprobe","-v","error","-select_streams",selector,
        "-show_entries","stream=duration","-of","default=nw=1:nk=1",str(path)
    ],text=True).strip()
    try: return float(out.splitlines()[0])
    except: return None

vd=probe(FULL,"v:0")
ad=probe(FULL,"a:0")
alignment={
    "video_duration_seconds":vd,
    "audio_duration_seconds":ad,
    "absolute_difference_seconds":abs(vd-ad) if vd is not None and ad is not None else None,
    "planned_runtime_seconds":runtime,
    "shot_count":len(STORY),
    "visual_lead_seconds":0,
    "draft_frame_quantization_seconds":1/DRAFT_FPS,
    "method":"Audio-first per-shot timing. Each visual is generated only after exact shot audio duration is known."
}
(ROOT/"alignment_report.json").write_text(json.dumps(alignment,indent=2),encoding="utf-8")

readme=f"""# The Stones Are Watching You — Full Film Pack

A narration-locked visual film generated from `expansion-essay46.md`.

## Included

- `the_stones_are_watching_you_full_film.mp4`
- `reference_narration.wav`
- `{len(STORY)}` independently reusable audiovisual clips in `shots/`
- `contact_sheet.jpg`
- `storyboard.json`
- `storyboard.csv`
- `visual_program.json`
- `PRODUCTION_BLUEPRINT.md`
- `alignment_report.json`
- `render_stones_are_watching.py`
- `source_essay.md`
- `narration_script.txt`

## Specifications

- 1280×720
- H.264 / AAC
- 24 fps delivery
- {len(STORY)} shots
- {runtime:.2f} seconds total
- exact audio-first shot alignment

The included eSpeak track is a timing reference and should be replaced by a publication-quality narration before release.
"""
(ROOT/"README.md").write_text(readme,encoding="utf-8")

# package, excluding intermediate raw files
ZIP=Path("/mnt/data/stones_are_watching_film_pack.zip")
if ZIP.exists(): ZIP.unlink()
with zipfile.ZipFile(ZIP,"w",zipfile.ZIP_DEFLATED,allowZip64=True) as z:
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in {"audio_raw","audio_padded","visual_drafts","temp"}:
            continue
        z.write(p,Path(ROOT.name)/rel)

print(json.dumps({
    "zip":str(ZIP),
    "film":str(FULL),
    "contact":str(CONTACT),
    "shots":len(STORY),
    "runtime":runtime,
    "alignment":alignment
},indent=2))
