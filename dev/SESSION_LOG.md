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

## 2026-11-09 Session 247 — 清理 dev/init_backup 舊版 wiki_index 備份

- **ID:** S247
- **Summary:** Leonard 批准後刪除 26 份舊版／重複 `wiki_index.json` 備份（5–6 月 24 份、與現用檔雜湊相同的 `20261013_105847_UTC`／`20261013_110720_UTC`），釋放 10,826,816 KiB（約 11.09 GB）；保留 `20261101_195458_UTC`（SHA-256 與現用檔相同）及其餘 43 個備份；`dev/rules/safety.md` `## Project Rules` 加入 wiki_index 備份只留最新一份的規則。
- **Changed:** `dev/rules/safety.md`、本 log（PR #89 → `82be06e`）；收工：交接、本 log、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、`START_NEXT_SESSION_PROMPT.txt`；本機刪除 `dev/init_backup/` 26 個資料夾（gitignored）
- **Done:** 只讀審核 → Leonard「批准刪除＋加規則」「開分支並開 PR」「CI 綠後合併」。
- **QC:** 27 資料夾逐一核內容與大小；3 份新版 SHA-256 與現用檔相同；全項目搜尋資料夾名稱無腳本／待辦引用；刪後保留份再核 SHA-256；safety.md 官方內文前綴 SHA-256 不變；PR #89 CI 通過。
- **Evidence disposition:** 數字與決定已吸收入交接檔 `## Validation / QC` S247；規則在 `dev/rules/safety.md`。
- **Sync:** DOC_SYNC_REGISTRY S247 段；開場鏡像由唯一區塊重生並核對。
- **Pending:** 見交接 `## Open Priorities`（下一步退役 `EDBC_9_2019_E`，先確認）。
- **Risks:** none（零生產改動）。
- **Log maintenance:** not_applicable。
- **Opening-message mirror:** regenerated and verified; full text omitted by design.
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-08 Session 246 — Option 2 清單清空；刪除 109 條 approved_fact 副本；PR #87 合併

- **ID:** S246
- **Summary:** 最後一條租金收入以 g02《財務管理指引》第 15 頁按原文修正，清單清空（resolved 289、dropped 166）；按規則第 5 條備份後刪除 Supabase 109 行 `role_facts_*`；PR #87 合併；舊分支刪除；兩個 footnote 來源判定按設計不登記。
- **Changed:** `dev/knowledge/channel_a_option2_queue.json`、`stats.json`／`app.html`／`index.html`／`README.md`（17,183 → 17,074）、`CHANGELOG.md`（工作 commit `28aaaf9`，經 PR #87 合併為 `62647fe`）；收工：交接、本 log、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、開場鏡像（分支 `s246-closeout`）。
- **Done:** Leonard「甲」「批准寫入」「匯出備份」「批准刪除」「加入 PR #87」「CI 綠後合併」「刪舊分支＋登記來源」；Supabase −109，17,074／315。
- **QC:** g02 PDF 按版面座標重組並逐字對照；清單序列化格式核對；備份 109 行＝`count=exact`；刪除 `id` 集合＝備份；display-sync 讀回並於線上確認；`build-gate` 在 `28aaaf9` 通過後才合併；`check_registry_drift --check` UNMANAGED 0；`d2c95ee` 與 `17903a3` patch 相同後才刪分支。
- **Risk observed:** Render 喚醒後首兩次查詢 `57014`（含通函索引），之後自行恢復 —— 屬既有 Risks 3，未新增風險。
- **Evidence disposition:** 備份在 `dev/init_backup/20261108_122028_UTC/`（gitignored，本機）；g02 PDF 與匯出腳本在 scratchpad（臨時）；決定與數字已吸收入交接檔 `## Validation / QC` S246 與清單本身。
- **Sync:** DOC_SYNC_REGISTRY S246 段；開場鏡像已由唯一區塊重生並讀回相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-05 Session 245 — Option 2 第二輪：清單 39 → 1；BYOD footnote 入庫

