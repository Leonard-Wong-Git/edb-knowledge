#!/usr/bin/env python3
"""
check_expiry.py
===============
Expiry sweep — the 6th monitor (S209). Finds ingested material whose reference
value has run out, and (behind a manual tick) removes it.

Where it sits among the other monitors:
  check_freshness     "did the upstream bytes change?"        — registry URLs
  check_served_urls   "does the link a user clicks work?"     — wiki_chunks.url
  discover_sources    "is there something we haven't got?"    — EDB index pages
  check_source_titles "is this the document we think it is?"  — PDF covers
  check_new_circulars "is there a new circular?"              — dashboard feed
  check_expiry        "should this still be in the corpus?"   — registry lifecycle

None of the other five can see this class. A briefing-session circular stays
200, keeps its bytes, keeps its title, and keeps answering questions with a
registration deadline that closed months ago. The S209 case that started it:
the 2026-06-07 BLNST sitting notes were still being served in late August, with
`截止申請日期：2026年4月30日` in the text, from a URL EDB had already withdrawn.

Detection is automatic; removal is not. `--check` only reports. `--purge` acts
on an explicit source list and refuses anything that is not both marked
`lifecycle: ephemeral` AND past its `expires_on` — so a mis-tick cannot delete a
guideline, and neither can a bug in the classifier.

Deletion is genuinely irreversible in this corpus: chunk ids are content hashes,
so a purged source can only come back through a full re-ingest.

Usage (from repo root):
  python3 dev/source/check_expiry.py --self-test          # offline, no network
  python3 dev/source/check_expiry.py --prove-assertions   # prove the tests go red
  python3 dev/source/check_expiry.py --check              # report expired sources
  python3 dev/source/check_expiry.py --check --changes-out expiry.json --ledger expiry.md
  python3 dev/source/check_expiry.py --classify           # propose fields for existing sources
  python3 dev/source/check_expiry.py --purge --sources a,b   # delete (needs service key)

Keys: `--check` / `--classify` need none (registry is local); a live chunk count
uses SUPABASE_ANON_KEY if present. `--purge` requires SUPABASE_SERVICE_KEY.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lifecycle as lc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "dev" / "source" / "source_registry.json"
BACKEND_ENV = REPO_ROOT / "backend" / ".env"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://youkcekbrbywuqjxgibe.supabase.co")
TABLE = "wiki_chunks"


# ── registry IO ──────────────────────────────────────────────────────────────
def load_registry() -> Dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(doc: Dict) -> None:
    """Write back in the exact formatting the file already uses, so a one-field
    change produces a one-line diff instead of a whole-file reformat."""
    REGISTRY_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")


def load_key(*names: str) -> str:
    for var in names:
        v = (os.environ.get(var) or "").strip()
        if v:
            return v
    if BACKEND_ENV.exists():
        for line in BACKEND_ENV.read_text(encoding="utf-8").splitlines():
            for var in names:
                if line.strip().startswith(var + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def chunk_count(source_id: str, key: str) -> Optional[int]:
    if not key:
        return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                         headers={"apikey": key, "Authorization": f"Bearer {key}",
                                  "Range-Unit": "items", "Range": "0-0",
                                  "Prefer": "count=exact"},
                         params={"select": "id", "source_id": f"eq.{source_id}"}, timeout=40)
        cr = r.headers.get("content-range", "")
        return int(cr.split("/")[-1]) if "/" in cr else None
    except Exception:                                        # noqa: BLE001
        return None


# ── pure selection ───────────────────────────────────────────────────────────
def expired_entries(sources: List[Dict], today: Optional[date] = None) -> List[Dict]:
    """Sources safe to offer for purge: marked ephemeral, dated, date in the past.

    Already-deprecated entries are still listed — a source can be marked retired
    in the registry while its chunks are still live, which is exactly the state
    a half-finished cleanup leaves behind.
    """
    return [s for s in sources if lc.is_expired(s, today)]


def expiring_soon(sources: List[Dict], within_days: int = 30,
                  today: Optional[date] = None) -> List[Dict]:
    """Ephemeral sources that will expire within the window — advance warning so
    an expiry is never a surprise on the day it fires."""
    t = today or date.today()
    horizon = t + timedelta(days=within_days)
    out = []
    for s in sources:
        if s.get("lifecycle") != "ephemeral":
            continue
        when = lc._parse_date(s.get("expires_on"))
        if when and t <= when <= horizon:
            out.append(s)
    return out


def render_ledger(expired: List[Dict], soon: List[Dict], today: str) -> str:
    lines = [
        "# 過期資料待清走",
        "",
        "<!-- AUTO-GENERATED by dev/source/check_expiry.py --ledger. Do not hand-edit. -->",
        "",
        f"- Last sweep: **{today}** (UTC)",
        f"- 待清走：**{len(expired)}** · 30 日內到期：{len(soon)}",
        "",
        "> 只列出 registry 明確標住 `lifecycle: ephemeral` 而且 `expires_on` 已過嘅源。",
        "> 指引／規例／年度版本文件永遠唔會出現喺呢度。刪除係人手閘，唔會自動執行。",
        "",
    ]
    if not expired:
        lines.append("_冇過期資料待清走。_")
    else:
        lines.append("| source_id | 標題 | 到期日 | chunks | 依據 |")
        lines.append("|---|---|---|---|---|")
        for e in expired:
            lines.append(f"| `{e['source_id']}` | {(e.get('title') or '')[:40]} | "
                         f"{e.get('expires_on')} | {e.get('chunks', '?')} | "
                         f"{(e.get('expiry_basis') or '')[:60]} |")
    if soon:
        lines.append("")
        lines.append(f"### 30 日內到期（{len(soon)}）")
        for e in soon:
            lines.append(f"- `{e['source_id']}` — {(e.get('title') or '')[:50]} · {e.get('expires_on')}")
    return "\n".join(lines) + "\n"


# ── self-test ────────────────────────────────────────────────────────────────
FAILS: List[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        FAILS.append(label)


def run_self_test(classify, is_expired) -> int:
    TODAY = date(2026, 8, 24)

    def pkg(title, tier=None, deadlines=()):
        return {"title": title, "proposed": {"tier": tier},
                "dashboard_signals": {"deadlines": [{"date": d} for d in deadlines]}}

    print("classify() — the ephemeral class:")
    r = classify(pkg("「中小學人工智能教育學生培訓計劃 2026/27」學習活動", tier=3,
                     deadlines=["2026-09-15"]))
    check("a tier-3 training programme with a deadline is ephemeral",
          r["lifecycle"] == "ephemeral")
    check("expiry is the last deadline plus the grace period",
          r["expires_on"] == "2026-10-15")
    r = classify(pkg("行政長官卓越教學獎（2026/2027） 最後籲請提名", deadlines=["2026-10-31"]))
    check("an award nomination is ephemeral on its keyword alone (no tier)",
          r["lifecycle"] == "ephemeral" and r["expires_on"] == "2026-11-30")
    r = classify(pkg("測試（非學位程度）(2026 年6 月)申請人須知", tier=3,
                     deadlines=["2026-04-30", "2026-06-07"]))
    check("the LAST deadline wins, not the first",
          r["expires_on"] == "2026-07-07")

    print("classify() — everything that must survive:")
    r = classify(pkg("學校行政手冊", tier=3, deadlines=["2026-01-01"]))
    check("a durable document type is never ephemeral, even at tier 3",
          r["lifecycle"] != "ephemeral" and r["expires_on"] is None)
    r = classify(pkg("資助則例（2026/27）", tier=3, deadlines=["2026-01-01"]))
    check("a durable document naming a year is a dated_edition, not ephemeral",
          r["lifecycle"] == "dated_edition" and r["expires_on"] is None)
    check("its covered period is recorded", r["covers_period"] == "2026/27")
    r = classify(pkg("教師專業發展課程簡介會", tier=3))
    check("an occasion with NO extractable date is kept, not guessed at",
          r["lifecycle"] != "ephemeral" and r["expires_on"] is None)
    r = classify(pkg("資訊及通訊科技 (中四至中六) (於2022/23學年實施並在2025年及以後的香港中學文憑考試生效)",
                     deadlines=["2026-01-01"]))
    check("HKDSE named in a curriculum document is not an occasion "
          "(S209 backfill false positive)", r["lifecycle"] != "ephemeral")
    r = classify(pkg("「我的行動承諾」（2026/27）", tier=3))
    check("a dateless occasion that names a school year is a dated_edition",
          r["lifecycle"] == "dated_edition" and r["covers_period"] == "2026/27")
    r = classify(pkg("小學數學科課程配套資料"))
    check("an ordinary document is reference", r["lifecycle"] == "reference")
    r = classify(pkg("學與教材料 (二零二六年八月)", tier=1, deadlines=["2026-01-01"]))
    check("tier-1 with a deadline is still not ephemeral",
          r["lifecycle"] != "ephemeral")

    print("is_expired() — the guard the purge relies on:")
    check("ephemeral + past date → expired",
          is_expired({"lifecycle": "ephemeral", "expires_on": "2026-07-07"}, TODAY))
    check("ephemeral + future date → not expired",
          not is_expired({"lifecycle": "ephemeral", "expires_on": "2026-12-01"}, TODAY))
    check("ephemeral + expiring exactly today → not yet expired",
          not is_expired({"lifecycle": "ephemeral", "expires_on": "2026-08-24"}, TODAY))
    check("ephemeral with NO date is never expired",
          not is_expired({"lifecycle": "ephemeral"}, TODAY))
    check("ephemeral with an unparseable date is never expired",
          not is_expired({"lifecycle": "ephemeral", "expires_on": "soon"}, TODAY))
    check("a dated_edition is never expired, however old",
          not is_expired({"lifecycle": "dated_edition", "expires_on": "2001-01-01"}, TODAY))
    check("a reference source is never expired",
          not is_expired({"lifecycle": "reference", "expires_on": "2001-01-01"}, TODAY))
    check("a source with no lifecycle field is never expired",
          not is_expired({"expires_on": "2001-01-01"}, TODAY))

    print("selection over a registry:")
    sources = [
        {"source_id": "gone", "lifecycle": "ephemeral", "expires_on": "2026-01-01"},
        {"source_id": "soon", "lifecycle": "ephemeral", "expires_on": "2026-09-10"},
        {"source_id": "guide", "lifecycle": "reference"},
        {"source_id": "rates", "lifecycle": "dated_edition", "covers_period": "2026/27"},
    ]
    check("expired_entries picks only the past-dated ephemeral",
          [s["source_id"] for s in expired_entries(sources, TODAY)] == ["gone"])
    check("expiring_soon warns ahead without selecting the already-expired",
          [s["source_id"] for s in expiring_soon(sources, 30, TODAY)] == ["soon"])

    print("registry reality check:")
    reg = load_registry()["sources"]
    marked = [s for s in reg if s.get("lifecycle")]
    check(f"registry carries lifecycle marks ({len(marked)} source(s))", len(marked) >= 1)
    bad = [s["source_id"] for s in reg
           if s.get("lifecycle") == "ephemeral" and not s.get("expires_on")]
    check(f"no ephemeral source lacks an expires_on (offenders: {bad or 'none'})", not bad)

    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED: " + "; ".join(FAILS))
        return 1
    print("ALL PASS")
    return 0


# ── modes ────────────────────────────────────────────────────────────────────
def do_check(args) -> int:
    today = date.today()
    sources = load_registry()["sources"]
    key = load_key("SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY")

    expired = [dict(s) for s in expired_entries(sources, today)]
    soon = [dict(s) for s in expiring_soon(sources, args.within, today)]
    for e in expired:
        e["chunks"] = chunk_count(e["source_id"], key)

    # An expired source whose chunks are already gone is DONE, not pending. It
    # stays in the registry as the record of what was removed, but it must not
    # sit on the action list for ever — that is exactly how a decision surface
    # becomes unreadable.
    done = [e for e in expired if e.get("chunks") == 0]
    live = [e for e in expired if (e.get("chunks") or 0) > 0]
    print(f"🗓  Expiry sweep | {today.isoformat()} (UTC)")
    print(f"   registry: {len(sources)} sources · "
          f"ephemeral marked: {sum(1 for s in sources if s.get('lifecycle') == 'ephemeral')}")
    print("-" * 60)
    print(f"   待清走：{len(live)} · 已清走（留低記錄）：{len(done)} · "
          f"{args.within} 日內到期：{len(soon)}")
    for e in live:
        print(f"  🗑  {e['source_id']:34} exp {e.get('expires_on')}  chunks={e.get('chunks')}  "
              f"{(e.get('title') or '')[:34]}")
    for e in soon:
        print(f"  ⏳ {e['source_id']:34} exp {e.get('expires_on')}  {(e.get('title') or '')[:34]}")

    report = {
        "generated_at": today.isoformat(),
        "registry_sources": len(sources),
        "expired": len(expired),
        "expired_with_chunks": len(live),
        "already_purged": len(done),
        "expiring_soon": len(soon),
        "expired_sources": [{k: e.get(k) for k in
                             ("source_id", "title", "expires_on", "expiry_basis", "chunks")}
                            for e in live],
        "soon_sources": [{k: e.get(k) for k in ("source_id", "title", "expires_on")}
                         for e in soon],
    }
    if args.changes_out:
        Path(args.changes_out).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
        print(f"\n📄 Report: {args.changes_out}")
    if args.ledger:
        Path(args.ledger).write_text(render_ledger(live, soon, today.isoformat()),
                                     encoding="utf-8")
        print(f"📋 Ledger: {args.ledger}")
    # Detection never fails the build — same signal routing as the sibling
    # monitors (S126): content findings go to the Issue, not the exit code.
    return 0


def do_classify(args) -> int:
    """Propose lifecycle fields for sources that have none. Report only —
    backfilling 270 sources by machine judgement is exactly the kind of bulk
    guess that should be read before it is written."""
    sources = load_registry()["sources"]
    unmarked = [s for s in sources if not s.get("lifecycle")]
    print(f"unmarked sources: {len(unmarked)} / {len(sources)}")
    proposals = []
    for s in unmarked:
        # A registry row is not an ingest package: it has no tier and no
        # extracted deadlines, so only the title-shaped rules can fire. That is
        # deliberate — it can propose dated_edition and reference, and it can
        # never propose ephemeral without a date to stand on.
        r = lc.classify({"title": s.get("title"), "proposed": {}, "dashboard_signals": {}})
        if r["lifecycle"] != "reference" or r["covers_period"]:
            proposals.append({"source_id": s["source_id"], "title": s.get("title"), **r})
    print(f"proposals (non-default): {len(proposals)}")
    for p in proposals[:args.limit or len(proposals)]:
        print(f"  {p['lifecycle']:14} {p['source_id']:32} {(p.get('covers_period') or '-'):9} "
              f"{(p.get('title') or '')[:40]}")
    if args.changes_out:
        Path(args.changes_out).write_text(json.dumps(proposals, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
        print(f"\n📄 Proposals: {args.changes_out}")
    if not args.apply:
        print("\n(report only — re-run with --apply to write these to the registry)")
        return 0

    # Backfill is write-once and additive: it only ever fills a field that is
    # absent, and it can only ever write `reference` / `dated_edition`. A
    # registry row carries no tier and no extracted deadlines, so this path
    # cannot produce `ephemeral` — asserted rather than assumed, because the
    # difference between the two is the difference between marking and deleting.
    doc = load_registry()
    by_id = {x["source_id"]: x for x in doc["sources"]}
    written = 0
    for prop in proposals:
        assert prop["lifecycle"] != "ephemeral", (
            f"backfill proposed ephemeral for {prop['source_id']} — refusing; "
            "an expiry must come from an ingest package with real deadlines")
        row = by_id[prop["source_id"]]
        if row.get("lifecycle"):
            continue
        row["lifecycle"] = prop["lifecycle"]
        row["expires_on"] = None
        row["expiry_basis"] = prop["expiry_basis"]
        row["covers_period"] = prop["covers_period"]
        written += 1
    save_registry(doc)
    print(f"\n✅ wrote lifecycle fields to {written} registry entries "
          f"(expires_on left null — nothing backfilled becomes sweepable)")
    return 0


def do_purge(args) -> int:
    if not args.sources:
        print("❌ --purge needs --sources a,b,c")
        return 2
    key = load_key("SUPABASE_SERVICE_KEY")
    if not key:
        print("❌ SUPABASE_SERVICE_KEY required for --purge")
        return 2
    doc = load_registry()
    by_id = {s["source_id"]: s for s in doc["sources"]}
    today = date.today()
    wanted = [x.strip() for x in args.sources.split(",") if x.strip()]

    approved, refused = [], []
    for sid in wanted:
        s = by_id.get(sid)
        if s is None:
            refused.append((sid, "not in registry"))
        elif s.get("lifecycle") != "ephemeral":
            refused.append((sid, f"lifecycle={s.get('lifecycle') or 'unset'}, not ephemeral"))
        elif not lc.is_expired(s, today):
            refused.append((sid, f"not expired (expires_on={s.get('expires_on')})"))
        else:
            approved.append(sid)

    for sid, why in refused:
        print(f"  ⛔ {sid}: refused — {why}")
    if not approved:
        print("nothing to purge")
        return 1 if refused else 0

    for sid in approved:
        before = chunk_count(sid, key)
        print(f"\n=== {sid}  ({before} chunks)  exp {by_id[sid].get('expires_on')}")
        if not args.apply:
            print("    [dry-run] would DELETE and mark the registry entry deprecated")
            continue
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                            headers={"apikey": key, "Authorization": f"Bearer {key}",
                                     "Content-Type": "application/json"},
                            params={"source_id": f"eq.{sid}"}, timeout=60)
        if not r.ok:
            print(f"    ❌ DELETE {r.status_code}: {r.text[:200]}")
            return 1
        after = chunk_count(sid, key)
        print(f"    ✅ deleted; chunks remaining: {after}")
        if after:
            print("    ❌ rows survived the delete — stopping")
            return 1
        entry = by_id[sid]
        entry["status"] = "deprecated"
        entry["notes"] = (entry.get("notes") or "") + (
            f" | expiry sweep {today.isoformat()}: purged {before} chunk(s), "
            f"expired {entry.get('expires_on')} ({entry.get('expiry_basis')}).")
    if args.apply:
        save_registry(doc)
        print("\nregistry updated (status=deprecated on the purged entries)")
        print("⚠️  Re-anchor the published chunk count before committing:")
        print("    python3 -c \"import sys;sys.path.insert(0,'dev/source');import execute_ingest as e;"
              "print(e.live_display_sync(e.current_chunk_total(), e.live_total_count()))\"")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--prove-assertions", action="store_true",
                    help="replace the rules with no-ops; the tests must go red")
    ap.add_argument("--check", action="store_true", help="report expired / expiring sources")
    ap.add_argument("--classify", action="store_true",
                    help="propose lifecycle fields for unmarked sources (report only)")
    ap.add_argument("--purge", action="store_true", help="delete named expired sources")
    ap.add_argument("--sources", help="comma-separated source_ids for --purge")
    ap.add_argument("--apply", action="store_true", help="--purge writes (default is dry-run)")
    ap.add_argument("--within", type=int, default=30, help="advance-warning window in days")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--changes-out")
    ap.add_argument("--ledger")
    args = ap.parse_args()

    if args.prove_assertions:
        print("PROVE MODE — rules replaced with no-ops; failures are the point.\n")
        classify = lambda p: {"lifecycle": "reference", "expires_on": None,      # noqa: E731
                              "expiry_basis": None, "covers_period": None}
        is_expired = lambda e, t=None: True                                      # noqa: E731
        run_self_test(classify, is_expired)
        ok = len(FAILS) >= 13
        print(f"\n{'ALL PASS' if ok else 'BROKEN'} — {len(FAILS)} assertions fired against the "
              f"no-op rules (expected ≥ 13).")
        return 0 if ok else 1
    if args.self_test:
        return run_self_test(lc.classify, lc.is_expired)
    if args.check:
        return do_check(args)
    if args.classify:
        return do_classify(args)
    if args.purge:
        return do_purge(args)
    ap.error("nothing to do: pass --self-test / --check / --classify / --purge")


if __name__ == "__main__":
    raise SystemExit(main())
