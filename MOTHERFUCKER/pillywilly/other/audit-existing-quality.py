#!/usr/bin/env python3
"""Audit all bridge papers: score quality and identify weakest per phase."""
import json, glob, os, re

WORKS_DIR = "/root/projects/blog/content/works"

# Phase-specific scoring dictionaries
PHASE_TERMS = {
    1: {  # Birth/Body
        "high": ["fetal consciousness", "bodily self", "body ownership", "out of body",
                 "embodied self", "minimal self", "self-location", "first-person perspective",
                 "embodied cognition", "self-consciousness", "multisensory integration",
                 "body representation", "interoception", "rubber hand illusion"],
    },
    2: {  # Breath/Soul
        "high": ["pranayama", "breathing", "respiration", "breath", "respiratory sinus",
                 "breath-brain", "cardiorespiratory", "slow breathing", "vagal tone",
                 "heart rate variability", "HRV"],
    },
    3: {  # Heat/Fire
        "high": ["kundalini", "subtle energy", "g-tummo", "tummo", "inner heat",
                 "tantric", "chakra", "yogic", "psychosomatic", "body temperature"],
    },
    4: {  # Wind/Pride
        "high": ["ego dissolution", "ego", "self-enhancement", "narcissism",
                 "hubris", "pride", "grandiose", "self-transcendence", "self-importance"],
    },
    5: {  # Water/Pleasure
        "high": ["flow state", "optimal experience", "intrinsic motivation", "aesthetic pleasure",
                 "peak experience", "self-transcendence", "ecstasy", "rapture",
                 "pleasure", "reward", "nucleus accumbens", "dopamine", "hedonic"],
    },
    6: {  # Dependent-arising
        "high": ["active inference", "free energy", "predictive coding", "predictive processing",
                 "bayesian brain", "prediction error", "synchronicity", "meaningful coincidence"],
    },
    7: {  # Form/Meditation
        "high": ["focused attention meditation", "concentrative meditation", "mindfulness meditation",
                 "meta-awareness", "body scan", "sustained attention", "executive attention"],
    },
    8: {  # Formless/Absorption
        "high": ["meditative absorption", "deep meditation", "jhana", "samadhi", "trance",
                 "altered state", "non-ordinary state", "hypnotic", "loving-kindness",
                 "compassion meditation", "metta", "self-transcendence", "mystical experience",
                 "transcendent", "transcendental meditation", "zen meditation"],
    },
    9: {  # Language/Mantra
        "high": ["mantra", "mantra meditation", "chanting", "verbal repetition", "inner speech",
                 "transcendental meditation", "focused attention", "self-talk", "private speech"],
    },
    10: {  # Imaginal
        "high": ["mental imagery", "visual imagery", "imagination", "aphantasia", "hyperphantasia",
                 "mental simulation", "pareidolia", "reality monitoring", "source monitoring",
                 "neural overlap", "shared representation", "imagery"],
    },
    11: {  # Body-energy
        "high": ["interoception", "interoceptive", "heartbeat", "insula", "allostasis",
                 "visceral", "heart-brain", "vagal", "cardiorespiratory"],
    },
    12: {  # Ritual
        "high": ["inter-brain", "interbrain", "hyperscanning", "neural synchrony", "interpersonal",
                 "synchronization", "epistemic trust", "collective effervescence", "dance",
                 "music", "entrainment", "social bonding", "shared experience"],
    },
    13: {  # Daimon
        "high": ["voice hearing", "hallucination", "auditory verbal hallucination", "inner speech",
                 "corollary discharge", "self-monitoring", "source monitoring", "agency detection"],
    },
    14: {  # Knowledge/Gnosis
        "high": ["insight", "aha moment", "insight problem", "creative insight",
                 "semantic cognition", "conceptual knowledge", "abstract knowledge",
                 "metacognition", "noetic", "gnostic", "intuitive knowledge"],
    },
    15: {  # Liberation/Enlightenment
        "high": ["ego dissolution", "self-transcendence", "self-loss", "ego death",
                 "enlightenment", "awakening", "spiritual awakening", "selflessness",
                 "no-self", "mystical experience", "peak experience"],
    },
    16: {  # Nondual/Unity
        "high": ["nondual", "non-dual", "nondual awareness", "oneness", "unity experience",
                 "oceanic", "sense of unity", "pure awareness", "pure consciousness",
                 "awareness itself", "minimal phenomenal experience", "breathwork",
                 "self-transcendence", "boundary dissolution", "transcendent"],
    },
    17: {  # Ultimate/Emptiness
        "high": ["open monitoring", "open awareness", "choiceless awareness",
                 "nothingness", "groundlessness", "emptiness", "witness consciousness",
                 "observing self", "background awareness", "field consciousness",
                 "depersonalization", "derealization"],
    },
}

