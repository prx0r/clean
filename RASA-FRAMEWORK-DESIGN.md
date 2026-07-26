# Rasa — GLSL Framework Design

## Architecture (Following LYGIA)

LYGIA's formula: **granular + composable + configurable + multi-language**.

Each file holds exactly one function. Functions compose through `#include`. Behavior changes through `#define`. The framework supports GLSL, HLSL, Metal, WGSL, CUDA from the same source.

We follow the same pattern for a different domain: not generic graphics primitives but **philosophically-grounded visual functions** — temporal structure, ontological depth, aesthetic modes, and the universalization pipeline.

---

## Directory Structure

```
rasa/
├── version.glsl              — Version info, changelog
├── rasa.glsl                 — Umbrella include (includes everything)
│
├── spanda/                   — Temporal pulse functions
│   ├── moment.glsl           — Three-moment pulse: udaya/sthiti/laya
│   ├── universal.glsl        — Sāmānyaspanda: wave from the Heart
│   ├── echo.glsl             — Echo: reflection in time
│   ├── hierarchy.glsl        — Nanavira's 3-level accelerated hierarchy
│   └── intensity.glsl        — Intensity distribution (2:1 weight)
│
├── tattva/                   — Ontological depth as visual density
│   ├── state.glsl            — TattvaState: {density, camatkara, color}
│   ├── atLevel.glsl          — tattvaAtLevel(1..36)
│   ├── fromProgress.glsl     — currentTattva(progress)
│   ├── range.glsl            — tattvaRange(start, end, progress)
│   └── color.glsl            — Spectral color map per tattva
│
├── rasa/                     — Emotional/ aesthetic modes
│   ├── mode.glsl             — RasaMode struct (spandaSpeed, tattvaRange, univRate, colorFn)
│   ├── forScene.glsl         — rasaForScene(sceneIndex)
│   ├── palette.glsl          — 9 rasa base palettes
│   └── motion.glsl           — Motion quality per rasa
│
├── camatkara/                — Wonder — aesthetic climax
│   ├── dissolve.glsl         — Dissolution into pure light
│   ├── reveal.glsl           — Reveal of structure
│   ├── apex.glsl             — Aesthetic climax combination
│   └── threshold.glsl        — Camatkāra threshold detection
│
├── sadharanikarana/          — Universalization pipeline
│   ├── universalize.glsl     — Strip specific, reveal universal
│   ├── vibhava.glsl          — Stimulus stage: specific geometry appears
│   ├── anubhava.glsl         — Response stage: geometry reacts
│   ├── vyabhicari.glsl       — Transient state: multiple layers interplay
│   └── rasasvadana.glsl      — Tasting stage: pure aesthetic form
│
├── pratibimba/               — Reflection/ mirror functions
│   ├── mirror.glsl           — pratibimba(color, tint, strength)
│   ├── analogize.glsl        — Like taste in saliva, smell in nose
│   └── echo.glsl             — Echo structure for reflections
│
├── samarasya/                — Resolution / integration
│   └── resolve.glsl          — Layer unification
│
├── bija/                     — Foundational primitives
│   ├── anuttara.glsl         — U1manifest, supreme
│   ├── kula.glsl             — The whole, the totality
│   ├── akula.glsl            — The part, the individual
│   └── matrka.glsl           — Phonemic consciousness (50 phonemes as seeds)
│
└── test/                     — Visual test examples
    ├── spanda_test.glsl
    ├── tattva_test.glsl
    └── rasa_test.glsl
```

---

## File Format Convention

Each file follows LYGIA's header convention exactly:

```glsl
// SPDX-License-Identifier: MIT
// Copyright (c) 2026 rasa-framework contributors
// 
// @function udaya_sthiti_laya — three-moment temporal pulse
// @param t  normalized time (0-1)
// @param frequency  pulse frequency
// @return pulse value (0-1) with udaya (rising), sthiti (abiding), laya (dissolving) phases
//
// Based on Abhinavagupta's spanda doctrine: consciousness as pulse.
// Three moments: emanation (udaya), abiding (sthiti), withdrawal (laya).
// Each moment is one-third of the cycle, weighted equally.
//
// See: Tantraloka Ahnika 7, Dyczkowski Vol.5 pp.3-5
// See: spanda/echo.glsl for reflection structure
//
// Examples:
//   float p = udaya_sthiti_laya(t * 0.5, 2.0);

#ifndef RASA_SPANDA_MOMENT
#define RASA_SPANDA_MOMENT

float udaya_sthiti_laya(float t, float frequency) {
    float phase = fract(t * frequency);
    float phase3 = phase * 3.0;
    float udaya = smoothstep(0.0, 1.0, phase3);
    float sthiti = smoothstep(0.0, 1.0, phase3 - 1.0) - smoothstep(1.0, 2.0, phase3 - 1.0);
    float laya = 1.0 - smoothstep(0.0, 1.0, phase3 - 2.0);
    return (udaya + sthiti + laya) * 0.333;
}

#endif
```

**Required header fields:**
- `@function` — Name and one-line description
- `@param` — One per parameter  
- `@return` — Return value description
- Philosophical provenance (source text citation)
- `@see` — Related functions
- Examples (optional but encouraged)

---

## Configuration System

Follow LYGIA's `#define` pattern for configurable behavior:

```glsl
// Default: linear acceleration
#ifndef RASA_SPANDA_FNC
#define RASA_SPANDA_FNC(t, freq) udaya_sthiti_laya(t, freq)
#endif

// Override for Nanavira-style accelerated hierarchy:
// #define RASA_SPANDA_FNC(t, freq) nanavira_moment(t, freq, 2.0)
```

