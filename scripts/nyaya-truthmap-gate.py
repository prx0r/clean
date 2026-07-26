#!/usr/bin/env python3
"""
nyaya-truthmap-gate.py

Standalone pre-ingestion gate for truth-map claims.

This script is intentionally additive: it does not modify the current truth-map
runtime. It reads a claim or information packet and emits gate records that can
later be inserted into `claim_gate_results`.

The gate combines:
  - truth-map required fields
  - Nyaya-inspired hetvabhasa checks
  - tarka-style falsifier requirements
  - optional Sanskritree proof-engine status probing when available
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


SANSKRITREE_ROOT = Path("/mnt/HC_Volume_106427611/sanskritree")
GATE_VERSION = "nyaya-truthmap-gate-v0.1"

PRAMANAS = {
    "pratyaksa",
    "anumana",
    "upamana",
    "sabda",
    "formal_proof",
    "mixed",
    "none",
}

EVIDENCE_DIMENSIONS = {
    "phenomenological",
    "empirical",
    "contemplative",
    "formal",
    "textual",
    "analogical",
}

FALLACY_TYPES = (
    "savyabhicara",
    "viruddha",
    "asiddha",
    "satpratipaksa",
    "badhita",
)

STRONG_WORDS = ("proves", "settles", "demonstrates", "decisive", "therefore reality")
ANALOGY_WORDS = ("maps to", "resembles", "analogous", "isomorphic", "parallel")
TESTIMONY_SOURCE_TYPES = {"translation", "ro", "text", "commentary", "expert"}
EMPIRICAL_SOURCE_TYPES = {"paper", "dataset", "experiment", "study", "pubmed", "arxiv"}
FORMAL_SOURCE_TYPES = {"formal", "lean", "proof", "theorem"}
CONTEMPLATIVE_PARADIGMS = {"contemplative", "meditation", "nondual_practice", "practitioner_report"}
TEXTUAL_PARADIGMS = {"trika", "nyaya", "dharmakirti", "madhyamaka", "vedanta", "sanskrit"}
EMPIRICAL_PARADIGMS = {
    "neuroscience",
    "neuropsychology",
    "active_inference",
    "predictive_processing",
    "iit",
    "gnwt",
    "high_energy_physics",
    "information_theory",
    "constructor_theory",
    "physical_closure",
}


@dataclass
class HetvabhasaFailure:
    fallacy_type: str
    severity: str
    rationale: str


@dataclass
class TarkaFalsifier:
    falsifier_type: str
    condition: str
    status: str = "untested"


@dataclass
class FormalProbe:
    attempted: bool = False
    status: str = "UNKNOWN"
    node_id: Optional[int] = None
    notes: str = ""


@dataclass
class NNExprProbe:
    attempted: bool = False
    status: str = "not_provided"
    expression: Optional[str] = None
    normalized_expression: Optional[str] = None
    parsed_tree: Optional[dict[str, Any]] = None
    notes: str = ""


@dataclass
class GateResult:
    claim_id: str
    gate_version: str
    outcome: str
    can_update_posterior: bool
    adjusted_lbf_cap: Optional[float]
    evidence_dimension: str
    pramana: str
    tradition_scope: str
    hetu: str
    sadhya: str
    vyapti_statement: str
    vyapti_confidence: Optional[float]
    falsifier_status: str
    failures: list[HetvabhasaFailure] = field(default_factory=list)
    tarka_falsifiers: list[TarkaFalsifier] = field(default_factory=list)
    nnexpr_probe: NNExprProbe = field(default_factory=NNExprProbe)
    formal_probe: FormalProbe = field(default_factory=FormalProbe)
    reasoning: str = ""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def packet_claims(data: Any) -> list[dict]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "claims" in data:
        return list(data.get("claims") or [])
    if isinstance(data, dict):
        return [data]
    raise ValueError("input must be a claim object, claim array, or packet with claims[]")


def infer_tradition_scope(claim: dict) -> str:
    for key in ("tradition_scope", "tradition", "paradigm"):
        value = claim.get(key)
        if value:
            return str(value).lower()
    source_id = str(claim.get("source_id", "")).lower()
    for marker in ("trika", "nyaya", "dharmakirti", "iit", "gnwt", "neuroscience"):
        if marker in source_id:
            return marker
    return "unknown"


def infer_pramana(claim: dict) -> str:
    explicit = claim.get("pramana") or claim.get("pramāṇa")
    if explicit:
        normalized = ascii_key(str(explicit))
        if normalized in PRAMANAS:
            return normalized

    source_type = str(claim.get("source_type", "")).lower()
    paradigm = infer_tradition_scope(claim)
    text = str(claim.get("claim_text", "")).lower()

    if source_type in FORMAL_SOURCE_TYPES or claim.get("lean_type"):
        return "formal_proof"
    if any(word in text for word in ANALOGY_WORDS):
        return "upamana"
    if paradigm in EMPIRICAL_PARADIGMS:
        return "anumana"
    if source_type in TESTIMONY_SOURCE_TYPES or paradigm in TEXTUAL_PARADIGMS:
        return "sabda"
    if source_type in EMPIRICAL_SOURCE_TYPES or paradigm in CONTEMPLATIVE_PARADIGMS:
        return "pratyaksa"
    if "therefore" in text or "implies" in text or "because" in text:
        return "anumana"
    return "anumana"


def infer_dimension(claim: dict, pramana: str) -> str:
    explicit = claim.get("evidence_dimension")
    if explicit and explicit in EVIDENCE_DIMENSIONS:
        return explicit
    if pramana == "formal_proof":
        return "formal"
    if pramana == "sabda":
        return "textual"
    if pramana == "upamana":
        return "analogical"
    if infer_tradition_scope(claim) in EMPIRICAL_PARADIGMS:
        return "empirical"
    if pramana == "pratyaksa":
        paradigm = infer_tradition_scope(claim)
        if paradigm in CONTEMPLATIVE_PARADIGMS:
            return "contemplative"
        return "empirical"
    return "phenomenological"


def ascii_key(value: str) -> str:
    replacements = {
        "pratyakṣa": "pratyaksa",
        "anumāna": "anumana",
        "upamāna": "upamana",
        "śabda": "sabda",
        "sabda": "sabda",
        "formal": "formal_proof",
    }
    return replacements.get(value.strip().lower(), value.strip().lower())


def claim_targets(claim: dict) -> list[str]:
    targets = []
    for target in claim.get("targets", []) or []:
        target_id = target.get("target_id")
        if target_id:
            targets.append(str(target_id))
    targets.extend(str(x) for x in claim.get("features", []) or [])
    targets.extend(str(x) for x in claim.get("target_feature_ids", []) or [])
    targets.extend(str(x) for x in claim.get("discriminators", []) or [])
    targets.extend(str(x) for x in claim.get("target_discriminator_ids", []) or [])
    question = claim.get("question_id") or claim.get("target_question_id")
    if question:
        targets.append(str(question))
    return sorted(set(targets))


def falsifier_status(claim: dict) -> str:
    falsifier = claim.get("falsifier")
    if not falsifier:
        return "missing"
    if isinstance(falsifier, str):
        return "present" if falsifier.strip() else "missing"
    if isinstance(falsifier, dict):
        status = str(falsifier.get("status", "untested"))
        condition = str(falsifier.get("condition", "")).strip()
        if not condition:
            return "missing_condition"
        return status
    return "invalid"


def tarka_falsifiers(claim: dict, hetu: str, sadhya: str) -> list[TarkaFalsifier]:
    existing = claim.get("tarka_falsifiers") or []
    out = []
    for item in existing:
        if isinstance(item, dict) and item.get("condition"):
            out.append(
                TarkaFalsifier(
                    falsifier_type=str(item.get("type", item.get("falsifier_type", "prasanga"))),
                    condition=str(item["condition"]),
                    status=str(item.get("status", "untested")),
                )
            )

    if not out and hetu and sadhya:
        out.append(
            TarkaFalsifier(
                falsifier_type="prasanga",
                condition=f"Show a case where {hetu} holds but {sadhya} does not follow.",
            )
        )
    if not out and claim.get("claim_text"):
        out.append(
            TarkaFalsifier(
                falsifier_type="semantic",
                condition="Show that the claim has no stable truth condition under its stated terms.",
            )
        )
    return out


def hetu_sadhya_vyapti(claim: dict, targets: list[str]) -> tuple[str, str, str, Optional[float]]:
    hetu = str(claim.get("hetu") or claim.get("claim_text") or "").strip()
    sadhya = str(claim.get("sadhya") or ", ".join(targets) or "").strip()
    vyapti = str(claim.get("vyapti_statement") or claim.get("vyāpti_statement") or "").strip()
    confidence = claim.get("vyapti_confidence", claim.get("vyāpti_confidence"))
    if confidence is not None:
        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            confidence = None
    if not vyapti and hetu and sadhya:
        vyapti = f"If {hetu}, then this bears on {sadhya}."
    return hetu, sadhya, vyapti, confidence


def check_hetvabhasa(claim: dict, hetu: str, sadhya: str, vyapti_confidence: Optional[float], peer_claims: list[dict]) -> list[HetvabhasaFailure]:
    failures: list[HetvabhasaFailure] = []
    text = str(claim.get("claim_text", "")).lower()
    lbf = float(claim.get("log_bayes_factor", 0.0) or 0.0)
    source_type = str(claim.get("source_type", "")).lower()
    pramana = infer_pramana(claim)

    if vyapti_confidence is not None and vyapti_confidence < 0.5:
        failures.append(
            HetvabhasaFailure(
                "savyabhicara",
                "moderate",
                "The claim declares weak vyapti confidence; the reason does not reliably imply the target.",
            )
        )

    violations = claim.get("vyapti_violations") or claim.get("vyāpti_violations") or []
    if violations:
        failures.append(
            HetvabhasaFailure(
                "savyabhicara",
                "moderate",
                "The claim lists vyapti violations/counterexamples.",
            )
        )

    if "meditation proves consciousness is fundamental" in text:
        failures.append(
            HetvabhasaFailure(
                "asiddha",
                "strong",
                "The bridge from meditation reports to consciousness-fundamental ontology is unproven.",
            )
        )
        failures.append(
            HetvabhasaFailure(
                "savyabhicara",
                "strong",
                "Meditation does not invariably produce nondual awareness or metaphysical insight.",
            )
        )

    if any(word in text for word in STRONG_WORDS) and abs(lbf) > 0.8 and pramana in {"sabda", "upamana"}:
        failures.append(
            HetvabhasaFailure(
                "asiddha",
                "moderate",
                "Strong conclusion is being drawn from testimony or analogy; independent establishment is required.",
            )
        )

    if source_type in {"essay", "video", "eo"} and claim.get("evidence_role", "primary") == "primary":
        failures.append(
            HetvabhasaFailure(
                "asiddha",
                "moderate",
                "Derived content is marked primary; source evidence is not independently established.",
            )
        )

    opposing = find_counterbalanced_claims(claim, peer_claims)
    if opposing:
        failures.append(
            HetvabhasaFailure(
                "satpratipaksa",
                "moderate",
                f"Found peer claim(s) with opposing LBF on overlapping targets: {', '.join(opposing)}.",
            )
        )

    if "brain damage" in text and lbf > 0 and "consciousness fundamental" in sadhya.lower():
        failures.append(
            HetvabhasaFailure(
                "viruddha",
                "strong",
                "Brain-damage evidence usually constrains or attacks consciousness-fundamental claims unless the mapping is carefully narrowed.",
            )
        )

    if (
        ("no neural correlate" in text or "no neural correlates" in text)
        and ("brain is irrelevant" in text or "brain irrelevant" in text)
    ):
        failures.append(
            HetvabhasaFailure(
                "badhita",
                "strong",
                "The denial of neural correlates and brain relevance is contradicted by established neuroscience unless heavily narrowed.",
            )
        )

    if pramana == "sabda" and "contradicted by" in text:
        failures.append(
            HetvabhasaFailure(
                "badhita",
                "moderate",
                "The claim itself says testimony is contradicted by stronger evidence.",
            )
        )

    return failures


def find_counterbalanced_claims(claim: dict, peer_claims: list[dict]) -> list[str]:
    this_id = claim.get("claim_id")
    this_lbf = float(claim.get("log_bayes_factor", 0.0) or 0.0)
    if this_lbf == 0:
        return []
    this_targets = set(claim_targets(claim))
    out = []
    for peer in peer_claims:
        peer_id = peer.get("claim_id")
        if not peer_id or peer_id == this_id:
            continue
        peer_lbf = float(peer.get("log_bayes_factor", 0.0) or 0.0)
        if peer_lbf == 0 or (peer_lbf > 0) == (this_lbf > 0):
            continue
        if this_targets.intersection(claim_targets(peer)):
            out.append(str(peer_id))
    return out


def strongest_failure(failures: list[HetvabhasaFailure]) -> Optional[str]:
    order = {"none": 0, "weak": 1, "moderate": 2, "strong": 3, "decisive": 4}
    if not failures:
        return None
    return max(failures, key=lambda f: order.get(f.severity, 0)).severity


def classify_outcome(claim: dict, failures: list[HetvabhasaFailure], falsifier_state: str, targets: list[str]) -> tuple[str, bool, Optional[float], str]:
    if not targets:
        return "needs_review", False, None, "Claim has no explicit target."

    if falsifier_state in {"missing", "missing_condition", "invalid"}:
        return "hollow", False, 0.0, "Claim lacks a usable falsifier or truth-condition boundary."

    max_failure = strongest_failure(failures)
    if max_failure == "decisive":
        return "refuted", False, 0.0, "Claim is decisively defeated by gate checks."
    if max_failure == "strong":
        return "needs_review", False, 0.15, "Strong defect requires review before any posterior update."
    if max_failure == "moderate":
        return "accepted_with_penalty", True, 0.35, "Claim has moderate defects; cap effect unless reviewed."
    if max_failure == "weak":
        return "accepted_with_penalty", True, 0.6, "Claim has weak defects; preserve penalty in provenance."

    return "accepted", True, None, "Claim passes the minimum gate."


def normalize_nnexpr(expression: str) -> str:
    replacements = {
        "vyapti(": "vyāpti(",
        "bhedagrahana(": "bhedāgrahaṇa(",
        "svabhavapratibandha(": "svabhāvapratibandha(",
        "karya(": "kārya(",
        "visaya(": "viṣaya(",
        "nirupana(": "nirūpaṇa(",
        "svarupa(": "svarūpa(",
    }
    normalized = expression.strip()
    for plain, marked in replacements.items():
        if normalized.startswith(plain):
            return marked + normalized[len(plain):]
    return normalized


def parse_nnexpr_probe(claim: dict) -> NNExprProbe:
    expression = claim.get("nn_expr") or claim.get("nnexpr")
    if not expression:
        return NNExprProbe()
    original = str(expression).strip()
    normalized = normalize_nnexpr(original)
    try:
        from scripts.logic.bnf import parse_nnexpr
    except Exception as exc:  # pragma: no cover - import environment dependent
        return NNExprProbe(
            attempted=True,
            status="parser_unavailable",
            expression=original,
            normalized_expression=normalized,
            notes=f"Could not import NNExpr parser: {exc}",
        )

    parsed = parse_nnexpr(normalized)
    if parsed is None:
        return NNExprProbe(
            attempted=True,
            status="invalid",
            expression=original,
            normalized_expression=normalized,
            notes="NNExpr did not parse under the current grammar.",
        )
    return NNExprProbe(
        attempted=True,
        status="parsed",
        expression=original,
        normalized_expression=normalized,
        parsed_tree=parsed,
        notes="NNExpr parsed under the current grammar.",
    )


def requires_valid_nnexpr(claim: dict, pramana: str, dimension: str) -> bool:
    target_types = {
        str(target.get("target_type"))
        for target in claim.get("targets", []) or []
        if target.get("target_type")
    }
    text = str(claim.get("claim_text", "")).lower()
    source_type = str(claim.get("source_type", "")).lower()
    return (
        "bridge" in target_types
        or pramana == "formal_proof"
        or dimension == "formal"
        or source_type in FORMAL_SOURCE_TYPES
        or "bridge candidate" in text
        or "same formal node" in text
    )


def optional_formal_probe(claim: dict, enabled: bool, db_path: Optional[str]) -> FormalProbe:
    if not enabled:
        return FormalProbe()
    if not SANSKRITREE_ROOT.exists():
        return FormalProbe(attempted=True, status="UNKNOWN", notes="Sanskritree path not found.")

    sys.path.insert(0, str(SANSKRITREE_ROOT))
    try:
        from proof_engine import algorithm
        from proof_engine import db as proof_db
    except Exception as exc:  # pragma: no cover - environment dependent
        return FormalProbe(attempted=True, status="UNKNOWN", notes=f"Could not import Sanskritree proof engine: {exc}")

    try:
        conn = proof_db.init_db(db_path or ":memory:")
        node_id = algorithm.process_claim(
            conn,
            str(claim.get("claim_text", claim.get("claim_id", ""))),
            sanskrit=claim.get("sanskrit"),
            devanagari=claim.get("devanagari"),
            provenance={
                "tradition": infer_tradition_scope(claim),
                "source_id": claim.get("source_id"),
                "claim_id": claim.get("claim_id"),
            },
            is_sanskrit=bool(claim.get("sanskrit")),
            fast_mode=True,
            dev_mode=True,
        )
        node = proof_db.get_node(conn, node_id)
        return FormalProbe(
            attempted=True,
            status=str(node.get("status", "UNKNOWN")) if node else "UNKNOWN",
            node_id=node_id,
            notes=str(node.get("notes") or "") if node else "",
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return FormalProbe(attempted=True, status="UNKNOWN", notes=f"Formal probe failed: {exc}")


def gate_claim(claim: dict, peer_claims: list[dict], *, formal_probe: bool = False, sanskritree_db: Optional[str] = None) -> GateResult:
    claim_id = str(claim.get("claim_id") or claim.get("id") or "cl:unknown")
    targets = claim_targets(claim)
    tradition = infer_tradition_scope(claim)
    pramana = infer_pramana(claim)
    dimension = infer_dimension(claim, pramana)
    hetu, sadhya, vyapti, vyapti_conf = hetu_sadhya_vyapti(claim, targets)
    f_status = falsifier_status(claim)
    failures = check_hetvabhasa(claim, hetu, sadhya, vyapti_conf, peer_claims)
    falsifiers = tarka_falsifiers(claim, hetu, sadhya)
    nnexpr = parse_nnexpr_probe(claim)
    outcome, can_update, lbf_cap, reason = classify_outcome(
        claim,
        failures,
        f_status,
        targets,
    )
    probe = optional_formal_probe(claim, formal_probe, sanskritree_db)

    if probe.attempted and probe.status == "HOLLOW" and outcome == "accepted":
        outcome = "hollow"
        can_update = False
        lbf_cap = 0.0
        reason = "Sanskritree formal gate classified the claim as HOLLOW."
    elif probe.attempted and probe.status == "OUTSIDE_FORMAL" and outcome == "accepted":
        outcome = "outside_formal"
        reason = "Sanskritree formal gate found a formal boundary; non-formal evidence may still be reviewed."

    if (
        nnexpr.attempted
        and nnexpr.status != "parsed"
        and requires_valid_nnexpr(claim, pramana, dimension)
        and can_update
    ):
        outcome = "needs_review"
        can_update = False
        lbf_cap = None
        reason = "Claim requests formal/bridge status but its NNExpr did not parse."

    if tradition == "unknown" and can_update:
        outcome = "needs_review"
        can_update = False
        lbf_cap = None
        reason = "Claim lacks explicit tradition_scope, tradition, or paradigm."

    return GateResult(
        claim_id=claim_id,
        gate_version=GATE_VERSION,
        outcome=outcome,
        can_update_posterior=can_update,
        adjusted_lbf_cap=lbf_cap,
        evidence_dimension=dimension,
        pramana=pramana,
        tradition_scope=tradition,
        hetu=hetu,
        sadhya=sadhya,
        vyapti_statement=vyapti,
        vyapti_confidence=vyapti_conf,
        falsifier_status=f_status,
        failures=failures,
        tarka_falsifiers=falsifiers,
        nnexpr_probe=nnexpr,
        formal_probe=probe,
        reasoning=reason,
    )


def validate(
    claim: dict,
    peer_claims: Optional[list[dict]] = None,
    *,
    formal_probe: bool = False,
    sanskritree_db: Optional[str] = None,
) -> GateResult:
    """Stable test/API wrapper around `gate_claim`."""
    return gate_claim(
        claim,
        peer_claims or [claim],
        formal_probe=formal_probe,
        sanskritree_db=sanskritree_db,
    )


def result_to_json(result: GateResult) -> dict:
    data = asdict(result)
    data["failures"] = [asdict(f) for f in result.failures]
    data["tarka_falsifiers"] = [asdict(f) for f in result.tarka_falsifiers]
    data["nnexpr_probe"] = asdict(result.nnexpr_probe)
    data["formal_probe"] = asdict(result.formal_probe)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Nyaya-inspired pre-ingestion gates over truth-map claims."
    )
    parser.add_argument("input", help="Claim JSON, claims[] JSON, or information packet")
    parser.add_argument(
        "--formal-probe",
        action="store_true",
        help="Attempt optional Sanskritree proof-engine probe in fast/dev mode",
    )
    parser.add_argument(
        "--sanskritree-db",
        help="Optional Sanskritree proof-engine SQLite DB path for formal probing",
    )
    args = parser.parse_args()

    data = load_json(Path(args.input))
    claims = packet_claims(data)
    results = [
        result_to_json(
            gate_claim(
                claim,
                claims,
                formal_probe=args.formal_probe,
                sanskritree_db=args.sanskritree_db,
            )
        )
        for claim in claims
    ]
    print(json.dumps({"gate_version": GATE_VERSION, "results": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
