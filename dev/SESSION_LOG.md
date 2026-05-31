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

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135/S136 證實 EDB + onrender egress 均通 — handoff 舊「EDB 去唔到」假設已過時，仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S136 (2026-05-31)：**Mobile UI Phase 2 完成 — app.html#guidelines（文件庫）專用 mobile render**。Channel B 經確認已到設計天花板（CB-3 ~88% final ceiling、剩 ~12% = 4 HTML + 5 xlsx 結構性硬限、不可再升）。HEAD origin/main = <S136 PERSIST commit>（起手自行 verify）。

S136 做咗 **A. Mobile UI Phase 2**（3 檔，純前端、mobile-only、desktop 已驗證不受影響）：(1) `app.html` +9 暴露 `window.GUIDELINES_REGISTRY`(148) + `dispatchEvent('k1-registry-ready')`；(2) `mobile.js` 新 `buildGuidelinesShell()`（分類/階段 chips + 排序 + 搜尋 + 文件卡 tap→EDB，鏡像桌面 GuidelinesPanel）+ guidelines 分支 event-driven build + hashchange→reload；(3) `mobile.css` `.m-guide-*` 樣式。修咗一個 TDZ bug（eager init-trigger 早過 const → 搬去 IIFE 尾）。Live-preview 6 scenario + desktop no-op + search-shell regression 全 PASS。

S136 **B. CORS incident 修復**（Leonard 真機驗 Mobile 後揪出）：Channel B 政策搜尋喺 `policychecker.wongfu.net` 出「搜尋服務暫未連線」。Root cause = Render env var `CORS_ORIGIN` 覆蓋源碼 default、缺品牌域名 → ACAO 回 github.io → 瀏覽器擋。**Latent 自 S132 brand launch**（一直用 github.io origin 測試而漏咗）。Fix = `backend/src/config/env.ts` `getCorsOrigins()` union `BASELINE_CORS_ORIGINS`(github.io + policychecker) + env → 漏 env var 都無法再令品牌域名離線。commit `59494fa` push → Render redeploy → 端到端 `Origin: policychecker` POST = HTTP 200 + ACAO match ✅。**遺留（獨立未修）:**「sen」短 query relevance 差 + `phys_sss_2007_2015` 源 mojibake 亂碼（資料質素 backlog）。

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
- `app.html`（暴露 GUIDELINES_REGISTRY + dispatch event）
- `mobile.js`（buildGuidelinesShell + guidelines 分支 event-driven + init-trigger 搬尾修 TDZ + hashchange→reload）
- `mobile.css`（.m-guide-* 樣式）
- `backend/src/config/env.ts`（CORS hardening：BASELINE_CORS_ORIGINS union）
- dev/SESSION_HANDOFF.md + dev/SESSION_LOG.md

