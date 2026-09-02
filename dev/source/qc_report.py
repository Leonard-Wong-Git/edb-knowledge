#!/usr/bin/env python3
"""qc_report.py — 知識庫品質健康檢查（S212）

Why this exists
---------------
Six monitors already run on a schedule (freshness / discovery / served-URL /
title-parity / expiry / new-circular), and each opens its own GitHub Issue. None
of them looks at the thing a user actually receives: the CHUNK. A URL can return
200, the registry can be fresh, the title can match — and the passage served can
still start halfway through a sentence, be one of two byte-identical copies, or
carry no page anchor to point at.

This is the sibling of the circular system's qc_report.json. Same contract on
purpose (generatedAt / overallStatus / counts / checks[] with severity, status,
detail, offenders, offender_total) so one mental model and one reader covers
both. It answers four questions, which are the four this was asked for:

  A. 政策是否指得清楚 — can the answer point at the policy (url, page, real title)
  B. chunk 是否合乎標準 — duplicates, TOC noise, length band
  C. 有冇 cut 多與少   — mid-clause starts (over-cut), page spans (under-cut)
  D. 質素是否可量度   — eval verdicts, route regression, mirror + freeze contracts

Severity ladder matches the circular report: BLOCKER > ERROR > WARN > INFO.
A check may also report NOT_MEASURED, which is NOT a pass — it says the
instrument does not exist yet, so the number below it is unknown rather than
zero. Reporting an unmeasured thing as green is the failure mode this whole
file exists to prevent.

Usage:
  python3 dev/source/qc_report.py --self-test
  python3 dev/source/qc_report.py --check [--out qc_report.json] [--cache PATH]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # …/Draft
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
EVAL_RUNS = REPO_ROOT / "dev" / "source" / "eval_runs"
DEFAULT_OUT = REPO_ROOT / "qc_report.json"
GATE_FILE = REPO_ROOT / "dev" / "source" / "release_gate.json"
HEALTH_URL = "https://edb-knowledge.onrender.com/health"
SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"

SEVERITY_ORDER = ["BLOCKER", "ERROR", "WARN", "INFO"]

# Chunk kinds that mirror Channel A. They carry no source document by design
# (S197: the store mirrors 109 of the 455 approved facts with an empty url), so
# pointing checks must exclude them or they report a design decision as a defect.
MIRROR_KINDS = {"approved_fact", "stat_fact"}

# --- thresholds -------------------------------------------------------------
# Deliberately expressed as "must not grow beyond the measured baseline" rather
# than as absolutes. Every one of these was counted on the live store on
# 2026-09-02 at 17,597 chunks; an absolute target of 0 would be red forever and
# become wallpaper (discipline #14), while a baseline makes any INCREASE visible
# the week it happens.
BASELINE = {
    "duplicate_groups": 956,
    "duplicate_extra_copies": 980,
    "midclause_start": 835,
    "toc_noise": 147,
    "no_anchor_url": 130,
    "no_page_anchor": 179,
    # 658, not the 116 first written here: the first count saw only
    # arts_kla_guide_2017 and missed the 13 stat_enrolment_YYYY sources plus
    # stat_kg. Recounted over the whole store before this file was trusted.
    "title_equals_slug": 658,
    "short_body": 3,
    "mojibake": 223,
}

_WS = re.compile(r"\s+")
_MARKER_HEAD = re.compile(r"^(?:\s*===[^=]{1,60}===\s*)+")
_PAGE_MARKER = re.compile(r"===\s*Page\s*(\d+)\s*===", re.I)
# A well-formed passage opens a clause. These openers can only be a continuation
# of something the previous chunk ended with.
_MIDCLAUSE = re.compile(r"^[）)」』、。，；：%】\]…·\-–—]|^\d{1,3}[名個條班元]")
_TOC_LEADER = re.compile(r"(\.{4,}\s*\d+|…{2,}\s*\d+)")
# Mojibake comes in TWO families and one detector cannot see both. Measured S212.
#   family 1 — CID glyph ids rendered as Latin-Extended / IPA / Greek. Looks like
#              「ƙŒȕ¸ǷǳȣƟĴ」.
#   family 2 — a Big5→UTF-8 misdecode landing in rare/extension CJK and stray
#              scripts. Looks like 「䓇ᶵ⎴䘬冰嵋冯傥≃」 — still CJK, so any check
#              that asks "is this Chinese?" passes it.
# U+00AD is NOT in family 1: the first version included it, and the control run
# showed it is an ordinary bullet marker in clean EDB prose, carrying every false
# positive on its own.
_MOJI_LATIN = re.compile(r"[\u0180-\u024f\u02b0-\u02ff\u0370-\u03ff\u0250-\u02af]")
_CJK_COMMON = re.compile(r"[\u4e00-\u9fff]")
_CJK_RARE = re.compile(r"[\u3400-\u4dbf\U00020000-\U0002ffff\u1000-\u109f"
                       r"\u0a80-\u0aff\u2e80-\u2eff]")


# ---------------------------------------------------------------------------
# pure helpers (offline-testable — no network, no clock)
# ---------------------------------------------------------------------------


def squeeze(text: str) -> str:
    """Strip ALL whitespace before comparing text.

    Same reason as eval_retrieval.squeeze: the PDF text layer breaks lines
    inside phrases, so any matcher that skips this measures line wrapping.
    """
    return _WS.sub("", text or "")


def body_of(text: str) -> str:
    """Chunk text minus its leading `=== Page N ===` / `=== label ===` markers."""
    return squeeze(_MARKER_HEAD.sub("", text or ""))


def is_midclause_start(text: str) -> bool:
    return bool(_MIDCLAUSE.match(body_of(text)))


def toc_leader_count(text: str) -> int:
    return len(_TOC_LEADER.findall(text or ""))


def page_anchored(chunk: dict) -> bool:
    """True when this chunk can point the reader at a page."""
    if _PAGE_MARKER.search(chunk.get("text") or ""):
        return True
    return "#page=" in (chunk.get("url") or "")


def mojibake_family(text: str) -> str | None:
    """Which mojibake family this chunk's body belongs to, if any.

    Family 2 is judged on the RATIO of rare-to-common CJK rather than on a raw
    count, because a legitimate document uses a rare glyph now and then; a
    misdecoded one is rare glyphs almost all the way down.
    """
    b = body_of(text)
    if len(b) < 40:
        return None
    latin = len(_MOJI_LATIN.findall(b))
    if latin >= 8 and latin / len(b) >= 0.05:
        return "latin_cid"
    rare = len(_CJK_RARE.findall(b))
    if rare >= 10 and rare > len(_CJK_COMMON.findall(b)) * 0.5:
        return "cjk_misdecode"
    return None


def duplicate_groups(chunks: list[dict]) -> dict[str, list[dict]]:
    """hash -> chunks, for hashes appearing more than once."""
    by_hash: dict[str, list[dict]] = collections.defaultdict(list)
    for c in chunks:
        by_hash[c.get("hash") or c.get("id")].append(c)
    return {h: v for h, v in by_hash.items() if len(v) > 1}


# The four questions this report exists to answer, plus the infrastructure that
# has to be up before any of them mean anything. The status page groups by this.
GROUPS = {
    "infra": "基礎設施",
    "pointing": "政策是否指得清楚",
    "chunk": "片段是否合乎標準",
    "cutting": "有沒有切得太碎或太粗",
    "measurable": "質素是否可量度",
}
CHECK_GROUP = {
    "BACKEND_HEALTH": "infra", "FREEZE_CONTRACT": "infra",
    "MIRROR_CONSISTENCY": "infra",
    "ANCHOR_URL_PRESENT": "pointing", "SOURCE_TITLE_REAL": "pointing",
    "PAGE_ANCHORED": "pointing",
    "REGISTRY_ZOMBIE": "pointing", "REGISTRY_UNMANAGED": "pointing",
    "REGISTRY_PHANTOM": "pointing", "REGISTRY_UNLISTED": "pointing",
    "REGISTRY_SERIES": "pointing",
    "NO_DUPLICATE_CHUNKS": "chunk", "NO_TOC_NOISE": "chunk",
    "BODY_LENGTH_FLOOR": "chunk", "MOJIBAKE": "chunk",
    "NO_MIDCLAUSE_START": "cutting", "TABLE_ROW_INTEGRITY": "cutting",
    "PAGE_SPAN": "cutting",
    "EVAL_LATEST": "measurable", "EVAL_CHUNK_LAYER": "measurable",
    "ROUTE_REGRESSION": "measurable",
}


def mk_check(cid: str, label: str, severity: str, status: str, detail: str,
             offenders: list[str] | None = None,
             offender_total: int | None = None) -> dict:
    offs = offenders or []
    return {
        "id": cid, "label": label, "severity": severity, "status": status,
        "group": CHECK_GROUP.get(cid, "infra"),
        "detail": detail,
        "offenders": offs[:12],
        "offender_total": offender_total if offender_total is not None else len(offs),
    }


def baseline_status(count: int, key: str) -> tuple[str, str]:
    """(status, comparison phrase) against the recorded baseline.

    Growth is the signal. Equal-to-baseline is WARN, not PASS: the defect is
    still being served — it is simply not getting worse. Calling a standing
    defect green is how a monitor stops being read.
    """
    base = BASELINE[key]
    if count > base:
        return "FAIL", f"{count} · 高於基準 {base}（+{count - base}）"
    if count < base:
        return "PASS", f"{count} · 低於基準 {base}（−{base - count}，已改善）"
    return "WARN", f"{count} · 與基準 {base} 相同（未惡化，但仍在服務中）"


def overall_status(checks: list[dict]) -> str:
    """Worst severity among failing checks. NOT_MEASURED never passes as green."""
    worst = "PASS"
    rank = {"PASS": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "BLOCKER": 4}
    for c in checks:
        if c["status"] == "PASS":
            continue
        sev = "WARN" if c["status"] == "NOT_MEASURED" else c["severity"]
        if c["status"] == "WARN":
            sev = "WARN"
        if rank[sev] > rank[worst]:
            worst = sev
    return worst


def count_checks(checks: list[dict]) -> dict:
    out = {"PASS": 0, "BLOCKER": 0, "ERROR": 0, "WARN": 0, "INFO": 0,
           "NOT_MEASURED": 0}
    for c in checks:
        if c["status"] == "PASS":
            out["PASS"] += 1
        elif c["status"] == "NOT_MEASURED":
            out["NOT_MEASURED"] += 1
        elif c["status"] == "WARN":
            out["WARN"] += 1
        else:
            out[c["severity"]] = out.get(c["severity"], 0) + 1
    return out


# ---------------------------------------------------------------------------
# check builders (pure — take data, return a check dict)
# ---------------------------------------------------------------------------


def check_anchor_url(chunks: list[dict]) -> dict:
    bad = [c for c in chunks
           if c.get("content_type") not in MIRROR_KINDS
           and not (c.get("url") or "").strip()]
    status, phrase = baseline_status(len(bad), "no_anchor_url")
    by_src = collections.Counter(c["source_id"] for c in bad)
    return mk_check(
        "ANCHOR_URL_PRESENT",
        "每條片段都有可點擊的來源連結（Channel A 鏡像除外）",
        "ERROR", status,
        f"{phrase} · 無連結片段來自 {len(by_src)} 個來源",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_title_real(chunks: list[dict]) -> dict:
    """A chunk whose title IS its source_id shows the user a raw slug."""
    bad = [c for c in chunks if (c.get("title") or "").strip() == c.get("source_id")]
    status, phrase = baseline_status(len(bad), "title_equals_slug")
    by_src = collections.Counter(c["source_id"] for c in bad)
    return mk_check(
        "SOURCE_TITLE_REAL",
        "片段標題是文件名稱，不是內部代號",
        "ERROR", status,
        f"{phrase} · 用戶會在答案中看見原始代號而非文件名",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_page_anchor(chunks: list[dict]) -> dict:
    bad = [c for c in chunks
           if c.get("content_type") not in MIRROR_KINDS and not page_anchored(c)]
    status, phrase = baseline_status(len(bad), "no_page_anchor")
    by_src = collections.Counter(c["source_id"] for c in bad)
    return mk_check(
        "PAGE_ANCHORED",
        "片段可指向頁數或章節（有 Page 標記或 #page= 連結）",
        "WARN", status,
        f"{phrase} · 這些片段只能把用戶帶到文件首頁",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_duplicates(chunks: list[dict]) -> dict:
    groups = duplicate_groups(chunks)
    extra = sum(len(v) - 1 for v in groups.values())
    status, phrase = baseline_status(len(groups), "duplicate_groups")
    pairs = collections.Counter()
    for v in groups.values():
        pairs[tuple(sorted({c["source_id"] for c in v}))] += 1
    return mk_check(
        "NO_DUPLICATE_CHUNKS",
        "沒有兩個來源載住逐字相同的片段",
        "ERROR", status,
        f"重複組 {phrase} · 多出的副本 {extra} 條 · "
        f"重複全部跨來源（同一來源內 0 組），即問題出在登記了兩次的文件，不是切片器。"
        f"⚠️ 此數是下限：只捉逐字相同的片段。同一份 PDF 分兩次抽取會切出不同邊界，"
        f"雜湊就不同 —— kgecg_2017 與 g29 是同一份《幼稚園教育課程指引（2017）》，"
        f"108 對 107 條，逐字相同 0 條，本檢查完全看不見",
        [f"{' ↔ '.join(k)}：{n} 組" for k, n in pairs.most_common()], len(groups))


def check_toc_noise(chunks: list[dict]) -> dict:
    bad = [c for c in chunks if toc_leader_count(c.get("text")) >= 3]
    status, phrase = baseline_status(len(bad), "toc_noise")
    by_src = collections.Counter(c["source_id"] for c in bad)
    return mk_check(
        "NO_TOC_NOISE",
        "沒有純目錄片段（三個或以上「……頁碼」）",
        "WARN", status,
        f"{phrase} · 目錄片段答不到任何問題，只會佔住合成窗",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_midclause(chunks: list[dict]) -> dict:
    """OVER-CUT: the passage begins in the middle of a clause."""
    bad = [c for c in chunks
           if c.get("content_type") == "vault_extract" and is_midclause_start(c.get("text"))]
    status, phrase = baseline_status(len(bad), "midclause_start")
    by_src = collections.Counter(c["source_id"] for c in bad)
    return mk_check(
        "NO_MIDCLAUSE_START",
        "切得不會太碎：片段不是由半句開始",
        "ERROR", status,
        f"{phrase} · 由半句開始的片段餵給合成器，正是 S211「片段由半行開始」那一類缺陷",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_short_body(chunks: list[dict]) -> dict:
    bad = [c for c in chunks
           if c.get("content_type") == "vault_extract" and len(body_of(c.get("text"))) < 60]
    status, phrase = baseline_status(len(bad), "short_body")
    return mk_check(
        "BODY_LENGTH_FLOOR",
        "片段正文不少於 60 字",
        "WARN", status,
        f"{phrase} · 逐條讀過：現存者全部是表格標題行（例如「全日制資助小學教學人員編制"
        f"（由 2022/23 學年起生效）」），屬正常，不是斷句",
        [f"{c['source_id']}：{body_of(c.get('text'))[:40]}" for c in bad], len(bad))


def check_mojibake(chunks: list[dict]) -> dict:
    """Unreadable chunks. Was NOT_MEASURED until S212 built a detector.

    No existing monitor can see this class: the URL returns 200 (check_served_urls),
    the registry bytes are unchanged (check_freshness), and the COVER text still
    matches the title (check_source_titles reads the cover, not the body). A source
    can therefore serve nothing but garbage while every light stays green — and one
    does.
    """
    hits = [(c, mojibake_family(c.get("text"))) for c in chunks]
    bad = [(c, f) for c, f in hits if f]
    status, phrase = baseline_status(len(bad), "mojibake")
    fams = collections.Counter(f for _, f in bad)
    by_src = collections.Counter(c["source_id"] for c, _ in bad)
    total = collections.Counter(c["source_id"] for c in chunks)
    return mk_check(
        "MOJIBAKE", "沒有不可讀片段（兩個亂碼家族）", "ERROR", status,
        f"{phrase} · 家族分佈 {dict(fams)} · "
        f"`phys_sss_2007_2015` 有 {by_src.get('phys_sss_2007_2015', 0)}/"
        f"{total.get('phys_sss_2007_2015', 0)} 條不可讀。"
        f"URL 回 200、雜湊不變、封面標題對得上，所以現有三個監察全部看不見",
        [f"{s}：{n}/{total[s]}（{100 * n / total[s]:.0f}%）"
         for s, n in by_src.most_common()], len(bad))


def check_page_span(chunks: list[dict]) -> dict:
    """UNDER-CUT proxy, reported as INFO on purpose."""
    bad = [c for c in chunks if len(set(_PAGE_MARKER.findall(c.get("text") or ""))) > 1]
    by_src = collections.Counter(c["source_id"] for c in bad)
    pct = (100.0 * len(bad) / len(chunks)) if chunks else 0.0
    return mk_check(
        "PAGE_SPAN", "跨頁片段數（切得太粗的觀察指標）", "INFO", "INFO",
        f"{len(bad)} 條（{pct:.1f}%）跨越分頁。散文跨頁是正常的，所以此項只記錄不判分；"
        f"要判「切得太粗」須先有 content_kind 標註（Open Priority ④），現時未有",
        [f"{s}（{n} 條）" for s, n in by_src.most_common()], len(bad))


def check_table_rows(chunks: list[dict]) -> dict:
    """staff_est_pri must serve one establishment row per chunk, both day types."""
    rows = [c for c in chunks if c["source_id"] == "staff_est_pri"]
    pat = re.compile(r"(全日制|半日制)資助小學核准開辦(\d+)班的教學人員編制")
    found = collections.defaultdict(set)
    multi = []
    for c in rows:
        hits = pat.findall(body_of(c.get("text")))
        if len(hits) > 1:
            multi.append(c["id"])
        for mode, n in hits:
            found[mode].add(int(n))
    full = sorted(found.get("全日制", set()))
    half = sorted(found.get("半日制", set()))
    ok = bool(full) and not multi
    detail = (f"staff_est_pri {len(rows)} 條 · 全日制班數 {len(full)} 個"
              f"（{full[0] if full else '-'}–{full[-1] if full else '-'}）· "
              f"半日制 {len(half)} 個 · 一片段載多過一行者 {len(multi)}")
    return mk_check(
        "TABLE_ROW_INTEGRITY", "編制表逐行切開，一個片段一行", "ERROR",
        "PASS" if ok else "FAIL", detail, multi, len(multi))


def check_eval_latest(run: dict | None) -> list[dict]:
    if run is None:
        return [mk_check("EVAL_LATEST", "最近一次檢索評測", "ERROR",
                         "NOT_MEASURED", "找不到 eval run 檔"),
                mk_check("EVAL_CHUNK_LAYER", "檢索評測的片段層斷言", "ERROR",
                         "NOT_MEASURED", "找不到 eval run 檔")]
    s = run.get("summary", {})
    fail, err = s.get("FAIL", 0), s.get("errors", 0)
    out = [mk_check(
        "EVAL_LATEST", "最近一次檢索評測（來源層）", "ERROR",
        "PASS" if fail == 0 and err == 0 else "FAIL",
        f"{run.get('label')} · PASS={s.get('PASS')} FAIL={fail} "
        f"RECORD_ONLY={s.get('RECORD_ONLY')} errors={err} · 共 {s.get('queries')} 條 query")]
    if "chunk_FAIL" in s:
        cf = s.get("chunk_FAIL", 0)
        out.append(mk_check(
            "EVAL_CHUNK_LAYER", "檢索評測的片段層斷言（S212 新增）", "ERROR",
            "PASS" if cf == 0 else "FAIL",
            f"chunk PASS={s.get('chunk_PASS')} FAIL={cf} · "
            f"斷言用文字簽名而非 chunk id（id 是 text 的 md5，每次重切都會變）"))
    else:
        out.append(mk_check(
            "EVAL_CHUNK_LAYER", "檢索評測的片段層斷言（S212 新增）", "ERROR",
            "NOT_MEASURED", "最近一次 run 由 S212 之前的 harness 產生，未記錄片段身分"))
    return out


def check_mirrors(live_total: int, mirror_values: dict[str, int | None]) -> dict:
    bad = [f"{k}：{v}" for k, v in mirror_values.items() if v != live_total]
    missing = [k for k, v in mirror_values.items() if v is None]
    return mk_check(
        "MIRROR_CONSISTENCY", "七個對外片段數鏡像與資料庫真數一致", "ERROR",
        "PASS" if not bad else "FAIL",
        f"資料庫真數 {live_total} · 已核對 {len(mirror_values)} 個鏡像 · "
        f"不一致 {len(bad)} 個 · 讀不到 {len(missing)} 個。"
        f"S209 定案：片段數一律由資料庫讀真數，不得靠加減推算",
        bad, len(bad))


def check_freeze_contract(knowledge: dict, guidelines: dict) -> dict:
    """The frozen public contract. Channel A is FROZEN at 455 facts since S111."""
    km, gm = knowledge.get("_meta", {}), guidelines.get("_meta", {})
    # Each topic block is a DICT of role -> list of facts, plus `_`-prefixed
    # metadata keys (_source_refs / _label / _keywords_zh). Summing the topic
    # values directly returns 0, which would have reported an intact contract as
    # broken; counted against the known 455 before being trusted.
    facts = 0
    for key, block in knowledge.items():
        if key == "_meta" or not isinstance(block, dict):
            continue
        for role, items in block.items():
            if not role.startswith("_") and isinstance(items, list):
                facts += len(items)
    want = {"knowledge_version": "2.3.0", "facts": 455,
            "guidelines_version": "2.6.1", "guidelines_count": 158}
    got = {"knowledge_version": km.get("version"), "facts": facts,
           "guidelines_version": gm.get("version"),
           "guidelines_count": gm.get("count")}
    bad = [f"{k}：預期 {want[k]}，實際 {got[k]}" for k in want if got[k] != want[k]]
    return mk_check(
        "FREEZE_CONTRACT", "凍結的對外契約零接觸", "BLOCKER",
        "PASS" if not bad else "FAIL",
        f"knowledge.json _meta {got['knowledge_version']} · 事實 {got['facts']} 條 · "
        f"guidelines.json _meta {got['guidelines_version']} · 指引 {got['guidelines_count']} 項。"
        f"下游 EDB 通告系統依賴這四個值；改動須另行協調",
        bad, len(bad))


def check_registry_drift(chunks: list[dict]) -> list[dict]:
    """Open Priority ② — three lists that must agree and do not.

    Replaces an earlier version here that compared COUNTS (273 registry vs 177
    browsable = "gap 96"). That number was meaningless: the drift runs in four
    directions and they net against each other, so the single figure hid both
    the 42 browse entries that serve nothing and the 14 sources no registry
    tracks. Delegated to check_registry_drift.py so there is one definition.
    """
    import check_registry_drift as drift_mod

    serving = collections.Counter(c["source_id"] for c in chunks)
    kinds: dict[str, str] = {}
    for c in chunks:
        kinds.setdefault(c["source_id"], c.get("content_type") or "")
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sources = reg["sources"] if isinstance(reg, dict) and "sources" in reg else reg
    live, dead = drift_mod.registry_ids(sources)
    listed = {g["id"] for g in drift_mod.parse_guidelines_registry(
        (REPO_ROOT / "app.html").read_text(encoding="utf-8", errors="replace"))}
    d = drift_mod.classify(dict(serving), kinds, live, dead, listed,
                           drift_mod.series_parents(sources))

    titles = {}
    for c in chunks:
        titles.setdefault(c["source_id"], c.get("title") or "")
    for src in sources:
        sid = src.get("source_id") or src.get("id")
        if sid and src.get("title"):
            titles[sid] = src["title"]

    out = []
    ids = ["REGISTRY_ZOMBIE", "REGISTRY_SERIES", "REGISTRY_UNMANAGED",
           "REGISTRY_PHANTOM", "REGISTRY_UNLISTED"]
    for cid, cls in zip(ids, ("ZOMBIE", "SERIES_UNMONITORED", "UNMANAGED",
                              "PHANTOM", "UNLISTED")):
        members = d[cls]
        n_chunks = sum(serving.get(s, 0) for s in members)
        extra = {
            "ZOMBIE": "已有人決定它應該停止服務，而它沒有停 —— 四類之中唯一不需要任何人再做決定的",
            "UNMANAGED": "新鮮度、到期、封面標題三個監察全部以 registry 為鍵，所以這些來源不受任何監察",
            "PHANTOM": "用戶可以瀏覽到，但搜尋答不出，因為庫內一條片段都沒有",
            "UNLISTED": "要逐個判斷該不該公開瀏覽，屬人手閘，不能自動修",
            "SERIES_UNMONITORED":
                "registry 用 url_primary_pattern + years_extracted 描述整個年度系列，"
                "但 check_freshness / check_expiry / check_source_titles 三者只讀 "
                "url_primary，全部不展開年份 —— 所以 13 個分年檔（528 條片段、13 條實測 200 的 URL）"
                "不受任何 registry 監察。缺陷在監察，不在登記",
        }[cls]
        out.append(mk_check(
            cid, drift_mod.LABEL[cls], drift_mod.SEVERITY[cls],
            "PASS" if not members else "FAIL",
            f"{len(members)} 個來源 / {n_chunks} 條片段 · {extra}",
            [f"{s}（{serving.get(s, 0)} 條）{titles.get(s, '')[:26]}" for s in members],
            len(members)))
    return out


def check_backend(health: dict | None) -> list[dict]:
    if health is None:
        return [mk_check("BACKEND_HEALTH", "後端服務可達", "BLOCKER",
                         "FAIL", "/health 無回應")]
    ok = bool(health.get("ok"))
    cache = health.get("cache_a", {})
    return [mk_check(
        "BACKEND_HEALTH", "後端服務可達", "BLOCKER", "PASS" if ok else "FAIL",
        f"ok={ok} · commit={health.get('commit')} · "
        f"啟動於 {health.get('started_at')} · Channel A 快取 {cache.get('size')} 條")]


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def http_json(url: str, headers: dict | None = None, timeout: int = 90):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def supabase_key() -> str:
    key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    if key:
        return key
    env = REPO_ROOT / "backend" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            for name in ("SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"):
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip()
    raise RuntimeError("no Supabase key in env or backend/.env")


def fetch_chunks(cache: Path | None) -> list[dict]:
    """Whole store, paged. A page that comes back as an error OBJECT is not rows.

    S211 lost a backup file to exactly that: an error dict was appended to a row
    list and its keys counted as records. The isinstance guard below is why this
    function asserts instead of trusting the response shape.
    """
    if cache and cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    key = supabase_key()
    cols = "id,hash,text,source_id,title,url,topic,content_type,fact_type"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    out: list[dict] = []
    step, off = 1000, 0
    while True:
        page = http_json(
            f"{SUPABASE_URL}/rest/v1/wiki_chunks?select={cols}"
            f"&order=id&offset={off}&limit={step}", headers, timeout=120)
        if isinstance(page, dict):
            raise RuntimeError(f"Supabase returned an error object at offset {off}: "
                               f"{json.dumps(page)[:200]}")
        assert all(isinstance(r, dict) for r in page), "non-dict row in page"
        out += page
        if len(page) < step:
            break
        off += step
    if cache:
        cache.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def read_mirrors(live_total: int) -> dict[str, int | None]:
    """The seven public chunk-count mirrors, read as they are actually written."""
    files = ["app.html", "index.html", "knowledge.json", "role_facts.json",
             "dev/knowledge/role_facts.json", "README.md", "K1_API_SPEC.md"]
    out: dict[str, int | None] = {}
    plain, comma = str(live_total), f"{live_total:,}"
    for f in files:
        p = REPO_ROOT / f
        if not p.exists():
            out[f] = None
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        out[f] = live_total if (plain in text or comma in text) else -1
    return out


def guidelines_registry_count() -> int | None:
    """Parse GUIDELINES_REGISTRY out of app.html (it is inline JSX, not JSON)."""
    app = (REPO_ROOT / "app.html").read_text(encoding="utf-8", errors="replace")
    i = app.find("GUIDELINES_REGISTRY")
    if i < 0:
        return None
    start = app.find("[", i)
    depth, j = 0, start
    while j < len(app):
        if app[j] == "[":
            depth += 1
        elif app[j] == "]":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return app.count('id:', start, j) or None


def latest_eval_run() -> dict | None:
    runs = sorted(EVAL_RUNS.glob("*.json"))
    if not runs:
        return None
    return json.loads(runs[-1].read_text(encoding="utf-8"))


def route_regression() -> dict:
    script = REPO_ROOT / "dev" / "source" / "route_regression.mjs"
    if not script.exists():
        return mk_check("ROUTE_REGRESSION", "路由回歸測試", "ERROR",
                        "NOT_MEASURED", "找不到 route_regression.mjs")
    try:
        p = subprocess.run(["node", str(script)], cwd=str(REPO_ROOT),
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return mk_check("ROUTE_REGRESSION", "路由回歸測試", "ERROR",
                        "NOT_MEASURED", f"無法執行：{e}")
    tail = [l for l in p.stdout.splitlines() if "PASS" in l and "/" in l]
    return mk_check("ROUTE_REGRESSION", "路由回歸測試（每條 query 去對的路由）",
                    "ERROR", "PASS" if p.returncode == 0 else "FAIL",
                    tail[-1].strip() if tail else f"exit={p.returncode}",
                    [l for l in p.stdout.splitlines() if l.startswith("FAIL")])


# ---------------------------------------------------------------------------
# report assembly
# ---------------------------------------------------------------------------


def build_report(chunks: list[dict], health: dict | None, registry: list[dict],
                 knowledge: dict, guidelines: dict, guideline_count: int | None,
                 run: dict | None) -> dict:
    live_total = len(chunks)
    serving = {c["source_id"] for c in chunks}
    checks: list[dict] = []
    checks += check_backend(health)
    checks.append(check_freeze_contract(knowledge, guidelines))
    checks.append(check_mirrors(live_total, read_mirrors(live_total)))
    # A. 政策是否指得清楚
    checks.append(check_anchor_url(chunks))
    checks.append(check_title_real(chunks))
    checks.append(check_page_anchor(chunks))
    # B. chunk 是否合乎標準
    checks.append(check_duplicates(chunks))
    checks.append(check_toc_noise(chunks))
    checks.append(check_short_body(chunks))
    # C. 有冇 cut 多與少
    checks.append(check_midclause(chunks))
    checks.append(check_table_rows(chunks))
    checks.append(check_page_span(chunks))
    # D. 質素是否可量度
    checks += check_eval_latest(run)
    checks.append(route_regression())
    checks += check_registry_drift(chunks)
    checks.append(check_mojibake(chunks))

    by_src = collections.Counter(c["source_id"] for c in chunks)
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "overallStatus": overall_status(checks),
        "counts": {"chunks": live_total, **count_checks(checks)},
        "version": platform_version(),
        "corpus": {
            "chunks": live_total,
            "sources_serving": len(serving),
            "sources_registered": len(registry),
            "guidelines_listed": guideline_count,
            "distinct_urls": len({(c.get("url") or "").split("#")[0]
                                  for c in chunks if (c.get("url") or "").strip()}),
            "largest_sources": [{"source_id": s, "chunks": n}
                                for s, n in by_src.most_common(8)],
        },
        "groups": GROUPS,
        "releaseGate": build_release_gate(
            checks,
            json.loads(GATE_FILE.read_text(encoding="utf-8")) if GATE_FILE.exists() else {},
            time.strftime("%Y-%m-%d", time.gmtime())),
        "checks": checks,
    }


def build_release_gate(checks: list[dict], cfg: dict, today: str) -> dict:
    """封版閘 — S212. Whether this state may be released, and why not.

    Three rules, and all three exist because a gate that can only pass is
    decoration:

    1. An unwaived WARN is NOT_MET. The default is to block. A standing defect
       becomes acceptable only when a person writes down who owns it, why, and
       until when — and the waiver expires on its own date, so nobody has to
       remember to revisit it.
    2. A manual criterion with no dated attestation is NOT_MET, never absent.
       The things a machine cannot check (does the answer match the PDF, does
       the tablet layout hold, does the uploaded file stay in the browser) are
       exactly the things that break; leaving them off the list would make the
       gate greener than the product.
    3. NOT_MEASURED is NOT_MET. Not measuring something is not evidence that it
       is fine.
    """
    by_id = {c["id"]: c for c in checks}
    auto = cfg.get("auto_criteria", {})
    waived = {w["check_id"]: w for w in cfg.get("standing_waivers", [])}
    crit: list[dict] = []

    def add(cid, label, kind, ok, detail):
        crit.append({"id": cid, "label": label, "kind": kind,
                     "status": "MET" if ok else "NOT_MET", "detail": detail})

    blockers = [c["id"] for c in checks
                if c["severity"] == "BLOCKER" and c["status"] not in ("PASS", "INFO")]
    if auto.get("no_blocker"):
        add("NO_BLOCKER", "沒有攔截級未通過項", "auto", not blockers,
            "、".join(blockers) if blockers else "0 項")

    errs = [c["id"] for c in checks
            if c["severity"] == "ERROR" and c["status"] == "FAIL"]
    if auto.get("no_error_fail"):
        add("NO_ERROR_FAIL", "沒有錯誤級 FAIL", "auto", not errs,
            "、".join(errs) if errs else "0 項")

    unmeasured = [c["id"] for c in checks if c["status"] == "NOT_MEASURED"]
    if auto.get("no_unmeasured"):
        add("NO_UNMEASURED", "沒有未量度項（或已明確列為 out-of-scope）", "auto",
            not unmeasured, "、".join(unmeasured) if unmeasured else "0 項")

    for cid in auto.get("must_pass", []):
        c = by_id.get(cid)
        add(f"PASS_{cid}", f"{cid} 必須 PASS", "auto",
            bool(c) and c["status"] == "PASS",
            c["status"] if c else "此檢查不存在")

    # Standing WARNs: waived (with an unexpired date) or blocking.
    warns = [c for c in checks if c["status"] == "WARN"]
    unwaived, expired = [], []
    for c in warns:
        w = waived.get(c["id"])
        if not w:
            unwaived.append(c["id"])
        elif str(w.get("accept_until", "")) < today:
            expired.append(f"{c['id']}（{w.get('owner')} 的接受期 {w.get('accept_until')} 已過）")
    add("WARNS_OWNED", "每個 standing WARN 都有 owner、理由、接受期限", "auto",
        not unwaived and not expired,
        f"未有 waiver {len(unwaived)} 項"
        + (f"：{'、'.join(unwaived[:6])}" if unwaived else "")
        + (f"；已過期 {len(expired)} 項：{'、'.join(expired)}" if expired else ""))

    for m in cfg.get("manual_checks", []):
        rec = m.get("verified_at")
        if not rec:
            add(m["id"], m["label"], "manual", False, "從未記錄人手驗證")
            continue
        age_ok = rec >= _days_ago(today, int(m.get("max_age_days", 30)))
        add(m["id"], m["label"], "manual", age_ok,
            f"{rec} 由 {m.get('verified_by', '?')} 驗證"
            + ("" if age_ok else f"，已超過 {m.get('max_age_days')} 日有效期"))

    unmet = [c for c in crit if c["status"] == "NOT_MET"]
    return {
        "status": "PASS" if not unmet else "FAIL",
        "summary": f"{len(crit) - len(unmet)}/{len(crit)} 項達標",
        "blocking": [c["id"] for c in unmet],
        "criteria": crit,
    }


def _days_ago(today: str, days: int) -> str:
    import datetime
    d = datetime.date.fromisoformat(today) - datetime.timedelta(days=days)
    return d.isoformat()


def platform_version() -> str:
    app = (REPO_ROOT / "app.html").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"PLATFORM_VERSION\s*=\s*['\"]([^'\"]+)", app)
    return f"v{m.group(1)}" if m else "version unverified"


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def self_test() -> int:
    fails = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    check("squeeze strips whitespace", squeeze("新 入\n職") == "新入職")
    check("body_of drops leading page markers",
          body_of("=== Page 3 ===\n全日制資助小學") == "全日制資助小學")
    check("body_of drops stacked markers",
          body_of("=== Page 1 ===\n=== introduction ===\n內容") == "內容")
    check("mid-clause start detected (closing bracket)",
          is_midclause_start("=== Page 2 ===\n），並能按情況修訂"))
    check("mid-clause start detected (bare count continuing a row)",
          is_midclause_start("14 名，教學人員合計21 名"))
    check("a normal opening is NOT flagged",
          not is_midclause_start("=== Page 1 ===\n全日制資助小學核准開辦12 班"))
    check("TOC leader counted", toc_leader_count("第一章......12\n第二章......18\n第三章......25") == 3)
    check("prose with one dotted line is not TOC",
          toc_leader_count("見附件......5") == 1)
    check("page anchor via marker", page_anchored({"text": "=== Page 4 ===x", "url": ""}))
    check("page anchor via url fragment",
          page_anchored({"text": "x", "url": "https://e.gov/a.pdf#page=7"}))
    check("no page anchor at all",
          not page_anchored({"text": "x", "url": "https://e.gov/a.pdf"}))

    check("family 1 detected (Latin-range CID glyph ids)",
          mojibake_family("ƙŒȕ¸ǷǳȣƟĴŏŹƭĎĪÅĄƭĎ¸ŵȕȣƟĴěï¸ǷǳȣƟĴƚĊĥȼě¼·ųǕéƌāȶËĴƵ")
          == "latin_cid")
    check("family 2 detected (rare/extension CJK misdecode)",
          mojibake_family(
              "嬘柴ᶲἄ㶙ℍ妶婾炻᷎栗䣢ṾᾹ怷廗⍲忋屓⛘䳬䷼堐忼シ⾝䘬傥≃ˤ⬠㟉⎗⍫教㭷⸜侫娎娎⌟炻"
              "ẍḮ妋侫娎䘬⼊⺷娎柴䘬㶙㶢䦳⹎ˤ㟉㛔姽㟠⛐℔攳姽㟠ᷕ炻㟉㛔姽㟠㗗㊯⛐⬠㟉忚埴炻"
              "᷎䓙ả㔁侩ⷓ姽↮䘬姽㟠ˤ⮵㕤䈑䎮䥹Ἦ婒炻㟉㛔姽㟠䘬ᷣ天䎮⾝㗗天㍸ὃ㚱㓰䘬⛆")
          == "cjk_misdecode")
    check("clean Traditional Chinese prose is NOT flagged",
          mojibake_family("學校應每年進行問卷調查，以促進學校進行以實證為本的自評，"
                          "並按學生的能力決定是否採用學生問卷，詳情請參閱有關指引。") is None)
    check("a soft hyphen used as a bullet is NOT mojibake (the first version's bug)",
          mojibake_family("與職場相關的情境透過提供以下資料和經驗，拓闊學生的視野："
                          "\u00ad專業／行業／工業群\u00ad環球及本地前景，讓學生掌握所選學習範疇") is None)
    check("a short chunk is not judged at all",
          mojibake_family("ƙŒȕ¸Ƿǳ") is None)

    dup = duplicate_groups([{"hash": "a", "source_id": "s1"},
                            {"hash": "a", "source_id": "s2"},
                            {"hash": "b", "source_id": "s1"}])
    check("duplicate groups found by hash", list(dup) == ["a"] and len(dup["a"]) == 2)

    # THE GATE MUST GO RED. Growth beyond baseline fails; parity warns; never green.
    check("count above baseline FAILS", baseline_status(957, "duplicate_groups")[0] == "FAIL")
    check("count equal to baseline WARNS (a standing defect is not green)",
          baseline_status(956, "duplicate_groups")[0] == "WARN")
    check("count below baseline PASSES", baseline_status(900, "duplicate_groups")[0] == "PASS")

    check("NOT_MEASURED never counts as green",
          overall_status([mk_check("x", "l", "WARN", "NOT_MEASURED", "d")]) == "WARN")
    check("a failing BLOCKER dominates a failing WARN",
          overall_status([mk_check("a", "l", "WARN", "FAIL", "d"),
                          mk_check("b", "l", "BLOCKER", "FAIL", "d")]) == "BLOCKER")
    check("all green is PASS",
          overall_status([mk_check("a", "l", "ERROR", "PASS", "d")]) == "PASS")

    # Shaped like the real file: topic -> {role: [facts], _meta keys}. A counter
    # that walks the wrong shape returns 0 and reports an intact contract broken,
    # which is what the first version of this check did.
    def kb(n):
        return {"_meta": {"version": "2.3.0"},
                "hr": {"_label": "人事", "_source_refs": ["x"],
                       "all_roles": [1] * n, "principal": []}}

    gl = {"_meta": {"version": "2.6.1", "count": 158}}
    check("intact freeze contract passes", check_freeze_contract(kb(455), gl)["status"] == "PASS")
    check("one missing fact breaks the freeze contract",
          check_freeze_contract(kb(454), gl)["status"] == "FAIL")
    check("metadata keys are not counted as facts",
          check_freeze_contract(kb(455), gl)["detail"].find("455 條") > 0)

    m_ok = check_mirrors(100, {"a": 100, "b": 100})
    m_bad = check_mirrors(100, {"a": 100, "b": -1})
    check("mirrors agreeing passes", m_ok["status"] == "PASS")
    check("one stale mirror FAILS", m_bad["status"] == "FAIL" and m_bad["offender_total"] == 1)

    rows = [{"id": "r1", "source_id": "staff_est_pri",
             "text": "=== Page 1 ===\n全日制資助小學核准開辦12 班的教學人員編制：校長1 名"},
            {"id": "r2", "source_id": "staff_est_pri",
             "text": "=== Page 3 ===\n半日制資助小學核准開辦12 班的教學人員編制：校長1 名"}]
    check("one row per chunk passes", check_table_rows(rows)["status"] == "PASS")
    merged = rows + [{"id": "r3", "source_id": "staff_est_pri",
                      "text": "全日制資助小學核准開辦24 班的教學人員編制：x "
                              "全日制資助小學核准開辦36 班的教學人員編制：y"}]
    check("two rows in one chunk FAILS", check_table_rows(merged)["status"] == "FAIL")

    check("eval with no run file is NOT_MEASURED, not PASS",
          all(c["status"] == "NOT_MEASURED" for c in check_eval_latest(None)))
    old_run = {"label": "old", "summary": {"PASS": 5, "FAIL": 0, "errors": 0,
                                           "RECORD_ONLY": 1, "queries": 6}}
    got = check_eval_latest(old_run)
    check("a pre-S212 run reports the chunk layer as NOT_MEASURED",
          got[0]["status"] == "PASS" and got[1]["status"] == "NOT_MEASURED")

    # ---- release gate ----------------------------------------------------
    def ck(cid, sev, st):
        return mk_check(cid, cid, sev, st, "d")

    green = [ck("FREEZE_CONTRACT", "BLOCKER", "PASS"), ck("EVAL_LATEST", "ERROR", "PASS")]
    cfg = {"auto_criteria": {"no_blocker": True, "no_error_fail": True,
                             "no_unmeasured": True,
                             "must_pass": ["FREEZE_CONTRACT", "EVAL_LATEST"]},
           "standing_waivers": [], "manual_checks": []}
    g = build_release_gate(green, cfg, "2026-09-02")
    check("a clean state with no manual checks passes the gate", g["status"] == "PASS")

    g = build_release_gate(green + [ck("X", "BLOCKER", "FAIL")], cfg, "2026-09-02")
    check("a BLOCKER fails the gate", g["status"] == "FAIL" and "NO_BLOCKER" in g["blocking"])

    g = build_release_gate(green + [ck("Y", "ERROR", "NOT_MEASURED")], cfg, "2026-09-02")
    check("NOT_MEASURED fails the gate (not measuring is not evidence)",
          "NO_UNMEASURED" in g["blocking"])

    # AN UNWAIVED WARN MUST BLOCK — the default is to stop, not to wave through.
    g = build_release_gate(green + [ck("W", "WARN", "WARN")], cfg, "2026-09-02")
    check("an unwaived standing WARN blocks", "WARNS_OWNED" in g["blocking"])

    cfg_w = dict(cfg, standing_waivers=[{"check_id": "W", "owner": "Leonard",
                                         "reason": "r", "accept_until": "2026-12-31"}])
    g = build_release_gate(green + [ck("W", "WARN", "WARN")], cfg_w, "2026-09-02")
    check("a WARN with a live waiver does not block", g["status"] == "PASS")

    g = build_release_gate(green + [ck("W", "WARN", "WARN")], cfg_w, "2027-01-01")
    check("the same waiver blocks again once its accept_until has passed",
          "WARNS_OWNED" in g["blocking"])

    cfg_m = dict(cfg, manual_checks=[{"id": "M", "label": "m", "max_age_days": 14}])
    g = build_release_gate(green, cfg_m, "2026-09-02")
    check("a manual check never verified is NOT_MET, not absent",
          "M" in g["blocking"] and any(c["id"] == "M" for c in g["criteria"]))

    cfg_m2 = dict(cfg, manual_checks=[{"id": "M", "label": "m", "max_age_days": 14,
                                       "verified_at": "2026-09-01",
                                       "verified_by": "Leonard"}])
    check("a fresh manual attestation is MET",
          build_release_gate(green, cfg_m2, "2026-09-02")["status"] == "PASS")
    check("a stale manual attestation blocks again",
          "M" in build_release_gate(green, cfg_m2, "2026-10-01")["blocking"])
    check("the shipped gate config parses and declares manual checks",
          len(json.loads(GATE_FILE.read_text(encoding="utf-8"))["manual_checks"]) >= 6)

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--cache", default="", help="reuse a local chunk dump")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.check:
        ap.print_help()
        return 2

    cache = Path(args.cache) if args.cache else None
    print("fetching store…", flush=True)
    chunks = fetch_chunks(cache)
    print(f"  {len(chunks)} chunks", flush=True)

    try:
        health = http_json(HEALTH_URL, timeout=90)
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"  /health unreachable: {e}", file=sys.stderr)
        health = None

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry = reg["sources"] if isinstance(reg, dict) and "sources" in reg else reg
    knowledge = json.loads((REPO_ROOT / "knowledge.json").read_text(encoding="utf-8"))
    guidelines = json.loads((REPO_ROOT / "guidelines.json").read_text(encoding="utf-8"))

    rep = build_report(chunks, health, registry, knowledge, guidelines,
                       guidelines_registry_count(), latest_eval_run())
    Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")

    print(f"\noverall: {rep['overallStatus']}   {rep['counts']}")
    for c in rep["checks"]:
        mark = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ",
                "NOT_MEASURED": "❔", "INFO": "ℹ️ "}.get(c["status"], "?")
        print(f"  {mark} [{c['severity']:<7}] {c['id']:<22} {c['detail'][:96]}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
