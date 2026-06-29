# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->
Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

Entries are kept, summarized, or archived — not current state. Do not remove validation evidence. Use latest opening message from most recent entry.

<!-- ack:section:session-log-entry-template -->
## Entry Template

- **ID:**
- **Summary:**
- **Changed:**
- **Done:**
- **QC:**
- **Evidence disposition:** <one-time only / kept as recent trace evidence / absorbed into handoff / indexed in PROJECT_INDEX / promoted to PROJECT_DECISIONS / promoted to rule pack>
- **Sync:**
- **Pending:**
- **Risks:**
- **Log maintenance:**

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first, then follow its §1 startup sequence:
Read in order: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
dev/DOC_SYNC_REGISTRY.md
```

---

<!-- ack:log-entry:start -->

## 2026-06-29 Session 190 — Option A Phase 3+4：populate ops repo + wire --live + ship executor.yml workflow

- **ID:** Claude_20260629_S190
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 起手探針 4/4 綠（served app.html v3.2.2 / Render warm 455 / HEAD `0ad0aed`==origin/main / knowledge 15,838）→ Leonard 貼 `https://github.com/Leonard-Wong-Git/edb-knowledge-ops.git`（已自建 private ops repo = Phase 3 前置①）。SSH ls-remote 證呢機 SSH key 對該 private repo 有讀寫權且 repo 全空 → 改變分工：原以為要 Leonard 雙手嘅「推 scaffold 入 repo」我可用 git over SSH 自己做。AskUserQuestion → Leonard 揀「做齊 ②+③」→ 完成後 Leonard 再講「做」→ 接住做 **④ Phase 4 executor.yml**。全程 inert：冇 secrets 任何嘢都唔會 live 入庫；Option A 4 phase 全部 ship，只待 Leonard 加 secrets 啟用。
- **Changed:**
  - **② Populate ops repo（git over SSH，非 gh CLI——gh 未登入）**：clone 空 `edb-knowledge-ops` → 將主 repo `dev/source/ops/` scaffold 複製做 repo root（README / APPROVAL_FORMAT / approvals{_TEMPLATE + edbc007 demo} / `.github/workflows/executor.yml.template`〔保持 `.template`、**未啟用**〕/ .gitignore）→ commit + push。ops repo HEAD `492a59b`（branch main）。**無 secrets 入 repo、workflow 仍 inert。**
  - **③ Wire `execute_ingest.py --live`（主 repo，commit `328b411`）**：加 6 步真執行（live_copy_to_vault〔複製 extract 落 vault 並改寫 header `topic_tags` 為 effective topic〕→ live_registry_append〔append entry，idempotent，更新 `_meta.updated`〕→ live_ingest〔subprocess `dev/ingest_one_source.py`，upsert by PK〕→ live_route_patch〔插入 SOURCE_SETS[route]，route 不存在則 raise 拒絕自動建〕→ live_display_sync〔9 檔 before→after，state-gated〕→ live_commit_push〔git add 指定檔 + commit + push HEAD:main〕）+ best-effort post_deploy_smoke（poll Render /health → Channel B 查新源是否 surface，非致命）。**三重閘**：(a) approval `decision==approved`（先於 secrets 檢查）(b) secrets pre-flight（無 OPENAI/SUPABASE key → exit 3、inert）(c) idempotent + resumable `execution_state.json`（失敗保留 approved、re-run skip 完成步驟）。`--live` 顯式 flag；bare invocation 改為報錯。docstring 更新。
  - **④ Phase 4 `executor.yml`（ops repo active workflow，HEAD `55854f2`，main `8cdc107`）**：Leonard 講「做」→ 接住寫 Phase 4。揭關鍵架構點：主 repo `dev/source/ingest_packages/` gitignored → workflow fresh clone 冇 package。核 `prepare_ingest_package.py` 介面（`--ids EDBC007/2026` 由 feed 確定性重生 package）→ 採「runner 重生 package」解法（integrity 取捨：執行時重抽，EDB 通告穩定+dupe-check 緩解；byte-pin 替代＝批准時 snapshot extract 入 ops，較重、未採）。寫 `executor.yml`：checkout ops+main(PAT)→setup py+install requests/pymupdf→git identity→「scan approvals(decision==approved)→per id 重生 package→copy approval→execute_ingest --live」bash loop；workflow_dispatch only（cron 註解，首跑驗好先開）、concurrency group、無 secrets inert。`execute_ingest.py init_approval` 加 `circular_number`（workflow 重生用，fallback regex 由 source_id 推導）；approvals(_TEMPLATE+edbc007 demo) 加 circular_number；APPROVAL_FORMAT + README 更新 Phase 3/4 狀態 + integrity note + Phase 4 啟用清單。刪 `executor.yml.template`（被 .yml 取代）。
  - **⑤ Leonard 加 3 secrets（ops repo）+ 端到端首跑（fail→修→成功）**：Leonard 加 PAT `MAIN_REPO_PAT`(fine-grained, Contents:RW edb-knowledge) + `SUPABASE_SERVICE_KEY`(本機 backend/.env，Render 冇——live 站只用 anon 唯讀，建議唔好加 service key 落 Render = least-privilege) + `OPENAI_API_KEY`，全 repo secret。**首跑 fail（19s）**：step 3 `ingest_one_source.py exit 1`＝runner 缺 `openai` package（workflow 只裝 requests/pymupdf；embed 喺 INSERT 前死 → 零 leaked insert 核實 Supabase edbc007=0、零 push、registry/vault 改動只喺 ephemeral runner、可逆）。**2 修**：ops `4bd9a00` `pip install requests pymupdf openai`；main `50c61f5` exec_live failed-step 偵測次序（報最早未完成步＝真失敗步，原報錯做 6_commit）。**re-run 成功**：bot `87997f1`。
  - **⑥ Leonard 4 點跟進（同 session）**：(1)(2) 更新日誌（index.html modal + update_log.json）兩輪：先改多來源 link（registry 逐源 url+短題、preview 實測 14/1/2/6/1/2/4 links 正確），Leonard 睇完反饋「**完全不顯來源 link**」+ 除技術/內部字眼 → **最終定案：每條只顯 日期+標籤+標題+簡潔描述、零 link**；除「（共 N 個知識片段）」「text-layer 逐字抽取/可追溯頁碼」「（首份經自動入庫管道入庫）」；`update_log.json` schema 收為 `{date,action,title,desc}`（URL 唔再存日誌、registry 為真源）；補 edbc007 entry（entries 8）；preview 實測 0 link/0 雜訊/截圖確認。main 至 `a4cc3f2`。 (3) **開每日 cron**：`executor.yml` `0 12 * * *`（HK 20:00）+ **idempotency guard**（source 已喺 main registry 即 skip、唔 re-ingest/唔漂 count；summary 加 skipped）→ 解決 stale approval / cron 重撞已入源；ops `401a9b1`。 (4) **批准 UX**：Leonard AskUserQuestion 揀「Issue 剔掣／留言批准」→ **起 `approval-issue.yml`**（ops `799723a`，GITHUB_TOKEN only）：refresh job（daily 11:30 UTC + manual）跑 check_new_circulars 砌私密 Issue「📥 待批准入庫候選」每候選一 checkbox；approve job（issues edited / issue_comment）剔 box 或 `/approve <num> route=...` → 寫 approval json + commit + dispatch executor + Issue 回覆。本地驗 parsing（checkbox/comment/sid）+ YAML valid；**未 live 測**（首測 = Run workflow 建 Issue → 剔一個 → 驗 approval 寫入 + executor 觸發）。私密性：批准面住 ops repo（非公開 main）解 S185 隱患。
  - **⑦ 批准 Issue loop 端到端 VERIFIED LIVE + off-by-one bug 修**：Leonard refresh 建 Issue（20 候選）→ 剔 EDBCM096/2026 → approve job 寫 approval+commit（ops `fdb654a`）→ executor 自動入庫（bot `7ce3e9f`，route=finance T2）。**揪出 off-by-one**：commit 原寫 +7→15,875 但 Supabase 實際 edbcm096=6 / 總 15,874 —— `plan_chunks` chunk staged extract 冇 strip `# header`（真 ingest `load_vault_sources` 有）→ delta 多 1（edbc007 啱啱唔受影響故首次冇暴露；本地實測 edbcm077 8→7、edbcm101 4→3）。**修**：plan_chunks strip header + exec_live 改用 live Supabase source count 做權威 delta（免漂）；9 display-sync 檔 15,875→15,874 修正。py_compile + dry-run 驗。main `7ce3e9f`→`0f2e6c8`。Supabase **15,874**、registry **244**。
  - **⑧ 更新日誌再精簡 + executor 自動寫日誌**：Leonard 反饋 edbc007 desc 仲有長簡介、唔應該有 → 8 條 desc 全改一行（去 synopsis；preview 實測 13–58 字）。再揀「executor 自動加精簡日誌」→ `live_append_update_log`（每入庫 prepend：標題=文件名+`_fmt_circular`通告號、desc=summary 首句截 ≤58、idempotent by title、隨 ingest commit；commit paths +update_log.json；exec_live step 5b）；補 edbcm096 entry。py_compile + temp 測（標題格式/idempotent/fmt_circular）✅。main 至 `b33052c`。
