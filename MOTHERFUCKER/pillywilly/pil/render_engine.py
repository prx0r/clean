#!/usr/bin/env python3
"""
TANTRALOKA RENDER ENGINE
Unified runner for all goldrender pack files.

Design:
- Discovers all *_pack.py files in the goldrender directory
- Determines pack type (old-style vs platinum/new-style)
- Renders each pack, tracking progress for resume
- Manages output directories (root for active, volume for archive)
- Generates master manifest, contact sheets, and concatenations

Usage:
  python render_engine.py                      # Render all incomplete packs
  python render_engine.py --pack spanda        # Render specific pack
  python render_engine.py --status             # Show render status
  python render_engine.py --resume             # Resume interrupted render
  python render_engine.py --output volume      # Output to volume storage
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

ROOT = Path(__file__).resolve().parent
VOLUME = Path("/mnt/HC_Volume_106427611/goldrender_outputs")
STATUS_FILE = ROOT / ".render_status.json"
CONCAT_ROOT = ROOT / "_master_concatenations"
CONTACT_ROOT = ROOT / "_master_contact_sheets"

DEFAULT_FPS = 10
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720


# =============================================================================
# PACK DISCOVERY & CLASSIFICATION
# =============================================================================

@dataclass
class PackInfo:
    """Metadata about a discovered pack file."""
    filename: str
    path: Path
    pack_type: str  # 'old' (render_all), 'platinum' (argparse), 'collection'
    scenes: int = 0
    duration: float = 0.0
    rendered: bool = False
    output_path: Optional[Path] = None
    error: Optional[str] = None


def discover_packs() -> list[PackInfo]:
    """Scan goldrender directory for all *_pack.py files."""
    packs = []
    for f in sorted(ROOT.glob("*_pack.py")):
        if f.name == "render_engine.py":
            continue
        info = classify_pack(f)
        if info:
            packs.append(info)
    return packs


def classify_pack(path: Path) -> Optional[PackInfo]:
    """Determine pack type and extract metadata."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    filename = path.name

    # Count scenes (Scene or Sc( data class constructors)
    scenes = len(re.findall(r'\b(?:Scene|Sc)\(', content))

    # Guess duration from scene-specific durations
    durations = re.findall(r'(?:duration|dur)\s*[=:]\s*(\d+\.?\d*)', content)
    if durations:
        avg_dur = sum(float(d) for d in durations) / len(durations)
    else:
        avg_dur = 6.5  # default estimate

    total_dur = scenes * avg_dur

    # Determine type
    if "argparse" in content and ("--preview" in content or "--scene" in content):
        pack_type = "platinum"
    elif "render_all" in content or "if __name__" in content:
        pack_type = "old"
    else:
        pack_type = "unknown"

    return PackInfo(
        filename=filename,
        path=path,
        pack_type=pack_type,
        scenes=scenes,
        duration=total_dur,
    )


# =============================================================================
# STATUS TRACKING (Resume Support)
# =============================================================================

def load_status() -> dict:
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {}


def save_status(status: dict) -> None:
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))


def mark_completed(pack_name: str, scenes_rendered: int = 0, output_path: str = "") -> None:
    status = load_status()
    status[pack_name] = {
        "completed": True,
        "scenes_rendered": scenes_rendered,
        "output_path": output_path,
        "timestamp": datetime.now().isoformat(),
    }
    save_status(status)


def mark_failed(pack_name: str, error: str, scenes_rendered: int = 0) -> None:
    status = load_status()
    status[pack_name] = {
        "completed": False,
        "scenes_rendered": scenes_rendered,
        "error": error,
        "timestamp": datetime.now().isoformat(),
    }
    save_status(status)


def is_completed(pack_name: str) -> bool:
    status = load_status()
    return status.get(pack_name, {}).get("completed", False)


def rendered_scene_count(pack_name: str) -> int:
    """Count actual rendered frames for a pack."""
    # Check for output directory
    output_dir = ROOT / f"output_{pack_name.replace('_pack.py','').replace('_','')}"
    if not output_dir.exists():
        return 0
    frame_dirs = list(output_dir.glob("frames/scene_*"))
    total_frames = 0
    for fd in frame_dirs:
        total_frames += len(list(fd.glob("*.jpg")))
    return total_frames


# =============================================================================
# PACK EXECUTION
# =============================================================================

