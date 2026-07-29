#!/usr/bin/env python3
"""
S197 — does the Channel B document corpus already carry what Channel A knows?

Channel A is 455 human-approved facts in role_facts.json, frozen at 455 since
2026-06-05. They are bare sentences: no URL, no page. Channel B is the document
corpus — verbatim EDB text with a source URL and a resolvable page.

The retirement question is NOT "do the two produce identical output" (they never
will: one returns curated sentences, the other returns cited source text). It is:

    for each approved fact, is the same substance present in the document
    corpus — and therefore available WITH a citation?

If yes, retiring Channel A loses nothing and gains traceability. If no, the
uncovered facts are the retirement blocker list.

WHAT THIS DELIBERATELY EXCLUDES
-------------------------------
The wiki_chunks table also stores 109 `approved_fact` rows and 26 `stat_fact`
rows. The 109 are, verbatim, a subset of the same 455 (verified: exact string
match, 109/109 in, 0 foreign). Both families carry an EMPTY url — they are
Channel A material mirrored into the vector store, not document evidence.

Searching for a fact without excluding them returns the fact itself at cosine
~0.83 and every fact scores as "covered". That number would be an artifact of
the query being its own answer. CORPUS_TYPES below is the whole point of this
script: only vault_extract and footnote_curated count as coverage.

WHY COSINE IS NOT THE VERDICT
-----------------------------
S195 measured adversarial queries topping out at 0.632 against true hits at
0.624 — the distributions overlap, so a high cosine cannot distinguish "found
the right passage" from "found something in the same register". S196 repeated
the lesson on the lexical axis. Here cosine only decides WHERE TO LOOK.

The evidence is the anchor check: most approved facts carry hard anchors —
amounts, day counts, percentages, ratios, ordinance chapters. An anchor either
appears in the retrieved passage or it does not, and that is checkable without
judgement. Facts whose anchors all appear in one passage are triaged COVERED;
everything else is routed to a human read. A triage verdict is not a finding
until the passage behind it has been opened.

DIRECTION OF ERROR
------------------
"Channel B covers everything" is the conclusion that makes this session look
decisive. Per dev/rules/communication.md rule 10 that is exactly why the script
refuses to let a high score alone produce it, refuses to count a transport error
as "not covered" (a failed call is ERROR, never absence — playbook
`throttled-api-not-empty-data`), and asserts conservation over the 455 so no
fact can drop out of the tally unnoticed. `--self-test` breaks that assertion on
purpose to prove it fires.

Read-only: embeds facts and reads Supabase. Writes nothing but its own report.

Usage:
  python3 dev/source/channel_a_coverage.py --self-test
  python3 dev/source/channel_a_coverage.py --run --out dev/source/coverage_runs/<name>.json
  python3 dev/source/channel_a_coverage.py --report <name>.json          # triage summary
  python3 dev/source/channel_a_coverage.py --report <name>.json --bucket NO_ANCHOR_HIT
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROLE_FACTS = ROOT / "role_facts.json"
RPC = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/rpc/match_wiki_chunks"
EMBED_URL = "https://api.openai.com/v1/embeddings"
EMBED_MODEL = "text-embedding-3-small"  # matches backend/src/lib/embeddingClient.ts:17

# Only these carry a source URL + page. approved_fact / stat_fact are Channel A
# material mirrored into the store with an empty url — including them would let
# every fact match itself. See module docstring.
CORPUS_TYPES = {"vault_extract", "footnote_curated"}

MATCH_COUNT = 40   # pulled from the whole index, then filtered down to CORPUS_TYPES
TOP_K = 5          # corpus passages kept per fact
CACHE = ROOT / "dev" / "source" / "coverage_runs" / "_embed_cache.json"

BUCKETS = ("COVERED_ANCHORS", "PARTIAL_ANCHORS", "NO_ANCHOR_HIT", "NO_ANCHORS", "ERROR")


# ── anchors ───────────────────────────────────────────────────────────────────

_CN_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9}
_CN_UNIT = {"十": 10, "百": 100, "千": 1000}
_CN_RUN = re.compile(r"[〇零一二兩三四五六七八九十百千]{1,8}")


def _cn_run_to_int(run: str) -> int | None:
    """Convert one run of Chinese numerals. Returns None if it is not a number.

    Handles both readings that appear in EDB text: positional years written
    digit-by-digit ("二零二五" = 2025) and ordinary numbers built with units
    ("三十" = 30, "十五" = 15, "一百二十" = 120).
    """
    if all(c in _CN_DIGIT for c in run):
        if len(run) == 1:
            return _CN_DIGIT[run]
        # 二零二五 → 2025; a unit-less multi-char run is positional
        return int("".join(str(_CN_DIGIT[c]) for c in run))
    total, current = 0, 0
    for c in run:
        if c in _CN_DIGIT:
            current = _CN_DIGIT[c]
        elif c in _CN_UNIT:
            unit = _CN_UNIT[c]
            total += (current or 1) * unit   # 十五 → 10 + 5, not 0
            current = 0
        else:
            return None
    return total + current


def fold_cn_numerals(s: str) -> str:
    """Rewrite Chinese numerals as Arabic so an anchor can be compared at all.

    Found by reading, not by design: the first pass reported "8月15日前提交假期表"
    as having no anchor in the corpus, when g11 states 「於每年八月十五日前…呈交
    下一學年的學校假期表」 — the same rule in Chinese numerals. Ten of the first
    29 facts inspected failed for this reason alone. Without this fold, the
    instrument systematically over-reports gaps, and every one of those false
    gaps would have argued for keeping Channel A.
    """
    def sub(m: re.Match) -> str:
        v = _cn_run_to_int(m.group(0))
        return str(v) if v is not None else m.group(0)
    return _CN_RUN.sub(sub, s)


def normalize(s: str) -> str:
    """Fold full-width forms and Chinese numerals, drop separators and spaces.

    A fact may write "$5,000" where the source PDF writes "5 000" or "5000";
    without this the anchor check would report a false absence.
    """
    s = unicodedata.normalize("NFKC", s)
    s = fold_cn_numerals(s)
    s = re.sub(r"(?<=\d)[,\s](?=\d)", "", s)
    return s.replace(" ", "").replace("　", "")


_NUM = r"\d+(?:\.\d+)?"
_CJK = r"[一-鿿]"
ANCHOR_PATTERNS = (
    rf"\$\s*{_NUM}",                    # $5000
    rf"{_NUM}\s*%",                     # 30%
    rf"{_NUM}\s*:\s*{_NUM}",            # 8.1:1
    rf"第\s*{_NUM}\s*章",               # 第279章
    rf"[Cc]ap\.?\s*{_NUM}",             # Cap.279
    rf"{_NUM}\s*{_CJK}{{1,2}}",         # 30人 / 2口頭 / 14天 / 2026年
)


def extract_anchors(fact: str) -> list[str]:
    """Hard, checkable tokens. Returns normalized surface forms, de-duplicated.

    The counted-unit pattern is generic (a number plus one or two CJK
    characters) rather than an enumerated unit list, because these facts count
    in units no list would anticipate — "2口頭報價", "5書面報價", "3課節". An
    enumerated list silently drops what it did not foresee, and a dropped anchor
    turns a fact into NO_ANCHORS, which reads as "nothing to check" rather than
    "not checked".

    Over-capture is the intended direction. A weak anchor like "2026年" makes the
    triage HARDER to satisfy (the fact needs it present too), so the error runs
    toward more human reads, not toward more facts declared covered.
    """
    text = normalize(fact)
    found: list[str] = []
    for pat in ANCHOR_PATTERNS:
        for m in re.finditer(pat, text):
            tok = normalize(m.group(0))
            if tok not in found:
                found.append(tok)
    return found


def anchor_present(anchor: str, passage: str) -> bool:
    """Is this anchor in the passage?

    Compared on the numeric core plus its unit where one exists, because a PDF
    may render "$5,000" as "5,000元". Matching the digits alone would be too
    loose (a page full of figures would satisfy anything), so the digits must
    carry over AND at least the unit character must appear near them when the
    anchor has one.
    """
    p = normalize(passage)
    digits = re.findall(_NUM, anchor)
    if not digits:
        return anchor in p
    core = digits[0]
    unit = re.sub(r"[\d.,$\s]", "", anchor)
    if not unit:
        return bool(re.search(rf"(?<!\d){re.escape(core)}(?!\d)", p))
    for m in re.finditer(rf"(?<!\d){re.escape(core)}(?!\d)", p):
        window = p[m.end():m.end() + 6]
        if any(ch in window for ch in unit):
            return True
    return False


def classify(anchors: list[str], passages: list[dict]) -> tuple[str, dict]:
    """Triage one fact against its retrieved passages.

    COVERED_ANCHORS requires every anchor to land in ONE passage. Anchors spread
    across several passages are PARTIAL: two half-matches in two documents is
    how a fabricated composite gets built, which is the failure S177 shipped.
    """
    if not anchors:
        return "NO_ANCHORS", {"best_hits": 0, "best_of": 0, "best_idx": None}
    best_idx, best_hits = None, -1
    for i, p in enumerate(passages):
        hits = sum(1 for a in anchors if anchor_present(a, p.get("text", "")))
        if hits > best_hits:
            best_idx, best_hits = i, hits
    detail = {"best_hits": best_hits, "best_of": len(anchors), "best_idx": best_idx}
    if best_hits == len(anchors) and best_hits > 0:
        return "COVERED_ANCHORS", detail
    if best_hits > 0:
        return "PARTIAL_ANCHORS", detail
    return "NO_ANCHOR_HIT", detail


# ── data ──────────────────────────────────────────────────────────────────────

def load_facts(path: Path = ROLE_FACTS) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = []
    for topic, tv in data.items():
        if topic == "_meta":
            continue
        for role, rv in tv.items():
            if role.startswith("_") or not isinstance(rv, list):
                continue
            for i, text in enumerate(rv):
                facts.append({"topic": topic, "role": role, "idx": i, "text": text})
    return facts


# ── transport ─────────────────────────────────────────────────────────────────

class Transient(Exception):
    """A call that failed in transit. NEVER a coverage verdict."""


def _post(url: str, body: dict, headers: dict, timeout: int):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read()[:200].decode("utf-8", "replace")
        # 57014 = statement timeout on the free tier; 429 = rate limited. Both
        # return no rows, and no rows must never be read as "the corpus lacks it".
        raise Transient(f"HTTP {e.code} {detail}") from e
    except Exception as e:  # noqa: BLE001 — socket/SSL/timeouts are all transient here
        raise Transient(repr(e)) from e


def with_retry(fn, attempts: int = 4, base: float = 2.0):
    last = None
    for n in range(attempts):
        try:
            return fn()
        except Transient as e:
            last = e
            if n < attempts - 1:
                time.sleep(base * (2 ** n))
    raise last


def embed(text: str, okey: str) -> list[float]:
    body = {"model": EMBED_MODEL, "input": text}
    hdr = {"Authorization": "Bearer " + okey, "Content-Type": "application/json"}
    return with_retry(lambda: _post(EMBED_URL, body, hdr, 60))["data"][0]["embedding"]


def search_corpus(vec: list[float], skey: str) -> list[dict]:
    body = {"query_embedding": "[" + ",".join(f"{x:.8f}" for x in vec) + "]",
            "match_threshold": 0.1, "match_count": MATCH_COUNT}
    hdr = {"apikey": skey, "Authorization": "Bearer " + skey,
           "Content-Type": "application/json"}
    rows = with_retry(lambda: _post(RPC, body, hdr, 120))
    keep = [r for r in rows if r.get("content_type") in CORPUS_TYPES]
    return keep[:TOP_K]


# ── run ───────────────────────────────────────────────────────────────────────

def assert_conservation(total: int, records: list[dict]) -> None:
    """Every fact lands in exactly one bucket. Proven to fire by --self-test.

    S196 lost three cases during a re-partition and under-reported the residual
    defect by more than half, in the direction that flattered the result. This
    assertion is the mechanical version of the rule that followed.
    """
    tally = {b: 0 for b in BUCKETS}
    for r in records:
        if r["bucket"] not in tally:
            raise AssertionError(f"unknown bucket {r['bucket']!r} for fact {r.get('idx')}")
        tally[r["bucket"]] += 1
    summed = sum(tally.values())
    if summed != total:
        raise AssertionError(f"conservation FAILED: {summed} bucketed != {total} facts ({tally})")


def run(out: Path, limit: int | None, pace: float) -> int:
    okey, skey = os.environ.get("OPENAI_API_KEY"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not (okey and skey):
        sys.exit("need OPENAI_API_KEY + SUPABASE_SERVICE_KEY in env")

    facts = load_facts()
    total_loaded = len(facts)
    if limit:
        facts = facts[:limit]
    print(f"facts loaded: {total_loaded}  running: {len(facts)}  "
          f"corpus types: {sorted(CORPUS_TYPES)}")

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    records = []
    for n, f in enumerate(facts, 1):
        anchors = extract_anchors(f["text"])
        rec = {**f, "anchors": anchors}
        try:
            vec = cache.get(f["text"])
            if vec is None:
                vec = embed(f["text"], okey)
                cache[f["text"]] = vec
            passages = search_corpus(vec, skey)
            rec["passages"] = [{
                "source_id": p.get("source_id"), "title": (p.get("title") or "")[:60],
                "url": p.get("url") or "", "score": round(p.get("score", 0), 4),
                "content_type": p.get("content_type"),
                "text": p.get("text", ""),
            } for p in passages]
            rec["top_score"] = rec["passages"][0]["score"] if rec["passages"] else 0.0
            bucket, detail = classify(anchors, rec["passages"])
            rec["bucket"], rec["anchor_detail"] = bucket, detail
        except Transient as e:
            rec["bucket"] = "ERROR"
            rec["error"] = str(e)
            rec["passages"], rec["top_score"] = [], None
        flag = {"COVERED_ANCHORS": "✅", "PARTIAL_ANCHORS": "◐", "NO_ANCHOR_HIT": "❌",
                "NO_ANCHORS": "·", "ERROR": "⚠"}[rec["bucket"]]
        print(f"  [{n}/{len(facts)}] {flag} {rec['bucket']:<16} "
              f"top={rec['top_score']} {f['text'][:34]}")
        records.append(rec)
        if n % 25 == 0:
            CACHE.write_text(json.dumps(cache), encoding="utf-8")
        time.sleep(pace)

    CACHE.write_text(json.dumps(cache), encoding="utf-8")
    assert_conservation(len(facts), records)

    tally = {b: sum(1 for r in records if r["bucket"] == b) for b in BUCKETS}
    report = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "facts_in_file": total_loaded, "facts_run": len(facts),
              "corpus_types": sorted(CORPUS_TYPES), "embed_model": EMBED_MODEL,
              "match_count": MATCH_COUNT, "top_k": TOP_K,
              "tally": tally, "records": records}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + "=" * 68)
    for b in BUCKETS:
        print(f"  {b:<16} {tally[b]}")
    print(f"  {'TOTAL':<16} {sum(tally.values())} (conservation OK vs {len(facts)})")
    print(f"\nwrote {out}")
    print("\nTriage only. COVERED_ANCHORS is a place to look, not a finding: the "
          "passage behind each verdict must be read before it is reported.")
    if tally["ERROR"]:
        print(f"⚠ {tally['ERROR']} facts failed in transit — NOT counted as uncovered. "
              "Re-run them before drawing any conclusion.")
    return 0


# ── report ────────────────────────────────────────────────────────────────────

def report(path: Path, bucket: str | None, sample: int) -> int:
    rep = json.loads(path.read_text(encoding="utf-8"))
    print(f"run {rep['generated']}  facts={rep['facts_run']}  corpus={rep['corpus_types']}")
    for b in BUCKETS:
        print(f"  {b:<16} {rep['tally'][b]}")
    if not bucket:
        return 0
    rows = [r for r in rep["records"] if r["bucket"] == bucket]
    if sample and sample < len(rows):
        rows = random.Random(7).sample(rows, sample)
    print(f"\n--- {bucket} ({len(rows)} shown) ---")
    for r in rows:
        print(f"\n[{r['topic']}/{r['role']}#{r['idx']}] top={r.get('top_score')} "
              f"anchors={r['anchors']} detail={r.get('anchor_detail')}")
        print(f"  FACT : {r['text']}")
        for p in r["passages"][:2]:
            print(f"  ↳ {p['score']} {p['source_id']} · {p['title']}")
            print(f"    {p['text'][:220].replace(chr(10), ' ')}")
            print(f"    url: {p['url'][:100]}")
    return 0


def reclassify(path: Path) -> int:
    """Re-run the anchor verdicts over a saved run, no API calls.

    The retrieved passages are the expensive part and they are already on disk,
    so a fix to the instrument (see fold_cn_numerals) can be applied to the whole
    455 without paying for the corpus again. Prints the before/after movement per
    bucket, because a silent re-partition is exactly what rule 8 forbids.
    """
    rep = json.loads(path.read_text(encoding="utf-8"))
    before = dict(rep["tally"])
    moved = []
    for r in rep["records"]:
        if r["bucket"] == "ERROR":
            continue
        old = r["bucket"]
        r["anchors"] = extract_anchors(r["text"])
        r["bucket"], r["anchor_detail"] = classify(r["anchors"], r["passages"])
        if r["bucket"] != old:
            moved.append((old, r["bucket"], r["text"][:40]))
    rep["tally"] = {b: sum(1 for r in rep["records"] if r["bucket"] == b) for b in BUCKETS}
    assert_conservation(rep["facts_run"], rep["records"])
    print(f"{'bucket':<18}{'before':>8}{'after':>8}{'delta':>8}")
    for b in BUCKETS:
        d = rep["tally"][b] - before[b]
        print(f"  {b:<16}{before[b]:>8}{rep['tally'][b]:>8}{d:>+8}")
    print(f"  {'TOTAL':<16}{sum(before.values()):>8}{sum(rep['tally'].values()):>8}"
          f"  (conservation OK vs {rep['facts_run']})")
    print(f"\n{len(moved)} facts changed bucket")
    out = path.with_name(path.stem + "_v2.json")
    rep["reclassified"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}")
    return 0


# ── lexical layer (offline; no API calls) ─────────────────────────────────────
#
# Roughly half the approved facts carry no numeric anchor at all — they are
# qualitative ("採購人員須遵守《防止賄賂條例》…"). For those the anchor check has
# nothing to check, and reading 250-odd facts by hand is not a measurement, it is
# a mood. So a second automated layer is needed.
#
# The layer is a DF-calibrated CJK bigram overlap, the same instrument S196 built
# for the footnote lead gate. But an instrument is not evidence until it is shown
# to separate the thing it claims to separate (communication.md rule 7), and S195
# already produced one case where a plausible score did NOT separate: adversarial
# queries reached 0.632 against true hits at 0.624.
#
# So this layer ships with its own control. Every fact is scored twice: once
# against the passage retrieved FOR IT, and once against a passage retrieved for
# an unrelated fact in another topic. If the two distributions overlap the way
# cosine did, the layer is reported as unusable and the facts go to human reading
# — the honest outcome, not a threshold picked to make the run finish.

def cjk_bigrams(text: str) -> set[str]:
    chars = re.findall(r"[一-鿿]", text)
    return {chars[i] + chars[i + 1] for i in range(len(chars) - 1)}


DF_FRACTION = 0.25  # a bigram in >25% of passages carries no topic signal


def build_informative(passages: list[str]) -> set[str]:
    """Bigrams rare enough across the retrieved pool to mean something."""
    df: dict[str, int] = {}
    for p in passages:
        for bg in cjk_bigrams(p):
            df[bg] = df.get(bg, 0) + 1
    cap = max(1, int(len(passages) * DF_FRACTION))
    return {bg for bg, n in df.items() if n <= cap}


def overlap(fact: str, passage: str, informative: set[str]) -> int:
    return len(cjk_bigrams(fact) & cjk_bigrams(passage) & informative)


def analyze(path: Path) -> int:
    rep = json.loads(path.read_text(encoding="utf-8"))
    recs = rep["records"]
    pool = [p["text"] for r in recs for p in r.get("passages", [])]
    if not pool:
        sys.exit("no passages in run — nothing to analyze")
    informative = build_informative(pool)
    print(f"passage pool: {len(pool)}   informative bigrams: {len(informative)} "
          f"(DF <= {DF_FRACTION:.0%})")

    rng = random.Random(11)
    with_top = [r for r in recs if r.get("passages")]
    pos, neg = [], []
    for r in with_top:
        own = r["passages"][0]["text"]
        r["lex_overlap"] = overlap(r["text"], own, informative)
        pos.append(r["lex_overlap"])
        # control: a passage pulled for an unrelated fact in a different topic
        others = [o for o in with_top if o["topic"] != r["topic"]]
        foreign = rng.choice(others)["passages"][0]["text"]
        r["lex_control"] = overlap(r["text"], foreign, informative)
        neg.append(r["lex_control"])

    def pct(xs, q):
        s = sorted(xs)
        return s[min(len(s) - 1, int(len(s) * q))]

    print(f"\n  own-passage overlap : median={pct(pos,.5)}  p10={pct(pos,.10)}  "
          f"p25={pct(pos,.25)}  max={max(pos)}")
    print(f"  control  overlap    : median={pct(neg,.5)}  p90={pct(neg,.90)}  "
          f"p99={pct(neg,.99)}  max={max(neg)}")

    # A usable threshold must sit above nearly all controls and below most
    # positives. If no such gap exists, say so instead of inventing one.
    thr = pct(neg, .99) + 1
    keep = sum(1 for x in pos if x >= thr)
    leak = sum(1 for x in neg if x >= thr)
    separated = leak <= len(neg) * 0.02 and keep >= len(pos) * 0.5
    print(f"\n  candidate threshold >= {thr}: keeps {keep}/{len(pos)} positives, "
          f"admits {leak}/{len(neg)} controls")
    print(f"  VERDICT: {'usable — distributions separate' if separated else 'NOT usable — distributions overlap, these facts need human reading'}")

    anchorless = [r for r in recs if r["bucket"] == "NO_ANCHORS"]
    if separated and anchorless:
        strong = [r for r in anchorless if r.get("lex_overlap", 0) >= thr]
        print(f"\n  NO_ANCHORS facts: {len(anchorless)}   "
              f"lexically supported (>= {thr}): {len(strong)}   "
              f"to read by hand: {len(anchorless) - len(strong)}")
    out = path.with_name(path.stem + "_lex.json")
    out.write_text(json.dumps({"threshold": thr, "separated": separated,
                               "informative_bigrams": len(informative),
                               "records": recs}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


# ── self-test ─────────────────────────────────────────────────────────────────

def self_test() -> int:
    fails = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    check("normalize strips thousands separator",
          normalize("$5,000") == "$5000")
    check("normalize folds full-width digits",
          normalize("３０％") == "30%")
    check("fold positional year run", fold_cn_numerals("二零二五年十月") == "2025年10月")
    check("fold unit-built number", fold_cn_numerals("三十天") == "30天")
    check("fold leading 十 as 10, not 0", fold_cn_numerals("十五日") == "15日")
    check("fold 兩 as 2", fold_cn_numerals("超逾兩天") == "超逾2天")
    check("fold hundreds", fold_cn_numerals("一百二十天") == "120天")
    check("leave non-numeric CJK alone", fold_cn_numerals("學校行政手冊") == "學校行政手冊")
    check("the g11 case that exposed this",
          anchor_present("8月15日", "於每年八月十五日前向有關的總學校發展主任呈交"))
    check("the kg_operation case",
          anchor_present("7天", "七個上課天無故缺課，學校須在該生缺課的第七天填妥通報表")
          or anchor_present("7個", "七個上課天無故缺課"))

    a = extract_anchors("≤$5,000直購；$5,001-$50,000 最少2口頭報價；>$200,000招標")
    check("extract money anchors", "$5000" in a and "$200000" in a)
    check("extract counted-unit anchor beyond any unit list",
          extract_anchors("最少2口頭報價") == ["2口頭"])
    check("extract ordinance anchor", "第279章" in extract_anchors("見教育條例第279章"))
    check("extract ratio anchor", "8.1:1" in extract_anchors("師生比例為8.1:1"))
    check("no anchors in a purely qualitative fact",
          extract_anchors("學校採購需競爭性報價，不可收受回扣") == [])

    check("anchor found across comma formatting",
          anchor_present("$200000", "凡超過 200,000 元須公開招標"))
    check("anchor with unit needs the unit nearby",
          anchor_present("2天", "病假超逾兩天/2天須遞交醫生證明"))
    check("bare digits elsewhere do not satisfy a unit anchor",
          not anchor_present("30人", "本通告第30段列明有關安排"))
    check("digit boundary respected (30 != 300)",
          not anchor_present("30人", "全校共300人參與"))

    ps = [{"text": "上限為30人，午睡時每班20人"}, {"text": "另見第5段"}]
    b, d = classify(["30人", "20人"], ps)
    check("all anchors in one passage = COVERED", b == "COVERED_ANCHORS" and d["best_idx"] == 0)
    b, _ = classify(["30人", "99天"], ps)
    check("some anchors missing = PARTIAL", b == "PARTIAL_ANCHORS")
    b, _ = classify(["77人"], ps)
    check("no anchor lands = NO_ANCHOR_HIT", b == "NO_ANCHOR_HIT")
    b, _ = classify([], ps)
    check("anchorless fact routed to NO_ANCHORS", b == "NO_ANCHORS")
    split = classify(["30人", "20人"], [{"text": "上限30人"}, {"text": "午睡20人"}])[0]
    check("anchors split across two passages is NOT covered", split == "PARTIAL_ANCHORS")

    ok = [{"bucket": "COVERED_ANCHORS"}, {"bucket": "ERROR"}]
    try:
        assert_conservation(2, ok)
        check("conservation passes when the tally is whole", True)
    except AssertionError:
        check("conservation passes when the tally is whole", False)

    # Prove the guard fires: a silently dropped fact must raise, not slip through.
    try:
        assert_conservation(3, ok)
        check("conservation FIRES on a dropped fact", False)
    except AssertionError:
        check("conservation FIRES on a dropped fact", True)
    try:
        assert_conservation(2, [{"bucket": "COVERED_ANCHORS"}, {"bucket": "typo"}])
        check("conservation FIRES on an unknown bucket", False)
    except AssertionError:
        check("conservation FIRES on an unknown bucket", True)

    check("cjk_bigrams ignores latin and digits",
          cjk_bigrams("AB12津貼撥款") == {"津貼", "貼撥", "撥款"})
    inf = build_informative(["津貼撥款安排", "津貼撥款安排", "校巴安全指引", "冷氣維修保養"])
    check("high-DF bigram filtered as uninformative", "津貼" not in inf)
    check("rare bigram kept as informative", "校巴" in inf)
    # 校巴/巴安/安全 — the straddling pair counts too; the sliding window is what
    # makes the measure insensitive to where a term boundary happens to fall.
    check("overlap counts only informative shared bigrams",
          overlap("校巴安全", "校巴安全指引", inf) == 3)
    check("overlap ignores shared but uninformative bigrams",
          overlap("津貼撥款", "津貼撥款安排", inf) == 0)

    facts = load_facts()
    check("role_facts.json yields 455 facts", len(facts) == 455)
    check("facts are distinct", len(set(f["text"] for f in facts)) == len(facts))
    check("approved_fact/stat_fact excluded from corpus",
          "approved_fact" not in CORPUS_TYPES and "stat_fact" not in CORPUS_TYPES)

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--analyze")
    ap.add_argument("--reclassify")
    ap.add_argument("--bucket", choices=BUCKETS)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--out", default="dev/source/coverage_runs/run.json")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--pace", type=float, default=0.12)
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.reclassify:
        q = Path(args.reclassify)
        return reclassify(q if q.is_absolute() else ROOT / args.reclassify)
    if args.analyze:
        p = Path(args.analyze)
        return analyze(p if p.is_absolute() else ROOT / args.analyze)
    if args.report:
        return report(ROOT / args.report if not Path(args.report).is_absolute()
                      else Path(args.report), args.bucket, args.sample)
    if args.run:
        return run(ROOT / args.out, args.limit, args.pace)
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
