#!/usr/bin/env python3
"""
Lifecycle classification — does this source expire, and when?

The problem it solves (S209, Leonard): the corpus only ever grows, but not
everything in it stays true. Three kinds of material behave differently and had
been treated identically:

  reference      A guideline, a code of aid, a manual, a policy circular. No
                 expiry. The default, and the answer whenever the signals are
                 unclear — a wrong "keep" costs shelf space, a wrong "delete"
                 costs a source nobody can get back (chunk ids are content
                 hashes; deleting means re-ingesting to recover).

  dated_edition  The 2026/27 rates table, the school-year calendar guide. The
                 old edition is still the authority for the year it covers, so
                 it is MARKED, never deleted (this is the S204 decision, and it
                 stands). `covers_period` records which year it speaks for.

  ephemeral      A briefing session, a training course, a competition, an award
                 nomination, a test sitting, an application deadline. Once the
                 date passes it has zero reference value and answering from it
                 actively misleads — the retired 2026-06-07 BLNST sitting notes
                 were still being served in August, with a closed application
                 deadline, from a URL EDB had already withdrawn. These expire
                 and get swept (`check_expiry.py`), behind a manual tick.

What makes this cheap: the ingest package already carries the two signals that
matter. `proposed.tier` is 3 for exactly the "event/announcement keyword" class
(the S170 skip discipline), and `dashboard_signals.deadlines[]` already holds
extracted dates with a type. So an expiry date is read off existing structure
rather than guessed from prose.

Both directions of the rule fail toward KEEP:
  - no date signal            → never ephemeral, whatever the keywords say
  - a durable-document word   → never ephemeral, whatever the tier says
  - anything unrecognised     → reference

Pure functions, no I/O. Asserted in `check_expiry.py --self-test`.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

# A sitting is over on the day, but people chase results and appeals for weeks
# after. The grace period is what separates "the date passed" from "nobody will
# ever ask about this again".
GRACE_DAYS = 30

# Words that describe a one-off occasion. Leonard's list, plus the near synonyms
# EDB actually uses in circular titles.
EPHEMERAL_WORDS = [
    "簡介會", "講座", "研討會", "工作坊", "培訓班", "培訓計劃", "訓練計劃",
    "比賽", "選拔", "提名", "獎勵計劃", "報名", "截止", "名額",
    # 「測試」/「測驗」name a sitting; bare 「考試」does not — HKDSE is a standing
    # institution, and every senior-secondary curriculum document mentions it.
    # Caught on the S209 backfill: 「香港中學文憑考試」 in two curriculum guides.
    "測試", "測驗", "考生須知", "申請人須知",
    "交流計劃", "參觀", "巡迴展覽", "開放日", "頒獎",
]

# Words that mark a document as standing authority. These win over everything:
# a training-course keyword inside a guideline title must not expire the
# guideline. (A blacklist would be the wrong shape here — this is a small,
# stable set of document TYPES, not an open-ended list of bad strings.)
DURABLE_WORDS = [
    "指引", "指南", "規例", "則例", "手冊", "守則", "章則", "程序",
    "課程綱要", "課程指引", "評估架構", "政策", "法例", "條例", "架構文件",
]

# 2026/27, 2026/2027, 二零二六／二七 — the shape of a school year.
SCHOOL_YEAR = re.compile(r"(20\d{2})\s*[／/–—-]\s*(\d{2}(?:\d{2})?)")


def _parse_date(raw: Optional[str]) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime((raw or "").strip(), fmt).date()
        except ValueError:
            continue
    return None


def deadline_dates(pkg: Dict) -> List[date]:
    """Every parseable date in the package's extracted deadlines, sorted."""
    out = []
    for d in (pkg.get("dashboard_signals") or {}).get("deadlines") or []:
        parsed = _parse_date(d.get("date") if isinstance(d, dict) else None)
        if parsed:
            out.append(parsed)
    return sorted(out)


def has_word(text: str, words: List[str]) -> Optional[str]:
    for w in words:
        if w in text:
            return w
    return None


def classify(pkg: Dict) -> Dict:
    """Return {lifecycle, expires_on, expiry_basis, covers_period} for a package.

    `expires_on` is an ISO date string and is set ONLY for `ephemeral`. Callers
    must treat a missing `expires_on` as "never sweep this", not as "expired".
    """
    title = (pkg.get("title") or "")
    tier = ((pkg.get("proposed") or {}).get("tier"))
    deadlines = deadline_dates(pkg)

    result = {"lifecycle": "reference", "expires_on": None,
              "expiry_basis": None, "covers_period": None}

    year = SCHOOL_YEAR.search(title)
    if year:
        a, b = year.group(1), year.group(2)
        result["covers_period"] = f"{a}/{b[-2:]}"

    durable = has_word(title, DURABLE_WORDS)
    if durable:
        # A standing document that happens to name a year is a dated edition:
        # marked, kept, never swept (S204).
        result["lifecycle"] = "dated_edition" if year else "reference"
        result["expiry_basis"] = f"durable document type ({durable}) — never swept"
        return result

    word = has_word(title, EPHEMERAL_WORDS)
    is_event = (tier == 3) or bool(word)
    if is_event and deadlines:
        last = deadlines[-1]
        result["lifecycle"] = "ephemeral"
        result["expires_on"] = (last + timedelta(days=GRACE_DAYS)).isoformat()
        why = "tier-3 event/announcement" if tier == 3 else f"one-off occasion ({word})"
        result["expiry_basis"] = f"{why}; last deadline {last.isoformat()} + {GRACE_DAYS}d grace"
        return result

    if is_event and not deadlines:
        # Looks like an occasion but carries no date. Never guess an expiry from
        # prose — invent nothing. If it names a school year it is at least a
        # dated edition; either way it is kept.
        result["lifecycle"] = "dated_edition" if year else "reference"
        result["expiry_basis"] = ("looks one-off but carries no extractable date — "
                                  "kept; set expires_on by hand if it should expire")
        return result

    if year:
        result["lifecycle"] = "dated_edition"
        result["expiry_basis"] = f"school-year edition {result['covers_period']} — marked, not swept"
    return result


def is_expired(entry: Dict, today: Optional[date] = None) -> bool:
    """True only for an ephemeral source with a parseable date in the past.

    Every other shape — reference, dated_edition, missing lifecycle, missing or
    unparseable `expires_on` — is False. A sweep can only ever act on a source
    that was explicitly marked and explicitly dated.
    """
    if entry.get("lifecycle") != "ephemeral":
        return False
    when = _parse_date(entry.get("expires_on"))
    if when is None:
        return False
    return when < (today or date.today())
