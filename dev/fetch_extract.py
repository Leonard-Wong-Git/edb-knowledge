#!/usr/bin/env python3
"""
fetch_extract.py — produce a vault extract_<id>.txt for Channel B ingest (S146)
───────────────────────────────────────────────────────────────────────────────
Mojibake-safe extraction into the canonical vault format that
build_wiki_index.load_vault_sources() parses.

Output: dev/vault/<id>/extract_<id>.txt with a 5-line header then body.
  PDF mode  → per-page text via PyMuPDF (fitz), each page prefixed with
              `=== Page N ===` so build_wiki_index page-carry makes chunks
              page-resolvable. Continuous page numbering across multiple PDFs.
  HTML mode → main-text via bs4 (nav/script/style stripped), each URL as a
              `=== <section> ===` block (no page markers — like other HTML sources).

Usage:
  python3 dev/fetch_extract.py --id g36 --title "科學教育學習領域課程指引(2017)" \
      --topic curriculum --url "https://.../SEKLACG_CHI_2017.pdf"
  python3 dev/fetch_extract.py --id g09 --title "非華語中文指引(節錄)" --topic curriculum \
      --url "https://.../CLEKLAG_2017_for_upload_final_R77.pdf" --pages 43-48
  python3 dev/fetch_extract.py --mode html --id g14 --title "校本資優培育指引" \
      --topic curriculum --url "<chapter1>" --url "<chapter2>" ...
"""
import argparse
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url: str, timeout=90) -> bytes:
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.content


def extract_pdf(urls, pages_spec=None):
    import fitz
    lo = hi = None
    if pages_spec:
        m = re.match(r"^(\d+)-(\d+)$", pages_spec.strip())
        if not m:
            sys.exit(f"--pages must be 'a-b', got {pages_spec!r}")
        lo, hi = int(m.group(1)), int(m.group(2))
    out, pageno, fffd, cjk = [], 0, 0, 0
    for url in urls:
        doc = fitz.open(stream=fetch(url), filetype="pdf")
        for i in range(doc.page_count):
            human = i + 1
            if lo is not None and not (lo <= human <= hi):
                continue
            t = doc[i].get_text("text").strip()
            if not t:
                continue
            pageno += 1
            fffd += t.count("�")
            cjk += sum(1 for c in t if "一" <= c <= "鿿")
            out.append(f"=== Page {pageno} ===\n{t}")
        doc.close()
    return "\n\n".join(out), {"pages": pageno, "U+FFFD": fffd, "cjk": cjk, "src_docs": len(urls)}


def extract_html(urls):
    from bs4 import BeautifulSoup
    out, fffd, cjk = [], 0, 0
    for url in urls:
        soup = BeautifulSoup(fetch(url), "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "form", "noscript"]):
            tag.decompose()
        main = (soup.select_one("#content, .content, main, article, #main-content")
                or soup.body or soup)
        txt = re.sub(r"\n{3,}", "\n\n", main.get_text("\n").strip())
        txt = "\n".join(ln.strip() for ln in txt.splitlines() if ln.strip())
        fffd += txt.count("�")
        cjk += sum(1 for c in txt if "一" <= c <= "鿿")
        tail = url.rstrip("/").split("/")[-1].replace(".html", "")
        out.append(f"=== {tail} ===\n{txt}")
    return "\n\n".join(out), {"sections": len(urls), "U+FFFD": fffd, "cjk": cjk}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--topic", default="curriculum")
    ap.add_argument("--fact-type", default="policy")
    ap.add_argument("--mode", choices=["pdf", "html"], default="pdf")
    ap.add_argument("--url", action="append", required=True, dest="urls")
    ap.add_argument("--pages", default=None, help="PDF only, e.g. 43-48")
    args = ap.parse_args()

    if args.mode == "pdf":
        body, stats = extract_pdf(args.urls, args.pages)
    else:
        body, stats = extract_html(args.urls)

    if not body.strip():
        sys.exit(f"ERROR [{args.id}]: extracted empty body")

    header = (f"# source_id: {args.id}\n# title: {args.title}\n"
              f"# url: {args.urls[0]}\n# fact_type: {args.fact_type}\n"
              f"# topic_tags: {args.topic}\n\n")
    out_dir = VAULT_DIR / args.id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"extract_{args.id}.txt"
    out_path.write_text(header + body, encoding="utf-8")

    chars = len(body)
    warn = ""
    if stats.get("U+FFFD", 0) > max(5, stats.get("cjk", 0) * 0.005):
        warn = "  ⚠ MOJIBAKE-SUSPECT (U+FFFD high vs cjk) — review before ingest"
    print(f"[{args.id}] wrote {out_path.relative_to(REPO_ROOT)}  chars={chars}  {stats}{warn}")


if __name__ == "__main__":
    main()
