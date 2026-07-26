# Versioning Infrastructure — Automated RO Lifecycle

## The Problem

Right now, versioning is manual. An agent edits a file and decides to bump the version. There's no automated tracking of:
- When a source changes, which ROs are affected
- When an RO changes, which EOs/dossiers reference it
- Whether a version bump is minor or major
- Whether downstream objects need review

We need software, not agent discipline.

---

## The Data Flow

```
SOURCE CHANGES
  Paper updated on arxiv (v2 published)
  New translation of existing text
  Retraction notice
       │
       ▼
  SO updated (version bump)
       │
       ▼
  RO index checked: which ROs reference this SO?
       │
       ├── None found → flag for possible RO creation (don't auto-create)
       │
       └── Found → compare SO versions
             │
             ├── Minor change (metadata fix, typo)
             │     → Auto-update RO: bump patch version
             │     → D1 index updated
             │     → No notification needed
             │
             ├── Medium change (new passages available, better translation)
             │     → Add new passages to RO: bump minor version
             │     → D1 index updated
             │     → Linked EOs/dossiers flagged: "new RO passages available"
             │
             └── Major change (retraction, incompatible edition)
                   → RO flagged for review: bump major version
                   → D1 index updated
                   → Linked EOs/dossiers flagged: "RO requires review"
                   → Human/agent must review before RO is usable

RO CHANGES (from agent editing)
  Agent edits RO file (additions, corrections, reorganizations)
       │
       ▼
  Git pre-commit hook:
    → Parse RO file
    → Compare to previous version (git diff)
    → Classify change type:
      - New passages added → minor bump
      - Existing passages edited → patch bump
      - Sources added/removed → minor bump
      - bears_on_questions changed → minor bump
      - Bulk rewrite → major bump
    → Auto-bump current_version if not manually bumped
    → Update D1 index
    → Check linked EOs/dossiers
    → Set needs_review flag if major bump
    → Commit with structured message:
      "ro:matter-of-wonder v1.2.0 → v1.3.0: added 3 passages from chapter 4"
```

---

## Software Components

### 1. RO Index (D1 Table)

For fast queries without scanning JSON files:

```sql
CREATE TABLE ro_index (
  ro_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  scope TEXT NOT NULL,
  traditions TEXT NOT NULL,        -- JSON array
  bears_on_questions TEXT,         -- JSON array of {question_id, relevance}
  source_ids TEXT NOT NULL,        -- JSON array of SO IDs referenced
  passage_count INTEGER DEFAULT 0,
  gate_pass_rate REAL,             -- fraction of passages that pass Nyāya gate (0-1)
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  auto_version_enabled INTEGER DEFAULT 1  -- 1 = auto-bump, 0 = manual only
);
```

### 2. RO Dependency Tracker (D1 Table)

Tracks which objects reference which ROs:

```sql
CREATE TABLE ro_dependents (
  ro_id TEXT NOT NULL,             -- the RO being referenced
  dependent_type TEXT NOT NULL,    -- 'eo' | 'dossier' | 'argument_fabric'
  dependent_id TEXT NOT NULL,      -- eo:xxx or q:xxx or candid:xxx
  passages_cited TEXT,             -- JSON array of passage_ids cited
  last_ro_version TEXT NOT NULL,   -- version of RO when last reviewed
  needs_review INTEGER DEFAULT 0,  -- 1 = RO changed, dependent needs check
  notified_at TEXT,
  PRIMARY KEY (ro_id, dependent_type, dependent_id)
);
```

When an RO version bumps, this table is queried. All dependents get `needs_review = 1`.

### 3. Change Classification Script (`scripts/version-ro.py`)

```python
# Called by git pre-commit hook or manually
# Detects what changed in an RO and auto-bumps version

def classify_change(old_ro: dict, new_ro: dict) -> str:
    """Returns: 'patch', 'minor', 'major'"""
    old_passages = {p['passage_id']: p for p in old_ro.get('body', [])}
    new_passages = {p['passage_id']: p for p in new_ro.get('body', [])}

    old_sources = {s['source_id'] for s in old_ro.get('sources', [])}
    new_sources = {s['source_id'] for s in new_ro.get('sources', [])}

    changes = []

    # Check for new passages
    for pid in new_passages:
        if pid not in old_passages:
            changes.append('passage_added')

    # Check for edited passages
    for pid in old_passages:
        if pid in new_passages and old_passages[pid] != new_passages[pid]:
            changes.append('passage_edited')

    # Check for source changes
    if old_sources != new_sources:
        changes.append('sources_changed')

    # Check for question changes
    if old_ro.get('bears_on_questions') != new_ro.get('bears_on_questions'):
        changes.append('questions_changed')

    # Classify
    if 'sources_changed' in changes or 'questions_changed' in changes:
        return 'minor'
    if 'passage_added' in changes:
        return 'minor'
    if 'passage_edited' in changes and len(changes) > 5:
        return 'major'
    if 'passage_edited' in changes:
        return 'patch'
    return 'patch'  # default


def auto_bump(old_version: str, change_type: str) -> str:
    major, minor, patch = map(int, old_version.split('.'))
    if change_type == 'major':
        return f"{major + 1}.0.0"
    if change_type == 'minor':
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"
```

