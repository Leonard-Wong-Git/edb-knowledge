# 工作清單（EDB K1 知識平台／policychecker）

> **本檔的角色**：所有待辦事項的唯一清單，每項都寫成可以照做的工作卡。由最強模型（Fable 5.2）於 2026-11-16（S251）一次過寫好，供之後任何模型跟進。
> **不是**現況權威（現況看 `dev/SESSION_HANDOFF.md` 的 `## Current Baseline`），**不是**規則本身（規則看 `AGENTS.md`、`dev/rules/safety.md`、`dev/ops/AUTONOMY_FLOW.md` §4a）。
> **提升搜尋準確度的計劃不在本檔**，在 `dev/ops/NEXT_UPGRADE.md`（只在有較強模型或 Leonard 明示時才做）。
> **更新時機**：做完一張卡、Leonard 作了一個決定、或出現新待辦時。做完的卡把狀態改為「✅ 完成（日期、PR 編號）」，保留一行，其餘內容刪去。
> **系統目標**（Leonard，S243／S249／S251）：平台各環節自行運作，人手只在真正要判斷或有風險的地方介入；要人手維護又沒有人用的功能，傾向刪除。**用戶**是香港學校的校長、教師與行政人員，多數只打一至三個詞的短查詢，要的是準確、有出處、可點擊到原文頁數的答案。

## 0. 怎樣用這份清單

每一節（session）照這個次序做：

1. **開工**：讀 `dev/SESSION_HANDOFF.md`，然後按 `dev/ops/playbooks/health-probe.md` 做起手探針。探針的停止條件觸發就先報告，不做其他事。
2. **揀工作**：Leonard 有指定就做指定的；沒有指定，就由 A 部由上而下揀第一張狀態為「可做」的卡。**一節只做一張卡**，做完還有餘力才做下一張。
3. **做**：照卡內步驟。每張卡都有「驗收」與「停止條件」；停止條件觸發就停，把情況寫進本卡的「備註」，不要即興補救。
4. **交付**：一張卡一個分支、一個 PR（`main` 受保護，不能直接推）。**合併只在 Leonard 明示時進行。**
5. **記錄**：更新本檔該卡的狀態；Leonard 說「收工」時按 `dev/rules/closeout.md` 做收工。

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

### A1　把「註腳更正」與「連結覆寫」接入每日質素檢查　【可做｜小｜不寫生產】

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

### A2　註腳出處每月自動核對（不用模型）　【可做｜中｜不寫生產】

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

### A3　來源有變但文字相同時自動確認　【可做｜中｜只寫監察基線】

- **目的**：每週的 Freshness 監察報「來源有變」，但 S249 處理的 19 項中有 11 項只是原文重新匯出、文字完全相同，要人手逐項確認。令機器自動確認這一類。
- **先讀**：`dev/source/FRESHNESS_GUIDE.md`（`--ack` 與指紋的意思）、`dev/ops/playbooks/freshness-triage.md`、`dev/SESSION_LOG.md` 內 S249 的條目（找當時用來逐頁比對的做法）。
- **做法**：在 `dev/source/check_freshness.py` 的排程路徑加一步：對指紋有變的 PDF 來源，下載新版，用與 vault 抽取檔相同的抽取方法逐頁抽文字，與 `dev/vault/<來源>/` 的現有抽取檔比對（NFKC、去空白後逐頁相等）。**完全相等**才自動確認基線並在輸出記一行「已自動確認：文字相同」；有任何一頁不同、頁數不同、或抽取失敗，一律不確認，留在清單等人處理。網頁類來源維持現狀，不納入。
- **驗收**：`--self-test` 加三個個案（相同→確認；一字不同→不確認；頁數不同→不確認）並通過；全量 dry-run 的錯誤數為 0。
- **停止條件**：找不到 S249 當時的比對方法，或不確定抽取方法是否與入庫時一致——停。用不同抽取器比對會誤判為「不同」（安全）或「相同」（危險），不可猜。

### A4　補回 `backend/README.md` 的旗標說明　【可做｜小｜不寫生產】

- **目的**：S215 遺失了 5 行旗標說明，沒有備份。
- **做法**：由 `backend/src` 內實際讀取的環境變數重寫（`grep -rn "process.env" backend/src`），每個旗標一行：名稱、預設值、作用、現時生產是否開啟（對照交接檔 `## Current Baseline` 5）。「不應啟用」的旗標要註明已量度並判定不出貨。
- **驗收**：README 列出的旗標與程式內讀取的完全對應；commit 訊息寫明「重寫，並非還原」。

### A5　為科目指引路由補題　【可做｜中｜不寫生產】

