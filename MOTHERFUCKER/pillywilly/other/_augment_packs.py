#!/usr/bin/env python3
"""Augment generated packs with more scenes and visual functions."""
import os, re

PKG_DIR = "/root/projects/tantraloka/goldrender"

def augment_file(fname, extra_scenes, extra_vis_funcs=None):
    path = os.path.join(PKG_DIR, fname)
    text = open(path).read()
    
    # Add extra visual functions before VISUALS dict
    if extra_vis_funcs:
        vis_marker = "\nVISUALS = {"
        idx = text.find(vis_marker)
        if idx > 0:
            insert = "\n\n" + "\n".join(extra_vis_funcs) + "\n"
            text = text[:idx] + insert + text[idx:]
    
    # Find where SCENES list ends
    scenes_end = text.rfind("\n]")
    if scenes_end < 0:
        print(f"  {fname}: could not find scenes end")
        return
    
    # Build extra scenes
    extra_text = "\n"
    for item in extra_scenes:
        title, narration, duration, visual = item[0], item[1], item[2], item[3]
        params = item[4] if len(item) > 4 else {}
        params_str = "{" + ", ".join(f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in params.items()) + "}"
        extra_text += f'    Scene("{title}", "{narration}", {duration}, "{visual}", {params_str}),\n'
    extra_text += "\n"
    
    text = text[:scenes_end] + extra_text + text[scenes_end:]
    
    text = text.replace("; if q<=0: continue", "\n        if q<=0: continue")
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    lines = text.count("\n")
    print(f"  {fname}: augmented to {lines} lines, {len(extra_scenes)} extra scenes")


# Extra scenes for each pack (using existing visuals) - (title, narration, duration, visual_key)
augment_file("morphospace_navigation_platinum.py", [
    ("The Field Remembers", "Injury does not erase the target. The field holds the memory of wholeness.", 8.0, "memory"),
    ("Cells Solve Problems", "A cell is not a machine. It is a problem-solver with a goal.", 8.5, "agency"),
    ("Bioelectric Computation", "Voltage patterns are a computational medium. Cells compute form.", 8.5, "field"),
    ("The Body is a Democracy", "Every cell votes on the shape of the whole. Cooperation is computation.", 9.0, "agency"),
    ("Regeneration is Memory", "A salamander regrows a limb because the field remembers the arm.", 8.5, "repair", {"mode": "heal"}),
    ("Form is Intelligent", "The shape of a body is a solution to a problem. Form is cognition expressed.", 9.0, "navigation"),
    ("The Morphic Field", "Memory is not stored in the brain alone. The field carries the pattern.", 8.5, "morphospace"),
])

augment_file("free_energy_primitive_platinum.py", [
    ("The Variational Principle", "Free energy is a variational bound on surprise. All life optimizes this bound.", 8.0, "principle"),
    ("Generative Models", "Every organism is a generative model of its world. To live is to predict.", 8.5, "prediction"),
    ("The Dark Room Problem", "Why not minimize surprise by sitting in a dark room? Because value pulls us.", 8.0, "active"),
    ("Epistemic Foraging", "We seek information that resolves uncertainty. Curiosity is free energy minimization.", 8.5, "precision"),
    ("Pragmatic Value", "Not all surprises are equal. Value-weighted predictions guide action.", 8.0, "surprise"),
    ("The Free Energy of Belief", "Beliefs are models. Changing a belief reduces free energy.", 8.5, "self"),
    ("Life as Inference", "To exist is to infer. Every living system is an inference machine.", 9.0, "free_energy"),
])

augment_file("consciousness_container_platinum.py", [
    ("The Body is a Universe", "Every cell contains the whole. The microcosm reflects the macrocosm.", 8.0, "maya"),
    ("The Dance of Shiva", "The five acts are not sequential. They are simultaneous facets of one act.", 9.0, "sakti"),
    ("The Knot of Maya", "Maya is not error. It is the condition for experience.", 8.0, "maya"),
    ("The Grace of Limitation", "To be finite is a gift. The infinite learns itself through limit.", 8.5, "kancukas"),
    ("The Return", "The descent and the ascent are one movement. Consciousness never left.", 9.5, "return_path"),
    ("Sivoham", "I am That. Not as attainment - as recognition of what already is.", 10.0, "realization"),
    ("Spanda in All Things", "The universe vibrates. Every atom is a pulse of consciousness.", 8.5, "pure_path"),
])

augment_file("time_is_forgetting_platinum.py", [
    ("The Spiral of Time", "Time does not move in a line. It spirals, returning at each turn.", 8.0, "time_spiral"),
    ("Simultaneity and Sequence", "Sequence is simultaneity viewed through the lens of forgetting.", 8.5, "simultaneous_vis"),
    ("The Rhythm of Awareness", "Consciousness pulses. Between pulses, time disappears.", 8.0, "spanda_pulse"),
    ("Memory as Re-creation", "Every act of memory is a new act of creation in the present.", 8.5, "past_vis"),
    ("The Future is Probable", "Not predetermined - a distribution of possibilities collapsed by attention.", 8.5, "future_vis"),
    ("Eternal Return", "Not that events repeat. That every moment contains all moments.", 9.0, "now_vis"),
    ("Time is the Pulse of Love", "What moves through time is attention. Attention is love.", 9.5, "spanda_pulse"),
])

