"""
=============================================================================
PART 1: tcee/core/database_propagation.py
Add these methods to your existing DatabaseManager class in database.py.
They implement the PropagationDB protocol against SQLite.
=============================================================================
"""

SQLITE_ADDITIONS = '''
# Add to tcee/core/database.py inside DatabaseManager class

def get_all_features(self) -> List["FeatureState"]:
    """Load all feature states from DB."""
    from tcee.propagation.propagation import FeatureState
    
    conn = self._get_connection()
    cursor = conn.execute(
        "SELECT id, prior_log_odds, log_odds FROM features"
    )
    rows = cursor.fetchall()
    return [
        FeatureState(
            id=row[0],
            prior_log_odds=row[1],
            log_odds_val=row[2],
        )
        for row in rows
    ]

def get_all_claims(self) -> List["ClaimRecord"]:
    """Load all non-retracted claims from DB."""
    from tcee.propagation.propagation import ClaimRecord
    import json
    
    conn = self._get_connection()
    cursor = conn.execute("""
        SELECT 
            c.id,
            c.target_feature_ids,
            c.log_bayes_factor,
            c.w_rel,
            c.w_map,
            c.w_aux,
            e.paradigm,
            e.is_retracted
        FROM claims c
        LEFT JOIN evidence e ON c.evidence_id = e.id
        WHERE e.is_retracted = 0 OR e.is_retracted IS NULL
    """)
    rows = cursor.fetchall()
    return [
        ClaimRecord(
            id=row[0],
            target_feature_ids=json.loads(row[1]),
            log_bayes_factor=row[2],
            w_rel=row[3],
            w_map=row[4],
            w_aux=row[5],
            paradigm=row[6],
            is_retracted=bool(row[7]) if row[7] is not None else False,
        )
        for row in rows
    ]

def get_claims_by_ids(self, claim_ids: List[str]) -> List["ClaimRecord"]:
    """Load specific claims by ID."""
    from tcee.propagation.propagation import ClaimRecord
    import json
    
    if not claim_ids:
        return []
    
    placeholders = ','.join('?' for _ in claim_ids)
    conn = self._get_connection()
    cursor = conn.execute(f"""
        SELECT 
            c.id,
            c.target_feature_ids,
            c.log_bayes_factor,
            c.w_rel,
            c.w_map,
            c.w_aux,
            e.paradigm,
            e.is_retracted
        FROM claims c
        LEFT JOIN evidence e ON c.evidence_id = e.id
        WHERE c.id IN ({placeholders})
    """, claim_ids)
    rows = cursor.fetchall()
    return [
        ClaimRecord(
            id=row[0],
            target_feature_ids=json.loads(row[1]),
            log_bayes_factor=row[2],
            w_rel=row[3],
            w_map=row[4],
            w_aux=row[5],
            paradigm=row[6],
            is_retracted=bool(row[7]) if row[7] is not None else False,
        )
        for row in rows
    ]

def count_claims_by_paradigm(self, feature_id: str, paradigm: str) -> int:
    """
    Count claims from a paradigm already applied to a feature.
    Used for dependence discounting.
    """
    conn = self._get_connection()
    cursor = conn.execute("""
        SELECT COUNT(*) 
        FROM claims c
        LEFT JOIN evidence e ON c.evidence_id = e.id
        WHERE e.paradigm = ?
          AND c.target_feature_ids LIKE ?
          AND (e.is_retracted = 0 OR e.is_retracted IS NULL)
    """, (paradigm, f'%"{feature_id}"%'))
    return cursor.fetchone()[0]

def get_branch_feature_profiles(self) -> Dict[str, Dict[str, str]]:
    """Load branch feature profiles from DB."""
    import json
    
    conn = self._get_connection()
    cursor = conn.execute(
        "SELECT id, feature_profile FROM branches"
    )
    rows = cursor.fetchall()
    return {
        row[0]: json.loads(row[1]) if row[1] else {}
        for row in rows
    }

def save_features(self, features: Dict[str, "FeatureState"]) -> None:
    """Persist feature log-odds and probabilities."""
    conn = self._get_connection()
    for fid, f in features.items():
        conn.execute("""
            UPDATE features 
            SET log_odds = ?, probability = ?
            WHERE id = ?
        """, (f.log_odds, f.probability, fid))
    conn.commit()

def save_branch_probabilities(self, branch_probs: Dict[str, float]) -> None:
    """Persist branch probabilities."""
    conn = self._get_connection()
    for bid, prob in branch_probs.items():
        conn.execute("""
            UPDATE branches 
            SET current_probability = ?
            WHERE id = ?
        """, (prob, bid))
    conn.commit()
'''
