#!/usr/bin/env python3
"""
The Light That Illuminates Itself — Suhrawardi's illuminationist philosophy.
Self-contained render. No infrastructure. Just PIL + ffmpeg + numpy.
"""
import math, subprocess, json, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FPS = 6
SHOT_S = 6.0
FRAMES = int(FPS * SHOT_S)

# ── Suhrawardi palette ──
NIGHT    = (10, 12, 20)
DEPTH    = (18, 22, 35)
SAPPHIRE = (30, 42, 75)
AZURE    = (50, 68, 120)
EMERALD  = (42, 95, 72)
GOLD     = (205, 162, 79)
AMBER    = (224, 172, 62)
FLARE    = (252, 232, 180)
SILVER   = (185, 195, 210)
MIST     = (200, 208, 220)
PEARL    = (235, 230, 218)
EARTH    = (160, 140, 115)
EMBER    = (180, 85, 45)
ROSE     = (195, 100, 120)
WHITE    = (248, 245, 238)
INK      = (25, 26, 30)

def canvas(bg=NIGHT): return Image.new("RGB", (W, H), bg)
def layer(): return Image.new("RGBA", (W, H), (0,0,0,0))
def lerp(a,b,t): return a + (b-a)*t
def clamp(v, lo=0, hi=1): return max(lo, min(hi, v))
def mix(a,b,t): return tuple(int(lerp(x,y,clamp(t))) for x,y in zip(a,b))
def rgba(c,a=255): return (*c[:3], int(a))
def ease(t): return t*t*(3-2*t)

def causal_ground(seed):
    rng = np.random.default_rng(seed)
    base = np.zeros((H,W,3), dtype=np.float32)
    base[:] = np.array(NIGHT, dtype=np.float32)
    coarse = rng.normal(0, 1, (45, 80)).astype(np.float32)
    cimg = Image.fromarray(np.uint8(np.clip((coarse-coarse.min())/(np.ptp(coarse)+1e-6)*255, 0, 255)))
    cimg = cimg.resize((W, H), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(18))
    carr = (np.asarray(cimg).astype(np.float32)-128)/128
    base += carr[...,None]*4.0 + rng.normal(0,1,(H,W))[...,None]*1.0
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx-W/2)/(W/2); dy = (yy-H/2)/(H/2)
    base -= np.clip((dx*dx+dy*dy)*18, 0, 27)[...,None]
    # central glow
    band = np.exp(-((yy-H*0.42)/(H*0.18))**2) * np.exp(-((xx-W/2)/(W*0.40))**2)
    base[...,0] += band*10; base[...,1] += band*14; base[...,2] += band*28
    return Image.fromarray(np.uint8(np.clip(base, 0, 255)), 'RGB').convert('RGBA')

def glow(im, xy, r, col, alpha=150, blur=18):
    gl = layer(); d = ImageDraw.Draw(gl)
    x, y = xy
    d.ellipse((x-r, y-r, x+r, y+r), fill=rgba(col, alpha))
    gl = gl.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(gl)

def line_glow(im, pts, col, width=3, alpha=150, blur=8):
    gl = layer(); d = ImageDraw.Draw(gl)
    d.line(pts, fill=rgba(col, alpha), width=max(1,width*3), joint='curve')
    gl = gl.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(gl)
    ImageDraw.Draw(im).line(pts, fill=rgba(col, min(255,alpha+50)), width=width, joint='curve')

def rosette(d, cx, cy, r, outer, inner):
    for i in range(8):
        a = 2*math.pi*i/8
        x = cx+math.cos(a)*r*.62; y = cy+math.sin(a)*r*.62
        d.ellipse((x-r*.42, y-r*.42, x+r*.42, y+r*.42), fill=rgba(outer,130), outline=rgba(inner,160), width=1)
    d.ellipse((cx-r*.42, cy-r*.42, cx+r*.42, cy+r*.42), fill=rgba(inner,110), outline=rgba(outer,200), width=2)

def border(im):
    d = ImageDraw.Draw(im)
    d.rectangle((28,28,W-28,H-28), outline=rgba(SILVER,90), width=2)
    d.rectangle((42,42,W-42,H-42), outline=rgba(GOLD,70), width=1)
    for x,y in [(70,70),(W-70,70),(70,H-70),(W-70,H-70)]:
        rosette(d,x,y,22,AZURE,GOLD)

