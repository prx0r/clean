#!/usr/bin/env python3
"""
Cloudflare D1 REST adapter for the truth-map propagation protocol.

This is the offline/admin bridge: it lets the Python reference engine run
against a real D1 database through Cloudflare's REST query endpoint.
"""

import json
import os
from typing import Dict, Iterable, List, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from truthengine_working import ClaimRecord, FeatureState, status_from_confidence


class D1APIError(RuntimeError):
    pass


class CloudflareD1TruthMapDB:
    def __init__(
        self,
        account_id: str,
        database_id: str,
        api_token: str,
        api_base: str = "https://api.cloudflare.com/client/v4",
    ):
        self.account_id = account_id
        self.database_id = database_id
        self.api_token = api_token
        self.api_base = api_base.rstrip("/")

    @classmethod
    def from_env(cls):
        missing = [
            name
            for name in [
                "CLOUDFLARE_ACCOUNT_ID",
                "CLOUDFLARE_D1_DATABASE_ID",
                "CLOUDFLARE_API_TOKEN",
            ]
            if not os.environ.get(name)
        ]
        if missing:
            raise D1APIError(f"Missing required env vars: {', '.join(missing)}")
        return cls(
            account_id=os.environ["CLOUDFLARE_ACCOUNT_ID"],
            database_id=os.environ["CLOUDFLARE_D1_DATABASE_ID"],
            api_token=os.environ["CLOUDFLARE_API_TOKEN"],
        )

    def _request(self, body: dict) -> list:
        url = (
            f"{self.api_base}/accounts/{self.account_id}"
            f"/d1/database/{self.database_id}/query"
        )
        req = Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise D1APIError(f"D1 HTTP {exc.code}: {detail}") from exc

        if not payload.get("success"):
            raise D1APIError(f"D1 API error: {payload.get('errors')}")

        results = payload.get("result") or []
        for result in results:
            if not result.get("success", True):
                raise D1APIError(f"D1 query failed: {result}")
        return results

    def query(self, sql: str, params: Optional[list] = None) -> list:
        results = self._request({"sql": sql, "params": params or []})
        if not results:
            return []
        return results[0].get("results") or []

    def batch(self, statements: List[tuple]) -> None:
        if not statements:
            return
        self._request(
            {
                "batch": [
                    {"sql": sql, "params": params or []}
                    for sql, params in statements
                ]
            }
        )

    def get_all_features(self) -> List[FeatureState]:
        rows = self.query(
            """
            SELECT feature_id, prior_log_odds, current_log_odds
            FROM feature_states
            ORDER BY feature_id
            """
        )
        return [
            FeatureState(
                id=row["feature_id"],
                prior_log_odds=row["prior_log_odds"],
                log_odds_val=row["current_log_odds"],
            )
            for row in rows
        ]

    def get_all_claims(self) -> List[ClaimRecord]:
        rows = self.query(
            """
            SELECT c.*, cf.feature_id
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.is_retracted = 0
            ORDER BY c.created_at, c.claim_id, cf.feature_id
            """
        )
        return self._rows_to_claims(rows)

    def get_claims_by_ids(self, claim_ids: List[str]) -> List[ClaimRecord]:
        if not claim_ids:
            return []
        claims: List[ClaimRecord] = []
        for chunk in _chunks(claim_ids, 80):
            placeholders = ",".join("?" for _ in chunk)
            rows = self.query(
                f"""
                SELECT c.*, cf.feature_id
                FROM claims c
                JOIN claim_features cf ON cf.claim_id = c.claim_id
                WHERE c.claim_id IN ({placeholders})
                ORDER BY c.created_at, c.claim_id, cf.feature_id
                """,
                chunk,
            )
            claims.extend(self._rows_to_claims(rows))
        return claims

    def _rows_to_claims(self, rows: Iterable[dict]) -> List[ClaimRecord]:
        grouped: Dict[str, dict] = {}
        for row in rows:
            cid = row["claim_id"]
            grouped.setdefault(cid, {"row": row, "features": []})
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
                    paradigm=row.get("paradigm"),
                    is_retracted=bool(row.get("is_retracted")),
                    target_question_id=row.get("target_question_id"),
                    source_cluster=row.get("source_cluster"),
                    method_family=row.get("method_family"),
                )
            )
        return claims

    def count_claims_by_paradigm(self, feature_id: str, paradigm: str) -> int:
        rows = self.query(
            """
            SELECT COUNT(*) AS cnt
            FROM claims c
            JOIN claim_features cf ON cf.claim_id = c.claim_id
            WHERE c.is_retracted = 0
              AND cf.feature_id = ?
              AND c.paradigm = ?
            """,
            [feature_id, paradigm],
        )
        return int(rows[0]["cnt"]) if rows else 0

    def bulk_dependence_counts(
        self,
        feature_ids: List[str],
        paradigms: List[str],
        exclude_claim_ids: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, int]]:
        counts: Dict[str, Dict[str, int]] = {fid: {} for fid in feature_ids}
        if not feature_ids or not paradigms:
            return counts

        for feature_chunk in _chunks(feature_ids, 50):
            for paradigm_chunk in _chunks(paradigms, 50):
                feature_placeholders = ",".join("?" for _ in feature_chunk)
                paradigm_placeholders = ",".join("?" for _ in paradigm_chunk)
                params: List[str] = list(feature_chunk) + list(paradigm_chunk)
                exclusion = ""
                if exclude_claim_ids:
                    exclusion_placeholders = ",".join("?" for _ in exclude_claim_ids)
                    exclusion = f"AND c.claim_id NOT IN ({exclusion_placeholders})"
                    params.extend(exclude_claim_ids)

                rows = self.query(
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
                )
                for row in rows:
                    counts[row["feature_id"]][row["paradigm"]] = int(
                        row["claim_count"]
                    )
        return counts

    def save_features(self, features: Dict[str, FeatureState]) -> None:
        self.batch(
            [
                (
                    """
                    UPDATE feature_states
                    SET current_log_odds = ?, probability = ?,
                        last_updated = datetime('now')
                    WHERE feature_id = ?
                    """,
                    [feature.log_odds, feature.probability, fid],
                )
                for fid, feature in features.items()
            ]
        )

    def save_question_states(self, features: Dict[str, FeatureState]) -> None:
        rows = self.query("SELECT question_id, feature_ids FROM truth_map_questions")
        statements = []
        for row in rows:
            feature_ids = json.loads(row["feature_ids"])
            probabilities = [
                features[fid].probability for fid in feature_ids if fid in features
            ]
            if not probabilities:
                continue
            confidence = sum(probabilities) / len(probabilities)
            statements.append(
                (
                    """
                    UPDATE truth_map_questions
                    SET confidence = ?, status = ?, last_updated = date('now'),
                        last_updated_by = 'propagation'
                    WHERE question_id = ?
                    """,
                    [
                        confidence,
                        status_from_confidence(confidence),
                        row["question_id"],
                    ],
                )
            )
        self.batch(statements)

    def get_branch_feature_profiles(self) -> Dict[str, Dict[str, str]]:
        rows = self.query("SELECT branch_id, feature_id, level FROM branch_profiles")
        profiles: Dict[str, Dict[str, str]] = {}
        for row in rows:
            profiles.setdefault(row["branch_id"], {})[row["feature_id"]] = row["level"]
        return profiles

    def save_branch_probabilities(self, branch_probs: Dict[str, float]) -> None:
        self.batch(
            [
                (
                    """
                    UPDATE branch_probabilities
                    SET probability = ?, score_type = 'relative_support',
                        last_updated = datetime('now')
                    WHERE branch_id = ?
                    """,
                    [prob, bid],
                )
                for bid, prob in branch_probs.items()
            ]
        )


def _chunks(values: List[str], size: int):
    for idx in range(0, len(values), size):
        yield values[idx : idx + size]
