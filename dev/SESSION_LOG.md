# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-31 Session 136 — Mobile UI Phase 2：文件庫 (#guidelines) 專用 mobile render

- **ID:** Claude_20260531_1200
- **Trigger:** Leonard 確認 Channel B 已到設計天花板（CB-3 ~88% final ceiling、剩 ~12% 結構性硬限）→ 揀 option 4（Mobile UI Phase 2）；資料源拍板 = 148（與桌面一致）
- **§3 Risk:** HIGH（3 檔 app.html/mobile.js/mobile.css + 公開 brand 介面 policychecker.wongfu.net；criterion a/b）→ 出 PLAN 等 Leonard 拍板資料源 → 入 CHANGE

### READ — 交接 claim 實證為 stale（§G.2 doc-drift 又中）
交接寫「index/q/t-purchase/app#guidelines 手機內容未 render」。實測（Explore agent + 直讀 code）：index/q/t-purchase 已 CSS 響應式、OK；**唯一真缺 = app.html#guidelines**。`mobile.js:421` 留明文 TODO「下節做專用 mobile render」；現時 fallback 硬露桌面 React panel，`w-44`(176px) 固定側欄喺 375px 壓爆內容（screenshot 證實標題逐字直排）。→ Phase 2 真範圍收窄成單一件事（≠ 交接講嘅 4 個介面）。

### CHANGE — 3 檔
1. `app.html`（+9）：registry 定義後 `window.GUIDELINES_REGISTRY = GUIDELINES_REGISTRY` + `dispatchEvent('k1-registry-ready')`（暴露 148 俾 vanilla mobile.js；desktop no-op、無害）
2. `mobile.js`（+215/-11）：新 `buildGuidelinesShell()` — 分類橫向 chips（zero-count 隱藏、鏡像桌面 CATS）+ 學習階段 chips + 最新/最舊/名稱排序 + 名稱搜尋 + 文件卡（format/year/level badge）tap→EDB 原文；filter/sort 語義完全鏡像桌面 `GuidelinesPanel`。guidelines 分支改 event-driven build + 12s poll backstop + graceful revealRoot fallback；新增 hashchange→reload（解 文件庫↔搜尋 tab 同檔 hash 切換唔 rebuild）
3. `mobile.css`（+216）：`.m-guide-*` 樣式（包在既有 `@media(max-width:640px)`、沿用既有 design tokens）

### §3 CHANGE divergence — TDZ bug（live-preview QC 揪出，textbook stop-and-fix）
首輪 preview shell 唔 build 且 0 console error。加 probe 揪出 `ReferenceError: Cannot access 'GUIDE_CATS' before initialization`。根因 = IIFE 頂部 eager-trigger `if(readyState!=='loading') initMobileShell()` 排喺 `const GUIDE_CATS` 宣告之上；deferred script 喺 'interactive' 執行 → init 早過 const init → TDZ。（既有 search shell 只靠後續 DOMContentLoaded re-init 僥倖 cover、latent 同類風險。）**修：eager-trigger 搬去 IIFE 尾（全部 module const 已 init 後）→ 連帶修咗 search shell latent TDZ。** Probe 事後全清（noProbes verified）。

### QC — live preview（Electron/Chrome real engine，375px mobile）全 PASS
- 6 §3d scenario 全 PASS：載入 #guidelines → 148 卡 / 8 分類 chip / 6 階段 chip /「148 份」/ 最新排序 ✓；分類 課程→127、+中學→52、搜尋「採購」→1（資助學校採購程序指引）、名稱排序 reorder ✓；TDZ 修復後 0 error；文件庫↔搜尋 tab hashchange→reload 正確換 shell ✓；**desktop 1280px → mobile.js no-op、React `.w-44` panel 正常、registry 暴露無害 ✓**；search shell 0 regression ✓
- card href = 真 EDB url；`node --check mobile.js` exit 0

### Sources changed
- `app.html`（registry 暴露 + event）/ `mobile.js`（buildGuidelinesShell + init relocate + hashchange）/ `mobile.css`（.m-guide-*）
- **NOT modified:** Supabase / knowledge.json / guidelines.json / source_registry / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT
- commit + push origin/main → GitHub Pages auto-deploy（policychecker.wongfu.net）；Leonard 真機 browser-verify pending

### CORS incident + fix（same-session follow-up — §8 regression record）

