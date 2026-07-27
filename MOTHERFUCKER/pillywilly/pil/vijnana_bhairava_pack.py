"""Vijñāna Bhairava Tantra — 6 meditation gates.
Each scene maps one meditation technique to a visual generator.
Doctrine→Motion vocabulary following Pratyabhijñā pack format."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
DARK = (12, 12, 15); GOLD = (208, 172, 91); INK = (235, 231, 220)
MUTED = (145, 141, 132); CRIMSON = (141, 44, 57); WHITE = (248, 246, 240)

def p(t, o=0, s=1.0): return 0.5+0.5*math.sin(t*s+o)
def s_(a,b,x): t_=max(0,min(1,(x-a)/(b-a))) if b!=a else 1; return t_*t_*(3-2*t_)
def canvas(bg=DARK): return Image.new("RGB", (W, H), bg)

# ═══════════════════════════════════════════════════════════════════
# 1. Between Two Breaths — the gap
# ═══════════════════════════════════════════════════════════════════
# Verse: "at the junction of inhalation and exhalation"
# Generator: moiré / interference — two waves meeting at center
# Concept: the gap between is the door

def s01_between_breaths(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    for ring in range(6):
        r1 = (20 + ring * 30 + 8 * p(t, ring*0.3, 0.4)) * (0.3 + 0.7 * u)
        r2 = (20 + ring * 30 + 8 * p(t + 0.5, ring*0.3, 0.4)) * (0.3 + 0.7 * u)
        a = 0.2 - ring * 0.025
        if a > 0:
            d.ellipse((cx-120-r1, cy-r1, cx-120+r1, cy+r1), outline=(GOLD[0],GOLD[1],GOLD[2],int(255*a)), width=1)
            d.ellipse((cx+120-r2, cy-r2, cx+120+r2, cy+r2), outline=(CRIMSON[0],CRIMSON[1],CRIMSON[2],int(255*a)), width=1)

    if u > 0.4:
        a = s_(0.4, 0.6, u)
        d.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(GOLD[0],GOLD[1],GOLD[2],int(80*a)))

    d.text((60, 60), "1", fill=MUTED)
    d.text((60, 90), "between two breaths", fill=INK)
    d.text((60, 120), "the gap is the door", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# 2. Attention at the Third Eye — bindu + radiant lines
# ═══════════════════════════════════════════════════════════════════
# Verse: "fix the mind between the eyebrows"
# Generator: radial burst from center point
# Concept: converging attention opens inner space

def s02_third_eye(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    n = int(36 * s_(0, 1, u))
    for i in range(n):
        a = i * 0.175 + t * 0.05
        r = 20 + 120 * p(t + i*0.05, 0, 0.3)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        d.line((cx, cy, x, y), fill=(GOLD[0],GOLD[1],GOLD[2],int(60 * p(t+i*0.05,0,0.5))), width=1)

    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=GOLD)
    if u > 0.6:
        d.ellipse((cx-12, cy-12, cx+12, cy+12), fill=(GOLD[0],GOLD[1],GOLD[2],int(30)))

    d.text((60, 60), "2", fill=MUTED)
    d.text((60, 90), "between the brows", fill=INK)
    d.text((60, 120), "attention converges, space opens", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# 3. The Central Channel — rising column
# ═══════════════════════════════════════════════════════════════════
# Verse: "from the root, rays of light rising through the central channel"
# Generator: vertical ascending particles along spine
# Concept: prāṇa rising through suṣumṇā

def s03_central_channel(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Central column
    d.line((cx, cy+150, cx, cy-150), fill=(GOLD[0],GOLD[1],GOLD[2],int(30)), width=3)

    # Rising particles
    n = int(40 * s_(0, 1, u))
    for i in range(n):
        y_offset = -300 + (600 * i / n) + 50 * p(t + i*0.1, 0, 0.5)
        x_offset = 20 * p(t + i*0.15, 0, 0.7)
        sz = 2 + 2 * p(t + i*0.05, 0, 0.6)
        shade = int(150 + 100 * p(t + i*0.05, 0, 0.4))
        d.ellipse((cx+x_offset-sz, cy+y_offset-sz, cx+x_offset+sz, cy+y_offset+sz), fill=(shade, shade-30, shade-60))

    # Chakra points
    for i in range(5):
        y = cy - 100 + i * 50
        r = 4 + 2 * p(t + i*0.3, 0, 0.5)
        d.ellipse((cx-r, y-r, cx+r, y+r), fill=CRIMSON)

    d.text((60, 60), "3", fill=MUTED)
    d.text((60, 90), "the central channel", fill=INK)
    d.text((60, 120), "rays of light rising", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# 4. Stillness Between Two Thoughts — wave settling
# ═══════════════════════════════════════════════════════════════════
# Verse: "between two thoughts, the space of pure awareness"
# Generator: damped harmonograph — chaotic motion settles into stillness
# Concept: thoughts arise and dissolve, the gap is awareness

def s04_between_thoughts(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    n = int(200 * s_(0, 1, u))
    pts = []
    for i in range(n):
        ti = i * 0.08
        damp = math.exp(-0.04 * ti)
        x = 200 * damp * (math.sin(2.5*ti) + 0.5*math.sin(4.0*ti))
        y = 200 * damp * (math.sin(3.0*ti) + 0.5*math.sin(2.0*ti))
        pts.append((cx + x, cy + y))

    for i in range(1, len(pts)):
        a = i / len(pts) * 0.8
        shade = int(200 * (1 - i/len(pts)))
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
               fill=(shade, shade, shade), width=1)

    # Center point emerges as motion settles
    if u > 0.6:
        a = s_(0.6, 0.8, u)
        d.ellipse((cx-8, cy-8, cx+8, cy+8), fill=(GOLD[0],GOLD[1],GOLD[2],int(180*a)))

    d.text((60, 60), "4", fill=MUTED)
    d.text((60, 90), "between two thoughts", fill=INK)
    d.text((60, 120), "motion settles into stillness", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# 5. Sense Withdrawal — five portals closing
# ═══════════════════════════════════════════════════════════════════
# Verse: "closing the doors of the senses one by one"
# Generator: five concentric rings, each closing in sequence
# Concept: senses retract inward like portals closing

def s05_sense_withdrawal(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    senses = ["sight", "sound", "touch", "taste", "smell"]
    for i in range(5):
        seq = s_(0.1 + i*0.12, 0.3 + i*0.12, u)
        if seq <= 0: continue
        r = (120 - i * 15) * seq
        a = 0.3 - i * 0.04
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=INK, width=2)
        # Closing arc
        if seq > 0.5:
            close_ang = 360 * (seq - 0.5) * 2
            d.arc((cx-r-5, cy-r-5, cx+r+5, cy+r+5), -90, -90 + close_ang, fill=CRIMSON, width=2)
        d.text((cx+r+20, cy-8), senses[i], fill=MUTED)

    d.text((60, 60), "5", fill=MUTED)
    d.text((60, 90), "five portals closing", fill=INK)
    d.text((60, 120), "senses withdraw inward", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# 6. Bhairava's Sudden Awakening — vertical burst
# ═══════════════════════════════════════════════════════════════════
# Verse: "Udyamo bhairavaḥ — the sudden impulse is Bhairava"
# Generator: vertical flame impulse, rising burst
# Concept: awakening as sudden recognition

def s06_sudden_awakening(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Vertical burst
    burst_pts = []
    for i in range(20):
        a = t*0.2 + i * 0.157
        r = 30 + 100 * p(t + i*0.1, 0, 0.5) * (0.5 + 0.5 * u)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        d.line((cx, cy, x, y), fill=(GOLD[0],GOLD[1],GOLD[2],int(80 * p(t+i*0.05,0,0.5))), width=1)

    # Flame body
    flame_h = 80 * u
    flame_w = 25 * u
    pts = []
    for i in range(20):
        a = i * 2 * math.pi / 20
        r = flame_w * (1 - abs(math.sin(a/2))**0.7)
        x = cx + r * math.cos(a)
        y = cy - 60 - flame_h * abs(math.sin(a/2))**1.5
        pts.append((x, y))
    if len(pts) > 2:
        for i in range(1, len(pts)):
            d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]), fill=GOLD, width=1)

    d.ellipse((cx-5, cy-5, cx+5, cy+5), fill=GOLD)

    d.text((60, 60), "6", fill=MUTED)
    d.text((60, 90), "udyamo bhairavaḥ", fill=INK)
    d.text((60, 120), "the sudden impulse is Bhairava", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# Registry + Knowledge Dossier
# ═══════════════════════════════════════════════════════════════════

VBT_PACK = [
    ("between_breaths", s01_between_breaths, 12, "moiré at the gap between breaths"),
    ("third_eye", s02_third_eye, 12, "radial burst — attention at the brow"),
    ("central_channel", s03_central_channel, 12, "rising light through suṣumṇā"),
    ("between_thoughts", s04_between_thoughts, 12, "damped harmonograph — settling"),
    ("sense_withdrawal", s05_sense_withdrawal, 12, "five portals closing sequentially"),
    ("sudden_awakening", s06_sudden_awakening, 12, "vertical burst — udyamo bhairavaḥ"),
]

KNOWLEDGE_DOSSIER = """# Agent Knowledge Dossier — Vijñāna Bhairava Tantra Scene System

## Doctrine→Motion
- between two breaths → moiré interference at the gap
- third eye / bhrūmadhya → radial burst from center point
- central channel / suṣumṇā → vertical ascending particles
- between two thoughts → damped harmonograph settling to stillness
- five senses withdrawing → concentric rings closing sequentially
- sudden awakening / udyamo bhairavaḥ → vertical flame impulse burst

## Source
Vijñāna Bhairava Tantra verses, Hareesh.org translations and commentaries.
Full content at content/research/hareesh-blog/by-topic/vbt/

## Reuse Map
- Gap/between states: scenes 1, 4
- Concentration / focus: scene 2
- Energy body / prāṇa: scene 3
- Sense restraint: scene 5
- Breakthrough / awakening: scene 6

## Renderer Schema
{
  "generator": "moire | radial_burst | particle_column | harmonograph | concentric_close | flame_burst",
  "duration": 12,
  "style": {"background": "dark", "primary": "gold", "secondary": "crimson"},
  "reveal": "progressive"
}
"""
