#!/usr/bin/env python3
"""
discover_sources.py
===================
Auto-discover NEW EDB documents that are not yet in source_registry.json (S150).

Companion to check_freshness.py:
  - check_freshness.py monitors *already-registered* sources for content CHANGES
    or dead URLs.
  - discover_sources.py crawls the EDB *landing/index pages* we already know
    (the registry's url_landing values) and DIFFS the document links found there
    against the registry's known URLs → surfaces brand-new documents that have
    appeared but were never registered.

It is detection-only. It never writes the registry and never ingests anything —
it emits a candidate list for human/agent review (same manual-gate discipline as
freshness). The output feeds a weekly GitHub Issue ("🆕 New EDB documents").

Honest limitations (documented so the operator does not over-trust it):
  1. Only finds docs linked from a *watched landing page*. A brand-new EDB section
     whose index page is not in any registry url_landing is still missed.
  2. Static fetch only — JS/AJAX-rendered link lists (e.g. the gifted policy
     landing) return nothing; such pages are flagged `js_suspect` (0 links on a
     large page) rather than silently treated as "no new docs".
  3. Landing pages list dups / old versions / posters / language variants, so the
     candidate list is NOISY by nature. Each row carries a `likely_noise` hint but
     nothing is dropped — over-listing is safer than silently hiding a real doc
     (heuristic-failure-direction: err toward retention).

Outputs:
  --changes-out PATH  machine-readable JSON for CI (default: discovered_sources.json)
  --ledger PATH       human Markdown ledger of new candidates grouped by landing page

Usage: python3 dev/source/discover_sources.py [--check] [--limit N] [--verbose]
                                               [--changes-out PATH] [--ledger PATH]
                                               [--self-test]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote

import requests

REGISTRY_PATH = Path("dev/source/source_registry.json")
FETCH_TIMEOUT = 30
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

DOC_EXT_RE = re.compile(r"\.(pdf|docx?|xlsx?)(?:$|[?#])", re.I)
HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)

# Filenames that are boilerplate / not policy content — suppressed entirely.
HARD_NOISE_RE = re.compile(r"(EDB_PDPO|privacy[-_]statement|/common/[^/]*\.pdf$)", re.I)
# Filenames that are usually low-value — flagged (not dropped) as likely_noise.
SOFT_NOISE_RE = re.compile(r"(poster|leaflet|pamphlet|comics?|survival|_eng?\.|_en\.|"
                          r"questionnaire|consultation|brief|membership|bibliography|preamble)", re.I)


# ---------------------------------------------------------------------------
# Pure helpers (offline-testable)
# ---------------------------------------------------------------------------
def normalize_url(url: str) -> str:
    """Canonicalize a URL for set membership: lowercase scheme+host, force https,
    decode %xx, drop fragment + trailing slash, collapse '//' in path."""
    if not url:
        return ""
    url = url.replace("&amp;", "&").strip()
    sp = urlsplit(url)
    scheme = "https"
    netloc = sp.netloc.lower()
    path = unquote(sp.path)
    path = re.sub(r"/{2,}", "/", path).rstrip("/")
    return urlunsplit((scheme, netloc, path, sp.query, ""))


def basename(url: str) -> str:
    return normalize_url(url).rsplit("/", 1)[-1]


def is_doc_link(url: str) -> bool:
    return bool(DOC_EXT_RE.search(url or ""))


def classify_noise(url: str) -> Optional[str]:
    """Return 'hard' (suppress), 'soft' (flag), or None."""
    bn = basename(url)
    if HARD_NOISE_RE.search(bn) or HARD_NOISE_RE.search(url):
        return "hard"
    if SOFT_NOISE_RE.search(bn):
        return "soft"
    return None


def extract_doc_links(html: str, page_url: str) -> List[str]:
    """All absolute document links on a page (deduped, order-preserving)."""
    out, seen = [], set()
    for href in HREF_RE.findall(html or ""):
        if not is_doc_link(href):
            continue
        absu = urljoin(page_url, href.replace("&amp;", "&"))
        n = normalize_url(absu)
        if n and n not in seen:
            seen.add(n)
            out.append(absu)
    return out


def collect_known(sources: List[Dict]) -> Tuple[Set[str], Set[str]]:
    """Known normalized URLs + known document basenames across the registry."""
    urls, names = set(), set()
    for s in sources:
        for key in ("url_primary", "url_landing"):
            u = s.get(key)
            if u:
                urls.add(normalize_url(u))
                if is_doc_link(u):
                    names.add(basename(u))
    return urls, names


def collect_watch_pages(sources: List[Dict]) -> List[str]:
    """Distinct EDB landing/index .html pages to crawl (from url_landing)."""
    seen, pages = set(), []
    for s in sources:
        u = s.get("url_landing") or ""
        if "edb.gov.hk" not in u or not u.lower().endswith((".html", "/")):
            continue
        n = normalize_url(u)
        if n and n not in seen:
            seen.add(n)
            pages.append(u)
    return pages


# ---------------------------------------------------------------------------
# Self-test (no network)
# ---------------------------------------------------------------------------
def run_self_test() -> int:
    f = 0
    def check(name, cond):
        nonlocal f
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            f += 1

    a = normalize_url("http://www.EDB.gov.hk/tc/a/b%20c.pdf#frag")
    check("normalize: scheme/host/%20/fragment", a == "https://www.edb.gov.hk/tc/a/b c.pdf")
    check("normalize: trailing slash + dup-slash",
          normalize_url("https://x.gov.hk//tc/a/") == "https://x.gov.hk/tc/a")
    check("is_doc_link pdf/doc/xlsx", all(map(is_doc_link, ["a.pdf", "b.PDF", "c.docx", "d.xlsx?x=1"])))
    check("is_doc_link rejects html", not is_doc_link("page.html"))
    check("classify_noise hard (PDPO)", classify_noise(".../common/EDB_PDPO_c.pdf") == "hard")
    check("classify_noise soft (poster)", classify_noise(".../GEF_injection_poster_TC.pdf") == "soft")
    check("classify_noise none (real guide)", classify_noise(".../SEKLACG_CHI_2017.pdf") is None)
    links = extract_doc_links(
        '<a href="docs/X.pdf">x</a><a href="Y.html">y</a><a href="docs/X.pdf">dup</a>'
        '<a href="http://z.gov.hk/W%20.pdf">w</a>', "https://www.edb.gov.hk/tc/k/index.html")
    check("extract_doc_links dedupes + resolves + skips html", links == [
        "https://www.edb.gov.hk/tc/k/docs/X.pdf", "http://z.gov.hk/W%20.pdf"])
    known, names = collect_known([{"url_primary": "https://e/a.pdf", "url_landing": "https://e/i.html"}])
    check("collect_known urls", normalize_url("https://e/a.pdf") in known)
    check("collect_known basenames", "a.pdf" in names)
    new = normalize_url("https://e/NEW.pdf") not in known
    check("diff: unseen url is new", new)

    print(f"\nSelf-test: {'ALL PASS' if f == 0 else f'{f} FAIL'}")
    return 1 if f else 0


# ---------------------------------------------------------------------------
def fetch(url: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT},
                         allow_redirects=True, timeout=FETCH_TIMEOUT)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        return r.text, None
    except Exception as e:
        return None, str(e)


def render_ledger(by_page: Dict[str, List[Dict]], today: str, pages: int,
                  new_count: int, errors: int) -> str:
    lines = [
        "# Newly Discovered EDB Documents — Pending Triage",
        "",
        "<!-- AUTO-GENERATED by dev/source/discover_sources.py --ledger. "
        "Do not hand-edit; overwritten each run. -->",
        "",
        f"- Generated: **{today}** (UTC)",
        f"- Watch pages crawled: {pages} · New candidates: **{new_count}** · Page errors: {errors}",
        "",
        "> ⚠️ Detection only. These are document links found on known EDB index pages "
        "that are NOT in `source_registry.json`. Many are dups / old versions / posters "
        "(`likely_noise`). Triage before any ingest (same manual gate as freshness).",
        "",
    ]
    if not new_count:
        lines.append("_No new documents discovered._")
        return "\n".join(lines) + "\n"
    for page, items in by_page.items():
        if not items:
            continue
        lines.append(f"### {page}")
        lines.append("")
        for it in items:
            tag = f" _(likely noise: {it['likely_noise']})_" if it.get("likely_noise") else ""
            lines.append(f"- `{it['filename']}`{tag}  \n  {it['url']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="Offline logic assertions and exit")
    ap.add_argument("--check", action="store_true", help="Read-only crawl (default behavior)")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="Crawl only the first N watch pages")
    ap.add_argument("--changes-out", default="discovered_sources.json")
    ap.add_argument("--ledger", default=None)
    args = ap.parse_args()

    if args.self_test:
        sys.exit(run_self_test())

    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found at {REGISTRY_PATH}")
        sys.exit(1)
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = registry.get("sources", [])

    known_urls, known_names = collect_known(sources)
    watch = collect_watch_pages(sources)
    if args.limit:
        watch = watch[:args.limit]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"🔎 Discovering new EDB docs across {len(watch)} watch pages "
          f"(known urls: {len(known_urls)})...")
    print("-" * 60)

    by_page: Dict[str, List[Dict]] = {}
    seen_new: Set[str] = set()
    new_records: List[Dict] = []
    errors = 0
    js_suspect = 0

    for i, page in enumerate(watch, 1):
        html, err = fetch(page)
        if err:
            errors += 1
            print(f"  ❌ {page} → {err}")
            continue
        links = extract_doc_links(html, page)
        if not links and len(html) > 50000:
            js_suspect += 1
            if args.verbose:
                print(f"  ⚠️ js_suspect (0 links, {len(html)//1000}KB): {page}")
        page_new = []
        for u in links:
            n = normalize_url(u)
            if n in known_urls or n in seen_new:
                continue
            noise = classify_noise(u)
            if noise == "hard":
                continue
            seen_new.add(n)
            rec = {
                "landing_page": page,
                "url": u,
                "filename": basename(u),
                "basename_known_elsewhere": basename(u) in known_names,
                "likely_noise": ("filename-pattern" if noise == "soft"
                                 else ("dup-basename" if basename(u) in known_names else None)),
            }
            page_new.append(rec)
            new_records.append(rec)
        by_page[page] = page_new
        if args.verbose and page_new:
            print(f"  [{i}] {page} → {len(page_new)} new")

    new_count = len(new_records)
    likely_real = [r for r in new_records if not r["likely_noise"]]

    report = {
        "generated_at": today,
        "watch_pages": len(watch),
        "known_urls": len(known_urls),
        "new_candidates": new_count,
        "likely_real": len(likely_real),
        "js_suspect_pages": js_suspect,
        "page_errors": errors,
        "candidates": new_records,
    }
    try:
        Path(args.changes_out).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
        print(f"\n📄 Report: {args.changes_out}")
    except Exception as e:
        print(f"  ⚠️ Could not write report: {e}")

    if args.ledger:
        try:
            Path(args.ledger).write_text(
                render_ledger(by_page, today, len(watch), new_count, errors), encoding="utf-8")
            print(f"📋 Ledger: {args.ledger}")
        except Exception as e:
            print(f"  ⚠️ Could not write ledger: {e}")

    print(f"\nSummary:")
    print(f"  Watch pages:     {len(watch)}")
    print(f"  New candidates:  {new_count}  (likely-real: {len(likely_real)}, "
          f"flagged-noise: {new_count - len(likely_real)})")
    print(f"  js_suspect:      {js_suspect}")
    print(f"  Page errors:     {errors}")

    # Page errors never fail the run unless catastrophic (most pages unreachable).
    threshold = max(5, len(watch) // 4)
    if errors > threshold:
        print(f"\n🚨 page errors {errors} > threshold {threshold} — exiting 1")
        sys.exit(1)


if __name__ == "__main__":
    main()
