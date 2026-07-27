#!/usr/bin/env python3
"""Fix Phase 1 counting bug and run remaining under-covered phases."""
import glob, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET, tarfile, subprocess

CONTENT_WORKS = "/root/projects/blog/content/works"
CONTENT_ESSAYS = "/root/projects/blog/content/glossary/essays"
LIBRARY_FRONTIER = "/root/projects/blog/library/frontier"
ACQUISITION_LOG = "/root/projects/blog/hermes/notes/t2-acquisition-log.md"

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OA_SVC = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
EMAIL = "hermes@research.local"
DELAY = 1.0

# Count existing papers for a specific phase (FIXED - only check phase_mapping.phase)
def count_phase(phase_num):
    seen = set()
    for w in glob.glob(f"{CONTENT_WORKS}/t2-*.json"):
        try:
            with open(w) as f:
                d = json.load(f)
            pm = d.get("phase_mapping", {})
            if pm and pm.get("phase") == phase_num:
                seen.add(w)
        except: pass
    return len(seen)

# Check what's needed per phase
print("=== PHASE INVENTORY (all 17 phases) ===")
for phase_num in range(1, 18):
    count = count_phase(phase_num)
    print(f"Phase {phase_num:2d}: {count:3d} papers {'✅' if count >= 50 else f'(need {50-count})'}")

# Now fix the phase-1 counting and run it
print("\n\nPhase 1 actual count:", count_phase(1))
