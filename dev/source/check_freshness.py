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

Annual series (S216): a registry row that carries `url_primary_pattern` +
`years_extracted` instead of `url_primary` stands for one document per year
(`stat_enrolment_report` → 13 PDFs). `registry_series.expand_sources` turns it
into one monitored row per year before the loop, so those URLs are checked like
any other; their baselines live in the parent's `freshness_metadata_years`
(year → the same five fields), because one `content_hash` cannot describe 13
files. Rows that are not a series are passed through unchanged, by identity.

content_hash shares the same lifecycle as the other freshness_metadata fields:
it is seeded / refreshed only on a write-sync (non-dry-run). Scheduled dry-runs
detect drift against the last synced baseline and never persist, so they stay
cheap — only sources whose HEAD tripped AND already have a seeded hash are
downloaded for confirmation.

HTML pages (S249): an EDB page is ~270 KB of site shell (menus, footer) around
a few KB of real content, so a raw-byte hash reported "changed" whenever the
shell moved — 16 of the 35 items stuck in the issue were pages like that. For a
`text/html` response the fingerprint is now the visible text + document links
of the main-content region only (`inner_page_content_container`; whole-page text when
the marker is absent). `content_hash_kind` records which method produced the
stored hash; a baseline of another kind cannot be compared and is reported as
"baseline 需要重設" until it is acknowledged. The region's document links are
stored (`doc_links`) so a change can say which links were added or removed.

Exits for the pending list (S249) — every surface that asks a human to decide
needs a way out:
  --ack SID[,SID]   Re-baseline ONLY the named sources (after a re-ingest, or
                    after judging a change needs no action). Nothing else in
                    the registry is touched.
  --seed-missing    With --dry-run: persist a baseline for rows that have none
                    (a newly ingested source). It cannot hide a change — there
                    was nothing to compare against — so the scheduled run does
                    it unattended. Before S249, 95 sources had no baseline and
                    were therefore never checked for content change.

Outputs (in addition to the registry writeback):
  --changes-out PATH  Always writes a machine-readable change report (JSON) for
                      CI to consume (open/update a GitHub Issue). Default:
                      freshness_changes.json
  --ledger PATH       When given (write-sync only), renders a human Markdown
                      ledger of pending re-ingest work. Per FRESHNESS_GUIDE the
                      execution stays a manual gate — this only surfaces the
                      work, it does not perform it.

Usage: python3 check_freshness.py [--dry-run [--seed-missing]] [--verbose]
                                   [--limit N] [--changes-out PATH] [--ledger PATH]
       python3 check_freshness.py --ack SID[,SID...]