def score_paper(title, abstract, phase):
    """Score a paper for bridge relevance to its phase. Returns 0-100 integer."""
    text = (title.lower() + " " + (abstract or "")).lower()
    terms = PHASE_TERMS.get(phase, {})
    score = 0
    for t in terms.get("high", []):
        if t.lower() in text:
            score += 6
    # Bonus for mechanistic terms
    mech = ["neural", "brain", "fmri", "eeg", "neuroimaging", "cortex", "activation",
            "mechanism", "pathway", "network", "connectivity", "neuroscience", "neurobiology"]
    score += sum(1 for t in mech if t in text)
    # Penalty for clinical noise
    clin = ["clinical trial", "randomized controlled", "diagnosis", "treatment", "symptom", "patient"]
    # Don't penalize if it has strong bridge terms
    has_bridge = any(t.lower() in text for t in terms.get("high", []))
    if not has_bridge:
        score -= sum(1 for t in clin if t in text)
    return max(0, score)

def main():
    # Find all v2 work JSONs
    works = {}
    for wf in sorted(glob.glob(f"{WORKS_DIR}/t2-pubmed-*.json")):
        with open(wf) as f:
            data = json.load(f)
        pm = data.get("phase_mapping", {})
        phase = pm.get("phase", 0)
        if not phase:
            continue
        title = data.get("title", "")
        abstract = data.get("assets", {}).get("abstract", "")
        score = score_paper(title, abstract, phase)
        
        # Determine quality
        if score >= 12:
            quality = "Excellent"
        elif score >= 8:
            quality = "Good"
        elif score >= 5:
            quality = "Marginal"
        else:
            quality = "Low"
        
        works[wf] = {
            "phase": phase,
            "phase_name": pm.get("phase_name", ""),
            "score": score,
            "quality": quality,
            "title": title[:60],
            "pdf": data.get("assets", {}).get("pdf_path") or data.get("pdf_file"),
            "nxml": data.get("nxml_file"),
        }
    
    # Per-phase statistics
    phases = {}
    for wf, info in works.items():
        p = info["phase"]
        if p not in phases:
            phases[p] = {"total": 0, "excellent": 0, "good": 0, "marginal": 0, "low": 0, "scores": [], "names": set()}
        phases[p]["total"] += 1
        phases[p][info["quality"].lower()] += 1
        phases[p]["scores"].append(info["score"])
        if info["phase_name"]:
            phases[p]["names"].add(info["phase_name"])
    
    print(f"{'Phase':<6} {'Name':<25} {'Total':<7} {'Exc':<5} {'Good':<6} {'Marg':<6} {'Low':<5} {'Avg Score':<10} {'Weakest Paper Score':<20}")
    print("-" * 95)
    
    weak_phases = []
    for p in sorted(phases.keys()):
        info = phases[p]
        avg = sum(info["scores"]) / max(len(info["scores"]), 1)
        name = next(iter(info["names"])) if info["names"] else "?"
        low_count = sum(1 for s in info["scores"] if s < 5)
        print(f"{p:<6} {name:<25} {info['total']:<7} {info['excellent']:<5} {info['good']:<6} {info['marginal']:<6} {info['low']:<5} {avg:<10.1f} {low_count:<20}")
        
        if low_count > 5 or avg < 8:
            weak_phases.append({"phase": p, "name": name, "low_count": low_count, "avg": avg})
    
    print(f"\n{'='*95}")
    print(f"WEAK PHASES (need improvement):")
    for wp in sorted(weak_phases, key=lambda x: x['low_count'], reverse=True):
        print(f"  Phase {wp['phase']:2d} ({wp['name']:<25}): {wp['low_count']} low-quality papers, avg score={wp['avg']:.1f}")
    
    # Show the actual lowest-scoring papers in weak phases
    print(f"\n{'='*95}")
    print(f"WEAKEST PAPERS ACROSS ALL PHASES (bottom 30):")
    sorted_works = sorted(works.items(), key=lambda x: x[1]["score"])
    for wf, info in sorted_works[:30]:
        pdf_status = "📄" if info["pdf"] else "📝" if info["nxml"] else "❌"
        print(f"  P{info['phase']:2d} ({info['phase_name']:<18}) {pdf_status} Score={info['score']:2d} [{info['quality']:<9}] {info['title']}")

if __name__ == "__main__":
    main()
