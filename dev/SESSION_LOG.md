# Session Log
<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->

> **Handoff role**: This log is the trace-back / audit trail layer. Handoff capability rests on `dev/SESSION_HANDOFF.md`. The next AI session can continue by reading `AGENTS.md` + `dev/SESSION_HANDOFF.md` + `dev/PROJECT_INDEX.md` + needed rule packs; reading this log is not required for continuity. Each closeout must run the maintenance trigger check per `AGENTS.md` `## Closeout And Handoff` step 11 (R-010 SESSION_LOG handoff-role discipline): N=1–3 keep full, N=4–10 may short-index after absorbed-source check when triggered, N=11+ archive into `dev/SESSION_LOG_archive/`.

Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

This log carries recent evidence, not current state. Put the current objective, next action, risks, and workspace identity in `dev/SESSION_HANDOFF.md`.

Keep recent entries concise. If older entries no longer affect the next action and the maintenance trigger check says cleanup is due, reduce them to short dated indexes that point to the durable source of truth. Archive long error output, validation detail, or research trails only when triggered; do not create an archive directory by default.

Before closeout, record whether older log detail was kept, summarized, or archived, and whether the maintenance trigger check was no-op, triggered, or backstop-driven. Do not remove validation evidence or unresolved risks. The full opening message never belongs in this log.

<!-- ack:section:session-log-entry-template -->

## Entry Template

````markdown
<!-- ack:log-entry:start -->
## <YYYY-MM-DD> — <short session title>

- **ID:** <agent_or_session_id>
- **Summary:** <one sentence>
- **Changed:** <files changed, or none>
- **Done:** <work completed this session>
- **QC:** <checks run and results, or why not run>
- **Evidence disposition:** <one-time only / kept as recent trace evidence / absorbed into handoff / indexed in PROJECT_INDEX / promoted to PROJECT_DECISIONS / promoted to rule pack>
- **Sync:** <doc/external sync status>
- **Pending:** <next work>
- **Risks:** <known risks or none>
- **Log maintenance:** <trigger check result; full maintenance action if triggered, otherwise no-op reason>
- **Opening-message mirror:** <regenerated and verified / blocked; full text omitted by design>
<!-- ack:log-entry:end -->
````

---

<!-- ack:log-entry:start -->

## 2026-09-24 Session 232 — GitHub 電郵收窄；GN10 以 footnote 修好，但交接寫下的 footnote 前提本身是錯的

- **ID:** S232
- **Summary:** 由頂層 root「開工」redirect 入 Draft，起手探針全綠。Leonard 逐步指示：GitHub 電郵太多 → 只留批准候選與最重要電郵 → 警報 @mention → GN10 走路線甲 → 寫入生產與兩次合成（「全做」）→ 收工。#32、#33、#34 由 Leonard 在網頁合併；收工 PR #35。
- **Changed:** `.github/workflows/monitor_watchdog.yml`／`backend_build_check.yml`（@mention）· 新 `dev/ingest_s232_kg_ratio_footnote.py` · `CHANGELOG.md` · 片段數同步七檔（`app.html`、`index.html`、`README.md`、`K1_API_SPEC.md`、`knowledge.json`、`role_facts.json`、`dev/knowledge/role_facts.json`）· `dev/source/2026-09-24_s232_*.json` 四份 · 治理文件。**生產 Supabase +1 行**。
- **Done:**
  - **電郵**：查明大宗來源是 repo 層 push 電郵（每次 push 一封，無 webhook、無 API 可讀）；Leonard 改帳戶設定（Watching 關電郵、Actions 只報失敗等）並清空四個 repo 的 push 電郵。
  - **#33**：看門狗與 build gate 的警報 issue 加 @mention（照 S191 做法）。
  - **GN10**：`synthesize:false` 看生產窗 —— 三條相鄰 footnote 在頂、真正比例的 vault 片段因路由到 `g29` 而取不回。對庫內原文寫新 footnote（1:15 → 1:11；通告 26/2003 每 15 名一名當值），INSPECT before/after 寫入（17,006 → 17,007、footnote 180 → 181）。等 Render 休眠重啟後驗收。
- **Fix Record:**
  - **Problem:** S231 交接為路線甲寫下的 footnote 內容是「普通幼稚園無規定師生比例、只有班額上限」。**Root Cause:** 該前提寫入交接時未對原文。**Fix:** 動手前逐條查 `kg_admin_guide_2026`／`kg_operation_manual_2026` 片段，發現原文相反，改以原文為準並在交接記錄。**Verification:** 新 footnote 每句都能在庫內片段找到對應原文。
  - **Problem:** 入庫後生產不會自動載入新 footnote。**Root Cause:** `_footnoteCache` 無 TTL，合併 PR 不會重新部署（三個 PR 都不動 `backend/`）。**Fix:** 21 分鐘不發請求讓免費方案休眠。**Verification:** `/health` `started_at` 17:37:51Z、`cache_b.footnote` 181。
