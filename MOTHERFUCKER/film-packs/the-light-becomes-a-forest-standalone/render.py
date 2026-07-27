#!/usr/bin/env python3
"""Render stills, review sheets, or intervals from the contrapuntal forest."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from engine import ROOT, frame_state, load_composition, seconds_to_clock

REPO_ROOT = ROOT.parent.parent
LIB_DIR = REPO_ROOT / "beautify-archive" / "lib"
SHADER = ROOT / "glsl" / "film.glsl"
INCLUDE_RE = re.compile(r'^\s*#include\s+"([^"]+)"\s*$', re.MULTILINE)


def resolve_includes(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        raise RuntimeError(
            "cyclic include: " + " -> ".join(item.name for item in (*stack, path))
        )
    source = path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        candidates = (
            path.parent / name,
            path.parent / "include" / name,
            LIB_DIR / name,
            LIB_DIR / Path(name).name,
        )
        include = next((candidate for candidate in candidates if candidate.exists()), None)
        if include is None:
            raise FileNotFoundError(f'include "{name}" from {path}')
        return resolve_includes(include, (*stack, path))

    return INCLUDE_RE.sub(replace, source)


class Renderer:
    VERTEX = """#version 330 core
in vec2 in_position;
void main() { gl_Position=vec4(in_position,0.0,1.0); }
"""

    def __init__(self, width: int, height: int):
        try:
            import moderngl
        except ModuleNotFoundError as exc:
            raise SystemExit(
                "ModernGL is required. Install it or add its target directory "
                "to PYTHONPATH."
            ) from exc
        self.moderngl = moderngl
        self.width = width
        self.height = height
        try:
            self.ctx = moderngl.create_standalone_context(backend="egl")
        except Exception:
            self.ctx = moderngl.create_standalone_context()
        self.program = self.ctx.program(
            vertex_shader=self.VERTEX,
            fragment_shader=resolve_includes(SHADER),
        )
        vertices = np.array(
            (-1.0, -1.0, 3.0, -1.0, -1.0, 3.0),
            dtype="f4",
        )
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f", "in_position")],
        )
        self.texture = self.ctx.texture((width, height), 4, dtype="f1")
        self.fbo = self.ctx.framebuffer((self.texture,))

    def render(self, composition: dict, seconds: float) -> Image.Image:
        state = frame_state(composition, seconds)
        values = {
            "iResolution": (float(self.width), float(self.height)),
            "u": state.progress,
            "t": state.seconds,
            "u_audioVolume": state.audio_volume,
            "u_audioBeat": state.audio_beat,
            "u_stateA": state.vector[:4],
            "u_stateB": state.vector[4:],
            "u_musicA": state.music_a,
            "u_musicB": state.music_b,
            "u_stage": float(state.stage),
            "u_local": state.local,
            "u_tattva": state.tattva_open,
        }
        for name, value in values.items():
            if name in self.program:
                self.program[name].value = value
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render(mode=self.moderngl.TRIANGLES)
        return Image.frombytes(
            "RGBA",
            (self.width, self.height),
            self.fbo.read(components=4, alignment=1),
        ).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def review_times(composition: dict, fraction: float) -> list[tuple[str, float]]:
    waypoints = composition["waypoints"]
    result = []
    for left, right in zip(waypoints, waypoints[1:]):
        start, end = float(left["time"]), float(right["time"])
        seconds = start + (end - start) * fraction
        result.append((left["title"], seconds))
    return result


def contact_sheet(
    frames: list[tuple[str, float, Image.Image]],
    *,
    columns: int = 3,
) -> Image.Image:
    thumb_width, thumb_height = frames[0][2].size
    label_height = 42
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * thumb_width, rows * (thumb_height + label_height)),
        "#070713",
    )
    draw = ImageDraw.Draw(sheet)
    for index, (title, seconds, frame) in enumerate(frames):
        x = (index % columns) * thumb_width
        y = (index // columns) * (thumb_height + label_height)
        sheet.paste(frame.convert("RGB"), (x, y))
        draw.text(
            (x + 9, y + thumb_height + 7),
            f"{seconds_to_clock(seconds)}  {title}",
            fill="#ece9df",
        )
    return sheet


def render_review_sheets(
    renderer: Renderer,
    composition: dict,
    output: Path,
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    samples = {
        "opening": 0.08,
        "mature": 0.58,
        "transition": 0.91,
    }
    for label, fraction in samples.items():
        frames = [
            (title, seconds, renderer.render(composition, seconds))
            for title, seconds in review_times(composition, fraction)
        ]
        path = output / f"contact-{label}.png"
        contact_sheet(frames).save(path)
        print(path)


def render_video(
    renderer: Renderer,
    composition: dict,
    *,
    start: float,
    end: float,
    fps: int,
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{renderer.width}x{renderer.height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    if process.stdin is None:
        raise RuntimeError("ffmpeg stdin did not open")
    frame_count = round((end - start) * fps)
    try:
        for index in range(frame_count):
            seconds = start + index / fps
            frame = renderer.render(composition, seconds).convert("RGB")
            process.stdin.write(frame.tobytes())
            if index and index % (fps * 10) == 0:
                print(
                    f"rendered {index / fps:.0f}s / {end - start:.0f}s",
                    flush=True,
                )
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(output)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    mode = result.add_mutually_exclusive_group(required=True)
    mode.add_argument("--frame", type=float, help="render one time in seconds")
    mode.add_argument("--contact-sheet", action="store_true")
    mode.add_argument("--video", action="store_true")
    result.add_argument("--start", type=float, default=0.0)
    result.add_argument("--end", type=float)
    result.add_argument("--fps", type=int, default=24)
    result.add_argument("--width", type=int, default=640)
    result.add_argument("--height", type=int, default=360)
    result.add_argument("--output", type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    composition = load_composition()
    renderer = Renderer(args.width, args.height)
    if args.frame is not None:
        output = args.output or ROOT / "build" / f"frame-{args.frame:06.1f}.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        renderer.render(composition, args.frame).save(output)
        print(output)
        return 0
    if args.contact_sheet:
        output = args.output or ROOT / "build"
        render_review_sheets(renderer, composition, output)
        return 0
    end = args.end if args.end is not None else float(composition["duration_seconds"])
    if not 0.0 <= args.start < end <= float(composition["duration_seconds"]):
        raise SystemExit("video interval is outside the composition")
    output = args.output or ROOT / "build" / f"film-{args.start:g}-{end:g}.mp4"
    render_video(
        renderer,
        composition,
        start=args.start,
        end=end,
        fps=args.fps,
        output=output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
