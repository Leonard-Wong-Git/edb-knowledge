#!/usr/bin/env python3
"""
_build_kg_chunks.py  (S162)
───────────────────────────
One-off: chunk the 2 new KG 2026 vault sources with the CANONICAL
build_wiki_index chunker (same as Supabase ingest → byte-identical chunk ids)
and merge their rows into _work/all_chunks.json so the checklist pipeline
(prep/mech-verify) can see them. Idempotent: removes any pre-existing rows for
these source_ids before appending. Backs up all_chunks.json first.

  cd ".../Draft" && python3 dev/checklists/_work/_build_kg_chunks.py [--check]
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]            # …/Draft
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw                              # canonical chunker

ALL_CHUNKS = REPO_ROOT / "dev" / "checklists" / "_work" / "all_chunks.json"
KG_SOURCES = ["kg_admin_guide_2026", "kg_operation_manual_2026"]


def rows_for(source_id: str):
    srcs = bw.load_vault_sources(filter_source=source_id)
    if not srcs:
        sys.exit(f"ERROR: no vault source for '{source_id}'")
    src = srcs[0]
    src["text"] = src["text"].replace("\x00", "")
    rows, seen = [], set()
    for ch in bw.chunk_text_with_page_carry(src["text"]):
        h = bw.text_hash(ch)
        cid = f"vault_{source_id}_{h}"
        if cid in seen:
            continue
        seen.add(cid)
        rows.append({
            "id": cid,
            "source_id": source_id,
            "content_type": "vault_extract",
            "text": ch,
        })
    return rows


def main():
    check_only = "--check" in sys.argv[1:]
    new_rows = []
    for sid in KG_SOURCES:
        r = rows_for(sid)
        print(f"  {sid}: {len(r)} chunks")
        new_rows.extend(r)

    all_chunks = json.loads(ALL_CHUNKS.read_text(encoding="utf-8"))
    before = len(all_chunks)
    kept = [c for c in all_chunks if c.get("source_id") not in KG_SOURCES]
    removed = before - len(kept)
    merged = kept + new_rows
    print(f"all_chunks: before={before} removed_existing_kg={removed} "
          f"new={len(new_rows)} after={len(merged)}")

    if check_only:
        print("(--check: not written)")
        return

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bak = ALL_CHUNKS.with_suffix(f".json.bak_{ts}")
    bak.write_text(json.dumps(all_chunks, ensure_ascii=False), encoding="utf-8")
    ALL_CHUNKS.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    print(f"→ backed up to {bak.name}; wrote {ALL_CHUNKS.name} ({len(merged)} chunks)")


if __name__ == "__main__":
    main()
