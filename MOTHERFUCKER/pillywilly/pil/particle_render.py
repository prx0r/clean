#!/usr/bin/env python3
"""
particle_render.py — Generate video clips of particle systems matching beat-map visuals.

Usage:
  python3 particle_render.py --beat daimon_clusters --duration 20 --out /tmp/clip.mp4
  python3 particle_render.py --beat void_particles --duration 10 --out /tmp/clip.mp4
  python3 particle_render.py --beat attractor_merge --duration 15 --out /tmp/clip.mp4
  python3 particle_render.py --beat body_coherence --duration 12 --out /tmp/clip.mp4
  python3 particle_render.py --beat cakra_spectrum --duration 15 --out /tmp/clip.mp4
  python3 particle_render.py --beat prediction_field --duration 8 --out /tmp/clip.mp4
  python3 particle_render.py --beat green_core_pulse --duration 10 --out /tmp/clip.mp4

Renders particle fields to PNG frames, then encodes to MP4 via FFmpeg subprocess.
Pure Python — no browser needed. Outputs 1920x1080 @ 24fps.
"""

import argparse
import math
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Color Palette ──
C = {
    "bg":       (13, 17, 23),       # #0D1117 void
    "gold":     (212, 165, 116),    # #D4A574 geometry
    "gold_dim": (139, 115, 85),     # #8B7355 dimmed
    "purple":   (168, 85, 247),     # #A855F7 secondary
    "white":    (230, 225, 220),    # #E6E1DC text
    "turquoise":(20, 184, 166),     # #14B8A6 accents
    "green":    (0, 255, 136),      # #00FF88 core
    "dark_green":(22, 101, 52),    # #166534 life
    "red":      (255, 68, 68),      # #FF4444 error
    "muted":    (107, 114, 128),    # #6B7280 grey
}

W, H = 1920, 1080
FPS = 24


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hsv_to_rgb(h, s=0.7, v=0.8):
    """h in [0,360], s,v in [0,1]"""
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


# ═══════════════════════════════════════════════════════════════
# SCENE: Void particles — subtle background noise field
# ═══════════════════════════════════════════════════════════════
class VoidParticles:
    def __init__(self, n=200):
        self.n = n
        self.particles = [{
            'x': random.random() * W, 'y': random.random() * H,
            'vx': (random.random() - 0.5) * 0.8,
            'vy': (random.random() - 0.5) * 0.8,
            'size': random.random() * 1.5 + 0.3,
            'opacity': random.random() * 0.3 + 0.05,
            'hue': random.random() * 30 + 25,  # gold range
        } for _ in range(n)]

    def update(self, t, phase=0):
        for p in self.particles:
            p['x'] += p['vx'] + math.sin(t * 3 + p['y'] * 0.01) * 0.3
            p['y'] += p['vy'] + math.cos(t * 2 + p['x'] * 0.01) * 0.3
            if p['x'] < -10: p['x'] = W + 10
            if p['x'] > W + 10: p['x'] = -10
            if p['y'] < -10: p['y'] = H + 10
            if p['y'] > H + 10: p['y'] = -10

    def draw(self, img, t):
        for p in self.particles:
            x, y = int(p['x']), int(p['y'])
            if 0 <= x < W and 0 <= y < H:
                c = hsv_to_rgb(p['hue'], 0.4, 0.3 + p['opacity'])
                img.putpixel((x, y), c)


# ═══════════════════════════════════════════════════════════════
# SCENE: Daimon clusters — 5 attractor clusters merging into 1
# ═══════════════════════════════════════════════════════════════
class DaimonClusters:
    def __init__(self, n=500):
        self.n = n
        # 5 initial cluster centers
        self.centers = []
        for i in range(5):
            angle = (i / 5) * math.pi * 2
            r = W * 0.25
            self.centers.append((W / 2 + math.cos(angle) * r, H / 2 + math.sin(angle) * r))

        self.target = (W / 2, H / 2)
        self.particles = []
        for _ in range(n):
            c = random.choice(self.centers)
            self.particles.append({
                'x': c[0] + (random.random() - 0.5) * 150,
                'y': c[1] + (random.random() - 0.5) * 150,
                'vx': 0, 'vy': 0,
                'cluster': random.randint(0, 4),
                'size': random.random() * 2 + 0.5,
                'hue': random.random() * 60 + 20,
            })

    def update(self, t, phase=1.0):
        for p in self.particles:
            c = self.centers[p['cluster']]
            # Attract toward cluster center (weakening) plus toward target (strengthening)
            cx, cy = c
            fx = (cx - p['x']) * 0.003 * (1 - phase) + (self.target[0] - p['x']) * 0.003 * phase
            fy = (cy - p['y']) * 0.003 * (1 - phase) + (self.target[1] - p['y']) * 0.003 * phase
            fx += (random.random() - 0.5) * 0.5
            fy += (random.random() - 0.5) * 0.5
            p['vx'] += fx
            p['vy'] += fy
            p['vx'] *= 0.96
            p['vy'] *= 0.96
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['hue'] = 30 + phase * 10  # goldish → converging to gold

    def draw(self, img, t):
        for p in self.particles:
            x, y = int(p['x']), int(p['y'])
            if 0 <= x < W and 0 <= y < H:
                c = hsv_to_rgb(p['hue'], 0.5, 0.6)
                # Draw small glow
                r = int(p['size'] * 3)
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r:
                            px, py = x + dx, y + dy
                            if 0 <= px < W and 0 <= py < H:
                                dist = math.sqrt(dx * dx + dy * dy)
                                alpha = max(0, 1 - dist / r) * 0.3
                                existing = img.getpixel((px, py))
                                blend = tuple(int(existing[i] * (1 - alpha) + c[i] * alpha) for i in range(3))
                                img.putpixel((px, py), blend)


