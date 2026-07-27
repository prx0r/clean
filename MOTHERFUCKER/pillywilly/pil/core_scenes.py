"""6 Core Scenes — implementation specs with exact math.
Each scene is a standalone function: scene_name(t, u, idx) → Image."""

import math, random
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
CHARCOAL = (40,40,40); CRIMSON = (141,44,57); GOLD = (208,172,91)
INK = (235,231,220); MUTED = (145,141,132); WHITE = (248,246,240); DARK = (12,12,15)
random.seed(42)

def clamp(v, l=0, h=1): return max(l, min(h, v))
def smoothstep(a,b,x):
    t = clamp((x-a)/(b-a)) if b!=a else 1
    return t*t*(3-2*t)

def lerp(a,b,t): return a+(b-a)*t

# ═══════════════════════════════════════════════════════════════════
# 1. BRANCHING INTELLIGENCE — L-system neural branching
# ═══════════════════════════════════════════════════════════════════
# Concept: Śakti unfolding, consciousness articulating itself
# Math: L-system with turtle graphics
# Reveal: stroke traversal (pen moves, line accumulates)

def scene_branching(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H - 80
    p = clamp(t / 10)  # 10s duration

    # Grammar: branching neural form
    # F=draw, +=turn left, -=turn right, [=push, ]=pop
    angle = math.radians(28)
    axiom = "F"
    rules = {"F": "F[+F]F[-F][+F]F"}

    # Generate full string
    s = axiom
    for _ in range(5):
        s = ''.join(rules.get(c, c) for c in s)

    # Turtle draw with progress
    n = int(len(s) * clamp(p * 1.1))
    partial = s[:n]
    stack = []
    cur_x, cur_y = cx, cy
    cur_angle = -math.pi / 2
    scale = 1.3

    for c in partial:
        if c == 'F':
            nx = cur_x + 10 * scale * math.cos(cur_angle)
            ny = cur_y + 10 * scale * math.sin(cur_angle)
            d.line((cur_x, cur_y, nx, ny), fill=CHARCOAL, width=2)
            cur_x, cur_y = nx, ny
        elif c == '+': cur_angle += angle
        elif c == '-': cur_angle -= angle
        elif c == '[': stack.append((cur_x, cur_y, cur_angle))
        elif c == ']' and stack:
            cur_x, cur_y, cur_angle = stack.pop()

    # Seed bindu at origin
    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=CRIMSON)

    # Labels
    if p > 0.3:
        a = smoothstep(0.3, 0.5, p)
        d.text((cx-40, 30), "बिन्दु", font=ImageFont.load_default(), fill=CHARCOAL)
    return im

# ═══════════════════════════════════════════════════════════════════
# 2. HARMONOGRAPH OF RECOGNITION — coupled oscillators
# ═══════════════════════════════════════════════════════════════════
# Concept: subtle cognition, mantra, recognition stabilizing
# Math: damped harmonic oscillator + Lissajous
# Reveal: stroke trace (pen draws accumulating curve)

def scene_harmonograph(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    p = clamp(t / 12)  # 12s

    # Damped harmonic oscillator parameters
    # x(t) = A1 * e^(-d1*t) * sin(f1*t + p1) + A2 * e^(-d2*t) * sin(f2*t + p2)
    # y(t) = A3 * e^(-d3*t) * sin(f3*t + p3) + A4 * e^(-d4*t) * sin(f4*t + p4)
    f1, f2 = 2.0, 3.0
    f3, f4 = 3.0, 2.0
    d1, d2 = 0.02, 0.03
    d3, d4 = 0.025, 0.01
    A = 180  # amplitude

    n = int(500 * p)
    pts = []
    for i in range(n):
        ti = i * 0.03
        x = A * (math.exp(-d1*ti)*math.sin(f1*ti) + math.exp(-d2*ti)*math.sin(f2*ti))
        y = A * (math.exp(-d3*ti)*math.sin(f3*ti) + math.exp(-d4*ti)*math.sin(f4*ti))
        pts.append((cx + x, cy + y))

    for i in range(1, len(pts)):
        d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
               fill=CHARCOAL, width=1)

    pts2 = []
    # Ghost trace (second harmonograph, slightly offset)
    if p > 0.4:
        gp = clamp((p - 0.4) / 0.6)
        n2 = int(500 * gp)
        pts2 = []
        for i in range(n2):
            ti = i * 0.03
            x = A * 0.8 * (math.exp(-0.015*ti)*math.sin(2.3*ti + 0.5) +
                           math.exp(-0.025*ti)*math.sin(2.7*ti))
            y = A * 0.8 * (math.exp(-0.02*ti)*math.sin(3.3*ti) +
                           math.exp(-0.015*ti)*math.sin(1.7*ti + 1.2))
            pts2.append((cx + x, cy + y))
        for i in range(1, len(pts2)):
            d.line((pts2[i-1][0], pts2[i-1][1], pts2[i][0], pts2[i][1]),
                   fill=MUTED, width=1)

    # Crimson emphasis at intersections (check for near points)
    if len(pts2) > 1:
        for i in range(0, len(pts)-1, 10):
            for j in range(0, min(len(pts2)-1, len(pts2)-1), 10):
                if j < len(pts2):
                    dx = pts[i][0] - pts2[j][0]
                    dy = pts[i][1] - pts2[j][1]
                    if dx*dx + dy*dy < 100:
                        d.ellipse((pts[i][0]-2, pts[i][1]-2, pts[i][0]+2, pts[i][1]+2),
                                  fill=CRIMSON)
    return im

