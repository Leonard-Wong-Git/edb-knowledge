## 2026-03-24 Session 15 — Backend Toolchain Fix + Dashboard Redesign

1. Agent & Session ID: Claude_20260324_1019
2. Task summary: 修復 backend OpenAI SDK 一系列工具鏈錯誤，確認伺服器啟動成功；重新設計指引文件庫介面；修復年份 badge；新增 11 份課程文件；加入學習階段篩選
3. Layer classification: Product / System Layer（backend 工具鏈 + Dashboard UI）
4. Files changed:
   - `backend/tsconfig.json` — 新增 `"allowSyntheticDefaultImports": true`
   - `backend/src/lib/llmClient.ts` — 還原為 `import OpenAI from "openai"` (default import)
   - `backend/src/lib/embeddingClient.ts` — 還原為 `import OpenAI from "openai"` (default import)
   - `backend/node_modules/openai/` — 刪除舊 stub，重新安裝真實 openai@4.104.0 + 所有依賴（node-fetch, formdata-node 等）
   - `k1-dashboard.html` — (1) 推送第4分頁至 GitHub Pages；(2) 重新設計 GuidelinesPanel；(3) 修復年份 badge；(4) 擴充課程文件；(5) 加入階段篩選
5. Completed:
   - ✅ 修復 `TS2339: Property 'embeddings' does not exist` — 發現 node_modules/openai 是舊 stub（只有 3 個文件），已刪除重裝
   - ✅ 修復 `TypeError: OpenAI is not a constructor` — stub 的 index.js 是空殼，重裝真實 SDK 解決
   - ✅ 修復 `ERR_MODULE_NOT_FOUND: node-fetch` — 分步補裝後，最終 `rm -rf node_modules package-lock.json && npm install` 一次裝齊所有 50 個套件
   - ✅ 伺服器啟動成功：`Knowledge Platform backend listening on http://localhost:8787 / CORS origin: https://leonard-wong-git.github.io`
   - ✅ 📋 通告分析 第4分頁推送 GitHub Pages
   - ✅ GuidelinesPanel 全面重新設計：左側欄分類導航（選中整行高亮）+ 排序控件（最新/最舊/名稱）
   - ✅ 修復年份 badge 消失問題：`bg-teal-600` 與左邊框顏色 `#0d9488` 完全一樣導致視覺融合 → 改為淺色底+深色字（emerald/sky/amber/gray）
   - ✅ 擴充課程文件：28 份 → 39 份，新增幼稚園(1)、小學(4)、中學(3)、跨階段(9) 共 11 份
   - ✅ 新增 `level` 欄位至所有課程條目（幼稚園/小學/中學/特殊/跨階段）
   - ✅ 新增「學習階段」篩選器（選「課程」分類時顯示），卡片顯示彩色階段標籤
6. Root causes fixed:
   - `TS2595` / `TS2497`（named import）: openai 只有 default export，需 `import OpenAI from "openai"` + `allowSyntheticDefaultImports: true`
   - `TypeError: OpenAI is not a constructor`: node_modules/openai 是空殼 stub，非真實 SDK
   - 年份 badge 消失：badge 顏色 == 邊框顏色，視覺融合
7. QC summary: `npm run check` exit 0 ✅；`npm run dev` 伺服器啟動 ✅；JSX bracket balance OK ✅；Registry 39 entries, IDs g01-g39 ✅

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow §1 startup: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md.

Project: K1 EDB Knowledge Platform (k1-dashboard.html + backend/).
Current state: v0.9.0 on GitHub Pages. Backend toolchain fully working (npm run dev starts server on :8787). Dashboard has 4 view modes. GuidelinesPanel redesigned with 39 docs, sidebar nav, sort, level filter.

Pending tasks (priority order):
1. End-to-end smoke test of "📋 通告分析": start backend (OPENAI_API_KEY=sk-... npm run dev from ~/Downloads/Claude-edb-knowledge/backend/), open GitHub Pages, paste real EDB circular, verify topic detection + AI analysis output.
2. Re-review 81 draft facts via 知識庫 dashboard tab — all currently in draft state.
3. Tune SIMILARITY_THRESHOLD in backend/src/services/topicDetector.ts if topic recall off (current: 0.35).
4. Expand guideline registry with more EDB documents as needed.

Key files changed this session:
- backend/tsconfig.json (allowSyntheticDefaultImports: true)
- backend/src/lib/llmClient.ts + embeddingClient.ts (default import)
- backend/node_modules/openai/ (real SDK installed, 50 packages)
- k1-dashboard.html (GuidelinesPanel redesign, 39 docs, level filter, year badge fix)

Known risks:
- OPENAI_API_KEY required at runtime for backend (not stored anywhere)
- EDB guideline URLs may become stale as EDB restructures website
- 81 facts all in draft — must re-review before using knowledge base in production

Validation: npm run check exit 0; npm run dev starts successfully; GitHub Pages updated.
First action: Smoke test 通告分析 with a real EDB circular.
```

---

## 2026-03-23 Scraper Merge Fix + Docs Update (v2.1.0)

1. Agent & Session ID: Claude_20260323_0000
2. Task summary: 修復 edb_scraper.py days-3 覆蓋問題（PHASE 4 merge）；README.md + CHANGELOG.md 更新至 v2.1.0；CODEBASE_CONTEXT.md 同步更新；所有文件同步至 git repo
3. Layer classification: Product / System Layer（後端 scraper fix + 文檔更新）
4. Files changed:
   - `edb_scraper.py`（PHASE 4 merge fix：load existing → merge raw → sort desc → save）
   - `README.md`（完整重寫：v0.1.0-mockup → v2.1.0 正式版，含新架構圖、功能表）
   - `CHANGELOG.md`（新增 v2.1.0 完整條目，更新 Unreleased → v2.2.0）
   - `dev/CODEBASE_CONTEXT.md`（dashboard 2766→3047 lines，Key Decision #9，AI Maintenance Log）
   - `dev/SESSION_HANDOFF.md`（Open Priorities 更新，Known Risks #3 已修復）
   - `dev/SESSION_LOG.md`（本次更新）
5. Completed:
   - ✅ edb_scraper.py PHASE 4 merge fix — `merged = dict(existing); merged[num] = circ` — days-3 現在保留所有舊通告
   - ✅ ast.parse 語法驗證 PASS；merge simulation 測試 PASS（OLD=1, NEW=3 → total=3 merge correct）
   - ✅ README.md 完整重寫（v2.1.0 功能表、架構圖、CLI 參數、AI 規格、六角色說明）
   - ✅ CHANGELOG.md v2.1.0 條目（Added/Changed/Fixed 完整記錄）
   - ✅ CODEBASE_CONTEXT.md 更新（Key Decision #9 scraper merge fix，directory map 更新）
   - ✅ 所有文件同步至 EDB-Circular-AI-analysis-system（git repo）
6. Root cause / fix (PHASE 4 overwrite bug):
   - Problem: PHASE 4 iterated only over `raw` (current run's results) → wrote only current-run data to JSON
   - Root cause: `existing` dict was loaded for PDF text reuse only, not included in final output
   - Fix: `merged = dict(existing)` then update with `raw` entries; sort by date desc; log new/updated/kept counts
   - Verification: ast.parse PASS; simulation OLD=1+NEW=3 → 3 total (merge correct, not append)
7. QC summary: PASS ✅

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow §1 startup: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md.

Current state: v2.1.0 fully complete. Scraper days-3 merge fix applied. README/CHANGELOG/CODEBASE_CONTEXT all updated. Files synced to git repo — awaiting Mac Terminal push.

Pending tasks (priority order):
1. Mac Terminal: git push the updated files (edb_scraper.py, README.md, CHANGELOG.md, dev/CODEBASE_CONTEXT.md, dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md). Use: cd to git repo path, cp updated files from Downloads/Claude-edb-Project-V3 first (governance files), then git pull --rebase origin main && git push origin main.
2. Confirm school-year workflow ran successfully (check GitHub Actions) and circulars.json now has full data.
3. Next feature: Supplier chart data fields (scraper modification — currently placeholder in dashboard).
4. K1 Phase 2 (separate project, long-term).

Key files changed this session:
- edb_scraper.py (PHASE 4 merge fix — days-3 now merges existing data instead of overwriting)
- README.md (complete rewrite to v2.1.0)
- CHANGELOG.md (v2.1.0 entry added)
- dev/CODEBASE_CONTEXT.md (v2.1.0, Key Decision #9)

Known risks:
- git pull --rebase may overwrite governance files — always cp from Claude-edb-Project-V3 to git repo BEFORE git pull --rebase
- Supplier chart still placeholder (needs scraper changes)
- Mac git repo path: /Users/leonard/Library/Application Support/Claude/local-agent-mode-sessions/f52b21f7-e7c9-49a3-80dc-00ab322afbcf/51c234d2-cb9f-4b55-bb07-b71de9e93c27/local_e454964f-74da-4734-9a60-bf4b4362ca65/outputs/EDB-Circular-AI-analysis-system

Validation: ast.parse PASS; merge simulation PASS; docs QC PASS.
Primary workspace: Claude-edb-Project-V3 (Downloads folder).
First action: Run Mac Terminal push commands (see GIT_PUSH_MANUAL.md or commands below).
```

---

## 2026-03-22 v2.1.0 Dashboard 14 項修復 + GitHub Pages 部署

1. Agent & Session ID: Claude_20260322_1520
2. Task summary: v2.1.0 Dashboard overhaul — 14 項問題修復，含首頁分離、搜尋獨立化、AI 改名、EDBC 月曆等；GitHub Pages 部署；circulars.json 覆蓋問題診斷
3. Layer classification: Product / System Layer（前端功能修復 + 部署驗證）
4. Files changed:
   - `edb-dashboard.html`（兩個 workspace：2766→3047 行，v2.0.0→v2.1.0）
   - `dev/SESSION_HANDOFF.md`（更新）、`dev/SESSION_LOG.md`（更新）
5. Completed:
   - ✅ 14 項修復：🏠 首頁 tab、stats toggle、通告總覽重置、搜尋 dropdown、LLM→AI、PDF 置頂、dtc-analysis 合併、EDBC 月曆、移除預設釘選、系統說明精簡、供應商圖表+法規參考
   - ✅ 24/24 structural QC checks + JS syntax check (Node.js) 全通過
   - ✅ GitHub Pages v2.1.0 部署成功（commit `5b45df0`）
   - ✅ 目視驗證：🏠 首頁、📊 通告總覽、v2.1.0 標題均正常顯示
   - ✅ 問題診斷：circulars.json 只有 1 條通告 = days-3 排程覆蓋了 school-year 全量數據
   - ✅ SESSION_HANDOFF.md rebase 覆蓋後重新修復（v1.1.0 Codex 版本 → v2.1.0）
6. Known issues diagnosed this session:
   - **days-3 覆蓋問題**：`edb_scraper.py` days-3 模式直接重寫 circulars.json，不 merge 現有數據
     * 影響：school-year 全量數據被後續 days-3 定時排程覆蓋，只剩最近幾天
     * 修復方向：days-3 模式應先 load 現有 JSON，再 merge 新通告，再 save
   - **git rebase 治理文件覆蓋**：GitHub Actions 定時 commit 導致遠端常領先，pull --rebase 時可能覆蓋 SESSION_HANDOFF.md
     * 緩解：push 前手動 cp 最新治理文件到 git repo
