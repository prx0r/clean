"""Add exactly one VBT scene to the state file. Run repeatedly."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, '.')
from renderer import Film, Scene
from PIL import Image, ImageDraw

W, H = 1280, 720; D = (12, 12, 15); G = (208, 172, 91); I_ = (235, 231, 220); M = (145, 141, 132); C_ = (141, 44, 57)
def p(t, o=0, s=1.0): return 0.5 + 0.5 * math.sin(t * s + o)
def S(a, b, x): t_ = max(0, min(1, (x - a) / (b - a))) if b != a else 1; return t_ * t_ * (3 - 2 * t_)
def ca(bg=D): return Image.new("RGB", (W, H), bg)

def draw_human(d, cx, cy, s=1.0, c=I_):
    a = int(255 * 0.9); hr = 18 * s
    d.ellipse((cx - hr, cy - 70 * s - hr, cx + hr, cy - 70 * s + hr), outline=(c[0], c[1], c[2], a), width=2)
    d.rounded_rectangle((cx - 25 * s, cy - 50 * s, cx + 25 * s, cy + 30 * s), radius=12, outline=(c[0], c[1], c[2], a), width=2)
    d.line((cx - 20 * s, cy - 10 * s, cx - 50 * s, cy + 40 * s), fill=(c[0], c[1], c[2], a), width=2)
    d.line((cx + 20 * s, cy - 10 * s, cx + 50 * s, cy + 40 * s), fill=(c[0], c[1], c[2], a), width=2)
    d.line((cx - 15 * s, cy + 30 * s, cx - 30 * s, cy + 80 * s), fill=(c[0], c[1], c[2], a), width=2)
    d.line((cx + 15 * s, cy + 30 * s, cx + 30 * s, cy + 80 * s), fill=(c[0], c[1], c[2], a), width=2)

# All remaining VBT definitions
SCENE_DEFS = {
    23: ("The void beneath", "contemplate the space below", "void"),
    24: ("Sudden waking", "the startle itself is Bhairava", "light"),
    25: ("Without support", "awareness without an object", "void"),
    26: ("In the pause of motion", "between walking steps", "void"),
    27: ("The breath stops itself", "the glory of the self", "breath"),
    28: ("Attention at the heart", "the pulse of awareness", "touch"),
    29: ("One taste", "all tastes as one", "touch"),
    30: ("Sound of an instrument", "follow sound to its source", "sound"),
    31: ("The unstruck sound", "hear the inner anāhata", "sound"),
    32: ("Merging in a familiar place", "the known becomes doorway", "light"),
    33: ("Sky above, sky below", "the body dissolved in space", "void"),
    34: ("The mind in the heart", "thought resting in its source", "void"),
    35: ("The thought of anything", "any perception is Śiva", "light"),
    36: ("The senses in the void", "withdraw senses into space", "touch"),
    37: ("Wherever the mind goes", "there is the Self", "light"),
    38: ("The pleasure of sex", "the peak of bliss is Śiva", "touch"),
    39: ("Sneeze, terror, sorrow", "extreme states open the door", "void"),
    40: ("The desire awakened", "in desire itself", "touch"),
    41: ("Running, falling, orgasm", "sudden intense moments", "void"),
    42: ("The pain of another", "empathy as dissolution", "touch"),
    43: ("The state of hunger", "the empty stomach is awareness", "void"),
    44: ("The state of fullness", "satiation dissolves", "touch"),
    45: ("Touching the palate", "tongue to the roof", "touch"),
    46: ("The ending of sleep", "the liminal state", "void"),
    47: ("The beginning of sleep", "falling into the source", "void"),
    48: ("Looking in a mirror", "the seer and seen collapse", "light"),
    49: ("Making love without climax", "suspended in the wave", "touch"),
    50: ("In the dark", "darkness itself is form", "light"),
    51: ("The scent of earth", "earth smell as grounding", "touch"),
    52: ("Eating a meal", "taste as offering", "touch"),
    53: ("The moon in water", "reflection and reality", "light"),
    54: ("Sitting like a mountain", "stillness itself", "void"),
    55: ("The breath of a mantra", "mantra rides the breath", "sound"),
    56: ("The sacred word", "AUM as the pulse", "sound"),
    57: ("Walking meditation", "each step a homecoming", "touch"),
    58: ("Looking at the sky", "the infinite opens", "light"),
    59: ("The fire of anger", "rage as energy", "touch"),
    60: ("The resonance of a bell", "sound fades into silence", "sound"),
    61: ("The flame of a lamp", "gaze without blinking", "light"),
    62: ("The cave of the heart", "rest in the heart center", "void"),
    63: ("The current of a river", "flow as awareness", "touch"),
    64: ("The still lake", "mind like still water", "void"),
    65: ("The moon alone in the sky", "single focus dissolves", "light"),
    66: ("Blinking awareness", "the gap in each blink", "light"),
    67: ("The space between breaths", "the pause is the door", "breath"),
    68: ("Sensing the skin", "the boundary dissolves", "touch"),
    69: ("Heat and cold", "sensation as pure energy", "touch"),
    70: ("Pleasure and pain", "both are consciousness", "touch"),
    71: ("The hum of the city", "all sounds as one", "sound"),
    72: ("The silence of a cave", "deep quiet opens", "void"),
    73: ("Looking at a flower", "perceive its suchness", "light"),
    74: ("The weight of the body", "gravity as presence", "touch"),
    75: ("Lying on the ground", "earth supports all", "touch"),
    76: ("Floating", "the body becomes space", "void"),
    77: ("The moment of orgasm", "bliss dissolves the knower", "touch"),
    78: ("After orgasm", "the peace that follows", "void"),
    79: ("Gazing at a child", "innocence awakens", "light"),
    80: ("The look of a dying man", "mortality opens", "light"),
    81: ("A sudden memory", "the past arises now", "void"),
    82: ("Anticipation", "the future in this moment", "void"),
    83: ("The present", "this moment itself", "void"),
    84: ("The number one", "all numbers return to one", "light"),
    85: ("The number zero", "zero as source", "void"),
    86: ("Counting breaths", "one to ten and back", "breath"),
    87: ("The moment of fear", "fear reveals", "void"),
    88: ("The moment of joy", "joy opens the heart", "touch"),
    89: ("The moment of sadness", "sorrow is the gate", "void"),
    90: ("The moment of surprise", "the unexpected is Śiva", "light"),
    91: ("The moment before speech", "the word unspoken", "sound"),
    92: ("The moment after speech", "silence after sound", "sound"),
    93: ("Touching the lips", "sensation at the threshold", "touch"),
    94: ("The tongue at the teeth", "the subtle sensation", "touch"),
    95: ("The edge of sleep", "between waking and dream", "void"),
    96: ("Waking within a dream", "lucid awareness", "light"),
    97: ("Dream within waking", "reality as dream", "light"),
    98: ("The empty cup", "space as form", "void"),
    99: ("The full cup", "form as space", "light"),
    100: ("All sounds at once", "the symphony of awareness", "sound"),
    101: ("Complete silence", "the sound of the void", "sound"),
    102: ("The single eye", "see without duality", "light"),
    103: ("The thousand eyes", "see from everywhere", "light"),
    104: ("Breath entering the body", "the gift of life", "breath"),
    105: ("Breath leaving the body", "release into the all", "breath"),
    106: ("The pause between", "the moment of rest", "void"),
    107: ("The centre of the storm", "stillness in chaos", "void"),
    108: ("The dance of Śiva", "all motion is one", "light"),
    109: ("The silence of Śakti", "stillness is power", "void"),
    110: ("Bhairava laughing", "the cosmos as play", "light"),
    111: ("Bhairava weeping", "compassion dissolves", "touch"),
    112: ("Neither this nor that", "neti neti — the supreme", "void"),
}

state_file = "/tmp/vbt_state.json"
state = json.load(open(state_file))
nv = state["next_verse"]

if nv in SCENE_DEFS:
    name, desc, ftype = SCENE_DEFS[nv]
    state["scenes"].append({"verse": nv, "name": name, "desc": desc, "type": ftype})
    state["next_verse"] = nv + 1
    json.dump(state, open(state_file, "w"))
    print(f"Added VBT {nv}: {name}")
else:
    print("COMPLETE: All defined scenes added")
    sys.exit(0)

# Build all scenes from state
all_scenes = []
for s in state["scenes"]:
    vn = s["verse"]; name = s["name"]; desc = s["desc"]; ft = s["type"]
    def make_fn(vn, n, d, ft):
        def scene_fn(t, u, i):
            im = ca(); dr = ImageDraw.Draw(im); draw_human(dr, 250, H // 2, 1.2, I_)
            if ft == "sound":
                for k in range(5): r = (40 + k * 30) * S(0, 1, u); x = 250 + 200 + k * 40; dr.ellipse((x - r, H // 2 - r * 0.5, x + r, H // 2 + r * 0.5), outline=(G[0], G[1], G[2], int(80 * (1 - k * 0.15))), width=1)
            elif ft == "light":
                for k in range(8): ang = k * 0.785 + t * 0.05; r = 40 + 50 * S(0, 1, u); dr.line((550, H // 2, 550 + r * math.cos(ang), H // 2 + r * math.sin(ang)), fill=(G[0], G[1], G[2], int(80)), width=1)
            elif ft == "breath":
                ap = 60 + 40 * p(t * 0.4, 0, 0.4); dr.rectangle((530, H // 2 - ap, 550, H // 2 + ap), outline=I_, width=2)
            elif ft == "touch":
                for k in range(5): r = (30 + k * 20) * S(0, 1, u); dr.ellipse((550 - r, H // 2 - r, 550 + r, H // 2 + r), outline=(C_[0], C_[1], C_[2], int(60)), width=1)
            elif ft == "void":
                r = 40 * S(0, 1, u); dr.ellipse((550 - r, H // 2 - r, 550 + r, H // 2 + r), outline=M, width=1)
            if u > 0.3:
                for k in range(8):
                    a_ = S(0.3 + k * 0.05, 0.6 + k * 0.05, u); ang = k * 0.785 + t * 0.03; r_ = 140 * a_
                    dr.line((530 + r_ * math.cos(ang), H // 2 + r_ * math.sin(ang), 300, H // 2 + 20 * math.sin(ang)), fill=(G[0], G[1], G[2], int(100 * a_)), width=1)
            if u > 0.6:
                a_ = S(0.6, 0.8, u); dr.ellipse((300 - 6, H // 2 - 6, 300 + 6, H // 2 + 6), fill=(G[0], G[1], G[2], int(200 * a_)))
            dr.text((60, 60), f"VBT {vn}", fill=M); dr.text((60, 90), n, fill=I_); dr.text((60, 120), d, fill=M)
            return im
        scene_fn.__name__ = f"vbt_{vn}"; return scene_fn
    fn = make_fn(vn, name, desc, ft)
    all_scenes.append(Scene(f"vbt_{vn}", 14, fn, f"VBT {vn}: {name}"))

film = Film("vbt_magnum", "Vijñāna Bhairava — 112 Meditation Techniques", all_scenes)
out = Path('/root/projects/FableCut/media/vbt-magnum-preview.mp4')
film.render(out)
print(f"✅ Pack: {len(all_scenes)} scenes (one added)")
PYEOF