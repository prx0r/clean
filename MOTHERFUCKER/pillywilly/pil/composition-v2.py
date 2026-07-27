"""
Composition v2 — "The Engine of Consciousness"
Not a build script. A composition: selecting existing scene functions,
arranging them with continuity, transitions, and narrative arc.

Uses: spanda_scenes, spanda_karika_pack, light_pack, p01_reflection,
vijnana_bhairava_pack, core_scenes, concept_packs
"""
import sys, os, math, json
from PIL import Image, ImageDraw

W, H = 1280, 720
OUT = '/root/projects/blog/content/publishing/renders/expansion-essay1-platinum/v2'
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, '/root/projects/blog/scripts/renderer')
from renderer import *
FPS = 8  # override renderer's default 2fps

# ── Palette ──
WHITE = (248, 246, 240)
INK = (30, 25, 27)
CRIMSON = (141, 44, 57)
GOLD = (208, 172, 91)
MUTED = (145, 141, 132)

# ── Import existing functions ──
sys.path.insert(0, '/root/projects/blog/visual-library')
from spanda_scenes import s_hook, s_wheel, s_six, s_mantra, s_perception, s_throb, s_chain, s_play, s_recog, s_close
from light_pack import scene_light_darkness, scene_light_wave, scene_vibration
from p01_reflection import s1 as mirror_self, s2 as mirror_reflections, s5 as mirror_recognition
from core_scenes import scene_resonance, scene_dissolution

