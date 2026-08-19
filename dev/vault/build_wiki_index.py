#!/usr/bin/env python3
"""
build_wiki_index.py — Channel B: LLM-Wiki Index Builder

Builds a searchable vector index from all knowledge sources for Channel B.
Channel B is independent of the Circular System (Channel A pipeline).
Circular System integration is PAUSED pending quality testing.

Sources indexed:
  1. Vault extract.txt files (raw EDB document chunks)
  2. role_facts.json (Channel A approved policy facts — for reference only)
  3. stat_facts.json (auto-approved statistical facts)
  4. Guidelines registry (document titles + URLs)

Token efficiency design:
  - Chunks are ≤600 chars (aligned with Circular System budget)
  - Each chunk embedded once; re-runs skip already-embedded chunks (hash check)
  - Embeddings stored locally in wiki_index.json — no re-embedding per query

Usage:
  cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"

  # Build full index from all sources
  python3 dev/vault/build_wiki_index.py

  # Build from specific vault source only
  python3 dev/vault/build_wiki_index.py --source circ_edbc24017

  # Force re-embed everything (ignore hash cache)
  python3 dev/vault/build_wiki_index.py --force

  # Dry-run: show what would be indexed without calling API
  python3 dev/vault/build_wiki_index.py --dry-run

Output:
  dev/knowledge/wiki_index.json
  Schema: { "_meta": {...}, "chunks": [ {id, text, embedding, source_id, ...} ] }

Environment:
  OPENAI_API_KEY — required (checked in backend/.env then os.environ)
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault"
KNOWLEDGE_DIR = REPO_ROOT / "dev" / "knowledge"
OUTPUT_PATH = KNOWLEDGE_DIR / "wiki_index.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_MAX_CHARS = 600   # aligned with Circular System 600-char budget
CHUNK_OVERLAP   = 60    # overlap to preserve context across chunk boundaries

VALID_TOPICS = ["finance", "hr", "curriculum", "activity", "student", "it", "general"]

# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and not key.startswith("sk-..."):
                    return key
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    print("ERROR: OPENAI_API_KEY not found.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, max_chars: int = CHUNK_MAX_CHARS,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks at sentence/line boundaries.
    Preserves context by overlapping adjacent chunks.
    """
    # Split on sentence-ending punctuation or newlines
    sentences = re.split(r'(?<=[。！？\n])', text)
    chunks = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(current) + len(sent) > max_chars and current:
            chunks.append(current.strip())
            # Overlap: keep last `overlap` chars of current chunk
            current = current[-overlap:] + sent if len(current) > overlap else sent
        else:
            current = (current + sent) if current else sent

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) >= 20]  # discard tiny fragments


# Matches the backend's extractFirstPage() regex (searchChannelB.ts) exactly,
# so a marker carried here is resolvable to a page number at query time.
PAGE_MARKER_RE = re.compile(r'={2,}\s*Page\s*(\d+)\s*={2,}', re.IGNORECASE)