- **QC:** 兩個 workflow YAML 可解析、內嵌腳本 `node --check` 通過、build gate 綠 · 入庫腳本 `--self-test`（embed 格式 cos 1.0000）· 生產窗口 6 條查詢（新 footnote 在 3 條排第 0、3 條排第 1）· `synthesize:true` 2 次皆答 1:11 · `footnote_lead_probe` before 26/27・4/13 → after 26/27・4/13，失去 lead 0、errors 0 · `footnote_lead_probe --self-test` PASS。**未跑**：185 題 gold（已列為下一步）。
- **Evidence disposition:** 四份 artifact 入 repo 為本修法的驗收證據；結論摘入交接 `## Validation / QC` S232；入庫腳本登記入 `dev/PROJECT_INDEX.md`。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S232 列 · 片段數七檔已同步 · 凍結合約零接觸 · 平台版本不變。
- **Pending:** 重跑 185 題 gold → 路線乙；log 維護兩套標準整合；收工 PR #35 待合併。
- **Risks:** 對象錯置這一類（D01／FT06）未修；gold 預計禁引 +1；警報 @mention 未經真實觸發驗證。
- **Log maintenance:** 寫入本條後主 log 為 5 條；`docs/qa/session_log_maintenance.py --check` 報 `line_count=169`、`entry_count=5`、`trigger=False`（§4a 不觸發；Kit 核心 ≥11 條亦未達）。`## Confirmed Decisions` 類章節未達 30 條；距上次全面維護未滿 10 次收工；本節無架構取捨需寫入 `PROJECT_DECISIONS.md`。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並讀回，內容相等（64 行／5,345 bytes）；全文依設計不入 log。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-24 Session 231 — 「入口和路由」沒有重複，但有三個分支；補回的判官基線與 S211 逐項相同，而那條「判官從不服務」的前提早已失效，實測到的是 GN10 在生產答錯

- **ID:** S231（跨 09-23／09-24 兩日）
- **Summary:** 由「開工」起手，Leonard 逐步指示：盤點「入口和路由」有沒有重複／分支 → 做第 1–4 項 → 同意（含本機 CORS）→ 做判官驗收基線 → 查 D01 前提 → 改過時註釋 → 收工。五個 PR（#26、#28–#31）全部由 Leonard 在 GitHub 網頁合併並部署核實。
- **Changed:** `app.html`（`BACKEND_URL`、`fetchUsageTotal()`、`PLATFORM_VERSION` 3.3.9）· `q.html`／`t-purchase.html`（註釋）· 刪 root `main` · `README.md` · `CHANGELOG.md` · `backend/src/server.ts`（本機 CORS）· `backend/src/api/searchChannelB.ts`（純註釋）· `dev/source/judge_runs/2026-09-24_s231_shipped_41mini.json`（新）· `dev/source/JUDGE_PROMPT_FINDINGS.md` · `dev/CODEBASE_CONTEXT.md` · `dev/PROJECT_INDEX.md` · `dev/DOC_SYNC_REGISTRY.md` · `dev/SESSION_HANDOFF.md` · `START_NEXT_SESSION_PROMPT.txt`
- **Done:**
  - **盤點**：前端六個入口頁、後端 12 條路由集中一個分派器 —— 無重複登記、無衝突、無網站副本。找到的是分支：後端網址寫了五次（一個死常數）、用量請求兩處各寫一份、平台介紹桌面／手機兩條路、手機無文件標註入口、舊 hash 轉址只在桌面、三條介面已退役但仍公開的路由。
  - **#28**：網址合一、用量共用、刪 `main`、註釋對正；v3.3.9。**#29**：非 Render 環境放行 localhost。**#30**：判官基線 artifact。**#31**：更正 S200 過時註釋。
  - **判官基線**：`gpt-4.1-mini` 凍結集 31/33、12/12、19/21（D01、GN10）、33/35 —— 與 S211 CHANGELOG 所記逐項相同。
  - **D01 前提**：程式碼註釋已證 S201 拆了 footnote bypass；生產各跑兩次：D01 無錯置，**GN10 一次答「1:30／1:14」錯置、一次正確拒答**。
- **Fix Record:**
  - **Problem:** 以為本機預覽的搜尋「連到生產」，改成連本機會令本機搜尋失效。**Root Cause:** 沒先測 —— 實測改動前後本機預覽連任何後端都被 CORS 擋（後端只回兩個生產網域；`.env` 的 `CORS_ORIGIN=*` 被當字面值比對）。**Fix:** CHANGELOG 照實改寫，另開 #29 修 CORS（只限非 Render）。**Verification:** 本機四個 origin 逐一測；合併後生產對 localhost 仍回生產網域。
  - **Problem:** `bump_version.py patch` 看似升版工具。**Root Cause:** 它升的是資料合約版本，`--dry-run` 顯示會改 `knowledge.json`／`role_facts.json`／`guidelines.json`。**Fix:** 不用它，手改三處；規則寫入交接 `Current Baseline` 1。**Verification:** 凍結合約 `_meta` 維持 2.3.0／2.6.2。
  - **Problem:** AI 的 `gh pr merge` 被 auto mode 權限閘擋下。**Fix:** 不繞過，交 Leonard 在網頁合併並逐步說明。**Verification:** 五個 PR 皆 MERGED，served 3.3.9、`/health` `f712172`。
