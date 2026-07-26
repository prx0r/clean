#!/usr/bin/env python3
"""Compile, audit, and preview the standalone beautify fragment shaders.

Examples:
    python beautify/render_harness.py --audit
    python beautify/render_harness.py --pack 02 --audit
    python beautify/render_harness.py --pack 02 --preview --u 0.72
    python beautify/render_harness.py --pack 03 --shader vis_vagus_highway --preview

ModernGL is imported only for previews. Static audits remain available on machines
without an EGL/OpenGL runtime.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INCLUDE_DIR = ROOT / "include"
PACK_DIRS = {
    "01": ROOT / "glsl-reference",
    "02": ROOT / "02_beliefs_create_biology",
    "03": ROOT / "03_voice_inside_chest",
    "04": ROOT / "04_dreams_create_worlds",
    "05": ROOT / "05_time_is_produced_by_forgetting",
}
UNIFORMS = ("iResolution", "u", "t", "u_audioVolume", "u_audioBeat")
INCLUDE_RE = re.compile(r'^\s*#include\s+"([^"]+)"\s*$', re.MULTILINE)


@dataclass(frozen=True)
class AuditResult:
    shader: Path
    errors: tuple[str, ...]


def shader_paths(pack: str | None = None, shader: str | None = None) -> list[Path]:
    packs = [pack] if pack else ["02", "03", "04", "05"]
    paths: list[Path] = []
    for key in packs:
        directory = PACK_DIRS[key]
        if not directory.exists():
            continue
        paths.extend(sorted(directory.glob("*.glsl")))
    if shader:
        name = shader if shader.endswith(".glsl") else f"{shader}.glsl"
        paths = [path for path in paths if path.name == name]
    return paths


def _include_path(name: str, parent: Path) -> Path:
    candidates = (
        parent / name,
        INCLUDE_DIR / name,
        ROOT / "glsl-reference" / "include" / name,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f'include "{name}" from {parent}')


def resolve_includes(path: Path, stack: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(item.name for item in (*stack, path))
        raise RuntimeError(f"cyclic GLSL include: {chain}")
    source = path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        include = _include_path(match.group(1), path.parent)
        return resolve_includes(include, (*stack, path))

    return INCLUDE_RE.sub(replace, source)


def audit_shader(path: Path) -> AuditResult:
    errors: list[str] = []
    try:
        source = resolve_includes(path)
    except (FileNotFoundError, RuntimeError) as exc:
        return AuditResult(path, (str(exc),))
    own_source = path.read_text(encoding="utf-8")
    if not own_source.lstrip().startswith("#version 330 core"):
        errors.append("missing '#version 330 core' header")
    for uniform in UNIFORMS:
        if not re.search(rf"\buniform\b[^;]*\b{re.escape(uniform)}\b", own_source):
            errors.append(f"missing uniform {uniform}")
    if "out vec4 fragColor" not in own_source:
        errors.append("missing fragColor output")
    if source.count("{") != source.count("}"):
        errors.append("unbalanced braces after include expansion")
    if re.search(r"\btexture2D\s*\(", source):
        errors.append("uses deprecated texture2D in GLSL 330")
    return AuditResult(path, tuple(errors))


def compile_shader(path: Path, compiler: str) -> tuple[bool, str]:
    source = resolve_includes(path)
    with tempfile.NamedTemporaryFile("w", suffix=".frag", encoding="utf-8") as handle:
        handle.write(source)
        handle.flush()
        completed = subprocess.run(
            (compiler, "-S", "frag", handle.name),
            check=False,
            capture_output=True,
            text=True,
        )
    diagnostic = "\n".join(
        item.strip() for item in (completed.stdout, completed.stderr) if item.strip()
    )
    return completed.returncode == 0, diagnostic


class PreviewRenderer:
    VERTEX = """#version 330 core
