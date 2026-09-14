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

## 2026-09-14 Session 224 — 把那道閘設成必過的正常做法，會反過來擋死整個 repo；而封版閘紅了一日，紅的是一件沒有發生過的事

- **ID:** `Claude_20260914_1313` — S224
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft，起手探針 6/6 綠、零漂移。Leonard 由 branch 選單見到兩條舊 `claude/*` 分支起問，一路推進到把 S223 交下來的 OP① 完整做完。**零 Supabase 寫入、零 `backend/src` 邏輯改動、零 flag 改動。**
- **Changed:** `.github/workflows/backend_build_check.yml`（拆 `paths:`，改為 job 內 scope）· `dev/source/execute_ingest.py`（步驟 6 改行 PR，self-test 13 → 28）· 四條 ledger workflow 加 `ssh-key` · `dev/source/qc_report.py`（凍結契約基準值 ＋ 兩條新紅案）· `dev/DOC_SYNC_CHECKLIST.md`（新 row）· `dev/PROJECT_INDEX.md` · `dev/CODEBASE_CONTEXT.md` · `qc_report.json`。commits `3affb71` → `eb585a0` → `abe1fad` → `fe3b6ba`(bot) → `4e46a7a`(PR #10) → `3359f94`(PR #11)。ops repo `5e27d2d`。
- **Done:**
  1. **OP① 完成，但原要求那一步本身是錯的。** 交接寫「去 GitHub 設 branch protection，五分鐘」。照做會撞兩堵牆：(a) `backend_build_check.yml` 有 `paths:` 過濾，而 required status check 要求該 commit 報 success／skipped／neutral —— **被過濾掉的 commit 甚麼都不報，那次 push 會永遠 pending**；(b) required check 擋的是**所有**直接 push（官方原文：`Required status checks must have a successful, skipped, or neutral status before collaborators can make changes to a protected branch`），而 `main` 有**五條**直接 push 路徑，不是交接寫的一條。
  2. **閘改為每次觸發、範圍在 job 內判斷。** 判不到就傾向照跑；scope 略過的 run **不會關閂** breakage issue（它甚麼都沒編譯，證明不了 main 編得過）。補 `route_regression.mjs` 入 watched 清單。兩半都在生產實測：`3affb71` → `BUILD — 2 watched path(s)` 九步全綠；`eb585a0`（純文件）→ `SKIP`，**5 秒** success。
  3. **Option A 步驟 6 改行 PR。** 推 `ingest/<source_id>` → 開 PR → auto-merge → 有上限輪詢。新增用 `ast` 讀自己的結構斷言，確認步驟 6 內再無 `HEAD:main`。
  4. **四條 ledger workflow 搬去 write deploy key**，因為兩條正路都不通（見 Fix Record）。`actions/checkout` 的 `ssh-key` 輸入先查證存在才用。
  5. **ruleset `main build gate` 落地**（id 23311105，bypass 只有 `DeployKey`，**沒有 admin**）。
  6. **修好 `FREEZE_CONTRACT` 假 BLOCKER**：BLOCKER 1 → 0，PASS 12 → 13，其餘計數不動。
- **Fix Record（三個假設被實證推翻，兩個是我自己的）：**
  - **「bypass GitHub Actions」在個人帳戶 repo 行不通。** GitHub 422：`Actor GitHub Actions integration must be part of the ruleset source or owner organization`。UI picker 沒有這一項不是找漏，是真的沒有。
  - **「把四條 ledger 改成開 PR」也不通。** 官方文件：由 `GITHUB_TOKEN` 開的 PR，其 run `require approval`，auto-merge 會卡死。deploy key 是排除法剩下那條，不是首選。
  - **`FREEZE_CONTRACT` 紅了一日，紅的是一件沒有發生過的事。** S223 依 Leonard 拍板把 guidelines 改為 2.6.2／151（公開端點實測早已服務該值），但 `qc_report.py` 的基準值仍寫 2.6.1／158。**根因不是疏忽：`DOC_SYNC_CHECKLIST.md` 根本沒有一條 row 指向那四個值。** 已補 row。同時補測試真空 —— 原有四條紅案**全部只變動事實數，guidelines 半邊零覆蓋**，而 S223 動的正是那半邊。
  - **我的指令害了 Leonard 兩次**：給他的收工 recipe 在「沒有未推 commit」時會失敗並留下空分支，中過兩次；第一版 ruleset 指令用了全形破折號，終端機 paste 時游標跳位令 JSON 壞掉。之後 git 操作由 AI 自己做，指令一律單行純 ASCII。
  - **攔截了一個假綠**：`git diff main <branch>` 報 `ambiguous argument`（repo root 有個 tracked 的 0-byte 檔案 `main`，2026-05-01 commit `8b03e1a` 誤入），輸出那個 `0` 來自指令失敗而非比對結果。改用 `--` 並以「分支 tip vs 它的 squash commit 樹比對」才刪分支。**退出碼非零時輸出的任何數字都不是量度結果。**
  - **本檔結構修復**：S223 與 S222 兩條條目原本被困在 Entry Template 的 ````markdown fence 內（fence 由第 20 行開到第 95 行），渲染成程式碼而非日誌條目。本節把兩條提出 fence 外、次序不變，fence 只留佔位模板。**零內容改動。**
- **QC:** `npm run check` 0 · `npm run build` 0 · `route_regression` **46/46** ＋成員斷言 · `execute_ingest --self-test` **28/28** · `qc_report --self-test` ALL PASS · `check_registry_drift`／`check_monitor_health --self-test` ALL PASS · 九個 workflow YAML 全部解析 · **紅測三次**（注入直接推 main → 27/28；回捲凍結基準值 → `intact freeze contract passes` 轉紅；移走 guidelines 比較 → 新加兩條準確轉紅且其餘不受影響）· **ruleset 實測擋得住**（推空 commit 被拒，兩條規則同時出聲）· **deploy key 實測推得到**（`abe1fad..fe3b6ba HEAD -> main`）· **PR 流程兩次**（#10、#11 皆 `BLOCKED → CLEAN → MERGED`）· 收工探針 v3.3.8 ／ 17,004 ／ ZOMBIE 0 ／ 線上 backend 碼 == HEAD。
- **Evidence disposition:** 全部為即時指令輸出與 GitHub API 讀數，已逐項寫入本條與交接 `## Validation / QC` S224 段；**無新增 eval run 檔**（本節零檢索改動）。ruleset 設定以 `gh api repos/:owner/:repo/rulesets/23311105` 可隨時重讀，故不另存快照。
- **Sync:** `PROJECT_INDEX.md`（閘那一 row 改寫，含「不得加回 `paths:`」禁令）· `CODEBASE_CONTEXT.md`（步驟 6 新形態 ＋ secrets 契約 ＋ AI Maintenance Log 兩條）· `DOC_SYNC_CHECKLIST.md`（**新增凍結契約 row**）· ops repo `executor.yml` 註釋（更正 `MAIN_REPO_PAT` 權限記載）· `qc_report.json` 重生並 commit。
- **Pending:** 185 題 gold 未重跑（OP①）· `finance` 路由缺口（OP②）· 封版閘仍非綠，四類（OP③）· **入庫 PR 路徑未經一次真實入庫驗證**（當日 approval queue 空）· 看門狗與 pgvector 監察仍未經真實排程觸發。
- **Risks:** ⚠️ 四條 ledger workflow 經 `DeployKey` 永久繞過該閘 —— 現時只寫 JSON、不碰 `backend/`，但那是「現時的碼」而非機制保證。⚠️ 新增一把沒有到期日的長期憑證 `LEDGER_DEPLOY_KEY`，等同可直接寫 `main` 的萬能匙。⚠️ 三項外部設定改動不在 git 內（auto-merge／delete-branch 兩個 toggle、deploy key `id=163258294`、repo secret），換機或重裝要記得。
- **Log maintenance:** **triggered（寫入後）＋ 記錄一個規則衝突。** 寫本條之前 `--check` 為 `trigger=False`（370 行 / 9 entries）；**本條寫入後升至 402 行，越過 §4a 的 400 行門檻**，`--check` 轉 `trigger=True line_trigger=True`。依 §4a「腳本是執行閘、不得靠判斷」執行 `--apply`：**402 → 187 行、10 → 5 條、5 條（S219–S215）移入 `dev/archive/SESSION_LOG_2026_Q3.md`**。逐條對帳 10/10 剛好一份，零重複零遺失；工具 `--self-test` 5/5。
  **⚠️ 規則衝突（依 AGENTS.md §5 記錄）：** 本專案 §4a 寫「>400 行即觸發、存 `dev/archive/`」，而 Kit closeout pack 寫「≥11 條或 >1500 行才觸發、存 `dev/SESSION_LOG_archive/`」—— 兩者門檻與目的地都不同。**取 §4a**：它有機械閘腳本、`dev/archive/` 已有 Q1／Q2／Q3 三個既有檔（即本專案既有慣例），且歸檔是移動非刪除，較可驗證。
  **⚠️ 同一衝突的第二面：** `--apply` 回報 `latest entry prompt block ok=False`，因為它按 §4 第 12 條期望本條含 `### Next Session Handoff Prompt (Verbatim)` 全文；而 **Kit closeout pack 明文禁止**把開場白全文複製到本檔（單一真源）。**取 Kit**：本專案在 S192–S193 正正因為 handoff 與 START 各寫一份而出現過 drift，三份副本只會重演。故該 `ok=False` 是**刻意的已知分歧，不是失敗**；exit code 為 0，非 §4a 第 4 條的停止條件。
- **Playbook（§14 留底）:** 見該庫 `usage/policychecker.log.md` 本日兩行。
- **Opening-message mirror:** **regenerated and verified** —— 由交接 `Next Session Opening Message` 唯一那個 fenced block 重生，五個錨點全部通過（marker 唯一、text fence 唯一、log 內無全文副本、正規化相等、byte-for-byte 相等；4,924 bytes / 62 行）。全文依 Kit 契約不複製到本檔。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-14 Session 223 — 部署已經死了十六小時而沒有任何徵狀；那個「刪了會失去 15%」的數字，是排版量出來的

- **ID:** `Claude_20260914_0650` — S223
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。起手探針按交接紀律「比檔不比 hash」，揪出 `main` 不編譯、Render 部署凍結 16 小時。Leonard 一句「全做」後連做三項；中途兩次以 `AskUserQuestion` 取得拍板（`g24` 去留、`guidelines.json` 是否 bump；`kgecg_2017` 是否清走）。**本節 AI 直接執行三次生產寫入**，推翻交接「分類器會擋住」的記載。
- **Changed:** 平台 **v3.3.5 → v3.3.8**（三次 bump）。新檔 `.github/workflows/backend_build_check.yml`、`dev/source/eval_runs/2026-09-14_s223_kgecg_g29_overlap.json`。改 `backend/src/api/searchChannelB.ts`（兩行位置）、`dev/source/execute_ingest.py`（locator 重寫 ＋ `--self-test`）、`backend/src/lib/wikiRepository.ts`（註釋）、`dev/_s213_run_gold.py`（註釋）、`dev/vault/sag_2025_11/extract_sag_2025_11_repaged.txt`（重抽）、`source_registry.json`、`guidelines.json`、`knowledge.json`／兩個 `role_facts.json`、`app.html`、`index.html`、`README.md`、`K1_API_SPEC.md`、`CHANGELOG.md`。commits `2dee4fb` → `7ab96bb` → `aeca54c` → `8deea11` → `e9d14be` → `abeba8a`（全部已 push）。
- **Done:**
  1. **部署管道解封。** `main` 由 2026-09-13 15:30 UTC 起不編譯（`e2b53f0`／`183b7a8`／`9e5f28c` 三個 watcher ingest commit），Render 建置失敗後繼續服務 `5765c43`，`/health` 照報 `ok:true`。**症狀不是停機，是部署凍結** —— 前端在 Pages 上完全正常，沒有用戶可見徵狀，所以 S222 收工時看不出來。
  2. **根因封死。** `plan_route_patch` 只掃 `start+60` 行找**含**「]」的行，找不到就把 `end` 留在 `start` —— `curriculum` 長到 61 行剛好越界。**修復工具交出一份看似正常的計劃，指向 route key 自己**，與 S222 那個 title backfill 同一家族。現在閉合括號必須整行只有括號且在 key 的縮排層級，無行數預算，找不到即報錯；executor 加結構不變式。`--self-test` 13 條，**紅測 6/13 FAILED**（含一條會即時掃真實檔案的斷言）。
  3. **新增 `Backend Build Gate`**（首跑通過）。此前八個 workflow **無一個跑 typecheck**，所以機械人可以把不編譯的 main 推上去而無人出聲。老實記住它偵測不阻擋。
  4. **OP①：《學校行政手冊》換 2026年8月版並合併 `g24`。** 上游 2026-09-07 原地換版，275 頁（舊 270）。用專案自己的 `repage_pdfs.py` 重抽 → **387 條**全部 page-resolvable。**連結由 landing page 改為 PDF** —— `g24` 本來才是指向 PDF 那個，沿用 landing 會**失去**跳頁而非保留甚麼。792 → 387。`guidelines.json` 以 `app.html` registry 為真源逐條對齊：移除 7 條、同步 32 個欄位，158 → **151**，bump **2.6.2**。
  5. **OP②：清走 `kgecg_2017` 108 條**，`g29` 107 條承接。**唯一的 ZOMBIE 由 1 歸 0。**
  6. **順手掃下游**：公開片段數多報 116 條（S222 清片段後沒跑 display-sync，用戶由 09-13 起一直見到 17,633）· README badge 停在 v3.3.3（S222 連 bump 兩次都沒掃到）。