"""

import json
import hashlib
import html as html_lib
import re
import sys
import argparse
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urldefrag
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry_series as rs  # noqa: E402

# Constants
REGISTRY_PATH = Path("dev/source/source_registry.json")
HEAD_TIMEOUT = 15
GET_TIMEOUT = 60          # content download (large PDFs, e.g. g10 ~25MB)
HASH_CHUNK = 1 << 16      # 64 KiB streaming chunks
KIND_RAW = "raw-bytes"
KIND_EDB_MAIN = "html-main-v1"     # main-content region: visible text + doc links
KIND_HTML_TEXT = "html-text-v1"    # no region marker: whole-page visible text + doc links
MAIN_START = "inner_page_content_container"
MAIN_END = "footer_content"
DOC_LINK_RE = re.compile(r'''href\s*=\s*["\']([^"\'#]+\.(?:pdf|docx?|xlsx?|pptx?|zip))(?:[?#][^"\']*)?["\']''', re.I)
ACK_REPORT_DAYS = 8                # an ack is reported to CI for one weekly cycle
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get_headers(url: str) -> Optional[Dict[str, str]]:
    """Fetch HEAD headers for a URL (GET-fallback when HEAD is blocked)."""
    import requests
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


def html_fingerprint(body: bytes, url: str) -> Tuple[str, str, List[str]]:
    """Fingerprint an HTML page by what a reader would notice. Pure — offline
    testable. Returns (sha256, kind, sorted absolute document links).

    Only the main-content region counts when the EDB marker is present, so a
    change to the site menu or footer no longer reads as a change to the source.
    """
    text = body.decode("utf-8", "ignore")
    kind = KIND_HTML_TEXT
    a = text.find(MAIN_START)
    if a != -1:
        b = text.find(MAIN_END, a)
        text = text[a:b if b != -1 else len(text)]
        kind = KIND_EDB_MAIN
    links = sorted({urldefrag(urljoin(url, html_lib.unescape(m)))[0]
                    for m in DOC_LINK_RE.findall(text)})
    visible = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", text)
    visible = re.sub(r"(?s)<!--.*?-->", " ", visible)
    visible = re.sub(r"(?s)<[^>]+>", " ", visible)
    visible = re.sub(r"\s+", " ", html_lib.unescape(visible)).strip()
    h = hashlib.sha256()
    h.update(visible.encode("utf-8"))
    h.update(b"\n--links--\n")
    h.update("\n".join(links).encode("utf-8"))
    return h.hexdigest(), kind, links


def get_content_hash(url: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[List[str]]]:
    """GET the full body and return (hash, error, kind, doc_links).

    Non-HTML: streamed raw-byte SHA-256 (large PDFs do not balloon memory),
    kind `raw-bytes`, doc_links None. HTML: `html_fingerprint`. Returns
    (None, reason, None, None) on failure.
    """
    import requests
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
            return None, f"HTTP {resp.status_code}", None, None
        if "html" in (resp.headers.get("Content-Type") or "").lower():
            body = resp.content
            resp.close()
            digest, kind, links = html_fingerprint(body, resp.url or url)
            return digest, None, kind, links
        h = hashlib.sha256()
        for chunk in resp.iter_content(chunk_size=HASH_CHUNK):
            if chunk:
                h.update(chunk)
        resp.close()
        return h.hexdigest(), None, KIND_RAW, None
    except Exception as e:
        return None, str(e), None, None


def link_diff(old: Optional[List[str]], new: Optional[List[str]]) -> Optional[Dict[str, List[str]]]:
    """Added / removed document links, or None when either side was not recorded."""
    if old is None or new is None:
        return None
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new))}


def classify_change(cheap_changed: bool, old_hash: Optional[str],
                    new_hash: Optional[str], hash_computed: bool,
                    old_kind: str = KIND_RAW, new_kind: str = KIND_RAW) -> Tuple[bool, Optional[str]]:
    """Decide whether a source changed. Pure function — offline testable.

    The content hash is authoritative when a baseline hash exists and a fresh one
    was computed this run; otherwise degrade gracefully to the cheap HEAD signal.
    Returns (changed, confidence-label).
    """
    if old_hash and hash_computed and new_hash:
        if (old_kind or KIND_RAW) != (new_kind or KIND_RAW):
            # two different fingerprint methods cannot be compared; say so
            # rather than report a content change that may not exist
            return True, "baseline 需要重設 (比對方式已改)"
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


def build_meta(meta: Dict, last_mod, cont_len, etag, new_hash, new_kind,
               new_links, hash_checked_at) -> Dict:
    """The stored freshness record. `doc_links` / `acked_at` appear only when
    they have a value, so PDF rows keep the exact shape they always had (plus
    the kind) and the registry diff stays readable."""
    out = {
        "last_modified": last_mod,
        "content_length": cont_len,
        "etag": etag,
        "content_hash": new_hash,
        "hash_checked_at": hash_checked_at,
    }
    if new_hash and (new_kind or KIND_RAW) != KIND_RAW:
        out["content_hash_kind"] = new_kind
        if new_links is not None:
            out["doc_links"] = new_links
    if meta.get("acked_at"):
        out["acked_at"] = meta["acked_at"]
    return out


def run_ack(registry: Dict, monitored: List[Dict], ack_arg: str, today: str) -> int:
    """Re-baseline only the named sources. All-or-nothing: an unknown id or a
    failed fetch writes nothing, so a typo cannot half-apply."""
    wanted = [x.strip() for x in ack_arg.split(",") if x.strip()]
    rows = [r for r in monitored
            if (r["source_id"] in wanted or rs.parent_id(r) in wanted) and r.get("url_primary")]
    found = {r["source_id"] for r in rows} | {rs.parent_id(r) for r in rows}
    missing = [w for w in wanted if w not in found]
    if missing or not rows:
        print(f"❌ --ack: not a monitored source with a url: {', '.join(missing) or ack_arg}")
        return 2
    staged = []
    for r in rows:
        sid, url = r["source_id"], r["url_primary"]
        headers = get_headers(url)
        digest, err, kind, links = get_content_hash(url)
        if not headers or not digest:
            print(f"❌ --ack: could not fetch {sid} ({err or 'HEAD failed'}) — nothing written")
            return 1
        meta = dict(r.get("freshness_metadata") or {})
        old = (meta.get("content_hash") or "—")[:12]
        meta["acked_at"] = today
        staged.append((r, build_meta(meta, headers.get("Last-Modified"), headers.get("Content-Length"),
                                     headers.get("ETag"), digest, kind, links, today)))
        print(f"  ✅ ack {sid}: {old} → {digest[:12]}  [{kind}]"
              + (f"  {len(links)} doc link(s)" if links is not None else ""))
    for r, new_meta in staged:
        rs.record_freshness(r, today, new_meta)
    registry.setdefault("_meta", {})["updated"] = today
    tmp = REGISTRY_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    tmp.replace(REGISTRY_PATH)
    print(f"💾 Registry updated: {len(staged)} baseline(s) acknowledged")
    return 0


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

    def assert_(name: str, cond: bool) -> None:
        nonlocal failures
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            failures += 1

    # --- HTML fingerprint (S249) ----------------------------------------------
    def page(shell: str, main: str) -> bytes:
        return (f'<html><div class="menu">{shell}</div>'
                f'<div class="{MAIN_START}">{main}</div>'
                f'<div class="{MAIN_END}">{shell} footer</div></html>').encode("utf-8")
    base_main = '<p>教職員批假指引</p><a href="/a/leave.pdf">PDF</a><script>var t=1;</script>'
    u = "https://www.edb.gov.hk/tc/x/index.html"
    h0, k0, l0 = html_fingerprint(page("menu v1", base_main), u)
    assert_("an EDB page is fingerprinted by its main-content region", k0 == KIND_EDB_MAIN)
    assert_("document links are absolute and recorded",
            l0 == ["https://www.edb.gov.hk/a/leave.pdf"])
    assert_("a change to the site shell (menu / footer) is not a change",
            html_fingerprint(page("menu v2 <a href='/new/privacy.pdf'>x</a>", base_main), u)[0] == h0)
    assert_("whitespace and script noise inside the content is not a change",
            html_fingerprint(page("menu v1", base_main.replace("<p>", "<p>\n  ")
                                  .replace("var t=1", "var t=2")), u)[0] == h0)
    assert_("a change to the content text IS a change",
            html_fingerprint(page("menu v1", base_main.replace("批假", "請假")), u)[0] != h0)
    h2, _, l2 = html_fingerprint(page("menu v1", base_main + '<a href="new.pdf#p2">新</a>'), u)
    assert_("a new document link IS a change, and the diff names it",
            h2 != h0 and link_diff(l0, l2) == {
                "added": ["https://www.edb.gov.hk/tc/x/new.pdf"], "removed": []})
    assert_("a page without the region marker falls back to whole-page text",
            html_fingerprint(b"<html><p>hi</p></html>", u)[1] == KIND_HTML_TEXT)
    assert_("link_diff says nothing when a side was never recorded",
            link_diff(None, l0) is None)
    assert_("baselines of two different kinds are not compared as a content change",
            "重設" in (classify_change(True, "a"*64, "b"*64, True, KIND_RAW, KIND_EDB_MAIN)[1] or ""))
    assert_("same kind, equal hash → still suppressed",
            classify_change(True, "a"*64, "a"*64, True, KIND_EDB_MAIN, KIND_EDB_MAIN) == (False, None))
    pdf_meta = build_meta({}, "L", "1", "E", "a"*64, KIND_RAW, None, "2026-11-16")
    assert_("a PDF row keeps its original five fields exactly",
            sorted(pdf_meta) == ["content_hash", "content_length", "etag",
                                 "hash_checked_at", "last_modified"])
    html_meta = build_meta({"acked_at": "2026-11-16"}, None, None, None, "a"*64,
                           KIND_EDB_MAIN, ["x"], "2026-11-16")
    assert_("an HTML row records its kind, links, and keeps acked_at",
            html_meta["content_hash_kind"] == KIND_EDB_MAIN and html_meta["doc_links"] == ["x"]
            and html_meta["acked_at"] == "2026-11-16")

    # --- annual series (S216) — which URLs the loop gets to see ---------------

    plain = {"source_id": "g29", "url_primary": "https://e/g29.pdf",
             "freshness_metadata": {"content_hash": "a" * 64}}
    series = {"source_id": "stat_enrolment_report",
              "url_primary_pattern": "https://e/Enrol_{YYYY}.pdf",
              "years_extracted": [2012, 2013],
              "freshness_metadata_years": {"2012": {"content_hash": "b" * 64}}}

    assert_("an ordinary row is passed through by identity (no copy, no change)",
            rs.monitor_rows(plain) == [plain] and rs.monitor_rows(plain)[0] is plain)
    rows = rs.monitor_rows(series)
    assert_("a series row expands to one row per year",
            [r["source_id"] for r in rows] == ["stat_enrolment_2012",
                                               "stat_enrolment_2013"])
    assert_("each year gets its own url from the pattern",
            [r["url_primary"] for r in rows] == ["https://e/Enrol_2012.pdf",
                                                 "https://e/Enrol_2013.pdf"])
    assert_("a year with a stored baseline sees it; a year without sees none",
            rows[0]["freshness_metadata"] == {"content_hash": "b" * 64}
            and rows[1]["freshness_metadata"] is None)

    # Writeback: the ordinary path must stay literally the two assignments it
    # was, and a series year must land on the PARENT — the derived row is a copy
    # and anything written to it would be dropped on the floor.
    p = dict(plain)
    rs.record_freshness(p, "2026-09-13", {"content_hash": "c" * 64})
    assert_("an ordinary row's result is written to the row itself, as before",
            p["freshness_metadata"] == {"content_hash": "c" * 64}
            and p["last_checked_at"] == "2026-09-13")
    rs.record_freshness(rows[1], "2026-09-13", {"content_hash": "d" * 64})
    assert_("a series year's result is written to the parent, not lost on the copy",
            series["freshness_metadata_years"]["2013"] == {"content_hash": "d" * 64}
            and series["last_checked_at"] == "2026-09-13")
    assert_("writing one year does not disturb another year's baseline",
            series["freshness_metadata_years"]["2012"] == {"content_hash": "b" * 64})
    assert_("a series parent grows no scalar freshness_metadata",
            "freshness_metadata" not in series)

    # Registry reality — the invariant that keeps `expand_url` honest. A pattern
    # with no {YYYY} slot would expand to N identical URLs instead of failing,
    # so the structural check lives here rather than in the expansion.
    reg = json.loads((Path(__file__).resolve().parent / "source_registry.json")
                     .read_text(encoding="utf-8"))
    reg_sources = reg["sources"] if isinstance(reg, dict) else reg
    patterned = [s for s in reg_sources if s.get("url_primary_pattern")]
    assert_(f"every url_primary_pattern in the registry carries {rs.YEAR_SLOT} "
            f"({len(patterned)} row(s))",
            bool(patterned) and all(rs.YEAR_SLOT in s["url_primary_pattern"]
                                    for s in patterned))
    expanded = rs.expand_sources(reg_sources)
    gained = len(expanded) - len(reg_sources)
    print(f"     [registry] {len(reg_sources)} rows → {len(expanded)} monitored "
          f"(+{gained} from {len(patterned)} annual series)")
    assert_("the registry's annual series now yields http urls to check",
            all((r.get("url_primary") or "").startswith("http")
                for r in expanded if rs.is_shard(r)) and gained > 0)
    assert_("no registry row is dropped by the expansion",
            {rs.parent_id(r) for r in expanded}
            >= {s["source_id"] for s in reg_sources})

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
    parser.add_argument("--seed-missing", action="store_true",
                        help="With --dry-run: still persist a baseline for rows that have none")
    parser.add_argument("--ack", default=None, metavar="SID[,SID]",
                        help="Re-baseline only these sources (after re-ingest / no action needed) and exit")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test())
    if args.ack and (args.dry_run or args.seed_missing or args.limit):
        parser.error("--ack runs on its own (it writes only the named sources)")

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

    # An annual-series row becomes one row per year here; every other row is
    # passed through by identity, so the loop below is unchanged for them.
    monitored = rs.expand_sources(sources)

    if args.ack:
        sys.exit(run_ack(registry, monitored, args.ack, today))

    seeded = 0
    acked_recent: List[str] = []
    ack_cutoff = (datetime.now(timezone.utc) - timedelta(days=ACK_REPORT_DAYS)).strftime("%Y-%m-%d")

    gained = len(monitored) - len(sources)
    print(f"🔍 Checking freshness for {len(monitored)} sources..."
          + (f" ({len(sources)} registry rows, +{gained} annual-series years)"
             if gained else ""))
    mode = ("dry-run + seed-missing" if args.dry_run and args.seed_missing
            else "dry-run" if args.dry_run else "write-sync")
    print(f"📅 Today: {today}  | mode: {mode}")
    print("-" * 60)

    for src in monitored:
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
        old_kind = meta.get("content_hash_kind") or KIND_RAW
        if (meta.get("acked_at") or "") >= ack_cutoff:
            acked_recent.append(sid)

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
        #   - an HTML baseline: always (a page is small, and a dynamic page may
        #     send no Last-Modified / Content-Length for the cheap tier to trip on).
        seeding = (not old_hash) and ((not args.dry_run) or args.seed_missing)
        need_hash = (cheap_changed and bool(old_hash)) or seeding or \
            (bool(old_hash) and old_kind != KIND_RAW)
        new_hash = old_hash
        new_kind = old_kind
        new_links = meta.get("doc_links")
        hash_state = "skipped"
        if need_hash:
            computed, herr, kind, links = get_content_hash(url)
            if computed:
                new_hash = computed
                new_kind = kind
                new_links = links
                hashed += 1
                hash_state = "computed"
            else:
                hash_state = f"fetch_failed ({herr})"
                if args.verbose:
                    print(f"     ⚠️ hash fetch failed for {sid}: {herr}")

        # Decide changed — content hash is authoritative when both sides exist.
        changed, confidence = classify_change(
            cheap_changed, old_hash, new_hash, hash_state == "computed",
            old_kind, new_kind
        )

        # Update record (persisted only when not dry-run). For an ordinary row
        # this is the same two assignments it always was; for a series year it
        # lands in the parent's year-keyed store instead of overwriting a single
        # scalar thirteen times.
        # A dry run must leave the row alone — except a row being seeded, which
        # had no baseline to lose.
        seeded_now = seeding and hash_state == "computed"
        if (not args.dry_run) or seeded_now:
            rs.record_freshness(src, today, build_meta(
                meta, last_mod, cont_len, etag, new_hash, new_kind, new_links,
                today if hash_state == "computed" else meta.get("hash_checked_at")))
            if seeded_now and args.dry_run:
                seeded += 1
                print(f"  🌱 seeded baseline: {sid}  [{new_kind}]")

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
                "links": link_diff(meta.get("doc_links"), new_links)
                         if hash_state == "computed" else None,
            })
            print(f"  🔔 CHANGE: {sid}  [{confidence}]")
            print(f"     Old: Mod={old_mod}, Len={old_len}, hash={(old_hash or '—')[:12]}")
            print(f"     New: Mod={last_mod}, Len={cont_len}, hash={(new_hash or '—')[:12] if hash_state=='computed' else '(not fetched)'}")
        elif args.verbose:
            print(f"  ✅ OK: {sid}")

    write_registry = (not args.dry_run) or seeded > 0
    if write_registry:
        registry.setdefault("_meta", {})["updated"] = today

    if write_registry:
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
        "seeded": seeded,
        # acknowledged within the last weekly cycle and no longer changed: CI
        # forgets these keys, so a later change to the same source notifies again
        "acked_sources": sorted(set(acked_recent) - {c["source_id"] for c in changed_records}),
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
    print(f"  Seeded:     {seeded}")
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
