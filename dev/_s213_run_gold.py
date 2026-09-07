#!/usr/bin/env python3
"""_s213_run_gold.py — run the S213 gold set against the live Channel B endpoint.

Emits a run file in the same shape `dev/source/eval_retrieval.py` writes, so the
existing `--compare` tooling and `_s213_eval_metrics.py` both read it. What it
adds over the shipped harness, per gold item:

  - `rank_of_expected_chunk` scored by PASSAGE SIGNATURE over the whole window,
    not only the first five, so Chunk Recall@k is answerable at every k
  - NFKC folding on both sides of every text comparison. The shipped
    `chunk_verdict_for` does not fold, and 868 chunks carry CJK compatibility
    ideographs — without folding a correct passage is scored FAIL because 理 is
    U+F9E4 rather than U+7406
  - `forbidden_hits`: sources the item says must NOT be cited, if they appeared
  - `no_answer` items scored on whether the system DECLINES, which the shipped
    harness cannot express at all (an empty `expect_any` is RECORD_ONLY there)

READ-ONLY: POSTs search queries with `synthesize: false`; writes one run file.
Never writes to Supabase and never deploys.

Cost note (discipline #17 — estimate bulk external calls before making them):
one embedding per query, ~20 tokens each, 162 queries ≈ 3.2k tokens on
text-embedding-3-small ≈ US$0.00007. Synthesis is off, so no completion spend.

USAGE
  python3 dev/_s213_run_gold.py --self-test
  python3 dev/_s213_run_gold.py --gold dev/_s213_gold_all.json \
      --out dev/source/eval_runs/2026-09-04_s213_gold_baseline.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "source"))
from _s213_corpus import fold, squeeze                      # noqa: E402
from eval_retrieval import (DEFAULT_ENDPOINT, DEFAULT_PACE_S,  # noqa: E402
                            query_once)


def match_rank(results: list[dict], signatures: list[str]) -> int | None:
    """Rank of the first result whose text carries one of the signatures.

    Scans the WHOLE window (the shipped harness stops at five) and folds both
    sides so a compatibility ideograph matches its unified twin.
    """
    wanted = [squeeze(fold(s)) for s in signatures if s]
    if not wanted:
        return None
    for i, r in enumerate(results):
        hay = squeeze(fold(r.get("text", "")))
        if any(w in hay for w in wanted):
            return i
    return None


def source_rank(sids: list[str], expected: list[str],
                alternatives: list[str]) -> int | None:
    ok = set(expected) | set(alternatives or [])
    for i, s in enumerate(sids):
        if s in ok:
            return i
    return None


def score_item(item: dict, results: list[dict]) -> dict:
    sids = [r.get("source_id") for r in results]
    scores = [float(r.get("score", 0.0)) for r in results]
    forbidden = [s for s in (item.get("forbidden_evidence") or []) if s in sids]

    if not item.get("answerable", True):
        # Declining is the correct behaviour. A high-confidence irrelevant
        # passage is the failure that matters, because the user cannot tell it
        # apart from a real answer.
        return {"verdict": "RECORD_ONLY", "rank_of_expected": None,
                "rank_of_expected_chunk": None, "chunk_verdict": "RECORD_ONLY",
                "forbidden_hits": forbidden,
                "top_score": max(scores) if scores else None}

    srank = source_rank(sids, item["expected_source_any"],
                        item.get("acceptable_alternatives"))
    crank = match_rank(results, item.get("expected_passage_signature") or [])
    return {
        "verdict": "PASS" if srank is not None else "FAIL",
        "rank_of_expected": srank,
        "rank_of_expected_chunk": crank,
        "chunk_verdict": "PASS" if crank is not None else "FAIL",
        "forbidden_hits": forbidden,
        "top_score": max(scores) if scores else None,
    }


def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    res = [{"source_id": "a", "text": "無關", "score": 0.9},
           {"source_id": "b", "text": "目標段落內容", "score": 0.8}]
    item = {"answerable": True, "expected_source_any": ["b"],
            "expected_passage_signature": ["目標段落"], "forbidden_evidence": ["a"]}
    out = score_item(item, res)
    check("來源與片段各自報自己的名次", out["rank_of_expected"] == 1
          and out["rank_of_expected_chunk"] == 1)
    check("forbidden_evidence 出現即記錄", out["forbidden_hits"] == ["a"])

    # the defect the shipped harness has
    compat = [{"source_id": "b", "text": "臨時護理室", "score": 0.9}]
    check("相容碼位（U+F9E4 理）仍然對得上 —— 未 fold 就會誤判 FAIL",
          match_rank(compat, ["臨時護理室"]) == 0)

    check("片段在窗內第 7 位仍找得到（舊 harness 只看前五）",
          match_rank([{"text": "x"}] * 6 + [{"text": "命中內容"}], ["命中內容"]) == 6)
    check("找不到就回 None，不是 0",
          match_rank([{"text": "x"}], ["無此語"]) is None)

    na = score_item({"answerable": False, "expected_source_any": [],
                     "expected_passage_signature": [],
                     "forbidden_evidence": []}, res)
    check("無答案題不判 PASS/FAIL，交由指標層評分",
          na["verdict"] == "RECORD_ONLY" and na["top_score"] == 0.9)
    check("零結果時 top_score 為 None（棄權，不是低分作答）",
          score_item({"answerable": False, "expected_source_any": [],
                      "expected_passage_signature": [],
                      "forbidden_evidence": []}, [])["top_score"] is None)
    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, default=Path("dev/_s213_gold_all.json"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--pace", type=float, default=DEFAULT_PACE_S)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        ap.error("--out is required")

    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    if args.limit:
        gold = gold[:args.limit]
    rows, errors = [], 0
    for i, item in enumerate(gold, 1):
        if i > 1:
            time.sleep(args.pace)
        try:
            resp = query_once(args.endpoint, item["query"], args.top_k)
        except RuntimeError as e:
            print(f"  [{i}/{len(gold)}] {item['id']:<28} ERROR {e}", file=sys.stderr)
            rows.append({"id": item["id"], "query": item["query"], "error": str(e)})
            errors += 1
            continue
        if resp.get("degraded"):
            detail = f"degraded:{resp.get('degraded_kind')} {resp.get('reason')}"
            rows.append({"id": item["id"], "query": item["query"], "error": detail})
            errors += 1
            continue

        results = resp.get("results") or []
        sc = score_item(item, results)
        rows.append({
            "id": item["id"], "query": item["query"], "note": item.get("intent"),
            "expect_any": item["expected_source_any"],
            "expect_text_any": item.get("expected_passage_signature") or [],
            "source_ids": [r.get("source_id") for r in results],
            "chunk_ids": [r.get("id") for r in results],
            "scores": [round(float(r.get("score", 0)), 4) for r in results],
            "content_types": [r.get("content_type") for r in results],
            "pages": [r.get("page") for r in results],
            "total": resp.get("total", len(results)),
            **sc,
        })
        flag = {"PASS": "✅", "FAIL": "❌", "RECORD_ONLY": "·"}[sc["verdict"]]
        warn = " ⚠禁引" if sc["forbidden_hits"] else ""
        print(f"  [{i}/{len(gold)}] {flag} {item['id']:<28} "
              f"src={sc['rank_of_expected']} chunk={sc['rank_of_expected_chunk']}{warn}")

    run = {
        "label": "S213 Phase 1 gold-set run",
        "endpoint": args.endpoint, "top_k": args.top_k,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gold_file": str(args.gold), "gold_count": len(gold),
        "tie_aliases": [["g24", "sag_2025_11"]],
        "summary": {"queries": len(gold), "errors": errors,
                    "PASS": sum(1 for r in rows if r.get("verdict") == "PASS"),
                    "FAIL": sum(1 for r in rows if r.get("verdict") == "FAIL")},
        "results": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(rows)} 條寫入 {args.out}（errors={errors}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
