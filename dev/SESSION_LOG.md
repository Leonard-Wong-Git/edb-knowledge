# Session Log

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
## 2026-09-07 Session 217 — 遠端又走前一步；rebase 保全逐位元組驗證後，四節 session 的未 push 狀態一次結清並部署

- **ID:** `Claude_20260907_1930` — S217
- **Summary:** 由「開工」起手探針揪出 `origin/main` 已被 bot 推前兩個 commit，本地由「領先七個」變成真分歧。Leonard 自行 rebase，Claude 逐位元組驗證保全、過齊 §3c 機器驗證閘，然後按 Leonard 選項 1 push 並觸發部署，最後在生產側實測三個端點。**零程式碼改動** —— 本節未寫過一行 `backend/` 或 `app.html`。
- **Changed:** 無程式碼改動。持久化：`dev/SESSION_HANDOFF.md`（`Current Baseline` 第 1–3 項／`Validation / QC` 新增 S217 段／`Risks / Blockers` 第 1、3 項／`Open Priorities` Recommended next step 與 ① 結案／`Last Session Record` 重生為 S217，S216 降級原文保留／`Next Session Opening Message` 重生）· `dev/SESSION_LOG.md`（本條）· `START_NEXT_SESSION_PROMPT.txt`（由 fenced block 重生，58 行，mirror 逐位元組相等）。
- **Done:**
  1. **起手探針五項**：平台 v3.3.2、Render `/health` `4a25a15` warm 455、Supabase 17,610、`source_registry` 281 全部相符。**唯一漂移**：`origin/main` `463434c` → **`42b1441`**，兩個 bot commit（`de030b7` discovery ledger、`42b1441` QC 報告重生，只碰三個資料檔）。本地變成 **7 ahead / 2 behind**，直接 push 會被拒。
  2. **先量後做**：實測 merge-base `463434c` 起計，本地七個 commit 與 bot 觸及的三個檔零重疊 → rebase 屬機械操作。據此建議 rebase，Leonard 自行執行。
  3. **rebase 保全逐位元組驗證**（不是「看落無事」）：`git diff 463434c 1378b53` 與 `git diff 42b1441 612e13e` 兩個 patch set **105,683 行／150 個檔完全相同**；`merge-base --is-ancestor 42b1441 HEAD` 確認兩個 bot commit 在祖先鏈。作者名由 rebase 正規化為 `leonard-wong-git`。
  4. **§3c 機器驗證閘（推之前）全綠**：`npm run check` exit 0 · `npm run build` exit 0（未弄髒工作區）· `regression:grounded` **48/48 ALL PASS** · `route_regression` **46/46 PASS**（兩個已知 `safety` 認裸「氣體」缺口不計入，行為同 S211 前後一樣）。
  5. **Push ＋ 部署**：Leonard 明示選項 1。`42b1441..612e13e` push 成功，分歧歸零。背景輪詢 Render，第三次（19:27:03Z）讀到 `commit=612e13e`、`started_at` 19:26:49Z、`cache_a.warm=true size=455`。
  6. **生產側煙霧測試**：`channel-a` 教師專業操守 → 50 條 · `channel-b` 幼稚園收生 → 8 條（top1 `k1_admission_2627` 0.738）· `combined` → total 58（a 50 + b 8）＋ synthesis 395 字。
  7. **一次 0 結果已定性**：部署後首個 `採購程序` 請求回 0 條，隨後連跑 5 次全部 8 條、shape 一致。發生在實例剛重啟後的首個請求，屬 S118 已記錄的 probes=8 冷啟動／間歇族，**不是本次部署引入**。但當時 response body 未保存，**成因未能確證**，只能排除「新 regression」這一項。
  8. **【Leonard 追問後補做】逐檔行為核對，推翻了我自己上一輪的講法。** 我原本說「flag 全 0 即行為不變」—— 那句**只對合成 prompt 成立**（`regression:grounded` 那條斷言的範圍），不覆蓋整個系統。以 `git diff 4a25a15 612e13e -- backend/src app.html` 逐個 hunk 讀過後：**`searchChannelB.ts` 的 establishment 路徑改動沒有任何 flag 保護，已在生產生效**。三處差異：(a) `estLead` 移除 `!seenIds.has(r.id)` 過濾；(b) 插入方式改為置頂並濾走整個 establishment 來源的其他列；(c) `trustedVaultLead` 判斷來源由 `results[forcedLeads]`（overlay 後）改為 `mainSearchLead`（overlay 前）。其餘執行碼逐個 hunk 確認零行為改動。**觸發範圍生產實測為窄**（staffing 路由 ＋「N 班」）：「小一派位第1班點分」未被塞入、「教師編制點計」正常；受影響的「12班小學有幾多個學位教師」回 學位教師 5／副校長 1／助理 14／合計 21，與 S211 記載的正確列相符（S211 錯答為 學位教師 2／助理 7／合計 10）。**但這是 1 條事後觀察，不是 before／after 對照**，舊碼已不在生產環境無法跑對照組。
- **QC:** 見上第 4、6、8 點。`agent-handoff-kit doctor` 本節未重跑（S216 實測 53/53，本節零治理結構改動）。**未跑：185 題 live 套件** —— 這是啟用任何 flag 的唯一閘，未動。`qc_report.json` overall **ERROR** 未處理，狀態同 S215／S216。
- **Evidence disposition:** rebase 保全驗證數字、機器閘結果、部署輪詢時序、煙霧測試逐條 → 留在本條 log 作 trace 證據；當前 HEAD／部署 commit／flag 狀態／① 結案 → 入 `SESSION_HANDOFF.md`。「遠端會自己走前，開工探針必須 `git fetch` 後比對而非讀交接記載的 hash」屬跨 session 可重用教訓，已寫入開場白 ⚠️ 段。未升 `PROJECT_DECISIONS.md` —— 本節無架構取捨。
- **Doc Sync: registry updated** —— `dev/DOC_SYNC_CHECKLIST.md` 新增一行「既有 commit 上主線並觸發部署（本身零程式碼改動；S217 建）」。原因：本節的改動類別（push 積壓 commit ＋ 觸發部署，零程式碼改動）在 registry 內無任何 row 匹配，按該檔 Anti-pattern guard 必須先補 row 再繼續，不得靜靜略過。
- **Sync:** `dev/CODEBASE_CONTEXT.md` **不需更新**（技術棧、目錄、build 指令、External Services、Key Decisions 本節皆未變）。`dev/PROJECT_INDEX.md` **不需更新**（無新檔、無新指令）。`START_NEXT_SESSION_PROMPT.txt` 已重生並 mirror check 通過 —— 因為原內容的頭號紅旗（七個未 push commit）已成事實錯誤，不屬「為了令 doctor 收聲而重生」。
- **Pending:** 185 題 live 套件未跑（啟用 flag 的閘）· `backend/README.md` 5 行未補 · 交接檔 8 個 marker 未有專屬章節（OP ⑥）· `INIT.md` 鏡像 blocked（OP ⑦）· 根目錄 v0.3.24 舊 Kit 未處理 · S212–S215 產品側遺留一項未動。
- **Risks:** ① **S214 候選碼已在生產環境，而且「flag 全 off」並不等於零行為改動** —— establishment 路徑無 flag 保護、已生效（見第 8 點）。單一 case 實測正確，但 184 條未量，`searchChannelB.ts` 那 +968 行從未經 185 題 live 驗證 —— **已部署 ≠ 已驗證**。② Option A watcher bot 會繼續自行推送，下次開工大機會又落後，先 rebase 再處理。③ `AGENTS.md`／`CLAUDE.md`／`GEMINI.md` gitignored 且從未 tracked，S216 升級改動仍不在版本控制內，唯一還原點是 `dev/governance_migrations/` 備份目錄（該目錄內的 `AGENTS.md` 同樣被 ignore）。
- **Log maintenance:** 無觸發。寫入本條後主 log **7 條** entry（門檻 11 條）、約 470 行（門檻 1500 行）；`dev/SESSION_LOG_archive/` 不存在。`PROJECT_DECISIONS.md` 觸發條件 (b) 不成立（交接檔無 ≥30 條 decisions-like 章節）、(c) 不成立（push 決定屬既有 OP ① 的執行，非新架構取捨）。10-closeout backstop 沿用 S216 的保守判定，未到。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成 58 行，讀回逐位元組相等；全文按契約不複製入本 log。
<!-- ack:log-entry:end -->


<!-- ack:log-entry:start -->
## 2026-09-07 Session 216 — Agent Handoff Kit v0.3.29 → v0.3.66 升級；四層 conflict 逐層解開，並揪回工具靜靜刪走的 65 行狀態

