--

Human Anatomy and Yogic Subtle-Body Packs

Design

The anatomy system is split into two inherited packs:

base
└── human-anatomy
    └── yogic-subtle-body

This division is deliberate. The same canonical body geometry supportsphysical systems, meditation phenomenology and yogic practice-maps, but thoseare not the same epistemic category.

Canonical body geometry

Every standing-body asset shares one coordinate system. Important landmarksinclude:

Region

Landmark IDs

Head

crown, brow, mouth

Neck and torso

throat, heart, lungLeft, lungRight, diaphragm, solarPlexus, navel

Pelvis

sacrum, root, leftHip, rightHip

Upper limbs

shoulders, elbows and wrists

Lower limbs

knees and ankles

This makes independent assets align perfectly. A nervous-system layer, chakrastack and body-scan band can share the same x, y and scale.

The geometry is defined in src/anatomy-geometry.mjs.

Physical and phenomenological assets

Asset

Function

human-standing-outline

Canonical standing front-body

human-seated-outline

Meditation posture

body-landmarks

Named coordinates and optional labels

lungs-diaphragm

Respiratory expansion and diaphragm movement

heart-circulation

Heart pulse and schematic routes

nervous-system

Central and peripheral signal paths

body-boundary

Operational body-world interface

awareness-halo

Movable phenomenological relevance field

body-scan-band

Ordered attentional scan

flow-particles

Generic deterministic current

Yogic subtle-body assets

Asset

Function

central-channel

Root-to-crown axis

chakra-stack

Seven parametrically animated lotus centers

ida-pingala

Paired woven channels

nadi-network

Branching channel field

kundalini-coil

Root coil and uncoiling motion

crown-field

Expansion above the crown

Physical and phenomenological mechanisms

Mechanism

Best used for

embodied-awareness-field

Awareness localized through changing relevance

body-scan

Ordered meditation instructions

meditation-settling

Coordination, reduced noise and stable posture

breath-cycle

Inhalation, exhalation, lung volume and diaphragm

breath-attention-coupling

Breath changing attention without identity claims

nervous-signal-propagation

Local stimulus and distributed response

interoceptive-map

Internal signals constructing a body-state

body-world-interface

Boundary, sensory access and selection

heart-breath-entrainment

Coordination of distinct bodily rhythms

Yogic mechanisms

Mechanism

Best used for

chakra-axis

A staged seven-centre practice-map

nadi-flow

Iḍā, piṅgalā and suṣumṇā coordination

kundalini-ascent

Coiled potential transforming into ascent

subtle-circulation

Return currents and cyclic practice

physical-subtle-compare

Rigorous science-versus-practice-map comparison

dvadasanta-ascent

Tantrāloka’s body-to-exterior twelve-station axis

prana-apana-balance

Opposed currents converging at the navel

Common recipes

Meditation instruction

Use:

meditation-settling;

optional awareness-halo;

optional body-scan-band;

anatomyIvory.

Scientific breath explanation

Use:

breath-cycle;

lungs-diaphragm;

optional body-landmarks;

no chakra or nāḍī overlay.

Tantra and neuroscience comparison

Use:

physical-subtle-compare;

physical assets on one body;

subtle assets on the other;

an explicit comparison subtitle;

no claim of anatomical identity.

Kuṇḍalinī or vertical ascent

Use:

kundalini-ascent for symbolic transformation;

dvadasanta-ascent for the specific twelve-station textual model;

nadi-flow when the claim concerns channels rather than ascent;

prana-apana-balance when the claim concerns opposed currents.

Awareness embodied but not owned

Use:

embodied-awareness-field;

body-boundary;

a base mechanism such as point-of-view in adjacent scenes;

continuity through one movable gold field.

Agent selection safeguards

A generic glowing body is not a mechanism.

A chakra stack must not be selected merely because the essay says “energy.”

breath-cycle is appropriate for respiration; nadi-flow is appropriatefor a yogic channel model.

Use physical-subtle-compare when an essay places Tantric maps and sciencein conversation.

Avoid mapping each chakra directly onto an endocrine gland unless the essayexplicitly discusses that contested proposal and labels its evidentialstatus.

Kuṇḍalinī motion is symbolic or contemplative unless the source claim isexplicitly phenomenological.

Render the proof

npm run contact:anatomy
npm run render:anatomy

The worked pack is packs/anatomy-and-subtle-body-capabilities.json.



