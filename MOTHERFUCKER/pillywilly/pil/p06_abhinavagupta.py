"""Pack 6: Abhinavagupta — life and daily practice of the great Tantric master."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57); B = (25, 20, 18)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def s1(t, u, i):
    im = ca(B); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    d.ellipse((cx - 50, cy - 60, cx + 50, cy + 40), outline=I_, width=2)
    d.line((cx, cy + 40, cx - 40, cy + 120), fill=I_, width=2)
    d.line((cx, cy + 40, cx + 40, cy + 120), fill=I_, width=2)
    d.ellipse((cx - 40, cy - 80, cx + 40, cy - 10), outline=I_, width=2)
    for k in range(8):
        a = t * 0.05 + k * 0.785; r = 80 + 30 * S(0, 1, u)
        x = cx + r * math.cos(a); y = cy + r * math.sin(a)
        d.line((cx, cy - 20, x, y), fill=G, width=1)
    d.text((60, 60), "abhinavagupta", fill=I_); d.text((60, 95), "10th-century Tantric master", fill=M); return im

def s2(t, u, i):
    im = ca(B); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(5):
        y = cy - 80 + i_ * 40; a = S(0.05 + i_ * 0.1, 0.2 + i_ * 0.1, u)
        d.ellipse((cx - 60 * a, y - 10, cx + 60 * a, y + 10), outline=[G, C_, I_, G, C_][i_], width=2)
    d.text((60, 60), "daily practice", fill=I_); d.text((60, 95), "dawn purification to night", fill=M); return im

def s3(t, u, i):
    im = ca(D); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(8):
        a2 = S(0.05 + k * 0.07, 0.25 + k * 0.07, u)
        ang = k * 0.785 + t * 0.03; r = 30 + 60 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.text((x - 8, y - 8), "oṃ", fill=G)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=G)
    d.text((60, 60), "meditation & pūjā", fill=I_); return im

def s4(t, u, i):
    im = ca(B); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(20):
        a2 = S(0.02 + i_ * 0.03, 0.15 + i_ * 0.03, u)
        ang = i_ * 0.314 + t * 0.01; r = 40 + 40 * (i_ / 20) * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.line((cx, cy - 20, x, y), fill=(I_[0], I_[1], I_[2], int(100 * a2)), width=1)
    d.text((60, 60), "study of texts", fill=I_); d.text((60, 95), "master of all systems", fill=M); return im

def s5(t, u, i):
    im = ca(B); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(6):
        a2 = S(0.05 + k * 0.1, 0.25 + k * 0.1, u)
        y = cy - 80 + k * 30; x = cx - 100 + 40 * math.sin(k * 1.3 + t * 0.5)
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=G)
    d.line((cx, cy + 40, cx - 30, cy + 80), fill=I_, width=2)
    d.line((cx, cy + 40, cx + 30, cy + 80), fill=I_, width=2)
    d.text((60, 60), "teaching & dictation", fill=I_); return im