- **Done:** ② ops repo populated（HEAD `4bd9a00`）。③ `--live` wired（三重閘）。④ `executor.yml` active workflow。⑤ **端到端 VERIFIED LIVE**：機械人自動 commit `87997f1`、edbc007 +30 → Supabase 15,868、registry 243、searchChannelB:335 入 activity route、vault 建、display-sync 9 檔、凍結合約 intact、Channel B live rank-1（0.71）。Option A 4 phase 全 ✅、管道 OPERATIONAL。
- **QC:** (1) py_compile OK。(2) **dry-run regression** `--all-prepared` 行為同 S189 完全一致（edbc007 approved→GATE ✅；077/101 no-approval→⛔）。(3) **approval-gate**：`--live` on edbcm077（無 approval）→ exit 1，未掂 secrets/live。(4) **secrets-guard**：forced-empty secrets + bogus BACKEND_ENV on approved edbc007 → exit 3、無 state 檔、零寫入。(5) **零 live 寫入核實**：無建 dev/vault/edbc007_2026 / registry 仍 242 / knowledge 仍 15838 / searchChannelB.ts diff 空 / git status 只 execute_ingest.py（execution_plan + ops/ 皆 gitignored）。(6) **Phase 4**：executor.yml YAML valid（PyYAML safe_load，workflow_dispatch only、6 steps、concurrency group）/ init_approval 出 circular_number（temp dir 測，無污染）/ regex 推導 3 ids 正確（edbc007→EDBC007/2026 等）/ ops+main JSON 全 valid。**注意：本地 backend/.env 有真 secrets，故未 run 真 `--live`（會真入庫+push）——live 端到端留 Phase 4 workflow 首跑（manual workflow_dispatch、Leonard 人盯）。**
- **Evidence disposition:** absorbed into handoff Current Baseline + Open Priorities；QC trace 留本 entry。
- **Sync:** 無 display-sync（無 chunk 變）/ 無凍結合約改 / 無 PLATFORM_VERSION bump（純 dev 工具 + 外部 ops repo；Supabase/Render/Pages 零接觸；execute_ingest.py 屬 dev script，backend byte-identical → Render no-op redeploy）。ops repo 係 separate private repo，唔入主 repo display-sync。
- **Pending（非阻塞，管道已 operational）:** (1) Leonard 信心夠時 uncomment `executor.yml` cron 開每日自動；(2) edbc007 demo approval 仍 `approved`——re-run idempotent 無害（registry/route skip、display-sync no-op、Supabase upsert 同 id），要清可改 decision 或刪檔；(3) **Follow-up（低優先，未 wired）**：run 後 write-back annotate ops approval（resulting commit + chunk delta / close candidate Issue）；目前只記入 main ephemeral checkout。
- **Risks:** Phase 3/4 碼 LOW（inert、三重閘、可逆/resumable）。⚠️ live_display_sync 用「全檔 replace before-count 字串」（同 manual 做法一致；current count 只現於 current-state + 最新 CHANGELOG entry，舊 entry 數字不同故不誤改，但屬假設）。⚠️ **Phase 4 integrity 取捨**：executor 執行時由 feed 重生 package（非批准時 snapshot），若上游 PDF 批准後改過，入嘅係新內容（EDB 通告發佈後穩定 + dupe-check 緩解；要 byte-pin 改為 snapshot extract 入 ops repo）。⚠️ 真 `--live` 未端到端跑過（無安全方法本地測而不真入庫）；Phase 4 首跑要人盯。⚠️ write-back annotate ops approval 未 wired（run 結果只記 main ephemeral checkout）。⚠️ Render free-tier cold-start ~50s（smoke poll 已留 ~160s buffer）。
- **Log maintenance:** §4a 檢查：SESSION_LOG <400 行、最舊 entry <30 日 → 唔觸發 archive。no-op。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft
Read AGENTS.md first, then §1 startup: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md. Read dev/DOC_SYNC_REGISTRY.md before file changes/closeout.
起手探針: served app.html PLATFORM_VERSION 3.2.2 + Render /health warm 455 + Draft HEAD==origin/main + Supabase chunk count 15,868.

