#!/usr/bin/env python3
"""_s214_gate2a1_replay.py — offline CURRENT-vs-PROPOSED replay for Gate 2A1.

Reuses `dev/_s214_rank_model.py` (merge_current, merge_proposed) against saved
production run artifacts. Computes ONLY metrics that are actually derivable
from what each artifact recorded; anything not derivable is reported as
NOT_COMPUTABLE rather than inferred, per the Gate 2A1 instruction to "report
exactly which metrics are genuinely computable ... rather than inferring."

Two artifact families, two different replay paths:

  PARALLEL-ARRAY runs (184-item `..._gold_expanded_resolved.json`, and the
  162-item S213 baseline for cross-reference): each row is
  source_ids[]/chunk_ids[]/scores[]/content_types[]/pages[], all same length.
  This is the eval_retrieval.py / _s213_run_gold.py output shape. FULLY
  COMPUTABLE here: Source Recall@k, Chunk Recall@k (by chunk_id identity — the
  file has no raw chunk text, so re-verifying a text signature after reordering
  is not possible; identity of the already-verified expected chunk_id is used
  instead, which is exact, not an approximation), both MRRs, forbidden
  exposure. `acceptable_alternatives` is read from the gold label file
  (`dev/_s213_gold_all.json`, extended in place to 184 items) rather than
  approximated, because 26/184 items actually carry one.

  NESTED-`results` runs (`..._user_nine_questions.json`,
  `..._user_nine_atomic_followups.json`): each row has a `results: [...]` list
  of chunk dicts. These carry no gold labels at all (they are live production
  probes, not eval-harness runs), so Source/Chunk Recall against an "expected"
  source cannot be computed — there is no `expect_any` to check against. What
  IS computable is STRUCTURAL: window membership, forced-lead position, and
  whether the CURRENT model reproduces the recorded order (fidelity, already
  covered by `_s214_rank_model.py --fidelity`). This script reports the
  structural delta (Codex Gate 1 items: index of exact-1.0 matches, footnote
  lead positions, forbidden-source positions) for these two files, and
  explicitly labels Source/Chunk Recall as NOT_COMPUTABLE for them.

READ-ONLY. No network, no clock, no Supabase, no writes outside the report
file this script is asked to produce (it prints; callers redirect to save it).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _s214_rank_model as rm  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Parallel-array runs (184-item, 162-item)
# ---------------------------------------------------------------------------

def parallel_row_to_cands(row: dict) -> list[rm.Cand]:
    """Adapt one parallel-array row into Cand objects `_s214_rank_model` can
    merge. `origin`/`required` are recovered the same way
    `classify_recorded` does for the nested format: forced footnote leads are
    the leading run of `footnote_curated` (max 2), establishment rows score
    exactly 1, spotlight is a `SPOTLIGHT_SOURCE_IDS` member sitting directly
    after the forced leads.
    """
    n = len(row["source_ids"])
    rows_as_dicts = [
        {"id": row["chunk_ids"][i], "source_id": row["source_ids"][i],
         "content_type": row["content_types"][i], "score": row["scores"][i]}
        for i in range(n)
    ]
    cls = rm.classify_recorded(rows_as_dicts, rm.SPOTLIGHT_SOURCE_IDS)
    return rm.rows_to_cands(rows_as_dicts, cls)


def source_rank(sids: list[str], expected: list[str], alternatives: list[str]) -> int | None:
    ok = set(expected) | set(alternatives or [])
    for i, s in enumerate(sids):
        if s in ok:
            return i
    return None


def chunk_rank(cids: list[str], truth_chunk: str | None) -> int | None:
    if not truth_chunk:
        return None
    for i, c in enumerate(cids):
        if c == truth_chunk:
            return i
    return None


def recall_at(ranks: list[int | None], k: int) -> float:
    n = len(ranks)
    if n == 0:
        return float("nan")
    return sum(1 for r in ranks if r is not None and r < k) / n


def mrr(ranks: list[int | None]) -> float:
    n = len(ranks)
    if n == 0:
        return float("nan")
    return sum(1 / (r + 1) for r in ranks if r is not None) / n


LABELS = ("current", "broad_score_sort", "exact_only")


def build_variant(label: str, cands: list) -> list:
    kwargs = dict(
        main=[c for c in cands if c.origin == rm.MAIN],
        footnotes=[c for c in cands if c.origin == rm.FOOTNOTE],
        footnote_lead_ids={c.id for c in cands if c.origin == rm.FOOTNOTE and c.required},
        spotlight=[c for c in cands if c.origin == rm.SPOTLIGHT],
        establishment=[c for c in cands if c.origin == rm.ESTABLISHMENT],
        top_k=len(cands),
    )
    if label == "current":
        return rm.merge_current(**kwargs)
    if label == "exact_only":
        return rm.merge_exact_only(**kwargs)
    if label == "broad_score_sort":
        # merge_proposed takes the flat candidate list directly (Gate 1's
        # rejected full-window score-sort design), not the (main, footnotes,
        # ...) split the other two variants take.
        return rm.merge_proposed(cands, top_k=len(cands))
    raise ValueError(label)


def replay_parallel(run_path: str, gold_path: str) -> dict:
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    gold = {g["id"]: g for g in json.loads(Path(gold_path).read_text(encoding="utf-8"))}

    fidelity_ok = fidelity_bad = 0
    fidelity_mismatches = []
    src_ranks = {label: [] for label in LABELS}
    chunk_ranks = {label: [] for label in LABELS}
    fb1 = {label: 0 for label in LABELS}
    fbtop3 = {label: 0 for label in LABELS}
    n_answerable = 0
    n_total = 0
    exact_established = []  # (id, {label: index}) for score==1 rows
    per_query = []  # (id, {label: source_rank}) for every answerable, scored query

    for row in run["results"]:
        n_total += 1
        g = gold.get(row["id"])
        if g is None:
            continue  # no gold label for this id; cannot score, but still fidelity-checkable
        cands = parallel_row_to_cands(row)
        variants = {label: build_variant(label, cands) for label in LABELS}
        cur = variants["current"]

        # Fidelity: does CURRENT reproduce the actually-recorded order?
        if [c.id for c in cur] == [c.id for c in cands]:
            fidelity_ok += 1
        else:
            fidelity_bad += 1
            fidelity_mismatches.append({
                "id": row["id"], "recorded": [c.id for c in cands],
                "model": [c.id for c in cur],
            })

        est = [c for c in cands if c.score >= 0.999]
        if est:
            ix = {label: min((variants[label].index(c) for c in est
                             if c in variants[label]), default=999)
                  for label in LABELS}
            exact_established.append((row["id"], ix))

        if not g.get("answerable", True):
            continue
        n_answerable += 1
        expected = g["expected_source_any"]
        alt = g.get("acceptable_alternatives") or []
        truth_chunk = (row["chunk_ids"][row["rank_of_expected_chunk"]]
                       if row.get("rank_of_expected_chunk") is not None else None)
        row_ranks = {}
        for label in LABELS:
            ordered = variants[label]
            sids = [c.source_id for c in ordered]
            cids = [c.id for c in ordered]
            sr = source_rank(sids, expected, alt)
            src_ranks[label].append(sr)
            chunk_ranks[label].append(chunk_rank(cids, truth_chunk))
            row_ranks[label] = sr
            forb = set(row.get("forbidden_hits") or [])
            if forb:
                pos = [i for i, s in enumerate(sids) if s in forb]
                if pos and min(pos) == 0:
                    fb1[label] += 1
                if pos and min(pos) < 3:
                    fbtop3[label] += 1
        per_query.append({"id": row["id"], "source_rank": row_ranks})

    metrics = {}
    for label in LABELS:
        metrics[label] = {
            "source_recall@1": recall_at(src_ranks[label], 1),
            "source_recall@3": recall_at(src_ranks[label], 3),
            "source_recall@5": recall_at(src_ranks[label], 5),
            "source_recall@8": recall_at(src_ranks[label], 8),
            "source_mrr": mrr(src_ranks[label]),
            "chunk_recall@1": recall_at(chunk_ranks[label], 1),
            "chunk_recall@3": recall_at(chunk_ranks[label], 3),
            "chunk_recall@5": recall_at(chunk_ranks[label], 5),
            "chunk_mrr": mrr(chunk_ranks[label]),
            "forbidden@1": fb1[label],
            "forbidden@top3": fbtop3[label],
        }

    def delta_summary(label: str) -> dict:
        fixed = sum(1 for _, ix in exact_established if ix[label] < ix["current"])
        same = sum(1 for _, ix in exact_established if ix[label] == ix["current"])
        worse = sum(1 for _, ix in exact_established if ix[label] > ix["current"])
        return {"moved_to_lower_index": fixed, "unchanged_index": same,
                "moved_to_higher_index": worse}

    # Named-query regression check (Codex Gate 2A1b): does a variant push a
    # gold-answer source's rank WORSE than CURRENT for any of the 7 footnote
    # answers Codex identified as demoted by broad_score_sort?
    named = ["hr_lsp", "hr_severance", "fin_ac_grant", "gov_imc_60pct",
             "gov_imc_pta", "gov_coa_imc", "kg_subsidy_eligibility"]
    named_regressions = {}
    by_id = {pq["id"]: pq["source_rank"] for pq in per_query}
    for qid in named:
        if qid not in by_id:
            named_regressions[qid] = "NOT_IN_184_SET"
            continue
        r = by_id[qid]
        named_regressions[qid] = {
            "current": r["current"], "broad_score_sort": r["broad_score_sort"],
            "exact_only": r["exact_only"],
            "broad_score_sort_worse_than_current": (
                r["broad_score_sort"] is None or
                (r["current"] is not None and r["broad_score_sort"] > r["current"])),
            "exact_only_worse_than_current": (
                r["exact_only"] is None or
                (r["current"] is not None and r["exact_only"] > r["current"])),
        }

    return {
        "run_path": run_path,
        "gold_path": gold_path,
        "n_rows_total": n_total,
        "n_rows_with_gold": fidelity_ok + fidelity_bad,
        "n_answerable_scored": n_answerable,
        "fidelity": {"reproduced": fidelity_ok, "mismatched": fidelity_bad,
                     "mismatches": fidelity_mismatches},
        "exact_score1_rows": len(exact_established),
        "exact_score1_summary": {label: delta_summary(label) for label in LABELS
                                 if label != "current"},
        "exact_score1_detail": [{"id": qid, **ix} for qid, ix in exact_established],
        "metrics": metrics,
        "named_regression_check": named_regressions,
    }


# ---------------------------------------------------------------------------
# Nested-`results` runs (no gold labels — structural comparison only)
# ---------------------------------------------------------------------------

def replay_nested(run_path: str) -> dict:
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    per_query = []
    skipped = 0
    for q in run["results"]:
        rows = q.get("results") or []
        if not rows or any(r.get("content_type") is None for r in rows):
            skipped += 1
            per_query.append({"id": q.get("id"), "computable": False,
                              "reason": "content_type missing from this artifact's schema "
                                        "— footnote vs vault_extract vs establishment cannot "
                                        "be told apart, so overlay roles cannot be recovered"})
            continue
        cls = rm.classify_recorded(rows, rm.SPOTLIGHT_SOURCE_IDS)
        cands = rm.rows_to_cands(rows, cls)
        cur = rm.merge_current(
            main=[c for c in cands if c.origin == rm.MAIN],
            footnotes=[c for c in cands if c.origin == rm.FOOTNOTE],
            footnote_lead_ids={c.id for c in cands
                               if c.origin == rm.FOOTNOTE and c.required},
            spotlight=[c for c in cands if c.origin == rm.SPOTLIGHT],
            establishment=[c for c in cands if c.origin == rm.ESTABLISHMENT],
            top_k=len(cands))
        prop = rm.merge_proposed(cands, top_k=len(cands))
        exact = rm.merge_exact_only(
            main=[c for c in cands if c.origin == rm.MAIN],
            footnotes=[c for c in cands if c.origin == rm.FOOTNOTE],
            footnote_lead_ids={c.id for c in cands
                               if c.origin == rm.FOOTNOTE and c.required},
            spotlight=[c for c in cands if c.origin == rm.SPOTLIGHT],
            establishment=[c for c in cands if c.origin == rm.ESTABLISHMENT],
            top_k=len(cands))
        reproduced = [c.id for c in cur] == [c.id for c in cands]
        est = [c for c in cands if c.score >= 0.999]
        per_query.append({
            "id": q.get("id"),
            "computable": True,
            "current_reproduces_recorded": reproduced,
            "current_order": [c.id for c in cur],
            "broad_score_sort_order": [c.id for c in prop],
            "exact_only_order": [c.id for c in exact],
            "exact_score1_index_current": (min(cur.index(c) for c in est)
                                           if est else None),
            "exact_score1_index_broad_score_sort": (min(prop.index(c) for c in est)
                                                    if est else None),
            "exact_score1_index_exact_only": (min(exact.index(c) for c in est)
                                              if est else None),
        })
    return {
        "run_path": run_path,
        "n_queries": len(run["results"]),
        "n_skipped_no_content_type": skipped,
        "n_computable": len(run["results"]) - skipped,
        "source_recall_note": "NOT_COMPUTABLE — this artifact carries no gold "
                              "expected-source labels (it is a live probe, not "
                              "an eval-harness run)",
        "per_query": per_query,
    }


def establishment_queries_detail(run_path: str) -> list[dict]:
    """Gate 2A1b item: verify the three establishment (score==1) queries
    individually, across all three variants, not just in an aggregate count."""
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    out = []
    for row in run["results"]:
        if not any(s >= 0.999 for s in row["scores"]):
            continue
        cands = parallel_row_to_cands(row)
        variants = {label: build_variant(label, cands) for label in LABELS}
        est_ids = {c.id for c in cands if c.score >= 0.999}
        out.append({
            "id": row["id"],
            "query": row["query"],
            **{f"{label}_establishment_index": min(
                (variants[label].index(c) for c in variants[label] if c.id in est_ids),
                default=None)
               for label in LABELS},
            **{f"{label}_order": [c.id for c in variants[label]] for label in LABELS},
        })
    return out


def main() -> int:
    gold_path = str(REPO_ROOT / "dev" / "_s213_gold_all.json")
    run_184 = str(REPO_ROOT / "dev/source/eval_runs/2026-09-04_s214_gold_expanded_resolved.json")
    out = {
        "label": "S214 Gate 2A1b offline replay — CURRENT vs BROAD-SCORE-SORT (rejected) "
                 "vs EXACT-ONLY",
        "parallel_184": replay_parallel(run_184, gold_path),
        "establishment_queries_individually": establishment_queries_detail(run_184),
        "nested_nine_questions": replay_nested(
            str(REPO_ROOT / "dev/source/eval_runs/2026-09-04_s214_user_nine_questions.json")),
        "nested_atomic_followups": replay_nested(
            str(REPO_ROOT / "dev/source/eval_runs/2026-09-04_s214_user_nine_atomic_followups.json")),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