- **QC:** 本機 1280px 預覽（v3.3.9 編譯、stub 用量 qa→about→qa 只 1 次請求、文件標註請求走 `BACKEND_URL`、主控台只有 CORS 錯誤）· `npm run check` 0（兩次）· `judge_acceptance` `--self-test` 0／`--check-parity` OK／`--plumbing-check` OK · 五個 PR 的 `build-gate` 全綠 · 收工探針：served 3.3.9、`/health` `f712172`、`backend` 零落後、Supabase 17,006、`check_registry_drift` 三項 0。
- **Evidence disposition:** 判官 run 檔保留為基線；GN10／D01 生產實測的答案原文摘入 `dev/SESSION_HANDOFF.md` `## Validation / QC` S231 第 5 點（原始回應只存於 scratchpad，未入 repo）。入口盤點的四項未決分支升入 `## Open Priorities` ③。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S231 十三列 · `dev/PROJECT_INDEX.md` judge harness 列更正 · `dev/CODEBASE_CONTEXT.md` app.html 條目 · `CHANGELOG.md`／README · 凍結合約零接觸。
- **Pending:** Leonard 選定 GN10 型錯置的處理路線（甲：curated footnote 個案修；乙：非提示式對象核對機制）；log 維護兩套標準整合；收工 PR 待合併。
- **Risks:** GN10 型錯置在生產非決定性出現；判官基線只跑一次，未達 ≥3 runs。
- **Log maintenance:** 寫入本條後主 log 為 **12 條**。`docs/qa/session_log_maintenance.py --check` 報 **`line_count=418`、`trigger=True`**（§4a 行數閘），故依 §4a 強制執行 `--apply`：**418 → 148 行、12 → 4 條，8 條（S220–S227）搬入 `dev/archive/SESSION_LOG_2026_Q3.md`**（append，未覆寫）。事前備份、事後逐行核對：12 個條目標題全數尋回、非標記內容 **0 行遺失**。**S224 記載的 off-by-one 再次出現**：主檔尾留下一個孤立 `ack:log-entry:start`，已刪（主檔改後 5/5 平衡）；歸檔檔本次 +8/+8，其既有的 4 個失衡照 S224 判斷不動。工具回報 `latest entry prompt block ok=False` —— §4a 硬規則 3 要求最新條目保留開場白全文，而 Kit 核心與本檔頭寫明「開場白全文不屬於 log」，屬同一組並存標準的另一處衝突，本節照 Kit 做法不寫入、記錄於此。重跑 `--check`：`line_count=146`、`trigger=False`。S230 記錄的兩套觸發標準衝突**本節仍未整合**；衝突已在交接 `Open Priorities`「次序」段列為治理側第一件維護工作。`## Confirmed Decisions` 類章節未達 30 條；距上次全面維護未滿 10 次收工；本節無架構取捨需寫入 `PROJECT_DECISIONS.md`。
- **Opening-message mirror:** 已由 `dev/SESSION_HANDOFF.md` 的 fenced 區塊重新產生 `START_NEXT_SESSION_PROMPT.txt` 並讀回逐字核對。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-22 Session 230 — 用 stub 判官量了三次「失去捷徑」，錯讀成「失去答案」；換真判官之後結論倒轉，然後兩個量度工具自己出錯，最後一個「新缺陷」是我沒讀 CODEBASE_CONTEXT

- **ID:** `Claude_20260921_1100` — S230（跨 09-21／09-22 兩日）
- **Summary:** 由「開工」起手，Leonard 逐步授權：合併 S228 的 PR → 收乾 S229 遺下的半完成狀態 → 定案並量度 S229 提的「換訊號」候選 → 補完四項出貨先決條件 → 奉命先修判官。淨結果：**候選由「不出貨」翻成「條件性可出貨」再收緊為疊加式設計**，而出貨仍卡在一個有前科的判官弱點。本節三度自我更正，其中兩次是自造的量度工具出錯，一次是來源優先次序倒轉。
- **Changed:** `backend/src/api/searchChannelB.ts`（`FEATURE_VAULT_GATE_RAWVEC`，預設關閉；第二版改為**疊加**而非取代）· `backend/src/lib/wikiRepository.ts`（`bareCosineForChunk()`，4 位小數對齊校準尺）· `backend/scripts/_s230_{gateSignalAB,leadOverlap,bypassCensus,judgeTakeover,readDeclines,judgeModelProbe}.ts`（新，六支）· `dev/_s230_relabel.py`（新）· `dev/source/judge_probe.py`＋`dev/source/judge_acceptance.py`（只加範圍說明與執行期警告，零行為、零預設改動）· `dev/DOC_SYNC_CHECKLIST.md`（row 41 驗收工具改指新探針）· `dev/SESSION_LOG.md`（補寫 S229 條）· `dev/SESSION_HANDOFF.md` · `dev/PROJECT_INDEX.md` · `dev/DOC_SYNC_REGISTRY.md` · `dev/source/eval_runs/2026-09-2{1,2}_s230_*`（七份）· `dev/source/2026-09-22_s230_footnote_lead.json`
- **Done:**
  - **S229 收乾**：它改了交接檔內容卻從未收工（無 log 條目、`Last Session Record` 停在 S228、四項改動未 commit）。補寫 S229 log 條目並明示是補寫、事實來源是它留下的實物；重跑 `_s229_scaleOffset.ts` 獨立覆核其數字（它沒存過原始輸出）—— A 尺 CLASS_B 上限 0.6321／CLASS_C 下限 0.6241 逐項重現 S195 原數。
  - **兩個 PR 合併並部署核實**：#22（S228，`2e803ec`）與 #23（本節候選與量度，`2678ea2`）。生產行為核實 S228 的 `kg_admin` 路由修正已生效（`幼稚園搬遷津貼` 現由 `edbcm144_2026` @ 0.7111 領先，整窗轉為幼稚園行政語料）。
  - **候選實作與量度**：把 vault judge-bypass 由讀「展開後＋路由收窄」分數改為讀同一片段對裸查詢向量的餘弦，`0.70` 一個位不動。instrument 先自我驗證：SQL 本身 `round(…,4)`，本機餘弦取 4 位小數後與 RPC **40/40 逐條相同**。
  - **24 條校準集**：bypass 5→0，只換到一條正確攔截，代價三個正控加一條已核實正確的 bypass —— **按預先定案失敗**。根因結構性：24 條在校準尺上最高只有 0.6457，閘卻設在 0.70，所以「放回校準尺」等於「移除 bypass」。
  - **185 題 gold 人口普查**（新工具，單 arm 足夠且該推導先對兩 arm 的 24 條逐條驗證 24/24）：真實作用面是 **59/185（31.9%）**。按 gold 真值拆：`FALSE_BYPASS` 5／`WRONG_PASSAGE` 44／`SOUND` 10。並排除兩個候選規則：詞面零重疊只攔 1/59、對五條 `FALSE_BYPASS` 全部失效。
  - **判官接手測試**（Leonard 明示批准 59 次，實用 53 次，errors 0）：**結論倒轉**。被攔的 `SOUND` 判官照樣答、`FALSE_BYPASS` 4/5 轉為拒答，預先定案全部達標。
  - **四項出貨先決條件**：`footnote_lead_probe` 已跑（正控 26/27、零 LLM，並證明本候選動不到它的觀測量）· `judge_probe.py` 改為講清角色而非重寫、row 41 驗收工具改指新探針 · 14 條拒答與 2 條新開 bypass 逐條讀窗 · 延遲實測（中位 288ms／p90 639ms）。
  - **按延遲收緊候選**：旗標由「取代舊閘」改為「疊加」（只在 applied ≥0.70 才做額外讀取）—— 額外讀取由 168 條降至 58（91%→31%），且候選**再也不可能新開 bypass**。全 185 條確認：新開 0、保住 6，與 53 次呼叫吻合。