def chunk_text_with_page_carry(text: str, max_chars: int = CHUNK_MAX_CHARS,
                               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    CB-3 (S119 Option B): chunk vault text, then make every chunk page-resolvable.

    `=== Page N ===` markers are sparse (one per source page) so a chunk falling
    between two markers carries none and extractFirstPage() returns nothing.
    Here we carry the last-seen page forward: a marker-less chunk is prefixed
    with the page where the preceding chunk ended.

    Invariants:
      - Chunks before the first marker (cover / front-matter) are left unchanged.
      - A source with NO page markers at all yields byte-identical output to
        chunk_text() — its text_hash (and thus Supabase chunk id) is unchanged,
        so the 74 marker-less sources are untouched by this change.
    """
    return carry_pages(chunk_text(text, max_chars, overlap))


# S207 — a crawled multi-page HTML source writes `=== <section> ===` between pages,
# the same shape as `=== Page N ===` but naming a sub-page instead of a page number.
# Whitespace-delimited rather than line-anchored: expand_vault's chunker prepends an
# overlap tail joined with a space, so a marker that owned its own line in the extract
# arrives mid-line in the chunk ("…培育課程。 === chapter-one ===\n[資料庫]…"). An
# anchored pattern silently matched only the first marker of the whole document.
# Page markers are recognised here and discarded by carry_sections() rather than
# excluded in the pattern — a lookahead is defeated by backtracking over the
# whitespace run, which is how the first draft read `=== Page 12 ===` as a section.
SECTION_MARKER_RE = re.compile(r'(?:^|\s)={2,}[ \t]*([^=\n]{1,120}?)[ \t]*={2,}(?=\s|$)')
_PAGE_LABEL_RE = re.compile(r'^Page[ \t]+\d+$', re.IGNORECASE)


def carry_sections(chunks: list[str]) -> list[str | None]:
    """
    S207: the section-carry rule, shaped after carry_pages() and sharing its
    contract — chunker-agnostic, takes an already-chunked list, returns one entry
    per chunk. Unlike carry_pages() it does NOT rewrite the text: a section
    resolves to a URL (a per-chunk column) rather than to a read-time parse, so
    there is nothing to inject into the chunk body.

    Invariants relied on by callers (asserted in dev/vault/test_carry_rules.py):
      - Chunks before the first marker return None (no section known yet).
      - A chunk list with NO section markers yields all-None, so a marker-less
        source keeps its header URL and is untouched.
      - `=== Page 12 ===` is never read as a section label, and never clears a
        section already carried — the two marker kinds coexist in one extract
        (g17 names an attachment PDF, then pages inside it).
    """
    current = None
    out: list[str | None] = []
    for ch in chunks:
        # Remove page markers FIRST. Two adjacent page markers on one line
        # (`=== Page 5 === 6 (Blank Page) === Page 6 ===`) otherwise present the
        # closing `===` of one and the opening `===` of the next as a single
        # section marker wrapped around the text between them — a false positive
        # that reads body text as a section name. Measured corpus-wide before the
        # fix: 847 phantom labels across 135 sources, e.g. '(Blank Page)', '第二章概論'.
        labels = [lab.strip() for lab in SECTION_MARKER_RE.findall(PAGE_MARKER_RE.sub("\n", ch))]
        labels = [lab for lab in labels if lab and not _PAGE_LABEL_RE.match(lab)]
        if labels:
            current = labels[-1]             # carry the section this chunk ends in
        out.append(current)
    return out


def carry_pages(chunks: list[str]) -> list[str]:
    """
    S206: the page-carry rule itself, lifted out of chunk_text_with_page_carry so
    the second ingestion pipeline can reuse it. Chunker-agnostic on purpose — it
    takes an already-chunked list. expand_vault.py splits text differently from
    this module, and their chunk hashes must stay independent, so they share the
    RULE without sharing the chunker (AGENTS §3b: one definition per rule).

    Invariants relied on by both callers:
      - Chunks before the first marker (cover / front-matter) are left unchanged.
      - A chunk list with NO markers at all is returned byte-identical, so a
        marker-less source keeps its text_hash (and thus its Supabase chunk id).
    """
    current_page = None
    out = []
    for ch in chunks:
        found = PAGE_MARKER_RE.findall(ch)
        if found:
            current_page = found[-1]            # carry the page this chunk ends on
            out.append(ch)                       # already resolvable — unchanged
        elif current_page is not None:
            out.append(f"=== Page {current_page} ===\n{ch}")
        else:
            out.append(ch)                       # before first marker — unchanged
    return out


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Source loaders
# ---------------------------------------------------------------------------

def load_vault_sources(filter_source: str = None) -> list[dict]:
    """Load all vault extract.txt files as raw text chunks."""
    sources = []
    for txt_file in sorted(VAULT_DIR.rglob("*.txt")):
        # Skip scripts
        if txt_file.parent == VAULT_DIR:
            continue
        text = txt_file.read_text(encoding="utf-8")
        meta = {}
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("# "):
                break
            m = re.match(r"^#\s+(\w+):\s*(.+)$", line)
            if m:
                meta[m.group(1)] = m.group(2).strip()

        source_id = meta.get("source_id", txt_file.stem)
        if filter_source and source_id != filter_source:
            continue

        # Remove header lines before chunking
        body = re.sub(r"^(# .+\n)+", "", text, flags=re.MULTILINE).strip()

        sources.append({
            "source_id": source_id,
            "title": meta.get("title", source_id),
            "url": meta.get("url", ""),
            "fact_type": meta.get("fact_type", "policy"),
            "topic": meta.get("topic_tags", "general"),
            "content_type": "vault_extract",
            "text": body,
            "file": str(txt_file.relative_to(REPO_ROOT)),
        })
    return sources


def load_role_facts() -> list[dict]:
    """Load Channel A approved facts as individual chunk items."""
    path = REPO_ROOT / "role_facts.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = []
    for topic, topic_data in data.items():
        if topic == "_meta" or not isinstance(topic_data, dict):
            continue
        label = topic_data.get("_label", topic)
        source_refs = topic_data.get("_source_refs", [])
        # _source_refs can be list of strings (source IDs) or dicts with url
        first_ref = source_refs[0] if source_refs else None
        url = (first_ref.get("url", "") if isinstance(first_ref, dict)
               else "") if first_ref else ""

        for role, facts in topic_data.items():
            if role.startswith("_") or not isinstance(facts, list):
                continue
            for fact in facts:
                if isinstance(fact, str) and fact.strip():
                    items.append({
                        "source_id": f"role_facts_{topic}",
                        "title": f"EDB 知識庫：{label}",
                        "url": url,
                        "fact_type": "approved_policy",
                        "topic": topic,
                        "role": role,
                        "content_type": "approved_fact",
                        "text": fact.strip(),
                        "file": "role_facts.json",
                    })
    return items


def load_stat_facts() -> list[dict]:
    """Load auto-approved statistical facts."""
    path = KNOWLEDGE_DIR / "stat_facts.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = []
    for fact in data.get("facts", []):
        text = fact.get("fact", "").strip()
        if text:
            items.append({
                "source_id": fact.get("source_id", "stat"),
                "title": f"EDB 統計數據：{fact.get('school_level', '')}",
                "url": fact.get("source_url", ""),
                "fact_type": "statistical",
                "topic": fact.get("topic", "student"),
                "school_level": fact.get("school_level", ""),
                "reference_year": fact.get("reference_year", ""),
                "content_type": "stat_fact",
                "text": text,
                "file": "dev/knowledge/stat_facts.json",
            })
    return items


def load_guidelines() -> list[dict]:
    """Load guidelines registry entries as searchable items."""
    # Guidelines are embedded in the dashboard — read from the JS constant
    # Fallback: try guidelines.json at repo root
    path = REPO_ROOT / "guidelines.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = []
    guidelines = data if isinstance(data, list) else data.get("guidelines", [])
    for g in guidelines:
        title = g.get("title", "")
        url = g.get("url", "")
        category = g.get("category", "general")
        if title and url:
            text = f"{title}。類別：{category}。"
            if g.get("description"):
                text += g["description"]
            items.append({
                "source_id": g.get("id", "guideline"),
                "title": title,
                "url": url,
                "fact_type": "guideline_reference",
                "topic": "general",
                "content_type": "guideline",
                "text": text,
                "file": "guidelines.json",
            })
    return items


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_batch(api_key: str, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using OpenAI text-embedding-3-small."""
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    BATCH_SIZE = 100  # API limit per request

    all_vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        print(f"  🔢 Embedding batch {i//BATCH_SIZE + 1} "
              f"({len(batch)} texts)...", file=sys.stderr)
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        vectors = [item.embedding for item in sorted(response.data,
                                                      key=lambda x: x.index)]
        all_vectors.extend(vectors)

    return all_vectors


# ---------------------------------------------------------------------------
# Index I/O
# ---------------------------------------------------------------------------

def load_existing_index(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"_meta": {}, "chunks": []}


def save_index(index: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    size_kb = path.stat().st_size / 1024
    print(f"  💾 Saved wiki_index.json ({size_kb:.0f} KB)", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main build logic
# ---------------------------------------------------------------------------

def build_index(args):
    api_key = None if args.dry_run else load_api_key()

    # Load all sources
    print("📥 Loading sources...", file=sys.stderr)
    vault_sources = load_vault_sources(filter_source=args.source)
    role_facts    = [] if args.source else load_role_facts()
    stat_facts    = [] if args.source else load_stat_facts()
    guidelines    = [] if args.source else load_guidelines()

    print(f"  Vault extracts: {len(vault_sources)} files", file=sys.stderr)
    print(f"  Approved facts: {len(role_facts)} items", file=sys.stderr)
    print(f"  Stat facts:     {len(stat_facts)} items", file=sys.stderr)
    print(f"  Guidelines:     {len(guidelines)} items", file=sys.stderr)

    # Load existing index for hash-based dedup
    existing_index = load_existing_index(OUTPUT_PATH) if not args.force else {"chunks": []}
    existing_hashes = {c["hash"] for c in existing_index.get("chunks", [])
                       if "hash" in c}
    print(f"\n  Existing chunks in index: {len(existing_hashes)}", file=sys.stderr)

    # Build new chunks
    new_chunks = []

    # 1. Vault extracts → chunked (CB-3: page-carry so each chunk is page-resolvable)
    for src in vault_sources:
        for chunk_text_item in chunk_text_with_page_carry(src["text"]):
            h = text_hash(chunk_text_item)
            if h in existing_hashes and not args.force:
                continue
            new_chunks.append({
                "id": f"vault_{src['source_id']}_{h}",
                "hash": h,
                "text": chunk_text_item,
                "source_id": src["source_id"],
                "title": src["title"],
                "url": src["url"],
                "topic": src["topic"],
                "content_type": src["content_type"],
                "fact_type": src["fact_type"],
            })

    # 2. Approved facts → each fact is one chunk (already short)
    for item in role_facts:
        h = text_hash(item["text"])
        if h in existing_hashes and not args.force:
            continue
        new_chunks.append({
            "id": f"fact_{item['source_id']}_{h}",
            "hash": h,
            "text": item["text"],
            "source_id": item["source_id"],
            "title": item["title"],
            "url": item["url"],
            "topic": item["topic"],
            "role": item.get("role", "all_roles"),
            "content_type": "approved_fact",
            "fact_type": "approved_policy",
        })

    # 3. Stat facts → each fact is one chunk
    for item in stat_facts:
        h = text_hash(item["text"])
        if h in existing_hashes and not args.force:
            continue
        new_chunks.append({
            "id": f"stat_{item['source_id']}_{h}",
            "hash": h,
            "text": item["text"],
            "source_id": item["source_id"],
            "title": item["title"],
            "url": item["url"],
            "topic": item["topic"],
            "content_type": "stat_fact",
            "fact_type": "statistical",
            "school_level": item.get("school_level", ""),
            "reference_year": item.get("reference_year", ""),
        })

    # 4. Guidelines → each entry is one chunk
    for item in guidelines:
        h = text_hash(item["text"])
        if h in existing_hashes and not args.force:
            continue
        new_chunks.append({
            "id": f"guide_{item['source_id']}_{h}",
            "hash": h,
            "text": item["text"],
            "source_id": item["source_id"],
            "title": item["title"],
            "url": item["url"],
            "topic": item["topic"],
            "content_type": "guideline",
            "fact_type": "guideline_reference",
        })

    print(f"\n  New chunks to embed: {len(new_chunks)}", file=sys.stderr)
    if not new_chunks:
        print("  ✅ Index is up to date. Nothing to embed.", file=sys.stderr)
        return

    if args.dry_run:
        print("\n[DRY RUN] Sample chunks:")
        for c in new_chunks[:5]:
            print(f"  [{c['content_type']} / {c['source_id']}] {c['text'][:80]}...")
        print(f"\n  Total new chunks: {len(new_chunks)}")
        estimated_tokens = sum(len(c["text"]) // 4 for c in new_chunks)
        print(f"  Estimated tokens: ~{estimated_tokens:,}")
        print(f"  Estimated cost (text-embedding-3-small $0.02/1M): "
              f"~${estimated_tokens / 1_000_000 * 0.02:.4f}")
        return

    # Embed new chunks
    print(f"\n🔢 Embedding {len(new_chunks)} new chunks...", file=sys.stderr)
    texts_to_embed = [c["text"] for c in new_chunks]
    vectors = embed_batch(api_key, texts_to_embed)

    for chunk, vector in zip(new_chunks, vectors):
        chunk["embedding"] = vector

    # Merge with existing
    all_chunks = existing_index.get("chunks", []) + new_chunks

    # Build final index
    index = {
        "_meta": {
            "schema": "wiki_index_v1",
            "channel": "B",
            "embedding_model": EMBEDDING_MODEL,
            "chunk_max_chars": CHUNK_MAX_CHARS,
            "chunk_overlap": CHUNK_OVERLAP,
            "total_chunks": len(all_chunks),
            "built_at": datetime.now(timezone.utc).isoformat(),
            "sources": sorted({c["source_id"] for c in all_chunks}),
            "content_types": sorted({c["content_type"] for c in all_chunks}),
            "note": (
                "Channel B LLM-wiki index. "
                "NOT connected to Circular System (paused pending testing). "
                "Use wiki_search.py for queries."
            ),
        },
        "chunks": all_chunks,
    }

    save_index(index, OUTPUT_PATH)

    print(f"\n✅ Wiki index built:", file=sys.stderr)
    print(f"   Total chunks: {len(all_chunks)}", file=sys.stderr)
    by_type = {}
    for c in all_chunks:
        ct = c["content_type"]
        by_type[ct] = by_type.get(ct, 0) + 1
    for ct, count in sorted(by_type.items()):
        print(f"   {ct}: {count}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Channel B: Build LLM-wiki vector index")
    parser.add_argument("--source", default=None,
                        help="Only index this source_id (e.g. circ_edbc24017)")
    parser.add_argument("--force", action="store_true",
                        help="Re-embed all chunks even if already in index")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be indexed + cost estimate, no API calls")
    args = parser.parse_args()
    build_index(args)


if __name__ == "__main__":
    main()
