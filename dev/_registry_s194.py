#!/usr/bin/env python3
"""
_registry_s194.py — one-off source_registry.json update for S194.
──────────────────────────────────────────────────────────────────
Three changes, dry-run by default (`--write` applies):

  1. NEW `iit_ai_framework_2026` — 《小學資訊與創新科技課程框架》「人工智能初探」
     範疇（試行版）, the framework body announced by EDBCM113/2026. Inserted next
     to that circular so the pair reads together.

  2. NEW `cgss_sss_2021` — 公民與社會發展科 課程及評估指引 (中四至中六) 2021.
     This is the document that was already in the vault and in Supabase, stored
     under the ICT entry: `CS_CAG` was read as Computer Science but means
     Citizenship and Social development.

  3. FIX `ict_sss_2021` — `url_primary` now points at the EDB-hosted ICT guide
     that matches the entry's own title. `freshness_metadata` is cleared because
     the recorded etag/hash/length describe the old (wrong) file; the weekly
     monitor re-seeds it on the next run (same re-seed pattern as S170).
     `ict_sss_2007_2015.superseded_by` is set per the S183 governance rule —
     only now is there a real 2021 ICT guide in the corpus to supersede it, so
     the matching backend `SUPERSEDED_IDS` entry is added in the same session.

The registry round-trips byte-stable at indent=2 with no trailing newline
(verified before writing), so the diff stays minimal.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"

TECH_DOC_LANDING = ("https://www.edb.gov.hk/tc/curriculum-development/kla/"
                    "technology-edu/curriculum-doc/index.html")

IIT_ENTRY = {
    "source_id": "iit_ai_framework_2026",
    "title": "《小學資訊與創新科技課程框架》—「人工智能初探」範疇（試行版）",
    "title_en": ("Primary Information and Innovation Technology Curriculum Framework — "
                 "Exploring Artificial Intelligence (Trial Version)"),
    "title_short": "人工智能初探範疇（試行版）",
    "url_landing": TECH_DOC_LANDING,
    "url_primary": ("https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/"
                    "technology-edu/curriculum-doc/IIT_Summary%20on%20AI_TC.pdf"),
    "source_type": "pdf",
    "authority": "edb",
    "spine": False,
    "topic_tags": ["curriculum", "it"],
    "access_mode": "public",
    "status": "verified",
    "version_label": "2026-trial",
    "last_checked_at": "2026-07-26",
    "supersedes": None,
    "parent_source_id": "tech_curr_docs",
    "related_source_ids": ["edbcm113_2026", "ct_programming_pri_2020",
                           "debp_ai_literacy_framework"],
    "notes": ("(S194) 《小學資訊與創新科技課程框架》「人工智能初探」範疇正文，由「檢視小學階段科技教育"
              "專責委員會」擬訂、課程發展議會「科技教育委員會」審閱；EDBCM113/2026 通函公布。"
              "通函本身只得 3 chunks（封面＋摘要），本檔才係實質內容（13 頁，text-layer 乾淨）。"
              "教師參考文件：學習階段一／二推展、與計算思維及編程的關係、以人為本科技向善六項要求。"),
}

CGSS_ENTRY = {
    "source_id": "cgss_sss_2021",
    "title": "公民與社會發展科 課程及評估指引 (中四至中六) 二零二一年 (由2021/22學年中四級開始適用)",
    "title_en": "Citizenship and Social Development Curriculum and Assessment Guide (Secondary 4-6) 2021",
    "title_short": "公民與社會發展科課程及評估指引2021",
    "url_landing": ("https://www.edb.gov.hk/tc/curriculum-development/kla/pshe/"
                    "curriculum-documents.html"),
    "url_primary": "https://cs.edb.edcity.hk/file/C_and_A_guide/202106/CS_CAG_S4-6_Chi_2021.pdf",
    "source_type": "pdf",
    "authority": "edb",
    "spine": False,
    "topic_tags": ["curriculum"],
    "access_mode": "public",
    "status": "verified",
    "version_label": "2021",
    "last_checked_at": "2026-07-26",
    "supersedes": None,
    "parent_source_id": None,
    "related_source_ids": [],
    "notes": ("(S194) 本 entry 修正一個長期 mislabel：呢份文件原本掛喺 `ict_sss_2021` 之下，"
              "標題寫《資訊及通訊科技 (中四至中六) 2021》——`CS_CAG` 被當成 Computer Science，"
              "實際係 Citizenship and Social development。封面（公民與社會發展科 課程及評估指引）"
              "＋目錄（「一國兩制」下的香港／改革開放以來的國家／互聯相依的當代世界／內地考察）核實。"
              "Supabase 原 81 chunks 由 S194 起改掛本 source_id，chunk 文字逐字不變"
              "（hash set 比對 81/81 相同）。vault 原文由 extract_ict_sss_2021_repaged.txt 搬過來。"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    original = REGISTRY.read_text(encoding="utf-8")
    reg = json.loads(original)
    sources: list[dict] = reg["sources"]
    by_id = {s["source_id"]: s for s in sources}

    for new_id in (IIT_ENTRY["source_id"], CGSS_ENTRY["source_id"]):
        if new_id in by_id:
            sys.exit(f"ERROR: {new_id} already in registry — refusing to duplicate")
    for need in ("ict_sss_2021", "ict_sss_2007_2015", "edbcm113_2026"):
        if need not in by_id:
            sys.exit(f"ERROR: expected existing entry {need} not found")

    changes: list[str] = []

    # 1 + 2 — insert the two new entries next to their relatives.
    def insert_after(anchor_id: str, entry: dict) -> None:
        idx = next(i for i, s in enumerate(sources) if s["source_id"] == anchor_id)
        sources.insert(idx + 1, entry)
        changes.append(f"+ {entry['source_id']} (inserted after {anchor_id})")

    insert_after("edbcm113_2026", IIT_ENTRY)
    insert_after("ict_sss_2021", CGSS_ENTRY)

    # 3 — repoint the ICT entry at the document its own title describes.
    ict = by_id["ict_sss_2021"]
    old_url = ict["url_primary"]
    ict["url_primary"] = ("https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/"
                          "technology-edu/curriculum-doc/ICT_C&A%20Guide_c_final.pdf")
    ict["last_checked_at"] = "2026-07-26"
    ict["freshness_metadata"] = None
    ict["notes"] = ("(S194) url_primary 由 edcity `CS_CAG_S4-6_Chi_2021.pdf` 更正為 EDB 官方 "
                    "`ICT_C&A Guide_c_final.pdf`（120 頁，封面「資訊及通訊科技 課程及評估指引 "
                    "(中四至中六) 二零二一年 由2022/23學年中四級開始適用」逐字對得上本 entry 標題）。"
                    "舊 URL 實際 serve 公民與社會發展科指引，已另立 `cgss_sss_2021`；原掛喺本 id 的 "
                    "81 條公社科 chunks 已遷去該 id，本 id 由 S194 起載真 ICT 2021 正文（116 chunks）。"
                    "freshness_metadata 清空待週跑監察重新 baseline（S170 re-seed 先例）。"
                    "高中資訊及通訊科技課程及評估指引（2021；2022/23 起實施）。")
    changes.append(f"~ ict_sss_2021.url_primary\n    - {old_url}\n    + {ict['url_primary']}")
    changes.append("~ ict_sss_2021.freshness_metadata → null (re-seed on next weekly run)")
    changes.append("~ ict_sss_2021.notes rewritten")

    old = by_id["ict_sss_2007_2015"]
    old["superseded_by"] = "ict_sss_2021"
    changes.append("~ ict_sss_2007_2015.superseded_by = ict_sss_2021 "
                   "(S183 rule: sync backend SUPERSEDED_IDS in the same session)")

    out = json.dumps(reg, ensure_ascii=False, indent=2)
    print(f"sources: {len(by_id)} → {len(sources)}")
    for c in changes:
        print(f"  {c}")

    if args.write:
        REGISTRY.write_text(out, encoding="utf-8")
        print(f"\nWROTE {REGISTRY.relative_to(REPO_ROOT)}")
    else:
        print("\n(dry-run — pass --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