Current: 平台 v3.2.2; Supabase 15,874; registry 244; 凍結合約 _meta 2.3.0/facts 455/guidelines 158; 0 outstanding bug. main HEAD 0f2e6c8; ops repo edb-knowledge-ops HEAD fdb654a.
Option A 自動入庫管道 4 phase 全 ✅ + 端到端 VERIFIED LIVE + OPERATIONAL + 每日 cron 已開: S190 首次全自動入庫 edbc007 成功 (Leonard 批准 → workflow 重生 package → embed+INSERT → route patch → display-sync → bot commit+push → Render redeploy → live rank-1). executor.yml cron 0 12 * * * (HK20:00) + idempotency guard (已入 registry 即 skip). 更新日誌精簡(只 日期+標題+簡潔描述、無 link、無技術字眼).
批准 UX = Issue 剔掣／留言批准 ✅ 端到端 VERIFIED LIVE (Leonard 剔 EDBCM096 → 自動入庫 +6 → 15,874; off-by-one bug 已揪出+修). NEXT (非阻塞低優先): (1) write-back annotate ops approval 未 wired; (2) refresh 重寫 body 重置未入庫剔號 (cosmetic). [已完成 S190: executor 自動寫 update_log 一行 entry per ingest; 更新日誌精簡定案=每條一行/無link/無synopsis]. 日後新通告流程: 每日 refresh Issue 列候選 → Leonard 剔 box (或 /approve <num> route=...) → approval-issue 寫 approval + dispatch executor → 自動入庫+部署 (cron 兜底).
其他 backlog: S187 安全(repo私有化 — 可同 ops 合一)/S186 2源 monitor/Feature 2a/2b/Phase 3 full_chunks_routed.
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-06-28 Session 189 — Option A 自動入庫管道 Phase 2（dry-run executor + 批准格式 + ops repo scaffold）BUILT + QC

