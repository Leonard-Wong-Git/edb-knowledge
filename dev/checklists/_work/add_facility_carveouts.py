#!/usr/bin/env python3
"""One-off: add facility/subject school-type carve-outs to the `safety` domain tag,
per Leonard's ruling (2026-06-13):
  家政/科技與生活、科學實驗室、工場/設計與科技 -> [secondary, special]  (小學不設此等特別室)
  視藝(一般) -> 共用(不動)；視藝(酸類/重金屬) -> [secondary] (已存在，不動)

Facility items/clauses are matched by keyword; GENERAL items that merely mention a
facility (universal obligations) are kept shared via KEEP_SHARED prefixes.
Locators are the shortest unique prefix (>=18 chars) of req/text.  Idempotent: skips
targets already carried by an existing carve-out.
"""
import json, os, sys

WORK = os.path.dirname(os.path.abspath(__file__))
TAGS = os.path.join(WORK, "..", "_school_type_tags.json")
KEY = "safety"
APPLIES = ["secondary", "special"]

FACILITY_KW = ["家政", "科技與生活", "實驗室", "理科教師", "本生燈", "預備室",
               "工場", "設計與科技", "設計及工藝", "危險化學品", "化學品貯物室",
               "煙櫥", "縫紉室", "美術室"]

# general obligations that merely reference a facility -> keep shared (prefix match)
KEEP_SHARED = [
    "學校須設立有效的安全管理系統",        # item 0.3 emergency plan + evacuation drill
    "所有學校均須安裝滅火筒",              # item 2.12 all-schools extinguishers
    "每間學校最少須有2名教師曾接受急救訓練",  # item 8.5 all-schools first-aiders
    "本校就意外事故維持完善的記錄制度",      # clause mixed: principal records ALL injuries
    "本校依據消防處處長要求及教育局指引",    # clause general fire-equipment config
    "本校須保持所有消防裝置或設備時刻在有效操作狀態",  # clause general fire devices
    "本校須保持所有課室及校舍之出口經常暢通無阻",      # clause mixed: exits + home-ec doors
    "本校於校內各氣體管道設施之供氣總掣位置",          # clause general gas mains shutoff
    "本校最少須有2名教師曾接受急救訓練",              # clause general first-aiders
]


def is_facility(t):
    return any(k in t for k in FACILITY_KW) and not any(t.startswith(p) for p in KEEP_SHARED)


def is_facility_clause(c):
    # a clause is facility-specific if its text OR its table carries a facility keyword,
    # unless its text is a known general/shared obligation (KEEP_SHARED)
    t = c.get("text", "")
    if any(t.startswith(p) for p in KEEP_SHARED):
        return False
    blob = t + json.dumps(c.get("table") or {}, ensure_ascii=False)
    return any(k in blob for k in FACILITY_KW)


def unique_locator(text, corpus, lo=18, hi=60):
    for n in range(lo, min(hi, len(text)) + 1):
        pref = text[:n]
        if sum(1 for c in corpus if pref in c) == 1:
            return pref
    return text[:hi]


def main():
    write = "--apply" in sys.argv
    tags = json.load(open(TAGS, encoding="utf-8"))
    raw = open(TAGS, encoding="utf-8").read()
    entry = next(t for t in tags if t["domain"] == KEY)

    chk = json.load(open(os.path.join(WORK, KEY, "checklist.json"), encoding="utf-8"))
    cls = json.load(open(os.path.join(WORK, KEY, "clauses.json"), encoding="utf-8"))
    items = [it for s in chk["sections"] for it in s["items"]]
    clauses = [c for ch in cls for c in ch.get("clauses", [])]
    item_reqs = [it["req"] for it in items]
    clause_txts = [c["text"] for c in clauses]

    # targets already carried by an existing carve-out (any subject) -> skip
    covered_items = {ex["locator"] for ex in entry["item_exceptions"]}
    covered_clauses = {ex["locator"] for ex in entry["clause_exceptions"]}

    new_items, new_clauses = [], []
    for it in items:
        if not is_facility(it["req"]):
            continue
        if any(loc in it["req"] for loc in covered_items):
            continue
        loc = unique_locator(it["req"], item_reqs)
        new_items.append({"locator": loc, "source_id": it["source_id"], "applies_to": APPLIES})
    for c in clauses:
        if not is_facility_clause(c):
            continue
        if any(loc in c["text"] for loc in covered_clauses):
            continue
        loc = unique_locator(c["text"], clause_txts)
        new_clauses.append({"locator": loc, "applies_to": APPLIES})

    print(f"safety facility carve-outs: +{len(new_items)} items, +{len(new_clauses)} clauses -> {APPLIES}")
    for x in new_items:
        print(f"   I «{x['locator'][:22]}…»")
    for x in new_clauses:
        print(f"   C «{x['locator'][:22]}…»")

    if write:
        entry["item_exceptions"].extend(new_items)
        entry["clause_exceptions"].extend(new_clauses)
        out = json.dumps(tags, indent=2, ensure_ascii=False)
        if raw.endswith("\n"):
            out += "\n"
        open(TAGS, "w", encoding="utf-8").write(out)
        print("WROTE _school_type_tags.json")
    else:
        print("(dry-run; pass --apply to write)")


if __name__ == "__main__":
    main()
