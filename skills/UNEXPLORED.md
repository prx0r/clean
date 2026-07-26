# Truth Map & Unexplored Features

## Part 1: The Truth Map — What It Actually Does

Right now the truth map is mentioned everywhere but concretely defined nowhere. Here's what it actually integrates into every factory:

### How the Truth Map Connects to Each Factory

**Factory 1 (Research):**
- **EXTRACT**: When creating an RO, the agent checks the truth map for relevant questions. If the source material bears on an underdetermined question, the RO gets tagged with that question_id. The RO's passages become evidence for or against.
- **SYNTHESIZE**: Every EO is created because the truth map has an underdetermined question. The EO's hypotheses are direct entries in the truth map's evidence_for / evidence_against arrays.
- **PROBE**: The hypothesis engine's sole input is the truth map. It scans for underdetermined questions, ranks them, proposes EOs. Without the truth map, the engine has no fuel.

**Factory 2 (Writing):**
- Every paper or essay that gets published should extract its claims and map them back to truth map questions. "This essay argues X. X is evidence_for question Q. Update the truth map."
- Currently: essays are written and published. They don't update anything. The truth map never learns from the output.

**Factory 3 (Video):**
- Same problem. Videos make claims. Those claims are evidence for or against truth map questions. Nobody tracks which video argued what.
- Videos also generate engagement data. If a video about a truth-map question gets high retention, that's data about audience interest in that question — which is not the same as truth, but is useful context.

**Factory 4 (Analytics):**
- This factory literally cannot function without the truth map. Its entire purpose is to update evidence weights and close the loop. Currently it has nothing to update because the truth map doesn't exist as a live object.

### The Missing Piece

The truth map is described as a JSON object with questions, evidence_for, evidence_against, status, confidence. But it needs:

1. **A home.** Where does it live? `content/source-metaphysics/questions.json`? D1 table? Both? The blog project pattern is file-based JSON with git versioning. The truth map should be the same — one JSON file per question, versioned in git, with a CI check that prevents contradictory updates.

2. **An update protocol.** When an EO is created, it adds evidence. When a paper is published, it adds evidence. When a video is released, it adds evidence. These are concurrent writers. Solution: append-only log of evidence statements. The "current state" of a question is computed from the full log, not stored as a mutable object.

3. **A staleness check.** Questions not updated in 90 days get flagged. The hypothesis engine deprioritizes them. If new source material appears, they re-enter the pool.

4. **A visualization.** The truth map should be publicly viewable — a dashboard showing every question, its status, evidence count, last updated. This becomes the project's face to the outside world. "These are the questions we're tracking, and here's what we know."

### What Needs to Be Built

- [ ] `content/source-metaphysics/` directory with one JSON file per question
- [ ] Append-only evidence log format (no editing, only adding)
- [ ] Truth map computation script (reads all evidence logs → computes current state per question)
- [ ] Truth map staleness checker (cron job, flags questions >90 days without new evidence)
- [ ] Factory 2 and 3 output hooks: when content publishes, extract claims → add to truth map
- [ ] Public truth map dashboard on the website

---

## The Object Hierarchy — Clarified

After reviewing the existing data model (`content/schemas/complete-data-model.md`), the hierarchy we need already exists — it just needs three small additions and one new layer.

### What Already Exists

```
CONCEPT (abstract)
  ├── Art (illustrates concept)
  ├── Concept Essay (compilation about concept)
  ├── Research Object (living compilation about concept) ← already called "living"
  │     └── Sources (works that provide passages)
  │           ├── Tier 1: Primary Source
  │           └── Tier 2: Commentary
  └── Book (collection of essays)
```

178 ROs, 1,796 essays, 76 concepts, 904 art objects — all linked by the glossary system. The web already exists.

### What's Missing (Small Fixes)

1. **Add `body_clean` to Works.** Currently Works are metadata-only (title, authors, DOI, etc.). They need the full cleaned source text as structured JSON. This turns a Work into a Source Object (SO). One 1-to-1 with the source text. Never updated after creation.

2. **Add `scope` field to ROs.** ROs currently don't distinguish between single-source extraction and multi-source collation. A `scope: "single_source" | "cross_source" | "cross_tradition"` field lets an agent know immediately whether an RO is a pure extraction (just the Enneads on daimon) or a synthesis (daimon across Neoplatonism). This subsumes the CO concept without creating a new object type.

3. **Git versioning for ROs.** ROs already have a `current_version` field. They're already called "living compilations." What's missing is a git commit hook that runs when an RO changes — so the RO history actually tracks its evolution. CI workflow, not a schema change.

4. **Quote budget by object type.** Each object type has a natural quote budget that decreases as you move up the hierarchy:

| Object | Scope | Quote Budget | Updated |
|--------|-------|-------------|---------|
| Work (with body_clean) | 1-to-1 with source | 100% | Never |
| RO (single_source) | One concept, one tradition | 70%+ source | Versioned |
| RO (cross_source) | One concept, multiple sources | 50-60% source | Versioned |
| RO (cross_tradition) | One concept, multiple traditions | 40-50% source | Versioned |
| Essay | Published output | 15-20% source | Static |

5. **One new layer: truth map.** Links ROs to questions. Not a new object type — just a new directory (`content/source-metaphysics/`) with one JSON file per question. Each file lists which ROs provide evidence for or against.

### What NOT to Build

- **EO (Essay Object).** Unnecessary. The bridge between RO and production is the Essay, which already exists. An RO with `scope: "cross_tradition"` IS the EO concept. No new object type needed.
- **CO (Comparison Object).** Subsumed by RO with `scope: "cross_source"` or `scope: "cross_tradition"`.
- **SO (Synthesis Object).** Subsumed by RO with `scope: "cross_tradition"`. The existing directory is empty for a reason — nobody needed it.