- **ID:** `Claude_20260907_1900` — S216
- **Summary:** Leonard 要求依官方安裝說明頁升級本資料夾的 Agent Handoff Kit。實際做的是：辨清兩份獨立安裝、逐層解開四批 conflict、修好一個一直靠垃圾值通過的隱形 check，以及發現並還原 `upgrade` 本身造成的 65 行狀態損失。**零程式碼、零檢索、零產品改動。**
- **Changed:** `AGENTS.md`（managed core）· `GEMINI.md`（全文換官方 bridge）· `dev/SESSION_HANDOFF.md` · `dev/SESSION_LOG.md` · `dev/PROJECT_INDEX.md` · `dev/PROJECT_DECISIONS.md` · `dev/RULE_PACKS.md` · `dev/DOC_SYNC_REGISTRY.md` · `dev/rules/` 八個 pack · 新增 `dev/rules/closeout.md` · 新增 `dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/` · `START_NEXT_SESSION_PROMPT.txt`。**已本地提交為 本節 S216 closeout commit（58 個路徑，指定檔案逐個 `git add`，未用 `-A`）；按 Leonard 明示只 commit 不 push。**
- **Done:**
  1. **先分清兩份安裝再落手**：專案根目錄有一份 v0.3.24（6 月停滯），`Draft/` 有一份 v0.3.29（live）。兩份都各自有 conflict。按 Leonard 選擇**只升 `Draft/`**，根目錄零接觸。落手前另做一份完整 tarball 備份（此 repo 的 `AGENTS.md` 等三檔不在 git 內，無 git 還原網）。
  2. **第一次 `upgrade --yes` 全數拒寫**：3 個 conflict 令它一個檔案都不寫（全有或全無），零改動。逐個查明：`GEMINI.md` 是 3 行舊 stub 零本地自訂 → 直接換官方版；`SESSION_LOG.md` 缺官方要求的 ```` ```markdown ```` Entry Template 圍欄 → 只換第 1–35 行頭部，440 行歷史**以 `diff` 逐位元組驗證一致**；`communication.md` 把官方本體原地改寫故 CLI 判不到 → 改為「官方 v0.3.66 本體 ＋ `## Local Appendix`」，S196 六條 claim discipline 全保留、規則編號 3/6/7/8/9/10 → L1–L6、L6 內「run rules 3, 6, 7, 8 and 9」同步改為 L1–L5。
  3. **第二層：`SESSION_HANDOFF.md` acceptance gate**。**沒有靠猜** —— 直接讀 CLI 原始碼 `bin/agent-handoff-kit.mjs:372` 與 `extractSectionText()`，確認 gate 只要求 `completed-this-session`／`validation-qc`／`next-priorities`／`risks-blockers` 四節加開場白非空。用 CLI 自己的函式寫探針實測，四節全部 `len=0`。**根因**：21 個 `ack:` marker 全部疊在檔頂第 3–23 行當目錄用，而 `extractSectionText` 是「由 marker 之後讀到**下一個** `ack:section:` 為止」，一行疊一行 → 全部抽出空字串。
  4. **修正**：marker 搬到各自章節；新建 `## Validation / QC` 與 `## Risks / Blockers`（本檔原本沒有這兩節），內容由 `Current Baseline` 第 2、4、5 項**搬**入、原位留指針，零重複零杜撰。搬完以 `diff`（濾走 marker 與空行）證實 1,220 行入面**只有預期那幾行改動**，其餘一字不動。
  5. **順手修好一個隱形 bug**：`lifecycle-conflicts-resolved` 這個 field marker 因疊在檔頂，`fieldValueAfterMarker()` 向下抓到 `## User Environment` 的 **Repo path** 當值 —— 該 check 一直靠垃圾值「通過」。收工時再犯同一原理的變種（在 log 散文入面寫出 marker 全名會被 `indexOf` 先抓到），已全檔掃描並改寫成不連續寫法，掃描結果 0 collision。
  6. **第三層：發現工具自己造成的資料損失**。`upgrade` 成功後 `doctor` 報 53/53 passed，但比對備份發現它把 `## Next Session Opening Message` **整段換成官方通用開場白**，並同時把 `START_NEXT_SESSION_PROMPT.txt` 由 70 行覆寫成 4 行 —— S215 那 **65 行**專案狀態（六個 commit 明細、`reset --hard` 事故必讀、四項已確立事實、未解決清單、`Post-startup first action`）在兩個 live 檔同時消失。由 CLI 備份取回，接在官方合約句之後重建，mirror 重生，`doctor` 仍 53/53。
  7. **逐檔核實無內容損失**：由 npm 取回 v0.3.29／v0.3.30／v0.3.32／v0.3.43 原檔逐一 `diff`，證實 `onboarding.md`／`integrations.md`／`knowledge.md`／`safety.md`／`writing.md`／`agent-governance.md` 六個 pack **與其綁定的官方版本逐字相同、零本地自訂**（`onboarding.md` 由 394 行縮到 241 行是官方改版，非專案內容流失）；`release.md` 消失行數 0；`RULE_PACKS.md` 少的一行被三行更細緻的官方 routing 列取代。
  8. **起手數字更正**：`git rev-list --left-right --count` 實測本地領先 `origin/main` **六個** commit，非交接記載的五個 —— 漏計的是 S215 自己的 closeout commit `6cb80c6`。四處記載已同步更正。
- **QC:** `agent-handoff-kit closeout-status --root .` —— lifecycle 與 sufficiency 兩道語意閘**通過**，整體報 `blocked`，唯一原因是 push 未獲授權（非治理狀態問題）。`agent-handoff-kit doctor --root .` **status: passed，53/53**（v0.3.66；工具／項目記錄／npm latest 三向對齊；prompt mirror 一致）。`upgrade` 自身報告 create 1 / merge 14 / skip 8 / **conflict 0**。gate 探針五項全 PASS。內容保全審計：逐檔比對升級前備份，所有「消失行」均已歸因為官方改版或本節刻意改動。**本節零程式碼改動，故 S215 產品側 QC（`regression:grounded` 48/48、`route_regression` 46/46、active gold 185）未重跑 —— 它們綁定的 commit 與檔案未變。**
- **Evidence disposition:** 升級逐步經過、conflict 逐個判斷依據、還原證據留在本條 log；當前狀態、六個 commit 與 17 個未提交檔、兩條新 OP 入 `SESSION_HANDOFF.md`；Kit 版本／新增檔／QC 指令／workspace identity 入 `PROJECT_INDEX.md`；本節 sync 義務與 blocked 理由入 `DOC_SYNC_REGISTRY.md`。「upgrade 會靜靜取代開場白、doctor 不會發現」屬跨 session 可重用教訓，已寫入開場白 ⚠️ 段；未升 `PROJECT_DECISIONS.md`，因本節是工具升級而非架構取捨。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` —— Governance rule change / Closeout-startup contract change / Workspace identity change / New file or directory 四行狀態已記於該檔 `## Session Sync Status`。`dev/DOC_SYNC_CHECKLIST.md` row「Governance rule change (AGENTS.md)」與「New governance file added to install」**blocked**：兩者要求同步 `INIT.md` FILE 1 mirror，但 `INIT.md`（1,036 行，2026-05-10）鏡像的是 package 化之前的 AGENTS.md 結構（§4a／§5a／§11a），v0.3.66 核心沒有這些章節 —— 要先決定 `INIT.md` 是否退役，已開為 OP ⑦。
- **Pending:** 七個本地 commit 未 push（待 Leonard 決定；本節 closeout commit 為其中之一）· 交接檔 8 個 marker 未有專屬章節（OP ⑥）· `INIT.md` 鏡像 blocked（OP ⑦）· 根目錄 v0.3.24 舊 Kit 未處理 · S212–S215 全部產品側遺留一項未動。
- **Risks:** ① 本地領先遠端七個 commit，而 Option A watcher bot 會繼續自行推送到 `origin/main`，時間越長分歧越大。② `AGENTS.md`／`CLAUDE.md`／`GEMINI.md` gitignored 且從未 tracked，本次升級對它們的改動不在版本控制內，唯一還原點是 `dev/governance_migrations/` 的備份目錄 —— 而 `.gitignore` 的 `AGENTS.md` 規則無前置斜線會在任何深度命中，**連該備份目錄內的 `AGENTS.md` 都被 ignore**（`git check-ignore -v` 實測命中 `.gitignore:9`），故升級前的 `AGENTS.md` 全世界只剩磁碟上一份。③ 根目錄與 `Draft/` 兩份獨立 Kit 安裝版本不同（v0.3.24 vs v0.3.66），日後容易撞混。④ `qc_report.json` overall ERROR 未處理（同 S215）。
- **Log maintenance:** 無觸發。主 log 實數 **6 條** entry、**443 行**（門檻：11 條或 1500 行），`dev/SESSION_LOG_archive/` 不存在故 N≥11 歸檔規則未啟用；`PROJECT_DECISIONS.md` 觸發條件 (b) 不成立（交接檔無 ≥30 條的 decisions-like 章節）、(c) 判為不成立（工具升級非架構取捨）。10-closeout backstop：主 log 6 條加 `dev/archive/` 三個季度檔，**確切 closeout 數無法可靠判定**，故按規則保守處理 —— 本節不做全量維護，並在此記明下一節應重新評估 backstop 是否到期。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成 58 行，經 `doctor` prompt mirror check 讀回報 ok；全文按契約不複製入本 log。
<!-- ack:log-entry:end -->


<!-- ack:log-entry:start -->
## 2026-09-07 Session 215 — 起手探針揪出四項漂移，收妥 Codex 兩節工作；中途一條錯誤的回退指令造成資料損失

- **ID:** `Claude_20260907_1400` — S215
- **Summary:** 由「開工」起做起手探針，發現交接四項數字全部過時（成因是 Option A watcher bot 09-05 自行推送兩次入庫，非人手）。盤點 Codex 交低的 97 個髒路徑並分批 commit。中途 Claude 交出一條附帶錯誤保證的回退指令，Leonard 執行後造成資料損失，其後逐項救援並驗證。
- **Changed:** 五個本地 commit（全部未 push）——`05854d5` 19 個 extract 補回 title/url header（正文位元組不變）· `3f31905` 評測工具＋30 個 eval_runs artifact＋active gold 185 · `8d90e56` S214 七份報告 · `5f7ce6e` 治理文檔 · `744a8dc` S214 候選全套（11 檔 +968 −26，三個 flag 全 `0`）。收工另寫 `SESSION_HANDOFF.md`、`SESSION_LOG.md`、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:**
  1. **四項漂移實測更正**：Supabase 17,602→**17,610**（唯讀 count）；`source_registry` 279→**281**（`qc_report.json`）；線上部署 `f513a18`→**`4a25a15`**（Render `/health`）；`HEAD==origin/main` `05ea10e`→**`463434c`**（`git fetch` 後）。
  2. **推翻交接「RPC 未安裝」**：以零列探針（`source_ids=[]`，不觸發 per-row vector cast）呼叫 `match_wiki_chunks_routed` 得 `200 []`，四參數簽名相符 → **已裝**。同時證實線上 build 對它引用次數 0，且 PostgREST 讀不到函式本體，故安裝者、授權、與 repo SQL 是否相同三者皆無法核實。
  3. **揪出 merge 次序陷阱**：機械人 09-05 把 `edbc016_2026`／`edbcm141_2026` 加入 `SOURCE_SETS` 與 `SPOTLIGHT_SOURCE_IDS`，而 Codex 本地 `searchChannelB.ts` 對兩者引用次數為 0。只取任何一邊都會令 8 條片段跌出 route allowlist —— 與 `chi_hist_jss_ncs_2019` 同一病。故 rebase 必須先於驗證。
  4. **範圍修正**：原擬 step 1 收 89 項，查證 `groundedSynthesis.ts` 依賴新加的 `LlmJsonSchema` 後改為 85 項，全部 `backend/` 押後 —— 否則 typecheck 即紅、`package.json` 註冊的 `regression:grounded` 在乾淨 checkout 上會失敗。
  5. **`reset --hard` 事故救援**（見 Fix Record）。
