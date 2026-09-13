#!/usr/bin/env python3
"""
registry_series.py — one registry row that stands for a whole annual series.

The problem it solves (S212 measured it, S216 fixed it): `stat_enrolment_report`
does not describe a document. It describes thirteen of them. Instead of
`url_primary` it carries

    url_primary_pattern : ".../figures/Enrol_{YYYY}.pdf"
    years_extracted     : [2012 … 2024]

and the store shards it one `source_id` per year (`stat_enrolment_2012` …
`stat_enrolment_2024`, 528 chunks, confirmed by the `# source_id:` header of
every extract in `dev/vault/stat_enrolment_report/`).

Every registry-keyed monitor gated on `src.get("url_primary")`, so the parent had
no URL to fetch and the shards had no registry row to key off. Thirteen live PDFs
served to users sat outside freshness, outside title parity, and outside the
chunk arithmetic of the expiry sweep. `check_registry_drift.py` has been
reporting exactly that as `SERIES_UNMONITORED` (ERROR) since S212 — it is the
only monitor that ever read the two fields.

One definition, three readers. `series_parents()` moved here out of
`check_registry_drift.py` rather than being copied: the id derivation
(`stat_enrolment_report` + 2012 → `stat_enrolment_2012`) is the same rule the
drift monitor uses to decide a shard is not UNMANAGED, and two copies of it would
be two answers to "what does this row stand for".

Everything here is a pure function. No network, no file IO — a monitor's
`--self-test` can assert the expansion offline, which is the whole point of
lifting it out of the monitors.

Behaviour for an ordinary row is identity, deliberately: `monitor_rows(src)`
returns `[src]` — the same object, not a copy — so a caller that iterates
expanded rows instead of raw sources cannot change what happens to the 280 rows
that are not a series.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# The slot an annual pattern carries. Kept as a constant because the registry
# writes it literally and a self-test asserts every pattern contains it.
YEAR_SLOT = "{YYYY}"

# Private keys on a derived row. Underscore-prefixed so they can never collide
# with a registry field, and never written back — the parent row is.
SERIES_YEAR = "_series_year"
SERIES_PARENT = "_series_parent"

# Where per-year freshness baselines live on the PARENT row. One `content_hash`
# cannot describe thirteen PDFs, so the series gets a year-keyed store beside the
# scalar field the other 280 rows use. Absent = no baseline = the same
# seed-on-write-sync path a brand-new source takes.
FRESHNESS_YEARS = "freshness_metadata_years"


def series_years(src: Dict[str, Any]) -> List[int]:
    """The years this row stands for, or [] when it is an ordinary source.

    The gate is deliberately the same pair of fields `check_registry_drift`
    used — a pattern AND a year list. A row with only one of them is not a
    series; it is a malformed row, and reporting it as an ordinary source keeps
    it visible to the drift monitor instead of quietly inventing URLs for it.
    """
    years = src.get("years_extracted") or []
    pattern = src.get("url_primary_pattern")
    if not (years and pattern):
        return []
    return [int(y) for y in years]


def shard_id(parent_id: str, year: int) -> str:
    """`stat_enrolment_report` + 2012 → `stat_enrolment_2012`.

    Moved verbatim from `check_registry_drift.series_parents` (S212). The store
    keys the shards this way; the derivation is not a guess.
    """
    stem = parent_id[:-len("_report")] if parent_id.endswith("_report") else parent_id
    return f"{stem}_{year}"


def expand_url(pattern: str, year: int) -> str:
    """Fill the `{YYYY}` slot. A pattern with no slot comes back unchanged —
    which a self-test invariant catches as thirteen identical URLs rather than
    this function guessing where the year was meant to go."""
    return pattern.replace(YEAR_SLOT, str(year))


def shard_ids(src: Dict[str, Any]) -> List[str]:
    """Every per-year source_id this row stands for; [] for an ordinary row."""
    sid = src.get("source_id") or src.get("id")
    if not sid:
        return []
    return [shard_id(sid, y) for y in series_years(src)]


def is_monitorable(src: Dict[str, Any]) -> bool:
    """True when this series row actually expands into checkable URLs.

    The point of the class `check_registry_drift` reports is that the shards sit
    outside the URL-keyed monitors. Once the expansion works, that is no longer
    true, and a check that keeps firing anyway is a red light nobody can turn
    off — the wallpaper failure this project keeps having to fix (紀律 #14).
    So the drift monitor asks THIS, rather than assuming the answer.

    Ordinary rows are not a series and are never monitorable *as* one; callers
    ask this only about rows that `series_years` already claimed.
    """
    rows = monitor_rows(src)
    if not (rows and is_shard(rows[0])):
        return False
    return all((r.get("url_primary") or "").startswith("http") for r in rows)


def monitorable_parents(sources: List[Dict[str, Any]]) -> set:
    """The parent ids whose shards the URL-keyed monitors can now reach."""
    return {s.get("source_id") or s.get("id")
            for s in sources if series_years(s) and is_monitorable(s)}


def series_parents(sources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """{parent_source_id: [expected shard ids]} over a whole registry."""
    out: Dict[str, List[str]] = {}
    for s in sources:
        ids = shard_ids(s)
        if ids:
            out[s.get("source_id") or s["id"]] = ids
    return out


def monitor_rows(src: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The rows a URL-keyed monitor should actually see for this registry entry.

    Ordinary row  → `[src]`, the same object. Identity, so nothing changes.
    Series row    → one derived row per year, each a shallow copy carrying the
                    shard's `source_id`, the expanded `url_primary`, and that
                    year's freshness baseline lifted out of the parent's
                    year-keyed store.

    A derived row is never written back to the registry. It holds a reference to
    the parent so a writer (`record_freshness`) can put the result where it
    belongs.
    """
    years = series_years(src)
    if not years:
        return [src]
    pattern = src["url_primary_pattern"]
    by_year = src.get(FRESHNESS_YEARS) or {}
    rows: List[Dict[str, Any]] = []
    for year in years:
        row = dict(src)
        row["source_id"] = shard_id(src["source_id"], year)
        row["url_primary"] = expand_url(pattern, year)
        row["freshness_metadata"] = by_year.get(str(year))
        row[SERIES_YEAR] = year
        row[SERIES_PARENT] = src
        rows.append(row)
    return rows


def expand_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """`monitor_rows` flattened over a registry, order preserved."""
    out: List[Dict[str, Any]] = []
    for src in sources:
        out.extend(monitor_rows(src))
    return out


def is_shard(row: Dict[str, Any]) -> bool:
    return SERIES_PARENT in row


def parent_id(row: Dict[str, Any]) -> Optional[str]:
    """The registry source_id a row belongs to — itself, unless it is a shard."""
    parent = row.get(SERIES_PARENT)
    if parent is not None:
        return parent.get("source_id")
    return row.get("source_id")


def record_freshness(row: Dict[str, Any], today: str, meta: Dict[str, Any]) -> None:
    """Persist one row's freshness result onto the REGISTRY row it belongs to.

    Ordinary row → exactly the two assignments `check_freshness` always made.
    Shard        → the parent's `freshness_metadata_years[str(year)]`, because a
                   single scalar cannot hold thirteen content hashes and
                   overwriting it once per year would make every run report the
                   series as changed.
    """
    parent = row.get(SERIES_PARENT)
    if parent is None:
        row["last_checked_at"] = today
        row["freshness_metadata"] = meta
        return
    parent["last_checked_at"] = today
    store = parent.get(FRESHNESS_YEARS)
    if not isinstance(store, dict):
        store = {}
        parent[FRESHNESS_YEARS] = store
    store[str(row[SERIES_YEAR])] = meta
