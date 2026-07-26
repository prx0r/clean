# Skills — Complete Map to Factories

Every Hermes skill, categorized by factory, with purpose, variants needed, and current status.

---

## Factory 1: Research — Source → RO → EO → Truth Map

| Skill | Variant | Purpose | Status |
|-------|---------|---------|--------|
| `acquire` | — | Download papers via DOI/URL → create Work JSON | ✅ exists |
| `search` | — | Map esoteric concepts to modern research domains | ✅ exists |
| `explore` | — | Cross-silo search across all content | ✅ exists |
| `navigate` | — | Knowledge graph connections browser | ✅ exists |
| `curate` | — | RO creation and management | ✅ exists |
| `synth` | — | Answer synthesis from internal docs | ✅ exists |
| `cron-acquire` | — | Tier 2 daily auto-acquisition | ✅ exists |
| **`research-object-creator`** | NEW | Automate RO creation from Work JSON → structured passages | ❌ needed |
| **`essay-object-creator`** | NEW | Combine ROs → EO with hypotheses + tension points | ❌ needed |
| **`source-metaphysics`** | NEW | Truth map maintenance: update evidence weights, staleness checks | ❌ needed |
| **`dataset-acquire`** | NEW | OpenNeuro S3 dataset downloads | ❌ needed |
| `sanskritree` | runs separately | Sanskrit NLP pipeline (7-pass translation) | ✅ independent |

---

## Factory 2: Writing — EO → Paper / Essay

| Skill | Variant | Purpose | Status |
|-------|---------|---------|--------|
| `write` | **TYPE A: Essay** | 3-pass essay from source (Dump → Refine → Shape) | ✅ exists |
| `publish` | **TYPE B: Paper** | Format existing text as JSON + audio | ✅ exists |
| `source-to-essay` | — | Extract from source → structured essay | ✅ exists |
| `writing/audio` | — | TTS + multi-voice audio generation | ✅ exists |
| `writing/art` | — | Art matching for essay passages | ✅ exists |
| **`write/ro`** | NEW | **RO writing skill** — Pure extraction, 0% AI commentary. Task: given a source text, extract structured passages by theme, organize into RO format. No interpretation, no paraphrasing, no synthesis. Validation: every passage is a direct quote or close paraphrase with source_id. |
| **`write/eo`** | NEW | **EO writing skill** — Synthesis from multiple ROs. Task: given 2+ ROs and a research question, produce an EO with tension points, competing hypotheses, and source metaphysics update. Quote budget: 40% source, 60% analysis/comparison. Validation: all hypotheses reference specific RO passages. |
| **`write/essay`** | NEW | **Public essay skill** — Polished, accessible long-form. Like the current 3-pass but with decreasing quote budget: P1 ≤70%, P3 final ≤15-20% with per-source cap (no single source quoted >1x in final pass). Validation: quote-word-count/total-word-count gate at each pass. |
| **`write/video-script`** | NEW | **Narrative script skill** — Script with timing + visual cues for video factory. Quote budget: ≤10% source, 90% original narrative prose. Validation: every scene has a corresponding visual mode or GLSL shader reference. |
| **`peer-review`** | — | Multi-agent structured paper review (6 dimensions) | ✅ exists |

### Quote Budget by Variant

| Variant | P1 Max | P3 Final | Per-Source Cap | Purpose |
|---------|--------|----------|----------------|---------|
| RO | 100% | 100% | unlimited | Pure extraction, no commentary |
| EO | 60% | 40% | 3 quotes/source | Synthesis with analysis |
| Essay | 70% | 15-20% | 1 quote/source | Polished public writing |
| Video Script | 30% | ≤10% | 1 quote/source | Narrative, not reference |
| Paper | 40% | 25% | 2 quotes/source | Academic writing |

### Writing Skill — Concrete Fixes (from review)

1. **Quote budget as a hard gate, not a vibe.** Add an explicit P1 validation gate that measures `quote_word_count / total_word_count` and fails if it exceeds the variant's limit.

