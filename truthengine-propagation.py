"""
Propagation Engine — Bayesian belief updating across features with
paradigm-aware dependence discounting.

This is the math engine behind the truth map. It implements:
  - Log-odds Bayesian updating (sigmoid, log_odds)
  - Dependence discounting for multiple claims from the same paradigm
  - Feature state management (prior, update, reset)
  - Weighted log Bayes factors: w_rel × w_map × w_dep × w_aux × log_bayes_factor
  - Branch probability derivation from feature posteriors
  - Full recompute vs incremental update modes
"""

import math
from typing import Dict, List, Optional, Protocol, Any


# ── Math primitives ─────────────────────────────────────────────────────────

def sigmoid(x: float) -> float:
    if x > 709:
        return 1.0 - 1e-15
    if x < -709:
        return 1e-15
    return 1.0 / (1.0 + math.exp(-x))


def log_odds(p: float) -> float:
    p = max(1e-15, min(1.0 - 1e-15, p))
    return math.log(p / (1.0 - p))


def compute_dep_weight(n_prior: int, alpha: float = 0.5) -> float:
    """
    Dependence discount for nth claim from same paradigm.

    n_prior = number of claims from this paradigm already applied
              to this feature (NOT counting current claim).

    Formula:
      n_same = n_prior + 1  (count including current claim)
      w_dep = 1 / (1 + alpha * max(0, n_same - 1))
            = 1 / (1 + alpha * n_prior)

    n_prior=0 → w_dep=1.0  (first claim, no discount)
    n_prior=1 → w_dep=0.666 (second claim)
    n_prior=2 → w_dep=0.5
    """
    return 1.0 / (1.0 + alpha * max(0, n_prior))


# ── Data classes ─────────────────────────────────────────────────────────────

class FeatureState:
    """
    Minimal feature representation used inside the engine.
    Tracks a single dimension of the truth map (e.g. a question's confidence).
    """
    def __init__(self, id: str, prior_log_odds: float, log_odds_val: float):
        self.id = id
        self.prior_log_odds = prior_log_odds
        self.log_odds = log_odds_val
        self.probability = sigmoid(log_odds_val)

    def update(self, weighted_lbf: float):
        self.log_odds += weighted_lbf
        self.probability = sigmoid(self.log_odds)

    def reset_to_prior(self):
        self.log_odds = self.prior_log_odds
        self.probability = sigmoid(self.prior_log_odds)


class ClaimRecord:
    """
    Minimal claim representation. One claim = one piece of evidence
    bearing on one or more features.

    w_rel  = relevance weight   (0-1, how directly the evidence bears)
    w_map  = mapping quality    (0-1, how precisely it maps)
    w_dep  = dependence discount (computed, 0-1, paradigm crowding)
    w_aux  = auxiliary weight   (0-1, source reliability + specificity)
    """
    def __init__(
        self,
        id: str,
        target_feature_ids: List[str],
        log_bayes_factor: float,
        w_rel: float,
        w_map: float,
        w_aux: float,
        paradigm: Optional[str],
        is_retracted: bool = False,
    ):
        self.id = id
        self.target_feature_ids = target_feature_ids
        self.log_bayes_factor = log_bayes_factor
        self.w_rel = w_rel
        self.w_map = w_map
        self.w_aux = w_aux
        self.paradigm = paradigm
        self.is_retracted = is_retracted
        self.w_dep: float = 1.0  # set during propagation

    @property
    def weighted_lbf(self) -> float:
        return (
            self.w_rel
            * self.w_map
            * self.w_dep
            * self.w_aux
            * self.log_bayes_factor
        )


# ── DB Protocol ──────────────────────────────────────────────────────────────

class PropagationDB(Protocol):
    """Interface the PropagationEngine requires from the database layer."""

    def get_all_features(self) -> List[FeatureState]: ...
    def get_all_claims(self) -> List[ClaimRecord]: ...
    def get_claims_by_ids(self, claim_ids: List[str]) -> List[ClaimRecord]: ...
    def count_claims_by_paradigm(self, feature_id: str, paradigm: str) -> int: ...
    def save_features(self, features: Dict[str, FeatureState]) -> None: ...
    def save_branch_probabilities(self, branch_probs: Dict[str, float]) -> None: ...
    def get_branch_feature_profiles(self) -> Dict[str, Dict[str, str]]: ...


# ── Branch derivation ────────────────────────────────────────────────────────