# ── Continuity bridge ──
def bridge_from_center(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    dot(d, 640, 360, 4 + u*8, GOLD, 1 - u*0.3)
    ring(d, 640, 360, 20 + u*60, GOLD, 0.3 - u*0.2, 1)
    return im

def bridge_pulse(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    throb = 1 + 0.04*math.sin(t*2)
    for i in range(2):
        ri = (20 + i*30) * throb
        ring(d, 640, 360, ri, CRIMSON, 0.2 - i*0.06, 1)
    dot(d, 640, 360, 4, GOLD, 0.8)
    return im

# ── Additional tailored shots ──
def void_emergence(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    r = 2 + u * 15
    dot(d, 640, 360, r, GOLD, smoothstep(0, 0.6, u))
    if u > 0.3:
        centered(d, "spanda", 200, FONT["dev_l"], GOLD, smoothstep(0.3, 0.7, u)*0.6)
    return im

def sanskrit_quote(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    centered(d, "यस्योन्मेषनिमेषाभ्यां", 250, FONT["dev_l"], GOLD, smoothstep(0, 0.4, u))
    centered(d, "जगतः प्रलयोदयौ", 310, FONT["dev_l"], GOLD, smoothstep(0.1, 0.5, u)*0.7)
    if u > 0.5:
        centered(d, "wheel of powers", 450, FONT["m"], MUTED, smoothstep(0.5, 0.8, u)*0.5)
    return im

def six_names_shot(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    names = [("प्राणना","vitality"),("स्फुरत्ता","effulgence"),("विश्रान्ति","repose"),
             ("जीव","being"),("हृदय","heart"),("स्पन्द","vibration")]
    dot(d, cx, cy, 3, GOLD, 0.5)
    for i, (skt, eng) in enumerate(names):
        at = 0.05 + i*0.1
        a = smoothstep(at, at+0.08, u) * 0.7
        if a <= 0: continue
        ang = i*1.047 - 1.57 + math.sin(t*0.2)*0.1
        r = 160 + 10*math.sin(t*0.3 + i)
        nx = cx + r*math.cos(ang)
        ny = cy + r*math.sin(ang)
        d.text((nx-20, ny-6), skt, font=FONT["dev_m"], fill=rgba(GOLD, a))
        d.text((nx+45, ny-4), eng, font=FONT["xs"], fill=rgba(MUTED, a*0.7))
    return im

def chain_shot(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx = 640
    chain = ["TIME", "BREATH", "SPANDA", "VOID", "CONSCIOUSNESS"]
    sp = 70
    sy = 360 - (len(chain)-1)*sp/2
    for i, label in enumerate(chain):
        at = 0.05 + i*0.1
        a = smoothstep(at, at+0.08, u)
        if a <= 0: continue
        y = sy + i*sp
        col = GOLD if label == "SPANDA" else INK
        d.rounded_rectangle((cx-90, y-14, cx+90, y+14), 4, 4, outline=rgba(col, a*0.6), width=1)
        centered(d, label, y+4, FONT["m"], col, a)
        if i < len(chain)-1:
            d.line((cx, y+18, cx, y+sp-18), fill=rgba(MUTED, a*0.3), width=1)
    return im

def closing_expansion(t, u, idx):
    im = canvas(DARK)
    d = ImageDraw.Draw(im)
    cx, cy = 640, 360
    r = 5 + smoothstep(0.5, 1.0, u) * 300
    dot(d, cx, cy, r, GOLD, max(0, 1 - u*0.6))
    if u < 0.4:
        a = smoothstep(0, 0.3, u)
        centered(d, "the sixth bliss", 280, FONT["l"], INK, a)
        centered(d, "is complete expansion", 340, FONT["m"], GOLD, a*0.7)
    if u > 0.7:
        centered(d, "स्पन्द", 400, FONT["dev_l"], GOLD, smoothstep(0.7, 0.9, u)*0.4)
    return im

# ── SHOT COMPOSITION ──
# Each chapter: [establish, develop, transition, resolve] using existing functions
SHOTS = [
    # Chapter 1: Hook — The Hidden Pulse (7 shots, ~50s)
    ("void_emerge",  6, void_emergence),
    ("s_hook_01",    8, lambda t,u,i: s_hook(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("void_emerge_02", 6, void_emergence),
    ("s_hook_02",    8, lambda t,u,i: s_hook(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 2: Wheel of Powers (5 shots, ~35s)
    ("s_wheel_01",   10, lambda t,u,i: s_wheel(t, u, i)),
    ("sanskrit_q",   8, sanskrit_quote),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_wheel_02",   10, lambda t,u,i: s_wheel(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 3: Six Names (5 shots, ~35s)
    ("s_six_01",     10, lambda t,u,i: s_six(t, u, i)),
    ("six_names_01", 8, six_names_shot),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_six_02",     10, lambda t,u,i: s_six(t, u, i)),

    # Chapter 4: Mantra as Pulse (5 shots, ~35s)
    ("s_mantra_01",  10, lambda t,u,i: s_mantra(t, u, i)),
    ("resonance_01", 8, lambda t,u,i: scene_resonance(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_mantra_02",  10, lambda t,u,i: s_mantra(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 5: Perception as Pulse (5 shots, ~35s)
    ("s_perc_01",    10, lambda t,u,i: s_perception(t, u, i)),
    ("scene_light_01", 8, lambda t,u,i: scene_light_darkness(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_perc_02",    10, lambda t,u,i: s_perception(t, u, i)),

    # Chapter 6: Resonance (5 shots, ~35s)
    ("resonance_01", 10, lambda t,u,i: scene_resonance(t, u, i)),
    ("vibration_01", 8, lambda t,u,i: scene_vibration(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("resonance_02", 10, lambda t,u,i: scene_resonance(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 7: Belly of the Fish (5 shots, ~35s)
    ("s_throb_01",   10, lambda t,u,i: s_throb(t, u, i)),
    ("scene_light_wave_01", 8, lambda t,u,i: scene_light_wave(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_throb_02",   10, lambda t,u,i: s_throb(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 8: Chain (5 shots, ~35s)
    ("s_chain_01",   10, lambda t,u,i: s_chain(t, u, i)),
    ("chain_specific", 8, chain_shot),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_chain_02",   10, lambda t,u,i: s_chain(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 9: Universe as Drum (5 shots, ~35s)
    ("s_play_01",    10, lambda t,u,i: s_play(t, u, i)),
    ("vibration_02", 8, lambda t,u,i: scene_vibration(t, u, i)),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_play_02",    10, lambda t,u,i: s_play(t, u, i)),

    # Chapter 10: Waves of One Pulse (5 shots, ~35s)
    ("light_wave_01", 10, lambda t,u,i: scene_light_wave(t, u, i)),
    ("light_wave_02", 8, lambda t,u,i: scene_light_wave(t+2, u, i)),  # phase-shifted
    ("bridge_pulse", 3, bridge_pulse),
    ("dissolve_01",  10, lambda t,u,i: scene_dissolution(t, u, i)),

    # Chapter 11: Play (4 shots, ~30s)
    ("s_play_03",    10, lambda t,u,i: s_play(t, u, i)),
    ("mirror_01",    8, mirror_self),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_play_04",    8, lambda t,u,i: s_play(t, u, i)),

    # Chapter 12: Recognition (5 shots, ~35s)
    ("s_recog_01",   10, lambda t,u,i: s_recog(t, u, i)),
    ("mirror_recog", 8, mirror_recognition),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_recog_02",   10, lambda t,u,i: s_recog(t, u, i)),
    ("bridge_center",3, bridge_from_center),

    # Chapter 13: Closing (4 shots, ~30s)
    ("s_close_01",   10, lambda t,u,i: s_close(t, u, i)),
    ("closing_expand", 8, closing_expansion),
    ("bridge_pulse", 3, bridge_pulse),
    ("s_close_02",   8, lambda t,u,i: s_close(t, u, i)),
]

def render():
    total_shots = len(SHOTS)
    total_dur = sum(s[1] for s in SHOTS)
    print(f"Composition: {total_shots} shots, {total_dur}s ({total_dur/60:.1f} min) at {FPS}fps")
    print(f"Chapters: 13")
    print(f"Existing functions used: s_hook, s_wheel, s_six, s_mantra, s_perception, s_throb,")
    print(f"  s_chain, s_play, s_recog, s_close, scene_resonance, scene_vibration,")
    print(f"  scene_light_darkness, scene_light_wave, scene_dissolution, mirror_self, mirror_recognition")
    print()
    
    for idx, (shot_id, dur, fn) in enumerate(SHOTS):
        scene_dir = os.path.join(OUT, shot_id)
        os.makedirs(scene_dir, exist_ok=True)
        total_frames = int(dur * FPS)
        for fi in range(total_frames):
            t = fi / FPS
            u = fi / total_frames if total_frames > 0 else 1
            im = fn(t, u, idx)
            im.save(os.path.join(scene_dir, f"frame_{fi:05d}.png"))
        print(f"  [{idx+1:2d}/{total_shots}] {shot_id}: {total_frames} frames = {dur}s")
    print(f"\nRendered {total_shots} shots, {total_dur}s")

if __name__ == "__main__":
    act = sys.argv[1] if len(sys.argv) > 1 else "all"
    if act in ("all", "render"):
        render()
    print("Done.")