# ═══════════════════════════════════════════════════════════════════
# 3. TATTVA DESCENT LATTICE — hierarchical node tree
# ═══════════════════════════════════════════════════════════════════
# Concept: 36 tattvas descending, ontological hierarchy
# Math: layered DAG with force-directed settling
# Reveal: top-down layer-by-layer

def scene_tattva_lattice(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    p = clamp(t / 14)

    # Levels: source → pure → maya → purusa/prakrti → inner → senses → elements
    levels = [
        ("Śiva", 1),
        ("Śakti", 1),
        ("Sadāśiva", 1),
        ("Īśvara", 1),
        ("Śuddhavidyā", 1),
        ("Māyā", 1),
        ("Kalā / Vidyā / Rāga / Kāla / Niyati", 5),
        ("Puruṣa / Prakṛti", 2),
        ("Buddhi / Ahaṅkāra / Manas", 3),
        ("5 senses + 5 actions", 10),
        ("5 subtle + 5 gross", 10),
    ]

    y_start = 80
    y_spacing = 55
    cx = W // 2

    for li, (name, count) in enumerate(levels):
        layer_progress = clamp((p * len(levels) - li) / 1.2)
        if layer_progress <= 0:
            continue

        y = y_start + li * y_spacing
        x_spacing = min(80, 600 // max(count, 1))
        x_start = cx - (count - 1) * x_spacing / 2

        # Draw nodes
        for j in range(count):
            node_progress = clamp((layer_progress * count - j) / 1.5)
            if node_progress <= 0:
                continue
            x = x_start + j * x_spacing
            r = 4 + node_progress * 3
            d.ellipse((x-r, y-r, x+r, y+r), fill=CHARCOAL)
            # Connect to parent
            if li > 0 and j == 0:
                d.line((cx, y - y_spacing + 10, x, y - 10), fill=MUTED, width=1)

        # Label
        if layer_progress > 0.5:
            a = clamp((layer_progress - 0.5) * 2)
            d.text((cx, y + 12), name, font=ImageFont.load_default(),
                   fill=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255*a)))
    return im

# ═══════════════════════════════════════════════════════════════════
# 4. CONSTRAINT RINGS / KAÑCUKA CLAMP — concentric contraction
# ═══════════════════════════════════════════════════════════════════
# Concept: Māyā, limitation, five kañcukas
# Math: radial geometry + parametric contraction
# Reveal: each ring draws, then constrains

def scene_constraint_rings(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    p = clamp(t / 12)

    kañcukas = ["Kalā", "Vidyā", "Rāga", "Kāla", "Niyati"]
    rings = len(kañcukas)

    # Open luminous field (background glow)
    d.ellipse((cx-250, cy-250, cx+250, cy+250), fill=(252, 250, 245))

    for i in range(rings):
        ring_progress = clamp((p * rings - i) / 1.2)
        if ring_progress <= 0:
            continue

        r = 200 - i * 35  # each ring smaller
        r_drawn = r * ring_progress

        # Ring style varies per kañcuka
        colors = [CHARCOAL, CRIMSON, CHARCOAL, CRIMSON, CHARCOAL]
        widths = [2, 3, 2, 3, 2]
        c = colors[i]
        w = widths[i]

        # Draw ring
        if r_drawn > 2:
            d.ellipse((cx-r_drawn, cy-r_drawn, cx+r_drawn, cy+r_drawn),
                      outline=c, width=w)

        # Label appears after ring completes
        if ring_progress > 0.8 and i < len(kañcukas):
            a = clamp((ring_progress - 0.8) * 5)
            label_x = cx + r + 30
            label_y = cy - 5
            d.text((label_x, label_y), kañcukas[i],
                   font=ImageFont.load_default(), fill=c)

    # Center dot
    d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=CRIMSON)
    return im

# ═══════════════════════════════════════════════════════════════════
# 5. RESONANCE BRIDGE — coupled oscillators synchronizing
# ═══════════════════════════════════════════════════════════════════
# Concept: mantra, transmission, grace, attunement
# Math: coupled oscillator field, phase synchronization
# Reveal: source → bridge → receiver wakes up

