-- Truth Map Argument Fabric schema
-- Additive schema: this does not replace the existing truth-map tables.
-- Existing tables expected nearby: claims, claim_targets, feature_states,
-- discriminators, branch_probabilities.

CREATE TABLE IF NOT EXISTS source_spans (
  span_id TEXT PRIMARY KEY,
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  locator TEXT,                         -- page, paragraph, verse, timestamp, byte range
  quote TEXT NOT NULL,
  normalized_text TEXT,
  language TEXT,
  tradition_scope TEXT,
  provenance TEXT NOT NULL DEFAULT '{}', -- JSON: edition, DOI, URL, retrieval, translator
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_source_spans_source
  ON source_spans(source_type, source_id);

CREATE INDEX IF NOT EXISTS idx_source_spans_tradition
  ON source_spans(tradition_scope);

CREATE TABLE IF NOT EXISTS argument_nodes (
  node_id TEXT PRIMARY KEY,
  node_type TEXT NOT NULL CHECK(node_type IN (
    'source_span',
    'claim',
    'argument',
    'candidate_explanation',
    'crux',
    'criticism',
    'falsifier',
    'formal_node',
    'bridge',
    'boundary',
    'state_of_play'
  )),
  title TEXT,
  statement TEXT NOT NULL,
  question_id TEXT,
  claim_id TEXT,
  span_id TEXT,
  tradition_scope TEXT,
  evidence_dimension TEXT CHECK(evidence_dimension IN (
    'phenomenological',
    'empirical',
    'contemplative',
    'formal',
    'textual',
    'analogical'
  )),
  pramana TEXT CHECK(pramana IN (
    'pratyaksa',
    'anumana',
    'upamana',
    'sabda',
    'formal_proof',
    'mixed',
    'none'
  )),
  status TEXT NOT NULL DEFAULT 'draft',
  payload TEXT NOT NULL DEFAULT '{}',   -- JSON for candidate/crux/state fields
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
  FOREIGN KEY (span_id) REFERENCES source_spans(span_id)
);

CREATE INDEX IF NOT EXISTS idx_argument_nodes_type
  ON argument_nodes(node_type);

CREATE INDEX IF NOT EXISTS idx_argument_nodes_question
  ON argument_nodes(question_id);

CREATE INDEX IF NOT EXISTS idx_argument_nodes_claim
  ON argument_nodes(claim_id);

CREATE INDEX IF NOT EXISTS idx_argument_nodes_scope
  ON argument_nodes(tradition_scope, pramana);

CREATE TABLE IF NOT EXISTS argument_edges (
  edge_id TEXT PRIMARY KEY,
  source_node_id TEXT NOT NULL,
  target_node_id TEXT NOT NULL,
  edge_type TEXT NOT NULL CHECK(edge_type IN (
    'supports',
    'attacks',
    'rephrases',
    'instantiates',
    'presupposes',
    'contradicts',
    'subsumes',
    'bridges',
    'decomposes_to',
    'targets',
    'falsified_by',
    'outside_formal'
  )),
  strength REAL NOT NULL DEFAULT 1.0 CHECK(strength >= 0.0 AND strength <= 1.0),
  polarity INTEGER NOT NULL DEFAULT 1 CHECK(polarity IN (-1, 0, 1)),
  relation_rationale TEXT NOT NULL,
  verified_by TEXT,
  verification_status TEXT NOT NULL DEFAULT 'unreviewed' CHECK(verification_status IN (
    'unreviewed',
    'agent_suggested',
    'human_reviewed',
    'lean_verified',
    'rejected'
  )),
  payload TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (source_node_id) REFERENCES argument_nodes(node_id),
  FOREIGN KEY (target_node_id) REFERENCES argument_nodes(node_id),
  UNIQUE(source_node_id, target_node_id, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_argument_edges_source
  ON argument_edges(source_node_id, edge_type);

CREATE INDEX IF NOT EXISTS idx_argument_edges_target
  ON argument_edges(target_node_id, edge_type);

CREATE TABLE IF NOT EXISTS claim_gate_results (
  gate_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL,
  gate_version TEXT NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN (
    'accepted',
    'accepted_with_penalty',
    'needs_review',
    'hollow',
    'outside_formal',
    'refuted'
  )),
  can_update_posterior INTEGER NOT NULL DEFAULT 0,
  adjusted_lbf_cap REAL,
  evidence_dimension TEXT,
  pramana TEXT,
  tradition_scope TEXT,
  hetu TEXT,
  sadhya TEXT,
  vyapti_statement TEXT,
  vyapti_confidence REAL CHECK(vyapti_confidence IS NULL OR (vyapti_confidence >= 0.0 AND vyapti_confidence <= 1.0)),
  falsifier_status TEXT,
  failures TEXT NOT NULL DEFAULT '[]',  -- JSON array of hetvabhasa/nigrahasthana defects
  reviewer TEXT,
  reasoning TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX IF NOT EXISTS idx_claim_gate_results_claim
  ON claim_gate_results(claim_id);

CREATE INDEX IF NOT EXISTS idx_claim_gate_results_outcome
  ON claim_gate_results(outcome, can_update_posterior);

CREATE TABLE IF NOT EXISTS hetvabhasa_checks (
  check_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL,
  fallacy_type TEXT NOT NULL CHECK(fallacy_type IN (
    'savyabhicara',
    'viruddha',
    'asiddha',
    'satpratipaksa',
    'badhita'
  )),
  present INTEGER NOT NULL CHECK(present IN (0, 1)),
  severity TEXT NOT NULL CHECK(severity IN ('none', 'weak', 'moderate', 'strong', 'decisive')),
  rationale TEXT NOT NULL,
  evidence_node_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
  FOREIGN KEY (evidence_node_id) REFERENCES argument_nodes(node_id),
  UNIQUE(claim_id, fallacy_type)
);

CREATE TABLE IF NOT EXISTS tarka_falsifiers (
  falsifier_id TEXT PRIMARY KEY,
  claim_id TEXT,
  candidate_id TEXT,
  falsifier_type TEXT NOT NULL CHECK(falsifier_type IN (
    'prasanga',
    'arthapatti',
    'empirical',
    'formal',
    'philological',
    'phenomenological',
    'semantic',
    'operational'
  )),
  condition TEXT NOT NULL,
  test_route TEXT,
  status TEXT NOT NULL DEFAULT 'untested' CHECK(status IN (
    'untested',
    'tested_survived',
    'tested_failed',
    'not_currently_testable',
    'unfalsifiable'
  )),
  result TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
  FOREIGN KEY (candidate_id) REFERENCES argument_nodes(node_id)
);

CREATE INDEX IF NOT EXISTS idx_tarka_falsifiers_claim
  ON tarka_falsifiers(claim_id);

CREATE TABLE IF NOT EXISTS nigrahasthana_events (
  event_id TEXT PRIMARY KEY,
  target_node_id TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN (
    'pratijnahani',
    'pratijnantara',
    'arthapatti',
    'prakaranasama',
    'sadhyasama',
    'other'
  )),
  description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'alleged' CHECK(status IN (
    'alleged',
    'answered',
    'sustained',
    'rejected',
    'needs_review'
  )),
  raised_by TEXT,
  resolved_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (target_node_id) REFERENCES argument_nodes(node_id)
);

CREATE TABLE IF NOT EXISTS formal_status_links (
  link_id TEXT PRIMARY KEY,
  argument_node_id TEXT NOT NULL,
  sanskritree_db_path TEXT,
  sanskritree_node_id TEXT,
  lean_file TEXT,
  lean_type TEXT,
  lean_proof TEXT,
  formal_status TEXT NOT NULL CHECK(formal_status IN (
    'PROVED',
    'UNPROVED',
    'PARTIAL',
    'HOLLOW',
    'OUTSIDE_FORMAL',
    'REFUTED',
    'UNKNOWN'
  )),
  axiom_scope TEXT,
  proof_trace TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (argument_node_id) REFERENCES argument_nodes(node_id)
);

CREATE INDEX IF NOT EXISTS idx_formal_status_links_node
  ON formal_status_links(argument_node_id);

CREATE TABLE IF NOT EXISTS negative_bridge_controls (
  control_id TEXT PRIMARY KEY,
  source_ref TEXT NOT NULL,
  node_a TEXT NOT NULL,
  node_b TEXT NOT NULL,
  reason TEXT NOT NULL,
  failure_type TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS structural_correspondences (
  correspondence_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL,
  left_term TEXT NOT NULL,
  left_scope TEXT NOT NULL,
  right_term TEXT NOT NULL,
  right_scope TEXT NOT NULL,
  shared_structure TEXT NOT NULL,
  important_difference TEXT NOT NULL,
  confidence_language TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN (
    'BRIDGES',
    'SUBSUMES',
    'CONTRADICTS',
    'OVERLAPS',
    'DIFFERENT',
    'needs_review'
  )),
  source_ids TEXT NOT NULL DEFAULT '[]',
  bridge_probe_id TEXT,
  negative_control_status TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_structural_correspondences_question
  ON structural_correspondences(question_id, status);

CREATE TABLE IF NOT EXISTS directional_critique_pairs (
  pair_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL,
  critic_lens TEXT NOT NULL,
  target_lens TEXT NOT NULL,
  reveals_about_target TEXT NOT NULL,
  pressure_type TEXT NOT NULL,
  target_response_required TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open' CHECK(status IN (
    'open',
    'answered',
    'sustained',
    'rejected',
    'needs_review'
  )),
  supporting_claim_ids TEXT NOT NULL DEFAULT '[]',
  crux_ids TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_directional_critique_pairs_question
  ON directional_critique_pairs(question_id, status);

CREATE TABLE IF NOT EXISTS state_of_play_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL,
  current_best_answer TEXT NOT NULL,
  confidence_language TEXT NOT NULL,
  solved_at_levels TEXT NOT NULL DEFAULT '[]',
  live_candidates TEXT NOT NULL DEFAULT '[]',
  weakened_candidates TEXT NOT NULL DEFAULT '[]',
  defeated_candidates TEXT NOT NULL DEFAULT '[]',
  open_cruxes TEXT NOT NULL DEFAULT '[]',
  next_tests TEXT NOT NULL DEFAULT '[]',
  implications TEXT NOT NULL DEFAULT '[]',
  provenance TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_state_of_play_question
  ON state_of_play_snapshots(question_id, created_at);
