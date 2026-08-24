#!/usr/bin/env python3
"""
S209 — clear the four broken served URLs the Method B monitor has been reporting.

Why a throwaway script (same shape as `dev/_s195_delete_stale_g18.py`): every
write below is a one-off remediation with a hand-verified target list. The
auto-mode permission gate blocks the agent from writing to Supabase, so this is
written to be READ, then run by Leonard.

The four, and what each one turned out to be
────────────────────────────────────────────
All four are the same family: a year- or session-specific EDB document whose
older edition was taken off the site. Two are pure URL churn (same facts, new
filename) and two are genuinely expired.

  1. eoebg_rates_2026        4 chunks   RE-POINT
     E_Sec_Table II_2026_e.pdf  →  E_Sec_Table II_2026_e_r 6.2026.pdf
     A June-2026 revision of the same 2026/27 rates table. All four footnote
     facts were re-verified verbatim against the revised PDF before writing:
       $440 monthly boarding fee (2026/27)          → p.186-187
       $800 / $7,800 per SS class, ceasing 2026/27  → p.188-190
       $59,570 MMLC additional IT grant             → p.184
       $300,000 floor, LWL + sister-school grant    → p.143
     Content identical → re-point, do not re-ingest (S195 discipline).

  2. edb_pnet_annex_jul2025  1 chunk    RE-POINT + TITLE
     letter_dd_23_Jul_2025_..._PNET_Annex.pdf
       →  letter_dd_2_Jul_2026_to_principals_PNET_2627sy_Annex.pdf
     The 2026/27 school-year edition of the same annex. The cited time-frames
     are word-for-word unchanged:
       Special Allowance   "August – September after commencement / prior to
                            expiry of the Contract"
       Passage/Baggage     "July – September of the respective school year"
     The stored title still said "23 Jul 2025", so it is corrected too. The
     source_id keeps its historical name: it is referenced by nothing in the
     backend, and renaming an id costs more than the wrong date in a slug.

  3. blnst_test_candidate_notes  8 chunks  RETIRE
  4. blnst_test_notes_nondeg     5 chunks  RETIRE
     The 《基本法及香港國安法》測試（非學位程度）notes for the 2026-06-07
     sitting. Application closed 2026-04-30; the sitting is over; EDB has
     removed the whole per-session notes family from the BLNST page (every
     filename variant probed returns 404 — Notes_ND*, Guidance Notes_ND*,
     FAQ_ND*). There is no successor edition to point at.
     Deliberately NOT re-pointed to `QA_BLNST_Apr26_tc.pdf`: it is a different
     document, and a live URL serving the wrong document is the S194
     `ict_sss_2021` failure — worse than a 404, because nothing detects it.
     BLNST coverage survives via `edbc13_2022_blnst` + `edbcm141_2025_blnst`,
     both still 200 and both already in the same SOURCE_SET.

Usage (from repo root):
  python3 dev/_s209_clear_404s.py                 # dry-run: show, verify, write nothing
  python3 dev/_s209_clear_404s.py --apply-repoint # do 1 + 2
  python3 dev/_s209_clear_404s.py --apply-retire  # do 3 + 4 (destructive, 13 rows)

Every write is preceded by a live HEAD check of the destination URL and fails
closed. `--apply-retire` prints the exact row ids it will delete and re-counts
afterwards. Reads `SUPABASE_SERVICE_KEY` from the environment or backend/.env.
"""
import argparse
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
TABLE = "wiki_chunks"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

REPOINTS = [
    {
        "source_id": "eoebg_rates_2026",
        "expect_rows": 4,
        "patch": {"url": "https://www.edb.gov.hk/attachment/en/sch-admin/fin-management/"
                         "subsidy-info/ref-e-oebg-cfeg/E_Sec_Table%20II_2026_e_r%206.2026.pdf"},
    },
    {
        "source_id": "edb_pnet_annex_jul2025",
        "expect_rows": 1,
        "patch": {"url": "https://www.edb.gov.hk/attachment/en/curriculum-development/"
                         "resource-support/net/letter_dd_2_Jul_2026_to_principals_PNET_2627sy_Annex.pdf",
                  "title": "PNET Annex 2 Jul 2026 (2026/27 s.y.) — Application time-frames"},
    },
]

RETIRES = [
    {"source_id": "blnst_test_candidate_notes", "expect_rows": 8},
    {"source_id": "blnst_test_notes_nondeg", "expect_rows": 5},
]


def load_key() -> str:
    import os
    v = (os.environ.get("SUPABASE_SERVICE_KEY") or "").strip()
    if v:
        return v
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("SUPABASE_SERVICE_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def headers(key: str, write: bool = False) -> dict:
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if write:
        h["Content-Type"] = "application/json"
        h["Prefer"] = "return=representation"
    return h


def rows_for(key: str, source_id: str) -> list:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                     headers=headers(key),
                     params={"select": "id,title,url", "source_id": f"eq.{source_id}"},
                     timeout=60)
    r.raise_for_status()
    return r.json()


