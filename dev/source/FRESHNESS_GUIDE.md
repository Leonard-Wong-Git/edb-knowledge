# Phase 2: Freshness Monitoring Operating Rhythm

This document establishes the official rhythm for maintaining the source registry freshness metadata and handling broken links or upstream content changes.

## 1. Monitoring Rhythm
- **Weekly (Recommended)**: Run the freshness checker to detect broken links and record meta changes.
- **Before Releases**: Must run and verify all sources in the registry.
- **On Error**: Any error in the checker's log must be investigated and repaired immediately (re-verify URL or search for archive).

## 2. Command Reference
```bash
# Offline logic self-test (no network) — run after editing the checker
python3 dev/source/check_freshness.py --self-test

# Dry-run detection: report changes without writing the registry
python3 dev/source/check_freshness.py --dry-run

# Official write-sync: verify sources, write back metadata + content hashes,
# and render the human ledger of pending re-ingest work
python3 dev/source/check_freshness.py --ledger dev/source/freshness_changes.md

# Scope to first N sources (testing); JSON change report goes to --changes-out
python3 dev/source/check_freshness.py --dry-run --limit 5 --changes-out /tmp/fc.json
```

### Two-tier change detection (S139 hybrid)
1. **Cheap tier** — HEAD compares `Last-Modified` / `Content-Length` / `ETag`.
2. **Confirm tier** — when the cheap signal trips (or a hash needs seeding), the
   checker GETs the file and compares a raw-byte **SHA-256** against the stored
   `content_hash`. The hash is **authoritative**: it suppresses HEAD
   false-positives (EDB redirect / re-export churn) and confirms true changes.

`content_hash` shares the lifecycle of the other metadata fields — it is seeded /
refreshed only on a write-sync. Scheduled runs are dry-run and detect drift
against the last synced baseline without persisting, so they stay cheap (only a
tripped, already-seeded source gets downloaded). The **first** write-sync seeds
hashes for all 147 sources (one-time heavier run; CI timeout is 30 min).

## 3. Handling Results
### `last_checked_at`
Automatically updated to the current date on every successful check. This serves as the primary "Freshness TTL" for the trust gate.

### `freshness_metadata`
Stores HTTP headers (`ETag`, `Content-Length`, `Last-Modified`) plus the
content `content_hash` (raw-byte SHA-256) and `hash_checked_at`.
- A `content_hash` mismatch is a high-confidence signal the upstream document
  actually changed; HEAD-only differences without a hash change are suppressed.
- **Manual Gate Rule (unchanged)**: Detection is automated and notifies; the
  **re-ingestion stays a human gate**. A flagged change requires the operator to
  decide and then run the manual page-carry pipeline — URL re-discovery (§E.12)
  → mojibake pre-flight → `repage_pdfs.py` → `cb3_b2_pagecarry_migrate.py` →
  backend `SOURCE_SETS` parity (S135 backfill-allowlist coupling) → deploy →
  live smoke. The detector never fetches into the vault, mutates Supabase, or
  deploys.

### Notification & ledger (auto)
- The weekly GitHub Action writes a machine report (`freshness_changes.json`,
  uploaded as a run artifact) and, when ≥1 content change is detected,
  **opens / updates a GitHub Issue** labelled `freshness-change` (GitHub emails
  the operator). The same open issue is reused, not duplicated, until acted on.
- A manual write-sync also commits `dev/source/freshness_changes.md` — a
  human-readable snapshot of pending re-ingest work that the next AI session
  sees at startup. Detected changes **never** fail the workflow; only errors
  above threshold do (exit-code semantics kept clean per the S126 lesson).

### Broken Links (Errors)
- If a URL returns 404/500/Timeout:
  1. Check if the URL has moved to an "Archive" section.
  2. Search for the document code (e.g., `EDBC 18/2023`) on the EDB site.
  3. Update `url_primary` or `url_landing` and mark as `verified`.
  4. If the document is officially withdrawn, change `status` to `superseded` or `blocked`.

## 4. Source Admission Policy (轻量级)
- Only `status: verified` public sources are checked.
- `manual_only` or `login_required` sources are currently excluded from automated monitoring; these MUST be manually re-verified by the operator once per school term.
