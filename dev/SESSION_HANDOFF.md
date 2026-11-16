# Session Handoff

<!-- Markers below have no dedicated local section yet; the next closeout should give each one a home. -->
<!-- ack:section:durable-anchors -->
<!-- ack:section:closeout-reconciled-state -->
<!-- ack:field:first-use-guidance-state -->
5. First-use guidance state: not_applicable — added by upgrade; prior use state is preserved and onboarding is not reactivated.

<!-- ack:section:task-understanding-summary -->
<!-- ack:section:active-objective -->
<!-- ack:section:sync-status -->
<!-- ack:field:user-intent -->
<!-- ack:field:task-essence -->
<!-- ack:field:success-criteria -->

<!-- ack:section:current-baseline -->
## Current Baseline

1. **平台**：v3.3.16。公開分頁三個（平台介紹／政策搜尋／EDB 指引）；文件標註收起待修（`FEATURE_TABS.annotate=false`）。Channel A 退役已完結（S243–S246）：`knowledge.json`／`role_facts.json` 已刪、內部清單清空、公開統計由 `stats.json` 提供；凍結合約只餘 `guidelines.json` 2.6.2／151。升版一律手改 `PLATFORM_VERSION`＋README 標章＋CHANGELOG，不可用 `bump_version.py`。
2. **知識庫**：**S249 checkpoint（2026-11-16）：Supabase 17,084 chunks、316 來源** —— 五份上游已更新的 PDF 經 Leonard 批准重新入庫（304 → 309；備份在本機 `dev/init_backup/20261116_083026_UTC/`），工作在 PR #97（未合併；公開數字要等合併才更新）。Freshness 待處理 35 → 3（餘 `stat_pri`／`stat_sec`／`stat_special`，上游已修訂教師數字，待批准重新入庫）。51 條 `PAGE_ANCHORED` 的修正建議清單在 scratchpad（一次性），未寫入。以下為 S248 數字：Supabase 17,079 chunks、316 來源（2026-11-15 讀 `stats.json`；PR #91 自動入庫 `edbcm203_2026` +5；S246 `count=exact` 實測為 17,074／315）。`footnote_curated` 177。EDB 指引書庫 182 份（S243；#91 之後未重核）。
3. **Registry 漂移**（2026-11-08 QC 報告）：`ZOMBIE`／`UNMANAGED`／`SERIES_UNMONITORED` 皆 0；`PHANTOM` 36；`UNLISTED` 118／2,621 片段（人手策展佇列）。2026-11-16 實測 `UNLISTED` 119／2,626（#91 入庫 `edbcm203_2026` 後 +1），其餘不變。
4. **Git 與部署**（2026-11-15 實測）：`origin/main` = `31ae8b2` 之後（PR #92 交接檔瘦身、#93 QC 惡化通知、#95 `PAGE_ANCHORED` 定義修正皆已合併）；線上 `/health` commit = `8b118fd`。`main` 受 ruleset 保護，一切改動走 PR，合併只在 Leonard 明示時進行。2026-11-16 起手探針：`origin/main` = `61ba038`（`31ae8b2` 之後只有 QC 報告自動 commit）、`/health` 通函索引 70 份。開著的 PR：#96（S248 收工分支 `s248-closeout`，只改治理文件；S248 收工於 2026-11-16 補完）、#70（內容早已入 `main`，關閉前先問 Leonard）。判斷線上是否落後看 `git diff --name-only <部署commit>..origin/main -- backend`，不要比 hash。入庫 PR 會改 `SOURCE_SETS`，合併後 Render 重新部署，新來源要等新版上線才搜得到。
5. **模型與旗標**：合成與判官皆 `gpt-6-luna`＋`none`（碼內預設，Render 無 `OPENAI_MODEL`）。生產已開：`FEATURE_ROUTE_FIRST_SEARCH`、`FEATURE_CIRCULAR_NUMBER_LOOKUP`。已部署未開：`FEATURE_SUBJECT_CHECK`（待 Leonard 決定）。**不應啟用**（皆已量度並判定不出貨）：`FEATURE_QUERY_FUSION`、`FEATURE_VAULT_GATE_RAWVEC`、`MAX_PER_SOURCE`、`FEATURE_LEXICAL_RERANK`、`FAMILY_QUOTA`、`EXPANSION_MIN_QUERY_CHARS`／`EXPANSION_BALANCE`／`EXPANSION_REPEAT_CAP`。`/health` 不報旗標。
6. **監察與檢索基線**：偵測型監察有新項目才 @Leonard；質素檢查高於基準時開 `qc-regression` Issue 並 @Leonard（S248，已上線並經真實運行驗證）；7 個排程 workflow 由每日看門狗監察，另有 `live_probe` 每 6 小時探測線上服務；四條 ledger workflow 經 deploy key 推。檢索基線（S233 生產，185 題）：來源層 PASS 125／FAIL 41，片段層 59／107；Source Recall@1 0.446、@5 0.711，Chunk Recall@5 0.349。重跑噪音：片段層 0、來源層 ±1。各項詳情見 `dev/SESSION_STATE_DETAIL.md`。

> 詳情與證據：`dev/SESSION_STATE_DETAIL.md`（做到該項才讀）；改寫前原文：`dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md` E 節。

<!-- ack:section:validation-qc -->
**S248（2026-11-15；收工於 2026-11-16 補完）—— 減維護負擔第一、二步。** 零 Supabase 寫入、零 flag、零 `backend/` 改動。(1) **交接檔瘦身**（PR #92 → `28102db`）：本檔 760 KB → 約 65 KB；移走的章節一字不改存於 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`，三段精簡版的詳情在 `dev/SESSION_STATE_DETAIL.md`。(2) **QC 惡化通知**（PR #93 → `1bbd911`）：`qc_report.json` 新增 `regressions`，`qc_report.yml` 以 `notify_new_items.js` 開 `qc-regression` Issue 並 @Leonard；首次真實運行開出 Issue #94，Leonard 確認收到電郵。(3) **`PAGE_ANCHORED` 定義修正**（PR #95 → `31ae8b2`，Leonard 批准）：只計 PDF、頁碼標記判斷與後端 `={2,}` 一致、基準 179 → 51；線上 17,079 片段實測 51（WARN，等於基準），Issue #94 自動關閉。(4) **2026-11-16 補收工時的起手探針**：served `PLATFORM_VERSION='3.3.16'`；`/health` `ok`、commit `8b118fd`、`footnote` 177、通函索引 70（剛喚醒首次讀取 `57014`，第二次正常，屬 Risks 6 冷熱落差）；`stats.json` 17,079／316；`origin/main` 的 `qc_report.json`（2026-11-15T19:59Z）`regressions` 為空；`check_registry_drift.py --check` `ZOMBIE`／`SERIES_UNMONITORED`／`UNMANAGED` 0、`PHANTOM` 36、`UNLISTED` 119／2,626；開著的 Issue 只有 #77。**未做**：餘下 51 條 `PAGE_ANCHORED` 真缺口未修（見 `## Open Priorities` 2）。

**S247（2026-11-09）—— 清理 `dev/init_backup/` 舊版 `wiki_index.json` 備份。** 只動本機 gitignored 檔案與兩份治理文件；零生產寫入、零 `backend/`、零部署。(1) 起手探針：served `PLATFORM_VERSION='3.3.16'`；`/health` `ok`、commit `20fd4a4`、`footnote` 177、`circular` enabled／index 69。(2) 27 個時間戳資料夾逐一核實只含一個 `wiki_index.json`；24 份為 5–6 月舊版（420,356,599／424,482,856／424,450,497／424,846,760 bytes），3 份為 476,940,257 bytes，SHA-256 皆與現用 `dev/knowledge/wiki_index.json` 相同（`ab8d1c40…`）。(3) 全項目搜尋資料夾名稱：只有 `dev/CODEBASE_CONTEXT.md` 維護紀錄與 `dev/archive/SESSION_LOG_2026_Q2.md` 歷史紀錄提及；`dev/vault/` 的命中全指向其他資料夾；無腳本或待辦引用。(4) Leonard 批准後刪除 26 份（保留 `20261101_195458_UTC`，刪後再核 SHA-256 相同），實際釋放 10,826,816 KiB（約 11.09 GB）；`dev/init_backup/` 剩 44 個資料夾約 476 MB。(5) `dev/rules/safety.md` 在官方內文之後加 `## Project Rules`（wiki_index 備份只留最新一份；Supabase 刪除／改寫前備份必須保留）；官方內文前綴 SHA-256 前後相同（`5a1598ae…`）。(6) PR #89 CI 通過後合併為 `82be06e`。

## Validation / QC