- **Problem:** Leonard 真機驗 Mobile 後回報 Channel B 政策搜尋「sen」出「搜尋服務暫未連線，請稍後再試」，retry 仍然。
- **Triage (§2b):** 非 code bug、非冷啟動。curl 實測：backend `/health` warm（200/0.22s）+ search endpoint 對 **無 Origin** request 正常返結果 → backend 本身通。但帶 `Origin: https://policychecker.wongfu.net` 嘅 OPTIONS/POST → `Access-Control-Allow-Origin` 回 `github.io`（≠ origin）→ **瀏覽器擋回應 → fetch throw → app.html:2881 catch 出 error**。= **環境/配置層 CORS bug**。
- **Root cause:** `getCorsOrigins()` = `process.env.CORS_ORIGIN || DEFAULT`。源碼 DEFAULT 自 S132 (c6dab15, 2026-05-28) 已含 policychecker，但 **Render env var `CORS_ORIGIN` 覆蓋咗 default 且只有 github.io** → live 清單缺 policychecker。**Latent 自 S132 brand launch：喺品牌域名搜尋一直 0 功能，因一直用 github.io origin 測試而未察覺**（§G.2 「測試環境 ≠ 生產環境 origin」教訓）。
- **Fix:** `backend/src/config/env.ts` 加 `BASELINE_CORS_ORIGINS = [github.io, policychecker.wongfu.net]`；`getCorsOrigins()` 改為 **union baseline + env origins**（baseline 行先、dedupe）→ 漏/錯 env var 都無法再令品牌域名離線；env var 仍可 ADD 其他 origin（如學校 iframe host）。
- **Verification:** typecheck+build exit 0；3 情境 node 單元驗（unset / stale-env-bug / env+school 都含兩個 brand origin）；commit `59494fa` push → Render auto-redeploy；live poll 第 4 次（~80s）ACAO 轉 `policychecker.wongfu.net`；端到端 `Origin: policychecker` POST「sen」= **HTTP 200 + ACAO match** ✅ → 原 error 解決。
- **§8b promote 候選:** 「first-party 品牌 origin 必須 code-baseline、唔可淨靠可變 env var」+「生產 origin 必入 smoke（唔好淨用 dev origin 測）」— recurrence 即 promote。
- **遺留（獨立、未修）:**「sen」短 query relevance 差 + `phys_sss_2007_2015` 源 **mojibake 亂碼**（端到端確認連 3 chunks surface、分數 0.26-0.27、零特殊教育/融合教育內容）→ 資料質素 backlog（同 S135 stat mojibake 同類；short-query-first）。

### Doc Sync
Matched row: **Product behavior / tuning change**（Mobile UI）+ **External API / service change**（CORS config）→ SESSION_HANDOFF + SESSION_LOG（done）。CODEBASE_CONTEXT N/A（mobile.js/.css 已在 dir map；CORS 屬 backend env 配置、無新 External Service block 欄位變）。

### UI polish（same-session follow-up，Leonard feedback）
- **命名統一「指引文件」**：原本 首頁(index.html)「文件庫」/ 內頁(app.html)「指引(148)」唔一致 → 三處 nav label + 手機 shell H1 全改「指引文件」（app.html「指引文件 (148)」保留 count）。
- **favicon 重新上色 navy→品牌綠**：原 favicon 背景係 navy `#0F2D5E`、唔 match 網站綠 header（`--edb #1F3A2E`）→ Leonard 要 favicon 背景跟網站背景色。PIL weighted colour-shift（`new = old + w*(green-navy)`、w 隨「離 navy 距離」漸變）保留 cream 文件 + 金色剔/§ + 平滑邊緣；重生 32/180/192/512 + source；原檔 §5.a backup `dev/init_backup/20260531_150222_UTC_favicon_navy/`。視覺 review 512 確認乾淨。commit `431ba09`。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135/S136 證實 EDB + onrender egress 均通 — handoff 舊「EDB 去唔到」假設已過時，仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S136 (2026-05-31)：**完成 (A) Mobile UI Phase 2 — app.html#guidelines（指引文件）專用 mobile render；(B) CORS incident 修復（品牌域名搜尋恢復）；(C) UI polish（命名統一+favicon 綠）**。Channel B 已到設計天花板（CB-3 ~88% final ceiling、剩 ~12% = 4 HTML + 5 xlsx 結構性硬限、不可再升）。HEAD origin/main = `c86d90a`（起手自行 verify）。

