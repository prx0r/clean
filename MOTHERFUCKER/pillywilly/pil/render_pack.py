"""
Gold Minute — essay 33 "the sun that knows itself"
8 shots, ~60 seconds, hand-crafted PIL scene functions.
Uses stable runtime: python -m factory.renderers.pil.runtime render_pack.py output/
"""
import math
from PIL import Image, ImageDraw, ImageFont

# ── CANVAS ─────────────────────────────────────────
W, H = 1280, 720

# ── PALETTE (gold material language) ──────────────
PARCHMENT = (245, 242, 238)
INK = (40, 40, 42)
GOLD = (180, 150, 60)
GOLD_LIGHT = (210, 190, 130)
CRIMSON = (160, 55, 55)
LAPIS = (55, 75, 120)
SILVER = (180, 188, 195)
DARK = (50, 52, 55)
WHITE = (250, 248, 244)

def canvas(bg=PARCHMENT):
    return Image.new("RGB", (W, H), bg)

def border(d):
    for i in range(4):
        d.rectangle([i, i, W-1-i, H-1-i], outline=(215, 210, 205), width=1)

# ── SHOT 1: Point of light in darkness ────────────
def s001(ctx, t, u):
    im = canvas((20, 20, 26))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    r = 15 + 30 * u
    for i in range(5):
        glow = int(60 - i * 10)
        d.ellipse([cx - r * (1 + i * 0.3), cy - r * (1 + i * 0.3),
                   cx + r * (1 + i * 0.3), cy + r * (1 + i * 0.3)],
                  outline=(GOLD[0], GOLD[1], GOLD[2], glow), width=1)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD_LIGHT)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=(255, 240, 200))
    return im

# ── SHOT 2: Sun corona forming ────────────────────
def s002(ctx, t, u):
    im = canvas((20, 20, 26))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    # Core
    d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=GOLD)
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=GOLD_LIGHT)
    # Corona rays emerging
    n_rays = int(8 + 16 * u)
    for i in range(n_rays):
        angle = (i / n_rays) * 2 * math.pi + t * 0.3
        length = 80 + 60 * u * (0.5 + 0.5 * math.sin(i * 1.3))
        x1 = cx + 50 * math.cos(angle)
        y1 = cy + 50 * math.sin(angle)
        x2 = cx + (50 + length) * math.cos(angle)
        y2 = cy + (50 + length) * math.sin(angle)
        d.line([(x1, y1), (x2, y2)], fill=GOLD_LIGHT, width=2)
    return im

# ── SHOT 3: Mirror pool ───────────────────────────
def s003(ctx, t, u):
    im = canvas(PARCHMENT)
    d = ImageDraw.Draw(im)
    cx = W // 2
    # Horizon line
    y_h = H // 2
    d.line([(100, y_h), (W - 100, y_h)], fill=INK, width=2)
    # Sky — warm light above
    d.rectangle([(100, 80), (W - 100, y_h)], fill=(255, 245, 230))
    # Pool below — reflection
    d.rectangle([(100, y_h), (W - 100, H - 80)], fill=(230, 225, 220))
    # Reflected circle
    r = 40 + 20 * math.sin(t * 2)
    d.ellipse([cx - r, y_h + 30 - r * 0.5, cx + r, y_h + 30 + r * 0.5],
              outline=SILVER, width=2)
    border(d)
    return im

# ── SHOT 4: Gold seam through stone ──────────────
def s004(ctx, t, u):
    im = canvas(PARCHMENT)
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    # Stone mass
    d.ellipse([cx - 200, cy - 120, cx + 200, cy + 120], fill=(220, 215, 208))
    d.ellipse([cx - 180, cy - 100, cx + 180, cy + 100], fill=(210, 205, 198))
    # Gold seam fracturing through
    points = [(cx - 180, cy - 20)]
    for i in range(1, 12):
        x = cx - 180 + i * 32
        y = cy + 40 * math.sin(x * 0.03 + u * 2)
        points.append((x, y))
    for i in range(len(points) - 1):
        d.line([points[i], points[i+1]], fill=GOLD, width=4)
    # Gold glow
    for i in range(3):
        d.line([points[i], points[i+1]], fill=GOLD_LIGHT, width=8)
    border(d)
    return im

# ── SHOT 5: Thread connecting two forms ──────────
def s005(ctx, t, u):
    im = canvas(PARCHMENT)
    d = ImageDraw.Draw(im)
    # Left form
    d.ellipse([200, 260, 320, 380], outline=INK, width=3)
    # Right form
    d.ellipse([960, 260, 1080, 380], outline=INK, width=3)
    # Thread weaving between
    points = []
    for i in range(20):
        x = 300 + i * 35
        y = 320 + 60 * math.sin(x * 0.03 + u * 3)
        points.append((x, y))
    for i in range(len(points) - 1):
        w = 1 + int(u * 3)
        d.line([points[i], points[i+1]], fill=CRIMSON, width=w)
    border(d)
    return im

# ── SHOT 6: Vessel preparing ─────────────────────
def s006(ctx, t, u):
    im = canvas(PARCHMENT)
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2 + 40
    # Vessel body
    d.rectangle([cx - 120, cy - 80, cx + 120, cy + 80], outline=INK, width=3)
    d.rectangle([cx - 100, cy - 60, cx + 100, cy + 60], outline=SILVER, width=1)
    d.rectangle([cx - 80, cy - 40, cx + 80, cy + 40], outline=GOLD, width=1)
    # Content filling
    fill_h = int(60 * u)
    d.rectangle([cx - 78, cy + 38 - fill_h, cx + 78, cy + 38], fill=GOLD_LIGHT)
    border(d)
    return im

# ── SHOT 7: Light recognizes itself ──────────────
def s007(ctx, t, u):
    im = canvas((20, 20, 26))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    # Two lights approaching
    separation = 300 - 280 * u
    for side, offset in [(-1, "left"), (1, "right")]:
        x = cx + side * separation // 2
        r = 20 + 15 * (1 - u)
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=GOLD_LIGHT)
        d.ellipse([x - r * 0.5, cy - r * 0.5, x + r * 0.5, cy + r * 0.5], fill=(255, 240, 200))
    # Merging glow
    if u > 0.5:
        m = (u - 0.5) * 2
        d.ellipse([cx - 60 * m, cy - 60 * m, cx + 60 * m, cy + 60 * m],
                  outline=GOLD, width=2)
    return im

# ── SHOT 8: Completed circle — closing seal ──────
def s008(ctx, t, u):
    im = canvas((20, 20, 26))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    # Circle completing
    r = 80 + 60 * u
    start_angle = 0
    end_angle = 360 * u
    d.arc([cx - r, cy - r, cx + r, cy + r], start_angle, end_angle, fill=GOLD, width=3)
    if u > 0.9:
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD_LIGHT)
    # Inner
    if u > 0.5:
        ri = 30 * (u - 0.5) * 2
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], outline=GOLD_LIGHT, width=1)
    return im


# ── SCENE REGISTRY ─────────────────────────────────
from factory.renderers.pil.runtime import SceneSpec

SCENES = [
    SceneSpec("s001", 7.0, s001),
    SceneSpec("s002", 8.0, s002),
    SceneSpec("s003", 7.5, s003),
    SceneSpec("s004", 8.0, s004),
    SceneSpec("s005", 7.0, s005),
    SceneSpec("s006", 7.5, s006),
    SceneSpec("s007", 8.0, s007),
    SceneSpec("s008", 7.0, s008),
]