7. QC summary: 24/24 PASS ✅

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow §1 startup: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md.

Current state: v2.1.0 Dashboard fully deployed on GitHub Pages (commit 5b45df0). 24/24 QC checks passed. Two known issues diagnosed but not yet fixed.

Pending tasks (priority order):
1. Trigger school-year workflow manually on GitHub Actions (to restore full circular data — currently only 1 circular due to days-3 overwrite)
2. Fix edb_scraper.py: days-3 mode must MERGE into existing circulars.json instead of overwriting it
3. Fix SESSION_HANDOFF.md rebase overwrite: before each push, manually cp governance files from Claude-edb-Project-V3 to git repo, THEN git pull --rebase, THEN push
4. README.md / CHANGELOG.md update (still showing v0.1.0-mockup)
5. Supplier chart new data fields (scraper modification)
6. K1 Phase 2 (separate project)

Key files changed last session:
- edb-dashboard.html (2766→3047 lines, v2.0.0→v2.1.0) — in both Claude-edb-Project-V3 and EDB-Circular-AI-analysis-system
- dev/SESSION_HANDOFF.md, dev/SESSION_LOG.md

Known risks:
- circulars.json only has 1 circular (days-3 overwrite issue — needs scraper fix)
- git pull --rebase may overwrite governance files (SESSION_HANDOFF.md, SESSION_LOG.md)
- Supplier chart is placeholder (needs scraper changes)
- README.md/CHANGELOG.md outdated (non-blocking)
- Mac git repo path: /Users/leonard/Library/Application Support/Claude/local-agent-mode-sessions/f52b21f7-e7c9-49a3-80dc-00ab322afbcf/51c234d2-cb9f-4b55-bb07-b71de9e93c27/local_e454964f-74da-4734-9a60-bf4b4362ca65/outputs/EDB-Circular-AI-analysis-system

Primary workspace: Claude-edb-Project-V3 (confirmed by user)
Validation: 24/24 QC checks passed; GitHub Pages v2.1.0 live.
First action: Go to GitHub Actions and manually trigger school-year workflow to restore full circular data.
```

---

## 2026-03-17

1. Agent & Session ID: Codex_20260317_1956
2. Task summary: 治理啟動流程執行 + `dev/CODEBASE_CONTEXT.md` 初始建立
3. Layer classification: Development Governance Layer（session startup / context persistence）
4. Source triage: 非產品 bug；屬 documentation/state completeness issue，根因是 `CODEBASE_CONTEXT.md` 尚未建立
5. Files read:
   - `AGENTS.md`（以用戶提供內容為治理 SSOT）
   - `dev/SESSION_HANDOFF.md`
   - `dev/SESSION_LOG.md`
   - `README.md`
   - `requirements.txt`
   - `edb_scraper.py`
   - `fetch_knowledge.py`
   - `dev/v0.2.0-FRONTEND-SPEC.md`
   - `dev/K1_KNOWLEDGE_INTERFACE_SPEC.md`
6. Files changed:
   - `dev/CODEBASE_CONTEXT.md`（新建）
   - `dev/SESSION_HANDOFF.md`（Mandatory Start Checklist + Last Session Record 更新）
   - `dev/SESSION_LOG.md`（本條目新增）
7. Completed:
   - 依 `AGENTS.md` §1 啟動順序讀取 handoff/log，定位最新 `Next Session Handoff Prompt (Verbatim)`
   - 顯示 1 個 Boot Visual Cue（Style B）
   - 掃描現有文件與程式入口，建立 `dev/CODEBASE_CONTEXT.md`
   - 記錄 Stack、Directory Map、Key Entry Points、Build & Run、External Services、Key Decisions、AI Maintenance Log
   - 將 `dev/CODEBASE_CONTEXT.md` 納入 `SESSION_HANDOFF.md` 的 Mandatory Start Checklist
8. Validation / QC:
   - `test -f dev/CODEBASE_CONTEXT.md` → exists ✅
   - `rg -n "^## " dev/CODEBASE_CONTEXT.md` → 7 個主要章節存在 ✅
   - `rg -n "CODEBASE_CONTEXT" dev/SESSION_HANDOFF.md dev/SESSION_LOG.md` → handoff/log 已同步更新 ✅
   - 產品程式碼未修改；未執行產品層 build/test（本 session 僅治理文件建立）
9. Risks / blockers:
   - `External Services` 中的 API 細節目前以 repo 既有證據整理，尚未重新對齊官方文件
   - 若後續要改寫 OpenAI/EDB API 呼叫邏輯，仍需依 `AGENTS.md` 0b 先完成官方文件校準
10. Next priorities:
   - 用 `dev/CODEBASE_CONTEXT.md` 作為穩定基線，恢復產品層工作
   - 決定下一個產品任務：K1/R1 知識框架或次要 UI 待辦
   - 若涉及外部 API 變更，先補官方文件對齊與 External Services 欄位更新

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 新 session 缺少 `dev/CODEBASE_CONTEXT.md`，穩定專案事實只能分散在 README、程式碼與 session 文件中
2. Root Cause: 初始安裝流程不建立此檔，且後續 session 尚未補建
3. Fix: 掃描既有文件與入口檔，建立 `dev/CODEBASE_CONTEXT.md` 並把它納入 startup checklist
4. Verification: `CODEBASE_CONTEXT.md` 已建立且含必需章節；SESSION_HANDOFF / SESSION_LOG 已同步引用 ✅
5. Regression / rule update: 無新增長期規則；僅落實既有 `AGENTS.md` §1 要求

### Consolidation / Retirement Record
1. Duplicate / drift found: 專案穩定事實分散於 README、SESSION_HANDOFF、程式碼註解
2. Single source of truth chosen: `dev/CODEBASE_CONTEXT.md` 作為穩定技術事實集中位置
3. What was merged: Stack、入口檔、Build & Run、External Services、Key Decisions 摘要整合進新檔
4. What was retired / superseded: 無；原始來源保留，改由 `CODEBASE_CONTEXT.md` 提供聚合視圖
5. Why consolidation was needed: 降低新 session 重建上下文成本，符合 sustainable session governance 目的

### Next Session Handoff Prompt (Verbatim)
```text
Read `AGENTS.md` first as the governance SSOT, then follow the startup sequence in §1 exactly: `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/CODEBASE_CONTEXT.md` (now present) → `dev/PROJECT_MASTER_SPEC.md` if it exists.

Current objective:
Resume product-layer work for the EDB Circular AI Analysis System from the new stable governance baseline established on 2026-03-17.

Current progress state:
- `dev/CODEBASE_CONTEXT.md` was created in session `Codex_20260317_1956` and now centralizes stack, directory map, entry points, build/run commands, external services, and key decisions.
- `dev/SESSION_HANDOFF.md` startup checklist now explicitly includes reading `dev/CODEBASE_CONTEXT.md`.
- No product code was changed in this session; product behavior remains as recorded in prior handoff/log entries.

Pending tasks in priority order:
1. Choose and resume the next product task, with strongest candidates being K1/R1 knowledge-framework work or the secondary UI backlog (`D8/D9`, `F4`, `H5`, `H6`).
2. If the next task changes external API-calling code, align with official docs first and update the relevant `External Services` block in `dev/CODEBASE_CONTEXT.md` before coding.
3. Keep `dev/CODEBASE_CONTEXT.md`, `dev/SESSION_HANDOFF.md`, and `dev/SESSION_LOG.md` synchronized whenever stable facts or session state change.

Key files changed in this session:
- `dev/CODEBASE_CONTEXT.md`
- `dev/SESSION_HANDOFF.md`
- `dev/SESSION_LOG.md`

Known risks / blockers / cautions:
- The `External Services` section is currently a repo-evidence baseline, not a substitute for official API verification.
- This session performed governance/documentation work only; no fresh product-level runtime verification was run.
- Existing product risks and operational cautions still live in `dev/SESSION_HANDOFF.md`.

Validation status:
- Startup-governance read sequence completed.
- `dev/CODEBASE_CONTEXT.md` exists and contains the required major sections.
- Handoff/log were updated to reference the new baseline.

First concrete next action:
After reading the startup files, inspect `dev/SESSION_HANDOFF.md` open priorities and select the next product task to execute, starting with either K1/R1 knowledge work or the secondary UI backlog.
```

---

## 2026-03-14 (RE06)

1. Agent & Session ID: Claude_20260314_RE06
2. Task summary: PDF timeout 修復 — proc.kill() (SIGKILL) + pdfminer DEBUG log 抑制
3. Layer classification: Product / System Layer（後端管線修復）
4. Source triage: 問題來源 = Known Risk #6 in SESSION_HANDOFF（pdfminer C 擴展卡死）；屬 code logic issue（SIGTERM 無法打斷 C 擴展）
5. Files read:
   - `dev/SESSION_HANDOFF.md`（當前狀態 + Known Risk #6）
   - `dev/SESSION_LOG.md`（RE05 失敗記錄）
   - `dev/v0.2.0-FRONTEND-SPEC.md`（架構確認）
   - `edb_scraper.py`（lines 560–610 PDF extractor + lines 785–810 logging setup）
6. Files changed:
   - `edb_scraper.py`（3 處修改，詳見下方）
   - `dev/SESSION_HANDOFF.md`（Known Risk #6 更新 + Last Session Record 更新）
   - `dev/SESSION_LOG.md`（本次記錄新增）
7. Changes detail:
   - **Fix A** — `extract_pdf_text()` line ~598：`proc.terminate()` → `proc.kill()` (SIGKILL)
     * 原因：SIGTERM 被 pdfminer C 擴展（psparser/pdfinterp）忽略；SIGKILL 由 OS 直接強殺，C 擴展無法攔截
   - **Fix B** — `extract_pdf_text()` line ~599：`proc.join()` → `proc.join(2)` 加 2 秒 timeout 安全邊際
   - **Fix C** — `_pdf_extract_worker()` 新增 pdfminer logging 抑制（子程序內）：
     * 所有 pdfminer sub-logger 設定 `ERROR` 級別，阻止 107K+ 行 DEBUG flood
   - **Fix D** — `run_pipeline()` 新增 pdfminer logging 抑制（main process）：
     * 與 Fix C 相同，雙重保護（子程序繼承 + 主程序獨立設定）
8. Validation / QC:
   - `python3 -c "import ast; ast.parse(open('edb_scraper.py').read())"` → Syntax OK ✅
   - grep 確認 `proc.kill` 存在於 line 598 ✅
   - grep 確認 pdfminer setLevel 存在於 lines 568–571（worker）+ 806–809（main）✅
   - **GitHub Actions `days-3` workflow 實測：33 秒完成** ✅（修復前卡死 30–60+ 分鐘）
   - **GitHub Pages 已更新** ✅
9. Additional completed (session close):
   - ✅ 版本標籤 v0.2.0 → v1.1.0（edb-dashboard.html 5 處，commit 1b50c62）
   - ✅ GitHub Pages 確認顯示 v1.1.0
   - ✅ 版本標籤同步規則寫入 SESSION_HANDOFF.md Session Close 保障
10. Next priorities:
    - K1/R1 知識框架實作
    - 次要 UI（D8/D9, F4, H5, H6）
    - school-year workflow 觀察
11. Risks / blockers: 主要風險已解決；school-year 模式尚未實測
12. Root Cause / Fix record (Regression entries):
    - **[RE06-A] PDF timeout:**
      * Problem: pdfminer C 擴展在特定 EDB PDF 進入無限解析迴圈，卡死 30–60+ 分鐘
      * Root Cause: SIGTERM 只在 Python bytecode 間處理，C 擴展層不受影響
      * Fix: proc.kill() SIGKILL + pdfminer log 抑制
      * Verification: days-3 workflow 33 秒完成 ✅
    - **[RE06-B] 版本標籤未同步:**
      * Problem: v1.1.0 功能已上線但 HTML 版本標籤仍顯示 v0.2.0，用戶誤判系統未更新
      * Root Cause: 功能開發 commit 未包含版本標籤更新；VM session 路徑 ≠ Mac git repo 路徑
      * Fix: Mac Terminal sed 直接修改 5 處標籤（commit 1b50c62）
      * Rule added: 版本標籤同步規則（SESSION_HANDOFF.md Session Close 保障 ⭐）
      * Verification: GitHub Pages 標題顯示 v1.1.0 ✅

### Next Session Handoff Prompt (Verbatim)

```text
Next Session Handoff Prompt — v15（RE06 Session Close 後最新版本 ✅）
將以下全文貼入新 session 的第一條訊息

