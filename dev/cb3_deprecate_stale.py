#!/usr/bin/env python3
"""
cb3_deprecate_stale.py — DROP-only deprecation of stale-superseded sources from Supabase wiki_chunks.

USAGE:
  python3 dev/cb3_deprecate_stale.py --only <sid>[,<sid>...] [--execute] [--skip-local]

Default = dry-run (shows DELETE count per source, no mutation).
With --execute: per-source REST DELETE via service_role + verify count=0 + audit log append.
With --skip-local: do NOT touch local wiki_index.json (recommended; Supabase query-authoritative per §E.14).

DESIGN (mirrors cb3_b2_pagecarry_migrate.py discipline):
  - service_role REST (bypasses RLS by default; never uses anon key)
  - Per-source DELETE→count verify (==0 post-delete) → next source
  - Phase backup: write audit log to dev/init_backup/<ts>/cb3_deprecation_log.json
    with pre-delete counts (reversibility audit trail — vault legacy extract files
    and source_registry entries are NOT touched, so rebuild via build_wiki_index.py
    + upload_wiki_to_supabase.py remains possible)
  - --skip-local default-on (no local wiki_index.json edit; Supabase query-authoritative)
  - No vault file mutation, no registry mutation, no chunk INSERT — pure DROP

USE WHEN:
  - Stale-superseded sources still indexed but newer version already page-carried
    (e.g. pe_sss_2007_2015 superseded by pe_sss_2023 marker-bearing S125b)
  - Cleaning up after audit cross-check rule (§8b S125b) flags ranking-competing
    older versions
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_ROOT = REPO_ROOT / "dev" / "init_backup"


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


def _request(method: str, url: str, headers: dict, data: Optional[bytes] = None) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def get_count(supabase_url: str, key: str, sid: str) -> int:  # noqa: E302
    url = f"{supabase_url}/rest/v1/wiki_chunks?select=id&source_id=eq.{sid}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "count=exact",
        "Range": "0-0",
    }
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            cr = r.headers.get("content-range", "")
            # format "0-N/TOTAL" or "*/TOTAL"
            if "/" in cr:
                total = cr.rsplit("/", 1)[1]
                return int(total) if total.isdigit() else -1
            return -1
    except urllib.error.HTTPError as e:
        if e.code == 416:
            # Range Not Satisfiable — count=0
            return 0
        raise


def delete_source(supabase_url: str, key: str, sid: str) -> Tuple[int, str]:
    url = f"{supabase_url}/rest/v1/wiki_chunks?source_id=eq.{sid}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "return=minimal",
    }
    status, body = _request("DELETE", url, headers)
    return status, body.decode("utf-8", errors="replace")[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", required=True, help="Comma-separated source_id list to DROP")
    ap.add_argument("--execute", action="store_true",
                    help="Actually perform REST DELETE (default = dry-run)")
    ap.add_argument("--skip-local", action="store_true", default=True,
                    help="Skip local wiki_index.json edit (recommended; Supabase authoritative)")
    args = ap.parse_args()

    sids = [s.strip() for s in args.only.split(",") if s.strip()]
    if not sids:
        raise SystemExit("--only required (comma-separated source_ids)")

    supabase_url = _env("SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_KEY")

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print("=" * 78)
    print(f"CB-3 batch-6 surgical DROP-only deprecation — {mode} — {len(sids)} sources")
    print("=" * 78)

    # Phase 1: count per source
    pre_counts = {}
    total_delete = 0
    for sid in sids:
        c = get_count(supabase_url, key, sid)
        pre_counts[sid] = c
        total_delete += c
        print(f"  {sid:36s} pre-DELETE count = {c}")

    if not args.execute:
        print(f"\nDRY-RUN only — nothing mutated. Total DELETE planned = {total_delete}.")
        return 0

    if total_delete == 0:
        print("\nNo rows to delete — all sources already empty in index.")
        return 0

    # Phase 2: backup audit log (before any mutation)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    audit = {
        "operation": "cb3_deprecate_stale",
        "timestamp_utc": ts,
        "sources": [{"source_id": sid, "pre_delete_count": pre_counts[sid]} for sid in sids],
        "total_pre_delete": total_delete,
        "reversibility_note": (
            "Vault legacy extract files (dev/vault/<sid>/extract_<sid>.txt) and "
            "source_registry.json entries NOT touched; to restore, rebuild chunks via "
            "build_wiki_index.py then upload via upload_wiki_to_supabase.py (or "
            "cb3_b2_pagecarry_migrate.py if vault has been re-extracted with page markers)."
        ),
    }
    audit_log = backup_dir / "cb3_deprecation_log.json"
    audit_log.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"\nAudit log: {audit_log}")

    # Phase 3: per-source DELETE + verify count==0
    print("\nPhase 3: per-source REST DELETE...")
    failures = []
    for sid in sids:
        status, body = delete_source(supabase_url, key, sid)
        post = get_count(supabase_url, key, sid)
        ok = post == 0 and status in (200, 204)
        marker = "OK" if ok else "FAIL"
        print(f"  {sid:36s} del_status={status} pre={pre_counts[sid]} post={post} {marker}")
        if not ok:
            failures.append((sid, status, body, post))

    print("\n" + "=" * 78)
    if failures:
        print(f"DONE WITH FAILURES: {len(failures)} source(s) failed.")
        for sid, st, body, post in failures:
            print(f"  {sid}: status={st} post-count={post} body={body!r}")
        return 1
    else:
        print(f"DONE: {len(sids)} sources deprecated | DELETED {total_delete} chunks | "
              f"all per-source counts verified 0")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
