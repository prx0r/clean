#!/usr/bin/env python3
"""
Frontier Science Bridge Paper Acquisition — PubMed/MEDLINE
Searches for 50 high-signal bridge papers per phase across all 17 phases.
Phase definitions, bridge keywords, scoring, work JSON + essay JSON creation.
"""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET

BASE_DIR = "/root/projects/blog"
CONTENT_WORKS = f"{BASE_DIR}/content/works"
CONTENT_ESSAYS = f"{BASE_DIR}/content/glossary/essays"
LIBRARY_FRONTIER = f"{BASE_DIR}/library/frontier"
ACQUISITION_LOG = f"{BASE_DIR}/hermes/notes/t2-acquisition-log.md"

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OA_SVC = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
EMAIL = "hermes@research.local"
DELAY = 1.0

# ─── Phase Definitions ───
PHASES = {
    "phase-1-metacognition": {
        "phase": 1, "name": "Dashboard Diagnosis",
        "concept": "Metacognition as self-observation — neural substrate of knowing that one knows.",
        "bridge_rationale": "Metacognition — self-awareness, self-monitoring, neural correlates of meta-awareness.",
        "queries": [
            '("metacognition"[Title/Abstract] OR "metacognitive"[Title/Abstract]) AND ("prefrontal cortex"[Title/Abstract] OR "anterior prefrontal"[Title/Abstract] OR "frontopolar"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "neuroimaging"[Title/Abstract]) AND 2010:2025[dp]',
            '("self-awareness"[Title/Abstract] OR "self-monitoring"[Title/Abstract] OR "meta-awareness"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND ("medial prefrontal"[Title/Abstract] OR "anterior cingulate"[Title/Abstract]) AND 2010:2025[dp]',
            '("metacognitive accuracy"[Title/Abstract] OR "metacognitive insight"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            '("confidence judgments"[Title/Abstract] OR "metacognitive judgments"[Title/Abstract]) AND ("neural basis"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("error monitoring"[Title/Abstract] OR "performance monitoring"[Title/Abstract] OR "error awareness"[Title/Abstract]) AND ("anterior cingulate"[Title/Abstract] OR "prefrontal"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-2-body-illusion": {
        "phase": 2, "name": "Physical De-solidification",
        "concept": "Body as constructed percept — multisensory integration, rubber hand illusion, ownership plasticity.",
        "bridge_rationale": "Body illusion — multisensory integration, rubber hand illusion, body ownership as constructed percept.",
        "queries": [
            '("rubber hand illusion"[Title/Abstract] OR "body ownership"[Title/Abstract] OR "multisensory ownership"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            '("body representation"[Title/Abstract] OR "body schema"[Title/Abstract] OR "bodily self"[Title/Abstract]) AND ("multisensory integration"[Title/Abstract] OR "temporal parietal"[Title/Abstract] OR "premotor"[Title/Abstract]) AND 2010:2025[dp]',
            '("self-other distinction"[Title/Abstract] OR "body boundary"[Title/Abstract] OR "peripersonal space"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            '("full body illusion"[Title/Abstract] OR "out-of-body"[Title/Abstract] OR "virtual body"[Title/Abstract] OR "embodiment illusion"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("ownership"[Title/Abstract] AND "agency"[Title/Abstract] AND "body"[Title/Abstract] AND ("premotor"[Title/Abstract] OR "insula"[Title/Abstract] OR "parietal"[Title/Abstract])) AND 2010:2025[dp]',
        ],
    },
    "phase-3-4e-cognition": {
        "phase": 3, "name": "Mind as Computer Critique",
        "concept": "Mind not a computer — embodied, embedded, enactive, extended cognition.",
        "bridge_rationale": "4E cognition — embodied, embedded, enactive, extended mind; critique of computationalism.",
        "queries": [
            '("embodied cognition"[Title/Abstract] OR "grounded cognition"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "sensorimotor"[Title/Abstract]) AND 2010:2025[dp]',
            '("enactive"[Title/Abstract] AND ("cognition"[Title/Abstract] OR "perception"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract])) AND 2010:2025[dp]',
            '("extended mind"[Title/Abstract] OR "situated cognition"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "cognition"[Title/Abstract] OR "embodied"[Title/Abstract]) AND 2010:2025[dp]',
            '("predictive processing"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("embodied"[Title/Abstract] OR "enactive"[Title/Abstract] OR "4E"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-4-agency": {
        "phase": 4, "name": "Nested Agency",
        "concept": "Sense of agency — voluntary action, free will as constructed experience, intentional binding.",
        "bridge_rationale": "Nested agency — voluntary action, free will as constructed experience, intentional binding.",
        "queries": [
            '("sense of agency"[Title/Abstract] OR "intentional binding"[Title/Abstract] OR "sense of control"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("voluntary action"[Title/Abstract] OR "volition"[Title/Abstract] OR "free will"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "prefrontal"[Title/Abstract]) AND 2010:2025[dp]',
            '("agency attribution"[Title/Abstract] OR "self-agency"[Title/Abstract] OR "sense of authorship"[Title/Abstract]) AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract] OR "insula"[Title/Abstract]) AND 2010:2025[dp]',
            '("corollary discharge"[Title/Abstract] OR "efference copy"[Title/Abstract]) AND ("agency"[Title/Abstract] OR "self"[Title/Abstract] OR "motor"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-5-mechanicality": {
        "phase": 5, "name": "Mechanicality",
        "concept": "Habit as automated behavior — loss of conscious control, automaticity, action monitoring.",
        "bridge_rationale": "Mechanicality — habit as automated behavior, loss of conscious control, automaticity.",
        "queries": [
            '("habit"[Title/Abstract] OR "habitual"[Title/Abstract] OR "automaticity"[Title/Abstract]) AND ("striatum"[Title/Abstract] OR "basal ganglia"[Title/Abstract] OR "cortico-striatal"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("action monitoring"[Title/Abstract] OR "conflict monitoring"[Title/Abstract] OR "error-related negativity"[Title/Abstract]) AND ("automatic"[Title/Abstract] OR "controlled"[Title/Abstract] OR "conscious"[Title/Abstract]) AND 2010:2025[dp]',
            '("chunking"[Title/Abstract] AND "behavior"[Title/Abstract] AND ("striatum"[Title/Abstract] OR "prefrontal"[Title/Abstract])) AND 2010:2025[dp]',
            '("goal-directed"[Title/Abstract] AND "habitual"[Title/Abstract] AND "control"[Title/Abstract] AND ("prefrontal"[Title/Abstract] OR "striatum"[Title/Abstract] OR "cortex"[Title/Abstract])) AND 2010:2025[dp]',
            '("compulsive"[Title/Abstract] OR "addiction"[Title/Abstract] OR "stereotype"[Title/Abstract]) AND ("habit"[Title/Abstract] OR "automatic"[Title/Abstract]) AND ("cortico-striatal"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-6-dependent-arising": {
        "phase": 6, "name": "Dependent Arising",
        "concept": "Predictive processing — free energy principle, active inference, Bayesian brain.",
        "bridge_rationale": "Dependent arising — predictive processing, free energy principle, active inference as causal cognition.",
        "queries": [
            '("free energy principle"[Title/Abstract] OR "active inference"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognition"[Title/Abstract]) AND ("behavior"[Title/Abstract] OR "perception"[Title/Abstract] OR "action"[Title/Abstract]) AND 2018:2025[dp]',
            '("predictive coding"[Title/Abstract] OR "predictive processing"[Title/Abstract]) AND ("hierarchical"[Title/Abstract] OR "Bayesian"[Title/Abstract]) AND ("perception"[Title/Abstract] OR "cognition"[Title/Abstract] OR "motor"[Title/Abstract]) AND 2018:2025[dp]',
            '("Bayesian brain"[Title/Abstract] OR "hierarchical Bayesian"[Title/Abstract]) AND ("perception"[Title/Abstract] OR "decision"[Title/Abstract] OR "learning"[Title/Abstract]) AND 2018:2025[dp]',
            '("prediction error"[Title/Abstract] AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND ("learning"[Title/Abstract] OR "perception"[Title/Abstract] OR "attention"[Title/Abstract])) AND 2018:2025[dp]',
            '("causal inference"[Title/Abstract] AND "predictive coding"[Title/Abstract]) OR ("Markov blanket"[Title/Abstract] AND "brain"[Title/Abstract]) AND 2018:2025[dp]',
        ],
    },
    "phase-7-emptiness": {
        "phase": 7, "name": "Emptiness",
        "concept": "Self-dissolution — ego dissolution, DMN decoupling, non-self in neuroscience.",
        "bridge_rationale": "Emptiness — dissolution of self, DMN decoupling, ego dissolution, nondual awareness.",
        "queries": [
            '("ego dissolution"[Title/Abstract] OR "self-loss"[Title/Abstract] OR "self-transcendence"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2010:2025[dp]',
            '("default mode network"[Title/Abstract] OR "DMN"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "mindfulness"[Title/Abstract] OR "psychedelic"[Title/Abstract]) AND ("self"[Title/Abstract] OR "self-referential"[Title/Abstract] OR "ego"[Title/Abstract]) AND 2010:2025[dp]',
            '("nondual"[Title/Abstract] OR "non-dual"[Title/Abstract] OR "nondual awareness"[Title/Abstract]) AND ("meditation"[Title/Abstract] OR "neuroscience"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2010:2025[dp]',
            '("depersonalization"[Title/Abstract] OR "derealization"[Title/Abstract] OR "self-boundary"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2015:2025[dp]',
        ],
    },
    "phase-8-spontaneous": {
        "phase": 8, "name": "Non-fabrication",
        "concept": "Spontaneous thought — mind-wandering, DMN, creative insight, involuntary cognition.",
        "bridge_rationale": "Non-fabrication — spontaneous thought, mind-wandering, DMN, creative insight.",
        "queries": [
            '("spontaneous thought"[Title/Abstract] OR "mind-wandering"[Title/Abstract] OR "daydreaming"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "DMN"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
            '("creative cognition"[Title/Abstract] OR "creative insight"[Title/Abstract] OR "divergent thinking"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "executive"[Title/Abstract] OR "brain network"[Title/Abstract]) AND 2010:2025[dp]',
            '("involuntary thought"[Title/Abstract] OR "involuntary memory"[Title/Abstract] OR "task-unrelated"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("resting state"[Title/Abstract] AND "thought"[Title/Abstract] AND ("spontaneous"[Title/Abstract] OR "mind-wandering"[Title/Abstract] OR "self-generated"[Title/Abstract])) AND 2015:2025[dp]',
            '("incubation"[Title/Abstract] OR "aha moment"[Title/Abstract] OR "insight"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "EEG"[Title/Abstract]) AND ("creativity"[Title/Abstract] OR "problem solving"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-9-language": {
        "phase": 9, "name": "Language/Mantra",
        "concept": "Mantra meditation, inner speech, focused attention, language as mantra.",
        "bridge_rationale": "Language as mantra — mantra meditation, inner speech, focused attention, verbal repetition.",
        "queries": [
            '("mantra"[Title/Abstract] OR "mantra meditation"[Title/Abstract] OR "transcendental meditation"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2005:2025[dp]',
            '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract] OR "self-talk"[Title/Abstract] OR "private speech"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2010:2025[dp]',
            '("focused attention"[Title/Abstract] AND "meditation"[Title/Abstract] AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "network"[Title/Abstract])) AND 2010:2025[dp]',
            '("verbal repetition"[Title/Abstract] OR "silent repetition"[Title/Abstract] OR "prayer"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2005:2025[dp]',
        ],
    },
    "phase-10-imaginal": {
        "phase": 10, "name": "Imaginal Reconstruction",
        "concept": "Mental imagery as real perception — imagination, pareidolia, aphantasia.",
        "bridge_rationale": "Imaginal — mental imagery as real perception, imagination activating sensory cortices, aphantasia.",
        "queries": [
            '("mental imagery"[Title/Abstract] OR "visual imagery"[Title/Abstract]) AND ("primary visual cortex"[Title/Abstract] OR "V1"[Title/Abstract] OR "early visual"[Title/Abstract]) AND ("fMRI"[Title/Abstract] OR "neuroimaging"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2015:2025[dp]',
            '("aphantasia"[Title/Abstract] OR "hyperphantasia"[Title/Abstract] OR "imagery deficit"[Title/Abstract] OR "imagery ability"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cortex"[Title/Abstract]) AND 2015:2025[dp]',
            '("pareidolia"[Title/Abstract] AND "brain"[Title/Abstract] OR "face perception"[Title/Abstract] AND "imagery"[Title/Abstract]) AND 2010:2025[dp]',
            '("reality monitoring"[Title/Abstract] OR "source monitoring"[Title/Abstract]) AND ("imagery"[Title/Abstract] OR "imagination"[Title/Abstract] OR "perception"[Title/Abstract]) AND ("prefrontal"[Title/Abstract] OR "hippocampus"[Title/Abstract]) AND 2010:2025[dp]',
            '("imagination"[Title/Abstract] AND "perception"[Title/Abstract] AND "neural overlap"[Title/Abstract]) OR ("mental simulation"[Title/Abstract] AND "sensory cortex"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-11-body-energy": {
        "phase": 11, "name": "Body-energy",
        "concept": "Interoception as spiritus — visceral perception, cardiac interoception, felt aliveness.",
        "bridge_rationale": "Body-energy — interoception, heart-brain axis, breathing entrainment, spiritus.",
        "queries": [
            '("interoception"[Title/Abstract] OR "interoceptive"[Title/Abstract]) AND ("insula"[Title/Abstract] OR "anterior cingulate"[Title/Abstract]) AND ("cardiac"[Title/Abstract] OR "heartbeat"[Title/Abstract] OR "visceral"[Title/Abstract]) AND 2015:2025[dp]',
            '("heartbeat evoked"[Title/Abstract] OR "heartbeat detection"[Title/Abstract] OR "cardiac interoception"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "cortex"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2015:2025[dp]',
            '("allostasis"[Title/Abstract] OR "allostatic"[Title/Abstract]) AND ("interoception"[Title/Abstract] OR "brain"[Title/Abstract] OR "predictive"[Title/Abstract]) AND 2015:2025[dp]',
            '("breathing"[Title/Abstract] OR "respiratory"[Title/Abstract]) AND ("interoception"[Title/Abstract] OR "insula"[Title/Abstract] OR "brain rhythm"[Title/Abstract]) AND 2015:2025[dp]',
            '("vagal"[Title/Abstract] OR "vagus"[Title/Abstract]) AND ("interoception"[Title/Abstract] OR "brain"[Title/Abstract] OR "emotion"[Title/Abstract] OR "self"[Title/Abstract]) AND 2015:2025[dp]',
        ],
    },
    "phase-12-ritual": {
        "phase": 12, "name": "Ritual",
        "concept": "Neural synchrony in ritual — interpersonal brain-to-brain coupling during shared behavior.",
        "bridge_rationale": "Ritual — neural synchrony in joint action, hyperscanning, interpersonal entrainment, collective bonding.",
        "queries": [
            '("hyperscanning"[Title/Abstract] OR "inter-brain"[Title/Abstract] OR "brain-to-brain"[Title/Abstract]) AND ("synchronization"[Title/Abstract] OR "synchrony"[Title/Abstract] OR "coherence"[Title/Abstract]) AND 2015:2025[dp]',
            '("interpersonal neural"[Title/Abstract] OR "interpersonal synchronization"[Title/Abstract]) AND ("EEG"[Title/Abstract] OR "fNIRS"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2010:2025[dp]',
            '("joint action"[Title/Abstract] OR "joint attention"[Title/Abstract]) AND ("neural synchrony"[Title/Abstract] OR "brain coupling"[Title/Abstract] OR "interpersonal"[Title/Abstract]) AND 2010:2025[dp]',
            '("music"[Title/Abstract] OR "rhythmic"[Title/Abstract] OR "drumming"[Title/Abstract]) AND ("neural synchrony"[Title/Abstract] OR "brain entrainment"[Title/Abstract] OR "synchronization"[Title/Abstract]) AND 2015:2025[dp]',
            '("collective"[Title/Abstract] AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract]) AND ("synchrony"[Title/Abstract] OR "coherence"[Title/Abstract]) AND ("social"[Title/Abstract] OR "group"[Title/Abstract])) AND 2015:2025[dp]',
        ],
    },
    "phase-13-daimon": {
        "phase": 13, "name": "Daimon",
        "concept": "Voice-hearing as spectrum phenomenon — auditory verbal hallucinations, agency detection, inner speech.",
        "bridge_rationale": "Daimonic voice — voice-hearing continuum, inner speech misattribution, corollary discharge.",
        "queries": [
            '("auditory verbal hallucination"[Title/Abstract] OR "voice hearing"[Title/Abstract]) AND ("continuum"[Title/Abstract] OR "spectrum"[Title/Abstract] OR "non-clinical"[Title/Abstract] OR "proneness"[Title/Abstract]) AND 2010:2025[dp]',
            '("inner speech"[Title/Abstract] OR "inner voice"[Title/Abstract]) AND ("hallucination"[Title/Abstract] OR "auditory"[Title/Abstract]) AND ("source monitoring"[Title/Abstract] OR "self-monitoring"[Title/Abstract]) AND 2010:2025[dp]',
            '("corollary discharge"[Title/Abstract] OR "efference copy"[Title/Abstract]) AND ("auditory"[Title/Abstract] OR "speech"[Title/Abstract] OR "voice"[Title/Abstract] OR "hallucination"[Title/Abstract]) AND 2010:2025[dp]',
            '("agency detection"[Title/Abstract] OR "hypervigilance"[Title/Abstract]) AND ("voice"[Title/Abstract] OR "hallucination"[Title/Abstract]) AND 2010:2025[dp]',
            '("predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract]) AND ("hallucinations"[Title/Abstract] OR "psychosis"[Title/Abstract] OR "auditory"[Title/Abstract]) AND 2015:2025[dp]',
        ],
    },
    "phase-14-psychedelic": {
        "phase": 14, "name": "Nonordinary Rendering",
        "concept": "Psychedelic decoupling — DMN disruption, ego dissolution, altered states of consciousness.",
        "bridge_rationale": "Nonordinary — psychedelic decoupling, ego dissolution, DMN disruption, altered states.",
        "queries": [
            '("psilocybin"[Title/Abstract] OR "psychedelic"[Title/Abstract] OR "DMT"[Title/Abstract]) AND ("default mode"[Title/Abstract] OR "DMN"[Title/Abstract] OR "neural"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "self"[Title/Abstract] OR "brain"[Title/Abstract]) AND 2015:2025[dp]',
            '("ego dissolution"[Title/Abstract] OR "ego-disintegration"[Title/Abstract] OR "self-dissolution"[Title/Abstract]) AND ("psychedelic"[Title/Abstract] OR "psilocybin"[Title/Abstract] OR "LSD"[Title/Abstract]) AND 2015:2025[dp]',
            '("altered states"[Title/Abstract] AND "consciousness"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "network"[Title/Abstract])) AND 2010:2025[dp]',
            '("entropic brain"[Title/Abstract] OR "brain entropy"[Title/Abstract] OR "neural entropy"[Title/Abstract]) AND ("consciousness"[Title/Abstract] OR "psychedelic"[Title/Abstract] OR "altered"[Title/Abstract]) AND 2015:2025[dp]',
        ],
    },
    "phase-15-ecology": {
        "phase": 15, "name": "Ecology/Animism",
        "concept": "Biophilia, nature connectedness, neurobiophilia, environmental neuroscience.",
        "bridge_rationale": "Ecology/Animism — biophilia, nature connectedness, environmental neuroscience, neurobiophilia.",
        "queries": [
            '("nature connectedness"[Title/Abstract] OR "nature exposure"[Title/Abstract] OR "nature experience"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "EEG"[Title/Abstract]) AND 2010:2025[dp]',
            '("biophilia"[Title/Abstract] OR "biophilic"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "psychology"[Title/Abstract] OR "wellbeing"[Title/Abstract]) AND 2005:2025[dp]',
            '("nature"[Title/Abstract] AND "attention restoration"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "cognitive"[Title/Abstract])) AND 2010:2025[dp]',
            '("green space"[Title/Abstract] OR "natural environment"[Title/Abstract]) AND ("mental health"[Title/Abstract] OR "brain"[Title/Abstract] OR "cognition"[Title/Abstract]) AND 2015:2025[dp]',
            '("awe"[Title/Abstract] AND "nature"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "psychology"[Title/Abstract])) AND 2015:2025[dp]',
        ],
    },
    "phase-16-transcendence": {
        "phase": 16, "name": "Visionary Cosmologies",
        "concept": "Self-transcendence, mystical experience, numinous, cosmic consciousness.",
        "bridge_rationale": "Visionary cosmologies — self-transcendence, mystical experience, numinous, awe, cosmic consciousness.",
        "queries": [
            '("self-transcendence"[Title/Abstract] OR "transcendence"[Title/Abstract] OR "transcendent"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "neuroimaging"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("mystical experience"[Title/Abstract] OR "mystical"[Title/Abstract] OR "numinous"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "psychedelic"[Title/Abstract] OR "meditation"[Title/Abstract]) AND 2010:2025[dp]',
            '("awe"[Title/Abstract] AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "fMRI"[Title/Abstract] OR "neuroimaging"[Title/Abstract])) AND 2015:2025[dp]',
            '("cosmic consciousness"[Title/Abstract] OR "oceanic"[Title/Abstract] OR "unity"[Title/Abstract] AND "consciousness"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
    "phase-17-social": {
        "phase": 17, "name": "Social Incarnation",
        "concept": "Intersubjectivity — embodied empathy, social predictive processing, second-person neuroscience.",
        "bridge_rationale": "Social Incarnation — intersubjectivity, embodied empathy, social predictive processing, second-person neuroscience.",
        "queries": [
            '("second-person"[Title/Abstract] OR "intersubjectivity"[Title/Abstract] OR "embodied empathy"[Title/Abstract] OR "shared intentionality"[Title/Abstract]) AND ("neural"[Title/Abstract] OR "brain"[Title/Abstract] OR "fMRI"[Title/Abstract]) AND 2010:2025[dp]',
            '("social cognition"[Title/Abstract] AND "predictive processing"[Title/Abstract] OR "predictive coding"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract]) AND 2015:2025[dp]',
            '("empathy"[Title/Abstract] OR "empathic"[Title/Abstract] AND "embodied"[Title/Abstract] OR "interoception"[Title/Abstract]) AND ("brain"[Title/Abstract] OR "neural"[Title/Abstract] OR "insula"[Title/Abstract]) AND 2010:2025[dp]',
            '("mirror neuron"[Title/Abstract] AND "empathy"[Title/Abstract] OR "action understanding"[Title/Abstract]) AND ("premotor"[Title/Abstract] OR "parietal"[Title/Abstract]) AND 2010:2025[dp]',
        ],
    },
}

# ─── Scoring ───
def score_paper(title, abstract, phase_key):
    """Score bridge relevance for a specific phase. Returns (numeric_score, label)."""
    text = f"{title} {abstract}".lower()
    
    # Immediate noise rejections
    noise = ["clinical trial", "pharmacological", "treatment outcome", "case report",
             "rat ", " mice ", "murine", "animal model", "surgery", "drug therapy",
             "randomized controlled", "phase 2", "phase 3"]
    for n in noise:
        if n in text:
            return 0, f"Noise: '{n}'"
    
    # Phase-specific bridge keywords with weights
    phase_terms = {
        "phase-1-metacognition": [
            ("metacognition", 1.5), ("metacognitive", 1.5), ("self-awareness", 1.2),
            ("self-monitoring", 1.2), ("meta-awareness", 1.5), ("prefrontal", 0.5),
            ("anterior cingulate", 0.5), ("error awareness", 1.2), ("confidence", 0.5),
            ("insight", 0.4), ("self-reflection", 0.8), ("introspection", 0.8),
        ],
        "phase-2-body-illusion": [
            ("rubber hand", 1.5), ("body ownership", 1.5), ("multisensory ownership", 1.5),
            ("body representation", 1.2), ("body schema", 1.2), ("peripersonal", 1.0),
            ("full body illusion", 1.5), ("out-of-body", 1.2), ("virtual body", 0.8),
            ("ownership", 0.6), ("embodiment illusion", 1.2), ("self-other", 0.8),
        ],
        "phase-3-4e-cognition": [
            ("embodied cognition", 1.5), ("grounded cognition", 1.2), ("enactive", 1.5),
            ("extended mind", 1.5), ("situated cognition", 1.2), ("sensorimotor", 0.8),
            ("4e cognition", 1.5), ("predictive processing", 0.6), ("active inference", 0.6),
            ("computationalism", 1.0),
        ],
        "phase-4-agency": [
            ("sense of agency", 1.5), ("intentional binding", 1.5), ("voluntary action", 1.2),
            ("volition", 1.0), ("free will", 1.0), ("agency attribution", 1.5),
            ("self-agency", 1.2), ("corollary discharge", 1.2), ("efference copy", 1.0),
            ("self-generated", 0.6), ("authorship", 0.5),
        ],
        "phase-5-mechanicality": [
            ("habit", 1.2), ("habitual", 1.2), ("automaticity", 1.5), ("chunking", 1.0),
            ("goal-directed", 0.6), ("action monitoring", 1.0), ("conflict monitoring", 0.8),
            ("error-related negativity", 1.0), ("compulsive", 0.8), ("striatum", 0.8),
            ("cortico-striatal", 1.0), ("automatic", 0.4),
        ],
        "phase-6-dependent-arising": [
            ("free energy principle", 1.5), ("active inference", 1.5), ("predictive coding", 1.2),
            ("predictive processing", 1.2), ("bayesian brain", 1.5), ("hierarchical predictive", 1.0),
            ("prediction error", 0.8), ("causal inference", 0.8), ("markov blanket", 1.5),
            ("free energy", 0.8), ("bayesian", 0.5),
        ],
        "phase-7-emptiness": [
            ("ego dissolution", 1.5), ("self-loss", 1.5), ("self-transcendence", 1.2),
            ("default mode", 0.8), ("nondual", 1.5), ("non-dual", 1.5),
            ("depersonalization", 0.8), ("derealization", 0.6), ("self-boundary", 1.0),
            ("self-referential", 0.5), ("meditation", 0.5), ("psychedelic", 0.5),
        ],
        "phase-8-spontaneous": [
            ("spontaneous thought", 1.5), ("mind-wandering", 1.5), ("daydreaming", 1.2),
            ("creative cognition", 1.0), ("creative insight", 1.0), ("divergent thinking", 0.8),
            ("involuntary thought", 1.2), ("incubation", 1.0), ("aha moment", 1.2),
            ("insight", 0.5), ("resting state", 0.4),
        ],
        "phase-9-language": [
            ("mantra", 1.5), ("mantra meditation", 1.8), ("inner speech", 1.5),
            ("inner voice", 1.2), ("self-talk", 1.0), ("private speech", 0.8),
            ("focused attention", 0.8), ("verbal repetition", 1.0), ("prayer", 0.8),
            ("transcendental meditation", 1.2),
        ],
        "phase-10-imaginal": [
            ("mental imagery", 1.5), ("visual imagery", 1.2), ("aphantasia", 1.8),
            ("hyperphantasia", 1.5), ("imagery deficit", 1.0), ("pareidolia", 1.5),
            ("reality monitoring", 1.0), ("source monitoring", 0.8), ("imagination", 0.6),
            ("mental simulation", 0.8), ("early visual", 0.5),
        ],
        "phase-11-body-energy": [
            ("interoception", 1.5), ("interoceptive", 1.5), ("cardiac interoception", 1.5),
            ("heartbeat evoked", 1.5), ("heartbeat detection", 1.2), ("allostasis", 1.2),
            ("insula", 0.5), ("visceral", 0.8), ("vagal", 0.8), ("breathing", 0.5),
            ("respiratory", 0.5), ("vagus", 0.6),
        ],
        "phase-12-ritual": [
            ("hyperscanning", 1.8), ("inter-brain", 1.5), ("brain-to-brain", 1.5),
            ("interpersonal synchronization", 1.5), ("neural synchrony", 1.2),
            ("joint action", 1.0), ("joint attention", 0.8), ("rhythmic entrainment", 1.0),
            ("brain entrainment", 1.0), ("coherence", 0.4), ("collective", 0.5),
        ],
        "phase-13-daimon": [
            ("auditory verbal hallucination", 1.5), ("voice hearing", 1.5),
            ("hallucination proneness", 1.2), ("inner speech", 0.8),
            ("corollary discharge", 1.2), ("source monitoring", 0.8),
            ("agency detection", 1.0), ("self-monitoring", 0.5), ("hallucinations", 0.5),
            ("psychosis", 0.4),
        ],
        "phase-14-psychedelic": [
            ("psilocybin", 1.2), ("psychedelic", 1.2), ("dmt", 0.8),
            ("ego dissolution", 1.5), ("altered states", 1.0),
            ("entropic brain", 1.5), ("brain entropy", 1.0), ("lsd", 0.8),
            ("ayahuasca", 1.0), ("default mode", 0.5),
        ],
        "phase-15-ecology": [
            ("nature connectedness", 1.5), ("nature exposure", 1.2),
            ("biophilia", 1.5), ("biophilic", 1.2), ("attention restoration", 1.0),
            ("green space", 0.8), ("nature", 0.3), ("awe", 0.8),
            ("environmental neuroscience", 1.5),
        ],
        "phase-16-transcendence": [
            ("self-transcendence", 1.5), ("transcendence", 1.2), ("mystical experience", 1.5),
            ("mystical", 0.8), ("numinous", 1.5), ("awe", 0.8),
            ("cosmic consciousness", 1.8), ("oceanic", 1.0), ("unity consciousness", 1.2),
            ("transcendent", 0.8),
        ],
        "phase-17-social": [
            ("second-person", 1.5), ("intersubjectivity", 1.5), ("embodied empathy", 1.5),
            ("shared intentionality", 1.2), ("predictive processing", 0.5),
            ("social cognition", 0.6), ("empathy", 0.5), ("mirror neuron", 0.8),
            ("interoception", 0.5), ("social brain", 0.4),
        ],
    }
    
    score = 0
    terms = phase_terms.get(phase_key, [])
    for term, weight in terms:
        if term in text:
            score += weight
    
    # Cross-phase boost for neural/mechanistic terms
    cross_terms = [("neural", 0.3), ("brain", 0.2), ("fMRI", 0.4), ("neuroimaging", 0.5),
                   ("cortex", 0.3), ("EEG", 0.4), ("mechanism", 0.5)]
    for term, weight in cross_terms:
        if term in text:
            score += weight
    
    # Reject very low scores
    if score < 1.5:
        return 0, f"Low signal (score={score:.1f})"
    
    # Quality labels
    if score >= 3.5:
        return 3, f"Excellent (score={score:.1f})"
    elif score >= 2.5:
        return 2, f"Good (score={score:.1f})"
    else:
        return 1, f"Marginal (score={score:.1f})"


# ─── PubMed API ───
def api_call(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAcquisition/2.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  [WARN] Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [ERROR] HTTP {e.code}: {url[:120]}...")
                if attempt < max_retries - 1: time.sleep(3)
        except Exception as e:
            print(f"  [ERROR] API error: {e}")
            if attempt < max_retries - 1: time.sleep(3)
    return None

def search_pubmed(query, retmax=30):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{ESEARCH}?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch_esummary(pmids):
    """Get summaries (title, journal, year, DOI, PMC ID) via esummary."""
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{ESUMMARY}?{params}")
    if not data: return {}
    try:
        result = {}
        parsed = json.loads(data)
        for uid, doc in parsed.get("result", {}).items():
            if uid == "uids": continue
            doi = ""
            pmc = ""
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "doi": doi = aid.get("value", "")
                if aid.get("idtype") == "pmc": pmc = aid.get("value", "")
            result[uid] = {
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "pubdate": doc.get("pubdate", ""),
                "doi": doi,
                "pmc": pmc,
                "authors": [a.get("name", "") for a in doc.get("authors", [])[:5]],
            }
        return result
    except: return {}

def fetch_abstracts(pmids):
    """Fetch full abstracts via efetch XML."""
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"{EFETCH}?{params}")
    if not data: return {}
    
    articles = {}
    try:
        root = ET.fromstring(data)
        for article in root.findall(".//PubmedArticle"):
            pmid_el = article.find(".//PMID")
            if pmid_el is None or not pmid_el.text: continue
            pmid = pmid_el.text.strip()
            
            # Title
            te = article.find(".//ArticleTitle")
            title = "".join(te.itertext()).strip() if te is not None else ""
            
            # Abstract
            abs_parts = []
            for ae in article.findall(".//AbstractText"):
                lbl = ae.get("Label", "")
                txt = "".join(ae.itertext()).strip()
                abs_parts.append(f"{lbl}: {txt}" if lbl else txt)
            abstract = " ".join(abs_parts)
            
            # Year
            ye = article.find(".//PubDate/Year")
            if ye is None: ye = article.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            
            articles[pmid] = {"title": title, "abstract": abstract, "year": year}
    except ET.ParseError as e:
        print(f"  [ERROR] XML parse: {e}")
    return articles

def download_pdf(pmc_id, title, doi):
    """Download PDF via OA Service API + HTTPS deprecated path."""
    if not pmc_id: return None
    
    # Clean PMC ID
    pmc_clean = pmc_id.replace("PMC", "")
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', title)[:50].strip('_')
    pdf_basename = f"t2-pubmed-pmc{pmc_clean}_{slug}.pdf"
    pdf_path = f"{LIBRARY_FRONTIER}/{pdf_basename}"
    
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
        return pdf_basename
    
    # Query OA Service
    time.sleep(DELAY)
    oa_url = f"{OA_SVC}?id=PMC{pmc_clean}"
    data = api_call(oa_url)
    if not data: return None
    
    try:
        root = ET.fromstring(data)
        error_el = root.find(".//error")
        if error_el is not None:
            print(f"  OA: No OA package for PMC{pmc_clean}")
            return None
        
        record = root.find(".//record")
        if record is None: return None
        link = record.find('link[@format="tgz"]')
        if link is None: return None
        ftp_href = link.get("href")
        if not ftp_href: return None
    except Exception as e:
        print(f"  OA parse error: {e}")
        return None
    
    # Convert FTP → HTTPS + deprecated path
    https_url = ftp_href.replace("ftp://", "https://")
    https_url = https_url.replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/")
    
    local_tgz = f"/tmp/pmc_{pmc_clean}.tar.gz"
    
    # Download via curl
    import subprocess
    try:
        subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "120",
                       "-o", local_tgz, https_url], check=True, timeout=130)
    except Exception as e:
        print(f"  curl download failed: {e}")
        return None
    
    if not os.path.exists(local_tgz) or os.path.getsize(local_tgz) < 1000:
        print(f"  Downloaded file too small or missing")
        return None
    
    # Extract PDF
    try:
        with tarfile.open(local_tgz, "r:gz") as tar:
            # Find main PDF (prefer Article_*, avoid MOESM/Suppl)
            pdfs = []
            for m in tar.getmembers():
                if m.name.endswith(".pdf"):
                    if "Article_" in m.name and "MOESM" not in m.name and "Suppl" not in m.name:
                        pdfs.insert(0, m)
                    elif "MOESM" not in m.name and "Suppl" not in m.name:
                        pdfs.append(m)
            if not pdfs:
                pdfs = [m for m in tar.getmembers() if m.name.endswith(".pdf")]
            if not pdfs:
                print(f"  No PDF in OA package")
                os.remove(local_tgz)
                return None
            
            os.makedirs(LIBRARY_FRONTIER, exist_ok=True)
            with tar.extractfile(pdfs[0]) as src, open(pdf_path, "wb") as dst:
                dst.write(src.read())
        
        os.remove(local_tgz)
        size = os.path.getsize(pdf_path)
        if size > 5000:
            print(f"  Downloaded PDF: {pdf_basename} ({size} bytes)")
            return pdf_basename
        else:
            os.remove(pdf_path)
            return None
    except Exception as e:
        print(f"  Extract error: {e}")
        if os.path.exists(local_tgz): os.remove(local_tgz)
        return None


# ─── Work/essay creation ───
def create_slug(title):
    """Create URL-friendly slug from title."""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    words = slug.split('-')
    return '-'.join(words[:15])  # limit length

def make_work_json(article, summary, phase_info, score_label, pdf_path=None):
    """Create a properly structured work JSON matching existing format."""
    pmid = article["pmid"]
    title = article["title"]
    doi = summary.get("doi", article.get("doi", ""))
    year = article.get("year", summary.get("pubdate", "")[:4])
    journal = summary.get("source", article.get("journal", ""))
    authors = summary.get("authors", article.get("authors", []))
    abstract = article.get("abstract", "")[:500]
    
    slug = create_slug(title)
    work_id = f"work:t2-pubmed-{slug}"
    
    # Extract year from pubdate if needed
    if not year or len(year) != 4:
        pd = summary.get("pubdate", "")
        m = re.search(r'\b(19|20)\d{2}\b', pd)
        if m: year = m.group(0)
    
    phase = phase_info["phase"]
    phase_name = phase_info["name"]
    
    data = {
        "work_id": work_id,
        "schema_version": 2,
        "title": title,
        "publication": {
            "year": int(year) if year and year.isdigit() else 0,
            "type": "article",
            "source": "PubMed/MEDLINE",
            "language": "en",
            "journal": journal
        },
        "identifiers": {
            "pmid": pmid,
            "doi": doi
        },
        "topics": [
            f"phase-{phase}-{phase_name.lower().replace(' ', '-')}",
            "frontier_science",
            "bridge_paper"
        ],
        "tradition": ["contemporary_science"],
        "tier": 2,
        "assets": {
            "pdf_path": pdf_path,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": abstract
        },
        "provenance": {
            "access_status": "open",
            "oa_status": "green",
            "source": "pubmed_t2_search",
            "retrieved_at": time.strftime("%Y-%m-%d")
        },
        "phase_mapping": {
            "phase": phase,
            "phase_name": phase_name,
            "bridge_rationale": phase_info["bridge_rationale"]
        }
    }
    return data, work_id


def make_essay_json(work_data, work_id, slug, phase_info, score_label):
    """Create Type B essay JSON."""
    title = work_data["title"]
    authors_list = work_data.get("publication", {}).get("journal", "")
    year = work_data.get("publication", {}).get("year", "")
    doi = work_data.get("identifiers", {}).get("doi", "")
    pmid = work_data.get("identifiers", {}).get("pmid", "")
    abstract = work_data.get("assets", {}).get("abstract", "")[:500]
    phase = phase_info["phase"]
    phase_name = phase_info["name"]
    
    essay_id = f"essay-{work_id.replace(':', '-')}"
    
    body = [
        {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{phase_name}** with mechanistic science from PubMed/MEDLINE."},
        {"kind": "ai", "text": f"**Bridge rationale:** {phase_info['bridge_rationale']}"},
        {"kind": "ai", "text": f"**Phase context:** {phase_info['concept']}"},
        {"kind": "summary", "text": f"**{title}** — {authors_list} ({year}). DOI: {doi}. PMID: {pmid}. {abstract}"},
    ]
    
    return {
        "id": essay_id,
        "type": "type-b-essay",
        "title": f"Bridge Essay: {title}",
        "source_work": work_id,
        "phase": f"phase-{phase}",
        "phase_name": phase_name,
        "concept": phase_info["concept"],
        "tags": ["frontier-science", "bridge-paper", f"phase-{phase}"],
        "body": body,
        "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase} ({phase_name}). Evaluation: {score_label}"
    }


def log_acquisition(phase_key, count, details):
    """Append to acquisition log."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## Session: {ts}\n**Phase:** {PHASES[phase_key]['name']}\n**New papers:** {count}\n\n"
    for d in details:
        entry += f"- {d}\n"
    try:
        os.makedirs(os.path.dirname(ACQUISITION_LOG), exist_ok=True)
        with open(ACQUISITION_LOG, "a") as f:
            f.write(entry)
    except: pass


# ─── Main ───
def acquire_phase(phase_key, target=50):
    """Search PubMed for a phase, evaluate, create work/essay JSONs, download PDFs."""
    info = PHASES[phase_key]
    phase = info["phase"]
    name = info["name"]
    
    # Count existing papers for this phase (only by phase_mapping.phase)
    existing = set()
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            pm = d.get("phase_mapping", {})
            if pm and pm.get("phase") == phase:
                existing.add(w)
        except: pass
    
    need = max(0, target - len(existing))
    print(f"\n{'='*60}")
    print(f"Phase {phase}: {name}")
    print(f"Existing: {len(existing)}, Need: {need}")
    print(f"{'='*60}")
    
    if need <= 0:
        print(f"  Already at target ({target})")
        return 0
    
    candidates = []
    seen_titles = set()
    
    # Load already-seen titles from existing works
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            seen_titles.add(d.get("title", "").lower().strip())
        except: pass
    
    for qi, query in enumerate(info["queries"]):
        if len(candidates) >= need * 2:  # Get 2x candidates for selection
            break
        if len(candidates) >= 50:  # Hard cap
            break
            
        print(f"\n  Query {qi+1}/{len(info['queries'])}...")
        pmids = search_pubmed(query, retmax=25)
        if not pmids:
            print(f"    No results")
            continue
        print(f"    Found {len(pmids)} PMIDs")
        
        # Get summaries for DOIs, PMC IDs, journals
        summaries = fetch_esummary(pmids)
        
        # Get abstracts
        abstracts = fetch_abstracts(pmids)
        
        for pmid in pmids:
            if len(candidates) >= need * 2:
                break
            
            summary = summaries.get(pmid, {})
            abstract_data = abstracts.get(pmid, {})
            title = summary.get("title", abstract_data.get("title", ""))
            if not title:
                continue
            
            title_lower = title.lower().strip()
            if title_lower in seen_titles:
                continue
            
            abstract = abstract_data.get("abstract", "")
            year = abstract_data.get("year", summary.get("pubdate", "")[:4])
            journal = summary.get("source", "")
            
            # Score
            score_val, score_label = score_paper(title, abstract, phase_key)
            if score_val < 2:
                continue  # Only good+ papers
            
            # Found a quality candidate
            seen_titles.add(title_lower)
            
            article = {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "year": year,
                "journal": journal,
                "authors": summary.get("authors", []),
                "doi": summary.get("doi", ""),
            }
            
            candidates.append((score_val, article, summary, score_label))
            print(f"    + [{score_label}] {title[:70]}...")
    
    if not candidates:
        print(f"  No candidates found for Phase {phase}")
        return 0
    
    # Sort by score descending, take top need
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[:min(need, len(candidates))]
    
    print(f"\n  Selected {len(selected)} papers for Phase {phase}")
    details = []
    created = 0
    
    for score_val, article, summary, score_label in selected:
        pmid = article["pmid"]
        title = article["title"]
        
        # PMC ID
        pmc_id = summary.get("pmc", "")
        
        # Download PDF if PMC ID available
        pdf_path = None
        if pmc_id:
            pdf_path = download_pdf(pmc_id, title, article.get("doi", ""))
        
        # Create work JSON
        work_data, work_id = make_work_json(article, summary, info, score_label, pdf_path)
        slug = create_slug(title)
        work_file = f"{CONTENT_WORKS}/t2-pubmed-{slug}.json"
        
        with open(work_file, "w") as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        # Create essay JSON
        essay_data = make_essay_json(work_data, work_id, slug, info, score_label)
        essay_file = f"{CONTENT_ESSAYS}/bridge-pubmed-{slug}.json"
        
        with open(essay_file, "w") as f:
            json.dump(essay_data, f, indent=2, ensure_ascii=False)
        
        created += 1
        detail = f"  ✓ {title[:60]}... ({article.get('journal','?')} {article.get('year','?')}) — {score_label}"
        if pdf_path: detail += " [PDF]"
        details.append(detail)
        print(detail)
    
    # Log
    log_acquisition(phase_key, created, details)
    print(f"\n  Phase {phase} complete: {created} new papers (total: {len(existing) + created})")
    return created


if __name__ == "__main__":
    os.makedirs(CONTENT_WORKS, exist_ok=True)
    os.makedirs(CONTENT_ESSAYS, exist_ok=True)
    os.makedirs(LIBRARY_FRONTIER, exist_ok=True)
    os.makedirs(os.path.dirname(ACQUISITION_LOG), exist_ok=True)
    
    # Import tarfile for PDF extraction
    import tarfile
    
    # Determine which phases to process
    # Priority: most under-covered first (based on pre-run analysis)
    if len(sys.argv) > 1:
        phases_to_run = [a for a in sys.argv[1:] if a in PHASES]
    else:
        # Default: run all phases (target 50 each)
        phases_to_run = list(PHASES.keys())
    
    total = 0
    for pk in phases_to_run:
        added = acquire_phase(pk, target=50)
        total += added
        # Summary after each phase
        print(f"\n  Running total: {total} new papers so far")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"ACQUISITION COMPLETE")
    print(f"{'='*60}")
    print(f"Total new papers: {total}")
    
    # Report phase counts
    print(f"\nUpdated phase counts:")
    phases = {}
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            pm = d.get("phase_mapping", {})
            p = pm.get("phase", 0) if pm else 0
            pn = pm.get("phase_name", "unassigned") if pm else "unassigned"
            key = (p, pn)
            phases[key] = phases.get(key, 0) + 1
        except: pass
    
    for (p, n), c in sorted(phases.items()):
        print(f"  Phase {p:2d} ({n:30s}): {c:3d}")
