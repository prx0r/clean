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
PropagationEngine = propagation.PropagationEngine
log_odds = propagation.log_odds


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

            CREATE INDEX IF NOT EXISTS idx_claims_question ON claims(target_question_id);
            CREATE INDEX IF NOT EXISTS idx_claims_paradigm ON claims(paradigm);
            CREATE INDEX IF NOT EXISTS idx_claims_supersedes ON claims(supersedes);
            CREATE INDEX IF NOT EXISTS idx_claim_features_feature ON claim_features(feature_id);
            """
        )
        self.conn.commit()

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

    def seed_questions_from_files(
        self, source_dir: Path = ROOT / "content" / "source-metaphysics"
    ) -> None:
        for path in sorted(source_dir.glob("q-*.json")):
            data = json.loads(path.read_text())
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

    def add_claim_dict(self, claim: dict) -> None:
        falsifier = claim.get("falsifier") or {
            "type": "textual",
            "condition": "A stronger source or result defeats this claim.",
            "status": "untested",
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO claims
            (claim_id, source_type, source_id, evidence_role, source_cluster,
             method_family, target_question_id, log_bayes_factor, w_rel, w_map,
             w_aux, paradigm, claim_text, falsifier, is_retracted, supersedes,
             superseded_by, extracted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim["claim_id"],
                claim.get("source_type", "ro"),
                claim.get("source_id", "ro:unknown"),
                claim.get("evidence_role", "primary"),
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
        for fid in claim["features"]:
            self.conn.execute(
                "INSERT INTO claim_features (claim_id, feature_id) VALUES (?, ?)",
                (claim["claim_id"], fid),
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


def build_truth_map_db(path: str = ":memory:", seed_claims: bool = True) -> TruthMapSQLiteDB:
    conn = sqlite3.connect(path)
    db = TruthMapSQLiteDB(conn)
    db.create_schema()
    db.seed_features_and_branches()
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
