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
