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

1. **【S246，2026-11-08】Option 2 清單清空（`resolved` 289、`dropped` 166、餘 0）：最後一條「租金收入」以 g02《財務管理指引》原 PDF 第 15 頁（印刷頁 14，引教育局通告第5/2011號）按原文寫 `fact_corrected`。Supabase 109 行 `approved_fact`（`role_facts_*`）已按規則第 5 條全欄位備份（`dev/init_backup/20261108_122028_UTC/`，本機、gitignored）後經 Leonard 批准刪除。Channel A 退役工作至此完結。** 以下為 S245 原文。 **【S245，2026-11-05】Option 2 第二輪完成：清單由 39 條減至 1 條（`resolved` 288，其中 23 條按原文修正、1 條經新 footnote；`dropped` 166，含時限資料 8、找不到出處 5、問卷題 1）。餘下 1 條：設有法團校董會資助學校的租金收入（《財務管理指引》g02 表格抽取後兩欄交錯，待 Leonard 定出處）。** 以下為 S244 原文。 **【S244，2026-11-05】Option 2 第一輪完成：清單 `dev/knowledge/channel_a_option2_queue.json` 由 455 條減至 39 條（`resolved` 264，其中 87 條帶 `fact_corrected`＝按原文修正的措辭；`dropped` 152，含角色職責類 71、時限資料已過時 27）；清單 `_meta.rules` 增補第 2 條（`same_matter`）、第 6–8 條（S244）。平台版本不變 v3.3.16。** 以下為 S243 原文。 **【S243，2026-11-03】平台 v3.3.16；Channel A（455 條）退役：`knowledge.json`／`role_facts.json` 已刪，原文移至內部清單 `dev/knowledge/channel_a_option2_queue.json`（不公開、不供搜尋，`_meta.rules` 定處理規則）；公開統計改由 `stats.json` 提供；凍結合約只餘 `guidelines.json` 2.6.2／151。公開分頁只餘平台介紹／政策搜尋／EDB指引：文件標註收起待修（`FEATURE_TABS.annotate=false`），範本下載、`q.html`、`t-purchase.html`、手機版選擇角色已刪。** 以下為舊紀錄。 平台 **v3.3.10**（S233 bump：新增搜尋記錄與回答評分 👍／👎，介面只多了評分按鈕）。**`search_log`（S233）已上線並經生產實測**：每次真實搜尋留底 180 日（查詢、路由、拒答、回答全文、結果窗連片段全文、耗時、評分），帶 `x-probe` 不記；讀取只經 service_role。設計與定案見 `dev/SEARCH_LOG_DESIGN.md`。**`guidelines.json` 凍結合約 2.6.2**；`knowledge.json` `_meta` 仍 **2.3.0** · facts **455**。⚠️ 升版一律手改 `PLATFORM_VERSION`＋README 標章＋CHANGELOG，**不可用 `bump_version.py`** —— S231 試跑 `--dry-run` 證實它會把 `knowledge.json`／`role_facts.json`／`guidelines.json` 三個凍結合約一併改寫。
2. 【S246，2026-11-08】Supabase **17,074** chunks、**315** 來源（−109 `role_facts_*`；`live_total_count`／`live_sources_count` 實測；公開數字已同步；footnote_curated 177 不變）。以下為 S245 原文。 【S245，2026-11-05】Supabase **17,183** chunks、**315** 來源（`live_total_count`／`live_sources_count` 實測；公開數字已同步。來源數多 2：S244 新 source_id `edbc29_2024_teacher_training` 當時未同步，加本節 `edb_byod_page`）：+1 `footnote_curated` `footnote_fn_byod_edb_support`（176 → 177，線上 `/health` `cache_b.footnote` 177，毋須重啟）。以下為 S244 原文。 【S244，2026-11-05】Supabase **17,182** chunks、**313** 來源（`count=exact` 實測）：+3 `footnote_curated`（`footnote_fn_ceg_recurrent_august`、`footnote_fn_leave_nonteaching_annual`、`footnote_fn_cpd_eservices_record`；footnote_curated 173 → 176），Leonard「全部批准」＋「入庫 3條，再commit 入 supabase」；線上 `/health` `cache_b.footnote` 已報 **176**（已載入）。公開數字已 display-sync 至 17,182。 【S243，2026-11-03】Supabase **17,179** chunks、**313** 來源（入庫 `moi_3rd_cycle_policy_2021` +9，`live_total_count` 實測；EDB 指引書庫 182）；109 條 `approved_fact`（`role_facts_*`）仍在庫但 `retiredMirrorFilter` 全數停服。 【S242，2026-11-01 寫入，11-02 合併部署】Supabase **17,170** chunks、**312** 來源（`count=exact` 實測）：封面核對 Issue #72 三份 —— `edbcm141_2025_blnst` 退役（404，由 `edbcm170_2026_blnst` ＋ `blnst_faq_2026` 取代，−5 +17）、`sdp_guide` 換 2026-09 資助學校版並新增 `sdp_guide_dss`（5→5 +5）、`iit_ai_framework_2026` 換 10-14 新檔（18→18，改稱「人工智能部分」）；舊資料連向量備份於 `dev/init_backup/20261101_195421_UTC/`（gitignored）；公開數字、EDB 指引書庫 181 份、更新日誌、清單 27 條條文與封面基線皆已同步。 【S241，2026-10-30】Supabase **17,101** chunks、**306** 來源（IIT 框架與單張 +64、EDBC017 +14、EDBCM186／197／198 +33；`live_total_count` 實測，公開顯示已同步）。以下為舊紀錄。Supabase **16,990** chunks（S238 `count=exact` 實測，2026-10-13：三份新版重新入庫 −2、K1／資優資源冊／自評工具以新版取代 −18、退役 `EDBC_8_2020_E` 與 `edbcm099_2026` −11；公開顯示已同步）。再之前 **17,021**（S235 `count=exact` 實測，2026-10-06；+14 是 Option A 自動入庫 `edbcm134_2026` 推廣閱讀津貼 +12、`edbcm142_2026` 幼稚園推廣閱讀津貼 +2，均經 Leonard 在 ops Issue 剔選批准）。之前 **17,007**（S232；+1 是 S232 經 Leonard 批准寫入的 curated footnote `footnote_fn_kg_teacher_pupil_ratio`，footnote_curated 180 → 181）。更早：+2 為 Option A 自動入庫 PR #27 `edbcm155_2026`；再早 S223 兩次生產寫入：SAG 換版合併 −792 ＋387，`kgecg_2017` 去重 −108）。in-app 瀏覽庫 **170** 份（退役 `g24`）；`guidelines.json` 公開端點 **151** 份（由 158 對正 in-app 標籤，移除 7 條、同步 32 個欄位）。兩者仍刻意不同。
3. 🟢 **【S241】10-28 機械人漂移帳：`ZOMBIE`／`UNMANAGED`／`SERIES_UNMONITORED` 皆 0，`PHANTOM` 36，`UNLISTED` 117（由 115 升 2，屬人手策展佇列）。** 以下為 S228 原文。 🟢 **`ZOMBIE` 與 `UNMANAGED` 皆為 0**（S228 開工 `check_registry_drift --check` 實測；`SERIES_UNMONITORED` 亦為 0）。`UNMANAGED` 那 1 個／2 片段（`stat_integrated` id 錯配）已由 S226 那兩行生產 `UPDATE` 修好，本行原文一直未同步，S228 更正。餘下 `PHANTOM` 36 · `UNLISTED` 115／2,616 片段。
4. **【S247，2026-11-09】PR #89（init_backup 清理紀錄＋備份保留規則）已於 CI 綠後按 Leonard 指示 squash 合併為 `82be06e`＝`origin/main`；PR #88（S246 收工）早前已合併為 `5244c02`；線上 `/health` commit 仍 `20fd4a4`。本節收工在分支 `s247-closeout`。#70 仍開著。** 以下為 S246 原文。 **【S246，2026-11-08】PR #87（S245 工作＋收工＋S246 清單清空）已於 CI 綠後按 Leonard 指示 squash 合併為 `62647fe`；`origin/main` = `d6b18f6`（其後 QC 機械人 commit）；線上 `/health` commit 仍 `20fd4a4`。舊分支 `s244-option2-round1` 已刪（遠端與本機；內容已入 `main`）。本節收工在分支 `s246-closeout`。#70 仍開著。** 以下為 S245 原文。 **【S245，2026-11-05】PR #86（S244）已 squash 合併為 `12c1ab7`；`origin/main` = `27a59d5`；線上 `/health` commit 仍 `20fd4a4`。本節工作與收工在新分支 `s245-option2-round2`（由 main 開出），PR #87 已開、未合併（不改 `backend/`）。舊分支 `s244-option2-round1` 上多了一個重複 commit `d2c95ee`（本節誤推，已無 PR，內容同 PR #87），可刪可留。** 以下為 S244 原文。 **【S244，2026-11-05】`origin/main` = `ab2aee9`（S243 收工 PR #85 已合併，其後兩個 QC 機械人 commit）；線上 `/health` commit 仍 `20fd4a4`。本節工作與收工同在分支 `s244-option2-round1`，PR #86 已開、未合併（不改 `backend/`，合併後不會重新部署）。#70 仍開著。** 以下為 S243 原文。 **【S243，2026-11-03】Leonard 每次指示「CI 綠後合併」：#79（入庫）、#80（Channel A 退役，改 `backend/`）、#81–#84（只改前端與文件）皆 squash 合併；`origin/main` = `37451db`，Render `/health` commit = `20fd4a4`（#80，之後不改 `backend/`）。收工 PR 由 `s243/closeout-final` 開出。#70 仍開著（內容早已入 `main`），關閉前先問 Leonard。** 以下為 S242 原文。 **【S242，2026-11-02】Leonard 三次指示「CI 綠後合併」：#73（`aeb6cb7`，含 #70 內容）、#74（`3ef9ab6`，`blnst` 路由）、#75（`f7b988c`，只改 `qc_report.yml`）皆已 squash 合併；`origin/main` = `814bd0c`（其後機械人 QC commit），Render `/health` commit = `3ef9ab6`（#75 與機械人 commit 不改 `backend/`，不觸發部署）。#70 內容已入 `main`，PR 仍開著，關閉前先問 Leonard。** 以下為 S241 原文。 **【S241，2026-10-29】PR #53 由 Leonard 指示 squash 合併：`origin/main` = `da44e55`，Render 已部署，`/health` commit `da44e55`。** 合併前 `origin/main` 為 `e4fc88f`（`77de1dd` 之後 7 個機械人 commit：QC 報告重產與 discovery ledger，不改 `backend/`）。本收工 PR（`s241/model-migration-circular`）**改 `backend/src`**（通函編號查找，旗標預設關），所以合併後 Render 會重新部署，行為不變直至開旗標。#45、#47 仍開著（關閉前先問 Leonard）。以下為 S240 原文。 **【S240，2026-10-23】PR #55（npm 依賴漏洞修補，只改 `backend/package-lock.json` 與 `dev/checklists/_work` 的 nanoid）由 Leonard 指示 squash 合併：`origin/main` = `77de1dd`，Render 已重新部署，線上執行碼 = `77de1dd`**（11:40 `/health` 實測：Channel A 455、`cache_b` footnote **173**／spotlight **303**，S237 記為 181／306，差額未逐條核對，較可能來自 S238 退役與換版）。#55 不改 `backend/src`，所以線上行為與 `a344504` 相同。**PR #53 仍未合併**（MERGEABLE／CLEAN，未 rebase 到 `77de1dd`，兩者不改同一檔）；S240 收工 commit 推上 `s239/query-fusion`，即 S239 與 S240 的交接要等 #53 合併才入 `main`。以下為 S239 原文。 **【S239 收工，2026-10-21】`origin/main` = `c4b3a6a`（S238 後只有監察機械人 commit），線上執行碼仍 `a344504`。PR #53（`s239/query-fusion`，build-gate 綠、可合併）未合併**：含狀態頁按知識庫改動重產、`FEATURE_QUERY_FUSION`（預設關）、**合成與判官碼內預設改 `gpt-6-luna`＋`reasoning.effort none`**、本節收工文件。合併後判官即時轉 `gpt-6-luna`（Render 無 `JUDGE_MODEL`），合成仍是 Render 設定的 `gpt-4o-mini`，直至 Leonard 刪除或改 `OPENAI_MODEL`。#45、#47 仍開著（內容已併入 #48，關閉前先問 Leonard）。以下為 S238 原文。 **【S238 第二次收工，2026-10-13】`main` = `a67bd29`**：#48（`e3d130d`）、#49（`513208b`）、#50（`a67bd29`）皆由 Leonard 指示 squash 合併，CI 全過；三個 PR 都不改 `backend/`，**線上執行碼仍為 `a344504`**。本收工 PR（`s238/closeout-2`）只改治理文件。以下為第一次收工原文。 **【S238，2026-10-13】PR #48 由 Leonard 指示合併**：含監察通知修正、來源更新（Supabase 已寫入）、S236／S237 兩個未合併收工 PR（#45、#47）的內容與本節收工文件；**不改 `backend/`，合併後不會重新部署，線上仍為 `a344504`**。合併前 `origin/main` = `7b6a68b`（`a344504` 之後只有監察 bot commit）。#45、#47 內容已併入 #48，可關閉（關閉前先問 Leonard）。合併後的 `main` hash 下節以 `git fetch` 核實。以下為 S237 原文。 **【S237 實測，2026-10-11】`origin/main` = `a344504`（PR #46 合成模型碼內預設改為 `gpt-4o-mini`；其前 #44 `f9da565` 路線乙 v1＋Kit v0.4.3），線上執行碼亦為 `a344504`**（合併後約 60 秒 `/health` 實測，`cache_b` 181／306）。S236 收工 PR #45 一直未合併，其內容已併入本節收工分支 `s237/closeout`，#45 可關閉（關閉要 Leonard 同意）。入庫 commit 會改 `searchChannelB.ts` 的 `SOURCE_SETS`，所以入庫 PR 合併後 Render 會重新部署，**新來源要等新版上線才搜得到**。`cache_b.footnote` **181**、`spotlight` **306**。本節收工 PR（`s237/closeout`）不改 `backend/`，合併後不會重新部署。**S236 起 AI 執行 `gh pr merge --squash` 成功**（#43、#44、#46 皆在 Leonard 明示「合併」後由 AI 合併，未被分類器擋）；合併仍只在 Leonard 明示指示時進行。🔴 `main` 仍受 ruleset 保護（`main build gate`），一切改動走 PR。**判斷線上是否落後看 `git diff --name-only <部署commit>..origin/main -- backend`，不要比 hash。** ⚠️ **footnote 入庫後生產要進程重啟才載入**（`_footnoteCache` 無 TTL）：S232 做法是入庫後 21 分鐘不發任何請求，令 Render 免費方案休眠，下一次請求喚醒時即重新載入，並以 `/health` 的 `cache_b.footnote` 數目核實。
5. **【S241】OpenAI 模型遷移已完成，使用中型號全部遷離 2027-01-14 停用名單。** Render 已由 Leonard 刪除 `OPENAI_MODEL`（18:53 UTC 重啟），合成與相關性判官皆 `gpt-6-luna`＋`none`（碼內預設）；四條帶 `x-probe` 線上答案 82–174 字（舊模型 277–324 字），零空答案。離線：`dev/ocr_extract.py` 預設 `gpt-6-luna`＋`none`；量度判官 `_s227_rubricJudge.ts` 預設 `gpt-6-luna`＋`low`，**不再讀 `JUDGE_MODEL`**。**`FEATURE_CIRCULAR_NUMBER_LOOKUP`（S241）：生產已開（2026-10-30 Leonard 在 Render 設 `=1`，#58 `f7ac967` 部署後 `/health` `cache_b.circular` 報 `enabled:true`、`index:64`）**。以下為 S239 原文。 **【S239】模型與新旗標**：OpenAI 2027-01-14 停用 `gpt-4o`／`gpt-4o-mini`／`gpt-4.1`／`gpt-4.1-mini`（官方頁核實）。PR #53 把碼內預設改為 `gpt-6-luna`＋effort `none`（只在模型用碼內預設時才自動帶 effort；新環境變數 `OPENAI_REASONING_EFFORT`／`JUDGE_REASONING_EFFORT`）。`FEATURE_QUERY_FUSION`（S239）答案層判定不出貨，**不應在 Render 啟用**。事實與量度見 `dev/CODEBASE_CONTEXT.md` OpenAI 段。以下為 S238 原文。 🟢 **`FEATURE_ROUTE_FIRST_SEARCH` 仍在生產啟用**（Render 環境變數，2026-09-09 起）。另兩個合成側 flag 仍 `0`。**S236 新增 `FEATURE_SUBJECT_CHECK`（路線乙 v1）：已部署、生產未設＝關閉，合併後以 D01 行為實測確認；開啟待 Leonard 決定。****`/health` 不報 flag，只有 Render dashboard 看得到** —— 但 **S226 起有了行為探針**：185 題生產 run 與本機旗標開啟側 **184/184 逐條同判**（含兩側判法相反的那 7 題，生產全部站在開啟側），與關閉側則有 7 題不同。**即這個 flag 的生產狀態現時可以由行為核實，不必靠 dashboard 記憶。**工具：`_s213_run_gold.py`（生產端點）對 `routeFirstGold.ts`（本機兩側）。另兩個合成側 flag 仍無同類探針。**S226 新增三個量度 knob，生產一律未設**：`MAX_PER_SOURCE`（未設＝現行公式）、`FEATURE_LEXICAL_RERANK` ＋ `LEXICAL_RERANK_WEIGHT`（未設＝關閉，預設權重 0.05）、`FAMILY_QUOTA`（未設＝關閉）。**三者都不應在 Render 啟用**：前者實測一換一、後者實測不成立、重排經 S227 判官實測答案層 net −1，判定不出貨。 **S228 再新增三個，生產同樣未設**：`EXPANSION_MIN_QUERY_CHARS`（未設＝照舊原文照貼展開詞）、`EXPANSION_BALANCE`（未設＝用戶查詢只出現一次）、`EXPANSION_REPEAT_CAP`（未設＝8）。**這三個與前三個不同：檢索兩層都實測有得益且零退步**（`floor=8`＋`balance=.5`：片段層 +7、來源層 +3，而七次重跑的片段層噪音是 0）。出貨與否見 `## Open Priorities` ①。**三個都是 Render 環境變數，改完重啟即生效，回退不需要重新部署。**
6. **【S238】偵測型監察改為「有新項目才 @Leonard 留言」**（`.github/scripts/notify_new_items.js`，接入 freshness／served-URL／cover-title／discovery，pgvector 內文加 @mention）。根因：Leonard 沒有 Watch repo，而監察只修改舊 Issue 內文，GitHub 不就修改發通知；Freshness Issue #1 由 2026-06-08 起四個月零通知。Leonard 已在帳戶設定勾選 @mention 電郵。已退役的通告監察留下的 Issue #3 已關閉。 **監察現有八個 workflow ＋ 一個每日看門狗，S234 再加 `live_probe.yml`（每 6 小時探測線上服務，見 `## Validation / QC` S234；已登記入看門狗，受其監察的排程由 6 個變 7 個）**（`backend_build_check.yml` push 觸發、無 schedule，故不計入看門狗的 cadence 契約 —— `check_monitor_health --self-test` 實測仍報「覆蓋所有排程 workflow（6 個）」ALL PASS）。**S224：四條會 commit ledger 的監察（`discover_check`／`freshness_check`／`pgvector_check`／`qc_report`）改為經 write deploy key 以 SSH 推**，因為 required check 會擋死一切直接 push，而個人帳戶 repo **不能**豁免內建 GitHub Actions。
7. **【S233 生產重跑，2026-09-28 —— 現行基線】** 185 題 gold 打生產（17,007 片段、`x-probe`、零 LLM）：來源層 **PASS 123／FAIL 39／RECORD_ONLY 19／errors 4**（四條皆 Supabase `57014` 逾時，單獨重跑全部取得結果、判定與 S226 相同；併入後 **PASS 125／FAIL 41／errors 0**）；片段層 **chunk_PASS 57／FAIL 105**（併入後 **59／107**，與 S228 本機七次重跑的 59 一致）。併入後指標：Source Recall **@1 0.446／@3 0.639／@5 0.711／@8 0.753**、Chunk Recall **@1 0.199／@3 0.307／@5 0.349**、MRR source **0.552**／chunk **0.254**；禁引違規 8 條（不變）。檔案：`dev/source/eval_runs/2026-09-28_s233_prod_gold.json`（原始 run，`EVAL_LATEST` 自動採用）。逐條拆解見 `## Validation / QC` S233。以下為 S226 舊基線，保留作對照。 **檢索準確度基線（S226 實測，2026-09-15）** —— 此項本來不存在，所以這些數字過去散落在 Risks 與 Open Priorities 裡各自變陳舊。**生產**（185 題 gold 打 `https://edb-knowledge.onrender.com/api/search/channel-b`）：來源層 **PASS 121／FAIL 44／RECORD_ONLY 19**、**errors 1**（`sen_iep_intellectual`，Supabase `57014` statement timeout）；片段層 **chunk_PASS 58／chunk_FAIL 107**（166 題有段落簽名，recall@8 **0.349**）。**本機 in-process 旗標開啟側**：PASS 122／FAIL 44、errors 0、chunk 58／108。**旗標關閉側**：PASS 119／FAIL 47、chunk 54／112。**兩層都要看**：來源層答「有沒有拿對文件」，片段層答「有沒有拿到答得到的那一段」——現時 **64 題是拿對文件、拿錯段落**，所以只看來源層會高估三分之二。檔案：`dev/source/eval_runs/2026-09-15_s226_prod_gold.json`（生產）、`..._s226_route_first_{before,after}.json`（本機兩側）、`..._s226_route_first_before_after.jsonl`（原始擷取，含逐個 RPC 的狀態與毫秒）。**完整指標（生產，`_s213_eval_metrics.py`，S226 首次跑得動）**：Source Recall **@1 0.442／@3 0.618／@5 0.691／@8 0.733**、Chunk Recall **@1 0.200／@3 0.309／@5 0.345**、MRR source **0.540**／chunk **0.255**；佔位——單一來源最多佔 **5/8** 格、**15** 條查詢有一個來源佔半數以上、逐字重複格位 0；無答案題——`WEAK_ANSWER` 18、**`CONFIDENT_WRONG` 1**；**禁引違規 8 條查詢**；最弱範疇 @1——gifted **0.111**、curriculum **0.125**、digital_education 0.200、cpd 與 school_bus 各 0.222。（S213 舊值 R@1 0.364／Chunk R@5 0.273 是 **162 題**的 gold 數，題集與語料都已改，**不可直接比**。） **【S228 補一個本機基線與一個噪音底線】** 本節在 S227 的 `staff_appraisal` 修正 ＋ 本節 OP⑩ 路由修正之上，同一配置連跑七次本機 in-process（生產配置 `FEATURE_ROUTE_FIRST_SEARCH=1`）：來源層 `PASS` **123** 六次、122 一次；片段層 `chunk_PASS` **七次全部 59**。**即片段層的重跑噪音是 0、來源層是 ±1** —— 以後任何「改善 1 條」的來源層結論都在噪音之內，不可單憑一次跑下判斷。（此本機數與 Current Baseline 上半的生產數不可直接比：本機用 service key 的 8 秒上限量一個 anon 3 秒的系統，見 Risks 2。）

