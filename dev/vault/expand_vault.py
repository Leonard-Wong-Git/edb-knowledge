#!/usr/bin/env python3
"""
expand_vault.py — Full AI Vault Expansion Pipeline
════════════════════════════════════════════════════
Reads source_registry.json, finds all sources without vault extracts, then:

  Phase 1  --fetch   Download + extract text → vault extract .txt files
  Phase 2  --embed   Chunk + embed + upsert to Supabase

Both phases can run together or separately (fetch first, review, then embed).

Usage (from repo root):
  # Dry-run: show what would be processed
  python3 dev/vault/expand_vault.py --dry-run

  # Fetch only (creates vault .txt files, no API calls)
  python3 dev/vault/expand_vault.py --fetch

  # Embed + upload only (processes existing vault .txt files not yet in Supabase)
  SUPABASE_SERVICE_KEY=sb-... python3 dev/vault/expand_vault.py --embed

  # Full pipeline (fetch + embed + upload)
  SUPABASE_SERVICE_KEY=sb-... python3 dev/vault/expand_vault.py --fetch --embed

  # Filter by topic or source type
  python3 dev/vault/expand_vault.py --fetch --topic hr
  python3 dev/vault/expand_vault.py --fetch --source-type pdf
  python3 dev/vault/expand_vault.py --fetch --sources g06,g15,g21

  # Limit number of sources (useful for testing)
  python3 dev/vault/expand_vault.py --fetch --embed --limit 5

Environment:
  OPENAI_API_KEY      — from backend/.env (auto-loaded) or environment
  SUPABASE_SERVICE_KEY — required only for --embed
  SUPABASE_URL        — optional, defaults to project URL

Output:
  dev/vault/<source_id>/extract_<source_id>.txt  — raw extracted text
  dev/knowledge/wiki_index.json                  — updated with new chunks
  Supabase public.wiki_chunks                    — new chunks inserted

Notes:
  - Already-extracted sources are skipped automatically (idempotent)
  - PDF extraction uses pdftotext (poppler) — must be installed
  - HTML extraction uses requests + BeautifulSoup4
  - Large PDFs capped at CHUNK_CAP chunks per source (default 300)
  - Supabase upsert uses merge-duplicates (safe to re-run)
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Dependencies ──────────────────────────────────────────────────────────────

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests --break-system-packages")
    sys.exit(1)

# BeautifulSoup is optional (only needed for HTML sources)
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "dev" / "source" / "source_registry.json"
VAULT_DIR = REPO_ROOT / "dev" / "vault"
WIKI_INDEX_PATH = REPO_ROOT / "dev" / "knowledge" / "wiki_index.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")

def _load_supabase_service_key() -> str:
    """Load SUPABASE_SERVICE_KEY from environment or backend/.env."""
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not key and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text().splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_SERVICE_KEY=") and not line.startswith("#"):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return key

SUPABASE_SERVICE_KEY = _load_supabase_service_key()

OPENAI_EMBED_MODEL = "text-embedding-3-small"
CHUNK_MAX_CHARS = 600
CHUNK_OVERLAP = 80
CHUNK_CAP = 300          # max chunks per source (prevents huge sources dominating)
DOWNLOAD_TIMEOUT = 60    # seconds
DOWNLOAD_DELAY = 1.5     # seconds between downloads (politeness)
EMBED_BATCH_SIZE = 20    # texts per OpenAI embedding call
TABLE = "wiki_chunks"

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── Key loading ───────────────────────────────────────────────────────────────

def load_openai_key() -> str:
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text().splitlines():
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print("❌ OPENAI_API_KEY not found in backend/.env or environment")
        sys.exit(1)
    return key

# ── Source registry ───────────────────────────────────────────────────────────

def load_registry() -> list[dict]:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)["sources"]


def source_override(source_id: str, key: str, default: int) -> int:
    """Per-source integer override from source_registry.json, else the global default.

    `chunk_cap`       — ceiling on chunks per source (the global cap drops the TAIL, which
                        on a long reference document discards its appendices).
    `chunk_max_chars` — target chunk size. Row-per-line tables want one row per chunk: a
                        600-char chunk holds ~6 establishment rows, and the extra rows
                        dilute the one the query is about (measured on staff_est_pri:
                        「12班小學有幾多個學位教師」 scores 0.521 against a 6-row chunk and
                        0.590 against the single row).
    """
    for src in load_registry():
        if src.get("source_id") == source_id:
            val = src.get(key)
            if isinstance(val, int) and val > 0:
                return val
            break
    return default

def get_extracted_source_ids() -> set[str]:
    """Return source IDs that already have a vault extract .txt file."""
    extracted = set()
    if not VAULT_DIR.exists():
        return extracted
    for d in VAULT_DIR.iterdir():
        if d.is_dir():
            txts = [f for f in d.iterdir() if f.suffix == ".txt" and "extract" in f.name.lower()]
            if txts:
                extracted.add(d.name)
    return extracted

def get_indexed_source_ids() -> set[str]:
    """Return source IDs already present in wiki_index.json."""
    if not WIKI_INDEX_PATH.exists():
        return set()
    with open(WIKI_INDEX_PATH, encoding="utf-8") as f:
        wiki = json.load(f)
    return {c["source_id"] for c in wiki.get("chunks", [])}

# ── Text extraction ───────────────────────────────────────────────────────────

def extract_pdf_text(url: str) -> str | None:
    """Download PDF from URL and extract text using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("  ⚠️  PyMuPDF not installed. Run: pip3 install pymupdf --break-system-packages")
        return None

    print(f"  ↓ Downloading PDF…")
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=DOWNLOAD_TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return None

    content_type = resp.headers.get("content-type", "")
    if "html" in content_type.lower():
        print(f"  ⚠️  URL returned HTML (not a PDF). Needs manual handling.")
        return None

    try:
        doc = fitz.open(stream=resp.content, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()
        text = "\n".join(pages_text)
        if len(text.strip()) < 100:
            print(f"  ⚠️  PyMuPDF returned very little text ({len(text)} chars) — may be a scanned PDF")
        else:
            print(f"  ✅ Extracted {len(text):,} chars from PDF ({len(pages_text)} pages)")
        return text
    except Exception as e:
        print(f"  ❌ PyMuPDF extraction failed: {e}")
        return None


def extract_html_text(url: str) -> str | None:
    """Fetch HTML page and extract main content text."""
    if not BS4_AVAILABLE:
        print("  ⚠️  BeautifulSoup not installed. Run: pip install beautifulsoup4 lxml --break-system-packages")
        return None

    print(f"  ↓ Fetching HTML…")
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=DOWNLOAD_TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ Fetch failed: {e}")
        return None

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove nav, header, footer, scripts, styles
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "noscript", "iframe", "form"]):
        tag.decompose()

    # Try to find main content area
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find(id=re.compile(r"content|main|body", re.I)) or
        soup.find(class_=re.compile(r"content|main|article", re.I)) or
        soup.find("div", class_=re.compile(r"container|wrapper", re.I)) or
        soup.body
    )

    if not main:
        main = soup

    # Get text, clean whitespace
    text = main.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    # Collapse runs of 3+ blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text.strip()) < 200:
        print(f"  ⚠️  Very little text extracted from HTML ({len(text)} chars)")
    else:
        print(f"  ✅ Extracted {len(text):,} chars from HTML")

    return text.strip() or None

