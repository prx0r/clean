# Tool Contracts

## Audio analyzer

Input:

```json
{
  "audio_path": "audio.wav",
  "output_path": "features.json"
}
```

Output: audio feature manifest version `1.0`.

## Narration analyzer

Input:

```json
{
  "timing_manifest": "narration-words.json",
  "semantic_events": "narration-events.json"
}
```

Output: narration feature manifest version `1.0`.

## Scene renderer

Input:

```json
{
  "scene_pack": "film.json",
  "audio_features": "music-features.json",
  "narration_features": "narration-features.json",
  "score_features": "score-features.json"
}
```

Output:

- frames;
- contact sheet;
- silent video;
- validation report.

## Muxer

Input:

- silent video;
- final audio mix.

Output:

- final publication MP4.
