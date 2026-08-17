#!/usr/bin/env python3
"""
extract_table_rows.py — coordinate-based table extraction for table-bearing sources
═══════════════════════════════════════════════════════════════════════════════════
S204. Writes the SAME `dev/vault/<source_id>/extract_<source_id>.txt` file that
`expand_vault.py --fetch` writes, so `--embed` consumes it unchanged. Run this BEFORE
`--fetch` (which skips sources that already have a vault extract).

Why this exists
───────────────
`expand_vault.py` extracts with PyMuPDF `page.get_text("text")`, which walks the page in
reading order. On the EDB establishment tables that emits COLUMN-MAJOR text: every 班數
value, then every 校長 value, then every 副校長 value… The row a number belongs to is
destroyed, and chunking can split a column block in half, so no downstream reader — LLM
or human — can reassemble it. `page.find_tables()` does not help: these PDFs have no
per-row ruling lines, so each column is detected as ONE cell holding every value.

This module instead clusters word-level bounding boxes by y-centre to rebuild real rows,
then renders each row as ONE self-contained sentence. A chunk boundary can then fall
anywhere without corrupting a row, and a query like 「12 班有幾多老師」 matches the row
that answers it.

Self-check (mandatory)
──────────────────────
Every spec carries `check`, an arithmetic invariant the table must satisfy on every row
(e.g. 校長 + 副校長 + 學位教師 + 助理 == 合計). Misaligned rows break the invariant, so a
silent extraction regression fails loudly instead of shipping wrong numbers. Extraction
aborts on any failed row — never write a partially-verified table.

Usage (from repo root):
  python3 dev/vault/extract_table_rows.py --self-test
  python3 dev/vault/extract_table_rows.py --source staff_est_pri --dry-run
  python3 dev/vault/extract_table_rows.py --source staff_est_pri
  python3 dev/vault/extract_table_rows.py --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_DIR = REPO_ROOT / "dev" / "vault"
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── Row reconstruction ────────────────────────────────────────────────────────

Y_TOLERANCE = 3.0  # points; words whose y-centres are within this belong to one row


def page_rows(page, tol: float = Y_TOLERANCE) -> list[str]:
    """Rebuild visual rows from word bounding boxes, left-to-right within each row."""
    buckets: dict[float, list] = defaultdict(list)
    keys: list[float] = []
    for w in page.get_text("words"):  # x0, y0, x1, y1, word, block, line, word_no
        centre = (w[1] + w[3]) / 2
        key = next((k for k in keys if abs(k - centre) <= tol), None)
        if key is None:
            keys.append(centre)
            key = centre
        buckets[key].append(w)
    return [
        " ".join(w[4] for w in sorted(buckets[k], key=lambda w: w[0]))
        for k in sorted(buckets)
    ]


# ── Table specs ───────────────────────────────────────────────────────────────
#
# `row`     regex over a reconstructed row; named groups become the row's fields
# `check`   invariant every row must satisfy (fields are ints where numeric)
# `render`  one self-contained sentence per row
# `pages`   1-based page numbers this table occupies, per sub-table

def _int(v: str) -> int:
    return 0 if v in {"--", "-", "—", "–"} else int(v)


def _vp(count: int) -> str:
    """The source prints `--` for class sizes with no deputy-head post; say so rather
    than rendering 「副校長 0 名」, which reads as a vacancy instead of no such post."""
    return "不設副校長職位" if count == 0 else f"副校長 {count} 名"


TABLE_SPECS: dict[str, dict] = {
    "staff_est_pri": {
        "title": "資助小學教學人員編制",
        "url": "https://www.edb.gov.hk/attachment/tc/sch-admin/admin/about-sch-staff/"
               "graduate-teacher-posts/Staff_est_pri_tc.pdf",
        "fact_type": "policy",
        "topic_tags": "hr",
        "tables": [
            {
                "pages": [1, 2],
                "caption": "全日制資助小學教學人員編制（由 2022/23 學年起生效）",
                "row": r'^(?P<classes>\d{1,2})\s+1\s*\((?P<head>.+?)\)\s+'
                       r'(?P<vp>--|-|\d+)\s+(?P<gm>\d+)\s+(?P<agm>\d+)\s+(?P<total>\d+)$',
                "check": lambda r: 1 + r["vp"] + r["gm"] + r["agm"] == r["total"],
                "render": lambda r: (
                    f"全日制資助小學核准開辦 {r['classes']} 班的教學人員編制："
                    f"校長 1 名（{r['head']}）、"
                    f"{_vp(r['vp'])}、"
                    f"小學學位教師 {r['gm']} 名（不包括副校長）、"
                    f"助理小學學位教師 {r['agm']} 名，"
                    f"教學人員合計 {r['total']} 名（包括校長）。"
                ),
            },
            {
                "pages": [3, 4],
                "caption": "半日制資助小學教學人員編制（由 2022/23 學年起生效）",
                "row": r'^(?P<classes>\d{1,2})\s+1\s*\((?P<head>.+?)\)\s+'
                       r'(?P<vp>--|-|\d+)\s+(?P<gm>\d+)\s+(?P<agm>\d+)\s+(?P<total>\d+)$',
                "check": lambda r: 1 + r["vp"] + r["gm"] + r["agm"] == r["total"],
                "render": lambda r: (
                    f"半日制資助小學核准開辦 {r['classes']} 班的教學人員編制："
                    f"校長 1 名（{r['head']}）、"
                    f"{_vp(r['vp'])}、"
                    f"小學學位教師 {r['gm']} 名（不包括副校長）、"
                    f"助理小學學位教師 {r['agm']} 名，"
                    f"教學人員合計 {r['total']} 名（包括校長）。"
                ),
            },
        ],
    },
    "staff_est_sp_sch_pri": {
        "title": "資助特殊學校小學部教學人員編制",
        "url": "https://www.edb.gov.hk/attachment/tc/sch-admin/admin/about-sch-staff/"
               "graduate-teacher-posts/Staff_est_sp_sch_pri_tc.pdf",
        "fact_type": "policy",
        "topic_tags": "hr",
        "tables": [
            {
                "pages": [1, 2],
                "caption": "資助特殊學校小學部教學人員編制（由 2022/23 學年起生效）",
                "row": r'^(?P<total>\d{1,2})\s+(?P<gm>--|-|\d+)\s+(?P<agm>\d+)$',
                "check": lambda r: r["gm"] + r["agm"] == r["total"],
                "render": lambda r: (
                    f"資助特殊學校小學部教學人員總數為 {r['total']} 名（不包括校長）時，"
                    f"各職級的職位數目為：小學學位教師 {r['gm']} 名、"
                    f"助理小學學位教師 {r['agm']} 名。"
                ),
            },
        ],
    },
}


def parse_table(doc, table: dict) -> tuple[list[dict], list[str]]:
    """Reconstruct the table's rows, then verify them.

    Returns (rows, leftovers). `leftovers` is every reconstructed line on the table's
    pages that is not a data row — captions, column headers and the footnotes that carry
    the ratios the grid itself omits (e.g. 全日制每 3.2 名教師設 1 個主任級職位). Those are
    kept verbatim rather than pattern-matched, so a note the source adds later is not
    silently dropped.
    """
    pattern = re.compile(table["row"])
    rows: list[dict] = []
    leftovers: list[str] = []

    for pno in table["pages"]:
        for line in page_rows(doc[pno - 1]):
            text = line.strip()
            m = pattern.match(text)
            if m:
                rows.append({
                    key: _int(val) if re.fullmatch(r'-{1,2}|—|–|\d+', val) else val
                    for key, val in m.groupdict().items()
                })
            elif len(text) >= 6:
                leftovers.append(text)

    failed = [r for r in rows if not table["check"](r)]
    if failed:
        raise SystemExit(
            f"❌ arithmetic self-check failed on {len(failed)} row(s) — extraction is "
            f"misaligned, refusing to write.\n   first failure: {failed[0]}"
        )
    if not rows:
        raise SystemExit(f"❌ no rows matched for table on pages {table['pages']}")
    return rows, leftovers


def build_extract(source_id: str, pdf_path: Path) -> tuple[str, int]:
    """Render the vault extract text for one source. Returns (text, row_count)."""
    import fitz  # PyMuPDF

    spec = TABLE_SPECS[source_id]
    doc = fitz.open(pdf_path)
    out: list[str] = [
        f"# {spec['title']}",
        f"# source_id: {source_id}",
        f"# title: {spec['title']}",
        f"# fact_type: {spec['fact_type']}",
        f"# topic_tags: {spec['topic_tags']}",
        f"# url: {spec['url']}",
        "# extracted: extract_table_rows.py (coordinate row reconstruction, S204)",
        "# auto_processed: false",
        "# " + "=" * 58,
        "",
    ]
    total_rows = 0
    for table in spec["tables"]:
        rows, leftovers = parse_table(doc, table)
        total_rows += len(rows)
        # Anchor the table to its first page so page attribution points at the real table.
        out.append(f"=== Page {table['pages'][0]} ===")
        out.append(table["caption"])
        out.append("")
        out.extend(table["render"](r) for r in rows)
        out.append("")
        if leftovers:
            out.append(f"{table['caption']}的說明及附註：")
            out.extend(leftovers)
            out.append("")
    doc.close()
    return "\n".join(out), total_rows


# ── Self-test ─────────────────────────────────────────────────────────────────

SELF_TEST_ROWS = """班數 校長(職級) 副校長 小學學位教師 助理小學學位教師 合計
1 1 (高級小學學位教師) -- 1 0 2
12 1 (二級小學校長) 1 5 14 21
36 1 (一級小學校長) 3 15 40 59
"""


def self_test() -> int:
    spec = TABLE_SPECS["staff_est_pri"]["tables"][0]
    pattern = re.compile(spec["row"])
    parsed = []
    for line in SELF_TEST_ROWS.strip().splitlines()[1:]:
        m = pattern.match(line.strip())
        if not m:
            print(f"❌ row did not parse: {line}")
            return 1
        row = {k: (_int(v) if re.fullmatch(r'-{1,2}|—|–|\d+', v) else v)
               for k, v in m.groupdict().items()}
        if not spec["check"](row):
            print(f"❌ self-check failed: {row}")
            return 1
        parsed.append(row)
    if [r["classes"] for r in parsed] != [1, 12, 36]:
        print("❌ unexpected parse result")
        return 1
    if "12 班的教學人員編制" not in spec["render"](parsed[1]):
        print("❌ render did not produce a self-contained row sentence")
        return 1
    # A deliberately misaligned row must be rejected, not silently rendered.
    if spec["check"]({"vp": 1, "gm": 5, "agm": 14, "total": 99}):
        print("❌ self-check accepted a misaligned row")
        return 1
    print(f"✅ self-test passed ({len(parsed)} rows parsed, misalignment rejected)")
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────

def fetch_pdf(url: str, dest: Path) -> Path:
    import requests

    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, headers=HTTP_HEADERS, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--source", help="source_id from TABLE_SPECS")
    ap.add_argument("--all", action="store_true", help="process every spec")
    ap.add_argument("--pdf", help="use a local PDF instead of downloading")
    ap.add_argument("--dry-run", action="store_true", help="print, do not write")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    targets = list(TABLE_SPECS) if args.all else ([args.source] if args.source else [])
    if not targets:
        ap.error("need --source, --all or --self-test")
    for source_id in targets:
        if source_id not in TABLE_SPECS:
            print(f"❌ no table spec for {source_id}")
            return 1
        spec = TABLE_SPECS[source_id]
        pdf = Path(args.pdf) if args.pdf else VAULT_DIR / source_id / f"{source_id}.pdf"
        if not pdf.exists():
            print(f"  ↓ downloading {source_id}…")
            fetch_pdf(spec["url"], pdf)
        text, rows = build_extract(source_id, pdf)
        out_path = VAULT_DIR / source_id / f"extract_{source_id}.txt"
        print(f"✅ {source_id}: {rows} rows, {len(text):,} chars → {out_path}")
        if args.dry_run:
            print("\n".join(text.splitlines()[:18]))
            print("   …")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
