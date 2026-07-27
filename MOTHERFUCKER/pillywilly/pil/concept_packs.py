"""Concept packs: deity representation, quote templates, premium visuals.
All pure PIL. No external assets needed."""

import math, random
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
random.seed(42)

# Palette
GOLD = (208, 172, 91); CRIMSON = (141, 44, 57); DARK = (12, 12, 15)
INK = (235, 231, 220); MUTED = (145, 141, 132); WHITE = (248, 246, 240)
BLACK = (19, 19, 21)
CHARCOAL = (40, 40, 40)

def clamp(v, l=0, h=1): return max(l, min(h, v))
def smoothstep(a,b,x): t=clamp((x-a)/(b-a)) if b!=a else 1; return t*t*(3-2*t)

# ═══════════════════════════════════════════════════════════════════
# DEITY REPRESENTATION
# Each deity = geometric form + color + motion signature
# ═══════════════════════════════════════════════════════════════════

DEITIES = {
    "śiva":       {"color": GOLD,   "form": "circle",     "motion": "still_center",    "desc": "pure consciousness"},
    "śakti":      {"color": CRIMSON,"form": "wave_spiral", "motion": "undulating",     "desc": "dynamic energy"},
    "bhairava":   {"color": DARK,   "form": "triangle",   "motion": "contract_expand","desc": "terrifying aspect"},
    "kālī":       {"color": BLACK,  "form": "burst",      "motion": "consuming",      "desc": "time devouring"},
    "sarasvatī":  {"color": INK,    "form": "lotus",      "motion": "flowing",        "desc": "wisdom, speech"},
    "natarāja":   {"color": GOLD,   "form": "circle_crown","motion": "dancing",       "desc": "cosmic dancer"},
    "dakṣiṇāmūrti":{"color": GOLD,  "form": "seated",     "motion": "still",          "desc": "silent guru"},
    "tripurasundarī":{"color": CRIMSON,"form": "sri_yantra","motion": "radiating",    "desc": "beauty of three worlds"},
}

def draw_deity(d, cx, cy, deity_id, t, progress, size=1.0):
    """Draw a deity as pure geometry + motion. No literal image."""
    info = DEITIES.get(deity_id, DEITIES["śiva"])
    color = info["color"]
    form = info["form"]
    p = clamp(progress)

    if form == "circle":
        r = 60 * size * (1 + 0.03*math.sin(t*0.5))
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=3)
        d.ellipse((cx-6, cy-6, cx+6, cy+6), fill=color)

    elif form == "wave_spiral":
        for i in range(20):
            a = t*0.3 + i*0.314
            r = 20 + i * 6 * size + 5*math.sin(t*0.7 + i*0.5)
            x = cx + r*math.cos(a)
            y = cy + r*math.sin(a)
            sz = 2 + 2*math.sin(t + i*0.3)
            d.ellipse((x-sz, y-sz, x+sz, y+sz), fill=color)

    elif form == "triangle":
        rot = t*0.2
        pts = []
        for i in range(3):
            a = rot + i*2.094
            r = 70*size
            pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        d.line(pts[0:2], fill=color, width=3)
        d.line(pts[1:3], fill=color, width=3)
        d.line(pts[2:4] if len(pts)>3 else [pts[2],pts[0]], fill=color, width=3)

    elif form == "burst":
        for i in range(24):
            a = t*0.4 + i*0.262
            r = 30 + 50*size*abs(math.sin(t*0.5 + i*0.3))
            x = cx + r*math.cos(a)
            y = cy + r*math.sin(a)
            d.line((cx, cy, x, y), fill=color, width=1)

    elif form == "lotus":
        for i in range(12):
            a = t*0.1 + i*0.524
            r = 50*size + 20*size*abs(math.sin(t*0.3 + i))
            x = cx + r*math.cos(a)
            y = cy + r*math.sin(a)
            d.ellipse((x-8, y-15, x+8, y+15), fill=None, outline=color, width=2)

    elif form == "circle_crown":
        d.ellipse((cx-50*size, cy-50*size, cx+50*size, cy+50*size), outline=color, width=2)
        for i in range(16):
            a = t*0.5 + i*0.393
            r = 55*size + 15*size*abs(math.sin(t*0.7 + i))
            x = cx + r*math.cos(a)
            y = cy + r*math.sin(a)
            d.ellipse((x-3, y-3, x+3, y+3), fill=color)

    elif form == "sri_yantra":
        for ring in range(4):
            r = (30 + ring*20)*size
            d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=1)
        for i in range(9):
            a = t*0.05 + i*0.698
            x = cx + 80*size*math.cos(a)
            y = cy + 80*size*math.sin(a)
            d.line((cx, cy, x, y), fill=color, width=1)


