#!/usr/bin/env python3
"""
check_source_titles.py — cover-title parity monitor (S194).
───────────────────────────────────────────────────────────
READ-ONLY. For every PDF source in `dev/source/source_registry.json`, fetch the
document, extract page 1 (the cover), and measure how much of the registry title
actually appears there. Surfaces the class of bug where a registry entry points
at the WRONG DOCUMENT — the title says one thing, the served file is something
else entirely.

Why this exists (S194): `ict_sss_2021` was titled 《資訊及通訊科技 (中四至中六)
2021》 but its `url_primary` pointed at `CS_CAG_S4-6_Chi_2021.pdf`, which is the
《公民與社會發展科課程及評估指引》 — `CS` was read as Computer Science, it means
Citizenship and Social development. 81 chunks of the wrong subject were ingested
and served under the ICT title for months. Neither existing monitor could see it:
`check_freshness.py` asks "did the bytes at this URL change?" and
`check_served_urls.py` asks "does this URL still return 200?" — both were happily
green, because the URL was live and stable. It was just the wrong document.

Method — deterministic CJK bigram coverage, no embeddings:
  coverage = |bigrams(title) ∩ bigrams(page-1 text)| / |bigrams(title)|
An embedding would blur exactly the distinction we need (two EDB curriculum
guides are near-identical in register and would score high on cosine while
naming different subjects); shared character bigrams are literal and free.
Coverage is computed against title / title_short / title_en and the best wins,
because a cover may carry any one of them.

Signal hygiene (S126 lesson — a crashing monitor must not read as "all clear"):
  · a fetch failure is `error`, never `mismatch`
  · an image-only PDF is `no_text_layer` (unjudgeable), never `mismatch`
  · only `checked` rows can be flagged, and the report is ranked lowest-coverage
    first so a human triages rather than trusting a threshold
  · exit 1 only when errors exceed max(5, checked//20), mirroring the freshness
    and served-URL monitors; flagged mismatches go to the report, never the exit
    code (a low score is a triage item, not a build break)

Known limitations — a flag is a triage item, NOT a defect. On the first full run
(S194, 192 PDFs checked) 17 sources flagged and every one was correct on
inspection; the wrong-document case that motivated the monitor was the only real
hit in the corpus. The recurring benign classes:
  · the leading pages are a table of contents or 引言, so the title never appears
    in the sampled text (g07, g29, kgecg_2017, kg_operation_manual_2026, g35)
  · the cover is in English while the registry title is Chinese (g33)
  · the title is a pure document number with no subject words at all
    (edbc002_2026 / edbc003_2026 / edbc005_2026 — nothing to match)
  · the title is a curated composite of several documents (kg_admin_guide,
    imc_governance_supplements, sch_activities_guide, k1_admission_2627)
  · the cover extracts as glyph soup, which `looks_mojibake` catches only when it
    lands outside the main CJK block (phys_sss_2007_2015 slips through as 0.0)
Read the ranked list, not the count. Side findings worth their own follow-up show
up as `error` / `not_pdf_body` rather than `flagged`.

Usage (from repo root):
  python3 dev/source/check_source_titles.py --self-test
  python3 dev/source/check_source_titles.py --check --limit 12
  python3 dev/source/check_source_titles.py --check --only ict_sss_2021,tech_kla_guide_2017
  python3 dev/source/check_source_titles.py --check --changes-out /tmp/title_report.json
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # …/Draft
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"

FLAG_THRESHOLD = 0.45   # below this → flag for human triage (calibrated in --self-test)
LIKELY_WRONG = 0.32     # below this → "likely_wrong" severity (the S194 case scored 0.298)
COVER_PAGES = 5         # some covers are a graphic; keep reading until there is text
MIN_CJK_BIGRAMS = 2     # a title variant with less CJK signal than this is unjudgeable
MIN_LATIN_WORDS = 2     # …unless it carries at least this many latin words
MIN_COVER_LATIN = 5     # an english title can only be judged against a latin cover
MAX_BYTES = 30 * 1024 * 1024
TIMEOUT_S = 60
WORKERS = 5
UA = "Mozilla/5.0 (compatible; edb-knowledge title-parity check; read-only)"

# Boilerplate that appears on nearly every EDB cover and therefore carries no
# identifying signal. Kept as whole tokens, removed before bigramming.
TITLE_NOISE = [
    "課程發展議會", "香港考試及評核局", "聯合編訂", "香港特別行政區政府教育局",
    "公布", "供學校使用", "供學校採用", "教育局", "課程及評估指引", "課程指引",
    "補充文件", "補充指引", "學習領域", "指引", "手冊", "通函", "通告",
]

# Level ranges and years are shared by the whole corpus: every senior-secondary
# guide says 中四至中六 and a year. Leaving them in is what let the one confirmed
# wrong-document case score 0.404 — it shares 中四至中六 + 二零二一年 with the
# title while naming a completely different subject. Stripping them concentrates
# the score on the subject phrase, which is the part that actually identifies a
# document.
LEVEL_YEAR_PATTERNS = [
    r"[（(][^（()）]*[）)]",          # parenthesised clauses: levels, years, "…更新"
    r"[中小][一二三四五六]至[中小][一二三四五六]",
    r"二[零〇][零〇一二三四五六七八九十]{2,}年",
    r"(?:19|20)\d{2}(?:/\d{2})?(?:年|學年)?",
]


# ---------------------------------------------------------------------------
# pure helpers (offline-testable)
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Drop whitespace and punctuation; keep CJK, latin alnum. Lowercase latin."""
    return re.sub(r"[^\w一-鿿]", "", text or "").lower()


