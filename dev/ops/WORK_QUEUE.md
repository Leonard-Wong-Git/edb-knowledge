# 工作清單（EDB K1 知識平台／policychecker）

> **本檔的角色**：所有待辦事項的唯一清單，每項都寫成可以照做的工作卡。由最強模型（Fable 5.2）於 2026-11-16（S251）一次過寫好，供之後任何模型跟進。
> **不是**現況權威（現況看 `dev/SESSION_HANDOFF.md` 的 `## Current Baseline`），**不是**規則本身（規則看 `AGENTS.md`、`dev/rules/safety.md`、`dev/ops/AUTONOMY_FLOW.md` §4a）。
> **提升搜尋準確度的計劃不在本檔**，在 `dev/ops/NEXT_UPGRADE.md`（只在有較強模型或 Leonard 明示時才做）。
> **更新時機**：做完一張卡、Leonard 作了一個決定、或出現新待辦時。做完的卡把狀態改為「✅ 完成（日期、PR 編號）」，保留一行，其餘內容刪去。
> **系統目標**（Leonard，S243／S249／S251）：平台各環節自行運作，人手只在真正要判斷或有風險的地方介入；要人手維護又沒有人用的功能，傾向刪除。**用戶**是香港學校的校長、教師與行政人員，多數只打一至三個詞的短查詢，要的是準確、有出處、可點擊到原文頁數的答案。

## 0. 怎樣用這份清單

每一節（session）照這個次序做：

1. **開工**：讀 `dev/SESSION_HANDOFF.md`，然後按 `dev/ops/playbooks/health-probe.md` 做起手探針。探針的停止條件觸發就先報告，不做其他事。
2. **提 Leonard 用哪個模型與 effort**：揀定工作後、動手之前，按下表告訴他建議的模型與推理強度，並說明現時 session 是否相符；不相符就請他切換，等他回覆。規則與原因見 `dev/ops/AUTONOMY_FLOW.md` §4b。
3. **揀工作**：Leonard 有指定就做指定的；沒有指定，就由 A 部由上而下揀第一張狀態為「可做」的卡。**一節只做一張卡**，做完還有餘力才做下一張。
4. **做**：照卡內步驟。每張卡都有「驗收」與「停止條件」；停止條件觸發就停，把情況寫進本卡的「備註」，不要即興補救。
5. **交付**：一張卡一個分支、一個 PR（`main` 受保護，不能直接推）。**合併只在 Leonard 明示時進行。**
6. **記錄**：更新本檔該卡的狀態；Leonard 說「收工」時按 `dev/rules/closeout.md` 做收工。

各卡建議的模型與推理強度（主力為 Opus 5.5；未經實測，見 `AUTONOMY_FLOW.md` §4b）：

| 工作 | 建議 |
|---|---|
| 起手探針、收工、A9、A10 | **low**（或 Haiku 5.5／Sonnet 5.5） |
| A1、A4、A7、A8、A12 | **medium** |
| A2、A3、A5、A13 | **medium**；卡內停止條件觸發時改 **high** 再看一次 |
| A6（註腳與原文比對）、B 部執行寫入或刪除生產資料的步驟 | **high** |
| A11、`dev/ops/NEXT_UPGRADE.md` 第 0、3、4 階段 | **xhigh** |

通用硬規則（任何卡都適用，與卡內文字衝突時以此為準）：

- 未得 Leonard 明示批准，不得：寫入或刪除 Supabase 生產資料、改旗標、執行 DDL、作外部模型批次、合併 PR。
- 寫生產資料只用有預演（dry-run）與讀回的工具；先全欄位備份到 `dev/init_backup/<UTC時間>/`。
- 路徑含空格，終端機指令一律用雙引號包住；一律先 `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`。
- 抽取、入庫、寫 Supabase 的腳本用 `/usr/local/bin/python3`；純檢查腳本用 `python3` 亦可。
- 金鑰在 `backend/.env`，不得印出。真實搜尋紀錄（`public.search_log`）的內容不得公開或寫入 git。
- 升版只手改 `app.html` 的 `PLATFORM_VERSION`、README 標章與 CHANGELOG；不可用 `bump_version.py`。
- 給 Leonard 的報告用白話：先說結果與影響，再附證據。不要把未分類的原始清單交給他。

狀態用語：**可做**（照卡做即可）· **待 Leonard**（要他答一句才可動）· **等觸發**（條件出現才做）· **不要做**（已量度並否決）。

---

## A. 可以直接做的工作（按次序）

### A1　把「註腳更正」與「連結覆寫」接入每日質素檢查　【✅ 完成（2026-11-17，S252）】