**S246（2026-11-08）—— Option 2 清單清空；刪除 109 條 `approved_fact` 副本。** 生產寫入：Supabase −109（只刪 `source_id like role_facts_*` 且 `content_type=approved_fact`）；零 DDL、零 flag、零 `backend/` 改動、零部署。(1) **租金收入定出處**：讀 g02 原 PDF（17 頁）第 15 頁，按 PyMuPDF 版面座標還原表格兩欄（庫內 chunk `vault_g02_b233f0a42484ec31` 的兩欄交錯是抽取問題，原文本身完整）；要點欄原句「一切租金收入，應首先撥入堂費／普通經費／資本儲備帳，並從該等帳項支付有關的費用，然後將餘額的40%撥入學校及班級津貼帳內。」＋備註「適用於設有法團校董會的資助學校。」寫入 `fact_corrected`；備註第二句（「擴大的營辦開支整筆津貼帳」）原文措辭不通順，按第 7 條不改寫亦不收入。候選（乙）`footnote_fn_tips_rental_40pct` 未提「學校及班級津貼」，不取。清單寫入時核對序列化格式不變，`git diff` 只三處。(2) **備份**：`select=*` 分頁匯出，109 行、`id` 唯一、含 embedding 109、`count=exact` 109；sha256 `c6b60572…7275fab4e9`，2,151,372 bytes。(3) **刪除**：REST DELETE `return=representation` 回 109 行，刪除 `id` 集合與備份完全相同；之後 `live_total_count` 17,074、`live_sources_count` 315（本來已扣 `role_facts_*`）。(4) **display-sync**：`live_display_sync(17183, 17074)` 改 `stats.json` 1、`app.html` 3、`index.html` 3、`README.md` 4；合併後線上 `stats.json`／`app.html`／`index.html` 讀回 17,074。(5) **線上搜尋**：Render 剛喚醒時首兩次查詢 `57014` 逾時（含通函索引載入失敗），隨後三次 4.3s → 1.9s → 1.1s 正常、通函索引 69 份 —— 屬 Risks 3 的冷熱落差，與刪除無關。(6) **來源登記更正**：`check_registry_drift.py --check` 實測 `UNMANAGED` 0／`ZOMBIE` 0／`SERIES_UNMONITORED` 0／`PHANTOM` 36／`UNLISTED` 118；`footnote_curated` 屬 `BY_DESIGN_KINDS`（`check_registry_drift.py:52-57`），按設計不登記 —— S244／S245 交接「新 footnote source_id 會列 UNMANAGED」的說法錯誤，`edbc29_2024_teacher_training`、`edb_byod_page` 不登記（與 `subvention_tips` 等既有 footnote 來源一致）。(7) **分支清理**：`d2c95ee` 與已合併的 `17903a3` patch 逐字相同，`s244-option2-round1` 遠端與本機已刪。

<!-- 歷史原文（S248 瘦身，2026-11-15）：`## Validation / QC` S245 及以前各節 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔A〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- ack:section:risks-blockers -->
## Risks / Blockers

