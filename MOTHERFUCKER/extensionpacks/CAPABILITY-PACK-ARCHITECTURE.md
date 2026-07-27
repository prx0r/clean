

Extensible Capability-Pack Architecture

Purpose

The framework is not a collection of finished animations. It is a growingvisual reasoning system for turning essays into deterministic Skia films.

The stable renderer owns quality. Capability packs expand what the system cansay visually. Project programs decide which capabilities are appropriate forone essay.

The unit of growth is therefore not one PIL file and not one scene. Theunit of growth is a reusable visual capability with:

a semantic relation it can prove;

a spatial grammar;

a temporal transformation;

explicit parameters;

a style-independent Skia renderer;

provenance and search tags;

validation and a worked example.

What the audit found

The source audit covers the 22 original platinum scripts plus the twoattached technical scripts.

Source family

Files

Scenes

Main value

Original platinum collection

22

240

Taxonomies, paths, nested worlds, cycles, filters, causal diagrams, body axes, cosmograms, matrices

Life-crosses-barriers

1

54

Barriers, tunnelling, energy landscapes, molecular gates, evidence and rate comparisons

Time-produced-by-forgetting

1

77

Simultaneity, sequence, moving present, traces, future branches, measurement versus experience

Total audited

24

371

A large visual corpus, but with renderer and visual logic mixed together

The original scripts and the current Skia framework solve different parts ofthe problem:

Concern

Original PIL packs

Existing Skia base

Capability-pack system

Rendering

Repeated in every file

Central, deterministic, native Skia

Inherited from the kernel

Border and typography

Reimplemented per file

Stable manuscript system

Theme tokens may replace chrome without replacing the renderer

Visual ideas

Many, but trapped in scene functions

Curated semantic mechanisms

Installable and searchable mechanisms

Essay reasoning

Usually authored inside one script

Typed argument IR and correspondence audit

Restricted to the mechanisms supplied by selected packs

Reuse

Copy and edit functions

Reuse built-ins

Inheritance, composition, parameters and provenance

Growth

File count rises

Core file grows

New child packs add capability without modifying the kernel

The audit report is generated ataudits/platinum-and-science-capability-inventory.json. It records 371 scenes,palette constants, renderer helpers, scene metadata, visual registries andcandidate mechanism clusters without executing the Python files.

The five layers

1. Kernel

The kernel changes slowly. It owns:

logical 1280×720 geometry and resolution scaling;

Skia canvas creation;

deterministic random state;

easing, paths, particles and text shaping;

background caching;

borders and lower thirds;

essay compilation and frame-quantized timing;

semantic correspondence auditing;

FFmpeg streaming and video validation.

Kernel code should never know what an enzyme, a temporal window or a tantriccosmogram means.

2. Style packs

A style pack changes presentation, not semantic truth. It can define:

color tokens;

background and texture;

border chrome;

footer chrome;

typography policy;

glow strength;

motion temperament;

label density;

transition defaults.

science-blue demonstrates this with a blue technical border, calibrationticks, a faint grid, precise panels and reduced glow.

A style pack must not claim that a visual is appropriate for an essay. That isthe job of capability metadata and the essay agent.

3. Capability packs

A capability pack contributes semantic mechanisms. Every mechanism declares:

Field

Meaning

id

Stable lowercase kebab-case name

description

What visual relation the mechanism performs

relations

Registered semantic relations it can validly encode

operators

Visual operations it supports

semanticTags

Search vocabulary for domain and concept matching

motionProof

Why time is necessary to make its claim

parameters

Bounded ways to adapt the mechanism

provenance

Source scenes or packs that motivated it

The runtime module supplies a native-Skia renderer for each declaredmechanism. A manifest declaration without a renderer fails during activation.

4. Domain packs

A domain pack combines style policy and mechanisms for a recurring subject.

Examples included here:

science-blue extends base;

bio-quantum extends science-blue;

temporal-cognition extends science-blue.

A future domain pack might be:

neuroscience extending science-blue;

systems-ecology extending science-blue;

platinum-tantra extending base;

mathematical-proof extending science-blue;

mythic-cosmology extending base.

5. Project programs

A project is one essay, its analysis, visual program and render settings. Itselects packs instead of seeing every mechanism ever written:

{
  "capabilityPacks": ["bio-quantum", "temporal-cognition"],
  "theme": "scienceBlue"
}

This produces the inheritance order:

base → science-blue → bio-quantum
                    → temporal-cognition

The project receives all base and science mechanisms plus both childvocabularies. If it selects only bio-quantum, amoving-time-window scene is rejected even if that mechanism has previouslybeen installed in the same process.

Deterministic inheritance rules

The resolver uses parent-first depth-first ordering.

Parents activate before children.

A child inherits every parent mechanism.

A mechanism ID has one owner. Children cannot silently override it.

A theme name may be repeated only when its full token definition isidentical.

The last child default theme becomes the resolved default.

Selection policy keys merge parent first, child last.

Cycles are errors.

Missing runtime implementations are errors.

