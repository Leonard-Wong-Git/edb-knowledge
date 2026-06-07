#!/usr/bin/env python3
"""
ocr_extract.py — cloud-vision OCR a scanned (image-only) OR CID-mojibake PDF into
a vault extract_<id>.txt for Channel B ingest (S147).
───────────────────────────────────────────────────────────────────────────────
Sibling of fetch_extract.py. Use this ONLY when fetch_extract.py reports
"extracted empty body" (scanned/image PDF, no text layer) OR the text layer is
CID/custom-font mojibake (cjk≈0, U+FFFD=0, glyphs map to control/ASCII — get_text
returns garbage). Rendering each page to an image and OCR-ing the image bypasses
both failure modes. Examples: mce_framework_2008 (8 image pages, S147),
g38 music_complete_guide_chi.pdf (153 pages, CID-mojibake, S147).

Per page: render to PNG via PyMuPDF (fitz) → OpenAI vision model → transcribe
Traditional-Chinese text. Output is the SAME canonical vault format
fetch_extract.py writes, so dev/ingest_one_source.py picks it up unchanged and
each chunk stays page-resolvable via `=== Page N ===`.

Rendering is single-threaded (fitz Document is not thread-safe); OCR (network
I/O) runs concurrently via --concurrency. 429 (TPM rate-limit) is honoured via
the Retry-After header / "try again in Xs" message (NOT a fixed short backoff —
a TPM window is ~60s); up to 6 retries. A page that still fails becomes a
`〔OCR失敗〕` placeholder rather than aborting the whole run; re-run with
--resume to re-OCR only the failed pages and merge (no re-spend on good pages).

⚠️ Low org TPM (e.g. 30k/min for gpt-4o) → keep --concurrency low (2-3). OCR
output is DRAFT quality; Channel B keeps traceability via chunk url + page.

Usage (from repo root; OPENAI_API_KEY auto-read from backend/.env):
  python3 dev/ocr_extract.py --id g38 --title "音樂課程指引(2003)" --topic curriculum \
      --url "https://.../music_complete_guide_chi.pdf" --dpi 175 --concurrency 3
  python3 dev/ocr_extract.py --id g38 ... --resume        # re-OCR only failed pages
  python3 dev/ocr_extract.py --id g38 ... --pages 1-4      # quality probe
"""
import argparse
import base64
import concurrent.futures
import re
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
UA = {"User-Agent": "Mozilla/5.0"}
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
FAIL_MARK = "〔OCR失敗〕"

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


def fetch(url: str, timeout=120) -> bytes:
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.content


def _retry_wait(resp, attempt: int) -> float:
    """Seconds to wait before retrying a 429/5xx — honour Retry-After / message."""
    ra = resp.headers.get("retry-after")
    if ra:
        try:
            return min(float(ra) + 1, 35)
        except ValueError:
            pass
    m = re.search(r"try again in ([\d.]+)s", resp.text)
    if m:
        return min(float(m.group(1)) + 1, 35)
    return min(8 * attempt, 35)  # exponential-ish fallback


def ocr_page(api_key: str, png_b64: str, model: str, retries: int = 6):
    """Return transcribed text, or None after exhausting retries."""
    body = {
        "model": model, "temperature": 0, "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": OCR_SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": OCR_USER},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{png_b64}", "detail": "high"}},
            ]},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(OPENAI_URL, headers=headers, json=body, timeout=180)
            if r.status_code == 200:
                txt = r.json()["choices"][0]["message"]["content"].strip()
                return re.sub(r"^```[a-z]*\n?|\n?```$", "", txt).strip()
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(_retry_wait(r, attempt))
                continue
            if attempt < retries:
                time.sleep(min(8 * attempt, 35))
                continue
            print(f"  ⚠ OCR HTTP {r.status_code}: {r.text[:120]}", file=sys.stderr)
            return None
        except Exception as e:
            if attempt < retries:
                time.sleep(min(8 * attempt, 35))
                continue
            print(f"  ⚠ OCR exception: {e}", file=sys.stderr)
            return None
    return None


def ocr_many(api_key, pages, model, concurrency):
    """pages = [(pageno, png_b64)] → {pageno: text|None}."""
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
        fut2pg = {ex.submit(ocr_page, api_key, b64, model): pg for pg, b64 in pages}
        done = 0
        for fut in concurrent.futures.as_completed(fut2pg):
            results[fut2pg[fut]] = fut.result()
            done += 1
            if done % 10 == 0 or done == len(pages):
                print(f"  OCR {done}/{len(pages)}", file=sys.stderr)
    return results


def render_range(urls, lo, hi, dpi):
    import fitz
    pages, pageno = [], 0
    for url in urls:
        doc = fitz.open(stream=fetch(url), filetype="pdf")
        for i in range(doc.page_count):
            if lo is not None and not (lo <= i + 1 <= hi):
                continue
            pageno += 1
            pages.append((pageno, base64.b64encode(doc[i].get_pixmap(dpi=dpi).tobytes("png")).decode()))
        doc.close()
    return pages


