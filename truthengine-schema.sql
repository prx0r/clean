"""
=============================================================================
PART 2: SQLite schema additions
Run this migration to add the new tables and columns.
Save as: tcee/scripts/migrate_v2.py
=============================================================================
"""

MIGRATION_SQL = """
-- Add features table
CREATE TABLE IF NOT EXISTS features (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prior_log_odds REAL NOT NULL,
    log_odds REAL NOT NULL,
    probability REAL NOT NULL
);

-- Add claims table  
CREATE TABLE IF NOT EXISTS claims (
    id TEXT PRIMARY KEY,
    evidence_id TEXT REFERENCES evidence(id),
    claim_text TEXT,
    target_feature_ids TEXT NOT NULL,  -- JSON array: ["F1", "F2"]
    target_mechanism_ids TEXT,         -- JSON array
    direction TEXT,                    -- 'supports' | 'challenges'
    log_bayes_factor REAL NOT NULL,
    lbf_confidence REAL DEFAULT 1.0,
    w_rel REAL NOT NULL DEFAULT 1.0,
    w_map REAL NOT NULL DEFAULT 1.0,
    w_aux REAL NOT NULL DEFAULT 1.0,
    verified_human BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Add paradigm and cluster tracking to evidence
ALTER TABLE evidence ADD COLUMN paradigm TEXT;
ALTER TABLE evidence ADD COLUMN lab_cluster TEXT;
ALTER TABLE evidence ADD COLUMN method_family TEXT;
ALTER TABLE evidence ADD COLUMN is_retracted BOOLEAN DEFAULT FALSE;

-- Add feature_profile to branches
ALTER TABLE branches ADD COLUMN feature_profile TEXT;  -- JSON

-- Add log_odds and probability columns to features if seeding separately
-- (If features table is new, these are already included above)
"""

SEED_FEATURES_SQL = """
-- Seed F1-F8 with priors from SPEC.md
-- Prior log-odds computed as log(p/(1-p))

INSERT OR REPLACE INTO features (id, name, description, prior_log_odds, log_odds, probability) VALUES
('F1', 'consciousness_fundamental',
 'Consciousness is ontologically primary, not reducible to physical processes',
 -0.405465,  -- log(0.4/0.6): slight prior against
 -0.405465, 0.4),

('F2', 'pattern_space_real',
 'Abstract pattern-space has genuine ontological status',
 0.200671,   -- log(0.55/0.45): slight prior for
 0.200671, 0.55),

('F3', 'pattern_space_nonphysical',
 'Pattern-space exists outside physical substrate',
 -0.619039,  -- log(0.35/0.65): prior against
 -0.619039, 0.35),

('F4', 'relations_ontologically_basic',
 'Relations and processes are more fundamental than substances',
 0.0,        -- log(0.5/0.5): agnostic
 0.0, 0.5),

('F5', 'information_persists_across_instantiation',
 'Information patterns persist through substrate loss (death etc)',
 -1.992176,  -- log(0.12/0.88): strong prior against
 -1.992176, 0.12),

('F6', 'teleology_real',
 'Purpose and directedness are genuine features of reality',
 -1.516127,  -- log(0.18/0.82): prior against
 -1.516127, 0.18),

('F7', 'cross_life_continuity',
 'Continuity of identity or pattern persists across life instances',
 -2.442347,  -- log(0.08/0.92): strong prior against
 -2.442347, 0.08),

('F8', 'physical_law_emergent',
 'Physical laws emerge from deeper substrate rather than being fundamental',
 -0.619039,  -- log(0.35/0.65): prior against
 -0.619039, 0.35);
"""

SEED_BRANCH_PROFILES_SQL = """
-- Update branches with feature profiles
-- Profiles define what each branch requires of the features

UPDATE branches SET feature_profile = '{"F2": "high", "F8": "high"}'
WHERE id = 'B1';  -- Thin Formalism

UPDATE branches SET feature_profile = '{"F1": "low", "F2": "low"}'
WHERE id = 'B2';  -- Physical Realism

UPDATE branches SET feature_profile = '{"F2": "high", "F3": "high"}'
WHERE id = 'B3';  -- Platonic/Computational Idealism

UPDATE branches SET feature_profile = 
    '{"F1": "high", "F2": "high", "F3": "high", "F5": "high", "F6": "high", "F7": "high"}'
WHERE id = 'B4';  -- Nondual Consciousness-First

UPDATE branches SET feature_profile = '{"F4": "high"}'
WHERE id = 'B5';  -- Process Metaphysics

UPDATE branches SET feature_profile = '{"F5": "high", "F7": "high"}'
WHERE id = 'B6';  -- Cross-Life Continuity / Rebirth
"""
