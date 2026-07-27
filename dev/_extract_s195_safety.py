#!/usr/bin/env python3
"""
_extract_s195_safety.py — repair the g21 / g22 citation misalignment (S195, staging only).

GitHub issue #5. Both sources return 200 and their covers match their titles, so
no monitor could see this; what is wrong is the document↔page correspondence.

g22 《科技教育–安全指引》
    The vault held 51 pages against a 52-page PDF and aligned only at offset +1 —
    the original extraction dropped the cover sheet, so every cited page number is
    one ahead of the real PDF sheet. Fixed by re-extracting all 52 pages.

g21 《視覺藝術科安全指引》
    The vault was TWO documents concatenated under one continuous numbering:
    pages 1-21 from VAsafety_pri_c.pdf (小學, revised from the 2000 edition) and
    pages 22-46 from VAsafety_sec_c.pdf (中學, revised from the 2002 edition) —
    each contributing its pages minus a blank cover, 21 + 25 = 46. All 49 chunks
    cited the PRIMARY url, so roughly half pointed at a document they did not come
    from, with anchors running past the end of a 22-page file. Fixed by splitting:
    g21 keeps the primary guide alone, and the secondary guide becomes its own
    source `va_safety_sec`.

STAGING ONLY: writes dev/vault/<id>/extract_<id>.txt. Ingest, the registry entry
for the new source, SOURCE_SETS wiring and the deletion of superseded chunks are
separate explicit steps. Deletion must use old_ids MINUS new_ids — chunk ids are
content hashes, so text that survives a re-extract keeps its id (S195 g18 lesson).

Usage (from repo root):
  python3 dev/_extract_s195_safety.py --pdf-dir /tmp --dry-run
  python3 dev/_extract_s195_safety.py --pdf-dir /tmp
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

import fitz  # PyMuPDF

REPO_ROOT = Path(__file__).resolve().parent.parent  # …/Draft
VAULT = REPO_ROOT / "dev" / "vault"
sys.path.insert(0, str(VAULT))
import build_wiki_index as bw

EDB = "https://www.edb.gov.hk/attachment"

JOBS = [
    {
        "pdf": "va_pri.pdf",
        "source_id": "g21",
        "title": "視覺藝術科安全指引（小學）",
        "topic_tags": "curriculum",
        "url": f"{EDB}/tc/curriculum-development/kla/arts-edu/resources/va-curri/VAsafety_pri_c.pdf",
        "note": ("S195 re-extract: the previous vault file concatenated this primary guide with the "
                 "secondary one (now va_safety_sec) under continuous numbering, so half the chunks "
                 "cited the wrong document; page markers also ran one ahead of the PDF sheet"),
        "expect_pages": 22,
    },
    {
        "pdf": "va_sec.pdf",
        "source_id": "va_safety_sec",
        "title": "視覺藝術科安全指引（中學）",
        "topic_tags": "curriculum",
        "url": f"{EDB}/tc/curriculum-development/kla/arts-edu/resources/va-curri/VAsafety_sec_c.pdf",
        "note": ("S195 NEW: split out of g21, whose vault file had silently carried this document's "
                 "25 pages under the primary guide's URL since S149"),
        "expect_pages": 26,
    },
    {
        "pdf": "tech_safety.pdf",
        "source_id": "g22",
        "title": "科技教育–安全指引（中學科技與生活／家政科教學安全手冊，2010）",
        "topic_tags": "curriculum",
        "url": (f"{EDB}/en/curriculum-development/kla/technology-edu/resources/"
                "technology-and-living/Safety_Booklet(Chi)_final_2010_r1.pdf"),
        "note": ("S195 re-extract: the previous vault file dropped the cover sheet, so every cited "
                 "page number ran one ahead of the real PDF sheet (50/51 pages aligned at offset +1)"),
        "expect_pages": 52,
    },
]


def write_extract(job: dict, pdf_path: Path, dry: bool) -> dict:
    doc = fitz.open(pdf_path)
    if doc.page_count != job["expect_pages"]:
        sys.exit(f"ABORT {job['source_id']}: expected {job['expect_pages']} pages, "
                 f"got {doc.page_count} — wrong file?")
    header = [
        f"# {job['title']}",
        f"# source_id: {job['source_id']}",
        f"# title: {job['title']}",
        "# fact_type: policy",
        f"# topic_tags: {job['topic_tags']}",
        f"# url: {job['url']}",
        "# source_type: pdf",
        "# extracted: 2026-07-27 (S195)",
        "# pipeline: _extract_s195_safety.py (PyMuPDF get_text, verbatim, page markers)",
        f"# note: {job['note']}",
        "# " + "=" * 60,
        "",
    ]
    body: list[str] = []
    for i, page in enumerate(doc, 1):
        body.append(f"=== Page {i} ===")
        body.append(page.get_text())
        body.append("")
    pages = doc.page_count
    doc.close()

    text = "\n".join(header + body)
    chunks, seen = [], set()
    for ch in bw.chunk_text_with_page_carry("\n".join(body).strip()):
        h = bw.text_hash(ch)
        if h in seen:
            continue
        seen.add(h)
        chunks.append(ch)
    lens = [len(c) for c in chunks] or [0]
    out_path = VAULT / job["source_id"] / f"extract_{job['source_id']}.txt"
    if not dry:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # the old g21 file has a different name; remove it so the vault dir has one truth
        for stale in out_path.parent.glob("extract_*.txt"):
            if stale != out_path:
                stale.unlink()
        out_path.write_text(text, encoding="utf-8")
    return {"source_id": job["source_id"], "pages": pages, "chunks": len(chunks),
            "char_min": min(lens), "char_med": int(statistics.median(lens)), "char_max": max(lens),
            "page_resolvable": all("=== Page" in c for c in chunks) if chunks else False,
            "nul": text.count("\x00"), "written": not dry}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    pdf_dir = Path(args.pdf_dir)
    for job in JOBS:
        p = pdf_dir / job["pdf"]
        if not p.exists():
            sys.exit(f"ERROR: missing {p}")
        s = write_extract(job, p, args.dry_run)
        print(f"[{s['source_id']:16}] pages={s['pages']:>2} chunks={s['chunks']:>2} "
              f"char={s['char_min']}/{s['char_med']}/{s['char_max']} "
              f"page_resolvable={s['page_resolvable']} nul={s['nul']} "
              f"{'WROTE' if s['written'] else 'dry'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