- **Fix Record（本節事故）：**
  - **成因：** Claude 交出的回退指令 `git reset --hard origin/main && git stash pop` 附了「不會刪走那 60 個未追蹤檔」這句保證。該句是錯的：那些檔已入 commit、變成 tracked，`reset --hard` 會一併刪除；同時亦還原六個從未 commit 亦未 stash 的 backend 檔。
  - **損失：** 55 個 dev 側檔案由磁碟消失；`llmClient.ts`／`wikiRepository.ts`／`schema.sql`／`package.json`／`.env.example`／`backend/README.md` 六個檔的 Codex 改動被還原。
  - **救援：** 四個 commit 以 `git merge --ff-only 5f7ce6e` 救回（刻意**不用** `reset --hard`，以保住工作區改動）；`llmClient.ts`／`package.json`／`.env.example` 依本對話完整 diff 逐字還原；`schema.sql` 由倖存的未追蹤檔 `backend/supabase/s214_route_first_candidate.sql` 還原，diffstat 38 + 與原記錄吻合；`wikiRepository.ts` 由 gitignored 因而未被刪的 `backend/dist/lib/wikiRepository.js` 反建。
  - **等同性證明：** 反建的 TypeScript 重新編譯後，`wikiRepository.js` 與 `llmClient.js` 均與倖存 dist **逐位元組一致**（首次比對揪出一處差異：原版 `options` 為必填參數，修正後一致）。行為等同已證；源碼排版與 `queryVec` 註釋是新寫，非 Codex 原文，diffstat 因此由 97 變 107 行。
  - **未救回：** `backend/README.md` 5 行 flag 說明，無任何備份來源，**沒有杜撰補回**。
  - **通則已入長期記憶：** 交回退指令前先分三類數（commit 內／stash 內／只在工作區），明寫會永久失去甚麼，不寫「不會刪走」這種未經逐項驗證的正面保證。
