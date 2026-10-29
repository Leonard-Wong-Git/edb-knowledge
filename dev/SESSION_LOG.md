# Session Log
<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->

> **Handoff role**: This log is the trace-back / audit trail layer. Handoff capability rests on `dev/SESSION_HANDOFF.md`. The next AI session can continue by reading `AGENTS.md` + `dev/SESSION_HANDOFF.md` + `dev/PROJECT_INDEX.md` + needed rule packs; reading this log is not required for continuity. Each closeout applies `dev/rules/closeout.md` `## Maintenance Trigger Check`; that owner defines the current thresholds and archive discipline.

Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

This log carries recent evidence, not current state. Put the current objective, next action, risks, and workspace identity in `dev/SESSION_HANDOFF.md`.

Keep recent entries concise. If older entries no longer affect the next action and the current maintenance assessment establishes cleanup is required, reduce them to short dated indexes that point to the durable source of truth. Archive long error output, validation detail, or research trails only when actual maintenance requires it; do not create an archive directory by default.

When current work requires a log entry, record whether relevant older detail was kept, summarized, or archived, and any actual maintenance or unresolved preservation risk. Do not create an entry solely for a size advisory. Do not remove validation evidence or unresolved risks. The full opening message never belongs in this log.

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
- **Log maintenance:** <actual maintenance action, preservation risk, or not_applicable>
- **Opening-message mirror:** <regenerated and verified / blocked; full text omitted by design>
<!-- ack:log-entry:end -->
````

---

<!-- ack:log-entry:start -->

## 2026-10-29 Session 241 — OpenAI 模型遷移完成、通函編號查找（旗標關）、註腳佔格量完不改、定期更新檢查規則

- **ID:** S241（Claude_20261029_1730）
- **Summary:** 由頂層 root 起手轉入 Draft。完成 OpenAI 模型遷移（#53 合併、Render 刪 `OPENAI_MODEL`、OCR 與量度判官選型）；原 OP ② 註腳佔格量完判定不是槓桿；按 Leonard 指示寫入定期系統更新檢查規則；讀 Mindsquare 思考紀錄後以真實搜尋紀錄分類 9 條拒答，據此實作通函編號查找（`FEATURE_CIRCULAR_NUMBER_LOOKUP`，預設關）。
- **Changed:** `backend/src/lib/circularRef.ts`（新）、`backend/src/lib/wikiRepository.ts`（`loadCircularIndex`）、`backend/src/api/searchChannelB.ts`（circular-number pass）、`backend/scripts/circularRefRegression.ts`（新）、`backend/scripts/_s241_circularAB.ts`（新）、`backend/scripts/_s227_rubricJudge.ts`（`--model`／`--effort`、自有預設）、`dev/ocr_extract.py`（`--effort`、預設 `gpt-6-luna`）、`dev/_s241_ocr_ab.py`（新）、`backend/README.md`、`backend/.env.example`、`dev/rules/coding.md`（`## Project Rules` 附錄）、`dev/CODEBASE_CONTEXT.md`、`dev/PROJECT_INDEX.md`、`dev/DOC_SYNC_REGISTRY.md`、交接、本 log、`dev/archive/SESSION_LOG_2026_Q3.md`、`START_NEXT_SESSION_PROMPT.txt`；artifacts `dev/source/2026-10-29_s241_footnote_lead_before.json`、`dev/source/eval_runs/2026-10-29_s241_*`（7 份）。生產：#53 squash 合併部署 `da44e55`；Render 刪除 `OPENAI_MODEL`（Leonard 操作）。Supabase 零寫入、零 DDL。
- **Done:** 官方頁重讀（無變）· 線上合成轉 `gpt-6-luna` 並抽查 · OCR 8 頁比對與改預設 · 量度判官四個設定校準、Leonard 定案 `gpt-6-luna`＋`low` · `footnote_lead_probe` 生產基線與 185 題擠出分析 · 定期更新檢查規則 · Mindsquare 兩點核對 · 9 條真實拒答分類 · 通函編號查找生產基線、實作與本機 before→after。
- **QC:** `npm run check`、`npm run build`、`circularRefRegression` 11/11、`regression:grounded` 50/50、`route_regression` 63/63、`execute_ingest --self-test` 28/28、`_s227_rubricJudge --self-test` 67/67、`footnote_lead_probe --self-test` PASS；`dev/rules/coding.md` 官方本體逐位元組相同。數字見交接 `## Validation / QC` S241。
- **Evidence disposition:** 量度 artifacts 保留為近期證據並在 `PROJECT_INDEX`／`CODEBASE_CONTEXT` 引用；真實搜尋紀錄只在工作區暫存分析，未入 git；規則升格入 `dev/rules/coding.md`。
- **Sync:** `DOC_SYNC_REGISTRY` 兩列更新（離線工具模型 → `done`；檢索旗標列加 S241）。
- **Pending:** 見交接 Open Priorities S241 ①–⑤（① 開通函查找旗標並生產重量）。
- **Risks:** 量度判官有 1 對位置偏誤（只監察）；收工 PR 改 `backend/src`，合併後會重新部署；交接檔約 69 萬位元組，本節只完整讀現況段落，cold zone 未逐字重讀。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：281→209 行、10→7 條，S233／S232／S231 三條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪，已核對三個標題由主檔移入歸檔、歸檔只有追加）；工具同樣把一個 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該批第一條前；主檔 start／end 8／8 平衡，歸檔檔既有失衡不動。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對與舊慣例同格式（區塊＋結尾換行）；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-23 Session 240 — npm 依賴漏洞修補（PR #55 合併部署）

