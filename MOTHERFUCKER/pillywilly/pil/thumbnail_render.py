#!/usr/bin/env python3
"""Thumbnail renderer for the video pipeline.

Takes a JSON spec (from DeepSeek art director) and renders a YouTube thumbnail.
"""

import json
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

FONT_REGISTRY = {
    "eb_garamond": "EB Garamond",
    "im_fell_english": "IM FELL English",
    "im_fell_sc": "IM FELL English SC",
    "cinzel": "Cinzel",
    "cinzel_decorative": "Cinzel Decorative",
    "cormorant_garamond": "Cormorant Garamond",
    "playfair_display": "Playfair Display",
    "alegreya": "Alegreya",
    "lora": "Lora",
    "libre_baskerville": "Libre Baskerville",
    "cardo": "Cardo",
    "goudy_bookletter": "Goudy Bookletter 1911",
    "unifraktur_cook": "UnifrakturCook",
    "unifraktur_maguntia": "UnifrakturMaguntia",
    "kaushan_script": "Kaushan Script",
    "mea_culpa": "Mea Culpa",
    "eagle_lake": "Eagle Lake",
    "metamorphous": "Metamorphous",
    "parisienne": "Parisienne",
    "old_standard": "Old Standard TT",
    "medievalsharp": "MedievalSharp",
    "alice": "Alice",
    "sorts_mill_goudy": "Sorts Mill Goudy",
    "ole": "Ole",
    "dancing_script": "Dancing Script",
    "lobster_two": "Lobster Two",
    "triod_postnaja": "TriodPostnaja",
    "elstob": "ElstobD",
    "junicode": "Junicode Two Beta",
    "eb_garamond_initials": "EB Garamond Initials",
    "dejavu_serif": "DejaVu Serif",
    "freeserif": "FreeSerif",
}

TREATMENT_PRESETS = {
    "historical_gentle": {"contrast": 1.04, "saturation": 0.95, "sharpness": 1.03, "brightness": 1.02, "sepia": 0.15},
    "engraving_crisp": {"contrast": 1.15, "saturation": 0.80, "sharpness": 1.20, "brightness": 1.00, "sepia": 0.0},
    "whimsical_vivid": {"contrast": 1.06, "saturation": 1.12, "sharpness": 1.05, "brightness": 1.02, "sepia": 0.0},
    "sepia_classic": {"contrast": 1.08, "saturation": 0.70, "sharpness": 1.04, "brightness": 1.00, "sepia": 0.35},
    "mystical_dark": {"contrast": 1.12, "saturation": 1.05, "sharpness": 1.06, "brightness": 0.90, "sepia": 0.0},
    "none": {"contrast": 1.0, "saturation": 1.0, "sharpness": 1.0, "brightness": 1.0, "sepia": 0.0},
}


def resolve_font(font_role, size):
    family = FONT_REGISTRY.get(font_role)
    if not family:
        print(f"  [WARN] Unknown font_role '{font_role}', falling back to DejaVu Serif", file=sys.stderr)
        family = "DejaVu Serif"
    try:
        return ImageFont.truetype(family, size)
    except Exception:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", size)
        except Exception:
            return ImageFont.load_default()


def apply_sepia(img, intensity):
    if intensity <= 0:
        return img
    arr = img.copy()
    r, g, b = arr.split()
    nr = r
    ng = r
    nb = r
    arr = Image.merge("RGB", (r, g, b))
    return arr


