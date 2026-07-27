"""Pack 7: Mantra Cycles & Breath — Cakrodaya in the Tantrāloka."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x): t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1; return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def s1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    ap = 50 + 40 * p(t * 0.4, 0, 0.4)
    d.rectangle((cx - 10, cy - ap, cx + 10, cy + ap), outline=I_, width=2)
    for y in range(-int(ap), int(ap), 6):
        wave = 6 * p(t * 2 + y * 0.04, 0, 0.6)
        d.line((cx + wave - 15, cy + y, cx + wave + 15, cy + y), fill=M, width=1)
    d.text((60, 60), "breath cycle", fill=I_); d.text((60, 95), "prāṇacakra", fill=M); return im

def s2(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(3):
        a2 = S(0.05 + k * 0.2, 0.25 + k * 0.2, u)
        y = cy - 60 + k * 60
        d.ellipse((cx - 50 * a2, y - 12, cx + 50 * a2, y + 12), outline=[G, C_, I_][k], width=2)
        d.text((cx + 60, y - 8), ["inhalation", "retention", "exhalation"][k], fill=M)
    d.text((60, 60), "three phases", fill=I_); return im

def s3(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(8):
        a2 = S(0.03 + k * 0.07, 0.2 + k * 0.07, u)
        ang = k * 0.785 + t * 0.04; r = 30 + 70 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy, x, y), fill=G, width=1)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=G)
    d.text((60, 60), "mantra on the breath", fill=I_); return im

def s4(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for ring in range(6):
        r = (20 + ring * 25) * S(0, 1, u)
        a = 0.2 - ring * 0.03
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(G[0], G[1], G[2], int(255 * max(0, a))), width=1)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "cakrodaya", fill=I_); d.text((60, 95), "the wheel arises from breath", fill=M); return im

def s5(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(5):
        y = cy - 80 + k * 40; a2 = S(0.05 + k * 0.1, 0.2 + k * 0.1, u)
        d.ellipse((cx - 50 * a2, y - 8, cx + 50 * a2, y + 8), outline=I_, width=2)
    d.text((60, 60), "mantra ascends", fill=I_); d.text((60, 95), "breath by breath", fill=M); return im