A project can use only mechanisms in its resolved profile.

Omitting capabilityPacks preserves legacy behavior and exposes only thebuilt-in base vocabulary.

These rules keep output reproducible and make it possible to answer, “Whichpack supplied this visual?”

Repository contract

capability-packs/
  base/
    pack.json
  science-blue/
    pack.json
  bio-quantum/
    pack.json
  temporal-cognition/
    pack.json
src/
  capability-packs.mjs
  science-visuals.mjs
capability-pack.schema.json
packs/
  science-blue-capabilities.json

A manifest has this shape:

{
  "version": "1.0",
  "id": "child-pack",
  "title": "Child Pack",
  "description": "What domain grammar this pack contributes.",
  "extends": ["science-blue"],
  "defaultTheme": "scienceBlue",
  "runtimeModule": "../../src/child-visuals.mjs",
  "themes": [],
  "mechanisms": [
    {
      "id": "new-mechanism",
      "description": "A relation-bearing description.",
      "relations": ["dependency", "transformation"],
      "operators": ["coordinate", "transform"],
      "semanticTags": ["domain", "process", "cause"],
      "motionProof": "What changes over time and why a still cannot prove it.",
      "parameters": {},
      "provenance": ["source_pack.py: scene or technique"]
    }
  ],
  "selectionPolicy": {}
}

The runtime module exports:

export const mechanismImplementations = Object.freeze({
  "new-mechanism": renderNewMechanism,
});

The capability types

Every imported PIL idea must be classified into exactly one primary type.

Type

Test

Destination

Kernel infrastructure

Is it needed by nearly every scene regardless of meaning?

Existing kernel module

Style token

Does it change appearance while preserving the same semantic geometry?

Theme manifest

Primitive

Is it a low-level mark useful inside several unrelated mechanisms?

src/primitives.mjs

Mechanism

Does it perform a distinct relation that existing mechanisms cannot?

Capability manifest + runtime

Parameter

Is it the same topology and motion with a bounded change?

Existing mechanism parameter schema

Preset

Is it a named parameter bundle useful to agents?

Pack preset metadata

Worked example

Is it valuable as a composition but not general enough to select?

Demo scene pack

Reject

Is it decorative, redundant, unreadable or semantically ungrounded?

Audit record only

This prevents the common failure where 100 source scenes become 100 nearlyidentical mechanism names.

Mechanism identity

Two scenes are the same mechanism when they share:

relation type;

topology of marks;

state transition;

preserved invariant;

information channels;

motion proof.

Different labels, colors, node counts or domain nouns usually becomeparameters. A new mechanism is justified when at least one of the six itemsabove changes in a way that lets the framework represent a claim it could notrepresent correctly before.

Examples:

PIL variation

Framework decision

Seven, twelve or thirty-six levels

One scalar/taxonomy mechanism with count and grouping parameters

Different colored nested eggs

One nested-containment mechanism with shell parameters

Barrier width versus particle mass

Presets or parameters on barrier/response mechanisms

Classical stop versus quantum penetration

A distinct barrier-tunnelling comparison mechanism

Clock, calendar and hourglass with no changing access relation

Reject as literal decoration

Moving present window over fixed events

Distinct moving-time-window mechanism

How to mine a PIL file

Run the AST inventory:

python3 tools/audit-pil-pack.py path/to/pack.py --out audits/pack.json

For a batch:

