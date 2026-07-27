#!/usr/bin/env python3
"""Hard-gate validation for The Light Becomes a Forest."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

from engine import COMPOSITION_PATH, ROOT, frame_state, load_composition
from generate_score import TempoMap

VALID_RASAS = {
    "shanta",
    "adbhuta",
    "raudra",
    "shringara",
    "vira",
    "karuna",
    "hasya",
    "bhayanaka",
    "bibhatsa",
}
AXES = (
    "radiance",
    "localization",
    "appetite",
    "reciprocity",
    "fecundity",
    "recognition",
)
CONVENTIONAL_LEVELS = {
    36: "Shiva",
    35: "Shakti",
    34: "Sadashiva",
    32: "shuddhavidya",
    31: "maya",
    30: "kala",
    29: "vidya",
    28: "raga",
    26: "niyati",
    25: "purusha",
}


def fail(message: str) -> None:
    raise ValueError(message)


def read_variable_length(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    while True:
        if offset >= len(data):
            fail("truncated MIDI variable-length value")
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, offset


def parse_note_spans(track: bytes) -> list[tuple[int, int, int, int]]:
    offset = 0
    tick = 0
    running_status: int | None = None
    active: dict[tuple[int, int], list[int]] = {}
    spans: list[tuple[int, int, int, int]] = []
    while offset < len(track):
        delta, offset = read_variable_length(track, offset)
        tick += delta
        if offset >= len(track):
            fail("truncated MIDI event")
        status = track[offset]
        if status & 0x80:
            offset += 1
            if status < 0xF0:
                running_status = status
        elif running_status is not None:
            status = running_status
        else:
            fail("MIDI running status used before a channel status")

        if status == 0xFF:
            if offset >= len(track):
                fail("truncated MIDI meta event")
            offset += 1
            payload_length, offset = read_variable_length(track, offset)
            offset += payload_length
            continue
        if status in (0xF0, 0xF7):
            payload_length, offset = read_variable_length(track, offset)
            offset += payload_length
            continue

        message = status & 0xF0
        channel = status & 0x0F
        parameter_count = 1 if message in (0xC0, 0xD0) else 2
        if offset + parameter_count > len(track):
            fail("truncated MIDI channel event")
        first = track[offset]
        second = track[offset + 1] if parameter_count == 2 else 0
        offset += parameter_count
        if message == 0x90 and second > 0:
            active.setdefault((channel, first), []).append(tick)
        elif message == 0x80 or (message == 0x90 and second == 0):
            key = (channel, first)
            starts = active.get(key)
            if not starts:
                fail(f"MIDI note-off has no active note at tick {tick}")
            start = starts.pop(0)
            spans.append((start, tick, channel, first))
            if not starts:
                del active[key]
    if active:
        fail("MIDI contains notes with no note-off")
    return spans


def validate_midi(
    path: Path,
) -> tuple[int, int, int, list[tuple[int, int, int, int]]]:
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        fail("score.mid is missing or has no MIDI header")
    header_length, midi_format, tracks, division = struct.unpack(">IHHH", data[4:14])
    if header_length != 6:
        fail(f"unexpected MIDI header length {header_length}")
    if midi_format != 1:
        fail(f"expected format-1 MIDI, got {midi_format}")
    if data.count(b"MTrk") != tracks:
        fail("MIDI track count does not match track chunks")
    if division != 480:
        fail(f"expected 480 ticks per beat, got {division}")

    offset = 14
    note_spans: list[tuple[int, int, int, int]] = []
    for _ in range(tracks):
        if data[offset : offset + 4] != b"MTrk":
            fail("expected MIDI track chunk")
        length = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
        start = offset + 8
        end = start + length
        if end > len(data):
            fail("truncated MIDI track chunk")
        note_spans.extend(parse_note_spans(data[start:end]))
        offset = end
    if offset != len(data):
        fail("unexpected bytes after final MIDI track")
    return midi_format, tracks, division, note_spans


def validate_checksums(path: Path) -> int:
    entries = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw_line)
        if not match:
            fail(f"malformed SHA256SUMS line: {raw_line!r}")
        expected, relative = match.groups()
        target = (ROOT / relative).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"checksum path escapes the pack: {relative}")
        if not target.is_file():
            fail(f"checksummed file is missing: {relative}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            fail(f"checksum mismatch: {relative}")
        entries += 1
    if entries < 15:
        fail("SHA256SUMS does not cover the complete pack")
    return entries


def main() -> int:
    composition = load_composition()
    duration = float(composition["duration_seconds"])
    if duration != 600.0:
        fail(f"duration must be 600 seconds, got {duration}")

    state_space = composition["state_space"]
    if tuple(state_space["order"]) != AXES:
        fail("Meaning State Vector axis order changed")
    if len(state_space["axes"]) != 6:
        fail("state space must define exactly six axes")

    waypoints = composition["waypoints"]
    if len(waypoints) != 13:
        fail(f"expected 13 waypoints, found {len(waypoints)}")
    times = [float(item["time"]) for item in waypoints]
    if times != sorted(times) or len(times) != len(set(times)):
        fail("waypoint times must be strictly increasing")
    if times[0] != 0.0 or times[-1] != duration:
        fail("trajectory must begin at 0 and end at the film duration")

    ids: set[str] = set()
    verbs: set[str] = set()
    for index, waypoint in enumerate(waypoints):
        if waypoint["index"] != index:
            fail(f"waypoint index mismatch at {waypoint['id']}")
        if waypoint["id"] in ids:
            fail(f"duplicate waypoint id {waypoint['id']}")
        ids.add(waypoint["id"])
        verbs.add(waypoint["visual_verb"])
        state = waypoint["state"]
        if len(state) != 6:
            fail(f"{waypoint['id']} does not have six state values")
        if any(not 0.0 <= float(value) <= 1.0 for value in state):
            fail(f"{waypoint['id']} has an out-of-range state value")
        for rasa in waypoint["rasa"].values():
            if rasa not in VALID_RASAS:
                fail(f"{waypoint['id']} has unknown rasa {rasa}")
        level = int(waypoint["tattva"]["level"])
        name = waypoint["tattva"]["name"]
        if level not in CONVENTIONAL_LEVELS:
            fail(f"{waypoint['id']} uses an unaudited tattva level {level}")
        if name != CONVENTIONAL_LEVELS[level]:
            fail(f"{waypoint['id']} mismatches conventional level {level} and {name}")
        notes = waypoint["music"]["notes"]
        if not 3 <= len(notes) <= 16:
            fail(f"{waypoint['id']} has an invalid chord size")
        if any(not 0 <= int(note) <= 127 for note in notes):
            fail(f"{waypoint['id']} contains an invalid MIDI pitch")
    if len(verbs) != len(waypoints):
        fail("every waypoint must define a distinct primary visual verb")

    recognition = composition["recognition_event"]
    essay = (ROOT / "essay.txt").read_text(encoding="utf-8")
    if recognition["key_sentence"] not in essay:
        fail("recognition sentence is not present verbatim in essay.txt")
    windows = composition["score"]["silence_windows"]
    if len(windows) != 1:
        fail("composition must contain exactly one formal silence aperture")
    window = windows[0]
    if float(window["end"]) - float(window["start"]) != 5.0:
        fail("formal silence aperture must last five seconds")
    if float(window["end"]) != float(recognition["key_sentence_time"]):
        fail("recognition sentence must begin exactly when silence ends")

    words = re.findall(r"\b[\w’'-]+\b", essay)
    if not 1350 <= len(words) <= 1700:
        fail(f"essay word count {len(words)} is outside the ten-minute target")
    semantic_headers = [
        line
        for line in essay.splitlines()
        if re.match(r"^\[\d\d:\d\d–\d\d:\d\d\] [A-Z]", line)
        and "FIVE SECONDS OF SILENCE" not in line
    ]
    if len(semantic_headers) != 12:
        fail(f"expected 12 semantic narration intervals, found {len(semantic_headers)}")

    required = [
        ROOT / "glsl" / "film.glsl",
        ROOT / "glsl" / "forest_fugue.glsl",
        ROOT / "glsl" / "include" / "primitives.glsl",
        ROOT / "glsl" / "include" / "visionary.glsl",
        ROOT / "glsl" / "include" / "cinema.glsl",
        ROOT / "glsl" / "include" / "signature.glsl",
        ROOT / "generate_score.py",
        ROOT / "render-audio.py",
        ROOT / "render.py",
        ROOT / "score.mid",
        ROOT / "score_manifest.json",
        ROOT / "ARCHITECTURE-ANALYSIS.md",
        ROOT / "CREATIVE-PROCESS-NOTES.md",
        ROOT / "REVIEW.md",
        ROOT / "SOURCES.md",
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "SHA256SUMS",
    ]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        fail(f"missing deliverables: {', '.join(missing)}")
    checksum_entries = validate_checksums(ROOT / "SHA256SUMS")

    midi_format, tracks, division, note_spans = validate_midi(ROOT / "score.mid")
    manifest = json.loads((ROOT / "score_manifest.json").read_text(encoding="utf-8"))
    expected_hash = hashlib.sha256(COMPOSITION_PATH.read_bytes()).hexdigest()
    if manifest["composition_sha256"] != expected_hash:
        fail("score manifest was not generated from the current composition")
    if manifest["duration_seconds"] != duration:
        fail("score manifest duration mismatch")
    if len(note_spans) != manifest["event_counts"]["note_on"]:
        fail("manifest note count does not match actual MIDI note intervals")
    subject = manifest["fugue_subject"]
    if subject["intervals"] != composition["score"]["fugue_subject_intervals"]:
        fail("manifest fugue subject differs from composition")
    if subject["beats"] != composition["score"]["fugue_subject_beats"]:
        fail("manifest fugue rhythm differs from composition")
    appearances = subject["appearances"]
    if len(appearances) < 48:
        fail("fugue subject is not developed often enough across the film")
    transforms = {appearance["transform"] for appearance in appearances}
    expected_transforms = {
        "original",
        "inversion",
        "augmentation",
        "diminution",
        "retrograde",
        "inverse-augmentation",
    }
    missing_transforms = expected_transforms - transforms
    if missing_transforms:
        fail(
            "fugue development is missing: "
            + ", ".join(sorted(missing_transforms))
        )

    tempo = TempoMap(composition)
    silence_start_tick = tempo.seconds_to_tick(float(window["start"]))
    silence_end_tick = tempo.seconds_to_tick(float(window["end"]))
    leaking_notes = [
        span
        for span in note_spans
        if span[0] < silence_end_tick and span[1] > silence_start_tick
    ]
    if leaking_notes:
        fail(f"{len(leaking_notes)} MIDI notes sound during formal silence")
    sentence_tick = tempo.seconds_to_tick(float(recognition["key_sentence_time"]))
    if not any(span[0] == sentence_tick for span in note_spans):
        fail("completed motif does not return with the recognition sentence")

    samples = [0.0, 304.0, 539.9, 540.0, 542.5, 544.999, 545.0, 548.0, 599.9]
    states = [frame_state(composition, value) for value in samples]
    if any(
        state.audio_volume != 0.0
        or state.audio_beat != 0.0
        or any(state.music_a)
        or any(state.music_b)
        for state in states[3:6]
    ):
        fail("silence aperture still emits audio-derived visual features")
    if states[6].audio_volume <= 0.0 or not any(states[6].music_a):
        fail("visual audio energy does not return with the key sentence")

    print(
        "PASS composition:",
        f"{len(waypoints)} waypoints,",
        f"{len(words)} narration words,",
        f"{len(verbs)} visual verbs",
    )
    print(
        "PASS score:",
        f"MIDI format {midi_format}, {tracks} tracks, {division} ticks/beat,",
        f"{manifest['event_counts']['note_on']} notes",
    )
    print(
        "PASS fugue:",
        f"{len(appearances)} explicit subject entries,",
        f"{len(transforms)} transformations",
    )
    print("PASS integrity:", f"{checksum_entries} checksummed files")
    print("PASS literal five-second MIDI silence and subject-synchronous recognition")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