- **ID:** Claude_20260628_S189
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 起手探針 4/4 綠（served app.html v3.2.2 / Render warm 455 / HEAD `134dcce`==origin/main / knowledge 15,838）→ Leonard `/goal 1` = 推進 **Option A 自動入庫管道 Phase 2**。把 S188 手動 staging 之後嘅 live 入庫管道做成一個**可審計 dry-run executor**，並設計批准格式 + 起未來 private ops repo 嘅 scaffold。全程 staging-only、零 live 寫入、可逆（跟 S188 紀律）。Phase 3（live executor）+ Phase 4（端到端 workflow）需 Leonard 先開 private repo + set secrets，已清楚標 boundary。
- **Changed:**
  - **新 file `dev/source/execute_ingest.py`**（tracked）：Option A Phase 2 dry-run executor。接一個 staged package，模擬 6 個 live 步驟並寫 `ingest_packages/<id>/execution_plan.json`：(1) copy extract→`dev/vault/<id>/`（顯示 src/dest/bytes）(2) registry-append（按真 schema 砌 entry）(3) ingest chunk（重用 build_wiki_index canonical chunker，count + char stats + page-resolvable + sample vault_id，**唔 embed/INSERT**）(4) route-patch（喺 searchChannelB.ts 定位 `SOURCE_SETS[<route>]` block + 顯示插入點/preview，已存在則 no-op）(5) display-sync（讀 knowledge.json `_meta.stats.chunks` before → after，列 9 個 touch-point 連 raw `15838`/逗號 `15,838` 兩格式 + occurrence count）(6) commit message。**批准 gate**：approval record `decision != approved` → plan 標 WOULD-BLOCK；**live 模式（無 --dry-run）hard-refuse exit 2**（Phase 3 未 wired，附手動 fallback 指引）。human overrides（topic/route/tier）覆蓋 auto-proposal。
  - **新 scaffold `dev/source/ops/`**（gitignored，未來 private `edb-knowledge-ops` repo 種子）：`README.md`（架構 + 為何 hosting public / 批准 private + Phase 3/4 Leonard 設置清單）/ `APPROVAL_FORMAT.md`（approval record schema + approver 指引）/ `.github/workflows/executor.yml.template`（未來排程 executor workflow，inert template）/ `approvals/_TEMPLATE.approval.json` + `approvals/edbc007_2026.approval.json`（DEMO record）/ `.gitignore`。
  - `.gitignore`：加 `dev/source/ops/`（種子 separate private repo、唔 track 入 public repo）；S188 ingest_packages comment 補 execution_plan.json。
- **Done:**
  - ✅ executor dry-run 喺 S188 留低 3 個 staged package 全跑通：edbc007_2026（finance/T1，+30 chunks，route finance block 293-302）/ edbcm077_2026（activity/T3，+8）/ edbcm101_2026（placement/T3，+4，route placement 217-220）。
  - ✅ **完整批准流程端到端示範**：`--init-approval` 建 pending → 改 `edbc007_2026` decision=approved + override route finance→activity → re-run dry-run：GATE ⛔→✅、effective route 翻 activity（approval-override）、route-patch 改指 `SOURCE_SETS.activity` block 328-335、char_med 591 對齊 package。
  - ✅ live 模式 hard-refuse exit 2 驗證。
