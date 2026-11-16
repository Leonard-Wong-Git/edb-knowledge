# Playbook：路由清單覆蓋（route-coverage）

- **何時用**：QC 報 `REGISTRY_UNROUTED` 高於基準；人手入庫新來源之後；懷疑某來源「在庫但搜不到」。
- **建議模型**：分類由最強模型做；量度可交中階。
- **背景**：後端認出問題的類別後，只在該類別的 `SOURCE_SETS` 清單內搜尋。不在任何清單的來源，問題一觸發路由就搜不到。S250 查出 55 個來源（約 38% 片段）屬此情況。

## 步驟

1. **找出未入清單的來源**：`cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/check_registry_drift.py --check --ledger <scratchpad>/ledger.md`，看 `UNROUTED`。
2. **逐個分類**：

| 情況 | 處理 |
|---|---|
| 現行文件，數量少、片段少 | 加入 `backend/src/api/searchChannelB.ts` 內題材相符的現有 `SOURCE_SETS` |
| 現行文件，一大批同類（S250：37 份科目指引、4,881 片段） | **另設一條路由**（新 `SOURCE_SETS` ＋ `TOPIC_KEYWORDS`），不要塞進現有的大清單（原因見下） |
| 已被庫內新版取代，或與另一來源是同一份文件 | 不加入；寫入 `check_registry_drift.py` 的 `ROUTE_EXEMPT` 並註明原因；列為退役候選交 Leonard |
| 統計來源（`stat_*`） | 設計上不供搜尋，不用處理 |

3. **先量**（線上、未改動的版本，185 題約 22 分鐘，不涉模型開支）：
   `python3 dev/_s213_run_gold.py --gold dev/_s213_gold_all.json --out dev/source/eval_runs/<日期>_<名稱>_gold_before_prod.json`
4. **改路由**，然後 `cd backend && npm run check && npm run build`。
5. **算出哪些題目受影響**：把改動前後兩份 `TOPIC_KEYWORDS` 套在題庫每一題上，列出「路由改變」和「落在被改動的清單」的題目（做法見 S250 的 scratchpad 腳本 `routediff.mjs`，邏輯與 `dev/source/route_regression.mjs` 的 `detect` 相同）。路由和清單都沒有變的題目，結果不會變，不必重跑。
6. **再量受影響的題目**：起本機後端（launch 設定 `backend-s250-local`，即 `backend/scripts/_s250_localServer.ts`），用同一個量度腳本加 `--endpoint http://localhost:8787/api/search/channel-b`。
7. **比較**：逐題看判定（來源層、片段層、禁引）有沒有變。原本因逾時出錯的題目要在線上單獨重跑才算有基線。本機用 service key（8 秒）而生產用 anon key（3 秒），**只比較結果，不比較錯誤率**。
8. **抽查新增來源**：用它們的標題式問句各查一次，確認結果內有該來源，並記下回應時間。
9. **鎖住行為**：在 `dev/source/route_regression.mjs` 的 `CASES` 加入新路由的正例，以及「不可以被新路由偷走」的反例。
10. **合併與部署後**在線上再跑一次完整題庫，檔名用 `<日期>_<名稱>_gold_prod_after.json`。

## 為何不把一大批來源塞進現有清單（S250 實測）

把 45 個來源全部加入 `curriculum`（3,660 → 8,454 片段）：

- 「中學 八個學習領域」原本找到 `g13`，改後被高中科目指引擠走（題庫 PASS → FAIL）。
- 同一條查詢由約 1 秒變成 5–17 秒，線上 3 秒限制下會逾時。
- 改為另設 `subject_guides` 路由後：20 條受影響題目判定全部不變，12 條新來源查詢全部命中，回應 1–2 秒。

## 要留意

- **題庫不覆蓋的地方，量度會說「沒有變差」而不是「變好了」**：S250 的 37 個來源在 185 題內只有 1 題觸及，所以它們搜不到的問題一直沒有被題庫發現。新增一條路由時，要同時為它補題。
- **`dev/source/eval_runs/` 內的檔名會影響 QC**：`qc_report.py` 的 `EVAL_LATEST` 會選「檔名排序最後、打生產、有 PASS／FAIL／queries」的那一份。39 題的快速量度、本機量度、被否決方案的量度不要放進去，放 scratchpad。
- 新來源進入結果，必然擠走原本排在尾段的結果；這是預期之內。只有「原本答對、現在答錯」才算退步。