<!-- ack:section:validation-qc -->
**S247（2026-11-09）—— 清理 `dev/init_backup/` 舊版 `wiki_index.json` 備份。** 只動本機 gitignored 檔案與兩份治理文件；零生產寫入、零 `backend/`、零部署。(1) 起手探針：served `PLATFORM_VERSION='3.3.16'`；`/health` `ok`、commit `20fd4a4`、`footnote` 177、`circular` enabled／index 69。(2) 27 個時間戳資料夾逐一核實只含一個 `wiki_index.json`；24 份為 5–6 月舊版（420,356,599／424,482,856／424,450,497／424,846,760 bytes），3 份為 476,940,257 bytes，SHA-256 皆與現用 `dev/knowledge/wiki_index.json` 相同（`ab8d1c40…`）。(3) 全項目搜尋資料夾名稱：只有 `dev/CODEBASE_CONTEXT.md` 維護紀錄與 `dev/archive/SESSION_LOG_2026_Q2.md` 歷史紀錄提及；`dev/vault/` 的命中全指向其他資料夾；無腳本或待辦引用。(4) Leonard 批准後刪除 26 份（保留 `20261101_195458_UTC`，刪後再核 SHA-256 相同），實際釋放 10,826,816 KiB（約 11.09 GB）；`dev/init_backup/` 剩 44 個資料夾約 476 MB。(5) `dev/rules/safety.md` 在官方內文之後加 `## Project Rules`（wiki_index 備份只留最新一份；Supabase 刪除／改寫前備份必須保留）；官方內文前綴 SHA-256 前後相同（`5a1598ae…`）。(6) PR #89 CI 通過後合併為 `82be06e`。

## Validation / QC

