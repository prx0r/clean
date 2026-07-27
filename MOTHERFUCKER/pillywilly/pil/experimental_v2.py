"""Experimental techniques v2 — varied, stop-motion charm, smoothed."""

import math, random
from PIL import Image, ImageDraw

CHARCOAL = (40, 40, 40)
CRIMSON = (141, 44, 57)
WHITE = (248, 246, 240)
DARK = (12, 12, 15)
INK = (235, 231, 220)
GOLD = (208, 172, 91)
MUTED = (145, 141, 132)

W, H = 1280, 720

def smoothstep(a, b, x):
    t = max(0, min(1, (x-a)/(b-a))) if b != a else 1
    return t*t*(3-2*t)

def lerp(a, b, t): return a + (b - a) * t

# ── 1. Symmetrical organic form (the tree/person they liked) ──────
def draw_symmetrical_form(d, cx, cy, scale, progress, color=CHARCOAL, width=2):
    """A bilateral organic figure — trunk, branches, crown. Symmetry axis at cx."""
    p = progress
    # Trunk (centre line)
    trunk_h = 120 * scale
    if p > 0:
        t = min(1, p * 1.5)
        d.line((cx, cy, cx, cy - trunk_h * t), fill=color, width=max(1, int(width)))

    # Branches — mirrored left/right with slight asymmetry for charm
    branches = [
        (0.3, 0.4, 50, 30),   # (height_fraction, spread_fraction, len, angle_offset)
        (0.5, 0.6, 70, 45),
        (0.7, 0.5, 55, 35),
        (0.85, 0.3, 35, 25),
    ]
    for hf, sf, bl, ang in branches:
        if p < hf: continue
        bp = min(1, (p - hf) / (1 - hf + 0.01)) * 1.2
        by = cy - trunk_h * hf + 10 * scale * (1 - bp)
        for side in (-1, 1):
            end_x = cx + side * bl * scale * bp * sf + 5 * scale * (1 - bp) * random.uniform(-0.1, 0.1)
            end_y = by - bl * scale * bp * 0.4 + 10 * scale * (1 - bp)
            d.line((cx, by, end_x, end_y), fill=color, width=max(1, int(width * (1 - hf * 0.4))))

    # Crown — symmetrical ellipse with slight wobble
    if p > 0.5:
        crown_p = min(1, (p - 0.5) * 2)
        crown_w = 90 * scale * crown_p
        crown_h = 70 * scale * crown_p
        # Left half
        lpts = []
        for i in range(10):
            ang = math.pi/2 + i * math.pi / 18
            r_offset = random.uniform(-3, 3) * scale
            lx = cx - crown_w * math.cos(ang) + r_offset
            ly = cy - trunk_h - crown_h * math.sin(ang) + r_offset
            lpts.append((lx, ly))
        # Right half (mirrored)
        rpts = []
        for i in range(9, -1, -1):
            ang = math.pi/2 + i * math.pi / 18
            r_offset = random.uniform(-3, 3) * scale
            rx = cx + crown_w * math.cos(ang) + r_offset
            ry = cy - trunk_h - crown_h * math.sin(ang) + r_offset
            rpts.append((rx, ry))
        all_pts = lpts + rpts
        for i in range(1, len(all_pts)):
            d.line((all_pts[i-1][0], all_pts[i-1][1], all_pts[i][0], all_pts[i][1]),
                   fill=color, width=1)


# ── 2. Ink wash — organic spreading stain ─────────────────────────
def ink_wash(d, cx, cy, radius, progress, color=CRIMSON, alpha=0.5):
    """Slowly spreading organic stain — like ink on paper."""
    r = radius * smoothstep(0, 1, progress)
    n = 36
    pts = []
    for i in range(n):
        a = i * 2 * math.pi / n
        wobble = 1 + 0.3 * math.sin(i * 2.7 + i * 0.4) + 0.15 * math.sin(i * 5.3)
        rr = r * wobble * (0.8 + 0.2 * smoothstep(0, 1, progress))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon([(int(x), int(y)) for x, y in pts],
              fill=(color[0], color[1], color[2], int(255 * alpha * smoothstep(0.3, 1, progress))))