- **目的**：註腳入庫腳本一旦以 `--execute` 重跑，已更正的文字和頁碼會被舊版蓋回去。現時只有人手跑工具才發現。要令每日 `qc_report` 自動發現並通知 Leonard。
- **改哪裏**：`dev/source/qc_report.py`。
- **做法**：
  1. 讀 `check_page_anchor`（約第 363 行）與 `REGISTRY_UNROUTED` 在 `BASELINE`、`BASELINE_OF` 的寫法，照同一模式新增兩個檢查：
     - `FOOTNOTE_CORRECTIONS`：讀 `dev/source/footnote_corrections.json`，逐個 id 在已載入的 `chunks` 找同 id 的片段；`text` 與清單不同、或找不到該片段，即計為一個違規。
     - `URL_OVERRIDES`：讀 `dev/source/url_overrides.json` 的 `overrides`，逐個 id 比對片段的 `url`；不同或找不到，即計為一個違規。
  2. 兩者嚴重程度 `ERROR`，基準 0（`BASELINE` 加 `footnote_corrections_drift: 0`、`url_overrides_drift: 0`，並加入 `BASELINE_OF`）。違規清單列出 id。
  3. 先確認 `qc_report.py` 取片段時有選取 `text` 與 `url` 兩欄（搜尋 `select=`）；沒有就加上。
  4. 自測（`--self-test`）內有一條斷言寫明「`BASELINE_OF` 涵蓋八個片段層檢查加 `REGISTRY_UNROUTED`」（約第 1455 行）；新增兩個檢查後要相應改這條斷言，並為兩個新檢查各加「一致時 0、改動一條時 1」的測試。
  5. 更新 `dev/ops/playbooks/qc-regression-triage.md` 的對照表：這兩項高於基準時，處理方法是跑 `dev/apply_footnote_corrections.py` 或 `dev/apply_url_overrides.py`（先預演，Leonard 批准後 `--execute`）。
- **驗收**：`python3 dev/source/qc_report.py --self-test` 全部通過；本機完整跑一次，兩個新檢查皆 0；暫時把清單檔的某條文字改一個字再跑，該檢查變 1（之後還原）。
- **停止條件**：自測有任何一條原有斷言失敗而你看不出原因——還原改動，報告。

### A2　註腳出處每月自動核對（不用模型）　【✅ 完成（2026-11-17，S252）】

- **目的**：S250 的註腳審核靠模型逐條讀，之後未必有模型可用。改為機械核對：每條註腳記下一句「錨句」（原文原句）與頁碼，每月下載原文，檢查錨句是否仍在該頁。原文換版、搬頁、失效都會被發現（例如 S251 的學資處網頁由 2025/26 換成 2026/27）。
- **新增檔案**：
  - `dev/source/footnote_anchors.json`：`{ "<註腳 id>": { "url": "…", "page": 3, "quote": "…" } }`。網頁類 `page` 為 `null`。
  - `dev/source/check_footnote_anchors.py`：核對工具。
  - `.github/workflows/footnote_anchor_check.yml`：每月一次（建議 `0 13 2 * *`）。
- **做法**：
  1. **建立錨句檔**：由 `dev/source/eval_runs/2026-11-16_s250_footnote_audit.json` 取結論為「相符」與「頁碼不對」的條目，`quote` 用其 `matched_quote`，`page` 用 `page_found`，`url` 用 Supabase 現時該註腳的 `url`（去掉 `#page=`）。S251 更正的 10 條，`quote` 用 `dev/source/footnote_corrections.json` 內 `basis` 所引的原句。結論為「找不到」的 13 條不放入（見 A6）。
  2. **工具邏輯**：每份文件只下載一次、相隔約 1 秒、失敗重試一次。PDF 用 PyMuPDF 逐頁抽文字；網頁抽主內容文字。比對前雙方做 NFKC 正規化並去掉所有空白。每條得出一個結果：
     - `OK`：錨句在所記頁。
     - `MOVED`：錨句在同一文件的另一頁（列出新頁）。
     - `GONE`：整份文件都找不到錨句（原文可能已換版）。
     - `FETCH_FAIL`：下載失敗（列出 HTTP 狀態）。
  3. 提供 `--self-test`（離線，用假文件測四種結果）與 `--only <id>`。輸出 JSON 與一份簡表。預設唯讀，沒有任何寫入模式。
  4. **工作流程**：仿 `.github/workflows/title_check.yml`（同是每月、同樣要下載文件），有 `MOVED`／`GONE` 時用 `.github/scripts/notify_new_items.js` 開或更新 Issue（標籤 `footnote-anchor`）並 @Leonard；全部 `OK` 時自動關閉。`FETCH_FAIL` 連續兩次才通知。
  5. **接入看門狗**：在 `dev/source/check_monitor_health.py` 登記這個新排程，跑它的 `--self-test` 與 `--prove-assertions`。
  6. 更新 `dev/ops/AUTONOMY_FLOW.md` §2、§3、§5 與 `dev/ops/playbooks/footnote-audit.md`（說明月檢由機器做；`MOVED` 改 `url_overrides.json`；`GONE` 把新舊原文並列交 Leonard）。
- **驗收**：`--self-test` 通過；本機全量跑一次，S250／S251 已核實的條目應為 `OK`，不是 `OK` 的逐條列出交 Leonard，不要自行改註腳。
- **停止條件**：全量跑出超過 15 條非 `OK`——多半是比對邏輯有問題而非原文變了，先抽 3 條人手對 PDF 查明，再決定。

### A3　來源有變但文字相同時自動確認　【✅ 完成（2026-11-17，S252）】

