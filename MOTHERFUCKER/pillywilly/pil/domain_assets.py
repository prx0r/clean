"""Domain-relevant assets using L-systems, Superformula, and Subdivision.
Each produces forms directly relevant to Kashmir Shaivism documentary content."""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
CHARCOAL = (40, 40, 40); CRIMSON = (141, 44, 57); GOLD = (208, 172, 91)
DARK = (12, 12, 15); INK = (235, 231, 220); MUTED = (145, 141, 132)
WHITE = (248, 246, 240)
random.seed(42)

def clamp(v, l=0, h=1): return max(l, min(h, v))

# ═════════════════════════════════════════════════════════════════════
# 1. SUPERFORMULA (Gielis curves) — exact math from Wikipedia
# ═════════════════════════════════════════════════════════════════════
# r(φ) = (|cos(mφ/4)/a|^n2 + |sin(mφ/4)/b|^n3) ^ (-1/n1)

def superformula_points(cx, cy, m, n1, n2, n3, a=1.0, b=1.0,
                         size=100, steps=60, rotation=0):
    """Generate polygon points for a Gielis superformula curve."""
    pts = []
    for i in range(steps):
        phi = i * 2 * math.pi / steps + rotation
        cos_val = math.cos(m * phi / 4)
        sin_val = math.sin(m * phi / 4)
        r = (abs(cos_val / a) ** n2 + abs(sin_val / b) ** n3) ** (-1 / n1)
        if math.isfinite(r):
            x = cx + r * size * math.cos(phi)
            y = cy + r * size * math.sin(phi)
            pts.append((x, y))
    return pts

def draw_superformula(d, cx, cy, params, progress, color=GOLD, width=2, fill=False, fill_alpha=0):
    """Draw a superformula shape with progressive reveal."""
    m, n1, n2, n3, size = params
    n = max(3, int(60 * clamp(progress)))
    pts = superformula_points(cx, cy, m, n1, n2, n3, size=size, steps=n)
    if len(pts) < 3:
        return
    if fill and fill_alpha > 0:
        d.polygon([(int(x), int(y)) for x, y in pts],
                  fill=(color[0], color[1], color[2], int(255 * fill_alpha)))
    for i in range(1, len(pts)):
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
               fill=color, width=width)
    if len(pts) > 2:
        d.line((pts[-1][0], pts[-1][1], pts[0][0], pts[0][1]),
               fill=color, width=width)

# ── Domain-relevant superformula presets ──────────────────────────
# (m, n1, n2, n3, size) — each maps to a tantric concept

SF_PRESETS = {
    "bindu":        (1, 1.0, 1.0, 1.0, 60),      # near-circle
    "mandala_5":    (5, 2.0, 1.0, 1.0, 120),    # 5-petal flower
    "mandala_8":    (8, 2.0, 1.0, 1.0, 120),    # 8-petal lotus
    "star_6":       (6, 1.0, 0.5, 0.5, 130),    # 6-pointed star
    "star_12":      (12, 1.0, 0.3, 0.3, 140),   # 12-pointed
    "square_rounded":(4, 2.0, 0.8, 0.8, 110),   # rounded square
    "flower_soft":  (7, 3.0, 2.0, 0.5, 100),    # soft flower
    "cog":          (10, 1.5, 0.2, 0.2, 130),   # gear/cog
    "shell":        (3, 1.5, 0.6, 3.0, 100),    # shell-like
    "cross":        (4, 1.0, 0.1, 0.1, 120),    # cross/star
}

# ═════════════════════════════════════════════════════════════════════
# 2. L-SYSTEM — turtle-based fractal tree
# ═════════════════════════════════════════════════════════════════════
# Grammar: axiom + rules → string → turtle interpretation
# Symbols: F=draw, +=turn left, -=turn right, [=push, ]=pop

class LSystem:
    def __init__(self, axiom, rules, angle):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle

    def generate(self, iterations):
        s = self.axiom
        for _ in range(iterations):
            s = ''.join(self.rules.get(c, c) for c in s)
        return s

    def draw(self, d, x, y, angle_offset, instruction_str, scale=1.0, color=CHARCOAL, width=2):
        stack = []
        cur_x, cur_y = x, y
        cur_angle = -math.pi / 2 + angle_offset

        for c in instruction_str:
            if c == 'F':
                new_x = cur_x + 12 * scale * math.cos(cur_angle)
                new_y = cur_y + 12 * scale * math.sin(cur_angle)
                d.line((cur_x, cur_y, new_x, new_y), fill=color, width=max(1, int(width)))
                cur_x, cur_y = new_x, new_y
            elif c == '+':
                cur_angle += self.angle
            elif c == '-':
                cur_angle -= self.angle
            elif c == '[':
                stack.append((cur_x, cur_y, cur_angle))
            elif c == ']':
                if stack:
                    cur_x, cur_y, cur_angle = stack.pop()
                    # draw a dot at branch point
                    d.ellipse((cur_x-1, cur_y-1, cur_x+1, cur_y+1), fill=color)

# ── Domain-relevant L-system presets ─────────────────────────────
LSYSTEMS = {
    "tree_basic": LSystem("F", {"F": "F[+F]F[-F]F"}, math.radians(30)),
    "tree_dense": LSystem("F", {"F": "FF[+F][-F]F"}, math.radians(25)),
    "shrub":      LSystem("F", {"F": "F[+F]F[-F][F]"}, math.radians(35)),
    "fern":       LSystem("X", {"X": "F[+X][-X]FX", "F": "FF"}, math.radians(20)),
    "spiral_tree": LSystem("F", {"F": "F[+F]F[-F][F]"}, math.radians(40)),
}

