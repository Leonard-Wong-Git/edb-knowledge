#!/usr/bin/env python3
"""_s213_title_backfill.py — give the 658 code-titled chunks their real document name.

WHY THIS EXISTS (root cause, proven S213):
`dev/vault/build_wiki_index.py:267-268` reads the `# title:` / `# url:` header
lines off each vault extract and falls back SILENTLY when they are absent:

    "title": meta.get("title", source_id),
    "url":   meta.get("url", ""),

19 extract files have no `# title:` header. The set of source_ids serving a
code title in the store is EXACTLY that set of 19 — intersection 19, neither
side has a member the other lacks. That is the causal chain, not a correlation.
1 of the 19 lost its headers to `repage_pdfs.py`; the other 18 are stat_*
extracts whose writers never emitted the headers at all.

This script repairs the SERVED rows. The extract headers and the silent
fallback are repaired separately — a backfill alone would be undone by the
next rebuild.

SAFE BY CONSTRUCTION:
  - `title` is metadata only. `build_wiki_index.py:547` embeds `c["text"]`
    alone, so no vector is invalidated.
  - chunk `id` is `vault_<source_id>_<hash>` and `hash` is the md5 of `text`,
    so a title change moves no id (playbook: `content-hash-id-delete-set`).
  - Therefore this is an UPDATE, never a delete-then-insert.

DISCIPLINE (playbook: `dry-run-blast-radius-before-destructive-batch`):
dry-run is the default and prints a per-source blast radius for human review;
`--execute` verifies each source's post-count before moving to the next and
stops on the first mismatch, naming the source.

USAGE:
  python3 dev/_s213_title_backfill.py                # dry-run, per-source plan
  python3 dev/_s213_title_backfill.py --self-test    # assertions, no network
  python3 dev/_s213_title_backfill.py --execute      # apply, per-source verify
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT = REPO_ROOT / "dev" / "vault"
REGISTRY = REPO_ROOT / "dev" / "source" / "source_registry.json"
SUPABASE_URL = "https://youkcekbrbywuqjxgibe.supabase.co"

# `arts_kla_guide_2017` is a byte-duplicate of `g37` and is slated for deletion
# in the same session. Re-titling rows we are about to drop would be work that
# argues with itself, so it is excluded unless explicitly asked for.
SLATED_FOR_DELETION = {"arts_kla_guide_2017"}


# ---------------------------------------------------------------------------
# pure helpers (covered by --self-test)
# ---------------------------------------------------------------------------

def read_extract_meta(path: Path) -> dict[str, str]:
    """The `# key: value` header block, stopping at the first non-header line."""
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("# "):
            break
        m = re.match(r"^#\s+(\w+):\s*(.+)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta


def enrolment_title(school_year: str) -> str:
    """`2014/15` -> the registry parent's name carrying that year.

    The parent `stat_enrolment_report` is registered as
    「學生人數統計報告書（年度系列）」, so each annual file is that name with the
    series placeholder replaced by the year the document itself declares. The
    year comes from the extract's `# school_year:` header, never from the
    source_id — the id is what we are trying to stop showing people.
    """
    if not re.fullmatch(r"\d{4}/\d{2}", school_year):
        raise ValueError(f"unexpected school_year: {school_year!r}")
    return f"學生人數統計報告書（{school_year} 學年）"


def is_code_title(title: str | None, source_id: str) -> bool:
    return (title or "").strip() == source_id


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------

def build_plan(include_deletion_slated: bool) -> list[dict]:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_id = {s["source_id"]: s for s in reg.get("sources", [])}

    plan: list[dict] = []
    for path in sorted(VAULT.rglob("*.txt")):
        meta = read_extract_meta(path)
        sid = meta.get("source_id")
        if not sid or "title" in meta:
            continue  # only the headerless extracts produce code titles
        if sid in SLATED_FOR_DELETION and not include_deletion_slated:
            continue

        title = url = None
        why = ""
        if sid.startswith("stat_enrolment_") and "school_year" in meta:
            title = enrolment_title(meta["school_year"])
            url = meta.get("url")
            why = "extract # school_year + registry parent stat_enrolment_report"
        elif sid in by_id:
            title = by_id[sid].get("title")
            url = meta.get("url") or by_id[sid].get("url_primary")
            why = "source_registry entry for this id"
        elif sid == "stat_integrated":
            # The extract sits in `stat_integrated_edu/` but its header declares
            # `stat_integrated`, so the registry has never seen this id. The
            # registered sibling describes the same spreadsheet.
            sib = by_id.get("stat_integrated_edu", {})
            title = sib.get("title")
            url = meta.get("url") or sib.get("url_primary")
            why = "registered sibling stat_integrated_edu (id mismatch, see report)"

        plan.append({
            "source_id": sid, "extract": str(path.relative_to(REPO_ROOT)),
            "title": title, "url": url, "why": why,
            "has_url_header": "url" in meta,
        })
    return plan


# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------

def service_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if key:
        return key
    env = REPO_ROOT / "backend" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("SUPABASE_SERVICE_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Missing SUPABASE_SERVICE_KEY (env or backend/.env)")


def _req(method: str, path: str, key: str, body: dict | None = None,
         prefer: str | None = None) -> tuple[int, str, dict]:
    headers = {"apikey": key, "Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{SUPABASE_URL}{path}", data=data,
                                 headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode("utf-8"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers)


def count_code_titled(sid: str, key: str) -> int:
    """Rows of this source whose title is still literally the source_id."""
    q = urllib.parse.urlencode({"select": "id", "source_id": f"eq.{sid}",
                                "title": f"eq.{sid}"})
    status, body, hdrs = _req("GET", f"/rest/v1/wiki_chunks?{q}", key,
                              prefer="count=exact")
    if status >= 300:
        raise RuntimeError(f"count failed for {sid}: {status} {body[:200]}")
    rng = hdrs.get("Content-Range", "")
    return int(rng.split("/")[-1]) if "/" in rng else len(json.loads(body))


def patch_source(sid: str, title: str, url: str | None, key: str) -> int:
    patch: dict[str, str] = {"title": title}
    if url:
        patch["url"] = url
    q = urllib.parse.urlencode({"source_id": f"eq.{sid}", "title": f"eq.{sid}"})
    status, body, _ = _req("PATCH", f"/rest/v1/wiki_chunks?{q}", key, patch,
                           prefer="return=representation")
    if status >= 300:
        raise RuntimeError(f"PATCH failed for {sid}: {status} {body[:300]}")
    return len(json.loads(body))


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    fails: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    check("enrolment_title 用學年而非 source_id",
          enrolment_title("2014/15") == "學生人數統計報告書（2014/15 學年）")
    bad = False
    try:
        enrolment_title("stat_enrolment_2014")
    except ValueError:
        bad = True
    check("enrolment_title 拒絕非學年輸入（證明會紅）", bad)
    check("is_code_title 認得代號標題", is_code_title("stat_kg", "stat_kg"))
    check("is_code_title 不誤判真標題",
          not is_code_title("幼稚園統計數字", "stat_kg"))
    check("is_code_title 對 None 安全", not is_code_title(None, "stat_kg"))

    plan = build_plan(include_deletion_slated=True)
    ids = {p["source_id"] for p in plan}
    check(f"計劃覆蓋 19 個缺 header 的來源（實得 {len(ids)}）", len(ids) == 19)
    check("每項都解析到標題", all(p["title"] for p in plan))
    check("計劃內無任何標題等於自己的 source_id",
          all(p["title"] != p["source_id"] for p in plan))
    check("13 個學生人數分年檔全部在內",
          len([p for p in plan if p["source_id"].startswith("stat_enrolment_")]) == 13)
    check("預設排除待刪的 arts_kla_guide_2017",
          "arts_kla_guide_2017" not in
          {p["source_id"] for p in build_plan(include_deletion_slated=False)})

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--include-deletion-slated", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    plan = build_plan(args.include_deletion_slated)
    unresolved = [p for p in plan if not p["title"]]
    if unresolved:
        print("STOP — 這些來源解析不到標題，不會動它們：")
        for p in unresolved:
            print(f"  {p['source_id']}  ({p['extract']})")
        return 1

    key = service_key()
    print(f"{'EXECUTE' if args.execute else 'DRY-RUN'} — 逐來源影響面\n")
    print(f"{'來源':<26}{'現時':>6}{'將改':>6}  新標題 / 連結")
    print("-" * 100)
    total_before = total_changed = 0
    for p in plan:
        sid = p["source_id"]
        before = count_code_titled(sid, key)
        total_before += before
        url_note = "＋補連結" if (p["url"] and not p["has_url_header"]) else ""
        print(f"{sid:<26}{before:>6}{before:>6}  {p['title']} {url_note}")
        print(f"{'':<26}{'':>12}  ← {p['why']}")
        if args.execute:
            n = patch_source(sid, p["title"], p["url"], key)
            after = count_code_titled(sid, key)
            if after != 0:
                print(f"\nSTOP — {sid} 改後仍有 {after} 條代號標題，中止，未處理後續來源。")
                return 1
            total_changed += n
            print(f"{'':<26}{'':>12}  ✓ 已改 {n} 條，複查剩餘 {after}")

    print("-" * 100)
    print(f"合計：{total_before} 條代號標題"
          + (f"，實改 {total_changed} 條" if args.execute else "（未改動，這是預覽）"))
    if not args.execute:
        print("\n確認影響面無誤後，加 --execute 執行。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
