#!/usr/bin/env python3
"""
Light That Knows Itself — self-contained render.
No infrastructure. No Worker. Just PIL + ffmpeg.
Essay: light is self-showing, consciousness is its own illumination.
"""
import math, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 1280, 720
FPS = 4
SHOT_S = 5.0
FRAMES = int(FPS * SHOT_S)

# ── Palette (cold light on deep ground) ──
VOID    = (10, 12, 18)
DEEPER  = (16, 20, 30)
FLINT   = (45, 52, 65)
MIST    = (140, 150, 170)
SILVER  = (190, 198, 212)
WARM    = (232, 215, 185)
GOLD    = (212, 175, 110)
FLARE   = (255, 235, 190)
PARCH   = (238, 233, 220)
INK     = (30, 30, 35)

def canvas(bg=VOID): return Image.new("RGB", (W, H), bg)
def lerp(a,b,t): return a + (b-a)*t
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))

def scene_emergence(ctx, t, u):
    """Light emerges from nothing. One point becomes a field."""
    im = canvas(VOID)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # Phase 1: faint point in absolute dark
    if u < 0.33:
        pr = 4 + 12 * (u / 0.33)
        d.ellipse([cx-pr, cy-pr, cx+pr, cy+pr], fill=FLARE)
        for i in range(3):
            r = pr * (2 + i * 1.5)
            a = int(30 - i * 8)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(FLARE[0], FLARE[1], FLARE[2], a), width=1)

    # Phase 2: light expands, warm halo forms
    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        r = 30 + 120 * prog
        for i in range(6):
            ri = r + i * 18
            alpha = int(70 - i * 10)
            col = mix(GOLD, FLARE, i/6)
            d.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], outline=(col[0], col[1], col[2], alpha), width=2)
        d.ellipse([cx-25, cy-25, cx+25, cy+25], fill=FLARE)

    # Phase 3: resolved — light fills the frame
    else:
        prog = (u - 0.66) / 0.34
        d.ellipse([0, 0, W, H], fill=mix(VOID, WARM, prog * 0.15))
        d.ellipse([cx-40, cy-40, cx+40, cy+40], fill=FLARE)
        for i in range(8):
            a = i * math.pi/4
            x = cx + math.cos(a) * 180
            y = cy + math.sin(a) * 180
            d.line([(cx+25*math.cos(a), cy+25*math.sin(a)), (x, y)],
                   fill=GOLD, width=2)

    return im


def scene_mirror(ctx, t, u):
    """A mirror pool reflects. The reflection knows itself as reflection."""
    im = canvas(PARCH)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # horizon
    d.line([(80, cy), (W-80, cy)], fill=INK, width=2)

    # upper: sky field
    sky = Image.new("RGB", (W-160, cy-80), mix(PARCH, WARM, 0.3))
    im.paste(sky, (80, 80))

    # lower: pool
    pool = Image.new("RGB", (W-160, H-cy-80), mix(PARCH, SILVER, 0.2))
    im.paste(pool, (80, cy+2))

    if u < 0.33:
        r = 20 + 15 * (u / 0.33)
        d.ellipse([cx-r, cy+40-r, cx+r, cy+40+r], outline=SILVER, width=2)

    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        r = 35 + 45 * prog
        d.ellipse([cx-r, cy+40-r, cx+r, cy+40+r], outline=GOLD, width=3)
        d.ellipse([cx-5, cy+40-5, cx+5, cy+40+5], fill=FLARE)

    else:
        r = 80
        d.ellipse([cx-r, cy+40-r, cx+r, cy+40+r], outline=GOLD, width=4)
        d.ellipse([cx-8, cy+40-8, cx+8, cy+40+8], fill=FLARE)
        # reflection line
        d.line([(cx-r, cy+40), (cx+r, cy+40)], fill=FLARE, width=2)

    return im


def scene_seam(ctx, t, u):
    """A gold seam fractures through stone. Light finds its path."""
    im = canvas(mix(VOID, FLINT, 0.3))
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # stone mass
    d.ellipse([cx-220, cy-130, cx+220, cy+130], fill=FLINT)
    d.ellipse([cx-200, cy-110, cx+200, cy+110], fill=mix(FLINT, VOID, 0.2))

    if u < 0.33:
        pts = [(cx-190, cy-15)]
        for i in range(1, 8):
            x = cx - 190 + i * 52
            y = cy + 20 * math.sin(x * 0.04)
            pts.append((x, y))
        for i in range(len(pts)-1):
            d.line([pts[i], pts[i+1]], fill=GOLD, width=2)

    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        pts = [(cx-190, cy-20)]
        n = int(6 + 6 * prog)
        for i in range(1, n):
            x = cx - 190 + i * (380 / max(1, n-1))
            y = cy + 35 * math.sin(x * 0.03 + prog * 3)
            pts.append((x, y))
        for i in range(len(pts)-1):
            w = 2 + int(prog * 4)
            d.line([pts[i], pts[i+1]], fill=mix(GOLD, FLARE, prog), width=w)

    else:
        prog = (u - 0.66) / 0.34
        pts = [(cx-190, cy-25)]
        n = 14
        for i in range(1, n):
            x = cx - 190 + i * 30
            y = cy + 40 * math.sin(x * 0.035 + 2.5)
            pts.append((x, y))
        for i in range(len(pts)-1):
            d.line([pts[i], pts[i+1]], fill=FLARE, width=5)
        # glow spread
        for i in range(3):
            r = 100 + i * 30
            d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(GOLD[0], GOLD[1], GOLD[2], 40-i*10), width=1)

    return im


