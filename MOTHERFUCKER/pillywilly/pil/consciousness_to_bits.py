"""Consciousness → Information: wave becomes bit, continuous becomes discrete.
Spanda as the pulse that resolves into 1/0, on/off, presence/absence."""

import math, random
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
DARK = (12, 12, 15); WHITE = (248, 246, 240); CHARCOAL = (40, 40, 40)
MUTED = (145, 141, 132); CRIMSON = (141, 44, 57); GOLD = (208, 172, 91)
INK = (235, 231, 220)

def p(t, o=0, s=1.0): return 0.5+0.5*math.sin(t*s+o)
def canvas(bg=WHITE): return Image.new("RGB", (W, H), bg)

# ── Consciousness → Information ──────────────────────────────────
# Wave gradually becomes discrete bits. The pulse resolves into 1s and 0s.

def scene_wave_to_bits(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Stage 1 (t=0-4): Pure wave — continuous
    if t < 4:
        pts = []
        for x in range(-300, 301, 4):
            y = 80 * p(t + x*0.01, 0, 0.6)
            pts.append((cx+x, cy+y))
        for i in range(1, len(pts)):
            d.line((pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1]), fill=CHARCOAL, width=2)

    # Stage 2 (t=4-8): Wave begins to fragment — dots appear
    elif t < 8:
        progress = (t - 4) / 4
        for i in range(80):
            x = cx - 300 + i * 7.5
            wave_y = 80 * p(t + i*0.04, 0, 0.6)
            # Dots replace line progressively
            if random.random() < progress:
                r = 2 + 2 * p(t + i*0.1, 0, 0.8)
                d.ellipse((x-r, cy+wave_y-r, x+r, cy+wave_y+r), fill=CHARCOAL)
            else:
                pass  # gap — the space between bits

    # Stage 3 (t=8-12): Pure bits — 1s and 0s
    else:
        bits = []
        for i in range(40):
            x = cx - 280 + i * 14
            # Each bit state comes from the pulse
            val = 1 if p(t + i*0.15, 0, 0.4) > 0.5 else 0
            if val:
                r = 4
                d.ellipse((x-r, cy-r, x+r, cy+r), fill=CHARCOAL)
            bits.append(val)

        # Label
        d.text((cx-30, cy+40), "1  0  1  0  1  0", fill=MUTED)

    # Title
    d.text((cx-80, 60), "consciousness → information", fill=MUTED)
    return im


# ── Pulse as Binary ──────────────────────────────────────────────
# Pure 1s and 0s arranged in a wave pattern

def scene_binary_pulse(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    for i in range(60):
        x = cx - 300 + i * 10
        val = 1 if p(t + i*0.1, 0, 0.5) > 0.5 else 0
        if val:
            y_offset = 30 * math.sin(i * 0.3)
            d.ellipse((x-3, cy+y_offset-3, x+3, cy+y_offset+3), fill=CHARCOAL)

    d.text((cx-50, 60), "spanda as binary", fill=MUTED)
    return im


# ── The Bit That Contains Everything ─────────────────────────────
# A single 1 pulses, expands, becomes the universe

def scene_the_bit(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # A single bit that pulses and radiates
    pulse = p(t, 0, 0.3)
    r = 5 + 200 * pulse

    for i in range(8):
        ri = r + i * 30 * p(t + i*0.2, 0, 0.5)
        a = 0.15 - i * 0.015
        d.ellipse((cx-ri, cy-ri, cx+ri, cy+ri), outline=CHARCOAL, width=1)

    # The bit at center
    d.ellipse((cx-8, cy-8, cx+8, cy+8), fill=CRIMSON)
    d.text((cx-25, cy-30), "1", fill=CHARCOAL)

    d.text((cx-70, 60), "the bit that contains everything", fill=MUTED)
    return im


# ═══════════════════════════════════════════════════════════════════
# PERFECTED QUOTE TEMPLATE — reusable, production-grade
# ═══════════════════════════════════════════════════════════════════

def make_quote(quote, author=None, source=None, theme="dark"):
    """Generate a reusable quote page. Returns a function (t, u, idx) → Image."""
    def scene(t, u, idx):
        bg = DARK if theme == "dark" else WHITE
        tx = INK if theme == "dark" else CHARCOAL
        im = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(im)

        progress = min(1, t / 3)

        # Decorative top and bottom lines
        if progress > 0:
            da = min(1, progress * 2)
            d.line((120, 100, W-120, 100), fill=GOLD, width=1)
            d.line((120, H-100, W-120, H-100), fill=GOLD, width=1)

        # Large opening quote mark
        if progress > 0.1:
            a = min(1, (progress - 0.1) / 0.3)
            d.text((120, 130), "❝", fill=GOLD)

        # Quote text — centered, wrapped
        if progress > 0.2:
            a = min(1, (progress - 0.2) / 0.4)
            # Wrap to ~60 chars per line
            words = quote.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) < 60:
                    cur += " " + w if cur else w
                else:
                    lines.append(cur)
                    cur = w
            if cur: lines.append(cur)

            y_start = 230
            for i, line in enumerate(lines):
                d.text((200, y_start + i*45), line, fill=tx)

        # Author & source
        y_auth = 230 + len(quote.split(" ")) * 45 // 60 * 45 + 50
        if author and progress > 0.5:
            a = min(1, (progress - 0.5) / 0.3)
            d.text((200, y_auth), f"— {author}", fill=MUTED)
        if source and progress > 0.6:
            a = min(1, (progress - 0.6) / 0.3)
            d.text((200, y_auth + 35), source, fill=MUTED)

        return im
    return scene

# Pre-built quotes using the template
QUOTES = [
    ("Spanda is the hidden pulse that controls everything you experience.",
     "Spanda Kārikā", "1.1", "dark"),
    ("The centre is the Heart, the pulsing core of consciousness.",
     "Tantrāloka", "Abhinavagupta", "dark"),
    ("All Mantras are the dynamic pulsing nature of consciousness.",
     "Tantrāloka", "", "dark"),
    ("When you know yourself as the pulse, desire becomes creative power.",
     "Spanda Kārikā", "", "dark"),
    ("The universe pulses — pulsing is what joy does when it moves.",
     "Tantrāloka", "Somānanda", "light"),
    ("The six bliss is complete expansion.",
     "Tantrāloka", "Abhinavagupta", "dark"),
]

quote_scenes = []
for q_text, q_auth, q_src, q_theme in QUOTES:
    name = f"quote_{q_auth.split()[0] if q_auth else 'anon'}"
    fn = make_quote(q_text, q_auth, q_src, q_theme)
    quote_scenes.append((name, fn, 10, f"Quote: {q_text[:40]}..."))

# ── Register ──────────────────────────────────────────────────────
ALL_SCENES = [
    ("wave_to_bits", scene_wave_to_bits, 12, "wave becomes discrete bits"),
    ("binary_pulse", scene_binary_pulse, 10, "1s and 0s as wave"),
    ("the_bit", scene_the_bit, 10, "one bit contains all"),
] + quote_scenes