def cjk_bigrams(text: str) -> set[str]:
    n = normalize(text)
    return {n[i:i + 2] for i in range(len(n) - 1)} if len(n) >= 2 else set()


def cjk_only_bigrams(text: str) -> set[str]:
    """Bigrams where BOTH characters are CJK — the identifying signal of a
    Chinese title. Digit/latin bigrams are excluded because they collide across
    unrelated documents: "ICT課程指引2021" reduces to "ICT2021", whose 20/02/21
    bigrams match any cover mentioning 2021 — which is exactly how the first
    version of this monitor scored the mis-pointed ict_sss_2021 at 0.5 and
    called it ok. See --self-test 'the S194 trap'."""
    return {b for b in cjk_bigrams(text)
            if all("一" <= ch <= "鿿" for ch in b)}


def has_signal(title: str) -> bool:
    """Can this title variant carry a verdict at all?"""
    core = strip_noise(title or "")
    return (len(normalize(core)) >= 2   # short subject names judged by containment
            or len(cjk_only_bigrams(core)) >= MIN_CJK_BIGRAMS
            or len(latin_words(core)) >= MIN_LATIN_WORDS)


def encode_url(url: str) -> str:
    """EDB filenames contain raw spaces and parentheses; urllib rejects those as
    control characters. Encode the path while leaving existing %XX escapes
    intact (same fix as the S122 freshness-monitor URL patch)."""
    from urllib.parse import quote, urlsplit, urlunsplit

    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc,
                       quote(parts.path, safe="/%"),
                       quote(parts.query, safe="=&%"), parts.fragment))


def looks_mojibake(text: str) -> bool:
    """CID/Identity-H PDFs extract as garbage CJK. Such a cover cannot be
    compared with a title — it is a different problem (see the playbook card
    pdf-extraction-mojibake-triage), not a mislabel."""
    sample = text[:2000]
    if not sample.strip():
        return False
    if "�" in sample:
        return True
    cjk = sum(1 for ch in sample if "一" <= ch <= "鿿")
    # Glyph-soup lands in CJK-adjacent blocks (Hangul/compat/PUA) instead of the
    # main CJK block; a real Chinese cover is CJK-dense.
    odd = sum(1 for ch in sample
              if "㄰" <= ch <= "㆏" or "" <= ch <= ""
              or "豈" <= ch <= "﫿")
    return odd > 20 and odd > cjk


def latin_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", (text or "").lower())}


def strip_noise(title: str) -> str:
    """Reduce a title to its identifying subject phrase."""
    out = title or ""
    for pattern in LEVEL_YEAR_PATTERNS:
        out = re.sub(pattern, "", out)
    for token in TITLE_NOISE:
        out = out.replace(token, "")
    return out


def coverage(title: str, page_text: str) -> float:
    """Fraction of the title's identifying bigrams (or latin words) present in
    the cover text. 0.0 when the title carries no signal after noise removal."""
    if not title or not page_text:
        return 0.0
    core = strip_noise(title)
    # Short subject names (生物 / 物理 / 數學) reduce to one or two bigrams, where
    # bigram coverage is a coin flip. Containment is the honest test for them:
    # either the cover names the subject or it does not.
    core_n = normalize(core)
    if 2 <= len(core_n) <= 3:
        return 1.0 if core_n in normalize(page_text) else 0.0
    tb, pb = cjk_bigrams(core), cjk_bigrams(page_text)
    if tb:
        return len(tb & pb) / len(tb)
    tw, pw = latin_words(core), latin_words(page_text)
    if tw:
        return len(tw & pw) / len(tw)
    return 0.0


