#!/usr/bin/env python3
"""
Option 2 — one round of checking the retired Channel A queue against the corpus
with Jev (S244; rule 2 of dev/knowledge/channel_a_option2_queue.json _meta.rules).

Three stages, each separately runnable, so nothing reaches the queue file
without a person reading the round report first:

  1. --retrieve   For every fact still in the queue: embed (cached, shared with
                  channel_a_coverage.py) → match_wiki_chunks → keep the top-K
                  passages that carry a real source (vault_extract /
                  footnote_curated; approved_fact mirrors would match
                  themselves). Read-only. Writes <round>/candidates.json.
  2. --judge      Per fact, ask Jev (dev/source/jev/channel_a_match_gate.json)
                  about each candidate in rank order, stopping at the first
                  candidate that settles the fact (resolved or dropped). Every
                  Jev call is an external call: --limit / --offset / --sample
                  bound it, and --dry-run prints the call count without calling.
                  Results append to <round>/judgements.jsonl (resumable).
  3. --apply      Writes resolved / dropped into the queue file and removes
                  those facts. Refuses unless --approved is given (Leonard's
                  approval of the round report) and every fact in the round has
                  a judgement.

Triage (rule 2, probabilities only — never the Jev verdict summary, which the
gate's _meta.note says misreports):
  same_rule ≥ 0.70 and role_match ≥ 0.70 and contradicts ≤ 0.30 → RESOLVED
  same_matter ≥ 0.70 and contradicts ≥ 0.70                    → DROPPED
  (same_matter added S244: a 2023 questionnaire fact was dropped against a
  different 2026 questionnaire passage — same kind, different matter)
  anything else, a missing passage, or a transport error       → MANUAL

A fact is RESOLVED if any candidate resolves it. It is DROPPED only if no
candidate resolves it and at least one contradicts it. A failed call is never
evidence of anything: it makes the fact MANUAL with the error attached.

Usage:
  python3 dev/source/channel_a_jev_round.py --self-test
  python3 dev/source/channel_a_jev_round.py --round r1 --retrieve
  python3 dev/source/channel_a_jev_round.py --round r1 --judge --sample 20 --dry-run
  python3 dev/source/channel_a_jev_round.py --round r1 --judge --sample 20
  python3 dev/source/channel_a_jev_round.py --round r1 --report
  python3 dev/source/channel_a_jev_round.py --round r1 --apply --approved "<Leonard 原話>"
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel_a_coverage as cov  # noqa: E402  (retrieval + embed cache, S197)

QUEUE = ROOT / "dev" / "knowledge" / "channel_a_option2_queue.json"
GATE = ROOT / "dev" / "source" / "jev" / "channel_a_match_gate.json"
JEV = Path.home() / ".claude" / "skills" / "jev-decide" / "scripts" / "jev.py"
RUNS = ROOT / "dev" / "source" / "coverage_runs" / "option2"

YES, NO = 0.70, 0.30
TOP_K = 3                 # candidates judged per fact (at most)
PASSAGE_MAX = 2500        # chars of passage text sent to Jev


# ── pure logic (self-tested) ────────────────────────────────────────────────

PAGE_RE = re.compile(r"={2,}\s*Page\s*(\d+)\s*={2,}", re.I)


def dominant_page(raw: str) -> int | None:
    """Python port of extractDominantPage (backend/src/api/searchChannelB.ts).

    The page holding the largest share of the chunk's text; text before the
    first marker belongs to the previous page; ties go to the earlier page.
    """
    marks = [(int(m.group(1)), m.start(), m.end()) for m in PAGE_RE.finditer(raw)]
    if not marks:
        return None
    weight: dict[int, int] = {}

    def add(page: int, text: str) -> None:
        n = len(re.sub(r"\s+", "", text))
        if n > 0:
            weight[page] = weight.get(page, 0) + n

    add(max(1, marks[0][0] - 1), raw[:marks[0][1]])
    for i, (page, _s, end) in enumerate(marks):
        nxt = marks[i + 1][1] if i + 1 < len(marks) else len(raw)
        add(page, raw[end:nxt])
    best, best_len = None, -1
    for page, n in weight.items():           # dict keeps insertion order
        if n > best_len:
            best, best_len = page, n
    return best


def clean(raw: str) -> str:
    return re.sub(r"\s+", " ", PAGE_RE.sub(" ", raw)).strip()


def triage_pair(probs: dict) -> str:
    s, r, c = probs.get("same_rule"), probs.get("role_match"), probs.get("contradicts")
    if None in (s, r, c):
        return "MANUAL"
    if s >= YES and r >= YES and c <= NO:
        return "RESOLVED"
    m = probs.get("same_matter")
    if m is not None and m >= YES and c >= YES:
        return "DROPPED"
    return "MANUAL"


def triage_fact(pairs: list[dict]) -> tuple[str, dict | None]:
    """pairs: [{'outcome': ..., ...}] in rank order. Returns (outcome, deciding pair)."""
    for p in pairs:
        if p["outcome"] == "RESOLVED":
            return "RESOLVED", p
    for p in pairs:
        if p["outcome"] == "DROPPED":
            return "DROPPED", p
    return "MANUAL", None


def fact_key(f: dict) -> str:
    return f"{f['topic']}/{f['role']}/{f['text']}"


def jev_probs(out: dict) -> dict:
    probs = {}
    for qid, a in (out.get("answers") or {}).items():
        if isinstance(a, dict) and "noul" in a:
            probs[qid] = round(float(a["noul"]), 4)
    return probs


# ── stage 1: retrieve ───────────────────────────────────────────────────────

def retrieve(rnd: Path) -> int:
    okey, skey = os.environ.get("OPENAI_API_KEY"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not skey:
        sys.exit("need SUPABASE_SERVICE_KEY (and OPENAI_API_KEY for uncached facts)")
    facts = cov.load_facts(QUEUE)
    cache = json.loads(cov.CACHE.read_text(encoding="utf-8")) if cov.CACHE.exists() else {}
    miss = [f for f in facts if f["text"] not in cache]
    if miss and not okey:
        sys.exit(f"{len(miss)} facts not in embed cache and no OPENAI_API_KEY")
    print(f"facts {len(facts)} · embed cache miss {len(miss)} (= OpenAI embedding calls)")
    out, errors = [], 0
    for n, f in enumerate(facts, 1):
        rec = {**f, "key": fact_key(f)}
        try:
            vec = cache.get(f["text"])
            if vec is None:
                vec = cov.embed(f["text"], okey)
                cache[f["text"]] = vec
            body = {"query_embedding": "[" + ",".join(f"{x:.8f}" for x in vec) + "]",
                    "match_threshold": 0.1, "match_count": cov.MATCH_COUNT}
            hdr = {"apikey": skey, "Authorization": "Bearer " + skey,
                   "Content-Type": "application/json"}
            rows = cov.with_retry(lambda: cov._post(cov.RPC, body, hdr, 120))
            keep = [r for r in rows if r.get("content_type") in cov.CORPUS_TYPES][:TOP_K]
            rec["candidates"] = [{
                "chunk_id": r.get("id"), "source_id": r.get("source_id"),
                "title": r.get("title") or "", "url": r.get("url") or "",
                "page": dominant_page(r.get("text") or ""),
                "score": round(r.get("score") or 0, 4),
                "content_type": r.get("content_type"),
                "text": clean(r.get("text") or ""),
            } for r in keep]
        except cov.Transient as e:
            rec["candidates"], rec["error"] = [], str(e)
            errors += 1
        out.append(rec)
        if n % 50 == 0:
            print(f"  {n}/{len(facts)}")
        time.sleep(0.2)
    if miss:
        cov.CACHE.write_text(json.dumps(cache), encoding="utf-8")
    assert len(out) == len(facts), "conservation"
    rnd.mkdir(parents=True, exist_ok=True)
    (rnd / "candidates.json").write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "queue_facts": len(facts), "top_k": TOP_K, "errors": errors,
        "records": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    nocand = sum(1 for r in out if not r["candidates"])
    print(f"wrote {rnd/'candidates.json'} · errors {errors} · facts with no candidate {nocand}")
    return 0


# ── stage 2: judge ──────────────────────────────────────────────────────────

def ask_jev(fact: dict, cand: dict) -> dict:
    state = {
        "fact": {"text": fact["text"], "topic": fact["topic"], "role": fact["role"]},
        "passage": {"source_id": cand["source_id"], "title": cand["title"],
                    "page": cand["page"], "text": cand["text"][:PASSAGE_MAX]},
    }
    r = subprocess.run([sys.executable, str(JEV), "--questions", str(GATE),
                        "--state-file", "-", "--json"],
                       input=json.dumps(state, ensure_ascii=False),
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return {"error": (r.stderr or r.stdout)[-300:]}
    try:
        out = json.loads(r.stdout[r.stdout.index("{"):])
    except ValueError:
        return {"error": "unparseable jev output: " + r.stdout[-200:]}
    return {"probs": jev_probs(out), "usage": out.get("usage", {})}


def load_judged(rnd: Path) -> dict:
    p = rnd / "judgements.jsonl"
    done = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                j = json.loads(line)
                done[j["key"]] = j
    return done


def pick(records: list[dict], offset: int, limit: int | None, sample: int | None,
         seed: int) -> list[dict]:
    if sample:
        rng = random.Random(seed)
        return rng.sample(records, min(sample, len(records)))
    sel = records[offset:]
    return sel[:limit] if limit else sel


def judge(rnd: Path, offset: int, limit: int | None, sample: int | None, seed: int,
          dry: bool, pace: float) -> int:
    cand = json.loads((rnd / "candidates.json").read_text(encoding="utf-8"))
    done = load_judged(rnd)
    todo = [r for r in pick(cand["records"], offset, limit, sample, seed) if r["key"] not in done]
    upper = sum(len(r["candidates"]) for r in todo)
    print(f"facts to judge {len(todo)} (already judged {len(done)}) · "
          f"Jev calls at most {upper} (stops early per fact once settled)")
    if dry:
        return 0
    calls, t0 = 0, time.time()
    with (rnd / "judgements.jsonl").open("a", encoding="utf-8") as fh:
        for n, r in enumerate(todo, 1):
            pairs = []
            for i, c in enumerate(r["candidates"]):
                res = ask_jev(r, c)
                calls += 1
                pair = {"rank": i, "chunk_id": c["chunk_id"], "source_id": c["source_id"],
                        "page": c["page"], "url": c["url"], "score": c["score"]}
                if "error" in res:
                    pair.update(outcome="MANUAL", error=res["error"])
                else:
                    pair.update(outcome=triage_pair(res["probs"]), probs=res["probs"])
                pairs.append(pair)
                time.sleep(pace)
                if pair["outcome"] in ("RESOLVED", "DROPPED"):
                    break
            outcome, by = triage_fact(pairs)
            if not r["candidates"]:
                reason = "no candidate passage" + (f" ({r['error']})" if r.get("error") else "")
            else:
                reason = ""
            rec = {"key": r["key"], "topic": r["topic"], "role": r["role"], "text": r["text"],
                   "outcome": outcome, "by": by, "pairs": pairs, "note": reason,
                   "judged": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            mark = {"RESOLVED": "✅", "DROPPED": "✖", "MANUAL": "·"}[outcome]
            print(f"  [{n}/{len(todo)}] {mark} {outcome:<8} {r['text'][:36]}")
    print(f"Jev calls {calls} · {time.time()-t0:.0f}s")
    return report(rnd)


# ── report ──────────────────────────────────────────────────────────────────

def report(rnd: Path) -> int:
    done = load_judged(rnd)
    cand = json.loads((rnd / "candidates.json").read_text(encoding="utf-8"))
    total = len(cand["records"])
    tally = {"RESOLVED": 0, "DROPPED": 0, "MANUAL": 0}
    errs = 0
    for j in done.values():
        tally[j["outcome"]] += 1
        errs += any("error" in p for p in j["pairs"])
    print(f"\nround {rnd.name}: judged {len(done)}/{total} · " +
          " · ".join(f"{k} {v}" for k, v in tally.items()) + f" · facts with a call error {errs}")
    for kind in ("RESOLVED", "DROPPED"):
        rows = [j for j in done.values() if j["outcome"] == kind]
        if rows:
            print(f"\n── {kind} ({len(rows)}) — read each before approving ──")
        for j in rows:
            b = j["by"]
            print(f"  • {j['text']}\n    → {b['source_id']} p.{b['page']}  {b['probs']}")
    return 0


# ── stage 3: apply ──────────────────────────────────────────────────────────

def apply(rnd: Path, approved: str | None, session: str) -> int:
    if not approved:
        sys.exit("refusing: --apply needs --approved \"<Leonard's approval wording>\"")
    cand = json.loads((rnd / "candidates.json").read_text(encoding="utf-8"))
    done = load_judged(rnd)
    missing = [r["key"] for r in cand["records"] if r["key"] not in done]
    if missing:
        sys.exit(f"refusing: {len(missing)} facts in this round have no judgement")
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    before = sum(len(v) for t, tv in q.items() if t != "_meta"
                 for k, v in tv.items() if not k.startswith("_") and isinstance(v, list))
    removed = 0
    for j in done.values():
        if j["outcome"] not in ("RESOLVED", "DROPPED"):
            continue
        lst = q[j["topic"]][j["role"]]
        if j["text"] not in lst:
            continue                         # already applied in an earlier run
        lst.remove(j["text"])
        b = j["by"]
        entry = {"fact": j["text"], "topic": j["topic"], "role": j["role"],
                 "source_id": b["source_id"], "page": b["page"], "url": b["url"],
                 "chunk_id": b["chunk_id"], "jev": b["probs"], "session": session,
                 "round": rnd.name, "approved": approved}
        if j["outcome"] == "DROPPED":
            entry["reason"] = "與現行原文矛盾（Jev same_matter 與 contradicts 皆 ≥ 0.70）"
            q["_meta"]["dropped"].append(entry)
        else:
            q["_meta"]["resolved"].append(entry)
        removed += 1
    after = before - removed
    q["_meta"]["facts_remaining"] = after
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"queue {before} → {after} (removed {removed})")
    return 0


# ── self-test ───────────────────────────────────────────────────────────────

def self_test() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("  PASS  " if cond else "  FAIL  ") + name)

    check("resolve", triage_pair({"same_rule": .9, "role_match": .8, "contradicts": .1}) == "RESOLVED")
    check("resolve edge", triage_pair({"same_rule": .7, "role_match": .7, "contradicts": .3}) == "RESOLVED")
    check("role blocks", triage_pair({"same_rule": .9, "role_match": .5, "contradicts": .1}) == "MANUAL")
    check("contradict mid blocks", triage_pair({"same_rule": .9, "role_match": .9, "contradicts": .4}) == "MANUAL")
    check("drop", triage_pair({"same_matter": .9, "same_rule": .1, "role_match": .9, "contradicts": .8}) == "DROPPED")
    check("drop needs same_matter", triage_pair({"same_matter": .2, "same_rule": .01, "role_match": .9, "contradicts": .91}) == "MANUAL")
    check("drop missing same_matter → manual", triage_pair({"same_rule": .1, "role_match": .9, "contradicts": .8}) == "MANUAL")
    check("S243 pilot → manual", triage_pair({"same_rule": .03, "role_match": .89, "contradicts": .56}) == "MANUAL")
    check("missing prob → manual", triage_pair({"same_rule": .9, "role_match": .9}) == "MANUAL")
    check("fact: resolve beats drop", triage_fact([{"outcome": "DROPPED"}, {"outcome": "RESOLVED"}])[0] == "RESOLVED")
    check("fact: drop if no resolve", triage_fact([{"outcome": "MANUAL"}, {"outcome": "DROPPED"}])[0] == "DROPPED")
    check("fact: empty → manual", triage_fact([])[0] == "MANUAL")
    check("fact: error pair → manual", triage_fact([{"outcome": "MANUAL", "error": "x"}])[0] == "MANUAL")
    check("jev noul parse", jev_probs({"answers": {"same_rule": {"type": "noul", "noul": 0.91}}}) == {"same_rule": 0.91})
    # dominant page — same cases as the backend doc comment
    check("page none", dominant_page("no markers") is None)
    check("page tail marker", dominant_page("=== Page 53 ===" + "甲" * 96 + "=== Page 54 ===乙") == 53)
    check("page pre-text → previous", dominant_page("甲" * 50 + "=== Page 8 ===乙") == 7)
    check("page tie → earlier", dominant_page("=== Page 3 ===甲乙=== Page 4 ===丙丁") == 3)
    check("clean strips markers", "Page" not in clean("a === Page 2 === b"))
    # conservation of the queue loader
    facts = cov.load_facts(QUEUE)
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    check("queue count == facts_remaining", len(facts) == q["_meta"]["facts_remaining"])
    check("fact keys unique", len({fact_key(f) for f in facts}) == len(facts))
    print("ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--round", default="r1")
    ap.add_argument("--retrieve", action="store_true")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--approved")
    ap.add_argument("--session", default="S244")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--sample", type=int)
    ap.add_argument("--seed", type=int, default=244)
    ap.add_argument("--pace", type=float, default=0.5)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    rnd = RUNS / a.round
    if a.retrieve:
        return retrieve(rnd)
    if a.judge:
        return judge(rnd, a.offset, a.limit, a.sample, a.seed, a.dry_run, a.pace)
    if a.report:
        return report(rnd)
    if a.apply:
        return apply(rnd, a.approved, a.session)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