augment_file("svatantrya_freedom_platinum.py", [
    ("The Ground of Freedom", "Before any law, there is the freedom that chooses law.", 8.0, "svatantrya_vis"),
    ("The Willing Contract", "The kancukas are not imposed. They are chosen by freedom for experience.", 8.5, "kancukas_vis"),
    ("Causality is a Subset", "Causality is what freedom looks like when you forget you are free.", 8.5, "causality_vis"),
    ("The Unbounded Choice", "Every choice you make is a free act. You just do not remember choosing.", 8.0, "choice_vis"),
    ("Constraints are Creative", "Limitation is not the opposite of freedom. It is the medium of freedom.", 8.5, "paradox_vis"),
    ("The Witness of Freedom", "The one who watches all choices is the one who is always free.", 9.0, "svatantrya_vis"),
    ("Freedom is Not a Goal", "It is the starting point. You cannot become free. You can only know you are.", 9.5, "living_vis"),
])

augment_file("objects_as_actions_platinum.py", [
    ("The Verb Universe", "The universe is not a collection of nouns. It is a dance of verbs.", 8.0, "tree"),
    ("Nouns are Frozen Verbs", "A noun is a verb we no longer see moving. Language freezes process.", 8.5, "stability_vis"),
    ("The Action of Appearing", "To appear is an act. Existence is something reality does.", 8.5, "kriya_vis"),
    ("Perception as Freezing", "To perceive is to slow the flux until patterns become visible.", 8.0, "perception_vis"),
    ("The Activity of Being", "Being is not a state. It is the most fundamental activity.", 9.0, "process_vis"),
    ("The Self is a Verb", "You are not a thing that acts. You are the acting itself.", 9.0, "identity_vis"),
    ("Action is Recognition", "Consciousness recognizes itself in the mirror of its own actions.", 9.5, "kriya_vis"),
])

augment_file("psyche_gestalt_platinum.py", [
    ("The Unfinished Psyche", "The psyche is never complete. It is always becoming what it is.", 8.0, "gestalt_vis"),
    ("Energy Takes Form", "Psychic energy crystallizes into beliefs, thoughts, and experiences.", 8.5, "energy_vis"),
    ("The Dream Architect", "The psyche designs dreams as rehearsal for waking reality.", 8.5, "dreaming_vis"),
    ("The Gods are Psychic Organs", "Gods are not external beings. They are living structures within the psyche.", 9.0, "gods_vis"),
    ("Value is the Steering", "The psyche moves toward what enhances life. Value is its compass.", 8.5, "value_vis"),
    ("The Open Gestalt", "The psyche is not a closed system. It is a conversation with the universe.", 9.0, "creation_vis"),
    ("You and Your Psyche", "You are not the owner of your psyche. You are its current expression.", 9.5, "gestalt_vis"),
])

augment_file("dna_antenna_platinum.py", [
    ("DNA is a Receiver", "You do not generate your reality. You receive it through DNA.", 8.0, "transceiver"),
    ("The Frequency of Life", "Life is a frequency that DNA is tuned to receive.", 8.5, "antenna_vis"),
    ("The Program is a Metaphor", "The genetic program is a useful metaphor, not a literal instruction set.", 8.0, "illusion"),
    ("The Wave and the Antenna", "Consciousness is a wave. DNA is the antenna that translates it into form.", 9.0, "strands"),
    ("Repairing the Antenna", "Healing is restoring the DNA to full reception capacity.", 8.5, "superconductor"),
    ("12 Strands of Light", "The 12-strand DNA is not biological. It is the full spectrum of reception.", 9.0, "antenna_vis"),
    ("You Are the Signal", "Not the receiver. Not the antenna. You are the signal experiencing itself.", 9.5, "strands"),
])

augment_file("constructed_self_platinum.py", [
    ("The Self is a Prediction", "The experience of 'I' is a prediction your brain makes about who is here.", 8.5, "prediction"),
    ("The Body Schema", "Your brain maintains a constantly updated model of your body. That model IS your body.", 8.0, "rubber"),
    ("The Empathic Self", "You can feel another's body as your own. The self-model extends beyond the skin.", 8.5, "swap"),
    ("The Narrative Self", "The story you tell about yourself IS the self you experience.", 8.5, "kancukas_self"),
    ("The Minimal Self", "Before the story, before the body, there is the bare sense of being.", 9.0, "obe"),
    ("The Self is Not a Thing", "Like the psyche, the self is a process, not an entity.", 9.5, "plasticity"),
    ("Liberating the Model", "When the self-model becomes flexible, healing happens. The cage opens.", 9.5, "plasticity"),
])

augment_file("cooperation_platinum.py", [
    ("The Symbiotic Body", "Your body contains more bacterial cells than human cells. Cooperation is the rule.", 8.5, "cooperation_vis"),
    ("The Gift of Life", "Every cell receives its life from the whole. Nothing is self-made.", 8.5, "given_vis"),
    ("The Immune System as Listener", "The immune system does not attack. It listens and responds.", 8.0, "molecular_vis"),
    ("Collective Intelligence", "The body is a swarm intelligence. No single cell knows the whole, but the whole knows itself.", 9.0, "cooperation_vis"),
    ("Cooperation is Consciousness", "When cells cooperate, consciousness emerges. The whole becomes aware of itself.", 9.5, "value_fulfillment"),
    ("The Body as Ecosystem", "Your body is an ecosystem of trillions of cooperating beings. You are their world.", 9.0, "molecular_vis"),
    ("Healing is Reconnection", "What we call illness is a breakdown of cooperation. Health is restored dialogue.", 9.5, "health_vis"),
])

print("Augmentation complete.")
