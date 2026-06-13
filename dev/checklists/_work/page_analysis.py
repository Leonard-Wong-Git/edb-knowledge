#!/usr/bin/env python3
# Task 1: whole-corpus page-marker coverage analysis (read-only).
# Pulls all wiki_chunks (id, source_id, text) paginated, computes per-source coverage,
# cross-refs registry + routes, writes PAGE_COVERAGE_REPORT.md + chunk cache.
import json, re, os, ssl, urllib.request

ROOT = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
WORK = os.path.join(ROOT, "dev/checklists/_work")
URL = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/wiki_chunks"

key = None
for line in open(os.path.join(ROOT, "backend/.env")):
    if line.startswith("SUPABASE_SERVICE_KEY="):
        key = line.split("=", 1)[1].strip()
assert key, "no service key"

def fetch(lo, hi):
    req = urllib.request.Request(
        URL + "?select=id,source_id,content_type,text&order=id",
        headers={"apikey": key, "Authorization": "Bearer " + key, "Range": f"{lo}-{hi}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf8"))

cache_path = os.path.join(WORK, "all_chunks.json")
if os.path.exists(cache_path):
    rows = json.load(open(cache_path))
    print("cache hit:", len(rows))
else:
    rows, lo = [], 0
    while True:
        batch = fetch(lo, lo + 999)
        rows += batch
        print("fetched", lo, "-", lo + len(batch) - 1, "total", len(rows), flush=True)
        if len(batch) < 1000:
            break
        lo += 1000
    json.dump(rows, open(cache_path, "w"), ensure_ascii=False)
print("TOTAL chunks:", len(rows))

PAGE_RE = re.compile(r"===\s*Page\s+(\d+)\s*===")
stats = {}  # sid -> dict
for r in rows:
    sid = r["source_id"]
    s = stats.setdefault(sid, {"total": 0, "marked": 0, "ctypes": {}})
    s["total"] += 1
    ct = r.get("content_type") or "?"
    s["ctypes"][ct] = s["ctypes"].get(ct, 0) + 1
    if PAGE_RE.search(r.get("text") or ""):
        s["marked"] += 1

# registry titles + source_type + url
reg = json.load(open(os.path.join(ROOT, "dev/source/source_registry.json")))
srcs = reg.get("sources", reg) if isinstance(reg, dict) else reg
reginfo = {}
for s in srcs:
    reginfo[s.get("source_id")] = {
        "title": s.get("title", ""),
        "stype": s.get("source_type", ""),
        "url": s.get("url_primary") or "",
    }

routes = json.load(open(os.path.join(ROOT, "dev/checklists/_work/routes.json")))
sid_routes = {}
for rk, members in routes.items():
    for sid in members:
        sid_routes.setdefault(sid, []).append(rk)

# classification
rows_out = []
for sid, s in sorted(stats.items(), key=lambda kv: -kv[1]["total"]):
    pct = 100.0 * s["marked"] / s["total"]
    ri = reginfo.get(sid, {})
    stype = ri.get("stype", "")
    is_rf = sid.startswith("role_facts") or "approved_fact" in s["ctypes"] or "stat_fact" in s["ctypes"]
    if pct == 100:
        cls = "✅ 全頁碼"
    elif sid.startswith("role_facts"):
        cls = "◻️ 核實事實（天生無頁）"
    elif stype in ("html", "xlsx", "web") or all(ct in ("stat_fact", "approved_fact") for ct in s["ctypes"]):
        cls = "◻️ 結構性無頁（HTML/數據）"
    elif pct == 0:
        cls = "🔴 全無頁碼（候選 repage）"
    else:
        cls = "🟡 部分頁碼（候選 repage）"
    rows_out.append((sid, ri.get("title", "")[:38], s["total"], s["marked"], pct, stype, cls,
                     ",".join(sid_routes.get(sid, []))))

total = sum(s["total"] for s in stats.values())
marked = sum(s["marked"] for s in stats.values())
n_full = sum(1 for r in rows_out if r[6].startswith("✅"))
n_part = sum(1 for r in rows_out if r[6].startswith("🟡"))
n_zero = sum(1 for r in rows_out if r[6].startswith("🔴"))
n_struct = sum(1 for r in rows_out if r[6].startswith("◻️"))

L = []
L.append("# 全庫頁碼覆蓋分析報告（2026-06-11，S155 自主批次）")
L.append("")
L.append(f"> 讀取 Supabase `wiki_chunks` 全量 **{total:,} chunks／{len(stats)} 源**（read-only，零改動）。")
L.append(f"> 頁碼標記定義：chunk text 含 `=== Page N ===`。整體覆蓋 **{marked:,}/{total:,} = {100.0*marked/total:.1f}%**。")
L.append("")
L.append(f"| 分類 | 源數 |")
L.append(f"|---|---|")
L.append(f"| ✅ 全頁碼 | {n_full} |")
L.append(f"| 🟡 部分頁碼（候選 repage） | {n_part} |")
L.append(f"| 🔴 全無頁碼（候選 repage） | {n_zero} |")
L.append(f"| ◻️ 結構性無頁（HTML／數據／核實事實） | {n_struct} |")
L.append("")
L.append("> ⚠️ repage 屬 Supabase 資料改動（CB-3 pipeline：repage_pdfs.py + cb3_b2_pagecarry_migrate.py），本批次**只分析不執行**，候選清單留 Leonard 拍板。歷史脈絡：S119–S132 已 page-carry 94 源、達 ~88% 可行天花板；下表 🔴🟡 即天花板以外殘餘＋新入庫源檢視。")
L.append("")
L.append("## 逐源明細（按 chunk 數降序）")
L.append("")
L.append("| source_id | 文件 | chunks | 有頁碼 | % | 類型 | 分類 | 所屬 route |")
L.append("|---|---|---|---|---|---|---|---|")
for r in rows_out:
    L.append(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]:.0f}% | {r[5]} | {r[6]} | {r[7]} |")
L.append("")

out = os.path.join(ROOT, "dev/checklists/PAGE_COVERAGE_REPORT.md")
open(out, "w").write("\n".join(L) + "\n")
print("report ->", out)
print(f"summary: full={n_full} partial={n_part} zero={n_zero} structural={n_struct}")
# per-route page health for the batch plan
print("\n=== route page health (doc sources only) ===")
for rk, members in routes.items():
    docs = [m for m in members if not m.startswith("role_facts")]
    tt = sum(stats.get(m, {}).get("total", 0) for m in docs)
    mm = sum(stats.get(m, {}).get("marked", 0) for m in docs)
    missing = [m for m in docs if m not in stats]
    print(f"{rk:18s} docs={len(docs):2d} chunks={tt:5d} marked={mm:5d} ({(100.0*mm/tt if tt else 0):.0f}%) notInDB={missing}")