**S246（2026-11-08）—— Option 2 清單清空；刪除 109 條 `approved_fact` 副本。** 生產寫入：Supabase −109（只刪 `source_id like role_facts_*` 且 `content_type=approved_fact`）；零 DDL、零 flag、零 `backend/` 改動、零部署。(1) **租金收入定出處**：讀 g02 原 PDF（17 頁）第 15 頁，按 PyMuPDF 版面座標還原表格兩欄（庫內 chunk `vault_g02_b233f0a42484ec31` 的兩欄交錯是抽取問題，原文本身完整）；要點欄原句「一切租金收入，應首先撥入堂費／普通經費／資本儲備帳，並從該等帳項支付有關的費用，然後將餘額的40%撥入學校及班級津貼帳內。」＋備註「適用於設有法團校董會的資助學校。」寫入 `fact_corrected`；備註第二句（「擴大的營辦開支整筆津貼帳」）原文措辭不通順，按第 7 條不改寫亦不收入。候選（乙）`footnote_fn_tips_rental_40pct` 未提「學校及班級津貼」，不取。清單寫入時核對序列化格式不變，`git diff` 只三處。(2) **備份**：`select=*` 分頁匯出，109 行、`id` 唯一、含 embedding 109、`count=exact` 109；sha256 `c6b60572…7275fab4e9`，2,151,372 bytes。(3) **刪除**：REST DELETE `return=representation` 回 109 行，刪除 `id` 集合與備份完全相同；之後 `live_total_count` 17,074、`live_sources_count` 315（本來已扣 `role_facts_*`）。(4) **display-sync**：`live_display_sync(17183, 17074)` 改 `stats.json` 1、`app.html` 3、`index.html` 3、`README.md` 4；合併後線上 `stats.json`／`app.html`／`index.html` 讀回 17,074。(5) **線上搜尋**：Render 剛喚醒時首兩次查詢 `57014` 逾時（含通函索引載入失敗），隨後三次 4.3s → 1.9s → 1.1s 正常、通函索引 69 份 —— 屬 Risks 3 的冷熱落差，與刪除無關。(6) **來源登記更正**：`check_registry_drift.py --check` 實測 `UNMANAGED` 0／`ZOMBIE` 0／`SERIES_UNMONITORED` 0／`PHANTOM` 36／`UNLISTED` 118；`footnote_curated` 屬 `BY_DESIGN_KINDS`（`check_registry_drift.py:52-57`），按設計不登記 —— S244／S245 交接「新 footnote source_id 會列 UNMANAGED」的說法錯誤，`edbc29_2024_teacher_training`、`edb_byod_page` 不登記（與 `subvention_tips` 等既有 footnote 來源一致）。(7) **分支清理**：`d2c95ee` 與已合併的 `17903a3` patch 逐字相同，`s244-option2-round1` 遠端與本機已刪。

<!-- 歷史原文（S248 瘦身，2026-11-15）：`## Validation / QC` S245 及以前各節 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔A〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- ack:section:risks-blockers -->
## Risks / Blockers

1. 🔴 **【S236 更新】「對象錯置」是會重複出現的一類，生產判官已知漏判 5 條；v1 對象核對已部署（`f9da565`）但旗標 `FEATURE_SUBJECT_CHECK` 未開，生產行為未變（v1 開啟後可攔其中 3 條）。** S236 合併後線上實測：D01 回答先承認未列明學生規定，再借用教職員「超過兩天須出示醫生證明書」推論學生「可能亦需」。 定義：窗內有**別類人**的同類規則，判官放行，合成器把它套到問題所問的人身上（D01 生產實測首句即寫「學生請病假需要提交有效的醫生證明書」）。已知漏判：D01、SX01（家長侍產假）、SX03（實習教師病假）、HX07（家長校董任期）、HX09（學生每年病假日數）；內容缺口題判官則全部正確拒答。**FT06 不屬這一類**（S235 證實窗內有答案，已改標）；GN10 屬範圍錯置，已由 S232 footnote 個案遮蓋，不能再當未修樣本。**v1 未攔到的兩條**是「對象詞在窗內以別的語境出現」，字串比對做不到，S235 已否決以加詞表擴大的做法（v2）。**換判官模型與改提示都已證修不了**（S202、S211、S230）。⚠️ **啟用 `FEATURE_VAULT_GATE_RAWVEC` 會令判官多承重 52 條查詢** —— 旗標仍不應啟用。設計、數字與限制唯一定義處：`dev/source/SUBJECT_CHECK_DESIGN.md`。

