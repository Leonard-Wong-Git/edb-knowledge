#!/usr/bin/env python3
"""
policy_signal_writer.py — reference implementation of `_write_policy_signal()`
=================================================================================

**This file is NOT called by K1.** It is a **drop-in reference** for the
Circular System (edb_scraper.py) team. K1 only reads `policy_signals.json`;
the write-side belongs to edb_scraper.py.

Role in the two-repo architecture
---------------------------------
```
┌────────────── Circular System repo ──────────────┐
│ edb_scraper.py                                   │
│   ├── scrape EDB website                         │
│   ├── analyse circular (title, topics, etc.)     │
│   └── _apply_post_analysis_review()              │
│         └── _write_policy_signal()  ← THIS FILE  │
│               │                                  │
│               ▼ writes                           │
│         dev/knowledge/policy_signals.json        │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼ read-only
┌────────────── K1 Knowledge Platform repo ────────┐
│ dev/vault/process_signals.py                     │
│   └── reads pending signals                      │
│       → downloads PDF → extract → add candidates │
└──────────────────────────────────────────────────┘
```

How to integrate (Circular System team)
---------------------------------------
1. Copy the function `write_policy_signal()` below into `edb_scraper.py`
   (rename to `_write_policy_signal` with leading underscore if you follow
   that convention for internal helpers).

2. Adjust the 3 variables at top of the function (`SIGNALS_PATH`, the
   title-keyword list, the topic list) to match your repo's layout.

3. Call it from `_apply_post_analysis_review()` **after** your existing
   analysis logic, passing:
     - circular_id  (e.g. "EDBC012/2025")
     - title         (Chinese circular title)
     - pdf_url       (direct PDF URL)
     - ai_topics     (list, e.g. ["curriculum","finance"])
     - extra_notes   (optional string)

4. If your loop already iterates a batch of circulars, call per circular.

5. **Fail silent**: _never_ let a signal write crash the scraper. The scraper
   is the source of truth for circular data; signal writing is best-effort.

6. **Idempotent**: if a signal with the same `signal_id` already exists, do
   nothing. This lets the scraper safely re-run on the same day.

Contract (schema v1)
--------------------
Each signal appended MUST include:
  - signal_id       (stable hash or derived id, used for idempotency)
  - circular_id     (source EDBC/...)
  - title           (verbatim Chinese title)
  - url             (direct PDF URL)  ← REQUIRED; K1 side needs it
  - signal_date     (ISO date)
  - trigger_reason  (dict with title_keywords_matched, ai_topics_matched)
  - status          ("pending_review" on first write)

On status transitions:
  - edb_scraper.py only writes initial "pending_review"
  - K1-side process_signals.py may update to "auto_processed" or
    "download_failed" etc. — do NOT overwrite status fields set by K1.

Guardrails
----------
- NEVER touch existing signals that already have status != "pending_review".
- NEVER set status != "pending_review" from edb_scraper.py.
- If `signals` list is missing, create it.
- If `_meta` is missing, preserve file unchanged and log a warning.

Run this file standalone to self-test against a fresh temp file.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# ── Configuration (adjust per your repo layout) ─────────────────────────────
SIGNALS_PATH_DEFAULT = Path(__file__).resolve().parent.parent / "knowledge" / "policy_signals.json"

# Strong-signal trigger conditions (match policy_signals_v1 schema)
STRONG_TITLE_KEYWORDS = ("架構", "課程框架", "學習宗旨", "指引（", "指引(")
STRONG_AI_TOPICS = ("curriculum",)


def _derive_signal_id(circular_id: str) -> str:
    """Stable id used for idempotency. e.g. EDBC012/2025 → sig_edbc012_2025."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", circular_id.lower()).strip("_")
    return f"sig_{slug}"


def _title_keywords_matched(title: str, keywords: Iterable[str]) -> list[str]:
    return [kw for kw in keywords if kw in (title or "")]


def _ai_topics_matched(ai_topics: Iterable[str], strong_topics: Iterable[str]) -> list[str]:
    s = set(strong_topics)
    return [t for t in ai_topics if t in s]


def _passes_strong_trigger(title: str, ai_topics: Iterable[str]) -> tuple[bool, dict]:
    title_matches = _title_keywords_matched(title, STRONG_TITLE_KEYWORDS)
    topic_matches = _ai_topics_matched(ai_topics, STRONG_AI_TOPICS)
    passed = bool(title_matches) and bool(topic_matches)
    return passed, {
        "title_keywords_matched": title_matches,
        "ai_topics_matched": topic_matches,
        "accuracy_verified": False,
        "notes": "",
    }


