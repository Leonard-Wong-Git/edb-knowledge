#!/usr/bin/env python3
"""fix_trg_url.py — repoint trg_imc_2023 served URL (S179 monitoring follow-up).

The S179 served-URL health monitor (check_served_urls.py) flagged the served URL
  https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/subsidy-info/trg/TRG_guidelines_C.pdf
returning HTTP 404 for source_id=trg_imc_2023 (EDB URL churn / store-lags class, same
family as the S170 SAG 404 + S172 #1 edbc12 re-point). The correct, verified-200 Chinese
target is
  https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/trg/TRG_guidelines_c.pdf
(tc path, lowercase c). trg_imc_2023 is footnote-only (NOT in source_registry.json), so the
store url is the single source of truth — no registry edit needed.

Reversible: url field only; the 3 chunks' prior urls were 2x en/...C.pdf + 1x tc/...C.pdf
(all uppercase C). This sets all to the canonical tc/...c.pdf.

Standard project gated-write pattern (mirrors ingest_*.py / cb3_*.py): dry-run default,
explicit --execute gate, INSPECT before/after. Leonard authorized the TRG fix ("1").

Modes:
  --self-test (default): INSPECT current urls + confirm target HTTP 200. NO WRITE.
  --execute            : INSPECT before -> PATCH url (all trg_imc_2023 chunks) -> INSPECT after.

Env: SUPABASE_SERVICE_KEY auto-read from backend/.env.
"""
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

SOURCE_ID = "trg_imc_2023"
NEW_URL = ("https://www.edb.gov.hk/attachment/tc/sch-admin/fin-management/subsidy-info/"
           "trg/TRG_guidelines_c.pdf")


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


def urls_now(h):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id,url&source_id=eq.{SOURCE_ID}",
        headers=h, timeout=40,
    )
    return r.json()


def self_test():
    h = headers_svc()
    print("=== current trg_imc_2023 chunks ===")
    for row in urls_now(h):
        print(f"  {row['id']}  ->  {row['url']}")
    code = requests.head(NEW_URL, timeout=40, allow_redirects=True).status_code
    print(f"=== target URL HTTP {code} (want 200) ===\n  {NEW_URL}")


def execute():
    h = headers_svc()
    print("=== INSPECT before ===")
    for row in urls_now(h):
        print(f"  {row['id']}  ->  {row['url']}")
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?source_id=eq.{SOURCE_ID}",
        headers={**h, "Prefer": "return=minimal"},
        json={"url": NEW_URL}, timeout=60,
    )
    if resp.status_code not in (200, 204):
        sys.exit(f"PATCH FAIL {resp.status_code}: {resp.text[:300]}")
    print("=== PATCH ok ===")
    print("=== INSPECT after ===")
    for row in urls_now(h):
        print(f"  {row['id']}  ->  {row['url']}")
    code = requests.head(NEW_URL, timeout=40, allow_redirects=True).status_code
    print(f"=== re-verify target HTTP {code} ===")


if __name__ == "__main__":
    if "--execute" in sys.argv:
        execute()
    else:
        self_test()