- **QC:** `npm run check` exit 0 · `npm run build` exit 0 · `regression:grounded` **48/48** · `route_regression` **46/46**（含來源成員斷言）· `_s214_rank_model --self-test` ALL PASS · `eval_retrieval --self-test` ALL PASS · `_s213_validate_gold --self-test` ALL PASS · `footnote_lead_probe --self-test` PASS · active gold **185** · 工作區乾淨。事故期間 `regression:grounded` 曾為 47 PASS + 1 FAIL，成因是最後一項斷言讀被 stash 的 `searchChannelB.ts`，復原後回復 48/48。**未跑：185 題 live 套件。**
- **Evidence disposition:** 事故經過與逐項救援證據留在本條 log；當前狀態入 `SESSION_HANDOFF.md`；S212–S214 舊基線與舊 Open Priorities 全文移入 handoff `## Detail Archive`（程式化驗證逐字保留，87,154 ＋ 4,679 字元）；回退指令教訓入 Claude 長期記憶，並已交 playbook inbox 提案 `inbox/2026-09-07-policychecker-rollback-command-blast-radius.md`（該庫本地 commit `68683d8`，未 push；grep `INDEX_TABLE.md` 的 rollback／reset --hard／回退／undo 零命中，故開新提案而非補現有卡）。
- **Sync:** `qc_report.json` 由 CI 每日重生，本節未碰；`DOC_SYNC_REGISTRY` 無新映射需求（本節未新增受監察表面）；`PROJECT_INDEX.md` 的 S214 檔案映射由 `5f7ce6e` 帶入，本節未再新增檔案。
- **Pending:** 五個 commit 未 push（去向待 Leonard 決定）· 185 題 live 套件未跑 · 三題 chunk recall 未查 · 4 條 fidelity 不一致未修 · 合成窗佔用率未改善 · `backend/README.md` 5 行未補 · S212／S213 遺留全部未動。
- **Risks:** ① 本地領先遠端五個 commit，時間越長分歧越大，而 Option A watcher bot 會繼續自行推送。② `match_wiki_chunks_routed` 已在 live schema 但無安裝記錄，屬未登記的 schema 改動。③ `wikiRepository.ts` 為反建版本，行為等同已證但源碼非原文。④ `qc_report.json` overall ERROR 未處理。
- **Boundary:** 零 push、零 deploy、零 DDL、零 Supabase 寫入、零重切語料、零外部模型呼叫。唯一網絡動作：三個唯讀探針（HTTP GET ×2、Supabase count ×1）、一次 `git fetch`、一次 `git pull --ff-only`。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check` 回報 `trigger=False`（`line_count=337`、`entry_count=5`，未達 400 行／30 日兩個閘），故本節不執行歸檔。⚠️ 寫入本條目後檔案為 **440 行**，已越過 400 行閘 —— **下一次收工的 §4a 檢查會觸發**，屆時須先跑 `--apply` 歸檔再寫新條目。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy：只讀 "Leonard's playbook/playbook/INDEX.md"；全表在 INDEX_TABLE.md，撞到才 grep，配到才開卡，用完補一行 usage。)

Current state (S215, 2026-09-07)：平台 v3.3.2；Supabase 17,610；source_registry 281；
guidelines.json _meta 2.6.1；knowledge.json 2.3.0 · facts 455；凍結合約零接觸。
origin/main = 463434c；本地 HEAD 領先五個 commit，全部未 push；線上部署 = 4a25a15。
本節零 push、零 deploy、零 DDL、零 Supabase 寫入、零重切語料。

🔴 最高優先：五個本地 commit 未 push，去向要 Leonard 決定。
   744a8dc  S214 候選全套（grounded synthesis + route-first），三個 flag 全部 0，
            產品 verdict 仍為 FAIL，185 題 live before／after 未跑
            —— 未驗證前不得啟用任何 flag、不得部署。
   5f7ce6e  治理文檔（handoff / log / index / master spec / codebase context / 啟動提示）
   8d90e56  S214 七份報告
   3f31905  評測工具 + 30 個 eval_runs artifact + active gold 185
   05854d5  19 個 extract 補回 title/url header，正文位元組不變
   後四個全部不改檢索行為。

⚠️ S215 事故必讀（同類錯誤不要重犯）：
   Claude 交出的回退指令附了「不會刪走未追蹤檔」這句錯誤保證，Leonard 據此執行，
   git reset --hard 刪走已 commit 的 55 個檔，並還原六個從未 commit 亦未 stash 的 backend 檔。
   已復原：四個 commit 用 merge --ff-only 救回（非 reset，故工作區改動保住）；
   llmClient.ts / package.json / .env.example 逐字還原；
   schema.sql 由倖存的 s214_route_first_candidate.sql 還原（38 +，與原記錄吻合）；
   wikiRepository.ts 由 gitignored 的 backend/dist 反建 —— 重新編譯後與倖存 dist 逐位元組一致，
   即行為等同已證，但源碼排版與 queryVec 註釋是新寫的，不是 Codex 原文。
   救唔返：backend/README.md 5 行 flag 說明，無備份，沒有杜撰補回。
   通則：交回退指令前先分三類數（commit 內／stash 內／只在工作區），明寫會永久失去甚麼。

✅ S215 已確立的事實（不必再查）：
   1. match_wiki_chunks_routed 已裝於 live Supabase —— 零列探針（source_ids=[]，不觸發
      per-row vector cast）回 200 []，四參數簽名相符。但 PostgREST 讀不到函式本體，
      「已裝」不等於「與 repo SQL 相同」；安裝者與授權無記錄；線上 build 引用次數 0。
      任何 DDL 前仍須先確認 live 定義，不得憑此重做安裝。
   2. searchChannelB.ts 已完成兩邊合併並驗證：機械人 09-05 加入的 edbc016_2026 /
      edbcm141_2026（SOURCE_SETS + SPOTLIGHT）與 Codex 的 route-first wiring 並存，
      零衝突標記，route_regression 46/46 含來源成員斷言。只取任何一邊都會令 8 條片段
      跌出 route allowlist —— 與 chi_hist_jss_ncs_2019 同一病。
   3. 交接數字漂移的成因是 Option A watcher bot，不是人手改動：09-05 兩次自動入庫
      （edbc016_2026 +6、edbcm141_2026 +2），Render 見 main 有新 commit 即自動部署。
      那五個 remote commit 不含後端程式碼實質改動，線上檢索行為等同 S214 所述的舊 build。
   4. qc_report.json（CI 2026-09-06）overall ERROR：6 FAIL 之中 5 條屬既有 registry 家族
      （ZOMBIE / PHANTOM / SERIES / UNMANAGED / UNLISTED）；NO_MIDCLAUSE_START 843（基準 835），
      09-03 已經是 842，兩條新入庫片段只帶來 +1，不是新缺陷類別。

⚠️ 未解決（不要當已解決）：
   · 三題 chunk recall：hr_lsp 完整公式跨第 3／4 頁而 dominant_page() 判第 3 頁；
     sen_special_school_curriculum 的 g10 與中史 NCS 目標片段均未入首 8。
     已證目標 chunk 根本不在新 RPC 原始 40 項之內，故根因不在後處理，
     下一步是離線查 query expansion 與向量排名。
   · 4 條 fidelity 不一致：3 條分數完全相同而生產 tie 次序非 id 升序（真正 tie 規則
     未查證，不得憑猜對齊）；1 條 fin_seg 的 edbc015_2026 未解釋。
   · 合成窗 overlay 平均佔 2.22/5 格（44%），正負 lead_score 分佈重疊，
     純提高門檻在數學上不可行。
   · backend/README.md 5 行未補。
   · S212／S213 遺留全部未動：658 代號標題 backfill（dry-run 已跑，執行被分類器擋住，
     須 Leonard 自己跑）、kgecg_2017 108 條 ZOMBIE、header 剝除正則吃掉 33 行正文
     （涉 2,212 條 chunk，修正要重入庫）、七個 standing WARN 無 waiver。

QC status（S215 收工實測）：npm check exit 0 · npm build exit 0 · regression:grounded 48/48
   · route_regression 46/46 · _s214_rank_model ALL PASS · eval_retrieval ALL PASS
   · _s213_validate_gold ALL PASS · active gold 185 · 工作區乾淨。
   未跑：185 題 live 套件。

Post-startup first action: 先做起手探針（served app.html PLATFORM_VERSION + Render /health
+ git fetch 後比對 HEAD／origin/main + Supabase live count），再向 Leonard 報告五個未 push
commit 的去向建議。未得明確批准，不得 push、不得部署、不得啟用任何 flag、不得執行 DDL、
不得作任何外部模型批次。如無新指示，行離線工作：追三題的 query expansion 與目標片段位置。
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-09-07 — 接續啟動與 route-first artifact 離線覆核

- **Done:** 核對已保存三題 before／after、active gold signature 及 RPC trace；發現「未安裝」交接與 artifact 不一致，沒有重新安裝。
- **QC:** NFKC／空白正規化比對：hr_lsp 舊策展 signature 兩邊位於 1；另外兩題兩邊均缺指定 signature。完整公式 chunk 兩邊缺席。新 RPC 三次 200、一次 57014 後成功；此為既有 artifact，非本輪 live 呼叫。
- **Evidence disposition:** `dev/_s214_route_first_focused_review.md` 保存覆核；handoff 加入現況限定，index 登記報告。
- **Sync:** 無產品程式修改；DOC_SYNC_REGISTRY 新檔映射已更新 index；無公開文件或外部同步需要。
- **Boundary:** 本輪零外部 API／DDL／commit／push／deploy。HEAD 與本地 origin/main 同為 05ea10e，未 fetch，不能代表遠端即時狀態。
- **Persistence:** Lightweight checkpoint；不重生啟動提示，不作 full closeout。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-05 Session 214 — Phase 1.1 收官、排序根因定案、測試基建落成，並改了一個未提交的生產檔

- **Codex continuation checkpoint（2026-09-05 至 09-06）：** 在既有排序候選上新增 feature-flagged grounded synthesis（`groundedSynthesis.ts`）、strict Structured Outputs 支援及離線回歸／模型 probe。兩個 flags 預設關閉；零 commit、零 push、零 deploy、零 Supabase 寫入。第一批固定 40 題錄得 56 個成功模型輸出（40 draft／16 judge），但 SDK 預設重試未關閉，HTTP 嘗試總數不可核證；分組實數為 19 條不可答、21 條可答，分別 17/19 棄權及 13/21 作答。人工覆核裁定候選 FAIL：兩個 audience blocker、核心子類別遺漏、正控誤拒答、4 個答案只由策展 footnote 支持、gold label 漂移。其後離線新增 `applicable` 閘、唯一引文跨片段重綁、來源標記防仿冒及 `maxRetries:0`／attempt 落盤；Leonard 批准方案 A，grounded synthesis 現只准 `vault_extract` 支持最終答案。Leonard 再批准第二批同範圍最多 80 次 HTTP 嘗試；post-fix artifact 實錄 `attempted_api_calls=54`，等於 40 draft＋14 judge。兩個 audience blocker已棄權、12 班題已答對，但 OCR 四重複詞進入答案，以及 `qa_esr_no_fixed_cycle` 截斷兼離題句獲 judge 接納，故外部模型 verdict 仍 FAIL。其後加入兩道 judge 前的保守輸出衞生閘：80 字以上 prose claim 必須完整收句；2–16 字元片語連續重複至少三次即拒絕。新增三項回歸後 `regression:grounded` 47/47；第二批全 40 題 artifact 離線重播只有兩個目標 blocker 轉為棄權，其餘 38 題逐字不變；typecheck、build、`git diff --check`、路由回歸 46/46 全綠。semantic regression 為 24 PASS、1 PASS-with-notes、1 FAIL；唯一 FAIL 是既有測試仍預期 `guidelines 2.5.0`，權威值已為 2.6.1，與本次 helper 改動無關，故未順手修改。三個 Codex 子代理第二輪覆核均因額度上限未能執行，沒有修改或外部呼叫，不能列作獨立 QC 完成。報告=`dev/_s214_grounded_acceptance_report.md`；artifacts=`2026-09-05_s214_grounded_synthesis_probe_acceptance_v1.json`、`acceptance_v2.json`。操作邊界：Claude 只用 CLI Plan 額度；Codex 每批外部 API 呼叫均須先取得 Leonard 明確批准。
- **Codex gold／棄權覆核（2026-09-06）：** 發現模型 probe 當時先 `.slice(0,5)` 才移除策展摘要，與生產「先篩 `vault_extract`，再取五格」不一致，18／40 題證據窗受影響；至少 `hr_lsp`、`hr_lang_req` 的正確來源因此被排除。舊兩批 artifact 降格為 harness-confounded，不可直接作 release 判決。已新增共用 `selectPrimaryEvidence()` 並由生產及 probe 使用，生產行為不變；新增選窗回歸後 `regression:grounded` 48/48，typecheck、build、diff check 全綠。另完成兩條 NCS label 重審、四條 rubric drift 及逐層棄權分類，見 `dev/_s214_gold_abstention_review.md`。probe 新增 `--acceptance-affected`（18 題、最多 36 次 HTTP）及 evidence-window fingerprint；無批准參數的 preflight 如期在建立模型 client 前停止。本步沒有外部 API 呼叫、commit、push、deploy 或 Supabase 寫入。
- **Leonard 批准 gold 修訂（2026-09-06）：** 兩條舊 NCS 從 active set 移出並完整保存於 `dev/source/gold_deprecated_s214.json`；新增 `ss_ncs_chinese_framework_progress_v2` 及 `ss_ncs_history_adapted_outline_v2`。`gov_imc_60pct` 收窄至 60% 上限，另拆 `gov_imc_alternate_excluded_v2`；`hr_lang_req`、`plc_central_alloc_confusable`、`saf_disease_notification` 改為 query 與一手 passage 完全對齊。Active gold 184→185，ID 185/185 唯一；七條新／修訂標籤以保存 evidence＋本地 extract 的最小 cache 驗證 7/7，gold validator／runner／metrics self-test 全綠。原全庫 cache 路徑已失效，未擅自連接 Supabase，故完整 185 條 corpus revalidation 尚待新唯讀 snapshot。probe 18 題模式改讀 active gold query 並記錄 evidence 原始 query；舊 40 題 mode 遇 deprecated fixture 會 fail closed。本步零外部 API、零 commit、零 push、零 deploy、零 Supabase 寫入。
- **Leonard 批准 V3 批次（2026-09-06）：** 以 OpenAI Responses API 跑 `--acceptance-affected` 18 題，draft=`gpt-4.1-nano`、judge=`gpt-4.1-mini`、`maxRetries=0`，實錄 `attempted_api_calls=25`（18 draft＋7 judge；批准上限 36）。不可答題 9／9 全部棄權、0 錯答；可答題 6／9 作答、3／9 棄權。人工覆核為 4 個完整 PASS、2 個安全但不完整、3 個棄權／證據不足；未再出現 audience 錯答、OCR 重複或截斷。`gov_imc_60pct` 因 gold query 已改但保存 evidence 仍來自舊 query，V3 對該新 rubric 不具判決力；`hr_lsp` 與 `sen_special_school_curriculum` 的目標 passage 未進五格。Verdict 維持 FAIL；下一步是五條新鮮 retrieval fixture及兩條完整性回歸。Artifact=`dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_acceptance_v3_windowfix.json`；人工覆核=`dev/_s214_grounded_v3_review.md`。本步零 Supabase 寫入、零 commit、零 push、零 deploy。
- **Leonard 批准五題 fresh retrieval（2026-09-06）：** 固定 5 次 Render `synthesize:false`，無重試；後端每題使用 `text-embedding-3-small` 並唯讀查 Supabase。結果 2 PASS／1 PARTIAL／2 FAIL：中文第二語言框架及校董 60% 正文入首 5；長期服務金一手片段有部分註釋但欠完整基本公式；特殊學校 `g10` 及非華語中史目標來源未入首 8。根因覆核發現 `chi_hist_jss_ncs_2019` 已入庫但漏 `SOURCE_SETS.curriculum`，已作最小 allowlist 修正並加來源成員斷言；`g10` 已在正確 route，未猜測加入 spotlight。另更正 `gov_imc_60pct` gold 的錯亂 signature、頁碼 21→4 及 chunk id。QC：route 46/46 + 成員斷言 PASS、grounded 48/48、typecheck、gold self-test、JSON parse、diff check 全綠。Artifact=`dev/source/eval_runs/2026-09-06_s214_fresh_retrieval_5.json`。本步零 Supabase 寫入、零 commit、零 push、零 deploy。
- **Leonard 批准候選中史 route 單題驗證（2026-09-06）：** 第一次本機請求因 `.env` 缺 `SUPABASE_URL`／`SUPABASE_ANON_KEY`，在任何 OpenAI／Supabase 調用前 fail closed，不能判分；其後按既有唯讀 fallback，以本機 service key 配合已登記 Supabase URL 完成同一批准範圍內的一次 `synthesize:false` 查詢。allowlist 修正令 `chi_hist_jss_ncs_2019` 由首 8 缺席升至 rank 0／1／3，但蒙古崛起第 17 頁目標片段仍未進首 8：Source Recall 修好，Chunk Recall 仍 FAIL。Artifact=`dev/source/eval_runs/2026-09-06_s214_ncs_history_candidate.json`。沒有重試、synthesis、Supabase 寫入、commit、push 或 deploy。
- **長期服務金離線根因（2026-09-06）：** 完整公式並非語料缺失；它在 `vault_long_service_payment_guide_ab49f971fc3d2752`，但 fresh retrieval 未取回。該 chunk 橫跨第 3／4 頁，公式實際在第 4 頁，現行 `dominant_page()` 卻判第 3 頁。嘗試把 `hr_lsp` gold 由策展摘要改指一手公式時，validator 正確揭示這個 mismatch；為免用錯誤第 3 頁換取綠燈，已撤回 gold 改動並記錄 schema 缺口：未來須分開 source-truth page 與 observed product page。這項與 `g10`／中史 NCS 一同歸類為長篇／表格式文件 chunk-boundary／ranking blocker。
- **Phase B route-first 候選（2026-09-07）：** 離線二／三字元 IDF 反例證實，路由內排名可把中史目標升至 rank 0、長期服務金兩個公式升至 rank 0／4，亦可把足以回答的 `g10` 相鄰片段升至 rank 1；但 gold 指定 `g10` chunk 因同詞片段大量同分只到 rank 12，故 lexical 不可單獨作主排名。已新增預設關閉的 `FEATURE_ROUTE_FIRST_SEARCH`、獨立 `match_wiki_chunks_routed` exact RPC 及 fail-open fallback；不 overload 舊 RPC，共用 query embedding，補回三次限定 `57014` 重試。Claude Code CLI Plan session 唯讀覆核為 PASS-with-flags、無 blocker；本地 typecheck、build、grounded 48/48、route 46/46、retry mock、diff check 全通過。RPC 未安裝，未做 live 185 題 before／after，產品 verdict 仍 FAIL；零 Supabase 寫入、commit、push、deploy。
- **ID:** `Claude_20260904_1204`（S214），2026-09-04 → 09-05 跨午夜，中途機器休眠一次。Codex 以 QC Governor 身分逐 gate 下單。
- **Summary:** 四個 gate：Phase 1.1（五項全完成）→ Gate 1 根因分析（唯讀，經兩輪 QC 退回修訂）→ Gate 2A1 測試基建 → Gate 2A2／2A2b 生產實作。**零 commit、零 push、零 deploy、零 Supabase 寫入、零重切語料。**
- **Changed:**
  - 生產（**未提交**）：`backend/src/api/searchChannelB.ts`（+31 −21，三處：`mainSearchLead` 在 overlay 前明確擷取、establishment dedup 方向對調、establishment 插入位置改前置）
  - 評測工具：`dev/source/eval_retrieval.py`（NFKC `fold()` ＋ 14 條 self-test）、`dev/source/footnote_lead_probe.py`（`window_of()` 記錄完整 top-8 ＋ 5 條 self-test，舊欄位零改動）
  - 新增：`dev/_s214_rank_model.py`、`dev/_s214_gate2a1_replay.py`、`dev/_s214_phase_1_1_report.md`、`dev/_s214_phase_2a1_gate2a1_report.md`、`dev/_s214_gate2a2_implementation_report.md`、`dev/_s214_inspect_fields.py`、`dev/_s214_nfkc_diff.py`
  - 新 artifacts：`2026-09-04_s214_gate2a1_footnote_probe.json`、`_gate2a1b_replay.json`、`_gate2a2_replay_postimpl.json`、`2026-09-05_s214_gate2a2_local39.json`
- **Done:**
  - **Phase 1.1 A–E 全部完成**。C 項的關鍵修正：`forbidden_hits` 4/4 進首五格，但**只有 1/4** 可證答案實際採用並造成對象混淆 —— 不可再把曝光寫成「答案引用」。D 項**否決全域 score sort**（Source@1 升但 Chunk@5 由 0.273 跌至 0.245，且把 `g19` 禁用來源推上榜首）。
  - **Gate 1 根因定案**：`searchChannelB.ts:1495` `[...lead, ...rest]` 無條件前置；lead 資格只看絕對門檻（0.45 ＋ 2 bigram），從不與被壓者比分。`:1146` 註釋寫明意圖是 top-5 **成員資格**，實作卻給 **index 0**（位置）——此落差即根因。
  - **Gate 2A1**：`_s214_rank_model.py` T1–T14 **41 條斷言 ALL PASS**；43 條 live probe 跑完（正向 30/30，errors 0）；fidelity **174/184 → 180/184**。
  - **Gate 2A2b**：Codex local 行為 QC 用 `staff_fullday_24` 揪出真缺陷並修好，`npm run check` 通過。
- **Fix Record:**
  - **問題**：fidelity 檢查在「全部跳過」時回 exit 0，讀成「檢查過冇事」，但其實一條都冇驗到。**修**：改為三態，`NO_EVIDENCE`=2 / `FAIL`=1 / `PASS`=0。**驗**：184 題檔實測回 exit 2。
  - **問題**：`classify_recorded` 的 spotlight 判別只看來源是否在 `SPOTLIGHT_SOURCE_IDS`，但 `staff_est_pri`／`edbcm116_2026` 本身憑分數就攞第一 → 184 條之中誤判 6 條，每條靜靜丟失一個 chunk。**根因**：set 成員資格 ≠ 強制插入。**修**：必須同時違反分數次序（後面有更高分項目）才判定為 spotlight。**驗**：fidelity 174→180/184，並加兩條專門斷言（正例／反例各一）。
  - **問題**：我在 Gate 1 寫「註腳正控集不存在」。**實際存在**（`footnote_lead_probe.py` ＋ `2026-07-28_s196_fnlead_final.json`，26/26 正向保住 lead）。**已收回並更正。**
- **QC:** `eval_retrieval.py --self-test` ALL PASS · `_s214_rank_model.py --self-test` 41 條 ALL PASS · `footnote_lead_probe.py --self-test` PASS · `backend` `npm run check` 通過 · 起手探針全綠（app.html 200／3.3.2、Supabase 17,602、registry 279、guidelines 2.6.1、HEAD==origin/main 05ea10e）。
- **Evidence disposition:** 詳細技術證據 absorbed into `dev/_s214_phase_1_1_report.md`、`dev/_s214_phase_2a1_gate2a1_report.md`、`dev/_s214_gate2a2_implementation_report.md`；交接只留指標，不複製內容。
- **Sync:** `dev/SESSION_HANDOFF.md`（Current Baseline / Open Priorities / Last Session Record / Next Session Opening Message / State Reconciliation Check 全部重生）、本檔、`START_NEXT_SESSION_PROMPT.txt`（由 opening message 重生 ＋ mirror check）。`DOC_SYNC_REGISTRY.md`：本節未改動對外行為或公開文案（生產改動未部署），**無新增 sync 義務**。
- **Pending:** 184 題 live 套件未跑；生產改動未 commit／未 push／未部署；4 條 fidelity 不一致未修；合成窗佔用率（44%）未處理；S213 遺留 ④⑤⑥ 全部未動。
- **Risks:** 🔴 **工作區有一個未提交的生產檔改動，會改變每一條查詢的結果次序。** 已通過 typecheck 但未跑 live 套件。下一節開工必須先向 Leonard 報三個選項（驗證後 push／stash／還原），不得自行決定。⚠️ 本節部分回合已不在 agent 上下文內，**檔案逐行歸屬無法可靠重建**，以兩份報告為準，不要憑 mtime 推論作者。
- **Log maintenance:** no-op —— 本檔 4 條 entry、288 行，未達 §4a 觸發條件（>400 行 或 最舊 entry >30 日），亦未達 core §4.11 的 N≥11／1500 行門檻。

### Next Session Handoff Prompt (Verbatim)

見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block；`START_NEXT_SESSION_PROMPT.txt` 為其逐字鏡像（本節 closeout 已做 mirror check）。

## 2026-09-04 Session 213 — 為檢索準確度建可信基線；順帶揪出 658 條代號標題的根因

- **ID:** Claude_20260904_1125（S213）。由「開工」起，Leonard 中途轉單三次：install playbook → 全做 OP → Codex 的 Phase 0／1 檢索基線 brief。
- **Summary:** 交付一套可信的檢索準確度量度能力，並第一次量到真實水平。舊 eval 的「PASS 27/39」用準確度語言講就是 Source Recall@8 = 1.000，而且是恆真的。新建 162 條 gold set 量出 Source Recall@1 = 0.364、Chunk Recall@5 = 0.273。**零生產寫入、零 deploy、零重切語料。**
- **Changed:**
  - 新（Phase 1 量度工具，不改生產）：`dev/_s213_corpus.py`、`_s213_eval_metrics.py`、`_s213_run_gold.py`、`_s213_validate_gold.py`、`_s213_build_gold_staffing.py`、`_s213_recon.py`；gold set 五個 JSON（`_s213_gold_all.json` 162 條）；兩個 eval run（`2026-09-03_s213_phase0_baseline.json`、`2026-09-04_s213_gold_baseline.json`）
  - 改（Phase 2 候選修正，未 deploy 未入庫）：`dev/vault/build_wiki_index.py`（缺 `# title:` 由靜默 fallback 改為 fail loud）、19 個 vault extract 補回 `# title:`／`# url:` header、`dev/_s213_fix_extract_headers.py`、`dev/_s213_title_backfill.py`（542 條標題回填，dry-run 已跑，**未執行**）
  - `AGENTS.md` §14 playbook pointer v2 → v3（該檔在 `.gitignore`，只存在於本機）
