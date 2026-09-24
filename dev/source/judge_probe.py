#!/usr/bin/env python3
"""
S195 — measure whether the vault_extract judge-bypass threshold can be lowered.

S183 set VAULT_LEAD_SCORE = 0.70: a vault_extract top hit at or above that score
skips the anti-confabulation judge and is allowed to synthesise. Sources ingested
since then score 0.62-0.63 on their own subject and are therefore declined even
though retrieval found exactly the right document.

Lowering the bar to ~0.60 would put it inside the band S177 identified as the
confabulation zone (0.55-0.65) — the band where the system invented an "IMC 60%"
figure for a frozen-post question. So the question this probe answers is narrow
and empirical:

    how high does the top vault_extract cosine get for a query the corpus
    CANNOT legitimately answer?

If adversarial queries top out well below 0.60, a 0.60 bar is safe. If they reach
into the low 0.6s, it is not, and the fix has to be the judge prompt instead.

Three query classes:
  A  off-domain      — nothing to do with HK schooling; a sanity floor
  B  plausible-gap   — sounds like a school-admin question, but the specific fact
                       is not in the corpus. THIS is the dangerous class: same
                       register, same vocabulary, no answer. S177's failure lived
                       here, and a floor set only on class A would be worthless.
  C  positive control — the real subjects of the newly ingested sources, to show
                       the separation (or lack of it) against class B

Read-only: embeds queries and reads Supabase. Writes nothing.
"""
import json
import os
import statistics
import sys
import urllib.request

RPC = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/rpc/match_wiki_chunks"

# ---------------------------------------------------------------------------
# WHAT THIS PROBE MEASURES, AND WHAT IT DOES NOT (S229 measured, S230 replayed)
# ---------------------------------------------------------------------------
# `top_vault()` below embeds the BARE query and searches the WHOLE index. That is the scale
# `VAULT_LEAD_SCORE = 0.70` was set on (S195B), and it is NOT the scale production applies it
# to: the gate reads `mainSearchLead.score`, which comes from a search over
# `expandQuery(query, category)` narrowed to the routed SOURCE_SET.
#
# Measured on these same 24 queries (backend/scripts/_s229_scaleOffset.ts; replayed
# independently 2026-09-21, dev/source/eval_runs/2026-09-21_s230_scale_offset_replay.json):
# routing does not lift scores (0 to -0.067) but expansion lifts them by up to +0.3226, and
# the adversarial/control overlap widens from 0.0080 to 0.0817 — ten times. 97 of the 185 gold
# items are routed, so for those two the two scales genuinely differ; the other 88 coincide.
#
# So DO NOT use this probe to accept or reject a change to the judge-bypass CONDITION. It
# cannot see the gate's actual input. The tools that do, both running the production path with
# gold ground truth, are:
#   backend/scripts/_s230_bypassCensus.ts   who bypasses today, and whether gold says each
#                                           bypass is sound, wrong-passage, or outright false
#   backend/scripts/_s230_judgeTakeover.ts  what the real judge does with the ones a candidate
#                                           gate hands back to it
# This probe keeps one durable job: it owns the CLASS_A/B/C case set below, which those two
# tools reuse verbatim as an answer key.
#
# KNOWN MISLABEL, left in place deliberately. 「老師病假連續請幾耐先要交醫生紙」 sits in CLASS_B
# ("the specific answer is NOT in the corpus"), and that is wrong: g04 states 「常額教師如申請
# 病假超逾兩天，必須出示有效的醫生證明書」, and S229 opened the window to confirm the leading
# chunk IS that passage, so the bypass firing on it is correct behaviour. It is NOT moved,
# because this list is an answer key and the recorded S195 statistics are read off it: on the
# calibration scale that query scores 0.4964, so reclassifying it to CLASS_C would drop the
# recorded control minimum from 0.6241 to 0.4964 and widen the published overlap further. That
# is a decision to take deliberately with the numbers restated, not a silent edit. Until then
# the probe prints it as a known mislabel so no future reader inherits the error.
MISLABELLED = {
    "老師病假連續請幾耐先要交醫生紙":
        "g04 answers it (常額教師…病假超逾兩天…醫生證明書); belongs in CLASS_C. See header.",
}

