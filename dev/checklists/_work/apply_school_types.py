#!/usr/bin/env python3
"""Apply per-school-type carve-outs from _school_type_tags.json onto each domain's
_work/<key>/checklist.json (items) and clauses.json (clauses) by writing an optional
`school_types` array field.  Idempotent: clears any existing school_types first, then
sets from the tag file.  No field == shared (applies to all phase-1 types).

Locator matching: tag.locator must be a substring of the target item.req / clause.text
and must match EXACTLY ONE target (errors out otherwise).  For items, source_id (when
present in the tag) further disambiguates.

Formatting preserved per-file:
  checklist.json -> compact  json.dumps(ensure_ascii=False)
  clauses.json   -> indent=2 json.dumps(indent=2, ensure_ascii=False)

Usage:
  python3 apply_school_types.py --check            # dry-run all tagged domains, report
  python3 apply_school_types.py --apply            # write all tagged domains
  python3 apply_school_types.py --check safety sen  # subset
"""
import json, os, sys

WORK = os.path.dirname(os.path.abspath(__file__))
TAGS = os.path.join(WORK, "..", "_school_type_tags.json")
PHASE1 = {"primary", "secondary", "special"}


def load_raw(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def dump_like(path, data):
    if os.path.basename(path) == "checklist.json":
        return json.dumps(data, ensure_ascii=False)
    return json.dumps(data, indent=2, ensure_ascii=False)


def iter_items(checklist):
    for s in checklist.get("sections", []):
        for it in s.get("items", []):
            yield it


def iter_clauses(clauses):
    for ch in clauses:
        for cl in ch.get("clauses", []):
            yield cl


def clear(objs):
    for o in objs:
        o.pop("school_types", None)


def apply_domain(tag, write):
    key = tag["domain"]
    errors, sets = [], []
    chk_path = os.path.join(WORK, key, "checklist.json")
    cls_path = os.path.join(WORK, key, "clauses.json")
    if not (os.path.exists(chk_path) and os.path.exists(cls_path)):
        return [f"{key}: missing checklist.json or clauses.json"], []

    chk_raw, cls_raw = load_raw(chk_path), load_raw(cls_path)
    checklist, clauses = json.loads(chk_raw), json.loads(cls_raw)

    items = list(iter_items(checklist))
    clz = list(iter_clauses(clauses))
    clear(items)
    clear(clz)

    # item exceptions
    for ex in tag.get("item_exceptions", []):
        loc, sid = ex["locator"], ex.get("source_id")
        ap = sorted(set(ex["applies_to"]))
        if not set(ap) <= PHASE1:
            errors.append(f"{key} item[{loc[:14]}…]: applies_to {ap} not subset of {sorted(PHASE1)}")
            continue
        hits = [it for it in items if loc in it.get("req", "") and (not sid or it.get("source_id") == sid)]
        if len(hits) != 1:
            errors.append(f"{key} item[{loc[:14]}…] sid={sid}: matched {len(hits)} (need 1)")
            continue
        hits[0]["school_types"] = ap
        sets.append(f"item «{loc[:14]}…» -> {ap}")

    # clause exceptions
    for ex in tag.get("clause_exceptions", []):
        loc = ex["locator"]
        ap = sorted(set(ex["applies_to"]))
        if not set(ap) <= PHASE1:
            errors.append(f"{key} clause[{loc[:14]}…]: applies_to {ap} not subset of {sorted(PHASE1)}")
            continue
        hits = [cl for cl in clz if loc in cl.get("text", "")]
        if len(hits) != 1:
            errors.append(f"{key} clause[{loc[:14]}…]: matched {len(hits)} (need 1)")
            continue
        hits[0]["school_types"] = ap
        sets.append(f"clause «{loc[:14]}…» -> {ap}")

    if write and not errors:
        with open(chk_path, "w", encoding="utf-8") as f:
            f.write(dump_like(chk_path, checklist))
        with open(cls_path, "w", encoding="utf-8") as f:
            f.write(dump_like(cls_path, clauses))
    return errors, sets


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mode_apply = "--apply" in sys.argv
    if not (mode_apply or "--check" in sys.argv):
        print("specify --check or --apply"); sys.exit(2)

    tags = json.load(open(TAGS, encoding="utf-8"))
    if args:
        tags = [t for t in tags if t["domain"] in args]

    total_err, total_set = 0, 0
    for tag in tags:
        errors, sets = apply_domain(tag, mode_apply)
        flag = "WROTE" if (mode_apply and not errors) else ("ERR" if errors else "ok")
        print(f"[{flag}] {tag['domain']}: {len(sets)} carve-outs, {len(errors)} errors")
        for s in sets:
            print(f"      + {s}")
        for e in errors:
            print(f"      ! {e}")
        total_err += len(errors); total_set += len(sets)
    print(f"\nTOTAL: {total_set} carve-outs, {total_err} errors across {len(tags)} domains "
          f"({'APPLIED' if mode_apply else 'dry-run'})")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
