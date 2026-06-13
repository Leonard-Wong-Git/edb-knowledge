#!/usr/bin/env python3
"""Mass-generate per-school-type policy + checklist docx for all tagged domains.
For each domain: regenerate the generic (all-types, bug-fixed) master + one school
version and one checklist per applicable Phase-1 type (primary/secondary/special,
per profile applies_to; kindergarten deferred to Phase 2).
"""
import json, os, subprocess, sys

WORK = os.path.dirname(os.path.abspath(__file__))
CHK = os.path.join(WORK, "..")
PROFILES = json.load(open(os.path.join(CHK, "_school_type_profiles.json"), encoding="utf-8"))
TAGS = json.load(open(os.path.join(CHK, "_school_type_tags.json"), encoding="utf-8"))
PHASE1 = ["primary", "secondary", "special"]
LABEL = {"primary": "小學", "secondary": "中學", "special": "特殊學校"}

prof = {p["domain"]: p for p in PROFILES}
domains = [t["domain"] for t in TAGS]  # the 13 tagged domains


def types_for(dom):
    ap = prof[dom]["applies_to"]
    return [t for t in PHASE1 if ap.get(t)]


def node(script, dom, ty=None):
    cmd = ["node", os.path.join(WORK, script), dom] + ([ty] if ty else [])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=WORK)
    if r.returncode != 0:
        print(f"   ERR {script} {dom} {ty or ''}: {r.stderr.strip()[:160]}")
        return False
    return True


def main():
    # 1. apply school_types into checklist/clauses
    r = subprocess.run(["python3", os.path.join(WORK, "apply_school_types.py"), "--apply"],
                       capture_output=True, text=True, cwd=WORK)
    print(r.stdout.strip().splitlines()[-1])
    if r.returncode != 0:
        print("apply failed; aborting"); sys.exit(1)

    total = 0
    for dom in domains:
        tys = types_for(dom)
        cn = json.load(open(os.path.join(WORK, dom, "checklist.json"), encoding="utf-8"))["cn"]
        variants = [None] + tys  # generic master + each type
        ok = 0
        for ty in variants:
            if node("gen_school_docx.js", dom, ty): ok += 1; total += 1
            if node("gen_checklist_docx.js", dom, ty): ok += 1; total += 1
        labels = "+".join(LABEL[t] for t in tys)
        print(f"  [{dom}] 《{cn}》 generic + ({labels}) -> {ok} docx")
    print(f"\nTOTAL generated: {total} docx across {len(domains)} domains")


if __name__ == "__main__":
    main()
