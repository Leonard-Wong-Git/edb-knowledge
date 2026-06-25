#!/usr/bin/env python3
"""
S183 registry update：
1. Add 2 new sources (values_edu_framework_2026 + edbc_3_2026_values_edu)
2. Mark 2 old sources (values_edu_framework_2021_trial + edbcm183_2023_values_edu)
   as superseded_by values_edu_framework_2026

--dry-run = print diff only, no write
--execute = write to source_registry.json
"""
import json
import sys
from pathlib import Path

REG_PATH = Path(__file__).resolve().parent / "source" / "source_registry.json"
TODAY = "2026-06-25"

NEW_SOURCES = [
    {
        "source_id": "values_edu_framework_2026",
        "title": "《價值觀教育課程架構》（2026）",
        "title_en": "Values Education Curriculum Framework (2026)",
        "title_short": "價值觀教育架構2026",
        "url_landing": "https://www.edb.gov.hk/tc/curriculum-development/4-key-tasks/moral-civic/ve_curriculum_framework2026.html",
        "url_primary": "https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/VE_CF_2026_.pdf",
        "source_type": "pdf",
        "authority": "edb",
        "spine": False,
        "topic_tags": ["curriculum"],
        "access_mode": "public",
        "status": "verified",
        "version_label": "2026",
        "last_checked_at": TODAY,
        "supersedes": ["values_edu_framework_2021_trial", "edbcm183_2023_values_edu"],
        "related_source_ids": ["moral_civic_curr", "edbc_3_2026_values_edu"],
        "notes": "《價值觀教育課程架構》(2026) 正式版，課程發展議會 2026/3 接納、2026/27 學年起在中小學正式推行；常委會以 2021 試行版為藍本、經各持份者意見及學校實踐經驗編訂。5 章節（價值觀教育的課程發展理念／架構的特色／學習期望／課程規劃與實施／資源與支援）；12 首要價值觀；總體方向「立根中華、聯通世界、擁抱未來」。Superseded 2021 試行版及 2023 EDBC 183（豐富試行版內容）。",
    },
    {
        "source_id": "edbc_3_2026_values_edu",
        "title": "教育局通告第3/2026號 —— 《價值觀教育課程架構》（2026）",
        "title_en": "EDB Circular No. 3/2026 — Values Education Curriculum Framework (2026)",
        "title_short": "EDBC 3/2026 價值觀教育",
        "url_landing": "https://www.edb.gov.hk/tc/curriculum-development/4-key-tasks/moral-civic/ve_curriculum_framework2026.html",
        "url_primary": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26003C.pdf",
        "source_type": "pdf",
        "authority": "edb",
        "spine": False,
        "topic_tags": ["curriculum"],
        "access_mode": "public",
        "status": "verified",
        "version_label": "2026",
        "last_checked_at": TODAY,
        "supersedes": None,
        "related_source_ids": ["values_edu_framework_2026", "moral_civic_curr"],
        "notes": "公布《價值觀教育課程架構》(2026) 嘅教育局通告；交官立、資助、按位津貼、私立及直接資助計劃學校校長／校監備辦。列出 2026 版主要更新及增潤內容（5 章節）。",
    },
]

SUPERSEDED_BY_MARK = {
    "values_edu_framework_2021_trial": "values_edu_framework_2026",
    "edbcm183_2023_values_edu": "values_edu_framework_2026",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--execute"):
        sys.exit("Usage: python3 dev/_s183_registry_update.py --dry-run | --execute")
    mode = sys.argv[1]

    with open(REG_PATH, encoding="utf-8") as f:
        reg = json.load(f)

    sources = reg["sources"]
    existing_ids = {s["source_id"] for s in sources}

    # Validate no collision for new entries
    for new in NEW_SOURCES:
        if new["source_id"] in existing_ids:
            sys.exit(f"❌ source_id collision: {new['source_id']} already in registry")

    # Find insertion point (after edbcm183_2023_values_edu)
    insert_after_idx = None
    for i, s in enumerate(sources):
        if s["source_id"] == "edbcm183_2023_values_edu":
            insert_after_idx = i
            break
    if insert_after_idx is None:
        sys.exit("❌ Cannot find edbcm183_2023_values_edu as insertion anchor")

    # Apply: insert new sources right after 2023 entry
    for offset, new in enumerate(NEW_SOURCES, start=1):
        sources.insert(insert_after_idx + offset, new)

    # Apply: mark superseded_by on 2021 + 2023
    superseded_count = 0
    for s in sources:
        if s["source_id"] in SUPERSEDED_BY_MARK:
            s["superseded_by"] = SUPERSEDED_BY_MARK[s["source_id"]]
            superseded_count += 1
            print(f"  ✓ {s['source_id']} → superseded_by={s['superseded_by']}")

    print(f"\nInserted {len(NEW_SOURCES)} new entries after index {insert_after_idx}")
    print(f"Marked {superseded_count} entries with superseded_by")
    print(f"Total sources: {len(sources)} (was {len(sources) - len(NEW_SOURCES)})")

    if mode == "--dry-run":
        print("\n[DRY-RUN] No write. Diff above.")
        return

    # Execute write
    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")  # trailing newline (existing file convention)
    print(f"\n✓ Wrote {REG_PATH}")


if __name__ == "__main__":
    main()
