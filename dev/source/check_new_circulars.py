#!/usr/bin/env python3
"""
check_new_circulars.py
======================
The 4th source monitor (S185). Watches Leonard's own EDB circular dashboard
feed — https://circular.wongfu.net/circulars.json — and surfaces brand-new EDB
circulars (EDBC / EDBCM) that are NOT yet in our source_registry.json, so the
weekly/daily triage can decide which to ingest.

Why this feed and not the EDB site directly:
  - discover_sources.py only crawls .html landing pages already in the registry;
    NONE of them is the EDB circulars master index, and the index itself is
    JS/AJAX-rendered (would return 0 links). So a brand-new circular like
    EDBC 8/2026 「學校效率津貼」 was structurally invisible to discover (verified
    S185 — debp.html, the only plausible watched page, does not link it).
  - circulars.json is a clean STATIC JSON: number / date / title / full text /
    topics / urgency / pdf_urls, plus K1-aligned fields (k1_topics,
    channel_b_facts, role_facts). It regenerates daily.

Detection only — re-ingestion stays a manual gate (same discipline as the other
three monitors). This script never writes the registry; it only surfaces
candidates for human triage. Verbatim ingest from pdf_urls (PyMuPDF) still
applies — do NOT trust the feed's pre-extracted `official` text as the SSOT.

Candidate signal (low-noise, self-clearing):
  A dashboard circular is a candidate when its PDF is NOT already in the registry
  AND it is either flagged `isNew` by the dashboard OR dated within --since-days.
  Match key = PDF basename (e.g. EDBC26008C.pdf), which both sides carry; the
  human "number" string (EDBC008/2026) and the registry id (edbc008_2026) do not
  share a stable normalization, so basename is authoritative.
  Once a candidate is ingested it enters the registry and drops off automatically,
  so the single living triage Issue is self-clearing.

Outputs:
  --changes-out PATH  Machine-readable JSON report for CI to open/update a GitHub
                      Issue. Default: new_circulars.json
  --since-days N      Safety-net lookback window in days (default 30). Catches
                      recent circulars even after the dashboard drops `isNew`.
  --dashboard-url URL Override the feed URL (default the wongfu.net dashboard).

Exit code: 0 on a successful run (detections never fail the run). Non-zero only
when the feed cannot be fetched/parsed at all (a real outage worth an email).

Usage: python3 dev/source/check_new_circulars.py [--since-days N]
                 [--changes-out PATH] [--dashboard-url URL] [--verbose]
"""

import json
import sys
import argparse
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Set

REGISTRY_PATH = Path("dev/source/source_registry.json")
DASHBOARD_URL = "https://circular.wongfu.net/circulars.json"
FETCH_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
# A single triage Issue should not be flooded; cap the listed candidates and note
# the overflow. The registry backlog (we ingest selectively) means a wide window
# can legitimately list many un-ingested circulars.
DISPLAY_CAP = 50


def basename(url: str) -> str:
    """Lowercased final path segment — the stable cross-feed match key."""
    return (url or "").split("?", 1)[0].rsplit("/", 1)[-1].strip().lower()


def load_registry_pdf_basenames() -> Set[str]:
    """Every PDF basename already known to the registry (url_primary/url_landing)."""
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) and "sources" in reg else reg
    known: Set[str] = set()
    for s in sources:
        for key in ("url_primary", "url_landing"):
            b = basename(s.get(key, ""))
            if b.endswith(".pdf"):
                known.add(b)
    return known


def fetch_circulars(url: str) -> Dict:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def in_registry(circular: Dict, known_pdfs: Set[str]) -> bool:
    return any(basename(u) in known_pdfs for u in (circular.get("pdf_urls") or []))


def main() -> int:
    ap = argparse.ArgumentParser(description="Surface brand-new EDB circulars from the dashboard feed.")
    ap.add_argument("--since-days", type=int, default=30, help="Safety-net lookback window (default 30).")
    ap.add_argument("--changes-out", default="new_circulars.json", help="JSON report path for CI.")
    ap.add_argument("--dashboard-url", default=DASHBOARD_URL, help="Feed URL override.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    # --- Fetch feed (a hard failure here is a real outage → non-zero exit) ---
    try:
        feed = fetch_circulars(args.dashboard_url)
    except Exception as e:
        print(f"ERROR: could not fetch/parse dashboard feed {args.dashboard_url}: {e}", file=sys.stderr)
        return 2

    circulars = feed.get("circulars") or []
    if not isinstance(circulars, list) or not circulars:
        print(f"ERROR: feed has no 'circulars' list (got {type(circulars).__name__}, len={len(circulars) if isinstance(circulars, list) else 'n/a'})", file=sys.stderr)
        return 2

    known_pdfs = load_registry_pdf_basenames()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.since_days)).strftime("%Y-%m-%d")

    candidates: List[Dict] = []
    for c in circulars:
        if in_registry(c, known_pdfs):
            continue
        is_new = bool(c.get("isNew"))
        recent = (c.get("date") or "") >= cutoff
        if not (is_new or recent):
            continue
        candidates.append({
            "number": c.get("number"),
            "type": c.get("type"),
            "date": c.get("date"),
            "title": c.get("title"),
            "isNew": is_new,
            "urgency": c.get("urgency"),
            "impact": c.get("impact"),
            "k1_topics": c.get("k1_topics") or [],
            "pdf_urls": c.get("pdf_urls") or [],
            "summary": (c.get("summary") or "")[:300],
        })

    # Newest first; dashboard-flagged isNew rises within the same date.
    candidates.sort(key=lambda c: (c.get("date") or "", c.get("isNew")), reverse=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dashboard_url": args.dashboard_url,
        "feed_generated_at": feed.get("generated_at"),
        "since_days": args.since_days,
        "cutoff_date": cutoff,
        "feed_count": len(circulars),
        "registry_known_pdfs": len(known_pdfs),
        "candidates": len(candidates),
        "new_circulars": candidates,
    }
    Path(args.changes_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Feed generated_at : {feed.get('generated_at')}")
    print(f"Feed circulars    : {len(circulars)} | registry known PDFs: {len(known_pdfs)}")
    print(f"Lookback cutoff    : {cutoff} (--since-days {args.since_days})")
    print(f"NEW candidates     : {len(candidates)}")
    if args.verbose or candidates:
        for c in candidates[:DISPLAY_CAP]:
            flag = "🆕" if c["isNew"] else "  "
            print(f"  {flag} {c['number']:<16} {c['date']}  {c['title']}  [{','.join(c['k1_topics'])}]")
        if len(candidates) > DISPLAY_CAP:
            print(f"  … +{len(candidates) - DISPLAY_CAP} more (see {args.changes_out})")
    print(f"Report written     : {args.changes_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