- **Fix Record:**
  - **Problem:** 三批量度都判「不出貨」，理由是候選會令查詢失去 bypass。**Root Cause:** 三支探針都用 stub 判官（刻意如此，為隔離閘），於是量到的是「失去捷徑」而我讀成「失去答案」。**Fix:** 用生產判官模型實測 53 次。**Verification:** 被攔的七條 `SOUND` 判官 7/7 照樣答，其中六條是二三個 token 的短查詢 —— 普查推論的「短查詢誤傷」在答案層並未實現。
  - **Problem:** `SOUND`／`WRONG_PASSAGE` 的分界（＝預先定案的讀數依據）可能量錯。**Root Cause:** 探針用原文子字串比對，而本專案單一口徑是 `squeeze(fold(s))`（NFKC＋刪空白）；`家長校董 點選` 的答案逐字在第 0 格，只因 gold 寫半形 `(PTA)` 而片段是全形 `（PTA）` 就被判成無答案。**Fix:** 改用本專案口徑並加紅測，用已有判官結果重新推導（零新呼叫）。**Verification:** 5 條由 `WRONG_PASSAGE` 移入 `SOUND`（全 gold 原文比對漏 25 條命中）；預先定案仍全部達標，但 `SOUND` 拒答由 0 變 1，**距「≥2 即不出貨」只差一條**。
  - **Problem:** 普查重跑整個崩潰、零輸出。**Root Cause:** 取裸查詢向量那個 embedding 呼叫放在 try/catch 之外。**Fix:** 加單次重試並把整條 item 包住。**Verification:** errors 由 2 降至 0，`bypass_before` 兩次都是 59。
  - **Problem:** 曾把「判官驗收自 S211 起量錯模型／D01 假答案屬未報缺陷／要 Leonard 去 Render 查 `JUDGE_MODEL`」寫成新發現，三項皆錯。**Root Cause:** 只讀了 `judge_acceptance.py` 的檔內註釋（§2 第 5 級來源）就下結論，未查 `dev/CODEBASE_CONTEXT.md`（第 3 級）—— **來源優先次序倒轉**；而該註釋本身確實過時，所以看起來像可信現況。**Fix:** 在 Risks 與 Validation 兩處逐項標明**收回**（不靜靜改掉，因為曾據此要求 Leonard 行動），harness 檔頭改為準確版本。**Verification:** `CHANGELOG.md` 記載 S211 確實用凍結集量過 `gpt-4.1-mini`（主集 31/33 打平、相同的兩個 false answer、無新增虛答）；`CODEBASE_CONTEXT.md` 明文記載 Render 不需條目、程式預設即在跑者。