1. 🔴 **【S221 改寫；S220 原文的定性只對一半】HNSW 的封鎖項不是 CVE，是兩個無法繞過的 vacuum 修正。** 版本閘已跑（S221 實測）：Supabase 提供的 `vector` 版本清單最高只到 **0.8.0**，而 0.8.0 正是已安裝那個（`installed: true`），故 `alter extension vector update;` 無任何可升目標。三個相關修正全部在我們之上 —— **0.8.2**：Fixed buffer overflow with parallel HNSW index build（＝CVE-2026-3172，CVSS 8.1），**這一項有官方緩解**，建索引前 `set max_parallel_maintenance_workers = 0;` 即避開觸發條件；**0.8.3**：Fixed possible index corruption with HNSW vacuuming；**0.8.4**：Fixed `hnsw graph not repaired` error with HNSW vacuuming ＋ vacuuming 期間 insert 出錯。**後兩項關不掉**（autovacuum 必然會跑），且是索引建成之後長期存在的風險，不是建索引那一刻的風險。**結論：在升級之前不得建 HNSW；但不要再以為「繞過 parallel 就可以做」。** **【S222 修正 S221 的下半截】升級現時亦解不到** —— Supabase 的建置最高只打包到 **0.8.2**，即使升到頂，0.8.3／0.8.4 那兩個修正仍然拿不到。解封的先決條件已由「Leonard 決定升不升」改為「上游打包 ≥0.8.4」，現由 `dev/source/check_pgvector_release.py` 每週監察，出現才出聲；**在它響之前這一項無事可做**，詳見 Open Priorities ⑤。⚠️ S228 更正：原文指向 ①，而 ① 已於 S227 完成並移除。（附帶事實：2026-08-05 起 Supabase 已棄用「建立／更新擴充時指定版本號」—— 版本子句會被忽略並只發 warning，一律安裝該映像的 default 版本。）現行 IVFFlat 完全碰不到上述三類問題。來源：pgvector CHANGELOG 0.8.2／0.8.3／0.8.4、NVD CVE-2026-3172、Supabase Extensions 與 Upgrading 文件、`supabase/postgres` `nix/ext/versions.json`＋PR #2158、PostgreSQL Routine Vacuuming（wraparound autovacuum 即使 `autovacuum_enabled = false` 仍會跑）—— S221 逐項核實，S222 補上打包上限一項。
2. ⚠️ **量度紀律三條 —— 違反其中任何一條都會得出錯的結論。** (a) **本機比 Render 慢約 1.5–2 秒**（生產端到端做更多事只需 3.07–3.96s，本機一支裸 RPC 已 3.31–3.88s）—— 本機數字只可用來排序，絕對值不可搬去生產。 (b) **`anon` 角色 `statement_timeout` 只有 3 秒**（`authenticated`／`service_role` 8s），而後端用 anon key；本專案 in-process 慣例 `SUPABASE_ANON_KEY ||= SUPABASE_SERVICE_KEY`（`routeFirstProbe.ts:8`）會在 8 秒上限下量一個 3 秒的系統，系統性低估失敗率。**任何本機量度之前先問：我用的是哪個 key。** (c) **【S226 重量，此項已結案，但結論要連同新數字一起讀】** 舊記載的 routed p90 **8,335ms** 與 S220 的失敗率確實已過時；S226 重跑 185 題實測：routed p90 **2,498ms**、route failures **0**、超過 8 秒的 RPC **0**（S220 分別是 8,335ms／9／18）。**但 (a) 與 (b) 兩條紀律照舊生效**：這批數字仍然是本機、仍然用 service key 的 8 秒上限量一個 anon 3 秒的系統，而同日的生產 run 出了 **1** 條 `57014` statement timeout（本機 0 條）—— **低估的方向與幅度都已量到，不要把本機的「零失敗」搬去生產。** **S222 補一條同族教訓**：比較兩份文件時**必須用同一個抽取器並設對照組**（自己對自己 = 0 miss）—— 跨抽取器比對會因閱讀次序差異產生大量假差異，本節就先量出過一個 20.8% 的假數。 **S223 再補一條同族教訓**：比較**兩批已入庫片段**比跨抽取器更危險 —— 那等於同時比較了抽取器、切割邊界與閱讀次序三樣東西。`kgecg_2017`／`g29` 那個「只覆蓋 84.5%」就是這樣量出來的，重量後真正獨有只有 **0.91%**。**判別法**：落差若在兩個方向上**對稱**，那是次序噪音不是內容差異；再把落差視窗拆半，一半在對方文件內就是接合處產物。 **【S233】生產 gold 185 題有 4 條 `57014` 逾時（S226 為 1 條），單獨重跑全部成功；若下次再升，要當成容量問題查，不可再當偶發。**
3. 只監察 —— **實例層的冷熱落差 58–90 倍，成因未查明。** 同一句唯讀查詢第一次 916ms／2,259ms，第二三次 10ms／39ms。`EXPLAIN` 報 `read=0`（頁面已在共享緩衝區）照計不應如此，疑似受管平台的 CPU 爆發額度，**無證據，不編機制**。用戶感到的忽快忽慢現時主要來自這一項，屬平台層，改碼幫不到。**任何兩組查詢的比較都必須交錯重量三輪以上**，否則會把冷熱差異誤讀成結構差異。（本節已結案的那半邊見 `## Current Baseline` 5 與 `## Validation / QC` S221 段，不再列為風險。）
4. ⚠️ **【S224 降級：已由 🔴 收窄】Option A watcher bot 曾經推出一個不編譯的 `main`；那條路已經封死，但封死它的是兩層新機制，兩層都要維持。** (a) **碼層**：`execute_ingest.py` 步驟 6 改為推 `ingest/<source_id>` 分支 → 開 PR → auto-merge，不再直接推 `main`；`--self-test` 有一條 `ast` 結構斷言守住（紅測實證會轉紅）。(b) **設定層**：`main` 受 ruleset 保護，`build-gate` 為 required check（推空 commit 實測被拒）。**仍然要小心的三件事**：① 四條 ledger workflow 經 `DeployKey` 永久繞過該閘 —— 它們現時只寫 JSON、不碰 `backend/`，但這是「現時的碼」而非機制保證。**那把鑰匙 `LEDGER_DEPLOY_KEY`（ed25519，`id=163258294`，`read_only=false`，沒有到期日）等同一把可以直接寫 `main` 的萬能匙**；私鑰全程未印出、本機檔案已刪，只存在於 repo 加密 secret。輪換：產生新 key → `gh repo deploy-key add --allow-write` → `gh secret set LEDGER_DEPLOY_KEY` → 刪舊 deploy key；四條 workflow 不需改動（只讀 secret 名）；② `backend_build_check.yml` **不得加回 `paths:` 過濾**（會令 required check 永遠 pending 並擋死所有 push，理由寫在該檔頭部）；③ ~~入庫 PR 路徑未經一次真實入庫驗證~~ —— 已多次真實運作（#27、#41、#42）。**【S235 新發現】同一次 executor 運行批准兩份以上時，第二份的 PR 必然衝突**：它的 `ingest/<id>` 分支建在第一份**未壓縮**的 commit 之上，而第一份合併時是 squash，於是兩個 commit 內容相同、歷史不同，10 個檔衝突、auto-merge 永遠等不到（executor 15 分鐘後報 DIRTY 失敗，但 Supabase 已寫入，資料庫領先 main）。人手解法：把第二份的單一 commit cherry-pick 到最新 main，再更新 PR 分支（需強制推送，要 Leonard 批准）。根治在 executor（見 `## Open Priorities` ⑫）。**另**：GitHub 執行機塞車時，剔選觸發的批准工作會零步驟被取消，**Issue 上的剔號仍在但沒有紀錄**；補救是重跑該 run（沿用當時的事件內容）。**紀律不變：開工與 push 前一定要 `git fetch` 後比對，不得讀交接記載的 hash 當現況。** 以下為 S223 原文記錄： 2026-09-13 三個連續 ingest commit（`e2b53f0`／`183b7a8`／`9e5f28c`）把兩條 allowlist 條目寫在 `curriculum: [` 之外，`main` **約 16 小時不編譯**，Render 建置失敗後繼續服務上一個成功 build（`5765c43`），`/health` 照報 `ok:true`，**所以症狀不是停機而是部署凍結**，前端在 Pages 上完全正常，沒有任何用戶可見徵狀。planner 根因已封死（見下 Open Priorities 註），並新增 `Backend Build Gate`。**但那個閘偵測，不阻擋** —— 它跑在 push 落地之後；要真正擋住需要在 GitHub 開 branch protection 並把該 job 設為 required check，**只有 Leonard 做得到**。**紀律不變：開工與 push 前一定要 `git fetch` 後比對，不得讀交接記載的 hash 當現況。**
5. 只監察 —— `AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 三檔在 `.gitignore` 內且從未 tracked；`.gitignore` 的 `AGENTS.md` 規則無前置斜線，會在任何深度命中，連升級前備份都被 ignore。**這三個檔 git 內沒有任何副本。**
6. ⚠️ **【S223 新發現】本機 python 環境分裂，專案腳本的 `python3` 未必跑得動。** PATH 第一個是 homebrew **3.14**，它**沒有 PyMuPDF（`fitz`）亦沒有 `openai`**；有齊依賴的是 `/usr/local/bin/python3`（openai 2.26）與 `/usr/bin/python3`。`dev/ingest_one_source.py` 本節第一次跑就因此直接失敗（`ERROR: openai not installed`）—— **而它是在 792 條片段已經刪走之後才失敗的**，即那一刻《學校行政手冊》在庫內是 0 條。**凡涉及抽取（`repage_pdfs.py`／`fetch_extract.py`）或入庫（`ingest_one_source.py`）的指令，一律明寫 `/usr/local/bin/python3`，不要寫 `python3`。** 更好的做法是先跑一次 `--dry-run` 確認依賴齊全再做破壞性步驟。
7. ⚠️ **【S222；S223 更正其下半截】看門狗救不到「七個一齊死」。** 它跑在同一套 GitHub Actions 排程機器上。官方行為：錯過或失敗的排程**不會補跑**、`schedule` 高負載會延遲或跳過、**PUBLIC repo 60 日無活動排程自動停用**。它買到的是**互相監察**＋偵測窗由一星期收窄到一日；這句寫死在它每次出聲的輸出裡。看門狗與 pgvector 監察**仍未經歷一次真實排程觸發**。**【S223 更正】「生產寫入仍然要 Leonard 在終端機跑」這句已經過時** —— 本節 AI 直接執行了 `cb3_deprecate_stale --execute` 兩次（共刪 900 條）與 `ingest_one_source` 一次（入 387 條），全部通過，無被分類器擋。**所以生產刪除現時是 AI 做得到的**，安全邊界由「跑唔到」變成「要先取得 Leonard 明示批准」，兩者強度不同，寫計劃時不要再假設有一道機械閘兜底。

8. 🟢 **【S225 發現並修好】封版閘的 `EVAL_LATEST` 假綠已收掉，但收掉之後那一格是紅的。** 舊行為：`latest_eval_run()`（`qc_report.py`）是 `sorted(glob("*.json"))[-1]`，不過濾揀中的是不是一次檢索評測；`check_eval_latest()` 再用 `s.get("FAIL", 0)` / `s.get("errors", 0)`，欄位不存在即當 0，於是「零失敗」恆真 → PASS。09-14 當日揀中 `2026-09-14_s223_kgecg_g29_overlap.json`（無 `summary` 欄），detail 逐字是 `None · PASS=None FAIL=0 … 共 None 條 query`。**修法**：新增 `is_gold_eval()`（要求 summary 具備 `PASS`／`FAIL`／`queries`），選檔改為由新到舊揀第一份合資格者，判分缺數據一律 `NOT_MEASURED`——即對齊同函式下半截 `EVAL_CHUNK_LAYER` 早已寫對的做法；detail 加印「量度自 <檔名>」令陳舊看得見。**實測**：`--self-test` ALL PASS（新增五條斷言），兩次針對性注入各自準確轉紅且不波及其他；重跑 `--check` 後 PASS 13 → 12、ERROR 2 → 3、releaseGate 5/15 → **4/15**，`PASS_EVAL_LATEST` 由 `MET` 轉 `NOT_MET`，其餘二十項檢查**零變動**。**餘下**：該格現時報 `FAIL`，量度自 2026-09-08 的 gold run（`FAIL 44/185`，且是旗標關閉的 before 基線）——**要令它轉綠只能靠改善檢索（現為 Open Priorities ②），不是靠再改 `qc_report.py`。**⚠️ **S228 更正**：原文寫「靠 ① 重跑 185 題」，但 ① 已於 S227 完成並移除，而且 S226 早已重跑過 gold —— 重跑本身不會令它轉綠，要轉綠必須真的把 FAIL 數壓下去。根因備註：`DOC_SYNC_CHECKLIST.md` 第 56 行早已寫明「新檢查不得預設報 0——量不到要報 `NOT_MEASURED`」，即這是既有規則沒被遵守，不是規則缺失。完整分析見 `dev/AUDIT.md` 乙①。

9. 🔴 **【S226 發現】封版閘那一格在報生產不執行的配置 —— 選檔永遠揀旗標關閉側。** `latest_eval_run()`（`qc_report.py:706`）是 `sorted(EVAL_RUNS.glob("*.json"), reverse=True)`，而同一日的 `..._before.json` 與 `..._after.json` 反向排序時 `b` 在 `a` 之後，**所以永遠揀 `before`**。現時 detail 逐字為「S219 route-first before (in-process, FEATURE_ROUTE_FIRST_SEARCH=0) · PASS=119 FAIL=47 … 量度自 `2026-09-15_s226_route_first_before.json`」，而 S226 已用行為探針核實生產行的是**開啟**側（184/184 逐條同判，見 Current Baseline 5）。**🟢 已修（Leonard 同節拍板選項 A）**：新增 `measures_production()`（`endpoint` 以 http(s) 開頭且非 localhost）與 `eval_source_kind()`；`latest_eval_run()` 在合格 gold run 中優先揀生產那一份，並在 detail 明寫「生產端點」或「非生產端點」，另列出未被採用的較新 run。**閘現時報 PASS 121／FAIL 44／errors 1（生產）**，不再報實驗室的旗標關閉側。7 條新斷言全綠，紅測（選檔打回 `runs[0]`）準確轉紅。**當初沒有逕自改的理由仍然成立並已記錄**：`/health` 不報 flag，「哪一份 run 代表生產」是個假設；選項 A 之所以可接受，是因為它不假設旗標值，只假設「打生產端點的 run 反映生產」，而這個假設由 S226 的行為探針（184/184）獨立支持。**同一節另一項已修**：`EVAL_CHUNK_LAYER` 長期 `NOT_MEASURED` 的原因不是沒重跑 gold，而是**兩支 185 題 harness 都沒有把片段層數字寫入 `summary`**（判分在 `check_eval_latest()` 的 `if "chunk_FAIL" in s`），每題的 `chunk_verdict` 其實一直算了出來、只是從未匯總；S226 把 `summarize()` 單一來源化後該格已有數（現報 FAIL）。**所以交接檔原本寫「做完 ① 就自然有」是錯的**，那是工具缺口，不是量度債。

11. 🟢 **【S241 結案，只監察】OpenAI 2027-01-14 停用的四個型號已不再使用。** 生產合成與判官已轉 `gpt-6-luna`＋`none`（#53 合併、Render 刪 `OPENAI_MODEL`、線上抽查正常）；OCR 轉 `gpt-6-luna`＋`none`（實測達標）；量度判官轉 `gpt-6-luna`＋`low`。**餘下要監察的只有一項**：量度判官的校準有 1 對位置偏誤（5/7 一致，基線 gpt-4.1 亦 5/7），Leonard 明知仍定案；有偏誤的一對會記為 `INCONSISTENT` 而不出勝方，代價是靈敏度。每次量度要看 artifact 的 `judge_health.always_first`，經常非 0 即要重新選型。gpt-5.6-luna 兩個設定亦已量過、不達標。以下為 S239 原文：🔴 **【S239】OpenAI 2027-01-14 停用 `gpt-4o-mini`（生產合成）、`gpt-4.1-mini`（生產判官）、`gpt-4.1`（答案層量度判官）、`gpt-4o`（`ocr_extract.py`）。** 生產兩項已有量好的遷移（PR #53＋Render 改 `OPENAI_MODEL`），**未合併、未改 Render 前仍是風險**；離線兩項未選型。合成失敗會被吞掉成空答案，所以停用日之後會靜默失效而非報錯。

10. ⚠️ **【S238；S239 更新】監察通知：機制已在 10-19 真實排程運作（Freshness #1 @mention 留言、Discovery #54 帶 @mention），只餘「Gmail 是否收到」待 Leonard 確認。** 以下為 S238 原文：**【S238】監察通知修正未經真實排程驗證。** 合併後 2026-10-19（週一）首次排程應在 Leonard 的 Gmail 收到 @mention 電郵；若沒有，先查 Actions log 的 `announced N new item(s)` 與 Leonard 帳戶通知設定。之後只有新項目才通知，freshness 舊項在基線 write-sync 前會一直留在 Issue 內文（不再重複通知）。

<!-- ack:section:workspace-identity -->
## User Environment (Always Reference Before Giving Shell Commands)
- **Repo path**: `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（路徑含空格 —— 終端機指令必須用雙引號包住）
- **Correct cd**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`
- 🔴 **Python：有三個，只有兩個跑得動本專案的抽取／入庫腳本。** 預設 `python3` = homebrew **3.14**，**無 `fitz`、無 `openai`**；`/usr/local/bin/python3`（openai 2.26 ＋ fitz ＋ requests）與 `/usr/bin/python3` 才齊。**抽取與入庫一律明寫 `/usr/local/bin/python3`**；純標準庫的監察腳本（`check_*.py`／`execute_ingest.py --self-test`／`build_wiki_index`）用 `python3` 沒問題。詳見 Risks 6。 **S232 補**：`python3.13` 亦有 `openai`＋`requests`，`dev/ingest_s232_kg_ratio_footnote.py` 與 `footnote_lead_probe.py` 以它實跑通過。
- **Python script invocation**: 一律由 repo root 起，例如 `cd "…/Draft" && python3 dev/vault/extract_candidates.py ...`
- **Backend**: `cd "…/Draft/backend" && npm run dev`
- **Git state（S247 收工，2026-11-09）**: `origin/main` = `82be06e`（PR #89 已合併）；線上執行碼 `20fd4a4`；本節收工分支 `s247-closeout`；本機另有已合併的 `s246-closeout`、`s247-init-backup-cleanup` 與 `s240/*`–`s245-*` 等舊本地分支（未清理，非本節範圍）；worktrees 1。以下為 S246 原文。 - **Git state（S246 收工，2026-11-08）**: `origin/main` = `d6b18f6`（PR #87 已合併為 `62647fe`）；線上執行碼 `20fd4a4`；本節收工分支 `s246-closeout`；`s244-option2-round1` 已刪；本機尚有 `s240/*`–`s245-*` 等舊本地分支（未清理，非本節範圍）；worktrees 1。以下為 S245 原文。 - **Git state（S245 收工，2026-11-05）**: `origin/main` = `27a59d5`（PR #86 已合併為 `12c1ab7`）；線上執行碼 `20fd4a4`；本節分支 `s245-option2-round2`（工作 commit＋收工 commit，PR #87，未合併）；舊分支 `s244-option2-round1` 多一個重複 commit `d2c95ee`（無 PR）；worktrees 1。以下為 S244 原文。 - **Git state（S244 收工，2026-11-05）**: `origin/main` = `ab2aee9`；線上執行碼 `20fd4a4`；本節分支 `s244-option2-round1`（工作 commit `90bb921`＋收工 commit，PR #86，未合併）；worktrees 1。以下為 S243 原文。 **Git state（S243 收工，2026-11-03）**: `origin/main` = `37451db`（#79–#84 已合併）；線上執行碼 `20fd4a4`；收工分支 `s243/closeout-final`（新 PR，只改治理文件與 README 一字）；本機已合併分支 `s243/*`、`s242/*` 未刪。以下為 S242 原文。 **Git state（S242 收工，2026-11-02）**: `origin/main` = `814bd0c`（#73、#74、#75 已合併）；線上執行碼 `3ef9ab6`；收工分支 `s242/closeout`（新 PR，只改治理文件）；已合併的本機分支 `s242/cover-title-refresh`、`s242/blnst-route`、`s242/qc-report-race` 未刪。以下為 S241 原文。 **Git state（S241 收工，2026-10-29）**: `main` = `da44e55`（#53 已合併並部署）；收工 commit 推上 `s241/model-migration-circular`（新 PR，含通函編號查找的 `backend/src` 改動）；已合併的本機分支 `s239/query-fusion`、`s240/deps-security` 未刪。以下為 S240 原文。 `main` = `77de1dd`（#55 已合併並部署）；收工 commit 推上 `s239/query-fusion`（PR #53，未合併，未含 #55）；已合併的本機分支 `s240/deps-security` 未刪。以下為 S239 原文。 **Git state（S239 收工，2026-10-21）**: 本機分支 `s239/query-fusion`（PR #53，已 rebase 到 `origin/main` `c4b3a6a`），收工 commit 推上同一分支；`main` 未含 S239 任何改動。以下為 S238 原文。 **Git state（S238 第二次收工，2026-10-13）**: `main` = `a67bd29`（#48／#49／#50 已合併）；收工分支 `s238/closeout-2` 由 `main` 開出，只改治理文件。以下為第一次收工原文。 **Git state（S238 收工，2026-10-13）**: 收工分支 **`s238/monitor-notify`**（由 `origin/main` `7b6a68b` 開出，合併了未合併的 `origin/s237/closeout`），PR #48 由 Leonard 指示合併（squash）；合併後 hash 下節核實。worktrees 1。以下為 S237 原文。 **Git state（S237 收工實測，2026-10-11）**: root 與 git root 皆為 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft` · 收工分支 **`s237/closeout`**（由未合併的 `origin/s236/closeout` 開出，再合併 `origin/main` `a344504`，只含收工文件）· worktrees **1**。`origin/main` = **`a344504`**；線上執行碼 **`a344504`**。已合併但仍在的本機分支（S235 記約 13 條，另加 `s235/route-b-closeout`、`s236/subject-check-v1`、`s236/closeout`、`s237/openai-model-default`）**未逐條核實、未刪**；清理須先唯讀核實已合併（squash 後 `git branch -d` 會報 not fully merged，要用「分支 tip 對其 squash commit 的樹比對＝0 檔差異」核實再 `-D`），並經 Leonard 批准。
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

**【S247 收工，2026-11-09】本節只清理本機 `dev/init_backup/` 舊版 `wiki_index.json` 備份（約 11.09 GB，已完成，不要重做）並加保留規則（`dev/rules/safety.md` `## Project Rules`）。Recommended next step 不變：退役 `EDBC_9_2019_E`，理由與做法見下列 S246 段；執行前先向 Leonard 再確認。** 以下為 S246 原文。 **【S246 收工，2026-11-08】Option 2 與 Channel A 退役已完結（清單 0 條、109 行副本已刪），下列 S245 段的 ①、(a)、(b)、(c) 皆已處理，不要重做。** (b) 的結論是**不登記**：footnote 來源按設計不入 `source_registry.json`（見 `## Validation / QC` S246 (6)）。**Recommended next step：退役 `EDBC_9_2019_E`（2 段 `footnote_curated`）** —— 理由：EDBC 4/2026 已取代通告 9/2019，S238 時 Leonard 已批准「退役及備份」但被分類器擋下一直未做，而它在「SEN學生留級」查詢佔第一格（S239 實測）。做法照 S238 原文（先 `select=*` 匯出到 `dev/init_backup/<ts>/` → `DELETE ?source_id=eq.EDBC_9_2019_E` → `live_display_sync(17074, 17072)` → 補 `update_log.json`）；批准已隔多節，**執行前先向 Leonard 再確認一次**。其餘待 Leonard 決定（無次序）：S244 三條 footnote 的粵語問句是否改寫；語料庫時限段落（例如通告第13/2025號 2025/26 培訓基地地點）是否交 `check_expiry.py`；`app.html` 角色標籤一律「全校」是否移除；以及 S243 段 (a)–(d)、S241 段 ③（定期系統更新檢查，上次 2026-10-30，約 11-29 到期）、`FEATURE_SUBJECT_CHECK`。 以下為 S245 原文。 **【S245 收工，2026-11-05】Recommended next step：Option 2 最後 1 條（租金收入）—— 請 Leonard 定出處，然後清空清單**。理由：清單清空才可按規則第 5 條匯出備份並經 Leonard 批准刪 Supabase 109 行 `approved_fact`（`role_facts_*`）。該條原文：「設有法團校董會的資助學校應按照指引收取租金，並將收入按比例用於學校及班級津貼。」兩個候選出處：(甲) `g02`《財務管理指引》表格（chunk `vault_g02_b233f0a42484ec31`，通告第5/2011號一行，抽取後兩欄交錯；要讀原 PDF 才可重組）；(乙) 已在庫的 `footnote_fn_tips_rental_40pct`（`subvention_tips`：淨租金收入40%須記入政府津貼帳）。定了出處 → 寫 `resolved`（帶 `fact_corrected`）→ 清單 0 條 → 按規則第 5 條：先 `select=*` 匯出 109 行到 `dev/init_backup/<ts>/`，報數，等 Leonard 批准才 DELETE，再 `live_display_sync`。 **同節待辦**：(a) PR #87 待 Leonard 指示合併；(b) 未登記 `source_registry.json` 的新 source_id 現有兩個：`edbc29_2024_teacher_training`（S244）、`edb_byod_page`（S245）——登記與否待決；(c) 舊分支 `s244-option2-round1` 可刪（PR #86 已合併；`d2c95ee` 為重複 commit）；(d) S244 的 (c)–(e) 照舊：S244 三條 footnote 的粵語問句是否改寫（S245 新 footnote 已用書面語）、語料庫時限段落是否交 `check_expiry.py`、`app.html` 角色標籤「全校」。 以下為 S244 原文。 **【S244 收工，2026-11-05】Recommended next step：Option 2 餘下 39 條 —— 繼續網上搜尋教育局原文**（Leonard S244 指示「庫內找不到相關段落 → 嘗試網外 Google 等搜尋，看看會否找到答案／出處，再判斷修正」）。理由：清單清空或餘項皆判定，才可按規則第 5 條匯出備份並經 Leonard 批准刪 Supabase 109 行 `approved_fact`。做法：逐條搜 `edb.gov.hk`（Tavily 曾 429，要放慢）；先查庫內是否其實已有該文件（S244 首輪 12 條中 6 條原來在庫，只是關鍵詞未中）；找到原文 → 按規則第 7 條以原文修正措辭；庫內沒有 → footnote_curated 入庫（規則第 3 條，要 Leonard 批准；範本 `dev/ingest_s244_option2_footnotes.py`）；找不到或已過時 → 剔除（規則第 4、6 條）。餘下類別：選舉日半天假、連續三日缺勤、小學科學培訓時間表（2024 上旬等，多屬時限資料）、境外活動呈報、性罪行定罪紀錄查核、BYOD、私隱、公開資料守則、借用機制、課程與資源類。 **同節待辦**：(a) PR #86 待 Leonard 指示合併（不改 `backend/`）；(b) 新 source_id `edbc29_2024_teacher_training` 未登記 `source_registry.json`（drift 檢查會列 UNMANAGED，非阻塞）——登記與否待決；(c) 三條新 footnote 開頭問句沿用現有 footnote 的粵語口語問法（為配合口語搜尋），與書面語規範不一致，是否改寫待 Leonard；(d) 時限資料規則（第 6 條）已用於清單，但**語料庫本身**的時限段落（例如教育局通告第13/2025號的 2025/26 培訓基地地點）未處理，Leonard 指示「應向退役機制思考」——下一步要決定是否把這類段落標為 `dated_edition`／`ephemeral` 交 `check_expiry.py`；(e) `app.html` 角色標籤一律顯示「全校」，可移除或改顯示文件適用對象（產品決定）。S243 其餘項目照舊列於下文。 **【S243 收工，2026-11-03】Recommended next step：Option 2 第一輪（Leonard 指定「下一步先做」）** —— 對 `dev/knowledge/channel_a_option2_queue.json` 的 455 條，按 `_meta.rules` 第 2 條以 Jev 判斷閘 `dev/source/jev/channel_a_match_gate.json` 逐條核對：先寫一支腳本（檢索候選段落 → 交 Jev → 按三題機率分流 → 寫 `resolved`／`dropped`／人手名單），小批試跑並抽樣覆核後才全量；理由是清單每減一條，Supabase 那 109 行副本就少一條要處理，而每輪入庫都要跑同一步。Jev 呼叫屬外部呼叫，批量前先報數量。其後：(a) **文件標註重開四條件**（CHANGELOG〔文件標註收起待修〕：最高分＋重量門檻、欠缺按相關度排、部分符合加字詞閘、開始記使用次數）；(b) **搜尋紀錄加拒答原因**：本節已設計（`decline_reason`＋`judge` 兩欄；`synthesizeAnswer` 回傳原因代號；`log_search` 要先刪舊簽名再建，防 PGRST203），DDL 待 Leonard 批准；同時修好「找不到相關政策」與空答案被記成已作答；(c) #70 待 Leonard 關閉；(d) 可選清理：`app.html`／`mobile.js` 不再觸發的 approved_fact 顯示程式、dev/vault 舊 Channel A 篩選腳本（`extract_candidates.py`、`ai_extract.py`、`dedup_check.py`）。S241 ①–⑤ 與 S242 三項照舊列於下文。 **【S242 收工，2026-11-02】** 封面核對 #72 已結（三份換版／退役入庫並部署）；`blnst` 路由與 QC 撞車修正已合併。**Recommended next step 不變，仍為下面 S241 開首的 ①（有效期第一次真實剔選時核實 PR 開出並合併）**，理由是它的清除路徑只用樁件測過，而 S242 沒有觸及。S242 新增三項，排在 ⑤ 之後：(a) **#70 已併入 `main`**，PR 仍開著，關閉前先問 Leonard；(b) **QC 撞車修正只經單次執行驗證** —— 下次合併 PR 同時關閉 Issue 時，看兩次 `Knowledge-base QC Report` 是否都 success；(c) **BLNST 短查詢第一位多為 `supply_teacher_guide`**（亦載 BLNST 條文，可接受）；若要讓通函或問與答排第一，要動配額或重排，不是路由。 **【S241 checkpoint，2026-10-30】** 原 ① 補丁三已合併並線上驗收（`## Validation / QC` S241 (9)），只餘「對照表補讀登記標題」一項可選。**expiry-sweep 清除路徑已修**（ops `e1c3eaf`）：purge job 改為推 `expiry/purge-*` 分支、以 `MAIN_REPO_PAT` 開 PR 並 auto-merge；DELETE 之後任何一步失敗都在 Issue 留言。本機以樁件跑過正常與「開 PR 失敗」兩條路徑；真實剔選尚未跑過，第一次使用時要看 PR 是否開出並合併。兩份過期候選已由 Leonard 決定保留，待清除 0。另：分類器會把 feed 中等於發出日期的「截止日」當期限、把標題「測試」當一次性，補標 feed 來源時要讀全文核實。**流程注意**：多份批准的 executor 運行期間，不要合併其他改 registry／公開數字的 PR。以下 ①–⑤ 其餘照舊。 **Recommended next step（S241 收工重生，2026-10-29）：** **① 通函編號查找收尾** —— 生產已開並驗收（`## Validation / QC` S241 (7d)：62/62 排第 1）。補丁三（文件內選段扣除編號，分支 `s241/circular-topic-ranking`）合併部署後，帶 `x-probe` 以「教育局通函第134/2026號 推廣閱讀津貼可以用來做甚麼」做一次 `synthesize:true`，確認不再拒答。可選：對照表補讀登記標題，覆蓋第 1 頁無標頭的 7 份。合併只在 Leonard 明示時進行。 **② 收錄「教學語言政策」文件** ——【S241 已完成，2026-10-30】Leonard 批准入庫 4 份：`edbc006_2009`（通告6/2009，17 片段）、`moi_3rd_cycle_2021`（4）、`moi_plan_2027_28`（5）、`moi_faq_2026`（26）；新 `moi` 路由，本機 12/12 查詢排第 1（改前 4/12）；Supabase 17,153、310 來源；來源頁「微調中學教學語言」納入新文件監察。待線上合成抽查一次。以下為原文：真實拒答 9 條中 5 條問這題，庫內只有零星提及。先查證教育局中學教學語言微調政策的官方文件與網址，列出候選，等 Leonard 批准才入庫。 **③ 定期系統更新檢查餘項**（規則：`dev/rules/coding.md` `## Project Rules`；紀錄：`dev/PROJECT_INDEX.md` 指令表「定期系統更新檢查」一行）：本節只完成 OpenAI 一項；未做本機及 Render 執行環境、排程監察、Kit 新版（0.4.4，是否升級要 Leonard 決定）。 **④ 退役 `EDBC_9_2019_E`**（S238 已批准未做；先匯出備份再刪，再 `live_display_sync`）。**⑤** Leonard 確認 Gmail 有否收到 10-19 @mention；待 token 項（非華語津貼路由、清單條文 8 條＋頁碼 49 處）；`FEATURE_SUBJECT_CHECK` 仍待 Leonard（開前以新判官重量）。 **另記（無須行動，只監察）**：原 ② 註腳佔格已量完並判定不是檢索槓桿（`## Validation / QC` S241 第 5 點），不要再當作待做；`search_log` 未記錄拒答原因（判官否決、合成出錯被吞、窗口為空在紀錄中一樣），要分清需改 `log_search` 函式與表（DDL，要 Leonard 批准）；`edbc100_2002_healthy_sch` 登記標題編號錯（見 S241 第 8 點）；推廣閱讀津貼查詢被路由到 `hr_admin`（同第 6 點）。 以下為 S240 收工時的原文，其中 ①（模型遷移）已於 S241 完成、② 已結案，保留作紀錄。 **【S240 收工逐項核對，2026-10-23】下列 S239 的 ①–⑤ 全部仍適用、次序不變**（S240 只做依賴漏洞修補 #55，未動任何 OP）；注意 ①(b) 的線上 commit 現為 `77de1dd`，#53 合併前線上不含 S239 任何後端改動。 **Recommended next step（S239 收工重生，2026-10-21）：** **① OpenAI 模型遷移收尾（期限 2027-01-14）** —— Leonard 定案「先收工，下一次再做時就檢查應該轉甚麼 model」，取向是**開支與效能為先、剛夠用就得、不追新**（官方建議替代只是候選之一）。做法：(a) **先重讀官方停用頁與價錢頁**（`dev/CODEBASE_CONTEXT.md` OpenAI 段列的三個網址），核對 `gpt-6-luna` 是否仍是「最便宜＋未公布停用」、價錢有否變、有否新的更平型號；有變就更新該段再決定。(b) 核實 PR #53 是否已合併、Render `OPENAI_MODEL` 是否已改（`/health` commit、行為探針 `x-probe` 一次合成看答案是否較短）；合併後線上抽幾條答案給 Leonard 看（新模型答案約短一半）。(c) **離線兩項選型**：答案層量度判官 `_s227_rubricJudge.ts`（現 `JUDGE_MODEL=gpt-4.1`；S227 證 mini 級是壞尺，換模型前必須重跑 7 對校準，位置偏誤須為 0）與 `dev/ocr_extract.py`（`gpt-4o` vision，Chat Completions）；兩者都要先查官方頁、再以小批量驗證，外部呼叫需 Leonard 批准。工具：`backend/scripts/_s239_modelAB.ts`（同一窗兩組模型、計時、記錄被吞錯誤）、`dev/source/judge_acceptance.py`（`JUDGE_MODEL`＋`JUDGE_REASONING_EFFORT`）。**② 合成窗被無關註腳佔格**（S239 新根因）：「SEN學生留級安排」頭兩格是境外遊學團 1:10、非華語暑期班；註腳 lead 門檻只要求兩個共用二字詞（「學生」「安排」即過）；先量 `footnote_lead_probe` 再改，不可單調門檻（S196 證正負分佈重疊）。**③ S238 ①：退役 `EDBC_9_2019_E`**（仍未做；S239 實測它在「SEN學生留級」佔頭一格）。**④** 確認 Gmail 收到 10-19 @mention 通知（只 Leonard）。**⑤** S238 ③（非華語津貼路由、清單條文 8 條＋頁碼 49 處，待 token）。另：`FEATURE_SUBJECT_CHECK` 決定仍待 Leonard —— 注意新判官 `gpt-6-luna` 在凍結集已正確拒答 D01／GN10，開旗標前要先以新判官重量。以下為 S238 原文：**Recommended next step（S238 收工重生，2026-10-13）：** **① 退役 `EDBC_9_2019_E`（2 段 `footnote_curated`）** —— Leonard S238 已明示批准「退役及備份」，但 auto mode 分類器擋下刪除與備份，未執行。理由：EDBC 4/2026 同時取代 8/2014、8/2020、9/2019（`EDBC26004E.pdf` 原文 "This circular supersedes…"），9/2019 連結仍 200 所以監察捉不到，內容卻已過時；同族的 8/2020 已於 S238 退役。做法：先 `select=*` 匯出到 `dev/init_backup/<ts>/`，再 `DELETE ?source_id=eq.EDBC_9_2019_E`，再用 `execute_ingest.live_display_sync(current_chunk_total(), live_total_count())` 同步公開數字（16,990 → 16,988）。若仍被擋，請 Leonard 調整權限或在 Supabase 自行執行。**② 確認 2026-10-19 週一監察通知真的寄到 Gmail**（見 `## Risks / Blockers` 10）。**③（待 Leonard 有 token）** 非華語學生津貼答案的路由（審計報告舊級別仍被引用、g19 新版未入前列）；清單條文：跑 `python3 dev/source/check_downstream_sync.py --sources g19,supply_teacher_guide,g26,k1_admission_2627,gifted_tp_resource_kit,sse_tools_2025 --base 7b6a68b --since 2026-10-13 --notes <改動摘要> --jev`，處理 Jev 判必須更新的 8 條與 49 處頁碼移位（改 `dev/checklists/_work/*/checklist.json` 後跑 `gen_checklists_bundle.py`，不手改 bundle）。**常設規則（S238）**：任何來源換版／改網址／退役後，收工前 `check_downstream_sync.py` 的 `MUST_UPDATE` 必須為 0。**④** Leonard 決定是否開 `FEATURE_SUBJECT_CHECK`（S236–S237 的第一順位，S238 未動，理由見下段原文）。 以下為 S236 原文：**Recommended next step（S236 收工重生，2026-10-07；S237 收工逐項核對仍然適用 —— S237 只處理模型停用通知，未動任何 OP）：** **由 Leonard 決定是否在 Render 開啟 `FEATURE_SUBJECT_CHECK=1`。** 理由：路線乙 v1 已按設計文件第七節實作，經 PR #44 合併並部署（`f9da565`，合併後線上實測旗標未開），旗標預設關閉；TS 與 Python 原型 250 題逐題相同，生產現行窗 254 題重量**攔 7、全部應拒答、應答與 gold 誤攔 0**，本機端到端確認旗標開時 D01／SX01 以固定句拒答、零模型呼叫（`dev/source/SUBJECT_CHECK_DESIGN.md` 第八節）。開啟只影響「窗內完全沒有該類人」一種錯置（已知判官漏判 5 條攔 3 條）；開啟後用 `search_log` 以固定前綴「根據檢索到的教育局文件，未有找到適用於」篩出真實攔截逐條讀窗。⚠️ v1 **不覆蓋** `FEATURE_GROUNDED_SYNTHESIS` 路徑（生產關閉）；如將來開 grounded，要另加一處。不要再改判官提示或擴詞表（S202、S211、S230、S235 已證無益）。**副線**：`search_log` 本機報告（`dev/search_log_report.py`，只在本機讀、不得公開）；狀態頁四項「待決定」監察 Issue 仍等 Leonard。

**次序（不可倒轉）**：~~補基線~~（S231）→ ~~GN10 個案修（甲）~~（S232）→ ~~重跑 gold~~（S233）→ ~~乙的離線設計與量度~~（S235）→ ~~乙 v1 實作（旗標關閉）＋重量~~（S236）→ **Leonard 決定是否開啟** → 才談啟用 `FEATURE_VAULT_GATE_RAWVEC`。原因見 `## Validation / QC` S230 第六至八批：候選會令判官對多 52 條查詢變成承重件。**治理側第一件維護工作（S230 留下、S231／S232 未做）**：log 維護兩套觸發標準（`AGENTS.md` §4a 的 >400 行／>30 日 對 Kit 核心的 ≥11 條）要整合為單一定義，見 `## State Reconciliation Check` S230「Pack 衝突」。