- **目的**：每週的 Freshness 監察報「來源有變」，但 S249 處理的 19 項中有 11 項只是原文重新匯出、文字完全相同，要人手逐項確認。令機器自動確認這一類。
- **先讀**：`dev/source/FRESHNESS_GUIDE.md`（`--ack` 與指紋的意思）、`dev/ops/playbooks/freshness-triage.md`、`dev/SESSION_LOG.md` 內 S249 的條目（找當時用來逐頁比對的做法）。
- **做法**：在 `dev/source/check_freshness.py` 的排程路徑加一步：對指紋有變的 PDF 來源，下載新版，用與 vault 抽取檔相同的抽取方法逐頁抽文字，與 `dev/vault/<來源>/` 的現有抽取檔比對（NFKC、去空白後逐頁相等）。**完全相等**才自動確認基線並在輸出記一行「已自動確認：文字相同」；有任何一頁不同、頁數不同、或抽取失敗，一律不確認，留在清單等人處理。網頁類來源維持現狀，不納入。
- **驗收**：`--self-test` 加三個個案（相同→確認；一字不同→不確認；頁數不同→不確認）並通過；全量 dry-run 的錯誤數為 0。
- **停止條件**：找不到 S249 當時的比對方法，或不確定抽取方法是否與入庫時一致——停。用不同抽取器比對會誤判為「不同」（安全）或「相同」（危險），不可猜。

### A4　補回 `backend/README.md` 的旗標說明　【✅ 完成（2026-11-17，S252）】

- **目的**：S215 遺失了 5 行旗標說明，沒有備份。
- **做法**：由 `backend/src` 內實際讀取的環境變數重寫（`grep -rn "process.env" backend/src`），每個旗標一行：名稱、預設值、作用、現時生產是否開啟（對照交接檔 `## Current Baseline` 5）。「不應啟用」的旗標要註明已量度並判定不出貨。
- **驗收**：README 列出的旗標與程式內讀取的完全對應；commit 訊息寫明「重寫，並非還原」。

### A5　為科目指引路由補題　【✅ 完成（2026-11-17，S252）】

- **結果**（S252）：10 題（`dev/_s252_gold_subject_guides.json`，6 題 dev、4 題 held_out），驗證 10／10 通過；生產首個基線來源層 10／10、片段層 4／10（`dev/source/gold_baselines/`）。片段層的 6 題都是取得正確文件、但不是答案那一段，與 `dev/ops/NEXT_UPGRADE.md` §1 的甲、乙兩類相同。`體育選修科 理論部分課時` 不觸發任何路由（全庫搜尋），仍取得正確文件。


- **目的**：S250 新增的 `subject_guides` 路由有 37 個來源，但 185 題題庫只有 1 題觸及，量度只能證明「沒有變差」。
- **先讀**：`dev/DOC_SYNC_CHECKLIST.md`「檢索準確度量度改動」一列；現有題庫檔 `dev/_s213_gold_*.json` 的格式；`dev/ops/playbooks/route-coverage.md`。
- **做法**：為其中 10 個來源各擬一條短查詢（一至三個詞，貼近教師實際會打的字，例如科目名加「課程指引」「評估」「課時」）。每題的正確答案段落必須由你**讀原文片段後**指明，不可憑題目猜。新題先跑 `_s213_validate_gold.py`；不通過的題目隔離，不要為通過而改標籤。
- **驗收**：驗證腳本通過；在生產跑一次這 10 題（帶 `x-probe: 1`，每題相隔 8 秒），記錄 PASS／FAIL 作為這批題目的首個基線。**不要把這次結果與 185 題的基線合併比較。**
- **停止條件**：不肯定某題的答案段落——該題不要加入。

### A6　13 條「找不到出處」的註腳　【✅ 完成（2026-11-17，S252）】

- **結果**（S252，原文逐條讀過）：(a) 11 條《教育條例》第 279 章條文（s10、11、13、14、42、46、47、48、50、52、61）以瀏覽器讀 e-Legislation，**與註腳逐字相符**；其中 s14 只列出 (b)(c)(d) 三項理由，原文另有 (g)(i)–(l)(n)–(p) 及第 (2) 款，問「拒絕理由有咩」時答案不完整（語意取捨，交 Leonard）。(b) `g11_schooldays`：190／209／91 日三個數字皆在《一般學校假期及上學日數的計算方法》PDF 第 1 頁（2026 年版），只是連結指向索引頁 → 已按 B15 更正（2026-11-17）。教訓：連結覆寫要與寫入同一 PR 完成，未套用的覆寫若先放進 `url_overrides.json`，每日漂移檢查會當成「被蓋回」而開警報。(c) `ceg_no_tutorial`：原句在 EOEBG 使用指引第 6 頁與 OEBG 使用指引第 7 頁 → 見 B8。
- **月檢**：e-Legislation 頁面由 JavaScript 產生，月檢工具抓不到，所以 11 條法例註腳不加錨句（加了會每月報下載失敗）。`g11` 的錨句（「因此全年上學日數不應少於209日」，PDF 第 1 頁）隨 B15 一同加入。


