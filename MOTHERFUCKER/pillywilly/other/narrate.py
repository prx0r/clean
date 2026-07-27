#!/usr/bin/env python3
"""
Narrate — add edge-tts narration to a rendered platinum pack.

Usage:
    python narrate.py output_life_crosses/
    python narrate.py output_life_crosses/ --voice en-US-GuyNeural
    python narrate.py output_life_crosses/ --scene 5
    python narrate.py output_life_crosses/ --dry-run
    python narrate.py output_life_crosses/ --keep-audio
"""
import argparse, asyncio, json, shutil, subprocess, sys
from pathlib import Path


def require_ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found on PATH")
    return exe


def get_audio_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=15,
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def ensure_narration_dir(output_dir: Path) -> Path:
    nd = output_dir / "narration"
    nd.mkdir(parents=True, exist_ok=True)
    return nd


async def generate_scene_audio(text: str, voice: str, output_path: Path) -> float:
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(output_path))
    return get_audio_duration(output_path)


def build_audio_list(nd: Path, scenes: list[dict]) -> Path:
    """Build concat file and return the combined WAV path."""
    combined = nd / "narration_full.wav"
    # Already built?
    if combined.exists():
        return combined

    files = sorted(nd.glob("scene_*.wav"))
    if not files:
        raise RuntimeError("No scene audio files found")

    # Build a concat demuxer file
    concat_txt = nd / "concat.txt"
    lines = [f"file '{f.resolve()}'" for f in files]
    concat_txt.write_text("\n".join(lines))

    ffmpeg = require_ffmpeg()
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_txt),
         "-c", "copy", str(combined)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return combined