def render_specific(url, pagenos, dpi):
    import fitz
    doc = fitz.open(stream=fetch(url), filetype="pdf")
    out = []
    for pno in sorted(pagenos):
        if 0 <= pno - 1 < doc.page_count:
            out.append((pno, base64.b64encode(doc[pno - 1].get_pixmap(dpi=dpi).tobytes("png")).decode()))
    doc.close()
    return out


def parse_existing(out_path):
    t = out_path.read_text(encoding="utf-8")
    split = re.split(r"=== Page (\d+) ===\n", t)
    header = split[0]
    pages, order = {}, []
    for i in range(1, len(split), 2):
        pno = int(split[i])
        pages[pno] = split[i + 1].strip()
        order.append(pno)
    return header, pages, order


def write_vault(out_path, header, pages, order):
    body = "\n\n".join(f"=== Page {p} ===\n{pages[p]}" for p in order)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header.rstrip() + "\n\n" + body, encoding="utf-8")


def stats_of(pages, order):
    cjk = fffd = 0
    failed = []
    for p in order:
        t = pages[p]
        if FAIL_MARK in t:
            failed.append(p)
        cjk += sum(1 for c in t if "一" <= c <= "鿿")
        fffd += t.count("�")
    return cjk, fffd, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--topic", default="curriculum")
    ap.add_argument("--fact-type", default="policy")
    ap.add_argument("--url", action="append", required=True, dest="urls")
    ap.add_argument("--pages", default=None, help="e.g. 1-4 (1-based, inclusive)")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--resume", action="store_true", help="re-OCR only 〔OCR失敗〕 pages in existing extract")
    args = ap.parse_args()

    api_key = load_api_key()
    out_path = VAULT_DIR / args.id / f"extract_{args.id}.txt"

    if args.resume:
        if not out_path.exists():
            sys.exit(f"--resume: no existing {out_path}")
        if len(args.urls) != 1:
            sys.exit("--resume supports a single --url (single-PDF page numbering)")
        header, pages, order = parse_existing(out_path)
        failed = [p for p in order if FAIL_MARK in pages[p]]
        if not failed:
            print(f"[{args.id}] no failed pages — nothing to resume")
            return
        print(f"[{args.id}] resume: re-OCR {len(failed)} failed pages @ {args.dpi}dpi "
              f"(concurrency={args.concurrency})", file=sys.stderr)
        todo = render_specific(args.urls[0], set(failed), args.dpi)
        res = ocr_many(api_key, todo, args.model, args.concurrency)
        recovered = 0
        for pno, _ in todo:
            t = res.get(pno)
            if t and FAIL_MARK not in t:
                pages[pno] = t
                recovered += 1
        write_vault(out_path, header, pages, order)
        cjk, fffd, still = stats_of(pages, order)
        print(f"[{args.id}] resume DONE  recovered={recovered}/{len(failed)}  "
              f"still_failed={len(still)} {still if still else ''}  cjk={cjk}  U+FFFD={fffd}")
        return

    lo = hi = None
    if args.pages:
        m = re.match(r"^(\d+)-(\d+)$", args.pages.strip())
        if not m:
            sys.exit(f"--pages must be 'a-b', got {args.pages!r}")
        lo, hi = int(m.group(1)), int(m.group(2))

    print(f"[{args.id}] rendering @ {args.dpi}dpi ...", file=sys.stderr)
    rendered = render_range(args.urls, lo, hi, args.dpi)
    print(f"[{args.id}] {len(rendered)} pages → OCR (concurrency={args.concurrency}, model={args.model})",
          file=sys.stderr)
    res = ocr_many(api_key, rendered, args.model, args.concurrency)

    order = [pg for pg, _ in rendered]
    pages = {pg: (res.get(pg) or FAIL_MARK) for pg in order}
    cjk, fffd, failed = stats_of(pages, order)
    if cjk == 0:
        sys.exit(f"ERROR [{args.id}]: OCR produced no usable CJK text")

    header = (f"# source_id: {args.id}\n# title: {args.title}\n"
              f"# url: {args.urls[0]}\n# fact_type: {args.fact_type}\n"
              f"# topic_tags: {args.topic}\n")
    write_vault(out_path, header, pages, order)
    warn = "  ⚠ MOJIBAKE-SUSPECT" if fffd > max(5, cjk * 0.005) else ""
    failnote = f"  ⚠ {len(failed)} pages failed (run --resume): {failed}" if failed else ""
    print(f"[{args.id}] wrote {out_path.relative_to(REPO_ROOT)}  pages={len(order)}  "
          f"cjk={cjk}  U+FFFD={fffd}  model={args.model}{warn}{failnote}")


if __name__ == "__main__":
    main()
