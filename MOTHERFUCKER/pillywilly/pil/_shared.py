"""
Shared platinum pack infrastructure — colors, helpers, pipeline, CLI.
Import by every pack to avoid 800 lines of boilerplate.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

IVORY = (249, 247, 241)
PAPER = (242, 239, 231)
INK = (31, 36, 42)
SOFT_INK = (85, 91, 97)
SILVER = (180, 187, 191)
PALE_SILVER = (224, 228, 228)
CYAN = (55, 157, 178)
PALE_CYAN = (194, 227, 233)
DEEP_CYAN = (35, 104, 128)
GOLD = (193, 155, 72)
PALE_GOLD = (235, 218, 172)
CRIMSON = (164, 57, 69)
PALE_CRIMSON = (231, 198, 201)
GREEN = (68, 139, 99)
PALE_GREEN = (196, 225, 206)
VIOLET = (107, 82, 151)
PALE_VIOLET = (218, 208, 235)
WHITE = (255, 254, 250)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def lerp(a, b, t):
    return a + (b - a) * clamp(t)

def mix(a, b, t):
    t = clamp(t)
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))

def smoothstep(a, b, x):
    if a == b:
        return 1.0 if x >= b else 0.0
    q = clamp((x - a) / (b - a))
    return q * q * (3 - 2 * q)

def ease(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)

def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3

def pulse(t, speed=1.0, phase=0.0):
    return 0.5 + 0.5 * math.sin(math.tau * (speed * t + phase))

def font(path, size):
    for c in (path, FONT_SERIF, FONT_SANS):
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            pass
    return ImageFont.load_default()

def layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))

def scientific_field(w, h, seed):
    rng = np.random.default_rng(seed)
    base = np.empty((h, w, 3), dtype=np.float32)
    base[:] = IVORY
    fine = rng.normal(0, 0.95, (h, w, 1))
    base += fine
    yy, xx = np.mgrid[0:h, 0:w]
    halo = np.exp(-(((xx - w * 0.52)/(w * 0.36))**2 + ((yy - h * 0.39)/(h * 0.30))**2) * 2.1)
    base[..., 0] += halo * 1.5
    base[..., 1] += halo * 4.0
    base[..., 2] += halo * 5.5
    base = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(base, "RGB").convert("RGBA")

def centered(draw, xy, text, fnt, fill=INK):
    draw.text(xy, text, font=fnt, fill=fill, anchor="mm")

def border(im):
    w, h = im.size
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((26, 26, w-26, h-26), radius=18, outline=(*INK, 48), width=2)
    for x, y in ((52,52),(w-52,52),(52,h-52),(w-52,h-52)):
        d.line((x-9,y,x+9,y), fill=(*CYAN,80), width=1)
        d.line((x,y-9,x,y+9), fill=(*CYAN,80), width=1)

def seal(im, title, subtitle="", color=INK):
    w, h = im.size
    d = ImageDraw.Draw(im)
    tf = font(FONT_SERIF_BOLD, max(22, int(h*0.040)))
    sf = font(FONT_SANS, max(13, int(h*0.019)))
    centered(d, (w/2, h*0.875), title, tf, color)
    if subtitle:
        centered(d, (w/2, h*0.923), subtitle, sf, SOFT_INK)

def glow_circle(im, x, y, r, color, alpha=170, blur=16):
    gl = layer(im.size)
    ImageDraw.Draw(gl).ellipse((x-r,y-r,x+r,y+r), fill=(*color, int(alpha)))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    core = layer(im.size)
    ImageDraw.Draw(core).ellipse((x-r*.38,y-r*.38,x+r*.38,y+r*.38),
                                  fill=(*mix(color,WHITE,.35), min(255,int(alpha)+55)))
    im.alpha_composite(core)

def glow_line(im, points, color, width=4, alpha=210, blur=12):
    if len(points)<2: return
    gl = layer(im.size)
    ImageDraw.Draw(gl).line(points, fill=(*color,int(alpha)), width=width*3, joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg = layer(im.size)
    ImageDraw.Draw(fg).line(points, fill=(*mix(color,WHITE,.08),min(255,int(alpha)+25)),
                             width=width, joint="curve")
    im.alpha_composite(fg)

def partial(points, amount):
    amount = clamp(amount)
    if not points: return []
    if amount >= 1: return points
    target = amount * (len(points)-1)
    idx = int(target)
    frac = target - idx
    out = list(points[:idx+1])
    if idx+1 < len(points):
        a, b = points[idx], points[idx+1]
        out.append((lerp(a[0],b[0],frac), lerp(a[1],b[1],frac)))
    return out

def arrow(draw, a, b, color=INK, width=3, head=10):
    draw.line((*a,*b), fill=color, width=width)
    ang = math.atan2(b[1]-a[1], b[0]-a[0])
    for s in (-1,1):
        p = (b[0]-math.cos(ang+s*.53)*head, b[1]-math.sin(ang+s*.53)*head)
        draw.line((*b,*p), fill=color, width=width)

def wave_curve(cx, cy, length, amplitude, phase=0.0, samples=80):
    pts = []
    for i in range(samples):
        q = i/(samples-1)
        x = cx - length/2 + q*length
        y = cy + math.sin(q*math.tau + phase)*amplitude
        pts.append((x,y))
    return pts

def dream_thread(cx, cy, length, amp, phase=0.0, samples=100):
    pts = []
    for i in range(samples):
        q = i/(samples-1)
        x = cx - length/2 + q*length
        y = cy + math.sin(q*math.tau*3+phase)*amp*(0.3+0.7*math.sin(math.pi*q)**0.6)
        pts.append((x,y))
    return pts


@dataclass
class Scene:
    title: str
    narration: str
    duration: float
    visual: str
    params: dict


def build_pipeline(visuals: dict, scenes: list[Scene], output_slug: str, title: str,
                   palette_roles: dict, continuity: str):
    OUTPUT = Path(f"/mnt/HC_Volume_106427611/goldrender/output_{output_slug}")
    FRAMES = OUTPUT / "frames"
    SCENES_DIR = OUTPUT / "scenes"
    VISUALS = visuals
    SCENES = scenes

    def render_frame(scene, frame_index, frame_count, width, height, seed):
        u = frame_index/max(1, frame_count-1)
        t = u * scene.duration
        im = scientific_field(width, height, seed)
        VISUALS[scene.visual](im, u, t, scene.params)
        border(im)
        return im.convert("RGB")

    def ffmpeg_path():
        ff = shutil.which("ffmpeg")
        if not ff: raise RuntimeError("ffmpeg required")
        return ff

    def encode_scene(scene_index, fps):
        out = SCENES_DIR / f"scene_{scene_index:03d}.mp4"
        fd = FRAMES / f"scene_{scene_index:03d}"
        subprocess.run([ffmpeg_path(), "-y", "-framerate", str(fps),
            "-i", str(fd/"%05d.jpg"), "-c:v", "libx264",
            "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(out)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out

    def render_scene(index, scene, fps, width, height, preview):
        fd = FRAMES / f"scene_{index:03d}"
        fd.mkdir(parents=True, exist_ok=True)
        SCENES_DIR.mkdir(parents=True, exist_ok=True)
        count = max(2, round(scene.duration * fps))
        if preview:
            for oi, fi in enumerate([0, int(count*.32), int(count*.72), count-1]):
                render_frame(scene, fi, count, width, height, index*10000+fi).save(
                    fd/f"preview_{oi:02d}.jpg", quality=95)
            return fd
        for fi in range(count):
            p = fd/f"{fi:05d}.jpg"
            if p.exists(): continue
            render_frame(scene, fi, count, width, height, index*10000+fi).save(p, quality=95, subsampling=0)
        return encode_scene(index, fps)

    def concat(paths):
        cp = OUTPUT/"concat.txt"
        cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths), encoding="utf-8")
        final = OUTPUT/f"{output_slug}.mp4"
        subprocess.run([ffmpeg_path(), "-y", "-f", "concat", "-safe", "0",
            "-i", str(cp), "-c", "copy", "-movflags", "+faststart", str(final)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return final

    def export_timeline():
        cursor = 0.0
        records = []
        for i, s in enumerate(SCENES, 1):
            item = asdict(s)
            item["scene_id"] = f"scene_{i:03d}"
            item["start_seconds"] = round(cursor, 3)
            cursor += s.duration
            item["end_seconds"] = round(cursor, 3)
            records.append(item)
        p = OUTPUT/"narration_timeline.json"
        p.write_text(json.dumps({
            "title": title, "scene_count": len(SCENES),
            "runtime_seconds": round(cursor, 3),
            "shot_duration_range": [5, 10],
            "continuity_object": continuity,
            "palette_roles": palette_roles,
            "scenes": records,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        return p

    def contact_sheet(width, height):
        tw, th = 320, int(320*height/width)
        cols, rows = 4, math.ceil(len(SCENES)/cols)
        ch = th + 48
        sheet = Image.new("RGB", (cols*tw, rows*ch), IVORY)
        d = ImageDraw.Draw(sheet)
        lf = font(FONT_SANS_BOLD, 14)
        for i, s in enumerate(SCENES, 1):
            cnt = max(2, round(s.duration*DEFAULT_FPS))
            im = render_frame(s, int(cnt*.72), cnt, width, height, i*10000+72)
            im.thumbnail((tw, th))
            sl = i-1
            x, y = (sl%cols)*tw, (sl//cols)*ch
            sheet.paste(im, (x, y))
            d.text((x+9, y+th+7), f"{i:02d}  {s.title}", font=lf, fill=INK)
        p = OUTPUT/"contact_sheet.jpg"
        sheet.save(p, quality=94)
        return p

    def args():
        p = argparse.ArgumentParser()
        p.add_argument("--fps", type=int, default=DEFAULT_FPS)
        p.add_argument("--width", type=int, default=DEFAULT_WIDTH)
        p.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
        p.add_argument("--scene", type=int, default=None)
        p.add_argument("--preview", action="store_true")
        p.add_argument("--no-contact-sheet", action="store_true")
        return p.parse_args()

    def main():
        a = args()
        OUTPUT.mkdir(parents=True, exist_ok=True)
        FRAMES.mkdir(parents=True, exist_ok=True)
        SCENES_DIR.mkdir(parents=True, exist_ok=True)
        tl = export_timeline()
        total = sum(s.duration for s in SCENES)
        print(f"Timeline: {tl}")
        print(f"Scenes: {len(SCENES)}")
        print(f"Runtime: {total/60:.2f} min")
        if a.scene is not None:
            if not 1 <= a.scene <= len(SCENES):
                raise ValueError(f"--scene must be 1..{len(SCENES)}")
            print(render_scene(a.scene, SCENES[a.scene-1], a.fps, a.width, a.height, a.preview))
            return
        rendered = []
        for i, s in enumerate(SCENES, 1):
            print(f"[{i:02d}/{len(SCENES):02d}] {s.title} ({s.duration:.1f}s)")
            rendered.append(render_scene(i, s, a.fps, a.width, a.height, a.preview))
        final = concat(rendered)
        print(f"Final: {final}")
        if not a.no_contact_sheet:
            print(f"Contact sheet: {contact_sheet(a.width, a.height)}")
        print("Done.")

    return main
