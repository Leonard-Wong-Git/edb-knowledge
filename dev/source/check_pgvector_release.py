#!/usr/bin/env python3
"""check_pgvector_release.py — 第 7 個監察：Supabase 幾時封裝 pgvector ≥ 0.8.4（S222）

Why this exists
---------------
HNSW is the one structural direction this project has left on the index side,
and it is blocked — not by a decision anybody can make, but by two upstream
fixes that are not yet packaged:

  0.8.3  Fixed possible index corruption with HNSW vacuuming
  0.8.4  Fixed `hnsw graph not repaired` error with HNSW vacuuming, and insert
         errors during vacuuming

Neither is avoidable by configuration. PostgreSQL runs anti-wraparound
autovacuum even when `autovacuum_enabled = false`, so an HNSW index built on a
build older than 0.8.4 carries a permanent corruption risk, not a one-off
build-time risk. (The third fix people quote, 0.8.2 / CVE-2026-3172 parallel
build overflow, DOES have an official mitigation — `set
max_parallel_maintenance_workers = 0` before the build — so it is not what is
blocking us. Getting that distinction wrong is what made the earlier handoff
note half-right.)

Supabase's own extension build tops out at 0.8.2. So the block lifts on a
packaging event upstream, at a date nobody here controls. The handoff recorded
that as "waiting for Leonard to decide", which is wrong: there is no decision,
only a wait. A wait belongs to a machine, not to a human decision surface.

Where it sits among the other monitors
--------------------------------------
  check_freshness      "did the upstream bytes change?"        — registry URLs
  check_served_urls    "does the link a user clicks work?"     — wiki_chunks.url
  discover_sources     "is there something we haven't got?"    — EDB index pages
  check_source_titles  "is this the document we think it is?"  — PDF covers
  check_new_circulars  "is there a new circular?"              — dashboard feed
  check_expiry         "should this still be in the corpus?"   — registry lifecycle
  check_pgvector_release
                       "is the platform blocker still there?"  — Supabase packaging

It is the only one that watches a THIRD-PARTY BUILD rather than our own corpus,
and the only one whose correct steady state is total silence.

紀律 #14 (the design constraint)
--------------------------------
Any surface that needs a human decision must have an exit, and an append-only
list becomes wallpaper that buries the real signal. Four monitors in this repo
had to be repaired for exactly that (`discover_sources` re-announcing a 238-doc
backlog every week → the seen-ledger; `check_expiry` keeping already-purged
sources on the action list; the eval harness going red every morning on Option
A ingests → `DISPLACED`; the "course page" monitor that was never built because
it would have reported "changed" every term).

Applied here, that rule has a sharp consequence:

  * UNCHANGED  → say nothing. No weekly "still 0.8.2".
  * CHANGED but still below the threshold (say 0.8.3 lands) → ALSO say nothing.
    0.8.3 does not unblock anything, so a notice about it is a notice nobody can
    act on, which is precisely the wallpaper. It is still recorded, in the state
    file and the run report — the committed diff on `pgvector_seen.json` is the
    trace, and a trace is not an alert.
  * UNBLOCKED  → speak once, loudly, open the Issue. The exit is a human closing
    that Issue after acting; the state file has already recorded the version, so
    the monitor never re-announces it.
  * SCHEMA_CHANGED → speak, and go red. That URL is a third-party path on a
    `develop` branch; it WILL move. A watcher that has quietly lost sight of its
    subject is worse than no watcher, because it manufactures a false "still
    blocked" every week for ever.
  * FETCH_FAILED → go red, but no Issue. A 5xx or a timeout is transient; the
    red scheduled run is the notice and next week's run is the retry.

Signal routing follows the house convention (S126): content findings go to the
Issue and never touch the exit code; only the tool being broken exits non-zero.
Here the "content finding" is UNBLOCKED (exit 0, loud Issue) and the "tool
broken" cases are SCHEMA_CHANGED / FETCH_FAILED (exit 1).

There is deliberately no Markdown ledger. The sibling monitors write one because
they produce a triage LIST; this one produces a single boolean, and a one-line
ledger regenerated weekly is a file whose only content is noise.

Usage (from repo root):
  python3 dev/source/check_pgvector_release.py --self-test         # offline, fixtures
  python3 dev/source/check_pgvector_release.py --prove-assertions  # tests must go red
  python3 dev/source/check_pgvector_release.py --check             # live, one fetch
  python3 dev/source/check_pgvector_release.py --check --changes-out pgvector_watch.json
  python3 dev/source/check_pgvector_release.py --check --no-state  # don't write state

No keys. One unauthenticated GET against a public raw.githubusercontent.com path.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_PATH = REPO_ROOT / "dev" / "source" / "pgvector_seen.json"

# Source of truth for what Supabase's Postgres image can actually install. This
# is the packaging manifest, i.e. the LEADING indicator: a version appears here
# before any project's instance is ever offered it. Verified live 2026-09-13.
VERSIONS_URL = ("https://raw.githubusercontent.com/supabase/postgres/"
                "develop/nix/ext/versions.json")
EXTENSION_KEY = "vector"

FETCH_TIMEOUT = 30
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# THE THRESHOLD. Not a magic number: 0.8.3 fixes "possible index corruption with
# HNSW vacuuming" and 0.8.4 fixes the "hnsw graph not repaired" error plus insert
# errors during vacuuming. BOTH must be in, and the second one only arrives at
# 0.8.4 — so 0.8.3 is explicitly NOT sufficient and must not trigger. Raise this
# only against a read of the pgvector CHANGELOG, never to silence the monitor.
HNSW_SAFE_MIN_VERSION = (0, 8, 4)

# A version string we will act on must be exactly numeric. `0.8.4-rc1` parses to
# None on purpose: a pre-release in a packaging manifest is not a release, and
# unblocking a corruption-risk decision on an rc tag would be the wrong failure
# direction.
VERSION_RE = re.compile(r"^\d+(?:\.\d+){1,2}$")

# Per-verdict routing. Kept as data (not scattered `if`s in the workflow YAML) so
# the 紀律 #14 contract is something the self-test can assert.
SPEAKS = {                    # does a human hear about this run at all?
    "UNBLOCKED": True,
    "SCHEMA_CHANGED": True,
    "FETCH_FAILED": True,
    "CHANGED": False,
    "UNCHANGED": False,
    "BASELINE": False,
}
OPENS_ISSUE = {               # ...and does it get a standing, closable surface?
    "UNBLOCKED": True,
    "SCHEMA_CHANGED": True,
    "FETCH_FAILED": False,    # transient: the red scheduled run is the notice
    "CHANGED": False,
    "UNCHANGED": False,
    "BASELINE": False,
}
EXIT_CODE = {                 # only a broken tool is a build failure
    "UNBLOCKED": 0,
    "SCHEMA_CHANGED": 1,
    "FETCH_FAILED": 1,
    "CHANGED": 0,
    "UNCHANGED": 0,
    "BASELINE": 0,
}
PERSISTS = {                  # may this run overwrite the committed state file?
    "UNBLOCKED": True,
    "CHANGED": True,
    "UNCHANGED": True,
    "BASELINE": True,
    "SCHEMA_CHANGED": False,  # we did not see a list; writing would erase the baseline
    "FETCH_FAILED": False,
}
LABEL = {
    "UNBLOCKED": "封裝咗 ≥ 0.8.4 —— HNSW 的封鎖項已解除",
    "CHANGED": "版本清單有變，但仍未到 0.8.4（記錄，不通報）",
    "UNCHANGED": "與上次所見相同（靜默）",
    "BASELINE": "首次建立基線（靜默）",
    "SCHEMA_CHANGED": "上游檔案搬走／`vector` 鍵消失／結構改變 —— 監察已瞎",
    "FETCH_FAILED": "抓取失敗（暫時性）",
}


# ---------------------------------------------------------------------------
# pure helpers (offline-testable)
# ---------------------------------------------------------------------------
def parse_version(text: object) -> Optional[Tuple[int, int, int]]:
    """`"0.8.2"` → `(0, 8, 2)`; `"1.0"` → `(1, 0, 0)`; anything else → None.

    Strict on purpose — see VERSION_RE.
    """
    s = str(text or "").strip()
    if not VERSION_RE.match(s):
        return None
    parts = [int(p) for p in s.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return (parts[0], parts[1], parts[2])


def sort_versions(versions: List[str], parse=parse_version) -> List[str]:
    """Numeric order, not lexical (`0.10.0` sorts after `0.8.2`). Unparseable
    entries are kept — they are evidence of an upstream change — and pushed to
    the end so they can never masquerade as "the newest version"."""
    good = sorted((v for v in versions if parse(v)), key=lambda v: parse(v))
    bad = sorted(v for v in versions if not parse(v))
    return good + bad


def unblocking_versions(versions: List[str], parse=parse_version) -> List[str]:
    """The subset that actually clears HNSW_SAFE_MIN_VERSION."""
    return [v for v in versions
            if (parse(v) or (0, 0, 0)) >= HNSW_SAFE_MIN_VERSION and parse(v)]


def unparseable_versions(versions: List[str], parse=parse_version) -> List[str]:
    return [v for v in versions if not parse(v)]


def extract_versions(doc: object, parse=parse_version
                     ) -> Tuple[Optional[List[str]], Optional[str]]:
    """`(sorted version strings, shape_error)` from a parsed versions.json.

    Every rejection returns a SENTENCE, not None — the whole point of the
    SCHEMA_CHANGED outcome is that a person can read what broke without opening
    the upstream file themselves.
    """
    if not isinstance(doc, dict):
        return None, (f"top level of versions.json is a {type(doc).__name__}, "
                      "expected a JSON object keyed by extension name")
    if EXTENSION_KEY not in doc:
        near = ", ".join(sorted(k for k in doc if "vec" in str(k).lower())) or "none"
        return None, (f"key '{EXTENSION_KEY}' is no longer present "
                      f"({len(doc)} extension key(s) in the file; "
                      f"vector-like keys: {near})")
    block = doc[EXTENSION_KEY]
    if not isinstance(block, dict):
        return None, (f"'{EXTENSION_KEY}' is a {type(block).__name__}, expected an "
                      "object keyed by version string")
    if not block:
        return None, f"'{EXTENSION_KEY}' is present but empty"
    versions = [str(k) for k in block]
    if not any(parse(v) for v in versions):
        return None, (f"no key under '{EXTENSION_KEY}' parses as a version "
                      f"(saw: {', '.join(sorted(versions)[:5])})")
    return sort_versions(versions, parse), None


def classify(seen: Optional[Dict], current: List[str],
             shape_error: Optional[str] = None,
             fetch_error: Optional[str] = None,
             parse=parse_version) -> Dict:
    """The whole decision, as one pure function over (last-seen, now).

    `seen is None` means no committed state file — a fresh install, not a change.
    """
    if fetch_error:
        return _verdict("FETCH_FAILED", reason=fetch_error)
    if shape_error:
        return _verdict("SCHEMA_CHANGED", reason=shape_error)

    previous = list((seen or {}).get("versions") or [])
    added = [v for v in current if v not in previous]
    removed = [v for v in previous if v not in current]
    unblocking = unblocking_versions(current, parse)
    # "Newly" is what makes this speak once instead of every week: on the run
    # after the announcement the qualifying version is already in `previous`.
    newly = [v for v in unblocking if seen is None or v in added]

    if unblocking and newly:
        verdict = "UNBLOCKED"
    elif seen is None:
        verdict = "BASELINE"
    elif added or removed:
        verdict = "CHANGED"
    else:
        verdict = "UNCHANGED"

    return _verdict(
        verdict,
        current=current, previous=previous, added=added, removed=removed,
        unblocking=unblocking, newly_unblocking=newly,
        unparseable=unparseable_versions(current, parse),
        unblocked=bool(unblocking),
        highest=(sort_versions(current, parse) or [None])[-1] if current else None,
        reason=LABEL[verdict],
    )


def _verdict(verdict: str, **extra) -> Dict:
    out = {
        "verdict": verdict,
        "label": LABEL[verdict],
        "speaks": SPEAKS[verdict],
        "opens_issue": OPENS_ISSUE[verdict],
        "exit_code": EXIT_CODE[verdict],
        "persists_state": PERSISTS[verdict],
        "threshold": ".".join(str(n) for n in HNSW_SAFE_MIN_VERSION),
        "current": [], "previous": [], "added": [], "removed": [],
        "unblocking": [], "newly_unblocking": [], "unparseable": [],
        "unblocked": False, "highest": None, "reason": "",
    }
    out.update(extra)
    return out


# ---------------------------------------------------------------------------
# state file  (prior art: dev/source/discovery_seen.json, S209)
# ---------------------------------------------------------------------------
def load_state(path: Optional[Path]) -> Optional[Dict]:
    """None means "no baseline yet" — deliberately distinct from an empty list,
    which would mean "upstream really has zero versions"."""
    if not path or not Path(path).exists():
        return None
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:                                        # noqa: BLE001
        return None
    return doc if isinstance(doc, dict) and "versions" in doc else None


def build_state(seen: Optional[Dict], current: List[str], today: str,
                verdict: str) -> Dict:
    """Carry each version's original first-seen date forward; stamp new ones."""
    old_first = dict((seen or {}).get("first_seen") or {})
    first_seen = {v: old_first.get(v, today) for v in current}
    return {
        "_semantics": ("Rewritten ONLY when the version list or the verdict "
                       "changes, so the weekly job produces no commit in the "
                       "steady state. `last_change_at` is therefore the date the "
                       "ANSWER last moved, not the date it was last checked — "
                       "run history lives in the workflow, not in this file."),
        "last_change_at": today,
        "source_url": VERSIONS_URL,
        "extension_key": EXTENSION_KEY,
        "hnsw_safe_min_version": ".".join(str(n) for n in HNSW_SAFE_MIN_VERSION),
        "last_verdict": verdict,
        "versions": current,
        "first_seen": first_seen,
    }