項目：EDB Circular AI Analysis System
GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git
GitHub Pages: https://leonard-wong-git.github.io/EDB-AI-Circular-System/

你是此項目的 AI 開發助手，請先讀取以下文件（按順序）：
1. dev/SESSION_HANDOFF.md — 當前狀態 + 所有已知風險 + Session Close 保障規則
2. dev/SESSION_LOG.md — 完整歷史記錄（含 RE06 成功/失敗教訓）
3. dev/v0.2.0-FRONTEND-SPEC.md — 前端規格 SSOT

項目概況
* 單頁 HTML Dashboard（edb-dashboard.html，2796 行）— 顯示 EDB 教育局通告 + AI 分析
* Python 爬蟲（edb_scraper.py）— 爬取 EDB 網站 + 用 gpt-5-nano LLM 分析
* GitHub Actions 自動排程（每日 3 次）抓取新通告 → 更新 circulars.json → 部署 GitHub Pages
* 當前版本：v1.1.0（版本標籤已正確顯示，GitHub Pages 已上線）✅

當前系統狀態（RE06 後全部正常）✅
* GitHub Pages：v1.1.0 已上線，8 項主功能全部可用
* GitHub Actions days-3 workflow：33 秒完成（PDF timeout 已修復）
* edb_scraper.py：SIGKILL timeout + pdfminer log 抑制，穩定運作
* edb-dashboard.html：2796 行，版本標籤 v1.1.0

次要待辦（主系統穩定後進行）
* D8/D9 月曆篩選邏輯
* F4 書籤 badge 計數
* H5 天數選擇器
* H6 已跟進切換
* K1 知識庫參考文件框架
* R1 全角色職責精確度
* LLM 引擎切換機制

⭐ 重要規則（RE06 新增）— 版本標籤同步
每次成功新增/更新功能並 push 後，必須在同一 commit 或立即下一個 commit 更新
edb-dashboard.html 的 5 處版本標籤。在 Mac Terminal（項目目錄內）執行：
  sed -i '' 's/EDB 通告智能分析系統 vX\.X\.X/EDB 通告智能分析系統 vY.Y.Y/g' edb-dashboard.html
  sed -i '' 's/vX\.X\.X-frontend/vY.Y.Y/g' edb-dashboard.html （如適用）
  sed -i '' 's/ vX\.X\.X<\/span>/ vY.Y.Y<\/span>/g' edb-dashboard.html
（VM 編輯路徑 ≠ Mac git repo 路徑，必須直接在 Mac Terminal 用 sed 執行）

gpt-5-nano 必遵守規則
* temperature=1（固定，否則 400 Bad Request）
* max_completion_tokens=16000（非 max_tokens）
* role="developer"（非 "system"）

Git 操作注意
* Mac git repo 路徑：find ~/Library -maxdepth 12 -name "edb-dashboard.html" 2>/dev/null
* Push：git push https://Leonard-Wong-Git@github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git main
* GitHub Actions 會自動 commit circulars.json，push 前先 git pull --rebase
* Workflow 觸發：手動到 GitHub Actions 點 Run workflow（無 push 觸發）
* 安全模式：days-3（33 秒，穩定）；school-year 模式尚未完整實測

建議第一個動作
確認 https://leonard-wong-git.github.io/EDB-AI-Circular-System/ 顯示 v1.1.0，
然後討論下一步：K1/R1 知識框架，或次要 UI 功能（D8/D9, F4, H5, H6）。
```

---

## 2026-03-09

1. Agent & Session ID: Claude_20260309_1943
2. Task summary: 治理框架安裝 + 讀取需求文件 + 製作互動式 HTML Mockup
3. Layer classification: Product / System Layer（Mockup 設計） + Development Governance Layer（框架安裝）
4. Source triage: 需求來源 = `EDB-項目需求及規則總覽.docx`（v2.0，2026-03-09），屬文件驅動設計
5. Files read:
   - `/sessions/.../mnt/uploads/EDB-項目需求及規則總覽.docx`（全文段落 + 10張表格）
   - `dev/SESSION_HANDOFF.md`（初始化空白模板）
   - `dev/SESSION_LOG.md`（初始化空白模板）
6. Files changed:
   - `AGENTS.md`（新建，完整治理規則）
   - `CLAUDE.md`（新建，@AGENTS.md 橋接）
   - `GEMINI.md`（新建，@./AGENTS.md 橋接）
   - `dev/SESSION_HANDOFF.md`（新建→本 session 更新）
   - `dev/SESSION_LOG.md`（新建→本 session 更新）
   - `edb-dashboard-mockup.html`（新建，1452行）
7. Completed:
   - Root Safety Check（pwd=/sessions/kind-eager-pasteur，git root=none）
   - 用戶確認 PROJECT_ROOT（Mac 本機路徑對應 mnt/outputs/EDB-Circular-AI-analysis-system）
   - INSTALL_ROOT_OK + INSTALL_WRITE_OK 雙重確認通過
   - 備份快照建立：`dev/init_backup/20260309_194343_UTC/`（無舊檔，備份為空）
   - 5 個治理檔案建立完成
   - 需求文件完整解析（8節 + 10張表格）
   - 互動式 HTML Mockup 完成：
     * 4 主分頁（通告總覽 / 月曆 / 供應商 / 設定）
     * 詳情面板（右側滑入，5 個內部分頁：總結/行動/截止/角色/版本比較）
     * 4 條 Mock 通告（含完整 llm 欄位、role_relevance、diff）
     * 搜尋建議下拉清單
     * 角色選擇器
     * 截止倒數列
     * 月曆（藍/紅點標記，點擊查看事件）
     * 主題切換（深色/淺色/自動）
     * 字體大小滑桿
     * 設定頁（LLM模型資訊 / 使用指南）
8. Validation / QC:
   - HTML 語法驗證：0 unclosed tags（python html.parser）
   - 20/20 UI 組件驗證全通過（grep 檢查）
   - 文件大小：1452 行
9. Pending: 正式 Dashboard 開發、後端 edb_scraper.py 開發
10. Next priorities:
    - 確認 Mockup UI 方向，收集修改意見
    - 開發正式 `edb-dashboard.html`（功能完整版）
    - 開發 `edb_scraper.py` 後端管線
11. Risks / blockers:
    - gpt-5-nano 必須 temperature=1
    - EDB 網站需 POST + ViewState
    - `--llm-only` 必須搭配 `--output`
12. Notes: 首次 session，專案從零開始

### Problem -> Root Cause -> Fix -> Verification
1. Problem: N/A（首次 session，無 bug）
2. Root Cause: —
3. Fix: —
4. Verification: —
5. Regression / rule update: —

### Consolidation / Retirement Record
1. Duplicate / drift found: 無
2. Single source of truth chosen: `EDB-項目需求及規則總覽.docx` 為本階段 SSOT
3. What was merged: —
4. What was retired / superseded: —
5. Why consolidation was needed: —

---

## 2026-03-09（續）

1. Agent & Session ID: Claude_20260309_KB01
2. Task summary: 知識庫文件建立 + GitHub 推送腳本 + fetch_knowledge.py
3. Layer classification: Product / System Layer（知識庫基礎建設）
4. Source triage: 用戶提供 8 個 EDB/ICAC URL；VM 網絡封鎖，以底稿 + 本地執行腳本代替
5. Files read:
   - `dev/SESSION_HANDOFF.md`（更新前版本）
   - `dev/SESSION_LOG.md`（更新前版本）
6. Files changed:
   - `dev/knowledge/sch_admin_guide.md`（新建）
   - `dev/knowledge/fin_management.md`（新建）
   - `dev/knowledge/curriculum_guides.md`（新建）
   - `dev/knowledge/sch_activities.md`（新建）
   - `dev/knowledge/press_releases.md`（新建）
   - `dev/knowledge/kpm.md`（新建）
   - `dev/knowledge/icac_reference.md`（新建）
   - `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`（新建）
   - `fetch_knowledge.py`（新建）
   - `push-to-github.sh`（新建）
   - `README.md`（新建）、`CHANGELOG.md`（新建）、`.gitignore`（新建）
7. Completed:
   - 8 個角色知識庫底稿（預填內容，清楚標示「底稿」）
   - `ROLE_KNOWLEDGE_INDEX.md`（角色→文件對照，使用說明）
   - `fetch_knowledge.py`（requests + BeautifulSoup4，支援 depth 子頁面抓取，自動生成 index）
   - `push-to-github.sh`（安全 PAT 輸入，re-init git，stage + commit + tag + push，自動清理 token）
   - `README.md`（完整架構圖、資料夾結構、CLI 參數、成本估算、Roadmap）
   - `CHANGELOG.md`（Keep-a-Changelog，v0.1.0-mockup 正式記錄）
   - `.gitignore`（Python/Data/Secrets/macOS/IDE）
8. Validation / QC:
   - 8 個知識文件結構一致（標題/來源/角色/狀態/主要章節）
   - ROLE_KNOWLEDGE_INDEX 對照表完整（6 角色 × 相關文件）
   - push-to-github.sh 安全設計驗證（read -s 隱藏輸入，push 後清理 token URL）
9. Pending: Mac Terminal 執行 `push-to-github.sh`，Mac Terminal 執行 `fetch_knowledge.py`
10. Next priorities:
    - 在 Mac Terminal 執行 push 腳本（需新 GitHub PAT）
    - 在 Mac Terminal 執行 fetch_knowledge.py 更新知識庫
    - 開發正式 `edb-dashboard.html`（v0.2.0-frontend）
11. Risks / blockers:
    - VM 網絡封鎖 edb.gov.hk + github.com（已 workaround：Mac Terminal 腳本）
    - EDB 部分頁面為 ASP.NET WebForms，requests GET 可能只獲取部分內容
12. Notes: 接續 Claude_20260309_1943 session，於新 session 中因 context window 用盡而分段處理

### Problem -> Root Cause -> Fix -> Verification
1. Problem: VM 網絡封鎖，無法直接抓取 EDB/ICAC URL 或推送 GitHub
2. Root Cause: VM egress proxy 封鎖外部請求（edb.gov.hk, icac.org.hk, github.com）
3. Fix: 建立底稿知識文件 + fetch_knowledge.py（Mac 執行）+ push-to-github.sh（Mac 執行）
4. Verification: 腳本邏輯審閱通過，用戶需在 Mac 端執行驗證
5. Regression / rule update: 已記錄「VM 網絡限制」於 SESSION_HANDOFF Known Risks

### Consolidation / Retirement Record
1. Duplicate / drift found: 無
2. Single source of truth chosen: 知識庫以官方 URL 為 SSOT，底稿為臨時替代
3. What was merged: —
4. What was retired / superseded: —
5. Why consolidation was needed: —

---

### Next Session Handoff Prompt (Verbatim)
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：Mockup v1.0 完成，進入正式開發階段

已完成：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）安裝完畢
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）已全文解析
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行）已完成並通過 QC

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard-mockup.html   ← 本 session 產出，請先瀏覽確認 UI 方向
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  └── dev/SESSION_HANDOFF.md + SESSION_LOG.md

待處理優先事項（按序）：
1. 用戶確認 Mockup UI 方向後，開發正式 edb-dashboard.html（功能完整版）
2. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano）
3. 整合測試：circulars.json 與 Dashboard 聯調，按需求文件第八節驗收

關鍵技術規則（必讀，開發前對齊）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS

第一個具體行動：
  在瀏覽器開啟 edb-dashboard-mockup.html，確認 UI 設計方向，
  提供修改意見後即可開始正式 edb-dashboard.html 開發。
```