- **QC:** py_compile（execute_ingest + prepare_ingest 兩者）OK。**零 live 寫入核實**：dev/vault/edbc007_2026 唔存在 / registry 仍 242 / knowledge.json 仍 15838 / searchChannelB.ts `git diff` 空。git status：只 `.gitignore`(M) + `execute_ingest.py`(??)，`ops/` 正確 ignore。
- **Evidence disposition:** Phase 2 完成 absorbed into handoff Current Baseline + Open Priorities；dry-run trace 留本 entry。
- **Sync:** 無 display-sync / 無凍結合約改 / 無 PLATFORM_VERSION bump（純新 dev 工具 + scaffold；Supabase/Render/Pages 零接觸；commit 推 inert 工具，backend byte-identical → Render no-op redeploy）。
- **Pending（Phase 3-4 需 Leonard 參與，HIGH risk）:** Phase 3 = wire `execute_ingest.py --live`（真做 6 步 + commit/push，approval gate + post-deploy smoke + 失敗 re-open 守住）；Phase 4 = `executor.yml` 排程 scan approvals → live executor per record → 回報。Leonard 前置：開 private repo `edb-knowledge-ops` + PAT(`MAIN_REPO_PAT` contents:RW on edb-knowledge) + secrets(`SUPABASE_SERVICE_KEY`/`OPENAI_API_KEY`) + 揀 trigger。詳見 `dev/source/ops/README.md` 清單。
- **Risks:** Phase 2 LOW（staging/dry-run/可逆）。executor route-patch 對「未存在嘅 route」會 warn 要 human 建 block（非靜默）。auto-proposal tier/route 仍係建議，approval gate 兜底。Render free-tier cold-start ~50s。
- **Log maintenance:** §4a 檢查：SESSION_LOG 387 行（<400）、最舊 2026-06-25（<30 日）→ 唔觸發 archive。no-op。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: 平台 v3.2.2; Supabase 15,838 chunks; registry 242; HEAD==origin/main (S189 latest); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158; 4 監察 active; 0 outstanding bug.
起手探針: served app.html PLATFORM_VERSION 3.2.2 + Render /health warm 455 + Draft HEAD==origin/main + Supabase chunk count.

Option A 自動入庫管道進度: Phase 1 (S188) 入庫包生成器 prepare_ingest_package.py ✓; Phase 2 (S189) dry-run executor dev/source/execute_ingest.py + 批准格式 + ops repo scaffold dev/source/ops/ (gitignored) ✓ — 全 staging-only 零 live 寫入. 三 staged package 已備 (edbc007 approved-demo / edbcm077 / edbcm101).
NEXT 待 Leonard: Phase 3 = wire execute_ingest.py --live (真 6 步 + commit/push, approval gate + smoke + 失敗 re-open). 前置(需 Leonard 雙手): 開 private repo edb-knowledge-ops + PAT MAIN_REPO_PAT + secrets SUPABASE_SERVICE_KEY/OPENAI_API_KEY — 清單見 dev/source/ops/README.md. 然後 Phase 4 = executor.yml 排程 端到端.
其他 backlog: S187 安全(repo私有化+hosting搬遷/Supabase RLS/sibling審) — 可同 Option A private-repo 合一; S186 2源 monitor (edbcm073/edbcm066 短query排名低); Feature 2a/2b; Phase 3 full_chunks_routed.
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-06-28 Session 188 — Option A 自動入庫管道 Phase 1（入庫包生成器）BUILT + 測試

- **ID:** Claude_20260628_S188
- **Summary:** Leonard「做埋」→ AskUserQuestion 揀範圍 = **只起 Option A 自動入庫管道**（唔郁 live 站、唔轉 private、唔做 RLS/sibling，嗰啲留 backlog）。我先講清「Option A 個 private repo（批准 queue）≠ 將公開站轉 private」（後者會令 policychecker.wongfu.net 404，GitHub Pages 免費 plan 不支援 private — S163 outage 根因，故絕不盲 flip）。起 Phase 1 包生成器。
- **Changed:**
  - **新 file `dev/source/prepare_ingest_package.py`**：Option A Phase 1 入庫包生成器。把 S186 手動 verbatim-ingest pipeline 腳本化成一個可覆核步驟。STAGING-ONLY（只寫 `dev/source/ingest_packages/<id>/`，零掂 Supabase/git/vault/deploy/registry）。流程：fetch circular.wongfu.net feed → 下載 PDF → text-layer probe（avg<100 chars/page = needs_ocr 自動 hold）→ PyMuPDF verbatim 抽 canonical extract（header + `=== Page N ===`，同 ingest_one_source byte-format 一致）→ dry-run chunk（build_wiki_index 同一 chunker，count+page-resolvable+char stats）→ dupe-check（PDF basename + derived source_id vs registry）→ 自動建議 source_id（EDBCM080/2026→edbcm080_2026）/ topic（dashboard topics→VALID_TOPICS）/ route（keyword 鏡 TOPIC_KEYWORDS）/ tier（TIER3 event keyword → skip；mandatory+substantive → T1；其餘 T2）→ attach deadlines/grant_info/k1_topics/channel_b_facts gap → 寫 package.json + INDEX.md。
  - `.gitignore`：加 `dev/source/ingest_packages/`（transient staging output）+ `new_circulars.json`（watcher CI output）。
