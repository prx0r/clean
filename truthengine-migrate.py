#!/usr/bin/env python3
"""
tcee/scripts/migrate_v2.py

Migrates existing TCEE SQLite DB to v2 schema.
Safe to run multiple times (uses IF NOT EXISTS / OR REPLACE).

Usage:
    python scripts/migrate_v2.py
"""

import sqlite3
import sys
import math
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tcee.db"


def migrate(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    
    print(f"Migrating {db_path}...")
    
    # 1. Create features table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS features (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            prior_log_odds REAL NOT NULL,
            log_odds REAL NOT NULL,
            probability REAL NOT NULL
        )
    """)
    print("  ✓ features table")
    
    # 2. Create claims table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            evidence_id TEXT REFERENCES evidence(id),
            claim_text TEXT,
            target_feature_ids TEXT NOT NULL,
            target_mechanism_ids TEXT,
            direction TEXT,
            log_bayes_factor REAL NOT NULL,
            lbf_confidence REAL DEFAULT 1.0,
            w_rel REAL NOT NULL DEFAULT 1.0,
            w_map REAL NOT NULL DEFAULT 1.0,
            w_aux REAL NOT NULL DEFAULT 1.0,
            verified_human BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ claims table")
    
    # 3. Add columns to evidence (safe — fails silently if exists)
    for col in [
        "ALTER TABLE evidence ADD COLUMN paradigm TEXT",
        "ALTER TABLE evidence ADD COLUMN lab_cluster TEXT",
        "ALTER TABLE evidence ADD COLUMN method_family TEXT",
        "ALTER TABLE evidence ADD COLUMN is_retracted BOOLEAN DEFAULT FALSE",
    ]:
        try:
            conn.execute(col)
        except sqlite3.OperationalError:
            pass  # Column already exists
    print("  ✓ evidence columns")
    
    # 4. Add feature_profile to branches
    try:
        conn.execute("ALTER TABLE branches ADD COLUMN feature_profile TEXT")
    except sqlite3.OperationalError:
        pass
    print("  ✓ branches.feature_profile")
    
    # 5. Seed features F1-F8
    def lo(p):
        return math.log(p / (1.0 - p))
    
    feature_seeds = [
        ('F1', 'consciousness_fundamental',
         'Consciousness is ontologically primary', lo(0.40), lo(0.40), 0.40),
        ('F2', 'pattern_space_real',
         'Abstract pattern-space has genuine ontological status', lo(0.55), lo(0.55), 0.55),
        ('F3', 'pattern_space_nonphysical',
         'Pattern-space exists outside physical substrate', lo(0.35), lo(0.35), 0.35),
        ('F4', 'relations_ontologically_basic',
         'Relations are more fundamental than substances', lo(0.50), lo(0.50), 0.50),
        ('F5', 'information_persists_across_instantiation',
         'Information patterns persist through substrate loss', lo(0.12), lo(0.12), 0.12),
        ('F6', 'teleology_real',
         'Purpose and directedness are genuine features of reality', lo(0.18), lo(0.18), 0.18),
        ('F7', 'cross_life_continuity',
         'Continuity persists across life instances', lo(0.08), lo(0.08), 0.08),
        ('F8', 'physical_law_emergent',
         'Physical laws emerge from deeper substrate', lo(0.35), lo(0.35), 0.35),
    ]
    
    conn.executemany("""
        INSERT OR REPLACE INTO features 
        (id, name, description, prior_log_odds, log_odds, probability)
        VALUES (?, ?, ?, ?, ?, ?)
    """, feature_seeds)
    print("  ✓ seeded F1-F8")
    
    # 6. Update branch feature profiles
    profiles = {
        'B1': '{"F2": "high", "F8": "high"}',
        'B2': '{"F1": "low", "F2": "low"}',
        'B3': '{"F2": "high", "F3": "high"}',
        'B4': '{"F1": "high", "F2": "high", "F3": "high", "F5": "high", "F6": "high", "F7": "high"}',
        'B5': '{"F4": "high"}',
        'B6': '{"F5": "high", "F7": "high"}',
    }
    
    for bid, profile in profiles.items():
        conn.execute(
            "UPDATE branches SET feature_profile = ? WHERE id = ?",
            (profile, bid)
        )
    print("  ✓ branch feature profiles")
    
    conn.commit()
    conn.close()
    print("\nMigration complete.")
    print("Next: run pytest tcee/tests/test_propagation_engine.py -v")
    print("Then: delete tcee/propagation/gbp.py")


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}")
        print("Run: python scripts/seed_sqlite.py first")
        sys.exit(1)
    
    migrate(DB_PATH)
