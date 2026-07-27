#!/usr/bin/env python3
"""Test Unpaywall PDF resolution for existing bridge papers."""
import json, time, urllib.request, urllib.parse, urllib.error, os

test_dois = [
    "10.3389/fpsyg.2021.647951",  # Frontiers - should have PDF
    "10.3390/e23060783",          # MDPI Entropy - should have PDF
    "10.3390/brainsci11050574",   # MDPI Brain Sciences
    "10.1371/journal.pone.0075526", # PLOS ONE
]

for doi in test_dois:
    url = f"https://api.unpaywall.org/v2/{doi}?email=hermes@research.local"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        best_loc = data.get("best_oa_location", {}) or {}
        pdf_url = best_loc.get("url_for_pdf", "")
        landing = best_loc.get("url_for_landing_page", "")
        print(f"\nDOI: {doi}")
        print(f"  OA status: {data.get('oa_status', 'unknown')}")
        print(f"  PDF URL: {pdf_url or 'N/A'}")
        print(f"  Landing: {landing or 'N/A'}")
        print(f"  Publisher: {best_loc.get('publisher', 'N/A')}")
        print(f"  Host type: {best_loc.get('host_type', 'N/A')}")
    except Exception as e:
        print(f"\nDOI: {doi} - Error: {e}")
    
    time.sleep(1)
