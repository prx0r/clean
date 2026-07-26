#!/usr/bin/env python3
"""
extract-claims.py — Paper → Information Packet

Takes an arxiv ID or PDF path, extracts structured claims via LLM,
outputs a versioned information packet JSON for truth map ingestion.

Usage:
    python scripts/extract-claims.py --arxiv 1312.2007
    python scripts/extract-claims.py --arxiv 1312.2007 --output my-packet.json
    python scripts/extract-claims.py --pdf /path/to/paper.pdf

Requires:
    pip install requests arxiv
    OPENCODE_API_KEY in environment (or --api-key)

Output: information packet JSON with claims mapped to D1-D5 discriminators and F1-F8 features.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request


ROOT = Path(__file__).resolve().parent.parent
PACKETS_DIR = ROOT / "content" / "information-packets"
PACKETS_DIR.mkdir(parents=True, exist_ok=True)

ARXIV_BASE = "https://arxiv.org"


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def fetch_arxiv_meta(arxiv_id: str) -> dict:
    """Fetch paper metadata via arxiv API."""
    import xml.etree.ElementTree as ET
    url = f"{ARXIV_BASE}/api/query?id_list={arxiv_id}"
    with urlopen(url, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        raise ValueError(f"arxiv ID {arxiv_id} not found")
    title = entry.find("a:title", ns).text.strip().replace("\n", " ").replace("  ", " ")
    authors = [a.find("a:name", ns).text for a in entry.findall("a:author", ns)]
    summary = entry.find("a:summary", ns).text.strip().replace("\n", " ")
    year = entry.find("a:published", ns).text[:4]
    return {"title": title, "authors": authors, "summary": summary, "year": year, "arxiv_id": arxiv_id}


def fetch_arxiv_abstract(arxiv_id: str) -> str:
    """Fetch just the abstract text."""
    url = f"{ARXIV_BASE}/abs/{arxiv_id}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    match = re.search(r'<blockquote class="abstract[^"]*">\s*(.*?)\s*</blockquote>', html, re.DOTALL)
    if match:
        text = match.group(1)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ""


def extract_claims_via_llm(
    title: str,
    authors: list,
    abstract: str,
    api_key: str,
    model: str = "deepseek-v4-flash",
) -> tuple:
    """Send paper to LLM, get back structured claims.

    Returns (claims_list, packet_id, raw_response).
    """
    prompt = f"""You are a claim extraction system for a truth map. Your job is to read a scientific paper and extract structured claims that bear on specific philosophical/scientific questions tracked by the truth map.

## Truth Map Discriminators (D1-D5)

These are binary questions whose answers eliminate or support entire metaphysical branches:

D1 — Physical Supervenience: Does every fact about information content, semantic reference, and observer identity supervene on the complete physical causal state and its lawful evolution?
D2 — Irreducible Macro Causation: Are there macro-scale or process-level causal powers that are not merely compressed descriptions of microphysical transition dynamics?
D3 — Intrinsic Phenomenality: Must the enabling condition for observer/object polarity include intrinsic phenomenal or reflexive manifestness, rather than only third-person structure?
D4 — Pattern Space Reality: Do mathematical or computational patterns have truth-making status independent of any particular physical instantiation or observer convention?
D5 — Substrate-Discontinuous Identity: Can the identity-relevant organization of an observer persist across destruction, replacement, or discontinuity of the original biological substrate?

## Truth Map Features (F1-F8)

These are lower-level evidence dimensions:

F1 — consciousness_fundamental
F2 — pattern_space_real
F3 — pattern_space_nonphysical
F4 — relations_ontologically_basic
F5 — information_persists_across_instantiation
F6 — teleology_real
F7 — cross_life_continuity
F8 — physical_law_emergent

## Instructions

Read the paper title, authors, and abstract below. Extract claims that bear on the truth map.

