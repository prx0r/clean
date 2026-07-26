# Hermes Skills — Complete Reference

All skills in /root/projects/blog/hermes/skills/. Each has a SKILL.md defining its purpose, workflow, and validation gates.

---

## Core Skills (hermes/skills/core/)

| Skill | Purpose |
|-------|---------|
| `acquire` | Paper acquisition pipeline. Takes DOI/title/URL → resolves via Crossref/OpenAlex/Unpaywall → finds OA copy → downloads → validates → creates Work JSON. Can fall back to user-assisted download via Telegram when VPS is IP-blocked. |
| `cron-acquire` | Tier 2 auto-acquisition. Runs daily to discover new papers for tracked concepts. |
| `curate` | Research Object management. Create, update, link ROs. |
| `explore` | Cross-silo search across ROs, works, essays, art, concepts. |
| `search` | Esoteric-to-science concept mapping. Maps astrological/esoteric concepts to modern research domains. |
| `synth` | Answer synthesis from internal docs. Given a question, searches all content and synthesizes an answer. |
| `navigate` | Knowledge graph browser. Shows connections between concepts, ROs, works, essays, art. |
| `publish` | Type B: mechanical paper publishing. Format existing text as JSON + audio. |
| `teach` | TetraHermes teaching pipeline. |
| `factory-pipeline` | 5-stage content pipeline (source → work → RO → essay → storyboard → video). Orchestrates the platinum video process. |

---

## Domain Skills

| Skill | Purpose |
|-------|---------|
| `writing/write` | **Type A: 3-Pass Essay Writing.** Dump → Refine → Shape. The primary essay generation skill. Uses validation gates at each pass. See full output below. |
| `writing/audio` | Audio generation for essays. TTS + multi-voice mixing. |
| `writing/art` | Art matching for essays. Finds relevant art from the glossary for each passage. |
| `source-to-essay` | Content pipeline. Extracts from source material → produces structured essay. |
| `platinum-designer` | PASS 1 of video production. Studies gold exemplars, designs rhetorical map, builds visual thesis, authors storyboard. |
| `platinum-renderer` | PASS 2 of video production. Reviews storyboard, writes PIL scene functions, renders, validates. |
| `publish-video-fablecut` | Full video pipeline: storyboard → voiceover → art search → quote cards → FableCut timeline → export. |
| `daily-research` | YouTube niche monitoring. Tracks 75 channels across source/authority/narrative roles, daily upload signals, breakout scoring. |
| `market-scan` | Niche gap analysis. Computes opportunity scores, language lag, breakout rates. |
| `astrology/deep-analysis` | Astrology research and analysis. |
| `daimon/daily-reading` | Daily daimon reading generation. |
| `daimon/weekly-review` | Weekly daimon review. |
| `practice/recommend-practice` | Contemplative practice recommendation. |
| `practice/schedule-ritual` | Ritual scheduling. |
| `ops/deploy` | Site deployment operations. |
| `site/art` | Art site management. |
| `engines/headline` | Headline scoring engine. |
| `peer-review` | **Scientific paper peer review. Multi-subagent, split-then-aggregate.** 6 independent dimension passes (Soundness, Originality, Substance, Replicability, Clarity, Comparison) → aggregated into structured review with recommendation. Based on MARG multi-agent review (D'Arcy et al. 2024). |
| `yogi-spotlight` | Yogi content spotlight. |
