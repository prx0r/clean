"""Pack 1: Tantraloka Reflection Doctrine (Pratibimbavāda).
All phenomena are reflections in the mirror of consciousness."""

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

# ── Scene 1: The Mirror Itself ────────────────────────────────────
def s1(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Mirror — luminous oval
    for ring in range(6):
        r = (40 + ring * 30) * (0.3 + 0.7 * u)
        a = 0.2 - ring * 0.03
        if a > 0:
            d.ellipse((cx - r, cy - r * 1.2, cx + r, cy + r * 1.2),
                      outline=(G[0], G[1], G[2], int(255 * a)), width=1)

    # Light source at center
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=G)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=I_)

    d.text((60, 60), "pratibimbavāda", fill=I_)
    d.text((60, 95), "the doctrine of reflection", fill=M)
    d.text((60, 130), "all phenomena shine within", fill=M)
    d.text((60, 165), "consciousness alone", fill=M)
    return im

# ── Scene 2: Reflections Arise ────────────────────────────────────
def s2(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Mirror surface
    for ring in range(4):
        r = (30 + ring * 25) * (0.3 + 0.7 * u)
        d.ellipse((cx - r, cy - r * 1.3, cx + r, cy + r * 1.3),
                  outline=(G[0], G[1], G[2], int(40)), width=1)

    # Reflections appearing — colored dots
    for k in range(16):
        a = S(0.05 + k * 0.04, 0.4 + k * 0.04, u)
        if a <= 0: continue
        ang = k * 0.393 + t * 0.02
        r = 80 + 40 * math.sin(k * 1.3 + t * 0.1)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) * 1.3
        sz = 2 + a * 3
        shade = k % 3
        if shade == 0:
            col = G
        elif shade == 1:
            col = C_
        else:
            col = I_
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(col[0], col[1], col[2], int(200 * a)))

    d.text((60, 60), "reflections arise", fill=I_)
    d.text((60, 95), "without disturbing the mirror", fill=M)
    return im

# ── Scene 3: Mirror and Image Inseparable ─────────────────────────
def s3(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Two paired forms — mirror and image
    for side, (x_off, col) in enumerate([(-120, G), (120, C_)]):
        for ring in range(5):
            r = (20 + ring * 18) * (0.3 + 0.7 * u)
            a = 0.2 - ring * 0.035
            if a > 0:
                d.ellipse((cx + x_off - r, cy - r, cx + x_off + r, cy + r),
                          outline=(col[0], col[1], col[2], int(255 * a)), width=1)

    # Connection — they are the same
    if u > 0.3:
        for k in range(10):
            a = S(0.3 + k * 0.04, 0.5 + k * 0.04, u)
            y = cy - 80 + k * 18
            d.line((cx - 100, y, cx + 100, y), fill=(G[0], G[1], G[2], int(60 * a)), width=1)

    d.text((60, 60), "mirror and image", fill=I_)
    d.text((60, 95), "one cannot appear", fill=M)
    d.text((60, 130), "without the other", fill=M)
    return im

# ── Scene 4: Letters as Reflective Powers ─────────────────────────
def s4(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # The alphabet of consciousness — letters radiating
    letters = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ḷ", "e", "ai", "o", "au",
               "ka", "kha", "ga", "gha", "ṅa", "ca", "cha", "ja", "jha", "ña",
               "ṭa", "ṭha", "ḍa", "ḍha", "ṇa", "ta", "tha", "da", "dha", "na",
               "pa", "pha", "ba", "bha", "ma", "ya", "ra", "la", "va",
               "śa", "ṣa", "sa", "ha", "kṣa"]

    for k, l in enumerate(letters):
        a = S(0.02 + k * 0.015, 0.15 + k * 0.015, u)
        if a <= 0: continue
        ang = k * 0.14 + t * 0.02
        r = 60 + 30 * (k / len(letters)) * u
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) * 0.8
        d.text((x - 6, y - 6), l, fill=(G[0], G[1], G[2], int(200 * a)))

    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "fifty reflective powers", fill=I_)
    d.text((60, 95), "the alphabet of consciousness", fill=M)
    return im

# ── Scene 5: Recognition as Return ────────────────────────────────
def s5(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Scattered elements returning to center
    for k in range(24):
        prog = S(0.05 + k * 0.025, 0.5 + k * 0.025, u)
        if prog <= 0: continue
        ta = k * 0.262
        start_r = 250
        end_r = 30
        r = start_r + (end_r - start_r) * prog
        ang = ta + (1 - prog) * (k * 0.06)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=I_)

    if u > 0.6:
        a = S(0.6, 0.8, u)
        d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(G[0], G[1], G[2], int(200 * a)))

    d.text((60, 60), "recognition", fill=I_)
    d.text((60, 95), "the reflections return", fill=M)
    d.text((60, 130), "to their source", fill=M)
    return im