For each claim, output a JSON object with:
- claim_id: "cl:{paper-slug}-{number}"
- claim_text: The specific claim from the paper that bears on the truth map
- targets: list of {{"target_id": "D1-D5 or F1-F8", "target_type": "discriminator" or "feature"}}
- log_bayes_factor: -10 to +10. How much this claim moves the posterior. +1 = moderately supports, +3 = strongly supports, -1 = moderately undermines.
- w_rel: 0-1. How directly the evidence bears on the target.
- w_map: 0-1. How precisely the evidence maps to the claim.
- w_aux: 0-1. Source reliability (arXiv preprint = 0.5, peer-reviewed = 0.7, landmark = 0.85).
- paradigm: Which paradigm produced this claim (e.g. "high_energy_physics", "neuroscience", "phenomenology", "trika")
- falsifier: {{"type": "empirical|formal|textual", "condition": "what would disprove this", "status": "untested"}}
- evidence_role: "primary" or "interpretation"
- reasoning: 2-4 sentences explaining WHY this claim bears on the targets and why you assigned these weights.

IMPORTANT RULES:
- Only extract claims that DIRECTLY bear on a discriminator or feature. If the paper is completely unrelated to the truth map, output an empty claims list.
- Do not overclaim. A paper about quantum gravity does not automatically prove or disprove consciousness-first metaphysics.
- Be conservative with log_bayes_factor. Most papers provide modest evidence (±0.2 to ±0.8), not decisive proof.
- Every claim must have a falsifier — what would disprove it.
- The reasoning field is critical. It's how reviewers validate your weight estimates.

Output ONLY a JSON array of claim objects. No markdown, no preamble.

Paper title: {title}
Paper authors: {', '.join(authors)}
Abstract: {abstract}
"""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }).encode("utf-8")

    req = Request(
        "https://opencode.ai/zen/go/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())

    raw = result["choices"][0]["message"]["content"].strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()

    try:
        claims = json.loads(raw)
        if not isinstance(claims, list):
            claims = [claims]
    except json.JSONDecodeError:
        print(f"WARNING: LLM returned non-JSON. Raw:\n{raw[:500]}")
        claims = []

    packet_slug = slugify(f"{authors[0].split()[-1].lower() if authors else 'unknown'}-{title[:60]}")
    return claims, packet_slug, raw


def build_packet(
    claims: list,
    title: str,
    authors: list,
    arxiv_id: str,
    year: str,
    packet_id: str,
) -> dict:
    return {
        "packet_id": f"ip:{packet_id}",
        "schema_version": 1,
        "source": {
            "title": title,
            "authors": authors,
            "arxiv_id": arxiv_id,
            "year": int(year),
            "type": "paper",
        },
        "extracted_by": "deepseek-v4-flash",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "status": "draft",
        "claims": claims,
        "review": {
            "reviewed_by": None,
            "reviewed_at": None,
            "corrections": [],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Extract claims from a paper into an information packet")
    parser.add_argument("--arxiv", type=str, help="arxiv ID (e.g. 1312.2007)")
    parser.add_argument("--pdf", type=str, help="Path to PDF file")
    parser.add_argument("--output", type=str, help="Output path for packet JSON (default: content/information-packets/)")
    parser.add_argument("--api-key", type=str, help="OpenCode API key (default: OPENCODE_API_KEY env var)")
    parser.add_argument("--model", type=str, default="deepseek-v4-flash", help="LLM model")
    args = parser.parse_args()

    if not args.arxiv and not args.pdf:
        parser.error("Provide --arxiv or --pdf")

    api_key = args.api_key or os.environ.get("OPENCODE_API_KEY")
    if not api_key:
        parser.error("Set OPENCODE_API_KEY or pass --api-key")

    if args.arxiv:
        meta = fetch_arxiv_meta(args.arxiv)
        abstract = fetch_arxiv_abstract(args.arxiv)
        if not abstract:
            abstract = meta["summary"]
    else:
        raise NotImplementedError("PDF extraction not yet implemented")

    print(f"Paper: {meta['title']}")
    print(f"Authors: {', '.join(meta['authors'])}")
    print(f"Abstract: {abstract[:200]}...")
    print("Extracting claims via LLM...")

    claims, packet_slug, raw = extract_claims_via_llm(
        title=meta["title"],
        authors=meta["authors"],
        abstract=abstract,
        api_key=api_key,
        model=args.model,
    )

    print(f"Extracted {len(claims)} claims")

    packet = build_packet(
        claims=claims,
        title=meta["title"],
        authors=meta["authors"],
        arxiv_id=args.arxiv,
        year=meta["year"],
        packet_id=packet_slug,
    )

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = PACKETS_DIR / f"{packet_slug}.json"

    out_path.write_text(json.dumps(packet, indent=2))
    print(f"Packet saved to {out_path}")


if __name__ == "__main__":
    main()
