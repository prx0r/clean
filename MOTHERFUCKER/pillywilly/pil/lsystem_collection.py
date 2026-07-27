"""L-system Collection — 20 grammars for organic documentary forms.
Each is a tuple: (name, axiom, rules, angle, iterations, description, use)"""

import math, random
from PIL import Image, ImageDraw

W, H = 1280, 720
CHARCOAL = (40,40,40); CRIMSON = (141,44,57); GOLD = (208,172,91)
MUTED = (145,141,132); WHITE = (248,246,240); DARK = (12,12,15)
random.seed(42)

# ── L-system definition ──────────────────────────────────────────
# Symbols: F=draw forward, +=turn left, -=turn right, [=push, ]=pop
# X, A, B = control characters (no draw)

def render_lsystem(axiom, rules, angle, iterations):
    """Generate the full L-system string."""
    s = axiom
    for _ in range(iterations):
        s = ''.join(rules.get(c, c) for c in s)
    return s

def draw_lsystem(d, instruction_str, start_x, start_y, start_angle, branch_angle,
                 step=10, color=CHARCOAL, width=2):
    """Turtle-draw an L-system string with progress."""
    stack = []
    cur_x, cur_y = start_x, start_y
    cur_angle = start_angle
    pts = [(cur_x, cur_y)]

    for c in instruction_str:
        if c == 'F':
            nx = cur_x + step * math.cos(cur_angle)
            ny = cur_y + step * math.sin(cur_angle)
            d.line((cur_x, cur_y, nx, ny), fill=color, width=max(1, int(width)))
            cur_x, cur_y = nx, ny
            pts.append((cur_x, cur_y))
        elif c == '+':
            cur_angle += branch_angle
        elif c == '-':
            cur_angle -= branch_angle
        elif c == '[':
            stack.append((cur_x, cur_y, cur_angle, width))
            width *= 0.7
        elif c == ']' and stack:
            cur_x, cur_y, cur_angle, width = stack.pop()
    return pts

def draw_lsystem_progressive(d, instruction_str, start_x, start_y, start_angle, branch_angle,
                              progress, step=10, color=CHARCOAL, width=2):
    """Draw only up to progress fraction of the instruction string."""
    n = max(1, int(len(instruction_str) * min(1, progress)))
    partial = instruction_str[:n]
    return draw_lsystem(d, partial, start_x, start_y, start_angle, branch_angle, step, color, width)

# ═══════════════════════════════════════════════════════════════════
# GRAMMAR COLLECTION — 20 L-systems
# ═══════════════════════════════════════════════════════════════════