1. 🔴 **對象錯置**：窗內有別類人的同類規則時，判官放行，合成器會把它套到所問的人身上；生產已知漏判 5 條。v1 對象核對已部署，`FEATURE_SUBJECT_CHECK` 未開。換判官模型、改提示、擴詞表皆已證無效。設計見 `dev/source/SUBJECT_CHECK_DESIGN.md`。
2. ⚠️ **量度紀律**：本機比生產慢約 1.5–2 秒，本機數字只可排序；後端用 anon key（`statement_timeout` 3 秒），本機量度前先確認用的是哪個 key；比較兩份文件必須用同一抽取器並設對照組。生產 gold 有 4 條 `57014` 逾時，再升要當容量問題查。
3. ⚠️ **入庫寫入路徑**：Option A 同一次運行批准兩份以上，第二份的 PR 必然衝突（Supabase 已寫入而 `main` 落後）；`LEDGER_DEPLOY_KEY` 等同可直接寫 `main` 的鑰匙；`backend_build_check.yml` 不得加回 `paths:` 過濾。開工與 push 前一定要 `git fetch` 後比對。
4. ⚠️ **本機 Python 環境分裂**：抽取與入庫指令一律寫 `/usr/local/bin/python3`；破壞性步驟前先跑 `--dry-run` 確認依賴齊全。
5. ⚠️ **生產刪除沒有機械閘**：AI 可以直接執行 Supabase 刪除，安全邊界只有「先備份、先取得 Leonard 明示批准」。看門狗與其他監察跑在同一套排程上，全部一齊停時無人出聲（公開 repo 60 日無活動會自動停用排程）。
6. **只監察**：HNSW 索引被 pgvector 版本擋住（要上游打包 ≥0.8.4，每週監察）；實例冷熱落差 58–90 倍（比較兩組查詢要交錯重量三輪以上）；量度判官有 1 對位置偏誤（每次看 `judge_health.always_first`）；`AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 不在 git 內，沒有任何副本。

各項的完整證據與數字見 `dev/SESSION_STATE_DETAIL.md`。

> 詳情與證據：`dev/SESSION_STATE_DETAIL.md`（做到該項才讀）；改寫前原文：`dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md` E 節。

<!-- ack:section:workspace-identity -->
## User Environment (Always Reference Before Giving Shell Commands)
- **Repo path**: `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（路徑含空格 —— 終端機指令必須用雙引號包住）
- **Correct cd**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`
- 🔴 **Python：有三個，只有兩個跑得動本專案的抽取／入庫腳本。** 預設 `python3` = homebrew **3.14**，**無 `fitz`、無 `openai`**；`/usr/local/bin/python3`（openai 2.26 ＋ fitz ＋ requests）與 `/usr/bin/python3` 才齊。**抽取與入庫一律明寫 `/usr/local/bin/python3`**；純標準庫的監察腳本（`check_*.py`／`execute_ingest.py --self-test`／`build_wiki_index`）用 `python3` 沒問題。詳見 Risks 6。 **S232 補**：`python3.13` 亦有 `openai`＋`requests`，`dev/ingest_s232_kg_ratio_footnote.py` 與 `footnote_lead_probe.py` 以它實跑通過。
- **Python script invocation**: 一律由 repo root 起，例如 `cd "…/Draft" && python3 dev/vault/extract_candidates.py ...`
- **Backend**: `cd "…/Draft/backend" && npm run dev`
- **Git state（S248 收工，2026-11-16 補完）**: `origin/main` = `61ba038`；線上執行碼 `8b118fd`；收工分支 `s248-closeout`（PR #96，只改治理文件）；#70 仍開著；舊本地分支未清理；worktrees 1。以下為 S247 原文。 - **Git state（S247 收工，2026-11-09）**: `origin/main` = `82be06e`（PR #89 已合併）；線上執行碼 `20fd4a4`；本節收工分支 `s247-closeout`；本機另有已合併的 `s246-closeout`、`s247-init-backup-cleanup` 與 `s240/*`–`s245-*` 等舊本地分支（未清理，非本節範圍）；worktrees 1。以下為 S246 原文。 - **Git state（S246 收工，2026-11-08）**: `origin/main` = `d6b18f6`（PR #87 已合併為 `62647fe`）；線上執行碼 `20fd4a4`；本節收工分支 `s246-closeout`；`s244-option2-round1` 已刪；本機尚有 `s240/*`–`s245-*` 等舊本地分支（未清理，非本節範圍）；worktrees 1。以下為 S245 原文。 - **Git state（S245 收工，2026-11-05）**: `origin/main` = `27a59d5`（PR #86 已合併為 `12c1ab7`）；線上執行碼 `20fd4a4`；本節分支 `s245-option2-round2`（工作 commit＋收工 commit，PR #87，未合併）；舊分支 `s244-option2-round1` 多一個重複 commit `d2c95ee`（無 PR）；worktrees 1。以下為 S244 原文。 - **Git state（S244 收工，2026-11-05）**: `origin/main` = `ab2aee9`；線上執行碼 `20fd4a4`；本節分支 `s244-option2-round1`（工作 commit `90bb921`＋收工 commit，PR #86，未合併）；worktrees 1。以下為 S243 原文。 **Git state（S243 收工，2026-11-03）**: `origin/main` = `37451db`（#79–#84 已合併）；線上執行碼 `20fd4a4`；收工分支 `s243/closeout-final`（新 PR，只改治理文件與 README 一字）；本機已合併分支 `s243/*`、`s242/*` 未刪。以下為 S242 原文。 **Git state（S242 收工，2026-11-02）**: `origin/main` = `814bd0c`（#73、#74、#75 已合併）；線上執行碼 `3ef9ab6`；收工分支 `s242/closeout`（新 PR，只改治理文件）；已合併的本機分支 `s242/cover-title-refresh`、`s242/blnst-route`、`s242/qc-report-race` 未刪。以下為 S241 原文。 **Git state（S241 收工，2026-10-29）**: `main` = `da44e55`（#53 已合併並部署）；收工 commit 推上 `s241/model-migration-circular`（新 PR，含通函編號查找的 `backend/src` 改動）；已合併的本機分支 `s239/query-fusion`、`s240/deps-security` 未刪。以下為 S240 原文。 `main` = `77de1dd`（#55 已合併並部署）；收工 commit 推上 `s239/query-fusion`（PR #53，未合併，未含 #55）；已合併的本機分支 `s240/deps-security` 未刪。以下為 S239 原文。 **Git state（S239 收工，2026-10-21）**: 本機分支 `s239/query-fusion`（PR #53，已 rebase 到 `origin/main` `c4b3a6a`），收工 commit 推上同一分支；`main` 未含 S239 任何改動。以下為 S238 原文。 **Git state（S238 第二次收工，2026-10-13）**: `main` = `a67bd29`（#48／#49／#50 已合併）；收工分支 `s238/closeout-2` 由 `main` 開出，只改治理文件。以下為第一次收工原文。 **Git state（S238 收工，2026-10-13）**: 收工分支 **`s238/monitor-notify`**（由 `origin/main` `7b6a68b` 開出，合併了未合併的 `origin/s237/closeout`），PR #48 由 Leonard 指示合併（squash）；合併後 hash 下節核實。worktrees 1。以下為 S237 原文。 **Git state（S237 收工實測，2026-10-11）**: root 與 git root 皆為 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft` · 收工分支 **`s237/closeout`**（由未合併的 `origin/s236/closeout` 開出，再合併 `origin/main` `a344504`，只含收工文件）· worktrees **1**。`origin/main` = **`a344504`**；線上執行碼 **`a344504`**。已合併但仍在的本機分支（S235 記約 13 條，另加 `s235/route-b-closeout`、`s236/subject-check-v1`、`s236/closeout`、`s237/openai-model-default`）**未逐條核實、未刪**；清理須先唯讀核實已合併（squash 後 `git branch -d` 會報 not fully merged，要用「分支 tip 對其 squash commit 的樹比對＝0 檔差異」核實再 `-D`），並經 Leonard 批准。
- **Production flag state**: 【S241】Render **已無 `OPENAI_MODEL`**（Leonard 刪除），亦無 `JUDGE_MODEL`，即兩者皆碼內預設 `gpt-6-luna`＋`none`；`FEATURE_ROUTE_FIRST_SEARCH=1` 不變；**`FEATURE_CIRCULAR_NUMBER_LOOKUP=1`（2026-10-30 Leonard 加上，截圖核實前一版未設）**；`FEATURE_QUERY_FUSION`、`FEATURE_SUBJECT_CHECK` 皆未設。以下為 S239 原文。 【S239】Render 仍為 `OPENAI_MODEL=gpt-4o-mini`、無 `JUDGE_MODEL`（即碼內預設；PR #53 合併後預設變 `gpt-6-luna`＋`none`）。合併後要 Leonard 刪除 `OPENAI_MODEL`（或改 `gpt-6-luna` 並加 `OPENAI_REASONING_EFFORT=none`）；**切勿替 `gpt-4o-mini`／`gpt-4.1-mini` 設 effort**（被拒、合成靜默變空）；次序必須先合併後改 Render。`FEATURE_QUERY_FUSION` 不設。以下為原文。 `FEATURE_ROUTE_FIRST_SEARCH=1` 於 Render 環境變數（S220 啟用）。另兩個合成側 flag 未設定＝關閉。`FEATURE_SUBJECT_CHECK`（S236）未設定＝關閉。**Render 環境變數只有 Leonard 改得到，AI 改不到；`/health` 亦不報 flag。** **S237（2026-10-11）Leonard 以截圖核實 Render 環境變數共 8 個**：`CHANNEL_B_SYNC_KEY`、`CORS_ORIGIN`、`FEATURE_ROUTE_FIRST_SEARCH`、`KNOWLEDGE_PATH`、`OPENAI_API_KEY`、`OPENAI_MODEL=gpt-4o-mini`、`SUPABASE_ANON_KEY`、`SUPABASE_URL`；**無 `JUDGE_MODEL`（判官用碼內預設 `gpt-4.1-mini`）、無 `FEATURE_SUBJECT_CHECK`（即關閉）**。
- 🔴 **Push 邊界（S224 新增）**：`main` 受 ruleset 保護，**直接 `git push origin main` 會被拒**。一切改動走 PR：`git checkout -b <topic>/<name>` → `git push -u origin HEAD` → `gh pr create --base main --fill`，**然後由 Leonard 在 GitHub 網頁按 Squash and merge**。⚠️ **S234 實測曾被 auto mode 分類器擋下；S236–S237 實測 `gh pr merge <N> --squash` 三次成功（#43、#44、#46，均在 Leonard 明示「合併」之後）。** 仍只在 Leonard 明示指示時合併；若再被擋，不要重試或繞過。**每 session 盡量只開一個 PR（Leonard S234 定案）**：工作與收工文件同一分支；合併後才有的驗收結果留待下節起手補記。S234 因 Leonard 選「先合併 #38 讓頁面上線」而例外開了第二個（收工）PR；S236 同樣例外（Leonard 在收工前指示合併 #44，收工文件另開 `s236/closeout`）。S237 亦然（Leonard 指示合併 #46；收工另開 `s237/closeout`，並帶上未合併的 #45 內容）。⚠️ 分支若與 `main` 同一個 commit，`gh pr create` 會失敗並留下一條空分支（S224 中過兩次）——**開分支前先確認真的有未推的 commit**。合併用 squash，所以事後 `git branch -d` 會報「not fully merged」；要刪本機分支請先用「分支 tip vs 它的 squash commit 樹比對＝0 個檔案差異」核實，再用 `-D`。
- **生產寫入權限（S223 更正）**: AI **跑得到** `cb3_deprecate_stale --execute` 與 `ingest_one_source`（本節實跑三次全部通過）。**擋住破壞性寫入的已經不是機械閘，而是「要先取得 Leonard 明示批准」這條紀律。**

<!-- ack:section:next-task-required-reading -->
## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Read `dev/PROJECT_MASTER_SPEC.md` (long-term spec + cross-agent handoff knowledge: goals, architected systems, proven methods, failure lessons, locked decisions)
4b. Read `dev/HANDOFF_PACKAGE.md` (Session 110+ — clean verified-state snapshot built by empirical check, not paraphrase; sits above the §1 read set as the trusted current-state map)
4c. **Lazy-query 共用經驗庫 Playbook**（S138 接駁、AGENTS.md §1 第 5 步 + §14）：開工只讀 `…/Leonard's playbook/playbook/INDEX.md`（細入口，**冇全表**）；撞到 task 就 `grep -i "<關鍵字>" …/playbook/INDEX_TABLE.md` 配 trigger，配到先開對應卡；唔好讀晒所有卡。**S212：pointer 已升 v2，用完一張卡要喺該庫 `usage/policychecker.log.md` 檔尾 append 一行。**
5. Confirm environment: backend needs `OPENAI_API_KEY` in `backend/.env`

---

## Architecture Decisions (Locked — 2026-04-16)

### Decision 1 — Public Entry + Full Workspace
```
index.html  ←  EDB S1 Home / document workspace entry
    │
    ├── q.html                  ← Quick Q&A (local knowledge.json search)
    ├── t-purchase.html         ← Template detail + draft flow
    └── app.html                ← K1知識平台 full React workspace

app.html
    ├── 🔍 政策搜尋              ← 已核實資料 / 來源文件 / 合併搜尋
    ├── 📚 指引文件庫              ← 3-level sort: category → sub_category → time desc
    ├── 📄 通告分析
    ├── ℹ️  平台介紹
    ├── ✍️  知識提煉（Admin）     ← 左右分欄佈局 + 即時行內修訂
    └── ⚙️  知識管理（Admin）
```

### Decision 2 — Backend API for Channel B Search
現有 Node.js TypeScript backend 擴展，新增端點：
```
/api/search/channel-a    ← role_facts.json keyword/semantic search
/api/search/channel-b    ← wiki_index.json cosine search (NO top-k limit, return all)
/api/search/combined     ← A+B merged, deduped, source-labelled
/api/channel-b/prompt    ← GET/SET Channel B extraction & synthesis prompts (Admin)
```
- Channel B 搜尋**不設 top-4 限制**，全數返回，前端分頁顯示
- 利用現有 `embeddingClient.ts` 做 query embedding
- 新增 `backend/src/lib/wikiRepository.ts`（載入 wiki_index.json + cosine 計算）

### Decision 3 — Platform Stats Are Dynamic (A+B Combined)
- 平台介紹 tab 的統計數字（事實數、chunks 數等）從實際資料動態計算
- 反映 Channel A（role_facts.json）+ Channel B（wiki_index.json）合計
- 不再硬編碼「109+」等數字

### Decision 4 — Channel B Admin Prompt Editor
- Channel B candidates 獨立於 Channel A queue
- Admin 可在「Channel B 後台」tab 編輯 SYSTEM_PROMPT_B 及 SYNTHESIS_PROMPT
- 提供測試沙盒（貼入段落 → 即時看提取結果）及新舊 Prompt 對比面板
- 品質指標：字數達標率、來源引用率、合規風險識別率

### Decision 5 — Two-Channel Knowledge Pipeline (Original)
**Channel A — Human Review（主線）**
```
source_registry → vault PDFs → extract_candidates.py
→ candidate_queue.js → Admin Approve (inline edit) → role_facts.json → Circular System
```

**Channel B — Full AI（副線）**
```
source_registry → same vault PDFs → ai_extract.py
→ ai_candidate_queue.json (independent) → wiki_index.json (vector search)
→ /api/search/channel-b (backend) → 智能搜尋 UI
```
- Channel B Circular System 接入**明確暫停**，待質素測試後決定

### Decision 6 — Guidelines Dual Sort
- GUIDELINES_REGISTRY 加入 `sub_category` 欄位（例如 `procurement`、`lsg`、`cpd`、`sen`）
- 排序：範疇 → 同科類 → 時序降序
- 視覺：同科分組小標題

### Decision 7 — WordCloud Removed
- QAPanel 的 floatWord 浮動動畫刪除（視覺效果差）

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. **S126 (2026-05-26)** `check_freshness.py --dry-run` = **Checked: 147 / Changes: 20 / Errors: 1 / Threshold: 7 → exit 0** ✅。**Root cause of 5 連 chronic fail since 2026-04-30 = script `AttributeError` 撞 `freshness_metadata=null` (line 101) crash 喺 entry ~22，唔係 handoff 估計嘅 `if errors > 0: sys.exit(1)`（後者係次要、threshold 太嚴）**；§G.2 verify-don't-trust-docs 再中。修：`meta = src.get("freshness_metadata") or {}` + `threshold = max(5, total_checked // 20)` gate + summary 加 failed-sids list 方便 GH Actions log artifact 分析。20 EDB CHANGE detected（包 sag_2025_11 / g24 / g29 / stat_* 等）+ 1 dead URL g28 — freshness_metadata 寫返 registry 留下次 sub-task；g28 EDB URL re-discovery 列 follow-up。
3. ⚠️ **`npm run regression:semantic` 實測 2026-05-17 S113：overall=FAIL（PASS=9 / FAIL=2）**。原寫「Online semantic regression PASS=12/FAIL=0 (2026-04-12) ✅」**已 false / stale**（2026-04-12 舊值，dedup 前；S113 startup verify 教訓再現 §G.2）。兩個 FAIL 同 S1/S2 無關、Leonard 裁示**只記錄不修**：
   - **FAIL-A（真 product regression）role-bucket `finance_distinct=false`**：S111 dedup（792→455，2026-05-16）把跨角色重複摺入 `all_roles`，令 `finance.all_roles`=83 條/2832 字；`knowledgeSelector` 排序 all_roles 行先→砍 600 字，頭 ~14 條 all_roles 已蓋爆 budget，**subject_head/panel_chair 角色專屬 finance 事實永遠注入唔到** → Circular System 對該兩角色嘅 finance 注入自 2026-05-16 起退化成「只通用、無角色專屬」。無 budget 時 distinct=True（角色拆分本身冇壞）。**未修**（涉 dedup/budget/排序設計決定，待 Leonard 排）。
   - **FAIL-B（瑣碎 doc-debt）schema consistency**：`backend/scripts/semanticRegression.ts:292` 硬斷言 `version === "1.3.1"`，實際 knowledge=2.3.0 / guidelines=2.2.0。stale 測試斷言，無行為影響。**未修**。
4. `npm run check`（typecheck）✅ / `npm run build` ✅（S113 實測，未變）。
5. **✅ S209 實測定案（唔使再查）：`check_served_urls.py` 監察嘅係 `wiki_chunks.url`，唔係 registry `url_primary`。** `fetch_served_urls()` = `SELECT url, source_id FROM wiki_chunks` 全表分頁，CI `limit=0` 全掃。所以**任何 per-chunk URL（含 S207 嘅 section deep link）一入庫即受每週一 11:00 UTC 監察**。證據四重：(a) live 逐源比對 g14 10 + g17 6 = **16/16** 真係喺 `wiki_chunks.url`；(b) CI run #11（2026-08-24 11:18 UTC）17,478 rows → **299 distinct URL 全測**，295 OK / 4 broken / 0 error，broken 冇一條係 g14/g17；(c) 本地 `--verbose` 全掃複現同一組數，16 條逐條印 HTTP 200；(d) distinct URL 08-17 **284** → 08-24 **299**，新 deep link 自動入集。紅測：唔存在嘅 `chapter-seven.html` → 404 → broken → 歸屬 g14。**錯誤源頭已清**：S207 `verify_section_urls` docstring、handoff OP⑥、DOC_SYNC row 41 三處。
6. **⚠️ S209 記錄：監察報住 4 條真 404 冇人跟。** `edb_pnet_annex_jul2025`、`eoebg_rates_2026` 最遲 2026-08-03 起壞；`blnst_test_candidate_notes`、`blnst_test_notes_nondeg` 最遲 2026-08-10 起壞。GitHub Issue #6 開住。用戶撳落去係真 404。**監察系統正常做嘢，係下游冇接手** —— re-anchor 係人手閘，要 Leonard 逐條批。同 S195 嗰兩條一樣嘅家族。
8. **✅ S209 實測定案：公開片段數以前係流水帳，唔係真數。** `execute_ingest.current_chunk_total()` 由 `knowledge.json` 讀個數再加自己嗰筆 delta 寫返七個鏡像檔 —— 純加法、從來冇對過 Supabase，所以歷史上任何一次少計都永久帶落去（實測長期少 1）。已改為入庫後 `live_total_count()` 由 store 讀真數，舊數只留低做「要替換嗰串字」同 fallback，唔夾會出 CI annotation。**改動後唔好再靠加減推算片段數** —— 清走 chunk 之後一律行 `live_display_sync(current_chunk_total(), live_total_count())`。
9. **✅ S209：4 條 404 已清（Leonard 批）。** 兩條純 URL churn re-point（`eoebg_rates_2026`、`edb_pnet_annex_jul2025`，四個引用數字逐個對返新 PDF 先寫）；兩條 `blnst_test_*` 共 13 chunks 係 2026-06-07 場次文件、EDB 整個 notes 家族落架 → 退役刪除，registry status=deprecated。**刻意冇指去 `QA_BLNST_Apr26_tc.pdf`**（另一份文件；200-但-錯檔比 404 更難捉，見 S194 `ict_sss_2021`）。BLNST 覆蓋由 `edbc13_2022_blnst` + `edbcm141_2025_blnst` 承接，backend SOURCE_SET 已清走死 id。
11. **✅ S209：`g28` 已入庫（40 chunks / 7 份文件），但揪出兩個未修嘅殘留。** (a) **`g17` 兩條 chunk 頁碼錯** —— S207 把三份各 1 頁嘅附件連續編成 Page 1/2/3，UI 顯示「頁 2 ↗」「頁 3 ↗」都指唔到；修法＝重生 extract + 重入 13 條。(b) **`gifted_policy_docs` 10/23 chunks** 喺新切法下會改善（佢有 `=== introduction === / === detail ===` 但冇 `section_urls`），要重入庫先生效。(c) **g28 唔使 spotlight** —— 加咗又同一 session 移走：用**內容專屬** query 實測（未部署任何 route 改動嘅 build），「Zoom 保安設定及使用建議」rank **0 @0.628**、「殭屍網絡」rank **1 @0.396**，純 ANN 已經到位。我最初用闊 query（「學校資訊保安」）搵唔到就當係「新細源 ANN 餓死」，**係揀錯 phrasing 得出嘅結論** —— 同 S195 spotlight prune 中嘅陷阱一模一樣，只係方向相反。(d) **route regex 未動** —— `digital_education` 個關鍵字 regex 冇任何資訊保安／網絡安全／雲端字眼，所以「資訊保安」一類 query 仲未 route 到嗰度；g28 而家靠 spotlight overlay 出街。改 regex 係檢索改動，要行 eval before→after 先做。
12. **❌ S209 實測：EDB 冇「學校使用雲端服務指引」。** g28 hub 上 8 份實質文件全文掃描，「雲」／"cloud" 合共 **0** 次；EDB 資訊保安頁「雲」字亦 0 次。最接近嘅權威文件係 **PCPD《雲端運算指引資料》(2025-01，13 頁)**（Leonard 提供），講 PDPO 保障資料第 2(3)/3/4 原則同第 65(2) 條，但「學校」／「教育」0 次，係通用機構指引。OGCIO/DPO 有 ISPG-SM04 雲端保安實務指引，但個 PDF URL 而家跳去 JS-gated 頁，curl 抽唔到，且對象係政府部門。**未入庫，待 Leonard 決定。**
13. **📌 S209 記錄：非-EDB 來源唔係先例問題。** 庫入面已有 **8 個非-EDB 域、208 條 chunk**（教城 81 / 廉署 78 / 衞生署 14 / 教育條例 ILO 11 / 機電署 7 / 審計署 4 / 學資處 2+11）。但 registry `authority` 欄位 **273/273 全部寫死 `edb`** —— 呢個欄位一直冇如實反映，屬資料品質債。
10. **🧭 S209 通則（一 session 內喺四個地方撞到同一條病）：任何要人做決定嘅表面，都必須有出口。** 只入唔出嘅清單一定會變牆紙，跟住真訊號就會被埋葬 —— Issue #6 由 2026-08-03 起準確列住 4 條真 404，冇人跟，因為佢同幾百項噪音混埋。四個實例同修法：(a) **待批入庫清單** 45 日 feed 窗令「唔會剔」嘅過渡通告霸住六星期 → 超過 21 日收摺；(b) **served-url issue** clean run early-return，永遠開住掛住舊清單 → clean run 留言＋自動閂；(c) **discovery issue** 每週重報成個 backlog（238 項，大部分永遠唔會入庫）→ 加 first-seen 帳，只報今次新出現嘅，backlog 收摺；(d) **expiry 清單** 已清走嘅源 chunks=0 但仍然過期，會永遠掛喺待辦 → 拆「待清走 / 已清走」。**改任何一個監察嘅 issue 開閂邏輯或清單長度，順手檢查其餘幾個**（已入 DOC_SYNC row 35）。
7. **✅ S209 新機制：`refetch_blocked`（registry 欄位）+ `expand_vault.run_fetch()` 下載前 fail closed。** 覆蓋 `expand_vault --fetch` 一條路；`dev/vault/process_signals.py` 亦寫 vault extract，但佢只處理通告 feed 嘅新 PDF signal，砌唔到現有 `section_urls` 源，故唔需要同一道閘。`test_carry_rules.py` 17→30 斷言（含結構不變式：有 `section_urls` 必有 `refetch_blocked`），`--prove-assertions` 8→16。

---

<!-- ack:section:next-priorities -->
## Open Priorities

**Recommended next step：退役 `EDBC_9_2019_E`（2 段 `footnote_curated`）。** 理由：EDBC 4/2026 已取代通告 9/2019，它仍在「SEN學生留級」查詢佔第一格；Leonard 於 S238 批准但當時被擋下，批准已隔多節，**執行前先向 Leonard 再確認**。

1. **退役 `EDBC_9_2019_E`**：先 `select=*` 匯出到 `dev/init_backup/<ts>/` → `DELETE ?source_id=eq.EDBC_9_2019_E` → `live_display_sync` 同步公開數字 → 補 `update_log.json`。
2. **減維護負擔**（Leonard 2026-11-15 定為優先方向）：第一步交接檔瘦身已做（PR #92 已合併）；第二步查明「舊帳與新故障分開」及「每日提交」皆為既有刻意設計（S234 狀態頁、`generatedAt` 過期偵測），真正缺口是質素檢查惡化沒有通知，已加 `qc-regression` 通知（PR #93 已合併；首次真實運行開出 Issue #94，Leonard 確認收到電郵）。Issue #94 查明 194 條中 143 條是檢查誤報（網頁／試算表無頁碼、標記首個「=」被切掉），Leonard 批准把 `PAGE_ANCHORED` 改為只計 PDF、標記判斷與後端一致、基準 179 → 51（PR #95 已合併，線上 QC 實測 51、Issue #94 已自動關閉）；**餘下 51 條真缺口未修**：41 條 PDF footnote 欠 `#page=`（16 個來源）、10 條 `gifted_policy_docs`（網址是 PDF、內容抽自網頁），修正要寫生產，先列清單給 Leonard 批准。第三步建議先做 Freshness（35 項中約半數是索引頁／統計頁，要改監察方式而非逐項處理）；其後清理 `PHANTOM` 36／`UNLISTED` 118／Freshness（Issue #77）累積清單。
3. **待 Leonard 決定**：是否開 `FEATURE_SUBJECT_CHECK`；文件標註修好重開還是刪除；已收起功能的公開端點去留；`search_log` 加拒答原因（DDL）；關閉 #70；S244 三條 footnote 的粵語問句是否改寫；語料庫時限段落是否交 `check_expiry.py`；`app.html` 角色標籤「全校」是否移除；Kit 是否升級至 v0.4.6。
4. **定期系統更新檢查**：上次 2026-10-30，約 2026-11-29 到期（規則在 `dev/rules/coding.md` `## Project Rules`）。
5. **提升片段層召回**（長期）：已排除七條方向，未試的只餘 cross-encoder 重排（上限多救 42 題）；動手前必讀 `dev/SESSION_STATE_DETAIL.md` 的 ②。

其餘只監察或次序較後的項目（封版閘、累積遺留、HNSW 監察、線上探測真實當機路徑、executor 多份批准衝突、Freshness 其餘項）詳見 `dev/SESSION_STATE_DETAIL.md`。

> 詳情與證據：`dev/SESSION_STATE_DETAIL.md`（做到該項才讀）；改寫前原文：`dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md` E 節。

## Backlog（次優先序，視 OP 完成情況流轉）

**治理側（S216 新增；S218 由 Open Priorities 原文移入，一字未改）：**

⑨ 🟢 **【S227 提出，S228 已修】`backend/scripts/*.ts` 從來不在 `npm run check` 覆蓋範圍內。** 成因：`backend/tsconfig.json` 的 `include` 只有 `src/**/*.ts`，所以 `npx tsc -p` 對 `scripts/` 完全不生效，S227 第一次跑 typecheck 報「零錯」其實是空過。**修法採選項 (a)**：新增 `backend/tsconfig.scripts.json`（`extends` 主檔、`noEmit: true`、`rootDir: "."`，避開 `rootDir: src` 會爆的 outDir 錯），`npm run check` 改為串跑兩個 project，另留 `npm run check:scripts` 單獨用。**順帶修好四個一直潛伏的型別錯**：`groundedSynthesisProbe.ts` 的 filter callback 把元素型別窄成單一欄位（連帶令整段無法定型）、`groundedSynthesisRegression.ts` 在 `EvidenceChunk` 上讀它沒有宣告的 `id`／`content_type`（那兩個欄位執行期確實存在，因為判的是「揀中邊條」而非合成本身，故以測試自己的形狀讀取，不為遷就測試而放寬生產介面）。**紅測**：在 `scripts/` 注入一個型別錯，閘準確轉紅 1 條；還原後 exit 0。`regression:grounded` 48/48 PASS。

⑧ **【S226 新增】`closeout-status` 的 lifecycle 配對規則與本專案的交接密度衝突。** 實況：本節連跑 8 次，前三次各捉到一件真事（已完成項留在未了清單、三項過時的「未做」、§4 合規備註放錯段），**其後每次都指向另一對「依合約必須同時出現」的段落** —— 「量到但未修」的事實必須同時在 `Validation / QC`（證據）與 `Open Priorities`（下一步），最後一次甚至指向 S219 起的 cold zone（Risks 2）。**選項**：(a) 與上游確認該配對規則是否應排除 cold zone 與證據段；(b) 在本專案定義「必然重疊」白名單；(c) 接受它在本專案長期回報 blocked，並以 `Closeout outcome` 逐次記錄邊界（本節採此法）。**不應採用的做法**：靠改寫文字去通過它 —— 那會把交接檔改壞。

⑥ **【S216 提出，S219 修好其中一半】交接檔有 8 個 `ack` marker 未有專屬章節。** `durable-anchors`／`closeout-reconciled-state`／`task-understanding-summary`／`active-objective`／`sync-status` 五個 section marker，加 `user-intent`／`task-essence`／`success-criteria` 三個 field marker，現時集中放在檔頂並附註釋。**不影響 `doctor` 與 `closeout-status`**（前者只檢查 marker 存在，後者只讀四節加開場白），但這些章節對下個 agent 而言機械上讀不到 —— **這半邊仍未做**。（另一半的邊界標記範圍問題已於 S219 修好，不再是待辦；詳見該節 Last Session Record。）

⑦ **【S216 新增，blocked】`dev/DOC_SYNC_CHECKLIST.md` 的 INIT.md 鏡像規則已失效。** row「Governance rule change (AGENTS.md)」與「New governance file added to install」要求同步 `INIT.md` FILE 1 mirror，但 `INIT.md`（1,036 行，2026-05-10）鏡像的是 package 化之前的 AGENTS.md 結構（§4a／§5a／§11a），v0.3.66 核心根本沒有這些章節。**本節不執行該同步**，因為要先決定 `INIT.md` 是否已退役 —— 這是 Leonard 的決定，不是機械同步。

**S204 新增／流轉：**
- **【S210 新增，Leonard 2026-08-26 拍板】正文連結零監察 —— 開新監察嘅正確落點。** 起因係 Leonard 問「課程專頁使唔使 monitoring」。**定案：課程專頁唔監察** —— 只得 2 條、逐學期換（`debp-pdp.html` 課程表、教城 EdAcademy），監察掛上去週週報「有變」，正正係紀律 #14 嗰種必然變牆紙嘅閘；而耐用嗰半邊（每三年 30 小時培訓／每年 50,000 名額）已經喺 EDBCM156 同《藍圖》入面入咗庫兼受監察。**真缺口喺另一邊**：全庫 17,568 條 chunk 掃過 —— anchor URL（`wiki_chunks.url`，受每週一監察）**420** 條；寫喺 chunk **正文**入面嘅 URL 形狀字串 **3,011** 條；兩者只重疊 **6** 條 → **3,005 條零監察**。頭幾個 host：`www.edb.gov.hk` 733、`applications.edb.gov.hk` 74、`www.hkedcity.net` 45、`bit.ly` 18。用戶喺答案入面撳嘅連結，絕大部分冇任何嘢睇住。**⚠️ 3,005 係上限唔係實數**：PDF 換行會把一條 URL 斬成幾段殘缺字串（S210 喺 EDBCM156 就要人手重組先攞到真 URL），要真數必須先對全庫做同一套重組 —— 呢個重組本身就係呢件工嘅第一步。監察機制上 `check_served_urls.py` 只 `select=url,source_id`，**從來唔讀 chunk 正文**，所以呢個缺口係結構性、唔係漏咗跑。
- ~~**時限性資料標示**~~ → **S209 已建，定案細分咗**（Leonard 2026-08-24 補充）：S204 原本寫「標示而唔係刪」，而家分兩類 —— **年度版本文件**（費率表、校曆、年曆）舊版仍是當年依據 → 照舊 `dated_edition`**標示唔刪**；**一次性事件文件**（簡介會／培訓／比賽／獎項提名／測試場次／報名截止）過咗零參考價值 → `ephemeral` **到期清走**。已落地：`dev/source/lifecycle.py` 分類（入庫時 stamp 四個 registry 欄位）+ `dev/source/check_expiry.py` 第 6 監察 + ops `expiry-issue.yml` 每週二剔一剔清走。**仲未做**：(a) UI 顯示 `現行 / 已過期 / 已有新版` 標示（前端零改動至今）；(b) 271 個舊源冇 `lifecycle` 標，`check_expiry.py --classify` 可出提案但未 backfill；(c) 「每年檢查 landing page 有冇新學年版」呢半邊仍未做。
- **公眾提交表單**（Leonard 提）：Phase 1 = Google Form + 平台加一粒「意見／報錯」掣（零代碼，先驗證有冇人用）；Phase 2 = 站內表單 → 現有 Render 後端 → Supabase 新表（要處理防濫發、唔收非必要個人資料）。
- **範本下載恢復**：`policy_templates.json`（106 檔／15 範疇）未隨知識庫更新，S204 已用 `window.FEATURE_TABS.templates=false` 收起。重新生成 manifest 後把 flag 揼返 true 即復原（面板 code 原封未動）。
- **真亂碼未量度**：S204 掃描時偵測器分唔清長 URL／底線填充，故**冇報數**。`gifted_ge_series` 確有真 CID 亂碼實例（playbook `pdf-extraction-mojibake-triage`）。要做要另寫準確偵測。
- **承 S203 未完**：judge 對象移植非-prompt 機制（②，工具 `v4a/v4b_s202.txt` + fresh 集已備）；Channel A Option 2 入庫 117 條（③，HIGH risk 跨 session）；24 條純職責歸屬孤兒決定（④）；`PUBLISH_PAT` fine-grained 確認（⑤，只有 Leonard 做得到）；拆 backend channel-a 半邊（⑥，**S205 已解鎖** —— route-probe 兩次讀齊、零外部呼叫、probe 已刪，前置條件已滿足）；總帳 172 UNVERIFIED + 107 PROVISIONAL 未讀（⑦）；g24/sag 合併 PLAN 備妥等 GO（⑧，真數 377 重疊、g24 零獨有內容）；維護：封面 baseline 208 / spotlight 6 源 / `MIN_OVERLAP` 兩份鏡像（⑨）。

**原有：**
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）
- **雲端 OCR 引擎選項**（image-PDF ingestion 升級線，S180 評估）：Google Vision `DOCUMENT_TEXT_DETECTION`（逐字信心 + bounding box、每月 1,000 單位永久免費 + ~$1.50/1,000、要綁卡開 billing）／Mistral OCR（Markdown+表格、~$2/1,000）——比現用 `gpt-4o` 圖像 OCR「draft 質」可能更準更平，且 bbox 可餵返 grid 重建。命中 image-PDF 質素問題（如 DEBP 主藍圖 ~16 圖像頁）先評估：**真檔實測 + 開 Google billing**（ingestion 處理公開文件、無未成年私隱顧慮；後端已存在故唔需要 brief 嗰套 serverless key-proxy）。詳見 playbook inbox 提案 `2026-06-24-edb-knowledge-cloud-ocr-engine-options.md` + `doc-extract-method-ladder` 卡。出處：Leonard 一份 OCR 收費版 brief（2026-06，已核實價）。

<!-- ack:section:completed-this-session -->
## Last Session Record

1. UTC date: 2026-11-15（收工因用量上限中斷，2026-11-16 下一節起手補完）
2. Session ID: S248。Leonard 定「減維護負擔」為優先方向；三個 PR 皆由 Leonard 明示後合併。
3. Completed（證據見 `## Validation / QC` S248）：
   - ✅ **交接檔瘦身**（PR #92）：歷史原文移入 `dev/archive/`，詳情移入 `dev/SESSION_STATE_DETAIL.md`。
   - ✅ **QC 惡化通知**（PR #93）：`qc-regression` Issue 並 @Leonard，通知鏈經真實運行驗證。
   - ✅ **`PAGE_ANCHORED` 定義修正**（PR #95）：基準 179 → 51，Issue #94 已關閉。
