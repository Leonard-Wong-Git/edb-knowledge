# 幼稚園營運（kg_operation）— 改寫覆核（QC verify issues）

> **✅ 全部 17 條 flag 已於 S163（2026-06-14）覆核並修正。** 詳列見下表（保留作 provenance）。
> 修法：刪去原文無嘅鋪墊／目的句及限定詞（虛構/加插）；補回漏咗嘅半段義務、還原適用主體（數字/義務走樣）；移除錯置引用（引用錯）。fix script：`dev/checklists/_work/kg_operation/_qc_fix.py`（exact-match + assert，全部 assertion 通過）。
>
> **同場修正一個 S162 結構 bug（非上述 17 條，QC 深挖揭發）：** `_work/kg_operation/clauses.json` 原用非標準 schema（`section_no`/`name`），而 14 個既有域 + 兩個 docx 生成器 + backend `checklistRevise` 全部期望 canonical `si`/`section_name`。後果：(1) `gen_checklists_bundle.py` 讀 `ch.si`→`None`，令 backend supplement linkage（`c.si === sectionIdx+1`）對 kg_operation **全部失效**（補回標準條文功能壞，388/388 items 拎唔到 clause）；(2) `gen_school_docx.js` 讀 `SECNAMES[ch.si-1]`→`undefined`，學校版 docx **章節名全空**（似 S159「undefined」bug）。已將 clauses.json 正規化為 `si`/`section_name`，重生 4 docx + bundle + manifest。驗證：bundle si=1–20、supplement linkage **388/388**（修前 0/388）、學校版 docx 20 章名齊。
>
> S162 幼稚園清單 pilot 自動產出。每章改寫後經獨立對抗覆核員（預設有錯、python3 機械＋語意比對）檢查。
> **S162 已自動修：** 全部「法團校董會（未設者為校董會）」→「校董會」（幼稚園無法團校董會；10 處 clause text + 12 處 adjustables）。
> 文件本身為 DRAFT 草擬本，已註明「如與教育局原文有出入，概以原文為準」。

## ✅ 已修（S163）— 下表為原 flag provenance