- **ID:** S240
- **Summary:** Leonard 要求「更新 php node 等漏洞」。本機與專案皆無 PHP；Homebrew Node 已是最新安全版。專案 `npm audit` 4 項以 `npm audit fix` 修補，PR #55 經 Leonard 指示 squash 合併，Render 部署 `77de1dd`。
- **Changed:** PR #55：`backend/package-lock.json`、`dev/checklists/_work/package-lock.json`、`dev/checklists/_work/node_modules/.package-lock.json`、`dev/checklists/_work/node_modules/nanoid/*` · 收工（推上 `s239/query-fusion`，即 PR #53）：交接、本 log、`dev/archive/SESSION_LOG_2026_Q3.md`、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:** backend `ws` 8.20.0→8.22.0、`form-data` 4.0.5→4.0.6、`hasown` 2.0.2→2.0.4、`esbuild` 0.27.4→0.27.2；checklists 工具 `nanoid` 5.1.11→5.1.16。合併後 `/health` 報 `77de1dd`。本機另一個 `/usr/local/bin/node`（24.14.0，無 pkg 收據）在本節 11:36 前後已被移除，非本 session 所刪，無殘留。
- **QC:** 兩處 `npm audit` 0；`npm ci`、`check`、`build`、`regression:grounded` 48/48、`route_regression` 63/63（與修補前逐字相同）、docx smoke test；build-gate pass；線上 `x-probe` 搜尋 200。
- **Evidence disposition:** 一次性；結論入交接 `## Validation / QC` S240。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S240 節。
- **Pending:** 不變，見交接 Open Priorities（S239 ①–⑤）。
- **Risks:** Render 所用 Node 22.x 小版本未核實；`cache_b` 173／303 對 S237 記錄 181／306 未逐條核對。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：292→264 行、10→9 條，S230 一條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；重查 `trigger=False`。工具再次把該條的 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該條標題前（兩檔各自 +1/+1，主檔既有失衡不動）。`latest entry prompt block ok=False` 為已知分歧（開場白不入 log）。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對相等；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-21 Session 239 — SEN 留級答錯的根因（展開詞）、查詢交替合併不出貨、狀態頁按改動重產、OpenAI 模型遷移選型與量度

- **ID:** S239（跨 2026-10-13、10-18、10-21）
- **Summary:** Leonard 以 RTHK 新聞指出系統答「SEN 學生留級未明確載明」與狀態頁未更新；要求治本。查明內容早已在庫，是類別展開詞把窄題目的答案推出候選池；交替合併的旗標檢索層 +9 片段但答案層不出貨。狀態頁改為按知識庫改動重產並自行比對現況。OpenAI 公布 2027-01-14 停用生產兩個模型，按 Leonard「剛夠用、不追新」選 `gpt-6-luna`＋effort `none`，量度後改碼內預設。全部在 PR #53（未合併）。
- **Changed:** PR #53（`s239/query-fusion`）：`backend/src/api/searchChannelB.ts`（`interleaveRankedLists`、旗標）、`backend/src/lib/wikiRepository.ts`（export `quotaBucket`）、`backend/src/lib/llmClient.ts`（`reasoning.effort`）、`backend/src/config/env.ts`（預設 `gpt-6-luna`、effort 解析與防呆）、`backend/src/server.ts`、`backend/scripts/_s226_knobAB.ts`、新 `backend/scripts/_s239_modelAB.ts`、`backend/scripts/groundedSynthesisRegression.ts`、`status-07cc7942c0.html`、`dev/source/status_page_test.mjs`、`.github/workflows/qc_report.yml`、`dev/source/check_monitor_health.py`、`dev/source/judge_acceptance.py`、文件（`backend/README.md`、`.env.example`、`DEPLOY_CHANNEL_B.md`、`README.md`、`dev/CODEBASE_CONTEXT.md`）、量度產物（`eval_runs/2026-10-1{3,8}_s239*`、`2026-10-21_s239model*`、`judge_runs/2026-10-21_s239_luna_none_r*`）· 收工：交接、本 log、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`PROJECT_DECISIONS.md`、`START_NEXT_SESSION_PROMPT.txt`、`dev/archive/SESSION_LOG_2026_Q3.md`。
- **Done:**
  - **根因**：`sen` 路由 1,135 段實測，答案段落（手冊 §3.3.2）原句排 1／4、展開句排 209／88；路由本身正確。另見頭兩格常被無關註腳佔（「學生」「安排」兩個二字詞即過 lead 門檻）。
  - **交替合併**：RRF 初稿以離線模擬否決；改交替合併後 185 題兩層量度、43 題答案層判官（Leonard 批准約 350 次）→ 不出貨（`net_after` +2.5、新增自信答錯 `cpd_induction_period_na`）。
  - **狀態頁**：頁面比對 `knowledge.json` 片段數與更新日誌；workflow 加 push／Issue 觸發（只認 owner 與機械人）與推送前 rebase；看門狗不計 skipped。
  - **模型遷移**：官方停用頁與價錢頁核實（經 web-fetch 代理）；判官凍結集 `gpt-6-luna`＋`none` 33/33 ×3 零錯放；答案層 36 題偏舊 0、偏新 15、耗時中位 3.4→2.8 秒；SDK 4.104 類型不認新 effort 值，以轉型送出（不升 4→7）；effort 只在模型用碼內預設時自動帶，防止 Render 現設的 `gpt-4o-mini` 被拒而靜默變空。
  - **S238 ② 核實**：10-19 排程在 Freshness #1 留 @mention 留言、Discovery #54 帶 @mention。
