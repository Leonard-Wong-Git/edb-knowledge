#!/usr/bin/env python3
"""ingest_s232_kg_ratio_footnote.py — add the KG teacher-pupil ratio footnote (content_type=footnote_curated).

S232 route 甲 for the GN10 production defect: 「幼稚園每班師生比例係幾多」 was answered
「至少1:30、某些情況可達1:14」. Production window (synthesize:false, 2026-09-24) holds three
kg_operation_manual footnotes — per-class on-duty minimum, class size <=30, and 1:14 (SCCC only)
— but NOT the actual ratio, so the synthesizer stitched class size and the SCCC ratio into one.
The real rule sits only in vault chunks that this query never retrieves (it routes to g29).

Verified against the corpus text (not memory):
  - kg_admin_guide_2026 §5.1.1.1 (PDF p.107) + its note 1: scheme KGs 1:15 (principal counted)
    -> 1:11 (principal not counted); headcount by mid-September total, half-day /2, round down;
    on-duty rule 1 teacher per 15 pupils present, principal may count, >=1 teacher per class.
  - kg_operation_manual_2026 附錄20 = 教育局通告第26/2003號 (PDF p.147-148): the 1:15 on-duty rule.
NOTE: the S231 handoff premise「普通幼稚園無規定師生比例」is WRONG — do not write that.

Route-independent: searchFootnotes() fetches ALL footnote_curated rows and scores by exact
cosine. After INSERT, Render must be restarted (in-memory _footnoteCache).

Modes:
  --self-test (default) : lock the production embed-input format against the STORED embedding
                          of footnote_fn_kgop_ratio, embed this footnote, cosine vs query
                          variants and vs the confusable SCCC query. NO WRITE.
  --execute             : INSPECT before + INSERT (merge-duplicates upsert) + INSPECT after.

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

FN = {
    "id": "footnote_fn_kg_teacher_pupil_ratio",
    "source_id": "kg_admin_guide_2026",
    "title": "幼稚園行政手冊",
    "url": "https://www.edb.gov.hk/attachment/tc/edu-system/preprimary-kindergarten/free-quality-kg-edu/KG%20Admin%20Guide_Chi_2026_May.pdf#page=107",
    "text": (
        "幼稚園師生比例是多少？每班要有多少位教師？"
        "《幼稚園行政手冊》5.1.1.1：參加幼稚園教育計劃的幼稚園，整體師生比例要求由1:15（校長計算在內）"
        "提升至1:11（校長不計算在內）；所需教師人數按九月中所有班級的總學生人數計算（半日制把數目除以二），"
        "並向下調整至整數。《學前機構辦學手冊》附錄20（教育局通告第26/2003號）：幼稚園在場當值的最少教師人數"
        "與在場學生人數的比例，規定為每15名學生（不足15名當15名計算）須有一名教師在場當值，校長可計算為其中"
        "一名教學人員，而每班須有最少一名教師在場當值。注意：「每班學生人數不應超過30人」是課室容納人數上限，"
        "不是師生比例；1:14的人手比例只適用於按《幼兒服務條例》註冊的特殊幼兒中心，不適用於幼稚園。"
    ),
    "keywords": [
        "師生比例", "師生比", "教師與學生比例", "1:11", "1:15", "每班師生比例",
        "每班幾多個老師", "幾多個老師", "教師人數", "當值教師", "在場當值",
        "幼稚園教育計劃", "校長不計算在內", "幼稚園", "師生比例係幾多",
    ],
    "topic": "general",
    "fact_type": "policy",
    "content_type": "footnote_curated",
}

FORMAT_PROBE = {  # existing row whose staging keywords are known (dev/footnote_staging.json)
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
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id,content_type&id=eq.{cid}", headers=h, timeout=40)
    return r.json()


def mk_row(vec):
    return {
        "id": FN["id"], "hash": bw.text_hash(FN["text"]), "text": FN["text"],
        "source_id": FN["source_id"], "title": FN["title"], "url": FN["url"],
        "topic": FN["topic"], "content_type": FN["content_type"], "fact_type": FN["fact_type"],
        "embedding": vec,
    }


def stored_embedding(h, cid):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=embedding&id=eq.{cid}", headers=h, timeout=40)
    e = r.json()[0]["embedding"]
    return json.loads(e) if isinstance(e, str) else e


def self_test():
    api = bw.load_api_key()
    h = headers_svc()

    # 1) Lock the production embed-input format against a STORED embedding.
    stored = stored_embedding(h, FORMAT_PROBE["id"])
    variants = {
        "text_only": FORMAT_PROBE["text"],
        "text+space+kw": combine(FORMAT_PROBE["text"], FORMAT_PROBE["keywords"]),
        "text+nl+kw": FORMAT_PROBE["text"] + "\n" + " ".join(FORMAT_PROBE["keywords"]),
    }
    vecs = bw.embed_batch(api, list(variants.values()))
    print(f"=== combine self-check vs STORED embedding ({FORMAT_PROBE['id']}) ===")
    for (name, _), v in zip(variants.items(), vecs):
        print(f"  {name:16} cos={cos(v, stored):.4f}")

    # 2) This footnote vs query variants; the SCCC query is the confusable control
    #    (gold kg_sccc_ratio_confusable forbids kg_admin_guide_2026 there).
    fn_vec = bw.embed_batch(api, [combine(FN["text"], FN["keywords"])])[0]
    queries = [
        ("GN10 原句", "幼稚園每班師生比例係幾多"),
        ("gold 短", "幼稚園師生比例"),
        ("短", "師生比例"),
        ("口語", "幼稚園一班要幾多個老師"),
        ("計劃", "幼稚園教育計劃 師生比例 1:11"),
        ("SCCC 對照", "幼兒中心人手比例"),
        ("英 control", "graduate teacher posts"),
    ]
    qvecs = bw.embed_batch(api, [q for _, q in queries])
    print("\n=== new footnote vs FORMAT_PROBE (1:14 SCCC) per query ===")
    for (tag, q), qv in zip(queries, qvecs):
        c_new, c_old = cos(fn_vec, qv), cos(vecs[1], qv)
        print(f"  new {c_new:.4f}  sccc {c_old:.4f}  {'NEW' if c_new > c_old else 'sccc'} wins  {tag}: {q}")

    print("\n=== row to INSERT (embedding dim only) ===")
    for k, v in mk_row(fn_vec).items():
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