② 🔴 **把片段層召回率拉高（缺口本體；基線與本節新數字見 `## Current Baseline` 7 與 `## Validation / QC` S228）。**

**S228 之後，已排除的方向增至七條**，前四條照舊（重新切片、調配額、詞面重排、改展開機制本身），新增三條：**(5) `EXPANSION_MIN_QUERY_CHARS`（floor）不出貨** —— 檢索兩層都改善（`floor=8` 片段層 +5、零退步），但它把展開詞整段拿走，**最高分中位跌 0.1296**，令 15–28 條題目跌穿 `VAULT_LEAD_SCORE` 0.70、17–27 條跌穿 `SPOTLIGHT_LEAD_SCORE` 0.60，答案層棄權由 8 升到 15（其中 10 條可答），判官 `net_after` +3.5／門檻 8 → `NO_MEASURABLE_GAIN`。**(6) 合併配置（floor ＋ balance）同樣不出貨**，理由同上（`net_after` +3.5）。**(7) `EXPANSION_BALANCE` 單獨啟用亦不出貨** —— 它幾乎不壓分（幅度只有 `floor` 的三十分之一、跌穿 0.60 者 0 條），檢索層 +4／+3、零退步，但答案層 `net_after` 只有 **+1.5**，棄權仍由 8 升到 11。⚠️ **這一條同時削弱了「全部怪門檻」這個讀法**：連幾乎不動分數尺的版本都只有 +1.5。所以本節的證據支持兩個並存的讀法，不要只取其一 —— **(i)** 下游兩個絕對分數閘確實吃掉了一部分得益（棄權上升、0.70 跌穿數可量）；**(ii)** 這個量級的檢索改動（片段層 +4 至 +7）本來就很難在 79–81 條的pairwise 判官上堆出 8 分淨值 —— 79 條之中判官判 **43 條 TIE**，即大部分題目的答案在它眼中根本無分別。**下一節要先決定信哪一個，因為兩者的下一步不同**：(i) 指向重校門檻，(ii) 指向「門檻 8 對這個量級的改動是否合適」，而後者屬 `dev/DOC_SYNC_CHECKLIST.md`「答案層評分改動」row ——**改門檻必須在跑之前決定並記低改前改後與理由，不可看完數字才改**。