def best_coverage(src: dict, page_text: str) -> tuple[float, str]:
    """Best coverage across the title variants a cover might legitimately use —
    but only over variants that carry enough signal to be judged (`has_signal`).
    Without that gate a low-information variant silently rescues a genuine
    mismatch by matching a year or a latin acronym."""
    # An english title variant can only be judged against a cover that actually
    # contains english. Without this, a Chinese-covered document whose core
    # Chinese title is short falls through to title_en, which scores 0.0 against
    # the Chinese cover and reads as a mismatch (this produced 22 false
    # positives before it was caught).
    cover_has_latin = len(latin_words(page_text)) >= MIN_COVER_LATIN

    best, which = 0.0, None
    for field in ("title", "title_short", "title_en"):
        value = src.get(field)
        if not value or not has_signal(value):
            continue
        if not cjk_only_bigrams(strip_noise(value)) and not cover_has_latin:
            continue  # latin-only variant vs a chinese-only cover
        score = coverage(value, page_text)
        if which is None or score > best:
            best, which = score, field
    if which is None and src.get("title"):
        # Nothing was judgeable; fall back to the primary title so the row is
        # still scored (and will read as low coverage → triage) rather than
        # silently passing.
        return coverage(src["title"], page_text), "title (low signal)"
    return best, which


def is_pdf_source(src: dict) -> bool:
    url = (src.get("url_primary") or "").lower()
    return src.get("source_type") == "pdf" or url.endswith(".pdf")


def classify(cov: float, threshold: float = FLAG_THRESHOLD) -> str:
    return "flagged" if cov < threshold else "ok"


def severity(cov: float) -> str:
    """Ranks the triage queue. `likely_wrong` is the band the one confirmed
    wrong-document case (ict_sss_2021 → 公社科 guide, 0.298) falls in; `review`
    is the band where curated composite titles and language mismatches live."""
    return "likely_wrong" if cov < LIKELY_WRONG else "review"


def select_sources(sources: list[dict], only: list[str] | None,
                   limit: int | None) -> tuple[list[dict], list[dict]]:
    """→ (to_check, skipped). Skipped rows carry a reason and are reported."""
    to_check, skipped = [], []
    for src in sources:
        sid = src.get("source_id")
        if only and sid not in only:
            continue
        if (src.get("status") or "") == "deprecated":
            skipped.append({"source_id": sid, "status": "skipped",
                            "reason": "registry status=deprecated"})
            continue
        if not is_pdf_source(src):
            skipped.append({"source_id": sid, "status": "skipped",
                            "reason": f"not a pdf source (type={src.get('source_type')})"})
            continue
        if not (src.get("url_primary") or "").startswith("http"):
            skipped.append({"source_id": sid, "status": "skipped",
                            "reason": "no http url_primary"})
            continue
        to_check.append(src)
    if limit:
        to_check = to_check[:limit]
    return to_check, skipped


