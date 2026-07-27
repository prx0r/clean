# Shorts Pipeline

## Principle

A short is not a clip from a long video. It is a **separate artifact** with the same relationship to the source essay as the long video: one claim, one punchline, fast.

## Two Skills

### Skill 1: `extract-short-ideas`
Input: scene pack or essay markdown
Output: 3-5 short concept cards

For each card:
- One-sentence hook (the claim)
- Target duration (15-60s based on hook complexity)
- Suggested title (informed by YouTube title pattern data from `/root/projects/blog/data/research/layer2/`)
- Reference to the source scene(s) in the long pack

The YouTube data (analysis of 30+ channels) tells us which title patterns drive breakouts — Asangoham's best performing titles start with "The" (0.78 breakout rate) vs "Why" (0.03). This data should inform short titles directly.

### Skill 2: `create-short`
Input: short concept card
Output: 1080×1920 vertical MP4 with TTS

## Short Format

Same scene format as everything else, just vertical:

```json
{
  "render": {"width": 1080, "height": 1920, "fps": 24, "crf": 14},
  "scenes": [
    {"motif": "argument-diagram", "duration": 6, "params": {"moves": [
      {"type": "claim", "text": "**The hook**", "size": 52}
    ]}},
    {"motif": "argument-diagram", "duration": 10, "params": {"moves": [
      {"type": "claim", "text": "The insight", "size": 40},
      {"type": "subclaim", "text": "Why it matters", "y": 500, "size": 24}
    ]}},
    {"motif": "argument-diagram", "duration": 6, "params": {"moves": [
      {"type": "converge", "text": "The punchline"}
    ]}}
  ]
}
```

## Pacing for Shorts

Based on the gold standard data:
- **3-5 scenes per short** (hook → build → punchline)
- **5-8 seconds per scene** (faster than long-form 6-12s)
- **Text fills 60-80% of vertical frame** (not 30-40% like horizontal)
- **No footer, no border, no devanagari** — screen space is at a premium
- **Bold hooks** — every short starts with a `**bold claim**` at 48-56px

## Vertical Resolution

1080×1920 (9:16). The motif handles this automatically — `argument-diagram` already centers all content. Just change `render.width` and `render.height`.

## YouTube Title Data Reference

From `/root/projects/blog/data/research/layer2/` — channel analysis shows:
- Best breakout titles start with "The" (+0.24 delta)
- Question titles ("What...", "Why...") underperform for this genre
- Optimal title length: 7-8 words
- Best performing format: "The [X] Of [Y]" or "[Subject]: [Claim]"

This data is analysed per-channel in `analysis_*.json` files and should be consulted per short.

## From Long-Form to Shorts

1. Take the long-form scene pack's claim and subclaim moves
2. The hook is the first claim, the punchline is the last converge or claim
3. Extract 3-5 intermediate insights as their own shorts
4. Each short gets 3-5 scenes from the original, adapted to vertical
5. Titles use the YouTube data patterns

## Short Types

| Type | Scenes | Duration | Purpose |
|---|---|---|---|
| Hook | 1-2 | 8-15s | Single provocative claim, drives to long video |
| Core insight | 3-4 | 20-30s | One complete argument, standalone |
| Trailer | 4-5 | 40-60s | Sequence of key claims, drives to channel |
