"""Spanda Kārikā — Six passages on the divine pulsation.
Inspired by the Pratyabhijñāhṛdayam pack's doctrine→motion approach.
Each scene maps one passage to a visual generator."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
DARK = (12, 12, 15); WHITE = (248, 246, 240); GOLD = (208, 172, 91)
INK = (235, 231, 220); MUTED = (145, 141, 132); CRIMSON = (141, 44, 57)

def p(t, o=0, s=1.0): return 0.5+0.5*math.sin(t*s+o)
def s_(a,b,x): t_=max(0,min(1,(x-a)/(b-a))) if b!=a else 1; return t_*t_*(3-2*t_)
def canvas(bg=DARK): return Image.new("RGB", (W, H), bg)

# ═══════════════════════════════════════════════════════════════════
# Scene 1: Spanda as Inner Exertion — harmonograph
# ═══════════════════════════════════════════════════════════════════
# Passage: "It is called vitality. It is the inner exertion which impels..."
# Generator: harmonograph / progressive stroke — one line that builds
# Concept: the pulse before any form

def s01_inner_exertion(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Single harmonograph line — builds progressively
    n = int(300 * s_(0, 1, u))
    pts = []
    for i in range(n):
        ti = i * 0.05
        x = 180 * (math.exp(-0.02*ti)*math.sin(2.0*ti) + math.exp(-0.03*ti)*math.sin(3.0*ti))
        y = 180 * (math.exp(-0.025*ti)*math.sin(3.0*ti) + math.exp(-0.02*ti)*math.sin(2.0*ti))
        pts.append((cx + x, cy + y))

    for i in range(1, len(pts)):
        a = i / len(pts) * 0.8
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]), fill=GOLD, width=1)

    # Label
    if u > 0.4:
        d.text((60, 60), "1", fill=MUTED)
        d.text((60, 90), "spanda as inner exertion", fill=INK)
        d.text((60, 120), "the pulse before any form", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# Scene 2: Six Names — L-system unfolding
# ═══════════════════════════════════════════════════════════════════
# Passage: "variously called vibration, effulgence, repose, the living being,
#           the Heart and intuition"
# Generator: L-system — one name per branch layer
# Concept: one reality expressed through multiple names

def s02_six_names(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H-80

    names = ["spanda", "sphurattā", "viśrānti", "jīva", "hṛdaya", "pratibhā"]
    angle = math.radians(22)
    step = 5

    axiom = "F"
    rules = {"F": "F[+F]F[-F]F"}
    s = axiom
    for _ in range(5):
        s = ''.join(rules.get(c,c) for c in s)

    n = int(len(s) * min(1, u * 1.2))
    partial = s[:n]
    stack = []
    cur_x, cur_y = cx, cy
    ca = -math.pi/2
    branch_count = 0

    for c in partial:
        if c == 'F':
            nx = cur_x + step * math.cos(ca)
            ny = cur_y + step * math.sin(ca)
            nx = max(10, min(W-10, nx))
            ny = max(10, min(H-10, ny))
            d.line((cur_x, cur_y, nx, ny), fill=INK, width=1)
            cur_x, cur_y = nx, ny
        elif c == '+': ca += angle
        elif c == '-': ca -= angle
        elif c == '[': stack.append((cur_x, cur_y, ca)); branch_count += 1
        elif c == ']' and stack:
            if branch_count < 7 and len(stack) > 0:
                idx_name = min(branch_count // 1, 5)
                d.text((cur_x+10, cur_y-20), names[min(idx_name, len(names)-1)], fill=GOLD)
            cur_x, cur_y, ca = stack.pop()

    d.text((60, 60), "2", fill=MUTED)
    d.text((60, 90), "six names for one pulse", fill=INK)
    return im

# ═══════════════════════════════════════════════════════════════════
# Scene 3: Wave Upon Wave — phyllotaxis
# ═══════════════════════════════════════════════════════════════════
# Passage: "Wave upon wave of its universal pulsation arises from the
#           ocean of the Heart and merges back into it."
# Generator: phyllotaxis / golden-angle point field
# Concept: multiplicity arising from one center

def s03_wave_upon_wave(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    n = int(200 * s_(0, 1, u))
    for i in range(n):
        a = i * 2.4  # golden angle approximation
        r = 5 * math.sqrt(i) * (1 + 0.1 * math.sin(t + i*0.05))
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        sz = 1.5 + p(t + i*0.02, 0, 0.5)
        shade = int(150 + 100 * p(t + i*0.03, 0, 0.3))
        d.ellipse((x-sz, y-sz, x+sz, y+sz), fill=(shade, shade-30, shade-60))

    # Ocean of the Heart — center
    d.ellipse((cx-8, cy-8, cx+8, cy+8), fill=GOLD)

    d.text((60, 60), "3", fill=MUTED)
    d.text((60, 90), "wave upon wave", fill=INK)
    d.text((60, 120), "golden-angle phyllotaxis", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# Scene 4: The Breath Becomes Pulse — braided spline
# ═══════════════════════════════════════════════════════════════════
# Passage: "the vitalizing power of the breath... is vibration (spanda)"
# Generator: braided spline — two strands weaving
# Concept: breath and pulse as one movement

def s04_breath_pulse(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    stride = 4
    pts1, pts2 = [], []
    for x in range(-300, 301, stride):
        y1 = 100 * p(t + x*0.01, 0, 0.4)
        y2 = 100 * p(t + x*0.01 + 0.5, 0, 0.4)
        pts1.append((cx+x, cy+y1-30))
        pts2.append((cx+x, cy+y2+30))

    progress = int(len(pts1) * s_(0, 1, u))
    for i in range(1, progress):
        d.line((pts1[i-1][0], pts1[i-1][1], pts1[i][0], pts1[i][1]), fill=GOLD, width=1)
        d.line((pts2[i-1][0], pts2[i-1][1], pts2[i][0], pts2[i][1]), fill=CRIMSON, width=1)
        # Cross-connections
        if i % 8 == 0:
            d.line((pts1[i][0], pts1[i][1], pts2[i][0], pts2[i][1]), fill=MUTED, width=1)

    d.text((60, 60), "4", fill=MUTED)
    d.text((60, 90), "breath and pulse", fill=INK)
    d.text((60, 120), "two strands of one movement", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# Scene 5: The Centre Between — moiré interference
# ═══════════════════════════════════════════════════════════════════
# Passage: "the centre between two thoughts... the Heart, the pulsing core"
# Generator: moiré / interference — two patterns meeting at center
# Concept: the gap between is the source

def s05_the_centre(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Two expanding wave patterns from opposite sides
    for ring in range(8):
        r1 = (30 + ring * 25 + 10 * p(t, ring*0.3, 0.5)) * (0.5 + 0.5 * u)
        r2 = (30 + ring * 25 + 10 * p(t + 0.5, ring*0.3, 0.5)) * (0.5 + 0.5 * u)
        a1, a2 = 0.2 - ring*0.02, 0.2 - ring*0.02
        if a1 > 0:
            d.ellipse((cx-150-r1, cy-r1, cx-150+r1, cy+r1), outline=(GOLD[0],GOLD[1],GOLD[2],int(255*a1)), width=1)
            d.ellipse((cx+150-r2, cy-r2, cx+150+r2, cy+r2), outline=(CRIMSON[0],CRIMSON[1],CRIMSON[2],int(255*a2)), width=1)

    # The centre — empty, luminous
    if u > 0.4:
        a = s_(0.4, 0.6, u)
        d.ellipse((cx-12, cy-12, cx+12, cy+12), fill=(GOLD[0],GOLD[1],GOLD[2],int(100*a)))

    d.text((60, 60), "5", fill=MUTED)
    d.text((60, 90), "the centre between", fill=INK)
    d.text((60, 120), "moiré interference at the gap", fill=MUTED)
    return im

# ═══════════════════════════════════════════════════════════════════
# Scene 6: Cosmic Bliss — expanding radial
# ═══════════════════════════════════════════════════════════════════
# Passage: "the sixth is complete expansion, experienced as Cosmic Bliss"
# Generator: radial expansion / wheel
# Concept: the pulse recognizes itself as universal

def s06_cosmic_bliss(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Radial wheel — expanding outward
    for i in range(20):
        r = (10 + i * 30) * (0.3 + 0.7 * u)
        a = 0.25 - i * 0.01
        if a < 0: continue
        shade = GOLD if i % 2 == 0 else CRIMSON
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=shade, width=1)
        d.line((cx, cy, cx+r*math.cos(t*0.1+i*0.314), cy+r*math.sin(t*0.1+i*0.314)), fill=MUTED, width=1)

    # Center
    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=GOLD)

    d.text((60, 60), "6", fill=MUTED)
    d.text((60, 90), "cosmic bliss", fill=INK)
    d.text((60, 120), "complete expansion — jagadānanda", fill=MUTED)

    return im

# ═══════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════

SPANDA_PACK = [
    ("inner_exertion", s01_inner_exertion, 12, "spanda as the pulse before form — harmonograph"),
    ("six_names", s02_six_names, 12, "six names unfolding — L-system"),
    ("wave_upon_wave", s03_wave_upon_wave, 12, "phyllotaxis from the Heart"),
    ("breath_pulse", s04_breath_pulse, 12, "breath and pulse as braided strands"),
    ("the_centre", s05_the_centre, 12, "moiré at the gap between"),
    ("cosmic_bliss", s06_cosmic_bliss, 12, "complete expansion — radial wheel"),
]

KNOWLEDGE_DOSSIER = """# Agent Knowledge Dossier — Spanda Kārikā Scene System

## Doctrine→Motion

- inner exertion (udyoga) → harmonograph / progressive stroke
- six names of spanda → L-system unfolding, one name per layer
- wave upon wave (sāmānyaspanda) → phyllotaxis / golden-angle field
- vital breath as vibration → braided spline, two strands weaving
- the centre between → moiré interference at the gap
- cosmic bliss (jagadānanda) → radial wheel / complete expansion

## Source
Passages from Tantrāloka Āhnika 5-6 (Dyczkowski Vol.4) and Spanda Kārikā.
Full source material at content/research-objects/source-material-spanda.md

## Reuse
- Emanation passages: scenes 1, 3
- Multiplicity/names: scene 2
- Breath/body: scene 4
- Meditation/gap: scene 5
- Culmination: scene 6

## Renderer schema
{
  "generator": "harmonograph | lsystem | phyllotaxis | braid | moire | radial",
  "duration": 12,
  "style": {"background": "dark", "primary": "gold", "secondary": "crimson"},
  "reveal": "progressive"
}
"""
