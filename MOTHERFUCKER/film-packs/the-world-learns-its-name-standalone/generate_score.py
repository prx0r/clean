#!/usr/bin/env python3
"""Generate the complete dependency-free MIDI score from composition.json."""
from __future__ import annotations

import hashlib
import json
import math
import random
import struct
from dataclasses import dataclass
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
    """Exact tick map used by both generation and silence validation."""

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
        seconds = max(
            0.0,
            min(float(self.composition["duration_seconds"]), seconds),
        )
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


def playable_spans(
    composition: dict,
    start: float,
    end: float,
) -> list[tuple[float, float]]:
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
    return [(left, right) for left, right in spans if right - left >= 0.04]


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
    for playable_start, playable_end in playable_spans(composition, start, end):
        start_tick = tempo.seconds_to_tick(playable_start)
        end_tick = max(start_tick + 1, tempo.seconds_to_tick(playable_end))
        events.append(
            MidiEvent(start_tick, 2, bytes((0x90 | channel, pitch, velocity)))
        )
        events.append(MidiEvent(end_tick, 0, bytes((0x80 | channel, pitch, 0))))


def program_track(
    name: str,
    channel: int,
    program: int,
    *,
    volume: int,
    pan: int,
) -> list[MidiEvent]:
    return [
        MidiEvent(0, 0, meta(0x03, name.encode("utf-8"))),
        MidiEvent(0, 1, bytes((0xC0 | channel, program))),
        MidiEvent(0, 1, bytes((0xB0 | channel, 7, volume))),
        MidiEvent(0, 1, bytes((0xB0 | channel, 10, pan))),
    ]


