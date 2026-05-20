#!/usr/bin/env python3
"""
repage_pdfs.py — CB-3 Option C (pilot): re-extract marker-less PDF vault
sources with explicit `=== Page N ===` separators so the page-carry chunker
(`build_wiki_index.chunk_text_with_page_carry`) can resolve a page for every
downstream chunk. Required because Channel-B north star = answer + guideline +
**page number**, and the existing `expand_vault.py` pipeline joins page text
without page markers.

Pilot scope (S119 follow-up, Leonard-approved): sag_2025_11, g06, g26
  - All 3 confirmed PDF source_type with reachable url_primary in
    source_registry.json (HTTP 200 HEAD probed before scripting).
  - HTML / xlsx sources are out of scope: structural ceiling (no #page=N).

Behaviour:
  - Default = dry-run. Downloads PDF in-memory, extracts page-by-page,
    counts markers, would-write report. NO disk write.
  - --write: backup old extract(s) to `dev/vault/<src>/_pre_repage_<ts>/`,
    then write consolidated `extract_<src>_repaged.txt` (header preserved
    from old, with `# repaged_at:` + `# repaged_pages:` + `# pipeline:`
    annotations appended).

Run from repo root:
  python3 dev/vault/repage_pdfs.py --only sag_2025_11,g06,g26            # dry-run
  python3 dev/vault/repage_pdfs.py --only sag_2025_11,g06,g26 --write    # mutate vault
"""
import argparse
import json
import re
import shutil
import ssl
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit, quote
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_DIR = REPO_ROOT / "dev" / "vault"
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"

PAGE_RE = re.compile(r"={2,}\s*Page\s*\d+\s*={2,}", re.IGNORECASE)
HEADER_RE = re.compile(r"^(# .+\n)+", re.MULTILINE)

# source_id -> list of legacy extract files to back up + remove
PILOT_LEGACY = {
    # S120 pilot (already done — kept for restartable / idempotent driver lookup)
    "sag_2025_11": [
        VAULT_DIR / "sag_2025_11" / "extract_sag_ch1_ch3_ch6_ch7.txt",
        VAULT_DIR / "sag_2025_11" / "extract_sag_ch2_ch4_ch5.txt",
    ],
    "g06": [VAULT_DIR / "g06" / "extract_g06.txt"],
    "g26": [VAULT_DIR / "g26" / "extract_g26.txt"],
    # S121 broader batch-1 (10 sources, size desc, cross-KLA, excludes g24/g29 dup-risk)
    "tech_kla_guide_2017": [VAULT_DIR / "tech_kla_guide_2017" / "extract_tech_kla_guide_2017.txt"],
    "eng_lit_guide_2023": [VAULT_DIR / "eng_lit_guide_2023" / "extract_eng_lit_guide_2023.txt"],
    "ls_jss_2010": [VAULT_DIR / "ls_jss_2010" / "extract_ls_jss_2010.txt"],
    "religious_edu_jss_2024": [VAULT_DIR / "religious_edu_jss_2024" / "extract_religious_edu_jss_2024.txt"],
    "geog_sss_2007_2022": [VAULT_DIR / "geog_sss_2007_2022" / "extract_geog_sss_2007_2022.txt"],
    "ces_jss_2024": [VAULT_DIR / "ces_jss_2024" / "extract_ces_jss_2024.txt"],
    "phys_sss_2007_2015": [VAULT_DIR / "phys_sss_2007_2015" / "extract_phys_sss_2007_2015.txt"],
    "chi_hist_sss_2007_2015": [VAULT_DIR / "chi_hist_sss_2007_2015" / "extract_chi_hist_sss_2007_2015.txt"],
    "chem_sss_2007_2018": [VAULT_DIR / "chem_sss_2007_2018" / "extract_chem_sss_2007_2018.txt"],
    "geog_jss": [VAULT_DIR / "geog_jss" / "extract_geog_jss.txt"],
}

