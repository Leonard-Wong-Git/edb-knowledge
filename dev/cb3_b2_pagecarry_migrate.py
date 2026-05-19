#!/usr/bin/env python3
"""
cb3_b2_pagecarry_migrate.py  (S119 CB-3 Option B, Phase B-2 — PRODUCTION)
─────────────────────────────────────────────────────────────────────────
Surgical per-source replace of the 39 marker-bearing vault sources so every
Channel-B chunk carries a resolvable `=== Page N ===` (CB-3 north star).

Design (Leonard-approved S119, corrected after §3 divergence):
  - chunking = build_wiki_index.chunk_text_with_page_carry  (CANONICAL — the
    exact code B-1 measured; NOT update_g04's divergent chunker)
  - id scheme = build_wiki_index: vault_{source_id}_{sha256(text)[:16]}
  - transport = update_g04_supabase.py proven pattern: per-source
    DELETE ?source_id=eq.X  ->  batched INSERT (Prefer: return=minimal)
  - bypasses build_wiki_index's (broken vs live corpus) hash-dedup entirely
  - only the 39 marker source_ids are touched; all other Supabase rows
    (74 marker-less + role/stat/guideline) are NEVER queried/deleted

Safety:
  - default = DRY-RUN (no mutation). Pass --execute to actually mutate.
  - phase 1 embeds ALL first (no mutation); only then per-source DELETE+INSERT,
    so an embedding failure mutates nothing.
  - wiki_index.json backed up to dev/init_backup/<ts>/ before local rewrite.
  - per-source fail-stop with explicit source id (re-runnable).

Run from repo root:
  python3 dev/cb3_b2_pagecarry_migrate.py            # dry-run
  python3 dev/cb3_b2_pagecarry_migrate.py --execute  # real (Leonard-approved)
"""
import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw  # canonical chunker / hash / loaders

SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
WIKI_INDEX_PATH = REPO_ROOT / "dev" / "knowledge" / "wiki_index.json"
TABLE = "wiki_chunks"
EMBED_URL = "https://api.openai.com/v1/embeddings"
EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH = 96
UPLOAD_BATCH = 50
PAGE_RE = bw.PAGE_MARKER_RE


def _env(name: str) -> str:
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{name}=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def embed(texts, api_key):
    out = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = texts[i:i + EMBED_BATCH]
        r = requests.post(
            EMBED_URL,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={"model": EMBED_MODEL, "input": batch}, timeout=90,
        )
        if r.status_code != 200:
            raise SystemExit(f"OpenAI {r.status_code}: {r.text[:300]}")
        data = sorted(r.json()["data"], key=lambda x: x["index"])
        out.extend(d["embedding"] for d in data)
        print(f"    embedded {min(i+EMBED_BATCH,len(texts))}/{len(texts)}",
              end="\r", flush=True)
        time.sleep(0.25)
    print()
    return out


def sb_count(sid, key):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Prefer": "count=exact", "Range": "0-0"},
        params={"source_id": f"eq.{sid}", "select": "id"}, timeout=30)
    cr = r.headers.get("Content-Range", "")
    return int(cr.split("/")[-1]) if "/" in cr and cr.split("/")[-1].isdigit() else -1


def sb_delete(sid, key):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?source_id=eq.{sid}",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "Prefer": "return=representation"}, timeout=60)
    if r.status_code not in (200, 204):
        raise SystemExit(f"DELETE {sid} -> {r.status_code}: {r.text[:200]}")
    try:
        j = r.json()
        return len(j) if isinstance(j, list) else -1
    except Exception:
        return -1


def sb_upload(rows, key):
    for i in range(0, len(rows), UPLOAD_BATCH):
        b = rows[i:i + UPLOAD_BATCH]
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/{TABLE}",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json",
                     "Prefer": "return=minimal"},
            json=b, timeout=90)
        if r.status_code not in (200, 201):
            raise SystemExit(f"UPLOAD {r.status_code}: {r.text[:300]}")
        time.sleep(0.2)