- **QC:** `npm run check`／`build`、`route_regression` 63/63、`regression:grounded` 50/50、`status_page_test` 全過、`check_monitor_health --self-test` 全過、`judge_acceptance --self-test`／`--check-parity`、環境組合 5 例；紅測四處（狀態頁比對、看門狗 skipped、effort 不繼承、knobAB 斷言 2 的空對照）皆轉紅；PR #53 build-gate SUCCESS。
- **Fix Record:** (1) 狀態頁新測試初稿把 22 小時前誤算為同日，修正的是測試日期，不是邏輯。(2) 第一次判官批次的 exit 1 來自迴圈最後一行 `[ $n -lt 3 ]` 的回傳值，三批實際全部完成（30＋28＋26 次）。(3) 第一次 effort 紅測沒有轉紅，是 sed 未套用；改用精確字串替換後確認轉紅。(4) 選題初版按 gold 次序補位會令幼稚園、人事、財務、校董會全部落選，改為平均間隔抽取。
- **Evidence disposition:** 量度產物入 git（eval_runs／judge_runs）；模型事實與量度入 `CODEBASE_CONTEXT.md`；選型取捨入 `PROJECT_DECISIONS.md`；Leonard 取向入長期記憶；暫存（sen_route.pkl、模擬腳本、批次清單）只在 scratchpad。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S239 節。
- **Pending:** ① 模型遷移收尾（先重讀官方頁確認應轉的模型、#53 合併與 Render 改動、離線兩項選型）② 註腳佔格 ③ `EDBC_9_2019_E` 退役 ④ Gmail 確認 ⑤ 待 token 項。
- **Risks:** 2027-01-14 停用（交接 Risks 11）；新模型答案約短一半，未經用戶回饋；外部呼叫：S239 第一次批准前跑了 282 次 embedding，已事後補報。
- **Log maintenance:** `session_log_maintenance.py --check` 報 date trigger → `--apply`：320→269 行、11→9 條，2 條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；重查 `trigger=False`。工具再次在檔尾留下孤立 `ack:log-entry:start`（S224／S231 記載的 off-by-one），已刪；主檔 start／end 12／11 的 +1 失衡在本節之前已存在（HEAD 為 13／12），不動。「latest entry prompt block ok=False」為已知分歧（Kit 規定開場白不入 log，S224 起取 Kit）。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對相等；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-13 Session 238 — 監察通知修正（新項目才 @Leonard）、三份新版入庫、16 個失效連結修復

- **ID:** S238
- **Summary:** Leonard 問監察有否偵測到來源更新；查出 freshness 已標 29 項、失效連結 15 條，但四個月無人收到通知。修好通知（新項目才以留言 @Leonard），並按 Leonard 逐項批准更新來源、修復連結（Supabase 17,021 → 16,990）。
- **Changed:** PR #48（`s238/monitor-notify`）：`.github/scripts/notify_new_items.js`＋`.test.js`、五個監察 workflow、`dev/source/FRESHNESS_GUIDE.md`、`dev/vault/repage_pdfs.py`（`REFRESH_S238`）、七份 vault 抽取檔、`source_registry.json`、`registry_drift.md`、清單資料（`checklists_bundle.json`、`dev/checklists/**`）、五個入庫腳本的網址常數、公開片段數七個鏡像檔 · 合併 `origin/s237/closeout`（S236／S237 收工）· 收工：交接、本 log、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:**
  - **通知根因**：未 Watch repo（subscription 404）＋監察只 `issues.update`；freshness／新通告／discovery／pgvector 從不 @mention。改為共用 helper：內文保留全清單、隱藏 marker 記已通知 key、新項目以中文 @mention 留言。Leonard 選「GitHub 電郵到 Gmail」「只在有新項目時通知」，並已在帳戶設定勾選 @mention 電郵（第一次截圖是 repo 的 push 電郵頁，已說明不要勾 Active）。Issue #3（退役監察）已關。
  - **四份 PDF 比對**（代理）：g19 新版、supply 新版、perf 小修訂、sag 純重新匯出；本人以全文 squeeze 抽查關鍵句全部吻合。
  - **入庫 B**：`repage_pdfs --write`（初次被分類器擋，經 Leonard 多選明示批准後執行）→ dry-run → 匯出 166 段備份 → `cb3_b2 --include-non-page --skip-local --execute`：116→115、36→35、14→14（supply 5 段註腳保留）。
  - **連結 C1**：9 個來源 Supabase `url` 更新（首輪精確比對漏了帶 `#page=` 的 6 段，改前綴比對補齊，0 殘留）；DSS 註腳改標 2026/27 並重新嵌入；registry、清單、腳本同步。
  - **連結 C2**：g26、k1（只載 2027/28 FAQ；通函已是 `edbcm080_2026`；3 段註腳逐字核對後改指新通函並重新嵌入）、資優 41→37、自評 10→10；第 279 章 11 段改指 e-Legislation；退役 EDBC_8_2020_E（8）、edbcm099_2026（3，registry `deprecated`）；display-sync 17,021 → 16,990。
  - **收工基底**：`main` 交接檔停在 S235（#45、#47 未合併），先合併 `origin/s237/closeout`，交接 sha 與 S237 收工版相同後才寫 S238。
