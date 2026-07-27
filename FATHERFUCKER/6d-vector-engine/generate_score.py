#!/usr/bin/env python3
"""Generate the complete dependency-free MIDI score from composition.json."""
from __future__ import annotations

import hashlib
import json
import math
import random
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from engine import COMPOSITION_PATH, ROOT, in_silence, load_composition

TPB = 480


def variable_length(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative variable-length MIDI value")
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


def meta(event_type: int, payload: bytes) -> bytes:
    return bytes((0xFF, event_type)) + variable_length(len(payload)) + payload


@dataclass(frozen=True)
class MidiEvent:
    tick: int
    priority: int
    data: bytes


class TempoMap:
    def __init__(self, composition: dict):
        self.composition = composition
        self.waypoints = composition["waypoints"]
        self.segment_ticks: list[int] = [0]
        total = 0
        for left, right in zip(self.waypoints, self.waypoints[1:]):
            seconds = float(right["time"]) - float(left["time"])
            bpm = float(left["music"]["bpm"])
            total += round(seconds * bpm / 60.0 * TPB)
            self.segment_ticks.append(total)

    def seconds_to_tick(self, seconds: float) -> int:
        seconds = max(0.0, min(float(self.composition["duration_seconds"]), seconds))
        for index, (left, right) in enumerate(
            zip(self.waypoints, self.waypoints[1:])
        ):
            start = float(left["time"])
            end = float(right["time"])
            if seconds <= end or index == len(self.waypoints) - 2:
                bpm = float(left["music"]["bpm"])
                local = max(0.0, seconds - start)
                return self.segment_ticks[index] + round(local * bpm / 60.0 * TPB)
        return self.segment_ticks[-1]


def track_chunk(events: Iterable[MidiEvent], end_tick: int) -> bytes:
    ordered = sorted(events, key=lambda event: (event.tick, event.priority, event.data))
    body = bytearray()
    previous = 0
    for event in ordered:
        body.extend(variable_length(event.tick - previous))
        body.extend(event.data)
        previous = event.tick
    body.extend(variable_length(max(0, end_tick - previous)))
    body.extend(meta(0x2F, b""))
    return b"MTrk" + struct.pack(">I", len(body)) + bytes(body)


def add_note(
    events: list[MidiEvent],
    tempo: TempoMap,
    composition: dict,
    *,
    start: float,
    end: float,
    channel: int,
    pitch: int,
    velocity: int,
) -> None:
    if end <= start:
        return
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))
    # Apply the silence aperture here, after every compositional decision. This
    # catches short gestures that begin before the window but would otherwise
    # sustain across its boundary.
    for playable_start, playable_end in playable_spans(composition, start, end):
        start_tick = tempo.seconds_to_tick(playable_start)
        end_tick = max(start_tick + 1, tempo.seconds_to_tick(playable_end))
        events.append(
            MidiEvent(start_tick, 2, bytes((0x90 | channel, pitch, velocity)))
        )
        events.append(MidiEvent(end_tick, 0, bytes((0x80 | channel, pitch, 0))))


def playable_spans(composition: dict, start: float, end: float) -> list[tuple[float, float]]:
    spans = [(start, end)]
    for window in composition["score"]["silence_windows"]:
        silence_start = float(window["start"])
        silence_end = float(window["end"])
        updated: list[tuple[float, float]] = []
        for left, right in spans:
            if right <= silence_start or left >= silence_end:
                updated.append((left, right))
            else:
                if left < silence_start:
                    updated.append((left, silence_start))
                if right > silence_end:
                    updated.append((silence_end, right))
        spans = updated
    return [(left, right) for left, right in spans if right - left >= 0.05]


def program_track(name: str, channel: int, program: int) -> list[MidiEvent]:
    encoded = name.encode("utf-8")
    return [
        MidiEvent(0, 0, meta(0x03, encoded)),
        MidiEvent(0, 1, bytes((0xC0 | channel, program))),
        MidiEvent(0, 1, bytes((0xB0 | channel, 7, 100))),
        MidiEvent(0, 1, bytes((0xB0 | channel, 10, 64))),
    ]