S136 做咗 **A. Mobile UI Phase 2**（3 檔，純前端、mobile-only、desktop 已驗證不受影響）：(1) `app.html` +9 暴露 `window.GUIDELINES_REGISTRY`(148) + `dispatchEvent('k1-registry-ready')`；(2) `mobile.js` 新 `buildGuidelinesShell()`（分類/階段 chips + 排序 + 搜尋 + 文件卡 tap→EDB，鏡像桌面 GuidelinesPanel）+ guidelines 分支 event-driven build + hashchange→reload；(3) `mobile.css` `.m-guide-*` 樣式。修咗一個 TDZ bug（eager init-trigger 早過 const → 搬去 IIFE 尾）。Live-preview 6 scenario + desktop no-op + search-shell regression 全 PASS。

S136 **B. CORS incident 修復**（Leonard 真機驗 Mobile 後揪出）：Channel B 政策搜尋喺 `policychecker.wongfu.net` 出「搜尋服務暫未連線」。Root cause = Render env var `CORS_ORIGIN` 覆蓋源碼 default、缺品牌域名 → ACAO 回 github.io → 瀏覽器擋。**Latent 自 S132 brand launch**（一直用 github.io origin 測試而漏咗）。Fix = `backend/src/config/env.ts` `getCorsOrigins()` union `BASELINE_CORS_ORIGINS`(github.io + policychecker) + env → 漏 env var 都無法再令品牌域名離線。commit `59494fa` push → Render redeploy → 端到端 `Origin: policychecker` POST = HTTP 200 + ACAO match ✅。**遺留（獨立未修）:**「sen」短 query relevance 差 + `phys_sss_2007_2015` 源 mojibake 亂碼（資料質素 backlog）。

S136 **C. UI polish**（Leonard feedback）：(1) 命名統一「指引文件」— 首頁 index.html「文件庫」/ 內頁 app.html「指引(148)」/ 手機底欄 + shell H1 全改「指引文件」；(2) favicon 背景 navy `#0F2D5E`→品牌綠 `#1F3A2E`（跟網站 `--edb` header；PIL weighted colour-shift 保留 cream 文件+金色剔/§+平滑邊；重生全尺寸；原檔 §5.a backup）。commit `431ba09` + PERSIST `c86d90a`。

⚠️ KEY LESSON S136：(1) **交接文檔 claim 又 stale**（§G.2）— 講 4 個 mobile 介面未 render，實測只 #guidelines 真缺；動手前實證咗先收窄範圍。(2) **deferred-script IIFE 的 eager `readyState!=='loading'` init-trigger 必須排喺所有 module const 之後**，否則 TDZ；live-preview probe 係揪呢類 silent fail 的關鍵（0 console error 都要 probe）。(3) in-browser Babel 編譯 app.html(4759 行)可 >3s，跨-script 時序用 custom event 比固定 poll timeout 可靠。(4) **生產 origin ≠ 測試 origin**：CORS/配置類問題用 dev origin（github.io）測唔到、要用真品牌域名（policychecker）端到端 smoke；first-party 品牌 origin 應 code-baseline、唔好淨靠可變 Render env var（§8b 候選）。

Current objective and progress state:
- Baseline: Supabase **9,849** / 102 marker-bearing / CB-3 final ceiling ~88%（已到頂、Channel B 無 pending 執行）/ brand live (policychecker.wongfu.net)
- **Mobile UI Phase 2 完成**（#guidelines 專用 mobile render live）；index/q/t-purchase mobile 經實證已響應式、無需動
- 下一階段方向待 Leonard

Pending tasks in priority order:
1. **🔴 資料質素 backlog（CORS 修好後浮面、user-facing）**：「sen」短 query → `phys_sss_2007_2015` 源 **mojibake 亂碼**（端到端確認連 3 chunks surface）+ 零特殊教育/融合教育。兩部分：(a) phys_sss mojibake re-index（同 S135 stat fix pattern、可做）；(b) 短英文 query relevance/routing（較深）。待 Leonard 決定優先。
2. **Leonard 真機 browser-verify**：(a) Mobile #guidelines（手機「文件庫」tab）；(b) Channel B 政策搜尋喺 policychecker.wongfu.net（CORS 已修、應通）。
3. **下一階段方向待 Leonard**：Q4 對外契約收斂（deferred 未明示勿掂）/ §8b automation / 39→148 / 既有 deferred backlog（§E.10 / 57014 / FAIL-A / stat_fact 2025/26 ROI≈0）。

