# Codex — Research Seed: Relevant Algorithms & Architectures

## 1. T-AIF: Trichotomic Argument Interchange Format
**arXiv:1812.06745** — Göttlinger & Schröder (2018)

Extends the Argument Interchange Format (AIF) with three dimensions: Logos (logical structure), Ethos (weighted trust edges between actors), Pathos (weighted commitment edges from actors to claims). 

**Relevance to our argument fabric:**
- Our `argument_nodes` and `argument_edges` schema is already AIF-like. T-AIF adds weighted trust between traditions/scholars and weighted commitment to claims.
- This gives us a formal model for: "Abhinavagupta is committed to vimarśa as intrinsic (Ethos). Dharmakīrti is committed to apoha as exclusion-based (Ethos). These commitments create the tension (Pathos)."
- Read the paper for how they handle weighted support/attack in a graph with actor-specific weights.

## 2. GraphRAG for Scientific Literature
**arXiv:2602.16650** — polymer science GraphRAG (2026)
**arXiv:2508.05660** — agentic hybrid RAG for science (2025)

Both build knowledge graphs from scientific papers and use hybrid retrieval (graph + vector) for multi-hop reasoning. The 2025 paper uses Neo4j + FAISS + an LLM agent that dynamically selects GraphRAG vs VectorRAG per query.

**Relevance:**
- Our evidence graph is a scientific knowledge graph. Their entity disambiguation and multi-hop reasoning patterns apply directly.
- The dynamic routing (graph search for structured queries, vector search for fuzzy matches) is what our state-of-play synthesis needs.
- Don't build Neo4j — SQLite is fine for our scale. But the architecture pattern is useful.

## 3. Stack Graphs — File-Incremental Graph Construction
**arXiv:2211.01224** — Creager & van Antwerpen (2022)

Each source file produces an isolated subgraph. Subgraphs are composed only when needed for path-finding queries. When a file changes, only its subgraph is rebuilt.

**Relevance:**
- This is exactly the model for RO versioning. Each RO is an isolated subgraph. When an SO changes, only the ROs that reference it get rebuilt. Dependents (EOs, dossiers) are flagged but not auto-recomputed.
- The "stack" mechanism for handling type-directed lookups maps to our bridge probing — when resolving whether two terms from different traditions are the same, you need to pause the current lookup and resolve a type equivalence first.

## 4. The Sanskritree Proof Engine (already in our repo)
**Location:** `/mnt/HC_Volume_106427611/sanskritree/proof_engine/`

We already have:
- `bnf.py` — NNExpr parser for Nyāya/Navya-Nyāya expressions (72 lines)
- `fol_lean_bridge.py` — maps NNExpr to Lean types (125 lines)
- `bridge_probe.py` — discovers SUBSUMES/BRIDGES/CONTRADICTS/OVERLAPS relations (131 lines)
- `algorithm.py` — 7-step proof algorithm with sayability gate (218 lines)
- `nyayaengine.py` — working demo with Nyāya NS 1.1.1 decomposition (574 lines)
- 11 JSON ground truth files (primitives, claims, negative controls)
- `lean/` directory with 5 Lean files (Entity, Relation, Decision, LayerB)

**Not yet imported into the clean project.** Should be in `scripts/logic/`.

## How These Fit Together

| Component | What it gives us | Where it goes |
|-----------|-----------------|---------------|
| T-AIF (Ethos + Pathos weights) | Formal model for tradition trust + claim commitment | argument_edges table extension |
| GraphRAG hybrid retrieval | Query pattern for state-of-play synthesis | scripts/state-of-play.py |
| Stack graphs | Versioning model for RO dependency tracking | VERSIONING-INFRA.md → implementation |
| Sanskritree proof engine | NNExpr parsing, Lean formalization, bridge probing | scripts/logic/ |

The core insight: **our architecture is novel.** No single paper does what we're building. But each paper gives us a piece of the formal model we can adapt.
