"""Pack 5: Spanda Kārikā Second Flow — how mantras work."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def s1(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for i_ in range(6):
        r = (20 + i_ * 30) * (0.3 + 0.7 * u)
        a = 0.2 - i_ * 0.03
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(G[0], G[1], G[2], int(255 * max(0, a))), width=1)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "spanda — second flow", fill=I_); d.text((60, 95), "the secret of mantra", fill=M); return im

def s2(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for x_ in range(-300, 301, 4):
        y1 = 40 * p(t * 0.6 + x_ * 0.006, 0, 0.5)
        y2 = 40 * p(t * 0.6 + x_ * 0.006 + 0.5, 0, 0.5)
        d.line((cx + x_, cy + y1 - 30, cx + x_, cy + y2 + 30), fill=(G[0], G[1], G[2], int(80)), width=1)
    d.text((60, 60), "mantra as vibration", fill=I_); return im

def s3(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(8):
        a = S(0.05 + k * 0.07, 0.25 + k * 0.07, u)
        ang = k * 0.785 + t * 0.05; r = 40 + 60 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.text((x - 10, y - 8), ["oṃ", "hrīṃ", "klīṃ", "aiṃ", "sauḥ", "huṃ", "phaṭ", "svāhā"][k], fill=G if k % 2 == 0 else C_)
    d.text((60, 60), "seed syllables", fill=I_); return im

def s4(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(5):
        y = cy - 80 + k * 40
        a = S(0.05 + k * 0.12, 0.2 + k * 0.12, u)
        d.ellipse((cx - 60 * a, y - 10, cx + 60 * a, y + 10), outline=I_, width=2)
        d.line((cx, y + 10, cx, y + 30), fill=M, width=1)
    d.text((60, 60), "mantra ascends", fill=I_); d.text((60, 95), "through the levels of speech", fill=M); return im

def s5(t, u, i):
    im = ca(); d = ImageDraw.Draw(im); cx, cy = W // 2, H // 2
    for k in range(16):
        a = S(0.03 + k * 0.04, 0.3 + k * 0.04, u)
        ang = k * 0.393 + t * 0.02; r = 20 + 90 * u
        x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=G)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=G)
    d.text((60, 60), "mantra dissolves", fill=I_); d.text((60, 95), "into the pulse", fill=M); return im