def scene_thread(ctx, t, u):
    """A thread connects two forms. The connection is the relation."""
    im = canvas(mix(VOID, DEEPER, 0.5))
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    # left form
    d.ellipse([180, cy-70, 320, cy+70], outline=SILVER, width=3)
    d.ellipse([200, cy-50, 300, cy+50], outline=mix(SILVER, VOID, 0.3), width=1)

    # right form
    d.ellipse([960, cy-70, 1100, cy+70], outline=GOLD, width=3)
    d.ellipse([980, cy-50, 1080, cy+50], outline=mix(GOLD, VOID, 0.3), width=1)

    if u < 0.33:
        d.ellipse([cx-4, cy-4, cx+4, cy+4], fill=SILVER)

    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        pts = []
        for i in range(15):
            x = 300 + i * 45
            y = cy + 50 * math.sin(x * 0.02 + prog * 4)
            pts.append((x, y))
        for i in range(len(pts)-1):
            d.line([pts[i], pts[i+1]], fill=mix(SILVER, GOLD, prog), width=2)

    else:
        prog = (u - 0.66) / 0.34
        pts = []
        for i in range(25):
            x = 300 + i * 27
            y = cy + 60 * math.sin(x * 0.025 + 3.5)
            pts.append((x, y))
        for i in range(len(pts)-1):
            w = 2 + int(prog * 4)
            d.line([pts[i], pts[i+1]], fill=GOLD, width=w)

    return im


def scene_fold(ctx, t, u):
    """Space folds. Inside and outside become one."""
    im = canvas(VOID)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    if u < 0.33:
        d.arc([cx-180, cy-100, cx+180, cy+100], 0, 180, fill=SILVER, width=3)
        d.arc([cx-180, cy-100, cx+180, cy+100], 180, 360, fill=SILVER, width=3)

    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        spread = 180 - 80 * prog
        d.arc([cx-spread, cy-80, cx+spread, cy+80], 0, 180, fill=mix(SILVER, GOLD, prog), width=3)
        d.arc([cx-spread, cy-80, cx+spread, cy+80], 180, 360, fill=mix(SILVER, GOLD, prog), width=3)
        d.ellipse([cx-15, cy-15, cx+15, cy+15], fill=FLARE)

    else:
        prog = (u - 0.66) / 0.34
        r = 60 + 40 * prog
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=GOLD, width=3)
        d.ellipse([cx-60, cy-60, cx+60, cy+60], outline=mix(GOLD, FLARE, 0.5), width=2)
        d.ellipse([cx-20, cy-20, cx+20, cy+20], fill=FLARE)
        # inner lines
        for i in range(6):
            a = i * math.pi/3
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r
            d.line([(cx, cy), (x, y)], fill=GOLD, width=1)

    return im


def scene_completion(ctx, t, u):
    """The circle closes. Light recognizes itself as the seeing."""
    im = canvas(VOID)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2

    if u < 0.33:
        angle = 360 * (u / 0.33)
        d.arc([cx-180, cy-180, cx+180, cy+180], 0, angle, fill=SILVER, width=3)
        d.ellipse([cx-6, cy-6, cx+6, cy+6], fill=SILVER)

    elif u < 0.66:
        prog = (u - 0.33) / 0.33
        angle = 360 + 360 * prog
        d.arc([cx-200, cy-200, cx+200, cy+200], 0, angle, fill=GOLD, width=4)
        d.ellipse([cx-40, cy-40, cx+40, cy+40], outline=GOLD, width=2)
        d.ellipse([cx-10, cy-10, cx+10, cy+10], fill=FLARE)
        for i in range(4):
            a = i * math.pi/2 + t * 0.5
            x = cx + math.cos(a) * 130
            y = cy + math.sin(a) * 130
            d.line([(cx, cy), (x, y)], fill=FLARE, width=1)

    else:
        prog = (u - 0.66) / 0.34
        d.ellipse([cx-220, cy-220, cx+220, cy+220], outline=GOLD, width=5)
        for i in range(12):
            a = i * math.pi/6 + t * 0.3
            r = 180 + 30 * math.sin(t * 2 + i)
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r
            d.ellipse([x-4, y-4, x+4, y+4], fill=FLARE)
        d.ellipse([cx-50, cy-50, cx+50, cy+50], outline=GOLD, width=2)
        d.ellipse([cx-15, cy-15, cx+15, cy+15], fill=FLARE)

    return im


SCENES = [
    ("Light Emerges", scene_emergence),
    ("Mirror Pool", scene_mirror),
    ("Gold Seam", scene_seam),
    ("Thread", scene_thread),
    ("Fold", scene_fold),
    ("Completion", scene_completion),
]

# ── Render Loop ──
OUT = Path("/tmp/light-video")
OUT.mkdir(parents=True, exist_ok=True)

for idx, (name, fn) in enumerate(SCENES):
    sid = f"s{idx+1:03d}"
    shot_dir = OUT / sid
    shot_dir.mkdir(exist_ok=True)

    for fi in range(FRAMES):
        t = fi / FPS
        u = fi / max(1, FRAMES - 1)
        im = fn(None, t, u)
        im.save(str(shot_dir / f"frame_{fi:04d}.png"))

    mp4 = OUT / f"{sid}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i",
        f"{shot_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "fast", "-crf", "22",
        str(mp4)
    ], capture_output=True)
    print(f"{sid}: {name}")

# Concat
with open(OUT / "concat.txt", "w") as f:
    for idx in range(len(SCENES)):
        f.write(f"file '{OUT / f's{idx+1:03d}.mp4'}'\n")

final = OUT / "final.mp4"
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(OUT / "concat.txt"), "-c", "copy", str(final)
], capture_output=True)

print(f"\nDone: {final}")
print(f"Size: {final.stat().st_size // 1024}KB")