- **目的**：S250 審核有 13 條因抓不到原文（多為電子版香港法例，頁面由 JavaScript 產生）而未能核對。
- **做法**：由 `dev/source/eval_runs/2026-11-16_s250_footnote_audit.json` 列出結論為「找不到」的 13 條。逐條用瀏覽器工具打開 `url`，讀到原文後，把註腳的數字、條文編號、條件與原文並列。只做並列與分類（相符／數字不同／原文沒有此說法／打不開），**不要改寫註腳**。
- **交付**：一份表交 Leonard。可逐字對照的更正（數字、條文編號）可同時備妥 `footnote_corrections.json` 的預演。

### A7　`/health` 的註腳載入時間不更新　【✅ 完成（2026-11-17，S252）】

- **現象**（S251 實測）：寫入註腳更正約 8 分鐘後，線上搜尋已回傳新文字，但 `/health` 的 `footnote_loaded_at` 仍是 30 多分鐘前的時間。
- **做法**：讀 `backend/src/lib/wikiRepository.ts` 約第 484–560 行與第 852 行。先只報告觀察到的事實：背景重讀成功後 `_footnoteLoadedAt` 有沒有被設定、`/health` 讀的是不是同一個變數、是否有多個執行個體。確定是顯示問題才改；改後要通過 `cd backend && npm run check && npm run build && npm run regression:overlay`。
- **停止條件**：看不出成因——只把觀察寫入本卡備註，不改碼。
- **備註**（S252）：`/health` 讀的與重讀成功後設定的是同一個變數；`/health` 本身不觸發重讀，要有搜尋請求在期滿後到達才會；重讀**失敗**時舊碼會把一個虛構的時間寫進顯示（已用離線測試重現並在 PR #111 修正，另加 `footnote_refresh_failed_at`）；只見一個執行個體，免費層閒置約 15–20 分鐘即休眠重啟。未能證實失敗路徑就是 S251 所見現象的成因（當時沒有記下 `started_at` 與後端日誌）。

### A8　瀏覽清單的累積差異　【✅ 完成（S252 #116 執行五項決定；餘下入庫由 A14 完成）】

- **結果**（S252）：36 項 PHANTOM 與 119 項 UNLISTED 全部分類，每項一個建議，見 `dev/ops/decisions/2026-11-17_A8_browse_list.md`（共五個是／否決定）。批准後按該檔「批准後做法」分批執行。


- **現況**：`PHANTOM` 36（瀏覽清單有、庫內零片段）、`UNLISTED` 119／2,626 片段（搜尋得到、「EDB 指引」瀏覽不到）。兩者是待辦清單，不是故障。
- **做法**：`python3 dev/source/check_registry_drift.py --check --ledger <scratchpad 路徑>` 取得清單（`--ledger` 一定要指向 repo 以外）。每次處理 20 項，為每項給出一個建議：
  - `UNLISTED`：屬指引、手冊、通告類而且用戶會想瀏覽的→建議加入 `app.html` 的 `GUIDELINES_REGISTRY`；屬表格、統計、註腳來源的→建議不列。
  - `PHANTOM`：瀏覽條目指向的文件是否已由另一個 id 承載（`ROUTE_EXEMPT` 內有說明的屬此類）→建議移除重複的瀏覽條目。
- **交付**：一份表（id、標題、片段數、建議、一句理由）交 Leonard 批准後才改 `app.html`；改後 README 的數目、`guidelines.json` 是否受影響，按 `dev/DOC_SYNC_CHECKLIST.md` 處理。

### A14　10 份「瀏覽清單有、庫內沒有」的現行文件入庫　【✅ 完成（9 份 2026-11-17 S252；`staff_est_sp_sch_pri` 2026-11-19 S254）】

- **結果**（S252）：9 份入庫，共 238 片段（17,084 → 17,322；來源 325），每份讀回數目與預演相同。路由：語文、數學、普通話入 `curriculum`（高中數學另入 `subject_guides`），公積金三份入 `hr_admin`。
- **`staff_est_sp_sch_pri`（S254 完成，Leonard 批准）**：28 片段入庫（15,828 → 15,856；來源 315），PHANTOM 1 → 0。「12班小學有幾多個學位教師」生產 3/3 答 5 名。**更正原卡前提**：`FEATURE_SUBJECT_CHECK` 擋不住 S204 那次錯答（問題判為「教師」，特殊學校表亦提及教師，故通過）；這次不再答錯，是因為 `staff_est_pri` 現排第 1（S204 時排第 6）。若日後 `staff_est_pri` 跌出前五，錯答可能重現 —— 回退：按 source_id 刪這 28 列（入庫前 0 列，備份 `dev/init_backup/20261119_114957_UTC/`）。**未解**：「特殊學校小學部有幾多個學位教師」被 `sen` 路由（關鍵字「特殊學校」）攔走，`sen` 清單無此表，取不到；見 A18。


- **文件**：`chi_pri_lo_2023`、`chi_sec_lo_2021`、`ma_pri_content_2017`、`ma_jss_content_2017`、`ma_sss_content_2017`、`pth_guide_2017`、`gspf_general_info_2023`、`sspf_general_info_2023`、`pf_edu_ord_2013_faq`、`staff_est_sp_sch_pri`（後者 registry 原標 `held_back`，Leonard 2026-11-17 批准入庫）。
- **做法**：一次一份，按 `dev/ops/playbooks/source-reingest.md` 或 Option A 入庫流程；每份入庫後確認它離開 PHANTOM、在 `SOURCE_SETS` 內（UNROUTED 0）、更新日誌加一條。部分未有 registry 項目，要先登記。
- **驗收**：`check_registry_drift.py --check` 的 PHANTOM 由 10 降至 0；每份以一條相關短查詢在生產取得該文件。

