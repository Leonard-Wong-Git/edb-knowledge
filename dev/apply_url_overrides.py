#!/usr/bin/env python3
"""apply_url_overrides.py — apply per-chunk `url` overrides to Supabase wiki_chunks (S249).

Why: the QC check PAGE_ANCHORED wants every PDF-sourced chunk to land on the right
page. Curated footnotes are written by per-topic ingest scripts that carry ONE url
per source, so their page anchors cannot live there; they live in
dev/source/url_overrides.json (chunk id -> url) and this script applies them.
It changes `url` only — text, hash and embedding are untouched.

Re-run it after ANY footnote ingest script is run with --execute: that upsert
writes the per-source url back over the anchors.

  /usr/local/bin/python3 dev/apply_url_overrides.py             # dry-run (default)
  /usr/local/bin/python3 dev/apply_url_overrides.py --execute   # backup, then PATCH

--execute first exports every affected row (select=*) to
dev/init_backup/<ts>/url_overrides_backup.json, then PATCHes one id at a time and
checks that exactly one row came back with the new url. Idempotent.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OVERRIDES = REPO_ROOT / "dev" / "source" / "url_overrides.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
DEFAULT_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
TABLE = "wiki_chunks"


def env():
    out = {}
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                out[k] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    execute = "--execute" in sys.argv
    e = env()
    base = e.get("SUPABASE_URL", DEFAULT_URL)
    key = e.get("SUPABASE_SERVICE_KEY")
    if not key:
        print("ERROR: SUPABASE_SERVICE_KEY missing in backend/.env")
        return 1
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    ov = json.loads(OVERRIDES.read_text(encoding="utf-8"))["overrides"]

    rows, todo, missing = [], [], []
    for cid, o in ov.items():
        r = requests.get(f"{base}/rest/v1/{TABLE}", headers=h,
                         params={"id": f"eq.{cid}", "select": "*"}, timeout=60)
        r.raise_for_status()
        got = r.json()
        if len(got) != 1:
            missing.append(cid)
            continue
        rows.append(got[0])
        if got[0].get("url") != o["url"]:
            todo.append((cid, got[0].get("url"), o["url"]))
    print(f"overrides={len(ov)} already_applied={len(rows) - len(todo)} "
          f"to_change={len(todo)} missing_in_store={len(missing)}")
    for cid in missing:
        print(f"  MISSING {cid}  (chunk id no longer exists — re-ingested? update the overrides file)")
    for cid, old, new in todo:
        print(f"  {cid}\n      - {old}\n      + {new}")
    if not execute:
        print("DRY-RUN — nothing written.")
        return 0
    if not todo:
        print("Nothing to do.")
        return 0

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    bdir = REPO_ROOT / "dev" / "init_backup" / ts
    bdir.mkdir(parents=True, exist_ok=True)
    changing = {c for c, _, _ in todo}
    bfile = bdir / "url_overrides_backup.json"
    bfile.write_text(json.dumps([r for r in rows if r["id"] in changing], ensure_ascii=False),
                     encoding="utf-8")
    print(f"backup: {bfile.relative_to(REPO_ROOT)} ({len(changing)} rows)")

    done = 0
    for cid, _old, new in todo:
        r = requests.patch(f"{base}/rest/v1/{TABLE}",
                           headers={**h, "Prefer": "return=representation"},
                           params={"id": f"eq.{cid}", "select": "id,url"},
                           json={"url": new}, timeout=60)
        if r.status_code not in (200, 204) or len(r.json()) != 1 or r.json()[0]["url"] != new:
            print(f"ABORT at {cid}: HTTP {r.status_code} {r.text[:200]}")
            print(f"applied {done}/{len(todo)} before the failure; re-run to continue (idempotent).")
            return 1
        done += 1
    print(f"DONE: {done} url(s) updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
