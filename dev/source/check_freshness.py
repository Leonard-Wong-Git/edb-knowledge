#!/usr/bin/env python3
"""
check_freshness.py
==================
Reads source_registry.json and verifies public source freshness.

Two-tier change detection (S139 hybrid upgrade):
  1. Cheap tier — HEAD request, compare Last-Modified / Content-Length / ETag
     against stored freshness_metadata.
  2. Confirm tier — when the cheap signal trips (or a hash needs seeding), GET the
     file and compare a raw-byte SHA-256 against the stored content_hash. The
     content hash is AUTHORITATIVE: it suppresses HEAD false-positives (EDB
     redirect / re-export churn) and confirms true content changes.

content_hash shares the same lifecycle as the other freshness_metadata fields:
it is seeded / refreshed only on a write-sync (non-dry-run). Scheduled dry-runs
detect drift against the last synced baseline and never persist, so they stay
cheap — only sources whose HEAD tripped AND already have a seeded hash are
downloaded for confirmation.

Outputs (in addition to the registry writeback):
  --changes-out PATH  Always writes a machine-readable change report (JSON) for
                      CI to consume (open/update a GitHub Issue). Default:
                      freshness_changes.json
  --ledger PATH       When given (write-sync only), renders a human Markdown
                      ledger of pending re-ingest work. Per FRESHNESS_GUIDE the
                      execution stays a manual gate — this only surfaces the
                      work, it does not perform it.

Usage: python3 check_freshness.py [--dry-run] [--verbose] [--limit N]
                                   [--changes-out PATH] [--ledger PATH]
"""

import json
import hashlib
import requests
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Constants
REGISTRY_PATH = Path("dev/source/source_registry.json")
HEAD_TIMEOUT = 15
GET_TIMEOUT = 60          # content download (large PDFs, e.g. g10 ~25MB)
HASH_CHUNK = 1 << 16      # 64 KiB streaming chunks
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get_headers(url: str) -> Optional[Dict[str, str]]:
    """Fetch HEAD headers for a URL (GET-fallback when HEAD is blocked)."""
    try:
        resp = requests.head(
            url,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
            timeout=HEAD_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.headers
        # Fallback to GET if HEAD is blocked but limit bytes
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
            timeout=HEAD_TIMEOUT,
            stream=True,
        )
        if resp.status_code == 200:
            h = dict(resp.headers)
            resp.close()
            return h
        return None
    except Exception as e:
        print(f"  ⚠️ Request failed for {url}: {e}")
        return None


def get_content_hash(url: str) -> Tuple[Optional[str], Optional[str]]:
    """GET the full body and return (sha256_hexdigest, error).

    Streams the response so large PDFs do not balloon memory. Hashes the raw
    bytes as received — good enough for change detection because execution stays
    a manual gate (a human judges any flagged change). Returns (None, reason) on
    failure.
    """
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
            timeout=GET_TIMEOUT,
            stream=True,
        )
        if resp.status_code != 200:
            resp.close()
            return None, f"HTTP {resp.status_code}"
        h = hashlib.sha256()
        for chunk in resp.iter_content(chunk_size=HASH_CHUNK):
            if chunk:
                h.update(chunk)
        resp.close()
        return h.hexdigest(), None
    except Exception as e:
        return None, str(e)


def classify_change(cheap_changed: bool, old_hash: Optional[str],
                    new_hash: Optional[str], hash_computed: bool) -> Tuple[bool, Optional[str]]:
    """Decide whether a source changed. Pure function — offline testable.

    The content hash is authoritative when a baseline hash exists and a fresh one
    was computed this run; otherwise degrade gracefully to the cheap HEAD signal.
    Returns (changed, confidence-label).
    """
    if old_hash and hash_computed and new_hash:
        if new_hash != old_hash:
            return True, "content-hash"
        return False, None  # equal hash → suppress HEAD false-positive
    if old_hash and not hash_computed:
        # had a baseline hash but could not fetch this run → fall back to cheap signal
        if cheap_changed:
            return True, "head-metadata (hash unavailable)"
        return False, None
    # no baseline hash yet → current HEAD behavior until a write-sync seeds it
    if cheap_changed:
        return True, "head-metadata (no baseline hash)"
    return False, None