# source_id -> consolidated output filename (single repaged extract per source)
PILOT_OUT = {
    "sag_2025_11": VAULT_DIR / "sag_2025_11" / "extract_sag_2025_11_repaged.txt",
    "g06": VAULT_DIR / "g06" / "extract_g06_repaged.txt",
    "g26": VAULT_DIR / "g26" / "extract_g26_repaged.txt",
    "tech_kla_guide_2017": VAULT_DIR / "tech_kla_guide_2017" / "extract_tech_kla_guide_2017_repaged.txt",
    "eng_lit_guide_2023": VAULT_DIR / "eng_lit_guide_2023" / "extract_eng_lit_guide_2023_repaged.txt",
    "ls_jss_2010": VAULT_DIR / "ls_jss_2010" / "extract_ls_jss_2010_repaged.txt",
    "religious_edu_jss_2024": VAULT_DIR / "religious_edu_jss_2024" / "extract_religious_edu_jss_2024_repaged.txt",
    "geog_sss_2007_2022": VAULT_DIR / "geog_sss_2007_2022" / "extract_geog_sss_2007_2022_repaged.txt",
    "ces_jss_2024": VAULT_DIR / "ces_jss_2024" / "extract_ces_jss_2024_repaged.txt",
    "phys_sss_2007_2015": VAULT_DIR / "phys_sss_2007_2015" / "extract_phys_sss_2007_2015_repaged.txt",
    "chi_hist_sss_2007_2015": VAULT_DIR / "chi_hist_sss_2007_2015" / "extract_chi_hist_sss_2007_2015_repaged.txt",
    "chem_sss_2007_2018": VAULT_DIR / "chem_sss_2007_2018" / "extract_chem_sss_2007_2018_repaged.txt",
    "geog_jss": VAULT_DIR / "geog_jss" / "extract_geog_jss_repaged.txt",
}


def fetch_pdf(url: str) -> bytes:
    """Fetch PDF via urllib; fall back to unverified SSL only if Mac
    Python.framework lacks the CA bundle (matches §D.7 known pattern).
    NB: EDB PDF filenames often contain literal spaces (e.g. "C&A Guide
    2022-chi.pdf"). urllib.request.Request rejects raw spaces as control
    chars, so quote() the path segment before constructing the request.
    safe="/%" preserves path separators and any existing percent-encoding
    that the registry may already carry."""
    sp = urlsplit(url)
    url = urlunsplit((sp.scheme, sp.netloc, quote(sp.path, safe="/%"),
                      sp.query, sp.fragment))
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 repage_pdfs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except (ssl.SSLError, urllib.error.URLError) as e:
        # Mac py.framework SSL CA fallback. Acceptable for read-only public PDF
        # fetch from EDB (no creds in flight, content integrity not safety-critical
        # since we'll measure chunk counts + spot-check downstream).
        print(f"    (ssl fallback after: {e})", file=sys.stderr)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
            return r.read()


def get_source_url(sid: str) -> str:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    src_list = reg.get("sources", reg) if isinstance(reg, dict) else reg
    for s in (src_list if isinstance(src_list, list) else []):
        if (s.get("id") or s.get("source_id")) == sid:
            return s.get("url_primary") or s.get("url") or ""
    return ""


def load_existing_header(path: Path) -> str:
    if not path or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    m = HEADER_RE.match(text)
    return m.group(0) if m else ""


def extract_paged(pdf_bytes: bytes) -> tuple[str, int]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise SystemExit("PyMuPDF missing. pip3 install pymupdf --break-system-packages")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    n = doc.page_count
    parts = []
    for i, page in enumerate(doc, start=1):
        parts.append(f"=== Page {i} ===")
        parts.append(page.get_text("text").rstrip())
    body = "\n".join(parts)
    doc.close()
    return body, n