- **ID:** S245
- **Summary:** 餘下 39 條逐條在庫內關鍵詞搜尋並上 edb.gov.hk 搜尋：23 條按原文修正入出處、14 條剔除、1 條（BYOD）原文只在網上，以 footnote_curated 入庫後入出處；只剩租金收入一條待 Leonard 定出處。
- **Changed:** `dev/knowledge/channel_a_option2_queue.json`、`dev/ingest_s245_option2_byod_footnote.py`（新）、`update_log.json`、`dev/PROJECT_INDEX.md`、`stats.json`／`app.html`／`index.html`／`README.md`（17,182 → 17,183；313 → 315）、交接與鏡像。
- **Done:** Leonard「Approve all」（37 條）、「Approve ingest」（footnote）；Supabase +1（176 → 177），線上 `/health` footnote 177；PR #86 已合併故改開 PR #87。
- **QC:** 修正句錨點核對（只兩處刻意刪符號）；每次寫入後 `channel_a_jev_round.py --self-test` 全過；footnote 自測 cos 1.0000、INSPECT before／after；display-sync 與 sources-sync 讀回。
- **Evidence disposition:** 提案檔與清單備份在 `dev/source/coverage_runs/option2/r1/`（gitignored，本機 trace）；決定與理由已寫入清單本身；現況與下一步已吸收入交接檔。
- **Sync:** DOC_SYNC_REGISTRY S245 段；開場鏡像已重生並核對相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-05 Session 244 — Option 2 第一輪：清單 455 → 39；3 條 curated footnote 入庫

- **ID:** S244
- **Summary:** 寫腳本以 Jev 逐條核對 Channel A 清單，加「同一件事」題修正剔除誤判，再經人手核對、關鍵詞與網上搜尋、按原文修正、角色類與時限資料剔除，清單減至 39 條；3 條網上出處以 footnote_curated 入 Supabase。
- **Changed:** `dev/source/channel_a_jev_round.py`（新）、`dev/ingest_s244_option2_footnotes.py`（新）、`dev/source/jev/channel_a_match_gate.json`、`dev/knowledge/channel_a_option2_queue.json`（決定＋規則 6–8）、`update_log.json`、`dev/PROJECT_INDEX.md`、`stats.json`／`app.html`／`index.html`／`README.md`（17,179 → 17,182）、交接與鏡像。
- **Done:** 每一批寫入均經 Leonard 批准（原話記於清單每條 `approved` 欄）；Supabase +3（footnote_curated 173 → 176），線上 `/health` footnote 176；PR #86。
- **QC:** `channel_a_jev_round.py --self-test` 21 項全過（每次寫入後重跑）；footnote 自測 embed 格式 cos 1.0000、INSPECT before／after；修正句錨點核對零不符；`live_display_sync` 四檔替換。
- **Evidence disposition:** 判斷紀錄、候選、各批提案與清單備份在 `dev/source/coverage_runs/option2/r1/`（gitignored，本機 trace）；決定與理由已寫入清單本身；現況與下一步已吸收入交接檔。
- **Sync:** DOC_SYNC_REGISTRY S244 段；開場鏡像已重生並核對相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-03 Session 243 — 新文件 #78 分流與入庫、Channel A（455 條）退役、文件標註收起待修、刪除範本下載與兩個休眠頁