```glsl
// Default: full 36 tattvas
#ifndef RASA_TATTVA_RANGE
#define RASA_TATTVA_RANGE(start, end) tattva_range(start, end, u)
#endif

// Override for specific rasa:
// #define RASA_TATTVA_RANGE(s, e) tattva_range_by_rasa(s, e, RASA_ADBHUTA)
```

---

## Versioning

```
rasa/v0.1/ — Spanda core (moment, universal, echo, hierarchy, intensity)
rasa/v0.2/ — Tattva system (state, atLevel, fromProgress, range, color)
rasa/v0.3/ — Rasa modes (mode, forScene, palette, motion)
rasa/v0.4/ — Sādhāraṇīkaraṇa pipeline (universalize, vibhava, anubhava, vyabhicari, rasasvadana)
rasa/v1.0/ — Full framework with camatkāra, pratibimba, sāmarasya
```

Each version is a directory with complete, non-breaking includes. Old versions remain available.

---

## Resolution Strategy (How It Compiles)

LYGIA uses a server (`lygia.xyz`) and a local `#include` resolver. Our framework needs:

1. **Local**: Clone `rasa/` into the project, `#include "rasa/spanda/moment.glsl"` resolved by the GLSL loader.
2. **Server**: Optional CDN for web use (future).
3. **Bundle script**: `bundle.py` that inlines all includes into a single file for environments without `#include` support.

---

## Design Principles

### 1. One function per file
Each `.glsl` file contains exactly one public function. Internal helpers prefixed with `_`. This makes the framework searchable, testable, and tree-shakeable.

### 2. Philosophical provenance in every header
Every function cites the source text it derives from. A user of `udaya_sthiti_laya()` should know they're using a function based on Tantraloka Āhnika 7. The philosophy is documented, not hidden.

### 3. Function names describe behavior, not philosophy
`udaya_sthiti_laya()` is named for what it does (three-phase pulse). The Tantraloka citation is in the comment. A user can understand the function without knowing the philosophy, and discover the philosophy through the citation.

### 4. All 36 tattvas can be bypassed
A user who just wants `tattva_range(5, 20)` to get a density gradient should not need to understand the Śaiva cosmology. The function works without the philosophy; the philosophy deepens the function.

### 5. Rasa as mode, not color
Rasa modes affect spanda speed, tattvic range, universalization rate, AND color. A shader set to `RAUDRA` mode doesn't just turn red — it pulses faster, moves through lower tattvas, universalizes more violently, and fractures its geometry.

### 6. Multi-language from day one
GLSL first. But structure the code so HLSL/Metal/WGSL translations can sit alongside:

```
rasa/spanda/
├── moment.glsl      — GLSL
├── moment.hlsl      — HLSL  
├── moment.metal     — Metal
└── moment.wgsl      — WebGPU
```

### 7. Testable through visual examples
Each `test/*.glsl` is a standalone shader that demonstrates one function. These double as documentation and as regression tests.

---

## Build System

### Bundle script (`bundle.py`)
Inlines all `#include` dependencies into a single file. Supports `--platform glsl|hlsl|metal|wgsl` and `--minify`.

```bash
python bundle.py --include rasa \
    --output rasa-bundle.glsl \
    --platform glsl
```

### Prune script (`prune.py`)
Removes unused functions from a bundle. Walks the include tree from an entry point and drops everything not referenced.

```bash
python prune.py --entry my_shader.glsl --framework rasa/
```

---

## Relationship to LYGIA

The rasa framework is **not a replacement for LYGIA**. It's a **domain-specific layer on top**.

```
Your Shader
    │
    ├── #include "rasa/spanda/moment.glsl"     ← temporal structure
    ├── #include "rasa/tattva/color.glsl"       ← ontological depth
    │
    └── #include "lygia/sdf/circle.glsl"        ← geometry primitives
    └── #include "lygia/generative/fbm.glsl"    ← noise
    └── #include "lygia/color/palette.glsl"     ← color mixing
```

LYGIA draws the circle. Rasa decides *why* the circle appears at this moment, in this color, with this motion quality, moving through which ontological depth.

---

## What We Build First (v0.1)

```
rasa/v0.1/
├── version.glsl
├── rasa.glsl
├── spanda/
│   ├── moment.glsl       — udaya_sthiti_laya(t, freq)
│   ├── universal.glsl    — samanya_spanda(p, t)
│   └── intensity.glsl    — intensity_distribution(thisVal, thatVal, thisWeight)
├── tattva/
│   ├── state.glsl        — TattvaState struct
│   └── atLevel.glsl      — tattva_at_level(level)
├── rasa/
│   ├── mode.glsl         — RasaMode struct
│   └── palette.glsl      — 9 rasa color functions
├── bija/
│   ├── anuttara.glsl     — Supreme, unmanifest
│   └── kula.glsl         — The whole
└── test/
    ├── spanda_demo.glsl
    └── tattva_demo.glsl
```

~20 files, ~400 total lines. Sized for a single focused build session. Adds genuine functionality that LYGIA doesn't provide.

v1.0 adds: full sādhāraṇīkaraṇa pipeline, camatkāra climax system, pratibimba reflection structure, sāmarasya resolution, nanavira hierarchy, 9 rasa modes fully specified, 36-tattva color map, test suite.

---

## Why This Is Worth Building

There are ~500 GLSL frameworks on GitHub. None encode **temporal structure from a non-linear philosophy of time**. None map **ontological depth to visual density**. None embed **aesthetic-spiritual cognition theory into shader functions**.

This is a genuinely novel contribution: a GLSL framework whose function signatures encode Abhinavagupta's Tantraloka and Ñāṇavīra's Fundamental Structure into real-time graphics code. The functions would be usable by anyone who wants hierarchical time, density-based color, or emotional mode systems — regardless of whether they know the philosophy. And the philosophy is documented in the headers for those who want to go deeper.
