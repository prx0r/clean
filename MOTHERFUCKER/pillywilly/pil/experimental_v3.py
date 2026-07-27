"""Techniques v3 — inspired by generative art research. 10 new effects."""

import math, random
from PIL import Image, ImageDraw

CHARCOAL = (40, 40, 40); CRIMSON = (141, 44, 57); WHITE = (248, 246, 240)
DARK = (12, 12, 15); INK = (235, 231, 220); GOLD = (208, 172, 91); MUTED = (145, 141, 132)
W, H = 1280, 720
random.seed(42)

def smoothstep(a,b,x):
    t = max(0,min(1,(x-a)/(b-a))) if b!=a else 1
    return t*t*(3-2*t)

# ── 1. Flow field — particles drift through a noise field ─────────
class FlowField:
    """Particles moving through a simulated vector field."""
    def __init__(self, count=200):
        self.particles = [{"x": random.uniform(0, W), "y": random.uniform(0, H),
                           "vx": 0, "vy": 0, "life": random.uniform(0, 1)} for _ in range(count)]

    def update(self, t, intensity=1.0):
        for p in self.particles:
            # Simplex-like noise approximation using sine layers
            angle = (math.sin(p["x"] * 0.003 + t * 0.2) * 0.5 +
                     math.cos(p["y"] * 0.004 + t * 0.15) * 0.5 +
                     math.sin((p["x"] + p["y"]) * 0.002 + t * 0.1) * 0.5) * math.pi * 2
            p["vx"] += math.cos(angle) * 0.1 * intensity
            p["vy"] += math.sin(angle) * 0.1 * intensity
            p["vx"] *= 0.95
            p["vy"] *= 0.95
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.003
            if p["life"] <= 0 or p["x"] < -20 or p["x"] > W+20 or p["y"] < -20 or p["y"] > H+20:
                p["x"] = random.uniform(0, W)
                p["y"] = random.uniform(0, H)
                p["vx"] = 0; p["vy"] = 0
                p["life"] = 1

    def draw(self, d, color=MUTED):
        for p in self.particles:
            if p["life"] > 0:
                d.ellipse((p["x"]-1.5, p["y"]-1.5, p["x"]+1.5, p["y"]+1.5),
                          fill=(color[0], color[1], color[2], int(255 * p["life"] * 0.6)))


# ── 2. Reaction-diffusion — organic pattern formation ──────────────
def reaction_diffusion(d, cx, cy, radius, iterations, progress, color=CRIMSON):
    """Simulated reaction-diffusion blob formation."""
    n = max(3, int(30 * smoothstep(0, 1, progress)))
    pts = []
    for i in range(n):
        a = i * 2 * math.pi / n + progress * 0.5
        r = radius * (0.5 + 0.5 * math.sin(i * 3.7 + progress * 4) * 0.3 +
                      0.5 * math.sin(i * 5.1 + progress * 3) * 0.15)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon([(int(x), int(y)) for x, y in pts],
              outline=color, width=2)
    # Inner spots
    for i in range(int(10 * progress)):
        x = cx + random.uniform(-radius*0.4, radius*0.4)
        y = cy + random.uniform(-radius*0.4, radius*0.4)
        d.ellipse((x-2, y-2, x+2, y+2), fill=color)


# ── 3. L-system tree — fractal branching ───────────────────────────
def lsystem_tree(d, cx, cy, length, angle, depth, progress, color=CHARCOAL):
    """Recursive branching tree (L-system style)."""
    if depth <= 0 or progress <= 0: return
    branches = int(3 * smoothstep(0, 1, min(1, progress * 2)))
    if branches < 1: return

    end_x = cx + length * math.cos(angle)
    end_y = cy + length * math.sin(angle)
    d.line((cx, cy, end_x, end_y), fill=color, width=max(1, depth))

    child_progress = max(0, (progress - 0.3) / 0.7) if depth <= 2 else progress
    if depth > 1 and child_progress > 0:
        spread = 0.5 + depth * 0.1
        for i in range(branches):
            child_angle = angle + (i - (branches-1)/2) * spread
            child_len = length * (0.6 + random.uniform(-0.05, 0.05))
            lsystem_tree(d, end_x, end_y, child_len, child_angle, depth-1, child_progress, color)


# ── 4. Cellular / Voronoi-like dots ────────────────────────────────
def cellular_dots(d, count, radius, progress, color=CRIMSON):
    """Dots that appear to form cellular boundaries."""
    n = int(count * smoothstep(0, 1, progress))
    points = [(random.uniform(50, W-50), random.uniform(50, H-50)) for _ in range(n)]
    for (x, y) in points:
        r = radius * (0.5 + 0.5 * random.random())
        d.ellipse((x-r, y-r, x+r, y+r), outline=color, width=1)


