#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import librosa
import numpy as np

def normalize(values: np.ndarray, percentile: float = 99.0) -> np.ndarray:
    values = np.nan_to_num(values.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    scale = np.percentile(np.abs(values), percentile) if values.size else 1.0
    return np.zeros_like(values) if scale <= 1e-12 else np.clip(values / scale, 0.0, 1.0)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--hop-length", type=int, default=512)
    args = parser.parse_args()
    y, sr = librosa.load(args.input, sr=args.sample_rate, mono=True)
    harmonic, percussive = librosa.effects.hpss(y)
    rms = librosa.feature.rms(y=y, hop_length=args.hop_length)[0]
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=args.hop_length)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=args.hop_length, sparse=True)
    pulse = librosa.beat.plp(onset_envelope=onset, sr=sr, hop_length=args.hop_length)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=args.hop_length)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=args.hop_length)[0]
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    harmonic_rms = librosa.feature.rms(y=harmonic, hop_length=args.hop_length)[0]
    percussive_rms = librosa.feature.rms(y=percussive, hop_length=args.hop_length)[0]
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=sr, hop_length=args.hop_length)
    tonnetz = librosa.feature.tonnetz(y=harmonic, sr=sr)
    f0, _, voiced_probability = librosa.pyin(
        harmonic,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        hop_length=args.hop_length,
    )
    beat_pulse = np.zeros_like(onset)
    for beat in np.asarray(beats, dtype=int):
        if 0 <= beat < len(beat_pulse):
            beat_pulse[beat] = 1.0
    features = {
        "rms": normalize(rms),
        "onset": normalize(onset),
        "beatPulse": beat_pulse,
        "localPulse": normalize(pulse),
        "harmonicEnergy": normalize(harmonic_rms),
        "percussiveEnergy": normalize(percussive_rms),
        "spectralCentroid": normalize(centroid),
        "spectralBandwidth": normalize(bandwidth),
        "spectralFlatness": normalize(flatness),
        "chroma": np.nan_to_num(chroma.T, nan=0.0),
        "tonnetz": np.nan_to_num(tonnetz.T, nan=0.0),
        "f0": np.nan_to_num(f0, nan=0.0),
        "voicedProbability": np.nan_to_num(voiced_probability, nan=0.0),
        "tempo": np.full_like(rms, float(np.asarray(tempo).reshape(-1)[0])),
    }
    frame_count = min(len(v) if v.ndim == 1 else v.shape[0] for v in features.values())
    times = librosa.frames_to_time(np.arange(frame_count), sr=sr, hop_length=args.hop_length)
    frames = []
    for index, time in enumerate(times):
        frame = {"time": round(float(time), 6)}
        for name, values in features.items():
            frame[name] = (
                round(float(values[index]), 6)
                if values.ndim == 1
                else [round(float(v), 6) for v in values[index]]
            )
        frames.append(frame)
    payload = {
        "version":"1.0",
        "input":Path(args.input).name,
        "sampleRate":sr,
        "hopLength":args.hop_length,
        "duration":round(float(librosa.get_duration(y=y, sr=sr)),6),
        "frames":frames,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",",":")), encoding="utf-8")

if __name__ == "__main__":
    main()
