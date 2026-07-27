"""Redone packs — proper care, real geometry, creative intent.
Replaces the batch-built weak packs."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57); W_ = (255, 255, 255)
BLACK = (10, 10, 10)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

# ═══════════════════════════════════════════════════════════════════
# PRATYABHIJÑĀ — Recognition (redone)
# ═══════════════════════════════════════════════════════════════════
# Recognition is the return to self. Mirror, alignment, stability.

def pr_01(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Mirror axis
    d.line((cx, 40, cx, H - 40), fill=M, width=1)

    # Elements scattered → aligned
    for k in range(20):
        prog = S(0.05 + k * 0.025, 0.5 + k * 0.025, u)
        if prog <= 0: continue
        ta = k * 0.314
        start_r = 260
        end_r = 70
        r = start_r + (end_r - start_r) * prog
        ang = ta + (1 - prog) * (k * 0.08)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        sz = 2 + prog * 2
        shade = int(200 * (1 - prog * 0.5))
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(shade, shade, shade))

    # Center emerges
    if u > 0.5:
        a = S(0.5, 0.7, u)
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=G)

    # Text
    d.text((60, 60), "pratyabhijñā", fill=I_)
    d.text((60, 95), "recognition", fill=I_)
    d.text((60, 130), "the return to self", fill=M)
    return im

def pr_02(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # A single harmonograph that settles
    n = int(200 * S(0, 1, u))
    pts = []
    for j in range(n):
        tj = j * 0.06
        damp = math.exp(-0.03 * tj)
        x = 200 * damp * math.sin(2.0 * tj + 0.3 * math.sin(tj * 0.5))
        y = 200 * damp * math.sin(2.7 * tj + 0.3 * math.cos(tj * 0.5))
        pts.append((cx + x, cy + y))

    for j in range(1, len(pts)):
        alpha = j / len(pts) * 0.6
        shade = int(200 * (1 - j / len(pts)))
        d.line((pts[j - 1][0], pts[j - 1][1], pts[j][0], pts[j][1]),
               fill=(shade, shade, shade), width=1)

    if u > 0.6:
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)

    d.text((60, 60), "recognition as settling", fill=I_)
    d.text((60, 95), "motion stabilizes into", fill=M)
    d.text((60, 130), "self-awareness", fill=M)
    return im

def pr_03(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Two fields becoming one
    for ring in range(5):
        r1 = (30 + ring * 25 + 6 * p(t, ring * 0.3, 0.4)) * (0.5 + 0.5 * u)
        r2 = (30 + ring * 25 + 6 * p(t + 0.5, ring * 0.3, 0.4)) * (0.5 + 0.5 * u)
        a = 0.2 - ring * 0.03
        off = 120 * (1 - u)  # move toward center
        d.ellipse((cx - off - r1, cy - r1, cx - off + r1, cy + r1),
                  outline=(G[0], G[1], G[2], int(255 * a)), width=1)
        d.ellipse((cx + off - r2, cy - r2, cx + off + r2, cy + r2),
                  outline=(C_[0], C_[1], C_[2], int(255 * a)), width=1)

    if u > 0.7:
        a = S(0.7, 0.9, u)
        d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(G[0], G[1], G[2], int(180 * a)))

    d.text((60, 60), "two become one", fill=I_)
    d.text((60, 95), "subject and object", fill=M)
    d.text((60, 130), "recognize their source", fill=M)
    return im


# ═══════════════════════════════════════════════════════════════════
# VBT FOUNDATIONAL — verses 22-27 (redone)
# ═══════════════════════════════════════════════════════════════════
# Foundational practice: attention, breath, body

def vf_01(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Breath column — expanding/contracting
    ap = 80 + 60 * p(t * 0.5, 0, 0.4)
    d.rectangle((cx - 8, cy - ap, cx + 8, cy + ap), outline=I_, width=2)

    # Inhalation/exhalation markers
    for y in range(-int(ap), int(ap), 10):
        wave = 6 * p(t * 2 + y * 0.05, 0, 0.6)
        d.line((cx + wave - 15, cy + y, cx + wave + 15, cy + y), fill=M, width=1)

    # Rising energy points
    for j in range(6):
        yy = cy - ap + (j / 5) * (ap * 2)
        sz = 2 + p(t + j * 0.3, 0, 0.5) * 2
        d.ellipse((cx - sz, yy - sz, cx + sz, yy + sz), fill=G)

    d.text((60, 60), "foundational practice", fill=I_)
    d.text((60, 95), "breath as vehicle", fill=M)
    return im

def vf_02(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Body contour — simple silhouette
    head_r = 25
    d.ellipse((cx - head_r, cy - 100 - head_r, cx + head_r, cy - 100 + head_r), outline=I_, width=2)
    d.rounded_rectangle((cx - 40, cy - 75, cx + 40, cy + 50), radius=20, outline=I_, width=2)
    d.line((cx - 35, cy - 20, cx - 70, cy + 60), fill=I_, width=2)
    d.line((cx + 35, cy - 20, cx + 70, cy + 60), fill=I_, width=2)

    # Inner light
    for j in range(12):
        a = t * 0.1 + j * 0.524
        r = 20 + 30 * p(t + j * 0.1, 0, 0.5)
        x = cx + r * math.cos(a)
        y = cy - 20 + r * math.sin(a)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=G)

    d.text((60, 60), "the body as ground", fill=I_)
    d.text((60, 95), "attention settles in", fill=M)
    d.text((60, 130), "the felt sense", fill=M)
    return im


# ═══════════════════════════════════════════════════════════════════
# VBT CENTRAL CHANNEL — verses 28-31 (redone)
# ═══════════════════════════════════════════════════════════════════

def vc_01(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Ascending light column
    d.line((cx, cy + 200, cx, cy - 200), fill=(G[0], G[1], G[2], int(60)), width=4)

    # Rays of light rising
    for j in range(40):
        y_off = -200 + (400 * j / 40) + 30 * p(t + j * 0.08, 0, 0.5)
        x_off = 15 * p(t + j * 0.12, 0, 0.6) + 5 * math.sin(j * 0.5)
        sz = 1.5 + 2 * p(t + j * 0.05, 0, 0.4)
        shade = int(150 + 105 * p(t + j * 0.05, 0, 0.3))
        d.ellipse((cx + x_off - sz, cy + y_off - sz, cx + x_off + sz, cy + y_off + sz),
                  fill=(shade, shade, shade))

    # Chakric nodes
    for j in range(7):
        yy = cy - 150 + j * 50
        r = 5 + 3 * p(t + j * 0.3, 0, 0.5)
        d.ellipse((cx - r, yy - r, cx + r, yy + r), fill=C_ if j % 2 == 0 else G)

    d.text((60, 60), "central channel", fill=I_)
    d.text((60, 95), "rays of light rising", fill=M)
    return im

def vc_02(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Khecarī — tongue piercing upward, sky
    # Aperture opening to infinite space
    for ring in range(8):
        r = (15 + ring * 20 + 8 * p(t, ring * 0.2, 0.4)) * (0.3 + 0.7 * u)
        a = 0.2 - ring * 0.02
        if a > 0:
            d.ellipse((cx - r, cy - r, cx + r, cy + r),
                      outline=(I_[0], I_[1], I_[2], int(255 * a)), width=1)

    # Sky arc — the khecarī opening
    d.arc((cx - 200, cy - 200, cx + 200, cy + 200), 180, 360, fill=G, width=2)
    if u > 0.5:
        a = S(0.5, 0.7, u)
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=(G[0], G[1], G[2], int(180 * a)))

    d.text((60, 60), "khecarī mudrā", fill=I_)
    d.text((60, 95), "the sky opens within", fill=M)
    return im


# ═══════════════════════════════════════════════════════════════════
# VBT SENSE SPACES — verses 32-39 (redone)
# ═══════════════════════════════════════════════════════════════════

def vs_01(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    senses = [("sight", G), ("sound", I_), ("touch", C_),
              ("taste", (G[0] - 40, G[1] - 20, G[2] - 40)), ("smell", M)]

    for k, (name, color) in enumerate(senses):
        seq = S(0.05 + k * 0.12, 0.25 + k * 0.12, u)
        if seq <= 0: continue
        r = (100 - k * 12) * seq
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=2)
        # Inner dissolution
        if seq > 0.6:
            ir = r * (seq - 0.6) * 2
            d.ellipse((cx - ir, cy - ir, cx + ir, cy + ir), outline=(color[0], color[1], color[2], int(80)), width=1)
        d.text((cx + r + 15, cy - 8), name, fill=M)

    d.text((60, 60), "five sense doors", fill=I_)
    d.text((60, 95), "each opens inward", fill=M)
    return im

def vs_02(t, u, i):
    im = ca()
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2

    # Sensual merging — two fields interpenetrating
    for k in range(30):
        a = t * 0.05 + k * 0.209
        r1 = 120 * S(0, 1, u) * p(t + k * 0.05, 0, 0.4)
        r2 = 120 * S(0, 1, u) * p(t + k * 0.05 + 0.5, 0, 0.4)
        x1 = cx - 60 + r1 * math.cos(a)
        y1 = cy + r1 * math.sin(a)
        x2 = cx + 60 + r2 * math.cos(a + 1.0)
        y2 = cy + r2 * math.sin(a + 1.0)
        d.ellipse((x1 - 2, y1 - 2, x1 + 2, y1 + 2), fill=G)
        d.ellipse((x2 - 2, y2 - 2, x2 + 2, y2 + 2), fill=C_)

    d.text((60, 60), "senses merging", fill=I_)
    d.text((60, 95), "perception becomes", fill=M)
    d.text((60, 130), "pure awareness", fill=M)
    return im


# ═══════════════════════════════════════════════════════════════════
# CATALOG
# ═══════════════════════════════════════════════════════════════════

PACKS = [
    ("pratyabhijna_redone", [pr_01, pr_02, pr_03], [14, 14, 14], "Pratyabhijñā — recognition as return to self"),
    ("vbt_foundational_redone", [vf_01, vf_02], [12, 12], "VBT 22-27 foundational practice"),
    ("vbt_central_channel_redone", [vc_01, vc_02], [12, 12], "VBT 28-31 central channel + khecarī"),
    ("vbt_sense_spaces_redone", [vs_01, vs_02], [12, 12], "VBT 32-39 five sense doors merging"),
]