- **Fix Record（推翻一個交接結論，並自我更正一次）：**
  - **「`kgecg_2017` 刪了會失去約 15% 內容」—— 假數。** S222 比較的是**兩批 live chunk**，出自不同管道（`g29` page-carried、`kgecg_2017` 無 page marker）與不同切割邊界，**量到的是管道不是文件**。同一抽取器＋對照組（自己對自己 0 miss）重量：兩份都 108 頁、`U+FFFD` 都 0、字元差 0.9%；落差**對稱**（11.7%／11.3%）；383 個落差視窗拆半後 88.5% 有一半在對方文件內、3.7% 兩半都在，**真正獨有 0.91%**，而那 30 條全是目錄與章節簡介的接合文字。**判別法**：落差對稱＝次序噪音。
  - **自我更正：曾在生產寫入之前就把預期的 17,112 寫入 README 與 `K1_API_SPEC.md`。** 這正是 S209 禁止的「靠加減推算」。已即時還原，等寫入落地後由 `live_total_count()` 讀真數再同步。
  - **`ingest_one_source.py` 在 792 條已經刪走之後才因缺 `openai` 失敗**，那一刻《學校行政手冊》在庫內是 0 條。成因是預設 `python3`（homebrew 3.14）沒有 `fitz` 亦沒有 `openai`。已入交接 Risks 6 與 `User Environment`。
