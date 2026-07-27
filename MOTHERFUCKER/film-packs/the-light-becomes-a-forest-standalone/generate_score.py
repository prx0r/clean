#!/usr/bin/env python3
"""Compose the original six-voice contrapuntal score as format-1 MIDI."""
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
        raise ValueError("negative MIDI variable-length value")
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
    """Exact seconds/ticks map shared by generation, rendering, and validation."""

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
                return self.segment_ticks[index] + round(
                    local * bpm / 60.0 * TPB
                )
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
        revised: list[tuple[float, float]] = []
        for left, right in spans:
            if right <= silence_start or left >= silence_end:
                revised.append((left, right))
            else:
                if left < silence_start:
                    revised.append((left, silence_start))
                if right > silence_end:
                    revised.append((silence_end, right))
        spans = revised
    return [(left, right) for left, right in spans if right - left >= 0.025]


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
) -> int:
    if end <= start:
        return 0
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))
    written = 0
    for playable_start, playable_end in playable_spans(composition, start, end):
        start_tick = tempo.seconds_to_tick(playable_start)
        end_tick = max(start_tick + 1, tempo.seconds_to_tick(playable_end))
        events.append(
            MidiEvent(start_tick, 2, bytes((0x90 | channel, pitch, velocity)))
        )
        events.append(MidiEvent(end_tick, 0, bytes((0x80 | channel, pitch, 0))))
        written += 1
    return written


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


def nearest_pitch(reference: int, pitch_class: int) -> int:
    candidates = [
        pitch
        for pitch in range(max(0, reference - 12), min(127, reference + 12) + 1)
        if pitch % 12 == pitch_class % 12
    ]
    return min(candidates, key=lambda pitch: abs(pitch - reference))


def subject_material(composition: dict) -> tuple[list[int], list[float]]:
    score = composition["score"]
    return (
        [int(value) for value in score["fugue_subject_intervals"]],
        [float(value) for value in score["fugue_subject_beats"]],
    )


def write_subject(
    events: list[MidiEvent],
    tempo: TempoMap,
    composition: dict,
    *,
    start: float,
    beat_seconds: float,
    channel: int,
    tonic: int,
    velocity: int,
    completeness: float,
    transform: str,
    duration_scale: float = 1.0,
    transpose: int = 0,
) -> tuple[float, int]:
    intervals, durations = subject_material(composition)
    count = max(3, min(len(intervals), round(3 + completeness * 9)))
    cursor = start
    written = 0
    for index, (interval, beats) in enumerate(zip(intervals[:count], durations[:count])):
        if transform in {"inversion", "inverse-augmentation"}:
            interval = -interval
        source_index = count - 1 - index if transform == "retrograde" else index
        if transform == "retrograde":
            interval = intervals[source_index]
            beats = durations[source_index]
        scale = duration_scale
        if transform in {"augmentation", "inverse-augmentation"}:
            scale *= 1.75
        elif transform == "diminution":
            scale *= 0.58
        note_length = beats * beat_seconds * scale
        pitch = tonic + interval + transpose
        articulation = 0.92 if transform != "augmentation" else 0.97
        written += add_note(
            events,
            tempo,
            composition,
            start=cursor,
            end=cursor + note_length * articulation,
            channel=channel,
            pitch=pitch,
            velocity=velocity - (index % 4) * 2,
        )
        cursor += note_length
    return cursor, written