def dust(im, seed, n=60):
    rng = np.random.default_rng(seed); ov = layer(); d = ImageDraw.Draw(ov)
    for _ in range(n):
        x = float(rng.uniform(115,W-115)); y = float(rng.uniform(100,H-180)); r = float(rng.uniform(.8,2.1))
        c = mix(SILVER, FLARE, rng.uniform(0,1))
        d.ellipse((x-r,y-r,x+r,y+r), fill=rgba(c, int(rng.uniform(15,65))))
    im.alpha_composite(ov)

def bezier(p0,p1,p2,p3,n=80):
    pts = []
    for i in range(n):
        t = i/(n-1); u = 1-t
        x = u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0]
        y = u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]
        pts.append((x,y))
    return pts

def partial(pts, amount):
    amount = clamp(amount)
    if amount <= 0: return []
    if amount >= 1: return pts
    f = amount*(len(pts)-1); idx = int(f); frac = f-idx
    out = list(pts[:idx+1])
    if idx+1 < len(pts):
        a,b = pts[idx], pts[idx+1]
        out.append((lerp(a[0],b[0],frac), lerp(a[1],b[1],frac)))
    return out

def draw_node(d, x, y, r, col, alpha=45):
    d.ellipse((x-r,y-r,x+r,y+r), outline=rgba(col,200), fill=rgba(col,alpha), width=2)

def arrow(d, p0, p1, col, scale=1.0):
    ang = math.atan2(p1[1]-p0[1], p1[0]-p0[0]); s = 14*scale
    pts = [p1, (p1[0]-math.cos(ang-.5)*s, p1[1]-math.sin(ang-.5)*s),
           (p1[0]-math.cos(ang+.5)*s, p1[1]-math.sin(ang+.5)*s)]
    d.polygon(pts, fill=rgba(col,220))

# ── Scene functions ──

def sc01(im, t):
    """Opening: light visible by itself — a single point that needs nothing else."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    if t < 0.25:
        pr = 3 + 20 * (t/0.25)
        d.ellipse([cx-pr, cy-pr, cx+pr, cy+pr], fill=FLARE)
    elif t < 0.55:
        p = (t-0.25)/0.3
        r = 23 + 80*p
        for i in range(5):
            ri = r + i*15
            col = mix(GOLD, FLARE, i/5)
            d.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], outline=rgba(col, 80-i*12), width=2)
        d.ellipse([cx-18, cy-18, cx+18, cy+18], fill=FLARE)
    else:
        p = (t-0.55)/0.45
        d.ellipse([0,0,W,H], fill=mix(NIGHT, (20,25,45), p*0.2))
        d.ellipse([cx-180, cy-180, cx+180, cy+180], outline=rgba(GOLD, 60), width=1)
        d.ellipse([cx-22, cy-22, cx+22, cy+22], fill=FLARE)
    d.text((cx, H-80), "light is visible by itself", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18), fill=SILVER, anchor="mm")

def sc02(im, t):
    """Mundus imaginalis — the world between worlds appears as a floating emerald city."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2-40
    if t < 0.3:
        p = t/0.3
        glow(im, (cx,cy), 60*p, EMERALD, 80, 20)
    elif t < 0.6:
        p = (t-0.3)/0.3
        for i in range(4):
            x = cx + (i-1.5)*200
            y = cy - 80 + abs(i-1.5)*60
            r = 40 + 30*p
            d.ellipse([x-r, y-r, x+r, y+r], outline=rgba(EMERALD, 120+40*p), width=2)
            d.ellipse([x-r+10, y-r+10, x+r-10, y+r-10], outline=rgba(AMBER, 60), width=1)
        glow(im, (cx, cy), 50, EMERALD, 100, 16)
    else:
        p = (t-0.6)/0.4
        for i in range(4):
            x = cx + (i-1.5)*200
            y = cy - 80 + abs(i-1.5)*60
            r = 70
            d.ellipse([x-r, y-r, x+r, y+r], outline=rgba(EMERALD, 180), fill=rgba(EMERALD, 25), width=2)
        glow(im, (cx, cy), 60, AMBER, 120, 18)
        d.ellipse([cx-12, cy-12, cx+12, cy+12], fill=FLARE)
    d.text((cx, H-80), "the world between worlds", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18), fill=EMERALD, anchor="mm")

