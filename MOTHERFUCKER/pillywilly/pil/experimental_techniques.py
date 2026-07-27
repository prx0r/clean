"""Experimental visual techniques. Each is a reusable effect for scene functions."""

import math, random
from PIL import Image, ImageDraw, ImageFilter

# Standalone color constants (for use without import from renderer)
CHARCOAL = (40, 40, 40)
MUTED = (145, 141, 132)
CRIMSON = (141, 44, 57)
WHITE = (248, 246, 240)
DARK = (12, 12, 15)
INK = (235, 231, 220)
GOLD = (208, 172, 91)

def smoothstep(a, b, x):
    t = max(0, min(1, (x-a)/(b-a))) if b != a else 1
    return t*t*(3-2*t)

random.seed(42)  # deterministic

# ── 1. Live Draw — a path that draws itself progressively ──────────
def live_draw(d, points, progress, color=CHARCOAL, width=2):
    """Draw a polyline incrementally. progress 0.0 → 1.0."""
    if progress <= 0: return
    n = max(1, int((len(points) - 1) * progress))
    for i in range(1, n + 1):
        p1, p2 = points[i - 1], points[i % len(points)]
        d.line((p1[0], p1[1], p2[0], p2[1]), fill=color, width=width)

# ── 2. Variable Speed Draw — same asset, different pacing ─────────
def draw_mountain(d, cx, cy, scale, progress, color=CHARCOAL):
    pts = [(cx-120*scale, cy+40), (cx-80*scale, cy-60*scale),
           (cx-40*scale, cy-20), (cx, cy-80*scale),
           (cx+40*scale, cy-10), (cx+80*scale, cy-50*scale),
           (cx+120*scale, cy+40)]
    live_draw(d, pts, progress, color, 2)

def draw_guru(d, cx, cy, scale, progress):
    # Simple seated figure — 12 points
    pts = [
        (cx, cy-50*scale),  # head top
        (cx-12*scale, cy-35*scale), (cx+12*scale, cy-35*scale),  # head sides
        (cx, cy-30*scale),  # neck
        (cx-30*scale, cy), (cx+30*scale, cy),  # shoulders
        (cx-25*scale, cy+30*scale), (cx+25*scale, cy+30*scale),  # torso
        (cx-35*scale, cy+60*scale), (cx, cy+50*scale), (cx+35*scale, cy+60*scale),  # crossed legs
    ]
    live_draw(d, pts, progress, CHARCOAL, 2)
    if progress > 0.7:
        # Head circle
        r = 16 * scale
        d.ellipse((cx-r, cy-50*scale-r, cx+r, cy-50*scale+r), outline=CHARCOAL, width=2)

def draw_temple(d, cx, cy, scale, progress):
    pts = [
        (cx-60*scale, cy+40*scale), (cx-60*scale, cy-10*scale),
        (cx-40*scale, cy-30*scale), (cx-40*scale, cy-50*scale),
        (cx, cy-70*scale), (cx+40*scale, cy-50*scale),
        (cx+40*scale, cy-30*scale), (cx+60*scale, cy-10*scale),
        (cx+60*scale, cy+40*scale),
    ]
    live_draw(d, pts, progress, CHARCOAL, 2)

def draw_tree(d, cx, cy, scale, progress):
    # Trunk
    if progress > 0:
        t = min(1, progress * 2)
        d.line((cx, cy, cx, cy-60*scale*t), fill=CHARCOAL, width=3)
    # Branches
    if progress > 0.5:
        b = (progress - 0.5) * 2
        d.line((cx, cy-30*scale, cx-30*scale*b, cy-50*scale*b), fill=CHARCOAL, width=2)
        d.line((cx, cy-30*scale, cx+30*scale*b, cy-50*scale*b), fill=CHARCOAL, width=2)
        d.line((cx, cy-50*scale, cx-20*scale*b, cy-65*scale*b), fill=CHARCOAL, width=1)
        d.line((cx, cy-50*scale, cx+20*scale*b, cy-65*scale*b), fill=CHARCOAL, width=1)
    # Canopy
    if progress > 0.7:
        r = 30*scale * ((progress - 0.7) / 0.3)
        d.ellipse((cx-r, cy-70*scale-r, cx+r, cy-70*scale+r), outline=CHARCOAL, width=1)

