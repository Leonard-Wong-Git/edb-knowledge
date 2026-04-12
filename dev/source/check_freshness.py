#!/usr/bin/env python3
"""
check_freshness.py
==================
Reads source_registry.json and performs HEAD requests to verify public source freshness.
Updates last_checked_at and records metadata (Last-Modified, Content-Length) if changed.

Usage: python3 check_freshness.py [--dry-run] [--verbose]
"""

import json
import requests
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Constants
REGISTRY_PATH = Path("dev/source/source_registry.json")
TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def get_headers(url: str) -> Optional[Dict[str, str]]:
    """Fetch HEAD headers for a URL."""
    try:
        resp = requests.head(
            url, 
            headers={"User-Agent": USER_AGENT}, 
            allow_redirects=True, 
            timeout=TIMEOUT
        )
        if resp.status_code == 200:
            return resp.headers
        # Fallback to GET if HEAD is blocked but limit bytes
        resp = requests.get(
            url, 
            headers={"User-Agent": USER_AGENT}, 
            allow_redirects=True, 
            timeout=TIMEOUT,
            stream=True
        )
        if resp.status_code == 200:
            h = dict(resp.headers)
            resp.close()
            return h
        return None
    except Exception as e:
        print(f"  ⚠️ Request failed for {url}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't save changes back to JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show more detail")
    args = parser.parse_args()

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

    print(f"🔍 Checking freshness for {len(sources)} sources...")
    print(f"📅 Today: {today}")
    print("-" * 60)

    for src in sources:
        # Filter: verified + public + has primary URL
        if (src.get("status") == "verified" and 
            src.get("access_mode") == "public" and 
            src.get("url_primary")):
            
            total_checked += 1
            url = src["url_primary"]
            sid = src["source_id"]
            
            if args.verbose:
                print(f"[{total_checked}] Checking {sid}...")
            
            headers = get_headers(url)
            if not headers:
                print(f"  ❌ Failed: {sid} ({url})")
                errors += 1
                continue

            # Extract metadata
            last_mod = headers.get("Last-Modified")
            cont_len = headers.get("Content-Length")
            etag = headers.get("ETag")

            # Compare with existing (if present in new metadata field)
            meta = src.get("freshness_metadata", {})
            old_mod = meta.get("last_modified")
            old_len = meta.get("content_length")

            changed = False
            if last_mod and old_mod and last_mod != old_mod:
                changed = True
            if cont_len and old_len and str(cont_len) != str(old_len):
                changed = True

            # Update record
            src["last_checked_at"] = today
            src["freshness_metadata"] = {
                "last_modified": last_mod,
                "content_length": cont_len,
                "etag": etag
            }

            if changed:
                changes_detected += 1
                print(f"  🔔 CHANGE: {sid}")
                print(f"     Old: Mod={old_mod}, Len={old_len}")
                print(f"     New: Mod={last_mod}, Len={cont_len}")
            elif args.verbose:
                print(f"  ✅ OK: {sid}")

    # Update global metadata
    registry["_meta"]["updated"] = today

    if not args.dry_run:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Registry updated: {REGISTRY_PATH}")
    else:
        print("\n🧪 Dry run: no changes saved.")

    print(f"\nSummary:")
    print(f"  Checked: {total_checked}")
    print(f"  Changes: {changes_detected}")
    print(f"  Errors:  {errors}")

if __name__ == "__main__":
    main()
