"""Minimal forms — pure geometry, one pulse, nothing extra.
Each form is the simplest possible representation of a concept."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
DARK = (12, 12, 15); WHITE = (248, 246, 240); CHARCOAL = (40, 40, 40)
MUTED = (145, 141, 132); CRIMSON = (141, 44, 57); GOLD = (208, 172, 91)

# ONE pulse — everything rides this
def p(t, offset=0, speed=1.0):
    return 0.5 + 0.5 * math.sin(t * speed + offset)

def canvas(bg=WHITE): return Image.new("RGB", (W, H), bg)

# ── 1. Circle that breathes ────────────────────────────────────────
def scene_breathing(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    r = 60 + 40 * p(t, 0, 0.3)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=CHARCOAL, width=2)
    return im

# ── 2. Line that waves ────────────────────────────────────────────
def scene_wave(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    pts = []
    for x in range(-300, 301, 6):
        pts.append((cx + x, cy + 60 * p(t + x*0.008, 0, 0.6)))
    for i in range(1, len(pts)):
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]), fill=CHARCOAL, width=1)
    return im

# ── 3. Single rotating line ───────────────────────────────────────
def scene_rotating(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    r = 150
    a = t * 0.3
    d.line((cx, cy, cx + r*math.cos(a), cy + r*math.sin(a)), fill=CHARCOAL, width=2)
    return im

# ── 4. Expanding ring ─────────────────────────────────────────────
def scene_expanding_ring(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    r = 20 + 200 * p(t, 0, 0.2)
    for i in range(3):
        ri = r + i*20
        a = p(t + i*0.3, 0, 0.5)
        d.ellipse((cx-ri, cy-ri, cx+ri, cy+ri), outline=CHARCOAL, width=1)
    return im

# ── 5. Falling dot ────────────────────────────────────────────────
def scene_falling(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx = W//2
    y = 100 + 520 * p(t, 0, 0.15)
    v = p(t, 0, 0.3)
    r = 4 + 6 * v
    d.ellipse((cx-r, y-r, cx+r, y+r), fill=CHARCOAL)
    return im

# ── 6. Two dots approaching ──────────────────────────────────────
def scene_approach(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cy = H//2
    sep = 300 * p(t, 0, 0.2)
    lx, rx = W//2 - sep, W//2 + sep
    d.ellipse((lx-8, cy-8, lx+8, cy+8), fill=CHARCOAL)
    d.ellipse((rx-8, cy-8, rx+8, cy+8), fill=CHARCOAL)
    if sep < 50:
        d.ellipse((W//2-4, cy-4, W//2+4, cy+4), fill=CRIMSON)
    return im

# ── 7. L-system bush (contained) ──────────────────────────────────
def scene_minimal_bush(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H-60
    axiom = "F"
    rules = {"F": "F[+F]F[-F]F"}
    angle = math.radians(25)
    step = 5
    s = axiom
    for _ in range(4):
        s = ''.join(rules.get(c, c) for c in s)
    n = int(len(s) * min(1, t / 6))
    partial = s[:n]
    stack = []; cur_x, cur_y = cx, cy; cur_a = -math.pi/2
    for c in partial:
        if c == 'F':
            nx = cur_x + step * math.cos(cur_a)
            ny = cur_y + step * math.sin(cur_a)
            nx = max(10, min(W-10, nx))
            ny = max(10, min(H-10, ny))
            d.line((cur_x, cur_y, nx, ny), fill=CHARCOAL, width=1)
            cur_x, cur_y = nx, ny
        elif c == '+': cur_a += angle
        elif c == '-': cur_a -= angle
        elif c == '[': stack.append((cur_x, cur_y, cur_a))
        elif c == ']' and stack: cur_x, cur_y, cur_a = stack.pop()
    return im

# ── 8. Grid of dots pulsing ───────────────────────────────────────
def scene_pulsing_dots(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    for row in range(8):
        for col in range(14):
            x = 100 + col * 80
            y = 80 + row * 75
            s = 3 + 6 * p(t + row*0.2 + col*0.15, 0, 0.3)
            d.ellipse((x-s, y-s, x+s, y+s), fill=CHARCOAL)
    return im

# ── 9. Vertical line that grows ───────────────────────────────────
def scene_growing_line(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx = W//2
    h = 500 * min(1, t / 6)
    d.line((cx, H-80, cx, H-80-h), fill=CHARCOAL, width=2)
    dot_r = 3 + 3 * p(t, 0, 0.5)
    d.ellipse((cx-dot_r, H-80-h-dot_r, cx+dot_r, H-80-h+dot_r), fill=CRIMSON)
    return im

# ── 10. Concentric squares ────────────────────────────────────────
def scene_squares(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    for i in range(5):
        s = 60 + i * 50 + 30 * p(t + i*0.2, 0, 0.3)
        x0, y0 = cx-s, cy-s
        x1, y1 = cx+s, cy+s
        d.rectangle((x0, y0, x1, y1), outline=CHARCOAL, width=1)
    return im


FORMS = [
    ("breathing_circle", scene_breathing, 8),
    ("wave", scene_wave, 8),
    ("rotating_line", scene_rotating, 8),
    ("expanding_ring", scene_expanding_ring, 8),
    ("falling_dot", scene_falling, 8),
    ("approach", scene_approach, 10),
    ("minimal_bush", scene_minimal_bush, 8),
    ("pulsing_dots", scene_pulsing_dots, 8),
    ("growing_line", scene_growing_line, 8),
    ("squares", scene_squares, 8),
]
