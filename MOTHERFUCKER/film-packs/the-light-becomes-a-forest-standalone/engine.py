#!/usr/bin/env python3
"""Shared trajectory and music-feature engine for the contrapuntal forest."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
COMPOSITION_PATH = ROOT / "composition.json"


@dataclass(frozen=True)
class FrameState:
    seconds: float
    progress: float
    stage: int
    local: float
    vector: tuple[float, float, float, float, float, float]
    tattva_open: float
    bpm: float
    beat_position: float
    audio_volume: float
    audio_beat: float
    music_a: tuple[float, float, float, float]
    music_b: tuple[float, float]


def load_composition(path: Path = COMPOSITION_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep01(value: float) -> float:
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def mix(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def semantic_intervals(
    composition: dict[str, Any],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return list(zip(composition["waypoints"], composition["waypoints"][1:]))


def segment_at(composition: dict[str, Any], seconds: float) -> tuple[int, float]:
    duration = float(composition["duration_seconds"])
    seconds = max(0.0, min(duration, seconds))
    intervals = semantic_intervals(composition)
    if seconds >= duration:
        return len(intervals) - 1, 1.0
    for index, (left, right) in enumerate(intervals):
        start = float(left["time"])
        end = float(right["time"])
        if start <= seconds < end:
            return index, (seconds - start) / (end - start)
    raise ValueError(f"no semantic interval contains {seconds}")


def interpolation_amount(
    left: dict[str, Any],
    right: dict[str, Any],
    local: float,
) -> float:
    """Reciprocity and recognition let the next state alter the present early."""
    reciprocal = 0.5 * (float(left["state"][3]) + float(right["state"][3]))
    recognition = 0.5 * (float(left["state"][5]) + float(right["state"][5]))
    causal_flow = smoothstep01(local)
    late_disclosure = smoothstep01(clamp01((local - 0.34) / 0.52))
    anticipation = smoothstep01(clamp01((local + 0.10) / 1.10))
    amount = mix(late_disclosure, causal_flow, reciprocal)
    return mix(amount, anticipation, recognition * 0.22)


def vector_at(composition: dict[str, Any], seconds: float) -> tuple[float, ...]:
    stage, local = segment_at(composition, seconds)
    left, right = semantic_intervals(composition)[stage]
    amount = interpolation_amount(left, right, local)
    return tuple(
        mix(float(a), float(b), amount)
        for a, b in zip(left["state"], right["state"], strict=True)
    )


def tattva_open_at(composition: dict[str, Any], seconds: float) -> float:
    stage, local = segment_at(composition, seconds)
    left, right = semantic_intervals(composition)[stage]
    amount = interpolation_amount(left, right, local)
    left_open = 1.0 - float(left["tattva"]["constraint"])
    right_open = 1.0 - float(right["tattva"]["constraint"])
    return mix(left_open, right_open, amount)


def bpm_at(composition: dict[str, Any], seconds: float) -> float:
    stage, local = segment_at(composition, seconds)
    left, right = semantic_intervals(composition)[stage]
    return mix(
        float(left["music"]["bpm"]),
        float(right["music"]["bpm"]),
        smoothstep01(local),
    )


def beat_position_at(composition: dict[str, Any], seconds: float) -> float:
    """Integrate the authored tempo curve with Simpson's rule."""
    seconds = max(0.0, min(float(composition["duration_seconds"]), seconds))
    beats = 0.0
    for left, right in semantic_intervals(composition):
        start = float(left["time"])
        end = float(right["time"])
        if seconds <= start:
            break
        span = min(seconds, end) - start
        if span <= 0.0:
            continue
        total = end - start
        bpm_a = float(left["music"]["bpm"])
        bpm_b = float(right["music"]["bpm"])
        steps = max(4, int(math.ceil(span / 1.5)))
        if steps % 2:
            steps += 1
        step_size = span / steps
        integral = 0.0
        for step in range(steps + 1):
            x = step * step_size
            local = x / total
            bpm = mix(bpm_a, bpm_b, smoothstep01(local))
            weight = 1 if step in (0, steps) else (4 if step % 2 else 2)
            integral += weight * bpm
        beats += integral * step_size / 3.0 / 60.0
        if seconds < end:
            break
    return beats