def write_state(path: Path, state: Dict) -> None:
    Path(path).write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8")


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------
def fetch(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """`(body, transient_error, structural_error)`.

    A 4xx is STRUCTURAL — the path moved or was renamed, which is the failure
    this monitor was told to expect. A 5xx or a socket error is TRANSIENT.
    """
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT},
                         allow_redirects=True, timeout=FETCH_TIMEOUT)
    except Exception as e:                                   # noqa: BLE001
        return None, f"could not reach {url}: {e}", None
    if 400 <= r.status_code < 500:
        return None, None, (f"HTTP {r.status_code} for {url} — the upstream path "
                            "has moved or been renamed")
    if r.status_code != 200:
        return None, f"HTTP {r.status_code} for {url}", None
    return r.text, None, None


# ---------------------------------------------------------------------------
# self-test  (offline: every assertion runs against a fixture, never the network)
# ---------------------------------------------------------------------------
# A trimmed but structurally faithful copy of the live file, captured 2026-09-13.
# Every `vector` key present upstream on that date is here; the sibling extension
# and the per-version payload shape are kept so a shape change upstream is a real
# difference against this fixture, not a difference against a simplification.
FIXTURE_VERSIONS_JSON = json.dumps({
    "pgjwt": {"9742dab1b2f297ad3811120db7b21451bca2d3c9": {
        "postgresql": ["15", "17"], "hash": "sha256-fixture"}},
    "vector": {
        "0.4.0": {"postgresql": ["15"], "hash": "sha256-bOckX7zvHhgJ"},
        "0.5.1": {"postgresql": ["15", "17"], "hash": "sha256-ZNzq+dATZn9L"},
        "0.6.0": {"postgresql": ["15", "17"], "hash": "sha256-hXm+k0BZ9xZP"},
        "0.6.2": {"postgresql": ["15", "17"], "hash": "sha256-r+TpFJg6WrMn"},
        "0.7.0": {"postgresql": ["15", "17"], "hash": "sha256-vFn7sNphOYyi"},
        "0.7.4": {"postgresql": ["15", "17"], "hash": "sha256-qwPaguQUdDHV"},
        "0.8.0": {"postgresql": ["15", "17"], "hash": "sha256-JsZV+I4eRMyp"},
        "0.8.2": {"postgresql": ["15", "17"], "hash": "sha256-TLPlH+amFdeI"},
    },
})
LIVE_VERSIONS_2026_09_13 = ["0.4.0", "0.5.1", "0.6.0", "0.6.2",
                            "0.7.0", "0.7.4", "0.8.0", "0.8.2"]