# ── 5. Bézier wave — smooth curved line ───────────────────────────
def bezier_wave(d, cx, cy, width, amplitude, frequency, t, color=CHARCOAL, width_l=2):
    """Smooth wavy line using cubic bezier approximation."""
    n = 8
    pts = []
    for i in range(n + 1):
        u = i / n
        x = cx - width/2 + width * u
        y = cy + amplitude * math.sin(u * frequency * math.pi * 2 + t * 0.5)
        pts.append((x, y))
    # Draw as connected bezier segments
    for i in range(len(pts) - 1):
        p0 = pts[i]
        p3 = pts[i+1]
        # Control points for smooth curve
        c1x = p0[0] + (p3[0] - p0[0]) / 3
        c1y = p0[1]
        c2x = p0[0] + 2 * (p3[0] - p0[0]) / 3
        c2y = p3[1]
        # Approximate bezier with small lines
        for s in range(10):
            u0 = s / 10
            u1 = (s + 1) / 10
            bx0 = (1-u0)**3 * p0[0] + 3*(1-u0)**2*u0*c1x + 3*(1-u0)*u0**2*c2x + u0**3*p3[0]
            by0 = (1-u0)**3 * p0[1] + 3*(1-u0)**2*u0*c1y + 3*(1-u0)*u0**2*c2y + u0**3*p3[1]
            bx1 = (1-u1)**3 * p0[0] + 3*(1-u1)**2*u1*c1x + 3*(1-u1)*u1**2*c2x + u1**3*p3[0]
            by1 = (1-u1)**3 * p0[1] + 3*(1-u1)**2*u1*c1y + 3*(1-u1)*u1**2*c2y + u1**3*p3[1]
            d.line((bx0, by0, bx1, by1), fill=color, width=width_l)


# ── 6. Metaballs — organic blobs that merge ───────────────────────
def metaballs(d, balls, progress, color=INK, threshold=1.0):
    """Simulated metaballs — blobs that merge when close."""
    # Simplified: draw overlapping circles with varying opacity to simulate merging
    for (bx, by, br, bphase) in balls:
        r = br * smoothstep(0, 1, progress)
        alpha = 0.15 + 0.1 * math.sin(bphase + progress * 3)
        for i in range(5):
            ri = r * (1 + i * 0.3)
            a = alpha * (1 - i * 0.15)
            d.ellipse((bx-ri, by-ri, bx+ri, by+ri),
                      fill=(color[0], color[1], color[2], int(255 * a)))


# ── 7. Perlin noise landscape ──────────────────────────────────────
def noise_landscape(d, progress, color=CHARCOAL):
    """A mountain-like terrain profile using layered sine noise."""
    p = smoothstep(0, 1, progress)
    n_layers = 4
    for layer in range(n_layers):
        a = p * (0.4 - layer * 0.08)
        if a <= 0: continue
        pts = []
        for x in range(0, W+5, 5):
            y_base = H - 100 - layer * 50
            noise_val = (math.sin(x * 0.005 + layer * 1.7) * 0.5 +
                         math.sin(x * 0.012 + layer * 3.2) * 0.3 +
                         math.sin(x * 0.025 + layer * 5.1) * 0.2)
            y = y_base + noise_val * 80 * p
            pts.append((x, y))
        for i in range(1, len(pts)):
            d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]),
                   fill=(color[0], color[1], color[2], int(255 * a)), width=1)


# ── 8. Turtle graphics — path with angle changes ──────────────────
def turtle_path(d, start_x, start_y, steps, step_size, turn_angle, progress, color=CHARCOAL):
    """A path where each step turns by a fixed angle — simple turtle."""
    n = int(steps * smoothstep(0, 1, progress))
    x, y = start_x, start_y
    angle = -math.pi / 2  # start upward
    for i in range(n):
        new_x = x + step_size * math.cos(angle)
        new_y = y + step_size * math.sin(angle)
        d.line((x, y, new_x, new_y), fill=color, width=1)
        x, y = new_x, new_y
        angle += turn_angle + math.sin(i * 0.1) * 0.05


# ── 9. Recursive subdivision (Sierpinski-like) ────────────────────
def recursive_subdivide(d, x, y, size, depth, progress, color=CHARCOAL):
    """Recursive triangular subdivision."""
    p = smoothstep(0, 1, progress)
    if depth <= 0 or p <= 0: return
    if depth <= 2 or p > 0.5:
        h = size * math.sqrt(3) / 2
        # Draw triangle
        d.line((x, y, x + size, y), fill=color, width=1)
        d.line((x, y, x + size/2, y - h), fill=color, width=1)
        d.line((x + size, y, x + size/2, y - h), fill=color, width=1)
        if depth > 1 and p > 0.3:
            child_p = (p - 0.3) / 0.7
            recursive_subdivide(d, x, y, size/2, depth-1, child_p, color)
            recursive_subdivide(d, x + size/2, y, size/2, depth-1, child_p, color)
            recursive_subdivide(d, x + size/4, y - h/2, size/2, depth-1, child_p, color)