- **Done:**
  - **OP⑦ 根因查實。** 交接寫「658 條片段以內部代號做標題，要 Supabase UPDATE」—— 那是症狀。真因是 `dev/vault/build_wiki_index.py:267-268` 的靜默 fallback：extract 缺 `# title:` 就拿 source_id 頂替、缺 `# url:` 就留空。**集合相等證明：庫內帶代號標題的 source_id 19 個、extract 缺 title header 的 19 個、交集 19、兩邊獨有各 0。** 同一行代碼同時製造 `SOURCE_TITLE_REAL`(658) 與 `ANCHOR_URL_PRESENT` 的無連結片段，兩個檢查一直當成兩件事。
  - **源頭已封死**：19 個 extract 補回 header（逐檔斷言正文位元組不變，故 chunk hash 不動、毋須重新 embedding）；守門改為 fail loud 並**證明會紅**（造假檔觸發、逃生門 `ALLOW_UNTITLED_EXTRACT=1` 亦驗過）。現時 265 個來源乾淨載入，源頭代號標題 0、缺連結 0。生產庫 658 條未動。
  - **Phase 0 凍結基線**：39 條 legacy 集重跑，PASS=27／FAIL=0／RECORD_ONLY=12／chunk PASS=2／errors=0，與 `qc_report` 的 `EVAL_LATEST` 逐項一致。
  - **Phase 1 gold set 162 條**：18 個政策範疇（14 個 ≥10 條）、143 可答＋19 無答案、錯字／簡稱／英文／自然句 39、易混淆 25、dev 114／held-out 48。每條標籤由語料現場抽出，經 `_s213_validate_gold.py` 獨立重驗（chunk 存在、簽名真在清洗後正文、頁碼等於 `dominant_page`、無答案題反向證明零命中）。
  - **`wiki_chunks` 無 `page` 欄** —— 頁碼是查詢時由 `=== Page N ===` 標記推導。已逐行移植 `extractDominantPage`（`searchChannelB.ts:1054`）並對四種語意驗證。
- **關鍵數字（`_s213_eval_metrics.py`，162 條 gold set，top_k=8，`synthesize:false`）:**
  - Source Recall@1／@3／@5／@8 = 0.364／0.552／0.636／0.706；MRR 0.474
  - Chunk Recall@1／@3／@5 = 0.119／0.245／0.273；MRR 0.184
  - 143 條可答題之中 **42 條在 8 格內完全搵唔到正確來源**
  - dev 0.340 ／ held-out 0.419（@1）—— held-out 略高，未見過擬合
  - 22 條查詢有單一來源佔窗一半或以上（最多 5 格）；逐字重複格位 0
  - 60/162 結果不是分數遞減排列，該 60 條位 0 全部是 `footnote_curated`