- **目的**：S250 新增的 `subject_guides` 路由有 37 個來源，但 185 題題庫只有 1 題觸及，量度只能證明「沒有變差」。
- **先讀**：`dev/DOC_SYNC_CHECKLIST.md`「檢索準確度量度改動」一列；現有題庫檔 `dev/_s213_gold_*.json` 的格式；`dev/ops/playbooks/route-coverage.md`。
- **做法**：為其中 10 個來源各擬一條短查詢（一至三個詞，貼近教師實際會打的字，例如科目名加「課程指引」「評估」「課時」）。每題的正確答案段落必須由你**讀原文片段後**指明，不可憑題目猜。新題先跑 `_s213_validate_gold.py`；不通過的題目隔離，不要為通過而改標籤。
- **驗收**：驗證腳本通過；在生產跑一次這 10 題（帶 `x-probe: 1`，每題相隔 8 秒），記錄 PASS／FAIL 作為這批題目的首個基線。**不要把這次結果與 185 題的基線合併比較。**
- **停止條件**：不肯定某題的答案段落——該題不要加入。

### A6　13 條「找不到出處」的註腳　【可做｜小｜不寫生產】

- **目的**：S250 審核有 13 條因抓不到原文（多為電子版香港法例，頁面由 JavaScript 產生）而未能核對。
- **做法**：由 `dev/source/eval_runs/2026-11-16_s250_footnote_audit.json` 列出結論為「找不到」的 13 條。逐條用瀏覽器工具打開 `url`，讀到原文後，把註腳的數字、條文編號、條件與原文並列。只做並列與分類（相符／數字不同／原文沒有此說法／打不開），**不要改寫註腳**。
- **交付**：一份表交 Leonard。可逐字對照的更正（數字、條文編號）可同時備妥 `footnote_corrections.json` 的預演。

### A7　`/health` 的註腳載入時間不更新　【可做｜小｜改後端】

- **現象**（S251 實測）：寫入註腳更正約 8 分鐘後，線上搜尋已回傳新文字，但 `/health` 的 `footnote_loaded_at` 仍是 30 多分鐘前的時間。
- **做法**：讀 `backend/src/lib/wikiRepository.ts` 約第 484–560 行與第 852 行。先只報告觀察到的事實：背景重讀成功後 `_footnoteLoadedAt` 有沒有被設定、`/health` 讀的是不是同一個變數、是否有多個執行個體。確定是顯示問題才改；改後要通過 `cd backend && npm run check && npm run build && npm run regression:overlay`。
- **停止條件**：看不出成因——只把觀察寫入本卡備註，不改碼。

### A8　瀏覽清單的累積差異　【可做｜中｜不寫生產】

- **現況**：`PHANTOM` 36（瀏覽清單有、庫內零片段）、`UNLISTED` 119／2,626 片段（搜尋得到、「EDB 指引」瀏覽不到）。兩者是待辦清單，不是故障。
- **做法**：`python3 dev/source/check_registry_drift.py --check --ledger <scratchpad 路徑>` 取得清單（`--ledger` 一定要指向 repo 以外）。每次處理 20 項，為每項給出一個建議：
  - `UNLISTED`：屬指引、手冊、通告類而且用戶會想瀏覽的→建議加入 `app.html` 的 `GUIDELINES_REGISTRY`；屬表格、統計、註腳來源的→建議不列。
  - `PHANTOM`：瀏覽條目指向的文件是否已由另一個 id 承載（`ROUTE_EXEMPT` 內有說明的屬此類）→建議移除重複的瀏覽條目。
- **交付**：一份表（id、標題、片段數、建議、一句理由）交 Leonard 批准後才改 `app.html`；改後 README 的數目、`guidelines.json` 是否受影響，按 `dev/DOC_SYNC_CHECKLIST.md` 處理。

### A9　定期系統更新檢查　【可做｜小｜到期日約 2026-11-28】

- **做法**：按 `dev/rules/coding.md` 的 `## Project Rules`。至少做：`cd backend && npm audit`；`cd dev/checklists/_work && npm audit`；核對 OpenAI 型號停用頁與價錢頁有否影響 `gpt-6-luna`；檢查 GitHub Actions 所有排程最近一次是否成功（`gh run list --limit 30`）。
- **記錄**：把結果與日期寫入 `dev/PROJECT_INDEX.md`「定期系統更新檢查」一列。上次（S241）未核對執行環境、排程監察與 Kit 新版本，這次要補。

### A10　清理本機已合併的分支　【待 Leonard 批准刪除｜小】

- **做法**：`git branch --merged origin/main` 列不全（squash 合併後不算已合併）。對每條本機分支，用 `git diff --stat <分支> <它的 squash commit>` 核實為 0 個檔案差異，才列入可刪清單。把清單交 Leonard，批准後才 `git branch -D`。

### A12　意見與報錯按鈕（第一期）　【待 Leonard 提供表單連結｜小｜不寫生產】