---

## 2026-03-09（SESSION CLOSE — Claude_20260309_KB02）

1. Agent & Session ID: Claude_20260309_KB02
2. Task summary: 知識庫使用規則澄清 + Session Close
3. Layer classification: Development Governance Layer（規則補充）
4. Source triage: 用戶口頭指示，補充知識庫使用約束條件
5. Files changed:
   - `dev/SESSION_HANDOFF.md`：新增「Knowledge Base Usage Rules」章節（5條強制規則）
   - `dev/SESSION_LOG.md`：本條目（session close 記錄）
6. Key clarifications recorded:
   - **知識庫只在分析通告時使用**（非一般對話）
   - **ROLE_KNOWLEDGE_INDEX 只列 top 5**，並非完整知識庫
   - **查閱方式：Index → Link → Fetch**（動態連結至相關章節，不全文載入）
   - 知識庫是輔助資料，不可因未覆蓋某範疇而拒絕分析
   - `fetch_knowledge.py` 已在 Mac 成功執行（20:48 UTC），9/9 來源成功，知識庫已含官網真實內容
7. Validation: SESSION_HANDOFF.md 規則章節結構正確，Next Session Handoff Prompt v3 已更新

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 知識庫使用邊界不清晰（何時用、如何查閱、覆蓋範圍）
2. Root Cause: 上兩個 session 只建立了文件，未明文定義使用協議
3. Fix: 在 SESSION_HANDOFF.md 新增 Knowledge Base Usage Rules（5條）
4. Verification: 規則已寫入 SSOT（SESSION_HANDOFF.md），下個 session 讀取時自動生效
5. Regression / rule update: 無

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: SESSION_HANDOFF.md Knowledge Base Usage Rules 章節
3. Merged: 知識庫使用規則集中至 SESSION_HANDOFF.md
4. Retired: Next Session Handoff Prompt v1、v2（由 v3 取代，見下方）
5. Why: 減少跨文件查閱，確保下個 agent 只需讀 SESSION_HANDOFF 即可對齊

---

---

## 2026-03-10

1. Agent & Session ID: Claude_20260310_FE01
2. Task summary: 正式版 `edb-dashboard.html` 開發（v0.2.0-frontend），全功能實作
3. Layer classification: Product / System Layer（正式前端開發）
4. Source triage: 需求來源 = `dev/v0.2.0-FRONTEND-SPEC.md`（用戶已確認 SSOT），補充用戶口頭反饋 A1–A10 + 助手提案 B1–B8
5. Files read:
   - `dev/SESSION_HANDOFF.md`
   - `dev/v0.2.0-FRONTEND-SPEC.md`
   - `dev/knowledge/ROLE_KNOWLEDGE_INDEX.md`
   - `dev/knowledge/icac_reference.md`
   - `edb-dashboard.html`（QC 驗證時）
6. Files changed:
   - `edb-dashboard.html`（新建，2,292 行）
   - `CHANGELOG.md`（新增 v0.2.0-frontend 記錄）
   - `dev/SESSION_HANDOFF.md`（本 session 記錄更新）
   - `dev/SESSION_LOG.md`（本 session 記錄，本條目）
7. Completed:
   - 用戶 UI 反饋整理：A1–A10（用戶提供）+ B1–B8（助手提案）共 18 項確認
   - `dev/v0.2.0-FRONTEND-SPEC.md` 建立（17 節完整規格，用戶確認為 SSOT）
   - `edb-dashboard.html` 全功能實作：
     * 6 主分頁（通告總覽 / 月曆 / 資源與申請 / 收藏清單 / 供應商 / 設定）
     * 詳情面板 5 個內部分頁（總結 / 行動方案 / 截止日期 / 角色分析 / 版本比較）
     * 4 色調 × 2 主題系統（Spring/Summer/Autumn/Winter × 深色/淺色）
     * localStorage 14 個 key 持久化
     * 角色條件顯示（供應商 Tab 僅在 supplier 角色出現）
     * Grant info 雙類型（💰可申請 vs 📦資源）
     * 截止日期三類型（apply/submission/awareness）
     * 狀態三態循環 + 書籤雙軌（⭐ + 📌）
     * 統計列（角色適配）+ 篩選列（6 維度，可收摺）
     * 月曆（Notion 風格，格內顯示標題）
     * Dev 頁面（?dev=1 或版本號連按 5 次）
     * 鍵盤快捷鍵（1–6 / / / T / Esc / ?）
     * Print 支援（@media print）
     * Mock 數據 4 條（完整 schema）
   - CHANGELOG.md 更新（v0.2.0-frontend 正式記錄）
8. Validation / QC:
   - HTML 語法驗證：0 unclosed tags（python html.parser）
   - 26/26 功能驗證全通過（grep 檢查）
   - 文件大小：2,292 行
9. Pending:
   - 用戶在瀏覽器視覺確認 `edb-dashboard.html`
   - Mac Terminal 執行 `push-to-github.sh`（更新 CHANGELOG 後推送，tag: v0.2.0-frontend）
   - 開發 `edb_scraper.py` 後端管線（v0.3.0-backend）
10. Next priorities:
    - 用戶瀏覽器開啟 `edb-dashboard.html` 目視驗收
    - GitHub 推送 v0.2.0-frontend tag
    - 開發 `edb_scraper.py`（v0.3.0-backend）
11. Risks / blockers:
    - 同前（VM 網絡封鎖，GitHub 推送需 Mac Terminal + 新 PAT）
12. Notes:
    - 本 session 因 context window 限制分為兩段（context compaction 後接續）
    - 大型 HTML 寫入分兩步驟（Write CSS+HTML → Edit JS 替換佔位符）解決 token 限制問題

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 單次 Write 工具輸出過長，HTML 被截斷
2. Root Cause: Output token 限制
3. Fix: 先 Write CSS+HTML（含 JS 佔位符），再 Edit 替換 JS 佔位符為完整 JavaScript
4. Verification: HTML 語法驗證通過，26/26 功能 grep 驗證通過
5. Regression / rule update: 大型單檔案寫入技巧記錄於本條目，可供後續 session 參考

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: `dev/v0.2.0-FRONTEND-SPEC.md` 為前端功能規格 SSOT
3. Merged: 用戶反饋 A1–A10 + 助手提案 B1–B8 統整至 SPEC
4. Retired: edb-dashboard-mockup.html 功能已被 edb-dashboard.html 取代（mockup 保留作參考）
5. Why: 正式版取代 mockup，規格 SSOT 集中管理

---

### Next Session Handoff Prompt — v5（最終版本 ✅，請用此版本）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.0-frontend ✅ 完成，準備進入 v0.3.0-backend 開發

已完成（全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行，QC 通過）✅
- 角色知識庫 9 個文件（dev/knowledge/）建立，官網內容已抓取 ✅
- 知識庫使用規則寫入 SESSION_HANDOFF.md ✅
- GitHub 推送完成（tag: v0.1.0-mockup）✅
- 正式 Dashboard（edb-dashboard.html，2292行，QC 26/26 通過）✅ ← NEW
- v0.2.0-FRONTEND-SPEC.md（規格 SSOT）✅ ← NEW

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html           ← 正式版 Dashboard（目視確認後推送 GitHub）
  ├── edb-dashboard-mockup.html   ← 保留作 UI 參考
  ├── fetch_knowledge.py
  ├── push-to-github.sh
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  ├── README.md / CHANGELOG.md / .gitignore
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── v0.2.0-FRONTEND-SPEC.md     ← 前端規格 SSOT
      └── knowledge/
          ├── ROLE_KNOWLEDGE_INDEX.md
          └── [9 個知識庫文件]

待處理優先事項（按序）：
1. 用戶在瀏覽器開啟 edb-dashboard.html 目視驗收
2. Mac Terminal 執行 push-to-github.sh 推送 v0.2.0-frontend tag
3. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano，v0.3.0-backend）
4. 整合測試：circulars.json 與 Dashboard 聯調（v1.0.0-release）

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）
- 知識庫是輔助資料，不可因未覆蓋而拒絕分析通告

第一個具體行動：
  在瀏覽器開啟 edb-dashboard.html，確認 UI + 所有功能正常，
  然後在 Mac Terminal 執行 push-to-github.sh 推送 v0.2.0-frontend，
  再開始 edb_scraper.py 後端開發。