**展開側兩個候選 S228 已全部量完並關閉；未試方向現時是 (b) 與 (c)，兩條都已有量過的成本或明確的先決條件：**

  **(a) ~~`EXPANSION_BALANCE` 單獨啟用~~ —— 🔴 S228 已量完並判定不出貨，此路已封。** 檢索層 +4 片段／+3 來源、零退步，壓分幅度只有 `floor` 的三十分之一（真正被重新配重的 57 條：平均 −0.0042、中位 −0.0021、最差 −0.0426），跌穿 0.60 的題目 0 條、跌穿 0.70 只 6 條 —— 但答案層判官 79 條、145 次呼叫，**`net_after` +1.5／門檻 8 → `NO_MEASURABLE_GAIN`**，棄權由 8 升到 11（3 條可答的失去答案）。**不要在未做 (c) 之前重跑這一個**。

  **(b) cross-encoder 重排 —— 上限已量到。** 166 條有簽名的題目中，**重排最多救得到 42 條**（片段層 59 → 101 為絕對上限），而 **65 條（39%）連寬池 top-40 都沒有，任何重排都救不到**。寬池就是現有的 over-fetch（`fetchCount = topK*5`），所以重排可以插進現有流程而不必再檢索一次；每條查詢要評 40 個候選，現時 routed p90 是 2,498ms，延遲預算要先算。⚠️ **具體模型／供應商未選，且按 AGENTS §0b 不得憑記憶寫 API** —— 動手前要先查官方文件並把端點、參數、回應路徑寫入 `dev/CODEBASE_CONTEXT.md` External Services。

  **(c) 【S228 新開】把下游的絕對分數門檻重新校，然後把 (a)／(b) 再量一次 —— 這是本節的發現直接指出來的方向。** 檢索層的得益是真的（合併配置片段層 +7、零退步、噪音底線 0），被吃掉的地方是 `VAULT_LEAD_SCORE = 0.70`（`searchChannelB.ts:1422`，合成 bypass）與 `SPOTLIGHT_LEAD_SCORE = 0.6`（`:1473`，overlay 放行）—— **兩個都是常數，都是在「查詢帶展開詞」的分數尺上校出來的**。兩條可走的路：①**重新校常數**（要先量出新尺上的等效分位，不可拍腦袋改數）；②**改為相對門檻**（例如取窗內分數的分位數而非絕對值），那樣任何動搖分數尺的改動都不會再撞這道閘 —— 但這是改合成閘的行為，屬另一個 row，要自己的 before→after。⚠️ **不要在未量門檻之前再跑一次展開側的 A/B**：結果會跟 S228 一樣，兩層檢索報喜、答案層被閘吃掉。

  🔴 **【S229 實測，2026-09-20】(c) 的方向要改：0.70 不是「被展開詞抬高了要調返低」，而是由頭到尾校錯了尺，而且現況是偏低不是偏高 —— 所以不要重校這個數，要換訊號。** 定 0.70 那支儀器是 `dev/source/judge_probe.py`，它 **embed 裸查詢兼打全庫**（`match_threshold 0.1, match_count 40`，無 `SOURCE_SET`）；而 0.70 套用在 `mainSearchLead.score`（`searchChannelB.ts:1242`），那個分數來自 **`expandQuery` 展開後 ＋ 路由收窄** 的搜尋。185 條 gold 之中 **97 條是路由題**，兩把尺不同；其餘 88 條無路由，兩尺重合。新探針 `backend/scripts/_s229_scaleOffset.ts`（生產配置 `FEATURE_ROUTE_FIRST_SEARCH=1`，用生產函式，零重寫）把同一批 24 條校準 query 分三把尺量：**A 裸＋全庫**（＝校準尺，重現 S195 原數：CLASS_B 上限 0.6321 對 0.632、CLASS_C 下限 0.6241 對 0.624，儀器自我驗證通過）、**B 裸＋路由**、**C 展開＋路由**（＝應用尺）。結果：路由本身**不抬分**（A→B 為 0 至 −0.067），抬分的是展開（B→C 最多 **+0.3226**）。**重疊由 0.0080 擴大到 0.0817，大十倍**；而 CLASS_B 敵意題在應用尺上有 **2 條 ≥ 0.70**，即合成閘被跳過。逐條開過段落核實（`_s229_leadDetail.ts`）：**「校巴司機最低工資係幾多」@ 0.7098 是真缺口** —— 窗內四個來源 `sch_bus_drivers_2026`／`sch_bus_parents_2026`／`sch_bus_operators_2026`／`g18` 共 31 片段，`工資` 與 `薪` 命中 **0**，全庫 `最低工資` 只有 10 條且全部是經濟／通識科課程文件，**判官被跳過而合成器手上零工資內容**，正是 0.70 當初要擋的 S177 那一類。**另一條「老師病假連續請幾耐先要交醫生紙」@ 0.7003 是探針標錯，不是缺陷** —— `g04` 原文有「常額教師如申請病假超逾兩天，必須出示有效的醫生證明書」，領先那一片就是答案片段，bypass 觸發是正確行為；`judge_probe.py` 把它列入 CLASS_B（語料無答案）是錯的。**兩個後果**：① `judge_probe.py` 本身要修（它不行生產路徑，違反共用經驗庫 `self-authored-probe-false-confidence` 方法 B 第 3 步），`dev/DOC_SYNC_CHECKLIST.md` 那個「跑 judge_probe」的 row 照現狀跑只會繼續報校準尺的數；② 兩個分佈在應用尺上重疊得更厲害，**同一張卡尾段寫明「兩分佈重疊時調 threshold 係死路，要換訊號或換判斷器」** —— 所以 (c) 的路①（重校常數）證據上不成立。**建議走第三條路（S229 新提，未實作、未量）**：`rawVec` 已經為每條查詢 embed 好（零額外成本），把 vault 閘改為測「領先片段對裸查詢向量的 cosine」，即把閘放回它被校準的那把尺上。**這是改合成閘行為，屬 `DOC_SYNC_CHECKLIST.md` 自己一個 row，要先定案再量 before→after，未得 Leonard 批准不得改。**

  🔴 **【S230 實測，2026-09-21】(c) 的兩條路都走過了，兩條都不通，而且不通的方式不同 —— 不要再當它是「未試」。** 路①（重校常數）已由 S229 否決。路②的具體做法（S229 提的「換訊號」：把 vault 閘改為測領先片段對裸查詢向量的餘弦）**本節已實作為 `FEATURE_VAULT_GATE_RAWVEC`（預設關閉）並量完**：bypass **5 → 0**，只有真缺口「校巴司機最低工資」一條是想要的結果，另外四條是三個正控加上預先定案明列必須保住的「老師病假」。**原因是結構性的、不是實作問題**：0.70 比整個校準集在校準尺上的最高分（0.6457）還高 0.07，S195 當初刻意這樣定（「no choice of number is safe… needs a better JUDGE, not a lower bar」），**所以換回校準尺等於移除 bypass**。而判官接手不了：`人工智能初探` 與 `資訊及通訊科技 課程指引` 兩條 `want: 能` 的裸名詞題，在三份記錄的凍結 run 全部判「否」。**旗標留在碼內預設關閉，作為這次量度的可重現路徑；不要在 Render 啟用它。** 逐批證據見 `## Validation / QC` S230 四批，artifacts 見 `dev/source/eval_runs/2026-09-21_s230_*`。

  🔴 **【S230 續跑，2026-09-22】185 題 gold 的 bypass 人口普查 —— 這道閘的作用面是 59/185（31.9%），不是幾條；(乙) 因此死亡，(甲) 被指出有短查詢偏差，並新開一條 (丙)。** 完整八點見 `## Validation / QC` S230 第五批。要記住的三件事：**①** 真正的傷害是 **5 條 `FALSE_BYPASS`**（語料本來答不到卻跳過判官），**五條的共同形狀是「問一個語料裡不存在的數額或版本」** —— `幼稚園 表現指標`／`藝術教育學習領域課程指引 2002 版`／`資優教育學苑 收生 智商分數要求`／`校車服務 每月收費標準`／`校董有冇人工`。**②** rawvec 閘攔到 5/5，但同時攔錯 7/10 條 `SOUND`，而那 7 條有六條是二三個 token 的短查詢（裸向量對短查詢結構上低分）——**所以這個訊號的偏差方向正好打在真實用戶的主要輸入形態上**。**③** 詞面零重疊規則只攔到 1/59、對五條 `FALSE_BYPASS` 全部失效（它們的重疊全部非零），24 條校準集看似可行只是巧合。**(丙) 新提，未實作未量**：五條的形狀是「問數額而語料無此數額」，所以要測的不是相似度也不是泛詞重疊，而是**「窗內有沒有被問的那一類數量」** —— 但注意 S229 對 `校巴司機最低工資` 做過的正是這個手工版本（`工資`／`薪` 命中 0），要先證明它在這五條上都成立才值得寫碼。⚠️ **不要用產生這個假設的同一批數據驗收它**（row 41 紀律）。

  🟢 **【S230 判官接手測試，2026-09-22 —— 本節最終結論，推翻上面兩段的「不出貨」】** 上面兩段（換訊號失敗、普查否決兩個規則）的共同盲點是：**它們都用 stub 判官量度，所以量到的是「失去 bypass」而不是「失去答案」**。用生產判官模型實測 53 次之後：被攔的七條 `SOUND` **7/7 判官照樣答**（其中六條是二三個 token 的短查詢，即第五批推論的短查詢誤傷**在答案層並未實現**），而五條 `FALSE_BYPASS` 有 **4 條正確轉為拒答**。**按預先定案，候選達標。**代價兩項、殘留缺口一項、未量成本一項（延遲），出貨先決條件四項 —— 全部逐條列在 `## Validation / QC` S230 第六批。**下一節不要再找新訊號；要做的是補完那四項先決條件。**

