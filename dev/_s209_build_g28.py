#!/usr/bin/env python3
"""
S209 — build the vault extract for `g28` 學校資訊保安建議措施 from its landing hub.

Why this exists: `g28` has been in the registry as `verified` since the seed
import and has **0 chunks** in Supabase. It was registered and never ingested,
so a search for school information security finds nothing — the closest hit for
「學校使用雲端服務指引」 was a senior-secondary ICT curriculum document.

The hub carries 41 documents, all live (probed 2026-08-24, zero 404s). Only 8
are ingested here. The other 33 are 31 seminar decks from 2018–2020 events — the
one-off-occasion class the S209 lifecycle work is about. They would not answer
a question about what a school should do today; they would only dilute
retrieval, so they are deliberately left out rather than ingested and expired.

Shape follows S207's g17: ONE source, one extract, a `=== <label> ===` marker
per document, and `section_urls` in the registry so every chunk cites the exact
PDF it came from instead of the hub page.

⚠️ One thing g17 got wrong and this does not: the page counter must RESTART at
each document. g17's three single-page attachments were numbered Page 1, 2, 3
by a counter that ran across the whole extract, so two chunks serve `#page=2`
and `#page=3` on one-page PDFs and the UI shows 「頁 2 ↗」 / 「頁 3 ↗」. Here N is
the page number *within its own PDF*, which is what `#page=N` means to a reader.

Usage (from repo root):
  python3 dev/_s209_build_g28.py --dry-run     # download + report, write nothing
  python3 dev/_s209_build_g28.py --write       # write dev/vault/g28/extract_g28.txt

Then, to ingest:
  python3 dev/vault/expand_vault.py --embed --force --sources g28
(which HEAD-verifies every section URL first and fails closed).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault" / "g28"
CACHE = REPO_ROOT / "dev" / "vault" / "g28" / "_pdf"
UA = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")}

BASE = ("https://www.edb.gov.hk/attachment/tc/edu-system/primary-secondary/"
        "applicable-to-primary-secondary/it-in-edu")

# label → (url, human title). The label becomes the section marker AND the
# `section_urls` key, so it must stay stable: changing it re-hashes every chunk.
DOCS = [
    ("edbcm084_2022", f"{BASE}/CM/2022/EDBCM22084C.pdf",
     "教育局通函第84/2022號"),
    ("edbcm071_2019", f"{BASE}/CM/EDBCM19071C-BuildaSecureCyberspace2019.pdf",
     "教育局通函第71/2019號 — 全城起動 快樂上網"),
    ("edbcm164_2018", f"{BASE}/CM/EDBCM18164C-CyberSecurityCampaign-SmartDevicesSecurity.pdf",
     "教育局通函第164/2018號 — 智能裝置保安"),
    ("edbcm101_2018", f"{BASE}/CM/EDBCM1012018C-BuildSecureCyberSpace.pdf",
     "教育局通函第101/2018號 — 建立安全網絡空間"),
    ("edbcm092_2018", f"{BASE}/CM/EDBCM2018092C-Antibotnet.pdf",
     "教育局通函第92/2018號 — 殭屍網絡"),
    ("zoom_desktop_hkpf", f"{BASE}/Information-Security/ZoomDataSecurityIncidents/ZOOM-Desktop-suggestion.pdf",
     "「Zoom」應用程式保安設定及使用建議（桌面版）— 香港警務處"),
    ("zoom_mobile_hkpf", f"{BASE}/Information-Security/ZoomDataSecurityIncidents/ZOOM-Mobile-suggestion.pdf",
     "「Zoom」應用程式保安設定及使用建議（流動裝置版）— 香港警務處"),
]

HEADER = """# source_id: g28
# title: 學校資訊保安建議措施
# url: https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/information-security.html
# fact_type: policy
# topic_tags: it
"""

# Left out on purpose, not overlooked:
#   學校網絡安全小貼士  <BASE>/CyberSecurityInSchoolsSmartTips.pdf
# One A4 page that is a single 2480x3508 JPEG — pdffonts reports no fonts at all,
# so there is no text layer and pdftotext yields 0 characters. It is a poster;
# reading it needs OCR (see the cloud-OCR options already in the backlog).
# Ingesting it blank would be worse than leaving it out: the source would look
# covered while answering nothing.

MIN_DOC_CHARS = 200          # a real document; a download error would fall short


def fetch(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    try:
        r = requests.get(url, headers=UA, timeout=90, allow_redirects=True)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            print(f"    ❌ HTTP {r.status_code} / not a PDF ({r.content[:8]!r})")
            return False
        dest.write_bytes(r.content)
        return True
    except Exception as e:                                   # noqa: BLE001
        print(f"    ❌ {e}")
        return False


def pages_of(pdf: Path) -> list:
    """Text per page, in order. Empty pages are kept so page numbers stay true."""
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return []
    # pdftotext separates pages with a form feed; the trailing split is the tail
    # after the last page break, not a page of its own.
    parts = out.stdout.split("\f")
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return parts


def build(write: bool) -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    body = []
    section_urls = {}
    failures = 0
    total_pages = 0

    for label, url, title in DOCS:
        print(f"\n=== {label}  ({title})")
        pdf = CACHE / f"{label}.pdf"
        if not fetch(url, pdf):
            failures += 1
            continue
        pages = pages_of(pdf)
        text_len = sum(len(p.strip()) for p in pages)
        print(f"    {len(pages)} page(s), {text_len} chars")
        if text_len < MIN_DOC_CHARS:
            print("    ❌ too little text — image-only PDF? refusing to ingest a blank")
            failures += 1
            continue
        body.append(f"=== {label} ===")
        for n, page in enumerate(pages, 1):        # ← restarts per document
            body.append(f"=== Page {n} ===")
            body.append(page.strip())
        section_urls[label] = url
        total_pages += len(pages)

    print(f"\n{'─'*60}")
    print(f"{len(section_urls)}/{len(DOCS)} documents, {total_pages} pages total, "
          f"{failures} failure(s)")
    if failures:
        print("❌ refusing to write a partial extract — fix the failures first")
        return 1

    text = HEADER + "\n" + "\n".join(body) + "\n"
    print(f"extract: {len(text)} chars")
    print("\nsection_urls to put in the registry:")
    for label, url in section_urls.items():
        print(f'    "{label}": "{url}"')

    if not write:
        print("\n[dry-run] nothing written. Re-run with --write.")
        return 0

    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    dest = VAULT_DIR / "extract_g28.txt"
    dest.write_text(text, encoding="utf-8")
    print(f"\n✅ wrote {dest.relative_to(REPO_ROOT)}")

    import json
    reg_path = REPO_ROOT / "dev" / "source" / "source_registry.json"
    doc = json.loads(reg_path.read_text(encoding="utf-8"))
    row = next(s for s in doc["sources"] if s["source_id"] == "g28")
    row["section_urls"] = section_urls
    row["refetch_blocked"] = ("multi-document hub extract built by dev/_s209_build_g28.py — "
                              "the generic single-page extract_html_text would replace all 8 "
                              "documents with the landing page and kill every section_urls "
                              "deep link (S209)")
    row["lifecycle"] = "reference"
    row["expires_on"] = None
    row["expiry_basis"] = "standing information-security guidance — never swept"
    row["covers_period"] = None
    row["notes"] = (row.get("notes") or "") + (
        " | S209(2026-08-24): ingested 7 of the 41 documents on the hub — 5 EDBCM circulars "
        "(84/2022, 71/2019, 164/2018, 101/2018, 92/2018) and the two HKPF Zoom advisories. "
        "學校網絡安全小貼士 is image-only (one 2480x3508 JPEG, no text layer) and needs OCR — left "
        "out rather than ingested blank. The other 33 are 31 seminar decks from 2018–2020 "
        "events (one-off occasions) plus 2 third-party cybersecurity.hk leaflets, and are "
        "deliberately NOT ingested: they would dilute retrieval without answering what a school "
        "should do today. All 41 probed live, zero 404s. Page numbers restart per document so "
        "#page=N means the page of THAT pdf (the bug g17 has). ⚠️ do not --fetch.")
    reg_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print("✅ registry updated (section_urls + refetch_blocked + lifecycle + notes)")
    print("\nNext:  python3 dev/vault/expand_vault.py --embed --force --sources g28")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args()
    return build(write=args.write)


if __name__ == "__main__":
    sys.exit(main())
