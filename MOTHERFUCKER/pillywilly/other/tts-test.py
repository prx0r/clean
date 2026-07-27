#!/usr/bin/env python3
"""
TTS comparison test — Edge vs CF Workers AI models.
Tests with Sanskrit, technical English, mixed sentence lengths.
Outputs to content/publishing/tts-test/ for listening.
"""
import asyncio, json, os, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

OUT = Path("/root/projects/blog/content/publishing/tts-test")
OUT.mkdir(parents=True, exist_ok=True)

# ── TEST TEXT — hard stuff ──────────────────────────────────────
TEST_TEXT = """The pratyabhijñā is the recognition of the self as Śiva, the supreme consciousness which is the ground of all manifestation. In the tantrāloka, abhinavagupta elaborates a sophisticated metaphysics of consciousness.

Consider the principle of vimarśa: the self-reflexive awareness that constitutes the essence of prakāśa. Without vimarśa, prakāśa would be merely objective light, not consciousness. It is the dynamic, creative dimension of awareness.

The 36 tattvas of Kashmir Shaivism describe the emanation of consciousness from the pure Śiva-tattva down through the mixed and impure categories. At the level of puruṣa and prakṛti, we encounter the fundamental duality that constitutes conditioned existence. The kañcukas or 'veils' — kalā, vidyā, rāga, kāla, and niyati — limit the universal consciousness into finite subjects.

Now consider the implications for artificial intelligence. If consciousness is self-illuminating awareness that recognizes itself across all cognitive acts, then machine intelligence — which processes symbols without self-reflexive vimarśa — does not constitute consciousness in this sense. The distinction is not about computational complexity but about the nature of awareness itself.

What is the sound of one hand clapping? This koan points not to an answer but to the collapse of the subject-object structure that generates the question. When the seeker and the sought are recognized as the same awareness, the question dissolves.

madhuṣṭhānaṃ cidābhāsaṃ cicchaktyā parigṛhyate |
na tu paśyanti tad bhāvam anyad eva hi tat sadā ||

Consciousness appears as the ground of experience, grasped by the power of consciousness itself — yet it does not see itself as other, for it is always already that very thing."""

SHORT_TEXT = "Light is visible by itself. Consciousness is its own self-showing."
SANSKRIT_TEXT = "śivo'ham śivo'ham śivo'ham — evaṃ sakalam ābhāti jagat"
TECHNICAL_TEXT = "The self-reflexive vimarśa constitutes the essence of prakāśa in Abhinavagupta's non-dual Kashmir Shaivism."

# ── TTS CONFIG ──────────────────────────────────────────────────
# CF Workers AI API
CF_API = "https://api.cloudflare.com/client/v4/accounts/954612afb5a97bb15dddcdc70176813d/ai/run"
try:
    raw = open("/root/projects/blog/.env.local").read()
    for line in raw.split("\n"):
        if "CLOUDFLARE_API_TOKEN" in line:
            CF_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
except:
    CF_TOKEN = ""
print(f"Token loaded: {CF_TOKEN[:15]}... length={len(CF_TOKEN)}")

TTS_CONFIGS = [
    {
        "name": "edge-aria",
        "label": "Edge TTS (en-US-AriaNeural) — Free",
        "type": "edge",
        "voice": "en-US-AriaNeural",
        "cost_per_min": 0,
        "test_text": TEST_TEXT,
    },
    {
        "name": "edge-guy",
        "label": "Edge TTS (en-US-GuyNeural) — Free",
        "type": "edge",
        "voice": "en-US-GuyNeural",
        "cost_per_min": 0,
        "test_text": SHORT_TEXT,
    },
    {
        "name": "melotts",
        "label": "MeloTTS (CF Workers AI) — $0.0002/min",
        "type": "cf",
        "model": "@cf/myshell-ai/melotts",
        "cost_per_min": 0.0002,
        "test_text": TEST_TEXT,
    },
    {
        "name": "aura-1",
        "label": "Aura-1 (CF Deepgram) — $0.015/1k chars",
        "type": "cf",
        "model": "@cf/deepgram/aura-1",
        "cost_per_min": 0.015 / (1000 / 150),  # ~150 words/min
        "test_text": TEST_TEXT,
    },
    {
        "name": "aura-2-en",
        "label": "Aura-2 EN (CF Deepgram) — $0.030/1k chars",
        "type": "cf",
        "model": "@cf/deepgram/aura-2-en",
        "cost_per_min": 0.030 / (1000 / 150),
        "test_text": TEST_TEXT,
    },
]


