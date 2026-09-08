#!/usr/bin/env python3
"""_s220_latency_verdict.py — count the production failure rate instead of projecting it.

WHY THIS EXISTS
  S219 measured route-first under the SERVICE key (8s statement_timeout), observed an
  11.1% failure rate, and PROJECTED 26.4% against anon's real 3s ceiling. A projection
  from a different ceiling is an estimate, not a measurement — and the project's own
  discipline (SESSION_HANDOFF Risks 4) is that measuring an 8s system to describe a 3s
  one systematically understates failure.

  `routeFirstGold.ts` now records every RPC call's wall time on BOTH the routed and the
  full-corpus path. A call that took longer than the ceiling would have been cancelled
  with 57014 at that ceiling. So the failure rate can be COUNTED per call, at any
  ceiling, from one run — no second live batch, no extrapolation.

WHAT IT DOES NOT CLAIM
  Simulating a lower ceiling does not reproduce a lower-ceiling run. A query cancelled
  at 3s frees its resources sooner, so a real 3s system is under different load than the
  8s run these timings came from. This gives the failure CLASSIFICATION (which calls
  exceed the ceiling), not a promise about wall-clock under that ceiling.

READ-ONLY. Prints a report; writes nothing.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

CEILINGS = [3000, 8000]


def simulate(side: dict, ceiling: int) -> str:
    """Replay one side's recorded calls against a ceiling. Mirrors searchChannelB:
    routed attempts first (with retry); on exhaustion, fall through to the full search."""
    routed = side.get("routed_calls") or []
    main = side.get("main_calls") or []
    routed_ok = any(c.get("status") == 200 and c.get("ms", 0) <= ceiling for c in routed)
    if routed_ok:
        return "ok-routed"
    main_ok = any(c.get("status") == 200 and c.get("ms", 0) <= ceiling for c in main)
    if main_ok:
        return "ok-main"
    if not routed and not main:
        return "no-call"
    return "FAIL"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()
    rows = [json.loads(l) for l in Path(args.raw).open(encoding="utf-8") if l.strip()]
    print(f"\n  題數：{len(rows)}\n")

    for ceiling in CEILINGS:
        print(f"  ── 上限 {ceiling}ms {'（anon＝生產真實值）' if ceiling == 3000 else '（service key＝本次量度值）'} ──")
        for mode, label in (("before", "flag OFF"), ("after", "flag ON ")):
            verdicts = [simulate({"routed_calls": r.get(f"{mode}_routed_calls"),
                                  "main_calls": r.get(f"{mode}_main_calls")}, ceiling) for r in rows]
            fail = verdicts.count("FAIL")
            pct = 100 * fail / len(rows) if rows else 0
            detail = " ".join(f"{v}={verdicts.count(v)}" for v in ("ok-routed", "ok-main", "no-call", "FAIL"))
            print(f"    {label}  失敗 {fail}/{len(rows)} = {pct:.1f}%   [{detail}]")
        print()

    # call-level shape, both sides
    print("  ── RPC 呼叫層面 ──")
    for mode, label in (("before", "flag OFF"), ("after", "flag ON ")):
        mains = [c for r in rows for c in (r.get(f"{mode}_main_calls") or [])]
        routeds = [c for r in rows for c in (r.get(f"{mode}_routed_calls") or [])]
        def stat(calls, name):
            if not calls:
                print(f"    {label} {name:10s} 0 次")
                return
            ms = sorted(c.get("ms", 0) for c in calls)
            over3 = sum(1 for c in calls if c.get("ms", 0) > 3000)
            e500 = sum(1 for c in calls if c.get("status") not in (200, None))
            print(f"    {label} {name:10s} {len(calls):4d} 次 | 中位 {ms[len(ms)//2]:5d}ms | p90 {ms[int(len(ms)*0.9)]:5d}ms | 最慢 {ms[-1]:6d}ms | >3s {over3:3d} ({100*over3/len(calls):.0f}%) | 非200 {e500}")
        stat(mains, "全庫 RPC")
        stat(routeds, "路由 RPC")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