def url_live(url: str) -> int:
    """HEAD, GET-fallback (EDB refuses HEAD on some paths). Returns status code."""
    try:
        resp = requests.head(url, headers={"User-Agent": UA}, allow_redirects=True, timeout=30)
        if resp.status_code != 200:
            resp = requests.get(url, headers={"User-Agent": UA}, allow_redirects=True,
                                timeout=45, stream=True)
            code = resp.status_code
            resp.close()
            return code
        return 200
    except Exception as e:                                   # noqa: BLE001
        print(f"    ⚠️  probe failed: {e}")
        return 0


def do_repoints(key: str, apply: bool) -> int:
    failures = 0
    for job in REPOINTS:
        sid, patch = job["source_id"], job["patch"]
        rows = rows_for(key, sid)
        print(f"\n=== {sid}  ({len(rows)} rows, expected {job['expect_rows']})")
        if len(rows) != job["expect_rows"]:
            print("    ❌ row count differs from the verified plan — refusing to write")
            failures += 1
            continue
        print(f"    before url  : {rows[0]['url']}")
        print(f"    before title: {rows[0]['title']}")
        for field, value in patch.items():
            print(f"    after  {field:5}: {value}")

        code = url_live(patch["url"])
        print(f"    destination HTTP {code}")
        if code != 200:
            print("    ❌ destination is not 200 — fail closed, nothing written")
            failures += 1
            continue
        if not apply:
            print("    [dry-run] would PATCH")
            continue
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                           headers=headers(key, write=True),
                           params={"source_id": f"eq.{sid}"},
                           data=json.dumps(patch), timeout=60)
        if not r.ok:
            print(f"    ❌ PATCH {r.status_code}: {r.text[:200]}")
            failures += 1
            continue
        after = rows_for(key, sid)
        urls = {x["url"] for x in after}
        print(f"    ✅ patched {len(r.json())} rows; distinct url now: {urls}")
        if urls != {patch["url"]}:
            print("    ❌ post-check mismatch")
            failures += 1
    return failures


def do_retires(key: str, apply: bool) -> int:
    failures = 0
    for job in RETIRES:
        sid = job["source_id"]
        rows = rows_for(key, sid)
        print(f"\n=== {sid}  ({len(rows)} rows, expected {job['expect_rows']})  RETIRE")
        if len(rows) != job["expect_rows"]:
            print("    ❌ row count differs from the verified plan — refusing to delete")
            failures += 1
            continue
        for x in rows:
            print(f"      - {x['id']}")
        if not apply:
            print("    [dry-run] would DELETE the rows above")
            continue
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                            headers=headers(key, write=True),
                            params={"source_id": f"eq.{sid}"}, timeout=60)
        if not r.ok:
            print(f"    ❌ DELETE {r.status_code}: {r.text[:200]}")
            failures += 1
            continue
        left = rows_for(key, sid)
        print(f"    ✅ deleted; rows remaining for {sid}: {len(left)}")
        if left:
            failures += 1
    return failures


def total_count(key: str) -> int:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                     headers={**headers(key), "Range-Unit": "items", "Range": "0-0",
                              "Prefer": "count=exact"},
                     params={"select": "id"}, timeout=60)
    cr = r.headers.get("content-range", "")
    return int(cr.split("/")[-1]) if "/" in cr else -1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply-repoint", action="store_true", help="write the two URL re-points")
    ap.add_argument("--apply-retire", action="store_true",
                    help="DELETE the 13 expired BLNST chunks (destructive)")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("❌ SUPABASE_SERVICE_KEY not found (env or backend/.env)")
        return 2

    before_total = total_count(key)
    print(f"wiki_chunks total before: {before_total:,}")

    failures = do_repoints(key, args.apply_repoint)
    failures += do_retires(key, args.apply_retire)

    after_total = total_count(key)
    print(f"\nwiki_chunks total after: {after_total:,}  (delta {after_total - before_total:+d})")
    if args.apply_retire:
        print("⚠️  Display-sync reminder: the published chunk count must be re-anchored.")
        print("    python3 -c \"import sys;sys.path.insert(0,'dev/source');import execute_ingest as e;"
              "print(e.live_display_sync(e.current_chunk_total(), e.live_total_count()))\"")
    if not (args.apply_repoint or args.apply_retire):
        print("\n[dry-run] nothing was written. Re-run with --apply-repoint and/or --apply-retire.")
    print(f"\n{'❌ ' + str(failures) + ' failure(s)' if failures else '✅ no failures'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