### A18　「特殊學校小學部編制」問法取不到 `staff_est_sp_sch_pri`　【✅ 完成（2026-11-22，S255；PR #129，生產驗收通過）】

- **現象**：問題含「特殊學校」即觸發 `sen` 路由，生產前八段不含本表。
- **原定做法無效**：把表加入 `sen` 清單後，本機實測前 30 段仍沒有本表 —— `sen` 的展開詞全是融合教育詞彙，把向量拉向 g06／g19。已撤回。
- **實際做法**：`TOPIC_KEYWORDS.staffing` 加「幾多／多少（個名位）（學位／文憑）教師／教員／老師」問人數條件（排除含「幼」的問題，因 `staffing` 清單只有中小學）。`staffing` 排在 `sen` 之前，且無展開詞。
- **量度**：`route_regression` 96/96（新增 6 條，改碼前紅 3 條）；已存 504 條 gold／eval 題路由變動 0；本機（旗標同生產）目標題第 3–5 段為本表，`sen` 對照題五條排名不變，「12班小學有幾多個學位教師」排名不變。證據 `dev/source/eval_runs/2026-11-22_s255_a18_route.json`。
- **未解（另一問題）**：本機合成對「特殊學校小學部有幾多個學位教師」及「6班特殊學校小學部…」皆拒答（後者改動前已走 `staffing`），不會答錯。
- **驗收 ✅**：`63a45d6` 部署後（2026-11-22T11:11Z）生產重跑同一組探測，目標題第 3–5 段為本表；其餘 7 條對照題排名與改動前完全相同。

### A15　重新定標 3 條暫停的題庫題目　【✅ 完成（2026-11-17，S252）；題庫回到 185 題】

- **結果**：三題改標並放回題庫（`cur_eight_kla` → 16 份含同一句的課程指引；`cur_four_key_project_stages` → `g13`；`cur_moral_civic_values` → `g13`／`sec_curr_guide_2017_booklet_6a`），驗證器通過；生產來源層 3／3、片段層 1／3。


- **背景**：S252 退役 g07 後，`cur_eight_kla`、`cur_four_key_project_stages`、`cur_moral_civic_values` 失去唯一答案來源，已移至 `dev/source/gold_deprecated_s252.json`（題庫 185 → 182 題）。
- **做法**：在 `g13`（中學教育課程指引 2017）、`sec_curr_guide_2017_booklet_6a`、`pri_curr_guide_2024` 找對應段落（S252 已見 g13 有「八個學習領域」與「專題研習的三個階段」、booklet 6A 有責任感定義），讀原文確認後按 `_s213_validate_gold.py` 流程改標並放回題庫。

### A16　《中國語文教育學習領域課程指引》2024 年版入庫，之後退役 2017 年版　【✅ 結案：前提不成立（2026-11-18，S253）；g08 標題已更正】

- **備註（S253，2026-11-18）**：沒有 2024 年版。教育局「中國語文教育－課程文件」頁（中、英文）現時只列 2017 年版（`CLEKLAG_2017_for_upload_final_R77.pdf`），全頁沒有「2024」。`g08` 的連結是「學校課程規劃及教學示例」頁，屬 2017 年版指引的示例；該頁唯一的「2024」是頁面修訂日期（28/08/2024）。所以 `g08` 標題的「(2024)」是誤標，2017 年版仍是現行版本，**不入庫、不退役**。另：2023 年的小學、初中《中國語文課程指引》（`chi_pri_guide_2023`、`chi_jss_guide_2023`）是科目指引，不取代學習領域指引。誤標出現在 `app.html` `GUIDELINES_REGISTRY`、`dev/source/source_registry.json` 與 `guidelines.json` 三處；Leonard 批准後三處一併更正為「《中國語文教育學習領域課程指引（小一至中六）》學校課程規劃及教學示例」、簡稱「中文課程規劃示例」、年份 2017（`guidelines.json` 的 `_meta` 不動，與 S238 #49 的先例相同）；`check_downstream_sync` `MUST_UPDATE` 0。

- **背景**：庫內服務的是 2017 年版（`chi_edu_curr_docs`，157 片段）；2024 年版只在瀏覽清單（`g08`，連結是課程文件總頁），未入庫。
- **做法**：先在總頁找到 2024 年版 PDF，按 A14 的做法入庫，然後按 `source-reingest.md`「入庫新版時順手退役舊版」處理 2017 年版。

### A17　題庫 25 題的「核實片段編號」已過時　【✅ 大部分完成（2026-11-17，S252）；8 題見 B16】

- **結果**：以原簽名在 2026-11-17 快照找回現行片段，更新 `verified_by.chunk_id` 與 `expected_page`（五個題庫檔共 35 處，簽名一字未改）。驗證器 160／185 → **177／185**。


