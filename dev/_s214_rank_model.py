#!/usr/bin/env python3
"""_s214_rank_model.py — pure model of Channel B overlay ordering (CURRENT and PROPOSED).

WHY THIS IS A PYTHON DEV HARNESS AND NOT A TYPESCRIPT EXTRACTION
---------------------------------------------------------------
Gate 2A1 asked for the smallest pure exportable merge model, extracted from
`backend/src/api/searchChannelB.ts` if a zero-behaviour extraction is safe, and
kept in a dev harness with an explanation if not. It is not safe, for two
reasons that are facts about the repo rather than preferences:

  1. The backend has NO test runner. `backend/package.json` devDependencies are
     exactly `@types/node`, `tsx`, `typescript`; scripts are `dev`, `build`,
     `check` (tsc --noEmit) and one tsx regression script. There is no jest,
     vitest or `node:test` usage anywhere under `backend/src` or
     `backend/scripts`. Landing T1-T14 as TypeScript tests means adding a test
     framework to production `package.json` — a dependency change, which Gate
     2A1 forbids and which is far larger than "the smallest model needed".
  2. The offline replay (Gate 2A1 item 6) reads saved JSON artifacts with the
     existing S213/S214 Python tooling. The model has to be callable from there.

DIVERGENCE RISK, AND HOW IT IS CONTROLLED
-----------------------------------------
A Python model of TypeScript production code can drift from it. That risk is
NOT hand-waved here: `fidelity_rows()` replays the model against real recorded
production output and asserts the CURRENT model reproduces the observed order.
A model that cannot reproduce production is not evidence about production.

When Gate 2B implements this in TypeScript, the TS implementation must be
validated against these same assertions — this file is the specification, not a
throwaway.

READ-ONLY. No network, no clock, no Supabase. Pure functions only.

Usage:
    python3 dev/_s214_rank_model.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path

# Synthesis window (backend/src/api/searchChannelB.ts:951 — `results.slice(0, 5)`).
WINDOW = 5
# backend/src/api/searchChannelB.ts:1193
VAULT_LEAD_SCORE = 0.70
# Overlay identity. `origin` is metadata for tests and overflow priority ONLY;
# it must never appear in a sort key for display order (Gate 1 defect D1).
MAIN, FOOTNOTE, SPOTLIGHT, ESTABLISHMENT = "main", "footnote", "spotlight", "establishment"

# Overflow priority when required members exceed the window (Gate 1 §3).
# Rationale is safety semantics, not taste: a wrong answer outranks a missing one.
#   0 establishment — lexical exact row. S211: picking a different row of the same
#     table produced a confidently WRONG number (12 classes answered as 2 graduate
#     teachers; the row says 5). Losing it reintroduces a measured wrong answer.
#   1 footnote      — hand-curated verbatim answer. S196: 26/26 positives depend on
#     the lead. Losing it makes a known-correct answer disappear.
#   2 spotlight     — reachability of freshly ingested sources. S195: removing it
#     turned 3 queries PASS->FAIL. That is a recall loss, not a wrong answer.
OVERFLOW_RANK = {ESTABLISHMENT: 0, FOOTNOTE: 1, SPOTLIGHT: 2, MAIN: 3}


@dataclass(frozen=True)
class Cand:
    """One candidate chunk. `guarantee` controls WINDOW MEMBERSHIP ONLY."""
    id: str
    score: float
    source_id: str
    content_type: str
    origin: str = MAIN
    required: bool = False

    @property
    def is_stat(self) -> bool:
        return self.content_type == "stat_fact" or self.source_id.startswith("stat_")


def by_score(c: Cand) -> tuple[float, str]:
    """The ONLY display sort key: score descending, then id ascending.

    `id` is not decoration. Without a total order the output is not reproducible
    when two chunks tie, and a non-reproducible ranking cannot be regression
    tested (S213 discipline #20: the instrument must be verified first).
    """
    return (-c.score, c.id)


def stat_filter(cands: list[Cand], include_statistical: bool) -> list[Cand]:
    """searchChannelB.ts:1603-1607."""
    if include_statistical:
        return list(cands)
    return [c for c in cands if not c.is_stat]


# ---------------------------------------------------------------------------
# CURRENT — a faithful model of production as it stands today
# ---------------------------------------------------------------------------

def merge_current(
    main: list[Cand],
    footnotes: list[Cand],
    footnote_lead_ids: set[str],
    spotlight: list[Cand],
    establishment: list[Cand],
    top_k: int = 8,
    include_statistical: bool = False,
) -> list[Cand]:
    """Model of searchChannelB.ts:1489-1496, 1529-1536, 1587-1594, 1603-1611.

    Order of operations is load-bearing and reproduced exactly:
      1. footnote pass  — `[...lead, ...rest]`, rest score-sorted   (:1495)
      2. spotlight pass — inserted AT `forcedLeads`                 (:1530-1534)
      3. establishment  — inserted AT `forcedLeads`                 (:1588-1592)
      4. statistical filter, applied to the WHOLE merged list       (:1603)
      5. slice(0, top_k), explicitly without re-sorting             (:1609-1611)
    """
    lead = [c for c in footnotes if c.id in footnote_lead_ids][:2]
    seen = {c.id for c in lead}
    rest: list[Cand] = []
    # `[...results, ...fnResults]` — main results are seen first, so on an id
    # collision the MAIN copy survives (:1489-1493).
    for c in list(main) + list(footnotes):
        if c.id in seen:
            continue
        seen.add(c.id)
        rest.append(c)
    rest.sort(key=by_score)
    results = lead + rest
    forced = len(lead)

    # Spotlight: only sources not already visible, and not an id already present.
    visible = {c.source_id for c in results}
    seen_ids = {c.id for c in results}
    spot = [c for c in spotlight if c.source_id not in visible and c.id not in seen_ids]
    spot.sort(key=by_score)
    spot = spot[:1]  # SPOTLIGHT_MAX_LEADS
    if spot:
        results = results[:forced] + spot + results[forced:]
        forced += len(spot)

    seen_ids = {c.id for c in results}
    est = [c for c in establishment if c.id not in seen_ids]
    if est:
        results = results[:forced] + est + results[forced:]
        forced += len(est)

    results = stat_filter(results, include_statistical)
    return results[:top_k]


def merge_exact_only(
    main: list[Cand],
    footnotes: list[Cand],
    footnote_lead_ids: set[str],
    spotlight: list[Cand],
    establishment: list[Cand],
    top_k: int = 8,
    include_statistical: bool = False,
) -> list[Cand]:
    """Gate 2A2b — the shipped production change (searchChannelB.ts).

    Identical to `merge_current` in footnote pass and spotlight pass —
    byte-identical, copy-pasted not refactored. The establishment step
    differs in TWO ways, both required:

      1. Position: inserted at the FRONT of `results`, not `AT forced`
         (behind whatever footnote/spotlight leads already claimed the
         front) — this is the Gate 2A1b change.
      2. Dedup direction: Gate 2A2 shipped with `est = [c for c in
         establishment if c.id not in seen_ids]`, i.e. an establishment row
         was DROPPED if ANN had already surfaced the identical chunk id
         anywhere in `results`. Codex's local behavioral QC caught this live:
         `staff_fullday_24`（「24班小學編制」）has its exact chunk already at
         ANN rank 2 (cosine 0.5288), so the old filter silently discarded the
         score-1 establishment row and rank 0 stayed a WRONG chunk — the
         synthesizer then said "about 40" and claimed the document did not
         state the number, when the exact row does. Gate 2A2b inverts the
         dedup: establishment always wins; any pre-existing copy is stripped
         OUT of `results` instead. Exactly one copy survives, at score 1.
      3. Conflict removal (2nd behavioral QC pass — Codex live-tested
         synthesis, not just retrieval order): ANN still surfaced OTHER
         `staff_est_pri` rows (other class counts) beside the exact row, and
         the synthesizer mixed them into one answer — 「副校長3名（或1名）」
         for a query whose exact row says 3, unconditionally. When
         establishment fires, every result sharing an establishment source_id
         is removed, not just the duplicate id. Non-establishment results are
         untouched.

    Consequence for `results[forced]`: dedup-direction #2 means an
    establishment row CAN now replace what was the main-search lead itself,
    not just prepend ahead of it — so `results[forced]` is NO LONGER a safe
    stand-in for "the original main-search lead" (Gate 2A1b's claim to the
    contrary is retracted). Production now captures `mainSearchLead`
    explicitly, before any overlay runs (`main_search_lead()` below), and
    passes it into `synthesizeAnswer` instead of an index into the
    post-overlay list. This model's `trusted_vault_lead()` takes that
    pre-overlay lead directly, matching the shipped signature change.
    """
    lead = [c for c in footnotes if c.id in footnote_lead_ids][:2]
    seen = {c.id for c in lead}
    rest: list[Cand] = []
    for c in list(main) + list(footnotes):
        if c.id in seen:
            continue
        seen.add(c.id)
        rest.append(c)
    rest.sort(key=by_score)
    results = lead + rest
    forced = len(lead)

    visible = {c.source_id for c in results}
    seen_ids = {c.id for c in results}
    spot = [c for c in spotlight if c.source_id not in visible and c.id not in seen_ids]
    spot.sort(key=by_score)
    spot = spot[:1]
    if spot:
        results = results[:forced] + spot + results[forced:]
        forced += len(spot)

    # Gate 2A2b (2nd pass): establishment always wins, and no OTHER row from
    # the same establishment source survives either — a 12-/14-class row
    # beside the exact 24-class row is conflicting evidence on this table,
    # not context (S211's class-row ambiguity, now closed at the retrieval
    # layer). `est_source_ids` is derived from `establishment` itself rather
    # than a separate constant, matching production's single-source
    # ESTABLISHMENT_SOURCE_IDS list.
    est = list(establishment)
    if est:
        est_source_ids = {c.source_id for c in est}
        results = est + [c for c in results if c.source_id not in est_source_ids]
        forced += len(est)

    results = stat_filter(results, include_statistical)
    return results[:top_k]


# ---------------------------------------------------------------------------
# PROPOSED — membership and display order are decided separately
# ---------------------------------------------------------------------------

def dedup(cands: list[Cand]) -> list[Cand]:
    """One entry per id. Keeps the STRONGER guarantee and the LARGER score.

    Both directions matter. Keeping the weaker guarantee would silently drop a
    required member; keeping the smaller score would rank a chunk below where its
    best-scoring retrieval path put it.
    """
    out: dict[str, Cand] = {}
    for c in cands:
        prev = out.get(c.id)
        if prev is None:
            out[c.id] = c
            continue
        out[c.id] = replace(
            prev,
            score=max(prev.score, c.score),
            required=prev.required or c.required,
            # The origin that carries the requirement is the one worth reporting.
            origin=c.origin if (c.required and not prev.required) else prev.origin,
        )
    return list(out.values())


def merge_proposed(
    cands: list[Cand],
    top_k: int = 8,
    include_statistical: bool = False,
) -> list[Cand]:
    """Guarantee decides WINDOW MEMBERSHIP. Score alone decides ORDER.

    The bug being fixed is that production conflates the two: a 0.45 footnote is
    given index 0 outright, so a score-1.0 lexical exact match lands at index 2.
    Here a required member is guaranteed to be IN the window — which is what
    searchChannelB.ts:1146 says the overlay is for ("reaches the synthesis
    window (top-5)") — and nothing more.

    The statistical filter runs BEFORE selection, unlike production, which
    filters after merging (:1603). Deliberate: a filtered-out chunk must not
    consume a guaranteed slot and leave the window short. See T10.
    """
    win = min(WINDOW, top_k)
    pool = dedup(stat_filter(cands, include_statistical))

    required = [c for c in pool if c.required]
    if len(required) > win:
        required = sorted(
            required, key=lambda c: (OVERFLOW_RANK[c.origin], -c.score, c.id)
        )[:win]
    req_ids = {c.id for c in required}

    non_required = sorted((c for c in pool if c.id not in req_ids), key=by_score)
    fill = non_required[: max(0, win - len(required))]

    window = sorted(required + fill, key=by_score)
    win_ids = {c.id for c in window}
    tail = sorted((c for c in pool if c.id not in win_ids), key=by_score)
    return (window + tail)[:top_k]


def trusted_vault_lead(main_search_lead: Cand | None) -> bool:
    """Gate 1 §4. Replaces `results[forcedLeads]` (searchChannelB.ts:1011).

    `None` (main search empty, or everything filtered out) must NOT bypass the
    judge. This is equivalent to today's behaviour but for a different reason:
    today `?? window[0]` lands on an overlay, whose content_type is never
    `vault_extract`, so the bypass is declined by accident. Here it is declined
    by design.
    """
    return (
        main_search_lead is not None
        and main_search_lead.content_type == "vault_extract"
        and main_search_lead.score >= VAULT_LEAD_SCORE
    )


def main_search_lead(main_sorted: list[Cand], include_statistical: bool = False) -> Cand | None:
    """First main-search result that survives the statistical filter, captured
    BEFORE any overlay runs. The filter predicate is applied here only; the
    broad filter at :1603 does not move."""
    for c in main_sorted:
        if include_statistical or not c.is_stat:
            return c
    return None


def synthesis_window(
    results: list[Cand],
    exact_source_ids: set[str] | None = None,
    enabled: bool = False,
) -> list[Cand]:
    """Gate 2C-1 model: narrow only an explicit establishment exact scope.

    The scope is produced by the establishment route, not inferred from score
    or position. An inconsistent scope falls back to the existing window.
    """
    default = results[:WINDOW]
    if not enabled or not exact_source_ids:
        return default
    narrowed = [c for c in default if c.source_id in exact_source_ids]
    return narrowed or default


# ---------------------------------------------------------------------------
# Fidelity: does the CURRENT model reproduce real recorded production output?
# ---------------------------------------------------------------------------

def classify_recorded(rows: list[dict], spotlight_ids: set[str]) -> dict:
    """Recover overlay roles from a recorded top-k window.

    What is recoverable, and what is not, stated plainly:
      RECOVERABLE  forced footnote leads  — production puts them first and caps
                   them at 2, so `footnote_curated` at index 0/1 are the leads.
      RECOVERABLE  establishment rows     — scored exactly 1 (wikiRepository:415).
      RECOVERABLE  spotlight lead         — a SPOTLIGHT_SOURCE_IDS member sitting
                   directly after the forced leads AND out of score order (a
                   later row scores higher than it). Membership in
                   SPOTLIGHT_SOURCE_IDS alone is NOT sufficient: `staff_est_pri`
                   and `edbcm116_2026` are spotlight-eligible sources that also
                   win ordinary top rank on plenty of queries, so a naive
                   "spotlight-eligible source right after the leads" test
                   misfires on every query where that source is legitimately
                   #1. Measured against 184 recorded production windows
                   (`dev/source/eval_runs/2026-09-04_s214_gold_expanded_resolved.json`):
                   the naive test produced 6/184 false positives, each one
                   silently dropping the misclassified chunk from the modeled
                   output (see `_s214_gate2a1_replay.py`'s fidelity check,
                   which caught this). The score-order-violation requirement
                   fixes all 6.
      NOT RECOVERABLE  whether a footnote at index >= 2 had CLEARED the lead gate
                   and merely lost on score. The response carries no gate flag.
                   Such footnotes are treated as non-required, which is what the
                   recorded order shows them to be.
      NOT RECOVERABLE  exact tie-break order. 3/184 recorded windows contain an
                   EXACT score tie (e.g. two chunks both at 0.7284) whose
                   recorded relative order is not id-ascending. This model uses
                   id-ascending as an explicit, documented tie-break (needed for
                   T2 determinism); it does not claim to reproduce production's
                   actual tie order, which appears to depend on something this
                   model does not have access to (likely DB/RPC return order)
                   and was not further investigated — see the Gate 2A1 report.
    """
    leads = []
    for r in rows[:2]:
        if r.get("content_type") == "footnote_curated":
            leads.append(r)
        else:
            break
    n = len(leads)
    est = [r for r in rows if isinstance(r.get("score"), (int, float)) and r["score"] >= 0.999]
    spot = None
    if n < len(rows):
        c = rows[n]
        later_scores = [r["score"] for r in rows[n + 1:]
                        if isinstance(r.get("score"), (int, float))]
        out_of_score_order = (
            isinstance(c.get("score"), (int, float))
            and later_scores and c["score"] < max(later_scores)
        )
        if c.get("source_id") in spotlight_ids and c not in est and out_of_score_order:
            spot = c
    return {"lead_rows": leads, "establishment_rows": est, "spotlight_row": spot}


def rows_to_cands(rows: list[dict], cls: dict) -> list[Cand]:
    lead_ix = {id(r) for r in cls["lead_rows"]}
    est_ix = {id(r) for r in cls["establishment_rows"]}
    spot_ix = {id(cls["spotlight_row"])} if cls["spotlight_row"] else set()
    out = []
    for r in rows:
        if id(r) in est_ix:
            origin, req = ESTABLISHMENT, True
        elif id(r) in lead_ix:
            origin, req = FOOTNOTE, True
        elif id(r) in spot_ix:
            origin, req = SPOTLIGHT, True
        else:
            origin, req = MAIN, False
        out.append(Cand(
            id=str(r.get("id") or r.get("chunk_id") or r.get("source_id")),
            score=float(r.get("score") or 0.0),
            source_id=str(r.get("source_id") or ""),
            content_type=str(r.get("content_type") or "unknown"),
            origin=origin, required=req,
        ))
    return out


# ---------------------------------------------------------------------------
# T1-T14
# ---------------------------------------------------------------------------

def self_test() -> int:
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    def C(cid, score, *, origin=MAIN, req=False, ct=None, sid=None) -> Cand:
        return Cand(id=cid, score=score, source_id=sid or cid,
                    content_type=ct or ("footnote_curated" if origin == FOOTNOTE
                                        else "vault_extract"),
                    origin=origin, required=req)

    def ids(lst): return [c.id for c in lst]
    def scores(lst): return [c.score for c in lst]

    # ---- T1 ordering invariant -------------------------------------------
    pool = [C("m1", 0.75), C("m2", 0.70), C("m3", 0.65), C("m4", 0.55),
            C("fn1", 0.50, origin=FOOTNOTE, req=True),
            C("fn2", 0.48, origin=FOOTNOTE, req=True),
            C("sp", 0.60, origin=SPOTLIGHT, req=True),
            C("est", 1.00, origin=ESTABLISHMENT, req=True)]
    out = merge_proposed(pool, top_k=8)
    win, tail = out[:WINDOW], out[WINDOW:]
    check("T1 window is sorted by (score desc, id asc)",
          [by_score(c) for c in win] == sorted(by_score(c) for c in win))
    check("T1 tail is sorted by (score desc, id asc)",
          [by_score(c) for c in tail] == sorted(by_score(c) for c in tail))

    # ---- T2 determinism + id tie-break -----------------------------------
    check("T2 same input twice gives identical output",
          ids(merge_proposed(pool, top_k=8)) == ids(merge_proposed(pool, top_k=8)))
    tie = [C("bbb", 0.5), C("aaa", 0.5), C("ccc", 0.5)]
    check("T2 equal scores break by id ascending",
          ids(merge_proposed(tie, top_k=3)) == ["aaa", "bbb", "ccc"])
    check("T2 input order does not matter",
          ids(merge_proposed(list(reversed(pool)), top_k=8))
          == ids(merge_proposed(pool, top_k=8)))

    # ---- T3 score-1 precedence -------------------------------------------
    t3 = [C("est", 1.00, origin=ESTABLISHMENT, req=True),
          C("fn1", 0.50, origin=FOOTNOTE, req=True),
          C("fn2", 0.48, origin=FOOTNOTE, req=True)]
    o3 = merge_proposed(t3, top_k=8)
    check("T3 exact score-1 establishment row leads",
          o3[0].id == "est" and o3[0].origin == ESTABLISHMENT)

    # ---- T4 single footnote (CORRECTED per Codex Gate 1 verdict) ---------
    # A qualifying footnote is NOT asserted to be off index 0. If it genuinely
    # has the top score, index 0 is correct. What is asserted is membership plus
    # the absence of any higher-scoring window member behind it.
    t4_low = [C("fn", 0.46, origin=FOOTNOTE, req=True)] + [
        C(f"m{i}", 0.90 - i * 0.01) for i in range(7)]
    o4 = merge_proposed(t4_low, top_k=8)
    pos = ids(o4).index("fn")
    w4 = o4[:min(WINDOW, 8)]
    check("T4 low-scoring qualifying footnote stays in top min(5,top_k)",
          pos < min(WINDOW, 8))
    check("T4 every higher-scoring selected window member precedes it",
          all(w4[i].score >= w4[i + 1].score for i in range(len(w4) - 1)))
    t4_high = [C("fn", 0.99, origin=FOOTNOTE, req=True)] + [
        C(f"m{i}", 0.50) for i in range(7)]
    check("T4 top-scoring qualifying footnote IS allowed at index 0",
          merge_proposed(t4_high, top_k=8)[0].id == "fn")

    # ---- T5 two footnotes -------------------------------------------------
    t5 = [C("fn1", 0.50, origin=FOOTNOTE, req=True),
          C("fn2", 0.48, origin=FOOTNOTE, req=True)] + [
        C(f"m{i}", 0.90) for i in range(6)]
    o5 = merge_proposed(t5, top_k=8)
    check("T5 both footnotes inside the window",
          ids(o5).index("fn1") < WINDOW and ids(o5).index("fn2") < WINDOW)
    check("T5 higher-scoring footnote precedes the lower one",
          ids(o5).index("fn1") < ids(o5).index("fn2"))

    # ---- T6 spotlight keeps top-5 membership (Gate 1 defect D2) ----------
    t6 = [C("sp", 0.60, origin=SPOTLIGHT, req=True),
          C("fn1", 0.50, origin=FOOTNOTE, req=True),
          C("fn2", 0.48, origin=FOOTNOTE, req=True)] + [
        C(f"m{i}", 0.90) for i in range(5)]
    o6 = merge_proposed(t6, top_k=8)
    check("T6 spotlight and both footnotes are all inside the window",
          all(ids(o6).index(x) < WINDOW for x in ("sp", "fn1", "fn2")))

    # ---- T7 the Codex worked example -------------------------------------
    o7 = merge_proposed(pool, top_k=8)
    check("T7 worked example order matches the agreed design",
          scores(o7) == [1.00, 0.75, 0.60, 0.50, 0.48, 0.70, 0.65, 0.55])
    check("T7 exact match moved from index 3 to index 0",
          ids(o7)[0] == "est")

    # ---- T8 dedup ---------------------------------------------------------
    t8 = [Cand("dup", 0.62, "s", "vault_extract", MAIN, False),
          Cand("dup", 0.60, "s", "footnote_curated", FOOTNOTE, True),
          C("m1", 0.80)]
    o8 = merge_proposed(t8, top_k=8)
    check("T8 duplicate id appears exactly once", ids(o8).count("dup") == 1)
    d8 = next(c for c in o8 if c.id == "dup")
    check("T8 dedup keeps the stronger guarantee", d8.required is True)
    check("T8 dedup keeps the larger score", d8.score == 0.62)

    # ---- T9 empty main search --------------------------------------------
    t9 = [C("fn1", 0.50, origin=FOOTNOTE, req=True),
          C("sp", 0.60, origin=SPOTLIGHT, req=True)]
    o9 = merge_proposed(t9, top_k=8)
    check("T9 overlay-only input does not crash and keeps every required member",
          len(o9) == 2 and set(ids(o9)) == {"fn1", "sp"})
    check("T9 empty candidate set returns empty", merge_proposed([], top_k=8) == [])

    # ---- T10 statistical filtering ---------------------------------------
    t10 = [Cand("st", 0.99, "stat_kg", "vault_extract", FOOTNOTE, True)] + [
        C(f"m{i}", 0.50 - i * 0.01) for i in range(7)]
    o10 = merge_proposed(t10, top_k=8)
    check("T10 statistical source is excluded when not requested",
          "st" not in ids(o10))
    check("T10 excluded statistical member does not consume a window slot",
          len(o10[:WINDOW]) == WINDOW and all(not c.is_stat for c in o10))
    check("T10 statistical source is kept when explicitly requested",
          "st" in ids(merge_proposed(t10, top_k=8, include_statistical=True)))

    # ---- T11 overflow -----------------------------------------------------
    t11 = ([C(f"e{i}", 1.00, origin=ESTABLISHMENT, req=True, sid="staff_est_pri")
            for i in range(4)]
           + [C("fn1", 0.50, origin=FOOTNOTE, req=True),
              C("fn2", 0.48, origin=FOOTNOTE, req=True),
              C("sp", 0.60, origin=SPOTLIGHT, req=True)]
           + [C("m1", 0.55)])
    o11 = merge_proposed(t11, top_k=8)
    w11 = o11[:WINDOW]
    check("T11 all four establishment rows hold window slots",
          all(f"e{i}" in ids(w11) for i in range(4)))
    check("T11 footnote takes the one remaining window slot (overflow rank 1)",
          "fn1" in ids(w11) and "fn2" not in ids(w11))
    check("T11 demoted spotlight is NOT dropped, only moved to the tail",
          "sp" in ids(o11) and ids(o11).index("sp") >= WINDOW)
    check("T11 nothing is lost overall", len(o11) == min(len(t11), 8))

    # ---- T12 trustedVaultLead --------------------------------------------
    check("T12 no main lead does not bypass the judge",
          trusted_vault_lead(None) is False)
    check("T12 a footnote lead does not bypass the judge",
          trusted_vault_lead(C("f", 0.95, origin=FOOTNOTE, ct="footnote_curated")) is False)
    check("T12 vault_extract at exactly 0.70 bypasses",
          trusted_vault_lead(C("v", 0.70, ct="vault_extract")) is True)
    check("T12 vault_extract at 0.6999 does not bypass",
          trusted_vault_lead(C("v", 0.6999, ct="vault_extract")) is False)
    check("T12 main lead skips a statistical row",
          main_search_lead([Cand("s", 0.9, "stat_kg", "vault_extract"),
                            Cand("v", 0.8, "g05", "vault_extract")]).id == "v")
    check("T12 main lead is None when everything is filtered out",
          main_search_lead([Cand("s", 0.9, "stat_kg", "vault_extract")]) is None)

    # ---- T13 membership conservation vs CURRENT (Gate 1 §5 proposition) ---
    # Claim, stated exactly: for a candidate set with NO statistical rows and
    # |R| <= min(5, top_k), CURRENT and PROPOSED return the same MULTISET at
    # top_k and the same SET in the window. Only the order differs.
    cur13 = merge_current(
        main=[C("m1", 0.75), C("m2", 0.70), C("m3", 0.65), C("m4", 0.55)],
        footnotes=[C("fn1", 0.50, origin=FOOTNOTE), C("fn2", 0.48, origin=FOOTNOTE)],
        footnote_lead_ids={"fn1", "fn2"},
        spotlight=[C("sp", 0.60, origin=SPOTLIGHT, sid="edbcm108_2026")],
        establishment=[C("est", 1.00, origin=ESTABLISHMENT)],
        top_k=8)
    prop13 = merge_proposed(pool, top_k=8)
    check("T13 top_k multiset is conserved", sorted(ids(cur13)) == sorted(ids(prop13)))
    check("T13 window SET is conserved",
          sorted(ids(cur13[:WINDOW])) == sorted(ids(prop13[:WINDOW])))
    check("T13 order genuinely differs (the change is not a no-op)",
          ids(cur13) != ids(prop13))
    check("T13 CURRENT really does bury the exact match",
          ids(cur13).index("est") == 3 and ids(prop13).index("est") == 0)

    # ---- T14 top_k < 5 ----------------------------------------------------
    t14 = [C("fn1", 0.20, origin=FOOTNOTE, req=True),
           C("fn2", 0.19, origin=FOOTNOTE, req=True)] + [C(f"m{i}", 0.9) for i in range(5)]
    o14 = merge_proposed(t14, top_k=3)
    check("T14 top_k=3 returns exactly 3", len(o14) == 3)
    check("T14 both required members still fit the narrowed window",
          "fn1" in ids(o14) and "fn2" in ids(o14))
    check("T14 window is still score-ordered",
          [by_score(c) for c in o14] == sorted(by_score(c) for c in o14))
    check("T14 top_k=0 returns empty", merge_proposed(pool, top_k=0) == [])

    # ---- EXACT-ONLY variant (Gate 2A1b) ------------------------------------
    eo_main = [C("m1", 0.75), C("m2", 0.70), C("m3", 0.65), C("m4", 0.55)]
    eo_fn = [C("fn1", 0.50, origin=FOOTNOTE, req=True),
             C("fn2", 0.48, origin=FOOTNOTE, req=True)]
    eo_sp = [C("sp", 0.60, origin=SPOTLIGHT, req=True, sid="edbcm108_2026")]
    eo_est = [C("est", 1.00, origin=ESTABLISHMENT, req=True)]

    eo_current = merge_current(eo_main, eo_fn, {"fn1", "fn2"}, eo_sp, eo_est, top_k=8)
    eo_exact = merge_exact_only(eo_main, eo_fn, {"fn1", "fn2"}, eo_sp, eo_est, top_k=8)

    check("EXACT-ONLY: worked example moves establishment to index 0",
          ids(eo_exact)[0] == "est")
    check("EXACT-ONLY: everything BEHIND establishment keeps CURRENT's exact order",
          ids(eo_exact)[1:] == ids(eo_current)[:ids(eo_current).index("est")]
          + ids(eo_current)[ids(eo_current).index("est") + 1:])
    check("EXACT-ONLY: CURRENT still buries establishment at index 3 (unchanged baseline)",
          ids(eo_current).index("est") == 3)
    check("EXACT-ONLY: footnote lead order is untouched (fn1 before fn2, both before spotlight)",
          ids(eo_exact).index("fn1") < ids(eo_exact).index("fn2")
          < ids(eo_exact).index("sp"))
    check("EXACT-ONLY: top_k multiset identical to CURRENT (pure reorder, no membership change)",
          sorted(ids(eo_exact)) == sorted(ids(eo_current)))

    # `results[forced]` happens to still be "m1" here — but ONLY because this
    # fixture has no id collision between establishment and main. §Gate 2A2b
    # tests below show that claim does NOT generalise once establishment can
    # replace a duplicate already in `results`, which is exactly why
    # `mainSearchLead` is now captured separately instead of read by index.
    n_forced_exact = 1 + 1 + len(eo_fn)  # est + spotlight + 2 footnotes
    check("EXACT-ONLY: results[forced] happens to be main-search lead (NO-COLLISION case only)",
          eo_exact[n_forced_exact].id == "m1")

    # Multiple establishment rows: front-insertion must preserve their own
    # relative order (by score, then id) — it does not reintroduce the
    # overflow-priority machinery from merge_proposed, since this variant never
    # needs it (production's `limit=8` on the establishment REST query and the
    # 184-item replay never produced more than 1 establishment row per query).
    eo_est2 = [C("e2", 1.00, origin=ESTABLISHMENT, req=True, sid="staff_est_pri"),
               C("e1", 1.00, origin=ESTABLISHMENT, req=True, sid="staff_est_pri")]
    eo_multi = merge_exact_only(eo_main, eo_fn, {"fn1", "fn2"}, eo_sp, eo_est2, top_k=8)
    # Neither CURRENT nor EXACT-ONLY sorts the establishment list internally —
    # both trust whatever order the establishment overlay query returned
    # (`wikiRepository.searchEstablishmentRows` does not ORDER BY score, since
    # every row is scored 1 and carries no other ranking signal). EXACT-ONLY
    # must not invent a new internal ordering CURRENT does not already have:
    # the input order (e2 then e1) is preserved verbatim, just moved to front.
    check("EXACT-ONLY: establishment internal order is pass-through, not re-sorted",
          ids(eo_multi)[:2] == ["e2", "e1"])
    check("EXACT-ONLY: multiple establishment rows both still land at the front",
          set(ids(eo_multi)[:2]) == {"e1", "e2"})

    check("EXACT-ONLY: no establishment row is a true no-op (identical to CURRENT)",
          merge_exact_only(eo_main, eo_fn, {"fn1", "fn2"}, eo_sp, [], top_k=8)
          == merge_current(eo_main, eo_fn, {"fn1", "fn2"}, eo_sp, [], top_k=8))

    # ---- Gate 2A2b: dedup-direction fix (Codex live QC caught staff_fullday_24) --
    # Reproduces the bug class exactly: `searchEstablishmentRows` returns the
    # SAME chunk id ANN already found (chunk ids are content hashes, so the
    # identical chunk retrieved two ways carries the identical id). The old
    # `est = [c for c in establishment if c.id not in seen_ids]` filter
    # dropped the score-1 row whenever this happened; the fix strips the
    # ANN duplicate out of `results` instead, so establishment always wins.

    dup_id = "vault_staff_est_pri_58f262551ffa"  # same id, two retrieval paths
    dup_ann_copy = Cand(dup_id, 0.5288, "staff_est_pri", "vault_extract", MAIN, False)
    dup_exact_copy = Cand(dup_id, 1.00, "staff_est_pri", "vault_extract",
                          ESTABLISHMENT, True)

    # exact row ABSENT from ANN (baseline — already covered by T3/T7, restated
    # here for a single self-contained Gate 2A2b block)
    absent_main = [C("m1", 0.5758), C("m2", 0.70), C("m3", 0.65)]
    o_absent = merge_exact_only(absent_main, [], set(), [], [dup_exact_copy], top_k=8)
    check("Gate 2A2b: exact row absent from ANN is simply prepended",
          ids(o_absent)[0] == dup_id and len(o_absent) == 4)

    # exact row already at MAIN RANK 0 (highest score) — the reproduced bug's
    # sibling case: the duplicate IS the current leader.
    rank0_main = [dup_ann_copy, C("m2", 0.40), C("m3", 0.30)]
    o_rank0 = merge_exact_only(rank0_main, [], set(), [], [dup_exact_copy], top_k=8)
    check("Gate 2A2b: exact row already at main rank 0 — old copy replaced, not duplicated",
          ids(o_rank0).count(dup_id) == 1 and o_rank0[0].id == dup_id
          and o_rank0[0].score == 1.00)

    # exact row already at MAIN RANK 2 — the EXACT `staff_fullday_24`
    # reproduction: 0.5758 leads, 0.5327 second, the dup at 0.5288 third.
    rank2_main = [C("hi", 0.5758), C("mid", 0.5327), dup_ann_copy]
    o_rank2 = merge_exact_only(rank2_main, [], set(), [], [dup_exact_copy], top_k=8)
    check("Gate 2A2b: exact row already at main rank 2 is promoted to rank 0",
          o_rank2[0].id == dup_id and o_rank2[0].score == 1.00)
    check("Gate 2A2b: the old rank-2 slot is gone, not left as a second copy",
          ids(o_rank2).count(dup_id) == 1)
    check("Gate 2A2b: displaced main candidates ('hi', 'mid') are NOT dropped",
          "hi" in ids(o_rank2) and "mid" in ids(o_rank2))

    # exact row duplicated through ANOTHER overlay too (footnote pass also
    # surfaced the identical id — the dedup must hold across ALL origins, not
    # just main).
    dup_footnote_copy = Cand(dup_id, 0.52, "staff_est_pri", "footnote_curated",
                             FOOTNOTE, False)
    o_multi_dup = merge_exact_only(
        [C("m1", 0.60)], [dup_footnote_copy], set(), [], [dup_exact_copy], top_k=8)
    check("Gate 2A2b: exact row duplicated via footnote pass still yields one copy",
          ids(o_multi_dup).count(dup_id) == 1)

    # exactly one output copy with score 1 — general property, not just this
    # fixture.
    check("Gate 2A2b: exactly one copy at score 1 across all three collision cases",
          all(sum(1 for c in out if c.id == dup_id and c.score == 1.00) == 1
              for out in (o_rank0, o_rank2, o_multi_dup)))

    # trustedVaultLead must evaluate the ORIGINAL pre-overlay main lead, not
    # whatever ends up at the front after establishment promotes a duplicate.
    # This is the concrete case the retracted Gate 2A1b claim missed: in
    # rank2_main, the pre-overlay main lead is "hi" (0.5758, vault_extract,
    # below VAULT_LEAD_SCORE 0.70) — establishment promotion must NOT make the
    # judge bypass fire on the newly-promoted score-1 establishment row.
    pre_overlay_lead = main_search_lead(sorted(rank2_main, key=by_score))
    check("Gate 2A2b: mainSearchLead is captured from the PRE-overlay main list",
          pre_overlay_lead is not None and pre_overlay_lead.id == "hi")
    check("Gate 2A2b: trustedVaultLead reads the pre-overlay lead, not the post-overlay front",
          trusted_vault_lead(pre_overlay_lead) is False)  # 0.5758 < VAULT_LEAD_SCORE
    check("Gate 2A2b: a pre-overlay lead that DOES clear the bar still bypasses",
          trusted_vault_lead(Cand("v", 0.70, "s", "vault_extract")) is True)

    # ---- Gate 2A2b (2nd pass): competing class-count rows are conflicting
    # evidence on THIS table, not context — Codex's live synthesis QC caught
    # the 24-class query mixing in a 14-class row's 副校長 count. Reproduces
    # the exact shape: one exact row for the asked class count, plus OTHER
    # staff_est_pri rows for different class counts that ANN also surfaced,
    # plus one unrelated source that must be left alone.
    exact_24 = Cand("vault_staff_est_pri_24exact", 1.00, "staff_est_pri",
                    "vault_extract", ESTABLISHMENT, True)
    row_14 = Cand("vault_staff_est_pri_14row", 0.5327, "staff_est_pri",
                  "vault_extract", MAIN, False)
    row_12 = Cand("vault_staff_est_pri_12row", 0.50, "staff_est_pri",
                  "vault_extract", MAIN, False)
    unrelated = Cand("vault_sag_2025_11_x", 0.45, "sag_2025_11",
                     "vault_extract", MAIN, False)
    conflict_main = [Cand("hi24", 0.5758, "staff_est_pri", "vault_extract", MAIN, False),
                     row_14, row_12, unrelated]
    o_conflict = merge_exact_only(conflict_main, [], set(), [], [exact_24], top_k=8)

    check("Gate 2A2b: only the exact establishment row from that source survives",
          sum(1 for c in o_conflict if c.source_id == "staff_est_pri") == 1
          and o_conflict[0].id == "vault_staff_est_pri_24exact")
    check("Gate 2A2b: the competing 14-/12-class rows are gone, not just deduped",
          "vault_staff_est_pri_14row" not in ids(o_conflict)
          and "vault_staff_est_pri_12row" not in ids(o_conflict))
    check("Gate 2A2b: the unrelated source is left alone",
          "vault_sag_2025_11_x" in ids(o_conflict))
    check("Gate 2A2b: top_k is refilled only from non-conflicting candidates "
          "(3 removed from a 5-candidate pool leaves exactly 2 in the output)",
          len(o_conflict) == 2)  # exact_24 + unrelated; hi24/row_14/row_12 all removed
    conflict_pre_overlay = main_search_lead(sorted(conflict_main, key=by_score))
    check("Gate 2A2b: mainSearchLead for the conflict case is still the PRE-overlay lead",
          conflict_pre_overlay is not None and conflict_pre_overlay.id == "hi24")
    check("Gate 2A2b: that pre-overlay lead correctly does not bypass (0.5758 < 0.70)",
          trusted_vault_lead(conflict_pre_overlay) is False)

    # ---- Gate 2C-1: synthesis scope is explicit, never inferred from rank/score.
    check("Gate 2C-1: flag off preserves the existing synthesis window",
          synthesis_window(o_conflict, {"staff_est_pri"}, enabled=False)
          == o_conflict[:WINDOW])
    check("Gate 2C-1: exact establishment scope removes unrelated context",
          ids(synthesis_window(o_conflict, {"staff_est_pri"}, enabled=True))
          == ["vault_staff_est_pri_24exact"])
    non_est_exact = [C("other_exact", 1.00, sid="other_source"), unrelated]
    check("Gate 2C-1: a score-1 non-establishment result does not self-trigger narrowing",
          synthesis_window(non_est_exact, None, enabled=True) == non_est_exact)
    check("Gate 2C-1: no exact scope does not narrow",
          synthesis_window(o_conflict, None, enabled=True) == o_conflict[:WINDOW])
    check("Gate 2C-1: inconsistent exact scope falls back instead of returning empty",
          synthesis_window(o_conflict, {"missing_source"}, enabled=True)
          == o_conflict[:WINDOW])

    # empty / statistically-filtered main search fails closed
    check("Gate 2A2b: no main search at all -> mainSearchLead is None -> fail closed",
          main_search_lead([]) is None and trusted_vault_lead(None) is False)
    stat_only_main = [Cand("st", 0.99, "stat_kg", "vault_extract")]
    check("Gate 2A2b: main search fully statistically-filtered -> None -> fail closed",
          main_search_lead(stat_only_main, include_statistical=False) is None
          and trusted_vault_lead(main_search_lead(stat_only_main)) is False)

    # ---- classify_recorded: spotlight heuristic must require a score-order
    # violation, not mere SPOTLIGHT_SOURCE_IDS membership (Gate 2A1 fidelity fix)
    def R(cid, sid, ct, sc):
        return {"id": cid, "source_id": sid, "content_type": ct, "score": sc}

    coincidental_top = [
        R("s1", "staff_est_pri", "vault_extract", 0.90),   # spotlight-eligible, but genuinely #1
        R("s2", "staff_est_pri", "vault_extract", 0.80),
        R("s3", "sag_2025_11", "vault_extract", 0.70),
    ]
    check("classify_recorded does NOT flag a spotlight-eligible top scorer",
          classify_recorded(coincidental_top, {"staff_est_pri"})["spotlight_row"] is None)
    genuine_insertion = [
        R("g1", "edbcm108_2026", "vault_extract", 0.62),   # spotlight-eligible, OUT of order
        R("g2", "sag_2025_11", "vault_extract", 0.68),     # scores higher, comes after
    ]
    check("classify_recorded DOES flag a genuine out-of-order spotlight insertion",
          classify_recorded(genuine_insertion, {"edbcm108_2026"})["spotlight_row"]
          == genuine_insertion[0])

    print()
    print(f"{'ALL PASS' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


# ---------------------------------------------------------------------------
# Fidelity check against recorded production output
# ---------------------------------------------------------------------------

SPOTLIGHT_SOURCE_IDS = {
    "edbcm113_2026", "edbcm094_2026", "edbcm073_2026", "edbcm066_2026",
    "iit_ai_framework_2026", "edbc013_2026", "edbcm116_2026", "staff_est_pri",
    "roles_functions_pri", "psm_sgt", "ppt_grad_pri_faq", "ppt_grad_pri_policy",
    "edbc19011", "faq_edbc19011", "edbcm099_2026", "edbcm135_2026",
    "edbcm108_2026", "edbc014_2026", "edbcm152_2026",
}


def fidelity_report(path: str) -> dict:
    """Replay the CURRENT model against recorded production windows.

    A recorded window is production's own output. If the CURRENT model, fed the
    roles recovered from that window, does not reproduce it, the model is not a
    model of production and nothing built on it is evidence about production.

    Returns a dict rather than printing, so a caller (the CLI, or the Gate 2A1
    replay script) can distinguish three outcomes that must NOT be collapsed
    into one number:
      - reproduced : the model matches recorded production order exactly.
      - mismatched : the model does NOT match — a real disagreement to explain.
      - skipped    : the artifact lacks `content_type`, so overlay roles cannot
                     be recovered at all. This is an ABSENCE of evidence, not a
                     pass. An artifact that is 100% skipped must never be
                     reported as "fidelity confirmed".
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ok, bad, skipped = 0, 0, 0
    mismatches: list[dict] = []
    for q in data["results"]:
        rows = q.get("results") or []
        if not rows or any(r.get("content_type") is None for r in rows):
            skipped += 1
            continue
        cls = classify_recorded(rows, SPOTLIGHT_SOURCE_IDS)
        cands = rows_to_cands(rows, cls)
        cur = merge_current(
            main=[c for c in cands if c.origin == MAIN],
            footnotes=[c for c in cands if c.origin == FOOTNOTE],
            footnote_lead_ids={c.id for c in cands
                               if c.origin == FOOTNOTE and c.required},
            spotlight=[c for c in cands if c.origin == SPOTLIGHT],
            establishment=[c for c in cands if c.origin == ESTABLISHMENT],
            top_k=len(rows))
        if [c.id for c in cur] == [c.id for c in cands]:
            ok += 1
        else:
            bad += 1
            mismatches.append({
                "id": q.get("id"),
                "recorded": [c.id for c in cands],
                "recorded_scores": [c.score for c in cands],
                "model": [c.id for c in cur],
            })
    verified = ok + bad
    return {
        "path": path,
        "reproduced": ok,
        "mismatched": bad,
        "skipped": skipped,
        "verified_total": verified,
        # Distinct from "PASS": a file that is 0/0/N (all skipped) has
        # verified_total == 0 and must not be read as fidelity evidence at all.
        "status": ("NO_EVIDENCE" if verified == 0
                   else "FAIL" if bad else "PASS"),
        "mismatches": mismatches,
    }


def fidelity_rows(path: str) -> int:
    """CLI wrapper: print the report and choose a process exit code.

    Exit code contract (this is the fix for the Gate 2A1 defect: a file that is
    entirely skipped must not exit 0, because 0 conventionally reads as "checked
    and fine" — here nothing was checked at all):
      0 = PASS         (verified_total > 0, zero mismatches)
      1 = FAIL         (at least one mismatch — a real disagreement)
      2 = NO_EVIDENCE  (verified_total == 0 — nothing could be checked)
    """
    r = fidelity_report(path)
    for m in r["mismatches"]:
        print(f"  MISMATCH {m['id']}")
        print(f"    recorded: {m['recorded']}  scores={m['recorded_scores']}")
        print(f"    model   : {m['model']}")
    print(f"fidelity[{r['status']}]: reproduced {r['reproduced']}, "
          f"mismatched {r['mismatched']}, skipped {r['skipped']} "
          f"(skipped = rows without content_type, not recoverable; "
          f"a file with verified_total=0 is NO_EVIDENCE, not a pass)")
    return {"PASS": 0, "FAIL": 1, "NO_EVIDENCE": 2}[r["status"]]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--fidelity", metavar="RUN_JSON",
                   help="replay the CURRENT model against a recorded run file")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if a.fidelity:
        return fidelity_rows(a.fidelity)
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