- **語料層兩個新缺陷（已量、未修）:**
  1. **CJK 相容表意文字 868 條 chunk（4.93%）、112 個來源、110 個不同變體字**（例：理 U+F9E4 而非 U+7406）。肉眼相同、位元組不同。**現行 `eval_retrieval.chunk_verdict_for` 只用 `squeeze()` 比對、無 NFKC folding，所以目標段落落在這 868 條之中時，正確檢索會被判 FAIL。** S213 全套工具比對前已 fold。
  2. **header 剝除正則吃掉正文的 `# ` 開頭行**：16 個來源、33 行真正消失（涉 2,212 條 chunk）。實例：`g24` 一行強制舉報懷疑虐兒的交叉引用。
- **本 session 自己犯咗而值得記低的錯：**
  1. **未實測就報血緣範圍。** 我掃出「23 個檔正文有 `# ` 行」就推論全部被刪、報 55 行／3,714 條／21.1%。逐條實測後真數是 16 個來源／33 行／2,212 條，而我舉的頭號例子 `staff_est_pri` 恰恰**沒有**受影響（它走 `extract_table_rows.py`，不經那個正則）。
  2. **工具兩個缺陷會污染整個 gold set**，而且 agent 已在用：`find`／`show`／`signature` 一律印 `page=None`（讀了不存在的欄）；`signature` 由原始文字切片，`--start 0` 會切出 `===Page1===`，而後端回傳前會剝走標記 —— 這種簽名永遠對不上正確答案。已修並通知 agent 重驗。
  3. **只 fold 了一邊。** 加 NFKC 後通過率由 83/83 崩到 43/123；乾草堆 fold 了、針沒有。
  4. **標記檢查過度觸發。** 寫 `"=" in s` 想擋 `=== Page N ===`，結果擋了空調津貼公式「（SAC）＝1個課室率」的全形等號（NFKC 後變 ASCII）。改認 `===` 與 `Page\d`。
  5. **越界結論：「系統沒有棄權能力」。** 我用 `synthesize:false` 跑，`judgeCanAnswer`／`SYNTHESIS_DECLINE`（`searchChannelB.ts:917/924/1016`）由頭到尾冇行過。應該寫「本次量度觀察不到棄權層」。
  6. **`forbidden_hits` 我寫成「引用」。** 它只證明禁用來源出現在結果窗，未證明答案採用其內容。
- **QC:** 全部 self-test 綠 —— `_s213_eval_metrics` 12/12（覆蓋 brief 要求的六種必須能顯示的失敗）、`_s213_run_gold` 7/7、`_s213_validate_gold` 9/9、`_s213_build_gold_staffing` 10/10、`_s213_fix_extract_headers` 6/6、`_s213_title_backfill` 10/10。gold set 驗證 162/163 通過、隔離 1（`dig_byod_mandatory_na` 聲稱無答案但「自攜裝置」有 1 條命中）。兩次 live run 共 201 條查詢、errors=0。
- **Evidence disposition:** 量度工具與 gold set 待 indexed in `dev/PROJECT_INDEX.md`；兩個語料層缺陷與五項 Codex 更正 absorbed into handoff；其餘 kept as recent trace evidence。
- **Sync:** 本節零生產改動，`qc_report` 數字未變（17,602／658／130／842）。DOC_SYNC 未命中新行。
- **Pending:** Codex 的 Phase 1.1 A–E，見 Open Priorities。
- **Log maintenance:** `session_log_maintenance.py --check` 報 `trigger=False`（162 行／2 個 entry，門檻 400）。無 op。`PROJECT_DECISIONS.md` 觸發條件 (c) 成立（多選項架構取捨：全域 score sort vs 結構化 exact-match 優先 vs 現行 forced-footnote），已於下一節列為待辦而非本節寫入，因為三者的反事實量度是 Phase 1.1 D 的交付。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: 只讀 "Leonard's playbook/playbook/INDEX.md"；全表在 INDEX_TABLE.md，撞到才 grep，配到才開卡，用完補一行 usage。)

Current state (S213, 2026-09-04): 平台 v3.3.2；Supabase 17,602；source_registry 279；
GUIDELINES_REGISTRY 177；凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S213 零生產寫入、零 deploy、零重切。HEAD == origin/main，但**工作區有未提交改動，開工先分類再決定**。

⛔ 未提交改動的分類（Codex 要求，勿混合提交、勿還原）：
  A. Phase 1 量度工具（不改生產，可獨立提交）：
     dev/_s213_corpus.py / _s213_eval_metrics.py / _s213_run_gold.py / _s213_validate_gold.py
     dev/_s213_build_gold_staffing.py / _s213_recon.py
     dev/_s213_gold_{all,staffing,curriculum,kg_safety,cpd_digital}.json
     dev/source/eval_runs/2026-09-0{3,4}_s213_*.json
  B. Phase 2 候選修正（改了行為，未 deploy、未入庫，**先等批准**）：
     dev/vault/build_wiki_index.py（缺 title header 由靜默 fallback 改為 fail loud）
     19 個 vault extract 補 header + dev/_s213_fix_extract_headers.py
     dev/_s213_title_backfill.py（542 條標題回填，dry-run 跑過，**未執行**）
  C. 他人工作：無。Codex brief 講 dev/DOC_SYNC_CHECKLIST.md 與 dev/PROJECT_INDEX.md 有未提交
     修改 —— 實測兩者乾淨，該前提不成立。

📊 S213 量到的真實水平（162 條 gold set，top_k=8，synthesize:false）：
   Source Recall@1/@3/@5/@8 = 0.364 / 0.552 / 0.636 / 0.706；MRR 0.474
   Chunk  Recall@1/@3/@5    = 0.119 / 0.245 / 0.273；MRR 0.184
   143 條可答題之中 42 條在 8 格內完全搵唔到正確來源。
   舊 39 條集的「PASS 27/39」＝ Source Recall@8 = 1.000，而且恆真（FAIL=0 的定義就是如此）。

🔴 產品 verdict：FAIL（Chunk Recall@5 = 0.273）。工具 verdict：Phase 1 完成。
   兩項要分開講，不可合併成一句。

⚠️ Codex QC 五項更正（已接受，但第 1 項的前提我實測係錯的）：
  1. Codex 話「S213 Gold Set 使用 synthesize」—— **不成立**。eval_retrieval.py:251 寫死
     "synthesize": False，gold run 冇用過 synthesize。但佢個結論仍然啱，只係理由相反：
     正因為關咗，judgeCanAnswer / SYNTHESIS_DECLINE / trustedVaultLead
     (searchChannelB.ts:917/924/1012/1016) 由頭到尾冇行過，所以觀察不到棄權層。
     我原本寫「系統沒有棄權能力」係越界，應為「本次量度觀察不到棄權層」。
  2. forbidden_hits 只證明禁用來源出現在結果窗，非「答案引用」。要 synthesize 才講得到。
  3. 60 條註腳置頂與 Recall@1 較低（0.308 vs 0.396）係相關性，不是因果。
  4. S213 runner 已做 NFKC，故 gold set 指標有效；缺陷在 canonical eval_retrieval.py。
  5. 樣本不足的不只 info_security(2)：kg_admission(4)、kg_operation(5)、
     digital_education(6) 同樣少於十條。

🚫 QC Governor 裁示：暫不批准直接按 A → C → B 改生產。**禁止**以全域 score sort 作修法 ——
   Codex 實測純 score 重排 Source Recall@1 升至約 0.420，但 Chunk Recall@5 反跌至約 0.245。
   （此數由 Codex 提供，S213 未獨立複核。）

NEXT = Phase 1.1「量度修正與決策證據」，做完停下等 Leonard 批准，不得 deploy／寫 Supabase／重切：
  A. 把 NFKC folding 加入 dev/source/eval_retrieval.py 的 chunk matching；加 self-test 證明
     相容碼位會命中、不同漢字不會誤命中；重跑 39 條 baseline 確認 verdict／rank／查詢集無非預期變化。
  B. 驗證現有棄權機制：19 條 no-answer 題以 synthesize 執行，另配 ≥19 條可答題做 positive control；
     每題分類為 正確拒答／正確作答／有依據但答非所問／無依據作答／技術錯誤；記錄 judge 結果、
     有無觸發 trustedVaultLead bypass、實際 synthesis、採用的前五個 chunk。
     **批量呼叫外部模型前先報預計次數、token 同成本**（紀律 #17）。
  C. 驗證 forbidden source 實際影響：四條查詢以 synthesize 執行，分四類報告
     （只在原始結果／進入 synthesis window／答案實際採用／因對象混淆而答錯），
     只有第 3、4 類先可以叫「引用」或「答錯」。
  D. 排序反事實測試（**不改生產**）：現行 forced-footnote vs 結構化 exact-match 優先再合資格
     footnote 再原排序 vs 全域 score sort（僅作反例）。每種報 Source Recall、Chunk Recall、MRR、
     forbidden exposure，以及原有 footnote positive control 的損失。
     **不得只以 Recall@1 選方案；Chunk Recall@3/@5 同錯答風險優先。**
  E. 補 gold set：kg_admission、kg_operation、digital_education、info_security 各補至 ≥10 條
     （每類 ≥8 條可答），保持 dev/held-out 分離，新 label 須過 corpus／signature／source／page／NFKC 驗證。

✅ S213 查實（不必再查）：
  1. wiki_chunks **沒有 page 欄**；頁碼由 === Page N === 標記在查詢時推導
     （extractDominantPage，searchChannelB.ts:1054，已移植入 _s213_corpus.dominant_page）。
  2. chunk id = vault_<sid>_<hash>，hash 由 text 決定（build_wiki_index.text_hash 係 sha256[:16]；
     eval_retrieval 註釋寫 md5[:12]，該註釋係錯的）。故改 title 不動 id、不廢 embedding。
  3. 後端 cleanChunkText 回傳前剝走 === Page N === 同 === section ===，簽名含標記者永遠對不上。
  4. build_wiki_index.py:267-268 的靜默 fallback 係 658 條代號標題 + 無連結片段的單一根因；
     集合相等已證（19 = 19，交集 19，兩邊獨有各 0）。
  5. 語料含 868 條 CJK 相容表意文字 chunk（4.93%／112 源／110 個變體字）。
  6. header 剝除正則吃掉正文 `# ` 開頭行：16 個來源、33 行真正消失（非我先前推論的 55 行）。