# ═══════════════════════════════════════════════════════════════
# SCENE: Body coherence — particle outline that doesn't decay
# ═══════════════════════════════════════════════════════════════
class BodyCoherence:
    def __init__(self, n=400):
        self.n = n
        cx, cy = W / 2, H / 2 - 50
        # Generate body outline points (simple ellipse for body)
        self.particles = []
        for _ in range(n):
            angle = random.random() * math.pi * 2
            rx = 120 + random.random() * 30
            ry = 280 + random.random() * 40
            self.particles.append({
                'x': cx + math.cos(angle) * rx,
                'y': cy + math.sin(angle) * ry * 0.4,
                'ox': cx + math.cos(angle) * rx,
                'oy': cy + math.sin(angle) * ry * 0.4,
                'size': random.random() * 2 + 0.5,
                'phase': random.random() * math.pi * 2,
                'hue': 30,
            })
        # Add heart-center cluster
        for _ in range(50):
            self.particles.append({
                'x': cx + (random.random() - 0.5) * 30,
                'y': cy - 60 + (random.random() - 0.5) * 30,
                'ox': cx, 'oy': cy - 60,
                'size': random.random() * 3 + 1,
                'phase': random.random() * math.pi * 2,
                'hue': 30,
                'heart': True,
            })

    def update(self, t, phase=0):
        for p in self.particles:
            if phase < 0.5:  # Alive: breathing animation
                breathe = math.sin(t * 1.5 + p['phase']) * (1 - phase) * 5
                p['x'] = p['ox'] + breathe * (p['ox'] - W / 2) * 0.01
                p['y'] = p['oy'] + breathe * (p['oy'] - (H / 2 - 50)) * 0.01
            elif phase < 0.8:  # Death: particles slow but don't dissipate
                p['x'] += (random.random() - 0.5) * 0.1
                p['y'] += (random.random() - 0.5) * 0.1
            else:  # Tukdam: minimal vibration
                p['x'] += (random.random() - 0.5) * 0.05
                p['y'] += (random.random() - 0.5) * 0.05
            p['hue'] = 30 - phase * 15  # gold → warm gold as coherence persists

    def draw(self, img, t):
        for p in self.particles:
            x, y = int(p['x']), int(p['y'])
            if 0 <= x < W and 0 <= y < H:
                c = hsv_to_rgb(p['hue'], 0.5, 0.5 + 0.3 if p.get('heart') else 0.3)
                r = int(p['size'] * 2)
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r:
                            px, py = x + dx, y + dy
                            if 0 <= px < W and 0 <= py < H:
                                dist = math.sqrt(dx * dx + dy * dy)
                                alpha = max(0, 1 - dist / r) * 0.25
                                existing = img.getpixel((px, py))
                                blend = tuple(int(existing[i] * (1 - alpha) + c[i] * alpha) for i in range(3))
                                img.putpixel((px, py), blend)


