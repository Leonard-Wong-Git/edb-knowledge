#!/usr/bin/env python3
"""_s214_nfkc_diff.py — prove the S214 NFKC patch touched ONLY the chunk layer.

`eval_retrieval.py --compare` answers "is this a regression". That is not the
question Codex asked. The question is narrower and stricter:

    did the NFKC fold change ANYTHING at the source layer, or the query set?

`--compare` cannot answer it, because it folds source-layer and chunk-layer
changes into one row status and treats a source rank move as a non-failing
`RANK_SHIFT`. A non-failing change is still a change, and here any source-layer
change at all would mean the patch leaked out of `chunk_verdict_for`.

So this walks the two run files field by field and partitions every difference
into SOURCE (must be empty) and CHUNK (the only place the fix may show up).

Read-only. No network. Usage from repo root:
    python3 dev/_s214_nfkc_diff.py BEFORE.json AFTER.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE_FIELDS = ["query", "verdict", "rank_of_expected", "source_ids",
                 "expect_any", "error"]
CHUNK_FIELDS = ["chunk_verdict", "rank_of_expected_chunk", "expect_text_any"]


def load(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    before, after = load(sys.argv[1]), load(sys.argv[2])
    b = {r["id"]: r for r in before["results"]}
    a = {r["id"]: r for r in after["results"]}

    print(f"before: {sys.argv[1]}")
    print(f"        label={before.get('label')!r} n={len(b)}")
    print(f"after : {sys.argv[2]}")
    print(f"        label={after.get('label')!r} n={len(a)}")
    print()

    # ---- query set -------------------------------------------------------
    only_b, only_a = sorted(set(b) - set(a)), sorted(set(a) - set(b))
    print("== QUERY SET ==")
    if only_b or only_a:
        print(f"  CHANGED  only-in-before={only_b}  only-in-after={only_a}")
    else:
        print(f"  IDENTICAL  {len(b)} ids, same set")

    # A query set can match as a set and still differ in what is asserted.
    assert_diff = [q for q in sorted(set(b) & set(a))
                   if b[q].get("expect_any") != a[q].get("expect_any")
                   or b[q].get("expect_text_any") != a[q].get("expect_text_any")]
    print(f"  assertions changed on: {assert_diff or 'none'}")
    print()

    # ---- source layer ----------------------------------------------------
    src_rows, chunk_rows = [], []
    for q in sorted(set(b) & set(a)):
        for f in SOURCE_FIELDS:
            if b[q].get(f) != a[q].get(f):
                src_rows.append((q, f, b[q].get(f), a[q].get(f)))
        for f in CHUNK_FIELDS:
            if b[q].get(f) != a[q].get(f):
                chunk_rows.append((q, f, b[q].get(f), a[q].get(f)))

    print("== SOURCE LAYER (must be empty) ==")
    if not src_rows:
        print("  CLEAN  0 differences across "
              f"{len(set(b) & set(a))} queries x {len(SOURCE_FIELDS)} fields")
    for q, f, bv, av in src_rows:
        print(f"  DIFF {q}.{f}: {str(bv)[:90]} -> {str(av)[:90]}")
    print()

    print("== CHUNK LAYER (the fix may show up here) ==")
    if not chunk_rows:
        print("  no chunk-layer differences")
    for q, f, bv, av in chunk_rows:
        print(f"  DIFF {q}.{f}: {str(bv)[:90]} -> {str(av)[:90]}")
    print()

    # ---- scores ----------------------------------------------------------
    # Scores come from the live endpoint, not from the matcher. They are
    # EXPECTED to drift between runs and say nothing about this patch; reported
    # separately so a reader never mistakes live jitter for a matcher change.
    moved = sum(1 for q in set(b) & set(a)
                if b[q].get("scores") != a[q].get("scores"))
    print(f"== LIVE JITTER (not attributable to the patch) ==\n"
          f"  queries whose scores differ between runs: {moved}")
    print()

    ok = not src_rows and not only_b and not only_a and not assert_diff
    print("VERDICT:", "PASS — patch is confined to the chunk layer" if ok
          else "FAIL — the patch changed something outside the chunk layer")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
