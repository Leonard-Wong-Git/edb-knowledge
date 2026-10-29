#!/usr/bin/env python3
"""
_s241_ocr_ab.py — choose the replacement for gpt-4o in dev/ocr_extract.py (S241).

WHY. gpt-4o is shut down 2027-01-14. ocr_extract.py is the only path for scanned /
CID-mojibake EDB PDFs. A vision model that drops or alters characters would put wrong
policy text into the store, so the replacement is chosen by measurement, not by price.

HOW. Pages that HAVE a good text layer are rendered to PNG exactly as ocr_extract.py
does, OCR'd through ocr_extract.ocr_page (the production request, not a copy), and the
output is scored against the PDF's own text layer — an objective answer key. Score =
difflib ratio over CJK characters and digits only (layout, spacing and punctuation
differ legitimately between a text layer and a transcription; characters and numbers
are what a reader relies on). Digit-only score is reported separately because a wrong
number in a policy is the costliest error.

SPEND GATE (S214 convention): --approved-max-calls=N is mandatory; nothing is sent
without it, and the count is checked before the first call. --dry-run renders and
prints the answer key only (zero API calls).

USAGE (repo root)
  /usr/local/bin/python3 dev/_s241_ocr_ab.py --dry-run
  /usr/local/bin/python3 dev/_s241_ocr_ab.py --approved-max-calls=24
"""
import argparse
import difflib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ocr_extract as ox  # noqa: E402

# Text-layer pages (answer key = the PDF's own text). g18 has a table on its later pages.
PAGES = [
    ("g18", "https://www.edb.gov.hk/attachment/tc/student-parents/safety/sch-bus-services/2026_Guidelines_Schools_TC.pdf", [1, 2, 3, 4]),
    ("edbc002_2026", "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26002C.pdf", [1, 2, 3, 4]),
]
CONFIGS = [("gpt-4o", None), ("gpt-6-luna", "none"), ("gpt-6-luna", "low")]
DPI = 200  # ocr_extract.py default

_KEEP = re.compile(r"[一-鿿0-9]")


def keep(s, digits_only=False):
    return "".join(c for c in s if (c.isdigit() if digits_only else _KEEP.match(c)))


def score(ref, hyp, digits_only=False):
    a, b = keep(ref, digits_only), keep(hyp, digits_only)
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--approved-max-calls", type=int, default=0)
    args = ap.parse_args()

    import fitz
    jobs = []  # (source_id, page, png_b64, key_text)
    for sid, url, pages in PAGES:
        doc = fitz.open(stream=ox.fetch(url), filetype="pdf")
        for p in pages:
            pg = doc[p - 1]
            png = ox.base64.b64encode(pg.get_pixmap(dpi=DPI).tobytes("png")).decode()
            jobs.append((sid, p, png, pg.get_text()))
        doc.close()

    need = len(jobs) * len(CONFIGS)
    for sid, p, _, key in jobs:
        print(f"{sid} p{p}: key cjk+digits={len(keep(key))} digits={len(keep(key, True))}")
    if args.dry_run:
        print(f"dry run: would make {need} OCR calls")
        return
    if args.approved_max_calls < need:
        sys.exit(f"needs {need} calls; pass --approved-max-calls>={need} only after Leonard approves")

    # Capture usage of each production request without duplicating its body.
    last = {}
    real_post = requests.post

    def post(*a, **kw):
        r = real_post(*a, **kw)
        try:
            last["usage"] = r.json().get("usage")
        except Exception:
            last["usage"] = None
        return r
    ox.requests.post = post

    key = ox.load_api_key()
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "dpi": DPI,
           "approved_max_calls": args.approved_max_calls, "calls": 0, "rows": []}
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = Path(__file__).resolve().parent / "source" / "eval_runs" / f"{stamp}_s241_ocr_ab.json"
    if out_path.exists():
        sys.exit(f"{out_path} exists; preserve prior evidence")

    for model, effort in CONFIGS:
        for sid, p, png, ref in jobs:
            out["calls"] += 1
            last.clear()
            t0 = time.time()
            # retries=1: an approved call count must not be multiplied silently.
            txt = ox.ocr_page(key, png, model, 1, effort)
            row = {"model": model, "effort": effort, "source": sid, "page": p,
                   "seconds": round(time.time() - t0, 2), "usage": last.get("usage"),
                   "ok": txt is not None,
                   "score_chars": round(score(ref, txt or ""), 4),
                   "score_digits": round(score(ref, txt or "", True), 4),
                   "text": txt}
            out["rows"].append(row)
            out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"{model}/{effort} {sid} p{p}: chars={row['score_chars']} digits={row['score_digits']} "
                  f"{row['seconds']}s usage={row['usage'] and {k: row['usage'].get(k) for k in ('prompt_tokens', 'completion_tokens')}}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