4. 生產改動：無（零 Supabase、零 flag；PR #91 自動入庫 `edbcm203_2026` +5 屬 Option A executor，非本節人手操作）。
5. Carry-forward：未完成事項一律不在此列舉，全部歸入 `## Open Priorities`。

<!-- 本地邊界 marker（S232 由 S231 之前上移至此；S236 沿用）：令 completed-this-session 的抽取範圍只涵蓋最新一節 -->
<!-- ack:section:session-history -->
## Previous Session Record (S247)

1. UTC date: 2026-11-09
2. Session ID: S247。「開工」（頂層轉 Draft）→ 清理 `dev/init_backup/` 任務（只讀審核先行）→「繼續」→「批准刪除＋加規則」→「開分支並開 PR」→「CI 綠後合併」→「收工」。
3. Completed（證據見 `## Validation / QC` S247）：
   - ✅ **刪除 26 份舊版／重複 `wiki_index.json` 備份**，釋放約 11.09 GB；保留 `20261101_195458_UTC`（與現用檔 SHA-256 相同）及其餘 43 個備份。
   - ✅ **備份保留規則**寫入 `dev/rules/safety.md` `## Project Rules`；PR #89 合併為 `82be06e`。
4. 生產改動：無（零 Supabase、零 flag、零部署）。
5. Carry-forward：未完成事項一律不在此列舉，全部歸入 `## Open Priorities`（S246 收工段）。

