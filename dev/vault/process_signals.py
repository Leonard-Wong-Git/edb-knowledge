#!/usr/bin/env python3
"""
process_signals.py — Policy Signals → Channel A Auto-Pipeline

Reads dev/knowledge/policy_signals.json and for each pending signal:
  1. Downloads the EDB Circular PDF
  2. Converts to text via pdftotext (with === Page N === markers)
  3. Writes a vault extract file
  4. Calls extract_candidates.py --append to add Channel A candidates
  5. Registers source in source_registry.json
  6. Updates signal status to "auto_processed"

Usage:
  # Process all pending signals
  python3 dev/vault/process_signals.py

  # Process a single signal by ID (works for pending_review OR download_failed)
  python3 dev/vault/process_signals.py --signal-id sig_edbc002_2026

  # Retry all download_failed signals
  python3 dev/vault/process_signals.py --retry-failed

  # Dry-run: show what would happen, don't write anything
  python3 dev/vault/process_signals.py --dry-run

  # Download + extract only (skip extract_candidates.py)
  python3 dev/vault/process_signals.py --no-candidates

Environment:
  OPENAI_API_KEY — required (checked in backend/.env then os.environ)
"""

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SIGNALS_FILE = REPO_ROOT / "dev" / "knowledge" / "policy_signals.json"
SOURCE_REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
VAULT_DIR = REPO_ROOT / "dev" / "vault"
EXTRACT_SCRIPT = REPO_ROOT / "dev" / "vault" / "extract_candidates.py"
CANDIDATE_QUEUE = REPO_ROOT / "dev" / "knowledge" / "candidate_queue.json"

# Max pages to extract from PDF (keep consistent with batch approach)
MAX_PDF_PAGES = 80

# ---------------------------------------------------------------------------
# Signal helpers
# ---------------------------------------------------------------------------

def load_signals() -> dict:
    """Load policy_signals.json."""
    if not SIGNALS_FILE.exists():
        print(f"ERROR: {SIGNALS_FILE} not found", file=sys.stderr)
        sys.exit(1)
    return json.loads(SIGNALS_FILE.read_text(encoding="utf-8"))


def save_signals(data: dict):
    """Write policy_signals.json back to disk."""
    SIGNALS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


RETRYABLE_STATUSES = {"pending_review", "download_failed", "extract_failed"}


def get_pending_signals(
    data: dict,
    signal_id: str | None = None,
    retry_failed: bool = False
) -> list[dict]:
    """Return signals to process, optionally filtered by signal_id or including failed ones."""
    signals = data.get("signals", [])

    if retry_failed:
        eligible = [s for s in signals if s.get("status") in RETRYABLE_STATUSES]
    else:
        eligible = [s for s in signals if s.get("status") == "pending_review"]

    if signal_id:
        # When --signal-id is given, match any retryable status
        matched = [s for s in signals
                   if s.get("signal_id") == signal_id
                   and s.get("status") in RETRYABLE_STATUSES]
        if not matched:
            print(f"ERROR: Signal '{signal_id}' not found or not retryable "
                  f"(must be one of: {', '.join(sorted(RETRYABLE_STATUSES))})", file=sys.stderr)
            sys.exit(1)
        return matched

    return eligible


# ---------------------------------------------------------------------------
# Source ID generation
# ---------------------------------------------------------------------------

def circular_id_to_source_id(circular_id: str) -> str:
    """
    Convert circular ID to source_id slug.

    Examples:
      EDBC002/2026  →  edbc002_2026
      EDBCM057/2024 →  edbcm057_2024
      EDBC13/2025   →  edbc013_2025
    """
    # Normalise: strip spaces, uppercase
    cid = circular_id.strip().upper()

    # Match patterns like EDBC002/2026 or EDBCM057/2024 or EDBC13/2025
    m = re.match(r"(EDBCM?)(\d+)/(\d{4})", cid)
    if m:
        prefix = m.group(1).lower()          # "edbc" or "edbcm"
        number = m.group(2).zfill(3)          # zero-pad to 3 digits
        year = m.group(3)
        return f"{prefix}{number}_{year}"

    # Fallback: lowercase + replace / with _
    return circular_id.lower().replace("/", "_").replace(" ", "_")