🧭 紀律（S212 十八條仍然生效，S213 新增三條）：
  19. **報血緣範圍前先逐條實測，唔好由「符合模式」推論。**（S213：我報 23 源／55 行／3,714 條，
      實測係 16 源／33 行／2,212 條，而頭號例子根本冇受影響。）
  20. **量度工具本身要先驗。**（S213：find/show/signature 一律印 page=None，因為讀了不存在的欄；
      agent 已經在用。工具錯會靜靜污染全部標籤。）
  21. **關掉了某一層就不可以講該層的能力。**（S213：synthesize:false 之下講「系統沒有棄權能力」。）
```

---

## 2026-09-03 Session 212 — 由文檔漂移開始，變成建一張品質檢查頁；期間自己整停咗生產搜尋

- **ID:** Claude_20260903（S212）。由「開工」起，Leonard 中途下多兩張單（狀態頁、Codex 覆檢五點）。
- **Summary:** 開場只係修三個小漂移，最後交付咗一張公開品質檢查頁 + 封版閘 + 兩支新監察，並修好一個 91% 不可讀嘅來源。過程中我自己整停咗生產搜尋約半小時（額度耗盡），呢件事已變成兩道會擋人嘅閘。
- **Changed:**
  - 新：`dev/source/qc_report.py`（21 項檢查）、`dev/source/check_registry_drift.py`、`dev/source/release_gate.json`、`qc_report.json`、`status-07cc7942c0.html`、`.github/workflows/qc_report.yml`、`dev/source/registry_drift.md`
  - 改：`backend/src/api/searchChannelB.ts`（新 `info_security` 路由 + 更正兩處 kgecg_2017 註釋）、`dev/source/eval_retrieval.py`（片段層）、`dev/source/eval_queries.json`（37→39）、`dev/source/route_regression.mjs`（33→46 + KNOWN_GAPS）、`dev/ocr_extract.py`（空白頁拒絕語）、`dev/source/source_registry.json`（phys 重抽紀錄）、`dev/PROJECT_INDEX.md`、`dev/DOC_SYNC_CHECKLIST.md`（+2 行）、七個片段數鏡像、判斷閘 model 文檔七處
  - Supabase：`phys_sss_2007_2015` 182（165 不可讀）→ 0 →（額度中斷）→ **187 條、亂碼 0**；全庫 17,597 → 17,602
- **Done:**
  - **判斷閘 model 文檔漂移**：S211 拆出 `JUDGE_MODEL` 後，所有部署者實際會看的地方仍寫住判斷閘跟 `OPENAI_MODEL`；補七處，並在 `JUDGE_PROMPT_FINDINGS.md` 的「READ THIS FIRST」橫幅上加 supersede 標示（該橫幅教人「判斷閘 model 由外部無法得知」，S211 之後已不成立）。
  - **Playbook pointer v1 → v2**。skill 的安裝步驟寫「見到 marker 就跳過」，正正係經驗庫自己 `idempotent-install-blocks-upgrade` 卡講嘅布林式冪等，照跟就永遠升唔到級；改用三態判斷，marker 加 `v2`。
  - **OP⑤ 資訊保安路由** —— 交接寫「加保安／雲端字眼落 `digital_education` regex」。先量度，發現照做會令目標 query 變差：該路由帶 21 個 DEBP/AI 詞嘅 expansion，接上去會把 query 本身蓋過（`g28` rank 0 → 消失；`pcpd` rank 0 → 消失）。改為獨立 `info_security` 路由、**不設 expansion**。刻意唔認裸「資訊保安」（S209 已定案該闊 query 返 SAG 係啱嘅）。
  - **OP① eval harness 片段層** —— 交接建議「斷言 chunk id 入唔入到前五」。查實 chunk id 係 text 嘅 md5，每次重切全源改晒，呢條斷言喺 S211 前一日寫好就會喺佢保護嘅修正上面紅。改用**文字簽名**（先 squeeze 空白，因 PDF 文字層會喺詞中間斷行）。兩條 `staffing_row_probe` 現場證綠。
  - **OP② 登記漂移監察** —— 原本嘅「273 對 177、落差 96」把四個方向互相抵消。查 registry 之後再修正一次：13 個 `stat_enrolment_YYYY` **唔係未登記**，父項用 `url_primary_pattern` + `years_extracted` 描述整個年度系列，真缺陷係三個 registry 監察都唔展開年份。UNMANAGED 14 → 1。
  - **品質檢查頁 + 封版閘**（Leonard 中途下單，對照通告系統嗰張）。門檻用基準值不用零，**等於基準報 WARN 不報 PASS**；未有 waiver 嘅 WARN 一律 NOT_MET；人手項目冇日期簽核係 NOT_MET 唔係「不存在」；`NOT_MEASURED` 等於 NOT_MET。出廠 7/15 FAIL，如實。
  - **`phys_sss_2007_2015` 重抽入庫**：165/182 不可讀 → 187 條、亂碼 0、頁碼 1–150 全覆蓋。eval 39/39 SAME、0 blocking。
- **本 session 自己犯咗而值得記低嘅錯：**
  1. **整停咗生產搜尋。** 先刪 182 條，之後先發現 OpenAI 額度已被同一 session 嘅 150 頁 OCR 耗盡 —— 該源變 0 條，而且**全站搜尋 429**（查詢要即時算 embedding）。直接成因：我喺單頁探針寫過「cost: trivial」，跳去 150 頁時**冇重新估算、冇查餘額**；次序亦錯（應先驗入得到再刪）。
  2. **一個負面結果差啲當咗證據。** 測 `kgecg_2017` 有冇搶格位，頭五條 query 全部 `kgecg=0`，睇落無害；但嗰五條全部路由去 `curriculum`，而 `kgecg_2017` 喺 S195 已被移出該 SOURCE_SET —— 係硬過濾擋住佢，唔係佢贏唔到。關掉過濾重測先見到真相（最多 6/8 格）。
  3. **兩個自己寫嘅檢查第一次跑就錯數**：事實計數器行錯結構、把完好嘅凍結契約報成破損；標題基準用咗「我見過嗰一個來源」嘅數而非全庫真數（116 vs 實際 658）。
  4. **封版閘喺公開頁面寫「8 項」而下面只列 6 個名**（截斷冇省略號）。係 Leonard 睇頁面睇出嚟，唔係任何 self-test 捉到。
  5. **commit 訊息用反引號中咗 shell substitution**，兩行被吃掉 —— 記憶入面本來就有呢條。
  6. **差啲把「普適氣體定律」搵唔到算落 OCR 頭上**；實測「普適」對「普通」分數只差 0.019，真兇係 `safety` 認裸「氣體」。
- **QC:** `qc_report --self-test` / `check_registry_drift --self-test` / `eval_retrieval --self-test` 全綠；`route_regression` 46/46；`tsc --noEmit` + `npm run build` exit 0；檢索 eval 兩對 before→after（`info_security` 路由：2 SET_LOST 全部係刻意收窄、掉走嘅係錯科目雜訊；phys 重入庫：39/39 SAME、0 blocking）；入庫後逐項核實片段數／亂碼／頁碼覆蓋／url。
- **Evidence disposition:** 工具已 indexed in `dev/PROJECT_INDEX.md`；兩條規則 promoted to `dev/DOC_SYNC_CHECKLIST.md`（row 53 品質檢查改動、row 54 重抽既有來源）；路由缺口 recorded in `route_regression.mjs` KNOWN_GAPS；其餘逐條拆解 kept as recent trace evidence。
- **Sync:** DOC_SYNC row 51（切 chunk 邏輯）、row 53、row 54 命中。七個鏡像 17,597 → 17,602 已同步（`live_display_sync` 讀真數）。
- **Pending:** 見 Open Priorities。
- **Log maintenance:** **觸發並已執行。** 我第一次寫「無觸發」係錯 —— 套用咗 managed-core 嘅門檻（N≥11／1500 行），但本 project 自己嘅 §4a、`SESSION_LOG.md` 檔頭註釋、同 `docs/qa/session_log_maintenance.py` 三者一致用 **400 行**，當時 450 行。跑 `--self-test`（5/5）後 `--apply`：450 → 90 行、5 → 2 個 entry、3 條（S208–S210）移入 `dev/archive/SESSION_LOG_2026_Q3.md`（只移不刪）。工具再報 `latest entry prompt block ok=False`，因為本 entry 漏咗 `### Next Session Handoff Prompt (Verbatim)` 區塊（AGENTS §1 startup 要讀嗰個），已補；`--check` 現時 trigger=False。`PROJECT_DECISIONS.md` 觸發條件 (c) 已兌現（多選項架構取捨：算術還原 vs OCR、折入既有路由 vs 獨立路由），收工時 append。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; the full table lives in
 INDEX_TABLE.md - grep it on trigger, open a card only on a hit, then log one usage line.)

Current state (S212, 2026-09-03): 平台 v3.3.2; Supabase 17,602 chunks; source_registry 279;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
自動化 active: 6 源監察 + Option A 自動入庫管道 + 🆕 每日品質檢查 (qc_report.yml, 12:00 UTC, 會自行 push main)。
開工時本地大機會落後 origin/main —— tree 乾淨 + 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

🆕 開工第一件事改咗 (S212): 唔使再靠人手查全庫狀態，開呢一頁就見到全部
   https://policychecker.wongfu.net/status-07cc7942c0.html  (機器可讀: /qc_report.json)
   21 項檢查 + 封版閘。現時 overall=ERROR、閘 7/15 FAIL。
   本機重生: set -a && . backend/.env && set +a && python3 dev/source/qc_report.py --check