2. **Per-source cap.** 70% spread across 12 sources is fine. 70% from one source is a summary, not an essay. Gate on `max_quote_per_source` too.

3. **Pass 2 applies to quoted material too.** The "replace abstraction with concrete image" rule currently only touches AI commentary. Quoted material must also get the same treatment — which means the 70% shrinks naturally because you can't justify keeping a quote that fails the concreteness test.

4. **Failure fallback.** After 3 retries: do NOT deploy. Default state is "do not deploy." The file should be moved to a quarantine directory, not left in the publishing pipeline where a subsequent process might pick it up.

5. **Different skills for different outputs.** RO writing is 100% extraction. EO writing is 40% source, 60% analysis. Essay writing is 15-20% source in final pass. Video script is ≤10% source. These need separate skills with different quote budgets and validation gates.

---

## Factory 3: Video — EO → Storyboard → Render → Export

| Skill | Variant | Purpose | Status |
|-------|---------|---------|--------|
| `platinum-designer` | — | Gold study → rhetorical map → visual thesis → storyboard | ✅ exists |
| `platinum-renderer` | — | Storyboard → PIL scene functions → render → QC | ✅ exists |
| `factory-pipeline` | — | 5-stage content pipeline orchestration | ✅ exists |
| `publish-video-fablecut` | — | Storyboard → voiceover → art → FableCut → export | ✅ exists |
| `video/publish-video` | — | Video publishing pipeline | ✅ exists |
| **`scene-review`** | NEW | HITL feedback loop: scene preview → user feedback → agent adjusts → re-render | ❌ needed |
| **`shader-creator`** | NEW | Write new GLSL shaders from visual descriptions | ❌ needed |
| **`audio-design`** | NEW | Music selection, audio mixing, voice cloning (Voicebox) | ❌ needed |

---

## Factory 4: Analytics — Products → Metrics → Truth Map

| Skill | Variant | Purpose | Status |
|-------|---------|---------|--------|
| `daily-research` | — | YouTube niche monitoring (75 channels) | ✅ exists |
| `market-scan` | — | Niche gap analysis, opportunity scoring | ✅ exists |
| `engines/headline` | — | Headline scoring engine | ✅ exists |
| `deep-analysis` | — | Data analysis (installed in Hermes) | ✅ exists |
| **`performance-track`** | NEW | Track video/paper performance → update truth map evidence | ❌ needed |
| **`hypothesis-test`** | NEW | Compare content performance against EO hypotheses | ❌ needed |

---

## Cross-Cutting / Other

| Skill | Variant | Purpose | Status |
|-------|---------|---------|--------|
| `peer-review` | — | Multi-agent paper review (6 dimensions) | ✅ exists |
| `teach` | — | TetraHermes teaching pipeline | ✅ exists |
| `astrology/deep-analysis` | — | Astrology research | ✅ exists |
| `daimon/daily-reading` | — | Daily daimon reading | ✅ exists |
| `daimon/weekly-review` | — | Weekly daimon review | ✅ exists |
| `practice/recommend-practice` | — | Contemplative practice recommendation | ✅ exists |
| `practice/schedule-ritual` | — | Ritual scheduling | ✅ exists |
| `ops/deploy` | — | Site deployment | ✅ exists |
| `site/art` | — | Art site management | ✅ exists |
| `yogi-spotlight` | — | Yogi content spotlight | ✅ exists |

---

## Summary

| Factory | Existing Skills | Skills Needed |
|---------|----------------|---------------|
| Research | 7 | 4 (RO creator, EO creator, source-metaphysics, dataset-acquire) |
| Writing | 5 | 4 (RO variant, EO variant, video-script variant, plus quote-budget fixes) |
| Video | 5 | 3 (scene-review, shader-creator, audio-design) |
| Analytics | 4 | 2 (performance-track, hypothesis-test) |
| Cross | 10 | 0 |

**Total: 31 skills exist. 13 new skills needed.**