# ── 3. Ink Bloom — dot that spreads like ink on paper ──────────────
def ink_bloom(d, cx, cy, radius, color=CRIMSON, alpha=1.0, wobble=0.3):
    """Draw a bloom with slightly irregular edges — organic feel."""
    pts = []
    n = 24
    for i in range(n):
        a = i * 2 * math.pi / n
        r = radius * (1 + wobble * math.sin(i * 3 + i * 0.7))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    polygon = [(int(x), int(y)) for x, y in pts]
    d.polygon(polygon, fill=color + (int(255 * alpha),))

# ── 4. Scan Reveal — horizontal line sweeps down revealing content ─
def scan_reveal(base_img, progress, y_start=0, y_end=None):
    """Returns an image where content is revealed by a scan line."""
    if y_end is None: y_end = base_img.height
    scan_y = y_start + (y_end - y_start) * progress
    mask = Image.new("L", base_img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle((0, 0, base_img.width, scan_y), fill=255)
    md.rectangle((0, max(0, scan_y-3), base_img.width, scan_y), fill=200)
    result = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    result.paste(base_img, (0, 0), mask)
    return result

# ── 5. Morph — interpolate between two point sets ─────────────────
def morph(d, pts_from, pts_to, progress, color=CHARCOAL, width=2):
    """Draw an intermediate shape between two point sets."""
    n = min(len(pts_from), len(pts_to))
    for i in range(n):
        x = pts_from[i][0] + (pts_to[i][0] - pts_from[i][0]) * progress
        y = pts_from[i][1] + (pts_to[i][1] - pts_from[i][1]) * progress
        next_i = (i + 1) % n
        nx = pts_from[next_i][0] + (pts_to[next_i][0] - pts_from[next_i][0]) * progress
        ny = pts_from[next_i][1] + (pts_to[next_i][1] - pts_from[next_i][1]) * progress
        d.line((x, y, nx, ny), fill=color, width=width)

def morph_circle_to_square(cx, cy, r, progress):
    """Generate points from circle (progress=0) to square (progress=1)."""
    n = 32
    pts = []
    for i in range(n):
        a = i * 2 * math.pi / n
        circle_r = r
        # Square radius varies with angle
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        square_r = r / max(abs(cos_a), abs(sin_a)) if max(abs(cos_a), abs(sin_a)) > 0 else r
        current_r = circle_r + (square_r - circle_r) * progress
        pts.append((cx + current_r * cos_a, cy + current_r * sin_a))
    return pts

# ── 6. Staggered Reveal — elements appear one after another ───────
def staggered(elements, t, stagger=0.15):
    """Given a list of (start_time, draw_func) pairs, return active at time t."""
    for i, (start, func) in enumerate(elements):
        progress = (t - start) / 0.5  # 0.5s fade per element
        if 0 <= progress <= 1:
            func(smoothstep(0, 1, progress))

# ── 7. Trail Effect — moving dots leave a fading trail ─────────────
class Trail:
    def __init__(self, max_points=20):
        self.points = []
        self.max = max_points

    def update(self, x, y):
        self.points.append((x, y))
        if len(self.points) > self.max:
            self.points.pop(0)

    def draw(self, d, color=CHARCOAL):
        for i, (x, y) in enumerate(self.points):
            alpha = i / len(self.points) if self.points else 0
            d.ellipse((x-2, y-2, x+2, y+2), fill=color + (int(80 * alpha),))

# ── 8. Hand-drawn Wobble — slightly irregular lines ────────────────
def wobble_line(d, x1, y1, x2, y2, color=CHARCOAL, width=2, amount=2):
    """Draw a line with slight hand-drawn irregularity."""
    n = max(2, int(math.dist((x1, y1), (x2, y2)) / 5))
    for i in range(n):
        t = i / n
        x = x1 + (x2 - x1) * t + random.uniform(-amount, amount)
        y = y1 + (y2 - y1) * t + random.uniform(-amount, amount)
        if i > 0:
            d.line((px, py, x, y), fill=color, width=width)
        px, py = x, y

def wobble_circle(d, cx, cy, r, color=CHARCOAL, width=2, amount=3):
    """Draw a circle with hand-drawn irregularity."""
    pts = []
    n = 24
    for i in range(n):
        a = i * 2 * math.pi / n
        x = cx + (r + random.uniform(-amount, amount)) * math.cos(a)
        y = cy + (r + random.uniform(-amount, amount)) * math.sin(a)
        pts.append((x, y))
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        d.line((p1[0], p1[1], p2[0], p2[1]), fill=color, width=width)

# ── 9. Floating Particles — dots that drift upward ─────────────────
class ParticleSystem:
    def __init__(self, count=20):
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": random.uniform(100, 1180),
                "y": random.uniform(100, 620),
                "speed": random.uniform(0.2, 0.8),
                "drift": random.uniform(-0.3, 0.3),
                "size": random.uniform(1, 3),
                "phase": random.uniform(0, 2 * math.pi),
            })

    def update(self, t):
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += p["drift"] + 0.3 * math.sin(t + p["phase"])
            if p["y"] < -10:
                p["y"] = 630
                p["x"] = random.uniform(100, 1180)

    def draw(self, d, color=MUTED):
        for p in self.particles:
            a = 0.3 + 0.2 * math.sin(p["phase"])
            d.ellipse((p["x"]-p["size"], p["y"]-p["size"],
                       p["x"]+p["size"], p["y"]+p["size"]),
                      fill=(color[0], color[1], color[2], int(255 * a)))

