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
