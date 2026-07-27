"""Ralph loop: builds packs one at a time from research objects.
Each pack is read, designed, built, saved. Then next."""

import math, json, sys, os
from PIL import Image, ImageDraw
from pathlib import Path

W, H = 1280, 720
D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57); W_ = (255, 255, 255)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def render_pack(name, scenes, desc):
    """Render a pack. scenes = [(fn, dur, title), ...]"""
    from renderer import Film, Scene
    path = Path(__file__).parent.parent.parent / 'scripts' / 'renderer'
    sys.path.insert(0, str(path))
    sys.path.insert(0, str(Path(__file__).parent))
    from renderer import Film, Scene
    
    scene_list = [Scene(title, dur, fn, title) for fn, dur, title in scenes]
    film = Film(name, desc, scene_list)
    out = Path(f'/root/projects/FableCut/media/ralph-{name}.mp4')
    film.render(out)
    sz = out.stat().st_size / 1024
    print(f"✅ ralph-{name}.mp4 — {sz:.0f}K ({len(scenes)} scenes)")
    return out
