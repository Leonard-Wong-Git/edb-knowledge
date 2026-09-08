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

## 2026-09-08 Session 218 — 起手探針五項全綠；HEAD 與 Render 報的 commit 不一致已查明屬正常，並非漂移

- **ID:** `Claude_20260908_0705` — S218
- **Summary:** 由「開工」起做起手探針，五項全部實測相符。唯一表面漂移（HEAD `0f8a7c9` vs Render `/health` 報 `612e13e`）逐檔核實為**零執行碼差異**，屬 S217 已記載的 `RENDER_GIT_COMMIT` 現象，非未部署。Option A watcher bot 本輪未推，不必 rebase。中段一次純資訊回覆（桌面 vs Claude mobile 的分別）。**零程式碼改動、零 QC 重跑、零 push。**
- **Changed:** 無程式碼改動。持久化：`dev/SESSION_HANDOFF.md`（`Current Baseline` 1–2／`Validation / QC` 新增 S218 段／`Risks / Blockers` 1／`Open Priorities` 整段重生＋治理兩項原文移入 `Backlog`／`Last Session Record` 重生為 S218，S217 降級原文保留／`Next Session Opening Message` 重生／`State Reconciliation Check` 新增 S218 段）· `dev/PROJECT_INDEX.md`（Branch / commit 列）· `dev/DOC_SYNC_REGISTRY.md`（S218 sync 段）· `dev/SESSION_LOG.md`（本條）· `START_NEXT_SESSION_PROMPT.txt`（由 fenced block 重生）。
- **Done:**
  1. **起手探針五項**：served `app.html` **3.3.2**（`curl policychecker.wongfu.net/app.html`）· Render `/health` **`ok:true`／`cache_a.warm` 455／`commit` `612e13e`／`started_at` 2026-09-08T06:58:08Z** · Supabase `wiki_chunks` **17,610**（service key `Prefer: count=exact`，讀 `Content-Range: 0-0/17610`）· `source_registry` **281** · `guidelines.json` `_meta` **2.6.1**。全部與交接相符。
  2. **表面漂移查明**：`git fetch` 後 `HEAD == origin/main == 0f8a7c9`、分歧 **0/0**、工作區乾淨。交接記的 `612e13e` 是 S217 收工前的 HEAD，之後 S217 自己再推兩個 commit（`72b5adb`、`0f8a7c9`）。**關鍵驗證**：`git diff --name-only 612e13e..HEAD -- backend app.html` = **0 個檔** → Render 雖報舊 commit，生產跑的執行碼與 `612e13e` 那次部署相同。**沒有查 Render 觸發設定，`RENDER_GIT_COMMIT` 不更新的成因仍未確證** —— 只證明了「不影響生產行為」，不等於「已解釋」。
  3. **bot 本輪未推**：`origin/main` 仍是 S217 收工那個 commit。S217 那次「遠端走前兩個」未重演，不必 rebase。**但 watcher 仍在，紀律不變**：開工一定要 `git fetch` 後比對，不得讀交接記載的 hash 當現況。
  4. **Playbook pointer 自我檢查**（該庫 `INDEX.md` 要求的 10 秒檢查）：本 project pointer 為 **v3**，最新，無須重裝、無須告知用戶。本節只讀 `INDEX.md`，**未 grep 全表、未開任何卡**，故按該庫規則**不寫 usage 行**（沒有查閱行為就沒有數據可留）。
  5. **一次純資訊回覆**：Leonard 問「在這裡開 session 然後在 Claude mobile 對話，跟桌面有何分別」。答案核心是「運算一直留在這部 Mac，手機是遙控器兼視窗」，並分「不變／會變」兩邊列出，重點是檔案連結在手機失效、要你親手做的事（Render dashboard、rebase、被分類器擋住的腳本）在手機做不到、以及 Mac 睡著 session 就停。**手機端 UI 細節（Run 掣、批准提示樣式）已明確標示為推斷、未實測**，沒有當事實講。
  7. **順手修好一個先前遺留的結構缺陷**：`dev/SESSION_LOG.md` 檔尾有一個懸空的 `ack:log-entry` 起始標記（後面無任何內容、無對應結束標記）。以 `git show HEAD:dev/SESSION_LOG.md` 核實**是本節之前已存在**（committed 版本即 5 start／4 end），非本節寫入造成，推測為 S217 `--apply` 歸檔後遺留。已刪去該行並確認後面零內容，現為 **5/5 平衡**（1 個 Entry Template ＋ 4 條 entry）。§4a `--check` 重跑仍 `trigger=False`（222 行／4 條）。
  6. **收工對齊 root**：Leonard 指出工作目錄跳回頂層 umbrella scaffold（該處 `START_NEXT_SESSION_PROMPT.txt` 有 ⛔ 明示不可在該 root 做事）。已切回 `Draft/` 才開始收工寫入。
  8. **交接檔標記兩項核對**（因上一項而順帶做）：(a) 我最初把 S218 的三個 reconciliation field 標記寫成 `-s218` 後綴的新名，**寫完自行核對發現與現行慣例不符** —— `git show HEAD:` 實測 committed 版本每個名字已各有 2 份（S217 一份、S216 一份，最新在前，`indexOf` 式讀取自然取最新），故已改回正名、疊在最前，全檔 32 → 35 個標記行，無新名字。(b) **發現一個既有但目前無害的碰撞**：`## Backlog` 治理側段的散文寫出了 `ack:section:` 加 `session-history` 的完整名字，位置在該真標記之前，`indexOf` 式讀取會先中散文那個。**本節刻意不改** —— 該段是我承諾「原文一字不刪移入」的文字，改了就破壞該承諾；且 S216 已查明 gate 只讀 `completed-this-session`／`validation-qc`／`next-priorities`／`risks-blockers` 四節加開場白，`session-history` 不在其中，故目前**無實際影響**。留給下節連同治理側其餘項目一併處理。

