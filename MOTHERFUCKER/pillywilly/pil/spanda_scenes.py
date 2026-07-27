"""Spanda scene functions. Each takes (t, u, idx) and returns an Image."""

import math
from PIL import ImageDraw
from renderer import *

def s_hook(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "The hidden pulse", dark=False)

    breathe = 1 + 0.04 * math.sin(t * 0.6)
    dot(d, cx, cy, 10*breathe, CRIMSON, 1)
    for i in range(4):
        a = smoothstep(3, 12, t) * max(0, 0.15 - i*0.03)
        ri = 70*(i+1) + 6*math.sin(t*0.5 + i)
        ring(d, cx, cy, ri, color=BLACK, alpha=a, width=1)

    if t > 25.5:
        a = smoothstep(25.5, 26.5, t)
        centered(d, "स्पन्द", 200, FONT["dev_xl"], CRIMSON, a)
    return im

def s_wheel(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2 - 20
    label(d, idx, "Wheel of powers", dark=False)

    dot(d, cx, cy, 6, BLACK, 1)
    for i in range(3):
        ang = t*0.3 + i*2.094
        d.line((cx, cy, cx+140*math.cos(ang), cy+140*math.sin(ang)), fill=BLACK, width=2)
    pr = 160 + 3*math.sin(t*0.4)
    ring(d, cx, cy, pr, color=BLACK, alpha=1, width=2)

    if t > 5:
        a = smoothstep(5, 8, t)
        centered(d, "यस्योन्मेषनिमेषाभ्यां", 100, FONT["dev_m"], BLACK, a)
        centered(d, "जगतः प्रलयोदयौ", 140, FONT["dev_m"], MUTED, a*0.7)
    return im

def s_six(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2 - 10
    label(d, idx, "Six names for one thing", dark=False)

    dot(d, cx, cy, 5, CRIMSON, 1)
    for i, (skt, eng) in enumerate([("प्राणना","vitality"),("स्फुरत्ता","effulgence"),("विश्रान्ति","repose"),
                                     ("जीव","being"),("हृदय","heart"),("स्पन्द","vibration")]):
        at = 0.05 + i*0.12
        a = smoothstep(at, at+0.06, u)
        if a <= 0: continue
        ang = i*1.047 - 1.57
        r = 160 + 10*math.sin(t*0.2 + i)
        nx = cx + r*math.cos(ang)
        ny = cy + r*math.sin(ang)
        d.text((nx-20, ny-10), skt, font=FONT["dev_m"], fill=BLACK)
        d.text((nx+45, ny-6), eng, font=FONT["xs"], fill=MUTED)
    centered(d, "six names for one thing", 80, FONT["m"], BLACK, smoothstep(0.02, 0.1, u))
    return im

def s_mantra(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "Mantra as pulse", dark=False)

    ap = 50 + 30*math.sin(t*0.6)
    d.rectangle((cx-15, cy-ap, cx+15, cy+ap), outline=BLACK, width=2)
    for i in range(6):
        y = cy - ap + 10 + i*(ap*2-20)/5
        dot(d, cx+10*math.sin(t*4+i), y, 2, CRIMSON, 0.5+0.3*math.sin(t+i))
    return im

def s_perception(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "Every perception a pulse", dark=False)

    ap = 40 + 40*math.sin(t*0.3)
    for side in (-1, 1):
        d.arc((cx-70, cy-35, cx+70, cy+35), -90+side*ap/2, 90-side*ap/2, fill=BLACK, width=3)
    dot(d, cx, cy, 5, CRIMSON, smoothstep(1, 3, t))
    if t > 3:
        a = smoothstep(3, 5, t)
        centered(d, "unmeṣa", 130, FONT["m"], BLACK, a)
        centered(d, "nimeṣa", 160, FONT["s"], MUTED, a*0.7)
    return im

def s_throb(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "Belly of the fish", dark=False)

    throb = 1 + 0.05*math.sin(t*0.6)
    for i in range(4):
        ri = 60*(i+1)*throb + 8*math.sin(t*0.5 + i)
        ring(d, cx, cy, ri, color=CRIMSON if i < 2 else BLACK,
             alpha=smoothstep(0.05+i*0.04, 0.3+i*0.04, u)*(0.3-i*0.05), width=2)
    dot(d, cx, cy, 6, CRIMSON, smoothstep(2, 4, t))
    return im

def s_chain(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2 - 20
    label(d, idx, "Time-breath-void", dark=False)

    chain = ["TIME", "BREATH", "SPANDA", "VOID", "CONSCIOUSNESS"]
    sp, sy = 75, cy - (len(chain)-1)*75/2
    for i, label_text in enumerate(chain):
        at = 0.03 + i*0.12
        a = smoothstep(at, at+0.08, u)
        if a <= 0: continue
        y = sy + i*sp
        d.rounded_rectangle((cx-80, y-16, cx+80, y+16), 5, 5, outline=BLACK, width=2)
        d.text((cx-55, y-10), label_text, font=FONT["m"], fill=BLACK)
        if i < len(chain)-1:
            d.line((cx, y+18, cx, y+sp-18), fill=MUTED, width=2)
    return im

def s_play(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "The universe is play", dark=False)

    dot(d, cx, cy, 6, BLACK, 1)
    for i in range(10):
        ang = t*0.2 + i*0.628
        r = 120 + 20*math.sin(t*0.3 + i)
        dot(d, cx+r*math.cos(ang), cy+r*math.sin(ang), 3,
            CRIMSON if i % 2 else BLACK, 0.6+0.3*math.sin(t+i))
    return im

def s_recog(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "Recognition", dark=False)

    d.line((cx, 50, cx, 650), fill=MUTED, width=1)
    progress = smoothstep(1, 12, t)
    for i in range(14):
        ta = i*2*math.pi/14
        r = 240*(1 - 0.6*progress)
        ang = ta + (1-progress)*(i*0.15)
        dot(d, cx+r*math.cos(ang), cy+r*math.sin(ang), 3, BLACK, 0.8-0.4*progress)
    dot(d, cx, cy, 6, CRIMSON, smoothstep(2, 6, t))
    return im

def s_close(t, u, idx):
    im = canvas(WHITE)
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2
    label(d, idx, "Complete expansion", dark=False)

    r = 6 + smoothstep(10, 18, t) * 700
    dot(d, cx, cy, r, CRIMSON, 1)
    if t < 10:
        a = smoothstep(1, 3, t)
        centered(d, "the sixth bliss", 300, FONT["l"], BLACK, a)
        centered(d, "is complete expansion", 360, FONT["m"], MUTED, a*0.7)
    return im

SCENES = [
    Scene("The hidden pulse",      35.7, s_hook,        "Hook: bindu, field, Sanskrit at 26s"),
    Scene("Wheel of powers",       42.0, s_wheel,       "Wheel hub, verse, three spokes"),
    Scene("Six names",             34.7, s_six,         "Six Sanskrit terms radiate"),
    Scene("Mantra as pulse",       35.3, s_mantra,      "Aperture breath, particles"),
    Scene("Every perception",      40.6, s_perception,  "Unmesha-nimesha eye aperture"),
    Scene("Belly of the fish",     37.0, s_throb,       "Throbbing rings, organic form"),
    Scene("Time-breath-void",      38.3, s_chain,       "Five-layer cascade"),
    Scene("The universe is play",  33.6, s_play,        "Orbiting geometry"),
    Scene("Recognition",           33.6, s_recog,       "Mirror alignment"),
    Scene("Complete expansion",    21.7, s_close,       "Bindu expands to white"),
]
