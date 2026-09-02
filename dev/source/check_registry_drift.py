#!/usr/bin/env python3
"""check_registry_drift.py — 登記、庫存、瀏覽清單三者對不上的地方（S212）

Open Priority ② asked for this monitor by name, and described one direction:
`source_registry` has more live sources than the front-end `GUIDELINES_REGISTRY`
lists, so documents that搜尋得到 cannot be browsed. Measuring it found the drift
runs in FOUR directions, and the raw count gap (273 vs 177 = 96) hid all of them
by netting them against each other:

  UNLISTED  serving + not retired, but absent from GUIDELINES_REGISTRY — the
            direction the priority described. 110 sources.
  PHANTOM   listed in GUIDELINES_REGISTRY but serving ZERO chunks — a user
            browses to a document the search cannot answer from. 42 entries.
            This direction was not known at all.
  UNMANAGED serving chunks under a source_id that source_registry has never
            heard of. 59 ids / 778 chunks. Freshness, expiry and title-parity
            monitoring all key off the registry, so these are outside every
            existing monitor.
  ZOMBIE    registry says deprecated / retired / held_back, store keeps serving.
            1 source, 108 chunks (kgecg_2017, deprecated S195 as a duplicate
            registration of g29 — the registry was updated, the store was not).

Why the three lists cannot simply be compared by count: they answer different
questions. The registry is what we have decided to track, the store is what a
user can be served, and GUIDELINES_REGISTRY is what a user can browse. Any two
of them disagreeing is a defect of a different kind, and a single number cannot
say which.

Usage:
  python3 dev/source/check_registry_drift.py --self-test
  python3 dev/source/check_registry_drift.py --check [--ledger PATH] [--cache PATH]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
APP = REPO_ROOT / "app.html"

RETIRED_STATES = {"deprecated", "retired", "held_back"}

# Serving ids that are mirrors or footnote labels rather than registered source
# documents. They are outside the registry BY DESIGN, so counting them as
# UNMANAGED would report an architecture as a defect (the S197 lesson: the store
# mirrors Channel A facts, and a check that forgets this reports itself wrong).
BY_DESIGN_KINDS = {"approved_fact", "stat_fact", "footnote_curated"}


# ---------------------------------------------------------------------------
# pure helpers
# ---------------------------------------------------------------------------


def registry_ids(sources: list[dict]) -> tuple[set[str], set[str]]:
    """(live ids, retired ids)."""
    live, dead = set(), set()
    for s in sources:
        sid = s.get("source_id") or s.get("id")
        if not sid:
            continue
        (dead if (s.get("status") or "").lower() in RETIRED_STATES else live).add(sid)
    return live, dead


def parse_guidelines_registry(app_html: str) -> list[dict]:
    """Pull GUIDELINES_REGISTRY out of app.html.

    It is inline JSX, not JSON, so this reads the ids with a regex rather than
    trying to parse JavaScript. Only `id` is needed; a bracket-matching parse
    plus a JS evaluator would be a second, drift-prone definition of the array.
    """
    i = app_html.find("GUIDELINES_REGISTRY")
    if i < 0:
        return []
    start = app_html.find("[", i)
    depth, j = 0, start
    while j < len(app_html):
        if app_html[j] == "[":
            depth += 1
        elif app_html[j] == "]":
            depth -= 1
            if depth == 0:
                break
        j += 1
    block = app_html[start:j + 1]
    return [{"id": m} for m in re.findall(r"\bid:\s*[\"']([^\"']+)[\"']", block)]


def series_parents(sources: list[dict]) -> dict[str, list[str]]:
    """{parent_source_id: [expected shard ids]} for entries modelled as a series.

    S212 — the first version of this file reported the 13 stat_enrolment_YYYY ids
    as UNMANAGED and stat_enrolment_report as PHANTOM, i.e. 14 separate defects.
    Reading the registry entry instead of assuming showed one deliberate design:
    `stat_enrolment_report` carries `url_primary_pattern` with a {YYYY} slot and
    `years_extracted: [2012..2024]`, and the store shards it one source_id per
    year. Nothing is missing; the parent and the shards are simply keyed
    differently, and no code reconciles them.

    That is still a defect — just a different one, and it belongs to the
    monitors, not the registry. check_freshness / check_expiry /
    check_source_titles all read `url_primary` and none of them reads
    `url_primary_pattern` or `years_extracted` (verified S212 by grep), so the
    parent has no URL for them to fetch and the shards have no registry row to
    key off. SERIES_UNMONITORED reports exactly that, instead of 14 rows that
    each name the wrong thing.
    """
    out: dict[str, list[str]] = {}
    for s in sources:
        sid = s.get("source_id") or s.get("id")
        years = s.get("years_extracted") or []
        pattern = s.get("url_primary_pattern")
        if not sid or not (years and pattern):
            continue
        stem = sid[:-len("_report")] if sid.endswith("_report") else sid
        out[sid] = [f"{stem}_{y}" for y in years]
    return out


def classify(serving: dict[str, int], serving_kinds: dict[str, str],
             live: set[str], dead: set[str], listed: set[str],
             series: dict[str, list[str]] | None = None) -> dict:
    """The five drift classes. Pure — takes counts, returns id lists."""
    series = series or {}
    shard_of = {shard: parent for parent, shards in series.items()
                for shard in shards}
    # A parent whose shards ARE serving is not a phantom, and its shards are not
    # unmanaged. Both are the same fact, so both are lifted out and reported once.
    sharded = sorted(p for p, shards in series.items()
                     if any(serving.get(sh, 0) for sh in shards))

    unlisted = sorted((sid for sid in serving
                       if sid in live and sid not in listed),
                      key=lambda s: -serving[s])
    phantom = sorted(sid for sid in listed
                     if serving.get(sid, 0) == 0 and sid not in sharded)
    unmanaged = sorted((sid for sid in serving
                        if sid not in live and sid not in dead
                        and sid not in shard_of
                        and serving_kinds.get(sid) not in BY_DESIGN_KINDS),
                       key=lambda s: -serving[s])
    zombie = sorted((sid for sid in serving if sid in dead),
                    key=lambda s: -serving[s])
    return {"UNLISTED": unlisted, "PHANTOM": phantom,
            "UNMANAGED": unmanaged, "ZOMBIE": zombie,
            "SERIES_UNMONITORED": sharded}


SEVERITY = {
    # The shards serve users but sit outside freshness / expiry / title-parity,
    # because those three read `url_primary` and this entry only has a pattern.
    "SERIES_UNMONITORED": "ERROR",
    # A retired source still answering users is the only one that is wrong on
    # its own terms: someone already decided it should stop, and it did not.
    "ZOMBIE": "ERROR",
    # Outside every registry-keyed monitor, so it silently ages.
    "UNMANAGED": "ERROR",
    # A browse entry the search cannot answer from.
    "PHANTOM": "WARN",
    # Needs a human curation decision per source, so it cannot be auto-fixed.
    "UNLISTED": "WARN",
}

LABEL = {
    "SERIES_UNMONITORED": "登記為年度系列，但三個 registry 監察都讀不到它的分年檔",
    "UNLISTED": "搜尋得到，但「📚EDB指引」瀏覽不到",
    "PHANTOM": "瀏覽清單有，但庫內零片段",
    "UNMANAGED": "庫內有片段，但 source_registry 從未登記",
    "ZOMBIE": "登記為已退役，但仍在服務片段",
}


def render_ledger(drift: dict, serving: dict[str, int],
                  titles: dict[str, str], generated_at: str) -> str:
    """Human triage list. UNLISTED is a decision queue, so it carries titles."""
    out = [f"# 登記／庫存／瀏覽清單 漂移帳（{generated_at}）", "",
           "由 `dev/source/check_registry_drift.py --check` 產生，請勿手改。", ""]
    for cls in ("ZOMBIE", "SERIES_UNMONITORED", "UNMANAGED", "PHANTOM", "UNLISTED"):
        ids = drift.get(cls, [])
        out.append(f"## {cls} — {LABEL[cls]}（{len(ids)}）")
        out.append("")
        if not ids:
            out.append("（無）")
            out.append("")
            continue
        out.append("| 片段 | source_id | 標題 |")
        out.append("|---:|---|---|")
        for sid in ids:
            t = (titles.get(sid) or "").replace("|", "｜")[:70]
            out.append(f"| {serving.get(sid, 0)} | `{sid}` | {t} |")
        out.append("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def self_test() -> int:
    fails = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    live, dead = registry_ids([
        {"source_id": "a", "status": "verified"},
        {"source_id": "b", "status": "deprecated"},
        {"source_id": "c", "status": "held_back"},
        {"source_id": "d"},
    ])
    check("live/retired split by status", live == {"a", "d"} and dead == {"b", "c"})

    html = ('x GUIDELINES_REGISTRY = [ {id: "sag_2025_11", title: "a"}, '
            "{id: 'g24', title: 'b'} ]; more")
    got = [g["id"] for g in parse_guidelines_registry(html)]
    check("GUIDELINES_REGISTRY ids parsed (both quote styles)",
          got == ["sag_2025_11", "g24"])
    check("absent GUIDELINES_REGISTRY yields empty, not a crash",
          parse_guidelines_registry("nothing here") == [])

    serving = {"a": 10, "b": 5, "z": 3, "m": 7, "fn": 2}
    kinds = {"a": "vault_extract", "b": "vault_extract", "z": "vault_extract",
             "m": "vault_extract", "fn": "footnote_curated"}
    d = classify(serving, kinds, live={"a", "b"}, dead={"z"}, listed={"a", "ghost"})
    sp = series_parents([
        {"source_id": "stat_enrolment_report", "years_extracted": [2012, 2013],
         "url_primary_pattern": "https://e/Enrol_{YYYY}.pdf"},
        {"source_id": "plain", "url_primary": "https://e/x.pdf"},
    ])
    check("series parent expands to its shard ids",
          sp == {"stat_enrolment_report": ["stat_enrolment_2012",
                                           "stat_enrolment_2013"]})
    check("an ordinary entry is not treated as a series", "plain" not in sp)

    ser_serving = {"stat_enrolment_2012": 55, "stat_enrolment_2013": 55, "orphan": 2}
    ser_kinds = {k: "vault_extract" for k in ser_serving}
    ds = classify(ser_serving, ser_kinds, live=set(), dead=set(),
                  listed={"stat_enrolment_report"}, series=sp)
    check("serving shards are NOT reported as unmanaged",
          ds["UNMANAGED"] == ["orphan"])
    check("a series parent with serving shards is NOT a phantom",
          ds["PHANTOM"] == [])
    check("the series is reported once, as its own class",
          ds["SERIES_UNMONITORED"] == ["stat_enrolment_report"])
    # THE GATE MUST STILL GO RED: a series whose shards serve nothing is a real
    # phantom, and must not be excused by being a series.
    dead_series = classify({"other": 1}, {"other": "vault_extract"}, {"other"},
                           set(), {"stat_enrolment_report"}, series=sp)
    check("a series with NO serving shards stays a phantom",
          dead_series["PHANTOM"] == ["stat_enrolment_report"]
          and dead_series["SERIES_UNMONITORED"] == [])

    check("UNLISTED = live + serving + not browsable", d["UNLISTED"] == ["b"])
    check("PHANTOM = browsable + zero chunks", d["PHANTOM"] == ["ghost"])
    check("ZOMBIE = retired + still serving", d["ZOMBIE"] == ["z"])
    check("UNMANAGED = serving + unknown to the registry", d["UNMANAGED"] == ["m"])
    check("a footnote label is NOT reported as unmanaged (by design)",
          "fn" not in d["UNMANAGED"])

    # THE GATE MUST GO RED: a clean corpus reports nothing, a dirty one reports.
    clean = classify({"a": 1}, {"a": "vault_extract"}, {"a"}, set(), {"a"})
    check("a consistent corpus produces four empty classes",
          all(not v for v in clean.values()))
    check("severity is assigned to every class",
          set(SEVERITY) == set(clean) == set(LABEL))

    led = render_ledger(d, serving, {"b": "測試標題"}, "2026-09-02")
    check("ledger names every class", all(c in led for c in d))
    check("ledger carries titles for the decision queue", "測試標題" in led)
    check("a pipe in a title cannot break the table row",
          "｜" in render_ledger({"ZOMBIE": ["z"], "UNMANAGED": [], "PHANTOM": [],
                                 "UNLISTED": [], "SERIES_UNMONITORED": []},
                                {"z": 1}, {"z": "a|b"}, "x"))

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--cache", default="", help="reuse a local chunk dump")
    ap.add_argument("--ledger", default=str(REPO_ROOT / "dev" / "source" /
                                            "registry_drift.md"))
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.check:
        ap.print_help()
        return 2

    import time
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from qc_report import fetch_chunks  # shared fetch — one definition, not two

    chunks = fetch_chunks(Path(args.cache) if args.cache else None)
    serving = collections.Counter(c["source_id"] for c in chunks)
    kinds: dict[str, str] = {}
    titles: dict[str, str] = {}
    for c in chunks:
        kinds.setdefault(c["source_id"], c.get("content_type") or "")
        titles.setdefault(c["source_id"], c.get("title") or "")

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) and "sources" in reg else reg
    for s in sources:
        sid = s.get("source_id") or s.get("id")
        if sid and s.get("title"):
            titles[sid] = s["title"]
    live, dead = registry_ids(sources)
    listed = {g["id"] for g in parse_guidelines_registry(
        APP.read_text(encoding="utf-8", errors="replace"))}

    drift = classify(dict(serving), kinds, live, dead, listed,
                     series_parents(sources))
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    Path(args.ledger).write_text(
        render_ledger(drift, dict(serving), titles, stamp), encoding="utf-8")

    print(f"registry live={len(live)} retired={len(dead)} · "
          f"GUIDELINES_REGISTRY={len(listed)} · serving ids={len(serving)}")
    for cls in ("ZOMBIE", "SERIES_UNMONITORED", "UNMANAGED", "PHANTOM", "UNLISTED"):
        ids = drift[cls]
        n = sum(serving.get(s, 0) for s in ids)
        print(f"  [{SEVERITY[cls]:<5}] {cls:<9} {len(ids):4d} 個來源 / {n:5d} 片段  "
              f"— {LABEL[cls]}")
    print(f"\nwrote {args.ledger}")
    # Only ZOMBIE exits non-zero: it is the one class that is unambiguously wrong
    # without a human deciding anything. The rest are triage queues, and a
    # monitor that exits 1 on a queue nobody can clear this week gets muted.
    return 1 if drift["ZOMBIE"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
