"""Pack 1: Five States of Consciousness — Tantrāloka Āhnika 10.
Waking, dream, deep sleep, the Fourth, beyond the Fourth."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720
DARK = (12, 12, 15); GOLD = (208, 172, 91); INK = (235, 231, 220)
MUTED = (145, 141, 132); CRIMSON = (141, 44, 57); WHITE = (248, 246, 240)

def p(t, o=0, s=1.0): return 0.5+0.5*math.sin(t*s+o)
def s_(a,b,x): t_=max(0,min(1,(x-a)/(b-a))) if b!=a else 1; return t_*t_*(3-2*t_)
def canvas(bg=DARK): return Image.new("RGB", (W, H), bg)

# ── 1. Waking — sharp lines, distinct forms ─────────────────────
def s01_waking(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    for i in range(12):
        a = t*0.1 + i*0.524
        r = 80 + 40*p(t+i*0.1,0,0.3)
        d.line((cx, cy, cx+r*math.cos(a), cy+r*math.sin(a)), fill=(40,40,40), width=2)
    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=(40,40,40))
    d.text((60,60), "1", fill=MUTED); d.text((60,90), "waking", fill=(40,40,40))
    d.text((60,120), "sharp lines, distinct forms", fill=MUTED)
    return im

# ── 2. Dream — flowing, morphing, soft ──────────────────────────
def s02_dream(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    pts = []
    for x in range(-300, 301, 3):
        y = 80 * p(t*0.5 + x*0.005, 0, 0.4) + 40 * p(t*0.3 + x*0.008, 0.5, 0.6)
        pts.append((cx+x, cy+y))
    for i in range(1, len(pts)):
        shade = int(150 + 100 * p(t + i*0.01, 0, 0.3))
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]), fill=(shade, shade-30, shade), width=2)
    d.text((60,60), "2", fill=MUTED); d.text((60,90), "dream", fill=INK)
    d.text((60,120), "flowing, morphing", fill=MUTED)
    return im

# ── 3. Deep Sleep — formless field, dark, no center ─────────────
def s03_deep_sleep(t, u, idx):
    im = canvas((8, 8, 12))
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    for i in range(10, 300, 8):
        d.ellipse((cx-i, cy-i, cx+i, cy+i), outline=(12,15,20), width=1)
    d.text((60,60), "3", fill=MUTED); d.text((60,90), "deep sleep", fill=(40,45,55))
    d.text((60,120), "formless, no center", fill=MUTED)
    return im

# ── 4. The Fourth — witness, stable center ──────────────────────
def s04_fourth(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    for i in range(5):
        r = 40 + i*35 + 10*p(t+i*0.2,0,0.3)
        a = 0.15 - i*0.025
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(GOLD[0],GOLD[1],GOLD[2],int(255*a)), width=1)
    d.ellipse((cx-8, cy-8, cx+8, cy+8), fill=GOLD)
    d.text((60,60), "4", fill=MUTED); d.text((60,90), "turīya — the witness", fill=INK)
    d.text((60,120), "still center perceiving all", fill=MUTED)
    return im

# ── 5. Beyond the Fourth — dissolution, light ───────────────────
def s05_beyond(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    r = 6 + 300 * s_(2, 10, t)
    shade = min(255, 20 + int(200 * s_(6, 10, t)))
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(shade, shade, shade))
    if t < 6:
        a = s_(0, 3, t)
        d.text((cx-100, cy-20), "turīyātīta", fill=(200,200,200,int(255*a)))
    d.text((60,60), "5", fill=MUTED); d.text((60,90), "beyond the fourth", fill=INK)
    d.text((60,120), "expansion into light", fill=MUTED)
    return im

PACK = [
    ("waking", s01_waking, 10, "sharp lines, distinct forms"),
    ("dream", s02_dream, 10, "flowing morphing wave"),
    ("deep_sleep", s03_deep_sleep, 10, "formless dark field"),
    ("the_fourth", s04_fourth, 10, "witness — still center"),
    ("beyond_fourth", s05_beyond, 12, "dissolution into light"),
]
