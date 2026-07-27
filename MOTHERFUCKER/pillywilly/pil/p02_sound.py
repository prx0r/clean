"""Pack 2: Tantraloka Sound Metaphysics — 50 phonemes, four levels of speech."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720
D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

# ── Scene 1: Phonemes as Reflective Powers ────────────────────────
def s1(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Letters arranged in a spiral
    letters = "aāiīuūṛḷeaitoauṃḥkkhgghṅcchjjhñṭṭhḍḍhṇtthddhnpphbbhmyrlvśṣsh"
    for k, l in enumerate(letters):
        a = S(0.02 + k * 0.012, 0.2 + k * 0.012, u)
        if a <= 0: continue
        ang = k * 0.25 + t * 0.02
        r = 40 + 80 * (k / len(letters)) * u
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) * 0.7
        d.text((x - 5, y - 6), l, fill=(G[0], G[1], G[2], int(200 * a)))

    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "fifty phonemes", fill=I_)
    d.text((60, 95), "forms of Śiva's reflective awareness", fill=M)
    return im

# ── Scene 2: Four Levels of Speech ────────────────────────────────
def s2(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    levels = [("parā", "supreme", G), ("paśyantī", "seeing", I_),
              ("madhyamā", "mental", C_), ("vaikharī", "spoken", M)]

    for k, (name, desc, col) in enumerate(levels):
        a = S(0.05 + k * 0.15, 0.2 + k * 0.15, u)
        y = cy - 120 + k * 70
        r = 80 * a
        d.ellipse((cx - r, y - 15, cx + r, y + 15), outline=col, width=2)
        d.text((cx - 25, y - 8), name, fill=col)
        if k > 0:
            d.line((cx, y - 15 - 5, cx, y + 15 + 5), fill=M, width=1)

    d.text((60, 60), "four levels of speech", fill=I_)
    d.text((60, 95), "from silence to articulation", fill=M)
    return im

# ── Scene 3: Mātṛkā and Mālinī Cakras ────────────────────────────
def s3(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Outer cycle (Mātṛkā) — conventional order
    for k in range(50):
        a = S(0.02 + k * 0.012, 0.3 + k * 0.012, u)
        if a <= 0: continue
        ang = k * 0.126 - math.pi / 2
        r = 130 + 10 * math.sin(k * 0.5 + t * 0.1)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(G[0], G[1], G[2], int(150 * a)))

    # Inner cycle (Mālinī) — esoteric order
    for k in range(50):
        a = S(0.15 + k * 0.012, 0.4 + k * 0.012, u)
        if a <= 0: continue
        ang = k * 0.126 + t * 0.03
        r = 60 + 10 * math.cos(k * 0.7 + t * 0.08)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(C_[0], C_[1], C_[2], int(150 * a)))

    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=G)
    d.text((60, 60), "mātṛkā & mālinī", fill=I_)
    d.text((60, 95), "two orders of the phonemes", fill=M)
    return im

# ── Scene 4: The AHAṂ Cycle ───────────────────────────────────────
def s4(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # A-H-AṂ — the three moments of the I
    labels = [("A", "anuttara", cx - 100), ("H", "visarga", cx), ("AṂ", "anusvāra", cx + 100)]
    for k, (letter, meaning, x) in enumerate(labels):
        a = S(0.05 + k * 0.2, 0.25 + k * 0.2, u)
        r = 30 + 20 * p(t + k * 0.3, 0, 0.5)
        d.ellipse((x - r, cy - r, x + r, cy + r), outline=G if k % 2 == 0 else C_, width=2)
        d.text((x - 8, cy - 8), letter, fill=I_)
        d.text((x - 25, cy + r + 12), meaning, fill=M)

    # Flow — arrows between them
    if u > 0.3:
        for k in range(2):
            a = S(0.3 + k * 0.15, 0.5 + k * 0.15, u)
            x1 = labels[k][2] + 30
            x2 = labels[k + 1][2] - 30
            d.line((x1, cy, x2, cy), fill=(G[0], G[1], G[2], int(150 * a)), width=2)

    d.text((60, 60), "ahaṁ — I am", fill=I_)
    d.text((60, 95), "the cycle of self-awareness", fill=M)
    return im

# ── Scene 5: Sound Becomes World ──────────────────────────────────
def s5(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Wave → particles → forms
    for x in range(-300, 301, 6):
        y = 80 * p(t * 0.5 + x * 0.006, 0, 0.5)
        shade = int(100 + 155 * S(0, 0.5, u))
        d.line((cx + x, cy + y - 2, cx + x, cy + y + 2), fill=(shade, shade, shade), width=1)

    # Condensing into forms
    for k in range(12):
        a = S(0.05 + k * 0.05, 0.4 + k * 0.05, u)
        if a <= 0: continue
        ang = k * 0.524 + t * 0.05
        r = 30 + 60 * u
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) + 30 * p(t + k * 0.2, 0, 0.5)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=G)

    d.text((60, 60), "sound becomes world", fill=I_)
    d.text((60, 95), "vibration condenses into form", fill=M)
    return im
