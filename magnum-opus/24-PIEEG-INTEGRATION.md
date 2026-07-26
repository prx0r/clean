# PiEEG + Satsang — Live Neurofeedback Meditation Platform

## The Vision

A meditation platform that reads your brain in real-time and adapts the teaching to what your brain is actually doing.

## Phase 1: Biofeedback (Now — No Stimulation)

User wears a PiEEG (8 or 16 channels). The Satsang app shows a live visualization of their brain state — not raw EEG, but meaningful metrics:

- **Attention index:** How focused vs. scattered
- **Alpha/theta ratio:** Deeper relaxation
- **Gamma power:** 40Hz band — the LH-LLM predicts this correlates with integrated information
- **Frontal asymmetry:** Approach/withdrawal balance
- **Avalanche exponent:** τ ≈ 1.5 — criticality measure. During jhāna, does it shift?

The guided meditation adapts in real-time:

```
User begins meditation
  → EEG shows high beta (scattered, normal waking)
  → Guide says: "Follow the breath. Notice the quality of attention."
  → Alpha rises
  → Guide says: "Good. Rest in that openness."
  → Theta appears — first jhāna boundary
  → Guide: "Now let go of the breath. Rest in the pleasant feeling itself."
  → Gamma increases — deep absorption
  → Guide: "Stay with it. Don't grasp. Let it support you."
  → System logs: 4-minute transition from beta to gamma, jhāna-like signature
  → Truth map update: session contributes to q:jhana-mechanisms, q:gamma-40hz-integration
```

Every session becomes data. Every user contributes to the research programme.

## Phase 2: Personalized State Detection

Over time, the system learns each user's unique EEG signature for different meditative states. No two people jhāna the same way. The system adapts:

- User A: high frontal gamma during access concentration → guide emphasizes pīti cultivation
- User B: theta bursts in posterior regions → guide emphasizes stillness
- User C: rapid alpha-to-gamma transition → guide skips preparatory stages

The Charioteer (from the Ouroboros architecture) selects the teaching strategy based on the user's live brain state, not their verbal report.

## Phase 3: Live Satsangs with EEG

Multiple users attend a live guided session. The teacher sees an aggregate dashboard — the group's brain states in real-time. When 80% of the room drops into coherent alpha, the teacher knows it's time to deepen the instruction. When someone's gamma spikes, the teacher can call on them: "What just happened for you?"

The session recording becomes content for the factory pipeline. The aggregate EEG data becomes a truth map entry. The individual's session log becomes part of their philosophy page — tracked over months, showing progress through states.

## Phase 4: Stimulation (With Caution)

Transcranial electrical stimulation (tES) — very low current (1-2mA) applied to specific scalp regions — can modulate brain states:

- **Anodal tDCS over frontal cortex:** Increases gamma, facilitates access concentration
- **tACS at 40Hz:** Entrains gamma oscillations — directly tests the LH-LLM's 40Hz binding hypothesis
- **tACS at theta (6Hz):** Facilitates hypnagogic-like states, dream-like imagery

This needs regulation, informed consent, and gradual deployment. Start with placebo-controlled protocols where neither the user nor the guide knows if stimulation is active. The double-blind data feeds the truth map directly — does 40Hz tACS actually increase subjective depth of meditation? Or is it placebo?

## Phase 5: The Experimental Platform

The PiEEG turns Satsang from a content platform into a **consciousness research laboratory with thousands of participants**:

| Experiment | What It Tests | Data Generated |
|-----------|--------------|----------------|
| Jhāna progression EEG signatures | Are jhānas distinct brain states or a continuum? | ~1000 sessions, labeled by self-report |
| 40Hz tACS during meditation | Does gamma entrainment increase absorption depth? | Double-blind, sham-controlled, ~200 sessions |
| Criticality during deep states | Does τ approach 1.5 during reported nondual experiences? | EEG avalanche exponents → truth map q:consciousness-criticality |
| Learning rate across sessions | How quickly do individuals progress through states? | Longitudinal tracking per user |
| Teacher effect | Does live guidance outperform recorded guidance in EEG outcomes? | Randomized trial: live vs. recorded |

## Hardware Cost

| Item | Cost | Source |
|------|------|--------|
| PiEEG-8 (8ch EEG shield) | ~$150 | pieeg.com |
| Raspberry Pi 4/5 | ~$50 | Anywhere |
| Electrodes (dry or gel) | ~$20-50 | Amazon |
| tDCS/tACS stimulator (Phase 4) | ~$100-200 | OpenBCI / DIY |
| **Total (passive)** | **~$220** | |
| **Total (with stimulation)** | **~$400** | |

## The Long Game

Satsang doesn't just produce content about meditation. It produces **meditators with quantified brain states**, tracked over years, whose data feeds the same truth map that the factory uses to decide what content to produce. The platform becomes a self-improving loop: users meditate → data flows → truth map updates → better content produced → users meditate deeper → more data flows.

The PiEEG is the hardware bridge between the truth map and actual human experience. Without it, the truth map only tracks what papers say about consciousness. With it, the truth map tracks what *actually happens* when real people practice.
