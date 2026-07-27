#!/usr/bin/env python3
"""Assign Phase 0 (unassigned) papers to appropriate phases based on title analysis."""
import glob, json, re

works_dir = 'content/works'

# Bridge keywords per phase for assignment
PHASE_MAP = {
    # Phase 7: Emptiness — self, meditation, ego dissolution, DMN
    'phase-7': {
        'phase': 7, 'name': 'Emptiness',
        'keywords': ['meditation', 'self', 'ego', 'dm', 'resting state', 'consciousness', 
                     'nondual', 'non-dual', 'awareness', 'mindfulness', 'brain', 'cognition'],
        'bridge': 'Self-dissolution, meditation, DMN, ego dissolution, resting state consciousness.'
    },
    # Phase 8: Non-fabrication — spontaneous thought, creativity, mind-wandering
    'phase-8': {
        'phase': 8, 'name': 'Non-fabrication',
        'keywords': ['creative', 'spontaneous', 'mind-wandering', 'spike', 'synchrony',
                     'music', 'improv', 'rhythm'],
        'bridge': 'Spontaneous thought, creativity, mind-wandering, involuntary cognition.'
    },
    # Phase 6: Dependent arising — predictive processing, causal, emergence
    'phase-6': {
        'phase': 6, 'name': 'Dependent Arising',
        'keywords': ['predictive', 'causal', 'emergence', 'morphogenesis', 'bioelectric',
                     'homeostasis', 'cellular', 'development', 'evolution', 'modeling',
                     'somatic', 'complex', 'bayesian', 'free energy', 'active inference'],
        'bridge': 'Predictive processing, causal inference, emergence, active inference.'
    },
    # Phase 10: Imaginal — mental imagery, perception, visualization
    'phase-10': {
        'phase': 10, 'name': 'Imaginal Reconstruction',
        'keywords': ['imagery', 'visual', 'mental image', 'fMRI brain', 'mind-to-image',
                     'decoding visual', 'perception', 'imagination', 'neural representation'],
        'bridge': 'Mental imagery, visual imagery, perception, neural decoding.'
    },
    # Phase 17: Social — social cognition, intersubjectivity
    'phase-17': {
        'phase': 17, 'name': 'Social Incarnation',
        'keywords': ['social', 'friends', 'tuning', 'multi-modal', 'gesture', 'music',
                     'category theory', 'gestural'],
        'bridge': 'Social cognition, intersubjectivity, gestural communication.'
    },
    # Phase 3: 4E cognition — embodied, enactive
    'phase-3': {
        'phase': 3, 'name': 'Mind as Computer Critique',
        'keywords': ['embodied', 'enactive', 'extended mind', 'situated', 'quantum',
                     'mind-brain', 'technological', 'virtual', 'representation'],
        'bridge': 'Embodied cognition, extended mind, situated cognition.'
    },
    # Phase 11: Body-energy — heart, interoception
    'phase-11': {
        'phase': 11, 'name': 'Body-energy',
        'keywords': ['heart rate', 'heart', 'variability', 'cardiac', 'interocept'],
        'bridge': 'Interoception, heart-brain axis, visceral perception.'
    },
}

def load_work(path):
    with open(path) as f:
        return json.load(f)

def save_work(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Find Phase 0 papers
phase0_files = []
for w in sorted(glob.glob(f'{works_dir}/t2-*.json')):
    data = load_work(w)
    pm = data.get('phase_mapping', {})
    if not pm or pm.get('phase') == 0:
        phase0_files.append((w, data))

print(f'Found {len(phase0_files)} Phase 0/unassigned papers')

assigned = 0
for w, data in phase0_files:
    title = data.get('title', '').lower()
    
    # Score each phase
    scores = {}
    for phase_key, phase_info in PHASE_MAP.items():
        score = 0
        for kw in phase_info['keywords']:
            if kw.lower() in title:
                score += 1
        scores[phase_key] = score
    
    best_phase = max(scores, key=scores.get)
    best_score = scores[best_phase]
    
    if best_score >= 1:
        info = PHASE_MAP[best_phase]
        # Update phase_mapping
        if 'phase_mapping' not in data or not data['phase_mapping']:
            data['phase_mapping'] = {}
        data['phase_mapping']['phase'] = info['phase']
        data['phase_mapping']['phase_name'] = info['name']
        data['phase_mapping']['bridge_rationale'] = info['bridge']
        
        # Update topics
        phase_tag = f'phase-{info["phase"]}-{info["name"].lower().replace(" ", "-")}'
        if 'topics' not in data:
            data['topics'] = []
        if phase_tag not in data['topics']:
            data['topics'].append(phase_tag)
        if 'frontier_science' not in data['topics']:
            data['topics'].append('frontier_science')
        
        save_work(w, data)
        assigned += 1
        print(f'  ASSIGNED Phase {info["phase"]} ({info["name"]}): {data["title"][:70]}')
    else:
        print(f'  UNASSIGNED (no match): {data["title"][:70]}')

print(f'\nTotal reassigned: {assigned}')

# Report updated phase counts
print('\nUpdated phase counts:')
phases = {}
for w in sorted(glob.glob(f'{works_dir}/t2-*.json')):
    data = load_work(w)
    pm = data.get('phase_mapping', {})
    p = pm.get('phase', 0) if pm else 0
    pn = pm.get('phase_name', 'no-phase-mapping') if pm else 'no-phase-mapping'
    key = (p, pn)
    phases[key] = phases.get(key, 0) + 1

for (p, n), c in sorted(phases.items()):
    print(f'  Phase {p:2d} ({n:30s}): {c:3d}')