- **ID:** S243（Claude_20261103_0930）
- **Summary:** 由頂層 root「/handoff-kit-start」轉入 Draft。Leonard 問新文件電郵（#78 二十份含 2017 年）→「逐份判斷」→「批准入庫」→ 問搜尋紀錄拒答原因與 455 條去留 →「做 1 3 …4 刪去」→「用 /jev 核對副本」→ 文件標註實測與 Jev 第二意見 →「收起待修」→「範本 Word 檔刪去」→「t-purchase.html 刪除」→ 每個 PR「CI 綠後合併」（#79–#84）→「收工」。
- **Changed:** PR #79 入庫 `moi_3rd_cycle_policy_2021`（登記冊、vault、`SOURCE_SETS.moi`＋「化時為科」觸發詞、route_regression、指引書庫 182、更新日誌、公開數字）· #80 Channel A 退役（刪 `knowledge.json`／`role_facts.json`／`q.html`／`K1_KNOWLEDGE_INTERFACE_SPEC.md`、後端 3 條路由與 9 個模組；`approved_fact` 全數停服；新 `stats.json`、`dev/knowledge/channel_a_option2_queue.json`；QC、狀態頁、execute_ingest 改讀 stats.json）· #81 文件標註收起＋Jev 判斷閘 `dev/source/jev/channel_a_match_gate.json` · #82 標註按鈕補開關 · #83 刪範本分頁、109 份 Word、生成腳本 · #84 刪 `t-purchase.html`、手機版選擇角色畫面、README 對齊。
- **Done:**
  - **#78 分流**：二十份是監察首次掃描 S241／S242 新增的三個來源頁（教學語言、IIT、基本法測試）而一次過列出；逐份讀全文，只有 2021-04-29 第三周期政策函件值得入庫（庫內 07-06 跟進函寫明須與之一併閱讀），其餘 19 份 Leonard 定「不入」；#78 等監察下週一自動關閉（Leonard 指示）。
  - **入庫**：Supabase +9（17,170 → 17,179，來源 313）。
  - **Channel A 退役**：線上 `/api/search/channel-a`、`combined`、`analyze-circular` 回 404；搜尋頭 5 位不再出現無出處副本；首頁與平台介紹不再顯示 455。
  - **文件標註**：線上實測三個質素問題（相關指引幾乎不顯示、欠缺按清單次序、部分符合配錯段落）；Jev：誤導 0.94、可一輪修好 0.92、使用證據 0.04；Leonard「收起待修」。
  - **刪除**：範本下載分頁＋109 份 Word＋生成腳本；`t-purchase.html`；手機版「選擇角色」（角色從未傳給搜尋）。
- **QC:** 每個 PR build-gate 綠後由 Leonard 指示合併；`npm run check`／`build`、route_regression 76/76（＋2 條新斷言）、execute_ingest 30/30、qc_report 與 status_page 自測、checklists_bundle 重生逐字相同；合併後線上核實 /health（20fd4a4）、四條 x-probe 搜尋、桌面與手機分頁、手機導覽四步、404 頁面、console 零錯誤。
- **Evidence disposition:** 二十份 PDF 與 Jev state 只在 scratchpad；判斷結果寫入交接 `## Validation / QC` S243 與 CHANGELOG；Option 2 規則寫入清單檔 `_meta.rules`。
- **Sync:** `DOC_SYNC_REGISTRY` 新增「任何入庫／換版／退役 → 核對 Option 2 清單」一列；`DOC_SYNC_CHECKLIST` 凍結合約列改為只餘 guidelines.json；README、CHANGELOG、CODEBASE_CONTEXT、PROJECT_MASTER_SPEC、K1_API_SPEC 已同步。
- **Pending:** 見交接 Open Priorities（S243 段）：Option 2 第一輪（Jev 判斷閘）、文件標註四項重開條件、拒答原因 DDL 待批、#70 待關閉。
- **Risks:** 109 條 `approved_fact` 仍在 Supabase（只停服）；`app.html`／`mobile.js` 尚有不再觸發的 approved_fact 顯示程式；dev/vault 舊 Channel A 篩選腳本未刪。
- **Log maintenance:** `--check` trigger=False（224 行、8 條），不需歸檔。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-11-02 Session 242 — 封面核對 Issue #72 三份換版／退役入庫、拆出 blnst 路由、QC 報告排隊撞車修正