# ── Vault file writing ────────────────────────────────────────────────────────

def write_vault_extract(source: dict, body_text: str) -> Path:
    """Write the vault extract .txt file for a source."""
    sid = source["source_id"]
    vault_folder = VAULT_DIR / sid
    vault_folder.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    topic_tags = ",".join(source.get("topic_tags", ["general"]))
    url = source.get("url_primary") or source.get("url_landing", "")
    title = source.get("title", sid)
    source_type = source.get("source_type", "pdf")

    header = (
        f"# source_id: {sid}\n"
        f"# title: {title}\n"
        f"# fact_type: policy\n"
        f"# topic_tags: {topic_tags}\n"
        f"# url: {url}\n"
        f"# source_type: {source_type}\n"
        f"# extracted: {today}\n"
        f"# pipeline: expand_vault.py (auto)\n"
        "# ============================================================\n\n"
    )

    extract_path = vault_folder / f"extract_{sid}.txt"
    extract_path.write_text(header + body_text, encoding="utf-8")
    return extract_path

# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str, max_chars: int = CHUNK_MAX_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = re.split(r"\n{2,}", text.strip())
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) > max_chars:
                lines = para.split("\n")
                sub = ""
                for line in lines:
                    if len(sub) + len(line) + 1 <= max_chars:
                        sub = (sub + "\n" + line).strip() if sub else line
                    else:
                        if sub:
                            chunks.append(sub)
                        sub = line
                current = sub if sub else ""
            else:
                current = para

    if current:
        chunks.append(current)

    # Add overlap
    overlapped: list[str] = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap > 0:
            prev_tail = chunks[i - 1][-overlap:]
            chunk = (prev_tail + " " + chunk)[: max_chars * 2]
        overlapped.append(chunk)

    return overlapped


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def parse_vault_header(text: str) -> dict:
    meta = {}
    for line in text.splitlines():
        if not line.startswith("#"):
            break
        if ":" in line:
            key, _, val = line[1:].partition(":")
            meta[key.strip()] = val.strip()
    return meta