def compose() -> tuple[bytes, dict]:
    composition = load_composition()
    tempo = TempoMap(composition)
    waypoints = composition["waypoints"]
    end_tick = tempo.seconds_to_tick(float(composition["duration_seconds"]))
    motif = [int(note) for note in composition["score"]["continuity_motif"]]
    rng = random.Random(0x5A8DA)

    conductor: list[MidiEvent] = [MidiEvent(0, 0, meta(0x03, b"Conductor"))]
    tracks = [
        program_track("Breath Spectrum", 0, 89, volume=88, pan=64),
        program_track("Vowel Pillars", 1, 53, volume=92, pan=48),
        program_track("Consonant Glass", 2, 11, volume=84, pan=80),
        program_track("Syntax Braid", 3, 46, volume=88, pan=58),
        program_track("Semantic Bloom", 4, 52, volume=94, pan=70),
    ]
    event_counts = {"note_on": 0, "tempo": 0, "marker": 0}
    motif_appearances: list[dict] = []

    for index, waypoint in enumerate(waypoints[:-1]):
        start = float(waypoint["time"])
        end = float(waypoints[index + 1]["time"])
        bpm = float(waypoint["music"]["bpm"])
        beat_seconds = 60.0 / bpm
        tick = tempo.seconds_to_tick(start)
        conductor.append(
            MidiEvent(
                tick,
                0,
                meta(0x51, round(60_000_000 / bpm).to_bytes(3, "big")),
            )
        )
        conductor.append(
            MidiEvent(tick, 1, meta(0x06, waypoint["title"].encode("utf-8")))
        )
        event_counts["tempo"] += 1
        event_counts["marker"] += 1

        articulation, continuity, deixis, resonance, prosody, semantic_density = (
            float(value) for value in waypoint["state"]
        )
        notes = [int(note) for note in waypoint["music"]["notes"]]
        spans = playable_spans(composition, start, end)

        # Breath spectrum: the copper thread is an unbroken low partial whose
        # localization follows deixis but never disappears from the piece.
        for left, right in spans:
            roots = notes[:1]
            if resonance > 0.72 and len(notes) > 1:
                roots.append(notes[1])
            for voice, pitch in enumerate(roots):
                add_note(
                    tracks[0],
                    tempo,
                    composition,
                    start=left,
                    end=max(left + 0.1, right - 0.035),
                    channel=0,
                    pitch=pitch,
                    velocity=round(25 + 24 * resonance + 15 * deixis - voice * 4),
                )

        # Vowel pillars: slow formant-like chord bands. Resonance adds voices;
        # articulation narrows their staggered entries.
        voice_count = max(2, min(len(notes), round(2 + semantic_density * 5)))
        vowel_notes = notes[-voice_count:]
        for left, right in spans:
            for voice, pitch in enumerate(vowel_notes):
                delay = voice * mix_value(0.68, 0.08, articulation)
                add_note(
                    tracks[1],
                    tempo,
                    composition,
                    start=min(right - 0.06, left + delay),
                    end=max(left + delay + 0.08, right - 0.07),
                    channel=1,
                    pitch=pitch,
                    velocity=round(
                        22 + 32 * resonance + 13 * continuity - voice * 0.7
                    ),
                )

        # Consonant glass: transient edges. Prosody controls grid confidence,
        # articulation controls attack density, and low resonance permits sparks
        # to disagree with the current harmony.
        subdivision = 2 if articulation + semantic_density > 1.12 else 1
        step = beat_seconds / subdivision
        cursor = start + beat_seconds * 0.5
        consonant_index = 0
        while cursor < end - 0.04:
            jitter = (rng.random() - 0.5) * step * 0.48 * (1.0 - prosody)
            event_time = max(start, min(end - 0.04, cursor + jitter))
            probability = 0.16 + 0.70 * articulation
            if rng.random() < probability and not in_silence(composition, event_time):
                pitch = notes[(consonant_index * 3) % len(notes)] + 12
                if resonance < 0.48 and consonant_index % 5 == 0:
                    pitch += 1
                add_note(
                    tracks[2],
                    tempo,
                    composition,
                    start=event_time,
                    end=min(
                        end,
                        event_time + step * (0.10 + 0.26 * continuity),
                    ),
                    channel=2,
                    pitch=pitch,
                    velocity=round(25 + 56 * articulation + 12 * rng.random()),
                )
            consonant_index += 1
            cursor += step

        # Syntax braid: one four-note identity is disclosed over the entire film.
        # Semantic density controls how much of it can be inferred at once.
        motif_length = max(1, min(4, 1 + round(semantic_density * 3)))
        motif_step = beat_seconds * mix_value(2.5, 0.75, prosody)
        cursor = start + beat_seconds
        motif_index = 0
        appearance_count = 0
        while cursor < end - 0.12:
            pitch = motif[motif_index % motif_length]
            octave = 12 if index >= 6 and motif_index % 4 == 3 else 0
            add_note(
                tracks[3],
                tempo,
                composition,
                start=cursor,
                end=min(
                    end,
                    cursor
                    + motif_step * mix_value(0.28, 0.86, continuity),
                ),
                channel=3,
                pitch=pitch + octave,
                velocity=round(28 + 26 * semantic_density + 18 * prosody),
            )
            appearance_count += 1
            motif_index += 1
            cursor += motif_step
        motif_appearances.append(
            {
                "waypoint": waypoint["id"],
                "available_notes": motif[:motif_length],
                "events": appearance_count,
            }
        )

        # Semantic bloom begins once the sentence can reorganize its parts.
        if index >= 6:
            bloom_step = beat_seconds * (4.0 if index < 9 else 3.0)
            cursor = start + beat_seconds * 1.5
            bloom_index = 0
            while cursor < end - 0.2:
                pitch = notes[-1 - (bloom_index % min(4, len(notes)))] + 12
                add_note(
                    tracks[4],
                    tempo,
                    composition,
                    start=cursor,
                    end=min(
                        end,
                        cursor + bloom_step * (0.50 + 0.36 * continuity),
                    ),
                    channel=4,
                    pitch=pitch,
                    velocity=round(24 + 45 * resonance + 8 * semantic_density),
                )
                bloom_index += 1
                cursor += bloom_step

    # The completed continuity motif returns with the recognition sentence.
    return_time = float(composition["recognition_event"]["key_sentence_time"])
    for offset, pitch in enumerate(motif):
        add_note(
            tracks[4],
            tempo,
            composition,
            start=return_time + offset * 0.19,
            end=return_time + 9.4 + offset * 0.31,
            channel=4,
            pitch=pitch + 12,
            velocity=54 - offset * 3,
        )

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
        "continuity_motif": motif,
        "motif_appearances": motif_appearances,
        "silence_windows": composition["score"]["silence_windows"],
        "mapping": {
            "articulation": "consonant attack density, voice-entry precision and spectral edge",
            "continuity": "note overlap, motif sustain and phrase carry",
            "deixis": "root pressure, local register anchoring and call-response bias",
            "resonance": "vowel voice strength, harmonic agreement and semantic bloom",
            "prosody": "grid reliability, motif spacing and accent regularity",
            "semantic_density": "polyphony, available motif notes and harmonic extension",
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


def mix_value(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


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