- **QC:** `npm run check` 0 · `npm run build` 0 · `regression:grounded` 48/48 · `route_regression` 63/63 · 五支探針 self-test 全綠（每支一條紅測）· `footnote_lead_probe --self-test` PASS · `judge_acceptance --self-test` 0 failure · `session_log_maintenance --check` trigger=False · `workspace-health` verified／dirty:no。**未跑**：`_s227_rubricJudge` 的 gold before→after（主指標已足以判定，花約 150 次呼叫量一個不出貨的候選是浪費，已記錄為刻意略去）；`judge_acceptance` 對 `gpt-4.1-mini` 的一次 run（35 次呼叫，下節第一件事）。
- **Evidence disposition:** 七份 `eval_runs` artifact ＋ footnote lead 一份保留為近期證據；結論與判讀已抄入 `dev/SESSION_HANDOFF.md` `## Validation / QC` S230 八批；六支探針與一支 Python 分析器已登記 `dev/PROJECT_INDEX.md`；「判官驗收工具由 `judge_probe.py` 改為新兩支」已升為 `dev/DOC_SYNC_CHECKLIST.md` row 41 的常設要求；「來源優先次序倒轉」這條教訓寫在本條 Fix Record 與 Risks 首條，**按 §8b 暫不升為新規則**（§2 已有該規則，是沒遵守而非缺失）。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` 已記本節十二列狀態 · `dev/PROJECT_INDEX.md` Local QC Commands 新增七列 · `dev/DOC_SYNC_CHECKLIST.md` row 41 已改寫 · `dev/CODEBASE_CONTEXT.md` **not_applicable**（零 tech stack／目錄／build／External Services／Key Decisions 改動；`bareCosineForChunk()` 沿用既有 Supabase REST 形狀）· `guidelines.json`／`knowledge.json` 凍結合約零接觸 · 平台版本零改動（`app.html` 未改）。
- **Pending:** 用 `gpt-4.1-mini` 跑一次 `judge_acceptance.py`（35 次呼叫）把 S211 那組只存在於 CHANGELOG 散文的基線補回 artifact；然後才談那條判官錯判或啟用旗標。**PR [#26](https://github.com/Leonard-Wong-Git/edb-knowledge/pull/26) 未合併**，本節的交接狀態在該分支上。
- **Risks:** 旗標生產未設＝行為不變。候選的殘留代價：1 條 `SOUND` 拒答（成因是判官判錯，距不出貨紅線一條）、1 條 `FALSE_BYPASS` 判官仍判「能」、延遲每查詢中位 +288ms（僅 31% 查詢）。
- **Log maintenance:** 🔴 **兩套標準衝突，本節照契約記錄而不自行決定。** 寫入本條之後 `session_log_maintenance --check` 報 **`line_count=393 entry_count=11`、`trigger=False`** —— 本專案 `AGENTS.md` §4a 的機械閘（>400 行 或 最舊條目 >30 日）**未觸發**，但 Kit 核心 `dev/rules/closeout.md` 的維護規則寫「主 log 達 **11 條**即觸發歸檔」，**該條已觸發**。兩者的歸檔目標亦不同（§4a：`dev/archive/SESSION_LOG_YYYY_QN.md`，已存在 `SESSION_LOG_2026_Q3.md`；Kit：`dev/SESSION_LOG_archive/archive_<batch>_...` ＋ `INDEX.md`）。**本節不執行歸檔**，理由三項：(1) §4a 明文把該腳本定為執行閘而它報未觸發；(2) 393 行遠低於兩套的行數門檻（400／1500）；(3) 在長 session 末端重組 log 屬結構性改動，且會在兩個並存的歸檔目錄之間造成第三種狀態。**依 `AGENTS.md` §5「若兩個 pack 衝突，取較安全而可驗證的路徑，並在收工記錄該衝突」處理。下一節第一件維護工作：決定本專案採用哪一套（建議把 §4a 的門檻與 Kit 的 11 條規則整合為單一定義，屬 §3b 整合而非疊加）。** `## Confirmed Decisions` 類章節未達 30 條；距上次全面維護未滿 10 次收工。本節一條跨節累積模式（「用 stub 判官量出的結論不可讀成答案層結論」）已寫入本條 Fix Record 與 `dev/SESSION_HANDOFF.md` 的量度紀律，未另立 `PROJECT_DECISIONS.md` 條目。
- **Opening-message mirror:** 已由 `dev/SESSION_HANDOFF.md` 的 fenced 區塊重新產生 `START_NEXT_SESSION_PROMPT.txt` 並讀回逐字核對。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-20 Session 229 — 那個門檻不是被展開詞抬高了，是由頭到尾校錯了尺

> ⚠️ **本條由 S230（2026-09-21）補寫。** S229 當日改了 `dev/SESSION_HANDOFF.md` 與 `dev/PROJECT_INDEX.md`、建了兩支探針，但**從未收工**：沒有本條目、沒有 `State Reconciliation Check` 條目、`Last Session Record` 仍停在 S228、開場白區塊與 `START_NEXT_SESSION_PROMPT.txt` 亦仍是 S228 版本，四項改動全部未 commit。本條的事實來源是 S229 留下的實物（交接檔 `## Open Priorities` ② 的 S229 段落、`dev/PROJECT_INDEX.md` 兩列新登記、`backend/scripts/_s229_{scaleOffset,leadDetail}.ts`），**不是憑記憶重構**；S229 沒有把任何一次 run 的原始輸出存檔，所以下列數字在本條寫成時只有交接檔一個來源，S230 已重跑 `_s229_scaleOffset.ts` 獨立覆核（結果見 S230 條）。