| 章 | 章名 | 類型 | item | 說明 |
|---|---|---|---|---|
| 1 | 校舍選址與樓宇結構 | 虛構/加插 | 0 | Clause 0 (covers 12,5,0) appends an obligation not in the source: 「故本校於選址時須避免採用結構性木地板的房產」. Item 0's source only states the regulatory consequence (當局將拒絕根據《教育條例》第12(1)(b)條發出證明書); it… |
| 2 | 園舍設施與設備 | 虛構/加插 | 0 | Clause 0 (covers 0,1,2,15) 開首加咗『本校洗手間的設計與裝修須符合衞生及安全標準。』呢句概括性義務句喺所被覆蓋嘅 item 0/1/2/15 嘅 req 同 quote 都搵唔到對應出處——item 只講具體規格（窗口面積1/10、一米瓷磚、防滑地磚、廁所分開、洗手盆比例），冇『須符合衞生及安全標準』呢條獨立 obligation。… |
| 5 | 樓宇維修與環境衞生 | 虛構/加插 | 4 | clause0 (covers 4,5) 加咗原文無嘅鋪墊語句「本校重視校園環境的安全與衞生」同結尾「讓幼兒在妥善照顧下成長學習」。source quote(item4「提供一個安全、健康和安排妥善的校園環境」/item5「幼稚園應保持校舍環境的衞生」)只係義務句，無此目的/態度框架語。屬輕度 fabricated 修飾，無加新義務或數字，但係 source… |
| 5 | 樓宇維修與環境衞生 | 虛構/加插 | 1 | clause2 (covers 1,2) 加咗原文無嘅目的鋪墊「為維持環境衞生及保障幼兒健康」。source quote 只係操作義務(漂白水1:99清潔 / 每星期更換床單),無此目的句。輕度 fabricated 修飾語,數字/時限本身保真。 |
| 5 | 樓宇維修與環境衞生 | 虛構/加插 | 3 | clause3 (covers 3) 加咗原文無嘅結尾目的句「確保用水安全衞生」。source quote 只到「…或其他認可的水源供應」為止,無此補充目的語。輕度 fabricated 修飾,核心義務(自來水喉/認可水源)保真。 |
| 6 | 兒童健康檢查與紀錄 | 引用錯 | 0 | clause0 covers items [0,1]（兩者源 kg_operation_manual_2026 p28/p29），但 citations 列咗 kg_admin_guide_2026 p47。p47 係 item 3 嘅源（item 3 喺 clause1 covered），唔屬 item 0/1。此 citation 喺 clause0 c… |
| 6 | 兒童健康檢查與紀錄 | 數字/義務走樣 | 3 | item 3 req 兩項義務：(a) 妥善保存學童個人健康紀錄及員工病假紀錄，(b) 定期檢查及記錄體溫。covering clause 應為 clause1（covers [2,3]）。但『定期檢查及記錄兒童體溫』被放入 clause0（covers [0,1]）；clause1 完全冇『體溫』字眼。item 3 嘅體溫義務脫離咗其 covering c… |
| 6 | 兒童健康檢查與紀錄 | 虛構/加插 | 1 | clause0 將入學前體格檢查寫成『由註冊醫生進行的全面體格檢查』，但 item 1 quote（p29）只有『一項全面的體格檢查』，並無『註冊醫生』限定。『註冊醫生』只出現於 item 4（留宿兒童 p90）context，被錯加到 item 1 嘅入學前檢查 → 加咗源唔支持嘅限定/義務語。 |
| 6 | 兒童健康檢查與紀錄 | 虛構/加插 | 0 | clause0 加咗 item 0 源唔支持嘅語句：『每日』（頻率限定，quote 只說『當兒童返抵園舍』無『每日』）及『方可入班』（一個入班 gating 後果，quote 只說『待確定他們身體健康後』，無入班條件後果）→ 情態/義務加強，源未支持。 |
| 9 | 意外、緊急事故與保險 | 數字/義務走樣 | 0 | clause0 (covers 0,1,6,2) 把 item0「所有留宿幼兒中心」同 item6「所有獨立幼兒中心」嘅適用主體一律改成通用「本校」，抹走咗中心類型／適用層級嘅限定，等於把專屬留宿／獨立幼兒中心嘅三個曆日特別事故呈報義務擴大到一般幼稚園。三個曆日（包括公眾假期）時限本身保留正確，但適用層級被改／含糊。 |
| 9 | 意外、緊急事故與保險 | 虛構/加插 | 7 | clause3 加咗「本校指派專人負責管理急救箱」呢項源文無嘅義務。item7 原文只係「負責管理急救箱的人士須確保…」，並無規定學校須『指派專人』；改寫無中生有一項委派義務（雖以 adjustable『指派專人』略作軟化，但仍屬源文唔支持嘅情態／義務加入）。 |
| 13 | 教職員健康、操守與專業發展 | 虛構/加插 | 14 | Clause 1 (covers 0,13,14,23) 喺「本校接受任何利益和捐贈，必須獲本校管理當局批准」後加咗「（經教育局核准的註冊費不屬利益）」。此 carve-out 原文只屬 item 4（quote:「學生的錄取或升級（經教育局核准的註冊費不屬利益）」），語境係學生錄取/升級時索取利益，唔屬捐贈批核語境。item 14 quote 只係「學校接… |
| 13 | 教職員健康、操守與專業發展 | 數字/義務走樣 | 23 | item 23 req=「遵守教育局通告...並參考廉署校董及職員行為守則範本」（兩段義務）。Clause 1 只寫「遵守教育局有關《學校及其教職員收受利益和捐贈事宜》通告的規定」，遺漏咗「參考廉署校董及職員行為守則範本」呢半段義務。屬層級/義務元素脫落（非數字，但屬 req 要素含糊/漏）。 |
| 13 | 教職員健康、操守與專業發展 | 數字/義務走樣 | 7 | item 7 quote 含兩段時限義務:「即時向中心管理人員報告；並在調查或訴訟完結後，即時向中心管理人員報告結果」。Clause 6 表格 row2(對應 item 7)只寫「管理人員須要求員工即時向中心管理人員報告」，遺漏咗「調查/訴訟完結後即時報告結果」呢段後續匯報時限義務（row1 雖泛言完結後報告但主體係教職員向本校，唔等同員工向中心管理人員嗰條… |
| 15 | 採購及招標 | 虛構/加插 | 1 | 覆蓋 [1,2,8] 嗰條 clause 開頭加咗目的語句「為確保採購過程廉潔及問責，本校須…」。原始 item 1/2/8 嘅 req+quote 完全無「廉潔」「問責」「為確保」呢類目的/理由語句（python3 全源比對：源文無此詞）。屬 source 唔支持嘅目的語句加插。 |
| 15 | 採購及招標 | 虛構/加插 | 15 | 覆蓋 [14,15] 嗰條 clause 將批核機關寫成「須先得到法團校董會（未設者為校董會）的批准」。原始 item 15 quote/req 只講「校董會」，全源從無出現「法團校董會」（grep 確認 0 次）。憑空加入「法團校董會（未設者為校董會）」呢個審批機關／層級，源文唔支持；且幼稚園情境一般無法團校董會（IMC 屬中小學概念），屬虛構並扭曲審批層… |
| 15 | 採購及招標 | 虛構/加插 | 16 | 覆蓋 [16,17] 嗰條 clause 將授權安排批准機關寫成「事先得到法團校董會（未設者為校董會）的批准」。原始 item 16 quote/req 只係「校董會」。同上，源文全無「法團校董會」，屬加插源文唔支持嘅審批機關／層級。 |

**合計：原 17 條 flag，分佈 7/20 章（其餘 13 章覆核全清）→ S163 全部已修。**

## 修法（S163 已套用）
- **虛構/加插**：刪去原文無嘅鋪墊／目的句（「為確保採購過程廉潔及問責…」「本校重視校園環境…」「為維持環境衞生…」）或限定詞（「註冊醫生」「每日」「方可入班」「指派專人」「結構性木地板房產須避免」「洗手間設計須符合衞生及安全標準」「確保用水安全衞生」「註冊費不屬利益」carve-out），數字/時限本身已保真。
- **數字/義務走樣**：ch6 體溫紀錄移回其 covering clause1、ch13 補回「參考廉政公署《校董及職員行為守則範本》」+ 表格補「調查/訴訟完結後即時報告結果」、ch9 還原適用主體（留宿/獨立幼兒中心專屬，勿擴大到一般幼稚園）。
- **引用錯**：ch6 clause0（covers 0,1）移除誤列 kg_admin_guide_2026 p47（屬 item3 源）。

> 改 clauses.json 後 re-run：`node gen_school_docx.js kg_operation [kindergarten]` + `node gen_checklist_docx.js kg_operation [kindergarten]` + `python3 dev/checklists/_work/gen_checklists_bundle.py` + `python3 dev/checklists/_work/gen_templates_manifest.py`。
