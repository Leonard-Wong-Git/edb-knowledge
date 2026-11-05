#!/usr/bin/env python3
"""ingest_s244_option2_footnotes.py — add 3 curated footnotes (content_type=footnote_curated) for Option 2.

S244: Channel A Option 2 queue (dev/knowledge/channel_a_option2_queue.json, _meta.rules 3).
Three facts had no source in the corpus; the EDB original was found on the web and verified
against the page text (Tavily extract / search, 2026-11-05). Leonard approved ingest in S244
(「全部批准」 then 「入庫 3條，再commit 入 supabase」).

Copied from dev/ingest_s232_kg_ratio_footnote.py (same embed format: text + space + keywords,
locked against the STORED embedding of footnote_fn_kgop_ratio).

Modes:
  --self-test (default) : format lock vs stored embedding + print rows. NO WRITE.
  --execute             : INSPECT before + upsert (merge-duplicates) + INSPECT after.

Rollback: delete the three ids below (one row each).
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
        "id": "footnote_fn_ceg_recurrent_august",
        "source_id": "ceg_calc_2026",
        "title": "學校發展津貼的參考資料",
        "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/subsidy-info/ref-capacity-enhancement-grant/index.html",
        "text": (
            "學校發展津貼幾時發放？要唔要每年申請？"
            "教育局「學校發展津貼的參考資料」：由二零零六年二月起，政府把「學校發展津貼」改為經常撥款，為學校提供長期的支援。"
            "由二零零七/零八學年起，學校毋須再每年申請「學校發展津貼」的撥款；教育局會按照新學年的核准班級數目，"
            "在八月份向合資格的學校發放新學年的「學校發展津貼」。法團校董會學校的「學校發展津貼」由每年九月起按季發放。"
        ),
        "keywords": ["學校發展津貼", "經常撥款", "八月", "發放", "核准班級數目", "按季發放", "法團校董會", "毋須申請", "CEG"],
        "topic": "finance",
        "fact_type": "policy",
        "content_type": "footnote_curated",
    },
    {
        "id": "footnote_fn_leave_nonteaching_annual",
        "source_id": "g04",
        "title": "資助學校批假事宜（教育局學校行政主任入職課程簡報，2020）",
        "url": "https://www.edb.gov.hk/attachment/tc/sch-admin/admin/about-sch-staff/schexo/InductionProg_Granting_of_Leave.pdf",
        "text": (
            "資助學校非教學人員每年有幾多日年假？"
            "教育局《資助學校批假事宜》簡報：以薪金津貼支薪的專責人員／實驗室技術員／學校行政主任／非專責人員，"
            "如在2000年6月1日或之後受聘，每年可享有的有薪假期：總薪級0至13點及第一標準薪級表人員，服務少於10年為14天，"
            "服務滿10年或以上為18天；總薪級14點或以上人員，服務少於10年為18天，服務滿10年或以上為22天；假期不可累積。"
            "專責人員、實驗室技術員、學校行政主任及非專責人員不享有學校假期。"
        ),
        "keywords": ["年假", "非教學人員", "有薪假期", "專責人員", "實驗室技術員", "學校行政主任", "文書", "總薪級", "14天", "18天", "22天", "假期不可累積"],
        "topic": "hr",
        "fact_type": "policy",
        "content_type": "footnote_curated",
    },
    {
        "id": "footnote_fn_cpd_eservices_record",
        "source_id": "edbc29_2024_teacher_training",
        "title": "教育局通告第29/2024號「教師培訓要求」",
        "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC24029C.pdf#page=5",
        "text": (
            "教師持續專業發展（CPD）紀錄要點樣記錄？要唔要學校審核？"
            "教育局通告第29/2024號第18段：教師應善用電子化服務入門網站記錄及檢視培訓進度；學校應確保所輸入的資料完整準確，"
            "提醒教師須於每學年初於電子化服務入門網站核實及確認個人的聘任紀錄和資料，以及上學年的培訓紀錄和資料，"
            "並要求教師於電子化服務入門網站記錄所修讀的培訓課程／活動資料，尤其是並非透過教育局培訓行事曆報讀的培訓課程，以便學校審核。"
        ),
        "keywords": ["持續專業發展", "CPD", "電子化服務入門網站", "e-Services", "培訓紀錄", "學校審核", "培訓行事曆", "教師培訓要求"],
        "topic": "hr",
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