def sc03(im, t):
    """Na-koja-abad — the land that is nowhere, the cosmic north within."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    for i in range(7):
        r = 40 + i*45
        alpha = 120 - i*14
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rgba(AZURE, max(20,alpha)), width=1)
    # compass rose
    if t > 0.2:
        p = clamp((t-0.2)/0.6)
        for angle, col in [(0, GOLD), (math.pi/2, EMERALD), (math.pi, AMBER), (3*math.pi/2, SILVER)]:
            x = cx + math.cos(angle)*160*p; y = cy + math.sin(angle)*160*p
            d.line([(cx,cy), (x,y)], fill=rgba(col, 150), width=2)
    glow(im, (cx,cy), 40, GOLD, 100, 14)
    d.ellipse([cx-10, cy-10, cx+10, cy+10], fill=FLARE)
    d.text((cx, H-80), "na-koja-abad — the land that is nowhere", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=GOLD, anchor="mm")

def sc04(im, t):
    """Perfect Nature — the Guide of Light, celestial counterpart."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # lower figure (seeker)
    y_low = cy + 100
    d.ellipse([cx-50, y_low-70, cx+50, y_low+10], outline=rgba(SILVER, 150), width=2)
    d.ellipse([cx-18, y_low-60, cx+18, y_low-28], outline=rgba(SILVER, 150), width=2)
    # upper figure (Guide)
    if t > 0.15:
        p = clamp((t-0.15)/0.5)
        y_up = cy - 120
        glow(im, (cx, y_up), 50, GOLD, 100*p, 16)
        d.ellipse([cx-45, y_up-65, cx+45, y_up+5], outline=rgba(GOLD, 180*p), width=3)
        d.ellipse([cx-15, y_up-55, cx+15, y_up-23], fill=rgba(FLARE, 200*p))
        # connection
        pts = bezier((cx, y_low-70), (cx+50, cy-40), (cx-50, cy-80), (cx, y_up+65))
        conn = partial(pts, p)
        if len(conn) > 1:
            line_glow(im, conn, GOLD, 2, 80, 6)
    d.text((cx, H-80), "thy perfect nature — the guide who was never absent", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=GOLD, anchor="mm")

def sc05(im, t):
    """Midnight sun — illumination at the darkest point."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2+30
    # dark night
    for i in range(20):
        a = i*2*math.pi/20
        r = 180 + 30*math.sin(i*1.5)
        x = cx+math.cos(a)*r; y = cy+math.sin(a)*r
        d.ellipse([x-2,y-2,x+2,y+2], fill=rgba(AZURE, 30))
    # midnight sun emerging
    if t > 0.2:
        p = clamp((t-0.2)/0.6)
        r = 30 + 110*p
        glow(im, (cx, cy-30), r, FLARE, int(60*p), 14)
        for i in range(8):
            a = i*math.pi/4 + t*0.3
            x = cx+math.cos(a)*r*1.3; y = cy-30+math.sin(a)*r*1.3
            d.line([(cx, cy-30), (x, y)], fill=rgba(GOLD, int(100*p)), width=2)
        d.ellipse([cx-15, cy-45, cx+15, cy-15], fill=FLARE)
    # Hermes keeping vigil
    d.ellipse([cx-65, cy+40, cx+65, cy+120], outline=rgba(SILVER, 100), width=2)
    d.ellipse([cx-20, cy+50, cx+20, cy+78], outline=rgba(SILVER, 100), width=2)
    d.text((cx, H-80), "at midnight the sun shines — media nocte vidi solem coruscantem", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 15), fill=FLARE, anchor="mm")

def sc06(im, t):
    """The eighth keshvar — Hurqalya, emerald cities on the cosmic mountain."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # mountain
    pts = [(cx-280, cy+130), (cx-120, cy-80), (cx, cy-140), (cx+120, cy-80), (cx+280, cy+130)]
    d.polygon(pts, outline=rgba(EMERALD, 120), fill=rgba(EMERALD, 15))
    # city on summit
    if t > 0.1:
        p = clamp((t-0.1)/0.5)
        for i in range(5):
            x = cx-60 + i*30
            y = cy-140 - 30*abs(i-2)/2
            h = 25 + 10*abs(i-2)
            d.rectangle([x-6, y-h, x+6, y], fill=rgba(EMERALD, 100*p))
            d.rectangle([x-4, y-h+8, x+4, y-h+8], fill=rgba(AMBER, 80*p))
    glow(im, (cx, cy-140), 40, EMERALD, 80, 12)
    d.text((cx, H-80), "the emerald rock — hurqalya on the mountain of qaf", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=EMERALD, anchor="mm")

