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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry_series import (  # noqa: E402  — one definition, not two
    series_parents, monitorable_parents,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
APP = REPO_ROOT / "app.html"

RETIRED_STATES = {"deprecated", "retired", "held_back"}

# Serving ids that are mirrors or footnote labels rather than registered source
# documents. They are outside the registry BY DESIGN, so counting them as
# UNMANAGED would report an architecture as a defect (the S197 lesson: the store
# mirrors Channel A facts, and a check that forgets this reports itself wrong).
BY_DESIGN_KINDS = {"approved_fact", "stat_fact", "footnote_curated"}

# S250 — the backend's route allowlists. A query that trips a route is searched only
# inside that route's SOURCE_SET, so a source that is in the store but in NO set can
# never be returned for any routed query. Until S250 nothing checked this: 57 sources /
# 6,652 chunks (39% of the corpus, mostly senior-secondary C&A guides) had been ingested
# and never allowlisted, and title-style queries for 7 of 8 sampled returned none of them.
SEARCH_TS = REPO_ROOT / "backend" / "src" / "api" / "searchChannelB.ts"

# Serving, deliberately in no set: superseded by a newer edition that IS routed, or a
# duplicate of a routed source. Allowlisting them would put two editions of one guide in
# the same window. Each is a retirement candidate awaiting Leonard's decision — remove
# the entry here when the source is retired (or routed).
ROUTE_EXEMPT: dict[str, str] = {}  # S255 B2: g33 and g20 retired; add an entry only for a serving, deliberately unrouted source


# S252 (A8, Leonard approved 2026-11-17) — browse-library entries that are DELIBERATELY
# not ingested: each is an EDB index / topic page or a form, i.e. a door to documents,
# not a document. Users browse them and click through to EDB; there is nothing to
# search. Without this list PHANTOM counted them forever and buried the real gaps.
# Remove an entry when it is retired from GUIDELINES_REGISTRY or when it gets chunks.
BROWSE_ONLY = {
    "arts_curr_docs": "index page: 藝術教育學習領域課程文件",
    "cs_curr": "external resource site (EdCity 電腦科)",
    "curr_renewal_guides": "index page: 課程更新指引及文件總覽",
    "gs_pri_curr": "index page: 常識科（小學）課程文件",
    "ma_curr_index": "index page: 數學教育學習領域課程文件",
    "moral_civic_curr": "index page: 德育及公民教育課程文件",
    "pe_curr_docs": "index page: 體育學習領域課程文件",
    "pecg_2024_landing": "index page for pri_curr_guide_2024 (the guide itself is ingested)",
    "ph_pri_curr": "topic page: 小學人文科 (guide ingested as ph_pri_guide_2025)",
    "pri_science": "topic page: 小學科學科",
    "pshe_curr_docs": "index page: PSHE 課程文件 (KLA guide ingested as g35)",
    "sci_curr_docs": "index page: 科學教育學習領域課程文件",
    "sen_curr_area": "topic page: 特殊教育需要課程發展",
    "steam_edu": "topic page: STEAM 教育",
    "tech_curr_docs": "index page: 科技教育學習領域課程文件",
    "provident_fund": "topic page: 教職員公積金",
    "stat_edb_figures": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_enrolment_report": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_integrated_edu": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_kg": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_pri": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_sec": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "stat_special": "EDB statistics page; chunks retired S255 B3 (statistical sources are not searchable by design)",
    "g20": "link hub to the EDB 學校活動指引 page; its one chunk was retired S255 B2 (sch_activities_guide carries the documents)",
    "g08": "links to the Chinese-education documents & exemplars page, not the guide PDF",
    "g32": "links to the PSHE curriculum-documents page",
    "pri_science_cert_application_form": "DOCX application form",
}

# S252 (A8, Leonard approved 2026-11-17) — serving sources deliberately NOT in the
# browse library: one-off or annual circulars and programme calls, a report, a non-EDB
# document, a duplicate. They stay searchable. UNLISTED should only show the guides
# and standing circulars nobody has decided about yet.
_ONE_OFF = "one-off / annual circular or programme call"
UNLISTED_BY_DESIGN = {
    **{sid: _ONE_OFF for sid in (
        "edbcm060_2026", "edbcm186_2026", "edbcm156_2026", "edbcm_221_2025_smart_teaching",
        "edbcm089_2026", "edbcm066_2026", "edbcm080_2026", "edbcm136_2026", "edbcm073_2026",
        "edbcm134_2026", "edbcm070_2026", "edbcm107_2026", "edbcm076_2026", "edbcm116_2026",
        "edbcm144_2026", "edbcm081_2026", "edbcm094_2026", "edbcm096_2026", "edbcm198_2026",
        "edbcm088_2026", "edbcm095_2026", "edbcm108_2026", "edbcm124_2026", "edbcm167_2026",
        "edbcm170_2026_blnst", "edbcm203_2026", "edbcm138_2026", "edbcm152_2026",
        "edbcm197_2026", "edbcm113_2026", "edbcm135_2026", "edbcm141_2026", "edbcm142_2026",
        "edbcm155_2026", "edbcm_major_repairs_grant", "k1_admission_2627",
        "hsp_drug_testing_2026", "surplus_teacher_arr_2026")},
    "tdtf_report_2019": "task-force report, not a guideline",
    "edbcm83_2020_student_care": "pandemic-period circular",
    "pcpd_cloud_computing": "not an EDB document (Privacy Commissioner)",
    "debp_leaflet": "duplicate: the blueprint and its summary are listed",
}


def parse_source_set_ids(ts_text: str) -> set[str]:
    """Every source id named in any SOURCE_SETS array. Comments are stripped first
    (ids are often mentioned in the notes explaining why they were REMOVED)."""
    start = ts_text.find("const SOURCE_SETS")
    if start < 0:
        return set()
    end = ts_text.find("\n};", start)
    body = ts_text[start:end if end > 0 else len(ts_text)]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = "\n".join(line.split("//", 1)[0] for line in body.splitlines())
    return set(re.findall(r'"([^"\n]+)"', body))


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


# `series_parents()` lives in `registry_series.py` and is imported above.
#
# S212 — the first version of this file reported the 13 stat_enrolment_YYYY ids
# as UNMANAGED and stat_enrolment_report as PHANTOM, i.e. 14 separate defects.
# Reading the registry entry instead of assuming showed one deliberate design:
# `stat_enrolment_report` carries `url_primary_pattern` with a {YYYY} slot and
# `years_extracted: [2012..2024]`, and the store shards it one source_id per
# year. Nothing is missing; the parent and the shards are simply keyed
# differently, and no code reconciled them.
#
# S216 — the same expansion is now what check_freshness and check_source_titles
# monitor the series by, so the id derivation moved into `registry_series.py`
# rather than being copied a second and third time. This monitor keeps asking
# its own question (is the parent still unmonitored?) off the shared answer.


def classify(serving: dict[str, int], serving_kinds: dict[str, str],
             live: set[str], dead: set[str], listed: set[str],
             series: dict[str, list[str]] | None = None,
             series_monitored: set[str] | None = None,
             routed: set[str] | None = None,
             route_exempt: set[str] | None = None,
             browse_only: set[str] | None = None,
             unlisted_by_design: set[str] | None = None) -> dict:
    """The six drift classes. Pure — takes counts, returns id lists.

    `routed` is the union of the backend SOURCE_SETS; None (not supplied) means the
    UNROUTED class is not evaluated and comes back empty. `browse_only` /
    `unlisted_by_design` default to the module lists (S252), so every caller —
    this script and qc_report — applies the same decisions."""
    browse = set(BROWSE_ONLY) if browse_only is None else browse_only
    by_design = set(UNLISTED_BY_DESIGN) if unlisted_by_design is None else unlisted_by_design
    series = series or {}
    monitored = series_monitored or set()
    shard_of = {shard: parent for parent, shards in series.items()
                for shard in shards}
    # A parent whose shards ARE serving is not a phantom, and its shards are not
    # unmanaged. That is one fact about the STORE and it never stops being true.
    serving_series = sorted(p for p, shards in series.items()
                            if any(serving.get(sh, 0) for sh in shards))

    # Whether those shards are REACHED by the URL-keyed monitors is a second,
    # independent fact, and only that one is a defect.
    #
    # S222: these two used to be the same list, which was harmless while no
    # monitor could expand a series — but S216 taught all three to expand, and
    # an ERROR that cannot be cleared by fixing the thing it names is the
    # wallpaper this project keeps having to remove (紀律 #14). Splitting them
    # also keeps the S212 fix intact: the parent stays out of PHANTOM on the
    # strength of its serving shards, not on the strength of being broken.
    sharded = [p for p in serving_series if p not in monitored]

    unlisted = sorted((sid for sid in serving
                       if sid in live and sid not in listed and sid not in by_design),
                      key=lambda s: -serving[s])
    # `serving_series`, not `sharded`: a parent stays out of PHANTOM because its
    # shards serve, which stays true after the monitoring defect is fixed.
    phantom = sorted(sid for sid in listed
                     if serving.get(sid, 0) == 0 and sid not in serving_series
                     and sid not in browse)
    unmanaged = sorted((sid for sid in serving
                        if sid not in live and sid not in dead
                        and sid not in shard_of
                        and serving_kinds.get(sid) not in BY_DESIGN_KINDS),
                       key=lambda s: -serving[s])
    zombie = sorted((sid for sid in serving if sid in dead),
                    key=lambda s: -serving[s])
    # Statistical sources are filtered out of search by design (include_statistical
    # is never set by the site), so their absence from every set is not a defect.
    exempt = route_exempt or set()
    unrouted = [] if routed is None else sorted(
        (sid for sid in serving
         if sid in live and sid not in routed and sid not in exempt
         and not sid.startswith("stat_")
         and serving_kinds.get(sid) not in BY_DESIGN_KINDS),
        key=lambda s: -serving[s])
    return {"UNLISTED": unlisted, "PHANTOM": phantom,
            "UNMANAGED": unmanaged, "ZOMBIE": zombie,
            "SERIES_UNMONITORED": sharded, "UNROUTED": unrouted}


SEVERITY = {
    # The shards serve users but sit outside freshness / expiry / title-parity,
    # because those three read `url_primary` and this entry only has a pattern.
    "SERIES_UNMONITORED": "ERROR",
    # A retired source still answering users is the only one that is wrong on
    # its own terms: someone already decided it should stop, and it did not.
    "ZOMBIE": "ERROR",
    # Outside every registry-keyed monitor, so it silently ages.
    "UNMANAGED": "ERROR",
    # In the store, but no routed query can ever return it.
    "UNROUTED": "ERROR",
    # A browse entry the search cannot answer from.
    "PHANTOM": "WARN",
    # Needs a human curation decision per source, so it cannot be auto-fixed.
    "UNLISTED": "WARN",
}

LABEL = {
    "SERIES_UNMONITORED": "登記為年度系列，但三個 registry 監察都讀不到它的分年檔",
    "UNLISTED": "搜尋得到，但「📚EDB指引」瀏覽不到",
    "UNROUTED": "已入庫，但不在後端任何路由清單（SOURCE_SETS）內，問題一觸發路由就搜不到",
    "PHANTOM": "瀏覽清單有，但庫內零片段",
    "UNMANAGED": "庫內有片段，但 source_registry 從未登記",
    "ZOMBIE": "登記為已退役，但仍在服務片段",
}


def render_ledger(drift: dict, serving: dict[str, int],
                  titles: dict[str, str], generated_at: str) -> str:
    """Human triage list. UNLISTED is a decision queue, so it carries titles."""
    out = [f"# 登記／庫存／瀏覽清單 漂移帳（{generated_at}）", "",
           "由 `dev/source/check_registry_drift.py --check` 產生，請勿手改。", ""]
    for cls in ("ZOMBIE", "SERIES_UNMONITORED", "UNMANAGED", "UNROUTED", "PHANTOM", "UNLISTED"):
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
    # S222 — the class must clear when the defect is fixed, and only then.
    # Both directions are asserted because a check that cannot go green is as
    # useless as one that cannot go red: the first buries the real signal under
    # a permanent ERROR, the second never fires at all.
    ds_fixed = classify(ser_serving, ser_kinds, live=set(), dead=set(),
                        listed={"stat_enrolment_report"}, series=sp,
                        series_monitored={"stat_enrolment_report"})
    check("a series the monitors CAN now expand is no longer reported",
          ds_fixed["SERIES_UNMONITORED"] == [])
    check("…and clearing it does not push the parent back into PHANTOM",
          ds_fixed["PHANTOM"] == [])
    check("…nor does it orphan the shards into UNMANAGED",
          ds_fixed["UNMANAGED"] == ["orphan"])
    # And the live registry must actually reach the green state, or the fix is
    # only true in fixtures.
    check("the real registry's annual series is monitorable today",
          monitorable_parents(json.loads(REGISTRY.read_text(encoding="utf-8"))
                              ["sources"]) == {"stat_enrolment_report"})
    # THE GATE MUST STILL GO RED: a series whose shards serve nothing is a real
    # phantom, and must not be excused by being a series.
    # S255 B3: stat_enrolment_report is now in BROWSE_ONLY, so pass an explicit empty
    # browse_only — this fixture tests the series rule, not the real browse decisions.
    dead_series = classify({"other": 1}, {"other": "vault_extract"}, {"other"},
                           set(), {"stat_enrolment_report"}, series=sp, browse_only=set())
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
    # --- UNROUTED (S250) ---
    ts = ('const SOURCE_SETS: Record<string, string[]> = {\n  a: [\n    "in_set",\n'
          '    // "commented_out" was removed in S195\n    "x", /* "blocked" */\n  ],\n};\n'
          'const OTHER = ["not_a_set"];')
    ids = parse_source_set_ids(ts)
    check("SOURCE_SETS ids are read; commented-out and outside ids are not",
          ids == {"in_set", "x"})
    rk = {"in_set": "vault_extract", "lost": "vault_extract", "fn": "footnote_curated",
          "stat_pri": "vault_extract", "old": "vault_extract"}
    ru = classify({"in_set": 5, "lost": 9, "fn": 2, "stat_pri": 3, "old": 4}, rk,
                  {"in_set", "lost", "stat_pri", "old"}, set(),
                  {"in_set", "lost", "stat_pri", "old"},
                  routed=ids, route_exempt={"old"})["UNROUTED"]
    check("UNROUTED = serving + live + in no SOURCE_SET", ru == ["lost"])
    check("…footnote-only, statistical and exempt sources are not reported",
          not {"fn", "stat_pri", "old"} & set(ru))
    check("UNROUTED is empty when the route sets were not supplied",
          classify({"lost": 9}, rk, {"lost"}, set(), {"lost"})["UNROUTED"] == [])
    real = parse_source_set_ids(SEARCH_TS.read_text(encoding="utf-8"))
    check(f"the real searchChannelB.ts yields a plausible id set ({len(real)})",
          len(real) > 150 and "sag_2025_11" in real)
    check("no ROUTE_EXEMPT entry is also routed (exempt must mean 'in no set')",
          not set(ROUTE_EXEMPT) & real)

    # --- S252: browse-only / unlisted-by-design decisions ---
    bd = classify({"guide": 3, "circ": 2, "listed_doc": 4},
                  {"guide": "vault_extract", "circ": "vault_extract", "listed_doc": "vault_extract"},
                  {"guide", "circ", "listed_doc"}, set(), {"listed_doc", "index_pg", "gap"},
                  browse_only={"index_pg"}, unlisted_by_design={"circ"})
    check("a browse-only entry with zero chunks is not a PHANTOM; a real gap still is",
          bd["PHANTOM"] == ["gap"])
    check("an unlisted-by-design source is not UNLISTED; an undecided one still is",
          bd["UNLISTED"] == ["guide"])
    check("no id is both browse-only and unlisted-by-design",
          not set(BROWSE_ONLY) & set(UNLISTED_BY_DESIGN))
    check("every decision carries a reason",
          all(v.strip() for v in list(BROWSE_ONLY.values()) + list(UNLISTED_BY_DESIGN.values())))

    check("a consistent corpus produces four empty classes",
          all(not v for v in clean.values()))
    check("severity is assigned to every class",
          set(SEVERITY) == set(clean) == set(LABEL))

    led = render_ledger(d, serving, {"b": "測試標題"}, "2026-09-02")
    check("ledger names every class", all(c in led for c in d))
    check("ledger carries titles for the decision queue", "測試標題" in led)
    check("a pipe in a title cannot break the table row",
          "｜" in render_ledger({"ZOMBIE": ["z"], "UNMANAGED": [], "PHANTOM": [],
                                 "UNLISTED": [], "SERIES_UNMONITORED": [],
                                 "UNROUTED": []},
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

    # S257 — only the three columns read below; the full store with text is ~30 MB of
    # Supabase egress per run, this is ~1 MB. A --cache dump (full rows) still works.
    chunks = fetch_chunks(Path(args.cache) if args.cache else None,
                          cols="source_id,content_type,title")
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
                     series_parents(sources),
                     monitorable_parents(sources),
                     routed=parse_source_set_ids(SEARCH_TS.read_text(encoding="utf-8")),
                     route_exempt=set(ROUTE_EXEMPT))
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    Path(args.ledger).write_text(
        render_ledger(drift, dict(serving), titles, stamp), encoding="utf-8")

    print(f"registry live={len(live)} retired={len(dead)} · "
          f"GUIDELINES_REGISTRY={len(listed)} · serving ids={len(serving)}")
    for cls in ("ZOMBIE", "SERIES_UNMONITORED", "UNMANAGED", "UNROUTED", "PHANTOM", "UNLISTED"):
        ids = drift[cls]
        n = sum(serving.get(s, 0) for s in ids)
        print(f"  [{SEVERITY[cls]:<5}] {cls:<9} {len(ids):4d} 個來源 / {n:5d} 片段  "
              f"— {LABEL[cls]}")
    # S252 — a decision list that no longer matches reality must say so, or it
    # silently hides the very thing it was written about.
    stale = sorted(s for s in BROWSE_ONLY if serving.get(s, 0) or s not in listed)
    stale += sorted(s for s in UNLISTED_BY_DESIGN if s in listed or not serving.get(s, 0))
    if stale:
        print(f"  [WARN ] 決定名單過時 {len(stale)} 項（BROWSE_ONLY 有片段或已不在清單；"
              f"UNLISTED_BY_DESIGN 已列入清單或已無片段）：{', '.join(stale)}")
    print(f"\nwrote {args.ledger}")
    # Only ZOMBIE exits non-zero: it is the one class that is unambiguously wrong
    # without a human deciding anything. The rest are triage queues, and a
    # monitor that exits 1 on a queue nobody can clear this week gets muted.
    return 1 if drift["ZOMBIE"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