- **QC:** `npm run check` 0 · `npm run build` 0 · `route_regression` **46/46** ＋成員斷言 · 五個 JSON 全部解析 · `execute_ingest --self-test` 13/13（紅測 6/13 FAILED 如預期）· `check_registry_drift --self-test` ALL PASS · `check_monitor_health --self-test` ALL PASS · 九個 workflow YAML 全部解析 · **生產寫入逐項對數**（409→0→387 / 383→0 / 108→0 / g29 107 未動 / 全庫 17,517→17,112→17,004）· **生產端到端五條查詢**（命中新版獨有的 8.4.4 國家安全章節 p.253；`g24`／`kgecg_2017` 零出現）· **瀏覽器實測三輪**（最終 v3.3.8 / 170 條 / 17,004 / 零過期數字 / 零 console error）。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-14_s223_kgecg_g29_overlap.json`（方法、對照組、視窗拆半分解）· `dev/init_backup/20260914_081342_UTC/`（SAG＋g24 刪除前計數）· `dev/init_backup/20260914_082948_UTC/`（kgecg 刪除前計數）。
- **Sync:** `CHANGELOG.md` 三條（v3.3.6／v3.3.7／v3.3.8）· `README.md` badge ＋ 四處數字 · `K1_API_SPEC.md` 四處 · `PROJECT_INDEX.md` 新檔與自測 · `DOC_SYNC_REGISTRY.md` 本節 row。
- **Pending:** branch protection（只有 Leonard 做得到）· 185 題 gold 未重跑，且 SAG 換版**沒有做 eval before→after**（舊語料已被覆寫，before 取不到）· `finance` 路由拿不到手冊 · `qc_report.json` overall ERROR · 36 個 PHANTOM · `stat_integrated` id 錯配。
- **Risks:** ⚠️ watcher bot 可以推出不編譯的 main，而新閘偵測不阻擋。⚠️ **「生產寫入會被分類器擋住」已證實過時** —— 安全邊界由機械閘變成「要先取得明示批准」這條紀律，兩者強度不同。⚠️ 預設 `python3` 缺依賴。
- **Log maintenance:** **no-op。** 本檔 8 條 → 加本條 9 條；未達 N≥11 或 1500 行任一硬觸發。10 次 backstop：S217 做過全面維護，其後 S218–S223 共 6 次，未到。
- **Playbook（§14 留底）:** 見本節 usage 行。
- **Opening-message mirror:** 見交接檔 `Next Session Opening Message`；本 log 依 Kit 契約不複製全文，只記驗證結果。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-13/14 Session 222 — 標籤講錯它服務的內容，是一個家族；監察偵測到了卻沒有人接，是另一個

- **ID:** `Claude_20260913_1330` — S222
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。Leonard 反覆「全做」推進：先答 Supabase 升級問題（核實後**取消**了 S221 交下來的那個決定），再由 `qc_report.json` 四個 ERROR 追出兩條主線 —— 瀏覽清單標籤錯配家族、監察排程的靜默死亡。兩個生產寫入由 Leonard 在終端機執行（分類器擋住 AI 的寫入路徑）。
- **Changed:** 平台 **v3.3.3 → v3.3.5**。新檔 `dev/source/registry_series.py`、`check_pgvector_release.py`＋`pgvector_seen.json`、`check_monitor_health.py`、`.github/workflows/pgvector_check.yml`＋`monitor_watchdog.yml`。改 `app.html`、`README.md`、`CHANGELOG.md`、`source_registry.json`、`_s213_title_backfill.py`、`cb3_deprecate_stale.py`、四個 `check_*.py`、`DOC_SYNC_CHECKLIST.md`、`PROJECT_INDEX.md`。commits `06daf7f` → `4623fbb` → `2ffba87` → `87c9c01` → `c8a2de3` → `fa13901`（全部已 push）。
- **Done:**
  1. **推翻了 S221 交下來的 OP①。** Supabase 的建置最高只打包到 pgvector **0.8.2**（`nix/ext/versions.json`，PR #2158，2026-05-22 之後三個多月無動靜），而封鎖 HNSW 的是 0.8.3／0.8.4。**升到頂都仍然封住** —— 那個決定無板可拍，改為機器監察。順帶分清兩個「最高版本」：0.8.0 是實例提供的（滯後），0.8.2 是建置打包的（領先）。
  2. **`_s213_title_backfill.py` 的 planner 由「讀成因」改為「讀損害」。** 它靠「找缺 header 的抽取檔」砌計劃；S213 補好 header 之後它就找到 0 個 —— **修復工具在損害仍然存在時靜靜解除了自己的武裝**。Leonard 執行後：代號標題 **658 → 0**、無連結 **265 → 109**（剩餘全是 role_facts_* Channel A 鏡像，依設計無連結）。
  3. **標籤錯配是一個家族，不是 g37 一個。** 176 條瀏覽條目逐條對照片段實際攜帶的標題／連結，26 條對不上；扣除良性的（瀏覽連 landing page、片段連深層 PDF，屬設計）後按同一裁示處理：六條標籤改正（`g36` 與 g37 完全同形、`g33`、`g22`、`nat_sec_edu`、兩個 hub），五條零片段重複條目移除。瀏覽庫 **177 → 171**。
  4. **清走 `arts_kla_guide_2017` 116 條**（Leonard 執行）。實測 115/116 條片段文本與 `g37` 逐條相同、內容 99.9% 重疊。全庫 17,633 → **17,517**，`g37` 116 條未受影響。
  5. **528 條片段脫離監察黑洞。** `registry_series.py` 令四個監察展開年度系列；`check_freshness` 檢查量 271 → 284。連帶修好 `SERIES_UNMONITORED` 這一類「無條件報 ERROR」的設計 —— 缺陷修好之後它本來會永遠亮紅。
  6. **監察排程的三個靜默死亡模式**（官方文件核實）：GitHub 不補跑錯過或失敗的排程、`schedule` 高負載會延遲或跳過、**PUBLIC repo 60 日無活動排程自動停用**。新增每日看門狗：由 Actions run 歷史判斷「最後一次成功」，過週期自動補跑，靜兩個週期才出聲。零改動現有七個 workflow。
- **Fix Record（自我推翻三次）：**
  - **「SAG 有人改了登記卻忘記入庫」** —— 錯。CHANGELOG 加實測證實：上一節評估過 2026年5月版唯一實質改動，用一條 footnote 精準覆蓋而不重入整本，是合理決定。**已完整撤回據此所作的改動。** 真正的漂移是下一版（2026年8月版）。
  - **「41 個可瀏覽指引搜尋不到 = 23% 缺口」** —— 作廢。至少 4 個根本不是缺口，內容早已入庫，只是掛在另一個 id 之下。
  - **「跨抽取器量得 20.8% delta」** —— 假數。舊 extract 出自 PyMuPDF、我用 pdftotext，閱讀次序差異造成大量假差異。改用同一抽取器並設對照組（舊對舊 0 miss）後為 11.9%／12.9%。
  - **看門狗第一次跑就揪出自己一個 bug**：`_token()` 有 guard 但漏了 `return`，送出 `Bearer None` 全部 401，而當時設計會把「讀唔到」摺成「從未成功」→ **假全紅**，同假全綠是同一缺陷的兩面。已加第三種狀態並補斷言。
- **QC:** 六個監察自測全 `ALL PASS`（含 `check_expiry` 18 條、`check_pgvector_release` 24 條、`check_monitor_health` 11 條 prove-assertions）· `_s213_title_backfill --self-test` 15/15 · 七個 workflow YAML 全部解析通過 · **瀏覽器實測** `app.html`：171 條、零重複 id、tab 顯示「📚 EDB指引 (171)」、零 console error · 18 條要寫入的 URL 逐條 HTTP 200 · 刪除後逐項對數（116→0、g37 未動、全庫 −116、代號標題 0）。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-13_s222_duplicate_rows_predelete.json`（刪除前完整 row dump）· `2026-09-13_s222_sag_edition_delta.json`（版次 delta，含對照組數字與 400 條新版獨有片段樣本）· `dev/init_backup/20260914_063210_UTC/`（cb3 工具自己寫的刪除前計數）。
- **Sync:** `DOC_SYNC_CHECKLIST.md` 加三行（上游原地換版、標籤與內容不一致、新增排程監察要同步 cadence 表）· `PROJECT_INDEX.md` 加三個新檔與三條自測 · `CHANGELOG.md` 兩條（v3.3.4／v3.3.5）· `README.md` 指引數 177 → 171 · `guidelines.json` **刻意未動**（凍結合約，見交接 Risks）。
- **Pending:** SAG 重新入庫（Leonard 指示下一輪做）· `kgecg_2017` 由哪一版重新入庫（下一輪）· `qc_report.json` overall ERROR · 36 個 PHANTOM · registry 281 vs 服務 300。
- **Risks:** ⚠️ 看門狗跑在同一套排程機器上，救不到「七個一齊死」；買到的是互相監察，偵測窗由一星期收窄到一日 —— 這句寫死在它每次出聲的輸出裡。⚠️ `.claude/settings.local.json` 已加 Bash 權限規則（Leonard 執行），dry-run 通過但 `--execute` 仍被分類器擋 —— 刪資料那一類清不到，屬預期。
- **Log maintenance:** **no-op。** 本檔 7 條 → 加本條 8 條、311 行；未達 N≥11 或 1500 行任一硬觸發。10 次 backstop：S217 做過全面維護，其後 S218–S222 共 5 次，未到。
- **Playbook（§14 留底）:** 兩行 usage（`freshness-monitor-test-served-url` lookup、`cloud-routine-vs-local-task` applied）＋ 新提案 `inbox/2026-09-13-policychecker-watchdog-for-cron-monitors.md`（「檢查報告不了自己從未運行」）。已 commit 並 push（`3d41612`）。
- **Opening-message mirror:** 見交接檔 `Next Session Opening Message`；本 log 依 Kit 契約不複製全文，只記驗證結果。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-12 Session 221 — cpd 路由慢的成因是查詢計劃把過濾次序倒轉；刪一行 GUC 令 S219 那個索引首次真的被用上

