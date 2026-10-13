#!/usr/bin/env python3
"""
check_downstream_sync.py — after a source is refreshed, replaced, re-pointed or
retired, list every user-facing place that still has to change (S238).

Why: S238 refreshed 7 documents and fixed 11 links in the store, then Leonard had
to point out, one at a time, that the public update log, the 📚 guideline library
(g26 still 2026/27) and the platform-intro demo (「學校行政手冊 2026年5月版」) had
not followed. Each surface had its own copy of the title / URL / edition and
nothing tied them to the store. This script is that tie.

Two layers (Leonard asked for the /jev-decide method):
  1. Deterministic — exact matches the script can decide alone: an old URL still
     served, an edition marker that differs from the registry, a missing update-log
     entry, a retired id still routed, a checklist item whose text is no longer in
     the new extract (or has moved page).
  2. Jev (--jev) — only for hits the script cannot decide (checklist text not
     found, hard-coded citations): asks dev/source/jev/downstream_sync_gate.json
     with the operator's change note. ≥0.70 → MUST_UPDATE, ≤0.30 → OK, between →
     REVIEW (a person decides). Jev is a second opinion, never an authority.

Usage (repo root):
  python3 dev/source/check_downstream_sync.py --sources g19,g26 --base <git ref>
  python3 dev/source/check_downstream_sync.py --sources g19 --base <ref> \
      --notes notes.json --jev            # notes.json: {"g19": "改動摘要…"}
  python3 dev/source/check_downstream_sync.py --self-test

--base is the commit BEFORE the change (old titles/URLs are read from it). Exit 1
when any MUST_UPDATE remains, so it can gate a closeout.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REGISTRY = "dev/source/source_registry.json"
APP = REPO / "app.html"
GUIDELINES = REPO / "guidelines.json"
UPDATE_LOG = REPO / "update_log.json"
CHECKLISTS = REPO / "checklists_bundle.json"
BACKEND = REPO / "backend" / "src" / "api" / "searchChannelB.ts"
VAULT = REPO / "dev" / "vault"
JEV = Path.home() / ".claude" / "skills" / "jev-decide" / "scripts" / "jev.py"
GATE = REPO / "dev" / "source" / "jev" / "downstream_sync_gate.json"
# user-facing files whose text can carry an old URL / edition
SURFACES = ["app.html", "index.html", "mobile.js", "guidelines.json", "checklists_bundle.json",
            "update_log.json", "README.md", "q.html"]

EDITION_RE = re.compile(r"(20\d\d\s*/\s*\d\d學年|20\d\d年\d{1,2}月(?:修訂)?版|（20\d\d）|\(20\d\d\)|20\d\d年版|20\d\d年更新)")
PAGE_RE = re.compile(r"=== Page (\d+) ===")


def squeeze(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s or ""))


def norm(s: str) -> str:
    """squeeze + drop punctuation, so 「防貪錦囊：學校…」 matches 「防貪錦囊（學校…」."""
    return re.sub(r"[^\w/]", "", squeeze(s))


DOCNO_RE = re.compile(r"\d{1,3}/20\d\d")


def mentions(text: str, title: str) -> bool:
    """Does free text (an update-log line) refer to this document? Either the
    circular number (221/2025) or any 6-character window of the title stem."""
    t = norm(text)
    if any(n in t for n in DOCNO_RE.findall(squeeze(title))):
        return True
    st = norm(stem(title))
    return any(st[i:i + 6] in t for i in range(0, max(1, min(len(st), 14) - 5)))


def editions(s: str) -> set:
    return {squeeze(m) for m in EDITION_RE.findall(s or "")}


def stem(title: str) -> str:
    """Title without edition markers / brackets — what other surfaces call it."""
    t = EDITION_RE.sub("", title or "")
    t = re.sub(r"[《》「」（）()\s]", "", t)
    return t


def load_registry(ref: str | None) -> dict:
    if ref:
        raw = subprocess.run(["git", "show", f"{ref}:{REGISTRY}"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
    else:
        raw = (REPO / REGISTRY).read_text(encoding="utf-8")
    return {s["source_id"]: s for s in json.loads(raw)["sources"]}


def urls_of(row: dict | None) -> set:
    if not row:
        return set()
    return {u for u in (row.get("url_primary"), row.get("url_landing")) if u}


def url_variants(u: str) -> set:
    return {u, u.replace(" ", "%20"), u.replace("%20", " ")}


# ── surfaces ───────────────────────────────────────────────────────────────
def library_entries() -> list:
    s = APP.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"\{ id: '([^']+)', title: '([^']*)'.*?year: '([^']*)'.*?url: '([^']*)' \}", s):
        out.append({"id": m.group(1), "title": m.group(2), "year": m.group(3), "url": m.group(4)})
    return out


def _pages_from_text(text: str) -> dict:
    parts = PAGE_RE.split(text)
    pages = {}
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = squeeze(parts[i + 1])
    return pages or {0: squeeze(text)}


def extract_pages(sid: str, ref: str | None = None) -> dict | None:
    """Page texts of the vault extract — current tree, or as of git `ref`."""
    if ref:
        ls = subprocess.run(["git", "ls-tree", "--name-only", ref, f"dev/vault/{sid}/"], cwd=REPO,
                            capture_output=True, text=True).stdout.split()
        files = sorted(f for f in ls if Path(f).name.startswith("extract_") and f.endswith(".txt"))
        if not files:
            return None
        return _pages_from_text(subprocess.run(["git", "show", f"{ref}:{files[0]}"], cwd=REPO,
                                               capture_output=True, text=True).stdout)
    d = VAULT / sid
    files = sorted(d.glob("extract_*.txt")) if d.is_dir() else []
    return _pages_from_text(files[0].read_text(encoding="utf-8")) if files else None


def locate(req: str, pages: dict) -> int | None:
    """Page whose text contains the item (exact squeeze, else a 24-char core)."""
    q = squeeze(req)
    cores = [q] + ([q[i:i + 24] for i in range(0, max(1, len(q) - 24), 12)] if len(q) > 30 else [])
    for core in cores:
        for p, t in pages.items():
            if core and core in t:
                return p
    return None


def scan(sources: list, base: str | None, since: str) -> list:
    now, old = load_registry(None), load_registry(base) if base else {}
    hits = []

    def add(level, surface, sid, where, detail, excerpt="", needs_jev=False):
        hits.append({"level": level, "surface": surface, "source_id": sid, "where": where,
                     "detail": detail, "excerpt": excerpt[:400], "needs_jev": needs_jev})

    lib = library_entries()
    gl = GUIDELINES.read_text(encoding="utf-8")
    log = json.loads(UPDATE_LOG.read_text(encoding="utf-8"))["entries"]
    bundle = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    backend = BACKEND.read_text(encoding="utf-8") if BACKEND.exists() else ""

    for sid in sources:
        cur, prev = now.get(sid), old.get(sid)
        title = (cur or prev or {}).get("title", sid)
        cur_urls = urls_of(cur)
        stale_urls = set()
        for u in urls_of(prev) - cur_urls:
            stale_urls |= url_variants(u)
        st = stem(title)

        # 1. old URL anywhere user-facing
        for f in SURFACES:
            p = REPO / f
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            for u in stale_urls:
                n = t.count(u)
                if n:
                    add("MUST_UPDATE", "舊連結", sid, f, f"仍有 {n} 處指向舊網址", u)

        # 2. guideline library (in-app + public endpoint)
        for e in lib:
            if e["id"] == sid or e["url"] in cur_urls | stale_urls or (st and len(st) >= 6 and st in stem(e["title"])):
                ed_lib, ed_reg = editions(e["title"]), editions(title)
                if ed_lib and ed_reg and ed_lib != ed_reg:
                    add("MUST_UPDATE", "指引文件庫", sid, f"app.html id={e['id']}",
                        f"標題版本 {sorted(ed_lib)} 與現行 {sorted(ed_reg)} 不同", e["title"])
                if e["url"] in stale_urls:
                    add("MUST_UPDATE", "指引文件庫", sid, f"app.html id={e['id']}", "連結是舊網址", e["url"])
                if e["id"] in gl and e["title"] not in gl:
                    add("MUST_UPDATE", "指引文件庫", sid, "guidelines.json",
                        "公開端點標題與 app.html 不一致", e["title"])
        if cur and cur.get("status") == "verified" and sid not in {e["id"] for e in lib}:
            add("INFO", "指引文件庫", sid, "app.html", "此來源不在指引文件庫（可能刻意不列，見 UNLISTED）")

        # 3. update log — only when this source actually changed (registry row or text)
        changed = (cur != prev) if base else True
        if base and not changed:
            changed = extract_pages(sid) != extract_pages(sid, base)
        recent = [e for e in log if e.get("date", "") >= since]
        if changed and not any(mentions(e.get("title", "") + e.get("desc", ""), title) for e in recent):
            add("MUST_UPDATE", "更新日誌", sid, "update_log.json",
                f"{since} 起沒有提及「{title}」的記錄（可合併成一條，但要提到它）")

        # 4. retired but still routed
        if cur and cur.get("status") in ("deprecated", "superseded", "blocked") and f'"{sid}"' in backend:
            add("SHOULD_UPDATE", "後端路由", sid, "backend/src/api/searchChannelB.ts",
                "已退役但仍在 SOURCE_SETS／spotlight（無片段可取，屬死引用）")

        # 5. checklists: source map + item text against the NEW extract
        # Checklist items are REWRITTEN requirements, not verbatim quotes (S238 first
        # run: 507 "not found" against the new text alone). So only the DIFFERENCE is a
        # signal: text that matched the old extract but no longer matches the new one,
        # or that sat on one page before and another now.
        pages = extract_pages(sid)
        old_pages = extract_pages(sid, base) if base else None
        if old_pages == pages:
            pages = None                      # extract unchanged → items unaffected
        for dkey, dom in bundle.get("domains", {}).items():
            src = (dom.get("src") or {}).get(sid)
            if src:
                if src[1] in stale_urls:
                    add("MUST_UPDATE", "清單", sid, f"checklists_bundle {dkey}.src", "來源連結是舊網址", src[1])
                if editions(src[0]) and editions(title) and editions(src[0]) != editions(title):
                    add("MUST_UPDATE", "清單", sid, f"checklists_bundle {dkey}.src", "來源名稱版本過時", src[0])
            if pages is None:
                continue
            for sec in dom.get("sections", []):
                for it in sec.get("items", []):
                    if it.get("source_id") != sid:
                        continue
                    where = f"checklists_bundle {dkey} 「{sec.get('name','')}」 p.{it.get('page')}"
                    if old_pages is None:
                        continue              # no baseline → cannot tell a change from a paraphrase
                    was = locate(it.get("req", ""), old_pages)
                    if was is None:
                        continue              # paraphrase: never matched verbatim, no signal
                    p = locate(it.get("req", ""), pages)
                    if p is None:
                        add("REVIEW", "清單", sid, where, f"舊版 p.{was} 找得到、新版找不到（條文已改寫或刪除）",
                            it.get("req", ""), needs_jev=True)
                    elif p != was:
                        add("SHOULD_UPDATE", "清單", sid, where, f"原文由 p.{was} 移到 p.{p}", it.get("req", ""))

        # 6. hard-coded citations in app copy (demo answers etc.)
        app = APP.read_text(encoding="utf-8")
        for m in re.finditer(r"source: '([^']*)'", app):
            cite = m.group(1)
            if st and len(st) >= 4 and st[:6] in squeeze(cite):
                ed_c, ed_reg = editions(cite), editions(title)
                lvl = "MUST_UPDATE" if (ed_c and ed_reg and ed_c != ed_reg) else "REVIEW"
                add(lvl, "平台文案", sid, "app.html source:", "硬編碼引用（示範問答等）", cite, needs_jev=True)
    return hits


# ── Jev layer ──────────────────────────────────────────────────────────────
def ask_jev(hit: dict, title: str, note: str) -> dict:
    state = {"source": {"title": title, "source_id": hit["source_id"]},
             "change_note": note or "",
             "downstream": {"where": hit["where"], "text": hit["excerpt"]},
             "evidence": hit["detail"]}
    r = subprocess.run([sys.executable, str(JEV), "--questions", str(GATE), "--state-file", "-", "--json"],
                       input=json.dumps(state, ensure_ascii=False), capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": (r.stderr or r.stdout)[-300:]}
    out = json.loads(r.stdout[r.stdout.index("{"):])
    return out


def jev_level(out: dict) -> tuple:
    probs = {}
    for qid, a in (out.get("answers") or out).items():
        if isinstance(a, dict) and ("noul" in a or "value" in a):
            probs[qid] = a.get("noul", a.get("value"))     # jev.py --json uses "noul"
    if not probs:
        return "REVIEW", probs
    top = max(probs.values())
    if top >= 0.70:
        return "MUST_UPDATE", probs
    if top <= 0.30:
        return "OK", probs
    return "REVIEW", probs


# ── self-test ──────────────────────────────────────────────────────────────
def self_test() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("  PASS  " if cond else "  FAIL  ") + name)

    check("edition: 學年", editions("2026/27學年幼稚園收生安排指引") == {"2026/27學年"})
    check("edition: 月版", editions("學校行政手冊（SAG）2026年5月版") == {"2026年5月版"})
    check("edition differs", editions("2026年5月版") != editions("學校行政手冊（2026年8月版）"))
    check("stem drops edition", stem("學校行政手冊（2026年8月版）") == "學校行政手冊")
    check("url variants", "a%20b" in url_variants("a b"))
    pages = {3: squeeze("學校與月薪臨時教師訂定的聘任期須不少於連續90個曆日。"), 4: squeeze("其他")}
    check("locate exact", locate("學校與月薪臨時教師訂定的聘任期須不少於連續90個曆日。", pages) == 3)
    check("locate missing", locate("整合代課教師津貼適用於少於30天的假期", pages) is None)
    check("mentions by number", mentions("通函第221/2025號及第83/2020號", "教育局通函第221/2025號 —— 撥款計劃"))
    check("mentions by window", mentions("廉署防貪錦囊（學校管治與內部監控）", "防貪錦囊：學校管治與內部監控 (ICAC)"))
    check("mentions negative", not mentions("香港學校表現指標", "2027/28學年幼稚園收生安排指引"))
    check("jev band high", jev_level({"answers": {"a": {"value": 0.9}}})[0] == "MUST_UPDATE")
    check("jev noul key", jev_level({"answers": {"a": {"type": "noul", "noul": 0.98}}})[0] == "MUST_UPDATE")
    check("jev band low", jev_level({"answers": {"a": {"value": 0.1}, "b": {"value": 0.2}}})[0] == "OK")
    check("jev band mid", jev_level({"answers": {"a": {"value": 0.5}}})[0] == "REVIEW")
    print("ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--sources", help="changed source_ids, comma-separated")
    ap.add_argument("--base", help="git ref before the change (old titles/URLs come from here)")
    ap.add_argument("--since", default=(date.today() - timedelta(days=7)).isoformat(),
                    help="update-log entries on/after this date count (default: 7 days ago)")
    ap.add_argument("--notes", help="JSON {source_id: change note} for the Jev layer")
    ap.add_argument("--jev", action="store_true", help="send undecidable hits to Jev")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.sources:
        ap.error("--sources is required")
    sources = [s.strip() for s in a.sources.split(",") if s.strip()]
    hits = scan(sources, a.base, a.since)
    if a.jev:
        notes = json.loads(Path(a.notes).read_text(encoding="utf-8")) if a.notes else {}
        reg = load_registry(None)
        for h in hits:
            if h["needs_jev"]:
                out = ask_jev(h, reg.get(h["source_id"], {}).get("title", h["source_id"]), notes.get(h["source_id"], ""))
                if "error" in out:
                    h["jev"] = out
                    continue
                lvl, probs = jev_level(out)
                h["jev"] = probs
                if h["level"] == "REVIEW":
                    h["level"] = lvl
    order = {"MUST_UPDATE": 0, "SHOULD_UPDATE": 1, "REVIEW": 2, "OK": 3, "INFO": 4}
    hits.sort(key=lambda h: (order[h["level"]], h["source_id"], h["surface"]))
    if a.json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
    else:
        for h in hits:
            j = f"  jev={h['jev']}" if "jev" in h else ""
            print(f"[{h['level']:<13}] {h['surface']:<6} {h['source_id']:<24} {h['where']} — {h['detail']}{j}")
            if h["excerpt"]:
                print(f"{'':16}「{h['excerpt'][:110]}」")
        c = {k: sum(1 for h in hits if h["level"] == k) for k in order}
        print("\nsummary:", json.dumps(c, ensure_ascii=False))
    return 1 if any(h["level"] == "MUST_UPDATE" for h in hits) else 0


if __name__ == "__main__":
    sys.exit(main())