def extract_vault_body(text: str) -> str:
    lines = text.splitlines()
    body = []
    in_header = True
    for line in lines:
        if in_header and (line.startswith("#") or line.strip() == ""):
            if line.strip() == "" and not in_header:
                body.append(line)
            continue
        in_header = False
        body.append(line)
    return "\n".join(body).strip()


def build_chunks_from_vault_file(extract_path: Path) -> list[dict]:
    """Build chunk dicts from a vault extract .txt file (no embeddings yet)."""
    raw = extract_path.read_text(encoding="utf-8")
    meta = parse_vault_header(raw)
    body = extract_vault_body(raw)

    sid = meta.get("source_id", extract_path.parent.name)
    title = meta.get("title", sid)
    url = meta.get("url", "")
    fact_type = meta.get("fact_type", "policy")

    # Infer topic from topic_tags
    tag_str = meta.get("topic_tags", "")
    topic = tag_str.split(",")[0].strip() if tag_str else "general"

    texts = chunk_text(body, max_chars=source_override(sid, "chunk_max_chars", CHUNK_MAX_CHARS))
    # Apply cap. CHUNK_CAP keeps one huge source from dominating the corpus, but it drops
    # the TAIL, so on a long reference document it silently discards the appendices — where
    # the Codes of Aid keep their staff establishment schedules. A source may raise its own
    # ceiling with `chunk_cap` in source_registry.json; every other source is unaffected.
    # (Retrieval already caps how many results one source_id may occupy, so a larger source
    # cannot crowd the result list either way.) Record the reason in the registry entry.
    cap = source_override(sid, "chunk_cap", CHUNK_CAP)
    if len(texts) > cap:
        print(f"  ✂️  Capped at {cap} chunks (was {len(texts)})")
        texts = texts[:cap]

    chunks = []
    for text in texts:
        h = text_hash(text)
        chunks.append({
            "id": f"vault_{sid}_{h}",
            "hash": h,
            "text": text,
            "source_id": sid,
            "title": title,
            "url": url,
            "topic": topic,
            "content_type": "vault_extract",
            "fact_type": fact_type,
            "role": None,
            "school_level": None,
            "reference_year": None,
        })
    return chunks

# ── Embedding ─────────────────────────────────────────────────────────────────

def embed_texts(texts: list[str], api_key: str) -> list[list[float]]:
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(
        url, headers=headers,
        json={"model": OPENAI_EMBED_MODEL, "input": texts},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]


def embed_chunks(chunks: list[dict], api_key: str) -> list[dict]:
    """Add embeddings to chunk dicts in-place."""
    texts = [c["text"] for c in chunks]
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        embs = embed_texts(batch, api_key)
        all_embeddings.extend(embs)
        print(f"    {min(i + EMBED_BATCH_SIZE, len(texts))}/{len(texts)} embedded", end="\r")
        time.sleep(0.3)
    print()
    for chunk, emb in zip(chunks, all_embeddings):
        chunk["embedding"] = emb
    return chunks