def derive_branch_prob_unnormalized(
    profile: Dict[str, str],
    features: Dict[str, FeatureState],
) -> float:
    """
    Unnormalized branch probability = product of feature probabilities
    per the profile.

    profile values:
      'high'     → multiply by P(F_k)
      'low'      → multiply by (1 - P(F_k))
      'agnostic' → skip (contributes 1.0)
    """
    prob = 1.0
    for fid, level in profile.items():
        if fid not in features:
            continue
        fp = features[fid].probability
        if level == 'high':
            prob *= fp
        elif level == 'low':
            prob *= (1.0 - fp)
    return prob


def derive_all_branch_probs(
    features: Dict[str, FeatureState],
    profiles: Dict[str, Dict[str, str]],
) -> Dict[str, float]:
    """
    Compute normalized branch probabilities from feature posteriors.
    Branches are NOT a clean partition, so normalization is approximate
    for reporting. The real inferential state lives in the feature log-odds.
    """
    raw = {
        bid: derive_branch_prob_unnormalized(profile, features)
        for bid, profile in profiles.items()
    }
    total = sum(raw.values())
    if total == 0:
        n = len(raw)
        return {bid: 1.0 / n for bid in raw}
    return {bid: v / total for bid, v in raw.items()}


# ── PropagationEngine ────────────────────────────────────────────────────────

class PropagationEngine:
    """
    Core propagation engine.

    Usage:
        engine = PropagationEngine(db)

        # Full recompute from priors
        result = engine.run()

        # Incremental update after single evidence ingestion
        result = engine.run(new_claim_ids=['CL-001', 'CL-002'])
    """

    def __init__(self, db: Any, dep_alpha: float = 0.5):
        self.db = db
        self.dep_alpha = dep_alpha
        self._paradigm_counts: Dict[str, Dict[str, int]] = {}

    def run(
        self,
        new_claim_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run propagation.

        If new_claim_ids is None: full recompute from priors.
        If new_claim_ids provided: incremental update only for those claims.
        """
        features = {f.id: f for f in self.db.get_all_features()}
        profiles = self.db.get_branch_feature_profiles()

        if new_claim_ids is None:
            for f in features.values():
                f.reset_to_prior()
            claims = self.db.get_all_claims()
            self._paradigm_counts = {}
        else:
            claims = self.db.get_claims_by_ids(new_claim_ids)
            self._paradigm_counts = self._load_paradigm_counts(
                features.keys(), claims
            )

        claims_processed = 0
        for claim in claims:
            if claim.is_retracted:
                continue

            for fid in claim.target_feature_ids:
                if fid not in features:
                    continue

                n_prior = self._get_paradigm_count(fid, claim.paradigm)
                claim.w_dep = compute_dep_weight(n_prior, self.dep_alpha)
                features[fid].update(claim.weighted_lbf)
                self._increment_paradigm_count(fid, claim.paradigm)

            claims_processed += 1

        branch_probs = derive_all_branch_probs(features, profiles)

        self.db.save_features(features)
        self.db.save_branch_probabilities(branch_probs)

        return {
            'features': {fid: f.probability for fid, f in features.items()},
            'branches': branch_probs,
            'claims_processed': claims_processed,
            'paradigm_counts': dict(self._paradigm_counts),
        }

    def _get_paradigm_count(self, feature_id: str, paradigm: Optional[str]) -> int:
        if paradigm is None:
            return 0
        return self._paradigm_counts.get(feature_id, {}).get(paradigm, 0)

    def _increment_paradigm_count(self, feature_id: str, paradigm: Optional[str]):
        if paradigm is None:
            return
        if feature_id not in self._paradigm_counts:
            self._paradigm_counts[feature_id] = {}
        counts = self._paradigm_counts[feature_id]
        counts[paradigm] = counts.get(paradigm, 0) + 1

    def _load_paradigm_counts(
        self,
        feature_ids,
        new_claims: List[ClaimRecord],
    ) -> Dict[str, Dict[str, int]]:
        counts: Dict[str, Dict[str, int]] = {}
        paradigms = set(c.paradigm for c in new_claims if c.paradigm)
        for fid in feature_ids:
            counts[fid] = {}
            for paradigm in paradigms:
                n = self.db.count_claims_by_paradigm(fid, paradigm)
                if n > 0:
                    counts[fid][paradigm] = n
        return counts