- **目的**：沒有強模型之後，用戶回報是發現「答錯」最直接的來源。詳見 `dev/ops/NEXT_UPGRADE.md` §7 第 1 項。
- **做法**：Leonard 建一份表單（例如 Google Form；不收非必要的個人資料）並提供連結。在 `app.html` 與流動版加一個「意見／報錯」按鈕連到該表單；按 `dev/DOC_SYNC_CHECKLIST.md` 掃下游文案；升版照通用硬規則。
- **驗收**：桌面與手機寬度各實際點一次，按鈕可見、連結正確；`npm run check`／`build` 不受影響。

### A13　在答案旁標示文件時效　【可做｜中｜不寫生產】

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
| B1 | 要不要開啟「答錯對象」的攔截（`FEATURE_SUBJECT_CHECK`）？現時已知 5 條會把別類人的規則套到所問的人身上，開啟可攔 3 條。 | 開。條件是開啟後重跑 185 題，來源層 PASS 不少於 130；少於即關回。 | Leonard 在 Render 加環境變數（只有他改得到）。之後按 `backend/scripts/_s236_subjectCheck.ts --live` 與 185 題量度比對，把結果寫入交接檔。 |
| B2 | 10 個已被新版取代或重複的來源（`check_registry_drift.ROUTE_EXEMPT` 所列）與 `EDBC_9_2019_E`，要不要退役（刪除生產片段）？ | 退役。舊版留在庫內會令用戶搜到過時內容。 | 逐個來源：備份（`select=*`）→ 預演 → 刪除 → `live_display_sync` → `update_log.json` → registry 標為 deprecated → `check_downstream_sync` `MUST_UPDATE` 為 0。一次只做一個來源，每個都要 Leonard 看過預演數目。 |
| B3 | 統計來源（19 個／569 片段）設計上搜不到，但每次更新都要人手重新入庫。開放搜尋，還是停止維護？ | 先查近 180 日搜尋紀錄有沒有人問統計數字（結果只口頭報告，不寫入 git）。沒有人問就停止維護並退役。 | 開放：改 `include_statistical` 的預設，屬檢索改動，要 185 題改前改後量度。停止：按 B2 的步驟退役。 |
| B4 | 題庫題目 `cur_arts_guide_2002_missing` 的前提已過時（它假設某份文件在庫，現已不成立），要不要更新？ | 更新。 | 改題目的禁引清單，跑 `_s213_validate_gold.py`。 |
| B5 | 「文件標註」功能現已收起。修好重開，還是刪除？ | 刪除，除非你知道有用戶需要。它要人手維護，目前沒有人用。 | 刪除面板程式碼、相關公開端點（連同 B6）與文案；按 `dev/DOC_SYNC_CHECKLIST.md` 掃下游文字。 |
| B6 | 已收起功能留下的公開端點，保留還是移除？ | 隨 B5 一併移除。 | 同上。 |
| B7 | 開著的 PR #70 內容早已在 `main`，可否關閉？ | 關閉。 | `gh pr close 70` 並留一句說明。 |
| B8 | `ceg_no_tutorial` 這條註腳的原句不在現時所引的文件；S249 查到出處在 EOEBG User Guide 第 6 頁或 OEBG User Guide 第 7 頁。用哪一份？ | 先由 agent 打開兩份核實原句確實在該頁，再把兩句並列給你選。 | 加入 `url_overrides.json`，預演後執行。 |
| B9 | Agent Handoff Kit 要不要由 0.4.3 升級（npm 最新為 0.4.7）？現時收工檢查因版本落後而回 `blocked`（S251 實測：`doctor` 的 project shortcuts 一項未通過）。 | 升級，建議排在 B 部最先，但只用官方指令 `agent-handoff-kit upgrade --yes --root <Draft 路徑>`，不可人手改 Kit 檔案。 | 跑指令，分開報告「遷移是否完成」與「專案健康檢查結果」。 |
| B10 | `INIT.md`（舊版治理安裝檔）是否已退役？ | 退役。它鏡像的是舊結構。 | 把 `dev/DOC_SYNC_CHECKLIST.md` 內要求同步 `INIT.md` 的兩列標為失效。 |
| B11 | 封版閘有兩個警告（內文過短 3 條、亂碼 58 條）已逐條看過可接受，只欠在 `dev/source/release_gate.json` 寫上負責人、理由與期限。由你作負責人可以嗎？ | 可以，期限一年。 | 寫入 waiver。 |
| B12 | 搜尋紀錄要不要加「拒答原因」一欄（要執行 DDL）？ | 暫不做。沒有它平台照常運作。 | —— |

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
- **不要動「提升片段層召回」**（重排、候選生成等）：這是檢索設計工作，沒有較強模型時不做。計劃已寫在 `dev/ops/NEXT_UPGRADE.md`（先後次序、出貨門檻、放棄條件），有較強模型或 Leonard 明示時才按它做。平台現時檢索基線為來源層 130／36、片段層 61／105，維持即可。
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
