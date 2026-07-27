#!/usr/bin/env python3
"""Render score.mid with composition-specific procedural instruments.

The renderer is intentionally SoundFont-free. It parses the generated format-1
MIDI directly, converts ticks with the composition's exact tempo map, and
streams a normalized stereo PCM mix to disk through a temporary memory map.

Dependencies:
    Python 3.10+
    NumPy
    ffmpeg only when the requested output is not WAV

Examples:
    python render-audio.py --output build/score.wav
    python render-audio.py --output build/score.flac
    python render-audio.py --start 526 --end 566 --output build/recognition.wav
"""
from __future__ import annotations

import argparse
import bisect
import math
import shutil
import struct
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from engine import ROOT, load_composition
from generate_score import TPB, TempoMap


@dataclass(frozen=True)
class Note:
    track: int
    name: str
    channel: int
    pitch: int
    velocity: int
    start_tick: int
    end_tick: int


@dataclass(frozen=True)
class RenderNote:
    track: int
    name: str
    pitch: int
    velocity: int
    volume: float
    pan: float
    start: float
    end: float


TRACK_STYLE = {
    "Breath Spectrum": 0,
    "Vowel Pillars": 1,
    "Consonant Glass": 2,
    "Syntax Braid": 3,
    "Semantic Bloom": 4,
}


def fail(message: str) -> None:
    raise ValueError(message)