- **ID:** `Claude_20260920_xxxx` — S229（實際時分不可考，S229 未記）
- **Summary:** 追 S228 交下來的 OP②(c)「重校 `VAULT_LEAD_SCORE` 0.70」，結果把這條路本身否決了 —— 0.70 不是被展開詞抬高了要調回低，而是**校準尺與應用尺根本是兩把尺**：定這個數的 `dev/source/judge_probe.py` embed 裸查詢兼打全庫，而 0.70 套用在「展開後 ＋ 路由收窄」的 `mainSearchLead.score` 上。185 條 gold 之中 97 條是路由題，兩尺不同。
- **Changed:** `backend/scripts/_s229_scaleOffset.ts`（新）· `backend/scripts/_s229_leadDetail.ts`（新）· `dev/SESSION_HANDOFF.md`（`## Open Priorities` ② 加入 S229 段落並更正 S228 那條硬紀律的適用範圍）· `dev/PROJECT_INDEX.md`（兩列新登記）。**四項皆未 commit，由 S230 接手。**
- **Done:**
  - **三把尺同批量度**（`_s229_scaleOffset.ts`，用生產 `searchChannelB`、零重寫、`FEATURE_ROUTE_FIRST_SEARCH=1`）：**A 裸＋全庫**（＝校準尺）／**B 裸＋路由**／**C 展開＋路由**（＝應用尺），對象是 `judge_probe.py` 當初定門檻那 24 條校準 query。**儀器自我驗證通過**：A 重現 S195 原數（CLASS_B 上限 0.6321 對 0.632、CLASS_C 下限 0.6241 對 0.624）。
  - **歸因分離**：路由本身**不抬分**（A→B 為 0 至 −0.067），抬分的是展開（B→C 最多 **+0.3226**）。兩個分佈的重疊由 **0.0080 擴大到 0.0817，大十倍**；CLASS_B 敵意題在應用尺上有 **2 條 ≥ 0.70**，即合成閘被跳過。
  - **逐條開窗核實**（`_s229_leadDetail.ts`，判 bypass 有無真的觸發，因為 `scaleOffset` 量的是窗內最高分 vault_extract 而閘測的是 `mainSearchLead`，過 0.70 是必要非充分條件）：**「校巴司機最低工資係幾多」@ 0.7098 是真缺口** —— 窗內四個來源共 31 片段，`工資`／`薪` 命中 0，全庫 `最低工資` 只有 10 條且全部是經濟／通識科課程文件，判官被跳過而合成器手上零工資內容，正是 0.70 當初要擋的 S177 那一類。**「老師病假連續請幾耐先要交醫生紙」@ 0.7003 則是探針標錯** —— `g04` 原文有「常額教師如申請病假超逾兩天，必須出示有效的醫生證明書」，領先那一片就是答案片段，bypass 觸發是正確行為；`judge_probe.py` 把它列入 CLASS_B（語料無答案）是錯的。
  - **更正 S228 立的硬紀律的適用範圍**：只有 `VAULT_LEAD_SCORE` 與 `min_score` 吃「展開後＋路由收窄」向量；`SPOTLIGHT_LEAD_SCORE` 與兩個 `FOOTNOTE_*` 門檻看的是裸查詢向量（`searchChannelB.ts:1756` 的 `rawVec`），**任何展開側改動都動不到它們**。證據：S228 十個 arm 共 1,667 筆 before／after 記錄，裸查詢字串兩側逐筆同一個，0 筆例外。
- **Fix Record:**
  - **Problem:** S228 交下來的 OP②(c) 叫下一節「重校 0.70」。**Root Cause:** S228 從分數分佈推斷門檻被展開詞抬高，但沒有查這個數當初是用哪把尺校出來的。**Fix:** 不重校 —— 改為換訊號（把閘放回它被校準的那把尺）。**Verification:** 三把尺實測，A 重現 S195 原數，路由不抬分、展開抬分，兩分佈在應用尺上重疊大十倍；共用經驗庫 `self-authored-probe-false-confidence` 卡尾段寫明「兩分佈重疊時調 threshold 係死路，要換訊號或換判斷器」。
- **QC:** `_s229_scaleOffset.ts` 的自我驗證（A 尺重現 S195 兩個邊界值）· `_s229_leadDetail.ts` 逐條開窗覆核兩條過線題。**未跑** `npm run check`／`route_regression`（本節零生產碼改動，但亦未記錄此判斷）。
- **Evidence disposition:** ⚠️ **原始 run 輸出未存檔** —— S229 的數字當時只存在於交接檔 `## Open Priorities` ② 的散文內。S230 已重跑並把 artifact 存入 `dev/source/eval_runs/`，此後以該檔為準。兩支探針的存在理由與用法已登記在 `dev/PROJECT_INDEX.md`。
- **Sync:** ⚠️ **S229 未做** —— `dev/DOC_SYNC_REGISTRY.md` 無 S229 列，`dev/DOC_SYNC_CHECKLIST.md`「Synthesis 前置閘改動」row 要求的 `judge_probe.py` 驗收亦未跑（S229 自己指出該工具現況跑出來的是校準尺的數，要先修）。由 S230 補。
- **Pending:** 換訊號的具體做法（S229 提出、未實作、未量）：`rawVec` 已為每條查詢 embed 好，把 vault 閘改為測「領先片段對裸查詢向量的 cosine」，即把閘放回被校準的那把尺上。屬 `dev/DOC_SYNC_CHECKLIST.md` 自己一個 row，要先定案再量 before→after。
- **Risks:** 本節零生產碼改動、零 Supabase 寫入、零部署。真正的風險是它留下的**半落地狀態**：交接檔內容已更新而敘事層（Last Session Record／開場白／鏡像檔）仍是 S228，下一個 agent 會讀到互相矛盾的兩段。已由 S230 收乾。
- **Log maintenance:** 補寫，不觸發維護檢查（由 S230 在本節收工時一併執行）。
- **Opening-message mirror:** ⚠️ S229 未產生；S230 收工時重新產生。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-16 Session 228 — 把三次逐條醫過的機制量了一次；兩層檢索都改善，答案層卻變差，原因是分數尺被動了

