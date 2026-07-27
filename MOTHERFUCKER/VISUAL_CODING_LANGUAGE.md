The Visual Coding Language

Core expression

A scene is now constructed as:

scene = theme + semantic mechanism + parameters + asset overlays + transition

Each term has one responsibility.

Layer

Responsibility

May change meaning?

Theme

Color, border, paper, typography, glow temperament

No

Asset

Reusable visible object or motion field

Only locally

Mechanism

The relation the shot proves

Yes; this is the semantic core

Parameter

Bounded variation within one mechanism

No

Overlay

Additional permitted assets layered over the mechanism

It may clarify, never replace the mechanism

Transition

Handoff between shots

No

Continuity object

Meaning preserved across several shots

Yes, across the film

Why assets and mechanisms are separate

lungs-diaphragm is an asset. It is a reusable animated structure.

breath-cycle is a mechanism. It coordinates air direction, lung expansionand diaphragm movement to prove a cyclical relation.

The same lung asset can appear in:

a breathing explanation;

meditation and attention coupling;

physical/subtle comparison;

heart-breath entrainment;

an essay-specific composition.

If every use required a new lung drawing, the framework would remain a scenecollection. Separating assets makes it a language.

Asset-layer syntax

Assets are rendered after the semantic mechanism and before the footer. Arrayorder is z-order.

{
  "capabilityPacks": ["yogic-subtle-body"],
  "theme": "anatomyIvory",
  "scenes": [
    {
      "id": "breath-focus",
      "title": "Breath Reorganises Attention",
      "subtitle": "The diaphragm and a field of relevance change together.",
      "term": "Prāṇa-dhāraṇā",
      "devanagari": "प्राणधारणा",
      "motif": "semantic-essay",
      "params": {
        "visual": "breath-cycle"
      },
      "overlays": [
        {
          "asset": "awareness-halo",
          "start": 0.18,
          "revealEnd": 0.38,
          "exitStart": 1,
          "opacity": 0.38,
          "params": {
            "focus": "diaphragm",
            "radius": 54
          }
        }
      ]
    }
  ]
}

Layer timing uses normalized scene time:

start: first possible appearance;

revealEnd: asset reaches full opacity;

exitStart: fade-out begins;

opacity: maximum layer opacity;

blendMode: optional canvas compositing mode.

Type rules

Pack permission

Every asset and mechanism has one owning pack. A project receives it only byselecting that pack or a child that inherits it.

Selecting human-anatomy grants lungs and breath mechanisms. It does notgrant chakras or kuṇḍalinī. Selecting yogic-subtle-body grants both becauseit inherits physical anatomy.

Semantic authority

The mechanism remains authoritative. Overlays cannot make an incompatiblemechanism valid.

Bad:

{
  "visual": "technical-rate-plot",
  "overlays": [{ "asset": "chakra-stack" }]
}

This does not become a valid chakra explanation merely because chakras aredrawn over a graph.

Good:

{
  "visual": "physical-subtle-compare",
  "overlays": [{ "asset": "body-landmarks", "opacity": 0.3 }]
}

The overlay clarifies the already valid comparison.

Epistemic typing

Assets and mechanisms may declare one of these modes:

Mode

Meaning

structural

Neutral coordinate or compositional structure

biomedical-schematic

Simplified empirically grounded physical process

phenomenological

Structure of reported or attended experience

functional-model

Abstract organization, not a literal organ

yogic-contemplative-model

Practice-map inherited from a yogic textual tradition

yogic-symbolic-model

Symbolic transformation used in practice or interpretation

textual-yogic-map

Specific ordered model from a source tradition

explicit-category-comparison

Different model types shown without collapse

An agent must preserve these modes in its rationale and subtitle. It maycompare modes but must not silently convert one into evidence for another.

Composition constraints

Begin with one semantically correct mechanism.

Add zero to three overlays under normal conditions.

Every overlay must have a named job:

provide a coordinate;

reveal a subsystem;

carry continuity;

emphasize a selected region;

show a secondary synchronized process.

Reject overlays that only make the frame busier.

Keep one dominant motion proof.

Preserve the footer safe area.

Prefer parameter changes over nearly duplicate assets.

Reuse canonical landmarks so assets align exactly.

Use theme color tokens before scene-specific colors.

Test combinations at both mature still time and intermediate motion.

Agent assembly algorithm

For each essay beat:

Determine the beat relation and epistemic mode.

Select a compatible mechanism from the resolved capability profile.

Identify required visible nouns that the mechanism does not already draw.

Search assets by semantic tags and epistemic mode.

Reject any asset from an incompatible mode unless the beat is explicitly acomparison.

Add the smallest useful overlay set.

Assign each asset a reveal time linked to narration.

Verify that removing the overlay would reduce clarity.

Verify that removing the mechanism would destroy the argument.

Render and inspect at t=0.25, 0.5, 0.72 and 0.95.

When to create something new

Create a new asset when a stable visible object or process will be reusedinside at least two different mechanisms.

Create a new mechanism when the source-to-target relation, preserved invariantor temporal proof is not represented by the current catalog.

Create a preset when geometry and motion stay the same but labels, counts,colors or selected nodes change.

Create a project-local composition when a combination is valuable once butdoes not yet justify shared vocabulary.


