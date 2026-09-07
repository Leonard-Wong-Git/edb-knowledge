#!/usr/bin/env python3
"""_s213_recon.py — read-only reconnaissance for Open Priorities ②③⑦ (S213).

Answers three questions against the LIVE store, with an inspected instance
printed behind every number (communication pack rule 6: a count is not
evidence, the opened passage is).

  ③ eng_sss_guide_2021/g33 and arts_kla_guide_2017/g37 — are the g-series
    titles hung on the wrong document, and is the claimed 2007 / 2002 edition
    really absent from the store?
  ⑦ which chunks carry an internal source code as their title, and what is
    the correct title for each group?
  ② kgecg_2017 zombie — confirm the count that would be deleted.

Read-only. Writes nothing to Supabase.

Usage:
  python3 dev/_s213_recon.py [--cache PATH]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "source"))
from qc_report import fetch_chunks  # noqa: E402  (reuse the paged, guarded fetch)

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"

PAIRS = [("eng_sss_guide_2021", "g33"), ("arts_kla_guide_2017", "g37"),
         ("g24", "sag_2025_11"), ("kgecg_2017", "g29")]

# A title that is really an internal code: ASCII-only identifier shape, no CJK.
CODE_TITLE = re.compile(r"^[a-z0-9][a-z0-9_\-]*$", re.I)


def looks_like_code(title: str | None) -> bool:
    if not title:
        return False
    t = title.strip()
    return bool(CODE_TITLE.match(t)) and not re.search(r"[一-鿿]", t)


def show(label: str) -> None:
    print(f"\n{'=' * 72}\n{label}\n{'=' * 72}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=None)
    args = ap.parse_args()

    rows = fetch_chunks(args.cache)
    print(f"store rows: {len(rows)}")

    by_source: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_source[r.get("source_id") or "<none>"].append(r)

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    reg_by_id = {s["source_id"]: s for s in reg.get("sources", [])}

    # ---------------- ③ duplicate registrations ----------------
    show("③ duplicate registrations — are the titles hung on the wrong file?")
    for a, b in PAIRS:
        print(f"\n--- {a}  vs  {b} ---")
        for sid in (a, b):
            chunks = by_source.get(sid, [])
            titles = collections.Counter(c.get("title") for c in chunks)
            urls = collections.Counter(c.get("url") for c in chunks)
            r = reg_by_id.get(sid)
            print(f"  {sid}: store {len(chunks)} chunks | registry "
                  f"{'present status=' + str(r.get('status')) if r else 'ABSENT'}")
            for t, n in titles.most_common(3):
                print(f"      title  ({n:4}) {t!r}")
            for u, n in urls.most_common(2):
                print(f"      url    ({n:4}) {u}")
            if r:
                print(f"      reg title: {r.get('title')!r}")
                print(f"      reg url_primary: {r.get('url_primary')}")
        ta = {c.get("text", "") for c in by_source.get(a, [])}
        tb = {c.get("text", "") for c in by_source.get(b, [])}
        print(f"  verbatim-identical texts: {len(ta & tb)} "
              f"(a-only {len(ta - tb)}, b-only {len(tb - ta)})")

    # ---------------- ③b edition evidence ----------------
    show("③b which edition is actually in the store? (year strings in text)")
    for sid in ("eng_sss_guide_2021", "g33", "arts_kla_guide_2017", "g37"):
        chunks = by_source.get(sid, [])
        years = collections.Counter()
        for c in chunks:
            for y in re.findall(r"(?:19|20)\d{2}", c.get("text", "")):
                years[y] += 1
        print(f"  {sid}: top years {years.most_common(6)}")

    # ---------------- ⑦ code titles ----------------
    show("⑦ chunks whose title is an internal code")
    offenders = [r for r in rows if looks_like_code(r.get("title"))]
    print(f"total: {len(offenders)}")
    per = collections.Counter(r.get("source_id") for r in offenders)
    print(f"distinct source_id: {len(per)}")
    for sid, n in per.most_common(40):
        r = reg_by_id.get(sid)
        reg_title = r.get("title") if r else None
        sample = next(x for x in offenders if x.get("source_id") == sid)
        print(f"  {n:5}  {sid:34} title={sample.get('title')!r:36} "
              f"registry_title={reg_title!r}")

    # is the stored title always equal to the source_id?
    same = sum(1 for r in offenders if (r.get("title") or "").strip() == r.get("source_id"))
    print(f"\ntitle == source_id for {same}/{len(offenders)} offenders")

    # ---------------- ② zombie ----------------
    show("② kgecg_2017 zombie")
    z = by_source.get("kgecg_2017", [])
    r = reg_by_id.get("kgecg_2017")
    print(f"  store chunks: {len(z)}")
    print(f"  registry status: {r.get('status') if r else 'ABSENT'}")
    print(f"  registry notes: {str(r.get('notes'))[:300] if r else '-'}")
    if z:
        print(f"  sample id/hash: {z[0].get('id')} / {z[0].get('hash')}")
        print(f"  sample text[:160]: {z[0].get('text', '')[:160]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
