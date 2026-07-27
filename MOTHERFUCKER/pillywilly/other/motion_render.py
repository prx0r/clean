#!/usr/bin/env python3
"""
Motion render — turns pack keyframes into cinematic narrated video using ffmpeg zoompan + xfade.
~2-5 min per pack, looks like real production.

Usage:
    python motion_render.py output_life_crosses/
    python motion_render.py output_life_crosses/ --fps 30 --quality medium
"""
import argparse, json, shlex, shutil, subprocess, sys, math, asyncio
from pathlib import Path


def require_ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found")
    return exe


def load_timeline(output_dir: Path):
    tl = output_dir / "narration_timeline.json"
    if not tl.exists():
        raise FileNotFoundError(f"Timeline not found: {tl}")
    return json.loads(tl.read_text())


def generate_scene_clip(still_dir: Path, scene_dur: float, fps: int, out_path: Path, quality: str):
    """Create a Ken Burns scene from 4 stills using zoompan + concat."""
    ffmpeg = require_ffmpeg()
    stills = sorted(still_dir.glob("still_*.jpg"))
    if len(stills) < 2:
        return None

    seg_dur = scene_dur / len(stills)
    n = len(stills)
    
    cmd = [ffmpeg, "-y"]
    for still in stills:
        cmd.extend(["-loop", "1", "-i", str(still)])
    
    n = len(stills)
    # Build filter: each input gets zoompan, then concat
    filter_parts = []
    for i in range(n):
        dur = seg_dur
        z = "1+(0.12*on/" + str(int(dur*fps)) + ")" if i % 2 == 0 else "1.12-(0.12*on/" + str(int(dur*fps)) + ")"
        filter_parts.append(
            f"[{i}:v]zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*fps)}:s=1280x720,fps={fps}[v{i}]"
        )
    
    # Concat all zoomed segments
    concat_inputs = "".join(f"[v{i}]" for i in range(n))
    filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=0,format=yuv420p[v]")
    
    filter_complex = ";".join(filter_parts)
    
    preset = "slow" if quality == "high" else "medium"
    crf = 18 if quality == "high" else 23
    
    cmd.extend(["-filter_complex", filter_complex, "-map", "[v]",
                 "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                 "-pix_fmt", "yuv420p", "-r", str(fps), str(out_path)])
    
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def mux_audio(video_path: Path, audio_path: Path, out_path: Path):
    ffmpeg = require_ffmpeg()
    subprocess.run(
        [ffmpeg, "-y", "-i", str(video_path), "-i", str(audio_path),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(out_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def concat_videos(paths: list[Path], out_path: Path):
    ffmpeg = require_ffmpeg()
    concat_txt = out_path.parent / "_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve()}'" for p in paths))
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_txt), "-c", "copy", "-movflags", "+faststart",
         str(out_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def get_audio_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=15,
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def parse_args():
    parser = argparse.ArgumentParser(description="Motion render from keyframes")
    parser.add_argument("output_dir", type=str, help="Pack output directory")
    parser.add_argument("--fps", type=int, default=24, help="Output framerate (default 24)")
    parser.add_argument("--quality", choices=["draft", "medium", "high"], default="medium")
    parser.add_argument("--no-audio", action="store_true", help="Skip audio mux")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    timeline = load_timeline(output_dir)
    scenes = timeline.get("scenes", [])
    frames_dir = output_dir / "frames"
    scenes_out = output_dir / "scenes_motion"
    scenes_out.mkdir(exist_ok=True)

    print(f"Motion render: {timeline.get('title', output_dir.name)}")
    print(f"  {len(scenes)} scenes @ {args.fps}fps, quality={args.quality}")

    rendered = []
    for i, scene in enumerate(scenes, 1):
        still_dir = frames_dir / f"scene_{i:03d}"
        if not still_dir.exists():
            print(f"  [{i:02d}/{len(scenes):02d}] SKIP — no keyframes in {still_dir.name}")
            continue
        
        dur = scene.get("duration", 6.0)
        out = scenes_out / f"scene_{i:03d}.mp4"
        if out.exists():
            rendered.append(out)
            continue

        generate_scene_clip(still_dir, dur, args.fps, out, args.quality)
        rendered.append(out)
        print(f"  [{i:02d}/{len(scenes):02d}] {scene.get('title',''):30s} {dur:.1f}s")

    if not rendered:
        print("No scenes rendered")
        return

    # Concatenate
    final_raw = output_dir / "life_crosses_barriers_motion.mp4"
    concat_videos(rendered, final_raw)
    print(f"\n  Raw: {final_raw}")

    # Mux audio
    if not args.no_audio:
        audio = output_dir / "narration" / "narration_full.wav"
        if audio.exists():
            final = output_dir / "life_crosses_barriers_narrated.mp4"
            mux_audio(final_raw, audio, final)
            print(f"  Narrated: {final}")
        else:
            print(f"  No audio found at {audio}")

    # Upload
    print("\n  Publish with:")
    print(f"  python publish_pipeline.py {shlex.quote(str(output_dir))} --slug life-crosses-barriers --narrated")


if __name__ == "__main__":
    main()
