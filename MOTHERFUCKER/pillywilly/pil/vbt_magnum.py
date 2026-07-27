"""Vijñāna Bhairava — 112 meditation techniques.
Each scene: subject → object → collapse to nondual perception.
Standard visual language: silhouette, sense field, return to center."""

import math
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220)
M = (145, 141, 132); C_ = (141, 44, 57)

def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x):
    t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1
    return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

# ── Standard human silhouette function ────────────────────────────
def draw_human(d, cx, cy, scale=1.0, color=I_, alpha=1.0):
    """Simple seated human figure — the practitioner."""
    a = int(255 * alpha)
    head_r = 18 * scale
    d.ellipse((cx - head_r, cy - 70 * scale - head_r, cx + head_r, cy - 70 * scale + head_r),
              outline=(color[0], color[1], color[2], a), width=2)
    d.rounded_rectangle((cx - 25 * scale, cy - 50 * scale, cx + 25 * scale, cy + 30 * scale),
                        radius=12, outline=(color[0], color[1], color[2], a), width=2)
    d.line((cx - 20 * scale, cy - 10 * scale, cx - 50 * scale, cy + 40 * scale),
           fill=(color[0], color[1], color[2], a), width=2)
    d.line((cx + 20 * scale, cy - 10 * scale, cx + 50 * scale, cy + 40 * scale),
           fill=(color[0], color[1], color[2], a), width=2)
    d.line((cx - 15 * scale, cy + 30 * scale, cx - 30 * scale, cy + 80 * scale),
           fill=(color[0], color[1], color[2], a), width=2)
    d.line((cx + 15 * scale, cy + 30 * scale, cx + 30 * scale, cy + 80 * scale),
           fill=(color[0], color[1], color[2], a), width=2)

# ── Meditation template function ──────────────────────────────────
def make_vbt_scene(verse_num, technique_name, description, focus_type="sound"):
    """Create a scene function for one VBT meditation.
    focus_type determines what kind of object appears:
    - "sound": sound waves from the right
    - "light": visual/light forms
    - "breath": breath column
    - "touch": tactile field
    - "void": empty space
    - "collapse": things returning to center
    """
    def scene(t, u, i):
        im = ca()
        d = ImageDraw.Draw(im)
        cx_human = 250  # human on left
        cy = H // 2

        # Draw human practitioner
        draw_human(d, cx_human, cy, 1.2, I_, 0.9)

        # Draw the sense object / focus area on the right
        if focus_type == "sound":
            # Sound waves emanating from right
            for k in range(5):
                r = (40 + k * 30) * S(0, 1, u)
                x = cx_human + 200 + k * 40
                d.ellipse((x - r, cy - r * 0.5, x + r, cy + r * 0.5),
                          outline=(G[0], G[1], G[2], int(80 * (1 - k * 0.15))), width=1)

        elif focus_type == "light":
            for k in range(8):
                ang = k * 0.785 + t * 0.05; r = 40 + 50 * S(0, 1, u)
                x = cx_human + 300 + r * math.cos(ang)
                y = cy + r * math.sin(ang)
                d.line((cx_human + 300, cy, x, y), fill=(G[0], G[1], G[2], int(80)), width=1)

        elif focus_type == "breath":
            ap = 60 + 40 * p(t * 0.4, 0, 0.4)
            d.rectangle((cx_human + 280, cy - ap, cx_human + 300, cy + ap), outline=I_, width=2)

        elif focus_type == "touch":
            for k in range(5):
                r = (30 + k * 20) * S(0, 1, u)
                d.ellipse((cx_human + 300 - r, cy - r, cx_human + 300 + r, cy + r),
                          outline=(C_[0], C_[1], C_[2], int(60)), width=1)

        elif focus_type == "void":
            r = 40 * S(0, 1, u)
            d.ellipse((cx_human + 300 - r, cy - r, cx_human + 300 + r, cy + r),
                      outline=M, width=1)

        # The return — arrows or particles flowing back to center
        if u > 0.3:
            for k in range(8):
                a = S(0.3 + k * 0.05, 0.6 + k * 0.05, u)
                ang = k * 0.785 + t * 0.03
                r = 140 * a
                x_start = cx_human + 280 + r * math.cos(ang)
                y_start = cy + r * math.sin(ang)
                x_end = cx_human + 50
                d.line((x_start, y_start, x_end, y_start + 20 * math.sin(ang)),
                       fill=(G[0], G[1], G[2], int(100 * a)), width=1)

        # Center bindu — nondual awareness
        if u > 0.6:
            a = S(0.6, 0.8, u)
            d.ellipse((cx_human + 50 - 6, cy - 6, cx_human + 50 + 6, cy + 6),
                      fill=(G[0], G[1], G[2], int(200 * a)))

        # Label
        d.text((60, 60), f"VBT {verse_num}", fill=M)
        d.text((60, 90), technique_name, fill=I_)
        d.text((60, 120), description, fill=M)
        return im

    scene.__name__ = f"vbt_{verse_num}"
    return scene, 14

# ── Build first 20 VBT scenes ─────────────────────────────────────
VBT_SCENES = [
    (1, "Between two breaths", "at the junction of inhalation and exhalation", "breath"),
    (2, "Full stop of breath", "breath stops, awareness opens", "breath"),
    (3, "Breath rushing down", "breath descends through the central channel", "breath"),
    (4, "Attention at the brow", "focus between the eyebrows", "light"),
    (5, "The void above", "contemplate the space above", "void"),
    (6, "Sound of a waterfall", "listen to natural sounds without distraction", "sound"),
    (7, "Mantra heard within", "hear the inner sound of a mantra", "sound"),
    (8, "Open eyes, open awareness", "look at the world without grasping", "light"),
    (9, "Close the seven doors", "withdraw the senses one by one", "touch"),
    (10, "In the gap between", "rest between two perceptions", "void"),
    (11, "Sudden impulse", "udyamo bhairavaḥ — the impulse itself", "light"),
    (12, "Taste without tongue", "experience taste as consciousness", "touch"),
    (13, "Smell without nose", "the fragrance of awareness", "touch"),
    (14, "Touch within touch", "feel the sensation of feeling itself", "touch"),
    (15, "Sound dissolving", "follow a sound until it dissolves", "sound"),
    (16, "Light expanding", "a point of light expands to fill all", "light"),
    (17, "Thought between thoughts", "the gap between two thoughts", "void"),
    (18, "The felt sense of I", "rest in the feeling of being", "void"),
    (19, "Body as space", "feel the body as empty space", "void"),
    (20, "Senses turning inward", "senses dissolve into their source", "collapse"),
]

scene_list = []
for verse_num, name, desc, focus in VBT_SCENES:
    fn, dur = make_vbt_scene(verse_num, name, desc, focus)
    scene_list.append((fn, dur, f"VBT {verse_num}: {name}"))
