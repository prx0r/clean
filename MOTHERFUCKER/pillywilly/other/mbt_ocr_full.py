"""Full batch OCR of all MBT Sanskrit pages via Google Vision API.
Saves incrementally for resumability."""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import fitz
import requests
import yaml

VISION_KEY = os.environ.get("VISION_API_KEY", "AIzaSyA7-ZK5BGBxDwGCGx1Wiro0fB7NfX68KIc")
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_KEY}"

BASE = Path(__file__).parents[1]
SOURCES = BASE / "sources"
OUTPUT = BASE / "data" / "ocr"
OUTPUT.mkdir(parents=True, exist_ok=True)

STATE_FILE = OUTPUT / "mbt_ocr_full_state.json"
MANIFEST_FILE = BASE / "data" / "manifests" / "mbt_kumarikakhanda_ocr_pilot.yaml"

MBT_FILE = list(SOURCES.glob("Manthānabhairavatantram _*"))[0]


def get_khalnayak_pages(pdf_path: str) -> list[int]:
    doc = fitz.open(pdf_path)
    pages = []
    for pn in range(len(doc)):
        fonts = doc[pn].get_fonts()
        if any("Khalnayak" in f[3] for f in fonts):
            pages.append(pn + 1)
    doc.close()
    return pages


def ocr_page(pdf_path: str, page_num: int, dpi: int = 300) -> tuple[int, str, float]:
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc.close()

    img_b64 = base64.b64encode(img_bytes).decode()
    payload = {
        "requests": [{
            "image": {"content": img_b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {"languageHints": ["sa", "hi"]},
        }]
    }

    t0 = time.time()
    r = requests.post(VISION_URL, json=payload, timeout=120)
    elapsed = time.time() - t0

    if r.status_code != 200:
        return page_num, f"HTTP {r.status_code}: {r.text[:200]}", elapsed

    resp = r.json()
    api_err = resp.get("responses", [{}])[0].get("error")
    if api_err:
        return page_num, f"API error: {api_err}", elapsed

    text = resp["responses"][0].get("textAnnotations", [{}])[0].get("description", "")
    return page_num, text, elapsed


def load_state() -> dict:
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        print(f"Resuming from saved state: {len(data.get('results', {}))} pages done")
        return data
    return {"results": {}, "errors": {}, "timing": [], "total_chars": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    # Also save readable full text
    out_lines = []
    for pn in sorted(state["results"].keys(), key=int):
        out_lines.append(f"\n{'='*60}\n[Page {pn}]\n{'='*60}")
        out_lines.append(state["results"][pn])
    (OUTPUT / "mbt_sanskrit_full_ocr.txt").write_text("\n".join(out_lines))


def produce_manifest(state: dict, all_pages: list[int]):
    """Convert OCR results to a YAML manifest matching Spandakārikā format."""
    passages = []
    for pn in all_pages:
        sp = str(pn)
        if sp not in state["results"]:
            continue
        text = state["results"][sp]
        passage = {
            "id": f"mbt.ocr.{pn:04d}",
            "reading_id": f"mbt.ocr.{pn:04d}.vision.2026",
            "type": "ocr_page",
            "transliteration": "Devanagari",
            "critical_status": "vision_ocr_unreviewed",
            "sanskrit": text,
            "source_page": str(pn),
        }
        passages.append(passage)

    manifest = {
        "work": {
            "id": "mbt_kumarikakhanda",
            "title": "Manthānabhairavatantram — Kumārikākhaṇḍaḥ",
            "title_iast": "Manthānabhairavatantram — Kumārikākhaṇḍaḥ",
            "author": "Dyczkowski (ed.)",
            "tradition": "kubjika",
            "genre": "tantra",
            "metadata": {
                "pilot_role": "full_ocr_calibration",
                "source_file": MBT_FILE.name,
                "ocr_engine": "google_vision_document_text_detection",
                "language_hints": ["sa", "hi"],
                "pages_processed": len(passages),
                "total_sanskrit_pages": len(all_pages),
            }
        },
        "edition": {
            "id": "dyczkowski.2009.ignca",
            "editor": "Mark S. G. Dyczkowski",
            "publication": "Indira Gandhi National Centre for the Arts, New Delhi",
            "year": 2009,
            "isbn": "9788124604984",
            "licence": "locally supplied commercial scan; not for redistribution",
            "critical_method": "Google Vision API OCR from rendered page images; unreviewed import",
        },
        "passages": passages,
    }

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"\nManifest saved: {MANIFEST_FILE}")


def main():
    print("Finding Sanskrit pages...")
    all_pages = get_khalnayak_pages(str(MBT_FILE))
    print(f"Total Sanskrit pages: {len(all_pages)}")

    state = load_state()
    results = state.setdefault("results", {})
    errors = state.setdefault("errors", {})
    timing = state.setdefault("timing", [])

    pending = [p for p in all_pages if str(p) not in results]
    print(f"Already done: {len(results)} | Pending: {len(pending)}")

    start_time = time.time()
    for i, pn in enumerate(pending):
        t0 = time.time()
        page_num, text, sec = ocr_page(str(MBT_FILE), pn)

        sp = str(page_num)
        if text.startswith("HTTP") or text.startswith("API error"):
            errors[sp] = text
            print(f"[{i+1}/{len(pending)}] Page {pn}: ERROR — {text[:60]}")
        else:
            results[sp] = text
            state["total_chars"] = sum(len(v) for v in results.values())
            timing.append({"page": pn, "seconds": round(sec, 2)})
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            rem = (len(pending) - i - 1) / rate if rate > 0 else 0
            print(f"[{i+1}/{len(pending)}] Page {pn}: {len(text)} chars ({sec:.1f}s, {rate:.1f}pg/s, ETA {rem/60:.0f}min)")

        # Save every 10 pages
        if (i + 1) % 10 == 0:
            save_state(state)

    # Final save
    save_state(state)

    elapsed = time.time() - start_time
    total_ok = len(results)
    total_err = len(errors)
    total_chars = state["total_chars"]

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"Total pages: {len(all_pages)}")
    print(f"  Success: {total_ok}")
    print(f"  Errors:  {total_err}")
    print(f"Total chars: {total_chars}")
    print(f"Time: {elapsed/60:.1f} min ({elapsed/len(all_pages):.2f}s avg)")

    # Produce manifest
    produce_manifest(state, all_pages)

    return total_ok == len(all_pages)


if __name__ == "__main__":
    main()