def error_budget(checked: int) -> int:
    """Same shape as check_freshness / check_served_urls (S126 lesson)."""
    return max(5, checked // 20)


# ---------------------------------------------------------------------------
# network + extraction
# ---------------------------------------------------------------------------


def fetch(url: str) -> bytes:
    req = urllib.request.Request(encode_url(url), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return resp.read(MAX_BYTES + 1)


def cover_text(pdf_bytes: bytes, pages: int = COVER_PAGES) -> tuple[str, int]:
    """Text of the leading pages + total page count. Reads up to `pages` pages
    but stops as soon as there is enough text to judge, so a graphic cover
    followed by a title page still yields signal (values_edu_framework_2026
    extracted literally "0 1" from its first two pages)."""
    import fitz  # imported lazily so --self-test needs no dependency

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        total = doc.page_count
        parts: list[str] = []
        for i in range(min(pages, total)):
            parts.append(doc.load_page(i).get_text("text"))
            if len("".join(parts).strip()) >= 120:
                break
    return "\n".join(parts), total


def check_one(src: dict) -> dict:
    sid, url = src.get("source_id"), src.get("url_primary")
    row = {"source_id": sid, "title": src.get("title"), "url": url}
    try:
        data = fetch(url)
    except urllib.error.HTTPError as e:
        return {**row, "status": "error", "reason": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001 — network/DNS/TLS all land here
        return {**row, "status": "error", "reason": f"{type(e).__name__}: {e}"}

    if len(data) > MAX_BYTES:
        return {**row, "status": "skipped", "reason": f">{MAX_BYTES // 1048576}MB"}
    if not data[:5].startswith(b"%PDF"):
        # Registry drift, not a fetch failure: the entry claims source_type=pdf
        # but the URL serves a landing page. Own status so it neither reads as a
        # title mismatch nor consumes the error budget.
        return {**row, "status": "not_pdf_body",
                "reason": "url serves HTML, not a PDF (registry says pdf)"}

    try:
        text, total_pages = cover_text(data)
    except Exception as e:  # noqa: BLE001
        return {**row, "status": "error", "reason": f"pdf parse: {type(e).__name__}"}

    if len(text.strip()) < 20:
        return {**row, "status": "no_text_layer", "pages": total_pages,
                "reason": "cover has no extractable text (image PDF) — unjudgeable"}
    if looks_mojibake(text):
        return {**row, "status": "mojibake", "pages": total_pages,
                "reason": "cover extracts as glyph soup (CID/Identity-H) — unjudgeable",
                "cover_head": " ".join(text.split())[:120]}

    cov, which = best_coverage(src, text)
    status = classify(cov)
    out = {**row, "status": status, "coverage": round(cov, 3),
           "matched_field": which, "pages": total_pages,
           "cover_head": " ".join(text.split())[:120]}
    if status == "flagged":
        out["severity"] = severity(cov)
    return out


def run_check(sources: list[dict], only: list[str] | None,
              limit: int | None) -> dict:
    to_check, skipped = select_sources(sources, only, limit)
    print(f"checking {len(to_check)} pdf sources "
          f"({len(skipped)} skipped) with {WORKERS} workers…")

    rows: list[dict] = []
    with futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for i, row in enumerate(pool.map(check_one, to_check), 1):
            rows.append(row)
            mark = {"ok": "·", "flagged": "⚠", "error": "!",
                    "no_text_layer": "?", "mojibake": "?",
                    "not_pdf_body": "H", "skipped": "-"}.get(row["status"], "?")
            cov = row.get("coverage")
            print(f"  [{i}/{len(to_check)}] {mark} {row['source_id']:<34} "
                  f"cov={cov if cov is not None else '--':<5} {row.get('reason','')}")

    counts: dict[str, int] = {}
    for row in rows + skipped:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    checked = sum(1 for r in rows if r["status"] in ("ok", "flagged"))
    return {"summary": {**counts, "checked": checked,
                        "error_budget": error_budget(checked)},
            "flagged": sorted((r for r in rows if r["status"] == "flagged"),
                              key=lambda r: r.get("coverage", 0)),
            "rows": rows, "skipped": skipped}


# ---------------------------------------------------------------------------
# self-test (offline)
# ---------------------------------------------------------------------------


def self_test() -> int:
    fails: list[str] = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    check("normalize strips punctuation and spaces",
          normalize("資訊及通訊科技 (中四至中六)") == "資訊及通訊科技中四至中六")
    check("bigrams of a 2-char string", cjk_bigrams("科技") == {"科技"})
    check("bigrams of a 1-char string are empty", cjk_bigrams("科") == set())
    check("noise removal drops EDB cover boilerplate",
          "課程發展議會" not in strip_noise("課程發展議會與香港考試及評核局聯合編訂"))
    check("noise removal reduces a title to its subject phrase",
          normalize(strip_noise("經濟課程及評估指引 (中四至中六) 2007 (2015年11月更新)")) == "經濟")
    check("noise removal strips chinese-numeral years and level ranges",
          normalize(strip_noise("資訊及通訊科技 (中四至中六) 二零二一年")) == "資訊及通訊科技")

    # The real S194 case, verbatim from the two documents.
    ict_title = ("資訊及通訊科技 (中四至中六) 二零二一年 "
                 "(於2022/23學年的中四實施並在2025年及以後的香港中學文憑考試生效)")
    right_cover = ("科技教育學習領域 資訊及通訊科技 課程及評估指引 （中四至中六） "
                   "課程發展議會與香港考試及評核局聯合編訂 "
                   "香港特別行政區政府教育局公布，供學校使用 二零二一年 "
                   "由2022/23 學年中四級開始適用")
    wrong_cover = ("公民與社會發展科 課程及評估指引 (中四至中六) "
                   "課程發展議會與香港考試及評核局聯合編訂 "
                   "香港特別行政區政府教育局公布，供學校採用 二零二一年 "
                   "由2021/22 學年中四級開始適用")
    cov_right = coverage(ict_title, right_cover)
    cov_wrong = coverage(ict_title, wrong_cover)
    print(f"     [calibration] right cover={cov_right:.3f}  wrong cover={cov_wrong:.3f}"
          f"  threshold={FLAG_THRESHOLD}")
    check("the correct ICT cover scores above the correct one by a clear margin",
          cov_right - cov_wrong > 0.15)
    check("the correct ICT cover is NOT flagged", classify(cov_right) == "ok")
    check("the wrong (公社科) cover IS flagged", classify(cov_wrong) == "flagged")

    # Regression test for the flaw that shipped in the first version of this
    # monitor: title_short "ICT課程指引2021" reduces to "ICT2021", whose digit
    # bigrams match the 公社科 cover's "由2021/22 學年", scoring 0.5 → "ok".
    ict_src = {"title": ict_title, "title_short": "ICT課程指引2021",
               "title_en": "Information and Communication Technology (Secondary 4 - 6) 2021"}
    # The invariant: whatever the eligibility rules are, a latin-acronym variant
    # must never be scored against a chinese-only cover — that is the path by
    # which "ICT課程指引2021" matched the 公社科 cover's "2021" and scored 0.5.
    # The trap, and the two independent guards that now close it: the year is
    # stripped as shared boilerplate (so "ICT課程指引2021" reduces to "ICT" and can
    # no longer match the cover's "由2021/22 學年"), and a latin-only variant is not
    # scored against a chinese-only cover at all. Either alone is sufficient.
    check("the S194 trap: a latin-acronym variant cannot match a chinese cover",
          coverage("ICT課程指引2021", wrong_cover) == 0.0
          and best_coverage({"title_short": "ICT課程指引2021"}, wrong_cover)[1] is None)
    cov_gated, field_gated = best_coverage(ict_src, wrong_cover)
    print(f"     [S194 trap] gated coverage={cov_gated:.3f} via {field_gated}"
          f"  (ungated title_short alone scored {coverage('ICT課程指引2021', wrong_cover):.3f})")
    check("with the gate, the mis-pointed source IS flagged",
          classify(cov_gated) == "flagged")
    check("and it lands in the likely_wrong band",
          severity(cov_gated) == "likely_wrong")
    check("a long chinese title has signal", has_signal(ict_title))
    check("an english title with enough words has signal",
          has_signal("Information and Communication Technology"))
    check("cjk-only bigrams exclude digit/latin pairs",
          cjk_only_bigrams("ICT2021") == set())
    check("a short chinese subject core is still judgeable (中國語文 = 3 bigrams)",
          has_signal("《中國語文課程指引（小一至小六）》（2023）"))
    # Regression test for the second flaw found while calibrating: with a short
    # Chinese core ruled unjudgeable, title_en took over and scored 0.0 against
    # a Chinese cover — 22 correct documents were flagged as mismatches.
    chi_src = {"title": "《中國語文課程指引（小一至小六）》（2023）",
               "title_en": "Chinese Language Curriculum Guide (Primary 1-6) 2023"}
    chi_cover = ("中國語文教育學習領域 中國語文課程指引 (小一至小六) 課程發展議會編訂 "
                 "香港特別行政區政府教育局公布，供學校採用 二零二三年")
    cov_chi, field_chi = best_coverage(chi_src, chi_cover)
    print(f"     [chinese cover] coverage={cov_chi:.3f} via {field_chi}")
    check("an english title_en must not judge a chinese-only cover",
          cov_chi == 1.0 and field_chi == "title")

    check("url encoding fixes raw spaces (the 24-error bug)",
          encode_url("https://a.hk/x/Geography C&A Guide 2022-chi.pdf")
          == "https://a.hk/x/Geography%20C%26A%20Guide%202022-chi.pdf")
    check("url encoding leaves existing %XX escapes alone",
          encode_url("https://a.hk/x/IIT_Summary%20on%20AI_TC.pdf")
          == "https://a.hk/x/IIT_Summary%20on%20AI_TC.pdf")

    check("mojibake cover detected (replacement chars)",
          looks_mojibake("這份文件���亂碼"))
    check("clean chinese cover is not mojibake",
          not looks_mojibake(right_cover))
    check("empty text is not mojibake", not looks_mojibake("   "))

    check("severity bands split at the calibrated value",
          severity(0.298) == "likely_wrong" and severity(0.40) == "review")

    check("a short subject name is judged by containment, not bigrams",
          coverage("生物(中四至中六) 二零零七年", "科學教育學習領域 生物 課程及評估指引") == 1.0
          and coverage("生物(中四至中六)", "科學教育學習領域 化學 課程及評估指引") == 0.0)

    check("a title with no signal after noise removal scores 0, not 1",
          coverage("課程指引", "完全無關的文件封面") == 0.0)
    check("english title falls back to word overlap",
          coverage("Information and Communication Technology",
                   "information and communication technology curriculum") > 0.9)
    check("empty page text scores 0", coverage(ict_title, "") == 0.0)

    check("best_coverage picks the winning variant",
          best_coverage({"title": "完全唔關事嘅標題",
                         "title_short": "資訊及通訊科技"}, right_cover)[1] == "title_short")

    check("pdf source detected by source_type",
          is_pdf_source({"source_type": "pdf", "url_primary": "http://x/a"}))
    check("pdf source detected by .pdf url",
          is_pdf_source({"source_type": "html", "url_primary": "http://x/a.PDF".lower()}))
    check("html landing page is not a pdf source",
          not is_pdf_source({"source_type": "html", "url_primary": "http://x/index.html"}))

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) else reg
    to_check, skipped = select_sources(sources, None, None)
    print(f"     [registry] {len(sources)} sources → {len(to_check)} pdf to check, "
          f"{len(skipped)} skipped")
    check("registry parses and yields a substantial pdf set", len(to_check) > 100)
    check("deprecated sources are skipped, not checked",
          all((s.get("status") or "") != "deprecated" for s in to_check))
    check("--only selects exactly one source",
          len(select_sources(sources, ["ict_sss_2021"], None)[0]) == 1)
    check("error budget matches the sibling monitors",
          error_budget(200) == 10 and error_budget(20) == 5)

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


# ---------------------------------------------------------------------------


def render_ledger(report: dict) -> str:
    lines = ["# Cover-title parity report", "",
             f"summary: {json.dumps(report['summary'], ensure_ascii=False)}", ""]
    if report["flagged"]:
        lines += ["## Flagged (lowest title coverage first — triage by hand)", ""]
        for r in report["flagged"]:
            lines += [f"### {r['source_id']}  coverage={r['coverage']} "
                      f"(vs {r['matched_field']})",
                      f"- registry title: {r['title']}",
                      f"- url: {r['url']}",
                      f"- cover says: {r.get('cover_head','')}", ""]
    else:
        lines += ["No flagged sources.", ""]
    for kind, header in (("error", "## Errors (fetch/parse — NOT mismatches)"),
                         ("no_text_layer", "## No text layer (unjudgeable)")):
        rows = [r for r in report["rows"] if r["status"] == kind]
        if rows:
            lines += [header, ""]
            lines += [f"- {r['source_id']}: {r.get('reason','')}" for r in rows]
            lines += [""]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--only", help="comma-separated source_ids")
    p.add_argument("--limit", type=int)
    p.add_argument("--changes-out", help="write the JSON report here")
    p.add_argument("--ledger", help="write a human-readable markdown report here")
    args = p.parse_args()

    if args.self_test:
        return self_test()
    if not args.check:
        p.print_help()
        return 0

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) else reg
    only = [s.strip() for s in args.only.split(",")] if args.only else None
    report = run_check(sources, only, args.limit)

    s = report["summary"]
    print(f"\nsummary: {json.dumps(s, ensure_ascii=False)}")
    if report["flagged"]:
        print(f"\n⚠ {len(report['flagged'])} flagged (lowest coverage first):")
        for r in report["flagged"]:
            print(f"  {r['coverage']:<6} {r['source_id']}")
            print(f"         title: {r['title'][:80]}")
            print(f"         cover: {r.get('cover_head','')[:80]}")

    if args.changes_out:
        Path(args.changes_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\nwrote {args.changes_out}")
    if args.ledger:
        Path(args.ledger).write_text(render_ledger(report), encoding="utf-8")
        print(f"wrote {args.ledger}")

    errors = s.get("error", 0)
    if errors > s["error_budget"]:
        print(f"\nFAIL: {errors} errors > budget {s['error_budget']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