def write_countersubject(
    events: list[MidiEvent],
    tempo: TempoMap,
    composition: dict,
    *,
    start: float,
    end: float,
    beat_seconds: float,
    channel: int,
    register: int,
    progression: list[list[int]],
    reciprocity: float,
    velocity: int,
) -> int:
    pattern = [0, -2, -4, -5, -3, -1, 1, 0]
    cursor = start
    index = 0
    written = 0
    step = beat_seconds * (1.0 if reciprocity < 0.72 else 0.5)
    while cursor < end - 0.04:
        chord = progression[(index // 4) % len(progression)]
        target_pc = chord[index % len(chord)]
        reference = register + pattern[index % len(pattern)]
        pitch = nearest_pitch(reference, target_pc)
        written += add_note(
            events,
            tempo,
            composition,
            start=cursor,
            end=min(end, cursor + step * (0.72 + 0.22 * reciprocity)),
            channel=channel,
            pitch=pitch,
            velocity=velocity - index % 3,
        )
        cursor += step
        index += 1
    return written


def stage_transforms(stage: int) -> list[str]:
    return {
        0: ["original"],
        1: ["original", "original"],
        2: ["original", "original", "inversion"],
        3: ["diminution", "inversion", "original"],
        4: ["original", "inversion", "original"],
        5: ["original", "retrograde", "inversion"],
        6: ["augmentation", "original", "diminution", "inversion"],
        7: ["original", "inversion", "diminution", "retrograde", "original"],
        8: ["inversion", "original", "retrograde", "original"],
        9: ["original", "inversion", "diminution", "retrograde", "augmentation", "original"],
        10: ["augmentation", "inverse-augmentation", "augmentation", "original", "inversion"],
        11: ["original", "inversion", "augmentation", "diminution", "retrograde", "original"],
    }.get(stage, ["original"])


def compose() -> tuple[bytes, dict]:
    composition = load_composition()
    waypoints = composition["waypoints"]
    tempo = TempoMap(composition)
    duration = float(composition["duration_seconds"])
    end_tick = tempo.seconds_to_tick(duration)
    rng = random.Random(0x51A7A)

    conductor: list[MidiEvent] = [MidiEvent(0, 0, meta(0x03, b"Conductor"))]
    tracks = [
        program_track("Earth Cello", 0, 42, volume=92, pan=24),
        program_track("Root Viola", 1, 41, volume=88, pan=43),
        program_track("Leaf Violin", 2, 40, volume=90, pan=64),
        program_track("Wind Flute", 3, 73, volume=86, pan=86),
        program_track("Light Oboe", 4, 68, volume=88, pan=105),
        program_track("River Harpsichord", 5, 6, volume=82, pan=68),
    ]
    registers = [38, 50, 62, 74, 78, 55]
    event_counts = {"note_on": 0, "tempo": 0, "marker": 0}
    stage_analysis: list[dict] = []
    subject_appearances: list[dict] = []

    for stage, waypoint in enumerate(waypoints[:-1]):
        start = float(waypoint["time"])
        end = float(waypoints[stage + 1]["time"])
        bpm = float(waypoint["music"]["bpm"])
        beat = 60.0 / bpm
        bar = beat * 4.0
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

        radiance, localization, appetite, reciprocity, fecundity, recognition = (
            float(value) for value in waypoint["state"]
        )
        progression = [
            [int(value) % 12 for value in chord]
            for chord in waypoint["music"]["progression"]
        ]
        voice_ids = [int(value) for value in waypoint["music"]["subject_voices"]]
        transforms = stage_transforms(stage)
        stage_note_start = sum(
            1
            for track in tracks
            for event in track
            if len(event.data) >= 3 and event.data[0] & 0xF0 == 0x90
        )

        # River harpsichord: broken harmonic current, never a sustained drone.
        subdivision = 4 if fecundity > 0.72 else 2
        step = beat / subdivision
        cursor = start
        continuo_index = 0
        while cursor < end - 0.025:
            chord = progression[(continuo_index // (subdivision * 4)) % len(progression)]
            contour = [0, 1, 2, 1, 0, 2, 1, 2]
            pitch_class = chord[contour[continuo_index % len(contour)] % len(chord)]
            octave_lift = 12 if continuo_index % 8 in (3, 6) else 0
            pitch = nearest_pitch(55 + octave_lift, pitch_class)
            velocity = round(28 + 20 * fecundity + 11 * radiance)
            add_note(
                tracks[5],
                tempo,
                composition,
                start=cursor,
                end=min(end, cursor + step * 0.55),
                channel=5,
                pitch=pitch,
                velocity=velocity,
            )
            cursor += step
            continuo_index += 1

        # Earth cello: walking ground whose approach tones embody appetite.
        cursor = start
        bass_index = 0
        while cursor < end - 0.05:
            chord = progression[(bass_index // 4) % len(progression)]
            pitch_class = chord[0 if bass_index % 4 in (0, 2) else -1]
            pitch = nearest_pitch(38 + (bass_index % 4 == 3) * 3, pitch_class)
            if appetite > 0.68 and bass_index % 4 == 3:
                pitch += -1 if (bass_index // 4) % 2 else 1
            add_note(
                tracks[0],
                tempo,
                composition,
                start=cursor,
                end=min(end, cursor + beat * (0.78 + 0.16 * reciprocity)),
                channel=0,
                pitch=pitch,
                velocity=round(34 + 26 * appetite + 10 * localization),
            )
            cursor += beat
            bass_index += 1

        # Prelude fragments let the subject germinate before formal exposition.
        if stage == 0:
            fragment_cursor = start + bar * 0.75
            while fragment_cursor < end - beat:
                _, written = write_subject(
                    tracks[4],
                    tempo,
                    composition,
                    start=fragment_cursor,
                    beat_seconds=beat,
                    channel=4,
                    tonic=74,
                    velocity=42,
                    completeness=0.08 + 0.12 * recognition,
                    transform="original",
                    duration_scale=1.15,
                )
                subject_appearances.append(
                    {
                        "stage": waypoint["id"],
                        "voice": "Light Oboe",
                        "time": round(fragment_cursor, 3),
                        "transform": "fragment",
                        "notes": written,
                    }
                )
                fragment_cursor += bar * 3.0
        else:
            # Formal entries. Stretto narrows the delay; reciprocity increases
            # how soon another voice can answer without erasing the first.
            entry_gap = bar * mix_value(2.1, 0.62, fecundity)
            if stage == 7:
                entry_gap = bar * 0.48
            elif stage == 10:
                entry_gap = bar * 1.25
            entry_base = start + beat * (0.5 if stage in (7, 9, 11) else 1.0)
            for appearance, voice in enumerate(voice_ids):
                entry = entry_base + appearance * entry_gap
                if entry >= end - beat:
                    break
                transform = transforms[appearance % len(transforms)]
                transpose = 7 if appearance % 2 and transform == "original" else 0
                if stage == 5 and appearance == 1:
                    transpose += 1
                completeness = clamp_value(
                    0.40 + recognition * 0.62 + fecundity * 0.10,
                    0.35,
                    1.0,
                )
                tonic = registers[voice]
                finish, written = write_subject(
                    tracks[voice],
                    tempo,
                    composition,
                    start=entry,
                    beat_seconds=beat,
                    channel=voice,
                    tonic=tonic,
                    velocity=round(
                        42
                        + 18 * recognition
                        + 12 * localization
                        + 7 * radiance
                    ),
                    completeness=completeness,
                    transform=transform,
                    duration_scale=1.0,
                    transpose=transpose,
                )
                subject_appearances.append(
                    {
                        "stage": waypoint["id"],
                        "voice": composition["score"]["tracks"][voice],
                        "time": round(entry, 3),
                        "end": round(min(finish, end), 3),
                        "transform": transform,
                        "notes": written,
                    }
                )

        # Independent countersubjects fill the voices not carrying an entry.
        melodic_voices = [1, 2, 3, 4]
        counter_count = max(1, min(4, round(1 + fecundity * 3)))
        ordered = sorted(
            melodic_voices,
            key=lambda voice: (voice not in voice_ids, rng.random()),
        )
        for voice in ordered[:counter_count]:
            counter_start = start + beat * (1.5 + voice * 0.31)
            write_countersubject(
                tracks[voice],
                tempo,
                composition,
                start=counter_start,
                end=end,
                beat_seconds=beat,
                channel=voice,
                register=registers[voice],
                progression=progression,
                reciprocity=reciprocity,
                velocity=round(28 + 18 * reciprocity + 10 * fecundity),
            )

        # Appetitive ornaments are brief approach notes, not random sparkle.
        if appetite > 0.55:
            ornament_step = bar * mix_value(1.5, 0.5, fecundity)
            cursor = start + bar * 0.5
            ornament_index = 0
            while cursor < end - 0.1:
                voice = 2 + ornament_index % 3
                chord = progression[ornament_index % len(progression)]
                destination = nearest_pitch(registers[voice], chord[-1])
                approach = destination + (-1 if ornament_index % 2 else 1)
                add_note(
                    tracks[voice],
                    tempo,
                    composition,
                    start=cursor,
                    end=min(end, cursor + beat * 0.18),
                    channel=voice,
                    pitch=approach,
                    velocity=round(24 + 30 * appetite),
                )
                cursor += ornament_step
                ornament_index += 1

        stage_note_end = sum(
            1
            for track in tracks
            for event in track
            if len(event.data) >= 3 and event.data[0] & 0xF0 == 0x90
        )
        stage_analysis.append(
            {
                "id": waypoint["id"],
                "time": start,
                "bpm": bpm,
                "harmony": waypoint["music"]["chord"],
                "technique": waypoint["music"]["fugue_technique"],
                "note_events": stage_note_end - stage_note_start,
                "state": waypoint["state"],
            }
        )

    # Cadential gathering: five voices arrive, release, and leave an exact
    # five-second aperture. The note clipping layer guarantees the silence.
    cadence = float(composition["recognition_event"]["cadence_time"])
    for voice, pitch in enumerate((38, 50, 57, 62, 66)):
        add_note(
            tracks[voice],
            tempo,
            composition,
            start=cadence - 3.4 + voice * 0.13,
            end=540.0,
            channel=voice,
            pitch=pitch,
            velocity=62 - voice * 3,
        )

    # Recognition: the complete subject returns at the exact first syllable,
    # answered in augmentation and inversion before the final exposition.
    return_time = float(composition["recognition_event"]["key_sentence_time"])
    return_beat = 60.0 / float(waypoints[10]["music"]["bpm"])
    for voice, transform, delay in (
        (2, "original", 0.0),
        (4, "inversion", 0.0),
        (1, "augmentation", 0.24),
        (3, "original", 0.48),
    ):
        _, written = write_subject(
            tracks[voice],
            tempo,
            composition,
            start=return_time + delay,
            beat_seconds=return_beat,
            channel=voice,
            tonic=registers[voice],
            velocity=62 - voice,
            completeness=1.0,
            transform=transform,
            duration_scale=0.72,
        )
        subject_appearances.append(
            {
                "stage": "recognition_return",
                "voice": composition["score"]["tracks"][voice],
                "time": return_time + delay,
                "transform": transform,
                "notes": written,
            }
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
        "duration_seconds": duration,
        "ticks_per_beat": TPB,
        "track_count": len(chunks),
        "event_counts": event_counts,
        "fugue_subject": {
            "tonal_center": composition["score"]["tonal_center_name"],
            "intervals": composition["score"]["fugue_subject_intervals"],
            "beats": composition["score"]["fugue_subject_beats"],
            "appearances": subject_appearances,
        },
        "silence_windows": composition["score"]["silence_windows"],
        "state_mapping": {
            "radiance": "upper partial openness, common-tone light, and consonant availability",
            "localization": "registral independence, spatial separation, and subject ownership",
            "appetite": "dominant pressure, approach tones, syncopation, and walking-bass direction",
            "reciprocity": "imitation delay, countersubject exchange, overlap, and suspension resolution",
            "fecundity": "voice count, subdivision, ornament, sequence, and stretto density",
            "recognition": "subject completeness and invariance across transformation",
        },
        "stages": stage_analysis,
    }
    return midi, manifest


def mix_value(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def clamp_value(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


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
    print(
        "Wrote score_manifest.json "
        f"({len(manifest['fugue_subject']['appearances'])} subject entries)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
