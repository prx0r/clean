"""Pack 3: Tantraloka Three Upāyas — Śāmbhava, Śākta, Āṇava."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57); BG = (22, 20, 25)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def s1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(3):
        ang = math.pi / 2 + i_ * 2.094; r = 120 * (0.3 + 0.7 * u)
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=[G, C_, I_][i_], width=2)
        d.text((x - 35, y - 8), ["śāmbhava", "śākta", "āṇava"][i_], fill=[G, C_, I_][i_])
    d.line((cx, cy, cx + 120 * math.cos(math.pi / 2) * (0.3 + 0.7 * u), cy + 120 * math.sin(math.pi / 2) * (0.3 + 0.7 * u)), fill=M, width=1)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "three upāyas", fill=I_); return im

def s2(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for ring in range(5):
        r = (20 + ring * 30) * (0.3 + 0.7 * u)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=G, width=1)
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=G)
    d.text((60, 60), "śāmbhavopāya", fill=G); d.text((60, 95), "divine means — will", fill=M)
    d.text((60, 130), "no thought constructs", fill=M); return im

def s3(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(8):
        a2 = S(0.05 + k * 0.07, 0.25 + k * 0.07, u)
        ang = t * 0.05 + k * 0.785; r = 80 + 40 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy, x, y), fill=C_, width=1)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=C_)
    d.text((60, 60), "śāktopāya", fill=C_); d.text((60, 95), "empowered means — knowledge", fill=M); return im

def s4(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(5):
        y = cy - 100 + i_ * 50; a2 = S(0.05 + i_ * 0.1, 0.25 + i_ * 0.1, u)
        d.ellipse((cx - 50, y - 12, cx + 50, y + 12), outline=I_, width=2)
        d.line((cx, y + 12, cx, y + 38), fill=M, width=1)
    d.text((60, 60), "āṇavopāya", fill=I_); d.text((60, 95), "individual means — action", fill=M); return im

def s5(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(3):
        ang = math.pi / 2 + i_ * 2.094; r = 100 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy, x, y), fill=[G, C_, I_][i_], width=2)
        d.text((x + 15, y - 8), ["will", "knowledge", "action"][i_], fill=[G, C_, I_][i_])
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "one reality", fill=I_); d.text((60, 95), "three approaches", fill=M); return im