def scene_resonance(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    p = clamp(t / 12)

    lx, rx = cx - 250, cx + 250
    source_amp = 1 + 0.08 * math.sin(t * 3)
    receiver_amp = 1 + 0.08 * math.sin((t - 4) * 3) * clamp((t - 3) / 2)

    # Source field (left)
    for i in range(5):
        r = 20 + i * 18 * source_amp
        a = 0.3 - i * 0.05
        d.ellipse((lx-r, cy-r, lx+r, cy+r), outline=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255*a)), width=1)

    # Receiver field (right) — starts still
    if t > 3:
        for i in range(5):
            r = 20 + i * 18 * receiver_amp
            a = (0.3 - i * 0.05) * clamp((t - 3) / 3)
            d.ellipse((rx-r, cy-r, rx+r, cy+r), outline=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255*a)), width=1)

    # Resonance bridge
    if t > 2:
        bridge_p = clamp((t - 2) / 4)
        if bridge_p > 0:
            for i in range(8):
                bx = lerp(lx, rx, i / 7)
                wave = 15 * math.sin(t * 4 + i * 0.8) * bridge_p
                d.ellipse((bx-2, cy+wave-2, bx+2, cy+wave+2),
                          fill=(CRIMSON[0], CRIMSON[1], CRIMSON[2], int(100 * bridge_p)))

    # Labels
    d.text((lx-30, cy+60), "mantra", font=ImageFont.load_default(), fill=MUTED)
    d.text((rx-30, cy+60), "spanda", font=ImageFont.load_default(), fill=MUTED)
    if t > 5:
        d.text((cx-30, cy-100), "resonance", font=ImageFont.load_default(), fill=CHARCOAL)
    return im

# ═══════════════════════════════════════════════════════════════════
# 6. APOPHATIC DISSOLUTION FIELD — reverse-draw to void
# ═══════════════════════════════════════════════════════════════════
# Concept: dissolution, reabsorption, void
# Math: contour erosion, recursive simplification
# Reveal: undrawing / reverse construction

def scene_dissolution(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    p = clamp(t / 12)
    # p = 0 is full form, p = 1 is fully dissolved

    dissolve = p  # 0 = whole, 1 = gone

    # Complex geometry that erodes
    # Outer rings dissolve first
    for i in range(8):
        ring_alpha = clamp(1 - dissolve * (1 + i * 0.2))
        if ring_alpha <= 0:
            continue
        r = 30 + i * 28
        d.ellipse((cx-r, cy-r, cx+r, cy+r),
                  outline=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255 * ring_alpha * 0.3)),
                  width=1)

    # Inner radial lines dissolve outward-to-inward
    for i in range(16):
        line_alpha = clamp(1 - dissolve * (1 + i * 0.1))
        if line_alpha <= 0:
            continue
        ang = i * 2 * math.pi / 16
        r = 220 * (1 - dissolve * 0.5)
        d.line((cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang)),
               fill=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255 * line_alpha * 0.2)),
               width=1)

    # Center point persists longest
    center_r = 6 * (1 - dissolve * 0.9)
    if center_r > 0.5:
        d.ellipse((cx-center_r, cy-center_r, cx+center_r, cy+center_r), fill=CRIMSON)

    # Text at threshold
    if 0.4 < dissolve < 0.8:
        a = clamp((dissolve - 0.4) / 0.2) * (1 - clamp((dissolve - 0.6) / 0.2))
        d.text((cx-60, cy-120), "neither this nor not-this",
               font=ImageFont.load_default(), fill=(CHARCOAL[0], CHARCOAL[1], CHARCOAL[2], int(255*a)))
    return im

# ═══════════════════════════════════════════════════════════════════
# SCENE REGISTRY — for agent scene selection
# ═══════════════════════════════════════════════════════════════════

SCENE_REGISTRY = [
    {
        "id": "branching_intelligence",
        "concepts": ["emanation", "shakti", "manifestation", "differentiation", "logos"],
        "generator": "lsystem",
        "reveal": "turtle_growth",
        "default_duration": 10,
        "fn": scene_branching,
    },
    {
        "id": "harmonograph_recognition",
        "concepts": ["recognition", "mantra", "reflexivity", "cognition", "tuning"],
        "generator": "harmonograph",
        "reveal": "stroke_trace",
        "default_duration": 12,
        "fn": scene_harmonograph,
    },
    {
        "id": "tattva_descent_lattice",
        "concepts": ["hierarchy", "tattvas", "emanation", "ontological_descent", "procession"],
        "generator": "layered_dag",
        "reveal": "layer_by_layer",
        "default_duration": 14,
        "fn": scene_tattva_lattice,
    },
    {
        "id": "constraint_rings",
        "concepts": ["limitation", "contraction", "maya", "kancukas", "finitude"],
        "generator": "radial_geometry",
        "reveal": "concentric",
        "default_duration": 12,
        "fn": scene_constraint_rings,
    },
    {
        "id": "resonance_bridge",
        "concepts": ["mantra", "transmission", "shaktipata", "attunement", "grace"],
        "generator": "coupled_oscillators",
        "reveal": "phase_sync",
        "default_duration": 12,
        "fn": scene_resonance,
    },
    {
        "id": "apophatic_dissolution",
        "concepts": ["void", "dissolution", "return", "reabsorption", "transcendence"],
        "generator": "contour_erosion",
        "reveal": "undraw",
        "default_duration": 12,
        "fn": scene_dissolution,
    },
]