def source_id_exists(source_id: str) -> bool:
    """Check if source_id already registered in source_registry.json."""
    if not SOURCE_REGISTRY.exists():
        return False
    try:
        reg = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        sources = reg.get("sources", [])
        return any(s.get("source_id") == source_id for s in sources)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# PDF download
# ---------------------------------------------------------------------------

def _make_ssl_context() -> ssl.SSLContext:
    """
    Create SSL context that works on macOS without system cert bundle issues.
    First tries the standard context (uses certifi if installed), then falls
    back to unverified context for gov.hk servers where macOS cert chain
    lookup fails.
    """
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        return ctx
    except ImportError:
        pass

    # Try default context first
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        pass

    # Last resort: skip verification (acceptable for official .gov.hk PDFs)
    ctx = ssl._create_unverified_context()
    print("  ⚠️  SSL: using unverified context (macOS cert chain issue)", file=sys.stderr)
    return ctx


def download_pdf(url: str, dest_path: Path, dry_run: bool = False) -> bool:
    """Download PDF from URL to dest_path. Returns True on success."""
    if dry_run:
        print(f"  [DRY-RUN] Would download: {url}", file=sys.stderr)
        print(f"  [DRY-RUN] → {dest_path}", file=sys.stderr)
        return True

    print(f"  ⬇️  Downloading {url}", file=sys.stderr)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; EDB-K1-Bot/1.0)",
            "Accept": "application/pdf,*/*"
        }
    )
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Try with proper SSL first, fall back to unverified if cert chain fails
    for attempt, ctx in enumerate([_make_ssl_context(), ssl._create_unverified_context()]):
        try:
            with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
                dest_path.write_bytes(response.read())
            size_kb = dest_path.stat().st_size // 1024
            if attempt > 0:
                print(f"  ⚠️  Downloaded via unverified SSL (macOS cert issue)", file=sys.stderr)
            print(f"  ✅ Downloaded {size_kb} KB → {dest_path.name}", file=sys.stderr)
            return True
        except ssl.SSLError:
            if attempt == 0:
                print(f"  ⚠️  SSL verify failed, retrying without verification...", file=sys.stderr)
                continue
            print(f"  ❌ SSL error persists", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  ❌ Download failed: {e}", file=sys.stderr)
            return False

    return False


# ---------------------------------------------------------------------------
# PDF → text extraction
# ---------------------------------------------------------------------------

def _pdftotext_available() -> bool:
    """Check if pdftotext (poppler) is available on the system."""
    try:
        result = subprocess.run(["which", "pdftotext"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def _extract_with_pdftotext(pdf_path: Path, max_pages: int) -> str | None:
    """Extract text using pdftotext (poppler). Returns text or None."""
    # Get total page count
    total_pages = max_pages
    try:
        info_result = subprocess.run(
            ["pdfinfo", str(pdf_path)], capture_output=True, text=True
        )
        for line in info_result.stdout.splitlines():
            if line.startswith("Pages:"):
                total_pages = int(line.split(":")[1].strip())
                break
    except Exception:
        pass

    pages_to_extract = min(total_pages, max_pages)
    print(f"  📄 [pdftotext] Extracting {pages_to_extract}/{total_pages} pages", file=sys.stderr)

    all_text_parts = []
    for page_num in range(1, pages_to_extract + 1):
        try:
            result = subprocess.run(
                ["pdftotext", "-f", str(page_num), "-l", str(page_num), str(pdf_path), "-"],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            page_text = result.stdout.strip()
            if page_text:
                all_text_parts.append(f"=== Page {page_num} ===\n{page_text}")
        except Exception as e:
            print(f"  ⚠️  Page {page_num}: {e}", file=sys.stderr)

    return "\n\n".join(all_text_parts) if all_text_parts else None


def _extract_with_pypdf(pdf_path: Path, max_pages: int) -> str | None:
    """
    Extract text using pypdf (pure Python fallback, no system tools needed).
    Auto-installs pypdf if missing.
    """
    try:
        import pypdf
    except ImportError:
        print("  ⏳ pypdf not installed — installing now...", file=sys.stderr)
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pypdf", "--quiet"],
                check=True
            )
            import pypdf
            print("  ✅ pypdf installed", file=sys.stderr)
        except Exception as e:
            print(f"  ❌ Could not install pypdf: {e}", file=sys.stderr)
            return None

    try:
        reader = pypdf.PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        pages_to_extract = min(total_pages, max_pages)
        print(f"  📄 [pypdf] Extracting {pages_to_extract}/{total_pages} pages", file=sys.stderr)

        all_text_parts = []
        for i in range(pages_to_extract):
            page_num = i + 1
            try:
                page_text = reader.pages[i].extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    all_text_parts.append(f"=== Page {page_num} ===\n{page_text}")
            except Exception as e:
                print(f"  ⚠️  Page {page_num}: {e}", file=sys.stderr)

        return "\n\n".join(all_text_parts) if all_text_parts else None

    except Exception as e:
        print(f"  ❌ pypdf extraction failed: {e}", file=sys.stderr)
        return None


def pdf_to_text_with_pages(pdf_path: Path, max_pages: int = MAX_PDF_PAGES) -> str | None:
    """
    Convert PDF to text with === Page N === markers.
    Tries pdftotext (poppler) first; falls back to pypdf (pure Python).
    Returns combined text string, or None on failure.
    """
    if _pdftotext_available():
        result = _extract_with_pdftotext(pdf_path, max_pages)
        if result:
            return result
        print("  ⚠️  pdftotext returned empty, trying pypdf...", file=sys.stderr)

    print("  ℹ️  Using pypdf fallback (tip: brew install poppler for better results)", file=sys.stderr)
    return _extract_with_pypdf(pdf_path, max_pages)


# ---------------------------------------------------------------------------
# Vault extract writer
# ---------------------------------------------------------------------------

def write_vault_extract(
    signal: dict,
    source_id: str,
    text: str,
    vault_dir: Path,
    dry_run: bool = False
) -> Path | None:
    """Write vault extract .txt file with standard header. Returns path or None."""
    extract_dir = vault_dir / source_id
    extract_path = extract_dir / f"extract_{source_id}.txt"

    title = signal.get("title", f"教育局通告 {signal.get('circular_id', '')}")
    url = signal.get("url", "")
    circular_id = signal.get("circular_id", "")

    # Derive year for version_label
    year_match = re.search(r"/(\d{4})", circular_id)
    year = year_match.group(1) if year_match else datetime.now().strftime("%Y")

    # Topic from trigger_reason
    ai_topics = signal.get("trigger_reason", {}).get("ai_topics_matched", ["curriculum"])
    topic_tags = "/".join(ai_topics) if ai_topics else "curriculum"

    header = f"""# {title}
# source_id: {source_id}
# title: {title}
# fact_type: policy
# topic_tags: {topic_tags}
# url: {url}
# circular_id: {circular_id}
# extracted: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
# auto_processed: true
# ============================================================
"""

    full_text = header + "\n" + text

    if dry_run:
        print(f"  [DRY-RUN] Would write vault extract: {extract_path}", file=sys.stderr)
        print(f"  [DRY-RUN] Header preview:\n{header}", file=sys.stderr)
        return extract_path

    extract_dir.mkdir(parents=True, exist_ok=True)
    extract_path.write_text(full_text, encoding="utf-8")
    print(f"  ✅ Vault extract written: {extract_path} ({len(full_text)} chars)", file=sys.stderr)
    return extract_path


# ---------------------------------------------------------------------------
# Run extract_candidates.py
# ---------------------------------------------------------------------------

def run_extract_candidates(extract_path: Path, dry_run: bool = False) -> int:
    """
    Call extract_candidates.py --append on the vault extract file.
    Returns number of new candidates added (estimated from output), or -1 on error.
    """
    if dry_run:
        print(f"  [DRY-RUN] Would run: python3 {EXTRACT_SCRIPT.name} --append {extract_path.name}", file=sys.stderr)
        return 0

    print(f"  🔬 Running extract_candidates.py...", file=sys.stderr)
    try:
        result = subprocess.run(
            [sys.executable, str(EXTRACT_SCRIPT), "--append", str(extract_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        # Print stderr (the progress output)
        if result.stderr:
            for line in result.stderr.splitlines():
                print(f"    {line}", file=sys.stderr)

        if result.returncode != 0:
            print(f"  ❌ extract_candidates.py failed (exit {result.returncode})", file=sys.stderr)
            return -1

        # Parse number from output like "Queue now contains N candidate(s)"
        added = 0
        for line in result.stderr.splitlines():
            m = re.search(r"(\d+) candidates passed validation", line)
            if m:
                added = int(m.group(1))
        return added

    except Exception as e:
        print(f"  ❌ Error running extract_candidates.py: {e}", file=sys.stderr)
        return -1


# ---------------------------------------------------------------------------
# Source registry update
# ---------------------------------------------------------------------------

def register_source(signal: dict, source_id: str, dry_run: bool = False):
    """Add new source entry to source_registry.json."""
    title = signal.get("title", f"教育局通告 {signal.get('circular_id', '')}")
    url = signal.get("url", "")
    circular_id = signal.get("circular_id", "")
    year_match = re.search(r"/(\d{4})", circular_id)
    year = year_match.group(1) if year_match else "unknown"
    ai_topics = signal.get("trigger_reason", {}).get("ai_topics_matched", ["curriculum"])

    new_source = {
        "source_id": source_id,
        "title": title,
        "title_en": None,
        "title_short": f"通告 {circular_id}",
        "url_landing": None,
        "url_primary": url,
        "source_type": "pdf",
        "authority": "edb",
        "spine": False,
        "topic_tags": ai_topics,
        "access_mode": "public",
        "status": "verified",
        "version_label": year,
        "last_checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "supersedes": None,
        "notes": f"Auto-registered via process_signals.py from policy signal. Signal ID: {signal.get('signal_id', '')}",
        "freshness_metadata": None
    }

    if dry_run:
        print(f"  [DRY-RUN] Would register source in source_registry:", file=sys.stderr)
        print(f"    source_id: {source_id}", file=sys.stderr)
        print(f"    title: {title}", file=sys.stderr)
        return

    try:
        reg = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        reg["sources"].append(new_source)
        SOURCE_REGISTRY.write_text(
            json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print(f"  ✅ Source registered: {source_id}", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️  Could not update source_registry: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main processing loop
# ---------------------------------------------------------------------------

def process_signal(
    signal: dict,
    data: dict,
    dry_run: bool = False,
    no_candidates: bool = False
) -> bool:
    """Process one signal. Returns True on success."""
    signal_id = signal.get("signal_id", "?")
    circular_id = signal.get("circular_id", "?")
    url = signal.get("url", "")

    print(f"\n{'─' * 60}", file=sys.stderr)
    print(f"📡 Signal: {signal_id}", file=sys.stderr)
    print(f"   Circular: {circular_id}", file=sys.stderr)
    print(f"   Title: {signal.get('title', '?')}", file=sys.stderr)
    print(f"   URL: {url}", file=sys.stderr)

    if not url:
        print(f"  ❌ No URL in signal — skipping", file=sys.stderr)
        return False

    # 1. Generate source_id
    source_id = circular_id_to_source_id(circular_id)
    print(f"  → source_id: {source_id}", file=sys.stderr)

    # 2. Check for duplicate
    if source_id_exists(source_id):
        print(f"  ⚠️  source_id '{source_id}' already in registry — skipping to avoid duplicate", file=sys.stderr)
        _update_signal_status(data, signal_id, "skipped_duplicate", source_id=source_id, notes="Already in source_registry")
        if not dry_run:
            save_signals(data)
        return False

    # 3. Download PDF
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / f"{source_id}.pdf"

        if not download_pdf(url, pdf_path, dry_run=dry_run):
            _update_signal_status(data, signal_id, "download_failed", notes=f"Failed to download {url}")
            if not dry_run:
                save_signals(data)
            return False

        if not dry_run and not pdf_path.exists():
            print(f"  ❌ PDF file missing after download", file=sys.stderr)
            return False

        # 4. PDF → text
        if dry_run:
            print(f"  [DRY-RUN] Would run pdftotext on downloaded PDF", file=sys.stderr)
            text = "[dry-run placeholder text]"
        else:
            text = pdf_to_text_with_pages(pdf_path)
            if not text:
                print(f"  ❌ Failed to extract text from PDF", file=sys.stderr)
                _update_signal_status(data, signal_id, "extract_failed", notes="pdftotext returned empty")
                save_signals(data)
                return False
            print(f"  ✅ Extracted {len(text)} chars from PDF", file=sys.stderr)

        # 5. Write vault extract
        extract_path = write_vault_extract(signal, source_id, text, VAULT_DIR, dry_run=dry_run)
        if not extract_path:
            return False

        # 6. Run extract_candidates.py (Channel A)
        candidates_added = 0
        if not no_candidates:
            candidates_added = run_extract_candidates(extract_path, dry_run=dry_run)
            if candidates_added < 0:
                print(f"  ⚠️  extract_candidates.py failed — vault extract still saved", file=sys.stderr)

        # 7. Register source
        register_source(signal, source_id, dry_run=dry_run)

        # 8. Update signal status
        _update_signal_status(
            data, signal_id, "auto_processed",
            source_id=source_id,
            candidates_added=candidates_added,
            notes=f"Auto-processed. {candidates_added} Channel A candidates added."
        )
        if not dry_run:
            save_signals(data)

        print(f"\n  ✅ Done: {signal_id} → {source_id} ({candidates_added} candidates)", file=sys.stderr)
        return True


def _update_signal_status(
    data: dict,
    signal_id: str,
    status: str,
    source_id: str | None = None,
    candidates_added: int | None = None,
    notes: str = ""
):
    """Update a signal's status fields in-place."""
    for s in data.get("signals", []):
        if s.get("signal_id") == signal_id:
            s["status"] = status
            s["processed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if source_id is not None:
                s["source_id"] = source_id
            if candidates_added is not None:
                s["channel_a_candidates_added"] = candidates_added
            if notes:
                s["notes"] = (s.get("notes", "") + " " + notes).strip()
            break


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Process EDB Policy Signals: download → extract → Channel A candidates"
    )
    parser.add_argument(
        "--signal-id", metavar="ID",
        help="Process a specific signal by ID (works for pending_review, download_failed, extract_failed)"
    )
    parser.add_argument(
        "--retry-failed", action="store_true",
        help="Also retry signals with status download_failed or extract_failed"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without downloading or writing files"
    )
    parser.add_argument(
        "--no-candidates", action="store_true",
        help="Skip extract_candidates.py (download + vault extract only)"
    )

    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("📡 EDB Policy Signals Processor", file=sys.stderr)
    if args.dry_run:
        print("   MODE: DRY-RUN (no files written)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    data = load_signals()
    pending = get_pending_signals(data, signal_id=args.signal_id, retry_failed=args.retry_failed)

    if not pending:
        print(f"\nℹ️  No pending signals to process.", file=sys.stderr)
        return

    print(f"\n📋 Found {len(pending)} pending signal(s)", file=sys.stderr)

    success = 0
    for signal in pending:
        ok = process_signal(
            signal, data,
            dry_run=args.dry_run,
            no_candidates=args.no_candidates
        )
        if ok:
            success += 1

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"✅ Processed {success}/{len(pending)} signals successfully", file=sys.stderr)
    if not args.dry_run and success > 0:
        print(f"   → Check K1 Dashboard → 知識提煉 to review new candidates", file=sys.stderr)
        print(f"   → Run build_wiki_index.py to update Channel B", file=sys.stderr)


if __name__ == "__main__":
    main()
