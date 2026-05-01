#!/usr/bin/env python3
"""
mempalace_sync.py — K1 EDB Knowledge Platform × MemPalace 同步工具
====================================================================
將 session 記錄寫入 MemPalace，或在 session 開始時查詢相關歷史。

Usage:
  python3 dev/mempalace_sync.py write              # 寫入最新 session log 條目
  python3 dev/mempalace_sync.py query "rate limit" # 查詢相關過去記錄
  python3 dev/mempalace_sync.py list               # 列出所有已儲存條目
  python3 dev/mempalace_sync.py stats              # 統計 palace 狀態

MemPalace 設定（須與 /Users/leonard/mempalace 安裝一致）:
  Palace path:  /Users/leonard/mempalace/palace
  Wing:         claude_edb_knowledge
  Venv:         /Users/leonard/mempalace/.venv
"""

import sys
import re
import json
import datetime
from pathlib import Path

PALACE_PATH = Path("/Users/leonard/mempalace/palace")
WING_NAME   = "claude_edb_knowledge"
REPO_ROOT   = Path(__file__).parent.parent
SESSION_LOG = REPO_ROOT / "dev" / "SESSION_LOG.md"
HANDOFF     = REPO_ROOT / "dev" / "SESSION_HANDOFF.md"

# ── MemPalace client ────────────────────────────────────────────────────────

def get_collection():
    try:
        import chromadb
    except ImportError:
        print("❌  chromadb not found. Run:")
        print("    source /Users/leonard/mempalace/.venv/bin/activate")
        sys.exit(1)

    client = chromadb.PersistentClient(
        path=str(PALACE_PATH),
        settings=chromadb.Settings(
            anonymized_telemetry=False,
            allow_reset=False,
        )
    )
    # Get or create the wing (collection)
    try:
        col = client.get_collection(WING_NAME)
    except Exception:
        col = client.create_collection(
            WING_NAME,
            metadata={"hnsw:num_threads": 1}   # recovery workaround
        )
    return col


# ── Parse SESSION_LOG.md ────────────────────────────────────────────────────

def parse_sessions(limit=5):
    """Parse the most recent N session blocks from SESSION_LOG.md."""
    content = SESSION_LOG.read_text(encoding="utf-8")
    # Split on ## YYYY-MM-DD Session N
    blocks = re.split(r'(?=## \d{4}-\d{2}-\d{2} Session \d+)', content)
    sessions = []
    for block in blocks:
        m = re.match(r'## (\d{4}-\d{2}-\d{2}) Session (\d+) — (.+)', block)
        if not m:
            continue
        date_str, session_num, title = m.group(1), m.group(2), m.group(3)

        # Extract key fields
        summary_m = re.search(r'\*\*Summary:\*\*\s*(.+?)(?=\n-|\n#|\Z)', block, re.DOTALL)
        done_m    = re.search(r'\*\*Done:\*\*\n(.*?)(?=\n- \*\*(?!Done)|\n###|\Z)', block, re.DOTALL)
        next_m    = re.search(r'\*\*Next:\*\*\s*(.+?)(?=\n###|\Z)', block, re.DOTALL)

        summary = summary_m.group(1).strip() if summary_m else ""
        done    = done_m.group(1).strip() if done_m else ""
        nxt     = next_m.group(1).strip() if next_m else ""

        sessions.append({
            "id":      f"session_{session_num}_{date_str}",
            "date":    date_str,
            "session": int(session_num),
            "title":   title.strip(),
            "summary": summary,
            "done":    done,
            "next":    nxt,
            "raw":     block[:2000],   # first 2000 chars for full text search
        })

    # Sort by session number descending, return latest N
    sessions.sort(key=lambda x: x["session"], reverse=True)
    return sessions[:limit]


# ── Commands ────────────────────────────────────────────────────────────────