def render_thumbnail(spec, image_lookup, output_path):
    W = spec["layout"]["canvas_width"]
    H = spec["layout"]["canvas_height"]
    bg = spec["layout"]["background"]

    canvas = Image.new("RGB", (W, H), bg)

    img_path = image_lookup.get(spec["selected_image_id"])
    if not img_path or not os.path.exists(img_path):
        print(f"  [ERROR] Image not found: {spec['selected_image_id']} -> {img_path}", file=sys.stderr)
        return False

    img = Image.open(img_path).convert("RGB")

    treatment = spec.get("image_treatment", {})
    if spec.get("treatment_preset") and not treatment:
        preset = TREATMENT_PRESETS.get(spec["treatment_preset"], TREATMENT_PRESETS["none"])
        treatment = preset
    if "sepia" in treatment and treatment["sepia"] > 0:
        arr = img
        r, g, b = arr.split()
        sepia_r = r
        sepia_g = g
        sepia_g = sepia_g
        sepia_b = b
        sepia_r = Image.blend(r, r, 1 - treatment["sepia"])
        sepia_g = Image.blend(g, g, 1 - treatment["sepia"])
        sepia_b = Image.blend(b, b, 1 - treatment["sepia"])
        img = Image.merge("RGB", (sepia_r, sepia_g, sepia_b))

    if "contrast" in treatment and treatment["contrast"] != 1.0:
        img = ImageEnhance.Contrast(img).enhance(treatment["contrast"])
    if "saturation" in treatment and treatment["saturation"] != 1.0:
        img = ImageEnhance.Color(img).enhance(treatment["saturation"])
    if "brightness" in treatment and treatment["brightness"] != 1.0:
        img = ImageEnhance.Brightness(img).enhance(treatment["brightness"])
    if "sharpness" in treatment and treatment["sharpness"] != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(treatment["sharpness"])

    box = spec["layout"]["image_box"]
    ratio = min(box["width"] / img.width, box["height"] / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    paste_x = box["x"] + (box["width"] - new_w) // 2
    paste_y = box["y"] + (box["height"] - new_h) // 2
    canvas.paste(img_resized, (paste_x, paste_y))

    draw = ImageDraw.Draw(canvas)
    caption = spec["caption"]
    font_role = spec.get("font_role", "eb_garamond")
    font_size = spec.get("font_size", 42)
    try:
        font = resolve_font(font_role, font_size)
    except Exception:
        font = ImageFont.load_default()

    cap = spec["layout"]["caption_box"]
    text_color = spec.get("text_color", (20, 20, 20))

    words = caption.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        tw = bbox[2] - bbox[0]
        if tw > cap["width"] and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    line_height = font_size * 1.3
    total_h = len(lines) * line_height
    start_y = cap["y"] + (cap["height"] - total_h) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = cap["x"] + (cap["width"] - tw) // 2
        ty = start_y + i * line_height
        draw.text((tx, ty), line, fill=text_color, font=font)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.save(output_path, "JPEG", quality=95)
    print(f"  -> Saved {output_path}")
    return True


def build_spec(video_title, image_id, caption, font_role, template_id="landscape_below",
               treatment_preset="historical_gentle", font_size=None):
    TEMPLATES = {
        "landscape_below": {
            "canvas_width": 1280, "canvas_height": 720, "background": "#f7f7f5",
            "image_box": {"x": 170, "y": 20, "width": 940, "height": 530},
            "caption_box": {"x": 220, "y": 580, "width": 840, "height": 90, "align": "center"},
        },
        "portrait_left": {
            "canvas_width": 1280, "canvas_height": 720, "background": "#f7f7f5",
            "image_box": {"x": 70, "y": 30, "width": 480, "height": 660},
            "caption_box": {"x": 620, "y": 260, "width": 580, "height": 180, "align": "center"},
        },
        "portrait_right": {
            "canvas_width": 1280, "canvas_height": 720, "background": "#f7f7f5",
            "image_box": {"x": 730, "y": 30, "width": 480, "height": 660},
            "caption_box": {"x": 70, "y": 260, "width": 580, "height": 180, "align": "center"},
        },
        "square_below": {
            "canvas_width": 1280, "canvas_height": 720, "background": "#f7f7f5",
            "image_box": {"x": 240, "y": 20, "width": 800, "height": 500},
            "caption_box": {"x": 220, "y": 560, "width": 840, "height": 110, "align": "center"},
        },
    }

    if not font_size:
        font_size = 54 if template_id in ("portrait_left", "portrait_right") else 44

    template = dict(TEMPLATES.get(template_id, TEMPLATES["landscape_below"]))
    return {
        "selected_image_id": image_id,
        "template_id": template_id,
        "caption": caption,
        "font_role": font_role,
        "font_size": font_size,
        "treatment_preset": treatment_preset,
        "image_treatment": {},
        "layout": template,
        "text_color": (20, 20, 20),
        "notes": f"Thumbnail for: {video_title}",
        "confidence": 0.9,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running renderer test...\n")
        image_paths = {}
        for root, dirs, files in os.walk("/root/projects/blog/content/sources/occult/alchemy/emblems"):
            for f in files:
                if f.endswith(".jpg") and not f.endswith(".json"):
                    gallery = os.path.basename(root)
                    img_id = f"alchemy_{gallery}_{f.replace('.jpg','')}"
                    image_paths[img_id] = os.path.join(root, f)

        for root, dirs, files in os.walk("/root/projects/blog/public/art"):
            for f in files:
                if f.endswith((".jpg", ".png", ".jpeg")):
                    img_id = f"curated_{f.rsplit('.',1)[0]}"
                    image_paths[img_id] = os.path.join(root, f)

        video_demos = [
            ("The Alchemical Marriage of Sun and Moon", "alchemy_gallery-1_A001", "historical_gentle",
             "Between Heaven and Earth", "cinzel", "landscape_below"),
            ("The Emerald Tablet: As Above, So Below", "alchemy_gallery-2_A045", "engraving_crisp",
             "As above, so below", "im_fell_english", "landscape_below"),
            ("The Philosopher's Stone: A Practical Guide", "alchemy_gallery-4_A150", "sepia_classic",
             "The Great Work", "eb_garamond", "landscape_below"),
            ("Robert Fludd and the Cosmic Hermeticism", "curated_art_fludd_macrocosm", "historical_gentle",
             "The Macrocosm Within", "cormorant_garamond", "landscape_below"),
            ("The Green Lion Devours the Sun", "alchemy_gallery-3_A102", "engraving_crisp",
             "The Green Lion", "unifraktur_cook", "landscape_below"),
            ("The Seven Metals of Alchemy", "alchemy_gallery-5_A200", "sepia_classic",
             "Seven metals, one stone", "goudy_bookletter", "landscape_below"),
            ("The Nigredo Stage: Black of Blacks", "alchemy_gallery-6_A250", "mystical_dark",
             "Through the black", "medievalsharp", "landscape_below"),
            ("The Rebis: Hermaphroditic Unity", "alchemy_gallery-7_A280", "historical_gentle",
             "The double nature", "cinzel_decorative", "landscape_below"),
            ("The Peacock's Tail: Albedo Rising", "alchemy_gallery-8_A310", "whimsical_vivid",
             "All colours arise", "alegreya", "landscape_below"),
            ("The Ouroboros: Eternity's Serpent", "curated_art_conjunction", "historical_gentle",
             "The serpent eats itself", "unifraktur_maguntia", "landscape_below"),
        ]

        out_dir = "/root/projects/blog/public/thumbnails/test"
        count = 0
        for title, img_id, preset, caption, font, template in video_demos:
            if img_id not in image_paths:
                print(f"  [SKIP] {img_id}: image not found")
                continue
            slug = title.lower().replace(":", "").replace(" ", "-")[:40]
            spec = build_spec(title, img_id, caption, font, template, preset)
            spec["notes"] = f"Test thumbnail for: {title}"
            ok = render_thumbnail(spec, image_paths, f"{out_dir}/{slug}.jpg")
            if ok:
                count += 1
        print(f"\nGenerated {count} test thumbnails in {out_dir}/")
    else:
        spec = json.loads(sys.stdin.read())
        image_lookup_path = spec.pop("_image_lookup", {})
        output = spec.pop("_output", "thumbnail.jpg")
        render_thumbnail(spec, image_lookup_path, output)