- **ID:** `Claude_20260916_1610` — S228
- **Summary:** 將「展開詞不論查詢多短都原文照貼」變成三個預設關閉的旗標並跑出劑量曲線（最佳配置片段層 **+7**、零退步、重跑噪音 0），但**兩個配置的答案層判官都判 `NO_MEASURABLE_GAIN`**（合併 +3.5、balance 單獨 +1.5／門檻 8），因此**本節零檢索改動出貨**；追出兩個並存的解釋（絕對分數閘吃掉得益／這個量級堆不出 8 分）並各自記下支持與削弱它的證據；同節修好 OP⑩ 路由並推翻交接檔對它的診斷，量出 cross-encoder 的上限（最多救 42 條、65 條救不到），並清掉 Backlog ⑨。
- **Changed:** `backend/src/api/searchChannelB.ts`（三個 `EXPANSION_*` 旗標 ＋ `repeatsForBalance()` ＋ `positiveIntFromEnv()` 去重；`TOPIC_KEYWORDS.kg_admin` 提前並加兩個 token；`SOURCE_SETS.kg_admin` 加 `edbcm144_2026`）· `backend/tsconfig.scripts.json`（新）· `backend/package.json`（`check` 串兩個 project ＋ `check:scripts`）· `backend/scripts/_s226_knobAB.ts`（`EXPANSION_*` 不變式 ＋ 逐條記低 embed 字串 ＋ `knob_changed_embedded_input`）· `backend/scripts/_s228_rerankCeiling.ts`（新）· `backend/scripts/groundedSynthesis{Probe,Regression}.ts`（型別）· `dev/_s228_ceiling_report.py`（新）· `dev/source/route_regression.mjs`（9 條新案例 ＋ 1 條 `SOURCE_MEMBERSHIP`）· `dev/DOC_SYNC_CHECKLIST.md`（新 row）· `dev/DOC_SYNC_REGISTRY.md` · `dev/PROJECT_INDEX.md` · `dev/SESSION_HANDOFF.md` · `dev/source/eval_runs/2026-09-16_s228*`（新，六個 arm ＋ 合成 ＋ 判官三份 ＋ 上限一份）
- **Done:**
  - **機制旗標化**：`EXPANSION_MIN_QUERY_CHARS`（短於 N 個碼位不貼展開詞）、`EXPANSION_BALANCE`（保留展開詞，重複用戶查詢令它佔至少 φ 字數比例）、`EXPANSION_REPEAT_CAP`（預設 8）。三者未設 = 改動前逐位元組相同，解析契約照搬 `capFromEnv`（打錯字必須被忽略，不得靜靜放寬）。
  - **劑量曲線（六個 arm × 185 題 × 生產配置）**：`floor` 6/8/10 → 片段層 +1/+5/+5（10 開始出現 1 條退步）；`balance` .35/.5 → +2/+4；合併 `floor=8`＋`balance=.5` → **+7、零退步**。**噪音底線量了七次**：同一配置七個獨立 before 側，片段層 `chunk_PASS` 全部 59、來源層 123 六次 122 一次。
  - **答案層（兩個配置都量了，都判不出貨）**：合併配置 81 條、154 次呼叫 → `net_after` **+3.5**（judged 76、`always_first` 1、`always_second` 1、剔除 22）；`balance` 單獨 79 條、145 次呼叫 → `net_after` **+1.5**（judged 72、`always_first` 1、`always_second` 0、剔除 15、TIE 43）。門檻 8 → 兩者皆 `NO_MEASURABLE_GAIN`。判官因 30k TPM 上限中止兩次（第 66 條、第 16 條），餘數各自補跑，合共四段。棄權：合併 8→15、balance 8→11。
  - **OP⑩**：交接檔記載的病因（展開詞壓低答案分數）**實測不成立** —— 展開全關掉答案段落仍入不到窗。真因是 `edbcm144_2026` 只靠 spotlight overlay 露面而 `SPOTLIGHT_MAX_LEADS = 1`。修法：`kg_admin` 由尾二提前到 `kg_admission` 之後、補「幼稚園＋津貼／搬遷」、`edbcm144_2026` 入 set。
  - **cross-encoder 成本評估**：新工具擷取每題 top_8 與 top_40 兩個窗（後者正是現有 over-fetch），判分交回 Python 共用判分器。166 條有簽名者：已入窗 59 · 重排最多救 42 · 救不到 65（39%）。
  - **Backlog ⑨**：`backend/scripts/*.ts` 首次納入型別閘，順帶修好四個潛伏錯。