- **現象**（S252 發現，S252 之前已存在）：以 2026-11-17 語料快照跑 `_s213_validate_gold.py`，25 題被隔離，原因全是 `verified_by.chunk_id` 在語料中不存在（`g19`、`perf_indicators_2022`、`k1_admission_2627`、`sdp_guide`、`debp_blueprint` 等重新入庫後片段編號改變）。
- **影響**：只影響驗證器的出處核對；題目以簽名比對評分，生產量度不受影響。但驗證器失去守門作用。
- **做法**：逐題以原簽名在快照內找回現行片段，只更新 `verified_by.chunk_id` 與 `expected_page`（頁碼仍由 `dominant_page` 推導）；簽名在全庫找不到的題目隔離並交 Leonard，不可改簽名遷就。

### A9　定期系統更新檢查　【✅ 完成（2026-11-17，S252）；下次約 2026-12-17，結果記在 PROJECT_INDEX】

- **做法**：按 `dev/rules/coding.md` 的 `## Project Rules`。至少做：`cd backend && npm audit`；`cd dev/checklists/_work && npm audit`；核對 OpenAI 型號停用頁與價錢頁有否影響 `gpt-6-luna`；檢查 GitHub Actions 所有排程最近一次是否成功（`gh run list --limit 30`）。
- **記錄**：把結果與日期寫入 `dev/PROJECT_INDEX.md`「定期系統更新檢查」一列。上次（S241）未核對執行環境、排程監察與 Kit 新版本，這次要補。

### A10　清理本機已合併的分支　【✅ 完成（2026-11-22，S255，Leonard 批准）：刪 76 條、保留 16 條】

- **結果**：每條分支對應已合併 PR，PR 改過的檔案在分支末端與 squash commit 逐一相同者才刪（76 條，只刪本機，遠端不動）。分支名與 commit 記在本機 `dev/init_backup/20261122_a10_deleted_branches.txt`，需要時可 `git branch <名> <sha>` 還原。保留 16 條：11 條無相同末端的已合併 PR、5 條與合併版本有差異。

- **做法**：`git branch --merged origin/main` 列不全（squash 合併後不算已合併）。對每條本機分支，用 `git diff --stat <分支> <它的 squash commit>` 核實為 0 個檔案差異，才列入可刪清單。把清單交 Leonard，批准後才 `git branch -D`。

### A19　數學課程闡釋入庫　【✅ 完成（2026-11-22，S255；PR #131，生產驗收通過）】

- 6 份（小學兩個學習階段、初中、高中必修與延伸單元一、二）共 361 片段，15,856 → 16,217；路由 `curriculum`（高中另入 `subject_guides`）；瀏覽清單 241 → 247。證據 `dev/source/eval_runs/2026-11-22_s255_ma_curric_ingest.json`。
- 背景：19 個索引頁之下 48 份「未入庫」文件經核對，大多已以另一編號入庫、已被取代或屬配套材料；數學課程闡釋是唯一實質缺口。其餘不入庫，有用戶問及才處理。

### A12　意見與報錯按鈕（第一期）　【待 Leonard 提供表單連結｜小｜不寫生產】

- **目的**：沒有強模型之後，用戶回報是發現「答錯」最直接的來源。詳見 `dev/ops/NEXT_UPGRADE.md` §7 第 1 項。
- **做法**：Leonard 建一份表單（例如 Google Form；不收非必要的個人資料）並提供連結。在 `app.html` 與流動版加一個「意見／報錯」按鈕連到該表單；按 `dev/DOC_SYNC_CHECKLIST.md` 掃下游文案；升版照通用硬規則。
- **驗收**：桌面與手機寬度各實際點一次，按鈕可見、連結正確；`npm run check`／`build` 不受影響。

### A13　在答案旁標示文件時效　【✅ 以退役代替（2026-11-17，S252）；前端標籤擱置】

- **結果**（S252）：分類工具對 227 個未標註來源給不出分類（觸發停止條件），改為按標題年份配對並人手核對。仍在服務、庫內已有新版的舊版共 12 份（約 1,650 片段），見 `dev/ops/decisions/2026-11-17_A13_superseded_editions.md`。


- **目的**：用戶最常見的風險是引用了舊版文件而不自知。詳見 `dev/ops/NEXT_UPGRADE.md` §7 第 2 項。
- **先讀**：`dev/source/lifecycle.py`、`dev/source/check_expiry.py`，以及交接檔 `## Backlog`「時限性資料標示」一段。
- **做法**：分兩步，各自一個 PR。(1) 用 `python3 dev/source/check_expiry.py --classify` 為未分類的舊來源出分類提案，交 Leonard 看過才寫入 registry。(2) 前端在來源連結旁顯示「現行」「已有新版」「已過期」；資料由後端回傳的來源資訊帶出，沒有分類的來源不顯示任何標示。
- **停止條件**：分類提案中有超過一成你不肯定屬哪一類——只交提案，不寫入。

### A11　路由清單改動時 CI 自動量度　【可做但較大——沒有較強模型時先不做】

- **目的**：PR 一旦改到 `backend/src` 內的 `SOURCE_SETS`，自動跑題庫改前改後比較並貼在 PR。
- **為何先不做**：要在 CI 起後端、處理金鑰與限速（185 題相隔 7 秒約 22 分鐘）、處理冷啟動逾時（`57014`）的重跑，設計判斷多。在此之前，改路由的 PR 一律按 `dev/ops/playbooks/route-coverage.md` 人手量度。