in vec2 in_position;
void main() { gl_Position=vec4(in_position,0.0,1.0); }
"""

    def __init__(self, width: int, height: int):
        try:
            import moderngl
            import numpy as np
        except ModuleNotFoundError as exc:
            raise SystemExit(
                "Preview rendering needs ModernGL: python -m pip install moderngl"
            ) from exc
        self.moderngl = moderngl
        self.np = np
        try:
            self.ctx = moderngl.create_standalone_context(backend="egl")
        except Exception:
            self.ctx = moderngl.create_standalone_context()
        self.width = width
        self.height = height
        vertices = np.array((-1.0, -1.0, 3.0, -1.0, -1.0, 3.0), dtype="f4")
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.texture = self.ctx.texture((width, height), 4, dtype="f1")
        self.fbo = self.ctx.framebuffer((self.texture,))

    def render(
        self,
        path: Path,
        *,
        u: float,
        t: float,
        audio_volume: float,
        audio_beat: float,
    ):
        from PIL import Image

        program = self.ctx.program(
            vertex_shader=self.VERTEX,
            fragment_shader=resolve_includes(path),
        )
        vao = self.ctx.vertex_array(
            program,
            [(self.vbo, "2f", "in_position")],
        )
        values = {
            "iResolution": (float(self.width), float(self.height)),
            "u": float(u),
            "t": float(t),
            "u_audioVolume": float(audio_volume),
            "u_audioBeat": float(audio_beat),
        }
        for name, value in values.items():
            if name in program:
                program[name].value = value
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        vao.render(mode=self.moderngl.TRIANGLES)
        return Image.frombytes(
            "RGBA",
            (self.width, self.height),
            self.fbo.read(components=4, alignment=1),
        ).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def contact_sheet(images: list[tuple[str, object]], columns: int = 4):
    from PIL import Image, ImageDraw

    if not images:
        raise ValueError("no images")
    thumb_w, thumb_h = images[0][1].size
    label_h = 30
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), "#09070f")
    draw = ImageDraw.Draw(sheet)
    for index, (name, image) in enumerate(images):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(image.convert("RGB"), (x, y))
        draw.text((x + 8, y + thumb_h + 8), name, fill="#e8dfcf")
    return sheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", choices=sorted(PACK_DIRS))
    parser.add_argument("--shader")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument(
        "--compiler",
        help="glslangValidator path (or set GLSLANG_VALIDATOR)",
    )
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--u", type=float, default=0.72)
    parser.add_argument("--t", type=float, default=2.75)
    parser.add_argument("--audio-volume", type=float, default=0.46)
    parser.add_argument("--audio-beat", type=float, default=0.62)
    parser.add_argument("--output", type=Path, default=ROOT / "previews")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    paths = shader_paths(args.pack, args.shader)
    if not paths:
        print("No shaders matched.", file=sys.stderr)
        return 2

    results = [audit_shader(path) for path in paths]
    failed = [result for result in results if result.errors]
    for result in failed:
        for error in result.errors:
            print(f"ERROR {result.shader.relative_to(ROOT)}: {error}", file=sys.stderr)
    print(f"Audit: {len(results)-len(failed)}/{len(results)} shaders passed")
    if failed:
        return 1

    if args.compile:
        compiler = (
            args.compiler
            or os.environ.get("GLSLANG_VALIDATOR")
            or shutil.which("glslangValidator")
        )
        if not compiler:
            print(
                "Compile validation requested but glslangValidator was not found.",
                file=sys.stderr,
            )
            return 2
        compile_failures = []
        for path in paths:
            passed, diagnostic = compile_shader(path, compiler)
            if not passed:
                compile_failures.append(path)
                print(f"COMPILE ERROR {path.relative_to(ROOT)}", file=sys.stderr)
                if diagnostic:
                    print(diagnostic, file=sys.stderr)
        print(f"Compile: {len(paths)-len(compile_failures)}/{len(paths)} shaders passed")
        if compile_failures:
            return 1

    if args.preview:
        renderer = PreviewRenderer(args.width, args.height)
        rendered = []
        for path in paths:
            image = renderer.render(
                path,
                u=args.u,
                t=args.t,
                audio_volume=args.audio_volume,
                audio_beat=args.audio_beat,
            )
            relative = path.relative_to(ROOT)
            destination = args.output / relative.with_suffix(".png")
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination)
            rendered.append((path.stem, image))
            print(f"Rendered {destination}")
        if len(rendered) > 1:
            pack_name = args.pack or "all"
            destination = args.output / f"contact-sheet-{pack_name}.jpg"
            contact_sheet(rendered).save(destination, quality=92)
            print(f"Rendered {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