- **QC:** helper 自測 6/6、紅測轉紅；五個 workflow 內嵌 JS `node --check` 全過；封面核對 11/11 ok；受影響 30 條網址 200；drift ZOMBIE／UNMANAGED／SERIES_UNMONITORED 0；生產總數逐步吻合；線上搜尋（x-probe）見新內容。**未做**：通知修正未在 GitHub 實跑（待 10-19 排程）。
- **Evidence disposition:** 現況與下一步入交接；代理比對報告與下載 PDF 只在 scratchpad（一次性）；Supabase 舊資料備份在本機 `dev/init_backup/20261013_105744_UTC/`（gitignored，不入 git）。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S238 節。
- **Pending:** ① 退役 `EDBC_9_2019_E`（Leonard 已批准，分類器擋下刪除及唯讀備份，未重試）② 10-19 通知到達 ③ 非華語學生津貼路由與清單舊字眼（待有 token）④ `FEATURE_SUBJECT_CHECK` 決定；⑬ freshness 其餘約 20 項。
- **Risks:** 通知修正未經真實排程（交接 Risks 10）；freshness 基線不可整體 write-sync。
- **Log maintenance:** `session_log_maintenance.py --check` 報 `line_count=295`、`entry_count=10`、`trigger=False`；寫入後 Kit 條目 12 個，達 Kit 核心規模提示門檻，本節無實際保存需要，不做歸檔（承 S230 兩套標準待整合）。
- **收工後續做（同日，第二次收工）:** Leonard「無更新 日誌」→ `update_log.json` 補記；「指引文件等有無都更新至最新／日誌保留最新 5–6 項」→ 指引文件庫 170 條全測、修 `g26`／`g28`／`g19`，日誌只留 6 條並在 `execute_ingest` 設 `UPDATE_LOG_KEEP=6`；「應該要有行政手冊／用 /jev-decide 寫規則」→ `sag_2025_11` 由「財務採購」移「行政」，新增 `check_downstream_sync.py`＋Jev 問題集（首跑 507 假陽性 → 改新舊版對照 → 11 真改動、50 頁碼移位；Jev 判 8 必須、4 交人手），清單來源表源頭修正並重產 bundle；示範問答「§3.1.2 約70至80天」查無出處，Leonard 揀改寫 → 附錄9／附錄1 原文（#50，Leonard 閱後確認正常）。PR #49（`513208b`）、#50（`a67bd29`）由 Leonard 指示合併。QC：`check_downstream_sync --self-test` 15/15、`execute_ingest --self-test` 28/28、瀏覽器實測指引文件庫與介紹頁、CI build-gate 皆過。Pending 加：清單條文 8 條＋頁碼 49 處（下一節）。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-11 Session 237 — OpenAI 舊模型停用通知：生產不受影響，碼內預設對齊 gpt-4o-mini

