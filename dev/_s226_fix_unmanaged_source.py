#!/usr/bin/env python3
"""_s226_fix_unmanaged_source.py — 把 2 條錯配 id 的片段併回已登記來源。

REGISTRY_UNMANAGED 是封版閘餘下三個 ERROR 之一。實況（S226 逐條開出來看）：
  · registry 有 `stat_integrated_edu`（status=verified，5 條 stat_fact 摘要句）
  · 庫內另有 2 條掛在 `stat_integrated`（vault_extract 原始表格），**從未登記**
  · 兩者同標題（融合教育統計數字）、同 URL（Integrated_Education_TC.xlsx）
  · 兩批內容零重疊（逐字雜湊比對），所以不是重複，是入庫時的 id 錯配

修法：UPDATE 2 行的 `source_id`，**非 DELETE**，舊值已知故可完全回退。
改完 7 條同屬已登記來源，受新鮮度／到期／封面標題三個監察覆蓋。

刻意不做的兩件事：
  · **不改 chunk id**。id 是 `<content_type>_<source_id>_<內容雜湊>`，改它等於刪除
    再入庫（連 embedding 重算）。為 2 行付這個代價不值，所以改完 id 會留下化石
    （`vault_stat_integrated_…` 而 source_id 是 `stat_integrated_edu`）。**這個不
    一致是已知且刻意的**，不是漏做。
  · **不替 `stat_integrated` 另開 registry 條目**。那等於為同一份文件登記兩次，
    正是 `g33`／`eng_sss_guide_2021`（421 條逐字相同）那種缺陷。

另有一項本工具解決不到，記在此以免下一位以為已完：其中一條片段
（`vault_stat_integrated_5f63b1cf17202f6f`）由表格中段開始、無標頭，屬
`NO_MIDCLAUSE_START` 家族。重貼標籤不會令它變成好答案材料；要徹底處理須重抽該 XLSX。

USAGE
  python3 dev/_s226_fix_unmanaged_source.py                 # dry-run（預設）
  python3 dev/_s226_fix_unmanaged_source.py --execute       # 真正寫入
  python3 dev/_s226_fix_unmanaged_source.py --rollback --execute
需要環境變數：  set -a && . backend/.env && set +a
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

URL = "https://youkcekbrbywuqjxgibe.supabase.co/rest/v1/wiki_chunks"
IDS = ["vault_stat_integrated_5f63b1cf17202f6f",
       "vault_stat_integrated_f3ef6f83c8d6fd02"]
OLD_SOURCE = "stat_integrated"
NEW_SOURCE = "stat_integrated_edu"


def key() -> str:
    k = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not k:
        raise SystemExit("缺 SUPABASE_SERVICE_KEY —— 先 `set -a && . backend/.env && set +a`")
    return k


def headers(extra: dict | None = None) -> dict:
    h = {"apikey": key(), "Authorization": f"Bearer {key()}",
         "Content-Type": "application/json"}
    h.update(extra or {})
    return h


def count(source_id: str | None = None) -> int:
    params = {"select": "id"}
    if source_id:
        params["source_id"] = f"eq.{source_id}"
    r = urllib.request.Request(f"{URL}?{urllib.parse.urlencode(params)}",
                               headers=headers({"Prefer": "count=exact", "Range": "0-0"}))
    with urllib.request.urlopen(r, timeout=45) as resp:
        return int((resp.headers.get("content-range") or "0-0/0").split("/")[-1])


def id_filter() -> str:
    return "in.(" + ",".join(f'"{i}"' for i in IDS) + ")"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="真正寫入（預設只 dry-run）")
    ap.add_argument("--rollback", action="store_true",
                    help=f"把 source_id 改回 {OLD_SOURCE}")
    args = ap.parse_args()
    target = OLD_SOURCE if args.rollback else NEW_SOURCE
    other = NEW_SOURCE if args.rollback else OLD_SOURCE

    r = urllib.request.Request(
        f"{URL}?{urllib.parse.urlencode({'select': 'id,source_id,title,content_type', 'id': id_filter()})}",
        headers=headers())
    with urllib.request.urlopen(r, timeout=45) as resp:
        rows = json.loads(resp.read())
    print(f"以 id 精確鎖定（不以 source_id 為條件，避免誤傷）：{len(rows)} 行")
    for row in rows:
        print(f"  {row['id']} | source_id={row['source_id']} | {row['content_type']} | {row['title']}")
    if len(rows) != 2:
        raise SystemExit(f"預期 2 行，實際 {len(rows)} 行 —— 停手，先查清楚")

    total_before, old_before, new_before = count(), count(OLD_SOURCE), count(NEW_SOURCE)
    print(f"\n改動前：{OLD_SOURCE} {old_before} 條 · {NEW_SOURCE} {new_before} 條 · 全庫 {total_before} 條")
    print(f"將把上列 2 行的 source_id 改為 `{target}`（UPDATE，非 DELETE；回退：--rollback --execute）")

    if not args.execute:
        print("\nDRY-RUN，未寫入。確認無誤後加 --execute。")
        return 0

    r = urllib.request.Request(
        f"{URL}?{urllib.parse.urlencode({'id': id_filter()})}", method="PATCH",
        headers=headers({"Prefer": "return=representation"}),
        data=json.dumps({"source_id": target}).encode())
    with urllib.request.urlopen(r, timeout=60) as resp:
        changed = json.loads(resp.read())
    print(f"\nPATCH HTTP {resp.status} · 實際改動 {len(changed)} 行")
    for row in changed:
        print(f"  {row['id']} → source_id={row['source_id']}")

    total_after, old_after, new_after = count(), count(OLD_SOURCE), count(NEW_SOURCE)
    print(f"\n改動後：{OLD_SOURCE} {old_after} 條 · {NEW_SOURCE} {new_after} 條 · 全庫 {total_after} 條")
    ok = (len(changed) == 2 and total_after == total_before
          and count(other) == 0 and count(target) == old_before + new_before)
    print(f"守恆核對：改動行數 2 ✓ · 全庫總數不變 {total_before}=={total_after} "
          f"{'✓' if total_after == total_before else '✗'} · "
          f"兩邊相加不變 {old_before + new_before} {'✓' if ok else '✗'}")
    print("\n下一步：重跑 `python3 dev/source/check_registry_drift.py --check`（UNMANAGED 應為 0）"
          "，再 `set -a && . backend/.env && set +a && python3 dev/source/qc_report.py --check`"
          "（ERROR 應由 3 降至 2），然後 commit `qc_report.json`。")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
