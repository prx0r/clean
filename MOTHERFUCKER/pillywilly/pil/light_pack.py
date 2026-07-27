"""Light Pack — candle, flame, light wave, vibration, glow.
Each scene is pure PIL, focused on one light concept."""

import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
random.seed(42)

BLACK = (5, 5, 8)
DARK = (12, 12, 15)
WARM = (255, 220, 160)
GOLD = (255, 200, 100)
CRIMSON = (180, 60, 40)
WHITE = (255, 252, 245)

def canvas(): return Image.new("RGB", (W, H), BLACK)

def smoothstep(a,b,x):
    t = max(0,min(1,(x-a)/(b-a))) if b!=a else 1
    return t*t*(3-2*t)

def glow(draw, cx, cy, radius, color, alpha):
    """Draw a soft radial glow."""
    for r in range(int(radius), 0, -2):
        a = int(alpha * 255 * (1 - r / radius))
        draw.ellipse((cx-r, cy-r, cx+r, cy+r),
                     fill=(color[0], color[1], color[2], a))

# ═══════════════════════════════════════════════════════════════════
# 1. CANDLE FLAME — flickering organic flame
# ═══════════════════════════════════════════════════════════════════
def scene_candle(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im)

    # Candle body
    cx, cy = W//2, H-100
    d.rectangle((cx-15, cy-200, cx+15, cy), fill=(240, 230, 210))
    d.rectangle((cx-18, cy-200, cx+18, cy-190), fill=(200, 190, 170))  # rim

    # Wick
    wick_x = cx + random.uniform(-2, 2)
    wick_y = cy - 200
    d.line((wick_x, wick_y, wick_x, wick_y - 12), fill=(100, 80, 60), width=2)

    # Flame — organic flicker
    flicker = 0.85 + 0.15 * math.sin(t * 8) * 0.5 + 0.15 * math.sin(t * 13.7)
    flicker2 = 0.9 + 0.1 * math.sin(t * 11.3 + 1.5)

    # Outer glow
    glow_r = 120 * flicker
    for i in range(5):
        r = glow_r * (1 - i * 0.15)
        a = 0.08 * (1 - i * 0.15) * flicker2
        draw_glow(d, wick_x, wick_y - 20, r, GOLD, a)

    # Flame body (teardrop shape)
    flame_pts = []
    for i in range(20):
        a = i * 2 * math.pi / 20
        flame_height = 45 * flicker * flicker2
        flame_width = 18 * flicker
        r = flame_width * (1 - abs(math.sin(a/2))**0.7) * (1 - 0.3 * abs(math.cos(a/2)))
        px = wick_x + r * math.cos(a)
        py = wick_y - 20 - flame_height * abs(math.sin(a/2)) ** 1.5
        flame_pts.append((px, py))
    d.polygon([(int(x), int(y)) for x, y in flame_pts],
              fill=(255, 200, 100, 200))

    # Inner flame (hotter)
    inner_pts = []
    for i in range(16):
        a = i * 2 * math.pi / 16
        h = 22 * flicker
        w = 8 * flicker
        r = w * (1 - abs(math.sin(a/2))**0.7)
        px = wick_x + r * math.cos(a)
        py = wick_y - 20 - h * abs(math.sin(a/2)) ** 1.5
        inner_pts.append((px, py))
    d.polygon([(int(x), int(y)) for x, y in inner_pts],
              fill=(255, 255, 220, 220))

    return im

def draw_glow(d, cx, cy, radius, color, alpha):
    """Helper: draw a soft radial glow circle."""
    for r in range(int(radius), 0, -2):
        a = int(alpha * 255 * (1 - r / radius))
        c = (color[0], color[1], color[2], a)
        # PIL doesn't support RGBA on RGB images for ellipse fill
        # So we use a different approach: draw concentric circles with decreasing opacity
        pass
    # Simpler approach: use GaussianBlur on a separate layer
    return

