#!/usr/bin/env python3
"""
S183 incremental registry update：加 EDBCM 221/2025 source entry。
Piggyback this batch（separate source_id、唔屬 value education curriculum）。

--dry-run / --execute
"""
import json
import sys
from pathlib import Path

REG_PATH = Path(__file__).resolve().parent / "source" / "source_registry.json"
TODAY = "2026-06-25"

NEW_SOURCE = {
    "source_id": "edbcm_221_2025_smart_teaching",
    "title": "教育局通函第221/2025號 —— 「『智』啟學教」撥款計劃",
    "title_en": "EDB Circular Memorandum No. 221/2025 — Smart Teaching Funding Scheme (AI for Learning & Teaching)",
    "title_short": "通函221/2025 智啟學教",
    "url_landing": "https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM25221C.pdf",
    "url_primary": "https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM25221C.pdf",
    "source_type": "pdf",
    "authority": "edb",
    "spine": False,
    "topic_tags": ["it"],
    "access_mode": "public",
    "status": "verified",
    "version_label": "2025",
    "last_checked_at": TODAY,
    "supersedes": None,
    "related_source_ids": ["debp_blueprint", "debp_ailf_example"],
    "notes": "「『智』啟學教」撥款計劃：支援中小學善用人工智能提升學與教效能。教育局於 2025/1 成立「數字教育策略發展督導委員會」，2025 施政報告 QEF 預留 20 億元推進數字教育；本計劃成功申請學校獲一次過 50 萬元撥款，啟動及推動校本人工智能賦能教育（包括購置／訂閱／租用 AI 軟件／硬件／平台／資源、資助學生參加 AI 素養活動）。承諾要求：將「AI 賦能教育」項目納入學校發展計劃、最少 3 個科目／2 個級別推行 AI 輔助教學、發展 6 個 AI 教學例子、舉辦 3 次公開課／3 次經驗分享會／2 個學生活動。申請截止 2026/2/28、發款 2026/6/30、可跨學年用至 2027/28、財政紀錄保留 7 年。屬 digital_education route。",
}

# Anchor: insert after debp_ailf_example (most recent digital_education entry)
ANCHOR_ID = "debp_ailf_example"


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--execute"):
        sys.exit("Usage: --dry-run | --execute")
    mode = sys.argv[1]

    reg = json.load(open(REG_PATH, encoding="utf-8"))
    sources = reg["sources"]
    existing_ids = {s["source_id"] for s in sources}

    if NEW_SOURCE["source_id"] in existing_ids:
        sys.exit(f"❌ collision: {NEW_SOURCE['source_id']} already in registry")

    # Find anchor
    anchor_idx = None
    for i, s in enumerate(sources):
        if s["source_id"] == ANCHOR_ID:
            anchor_idx = i
            break
    if anchor_idx is None:
        print(f"⚠ anchor {ANCHOR_ID} not found; will append at end instead")
        anchor_idx = len(sources) - 1

    sources.insert(anchor_idx + 1, NEW_SOURCE)
    print(f"✓ Inserted {NEW_SOURCE['source_id']} after [{anchor_idx}] {ANCHOR_ID}")
    print(f"Total sources: {len(sources)} (was {len(sources) - 1})")

    if mode == "--dry-run":
        print("\n[DRY-RUN] No write.")
        return

    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\n✓ Wrote {REG_PATH}")


if __name__ == "__main__":
    main()