# ── 10. Manuscript Unroll — scroll effect ──────────────────────────
def manuscript_unroll(d, cx, cy, width, height, progress):
    """An unrolling scroll/paper effect."""
    reveal = width * progress
    # Scroll body
    d.rectangle((cx - reveal / 2, cy - height / 2,
                 cx + reveal / 2, cy + height / 2),
                fill=(248, 246, 240), outline=CHARCOAL, width=1)
    # Roll at leading edge
    roll_r = min(8, reveal * 0.05)
    d.ellipse((cx + reveal / 2 - roll_r, cy - height / 2,
               cx + reveal / 2 + roll_r, cy + height / 2),
              fill=(240, 238, 230), outline=CHARCOAL, width=1)

# ── Demo Scene: all techniques in one showreel ─────────────────────
def demo_techniques(t, u, idx):
    im = Image.new("RGB", (1280, 720), WHITE)
    d = ImageDraw.Draw(im)

    # Section 1: Live draw mountain (0-5s)
    if t < 5:
        p = smoothstep(0, 4, t)
        draw_mountain(d, 300, 400, 1.2, p)

    # Section 2: Guru drawing (5-10s)
    if 5 <= t < 10:
        p = smoothstep(5, 9, t)
        draw_guru(d, 300, 400, 1.0, p)

    # Section 3: Temple (10-15s)
    if 10 <= t < 15:
        p = smoothstep(10, 14, t)
        draw_temple(d, 900, 400, 1.0, p)

    # Section 4: Tree (15-20s)
    if 15 <= t < 20:
        p = smoothstep(15, 19, t)
        draw_tree(d, 900, 400, 1.0, p)

    # Section 5: Morph circle→square (20-25s)
    if 20 <= t < 25:
        p = smoothstep(20, 24, t)
        pts = morph_circle_to_square(640, 360, 80, p)
        polygon = [(int(x), int(y)) for x, y in pts]
        d.polygon(polygon, outline=CHARCOAL, width=2)

    # Section 6: Ink bloom (25-30s)
    if 25 <= t < 27:
        p = smoothstep(25, 27, t)
        ink_bloom(d, 640, 360, 5 + 60 * p, CRIMSON, 0.6)
    elif 27 <= t < 30:
        # Settled bloom
        ink_bloom(d, 640, 360, 65, CRIMSON, 0.6)

    # Section 7: Floating particles (throughout)
    ps = ParticleSystem(30)
    ps.update(t * 2)
    ps.draw(d, MUTED)

    # Section 8: Hand-drawn wobble circle (30-35s)
    if 30 <= t < 35:
        p = smoothstep(30, 34, t)
        wobble_circle(d, 200, 200, 30 + p * 40, CHARCOAL, 2, 3)

    # Section 9: Manuscript unroll (35-40s)
    if 35 <= t < 40:
        p = smoothstep(35, 39, t)
        manuscript_unroll(d, 900, 400, 200, 120, p)

    # Section 10: Trail effect (40-45s)
    if 40 <= t < 45:
        trail = Trail(15)
        for i in range(15):
            x = 500 + i * 20
            y = 360 + 30 * math.sin(t + i * 0.5)
            trail.update(x, y)
        trail.draw(d, CRIMSON)

    return im
