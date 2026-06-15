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

### Stub-baseline artifact (S170 lesson)
A flagged "change" where the **old** baseline is tiny (1–3 KB) but the **new**
fetch is multi-MB — often with the new `Last-Modified` *older* than the recorded
one — is **not** a content change. It means the baseline was once seeded from a
redirect/landing **stub** and the crawl now resolves through to the real file
(KB→MB + time-going-backwards = the file's own header). **Fix: re-seed via a
write-sync** (`check_freshness.py --ledger …`) so the baseline becomes the real
file's hash; do **not** re-ingest. After re-seed, a second `--dry-run` should
report `Changes: 0`. (S170: 9 such artifacts → 0; all 215 baselines re-seeded.)

## 4. Source Admission Policy (轻量级)
- Only `status: verified` public sources are checked.
- `manual_only` or `login_required` sources are currently excluded from automated monitoring; these MUST be manually re-verified by the operator once per school term.

## 5. Sibling: New-Source Discovery (`discover_sources.py`)
Detection-only crawler that finds EDB documents **not yet in the registry**. It
derives its watch pages from every registered source's `url_landing` (no manual
flag), subtracts all known URLs, and reports the rest.
```bash
python3 dev/source/discover_sources.py --self-test          # offline logic
python3 dev/source/discover_sources.py --check              # read-only crawl
```
- Weekly GitHub Action `discover_check.yml` (Mon 10:00 UTC, read-only) opens/updates
  GitHub Issue **#2** with the candidates. Same manual gate: never ingests.
- **Enumeration-page cap (S170):** a watch page yielding more than
  `ENUMERATION_PAGE_CAP` (=25) new links is an archive/listing index (e.g. the
  free-quality-KG per-school dump = 316 links); its records are flagged
  `enumeration-page` — kept in the report but dropped from the `likely-real`
  signal (no-loss) so one index can't flood triage. Tunable constant at the top
  of the script.
- **Triage before ingest:** most candidates are chapter-fragments of in-corpus
  docs / superseded old circulars / forms / English dups — "全入庫" must be
  triaged per-source, not batch-ingested. Most weeks there is nothing worth
  ingesting; that is normal.

## 6. Known blind-spot (follow-up)
Both monitors test the **registry** URLs (`url_primary` / `url_landing`). The
user-facing 「開啟」 link, however, uses the URL stored **per-chunk in Supabase**,
which can drift independently (S170: a `sag_2025_11` chunk served a stale
`/attachment/…/index.html` → 404 while the registry URL was a healthy PDF). A
registry check is **not** a guarantee the served link works. Planned: a
served-URL health check that pulls distinct URLs from the vector store / API and
HTTP-tests them.
