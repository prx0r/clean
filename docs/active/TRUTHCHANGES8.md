# Truth Changes 8 — Translation → Logic → Truth Map Pipeline

## The Connection

We have three things that were built separately and need to be wired together:

1. **TO pipeline** (7-pass DeepSeek translation) — converts Sanskrit text → Translation Object with verse-level translations, alternatives, confidence
2. **NNExpr BNF grammar** (`sanskritree/proof_engine/bnf.py`) — parses Navya-Nyāya logical expressions from translated text
3. **Truth map** — tracks evidence for/against research questions

The connection: **translated Navya-Nyāya texts are not just language — they're logical training data.** Each verse encodes a structured argument pattern. If we parse them through the NNExpr grammar, we extract the inference rules directly.

---

## The Pipeline

```
Sanskrit text (Tarkasaṃgraha, Nyāya-Sūtras)
  → TO pipeline (7-pass DeepSeek translation)
    → Translation Object: structured JSON per verse
      → NNExpr parser (bnf.py)
        → Extracted: vyāpti(a,b), abheda(c,d), avacchedaka(e,f)
          → Claim template generated for truth map
            "This text uses vyāpti between A and B as evidence for C"
          → Inference pattern stored for engine calibration
            "vyāpti in Navya-Nyāya maps to w_map with these constraints"
        → Cross-reference with existing truth map claims
          "Does this vyāpti pattern match a known discriminator?"
      → Falsifier generated for truth map
        "If vyāpti(a,b) fails when... then the original claim is weakened"
```

### Concrete Example

Say we translate Tarkasaṃgraha §1 on pramāṇa:

```
Sanskrit: "pramākaraṇaṃ pramāṇam"
Translation: "The instrument of valid cognition is pramāṇa"
NNExpr parse: abheda(pramā, pramāṇa)
  → Truth map: this is a definitional equivalence
  → Claim template: "X = definitionally Y" → use identity rule, not evidence weight
  → Falsifier: "If valid cognition can occur without pramāṇa, this is false"
```

Then we process Nyāya-Sūtra 1.1.1 on perception:

```
Sanskrit: "indriyārthasannikarṣotpannaṃ jñānaṃ pratyakṣam"
Translation: "Perception is cognition born from sense-object contact"
NNExpr parse: vyāpti(jñāna_indriya_artha_sannikarṣa, pratyakṣa)
  → Truth map: this is a pervasion relation
  → Claim template: "evidence type X → conclusion Y via vyāpti"
  → Maps to our pramāṇa-based evidence dimension:
    pratyakṣa (perception) = empirical dimension
  → Falsifier: "Cognition without sense-object contact would disprove this"
```

---

## How Tuning Helps

### 1. Ground Truth Claim Templates

Every Navya-Nyāya argument pattern teaches the engine what valid inference looks like:

| Pattern from NNExpr | What it encodes | How it trains the engine |
|---|---|---|
| `abheda(X, Y)` | X and Y are identical | Don't assign separate evidence weights — they're the same thing |
| `vyāpti(X, Y)` | X always implies Y | The mapping from evidence to conclusion is invariable. Use high w_map. |
| `avacchedaka(X, Y)` | X is a limitor of Y | Evidence X only applies to question Y within these boundaries |
| `pratiyogin(X, Y)` | X is the counterpositive of Y's absence | Generate falsifier: if ¬X then ¬Y |
| `sambandha(X, Y)` | X is related to Y | Weak evidence — correlation without causation |
| `catuskoṭi(X)` | X has 4 truth values | Switch to FDE logic, not classical. Don't apply bivalence. |

The engine learns: different NNExpr patterns → different claim validation rules, different weight defaults, different falsifier templates.

### 2. Calibrating Weight Defaults

Instead of LLMs guessing w_rel/w_map/w_aux, the engine derives defaults from the argument pattern:

```
NNExpr pattern: vyāpti(X, Y)
  → w_map default: 0.85 (vyāpti is a strong mapping by definition)
  → w_rel default: 0.90 (the evidence is directly relevant)
  → Falsifier generated automatically: "if X without Y is found, this claim fails"

NNExpr pattern: sambandha(X, Y)  
  → w_map default: 0.30 (correlation ≠ causation)
  → w_rel default: 0.40
  → Requires additional evidence to strengthen

NNExpr pattern: abheda(X, Y)
  → No weights needed — this is a definitional identity
  → X and Y should be merged in the truth map
```

### 3. Falsifier Generation from Argument Structure

The most valuable output: every Navya-Nyāya argument pattern tells us what would break it.

```
pratiyogin(X, absence_of_Y): 
  "X is the counterpositive of Y's absence"
  → Falsifier: "show X existing without Y → the vyāpti is broken"

avacchedaka(X, property_Y):
  "X is the limitor of property Y"
  → Falsifier: "show property Y manifesting outside limitor X → the avacchedaka is wrong"

catuskoṭi(claim):
  "This claim has 4 logical possibilities"
  → Falsifier: "If the claim can be shown to be only 2-valued, catuskoṭi doesn't apply"
```

### 4. Cross-Tradition Bridge Discovery

When two translated texts encode the same NNExpr pattern for different traditions, that's a **bridge**:

```
Dharmakīrti (PV III): vyāpti(arthakriyā, pramāṇa)
  → "Causal efficacy pervades valid cognition"

Nyāya (NS 1.1.1): vyāpti(pramākaraṇa, pramāṇa)
  → "Instrument pervades valid cognition"

These are vyāpti statements about the same concept (pramāṇa).
  → Bridge: both use vyāpti to define pramāṇa
  → Divergence: Dharmakīrti defines via causal efficacy, Nyāya via instrumentality
  → Truth map insight: the traditions agree on the logical FORM (vyāpti) 
    but disagree on the CONTENT (what pervades pramāṇa)
  → This is a divergence node with type "shared form, different content"
```

---

## Do We Need to Work in Sanskritree, or Is What We Have Good Enough?

**What we have is good enough to start.** The sanskritree project is ~40% complete and has all the core pieces working:

| What exists | Status |
|---|---|
| NNExpr BNF grammar (bnf.py) | ✅ Working, 72 lines |
| FOL-to-Lean bridge (fol_lean_bridge.py) | ✅ Working for Nyāya + Dharmakīrti |
| Proof engine algorithm (algorithm.py) | ✅ Working 7-step process |
| Ground truth seeds (11 JSON files) | ✅ Ready |
| Nyāya Phase 1 engine (phase1_nyaya.py) | ✅ NS 1.1.1 running |
| TO pipeline (7-pass) | ⚠️ Spec exists, not fully automated |

**To start integrating, we don't need more sanskritree work. We need:**

1. **Import the NNExpr parser** into the clean project's claim validation pipeline (takes 1 hour)
2. **Translate one Nyāya text** (Tarkasaṃgraha) through the 7-pass pipeline to get real NNExpr patterns (takes ~1 day)
3. **Wire the parsed patterns** into the truth map as claim templates (takes 2-3 hours)
4. **Create one EO** using the extracted argument structure (the critical gap)

**The tuning helps immediately** because it replaces LLM-guessed weights with pattern-derived defaults. Every claim that matches a known NNExpr pattern gets better default weights and automatic falsifier generation. Claims that don't match any pattern get flagged for review.

---

## Implementation Order

1. **(P0) Import bnf.py** into clean project under `scripts/logic/` — 72 lines, zero dependencies
2. **(P0) Import fol_lean_bridge.py** into clean project — 125 lines, gives us Nyāya Lean types
3. **(P1) Write `scripts/translate-to-nnexpr.py`** — takes a TO, runs each verse through NNExpr parser, outputs structured inference patterns
4. **(P1) Create claim template registry** — NNExpr pattern → truth map default weights + falsifier template
5. **(P2) Translate Tarkasaṃgraha** through 7-pass pipeline to get real training data
6. **(P3) Build bridge discovery** across translated texts
