#!/usr/bin/env python3
"""
eval_retrieval.py — Channel B retrieval eval harness (roadmap R1).
──────────────────────────────────────────────────────────────────
READ-ONLY. Runs a fixed query set (`dev/source/eval_queries.json`) against the
live Channel B endpoint, records the ranked source_ids per query, and diffs two
runs so a retrieval change can be judged as "intended improvement" vs "silent
regression" mechanically instead of by eyeballing a handful of curl calls.

Why this exists (S192 roadmap R1): every retrieval change so far (S174 footnote
overlay, S183 supersede penalty, S193 spotlight) was verified by ad-hoc live
queries typed fresh each session. That catches the intended win but only samples
the collateral damage, and nothing is comparable across sessions.

Two hard-won rules baked in:
  1. TIE FLIPS ARE NOT REGRESSIONS. g24 and sag_2025_11 are the same document
     ingested twice; their chunk text is identical, so cosine is identical and
     the order between them flips run to run (verified S193 on an unmodified
     build). `_tie_aliases` in the query file collapses such pairs into one
     identity before comparing.
  2. A THROTTLED CALL IS NOT AN EMPTY RESULT. The endpoint is rate-limited
     (10/min per IP for POST + a global backstop). A 429 is retried with
     backoff and, if it still fails, recorded as `error` — never as "0 results",
     which would read as a catastrophic regression.

Usage (from repo root):
  python3 dev/source/eval_retrieval.py --self-test
  python3 dev/source/eval_retrieval.py --run --out dev/source/eval_runs/baseline.json
  python3 dev/source/eval_retrieval.py --run --out after.json --limit 5
  python3 dev/source/eval_retrieval.py --compare before.json after.json

Exit codes: 0 = ok / no regression, 1 = regression or run error.
`--compare` treats only SET_LOST and VERDICT_REGRESSED as failures; rank shifts
and newly added sources are reported but do not fail (a new source entering the
top_k is the normal, intended effect of an ingest). S210: the *other half* of
that same event -- the tail the entrant evicts -- is DISPLACED, also reported
and also non-failing. Scoring the entrance benign but the eviction blocking
made the gate fire on every run following an ingest, and the Option A pipeline
now ingests daily; a gate that is red every morning is a gate nobody reads.
"""
from __future__ import annotations

import argparse
import http.client
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # …/Draft
QUERY_FILE = REPO_ROOT / "dev" / "source" / "eval_queries.json"
DEFAULT_ENDPOINT = "https://edb-knowledge.onrender.com/api/search/channel-b"

# The POST limiter is 10/min per IP; 7s keeps us under it with headroom for the
# warm-up call. Raise with --pace if the limiter is ever tightened.
DEFAULT_PACE_S = 7.0
REQUEST_TIMEOUT_S = 120  # Render free tier cold-starts at ~50s
MAX_ATTEMPTS = 4
SCORE_EPSILON = 0.002  # below this, a score move is noise, not a change
DEFAULT_CHUNK_WITHIN = 5  # S212 — a chunk assertion asks about the synthesis window

# ---------------------------------------------------------------------------
# pure helpers (offline-testable — no network, no clock)
# ---------------------------------------------------------------------------


