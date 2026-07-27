#!/usr/bin/env python3
"""
_extract_s195.py — one-off verbatim extraction for S195 (staging only).
────────────────────────────────────────────────────────────────────────
Writes the canonical `dev/vault/<id>/extract_<id>.txt` (same format as
`_extract_s194.py` / `prepare_ingest_package.write_extract`) for:

  g18 — 學童乘搭校車的安全指引, refreshed to the 2026/27 edition.

Why a re-extract and not a URL re-point: the ingested text is the 2025/26
edition (8 pages) and EDB has replaced it with the 2026/27 edition
(`2026_Guidelines_Schools_TC.pdf`, 6 pages). Comparing them page-by-page,
only 3/8 pages are identical — this is a content revision, not a rename, so
re-pointing the URL would leave 2025/26 text citing a 2026/27 document (the
S194 `ict_sss_2021` failure mode). The old URL now 404s (served-URL monitor
issue #4).

STAGING ONLY: writes one file under dev/vault/ and nothing else. No embedding,
no Supabase, no git. Ingest is a separate explicit step (dev/ingest_one_source.py),
and the stale chunks must be DELETEd by source_id first — chunk ids are
content-hashed, so an insert alone would leave the 2025/26 rows in place.

Usage (from repo root):
  python3 dev/_extract_s195.py --pdf <path to 2026_Guidelines_Schools_TC.pdf> --dry-run
  python3 dev/_extract_s195.py --pdf <path>
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
import build_wiki_index as bw  # canonical chunker, for the dry-run count

JOB = {
    "source_id": "g18",
    "title": "學童乘搭校車的安全指引（2026/27）",
    "topic_tags": "student",
    "url": ("https://www.edb.gov.hk/attachment/tc/student-parents/safety/"
            "sch-bus-services/2026_Guidelines_Schools_TC.pdf"),
    "note": ("2026/27 edition; replaces the 2025/26 edition whose URL now 404s "
             "(only 3/8 pages carried over, so re-ingested rather than re-pointed) — S195"),
}


def write_extract(pdf_path: Path, dry: bool) -> dict:
    doc = fitz.open(pdf_path)
    header = [
        f"# {JOB['title']}",
        f"# source_id: {JOB['source_id']}",
        f"# title: {JOB['title']}",
        "# fact_type: policy",
        f"# topic_tags: {JOB['topic_tags']}",
        f"# url: {JOB['url']}",
        "# source_type: pdf",
        "# extracted: 2026-07-27 (S195)",
        "# pipeline: _extract_s195.py (PyMuPDF get_text, verbatim, page markers)",
        f"# note: {JOB['note']}",
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
    stats = {
        "source_id": JOB["source_id"],
        "pages": pages,
        "body_chars": len("\n".join(body).strip()),
        "chunks": len(chunks),
        "char_min": min(lens),
        "char_med": int(statistics.median(lens)),
        "char_max": max(lens),
        "page_resolvable": all("=== Page" in c for c in chunks) if chunks else False,
        "nul_bytes": text.count("\x00"),
    }

    out_dir = VAULT / JOB["source_id"]
    out_path = out_dir / f"extract_{JOB['source_id']}.txt"
    if not dry:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    stats["path"] = str(out_path.relative_to(REPO_ROOT))
    stats["written"] = not dry
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        sys.exit(f"ERROR: missing {pdf_path}")
    s = write_extract(pdf_path, args.dry_run)
    print(f"[{s['source_id']}] pages={s['pages']} body_chars={s['body_chars']} "
          f"chunks={s['chunks']} char(min/med/max)={s['char_min']}/{s['char_med']}/{s['char_max']} "
          f"page_resolvable={s['page_resolvable']} nul={s['nul_bytes']} "
          f"{'WROTE' if s['written'] else 'dry-run'} {s['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
