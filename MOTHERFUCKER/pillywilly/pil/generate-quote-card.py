#!/usr/bin/env python3
"""Generate quote card PNG for video overlay.

Output: transparent-background PNG with styled text, ready for FableCut.

Fonts: quote text in Ephesis (or specified), author in specified accent font.
"""

import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/truetype"

FONT_MAP = {
    "reenie_beanie": os.path.join(FONT_DIR, "ReenieBeanie.ttf"),
    "ephesis": os.path.join(FONT_DIR, "Ephesis-Regular.ttf"),
    "sedgwick": os.path.join(FONT_DIR, "SedgwickAveDisplay-Regular.ttf"),
    "caveat": os.path.join(FONT_DIR, "Caveat", "Caveat-Regular.ttf"),
    "eb_garamond": "EB Garamond",
    "im_fell": "IM FELL English",
    "cinzel": "Cinzel",
    "playfair": "Playfair Display",
    "cormorant": "Cormorant Garamond",
    "lora": "Lora",
}

STYLES = {
    "centered_sparse": {
        "width": 1280, "height": 720,
        "text_color": (255, 255, 255),
        "author_color": (255, 232, 200),
        "text_font": "ephesis",
        "author_font": "cormorant",
        "text_size": 52,
        "author_size": 28,
        "margin_x": 160,
        "margin_y": 240,
        "line_spacing": 1.5,
        "shadow": True,
    },
    "lower_third": {
        "width": 1280, "height": 720,
        "text_color": (255, 255, 255),
        "author_color": (255, 232, 200),
        "text_font": "reenie_beanie",
        "author_font": "cormorant",
        "text_size": 44,
        "author_size": 24,
        "margin_x": 80,
        "margin_y": 460,
        "line_spacing": 1.4,
        "shadow": True,
    },
    "full_quote": {
        "width": 1280, "height": 720,
        "text_color": (255, 255, 255),
        "author_color": (255, 232, 200),
        "text_font": "ephesis",
        "author_font": "playfair",
        "text_size": 48,
        "author_size": 26,
        "margin_x": 200,
        "margin_y": 200,
        "line_spacing": 1.6,
            "shadow": True,
    },
    "black_page": {
        "width": 1280, "height": 720,
        "text_color": (255, 255, 255),
        "author_color": (200, 180, 150),
        "text_font": "eb_garamond",
        "author_font": "cormorant",
        "text_size": 56,
        "author_size": 24,
        "margin_x": 200,
        "margin_y": 240,
        "line_spacing": 1.4,
        "shadow": False,
        "background": (10, 10, 10),
    },
    "black_page_compact": {
        "width": 1280, "height": 720,
        "text_color": (255, 255, 255),
        "author_color": (200, 180, 150),
        "text_font": "eb_garamond",
        "author_font": "cormorant",
        "text_size": 44,
        "author_size": 22,
        "margin_x": 200,
        "margin_y": 300,
        "line_spacing": 1.3,
        "shadow": False,
        "background": (10, 10, 10),
    },
}

def resolve_font(name, size):
    path = FONT_MAP.get(name)
    if not path:
        return ImageFont.load_default()
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
        else:
            return ImageFont.truetype(path, size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", size)
        except:
            return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + " " + w if current else w
        bbox = draw.textbbox((0, 0), test, font=font)
        tw = bbox[2] - bbox[0]
        if tw > max_width and current:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    return lines

def generate_card(text, author="", style_name="centered_sparse", output_path=None):
    style = STYLES.get(style_name, STYLES["centered_sparse"])
    W, H = style["width"], style["height"]

    bg_color = style.get("background")
    if bg_color:
        canvas = Image.new("RGB", (W, H), bg_color)
    else:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    text_font = resolve_font(style["text_font"], style["text_size"])
    author_font = resolve_font(style["author_font"], style["author_size"])
    mx, my = style["margin_x"], style["margin_y"]
    max_w = W - 2 * mx

    lines = wrap_text(text, text_font, max_w, draw)
    line_h = style["text_size"] * style["line_spacing"]
    total_h = len(lines) * line_h

    start_y = my

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=text_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        ty = start_y + i * line_h

        if style.get("shadow"):
            draw.text((tx + 2, ty + 2), line, fill=(0, 0, 0, 120), font=text_font)

        draw.text((tx, ty), line, fill=style["text_color"], font=text_font)

    if author:
        bbox = draw.textbbox((0, 0), author, font=author_font)
        aw = bbox[2] - bbox[0]
        ax = (W - aw) // 2
        ay = start_y + len(lines) * line_h + 20
        draw.text((ax, ay), f"— {author}", fill=style["author_color"], font=author_font)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas.save(output_path, "PNG")
        return output_path

    return canvas


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate-quote-card.py <json> [output.png]")
        print("JSON: { text, author?, style? }")
        sys.exit(1)

    if len(sys.argv) >= 2 and sys.argv[1] != "--demo":
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = {"text": "The imaginal is not the imaginary.\nIt is the place where the soul lives.", "author": "Henry Corbin", "style": "centered_sparse"}

    text = data.get("text", "")
    author = data.get("author", "")
    style = data.get("style", "centered_sparse")
    output = data.get("output") if not sys.argv[1] == "--demo" else None

    if len(sys.argv) >= 3 and sys.argv[2]:
        output = sys.argv[2]

    if not output:
        output = f"/tmp/quote_{hash(text) & 0xffffffff:08x}.png"

    path = generate_card(text, author, style, output)
    print(f"Quote card: {path}")
    print(f"Size: {os.path.getsize(path)} bytes")
