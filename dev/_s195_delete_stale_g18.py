#!/usr/bin/env python3
"""
_s195_delete_stale_g18.py — remove the 6 superseded 2025/26 chunks of g18.

Context: g18 (學童乘搭校車的安全指引) was refreshed to the 2026/27 edition in S195.
The new edition was already INSERTed (7 chunks). Because chunk ids are content
hashes, 3 of the 9 old rows are byte-identical to new ones and were merged by the
upsert — so the delete set is exactly `old_ids - new_ids` = 6 rows, NOT all 9.
Deleting by source_id would destroy the 3 carried-over chunks too.

The 6 targets are hard-coded below (computed and printed in the S195 session, and
recorded in dev/SESSION_LOG.md) rather than recomputed, so this script cannot drift
into deleting something else if the vault file changes.

Safety: dry-run by default; --apply deletes one id at a time and verifies each
response, then re-counts. Expected end state: g18 = 7 rows, grand total 16,033.

Usage (from repo root):
  python3 dev/_s195_delete_stale_g18.py
  python3 dev/_s195_delete_stale_g18.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/wiki_chunks"
REPO_ROOT = Path(__file__).resolve().parent.parent

STALE_IDS = [
    "vault_g18_2c626269e6adbdea",
    "vault_g18_3d357d61042e8098",
    "vault_g18_90b715d7a2528b89",
    "vault_g18_c338c4fa817a454a",
    "vault_g18_c6a1368bf3f35335",
    "vault_g18_c70d937760b20135",
]
EXPECTED_G18_AFTER = 7
EXPECTED_TOTAL_AFTER = 16033
OLD_URL_MARK = "2025_Guidelines_Schools_TC(r).pdf"


def service_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not key:
        env = REPO_ROOT / "backend" / ".env"
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("SUPABASE_SERVICE_KEY="):
                key = line.split("=", 1)[1].strip()
                break
    if not key:
        sys.exit("SUPABASE_SERVICE_KEY not found (env or backend/.env)")
    return key


def call(method: str, url: str, extra=None):
    h = {"apikey": KEY, "Authorization": "Bearer " + KEY}
    h.update(extra or {})
    req = urllib.request.Request(url, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read().decode()
        return dict(r.headers), (json.loads(raw) if raw.strip() else None)


def count(filter_qs: str = "") -> int:
    url = f"{BASE}?select=id" + (f"&{filter_qs}" if filter_qs else "")
    headers, _ = call("GET", url, {"Prefer": "count=exact", "Range": "0-0"})
    cr = next(v for k, v in headers.items() if k.lower() == "content-range")
    return int(cr.split("/")[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    _, rows = call("GET", f"{BASE}?select=id,url&source_id=eq.g18")
    by_id = {r["id"]: r for r in rows}
    print(f"g18 rows now: {len(rows)}  |  grand total: {count()}")

    print("\nblast radius — every row this will delete:")
    missing = []
    for cid in STALE_IDS:
        row = by_id.get(cid)
        if row is None:
            missing.append(cid)
            print(f"  ! {cid}  ALREADY GONE")
            continue
        stale_url = OLD_URL_MARK in row["url"]
        print(f"  - {cid}  url_is_2025_edition={stale_url}")
        if not stale_url:
            sys.exit(f"ABORT — {cid} does not carry the 2025/26 URL; refusing to delete")

    survivors = [r for r in rows if r["id"] not in set(STALE_IDS)]
    print(f"\nkeeping {len(survivors)} rows (all should be the 2026/27 edition):")
    for u in sorted({r["url"] for r in survivors}):
        print(f"  {u}")
    if any(OLD_URL_MARK in r["url"] for r in survivors):
        sys.exit("ABORT — a survivor still carries the 2025/26 URL; investigate first")

    if not args.apply:
        print(f"\nDRY-RUN — nothing deleted. Would remove {len(STALE_IDS) - len(missing)} rows "
              f"→ g18 {EXPECTED_G18_AFTER}, total {EXPECTED_TOTAL_AFTER}.")
        print("Re-run with --apply to execute.")
        return 0

    print("\napplying:")
    gone = 0
    for cid in STALE_IDS:
        if cid in missing:
            continue
        q = f"{BASE}?id=eq.{urllib.parse.quote(cid, safe='')}"
        _, rep = call("DELETE", q, {"Prefer": "return=representation"})
        n = len(rep or [])
        print(f"  {cid} -> deleted {n}")
        if n != 1:
            sys.exit(f"ABORT — expected to delete 1 row for {cid}, deleted {n}")
        gone += n

    g18_after, total_after = count("source_id=eq.g18"), count()
    print(f"\ndeleted {gone} rows")
    print(f"g18 rows: {g18_after} (expected {EXPECTED_G18_AFTER})")
    print(f"grand total: {total_after} (expected {EXPECTED_TOTAL_AFTER})")
    ok = g18_after == EXPECTED_G18_AFTER and total_after == EXPECTED_TOTAL_AFTER
    print("VERIFY:", "PASS" if ok else "FAIL — investigate before continuing")
    return 0 if ok else 1


KEY = service_key()

if __name__ == "__main__":
    sys.exit(main())