# ── 3. Vine / tendril — organic curling growth ────────────────────
def draw_vine(d, cx, cy, length, progress, color=CHARCOAL):
    """A curling tendril that grows organically."""
    n = 30
    pts = []
    for i in range(n):
        t = min(1, progress * n / (i + 1))
        if t <= 0: break
        u = i / n
        x = cx + length * u * math.cos(u * math.pi * 2 + u * 0.5)
        y = cy - length * u * 0.7 + 20 * math.sin(u * math.pi * 3)
        pts.append((x, y))
    for i in range(1, len(pts)):
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
               fill=color, width=2)


# ── 4. Petal unfold — flower-like opening ─────────────────────────
def petal_unfold(d, cx, cy, radius, petal_count, progress, color=CRIMSON):
    """Flower petals unfolding from center."""
    p = smoothstep(0, 1, progress)
    for i in range(petal_count):
        a = i * 2 * math.pi / petal_count + p * 0.2
        r = radius * p * (0.7 + 0.3 * math.sin(i * 1.3 + p * 2))
        # Petal outline
        tip_x = cx + r * math.cos(a)
        tip_y = cy + r * math.sin(a)
        base_left_x = cx + r * 0.2 * math.cos(a + 0.4)
        base_left_y = cy + r * 0.2 * math.sin(a + 0.4)
        base_right_x = cx + r * 0.2 * math.cos(a - 0.4)
        base_right_y = cy + r * 0.2 * math.sin(a - 0.4)
        d.line((cx, cy, base_left_x, base_left_y), fill=color, width=1)
        d.line((cx, cy, base_right_x, base_right_y), fill=color, width=1)
        d.line((base_left_x, base_left_y, tip_x, tip_y), fill=color, width=1)
        d.line((base_right_x, base_right_y, tip_x, tip_y), fill=color, width=1)
    # Center dot
    dot_r = 4 * (0.5 + 0.5 * p)
    d.ellipse((cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r), fill=color)


# ── 5. Ripple — concentric rings with staggered timing ────────────
def ripple(d, cx, cy, max_radius, count, t, color=INK, width=1):
    """Staggered concentric rings that feel like water ripples."""
    for i in range(count):
        phase = i * 0.3
        progress = (t - phase) % 2.0
        if progress < 0: continue
        r = max_radius * smoothstep(0, 1, min(1, progress))
        a = 0.4 * (1 - smoothstep(0, 1, min(1, progress)))
        if r > 2:
            d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(color[0], color[1], color[2], int(255*a)), width=width)