# ── Supabase operations ───────────────────────────────────────────────────────

def supabase_delete_source(source_id: str, service_key: str) -> int:
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?source_id=eq.{source_id}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Prefer": "return=representation",
    }
    resp = requests.delete(url, headers=headers, timeout=30)
    if resp.status_code in (200, 204):
        try:
            return len(resp.json()) if isinstance(resp.json(), list) else 0
        except Exception:
            return 0
    return 0


def _sanitize_text(text: str) -> str:
    """Strip null bytes (chr(0)) which PostgreSQL text columns reject."""
    return text.replace('\x00', '').replace('', '')


def supabase_upsert_batch(batch: list[dict], service_key: str) -> bool:
    # Sanitize all text fields before upload
    clean = []
    for row in batch:
        clean.append({k: (_sanitize_text(v) if isinstance(v, str) else v)
                      for k, v in row.items()})
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    resp = requests.post(url, headers=headers, json=clean, timeout=60)
    if resp.status_code in (200, 201):
        return True
    print(f"\n  ❌ Upsert failed {resp.status_code}: {resp.text[:300]}")
    return False

# ── wiki_index.json update ────────────────────────────────────────────────────

def update_wiki_index(new_chunks_by_source: dict[str, list[dict]]) -> None:
    """Replace chunks for updated sources in local wiki_index.json."""
    if not WIKI_INDEX_PATH.exists():
        print("  ⚠️  wiki_index.json not found, skipping local update")
        return

    with open(WIKI_INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    updated_sids = set(new_chunks_by_source.keys())
    old_count = len(index["chunks"])
    index["chunks"] = [c for c in index["chunks"] if c.get("source_id") not in updated_sids]
    removed = old_count - len(index["chunks"])

    added = 0
    for chunks in new_chunks_by_source.values():
        index["chunks"].extend(chunks)
        added += len(chunks)

    with open(WIKI_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)

    print(f"  📝 wiki_index.json: -{removed} old, +{added} new chunks")

# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_fetch(sources_to_process: list[dict], dry_run: bool) -> list[Path]:
    """Phase 1: Download + extract text, write vault .txt files."""
    print(f"\n{'═'*60}")
    print(f"Phase 1 — FETCH ({len(sources_to_process)} sources)")
    print(f"{'═'*60}")

    if not BS4_AVAILABLE:
        html_count = sum(1 for s in sources_to_process if s["source_type"] == "html")
        if html_count > 0:
            print(f"⚠️  {html_count} HTML sources require BeautifulSoup:")
            print("   pip install beautifulsoup4 lxml --break-system-packages")

    created: list[Path] = []
    skipped = 0
    failed = 0

    for i, source in enumerate(sources_to_process, 1):
        sid = source["source_id"]
        stype = source["source_type"]
        url = source.get("url_primary") or source.get("url_landing", "")
        title = source.get("title", sid)[:60]

        print(f"\n[{i}/{len(sources_to_process)}] {sid} ({stype})")
        print(f"  {title}")
        print(f"  {url[:80]}")

        if dry_run:
            print("  [dry-run] skipped")
            continue

        # Skip unsupported types
        if stype in ("index",):
            print(f"  ⏭  source_type '{stype}' — manual handling needed")
            skipped += 1
            continue

        if stype == "docx":
            print(f"  ⏭  source_type 'docx' — manual handling needed")
            skipped += 1
            continue

        if stype == "xlsx":
            print(f"  ⏭  source_type 'xlsx' — statistical data (handled by build_stat_facts.py)")
            skipped += 1
            continue

        # Extract text
        body_text: str | None = None

        if stype == "pdf":
            if not url.endswith(".pdf"):
                print(f"  ⚠️  URL doesn't end in .pdf — may need manual download")
                # Try anyway
            body_text = extract_pdf_text(url)

        elif stype == "html":
            body_text = extract_html_text(url)

        if not body_text or len(body_text.strip()) < 200:
            print(f"  ❌ Insufficient text extracted, skipping")
            failed += 1
        else:
            path = write_vault_extract(source, body_text)
            created.append(path)
            print(f"  ✅ Saved → {path.relative_to(REPO_ROOT)}")

        # Politeness delay
        if i < len(sources_to_process):
            time.sleep(DOWNLOAD_DELAY)

    print(f"\n{'─'*60}")
    print(f"Fetch complete: {len(created)} created, {skipped} skipped, {failed} failed")
    return created


def run_embed(sources_to_embed: list[dict], dry_run: bool, api_key: str) -> None:
    """Phase 2: Chunk + embed + upsert to Supabase."""
    print(f"\n{'═'*60}")
    print(f"Phase 2 — EMBED + UPLOAD ({len(sources_to_embed)} sources)")
    print(f"{'═'*60}")

    if not SUPABASE_SERVICE_KEY and not dry_run:
        print("❌ SUPABASE_SERVICE_KEY required for --embed")
        print("   SUPABASE_SERVICE_KEY=sb-... python3 dev/vault/expand_vault.py --embed")
        return

    new_chunks_by_source: dict[str, list[dict]] = {}
    total_chunks = 0
    total_uploaded = 0

    for i, source in enumerate(sources_to_embed, 1):
        sid = source["source_id"]
        vault_folder = VAULT_DIR / sid
        txts = sorted(vault_folder.glob("extract_*.txt")) if vault_folder.exists() else []

        if not txts:
            print(f"\n[{i}/{len(sources_to_embed)}] {sid} — no extract .txt found, skipping")
            continue

        print(f"\n[{i}/{len(sources_to_embed)}] {sid}")

        # Build chunks from ALL extract files for this source
        all_chunks: list[dict] = []
        for txt_path in txts:
            chunks = build_chunks_from_vault_file(txt_path)
            all_chunks.extend(chunks)
            print(f"  📄 {txt_path.name}: {len(chunks)} chunks")

        # Deduplicate by id
        seen: set[str] = set()
        deduped = []
        for c in all_chunks:
            if c["id"] not in seen:
                seen.add(c["id"])
                deduped.append(c)

        print(f"  → {len(deduped)} unique chunks total")
        total_chunks += len(deduped)

        if dry_run:
            print("  [dry-run] skipped embedding")
            continue

        # Embed
        print(f"  🔮 Embedding…")
        try:
            embed_chunks(deduped, api_key)
        except Exception as e:
            print(f"  ❌ Embedding failed: {e}")
            continue

        # Delete old Supabase rows for this source
        deleted = supabase_delete_source(sid, SUPABASE_SERVICE_KEY)
        if deleted:
            print(f"  🗑️  Deleted {deleted} old Supabase chunks")

        # Upsert new chunks
        BATCH_SIZE = 50
        uploaded = 0
        ok = True
        for j in range(0, len(deduped), BATCH_SIZE):
            batch = deduped[j:j + BATCH_SIZE]
            if not supabase_upsert_batch(batch, SUPABASE_SERVICE_KEY):
                ok = False
                break
            uploaded += len(batch)
            time.sleep(0.2)

        if ok:
            print(f"  ✅ Uploaded {uploaded} chunks to Supabase")
            total_uploaded += uploaded
            new_chunks_by_source[sid] = deduped
        else:
            print(f"  ❌ Upload failed after {uploaded} chunks")

    # Update local wiki_index.json
    if new_chunks_by_source:
        print(f"\n📝 Updating wiki_index.json…")
        update_wiki_index(new_chunks_by_source)

    print(f"\n{'─'*60}")
    print(f"Embed complete: {total_chunks} chunks prepared, {total_uploaded} uploaded to Supabase")
    if dry_run:
        print("(dry-run: no actual embedding or upload)")

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vault expansion pipeline: fetch → embed → Supabase"
    )
    parser.add_argument("--fetch", action="store_true", help="Phase 1: download + extract text")
    parser.add_argument("--embed", action="store_true", help="Phase 2: chunk + embed + upload")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, no downloads or API calls")
    parser.add_argument("--topic", help="Filter by topic tag (e.g. hr, curriculum, general)")
    parser.add_argument("--source-type", dest="source_type", help="Filter by source_type (pdf, html)")
    parser.add_argument("--sources", help="Comma-separated list of source_ids to process")
    parser.add_argument("--limit", type=int, help="Limit number of sources to process")
    parser.add_argument("--force", action="store_true", help="Re-extract even if vault file already exists")

    args = parser.parse_args()

    if not args.fetch and not args.embed and not args.dry_run:
        parser.print_help()
        print("\n💡 Quick start:")
        print("  python3 dev/vault/expand_vault.py --dry-run")
        print("  python3 dev/vault/expand_vault.py --fetch")
        print("  SUPABASE_SERVICE_KEY=sb-... python3 dev/vault/expand_vault.py --embed")
        sys.exit(0)

    # Load sources
    all_sources = load_registry()
    already_extracted = get_extracted_source_ids()
    already_indexed = get_indexed_source_ids()

    print(f"Registry: {len(all_sources)} sources total")
    print(f"Already extracted (vault .txt): {len(already_extracted)}")
    print(f"Already indexed (wiki_index): {len(already_indexed)}")

    # Apply filters
    candidate_sources = [s for s in all_sources if s.get("status") != "superseded"]

    if args.sources:
        sid_filter = set(args.sources.split(","))
        candidate_sources = [s for s in candidate_sources if s["source_id"] in sid_filter]
        print(f"Filtered to {len(candidate_sources)} by --sources")

    if args.topic:
        candidate_sources = [s for s in candidate_sources
                              if args.topic in s.get("topic_tags", [])]
        print(f"Filtered to {len(candidate_sources)} by topic={args.topic}")

    if args.source_type:
        candidate_sources = [s for s in candidate_sources
                              if s.get("source_type") == args.source_type]
        print(f"Filtered to {len(candidate_sources)} by source_type={args.source_type}")

    # Determine what to fetch vs embed
    if args.fetch or args.dry_run:
        to_fetch = candidate_sources if args.force else [
            s for s in candidate_sources if s["source_id"] not in already_extracted
        ]
        if args.limit:
            to_fetch = to_fetch[:args.limit]
        print(f"\nTo fetch: {len(to_fetch)} sources")
        for s in to_fetch[:10]:
            print(f"  {s['source_id']} ({s['source_type']}) — {s['title'][:50]}")
        if len(to_fetch) > 10:
            print(f"  ... and {len(to_fetch)-10} more")

    if args.embed or args.dry_run:
        to_embed = [
            s for s in candidate_sources if s["source_id"] in already_extracted
        ] if not args.fetch else candidate_sources  # if fetching too, embed what we just fetched
        to_embed = [s for s in to_embed if s["source_id"] not in already_indexed] if not args.force else to_embed
        if args.limit and not args.fetch:
            to_embed = to_embed[:args.limit]
        print(f"\nTo embed: {len(to_embed)} sources")

    if args.dry_run:
        print("\n[dry-run] No downloads or API calls made.")
        if args.fetch and 'to_fetch' in dir():
            run_fetch(to_fetch, dry_run=True)
        if args.embed and 'to_embed' in dir():
            api_key = ""
            run_embed(to_embed, dry_run=True, api_key=api_key)
        return

    api_key = load_openai_key() if args.embed else ""

    if args.fetch:
        run_fetch(to_fetch, dry_run=False)
        # After fetching, re-check what's now extracted for the embed phase
        already_extracted = get_extracted_source_ids()

    if args.embed:
        # Embed all candidate sources that now have vault files
        to_embed_now = [s for s in candidate_sources
                        if s["source_id"] in already_extracted
                        and (args.force or s["source_id"] not in already_indexed)]
        if args.limit and not args.fetch:
            to_embed_now = to_embed_now[:args.limit]
        run_embed(to_embed_now, dry_run=False, api_key=api_key)

    print(f"\n✅ Done.")
    print(f"\nVerify in Supabase SQL Editor:")
    print(f"  select source_id, count(*) from public.wiki_chunks group by source_id order by count desc;")


if __name__ == "__main__":
    main()