- **ID:** `Claude_20260912_0655` — S221
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。跑起手探針揪出 S220 收工 commit 未 push（Leonard 自行 rebase＋push）；跑版本閘後**改寫了 HNSW 的封鎖理由**；然後查 cpd 抖動，用 `explain (analyze, buffers)` 找出真因並由 Leonard 套用一行 DDL 修正。
- **Changed:** `dev/SESSION_HANDOFF.md`（Risks 1／4、OP ①③、Recommended next step、Current Baseline git 事實、開場白段落、Supabase Technical Notes 加 S221 block）· `dev/DOC_SYNC_CHECKLIST.md`（新增一行：外部平台事實重驗推翻既有判斷）· 新工具 `backend/scripts/_s221_routedBaseline.ts`。**零 `backend/src` 改動、零前端改動、零 git push。** 唯一外部寫入是 Leonard 在 Supabase 執行的一句 `create or replace function`。
- **Done:**
  1. **版本閘（OP①）跑完：Supabase 提供的 `vector` 版本最高只到 0.8.0 ＝ 已安裝版本，升無可升。** 並**改正了交接對這件事的定性**：擋住 HNSW 的不是 CVE-2026-3172（0.8.2 修，官方緩解為建索引前 `set max_parallel_maintenance_workers = 0`），而是 **0.8.3／0.8.4 那兩個 HNSW vacuum 修正 —— 關不掉**（autovacuum 必然會跑）。解封只有 Supabase 平台升級一條路。來源：pgvector CHANGELOG、NVD、Supabase Extensions 文件。
  2. **查明 cpd 抖動主因。** `explain (analyze, buffers)` 對照兩個 allowlist：curriculum 的 Filter 先 `source_id` 後距離（3,615 列／81,619 buffer hits／131ms）；**cpd 的 Filter 次序倒轉**，先為全部 17,610 列算距離（135,502 hits／9,639ms、重跑 5,475ms）。同一句放行 bitmap 之後走 `Bitmap Index Scan on wiki_chunks_source_id_idx`（939 列／17,433 hits／681ms）。**工作量降至 12.9%（buffer hits，確定性數字）；時間欄同一計劃三跑差近倍，屬實例負載，不作為結論依據。**
  3. **DDL 已套用（Leonard 執行）**：刪 `match_wiki_chunks_routed` 內的 `set local enable_bitmapscan = off`。連帶意義 —— S219 加的 `wiki_chunks_source_id_idx` 一直被那句封死，此前從未被用過。
  4. **正確性閘先立後驗（新工具 `_s221_routedBaseline.ts`）**：改前記低 7 條題的 routed RPC 回傳（id＋score），改後重用**同一批向量**再跑一次逐條比對。結果 **6/6 原本成功的完全相同**，第 7 條（cpd「專業階梯」）由 **HTTP 500／0 列 → 200／40 列**。
  5. **實測坐實了一個此前只是推斷的事**：改之前那條 cpd 題在本機 8 秒上限之下就已經逾時回 500，`catch` 吞掉後靜靜回落全庫搜尋 —— 即 cpd 這條路由在生產形同虛設，用戶不會察覺。
  6. **排除了自己提出的「cpd 每列貴 20 倍」。** 交錯重量三輪（A 只揀資料／B 揀+計算，兩個 allowlist 交替）：暖狀態每列 cpd **0.0096ms**、curriculum **0.0102ms**，總時間隨列數線性（×3.85 列 → ×3.9 時間）。**那 681ms 對 131ms 是冷熱兩個狀態的比較，不是兩批資料的差異。** 真正在飄的是實例：同一句第一次 916／2,259ms，第二三次 10／39ms，差 58–90 倍；**成因未查明**（EXPLAIN 報 `read=0`，頁面已在記憶體，照計不應如此；疑似免費方案 CPU 爆發額度，無證據）。附帶：暖狀態下 routed 查詢真實成本只有 10–39ms，用戶等的 1.5–2.4 秒主要在 embedding 與網絡。