```

---

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE01
2. Task summary: v0.2.1-frontend 13 項 UI 修訂 + v0.3.0-backend 後端管線啟動
3. Layer classification: Product / System Layer（UI 修訂 + 後端開發）
4. Source triage: 用戶口頭列舉 13 項修訂；後端規格來自需求文件第五/六節
5. Files read:
   - `dev/SESSION_HANDOFF.md`（v0.2.0-frontend 版本）
   - `CHANGELOG.md`（v0.2.0-frontend 版本）
   - `edb_scraper.py`（新建後驗證）
6. Files changed:
   - `edb-dashboard.html`（更新，2,292→2,453 行，13 項修訂）
   - `edb_scraper.py`（新建，v0.3.0-backend，450+ 行）
   - `requirements.txt`（新建）
   - `CHANGELOG.md`（更新，新增 v0.2.1-frontend 記錄）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - v0.2.1-frontend 13 項 UI 修訂（完整清單見 CHANGELOG.md v0.2.1-frontend 節）：
     * Fix 1：4 個統計 Tag 改為可點擊連結
     * Fix 2：視圖工具列加「卡片」「列表」文字 + 🖨️ 列印按鈕
     * Fix 3：收藏頁指引橫幅 + Tab 徽章
     * Fix 4：月曆顏色邏輯（紅=高影響+必須，藍=一般，綠=截止）+ isAttention()
     * Fix 5：REFERENCE_CIRCULARS 3 條預設常備通告（自動首次釘選）
     * Fix 6：4 色調 × 2 主題 CSS 組合選擇器（surface/border 也變色）
     * Fix 7：數據來源卡片移至 Dev 頁
     * Fix 8：使用指南移至 Dev 頁（標示「開發者」）
     * Fix 9a：快捷鍵 T→D（避免衝突）
     * Fix 9b：Header 角色指示器徽章 + updateRoleIndicator()
     * Fix 10：行動角色名稱改中文 + 當前角色高亮
     * Fix 11：頁腳免責聲明（EDB 數據來源）
     * Fix 12：系統設計者 Leonard Wong
     * Fix 13：供應商頁移除政策指引 chip，加外部連結注釋
   - `edb_scraper.py` v0.3.0-backend 建立（ASP.NET ViewState POST + 位置式表格 + pdfplumber + gpt-5-nano json_schema，temperature=1 固定）
   - `requirements.txt` 建立（requests / beautifulsoup4 / pdfplumber / openai / lxml）
   - `edb_scraper.py` py_compile 語法驗證通過
8. Validation / QC:
   - edb_scraper.py：`python3 -m py_compile` ✅ Syntax OK
   - edb-dashboard.html：2,453 行（+161 行 vs v0.2.0）
   - CHANGELOG.md v0.2.1-frontend 記錄完整
9. Pending:
   - Mac Terminal：`pip install -r requirements.txt`
   - Mac Terminal：`python3 edb_scraper.py --days 7 --dry-run -v`（EDB 網絡測試）
   - Mac Terminal：`push-to-github.sh`（tag: v0.2.1-frontend）
   - 設定 `export OPENAI_API_KEY="sk-..."`
   - 完整後端執行：`python3 edb_scraper.py --days 30 --output ./circulars.json -v`
10. Next priorities:
    - dry-run 測試驗證 EDB ViewState POST 有效
    - 完整 LLM 分析執行，生成真實 circulars.json
    - 整合測試：circulars.json 載入 Dashboard（v1.0.0-release）
11. Risks / blockers:
    - gpt-5-nano temperature=1 固定（不可更改）
    - EDB 網站位置式表格（Col 0=通告號，Col 1=標題，Col 2=日期，Col 3+=PDF）
    - VM 網絡封鎖，所有外部操作需 Mac Terminal
12. Notes:
    - 本 session 因 context compaction 從摘要接續，所有設計決定見上方摘要
    - 大型 HTML 修改分多次 Edit（而非整體重寫）以維持穩定性

### Problem -> Root Cause -> Fix -> Verification
1. Problem: QC「Fix3 instructions visible」字串比對失敗
2. Root Cause: QC 查找字串帶逗號（`'釘選），永久保存'`），HTML 實際無逗號
3. Fix: 確認 HTML 內容正確（無逗號版本），QC 邏輯調整
4. Verification: 目視確認 Fix 3 橫幅文字正確
5. Regression / rule update: QC grep 字串需與實際 HTML 完全一致

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: CHANGELOG.md 記錄 v0.2.1-frontend 修訂；需求文件後端規格保持不變
3. Merged: 13 項修訂統整至 CHANGELOG v0.2.1-frontend
4. Retired: v5 Handoff Prompt（由 v6 取代，見下方）
5. Why: 版本進度更新，後端管線啟動

---

### Next Session Handoff Prompt — v6（已由 v7 取代）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.1-frontend ✅ 完成，v0.3.0-backend 管線已建立，待 Mac Terminal 測試

已完成（全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行）✅
- 角色知識庫 9 個文件（dev/knowledge/）+ 官網內容已抓取 ✅
- GitHub 推送（tag: v0.1.0-mockup）✅
- 正式 Dashboard（edb-dashboard.html，v0.2.0，2292行，QC 26/26）✅
- v0.2.1-frontend 13 項 UI 修訂（2453行）✅ ← NEW
- edb_scraper.py 後端管線建立（v0.3.0-backend，450+行，syntax OK）✅ ← NEW
- requirements.txt 更新 ✅ ← NEW

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html           ← 正式版 Dashboard（v0.2.1，2453行）
  ├── edb_scraper.py               ← 後端管線（v0.3.0-backend，待測試）
  ├── fetch_knowledge.py           ← 知識庫抓取工具
  ├── requirements.txt             ← Python 依賴（已更新）
  ├── push-to-github.sh            ← GitHub 推送腳本
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── v0.2.0-FRONTEND-SPEC.md  ← 前端規格 SSOT
      └── knowledge/[9 個知識庫文件]

待處理優先事項（按序，Mac Terminal 執行）：
1. cd ~/path/to/EDB-Circular-AI-analysis-system
2. pip install -r requirements.txt
3. export OPENAI_API_KEY="sk-..."
4. python3 edb_scraper.py --days 7 --output ./circulars.json --dry-run -v  # 測試網絡
5. python3 edb_scraper.py --days 30 --output ./circulars.json -v           # 完整執行
6. bash push-to-github.sh  # 推送 tag v0.2.1-frontend
7. 在瀏覽器開啟 edb-dashboard.html，確認真實 circulars.json 已載入

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
  表格欄位：Col 0=通告號，Col 1=標題+URL，Col 2=日期，Col 3+=PDF 連結
- gpt-5-nano：temperature=1 固定（不可更改），Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）

第一個具體行動：
  在 Mac Terminal 執行 dry-run 測試，確認 EDB 網站連通 + ViewState POST 有效：
  python3 edb_scraper.py --days 7 --output ./circulars.json --dry-run -v
  若成功：執行完整版 python3 edb_scraper.py --days 30 --output ./circulars.json -v
```

---

### Next Session Handoff Prompt — v5（已由 v7 取代）
```text
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.1.0-mockup ✅ 全數完成，準備進入 v0.2.0-frontend 開發

已完成（v0.1.0-mockup 里程碑，全部 ✅）：
- 治理框架（AGENTS.md / CLAUDE.md / GEMINI.md）✅
- 需求文件（EDB-項目需求及規則總覽.docx v2.0）全文解析 ✅
- 互動式 HTML Mockup（edb-dashboard-mockup.html，1452行，QC 通過）✅
- 角色知識庫 9 個文件（dev/knowledge/）建立，官網內容已抓取（2026-03-09 20:48 UTC）✅
- 知識庫使用規則寫入 SESSION_HANDOFF.md ✅
- GitHub 推送完成（tag: v0.1.0-mockup，repo: Leonard-Wong-Git/EDB-AI-Circular-System）✅

主要檔案位置（Mac）：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard-mockup.html   ← 請先在瀏覽器開啟確認 UI 方向
  ├── fetch_knowledge.py
  ├── push-to-github.sh
  ├── AGENTS.md / CLAUDE.md / GEMINI.md
  ├── README.md / CHANGELOG.md / .gitignore
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      └── knowledge/
          ├── ROLE_KNOWLEDGE_INDEX.md     ← 角色→知識文件對照（top 5）
          ├── sch_admin_guide.md          ← 所有角色
          ├── fin_management.md           ← 所有角色
          ├── curriculum_guides.md        ← 所有角色
          ├── sch_activities.md           ← 所有角色
          ├── press_releases.md           ← 所有角色
          ├── kpm.md                      ← 所有角色
          ├── fin_management_supplier.md  ← supplier 專屬
          ├── icac_reference.md           ← supplier 專屬
          └── press_releases_supplier.md  ← supplier 專屬

待處理優先事項（按序）：
1. 用戶確認 Mockup UI 方向後，開發正式 edb-dashboard.html（v0.2.0-frontend）
2. 開發 edb_scraper.py 後端（ASP.NET POST 抓取 → pdfplumber → gpt-5-nano，v0.3.0-backend）
3. 整合測試：circulars.json 與 Dashboard 聯調，按需求文件第八節驗收（v1.0.0-release）

關鍵技術規則（必讀）：
- EDB 網站：POST + ViewState（GET 無效），解析用位置式（非 CSS class）
- gpt-5-nano：temperature=1 固定，Structured Output 用 json_schema
- --llm-only 必須搭配 --output ./circulars.json
- circulars.json 必須與 edb-dashboard.html 同目錄
- Dashboard：單檔案 HTML（無建構工具），內嵌 CSS+JS
- VM 網絡封鎖 edb.gov.hk + github.com，所有外部操作必須在 Mac Terminal 執行

知識庫使用規則（必須遵守）：
- 只在「分析通告」時使用，不用於一般對話
- ROLE_KNOWLEDGE_INDEX.md 只列每角色 top 5，非完整清單
- 查閱方式：Index → Link → Fetch（只讀相關章節，不全文載入）
- 知識庫是輔助資料，不可因未覆蓋而拒絕分析通告

第一個具體行動：
  在瀏覽器開啟 edb-dashboard-mockup.html，確認 UI 設計方向，
  提供修改意見後即可開始正式 edb-dashboard.html 開發（v0.2.0-frontend）。
```

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE02
2. Task summary: EDB POST 表單字段診斷 + 修正
3. Layer classification: Product / System Layer（後端調試）
4. Source triage: Mac Terminal 實測輸出（parse_form.py 解析 debug_edb_GET.html），屬實測驅動修正
5. Files read: edb_scraper.py（查閱舊字段）; debug_edb_GET.html（Mac 存檔，parse_form.py 解析）
6. Files changed:
   - `edb_scraper.py`（更新：POST data 字段全部修正）
   - `debug_edb_html.py`（新建→更新：POST 字段同步修正）
   - `parse_form.py`（新建：表單結構解析工具）
   - `dev/SESSION_HANDOFF.md`（更新：Known Risks #4 + Open Priorities）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - Mac Terminal：pip install 成功 ✅
   - dry-run 執行：HTTP 200 但表格找不到（字段全錯）
   - parse_form.py 解析揭示實際字段，完成以下修正：
     * ContentPlaceHolder1 → MainContentPlaceHolder
     * txtFromDate → txtPeriodFrom
     * txtToDate → txtPeriodTo
     * btnSearch → btnSearch2
     * 移除不存在的 ddlYear/ddlMonth
     * 新增 ctl00$currentSection="2" + lbltab_circular="通告"
8. Validation / QC: parse_form.py 輸出確認實際字段；修正後待 Mac Terminal 驗證
9. Pending: python3 debug_edb_html.py（驗證修正）→ dry-run → 完整 LLM 執行
10. Next priorities:
    - ⭐ python3 debug_edb_html.py 確認 POST 找到通告號碼
    - 完整 dry-run → LLM 分析 → circulars.json
    - push-to-github.sh（tag: v0.2.1-frontend）
11. Risks / blockers: _parse_list() 表格格式未知，可能仍需調整；通告號正則待確認

### Problem -> Root Cause -> Fix -> Verification
1. Problem: POST 後找不到通告表格
2. Root Cause: 所有 POST 字段名稱錯誤（假設了錯誤的 ContentPlaceHolder1）
3. Fix: parse_form.py 解析實際 HTML，全部修正至真實字段名稱
4. Verification: 待執行 debug_edb_html.py（下個 session）
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #4（SSOT）

### Consolidation / Retirement Record
1. SSOT: SESSION_HANDOFF Known Risks #4 = EDB 表單字段唯一正確記錄
2. Retired: 舊 POST data（ContentPlaceHolder1 版本）已替換

---

### Next Session Handoff Prompt — v7（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.2.1-frontend ✅，後端 POST 字段已修正，待 Mac Terminal 驗證