def in_silence(composition: dict[str, Any], seconds: float) -> bool:
    return any(
        float(window["start"]) <= seconds < float(window["end"])
        for window in composition["score"]["silence_windows"]
    )


def periodic_pulse(position: float, subdivision: float, width: float) -> float:
    phase = (position * subdivision) % 1.0
    distance = min(phase, 1.0 - phase)
    return math.exp(-0.5 * (distance / max(width, 0.001)) ** 2)


def audio_features(
    composition: dict[str, Any],
    seconds: float,
    vector: tuple[float, ...],
    beat_position: float,
) -> tuple[float, float]:
    if in_silence(composition, seconds):
        return 0.0, 0.0
    radiance, localization, appetite, reciprocity, fecundity, recognition = vector
    pulse_width = mix(0.19, 0.045, appetite * 0.62 + fecundity * 0.38)
    beat = periodic_pulse(beat_position, 1.0, pulse_width)
    breath = 0.88 + 0.12 * math.sin(
        seconds * 0.071 + reciprocity * 3.0 + recognition * 2.0
    )
    volume = (
        0.12
        + 0.13 * radiance
        + 0.18 * localization
        + 0.20 * appetite
        + 0.15 * reciprocity
        + 0.18 * fecundity
    ) * breath
    return clamp01(volume), clamp01(beat)


def music_features(
    composition: dict[str, Any],
    seconds: float,
    vector: tuple[float, ...],
    beat_position: float,
) -> tuple[tuple[float, float, float, float], tuple[float, float]]:
    """Expose polyphonic activity to GLSL without decoding an audio file."""
    if in_silence(composition, seconds):
        return (0.0, 0.0, 0.0, 0.0), (0.0, 0.0)
    radiance, localization, appetite, reciprocity, fecundity, recognition = vector
    bass = periodic_pulse(beat_position, 1.0, mix(0.16, 0.07, appetite))
    inner = periodic_pulse(
        beat_position + 0.5 * reciprocity,
        mix(1.0, 2.0, fecundity),
        0.085,
    )
    upper = periodic_pulse(
        beat_position + 0.25,
        mix(1.0, 4.0, fecundity),
        mix(0.12, 0.045, localization),
    )
    continuo = periodic_pulse(
        beat_position,
        mix(2.0, 4.0, fecundity),
        0.055,
    )
    bar_phase = (beat_position % 8.0) / 8.0
    subject_envelope = math.sin(math.pi * clamp01(bar_phase)) ** 2
    subject = clamp01(recognition * (0.38 + 0.62 * subject_envelope))
    chromatic_wave = 0.5 + 0.5 * math.sin(beat_position * math.pi * 0.5)
    tension = clamp01(
        appetite * (0.48 + 0.34 * chromatic_wave)
        + localization * 0.18
        - reciprocity * 0.22
        - radiance * 0.10
    )
    return (
        clamp01(bass),
        clamp01(inner),
        clamp01(upper),
        clamp01(continuo),
    ), (tension, subject)


def frame_state(composition: dict[str, Any], seconds: float) -> FrameState:
    duration = float(composition["duration_seconds"])
    seconds = max(0.0, min(duration, seconds))
    stage, local = segment_at(composition, seconds)
    vector = vector_at(composition, seconds)
    beat_position = beat_position_at(composition, seconds)
    volume, beat = audio_features(composition, seconds, vector, beat_position)
    music_a, music_b = music_features(
        composition,
        seconds,
        vector,
        beat_position,
    )
    return FrameState(
        seconds=seconds,
        progress=seconds / duration,
        stage=stage,
        local=local,
        vector=vector,  # type: ignore[arg-type]
        tattva_open=tattva_open_at(composition, seconds),
        bpm=bpm_at(composition, seconds),
        beat_position=beat_position,
        audio_volume=volume,
        audio_beat=beat,
        music_a=music_a,
        music_b=music_b,
    )


def seconds_to_clock(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:04.1f}"
