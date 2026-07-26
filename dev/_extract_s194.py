#!/usr/bin/env python3
"""
_extract_s194.py — one-off verbatim extraction for S194 (staging only).
────────────────────────────────────────────────────────────────────────
Writes canonical `dev/vault/<id>/extract_<id>.txt` files (same format as
`prepare_ingest_package.write_extract`: `# key: value` header, then one
`=== Page N ===` marker per source page) for the two documents S194 ingests:

  1. iit_ai_framework_2026 — 《小學資訊與創新科技課程框架》「人工智能初探」範疇
     （試行版）. The body of the framework announced by EDBCM113/2026; the
     circular itself only yielded 3 chunks (cover + summary).
  2. ict_sss_2021 — the REAL 《資訊及通訊科技 課程及評估指引 (中四至中六) 2021》,
     replacing content that was never this document: the registry entry pointed
     at `CS_CAG_S4-6_Chi_2021.pdf`, which is the 公民與社會發展科 guide (`CS` =
     Citizenship and Social development, not Computer Science). The 公社科 text
     already in the vault is preserved by moving it to `cgss_sss_2021`, not by
     re-extracting it, so the bytes behind the live chunks stay verbatim.

STAGING ONLY: writes files under dev/vault/ and nothing else. No embedding, no
Supabase, no git. Ingest is a separate, explicit step (dev/ingest_one_source.py).

Usage (from repo root):
  python3 dev/_extract_s194.py --pdf-dir <dir holding the two downloaded PDFs>
  python3 dev/_extract_s194.py --pdf-dir <dir> --dry-run
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

JOBS = [
    {
        "pdf": "IIT_Summary_on_AI_TC.pdf",
        "source_id": "iit_ai_framework_2026",
        "title": "《小學資訊與創新科技課程框架》—「人工智能初探」範疇（試行版）",
        "topic_tags": "curriculum,it",
        "url": ("https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/"
                "technology-edu/curriculum-doc/IIT_Summary%20on%20AI_TC.pdf"),
        "note": "framework body announced by EDBCM113/2026",
    },
    {
        "pdf": "ICT_CA_Guide_c_final.pdf",
        "source_id": "ict_sss_2021",
        "title": ("資訊及通訊科技 (中四至中六) 二零二一年 "
                  "(於2022/23學年的中四實施並在2025年及以後的香港中學文憑考試生效)"),
        "topic_tags": "curriculum,it",
        "url": ("https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/"
                "technology-edu/curriculum-doc/ICT_C&A%20Guide_c_final.pdf"),
        "note": "replaces the mis-pointed edcity CS_CAG url (S194)",
    },
]


def write_extract(job: dict, pdf_path: Path, dry: bool) -> dict:
    doc = fitz.open(pdf_path)
    header = [
        f"# {job['title']}",
        f"# source_id: {job['source_id']}",
        f"# title: {job['title']}",
        "# fact_type: policy",
        f"# topic_tags: {job['topic_tags']}",
        f"# url: {job['url']}",
        "# source_type: pdf",
        "# extracted: 2026-07-26 (S194)",
        "# pipeline: _extract_s194.py (PyMuPDF get_text, verbatim, page markers)",
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
    # Dry-run chunk count uses the canonical chunker on the header-stripped body,
    # matching what ingest_one_source will actually insert.
    chunks = []
    seen = set()
    for ch in bw.chunk_text_with_page_carry("\n".join(body).strip()):
        h = bw.text_hash(ch)
        if h in seen:
            continue
        seen.add(h)
        chunks.append(ch)
    lens = [len(c) for c in chunks] or [0]
    stats = {
        "source_id": job["source_id"],
        "pages": pages,
        "body_chars": len("\n".join(body).strip()),
        "chunks": len(chunks),
        "char_min": min(lens),
        "char_med": int(statistics.median(lens)),
        "char_max": max(lens),
        "page_resolvable": all("=== Page" in c for c in chunks) if chunks else False,
        "nul_bytes": text.count("\x00"),
    }

    out_dir = VAULT / job["source_id"]
    out_path = out_dir / f"extract_{job['source_id']}.txt"
    if not dry:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    stats["path"] = str(out_path.relative_to(REPO_ROOT))
    stats["written"] = not dry
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdf_dir = Path(args.pdf_dir)
    for job in JOBS:
        pdf_path = pdf_dir / job["pdf"]
        if not pdf_path.exists():
            sys.exit(f"ERROR: missing {pdf_path}")
        s = write_extract(job, pdf_path, args.dry_run)
        print(f"[{s['source_id']}] pages={s['pages']} body_chars={s['body_chars']} "
              f"chunks={s['chunks']} char(min/med/max)={s['char_min']}/{s['char_med']}/{s['char_max']} "
              f"page_resolvable={s['page_resolvable']} nul={s['nul_bytes']} "
              f"{'WROTE' if s['written'] else 'dry-run'} {s['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
