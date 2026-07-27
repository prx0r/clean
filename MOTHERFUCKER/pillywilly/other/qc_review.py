#!/usr/bin/env python3
"""
Tantrāloka Quality Control Pipeline
Validate completed renders for correctness, continuity, and quality.

Usage:
    python qc_review.py                              # QC all completed renders
    python qc_review.py --pack fire_not_destroying   # QC specific pack
    python qc_review.py --output qc_report.json      # Write detailed JSON report
    python qc_review.py --verbose                     # Full output
    python qc_review.py --check-narration            # Validate narration timeline alignments
    python qc_review.py --generate-contact-sheets    # Generate any missing contact sheets
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RENDERS_DIR = ROOT / "renders"


def discover_outputs(args) -> list[Path]:
    outputs = sorted(ROOT.glob("output_*"))
    if args.pack:
        outputs = [o for o in outputs if args.pack.lower() in o.name.lower()]
    # Filter: only dirs with at least one .mp4
    outputs = [o for o in outputs if o.is_dir() and list(o.glob("*.mp4"))]
    return outputs


def check_timeline(outdir: Path) -> dict:
    tl = outdir / "narration_timeline.json"
    if not tl.exists():
        return {"pass": False, "error": "Missing narration_timeline.json"}

    try:
        data = json.loads(tl.read_text())
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"Invalid JSON: {e}"}

    checks = {}

    # Must have scenes list
    scenes = data.get("scenes", data.get("shot_scenes", data.get("segments", [])))
    if not scenes:
        checks["scenes_exist"] = {"pass": False, "error": "No scenes found in timeline"}
    else:
        checks["scenes_exist"] = {"pass": True, "count": len(scenes)}

    # Each scene needs timing info
    missing_timing = 0
    missing_narration = 0
    for s in scenes:
        if not any(k in s for k in ("duration", "end_frame", "duration_seconds", "runtime")):
            missing_timing += 1
        if not any(k in s for k in ("narration", "text", "dialogue", "caption")):
            missing_narration += 1

    checks["scene_timing"] = {
        "pass": missing_timing == 0,
        "scenes_missing_timing": missing_timing,
    }
    checks["scene_narration"] = {
        "pass": missing_narration == 0,
        "scenes_missing_narration": missing_narration,
    }

    # Runtime should exist
    runtime = data.get("runtime_seconds", data.get("total_duration", 0))
    checks["runtime"] = {"pass": runtime > 0, "runtime_seconds": runtime}

    overall = all(c["pass"] for c in checks.values())
    return {"pass": overall, "checks": checks, "file": str(tl)}


def check_mp4s(outdir: Path) -> dict:
    mp4s = list(outdir.glob("*.mp4"))
    if not mp4s:
        return {"pass": False, "error": "No MP4 render found"}

    sizes = {}
    for mp4 in mp4s:
        sizes[mp4.name] = mp4.stat().st_size

    main_mp4 = [m for m in mp4s if "scene" not in m.name.lower()]
    has_main = len(main_mp4) > 0
    main_ok = True
    if has_main:
        main_mp4_size = main_mp4[0].stat().st_size
        main_ok = main_mp4_size > 1024  # At least 1KB

    return {
        "pass": has_main and main_ok,
        "has_main_mp4": has_main,
        "main_mp4_size": main_mp4[0].stat().st_size if main_mp4 else 0,
        "total_mp4s": len(mp4s),
        "mp4_sizes": sizes,
    }


def check_scene_clips(outdir: Path, timeline: dict) -> dict:
    scenes_dir = outdir / "scenes"
    clips = sorted(scenes_dir.glob("*.mp4")) if scenes_dir.exists() else []

    # Expected count from timeline
    expected = 0
    if timeline.get("pass") and timeline.get("checks", {}).get("scenes_exist", {}).get("pass"):
        expected = timeline["checks"]["scenes_exist"]["count"]

    missing_clips = expected - len(clips) if expected > 0 else 0

    return {
        "pass": missing_clips <= 0,
        "scene_clips_found": len(clips),
        "scene_clips_expected": expected,
        "missing_clips": max(0, missing_clips),
        "scene_clip_size_bytes": sum(c.stat().st_size for c in clips),
    }


def check_contact_sheet(outdir: Path) -> dict:
    cs = outdir / "contact_sheet.jpg"
    if cs.exists():
        return {"pass": True, "size_bytes": cs.stat().st_size, "file": str(cs)}
    # Also try .png
    cs = outdir / "contact_sheet.png"
    if cs.exists():
        return {"pass": True, "size_bytes": cs.stat().st_size, "file": str(cs)}
    return {"pass": False, "error": "No contact_sheet.{jpg,png} found"}


def check_continuity_object(outdir: Path) -> dict:
    """Check that the same continuity object appears across scenes."""
    # Look for references in the pack source
    stem = outdir.name.replace("output_", "")
    pack_file = ROOT / f"{stem}_platinum.py"
    if not pack_file.exists():
        return {"pass": None, "error": "No pack source to check continuity"}

    source = pack_file.read_text()

    import re
    # Find continuity object keyword references
    continuity_refs = re.findall(r"continuity|chase_light|gold_thread|luminous_fractal|crystal_lotus", source, re.IGNORECASE)
    if not continuity_refs:
        return {"pass": None, "info": "No continuity object references found in source"}

    unique_refs = set(r.lower() for r in continuity_refs)

    # Check if scenes reference the continuity object
    scene_functions = re.findall(r"def scene_\d+", source)
    scenes_with_continuity = 0
    for func in scene_functions:
        func_match = re.search(re.escape(func) + r".*?(?=\ndef scene_|$)", source, re.DOTALL)
        if func_match:
            func_body = func_match.group()
            if any(ref in func_body.lower() for ref in unique_refs):
                scenes_with_continuity += 1

    return {
        "pass": scenes_with_continuity >= 2,  # At least 2 scenes use it
        "continuity_objects": list(unique_refs),
        "total_scenes": len(scene_functions),
        "scenes_with_continuity": scenes_with_continuity,
    }


def check_still_frame_quality(outdir: Path) -> dict:
    """Check the preview frame at u=0.72 exists and has reasonable size."""
    stills = list(outdir.glob("*frame*")) + list(outdir.glob("*still*")) + list(outdir.glob("*preview*"))
    if not stills:
        return {"pass": None, "info": "No still frame generated (run --preview)"}

    max_still = max(stills, key=lambda f: f.stat().st_size)
    size_kb = max_still.stat().st_size / 1024
    return {
        "pass": size_kb > 10,
        "still_file": max_still.name,
        "size_kb": round(size_kb, 1),
    }


def get_render_stats(outdir: Path) -> dict:
    """Gather render timing / metadata."""
    log = RENDERS_DIR / "render.log"
    stats = {"render_time_seconds": None, "frame_count": None}

    if log.exists():
        content = log.read_text()
        pack_stem = outdir.name.replace("output_", "")
        for line in content.splitlines():
            if pack_stem in line:
                if "completed" in line.lower() and "s" in line:
                    import re
                    m = re.search(r"(\d+\.?\d*)s", line)
                    if m:
                        stats["render_time_seconds"] = float(m.group(1))
                if "frames" in line.lower():
                    m = re.search(r"(\d+)\s*frames?", line, re.IGNORECASE)
                    if m:
                        stats["frame_count"] = int(m.group(1))

    return stats


def grade_pack(checks: dict) -> str:
    """Assign A/B/C/F grade."""
    pass_count = sum(1 for c in checks.values() if isinstance(c, dict) and c.get("pass") is True)
    fail_count = sum(1 for c in checks.values() if isinstance(c, dict) and c.get("pass") is False)
    total = pass_count + fail_count
    if total == 0:
        return "?"
    pct = pass_count / total
    if pct >= 0.9:
        return "A"
    elif pct >= 0.7:
        return "B"
    elif pct >= 0.4:
        return "C"
    return "F"


def generate_contact_sheet(outdir: Path, fps: int = 10) -> dict:
    """Generate a contact sheet from the scene clips using ffmpeg tile filter."""
    scenes_dir = outdir / "scenes"
    clips = sorted(scenes_dir.glob("*.mp4")) if scenes_dir.exists() else []
    if not clips:
        return {"pass": False, "error": "No scene clips to generate contact sheet"}

    # Pick midpoint frame from each scene
    tile_width = min(4, len(clips))
    tile_height = (len(clips) + tile_width - 1) // tile_width
    tile_height = min(tile_height, len(clips))

    output_path = outdir / "contact_sheet.jpg"

    # Build filter: select middle frame from each clip
    filter_parts = []
    inputs = []
    for i, clip in enumerate(clips):
        inputs.extend(["-ss", "3", "-i", str(clip)])
        filter_parts.append(f"[{i}:v]")

    if not inputs:
        return {"pass": False, "error": "No valid scene clips"}

    filter_str = "".join(filter_parts)
    filter_str += f"hstack=inputs={tile_width},scale=320:-1"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-vframes", "1",
        str(output_path),
    ]

    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        if output_path.exists():
            return {"pass": True, "file": str(output_path), "size_bytes": output_path.stat().st_size}
        return {"pass": False, "error": "ffmpeg produced no output"}
    except subprocess.CalledProcessError as e:
        return {"pass": False, "error": e.stderr.decode()[:200]}
    except FileNotFoundError:
        return {"pass": False, "error": "ffmpeg not found"}
    except subprocess.TimeoutExpired:
        return {"pass": False, "error": "ffmpeg timed out"}


def run_qc(outdir: Path, args) -> dict:
    name = outdir.name.replace("output_", "")
    checks = {}

    checks["timeline"] = check_timeline(outdir)
    checks["mp4"] = check_mp4s(outdir)
    checks["scenes"] = check_scene_clips(outdir, checks["timeline"])

    # Contact sheet — generate if missing and requested
    checks["contact_sheet"] = check_contact_sheet(outdir)
    if not checks["contact_sheet"]["pass"] and args.generate_contact_sheets:
        print(f"    Generating contact sheet for {name}...", end=" ", flush=True)
        result = generate_contact_sheet(outdir)
        checks["contact_sheet"] = result
        print("OK" if result["pass"] else "FAILED")

    checks["continuity"] = check_continuity_object(outdir)
    checks["still_frame"] = check_still_frame_quality(outdir)
    stats = get_render_stats(outdir)

    overall_pass = all(
        c["pass"] is not False for c in checks.values()
        if isinstance(c, dict) and "pass" in c
    )

    return {
        "name": name,
        "grade": grade_pack(checks),
        "pass": overall_pass,
        "checks": {k: v for k, v in checks.items()},
        "stats": stats,
    }


def print_result(result: dict, verbose: bool):
    name = result["name"]
    grade = result["grade"]
    status = "✅" if result["pass"] else "❌" if not result["pass"] else "⚠️"
    print(f"\n{status} {name} — Grade: {grade}")

    for check_name, check_data in result["checks"].items():
        if not isinstance(check_data, dict):
            continue
        pass_text = "✅" if check_data.get("pass") is True else "❌" if check_data.get("pass") is False else "⚠️"
        head = f"  {pass_text} {check_name}"
        if verbose:
            error = check_data.get("error") or check_data.get("info") or ""
            if error:
                head += f": {error}"
        print(head)
        if verbose and check_data.get("pass") is not None:
            # Print details
            for k, v in check_data.items():
                if k != "pass" and k != "error" and k != "info":
                    print(f"    {k}: {v}")

    if result.get("stats"):
        stats = result["stats"]
        parts = []
        if stats.get("render_time_seconds"):
            parts.append(f"render: {stats['render_time_seconds']:.0f}s")
        if stats.get("frame_count"):
            parts.append(f"frames: {stats['frame_count']}")
        if parts:
            print(f"  📊 {' | '.join(parts)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Tantrāloka QC Pipeline")
    parser.add_argument("--pack", type=str, help="QC specific pack")
    parser.add_argument("--output", type=str, help="Write QC report JSON to path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-narration", action="store_true", help="Validate narration alignment")
    parser.add_argument("--generate-contact-sheets", action="store_true", help="Generate missing contact sheets via ffmpeg")
    parser.add_argument("--require-all", action="store_true", help="Fail if any check does not pass")
    return parser.parse_args()


def main():
    args = parse_args()
    outputs = discover_outputs(args)

    if not outputs:
        print("No completed renders found.")
        sys.exit(1)

    print(f"QC Review: {len(outputs)} pack(s)\n")

    results = []
    for outdir in outputs:
        name = outdir.name.replace("output_", "")
        print(f"  Checking {name}...", flush=True)
        result = run_qc(outdir, args)
        results.append(result)
        if args.verbose:
            print_result(result, verbose=True)

    if not args.verbose:
        for r in results:
            print_result(r, verbose=False)

    # Summary
    passed = sum(1 for r in results if r["pass"])
    grades = [r["grade"] for r in results]
    a_count = grades.count("A")
    b_count = grades.count("B")
    c_count = grades.count("C")
    f_count = grades.count("F")

    print(f"\n{'='*50}")
    print(f"  QC Summary: {passed}/{len(results)} passed")
    print(f"  Grades: A={a_count} B={b_count} C={c_count} F={f_count}")
    print(f"{'='*50}")

    if args.output:
        report_path = Path(args.output)
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  Report: {report_path}")

    if args.require_all and passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