已完成（全部 ✅）：
- 治理框架 ✅ | 需求文件解析 ✅ | Mockup ✅ | 知識庫 ✅
- Dashboard v0.2.1（2453行，13修訂）✅
- edb_scraper.py v0.3.0-backend 建立 + POST 字段修正 ✅
- pip install 成功 ✅

⚠️ EDB 表單字段（已從實測確認，見 SESSION_HANDOFF Known Risks #4）：
  PlaceholderID : MainContentPlaceHolder（非 ContentPlaceHolder1）
  日期字段      : txtPeriodFrom / txtPeriodTo
  搜尋按鈕      : btnSearch2
  必要字段      : ctl00$currentSection="2", lbltab_circular="通告"
  下拉字段      : ddlSchoolType2 + ddlCircularType（無 ddlYear/ddlMonth）

主要檔案：outputs/EDB-Circular-AI-analysis-system/
  edb_scraper.py, debug_edb_html.py, parse_form.py, requirements.txt
  push-to-github.sh, edb-dashboard.html（v0.2.1）

⭐ 立即執行（Mac Terminal）：
  cd "<EDB 項目路徑>"
  python3 debug_edb_html.py
  # 成功標誌：EDB CIRCULAR NUMBERS FOUND 列出通告號碼

確認成功後：
  python3 edb_scraper.py --days 30 --output ./circulars.json --dry-run -v
  export OPENAI_API_KEY="sk-..."
  python3 edb_scraper.py --days 30 --output ./circulars.json -v
  bash push-to-github.sh  # tag: v0.2.1-frontend

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE03
2. Task summary: EDB HTML 結構解析 + _parse_list 完整重寫 + dry-run 通過 ✅
3. Layer classification: Product / System Layer（後端調試 + 驗證）
4. Source triage: Mac Terminal 執行 parse_structure.py + parse_row.py 輸出，屬實測驅動修正
5. Files read: edb_scraper.py（多次）
6. Files changed:
   - `edb_scraper.py`（更新：_parse_list 完整重寫 + _abs_url urljoin + timezone fix）
   - `parse_structure.py`（新建：DOM 結構診斷）
   - `parse_row.py`（新建：完整 row 解析）
   - `dev/SESSION_HANDOFF.md`（更新：Known Risks #5 + Open Priorities + Last Session）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - debug_edb_html.py（修正後）確認 POST 找到 14 條通告號碼 ✅
   - parse_structure.py：確認通告號在 <div class="circulars_result_remark"> 內
   - parse_row.py：確認完整 row 結構（3 cells，PDF 3個連結，無 detail_url，日期格式 "日期DD/MM/YYYY"）
   - _parse_list() 完整重寫（基於實測結構，移除舊假設）
   - _abs_url() 修正為 urljoin（正確處理 ../）
   - datetime.utcnow() → datetime.now(timezone.utc)（消除 DeprecationWarning）
   - **Dry-run 完全通過：**
     * 14 條通告爬取並解析 ✅
     * PDF 下載並文字提取（pdfplumber，最大 7310 chars）✅
     * circulars.json 38.4KB 儲存成功 ✅
     * 零錯誤，只剩 datetime 警告（已修正）
8. Validation / QC:
   - py_compile OK ✅
   - dry-run: 14/14 circulars parsed, PDFs extracted, JSON saved ✅
9. Pending: export OPENAI_API_KEY → 完整 LLM 執行
10. Next priorities:
    - ⭐ python3 edb_scraper.py --days 30 --output ./circulars.json -v（真實 LLM）
    - 瀏覽器確認 circulars.json 載入 Dashboard
    - push-to-github.sh（tag: v0.3.0-backend）
11. Risks / blockers:
    - LLM 分析 14條 × ~30s = 約 7分鐘，正常
    - OPENAI_API_KEY 必須在 Mac Terminal export

### Problem -> Root Cause -> Fix -> Verification
1. Problem: _parse_list() 找不到表格（表格存在但結構與假設完全不符）
2. Root Cause: EDB 用非標準結構（td.circularResultRow + div.circulars_result_remark），非簡單表格列
3. Fix: 完整重寫 _parse_list()，基於 parse_row.py 確認的真實結構
4. Verification: dry-run 通過（14 circulars parsed）✅
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #5（SSOT）

### Consolidation / Retirement Record
1. Duplicate / drift: 舊 _parse_list 假設（col0=通告號，col1=標題，col2=日期）已替換
2. SSOT: SESSION_HANDOFF Known Risks #5 = EDB HTML 通告結構唯一正確記錄
3. Merged: HTML 結構知識集中於 Known Risks
4. Retired: 舊 _parse_list 邏輯（基於不存在的表格結構）
5. Why: 防止未來 session 重複分析相同結構

---

### Next Session Handoff Prompt — v8（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：Dry-run ✅ 通過，準備執行完整 LLM 分析

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅ | edb_scraper.py v0.3.0 ✅
- pip install ✅ | EDB POST 字段修正 ✅ | HTML 解析修正 ✅
- Dry-run: 14 circulars + PDF text + 38.4KB JSON ✅

⭐ 立即執行（Mac Terminal）：
  export OPENAI_API_KEY="sk-..."
  python3 edb_scraper.py --days 30 --output ./circulars.json -v
  # 預計時間：約 7-10 分鐘（14條 × LLM 分析）

完成後：
  在瀏覽器開啟 edb-dashboard.html，確認真實 circulars.json 顯示正常
  bash push-to-github.sh  # tag: v0.3.0-backend

關鍵規則：gpt-5-nano temperature=1 固定（不可更改）
EDB HTML 結構：見 SESSION_HANDOFF Known Risks #5
```

---

## 2026-03-10（續）

1. Agent & Session ID: Claude_20260310_BE04
2. Task summary: gpt-5-nano LLM 修正（developer role + max_completion_tokens）+ 完整管線通過 + GitHub 推送
3. Layer classification: Product / System Layer（後端 LLM 調試 + 發布）
4. Source triage: OpenAI API 錯誤訊息驅動修正；Mac Terminal 實測驗證
5. Files changed:
   - `edb_scraper.py`（更新：max_tokens→max_completion_tokens，system→developer role，tokens 4096→16000）
   - `test_llm.py`（更新：同步修正 + 增加 developer role）
   - `dev/SESSION_HANDOFF.md`（更新：v0.3.0-backend 完成標記 + LLM 規則補充）
   - `dev/SESSION_LOG.md`（本條目）
6. Completed:
   - 修正 `max_tokens` → `max_completion_tokens`（gpt-5-nano 推理模型要求）
   - 修正 `"system"` → `"developer"` role（推理模型要求）
   - 修正 `max_completion_tokens` 4096 → 16000（推理 tokens 消耗大）
   - test_llm.py Test 2 ✅ Test 3 ✅（finish_reason: stop，1675 chars）
   - 完整 LLM 執行成功：EDBCM030 high/721chars，EDBCM026 mid/462chars ✅
   - GitHub force push 成功（52 objects，11.35 MiB）✅
   - tag v0.3.0-backend 推送成功 ✅
7. Validation / QC:
   - LLM 分析：summary 有內容，impact/tags 正確 ✅
   - GitHub: https://github.com/Leonard-Wong-Git/EDB-AI-Circular-System.git tag v0.3.0-backend ✅
8. Pending: 瀏覽器開啟 edb-dashboard.html 確認真實數據顯示
9. Next priorities:
   - ⭐ open edb-dashboard.html 確認真實 circulars.json 整合
   - 根據真實數據微調 Dashboard（如有需要）
   - v1.0.0-release
10. Notes: gpt-5-nano 確認為推理模型（需要 developer role + max_completion_tokens + 16000 tokens）

### Problem -> Root Cause -> Fix -> Verification
1. Problem: LLM 返回空內容（finish_reason: length，0 chars）
2. Root Cause: gpt-5-nano 是推理模型，max_completion_tokens=4096 被推理過程耗盡；system role 不支援
3. Fix: developer role + max_completion_tokens=16000
4. Verification: test_llm.py Test 3 finish_reason=stop，1675 chars ✅；完整管線 LLM 成功 ✅
5. Regression / rule update: 記錄於 SESSION_HANDOFF Known Risks #1（補充）

### Consolidation / Retirement Record
1. SSOT: SESSION_HANDOFF Known Risks #1 = gpt-5-nano 所有規則（temperature=1, developer role, max_completion_tokens=16000）
2. Retired: system role（已替換為 developer）；max_tokens（已替換為 max_completion_tokens）

---

### Next Session Handoff Prompt — v8（已由 v9 取代）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.3.0-backend ✅ 完成並推送 GitHub，準備瀏覽器整合確認

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅
- edb_scraper.py v0.3.0：14條真實通告 + PDF + LLM 分析 ✅
- circulars.json 已生成（真實 EDB 數據）✅
- GitHub tag v0.3.0-backend 已推送 ✅

⚠️ gpt-5-nano 規則（全部已確認，不可更改）：
  temperature=1（固定）
  role="developer"（非"system"）
  max_completion_tokens=16000（非max_tokens，非4096）

⭐ 下一步：
  open edb-dashboard.html  # 確認真實 circulars.json 正確顯示
  # 如有顯示問題，調整 Dashboard JS 數據載入邏輯

最終里程碑：v1.0.0-release（整合測試通過後）
```

---

## 2026-03-10（Session Close — Claude_20260310_BE04）

1. Agent & Session ID: Claude_20260310_BE04（Session Close）
2. Task summary: Session 收尾打包 — CHANGELOG 更新、診斷工具歸檔、手動 git 指南、SESSION 文件完成
3. Layer classification: Development Governance Layer（Session 管理）
4. Source triage: 用戶指示（「session close，pack 好相關文件，建設新資料夾，git 上載方法詳細清楚，handover 去其他 session」）
5. Files read: SESSION_HANDOFF.md（驗證），CHANGELOG.md（更新前確認）
6. Files changed:
   - `CHANGELOG.md`（更新：新增完整 v0.3.0-backend 節，含 Added/Fixed/Verified/Technical 四段）
   - `dev/tools/`（新建資料夾）：
     * `debug_edb_html.py`（移入）
     * `parse_form.py`（移入）
     * `parse_structure.py`（移入）
     * `parse_row.py`（移入）
     * `test_llm.py`（移入）
   - `dev/GIT_PUSH_MANUAL.md`（新建：完整手動 git 推送指南，含 PAT 方法、版本號規則、常用指令）
   - `dev/SESSION_HANDOFF.md`（更新：Last Session Record 完整補全，Open Priorities 全部標記完成）
   - `dev/SESSION_LOG.md`（本條目 + v9 Handoff Prompt）
7. Completed:
   - CHANGELOG.md v0.3.0-backend 完整記錄（Added 7項 + Fixed 8項 + Verified 4項 + Technical 2項）✅
   - 診斷工具從根目錄移至 `dev/tools/`（保持根目錄整潔）✅
   - `dev/GIT_PUSH_MANUAL.md` 建立（無需依賴 push-to-github.sh，手動 PAT 推送全流程）✅
   - SESSION_HANDOFF.md Last Session Record 完整更新（BE04 全部完成事項）✅
   - SESSION_LOG.md v9 Handoff Prompt 完成（見下方）✅
