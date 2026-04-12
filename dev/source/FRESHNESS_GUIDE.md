# Phase 2: Freshness Monitoring Operating Rhythm

This document establishes the official rhythm for maintaining the source registry freshness metadata and handling broken links or upstream content changes.

## 1. Monitoring Rhythm
- **Weekly (Recommended)**: Run the freshness checker to detect broken links and record meta changes.
- **Before Releases**: Must run and verify all sources in the registry.
- **On Error**: Any error in the checker's log must be investigated and repaired immediately (re-verify URL or search for archive).

## 2. Command Reference
```bash
# Dry-run mode: check for errors without updating the registry
python3 dev/source/check_freshness.py --dry-run

# Official sync: verify sources and writeback metadata to source_registry.json
python3 dev/source/check_freshness.py
```

## 3. Handling Results
### `last_checked_at`
Automatically updated to the current date on every successful check. This serves as the primary "Freshness TTL" for the trust gate.

### `freshness_metadata`
Stores HTTP headers (`ETag`, `Content-Length`, `Last-Modified`).
- If these change, it indicates the upstream document has likely been updated.
- **Manual Gate Rule**: Any modified date or content length change requires a human operator to review the document and decide if `role_facts.json` or `guidelines.json` needs adjustment.

### Broken Links (Errors)
- If a URL returns 404/500/Timeout:
  1. Check if the URL has moved to an "Archive" section.
  2. Search for the document code (e.g., `EDBC 18/2023`) on the EDB site.
  3. Update `url_primary` or `url_landing` and mark as `verified`.
  4. If the document is officially withdrawn, change `status` to `superseded` or `blocked`.

## 4. Source Admission Policy (轻量级)
- Only `status: verified` public sources are checked.
- `manual_only` or `login_required` sources are currently excluded from automated monitoring; these MUST be manually re-verified by the operator once per school term.