def sc07(im, t):
    """Fravarti — heavenly twin, syzygy of light."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # two figures facing
    for side, col in [(-1, SILVER), (1, GOLD)]:
        x = cx + side*140
        d.ellipse([x-55, cy-80, x+55, cy+15], outline=rgba(col, 170), width=2)
        d.ellipse([x-20, cy-68, x+20, cy-35], outline=rgba(col, 180), width=2)
    # light between them
    if t > 0.1:
        p = clamp((t-0.1)/0.5)
        glow(im, (cx, cy-30), 60, FLARE, int(70*p), 16)
        pts = bezier((cx-85, cy-55), (cx-40, cy-90), (cx+40, cy-90), (cx+85, cy-55))
        conn = partial(pts, p)
        if len(conn) > 1: line_glow(im, conn, FLARE, 3, 100, 7)
    d.text((cx, H-80), "thou art the spirit who gave birth to me — and the child to whom I give birth", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 14), fill=FLARE, anchor="mm")

def sc08(im, t):
    """Cognitio matutina — morning knowledge, knowledge by identity."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # horizon — dawn line
    d.line([(80, cy+40), (W-80, cy+40)], fill=rgba(SILVER, 130), width=2)
    # lower: evening knowledge (cognitio vespertina)
    d.rectangle([(100, cy+42), (W-100, H-90)], fill=rgba(DEPTH, 50))
    d.text((cx, cy+80), "cognitio vespertina — knowledge from outside", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 14), fill=SILVER, anchor="mm")
    d.text((cx, cy+110), "evening knowledge", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 12), fill=SILVER, anchor="mm")
    # upper: morning knowledge emerging
    if t > 0.2:
        p = clamp((t-0.2)/0.5)
        glow(im, (cx, cy-80), 80, GOLD, int(60*p), 18)
        for i in range(6):
            a = i*math.pi/6 - math.pi/2 + t*0.2
            r = 100 + 40*p
            x = cx+math.cos(a)*r; y = cy-80+math.sin(a)*r*0.5
            d.ellipse([x-6, y-3, x+6, y+3], fill=rgba(FLARE, int(100*p)))
    d.text((cx, cy-130), "cognitio matutina — knowledge from within", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 14), fill=GOLD, anchor="mm")
    d.text((cx, cy-105), "morning knowledge", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 12), fill=AMBER, anchor="mm")

