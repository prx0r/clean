# Formal Notes 2 — Concept Ontology Schema

## Core Insight

Sanskrit as a single canonical language is a trap. It privileges one tradition and distorts others. The solution: a canonical identifier in functional English, with language-qualified instances.

```
Concept
  - id: "absorption_state" (canonical ID — functional English)
  - instances:
      - term: "jhana"
        language: Pali
        tradition: Theravada
        definition: [from primary text]
      - term: "dhyana"
        language: Sanskrit
        tradition: Brahmanical_yoga
        definition: [different from jhana]
      - term: "shamatha"
        language: Tibetan
        tradition: Vajrayana
        definition: [overlaps with both]
```

No tradition's vocabulary colonises the others. The relationship between terms is explicit and queryable.

---

## The Schema — Two Entities Only

### FRAMEWORK

Every concept exists within a framework. You must define the framework before you can define any concept within it. The framework is the lens. Without it, words mean nothing.

| Field | Type | Description |
|-------|------|-------------|
| `framework_id` | string | snake_case, e.g. "advaita_vedanta_shankara" |
| `name` | string | "Advaita Vedanta (Shankara)" |
| `author` | string | Specific thinker if applicable |
| `tradition` | string | Broader tradition |
| `period` | string | "8th century CE" |
| `primary_texts` | string[] | Source texts this framework is drawn from |
| `language` | string | Original language |
| `authority_type` | enum | REVEALED \| RATIONAL \| EXPERIENTIAL \| EMPIRICAL \| MIXED |
| `notes` | string | Essential context before reading concepts |

**Authority types:**
- REVEALED = scripture/transmission
- RATIONAL = argument/logic
- EXPERIENTIAL = direct experience
- EMPIRICAL = observation/experiment
- MIXED = combination

### CONCEPT

| Field | Type | Description |
|-------|------|-------------|
| `concept_id` | string | snake_case. Format: `term_framework` |
| `canonical_term` | string | Term in original language |
| `transliteration` | string | Standardised romanisation |
| `translation` | string | Literal English only (not interpretive) |
| `framework_id` | string | Which framework this belongs to |
| `category` | enum | See Category Taxonomy below |
| `definition` | string | What this concept IS. From primary source, not interpretation. Precise, minimal, no metaphors unless in original. |
| `source_text` | string | Primary text the definition is drawn from |
| `source_locus` | string | Specific chapter/verse/section |
| `is_not` | string[] | **MANDATORY.** What this concept explicitly IS NOT. Minimum 3 entries. Each labelled with its source. Drawn from: (a) explicit statements in primary texts, (b) the author's own polemics, (c) common misreadings the tradition corrects. |
| `internal_variants` | string[] | Where does this concept vary WITHIN its framework? |
| `contested` | bool | Is the definition disputed within the tradition? |
| `contest_notes` | string | Who disputes it, how, and why |
| `related_concepts` | string[] | Other concept_ids within the SAME framework. No cross-framework links here. |

---

## Category Taxonomy

12 irreducible questions every framework must answer. Every concept belongs to one.

| Category | Question |
|----------|----------|
| GROUND | What is most fundamentally real? The ontological base. |
| SELF | What is a human being? The nature of the subject of experience. |
| COSMOS | How is reality structured? Layers, levels, dimensions. |
| CAUSATION | How do things affect other things? Principles of change. |
| PROBLEM | What (if anything) is wrong? Diagnosis of the human condition. (Optional) |
| PATH | What do you do about it? Method, practice, way. (Optional) |
| GOAL | What does resolution look like? Telos, liberation, completion. (Optional) |
| DEATH | What happens when the body dies? What continues? |
| EXPERIENCE | What states or stages arise in practice or in life? |
| PRACTICE | What do you actually do? Specific techniques, methods. |
| TRANSMISSION | How does knowledge pass between beings? Teacher-student, text, ritual, grace. |
| ETHICS | How should one act? The normative dimension. |

Some frameworks won't have PROBLEM, PATH, or GOAL — the category being absent is itself data.

---

## Example: Atman — Advaita Vedanta (Shankara)