def build_rows(src):
    """
    Page-carried chunk rows for one source. De-dupes by chunk id within the
    source (identical text -> identical sha256 -> identical pkey id): repetitive
    tabular sources (stat_enrolment_*) emit byte-identical chunks which would
    otherwise 409 on the 2nd insert. Mirrors upload_wiki_to_supabase.py's
    seen_ids guard (the proven pattern this driver must fully reuse).
    """
    rows = []
    seen = set()
    for ch in bw.chunk_text_with_page_carry(src["text"]):
        h = bw.text_hash(ch)
        cid = f"vault_{src['source_id']}_{h}"
        if cid in seen:
            continue
        seen.add(cid)
        rows.append({
            "id": cid, "hash": h, "text": ch,
            "source_id": src["source_id"], "title": src["title"],
            "url": src["url"], "topic": src["topic"],
            "content_type": src["content_type"], "fact_type": src["fact_type"],
            "role": None, "school_level": None, "reference_year": None,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="actually mutate Supabase + wiki_index.json")
    ap.add_argument("--only", default="",
                    help="comma-separated source_ids to process (subset; "
                         "used for scoped recovery — others left untouched)")
    ap.add_argument("--skip-local", action="store_true",
                    help="do NOT rewrite local wiki_index.json (use for partial "
                         "recovery runs to avoid a mixed old/new local artifact; "
                         "Supabase is the query-authoritative store)")
    args = ap.parse_args()
    mode = "EXECUTE" if args.execute else "DRY-RUN"
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    okey = _env("OPENAI_API_KEY")
    skey = _env("SUPABASE_SERVICE_KEY")
    if not okey or not skey:
        raise SystemExit("Missing OPENAI_API_KEY / SUPABASE_SERVICE_KEY in backend/.env")

    targets = [s for s in bw.load_vault_sources() if PAGE_RE.search(s["text"])]
    if only:
        targets = [s for s in targets if s["source_id"] in only]
        missing = only - {s["source_id"] for s in targets}
        if missing:
            raise SystemExit(f"--only ids not marker-bearing/known: {sorted(missing)}")
    print("=" * 74)
    print(f"CB-3 B-2 surgical page-carry migrate — {mode} — {len(targets)} sources"
          + (f"  (scoped --only)" if only else ""))
    print("=" * 74)

    # Phase 1: chunk + embed ALL (NO mutation yet)
    plan = []
    tot_new = 0
    for src in sorted(targets, key=lambda s: s["source_id"]):
        rows = build_rows(src)
        tot_new += len(rows)
        plan.append((src["source_id"], rows))
    print(f"Phase 1: {tot_new} page-carried chunks built (canonical chunker).")

    if not args.execute:
        for sid, rows in plan:
            old = sb_count(sid, skey)
            print(f"  {sid:<30} DELETE {old:>4} -> INSERT {len(rows):>4}")
        print(f"\nDRY-RUN only — nothing mutated. Total INSERT {tot_new}.")
        return

    print("Phase 1b: embedding all chunks (no mutation until done)...")
    for sid, rows in plan:
        vecs = embed([r["text"] for r in rows], okey)
        for r, v in zip(rows, vecs):
            r["embedding"] = v
        print(f"  embedded {sid} ({len(rows)})")

    # Backup local wiki_index.json before any rewrite
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    bdir = REPO_ROOT / "dev" / "init_backup" / ts
    bdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WIKI_INDEX_PATH, bdir / "wiki_index.json")
    print(f"Backup: {bdir / 'wiki_index.json'}")

    # Phase 2: per-source DELETE -> upload -> verify
    results = []
    for sid, rows in plan:
        old = sb_count(sid, skey)
        deleted = sb_delete(sid, skey)
        sb_upload(rows, skey)
        new = sb_count(sid, skey)
        ok = (new == len(rows))
        results.append((sid, old, deleted, len(rows), new, ok))
        print(f"  {sid:<30} del={deleted:>4} ins={len(rows):>4} "
              f"now={new:>4} {'OK' if ok else 'MISMATCH!!'}")
        if not ok:
            raise SystemExit(f"ABORT at {sid}: post-count {new} != expected {len(rows)}")

    # Phase 3: update local wiki_index.json (replace processed sources' chunks).
    # Skipped on scoped recovery runs: a partial rewrite would make local a
    # mixed old/new artifact. Supabase is the query-authoritative store; local
    # wiki_index.json is a build/backup artifact and is left fully-consistent
    # (all-old) + the divergence documented, rather than partially mixed.
    if args.skip_local:
        print("Phase 3 SKIPPED (--skip-local): local wiki_index.json left "
              "untouched (Supabase authoritative; divergence documented).")
    else:
        idx = json.loads(WIKI_INDEX_PATH.read_text(encoding="utf-8"))
        tids = {sid for sid, _ in plan}
        kept = [c for c in idx["chunks"] if c.get("source_id") not in tids]
        new_all = []
        for _, rows in plan:
            new_all.extend(rows)
        idx["chunks"] = kept + new_all
        idx.setdefault("_meta", {})["total_chunks"] = len(idx["chunks"])
        idx["_meta"]["cb3_b2_pagecarry_at"] = ts
        WIKI_INDEX_PATH.write_text(
            json.dumps(idx, ensure_ascii=False), encoding="utf-8")
        print(f"local wiki_index.json: kept {len(kept)} + new {len(new_all)} "
              f"= {len(idx['chunks'])}")

    tot_del = sum(r[2] for r in results)
    tot_ins = sum(r[3] for r in results)
    print("=" * 74)
    print(f"DONE: {len(results)} sources | DELETED {tot_del} -> "
          f"INSERTED {tot_ins} | all per-source counts OK")
    print("=" * 74)


if __name__ == "__main__":
    main()
