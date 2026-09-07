#!/usr/bin/env python3
"""_s213_eval_metrics.py — turn a retrieval run into accuracy metrics.

The existing harness answers ONE question: "did a change move anything?" It
scores a query PASS when any expected source_id appears ANYWHERE in the returned
window, so PASS at rank 7 and PASS at rank 0 are the same result, and 37 of the
39 queries assert nothing about which PASSAGE came back. That is a regression
detector, and it is a good one — but a regression detector cannot be read as an
accuracy measure, and this module exists so the two are never conflated again.

What this adds, none of which the old harness can express:
  - Source Recall@1/3/5/8 and Chunk Recall@1/3/5 — rank actually matters
  - MRR over both layers
  - occupancy: how much of the window one source, or one repeated text, ate
  - no-answer scoring: a confident irrelevant answer is a FAILURE, not a blank
  - per-domain, and dev vs held-out, reported separately

Duplicate and page facts are recovered by joining the run's `chunk_ids` against
the corpus snapshot, because `wiki_chunks` HAS NO page column — the page a user
sees is derived from `=== Page N ===` markers at query time (see
`_s213_corpus.dominant_page`, a line-by-line port of the backend).

READ-ONLY. Consumes run JSON + corpus cache; writes nothing but its report.

USAGE
  python3 dev/_s213_eval_metrics.py --self-test
  python3 dev/_s213_eval_metrics.py --run dev/source/eval_runs/<run>.json
  python3 dev/_s213_eval_metrics.py --run <run> --gold dev/_s213_gold_all.json
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _s213_corpus import DEFAULT_CACHE, dominant_page, load, squeeze  # noqa: E402

K_SOURCE = (1, 3, 5, 8)
K_CHUNK = (1, 3, 5)


# ---------------------------------------------------------------------------
# pure metric helpers — every one is exercised by --self-test
# ---------------------------------------------------------------------------

def recall_at(ranks: list[int | None], k: int) -> float:
    """Share of scored queries whose expected item landed in the top k.

    `None` means "not found anywhere in the window" and counts as a miss, never
    as an exclusion — dropping unfound queries from the denominator is how a
    recall number flatters itself.
    """
    if not ranks:
        return float("nan")
    return sum(1 for r in ranks if r is not None and r < k) / len(ranks)


def mrr(ranks: list[int | None]) -> float:
    if not ranks:
        return float("nan")
    return sum(0.0 if r is None else 1.0 / (r + 1) for r in ranks) / len(ranks)


def max_same_source(source_ids: list[str], tie_map: dict[str, str]) -> int:
    """Largest number of window slots taken by one document.

    Tie aliases collapse first: `g24` and `sag_2025_11` are the same document
    ingested twice, so counting them separately would report the duplicate as
    healthy diversity — the exact error this metric exists to catch.
    """
    if not source_ids:
        return 0
    canon = [tie_map.get(s, s) for s in source_ids]
    return collections.Counter(canon).most_common(1)[0][1]


def duplicate_slots(texts: list[str]) -> int:
    """Window slots that are byte-identical repeats of an earlier slot."""
    seen, dup = set(), 0
    for t in texts:
        key = squeeze(t)
        if not key:
            continue
        if key in seen:
            dup += 1
        else:
            seen.add(key)
    return dup


def no_answer_outcome(scores: list[float], threshold: float) -> str:
    """A no-answer query is only correct when the system declines.

    Returning nothing is CORRECT_ABSTAIN. Returning something weak is
    WEAK_ANSWER — visible to a user but hedged. Returning something strong is
    CONFIDENT_WRONG, the failure mode that matters: the user has no way to tell
    it apart from a real answer.
    """
    if not scores:
        return "CORRECT_ABSTAIN"
    return "CONFIDENT_WRONG" if max(scores) >= threshold else "WEAK_ANSWER"


# ---------------------------------------------------------------------------

def build_index(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows}


def analyse(run: dict, corpus: dict[str, dict], gold: list[dict] | None,
            abstain_threshold: float) -> dict:
    tie_map: dict[str, str] = {}
    for group in run.get("tie_aliases") or []:
        for member in group[1:]:
            tie_map[member] = group[0]

    gold_by_id = {g["id"]: g for g in (gold or [])}
    per_query, s_ranks, c_ranks = [], [], []
    na_outcomes: list[str] = []
    by_domain: dict[str, list[int | None]] = collections.defaultdict(list)
    by_split: dict[str, list[int | None]] = collections.defaultdict(list)

    for r in run.get("results", []):
        if r.get("error"):
            per_query.append({"id": r["id"], "error": r["error"]})
            continue
        g = gold_by_id.get(r["id"])
        sids = r.get("source_ids", [])
        cids = r.get("chunk_ids", [])
        texts = [(corpus.get(c) or {}).get("text", "") for c in cids]
        pages = [dominant_page(t) for t in texts]

        srank = r.get("rank_of_expected")
        crank = r.get("rank_of_expected_chunk")
        answerable = True if g is None else bool(g.get("answerable", True))

        if not answerable:
            outcome = no_answer_outcome(r.get("scores") or [], abstain_threshold)
            na_outcomes.append(outcome)
        else:
            outcome = None
            if r.get("expect_any"):
                s_ranks.append(srank)
                if g:
                    by_domain[g.get("domain", "?")].append(srank)
                    by_split[g.get("split", "dev")].append(srank)
            if r.get("expect_text_any"):
                c_ranks.append(crank)

        per_query.append({
            "id": r["id"], "query": r.get("query"),
            "domain": (g or {}).get("domain"),
            "split": (g or {}).get("split"),
            "answerable": answerable,
            "source_rank": srank, "chunk_rank": crank,
            "asserts_source": bool(r.get("expect_any")),
            "asserts_chunk": bool(r.get("expect_text_any")),
            "top_source": sids[0] if sids else None,
            "top_score": (r.get("scores") or [None])[0],
            "expected_page": (g or {}).get("expected_page"),
            "page_at_expected_rank": pages[srank] if (srank is not None and srank < len(pages)) else None,
            "pages": pages,
            "max_same_source": max_same_source(sids, tie_map),
            "duplicate_slots": duplicate_slots(texts),
            "no_answer_outcome": outcome,
            # A source the gold entry names as wrong-to-cite, cited anyway. This
            # is scored separately from recall on purpose: an item can find the
            # right passage AND still put a mislabelled or retired document in
            # front of the user, and averaging the two would hide it.
            "forbidden_hits": r.get("forbidden_hits") or [],
            "window": len(sids),
        })

    return {
        "meta": {k: run.get(k) for k in ("label", "endpoint", "top_k", "generated_at")},
        "counts": {
            "queries": len(run.get("results", [])),
            "scored_source": len(s_ranks), "scored_chunk": len(c_ranks),
            "no_answer": len(na_outcomes),
            "unasserted": sum(1 for q in per_query
                              if not q.get("error") and not q.get("asserts_source")
                              and q.get("answerable")),
        },
        "source_recall": {f"@{k}": recall_at(s_ranks, k) for k in K_SOURCE},
        "chunk_recall": {f"@{k}": recall_at(c_ranks, k) for k in K_CHUNK},
        "mrr": {"source": mrr(s_ranks), "chunk": mrr(c_ranks)},
        "no_answer": dict(collections.Counter(na_outcomes)),
        "forbidden": {
            "queries_citing_forbidden":
                sum(1 for q in per_query if q.get("forbidden_hits")),
            "offending_sources": sorted({s for q in per_query
                                         for s in (q.get("forbidden_hits") or [])}),
        },
        "occupancy": {
            "queries_with_duplicate_slots":
                sum(1 for q in per_query if q.get("duplicate_slots")),
            "duplicate_slots_total":
                sum(q.get("duplicate_slots") or 0 for q in per_query),
            "max_same_source_seen":
                max((q.get("max_same_source") or 0 for q in per_query), default=0),
            "queries_one_source_ge_half":
                sum(1 for q in per_query
                    if q.get("window") and (q.get("max_same_source") or 0) * 2 >= q["window"]),
        },
        "by_domain": {d: {"n": len(v), **{f"recall@{k}": recall_at(v, k) for k in (1, 5)}}
                      for d, v in sorted(by_domain.items())},
        "by_split": {s: {"n": len(v), **{f"recall@{k}": recall_at(v, k) for k in (1, 5)}}
                     for s, v in sorted(by_split.items())},
        "per_query": per_query,
    }


# ---------------------------------------------------------------------------

def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    # --- these are the six failures Phase 1 requires the harness to be able to show ---
    check("① 來源在窗內但正確段落不在前五 → chunk recall@5 為 0，而 source recall 滿分",
          recall_at([0, 0, 0], 5) == 1.0 and recall_at([6, 7, None], 5) == 0.0)
    check("② 正確來源被同來源不相關 chunk 佔位 → max_same_source 偵測得到",
          max_same_source(["a", "a", "a", "a", "b"], {}) == 4)
    check("②b tie alias 摺疊後才計，否則重複登記會偽裝成多樣性",
          max_same_source(["g24", "sag_2025_11", "x"], {"sag_2025_11": "g24"}) == 2)
    check("③ 完全重複 chunk 佔滿結果 → duplicate_slots 數得到",
          duplicate_slots(["同一段", "同 一 段", "別的", "同一段"]) == 2)
    check("④ 無答案題返回高信心不相關段落 → CONFIDENT_WRONG",
          no_answer_outcome([0.81, 0.4], 0.75) == "CONFIDENT_WRONG")
    check("④b 無答案題正確棄權 → CORRECT_ABSTAIN",
          no_answer_outcome([], 0.75) == "CORRECT_ABSTAIN")
    check("④c 無答案題低分作答 → WEAK_ANSWER（與棄權不可混為一談）",
          no_answer_outcome([0.5], 0.75) == "WEAK_ANSWER")
    check("⑤ 找不到者計入分母，不得剔走（否則 recall 自我美化）",
          recall_at([0, None, None], 1) == 1 / 3)
    check("⑤b MRR 對 None 給 0 分而非跳過",
          abs(mrr([0, None]) - 0.5) < 1e-9)

    # --- the guard that stops a green run from meaning nothing ---
    run = {"results": [{"id": "x", "query": "q", "expect_any": ["a"],
                        "rank_of_expected": 0, "source_ids": ["a"],
                        "chunk_ids": ["c1"], "scores": [0.9],
                        "expect_text_any": []}]}
    out = analyse(run, {"c1": {"text": "t"}}, None, 0.75)
    check("⑥ 評測檔缺 chunk assertion 時，chunk recall 為 NaN 不是 1.0（不可顯示為綠）",
          out["chunk_recall"]["@5"] != out["chunk_recall"]["@5"])  # NaN != NaN
    check("⑥b 未斷言的查詢被獨立計數，不能混入分母",
          out["counts"]["scored_chunk"] == 0)

    # --- prove the page port is wired in, not just present ---
    run2 = {"results": [{"id": "p", "query": "q", "expect_any": ["a"],
                         "rank_of_expected": 0, "source_ids": ["a"],
                         "chunk_ids": ["c9"], "scores": [0.9], "expect_text_any": []}]}
    out2 = analyse(run2, {"c9": {"text": "=== Page 7 ===" + "字" * 50}}, None, 0.75)
    check("⑦ 頁碼由 chunk 正文推導（=== Page 7 === → 7）",
          out2["per_query"][0]["page_at_expected_rank"] == 7)

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path)
    ap.add_argument("--gold", type=Path)
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--abstain-threshold", type=float, default=0.75)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.run:
        ap.error("--run is required")

    corpus = {r["id"]: r for r in load(args.cache)}
    gold = json.loads(args.gold.read_text(encoding="utf-8")) if args.gold else None
    report = analyse(json.loads(args.run.read_text(encoding="utf-8")),
                     corpus, gold, args.abstain_threshold)

    m, c = report["meta"], report["counts"]
    print(f"{m['label']}  |  top_k={m['top_k']}  |  {m['generated_at']}")
    print(f"查詢 {c['queries']}：有來源斷言 {c['scored_source']}、"
          f"有片段斷言 {c['scored_chunk']}、無答案題 {c['no_answer']}、"
          f"完全無斷言 {c['unasserted']}")
    fmt = lambda v: "n/a" if v != v else f"{v:.3f}"          # noqa: E731
    print("\nSource Recall  " + "  ".join(f"{k}={fmt(v)}" for k, v in report["source_recall"].items()))
    print("Chunk  Recall  " + "  ".join(f"{k}={fmt(v)}" for k, v in report["chunk_recall"].items()))
    print(f"MRR            source={fmt(report['mrr']['source'])}  chunk={fmt(report['mrr']['chunk'])}")
    o = report["occupancy"]
    print(f"\n佔位          單一來源最多佔 {o['max_same_source_seen']} 格；"
          f"一源佔半數或以上的查詢 {o['queries_one_source_ge_half']}；"
          f"逐字重複格位 {o['duplicate_slots_total']} 個"
          f"（涉及 {o['queries_with_duplicate_slots']} 條查詢）")
    if report["no_answer"]:
        print(f"無答案題      {report['no_answer']}")
    fb = report["forbidden"]
    print(f"禁引違規      {fb['queries_citing_forbidden']} 條查詢引用了明令不可引用的來源"
          + (f"：{fb['offending_sources']}" if fb["offending_sources"] else ""))
    if report["by_domain"]:
        print("\n分範疇 (n, recall@1, recall@5)")
        for d, v in report["by_domain"].items():
            print(f"  {d:<22}{v['n']:>4}  {fmt(v['recall@1'])}  {fmt(v['recall@5'])}")
    if report["by_split"]:
        print("\n分 split")
        for s, v in report["by_split"].items():
            print(f"  {s:<22}{v['n']:>4}  {fmt(v['recall@1'])}  {fmt(v['recall@5'])}")
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n報告已寫入 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
