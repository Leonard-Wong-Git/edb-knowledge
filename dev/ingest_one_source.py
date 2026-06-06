#!/usr/bin/env python3
"""
ingest_one_source.py <source_id> [--dry-run]
─────────────────────────────────────────────
SAFE per-source Channel B ingest for NEW sources (S146).

Reads dev/vault/<id>/extract_<id>.txt, chunks it with the CANONICAL
build_wiki_index chunker (chunk_text_with_page_carry, 600 chars / 60 overlap,
page-resolvable), embeds with text-embedding-3-small (1536), and INSERTs ONLY
this source_id's chunks into Supabase wiki_chunks via direct REST
(Prefer: resolution=merge-duplicates → safe re-run, upsert by PK id).

Why not build_wiki_index.py + upload_wiki_to_supabase.py?
  The local dev/knowledge/wiki_index.json is STALE (≈2,874 chunks vs live
  10,594). Running the full uploader would risk re-inserting chunk ids that
  were deprecated/superseded in live. This script touches ONLY <source_id>,
  never the shared wiki_index.json and never other sources.

Usage (from repo root):
  SUPABASE_SERVICE_KEY=... python3 dev/ingest_one_source.py g36
  python3 dev/ingest_one_source.py g36 --dry-run    # chunk only, no API / no insert

Env: OPENAI_API_KEY + SUPABASE_SERVICE_KEY auto-read from backend/.env.
"""
import os
import sys
import statistics
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent          # …/Draft
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw                                # canonical chunker + embed

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
INSERT_BATCH = 50


def load_service_key() -> str:
    k = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return k


def build_rows(source_id: str):
    srcs = bw.load_vault_sources(filter_source=source_id)
    if not srcs:
        sys.exit(f"ERROR: no vault source for '{source_id}' "
                 f"(need dev/vault/{source_id}/extract_{source_id}.txt)")
    src = srcs[0]
    src["text"] = src["text"].replace("\x00", "")   # strip NUL byte → avoid Postgres 22P05 on INSERT (matches cb3_b2_pagecarry S132 fix)
    topic = (src.get("topic") or "general").split(",")[0].strip()
    if topic not in bw.VALID_TOPICS:
        print(f"  ⚠ topic '{topic}' not in VALID_TOPICS → fallback 'curriculum'", file=sys.stderr)
        topic = "curriculum"
    rows, seen = [], set()
    for ch in bw.chunk_text_with_page_carry(src["text"]):
        h = bw.text_hash(ch)
        cid = f"vault_{source_id}_{h}"
        if cid in seen:                 # byte-identical chunk dedupe (repeated tables etc.)
            continue
        seen.add(cid)
        rows.append({
            "id": cid, "hash": h, "text": ch,
            "source_id": source_id, "title": src["title"], "url": src["url"],
            "topic": topic, "content_type": "vault_extract",
            "fact_type": src.get("fact_type", "policy"),
        })
    return src, topic, rows


def live_count(headers, source_id: str) -> str:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id&source_id=eq.{source_id}",
                     headers={**headers, "Range-Unit": "items", "Range": "0-0",
                              "Prefer": "count=exact"}, timeout=40)
    return r.headers.get("content-range", "?")


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    ids = [a for a in argv if not a.startswith("--")]
    if len(ids) != 1:
        sys.exit("usage: ingest_one_source.py <source_id> [--dry-run]")
    sid = ids[0]

    src, topic, rows = build_rows(sid)
    lens = [len(r["text"]) for r in rows] or [0]
    print(f"[{sid}] title={src['title']!r}  topic={topic}  chunks={len(rows)}  "
          f"char(min/med/max)={min(lens)}/{int(statistics.median(lens))}/{max(lens)}")
    if rows:
        print(f"  sample id: {rows[0]['id']}")

    if dry:
        for r in rows[:3]:
            print(f"  id={r['id']}  page-resolvable={'=== Page' in r['text']}")
        return
    if not rows:
        sys.exit("ERROR: 0 chunks built — refuse to proceed")

    # embed (canonical, batches of 100)
    api_key = bw.load_api_key()
    vectors = bw.embed_batch(api_key, [r["text"] for r in rows])
    if len(vectors) != len(rows):
        sys.exit(f"ERROR: embed count {len(vectors)} != rows {len(rows)}")
    for r, v in zip(rows, vectors):
        r["embedding"] = v

    # insert (this source_id only)
    svc = load_service_key()
    if not svc:
        sys.exit("ERROR: SUPABASE_SERVICE_KEY missing")
    headers = {"apikey": svc, "Authorization": f"Bearer {svc}",
               "Content-Type": "application/json",
               "Prefer": "resolution=merge-duplicates,return=minimal"}
    ep = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    before = live_count(headers, sid)
    done = 0
    for i in range(0, len(rows), INSERT_BATCH):
        batch = rows[i:i + INSERT_BATCH]
        resp = requests.post(ep, headers=headers, json=batch, timeout=90)
        if resp.status_code not in (200, 201, 204):
            sys.exit(f"INSERT FAIL {resp.status_code}: {resp.text[:300]}")
        done += len(batch)
        print(f"  inserted {done}/{len(rows)}")
    after = live_count(headers, sid)
    print(f"[{sid}] DONE  before={before}  after={after}")


if __name__ == "__main__":
    main()