✅ S212 查實 (唔使再查):
  1. **重抽文字層救唔到 CID 亂碼。** phys_sss_2007_2015 嘅 PDF ToUnicode CMap 壞咗，pdftotext 抽出
     同舊 extract 逐字相同嘅亂碼。要用 dev/ocr_extract.py (S147 為此 failure mode 而建)。
  2. **亂碼算術還原係陷阱。** 三個固定偏移 (+0x3058 / +0x2D1E / +0x8E51) 可還原 98.4%、讀落通順,
     但交叉核對見到「二零一五年十一月」變成八個似是而非嘅漢字 —— 剩低嗰 1.6% 唔係明顯壞,
     係靜靜錯。用嚟做交叉核對可以, 唔可以當修法。
  3. **OCR 係草稿質素, 錯法係術語級誤字。** 逐頁對照原圖: 普適→普通、查證→查察、貫徹→實徵、
     樂意→樂於, 約每頁 1-2 個 (≈0.5%)。引用具體字眼前對回原文。
  4. **judge 同 synthesis 用兩個 model** (OPENAI_MODEL 合成 / JUDGE_MODEL 判斷閘, 後者程式預設
     gpt-4.1-mini)。S211 拆咗但七處文檔冇跟, S212 已補齊。
  5. **/health 報 ok:true 唔代表搜尋活。** 佢只驗 Channel A 快取。要驗真嘅睇
     qc_report 嘅 SEARCH_PIPELINE_LIVE, 或者直接打一條查詢。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先確認係邊個 model 變數。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」
     (S212 再中: 測 kgecg_2017 有冇搶格位, 頭五條 query 全部 0, 但嗰五條全部路由走咗,
      係硬過濾擋住, 唔係佢贏唔到。關掉過濾先見到真相。)
  3. 報一個數之前打開數字背後至少一個實例親眼睇。
     (S212: 數字密度偵測器返 701 條, 啱啱好落喺 S204 估算範圍, 但逐條讀係四樣唔同嘅嘢。)
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; synthesis-gate 改動一律 live before→after。
  6. judge 係 LLM、非決定性 → verdict 要重複 run (≥3); 更好係搵個確定性量度。
  7. 入庫 ≠ 可達; 可達 ≠ 贏得到; 贏得到 ≠ 答得啱。
  8. 交接寫低嘅選項框架本身可以係錯。(S212 三次: 「加保安字眼落 digital_education」會令目標
     query 變差; 「斷言 chunk id」會喺自己嘅修正上面紅; 「14 個 unmanaged 要分流」其實係
     一個 series 父項數咗 14 次。)
  9. 「應該冇」唔係「冇」。10. 報 population 數字要即刻拆類。
  11. **守門要證明佢會紅。** (S212 代價示範: /health 永遠唔會紅, 結果全站搜尋死咗半個鐘冇人知。)
  12. 交付一個檔案之前 ls 實證佢存在。 13. 揀嘅 phrasing 決定得出嘅答案。
  14. 任何要人做決定嘅表面都要有出口; 只入唔出嘅清單一定變牆紙。
  15. 改完一樣嘢, grep 該功能自己嘅字眼掃全站散文、meta、分享卡、README。
  16. 改 mobile.css / mobile.js 必須同時推 PLATFORM_VERSION。
  17. **S212 新增: 刪之前先驗「入得到」。** 先刪 182 條、後發現額度耗盡 = 該源 0 條 + 全站 429。
      任何會大量呼叫外部 API 嘅步驟 (OCR / 批次 embedding) 事前要估算並講出用量,
      唔可以把單頁探針嘅成本當成全份嘅成本。見 DOC_SYNC row 54。
  18. **S212 新增: 呈現層要有人眼睇。** 封版閘喺公開頁寫「8 項」而下面只列 6 個名 (截斷冇省略號),
      係 Leonard 睇頁面睇出嚟, 冇任何 self-test 捉到。self-test 驗邏輯, 唔驗呈現。

NEXT (見 Open Priorities 全文, 已重生為 8 項):
  ① 八個 standing WARN 要 Leonard 批 waiver 或當要修 + 六項人手檢查未簽核 (封版閘現時因此 FAIL)。
  ② kgecg_2017 108 條已證可刪, 但 cb3_deprecate_stale.py 被 auto mode 分類器擋住, 要 Leonard 跑。
  ③ ⚠️ eng_sss_guide_2021/g33 同 arts_kla_guide_2017/g37 唔係單純重複 —— 兩個 g-series 標題
     掛錯文件 (2007 英文指引、2002 藝術指引根本唔喺庫入面), 唔可以當刪重複處理。
  ④ TOPIC_KEYWORDS.safety 認裸「氣體」, 偷走氣體相關嘅課程查詢 (已入 KNOWN_GAPS)。
  ⑤ 特殊學校編制表恢復 —— 注意佢仍然喺 SOURCE_SETS.staffing 入面, 要先移走。
  ⑥ content_kind 框架要重新定義, 唔好再用分類器路線。
  ⑦ 658 條片段以內部代號做標題。 ⑧ 六個現有監察未接入狀態頁。

⚠️ 未做而應該知: coa_pri_e / coa_ss_e 亦載編制條款, 未逐一檢查有無同類「答錯班數」問題。
```

## 2026-09-01 Session 211 — 一條答唔到嘅查詢，拆出四層獨立缺陷

- **ID:** Claude_20260901（S211）。跨午夜：2026-08-31 20:58 → 2026-09-01 10:12（本機 BST）。
- **Summary:** 由「收起通告分析卡」開始，中途 Leonard 貼咗一條真實查詢「只修讀中學師資資格是否可以在小學任常額職位」同 Google AI Overview 對照。平台拒答。拆落去發現係四層獨立缺陷疊埋，而每一層「最順理成章」嘅修法都被實測否決。
- **Changed:** `app.html` / `index.html` / `q.html` / `t-purchase.html` / `mobile.js` / `mobile.css` / `README.md` / `K1_API_SPEC.md` / 三個 JSON 鏡像；`backend/src/api/searchChannelB.ts` / `backend/src/lib/wikiRepository.ts` / `backend/src/server.ts` / `backend/src/config/env.ts`；`dev/vault/expand_vault.py`；`dev/source/source_registry.json`；新增 `dev/source/route_regression.mjs` / `vault_lead_delta.mjs` / `cache_drift.mjs`；`dev/source/JUDGE_PROMPT_FINDINGS.md` §5–§7；`dev/DOC_SYNC_CHECKLIST.md` row「Tab withdraw / restore」重整。Supabase `staff_est_pri` 81 → 85（全庫 17,593 → 17,597）。
- **Done:**
  - 前端五項，平台 v3.3.0 → v3.3.2（收卡 / 平板版面錯位 / 統計列 / 三處寫死數字 / 五句散文）。
  - `/health` 加 `commit` + `started_at`。
  - 判斷閘改用獨立模型 `gpt-4.1-mini`（`JUDGE_MODEL`，程式預設）。
  - 檢索四層：`teacher_qualification` 路由、bypass 改讀 `results[forcedLeads]`、合成器字數由目標改上限、`chunk_overlap` 覆寫 ＋ `searchEstablishmentRows()` 詞彙層 overlay。
  - 內容準確性：編制答案預設只出全日制（Leonard 指出資助及官立小學已無半日制）。
  - 防漂移：`app.html` 分頁開關註釋第 8、9 項；DOC_SYNC row 重整。
- **QC:** `tsc --noEmit` / `npm run build` 全部 exit 0；`route_regression.mjs` 33/33 PASS，並以改前版本跑同一套作 baseline，證實無舊 query 改路由；`vault_lead_delta.mjs` 確定性證實 bypass 改動只影響 3 個 case 且全部 `want=能`、21 個 `want=否` 一個都無受影響；判斷閘換 model 對凍結集主集 31/33 打平、無新增 false answer、連 bare-noun 33/35 對 31/35；四個過度觸發 case 實測歸零；每次 push 後以 `/health` 嘅 `commit` 確認部署落地再驗真站。 **檢索 eval before→after 已跑**（DOC_SYNC row 43／51 要求）：對 `2026-08-26_s210_after_leaflet.json`，`2026-09-01_s211_after.json` 為 **PASS=25 / FAIL=0 / errors=0（與基線一致）、SAME 36 / 37、blocking failures 0**。唯一非 SAME 係 `sef` 一條 DISPLACED：尾位（第 8）嘅 `debp_blueprint` 被 `edbc015_2026` 擠走，而後者係 S210 之後 Option A 管道自動入庫嘅通函，**與本 session 四層改動無關**——正正係 S210 建立 DISPLACED 分類要吸收嘅情況。
- **本 session 自己犯咗而值得記低嘅錯：**
  1. **用 exact substring 搵原文，撞正 PDF 換行**（「新 入職教師」中間有換行），一度報「冇入 top-80」，實情係第 1 位。負面結果落結論前要問儀器顯唔顯示到。
  2. **分頁攞 81 行寫成 `limit=60`**，兩次請求其中一次回 error object，而我 `rows += b` 把 dict 嘅 key 當成 row 加咗入去，備份檔一度有 85 個元素。加咗 assert 逐項核 `isinstance(dict)` 同對權威 `count=exact` 先重做。
  3. **一度判斷「Render 部署失敗」並寫成報告請 Leonard 介入**，實情只係慢，而它喺報告寫到一半時上線。直接成因係服務無 version endpoint——已補。
  4. **兩次 full-pipeline run 分別喺 GN02 同 GN03 見到 false answer，一度當成回歸**，實情兩個 case 都唔喺改動影響範圍內，純 LLM 雜訊。改為寫確定性量度腳本先落結論。
  5. **「重新切片就係修法」講早咗一步**：做完發現答案變成由鄰近班數內插，隨即逐 byte 還原生產資料，確認詞彙層 overlay 之後先再重入。
  6. **`searchEstablishmentRows` 同 `staffing` 路由第一版都過度觸發**：「小一派位第 1 班點分」被塞八段編制表。實測到先收窄。
- **Evidence disposition:** 檢索／判斷閘嘅可重用結論已 promoted 入 `dev/source/JUDGE_PROMPT_FINDINGS.md` §5–§7（判斷提示唔係槓桿、凍結 cache 已漂移、班數查詢真兇）；三個量度工具已 indexed in `dev/PROJECT_INDEX.md`；架構取捨已 promoted to `dev/PROJECT_DECISIONS.md`；其餘逐條 compare 拆解同自己犯嘅錯 kept as recent trace evidence。
- **Sync:** DOC_SYNC row 37（vault source backfill）、row 43（eval harness）、row 51（切 chunk 邏輯）三行命中；「Tab withdraw / restore」一行重整為 A/B/C/D 四組並加入 grep 驗證步驟。公開片段數七個鏡像已同步 17,593 → 17,597。
- **Pending:** 見 Open Priorities。⚠️ `coa_pri_e` / `coa_ss_e` 亦載編制條款，未逐一檢查有無同類「答錯班數」問題。
- **Log maintenance:** 無觸發。本檔 4 個 session entry（N=4 < 11）、行數未逾 1500；`PROJECT_DECISIONS.md` 觸發條件 (c)（多選項架構取捨連理由）已兌現，本 session 已 append。