LSYSTEMS = [
    # (name, axiom, rules, angle_deg, iters, description, content_use)

    # ── Trees & Branching ───────────────────────────────────────
    ("binary_tree", "F",
     {"F": "F[+F]F[-F]F"}, 30, 6,
     "Classic binary branching tree",
     "emanation, duality, one becoming two"),

    ("dense_tree", "F",
     {"F": "FF[+F][-F]F"}, 25, 5,
     "Dense bushy tree with tight branching",
     "abundance, Śakti unfolding, fullness"),

    ("corkscrew_tree", "F",
     {"F": "F[+F]F[-F][+F]F"}, 35, 5,
     "Spiral-twist branching pattern",
     "kundalini, spiral energy, life force"),

    ("weeping_tree", "F",
     {"F": "F[+F][-F]F"}, 40, 6,
     "Cascading / weeping willow style",
     "grace descending, receptivity"),

    ("star_tree", "F",
     {"F": "F[+F]F[-F]F[+F]F"}, 22, 5,
     "Multi-branch star-like crown",
     "radiance, many from one"),

    # ── Fractal Plants & Herbs ──────────────────────────────────
    ("fractal_plant", "X",
     {"X": "F[+X][-X]FX", "F": "FF"}, 25, 6,
     "Classic fractal plant (Prusinkiewicz)",
     "growth, organic unfolding, life"),

    ("fern_spiral", "X",
     {"X": "F[+X]F[-X]+X", "F": "FF"}, 20, 6,
     "Fern-like spiral frond",
     "patience, gradual revelation"),

    ("thistle", "X",
     {"X": "F[+X][-X]F", "F": "FF"}, 30, 5,
     "Prickly upright growth",
     "protection, contraction, boundary"),

    ("grass_tuft", "F",
     {"F": "[+F][-F]"}, 45, 4,
     "Clustered grass-like tufts",
     "multiplicity, ground, foundation"),

    # ── Space-Filling & Geometric ───────────────────────────────
    ("dragon_curve", "FX",
     {"X": "X+YF+", "Y": "-FX-Y"}, 90, 8,
     "Harter-Heighway dragon curve",
     "folding, complexity from simple rules"),

    ("koch_square", "F",
     {"F": "F+F-F-F+F"}, 90, 4,
     "Koch square / quadric fractal",
     "structure, crystalline order"),

    ("sierpinski_arrow", "A",
     {"A": "B-A-B", "B": "A+B+A"}, 60, 6,
     "Sierpinski arrowhead curve",
     "hierarchy, self-similarity"),

    ("hilbert_curve", "X",
     {"X": "+YF-XFX-FY+", "Y": "-XF+YFY+FX-"}, 90, 4,
     "Hilbert space-filling curve",
     "continuity, field, totality"),

    ("cantor_set", "A",
     {"A": "ABA", "B": "BBB"}, 0, 5,
     "Cantor set — draw/space pattern",
     "void, interval, the gap"),

    # ── Organic / Natural ───────────────────────────────────────
    ("algae", "A",
     {"A": "AB", "B": "A"}, 0, 7,
     "Lindenmayer's original algae",
     "Fibonacci, growth, cellular"),

    ("weed", "F",
     {"F": "F[+F][-F]F"}, 25, 5,
     "Simple weed / ground cover",
     "persistence, spread"),

    ("vine_tendril", "F",
     {"F": "F[+F]F[-F]F"}, 60, 5,
     "Wide-angle vine / tendril",
     "reaching, seeking, connection"),

    # ── Abstract / Conceptual ───────────────────────────────────
    ("peano", "X",
     {"X": "XFYFX+F+YFXFY-F-XFYFX", "Y": "YFXFY-F-XFYFX+F+YFXFY"}, 90, 3,
     "Peano curve variant",
     "totality, infinite in finite"),

    ("kolam", "F",
     {"F": "F+F-F-F+F+F+F-F"}, 90, 3,
     "Kolam / rangoli-style pattern",
     "sacred geometry, threshold"),

    ("symmetric_bush", "F",
     {"F": "F[+F][-F]F[+F][-F]F"}, 20, 4,
     "Highly symmetric radial bush",
     "balance, harmony, mandala"),
]

def render_grammar_demo(t, grammar_idx, progress):
    """Render a single grammar at given progress."""
    name, axiom, rules, angle_deg, iters, desc, use = LSYSTEMS[grammar_idx]
    angle = math.radians(angle_deg)
    full = render_lsystem(axiom, rules, angle, iters)
    n = int(len(full) * min(1, progress))
    partial = full[:n]

    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    cx, cy = W//2, H - 80
    draw_lsystem(d, partial, cx, cy, -math.pi/2, angle, 8, CHARCOAL, 2)

    # Label
    d.text((20, 10), f"{grammar_idx+1}. {name}", fill=CHARCOAL)
    d.text((20, 30), f"  rule: {axiom} → {rules.get(list(rules.keys())[0],'')}", fill=MUTED)
    d.text((20, 50), f"  angle: {angle_deg}°  iterations: {iters}", fill=MUTED)
    d.text((20, 70), f"  use: {use}", fill=CRIMSON)
    return im

def demo_all(t, u, idx):
    """Demo all 20 grammars, 3s each = 60s total."""
    grammar_idx = min(19, int(t / 3))
    local_t = t - grammar_idx * 3
    progress = min(1, local_t / 2.8)
    return render_grammar_demo(t, grammar_idx, progress)