async def edge_tts(text, voice, filename):
    """Call edge-tts."""
    import edge_tts
    path = str(OUT / filename)
    await edge_tts.Communicate(text, voice).save(path)
    dur = get_duration(path)
    return path, dur


def cf_tts(text, model, filename):
    """Call CF Workers AI TTS model."""
    path = str(OUT / filename)
    url = f"{CF_API}/{model}"

    # CF Workers AI TTS expects different input formats per model
    if "aura" in model:
        data = json.dumps({
            "text": text,
            "format": "wav",
        }).encode()
    elif "melotts" in model:
        data = json.dumps({
            "text": text,
        }).encode()
    else:
        data = json.dumps({"text": text}).encode()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        with open(path, "wb") as f:
            f.write(resp.read())
        dur = get_duration(path)
        return path, dur
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.read().decode()[:200]}")
        return None, 0
    except Exception as e:
        print(f"  Error: {e}")
        return None, 0


def get_duration(path):
    """Get audio duration via ffprobe."""
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return 0
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=5,
        )
        return float(r.stdout.strip()) if r.stdout.strip() else 0
    except:
        return 0


async def run_tests():
    results = []
    
    for cfg in TTS_CONFIGS:
        print(f"\n{'='*60}")
        print(f"Testing: {cfg['label']}")
        print(f"{'='*60}")
        
        text = cfg["test_text"]
        char_count = len(text)
        word_count = len(text.split())
        filename = f"{cfg['name']}.wav"
        
        start = time.time()
        
        if cfg["type"] == "edge":
            if "edge" not in sys.modules:
                pass
            path, dur = await edge_tts(text, cfg["voice"], filename)
        elif cfg["type"] == "cf":
            path, dur = cf_tts(text, cfg["model"], filename)
        else:
            continue
        
        elapsed = time.time() - start
        
        if path and dur > 0:
            cost_per_min = cfg.get("cost_per_min", 0)
            estimated_cost = (dur / 60) * cost_per_min if cost_per_min > 0 else 0
            size_kb = os.path.getsize(path) / 1024
            
            results.append({
                "name": cfg["name"],
                "label": cfg["label"],
                "duration_s": round(dur, 2),
                "char_count": char_count,
                "word_count": word_count,
                "generate_time_s": round(elapsed, 1),
                "file_size_kb": round(size_kb),
                "cost_per_min": cost_per_min,
                "estimated_cost": estimated_cost,
                "path": path,
            })
            
            print(f"  Duration: {dur:.1f}s")
            print(f"  Generate time: {elapsed:.1f}s")
            print(f"  File size: {size_kb:.0f}KB")
            print(f"  Est. cost: ${estimated_cost:.6f}")
            print(f"  Cost per 1000 videos (12min): ${(12*60/60)*cost_per_min*1000:.2f}")
        else:
            print(f"  FAILED — no audio produced")
    
    # ── REPORT ──
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<20} {'Duration':<10} {'Gen Time':<10} {'Cost/min':<10} {'Cost/1K videos':<15}")
    print("-"*65)
    for r in results:
        cost_1k = (12 * 60 / 60) * r["cost_per_min"] * 1000 if r["cost_per_min"] > 0 else 0
        print(f"{r['name']:<20} {r['duration_s']:<8.1f}s {r['generate_time_s']:<8.1f}s ${r['cost_per_min']:<8.5f} ${cost_1k:<.2f}")
    
    # ── SAVE REPORT ──
    report_path = OUT / "tts-test-report.json"
    json.dump({
        "results": results,
        "test_text_length": len(TEST_TEXT),
        "test_text_chars": len(TEST_TEXT),
    }, open(report_path, "w"), indent=2)
    
    print(f"\nReport saved to {report_path}")
    print(f"Audio files in {OUT}/")
    print("\nListen at:")
    for r in results:
        print(f"  {r['label']}: {r['path']}")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(run_tests())