Key files changed this session:
- `app.html`（暴露 GUIDELINES_REGISTRY + dispatch event；nav「指引文件 (148)」）
- `mobile.js`（buildGuidelinesShell + event-driven build + init-trigger 搬尾修 TDZ + hashchange→reload；tab/H1「指引文件」）
- `mobile.css`（.m-guide-* 樣式）
- `index.html`（nav「指引文件」）
- `backend/src/config/env.ts`（CORS hardening：BASELINE_CORS_ORIGINS union）
- favicon-32 / apple-touch-icon / icon-192 / icon-512 / icon-source.png（navy→綠；原檔 backup dev/init_backup/20260531_150222_UTC_favicon_navy/）
- dev/SESSION_HANDOFF.md + dev/SESSION_LOG.md

Known risks / blockers / cautions:
- **CORS 已修（commit `59494fa`、live verified）**；first-party 品牌 origin 現 code-baseline。Render env var `CORS_ORIGIN` 可繼續 ADD 其他 origin（如學校 iframe host）但唔再能令品牌域名離線。
- 🔴 **NEW 資料質素**：`phys_sss_2007_2015` mojibake 亂碼 surface（user-facing；待修）+ 短英文 query relevance 差。
- 既有不變: 🔴 57014 transient (retry); FAIL-A (record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB code path dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG
- mobile.js 教訓：任何新 module const 喺 init 路徑用到，必確保 eager init-trigger 喺其後（已搬 IIFE 尾、現安全）

Validation status:
- PASS: Mobile UI — `node --check mobile.js` exit 0；live preview 6 §3d scenario + desktop no-op + search-shell regression 全 PASS（375px + 1280px real-engine）
- PASS: CORS fix — `npm run check`/`build` exit 0；node 3-scenario union 驗；live ACAO 端到端確認 `policychecker` allowed + Channel B「sen」HTTP 200
- COMMITTED: Mobile `0c2e201` + PERSIST `664ecdb` + CORS `59494fa` + PERSIST `a58b089` + UI polish（命名統一+favicon 綠）`431ba09` origin/main（起手自行 verify HEAD），tree clean
- OPEN: 資料質素 backlog（phys_sss mojibake + 短 query relevance）；Leonard 真機 verify；下一階段方向待 Leonard

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD / knowledge.json stats facts:455 / Supabase 9,849 / egress onrender /health + **CORS：`Origin: https://policychecker.wongfu.net` 打 OPTIONS `/api/search/channel-b` 應回 ACAO=policychecker**）後，**Mobile UI Phase 2 + CORS 修復已完成**。第一件事＝問 Leonard：要唔要而家修資料質素 backlog（(a) phys_sss_2007_2015 mojibake re-index — 同 S135 stat fix pattern、可即做；(b) 短英文 query「sen」relevance/routing — 較深），定行其他方向。未 Leonard 明示前唔好自行 resume / 掂 Q4 契約 / reopen §E.10 / 動 Stage-2。
```

## 2026-05-30 Session 135 — Phase 3 全力完成 (3a #3 5源 no-op + 2 backfill〔history_jss_2019 + edbc197〕+ stat mojibake fix + allowlist parity)

- **ID:** Claude_20260530_1700
- **Trigger:** Leonard 揀 Phase 3a #3 剩餘源 case-by-case → 4-step read-only diagnostic → 唯一真 finding history_jss_2019 coverage gap → Leonard 授權 HIGH-risk backfill + deploy
- **§3 Risk:** diagnostic READ-only LOW；backfill (vault+Supabase+registry+backend allowlist+Render deploy) = HIGH，逐 gate 執行、Leonard 授權

### Phase 3a #3 diagnostic (read-only, paced 429-aware)

5 cluster 全 **healthy no-op**（Supabase REST count + paced live onrender smoke）：

| Cluster | chunks | 結論 |
|---|---|---|
| geog | geog_jss 203 / sss_2007_2022 214 / +40 = 457 | 「地理科」→ geog_jss p=106 ✓（「地理科課程指引」HTTP 400 = 已知 57014 transient，re-probe 正常）|
| pe | pe_kla_2017 74 / pe_sss_2023 79 = 153 | 「體育科課程指引」→ pe_kla_2017 top-3 0.71-0.74 ✓；pe_sss_2007_2015=0 確認 S125 deprecation 清走；pe_curr_docs=0 catalogue HTML |
| dat | 108 / ict 216 / music_sss 198 | 同 S134 cluster 一致、healthy |

grand total 對齊 baseline 9,713；無 throttle masking（429-aware script + 總數正常）。

### history_jss_2019 BACKFILL（唯一真 finding）

- **Gap:** history_jss_2019（歷史科課程指引 中一至中三 2019 = 西史/世界歷史初中）= **0 chunks**；live「世界歷史初中」mis-route 去中史 chi_hist_jss_2019。與中史 CHist_*、西史高中 Hist_C&A（history_sss_2007_2015 155 chunks）互不重疊。
- **Root cause = §E.12 EDB URL churn:** registry notes 揭原 `hist_c_j1-3_2019.pdf` 直連失效 → 曾改指 PSHE catalogue HTML（source_type=html）→ 從未提取。
- **Re-discovery:** curl EDB catalogue page（**egress 通 — 推翻 handoff「EDB 去唔到」假設**）+ 解析 PDF 連結，搵返 rename 後直連 `Hist_Curr_Guide_S1-3_Chi_final_10072019.pdf`（HTTP 200 / 5.9MB / 118p / page-2 標題核實西史初中）。
- **Backfill gated execute:** §5.a backup → registry 修正（url_primary 直連 PDF / source_type pdf / notes）→ repage_pdfs.py +PILOT_LEGACY/OUT entry（**首次全新源 path：header-stub seed**）→ repage --write Gate 1 **118 pages/markers** → cb3_b2 --execute Gate 2 **del=0 ins=125 純新增**（Supabase 9,713→**9,838**，per-source verify now=125 OK）。

### §3 CHANGE divergence — backfill-allowlist coupling

- 數據入庫 + unfiltered query 確認可檢索（history_jss_2019 #1 p=106），**但 curriculum-category query 仍 mis-route 去中史**。
- 根因 = backend `searchChannelB.ts` `SOURCE_SETS.curriculum` allowlist 未含 history_jss_2019（建表時佢仲係 0-chunks/html、實質唔存在）→ 「歷史科課程指引」match curriculum → 搜索限白名單 → 新源被 filter 走。
- STOP 報告 Leonard → 授權加 allowlist（**只加初中**；西史高中 history_sss_2007_2015 亦不在 allowlist = pre-existing gap、Leonard 揀暫不加）→ `npm check`/`build` exit 0 → commit `ceb7c91` push → **Render auto-deploy** → background poller verify：deploy 上線後「歷史科課程指引 中一至中三」→ **history_jss_2019 #1/#2/#3 p=1/46/6**，中史降 #4/#5。**Mis-route FIXED。**

### Lessons (§8 monitoring)

1. **§E.12 EDB URL re-discovery via catalogue 解析**：直連 PDF rename 後可由 catalogue page 解析搵返；「直連失效」唔代表文件消失。
2. **NEW backfill-allowlist coupling（§8b 候選）**：把新源 page-carry 入 Supabase **唔會自動 surface** — topic-routed category 受 `SOURCE_SETS` allowlist gate。**任何 future 新源 backfill 必同時檢查/更新 `SOURCE_SETS`**，否則 user-facing 零效果。recurrence-prone（任何新源都中）→ 留 recurrence 即 promote SOP。
3. egress 實測：EDB / onrender 本 session 均通；handoff「EDB egress 去唔到」假設過時（§G.2 verify-don't-trust 又中）。

### Phase 3c (same session — Leonard /goal「Phase 3 全力完成」)

5 catalogue-level HTML 源審核（fetch EDB + 解析 PDF 連結 vs registry/Supabase）→ 只 2 個真 actionable：

| 源 | 現況 | 處理 |
|---|---|---|
| **edbc197_2024_ph_pri** | 0 chunks、type=html 指 ph-primary index（§E.12：原 EDBCM24197C.pdf 失效）| EDB rename→`edbcm_197_2024_c.pdf`（HTTP 200/11p）→ registry 修正 + repage Gate1 11p/11markers + cb3_b2 Gate2 **del=0 ins=12** |
| **stat_edb_figures** | vault double-encoded mojibake（latin-1/utf-8）、2 garbage Supabase chunks | carry-decode 還原（2 byte-lossy split 字 六/其 由已知 EDB 刊物名復原）→ re-index `--include-non-page` **del=2 ins=1 clean** |
| arts_curr_docs | 0 chunks、catalogue | 8 PDF children（arts_kla/music/va）**全已索引** → 結構 no-op |
| moral_civic_curr | 0 chunks、catalogue.json | 5 children（values_edu/edbcm183/sec_6a…）**全已索引** → 結構 no-op |
| ph_pri_curr | 0 chunks、catalogue | children（ph_pri_guide_2025 146 + edbc9/12/20）**全已索引** → 結構 no-op |

**allowlist parity**：`SOURCE_SETS.curriculum` 加 `edbc197_2024_ph_pri` + `history_sss_2007_2015`（西史高中 pre-existing gap、Phase 3a 尾巴）。build/check exit 0 → commit `5d0d002` push → Render deploy → **live verify**：edbc197「小學人文科問卷調查」#1/#2 p=5/1 0.652/0.627；西史高中「歷史課程及評估指引 中四至中六」#2/#3 p=1/25。

結構 no-op 不索引 catalogue 導航文字 = 刻意避 Channel B noise（catalogue 內容已被 children page-carried 覆蓋）。**Phase 3 (a/b/c) 全力完成。Supabase 9,838→9,849。**

### Sources changed

- `dev/source/source_registry.json`（history_jss_2019 + edbc197_2024_ph_pri：url_primary→直連PDF / source_type html→pdf / notes / last_checked）
- `dev/vault/repage_pdfs.py`（PILOT_LEGACY + PILOT_OUT history_jss_2019 entry）
- `dev/vault/history_jss_2019/extract_history_jss_2019_repaged.txt`（NEW，118p page-carried；stub seed 已 backup→`dev/init_backup/20260530_161915_UTC/`+removed）
- `dev/vault/edbc197_2024_ph_pri/extract_edbc197_2024_ph_pri_repaged.txt`（NEW Phase 3c，11p page-carried；stub seed backup+removed）
- `dev/vault/stat_edb_figures/extract_stat_edb_figures.txt`（Phase 3c mojibake fix；§5.a backup `dev/init_backup/20260530_171517_UTC_phase3c/`）
- `dev/vault/repage_pdfs.py`（history_jss_2019 + edbc197_2024_ph_pri PILOT_LEGACY/OUT entries）
- `backend/src/api/searchChannelB.ts`（`SOURCE_SETS.curriculum` +history_jss_2019 +history_sss_2007_2015 +edbc197_2024_ph_pri）
- Supabase wiki_chunks（history_jss del=0 ins=125 → 9,838；edbc197 del=0 ins=12；stat_edb_figures del=2 ins=1 → **9,849**）+ wiki_index.json（gitignored，→13042）
- commit chain `ceb7c91`（history backfill）→`60dc174`（PERSIST）→`5d0d002`（Phase 3c）+ 本 PERSIST commit
- **NOT modified:** knowledge.json / guidelines.json / app.html / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### DOC_SYNC Matrix Scan

| Change Category | Required Doc Updates | Status |
|---|---|---|
| New source backfill ×2 (history_jss_2019 + edbc197) data+registry+vault | SESSION_HANDOFF baseline (9,849 / 102 marker-bearing) + SESSION_LOG | ✓ Done |
| Backend behavior change (allowlist ×3) + Render deploy | SESSION_HANDOFF Last Record + SESSION_LOG; live verify ×4 | ✓ Done (deploy verified) |
| Vault content fix (stat_edb_figures mojibake) | SESSION_LOG Phase 3c + SESSION_HANDOFF baseline | ✓ Done |
| New process lesson (backfill-allowlist coupling) | SESSION_LOG Lessons + SESSION_HANDOFF caution; PMS §8b promote deferred | ✓ Done (monitoring tier) |
| External service (Supabase chunks / EDB fetch) | CODEBASE_CONTEXT — no schema/endpoint change (chunk count only) | N/A |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135 證實 EDB + onrender egress 均通 — handoff 舊「EDB 去唔到」假設已過時，仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S135 (2026-05-30, Leonard /goal「Phase 3 全力完成」)：**Phase 3 (a/b/c) 全部完成**。HEAD origin/main = `9434581`（S135 PERSIST）← `5d0d002`（Phase 3c）← `60dc174`（PERSIST）← `ceb7c91`（history backfill）。

S135 做咗：(1) Phase 3a #3 — geog/pe/dat/ict/music_sss 5 cluster 4-step diagnostic 全 healthy no-op；(2) **history_jss_2019 西史初中 backfill** del=0 ins=125（§E.12 EDB URL re-discovery：原直連失效 → catalogue 解析搵返 rename 後 PDF）；(3) **Phase 3c** — edbc197_2024_ph_pri 通函 backfill del=0 ins=12（同 §E.12 pattern）+ stat_edb_figures mojibake fix del=2 ins=1 + arts_curr_docs/moral_civic_curr/ph_pri_curr 結構 no-op（children 全索引）；(4) allowlist parity — `SOURCE_SETS.curriculum` 加 history_jss_2019 + history_sss_2007_2015（西史高中）+ edbc197_2024_ph_pri。全部 Render deploy live verified。

⚠️ KEY LESSON S135 (§8 monitoring, §8b 候選): **backfill-allowlist coupling** — 把新源 page-carry 入 Supabase 唔會自動 surface；topic-routed category 受 backend `SOURCE_SETS` allowlist gate，新源必須同時加 allowlist + redeploy 先 surface。**Future 任何新源 backfill 必檢查/更新 SOURCE_SETS。** 另 §E.12 EDB URL churn：直連 PDF rename 後可由 catalogue page 解析搵返（「直連失效」≠ 文件消失）。

Current objective and progress state:
- Baseline: Supabase **9,849** / 102 marker-bearing / CB-3 final ceiling ~88% / brand live (policychecker.wongfu.net)
- **Phase 3 (a/b/c) 全部完成**；driver cb3_b2 13 輪 0 incident（含 S135 全新源 path ×2 + mojibake re-index ×1）
- 下一階段方向未定，待 Leonard

Pending tasks in priority order:
1. **下一階段方向待 Leonard 揀**：Q4 對外契約收斂（deferred、未明示勿掂）/ §8b rule 2 semantic-supersede automation tooling / Mobile UI P2 / 39→148 guidelines 擴展 / 既有 deferred backlog
2. **既有 deferred backlog**：§E.10 (a) admin-login client-side gate（ACCEPTED conditional）/ 57014 transient（retry 即恢復、S135 又遇 2 次）/ FAIL-A 注入 regression（record-only）/ stat_fact 升 2025/26（ROI≈0）
3. **§8b promote 評估**：backfill-allowlist coupling（S135）+ 429-masquerade（S134）兩個 monitoring-tier lesson，若 recurrence 即 promote 入 PMS §G.2/§8b

Key files changed this session:
- `dev/source/source_registry.json`（history_jss_2019 + edbc197_2024_ph_pri：url_primary→直連PDF / source_type→pdf）
- `dev/vault/history_jss_2019/` + `dev/vault/edbc197_2024_ph_pri/`（NEW repaged extracts，page-carried）
- `dev/vault/stat_edb_figures/extract_stat_edb_figures.txt`（mojibake fix）
- `dev/vault/repage_pdfs.py`（2 新源 PILOT_LEGACY/OUT entries）
- `backend/src/api/searchChannelB.ts`（SOURCE_SETS.curriculum +3 entries）
- Supabase wiki_chunks（9,713→9,849）；dev/SESSION_HANDOFF.md + dev/SESSION_LOG.md

Known risks / blockers / cautions:
- 0 new product risks（2 backfill 純新增可逆 + mojibake fix 淨改善）
- NEW caution: backfill-allowlist coupling（新源入庫 ≠ 自動 surface，必加 SOURCE_SETS）
- 既有不變: 🔴 57014 transient (retry); FAIL-A (record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB code path dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG

Validation status:
- PASS: build/typecheck exit 0；Supabase per-source verify（history del=0 ins=125 / edbc197 del=0 ins=12 / stat del=2 ins=1）；4 條 live deploy smoke（帶頁碼）
- COMMITTED: `ceb7c91`→`60dc174`→`5d0d002`→`9434581` origin/main, tree clean
- OPEN: 下一階段方向待 Leonard

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD = 9434581 / knowledge.json._meta.stats facts:455 / Supabase 9,849 / egress onrender /health warm 455）後，**Phase 3 已全力完成、無 pending 執行**。第一件事＝問 Leonard 下一階段方向（Q4 契約未明示勿掂 / §8b automation / Mobile UI P2 / 39→148 / 既有 backlog）。未 Leonard 明示前唔好自行 resume / 掂 Q4 契約 / reopen §E.10 / 動 Stage-2。
```
