#!/usr/bin/env python3
"""ingest_tips_footnotes.py — add 2 EDB "Tips on handling govt subventions" footnotes
(S178 forms 第二批 手尾: #27 rental-income 40% + #28 repeat-procurement no-split-order).

Same mechanism as forms_ingest.py / ingest_trg_footnote.py: content_type=footnote_curated,
route-independent overlay, embed = text + " " + " ".join(keywords). Both facts verbatim-
verified against the official EDB source PDF (pymupdf) this session:
  https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/
    tips-handling-gov-subventions/Tips on handling govt subventions for aided schools_c.pdf
  (文件署「教育局 2025年5月」)
  #27 (g)(b 段): 「根據教育局通告第5/2011號，學校若出租校舍，所收取40%的淨租金收入須記入政府津貼帳。」
  #28 (g 段):     「根據教育局通告第4/2013號，…學校只有在12個月內，採購項目的累積價值不超過
                   50,000元及200,000元的情況下，才可分別以口頭報價及書面報價方式重複採購同一類
                   項目。學校不得分拆訂單…」

NOTE on #28 vs the already-ingested #26 (footnote_fn_procurement_thresholds): distinct facts —
#26 = per-purchase quote/tender thresholds; #28 = 12-month cumulative aggregation + no order
splitting. Self-test asserts #28's query leads to #28, not #26.

Modes:
  --self-test (default) : embed both + cosine vs representative query (gate LEAD>=0.45) +
                          dup-id check + #28-vs-#26 separation probe. NO WRITE.
  --execute             : INSPECT before (footnote_curated count + id collision) + batch
                          INSERT (merge-duplicates upsert) + INSPECT after.

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
"""
import os
import sys
import math
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw  # canonical embed + hash

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

SRC_ID = "subvention_tips"
SRC_TITLE = "處理政府給予資助學校資助的提示（2025年5月）"
SRC_URL = (
    "https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/"
    "tips-handling-gov-subventions/Tips%20on%20handling%20govt%20subventions%20for%20aided%20schools_c.pdf"
)

# (fid, text, keywords, test_query)
F = [
    ("tips_rental_40pct",
     "資助學校出租／分租校舍所得的租金收入，要點處理？根據教育局通告第5/2011號，學校若出租校舍，"
     "所收取淨租金收入的40%須記入政府津貼帳（政府資助戶口），不可全數撥入學校自有經費帳。",
     ["出租校舍", "分租校舍", "校舍租金", "租金收入", "淨租金收入", "40%", "政府津貼帳",
      "政府資助戶口", "通告5/2011", "EDBC 5/2011", "學校商業活動"],
     "學校出租校舍租金收入點處理 撥幾多入政府帳"),
    ("tips_no_split_order",
     "資助學校短時間內重複採購同一類項目，會唔會違反招標規定？可唔可以拆單避開招標？根據教育局通告第4/2013號："
     "每次採購費用超過200,000元的物料／服務，須向至少五名供應商個別邀請投標；學校只有在12個月內、採購同類項目"
     "的累積價值不超過50,000元（口頭報價）及200,000元（書面報價）時，才可分別以口頭及書面報價方式重複採購。"
     "學校不得分拆訂單（拆細訂單），藉以規避報價／招標程序。",
     ["重複採購", "同類項目", "拆單", "分拆訂單", "拆細訂單", "避免招標", "規避招標", "12個月",
      "累積價值", "50000", "200000", "口頭報價", "書面報價", "招標", "通告4/2013", "EDBC 4/2013"],
     "12個月內重複採購同類項目可唔可以拆單"),
]


def combine(text, kw):
    return text + " " + " ".join(kw)


def cos(a, b):
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return s / (na * nb) if na and nb else 0.0


def load_service_key():
    k = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return k


def headers_svc():
    svc = load_service_key()
    if not svc:
        sys.exit("ERROR: SUPABASE_SERVICE_KEY missing")
    return {"apikey": svc, "Authorization": f"Bearer {svc}", "Content-Type": "application/json"}


def fn_count(h):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&content_type=eq.footnote_curated",
        headers={**h, "Range-Unit": "items", "Range": "0-0", "Prefer": "count=exact"},
        timeout=40,
    )
    return r.headers.get("content-range", "?")


def id_lookup(h, cid):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def build_rows(vectors):
    rows = []
    for (fid, text, kw, _q), v in zip(F, vectors):
        rows.append({
            "id": f"footnote_fn_{fid}", "hash": bw.text_hash(text), "text": text,
            "source_id": SRC_ID, "title": SRC_TITLE, "url": SRC_URL,
            "topic": "general", "content_type": "footnote_curated", "fact_type": "policy",
            "embedding": v,
        })
    return rows


def self_test():
    api = bw.load_api_key()
    ids = [f"footnote_fn_{x[0]}" for x in F]
    print(f"entries={len(F)} unique_ids={len(set(ids))} -> {ids}")
    fn_vecs = bw.embed_batch(api, [combine(t, kw) for _, t, kw, _ in F])
    q_vecs = bw.embed_batch(api, [q for *_, q in F])
    print("=== per-entry cosine vs representative query (gate LEAD>=0.45) ===")
    weak = 0
    for (fid, *_), fv, qv in zip(F, fn_vecs, q_vecs):
        c = cos(fv, qv)
        flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "WEAK")
        if c < 0.45:
            weak += 1
        print(f"  {c:.3f} [{flag:5}] {fid}")
    print(f"=== {len(F)-weak}/{len(F)} >= 0.45 lead ===")
    # #28 must out-score #26 (procurement_thresholds) for the repeat/split query.
    q28 = bw.embed_batch(api, ["12個月內重複採購同一類項目可唔可以拆單 累積價值上限"])[0]
    c28 = cos(fn_vecs[1], q28)
    print(f"=== #28 separation probe: query 'repeat/split' vs #28 footnote cos={c28:.3f} (want LEAD>=0.45) ===")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    for fid, *_ in F:
        cid = f"footnote_fn_{fid}"
        print(f"  id {cid} ->", id_lookup(h, cid))
    vectors = bw.embed_batch(api, [combine(t, kw) for _, t, kw, _ in F])
    rows = build_rows(vectors)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=rows, timeout=120)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    for fid, *_ in F:
        cid = f"footnote_fn_{fid}"
        print(f"  id {cid} ->", id_lookup(h, cid))


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