# ── 6. Geometric mandala — radial symmetry from points ────────────
def draw_mandala(d, cx, cy, radius, points, progress, color=GOLD, width=1):
    """Radial geometric pattern — symmetric lines radiating."""
    p = smoothstep(0, 1, progress)
    n = points
    inner_r = radius * 0.3 * p
    outer_r = radius * p
    for i in range(n):
        a = i * 2 * math.pi / n
        x1 = cx + inner_r * math.cos(a)
        y1 = cy + inner_r * math.sin(a)
        x2 = cx + outer_r * math.cos(a)
        y2 = cy + outer_r * math.sin(a)
        d.line((x1, y1, x2, y2), fill=color, width=width)
        # Connect every other point
        if i % 2 == 0:
            j = (i + n // 2) % n
            x3 = cx + outer_r * math.cos(j * 2 * math.pi / n)
            y3 = cy + outer_r * math.sin(j * 2 * math.pi / n)
            d.line((x2, y2, x3, y3), fill=(color[0], color[1], color[2], int(100 * p)), width=max(1, width-1))


# ── 7. Smoke trail — drifting upward with fade ────────────────────
class Smoke:
    def __init__(self, count=8):
        self.puffs = [{ "x": random.uniform(100, 1180),
                        "y": random.uniform(500, 650),
                        "vx": random.uniform(-0.2, 0.2),
                        "vy": random.uniform(-0.5, -0.2),
                        "r": random.uniform(4, 12),
                        "phase": random.uniform(0, 2*math.pi) } for _ in range(count)]
    def update(self, t):
        for p in self.puffs:
            p["x"] += p["vx"] + 0.1 * math.sin(t * 0.5 + p["phase"])
            p["y"] += p["vy"]
            p["r"] += 0.05
            if p["y"] < -20:
                p["y"] = 650
                p["x"] = random.uniform(100, 1180)
                p["r"] = random.uniform(4, 12)
    def draw(self, d, color=MUTED):
        for p in self.puffs:
            a = max(0, 0.5 * (1 - (650 - p["y"]) / 650))
            r = p["r"]
            d.ellipse((p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r),
                      fill=(color[0], color[1], color[2], int(255 * a)))


# ── 8. Dashed path — dotted line that draws itself ────────────────
def dashed_live_draw(d, points, progress, color=CHARCOAL, width=2, dash=8, gap=5):
    """A path that draws itself with dashed strokes — like animating stroke-dashoffset."""
    total_len = 0
    seg_lens = []
    for i in range(1, len(points)):
        dx = points[i][0] - points[i-1][0]
        dy = points[i][1] - points[i-1][1]
        seg_len = math.sqrt(dx*dx + dy*dy)
        seg_lens.append(seg_len)
        total_len += seg_len
    target = total_len * progress
    drawn = 0
    for i in range(1, len(points)):
        if drawn >= target: break
        seg_len = seg_lens[i-1]
        if drawn + seg_len <= target:
            # Draw full segment as dashed
            seg_progress = 1.0
            _draw_dashed(d, points[i-1], points[i], seg_progress, color, width, dash, gap)
            drawn += seg_len
        else:
            remaining = target - drawn
            seg_progress = remaining / seg_len if seg_len > 0 else 0
            _draw_dashed(d, points[i-1], points[i], seg_progress, color, width, dash, gap)
            drawn = target

def _draw_dashed(d, p1, p2, progress, color, width, dash, gap):
    """Draw a portion of a line with dashes."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    total_len = math.sqrt(dx*dx + dy*dy)
    if total_len == 0: return
    draw_len = total_len * progress
    is_dash = True
    pos = 0
    while pos < draw_len:
        seg = dash if is_dash else gap
        end = min(pos + seg, draw_len)
        if is_dash:
            u1 = pos / total_len
            u2 = end / total_len
            x1 = p1[0] + dx * u1; y1 = p1[1] + dy * u1
            x2 = p1[0] + dx * u2; y2 = p1[1] + dy * u2
            d.line((x1, y1, x2, y2), fill=color, width=width)
        pos += seg
        is_dash = not is_dash


# ── 9. Spiral — expanding or contracting ──────────────────────────
def draw_spiral(d, cx, cy, max_radius, turns, progress, color=GOLD, width=1):
    """Archimedean spiral that draws progressively."""
    p = smoothstep(0, 1, progress)
    n = int(60 * p)
    for i in range(1, n):
        u = i / 60
        a = u * turns * 2 * math.pi
        r = max_radius * u
        x1 = cx + r * math.cos(a)
        y1 = cy + r * math.sin(a)
        u_prev = (i-1) / 60
        a_prev = u_prev * turns * 2 * math.pi
        r_prev = max_radius * u_prev
        x0 = cx + r_prev * math.cos(a_prev)
        y0 = cy + r_prev * math.sin(a_prev)
        d.line((x0, y0, x1, y1), fill=color, width=width)


# ── 10. Fragment gather — pieces coming together ──────────────────
def fragment_gather(d, cx, cy, fragment_count, spread, progress, color=CHARCOAL, size=4):
    """Scattered fragments that converge to a point."""
    p = smoothstep(0, 1, progress)
    random.seed(42)
    for i in range(fragment_count):
        start_angle = random.uniform(0, 2 * math.pi)
        start_r = random.uniform(spread * 0.3, spread)
        cur_angle = start_angle
        cur_r = start_r * (1 - p)
        x = cx + cur_r * math.cos(cur_angle)
        y = cy + cur_r * math.sin(cur_angle)
        a = 0.3 + 0.7 * (1 - p)
        d.ellipse((x-size/2, y-size/2, x+size/2, y+size/2),
                  fill=(color[0], color[1], color[2], int(255 * a)))


# ── COMPOSITE DEMO: ALL 10 TECHNIQUES IN ONE SCENE ──────────────
def demo_v2(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    # Section 1 (t=0-4): Symmetrical organic form — the tree/person
    if t < 4:
        p = smoothstep(0, 3.5, t)
        draw_symmetrical_form(d, W//2, H//2 + 40, 1.5, p, CHARCOAL, 3)
        d.text((20, 10), "symmetrical form", fill=MUTED)

    # Section 2 (t=4-8): Ink wash
    elif t < 8:
        p = smoothstep(4, 7.5, t)
        ink_wash(d, W//3, H//2, 150, p, CRIMSON, 0.4)
        ink_wash(d, 2*W//3, H//2 + 30, 100, (t - 5) / 2, GOLD, 0.3)
        d.text((20, 10), "ink wash — organic spread", fill=MUTED)

    # Section 3 (t=8-12): Vine / tendril
    elif t < 12:
        p = smoothstep(8, 11.5, t)
        draw_vine(d, W//3, H - 100, 200, p, CHARCOAL)
        draw_vine(d, 2*W//3, H - 100, 160, (t - 9) / 2.5, CRIMSON)
        d.text((20, 10), "organic tendril", fill=MUTED)

    # Section 4 (t=12-16): Petal unfold
    elif t < 16:
        p = smoothstep(12, 15.5, t)
        petal_unfold(d, W//2 - 150, H//2, 120, 8, p, CRIMSON)
        petal_unfold(d, W//2 + 150, H//2 + 20, 90, 6, (t - 13) / 2.5, GOLD)
        d.text((20, 10), "petal unfold", fill=MUTED)

    # Section 5 (t=16-20): Ripple
    elif t < 20:
        ripple(d, W//2, H//2, 180, 4, (t - 16) * 0.8, CHARCOAL, 2)
        ripple(d, W//2 + 200, H//2 - 50, 120, 3, (t - 16) * 0.9, CRIMSON, 1)
        d.text((20, 10), "water ripple", fill=MUTED)

    # Section 6 (t=20-24): Mandala
    elif t < 24:
        p = smoothstep(20, 23.5, t)
        draw_mandala(d, W//2, H//2, 200, 12, p, GOLD, 2)
        d.text((20, 10), "radial mandala", fill=MUTED)

    # Section 7 (t=24-28): Smoke trail
    elif t < 28:
        smoke = Smoke(10)
        smoke.update((t - 24) * 3)
        smoke.draw(d, MUTED)
        d.text((20, 10), "smoke / drifting", fill=MUTED)

    # Section 8 (t=28-32): Dashed live draw — mountain
    elif t < 32:
        p = smoothstep(28, 31.5, t)
        pts = [(200, 500), (300, 350), (400, 420), (500, 280),
               (600, 380), (700, 320), (800, 400), (900, 350), (1000, 500)]
        dashed_live_draw(d, pts, p, CHARCOAL, 3, 12, 6)
        d.text((20, 10), "dashed live draw", fill=MUTED)

    # Section 9 (t=32-36): Spiral
    elif t < 36:
        p = smoothstep(32, 35.5, t)
        draw_spiral(d, W//2, H//2, 180, 3, p, GOLD, 2)
        d.text((20, 10), "spiral", fill=MUTED)

    # Section 10 (t=36-45): Fragment gather
    else:
        p = smoothstep(36, 43, t)
        fragment_gather(d, W//2, H//2, 40, 300, p, CRIMSON, 6)
        if p > 0.8:
            r = 6 * (p - 0.8) / 0.2
            d.ellipse((W//2-r, H//2-r, W//2+r, H//2+r), fill=CRIMSON)
        d.text((20, 10), "fragments gather", fill=MUTED)

    return im