def cmd_write():
    """Write recent sessions to MemPalace."""
    col = get_collection()
    sessions = parse_sessions(limit=10)

    if not sessions:
        print("⚠️  No sessions found in SESSION_LOG.md")
        return

    added = 0
    skipped = 0
    for s in sessions:
        # Build the document text for embedding
        doc_text = f"Session {s['session']} ({s['date']}): {s['title']}\n\n"
        doc_text += f"Summary: {s['summary']}\n\n"
        if s['done']:
            doc_text += f"Done:\n{s['done']}\n\n"
        if s['next']:
            doc_text += f"Next: {s['next']}\n"

        metadata = {
            "session":  s['session'],
            "date":     s['date'],
            "title":    s['title'],
            "type":     "session_log",
            "project":  "edb_knowledge_platform",
        }

        try:
            # Upsert: update if exists, insert if new
            col.upsert(
                ids=[s['id']],
                documents=[doc_text],
                metadatas=[metadata],
            )
            print(f"  ✓  Session {s['session']} ({s['date']}) — {s['title'][:60]}")
            added += 1
        except Exception as e:
            print(f"  ⚠️  Session {s['session']}: {e}")
            skipped += 1

    # Also write current handoff snapshot
    handoff_text = HANDOFF.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    col.upsert(
        ids=["handoff_current"],
        documents=[handoff_text[:3000]],
        metadatas={
            "type":    "handoff_snapshot",
            "date":    today,
            "project": "edb_knowledge_platform",
        },
    )
    print(f"  ✓  SESSION_HANDOFF.md snapshot → handoff_current")

    print(f"\n✅  Written {added} sessions + handoff snapshot. Skipped: {skipped}")
    print(f"   Total in wing '{WING_NAME}': {col.count()} entries")


def cmd_query(query_text: str, n_results: int = 5):
    """Query MemPalace for relevant past records."""
    col = get_collection()
    if col.count() == 0:
        print("⚠️  MemPalace is empty. Run: python3 dev/mempalace_sync.py write")
        return

    results = col.query(
        query_texts=[query_text],
        n_results=min(n_results, col.count()),
        include=["documents", "metadatas", "distances"],
    )

    print(f"\n🔍  Query: \"{query_text}\"\n")
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, distances):
        similarity = round(1 - dist, 3)
        label = meta.get("title") or meta.get("type", "unknown")
        date  = meta.get("date", "")
        sess  = meta.get("session", "")
        tag   = f"Session {sess} ({date})" if sess else date
        print(f"  [{similarity:.3f}] {tag} — {label[:70]}")
        # Show first 300 chars of document
        preview = doc[:300].replace("\n", " ")
        print(f"           {preview}…\n")


def cmd_list():
    """List all entries in MemPalace."""
    col = get_collection()
    count = col.count()
    print(f"\n📚  Wing '{WING_NAME}': {count} entries\n")
    if count == 0:
        print("  (empty — run 'write' to populate)")
        return

    results = col.get(include=["metadatas"])
    entries = list(zip(results["ids"], results["metadatas"]))
    entries.sort(key=lambda x: (x[1].get("type",""), -x[1].get("session", 0)))

    for id_, meta in entries:
        sess  = meta.get("session", "")
        date  = meta.get("date", "")
        title = meta.get("title") or meta.get("type", "")
        tag   = f"Session {sess} ({date})" if sess else f"{meta.get('type','')} ({date})"
        print(f"  {id_:<40} {tag} — {title[:50]}")
    print()


def cmd_stats():
    """Show palace statistics."""
    col = get_collection()
    count = col.count()
    print(f"\n📊  MemPalace Stats")
    print(f"   Palace path:  {PALACE_PATH}")
    print(f"   Wing:         {WING_NAME}")
    print(f"   Total entries: {count}")

    if count > 0:
        results = col.get(include=["metadatas"])
        types = {}
        for meta in results["metadatas"]:
            t = meta.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        print(f"   By type:")
        for t, n in sorted(types.items()):
            print(f"     {t}: {n}")
    print()


# ── Entry point ─────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = args[0]
    if cmd == "write":
        cmd_write()
    elif cmd == "query":
        if len(args) < 2:
            print("Usage: python3 dev/mempalace_sync.py query \"your question\"")
            sys.exit(1)
        cmd_query(args[1], n_results=int(args[2]) if len(args) > 2 else 5)
    elif cmd == "list":
        cmd_list()
    elif cmd == "stats":
        cmd_stats()
    else:
        print(f"❌  Unknown command: {cmd}")
        print("Commands: write | query <text> | list | stats")
        sys.exit(1)


if __name__ == "__main__":
    main()