- **ID:** S237（Claude_20261011_1327）
- **Summary:** 由頂層 root 起手（Leonard 指出應直接轉 Draft），處理 OpenAI 2026-10-23 停用 `gpt-4.1-nano` 等舊模型的電郵；核實生產不受影響後，按 Leonard「修以上 1 2」對齊碼內預設與離線腳本，PR #46 合併並部署。
- **Changed:** PR #46（`a344504`）：`backend/src/config/env.ts`（`DEFAULT_OPENAI_MODEL` → `gpt-4o-mini`）、`backend/src/api/searchChannelB.ts`（頂部註解）、`backend/.env.example`、`README.md`、`backend/README.md`、`backend/DEPLOY_CHANNEL_B.md`、`dev/CODEBASE_CONTEXT.md`、`dev/PROJECT_MASTER_SPEC.md`、`dev/vault/{ai_extract,extract_candidates,wiki_search}.py`、`dev/test_synthesis_guard.py`、`dev/source/judge_acceptance.py`（註解）、`dev/source/JUDGE_PROMPT_FINDINGS.md`（現況註）· 收工：交接、本 log、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`CODEBASE_CONTEXT.md` AI Maintenance Log、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:**
  - **影響核對**：官方停用頁（`developers.openai.com/api/docs/deprecations`，2026-10-11 讀；電郵內追蹤連結未點擊）列 `gpt-4.1-nano` 2026-10-23 停用、替代 `gpt-5.6-luna`；`gpt-4o-mini`、`gpt-4.1-mini`、`gpt-4o` 別名、`text-embedding-3-small` 不在名單。全庫 grep 找出生產合成經 `OPENAI_MODEL`（碼內預設 `gpt-4.1-nano`），合成失敗會被吞掉返回空字串。Leonard 截圖核實 Render `OPENAI_MODEL=gpt-4o-mini`、無 `JUDGE_MODEL` → 生產不受影響。
  - **PR #46**：碼內預設、文件與四個離線腳本改 `gpt-4o-mini`；歷史記錄（CHANGELOG、`_s214_*` 報告、`AUDIT.md`、`PROJECT_MILESTONES_REVIEW.md`、S199 段落）保留原文。Leonard「合併」後 AI 以 `gh pr merge 46 --squash` 合併。
  - **收工分支**：S236 收工 PR #45 一直未合併；本節收工分支 `s237/closeout` 由 `origin/s236/closeout` 開出再合併 `origin/main`，#45 可關閉（待 Leonard 同意）。
- **QC:** `npm run check`（src＋scripts）、`npm run build` 通過 · 五個 Python 檔 `py_compile` 通過 · CI `build-gate` pass · 合併後 `/health` 約 60 秒轉 `a344504`、`cache_a` 455、`cache_b` 181／306 · 線上 `channel-b`（`x-probe`）8 條結果、合成 314 字內容正確 · 四個離線腳本未實跑。
- **Evidence disposition:** 現況（Render 環境變數快照、`a344504`）入交接；停用名單與替代模型只作本節核對，不另立文件（生產不用 nano）；臨時編輯腳本只在 scratchpad。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S237 節。
- **Pending:** 不變，見交接 `## Open Priorities`（首位仍為 Leonard 決定開 `FEATURE_SUBJECT_CHECK`）；關閉 #45。
- **Risks:** 無新增。
- **Log maintenance:** `session_log_maintenance.py --check` 報 `line_count=273`、`entry_count=9`、`trigger=False`；寫入後 Kit 條目 11 個，達 Kit 核心規模提示門檻，本節無實際保存或延續需要，不做歸檔（承 S230 兩套觸發標準待整合）。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文依設計不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-07 Session 236 — 路線乙 v1 以旗標上線（預設關閉）、Kit v0.4.3（Draft 與頂層）、刪除兩個 here.now 舊站

- **ID:** S236（Claude_20261007_1130）
- **Summary:** 由頂層 root「開工」轉入 Draft，起手探針全綠。Leonard 逐步指示：刪除兩個 here.now 舊站 → 「合併及批准」（#43、路線乙 v1）→ 讀官方頁面安裝或升級 Kit（選「兩個都升級」，再授權衝突合併）→「全做」→「合併 PR #44」→「收工」。
- **Changed:** 新 `backend/src/lib/subjectCheck.ts`、`backend/scripts/_s236_subjectCheck.ts`、`dev/source/eval_runs/2026-10-07_s236_subject_live.json` · `backend/src/api/searchChannelB.ts`（旗標閘＋`isSynthesisDecline`）· `backend/src/server.ts`（search_log 拒答判定）· `backend/src/config/env.ts`（移除 `tender-garnet-hqbd` CORS）· `dev/source/subject_check_probe.py`（`--export-rows`）· `backend/README.md`、`.env.example`、`dev/AUDIT.md`、`dev/CODEBASE_CONTEXT.md`、`dev/DOC_SYNC_CHECKLIST.md`、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、`dev/PROJECT_MASTER_SPEC.md`、`dev/source/SUBJECT_CHECK_DESIGN.md`、`dev/source/JUDGE_PROMPT_FINDINGS.md` · Kit 官方檔（`dev/rules/{agent-governance,closeout}.md`、`dev/handoff-kit/*`、快捷入口 4 個）· 頂層 dormant root 的 `dev/SESSION_HANDOFF.md`、`dev/SESSION_LOG.md`、`START_NEXT_SESSION_PROMPT.txt` 與 Kit 檔（不在 git）。
- **Done:**
  - **here.now**：`jade-nirvana-99hh`（2026-04 介紹頁）與 `tender-garnet-hqbd`（S163 前端鏡像，停在 v3.0.0，仍在 CORS 白名單）皆為永久站點、仍在線，非已過期；報告後 Leonard 指示不備份直接刪除 → API 刪除後兩者 404、帳戶 11 → 9 個站點。
  - **PR #43 合併**（`869ecf3`）。`gh pr merge` 本節兩次（#43、#44）均成功執行，未被分類器擋。
  - **路線乙 v1**：照設計文件第七節實作，`FEATURE_SUBJECT_CHECK` 預設關閉，放在判官與 vault bypass 之前，不覆蓋 grounded 路徑。發現並修好一個隱藏後果：search_log 以 `=== SYNTHESIS_DECLINE` 判拒答，新拒答句會被記成已作答 → 新增 `isSynthesisDecline()`。
  - **Kit v0.4.3**：Draft 試跑 conflict，因 S235 自己記錄上次衝突的那一句又引用了完整開場標題（v0.4.3 要求全檔唯一）；頂層 conflict 因 State Reconciliation Check 缺三個 `ack:field` 標記、開場訊息缺官方兩段、SESSION_LOG 存有開場訊息逐字副本。兩邊都先在臨時副本完整演練並逐字比對，取得 Leonard 授權後才改正式檔；升級後與演練逐字相同，`doctor` passed。頂層 log 的副本移除前已核對與交接檔逐字相同。
  - **PR #44 合併**（`f9da565`），Render 約 60 秒部署；合併後線上問 D01 仍經判官作答（證明旗標未開）。