python3 tools/audit-pil-pack.py path/to/packs/*.py --out audits/all-packs.json

Then perform these passes.

Pass A: remove duplicated infrastructure

Mark background generation, fonts, glow helpers, partial paths, borders,footers, FFmpeg, frame folders, contact sheets and validation as kernelconcerns. Do not port them into a child pack.

Pass B: extract style

Convert palette, border, texture, label and motion conventions into themetokens. Render an existing base mechanism with the new theme. If the meaningis unchanged, the extraction is correct.

Pass C: fingerprint every scene

For each scene record:

claim;

relation;

source state;

target state;

preserved invariant;

marks and channels;

temporal change;

likely misreading;

domain tags.

Do not use the source function name as the final mechanism name until thisfingerprint is complete.

Pass D: deduplicate

Compare the fingerprint with the resolved base and domain profiles.

Same fingerprint: create a preset or example.

Same relation but genuinely different topology: consider a new mechanism.

New primitive inside an existing topology: add the primitive, then reuse themechanism.

No relation-bearing motion: reject or redesign.

Pass E: implement native Skia

Port only the visual middle layer. Use logical coordinates and existingprimitives. The framework continues to draw background, border and footer.Randomness must come from the supplied deterministic environment.

Pass F: register and prove

Add manifest metadata, parameter bounds, provenance, tests and at least onedemo scene. Render at t=0.0, 0.5, 0.72 and 1.0.

Acceptance gates for a new mechanism

A mechanism joins the library only if every gate passes.

Correspondence: its geometry directly encodes every declared relation.

Motion proof: removing time would remove part of the argument.

Caption independence: the primary claim remains inferable withouttypesetting the narration.

Parameter bounds: an agent cannot pass values that destroy legibility.

Style independence: it works under its parent theme and at least onealternate compatible theme.

Determinism: identical seed, scene and time produce identical pixels.

Resolution: it remains legible at 640×360 and clean at 1920×1080.

Continuity: it declares what object may enter and leave the scene.

Provenance: its source PIL scenes are named.

Novelty: it adds a missing capability rather than another noun for anexisting drawing.

How an essay agent selects packs

Pack selection happens before shot selection.

Extract the essay's domain terms, relation histogram and epistemic tone.

Resolve base.

Score optional packs:

relation coverage: 40;

domain-tag match: 25;

style/tone match: 15;

continuity support: 10;

mechanism novelty useful to this essay: 10.

Select the smallest set that covers the argument. More packs are notautomatically better.

If one theme is clearly requested, select its parent style pack.

If no optional pack reaches 55/100, remain on base.

If the essay needs a missing relation, author a project-local mechanismand validate it before use. Do not force a nearby but incorrect visual.

Examples:

Essay

Packs

Theme

General philosophy of identity and relation

base

ivoryManuscript

Enzyme tunnelling and evidence

bio-quantum

scienceBlue

Memory, attention and produced time

temporal-cognition

scienceBlue

Essay joining biological barriers and temporal prediction

bio-quantum, temporal-cognition

scienceBlue

One-off branded commission

Relevant domain pack plus project-local style pack

Project theme

How an essay agent selects a mechanism

For every beat, the agent must first write a visual-free argument record:

semantic role;

exact claim;

relation type;

source state;

target state;

preserved invariant;

continuity object;

misreading risk.

It then filters the resolved profile by exact relation compatibility andscores at least three candidates:

Criterion

Points

Exact relation correspondence

30

Motion performs the claimed change

20

Domain and scale match

15

Continuity handoff

15

Legibility and information economy

10

Useful novelty relative to neighboring shots

10

Reject a candidate regardless of score if:

its registered relations do not include the beat relation;

the visual is understandable only because the full narration is printed;

motion is ornamental;

it creates a stronger metaphysical or scientific claim than the essay;

it repeats an unchanged signature already used nearby;

it belongs to an unselected pack.

If no candidate scores at least 72, the agent must redesign the beat,compose a supported custom visual, or propose a new capability.

Scene parameterization rules

Parameters adapt evidence; they do not rewrite mechanism identity.

Good parameters:

bounded node count;

labels shorter than a declared maximum;

selected branch or tier;

axis names;

direction;

grouping;

domain-specific palette accents;

intensity or density within tested limits.

Bad parameters:

arbitrary callback code;

unbounded arrays;

prose paragraphs;

a switch that changes the relation type;

a mode that turns a network into an unrelated cosmogram.

When a parameter begins changing topology or motion proof, split a newmechanism.

Growth metrics

Count capability, not files.

Track:

mechanisms by relation type;

domain-tag coverage;

parameter and preset reuse;

percentage of new PIL scenes deduplicated into existing mechanisms;

mechanisms used successfully in more than one essay;

visual audit failures by cause;

adjacent-shot repetition;

caption-independence review;

project-local mechanisms promoted into shared packs.

A healthy library has increasing reuse. If every new source file creates a newmechanism, the abstraction layer is too weak.

Versioning

Patch: rendering fix with unchanged semantic contract.

Minor: new mechanism, parameter or theme compatible with existing programs.

Major: changed relation contract, removed ID, changed parameter meaning orinheritance behavior.

Mechanism IDs are permanent. Deprecate them with a replacement; do not reusetheir names for different geometry.

Included worked inheritance

science-blue contributes:

technical-rate-plot;

evidence-ladder;

phase-space-trajectories;

the scienceBlue technical theme.

bio-quantum inherits those and adds:

barrier-tunnelling;

energy-landscape;

molecular-gate.

temporal-cognition inherits the same parent and adds:

moving-time-window;

simultaneity-sequence;

branching-future.

The nine-scene proof is packs/science-blue-capabilities.json.

Commands

# List installed capability packs
node src/cli.mjs capabilities

# Resolve inheritance and inspect the exact mechanism vocabulary
node src/cli.mjs capabilities bio-quantum temporal-cognition

# Validate and render the worked child-pack proof
node src/cli.mjs validate packs/science-blue-capabilities.json
node src/cli.mjs contact packs/science-blue-capabilities.json
node src/cli.mjs render packs/science-blue-capabilities.json

# Run deterministic kernel, essay and capability tests
npm test

Definition of done for a child pack

A child pack is complete when:

its manifest validates;

every parent resolves;

it introduces no mechanism or theme conflicts;

every declared renderer registers;

every mechanism has relation, operator, tags, motion proof, parameters andprovenance;

a project can use inherited and local mechanisms;

a project cannot use sibling mechanisms without selecting the sibling;

representative frames pass visual review;

deterministic tests pass;

a short demo pack shows each new mechanism;



the essay-agent prompt can discover and select the pack without reading itsimplementation.

