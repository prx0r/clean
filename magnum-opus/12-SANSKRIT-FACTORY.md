# Factory 5: Sanskrit — Spec

## Purpose

A Sanskrit philology factory that ingests Sanskrit literature, organizes it by date/lineage/school/topic, translates it using DeepSeek's 7-pass process, and produces **Translation Objects (TOs)** — versioned, audited translations with full chain of reasoning.

The TO is then available as source material for the Research Factory (RO creation) and as a live web object where scholars can compare alternative translations, comment, and submit their own.

---

## Key Insight

From sanskritree audit (2026-07-24): DeepSeek is capable of high-quality Sanskrit translation. The old factor-graph + sense-ranker pipeline was overly complex. The new approach is a 7-pass DeepSeek process that achieves 98.8% accuracy on Spandakarika.

**Old pipeline:** Factor graph → sense ranker → constrained LLM → translation  
**New pipeline:** DeepSeek 7-pass → translation → adversarial review → scholarly verification

The factory formalizes and scales this insight.

---

## Pipeline

```
Sanskrit Text (GRETIL, manuscript, scan)
  → 5a. INGEST — digitize, clean, format
  → 5b. CATALOGUE — date, lineage, school, topics, metadata
  → 5c. TRANSLATE — DeepSeek 7-pass process
  → 5d. VERIFY — adversarial review + comparative review
  → 5e. TO — Translation Object created (versioned, audited)
    → Feeds Research Factory as source material
    → Feeds Website as live translation browser
```

---

## 5a. INGEST — Text Acquisition & Cleaning

**Input:** Raw Sanskrit text (GRETIL, manuscript scans, digital editions)
**Output:** Clean, structured Sanskrit text with metadata

**Sub-process:**
```
Raw text → OCR (if scan) → Structural cleanup → BIS to standard → Verse/chapter segmentation → Linguistic preprocessing → Stored in sanskritree DB
```

**Current corpus (from sanskritree):**
| Work | Status | Coverage |
|------|--------|----------|
| Spandakārikā | ✅ Complete | 53/53 (98%) |
| Vijñānabhairava | ✅ Complete | 160/162 (99%) |
| Bhagavad Gītā | ⚠️ Partial | 1,138/3,089 (37%) |
| Bhairavastava | ✅ Complete | 9/9 (100%) |
| Tantrāloka (GRETIL) | ✅ Raw text | Available in texts/ |

**Planned additions (from phase plan):**
- Tarkasaṅgraha + Dīpikā (Nyāya-Vaiśeṣika)
- Spandanirṇaya (commentarial tantra)
- Bhāṣāpariccheda + Muktāvalī (Navya-Nyāya)
- Nyāyasūtra Book 1 + Vātsyāyana Bhāṣya
- Kiraṇatantra or Parākhyatantra (Śaiva Siddhānta)

---

## 5b. CATALOGUE — Metadata & Organization

**Input:** Clean Sanskrit text
**Output:** Structured metadata record

**Metadata schema:**
```json
{
  "text_id": "text:spandakarika",
  "title_sanskrit": "स्पन्दकारिका",
  "title_transliterated": "Spandakārikā",
  "title_english": "Stanzas on Vibration",
  "author": "Vasugupta (attr.)",
  "date": "~850-900 CE",
  "lineage": "Śaiva, Trika",
  "school": "Spanda",
  "tradition": "Kashmir Śaivism",
  "topics": ["spanda", "vibration", "consciousness", "self-awareness"],
  "related_texts": ["text:sivasutra", "text:vijnanabhairava"],
  "verses": 53,
  "language": "Sanskrit",
  "script": "Devanagari",
  "source": "GRETIL",
  "coverage_status": "complete",
  "translation_status": "v1.0_complete"
}
```

**Organization hierarchy:**
```
Tradition (e.g., Kashmir Śaivism)
  → School (e.g., Spanda, Pratyabhijñā, Krama)
    → Author (e.g., Vasugupta, Utpaladeva, Abhinavagupta)
      → Text (e.g., Spandakārikā, IPK, Tantrāloka)
        → Chapter/Āhnika
          → Verse/Kārikā
```

This enables:
- Browse by tradition, school, author, or text
- Find all texts on a topic (e.g., all texts about spanda)
- Chronological ordering within a school
- Cross-reference between related texts

---

