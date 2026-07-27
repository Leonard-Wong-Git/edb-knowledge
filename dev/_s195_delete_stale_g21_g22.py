#!/usr/bin/env python3
"""
_s195_delete_stale_g21_g22.py — remove the superseded g21 / g22 vault chunks.

Context (GitHub issue #5): both sources were re-extracted in S195 because their
page markers did not match the PDFs they cite.
  · g22 had dropped the cover sheet, so every page number ran one ahead.
  · g21's vault file was the primary AND secondary visual-arts guides concatenated,
    so ~half its chunks cited a document they did not come from. The secondary
    guide is now its own source, va_safety_sec.

The new chunks are already INSERTed. This removes the old ones.

Two guards that matter:
  1. **Curated footnotes are excluded.** g21 and g22 each carry one
     `footnote_curated` chunk that is hand-written, not derived from the vault
     file. Deleting by source_id would destroy them. They are preserved (and were
     re-pointed at the correct PDF sheet earlier in S195).
  2. **The delete set is old_ids MINUS new_ids.** Chunk ids are content hashes, so
     text that survives a re-extract keeps its id. Here the page renumbering
     changed every chunk, so the intersection happens to be empty — but the set is
     still computed that way, and hard-coded below rather than recomputed, so this
     script cannot drift into deleting current content.

Expected end state:
    g21 = 22 vault + 1 curated = 23   (was 49)
    g22 = 58 vault + 1 curated = 59   (was 59)
    va_safety_sec = 27                (new)
    grand total 16,168 → 16,062

Usage (from repo root):
  python3 dev/_s195_delete_stale_g21_g22.py
  python3 dev/_s195_delete_stale_g21_g22.py --apply
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
STALE_FILE = REPO_ROOT / "dev" / "_s195_g21_g22_delete_set.json"

EXPECTED = {"g21": 23, "g22": 59, "va_safety_sec": 27}
EXPECTED_TOTAL_AFTER = 16062
PRESERVE = {"footnote_fn_g21_astm", "footnote_fn_g22_inspectfreq"}


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


def load_targets() -> list[str]:
    if not STALE_FILE.exists():
        sys.exit(f"missing {STALE_FILE} — it is written by the S195 re-extract step")
    ids = json.loads(STALE_FILE.read_text())
    bad = [i for i in ids if i in PRESERVE or not i.startswith("vault_")]
    if bad:
        sys.exit(f"ABORT — delete list contains protected or non-vault ids: {bad}")
    return sorted(ids)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    targets = load_targets()
    print(f"targets: {len(targets)} stale vault chunks "
          f"(g21 {sum(1 for i in targets if i.startswith('vault_g21_'))}, "
          f"g22 {sum(1 for i in targets if i.startswith('vault_g22_'))})")
    print(f"grand total now: {count()}")
    for sid in EXPECTED:
        print(f"  {sid}: {count(f'source_id=eq.{sid}')} rows now → expect {EXPECTED[sid]} after")

    _, rows = call("GET", f"{BASE}?select=id&source_id=in.(g21,g22)")
    live = {r["id"] for r in rows}
    missing = [i for i in targets if i not in live]
    print(f"\nof the {len(targets)} targets, {len(targets) - len(missing)} are live"
          + (f", {len(missing)} already gone" if missing else ""))
    for cid in PRESERVE:
        print(f"  preserved (curated, never deleted): {cid} "
              f"{'present' if cid in live else 'MISSING — investigate'}")
    if any(c not in live for c in PRESERVE):
        return 1

    if not args.apply:
        print("\nDRY-RUN — nothing deleted. Re-run with --apply.")
        return 0

    print("\napplying:")
    gone = 0
    for cid in targets:
        if cid in missing:
            continue
        _, rep = call("DELETE", f"{BASE}?id=eq.{urllib.parse.quote(cid, safe='')}",
                      {"Prefer": "return=representation"})
        n = len(rep or [])
        if n != 1:
            print(f"ABORT — {cid} deleted {n} rows, expected 1")
            return 1
        gone += 1
        if gone % 20 == 0:
            print(f"  … {gone}/{len(targets)}")
    print(f"  deleted {gone}")

    print("\nVERIFY:")
    ok = True
    for sid, want in EXPECTED.items():
        got = count(f"source_id=eq.{sid}")
        print(f"  {sid}: {got} rows (expected {want}) {'✓' if got == want else '✗'}")
        ok &= got == want
    total = count()
    print(f"  grand total: {total} (expected {EXPECTED_TOTAL_AFTER}) "
          f"{'✓' if total == EXPECTED_TOTAL_AFTER else '✗'}")
    ok &= total == EXPECTED_TOTAL_AFTER
    print("RESULT:", "PASS" if ok else "FAIL — investigate before continuing")
    return 0 if ok else 1


KEY = service_key()

if __name__ == "__main__":
    sys.exit(main())