def render_ledger(changed: List[Dict], today: str, checked: int, errors: int) -> str:
    """Render the human-facing pending re-ingest ledger (Markdown)."""
    lines = [
        "# Freshness Changes — Pending Manual Review",
        "",
        "<!-- AUTO-GENERATED by dev/source/check_freshness.py --ledger. Do not hand-edit; "
        "it is overwritten on each write-sync. -->",
        "",
        f"- Last sync: **{today}** (UTC)",
        f"- Checked: {checked} · Changed: **{len(changed)}** · Errors: {errors}",
        "",
        "> ⚠️ Detection only. Re-ingestion stays a **manual gate** "
        "(see `FRESHNESS_GUIDE.md` §3 + the manual page-carry pipeline: "
        "URL re-discovery → mojibake pre-flight → repage → cb3_b2 → SOURCE_SETS parity → deploy).",
        "",
    ]
    if not changed:
        lines.append("_No content changes detected at last sync._")
        return "\n".join(lines) + "\n"

    lines.append("| source_id | title | confidence | old_hash | new_hash | Last-Modified (old→new) |")
    lines.append("|---|---|---|---|---|---|")
    for c in changed:
        oh = (c.get("old_hash") or "—")[:12]
        nh = (c.get("new_hash") or "—")[:12]
        lm = c.get("last_modified") or {}
        lm_s = f"{lm.get('old') or '—'} → {lm.get('new') or '—'}"
        title = (c.get("title") or "").replace("|", "/")
        lines.append(
            f"| `{c['source_id']}` | {title} | {c.get('confidence','')} | `{oh}` | `{nh}` | {lm_s} |"
        )
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    """Offline deterministic assertions for the change-classification logic and
    ledger rendering. No network. Returns process exit code."""
    cases = [
        # (cheap_changed, old_hash, new_hash, hash_computed) -> (changed, confidence_substr_or_None)
        ("no baseline, cheap unchanged", (False, None, None, False), (False, None)),
        ("no baseline, cheap changed",   (True,  None, None, False), (True, "no baseline")),
        ("baseline, hash equal (suppress HEAD noise)", (True, "a"*64, "a"*64, True), (False, None)),
        ("baseline, hash differs",       (False, "a"*64, "b"*64, True), (True, "content-hash")),
        ("baseline, fetch failed + cheap changed", (True, "a"*64, "a"*64, False), (True, "hash unavailable")),
        ("baseline, fetch failed, cheap unchanged", (False, "a"*64, "a"*64, False), (False, None)),
        ("steady state (baseline, no fetch, no cheap)", (False, "a"*64, "a"*64, False), (False, None)),
    ]
    failures = 0
    for name, args_t, expected in cases:
        changed, conf = classify_change(*args_t)
        exp_changed, exp_sub = expected
        ok = (changed == exp_changed) and (
            exp_sub is None and conf is None or
            (exp_sub is not None and conf is not None and exp_sub in conf)
        )
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: -> ({changed}, {conf!r})")
        if not ok:
            failures += 1
            print(f"         expected changed={exp_changed}, confidence~={exp_sub!r}")

    # Ledger rendering
    empty = render_ledger([], "2026-06-03", 147, 0)
    if "No content changes" not in empty:
        print("  [FAIL] render_ledger(empty) missing 'No content changes'"); failures += 1
    else:
        print("  [PASS] render_ledger(empty)")
    one = render_ledger([{
        "source_id": "g29", "title": "幼稚園教育課程指引", "confidence": "content-hash",
        "old_hash": "a"*64, "new_hash": "b"*64,
        "last_modified": {"old": "X", "new": "Y"},
    }], "2026-06-03", 147, 0)
    if "g29" in one and "content-hash" in one and "| source_id |" in one:
        print("  [PASS] render_ledger(one)")
    else:
        print("  [FAIL] render_ledger(one) malformed"); failures += 1

    print(f"\nSelf-test: {'ALL PASS' if failures == 0 else f'{failures} FAIL'}")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="Run offline logic assertions and exit")
    parser.add_argument("--dry-run", action="store_true", help="Don't save changes back to JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show more detail")
    parser.add_argument("--limit", type=int, default=0, help="Only check the first N sources (testing)")
    parser.add_argument("--changes-out", default="freshness_changes.json",
                        help="Path to write the machine-readable change report (JSON)")
    parser.add_argument("--ledger", default=None,
                        help="Path to write the human Markdown ledger (write-sync only)")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test())

    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found at {REGISTRY_PATH}")
        sys.exit(1)

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    sources = registry.get("sources", [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changes_detected = 0
    errors = 0
    total_checked = 0
    hashed = 0
    failed_records: List[Dict[str, str]] = []
    changed_records: List[Dict] = []

    print(f"🔍 Checking freshness for {len(sources)} sources...")
    print(f"📅 Today: {today}  | mode: {'dry-run' if args.dry_run else 'write-sync'}")
    print("-" * 60)

    for src in sources:
        # Filter: verified + public + has primary URL
        if not (src.get("status") == "verified" and
                src.get("access_mode") == "public" and
                src.get("url_primary")):
            continue

        if args.limit and total_checked >= args.limit:
            break

        total_checked += 1
        url = src["url_primary"]
        sid = src["source_id"]

        if args.verbose:
            print(f"[{total_checked}] Checking {sid}...")

        headers = get_headers(url)
        if not headers:
            print(f"  ❌ Failed: {sid} ({url})")
            errors += 1
            failed_records.append({"sid": sid, "url": url})
            continue

        last_mod = headers.get("Last-Modified")
        cont_len = headers.get("Content-Length")
        etag = headers.get("ETag")

        # The key may exist with value None for sources that never recorded
        # metadata; the {} default on dict.get only triggers when the key is
        # absent, so coerce here.
        meta = src.get("freshness_metadata") or {}
        old_mod = meta.get("last_modified")
        old_len = meta.get("content_length")
        old_etag = meta.get("etag")
        old_hash = meta.get("content_hash")

        # Tier 1 — cheap HEAD signal
        cheap_changed = False
        if last_mod and old_mod and last_mod != old_mod:
            cheap_changed = True
        if cont_len and old_len and str(cont_len) != str(old_len):
            cheap_changed = True
        if etag and old_etag and etag != old_etag:
            cheap_changed = True

        # Tier 2 — content-hash confirm. Compute only when it is useful:
        #   - cheap signal tripped AND we have a baseline hash to compare against
        #     (precise confirm / false-positive suppression), regardless of mode; OR
        #   - no baseline hash yet AND we are writing (seed for future runs).
        need_hash = (cheap_changed and bool(old_hash)) or ((not old_hash) and (not args.dry_run))
        new_hash = old_hash
        hash_state = "skipped"
        if need_hash:
            computed, herr = get_content_hash(url)
            if computed:
                new_hash = computed
                hashed += 1
                hash_state = "computed"
            else:
                hash_state = f"fetch_failed ({herr})"
                if args.verbose:
                    print(f"     ⚠️ hash fetch failed for {sid}: {herr}")

        # Decide changed — content hash is authoritative when both sides exist.
        changed, confidence = classify_change(
            cheap_changed, old_hash, new_hash, hash_state == "computed"
        )

        # Update record (persisted only when not dry-run)
        src["last_checked_at"] = today
        src["freshness_metadata"] = {
            "last_modified": last_mod,
            "content_length": cont_len,
            "etag": etag,
            "content_hash": new_hash,
            "hash_checked_at": today if hash_state == "computed" else meta.get("hash_checked_at"),
        }

        if changed:
            changes_detected += 1
            changed_records.append({
                "source_id": sid,
                "title": src.get("title") or src.get("title_short") or "",
                "url": url,
                "confidence": confidence,
                "old_hash": old_hash,
                "new_hash": new_hash if hash_state == "computed" else None,
                "hash_status": hash_state,
                "last_modified": {"old": old_mod, "new": last_mod},
                "content_length": {"old": old_len, "new": cont_len},
            })
            print(f"  🔔 CHANGE: {sid}  [{confidence}]")
            print(f"     Old: Mod={old_mod}, Len={old_len}, hash={(old_hash or '—')[:12]}")
            print(f"     New: Mod={last_mod}, Len={cont_len}, hash={(new_hash or '—')[:12] if hash_state=='computed' else '(not fetched)'}")
        elif args.verbose:
            print(f"  ✅ OK: {sid}")

    # Update global metadata
    registry.setdefault("_meta", {})["updated"] = today

    if not args.dry_run:
        # Atomic write: serialize to a temp file then os-replace, so an
        # interrupted/failed write can never leave a half-written (corrupt)
        # registry that would crash every subsequent run's json.load().
        try:
            tmp = REGISTRY_PATH.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            tmp.replace(REGISTRY_PATH)  # atomic rename on the same filesystem
            print(f"\n💾 Registry updated: {REGISTRY_PATH}")
        except Exception as e:
            print(f"\n❌ Failed to write registry (left unchanged): {e}")
            sys.exit(1)
    else:
        print("\n🧪 Dry run: registry not modified.")

    # Always emit the machine-readable change report (consumed by CI).
    report = {
        "generated_at": today,
        "dry_run": args.dry_run,
        "checked": total_checked,
        "changes": changes_detected,
        "errors": errors,
        "hashed": hashed,
        "changed_sources": changed_records,
        "failed_sources": failed_records,
    }
    try:
        with open(args.changes_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📄 Change report: {args.changes_out}")
    except Exception as e:
        print(f"  ⚠️ Could not write change report to {args.changes_out}: {e}")

    # Human ledger — write-sync only (a committed snapshot at sync time).
    if args.ledger and not args.dry_run:
        try:
            with open(args.ledger, "w", encoding="utf-8") as f:
                f.write(render_ledger(changed_records, today, total_checked, errors))
            print(f"📋 Ledger: {args.ledger}")
        except Exception as e:
            print(f"  ⚠️ Could not write ledger to {args.ledger}: {e}")

    # Fail-threshold: tolerate isolated EDB intermittent timeouts / a handful of
    # stale URLs, but still surface a real outage. Trips when errors exceed the
    # greater of 5 absolute and 5% of total checked (rounded down).
    # NOTE: detected CHANGES never affect exit code — only errors do (S126
    # chronic-fail lesson: do not overload exit semantics with change signals).
    threshold = max(5, total_checked // 20)

    print(f"\nSummary:")
    print(f"  Checked:    {total_checked}")
    print(f"  Changes:    {changes_detected}")
    print(f"  Hashed:     {hashed}")
    print(f"  Errors:     {errors}")
    print(f"  Threshold:  {threshold}  (fail when errors > threshold)")

    if changed_records:
        print(f"\nChanged sources ({len(changed_records)}):")
        for rec in changed_records:
            print(f"  - {rec['source_id']}: {rec['confidence']}")

    if failed_records:
        print(f"\nFailed sources ({len(failed_records)}):")
        for rec in failed_records:
            print(f"  - {rec['sid']}: {rec['url']}")

    if errors > threshold:
        print(f"\n🚨 errors {errors} > threshold {threshold} — exiting 1")
        sys.exit(1)

    if errors > 0:
        print(f"\n⚠️  errors {errors} within threshold {threshold} — exit 0 (workflow remains green)")


if __name__ == "__main__":
    main()