def mux_audio(mp4_path: Path, audio_path: Path, output_path: Path) -> Path:
    """Mux audio into the video, trimming/padding to match."""
    ffmpeg = require_ffmpeg()
    subprocess.run(
        [ffmpeg, "-y",
         "-i", str(mp4_path),
         "-i", str(audio_path),
         "-c:v", "copy",
         "-c:a", "aac",
         "-b:a", "192k",
         "-shortest",
         "-movflags", "+faststart",
         str(output_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return output_path


def mux_single_scene(scene_idx: int, scenes_dir: Path, audio_path: Path, output_dir: Path) -> Path:
    """Mux a single scene clip with its audio."""
    mp4 = scenes_dir / f"scene_{scene_idx:03d}.mp4"
    if not mp4.exists():
        raise FileNotFoundError(f"Missing scene MP4: {mp4}")

    out = output_dir / f"scene_{scene_idx:03d}_narrated.mp4"
    ffmpeg = require_ffmpeg()
    subprocess.run(
        [ffmpeg, "-y",
         "-i", str(mp4),
         "-i", str(audio_path),
         "-c:v", "copy",
         "-c:a", "aac",
         "-b:a", "192k",
         "-shortest",
         "-movflags", "+faststart",
         str(out)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def load_timeline(output_dir: Path) -> dict:
    """Load narration_timeline.json from the output directory."""
    tl = output_dir / "narration_timeline.json"
    if not tl.exists():
        raise FileNotFoundError(f"Timeline not found: {tl}")
    return json.loads(tl.read_text())


def find_main_mp4(output_dir: Path) -> Path | None:
    """Find the main combined MP4 in the output directory."""
    # Common names
    for name in ["life_crosses_barriers.mp4", "final.mp4", "output.mp4"]:
        p = output_dir / name
        if p.exists():
            return p
    # Fallback: any non-scene MP4 in root
    mp4s = sorted(output_dir.glob("*.mp4"))
    for mp4 in mp4s:
        if "scene" not in mp4.name.lower():
            return mp4
    return None


async def narrate_pack(output_dir: Path, args) -> dict:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    timeline = load_timeline(output_dir)
    scenes = timeline.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes found in timeline")

    title = timeline.get("title", output_dir.name)
    voice = args.voice
    nd = ensure_narration_dir(output_dir)

    print(f"Narrating: {title}")
    print(f"  Scenes: {len(scenes)}")
    print(f"  Runtime: {timeline.get('runtime_seconds', 0):.1f}s")
    print(f"  Voice: {voice}")
    print()

    # Generate per-scene audio
    audio_files = []
    total_generated = 0.0
    for i, scene in enumerate(scenes, 1):
        wav_path = nd / f"scene_{i:03d}.wav"
        if wav_path.exists():
            dur = get_audio_duration(wav_path)
            audio_files.append({"index": i, "path": wav_path, "duration": dur,
                                "existing": True})
            total_generated += dur
            print(f"  [{i:02d}/{len(scenes):02d}] {wav_path.name} ({dur:.1f}s) — using cached")
            continue

        text = scene.get("narration", scene.get("text", ""))
        if not text:
            print(f"  [{i:02d}/{len(scenes):02d}] SKIP — no narration text")
            continue

        if args.dry_run:
            print(f"  [{i:02d}/{len(scenes):02d}] would generate: \"{text[:60]}...\"")
            continue

        dur = await generate_scene_audio(text, voice, wav_path)
        audio_files.append({"index": i, "path": wav_path, "duration": dur,
                            "existing": False})
        total_generated += dur
        scene_dur = scene.get("duration", scene.get("end_seconds", 0) - scene.get("start_seconds", 0))
        status = "OK" if abs(dur - scene_dur) < 2.0 else f"MISMATCH (scene={scene_dur:.1f}s, audio={dur:.1f}s)"
        print(f"  [{i:02d}/{len(scenes):02d}] {wav_path.name} ({dur:.1f}s) — {status}")

    if args.dry_run or not audio_files:
        return {"status": "dry_run" if args.dry_run else "no_audio", "title": title}

    # Combine all scene audio into one narration track
    print(f"\n  Combining audio ({total_generated:.1f}s total)...")
    combined_audio = build_audio_list(nd, scenes)
    print(f"  Combined: {combined_audio} ({get_audio_duration(combined_audio):.1f}s)")

    # Create narrated scenes directory
    narrated_scenes_dir = output_dir / "scenes_narrated"
    narrated_scenes_dir.mkdir(exist_ok=True)

    # Mux each scene individually
    scenes_dir = output_dir / "scenes"
    if scenes_dir.exists():
        print("  Muxing per-scene narration...")
        for af in audio_files:
            idx = af["index"]
            scene_mp4 = scenes_dir / f"scene_{idx:03d}.mp4"
            if scene_mp4.exists():
                narrated = mux_single_scene(idx, scenes_dir, af["path"], narrated_scenes_dir)
                print(f"    scene_{idx:03d} → {narrated.name}")

    # Mux full pack
    main_mp4 = find_main_mp4(output_dir)
    if main_mp4:
        narrated_output = output_dir / f"{main_mp4.stem}_narrated.mp4"
        print(f"  Muxing full video: {narrated_output.name}...")
        mux_audio(main_mp4, combined_audio, narrated_output)
        print(f"  → {narrated_output}")

        # Also produce a sidecar: just the final audio
        final_audio = output_dir / "narration_full.wav"
        shutil.copy2(str(combined_audio), str(final_audio))
        print(f"  → {final_audio}")
    else:
        print("  No main MP4 found — only per-scene narrated clips produced")

    print(f"\n  Done.")
    return {"status": "ok", "title": title, "scenes_processed": len(audio_files)}


def parse_args():
    parser = argparse.ArgumentParser(description="Add edge-tts narration to a rendered platinum pack")
    parser.add_argument("output_dir", type=str, help="Pack output directory (e.g. output_life_crosses/)")
    parser.add_argument("--voice", default="en-US-AriaNeural",
                        help="Edge TTS voice (default: en-US-AriaNeural)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--keep-audio", action="store_true", help="Keep per-scene WAVs (always on)")
    parser.add_argument("--scene", type=int, help="Narrate a single scene only")
    return parser.parse_args()


def main():
    args = parse_args()
    asyncio.run(narrate_pack(args.output_dir, args))


if __name__ == "__main__":
    main()