---

## B. 等 Leonard 決定（每項只需答一句）

每項已寫好建議與「答了之後怎樣做」。向 Leonard 提問時，一次最多問三項，用白話。

| # | 問題 | 建議 | 答「好」之後 |
|---|---|---|---|
| B1 | ✅ 完成（2026-11-19，S254）：Leonard 在 Render 設 `FEATURE_SUBJECT_CHECK=1`。`--live` 254 題攔 7 題、誤攔應答題 0、gold 0；生產實查攔截句出現、老師對照題照答。原寫「183 題來源層 ≥132」準則量不到此旗標（183 題不經合成），已於 `NEXT_UPGRADE.md` §4 更正。 | —— | —— |
| B2 | ✅ 完成（Leonard 2026-11-22 S255 批准）：退役 `g33`（421，與 `eng_sss_guide_2021` 逐條相同）、`g20`（1，連結頁）、`EDBC_9_2019_E`（2 條註腳，已由 EDBC 4/2026 取代）共 424 條；備份 `dev/init_backup/20261122_154837_UTC/`（含 embedding），刪後讀回 0；15,793 段／318 來源；漂移 ERROR 類 0。`g20` 瀏覽條目按 Leonard 決定保留（`BROWSE_ONLY`），`g33` 條目已移除（246）。**餘下**：①後端約 30 分鐘重讀註腳後，生產不應再取回 `EDBC_9_2019_E`（部署後首次探測仍見它排第 1，屬註腳快取）；②`dev/source/judge_acceptance_cases.json` 的 A01（以 `EDBC_9_2019_E` 註腳為答案）是凍結題集，未改，下次跑判官驗收時預期該題失敗，需 Leonard 決定改題或移出。 | —— | —— |
| B3 | ✅ 完成（Leonard 2026-11-23 S255 批准）：19 個統計來源共 569 條片段已刪並讀回為 0（`stat_enrolment_2012–2024`、`stat_edb_figures`、`stat_kg`／`pri`／`sec`／`special`／`integrated_edu`）；備份 `dev/init_backup/20261123_114544_UTC/`（含 embedding，569/569）；15,224 段／299 來源。7 個登記項標 deprecated，7 個瀏覽條目保留並列入 `BROWSE_ONLY`；vault 抽取檔保留可重新入庫；`searchChannelB.ts` 移除 `stat_kg` 兩處死引用。**備忘**：①QC 基準已遠高於現況（重複 956→0、封面代號 658→0、無連結 130→0、半句開始 835→744、目錄 147→105），但 `baseline_status` 設計為「等於基準即 WARN」，基準降到 0 會令這些檢查永遠 WARN，所以**沒有調低**，需另行決定做法；②B2 那次我漏改 README 來源數（321 應為 318），今次一併改為 299。 | —— | —— |
| B4 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`cur_arts_guide_2002_missing` 移除 `g37` 禁引（g37 標題已更正為 2017 年版），題目仍要求說明庫內無 2002 年版。驗證器結果改前改後相同（165／183，18 題因本機語料缺片段編號而隔離，屬舊問題）。 | —— | —— |
| B5 | 已批准刪除「文件標註」功能（面板程式碼、文案）。**待執行**：連同 B6；刪 `release_gate.json` 的 `DOC_ANNOTATION_FLOW` 人手檢查。（Leonard 2026-11-22 S255 批准） | —— | 見左欄 |
| B6 | 已批准隨 B5 移除公開端點。**待執行**：屬後端改動，要部署。（Leonard 2026-11-22 S255 批准） | —— | 見左欄 |
| B7 | ✅ 完成（Leonard 2026-11-22 S255 批准）：PR #70 已關閉並留言（22 行中 18 行逐字在 main，餘 4 行為其後修訂版）。 | —— | —— |
| B8 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`footnote_fn_ceg_no_tutorial` 改指 EOEBG 使用指引第 6 頁，文字補「OEBG 學校的使用指引亦有相同規定」；錨句已加入月檢並核對 OK。備份 `dev/init_backup/20261122_154303_UTC/`、`20261122_154347_UTC/`。 | —— | —— |
| B9 | ✅ 完成（2026-11-16，S251）：Agent Handoff Kit 已以官方 CLI 升級至 v0.4.7，migration committed、project health passed。 | —— | —— |
| B10 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`INIT.md` 當作已退役；`dev/DOC_SYNC_CHECKLIST.md` 三列內要求同步 INIT.md 的部分標為失效（檔案保留不刪）。 | —— | —— |
| B11 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`release_gate.json` 加 `MOJIBAKE` 豁免（負責人 Leonard，至 2027-11-22）。「內文過短」由 3 增至 6 條已轉 FAIL（豁免只適用 WARN），逐條核對後全是表格標題行與封面頁，`qc_report.py` 基準改為 6 並寫明是哪 6 條。 | —— | —— |
| B14 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`footnote_fn_cap279_s14_refuse_grounds` 末加「（此處只列部分理由，完整見條文）」。兩個入庫腳本同步改字。 | —— | —— |
| B15 | ✅ 完成（2026-11-17，S252）：校曆註腳 `g11_schooldays` 已改指《一般學校假期及上學日數的計算方法》PDF 第 1 頁（Leonard 批准；先備份，寫入後讀回 `to_change=0`；月檢錨句已加入並核對 OK）。 | —— | —— |
| B16 | ✅ 完成（2026-11-17，S252，Leonard 批准）：6 題改標（3 題改指 `edbcm080_2026`；註冊費與取錄通知日期改為 2027/28 學年；持份者問卷一句按原文補「（第三版）」），2 題移至 `dev/source/gold_deprecated_s252.json`（`plc_school_net_count`、`hr_ncs_allowance`：庫內已無答案來源）。題庫 185 → **183**，驗證器 183／183。生產：改標 6 題中 3 題通過；「持份者問卷」「KG 收生」「2027/28 K1取錄結果何時通知」未取回答案文件，屬檢索問題，未為遷就而改標。 | —— | —— |
| B12 | 搜尋紀錄要不要加「拒答原因」一欄（要執行 DDL）？ | 暫不做。沒有它平台照常運作。 | —— |
| B13 | ✅ 完成（Leonard 2026-11-22 S255 批准）：`AGENTS.md` §4 第 12–14 項改為「不把開場訊息複製入 log，只留一行指引」，第 132 行與 §4a 第 3 項同步改為只適用舊格式。改前備份 `dev/init_backup/*_agents_b13/`（`AGENTS.md` 不在 git）；Kit doctor（v0.4.8）healthy。 | —— | —— |