def sc09(im, t):
    """The Emerald Rock — translucent wall of a mystical Sinai."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # rock formation
    pts = [(cx-180, cy+120), (cx-60, cy-80), (cx, cy-120), (cx+60, cy-80), (cx+180, cy+120)]
    d.polygon(pts, outline=rgba(EMERALD, 160), fill=rgba(EMERALD, 25))
    # inner translucence
    if t > 0.15:
        p = clamp((t-0.15)/0.55)
        glow(im, (cx, cy-60), 80, FLARE, int(50*p), 20)
        for i in range(3):
            ri = 40 + i*35
            d.ellipse([cx-ri, cy-60-ri, cx+ri, cy-60+ri], outline=rgba(AMBER, int(70*p-15*i)), width=1)
    # pilgrim approaching
    x_p = int(lerp(W+50, cx-130, clamp((t-0.3)/0.4)))
    d.ellipse([x_p-22, cy-30, x_p+22, cy+30], outline=rgba(SILVER, 150), width=2)
    d.ellipse([x_p-8, cy-22, x_p+8, cy-5], outline=rgba(SILVER, 150), width=2)
    d.text((cx, H-80), "the emerald rock — the threshold where light meets its source", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 15), fill=EMERALD, anchor="mm")

def sc10(im, t):
    """The exile remembers — the Chinvat Bridge."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # bridge
    pts = bezier((80, cy+80), (W//4, cy-40), (3*W//4, cy+40), (W-80, cy-60))
    bridge = partial(pts, clamp(t/0.7))
    if len(bridge) > 1: line_glow(im, bridge, GOLD, 3, 120, 8)
    # exile on one side
    x_left = int(lerp(60, 200, clamp((t-0.1)/0.3)))
    d.ellipse([x_left-28, cy+40, x_left+28, cy+90], outline=rgba(SILVER, 130), width=2)
    d.ellipse([x_left-10, cy+48, x_left+10, cy+65], outline=rgba(SILVER, 130), width=2)
    # guide on other side
    if t > 0.4:
        p = clamp((t-0.4)/0.4)
        x_right = int(lerp(W-60, W-200, p))
        glow(im, (x_right, cy-20), 40, GOLD, int(80*p), 14)
        d.ellipse([x_right-28, cy-30, x_right+28, cy+30], outline=rgba(GOLD, int(180*p)), width=2)
        d.ellipse([x_right-10, cy-22, x_right+10, cy-5], fill=rgba(FLARE, int(200*p)))
    d.text((cx, H-80), "the exile ends when you recognize the one who walked beside you", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 15), fill=GOLD, anchor="mm")

def sc11(im, t):
    """Light upon light — the hierarchy of intensities."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    for i in range(9):
        y = cy - 120 + i*30
        r = 20 - i
        col = mix(SAPPHIRE, FLARE, i/8)
        d.ellipse([cx-r, y-r, cx+r, y+r], fill=rgba(col, 180-i*12))
        if i < 8:
            d.line([(cx, y+r), (cx, y+r+30)], fill=rgba(SILVER, 80), width=1)
    # topmost — Light of Lights
    glow(im, (cx, cy-130), 35, FLARE, 90, 14)
    d.ellipse([cx-12, cy-142, cx+12, cy-118], fill=FLARE)
    d.text((cx, H-80), "light upon light — a difference in intensity, not in kind", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 15), fill=GOLD, anchor="mm")

def sc12(im, t):
    """The veils of darkness fall — self-recognition."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # veils dropping
    for i in range(5):
        y = 60 + i*130
        lift = int(lerp(0, 100, clamp(t*2 - i*0.3)))
        if lift < 100:
            d.rectangle([0, y, W, y+60], fill=NIGHT)
    # light emerging behind veils
    if t > 0.3:
        p = clamp((t-0.3)/0.5)
        glow(im, (cx, cy), 120, FLARE, int(40*p), 24)
        d.ellipse([cx-180, cy-180, cx+180, cy+180], outline=rgba(GOLD, int(50*p)), width=2)
    # the eye that sees itself
    if t > 0.6:
        p = clamp((t-0.6)/0.4)
        d.ellipse([cx-35, cy-25, cx+35, cy+25], outline=rgba(GOLD, int(200*p)), width=3)
        d.ellipse([cx-12, cy-8, cx+12, cy+8], fill=rgba(FLARE, int(255*p)))
    d.text((cx, H-80), "the seeker and the sought are the same luminosity", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=FLARE, anchor="mm")

def sc13(im, t):
    """The circle of consciousness — center everywhere, circumference nowhere."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    for i in range(8):
        r = 40 + i*42
        col = mix(SAPPHIRE, GOLD, i/7)
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rgba(col, 140-i*14), width=2)
    # radial lines
    if t > 0.1:
        p = clamp((t-0.1)/0.6)
        for i in range(12):
            a = i*math.pi/6 + t*0.2
            x = cx+math.cos(a)*380*p; y = cy+math.sin(a)*380*p
            d.line([(cx,cy), (x,y)], fill=rgba(GOLD, int(50*p)), width=1)
    glow(im, (cx,cy), 30, FLARE, 90, 12)
    d.ellipse([cx-10, cy-10, cx+10, cy+10], fill=FLARE)
    d.text((cx, H-80), "the center of the circle of consciousness is everywhere", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=GOLD, anchor="mm")

def sc14(im, t):
    """The dawn that seeks you — illumination finds the prepared."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2+30
    # dark preparation
    for i in range(15):
        a = i*2*math.pi/15
        r = 150 + 40*math.sin(i*2.3)
        x = cx+math.cos(a)*r; y = cy+math.sin(a)*r
        d.ellipse([x-3,y-3,x+3,y+3], fill=rgba(AZURE, 40))
    # dawn breaking
    if t > 0.2:
        p = clamp((t-0.2)/0.55)
        for i in range(30):
            a = i*2*math.pi/30 + t*0.15
            r = 80 + 140*p
            x = cx+math.cos(a)*r; y = cy+math.sin(a)*r-40
            col = mix(SAPPHIRE, FLARE, i/30 * p)
            d.ellipse([x-5,y-2,x+5,y+2], fill=rgba(col, int(60*p)))
    glow(im, (cx, cy-40), 70, AMBER, int(70*clamp((t-0.3)/0.5)), 18)
    d.text((cx, H-80), "the dawn seeks hermès — illumination finds the one who waits", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 15), fill=AMBER, anchor="mm")