# ── 10. Harmonic motion — coupled oscillators ─────────────────────
def harmonic_motion(d, cx, cy, count, max_r, t, color=CRIMSON):
    """Multiple orbiting points with harmonic coupling."""
    for i in range(count):
        phase = i * 2 * math.pi / count + t * 0.3
        freq1 = 0.7 + 0.3 * math.sin(i * 0.5)
        freq2 = 0.5 + 0.4 * math.cos(i * 0.7)
        r = max_r * (0.3 + 0.7 * abs(math.sin(t * 0.1 + i * 0.3)))
        x = cx + r * math.cos(phase * freq1)
        y = cy + r * math.sin(phase * freq2)
        s = 2 + 1.5 * math.sin(t * 0.5 + i)
        d.ellipse((x-s, y-s, x+s, y+s), fill=color)
    # Connecting lines between nearby points
    for i in range(count):
        phase_i = i * 2 * math.pi / count + t * 0.3
        ri = max_r * (0.3 + 0.7 * abs(math.sin(t * 0.1 + i * 0.3)))
        xi = cx + ri * math.cos(phase_i * (0.7 + 0.3*math.sin(i*0.5)))
        yi = cy + ri * math.sin(phase_i * (0.5 + 0.4*math.cos(i*0.7)))
        for j in range(i+1, count):
            phase_j = j * 2 * math.pi / count + t * 0.3
            rj = max_r * (0.3 + 0.7 * abs(math.sin(t * 0.1 + j * 0.3)))
            xj = cx + rj * math.cos(phase_j * (0.7 + 0.3*math.sin(j*0.5)))
            yj = cy + rj * math.sin(phase_j * (0.5 + 0.4*math.cos(j*0.7)))
            dist = math.sqrt((xi-xj)**2 + (yi-yj)**2)
            if dist < 150:
                d.line((xi, yi, xj, yj), fill=(color[0], color[1], color[2], int(100 * (1 - dist/150))), width=1)


# ── COMPOSITE DEMO ─────────────────────────────────────────────────
def demo_v3(t, u, idx):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    if t < 4:  # Flow field
        ff = FlowField(150)
        for _ in range(int(t * 10)):
            ff.update(t, 0.5)
        ff.draw(d, CHARCOAL)
        d.text((10, 10), "flow field", fill=MUTED)

    elif t < 8:  # Reaction-diffusion
        reaction_diffusion(d, W//2, H//2, 180, 20, (t-4)/3.5, CRIMSON)
        reaction_diffusion(d, W//2+120, H//2-50, 120, 15, (t-5)/2.5, GOLD)
        d.text((10, 10), "reaction-diffusion", fill=MUTED)

    elif t < 12:  # L-system tree
        lsystem_tree(d, W//2, H-50, 150, -math.pi/2, 6, (t-8)/3.5, CHARCOAL)
        d.text((10, 10), "l-system tree", fill=MUTED)

    elif t < 16:  # Cellular dots
        CELL_SIZE = 60
        random.seed(42)
        cellular_dots(d, 80, 15, (t-12)/3.5, CRIMSON)
        d.text((10, 10), "cellular / voronoi", fill=MUTED)

    elif t < 20:  # Bézier wave
        for i in range(4):
            bezier_wave(d, W//2, 200 + i*100, 800, 40 + i*10, 1.5 + i*0.3, t, CHARCOAL, 2)
        d.text((10, 10), "bezier waves", fill=MUTED)

    elif t < 24:  # Metaballs
        balls = [(400, 360, 80, 0), (640, 320, 70, 1.5), (880, 380, 90, 3.0),
                 (520, 420, 50, 4.2), (760, 280, 60, 5.7)]
        metaballs(d, balls, (t-20)/3.5, CRIMSON)
        d.text((10, 10), "metaballs", fill=MUTED)

    elif t < 28:  # Landscape
        noise_landscape(d, (t-24)/3.5, CHARCOAL)
        d.text((10, 10), "perlin landscape", fill=MUTED)

    elif t < 32:  # Turtle
        turtle_path(d, W//2, H//2, 200, 8, 1.8, (t-28)/3.5, CHARCOAL)
        d.text((10, 10), "turtle path", fill=MUTED)

    elif t < 36:  # Recursive subdivision
        recursive_subdivide(d, 200, H-50, 880, 4, (t-32)/3.5, CHARCOAL)
        d.text((10, 10), "recursive subdivision", fill=MUTED)

    else:  # Harmonic motion
        harmonic_motion(d, W//2, H//2, 16, 200, t * 0.5, CRIMSON)
        d.text((10, 10), "harmonic oscillators", fill=MUTED)

    return im