FAILS: List[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        FAILS.append(label)


def run_self_test(parse, classify_fn) -> int:
    def st(seen, current, **kw):
        return classify_fn(seen, current, parse=parse, **kw)

    print("parse_version() — what counts as a release:")
    check("a three-part version parses", parse("0.8.2") == (0, 8, 2))
    check("the threshold version parses", parse("0.8.4") == (0, 8, 4))
    check("a two-part version is padded", parse("1.0") == (1, 0, 0))
    check("a pre-release tag does NOT parse (an rc must not unblock)",
          parse("0.8.4-rc1") is None)
    check("a git sha (the shape sibling extensions use) does NOT parse",
          parse("9742dab1b2f297ad3811120db7b21451bca2d3c9") is None)
    check("empty / None do not parse", parse("") is None and parse(None) is None)

    print("\nordering — numeric, not lexical:")
    check("0.10.0 sorts after 0.8.2, not before",
          sort_versions(["0.8.2", "0.10.0", "0.9.0"], parse)
          == ["0.8.2", "0.9.0", "0.10.0"])
    check("an unparseable entry is kept but never sorts last-as-newest",
          sort_versions(["zzz", "0.8.2"], parse) == ["0.8.2", "zzz"])

    print("\nthe threshold — 0.8.3 is NOT enough:")
    check("0.8.2 (what Supabase ships today) does not unblock",
          unblocking_versions(["0.8.2"], parse) == [])
    check("0.8.3 does not unblock — the second vacuum fix lands in 0.8.4",
          unblocking_versions(["0.8.3"], parse) == [])
    check("0.8.4 unblocks", unblocking_versions(["0.8.4"], parse) == ["0.8.4"])
    check("a later minor/major unblocks",
          unblocking_versions(["0.9.0", "1.0.0"], parse) == ["0.9.0", "1.0.0"])
    check("only the qualifying versions are picked out of a full list",
          unblocking_versions(LIVE_VERSIONS_2026_09_13 + ["0.8.4"], parse)
          == ["0.8.4"])
    check("an rc cannot unblock even though it looks newer",
          unblocking_versions(["0.8.2", "0.8.4-rc1"], parse) == [])

    print("\nextract_versions() — reading the upstream file:")
    got, err = extract_versions(json.loads(FIXTURE_VERSIONS_JSON), parse)
    check("the real-shaped fixture yields exactly the 8 live versions",
          err is None and got == LIVE_VERSIONS_2026_09_13)
    check("a sibling extension's keys are not mixed in",
          got is not None and "9742dab1b2f297ad3811120db7b21451bca2d3c9" not in got)
    _, err = extract_versions({"pgjwt": {}}, parse)
    check("a missing 'vector' key is a sentence, not a crash",
          err is not None and "vector" in err)
    _, err = extract_versions({"vector": ["0.8.2"]}, parse)
    check("'vector' as a list is reported as a shape change",
          err is not None and "list" in err)
    _, err = extract_versions([{"vector": {}}], parse)
    check("a top-level list is reported as a shape change", err is not None)
    _, err = extract_versions({"vector": {}}, parse)
    check("an empty 'vector' object is reported, not read as zero versions",
          err is not None)
    _, err = extract_versions({"vector": {"main": {}, "dev": {}}}, parse)
    check("'vector' keyed by branch names instead of versions is reported",
          err is not None)

    print("\nclassify() — 紀律 #14: silence is the correct steady state:")
    base = {"versions": list(LIVE_VERSIONS_2026_09_13)}
    r = st(base, list(LIVE_VERSIONS_2026_09_13))
    check("an unchanged list is UNCHANGED", r["verdict"] == "UNCHANGED")
    check("...and says nothing, opens nothing, exits 0",
          not r["speaks"] and not r["opens_issue"] and r["exit_code"] == 0)
    r = st(base, LIVE_VERSIONS_2026_09_13 + ["0.8.3"])
    check("0.8.3 appearing is CHANGED, not UNBLOCKED", r["verdict"] == "CHANGED")
    check("...and is still SILENT — nobody can act on 0.8.3",
          not r["speaks"] and not r["opens_issue"] and r["exit_code"] == 0)
    check("...but it is recorded as added, so the state diff carries the trace",
          r["added"] == ["0.8.3"])
    r = st(base, LIVE_VERSIONS_2026_09_13 + ["0.8.4"])
    check("0.8.4 appearing is UNBLOCKED", r["verdict"] == "UNBLOCKED")
    check("...and it speaks and opens the Issue",
          r["speaks"] and r["opens_issue"])
    check("...and does NOT fail CI (a finding is not a build failure)",
          r["exit_code"] == 0)
    check("...naming the version that did it", r["newly_unblocking"] == ["0.8.4"])
    r = st({"versions": LIVE_VERSIONS_2026_09_13 + ["0.8.4"]},
           LIVE_VERSIONS_2026_09_13 + ["0.8.4"])
    check("the week AFTER the announcement it goes quiet again (speaks once)",
          r["verdict"] == "UNCHANGED" and not r["speaks"])
    check("...while the report still tells the truth about being unblocked",
          r["unblocked"] is True)
    r = st(None, list(LIVE_VERSIONS_2026_09_13))
    check("a first run with no state file is BASELINE, not a change",
          r["verdict"] == "BASELINE" and not r["speaks"])
    r = st(None, LIVE_VERSIONS_2026_09_13 + ["0.8.4"])
    check("a first run into an ALREADY-unblocked world still speaks",
          r["verdict"] == "UNBLOCKED" and r["speaks"])
    r = st(base, [v for v in LIVE_VERSIONS_2026_09_13 if v != "0.4.0"])
    check("a version being withdrawn is CHANGED and recorded",
          r["verdict"] == "CHANGED" and r["removed"] == ["0.4.0"])

    print("\nclassify() — the monitor going blind:")
    r = st(base, [], shape_error="key 'vector' is no longer present")
    check("a shape change is SCHEMA_CHANGED", r["verdict"] == "SCHEMA_CHANGED")
    check("...it speaks, opens an Issue, AND fails the run",
          r["speaks"] and r["opens_issue"] and r["exit_code"] == 1)
    check("...carrying the upstream reason verbatim", "vector" in r["reason"])
    r = st(base, [], fetch_error="HTTP 503")
    check("a transient fetch error is FETCH_FAILED and fails the run",
          r["verdict"] == "FETCH_FAILED" and r["exit_code"] == 1)
    check("...but opens no Issue (transient — next week is the retry)",
          not r["opens_issue"])
    check("a blind run must NEVER overwrite the committed baseline",
          not st(base, [], shape_error="x")["persists_state"]
          and not st(base, [], fetch_error="x")["persists_state"])
    check("a sighted run always may",
          all(st(base, list(LIVE_VERSIONS_2026_09_13))["persists_state"]
              for _ in (0,)))

    print("\nrouting table is total (no verdict can fall through):")
    verdicts = set(LABEL)
    check("every verdict has speak / issue / exit / persist routing",
          verdicts == set(SPEAKS) == set(OPENS_ISSUE) == set(EXIT_CODE)
          == set(PERSISTS))
    check("exactly two verdicts are allowed to fail CI",
          {v for v, c in EXIT_CODE.items() if c} == {"SCHEMA_CHANGED",
                                                     "FETCH_FAILED"})
    check("exactly one CONTENT verdict speaks (紀律 #14)",
          {v for v in ("UNBLOCKED", "CHANGED", "UNCHANGED", "BASELINE")
           if SPEAKS[v]} == {"UNBLOCKED"})

    print("\nstate file:")
    check("a missing state file reads as no-baseline, not as empty-upstream",
          load_state(None) is None
          and load_state(Path("/nonexistent/pgvector_seen.json")) is None)
    s = build_state({"first_seen": {"0.8.0": "2026-01-01"}},
                    ["0.8.0", "0.8.2"], "2026-09-13", "CHANGED")
    check("an existing version keeps its original first-seen date",
          s["first_seen"]["0.8.0"] == "2026-01-01")
    check("a newly appeared version is stamped today",
          s["first_seen"]["0.8.2"] == "2026-09-13")
    check("the state records what it was watching, so a future reader can tell",
          s["source_url"] == VERSIONS_URL and s["extension_key"] == EXTENSION_KEY
          and s["hnsw_safe_min_version"] == "0.8.4")
    s2 = build_state(s, ["0.8.2"], "2026-10-01", "CHANGED")
    check("a withdrawn version drops out of first_seen",
          "0.8.0" not in s2["first_seen"])

    print("\ncommitted-state reality check (offline):")
    committed = load_state(STATE_PATH)
    check(f"the committed baseline exists at {STATE_PATH.name}",
          committed is not None)
    if committed:
        check("it watches the URL and key this file watches",
              committed.get("source_url") == VERSIONS_URL
              and committed.get("extension_key") == EXTENSION_KEY)
        check("its recorded threshold matches HNSW_SAFE_MIN_VERSION",
              committed.get("hnsw_safe_min_version")
              == ".".join(str(n) for n in HNSW_SAFE_MIN_VERSION))
        check("every recorded version parses (nothing junk got committed)",
              all(parse(v) for v in committed.get("versions", [])))
        # If this one ever fails, that is the good news, not a bug.
        check("the committed baseline is still BELOW the threshold "
              f"(highest: {(committed.get('versions') or ['-'])[-1]})",
              not unblocking_versions(committed.get("versions", []), parse))

    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED: " + "; ".join(FAILS))
        return 1
    print("ALL PASS")
    return 0


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------
def do_check(args) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body, transient, structural = fetch(args.url)

    shape_error = structural
    current: List[str] = []
    if body is not None:
        try:
            doc = json.loads(body)
        except Exception as e:                               # noqa: BLE001
            shape_error = f"response from {args.url} is not JSON: {e}"
        else:
            got, shape_error = extract_versions(doc)
            current = got or []

    seen = load_state(Path(args.state) if args.state else None)
    r = classify(seen, current, shape_error=shape_error, fetch_error=transient)

    print(f"🧩 pgvector packaging watch | {today} (UTC)")
    print(f"   {args.url}")
    print(f"   key '{EXTENSION_KEY}' · HNSW unblocks at "
          f">= {'.'.join(str(n) for n in HNSW_SAFE_MIN_VERSION)}")
    print("-" * 68)
    if r["verdict"] in ("SCHEMA_CHANGED", "FETCH_FAILED"):
        print(f"  ❌ {r['verdict']} — {r['reason']}")
    else:
        prev = (seen or {}).get("versions") or []
        print(f"  upstream now : {', '.join(current) or '(none)'}")
        print(f"  last seen    : {', '.join(prev) or '(no baseline)'}")
        if r["added"]:
            print(f"  ➕ added     : {', '.join(r['added'])}")
        if r["removed"]:
            print(f"  ➖ removed   : {', '.join(r['removed'])}")
        if r["unparseable"]:
            print(f"  ⚠️  unparseable keys: {', '.join(r['unparseable'])}")
        icon = "🎉" if r["verdict"] == "UNBLOCKED" else "·"
        print(f"  {icon} {r['verdict']} — {r['label']}")
        if r["verdict"] != "UNBLOCKED":
            print("     (HNSW 仍然封鎖：0.8.3 修索引損壞、0.8.4 修 "
                  "`hnsw graph not repaired`，兩者都關不掉 autovacuum。)")

    report = {"generated_at": today, "source_url": args.url,
              "extension_key": EXTENSION_KEY, **r}
    if args.changes_out:
        Path(args.changes_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📄 Report: {args.changes_out}")

    if args.state and r["persists_state"] and not args.no_state:
        state = build_state(seen, current, today, r["verdict"])
        if seen and seen.get("versions") == current and \
                seen.get("last_verdict") == r["verdict"]:
            # Nothing moved AND nothing about the verdict moved: leave the file
            # byte-identical so the weekly CI run produces no commit at all.
            print(f"🗂  State unchanged: {args.state}")
        else:
            write_state(Path(args.state), state)
            print(f"🗂  State written: {args.state} ({len(current)} version(s))")
    elif not r["persists_state"]:
        print("🗂  State NOT written — this run could not see the version list.")
    elif args.no_state:
        print("🗂  State NOT written — --no-state.")

    print(f"\nverdict={r['verdict']} speaks={r['speaks']} "
          f"issue={r['opens_issue']} exit={r['exit_code']}")
    return r["exit_code"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="offline assertions against fixtures, then exit")
    ap.add_argument("--prove-assertions", action="store_true",
                    help="replace the rules with no-ops; the tests must go red")
    ap.add_argument("--check", action="store_true",
                    help="fetch the manifest once and compare against the state file")
    ap.add_argument("--url", default=VERSIONS_URL)
    ap.add_argument("--state", default=str(STATE_PATH),
                    help="committed last-seen file (prior art: discovery_seen.json)")
    ap.add_argument("--no-state", action="store_true",
                    help="read the state file but never write it")
    ap.add_argument("--changes-out", default="",
                    help="write the machine-readable run report here")
    args = ap.parse_args()

    if args.prove_assertions:
        print("PROVE MODE — rules replaced with no-ops; failures are the point.\n")
        noop_parse = lambda _s: None                                     # noqa: E731
        noop_classify = lambda seen, current, shape_error=None, \
            fetch_error=None, parse=None: _verdict("UNCHANGED")          # noqa: E731
        run_self_test(noop_parse, noop_classify)
        expected = PROVE_MIN_FAILURES
        ok = len(FAILS) >= expected
        print(f"\n{'ALL PASS' if ok else 'BROKEN'} — {len(FAILS)} assertions fired "
              f"against the no-op rules (expected >= {expected}).")
        return 0 if ok else 1
    if args.self_test:
        return run_self_test(parse_version, classify)
    if args.check:
        return do_check(args)
    ap.error("nothing to do: pass --self-test / --prove-assertions / --check")


# The floor for --prove-assertions. Set from an observed run (24 on 2026-09-13),
# not guessed: if a future edit makes fewer assertions fire against the no-op
# rules, some assertion has stopped testing anything and the prove run goes red.
#
# The assertions that legitimately survive a no-op are the negative ones — "an rc
# does NOT unblock", "0.8.3 does NOT unblock", "a shape change IS reported" — plus
# the pure routing-table checks. A rule that always answers "no" trivially
# satisfies a test that expects "no". That is a known limit of prove-mode, which
# is exactly why the positive counterparts (0.8.4 DOES unblock, the fixture DOES
# yield 8 versions) are asserted alongside every one of them.
PROVE_MIN_FAILURES = 24


if __name__ == "__main__":
    raise SystemExit(main())