## 5c. TRANSLATE — DeepSeek 7-Pass Process

**Input:** Clean Sanskrit text + metadata
**Output:** Full translation + concept map + revision notes

**The 7-pass process (from deepsanskrit.md):**

### Pass 1 — Global Translation
Give DeepSeek the work in coherent chapter-sized windows with title, author, historical context, preceding chapter summary, overlapping Sanskrit context, source metadata. Ask for the best translation it can produce. No forced literal first pass, no ban on commentary.

### Pass 2 — Whole-Work Understanding
After Pass 1, ask DeepSeek to construct: central doctrines, technical vocabulary, recurring metaphors, ritual structures, named deities and practices, internal cross-references, how concepts change by context, unresolved passages. This becomes a living model of the work.

### Pass 3 — Retrospective Revision
Give DeepSeek the full first translation, the whole-work concept map, later occurrences of important terms, and inconsistencies detected across chapters. Ask it to revise earlier passages now that it understands the whole work.

### Pass 4 — Corpus Investigation
Let the model generate its own research queries: find occurrences of a term, compare grammatical constructions, retrieve definitions, locate commentarial glosses, contrast usage across texts. The system executes those searches and returns evidence. DeepSeek decides what it needs to investigate.

### Pass 5 — Adversarial Review
Attack the translation: identify mistranslated compounds, find missing words, detect doctrinal assumptions, test alternative parses, compare Sanskrit and English clause by clause, challenge suspiciously fluent passages, search for internal contradictions. Primary translator responds and revises.

### Pass 6 — Comparative Review
Compare against Sanskrit commentaries, editions and apparatus, parallel passages, related tantras, partial scholarly translations, quotations in later literature. Do not automatically obey any one source — reason about disagreement.

### Pass 7 — Stylistic & Terminological Revision
Only after meaning stabilizes: improve English, harmonize recurring terminology where appropriate, preserve meaningful variation where the Sanskrit varies, add notes, distinguish supplied interpretation from explicit text.

---

## 5d. VERIFY — Quality Assurance

**Input:** Draft translation + all 7 pass outputs
**Output:** Verified translation with confidence scores

**Verification layers:**
1. **Automated checks:** Verse coverage (100%), terminology consistency, structural completeness
2. **Adversarial LLM review:** A different model (e.g., Claude) attacks the translation
3. **Scholarly review:** Subject matter expert reviews key passages (optional for gold-standard TOs)
4. **Community review:** Website visitors can flag issues (crowdsourced verification)

**Confidence scoring per verse:**
```json
{
  "verse": "1.1",
  "confidence": 0.95,
  "pass_1_quality": 0.88,
  "pass_5_adversarial_score": 0.92,
  "pass_6_comparative_agreement": 0.97,
  "pass_7_stylistic_score": 0.94,
  "issues": [],
  "alternatives": [
    {
      "phrase": "spanda",
      "translation": "vibration",
      "alternative": "pulsation",
      "reasoning": "Both valid. 'Vibration' preferred for scientific comparison, 'pulsation' for biological/embodied contexts.",
      "confidence": 0.9
    }
  ]
}
```

---

## 5e. TO — Translation Object

**Input:** Verified translation + all evidence
**Output:** Versioned Translation Object