- **QC:** `npm run check` 0 · `_s221_routedBaseline.ts --compare` **6/6 identical ＋ 1 was-failing-now-ok ＋ 0 problems** · `route_regression` **46/46** · `regression:grounded` **48/48** · 生產 `/api/search/channel-b` 三條 cpd 題各 3 次共 9 次全部 `ok`／8 結果（1.48–2.42 秒；**首次 24.6 秒是 Render 冷啟動，不是查詢延遲**）。**未做：同批查詢的生產前後對照**（前值取自 S220 記錄的 2.81／6.10／6.41 秒，非同一批、非同一時段），故「快了多少」只有指示性。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-12_s221_routed_before.json`／`_after.json`／`_vectors.json`（向量快取，供日後同基準重跑）。
- **Sync:** 交接檔 Risks 1／4、OP ①③、Supabase Technical Notes 已同步；`DOC_SYNC_CHECKLIST.md` 依其 anti-pattern 規則補了缺失的一行。`CODEBASE_CONTEXT.md` **N/A** —— pgvector 版本與 RPC 計劃設定不屬其 External Services 已登記項目（如日後要登記，應與 Supabase block 一併處理）。
- **Pending:** OP① 平台升級待 Leonard 決定 · Risks 4 餘下那截（cpd 每列仍比 curriculum 慢約 20 倍）未查明 · 三題 chunk recall · `qc_report.json` overall ERROR · 41 個指引 chunks=0 · registry 281 vs 服務 300。
- **Risks:** ⚠️ 本次 DDL 只在生產庫套用，**沒有 staging 對照**；回滾段已備在交接檔 Supabase Technical Notes。⚠️ 本機量度仍在 8 秒上限之下進行（`.env` 沒有 `SUPABASE_ANON_KEY`），故本節所有本機時間**不可當生產數**。
- **Log maintenance:** **no-op。** 本檔 6 條 → 加本條 7 條；未達 N≥11 或 1500 行任一硬觸發，10 次 backstop 亦未到。
- **Playbook（§14 留底）:** 收工時 grep 全表，配到 `inspect-live-infra-before-ddl`（本節確有照做：改 DDL 前先 `pg_get_functiondef` 抽 live 定義），已 append usage 一行（applied）。另交提案 `inbox/2026-09-12-policychecker-guc-disable-kills-filter-index.md`：為求 exact 而關索引，關得太闊會連過濾用的 btree 一齊封死；附冷熱交錯重量的判別法。兩者已 commit 並 push 至該庫。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成 `START_NEXT_SESSION_PROMPT.txt`（62 行 / 5,070 bytes），讀回逐位元組相等；全文按 Kit 契約不複製入本 log（沿用 S216–S220 對 §4 規則 12–14 與 Kit core 衝突的既定取捨）。
- **機器閘（收工實跑）:** `doctor` **53/53 status: passed** · `closeout-status` **status: complete**（首三次報 blocked，皆因本節記錄與 Open Priorities／Risks 有重複措辭令 lifecycle 讀回判為「已完成又仍待辦」；逐次收窄措辭後轉綠，內容未刪）· `session_log_maintenance.py --check` `trigger=False`。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-09 Session 220 — route-first 的碼與名字相反：它疊加而非取代全庫搜尋；修正後 OP② 在生產由 9 次 5 敗變 0 敗

- **ID:** `Claude_20260909_0700` — S220
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。Leonard 逐步授權：收 watcher commit → 補 OP③ → 全修文案 → 開始 OP① → 批 185 題 live 批次 → 揀「先修重試再開 flag」→ 在 Render 開 `FEATURE_ROUTE_FIRST_SEARCH=1`。**本節推翻了 S219 兩個結論，兩個都有實測支撐。**
- **Changed:** 8 個 commit 全部已推（`7ddafc7` `f8eabf0` `5cb1ec7` `e4090dc` `bda6ae8` `9072af1` `172c3cd` `6cbb49c`）。生產碼 `backend/src/api/searchChannelB.ts`、`backend/src/lib/wikiRepository.ts`。工具 `backend/scripts/routeFirstGold.ts`（改良）、`_s220_retryBudget.ts`、`dev/_s220_latency_verdict.py`（新）。文案 `README.md` `K1_API_SPEC.md` `CHANGELOG.md` `app.html` `index.html` `q.html` `t-purchase.html` `embed-sample.html` `mobile.js` `knowledge.json` `role_facts.json` `dev/knowledge/role_facts.json` `backend/README.md` `dev/source/execute_ingest.py`。平台 **v3.3.2 → v3.3.3**。
- **Done:**
  1. **推翻 S219「索引幫不到」。** 該結論源自 `select=id,embedding` 取 50 列 = 1,042ms → 16ms/列。實測每列回應 **19.3 KB**（50 列共 965 KB），那是 JSON 出口頻寬，不是伺服器運算。決定性一測：RPC 只回 **942 位元組**仍要 **3.37 秒**，與回 50 列的 3.41 秒相同 → 成本在伺服器端搜尋，索引直接相關。
  2. **揪出 route-first 的碼與名字相反。** `searchWiki` 在 1467 行無條件 await，無任何 branch 跳得過；routed 在其後跑並覆蓋結果 → flag 開啟時命中路由的查詢付雙倍代價、丟棄貴那半。**這才是 S219 那 26.4% 的成因**，不是「系統餘裕不足」。已修為 routed 取代、失敗才回落。
  3. **185 題閘重跑（Leonard 批准 live 批次）。** 185/185、errors=0。正確性與 S219 完全相同（FAIL→PASS 5、PASS→FAIL 4、淨 +1）——**證明次序修正不改檢索結果，只是不再白做**。
  4. **重試由次數制改為 6,000ms 時間預算。** 57014 代表已耗盡 `statement_timeout`，再試兩次等於再等兩個上限；gold 跑實測一題 8,842＋9,183＋8,316ms ≈ 27 秒。冷啟動閃斷的重試保留。兩個重複迴圈合併為 `postRpcWithRetry()`。
  5. **OP② 在生產解決。** 同三條題、同端點、前後皆在生產量：**9 次 5 敗 → 9 次 0 敗**，`cur_eight_kla` 由 3/3 敗變 3/3 過。設對照組（兩條無路由題）排除「整體變暖」：它們仍在 2.7–3.9 秒，有路由題已降至 1.4–2.2 秒。
  6. **全站文案對正**（Leonard 指示「留意適時更新」）：`sources` 六個鏡像寫 288、`app.html` 同屏另有寫死的 120，實查 distinct `source_id` 307 扣 7 個 `role_facts_*` = **300**；`index.html` 兩段幻影文案（S167 已移除的螢光標註、已下架的通告分析）；手機 `#templates` 死路加閘；README 四處自相矛盾；`K1_API_SPEC` 對下游報 152 而端點實為 158。另 `execute_ingest.py` 加 `live_sources_count()`＋step 5c 防再漂（**用具名欄位配對，不沿用裸數字全檔取代** —— 對 17610 安全，對 288 不安全）。
  7. **兩個休眠頁封路。** `q.html`／`t-purchase.html` 是已建未出街的功能。實測仍有活路徑：公開 README ＋ 交予學校 IT 的 `embed-sample.html` → `q.html` → `t-purchase.html`，三頁皆 200 且無 robots meta。已加 `noindex,nofollow` 並移除兩條入站連結，頁面本體不動。**刻意不加 `robots.txt`** —— `Disallow` 會令爬蟲讀不到 `noindex`，兩者互相抵消，且公開檔會替刻意不設連結的 status 頁賣廣告。
  8. **OP③ 補回** `backend/README.md` 遺失的 flag 說明。先查證不可還原（README 最後 commit `cd4c10e` 早於引入 flag 的 S214，`git log -S"FEATURE_"` 零結果），改為**由碼重寫**並在 commit message 明寫非還原。