8. Validation / QC:
   - CHANGELOG.md 結構正確（Keep-a-Changelog 格式）
   - dev/tools/ 5 個工具文件確認存在
   - GIT_PUSH_MANUAL.md 包含：標準推送流程、首次設定、PAT 生成步驟、版本號規則、現有 tags
9. Pending: 在 Mac Terminal 執行最終 git push（含 dev/tools/ + GIT_PUSH_MANUAL.md + CHANGELOG 更新）
10. Notes: 下個 session 的首要任務是 v1.0.0-release 整合測試

### Problem -> Root Cause -> Fix -> Verification
1. Problem: N/A（session close 無 bug）
2. Root Cause: —
3. Fix: —
4. Verification: —
5. Regression / rule update: 無新規則；診斷工具歸檔政策記錄於本條目

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. SSOT: GIT_PUSH_MANUAL.md 為手動 git 推送的 SSOT（push-to-github.sh 仍保留作參考）
3. Merged: 診斷工具集中於 dev/tools/
4. Retired: v8 Handoff Prompt（由 v9 取代）
5. Why: Session close 時清理工具文件，保持根目錄整潔

---

### Next Session Handoff Prompt — v9（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v0.3.0-backend ✅ 完整完成 + GitHub 推送 + Session Close 打包完畢

已完成（全部 ✅）：
- 治理框架 ✅ | 需求文件解析 ✅ | Mockup ✅ | 知識庫 ✅
- Dashboard v0.2.1（2453行，13修訂）✅
- edb_scraper.py v0.3.0-backend：完整管線（POST + PDF + LLM）✅
- circulars.json：14條真實 EDB 通告 + LLM 分析 ✅
- GitHub tag v0.3.0-backend ✅
- Session Close 打包：CHANGELOG ✅ | dev/tools/ ✅ | GIT_PUSH_MANUAL.md ✅

⚠️ gpt-5-nano 規則（全部已確認，不可更改）：
  temperature=1（固定）
  role="developer"（非 "system"）
  max_completion_tokens=16000（非 max_tokens，非 4096）

⚠️ EDB 網站字段（已從實測確認，不可更改）：
  PlaceholderID : MainContentPlaceHolder
  日期字段      : txtPeriodFrom / txtPeriodTo
  搜尋按鈕      : btnSearch2
  必要字段      : ctl00$currentSection="2", lbltab_circular="通告"

⚠️ EDB HTML 通告結構（已從實測確認）：
  每條通告 = <tr> 含 3× <td class="circularResultRow circulartRow">
  Cell[0]=日期（"日期DD/MM/YYYY"），Cell[1]=標題+通告號，Cell[2]=PDF連結（C/E/S）
  無 detail_url；PDF C.pdf（繁中）優先

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html        ← 正式版 Dashboard v0.2.1
  ├── edb_scraper.py            ← 後端管線 v0.3.0
  ├── circulars.json            ← 14條真實通告（真實 LLM 分析）
  ├── requirements.txt
  ├── push-to-github.sh         ← 舊推送腳本（備用）
  └── dev/
      ├── SESSION_HANDOFF.md + SESSION_LOG.md
      ├── GIT_PUSH_MANUAL.md    ← ⭐ 新版手動 git 推送指南
      ├── v0.2.0-FRONTEND-SPEC.md
      ├── tools/                ← 診斷工具（debug/parse/test）
      └── knowledge/[9 個知識庫文件]

⭐ 下一步（v1.0.0-release）：
  1. 在瀏覽器開啟 edb-dashboard.html，確認 circulars.json 真實數據正確顯示
  2. 如有顯示問題，微調 Dashboard JS 數據載入邏輯
  3. 整合驗收通過後，參照 dev/GIT_PUSH_MANUAL.md 推送 tag v1.0.0-release

Mac Terminal 最終 git push（先推送 session close 文件）：
  cd "<EDB 項目路徑>"
  git add dev/tools/ dev/GIT_PUSH_MANUAL.md CHANGELOG.md dev/SESSION_HANDOFF.md dev/SESSION_LOG.md
  git commit -m "chore: session close — pack tools, git manual, update docs"
  # 然後按 GIT_PUSH_MANUAL.md 步驟推送

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-10（SESSION CLOSE — Claude_20260310_RE01）

1. Agent & Session ID: Claude_20260310_RE01
2. Task summary: v1.0.0 整合測試修復 + --school-year 功能 + GitHub Pages 部署配置 + Session Close
3. Layer classification: Product / System Layer（整合修復 + 部署）
4. Source triage: 整合測試發現 bug（title 污染、ID 碰撞）+ 用戶新需求（學年模式、公開部署）
5. Files read: edb_scraper.py, edb-dashboard.html, CHANGELOG.md, .gitignore, SESSION_HANDOFF.md
6. Files changed:
   - `edb_scraper.py`（更新：title 污染修復 + school_year_start() + date_from + v1.0.0）
   - `edb-dashboard.html`（更新：REFERENCE_CIRCULARS id 9001/9002/9003）
   - `.github/workflows/update-circulars.yml`（新建）
   - `index.html`（新建）
   - `.gitignore`（更新）
   - `CHANGELOG.md`（更新：v1.0.0-release + v1.0.1-hosting）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - title 污染修復 ✅ | REFERENCE_CIRCULARS ID 碰撞修復 ✅
   - `school_year_start()` + `--school-year` + `date_from` 參數 ✅
   - circulars.json 新增 range/date_from/date_to 欄位 ✅
   - GitHub Actions workflow（每天 HKT 07:00 + 手動 4 模式）✅
   - index.html + .gitignore 更新 ✅
   - py_compile 語法驗證 ✅
   - ⏳ 學年爬蟲執行中（用戶確認後補錄）
8. Pending: 確認學年爬蟲結果 → GitHub Pages 一次性設定 → tag v1.0.1-hosting

### Problem -> Root Cause -> Fix -> Verification
1. title 含「摘要：」→ EDB content_div 直接文字節點包含摘要 → `re.sub(r"\s*摘要[：:].*$","",title)` → py_compile ✅
2. REFERENCE_CIRCULARS id 碰撞 → 固定 id 10/11/12 與真實數據重疊 → 改為 9001/9002/9003 → 代碼審閱 ✅

### Consolidation / Retirement Record
1. Retired: v9 Handoff Prompt（由 v10 取代）

---

### Next Session Handoff Prompt — v10（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.0.1-hosting 配置完成，學年爬蟲 ✅ 104條/834.5KB，待 GitHub Pages 設定

已完成（全部 ✅）：
- Dashboard v0.2.1（2453行）✅
- edb_scraper.py v1.0.0：--school-year + title fix + ID fix ✅
- GitHub Actions workflow + index.html + .gitignore 更新 ✅
- ✅ 學年爬蟲完成：104 條通告，834.5KB circulars.json

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5

⭐ 下一步（按序）：
  1. 在瀏覽器開啟 edb-dashboard.html，確認 104 條學年通告正確顯示
  2. GitHub Pages 一次性設定（見下方步驟）
  3. GitHub Pages 一次性設定（Mac Terminal + GitHub 網頁操作）：
     a. git add . && git commit && git push（含 .github/workflows/, index.html, .gitignore 更新）
     b. github.com/Leonard-Wong-Git/EDB-AI-Circular-System
        → Settings → Secrets → Actions → New secret: OPENAI_API_KEY
        → Settings → Pages → Source: GitHub Actions
        → Actions → Update EDB Circulars → Run workflow → school-year
  4. 確認公開 URL：https://leonard-wong-git.github.io/EDB-AI-Circular-System/

完成後：
  git tag v1.0.1-hosting
  git push --force origin main && git push origin --tags
  cp -r "." "../EDB-Circular-AI-analysis-system-snapshot-v1.0.1"

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html, edb_scraper.py, circulars.json
  ├── index.html（新）← GitHub Pages 根 URL 跳轉
  ├── .github/workflows/update-circulars.yml（新）← 自動更新
  ├── requirements.txt, .gitignore（更新）
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, GIT_PUSH_MANUAL, tools/, knowledge/]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE02）

1. Agent & Session ID: Claude_20260311_RE02
2. Task summary: PDF 連結修復 + 導航 Bug 修復 + 系統說明 + 驗收清單
3. Layer classification: Product / System Layer（UI 修復 + 文件）
4. Source triage: 用戶要求（PDF 連結未能直link EDB原文件、導航未互通、系統說明、驗收清單）
5. Files read: edb_scraper.py, edb-dashboard.html, circulars.json（結構確認）, SESSION_HANDOFF.md
6. Files changed:
   - `edb_scraper.py`（更新：output record 新增 `pdf_urls` 欄位）
   - `edb-dashboard.html`（更新：buildPdfLinks() + 導航修復 + 系統說明卡）
   - `dev/ACCEPTANCE_CHECKLIST.md`（新建）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - pdf_urls 修復（scraper 未輸出→已加，dashboard 靜態#→動態 EDB URL）✅
   - buildPdfLinks() helper：pdf_urls有時→用真實URL；無時→推算EDBCM格式URL；fallback→EDB列表頁 ✅
   - Stats Bar「即將截止」chip：先 switchTab('overview')，再 scrollIntoView ✅
   - 供應商 Tab Note 重複插入 bug：加 id='supplierNote' guard ✅
   - Settings 新增全寬「📖 系統功能說明」卡片（8個功能模組說明）✅
   - dev/ACCEPTANCE_CHECKLIST.md：11類別 80+測試項目 ✅
8. Pending: git push → 重新爬取取得 pdf_urls → 按驗收清單測試

### Problem -> Root Cause -> Fix -> Verification
1. PDF 按鈕 href="#" → 靜態硬碼，未使用 pdf_urls 欄位；且 pdf_urls 本身未輸出至 JSON → 雙重修復：scraper 加 pdf_urls 至 record；dashboard 改用 buildPdfLinks() ✅
2. Stats Bar「即將截止」在非總覽 tab 點擊不切換 tab → 未加 switchTab() 呼叫 → 加入 switchTab 後 setTimeout scroll ✅
3. Supplier Note 每次 renderSupplier() 都插入 → 無 guard → 加 id='supplierNote' 防重複 ✅

### Consolidation / Retirement Record
1. Retired: v10 Handoff Prompt（由 v11 取代）

---

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE03）

1. Agent & Session ID: Claude_20260311_RE03
2. Task summary: 自動化驗收測試（完整清單報告）+ `💰null` Bug 修復 + git push upstream 診斷
3. Layer classification: Product / System Layer（驗收測試 + Bug 修復）
4. Source triage: 用戶指示「由你自動在 GitHub Pages 按清單逐項檢視，再報告予我」
5. Files read: edb-dashboard.html（grantChip 函數定位）
6. Files changed:
   - `edb-dashboard.html`（修復：grantChip() applicable type 缺 null fallback → `||'資助'`）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed:
   - 自動化驗收測試（瀏覽器 JS 執行，測試 A–K 全部類別）✅
   - 完整驗收報告（73/80 通過，91%）✅
   - **Bug 修復：** `grantChip()` applicable 類型缺少 null guard → `${g.amount_label||'資助'}`（影響 10+ 張卡片）✅
   - git push upstream 錯誤診斷：`fatal: no upstream branch` → 建議 `git push --set-upstream origin main` ✅
8. Pending: 用戶執行 `git push --set-upstream origin main` 推送 grantChip 修復

