#!/usr/bin/env python3
"""Acquire bridge papers for alternative 17-phase framework.

Targets zero-paper phases: Birth/Body, Heat/Fire, Form/Meditation, Imaginal,
Knowledge/Gnosis, Nondual/Unity, Ultimate/Emptiness.
Also fills partial phases: Water/Pleasure, Breath/Soul, Dependent-arising,
Formless/Absorption, Wind/Pride, Liberation/Enlightenment, Language/Mantra.
"""
import glob, json, os, re, sys, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

BASE = "/root/projects/blog"
WORKS_DIR = f"{BASE}/content/works"
ESSAYS_DIR = f"{BASE}/content/glossary/essays"
LIBRARY = f"{BASE}/library/frontier"
EMAIL = "hermes@research.local"
DELAY = 1.0
MAX_PER_QUERY = 25

# Alternative 17-phase framework definitions
PHASES = {
    1: {"name": "Birth/Body",
        "queries": [
            '(fetal consciousness[Title/Abstract] OR neonatal consciousness[Title/Abstract] OR prenatal[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR consciousness[Title/Abstract]) AND 2005:2025[dp]',
            '(body ownership[Title/Abstract] OR bodily self[Title/Abstract] OR minimal self[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR fMRI[Title/Abstract]) AND 2010:2025[dp]',
            '(self-consciousness[Title/Abstract] OR first-person perspective[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2010:2025[dp]',
            '(embodied cognition[Title/Abstract] OR body representation[Title/Abstract] OR perinatal[Title/Abstract]) AND (self[Title/Abstract] OR consciousness[Title/Abstract] OR brain[Title/Abstract]) AND 2010:2025[dp]',
            '(multisensory integration[Title/Abstract] AND (body[Title/Abstract] OR self[Title/Abstract] OR ownership[Title/Abstract])) AND (neural[Title/Abstract] OR brain[Title/Abstract] OR cortex[Title/Abstract]) AND 2010:2025[dp]',
            '(out-of-body[Title/Abstract] OR full-body illusion[Title/Abstract] OR rubber hand illusion[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR multisensory[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": {"fetal consciousness": 6, "neonatal consciousness": 6, "prenatal": 3,
                  "body ownership": 5, "bodily self": 5, "minimal self": 5,
                  "self-consciousness": 4, "first-person": 4, "body representation": 4,
                  "embodied self": 5, "self-location": 5, "out-of-body": 4,
                  "full-body illusion": 5, "rubber hand illusion": 4, "perinatal": 3,
                  "multisensory integration": 3, "body awareness": 3, "proprioception": 2,
                  "interoception": 2, "embodied cognition": 2, "pregnancy": 1, "neonatal": 1}},
    3: {"name": "Heat/Fire",
        "queries": [
            '(kundalini[Title/Abstract] OR subtle energy[Title/Abstract] OR chakra[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract]) AND 2000:2025[dp]',
            '(tummo[Title/Abstract] OR g-tummo[Title/Abstract] OR inner heat[Title/Abstract]) AND (meditation[Title/Abstract] OR yogic[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '(body temperature[Title/Abstract] AND meditation[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR autonomic[Title/Abstract] OR thermoregulation[Title/Abstract])) AND 2000:2025[dp]',
            '(yogic[Title/Abstract] OR tantric[Title/Abstract]) AND (thermoregulation[Title/Abstract] OR metabolism[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '(psychosomatic[Title/Abstract] AND (energy[Title/Abstract] OR heat[Title/Abstract] OR body[Title/Abstract] OR mind-body[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract])) AND 2000:2025[dp]',
            '(thermogenesis[Title/Abstract] OR brown fat[Title/Abstract] OR heat generation[Title/Abstract]) AND (meditation[Title/Abstract] OR yoga[Title/Abstract] OR breathing[Title/Abstract] OR autonomic[Title/Abstract]) AND 2000:2025[dp]',
        ],
        "terms": {"kundalini": 6, "subtle energy": 5, "chakra": 5, "tummo": 6,
                  "g-tummo": 6, "inner heat": 5, "yogic": 3, "tantric": 4,
                  "thermoregulation": 3, "body temperature": 3, "heat generating": 4,
                  "psychosomatic": 3, "mind-body": 3, "thermogenesis": 2,
                  "autonomic": 2, "sympathetic": 2, "meditation": 2, "yoga": 2,
                  "energy metabolism": 2, "breathing": 1}},
    7: {"name": "Form/Meditation",
        "queries": [
            '(focused attention[Title/Abstract] OR concentrative meditation[Title/Abstract]) AND (brain[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(sustained attention[Title/Abstract] AND meditation[Title/Abstract] AND (neural[Title/Abstract] OR brain[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract])) AND 2010:2025[dp]',
            '(meta-awareness[Title/Abstract] OR metacognitive awareness[Title/Abstract]) AND (meditation[Title/Abstract] OR mindfulness[Title/Abstract]) AND 2010:2025[dp]',
            '(attentional control[Title/Abstract] AND meditation[Title/Abstract] AND (anterior cingulate[Title/Abstract] OR prefrontal[Title/Abstract] OR parietal[Title/Abstract])) AND 2010:2025[dp]',
            '(body scan[Title/Abstract] OR breath meditation[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract] OR fMRI[Title/Abstract]) AND 2010:2025[dp]',
            '(executive attention[Title/Abstract] OR attentional network[Title/Abstract]) AND (meditation[Title/Abstract] OR mindfulness[Title/Abstract]) AND (neural[Title/Abstract] OR brain[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"focused attention": 5, "concentrative": 5, "sustained attention": 4,
                  "meta-awareness": 5, "metacognitive awareness": 5, "body scan": 4,
                  "breath meditation": 5, "attentional control": 4, "executive attention": 3,
                  "anterior cingulate": 3, "mindfulness": 2, "meditation": 2,
                  "attention network": 3, "walking meditation": 3, "reappraisal": 2}},
    10: {"name": "Imaginal",
         "queries": [
            '(mental imagery[Title/Abstract] OR visual imagery[Title/Abstract]) AND (perception[Title/Abstract] OR sensory[Title/Abstract]) AND (neural overlap[Title/Abstract] OR shared representation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(aphantasia[Title/Abstract] OR hyperphantasia[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR visual cortex[Title/Abstract] OR fMRI[Title/Abstract]) AND 2015:2025[dp]',
            '(imagination[Title/Abstract] AND perception[Title/Abstract] AND (neural[Title/Abstract] OR brain[Title/Abstract] OR fMRI[Title/Abstract] OR visual cortex[Title/Abstract])) AND 2010:2025[dp]',
            '(reality monitoring[Title/Abstract] OR source monitoring[Title/Abstract] OR reality discrimination[Title/Abstract]) AND (prefrontal[Title/Abstract] OR frontopolar[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(mental simulation[Title/Abstract] OR mental practice[Title/Abstract]) AND (brain[Title/Abstract] OR motor cortex[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2010:2025[dp]',
            '(pareidolia[Title/Abstract] OR illusory pattern[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR visual[Title/Abstract] OR perception[Title/Abstract]) AND 2010:2025[dp]',
         ],
         "terms": {"mental imagery": 5, "visual imagery": 4, "imagery": 3,
                   "aphantasia": 6, "hyperphantasia": 6, "imagination": 3,
                   "neural overlap": 5, "shared representation": 4, "reality monitoring": 5,
                   "source monitoring": 4, "mental simulation": 4, "pareidolia": 5,
                   "visual cortex": 3, "mental practice": 3, "imagery perception": 4,
                   "imagery deficit": 4, "frontopolar": 2, "prefrontal": 2}},
    14: {"name": "Knowledge/Gnosis",
         "queries": [
            '(insight[Title/Abstract] AND creativity[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract])) AND 2010:2025[dp] AND loattrfree full text[sb]',
            '(aha moment[Title/Abstract] OR insight problem[Title/Abstract] OR creative insight[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '(semantic cognition[Title/Abstract] OR conceptual knowledge[Title/Abstract] OR abstract knowledge[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR anterior temporal[Title/Abstract]) AND 2010:2025[dp]',
            '(metacognition[Title/Abstract] OR noetic[Title/Abstract] OR intuitive knowledge[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR prefrontal[Title/Abstract] OR cognition[Title/Abstract]) AND 2010:2025[dp]',
            '(epistemic[Title/Abstract] OR "sense of knowing"[Title/Abstract] OR "felt sense"[Title/Abstract] OR "knowing"[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cognition[Title/Abstract]) AND 2005:2025[dp]',
            '(belief updating[Title/Abstract] OR prediction error[Title/Abstract] AND insight[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR prefrontal[Title/Abstract]) AND 2005:2025[dp]',
         ],
         "terms": {"insight": 4, "aha moment": 6, "insight problem": 5, "creative insight": 5,
                   "semantic cognition": 5, "conceptual knowledge": 4, "abstract knowledge": 4,
                   "metacognition": 3, "noetic": 5, "gnostic": 5, "intuitive knowledge": 5,
                   "felt sense": 5, "knowing": 3, "belief updating": 4, "epistemic": 4,
                   "prediction error": 3, "anterior temporal": 3, "default mode": 2,
                   "creativity": 2, "prefrontal": 2, "knowledge": 2}},
    16: {"name": "Nondual/Unity",
         "queries": [
            '(nondual[Title/Abstract] OR non-dual[Title/Abstract] OR nondual awareness[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract] OR consciousness[Title/Abstract]) AND 2005:2025[dp]',
            '(oneness[Title/Abstract] OR unity experience[Title/Abstract] OR sense of unity[Title/Abstract] OR oceanic[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(pure awareness[Title/Abstract] OR pure consciousness[Title/Abstract] OR awareness itself[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR consciousness[Title/Abstract]) AND 2005:2025[dp]',
            '(minimal phenomenal experience[Title/Abstract] OR minimal self[Title/Abstract] OR basic self[Title/Abstract]) AND (consciousness[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(self-other[Title/Abstract] AND boundary dissolution[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract])) AND 2005:2025[dp]',
            '(ego dissolution[Title/Abstract] AND transcendence[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR default mode[Title/Abstract])) AND 2010:2025[dp]',
         ],
         "terms": {"nondual": 6, "non-dual": 6, "nondual awareness": 6,
                   "oneness": 5, "unity experience": 5, "sense of unity": 5,
                   "oceanic": 4, "pure awareness": 6, "pure consciousness": 6,
                   "awareness itself": 6, "minimal phenomenal experience": 6,
                   "minimal self": 4, "basic self": 4, "self-other": 3,
                   "boundary dissolution": 5, "ego dissolution": 4,
                   "default mode": 2, "meditation": 2, "psychedelic": 2,
                   "transcend": 2, "self-transcendence": 2}},
    17: {"name": "Ultimate/Emptiness",
         "queries": [
            '(open monitoring[Title/Abstract] OR open awareness[Title/Abstract] OR choiceless awareness[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(depersonalization[Title/Abstract] OR derealization[Title/Abstract]) AND (self[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR default mode[Title/Abstract]) AND 2010:2025[dp]',
            '(self-awareness[Title/Abstract] OR meta-awareness[Title/Abstract]) AND (meditation[Title/Abstract] OR mindfulness[Title/Abstract] OR emptiness[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR default mode[Title/Abstract]) AND 2010:2025[dp]',
            '(witness consciousness[Title/Abstract] OR observing self[Title/Abstract] OR background awareness[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '(field consciousness[Title/Abstract] OR groundlessness[Title/Abstract] OR nothingness[Title/Abstract]) AND (experience[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2000:2025[dp]',
            '(ego dissolution[Title/Abstract] OR self-loss[Title/Abstract] OR self-transcendence[Title/Abstract]) AND (DMN[Title/Abstract] OR "default mode"[Title/Abstract] OR brain[Title/Abstract]) AND 2010:2025[dp]',
         ],
         "terms": {"open monitoring": 5, "open awareness": 5, "choiceless awareness": 6,
                   "depersonalization": 4, "derealization": 4, "witness consciousness": 6,
                   "observing self": 5, "background awareness": 5, "field consciousness": 5,
                   "groundlessness": 6, "nothingness": 5, "emptiness": 4, "sunyata": 6,
                   "ego dissolution": 4, "self-loss": 4, "self-transcendence": 3,
                   "default mode": 2, "DMN": 2, "dissociation": 3,
                   "meta-awareness": 3, "meditation": 2, "mindfulness": 2}},
}

# Partial phases that need filling
PARTIAL_PHASES = {
    2: {"name": "Breath/Soul", "have": 15, "want": 50,
        "queries": [
            '(pranayama[Title/Abstract] OR breathwork[Title/Abstract] OR slow breathing[Title/Abstract] OR nasal breathing[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR autonomic[Title/Abstract] OR HRV[Title/Abstract] OR vagal[Title/Abstract]) AND 2005:2025[dp]',
            '(respiration[Title/Abstract] OR respiratory[Title/Abstract] OR cardiorespiratory[Title/Abstract]) AND (meditation[Title/Abstract] OR yoga[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract]) AND 2005:2025[dp]',
            '(breath[Title/Abstract] AND brain[Title/Abstract] AND (neural[Title/Abstract] OR oscillation[Title/Abstract] OR entrainment[Title/Abstract] OR synchronization[Title/Abstract])) AND 2010:2025[dp]',
            '(vagal tone[Title/Abstract] OR heart rate variability[Title/Abstract] AND respiration[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract]) AND 2010:2025[dp]',
            '(yoga breathing[Title/Abstract] OR nostril breathing[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract] OR autonomic[Title/Abstract]) AND 2000:2025[dp]',
        ],
        "terms": {"pranayama": 5, "breathwork": 4, "slow breathing": 4, "nasal breathing": 3,
                  "breathing": 2, "respiration": 2, "respiratory": 2, "breath": 2,
                  "vagal tone": 4, "heart rate variability": 3, "HRV": 3,
                  "cardiorespiratory": 4, "breath-brain": 5, "yoga breathing": 4,
                  "nostril breathing": 3, "autonomic": 2, "meditation": 1}},
    4: {"name": "Wind/Pride", "have": 15, "want": 50,
        "queries": [
            '(narcissism[Title/Abstract] OR narcissistic[Title/Abstract] OR grandiose[Title/Abstract] OR hubris[Title/Abstract] OR pride[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR prefrontal[Title/Abstract]) AND 2005:2025[dp]',
            '(self-enhancement[Title/Abstract] OR self-aggrandizement[Title/Abstract] OR self-esteem[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(social dominance[Title/Abstract] OR social hierarchy[Title/Abstract] OR social status[Title/Abstract] OR social rank[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR prefrontal[Title/Abstract] OR striatum[Title/Abstract]) AND 2010:2025[dp]',
            '(ego dissolution[Title/Abstract] AND (narcissism[Title/Abstract] OR self[Title/Abstract] OR pride[Title/Abstract] OR dominance[Title/Abstract])) AND 2010:2025[dp]',
            '(self-importance[Title/Abstract] OR entitlement[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": {"narcissism": 5, "narcissistic": 4, "grandiose": 4, "hubris": 5, "pride": 4,
                  "self-enhancement": 4, "self-aggrandizement": 5, "self-esteem": 3,
                  "social dominance": 4, "social hierarchy": 3, "social status": 3,
                  "social rank": 3, "self-importance": 4, "entitlement": 3,
                  "ego dissolution": 3, "default mode": 2, "self-referential": 2,
                  "prefrontal": 2, "prefrontal": 2, "striatum": 2}},
    5: {"name": "Water/Pleasure", "have": 12, "want": 50,
        "queries": [
            '(flow state[Title/Abstract] OR flow experience[Title/Abstract] OR optimal experience[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract] OR neuroscience[Title/Abstract]) AND 2005:2025[dp]',
            '(pleasure[Title/Abstract] OR hedonic[Title/Abstract] OR reward[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR nucleus accumbens[Title/Abstract] OR dopamine[Title/Abstract]) AND 2005:2025[dp]',
            '(peak experience[Title/Abstract] OR aesthetic pleasure[Title/Abstract] OR aesthetic experience[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(orgasm[Title/Abstract] OR sexual arousal[Title/Abstract] OR sexual pleasure[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR neuroimaging[Title/Abstract]) AND 2005:2025[dp]',
            '(ecstasy[Title/Abstract] OR rapture[Title/Abstract] OR bliss[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract]) AND 2000:2025[dp]',
            '(music[Title/Abstract] AND pleasure[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR reward[Title/Abstract] OR dopamine[Title/Abstract])) AND 2010:2025[dp]',
        ],
        "terms": {"flow state": 5, "flow experience": 5, "optimal experience": 4,
                  "pleasure": 3, "hedonic": 3, "reward": 2, "nucleus accumbens": 3,
                  "dopamine": 2, "peak experience": 5, "aesthetic": 3,
                  "orgasm": 4, "sexual arousal": 3, "ecstasy": 5, "rapture": 5, "bliss": 4,
                  "intrinsic motivation": 3, "self-transcendence": 2, "liking": 2, "wanting": 2,
                  "music": 2, "beauty": 2, "craving": 1, "desire": 1}},
    6: {"name": "Dependent-arising", "have": 15, "want": 50,
        "queries": [
            '(predictive coding[Title/Abstract] OR predictive processing[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR organization[Title/Abstract] OR theory[Title/Abstract]) AND 2010:2025[dp]',
            '(free energy principle[Title/Abstract] OR active inference[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cognition[Title/Abstract] OR behavior[Title/Abstract]) AND 2010:2025[dp]',
            '(Bayesian brain[Title/Abstract] OR Bayesian inference[Title/Abstract]) AND (perception[Title/Abstract] OR cognition[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2010:2025[dp]',
            '(prediction error[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract] OR learning[Title/Abstract])) AND 2010:2025[dp]',
            '(hierarchical inference[Title/Abstract] OR hierarchical predictive[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract]) AND 2010:2025[dp]',
            '(interoceptive inference[Title/Abstract] OR embodied inference[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR emotion[Title/Abstract] OR self[Title/Abstract]) AND 2010:2025[dp]',
        ],
        "terms": {"predictive coding": 5, "predictive processing": 4, "free energy": 4,
                  "free energy principle": 5, "active inference": 5, "Bayesian brain": 4,
                  "Bayesian inference": 3, "prediction error": 4, "hierarchical inference": 4,
                  "hierarchical predictive": 3, "interoceptive inference": 5,
                  "embodied inference": 4, "bayesian": 2, "belief updating": 3,
                  "precision weighting": 3, "generative model": 3, "expectation": 1}},
    8: {"name": "Formless/Absorption", "have": 15, "want": 50,
        "queries": [
            '(meditative absorption[Title/Abstract] OR deep meditation[Title/Abstract] OR samadhi[Title/Abstract]) AND (EEG[Title/Abstract] OR fMRI[Title/Abstract] OR neural[Title/Abstract] OR brain[Title/Abstract]) AND 2000:2025[dp]',
            '(altered state[Title/Abstract] OR non-ordinary[Title/Abstract] OR trance[Title/Abstract]) AND (meditation[Title/Abstract] OR hypnotic[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '(gamma[Title/Abstract] OR theta[Title/Abstract] OR alpha[Title/Abstract]) AND meditation[Title/Abstract] AND (coherence[Title/Abstract] OR synchronization[Title/Abstract] OR long-term[Title/Abstract]) AND 2005:2025[dp]',
            '(loving-kindness[Title/Abstract] OR compassion meditation[Title/Abstract] OR metta[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
            '(transcendental meditation[Title/Abstract] OR zen meditation[Title/Abstract] OR TM[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract]) AND 2000:2025[dp]',
            '(mystical experience[Title/Abstract] OR self-transcendence[Title/Abstract] OR transcendent[Title/Abstract]) AND (meditation[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"meditative absorption": 5, "deep meditation": 4, "samadhi": 6,
                  "altered state": 3, "non-ordinary": 3, "trance": 3,
                  "gamma": 2, "theta": 2, "alpha": 2, "coherence": 2,
                  "loving-kindness": 4, "compassion meditation": 4, "metta": 4,
                  "transcendental meditation": 4, "zen meditation": 4, "TM meditation": 3,
                  "mystical experience": 3, "self-transcendence": 3, "transcend": 2,
                  "long-term meditator": 2, "expert meditator": 2, "spiritual": 1}},
    9: {"name": "Language/Mantra", "have": 47, "want": 50,
        "queries": [
            '(mantra[Title/Abstract] OR mantra meditation[Title/Abstract] OR "OM"[Title/Abstract]) AND (brain[Title/Abstract] OR EEG[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract]) AND 2005:2025[dp]',
            '(inner speech[Title/Abstract] OR private speech[Title/Abstract] OR self-talk[Title/Abstract] OR verbal rehearsal[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR cortex[Title/Abstract] OR frontal[Title/Abstract]) AND 2010:2025[dp]',
            '(chanting[Title/Abstract] OR verbal repetition[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR EEG[Title/Abstract]) AND 2005:2025[dp]',
        ],
        "terms": {"mantra": 5, "mantra meditation": 5, "OM": 3, "inner speech": 4,
                  "private speech": 4, "self-talk": 3, "verbal rehearsal": 3,
                  "chanting": 4, "verbal repetition": 4, "focused attention": 2,
                  "meditation": 1, "repetitive speech": 3, "language": 1}},
    15: {"name": "Liberation/Enlightenment", "have": 15, "want": 50,
         "queries": [
            '(enlightenment[Title/Abstract] OR awakening[Title/Abstract] OR spiritual awakening[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract] OR experience[Title/Abstract]) AND 2005:2025[dp]',
            '(ego dissolution[Title/Abstract] OR self-loss[Title/Abstract] OR selflessness[Title/Abstract] OR no-self[Title/Abstract] OR anatta[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR psychedelic[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(enlightenment[Title/Abstract] OR spiritual enlightenment[Title/Abstract]) AND (neuroscience[Title/Abstract] OR brain[Title/Abstract] OR neural[Title/Abstract]) AND 2005:2025[dp]',
            '(nibbana[Title/Abstract] OR nirvana[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR meditation[Title/Abstract]) AND 2000:2025[dp]',
            '(religious experience[Title/Abstract] OR peak experience[Title/Abstract] OR mystical experience[Title/Abstract]) AND (brain[Title/Abstract] OR neural[Title/Abstract] OR neuroscience[Title/Abstract] OR meditation[Title/Abstract]) AND 2005:2025[dp]',
            '(self-transcendence[Title/Abstract] AND (brain[Title/Abstract] OR neural[Title/Abstract] OR fMRI[Title/Abstract] OR experience[Title/Abstract] OR meditation[Title/Abstract])) AND 2010:2025[dp]',
         ],
         "terms": {"enlightenment": 4, "awakening": 3, "spiritual awakening": 5,
                   "ego dissolution": 5, "self-loss": 5, "selflessness": 4,
                   "no-self": 5, "anatta": 6, "nibbana": 6, "nirvana": 5,
                   "religious experience": 3, "peak experience": 4, "mystical experience": 4,
                   "self-transcendence": 4, "default mode network": 3, "DMN": 2,
                   "psychedelic": 2, "psilocybin": 2, "meditation": 1}},
}

os.makedirs(WORKS_DIR, exist_ok=True)
os.makedirs(ESSAYS_DIR, exist_ok=True)
os.makedirs(LIBRARY, exist_ok=True)

def api_call(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Alt17Acq/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if "429" in str(e):
                time.sleep(5)  # rate limit backoff
            elif attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None
    return None

def search(query, retmax=MAX_PER_QUERY):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query,
        "retmax": retmax, "retmode": "json", "sort": "relevance", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    if not data: return []
    try: return json.loads(data).get("esearchresult", {}).get("idlist", [])
    except: return []

def fetch_summary(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
        "retmode": "json", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}")
    if not data: return {}
    result = {}
    try:
        parsed = json.loads(data)
        for uid, doc in parsed.get("result", {}).items():
            if uid == "uids": continue
            doi = pmc = ""
            for aid in doc.get("articleids", []):
                if aid.get("idtype") == "doi": doi = aid.get("value", "")
                if aid.get("idtype") == "pmc": pmc = aid.get("value", "")
            result[uid] = {
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "pubdate": doc.get("pubdate", ""),
                "doi": doi, "pmc": pmc,
                "authors": [a.get("name", "") for a in doc.get("authors", [])[:5]],
            }
    except: pass
    return result

def fetch_abstracts(pmids):
    if not pmids: return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
        "retmode": "xml", "rettype": "abstract", "email": EMAIL})
    time.sleep(DELAY)
    data = api_call(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params}")
    if not data: return {}
    articles = {}
    try:
        root = ET.fromstring(data)
        for article in root.findall(".//PubmedArticle"):
            pmid_el = article.find(".//PMID")
            if pmid_el is None or not pmid_el.text: continue
            pmid = pmid_el.text.strip()
            te = article.find(".//ArticleTitle")
            title = "".join(te.itertext()).strip() if te is not None else ""
            abs_parts = []
            for ae in article.findall(".//AbstractText"):
                txt = "".join(ae.itertext()).strip()
                if txt: abs_parts.append(txt)
            abstract = " ".join(abs_parts)
            ye = article.find(".//PubDate/Year")
            if ye is None: ye = article.find(".//PubDate/MedlineDate")
            year = ye.text.strip()[:4] if ye is not None and ye.text else ""
            articles[pmid] = {"title": title, "abstract": abstract, "year": year}
    except: pass
    return articles

def score_text(text, phase_terms):
    """Score a paper's title+abstract against phase-specific bridge terms."""
    tl = text.lower()
    score = 0
    for term, weight in phase_terms.items():
        if term.lower() in tl:
            score += weight
    # Bonus for mechanistic terms
    mech = ["neural", "brain", "fmri", "eeg", "neuroimaging", "cortex",
            "mechanism", "network", "connectivity", "neuroscience"]
    score += sum(0.5 for t in mech if t in tl)
    return score

def make_slug(title):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')[:60]
    return s or "untitled"

def is_clinical_noise(title, abstract):
    """Check if paper is clinical/engineering noise."""
    t = (title + " " + abstract).lower()
    clin = ["clinical trial", "randomized controlled", "randomized clinical",
            "mouse", "rat ", "mice", "case report", "animal model",
            "pharmacological treatment", "algorithm", "deep learning",
            "machine learning", "artificial intelligence", "robot"]
    clin_hits = sum(1 for c in clin if c in t)
    return clin_hits >= 2

def year_from_summary(s):
    """Extract year from pubdate string."""
    m = re.search(r'(\d{4})', s.get("pubdate", ""))
    return m.group(1) if m else ""

def download_pdf(pmc, doi, title, phase_name):
    """Try to download PDF for a PMC paper."""
    if not pmc and not doi: return None
    pmc_num = pmc.replace("PMC", "").strip() if pmc else ""
    time.sleep(DELAY)
    # Strategy 1: Publisher direct patterns
    if doi:
        doi_clean = doi.replace("doi:", "").strip()
        # Frontiers
        if "frontiers" in doi_clean.lower() or "frontiersin" in (title.lower()):
            url = f"https://journal.frontiersin.org/article/{doi_clean}/pdf"
            dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
            try:
                subprocess.run(["curl", "-sL", "-o", dest, url], timeout=20)
                if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                    return os.path.basename(dest)
            except: pass
        # Springer/BMC
        if any(x in doi_clean.lower() for x in ["springer", "10.1007", "10.1186", "bmc"]):
            url = f"https://link.springer.com/content/pdf/{doi_clean}.pdf"
            dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
            try:
                subprocess.run(["curl", "-sL", "-o", dest, url], timeout=20)
                if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                    return os.path.basename(dest)
            except: pass
        # PLoS One
        if "10.1371" in doi_clean:
            url = f"https://journals.plos.org/plosone/article/file?id={doi_clean}&type=printable"
            dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
            try:
                subprocess.run(["curl", "-sL", "-o", dest, url], timeout=20)
                if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                    return os.path.basename(dest)
            except: pass
        # eLife
        if "10.7554" in doi_clean:
            elife_id = doi_clean.split(".")[-1]
            url = f"https://cdn.elifesciences.org/articles/{elife_id}/elife-{elife_id}-v1.pdf"
            dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
            try:
                subprocess.run(["curl", "-sL", "-o", dest, url], timeout=20)
                if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                    return os.path.basename(dest)
            except: pass
        # Nature / Scientific Reports
        if "10.1038" in doi_clean:
            nature_id = doi_clean.split("/")[-1]
            url = f"https://www.nature.com/articles/{nature_id}.pdf"
            dest = os.path.join(LIBRARY, f"t2-{pmc_num or 'pubmed'}-{make_slug(title)}.pdf")
            try:
                subprocess.run(["curl", "-sL", "-o", dest, url], timeout=20)
                if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                    return os.path.basename(dest)
            except: pass

    # Strategy 2: OA FTP deprecated path
    if pmc_num:
        oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_num}"
        time.sleep(DELAY)
        try:
            with urllib.request.urlopen(oa_url, timeout=20) as resp:
                oa_xml = resp.read().decode("utf-8")
            oa_root = ET.fromstring(oa_xml)
            record = oa_root.find(".//record")
            if record is not None:
                for link in record.findall("link"):
                    if link.get("format") == "tgz":
                        ftp_href = link.get("href", "")
                        https_url = ftp_href.replace("ftp://", "https://")
                        dest_tgz = f"/tmp/pmc_{pmc_num}.tar.gz"
                        try:
                            subprocess.run(["curl", "-sL", "-o", dest_tgz, https_url], timeout=60)
                            if os.path.exists(dest_tgz) and os.path.getsize(dest_tgz) > 1000:
                                with tarfile.open(dest_tgz, "r:gz") as tar:
                                    pdf_members = [m for m in tar.getmembers()
                                                   if m.name.endswith(".pdf") and "Suppl" not in m.name]
                                    if pdf_members:
                                        pdf_fn = f"t2-{pmc_num}-{make_slug(title)}.pdf"
                                        pdf_dest = os.path.join(LIBRARY, pdf_fn)
                                        tar.extract(pdf_members[0], path="/tmp/pmc_extract/")
                                        src = f"/tmp/pmc_extract/{pdf_members[0].name}"
                                        if os.path.exists(src):
                                            import shutil
                                            shutil.move(src, pdf_dest)
                                            subprocess.run(["rm", "-rf", "/tmp/pmc_extract/"])
                                            if os.path.exists(pdf_dest) and os.path.getsize(pdf_dest) > 5000:
                                                return pdf_fn
                                subprocess.run(["rm", "-f", dest_tgz])
                        except: pass
        except: pass

    return None

def create_work_json(pmid, article, summary, phase_num, phase_name, score):
    """Create a work JSON file."""
    slug = f"pubmed-{make_slug(article['title'])}"
    work_id = f"work:t2-{slug}"
    
    # Check if already exists
    if os.path.exists(f"{WORKS_DIR}/t2-{slug}.json"):
        return None
    
    ident = {"pmid": pmid, "doi": summary.get("doi", "")}
    
    work = {
        "work_id": work_id,
        "schema_version": 2,
        "title": article["title"],
        "authors": [{"name": a} for a in summary.get("authors", [])],
        "publication": {
            "year": int(article["year"]) if article["year"].isdigit() else 0,
            "journal": summary.get("source", ""),
            "source": "PubMed/MEDLINE",
            "language": "en"
        },
        "identifiers": ident,
        "topics": [f"phase-{phase_num}-{phase_name.lower().replace('/', '-')}",
                   "frontier_science", "bridge_paper"],
        "assets": {
            "pdf_path": None,
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": article["abstract"][:500]
        },
        "provenance": {
            "access_status": "open",
            "oa_status": "green",
            "source": "pubmed_alt17_acquisition",
            "retrieved_at": time.strftime("%Y-%m-%d")
        },
        "phase_mapping": {
            "phase": phase_num,
            "phase_name": phase_name,
            "bridge_rationale": f"Bridge paper score={score:.1f}: links {phase_name} concept to mechanistic neuroscience"
        },
        "evaluation": f"Score {int(score)}: {'Excellent' if score >= 10 else 'Good' if score >= 6 else 'Marginal' if score >= 4 else 'Low'} bridge signal"
    }
    
    fpath = f"{WORKS_DIR}/t2-{slug}.json"
    with open(fpath, "w") as f:
        json.dump(work, f, indent=2)
    
    # Create Type B essay
    essay = {
        "id": f"bridge-{slug}",
        "type": "type-b-essay",
        "title": f"Bridge Essay: {article['title'][:80]}",
        "source_work": work_id,
        "phase": f"phase-{phase_num}",
        "phase_name": phase_name,
        "tags": ["frontier-science", "bridge-paper", f"phase-{phase_num}"],
        "body": [
            {"kind": "ai", "text": f"This bridge paper connects the esoteric/philosophical concept of **{phase_name}** (Phase {phase_num}) with mechanistic science from PubMed/MEDLINE."},
            {"kind": "ai", "text": f"**Bridge rationale:** Links {phase_name} to mechanistic neuroscience through {', '.join(article['title'].split()[:5])}."},
            {"kind": "summary", "text": f"**{article['title']}** — {summary.get('source','')} ({article['year']}). PMID: {pmid}. DOI: {summary.get('doi','')}. {article['abstract'][:500]}"}
        ],
        "notes": f"Auto-acquired from PubMed/MEDLINE on {time.strftime('%Y-%m-%d')}. Phase {phase_num} ({phase_name})."
    }
    
    epath = f"{ESSAYS_DIR}/bridge-{slug}.json"
    with open(epath, "w") as f:
        json.dump(essay, f, indent=2)
    
    return fpath

def acquire_phase(phase_num, config):
    """Acquire bridge papers for a single phase."""
    name = config["name"]
    have = config.get("have", 0)
    want = config.get("want", 50)
    need = want - have
    queries = config["queries"]
    terms = config["terms"]
    
    print(f"\n{'='*60}")
    print(f"Phase {phase_num}: {name} — have {have}, need {need}")
    print(f"{'='*60}")
    
    if need <= 0:
        print("Already at target, skipping.")
        return
    
    seen_titles = set()
    candidates = []
    
    for qi, query in enumerate(queries):
        if len(candidates) >= need * 2:  # get 2x needed for scoring buffer
            break
        print(f"\nQuery {qi+1}/{len(queries)}: {query[:80]}...")
        
        pmids = search(query)
        if not pmids:
            print("  No results.")
            continue
        print(f"  Found {len(pmids)} PMIDs")
        
        # Fetch summaries and abstracts
        summaries = fetch_summary(pmids[:MAX_PER_QUERY])
        abstracts = fetch_abstracts(pmids[:MAX_PER_QUERY])
        
        for pmid in pmids[:MAX_PER_QUERY]:
            if pmid not in abstracts or pmid not in summaries:
                continue
            article = abstracts[pmid]
            summary = summaries[pmid]
            
            title = article.get("title", "")
            abstract = article.get("abstract", "")
            year = article.get("year", "")
            
            # Skip clinical noise
            if is_clinical_noise(title, abstract):
                continue
            
            # Skip pre-2000
            if year.isdigit() and int(year) < 2000:
                continue
            # Skip pre-2015 unless exceptional
            if year.isdigit() and int(year) < 2015:
                score = score_text(title + " " + abstract, terms)
                if score < 8:
                    continue
            
            # Skip duplicates
            title_key = title.lower().strip()[:80]
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            
            score = score_text(title + " " + abstract, terms)
            
            if score >= 4:  # Accept threshold
                candidates.append((score, pmid, article, summary))
        
        time.sleep(DELAY)
    
    print(f"\nFound {len(candidates)} candidates above threshold")
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    created = 0
    for score, pmid, article, summary in candidates:
        if created >= need:
            break
        
        result = create_work_json(pmid, article, summary, phase_num, name, score)
        if result:
            created += 1
            print(f"  ✓ [{int(score)}pts] {article['title'][:60]}...")
            
            # Try to download PDF
            pmc = summary.get("pmc", "")
            doi = summary.get("doi", "")
            pdf = download_pdf(pmc, doi, article["title"], name)
            if pdf:
                # Update work JSON with PDF path
                try:
                    with open(result) as f:
                        wd = json.load(f)
                    wd["assets"]["pdf_path"] = pdf
                    with open(result, "w") as f:
                        json.dump(wd, f, indent=2)
                except: pass
                print(f"       PDF: {pdf}")
    
    print(f"\nCreated {created} new papers for Phase {phase_num} ({name})")
    return created


# =============================================
# MAIN EXECUTION
# =============================================
import subprocess, tarfile, shutil

print("=" * 60)
print("ALTERNATIVE 17-PHASE BRIDGE PAPER ACQUISITION")
print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# Zero-paper phases first (highest priority)
ZERO_PHASES = [1, 3, 7, 10, 14, 16, 17]
PARTIAL_PHASES = [2, 4, 5, 6, 8, 9, 15]

total_created = 0

# Process zero-paper phases with FULL 6-query search
for pn in ZERO_PHASES:
    config = PHASES[pn].copy()
    config["have"] = 0
    config["want"] = 50
    n = acquire_phase(pn, config)
    if n: total_created += n

# Process partial phases
for pn in PARTIAL_PHASES:
    config = PARTIAL_PHASES[pn].copy()
    n = acquire_phase(pn, config)
    if n: total_created += n

print("\n" + "=" * 60)
print(f"ACQUISITION COMPLETE")
print(f"Total new papers created: {total_created}")
print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