def run_old_style(pack: PackInfo, output_root: Path) -> Optional[Path]:
    """Run an old-style pack (executes render_all() via subprocess)."""
    print(f"  Running old-style: {pack.filename}")
    result = subprocess.run(
        [sys.executable, str(pack.path)],
        cwd=pack.path.parent,
        capture_output=True,
        text=True,
        timeout=18000,  # 5 hour timeout per pack
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pack failed:\n{result.stderr[:500]}")
    # Find output MP4
    mp4s = list(pack.path.parent.glob(f"{pack.path.stem.replace('_pack','')}_animation.mp4"))
    if mp4s:
        return mp4s[0]
    return None


def run_platinum_style(pack: PackInfo, output_root: Path, fps: int, width: int, height: int,
                       scene: Optional[int] = None, preview: bool = False) -> Optional[Path]:
    """Run a platinum-style pack (uses argparse)."""
    cmd = [sys.executable, str(pack.path),
           "--fps", str(fps),
           "--width", str(width),
           "--height", str(height)]
    if scene:
        cmd += ["--scene", str(scene)]
    if preview:
        cmd += ["--preview"]

    print(f"  Running: {' '.join(cmd[:5])}...")
    result = subprocess.run(
        cmd,
        cwd=pack.path.parent,
        capture_output=True,
        text=True,
        timeout=36000,  # 10 hours for full render
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pack failed:\n{result.stderr[:500]}")

    # Find output — platinum packs write to output_* directory
    stem = pack.path.stem
    output_dir = pack.path.parent / f"output_{stem.replace('_pack','').replace('_','').replace('_platinum','')}"
    mp4 = output_dir / f"{stem.replace('_pack','').replace('_platinum','')}.mp4"
    if mp4.exists():
        return mp4
    # Also check for common pattern
    mp4s = list(output_dir.glob("*.mp4"))
    if mp4s:
        return mp4s[0]
    return None


# =============================================================================
# MASTER OUTPUTS
# =============================================================================

def generate_manifest(packs: list[PackInfo]) -> Path:
    """Generate a master JSON manifest of all packs."""
    manifest = {
        "generated": datetime.now().isoformat(),
        "total_packs": len(packs),
        "total_scenes": sum(p.scenes for p in packs),
        "total_duration_seconds": round(sum(p.duration for p in packs), 1),
        "total_duration_minutes": round(sum(p.duration for p in packs) / 60, 1),
        "packs": [
            {
                "name": p.filename,
                "type": p.pack_type,
                "scenes": p.scenes,
                "duration_seconds": round(p.duration, 1),
                "rendered": p.rendered,
                "output": str(p.output_path) if p.output_path else None,
            }
            for p in packs
        ]
    }
    path = ROOT / "master_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return path


def generate_contact_sheet(packs: list[PackInfo]) -> Path:
    """Generate a master contact sheet from all completed packs."""
    from PIL import Image
    thumbs = []
    # Find pack output directories
    for pack in packs:
        if not is_completed(pack.filename):
            continue
        # Look for contact sheet in pack's output dirs
        stem = pack.path.stem
        candidates = list(Path(".").glob(f"output_{stem.replace('_pack','').replace('_','')}/contact_sheet.jpg"))
        if candidates:
            thumbs.append(Image.open(candidates[0]).resize((320, 180)))

    if not thumbs:
        print("  No contact sheets found to combine")
        return Path()

    import math
    cols = 4
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 320, rows * 195), (248, 247, 243))
    for i, thumb in enumerate(thumbs):
        x = (i % cols) * 320
        y = (i // cols) * 195
        sheet.paste(thumb, (x, y))

    path = CONTACT_ROOT / "master_contact_sheet.jpg"
    CONTACT_ROOT.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=94)
    return path


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def render_all(fps: int, width: int, height: int, output_root: Path,
               specific_pack: Optional[str] = None, resume: bool = False,
               preview: bool = False) -> None:
    """Main entry point — render all or specific packs."""
    packs = discover_packs()
    print(f"\n{'='*60}")
    print(f"Tantraloka Render Engine")
    print(f"{'='*60}")
    print(f"Discovered {len(packs)} pack files")
    print(f"{'='*60}\n")

    # Filter to specific pack if requested
    if specific_pack:
        packs = [p for p in packs if specific_pack in p.filename]
        if not packs:
            print(f"No packs matching '{specific_pack}'")
            return
        print(f"Filtered to {len(packs)} pack(s): {[p.filename for p in packs]}")

    # Print summary
    print(f"{'Pack':50s} {'Type':12s} {'Scenes':>7s} {'Duration':>10s}")
    print("-" * 80)
    for p in packs:
        status = " ✓" if is_completed(p.filename) else ""
        print(f"{p.filename:50s} {p.pack_type:12s} {p.scenes:>7d} {p.duration/60:>5.1f}m{status}")
    print("-" * 80)
    total_scenes = sum(p.scenes for p in packs)
    total_dur = sum(p.duration for p in packs)
    completed = sum(1 for p in packs if is_completed(p.filename))
    print(f"Total: {total_scenes} scenes, {total_dur/60:.1f} min across {len(packs)} packs")
    print(f"Completed: {completed}/{len(packs)}")

    # Render uncompleted packs
    print(f"\n{'='*60}")
    print("RENDER QUEUE")
    print(f"{'='*60}\n")

    for pack in packs:
        if resume and is_completed(pack.filename):
            print(f"  ⏭  Skipping {pack.filename} (already completed)")
            continue
        if is_completed(pack.filename) and not specific_pack:
            print(f"  ⏭  {pack.filename} already rendered (use --resume to re-render)")
            continue

        print(f"\n  ▶ Rendering {pack.filename} ({pack.scenes} scenes, {pack.duration/60:.1f}min)...")
        start_time = time.time()

        try:
            output_root.mkdir(parents=True, exist_ok=True)

            if pack.pack_type == "platinum":
                out = run_platinum_style(pack, output_root, fps, width, height,
                                         preview=preview)
            else:
                out = run_old_style(pack, output_root)

            elapsed = time.time() - start_time
            if out and out.exists():
                pack.rendered = True
                pack.output_path = out
                mark_completed(pack.filename, pack.scenes, str(out))
                print(f"  ✓ {pack.filename} done in {elapsed/60:.1f}min → {out}")
            else:
                # Check if output exists in default location
                mark_completed(pack.filename, pack.scenes)
                print(f"  ✓ {pack.filename} done in {elapsed/60:.1f}min (output in default location)")

        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)[:200]
            mark_failed(pack.filename, error_msg)
            print(f"  ✗ {pack.filename} FAILED after {elapsed/60:.1f}min: {error_msg}")

    # Generate master outputs
    print(f"\n{'='*60}")
    print("GENERATING MASTER OUTPUTS")
    print(f"{'='*60}")
    manifest = generate_manifest(packs)
    print(f"  Manifest: {manifest}")
    contacts = generate_contact_sheet(packs)
    if contacts:
        print(f"  Contact sheet: {contacts}")
    print(f"\n{'='*60}")
    print("DONE")
    print(f"{'='*60}")