- **Fix Record:**
  - **Problem:** 第一次 `--live` 重量間隔 400ms，25 題後全數撞生產每 IP 每分鐘 10 次限速。**Root Cause:** 未先讀 `eval_retrieval.py` 的 `DEFAULT_PACE_S = 7.0`；`x-probe` 不豁免限速。**Fix:** 停掉重跑，改 7 秒並把 429 退避拉長到超過一個限速窗，常數旁寫明原因。**Verification:** 重跑 254 題錯誤 0。不升為規則（工具常數已記）。
- **QC:** `npm run check`／`build` 通過 · `regression:grounded` 48/48 · `route_regression` 63/63 · `judge_acceptance.py --self-test` 0 failure、`--check-parity` 逐字相同 · `_s236_subjectCheck.ts --self-test` 19 項 ALL PASS · `--parity` 250 題差異 0 · `--live` 254 題、攔 7、全部應拒答、應答與 gold 誤攔 0 · `--smoke` 4 項通過（LLM 4 次）· Kit `doctor` passed（兩個 root）· 合併後 `/health` `f9da565`、`cache_b` 181／306。
- **Evidence disposition:** 實作、量度與限制入 `dev/source/SUBJECT_CHECK_DESIGN.md` 第八節（唯一定義處）；live 運行檔入 repo（不含片段全文）；parity 用的 rows（含片段全文）、Kit 臨時副本（約 10 GB）與診斷用 CLI 副本只在 scratchpad，已刪；四項驗收寫入 `DOC_SYNC_CHECKLIST.md`「Synthesis 前置閘改動」row 作可重用程序。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S236 節。
- **Pending:** Leonard 決定是否在 Render 開 `FEATURE_SUBJECT_CHECK=1`；⑫ executor 多份批准必衝突；⑪(c) 真實當機路徑；狀態頁「待決定」四項；log 維護兩套觸發標準整合（承 S230）。
- **Risks:** 旗標未開前生產判官照舊放行對象錯置（D01 合併後線上實測仍借用教職員規則推論）；v1 開啟後仍看不到 SX03、HX07 一類。
- **Log maintenance:** `session_log_maintenance.py --check` 報 `line_count=247`、`entry_count=8`、`trigger=False`（§4a 未觸發）；寫入後 Kit 條目 10 個，只屬 Kit 核心的規模提示，本節無實際保存或延續需要，不做歸檔。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文依設計不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-06 Session 235 — 入庫補救、Kit v0.4.2；路線乙量出「對象錯置」確實會重現，v1 攔一半而零誤攔，v2 在未見過的題目上被否決