另有三項要先讀資料才能問（`dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md` 搜尋相關字眼）：S244 三條註腳的粵語問句是否改寫；語料庫內有時限的段落是否交退役機制處理；`app.html`「全校」角色標籤的處理。**未讀清楚前不要向 Leonard 提問。**

---

## C. 等觸發才做

| 項目 | 觸發 | 之後做甚麼 |
|---|---|---|
| 向量索引升級（HNSW） | `pgvector_check.yml` 報上游版本 ≥ 0.8.4 | 通知 Leonard；索引改動屬 DDL，由他在 Supabase 執行 |
| 線上當機通知未在真實當機下驗證 | 生產真的短暫當機時 | 順手核對是否開了 `service-down` Issue、恢復後是否自動關閉。**不要為演練弄壞生產** |
| 入庫 executor 一次批准多份會衝突 | —— | 不修。提醒 Leonard 在入庫 Issue 一次只剔一份 |
| Freshness 清單其餘項目 | `freshness-change` Issue 有新項目 | 按 `dev/ops/playbooks/freshness-triage.md`；A3 完成後大部分會自動處理 |
| 公開 repo 60 日無活動，GitHub 會停用所有排程 | 連續 50 日沒有任何 commit | 推一個小 commit（例如更新本檔日期） |

---

## D. 不要做（已量度並否決——重做只會浪費用量）

- **不要啟用**：`FEATURE_QUERY_FUSION`、`FEATURE_VAULT_GATE_RAWVEC`（未補完四項先決條件前；詳見 `dev/ops/NEXT_UPGRADE.md` §4）、`MAX_PER_SOURCE`、`FEATURE_LEXICAL_RERANK`、`FAMILY_QUOTA`、`EXPANSION_MIN_QUERY_CHARS`、`EXPANSION_BALANCE`、`EXPANSION_REPEAT_CAP`。
- **不要調門檻**：`VAULT_LEAD_SCORE`、`SPOTLIGHT_LEAD_SCORE`、`min_score`、相似度截斷，全部試過。
- **不要把大批來源塞進現有路由清單**（S250：令原有題目逾時或被擠走）。新來源照 `route-coverage.md` 分類。
- **不要把 `ROUTE_EXEMPT` 的舊版來源加入路由**；它們應退役（B2）。
- **不要以註腳入庫腳本 `--execute` 更正單條註腳**；用 `dev/apply_footnote_corrections.py`。
- **不要跑全量 Freshness write-sync**（會一次重設所有基線）；用 `--ack`。
- **不要把快速量度或本機量度檔放進 `dev/source/eval_runs/`**（會被質素檢查誤當最新基線）。
- **不要重造系統**（Leonard S249 問過，結論是修好而非重造）。
- **不要動「提升片段層召回」**（重排、候選生成等）：這是檢索設計工作，沒有較強模型時不做。計劃已寫在 `dev/ops/NEXT_UPGRADE.md`（先後次序、出貨門檻、放棄條件），有較強模型或 Leonard 明示時才按它做。平台現時檢索基線為來源層 132／32、片段層 61／103（S253，183 題），維持即可。
- **不要為了通過 `closeout-status` 而改寫交接檔的文字**；通不過就如實記為 blocked。

---

## E. 做完一張卡後的最小核對

```bash
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
python3 dev/source/qc_report.py --self-test
/usr/local/bin/python3 dev/apply_footnote_corrections.py --check
/usr/local/bin/python3 dev/apply_url_overrides.py
python3 dev/source/check_registry_drift.py --check --ledger "<scratchpad 路徑>/ledger.md"
```

改過 `backend/` 的另加：`cd backend && npm run check && npm run build && npm run regression:grounded && npm run regression:overlay`，以及 `node dev/source/route_regression.mjs`。