## Part 2: Unexplored Features

### From the Visionary Doc (Not Yet Spec'd)

| Feature | Where It Was Mentioned | What's Missing |
|---------|----------------------|----------------|
| **Collaborative Scholar Platform** | 14-VISIONARY.md | TO browser with comments, scholar reputation system, "GitHub for Sanskrit philology." Never spec'd beyond a paragraph. |
| **Experiment Engine** | 14-VISIONARY.md | Given an EO with competing hypotheses, propose a falsifiable experiment. Never designed. |
| **Tertiary Literature Engine** | 14-VISIONARY.md | Auto-generated living Wikipedia page per truth-map question, regenerated from evidence. Never designed. |
| **Cross-Tradition Bridge Engine** | 14-VISIONARY.md | Find structural correspondences across traditions automatically. Blog does this manually. No formal engine. |
| **Embodied Practice Pipeline** | 14-VISIONARY.md | TOs → guided meditation audio tracks. Never designed. |
| **Reputation Economy** | 14-VISIONARY.md | Trust points, citation tracking for scholar contributions. Never designed. |
| **Offline/Mesh Mode** | 14-VISIONARY.md | Runs on a laptop with Ollama. Never designed. |
| **Funding Layer** | 14-VISIONARY.md | Grants, API sales, donations. Never designed. |

### From the Main Spec (Not Yet Built)

| Feature | Where | What's Missing |
|---------|-------|----------------|
| **Truth Map** | Everywhere | No directory, no update protocol, no staleness check. The single biggest gap. |
| **EO Directory** | 04-ESSAY-OBJECTS.md | `content/essay-objects/` doesn't exist. Zero EOs have ever been created. |
| **Hypothesis Engine** | 07-HYPOTHESIS-ENGINE.md | No cron job, no ranking algorithm, no proposal format. |
| **Sanskrit TO Directory** | 12-SANSKRIT-FACTORY.md | `content/translation-objects/` doesn't exist. Only one TO exists (Spandakarika). |
| **Quote Budget Gates** | FACTORY-SPEC.md | No validation scripts exist for quote-word-count / total-word-count ratio. |
| **Source Metaphysics Dashboard** | Never | No public view of the truth map. No one outside the project can see what questions are being tracked. |

### Things We've Never Even Discussed

**1. The Content Review DAO**
A decentralized group of trusted reviewers who vote on content quality before publication. Each reviewer stakes reputation. If they approve something that performs poorly, they lose reputation. If they approve something that performs well, they gain reputation. This turns content review from a bottleneck into a game.

**2. The Personalization Engine**
Not an algorithm — a user-declared preference system. "I want to see content at the intersection of Kashmir Shaivism and predictive processing." The system builds a feed from available EOs that match. Every user gets a unique research programme. This is already half-designed in the GreenScreen spec but hasn't been connected to the factory pipeline.

**3. The Live Translation Events**
Sanskritree sessions streamed live. A scholar reads a verse. The audience sees the 7-pass translation process in real-time. Each pass reveals more of the text's meaning. Viewers can propose alternative translations in chat. The best ones get incorporated into the TO. This is content AND research happening simultaneously.

**4. The Audio-First Pipeline**
Every essay, every RO, every EO should have an audio version. Not TTS — a proper narrated version with pacing, emphasis, and musical interludes. Voicebox makes this feasible. Currently the pipeline produces text first, audio as an afterthought. Flip it: produce audio first, text as the transcript.

**5. The Feedback-as-Training-Dataset Loop**
Every piece of feedback on the studio (user says "make the glow warmer") is logged. Over time, this becomes a training dataset for a preference model. The model learns "when the user says 'warmer,' they mean increase glow_warmth from current value by 0.15-0.25." Eventually the agent can anticipate adjustments before the user asks.

**6. The Scholarship Fund**
100% of ad revenue from the video content goes to a scholarship fund for Sanskrit students. This is mentioned in the GreenScreen attention budget but never connected to the factory pipeline. If the factories produce revenue, where does it go? Answering this now prevents future awkwardness.

**7. The Plugin Architecture**
The factory pipeline is tightly coupled to the blog project's specific tools (PIL, FableCut, Hermes). If someone wanted to use a different renderer, or a different AI provider, or a different video editor — they'd have to fork the whole thing. A plugin architecture (each stage is a replaceable module with a standard interface) would make the system extensible. Currently not designed.

**8. The Self-Correction Protocol**
If an EO's hypothesis is tested and found wrong, what happens? Currently: nothing. The EO stays in the directory, the truth map says "underdetermined." There's no mechanism for closing a question with "this hypothesis was tested and is likely false." The system can only accumulate evidence, never conclude. A conclusion protocol would mark a question as "answered" and move it to a reference archive. New EOs can still reference it, but the hypothesis engine won't propose it.

### Priority Order (What to Actually Build Next)

1. **Truth Map** — without this, there's no closed loop. Everything else is downstream.
2. **EO Directory** — without EOs, the bridge between research and production doesn't exist.
3. **Quote Budget Gates** — without these, the writing skills produce unreliable output.
4. **Live Translation Events** — highest-impact, lowest-effort. Streaming is cheap. Content is unique.
5. **Feedback-as-Training** — turns the HITL review loop into a long-term asset.
6. **Conclusion Protocol** — necessary for the system to converge on knowledge rather than accumulating infinite uncertainty.
7. **Audio-First Pipeline** — differentiates the content in a crowded video space.
8. **Plugin Architecture** — only matters if someone else wants to use the system. Not urgent.
9. **Scholarship Fund** — only matters once there's revenue to distribute.
10. **Collaborative Scholar Platform** — only matters once there's a community to use it.
