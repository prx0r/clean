"""Complexity pack: Mandelbrot, cellular automata, contained L-systems.
Minimal. One rhythm unifies all motion."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
random.seed(42)

GOLD = (208, 172, 91); CRIMSON = (141, 44, 57); DARK = (12, 12, 15)
INK = (235, 231, 220); MUTED = (145, 141, 132); WHITE = (248, 246, 240)

# Universal pulse — all motion rides this rhythm
def pulse(t, offset=0, speed=1.0):
    """Single unified vibration: smooth sine, all scenes use this."""
    return 0.5 + 0.5 * math.sin(t * speed + offset)

def smoothstep(e0, e1, x):
    t = max(0, min(1, (x-e0)/(e1-e0))) if e1!=e0 else 1
    return t*t*(3-2*t)

# ═══════════════════════════════════════════════════════════════════
# 1. MANDELBROT SET — slow explore
# ═══════════════════════════════════════════════════════════════════
def mandelbrot(c, max_iter=50):
    z = 0+0j
    for i in range(max_iter):
        z = z*z + c
        if abs(z) > 2:
            return i / max_iter
    return 1.0

def scene_mandelbrot(t, u, idx):
    """Mandelbrot set — slowly zooming, minimal palette."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    # Slow zoom into the set
    zoom = 0.5 + 0.3 * pulse(t, 0, 0.05)
    cx, cy = -0.5 + 0.3 * pulse(t, 0.5, 0.03), 0
    r = 2.0 / zoom

    x0, x1 = cx - r, cx + r
    y0, y1 = cy - r * H/W, cy + r * H/W

    for px in range(0, W, 4):
        for py in range(0, H, 4):
            x = x0 + (x1-x0) * px / W
            y = y0 + (y1-y0) * py / H
            m = mandelbrot(complex(x, y), 30)
            if m >= 1:
                d.point((px, py), fill=DARK)
            else:
                val = int(200 * m * pulse(t, py*0.01, 0.1))
                d.point((px, py), fill=(val, val//2, val//3))

    return im

# ═══════════════════════════════════════════════════════════════════
# 2. JULIA SET — morphing
# ═══════════════════════════════════════════════════════════════════
def julia(z, c, max_iter=40):
    for i in range(max_iter):
        z = z*z + c
        if abs(z) > 2:
            return i / max_iter
    return 1.0

def scene_julia(t, u, idx):
    """Julia set — morphing with the pulse."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    # Julia parameter morphs with the pulse
    cr = 0.7885 * math.cos(t * 0.05)
    ci = 0.7885 * math.sin(t * 0.05)
    c = complex(cr, ci)

    x0, x1 = -1.5, 1.5
    y0, y1 = -1.5, 1.5

    for px in range(0, W, 3):
        for py in range(0, H, 3):
            zx = x0 + (x1-x0) * px / W
            zy = y0 + (y1-y0) * py / H
            m = julia(complex(zx, zy), c, 30)
            if m >= 1:
                d.point((px, py), fill=DARK)
            else:
                b = int(180 * (1-m) * pulse(t, px*0.005, 0.2))
                d.point((px, py), fill=(b//2, b, b//2))

    return im

# ═══════════════════════════════════════════════════════════════════
# 3. CELLULAR AUTOMATON — Rule 30
# ═══════════════════════════════════════════════════════════════════
def scene_cellular(t, u, idx):
    """Wolfram Rule 30 — growing from a single seed."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    n_rows = min(H // 6, 60)
    n_cols = W // 6
    grid = [[0] * n_cols for _ in range(n_rows)]
    grid[0][n_cols // 2] = 1

    for row in range(1, n_rows):
        for col in range(1, n_cols - 1):
            left = grid[row-1][col-1]
            center = grid[row-1][col]
            right = grid[row-1][col+1]
            # Rule 30: 111->0, 110->0, 101->0, 100->1, 011->1, 010->1, 001->1, 000->0
            pattern = (left << 2) | (center << 1) | right
            grid[row][col] = 1 if pattern in (1,2,3,4) else 0

    progress = min(n_rows, int(n_rows * smoothstep(0, 8, t)))
    for row in range(progress):
        for col in range(n_cols):
            if grid[row][col]:
                b = int(200 * pulse(t, row*0.3, 0.5))
                d.point((col*6, row*6), fill=(b, b//2, 0))

    return im

# ═══════════════════════════════════════════════════════════════════
# 4. CONTAINED L-SYSTEM — stays on page, minimal
# ═══════════════════════════════════════════════════════════════════
def scene_contained_tree(t, u, idx):
    """L-system tree that stays within frame. Short branches, tight angle."""
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    # Controlled grammar — won't escape
    axiom = "F"
    rules = {"F": "F[+F]F[-F]F"}
    angle = math.radians(25)
    step = 6

    # Generate
    s = axiom
    for _ in range(4):
        s = ''.join(rules.get(c, c) for c in s)

    progress = clamp(t / 8)
    n = int(len(s) * min(1, progress))
    partial = s[:n]

    # Draw with strict containment
    cx, cy = W//2, H-60
    stack = []
    cur_x, cur_y = cx, cy
    cur_angle = -math.pi/2

    for c in partial:
        if c == 'F':
            nx = cur_x + step * math.cos(cur_angle)
            ny = cur_y + step * math.sin(cur_angle)
            # Clamp to frame
            nx = max(10, min(W-10, nx))
            ny = max(10, min(H-10, ny))
            d.line((cur_x, cur_y, nx, ny), fill=(40, 40, 40), width=1)
            cur_x, cur_y = nx, ny
        elif c == '+': cur_angle += angle
        elif c == '-': cur_angle -= angle
        elif c == '[': stack.append((cur_x, cur_y, cur_angle))
        elif c == ']' and stack: cur_x, cur_y, cur_angle = stack.pop()

    return im

def clamp(v, lo=0, hi=1): return max(lo, min(hi, v))

# ═══════════════════════════════════════════════════════════════════
# 5. MINIMAL DYNAMIC ENERGY — simplified, rhythmic
# ═══════════════════════════════════════════════════════════════════
def scene_minimal_energy(t, u, idx):
    """Dynamic energy stripped down: one pulsing line, one rhythm."""
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Single undulating line — the pulse is the vibration
    pts = []
    for x in range(-200, 201, 4):
        y = 80 * pulse(t + x*0.01, 0, 0.8) - 40
        px = cx + x
        py = cy + y
        pts.append((px, py))

    for i in range(1, len(pts)):
        a = pulse(t + i*0.1, 0, 0.5)
        shade = int(40 + 60 * a)
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
               fill=(shade, shade, shade), width=1)

    return im

# ═══════════════════════════════════════════════════════════════════
# 6. GAME OF LIFE — glider
# ═══════════════════════════════════════════════════════════════════
def scene_game_of_life(t, u, idx):
    """Conway's Game of Life — glider moving across field."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    n = 60
    cell_size = W // n
    grid = [[0]*n for _ in range(n)]

    # Glider
    glider = [(0,1),(1,2),(2,0),(2,1),(2,2)]
    offset_x = int(20 * smoothstep(0, 15, t)) % n
    for gx, gy in glider:
        grid[gy][(gx + offset_x) % n] = 1

    for row in range(n):
        for col in range(n):
            if grid[row][col]:
                a = pulse(t + col*0.1, 0, 0.3)
                b = int(200 * a)
                d.rectangle((col*cell_size, row*cell_size,
                            (col+1)*cell_size, (row+1)*cell_size),
                            fill=(b, b, b//2))

    return im

# ═══════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════
COMPLEXITY_SCENES = [
    ("mandelbrot", scene_mandelbrot, 12, "Mandelbrot set — slow zoom"),
    ("julia", scene_julia, 12, "Julia set — morphing"),
    ("cellular_automaton", scene_cellular, 10, "Rule 30 cellular automaton"),
    ("contained_tree", scene_contained_tree, 10, "L-system tree — contained"),
    ("minimal_energy", scene_minimal_energy, 8, "one pulsing line"),
    ("game_of_life", scene_game_of_life, 12, "Game of Life — glider"),
]
