#!/usr/bin/env python3
"""
Add evaluation scores to all existing t2 bridge works.
Uses the same scoring system as the v2 acquisition pipeline.
"""
import glob, json, os, re, sys, time

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"

# ─── Phase-specific scoring terms (same as v2 script) ───
PHASE_TERMS = {
    1: [ # Dashboard Diagnosis - Metacognition
        ("metacognition", 1.5), ("metacognitive", 1.5), ("self-awareness", 1.2),
        ("self-monitoring", 1.2), ("meta-awareness", 1.5), ("prefrontal", 0.5),
        ("anterior cingulate", 0.5), ("error awareness", 1.2), ("confidence", 0.5),
        ("insight", 0.4), ("self-reflection", 0.8), ("introspection", 0.8),
    ],
    2: [ # Physical De-solidification - Body Illusion
        ("rubber hand", 1.5), ("body ownership", 1.5), ("multisensory ownership", 1.5),
        ("body representation", 1.2), ("body schema", 1.2), ("peripersonal", 1.0),
        ("full body illusion", 1.5), ("out-of-body", 1.2), ("virtual body", 0.8),
        ("ownership", 0.6), ("embodiment illusion", 1.2), ("self-other", 0.8),
    ],
    3: [ # Mind as Computer Critique - 4E Cognition
        ("embodied cognition", 1.5), ("grounded cognition", 1.2), ("enactive", 1.5),
        ("extended mind", 1.5), ("situated cognition", 1.2), ("sensorimotor", 0.8),
        ("4e cognition", 1.5), ("predictive processing", 0.6), ("active inference", 0.6),
    ],
    4: [ # Nested Agency
        ("sense of agency", 1.5), ("intentional binding", 1.5), ("voluntary action", 1.2),
        ("volition", 1.0), ("free will", 1.0), ("agency attribution", 1.5),
        ("self-agency", 1.2), ("corollary discharge", 1.2), ("efference copy", 1.0),
    ],
    5: [ # Mechanicality - Habit
        ("habit", 1.2), ("habitual", 1.2), ("automaticity", 1.5), ("chunking", 1.0),
        ("goal-directed", 0.6), ("action monitoring", 1.0), ("conflict monitoring", 0.8),
        ("error-related negativity", 1.0), ("compulsive", 0.8), ("striatum", 0.8),
        ("cortico-striatal", 1.0), ("automatic", 0.4),
    ],
    6: [ # Dependent Arising - Predictive Processing
        ("free energy principle", 1.5), ("active inference", 1.5), ("predictive coding", 1.2),
        ("predictive processing", 1.2), ("bayesian brain", 1.5), ("hierarchical predictive", 1.0),
        ("prediction error", 0.8), ("causal inference", 0.8), ("markov blanket", 1.5),
        ("free energy", 0.8), ("bayesian", 0.5),
    ],
    7: [ # Emptiness - Self-Dissolution
        ("ego dissolution", 1.5), ("self-loss", 1.5), ("self-transcendence", 1.2),
        ("default mode", 0.8), ("nondual", 1.5), ("non-dual", 1.5),
        ("depersonalization", 0.8), ("derealization", 0.6), ("self-boundary", 1.0),
        ("self-referential", 0.5), ("meditation", 0.5), ("psychedelic", 0.5),
    ],
    8: [ # Non-fabrication - Spontaneous Thought
        ("spontaneous thought", 1.5), ("mind-wandering", 1.5), ("daydreaming", 1.2),
        ("creative cognition", 1.0), ("creative insight", 1.0), ("divergent thinking", 0.8),
        ("involuntary thought", 1.2), ("incubation", 1.0), ("aha moment", 1.2),
        ("insight", 0.5), ("resting state", 0.4),
    ],
    9: [ # Language/Mantra
        ("mantra", 1.5), ("mantra meditation", 1.8), ("inner speech", 1.5),
        ("inner voice", 1.2), ("self-talk", 1.0), ("private speech", 0.8),
        ("focused attention", 0.8), ("verbal repetition", 1.0), ("prayer", 0.8),
        ("transcendental meditation", 1.2),
    ],
    10: [ # Imaginal Reconstruction
        ("mental imagery", 1.5), ("visual imagery", 1.2), ("aphantasia", 1.8),
        ("hyperphantasia", 1.5), ("imagery deficit", 1.0), ("pareidolia", 1.5),
        ("reality monitoring", 1.0), ("source monitoring", 0.8), ("imagination", 0.6),
        ("mental simulation", 0.8), ("early visual", 0.5),
    ],
    11: [ # Body-energy - Interoception
        ("interoception", 1.5), ("interoceptive", 1.5), ("cardiac interoception", 1.5),
        ("heartbeat evoked", 1.5), ("heartbeat detection", 1.2), ("allostasis", 1.2),
        ("insula", 0.5), ("visceral", 0.8), ("vagal", 0.8), ("breathing", 0.5),
        ("respiratory", 0.5), ("vagus", 0.6),
    ],
    12: [ # Ritual - Neural Synchrony
        ("hyperscanning", 1.8), ("inter-brain", 1.5), ("brain-to-brain", 1.5),
        ("interpersonal synchronization", 1.5), ("neural synchrony", 1.2),
        ("joint action", 1.0), ("joint attention", 0.8), ("rhythmic entrainment", 1.0),
        ("brain entrainment", 1.0), ("coherence", 0.4), ("collective", 0.5),
    ],
    13: [ # Daimon - Voice-Hearing
        ("auditory verbal hallucination", 1.5), ("voice hearing", 1.5),
        ("hallucination proneness", 1.2), ("inner speech", 0.8),
        ("corollary discharge", 1.2), ("source monitoring", 0.8),
        ("agency detection", 1.0), ("self-monitoring", 0.5), ("hallucinations", 0.5),
        ("psychosis", 0.4),
    ],
    14: [ # Nonordinary Rendering - Psychedelics
        ("psilocybin", 1.2), ("psychedelic", 1.2), ("dmt", 0.8),
        ("ego dissolution", 1.5), ("altered states", 1.0),
        ("entropic brain", 1.5), ("brain entropy", 1.0), ("lsd", 0.8),
        ("ayahuasca", 1.0), ("default mode", 0.5),
    ],
    15: [ # Ecology/Animism
        ("nature connectedness", 1.5), ("nature exposure", 1.2),
        ("biophilia", 1.5), ("biophilic", 1.2), ("attention restoration", 1.0),
        ("green space", 0.8), ("nature", 0.3), ("awe", 0.8),
        ("environmental neuroscience", 1.5),
    ],
    16: [ # Visionary Cosmologies
        ("self-transcendence", 1.5), ("transcendence", 1.2), ("mystical experience", 1.5),
        ("mystical", 0.8), ("numinous", 1.5), ("awe", 0.8),
        ("cosmic consciousness", 1.8), ("oceanic", 1.0), ("unity consciousness", 1.2),
        ("transcendent", 0.8),
    ],
    17: [ # Social Incarnation
        ("second-person", 1.5), ("intersubjectivity", 1.5), ("embodied empathy", 1.5),
        ("shared intentionality", 1.2), ("predictive processing", 0.5),
        ("social cognition", 0.6), ("empathy", 0.5), ("mirror neuron", 0.8),
        ("interoception", 0.5), ("social brain", 0.4),
    ],
}

