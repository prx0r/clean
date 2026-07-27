"""Packs 19-25: Tantra-focused packs."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from renderer import Film, Scene

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220); M = (145, 141, 132); C_ = (141, 44, 57)
def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x): t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1; return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

packs = []

def add(name, fn_dur_list, desc):
    scenes = [Scene(f"s{i+1}", d, f, desc) for i, (f, d) in enumerate(fn_dur_list)]
    packs.append((name, scenes, desc))

# 19: Nine Rasas
def r1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    rasas = ["śṛṅgāra", "vīra", "bībhatsa", "raudra", "hāsya", "bhayānaka", "karuṇa", "adbhuta", "śānta"]
    for k, _ in enumerate(rasas):
        a = S(0.03 + k * 0.06, 0.2 + k * 0.06, u); ang = k * 0.698 + t * 0.03; rr = 30 + 60 * u
        x = cx + rr * math.cos(ang); y = cy + rr * math.sin(ang)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), outline=[G, C_, I_, G, C_, I_, G, C_, I_][k], width=2)
        d.text((x - 20, y + 15), rasas[k], fill=M)
    d.text((60, 60), "nine rasas", fill=I_); return im
add("nine_rasas", [(r1, 14)], "Nine rasas")

# 20: VBT Sense Doors
def s1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(5):
        a = S(0.05 + k * 0.12, 0.3 + k * 0.12, u); r = (90 - k * 15) * a
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=[G, I_, C_, G, I_][k], width=2)
        d.text((cx + r + 12, cy - 8), ["sight", "sound", "touch", "taste", "smell"][k], fill=M)
    d.text((60, 60), "five sense doors", fill=I_); return im
add("vbt_sense_doors", [(s1, 14)], "VBT sense doors")

# 21: Trika
def t1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(3):
        ang = math.pi / 2 + i_ * 2.094; r = 100 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=[G, C_, I_][i_], width=2)
        d.text((x - 18, y - 8), ["śiva", "śakti", "nara"][i_], fill=[G, C_, I_][i_])
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=G); d.text((60, 60), "trika", fill=I_); return im
add("trika", [(t1, 14)], "Trika triad")

# 22: Spanda Third Flow
def sp3(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(20):
        a = S(0.02 + k * 0.03, 0.3 + k * 0.03, u); ang = k * 0.314 + t * 0.02; r = 20 + 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=G)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G); d.text((60, 60), "spanda — third flow", fill=I_); return im
add("spanda_third_flow", [(sp3, 14)], "Spanda third flow")

# 23: Pratyabhijñā
def pr(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    d.line((cx, 50, cx, 670), fill=M, width=1)
    for k in range(20):
        p_ = S(0.03 + k * 0.03, 0.4 + k * 0.03, u); ta = k * 0.314
        r = 240 * (1 - 0.7 * p_); ang = ta + (1 - p_) * k * 0.08
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=I_)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G); d.text((60, 60), "pratyabhijñā", fill=I_); return im
add("pratyabhijna", [(pr, 14)], "Pratyabhijñā")

# 24: Krama
def kr(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(12):
        a = S(0.02 + k * 0.05, 0.2 + k * 0.05, u); ang = k * 0.524 + t * 0.05; r = 30 + 80 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy, x, y), fill=C_, width=1); d.ellipse((x - 4, y - 4, x + 4, y + 4), outline=G, width=2)
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=G)
    d.text((60, 60), "krama", fill=I_); d.text((60, 95), "sequence of consciousness", fill=M); return im
add("krama", [(kr, 14)], "Krama sequence")

# 25: Mantra System
def ms(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(8):
        r = (20 + i_ * 25) * S(0, 1, u)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=I_ if i_ % 2 == 0 else G, width=1)
    d.text((cx - 15, cy - 10), "oṃ", fill=G)
    d.text((60, 60), "mantra system", fill=I_); return im
add("mantra_system", [(ms, 14)], "Mantra system")

# Render
for i, (name, scenes, desc) in enumerate(packs, 19):
    film = Film(name, desc, scenes)
    out = Path(f'/root/projects/FableCut/media/p{i:02d}-{name}.mp4')
    film.render(out)
    print(f"✅ p{i:02d}-{name}.mp4 — {out.stat().st_size / 1024:.0f}K ({len(scenes)} scene)")