## Previous Session Record (S246)

1. UTC date: 2026-11-08
2. Session ID: S246。「開工」（頂層轉 Draft）→「list out 出處我需要的選擇」→「甲」→「批准寫入」→「匯出備份」→「批准刪除」→「加入 PR #87」→「CI 綠後合併」→「繼續」→「刪舊分支＋登記來源」→「收工」。
3. Completed（證據見 `## Validation / QC` S246）：
   - ✅ **Option 2 清單清空**：租金收入以 g02 第 15 頁按原文修正；清單 resolved 289、dropped 166、餘 0。
   - ✅ **109 行 `approved_fact` 備份後刪除**；Supabase 17,074／315；公開數字同步並於線上讀回。
   - ✅ **PR #87 合併**（`62647fe`）；舊分支 `s244-option2-round1` 已刪；兩個 footnote 來源判定不登記（按設計）。
4. 生產改動：Supabase −109；零 DDL、零 flag、零部署。
5. Carry-forward：未完成事項一律不在此列舉，全部歸入 `## Open Priorities`（S246 收工段）。

## Previous Session Record (S245)

1. UTC date: 2026-11-05
2. Session ID: S245。「/handoff-kit-start」→「繼續」→「Approve all」→「Approve ingest」→「Commit to PR #86」（#86 已合併，改開新分支）→「Open new PR」→「收工」。
3. Completed（證據見 `## Validation / QC` S245）：
   - ✅ **Option 2 第二輪**：清單 39 → 1（23 條按原文修正入出處、1 條經 footnote、14 條剔除）。
   - ✅ **1 條 curated footnote 入 Supabase**（176 → 177，`footnote_fn_byod_edb_support`），線上已載入；公開數字同步至 17,183／315。
   - ✅ **commit 與 push**：PR #87（`s245-option2-round2`），未合併。
