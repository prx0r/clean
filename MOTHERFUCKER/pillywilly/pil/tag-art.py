#!/usr/bin/env python3
"""Tag untagged artwork using vision LLM. Also generate CLIP-style embeddings for similarity.

Usage:
  python3 scripts/tag-art.py                          # tag all untagged art
  python3 scripts/tag-art.py --image public/art/x.jpg # tag single image
  python3 scripts/tag-art.py --embeddings             # generate embeddings only
  python3 scripts/tag-art.py --dry-run                # preview what would be tagged

Requires:
  - VIDEO_LLM_API_KEY in environment (opencode endpoint with mimo-v2-omni for vision)
  - Or CF_ACCOUNT_ID + CF_API_TOKEN for Cloudflare Workers AI (Llama vision)
"""

import json, os, sys, base64, subprocess
from PIL import Image

ROOT = "/root/projects/blog"
ART_DIR = os.path.join(ROOT, "content", "glossary", "art")
IMG_DIR = os.path.join(ROOT, "public", "art")
ALCHEMY_DIR = os.path.join(ROOT, "content", "sources", "occult", "alchemy", "emblems")

# OpenCode API config
# Try Cloudflare Workers AI first (free), fall back to opencode (paid)
CF_ACCOUNT = os.environ.get("CF_ACCOUNT_ID")
CF_TOKEN = os.environ.get("CF_API_TOKEN")

API_KEY = os.environ.get("VIDEO_LLM_API_KEY")
if not API_KEY:
    raise ValueError("Set VIDEO_LLM_API_KEY environment variable")
BASE_URL = "https://opencode.ai/zen/go/v1"
VISION_MODEL_OPENCODE = "mimo-v2-omni"
VISION_MODEL_CF = "@cf/meta/llama-3.2-11b-vision-instruct"

CONCEPT_TAXONOMY = [
    "Unity", "Transformation", "Beauty", "Imagination", "Perception",
    "Imaginal World", "Correspondence", "Divine Order", "Ascent",
    "Sacred Matter", "Purification", "Angel", "Theophany", "Revelation",
    "Cosmology", "Macrocosm", "Microcosm", "Liberation", "Divine Love",
    "Creative Imagination", "Mundus Imaginalis", "Perfect Nature",
    "Cosmic", "Visionary", "Mystical", "Contemplative", "Antique",
    "Sacred", "Illuminated", "Alchemical"
]

MOOD_TAXONOMY = ["mystical", "visionary", "contemplative", "antique", "cosmic",
                  "austere", "symbolic", "illuminated", "sacred", "dreamlike",
                  "dramatic", "serene", "dark", "radiant", "intimate"]

STYLE_TAXONOMY = ["engraving", "renaissance", "baroque", "kabbalistic",
                  "illuminated_manuscript", "rosicrucian", "medieval",
                  "persian_miniature", "byzantine", "painting", "drawing",
                  "woodcut", "photograph", "ceramic", "sculpture", "mosaic"]

def find_image_path(art_id, art_entry):
    """Find the actual image file for an art entry."""
    # Check local_file first
    local = art_entry.get("local_file", "")
    if local:
        full_path = os.path.join(ROOT, local)
        if os.path.exists(full_path):
            return full_path
    # Check resolved path
    rp = art_entry.get("_resolved_path", "")
    if rp and os.path.exists(rp):
        return rp
    # Check public/art/
    for ext in [".jpg", ".png", ".jpeg", ".gif", ".webp"]:
        p = os.path.join(IMG_DIR, f"{art_id}{ext}")
        if os.path.exists(p):
            return p
    # Check alchemy dirs
    if "alchemy" in art_id:
        for g in range(1, 9):
            for f in os.listdir(os.path.join(ALCHEMY_DIR, f"gallery-{g}")):
                if f.endswith(".jpg") and f.replace(".jpg","") in art_id:
                    return os.path.join(ALCHEMY_DIR, f"gallery-{g}", f)
    return None

def needs_tagging(art_entry):
    """Check if this art entry already has enough metadata."""
    concepts = art_entry.get("concepts", [])
    return not any(c.strip() for c in concepts if c.strip())

def tag_with_vision(image_path, art_entry):
    """Call vision model to extract concepts, mood, style from image."""
    if not image_path or not os.path.exists(image_path):
        return None
    
    # Resize image for API (reduce to max 800px)
    img = Image.open(image_path)
    max_size = 800
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)))
    
    # Convert to base64
    import io
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    
    title = art_entry.get("title", "untitled")[:100]
    
    prompt = f"""Analyze this artwork titled "{title}" and return a JSON object with:
- concepts: array of 2-5 concepts from this list: {CONCEPT_TAXONOMY}
- mood: 1-3 moods from: {MOOD_TAXONOMY}
- style: 1-2 styles from: {STYLE_TAXONOMY}
- visual_motifs: array of 2-4 key visual elements (sun, angel, tree, etc.)
- entities_depicted: array of figures/objects shown
- color_palette: 2-4 dominant colors
- composition: one of: single_figure, multi_figure, landscape, diagrammatic, emblematic, abstract, portrait, still_life

Return ONLY valid JSON. No explanation."""
    
    import urllib.request
    data = json.dumps({
        "model": VISION_MODEL,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}
        ],
        "max_tokens": 500,
    }).encode()
    
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        text = result["choices"][0]["message"]["content"]
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None
    except Exception as e:
        print(f"  API error: {e}")
        return None

def main():
    dry_run = "--dry-run" in sys.argv
    gen_embeddings = "--embeddings" in sys.argv
    single_image = None
    if "--image" in sys.argv:
        idx = sys.argv.index("--image") + 1
        if idx < len(sys.argv):
            single_image = sys.argv[idx]
    
    # Load all art entries
    arts = []
    for f in sorted(os.listdir(ART_DIR)):
        if not f.endswith(".json"): continue
        art = json.load(open(os.path.join(ART_DIR, f)))
        arts.append(art)
    
    if single_image:
        arts = [a for a in arts if single_image in a.get("id", "")]
    
    untagged = [a for a in arts if needs_tagging(a)]
    print(f"Total art: {len(arts)}")
    print(f"Needs tagging: {len(untagged)}")
    
    if dry_run:
        print("\nWould tag:")
        for a in untagged[:10]:
            print(f"  {a['id']}: {a.get('title','?')[:60]}")
        return
    
    tagged = 0
    for art in untagged:
        aid = art["id"]
        img_path = find_image_path(aid, art)
        if not img_path:
            print(f"  SKIP {aid}: no image found")
            continue
        
        print(f"  TAGGING {aid}...", end=" ", flush=True)
        result = tag_with_vision(img_path, art)
        if result:
            # Update art entry
            art["concepts"] = result.get("concepts", art.get("concepts", []))
            art["mood"] = result.get("mood", art.get("mood", []))
            art["style"] = result.get("style", art.get("style", []))
            art["visual_motifs"] = result.get("visual_motifs", art.get("visual_motifs", []))
            art["entities_depicted"] = result.get("entities_depicted", art.get("entities_depicted", []))
            art["color_palette"] = result.get("color_palette", art.get("color_palette", []))
            art["composition"] = result.get("composition", art.get("composition", ""))
            
            with open(os.path.join(ART_DIR, f"{aid}.json"), "w") as f:
                json.dump(art, f, indent=2)
            tagged += 1
            print(f"✅ {result.get('concepts',[])}")
        else:
            print("❌")
    
    print(f"\nTagged: {tagged}/{len(untagged)}")

if __name__ == "__main__":
    main()
