"""Focus pack: L-systems, subdivision, harmonic oscillators. Variable speed."""

import math, random
from PIL import Image, ImageDraw

CHARCOAL = (40, 40, 40); CRIMSON = (141, 44, 57); WHITE = (248, 246, 240)

def smoothstep(a,b,x):
    t = max(0,min(1,(x-a)/(b-a))) if b!=a else 1
    return t*t*(3-2*t)
DARK = (12, 12, 15); INK = (235, 231, 220); GOLD = (208, 172, 91); MUTED = (145, 141, 132)
W, H = 1280, 720
random.seed(42)

# ── SPEED CONTROL — the key innovation ──────────────────────────
# Instead of linear progress, we use velocity curves.
# speed_profile(t, segments) returns progress 0→1 with variable speed.
# segments = [(start_t, end_t, speed_multiplier), ...]

def speed_profile(t, segments):
    """Map time t to progress 0→1 using variable-speed segments."""
    total_weight = sum((e - s) * m for s, e, m in segments)
    if total_weight <= 0: return min(1, t)
    elapsed = 0
    for s, e, m in segments:
        if t < s: break
        seg_dur = min(t, e) - s
        elapsed += seg_dur * m
        if t <= e: break
    return min(1, elapsed / total_weight)

# ── 1. L-SYSTEM TREE with variable speed ───────────────────────
def draw_lsystem(d, cx, cy, length, angle, depth, progress, color=CHARCOAL, width=2):
    """Recursive branching tree. progress 0→1, speed can vary."""
    if depth <= 0 or progress <= 0: return
    branches = min(depth, max(1, int(3 * progress)))
    if branches < 1: return

    end_x = cx + length * math.cos(angle)
    end_y = cy + length * math.sin(angle)
    d.line((cx, cy, end_x, end_y), fill=color, width=max(1, width))

    child_progress = max(0, (progress - 0.2) / 0.8)
    if depth > 1 and child_progress > 0:
        spread = 0.6 + depth * 0.08
        for i in range(branches):
            child_angle = angle + (i - (branches-1)/2) * spread
            child_len = length * (0.62 + 0.05 * math.sin(depth * 1.3 + i * 2.1))
            draw_lsystem(d, end_x, end_y, child_len, child_angle, depth-1,
                        child_progress, color, max(1, width-1))

def scene_lsystem(t, speed=1.0):
    """L-system scene with speed control. t = seconds."""
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    # Speed profile: start fast, slow down for detail
    segments = [(0, 1, 2.0 * speed), (1, 3, speed), (3, 5, 0.5 * speed)]
    progress = speed_profile(t, segments)

    draw_lsystem(d, W//2, H-60, 140, -math.pi/2, 7, progress, CHARCOAL, 3)
    d.text((10, 10), f"L-system tree  speed={speed:.1f}", fill=MUTED)
    return im

# ── 2. RECURSIVE SUBDIVISION with variable speed ───────────────
def draw_subdivision(d, x, y, size, depth, progress, color=CHARCOAL):
    """Sierpinski-style triangular subdivision."""
    if depth <= 0 or progress <= 0: return
    h = size * math.sqrt(3) / 2

    # Triangle outline
    d.line((x, y, x + size, y), fill=color, width=1)
    d.line((x, y, x + size/2, y - h), fill=color, width=1)
    d.line((x + size, y, x + size/2, y - h), fill=color, width=1)

    if depth > 1 and progress > 0.3:
        child_p = (progress - 0.3) / 0.7
        draw_subdivision(d, x, y, size/2, depth-1, child_p, color)
        draw_subdivision(d, x + size/2, y, size/2, depth-1, child_p, color)
        draw_subdivision(d, x + size/4, y - h/2, size/2, depth-1, child_p, color)

def scene_subdivision(t, speed=1.0):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    # Speed profile: slow reveal, then accelerate
    segments = [(0, 2, 0.5 * speed), (2, 4, speed), (4, 6, 2.0 * speed)]
    progress = speed_profile(t, segments)

    draw_subdivision(d, 200, H-60, 880, 5, progress, GOLD)
    d.text((10, 10), f"Sierpinski subdivision  speed={speed:.1f}", fill=MUTED)
    return im

# ── 3. HARMONIC OSCILLATORS with variable speed ────────────────
def draw_harmonic(d, cx, cy, count, max_r, t, progress, color=CRIMSON, connections=True):
    """Coupled oscillators. t = time, progress = 0→1 for building."""
    active = int(count * progress)
    if active < 2: return

    points = []
    for i in range(active):
        phase = i * 2 * math.pi / count + t * 0.3
        freq1 = 0.7 + 0.3 * math.sin(i * 0.5 + progress * 2)
        freq2 = 0.5 + 0.4 * math.cos(i * 0.7 + progress * 1.5)
        r = max_r * (0.3 + 0.7 * abs(math.sin(t * 0.1 + i * 0.3)))
        x = cx + r * math.cos(phase * freq1)
        y = cy + r * math.sin(phase * freq2)
        points.append((x, y))
        s = 2 + 1.5 * math.sin(t * 0.5 + i)
        d.ellipse((x-s, y-s, x+s, y+s), fill=color)

    # Connecting lines — draw at reduced opacity
    if connections:
        for i in range(active):
            for j in range(i+1, active):
                xi, yi = points[i]
                xj, yj = points[j]
                dist = math.sqrt((xi-xj)**2 + (yi-yj)**2)
                if dist < 200:
                    a = int(80 * (1 - dist/200) * progress)
                    d.line((xi, yi, xj, yj), fill=(color[0], color[1], color[2], a), width=1)

def scene_harmonic(t, speed=1.0):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)

    # Speed profile: fast build, then slow oscillation
    segments = [(0, 1, 2.0 * speed), (1, 3, speed), (3, 6, 0.3 * speed)]
    progress = speed_profile(t, segments)

    draw_harmonic(d, W//2, H//2, 24, 220, t * 0.5 * speed, progress, GOLD, True)
    d.text((10, 10), f"Harmonic oscillators  speed={speed:.1f}", fill=MUTED)
    return im

# ── COMPOSITE DEMO: all 3, each with speed variation ────────────
def demo_focus(t, u, idx):
    if t < 5:  # L-system at varying speed
        sp = 0.5 + 1.5 * smoothstep(0, 4, t)  # accelerates
        return scene_lsystem(t, sp)
    elif t < 10:  # Subdivision
        sp = 1.0 + math.sin(t * 0.5)  # oscillates speed
        return scene_subdivision(t - 5, sp)
    else:  # Harmonic
        sp = 0.3 + 1.7 * (0.5 + 0.5 * math.sin(t * 0.3))
        return scene_harmonic(t - 10, sp)