### 4. Git Pre-Commit Hook (`.git/hooks/pre-commit`)

```bash
#!/bin/bash
# Auto-bump RO versions on commit
for file in $(git diff --cached --name-only -- 'content/research-objects/**/ro.json'); do
    python3 scripts/version-ro.py --file "$file" --mode auto-bump
done
```

### 5. Source Change Handler (`scripts/on-source-update.py`)

Called when an SO is updated (by the acquire skill or manually):

```python
def handle_source_update(so_id: str, change_type: str):
    """Called when an SO changes. Finds affected ROs and handles them."""
    affected_ros = db.query(
        "SELECT ro_id FROM ro_index WHERE source_ids LIKE ?",
        (f'%{so_id}%',)
    )
    for ro_id in affected_ros:
        if change_type == 'minor':
            # Auto-update: add new metadata if available, bump patch
            update_ro_metadata(ro_id, so_id)
            auto_bump_version(ro_id, 'patch')
        elif change_type == 'medium':
            # Add new passages if the extraction pipeline has them
            new_passages = extract_new_passages(so_id, ro_id)
            if new_passages:
                add_passages_to_ro(ro_id, new_passages)
                auto_bump_version(ro_id, 'minor')
                flag_dependents_for_review(ro_id)
        elif change_type == 'major':
            # Can't auto-handle retractions or incompatible editions
            flag_ro_for_review(ro_id)
            auto_bump_version(ro_id, 'major')
            flag_dependents_for_review(ro_id)
```

---

## Full Pipeline: Paper Arrives to Review Flagged

```
1. Paper arrives via acquire skill (arxiv:2409.20318)
   → SO created: so:ramstead-inner-screen-2023
   → ro_index queried: any existing RO referencing this SO?
     → No: flag for agent review — "new paper available on consciousness"
     → Agent decides: should an RO be created? What theme?

2. Agent creates RO "Inner Screen Model of Consciousness"
   → Extracts 8 passages about the free-energy principle and manifestness
   → Each passage assigned: topic, section, source_id
   → RO saved: content/research-objects/ro-inner-screen/ro.json
   → Git commit triggers pre-commit hook
   → hooks/version-ro.py detects:
     - No previous version → set v1.0.0
     - Update ro_index D1 table
   → No dependents to flag (first version)

3. Six months later: arxiv publishes v2 of the same paper
   → acquire skill detects: SO already exists with older version
   → handle_source_update('so:ramstead-inner-screen-2023', 'minor')
   → ro_index queried: ro:inner-screen references this SO
   → No new passages needed (minor update: metadata only)
   → Auto-bump RO: v1.0.0 → v1.0.1
   → ro_index updated
   → No dependent flagging (patch bump)

4. Later: new translation of Ennead IV becomes available
   → SO so:plotinus-enneads updated: new source text added
   → handle_source_update('so:plotinus-enneads', 'medium')
   → ro:the-soul-in-the-enneads references this SO
   → New passages extracted and added to RO body
   → Auto-bump: v2.1.0 → v2.2.0
   → ro_dependents queried:
     - eo:consciousness-depends-on-brain has needs_review = 0
     - Flag set to 1: "RO has new passages about soul-body relation"
   → Agent sees: "eo:consciousness-depends-on-brain needs review — new Plotinus passages available"
```

---

## What This Replaces

Without this infra, versioning relies on:
- An agent remembering to bump versions
- An agent knowing which ROs reference a changed SO
- An agent checking which EOs need review after an RO changes

With this infra, the software handles all of that automatically. The agent only makes **content decisions** (what passages to extract, what theme to organize around).

---

## Implementation Order

1. **Create `scripts/version-ro.py`** — change classification + auto-bump logic (60 lines)
2. **Create `scripts/on-source-update.py`** — source change handler (80 lines)
3. **Add `ro_index` table** to truth map schema (one-time migration)
4. **Add `ro_dependents` table** to truth map schema (one-time migration)
5. **Write git pre-commit hook** for auto-bumping
6. **Wire `on-source-update.py`** into the acquire skill's post-ingestion step
