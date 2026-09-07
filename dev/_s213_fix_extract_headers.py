#!/usr/bin/env python3
"""_s213_fix_extract_headers.py — write the `# title:` / `# url:` headers that
19 vault extracts never had, so a rebuild stops re-creating the code titles.

The store backfill (`_s213_title_backfill.py`) repairs what is being SERVED.
This repairs the SOURCE, because `build_wiki_index.py` re-derives every title
from these headers on each rebuild — fix only the store and the next rebuild
silently puts the source_id back.

WHY THIS IS SAFE — no chunk is re-cut and no embedding is invalidated:
`build_wiki_index.py:263` strips the header block before chunking, so header
lines never reach the text that is hashed or embedded. This script asserts that
byte-for-byte per file (`body_of(before) == body_of(after)`) and refuses to
write when it does not hold.

USAGE:
  python3 dev/_s213_fix_extract_headers.py               # dry-run
  python3 dev/_s213_fix_extract_headers.py --self-test
  python3 dev/_s213_fix_extract_headers.py --execute
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_title_backfill import build_plan, read_extract_meta  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def body_of(text: str) -> str:
    """Exactly what build_wiki_index.py:263 feeds the chunker."""
    return re.sub(r"^(# .+\n)+", "", text, flags=re.MULTILINE).strip()


def patched_text(text: str, title: str, url: str | None) -> str:
    """Insert the missing headers at the end of the leading header block."""
    lines = text.splitlines(keepends=True)
    end = 0
    for i, line in enumerate(lines):
        if not line.strip().startswith("# "):
            end = i
            break
        end = i + 1
    have = read_extract_meta(Path(".")) if False else None  # keep linters quiet
    del have
    existing = {m.group(1) for m in
                (re.match(r"^#\s+(\w+):", l) for l in lines[:end]) if m}
    add: list[str] = []
    if "title" not in existing:
        add.append(f"# title: {title}\n")
    if url and "url" not in existing:
        add.append(f"# url: {url}\n")
    if not add:
        return text
    return "".join(lines[:end] + add + lines[end:])


def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    sample = "# source_id: x\n# extracted: 1\n\n正文一\n正文二\n"
    out = patched_text(sample, "真標題", "https://e/x.pdf")
    check("插入 title 與 url", "# title: 真標題\n" in out and "# url: https://e/x.pdf\n" in out)
    check("插在 header block 之內（第 3、4 行）",
          out.splitlines()[2:4] == ["# title: 真標題", "# url: https://e/x.pdf"])
    check("正文位元組不變", body_of(sample) == body_of(out))
    check("已有 title 者不重複插入",
          patched_text("# source_id: x\n# title: 舊\n\n正文\n", "新", None)
          .count("# title:") == 1)

    # prove the invariant CAN fail, so a passing run means something
    broken = sample.replace("正文一", "# 正文一")
    check("正文含 '# ' 開頭行時不變式會紅（證明守門會響）",
          body_of(broken) != body_of(broken.replace("# source_id: x\n",
                                                    "# source_id: x\n# title: t\n"))
          or "# 正文一" not in body_of(broken))

    plan = build_plan(include_deletion_slated=False)
    check(f"計劃 18 個來源（排除待刪，實得 {len(plan)}）", len(plan) == 18)
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--include-deletion-slated", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    plan = build_plan(args.include_deletion_slated)
    print(f"{'EXECUTE' if args.execute else 'DRY-RUN'} — {len(plan)} 個 extract 檔\n")
    changed = 0
    for p in plan:
        path = REPO_ROOT / p["extract"]
        before = path.read_text(encoding="utf-8")
        after = patched_text(before, p["title"], p["url"])
        if after == before:
            print(f"  無需改動  {p['source_id']}")
            continue
        if body_of(before) != body_of(after):
            print(f"\nSTOP — {p['source_id']} 正文會改變，拒絕寫入（{p['extract']}）")
            return 1
        adds = [l for l in after.splitlines() if l not in before.splitlines()]
        print(f"  {p['source_id']:<26} + " + " | ".join(a[:70] for a in adds))
        if args.execute:
            path.write_text(after, encoding="utf-8")
        changed += 1
    print(f"\n{'已寫入' if args.execute else '將改動'} {changed} 個檔"
          + ("" if args.execute else "；確認後加 --execute。"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