CLASS_A = [
    "香港股票市場今日收市指數",
    "米線湯底煮法食譜",
    "英超足球聯賽賽程表",
    "比特幣今年價格走勢",
    "台灣高鐵時刻表同票價",
    "iPhone 換電池保養價錢",
]

CLASS_B = [
    "教師每年可以請幾多日大假",
    "校長退休金點樣計",
    "解僱教師要俾幾多個月遣散費",
    "幼稚園每班最多可以收幾多個學生",
    "學校泳池水質檢測標準係咩",
    "老師病假連續請幾耐先要交醫生紙",
    "學校可唔可以借錢俾教職員",
    "校巴司機最低工資係幾多",
    "學生喺校內可以用手機幾耐",
    "教師評核幾多分先算合格",
    "學校每堂補習費可以收幾多",
    "校服供應商招標要幾多間報價",
    "體罰投訴要幾多日內處理完",
    "課室冷氣應該調到幾多度",
]

CLASS_C = [
    "人工智能初探",
    "資訊及通訊科技 課程指引",
    "跟車保母有咩要求",
    "校巴司機安全指引",
]


def embed(q: str, key: str):
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps({"model": "text-embedding-3-small", "input": q}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["data"][0]["embedding"]


def top_vault(q: str, okey: str, skey: str):
    """Top whole-index vault_extract hit for a query — what the judge would see."""
    vec = embed(q, okey)
    body = {"query_embedding": "[" + ",".join(f"{x:.8f}" for x in vec) + "]",
            "match_threshold": 0.1, "match_count": 40}
    req = urllib.request.Request(RPC, data=json.dumps(body).encode(),
                                 headers={"apikey": skey, "Authorization": "Bearer " + skey,
                                          "Content-Type": "application/json"})
    rows = json.load(urllib.request.urlopen(req, timeout=90))
    for r in rows:
        if r.get("content_type") == "vault_extract":
            return round(r["score"], 3), r["source_id"], r.get("title", "")[:26]
    return None, None, None


def main() -> int:
    okey, skey = os.environ.get("OPENAI_API_KEY"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not (okey and skey):
        sys.exit("need OPENAI_API_KEY + SUPABASE_SERVICE_KEY")

    results = {}
    for label, queries in (("A off-domain", CLASS_A),
                           ("B plausible-gap", CLASS_B),
                           ("C positive control", CLASS_C)):
        print(f"\n=== class {label} ({len(queries)} queries) ===")
        scores = []
        for q in queries:
            s, sid, title = top_vault(q, okey, skey)
            scores.append(s if s is not None else 0.0)
            print(f"  {s if s is not None else '  —  '}  {q[:26]:28} → {sid} · {title}")
        results[label] = scores
        print(f"  max={max(scores)}  median={statistics.median(scores)}  n={len(scores)}")

    if MISLABELLED:
        print("\n" + "=" * 66)
        print("KNOWN MISLABEL — these are printed, not silently counted; see the header:")
        for q, why in MISLABELLED.items():
            print(f"  {q}\n    {why}")

    adv = results["A off-domain"] + results["B plausible-gap"]
    ctrl = results["C positive control"]
    print("\n" + "=" * 66)
    print(f"adversarial (A+B, n={len(adv)}): max={max(adv)}  "
          f"p90={sorted(adv)[int(len(adv) * 0.9)]}  median={statistics.median(adv)}")
    print(f"controls   (C,   n={len(ctrl)}): min={min(ctrl)}  median={statistics.median(ctrl)}")
    gap = min(ctrl) - max(adv)
    print(f"separation between the worst control and the best adversarial: {gap:+.3f}")
    print("\nverdict:")
    if gap <= 0:
        print("  NO SAFE THRESHOLD — adversarial queries reach as high as the real ones.")
        print("  Lowering the bypass cannot be made safe by threshold choice alone;")
        print("  the fix has to be the judge prompt (option c), not the number.")
    else:
        lo, hi = max(adv), min(ctrl)
        print(f"  a bypass anywhere in ({lo:.3f}, {hi:.3f}) separates them on this sample.")
        print(f"  midpoint = {(lo + hi) / 2:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
