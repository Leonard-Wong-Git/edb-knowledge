import json, sys, collections
from pathlib import Path
W = Path("dev/checklists/_work/kg_operation")
mp = json.load(open(W/"_section_map.json", encoding="utf-8"))["map"]
mp["盈餘上限"] = 13; mp["租金資助"] = 13   # agent omissions → finance
c = json.load(open(W/"checklist.json.pre_remap", encoding="utf-8"))

# canonical chapters; index 13 will be split into 4 finance sub-chapters by keyword
CANON = ["校舍選址與樓宇結構","園舍設施與設備","消防安全與走火","氣體、電力及機電安全",
"樓宇維修與環境衞生","兒童健康檢查與紀錄","疾病處理與傳染病防控","膳食與食物安全",
"意外、緊急事故與保險","兒童看管與保安","戶外活動與惡劣天氣安排","教職員聘任、資歷與師生比例",
"教職員健康、操守與專業發展","__FIN__","註冊、牌照與行政呈報","家校溝通與資料披露",
"紀錄保存、查閱與一般行政"]

FIN_SUB = [  # (chapter name, keyword list on item['section'])
 ("學費及收費", ["收費","學費","留位","報名","註冊費","額外","自願","代辦","活動收費","費用","半日","加費","回佣"]),
 ("採購及招標", ["採購","招標","標書","中標","競投","甄選","營辦商","辦團","防規避","防詐","單一"]),
 ("財務管理及內部監控", ["帳","銀行","支票","現金","憑單","付款","資產","盤點","內部監控","職務分工","職責分工","核數","周年","薪酬","零用","收入","收款","資金","存款","投資","關連","審核","盈餘禁轉","帳戶"]),
 ("資助運用、籌款及盈餘", ["資助","租金","租約","差餉","盈餘","籌款","捐","專款","專項","拆帳","成本","固定資產調撥","炊事","捐贈","商業活動","資金管理"]),
]
def fin_bucket(sec):
    for i,(nm,kws) in enumerate(FIN_SUB):
        if any(k in (sec or "") for k in kws): return i
    return 2  # default → 財務管理及內部監控

buckets = collections.defaultdict(list)  # key = (orderfloat, name)
fin = collections.defaultdict(list)
for s in c["sections"]:
    ci = mp.get(s["name"], 16)
    for it in s["items"]:
        if ci == 13:
            fin[fin_bucket(it.get("section",""))].append(it)
        else:
            buckets[ci].append(it)

new_sections = []
for ci, name in enumerate(CANON):
    if name == "__FIN__":
        for fi,(fname,_) in enumerate(FIN_SUB):
            its = fin.get(fi, [])
            if its: new_sections.append({"name": fname, "items": its})
    else:
        its = buckets.get(ci, [])
        if its: new_sections.append({"name": name, "items": its})

c["sections"] = new_sections
json.dump(c, open(W/"checklist.json","w", encoding="utf-8"), ensure_ascii=False)
print(f"remapped → {len(new_sections)} chapters, {sum(len(s['items']) for s in new_sections)} items")
for s in new_sections:
    print(f"  {s['name']}: {len(s['items'])}")
