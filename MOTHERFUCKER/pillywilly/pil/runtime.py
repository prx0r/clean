"""
PIL Render Runtime v1 — stable harness for scene function execution.
LLM generates only scene functions. This runtime handles everything else.
"""
import json, math, os, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from PIL import Image, ImageDraw

# ── CONFIG ─────────────────────────────────────────
W, H = 1280, 720
FPS = 2
DEFAULT_DURATION = 6.0

# ── SCENE SPEC ────────────────────────────────────
@dataclass
class SceneSpec:
    shot_id: str
    duration: float
    render: Callable  # fn(ctx, t, u) -> Image

# ── RENDER CONTEXT ───────────────────────────────
@dataclass
class RenderContext:
    shot_id: str
    width: int = W
    height: int = H
    fps: int = FPS
    frame_count: int = 0
    output_dir: Path = Path("output")
    assets: dict = field(default_factory=dict)

# ── PALETTE (frozen — all generated code must use these symbols) ──
PALETTE = {
    "PARCHMENT": (245, 242, 238),
    "INK": (40, 40, 42),
    "GOLD": (180, 150, 60),
    "GOLD_LIGHT": (210, 190, 130),
    "CRIMSON": (160, 55, 55),
    "LAPIS": (55, 75, 120),
    "SILVER": (180, 188, 195),
    "DARK": (50, 52, 55),
    "WHITE": (250, 248, 244),
    "VOID": (26, 29, 35),
}

def canvas(bg=PALETTE["PARCHMENT"]):
    return Image.new("RGB", (W, H), bg)
    return Image.new("RGB", (W, H), bg)

# ── FILM ──────────────────────────────────────────
class Film:
    def __init__(self, scenes: list, output_dir: str = "output"):
        self.scenes = scenes
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.shot_dir = self.output_dir / "shots"
        self.shot_dir.mkdir(exist_ok=True)

    def render(self):
        clip_paths = []
        for spec in self.scenes:
            sid = spec.shot_id
            dur = spec.duration
            n_frames = max(1, int(dur * FPS))
            ctx = RenderContext(shot_id=sid, frame_count=n_frames, output_dir=self.shot_dir)
            shot_out = self.shot_dir / sid
            shot_out.mkdir(exist_ok=True)
            print(f"  {sid}: {n_frames} frames @ {FPS}fps = {dur}s")

            for fi in range(n_frames):
                t_val = fi / FPS
                u_val = fi / max(1, n_frames - 1)
                im = spec.render(ctx, t_val, u_val)
                im.save(str(shot_out / f"frame_{fi:04d}.png"))

            # Assemble MP4 shot clip
            mp4 = self.shot_dir / f"{sid}.mp4"
            subprocess.run([
                "ffmpeg", "-y", "-framerate", str(FPS), "-i",
                f"{shot_out}/frame_%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "ultrafast", "-crf", "28",
                "-t", str(dur), str(mp4)
            ], capture_output=True)
            clip_paths.append(mp4)

        # Concatenate all clips
        concat_file = self.output_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for mp4 in clip_paths:
                f.write(f"file '{mp4}'\n")

        draft = self.output_dir / "draft.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-c", "copy", str(draft)
        ], capture_output=True)
        print(f"  Draft: {draft}")
        return draft

    def contact_sheet(self):
        """Generate a 4-frame motion strip for each shot."""
        strip_dir = self.output_dir / "motion_strips"
        strip_dir.mkdir(exist_ok=True)
        times = [0.15, 0.40, 0.70, 0.92]

        for spec in self.scenes:
            sid = spec.shot_id
            dur = spec.duration
            n_frames = max(1, int(dur * FPS))
            ctx = RenderContext(shot_id=sid, frame_count=n_frames, output_dir=self.shot_dir)

            strip = Image.new("RGB", (W * 4, H), PALETTE["PARCHMENT"])
            for i, u in enumerate(times):
                fi = int(u * (n_frames - 1))
                t_val = fi / FPS
                im = spec.render(ctx, t_val, u)
                strip.paste(im, (i * W, 0))

            strip.save(str(strip_dir / f"{sid}_strip.jpg"))

        # Full contact sheet — one representative frame per shot
        sheet = Image.new("RGB", (W * 4, H * ((len(self.scenes) + 3) // 4)), PALETTE["SILVER"])
        for i, spec in enumerate(self.scenes):
            dur = spec.duration
            n_frames = max(1, int(dur * FPS))
            ctx = RenderContext(shot_id=spec.shot_id, frame_count=n_frames, output_dir=self.shot_dir)
            u = 0.72
            fi = int(u * (n_frames - 1))
            t_val = fi / FPS
            im = spec.render(ctx, t_val, u)
            col, row = i % 4, i // 4
            sheet.paste(im, (col * W, row * H))

        sheet.save(str(self.output_dir / "contact_sheet.jpg"))
        print(f"  Contact sheet: {self.output_dir / 'contact_sheet.jpg'}")


# ── CLI ────────────────────────────────────────────
if __name__ == "__main__":
    import importlib.util
    pack_path = sys.argv[1] if len(sys.argv) > 1 else "render_pack.py"
    spec = importlib.util.spec_from_file_location("pack", pack_path)
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)

    film = Film(pack.SCENES, output_dir=sys.argv[2] if len(sys.argv) > 2 else "output")
    film.render()
    film.contact_sheet()
    print("Done.")