def load_query_set(path: Path = QUERY_FILE) -> tuple[list[dict], list[list[str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["queries"], data.get("_tie_aliases", [])


def build_tie_map(tie_aliases: list[list[str]]) -> dict[str, str]:
    """{'g24': 'g24|sag_2025_11', 'sag_2025_11': 'g24|sag_2025_11'}"""
    tie_map: dict[str, str] = {}
    for group in tie_aliases:
        canonical = "|".join(sorted(group))
        for sid in group:
            tie_map[sid] = canonical
    return tie_map


def canon(source_id: str, tie_map: dict[str, str]) -> str:
    return tie_map.get(source_id, source_id)


def squeeze(text: str) -> str:
    """Strip ALL whitespace. Required, not cosmetic.

    S211 spent part of a session concluding a passage was absent from the top 80
    because the exact substring search missed 「新 入職教師」 — the PDF text layer
    had a line break inside the phrase, and the passage was in fact at rank 1. Any
    matcher that reads chunk text and does not do this is measuring the extractor's
    line wrapping, not retrieval.
    """
    return re.sub(r"\s+", "", text or "")


def chunk_verdict_for(results: list[dict], expect_text_any: list[str],
                      within: int = DEFAULT_CHUNK_WITHIN) -> tuple[str, int | None]:
    """(verdict, rank of the first result whose TEXT carries a wanted signature).

    S212 — the chunk-layer assertion the harness was missing. Asserts on a text
    signature rather than the chunk id, deliberately, and against the priority's
    own suggested wording ("assert the chunk id enters the top five"):

      chunk ids are `vault_<sid>_<md5(text)[:12]>` (dev/vault/expand_vault.py:502,
      627), i.e. derived from the chunk's own text. Every re-chunk mints new ids
      for the whole source. S211 re-chunked staff_est_pri with chunk_overlap=0, so
      an id assertion written the day before would have gone red on the very fix it
      was built to protect. An instrument that cries wolf on every ingest is the
      wallpaper failure of discipline #14.

    A text signature also fails in exactly the case worth catching: if re-chunking
    splits a table row so the signature no longer sits inside one chunk, the answer
    passage no longer exists as a retrievable unit — which is the S211 defect
    ("片段由半行開始") stated as a testable condition.
    """
    if not expect_text_any:
        return "RECORD_ONLY", None
    wanted = [squeeze(w) for w in expect_text_any]
    for i, r in enumerate(results[:within]):
        hay = squeeze(r.get("text", ""))
        if any(w and w in hay for w in wanted):
            return "PASS", i
    return "FAIL", None


def verdict_for(result_sids: list[str], expect_any: list[str],
                tie_map: dict[str, str]) -> tuple[str, int | None]:
    """(verdict, rank_of_first_expected). RECORD_ONLY when nothing is asserted."""
    if not expect_any:
        return "RECORD_ONLY", None
    wanted = {canon(s, tie_map) for s in expect_any}
    for i, sid in enumerate(result_sids):
        if canon(sid, tie_map) in wanted:
            return "PASS", i
    return "FAIL", None


def _is_displacement(b_sids: list[str], a_sids: list[str],
                     added: list[str]) -> bool:
    """True when every lost source was evicted from the tail by a new entrant.

    At a fixed top_k, a source entering the list necessarily pushes the same
    number of entries off the bottom. compare_runs already treats the entrance
    as benign (SET_ADDED); calling the eviction it causes a blocking failure
    scores one event twice, in opposite directions.

    Only the tail may be evicted. `cut` is the number of slots that survive N
    insertions, so a loss from at or below it is arithmetic and a loss from
    above it is a real drop that stays SET_LOST. A short after-list is also a
    real drop: fewer results came back than went in, so nothing was displaced.
    """
    if not added or len(a_sids) < len(b_sids):
        return False
    cut = len(b_sids) - len(added)
    lost_positions = [i for i, sid in enumerate(b_sids) if sid not in a_sids]
    return bool(lost_positions) and all(i >= cut for i in lost_positions)


def compare_runs(before: dict, after: dict) -> dict:
    """Diff two run files. Pure — takes parsed dicts, returns a report dict."""
    tie_map = build_tie_map(before.get("tie_aliases") or [])
    b_by_id = {q["id"]: q for q in before["results"]}
    a_by_id = {q["id"]: q for q in after["results"]}

    rows, failures = [], 0
    for qid in sorted(set(b_by_id) | set(a_by_id)):
        b, a = b_by_id.get(qid), a_by_id.get(qid)
        if b is None or a is None:
            rows.append({"id": qid, "status": "ONLY_IN_ONE_RUN",
                         "detail": "before" if a is None else "after"})
            continue
        if b.get("error") or a.get("error"):
            rows.append({"id": qid, "status": "ERROR",
                         "detail": a.get("error") or b.get("error")})
            failures += 1
            continue

        b_sids = [canon(s, tie_map) for s in b["source_ids"]]
        a_sids = [canon(s, tie_map) for s in a["source_ids"]]
        lost = [s for s in b_sids if s not in a_sids]
        added = [s for s in a_sids if s not in b_sids]

        if b["verdict"] == "PASS" and a["verdict"] == "FAIL":
            status = "VERDICT_REGRESSED"
        elif b["verdict"] == "FAIL" and a["verdict"] == "PASS":
            status = "VERDICT_FIXED"
        elif lost:
            # S210 — a tail eviction caused by a new entrant is the arithmetic
            # consequence of an ingest, not a retrieval loss. See
            # _is_displacement() for why this is not scored as a failure.
            status = "DISPLACED" if _is_displacement(b_sids, a_sids, added) else "SET_LOST"
        elif added:
            status = "SET_ADDED"
        elif b_sids != a_sids:
            status = "RANK_SHIFT"
        else:
            moved = max(
                (abs(x - y) for x, y in zip(b["scores"], a["scores"])), default=0.0
            )
            status = "SAME" if moved <= SCORE_EPSILON else "SCORE_MOVED"

        # S212 — the chunk layer is judged INDEPENDENTLY of the source layer, and
        # on purpose. A query can be SAME at source level while the passage that
        # actually answers it drops out of the window: same documents, different
        # chunks. That is the exact blind spot the source-level assertions had, so
        # folding this into `status` would re-create it.
        bc, ac = b.get("chunk_verdict"), a.get("chunk_verdict")
        if bc == "PASS" and ac == "FAIL":
            chunk_status = "CHUNK_REGRESSED"
        elif bc == "FAIL" and ac == "PASS":
            chunk_status = "CHUNK_FIXED"
        elif bc == "PASS" and ac == "PASS" and \
                b.get("rank_of_expected_chunk") != a.get("rank_of_expected_chunk"):
            chunk_status = "CHUNK_RANK_SHIFT"
        elif bc is None and ac is None:
            chunk_status = "CHUNK_UNRECORDED"  # run file predates S212
        else:
            chunk_status = "CHUNK_SAME"

        if status in ("VERDICT_REGRESSED", "SET_LOST") or \
                chunk_status == "CHUNK_REGRESSED":
            failures += 1
        rows.append({
            "id": qid, "status": status,
            "before": b_sids, "after": a_sids,
            "lost": lost, "added": added,
            "before_verdict": b["verdict"], "after_verdict": a["verdict"],
            "chunk_status": chunk_status,
            "before_chunk_rank": b.get("rank_of_expected_chunk"),
            "after_chunk_rank": a.get("rank_of_expected_chunk"),
        })

    return {"rows": rows, "failures": failures,
            "before_label": before.get("label"), "after_label": after.get("label")}


# ---------------------------------------------------------------------------
# network
# ---------------------------------------------------------------------------


def query_once(endpoint: str, query: str, top_k: int) -> dict:
    """One POST. Retries 429/5xx with backoff. Raises on final failure."""
    body = json.dumps({"query": query, "top_k": top_k,
                       "synthesize": False}).encode("utf-8")
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = urllib.request.Request(
            endpoint, data=body,
            headers={"Content-Type": "application/json",
                         # S204: served normally but NOT counted by the usage counter —
                         # this harness fires dozens of live queries per run.
                         "x-probe": "1"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            # 429 = throttled, 5xx = transient. Neither is "no results".
            if e.code in (429, 500, 502, 503, 504) and attempt < MAX_ATTEMPTS:
                time.sleep(DEFAULT_PACE_S * attempt * 2)
                continue
            raise RuntimeError(f"{last}: {e.read()[:200]!r}") from e
        except (OSError, http.client.HTTPException) as e:
            # S207: the earlier `(URLError, TimeoutError)` clause let a bare
            # ConnectionResetError from the TLS read escape and kill the whole run
            # mid-set, losing every query already paid for. Render's free tier drops
            # idle connections, so this is routine, not exceptional. OSError covers
            # URLError/TimeoutError/ConnectionReset alike; HTTPError is caught above.
            last = f"network {type(e).__name__}: {e}"
            if attempt < MAX_ATTEMPTS:
                time.sleep(DEFAULT_PACE_S * attempt)
                continue
            raise RuntimeError(last) from e
    raise RuntimeError(last or "unreachable")


def run_set(endpoint: str, top_k: int, pace: float, limit: int | None,
            label: str) -> dict:
    queries, tie_aliases = load_query_set()
    tie_map = build_tie_map(tie_aliases)
    if limit:
        queries = queries[:limit]

    out_rows, errors = [], 0
    for i, q in enumerate(queries, 1):
        if i > 1:
            time.sleep(pace)
        try:
            resp = query_once(endpoint, q["query"], top_k)
        except RuntimeError as e:
            print(f"  [{i}/{len(queries)}] {q['id']:<16} ERROR {e}", file=sys.stderr)
            out_rows.append({**{k: q[k] for k in ("id", "query", "note")},
                             "error": str(e)})
            errors += 1
            continue

        if resp.get("degraded"):
            # Real Channel B failure surfaced by the S117 discriminator — an
            # infra fault, not a retrieval result. Do not record it as empty.
            detail = f"degraded:{resp.get('degraded_kind')} {resp.get('reason')}"
            print(f"  [{i}/{len(queries)}] {q['id']:<16} {detail}", file=sys.stderr)
            out_rows.append({**{k: q[k] for k in ("id", "query", "note")},
                             "error": detail})
            errors += 1
            continue

        results = resp.get("results") or []
        sids = [r["source_id"] for r in results]
        verdict, rank = verdict_for(sids, q["expect_any"], tie_map)
        # S212 — chunk layer. chunk_ids are recorded for EVERY query, asserted or
        # not: source-level rows cannot answer "did the right passage enter the
        # window", and a run file without them cannot be re-asked that question
        # later. Recording is cheap; re-running the whole set is not.
        expect_text = q.get("expect_text_any") or []
        within = int(q.get("chunk_within", DEFAULT_CHUNK_WITHIN))
        c_verdict, c_rank = chunk_verdict_for(results, expect_text, within)
        out_rows.append({
            "id": q["id"], "query": q["query"], "note": q["note"],
            "expect_any": q["expect_any"],
            "verdict": verdict, "rank_of_expected": rank,
            "source_ids": sids,
            "chunk_ids": [r.get("id") for r in results],
            "expect_text_any": expect_text,
            "chunk_within": within,
            "chunk_verdict": c_verdict, "rank_of_expected_chunk": c_rank,
            "scores": [round(float(r["score"]), 4) for r in results],
            "content_types": [r.get("content_type") for r in results],
            "pages": [r.get("page") for r in results],
            "total": resp.get("total", len(results)),
        })
        flag = {"PASS": "✅", "FAIL": "❌", "RECORD_ONLY": "·"}[verdict]
        cflag = {"PASS": " chunk✅", "FAIL": " chunk❌", "RECORD_ONLY": ""}[c_verdict]
        top = f"{sids[0]}@{results[0]['score']:.3f}" if results else "(0 results)"
        print(f"  [{i}/{len(queries)}] {flag} {q['id']:<16} rank={rank} top={top}{cflag}")

    counts = {v: sum(1 for r in out_rows if r.get("verdict") == v)
              for v in ("PASS", "FAIL", "RECORD_ONLY")}
    chunk_counts = {f"chunk_{v}": sum(1 for r in out_rows
                                      if r.get("chunk_verdict") == v)
                    for v in ("PASS", "FAIL")}
    return {
        "label": label,
        "endpoint": endpoint,
        "top_k": top_k,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tie_aliases": tie_aliases,
        "summary": {**counts, **chunk_counts,
                    "errors": errors, "queries": len(out_rows)},
        "results": out_rows,
    }


# ---------------------------------------------------------------------------
# self-test (offline, no network)
# ---------------------------------------------------------------------------


def self_test() -> int:
    fails = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    tie_map = build_tie_map([["g24", "sag_2025_11"]])
    check("tie map collapses both ids to one canonical",
          tie_map["g24"] == tie_map["sag_2025_11"] == "g24|sag_2025_11")
    check("non-tie id passes through", canon("edbcm113_2026", tie_map) == "edbcm113_2026")

    check("verdict PASS at rank 0",
          verdict_for(["a", "b"], ["a"], {}) == ("PASS", 0))
    check("verdict PASS at rank 2 (any-of)",
          verdict_for(["x", "y", "b"], ["a", "b"], {}) == ("PASS", 2))
    check("verdict FAIL when absent",
          verdict_for(["x"], ["a"], {}) == ("FAIL", None))
    check("empty expect_any = RECORD_ONLY",
          verdict_for(["x"], [], {}) == ("RECORD_ONLY", None))
    check("tie alias satisfies expectation via the other id",
          verdict_for(["sag_2025_11"], ["g24"], tie_map) == ("PASS", 0))

    # ---- S212 chunk layer ------------------------------------------------
    def cr(text):
        return {"id": "x", "text": text}

    check("squeeze strips the PDF line break that fooled S211",
          squeeze("新 入\n職 教師") == "新入職教師")
    check("chunk PASS at rank 0",
          chunk_verdict_for([cr("開辦12班的教學人員編制")], ["開辦12班的教學人員編制"])
          == ("PASS", 0))
    check("chunk signature matches THROUGH extractor whitespace (the real case)",
          chunk_verdict_for([cr("核准開辦12 班的教學\n人員編制：校長1 名")],
                            ["開辦12班的教學人員編制"]) == ("PASS", 0))
    check("chunk FAIL when the signature is absent",
          chunk_verdict_for([cr("完全無關嘅內容")], ["開辦12班"]) == ("FAIL", None))
    check("empty expect_text_any = RECORD_ONLY",
          chunk_verdict_for([cr("任何嘢")], []) == ("RECORD_ONLY", None))
    # PROVES THE GATE GOES RED: present, but outside the window it is asked about.
    check("chunk FAIL when present only BELOW the window (window is enforced)",
          chunk_verdict_for([cr("a"), cr("b"), cr("c"), cr("d"), cr("e"),
                             cr("開辦12班的教學人員編制")], ["開辦12班"], within=5)
          == ("FAIL", None))
    check("same chunk INSIDE a widened window passes (the window is the only reason)",
          chunk_verdict_for([cr("a"), cr("b"), cr("c"), cr("d"), cr("e"),
                             cr("開辦12班的教學人員編制")], ["開辦12班"], within=6)
          == ("PASS", 5))
    check("a wrong-row signature does NOT satisfy a right-row assertion",
          chunk_verdict_for([cr("核准開辦24 班的教學人員編制")],
                            ["開辦12班的教學人員編制"]) == ("FAIL", None))

    def mk(label, rows):
        return {"label": label, "tie_aliases": [["g24", "sag_2025_11"]], "results": rows}

    def row(qid, sids, verdict="PASS", scores=None):
        return {"id": qid, "source_ids": sids, "verdict": verdict,
                "scores": scores if scores is not None else [0.7] * len(sids)}

    rep = compare_runs(mk("b", [row("q1", ["a", "b"])]), mk("a", [row("q1", ["a", "b"])]))
    check("identical run = SAME, 0 failures",
          rep["rows"][0]["status"] == "SAME" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["g24", "x"])]),
                       mk("a", [row("q1", ["sag_2025_11", "x"])]))
    check("tie flip is SAME, not a regression",
          rep["rows"][0]["status"] == "SAME" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a", "b"])]), mk("a", [row("q1", ["b", "a"])]))
    check("reordering = RANK_SHIFT and does NOT fail",
          rep["rows"][0]["status"] == "RANK_SHIFT" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a", "b"])]), mk("a", [row("q1", ["a"])]))
    check("a dropped source = SET_LOST and FAILS",
          rep["rows"][0]["status"] == "SET_LOST" and rep["failures"] == 1)

    rep = compare_runs(mk("b", [row("q1", ["a"])]), mk("a", [row("q1", ["a", "new"])]))
    check("a newly surfaced source = SET_ADDED and does NOT fail",
          rep["rows"][0]["status"] == "SET_ADDED" and rep["failures"] == 0)

    # S210 DISPLACED — and, per discipline #11, proof the gate still goes red.
    rep = compare_runs(mk("b", [row("q1", ["a", "b", "c", "tail"])]),
                       mk("a", [row("q1", ["a", "new", "b", "c"])]))
    check("tail eviction by a new entrant = DISPLACED and does NOT fail",
          rep["rows"][0]["status"] == "DISPLACED" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a", "gone", "c", "d"])]),
                       mk("a", [row("q1", ["a", "new", "c", "d"])]))
    check("a loss from ABOVE the cut line stays SET_LOST and FAILS",
          rep["rows"][0]["status"] == "SET_LOST" and rep["failures"] == 1)

    rep = compare_runs(mk("b", [row("q1", ["a", "b", "c", "tail"])]),
                       mk("a", [row("q1", ["a", "new", "b"])]))
    check("a shorter after-list is a real drop, not displacement",
          rep["rows"][0]["status"] == "SET_LOST" and rep["failures"] == 1)

    rep = compare_runs(mk("b", [row("q1", ["a", "b", "t1", "t2"])]),
                       mk("a", [row("q1", ["n1", "n2", "a", "b"])]))
    check("two entrants evict exactly two tail slots = DISPLACED",
          rep["rows"][0]["status"] == "DISPLACED" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a"], "PASS")]),
                       mk("a", [row("q1", ["a"], "FAIL")]))
    check("PASS→FAIL = VERDICT_REGRESSED and FAILS",
          rep["rows"][0]["status"] == "VERDICT_REGRESSED" and rep["failures"] == 1)

    rep = compare_runs(mk("b", [row("q1", ["a"], "FAIL")]),
                       mk("a", [row("q1", ["a"], "PASS")]))
    check("FAIL→PASS = VERDICT_FIXED and does NOT fail",
          rep["rows"][0]["status"] == "VERDICT_FIXED" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a"], "PASS", [0.700])]),
                       mk("a", [row("q1", ["a"], "PASS", [0.7005])]))
    check("sub-epsilon score jitter = SAME",
          rep["rows"][0]["status"] == "SAME")

    rep = compare_runs(mk("b", [row("q1", ["a"], "PASS", [0.700])]),
                       mk("a", [row("q1", ["a"], "PASS", [0.760])]))
    check("score move beyond epsilon = SCORE_MOVED (reported, not a failure)",
          rep["rows"][0]["status"] == "SCORE_MOVED" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [{"id": "q1", "error": "HTTP 429"}]),
                       mk("a", [row("q1", ["a"])]))
    check("an errored query FAILS the compare (never read as empty)",
          rep["rows"][0]["status"] == "ERROR" and rep["failures"] == 1)

    def crow(qid, sids, cverdict, crank, verdict="PASS"):
        return {"id": qid, "source_ids": sids, "verdict": verdict,
                "scores": [0.7] * len(sids),
                "chunk_verdict": cverdict, "rank_of_expected_chunk": crank}

    # THE WHOLE POINT: identical sources, and the right passage still fell out.
    rep = compare_runs(mk("b", [crow("q1", ["a", "b"], "PASS", 0)]),
                       mk("a", [crow("q1", ["a", "b"], "FAIL", None)]))
    check("chunk regression FAILS even when the source list is identical",
          rep["rows"][0]["status"] == "SAME"
          and rep["rows"][0]["chunk_status"] == "CHUNK_REGRESSED"
          and rep["failures"] == 1)

    rep = compare_runs(mk("b", [crow("q1", ["a"], "FAIL", None)]),
                       mk("a", [crow("q1", ["a"], "PASS", 0)]))
    check("chunk fix is reported and does NOT fail",
          rep["rows"][0]["chunk_status"] == "CHUNK_FIXED" and rep["failures"] == 0)

    rep = compare_runs(mk("b", [crow("q1", ["a"], "PASS", 0)]),
                       mk("a", [crow("q1", ["a"], "PASS", 3)]))
    check("chunk rank move is reported and does NOT fail",
          rep["rows"][0]["chunk_status"] == "CHUNK_RANK_SHIFT"
          and rep["failures"] == 0)

    rep = compare_runs(mk("b", [row("q1", ["a"])]), mk("a", [row("q1", ["a"])]))
    check("a pre-S212 run file compares as CHUNK_UNRECORDED, not as a pass",
          rep["rows"][0]["chunk_status"] == "CHUNK_UNRECORDED")

    queries, aliases = load_query_set()
    check("query set loads and is non-trivial", len(queries) >= 20)
    check("every query has id/query/expect_any/note",
          all(all(k in q for k in ("id", "query", "expect_any", "note")) for q in queries))
    check("query ids are unique", len({q["id"] for q in queries}) == len(queries))
    check("tie aliases declared in the query file", aliases == [["g24", "sag_2025_11"]])
    chunk_qs = [q for q in queries if q.get("expect_text_any")]
    check(f"at least one chunk-layer assertion exists (S212); found {len(chunk_qs)}",
          len(chunk_qs) >= 1)
    check("every chunk assertion also names the source it must come from",
          all(q.get("expect_any") for q in chunk_qs))
    short = [q["id"] for q in queries if len(q["query"]) > 14]
    check(f"queries stay short (S183 rule 4); long ones: {short}", not short)

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


# ---------------------------------------------------------------------------


def print_compare(rep: dict) -> None:
    order = ["VERDICT_REGRESSED", "SET_LOST", "ERROR", "VERDICT_FIXED",
             "DISPLACED", "SET_ADDED", "RANK_SHIFT", "SCORE_MOVED", "SAME",
             "ONLY_IN_ONE_RUN"]
    by_status: dict[str, list[dict]] = {}
    for r in rep["rows"]:
        by_status.setdefault(r["status"], []).append(r)

    print(f"\ncompare: {rep['before_label']} → {rep['after_label']}")
    for status in order:
        rows = by_status.get(status)
        if not rows:
            continue
        print(f"\n{status}  ({len(rows)})")
        for r in rows:
            if status == "SAME":
                print(f"  · {r['id']}")
            elif status == "ERROR":
                print(f"  ! {r['id']}: {r.get('detail')}")
            elif status == "ONLY_IN_ONE_RUN":
                print(f"  ? {r['id']}: only in {r.get('detail')}")
            else:
                bits = []
                if r.get("lost"):
                    bits.append(f"lost={r['lost']}")
                if r.get("added"):
                    bits.append(f"added={r['added']}")
                if r["before_verdict"] != r["after_verdict"]:
                    bits.append(f"{r['before_verdict']}→{r['after_verdict']}")
                print(f"  • {r['id']}: {' '.join(bits) or 'order changed'}")
                print(f"      before {r['before']}")
                print(f"      after  {r['after']}")
    # S212 — chunk layer printed as its own block. A CHUNK_REGRESSED row may sit
    # under SAME above (same sources, different passage), so it must be visible
    # here or the one thing the source layer could not see stays invisible.
    chunk_order = ["CHUNK_REGRESSED", "CHUNK_FIXED", "CHUNK_RANK_SHIFT"]
    by_chunk: dict[str, list[dict]] = {}
    for r in rep["rows"]:
        cs = r.get("chunk_status")
        if cs in chunk_order:
            by_chunk.setdefault(cs, []).append(r)
    if by_chunk:
        print("\n--- chunk layer (S212) ---")
        for cs in chunk_order:
            for r in by_chunk.get(cs, []):
                print(f"  {cs}  {r['id']}: "
                      f"rank {r.get('before_chunk_rank')} → {r.get('after_chunk_rank')}"
                      f"  (source status: {r['status']})")

    print(f"\nblocking failures: {rep['failures']}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true", help="offline assertions only")
    p.add_argument("--run", action="store_true", help="run the query set (network)")
    p.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    p.add_argument("--out", help="write the run to this JSON path")
    p.add_argument("--label", default="", help="label stored in the run file")
    p.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    p.add_argument("--top-k", type=int, default=8)
    p.add_argument("--pace", type=float, default=DEFAULT_PACE_S,
                   help=f"seconds between calls (default {DEFAULT_PACE_S}; POST limiter is 10/min)")
    p.add_argument("--limit", type=int, help="only the first N queries")
    args = p.parse_args()

    if args.self_test:
        return self_test()

    if args.compare:
        before = json.loads(Path(args.compare[0]).read_text(encoding="utf-8"))
        after = json.loads(Path(args.compare[1]).read_text(encoding="utf-8"))
        rep = compare_runs(before, after)
        print_compare(rep)
        return 1 if rep["failures"] else 0

    if args.run:
        label = args.label or time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
        print(f"running {args.endpoint}  top_k={args.top_k}  pace={args.pace}s")
        run = run_set(args.endpoint, args.top_k, args.pace, args.limit, label)
        s = run["summary"]
        scores = [x for r in run["results"] for x in r.get("scores", [])]
        print(f"\nsummary: PASS={s['PASS']} FAIL={s['FAIL']} "
              f"RECORD_ONLY={s['RECORD_ONLY']} errors={s['errors']} "
              f"(median score {statistics.median(scores):.3f})" if scores else "")
        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(run, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
            print(f"wrote {out.relative_to(REPO_ROOT) if out.is_absolute() else out}")
        return 1 if s["errors"] else 0

    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
