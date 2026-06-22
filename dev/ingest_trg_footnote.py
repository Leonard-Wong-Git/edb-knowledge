#!/usr/bin/env python3
"""ingest_trg_footnote.py — add the TRG 凍結教席 10% footnote (content_type=footnote_curated).

S177 follow-up to the S174 footnote overlay. Route-independent: searchFootnotes() fetches
ALL footnote_curated rows and scores by exact cosine, so this new footnote is retrievable
without any backend/routing change. After INSERT, Render must be restarted (in-memory
_footnoteCache).

Modes:
  --self-test (default) : combine self-check vs an existing stored row (to lock the SAME
                          embed-input format S174 used) + embed the TRG footnote + cosine
                          against query variants. NO WRITE.
  --execute             : INSPECT before (footnote_curated count + id collision) + INSERT
                          (merge-duplicates upsert) + INSPECT after.

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
"""
import os
import sys
import json
import math
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw  # canonical embed + hash

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

# ── The footnote (TRG 凍結教席 10% — verified against EN Annex III claim form +
#    CN 附件III「凍結教師編制申請整合代課教師現金津貼表格」, both say 10% / 一成 of
#    approved teaching staff establishment / 核准教學人員編制). ──
FN = {
    "id": "footnote_fn_trg_freeze_ceiling",
    "source_id": "trg_imc_2023",  # new source id; footnote pass is route-independent (not in registry/SOURCE_SET)
    "title": "為設有法團校董會學校而提供的整合代課教師津貼（2023年9月）",
    "url": "https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/trg/TRG_guidelines_C.pdf",
    "text": (
        "已成立法團校董會的資助學校——可凍結教師編制（申請整合代課教師津貼 TRG）的教席上限是多少？"
        "《為設有法團校董會學校而提供的整合代課教師津貼》附件III申請表訂明：學校申領津貼而凍結的教席總數"
        "——包括（甲）教師放取假期而暫時凍結的教席、（乙）核准編制上的教席空缺，以及（丙）永久凍結的常額教席"
        "——三者合計不得超過該校核准教學人員編制的一成（10%）。凍結教席須事先經校董會／法團校董會同意。"
    ),
    "keywords": [
        "凍結教席", "凍結教師編制", "凍結常額教席", "教席上限", "可以凍結",
        "核准教學人員編制", "核准編制", "一成", "10%", "百分之十", "百分之幾",
        "整合代課教師津貼", "代課教師津貼", "TRG", "法團校董會", "已成立法團校董會",
        "資助學校", "教師放假", "編制空缺",
    ],
    "topic": "general",
    "fact_type": "policy",
    "content_type": "footnote_curated",
}


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
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id,content_type&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def mk_row(vec):
    return {
        "id": FN["id"], "hash": bw.text_hash(FN["text"]), "text": FN["text"],
        "source_id": FN["source_id"], "title": FN["title"], "url": FN["url"],
        "topic": FN["topic"], "content_type": FN["content_type"], "fact_type": FN["fact_type"],
        "embedding": vec,
    }


def self_test():
    api = bw.load_api_key()
    staging = {x["id"]: x for x in json.load(open(REPO_ROOT / "dev" / "footnote_staging.json"))["chunks"]}
    rows = {x["id"]: x for x in json.load(open(REPO_ROOT / "dev" / "footnote_rows.json"))}

    # 1) Lock the production embed-input format: re-embed an existing footnote's
    #    text under several combine formats, compare to its STORED embedding.
    probe = staging["fn_k1_regfee"]
    stored = rows["footnote_fn_k1_regfee"]["embedding"]
    variants = {
        "text_only": probe["text"],
        "text+space+kw": probe["text"] + " " + " ".join(probe["keywords"]),
        "text+nl+kw": probe["text"] + "\n" + " ".join(probe["keywords"]),
    }
    vecs = bw.embed_batch(api, list(variants.values()))
    print("=== combine self-check vs STORED embedding (footnote_fn_k1_regfee) ===")
    best = None
    for (name, _), v in zip(variants.items(), vecs):
        c = cos(v, stored)
        print(f"  {name:16} cos={c:.4f}")
        if best is None or c > best[1]:
            best = (name, c)
    print(f"  -> production combine = {best[0]} (cos={best[1]:.4f})")

    # 2) Embed the TRG footnote (production combine) + cosine vs query variants.
    fn_vec = bw.embed_batch(api, [combine(FN["text"], FN["keywords"])])[0]
    queries = [
        ("原 query", "現在已成立法團校董會學校可以凍結的教席上限是百分之幾？"),
        ("短", "凍結教席上限"),
        ("口語", "學校可以凍結幾多教席"),
        ("TRG 角度", "代課教師津貼 凍結編制 上限"),
        ("常額", "凍結常額教席 核准編制 比例"),
        ("英 control", "graduate teacher posts"),
    ]
    qvecs = bw.embed_batch(api, [q for _, q in queries])
    print("\n=== TRG footnote vs query variants (gate: LEAD>=0.45 / merge>=0.42) ===")
    for (tag, q), qv in zip(queries, qvecs):
        c = cos(fn_vec, qv)
        flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "--")
        print(f"  {c:.4f} [{flag:5}] {tag}: {q}")

    print("\n=== row to INSERT (embedding dim only) ===")
    row = mk_row(fn_vec)
    for k, v in row.items():
        print(f"  {k}: {('<%d-dim vector>' % len(v)) if k == 'embedding' else repr(v)[:120]}")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    print(f"  id {FN['id']} ->", id_lookup(h, FN["id"]))
    fn_vec = bw.embed_batch(api, [combine(FN["text"], FN["keywords"])])[0]
    row = mk_row(fn_vec)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=[row], timeout=90)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    print("  id check:", id_lookup(h, FN["id"]))


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