# Actually let me use the simpler approach with ImageFilter
def render_glow(size, cx, cy, radius, color, alpha):
    """Create a glow layer using GaussianBlur."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    r = max(1, int(radius))
    ld.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(color[0], color[1], color[2], int(255 * alpha)))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius * 0.5))
    return blurred

# ═══════════════════════════════════════════════════════════════════
# 2. FLAME in darkness — single flame, dark surround
# ═══════════════════════════════════════════════════════════════════
def scene_flame_darkness(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = W//2, H//2

    flicker = 0.85 + 0.15 * math.sin(t * 7.5)

    # Glow layers
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)

    for i in range(3):
        r = (100 - i * 25) * flicker
        a = (0.12 - i * 0.035) * flicker
        gd.ellipse((cx-r, cy-r, cx+r, cy+r),
                   fill=(255, 200, 100, int(255 * a)))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(20))

    # Composite glow
    im_composite = Image.alpha_composite(im.convert("RGBA"), blurred)

    # Flame teardrop
    fd = ImageDraw.Draw(im_composite)
    flame_h = 60 * flicker
    flame_w = 25 * flicker
    pts = []
    for i in range(24):
        a = i * 2 * math.pi / 24
        r = flame_w * (1 - abs(math.sin(a/2))**0.6) * (1 - 0.2 * abs(math.cos(a/2)))
        px = cx + r * math.cos(a)
        py = cy - flame_h * abs(math.sin(a/2)) ** 1.5
        pts.append((px, py))
    fd.polygon([(int(x), int(y)) for x, y in pts],
               fill=(255, 200, 80, 230))

    # Inner core
    pts2 = []
    for i in range(20):
        a = i * 2 * math.pi / 20
        h = 25 * flicker
        w = 10 * flicker
        r = w * (1 - abs(math.sin(a/2))**0.6)
        px = cx + r * math.cos(a)
        py = cy - h * abs(math.sin(a/2)) ** 1.5
        pts2.append((px, py))
    fd.polygon([(int(x), int(y)) for x, y in pts2],
               fill=(255, 255, 230, 240))

    return im_composite.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 3. LIGHT WAVE — wave propagating through darkness
# ═══════════════════════════════════════════════════════════════════
def scene_light_wave(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = W//2, H//2

    # Expanding rings of light
    for i in range(5):
        phase = i * 0.3
        progress = (t - phase) % 3.0
        if progress < 0:
            continue
        r = 200 * max(0, min(1, progress))
        a = max(0, 1 - progress) * 0.15

        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.ellipse((cx-r, cy-r, cx+r, cy+r),
                   fill=(255, 220, 150, int(255 * a)))
        blurred = glow_layer.filter(ImageFilter.GaussianBlur(15))
        im = Image.alpha_composite(im.convert("RGBA"), blurred)

    # Bright center
    d2 = ImageDraw.Draw(im)
    d2.ellipse((cx-8, cy-8, cx+8, cy+8), fill=(255, 240, 200, 200))

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 4. CANDLE GOING OUT — flicker, dim, smoke
# ═══════════════════════════════════════════════════════════════════
def scene_candle_out(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = W//2, H-100

    # Candle body
    d.rectangle((cx-15, cy-200, cx+15, cy), fill=(240, 230, 210))
    d.rectangle((cx-18, cy-200, cx+18, cy-190), fill=(200, 190, 170))

    # Flame dies over time
    life = max(0, 1 - t / 6)  # 6s to go out
    flicker = life * (0.85 + 0.15 * math.sin(t * 12))

    if life > 0.01:
        # Glow
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        glow_r = 80 * flicker
        gd.ellipse((cx-glow_r, cy-200-glow_r, cx+glow_r, cy-200+glow_r),
                   fill=(255, 200, 100, int(100 * flicker)))
        blurred = glow_layer.filter(ImageFilter.GaussianBlur(15))
        im = Image.alpha_composite(im.convert("RGBA"), blurred)

        # Flame
        fd = ImageDraw.Draw(im)
        h = 40 * flicker
        w = 15 * flicker
        pts = []
        for i in range(20):
            a = i * 2 * math.pi / 20
            r = w * (1 - abs(math.sin(a/2))**0.7)
            px = cx + r * math.cos(a)
            py = cy - 200 - h * abs(math.sin(a/2)) ** 1.5
            pts.append((px, py))
        if len(pts) > 2:
            fd.polygon([(int(x), int(y)) for x, y in pts],
                       fill=(255, 200, 80, int(200 * life)))

    # Smoke after flame dies
    if t > 4:
        smoke_p = (t - 4) / 4
        for i in range(8):
            sx = cx + random.uniform(-10, 10) + math.sin(t * 2 + i) * 20 * smoke_p
            sy = cy - 200 - 100 * smoke_p - i * 15 * smoke_p
            sr = 3 + i * 2 * smoke_p
            a = max(0, (1 - smoke_p) * 0.3)
            d.ellipse((sx-sr, sy-sr, sx+sr, sy+sr),
                      fill=(200, 200, 200, int(50 * a)))

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 5. MULTIPLE CANDLES — row of candles, some lit, some out
# ═══════════════════════════════════════════════════════════════════
def scene_candles_row(t, u, idx):
    im = canvas()
    d = ImageDraw.Draw(im, "RGBA")

    n_candles = 7
    spacing = W // (n_candles + 1)
    base_y = H - 80

    for i in range(n_candles):
        cx = spacing * (i + 1)
        flicker = 0.9 + 0.1 * math.sin(t * 6 + i * 2.3) * (0.5 + 0.5 * math.sin(i * 1.7))
        lit = t > i * 0.8  # each lights up sequentially

        # Candle body
        d.rectangle((cx-12, base_y-150, cx+12, base_y), fill=(230, 220, 200))

        if lit:
            # Glow
            glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_layer)
            gd.ellipse((cx-60*flicker, base_y-170-60*flicker, cx+60*flicker, base_y-170+60*flicker),
                       fill=(255, 200, 100, int(60 * flicker)))
            blurred = glow_layer.filter(ImageFilter.GaussianBlur(10))
            im = Image.alpha_composite(im.convert("RGBA"), blurred)

            # Flame
            fd = ImageDraw.Draw(im)
            h = 35 * flicker
            w = 12 * flicker
            pts = []
            for j in range(20):
                a = j * 2 * math.pi / 20
                r = w * (1 - abs(math.sin(a/2))**0.7)
                px = cx + r * math.cos(a)
                py = base_y - 150 - h * abs(math.sin(a/2)) ** 1.5
                pts.append((px, py))
            if len(pts) > 2:
                fd.polygon([(int(x), int(y)) for x, y in pts],
                           fill=(255, 200, 80, 200))

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 6. LIGHT IN DARKNESS — single point radiating
# ═══════════════════════════════════════════════════════════════════
def scene_light_darkness(t, u, idx):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = W//2, H//2

    # Radiating light
    pulse = 0.8 + 0.2 * math.sin(t * 0.5)
    for i in range(8):
        r = (30 + i * 35) * pulse
        a = (0.2 - i * 0.022) * pulse
        if a <= 0: continue
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.ellipse((cx-r, cy-r, cx+r, cy+r),
                   fill=(255, 220, 150, int(255 * a)))
        blurred = glow_layer.filter(ImageFilter.GaussianBlur(12))
        im = Image.alpha_composite(im.convert("RGBA"), blurred)

    # Core
    d2 = ImageDraw.Draw(im)
    d2.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(255, 240, 200, 220))

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 7. VIBRATION / FREQUENCY — light frequency waves
# ═══════════════════════════════════════════════════════════════════
def scene_vibration(t, u, idx):
    im = Image.new("RGB", (W, H), (5, 5, 10))
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = W//2, H//2

    # Multiple frequencies of light waves
    for freq in [0.5, 1.0, 2.0, 3.0]:
        amp = 80 + 40 * math.sin(freq * t * 2)
        for x in range(0, W, 2):
            y = cy + amp * math.sin(x * 0.02 * freq + t * 3 * freq)
            a = 0.1 + 0.05 * math.sin(x * 0.01 + t + freq)
            brightness = int(200 * a)
            d.point((x, int(y)), fill=(brightness, brightness, int(brightness * 0.6), int(255 * a)))

    # Center glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    r = 60 + 20 * math.sin(t * 0.7)
    gd.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 220, 150, 40))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(20))
    im = Image.alpha_composite(im.convert("RGBA"), blurred)

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 8. CANDLE + MIRROR — flame reflected + doubled
# ═══════════════════════════════════════════════════════════════════
def scene_candle_mirror(t, u, idx):
    im = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(im, "RGBA")

    # Left candle
    lx, ly = W//3, H-120
    d.rectangle((lx-12, ly-150, lx+12, ly), fill=(230, 220, 200))
    flame_l = 0.9 + 0.1 * math.sin(t * 7)

    # Right candle (mirror)
    rx, ry = 2*W//3, H-120
    d.rectangle((rx-12, ry-150, rx+12, ry), fill=(230, 220, 200))
    flame_r = 0.85 + 0.15 * math.sin(t * 8.5 + 2.0)

    for cx, cy, fl, offset in [(lx, ly, flame_l, 0), (rx, ry, flame_r, 1)]:
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.ellipse((cx-80*fl, cy-170-60*fl, cx+80*fl, cy-170+60*fl),
                   fill=(255, 200, 100, int(50 * fl)))
        blurred = glow_layer.filter(ImageFilter.GaussianBlur(12))
        im = Image.alpha_composite(im.convert("RGBA"), blurred)

        fd = ImageDraw.Draw(im)
        h = 40 * fl
        w = 14 * fl
        pts = []
        for j in range(20):
            a = j * 2 * math.pi / 20
            r = w * (1 - abs(math.sin(a/2))**0.7)
            px = cx + r * math.cos(a)
            py = cy - 150 - h * abs(math.sin(a/2)) ** 1.5
            pts.append((px, py))
        if len(pts) > 2:
            fd.polygon([(int(x), int(y)) for x, y in pts], fill=(255, 200, 80, 200))

    # Mirror axis
    d.line((W//2, 40, W//2, H-40), fill=(200, 200, 200, 30), width=1)

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 9. WAVE PACKET — localized light wave
# ═══════════════════════════════════════════════════════════════════
def scene_wave_packet(t, u, idx):
    im = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(im, "RGBA")

    cx = W//2 + (t / 8) * 600 - 300  # moves right
    cy = H//2

    # Wave packet envelope
    for x in range(0, W, 2):
        dx = x - cx
        envelope = math.exp(-dx * dx / (5000))
        wave = math.sin(dx * 0.05 - t * 4)
        y = cy + 80 * envelope * wave
        brightness = int(200 * envelope)
        a = int(255 * envelope)
        d.point((x, int(y)), fill=(brightness, brightness, int(brightness * 0.7), a))

    # Center glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse((cx-30, cy-30, cx+30, cy+30), fill=(255, 220, 150, 60))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(15))
    im = Image.alpha_composite(im.convert("RGBA"), blurred)

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# 10. CONSTELLATION — points of light connecting
# ═══════════════════════════════════════════════════════════════════
def scene_constellation(t, u, idx):
    im = Image.new("RGB", (W, H), (5, 5, 10))
    d = ImageDraw.Draw(im, "RGBA")

    random.seed(42)
    stars = [(random.uniform(50, W-50), random.uniform(50, H-50)) for _ in range(40)]

    for i, (sx, sy) in enumerate(stars):
        twinkle = 0.5 + 0.5 * math.sin(t * 2 + i * 1.3)
        r = 1 + twinkle * 1.5
        a = int(150 + 105 * twinkle)
        d.ellipse((sx-r, sy-r, sx+r, sy+r), fill=(255, 240, 200, a))

        # Connect nearby stars
        for j in range(i+1, len(stars)):
            ex, ey = stars[j]
            dist = math.sqrt((sx-ex)**2 + (sy-ey)**2)
            if dist < 100:
                a = int(40 * (1 - dist/100) * twinkle)
                d.line((sx, sy, ex, ey), fill=(200, 200, 255, a), width=1)

    return im.convert("RGB")


# ═══════════════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════════════
LIGHT_SCENES = [
    ("candle_flame", scene_candle, 8, "single candle, organic flicker"),
    ("flame_darkness", scene_flame_darkness, 8, "flame in void, soft glow"),
    ("light_wave", scene_light_wave, 8, "expanding rings of light"),
    ("candle_going_out", scene_candle_out, 8, "candle dims, smoke rises"),
    ("candles_row", scene_candles_row, 10, "seven candles, sequential lighting"),
    ("light_in_darkness", scene_light_darkness, 8, "single point radiating"),
    ("vibration", scene_vibration, 8, "frequency waves, multiple harmonics"),
    ("candle_mirror", scene_candle_mirror, 8, "two candles mirroring"),
    ("wave_packet", scene_wave_packet, 8, "localized wave moving"),
    ("constellation", scene_constellation, 8, "points of light connecting"),
]