- **ID:** S235（Claude_20261006_1030）
- **Summary:** 由頂層 root「開工」轉入 Draft，起手探針全綠。Leonard 報 GitHub 電郵有問題 → 查出 10-05 晚執行機塞車令兩份入庫批准失效 →「批准，全做」→ 安裝／升級 Kit →「全做」兩次（PR #42、核實 134、擴大樣本、改良與驗證、收工開 PR）。
- **Changed:** 新 `dev/source/subject_check_probe.py`、`dev/source/SUBJECT_CHECK_DESIGN.md`、`dev/source/judge_subject_s235.json`、`dev/source/judge_subject_heldout_s235.json`、`dev/source/judge_runs/chunks_cache_subject{,_heldout}_s235.json`、`dev/source/judge_runs/2026-10-06_s235_{subject,heldout}_41mini_r{1,2,3}.json` · `dev/source/judge_transplant_fresh_s202.json`（FT06 改標）· `dev/source/judge_acceptance.py`（擴題規則 4，docstring）· `dev/source/JUDGE_PROMPT_FINDINGS.md`（S235 節）· Kit 升級寫入的 `dev/rules/*`、`dev/handoff-kit/`、`.agents/`、`.gemini/`、`dev/governance_migrations/2026-10-06T11-18-20-705Z-…/` · 治理文件。**生產：Supabase +14（Option A 入庫，Leonard 剔選批准）；零 DDL；零 flag；PR #41、#42 自動合併並部署 `e6015f3`。**
- **Done:**
  - **GitHub 電郵**：三封失敗通知。Pages 失敗只是回報步驟被取消（建置與部署成功）；ops `option-a-approvals` 兩個工作排隊 15 分鐘零步驟被取消 → Leonard 剔選的 EDBCM134／142 無批准紀錄。另兩封為例行監察 Issue（#7 失效連結 15 條、#40 新文件 3 份）。
  - **入庫補救**：重跑較後的失敗 run（沿用事件內容）→ 兩份批准 → executor：134 經 #41 合併；142 的 #42 衝突（分支夾帶未壓縮的 134 commit）→ cherry-pick 到最新 main → 強制更新 PR 分支（首次被分類器擋，Leonard「全做」後重試成功）→ 合併 `e6015f3` → 部署後兩份實測搜得到。134 的「NOT retrievable」警告屬誤報。
  - **Kit v0.3.66 → v0.4.2**：試跑 conflict 源於兩行歷史紀錄引用了「## Next Session Opening Message」字串；改引號後先在臨時副本完整升級並逐行比對，才套用正式資料夾。
  - **路線乙**：讀 S202 原文 → 線上實測 D01 首句錯置、FT06 正確作答 → 證實 FT06 標錯 → presence／cooccur 原型（cooccur 對 gold 誤攔 9／50，棄用）→ 獨立審核 agent 確認四項數字並指出 D01 被攔屬窗口巧合 → SX 12 題（全文重核後 SX09 改標）→ v2 凍結（sha256 前綴 `6f81ee485a5f3728`）→ HX 12 題（凍結後才寫）→ 判官與 v1／v2 量度 → v2 否決。
- **Fix Record:**
  - **Problem:** SX09 第一次標為「否」，實際窗內有答案。**Root Cause:** 讀窗時每段截在約 550 字，漏看第 3 段後半「(5)志願工作者」；與 S202 的 FT06 是同一種錯。**Fix:** 全文關鍵字逐題重核（只有 SX09 需改），HX 改為讀全文後才定標。**Verification:** 重核輸出逐題列出命中位置。**升為規則**（重複發生，且會令量度結論錯）：`judge_acceptance.py` 擴題規則第 4 條。
  - **Problem:** 合併 PR #42 需要強制推送，第一次被 auto mode 分類器擋下。**Root Cause:** 屬改寫遠端分支歷史，需人批准。**Fix:** 沒有繞路，停下交 Leonard；獲「全做」後重試同一指令成功。不升為規則（`## User Environment` Push 邊界已涵蓋）。
- **QC:** `subject_check_probe.py --self-test` 全部通過（含 v2 斷言）· `judge_acceptance.py --self-test` 0 failure、`--check-parity` 逐字相同 · 判官 SX、HX 各三輪結果一致 · gold 181 題 v1 誤攔 0 · 獨立審核 agent 重算四項數字全部確認 · Kit `doctor` 54/54、`upgrade` migration committed · #42 build gate 綠 · 部署後線上檢索實測。
- **Evidence disposition:** 設計、數字與否決理由入 `dev/source/SUBJECT_CHECK_DESIGN.md`（唯一定義處）；題集、緩存與運行檔入 repo 作可重現證據；scratchpad 內的 gold 窗口全文、審核筆記、臨時 worktree 不保留（已移除 `wt142`）；v1／v2 取捨入 `PROJECT_DECISIONS.md`；擴題紀律入 harness 規則 4。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S235 節。
- **Pending:** v1 實作（旗標預設關閉）並以五套題重量；⑫ executor 多份批准必衝突的根治；⑪(c) 真實當機路徑；狀態頁「待決定」四項；log 維護兩套觸發標準整合（承 S230）。
- **Risks:** 生產判官仍會對「對象錯置」放行（已知 5 條）；executor 下次一次批准多份時會重演 #42 的衝突。
- **Log maintenance:** 寫入前 `session_log_maintenance.py --check` 報 `line_count=221`、`entry_count=7`、`trigger=False`；寫入後主 log 有 10 個 Kit 條目，未達 ≥11。`## Confirmed Decisions` 類章節未達 30 條。10 次收工 backstop：最近一次實際維護是 S231 收工（§4a 行數觸發歸檔），之後 S232–S235 共 4 次，未到。本節有一項多選取捨（v1 留、v2 否決），已寫入 `PROJECT_DECISIONS.md`。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文依設計不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-09-29 Session 234 — 白話狀態頁、線上服務探測、搜尋記錄本機報告