4. 生產改動：Supabase +1；零 DDL、零 flag、零部署。
5. Carry-forward：未完成事項一律不在此列舉，全部歸入 `## Open Priorities`（S245 收工段）。

<!-- 歷史原文（S248 瘦身，2026-11-15）：`## Previous Session Record` S244 及以前 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔B〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- 歷史原文（S248 瘦身，2026-11-15）：`## Detail Archive (S212–S214)` 整節 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔C〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- ack:section:state-reconciliation-check -->
## State Reconciliation Check

- **2026-11-16 S248 closeout reconciliation（補完；交接檔瘦身 ／ QC 惡化通知 ／ `PAGE_ANCHORED` 修正）：** S248 於 2026-11-15 因用量上限中斷，下一節起手讀完本檔全文（398 行）並跑起手探針後補完。差異式更新：`Current Baseline` 3（加 2026-11-16 實測）、4（S248 收工狀態）· `Validation / QC`（新增 S248 段於最前）· `User Environment` Git state · `Last Session Record`（S248；S247 原文改題為 `Previous Session Record (S247)`，內容不變）· 本段各 S248 欄位 · `Handoff Sufficiency Check` · `Next Session Opening Message`（刪去「收工未做完」一段）。**未改**：`Risks / Blockers`、`Open Priorities`（S248 中斷前已重生，逐項核過仍為現況）及其餘章節。
- **2026-11-09 S247 closeout reconciliation（init_backup 舊版 wiki_index 清理 ／ 備份保留規則 ／ PR #89 合併）：** 差異式更新：`Current Baseline` 4（S247 git 狀態）· `Validation / QC`（新增 S247 段於最前）· `User Environment` Git state · `Open Priorities`（加 S247 一句，Recommended next step 不變）· `Last Session Record`（S247；S246 原文改題為 `Previous Session Record (S246)`，內容不變）· 本段六個 S247 欄位 · `Handoff Sufficiency Check` · `Next Session Opening Message`。**未改**：`Current Baseline` 1、2、3、5、6、7 · `Risks / Blockers` · 其餘章節。`ack` marker 數改前改後一致。⚠️ 本節收工未完整讀取本檔全文（約 750 KB）：只讀了被改動的章節與 Open Priorities、Risks 開首、Current Baseline；未改動章節保持原位元組。
- **2026-11-08 S246 closeout reconciliation（Option 2 清單清空 ／ 109 行副本刪除 ／ PR #87 合併）：** 工作 commit 併入 PR #87 並已合併；收工另開分支 `s246-closeout`（由 `d6b18f6` 開出）。差異式更新：`Current Baseline` 1、2、4（前置 S246 句，舊文保留）· `Validation / QC` 新增 S246 七點於最前 · `User Environment` Git state · `Open Priorities` 前置 S246 段（新 Recommended next step）· `Last Session Record` 換 S246、S245 移入歷史 · 本節各欄 · `Handoff Sufficiency Check` · 開場訊息；`dev/PROJECT_INDEX.md` Branch / commit 由 S243 舊快照更新。其餘章節未動。
<!-- 歷史原文（S248 瘦身，2026-11-15）：`## State Reconciliation Check` S245 及以前的逐節敍述、各欄位 S246 及以前的舊行、S217 及以前的區塊 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔D1〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- ack:field:stale-snapshots-left -->
- Stale snapshots left (S248): no — Current Baseline 3、4、User Environment Git state、PROJECT_INDEX Branch / commit 已改為 2026-11-16 實測（origin/main 61ba038、線上 8b118fd）；S247 句標為原文。

<!-- ack:field:closeout-outcome -->
- Closeout outcome (S248): complete — 交接、log、DOC_SYNC_REGISTRY、PROJECT_INDEX 已寫入並讀回；開場鏡像重生並核對；closeout-status 為最終讀回。

<!-- ack:field:project-required-persistence -->
- Project-required persistence (S248): complete — 工作 commit 已隨 PR #92、#93、#95 合併入 `main`；收工 commit 推上 `s248-closeout`（PR #96），只改治理文件，合併待 Leonard 指示，毋須部署。

<!-- ack:field:recommended-next-step-explicit -->
- Recommended next step is explicit and reasoned (S248): yes — `## Open Priorities` 開首：退役 `EDBC_9_2019_E`，理由同段；執行前再確認。

<!-- ack:field:next-ai-can-continue -->
- Next AI can continue (S248): yes — 由 `AGENTS.md`、本檔 `## Open Priorities` 1、2 即可續做，證據見 `## Handoff Sufficiency Check` 的 Reconstruction evidence。

<!-- ack:field:opening-message-matches-current-state -->
- Opening message matches current state (S248): yes — 開場訊息記 origin/main 61ba038、線上 8b118fd、17,079／316、footnote 177、S248 三項已完成、下一步退役 EDBC_9_2019_E，與 `## Open Priorities` 及 `## Current Baseline` 一致。

<!-- ack:field:state-sections-rewritten-or-confirmed -->
- **State sections rewritten or confirmed current（S218）：** **重寫**：`Current Baseline` 第 1 項（探針歸屬改 S218 並補齊五個實測值）· 第 2 項（HEAD 由 `612e13e` 更正為 `0f8a7c9`，並新增「Render 報舊 commit 屬正常、零執行碼差異」的定性）· `Validation / QC`（新增 S218 段，明寫零重跑、S217 數值為何仍有效、`doctor` 仍未驗證）· `Risks / Blockers` 第 1 項（補 S218 實測 bot 本輪未推）· `Open Priorities`（**整段重生**：S217 的 ① 已結案故移除，②' 升為 ①，其餘重排；治理側原 ⑥⑦ 依 §4 五項上限原文移入 `## Backlog` 治理側段，`grep` 實測全檔只出現一次 = 搬非複製）· `Last Session Record`（重生為 S218，S217 降為 `Previous Session Record (S217)`，內容一字未改）· `Next Session Opening Message`（重生，新增「/health 報舊 commit 是正常」的防誤判段）。**逐段讀過確認仍 current、不改**：`Architecture Decisions`、`Regression / Verification Notes`、`Backlog` 原有內容、`User Environment`、`Mandatory Start Checklist`、`Supabase Technical Notes`、`Detail Archive`、所有 `Previous Session Record`。