Known risks / blockers / cautions:
- **CORS 已修（commit `59494fa`、live verified）**；first-party 品牌 origin 現 code-baseline。Render env var `CORS_ORIGIN` 可繼續 ADD 其他 origin（如學校 iframe host）但唔再能令品牌域名離線。
- 🔴 **NEW 資料質素**：`phys_sss_2007_2015` mojibake 亂碼 surface（user-facing；待修）+ 短英文 query relevance 差。
- 既有不變: 🔴 57014 transient (retry); FAIL-A (record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB code path dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG
- mobile.js 教訓：任何新 module const 喺 init 路徑用到，必確保 eager init-trigger 喺其後（已搬 IIFE 尾、現安全）

Validation status:
- PASS: Mobile UI — `node --check mobile.js` exit 0；live preview 6 §3d scenario + desktop no-op + search-shell regression 全 PASS（375px + 1280px real-engine）
- PASS: CORS fix — `npm run check`/`build` exit 0；node 3-scenario union 驗；live ACAO 端到端確認 `policychecker` allowed + Channel B「sen」HTTP 200
- COMMITTED: Mobile `0c2e201` + PERSIST `664ecdb` + CORS `59494fa` origin/main（起手自行 verify HEAD），tree clean
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

## 2026-05-30 Session 134 — Phase 3a #2 batch diagnostic = 5 sources no-op (429-masquerade-as-data near-miss)

- **ID:** Claude_20260530_1500
- **Trigger:** Leonard 起手 `/goal 1` 揀 Phase 3a #2 source case-by-case → 跑 5 候選 (tech_kla / chi_hist / ls_jss / arts / econ) 4-step diagnostic → 中途揀「行 ls_jss page-carry」→ 數據修正後 page-carry 撤回 → 全部「No-op + 文檔化 收尾」
- **§3 Risk:** Diagnostic READ-only = LOW；remediation (rejected) HIGH backend routing；ls_jss page-carry (rejected after data correction) = HIGH **避免咗**

### Diagnostic data (read-only：live onrender `/api/search/channel-b` + Supabase service-role REST count)

Supabase grand total = **9,713** (對齊 baseline)。Per-source chunk count（真實值，已濾走 429）：

| Cluster | Chunk counts | Live smoke 結論 |
|---|---|---|
| tech_kla | tech_kla_guide_2017 **237** / ict_2021 81 / ict_2007 135 / dat_2007 103 / ct_prog 10 / dat_supp 5 = **571** (5.88%) | 資訊/設計/編程 query → 對應 specific source + 頁碼正確；廣義「科技教育課程指引」semantic 撞 ma_kla/pri_science（非 top-1 wrong-domain）|
| chi_hist | chi_hist_jss_2019 **111** / sss 166 / ncs 25 / bilingual 33；history_sss 155；**history_jss_2019 = 0**（西史初中未入庫，獨立 gap）| 中史 query → chi_hist_jss_2019 top-3 p=8/1/29，零西史污染 |
| ls_jss | ls_jss_2010 = **251** | 「生活與社會中一至中三」→ ls_jss top-3 **p=78/8/76**；「生活與社會課程指引」→ 較新人文科 ph_pri_guide_2025 上（合理 supersede）|
| arts | arts_kla_guide_2017 **116** / music_p1_s6 85 / va_p1_s6 71 / music_sss_2024 69 / music_sss_2015 129 / va_sss_2015 144 = **617** | 「藝術教育學習領域課程指引」→ music_p1_s6_2024 #1 / va_p1_s6 #2-4 / pe_kla #5；**arts_kla_guide_2017 跌出 top-5** |
| econ | econ_2025 87 / supp_2025 32 / econ_2007 112 / supp_2015 31 = **262** | 限速截斷未完整 smoke；counts 確認 2025 版已入庫；pre-throttle partial 顯示最新版 dominate |

### CRITICAL CORRECTION — 429 masquerade-as-data near-miss

- 初步診斷以 ls_jss = **24 chunks / 0 pages** → 推「page-carry 需要」→ Leonard 授權執行。**呢個結論係錯。**
- 真相：HTTP **429 (onrender 10 req/min/IP + Supabase free-tier throttle)** 被我 diagnostic script 把錯誤 response 印成 `0` / `ERR` / 空白頁；加上 harness 把大批 parallel call buffer 後一次過 flush，造成「工具壞咗」嘅錯覺。**工具一直正常。**
- 正確：ls_jss_2010 = **251 chunks、已 page-carried**、live smoke top-3 帶頁碼。**page-carry 完全唔使做。**
- **因 STOP 咗冇執行** → 避免咗對**已經正確**嘅數據跑一次冇必要嘅破壞性 Supabase DELETE/INSERT mutation。

### Classification — all 5 = no-op (Leonard 揀)

- tech_kla / chi_hist / ls_jss / econ = **healthy**（topical query 正確 surface + 頁碼；data 充足）
- arts = **輕微 ranking 競爭**（arts_kla_guide_2017 完整書名 query 被較新 2024 音樂/視藝分科指引壓出 top-5，同 S122/S123 music_sss_2024 KLA-vs-分科 pattern 一致）→ Leonard 裁示視為**可接受 newer-guide-優先**、no-op（強推 arts_kla 上反而壓低更有用嘅分科指引，同 g29 quota-cap 反效果同理）
- Phase 3a #2 清單 5 源全 close as false-alarm/no-op

### Lessons

- **§G.2 verify-don't-trust 延伸（5th-instance candidate）**：Throttled/rate-limited API response 會**偽裝成數據**（0 count / 空白頁 / ERR），導致假「需要修」結論。Diagnostic script 必須 distinguish HTTP 429/error vs 真 0；live smoke 對 onrender 要 pacing（10 req/min/IP）。§8 monitoring tier — near-miss 非 incident、未升 SOP（promote 入 PMS §G.2 banner 留下次評估）。
- 「Ranking competition」listed-in-backlog 多源自 S122-S125 generic batch-smoke 非-surface 觀察；topical query 一驗即知 4/5 健康（同 g29/S133 meta-lesson 一致）。

### Sources changed in this session

- `dev/SESSION_HANDOFF.md`（Open Priority #1 Phase 3a #2 5 源剔走 + ✅ S134 entry + Last/Previous demote）
- `dev/SESSION_LOG.md`（本 S134 entry prepend）
- temp diagnostic helpers（`dev/_phase3a_smoke.py` / `dev/_phase3a_count.py` / `dev/_dump.py` / `dev/_dump2.py`）已刪
- **NOT modified:** code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### DOC_SYNC Matrix Scan

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Phase 3a diagnostic finding (no-op closure ×5) | SESSION_HANDOFF Open Priority #1 + ✅ S134 entry | ✓ Done |
| Session history | SESSION_LOG S134 entry | ✓ Done |
| New process lesson (429-masquerade) | SESSION_LOG Lessons + handoff caution; PMS §G.2 promote deferred | ✓ Done (monitoring tier) |
| No code / data / config / external service change | (no doc impact) | N/A |

(Registry `dev/DOC_SYNC_CHECKLIST.md` not consulted directly — pure read-only diagnostic finding closure, no governance-doc category row applies beyond §4 PERSIST baseline.)

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S134 (2026-05-30, Leonard /goal 1 揀 Phase 3a #2 → 跑 5 源 4-step diagnostic → 全部 No-op + 文檔化 收尾)：**Phase 3a #2 batch (tech_kla / chi_hist / ls_jss / arts / econ) = 5 源全 no-op, 0 code/data/Supabase mutation**。

⚠️ KEY LESSON S134 (§G.2 延伸): 診斷中途因 HTTP 429 (onrender 10 req/min + Supabase throttle) 被 script 印成 0/ERR/空白頁 → 誤判 ls_jss = 24 chunks/0 pages 需要 page-carry。STOP 後修正：ls_jss 真實 = 251 chunks 已 page-carried、healthy。**Throttled API response 會偽裝成數據；live smoke 必須 pace (10 req/min) + distinguish 429 vs 真 0。** 差啲對正確數據跑冇必要破壞性 Supabase mutation。

Diagnostic 真實數據 (429 已濾): tech_kla cluster 571 (tech_kla 237) / chi_hist 中史 277 (history_jss_2019=0 西史初中 gap) / ls_jss 251 page-carried / arts cluster 617 (arts_kla 116) / econ 2025版 119+舊143。Live smoke: 4/5 topical query 正確 surface + 頁碼。

Classification: tech_kla/chi_hist/ls_jss/econ = healthy no-op；arts = 輕微 ranking 競爭 (arts_kla_guide_2017 完整書名被 2024 分科音樂/視藝指引壓出 top-5)，Leonard 裁示視為可接受 newer-guide-優先 no-op (強推反壓低有用分科指引，同 g29 quota-cap 反效果同理)。

Current objective and progress state:
- Baseline unchanged: Supabase 9,713 / 100/113 marker-bearing / CB-3 final ceiling ~88% / brand launch live (policychecker.wongfu.net)
- S134 = pure governance doc update, 0 code/data/Supabase mutation
- Phase 3a 清單剩 ~9-12 sources (5 源再剔走)

Pending tasks in priority order:
1. **Phase 3a #3 剩餘源 case-by-case** (geog / history_jss_2019=0 西史初中 coverage gap / dat / ict / pe / music_sss / 等)。沿用 S133 4-step diagnostic template + S134 教訓 (pace live smoke、429 vs 真 0)。Each source individual judgment。注意 history_jss_2019=0 chunks = 真 coverage gap (非 ranking)。
2. **Phase 3c 5 HTML catalogue-level refresh (low ROI)**: stat_edb_figures / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr。結構天花板。
3. **既有 deferred backlog**: §E.10 conditional ACCEPTED / 57014 transient / FAIL-A record-only / P2/P3 (39→148) / Mobile UI P2 / HKEAA / stat_fact upgrade (deprioritized)
4. **Q4 對外契約收斂** (deferred; 未明示勿掂)
5. **§8b rule 2 automation tooling** (future) + **PMS §G.2 5th-instance (429-masquerade) promote 評估**

Key files changed this session:
- `dev/SESSION_HANDOFF.md` (Open Priority #1 5 源剔走 + ✅ S134 + Last/Previous demote)
- `dev/SESSION_LOG.md` (S134 entry prepend + 4-step diagnostic + 429 correction + verbatim handoff)
- temp diagnostic helpers 已刪
- **NOT modified**: 任何 code / data / Supabase / source_registry / knowledge.json / app.html / backend / PMS / CODEBASE_CONTEXT

Known risks / blockers / cautions:
- 0 new product risks (diagnostic-only session)
- NEW process caution: onrender backend 10 req/min/IP rate limit + Supabase free-tier throttle → diagnostic live smoke 必須 pace + 處理 429（勿當數據）
- 既有 risks 不變: 🔴 Supabase 57014 transient (retry); FAIL-A 注入 regression (record-only); §E.10 (a) ACCEPTED conditional; q.html/A·AB code path/backend dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活
- egress 每次自測; EDB PDF `url_primary` (§E.12); 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG (本 session 0 code/data 改、僅 2 governance doc)

Validation status:
- PASS S134 §3d diagnostic scenarios (chunk count via service-role REST / live smoke 4/5 topical queries 正確 + 頁碼 / 429 correction verified)
- COMMIT: S134 doc commit pending (起手自行 verify HEAD)
- OPEN: Phase 3a #3 剩餘源 / 3c / 既有 deferred backlog

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測 (git HEAD / knowledge.json._meta.stats facts:455 / Supabase 9,713 / egress onrender /health warm 455) 後，**S134 Phase 3a #2 batch 5 源 no-op closed**。第一件事＝問 Leonard 揀: (a) **Phase 3a #3 剩餘源** (geog / history_jss gap / dat / ict / pe / music_sss — 4-step diagnostic + pace live smoke 防 429); (b) **Phase 3c 5 HTML refresh** (low ROI); (c) **既有 deferred backlog**; (d) **Q4 契約** (未明示勿掂); (e) 收工？未 Leonard 明示前**唔好自行 resume / 掂 Q4 契約 / reopen §E.10**。
```

---

## 2026-05-28 Session 133 — Phase 3a #1 g29 dominance diagnostic = false-alarm (data scarcity, no-op)

- **ID:** Claude_20260528_1339
- **Trigger:** Leonard 起手揀 Phase 3a batch ranking polish → 揀第一個 target = g29 KGECG-TC-2017 dominance → 提出 hypothesis「可能本身有關幼稚園的資料就不多」→ empirical verify
- **§3 Risk:** Diagnostic READ-only = LOW; if remediation applied → HIGH (backend routing). Leonard 揀「No-op + 文檔化」→ 全程 LOW (doc-only)

### Diagnostic data (3 tasks, all read-only)

- **Task #1 — Inventory (source_registry):** 151 total → KG-related 4 sources only: `g29` 幼稚園教育課程指引 2017 主框架 / `g25` 幼稚園相關指引及須知 / `g26` 2026/27 收生安排 / `stat_kg` 統計數字 (Channel B filter `content_type!=="stat_fact"` 排除). **User-facing 只 3 個 KG sources.**
- **Task #2 — Supabase chunk count per KG source:** g29=**107** / g26=19 / g25=1 / stat_kg=8. KG user-facing total = **127 chunks**. g29 占 KG 庫 **84.3%**. KG 占全 Supabase 9,713 = **1.3%**.
- **Task #3 — Live smoke 5 KG queries via `/api/search/channel-b`** (top-5 distribution):

  | Query | Top-1~5 source distribution | g29 in top-5 | 評估 |
  |---|---|---|---|
  | 幼稚園課程框架 | g29 / g29 / g29 / pri_curr_guide_2024 / music_p1_s6_2024 | 3/5 | ✅ 合理（課程框架=g29 核心 topic）|
  | 幼稚園收生 | g26 / g26 / g26 / — / — | 0/3 | ✅ g26 正確 dominate；g29 不沾邊 |
  | 幼稚園評估 | g29 / pri_curr_guide_2024 / g29 / g29 / va_p1_s6_2024 | 3/5 | ✅ g29 合理（評估=g29 ch.4 內容）|
  | 幼稚園教師專業發展 | g06 / role_facts_hr / g06 / g06 / sag_2025_11 | **0/5** | ✅ CPD 領域 g06 正確；g29 完全 yield |
  | 幼稚園教學語言 | g29 / g29 / g29 / chi_pri_guide_2023 / chi_pri_guide_2023 | 3/5 | ✅ g29 合理（教學語言=g29 內容）|

### Diagnostic conclusion

- **Root cause = (b) data scarcity reflection** — KG domain 結構性內容貧瘠（only 3 user-facing sources, 127 chunks），g29 結構性 own 84% 嘅 KG content
- **NOT (a) ranking bug** — g29 唔係盲目 dominate: admission queries g26 上、CPD queries g06 上、g29 完全 yield；只喺 curriculum/teaching/assessment 即 g29 核心 topic 上 dominate（合理）
- **Cross-domain contamination** 次要觀察: `pri_curr_guide_2024` / `music_p1_s6_2024` / `va_p1_s6_2024` 喺 KG queries surface top-4/5 — embedding semantic similarity，唔搶 top-1~3、user-visible harm 微

### Fix decision (Leonard 揀)

- **No-op + 文檔化** — 0 code/data/Supabase mutation
- Rationale: quota cap 會將 g29 從 top-5 踢走、留空位俾跨域非-KG sources surface，反而傷北極星 traceability。**唯一相關 KG 主文件被搶位 = 比 g29 結構性 dominate 更差**
- Phase 3a #1 closed as false-alarm

### Lessons (§G.2 verify-don't-trust hypothesis 再應用)

- 「Dominance」唔等於「Ranking bug」— 必須 first 量 inventory + chunk count + live smoke 確認 alternative source 存在與否
- Future Phase 3a sources 診斷模板：(1) registry inventory (2) Supabase chunk distribution (3) live smoke 4-5 representative queries (4) judge root cause class
- 適用 §8 monitoring tier — 此次 false-alarm 唔升 SOP，但記錄入 process knowledge

### Sources changed in this session

- `dev/SESSION_HANDOFF.md` (Open Priority #1 g29 剔走 + ✅ S133 完成 entry prepend)
- `dev/SESSION_LOG.md` (本 S133 entry prepend)
- **NOT modified:** code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### DOC_SYNC Matrix Scan

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Phase 3a diagnostic finding (false-alarm closure) | SESSION_HANDOFF Open Priority #1 + ✅ S133 entry | ✓ Done |
| Session history | SESSION_LOG S133 entry | ✓ Done |
| No code / data / config / external service change | (no doc impact) | N/A |

(Registry `dev/DOC_SYNC_CHECKLIST.md` not consulted directly — no governance-doc category rows match a pure read-only diagnostic finding closure. Doc updates above are §4 PERSIST baseline minimum.)

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S133 (2026-05-28, Leonard 起手揀 Phase 3a #1 g29 dominance → 提出 hypothesis「幼稚園資料本身少」→ empirical verify → no-op + 文檔化 → 收工)：**Phase 3a #1 g29 dominance diagnostic = false-alarm, no code/data/Supabase mutation**。HEAD origin/main = `8d9aa54` (S133 closeout)。

Diagnostic data (4-step read-only template, future Phase 3a 沿用):
1. Registry inventory: 151 sources → 4 KG-related (g29 / g25 / g26 / stat_kg), user-facing 只 3 (stat_kg `content_type=stat_fact` 被 Channel B filter 排除)
2. Supabase chunk count per KG source: g29=**107** (KG 庫 84.3%) / g26=19 / g25=1 / stat_kg=8；KG user-facing total 127 = 全庫 9,713 之 **1.3%**
3. Live smoke 5 queries top-5: 幼稚園收生→g26 #1+#2+#3 (g29 完全不出) / 幼稚園教師專業發展→g06 #1+#3+#4 (g29 完全 yield) / 幼稚園課程框架/評估/教學語言→g29 dominate (合理、g29 核心 topic)
4. Classification: **(b) data scarcity NOT (a) ranking bug**

Fix decision per Leonard: **No-op + 文檔化**。Rationale: quota cap 會將 g29 從 top-5 踢走、留空位俾跨域非-KG sources surface，反而傷北極星 traceability（唯一相關 KG 主文件被搶位 = 比結構性 dominate 更差）。Phase 3a #1 closed as false-alarm。

Lesson (§G.2 verify-don't-trust hypothesis 再應用): 「Dominance」 ≠「Ranking bug」— 必先量 inventory + chunk count + live smoke 確認 alternative source 存在與否。Future Phase 3a 沿用 4-step diagnostic 模板。§8 monitoring tier, 未升 SOP。

Current objective and progress state:
- S132 base unchanged: Supabase 9,713 / 100/113 marker-bearing / CB-3 final ceiling ~88% / brand launch live (policychecker.wongfu.net)
- S133 = pure governance doc update, 0 code/data/Supabase mutation
- Phase 3a 清單剩 ~14-17 sources (g29 剔走)

Pending tasks in priority order:
1. **Phase 3a #2 source case-by-case**: tech_kla / chi_hist / ls_jss / arts ranking competition / econ_sss_supp competition / 等。Future sources 沿用 S133 4-step diagnostic template。Each source needs individual judgment (dedicated route / query expansion / per-source quota / OR no-op if data-scarcity-confirmed)。
2. **Phase 3c 5 HTML catalogue-level refresh (low ROI)**: stat_edb_figures (vault mojibake) / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr。結構天花板。
3. **既有 deferred backlog**: §E.10 conditional ACCEPTED / 57014 transient / FAIL-A record-only / P2/P3 (39→148) / Mobile UI P2 / HKEAA / stat_fact upgrade (deprioritized)
4. **Q4 對外契約收斂** (deferred; 未明示勿掂)
5. **§8b rule 2 automation tooling** (future; KLA-title embedding similarity check sub-agent prompt)

Key files changed this session:
- `dev/SESSION_HANDOFF.md` (Open Priority #1 g29 剔走 + ✅ S133 prepend + Last/Previous demote)
- `dev/SESSION_LOG.md` (S133 entry prepend with 4-step diagnostic + DOC_SYNC + verbatim handoff)
- **NOT modified**: 任何 code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT (read-only diagnostic only)

Known risks / blockers / cautions:
- 0 new risks (diagnostic-only session)
- 既有 risks 不變: 🔴 Supabase free-tier 57014 transient (retry 即恢復); FAIL-A 注入 regression (record-only); §3c FAIL-A/B record-only; §E.10 (a) ACCEPTED conditional on cosmetic-gate design unchanged; q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活
- egress 每次自測; EDB PDF 永遠用 `url_primary` (§E.12); 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG (本 session 0 code/data 改、僅 2 governance doc)

Validation status:
- PASS S133 §3d 3 scenarios (inventory query / Supabase count query / live smoke 5 queries)
- COMMITTED: S133 doc commit `8d9aa54` (origin/main advanced from `93a3b74`)
- OPEN: Phase 3a #2 / 3c / 既有 deferred backlog

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測 (git HEAD 對齊 SESSION_HANDOFF Last entry / knowledge.json._meta.stats facts:455 / Supabase chunk count = 9,713 / egress onrender /health warm 455) 後，**S133 Phase 3a #1 g29 false-alarm closed**。第一件事＝問 Leonard 揀: (a) **Phase 3a #2 source** (tech_kla / chi_hist / ls_jss / arts / econ_sss_supp — case-by-case 4-step diagnostic); (b) **Phase 3c 5 HTML catalogue-level refresh** (low ROI); (c) **既有 deferred backlog**; (d) **Q4 對外契約收斂** (未明示勿掂); (e) 收工？未 Leonard 明示前**唔好自行 resume / 掂 Q4 契約 / reopen §E.10**。
```

---