- **QC:** **本節零 QC 重跑。** S217 推之前實測的數值仍有效，因為綁定的 commit 與檔案本節一字未改：`npm run check` 0 · `npm run build` 0 · `regression:grounded` 48/48 · `route_regression` 46/46 · active gold 185。**未跑：185 題 live 套件**（啟用 flag 的唯一閘）。**未驗證：`agent-handoff-kit doctor`** —— CLI 仍不在 PATH、全局與本地 `node_modules` 皆無、npm 上該名字 404，狀況同 S217；**列為未驗證，不當通過**。`qc_report.json` overall **ERROR** 未處理，狀態同 S215–S217。§4a `--check` 實測 `trigger=False`（199 行／3 條 entry，未達 400 行或 30 日門檻）。
- **Evidence disposition:** 探針逐項數值、`git diff --name-only` 的零檔驗證、mobile 問答內容 → 留在本條 log 作 trace 證據；當前 HEAD／部署 commit 的正確解讀、bot 本輪未推、OP 重排 → 入 `dev/SESSION_HANDOFF.md`。「Render `/health` 報的 commit 可以合法地舊過 HEAD，判斷要看 `git diff --name-only` 而非比 hash」屬跨 session 可重用的判讀規則，已寫入開場白 ⚠️ 防誤判段。未升 `dev/PROJECT_DECISIONS.md` —— 本節無架構取捨。
- **Sync:** `dev/CODEBASE_CONTEXT.md` **不需更新**（技術棧、目錄、build 指令、External Services、Key Decisions 本節皆未變）。`dev/PROJECT_INDEX.md` Branch / commit 列**已更新**。`dev/DOC_SYNC_REGISTRY.md` 已記 S218 七行狀態。**DOC_SYNC Matrix Scan — SKIP（本節 CHANGE 階段零檔案改動；所有寫入均為收工持久化本身）。**
- **Pending:** 185 題 live 套件未跑（OP ①，啟用 flag 的唯一閘）· `backend/README.md` 5 行未補（OP ②）· 三題 chunk recall（OP ③）· 4 條 fidelity ＋ 合成窗（OP ④）· S212／S213 全部遺留（OP ⑤）· 治理兩項（`ack` marker 專屬章節、`INIT.md` 鏡像 blocked，已移入 Backlog 治理側段）· `qc_report.json` overall ERROR · `agent-handoff-kit doctor` 連續兩節未能執行。
- **Risks:** ① S214 候選碼在生產且 establishment 路徑**無 flag 保護、已生效**，184 條未量 —— 已部署 ≠ 已驗證（未變）。② Option A watcher bot 仍會自行推送，本輪未推不代表下輪不推。③ `AGENTS.md`／`CLAUDE.md`／`GEMINI.md` gitignored 且從未 tracked，S216 升級改動不在版本控制內。④ **新增觀察**：`agent-handoff-kit` CLI 連續兩節取不到，治理健康度已連續兩節無機器驗證 —— 目前只靠人手核 marker，屬逐節累積的驗證缺口。
- **Log maintenance:** **無觸發。** 收工前跑 `python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → `trigger=False line_trigger=False date_trigger=False`（`line_count=199`、`entry_count=3`，門檻為 400 行或最舊條目逾 30 日）。S217 剛做完歸檔，故本節按規則寫一行 no-op 理由，不執行長期維護。
- **規則衝突（依 §5 記錄）：** 沿用 S216／S217 的取捨 —— 專案 INSTRUCTIONS 層 §4 規則 12–14 要求把開場白逐字寫入本 log，Kit managed core 則寫明開場白全文不屬於本 log。跟 Kit 契約：全文只存 `dev/SESSION_HANDOFF.md` 與 `START_NEXT_SESSION_PROMPT.txt` 兩處，本 log 只記 mirror 已驗證。
- **收工後補正（自我發現）：** push 完成後 HEAD 由 `0f8a7c9` 變成收工 commit `f3ca973`，令剛寫好的交接檔與開場白即時落後一格 —— 這是「收工 commit 改變自己所描述的狀態」的必然遞歸，S217 也中過（記 `612e13e` 而實際留下 `0f8a7c9`）。**修法不是再追一次 hash，而是改成不靠 hash 的判斷準則**：交接檔與開場白現已明寫「每次收工都會多一個治理 commit，HEAD 必然前進；判斷線上是否落後要看 `git diff --name-only <部署commit>..HEAD -- backend app.html` 是否為 0，不要比 hash」。mirror 隨之重生為 77 行並驗證逐位元組相等。該補正為 commit `b0a8b0f`（已 push）。
- **Playbook（§14 留底）：** **本節不交提案。** 只做了 pointer 版本自我檢查（v3，最新）。沒有 grep 全表、沒有開卡，故按該庫規則**不寫 usage 行**。本節唯一可能可轉移的教訓（「`/health` 報的 commit 可以合法地舊過 HEAD」）**判為未夠成熟**：只有 S217、S218 兩次觀察且成因未確證，交上去會是一條無根據的卡；待成因查明再考慮。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成，讀回逐位元組相等；全文按契約不複製入本 log。
<!-- ack:log-entry:end -->

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
- **Log maintenance:** **觸發並已執行。** 收工前跑 `python3 docs/qa/session_log_maintenance.py --check` → `trigger=True line_trigger=True`（494 行 > 400 門檻；`date_trigger=False`）。先跑 `--self-test` **5/5 passed** 確認工具本身健康，備份現檔後跑 `--apply`：**494 → 197 行、8 → 3 條 entry、歸檔 5 條**入 `dev/archive/SESSION_LOG_2026_Q3.md`（1,717 行）。**無損已驗證**：8 條 entry 標題全部可在 log 或 archive 尋回，S211／S212 各抽 1,500 字元逐字比對相符。archive pointer 已在檔頭。**註：門檻用 400 行（本 project `docs/qa/` 工具與 §4a 的定義），非 managed core 寫的 1500 行 —— §4a 規則 3 明訂「script command 是執行閘」，故以工具為準。**
- **規則衝突（依 §5 記錄）：** 專案 INSTRUCTIONS 層 §4 規則 12–14 要求把 `Next Session Handoff Prompt` 逐字寫入本 log；Kit managed core 則寫明「The full opening message never belongs in this log」。維護工具亦報 `latest entry prompt block ok=False`。**沿用 S216 的取捨：跟 Kit 契約，全文只存於 `dev/SESSION_HANDOFF.md` 與 `START_NEXT_SESSION_PROMPT.txt` 兩處，本 log 只記 mirror 已驗證。** 理由：單一出處比三處各存一份更可驗證，且避免 S216 踩過的「兩個 live 檔同時被覆寫」風險。
- **Playbook（§14 留底）：** 已交提案 `inbox/2026-09-07-policychecker-flag-gated-not-behavior-neutral.md`（pattern，battle-tested）—— 內容為本節第 8 點那條教訓，寫成方法 A／B／C 對照，C 為四步可照做的驗證程序。交之前依規矩先 grep 全表兩輪，開過 `zero-regression-default-path` 確認方向不同（該卡是設計側、本提案是驗證側），已在提案註明並建議互相引用；`usage/policychecker.log.md` append 一行 `lookup`。**零接觸 trunk**（`patterns/`／`conventions/`／`INDEX.md`／`INDEX_TABLE.md` 一字未改）。順帶清走該庫一個上一 session 遺下未 push 的提案 commit `68683d8`，三個 commit 一併推上（`b0f69ec..8508a94`）。`PROJECT_DECISIONS.md` 觸發條件 (b) 不成立（交接檔無 ≥30 條 decisions-like 章節）、(c) 不成立（push 決定屬既有 OP ① 的執行，非新架構取捨）。10-closeout backstop 沿用 S216 的保守判定，未到。
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
- **Pending:** 交接檔 8 個 marker 未有專屬章節（OP ⑥）· `INIT.md` 鏡像 blocked（OP ⑦）· 根目錄 v0.3.24 舊 Kit 未處理 · S212–S215 全部產品側遺留一項未動。
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
