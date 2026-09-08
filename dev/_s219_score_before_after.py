#!/usr/bin/env python3
"""_s219_score_before_after.py — score the route-first before/after capture.

Consumes the JSONL written by `backend/scripts/routeFirstGold.ts` and scores both
sides with `_s213_run_gold.score_item`, so the NFKC-folding scorer stays single-
sourced rather than reimplemented in TypeScript.

Emits two run files in the shape `dev/source/eval_retrieval.py` writes, so
`_s213_eval_metrics.py --run <file>` reads either side unchanged.

ROUTE HEALTH IS PART OF THE VERDICT, NOT A FOOTNOTE
  `searchChannelB` swallows a failing routed RPC in a bare `catch {}` and keeps the
  legacy results. So `after == before` has two very different causes:
    - `routed`        the RPC ran, returned, and the flag genuinely changed nothing
    - `silent-fallback` every RPC attempt failed; the flag did nothing because it
                      could not run, and the user paid the latency for nothing
  Counting the second as evidence of a safe flag is the false pass this file exists
  to prevent. `partial` (failed, then succeeded on retry) is reported separately
  because it is a latency problem, not a correctness one.

READ-ONLY. Writes only its two run files and its report to stdout.

USAGE
  python3 dev/_s219_score_before_after.py --self-test
  python3 dev/_s219_score_before_after.py \
      --raw dev/source/eval_runs/2026-09-08_s219_route_first_before_after.jsonl \
      --gold dev/_s213_gold_all.json --out-dir dev/source/eval_runs
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_run_gold import score_item  # noqa: E402


def route_state(calls: list[dict]) -> str:
    """Classify one side's routed-RPC attempts. See module docstring."""
    if not calls:
        return "no-route"
    ok = sum(1 for c in calls if c.get("status") == 200)
    if ok == len(calls):
        return "routed"
    if ok:
        return "partial"
    return "silent-fallback"


def build_row(item: dict, side: dict, gold_item: dict) -> dict:
    """One run-file row, same keys `_s213_run_gold` writes."""
    if side.get("error"):
        return {"id": item["id"], "query": item["query"], "error": side["error"]}
    results = side.get("results") or []
    sc = score_item(gold_item, results)
    return {
        "id": item["id"],
        "query": item["query"],
        "note": gold_item.get("intent"),
        "expect_any": gold_item["expected_source_any"],
        "expect_text_any": gold_item.get("expected_passage_signature") or [],
        "source_ids": [r.get("source_id") for r in results],
        "chunk_ids": [r.get("id") for r in results],
        "scores": [round(float(r.get("score", 0)), 4) for r in results],
        "content_types": [r.get("content_type") for r in results],
        "pages": [r.get("page") for r in results],
        "total": side.get("total", len(results)),
        **sc,
    }


def verdict_of(row: dict) -> str:
    return "ERROR" if row.get("error") else row["verdict"]


def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    check("無 routed 呼叫 = 該題根本沒有路由，flag 無從生效",
          route_state([]) == "no-route")
    check("全部 200 = 旗標真的跑過",
          route_state([{"status": 200}, {"status": 200}]) == "routed")
    check("全部失敗 = 靜默退回，不可當作『改動無害』",
          route_state([{"status": 500}, {"status": 500}]) == "silent-fallback")
    check("先敗後成 = 延遲問題，不是正確性問題",
          route_state([{"status": 500}, {"status": 200}]) == "partial")

    gold_item = {"answerable": True, "expected_source_any": ["b"],
                 "expected_passage_signature": ["目標"], "forbidden_evidence": []}
    row = build_row({"id": "x", "query": "q"},
                    {"results": [{"source_id": "b", "text": "目標段落", "score": 0.8,
                                  "id": "c1"}], "total": 1},
                    gold_item)
    check("判分沿用 _s213_run_gold.score_item", row["verdict"] == "PASS")
    check("side 帶 error 時原樣保留，不當作 FAIL",
          verdict_of(build_row({"id": "x", "query": "q"}, {"error": "boom"},
                               gold_item)) == "ERROR")
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path)
    ap.add_argument("--gold", type=Path, default=Path("dev/_s213_gold_all.json"))
    ap.add_argument("--out-dir", type=Path, default=Path("dev/source/eval_runs"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.raw:
        ap.error("--raw is required")

    gold = {g["id"]: g for g in json.loads(args.gold.read_text(encoding="utf-8"))}
    rows = {"before": [], "after": []}
    route = Counter()
    per_item: list[tuple[str, str, str, str]] = []

    for line in args.raw.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        g = gold[item["id"]]
        built = {}
        for side in ("before", "after"):
            built[side] = build_row(item, item.get(side) or {}, g)
            rows[side].append(built[side])
        state = route_state(item.get("after_routed_calls") or [])
        route[state] += 1
        per_item.append((item["id"], verdict_of(built["before"]),
                         verdict_of(built["after"]), state))

    stem = args.raw.stem.replace("_before_after", "")
    written = []
    for side in ("before", "after"):
        out = args.out_dir / f"{stem}_{side}.json"
        out.write_text(json.dumps({
            "label": f"S219 route-first {side} (in-process, FEATURE_ROUTE_FIRST_SEARCH="
                     f"{'1' if side == 'after' else '0'})",
            "endpoint": "in-process searchChannelB", "top_k": 8,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "gold_file": str(args.gold), "gold_count": len(rows[side]),
            "tie_aliases": [["g24", "sag_2025_11"]],
            "summary": {
                "queries": len(rows[side]),
                "errors": sum(1 for r in rows[side] if r.get("error")),
                "PASS": sum(1 for r in rows[side] if r.get("verdict") == "PASS"),
                "FAIL": sum(1 for r in rows[side] if r.get("verdict") == "FAIL"),
            },
            "results": rows[side],
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        written.append(out)

    print("=== 路由健康度（after 側）===")
    for k in ("routed", "partial", "silent-fallback", "no-route"):
        if route[k]:
            print(f"  {k:<17} {route[k]:>4}")

    print("\n=== verdict 遷移（before → after）===")
    mig = Counter((b, a) for _, b, a, _ in per_item)
    for (b, a), c in sorted(mig.items(), key=lambda x: -x[1]):
        print(f"  {b:<12} → {a:<12} {c:>4}{'' if b == a else '   ← 變'}")

    changed = [(i, b, a, s) for i, b, a, s in per_item if b != a]
    print(f"\n=== 逐條 verdict 改變（{len(changed)} 條）===")
    for i, b, a, s in changed:
        worse = (b == "PASS" and a != "PASS")
        print(f"  {'🔴' if worse else '🟢'} {i:<34} {b:<11} → {a:<11} [{s}]")
    if not changed:
        print("  （無）")

    for out in written:
        print(f"\n寫入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