def sc15(im, t):
    """The candle that forgot it is fire — recognition scene."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # small candle flame
    if t < 0.5:
        p = t/0.5
        for i in range(3):
            r = 15 - i*4
            col = mix(GOLD, FLARE, i/3)
            d.ellipse([cx-r, cy-180-r, cx+r, cy-180+r], fill=rgba(col, int(200-50*i)))
        d.rectangle([cx-6, cy-170, cx+6, cy-145], fill=INK)
    # expanding fire
    if t > 0.3:
        p = clamp((t-0.3)/0.55)
        r = 30 + 160*p
        glow(im, (cx, cy), r, GOLD, int(40*p), 20)
        for i in range(12):
            a = i*math.pi/6 + t*0.4
            x = cx+math.cos(a)*r*0.8; y = cy+math.sin(a)*r*0.8
            d.ellipse([x-6, y-6, x+6, y+6], fill=rgba(FLARE, int(80*p)))
    # closing: the light recognizes itself
    if t > 0.7:
        p = clamp((t-0.7)/0.3)
        d.ellipse([cx-200, cy-200, cx+200, cy+200], outline=rgba(GOLD, int(150*p)), width=3)
        d.ellipse([cx-180, cy-180, cx+180, cy+180], outline=rgba(FLARE, int(80*p)), width=1)
        d.ellipse([cx-25, cy-25, cx+25, cy+25], fill=FLARE)
    d.text((cx, H-80), "you are a candle that has forgotten it is fire", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16), fill=GOLD, anchor="mm")

def sc16(im, t):
    """Closing seal — the light returns to itself, the circle complete."""
    d = ImageDraw.Draw(im); cx,cy = W//2, H//2
    # nested circles sealing
    for i in range(6):
        r = 50 + i*55
        angle = 360*(clamp(t*1.2 - i*0.08))
        col = mix(EMERALD, GOLD, i/5)
        d.arc([cx-r, cy-r, cx+r, cy+r], 0, angle, fill=rgba(col, 160-i*20), width=3)
    # central eye
    if t > 0.4:
        p = clamp((t-0.4)/0.5)
        glow(im, (cx, cy), 70, FLARE, int(70*p), 20)
        d.ellipse([cx-40, cy-28, cx+40, cy+28], outline=rgba(GOLD, int(200*p)), width=3)
        d.ellipse([cx-14, cy-10, cx+14, cy+10], fill=rgba(FLARE, int(255*p)))
        # rays
        for i in range(8):
            a = i*math.pi/4
            x = cx+math.cos(a)*220; y = cy+math.sin(a)*220
            d.line([(cx+math.cos(a)*50, cy+math.sin(a)*50), (x, y)], fill=rgba(GOLD, int(100*p)), width=2)
    # closing quote
    d.text((cx, H-80), "the light you seek has always been the light you are", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 17), fill=FLARE, anchor="mm")

SCENES = [
    ("The Light Visible By Itself", sc01),
    ("Mundus Imaginalis", sc02),
    ("Na-Koja-Abad", sc03),
    ("Perfect Nature", sc04),
    ("Midnight Sun", sc05),
    ("Hurqalya", sc06),
    ("Fravarti", sc07),
    ("Morning Knowledge", sc08),
    ("The Emerald Rock", sc09),
    ("Chinvat Bridge", sc10),
    ("Light Upon Light", sc11),
    ("The Veils Fall", sc12),
    ("Circle of Consciousness", sc13),
    ("The Dawn Seeks You", sc14),
    ("The Candle and the Fire", sc15),
    ("Closing Seal", sc16),
]

def render_all():
    out = Path("/tmp/light-illuminates")
    out.mkdir(parents=True, exist_ok=True)
    for idx, (name, fn) in enumerate(SCENES):
        sid = f"s{idx+1:03d}"
        sd = out / sid; sd.mkdir(exist_ok=True)
        seed = 90909 + idx*137
        for fi in range(FRAMES):
            t = fi / FPS
            im = causal_ground(seed + fi)
            border(im); dust(im, seed + fi, 55)
            fn(im, t)
            im.convert("RGB").save(str(sd / f"frame_{fi:04d}.png"), quality=92)
        mp4 = out / f"{sid}.mp4"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",str(sd/"frame_%04d.png"),"-c:v","libx264","-pix_fmt","yuv420p","-preset","fast","-crf","20",str(mp4)])
        print(f"{sid}: {name}")
    # concat
    with open(out/"concat.txt","w") as f:
        for idx in range(len(SCENES)):
            f.write(f"file '{out}/s{idx+1:03d}.mp4'\n")
    final = out/"final.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(out/"concat.txt"),"-c","copy",str(final)])
    print(f"\nDone: {final}  ({final.stat().st_size//1024}KB)")

if __name__ == "__main__":
    render_all()