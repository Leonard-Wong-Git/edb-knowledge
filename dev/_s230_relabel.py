#!/usr/bin/env python3
"""_s230_relabel.py — re-read the judge-takeover table against the CORRECTED gold labels.

Why this exists. `_s230_bypassCensus.ts` first classified each bypass by testing the gold
passage signature as a RAW substring of the window. The project compares text as
`squeeze(fold(s))` (dev/_s213_corpus.py: NFKC fold, then drop all whitespace), and the raw
test misclassified at least two real hits: `家長校董 點選` carries its answer verbatim in slot 0
but gold writes 家長教師會(PTA) half-width while the chunk has （PTA） full-width, and
`小學 STEAM 教育` has its signature split across a chunk boundary.

That matters because the SOUND / WRONG_PASSAGE split is what the pre-registered ship
conditions are read against. The judge outcomes themselves are per-query facts and do not
depend on the labels, so re-deciding the verdict needs NO new model calls: join the recorded
outcomes onto the corrected labels and re-evaluate.

Usage:
  python3 dev/_s230_relabel.py --self-test
  python3 dev/_s230_relabel.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "source" / "eval_runs"


def verdict(answerable: bool, signature_in_window):
    """Same three-way split as the probe, kept in one place so both agree."""
    if not answerable:
        return "FALSE_BYPASS"
    if signature_in_window is None:
        return "UNKNOWN"
    return "SOUND" if signature_in_window else "WRONG_PASSAGE"


def ship_reading(t: dict) -> dict:
    """The conditions pre-registered in dev/SESSION_HANDOFF.md before the judge batch ran."""
    fb, sound, wrong = t["FALSE_BYPASS"], t["SOUND"], t["WRONG_PASSAGE"]
    blocked_sound = sound["JUDGE_ANSWERS"] + sound["JUDGE_DECLINES"]
    return {
        "false_bypass_declines": fb["JUDGE_DECLINES"],
        "false_bypass_declines_meets_>=4": fb["JUDGE_DECLINES"] >= 4,
        "blocked_sound": blocked_sound,
        "blocked_sound_still_answered": sound["JUDGE_ANSWERS"],
        "sound_answered_meets_>=6": sound["JUDGE_ANSWERS"] >= 6,
        "stop_sound_declines_>=2": sound["JUDGE_DECLINES"] >= 2,
        "stop_false_bypass_answered_>=2": fb["JUDGE_ANSWERS"] >= 2,
        "warn_wrong_passage_declines_>=30": wrong["JUDGE_DECLINES"] >= 30,
    }


def selftest() -> int:
    fails = 0

    def ok(name, cond):
        nonlocal fails
        if not cond:
            fails += 1
            print(f"  FAIL {name}")
        else:
            print(f"  ok   {name}")

    ok("unanswerable is FALSE_BYPASS", verdict(False, True) == "FALSE_BYPASS")
    ok("signature present is SOUND", verdict(True, True) == "SOUND")
    ok("signature absent is WRONG_PASSAGE", verdict(True, False) == "WRONG_PASSAGE")
    ok("no signature to test is UNKNOWN", verdict(True, None) == "UNKNOWN")

    base = {
        "FALSE_BYPASS": {"JUDGE_DECLINES": 4, "JUDGE_ANSWERS": 1},
        "SOUND": {"JUDGE_DECLINES": 0, "JUDGE_ANSWERS": 7},
        "WRONG_PASSAGE": {"JUDGE_DECLINES": 10, "JUDGE_ANSWERS": 31},
    }
    r = ship_reading(base)
    ok("the recorded run meets both ship conditions",
       r["false_bypass_declines_meets_>=4"] and r["sound_answered_meets_>=6"])
    ok("no stop condition on the recorded run",
       not r["stop_sound_declines_>=2"] and not r["stop_false_bypass_answered_>=2"])
    # RED-TEST ASSERTION — relabelling can only move rows INTO SOUND, and two SOUND declines
    # is the pre-registered stop. If this ever reads False the gate has stopped being a gate.
    moved = {**base, "SOUND": {"JUDGE_DECLINES": 2, "JUDGE_ANSWERS": 7}}
    ok("two SOUND declines trips the stop condition", ship_reading(moved)["stop_sound_declines_>=2"])

    print("\nALL PASS" if fails == 0 else f"\n{fails} FAILED")
    return 0 if fails == 0 else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return selftest()

    old = json.loads((RUNS / "2026-09-22_s230_bypass_census.json").read_text("utf-8"))
    new = json.loads((RUNS / "2026-09-22_s230_bypass_census_nfkc.json").read_text("utf-8"))
    take = json.loads((RUNS / "2026-09-22_s230_judge_takeover.json").read_text("utf-8"))

    new_by_id = {r["id"]: r for r in new["rows"] if "answerable" in r}
    old_by_id = {r["id"]: r for r in old["rows"] if "answerable" in r}

    moved = []
    for rid, r in new_by_id.items():
        o = old_by_id.get(rid)
        if not o or not o.get("bypass_before"):
            continue
        before = verdict(o["answerable"], o.get("signature_in_window"))
        after = verdict(r["answerable"], r.get("signature_in_window"))
        if before != after:
            moved.append((rid, r["query"], before, after))

    tallies = {v: {"n": 0, "KEEPS_BYPASS": 0, "JUDGE_ANSWERS": 0, "JUDGE_DECLINES": 0, "JUDGE_ERROR": 0}
               for v in ("FALSE_BYPASS", "SOUND", "WRONG_PASSAGE", "UNKNOWN")}
    for row in take["rows"]:
        r = new_by_id.get(row["id"])
        if r is None:
            continue
        v = verdict(r["answerable"], r.get("signature_in_window"))
        tallies[v]["n"] += 1
        tallies[v][row["outcome"]] += 1

    print("=== 標籤改正後移動的條目 ===")
    for rid, q, b, a in moved:
        print(f"  {b} → {a}   {q[:46]}  ({rid})")
    print(f"  合計 {len(moved)} 條移動\n")

    print("=== 判官接手表（標籤已改正，判官結果未變）===")
    for v in ("FALSE_BYPASS", "SOUND", "WRONG_PASSAGE", "UNKNOWN"):
        t = tallies[v]
        if t["n"] == 0:
            continue
        print(f"  {v:14} n={t['n']:2}  保住={t['KEEPS_BYPASS']:2}  判官答={t['JUDGE_ANSWERS']:2}"
              f"  判官拒={t['JUDGE_DECLINES']:2}  error={t['JUDGE_ERROR']}")

    print("\n=== 對照預先定案 ===")
    print(json.dumps(ship_reading(tallies), ensure_ascii=False, indent=2))

    raw_gap = sum(1 for r in new_by_id.values()
                  if r.get("signature_in_window") is True and r.get("signature_in_window_raw_substring") is False)
    print(f"\n原文子字串比對會漏掉的 signature 命中（全 gold）：{raw_gap} 條")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