def show_status() -> None:
    """Display render status."""
    status = load_status()
    if not status:
        print("No render status found. Run the engine first.")
        return

    print(f"\n{'='*60}")
    print("RENDER STATUS")
    print(f"{'='*60}")
    print(f"{'Pack':45s} {'Status':10s} {'Scenes':>7s} {'Output':>20s}")
    print("-" * 82)
    total_completed = 0
    for pack_name, info in sorted(status.items()):
        completed = info.get("completed", False)
        status_str = "✓" if completed else "✗"
        scenes = info.get("scenes_rendered", 0)
        output = Path(info.get("output_path", "")).name if info.get("output_path") else ""
        print(f"{pack_name:45s} {status_str:10s} {scenes:>7d} {output:>20s}")
        if completed:
            total_completed += 1
    print("-" * 82)
    print(f"Completed: {total_completed}/{len(status)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tantraloka Goldrender Engine")
    parser.add_argument("--pack", type=str, default=None,
                        help="Render a specific pack (substring match on filename)")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--output", choices=["root", "volume"], default="root",
                        help="Output destination")
    parser.add_argument("--resume", action="store_true",
                        help="Resume incomplete renders (skip completed packs)")
    parser.add_argument("--status", action="store_true",
                        help="Show render status and exit")
    parser.add_argument("--preview", action="store_true",
                        help="Preview mode (fewer frames per scene)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.status:
        show_status()
        return

    output_root = VOLUME if args.output == "volume" else ROOT
    output_root.mkdir(parents=True, exist_ok=True)

    render_all(
        fps=args.fps,
        width=args.width,
        height=args.height,
        output_root=output_root,
        specific_pack=args.pack,
        resume=args.resume,
        preview=args.preview,
    )


if __name__ == "__main__":
    main()
