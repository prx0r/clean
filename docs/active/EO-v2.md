# Essay Object v2 — Full Spec

## Purpose

An EO is a **structured tension point between two or more serious explanations of the same phenomenon.** It is the bridge between research (ROs, truth map) and production (essays, videos). The EO exists to answer: *what is the state of this debate right now, what survives criticism, and what should we produce about it?*

An EO is structured as a **Nyāya 5-member syllogism**:
1. **Pratijñā** (proposition) — the question and why it matters
2. **Hetu** (reason) — the evidence and arguments that bear on it
3. **Udāharaṇa** (example) — concrete cases demonstrating the tension
4. **Upanaya** (application) — how the evidence applies to this specific question
5. **Nigamana** (conclusion) — what currently survives criticism and what doesn't

---

## 1. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "EssayObjectV2",
  "type": "object",
  "required": [
    "eo_id", "schema_version", "title", "status",
    "syllogism", "state_of_play", "provenance"
  ],
  "properties": {
    "eo_id": {
      "type": "string",
      "pattern": "^eo:[a-z0-9_-]+$"
    },
    "schema_version": {
      "type": "integer",
      "minimum": 2
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Should contain a defensible claim, not just a question. e.g. 'Structural reflexivity is locally proven; universal consciousness is not entailed'"
    },
    "status": {
      "type": "string",
      "enum": ["idea", "draft", "active", "in_production", "answered", "archived"]
    },

    "question": {
      "type": "object",
      "required": ["question_id", "tension_point", "why_it_matters"],
      "properties": {
        "question_id": {
          "type": "string",
          "pattern": "^q:[a-z0-9_-]+$",
          "description": "Links to truth map question"
        },
        "tension_point": {
          "type": "string",
          "description": "The exact unresolved tension. Must name both sides."
        },
        "why_it_matters": {
          "type": "string",
          "maxLength": 2000,
          "description": "Scientific, philosophical, and contemplative stakes"
        },
        "resolution_level": {
          "type": "string",
          "enum": ["philological", "local_argument", "phenomenological", "empirical_constraint", "formal", "branch_relevant", "global_metaphysical"],
          "description": "What kind of resolution is possible here"
        }
      }
    },

    "syllogism": {
      "type": "object",
      "description": "Nyāya 5-member syllogism structure for the EO",
      "required": ["pratijna", "hetu", "udaharana", "upanaya", "nigamana"],
      "properties": {
        "pratijna": {
          "type": "object",
          "required": ["proposition", "what_it_claims"],
          "properties": {
            "proposition": {
              "type": "string",
              "description": "The claim to be examined. Concise, defensible."
            },
            "what_it_claims": {
              "type": "string",
              "description": "Expanded explanation of the proposition's commitments"
            }
          }
        },
        "hetu": {
          "type": "object",
          "required": ["evidence", "source_ids"],
          "properties": {
            "evidence": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["claim", "pramana", "source_id"],
                "properties": {
                  "claim": { "type": "string" },
                  "pramana": {
                    "type": "string",
                    "enum": ["pratyaksa", "anumana", "upamana", "sabda"]
                  },
                  "source_id": { "type": "string" },
                  "target": { "type": "string", "description": "Which discriminator or feature this bears on" }
                }
              }
            },
            "source_ids": {
              "type": "array",
              "items": { "type": "string" },
              "description": "All SO and RO IDs referenced"
            }
          }
        },
        "udaharana": {
          "type": "object",
          "required": ["examples"],
          "properties": {
            "examples": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["scenario", "what_it_shows"],
                "properties": {
                  "scenario": { "type": "string" },
                  "what_it_shows": { "type": "string" }
                }
              },
              "minItems": 1,
              "description": "Concrete cases demonstrating the tension in action"
            }
          }
        },
        "upanaya": {
          "type": "object",
          "required": ["application"],
          "properties": {
            "application": {
              "type": "string",
              "description": "How the hetu and udaharana specifically bear on this question"
            },
            "cruxes": {
              "type": "array",
              "items": { "type": "string" },
              "description": "The specific points where explanations diverge"
            }
          }
        },
        "nigamana": {
          "type": "object",
          "required": ["best_current_answer", "status"],
          "properties": {
            "best_current_answer": { "type": "string" },
            "status": {
              "type": "string",
              "enum": ["strongly_supported", "plausible", "structurally_suggestive", "underdetermined", "weak"]
            },
            "scope": {
              "type": "string",
              "description": "What level the answer is settled at vs what level it's open"
            }
          }
        }
      }
    },

    "candidates": {
      "type": "array",
      "description": "Serious possible answers to the question from different traditions",
      "items": {
        "type": "object",
        "required": ["candidate_id", "name", "position", "tradition"],
        "properties": {
          "candidate_id": { "type": "string" },
          "name": { "type": "string" },
          "tradition": { "type": "string" },
          "position": { "type": "string", "description": "The strongest statement of this position" },
          "proponent": { "type": "string", "description": "Key thinker(s)" },
          "source_ids": {
            "type": "array",
            "items": { "type": "string" }
          },
          "hard_to_vary_core": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Claims this explanation cannot change without breaking"
          },
          "current_problems": {
            "type": "array",
            "items": { "type": "string" }
          },
          "falsifiers": {
            "type": "array",
            "items": { "type": "string" },
            "description": "What would weaken or defeat this candidate"
          },
          "status": {
            "type": "string",
            "enum": ["live", "weakened", "defeated", "merged"]
          }
        }
      },
      "minItems": 2
    },

    "state_of_play": {
      "type": "object",
      "required": ["summary", "what_survives", "what_is_weakened", "what_would_change_our_mind"],
      "properties": {
        "summary": { "type": "string" },
        "what_survives": { "type": "string" },
        "what_is_weakened": { "type": "string" },
        "what_would_change_our_mind": { "type": "string" },
        "open_cruxes": {
          "type": "array",
          "items": { "type": "string" }
        },
        "next_tests": {
          "type": "array",
          "items": { "type": "string" }
        },
        "implications": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "condition": { "type": "string", "description": "If this answer holds" },
              "consequence": { "type": "string", "description": "Then what follows?" }
            }
          }
        }
      }
    },

    "provenance": {
      "type": "object",
      "required": ["created_by", "last_updated"],
      "properties": {
        "parent_ros": {
          "type": "array",
          "items": { "type": "string" }
        },
        "parent_dossier": {
          "type": "string",
          "description": "Link to the argument dossier JSON in content/source-metaphysics/"
        },
        "created_by": { "type": "string" },
        "last_updated": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

---

## 2. Relationship to Other Objects

```
Truth Map Question (q:reflexivity-intrinsic-or-constructed)
  │
  ├── Argument Dossier (q-reflexivity.argument.json)
  │     Raw candidates, cruxes, criticisms — the research raw material
  │
  └── EO (eo:reflexivity-intrinsic-or-constructed)
        The structured syllogism — ready for factory consumption
        Contains: pratiñā → hetu → udāharaṇa → upanaya → nigamana
        +
        Candidates with status (live/weakened/defeated)
        +
        State of play (what survives, what's open, next tests)
              │
              ├──→ Factory 2: Writing → Essay
              │     Uses the syllogism as article structure
              │     Uses the state of play as conclusion
              │
              └──→ Factory 3: Video → YouTube
                    Uses the candidates as narrative tension
                    Uses the open cruxes as unresolved ending
```

---

## 3. Example: Reflexivity EO

```json
{
  "eo_id": "eo:reflexivity-intrinsic-or-constructed",
  "schema_version": 2,
  "title": "Structural reflexivity is locally proven; universal consciousness is not entailed",
  "status": "draft",

  "question": {
    "question_id": "q:reflexivity-intrinsic-or-constructed",
    "tension_point": "Is reflexive awareness intrinsic to experience (Abhinavagupta) or a constructed operation (Dharmakīrti, higher-order theories)? Ñāṇavīra offers a middle path: structural reflexivity without hidden substance.",
    "why_it_matters": "This is the local crux between Buddhist no-self analyses, higher-order theories of consciousness, and Pratyabhijñā vimarśa. If reflexivity is intrinsic, the hard problem shifts. If it's constructed, physicalist accounts gain plausibility.",
    "resolution_level": "local_argument"
  },

  "syllogism": {
    "pratijna": {
      "proposition": "Structural reflexivity is locally confirmed in phenomenology; universal consciousness does not follow from local reflexivity alone.",
      "what_it_claims": "The claim splits into two parts. First: experience includes its own occurrence without requiring a hidden soul-substance — this is phenomenologically well-supported by Ñāṇavīra's analysis and by cross-traditional reports. Second: generalizing from local reflexivity to 'consciousness is the ground of all reality' is an additional step that is not entailed by the evidence."
    },
    "hetu": {
      "evidence": [
        {
          "claim": "Two things define a thing, namely the difference between them",
          "pramana": "anumana",
          "source_id": "so:nanavira-fundamental-structure",
          "target": "D3"
        },
        {
          "claim": "Nondual awareness has distinct neural correlates (DMN decoupling + sensory integration)",
          "pramana": "pratyaksa",
          "source_id": "so:josipovic-nondual-neural-2014",
          "target": "D3"
        },
        {
          "claim": "Memory requires a unified subject — Buddhist momentariness cannot account for recognition",
          "pramana": "anumana",
          "source_id": "so:utpaladeva-ipk",
          "target": "D3"
        },
        {
          "claim": "Reflexive awareness can be modelled as self-modelling without remainder",
          "pramana": "anumana",
          "source_id": "so:metzinger-mpe-2020",
          "target": "D3"
        }
      ],
      "source_ids": ["so:nanavira-fundamental-structure", "so:josipovic-nondual-neural-2014", "so:utpaladeva-ipk", "so:metzinger-mpe-2020"]
    },
    "udaharana": {
      "examples": [
        {
          "scenario": "Ñāṇavīra's 'difference between two things' argument: to perceive two things as two requires an operation of differentiation that is itself invariant and more general than either thing.",
          "what_it_shows": "Reflexivity is not an extra property added to experience — it is the condition for there being experience at all."
        },
        {
          "scenario": "Josipovic 2014: nondual awareness shows DMN decoupling + sensory integration simultaneously — a specific neural signature, not absence.",
          "what_it_shows": "Nondual awareness is not 'nothing' — it has a reproducible structure. But this structure is neural, which pressures the claim that it's fundamental."
        }
      ]
    },
    "upanaya": {
      "application": "The evidence converges on structural reflexivity as a well-supported phenomenological invariant. But the evidence diverges on whether this reflexivity requires a universal ground (Abhinavagupta) or is simply the structure of any cognition (Dharmakīrti, Ñāṇavīra).",
      "cruxes": [
        "Does recognition require intrinsic self-manifestation?",
        "Can reflexivity be constructed without presupposing manifestness?",
        "Does local reflexivity license universal consciousness?",
        "Can neuroscience distinguish self-model reflexivity from manifestness?"
      ]
    },
    "nigamana": {
      "best_current_answer": "Structural reflexivity is strongly supported phenomenologically. Universal consciousness remains a separate, weaker step. The debate between Abhinavagupta, Dharmakīrti, and Ñāṇavīra is locally tractable on reflexivity but not globally resolvable on metaphysics.",
      "status": "structurally_suggestive",
      "scope": "Local reflexivity: plausible. Universal consciousness: underdetermined."
    }
  },

  "candidates": [
    {
      "candidate_id": "cand:abh-vimarsa",
      "name": "Intrinsic self-manifestation",
      "tradition": "trika_pratyabhijna",
      "proponent": "Abhinavagupta",
      "position": "Experience is not merely present; its presence is self-apprehending. Vimarśa (reflexive awareness) is intrinsic to prakāśa (manifestness).",
      "source_ids": ["so:utpaladeva-ipk"],
      "hard_to_vary_core": ["manifestness cannot be explained by non-manifest structure", "recognition requires reflexive self-presence"],
      "current_problems": ["universalisation from local reflexivity", "relation to brain dependence", "risk of reifying subjectivity"],
      "falsifiers": ["A complete account of recognition/reflexivity that does not presuppose self-manifestation"],
      "status": "live"
    },
    {
      "candidate_id": "cand:dharmakirti-apoha",
      "name": "Conditioned reflexivity without Self",
      "tradition": "buddhist_pramana",
      "proponent": "Dharmakīrti",
      "position": "Reflexivity is a structured feature of cognition, not evidence for an ultimate subject. Meaning is exclusion (apoha); identity is structure, not substance.",
      "source_ids": ["so:dharmakirti-pv3"],
      "hard_to_vary_core": ["identity is exclusion/structure, not substance", "selfhood is constructed from cognitive operations"],
      "current_problems": ["whether manifestness is assumed rather than explained", "whether reflexive awareness can be fully non-substantial without becoming eliminative"],
      "falsifiers": ["A demonstration that conditioned cognition cannot account for immediate self-presence"],
      "status": "live"
    },
    {
      "candidate_id": "cand:nanavira-structural",
      "name": "Structural reflexivity without hidden substance",
      "tradition": "buddhist_phenomenology",
      "proponent": "Ñāṇavīra Thera",
      "position": "Two things define a thing, namely the difference between them. Experience includes its own occurrence through structural necessity, not through a hidden subject. Reflexivity is the invariant operation of differentiation.",
      "source_ids": ["so:nanavira-fundamental-structure"],
      "hard_to_vary_core": ["two things define the difference between them", "the operation is invariant during transformation", "the structure of structure has the structure of structure"],
      "current_problems": ["whether the invariant operation implies an invariant operator", "whether structural reflexivity can ground ethics", "relation to brain dependence"],
      "falsifiers": ["A demonstration that difference can be perceived without an invariant operation of differentiation"],
      "status": "live"
    },
    {
      "candidate_id": "cand:higher-order-self-model",
      "name": "Higher-order / self-model theories",
      "tradition": "cognitive_science",
      "proponent": "Metzinger, Laukkonen",
      "position": "Reflexivity is a constructed higher-order operation — a self-model that models itself. Nondual awareness is self-model collapse, not ontological revelation.",
      "source_ids": ["so:metzinger-mpe-2020", "so:laukkonen-beautiful-loop-2025"],
      "hard_to_vary_core": ["consciousness can be modelled as meta-cognition", "self-models are constructed, not given"],
      "current_problems": ["hard problem: why is there manifestness at all?", "recognition phenomenology exceeds model predictions"],
      "falsifiers": ["A demonstration that self-modelling requires presupposing what it claims to explain"],
      "status": "live"
    }
  ],

  "state_of_play": {
    "summary": "Structural reflexivity is the common ground. Abhinavagupta, Dharmakīrti, and Ñāṇavīra all agree that experience includes reflexive awareness. They disagree on what it entails. Cognitive science can model some of this but cannot yet account for manifestness.",
    "what_survives": "Structural reflexivity as a phenomenological invariant. The operation of differentiation is more fundamental than either of the things it differentiates. This survives cross-traditional scrutiny (Trika, Buddhist, phenomenological).",
    "what_is_weakened": "Universal consciousness claims are weakened by brain dependence data and by Ñāṇavīra's demonstration that structural reflexivity does not require an absolute subject. Pure constructionism is weakened by the recognition phenomenology that self-model theories struggle to explain.",
    "what_would_change_our_mind": "A decisive experiment distinguishing intrinsic reflexivity from constructed self-modelling would break the deadlock. Currently, the debate is observationally unresolved — both interpretations fit the available evidence.",
    "open_cruxes": [
      "Does recognition require intrinsic self-manifestation or is it explicable as structured cognition?",
      "Can the invariant operation of differentiation exist without an invariant operator?",
      "Does the hard problem dissolve if reflexivity is accepted as primitive?"
    ],
    "next_tests": [
      "TMS study comparing DMN disruption phenomenology with nondual recognition — is it recognition or confusion?",
      "Formal analysis of Ñāṇavīra's invariant operation: can it be modelled in category theory?",
      "Cross-traditional survey of advanced practitioners: does nondual awareness feel like recognition or construction?"
    ],
    "implications": [
      {"condition": "If structural reflexivity is accepted as a primitive", "consequence": "The hard problem shifts from 'why experience?' to 'why individuation?'"},
      {"condition": "If universal consciousness does not follow from local reflexivity", "consequence": "Trika's metaphysical claims must be separated from its phenomenological claims"},
      {"condition": "If self-model theories can explain recognition", "consequence": "Physicalism is strengthened; contemplative traditions lose metaphysical force"}
    ]
  },

  "provenance": {
    "parent_ros": [],
    "parent_dossier": "content/source-metaphysics/q-reflexivity-intrinsic-or-constructed.argument.json",
    "created_by": "agent/research",
    "last_updated": "2026-07-26"
  }
}
```

---

## 4. Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| E01 | Less than 2 candidates | Reject — every EO needs at least 2 competing explanations |
| E02 | No cruc named in upanaya | Reject — must specify the divergence points |
| E03 | state_of_play missing what_would_change_our_mind | Reject — EOs must identify what would break the current answer |
| E04 | syllogism missing any of 5 members | Reject — must follow Nyāya syllogism form |
| E05 | Candidate with "defeated" status but no documented criticism | Warn — defeated candidates should show why |
| E06 | No falsifier on any candidate | Warn — every candidate should have at least one falsifier |
| E07 | question_id doesn't match a truth map question | Warn — should link to existing question |
| E08 | resolution_level is global_metaphysical with no lower-level resolutions | Reject — don't claim global resolution without local evidence |

---

## 5. Lifecycle

```
Truth map question underdetermined
  → Hypothesis engine detects: enough ROs exist, question is open
    → Research agent creates argument dossier
      → Raw candidates, cruxes, criticisms compiled
    → Argument dossier → EO via syllogism structure
      → pratiñā, hetu, udāharaṇa, upanaya, nigamana populated
      → Candidates assigned statuses
      → State of play written
    → EO enters queue for Writing Factory
      → Essay produced (V7 algorithm)
    → EO enters queue for Video Factory
      → Video produced (platinum pipeline)
    → Both update truth map:
      → Question status updated based on what was discovered
      → New claims from the content extracted and ingested
```

---

## 6. Relationship to Nyāya Gate

The EO inherits validation from the Nyāya gate:

- Every claim in `syllogism.hetu.evidence` must have passed hetvābhāsa checking
- Every falsifier should be structured as a tarka prasaṅga (reductio)
- The 5-member syllogism structure ensures the EO is logically well-formed before factories touch it
- If the gate would reject a claim, the EO must be revised before entering production

---

## 7. Relationship to Previous Spec

The v1 spec (in `specs/EO.md`) had: `hypotheses`, `tension_point`, `truth_map_question`. 
The v2 spec replaces these with:
- **syllogism** (Nyāya 5-member structure replaces free-form hypotheses)
- **candidates** (named positions with falsifiers, replacing hypothesis array)
- **state_of_play** (explicit tracking of what survives, what's weakened, next tests)
- **question** (structured link to truth map with resolution_level)

Migration: v1 EOs can be converted by extracting tension_point → syllogism.pratijna and hypotheses → candidates.