# ═══════════════════════════════════════════════════════════════════
# QUOTE PAGE TEMPLATE — L-system borders + centered quote
# ═══════════════════════════════════════════════════════════════════

def draw_lsystem_border(d, x, y, width, height, side, progress, color=CHARCOAL):
    """Draw a decorative L-system plant on one side of the page."""
    # Simple vine: F[+F]F[-F]F pattern along the side
    step = 12
    cx = x if side == 'left' else x + width
    cy = y + height

    angle = -math.pi/2
    stack = []
    cur_x, cur_y = cx, cy
    total = int(30 * clamp(progress))
    for i in range(total):
        if i % 3 == 0:
            nx = cur_x + (0 if side=='left' else 0) + step * math.cos(angle + 0.3)
            ny = cur_y + step * math.sin(angle + 0.3)
        elif i % 3 == 1:
            nx = cur_x + step * math.cos(angle + 0.8)
            ny = cur_y + step * math.sin(angle - 0.2)
        else:
            nx = cur_x + step * math.cos(angle - 0.5)
            ny = cur_y + step * math.sin(angle + 0.4)
        d.line((cur_x, cur_y, nx, ny), fill=color, width=1)
        cur_x, cur_y = nx, ny

def quote_page(quote, author, source="", t=0, theme="dark"):
    """Generate a quote page with decorative L-system borders."""
    bg = DARK if theme == "dark" else WHITE
    text_color = INK if theme == "dark" else BLACK
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)

    # L-system borders on left and right
    border_progress = clamp(t / 2)
    draw_lsystem_border(d, 30, 30, 40, H-60, 'left', border_progress, GOLD)
    draw_lsystem_border(d, W-70, 30, 40, H-60, 'right', border_progress, GOLD)

    # Quote text (centered)
    a = clamp((t - 0.5) / 2)
    if a > 0:
        # Quote mark
        d.text((W//2-20, 140), '"', fill=GOLD, font=ImageFont.load_default())
        # Quote body — wrap
        words = quote.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + " " + w) < 55:
                cur += " " + w if cur else w
            else: lines.append(cur); cur = w
        if cur: lines.append(cur)

        y_start = 220
        for i, line in enumerate(lines):
            d.text((W//2 - 200, y_start + i*38), line, fill=text_color, font=ImageFont.load_default())

        # Author
        y_author = y_start + len(lines)*38 + 40
        d.text((W//2 - 200, y_author), f"— {author}", fill=MUTED, font=ImageFont.load_default())

        # Source
        if source:
            d.text((W//2 - 200, y_author + 30), source, fill=MUTED, font=ImageFont.load_default())

    return im


# ═══════════════════════════════════════════════════════════════════
# SCENE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def scene_shiva_consciousness(t, u, idx):
    """Śiva as pure consciousness — still center, gold circle, radiating field."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Radiating field
    for i in range(8):
        r = 30 + i*35 + 10*math.sin(t*0.3 + i)
        a = 0.15 - i*0.015
        if a > 0:
            d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(GOLD[0], GOLD[1], GOLD[2], int(255*a)), width=1)

    # Śiva as still gold circle
    draw_deity(d, cx, cy, "śiva", t, 1, 1.2)
    d.text((cx-30, 60), "शिव", fill=GOLD, font=ImageFont.load_default())
    d.text((cx-60, H-60), "pure consciousness", fill=MUTED, font=ImageFont.load_default())
    return im

def scene_shakti_energy(t, u, idx):
    """Śakti as dynamic crimson wave-spiral — undulating energy."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    for i in range(30):
        a = (i*0.4) + t*0.5
        r = 10 + i*5
        x = cx + r*math.cos(a + t*0.3)
        y = cy + r*math.sin(a + t*0.5)
        sz = 2 + 2*math.sin(t + i*0.3)
        d.ellipse((x-sz, y-sz, x+sz, y+sz), fill=CRIMSON)

    d.text((cx-30, 60), "शक्ति", fill=CRIMSON, font=ImageFont.load_default())
    return im

def scene_nataraja_dance(t, u, idx):
    """Natarāja as cosmic dance — rotating geometry."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    draw_deity(d, cx, cy, "natarāja", t, 1, 1.5)

    # Orbiting energy rings
    for i in range(12):
        a = t*0.5 + i*0.524
        r = 90 + 20*math.sin(t*0.4 + i)
        x = cx + r*math.cos(a)
        y = cy + r*math.sin(a)
        d.ellipse((x-4, y-4, x+4, y+4), fill=GOLD)

    d.text((cx-50, 60), "नटराज", fill=GOLD, font=ImageFont.load_default())
    d.text((cx-90, H-60), "cosic dancer — play of consciousness", fill=MUTED, font=ImageFont.load_default())
    return im

def scene_kali_time(t, u, idx):
    """Kālī as time devouring — dark burst, consuming geometry."""
    im = Image.new("RGB", (W, H), (5, 5, 8))
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Consuming dark burst
    for i in range(36):
        a = t*0.5 + i*0.175
        r = 20 + 60*abs(math.sin(t*0.4 + i*0.2))
        x = cx + r*math.cos(a)
        y = cy + r*math.sin(a)
        d.line((cx, cy, x, y), fill=(180, 40, 40, 100), width=1)

    # Inner dark center
    r = 20 + 5*math.sin(t*0.7)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(80, 20, 20))

    d.text((cx-30, 60), "काली", fill=MUTED, font=ImageFont.load_default())
    return im

def scene_abhinavagupta(t, u, idx):
    """Abhinavagupta concept: consciousness unfolding through all systems."""
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Central light
    draw_deity(d, cx, cy, "śiva", t, 1, 1.0)

    # Radiating knowledge — concentric text rings
    texts = ["तन्त्रालोक", "प्रत्यभिज्ञा", "स्पन्द", "मालिनी", "तन्त्र"]
    for i, txt in enumerate(texts):
        a = t*0.1 + i*1.257
        r = 100 + i*25 + 10*math.sin(t*0.3 + i)
        x = cx + r*math.cos(a)
        y = cy + r*math.sin(a)
        d.text((x-30, y-10), txt, fill=GOLD if i%2==0 else INK, font=ImageFont.load_default())

    d.text((cx-80, 60), "अभिनवगुप्त", fill=GOLD, font=ImageFont.load_default())
    d.text((cx-120, H-60), "consciousness articulating through all systems", fill=MUTED, font=ImageFont.load_default())
    return im

def scene_quote_theurgy(t, u, idx):
    """Quote page: Iamblichus on theurgy."""
    return quote_page(
        "The gods need human rituals as much as humans need divine grace.",
        "Iamblichus", "De Mysteriis", t, "dark"
    )

def scene_quote_recognition(t, u, idx):
    """Quote page: recognition."""
    return quote_page(
        "Liberation is not the acquisition of something new. It is the removal of misrecognition.",
        "Utpaladeva", "Īśvara-pratyabhijñā-kārikā", t, "dark"
    )


# ── Registry ───────────────────────────────────────────────────────
CONCEPT_SCENES = [
    ("śiva_consciousness", scene_shiva_consciousness, 12, "Śiva as pure consciousness — gold circle, radiating field"),
    ("śakti_energy", scene_shakti_energy, 12, "Śakti as dynamic crimson wave-spiral"),
    ("natarāja_dance", scene_nataraja_dance, 12, "Natarāja as cosmic dance"),
    ("kālī_time", scene_kali_time, 10, "Kālī as time devouring"),
    ("abhinavagupta", scene_abhinavagupta, 14, "Abhinavagupta: consciousness unfolding"),
    ("quote_theurgy", scene_quote_theurgy, 10, "Quote: Iamblichus on theurgy"),
    ("quote_recognition", scene_quote_recognition, 10, "Quote: Utpaladeva on recognition"),
]