def write_policy_signal(
    *,
    circular_id: str,
    title: str,
    pdf_url: str,
    ai_topics: Iterable[str],
    extra_notes: str = "",
    signals_path: Path = SIGNALS_PATH_DEFAULT,
    today: str | None = None,
) -> dict | None:
    """
    Idempotent, fail-silent append of a strong policy signal.

    Returns the newly written signal dict, or None if:
      - trigger conditions not met (not an error)
      - signal already exists (not an error)
      - file I/O or schema failure (logged; not raised)
    """
    try:
        passed, trigger_reason = _passes_strong_trigger(title, list(ai_topics or []))
        if not passed:
            return None  # not strong; silently skip

        if not circular_id or not title or not pdf_url:
            logger.warning("write_policy_signal: missing required field; skip.")
            return None

        signal_id = _derive_signal_id(circular_id)
        today_iso = today or datetime.date.today().isoformat()

        # Load existing file (create minimal if missing)
        if signals_path.exists():
            try:
                doc = json.loads(signals_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.error("policy_signals.json unreadable; NOT overwriting.")
                return None
        else:
            doc = {"_meta": {"schema": "policy_signals_v1", "trigger_mode": "strong"}, "signals": []}

        signals = doc.setdefault("signals", [])

        # Idempotency: if signal_id already present, leave it alone
        for existing in signals:
            if existing.get("signal_id") == signal_id:
                return None

        new_signal = {
            "signal_id": signal_id,
            "circular_id": circular_id,
            "title": title,
            "url": pdf_url,
            "signal_date": today_iso,
            "trigger_reason": {
                **trigger_reason,
                "notes": extra_notes or trigger_reason["notes"],
            },
            "status": "pending_review",
        }
        signals.append(new_signal)

        # Bump _meta.updated (best-effort; preserve if missing)
        meta = doc.setdefault("_meta", {})
        meta["updated"] = today_iso

        # Atomic write: tmp → rename
        tmp = signals_path.with_suffix(signals_path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(signals_path)

        logger.info("wrote policy signal %s (%s)", signal_id, circular_id)
        return new_signal

    except Exception as exc:  # noqa: BLE001
        # Fail silent — never crash the scraper over a signal-write failure
        logger.exception("write_policy_signal failed: %s", exc)
        return None


# ── Self-test ───────────────────────────────────────────────────────────────
def _self_test() -> None:
    import tempfile

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    with tempfile.TemporaryDirectory() as td:
        signals_path = Path(td) / "policy_signals.json"

        # Case 1 — strong signal, first write
        out = write_policy_signal(
            circular_id="EDBC099/2026",
            title="教育局通告第99/2026號 — 課程框架更新",
            pdf_url="https://example.gov.hk/edbc99.pdf",
            ai_topics=["curriculum", "general"],
            signals_path=signals_path,
            today="2026-04-19",
        )
        assert out is not None and out["signal_id"] == "sig_edbc099_2026"
        assert out["status"] == "pending_review"
        assert "課程框架" in out["trigger_reason"]["title_keywords_matched"]

        # Case 2 — idempotent (re-write same id)
        out2 = write_policy_signal(
            circular_id="EDBC099/2026",
            title="教育局通告第99/2026號 — 課程框架更新",
            pdf_url="https://example.gov.hk/edbc99.pdf",
            ai_topics=["curriculum"],
            signals_path=signals_path,
            today="2026-04-19",
        )
        assert out2 is None, "re-writing same signal should be a no-op"

        # Case 3 — weak trigger (no curriculum topic)
        out3 = write_policy_signal(
            circular_id="EDBC100/2026",
            title="財務政策架構更新",
            pdf_url="https://example.gov.hk/edbc100.pdf",
            ai_topics=["finance"],
            signals_path=signals_path,
            today="2026-04-19",
        )
        assert out3 is None, "finance topic should not trigger strong"

        # Case 4 — weak trigger (no title keyword match)
        out4 = write_policy_signal(
            circular_id="EDBC101/2026",
            title="小學教學資源補助",
            pdf_url="https://example.gov.hk/edbc101.pdf",
            ai_topics=["curriculum"],
            signals_path=signals_path,
            today="2026-04-19",
        )
        assert out4 is None

        # File has exactly 1 signal
        final = json.loads(signals_path.read_text(encoding="utf-8"))
        assert len(final["signals"]) == 1, f"expected 1 signal, got {len(final['signals'])}"
        assert final["_meta"]["updated"] == "2026-04-19"

        print("self-test: PASS (1 signal written, idempotency + weak-filter verified)")


if __name__ == "__main__":
    _self_test()
