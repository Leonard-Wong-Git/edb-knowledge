#!/usr/bin/env python3
"""
_extract_s183.py — S183 一次性 extract script
─────────────────────────────────────────────
抽 VE_CF_2026.pdf + EDBC_3_2026.pdf 入 canonical vault structure：
  dev/vault/values_edu_framework_2026/extract_values_edu_framework_2026.txt
  dev/vault/edbc_3_2026_values_edu/extract_edbc_3_2026_values_edu.txt

格式：跟 cgss_2024 / 其他 vault source 嘅 extract_*.txt 模板
  # source_id: ...
  # title: ...
  # url: ...
  # fact_type: policy
  # topic_tags: curriculum
  (blank line)
  === Page 1 ===
  <text>
  === Page 2 ===
  ...

Usage: python3 dev/vault/value_education_2026/_extract_s183.py
"""
import fitz
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # dev/vault/value_education_2026/
VAULT_DIR = SCRIPT_DIR.parent                          # dev/vault/

SOURCES = [
    {
        "pdf": SCRIPT_DIR / "VE_CF_2026.pdf",
        "source_id": "values_edu_framework_2026",
        "title": "《價值觀教育課程架構》（2026）",
        "url": "https://www.edb.gov.hk/attachment/tc/curriculum-development/4-key-tasks/moral-civic/VE_CF_2026_.pdf",
        "fact_type": "policy",
        "topic_tags": "curriculum",
        "skip_pages_start": 3,   # page 1-3 cover / 排版空白
        "skip_pages_end": 1,     # last page 空白 / page number only
    },
    {
        "pdf": SCRIPT_DIR / "EDBC_3_2026.pdf",
        "source_id": "edbc_3_2026_values_edu",
        "title": "教育局通告第3/2026號 —— 《價值觀教育課程架構》（2026）",
        "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26003C.pdf",
        "fact_type": "policy",
        "topic_tags": "curriculum",
        "skip_pages_start": 0,
        "skip_pages_end": 0,
    },
    {
        "pdf": SCRIPT_DIR / "EDBCM_221_2025.pdf",
        "source_id": "edbcm_221_2025_smart_teaching",
        "title": "教育局通函第221/2025號 —— 「『智』啟學教」撥款計劃（支援中小學善用人工智能提升學與教效能）",
        "url": "https://applications.edb.gov.hk/circular/upload/EDBCM/EDBCM25221C.pdf",
        "fact_type": "policy",
        "topic_tags": "it",
        "skip_pages_start": 0,
        "skip_pages_end": 0,
    },
]


def extract_pdf_to_text(src: dict) -> tuple[str, int, int]:
    """抽 PDF → (text with page markers, total_pages, chars)"""
    doc = fitz.open(str(src["pdf"]))
    total = len(doc)
    start = src["skip_pages_start"]
    end = total - src["skip_pages_end"]
    parts = []
    for p_idx in range(start, end):
        page_num = p_idx + 1  # 1-indexed for display
        text = doc[p_idx].get_text().strip()
        if not text:
            continue  # skip blank pages
        parts.append(f"=== Page {page_num} ===\n{text}")
    doc.close()
    body = "\n\n".join(parts)
    return body, total, len(body)


def write_extract(src: dict, body: str):
    sid = src["source_id"]
    out_dir = VAULT_DIR / sid
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"extract_{sid}.txt"
    header = (
        f"# source_id: {sid}\n"
        f"# title: {src['title']}\n"
        f"# url: {src['url']}\n"
        f"# fact_type: {src['fact_type']}\n"
        f"# topic_tags: {src['topic_tags']}\n"
        f"\n"
    )
    out_path.write_text(header + body, encoding="utf-8")
    return out_path


def main():
    for src in SOURCES:
        if not src["pdf"].exists():
            print(f"⚠ Missing PDF: {src['pdf']}")
            continue
        body, total, chars = extract_pdf_to_text(src)
        out_path = write_extract(src, body)
        skip_info = f"(skipped first {src['skip_pages_start']} + last {src['skip_pages_end']} pages)"
        print(f"✓ {src['source_id']}: {chars:,} chars from {total} pages {skip_info} → {out_path.relative_to(VAULT_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
