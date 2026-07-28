#!/usr/bin/env python3
"""
S196 — acceptance harness for the curated-footnote LEAD SLOT.

Why this exists
---------------
`searchChannelB.ts` gives any `footnote_curated` chunk scoring >= FOOTNOTE_LEAD_SCORE
(0.45) a guaranteed slot at the front of the result list, and a footnote in that slot
also bypasses the anti-confabulation judge. That was built (S174/S178) so a precisely
curated answer is not buried by a mis-routed main search, and it works.

The failure it also produces, measured live on 「校巴營辦商責任」 (S196):

    rank 0  imc_establishment_operation  0.518  法團校董會…小賣部經營利潤
    rank 1  sag_2025_11                  0.495  承辦商性罪行定罪紀錄查核
    rank 2  sch_bus_escorts_2026         0.768  the guideline that answers the question

Both footnotes are off-topic; they match on 營辦/經營/承辦商 — same register, different
subject, which is precisely what cosine cannot separate (S195B measured the same thing
for the vault threshold: adversarial 0.632 vs true hit 0.624). Because the lead was a
footnote, the judge was skipped and the synthesiser stated that school-bus operating
profit must be returned to students.

So a threshold cannot fix this and this probe does not try to find one. It measures
whether a LEXICAL gate separates the two populations, and gives the before/after
evidence for changing the gate:

  positive controls — each sampled footnote's OWN question. The footnote must keep its
                      lead. This is the S174/S178 value the gate must not destroy.
  negative controls — plausible-gap queries (same register, answer not in the corpus;
                      reused from judge_probe.py class B) plus the S196 bus case. No
                      footnote should lead these.

For every lead it finds, the probe reports the informative-bigram overlap between the
query and the footnote text, so the gate constant is chosen from the measured
separation rather than from taste. "Informative" is self-calibrated against the curated
footnote corpus itself: a CJK bigram occurring in more than STOPWORD_DF_FRACTION of the
206 footnotes is boilerplate (學校/教育/津貼…) and cannot manufacture overlap — the same
device already used in checklistRevise.ts.

Read-only: reads Supabase and calls the public search endpoint. Writes only its report.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
import urllib.error
import urllib.request

SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
DEFAULT_ENDPOINT = "https://edb-knowledge.onrender.com/api/search/channel-b"

# Mirrors checklistRevise.ts STOPWORD_DF_FRACTION. A bigram in more than this fraction
# of the footnote corpus is boilerplate.
STOPWORD_DF_FRACTION = 0.25

# Negative controls: queries in school-admin register whose answer is in NEITHER the vault
# nor the curated footnotes. Each was verified against the live corpus in S196 — do not add
# to this list without checking, and do not borrow judge_probe.py's class B wholesale.
#
# That borrowing is exactly the mistake this comment exists to prevent. judge_probe measures
# the VAULT threshold, so its class B asks "is this answerable from vault?" — a fair question
# there. Reused here it is wrong, because the curated footnotes answer several of those
# queries precisely, and the S196 run consequently reported 7 footnote leads as failures when
# most were the feature working. The verified split (S196 audit of all 14):
#   answerable from footnotes -> moved to ANSWERABLE_CONTROLS below
#   answerable from vault     -> never belonged in a footnote probe at all
#   answerable from neither   -> the list below
PLAUSIBLE_GAP = [
    "校長退休金點樣計",            # g24 covers retirement AGE and service certificates, not pension calculation
    "學校泳池水質檢測標準係咩",     # g23 covers pool safety and depth, not water-quality testing
    "校巴司機最低工資係幾多",       # the bus guidelines carry duties, no wage figures
    "學生喺校內可以用手機幾耐",     # nothing on student phone use anywhere in the corpus
    "課室冷氣應該調到幾多度",       # lab_prep_room_aircon specifies equipment, never a temperature
    "教師每年可以請幾多日大假",     # ANNUAL leave is absent; the corpus has sick leave, which is a
                                   # different entitlement — the failure mode here is answering the
                                   # neighbouring question rather than inventing a number
    "學校每堂補習費可以收幾多",     # the approved-fee schedule exists but caps no tutorial fee
    # S196 second pass. These three were dropped from the list on a first reading as
    # "borderline", with no record — which quietly under-reported the residual defect,
    # since all three still take a footnote lead. Re-checked against the corpus by opening
    # the actual chunks rather than trusting a keyword hit, and all three are genuine gaps:
    "解僱教師要俾幾多個月遣散費",   # 三分之二 in the corpus is IMC quorum and DSS fee ratios;
                                   # the LSP guide gives a pro-rata METHOD, never a month rate
    "學校可唔可以借錢俾教職員",     # 借貸/借錢/貸款 hits are the BAFS accounting syllabus,
                                   # student-gambling warning signs and student loan schemes —
                                   # no rule anywhere about a school lending to its staff, so the
                                   # confident-sounding answer this query produces is ungrounded
    "教師評核幾多分先算合格",       # 合格/及格 in the corpus mean QUALIFIED TEACHER status and the
                                   # BLNST pass, a different sense; no appraisal pass mark exists
]

# Queries that LOOK adversarial in the same register but are genuinely answered by a curated
# footnote. A footnote lead on these is the feature, not the defect, so they are scored as
# positives: losing one is a regression.
ANSWERABLE_CONTROLS = [
    "幼稚園每班最多可以收幾多個學生",  # 學前機構辦學手冊 附10: 每班不超過30人, 午睡課室20人
    "老師病假連續請幾耐先要交醫生紙",  # 學校行政手冊 附錄9: 超逾兩天須出示醫生證明書
    "校服供應商招標要幾多間報價",      # subvention_tips: >$200k 公開招標邀請最少5個供應商
    "體罰投訴要幾多日內處理完",        # 學校處理投訴指引 2023: 調查建議兩個月內, 上訴14天
]

# The S196 case itself, plus phrasings of it. These must stop taking footnote leads.
S196_CASES = [
    "校巴營辦商責任",
    "校車營辦商",
    "校巴營辦商有咩責任",
]


# ---------------------------------------------------------------------------
# Lexical helpers (mirror of the TS side, kept deliberately tiny)
# ---------------------------------------------------------------------------

def cjk_bigrams(s: str) -> list[str]:
    """Every adjacent CJK pair, non-CJK stripped. Mirrors cjkBigrams() in checklistRevise.ts."""
    cjk = "".join(ch for ch in (s or "") if "一" <= ch <= "鿿")
    return [cjk[i:i + 2] for i in range(len(cjk) - 1)]


def build_informative(corpus_texts: list[str]) -> set[str]:
    """Bigrams appearing in <= STOPWORD_DF_FRACTION of the corpus are informative."""
    df: dict[str, int] = {}
    for t in corpus_texts:
        for bg in set(cjk_bigrams(t)):
            df[bg] = df.get(bg, 0) + 1
    cap = max(2, math.ceil(len(corpus_texts) * STOPWORD_DF_FRACTION))
    return {bg for bg, n in df.items() if n <= cap}


# Mirrors FOOTNOTE_LEAD_MIN_OVERLAP in searchChannelB.ts. Kept here so the probe reports
# "unjudgeable" for exactly the queries the gate declines to judge.
MIN_OVERLAP = 2


def overlap(query: str, text: str, informative: set[str]) -> int | None:
    """Distinct informative bigrams shared by query and text.

    Returns None when the query carries fewer than MIN_OVERLAP informative CJK bigrams —
    an English or number-led query such as "NET Grant School Plan / School Report 要點？"
    reduces to one generic bigram. That is "cannot judge", not "no overlap": the TS gate
    fails open in the same situation, and reporting 0 here would make the probe disagree
    with the thing it is measuring."""
    qb = set(cjk_bigrams(query)) & informative
    if len(qb) < MIN_OVERLAP:
        return None
    tb = set(cjk_bigrams(text))
    return len(qb & tb)



# ---------------------------------------------------------------------------
# Set-conservation guard
# ---------------------------------------------------------------------------

# The whole point of this function is that S196 re-labelled a 14-query set into three
# groups, wrote back only two of them, and never checked that the parts still summed to
# the whole. Three queries disappeared, all three were still failing, and the reported
# residual defect came out at less than half its real size. A comment asking the next
# agent to "remember to check" would have failed the same way, so the check is code and
# it runs in --self-test.
SOURCE_SET_S196_AUDIT = [
    "教師每年可以請幾多日大假", "校長退休金點樣計", "解僱教師要俾幾多個月遣散費",
    "幼稚園每班最多可以收幾多個學生", "學校泳池水質檢測標準係咩",
    "老師病假連續請幾耐先要交醫生紙", "學校可唔可以借錢俾教職員",
    "校巴司機最低工資係幾多", "學生喺校內可以用手機幾耐", "教師評核幾多分先算合格",
    "學校每堂補習費可以收幾多", "校服供應商招標要幾多間報價",
    "體罰投訴要幾多日內處理完", "課室冷氣應該調到幾多度",
]


def partition_gaps(source: list[str], *parts: list[str]) -> tuple[list[str], list[str]]:
    """Items of `source` present in no part, and items in a part that are not in `source`.

    Both directions matter: the first catches silent shrinkage, the second catches a query
    quietly rewritten so it no longer corresponds to anything that was audited."""
    covered: set[str] = set()
    for part in parts:
        covered |= set(part)
    missing = [q for q in source if q not in covered]
    unknown = sorted(covered - set(source))
    return missing, unknown


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def read_service_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if key:
        return key.strip()
    here = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(here, "..", "..", "backend", ".env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") or line.startswith("SUPABASE_ANON_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("no Supabase key: set SUPABASE_SERVICE_KEY or provide backend/.env")


def fetch_footnotes() -> list[dict]:
    key = read_service_key()
    url = (f"{SUPABASE_URL}/rest/v1/wiki_chunks"
           f"?select=id,source_id,text&content_type=eq.footnote_curated&limit=1000")
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def extract_question(text: str) -> str:
    """Curated footnotes are written '<question>？<answer>'. The question alone is the
    most honest positive control: it is what a user who wants that fact would type."""
    t = (text or "").strip()
    for mark in ("？", "?"):
        i = t.find(mark)
        if 0 < i <= 60:
            return t[:i + 1]
    return t[:40]


def query_once(endpoint: str, query: str, retries: int = 2) -> dict:
    body = json.dumps({"query": query, "synthesize": False}).encode("utf-8")
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                endpoint, data=body,
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as exc:  # 429 / 57014 / network — never treat as "no results"
            last = exc
            time.sleep(4 * (attempt + 1))
    return {"_error": str(last)}


def leads_of(resp: dict) -> list[dict]:
    """The lead slots are the front entries whose score is NOT the max — the merge in
    searchChannelB puts forced leads first and sorts the rest. Rather than infer, take
    the first two results and let the caller check content_type."""
    return (resp.get("results") or [])[:2]


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run(endpoint: str, sample_every: int, pace: float, limit: int | None) -> dict:
    footnotes = fetch_footnotes()
    informative = build_informative([f["text"] for f in footnotes])
    positives = footnotes[::sample_every]
    if limit:
        positives = positives[:limit]

    rows: list[dict] = []

    for f in positives:
        q = extract_question(f["text"])
        resp = query_once(endpoint, q)
        if "_error" in resp:
            rows.append({"class": "positive", "query": q, "want_source": f["source_id"],
                         "error": resp["_error"]})
            time.sleep(pace)
            continue
        lead = None
        for r in leads_of(resp):
            if r.get("content_type") == "footnote_curated":
                lead = r
                break
        rows.append({
            "class": "positive",
            "query": q,
            "want_source": f["source_id"],
            "lead_source": lead.get("source_id") if lead else None,
            "lead_score": round(lead.get("score", 0), 4) if lead else None,
            "lead_overlap": overlap(q, lead.get("text", ""), informative) if lead else None,
            # A positive passes when SOME curated footnote leads. Requiring the exact
            # source_id would fail on near-duplicate footnotes that answer equally well.
            "kept": bool(lead),
        })
        time.sleep(pace)

    for q in PLAUSIBLE_GAP + S196_CASES + ANSWERABLE_CONTROLS:
        if q in S196_CASES:
            cls = "s196"
        elif q in ANSWERABLE_CONTROLS:
            cls = "answerable"
        else:
            cls = "plausible_gap"
        resp = query_once(endpoint, q)
        if "_error" in resp:
            rows.append({"class": cls, "query": q, "error": resp["_error"]})
            time.sleep(pace)
            continue
        lead = None
        for r in leads_of(resp):
            if r.get("content_type") == "footnote_curated":
                lead = r
                break
        rows.append({
            "class": cls,
            "query": q,
            "lead_source": lead.get("source_id") if lead else None,
            "lead_score": round(lead.get("score", 0), 4) if lead else None,
            "lead_overlap": overlap(q, lead.get("text", ""), informative) if lead else None,
            "kept": bool(lead),
        })
        time.sleep(pace)

    pos = [r for r in rows if r["class"] in ("positive", "answerable") and "error" not in r]
    neg = [r for r in rows if r["class"] not in ("positive", "answerable")
           and "error" not in r]
    pos_led = [r for r in pos if r["kept"]]
    neg_led = [r for r in neg if r["kept"]]

    return {
        "endpoint": endpoint,
        "informative_bigrams": len(informative),
        "footnote_corpus": len(footnotes),
        "summary": {
            "positive_total": len(pos),
            "positive_with_lead": len(pos_led),
            "negative_total": len(neg),
            "negative_with_lead": len(neg_led),
            "errors": len([r for r in rows if "error" in r]),
            "positive_overlap_min": min((r["lead_overlap"] for r in pos_led
                                        if r["lead_overlap"] is not None), default=None),
            "positive_overlap_median": (
                statistics.median([r["lead_overlap"] for r in pos_led
                                   if r["lead_overlap"] is not None]) if pos_led else None),
            "negative_overlap_max": max((r["lead_overlap"] for r in neg_led
                                        if r["lead_overlap"] is not None), default=None),
        },
        "rows": rows,
    }


def self_test() -> int:
    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        if not cond:
            fails += 1
            print(f"FAIL {name}")

    check("bigrams basic", cjk_bigrams("校巴營辦商") == ["校巴", "巴營", "營辦", "辦商"])
    check("bigrams strip non-cjk", cjk_bigrams("a校 巴b") == ["校巴"])
    check("bigrams short", cjk_bigrams("校") == [])
    # boilerplate self-calibrates out: 學校 in every doc, 校巴 in one
    corpus = ["學校規定" for _ in range(9)] + ["學校校巴營辦"]
    info = build_informative(corpus)
    check("df drops boilerplate", "學校" not in info)
    check("df keeps rare", "校巴" in info)
    check("overlap counts informative only",
          overlap("校巴營辦", "學校校巴營辦", info) >= 1)
    # judgeable query (3 informative bigrams here) that shares nothing with the text
    check("overlap zero when unrelated", overlap("校巴營辦", "學校規定", info) == 0)
    # unjudgeable query: no informative CJK bigrams at all -> None, never 0
    check("overlap None when query has no informative cjk",
          overlap("NET grant 2026", "學校校巴營辦", info) is None)
    check("None is distinct from zero", overlap("NET grant", "任何內容", info) is None)
    # a query with only ONE informative bigram is below the bar the gate can judge on
    check("single-bigram query is unjudgeable",
          overlap("校巴", "學校校巴營辦", info) is None)
    check("question split", extract_question("邊個負責？答案在此。") == "邊個負責？")
    check("question fallback when no mark",
          extract_question("一段冇問號嘅長文字" * 5).startswith("一段"))
    check("question ignores late mark",
          extract_question("x" * 80 + "？yes") == ("x" * 80 + "？")[:40])
    check("leads_of takes two", len(leads_of({"results": [1, 2, 3]})) == 2)
    check("leads_of empty", leads_of({}) == [])

    # Conservation: every query from the audited source set must be accounted for.
    missing, unknown = partition_gaps(SOURCE_SET_S196_AUDIT, PLAUSIBLE_GAP, ANSWERABLE_CONTROLS)
    if missing:
        print("FAIL partition drops queries with no record:")
        for q in missing:
            print(f"       - {q}")
    if unknown:
        print("FAIL partition contains queries never audited:")
        for q in unknown:
            print(f"       + {q}")
    check("partition conserves the audited set", not missing and not unknown)
    check("partition_gaps detects a drop",
          partition_gaps(["a", "b"], ["a"]) == (["b"], []))
    check("partition_gaps detects an unaudited addition",
          partition_gaps(["a"], ["a", "z"]) == ([], ["z"]))

    print(f"self-test: {'PASS' if fails == 0 else f'{fails} FAILED'}")
    return 1 if fails else 0


def compare(before_path: str, after_path: str) -> int:
    before = json.load(open(before_path, encoding="utf-8"))
    after = json.load(open(after_path, encoding="utf-8"))
    b_rows = {r["query"]: r for r in before["rows"]}
    a_rows = {r["query"]: r for r in after["rows"]}

    lost, fixed, still_bad, errors = [], [], [], []
    for q, b in b_rows.items():
        a = a_rows.get(q)
        if a is None:
            continue
        if "error" in b or "error" in a:
            errors.append(q)
            continue
        if b["class"] in ("positive", "answerable"):
            if b["kept"] and not a["kept"]:
                lost.append(q)
        else:
            if b["kept"] and not a["kept"]:
                fixed.append(q)
            elif a["kept"]:
                still_bad.append((q, a.get("lead_source"), a.get("lead_overlap")))

    print(f"positives that LOST their footnote lead : {len(lost)}")
    for q in lost:
        print(f"   - {q}")
    print(f"negatives FIXED (lead removed)          : {len(fixed)}")
    for q in fixed:
        print(f"   + {q}")
    print(f"negatives still leading                 : {len(still_bad)}")
    for q, src, ov in still_bad:
        print(f"   ! {q}  ({src}, overlap={ov})")
    if errors:
        print(f"rows with an error on either side       : {len(errors)}")

    # A regression is a lost positive. Negatives that remain are reported, not fatal,
    # so a partial improvement can still be inspected rather than silently failing.
    return 1 if lost else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--out")
    p.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    p.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    p.add_argument("--sample-every", type=int, default=8,
                   help="take every Nth curated footnote as a positive control")
    p.add_argument("--pace", type=float, default=1.5)
    p.add_argument("--limit", type=int)
    args = p.parse_args()

    if args.self_test:
        return self_test()
    if args.compare:
        return compare(*args.compare)
    if args.run:
        report = run(args.endpoint, args.sample_every, args.pace, args.limit)
        s = report["summary"]
        print(f"footnote corpus {report['footnote_corpus']} | "
              f"informative bigrams {report['informative_bigrams']}")
        print(f"positives with a footnote lead : {s['positive_with_lead']}/{s['positive_total']}"
              f"  (overlap min={s['positive_overlap_min']} median={s['positive_overlap_median']})")
        print(f"negatives with a footnote lead : {s['negative_with_lead']}/{s['negative_total']}"
              f"  (overlap max={s['negative_overlap_max']})")
        print(f"errors: {s['errors']}")
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"wrote {args.out}")
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