- **ID:** S234（Claude_20260929_0955）
- **Summary:** 由頂層 root「開工」轉入 Draft，起手探針全綠。Leonard 對分支與合併的困擾 → 選「每 session 一個 PR」→ 要求狀態頁簡潔、少工程字眼、維持運作並在需要時匯報 →「照做」→ 頁面上線後補上搜尋記錄的顯示需求 → 選本機報告（C）並「全做」。
- **Changed:** 新 `.github/workflows/live_probe.yml`、`dev/source/live_probe.py`、`dev/source/status_page_test.mjs`、`dev/search_log_report.py` · `status-07cc7942c0.html`（重寫前台，舊內容收入「技術詳情」）· `dev/source/qc_report.py`（`attention` 欄位）· `dev/source/check_monitor_health.py`（登記 `live_probe`）· `.github/workflows/qc_report.yml`、`monitor_watchdog.yml`（註釋）· 治理文件（`PROJECT_INDEX`、`DOC_SYNC_CHECKLIST`／`REGISTRY`、`CODEBASE_CONTEXT`、`PROJECT_DECISIONS` ADR-00W、`SEARCH_LOG_DESIGN` 第八節）。**生產：Supabase 零寫入零 DDL、零 flag、`backend/` 零改動。**
- **Done:**
  - **調查**：舊頁面橫額因檢索質素常設缺口天天紅；21 項檢查、封版閘、代號與複製指令佔滿版面；`backend_build_check` 只在 push／PR 時跑、看門狗只管監察有否跑，**沒有任何東西在服務當機時通知 Leonard**。
  - **#38**：狀態頁前台（一句話橫額、「需要你處理」、「運作概況」）、`attention` 欄位、`live_probe`；Leonard 在網頁合併 #37、#38。
  - **合併後驗收**：手動觸發 `live_probe` 與每日 QC 各一次（Leonard「全做」批准），均 success；探測 `up=True`、無 issue；QC 的 `Collect open items` 成功、線上 JSON 帶 4 項 `attention`，頁面實看正常。
  - **搜尋記錄本機報告**：Leonard 想在頁面看到用戶搜尋內容；指出 repo 與頁面公開，給 A／B／C 三案，Leonard 選 C。持久規則寫入 `dev/SEARCH_LOG_DESIGN.md` 第八節。
- **Fix Record:**
  - **Problem:** 我為 `qc_report.py` 寫的最後兩條斷言不會轉紅（一條的條件恆為真、一條寫了 `or True`）。**Root Cause:** 想「順手」加一條覆蓋，沒有問「這條斷言能不能失敗」。**Fix:** 自查時發現並刪除，改為只保留能失敗的斷言。**Verification:** 之後每個新測試都做了破壞測試（探測自檢的「永遠正常」取代、頁面測試的三種破壞、報告工具的「注入第二個請求」），均轉紅。只記錄，不升為規則（`DOC_SYNC_CHECKLIST` 第 56 列已寫明此紀律）。
  - **Problem:** `search_log_report.py` 的「唯讀」斷言第一次跑就失敗。**Root Cause:** 斷言用的搜尋字串同時出現在斷言本身，被算成第二處網絡請求。**Fix:** 把字串拆開寫。**Verification:** 通過，且注入第二個帶 body 的請求後轉紅 2 條。
- **QC:** `live_probe --self-test` 8 條 ＋ 「永遠正常」取代後 6 條轉紅 · `qc_report --self-test` ALL PASS（+9）· `check_monitor_health` `--self-test` 7 個 ＋ `--prove-assertions` 11 條轉紅 · `status_page_test.mjs` 24 項 ＋ 三種破壞轉紅 · `search_log_report --self-test` 23 條 · Issue 開／更新／關以模擬 GitHub API 跑五個情境（含建標籤 403 仍開警報）· 真實探測與真實報告各一次 · 桌面與手機實看（375 寬無橫向溢出）· build gate 綠。**未做：真實當機演練**（服務正常，只在模擬下驗過開 Issue 路徑）。
- **Evidence disposition:** 一次性 scratchpad 檔（模擬 harness、變異版本）不保留；持久結論入 `dev/SEARCH_LOG_DESIGN.md` 第八節與 `PROJECT_DECISIONS.md` ADR-00W；指令入 `PROJECT_INDEX.md`。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S234 節。
- **Pending:** 路線乙；`live_probe` 首次排程觸發與真實當機路徑；頁面「待決定」四項事項（自 2026-06-08 起）；`search_log` 累積後再加「路由分佈」與「gold 候選」；log 維護兩套觸發標準整合（承 S230）。
- **Risks:** AI 開的 PR 不能由 AI 合併（分類器擋，Leonard 未加 `permissions.allow` 規則）；`search_log` 內容一旦進公開檔案不可回收。
- **Log maintenance:** 寫入前 `session_log_maintenance.py --check` 報 `line_count=195`、`entry_count=6`、`trigger=False`；寫入後 7 條，Kit 核心 ≥11 條未達。`## Confirmed Decisions` 類章節未達 30 條。全面維護的 10 次收工 backstop：沿用 S233 的「未滿」判斷，本節未重新計數。本節有一項架構取捨（狀態頁橫額脫鉤、搜尋內容不上公開頁面），已寫入 `PROJECT_DECISIONS.md` ADR-00W。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文依設計不入 log。
<!-- ack:log-entry:end -->