- **Done:**
  - ✅ py_compile OK。實測 4 候選：EDBCM080（今日已入庫）→ **DUP 正確偵測 skip**；EDBCM077 卓越教學獎 → **T3**（event keyword）；EDBCM101 中一測驗舉行日期 → **T3 + placement route**；EDBC007 開放校舍體育計劃 → **T1**（borderline，human 覆核可改）。全部 extract + chunk + page-resolvable=true、deadlines（3/2/3/1）全捕捉。
  - ✅ 確認 package「準備包」含齊批准面需要嘅嘢：proposed source_id/topic/route/tier(+reason) + dashboard signals + summary + canonical extract（approve = copy 去 dev/vault/ + 跑 ingest_one_source.py 不變）+ chunking stats + dupe flag。
- **QC:** py_compile + 4-candidate live 測試（dupe/tier/route/extract/chunk/deadline 全對）。Phase 1 = LOW risk、純 staging、可逆。
- **Evidence disposition:** Phase 1 完成 absorbed into handoff；測試 trace 留本 entry。
- **Sync:** 無 display-sync / 無凍結合約改 / 無 version bump（純新工具腳本）。
- **Pending（Phase 2-4 需 Leonard 參與，HIGH risk，逐 phase sub-PLAN）:** Phase 2 = 建 private ops repo（edb-knowledge-ops）+ 批准格式（package.json → private Issue/檔）+ executor dry-run；Phase 3 = cross-repo token/secrets + live executor（批准 → copy extract→vault → ingest_one_source → route patch → push → display-sync，免開 Claude/git）；Phase 4 = 串通 偵測→自動準備→批准 端到端。安全 backlog（S187）：repo private+hosting 搬遷 / Supabase RLS / sibling repo 審。
- **Risks:** Phase 1 tier/route 係建議（human 5 秒覆核兜底，設計如此）；OCR 檔自動 hold 留人手。Render free-tier cold-start ~50s。
- **Log maintenance:** §4a 檢查：SESSION_LOG < 400 行、最舊 entry 在 30 日內 → 唔觸發 archive。no-op。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: 平台 v3.2.2; Supabase 15,838 chunks; registry 242; HEAD==origin/main (S188 latest); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158; 4 監察 active; 0 outstanding bug.
今日 (2026-06-28) 三大件: S186 watcher 首批 14 條 2026/6 EDB 通告入庫 (2 monitor: edbcm073/edbcm066 短query排名低); S187 安全審計修 API abuse (rate-limit wallet-drain + body cap + Channel A scrape cap) LIVE; S188 Option A 自動入庫管道 Phase 1 包生成器 BUILT (dev/source/prepare_ingest_package.py, staging-only, 測試綠).
起手探針: served app.html PLATFORM_VERSION 3.2.2 + Render /health warm 455 + Draft HEAD==origin/main + Supabase chunk count.
Next (待 Leonard): Option A Phase 2 (建 private ops repo edb-knowledge-ops + 批准格式 + executor dry-run, 需 Leonard 開 repo + set secrets) → Phase 3 live executor → Phase 4 端到端. 安全 backlog: repo轉private+hosting搬遷 / Supabase RLS / sibling repo審. 其他: Feature 2a/2b, Phase 3 routed.
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-06-28 Session 187 — 安全審計（12-agent workflow）→ 修 API abuse surface 1 HIGH + 2 MED LIVE

- **ID:** Claude_20260628_S187
- **Summary:** Leonard 問「PolicyChecker 核心放 GitHub 是否人人可取用 / 15,838 chunks 會否被 clone 走或引用去其他系統」→ 開 12-agent 安全審計 workflow（5 維度並行 repo_visibility/secret_leakage/data_extractability/backend_ip/api_abuse + 每 material finding 敵意覆核，全程 read-only 無觸碰 live service）→ 回答 + 修 3 個確認漏洞。
- **審計結論（770k tokens、187 tool calls）:**
  - repo `Leonard-Wong-Git/edb-knowledge` = **PUBLIC**（GitHub Pages 免費 plan）→ tree + git history world-readable；sibling `EDB-AI-Circular-System`（circular.wongfu.net）都 public。
  - **Secrets 全清白** ✅：Supabase service/anon key + OpenAI key 從未 commit（backend/.env gitignored、git history 零 JWT、前端零 key、search 經後端 proxy）。
  - **15,838 chunks 本身難 clone** ✅：住 Supabase 非 repo、anon key 不在 repo/前端（REST 401）、無 write endpoint、sync X-Sync-Key gated、Channel B top-8/大 top_k 拒。
  - 灰色地帶：backend 邏輯 + 揀料藍圖（registry 242 + vault 19MB verbatim）public = 可照藍圖 rebuild；Channel A 455 + min_score:0 dump public-by-design。
