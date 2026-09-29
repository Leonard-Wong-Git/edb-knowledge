#!/usr/bin/env python3
"""search_log_report.py — 有人搜尋了甚麼？（S234；S233 設計第六節第 4 點的最小版）

WHY THIS IS A LOCAL TOOL AND NOT A PAGE
`public.search_log` holds what strangers typed into the search box. The repository
and the status page are PUBLIC and git history is permanent, so baking the queries
into `qc_report.json` would publish every user's words for good. S233 fixed the
rule "read only through service_role"; this tool keeps to it: it runs on Leonard's
Mac with the key in `backend/.env`, reads, prints, and writes nothing anywhere.
Do not redirect its output into a tracked file.

Read-only by construction: one GET, no other verb exists in this file.

    python3 dev/search_log_report.py                  # 最近 30 日，最多 100 條
    python3 dev/search_log_report.py --days 7 --limit 50
    python3 dev/search_log_report.py --answers        # 連回答全文（很長）
    python3 dev/search_log_report.py --json           # 原始資料，供進一步分析
    python3 dev/search_log_report.py --self-test

Reading it: traffic is about 1–5 searches a day, so read the rows one by one — the
value is the SHAPE of what users ask, not the percentages. The log cannot tell
Leonard's own manual searches from real users' (identity is deliberately not kept).
Our own probes carry `x-probe` and never reach the log.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TABLE_URL = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/search_log"
HKT = timezone(timedelta(hours=8))          # Hong Kong has no daylight saving
QUERY_CELL_MAX = 60


# ---------------------------------------------------------------------------
# pure helpers — every one covered by --self-test
# ---------------------------------------------------------------------------

def hkt(iso: str | None) -> str:
    """UTC ISO stamp -> 'MM-DD HH:MM' in Hong Kong time; '—' when unusable."""
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(HKT).strftime("%m-%d %H:%M")


def verdict(row: dict) -> str:
    """What the user got. Order matters: a degraded search that also declined is
    a degraded search first — the cause is the service, not the corpus."""
    if row.get("degraded"):
        return "服務降級"
    if row.get("declined"):
        return "拒答"
    if row.get("total") == 0:
        return "無結果"
    return "有答案"


def rating(row: dict) -> str:
    return {1: "👍", -1: "👎"}.get(row.get("feedback"), "—")


def device(row: dict) -> str:
    return {"desktop": "桌面", "mobile": "手機"}.get(row.get("client"), "未標示")


def cell(text: str | None, limit: int = QUERY_CELL_MAX) -> str:
    """One Markdown table cell: flatten whitespace, escape the pipe, cap length."""
    t = " ".join(str(text or "").split()).replace("|", "｜")
    return t if len(t) <= limit else t[: limit - 1] + "…"


def summarize(rows: list[dict]) -> dict:
    lat = [r["latency_ms"] for r in rows if isinstance(r.get("latency_ms"), int)]
    return {
        "total": len(rows),
        "declined": sum(1 for r in rows if verdict(r) == "拒答"),
        "degraded": sum(1 for r in rows if verdict(r) == "服務降級"),
        "no_result": sum(1 for r in rows if verdict(r) == "無結果"),
        "up": sum(1 for r in rows if r.get("feedback") == 1),
        "down": sum(1 for r in rows if r.get("feedback") == -1),
        "desktop": sum(1 for r in rows if r.get("client") == "desktop"),
        "mobile": sum(1 for r in rows if r.get("client") == "mobile"),
        "unlabelled": sum(1 for r in rows if r.get("client") not in ("desktop", "mobile")),
        "avg_latency_s": round(sum(lat) / len(lat) / 1000, 1) if lat else None,
    }


def render_table(rows: list[dict]) -> str:
    out = ["| 時間（香港） | 搜尋內容 | 結果 | 評分 | 裝置 |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {hkt(r.get('created_at'))} | {cell(r.get('query'))} | "
                   f"{verdict(r)} | {rating(r)} | {device(r)} |")
    return "\n".join(out)


def render_report(rows: list[dict], days: int, show_answers: bool = False) -> str:
    if not rows:
        return (f"最近 {days} 日沒有搜尋記錄。\n"
                "（這可能是真的沒有人搜尋，也可能是記錄寫入失敗——後者會在後端日誌留下 "
                "warn，搜尋本身不受影響。）")
    s = summarize(rows)
    lines = [
        f"# 用戶搜尋記錄（最近 {days} 日，共 {s['total']} 條）",
        "",
        f"- 結果：拒答 {s['declined']}、無結果 {s['no_result']}、服務降級 {s['degraded']}",
        f"- 評分：👍 {s['up']}、👎 {s['down']}（其餘未評分）",
        f"- 裝置：桌面 {s['desktop']}、手機 {s['mobile']}、未標示 {s['unlabelled']}",
        f"- 平均耗時：{s['avg_latency_s']} 秒" if s["avg_latency_s"] is not None
        else "- 平均耗時：無資料",
        "",
        "## 全部搜尋（新的在前）",
        "",
        render_table(rows),
    ]
    attention = [r for r in rows if verdict(r) in ("拒答", "無結果") or r.get("feedback") == -1]
    if attention:
        lines += ["", "## 值得逐條看：拒答、無結果或被評 👎", ""]
        for r in attention:
            lines.append(f"- {hkt(r.get('created_at'))}　{cell(r.get('query'), 120)}"
                         f"　（{verdict(r)}，{rating(r)}，範疇：{r.get('route') or '無'}）")
    if show_answers:
        lines += ["", "## 回答全文", ""]
        for r in rows:
            lines += [f"### {hkt(r.get('created_at'))}　{cell(r.get('query'), 120)}", "",
                      (r.get("synthesis") or "（無回答文字）").strip(), ""]
    lines += ["", "—— 流量很低，請逐條閱讀，不要只看比例。記錄含你自己的手動搜尋，無法區分。",
              "—— 本報告只在本機顯示，不要貼進 repo 內任何檔案（repo 公開，git 歷史永久）。"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# I/O — the only network call in this file is the GET below
# ---------------------------------------------------------------------------

def service_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if key:
        return key
    env = REPO_ROOT / "backend" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("SUPABASE_SERVICE_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("找不到 SUPABASE_SERVICE_KEY（環境變數或 backend/.env）。"
                       "search_log 只有 service_role 讀得到。")


def fetch_rows(days: int, limit: int, with_answers: bool) -> list[dict]:
    key = service_key()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cols = ["created_at", "query", "client", "route", "declined", "degraded",
            "feedback", "latency_ms", "total"] + (["synthesis"] if with_answers else [])
    url = TABLE_URL + "?" + urllib.parse.urlencode({
        "select": ",".join(cols), "created_at": f"gte.{since}",
        "order": "created_at.desc", "limit": str(limit)})
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Never echo request headers: they carry the key.
        raise RuntimeError(f"Supabase 回 HTTP {e.code}") from None


# ---------------------------------------------------------------------------
# self-test — offline, fixtures only
# ---------------------------------------------------------------------------

def self_test() -> int:
    fails: list[str] = []

    def check(name: str, cond: bool):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(name)

    check("UTC 18:42 → 香港翌日 02:42", hkt("2026-09-28T18:42:10.123+00:00") == "09-29 02:42")
    check("Z 結尾也可解析", hkt("2026-09-28T18:42:10Z") == "09-29 02:42")
    check("壞時間戳不崩潰", hkt("garbage") == "—" and hkt(None) == "—")

    check("降級優先於拒答", verdict({"degraded": True, "declined": True}) == "服務降級")
    check("拒答", verdict({"declined": True, "total": 8}) == "拒答")
    check("零結果而未拒答 → 無結果", verdict({"total": 0}) == "無結果")
    check("total 缺失不當作無結果", verdict({}) == "有答案")
    check("有答案", verdict({"total": 8}) == "有答案")
    check("評分 👍／👎／未評", rating({"feedback": 1}) == "👍" and rating({"feedback": -1}) == "👎"
          and rating({"feedback": None}) == "—")
    check("裝置：未標示是 server-to-server 或舊請求",
          device({"client": None}) == "未標示" and device({"client": "mobile"}) == "手機")

    check("表格格內的 | 會被轉義，不會弄壞表格", "|" not in cell("a|b").replace("｜", ""))
    check("換行與多餘空白被壓平", cell("a\n\n  b") == "a b")
    check("過長查詢被截斷並加 …", cell("字" * 100).endswith("…") and len(cell("字" * 100)) == QUERY_CELL_MAX)

    rows = [
        {"created_at": "2026-09-28T18:42:00Z", "query": "某個關於假期的問題", "client": "desktop",
         "route": "hr_admin", "declined": False, "degraded": False, "feedback": 1,
         "latency_ms": 9200, "total": 8},
        {"created_at": "2026-09-27T10:00:00Z", "query": "某個語料沒有的問題", "client": "mobile",
         "route": None, "declined": True, "degraded": False, "feedback": -1,
         "latency_ms": 4100, "total": 8},
        {"created_at": "2026-09-26T10:00:00Z", "query": "x", "client": None, "route": None,
         "declined": False, "degraded": False, "feedback": None, "latency_ms": None, "total": 0},
    ]
    s = summarize(rows)
    check("概況數字", s["total"] == 3 and s["declined"] == 1 and s["no_result"] == 1
          and s["up"] == 1 and s["down"] == 1 and s["desktop"] == 1 and s["mobile"] == 1
          and s["unlabelled"] == 1)
    check("平均耗時只計有數值者（9.2 與 4.1 → 6.7）", s["avg_latency_s"] == 6.7)
    check("全無耗時 → None 而非除以零", summarize([{"query": "a"}])["avg_latency_s"] is None)

    rep = render_report(rows, 30)
    check("報告含三行資料與『值得逐條看』", rep.count("\n| 09-") == 3 and "值得逐條看" in rep)
    check("拒答那條出現在『值得逐條看』", "某個語料沒有的問題" in rep.split("值得逐條看")[1])
    check("正常且已評 👍 的不列入『值得逐條看』", "某個關於假期的問題" not in rep.split("值得逐條看")[1])
    check("報告帶不進 repo 的提醒", "不要貼進 repo" in rep)
    check("--answers 才出現回答全文", "回答全文" not in rep
          and "回答全文" in render_report([dict(rows[0], synthesis="答案內容")], 30, True))
    check("零筆資料：給出兩種可能的原因，不崩潰", "沒有搜尋記錄" in render_report([], 30)
          and "寫入失敗" in render_report([], 30))

    # 唯讀：本檔只可能有一個網絡請求，且是 GET（沒有 data= 就是 GET）
    src = Path(__file__).read_text(encoding="utf-8")
    needle = "urllib.request." + "urlopen("        # split so this line does not match itself
    body_kw = "da" + "ta="                          # a request body would turn it into a POST
    check("本檔只有一處網絡請求，且不帶 body（＝唯讀 GET）",
          src.count(needle) == 1
          and body_kw not in src.split("def fetch_rows")[1].split("def self_test")[0])

    print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--answers", action="store_true", help="連回答全文一併顯示")
    ap.add_argument("--json", action="store_true", help="輸出原始 JSON")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.days < 1 or not 1 <= args.limit <= 1000:
        print("--days 要 ≥ 1，--limit 要在 1 至 1000 之間", file=sys.stderr)
        return 2
    try:
        rows = fetch_rows(args.days, args.limit, args.answers)
    except RuntimeError as e:
        print(f"讀取失敗：{e}", file=sys.stderr)
        return 2
    print(json.dumps(rows, ensure_ascii=False, indent=2) if args.json
          else render_report(rows, args.days, args.answers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
