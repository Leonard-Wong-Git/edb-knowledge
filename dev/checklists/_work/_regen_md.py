import json
from pathlib import Path
W = Path("dev/checklists/_work/kg_operation")
OUT = Path("dev/checklists/kg_operation/DRAFT_checklist_kg_operation.md")
c = json.load(open(W/"checklist.json", encoding="utf-8"))
cn = c["cn"]
L = [f"# 校本「{cn}」政策文件 — 要求清單（DRAFT v0.1）", "",
     "> **狀態：DRAFT，待 Leonard 審。** S162 幼稚園清單 pilot 產出（2026-06-14）。",
     "> 來源：《學前機構辦學手冊》＋《幼稚園行政手冊》(2026)。範疇＝幼稚園營運與行政義務（收生屬 kg_admission、課程屬 curriculum，不重複）。",
     "> 生成方法同 14 域：蒸餾 → 獨立對抗覆核 → 完整性批判 → 本機機械重驗（exact→去空格→NFKC 三級引文比對＋頁碼重計）→ 章節整合。每條必帶原文引文。", "",
     "## 來源文件", "", "| source_id | 文件 | 連結 |", "|---|---|---|"]
for sid,(title,url) in c["src"].items():
    L.append(f"| `{sid}` | 《{title}》 | [開啟]({url}) |")
L += ["", "## 要求清單", ""]
total=0
for si,sec in enumerate(c["sections"],1):
    L.append(f"### {si}. {sec['name']}"); L.append("")
    for j,it in enumerate(sec["items"],1):
        total+=1
        title,url=c["src"][it["source_id"]]
        if it.get("no_page"):
            cite=f"《{title}》（無頁碼源） — [開啟原文]({url})"
        else:
            flag=" ⚠️頁碼近似" if it.get("approx") else ""
            cite=f"《{title}》第 {it['page']} 頁{flag} — [開啟原文]({url}#page={it['page']})"
        add="（覆核補遺）" if it.get("addendum") else ""
        L.append(f"- **R-{si}.{j}** {add}{it['req']}")
        L.append(f"  - 出處：{cite}")
        L.append(f"  - 引文：「{it['quote']}」")
    L.append("")
L += ["## 覆蓋度與 QC 紀錄","",
      f"- 條目總數：**{total}**；章節：{len(c['sections'])}；本機機械重驗全通過（fail 已剔）。",
      "- 範疇 scope：幼稚園/學前機構營運與行政（校舍/安全/衞生/健康/膳食/人事/財務/註冊/家校溝通/紀錄）。",
      "- 本清單係指引義務蒸餾，唔係法律意見；源文件改版須重新派生。",""]
OUT.write_text("\n".join(L)+"\n", encoding="utf-8")
print(f"regen md: {total} items, {len(c['sections'])} chapters → {OUT}")
