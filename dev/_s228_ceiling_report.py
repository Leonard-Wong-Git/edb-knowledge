#!/usr/bin/env python3
"""_s228_ceiling_report.py — rank the two windows captured by _s228_rerankCeiling.ts.

WHY SEPARATE FROM THE CAPTURE
  The signature match (NFKC fold + `=== Page N ===` stripping + dominant-page rules)
  lives in `_s213_run_gold.score_item` and must have exactly one definition. The
  TypeScript side therefore captures windows and scores nothing, the same split
  `routeFirstGold.ts` / `_s219_score_before_after.py` already uses.

WHAT IT ANSWERS (Open Priorities ②)
  Of the gold items whose answering passage is NOT in the production window (top 8),
  how many are present in the wider pool a re-ranker would see (top 40)? That count
  is the CEILING on the cross-encoder direction: a passage absent from the pool
  cannot be re-ranked into it.

  The ceiling is an upper bound twice over — presence is necessary, not sufficient,
  and the wide pool carries a wider per-source quota than production. Both errors
  point the same way, which is the safe direction for a bound.

READ-ONLY. Prints a report; writes nothing.

USAGE
  python3 dev/_s228_ceiling_report.py --self-test
  python3 dev/_s228_ceiling_report.py --capture dev/source/eval_runs/<date>_s228ceiling.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_run_gold import score_item  # noqa: E402


def rank_in(gold_item: dict, window: dict) -> int | None:
    """Rank of the answering chunk in one captured window, via the shared scorer."""
    if not window or window.get("error"):
        return None
    sc = score_item(gold_item, window.get("results") or [])
    return sc.get("rank_of_expected_chunk")


def classify(narrow: int | None, wide: int | None) -> str:
    if narrow is not None:
        return "in_window"
    if wide is not None:
        return "recoverable"
    return "not_in_pool"


def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    g = {"answerable": True, "expected_source_any": ["s"],
         "expected_passage_signature": ["目標句子"], "forbidden_evidence": []}
    win = {"results": [{"id": "a", "source_id": "s", "text": "無關", "score": 0.5},
                       {"id": "b", "source_id": "s", "text": "=== Page 3 === 目標句子", "score": 0.4}]}
    check("判分沿用 _s213_run_gold.score_item，頁碼標記不得造成假 miss", rank_in(g, win) == 1)
    check("空窗回傳 None，不可當 0", rank_in(g, {"results": []}) is None)
    check("擷取失敗回傳 None，不得當作『找不到』的證據", rank_in(g, {"error": "boom"}) is None)
    check("窗內命中 = in_window", classify(3, 3) == "in_window")
    check("只喺寬池命中 = recoverable（重排的上限）", classify(None, 17) == "recoverable")
    check("兩邊都冇 = not_in_pool，重排救唔到", classify(None, None) == "not_in_pool")
    # 證明它會紅：簽名改一個字，名次必須由 1 變 None。
    g2 = dict(g, expected_passage_signature=["目標句X"])
    check("斷言綁住內容：簽名改一個字即找不到", rank_in(g2, win) is None)
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", type=Path)
    ap.add_argument("--gold", type=Path, default=Path("dev/_s213_gold_all.json"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.capture:
        ap.error("--capture is required")

    gold = {g["id"]: g for g in json.loads(args.gold.read_text(encoding="utf-8"))}
    cap = json.loads(args.capture.read_text(encoding="utf-8"))
    rows = cap["results"]

    tally: Counter[str] = Counter()
    by_kind: dict[str, Counter[str]] = {}
    recoverable_rows: list[tuple[str, str, int]] = []

    for r in rows:
        g = gold[r["id"]]
        n = rank_in(g, r.get("narrow") or {})
        w = rank_in(g, r.get("wide") or {})
        state = classify(n, w)
        tally[state] += 1
        by_kind.setdefault(g["query_kind"], Counter())[state] += 1
        if state == "recoverable":
            recoverable_rows.append((r["id"], g["query"], w))

    total = len(rows)
    print(f"=== 有答案簽名的題目：{total} 條（窗 top_{cap['narrow_k']} vs 寬池 top_{cap['wide_k']}）===")
    print(f"  已經入窗            {tally['in_window']:>4}")
    print(f"  重排救得到（上限）  {tally['recoverable']:>4}")
    print(f"  寬池都冇，救唔到    {tally['not_in_pool']:>4}")
    print("\n  ⚠️ 『救得到』是上限而非預測：入池只是必要條件，而且寬池的每源配額比生產鬆。")

    print("\n=== 按查詢類型 ===")
    for k, c in sorted(by_kind.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        print(f"  {k:18s} n={n:>3}  已入窗 {c['in_window']:>3} · 救得到 {c['recoverable']:>3} · 救唔到 {c['not_in_pool']:>3}")

    print(f"\n=== 重排救得到的逐條（{len(recoverable_rows)} 條，括號為寬池名次）===")
    for i, (item_id, q, w) in enumerate(sorted(recoverable_rows, key=lambda x: x[2])):
        print(f"  {item_id:32s} @{w:<3} {q[:26]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