CROSS_TERMS = [
    ("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("neuroimaging", 0.5),
    ("cortex", 0.3), ("EEG", 0.4), ("mechanism", 0.5),
]

NOISE = ["clinical trial", "pharmacological", "treatment outcome", "case report",
         "rat ", " mice ", "murine", "animal model", "surgery", "drug therapy",
         "randomized controlled", "phase 2", "phase 3"]

def score_text(title, abstract, phase):
    """Score a paper's bridge relevance using phase-specific terms."""
    text = f"{title} {abstract}".lower()
    
    # Noise check
    for n in NOISE:
        if n in text:
            return 0, f"Noise: '{n}'"
    
    # Phase-specific terms
    score = 0
    terms = PHASE_TERMS.get(phase, [])
    for term, weight in terms:
        if term in text:
            score += weight
    
    # Cross-phase neural/mechanistic boost
    for term, weight in CROSS_TERMS:
        if term in text:
            score += weight
    
    # Labels
    if score >= 3.5:
        return score, f"Excellent (score={score:.1f})"
    elif score >= 2.5:
        return score, f"Good (score={score:.1f})"
    elif score >= 1.5:
        return score, f"Marginal (score={score:.1f})"
    else:
        return score, f"Low signal (score={score:.1f})"

def main():
    # Process all t2 works (pubmed + pmc + arxiv + levin)
    works = sorted(glob.glob(f"{WORKS_DIR}/t2-*.json"))
    print(f"Found {len(works)} total works")
    
    scored = 0
    already_scored = 0
    no_phase = 0
    score_counts = {"Excellent": 0, "Good": 0, "Marginal": 0, "Low": 0, "Noise": 0}
    
    for w in works:
        try:
            data = json.load(open(w))
        except:
            continue
        
        # Skip if already has evaluation
        if data.get("evaluation") or data.get("evaluation_text"):
            already_scored += 1
            continue
        
        # Get phase
        pm = data.get("phase_mapping", {})
        phase = pm.get("phase", 0) if pm else 0
        if not phase:
            no_phase += 1
            continue
        
        # Get title and abstract
        title = data.get("title", "")
        abstract = data.get("assets", {}).get("abstract", "")
        
        # Score
        score_val, score_label = score_text(title, abstract, phase)
        
        # Add evaluation to work JSON
        data["evaluation"] = score_label
        
        with open(w, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        scored += 1
        
        # Track distribution
        if "Excellent" in score_label:
            score_counts["Excellent"] += 1
        elif "Good" in score_label:
            score_counts["Good"] += 1
        elif "Marginal" in score_label:
            score_counts["Marginal"] += 1
        elif "Low" in score_label:
            score_counts["Low"] += 1
        else:
            score_counts["Noise"] += 1
    
    print(f"\nScoring Results:")
    print(f"  Newly scored: {scored}")
    print(f"  Already scored: {already_scored}")
    print(f"  No phase: {no_phase}")
    print(f"\n  Score distribution:")
    for label, count in sorted(score_counts.items()):
        print(f"    {label}: {count}")
    
    # Phase-by-phase summary
    print(f"\nPhase-by-phase counts:")
    for p in range(1, 18):
        phase_works = []
        for w in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try:
                data = json.load(open(w))
            except:
                continue
            pm = data.get("phase_mapping", {})
            if pm and pm.get("phase") == p:
                eval_label = data.get("evaluation", "No evaluation")
                pdf = data.get("assets", {}).get("pdf_path", "")
                phase_works.append((data.get("title","?"), eval_label, pdf))
        name = next((pm.get("phase_name","") for w2 in glob.glob(f"{WORKS_DIR}/t2-*.json") 
                     if (lambda d: json.load(open(w2)))(None) and False), "")
        # Get name properly
        names = set()
        for w2 in glob.glob(f"{WORKS_DIR}/t2-*.json"):
            try:
                d2 = json.load(open(w2))
                pm2 = d2.get("phase_mapping", {})
                if pm2 and pm2.get("phase") == p:
                    names.add(pm2.get("phase_name", ""))
            except: pass
        name = next(iter(names)) if names else ""
        
        pdfs = sum(1 for _, _, p in phase_works if p)
        excellent = sum(1 for _, e, _ in phase_works if e and "Excellent" in e)
        good = sum(1 for _, e, _ in phase_works if e and "Good" in e)
        marginal = sum(1 for _, e, _ in phase_works if e and "Marginal" in e)
        print(f"  Phase {p:2d} ({name or '?':30s}): {len(phase_works):2d} works, {pdfs:2d} PDFs, {excellent} Exc, {good} Good, {marginal} Marginal")

if __name__ == "__main__":
    main()
