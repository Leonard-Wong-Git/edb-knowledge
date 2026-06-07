#!/usr/bin/env python3
"""
ocr_extract.py — cloud-vision OCR a scanned (image-only) PDF into a vault
extract_<id>.txt for Channel B ingest (S147).
───────────────────────────────────────────────────────────────────────────────
Sibling of fetch_extract.py. Use this ONLY when fetch_extract.py reports
"extracted empty body" because the PDF has NO text layer (scanned images) — e.g.
mce_framework_2008 (8 image pages), g38 (CID-mojibake) family.

Per page: render to PNG via PyMuPDF (fitz) → send to an OpenAI vision model →
transcribe Traditional-Chinese text. Output is the SAME canonical vault format
fetch_extract.py writes, so dev/ingest_one_source.py picks it up unchanged and
each chunk stays page-resolvable via `=== Page N ===`.

⚠️ OCR output is DRAFT quality (transcription errors possible). Acceptable for
Channel B semantic search because every chunk carries the source url + page → the
user can always click back to the original PDF (traceability preserved, §A.2).
Do NOT use OCR text as an authoritative Channel A fact without human review.

Usage (from repo root; OPENAI_API_KEY auto-read from backend/.env):
  python3 dev/ocr_extract.py --id mce_framework_2008 \
      --title "《德育及公民教育課程架構》(2008)" --topic curriculum \
      --url "https://www.edb.gov.hk/attachment/tc/common/revised%20mce%20framework.pdf"
  python3 dev/ocr_extract.py ... --pages 1-1          # quality probe, 1 page
  python3 dev/ocr_extract.py ... --dpi 220 --model gpt-4o
"""
import argparse
import base64
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
UA = {"User-Agent": "Mozilla/5.0"}
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

OCR_SYSTEM = (
    "You are a precise OCR engine for scanned Traditional-Chinese (Hong Kong) "
    "education policy documents. Transcribe text exactly; never translate, "
    "summarise, explain, or add markdown."
)
OCR_USER = (
    "Transcribe ALL text on this scanned page, preserving the natural reading "
    "order and paragraph / line breaks. Use Traditional Chinese characters "
    "(香港繁體). Transcribe tables row by row, left to right. Keep section "
    "numbers, bullets and headings. Output ONLY the transcribed text — no "
    "commentary, no code fences. For a genuinely illegible region write 〔不清楚〕."
)


def load_api_key() -> str:
    import os
    k = os.environ.get("OPENAI_API_KEY", "")
    if not k and BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY=") and not line.startswith("#"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not k:
        sys.exit("ERROR: OPENAI_API_KEY missing (env or backend/.env)")
    return k


def fetch(url: str, timeout=90) -> bytes:
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.content


def ocr_page(api_key: str, png_b64: str, model: str) -> str:
    body = {
        "model": model,
        "temperature": 0,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": OCR_SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": OCR_USER},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{png_b64}",
                               "detail": "high"}},
            ]},
        ],
    }
    r = requests.post(OPENAI_URL,
                      headers={"Authorization": f"Bearer {api_key}",
                               "Content-Type": "application/json"},
                      json=body, timeout=180)
    if r.status_code != 200:
        sys.exit(f"OCR API FAIL {r.status_code}: {r.text[:400]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def main():
    import fitz
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--topic", default="curriculum")
    ap.add_argument("--fact-type", default="policy")
    ap.add_argument("--url", action="append", required=True, dest="urls")
    ap.add_argument("--pages", default=None, help="e.g. 1-1 (1-based, inclusive)")
    ap.add_argument("--dpi", type=int, default=220)
    ap.add_argument("--model", default="gpt-4o")
    args = ap.parse_args()

    lo = hi = None
    if args.pages:
        m = re.match(r"^(\d+)-(\d+)$", args.pages.strip())
        if not m:
            sys.exit(f"--pages must be 'a-b', got {args.pages!r}")
        lo, hi = int(m.group(1)), int(m.group(2))

    api_key = load_api_key()
    out, pageno, fffd, cjk = [], 0, 0, 0
    for url in args.urls:
        doc = fitz.open(stream=fetch(url), filetype="pdf")
        for i in range(doc.page_count):
            human = i + 1
            if lo is not None and not (lo <= human <= hi):
                continue
            pix = doc[i].get_pixmap(dpi=args.dpi)
            png_b64 = base64.b64encode(pix.tobytes("png")).decode()
            text = ocr_page(api_key, png_b64, args.model)
            text = re.sub(r"^```[a-z]*\n?|\n?```$", "", text).strip()  # strip stray fences
            if not text:
                print(f"  ⚠ page {human}: OCR returned empty", file=sys.stderr)
                continue
            pageno += 1
            fffd += text.count("�")
            cjk += sum(1 for c in text if "一" <= c <= "鿿")
            out.append(f"=== Page {pageno} ===\n{text}")
            print(f"  page {human} → {len(text)} chars, cjk={sum(1 for c in text if chr(0x4e00) <= c <= chr(0x9fff))}",
                  file=sys.stderr)
        doc.close()

    body = "\n\n".join(out).replace("\x00", "")
    if not body.strip():
        sys.exit(f"ERROR [{args.id}]: OCR produced empty body")

    header = (f"# source_id: {args.id}\n# title: {args.title}\n"
              f"# url: {args.urls[0]}\n# fact_type: {args.fact_type}\n"
              f"# topic_tags: {args.topic}\n\n")
    out_dir = VAULT_DIR / args.id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"extract_{args.id}.txt"
    out_path.write_text(header + body, encoding="utf-8")

    warn = "  ⚠ MOJIBAKE-SUSPECT" if fffd > max(5, cjk * 0.005) else ""
    print(f"[{args.id}] wrote {out_path.relative_to(REPO_ROOT)}  chars={len(body)}  "
          f"pages={pageno}  cjk={cjk}  U+FFFD={fffd}  model={args.model}{warn}")


if __name__ == "__main__":
    main()
