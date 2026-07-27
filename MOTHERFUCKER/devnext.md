# DevNext — Build Notes

## 1. Meditation Guide Motif

**Status:** Not built

A new motif for guided meditation content (Vijñāna Bhairava 112 dhāraṇās, breath guides, contemplative reading).

### Scene format
```json
{
  "motif": "meditation-guide",
  "duration": 60,
  "params": {
    "verse": "चैतन्यं प्राणबन्धनम्",
    "transliteration": "Caitanyaṁ prāṇabandhanam",
    "translation": "Consciousness is bound to breath",
    "guide": "Observe the gap where inhalation becomes exhalation",
    "breath": true,
    "chapter": "1. Śiva's First Teaching"
  }
}
```

### What it renders
- Clean dark background (#0D1117 or theme background)
- Expanding/contracting breath circle (reuse `breath-cycle` from anatomy pack or create simpler)
- Verse in Devanagari, centered, large
- Transliteration below, smaller
- Translation at bottom, muted
- Optional guided text that fades in and out
- The breath pulse is the primary animation — everything else is static and timed

### Implementation
- New file: `src/meditation-guide.mjs`
- Register in `motifs.mjs`: `"meditation-guide": renderMeditationGuide`
- Uses existing `fonts.mjs` for Noto Serif Devanagari + Source Serif 4
- No complex moves, no interaction — just timed text display with breath animation
- Scene durations: 30-120s per verse (each dhāraṇā gets one scene)

---

## 2. YouTube → Sleeper Video Pipeline

**Status:** Not built

A pipeline that takes YouTube URLs, extracts audio + captions, curates segments, and produces long ambient videos with minimal visuals.

### Known issue: yt-dlp needs browser cookies
`yt-dlp` inside a headless environment (our vast instance, this machine) cannot access YouTube's age-restricted or logged-in content without cookies. Hermes needs to:
```bash
yt-dlp --cookies-from-browser chromium URL
```
But there's no browser installed on the vast instance and this machine runs headless. **Workaround:** export cookies once from a desktop browser (`Get cookies.txt` extension), upload the file, and use:
```bash
yt-dlp --cookies cookies.txt URL
```

### Pipeline steps
```bash
Step 1: yt-dlp --write-auto-subs --sub-lang en --cookies cookies.txt URL     # gets captions free
Step 2: yt-dlp -x --audio-format mp3 --cookies cookies.txt URL               # downloads audio
Step 3: python3 tools/analyse-audio.py audio.mp3 features.json               # finds quiet/loud sections
Step 4: LLM reads transcript, transcripts + features → picks best segments   # curation
Step 5: ffmpeg concat curated segments into trimmed audio                    # assembly
Step 6: node cli.mjs render sleeper-pack.json                                # renders black screen MP4
Step 7: ffmpeg -i black.mp4 -i curated.mp3 -c:v copy -c:a aac final.mp4     # mux
Step 8: ffmpeg -i final.mp4 -vf "subtitles=curated.vtt" published.mp4       # optional subtitle burn
```

### Sleeper pack format
```json
{
  "version": "1.0",
  "id": "sleeper-dzogchen",
  "render": {"width": 1280, "height": 720, "fps": 24, "crf": 18},
  "theme": "midnightVellum",
  "scenes": [{
    "id": "s01",
    "title": "Long Black Screen",
    "duration": 3600,
    "motif": "logical-argument",
    "params": {"blocks": []}
  }]
}
```

### YouTube API alternative
If `yt-dlp` is unreliable, use the YouTube Data API (we already have quota from the research pipeline at `/root/projects/blog/data/`). `videos.list` and `captions.list` endpoints can download captions. Audio still needs `yt-dlp`.

---

## 3. Voice Cloning Integration

**Status:** Experimental

### Current state
- `edge-tts` works — fast, reliable, 3 voices available
- Qwen3TTS 1.7B cloned voice of Mark Dyczkowski works but slow on RTX 3060

### To speed up Qwen3TTS
- Use FP16 or quantized model (4-bit AWQ)
- Use `llama.cpp` if GGUF available
- Batch inference — generate all narration at once, not per-scene
- Fine-tune a smaller model (e.g. Kokoro 82M) on the cloned voice embedding

### Channel voice assignments
| Channel | Voice | Engine |
|---|---|---|
| Tantrafiles | Sonia (British warm) | edge-tts |
| Ochema | Ryan (British sharp) | edge-tts |
| Anakhya | Custom Sanskrit-trained | Kokoro / Qwen3TTS clone |
| Intelligent Others | Neutral US | edge-tts or Kokoro |

---

## 4. ACE / Music Themes

**Status:** Not built

### Approach
Don't generate per-video. Generate once per channel.
- 3-5 second branded intro/outro for each channel
- Use MusicGen or Stable Audio Open to generate from text prompt
- Render once, prepend/append via ffmpeg concat
- Each channel gets a consistent audio signature

### Channel prompts
- Tantrafiles: warm tanpura + soft bhajan drone
- Ochema: single cello note held, minimal
- Anakhya: temple bells, ambient
- Intelligent Others: synth pad, sub-bass pulse, sci-fi

---

## 5. Shorts Batch Pipeline

**Status:** Specced in `magnum-opus/25-SHORTS-PIPELINE.md`

### Next step
Build `tools/batch-shorts.mjs` — takes a long scene pack → extracts hook, 3 insights, punchline → creates 5 vertical packs → renders all → uploads.

---

## Reference Docs
- `magnum-opus/25-SHORTS-PIPELINE.md` — shorts format and 2-skill system
- `magnum-opus/21-ANAKHYA.md` — platform vision
- `MOTHERFUCKER/AGENT-GUIDE.md` — how to use the framework
- `MOTHERFUCKER/HANDOVER.md` — current state and priorities