- **Fix Record:**
  - **Problem:** 六個 arm 全部報 `arm-noop`，看似「機制沒生效」。**Root Cause:** harness 以 last-write-wins 記錄送去 embed 的字串，而 `searchChannelB` 每側 embed 兩次（展開後查詢 ＋ spotlight 用的裸查詢）。**Fix:** 逐條記錄全部字串，並移植回 `_s226_knobAB.ts`。**Verification:** 重跑後畫面顯示 `幼稚園搬遷津貼` 被重複 6 次再接展開詞；`knob_changed_embedded_input` 81/81。
  - **Problem:** 交接檔把 OP⑩ 記為展開詞問題。**Root Cause:** 原分析用的是舊路由下的全域窗第 8 名作對照，而那個窗當時塞滿無關的 SAG 段落。**Fix:** 逐條量該通函全部 8 片段對查詢的餘弦。**Verification:** 答案段落在自己文件內排第 6／第 5，而配額是 3 —— 屬配額家族，已重新歸入 OP④。
  - **Problem:** 兩層檢索指標都報喜，答案層卻多了 7 次棄權。**Root Cause:** `floor` 令最高分中位跌 0.1296，題目跌穿 `VAULT_LEAD_SCORE` 0.70 而不再 bypass 合成閘。**Fix:** 未修 —— 這是「要不要出貨」的證據，不是 bug。**Verification:** 拆開兩個旗標量，`floor` 那 26 條中位 −0.1296、`balance` 那 71 條中位 ±0.0000；跌穿 0.60 的條數 `floor` 9/17/27 vs `balance` 0/0。
- **QC:** `npm run check` 0（現含 `tsconfig.scripts.json`）· `npm run build` 0 · `route_regression` **63/63** ＋ 2 條 `SOURCE_MEMBERSHIP`（改碼前紅測準確紅 3 條）· `route_blast_radius HEAD` 185 條只 2 條改路由 · `regression:grounded` 48/48 · `_s226_knobAB.ts` 開跑前兩行 `invariant OK` · `_s228_rerankCeiling --self-test` 4 條 · `_s228_ceiling_report --self-test` 7 條 · scripts 型別閘紅測準確轉紅 1 條 · 判官先校準（4/7，位置偏誤 0）才使用。
- **Evidence disposition:** 六個 arm 的原始擷取與判分、合成 A/B、判官三份 artifact、上限探針一份，全部保留為近期證據（下一節會引用）；劑量曲線、噪音底線、門檻跌穿表與上限數字已抄入 `dev/SESSION_HANDOFF.md` `## Validation / QC`；「動搖絕對分數必須連同下游門檻一起重新校」已升為 `## Open Priorities` ② 的硬紀律；「harness 必須逐條記低送去 embed 的字串」已升為 `dev/DOC_SYNC_CHECKLIST.md` 新 row 第 ④ 條。煙霧測試與等價性驗證的臨時 artifact 已刪。
- **Sync:** `dev/DOC_SYNC_CHECKLIST.md` 新增「查詢展開機制改動」row（依 anti-pattern guard 先補 row 再做）· `dev/DOC_SYNC_REGISTRY.md` 已記本節十列狀態 · `dev/PROJECT_INDEX.md` Local QC Commands 已更新 · `dev/CODEBASE_CONTEXT.md` **不需改**（技術棧／目錄／build 指令／外部服務／Key Decisions 均無變；新增的 `tsconfig.scripts.json` 屬 `npm run check` 的內部串接，已記在 PROJECT_INDEX）。
- **Pending:** 先決定信哪個讀法再動手 —— (i) 兩個絕對分數閘吃掉得益 → 重校門檻（OP②(c)）；(ii) 這個量級堆不出 8 分淨值 → 重新審視判官門檻是否適用。**在兩者之一有結論之前不要再跑展開側 A/B。**
- **Risks:** 三個 `EXPANSION_*` 旗標生產一律未設，未設 = 現狀，所以合併本身不改變生產行為；`kg_admin` 路由改動**不是旗標、合併後會即時生效**，影響面已量（185 條只 2 條改路由、off-gold 只影響含「幼稚園」的查詢）。
- **Log maintenance:** 觸發檢查 —— 主 log 目前 N < 11 條且未逾 1500 行，`## Confirmed Decisions` 類章節未達 30 條，本節無跨節累積模式需要即時寫入 `PROJECT_DECISIONS.md`；距離上次全面維護未滿 10 次收工。**結論：no-op**，不做長期維護。
- **Opening-message mirror:** 已由 `dev/SESSION_HANDOFF.md` 的 fenced 區塊重新產生 `START_NEXT_SESSION_PROMPT.txt`，並讀回逐字核對相同（76 行）。⚠️ **順帶修好 S227 的反向操作**：S227 只更新了鏡像檔、沒回寫交接檔區塊，令該區塊停在 S226 內容，而交接檔自己寫明「兩者不符以本區塊為準」—— 本節先由鏡像回寫，再按收工契約第 9 步的正常方向重新產生。
- **PR:** [#22](https://github.com/Leonard-Wong-Git/edb-knowledge/pull/22)（分支 `s228/expansion-knobs`，rebase 落 `8b630e3` 之上 —— 該 commit 是排程監察 `qc_report` 在本節中途自行推的帳本更新，零 `backend/` 改動）。**未合併**：合併會觸發 Render auto-deploy 並令 `kg_admin` 路由改動即時生效，依交接檔「`gh pr merge` 在 Leonard 明示授權下可執行」，等 Leonard 拍板。
<!-- ack:log-entry:end -->
