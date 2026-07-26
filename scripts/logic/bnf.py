"""
NNExpr BNF grammar gate per Schema v3 §9b.
LLM output is validated against this before proceeding.
"""

import re
from typing import Optional

# Simplified BNF: Atom | BinaryOp(Atom,Atom) | UnaryOp(Atom) | Negation(Atom)
# Traditions: Ny | Dk | Adv | Mim | Nag
TRADITIONS = {"Ny", "Dk", "Adv", "Mim", "Nag"}
BINARY_OPS = {"vyāpti", "sambandha", "abheda", "bhedāgrahaṇa", "svabhāvapratibandha", "kārya"}
UNARY_OPS = {"viṣaya", "avacchedaka", "pratiyogin", "anuyogin", "nirūpaṇa", "svarūpa"}
NEGATION_OPS = {"abhāva_mutual", "abhāva_relational", "abhāva_prior", "abhāva_posterior", "abhāva_absolute"}
FDE_OPS = {"catuskoti", "prasanga", "apoha"}


def parse_nnexpr(s: str) -> Optional[dict]:
    """
    Parse NNExpr string. Returns dict with {kind, args} or None if invalid.
    Accepts: TID_123[Dk], vyāpti(TID_1[Dk], TID_2[Dk]), abheda(a,b), etc.
    """
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    # TID_N[Tradition]
    m = re.match(r"TID_(\d+)\[(Ny|Dk|Adv|Mim|Nag)\]", s)
    if m:
        return {"kind": "atom", "tid": int(m.group(1)), "tradition": m.group(2)}

    # Var
    if re.match(r"^[a-z][a-z0-9_]*$", s):
        return {"kind": "atom", "var": s}

    # Op(Expr, Expr) or Op(Expr)
    for op in BINARY_OPS | UNARY_OPS | NEGATION_OPS | FDE_OPS:
        prefix = op + "("
        if s.startswith(prefix) and s.endswith(")"):
            inner = s[len(prefix):-1]
            if op in BINARY_OPS:
                parts = _split_outer(inner, ",")
                if len(parts) == 2:
                    a, b = parse_nnexpr(parts[0].strip()), parse_nnexpr(parts[1].strip())
                    if a and b:
                        return {"kind": "binary", "op": op, "args": [a, b]}
            else:
                a = parse_nnexpr(inner.strip())
                if a:
                    return {"kind": "unary" if op in UNARY_OPS else "negation" if op in NEGATION_OPS else "fde", "op": op, "arg": a}
    return None


def _split_outer(s: str, sep: str) -> list[str]:
    """Split by sep at top level (ignore inside parens)."""
    depth = 0
    out = []
    start = 0
    for i, c in enumerate(s):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == sep and depth == 0:
            out.append(s[start:i])
            start = i + 1
    out.append(s[start:])
    return out


def validate_nnexpr(s: str) -> bool:
    """Return True if s parses as valid NNExpr."""
    return parse_nnexpr(s) is not None