<!-- ack:field:lifecycle-conflicts-resolved -->
- **Lifecycle conflicts resolved（S218）：** 是，逐項對過五節。(a) **已完成項不再以未了項身分留存**：S217 的七個 commit 去向已於上節結案，本節從 `Open Priorities` 移除，其事實改由 `Current Baseline` 第 2 項承載。(b) **本節無任何完成項** —— 探針與資訊回覆都不產生待辦，故無新項需要降級。(c) **未解項全部保留**：185 題 live、`backend/README.md`、三題 recall、fidelity、S212／S213 遺留、治理兩項、`qc_report.json` ERROR 全部仍列未解，無一被誤標完成。(d) **未驗證項明確標示**：`agent-handoff-kit doctor` 連續兩節跑不到，`Validation / QC` 與開場白皆寫明「列為未驗證，不當通過」。(e) **開場白與現況一致**：HEAD、部署 commit、flag 狀態、OP 編號三處對齊。

<!-- ack:field:persistence-routing-checked -->
- **Persistence routing checked（S218）：** 是。當前狀態／風險／建議下一步／OP 重排 → 本 handoff；探針逐項數值、git 差距的逐檔驗證、桌面與 mobile 的分別問答 → `dev/SESSION_LOG.md` S218 條（trace 證據）。**未升 `dev/PROJECT_DECISIONS.md`** —— 本節無架構取捨、無研究推導決定。**未改 `dev/CODEBASE_CONTEXT.md`** —— 技術棧、目錄、build 指令、External Services、Key Decisions 本節皆未變。**未改 `dev/PROJECT_INDEX.md` 的 Branch / commit 列**？已改（見下方 Sync）。
Lifecycle consistency rule: compare `Completed This Session`, `Validation / QC`, `Next Priorities`, `Risks / Blockers`, and `Next Session Opening Message`. A completed or verified item must not remain as an unresolved next priority, active risk, or startup instruction unless it is explicitly reclassified as monitor-only, follow-up scope, blocked, or reopened with the missing evidence or trigger condition stated.
Persistence routing rule: one-time delivery instructions, historical validation evidence, old hashes, old version facts, and incident notes must stay in trace evidence unless they still affect the next action.
Recommended next-step rule: `Next Priorities` must name the single recommended next action and a short reason before listing additional options, unless the next action is blocked or genuinely requires a user decision.

<!-- ack:section:handoff-sufficiency-check -->
## Handoff Sufficiency Check

Can the next AI continue from `AGENTS.md`, this handoff, `dev/PROJECT_INDEX.md`, and needed rule packs without searching old log history?

Answer: yes — S248 收工覆核（2026-11-16：origin/main 61ba038、線上 8b118fd；Supabase 17,079／316；footnote 177）；以下 S247 覆核內容除數字外仍適用。S247 收工覆核（origin/main 82be06e、線上 20fd4a4；Supabase 17,074／315；footnote 177；init_backup 已清理）；以下 S246 覆核內容仍適用。S246 收工覆核（origin/main d6b18f6、線上 20fd4a4；Supabase 17,074／315；footnote 177；清單 0 條、109 行副本已刪）。下一個 agent 只讀 `AGENTS.md` ＋ 本檔即可續做：現況（`## Current Baseline` 1、2、4）、已做與證據（`## Validation / QC` S246）、下一步（`## Open Priorities` 開首 S246 段）、邊界（`## User Environment`：合併、DDL、Supabase 寫入或刪除、外部模型批量都要 Leonard 明示）。

Reconstruction evidence: **S248 補充**：父目標是 Leonard 2026-11-15 定的「減維護負擔」（`## Open Priorities` 2）；第一、二步已完成（`## Validation / QC` S248、`## Last Session Record`），續做點是第三步 Freshness（Issue #77）與 51 條 `PAGE_ANCHORED` 真缺口（寫生產前先列清單給 Leonard 批准）；退役步驟的數字以當時實測為準（現為 17,079 → 17,077）。以下 S247／S246 證據仍適用。 **S247 補充**：本節是獨立小任務（本機備份清理，已完成，`## Validation / QC` S247、`## Last Session Record`），不改父目標與續做點；規則見 `dev/rules/safety.md` `## Project Rules`。以下 S246 證據仍適用。 **父目標與消費者**：Leonard 要系統各環節自行運作、少介入（S243）；Channel A 退役與 455 條清單已於 S246 完結（`## Current Baseline` 1），消費者是 Leonard 與用戶搜尋。**確切續做點**：`## Open Priorities` 開首 S246 段 —— 退役 `EDBC_9_2019_E`（S238 已批准未執行，執行前再確認），步驟寫在同節 S238 原文（備份 → DELETE → `live_display_sync(17074, 17072)` → `update_log.json`）。**已做、不要重做**：清單清空、109 行備份與刪除、PR #87 合併、舊分支刪除（`## Validation / QC` S246）。**已否決**：把 footnote 來源登記入 `source_registry.json`（按設計不登記，S246 (6)）；租金收入不以 `footnote_fn_tips_rental_40pct` 為出處（未提學校及班級津貼）。**仍待 Leonard 的產品決定**：粵語問句改寫、時限段落交退役機制、「全校」角色標籤、`FEATURE_SUBJECT_CHECK`、Kit 0.4.4 升級。**必讀來源**：`dev/source/execute_ingest.py` 的 `live_display_sync`／`live_total_count`；Risks 3（冷啟動首查詢會 `57014`，量度前先暖機）。**權限邊界**：Supabase 寫入或刪除、批量 Jev／OpenAI 呼叫、合併 PR 皆須 Leonard 明示；搜尋內容不得公開。

**🟢 S230 的分支邊界已結案（S231）**：PR #26 已由 Leonard 合併，S230 與 S231 的交接狀態都在 `main`。本節收工 PR 同樣要 Leonard 在網頁合併；**開工第一件事照舊是 `git fetch` 後確認分支與 `origin/main`**。

**🟢 S224 記的 0-byte `main` 檔已刪（S231 #28，Leonard 批准）**：`git diff main <branch>` 不再報 `ambiguous argument`。`execute_ingest.py` self-test 內的字串 `"../../main"` 不是對該檔的引用，未受影響。

**⚠️ S215 新增治理缺口（未修）**：`backend/README.md` 5 行 flag 說明永久遺失，無備份、沒有杜撰補回；補寫時須在 commit message 明寫是重寫非還原。

**⚠️ 已知治理缺口（S205 發現，S206、S207 沿用同一判斷）**：S204 closeout 冇寫 `State Reconciliation Check` 條目（本節由 S205 起補回並持續）。屬歷史記錄缺口，唔影響當前狀態可信度。

If no, update this handoff before closeout.

Continuity rule: this file carries current state and next action. `dev/SESSION_LOG.md` carries recent evidence only. Archive old detail only when needed; do not create an archive directory by default.

<!-- ack:section:next-session-opening-message -->
## Next Session Opening Message

This fenced block is the authoritative agent-managed startup content. At closeout, regenerate `START_NEXT_SESSION_PROMPT.txt` from this block. If the two differ, trust this block and rewrite the convenience copy.

📋 Next session: agent-managed startup content below