def draw_lsystem(d, lsys_key, cx, cy, iterations, progress, angle_offset=0,
                 scale=1.0, color=CHARCOAL, width=2):
    """Draw an L-system tree progressively."""
    ls = LSYSTEMS[lsys_key]
    full = ls.generate(iterations)
    n = int(len(full) * clamp(progress))
    partial = full[:n]
    ls.draw(d, cx, cy, angle_offset, partial, scale, color, width)

# ═════════════════════════════════════════════════════════════════════
# 3. RECURSIVE SUBDIVISION — Sierpinski / fractal hierarchy
# ═════════════════════════════════════════════════════════════════════

def draw_triangle(d, x, y, size, color=CHARCOAL, width=1):
    h = size * math.sqrt(3) / 2
    d.line((x, y, x+size, y), fill=color, width=width)
    d.line((x, y, x+size/2, y-h), fill=color, width=width)
    d.line((x+size, y, x+size/2, y-h), fill=color, width=width)

def draw_sierpinski(d, x, y, size, depth, progress, color=CHARCOAL, width=1):
    """Recursive Sierpinski triangle with progress control."""
    p = clamp(progress)
    if depth <= 0 or p <= 0: return
    h = size * math.sqrt(3) / 2

    draw_triangle(d, x, y, size, color, width)

    if depth > 1 and p > 0.3:
        child_p = (p - 0.3) / 0.7
        draw_sierpinski(d, x, y, size/2, depth-1, child_p, color, max(1, width-1))
        draw_sierpinski(d, x + size/2, y, size/2, depth-1, child_p, color, max(1, width-1))
        draw_sierpinski(d, x + size/4, y - h/2, size/2, depth-1, child_p, color, max(1, width-1))

def draw_carpet(d, x, y, size, depth, progress, color=CHARCOAL):
    """Sierpinski carpet (square subdivision)."""
    p = clamp(progress)
    if depth <= 0 or p <= 0: return
    # Draw outer square
    d.rectangle((x, y, x+size, y+size), outline=color, width=1)
    if depth > 1 and p > 0.3:
        child_p = (p - 0.3) / 0.7
        third = size / 3
        for row in range(3):
            for col in range(3):
                if row == 1 and col == 1:  # center hole
                    continue
                draw_carpet(d, x + col*third, y + row*third, third,
                           depth-1, child_p, color)
    if depth <= 2 and p > 0.5:
        # Fill solid at last visible level
        d.rectangle((x+1, y+1, x+size-1, y+size-1), fill=None)

# ═════════════════════════════════════════════════════════════════════
# COMPOSITE DEMO — domain-relevant forms for Kashmir Shaivism
# ═════════════════════════════════════════════════════════════════════

def demo_domain(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    # Section 1 (t=0-5s): Superformula mandalas — "wheel of powers"
    if t < 5:
        p = clamp((t) / 4.5)
        if p > 0:
            # Outer 8-petal mandala (consciousness)
            draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["mandala_8"],
                            p * 0.8, GOLD, 2, fill=True, fill_alpha=0.05)
            # Inner 5-petal (powers)
            draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["mandala_5"],
                            p, CRIMSON, 2)
            # Center bindu
            draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["bindu"],
                            p, CHARCOAL, 2)
        d.text((10, 10), "superformula: wheel of powers", fill=MUTED)

    # Section 2 (t=5-10s): L-system tree — "sages of Kashmir"
    elif t < 10:
        p = clamp((t - 5) / 4.5)
        draw_lsystem(d, "tree_dense", W//2, H-60, 5, p, 0, 1.2, CHARCOAL, 3)
        # Small tree on right
        if p > 0.5:
            draw_lsystem(d, "tree_basic", W-200, H-40, 4, (p-0.5)*2, 0.3, 0.8, MUTED, 2)
        d.text((10, 10), "l-system: sages under the tree", fill=MUTED)

    # Section 3 (t=10-15s): Sierpinski hierarchy — "tattvas descending"
    elif t < 15:
        p = clamp((t - 10) / 4.5)
        draw_sierpinski(d, 200, H-60, 880, 5, p, CHARCOAL, 2)
        d.text((10, 10), "sierpinski: tattva hierarchy", fill=MUTED)

    # Section 4 (t=15-20s): Sierpinski carpet — "36 tattvas grid"
    elif t < 20:
        p = clamp((t - 15) / 4.5)
        draw_carpet(d, 200, 60, 880, 4, p, CRIMSON)
        d.text((10, 10), "carpet: 36 tattvas", fill=MUTED)

    # Section 5 (t=20-25s): Star geometry — "twelve kalīs"
    elif t < 25:
        p = clamp((t - 20) / 4.5)
        draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["star_12"],
                        p, GOLD, 2)
        draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["star_6"],
                        p * 0.7, CRIMSON, 2)
        draw_superformula(d, W//2, H//2 - 20, SF_PRESETS["bindu"],
                        p, CHARCOAL, 2)
        d.text((10, 10), "star geometry: twelve kalis", fill=MUTED)

    # Section 6 (t=25-30s): Shell — "spiral of consciousness"
    else:
        p = clamp((t - 25) / 4.5)
        for i in range(3):
            sp = clamp((p - i * 0.2) / (1 - i * 0.2))
            if sp > 0:
                size = 80 + i * 30
                params = (3 + i, 1.5 + i * 0.3, 0.6, 3.0, size)
                draw_superformula(d, W//2, H//2 - 20, params,
                                sp, [GOLD, CRIMSON, CHARCOAL][i], 2)
        d.text((10, 10), "shell: consciousness unfolding", fill=MUTED)

    return im
