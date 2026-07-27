#!/usr/bin/env python3
"""
_extract_s195_schoolbus.py — the five sibling school-bus guidelines (S195, staging only).

`g18` covers the school's own obligations. The same EDB page publishes five more
2026/27 guidelines aimed at the other parties a school has to supervise or advise:
drivers, escorts (跟車保母), operators, parents/guardians and the students
themselves. None had ever been ingested, so a question like "跟車保母有咩要求"
had nothing to answer from even though the answer is a published EDB guideline.

All five are text-layer PDFs; covers verified to name the audience they claim.

STAGING ONLY: writes dev/vault/<id>/extract_<id>.txt and nothing else. Ingest is
a separate explicit step (dev/ingest_one_source.py), and the registry entries plus
SOURCE_SETS wiring are separate again — a new Supabase source does NOT surface
until it is allowlisted (S135 backfill-allowlist coupling).

Usage (from repo root):
  python3 dev/_extract_s195_schoolbus.py --pdf-dir /tmp/sbus --dry-run
  python3 dev/_extract_s195_schoolbus.py --pdf-dir /tmp/sbus
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

BASE = ("https://www.edb.gov.hk/attachment/tc/student-parents/safety/"
        "sch-bus-services/2026_Guidelines_%s_TC.pdf")

JOBS = [
    {"pdf": "Drivers.pdf", "source_id": "sch_bus_drivers_2026", "slug": "Drivers",
     "title": "學童乘搭學生服務車輛的安全指引 — 供司機遵守（2026/27）",
     "audience": "司機"},
    {"pdf": "Escorts.pdf", "source_id": "sch_bus_escorts_2026", "slug": "Escorts",
     "title": "學童乘搭學生服務車輛的安全指引 — 供跟車保母遵守（2026/27）",
     "audience": "跟車保母"},
    {"pdf": "Operators.pdf", "source_id": "sch_bus_operators_2026", "slug": "Operators",
     "title": "學童乘搭學生服務車輛的安全指引 — 供學校巴士服務營辦商遵守（2026/27）",
     "audience": "營辦商"},
    {"pdf": "Parents.pdf", "source_id": "sch_bus_parents_2026", "slug": "Parents",
     "title": "學童乘搭學生服務車輛的安全指引 — 供家長／監護人遵守（2026/27）",
     "audience": "家長／監護人"},
    {"pdf": "Students.pdf", "source_id": "sch_bus_students_2026", "slug": "Students",
     "title": "學童乘搭學生服務車輛的安全指引 — 供學童遵守（2026/27）",
     "audience": "學童"},
]


def write_extract(job: dict, pdf_path: Path, dry: bool) -> dict:
    doc = fitz.open(pdf_path)
    url = BASE % job["slug"]
    header = [
        f"# {job['title']}",
        f"# source_id: {job['source_id']}",
        f"# title: {job['title']}",
        "# fact_type: policy",
        "# topic_tags: student",
        f"# url: {url}",
        "# source_type: pdf",
        "# extracted: 2026-07-27 (S195)",
        "# pipeline: _extract_s195_schoolbus.py (PyMuPDF get_text, verbatim, page markers)",
        f"# note: 2026/27 school-bus safety guidelines for {job['audience']}; "
        f"sibling of g18 (供學校) on the same EDB page",
        "# " + "=" * 60,
        "",
    ]
    body: list[str] = []
    for i, page in enumerate(doc, 1):
        body.append(f"=== Page {i} ===")
        body.append(page.get_text())
        body.append("")
    pages = doc.page_count
    cover = " ".join(doc[0].get_text().split())[:60]
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
        "source_id": job["source_id"], "pages": pages, "chunks": len(chunks),
        "char_min": min(lens), "char_med": int(statistics.median(lens)), "char_max": max(lens),
        "page_resolvable": all("=== Page" in c for c in chunks) if chunks else False,
        "nul": text.count("\x00"), "cover": cover,
        "audience_on_cover": job["audience"].split("／")[0] in cover,
    }

    out_dir = VAULT / job["source_id"]
    out_path = out_dir / f"extract_{job['source_id']}.txt"
    if not dry:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    stats["written"] = not dry
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pdf_dir = Path(args.pdf_dir)
    total = 0
    for job in JOBS:
        p = pdf_dir / job["pdf"]
        if not p.exists():
            sys.exit(f"ERROR: missing {p}")
        s = write_extract(job, p, args.dry_run)
        total += s["chunks"]
        print(f"[{s['source_id']:24}] pages={s['pages']:>2} chunks={s['chunks']:>2} "
              f"char={s['char_min']}/{s['char_med']}/{s['char_max']} "
              f"page_resolvable={s['page_resolvable']} nul={s['nul']} "
              f"audience_on_cover={s['audience_on_cover']} {'WROTE' if s['written'] else 'dry'}")
    print(f"\ntotal chunks across the five: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
