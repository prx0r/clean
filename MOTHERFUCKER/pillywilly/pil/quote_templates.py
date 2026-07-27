"""Quote templates — one L-system species per side, quote centered."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720
DARK = (12, 12, 15); WHITE = (248, 246, 240); GOLD = (208, 172, 91)
INK = (235, 231, 220); MUTED = (145, 141, 132); CHARCOAL = (40, 40, 40)

# L-system species for borders — kept small and contained
SPECIES = [
    ("weed", "F", {"F": "F[+F][-F]F"}, 25, 4),
    ("tree", "F", {"F": "F[+F]F[-F]F"}, 30, 4),
    ("fern", "X", {"X": "F[+X][-X]FX", "F": "FF"}, 25, 4),
    ("thistle", "X", {"X": "F[+X][-X]F", "F": "FF"}, 30, 4),
    ("grass", "F", {"F": "[+F][-F]"}, 45, 3),
    ("bush", "F", {"F": "F[+F]F[-F]F[+F]F"}, 22, 4),
]

def generate(axiom, rules, angle_rad, iters):
    s = axiom
    for _ in range(iters):
        s = ''.join(rules.get(c,c) for c in s)
    return s

def draw_side(d, instr, x, y, flip_x=False):
    """Draw L-system on one side. flip_x mirrors for right side."""
    step = 5
    angle = math.radians(25)
    stack = []
    cx, cy = x, y
    ca = -math.pi/2
    for c in instr:
        if c == 'F':
            nx = cx + step * math.cos(ca)
            ny = cy + step * math.sin(ca)
            # Mirror if right side
            if flip_x:
                nx = x - (nx - x)
            nx = max(5, min(W-5, nx))
            ny = max(5, min(H-5, ny))
            d.line((cx, cy, nx, ny), fill=CHARCOAL, width=1)
            cx, cy = nx, ny
        elif c == '+': ca += angle
        elif c == '-': ca -= angle
        elif c == '[': stack.append((cx, cy, ca))
        elif c == ']' and stack: cx, cy, ca = stack.pop()

def make_species_scene(species_idx):
    """Create a scene function for one L-system species pair."""
    name, axiom, rules, angle_deg, iters = SPECIES[species_idx]
    angle_rad = math.radians(angle_deg)
    full = generate(axiom, rules, angle_rad, iters)

    QUOTE = [
        "Spanda is the hidden pulse that controls everything you experience.",
        "The centre is the Heart, the pulsing core of consciousness.",
        "All Mantras are the dynamic pulsing nature of consciousness.",
        "When you know yourself as the pulse, desire becomes creative power.",
        "The universe pulses — pulsing is what joy does when it moves.",
        "The sixth bliss is complete expansion.",
        "Wave upon wave of universal pulsation arises from the ocean of the Heart.",
        "The breath is time itself — condensed into rhythm.",
        "Play — krida — is vibration seeking out joy.",
        "The hidden pulse — the substrate of every thought you have ever thought.",
    ][species_idx]

    def scene(t, u, idx):
        im = Image.new("RGB", (W, H), DARK)
        d = ImageDraw.Draw(im)
        progress = min(1, t / 3)

        # Draw L-systems on both sides
        n = int(len(full) * progress)
        left_part = full[:n]
        right_part = full[:n]

        draw_side(d, left_part, 60, H-60, flip_x=False)
        draw_side(d, right_part, W-60, H-60, flip_x=True)

        # Quote text
        if progress > 0.2:
            a = min(1, (progress - 0.2) / 0.4)
            words = QUOTE.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) < 55:
                    cur += " " + w if cur else w
                else:
                    lines.append(cur); cur = w
            if cur: lines.append(cur)

            y = 260
            for line in lines:
                # Center each line
                lw = len(line) * 12  # approximate pixel width
                x = (W - lw) // 2
                d.text((x, y), line, fill=INK)
                y += 38

        # Species label bottom
        if progress > 0.6:
            d.text((W//2-40, H-30), name, fill=MUTED)

        return im
    return scene, f"quote_{name}"

# Build all scene functions
QUOTE_SCENES = []
for i in range(len(SPECIES)):
    fn, name = make_species_scene(i)
    QUOTE_SCENES.append((name, fn, 10, f"Quote with {SPECIES[i][0]} borders"))
