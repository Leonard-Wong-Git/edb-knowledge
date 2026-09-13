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

# The Channel A mirror carries curated facts, not documents, so it has no
# upstream page to link to. Its rows are url-less by design and must never be
# counted as damage — otherwise every run reports 109 phantom defects and the
# real ones drown (紀律 #14: a list nobody can finish becomes wallpaper).
NO_SOURCE_URL_BY_DESIGN = {r"role_facts_.*"}


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

def extract_headers() -> dict[str, tuple[str, dict[str, str]]]:
    """source_id -> (extract path, header block), first extract wins.

    Read from the vault, which S213 repaired: every extract now carries a
    correct `# title:` and `# url:`. The vault is the authority for what the
    served rows SHOULD say.
    """
    found: dict[str, tuple[str, dict[str, str]]] = {}
    for path in sorted(VAULT.rglob("*.txt")):
        meta = read_extract_meta(path)
        sid = meta.get("source_id")
        if sid and sid not in found:
            found[sid] = (str(path.relative_to(REPO_ROOT)), meta)
    return found


def build_plan(damaged: dict[str, dict[str, int]],
               include_deletion_slated: bool,
               headers: dict[str, tuple[str, dict[str, str]]] | None = None,
               registry: dict | None = None) -> list[dict]:
    """One entry per damaged source, resolved against the repaired vault headers.

    S222 CORRECTION — this used to plan from the CAUSE and now plans from the
    DAMAGE. The old version walked the vault looking for extracts with no
    `# title:` header, because in S213 that set was exactly the set of sources
    serving code titles. S213 then fixed the headers but never repaired the
    store, so the planner's input went to zero while the 658 damaged rows kept
    serving. A repair tool that disarms itself the moment its cause is fixed
    reports success on an untouched defect — the mirror image of the silent
    fallback in `build_wiki_index.py` that caused all this. The damage is now
    measured where it actually lives: the store.
    """
    reg = registry if registry is not None else json.loads(
        REGISTRY.read_text(encoding="utf-8"))
    by_id = {s["source_id"]: s for s in reg.get("sources", [])}
    hdrs = headers if headers is not None else extract_headers()

    plan: list[dict] = []
    for sid in sorted(damaged):
        if sid in SLATED_FOR_DELETION and not include_deletion_slated:
            continue
        if any(re.fullmatch(pat, sid) for pat in NO_SOURCE_URL_BY_DESIGN):
            continue

        counts = damaged[sid]
        path, meta = hdrs.get(sid, (None, {}))
        title = meta.get("title")
        url = meta.get("url")
        why = f"vault extract header ({path})" if path else ""

        if not title and sid in by_id:
            title = by_id[sid].get("title")
            url = url or by_id[sid].get("url_primary")
            why = "source_registry entry for this id (no vault extract)"

        # Cross-check, not a substitute: the annual files declare their own
        # title now, so `enrolment_title` stops being the generator and becomes
        # the assertion that the header agrees with the registry parent's name.
        if sid.startswith("stat_enrolment_") and meta.get("school_year"):
            expected = enrolment_title(meta["school_year"])
            if title != expected:
                why += f"  ⚠ header title disagrees with parent series ({expected!r})"

        plan.append({
            "source_id": sid, "extract": path, "title": title, "url": url,
            "why": why,
            "code_titled": counts.get("code_title", 0),
            "url_less": counts.get("empty_url", 0),
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


def damage_from_store(key: str) -> dict[str, dict[str, int]]:
    """Scan every served row and count the two defects per source.

    Paged with limit/offset — PostgREST caps a single response at 1000 rows,
    and a Range header that asks for more comes back silently truncated, which
    would under-report the damage rather than fail.
    """
    rows: list[dict] = []
    step, off = 1000, 0
    while True:
        q = urllib.parse.urlencode({"select": "source_id,title,url",
                                    "order": "id.asc",
                                    "limit": step, "offset": off})
        status, body, _ = _req("GET", f"/rest/v1/wiki_chunks?{q}", key)
        if status >= 300:
            raise RuntimeError(f"damage scan failed at offset {off}: "
                               f"{status} {body[:200]}")
        batch = json.loads(body)
        rows += batch
        off += len(batch)
        if len(batch) < step:
            break

    damaged: dict[str, dict[str, int]] = {}
    for r in rows:
        sid = r["source_id"]
        if is_code_title(r.get("title"), sid):
            damaged.setdefault(sid, {}).setdefault("code_title", 0)
            damaged[sid]["code_title"] += 1
        if not (r.get("url") or "").strip():
            damaged.setdefault(sid, {}).setdefault("empty_url", 0)
            damaged[sid]["empty_url"] += 1
    return damaged


def patch_source(sid: str, title: str, url: str | None, key: str) -> int:
    """Repair one source's rows, one defect at a time.

    Filtered so each PATCH touches only rows still carrying that defect, which
    makes the whole thing idempotent and keeps a re-run from rewriting rows
    that are already correct. Title and url are repaired separately because
    they do not always co-occur — 26 rows carry a real title and no link.
    """
    touched = 0
    if title:
        q = urllib.parse.urlencode({"source_id": f"eq.{sid}",
                                    "title": f"eq.{sid}"})
        status, body, _ = _req("PATCH", f"/rest/v1/wiki_chunks?{q}", key,
                               {"title": title}, prefer="return=representation")
        if status >= 300:
            raise RuntimeError(f"title PATCH failed for {sid}: {status} {body[:300]}")
        touched += len(json.loads(body))
    if url:
        q = urllib.parse.urlencode({"source_id": f"eq.{sid}", "url": "eq."})
        status, body, _ = _req("PATCH", f"/rest/v1/wiki_chunks?{q}", key,
                               {"url": url}, prefer="return=representation")
        if status >= 300:
            raise RuntimeError(f"url PATCH failed for {sid}: {status} {body[:300]}")
        touched += len(json.loads(body))
    return touched


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

    # Fixtures — the planner is now fed the damage, so the whole plan is
    # provable with no network and no dependence on today's store contents.
    fx_damage = {
        "stat_kg": {"code_title": 3, "empty_url": 8},
        "stat_enrolment_2014": {"code_title": 56, "empty_url": 0},
        "stat_integrated_edu": {"empty_url": 5},
        "role_facts_finance": {"empty_url": 25},
        "arts_kla_guide_2017": {"code_title": 116, "empty_url": 116},
    }
    fx_headers = {
        "stat_kg": ("dev/vault/stat_kg/x.txt",
                    {"title": "幼稚園統計數字", "url": "https://e/kg.xlsx"}),
        "stat_enrolment_2014": ("dev/vault/stat_enrolment_report/x.txt",
                                {"title": "學生人數統計報告書（2014/15 學年）",
                                 "school_year": "2014/15",
                                 "url": "https://e/Enrol_2014.pdf"}),
        "stat_integrated_edu": ("dev/vault/stat_integrated_edu/x.txt",
                                {"title": "融合教育統計數字", "url": "https://e/ie.xlsx"}),
        "arts_kla_guide_2017": ("dev/vault/arts_kla_guide_2017/x.txt",
                                {"title": "藝術教育學習領域課程指引", "url": "https://e/ae.pdf"}),
    }
    fx_reg: dict = {"sources": []}

    def fx_plan(slated: bool = False) -> list[dict]:
        return build_plan(fx_damage, slated, headers=fx_headers, registry=fx_reg)

    plan = fx_plan()
    ids = {p["source_id"] for p in plan}
    check("Channel A 鏡像不當作損害（role_facts_* 依設計無連結）",
          "role_facts_finance" not in ids)
    check("預設排除待刪的 arts_kla_guide_2017", "arts_kla_guide_2017" not in ids)
    check("--include-deletion-slated 才會納入 arts_kla_guide_2017",
          "arts_kla_guide_2017" in {p["source_id"] for p in fx_plan(True)})
    check("只有真標題、無連結的來源一樣入計劃（title 對但 url 空）",
          "stat_integrated_edu" in ids)
    check("每項都解析到標題", all(p["title"] for p in plan))
    check("計劃內無任何標題等於自己的 source_id",
          all(p["title"] != p["source_id"] for p in plan))
    check("兩種損害的數量分開帶落計劃",
          next(p for p in plan if p["source_id"] == "stat_kg")["code_titled"] == 3
          and next(p for p in plan if p["source_id"] == "stat_kg")["url_less"] == 8)
    check("學年交叉核對通過時不出警告",
          "⚠" not in next(p for p in plan
                          if p["source_id"] == "stat_enrolment_2014")["why"])

    # Prove the cross-check can go red: a header whose title contradicts the
    # school_year it declares must be flagged, not silently written.
    bad_headers = dict(fx_headers)
    bad_headers["stat_enrolment_2014"] = (
        "x", {"title": "學生人數統計報告書（1999/00 學年）",
              "school_year": "2014/15", "url": "https://e/x.pdf"})
    bad_plan = build_plan({"stat_enrolment_2014": {"code_title": 1}}, False,
                          headers=bad_headers, registry=fx_reg)
    check("學年交叉核對證明會紅（標題與 school_year 不符）",
          "⚠" in bad_plan[0]["why"])

    # The damage scan must not under-report: a source present in the store but
    # absent from the vault still has to reach the plan via the registry.
    reg_only = build_plan({"only_in_registry": {"code_title": 4}}, False,
                          headers={}, registry={"sources": [
                              {"source_id": "only_in_registry",
                               "title": "真標題", "url_primary": "https://e/r.pdf"}]})
    check("庫內有損害但 vault 無抽取檔時，回落 registry",
          reg_only and reg_only[0]["title"] == "真標題")

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

    key = service_key()
    damaged = damage_from_store(key)
    plan = build_plan(damaged, args.include_deletion_slated)

    unresolved = [p for p in plan if not p["title"]]
    if unresolved:
        print("STOP — 這些來源解析不到標題，不會動它們：")
        for p in unresolved:
            print(f"  {p['source_id']}  ({p['extract'] or '無 vault 抽取檔、registry 亦無登記'})")
        return 1

    print(f"{'EXECUTE' if args.execute else 'DRY-RUN'} — 逐來源影響面\n")
    print(f"{'來源':<26}{'代號標題':>8}{'無連結':>8}  新標題 / 連結")
    print("-" * 100)
    total_title = total_url = total_changed = 0
    for p in plan:
        sid = p["source_id"]
        total_title += p["code_titled"]
        total_url += p["url_less"]
        print(f"{sid:<26}{p['code_titled']:>8}{p['url_less']:>8}  {p['title']}")
        print(f"{'':<26}{'':>16}  ← {p['why']}")
        if p["url"]:
            print(f"{'':<26}{'':>16}  ↗ {p['url']}")
        if args.execute:
            n = patch_source(sid, p["title"], p["url"], key)
            after = count_code_titled(sid, key)
            if after != 0:
                print(f"\nSTOP — {sid} 改後仍有 {after} 條代號標題，中止，未處理後續來源。")
                return 1
            total_changed += n
            print(f"{'':<26}{'':>16}  ✓ 已改 {n} 條，複查剩餘代號標題 {after}")

    print("-" * 100)
    print(f"合計：{total_title} 條代號標題、{total_url} 條無連結"
          + (f"，實改 {total_changed} 條" if args.execute else "（未改動，這是預覽）"))

    skipped = sorted(set(damaged) - {p["source_id"] for p in plan})
    if skipped:
        print(f"\n依設計略過 {len(skipped)} 個來源："
              + "、".join(skipped[:6]) + ("…" if len(skipped) > 6 else ""))
        print("  role_facts_*＝Channel A 鏡像，本來就無上游連結；"
              "arts_kla_guide_2017＝g37 的逐位元組重複，待刪不待改名。")
    if not args.execute:
        print("\n確認影響面無誤後，加 --execute 執行。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
