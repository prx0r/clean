#!/usr/bin/env python3
"""
Executable truth-map runtime for local validation.

This module uses a D1-shaped SQLite schema so the propagation loop can be
tested without Cloudflare credentials. It is intentionally small: the Python
engine remains the math reference, and this adapter proves the data loop.
"""

import importlib.util
import json
import math
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).parent
PROPAGATION_PATH = ROOT / "truthengine-propagation.py"
ARGUMENT_SCHEMA_PATH = ROOT / "truthmap-argument-schema.sql"


def _load_propagation_module():
    spec = importlib.util.spec_from_file_location(
        "truthengine_propagation", PROPAGATION_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


propagation = _load_propagation_module()
ClaimRecord = propagation.ClaimRecord
FeatureState = propagation.FeatureState
BasePropagationEngine = propagation.PropagationEngine
log_odds = propagation.log_odds
sigmoid = propagation.sigmoid


FEATURE_SEEDS = [
    ("F1", "consciousness_fundamental", 0.40),
    ("F2", "pattern_space_real", 0.55),
    ("F3", "pattern_space_nonphysical", 0.35),
    ("F4", "relations_ontologically_basic", 0.50),
    ("F5", "information_persists_across_instantiation", 0.12),
    ("F6", "teleology_real", 0.18),
    ("F7", "cross_life_continuity", 0.08),
    ("F8", "physical_law_emergent", 0.35),
]


BRANCH_PROFILES = {
    "B1": {"F2": "high", "F8": "high"},
    "B2": {"F1": "low", "F2": "low"},
    "B3": {"F2": "high", "F3": "high"},
    "B4": {
        "F1": "high",
        "F2": "high",
        "F3": "high",
        "F5": "high",
        "F6": "high",
        "F7": "high",
    },
    "B5": {"F4": "high"},
    "B6": {"F5": "high", "F7": "high"},
}

DISCRIMINATOR_SEEDS = [
    (
        "D1",
        "Does every fact about information content, semantic reference, and observer identity supervene on the complete physical causal state and its lawful evolution?",
        0.50,
        0.85,
        0.15,
    ),
    (
        "D2",
        "Are there macro-scale or process-level causal powers that are not merely compressed descriptions of microphysical transition dynamics?",
        0.50,
        0.80,
        0.20,
    ),
    (
        "D3",
        "Must the enabling condition for observer/object polarity include intrinsic phenomenal or reflexive manifestness, rather than only third-person structure?",
        0.50,
        0.90,
        0.10,
    ),
    (
        "D4",
        "Do mathematical or computational patterns have truth-making status independent of any particular physical instantiation or observer convention?",
        0.50,
        0.85,
        0.15,
    ),
    (
        "D5",
        "Can the identity-relevant organization of an observer persist across destruction, replacement, or discontinuity of the original biological substrate?",
        0.50,
        0.95,
        0.05,
    ),
]

DISCRIMINATOR_BRANCH_EFFECTS = {
    "D1": {
        "yes": {"B1": 0.45, "B2": 1.35, "B3": 0.15, "B4": 0.10, "B5": 0.85, "B6": 0.10},
        "no": {"B1": 1.05, "B2": 0.10, "B3": 1.25, "B4": 1.25, "B5": 1.15, "B6": 1.20},
    },
    "D2": {
        "yes": {"B1": 0.80, "B2": 0.20, "B3": 0.90, "B4": 1.05, "B5": 1.35, "B6": 1.00},
        "no": {"B1": 1.10, "B2": 1.25, "B3": 1.05, "B4": 0.80, "B5": 0.15, "B6": 0.75},
    },
    "D3": {
        "yes": {"B1": 0.20, "B2": 0.10, "B3": 0.35, "B4": 1.45, "B5": 0.45, "B6": 0.80},
        "no": {"B1": 1.15, "B2": 1.20, "B3": 1.10, "B4": 0.05, "B5": 1.10, "B6": 0.90},
    },
    "D4": {
        "yes": {"B1": 0.70, "B2": 0.25, "B3": 1.40, "B4": 0.85, "B5": 0.90, "B6": 1.15},
        "no": {"B1": 1.20, "B2": 1.25, "B3": 0.10, "B4": 1.05, "B5": 1.05, "B6": 0.25},
    },
    "D5": {
        "yes": {"B1": 0.80, "B2": 0.05, "B3": 1.15, "B4": 1.05, "B5": 0.85, "B6": 1.50},
        "no": {"B1": 1.10, "B2": 1.20, "B3": 0.80, "B4": 0.95, "B5": 1.05, "B6": 0.05},
    },
}

FEATURE_TO_DISCRIMINATOR_WEIGHTS = {
    "F1": {"D1": -0.35, "D3": 0.75},
    "F2": {"D1": -0.25, "D4": 0.70, "D5": 0.15},
    "F3": {"D1": -0.35, "D4": 0.80, "D5": 0.20},
    "F4": {"D1": -0.15, "D2": 0.70},
    "F5": {"D1": -0.45, "D4": 0.20, "D5": 0.75},
    "F6": {"D1": -0.20, "D2": 0.35, "D3": 0.20},
    "F7": {"D1": -0.35, "D3": 0.10, "D4": 0.15, "D5": 0.90},
    "F8": {"D1": -0.10, "D2": 0.15, "D4": 0.45},
}

DERIVED_DISCRIMINATOR_LBF_CAP = 0.6

EVIDENCE_DIMENSIONS = ("phenomenological", "empirical", "contemplative")

PARADIGM_DEFAULT_DIMENSIONS = {
    "trika": "phenomenological",
    "phenomenology": "phenomenological",
    "analytic_philosophy": "phenomenological",
    "buddhist_logic": "phenomenological",
    "madhyamaka": "phenomenological",
    "vedanta": "phenomenological",
    "hermeneutics": "phenomenological",
    "neuroscience": "empirical",
    "neuropsychology": "empirical",
    "active_inference": "empirical",
    "predictive_processing": "empirical",
    "iit": "empirical",
    "gnwt": "empirical",
    "high_energy_physics": "empirical",
    "information_theory": "empirical",
    "physical_closure": "empirical",
    "identity_continuity": "empirical",
    "lab": "empirical",
    "independent": "empirical",
    "contemplative": "contemplative",
    "meditation": "contemplative",
    "nondual_practice": "contemplative",
    "practitioner_report": "contemplative",
}


QUESTION_FEATURES = {
    "q:consciousness-fundamental": ["F1"],
    "q:brain-filter-or-appearance": ["F1", "F4"],
    "q:iccha-jnana-kriya-necessary": ["F4", "F6"],
    "q:nondual-awareness-reality-or-plasticity": ["F1", "F4"],
    "q:prakasa-definition": ["F1", "F3"],
    "q:svatantrya-explanation": ["F6", "F8"],
}


QUESTION_BRANCHES = {
    "q:consciousness-fundamental": ["B2", "B4"],
    "q:brain-filter-or-appearance": ["B2", "B4", "B5"],
    "q:iccha-jnana-kriya-necessary": ["B4", "B5"],
    "q:nondual-awareness-reality-or-plasticity": ["B2", "B4", "B5"],
    "q:prakasa-definition": ["B3", "B4"],
    "q:svatantrya-explanation": ["B1", "B4"],
}


SEED_CLAIMS = [
    {
        "claim_id": "cl:q-consciousness-fundamental-trika-ground",
        "question_id": "q:consciousness-fundamental",
        "features": ["F1"],
        "source_type": "ro",
        "source_id": "ro:utpaladeva-ipk",
        "claim_text": "Trika treats prakasa-vimarsa consciousness as the ground of manifestation.",
        "log_bayes_factor": 0.55,
        "w_rel": 0.85,
        "w_map": 0.65,
        "w_aux": 0.70,
        "paradigm": "trika",
    },
    {
        "claim_id": "cl:q-consciousness-fundamental-hard-problem",
        "question_id": "q:consciousness-fundamental",
        "features": ["F1"],
        "source_type": "ro",
        "source_id": "ro:hard-problem",
        "claim_text": "The hard problem keeps reductionist explanations underdetermined.",
        "log_bayes_factor": 0.35,
        "w_rel": 0.75,
        "w_map": 0.55,
        "w_aux": 0.60,
        "paradigm": "phenomenology",
    },
    {
        "claim_id": "cl:q-consciousness-fundamental-brain-damage",
        "question_id": "q:consciousness-fundamental",
        "features": ["F1"],
        "source_type": "ro",
        "source_id": "ro:neuropsychology",
        "claim_text": "Brain damage strongly couples conscious capacity to physical brain state.",
        "log_bayes_factor": -0.70,
        "w_rel": 0.90,
        "w_map": 0.75,
        "w_aux": 0.80,
        "paradigm": "neuroscience",
    },
    {
        "claim_id": "cl:q-brain-filter-active-inference",
        "question_id": "q:brain-filter-or-appearance",
        "features": ["F4"],
        "source_type": "ro",
        "source_id": "ro:active-inference",
        "claim_text": "Predictive processing models the brain as an inferential interface.",
        "log_bayes_factor": 0.45,
        "w_rel": 0.80,
        "w_map": 0.70,
        "w_aux": 0.65,
        "paradigm": "active_inference",
    },
    {
        "claim_id": "cl:q-iccha-active-inference-map",
        "question_id": "q:iccha-jnana-kriya-necessary",
        "features": ["F4", "F6"],
        "source_type": "ro",
        "source_id": "ro:active-inference",
        "claim_text": "Iccha-jnana-kriya maps structurally onto preference-model-policy.",
        "log_bayes_factor": 0.50,
        "w_rel": 0.75,
        "w_map": 0.65,
        "w_aux": 0.60,
        "paradigm": "active_inference",
    },
    {
        "claim_id": "cl:q-nondual-self-model-plasticity",
        "question_id": "q:nondual-awareness-reality-or-plasticity",
        "features": ["F1"],
        "source_type": "ro",
        "source_id": "ro:minimal-phenomenal-experience",
        "claim_text": "Nondual reports can be explained by attenuation of high-level self-models.",
        "log_bayes_factor": -0.45,
        "w_rel": 0.85,
        "w_map": 0.60,
        "w_aux": 0.65,
        "paradigm": "phenomenology",
    },
    {
        "claim_id": "cl:q-prakasa-manifestness",
        "question_id": "q:prakasa-definition",
        "features": ["F1", "F3"],
        "source_type": "ro",
        "source_id": "ro:hermeneutics-of-absolute",
        "claim_text": "Prakasa is better read as manifestness or self-revealing presence.",
        "log_bayes_factor": 0.40,
        "w_rel": 0.80,
        "w_map": 0.70,
        "w_aux": 0.70,
        "paradigm": "trika",
    },
    {
        "claim_id": "cl:q-svatantrya-no-external-constraint",
        "question_id": "q:svatantrya-explanation",
        "features": ["F6"],
        "source_type": "ro",
        "source_id": "ro:matter-of-wonder",
        "claim_text": "Svatantrya rules out external compulsion but may not explain manifestation.",
        "log_bayes_factor": -0.25,
        "w_rel": 0.70,
        "w_map": 0.55,
        "w_aux": 0.65,
        "paradigm": "trika",
    },
]


def status_from_confidence(confidence: float) -> str:
    if confidence >= 0.75:
        return "strongly_supported"
    if confidence >= 0.55:
        return "plausible"
    if confidence <= 0.20:
        return "incompatible"
    return "underdetermined"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def discriminator_status(probability_yes: float, threshold_yes: float, threshold_no: float) -> str:
    if probability_yes >= threshold_yes or probability_yes <= threshold_no:
        return "answered"
    return "open"


def feature_projection_from_probs(
    profile: Dict[str, str],
    feature_probs: Dict[str, float],
) -> float:
    prob = 1.0
    for fid, level in profile.items():
        if fid not in feature_probs:
            continue
        fp = feature_probs[fid]
        if level == "high":
            prob *= fp
        elif level == "low":
            prob *= 1.0 - fp
    return prob


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    total = sum(scores.values())
    if total == 0:
        n = len(scores)
        return {key: 1.0 / n for key in scores}
    return {key: value / total for key, value in scores.items()}


def expected_branch_effect(probability_yes: float, yes_multiplier: float, no_multiplier: float) -> float:
    return probability_yes * yes_multiplier + (1.0 - probability_yes) * no_multiplier


def infer_evidence_dimension(paradigm: Optional[str]) -> str:
    if not paradigm:
        return "empirical"
    return PARADIGM_DEFAULT_DIMENSIONS.get(paradigm.lower(), "empirical")


def validate_evidence_dimension(dimension: Optional[str], paradigm: Optional[str]) -> str:
    resolved = dimension or infer_evidence_dimension(paradigm)
    if resolved not in EVIDENCE_DIMENSIONS:
        allowed = ", ".join(EVIDENCE_DIMENSIONS)
        raise ValueError(f"unknown evidence_dimension {resolved!r}; expected one of {allowed}")
    return resolved


def compute_convergence(dimension_probs: Dict[str, float]) -> float:
    """Agreement across bounded probability estimates.

    The score is 1.0 when dimensions agree and approaches 0.0 when one
    dimension is maximally separated from the rest. It is a disagreement
    diagnostic, not a hidden confidence multiplier.
    """
    probs = list(dimension_probs.values())
    if len(probs) < 2:
        return 1.0
    mean = sum(probs) / len(probs)
    variance = sum((p - mean) ** 2 for p in probs) / len(probs)
    max_variance = (len(probs) - 1) / (len(probs) ** 2)
    if max_variance == 0:
        return 1.0
    return clamp(1.0 - (variance / max_variance), 0.0, 1.0)


class TruthMapSQLiteDB:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def create_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS truth_map_questions (
              question_id TEXT PRIMARY KEY,
              question TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'unasked',
              confidence REAL NOT NULL DEFAULT 0.0,
              feature_ids TEXT NOT NULL DEFAULT '[]',
              branches TEXT NOT NULL DEFAULT '[]',
              parent_question TEXT,
              best_answer TEXT,
              last_updated TEXT,
              last_updated_by TEXT
            );

            CREATE TABLE IF NOT EXISTS claims (
              claim_id TEXT PRIMARY KEY,
              schema_version INTEGER NOT NULL DEFAULT 1,
              source_type TEXT NOT NULL,
              source_id TEXT NOT NULL,
              evidence_role TEXT NOT NULL DEFAULT 'primary',
              evidence_dimension TEXT NOT NULL DEFAULT 'empirical',
              source_cluster TEXT,
              method_family TEXT,
              target_question_id TEXT,
              log_bayes_factor REAL NOT NULL,
              w_rel REAL NOT NULL DEFAULT 1.0,
              w_map REAL NOT NULL DEFAULT 1.0,
              w_aux REAL NOT NULL DEFAULT 1.0,
              paradigm TEXT,
              claim_text TEXT NOT NULL,
              falsifier TEXT,
              is_retracted INTEGER NOT NULL DEFAULT 0,
              supersedes TEXT,
              superseded_by TEXT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              extracted_by TEXT,
              FOREIGN KEY (target_question_id) REFERENCES truth_map_questions(question_id)
            );

            CREATE TABLE IF NOT EXISTS claim_features (
              claim_id TEXT NOT NULL,
              feature_id TEXT NOT NULL,
              PRIMARY KEY (claim_id, feature_id),
              FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
            );

            CREATE TABLE IF NOT EXISTS feature_states (
              feature_id TEXT PRIMARY KEY,
              label TEXT NOT NULL,
              prior_log_odds REAL NOT NULL,
              current_log_odds REAL NOT NULL,
              probability REAL NOT NULL,
              last_updated TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS branch_probabilities (
              branch_id TEXT PRIMARY KEY,
              label TEXT NOT NULL,
              probability REAL NOT NULL,
              score_type TEXT NOT NULL DEFAULT 'relative_support',
              last_updated TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS branch_profiles (
              branch_id TEXT NOT NULL,
              feature_id TEXT NOT NULL,
              level TEXT NOT NULL CHECK(level IN ('high','low','agnostic')),
              PRIMARY KEY (branch_id, feature_id)
            );

            CREATE TABLE IF NOT EXISTS discriminators (
              discriminator_id TEXT PRIMARY KEY,
              question TEXT NOT NULL,
              prior_log_odds REAL NOT NULL,
              current_log_odds REAL NOT NULL,
              probability_yes REAL NOT NULL,
              threshold_yes REAL NOT NULL,
              threshold_no REAL NOT NULL,
              status TEXT NOT NULL DEFAULT 'open',
              last_updated TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS discriminator_branch_effects (
              discriminator_id TEXT NOT NULL,
              answer TEXT NOT NULL CHECK(answer IN ('yes', 'no')),
              branch_id TEXT NOT NULL,
              multiplier REAL NOT NULL,
              PRIMARY KEY (discriminator_id, answer, branch_id),
              FOREIGN KEY (discriminator_id) REFERENCES discriminators(discriminator_id)
            );

            CREATE TABLE IF NOT EXISTS claim_targets (
              claim_id TEXT NOT NULL,
              target_id TEXT NOT NULL,
              target_type TEXT NOT NULL CHECK(target_type IN ('feature', 'discriminator')),
              evidence_role TEXT NOT NULL DEFAULT 'direct',
              PRIMARY KEY (claim_id, target_id),
              FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
            );

            CREATE INDEX IF NOT EXISTS idx_claims_question ON claims(target_question_id);
            CREATE INDEX IF NOT EXISTS idx_claims_paradigm ON claims(paradigm);
            CREATE INDEX IF NOT EXISTS idx_claims_supersedes ON claims(supersedes);
            CREATE INDEX IF NOT EXISTS idx_claim_features_feature ON claim_features(feature_id);
            CREATE INDEX IF NOT EXISTS idx_claim_targets_target ON claim_targets(target_id, target_type);
            """
        )
        self._ensure_column(
            "claims",
            "evidence_dimension",
            "TEXT NOT NULL DEFAULT 'empirical'",
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_dimension ON claims(evidence_dimension)"
        )
        self.conn.commit()

    def create_argument_schema(
        self,
        schema_path: Path = ARGUMENT_SCHEMA_PATH,
    ) -> None:
        self.conn.executescript(schema_path.read_text(encoding="utf-8"))
        self.conn.commit()

    def _ensure_column(self, table: str, column: str, declaration: str) -> None:
        rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        if column in {row["name"] for row in rows}:
            return
        self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")

    def seed_features_and_branches(self) -> None:
        for fid, label, prior in FEATURE_SEEDS:
            lo = log_odds(prior)
            self.conn.execute(
                """
                INSERT OR REPLACE INTO feature_states
                (feature_id, label, prior_log_odds, current_log_odds, probability)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fid, label, lo, lo, prior),
            )

        for bid, profile in BRANCH_PROFILES.items():
            self.conn.execute(
                """
                INSERT OR REPLACE INTO branch_probabilities
                (branch_id, label, probability, score_type)
                VALUES (?, ?, 0.0, 'relative_support')
                """,
                (bid, bid),
            )
            for fid, level in profile.items():
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO branch_profiles (branch_id, feature_id, level)
                    VALUES (?, ?, ?)
                    """,
                    (bid, fid, level),
                )
        self.conn.commit()

    def seed_discriminators(self) -> None:
        for did, question, prior, threshold_yes, threshold_no in DISCRIMINATOR_SEEDS:
            lo = log_odds(prior)
            self.conn.execute(
                """
                INSERT OR REPLACE INTO discriminators
                (discriminator_id, question, prior_log_odds, current_log_odds,
                 probability_yes, threshold_yes, threshold_no, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
                """,
                (did, question, lo, lo, prior, threshold_yes, threshold_no),
            )

        for did, answer_map in DISCRIMINATOR_BRANCH_EFFECTS.items():
            for answer, branch_map in answer_map.items():
                for bid, multiplier in branch_map.items():
                    self.conn.execute(
                        """
                        INSERT OR REPLACE INTO discriminator_branch_effects
                        (discriminator_id, answer, branch_id, multiplier)
                        VALUES (?, ?, ?, ?)
                        """,
                        (did, answer, bid, multiplier),
                    )
        self.conn.commit()

    def seed_questions_from_files(
        self, source_dir: Path = ROOT / "content" / "source-metaphysics"
    ) -> None:
        for path in sorted(source_dir.glob("q-*.json")):
            data = json.loads(path.read_text())
            artifact_type = data.get("artifact_type")
            if artifact_type and artifact_type != "truth_map_question":
                continue
            if "question_id" not in data or "question" not in data:
                continue
            qid = data["question_id"]
            feature_ids = QUESTION_FEATURES.get(qid, [])
            branches = QUESTION_BRANCHES.get(qid, [])
            self.conn.execute(
                """
                INSERT OR REPLACE INTO truth_map_questions
                (question_id, question, status, confidence, feature_ids, branches,
                 parent_question, best_answer, last_updated, last_updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    qid,
                    data["question"],
                    data.get("status", "unasked"),
                    float(data.get("confidence", 0.0)),
                    json.dumps(feature_ids),
                    json.dumps(branches),
                    data.get("parent_question"),
                    data.get("best_answer"),
                    data.get("last_updated"),
                    data.get("last_updated_by"),
                ),
            )
        self.conn.commit()

    def seed_claims(self, claims: Optional[List[dict]] = None) -> None:
        for claim in claims or SEED_CLAIMS:
            self.add_claim_dict(claim)
        self.conn.commit()

    def _claim_targets(self, claim: dict) -> tuple[List[str], List[str]]:
        if "targets" in claim:
            feature_ids: List[str] = []
            discriminator_ids: List[str] = []
            for target in claim.get("targets", []):
                target_id = target.get("target_id")
                target_type = target.get("target_type")
                if target_type == "feature" and target_id:
                    feature_ids.append(target_id)
                elif target_type == "discriminator" and target_id:
                    discriminator_ids.append(target_id)
            return feature_ids, discriminator_ids

        return (
            list(claim.get("features") or claim.get("target_feature_ids") or []),
            list(claim.get("discriminators") or claim.get("target_discriminator_ids") or []),
        )

    def add_claim_dict(self, claim: dict) -> None:
        feature_ids, discriminator_ids = self._claim_targets(claim)
        if not feature_ids and not discriminator_ids:
            raise ValueError(f"claim {claim['claim_id']} has no feature or discriminator targets")
        evidence_dimension = validate_evidence_dimension(
            claim.get("evidence_dimension"),
            claim.get("paradigm"),
        )

        falsifier = claim.get("falsifier") or {
            "type": "textual",
            "condition": "A stronger source or result defeats this claim.",
            "status": "untested",
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO claims
            (claim_id, source_type, source_id, evidence_role, evidence_dimension,
             source_cluster, method_family, target_question_id, log_bayes_factor,
             w_rel, w_map, w_aux, paradigm, claim_text, falsifier, is_retracted,
             supersedes, superseded_by, extracted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim["claim_id"],
                claim.get("source_type", "ro"),
                claim.get("source_id", "ro:unknown"),
                claim.get("evidence_role", "primary"),
                evidence_dimension,
                claim.get("source_cluster"),
                claim.get("method_family"),
                claim.get("question_id"),
                claim["log_bayes_factor"],
                claim.get("w_rel", 1.0),
                claim.get("w_map", 1.0),
                claim.get("w_aux", 1.0),
                claim.get("paradigm"),
                claim.get("claim_text", claim["claim_id"]),
                json.dumps(falsifier),
                int(claim.get("is_retracted", False)),
                claim.get("supersedes"),
                claim.get("superseded_by"),
                claim.get("extracted_by", "seed"),
            ),
        )
        self.conn.execute("DELETE FROM claim_features WHERE claim_id = ?", (claim["claim_id"],))
        self.conn.execute("DELETE FROM claim_targets WHERE claim_id = ?", (claim["claim_id"],))
        for fid in feature_ids:
            self.conn.execute(
                "INSERT INTO claim_features (claim_id, feature_id) VALUES (?, ?)",
                (claim["claim_id"], fid),
            )
            self.conn.execute(
                """
                INSERT INTO claim_targets (claim_id, target_id, target_type, evidence_role)
                VALUES (?, ?, 'feature', 'direct')
                """,
                (claim["claim_id"], fid),
            )
        for did in discriminator_ids:
            self.conn.execute(
                """
                INSERT INTO claim_targets (claim_id, target_id, target_type, evidence_role)
                VALUES (?, ?, 'discriminator', 'direct')
                """,
                (claim["claim_id"], did),
            )

    def add_claim(self, claim: ClaimRecord) -> None:
        self.add_claim_dict(
            {
                "claim_id": claim.id,
                "question_id": claim.target_question_id,
                "features": claim.target_feature_ids,
                "log_bayes_factor": claim.log_bayes_factor,
                "w_rel": claim.w_rel,
                "w_map": claim.w_map,
                "w_aux": claim.w_aux,
                "paradigm": claim.paradigm,
                "evidence_dimension": infer_evidence_dimension(claim.paradigm),
                "source_cluster": claim.source_cluster,
                "method_family": claim.method_family,
                "claim_text": claim.id,
                "is_retracted": claim.is_retracted,
            }
        )
        self.conn.commit()

    def supersede_claim(self, old_claim_id: str, new_claim: dict) -> None:
        self.conn.execute(
            "UPDATE claims SET is_retracted = 1, superseded_by = ? WHERE claim_id = ?",
            (new_claim["claim_id"], old_claim_id),
        )
        new_claim = dict(new_claim)
        new_claim["supersedes"] = old_claim_id
        self.add_claim_dict(new_claim)
        self.conn.commit()

    def get_all_features(self) -> List[FeatureState]:
        rows = self.conn.execute(
            """
            SELECT feature_id, prior_log_odds, current_log_odds
            FROM feature_states
            ORDER BY feature_id
            """
        ).fetchall()
        return [
            FeatureState(
                id=row["feature_id"],
                prior_log_odds=row["prior_log_odds"],
                log_odds_val=row["current_log_odds"],
            )
            for row in rows
        ]

    def get_all_claims(self) -> List[ClaimRecord]:
        rows = self.conn.execute(
            """
            SELECT c.*, cf.feature_id
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.is_retracted = 0
            ORDER BY c.created_at, c.claim_id, cf.feature_id
            """
        ).fetchall()
        return self._rows_to_claims(rows)

    def get_all_claims_with_targets(self) -> List[dict]:
        rows = self.conn.execute(
            """
            SELECT c.*, ct.target_id, ct.target_type
            FROM claims c
            JOIN claim_targets ct ON ct.claim_id = c.claim_id
            WHERE c.is_retracted = 0
            ORDER BY c.created_at, c.claim_id, ct.target_type, ct.target_id
            """
        ).fetchall()
        grouped: Dict[str, dict] = {}
        for row in rows:
            cid = row["claim_id"]
            if cid not in grouped:
                grouped[cid] = {
                    "claim_id": cid,
                    "source_type": row["source_type"],
                    "source_id": row["source_id"],
                    "claim_text": row["claim_text"],
                    "log_bayes_factor": row["log_bayes_factor"],
                    "w_rel": row["w_rel"],
                    "w_map": row["w_map"],
                    "w_aux": row["w_aux"],
                    "paradigm": row["paradigm"],
                    "evidence_dimension": row["evidence_dimension"],
                    "features": [],
                    "discriminators": [],
                }
            if row["target_type"] == "feature":
                grouped[cid]["features"].append(row["target_id"])
            elif row["target_type"] == "discriminator":
                grouped[cid]["discriminators"].append(row["target_id"])
        return list(grouped.values())

    def get_all_discriminators(self) -> List[FeatureState]:
        rows = self.conn.execute(
            """
            SELECT discriminator_id, prior_log_odds, current_log_odds
            FROM discriminators
            ORDER BY discriminator_id
            """
        ).fetchall()
        return [
            FeatureState(
                id=row["discriminator_id"],
                prior_log_odds=row["prior_log_odds"],
                log_odds_val=row["current_log_odds"],
            )
            for row in rows
        ]

    def get_discriminator_thresholds(self) -> Dict[str, tuple[float, float]]:
        rows = self.conn.execute(
            "SELECT discriminator_id, threshold_yes, threshold_no FROM discriminators"
        ).fetchall()
        return {
            row["discriminator_id"]: (row["threshold_yes"], row["threshold_no"])
            for row in rows
        }

    def get_discriminator_branch_effects(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        rows = self.conn.execute(
            """
            SELECT discriminator_id, answer, branch_id, multiplier
            FROM discriminator_branch_effects
            ORDER BY discriminator_id, answer, branch_id
            """
        ).fetchall()
        effects: Dict[str, Dict[str, Dict[str, float]]] = {}
        for row in rows:
            effects.setdefault(row["discriminator_id"], {}).setdefault(row["answer"], {})[
                row["branch_id"]
            ] = row["multiplier"]
        return effects

    def get_claims_by_ids(self, claim_ids: List[str]) -> List[ClaimRecord]:
        if not claim_ids:
            return []
        placeholders = ",".join("?" for _ in claim_ids)
        rows = self.conn.execute(
            f"""
            SELECT c.*, cf.feature_id
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.claim_id IN ({placeholders})
            ORDER BY c.created_at, c.claim_id, cf.feature_id
            """,
            claim_ids,
        ).fetchall()
        return self._rows_to_claims(rows)

    def _rows_to_claims(self, rows: Iterable[sqlite3.Row]) -> List[ClaimRecord]:
        grouped: Dict[str, dict] = {}
        for row in rows:
            cid = row["claim_id"]
            if cid not in grouped:
                grouped[cid] = {"row": row, "features": []}
            grouped[cid]["features"].append(row["feature_id"])

        claims = []
        for cid, data in grouped.items():
            row = data["row"]
            claims.append(
                ClaimRecord(
                    id=cid,
                    target_feature_ids=data["features"],
                    log_bayes_factor=row["log_bayes_factor"],
                    w_rel=row["w_rel"],
                    w_map=row["w_map"],
                    w_aux=row["w_aux"],
                    paradigm=row["paradigm"],
                    is_retracted=bool(row["is_retracted"]),
                    target_question_id=row["target_question_id"],
                    source_cluster=row["source_cluster"],
                    method_family=row["method_family"],
                )
            )
        return claims

    def count_claims_by_paradigm(self, feature_id: str, paradigm: str) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.is_retracted = 0
              AND cf.feature_id = ?
              AND c.paradigm = ?
            """,
            (feature_id, paradigm),
        ).fetchone()
        return int(row["cnt"])

    def bulk_dependence_counts(
        self,
        feature_ids: List[str],
        paradigms: List[str],
        exclude_claim_ids: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, int]]:
        counts: Dict[str, Dict[str, int]] = {fid: {} for fid in feature_ids}
        if not feature_ids or not paradigms:
            return counts

        feature_placeholders = ",".join("?" for _ in feature_ids)
        paradigm_placeholders = ",".join("?" for _ in paradigms)
        params: List[str] = list(feature_ids) + list(paradigms)
        exclusion = ""
        if exclude_claim_ids:
            exclusion_placeholders = ",".join("?" for _ in exclude_claim_ids)
            exclusion = f"AND c.claim_id NOT IN ({exclusion_placeholders})"
            params.extend(exclude_claim_ids)

        rows = self.conn.execute(
            f"""
            SELECT cf.feature_id, c.paradigm, COUNT(*) AS claim_count
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.is_retracted = 0
              AND cf.feature_id IN ({feature_placeholders})
              AND c.paradigm IN ({paradigm_placeholders})
              {exclusion}
            GROUP BY cf.feature_id, c.paradigm
            """,
            params,
        ).fetchall()
        for row in rows:
            counts[row["feature_id"]][row["paradigm"]] = int(row["claim_count"])
        return counts

    def save_features(self, features: Dict[str, FeatureState]) -> None:
        self.conn.executemany(
            """
            UPDATE feature_states
            SET current_log_odds = ?, probability = ?, last_updated = datetime('now')
            WHERE feature_id = ?
            """,
            [(f.log_odds, f.probability, fid) for fid, f in features.items()],
        )
        self.conn.commit()

    def save_discriminators(self, discriminators: Dict[str, FeatureState]) -> None:
        thresholds = self.get_discriminator_thresholds()
        updates = []
        for did, discriminator in discriminators.items():
            threshold_yes, threshold_no = thresholds[did]
            updates.append(
                (
                    discriminator.log_odds,
                    discriminator.probability,
                    discriminator_status(
                        discriminator.probability,
                        threshold_yes,
                        threshold_no,
                    ),
                    did,
                )
            )
        self.conn.executemany(
            """
            UPDATE discriminators
            SET current_log_odds = ?, probability_yes = ?, status = ?,
                last_updated = datetime('now')
            WHERE discriminator_id = ?
            """,
            updates,
        )
        self.conn.commit()

    def save_question_states(self, features: Dict[str, FeatureState]) -> None:
        rows = self.conn.execute(
            "SELECT question_id, feature_ids FROM truth_map_questions"
        ).fetchall()
        updates = []
        for row in rows:
            feature_ids = json.loads(row["feature_ids"])
            probabilities = [
                features[fid].probability for fid in feature_ids if fid in features
            ]
            if not probabilities:
                continue
            confidence = sum(probabilities) / len(probabilities)
            updates.append(
                (
                    confidence,
                    status_from_confidence(confidence),
                    row["question_id"],
                )
            )
        self.conn.executemany(
            """
            UPDATE truth_map_questions
            SET confidence = ?, status = ?, last_updated = date('now'),
                last_updated_by = 'propagation'
            WHERE question_id = ?
            """,
            updates,
        )
        self.conn.commit()

    def get_branch_feature_profiles(self) -> Dict[str, Dict[str, str]]:
        rows = self.conn.execute(
            "SELECT branch_id, feature_id, level FROM branch_profiles"
        ).fetchall()
        profiles: Dict[str, Dict[str, str]] = {}
        for row in rows:
            profiles.setdefault(row["branch_id"], {})[row["feature_id"]] = row["level"]
        return profiles

    def save_branch_probabilities(self, branch_probs: Dict[str, float]) -> None:
        self.conn.executemany(
            """
            UPDATE branch_probabilities
            SET probability = ?, score_type = 'relative_support',
                last_updated = datetime('now')
            WHERE branch_id = ?
            """,
            [(prob, bid) for bid, prob in branch_probs.items()],
        )
        self.conn.commit()

    def question_state(self, question_id: str) -> sqlite3.Row:
        return self.conn.execute(
            """
            SELECT question_id, confidence, status, feature_ids
            FROM truth_map_questions
            WHERE question_id = ?
            """,
            (question_id,),
        ).fetchone()

    def branch_state(self, branch_id: str) -> sqlite3.Row:
        return self.conn.execute(
            """
            SELECT branch_id, probability, score_type
            FROM branch_probabilities
            WHERE branch_id = ?
            """,
            (branch_id,),
        ).fetchone()

    def discriminator_state(self, discriminator_id: str) -> sqlite3.Row:
        return self.conn.execute(
            """
            SELECT discriminator_id, probability_yes, status,
                   current_log_odds, threshold_yes, threshold_no
            FROM discriminators
            WHERE discriminator_id = ?
            """,
            (discriminator_id,),
        ).fetchone()

    def count_discriminator_effects(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM discriminator_branch_effects"
        ).fetchone()
        return int(row["cnt"])


class PropagationEngine:
    """SQLite runtime wrapper that adds the D1-D5 cascade above F1-F8."""

    def __init__(self, db: TruthMapSQLiteDB, dep_alpha: float = 0.5):
        self.db = db
        self.dep_alpha = dep_alpha
        self.feature_engine = BasePropagationEngine(db, dep_alpha=dep_alpha)

    def contribution_trace(
        self,
        source_id: Optional[str] = None,
        claim_id: Optional[str] = None,
    ) -> List[dict]:
        """Replay active claims and return per-target contribution records.

        This is the belief-provenance path: it exposes the exact weight
        decomposition used during propagation without mutating persisted state.
        """
        features_by_dimension = self._initial_features_by_dimension()
        discriminators_by_dimension = self._initial_discriminators_by_dimension()
        feature_counts: Dict[str, Dict[str, Dict[str, int]]] = {
            dimension: {} for dimension in EVIDENCE_DIMENSIONS
        }
        discriminator_counts: Dict[str, Dict[str, Dict[str, int]]] = {
            dimension: {} for dimension in EVIDENCE_DIMENSIONS
        }
        trace: List[dict] = []

        for claim in self.db.get_all_claims_with_targets():
            dimension = claim["evidence_dimension"]
            features = features_by_dimension[dimension]
            discriminators = discriminators_by_dimension[dimension]
            matches = (
                (source_id is None or claim["source_id"] == source_id)
                and (claim_id is None or claim["claim_id"] == claim_id)
            )
            base_lbf = self._claim_base_lbf(claim)

            for fid in claim["features"]:
                if fid not in features:
                    continue
                w_dep = self._target_dep_weight(
                    feature_counts[dimension],
                    fid,
                    claim["paradigm"],
                )
                before = features[fid].probability
                branch_before = self._branch_support_snapshot(features, discriminators)
                effective_lbf = base_lbf * w_dep
                features[fid].update(effective_lbf)
                after = features[fid].probability
                branch_after = self._branch_support_snapshot(features, discriminators)
                self._increment_target_count(
                    feature_counts[dimension],
                    fid,
                    claim["paradigm"],
                )
                if matches:
                    trace.append(
                        self._trace_record(
                            claim,
                            target_id=fid,
                            target_type="feature",
                            evidence_role="direct",
                            base_lbf=base_lbf,
                            w_dep=w_dep,
                            effective_lbf=effective_lbf,
                            posterior_before=before,
                            posterior_after=after,
                            branch_support_before=branch_before,
                            branch_support_after=branch_after,
                        )
                    )

            direct_discriminators = {
                did for did in claim["discriminators"] if did in discriminators
            }
            for did in direct_discriminators:
                w_dep = self._target_dep_weight(
                    discriminator_counts[dimension],
                    did,
                    claim["paradigm"],
                )
                before = discriminators[did].probability
                branch_before = self._branch_support_snapshot(features, discriminators)
                effective_lbf = base_lbf * w_dep
                discriminators[did].update(effective_lbf)
                after = discriminators[did].probability
                branch_after = self._branch_support_snapshot(features, discriminators)
                self._increment_target_count(
                    discriminator_counts[dimension],
                    did,
                    claim["paradigm"],
                )
                if matches:
                    trace.append(
                        self._trace_record(
                            claim,
                            target_id=did,
                            target_type="discriminator",
                            evidence_role="direct",
                            base_lbf=base_lbf,
                            w_dep=w_dep,
                            effective_lbf=effective_lbf,
                            posterior_before=before,
                            posterior_after=after,
                            branch_support_before=branch_before,
                            branch_support_after=branch_after,
                        )
                    )

            derived_targets = self._derived_targets_for_claim(
                claim["features"],
                direct_discriminators,
                base_lbf,
            )
            for did, derived_lbf in derived_targets.items():
                if did not in discriminators:
                    continue
                w_dep = self._target_dep_weight(
                    discriminator_counts[dimension],
                    did,
                    claim["paradigm"],
                )
                before = discriminators[did].probability
                branch_before = self._branch_support_snapshot(features, discriminators)
                effective_lbf = clamp(
                    derived_lbf * w_dep,
                    -DERIVED_DISCRIMINATOR_LBF_CAP,
                    DERIVED_DISCRIMINATOR_LBF_CAP,
                )
                discriminators[did].update(effective_lbf)
                after = discriminators[did].probability
                branch_after = self._branch_support_snapshot(features, discriminators)
                self._increment_target_count(
                    discriminator_counts[dimension],
                    did,
                    claim["paradigm"],
                )
                if matches:
                    trace.append(
                        self._trace_record(
                            claim,
                            target_id=did,
                            target_type="discriminator",
                            evidence_role="derived_mapping",
                            base_lbf=derived_lbf,
                            w_dep=w_dep,
                            effective_lbf=effective_lbf,
                            posterior_before=before,
                            posterior_after=after,
                            branch_support_before=branch_before,
                            branch_support_after=branch_after,
                        )
                    )

        return trace

    def blame(self, target_id: str) -> List[dict]:
        rows = [
            row for row in self.contribution_trace() if row["target_id"] == target_id
        ]
        rows.sort(key=lambda row: abs(row["effective_lbf"]), reverse=True)
        return rows

    def run(self, new_claim_ids: Optional[List[str]] = None) -> dict:
        base_result = self.feature_engine.run(new_claim_ids=new_claim_ids)
        discriminators, discriminator_claims_processed = self._recompute_discriminators()
        feature_probs = {f.id: f.probability for f in self.db.get_all_features()}
        branch_support = self._derive_branch_support(feature_probs, discriminators)
        dimensional = self._recompute_dimension_state()

        self.db.save_discriminators(discriminators)
        self.db.save_branch_probabilities(branch_support)

        return {
            "features": base_result["features"],
            "discriminators": {
                did: discriminator.probability
                for did, discriminator in discriminators.items()
            },
            "branches": branch_support,
            "claims_processed": base_result["claims_processed"],
            "discriminator_claims_processed": discriminator_claims_processed,
            "paradigm_counts": base_result["paradigm_counts"],
            "dimension_features": dimensional["features"],
            "dimension_discriminators": dimensional["discriminators"],
            "dimension_branches": dimensional["branches"],
            "dimension_convergence": dimensional["convergence"],
            "dimension_claims_processed": dimensional["claims_processed"],
        }

    def _recompute_dimension_state(self) -> dict:
        features_by_dimension = self._initial_features_by_dimension()
        discriminators_by_dimension = self._initial_discriminators_by_dimension()
        feature_counts: Dict[str, Dict[str, Dict[str, int]]] = {
            dimension: {} for dimension in EVIDENCE_DIMENSIONS
        }
        discriminator_counts: Dict[str, Dict[str, Dict[str, int]]] = {
            dimension: {} for dimension in EVIDENCE_DIMENSIONS
        }
        claims_processed = {dimension: 0 for dimension in EVIDENCE_DIMENSIONS}

        for claim in self.db.get_all_claims_with_targets():
            dimension = claim["evidence_dimension"]
            features = features_by_dimension[dimension]
            discriminators = discriminators_by_dimension[dimension]
            base_lbf = self._claim_base_lbf(claim)
            direct_discriminators = {
                did for did in claim["discriminators"] if did in discriminators
            }
            changed = False

            for fid in claim["features"]:
                if fid not in features:
                    continue
                self._apply_target_lbf(
                    features,
                    feature_counts[dimension],
                    fid,
                    base_lbf,
                    claim["paradigm"],
                )
                changed = True

            for did in direct_discriminators:
                self._apply_target_lbf(
                    discriminators,
                    discriminator_counts[dimension],
                    did,
                    base_lbf,
                    claim["paradigm"],
                )
                changed = True

            derived_targets = self._derived_targets_for_claim(
                claim["features"],
                direct_discriminators,
                base_lbf,
            )
            for did, derived_lbf in derived_targets.items():
                if did not in discriminators:
                    continue
                self._apply_target_lbf(
                    discriminators,
                    discriminator_counts[dimension],
                    did,
                    derived_lbf,
                    claim["paradigm"],
                    cap=DERIVED_DISCRIMINATOR_LBF_CAP,
                )
                changed = True

            if changed:
                claims_processed[dimension] += 1

        branch_by_dimension = {
            dimension: self._derive_branch_support(
                {
                    fid: feature.probability
                    for fid, feature in features_by_dimension[dimension].items()
                },
                discriminators_by_dimension[dimension],
            )
            for dimension in EVIDENCE_DIMENSIONS
        }
        features = self._dimension_probability_map(features_by_dimension)
        discriminators = self._dimension_probability_map(discriminators_by_dimension)
        branches = self._invert_dimension_map(branch_by_dimension)

        return {
            "features": features,
            "discriminators": discriminators,
            "branches": branches,
            "convergence": {
                "features": {
                    target_id: compute_convergence(dimension_probs)
                    for target_id, dimension_probs in features.items()
                },
                "discriminators": {
                    target_id: compute_convergence(dimension_probs)
                    for target_id, dimension_probs in discriminators.items()
                },
                "branches": {
                    branch_id: compute_convergence(dimension_probs)
                    for branch_id, dimension_probs in branches.items()
                },
            },
            "claims_processed": claims_processed,
        }

    def _initial_features_by_dimension(self) -> Dict[str, Dict[str, FeatureState]]:
        seed_features = self.db.get_all_features()
        return {
            dimension: {
                feature.id: FeatureState(
                    id=feature.id,
                    prior_log_odds=feature.prior_log_odds,
                    log_odds_val=feature.prior_log_odds,
                )
                for feature in seed_features
            }
            for dimension in EVIDENCE_DIMENSIONS
        }

    def _initial_discriminators_by_dimension(self) -> Dict[str, Dict[str, FeatureState]]:
        seed_discriminators = self.db.get_all_discriminators()
        return {
            dimension: {
                discriminator.id: FeatureState(
                    id=discriminator.id,
                    prior_log_odds=discriminator.prior_log_odds,
                    log_odds_val=discriminator.prior_log_odds,
                )
                for discriminator in seed_discriminators
            }
            for dimension in EVIDENCE_DIMENSIONS
        }

    def _dimension_probability_map(
        self,
        states_by_dimension: Dict[str, Dict[str, FeatureState]],
    ) -> Dict[str, Dict[str, float]]:
        return self._invert_dimension_map(
            {
                dimension: {
                    target_id: state.probability
                    for target_id, state in states.items()
                }
                for dimension, states in states_by_dimension.items()
            }
        )

    def _invert_dimension_map(
        self,
        values_by_dimension: Dict[str, Dict[str, float]],
    ) -> Dict[str, Dict[str, float]]:
        inverted: Dict[str, Dict[str, float]] = {}
        for dimension, values in values_by_dimension.items():
            for target_id, value in values.items():
                inverted.setdefault(target_id, {})[dimension] = value
        return inverted

    def _claim_base_lbf(self, claim: dict) -> float:
        return (
            claim["log_bayes_factor"]
            * claim["w_rel"]
            * claim["w_map"]
            * claim["w_aux"]
        )

    def _recompute_discriminators(self) -> tuple[Dict[str, FeatureState], int]:
        discriminators = {d.id: d for d in self.db.get_all_discriminators()}
        for discriminator in discriminators.values():
            discriminator.reset_to_prior()

        paradigm_counts: Dict[str, Dict[str, int]] = {}
        claims_processed = 0
        for claim in self.db.get_all_claims_with_targets():
            direct_targets = [
                did for did in claim["discriminators"] if did in discriminators
            ]
            effective_claim_lbf = self._claim_base_lbf(claim)
            derived_targets = self._derived_targets_for_claim(
                claim["features"],
                set(direct_targets),
                effective_claim_lbf,
            )

            for did in direct_targets:
                self._apply_discriminator_lbf(
                    discriminators,
                    paradigm_counts,
                    did,
                    effective_claim_lbf,
                    claim["paradigm"],
                )

            for did, derived_lbf in derived_targets.items():
                self._apply_discriminator_lbf(
                    discriminators,
                    paradigm_counts,
                    did,
                    derived_lbf,
                    claim["paradigm"],
                    cap=DERIVED_DISCRIMINATOR_LBF_CAP,
                )

            if direct_targets or derived_targets:
                claims_processed += 1

        return discriminators, claims_processed

    def _derived_targets_for_claim(
        self,
        feature_ids: List[str],
        direct_targets: set[str],
        effective_claim_lbf: float,
    ) -> Dict[str, float]:
        derived: Dict[str, float] = {}
        for fid in feature_ids:
            for did, mapping_weight in FEATURE_TO_DISCRIMINATOR_WEIGHTS.get(fid, {}).items():
                if did in direct_targets or mapping_weight == 0:
                    continue
                contribution = clamp(
                    effective_claim_lbf * mapping_weight,
                    -DERIVED_DISCRIMINATOR_LBF_CAP,
                    DERIVED_DISCRIMINATOR_LBF_CAP,
                )
                derived[did] = derived.get(did, 0.0) + contribution
        return derived

    def _apply_discriminator_lbf(
        self,
        discriminators: Dict[str, FeatureState],
        paradigm_counts: Dict[str, Dict[str, int]],
        discriminator_id: str,
        effective_lbf: float,
        paradigm: Optional[str],
        cap: Optional[float] = None,
    ) -> None:
        if discriminator_id not in discriminators:
            return

        n_prior = paradigm_counts.get(discriminator_id, {}).get(paradigm, 0) if paradigm else 0
        w_dep = propagation.compute_dep_weight(n_prior, self.dep_alpha)
        weighted_lbf = effective_lbf * w_dep
        if cap is not None:
            weighted_lbf = clamp(weighted_lbf, -cap, cap)
        discriminators[discriminator_id].update(weighted_lbf)

        if paradigm:
            bucket = paradigm_counts.setdefault(discriminator_id, {})
            bucket[paradigm] = bucket.get(paradigm, 0) + 1

    def _apply_target_lbf(
        self,
        states: Dict[str, FeatureState],
        paradigm_counts: Dict[str, Dict[str, int]],
        target_id: str,
        effective_lbf: float,
        paradigm: Optional[str],
        cap: Optional[float] = None,
    ) -> float:
        if target_id not in states:
            return 0.0
        w_dep = self._target_dep_weight(paradigm_counts, target_id, paradigm)
        weighted_lbf = effective_lbf * w_dep
        if cap is not None:
            weighted_lbf = clamp(weighted_lbf, -cap, cap)
        states[target_id].update(weighted_lbf)
        self._increment_target_count(paradigm_counts, target_id, paradigm)
        return w_dep

    def _target_dep_weight(
        self,
        counts: Dict[str, Dict[str, int]],
        target_id: str,
        paradigm: Optional[str],
    ) -> float:
        if not paradigm:
            return 1.0
        return propagation.compute_dep_weight(
            counts.get(target_id, {}).get(paradigm, 0),
            self.dep_alpha,
        )

    def _increment_target_count(
        self,
        counts: Dict[str, Dict[str, int]],
        target_id: str,
        paradigm: Optional[str],
    ) -> None:
        if not paradigm:
            return
        bucket = counts.setdefault(target_id, {})
        bucket[paradigm] = bucket.get(paradigm, 0) + 1

    def _trace_record(
        self,
        claim: dict,
        target_id: str,
        target_type: str,
        evidence_role: str,
        base_lbf: float,
        w_dep: float,
        effective_lbf: float,
        posterior_before: float,
        posterior_after: float,
        branch_support_before: Dict[str, float],
        branch_support_after: Dict[str, float],
    ) -> dict:
        branch_support_delta = {
            bid: branch_support_after[bid] - branch_support_before[bid]
            for bid in branch_support_before
        }
        return {
            "claim_id": claim["claim_id"],
            "source_type": claim["source_type"],
            "source_id": claim["source_id"],
            "claim_text": claim["claim_text"],
            "evidence_dimension": claim["evidence_dimension"],
            "target_id": target_id,
            "target_type": target_type,
            "evidence_role": evidence_role,
            "log_bayes_factor": claim["log_bayes_factor"],
            "w_rel": claim["w_rel"],
            "w_map": claim["w_map"],
            "w_aux": claim["w_aux"],
            "w_dep": w_dep,
            "base_lbf": base_lbf,
            "effective_lbf": effective_lbf,
            "posterior_before": posterior_before,
            "posterior_after": posterior_after,
            "posterior_delta": posterior_after - posterior_before,
            "branch_support_before": branch_support_before,
            "branch_support_after": branch_support_after,
            "branch_support_delta": branch_support_delta,
        }

    def _branch_support_snapshot(
        self,
        features: Dict[str, FeatureState],
        discriminators: Dict[str, FeatureState],
    ) -> Dict[str, float]:
        return self._derive_branch_support(
            {fid: feature.probability for fid, feature in features.items()},
            discriminators,
        )

    def _derive_branch_support(
        self,
        feature_probs: Dict[str, float],
        discriminators: Dict[str, FeatureState],
    ) -> Dict[str, float]:
        profiles = self.db.get_branch_feature_profiles()
        effects = self.db.get_discriminator_branch_effects()
        raw: Dict[str, float] = {}

        for bid, profile in profiles.items():
            support = feature_projection_from_probs(profile, feature_probs)
            for did, discriminator in discriminators.items():
                answer_effects = effects.get(did, {})
                yes_effect = answer_effects.get("yes", {}).get(bid, 1.0)
                no_effect = answer_effects.get("no", {}).get(bid, 1.0)
                support *= expected_branch_effect(
                    discriminator.probability,
                    yes_effect,
                    no_effect,
                )
            raw[bid] = support

        return normalize_scores(raw)


def build_truth_map_db(
    path: str = ":memory:",
    seed_claims: bool = True,
    argument_schema: bool = False,
) -> TruthMapSQLiteDB:
    conn = sqlite3.connect(path)
    db = TruthMapSQLiteDB(conn)
    db.create_schema()
    if argument_schema:
        db.create_argument_schema()
    db.seed_features_and_branches()
    db.seed_discriminators()
    db.seed_questions_from_files()
    if seed_claims:
        db.seed_claims()
    return db


def run_seeded_truth_map(path: str = ":memory:") -> dict:
    db = build_truth_map_db(path)
    engine = PropagationEngine(db)
    return engine.run()


if __name__ == "__main__":
    result = run_seeded_truth_map()
    print(json.dumps(result, indent=2, sort_keys=True))
