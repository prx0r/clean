"""Pack 4: Tantraloka Twelve Kālīs — three groups of four consuming phases."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57); BG = (18, 15, 20)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def s1(t, u, i):
    im = ca(BG); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(12):
        a = S(0.02 + k * 0.05, 0.25 + k * 0.05, u)
        ang = k * 0.524 + t * 0.05; r = 30 + 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy, x, y), fill=C_, width=1)
        d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=G, width=2)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=C_)
    d.text((60, 60), "twelve kālīs", fill=I_); d.text((60, 95), "the wheel of consumption", fill=M); return im

def s2(t, u, i):
    im = ca(BG); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(4):
        a = S(0.05 + k * 0.15, 0.25 + k * 0.15, u)
        ang = -math.pi / 2 + k * 1.571; r = 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=G, width=2)
        d.text((x - 15, y - 8), ["sṛṣṭi", "sthiti", "saṃhāra", "anākhyā"][k], fill=G)
    d.text((60, 60), "consuming objectivity", fill=I_); return im

def s3(t, u, i):
    im = ca(BG); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(4):
        a = S(0.05 + k * 0.15, 0.25 + k * 0.15, u)
        ang = math.pi * 0.75 + k * 1.571; r = 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=C_, width=2)
        d.text((x - 20, y - 8), ["kālī", "kālī", "kālī", "kālī"][k], fill=C_)
    d.text((60, 60), "consuming means", fill=I_); return im

def s4(t, u, i):
    im = ca(BG); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(4):
        a = S(0.05 + k * 0.15, 0.25 + k * 0.15, u)
        ang = -math.pi / 4 + k * 1.571; r = 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=I_, width=2)
    d.text((60, 60), "consuming subjectivity", fill=I_); return im

def s5(t, u, i):
    im = ca(BG); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(12):
        ang = k * 0.524 + t * 0.02; r = 30 + 80 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=C_ if k < 4 else (G if k < 8 else I_))
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "the inexplicable wheel", fill=I_); d.text((60, 95), "anākhyacakra", fill=M); return im