- **ID:** S242（Claude_20261101_1930）
- **Summary:** 由頂層 root「/handoff-kit-start」轉入 Draft。Leonard「處理封面核對」→「全部批准」→「完成就commit and push」→ 三次「CI 綠後合併」（#73、#74、#75）→ 中途「現在追查」（基本法測試短查詢）與「10:48 收到 failed 電郵」→「收工」。
- **Changed:** `dev/source/source_registry.json`（退役 `edbcm141_2025_blnst`；新增 `edbcm170_2026_blnst`、`blnst_faq_2026`、`sdp_guide_dss`；`sdp_guide`、`iit_ai_framework_2026` 換版）· vault 抽取檔 · `dev/vault/repage_pdfs.py` · `backend/src/api/searchChannelB.ts`（#73 三個路由集合；#74 新 `blnst` 路由）· `dev/source/route_regression.mjs` · `app.html`、`README.md`、`index.html`、`knowledge.json`、`role_facts.json`、`K1_API_SPEC.md`、`update_log.json`（公開數字）· `dev/source/title_baseline.json` · 三個清單範疇 `checklist.json`／`meta.json`／`clauses.json` 與 `checklists_bundle.json` · `.github/workflows/qc_report.yml`。**生產**：Supabase −10 +40（17,153 → 17,170，310 → 312 來源，逐項經 Leonard 批准）；Render 部署 `aeb6cb7`、`3ef9ab6`、`f7b988c`。
- **Done:**
  - **#73**：封面核對三份。141/2025 與 SDP 2010 版皆 404，教育局改掛新文件；iit 同網址換檔並改寫。舊資料連向量備份於 `dev/init_backup/20261101_195421_UTC/`（gitignored）。清單 27 條條文逐句在新文件找回原句後改指新片段。
  - **#74**：線上抽查發現「基本法測試」「BLNST」取不到新文件。量度證實是 hr_admin 展開詞（假期／薪酬）所致（最佳排名 1 → 36；BLNST 319 → 81），拆出 `blnst` 路由並以文件原用詞作展開，六種問法首三位全是 BLNST 文件。
  - **#75**：10:48 失敗通知 = QC 報告兩次排隊執行（push #73 ＋ 關閉 Issue #72），第二次由觸發當刻的 commit 重產，rebase 撞 `registry_drift.md`。改為 checkout `ref: main` ＋ `pull --rebase -X theirs`。
- **QC:** 封面核對 6/6 ok、基線差異 0 · `check_downstream_sync` MUST_UPDATE 0 · `npm run check`／`build` · `route_regression` 79 PASS · `route_blast_radius` 185 條只 1 條改路由（`cpd_blnst_test`，預期）· `check_source_titles --self-test`、`execute_ingest --self-test` 30/30 · 三個 PR build-gate 綠 · 合併後 `/health` commit 逐次核實 · 帶 `x-probe` 線上抽查（SDP、人工智能部分、BLNST 六問法）· QC 工作流程手動觸發一次 success。
- **Evidence disposition:** 量度腳本（`measure.py`、`probe.py`、`remap.py`）只在 scratchpad，不保留；數字寫入交接 `## Validation / QC` S242 與 `searchChannelB.ts` 的 `SOURCE_SETS.blnst` 註釋。
- **Sync:** `DOC_SYNC_REGISTRY` 不新增列；入庫常設步驟（更新日誌、指引書庫、README、下游同步、封面基線）已逐項做完。
- **Pending:** 見交接 Open Priorities（S242 段）。
- **Risks:** QC 撞車修正只經單次執行驗證，未經真實並發；交接檔約 71 萬位元組，本節只完整讀現況段落。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：226→204 行、8→7 條，S234 一條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；工具再把該條的 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該條標題前。主檔 start／end 的既有失衡不動。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文不入 log。
<!-- ack:log-entry:end -->

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
- **Fix Record（收工後補丁）:** Problem：#56 合併、Leonard 開旗標後生產無效。Root Cause：對照表查詢全表文字掃描，匿名角色 3 秒上限冷啟動逾時（4.2 秒），被 catch 吞掉；本機用 service key（8 秒）量不到。Fix：先按 `source_id` 前綴篩選，暖機預載。Verification：匿名金鑰冷 1.8 秒／熱 0.5 秒、64 份；匿名重跑 88/88 排第 1、零退步；check、build、單元 11/11、grounded 50/50、路由 63/63。教訓與既有量度紀律「本機用 service key 量 anon 系統會低估」相同，已有規則，未另立新規。
- **Fix Record 2（2026-10-30）:** Problem：#57 部署、旗標加上後仍無效。Root Cause：縮小後的文字掃描在冷資料庫仍 4.4 秒逾時；fail-open 令旗標缺失與載入失敗從外面無法分辨（截圖另核實前一次旗標其實未設）。Fix：按常見命名猜 id 直接查並以標頭核對、完整對照表背景載入與重試、失敗寫日誌、`/health` 報 `cache_b.circular`。Verification：匿名金鑰 resolve 約 1.1–1.7 秒、64 份；88/88 排第 1；單元 12/12、grounded 50/50、路由 63/63、check、build。另：補丁二的 commit 一度誤推上已合併的 `s241/circular-index-anon-timeout` 分支（無 PR，不影響 main），已 cherry-pick 到新分支。
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