```yaml
concept_id:         "atman_advaita_shankara"
canonical_term:     "Ātman"
transliteration:    "atman"
translation:        "self / breath / the essential principle of the individual"
framework_id:       "advaita_vedanta_shankara"
category:           SELF

definition:         "The innermost reality of the individual, identical with Brahman
                    (the ground of all reality). Pure undifferentiated awareness,
                    self-luminous, self-evident, not an object of knowledge but the
                    knowing itself. Not produced, not modified, not destroyed."
source_text:        "Upadesasahasri"
source_locus:       "Chapter 1 (Prose), verses 1-18"

is_not:
  - "NOT the ego or personal identity (ahankara) — these are products of avidya superimposed on Atman. [Source: Vivekachudamani v.136-140]"
  - "NOT a thing that can be known as an object — 'The knower cannot be known by itself as an object; the seer cannot be seen.' [Source: Brihadaranyaka Upanishad 3.4.2, Shankara's commentary]"
  - "NOT multiple — there are not many Atmans, one per person. Plurality is apparent, produced by maya. [Source: Brahmasutra Bhashya 2.1.14]"
  - "NOT the Buddhist anatta — Shankara explicitly argues against the Buddhist denial of self. For Shankara, the Buddha's 'no self' teaching applies to the false ego, not to the real Atman. [Source: Brahmasutra Bhashya 2.2.18-32]"
  - "NOT produced by meditation or practice — Atman is always already what one is. Liberation is recognition, not production. [Source: Upadesasahasri 1.18.3]"

internal_variants:
  - "Jivatman — Atman as apparently individualised through upadhi (limiting adjuncts). Conventionally real, ultimately identical to Brahman."
  - "Paramatman — Atman considered as the universal, identical with Brahman."

contested:          true
contest_notes:      "Ramanuja (Vishishtadvaita): Atman is real and distinct from Brahman,
                    related as attribute to substance, not numerically identical.
                    Madhva (Dvaita): Atman is genuinely distinct from Brahman, eternally so."

related_concepts:
  - "brahman_advaita_shankara"
  - "avidya_advaita_shankara"
  - "maya_advaita_shankara"
  - "jiva_advaita_shankara"
  - "moksha_advaita_shankara"
```

---

## Example: Anatta — Theravada (Pali Canon)

```yaml
concept_id:         "anatta_theravada_pali"
canonical_term:     "Anattā"
transliteration:    "anatta"
translation:        "non-self / not-self / without self"
framework_id:       "theravada_pali_canon"
category:           SELF

definition:         "The third characteristic of conditioned existence (alongside
                    anicca and dukkha). None of the five aggregates (khandhas) —
                    form, feeling, perception, mental formations, consciousness —
                    constitutes or contains a self. There is no persistent, unified,
                    autonomous agent behind experience."
source_text:        "Anattalakkhana Sutta"
source_locus:       "SN 22.59"

is_not:
  - "NOT the claim that 'nothing exists' or nihilism (uccheda-ditthi). The Buddha explicitly rejects nihilism alongside eternalism. [Source: SN 12.15, Kaccayanagotta Sutta]"
  - "NOT equivalent to Shankara's Atman being merely the ego — the Buddha refuses to say a real Atman underlies the ego. [Source: MN 72, Aggivacchagotta Sutta]"
  - "NOT a metaphysical claim about ultimate reality — it is a soteriological analysis. [Source: Steven Collins, Selfless Persons, Ch.3]"
  - "NOT the same as Nagarjuna's sunyata — Theravada anatta applies to persons. Nagarjuna extends the analysis to all dharmas. [Source: Analayo, comparative studies]"
  - "NOT a denial of conventional identity — conventionally, persons exist and are responsible for actions. [Source: Milindapanha, chariot analogy]"

internal_variants:
  - "Pudgalavada interpretation (rejected): the Pudgala school posited a 'person' not identical to the aggregates but not separate either."
  - "Strong vs weak anatta: Does anatta mean no self at any level or no PERMANENT self?"

contested:          true
contest_notes:      "Does anatta deny only a permanent, unchanging self? Or any self whatsoever?
                    Bhikkhu Analayo argues the Buddha's teaching is soteriological not metaphysical."

related_concepts:
  - "khandha_theravada"
  - "anicca_theravada"
  - "dukkha_theravada"
  - "nirvana_theravada"
  - "rebirth_theravada"
  - "avyakata_theravada"
```

---

## Design Principles

1. **One concept = one framework.** No cross-framework links in the concept record itself. Connections emerge naturally from comparing definitions once they exist.

2. **`is_not` is mandatory, sourced, and minimum 3 entries.** A definition without its negative space is incomplete. Every "not" must be traceable to a source. This prevents freeform opinion.

3. **`related_concepts` is same-framework only.** Forces understanding the internal logic before comparing. Atman relates to Brahman, Maya, Avidya within Advaita. That relationship system IS the framework's logic.

4. **Category is structural, not interpretive.** The same 12 questions get different answers. Categories don't change between frameworks.

5. **Build the definitions first.** When 200 concept nodes exist in this format, connections become obvious and scientific interfaces suggest themselves. Do not anticipate them.

6. **Fractal structure.** Each concept can be drilled into deeper granularity — the framework is the root, concepts are branches, and each concept can itself become a framework for sub-concepts.

---

## The Translation Layer

The typed relationship graph between concepts across frameworks:

| Relationship | Meaning |
|-------------|---------|
| CONVERGENT | Strong scholarly case for equivalence |
| POLEMICAL | Explicit argument against the other position |
| ANALOGICAL | Structural parallel, no historical contact |
| SUPERFICIAL | Looks similar, likely different structure |

Example: Śūnyatā → Wu: CONVERGENT (textual influence documented)
Example: Śūnyatā → Brahman: POLEMICAL (Nāgārjuna argues against ground)
Example: Śūnyatā → Godhead (Eckhart): ANALOGICAL (no historical contact)
