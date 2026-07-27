"""Generate 16 platinum packs as thin wrappers around _shared.py."""
from pathlib import Path

BOILER = '''#!/usr/bin/env python3
from __future__ import annotations
import math, random
from PIL import Image, ImageDraw, ImageFilter
from _shared import *

OUTPUT_SLUG = "{slug}"
TITLE = "{title}"
SUBTITLE = "{subtitle}"
CONTINUITY = "{cont}"
PALETTE = {pal}

'''

VIS_FUNC = '''
def v_{name}(im, u, t, p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*0.50,h*0.42
    r=ease(u)
    for i in range(int(8*r)):
        a=i*math.tau/8+t*0.15
        x=cx+math.cos(a)*(20+15*i*r/8)
        y=cy+math.sin(a)*(20+15*i*r/8)*0.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(80*r)),width=2)
    glow_circle(im,cx,cy,12,GOLD,int(150*r),10)
    seal(im,"{label}","",GOLD)
'''

# Each pack: list of (visual_name, scene_title, scene_subtitle)
PACKS = [
    ("law_of_one_densities","The Densities of Consciousness","Law of One — 8 levels","rainbow spectrum ascending",{"ink":"1D","gold":"STO","cyan":"4D","violet":"6D","green":"green ray"},[
        ("intro","Intelligent Infinity","The One Creator aware of itself"),
        ("first","First Density: Awareness of Being","Mineral and water learning from fire and wind"),
        ("second","Second Density: Growth","The leaf striving toward the light"),
        ("third","Third Density: Self-Consciousness","The density of forgetting and choice"),
        ("fourth","Fourth Density: Love","Variable physicality — group consciousness"),
        ("fifth","Fifth Density: Wisdom","Light and knowledge united"),
        ("sixth","Sixth Density: Balance","STO and STS reconciled"),
        ("seventh","Seventh Density: Unity","The gateway to intelligent infinity"),
        ("octave","The Great Octave","Eighth density begins the next octave"),
    ]),
    ("spacious_present","All Time Is Now","Seth — simultaneous time","spiral threading all moments",{"ink":"clock time","violet":"spacious present","gold":"eternal now"},[
        ("clock","Clock Time is a Convention","The brain parses sequence"),
        ("inner","Psychological Time","The 2nd inner sense"),
        ("dreams","In Dreams You Know","Beginning and end at once"),
        ("spacious","The Spacious Present","Past, present, future coexist"),
        ("simultaneous","All Lives are Simultaneous","Reincarnation is a landscape"),
        ("past","Each Present Brings Its Past","The past changes with the present"),
        ("future","Probable Futures","You choose which to actualize"),
        ("remember","Remembering","When you remember everything, time ceases"),
    ]),
    ("you_create_reality","You Create Your Own Reality","Seth — literally","golden thread of intent",{"ink":"passive","gold":"active creator","violet":"dreaming self"},[
        ("claim","The Foundational Claim","You create your own reality"),
        ("belief","Beliefs Form Experience","What you believe shapes what you perceive"),
        ("expectation","Expectation Directs Events","Reality conforms to expectation"),
        ("emotion","Emotion is the Engine","Intensity determines speed of manifestation"),
        ("probable","Probable Realities","You choose among infinite realities each moment"),
        ("responsibility","Radical Responsibility","If you create it, you can change it"),
        ("freedom","You Are Not at the Mercy","You ARE the reality that mercy comes from"),
    ]),
    ("veils_of_forgetting","The Veil of Forgetting","Law of One — why we forget","descending curtain",{"ink":"the veil","gold":"truth","violet":"unconscious"},[
        ("veil","The Veil of Forgetting","The tool for extending free will"),
        ("purpose","Why We Forget","Without forgetting, no real choice"),
        ("before","Before the Veil","No separation between conscious and unconscious"),
        ("after","After the Veil","Third density: the density of choice"),
        ("thinning","The Veil is Thinning","As the planet moves to 4D, memory returns"),
        ("memory","What You Really Are","The infinite creator experiencing itself"),
        ("piercing","Piercing the Veil","Meditation, dreams, art, love"),
    ]),
    ("daimon_encounter","Meeting Your Own Daimon","The 5-stage path","thread of recognition",{"violet":"daimon","gold":"recognition","green":"integration"},[
        ("foundation","Foundation: Stillness","You cannot contact the daimon until you can hear"),
        ("purification","Purification: Reducing Noise","The daimon is always speaking"),
        ("threshold","The Threshold: Ego Suspension","The false self must step aside"),
        ("encounter","The Encounter: Recognition","The distinction dissolves"),
        ("integration","Integration: Communion","The daimon becomes accessible"),
        ("abramelin","The Abramelin Operation","Six-month retreat to direct vision"),
        ("samekh","Liber Samekh","Crowley's barbarous names invocation"),
        ("pgm","PGM Systasis","The egg ritual — meeting your own daimon"),
    ]),
    ("dream_incubation","The Daimon Speaks in Dreams","Synesius — dream seeding","dream-thread from daimon to sleeper",{"violet":"daimon","gold":"dream image","cyan":"pneuma"},[
        ("core","The Core Claim","The daimon impresses images on the pneuma during sleep"),
        ("pneuma","The Imaginative Pneuma","Shared medium between soul and daimon"),
        ("three","Three Dream States","Dreamless, ordinary, lucid — each has a daimonic function"),
        ("synesian","The Synesian Method","A question before sleep seeds the astral body"),
        ("curriculum","PGM Dream Curriculum","18 spells — 6 levels from dream recall to systasis"),
        ("waking","The Egg Ritual as Waking Dream","Entering the dream state consciously"),
        ("practice","Daily Practice","Write, place under pillow, listen"),
    ]),
    ("morphospace_navigation","Cells Navigate Possible Forms","Levin — basal cognition","navigating particle in morphospace",{"cyan":"bioelectric field","gold":"target form","green":"repair"},[
        ("planaria","A Flatworm Remembers","Cut it — pieces know what to become"),
        ("field","The Bioelectric Field","Voltage carries pattern across cells"),
        ("memory","Pattern Memory Without Brain","The body remembers a shape it is not wearing"),
        ("xenobot","Xenobots","Cells reorganize without genetic modification"),
        ("morphospace","The Morphospace","All possible body plans as attractors"),
        ("agency","Diverse Intelligence","Cells navigate, decide, communicate"),
        ("implication","Genes Are Not the Blueprint","The field carries the plan"),
    ]),
    ("free_energy_primitive","All Systems Minimize Surprise","Friston — free energy principle","descending prediction error",{"cyan":"prediction","gold":"surprise","green":"precision"},[
        ("principle","The Free Energy Principle","Self-organizing systems minimize surprise"),
        ("prediction","Predictive Processing","The brain predicts and updates"),
        ("active","Active Inference","Action makes world match prediction"),
        ("markov","Markov Blankets","Boundary between self and world — actively maintained"),
        ("surprise","Surprise is Information","Error is the engine of learning"),
        ("hierarchy","Hierarchical Inference","Deep models at multiple scales"),
        ("self","The Self is a Prediction","You are your brain's best guess"),
    ]),
    ("consciousness_container","Consciousness Contains the Body","Tantraloka — 36 tattvas","expanding spheres from Siva to Earth",{"gold":"Siva","violet":"Sakti","cyan":"pure path","ink":"impure path"},[
        ("siva","Siva: Pure Consciousness","The ground — without qualities, without limit"),
        ("sakti","Sakti: The Power","Consciousness is dynamic, creative, free"),
        ("descent","Descent of the Tattvas","From Siva through the pure path to the elements"),
        ("kancukas","The Five Kancukas","Self-limitation of the infinite"),
        ("maya","Maya is Not Illusion","Creative limitation that makes experience possible"),
        ("return","The Ascent","Every contraction carries the memory of expansion"),
        ("realization","Realization","Consciousness is not in the body"),
    ]),
    ("time_is_forgetting","Time Is Produced By Forgetting","Tantraloka — kalagrasa","tightening spiral of forgetting",{"gold":"simultaneity","cyan":"sequence","crimson":"forgetting"},[
        ("simultaneous","All Moments Coexist","The universe is a single act"),
        ("forgetting","Forgetting Produces Sequence","When you cannot perceive all at once"),
        ("spanda","The Pulse of Consciousness","Spanda IS time"),
        ("kalagrasa","Consuming Time","The power of time is consumed in spanda"),
        ("past","The Past is Not Gone","Hidden — recoverable, mutable"),
        ("future","The Future is Not Yet","Another region of the same landscape"),
        ("now","The Eternal Now","The spacious present"),
    ]),
    ("svatantrya_freedom","Freedom Comes Before Causality","Tantraloka — svatantrya","unbounded field contracting freely",{"gold":"freedom","crimson":"constraint","cyan":"causality"},[
        ("svatantrya","Svatantrya: Absolute Freedom","Consciousness IS freedom"),
        ("causality","Causality is Derived","Freedom contracts into law"),
        ("kancukas","The Kancukas as Self-Limitation","Freedom choosing to appear constrained"),
        ("choice","Choice is Not an Illusion","Every moment is a free act"),
        ("physics","Physics Describes Constraints","Not why there are constraints"),
        ("paradox","The Paradox of Freedom","To be free includes appearing unfree"),
        ("living","Living from Freedom","Acting without bondage to the past"),
    ]),
    ("objects_as_actions","Objects Are Frozen Actions","Tantraloka — kriya-shakti","waveforms decelerating to stasis",{"gold":"action","cyan":"appearance","ink":"object"},[
        ("tree","A Tree IS the Act of Tree-ing","Reality is verbs masquerading as nouns"),
        ("kriya","Kriya-Shakti","Consciousness does not act — it IS action"),
        ("stability","Stability is Rate","An object is slowed activity"),
        ("process","Everything is Process","Matter is frozen energy"),
        ("perception","Perception Freezes Action","Seeing solidifies the flux"),
        ("identity","You Are Not a Thing","You are a verb — activity recognizing itself"),
    ]),
    ("psyche_gestalt","The Psyche Is Not a Thing","Seth — gestalt of aware energy","rearranging energy constellation",{"violet":"psyche","gold":"individuation","cyan":"energy"},[
        ("gestalt","Gestalt of Aware Energy","It is not a thing — no beginning or ending"),
        ("creation","You Create It and It Creates You","An ever-forming state of being"),
        ("energy","Pure Energy and Individuation","Energy becomes its manifestations"),
        ("dreaming","The Dreaming Psyche is Awake","As conscious as in waking"),
        ("gods","Psyche, Languages, and Gods","Beliefs create the gods"),
        ("value","Value Fulfillment","Enhancing the quality of life itself"),
    ]),
    ("dna_antenna","DNA Is Not a Blueprint","Cassiopaean — the living antenna","double helix radiating signals",{"cyan":"DNA","gold":"signal","violet":"consciousness"},[
        ("superconductor","DNA as Superconductor","Conducts electricity — not just information"),
        ("transceiver","Neurotransceiver for Thought","DNA receives and transmits consciousness"),
        ("illusion","The Program Illusion","Linear time is a DNA readout"),
        ("strands","You Receive, Not Get","The Wave adds frequency"),
        ("removal","Removal of Knowledge Centers","Osiris cut apart = DNA frequency reduced"),
        ("antenna","The Antenna Model","DNA optimized for reception"),
    ]),
    ("constructed_self","You Are Not in Your Body","Rubber hand — self as constructed model","body outline redrawn by integration",{"gold":"self-model","cyan":"multisensory","crimson":"illusion"},[
        ("rubber","The Rubber Hand Illusion","Stroke a fake hand — it becomes yours in seconds"),
        ("swap","The Body Swap","You can feel located in another body"),
        ("obe","Out-of-Body Experience","The self can be displaced"),
        ("prediction","Predictive Processing of Body","The prediction IS the experience"),
        ("kancukas","Kancukas as Self-Parameters","Limited agency, knowledge, time, causality"),
        ("plasticity","The Self is Plastic","Updated in minutes — the mechanism of healing"),
    ]),
    ("cooperation","The Body is a Cooperative Venture","Seth — molecular cooperation","cooperating node network",{"green":"cooperation","gold":"value","cyan":"cellular"},[
        ("cooperation","The Body Exists Through Cooperation","Inner cooperative relationships bind every cell"),
        ("given","Cooperation is Given","It is the gift of life — present at birth"),
        ("molecular","Molecular Cooperation","The body speaks against chance"),
        ("value","Value Fulfillment","Enhancing quality for all species"),
        ("altruism","Innate Altruism","A natural bent for caring"),
        ("faith","Each Cell Believes","Built-in faith in a better tomorrow"),
        ("health","Health as Cooperation","Illness is broken communication"),
    ]),
]

BASE = '''VISUALS = {{
{v_funcs}
}}

SCENES = [
{scenes}
]

if __name__ == "__main__":
    build_pipeline(VISUALS, SCENES, OUTPUT_SLUG, TITLE, PALETTE, CONTINUITY)()
'''

for slug, title, subtitle, cont, pal, items in PACKS:
    v_funcs = ""
    scene_lines = []
    for vname, label, sub in items:
        v_funcs += f'    "{vname}": v_{vname},\n'
        scene_lines.append(f'    Scene("{label}", "{sub}", 7.0, "{vname}", {{}}),')

    content = BOILER.format(slug=slug, title=title, subtitle=subtitle, cont=cont, pal=pal)
    for vname, label, sub in items:
        content += VIS_FUNC.format(name=vname, label=label, sub=sub)
    content += BASE.format(
        v_funcs=v_funcs.rstrip(",\n") + ",",
        scenes="\n".join(scene_lines)
    )
    path = Path(f"/root/projects/tantraloka/goldrender/{slug}_platinum.py")
    path.write_text(content)
    print(f"Wrote {path.name}")

print("\nAll 16 packs written. Verifying compilation...")
