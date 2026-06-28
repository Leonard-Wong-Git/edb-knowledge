#!/usr/bin/env python3
"""
prepare_ingest_package.py  —  Option A, Phase 1 (S188)
======================================================
The ingest-PACKAGE GENERATOR for the automated-ingest pipeline.

Given EDB circular candidate(s) surfaced by the 4th monitor
(check_new_circulars.py / circular.wongfu.net feed), this scripts the *manual*
verbatim-ingest pipeline that S186 ran by hand into one reproducible step, and
emits a reviewable "ingest package" per candidate:

    download PDF -> text-layer probe -> PyMuPDF verbatim extract (canonical
    header + `=== Page N ===`) -> dry-run chunk (count + page-resolvable) ->
    dupe-check vs registry -> PROPOSE source_id / topic / route / Tier ->
    attach dashboard signals (urgency / compliance / deadlines / grant_info /
    k1_topics / channel_b_facts gap) -> write package.json + INDEX.md row.

SAFETY / SCOPE (Phase 1 is intentionally inert):
  - STAGING ONLY. Writes solely under dev/source/ingest_packages/<source_id>/.
    Never touches dev/vault/, Supabase, git, the registry, or any live surface.
  - NO ingest, NO embed, NO INSERT, NO deploy. Those belong to a later phase's
    executor, AFTER human one-click approval.
  - The extract file is byte-format-identical to what ingest_one_source.py
    expects, so an approved package is ingested by copying it to
    dev/vault/<id>/ and running the existing, unchanged ingest_one_source.py.
  - Proposals (Tier / route / topic) are SUGGESTIONS for the human approver,
    derived from the dashboard's own triage fields + title keywords. They are
    never trusted blindly — the whole point of the "one-click approval" design
    is that a human confirms them in ~5 seconds.
  - OCR / image-only PDFs are NOT auto-extracted: they are flagged
    needs_ocr=true and held for manual handling (verbatim discipline).

Usage (from repo root):
  python3 dev/source/prepare_ingest_package.py --ids EDBCM080/2026,EDBC012/2026
  python3 dev/source/prepare_ingest_package.py --from-report new_circulars.json --limit 5
  python3 dev/source/prepare_ingest_package.py --candidates           # all registry-new feed entries
  (add --tier 1,2  to restrict to proposed Tiers; --dry chunks without writing files)
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]            # …/Draft
sys.path.insert(0, str(REPO_ROOT / "dev" / "vault"))
import build_wiki_index as bw                              # canonical chunker (parity with ingest_one_source)

import fitz  # PyMuPDF — verbatim extraction

REGISTRY_PATH = REPO_ROOT / "dev" / "source" / "source_registry.json"
DASHBOARD_URL = "https://circular.wongfu.net/circulars.json"
STAGING_DIR = REPO_ROOT / "dev" / "source" / "ingest_packages"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FETCH_TIMEOUT = 40
TEXT_LAYER_MIN_AVG = 100   # chars/page below this => likely image/scanned => needs OCR

# ── route proposal: ordered keyword → route (mirrors searchChannelB TOPIC_KEYWORDS
# first-match intent; this is only a SUGGESTION, the approver confirms) ──────────
ROUTE_KEYWORDS = [
    ("kg_admission",      r"幼稚園.{0,4}收生|幼稚園.{0,4}入學|幼兒班.{0,2}收生|K1.{0,3}收生"),
    ("kg_admin",          r"幼稚園.{0,4}帳目|幼稚園.{0,4}周年|幼稚園.{0,4}行政|辦學手冊|幼稚園.{0,4}財務|學前機構"),
    ("digital_education", r"數字教育|發展藍圖|DEBP|人工智能|AI|電子學習|流動電腦|智啟學教|數字素養|資訊科技教育"),
    ("value_education",   r"價值觀教育|首要價值觀|德育|公民教育|國民身份|心繫家國|學憲法|國安法"),
    ("gifted",            r"資優|資賦|拔尖"),
    ("safety",            r"消防|校舍安全|學校安全|職安|實驗室安全|斜坡|熱帶氣旋|颱風|演習|疏散"),
    ("student_support",   r"免費午膳|午膳|輔導|訓育|欺凌|虐待|危機處理|精神健康|關顧學生|健康校園|禁毒"),
    ("hr_admin",          r"教師.{0,4}語文|語文能力|基準試|教師.{0,2}獎學金|準英語教師|教師註冊|聘任|假期|薪酬|操守|代課"),
    ("activity",          r"全方位學習|課外活動|戶外活動|遊學|家校合作|家庭與學校合作|境外"),
    ("placement",         r"中學學位分配|中一派位|統一派位|學位分配|入學前.{0,4}測驗|跨境學童"),
    ("school_governance", r"法團校董|校董會|校監|辦學團體|學校管理委員會|\bIMC\b|\bSMC\b"),
    ("finance",           r"津貼|撥款|資助|採購|招標|報價|財務|捐款|多元學習津貼"),
    ("curriculum",        r"課程|科目|教學|數學建模|學習領域|課程指引|教材"),
]

# ── Tier proposal heuristics ────────────────────────────────────────────────
# Tier 3 = transient announcement / event (skip per S170 discipline)
TIER3_KEYWORDS = r"比賽|獎(?!學金)|頒獎|卓越教學|交流計劃|全年概覽|放榜|舉行日期|學與教材料|我的行動承諾|心繫家國|學憲法|教學成果獎|冠名|周年(?!帳目)|成立.{0,2}周年|名單|嘉許|典禮|展覽"
# Tier 1 = substantive evergreen policy signal
TIER1_KEYWORDS = r"收生|周年帳目|經審核|語文能力要求|免費午膳|消防|安全|課程微調|數學建模|收費|上限|要求|規定|註冊|牌照"

VALID_TOPICS = ["finance", "hr", "curriculum", "activity", "student", "it", "general"]
# dashboard topic vocab → our VALID_TOPICS
TOPIC_MAP = {
    "finance": "finance", "procurement": "finance",
    "hr": "hr", "staff": "hr",
    "curriculum": "curriculum", "teaching": "curriculum",
    "activity": "activity",
    "student": "student",
    "it": "it", "digital": "it", "technology": "it",
    "safety": "general", "governance": "general", "admin": "general", "general": "general",
}


def basename(url: str) -> str:
    return (url or "").split("?", 1)[0].rsplit("/", 1)[-1].strip().lower()


def derive_source_id(number: str, ctype: str) -> Optional[str]:
    """'EDBCM080/2026' + type 'EDBCM' -> 'edbcm080_2026'."""
    if not number or "/" not in number:
        return None
    left, _, year = number.partition("/")
    year = year.strip()
    t = (ctype or "").upper()
    num = left.upper()
    if t and num.startswith(t):
        num = num[len(t):]
    num = num.strip().lstrip("0") or "0"
    # keep the dashboard's own zero-padding (080) for human parity with EDBCM26080C
    padded = left.upper()[len(t):] if (t and left.upper().startswith(t)) else num
    return f"{t.lower()}{padded}_{year}"


def load_registry():
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) and "sources" in reg else reg
    ids = {s.get("source_id") for s in sources}
    pdfs: Set[str] = set()
    for s in sources:
        for k in ("url_primary", "url_landing"):
            b = basename(s.get(k, ""))
            if b.endswith(".pdf"):
                pdfs.add(b)
    return ids, pdfs


def propose_topic(entry: Dict) -> str:
    for t in (entry.get("k1_topics") or []) + (entry.get("topics") or []):
        mapped = TOPIC_MAP.get(str(t).lower())
        if mapped in VALID_TOPICS:
            return mapped
    return "general"


def propose_route(title: str, tags: List[str]) -> str:
    hay = (title or "") + " " + " ".join(tags or [])
    for route, pat in ROUTE_KEYWORDS:
        if re.search(pat, hay):
            return route
    return "curriculum"  # broad catch-all (matches searchChannelB fallback)


def propose_tier(entry: Dict) -> Dict:
    title = entry.get("title") or ""
    tags = " ".join(entry.get("tags") or [])
    hay = title + " " + tags
    reasons = []
    if re.search(TIER3_KEYWORDS, hay):
        return {"tier": 3, "reason": "event/announcement keyword (per S170 skip discipline)"}
    compliance = (entry.get("compliance") or "").lower()
    impact = (entry.get("impact") or "").lower()
    urgency = (entry.get("urgency") or "").lower()
    if re.search(TIER1_KEYWORDS, hay):
        reasons.append("substantive-policy keyword")
    if compliance == "mandatory":
        reasons.append("mandatory compliance")
    if impact == "high" or urgency == "high":
        reasons.append(f"impact/urgency high")
    if reasons and (compliance == "mandatory" or re.search(TIER1_KEYWORDS, hay)):
        return {"tier": 1, "reason": "; ".join(reasons)}
    return {"tier": 2, "reason": "; ".join(reasons) or "grant/scheme/administrative"}


def write_extract(source_id: str, title: str, topic: str, number: str, url: str, doc) -> tuple:
    """Write canonical extract (parity with dev/vault/<id>/extract_<id>.txt). Returns (path, n_pages)."""
    out = [
        f"# {title}", f"# source_id: {source_id}", f"# title: {title}",
        f"# fact_type: policy", f"# topic_tags: {topic}", f"# url: {url}",
        f"# circular_id: {number}", f"# extracted: (staging — prepare_ingest_package)",
        f"# auto_processed: false", "# " + "=" * 60, "",
    ]
    n = 0
    for i, page in enumerate(doc, 1):
        out.append(f"=== Page {i} ===")
        out.append(page.get_text())
        out.append("")
        n = i
    pkg_dir = STAGING_DIR / source_id
    pkg_dir.mkdir(parents=True, exist_ok=True)
    path = pkg_dir / f"extract_{source_id}.txt"
    path.write_text("\n".join(out), encoding="utf-8")
    return path, n


def chunk_stats(extract_text: str) -> Dict:
    chunks = list(bw.chunk_text_with_page_carry(extract_text))
    seen, uniq = set(), []
    for ch in chunks:
        h = bw.text_hash(ch)
        if h in seen:
            continue
        seen.add(h)
        uniq.append(ch)
    lens = [len(c) for c in uniq] or [0]
    return {
        "chunks": len(uniq),
        "char_min": min(lens), "char_med": int(statistics.median(lens)), "char_max": max(lens),
        "page_resolvable": all("=== Page" in c for c in uniq) if uniq else False,
    }


def prepare_one(entry: Dict, reg_ids: Set[str], reg_pdfs: Set[str], dry: bool) -> Optional[Dict]:
    number = entry.get("number")
    ctype = entry.get("type")
    title = entry.get("title") or ""
    pdf_urls = entry.get("pdf_urls") or []
    if not number or not pdf_urls:
        return None
    source_id = derive_source_id(number, ctype)
    url = pdf_urls[0]

    # dupe-check (PDF basename OR derived source_id already in registry)
    dupe = (basename(url) in reg_pdfs) or (source_id in reg_ids)

    topic = propose_topic(entry)
    route = propose_route(title, entry.get("tags") or [])
    tier = propose_tier(entry)

    pkg = {
        "source_id": source_id,
        "circular_number": number,
        "title": title,
        "date": entry.get("date"),
        "pdf_url": url,
        "in_registry_already": dupe,
        "proposed": {"topic": topic, "route": route, "tier": tier["tier"], "tier_reason": tier["reason"]},
        "dashboard_signals": {
            "urgency": entry.get("urgency"), "impact": entry.get("impact"),
            "compliance": entry.get("compliance"), "k1_topics": entry.get("k1_topics") or [],
            "deadlines": entry.get("deadlines") or [],
            "grant_info": entry.get("grant_info") or {},
            "channel_b_facts_linked": len(entry.get("channel_b_facts") or []),
        },
        "summary": (entry.get("summary") or "")[:400],
        "extract": None, "chunking": None, "needs_ocr": False, "status": "prepared",
    }

    if dupe:
        pkg["status"] = "skip_already_in_registry"
        return pkg

    # download + text-layer probe
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT)
        r.raise_for_status()
        doc = fitz.open(stream=r.content, filetype="pdf")
    except Exception as e:
        pkg["status"] = f"error_download_or_open: {e}"
        return pkg

    npages = doc.page_count
    total_chars = sum(len(p.get_text()) for p in doc)
    avg = total_chars // max(npages, 1)
    if avg < TEXT_LAYER_MIN_AVG:
        pkg["needs_ocr"] = True
        pkg["status"] = "held_needs_ocr"
        pkg["chunking"] = {"avg_chars_per_page": avg, "pages": npages}
        doc.close()
        return pkg

    if dry:
        # chunk in-memory without writing the extract file
        buf = []
        for i, page in enumerate(doc, 1):
            buf.append(f"=== Page {i} ===")
            buf.append(page.get_text())
            buf.append("")
        pkg["chunking"] = chunk_stats("\n".join(buf))
        pkg["status"] = "dry_run"
        doc.close()
        return pkg

    path, n = write_extract(source_id, title, topic, number, url, doc)
    doc.close()
    pkg["extract"] = str(path.relative_to(REPO_ROOT))
    pkg["chunking"] = chunk_stats(path.read_text(encoding="utf-8"))
    (STAGING_DIR / source_id / "package.json").write_text(
        json.dumps(pkg, ensure_ascii=False, indent=2), encoding="utf-8")
    return pkg


def fetch_feed(url: str) -> List[Dict]:
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT)
    r.raise_for_status()
    return (r.json().get("circulars") or [])


def write_index(pkgs: List[Dict]):
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# Ingest packages — pending review (Option A Phase 1 staging)", "",
             "> Generated by `prepare_ingest_package.py`. STAGING ONLY — nothing is ingested",
             "> until a human approves. Approve = (later phase) copy extract to dev/vault/<id>/",
             "> + run ingest_one_source.py + apply route patch + display-sync.", "",
             "| source_id | Tier | route | topic | chunks | dupe | OCR | status | title |",
             "|---|---|---|---|---|---|---|---|---|"]
    for p in pkgs:
        ch = (p.get("chunking") or {}).get("chunks", "—")
        lines.append(
            f"| `{p['source_id']}` | {p['proposed']['tier']} | {p['proposed']['route']} | "
            f"{p['proposed']['topic']} | {ch} | {'Y' if p['in_registry_already'] else ''} | "
            f"{'Y' if p['needs_ocr'] else ''} | {p['status']} | {p['title'][:36]} |")
    (STAGING_DIR / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare reviewable ingest packages for EDB circular candidates (staging only).")
    ap.add_argument("--ids", help="Comma-separated circular numbers, e.g. EDBCM080/2026,EDBC012/2026")
    ap.add_argument("--from-report", help="new_circulars.json report from check_new_circulars.py")
    ap.add_argument("--candidates", action="store_true", help="All feed entries whose PDF is not yet in the registry")
    ap.add_argument("--tier", help="Restrict to proposed Tiers, e.g. 1,2")
    ap.add_argument("--limit", type=int, default=0, help="Cap number of packages (0 = no cap)")
    ap.add_argument("--dashboard-url", default=DASHBOARD_URL)
    ap.add_argument("--dry", action="store_true", help="Chunk in memory; do not write extract/package files")
    args = ap.parse_args()

    reg_ids, reg_pdfs = load_registry()
    feed = fetch_feed(args.dashboard_url)
    by_number = {c.get("number"): c for c in feed}

    # select entries
    if args.ids:
        wanted = [s.strip() for s in args.ids.split(",") if s.strip()]
        entries = [by_number[n] for n in wanted if n in by_number]
        missing = [n for n in wanted if n not in by_number]
        if missing:
            print(f"⚠ not found in feed: {missing}", file=sys.stderr)
    elif args.from_report:
        rep = json.loads(Path(args.from_report).read_text(encoding="utf-8"))
        nums = [c.get("number") for c in rep.get("new_circulars", [])]
        entries = [by_number[n] for n in nums if n in by_number]
    elif args.candidates:
        entries = [c for c in feed if not any(basename(u) in reg_pdfs for u in (c.get("pdf_urls") or []))]
    else:
        ap.error("specify one of --ids / --from-report / --candidates")
        return 2

    tier_filter = {int(t) for t in args.tier.split(",")} if args.tier else None

    pkgs: List[Dict] = []
    for e in entries:
        pkg = prepare_one(e, reg_ids, reg_pdfs, args.dry)
        if not pkg:
            continue
        if tier_filter and pkg["proposed"]["tier"] not in tier_filter:
            continue
        pkgs.append(pkg)
        if args.limit and len(pkgs) >= args.limit:
            break

    if not args.dry:
        write_index(pkgs)

    # console summary
    print(f"Prepared {len(pkgs)} package(s){' (dry-run)' if args.dry else ''}:")
    for p in pkgs:
        ch = (p.get("chunking") or {}).get("chunks", "—")
        dl = len(p["dashboard_signals"]["deadlines"])
        flag = "DUP" if p["in_registry_already"] else ("OCR" if p["needs_ocr"] else f"T{p['proposed']['tier']}")
        print(f"  [{flag}] {p['source_id']:18} route={p['proposed']['route']:17} chunks={ch} "
              f"deadlines={dl} | {p['title'][:40]}  -> {p['status']}")
    if not args.dry:
        print(f"\nReview: {(STAGING_DIR / 'INDEX.md').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