```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft. Read AGENTS.md, then dev/SESSION_HANDOFF.md. Trust the handoff over this generated mirror.

If the root does not match the handoff, stop and ask for confirmation. Do not read dev/SESSION_LOG.md during ordinary startup. Read dev/PROJECT_INDEX.md, dev/RULE_PACKS.md, dev/DOC_SYNC_REGISTRY.md, dev/CODEBASE_CONTEXT.md, dev/PROJECT_MASTER_SPEC.md, and task packs only when the current task requires them.
所有路徑含空格，終端機指令必須用雙引號包住。

一個單獨的「開工」/「Start Agent Handoff」只授權：最小狀態復原 → 起手探針 → 起手卡 →
報告當前目標／風險／建議下一步，然後結束該回合。同一則訊息若帶任務則照常開始。

--- 專案狀態（S248 收工, 2026-11-15；2026-11-16 補完）---

平台 v3.3.16；Supabase 17,079 chunks（316 來源，2026-11-15 讀 stats.json，PR #91 自動入庫 edbcm203_2026 +5；footnote_curated 177）；EDB 指引書庫 182 份；guidelines.json 公開端點 151 份（_meta 2.6.2）。
Channel A 退役已完結：內部清單 dev/knowledge/channel_a_option2_queue.json 已清空（resolved 289、dropped 166、餘 0）；
Supabase 109 條 approved_fact（role_facts_*）已備份後刪除（備份在本機 dev/init_backup/20261108_122028_UTC/）。
Agent Handoff Kit v0.4.3（npm 已有 0.4.6，未升級；doctor 報 project shortcuts 一項未通過）。
origin/main = 61ba038（PR #92、#93、#95 已合併）；線上 /health commit = 8b118fd、通函索引 70 份（2026-11-16 實測；開工以 /health 核實）。
開著的 PR：#96（S248 收工，只改治理文件，合併待 Leonard 指示）、#70（內容已入 main，關閉前先問 Leonard）。
Render：無 OPENAI_MODEL、無 JUDGE_MODEL → 碼內預設 gpt-6-luna＋reasoning.effort none。
FEATURE_ROUTE_FIRST_SEARCH=1、FEATURE_CIRCULAR_NUMBER_LOOKUP=1；FEATURE_QUERY_FUSION、FEATURE_SUBJECT_CHECK 未設＝關閉。
public.search_log 記錄真實搜尋 180 日（🔴 搜尋內容不得公開或入 git）。

🟢 S248 做完（不用重做）：
   · 交接檔瘦身 760 KB → 65 KB：歷史原文在 dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md；
     三段精簡版的詳情在 dev/SESSION_STATE_DETAIL.md（開工不讀，做到該項才讀）。PR #92 已合併。
   · QC 惡化通知：qc_report.json 新增 regressions（只列高於基準的基準檢查），qc_report.yml 以 notify_new_items.js
     開 qc-regression Issue 並 @Leonard；數字不變不重複通知。PR #93 已合併，首次真實運行開出 Issue #94，
     Leonard 確認收到 @mention 電郵（監察通知鏈至此全程驗證）。
   · PAGE_ANCHORED 定義修正（Leonard 批准）：只計 PDF 來源、頁碼標記判斷與後端 ={2,} 一致、基準 179 → 51；
     線上 17,079 片段實測 51（WARN，等於基準）。PR #95 已合併，線上 QC 運行已自動關閉 Issue #94。
🟢 S247 做完（不用重做）：
   · dev/init_backup/ 刪除 26 份舊版／重複 wiki_index.json 備份（約 11.09 GB），保留 20261101_195458_UTC；
     保留規則在 dev/rules/safety.md「Project Rules」（wiki_index 備份只留最新一份；Supabase 刪除前備份必須保留）。
🟢 S246 做完（不用重做）：
   · 租金收入以 g02《財務管理指引》第 15 頁按原文修正，清單清空。
   · 109 行 approved_fact 全欄位備份 → 經 Leonard 批准刪除 → 公開數字 17,074，線上已讀回。
   · PR #87 合併；舊分支 s244-option2-round1 已刪；edbc29_2024_teacher_training、edb_byod_page 按設計不登記 source_registry。

🚀 下一步：
   ① 退役 EDBC_9_2019_E（2 段 footnote_curated；已被 EDBC 4/2026 取代；S238 已批准未執行 —— 執行前先向 Leonard 再確認）：
      select=* 匯出備份 → DELETE → live_display_sync（以當時實測數為準，現為 17,079 → 17,077） → update_log.json。
   ② 餘下 51 條真缺口（41 條 PDF footnote 欠 #page=、10 條 gifted_policy_docs）要寫生產，先列清單給 Leonard 批准。
      其後續做減維護負擔第三步（Leonard 2026-11-15 定為優先）：先 Freshness（Issue #77，35 項，約半數是索引頁／統計頁），
      再 PHANTOM 36／UNLISTED 119。
   ③ 待決定：S244 三條 footnote 粵語問句是否改寫；語料庫時限段落是否交 check_expiry；app.html「全校」角色標籤；
      文件標註四項重開條件；搜尋紀錄加拒答原因（DDL 待批）；FEATURE_SUBJECT_CHECK；Kit 0.4.6 升級；已收起功能的公開端點去留；定期系統更新檢查約 11-29 到期。

⚠️ 量度紀律（違反任何一條都會得出錯的結論）：
   · 定標必須讀每一段全文；用 stub 判官量的是「失去捷徑」不是「失去答案」；答案層結論必須用真判官量。
   · 檢索層得益不等於答案層得益（S228、S239 兩次）；改檢索或模型都要量答案層。
   · 新規則要先凍結，再用未見過的題目驗證；比對 gold signature 一律用 squeeze(fold(s))。
   · searchChannelB 會吞掉合成失敗成空答案；量模型時要另記呼叫錯誤（_s239_modelAB.ts 已做）。
   · 推理模型的推理 token 按輸出計費；換模型時同時量開支與延遲。
   · 生產量度一律帶 x-probe；生產限速每 IP 每分鐘 10 次，批量至少間隔 7 秒；Render 剛喚醒時首查詢會 57014，先暖機。
   · 本機用 service key（8 秒）量 anon（3 秒）系統，延遲與逾時會低估。
   · 升版只手改 PLATFORM_VERSION＋README＋CHANGELOG；任何來源換版／改網址／退役後 check_downstream_sync 的 MUST_UPDATE 必須為 0。
   · 抽取與入庫一律用 /usr/local/bin/python3。

Post-startup first action: 先做起手探針（served app.html PLATFORM_VERSION 應為 3.3.16 + Render /health commit
（應為 8b118fd 或之後改 backend 的 commit；cache_b.footnote 應為 177）+ git fetch 後比對分支與 origin/main、gh pr list
+ Supabase live count 應為 17,079 + check_registry_drift --check --ledger <scratchpad> 的 ZOMBIE／SERIES_UNMONITORED／UNMANAGED 應為 0
+ dev/PROJECT_INDEX.md「定期系統更新檢查」一行日期是否已逾 30 日）。
之後報告，並按 ① 處理（先確認）。
未得明確批准，不得改任何 flag、不得執行 DDL、不得刪除或寫入生產片段、不得作外部模型批次、不得合併 PR。
```

## Session Close Checklist (每次 session 結束必須執行)
```bash
# 1. 更新 SESSION_LOG.md + SESSION_HANDOFF.md（Claude 負責）
# 2. Git commit + push（Leonard S115 授權「push 係你做」— Claude 執行；加指定檔，勿 -A）
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
git add <指定治理/文檔檔> && git commit -m "session close: <描述>" && git push origin main
# （MemPalace sync 已於 S115 移除 — 本專案不再使用 MemPalace）
```

## Supabase Technical Notes (Channel B)
- Project: `edb-knowledge` at `https://youkcekbrbywuqjxgibe.supabase.co`
- Table: `public.wiki_chunks` — vector(1536), IVFFlat index **lists=60** (per `backend/supabase/schema.sql`, the authoritative DDL — S115 §0b corrected: prior "lists=50" + "2,822 rows" were drift; local wiki_index build artifact = 12,906 chunks / 120 src; live Supabase row-count + index not introspected this session)
- Function: `match_wiki_chunks(query_embedding text, match_threshold double precision DEFAULT 0.1, match_count integer DEFAULT NULL)` — **this (text) is the LIVE signature the backend uses (sends embedding as string); schema.sql had drifted to `vector(1536)` and applying it created a 2nd overload → PGRST203 → Channel B 0 (S116 live incident). Always INSPECT live `pg_get_functiondef` before any RPC DDL — see PROJECT_MASTER_SPEC §E.13.**
  - Uses `query_embedding::vector` cast internally; ordered by cosine DESC; null match_count = return all above threshold
  - **S116: now `language plpgsql VOLATILE` with body `set local ivfflat.probes = 8`** (was `language sql stable`, probes=1 default). Mechanism constraints (all empirically hit): function-level `SET ivfflat.probes` clause → 42501 (Supabase blocks ext-GUC clause); `SET`/`SET LOCAL` in STABLE/IMMUTABLE or `language sql` → 0A000 (must be VOLATILE plpgsql). probes=8≈sqrt(lists=60). Production Channel B currently runs probes=8 (Stage-1 FULL PASS, S116). Reference: auto-memory reference_supabase_pgvector_probes.
  - DDL needs Supabase Dashboard SQL Editor (Leonard's auth); no CLI/psql/DB-url/service-via-PostgREST path. Claude prepares exact APPLY+ROLLBACK+read-only INSPECT; Leonard applies.
  - ✅ **S117 FIXED** (was S116 promote-blocker): `searchCombined.ts` `.catch` now returns `failedChannelBResponse` → combined surfaces `channel_b_status:"error"` + `CHANNEL_B_ERROR_REASON`, distinct from genuine unconfigured (`channel_b_status:"unconfigured"` + 未配置). Real Channel B failures now visible to monitoring/eval via the `channel_b_status` discriminator (no more fake "未配置" masking). Genuine-unconfigured path (`searchChannelB.ts` `isSupabaseConfigured()` guard) unchanged. Dedicated `/api/search/channel-b` still recommended for live-grade (no route-level catch — methodology unchanged). Deploy: Render auto-deploys on push to main.
  - 🔴 **S118: free-tier probes=8 intermittent statement-timeout** — live-verify saw 2/5 RPC calls return HTTP 400 / Supabase `57014` "canceling statement due to statement timeout" at probes=8 (succeeded on retry; one was cold-start, one intermittent ~60s after a healthy call). Production-availability risk independent of retrieval correctness; post-S117 it correctly surfaces as `channel_b_status:"error"` (not fake "未配置"). Open Priority — options: lower probes / app-level retry / paid tier. probes=8-live itself still NOT independently introspected (audit-flagged; read-only `pg_get_functiondef`/`proconfig` SQL prepared, not yet run).
  - **S118: Channel B routing +4 dedicated selective routes** (`searchChannelB.ts` `TOPIC_KEYWORDS`/`SOURCE_SETS`/`QUERY_EXPANSIONS`, first-match before `finance`): cpd, kg_admission, conduct, steam (PLAN-1b promote; fixed cutoff unchanged; SAG in cpd/conduct bounded by per-source quota cap=3 → §E.3-safe). Stage-2 adaptive combo abandoned (non-viable; do not revive).
- **S221 `match_wiki_chunks_routed` 計劃修正（DDL 已由 Leonard 套用，2026-09-12）**：原函式開頭同時 `set local enable_indexscan = off` 與 `set local enable_bitmapscan = off`，令 S219 加的 `wiki_chunks_source_id_idx`（btree）完全用不到，planner 對 cpd 的計劃先為 17,610 列算餘弦距離才篩 `source_id`（135,502 buffer hits）。**已刪 `enable_bitmapscan` 那一行**；`enable_indexscan = off` 保留，因為它才是封住 ivfflat、保住 exact 語義的那一句（ivfflat 是 ordering-only，bitmap 形態下用不著）。實測改後走 `Bitmap Index Scan on wiki_chunks_source_id_idx`，939 列／17,433 hits。**ROLLBACK = 把 `set local enable_bitmapscan = off;` 加回原位並重新 `create or replace`（同簽章＝替換，不會產生第二個 overload）。** 正確性證據見 `dev/source/eval_runs/2026-09-12_s221_routed_before.json` 與 `_after.json`，比對工具 `backend/scripts/_s221_routedBaseline.ts --compare`。
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