- **Fix Record（自我推翻一次）：**
  - **問題：** 我由「40 列 0.5 秒 vs 全庫 3.1 秒」推出「每列約 1.1 毫秒」的成本模型。**根因：** 樣本只有兩點就外推線性關係。**實測反證：** curriculum 3,618 列只需 0.82 秒，而 cpd 939 列要 2.8–6.4 秒。**修正：** 該模型已撤回，成本不隨路由列數線性縮放；cpd 的抖動成因未查明，不編機制。
- **QC:** `npm run check` 0 · `build` 0 · `regression:grounded` **48/48** · `route_regression` **46/46**（含 flags-off 不變式閘）· `_s220_retryBudget.ts` **4/4**（離線 stub，零網絡）· `_s219_score_before_after.py --self-test` **6/6**。部署後生產實測 12 項全通過（`/health` commit＋暖機、三端點、noindex、入站連結、sources=300、幻影文案、mobile 閘、版本與快取鍵）。**未跑：Recall@k**（工具需要已刪除的舊 scratchpad 語料快取，重負載後不宜再拉語料；**未量，亦未沿用 S219 數字**）。
- **Evidence disposition:** 四份存 `dev/source/eval_runs/`：`2026-09-08_s220_route_first_before_after.jsonl`＋`.meta.json`、`_before.json`／`_after.json`、`2026-09-09_s220_op2_preflag_production.json`、`2026-09-09_s220_op2_postflag_production.json`。**兩份生產檔含全部回應 body（含失敗）** —— S217／S219 各有一次「未存 body 故成因無法證明」，本節不重複。
- **Sync:** `CODEBASE_CONTEXT.md` 已更新（route-first RPC block 的啟用狀態、次序、重試預算；另修正 S215 兩處已被交接推翻的記載 —— 本體「未經核實」已由 S219 introspection 結案、部署 build 引用次數由 `4a25a15` 的 0 更正為 `3ebd11f` 的 3）＋ AI Maintenance Log 兩條。`CHANGELOG.md` 加 v3.3.3 條目。
- **Pending:** OP① HNSW 未開始（**先決條件：Leonard 跑 `pg_available_extension_versions` 唯讀查詢**）· cpd 路由抖動未查明 · `qc_report.json` overall ERROR 未處理 · 41 個指引 chunks=0 · registry 281 vs 服務 300 的差額未對帳 · `app.html` KLA「多份」待 Leonard 定義精確數。
- **Risks:** 🔴 **CVE-2026-3172 影響 pgvector 0.6.0–0.8.1（本專案 0.8.0），觸發條件正是以 parallel worker 建立／重建 HNSW 索引** —— 未確認可升級前不得建 HNSW。⚠️ 本機量度比 Render 慢約 1.5–2 秒（實測：生產端到端做更多事只需 3.07–3.96s，而本機裸 RPC 已 3.31–3.88s），**故 S220 gold 跑的 35.1%／18.4% 是上限值，不可當生產數**。⚠️ 路由的 p90 尾部（8,335ms）比全庫（3,782ms）更差。
- **Log maintenance:** **no-op。** 本檔 5 條 → 加本條 6 條，255 行；未達 N≥11 或 1500 行任一硬觸發，S217 剛做過全面維護、10 次 backstop 亦未到。
- **規則衝突（依 §5 記錄）：** 沿用 S216–S219 的取捨 —— 專案 INSTRUCTIONS 層 §4 規則 12–14 要求把開場白逐字寫入本 log，本檔前言（Kit managed core）則明寫「The full opening message never belongs in this log」。取較可驗證且不製造第二個真相源的一方：只寫 mirror 行，全文留在交接檔。 **本節另撞到同一家族的第二處衝突**：§4 規則 5 要求開場白逐字使用「§1 startup sequence: … → dev/SESSION_LOG.md → …」模板，而 Kit managed core 的 anchor 要求開場白必須含「Do not read dev/SESSION_LOG.md during ordinary startup」—— 兩句語意直接相反。我起初寫了 §4 模板，`doctor` 隨即報 anchor 缺失（35 項檢查 1 項不過）。**取 Kit 一方**（機器可驗證，且與 S216–S219 的既有開場白一致），衝突記於此。
- **Playbook（§14 留底）：** **本節未 grep 全表、未開任何卡，故按該庫規則不寫 usage 行。** 但產生了兩條夠成熟可轉移的教訓，已備妥提案待交（見交接檔 Pending）：(a)「量到出口頻寬，卻用來論斷伺服器端成本」這個量度陷阱；(b)「當失敗本身就是逾時，重試預算應該用時間而非次數」。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成，讀回逐位元組相等；全文按契約不複製入本 log。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
