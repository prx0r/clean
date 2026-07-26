# Development Roadmap

Ordered by dependency — each phase unlocks the next.

---

## PHASE 0: Foundation (Now)

The core loop must work before anything else matters.

### 0.1 Truth Map (6 questions seeded)
**Status:** ✅ Done — `content/source-metaphysics/` with 6 questions
**Next:** Add the append-only evidence log format, confidence computation script, staleness cron

### 0.2 Studio Timestamp Capture
**Status:** ✅ Done — comments now capture pause timestamp, API accepts `timestamp_seconds`, existing timestamped comments are clickable
**Next:** Deploy (needs node 22+)

### 0.3 Publish Gate
**Status:** ✅ Done — Hermes publish skill now requires mapping claims to truth map questions
**Next:** Enforce — when the gate blocks a publish, create the missing truth map entry automatically

### 0.4 One Manual EO
**Status:** ❌ Not started
**Why:** Validates that the RO → EO concept works before automating it
**Time:** 1 day
**Action:** Pick a tension point (icchā-jñāna-kriyā vs active inference), write one EO manually with hypotheses, evidence, and source ROs

### 0.5 Truth Map Dashboard
**Status:** ❌ Not started
**Why:** The public face of the research programme. A simple page showing all questions, statuses, and linked content.
**Time:** 2 days
**Action:** HTML page that reads `content/source-metaphysics/` and renders a table

---

## PHASE 1: Core Loop (Weeks 1-4)

The publish gate forces every piece of content to answer a question. Now make that loop fast.

### 1.1 RO → EO Pipeline
**Action:** Create the `essay-object-creator` Hermes skill that takes ROs + a tension point and produces an EO with hypotheses
**Gate:** Manual EO from 0.4 must have proven the concept works

### 1.2 EO → Essay Pipeline
**Action:** Create the `essay-from-eo` Hermes skill variant that takes an EO and runs the 3-pass write (with quote budget gates enforced)
**Gate:** EO directory must exist with ≥3 EOs

### 1.3 EO → Video Pipeline
**Action:** Create the `video-from-eo` Hermes skill that takes an EO and runs the platinum pipeline
**Gate:** ≥3 EOs must exist

### 1.4 Truth Map Update on Publish
**Action:** Both essay and video publish scripts must update the truth map — add the content as evidence for the claims it makes
**Gate:** Publish gate must be running (0.3)

---

## PHASE 2: The Dreaming Loop (Weeks 5-8)

Now that content is being produced and feeding back into the truth map, add the overnight consolidation.

### 2.1 Truth Map Staleness Cron
**Action:** Weekly cron that flags questions not updated in 90 days, archives dead ones
**Gate:** ≥50 truth map entries

### 2.2 Evidence Log Consolidation
**Action:** Nightly script that reviews temporary evidence entries (from new ROs, essays, videos), promotes high-confidence ones, discards duplicates
**Gate:** ≥100 evidence entries in the log

### 2.3 Gap Analysis
**Action:** Nightly script that finds truth map questions with no ROs, generates ACQUIRE missions
**Gate:** Truth map must be actively used for ≥1 month

### 2.4 Critic Agent (First Gate)
**Action:** Add Critic agent to the EO proposal stage — before an EO enters production, the Critic tries to falsify its central hypothesis
**Gate:** EO pipeline must be running (1.1)

---

## PHASE 3: The Platform (Months 3-6)

Now the pipeline works. Open it to other people.

### 3.1 Satsang.digital — User Accounts
**Action:** Basic auth, philosophy pages (traditions, teachers, values), watch history, Q-score tracking
**Gate:** ≥50 EOs, ≥20 videos published

### 3.2 Feed Algorithm v1
**Action:** User-controlled feed builder — topic selection, creator prioritization, blocking. No black box.
**Gate:** ≥100 videos on the platform

### 3.3 Truth Market v1
**Action:** Users stake reputation on truth map questions. Propagation engine is the oracle.
**Gate:** Truth map must be actively maintained for ≥3 months

### 3.4 Reputation Tiers
**Action:** Unlock features based on Q-score — question priority, source submission, translation voting, truth map confidence voting
**Gate:** ≥100 active users

---

## PHASE 4: Sanskrit Factory (Ongoing)

Runs in parallel with everything above — doesn't block the earlier phases.

### 4.1 TO Pipeline
**Action:** Formalize Translation Objects from the 7-pass DeepSeek process. Create `content/translation-objects/` directory.
**Status:** Spandakarika v1.0 exists. Needs formalization.

### 4.2 Vijnanabhairava Completion
**Action:** Complete the Vijnanabhairava translation (160/162 verses done)
**Gate:** TO pipeline formalized

### 4.3 Tarkasangraha Phase
**Action:** First non-tantric text — Nyāya-Vaiśeṣika manual. Tests whether the 7-pass generalizes beyond tantra.
**Gate:** Minimum 2 TOs in the formal pipeline

### 4.4 TO Browser (Satsang)
**Action:** Live translation browser on Satsang — scholars can compare alternatives, comment, vote
**Gate:** ≥5 TOs published

### 4.5 Rasa Institute — First Print Run
**Action:** Print the first critical edition with scholar apparatus. Funded by pre-orders + video revenue.
**Gate:** ≥5 TOs with ≥6 months of community review

---

## PHASE 5: Tradition Worlds (Months 6-18)

VR-adjacent now, full VR later.

### 5.1 2D Interactive Maps
**Action:** Each major tradition gets a navigable 2D web map (Trika tattva descent, Neoplatonic spheres, Sufi garden, Tantric body)
**Gate:** Satsang platform must be live (Phase 3)

### 5.2 Digital Satsangs
**Action:** Live-streamed study groups with shared objects of attention (verse being translated, question being investigated)
**Gate:** ≥5 engaged scholar-contributors on the platform

### 5.3 VR Prototypes
**Action:** One tradition world in WebXR (start with Trika — 36-level tattva descent)
**Gate:** 2D maps validated with real user traffic

---

## PHASE 6: The Long Tail (Months 12+)

Things that matter once the system is running.

### 6.1 Multi-User Question Chain
Users' questions form dependency trees — "your question led to 12 further questions and 4 videos." Visualized as dependent origination.

### 6.2 Truth Market as Prediction Platform
External researchers can stake on truth map questions. The odds become a public signal of where the evidence is heading.

### 6.3 Scholarship Fund from Video Revenue
Every view contributes to Sanskrit student scholarships. Visible counter on every video.

### 6.4 Rasa Institute Grant-Funded Series
First series funded by pre-orders. Second series by grants from Templeton, Mind & Life, Fetzer.

### 6.5 Full VR Tradition Worlds
All six tradition worlds navigable in VR. The meta-world connecting them at their conceptual boundaries.

---

## Dependency Summary

```
Phase 0 (Foundation)
  └── Phase 1 (Core Loop)
       ├── Phase 2 (Dreaming Loop)
       │    └── Phase 5 (Tradition Worlds, some)
       └── Phase 3 (Platform)
            ├── Phase 4 (Sanskrit Factory, parallel)
            │    └── Phase 5 (Tradition Worlds, rest)
            └── Phase 6 (Long Tail)
```

Phase 0 doesn't depend on anything except existing code. Phase 1 depends on Phase 0. Phase 2 depends on Phase 1 running for a month. Phase 3 depends on Phase 1 producing content. Phase 4 runs in parallel with everything. Phases 5 and 6 depend on the platform existing.