- **Changed（`d12a2c2`）:**
  - `backend/src/server.ts`：(1) `getClientIp` 改用 XFF **最右 hop**（Render-trusted，唔再信 spoofable 最左）；(2) `GLOBAL_RATE_LIMIT=120/min` + `checkGlobalLimit()` backstop（denial-of-wallet 平台無關閘）；(3) search ×3 + `/analyze-circular` 加 `readJsonBody` body cap（16KB / MAX_TEXT_CHARS）+ PAYLOAD_TOO_LARGE→413。
  - `backend/src/api/searchChannelA.ts`：`min_score` clamp floor 0.05 + result cap 50（防 `min_score:0` 一 call dump 455）。
- **Done:**
  - ✅ 修 🔴 HIGH（rate-limit XFF spoof → OpenAI denial-of-wallet）+ 🟠 MED（body cap，memory DoS）+ 🟢 LOW（Channel A bulk-scrape）。
  - ✅ 本地實測 3/3 PASS（min_score:0→total 50 / 20KB body→413 / 12 rapid→429 after 10）+ tsc exit 0。
  - ✅ prod LIVE 驗：min_score:0 由 455→**50**、正常 Channel B 搜尋 8 results+synthesis（top=edbcm080_2026）、oversized→413、/health warm 455。
- **QC:** 本地 server `--env-file` 起喺 :8787 probe 3/3、tsc 0、prod poll 確認部署、prod sanity 3/3。push `d12a2c2`。
- **Evidence disposition:** 審計結論 + 未修 backlog absorbed into handoff baseline + Open Priorities；完整審計報告喺 task output（wc1wnmm33）trace。
- **Sync:** 無 display-sync（chunk 數零變）；凍結合約零接觸；無 version bump（純後端安全修補）。
- **Pending（Leonard 揀只修 API、其餘留 backlog）:** 🟠 backend IP 全公開（修法=repo private + hosting 搬離 Pages，同 Option A private-repo 合一）；🟢 Supabase RLS-off + anon SELECT（建議開 RLS / anon RPC-only）；sibling repo 待審；GitHub Issues world-readable（low）。
- **Risks:** XFF 右-hop 假設 Render append 真 IP 喺最右（審計實證 + 業界 single-proxy 標準做法）；GLOBAL_RATE_LIMIT 120 backstop 平台無關兜底。Render free-tier cold-start ~50s。
- **Log maintenance:** §4a 檢查：SESSION_LOG < 400 行、最舊 entry 在 30 日內 → 唔觸發 archive。no-op。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: 平台 v3.2.2; Supabase 15,838 chunks; registry 242; HEAD==origin/main d12a2c2 (後接 closeout docs commit 如有); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158; 4 監察 active; 0 outstanding bug.
S186: watcher 首批 14 條 2026/6 EDB 通告入庫 (2 monitor: edbcm073/edbcm066 短query crowded-route 排名低).
S187: 安全審計修 API abuse (rate-limit wallet-drain + body cap + Channel A scrape cap), LIVE 驗綠.
起手探針: served app.html PLATFORM_VERSION 3.2.2 + Render /health warm 455 + Draft HEAD==origin/main + Supabase chunk count.
Next 大方向 (待 Leonard 揀): (1) Option A 自動入庫管道正式 build (準備包+一撳批准, 同 repo-private 安全加固合一) (2) 安全 backlog: repo 轉 private + Supabase RLS + sibling repo 審計 (3) Feature 2a/2b / Phase 3 routed.
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-06-28 Session 186 — watcher 首批真實捕捉 → 14 條 2026/6 EDB 通告批次入庫 (Tier 1+2) LIVE