def process_source(sid: str, write: bool, ts: str) -> dict:
    if sid not in PILOT_LEGACY:
        return {"sid": sid, "status": "skip", "reason": "not in pilot set"}

    url = get_source_url(sid)
    if not url:
        return {"sid": sid, "status": "fail", "reason": "no url_primary in registry"}

    print(f"\n[{sid}] url_primary = {url}", flush=True)
    print(f"  ↓ fetching ...", flush=True)
    try:
        data = fetch_pdf(url)
    except Exception as e:
        return {"sid": sid, "status": "fail", "reason": f"fetch: {e}"}
    print(f"  ✓ downloaded {len(data) / 1e6:.2f} MB")

    try:
        body, n_pages = extract_paged(data)
    except Exception as e:
        return {"sid": sid, "status": "fail", "reason": f"extract: {e}"}

    markers = len(PAGE_RE.findall(body))
    print(f"  ✓ extracted {n_pages} pages, {len(body):,} chars, "
          f"{markers} markers (expect {n_pages})")

    legacy = [p for p in PILOT_LEGACY[sid] if p.exists()]
    legacy_bytes = sum(p.stat().st_size for p in legacy)
    legacy_chars = 0
    legacy_markers = 0
    for p in legacy:
        ptxt = p.read_text(encoding="utf-8")
        legacy_chars += len(ptxt)
        legacy_markers += len(PAGE_RE.findall(ptxt))
    print(f"  legacy: {len(legacy)} file(s), {legacy_chars:,} chars "
          f"({legacy_bytes:,} bytes UTF-8), {legacy_markers} markers")

    header = load_existing_header(legacy[0]) if legacy else f"# source_id: {sid}\n"
    annot = (f"# repaged_at: {ts}\n"
             f"# repaged_pages: {n_pages}\n"
             f"# pipeline: repage_pdfs.py (PyMuPDF page-by-page + === Page N === markers)\n")
    sep = "# " + "=" * 60 + "\n"
    full = header + annot + sep + "\n" + body + "\n"

    out = PILOT_OUT[sid]

    if not write:
        print(f"  DRY-RUN: would backup {len(legacy)} legacy → "
              f"{legacy[0].parent.name}/_pre_repage_{ts}/" if legacy else
              "  DRY-RUN: no legacy to back up")
        print(f"  DRY-RUN: would write → {out.relative_to(REPO_ROOT)} "
              f"({len(full):,} chars, {markers} markers)")
        return {"sid": sid, "status": "dry-run-ok",
                "pages": n_pages, "markers": markers,
                "chars": len(full), "legacy_files": len(legacy),
                "legacy_chars": legacy_chars}

    # Write path. NB: backup dir MUST live outside dev/vault/ tree because
    # build_wiki_index.load_vault_sources() uses VAULT_DIR.rglob("*.txt") which
    # would otherwise load the backups as ghost vault entries (collides with
    # active source_id). Use §5.a-compliant dev/init_backup/<ts>/ location.
    if legacy:
        bdir = REPO_ROOT / "dev" / "init_backup" / ts / "cb3c_pilot_legacy" / sid
        bdir.mkdir(parents=True, exist_ok=True)
        for f in legacy:
            shutil.copy2(f, bdir / f.name)
            f.unlink()
            print(f"  ⇒ backed up + removed {f.relative_to(REPO_ROOT)}")
        print(f"  ⇒ backup dir: {bdir.relative_to(REPO_ROOT)}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(full, encoding="utf-8")
    print(f"  ✓ wrote {out.relative_to(REPO_ROOT)} ({len(full):,} chars)")
    return {"sid": sid, "status": "written",
            "pages": n_pages, "markers": markers,
            "chars": len(full), "legacy_files": len(legacy),
            "legacy_chars": legacy_chars}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="sag_2025_11,g06,g26",
                    help="comma-separated source_ids (pilot subset)")
    ap.add_argument("--write", action="store_true",
                    help="actually mutate vault extracts (default = dry-run)")
    args = ap.parse_args()

    ids = [s.strip() for s in args.only.split(",") if s.strip()]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    mode = "WRITE" if args.write else "DRY-RUN"
    print("=" * 74)
    print(f"repage_pdfs.py — {mode} — sources: {ids}")
    print("=" * 74)

    results = []
    for sid in ids:
        results.append(process_source(sid, args.write, ts))

    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    for r in results:
        if r["status"] in ("written", "dry-run-ok"):
            print(f"  {r['sid']:<18} {r['status']:<12} "
                  f"pages={r['pages']:>4} markers={r['markers']:>4} "
                  f"new_chars={r['chars']:>10,} "
                  f"legacy={r['legacy_files']}f/{r['legacy_chars']:>8,}c")
        else:
            print(f"  {r['sid']:<18} {r['status']:<12} {r.get('reason','')}")
    ok = sum(1 for r in results if r["status"] in ("written", "dry-run-ok"))
    print(f"\n{ok}/{len(results)} ok ({mode}).")


if __name__ == "__main__":
    main()