# ═══════════════════════════════════════════════════════════════
# SCENE: Cakra spectrum — 7 colors with green center at 550nm
# ═══════════════════════════════════════════════════════════════
class CakraSpectrum:
    def __init__(self, n=300):
        self.n = n
        self.cakras = [
            {'y': H * 0.85, 'hue': 0,   'name': 'ROOT', 'size': 40},
            {'y': H * 0.72, 'hue': 30,  'name': 'SACRAL', 'size': 45},
            {'y': H * 0.59, 'hue': 50,  'name': 'SOLAR PLEXUS', 'size': 50},
            {'y': H * 0.46, 'hue': 140, 'name': 'HEART · 550nm', 'size': 60},  # GREEN
            {'y': H * 0.33, 'hue': 210, 'name': 'THROAT', 'size': 50},
            {'y': H * 0.20, 'hue': 270, 'name': 'THIRD EYE', 'size': 45},
            {'y': H * 0.08, 'hue': 290, 'name': 'CROWN', 'size': 40},
        ]
        # Place particles around each cakra
        self.particles = []
        for c in self.cakras:
            for _ in range(n // 7):
                angle = random.random() * math.pi * 2
                r = c['size'] + random.random() * 30
                self.particles.append({
                    'x': W / 2 + math.cos(angle) * r,
                    'y': c['y'] + math.sin(angle) * r * 0.5,
                    'ox': W / 2 + math.cos(angle) * r,
                    'oy': c['y'] + math.sin(angle) * r * 0.5,
                    'hue': c['hue'],
                    'size': random.random() * 2 + 0.5,
                    'phase': random.random() * math.pi * 2,
                })

    def update(self, t, phase=0):
        for p in self.particles:
            p['x'] = p['ox'] + math.sin(t * 1.2 + p['phase']) * 3
            p['y'] = p['oy'] + math.cos(t * 0.8 + p['phase']) * 2

    def draw(self, img, t):
        for p in self.particles:
            x, y = int(p['x']), int(p['y'])
            if 0 <= x < W and 0 <= y < H:
                c = hsv_to_rgb(p['hue'], 0.7, 0.6)
                r = int(p['size'] * 2)
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r:
                            px, py = x + dx, y + dy
                            if 0 <= px < W and 0 <= py < H:
                                dist = math.sqrt(dx * dx + dy * dy)
                                alpha = max(0, 1 - dist / r) * 0.2
                                existing = img.getpixel((px, py))
                                blend = tuple(int(existing[i] * (1 - alpha) + c[i] * alpha) for i in range(3))
                                img.putpixel((px, py), blend)


# ═══════════════════════════════════════════════════════════════
# SCENE: Prediction error field — particles minimizing error
# ═══════════════════════════════════════════════════════════════
class PredictionField:
    def __init__(self, n=400):
        self.n = n
        self.particles = []
        for _ in range(n):
            self.particles.append({
                'x': random.random() * W,
                'y': random.random() * H,
                'vx': (random.random() - 0.5) * 3,
                'vy': (random.random() - 0.5) * 3,
                'size': random.random() * 2 + 0.3,
                'error': random.random(),
                'hue': random.random() * 20,  # red range — high error
            })

    def update(self, t, phase=0):
        # As phase progresses, error decreases — particles settle
        for p in self.particles:
            p['error'] = max(0.01, p['error'] - 0.002)
            speed = p['error'] * 2
            p['vx'] += (random.random() - 0.5) * speed * 0.2
            p['vy'] += (random.random() - 0.5) * speed * 0.2
            p['vx'] *= 0.98
            p['vy'] *= 0.98
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['x'] < 0: p['x'] = W
            if p['x'] > W: p['x'] = 0
            if p['y'] < 0: p['y'] = H
            if p['y'] > H: p['y'] = 0
            p['hue'] = p['error'] * 30 + (1 - p['error']) * 160  # red → green

    def draw(self, img, t):
        for p in self.particles:
            x, y = int(p['x']), int(p['y'])
            if 0 <= x < W and 0 <= y < H:
                c = hsv_to_rgb(p['hue'], 0.6, 0.5 + (1 - p['error']) * 0.3)
                r = int(p['size'] * 3)
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r:
                            px, py = x + dx, y + dy
                            if 0 <= px < W and 0 <= py < H:
                                dist = math.sqrt(dx * dx + dy * dy)
                                alpha = max(0, 1 - dist / r) * 0.15
                                existing = img.getpixel((px, py))
                                blend = tuple(int(existing[i] * (1 - alpha) + c[i] * alpha) for i in range(3))
                                img.putpixel((px, py), blend)


# ═══════════════════════════════════════════════════════════════
# RENDERER — Frame loop → FFmpeg encode
# ═══════════════════════════════════════════════════════════════
SCENES = {
    'void_particles': VoidParticles,
    'daimon_clusters': DaimonClusters,
    'body_coherence': BodyCoherence,
    'cakra_spectrum': CakraSpectrum,
    'prediction_field': PredictionField,
}


def render_scene(scene_name, duration, out_path, phase_fn=None):
    """Render a particle scene to MP4 via frame rendering + FFmpeg pipe."""
    if scene_name not in SCENES:
        print(f"Unknown scene: {scene_name}")
        print(f"Available: {list(SCENES.keys())}")
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed. Install with: pip install Pillow")
        sys.exit(1)

    scene = SCENES[scene_name]()
    n_frames = int(duration * FPS)

    # Encode via FFmpeg pipe
    ffmpeg_cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}', '-pix_fmt', 'rgb24', '-r', str(FPS),
        '-i', 'pipe:0',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        out_path,
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    for frame_i in range(n_frames):
        t = frame_i / FPS
        phase = phase_fn(t) if phase_fn else t / duration
        img = Image.new('RGB', (W, H), C['bg'])
        scene.update(t, phase)
        scene.draw(img, t)
        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        print(f"FFmpeg failed with code {proc.returncode}")
        sys.exit(1)

    print(f"  Rendered: {out_path} ({duration}s, {n_frames} frames)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--beat', required=True, choices=list(SCENES.keys()))
    parser.add_argument('--duration', type=float, required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    render_scene(args.beat, args.duration, args.out)