- **ID:** Claude_20260628_S186
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 起手探針全綠（HEAD `c545bea`==origin/main、app v3.2.2、Render /health warm 455、Supabase 15,656）。Leonard 手動行 → 收到第 4 監察 (S185 建 new-circular watcher) 首次真實 email：GitHub Issue #3 撈到 29 條未入庫通告。我做 dupe check + K1 相關性 triage（Tier 1 核心政策 6 / Tier 2 撥款計劃 8 / Tier 3 過渡公告 15）→ AskUserQuestion → Leonard 揀 **Tier 1+2 = 14 條** 入庫。跟 S181/S183 pipeline 全程執行：下載 → PyMuPDF verbatim 抽 → canonical chunk → live Supabase INSERT → route patch → push → Render+Pages redeploy → live verify。
- **Changed:**
  - **Supabase wiki_chunks +182**（14 新 `vault_extract` source，15,656 → **15,838**，逐源 INSPECT before=0 確認無重複）。14 源：edbcm080(14)/edbcm060(68)/edbcm088(5)/edbcm081(7)/edbc010(5)/edbc012(3)/edbc009(9)/edbcm070(10)/edbcm089(15)/edbcm073(12)/edbc011(5)/edbcm066(14)/edbcm107(10)/edbcm095(5)。
  - `dev/vault/<14>/extract_*.txt`：14 個 canonical verbatim extract（metadata header + `=== Page N ===`、全 text-layer、NUL=0）。
  - `backend/src/api/searchChannelB.ts`：9 route SOURCE_SETS 擴（kg_admission/kg_admin/hr_admin/student_support/curriculum/finance/safety/activity/digital_education/gifted）+ TOPIC_KEYWORDS 加 語文能力要求/基準試/準英語教師/英語教師獎學金(hr_admin)、免費午膳/在校午膳(student_support)、數學建模(curriculum)、電子學習撥款/流動電腦裝置/上網支援(digital_education)、家校合作/家庭與學校合作/家教會(activity)、多元學習津貼(finance)；**activity route 提升至 finance 之上**（防「家校合作活動整合津貼」被 finance「津貼」偷）。
  - `source_registry.json` 228 → **242**（+14 entries 全含 freshness_metadata）。
  - Display-sync 7 處（role_facts ×2 / knowledge.json _meta.stats.chunks / index.html ×3 / app.html ×4 / K1_API_SPEC / README ×4）+ update_log.json 新 entry + CHANGELOG S186 entry。15,656 → 15,838。
  - **凍結合約零接觸**：knowledge.json `_meta.version`=2.3.0 / facts=455 / guidelines=158 不變（只 chunks 動態 stat 升）；無 PLATFORM_VERSION bump（維持 v3.2.2）。
- **Done:**
  - ✅ 14 條全部 live INSERT，Supabase 總數 15,838 核對齊（per-source sum=182）。
  - ✅ Routing smoke `detectQueryCategory` **21/21 PASS**（14 新源 query + 7 regression）。tsc exit 0。
  - ✅ Render+Pages redeploy LIVE：12/14 源喺 top-8 surface（edbc010 rank-0、edbcm081 rank-1、edbcm080/070/089 rank-2、edbcm060 rank-3、edbc012 rank-4、edbc009/edbc011/edbcm107/edbcm095 rank-5、edbcm088 rank-7）全帶 synthesis。
  - ✅ Pages 前端 served index.html=15,838 + 更新日誌新 entry live；Render warm 455；凍結合約完整。
- **QC:** verbatim spot-check（KG 報名費$40 / 消防年檢 / 數學建模）✓；NUL=0；dupe check 全 0 hit + INSPECT before=0；routing 21/21；tsc 0；live 12/14 top-8。commits `b79f475`（ingest+route+display-sync+docs）push origin/main。
- **Evidence disposition:** 入庫結果 + 新 baseline absorbed into handoff；trace（rank/score 明細）留本 entry。
- **Sync:** display-sync 7 處 + update_log + CHANGELOG done；DOC_SYNC registry 不需額外（內容新增類，已跟 display-sync rule）。CODEBASE_CONTEXT External Services 無新增（同 endpoint）。
- **Pending:** ⚠️ **2 源 monitor**：edbcm073_2026（電子學習撥款，digital_education route 被 DEBP/AI corpus 0.69-0.73 擠出 top-8）+ edbcm066_2026（準英語教師獎學金，hr_admin 被 sag/g04 0.73 擠出；fuller query「準英語教師獎學金 2026/27 申請」surface rank-7）— in-route 可檢索但短 query 排名低（S152 cgss 同類）。Leonard 若報 miss 再 boost（dedicated micro-route / lead-slot / supersede-style boost）。其餘 29 條未入嘅 15 條 Tier 3 過渡公告（活動/比賽/日期/獎項）按 S170 鐵律不入。
- **Risks:** Render free-tier cold-start ~50s。2 monitor 源見 Pending。Option A 自動入庫管道仍待下次專注 session PLAN（HIGH risk）。
- **Log maintenance:** §4a 檢查：SESSION_LOG 269 行 < 400、最舊 entry 在 30 日內 → 唔觸發 archive。no-op。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current state: 平台 v3.2.2; Supabase 15,838 chunks (S186 +182, 14 條 2026/6 EDB 通告批次入庫); registry 242; HEAD==origin/main b79f475 (後接 closeout docs commit 如有); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158; 4 個自動監察 active (discover/freshness/served-url/new-circular); 0 outstanding bug.
起手探針: served app.html PLATFORM_VERSION 3.2.2 + Render /health warm 455 + Draft HEAD==origin/main + Supabase chunk count。
Monitor: edbcm073_2026 + edbcm066_2026 in-route 但短 query 排名低 (crowded route) — Leonard 報 miss 先 boost。
Next 大方向: Option A 自動入庫管道正式 PLAN (HIGH risk) / Feature 2a 追問 + 2b 文件 scoped Q&A / Phase 3 full_chunks_routed。
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