def read_vlq(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    while True:
        if offset >= len(data):
            fail("truncated MIDI variable-length value")
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, offset


def parse_track(
    data: bytes,
    track_index: int,
) -> tuple[list[Note], dict[int, int], dict[int, int]]:
    offset = 0
    tick = 0
    running_status: int | None = None
    track_name = f"Track {track_index}"
    active: dict[tuple[int, int], list[tuple[int, int]]] = {}
    notes: list[Note] = []
    channel_volume: dict[int, int] = {}
    channel_pan: dict[int, int] = {}

    while offset < len(data):
        delta, offset = read_vlq(data, offset)
        tick += delta
        if offset >= len(data):
            fail("truncated MIDI event")
        status = data[offset]
        if status & 0x80:
            offset += 1
            if status < 0xF0:
                running_status = status
        elif running_status is not None:
            status = running_status
        else:
            fail("running status used before a channel status")

        if status == 0xFF:
            if offset >= len(data):
                fail("truncated MIDI meta event")
            event_type = data[offset]
            offset += 1
            length, offset = read_vlq(data, offset)
            payload = data[offset : offset + length]
            offset += length
            if event_type == 0x03:
                track_name = payload.decode("utf-8", errors="replace")
            continue
        if status in (0xF0, 0xF7):
            length, offset = read_vlq(data, offset)
            offset += length
            continue

        message = status & 0xF0
        channel = status & 0x0F
        parameter_count = 1 if message in (0xC0, 0xD0) else 2
        if offset + parameter_count > len(data):
            fail("truncated MIDI channel event")
        first = data[offset]
        second = data[offset + 1] if parameter_count == 2 else 0
        offset += parameter_count

        if message == 0xB0:
            if first == 7:
                channel_volume[channel] = second
            elif first == 10:
                channel_pan[channel] = second
        elif message == 0x90 and second > 0:
            active.setdefault((channel, first), []).append((tick, second))
        elif message == 0x80 or (message == 0x90 and second == 0):
            key = (channel, first)
            starts = active.get(key)
            if not starts:
                fail(f"note-off without note-on at tick {tick}")
            start_tick, velocity = starts.pop(0)
            notes.append(
                Note(
                    track=track_index,
                    name=track_name,
                    channel=channel,
                    pitch=first,
                    velocity=velocity,
                    start_tick=start_tick,
                    end_tick=tick,
                )
            )
            if not starts:
                del active[key]

    if active:
        fail(f"{track_name} contains notes without note-off events")
    return notes, channel_volume, channel_pan


def parse_midi(path: Path) -> tuple[int, list[Note], dict[int, int], dict[int, int]]:
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        fail(f"{path} is not a MIDI file")
    header_length, midi_format, track_count, division = struct.unpack(
        ">IHHH", data[4:14]
    )
    if header_length != 6 or midi_format != 1:
        fail("the procedural renderer expects a format-1 MIDI file")
    if division & 0x8000:
        fail("SMPTE MIDI timing is not supported")

    offset = 14
    notes: list[Note] = []
    volumes: dict[int, int] = {}
    pans: dict[int, int] = {}
    for track_index in range(track_count):
        if data[offset : offset + 4] != b"MTrk":
            fail("expected MIDI track chunk")
        length = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
        start = offset + 8
        end = start + length
        if end > len(data):
            fail("truncated MIDI track chunk")
        track_notes, track_volumes, track_pans = parse_track(
            data[start:end],
            track_index,
        )
        notes.extend(track_notes)
        volumes.update(track_volumes)
        pans.update(track_pans)
        offset = end
    if offset != len(data):
        fail("unexpected bytes after the final MIDI track")
    return division, notes, volumes, pans


def tick_to_seconds(tick: int, composition: dict, tempo: TempoMap) -> float:
    index = bisect.bisect_right(tempo.segment_ticks, tick) - 1
    index = max(0, index)
    if index >= len(tempo.segment_ticks) - 1:
        return float(composition["duration_seconds"])
    waypoint = composition["waypoints"][index]
    start_seconds = float(waypoint["time"])
    bpm = float(waypoint["music"]["bpm"])
    local_ticks = tick - tempo.segment_ticks[index]
    return start_seconds + local_ticks * 60.0 / (bpm * TPB)


def render_notes(path: Path, composition: dict) -> list[RenderNote]:
    division, notes, volumes, pans = parse_midi(path)
    if division != TPB:
        fail(f"MIDI division {division} does not match generator division {TPB}")
    tempo = TempoMap(composition)
    rendered = []
    for note in notes:
        start = tick_to_seconds(note.start_tick, composition, tempo)
        end = tick_to_seconds(note.end_tick, composition, tempo)
        if end <= start:
            continue
        rendered.append(
            RenderNote(
                track=TRACK_STYLE.get(note.name, max(0, note.track - 1)),
                name=note.name,
                pitch=note.pitch,
                velocity=note.velocity,
                volume=volumes.get(note.channel, 96) / 127.0,
                pan=pans.get(note.channel, 64) / 127.0,
                start=start,
                end=end,
            )
        )
    return rendered


def midi_frequency(pitch: int) -> float:
    return 440.0 * 2.0 ** ((pitch - 69) / 12.0)


def soft_envelope(
    age: np.ndarray,
    remaining: np.ndarray,
    attack: float,
    release: float,
) -> np.ndarray:
    attack_shape = np.sin(
        0.5 * math.pi * np.clip(age / max(attack, 0.0001), 0.0, 1.0)
    ) ** 2
    release_shape = np.sin(
        0.5 * math.pi * np.clip(remaining / max(release, 0.0001), 0.0, 1.0)
    ) ** 2
    return np.minimum(attack_shape, release_shape)


def harmonic(
    phase: np.ndarray,
    multiplier: float,
    weight: float,
    nyquist: float,
    frequency: float,
    offset: float = 0.0,
) -> np.ndarray:
    if frequency * multiplier >= nyquist * 0.96:
        return np.zeros_like(phase)
    return weight * np.sin(phase * multiplier + offset)


def instrument(
    style: int,
    frequency: float,
    absolute_time: np.ndarray,
    age: np.ndarray,
    remaining: np.ndarray,
    sample_rate: int,
    seed: float,
) -> np.ndarray:
    nyquist = sample_rate * 0.5
    phase = math.tau * frequency * absolute_time

    if style == 0:
        # Copper breath: a stable fundamental carrying slow spectral turbulence.
        signal = harmonic(phase, 1.0, 0.64, nyquist, frequency)
        signal += harmonic(phase, 2.01, 0.18, nyquist, frequency, 0.4)
        signal += harmonic(phase, 0.5, 0.12, nyquist, frequency, seed)
        breath = (
            np.sin(absolute_time * 113.0 + seed * 2.3)
            * np.sin(absolute_time * 173.0 + seed * 0.7)
            * np.sin(absolute_time * 229.0 + 1.4)
        )
        signal += breath * (0.025 + 0.020 * np.sin(absolute_time * 0.31))
        envelope = soft_envelope(age, remaining, 1.4, 1.8)
    elif style == 1:
        # Vowel pillars: slowly detuned formant bands rather than a literal choir.
        wobble = 0.055 * np.sin(absolute_time * 1.07 + seed)
        signal = np.sin(phase + wobble)
        signal += harmonic(phase, 2.0, 0.27, nyquist, frequency, 0.3)
        signal += harmonic(phase, 3.0, 0.16, nyquist, frequency, 1.1)
        signal += harmonic(phase, 5.0, 0.07, nyquist, frequency, seed)
        envelope = soft_envelope(age, remaining, 0.65, 1.25)
    elif style == 2:
        # Consonant glass: brief inharmonic edges with no reverb across silence.
        signal = harmonic(phase, 1.0, 0.30, nyquist, frequency)
        signal += harmonic(phase, 2.73, 0.52, nyquist, frequency, seed)
        signal += harmonic(phase, 4.11, 0.29, nyquist, frequency, 0.7)
        signal += harmonic(phase, 7.37, 0.14, nyquist, frequency, 1.9)
        envelope = soft_envelope(age, remaining, 0.004, 0.035)
        envelope *= np.exp(-age * 4.2)
    elif style == 3:
        # Syntax braid: a compact plucked spectrum whose overtones imply a whole.
        signal = np.zeros_like(phase)
        for partial in range(1, 7):
            signal += harmonic(
                phase,
                float(partial),
                1.0 / partial,
                nyquist,
                frequency,
                seed * partial * 0.07,
            )
        signal *= 0.48 + 0.52 * np.exp(-age * 0.42)
        envelope = soft_envelope(age, remaining, 0.018, 0.32)
    else:
        # Semantic bloom: wide beating partials whose centre stays pitch-stable.
        signal = 0.44 * np.sin(phase * 0.995 + seed)
        signal += 0.44 * np.sin(phase * 1.005 - seed * 0.4)
        signal += harmonic(phase, 2.0, 0.18, nyquist, frequency, 0.6)
        signal += harmonic(phase, 3.0, 0.08, nyquist, frequency, 1.7)
        envelope = soft_envelope(age, remaining, 0.95, 1.6)

    return signal * envelope


def equal_power_pan(pan: float) -> tuple[float, float]:
    angle = np.clip(pan, 0.0, 1.0) * math.pi * 0.5
    return math.cos(angle), math.sin(angle)


def synthesize(
    notes: list[RenderNote],
    output: Path,
    *,
    start: float,
    end: float,
    sample_rate: int,
    peak_db: float,
) -> None:
    if end <= start:
        fail("--end must be greater than --start")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame_count = int(math.ceil((end - start) * sample_rate))
    note_chunk = 131_072
    io_chunk = 65_536

    with tempfile.TemporaryDirectory(prefix="phononic-audio-") as temporary:
        mix_path = Path(temporary) / "mix.f32"
        mix = np.memmap(
            mix_path,
            dtype=np.float32,
            mode="w+",
            shape=(frame_count, 2),
        )
        mix[:] = 0.0

        selected = [
            note for note in notes if note.start < end and note.end > start
        ]
        for number, note in enumerate(selected):
            clipped_start = max(start, note.start)
            clipped_end = min(end, note.end)
            first_frame = max(0, int(math.floor((clipped_start - start) * sample_rate)))
            last_frame = min(
                frame_count,
                int(math.ceil((clipped_end - start) * sample_rate)),
            )
            frequency = midi_frequency(note.pitch)
            left_gain, right_gain = equal_power_pan(note.pan)
            amplitude = (
                (note.velocity / 127.0) ** 1.35
                * note.volume
                * (0.082 if note.track != 2 else 0.105)
            )
            seed = note.pitch * 0.173 + note.track * 1.917

            for block_start in range(first_frame, last_frame, note_chunk):
                block_end = min(last_frame, block_start + note_chunk)
                frames = np.arange(block_start, block_end, dtype=np.float64)
                absolute_time = start + frames / sample_rate
                age = absolute_time - note.start
                remaining = note.end - absolute_time
                signal = instrument(
                    note.track,
                    frequency,
                    absolute_time,
                    age,
                    remaining,
                    sample_rate,
                    seed,
                )
                mix[block_start:block_end, 0] += (
                    signal * amplitude * left_gain
                ).astype(np.float32)
                mix[block_start:block_end, 1] += (
                    signal * amplitude * right_gain
                ).astype(np.float32)
            if number and number % 200 == 0:
                print(f"synthesized {number}/{len(selected)} notes", flush=True)
        mix.flush()

        raw_peak = 0.0
        for block_start in range(0, frame_count, io_chunk):
            block = np.asarray(
                mix[block_start : block_start + io_chunk],
                dtype=np.float32,
            )
            raw_peak = max(raw_peak, float(np.max(np.abs(np.tanh(block)))))
        target_peak = 10.0 ** (peak_db / 20.0)
        gain = target_peak / max(raw_peak, 1.0e-9)

        with wave.open(str(output), "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for block_start in range(0, frame_count, io_chunk):
                block = np.asarray(
                    mix[block_start : block_start + io_chunk],
                    dtype=np.float32,
                )
                mastered = np.tanh(block) * gain
                pcm = np.clip(mastered, -1.0, 1.0)
                pcm = (pcm * 32767.0).astype("<i2")
                wav.writeframes(pcm.tobytes())

    print(
        f"Wrote {output} "
        f"({end-start:.1f}s, {sample_rate} Hz, {len(selected)} notes)"
    )


def encode_with_ffmpeg(source: Path, destination: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        fail("ffmpeg is required for non-WAV output")
    codec_options: dict[str, list[str]] = {
        ".flac": ["-c:a", "flac"],
        ".m4a": ["-c:a", "aac", "-b:a", "256k"],
        ".mp3": ["-c:a", "libmp3lame", "-q:a", "1"],
        ".ogg": ["-c:a", "libvorbis", "-q:a", "7"],
    }
    suffix = destination.suffix.lower()
    if suffix not in codec_options:
        fail(f"unsupported output format {suffix}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            *codec_options[suffix],
            str(destination),
        ],
        check=True,
    )
    print(f"Encoded {destination}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--midi", type=Path, default=ROOT / "score.mid")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "score.wav")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float)
    parser.add_argument("--sample-rate", type=int, default=44_100)
    parser.add_argument(
        "--peak-db",
        type=float,
        default=-1.0,
        help="normalized peak level in dBFS",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    composition = load_composition()
    duration = float(composition["duration_seconds"])
    start = max(0.0, args.start)
    end = min(duration, args.end if args.end is not None else duration)
    if not 8_000 <= args.sample_rate <= 192_000:
        fail("sample rate must be between 8000 and 192000")
    if not -24.0 <= args.peak_db <= 0.0:
        fail("--peak-db must be between -24 and 0")

    notes = render_notes(args.midi, composition)
    if args.output.suffix.lower() == ".wav":
        synthesize(
            notes,
            args.output,
            start=start,
            end=end,
            sample_rate=args.sample_rate,
            peak_db=args.peak_db,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="phononic-encode-") as temporary:
            temporary_wav = Path(temporary) / "score.wav"
            synthesize(
                notes,
                temporary_wav,
                start=start,
                end=end,
                sample_rate=args.sample_rate,
                peak_db=args.peak_db,
            )
            encode_with_ffmpeg(temporary_wav, args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
