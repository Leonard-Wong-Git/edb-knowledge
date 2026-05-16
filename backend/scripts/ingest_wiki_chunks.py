#!/usr/bin/env python3
"""
ingest_wiki_chunks.py — one-shot Channel B ingestion into Supabase.

Loads pre-embedded chunks from the local wiki index and upserts them into the
`public.wiki_chunks` table (created by backend/supabase/schema.sql), in
batches, idempotently.

WHY THIS SCRIPT IS PYTHON:
  The chunk+embedding source (dev/knowledge/wiki_index.json, ~420 MB, schema
  "wiki_index_v1") is produced by the repo's Python vault tooling and is NOT
  committed (it exceeds GitHub's 100 MB limit — see .gitignore). It must be
  rebuilt/obtained locally before running this. The backend itself never reads
  this file at runtime; it only queries Supabase via the match_wiki_chunks RPC.

CREDENTIALS — env vars ONLY (never hardcoded, never read from .env files here):
  SUPABASE_URL            REQUIRED. Same value the backend uses
                          (Supabase -> Project Settings -> Data API -> Project URL).
  SUPABASE_SERVICE_KEY    REQUIRED for ingestion. The service_role (secret) key.
                          Bulk INSERT/UPSERT into public.wiki_chunks needs write
                          access. The anon key the *runtime* uses only has
                          SELECT/EXECUTE grants (see schema.sql step 5), so it
                          CANNOT write rows. Use the service_role key for this
                          one-time load only; do NOT put it in Render env.

NOTE ON KEY NAMES (known pitfall):
  The backend RUNTIME reads SUPABASE_ANON_KEY (anon/public key) — see
  backend/src/config/env.ts. This INGESTION uses SUPABASE_SERVICE_KEY (a
  different, secret key). They are not interchangeable: a service key in the
  runtime would over-privilege the public API; an anon key here cannot write.

USAGE (from the repo root; path has spaces):
  SUPABASE_URL="https://<ref>.supabase.co" \
  SUPABASE_SERVICE_KEY="<service_role_secret>" \
  python3 backend/scripts/ingest_wiki_chunks.py

  Optional overrides:
    WIKI_INDEX_PATH=/abs/path/to/wiki_index.json   (default: dev/knowledge/wiki_index.json)
    WIKI_INGEST_BATCH_SIZE=50

Idempotent: uses PostgREST `Prefer: resolution=merge-duplicates` (UPSERT on the
`id` primary key) and de-duplicates by id locally first, so re-running after a
partial failure is safe — already-loaded rows are merged, not duplicated.

Requires: `requests` (pip install requests).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

# --- Resolve config strictly from environment ------------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

REPO_ROOT = Path(__file__).resolve().parents[2]  # backend/scripts -> backend -> repo root
DEFAULT_WIKI_INDEX = REPO_ROOT / "dev" / "knowledge" / "wiki_index.json"
WIKI_INDEX_PATH = Path(
    os.environ.get("WIKI_INDEX_PATH", str(DEFAULT_WIKI_INDEX))
).expanduser()

BATCH_SIZE = int(os.environ.get("WIKI_INGEST_BATCH_SIZE", "50"))
TABLE = "wiki_chunks"

# Columns that exist in public.wiki_chunks (must match schema.sql). Any extra
# keys in the source JSON are dropped so the insert never fails on unknown cols.
VALID_FIELDS = {
    "id", "hash", "text", "source_id", "title", "url",
    "topic", "content_type", "fact_type", "role",
    "school_level", "reference_year", "embedding",
}
NULLABLE_FIELDS = ("role", "school_level", "reference_year")


def _fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# --- Validate ---------------------------------------------------------------

if not SUPABASE_URL:
    _fail("SUPABASE_URL is not set (export it; do not hardcode).")
if not SUPABASE_SERVICE_KEY:
    _fail(
        "SUPABASE_SERVICE_KEY is not set. Bulk upsert needs the service_role "
        "(secret) key — the anon key used at runtime only has SELECT/EXECUTE. "
        "Get it from Supabase -> Project Settings -> API Keys -> service_role."
    )
if not WIKI_INDEX_PATH.exists():
    _fail(
        f"wiki index not found: {WIKI_INDEX_PATH}\n"
        "It is gitignored (~420 MB, exceeds GitHub's 100 MB limit). Rebuild it "
        "with the repo's vault tooling or set WIKI_INDEX_PATH to its location."
    )


# --- Load source ------------------------------------------------------------

print(f"Loading {WIKI_INDEX_PATH} ...")
with open(WIKI_INDEX_PATH, "r", encoding="utf-8") as fh:
    data = json.load(fh)

meta = data.get("_meta", {})
model = meta.get("embedding_model")
if model and model != "text-embedding-3-small":
    print(
        f"WARNING: wiki index embedding_model is {model!r}; the schema and "
        "runtime expect text-embedding-3-small (vector dim 1536). Mismatched "
        "dimensions will make the RPC error or return nonsense.",
        file=sys.stderr,
    )

chunks = data.get("chunks") or []
total_raw = len(chunks)
print(f"Loaded {total_raw} chunks (schema={meta.get('schema')!r}, model={model!r}).")


def _sanitize(v):
    """PostgreSQL rejects NUL bytes in text columns; strip them."""
    if isinstance(v, str):
        return v.replace("\x00", "")
    return v


def clean_chunk(c: dict) -> dict | None:
    cleaned = {k: _sanitize(v) for k, v in c.items() if k in VALID_FIELDS}
    for nullable in NULLABLE_FIELDS:
        cleaned.setdefault(nullable, None)
    emb = cleaned.get("embedding")
    if not emb:
        return None
    if len(emb) != 1536:
        print(
            f"  skip {cleaned.get('id')}: embedding dim {len(emb)} != 1536",
            file=sys.stderr,
        )
        return None
    return cleaned


# De-duplicate by id (UPSERT key) and drop embedding-less rows.
seen_ids: set[str] = set()
rows: list[dict] = []
skipped = 0
for c in chunks:
    cleaned = clean_chunk(c)
    if cleaned is None:
        skipped += 1
        continue
    if cleaned["id"] in seen_ids:
        skipped += 1
        continue
    seen_ids.add(cleaned["id"])
    rows.append(cleaned)

print(f"Prepared {len(rows)} rows for upsert (skipped {skipped}).")
if not rows:
    _fail("No valid rows to upsert.")


# --- Upsert in batches ------------------------------------------------------

endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE}"
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    # merge-duplicates => UPSERT on the `id` primary key (safe to re-run).
    "Prefer": "resolution=merge-duplicates,return=minimal",
}

batches = [rows[i : i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
total_batches = len(batches)
uploaded = 0
failed: list[int] = []

print(f"Upserting {len(rows)} rows in {total_batches} batches of {BATCH_SIZE} ...")
for i, batch in enumerate(batches, 1):
    try:
        resp = requests.post(endpoint, headers=headers, json=batch, timeout=60)
    except requests.RequestException as exc:
        print(f"\n  batch {i}/{total_batches} request error: {exc}", file=sys.stderr)
        failed.append(i)
        continue
    if resp.status_code in (200, 201):
        uploaded += len(batch)
        bar = "#" * int(uploaded / len(rows) * 40)
        print(
            f"\r  [{bar:<40}] {uploaded}/{len(rows)} (batch {i}/{total_batches})",
            end="",
            flush=True,
        )
    else:
        print(
            f"\n  batch {i}/{total_batches} failed: "
            f"{resp.status_code} {resp.text[:200]}",
            file=sys.stderr,
        )
        failed.append(i)
    time.sleep(0.2)  # gentle pacing

print()
print("=" * 50)
print(f"Upserted: {uploaded}/{len(rows)} rows")
if skipped:
    print(f"Skipped (no/invalid embedding or dup id): {skipped}")
if failed:
    print(f"Failed batches: {failed}")
    print("Re-run the script — merge-duplicates makes already-loaded rows safe.")
    sys.exit(2)

print("Done. Verify in Supabase SQL editor:")
print(f"  select count(*) from public.{TABLE};   -- expect {uploaded}")
