#!/usr/bin/env python3
"""ingest_s245_option2_byod_footnote.py — add 1 curated footnote (footnote_curated) for Option 2.

S245: the BYOD fact in dev/knowledge/channel_a_option2_queue.json had no source in the corpus;
the EDB original was found on the web and read in full (Tavily extract, 2026-11-05).
Leonard approved ingest in S245 (「Approve ingest」).

Copied from dev/ingest_s244_option2_footnotes.py (same embed format and format lock).
Question prefix is written Chinese (S244 open item (c) concerned colloquial prefixes).

Modes:
  --self-test (default) : format lock vs stored embedding + print rows. NO WRITE.
  --execute             : INSPECT before + upsert (merge-duplicates) + INSPECT after.

Rollback: delete id footnote_fn_byod_edb_support (one row).
After INSERT, Render must be restarted (in-memory _footnoteCache); verify /health cache_b.footnote.
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

FNS = [
    {
        "id": "footnote_fn_byod_edb_support",
        "source_id": "edb_byod_page",
        "title": "在中小學推行「自攜裝置」（教育局網頁）",
        "url": "https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/BYOD/byod_index.html",
        "text": (
            "學校推行自攜裝置（BYOD）時，教育局提供甚麼支援？學校須訂定甚麼使用政策？"
            "教育局「在中小學推行『自攜裝置』」網頁：為配合學校制定有效推行「自攜裝置」的策略，教育局為學校提供全方位的支援，"
            "包括加強有關「自攜裝置」的教師專業培訓及到校支援服務。"
            "學校亦需訂定「可接受使用政策」（AUP），詳述學生在學校使用自攜裝置時可接受和不可接受的行為，"
            "作為規範學生使用流動電腦、無線網絡和資訊的協議。"
        ),
        "keywords": ["自攜裝置", "BYOD", "電子學習", "可接受使用政策", "AUP", "流動電腦裝置", "到校支援", "教師專業培訓", "資訊科技教育"],
        "topic": "it",
        "fact_type": "policy",
        "content_type": "footnote_curated",
    },
]

FORMAT_PROBE = {
    "id": "footnote_fn_kgop_ratio",
    "text": "《學前機構辦學手冊》人手比例表(**註)：三歲至六歲組別1:14的人手比例，只適用於按《幼兒服務條例》註冊的特殊幼兒中心(SCCC)；中心開放時間以社會福利署署長按《幼兒服務規例》第10(1)條批准的時間表為準。",
    "keywords": ["幼稚園", "人手比例", "1:14", "特殊幼兒中心", "SCCC", "幼兒服務條例", "幼兒工作員"],
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
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id,content_type,source_id&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def mk_row(fn, vec):
    return {
        "id": fn["id"], "hash": bw.text_hash(fn["text"]), "text": fn["text"],
        "source_id": fn["source_id"], "title": fn["title"], "url": fn["url"],
        "topic": fn["topic"], "content_type": fn["content_type"], "fact_type": fn["fact_type"],
        "embedding": vec,
    }


def stored_embedding(h, cid):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=embedding&id=eq.{cid}", headers=h, timeout=40)
    e = r.json()[0]["embedding"]
    return json.loads(e) if isinstance(e, str) else e


def self_test():
    api = bw.load_api_key()
    h = headers_svc()
    stored = stored_embedding(h, FORMAT_PROBE["id"])
    v = bw.embed_batch(api, [combine(FORMAT_PROBE["text"], FORMAT_PROBE["keywords"])])[0]
    c = cos(v, stored)
    print(f"format lock text+space+kw vs stored {FORMAT_PROBE['id']}: cos={c:.4f}")
    if c < 0.999:
        sys.exit("FORMAT LOCK FAILED — do not execute")
    for fn in FNS:
        print(f"  {fn['id']} | {fn['source_id']} | exists={bool(id_lookup(h, fn['id']))} | {len(fn['text'])} chars")
    print("self-test OK (no write)")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    for fn in FNS:
        print(f"  id {fn['id']} ->", id_lookup(h, fn["id"]))
    vecs = bw.embed_batch(api, [combine(fn["text"], fn["keywords"]) for fn in FNS])
    rows = [mk_row(fn, v) for fn, v in zip(FNS, vecs)]
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=rows, timeout=90)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    for fn in FNS:
        print(f"  id {fn['id']} ->", id_lookup(h, fn["id"]))


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