**TO Schema:**
```json
{
  "to_id": "to:spandakarika-v1.0",
  "schema_version": 1,
  "text_id": "text:spandakarika",
  "title": "Spandakārikā — Stanzas on Vibration",
  "version": "1.0",
  "status": "verified",
  "translator": "DeepSeek 7-pass (Pass 1-7)",
  "human_reviewer": null,
  "date_completed": "2026-07-24",
  "verses": {
    "total": 53,
    "translated": 53,
    "verified": 53
  },
  "overall_confidence": 0.94,
  "provenance": {
    "source_text_version": "gretil_2024",
    "pipeline_version": "7-pass v1",
    "model": "deepseek-v4-flash",
    "pass_log": [
      {"pass": 1, "date": "2026-07-20", "status": "complete"},
      {"pass": 2, "date": "2026-07-21", "status": "complete"},
      {"pass": 3, "date": "2026-07-22", "status": "complete"},
      {"pass": 4, "date": "2026-07-22", "status": "complete"},
      {"pass": 5, "date": "2026-07-23", "status": "complete"},
      {"pass": 6, "date": "2026-07-23", "status": "complete"},
      {"pass": 7, "date": "2026-07-24", "status": "complete"}
    ]
  },
  "translation": [
    {
      "verse_number": "1.1",
      "sanskrit": "अथ शृण्वन्तु भद्रं वः सर्व एव समाहिताः ।",
      "transliteration": "atha śṛṇvantu bhadraṃ vaḥ sarva eva samāhitāḥ",
      "translation": "Now listen, all of you, with focused minds — may good fortune be yours.",
      "alternative_translations": [
        {
          "translator": "Dyczkowski",
          "translation": "Now, being all well-established (in this teaching), may good attend you; listen.",
          "notes": "More literal. 'Samāhitāḥ' as 'well-established' vs 'focused minds'.",
          "source": "The Stanzas on Vibration, SUNY 1992"
        },
        {
          "translator": "Singh",
          "translation": "Now listen all of you, being attentive. Auspicious be unto you.",
          "notes": "Simpler phrasing. 'Samāhitāḥ' as 'attentive'.",
          "source": "Spanda Karikas, 1980"
        }
      ],
      "notes": "Opening invocation. The imperative śṛṇvantu (listen) indicates oral transmission context.",
      "key_terms": [
        {"sanskrit": "samāhitāḥ", "translation": "focused minds", "alternatives": ["well-established", "attentive", "composed"], "confidence": 0.88}
      ],
      "confidence": 0.95,
      "pass_5_issues": []
    }
  ],
  "concept_map": {
    "spanda": "The central concept — primordial vibration/pulsation of consciousness",
    "sva-samvedana": "Self-awareness/self-reflexive consciousness",
    "...": "..."
  }
}
```

**Key features:**
- **Versioned**: Each TO has a version number. Updates create new versions.
- **Audited**: Every verse links back to the pass log and reasoning.
- **Alternative translations**: Competing scholarly translations included with reasoning.
- **Confidence per verse**: Not global — verse-level granularity.
- **Key terms tracked**: Every Sanskrit term has alternatives, confidence, and reasoning.

### Live Website Integration

The TO becomes a live web object at `/sanskrit/{text_id}`:

- **Default view**: Best translation (highest confidence) 
- **Toggle**: Switch between alternative translations per verse
- **Compare mode**: Side-by-side view of translations (DeepSeek vs Dyczkowski vs Singh)
- **Key terms**: Hover over any Sanskrit term to see alternatives, confidence, and reasoning
- **Scholar comments**: Registered scholars can:
  - Comment on specific verses
  - Vote on which translation is best with reasoned justifications
  - Submit their own alternative translations for specific verses
  - Build reputation over time (accuracy of their suggestions)
- **Full audit trail**: Every verse shows the chain of reasoning from Pass 1-7

This transforms the website from a content consumer into a **collaborative philology platform**.

---

## Integration with Research Factory

```
TO (Translation Object)
  → Direct source material for RO creation (no re-translation needed)
  → Alternative translations preserved as RO passages
  → Confidence scores inform RO quality metrics
  → Scholar comments feed into RO interpretation notes

Sanskrit Factory output → Research Factory 1b (EXTRACT)
  → Creates ROs from translated texts
  → ROs include translation notes and alternatives
  → EOs can reference specific translations
```

---

## Current State

| Component | Status |
|-----------|--------|
| Text corpus (5 works) | ✅ In sanskritree DB |
| 7-pass process design | ✅ Documented in deepsanskrit.md |
| Spandakārikā translation | ✅ v1.0 complete (98.8% accuracy) |
| Vijñānabhairava translation | ⚠️ Phase 2 in progress |
| TO schema | ❌ Needs implementation |
| TO directory | ❌ Needs creation |
| Website integration | ❌ Needs design |
| Scholar platform | ❌ Needs specification |

## Todo

- [ ] Create TO directory (`content/translation-objects/`)
- [ ] Formalize TO JSON schema
- [ ] Write Hermes skill `sanskrit-translate` that runs 7-pass process
- [ ] Write Hermes skill `sanskrit-catalogue` for metadata creation
- [ ] Complete Vijñānabhairava 7-pass translation
- [ ] Add Tarkasaṅgraha + Dīpikā (Phase 3)
- [ ] Design website UI for live translation browsing
- [ ] Design scholar comment/vote/contribute system
- [ ] Integrate TOs with Research Factory (automatic RO creation from new TOs)