def compose() -> tuple[bytes, dict]:
    composition = load_composition()
    tempo = TempoMap(composition)
    waypoints = composition["waypoints"]
    end_tick = tempo.seconds_to_tick(float(composition["duration_seconds"]))
    rng = random.Random(0xCA7A6A)

    conductor: list[MidiEvent] = [MidiEvent(0, 0, meta(0x03, b"Conductor"))]
    tracks = [
        program_track("Breath Field", 0, 89),
        program_track("Continuity Strings", 1, 48),
        program_track("Predictive Filaments", 2, 11),
        program_track("Boundary Pulse", 3, 81),
        program_track("Recognition Bloom", 4, 52),
    ]
    event_counts = {"note_on": 0, "tempo": 0, "marker": 0}

    for index, waypoint in enumerate(waypoints[:-1]):
        start = float(waypoint["time"])
        end = float(waypoints[index + 1]["time"])
        bpm = float(waypoint["music"]["bpm"])
        tempo_value = round(60_000_000 / bpm)
        tick = tempo.seconds_to_tick(start)
        conductor.append(
            MidiEvent(tick, 0, meta(0x51, tempo_value.to_bytes(3, "big")))
        )
        conductor.append(MidiEvent(tick, 1, meta(0x06, waypoint["title"].encode())))
        event_counts["tempo"] += 1
        event_counts["marker"] += 1

        delta, continuity, centricity, coherence, periodicity, density = (
            float(value) for value in waypoint["state"]
        )
        notes = [int(note) for note in waypoint["music"]["notes"]]
        beat_seconds = 60.0 / bpm
        spans = playable_spans(composition, start, end)

        # Breath field: centricity determines how strongly the local root persists.
        for left, right in spans:
            roots = notes[:1] + ([notes[1]] if centricity > 0.45 and len(notes) > 1 else [])
            for voice, pitch in enumerate(roots):
                add_note(
                    tracks[0],
                    tempo,
                    composition,
                    start=left,
                    end=max(left + 0.1, right - 0.04),
                    channel=0,
                    pitch=pitch,
                    velocity=round(23 + 35 * centricity - voice * 5),
                )
                event_counts["note_on"] += 1

        # Continuity strings: common tones span each semantic interval.
        voice_count = max(2, min(len(notes), round(2 + density * 5)))
        chosen = notes[-voice_count:]
        for left, right in spans:
            for voice, pitch in enumerate(chosen):
                delayed = left + min(1.8, voice * (1.0 - continuity) * 0.45)
                add_note(
                    tracks[1],
                    tempo,
                    composition,
                    start=delayed,
                    end=max(delayed + 0.1, right - 0.08),
                    channel=1,
                    pitch=pitch,
                    velocity=round(25 + coherence * 27 + density * 10 - voice),
                )
                event_counts["note_on"] += 1

        # Predictive filaments: density adds branches, low periodicity adds bounded jitter.
        subdivision = 2 if density > 0.54 else 1
        step = beat_seconds / subdivision
        cursor = start + 0.5 * beat_seconds
        filament_index = 0
        while cursor < end - 0.05:
            jitter = (rng.random() - 0.5) * step * 0.42 * (1.0 - periodicity)
            event_time = max(start, min(end - 0.05, cursor + jitter))
            if not in_silence(composition, event_time):
                probability = 0.22 + 0.70 * density
                if rng.random() < probability:
                    direction = 1 if filament_index % 2 == 0 else -1
                    note_index = (filament_index * direction) % len(notes)
                    pitch = notes[note_index] + 12 * (1 if filament_index % 5 else 2)
                    length = step * (0.22 + 0.52 * continuity)
                    add_note(
                        tracks[2],
                        tempo,
                        composition,
                        start=event_time,
                        end=min(end, event_time + length),
                        channel=2,
                        pitch=pitch,
                        velocity=round(24 + 50 * delta + 18 * rng.random()),
                    )
                    event_counts["note_on"] += 1
            filament_index += 1
            cursor += step

        # Boundary pulse: periodicity controls reliability; density controls subdivisions.
        pulse_step = beat_seconds * (1.0 if density < 0.72 else 0.5)
        cursor = start
        pulse_index = 0
        while cursor < end - 0.04:
            jitter = (rng.random() - 0.5) * pulse_step * 0.28 * (1.0 - periodicity)
            event_time = cursor + jitter
            if start <= event_time < end and not in_silence(composition, event_time):
                accent = 1.0 if pulse_index % 4 == 0 else 0.58
                pitch = notes[0] + (12 if pulse_index % 2 else 0)
                add_note(
                    tracks[3],
                    tempo,
                    composition,
                    start=event_time,
                    end=min(end, event_time + 0.12 + 0.18 * coherence),
                    channel=3,
                    pitch=pitch,
                    velocity=round((28 + 54 * centricity) * accent),
                )
                event_counts["note_on"] += 1
            cursor += pulse_step
            pulse_index += 1

        # Recognition bloom enters only once the camera begins to reverse.
        if index >= 8:
            bloom_step = beat_seconds * (4.0 if index < 10 else 2.0)
            cursor = start + beat_seconds
            bloom_index = 0
            while cursor < end - 0.2:
                if not in_silence(composition, cursor):
                    pitch = notes[-1 - (bloom_index % min(3, len(notes)))] + 12
                    add_note(
                        tracks[4],
                        tempo,
                        composition,
                        start=cursor,
                        end=min(end, cursor + bloom_step * (0.72 + 0.22 * continuity)),
                        channel=4,
                        pitch=pitch,
                        velocity=round(34 + 45 * coherence),
                    )
                    event_counts["note_on"] += 1
                cursor += bloom_step
                bloom_index += 1

    # Ensure the key sentence arrives with a fresh, quiet transformed tonic.
    return_time = float(composition["recognition_event"]["key_sentence_time"])
    final_notes = waypoints[11]["music"]["notes"]
    for offset, pitch in enumerate(final_notes[1:6]):
        add_note(
            tracks[4],
            tempo,
            composition,
            start=return_time + offset * 0.18,
            end=return_time + 8.8 + offset * 0.26,
            channel=4,
            pitch=int(pitch) + 12,
            velocity=50 - offset * 3,
        )
        event_counts["note_on"] += 1

    event_counts["note_on"] = sum(
        1
        for track in tracks
        for event in track
        if len(event.data) >= 3
        and event.data[0] & 0xF0 == 0x90
        and event.data[2] > 0
    )
    chunks = [track_chunk(conductor, end_tick)] + [
        track_chunk(track, end_tick) for track in tracks
    ]
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), TPB)
    midi = header + b"".join(chunks)
    manifest = {
        "composition_id": composition["id"],
        "composition_sha256": hashlib.sha256(COMPOSITION_PATH.read_bytes()).hexdigest(),
        "duration_seconds": float(composition["duration_seconds"]),
        "ticks_per_beat": TPB,
        "track_count": len(chunks),
        "event_counts": event_counts,
        "silence_windows": composition["score"]["silence_windows"],
        "mapping": {
            "metamorphosis": "filament register travel, velocity, and chord displacement",
            "continuity": "note overlap, common-tone persistence, and voice-entry delay",
            "centricity": "drone strength and boundary-pulse velocity",
            "coherence": "sustained chord voicing and recognition-bloom intensity",
            "periodicity": "bounded rhythmic jitter and pulse-grid reliability",
            "density": "string voice count, subdivision, and event probability",
        },
        "chapters": [
            {
                "time": waypoint["time"],
                "id": waypoint["id"],
                "bpm": waypoint["music"]["bpm"],
                "chord": waypoint["music"]["chord"],
                "notes": waypoint["music"]["notes"],
            }
            for waypoint in waypoints
        ],
    }
    return midi, manifest


def main() -> int:
    midi, manifest = compose()
    (ROOT / "score.mid").write_bytes(midi)
    (ROOT / "score_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote score.mid ({len(midi):,} bytes, "
        f"{manifest['event_counts']['note_on']} note events)"
    )
    print("Wrote score_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
