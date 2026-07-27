#!/usr/bin/env python3
"""Shared trajectory engine for the integrated audiovisual composition."""
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


def load_composition(path: Path = COMPOSITION_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep01(value: float) -> float:
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def mix(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def semantic_intervals(composition: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    waypoints = composition["waypoints"]
    return list(zip(waypoints, waypoints[1:]))


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
    raise ValueError(f"no segment contains {seconds}")


def interpolation_amount(left: dict[str, Any], right: dict[str, Any], local: float) -> float:
    """Blend gently when continuity is high and decisively when it is low."""
    continuity = 0.5 * (float(left["state"][1]) + float(right["state"][1]))
    fluid = smoothstep01(local)
    decisive = smoothstep01(clamp01((local - 0.34) / 0.32))
    return mix(decisive, fluid, continuity)


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
    amount = smoothstep01(local)
    return mix(float(left["music"]["bpm"]), float(right["music"]["bpm"]), amount)


def beat_position_at(composition: dict[str, Any], seconds: float) -> float:
    """Integrate the piecewise-linear tempo curve analytically enough for rendering."""
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
        fraction = span / total
        bpm_a = float(left["music"]["bpm"])
        bpm_b = float(right["music"]["bpm"])
        # Tempo interpolation is smooth in the frame engine. Simpson sampling is
        # deterministic and sufficiently accurate for the visual pulse.
        steps = max(4, int(math.ceil(span / 2.0)))
        if steps % 2:
            steps += 1
        h = span / steps
        integral = 0.0
        for step in range(steps + 1):
            x = step * h
            local = x / total
            bpm = mix(bpm_a, bpm_b, smoothstep01(local))
            weight = 1 if step in (0, steps) else (4 if step % 2 else 2)
            integral += weight * bpm
        beats += integral * h / 3.0 / 60.0
        if seconds < end:
            break
    return beats


def in_silence(composition: dict[str, Any], seconds: float) -> bool:
    return any(
        float(window["start"]) <= seconds < float(window["end"])
        for window in composition["score"]["silence_windows"]
    )


def audio_features(
    composition: dict[str, Any],
    seconds: float,
    vector: tuple[float, ...],
    beat_position: float,
) -> tuple[float, float]:
    if in_silence(composition, seconds):
        return 0.0, 0.0
    metamorphosis, _, centricity, coherence, periodicity, density = vector
    phase = beat_position - math.floor(beat_position)
    distance = min(phase, 1.0 - phase)
    width = mix(0.22, 0.065, periodicity)
    beat = math.exp(-0.5 * (distance / width) ** 2)
    # Energy affects pressure and reach in the shader, never final exposure alone.
    breathing = 0.86 + 0.14 * math.sin(seconds * 0.17 + density * 3.0)
    volume = (
        0.12
        + 0.46 * density
        + 0.18 * metamorphosis
        + 0.08 * centricity
        + 0.05 * coherence
    ) * breathing
    return clamp01(volume), clamp01(beat)


def frame_state(composition: dict[str, Any], seconds: float) -> FrameState:
    duration = float(composition["duration_seconds"])
    seconds = max(0.0, min(duration, seconds))
    stage, local = segment_at(composition, seconds)
    vector = vector_at(composition, seconds)
    beat_position = beat_position_at(composition, seconds)
    volume, beat = audio_features(composition, seconds, vector, beat_position)
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
    )


def seconds_to_clock(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:04.1f}"
