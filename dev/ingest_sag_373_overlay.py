#!/usr/bin/env python3
"""ingest_sag_373_overlay.py — SAG 2026-05 §3.7.3 delta capture (curated overlay).

CONTEXT (S180 SAG version reconciliation):
  The S179 discovery agent flagged that EDB's 學校行政手冊 (SAG) had a suspected
  newer version while our registry/store still labelled 2025-11. This session
  CONFIRMED live: EDB SAG is now the 2026年5月版 (SAG_C_markup.pdf / SAG_C.pdf
  Last-Modified 2026-05-20), served at the SAME filenames (so the served-URL +
  freshness monitors — which test URL reachability, not content version — were
  structurally blind to it; same blind spot as playbook freshness-monitor-test-served-url).

  The official 更新項目 log sheet (Log_sheet_SAG_monthly_updated_items-c.pdf)
  shows the ONLY delta since 2025-11 is item 73: ch3 §3.7.3「與性有關的問題」
  (both EN+TC revised). A char-level diff of our store §3.7.3 (chunks
  vault_sag_2025_11_d0aba286* + _f1a08082*) vs the 2026-05 PDF shows the
  substantive change is exactly ONE newly-added passage (verbatim, page 80 of
  SAG_C_markup.pdf), about handling SUSPECTED SEXUAL ABUSE cases:

    "如問題懷疑涉及性侵犯，學校須遵照社會福利署《保護兒童免受虐待–多專業合作程序
     指引》，諮詢社會福利署的保護家庭及兒童服務課或香港警務處虐兒案件調查組，以採取
     合適的處理程序。如情況顯示個案可能涉及刑事罪行，學校應向警方舉報。"

  No S179 curated SAG footnote references §3.7.3, so nothing existing is wrong.
  We capture this single new requirement as a route-independent curated overlay
  (same mechanism as ingest_s179_footnotes.py / ingest_s179_topics.py:
  content_type=footnote_curated, id=footnote_fn_<fid>, embed=text+keywords),
  rather than re-ingesting the whole 383-chunk SAG (overkill for a 1-passage delta,
  and SAG is double-ingested as sag_2025_11 markup + g24 clean — the overlay is
  route/source-independent so it surfaces regardless).

  Separately (handled outside this script, tracked-file edits): bump
  source_registry.json version_label 2025-11 -> 2026-05 + last_checked_at for
  sag_2025_11 AND g24, and display-sync the +1 chunk count.

VERBATIM verified this session: passage byte-identical in BOTH SAG_C_markup.pdf and
SAG_C.pdf (2026-05), page index 79 / display page 80.

Modes:
  --self-test (default): embed + cosine vs representative query (gate LEAD>=0.45)
                         + dup-id check + collision check vs live footnote_curated. NO WRITE.
  --execute            : INSPECT before (count + id collision) + INSERT
                         (merge-duplicates upsert) + INSPECT after.

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
NOTE: after --execute, restart/redeploy Render (footnote in-memory cache).
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

SAG_MARKUP_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/regulations/"
                  "sch-admin-guide/SAG_C_markup.pdf")

# Verbatim quoted requirement (the colon-prefixed part is verbatim from the 2026-05 PDF;
# the leading question + "(2026年5月版新增此段)" annotation are framing, clearly mine).
F = [
    dict(fid="sag_sexual_abuse_referral", source_id="sag_2025_11", title="學校行政手冊",
         topic="general", url=f"{SAG_MARKUP_URL}#page=80",
         text="學生懷疑涉及性侵犯（與性有關的問題），學校點處理？要諮詢／轉介邊個部門？幾時要報警？"
              "《學校行政手冊》3.7.3 與性有關的問題（2026年5月版新增此段）："
              "如問題懷疑涉及性侵犯，學校須遵照社會福利署《保護兒童免受虐待–多專業合作程序指引》，"
              "諮詢社會福利署的保護家庭及兒童服務課或香港警務處虐兒案件調查組，以採取合適的處理程序。"
              "如情況顯示個案可能涉及刑事罪行，學校應向警方舉報。",
         keywords=["性侵犯", "懷疑性侵犯", "學生被性侵犯", "與性有關的問題", "兒童性侵犯",
                   "保護兒童免受虐待", "多專業合作程序指引", "社會福利署", "保護家庭及兒童服務課",
                   "虐兒案件調查組", "香港警務處", "警方舉報", "報警", "刑事罪行", "轉介",
                   "學校行政手冊", "3.7.3"],
         q="學生懷疑被性侵犯 學校點處理 諮詢轉介邊個部門 報警"),
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
    for e, v in zip(F, vectors):
        rows.append({
            "id": f"footnote_fn_{e['fid']}", "hash": bw.text_hash(e["text"]), "text": e["text"],
            "source_id": e["source_id"], "title": e["title"], "url": e["url"],
            "topic": e["topic"], "content_type": "footnote_curated", "fact_type": "policy",
            "embedding": v,
        })
    return rows


def self_test():
    api = bw.load_api_key()
    ids = [f"footnote_fn_{e['fid']}" for e in F]
    print(f"entries={len(F)} unique_ids={len(set(ids))}")
    fn_vecs = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    q_vecs = bw.embed_batch(api, [e["q"] for e in F])
    print("=== per-entry cosine vs representative query (gate LEAD>=0.45) ===")
    weak = 0
    for e, fv, qv in zip(F, fn_vecs, q_vecs):
        c = cos(fv, qv)
        flag = "LEAD" if c >= 0.45 else ("merge" if c >= 0.42 else "WEAK")
        if c < 0.45:
            weak += 1
        print(f"  {c:.3f} [{flag:5}] {e['fid']}  id=footnote_fn_{e['fid']}")
    print(f"=== {len(F)-weak}/{len(F)} >= 0.45 lead ===")
    # live collision check (read-only): does this id already exist?
    h = headers_svc()
    for cid in ids:
        existing = id_lookup(h, cid)
        print(f"  live id collision for {cid}: {'EXISTS (will upsert/merge)' if existing else 'none (clean new)'}")


def execute():
    api = bw.load_api_key()
    h = headers_svc()
    print("=== INSPECT before ===")
    print("  footnote_curated count:", fn_count(h))
    for e in F:
        cid = f"footnote_fn_{e['fid']}"
        print(f"  id {cid} ->", id_lookup(h, cid))
    vectors = bw.embed_batch(api, [combine(e["text"], e["keywords"]) for e in F])
    rows = build_rows(vectors)
    hh = {**h, "Prefer": "resolution=merge-duplicates,return=minimal"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}", headers=hh, json=rows, timeout=180)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== INSERT ok ===")
    print("=== INSPECT after ===")
    print("  footnote_curated count:", fn_count(h))
    missing = [f"footnote_fn_{e['fid']}" for e in F if not id_lookup(h, f"footnote_fn_{e['fid']}")]
    print("  missing after insert:", missing or "none")


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