**那 65 條救不到的題目是另一件事**：它們要動的是候選生成（索引／路由／切法），不是重排。這是 ⑤ 與 ④ 的地盤。

**出貨閘不變**：用 `backend/scripts/_s227_rubricJudge.ts` 量答案層再決定。⚠️ 用它之前要知的三件事：(a) 判官模型：S241 起腳本自有預設 `gpt-6-luna`＋`low`，不再讀 `JUDGE_MODEL`（S227 要求的 `gpt-4.1` 已因 2027-01-14 停用而失效；校準結果見 `## Risks / Blockers` 11）；(b) 依賴準則 3（數字）的判決自動標 `needs_human_review`（S228 有 22/81 條落入此類，比例不低，報結論時要連這個數一齊講）；(c) 跨次跑有變異（同一校準集 5/7 與 4/7），單題結論不可當定論。

🔴 **S228 新增的一條硬紀律（所有檢索改動都適用）** —— ⚠️ **S229 實測更正了它的適用範圍，照舊文照做會白做功夫**：原文寫「`VAULT_LEAD_SCORE` 0.70、`SPOTLIGHT_LEAD_SCORE` 0.60、`min_score` 全部是在『查詢帶展開詞』的分數尺上校出來的」。**只有 `VAULT_LEAD_SCORE` 與 `min_score` 是**；`SPOTLIGHT_LEAD_SCORE` 與兩個 `FOOTNOTE_*` 門檻**看的是裸查詢向量**（`searchChannelB.ts:1756` 的 `rawVec`，由 `:1770` 與 `:1821` 傳入兩個 overlay），所以**任何展開側改動都動不到它們**。證據：S228 十個 arm、共 1,667 筆 before／after 記錄，裸查詢字串在兩側逐筆同一個（`before_embedded`／`after_embedded`），0 筆例外。**修正後的紀律**：只有吃「展開後＋路由收窄」向量的閘（`VAULT_LEAD_SCORE`、`min_score`）才需要連同重校；把 spotlight／footnote 一齊算進去會做出一個不存在的因果。原文後半仍然成立 —— 動搖絕對分數而不重校，檢索兩層報喜而答案層變差，兩層檢索指標都不會顯示。

⑩ 🟢 **【S227 提出，S228 修好並重新定性】`hr_admin` 的「津貼」token 搶走幼稚園搬遷津貼查詢 —— 路由部分已修，但交接檔原本記載的病因是錯的。**

原記載說這是展開詞問題（裸查詢 0.5919 高過第 8 名 0.5879，加展開後跌到 0.4994）。S228 把展開完全關掉重量，**答案段落仍然入不到窗** —— 真正的閘是 `edbcm144_2026` 不在任何該查詢到達得到的 `SOURCE_SET`，只靠 spotlight overlay 露面，而 `SPOTLIGHT_MAX_LEADS = 1`，那唯一一格被 p.2 片段佔了。**已修**：`kg_admin` 由尾二提前到 `kg_admission` 之後、補「幼稚園＋津貼／搬遷」兩個 token、`edbcm144_2026` 入 `SOURCE_SETS.kg_admin`。blast radius 185 條只有 2 條改路由（皆為目標）、`route_regression` 63/63、第三條走 `kg_admin` 的 gold 零變動、off-gold 的 `幼稚園財務管理` 實窗核實已轉為幼稚園財務語料而 `學校財務管理` 不受影響。

**餘下的部分已改屬 ④ 的配額家族，不要再當成路由問題**：那兩條 gold 的答案段落在**它自己那份 8 片段文件內**排第 6（0.5919）與第 5（0.5943），而前三名是 0.7111／0.6868／0.6659、每源配額是 3。換言之路由修好之後窗由「SAG 假期段落 ＋ 1 條 KG 片段」變成「3 條該通函片段 ＋ 幼稚園行政手冊」，是實質改善，但 gold 量不到，而任何路由或展開調校都救不了它 —— 要動的是配額或重排。

③ **封版閘 5/15，餘下兩個 ERROR 都是檢索問題而非閘的問題。** `EVAL_LATEST`（生產 FAIL 44/185）與 `EVAL_CHUNK_LAYER`（chunk FAIL 107）**只能靠 ①② 改善檢索來清走**，改閘無用。另外：兩個 WARN 未有 waiver（`BODY_LENGTH_FLOOR` 3、`MOJIBAKE` 58 —— 兩者都已逐條讀過判定可接受，只欠在 `release_gate.json` 寫 owner／理由／接受期限）· 六項人手驗證從未記錄（核心搜尋案例、答案事實 spot-check、文件標註流程、mobile/desktop 分流、私隱與上載、冷啟動與錯誤狀態）。 **【S231 追加，入口盤點的產品決定四項，全部未動】** (a) 平台介紹桌面／手機分兩條路；(b) 手機無文件標註入口、分享的 `#annotate` 落入搜尋殼；(c) `#analyze`／`#review` 舊 hash 轉址已過「一季」且手機不處理；(d) 退役或收費路由 `/api/analyze-document`、`/api/checklist-revise`、`/analyze-circular` 仍公開（兩條會呼叫 LLM），保留與否無記錄。詳見 `## Validation / QC` S231 第 3 點。另：本機後端 `backend/.env` 缺 `SUPABASE_URL`，本機 Channel B 搜尋仍會失敗（#29 只修了 CORS）。 **【S233 追加】** (e) `index.html` 頁尾仍寫「v3.3.3」，是 S233 之前已存在的漂移（README 頁尾已於 #36 更正），未改。

④ **【累積遺留；S228 併入兩條新成員】** **新成員**：`kg_relocation_grant` 與 `fin_kg_relocation` —— 路由已修好（見 ⑩），但答案段落在**它自己那份 8 片段文件內**排第 6（0.5919）與第 5（0.5943），而每源配額是 3、前三名是 0.7111／0.6868／0.6659，**所以這兩條是配額問題不是路由問題**。⚠️ 加大 `MAX_PER_SOURCE` 已於 S226 實測是一換一（來源層 −4 換片段層 +5），不要當成現成解。**原有**：兩個護欄缺陷（1 條 `CONFIDENT_WRONG` 分數 0.7575 超過棄權門檻 0.75；**8 條查詢引用 gold 明令禁引的來源**，全部是「同一指引的不同對象／學級版本」）· `sch_bus` 五個對象版本吃掉 69 個窗格（**共用配額已證不成立**，要處理的是那五份文件該不該各自入庫與瀏覽 —— 產品決定）· `finance` 拿不到《學校行政手冊》與 `school_governance` 拿不到 `g02`（同一個病：路由集合缺跨範疇來源；要先寫 gold 題）· 36 個 PHANTOM · 115 個 UNLISTED／2,616 片段 · `docs/qa/session_log_maintenance.py` off-by-one（工具本身與歸檔檔 4 個孤懸 `end` 未修）· `source_registry` 276 live vs 服務 306 未對帳。 **【S233 只監察】** S232 的師生比例 footnote 會溢出到相鄰的幼稚園查詢（`hr_pay_adjust_kg` 第 2 格），現時令來源層意外判 PASS，未見害處；若出現在答案內容才處理。

