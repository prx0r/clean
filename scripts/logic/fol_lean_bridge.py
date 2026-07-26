"""
FOL → Lean4 type translation for Navya-Nyāya structures.
Per instruction.md: ~200 lines mapping NN operators (avacchedaka, pratiyogin, anuyogin, sambandha)
to type-theoretic equivalents. Ganeri 2008 gives FOL; this is the novel bridge.
"""

from typing import Any
from dataclasses import dataclass

# Navya-Nyāya relational operators (Ganeri 2008 property-theoretic FOL)
# avacchedaka = limitor (restricts the domain of a relation)
# pratiyogin = counterpositive (negation of the relatum)
# anuyogin = locus (the subject of the relation)
# sambandha = relation (connector between relata)
# abheda = identity
# vyāpti = pervasion / universal concomitance


@dataclass
class NNExpr:
    """Navya-Nyāya expression in FOL-like form."""
    kind: str  # "abheda" | "vyapti" | "sambandha" | "avacchedaka" | "pratiyogin" | "anuyogin" | "property" | "negation"
    args: list[Any]


def nn_to_lean(nn: NNExpr) -> str:
    """
    Map NN FOL expression to Lean4 type.
    Conservative: only maps structures we can formalize.
    """
    if nn.kind == "abheda":
        # Identity: a = b. Two nominals, same referent.
        if len(nn.args) >= 2:
            a, b = str(nn.args[0]), str(nn.args[1])
            return f"{a} = {b}"
        return "?"

    if nn.kind == "vyapti":
        # Universal concomitance: wherever hetu, there sādhya.
        # ∀ x, Hetu x → Sadhya x
        if len(nn.args) >= 2:
            hetu, sadhya = nn.args[0], nn.args[1]
            h = _term(hetu)
            s = _term(sadhya)
            return f"∀ x, {h} x → {s} x"
        return "∀ (Hetu Sadhya : α → Prop), (∀ x, Hetu x → Sadhya x)"

    if nn.kind == "sambandha":
        # Relation R between a and b: R a b
        if len(nn.args) >= 3:
            r, a, b = nn.args[0], nn.args[1], nn.args[2]
            return f"{_term(r)} {_term(a)} {_term(b)}"
        return "?"

    if nn.kind == "avacchedaka":
        # Limitor: restricts domain. In type theory: (x : α) where α is the limited type
        if len(nn.args) >= 2:
            prop, limitor = nn.args[0], nn.args[1]
            return f"∀ {{x : {_term(limitor)}}}, {_term(prop)} x"
        return "?"

    if nn.kind == "property":
        if len(nn.args) >= 1:
            return f"{_term(nn.args[0])} : α → Prop"
        return "?"

    if nn.kind == "negation":
        if len(nn.args) >= 1:
            inner = nn.args[0]
            return f"¬ ({nn_to_lean(inner)})" if isinstance(inner, NNExpr) else f"¬ {_term(inner)}"
        return "?"

    return "?"


def _term(x: Any) -> str:
    if isinstance(x, NNExpr):
        return f"({nn_to_lean(x)})"
    return str(x)


def parse_nn_from_heritage(heritage_output: dict) -> NNExpr | None:
    """
    Parse Heritage Engine / Navya-Nyāya output into NNExpr.
    Heritage gives: sandhi split, morphological analysis.
    Expected keys: relations, abheda, vyapti, etc.
    """
    if not heritage_output:
        return None
    rels = heritage_output.get("relations", [])
    if not rels:
        # Single nominal or identity
        if heritage_output.get("abheda"):
            a, b = heritage_output["abheda"][:2] if len(heritage_output.get("abheda", [])) >= 2 else ("A", "B")
            return NNExpr("abheda", [a, b])
        return None
    r = rels[0]
    kind = r.get("kind", "sambandha")
    args = r.get("args", [])
    return NNExpr(kind, args)


# Predefined mappings for Phase 1 Nyāya terms (faithful to source, no bias)
NYAYA_LEAN_TYPES = {
    "pramāṇa": "∀ (source : Type) (belief : Prop), ValidCognition source belief → belief",
    "pramāṇam": "∀ (source : Type) (belief : Prop), ValidCognition source belief → belief",
    "saṃśaya": "∀ (obj : α), Doubt obj ↔ ¬(∃! (c : Cognition), Determines c obj)",
    "saṃśayaḥ": "∀ (obj : α), Doubt obj ↔ ¬(∃! (c : Cognition), Determines c obj)",
    "vyāpti": "∀ (α : Type*) (Hetu Sadhya : α → Prop), (∀ x, Hetu x → Sadhya x)",
    "vyāptiḥ": "∀ (α : Type*) (Hetu Sadhya : α → Prop), (∀ x, Hetu x → Sadhya x)",
    "anumāna": "InferenceRule",  # Five-membered syllogism — decompose further
}

# Dharmakīrti (PV III pratyakṣa chapter). logic_foundation: classical.
# pramāṇa ↔ arthakriyā ↔ successful cognition: circular, mark coherentist.
DHARMAKIRTI_LEAN_TYPES = {
    "pratyakṣa": "∀ (c : Cognition) (x : Svalaksana), Perceives c x → ¬ Kalpana c",
    "pratyakṣam": "∀ (c : Cognition) (x : Svalaksana), Perceives c x → ¬ Kalpana c",
    "kalpanā": "Kalpana : Cognition → Prop",  # conceptual construction
    "kalpanāpoḍha": "∀ (c : Cognition), ¬ Kalpana c",  # free from conceptual construction
    "svalakṣaṇa": "Svalaksana : Type",  # particular, inexpressible
    "arthakriyā": "∀ (x : Object), Arthakriya x → SuccessfulCognition x",  # causal efficacy
    "pramāṇa": "∀ (c : Cognition), Pramana c ↔ Arthakriya (object_of c)",  # DK: via arthakriyā
    "pramāṇam": "∀ (c : Cognition), Pramana c ↔ Arthakriya (object_of c)",
}
