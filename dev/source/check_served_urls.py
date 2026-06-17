#!/usr/bin/env python3
"""
check_served_urls.py
====================
Served-URL health check — Method B (the delivery-integrity monitor).

`check_freshness.py` tests the REGISTRY (`source_registry.json` → `url_primary`):
it answers "did the upstream EDB source change?". It cannot see drift in the
DERIVED store. Channel-B chunks in Supabase carry their OWN copy of the source
URL (`wiki_chunks.url`) — the link a user actually clicks. When the registry is
corrected but the store is not re-synced (or an old malformed URL was ingested),
the registry monitor stays green (200, errors=0) while users hit a 404.

That is exactly what happened S170: registry had the right SAG URL, but 383
`sag_2025_11` chunks served `/sch-admin-guide/index.html` (404). The
registry-only monitor could never catch it. This script closes that blind spot.

What it does:
  1. Pull every DISTINCT served URL from `wiki_chunks.url` (paginated REST scan).
  2. HTTP-test each (HEAD, GET-fallback) — the URL the user is actually handed.
  3. Classify: ok (2xx) / broken (4xx — a dead link served to users) / error
     (network / 5xx — transient, does not prove the link is dead).

Signal routing (mirrors check_freshness.py — S126 lesson: do NOT overload exit
semantics with content signals):
  - BROKEN served URLs are the SIGNAL → surfaced in the JSON report + ledger so
    CI opens/updates a GitHub Issue (weekly e-mail via Watch). They do NOT fail
    the build (a single dead upstream link should not red-flag the whole run).
  - ERRORS (could-not-test: network / 5xx) drive the exit-code threshold — only
    a real outage (errors > max(5, checked//20)) exits non-zero.

Read-only: SELECTs `wiki_chunks` and issues HTTP HEAD/GET. Never writes the
store, the registry, or any source. Pairs with check_freshness.py — A tests
upstream change, B tests delivery integrity (see FRESHNESS_GUIDE.md).

Usage (from repo root):
  python3 dev/source/check_served_urls.py --self-test            # offline logic, no network
  python3 dev/source/check_served_urls.py --check                # full live scan
  python3 dev/source/check_served_urls.py --check --limit 20     # only first 20 distinct URLs
  python3 dev/source/check_served_urls.py --check \
      --changes-out served_url_changes.json --ledger served_url_changes.md

Env: SUPABASE_ANON_KEY (preferred, read-only) or SUPABASE_SERVICE_KEY; falls
back to backend/.env (SUPABASE_SERVICE_KEY). SUPABASE_URL optional (defaults to
the project URL).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

import requests

# ── Constants ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent      # …/Draft
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"
TABLE = "wiki_chunks"
PAGE_SIZE = 1000                 # PostgREST Range page size
HEAD_TIMEOUT = 15
GET_TIMEOUT = 30
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


# ── Pure helpers (offline self-testable) ─────────────────────────────────────
def normalize_url(u: Optional[str]) -> Optional[str]:
    """Return the base URL a server would actually receive: trimmed, with the
    client-side `#fragment` (e.g. `#page=12`) stripped. Falsy / non-http → None.

    Two stored URLs that differ only by page fragment are the SAME served
    resource for health-check purposes — testing one covers both.
    """
    if not u or not isinstance(u, str):
        return None
    u = u.strip()
    if not u:
        return None
    parts = urlsplit(u)
    if parts.scheme not in ("http", "https"):
        return None
    # drop fragment, keep scheme/host/path/query
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def aggregate_urls(rows: List[Dict]) -> Dict[str, List[str]]:
    """Group raw [{'url','source_id'}, …] rows by normalized base URL.

    Returns {base_url: [source_id, …]} with source_ids sorted+deduped. Rows with
    a falsy / non-http URL are skipped (they cannot be served as a link). Pure.
    """
    agg: Dict[str, set] = {}
    for row in rows:
        base = normalize_url(row.get("url"))
        if not base:
            continue
        sid = row.get("source_id") or "?"
        agg.setdefault(base, set()).add(sid)
    return {u: sorted(sids) for u, sids in sorted(agg.items())}


def classify_status(status_code: Optional[int], error: Optional[str]) -> Tuple[str, str]:
    """Map a probe outcome to (verdict, label). Pure.

    verdict ∈ {ok, broken, error}:
      - error present                  → ('error', reason)        # could not test
      - 408 / 429                      → ('error', …)             # transient: timeout / rate-limit, NOT a dead link
      - 200 ≤ code < 400               → ('ok', 'HTTP <code>')    # served fine (redirects followed)
      - 400 ≤ code < 500               → ('broken', 'HTTP <code>')# dead link served to users
      - everything else (≥500, None)   → ('error', …)             # transient / server-side

    408 (Request Timeout) and 429 (Too Many Requests) are 4xx but transient — a
    rate-limited LIVE url must not be reported as a broken link (false alarm /
    crying-wolf). They go in the error bucket (could-not-test), same as 5xx.
    """
    if error:
        return "error", error
    if status_code is None:
        return "error", "no response"
    if status_code in (408, 429):
        return "error", f"HTTP {status_code} (transient)"
    if 200 <= status_code < 400:
        return "ok", f"HTTP {status_code}"
    if 400 <= status_code < 500:
        return "broken", f"HTTP {status_code}"
    return "error", f"HTTP {status_code}"


def render_ledger(broken: List[Dict], errors: List[Dict], today: str,
                  checked: int) -> str:
    """Render the human-facing broken-served-URL ledger (Markdown)."""
    lines = [
        "# Served-URL Health — Broken Links Pending Review",
        "",
        "<!-- AUTO-GENERATED by dev/source/check_served_urls.py --ledger. Do not "
        "hand-edit; it is overwritten on each run. -->",
        "",
        f"- Last check: **{today}** (UTC)",
        f"- Distinct served URLs checked: {checked} · Broken: **{len(broken)}** · "
        f"Errors (could-not-test): {len(errors)}",
        "",
        "> ⚠️ These are URLs the VECTOR STORE serves to users (`wiki_chunks.url`), "
        "not registry URLs. A broken one means the store drifted from the registry "
        "(re-ingest / Supabase UPDATE the affected source — see FRESHNESS_GUIDE.md). "
        "Detection only; the fix stays a manual gate.",
        "",
    ]
    if not broken:
        lines.append("_No broken served URLs detected._")
    else:
        lines.append("| served URL | status | source_id(s) |")
        lines.append("|---|---|---|")
        for b in broken:
            sids = ", ".join(f"`{s}`" for s in b.get("source_ids", []))
            url = (b.get("url") or "").replace("|", "%7C")
            lines.append(f"| {url} | {b.get('status', '')} | {sids} |")
    if errors:
        lines.append("")
        lines.append(f"### Could-not-test ({len(errors)}) — transient / server-side")
        lines.append("| served URL | reason | source_id(s) |")
        lines.append("|---|---|---|")
        for e in errors:
            sids = ", ".join(f"`{s}`" for s in e.get("source_ids", []))
            url = (e.get("url") or "").replace("|", "%7C")
            lines.append(f"| {url} | {e.get('reason', '')} | {sids} |")
    return "\n".join(lines) + "\n"


# ── Network ──────────────────────────────────────────────────────────────────
def load_key() -> str:
    """Read a Supabase key. Prefer the read-only anon key; accept the service
    key. Env first, then backend/.env (which holds SUPABASE_SERVICE_KEY)."""
    for var in ("SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"):
        v = (__import__("os").environ.get(var) or "").strip()
        if v:
            return v
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            for var in ("SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"):
                if line.startswith(var + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def fetch_served_urls(base_url: str, key: str, limit_rows: int = 0,
                      verbose: bool = False) -> List[Dict]:
    """Paginate `SELECT url, source_id FROM wiki_chunks` via PostgREST Range.

    Returns a flat list of {'url','source_id'} dicts (one per chunk row). Raises
    on a hard HTTP/connection failure so the caller can report a fetch outage
    rather than silently checking an empty set (prod-fail-visible)."""
    endpoint = f"{base_url}/rest/v1/{TABLE}?select=url,source_id"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }
    out: List[Dict] = []
    start = 0
    while True:
        end = start + PAGE_SIZE - 1
        h = dict(headers)
        h["Range-Unit"] = "items"
        h["Range"] = f"{start}-{end}"
        resp = requests.get(endpoint, headers=h, timeout=GET_TIMEOUT)
        if resp.status_code not in (200, 206):
            raise RuntimeError(
                f"Supabase fetch failed: HTTP {resp.status_code} {resp.text[:200]}")
        page = resp.json()
        out.extend(page)
        if verbose:
            print(f"  …fetched {len(out)} rows")
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
        if limit_rows and len(out) >= limit_rows:
            break
    return out


def probe_url(url: str) -> Tuple[Optional[int], Optional[str]]:
    """HEAD the URL (GET-fallback when HEAD is blocked). Returns
    (status_code, error). Mirrors check_freshness.get_headers semantics."""
    try:
        resp = requests.head(url, headers={"User-Agent": USER_AGENT},
                             allow_redirects=True, timeout=HEAD_TIMEOUT)
        # Many servers reject/!=200 on HEAD but serve GET — confirm with a GET.
        if resp.status_code != 200:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT},
                                allow_redirects=True, timeout=GET_TIMEOUT,
                                stream=True)
            code = resp.status_code
            resp.close()
            return code, None
        return resp.status_code, None
    except Exception as e:                                   # noqa: BLE001
        return None, str(e)


# ── Self-test ────────────────────────────────────────────────────────────────
def run_self_test() -> int:
    """Offline deterministic assertions. No network. Returns process exit code."""
    failures = 0

    def check(name: str, got, exp):
        nonlocal failures
        ok = got == exp
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            failures += 1
            print(f"         got={got!r}  expected={exp!r}")

    # normalize_url
    check("normalize strips #page fragment",
          normalize_url("https://e.gov.hk/a.pdf#page=12"), "https://e.gov.hk/a.pdf")
    check("normalize keeps query",
          normalize_url("https://e.gov.hk/a?b=1"), "https://e.gov.hk/a?b=1")
    check("normalize trims whitespace",
          normalize_url("  https://e.gov.hk/a.pdf  "), "https://e.gov.hk/a.pdf")
    check("normalize rejects empty", normalize_url(""), None)
    check("normalize rejects None", normalize_url(None), None)
    check("normalize rejects non-http (mailto)",
          normalize_url("mailto:x@y.com"), None)

    # aggregate_urls — same base via different fragments collapses; sids dedup+sort
    agg = aggregate_urls([
        {"url": "https://e.gov.hk/a.pdf#page=1", "source_id": "g02"},
        {"url": "https://e.gov.hk/a.pdf#page=9", "source_id": "g01"},
        {"url": "https://e.gov.hk/a.pdf#page=9", "source_id": "g01"},
        {"url": "", "source_id": "skip"},
        {"url": None, "source_id": "skip2"},
        {"url": "https://e.gov.hk/b.pdf", "source_id": "g03"},
    ])
    check("aggregate collapses fragments to 2 distinct URLs", len(agg), 2)
    check("aggregate dedups+sorts source_ids",
          agg.get("https://e.gov.hk/a.pdf"), ["g01", "g02"])
    check("aggregate skips falsy URLs (no empty/None keys)",
          all(k for k in agg), True)

    # classify_status
    check("classify 200 → ok", classify_status(200, None), ("ok", "HTTP 200"))
    check("classify 301 (followed) → ok", classify_status(301, None), ("ok", "HTTP 301"))
    check("classify 404 → broken", classify_status(404, None), ("broken", "HTTP 404"))
    check("classify 403 → broken", classify_status(403, None), ("broken", "HTTP 403"))
    check("classify 429 (rate-limit) → error not broken",
          classify_status(429, None), ("error", "HTTP 429 (transient)"))
    check("classify 408 (timeout) → error not broken",
          classify_status(408, None), ("error", "HTTP 408 (transient)"))
    check("classify 500 → error", classify_status(500, None), ("error", "HTTP 500"))
    check("classify network exc → error",
          classify_status(None, "timeout")[0], "error")
    check("classify no response → error",
          classify_status(None, None), ("error", "no response"))

    # render_ledger
    empty = render_ledger([], [], "2026-06-17", 224)
    check("ledger(empty) says no broken", "No broken served URLs" in empty, True)
    one = render_ledger(
        [{"url": "https://e.gov.hk/dead.html", "status": "HTTP 404",
          "source_ids": ["sag_2025_11"]}],
        [{"url": "https://e.gov.hk/slow.pdf", "reason": "timeout",
          "source_ids": ["g10"]}],
        "2026-06-17", 224)
    check("ledger(one) lists broken url + sid",
          "dead.html" in one and "sag_2025_11" in one, True)
    check("ledger(one) lists could-not-test section",
          "Could-not-test" in one and "slow.pdf" in one, True)

    print(f"\nSelf-test: {'ALL PASS' if failures == 0 else f'{failures} FAIL'}")
    return 1 if failures else 0


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--self-test", action="store_true",
                        help="Run offline logic assertions and exit (no network)")
    parser.add_argument("--check", action="store_true",
                        help="Run the live served-URL scan")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only test the first N distinct URLs (testing)")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--changes-out", default="served_url_changes.json",
                        help="Path to write the machine-readable report (JSON)")
    parser.add_argument("--ledger", default=None,
                        help="Path to write the human Markdown ledger")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test())

    if not args.check:
        parser.error("nothing to do: pass --self-test or --check")

    key = load_key()
    if not key:
        print("❌ Supabase key not configured. Set SUPABASE_ANON_KEY (read-only, "
              "preferred) or SUPABASE_SERVICE_KEY in the environment, or put "
              "SUPABASE_SERVICE_KEY in backend/.env.")
        sys.exit(2)

    base_url = (__import__("os").environ.get("SUPABASE_URL") or SUPABASE_URL).rstrip("/")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"🔗 Served-URL health check  | mode: live  | {today} (UTC)")
    print(f"   store: {base_url}/rest/v1/{TABLE}")
    print("-" * 60)

    # 1. Pull served URLs from the store.
    try:
        rows = fetch_served_urls(base_url, key, limit_rows=0, verbose=args.verbose)
    except Exception as e:                                   # noqa: BLE001
        # A store-read failure is an outage, not a clean "no broken links".
        print(f"❌ Could not read served URLs from store: {e}")
        sys.exit(1)

    distinct = aggregate_urls(rows)
    all_urls = list(distinct.keys())
    if args.limit:
        all_urls = all_urls[:args.limit]
    print(f"📦 {len(rows)} chunk rows → {len(distinct)} distinct served URLs"
          f"{f' (testing first {len(all_urls)})' if args.limit else ''}")
    print("-" * 60)

    broken: List[Dict] = []
    errors: List[Dict] = []
    ok_count = 0
    for i, url in enumerate(all_urls, 1):
        sids = distinct[url]
        code, err = probe_url(url)
        verdict, label = classify_status(code, err)
        if verdict == "ok":
            ok_count += 1
            if args.verbose:
                print(f"  ✅ [{i}/{len(all_urls)}] {label}  {url}")
        elif verdict == "broken":
            broken.append({"url": url, "status": label, "source_ids": sids})
            print(f"  🔴 [{i}/{len(all_urls)}] {label}  {url}")
            print(f"       source_id(s): {', '.join(sids)}")
        else:
            errors.append({"url": url, "reason": label, "source_ids": sids})
            print(f"  ⚠️  [{i}/{len(all_urls)}] {label}  {url}")

    checked = len(all_urls)
    # Exit-code threshold: tolerate isolated EDB intermittent timeouts, surface a
    # real outage. BROKEN links never affect exit code (S126 lesson) — they are
    # the content signal, routed to the Issue, not the build status.
    threshold = max(5, checked // 20)

    print("\nSummary:")
    print(f"  Distinct URLs: {len(distinct)}")
    print(f"  Checked:       {checked}")
    print(f"  OK:            {ok_count}")
    print(f"  Broken (4xx):  {len(broken)}")
    print(f"  Errors:        {len(errors)}")
    print(f"  Threshold:     {threshold}  (fail when errors > threshold)")

    if broken:
        print(f"\nBroken served URLs ({len(broken)}):")
        for b in broken:
            print(f"  - {b['status']}  {b['url']}  [{', '.join(b['source_ids'])}]")

    # Machine-readable report (consumed by CI to open/update an Issue).
    report = {
        "generated_at": today,
        "store": f"{base_url}/rest/v1/{TABLE}",
        "chunk_rows": len(rows),
        "distinct_urls": len(distinct),
        "checked": checked,
        "ok": ok_count,
        "broken": len(broken),
        "errors": len(errors),
        "broken_urls": broken,
        "error_urls": errors,
    }
    try:
        with open(args.changes_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Report: {args.changes_out}")
    except Exception as e:                                   # noqa: BLE001
        print(f"  ⚠️ Could not write report to {args.changes_out}: {e}")

    if args.ledger:
        try:
            with open(args.ledger, "w", encoding="utf-8") as f:
                f.write(render_ledger(broken, errors, today, checked))
            print(f"📋 Ledger: {args.ledger}")
        except Exception as e:                               # noqa: BLE001
            print(f"  ⚠️ Could not write ledger to {args.ledger}: {e}")

    if len(errors) > threshold:
        print(f"\n🚨 errors {len(errors)} > threshold {threshold} — exiting 1")
        sys.exit(1)
    if errors:
        print(f"\n⚠️  errors {len(errors)} within threshold {threshold} — exit 0")


if __name__ == "__main__":
    main()