⑤ **【S219 遺留，機器監察中】56 條無路由題仍全額付全庫代價。** 索引方向被 pgvector 版本擋住（Risks 1），已改為 `check_pgvector_release.py` 每週一監察，**出現 ≥0.8.4 才出聲；在它響之前這一項無事可做。**

⑪ **【S234 新增，只監察；S235 收窄】線上探測的真實當機路徑未驗。** (a)(b) 已於 S235 開工核實並移除（`live_probe` 排程 10-04 起連續 6 次 success；10-05 每日 QC 的 `qc_report.json` 帶 `attention`）。餘下 (c)：**真實當機路徑**與 `service-down` 標籤建立只在模擬下驗過，不要為了演練而弄壞生產，下次生產真的短暫當機時順手核對是否開了 Issue、恢復後是否自動關閉。

⑫ **【S235 新增】Option A executor 一次批准多份時，第二份起的 PR 必然衝突。** 成因與人手解法見 `## Risks / Blockers` 4 ③。根治方向（未設計、未量）：executor 逐份入庫時，每份都由**當下最新的 `origin/main`** 開分支，而不是接在上一份未壓縮的 commit 之上；或一次只處理一份、其餘留待下次運行。改動在 private repo `edb-knowledge-ops` 與本 repo 的 `dev/source/execute_ingest.py` 步驟 6，屬入庫寫入路徑，要先讀碼定案再改。

⑬ **【S238 新增】Freshness 清單其餘約 20 項未處理**（Issue #1）：17 個 HTML 索引／統計頁（`g04` 教職員批假指引、4 個 `stat_*`、9 個課程文件索引頁、`g32`／`g38`／`g11`）與 `music_p1_s6_2024`、`econ_sss_2025`、`pri_science_cert_course_list`、`debp_*` 三份、`g23`。S238 已處理 g19、supply、perf（入庫）與 sag（判定純重新匯出，不入庫）。處理完一批後要用 `check_freshness.py --ledger` write-sync 更新基線，**但它會重寫全部來源的 hash**——未處理的項目會一併被蓋過，所以要等清單清完或改為按來源 write-sync。

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

1. UTC date: 2026-11-09
2. Session ID: S247。「開工」（頂層轉 Draft）→ 清理 `dev/init_backup/` 任務（只讀審核先行）→「繼續」→「批准刪除＋加規則」→「開分支並開 PR」→「CI 綠後合併」→「收工」。
3. Completed（證據見 `## Validation / QC` S247）：
   - ✅ **刪除 26 份舊版／重複 `wiki_index.json` 備份**，釋放約 11.09 GB；保留 `20261101_195458_UTC`（與現用檔 SHA-256 相同）及其餘 43 個備份。
   - ✅ **備份保留規則**寫入 `dev/rules/safety.md` `## Project Rules`；PR #89 合併為 `82be06e`。
4. 生產改動：無（零 Supabase、零 flag、零部署）。
5. Carry-forward：未完成事項一律不在此列舉，全部歸入 `## Open Priorities`（S246 收工段）。

<!-- 本地邊界 marker（S232 由 S231 之前上移至此；S236 沿用）：令 completed-this-session 的抽取範圍只涵蓋最新一節 -->
<!-- ack:section:session-history -->
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

- **2026-11-09 S247 closeout reconciliation（init_backup 舊版 wiki_index 清理 ／ 備份保留規則 ／ PR #89 合併）：** 差異式更新：`Current Baseline` 4（S247 git 狀態）· `Validation / QC`（新增 S247 段於最前）· `User Environment` Git state · `Open Priorities`（加 S247 一句，Recommended next step 不變）· `Last Session Record`（S247；S246 原文改題為 `Previous Session Record (S246)`，內容不變）· 本段六個 S247 欄位 · `Handoff Sufficiency Check` · `Next Session Opening Message`。**未改**：`Current Baseline` 1、2、3、5、6、7 · `Risks / Blockers` · 其餘章節。`ack` marker 數改前改後一致。⚠️ 本節收工未完整讀取本檔全文（約 750 KB）：只讀了被改動的章節與 Open Priorities、Risks 開首、Current Baseline；未改動章節保持原位元組。
- **2026-11-08 S246 closeout reconciliation（Option 2 清單清空 ／ 109 行副本刪除 ／ PR #87 合併）：** 工作 commit 併入 PR #87 並已合併；收工另開分支 `s246-closeout`（由 `d6b18f6` 開出）。差異式更新：`Current Baseline` 1、2、4（前置 S246 句，舊文保留）· `Validation / QC` 新增 S246 七點於最前 · `User Environment` Git state · `Open Priorities` 前置 S246 段（新 Recommended next step）· `Last Session Record` 換 S246、S245 移入歷史 · 本節各欄 · `Handoff Sufficiency Check` · 開場訊息；`dev/PROJECT_INDEX.md` Branch / commit 由 S243 舊快照更新。其餘章節未動。
<!-- 歷史原文（S248 瘦身，2026-11-15）：`## State Reconciliation Check` S245 及以前的逐節敍述、各欄位 S246 及以前的舊行、S217 及以前的區塊 已一字不改移至 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`〔D1〕；開工毋須讀取，追查舊證據時才查。 -->

<!-- ack:field:stale-snapshots-left -->
- Stale snapshots left (S247): no — Current Baseline 4、User Environment Git state、PROJECT_INDEX Branch / commit 已改為 S247 實測（origin/main 82be06e、線上 20fd4a4）；S246 句標為原文。

<!-- ack:field:closeout-outcome -->
- Closeout outcome (S247): complete — 交接、log、DOC_SYNC_REGISTRY、PROJECT_INDEX 已寫入並讀回；開場鏡像重生並核對；closeout-status 為最終讀回。

<!-- ack:field:project-required-persistence -->
- Project-required persistence (S247): complete — 工作 commit 已隨 PR #89 合併入 `main`（`82be06e`）；收工 commit 推上 `s247-closeout` 並開 PR，只改治理文件，合併待 Leonard 指示，毋須部署；刪除的備份屬本機 gitignored 檔，無需 git 持久化。

<!-- ack:field:recommended-next-step-explicit -->
- Recommended next step is explicit and reasoned (S247): yes — `## Open Priorities` 開首 S247 句沿用 S246 段：退役 `EDBC_9_2019_E`，理由見 S246 段；執行前再確認。

<!-- ack:field:next-ai-can-continue -->
- Next AI can continue (S247): yes — 由 `AGENTS.md`、本檔 `## Open Priorities` S247／S246 段與 S238 原文的退役步驟即可續做，證據見 `## Handoff Sufficiency Check` 的 Reconstruction evidence。

<!-- ack:field:opening-message-matches-current-state -->
- Opening message matches current state (S247): yes — 開場訊息記 origin/main 82be06e、線上 20fd4a4、17,074／315、footnote 177、init_backup 已清理、下一步退役 EDBC_9_2019_E，與 `## Open Priorities` 及 `## Current Baseline` 一致。

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

Answer: yes — S247 收工覆核（origin/main 82be06e、線上 20fd4a4；Supabase 17,074／315；footnote 177；init_backup 已清理）；以下 S246 覆核內容仍適用。S246 收工覆核（origin/main d6b18f6、線上 20fd4a4；Supabase 17,074／315；footnote 177；清單 0 條、109 行副本已刪）。下一個 agent 只讀 `AGENTS.md` ＋ 本檔即可續做：現況（`## Current Baseline` 1、2、4）、已做與證據（`## Validation / QC` S246）、下一步（`## Open Priorities` 開首 S246 段）、邊界（`## User Environment`：合併、DDL、Supabase 寫入或刪除、外部模型批量都要 Leonard 明示）。

Reconstruction evidence: **S247 補充**：本節是獨立小任務（本機備份清理，已完成，`## Validation / QC` S247、`## Last Session Record`），不改父目標與續做點；規則見 `dev/rules/safety.md` `## Project Rules`。以下 S246 證據仍適用。 **父目標與消費者**：Leonard 要系統各環節自行運作、少介入（S243）；Channel A 退役與 455 條清單已於 S246 完結（`## Current Baseline` 1），消費者是 Leonard 與用戶搜尋。**確切續做點**：`## Open Priorities` 開首 S246 段 —— 退役 `EDBC_9_2019_E`（S238 已批准未執行，執行前再確認），步驟寫在同節 S238 原文（備份 → DELETE → `live_display_sync(17074, 17072)` → `update_log.json`）。**已做、不要重做**：清單清空、109 行備份與刪除、PR #87 合併、舊分支刪除（`## Validation / QC` S246）。**已否決**：把 footnote 來源登記入 `source_registry.json`（按設計不登記，S246 (6)）；租金收入不以 `footnote_fn_tips_rental_40pct` 為出處（未提學校及班級津貼）。**仍待 Leonard 的產品決定**：粵語問句改寫、時限段落交退役機制、「全校」角色標籤、`FEATURE_SUBJECT_CHECK`、Kit 0.4.4 升級。**必讀來源**：`dev/source/execute_ingest.py` 的 `live_display_sync`／`live_total_count`；Risks 3（冷啟動首查詢會 `57014`，量度前先暖機）。**權限邊界**：Supabase 寫入或刪除、批量 Jev／OpenAI 呼叫、合併 PR 皆須 Leonard 明示；搜尋內容不得公開。

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

--- 專案狀態（S247 收工, 2026-11-09）---

平台 v3.3.16；Supabase 17,074 chunks（315 來源；footnote_curated 177）；EDB 指引書庫 182 份；guidelines.json 公開端點 151 份（_meta 2.6.2）。
Channel A 退役已完結：內部清單 dev/knowledge/channel_a_option2_queue.json 已清空（resolved 289、dropped 166、餘 0）；
Supabase 109 條 approved_fact（role_facts_*）已備份後刪除（備份在本機 dev/init_backup/20261108_122028_UTC/）。
Agent Handoff Kit v0.4.3（npm 已有 0.4.4，未升級）。
origin/main = 82be06e（PR #89 已合併）；線上 /health commit = 20fd4a4（開工以 /health 核實）。
本節收工分支 s247-closeout（只改治理文件）。#70 仍開著。
Render：無 OPENAI_MODEL、無 JUDGE_MODEL → 碼內預設 gpt-6-luna＋reasoning.effort none。
FEATURE_ROUTE_FIRST_SEARCH=1、FEATURE_CIRCULAR_NUMBER_LOOKUP=1；FEATURE_QUERY_FUSION、FEATURE_SUBJECT_CHECK 未設＝關閉。
public.search_log 記錄真實搜尋 180 日（🔴 搜尋內容不得公開或入 git）。

🟢 S247 做完（不用重做）：
   · dev/init_backup/ 刪除 26 份舊版／重複 wiki_index.json 備份（約 11.09 GB），保留 20261101_195458_UTC；
     保留規則在 dev/rules/safety.md「Project Rules」（wiki_index 備份只留最新一份；Supabase 刪除前備份必須保留）。
🟢 S246 做完（不用重做）：
   · 租金收入以 g02《財務管理指引》第 15 頁按原文修正，清單清空。
   · 109 行 approved_fact 全欄位備份 → 經 Leonard 批准刪除 → 公開數字 17,074，線上已讀回。
   · PR #87 合併；舊分支 s244-option2-round1 已刪；edbc29_2024_teacher_training、edb_byod_page 按設計不登記 source_registry。

🚀 下一步：
   ① 退役 EDBC_9_2019_E（2 段 footnote_curated；已被 EDBC 4/2026 取代；S238 已批准未執行 —— 執行前先向 Leonard 再確認）：
      select=* 匯出備份 → DELETE → live_display_sync(17074, 17072) → update_log.json。
   ② 本節收工 PR 待 Leonard 指示合併。
   ③ 待決定：S244 三條 footnote 粵語問句是否改寫；語料庫時限段落是否交 check_expiry；app.html「全校」角色標籤；
      文件標註四項重開條件；搜尋紀錄加拒答原因（DDL 待批）；FEATURE_SUBJECT_CHECK；Kit 0.4.4 升級；定期系統更新檢查約 11-29 到期。

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
（應為 20fd4a4 或之後改 backend 的 commit；cache_b.footnote 應為 177）+ git fetch 後比對分支與 origin/main、gh pr list
+ Supabase live count 應為 17,074 + check_registry_drift --check --ledger <scratchpad> 的 ZOMBIE／SERIES_UNMONITORED／UNMANAGED 應為 0
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