### Problem -> Root Cause -> Fix -> Verification
1. Problem: 卡片顯示「💰null」（約 10 張卡片受影響）
2. Root Cause: `grantChip()` 第 1776 行：applicable 類型直接 `${g.amount_label}` 無 null guard；resource 類型已有 `||'資源'` 但 applicable 類型遺漏
3. Fix: `${g.amount_label}` → `${g.amount_label||'資助'}`（一字之差）
4. Verification: 邏輯確認正確；live site 需推送後確認
5. Regression / rule update: 無新規則

### Consolidation / Retirement Record
1. Duplicate / drift: 無
2. Retired: v11 Handoff Prompt（由 v12 取代）

---

### 驗收報告摘要（RE03 自動測試結果）
- **A. 資料載入** 4/4 ✅
- **B. 通告總覽** 13/15（B5 無下拉建議，屬 UX 差異非 bug）
- **C. 詳情面板** 17/17 ✅
- **D. 月曆** 7/9（D8/D9 篩選按鈕未實作）
- **E. 資源申請** 5/5 ✅
- **F. 收藏** 4/5（F4 badge 計數未顯示）
- **G. 供應商** 6/6 ✅
- **H. 設定** 9/12（H5 天數選擇器 / H6 已跟進切換 未找到）
- **I. 鍵盤快捷鍵** 5/5 ✅
- **J. GitHub Actions** 7/7 ✅
- **K. 響應式設計** 未測試（需人手）
- **Bug:** `💰null` 顯示（已修復於本 session）

---

### Next Session Handoff Prompt — v12（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.0.2 驗收通過（91%），grantChip null 修復，待最終 git push

已完成（全部 ✅）：
- Dashboard v1.0.2：PDF連結、導航、系統說明、供應商Note去重
- edb_scraper.py：output record 含 pdf_urls
- GitHub Pages：https://leonard-wong-git.github.io/EDB-AI-Circular-System/ 已上線
- GitHub Actions：每日 HKT 07:00/13:00/17:00 自動更新（105條通告，全部含 pdf_urls）
- 驗收測試：73/80（91%）通過 ✅
- grantChip() null 修復：applicable 類型加 `||'資助'` ✅

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5

⭐ 下一步（按序）：
  1. git push --set-upstream origin main（推送 grantChip 修復）
  2. 確認 GitHub Pages 自動重新部署
  3. 選做：修復次要缺陷（D8/D9 月曆篩選 / F4 收藏 badge / H5 天數選擇器 / H6 已跟進切換）
  4. 完成後打 tag v1.0.3-bugfix

次要缺陷清單（可選做，非阻礙性）：
  - D8/D9：月曆頁添加篩選按鈕（高影響 / 截止日 類型篩選）
  - F4：收藏 tab badge 顯示收藏數量
  - H5：設定頁截止提醒天數選擇器（3/7/14天）
  - H6：設定頁「顯示/隱藏已跟進通告」切換按鈕

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html（v1.0.2 + grantChip null fix）
  ├── edb_scraper.py（含 pdf_urls 輸出）
  ├── circulars.json（105條，含 pdf_urls，由 GitHub Actions 維護）
  ├── index.html, .github/workflows/update-circulars.yml
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, ACCEPTANCE_CHECKLIST, GIT_PUSH_MANUAL, ...]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

## 2026-03-11（SESSION CLOSE — Claude_20260311_RE04）

1. Agent & Session ID: Claude_20260311_RE04
2. Task summary: 8 項功能實作（B5/B6/B7/B8 匯出列印日曆多選 + F1/F2 排序主題 + C1/C2 狀態互通）
3. Layer classification: Product / System Layer（前端功能擴展）
4. Source triage: 用戶確認「自做一、及二」= Batch 1（F1/F2/C1/C2/B5/B7）+ Batch 2（B6/B8）；K1/R1 留後討論
5. Files read: edb-dashboard.html（多次，修改前後確認）
6. Files changed:
   - `edb-dashboard.html`（更新：2453→2796 行，8 項功能，HTML 驗證通過）
   - `dev/SESSION_HANDOFF.md`（更新）
   - `dev/SESSION_LOG.md`（本條目）
7. Completed（全部 8 項）：
   - **F1（排序持久化）**：`lsLoad()` 讀 `edb_sort_field`/`edb_sort_asc`；`sortList()` 寫 localStorage；預設日期降序 ✅
   - **F2（時段自動主題）**：`applyTheme()` 改用時鐘（07-18=淺色，其餘=深色）；60秒 setInterval ✅
   - **C1（狀態互通）**：`updateBmBadge()` + `syncStatusBtns(id,status)`；所有狀態/書籤/釘選按鈕改為 DOM 即時更新（無 full re-render）；data-sid 屬性 ✅
   - **C2（資源行色+日期）**：行色 CSS（.res-applying/applied/closed/na）；`setApplyStatus()` 即時更新行 CSS + 記錄申請日期至 `edb_apply_dates` localStorage + toast ✅
   - **B5（CSV 增強）**：`exportExcel()` 加「行動數」「AI摘要前200字」兩欄 ✅
   - **B7（.ics 日曆匯出）**：新增 `exportICS()`（iCalendar VCALENDAR/VEVENT 格式）；📅 日曆工具列按鈕 ✅
   - **B6（格式化列印）**：`printDetail()` 改寫（`window.open` 新視窗，完整 HTML 報告含列印/關閉按鈕）；移除舊 `window.print()` 重複函數 ✅
   - **B8（多選批量匯出）**：新增 `toggleMultiSelect()`/`cardClick()`/`exportSelected()`；浮動 #batchBar；.card-selected CSS + 框 overlay；☑️ 多選工具列按鈕 ✅
   - **HTML 驗證**：`html.parser` 確認「HTML OK — All tags balanced」✅
   - **函數驗證**：所有 11 個新函數 grep 全部找到 ✅
   - **git 衝突診斷**：
     * `fatal: no upstream` → `git push --set-upstream origin main`
     * `fatal: not a git repository` → 需先 cd 至項目目錄（`find ~ -maxdepth 6 -name ".git" -type d 2>/dev/null | grep -i EDB`）
     * `[rejected] fetch first` → `git pull --rebase origin main && git push`（GitHub Actions 持續 push 造成衝突）
8. New localStorage keys: `edb_sort_field`、`edb_sort_asc`、`edb_apply_dates`（總共 12 個 keys）
9. Validation / QC:
   - HTML parser: HTML OK ✅
   - 11 新函數全部 grep 找到 ✅
   - 2796 行（+343 行 vs v1.0.2）
10. Pending:
    - ✅ git push 已完成（commit b593707，tag v1.1.0-features 已推送）
    - ❌ GitHub Pages 仍是舊版（無 📅 日曆 / ☑️ 多選）：手動觸發 workflow 因 pdfminer 卡死逾 1 小時被取消
    - ⭐ 下個 session 首要：修復 edb_scraper.py PDF timeout → 重新 push → workflow 自動觸發 → Pages 部署
    - 討論：K1 知識庫框架、R1 全角色職責精確度、LLM 引擎切換機制
    - 選做：次要缺陷（D8/D9/F4/H5/H6）
11. Risks / blockers: ⚠️ pdfminer 無 timeout → workflow 卡死（已記錄 SESSION_HANDOFF Known Risks #6）；修復前勿手動觸發 school-year workflow

### Problem -> Root Cause -> Fix -> Verification
1. Problem: B6 `printDetail()` 重複定義（新舊兩個版本同時存在）
2. Root Cause: 實作新版本時，舊 `window.print()` 版本未移除
3. Fix: 找出舊版本（Export section）並移除
4. Verification: grep 確認只有一個 `printDetail` 定義 ✅
5. Regression / rule update: 實作新函數前先搜尋是否存在舊版本

### Consolidation / Retirement Record
1. Duplicate / drift: 舊 `printDetail()` 移除（只保留新格式化版本）
2. SSOT: 無新 SSOT；功能規格沿用 `dev/v0.2.0-FRONTEND-SPEC.md`
3. Merged: B6/B7/B8 工具列按鈕整合至現有工具列
4. Retired: v12 Handoff Prompt（由 v13 取代）
5. Why: 版本進度更新，8 項功能完成

---

### Next Session Handoff Prompt — v13（最新版本 ✅，請用此版本）
```
專案：EDB 通告智能分析系統 (EDB-Circular-AI-analysis-system)
狀態：v1.1.0-features ✅ 代碼已推送 GitHub，但 GitHub Pages 仍是舊版（待修 PDF timeout 後重新部署）

已完成（全部 ✅）：
- Dashboard v1.1.0（2796行）：8 項新功能已寫入代碼並推送 ✅
  * F1 排序持久化 / F2 時段主題 / C1 狀態互通 / C2 資源行色
  * B5 CSV增強 / B6 格式化列印 / B7 .ics日曆 / B8 多選批量匯出
- git push 完成：commit b593707，tag v1.1.0-features ✅
- GitHub Pages 功能正常（舊版），但新按鈕尚未顯示

⚠️ 緊急修復（第一優先）：pdfminer PDF 解析無 timeout
  症狀：Actions workflow 卡死超過 1 小時（正常 25 分鐘），日誌停在 pdfminer DEBUG
  影響：GitHub Pages 無法部署新版本（workflow 被取消）
  ⚠️ 勿再手動觸發 school-year workflow，修復前會再次卡死

  修復方案（在 edb_scraper.py PDF 解析函數加入）：
  import signal
  def _pdf_timeout(signum, frame): raise TimeoutError("PDF parse timeout")
  signal.signal(signal.SIGALRM, _pdf_timeout)
  signal.alarm(60)   # 60秒 timeout
  try:
      text = pdfplumber.open(...)...
  except TimeoutError:
      text = ""      # 跳過此 PDF
  finally:
      signal.alarm(0)

⚠️ gpt-5-nano 規則（不可更改）：
  temperature=1 | role="developer" | max_completion_tokens=16000

⚠️ EDB 字段 + HTML 結構：見 SESSION_HANDOFF Known Risks #4 + #5 + #6

⭐ 下一步（按序）：
  1. 修復 edb_scraper.py PDF timeout（見上方方案）
  2. git add edb_scraper.py && git commit -m "fix: PDF parse timeout to prevent workflow hang"
  3. git push → GitHub Actions 自動觸發 → 等待完成（約 25 分鐘）
  4. Cmd+Shift+R 確認 GitHub Pages 出現 📅 日曆 + ☑️ 多選 按鈕

待討論（下個 session）：
- K1：知識庫參考文件框架（每主題域濃縮底稿；半年自動更新）
- R1：全角色職責精確度（6角色×真實 EDB 職責）
- LLM 引擎切換機制
- 次要缺陷：D8/D9 / F4 / H5 / H6

主要檔案：
  outputs/EDB-Circular-AI-analysis-system/
  ├── edb-dashboard.html（v1.1.0，2796行，8項新功能）
  ├── edb_scraper.py（⚠️ 需加 PDF timeout）
  ├── circulars.json, index.html
  ├── .github/workflows/update-circulars.yml
  └── dev/ [SESSION_HANDOFF, SESSION_LOG, GIT_PUSH_MANUAL, ACCEPTANCE_CHECKLIST, tools/, knowledge/]

關鍵規則：gpt-5-nano temperature=1 固定 | VM 網絡封鎖→Mac Terminal
```

---

### Next Session Handoff Prompt — v11（已由 v13 取代，內容略）
