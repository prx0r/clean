# The Truth Market — Prediction Markets for Epistemic Progress

## Concept

Every truth map question becomes a prediction market. Users stake reputation (or a platform currency) on which direction the evidence will move. This turns epistemology into a live, incentivized game and generates the most honest signal possible about where the evidence is heading.

## How It Works

### 1. Questions Become Markets

Every truth map question with status `underdetermined` or `plausible` gets a prediction market:

- q:consciousness-fundamental — Current confidence: 0.4
- q:iccha-jnana-kriya-necessary — Current confidence: 0.35
- q:brain-filter-or-appearance — Current confidence: 0.3

Each market has a binary or range outcome:

**Binary:** "Will F1 (consciousness_fundamental) reach confidence ≥ 0.7 within 12 months?" Yes/No.

**Range:** "What will F1's confidence be in 6 months?" 0.0-0.2 / 0.2-0.4 / 0.4-0.6 / 0.6-0.8 / 0.8-1.0

### 2. Users Stake Reputation

Users put reputation (earned through asking questions, submitting sources, writing comments, etc.) on the outcome:

> User A: "I predict F1 reaches 0.7. I stake 50 reputation on Yes."
> User B: "I predict it stays below 0.7. I stake 30 reputation on No."

The market odds update dynamically based on the stake ratio.

### 3. Evidence Is the Oracle

The truth engine IS the oracle. When new evidence enters the system (a new RO, a published essay, a completed video), the propagation engine recomputes the feature posteriors. If confidence crosses the threshold, the market resolves.

This is the critical design constraint: **the oracle is not a human judge. It's the propagation engine processing real evidence.** No one can manipulate the outcome by voting — only by producing actual evidence that changes the Bayesian posterior.

### 4. Resolution and Payout

When the resolution date arrives or the threshold is crossed:

- Correct predictors get their stake back + a share of the losing side's stake, minus a platform fee
- The platform fee goes to the attention budget (funding more research)
- The predictor's reputation score updates: correct predictions increase it, incorrect ones decrease it

---

## Terms and Conditions (T+C)

### 1. Eligibility

1.1. Any user with a Satsang account in good standing may participate.
1.2. Users must have earned at least 10 Q-score (from asking questions that led to content) to stake reputation.
1.3. Users may not stake more than 50% of their total reputation on any single market.

### 2. What Constitutes Falsifiable Evidence

2.1. **Evidence is defined as a claim record in the truth engine database** — a structured entry with:
   - Source ID (linking to an RO, essay, video, or experiment)
   - Target feature (which F1-F8 the evidence bears on)
   - Log Bayes factor (how much the evidence moves the posterior)
   - Weight factors (w_rel, w_map, w_aux, w_dep)
   - Paradigm tag (to compute dependence discounting)
   - Falsifier field (what would disprove this claim)

2.2. **Qualifying evidence sources:**
   - ✅ Peer-reviewed experimental studies (w_rel ≥ 0.7)
   - ✅ Adversarial collaborations (w_rel ≥ 0.85)
   - ✅ Direct phenomenological reports from advanced practitioners (w_rel ≥ 0.5, requires verification)
   - ✅ Systematic meta-analyses (w_rel ≥ 0.8)
   - ✅ Primary Sanskrit text translations via the 7-pass pipeline (w_rel ≥ 0.6)
   - ❌ Single anecdotes without verification
   - ❌ Non-falsifiable metaphysical claims without empirical component
   - ❌ Evidence from retracted studies

2.3. **The oracle is the propagation engine.** Market resolution is determined by the engine's computation of feature posteriors, not by human judgment. The engine reads all claim records in the database, applies the Bayesian update rules (sigmoid, log-odds, paradigm dependence discounting), and outputs the posterior probability.

2.4. **Pre-registration required.** Evidence must be pre-registered (submitted to the truth map) before the prediction deadline. Post-hoc evidence — evidence submitted after the market resolution date — does not count.

### 3. Market Resolution

3.1. Markets have a fixed resolution date (typically 6 or 12 months from opening).
3.2. A market may also resolve early if the threshold condition is met and confirmed by the propagation engine.
3.3. If the propagation engine fails to produce a determinate result (e.g., no evidence was entered during the period), the market resolves as "no result" and all stakes are returned.
3.4. Disputes are resolved by the platform's moderation council, who can inspect the evidence record and propagation engine state.

### 4. Reputation Staking

4.1. Reputation is non-transferable — it cannot be bought, sold, or exchanged for currency.
4.2. Reputation is earned through: asking questions that lead to content, submitting verified source materials, writing peer reviews, contributing alternative translations, and voting on moderation decisions.
4.3. Staked reputation is locked for the duration of the market and cannot be used for other bets simultaneously.
4.4. If a user's reputation falls below a threshold, they cannot stake on new markets until they earn more through contributions.

### 5. Market Integrity

5.1. **No self-dealing.** Users may not stake on both sides of the same market.
5.2. **No insider trading.** Users with advance knowledge of incoming evidence (e.g., as reviewers or translators) may not stake on affected markets until the evidence is published.
5.3. **Evidence front-running.** If a user stakes heavily on a market and immediately submits evidence that moves it in their favor, the stake may be forfeit and the evidence flagged for review.
5.4. **Market manipulation.** Coordinated staking across multiple accounts to artificially move odds is prohibited and results in reputation forfeiture and account suspension.

### 6. Fee Structure

6.1. The platform takes 10% of the losing side's stake pool.
6.2. The remaining 90% is distributed to winners proportionally to their stake.
6.3. The platform fee funds: research operations, evidence acquisition, translation pipeline costs, and infrastructure.

---

## The VR Connection

From hxrmxs/endgame.txt: every web interaction is a VR proxy. Mouse hesitation maps to hand-tracking hesitation. Scroll behavior maps to approach distance. Click decisions map to spatial choices.

**For the truth market:** The market dashboard could eventually be a VR space where each truth map question is a physical room. You walk toward the room whose question interests you. The room's walls show the current evidence for and against. You stake reputation by placing a token on a pedestal. Other users' stakes glow in proportion to their size. The propagation engine updates are visualized as light pulsing through the floor from evidence nodes to feature nodes.

But the web version works first, and every interaction is designed to map directly to the VR version:

| Web Interaction | VR Equivalent |
|----------------|---------------|
| Click question node | Walk toward that room |
| Hover over evidence | Gaze at evidence panel |
| Drag to stake slider | Place token on pedestal |
| Scroll evidence log | Walk along timeline |
| Click resolution | Confirm with hand gesture |

The VR version is a spatial truth map. The web version is the cheap prototype that validates the interaction patterns before building 3D environments.

---

## Why This Works

1. **It aligns incentives.** Users who want to earn reputation have to engage with the evidence honestly. The only way to win is to correctly predict where the evidence is heading. Wishful thinking loses reputation.

2. **It generates a prediction signal.** The market odds are a real-time estimate of where the evidence is heading, aggregating the judgment of everyone following the question. This is more reliable than any single expert's opinion.

3. **It funds research.** The 10% platform fee creates a revenue stream that directly funds the research pipeline. The more people bet on truth map questions, the more resources the system has to produce evidence.

4. **It makes epistemology visible.** Users can see which questions the community thinks are close to resolution, which are stuck, and which have conflicting evidence. The market becomes a heatmap of the frontier.

5. **It prevents stagnation.** Questions that haven't moved in months have low odds, which means low staking activity. This signals that the question needs fresh evidence, which the hypothesis engine can prioritize.
