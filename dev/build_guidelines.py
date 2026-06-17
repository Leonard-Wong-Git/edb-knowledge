#!/usr/bin/env python3
"""Generate the public guidelines.json from app.html GUIDELINES_REGISTRY (the SSOT).

Why this exists (S140): the public `guidelines.json` endpoint (consumed by the EDB
Circular System) used to be a hand-maintained 39-entry curated subset that drifted
from the 148-entry in-app `GUIDELINES_REGISTRY`. This generator makes the registry
the single source of truth: it projects the public schema, maps the internal Chinese
`category` to the public topic id, and drops non-document entries by rule.

Drop rules (rule-based, NO hardcoded id list):
  1. sub_category == 'stat'      -> statistics data tables (XLSX / stat HTML / stat PDF)
  2. format == 'DOCX'            -> application forms, not guidelines
  3. url contains 'vertexaisearch' -> broken Google grounding-redirect URL (data bug)

Public schema (drops internal category / sub_category / isSpine):
  id, title, titleShort, url, year, format (+ level when present)
  format 'INDEX' is normalised to 'HTML' (INDEX is an ingestion hint = an HTML landing page).

Safety: default is --check (dry-run, no write). Pass --write to mutate guidelines.json.
The version is preserved from the existing file unless --version is given, so this
generator does NOT fight bump_version.py (which owns cross-artifact version lockstep).

Usage:
  python3 dev/build_guidelines.py --check                 # dry-run summary
  python3 dev/build_guidelines.py --write --version 2.3.0 --updated 2026-06-03
  python3 dev/build_guidelines.py --self-test             # offline assertions
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
APP = REPO / "app.html"
OUT = REPO / "guidelines.json"

CATEGORY_TO_TOPIC = {
    "財務採購": "finance",
    "人力資源": "hr",
    "課程": "curriculum",
    "活動": "activity",
    "學生事務": "student",
    "數字教育": "it",
    "行政": "general",
}
TOPIC_ORDER = ["finance", "hr", "curriculum", "activity", "student", "it", "general"]


def extract_registry(app_text):
    m = re.search(r"const GUIDELINES_REGISTRY = \[(.*?)\n\];", app_text, re.S)
    if not m:
        raise SystemExit("ERROR: GUIDELINES_REGISTRY array not found in app.html")
    rows = re.findall(r"\{[^{}]*\}", m.group(1))
    items = []
    for r in rows:
        def fstr(key):
            mm = re.search(r"%s:\s*'((?:[^'\\]|\\.)*)'" % key, r)
            return mm.group(1).replace("\\'", "'") if mm else None

        def fbool(key):
            mm = re.search(r"%s:\s*(true|false)" % key, r)
            return (mm.group(1) == "true") if mm else None

        items.append({
            "id": fstr("id"),
            "title": fstr("title"),
            "titleShort": fstr("titleShort"),
            "format": fstr("format"),
            "category": fstr("category"),
            "sub_category": fstr("sub_category"),
            "level": fstr("level"),
            "year": fstr("year"),
            "url": fstr("url"),
            "isSpine": fbool("isSpine"),
        })
    return items


def drop_reason(entry):
    """Return a non-document drop reason, or None to keep."""
    if entry["sub_category"] == "stat":
        return "stat-data"
    if entry["format"] == "DOCX":
        return "form"
    if "vertexaisearch" in (entry["url"] or ""):
        return "broken-url"
    return None


def public_format(fmt):
    return "HTML" if fmt == "INDEX" else fmt


def build(items, version, updated):
    buckets = {t: [] for t in TOPIC_ORDER}
    dropped = []
    for e in items:
        why = drop_reason(e)
        if why:
            dropped.append((e["id"], why))
            continue
        topic = CATEGORY_TO_TOPIC.get(e["category"])
        if topic is None:
            raise SystemExit(
                "ERROR: unmapped category %r for entry %s — add it to CATEGORY_TO_TOPIC"
                % (e["category"], e["id"])
            )
        rec = {
            "id": e["id"],
            "title": e["title"],
            "titleShort": e["titleShort"],
            "url": e["url"],
            "year": e["year"],
            "format": public_format(e["format"]),
        }
        if e["level"]:
            rec["level"] = e["level"]
        buckets[topic].append(rec)

    count = sum(len(v) for v in buckets.values())
    out = {
        "_meta": {
            "version": version,
            "updated": updated,
            "count": count,
            "description": (
                "EDB 指引文件連結庫 — app 內庫指引/通告全集（已剔統計數據表/申請表/壞連結），"
                "供 EDB 通告智能分析系統按通告主題提取參考文件連結。每項只含標題、簡稱、URL、年份、格式。"
            ),
        }
    }
    for t in TOPIC_ORDER:
        out[t] = buckets[t]
    return out, dropped


def ids_of(doc):
    out = set()
    for k, v in doc.items():
        if k == "_meta":
            continue
        for e in v:
            out.add(e["id"])
    return out


def verify(out, old_doc):
    """Assertions that must hold for a valid public contract. Raises on failure."""
    problems = []
    new_ids = ids_of(out)

    # 1. No previously-public entry may silently disappear (contract regression guard).
    if old_doc is not None:
        lost = ids_of(old_doc) - new_ids
        if lost:
            problems.append("previously-public ids dropped: %s" % sorted(lost))

    # 2. No excluded class leaked through.
    for topic in TOPIC_ORDER:
        for e in out[topic]:
            if e["format"] in ("XLSX", "DOCX", "INDEX"):
                problems.append("non-public format %s leaked: %s" % (e["format"], e["id"]))
            if "vertexaisearch" in e["url"]:
                problems.append("broken url leaked: %s" % e["id"])
            for req in ("id", "title", "titleShort", "url", "year", "format"):
                if not e.get(req):
                    problems.append("missing %s on %s" % (req, e["id"]))

    # 3. _meta.count matches actual.
    actual = sum(len(out[t]) for t in TOPIC_ORDER)
    if out["_meta"]["count"] != actual:
        problems.append("_meta.count %s != actual %s" % (out["_meta"]["count"], actual))

    if problems:
        raise SystemExit("VERIFY FAILED:\n  - " + "\n  - ".join(problems))


def summary(out, dropped, old_doc):
    print("guidelines.json build summary")
    print("  version:", out["_meta"]["version"], "| updated:", out["_meta"]["updated"])
    print("  public count:", out["_meta"]["count"])
    print("  per-topic:")
    for t in TOPIC_ORDER:
        print("    %-11s %3d" % (t, len(out[t])))
    by_reason = {}
    for _id, why in dropped:
        by_reason.setdefault(why, []).append(_id)
    print("  dropped (%d):" % len(dropped))
    for why, ids in sorted(by_reason.items()):
        print("    %-11s %2d  %s" % (why, len(ids), ", ".join(ids)))
    if old_doc is not None:
        old_ids = ids_of(old_doc)
        new_ids = ids_of(out)
        print("  vs existing: %d -> %d  (+%d new public, -0 lost)"
              % (len(old_ids), len(new_ids), len(new_ids - old_ids)))


def load_old():
    if OUT.exists():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def write_atomic(out):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, OUT)


def run_self_test():
    """Offline assertions on the live registry — no file writes."""
    items = extract_registry(APP.read_text(encoding="utf-8"))
    assert len(items) >= 140, "registry too small: %d" % len(items)
    out, dropped = build(items, "0.0.0-test", "1970-01-01")
    old = load_old()
    verify(out, old)
    # rule coverage
    stat = [i for i, w in dropped if w == "stat-data"]
    form = [i for i, w in dropped if w == "form"]
    broken = [i for i, w in dropped if w == "broken-url"]
    assert stat, "expected stat drops"
    assert form, "expected form drops"
    assert broken == ["religious_edu_jss"], "broken-url drop mismatch: %s" % broken
    assert "g10" in ids_of(out) and "g16" in ids_of(out) and "g28" in ids_of(out), \
        "g10/g16/g28 must stay public (real guidelines, not nav pages)"
    # category map total = kept + dropped
    assert sum(len(out[t]) for t in TOPIC_ORDER) + len(dropped) == len(items)
    print("SELF-TEST PASS: registry=%d, public=%d, dropped=%d (stat=%d form=%d broken=%d)"
          % (len(items), out["_meta"]["count"], len(dropped), len(stat), len(form), len(broken)))


def main():
    ap = argparse.ArgumentParser(description="Generate public guidelines.json from app.html registry")
    ap.add_argument("--write", action="store_true", help="write guidelines.json (default: dry-run)")
    ap.add_argument("--check", action="store_true", help="dry-run summary (default if neither flag)")
    ap.add_argument("--self-test", action="store_true", help="run offline assertions and exit")
    ap.add_argument("--version", help="_meta.version (default: preserve existing)")
    ap.add_argument("--updated", help="_meta.updated date (default: today UTC)")
    args = ap.parse_args()

    if args.self_test:
        run_self_test()
        return

    items = extract_registry(APP.read_text(encoding="utf-8"))
    old = load_old()
    version = args.version or (old or {}).get("_meta", {}).get("version") or "2.2.0"
    updated = args.updated or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    out, dropped = build(items, version, updated)
    verify(out, old)
    summary(out, dropped, old)

    if args.write:
        write_atomic(out)
        print("WROTE", OUT)
    else:
        print("(dry-run — pass --write to update guidelines.json)")


if __name__ == "__main__":
    main()
