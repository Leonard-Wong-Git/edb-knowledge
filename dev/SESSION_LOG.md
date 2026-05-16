# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-16 Session 109 — PROJECT_MASTER_SPEC.md 建立 + 專案目錄遷移

- **ID:** Claude_20260516_0841
- **Summary:** 兩部分。(1) 用戶準備交畀另一個 AI agent 接手，依 AGENTS.md §10 建立 `dev/PROJECT_MASTER_SPEC.md`（跨 agent 交接權威知識庫，§1 啟動序列必讀）；失敗教訓由 general-purpose agent 提煉 `dev/archive/` Q1+Q2 全歷史。(2) 將整個專案由 `/Users/leonard/Downloads/Claude-edb-knowledge` 遷至 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（同磁碟 `mv` rename，931MB 全量含 .git/node_modules/.venv），並同步更新所有舊絕對路徑引用。亦建立 `.claude/launch.json`（backend:8787 + frontend-static:8080，用戶選擇暫不啟動）。
- **Changed:** `dev/PROJECT_MASTER_SPEC.md`（新增 + §A.5 路徑）, `dev/CODEBASE_CONTEXT.md`（directory map + AI Maintenance Log）, `dev/DOC_SYNC_CHECKLIST.md`（+3 rows 含 relocation）, `dev/SESSION_HANDOFF.md`（Start Checklist +1 / User Environment 新路徑 / Session Close Checklist 新路徑 / Last Session Record / 移除 Session 105）, `AGENTS.md`（header line 1 + §13 三範例新路徑）, `bump_version.py` + `dev/vault/dedup_check.py`（印出/docstring 路徑提示）, `.claude/launch.json`（新增）
- **Done:**
  - ✅ **[PROJECT_MASTER_SPEC §A–§G]** 目標/scope/不變量 + 功能要求 + 已架構系統地圖 + 13 條高效方法 + 9 類必避失敗教訓 + 10 條鎖定決策 + 起手指南
  - ✅ **[Governance wiring]** §1 啟動序列第 4 讀；DOC_SYNC rows；CODEBASE_CONTEXT 雙更新
  - ✅ **[專案遷移]** commit 還原點 `4d54b2a` → rmdir 空 Draft → `mv` 來源成為 Draft；驗證 931MB 全量 / git 歷史+remote 完好 / 舊路徑已消失 / 工作區乾淨
  - ✅ **[路徑 doc-sync]** AGENTS.md header+§13、SESSION_HANDOFF User Environment+Close Checklist、PROJECT_MASTER_SPEC §A.5、bump_version.py+dedup_check.py 提示 全部改為含空格新路徑（雙引號包覆）；功能性腳本全部用相對路徑、不受影響
- **QC:** §4a check trigger=False；mv 後 `git rev-parse --show-toplevel` = 新路徑、HEAD `4d54b2a`、`git status` clean、remote `origin` 不變；grep 確認剩餘舊路徑只在 `dev/archive/` + `dev/SESSION_LOG.md` 歷史條目（正常，不改寫歷史）；`.claude/launch.json` 用相對 cwd 不受遷移影響
- **Pending（用戶 Terminal，新路徑）:** Git push（含遷移後路徑更新 commit）；用戶 review PROJECT_MASTER_SPEC 內容
- **Next:** 1. Mobile UI Phase 2 餘下（index/q/t-purchase/#guidelines）；2. Q&A admin login backlog；3. HKEAA source family 補完

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| New cross-agent handoff knowledge doc added | CODEBASE_CONTEXT Directory Map + AI Maintenance Log；DOC_SYNC registry row；SESSION_HANDOFF/LOG | ✓ Done |
| Long-term spec / locked decision / architecture invariant change | dev/PROJECT_MASTER_SPEC.md（新建，§A–§G）；CODEBASE_CONTEXT Key Decisions（無方向轉變，N/A） | ✓ Row added |
| Governance bootstrap-adjacent (Mandatory Start Checklist + §1 read list) | SESSION_HANDOFF Start Checklist；CODEBASE_CONTEXT | ✓ Done |
| Project relocation / repo absolute-path change | AGENTS.md header+§13；SESSION_HANDOFF User Environment+Close Checklist；PROJECT_MASTER_SPEC §A.5；bump_version.py+dedup_check.py 提示；DOC_SYNC row；SESSION_LOG/HANDOFF | ✓ Done（row added + applied） |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 專案已遷移：repo root 現為 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須用雙引號包覆絕對路徑）。舊路徑 ~/Downloads/Claude-edb-knowledge 已不存在。

Current objective and progress state:
- Session 109 (2026-05-16) 兩部分：(1) 建立 dev/PROJECT_MASTER_SPEC.md（跨 agent 交接權威知識庫，已接入 §1 第 4 讀 + Mandatory Start Checklist 第 4 項）；(2) 整個專案 mv 遷至新路徑並同步所有舊絕對路徑引用 + 建立 .claude/launch.json（暫不啟動）。
- git：commit 4d54b2a（遷移前還原點）+ 88205dc（遷移後路徑同步）已 push 上 origin/main；工作區乾淨。
- 商品狀態（以 SESSION_HANDOFF Current Baseline 為準）：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources / Mobile UI app.html search ✅ 其餘頁面 mobile content 未做。

Pending tasks in priority order:
1. Mobile UI Phase 2 餘下：index.html mobile landing / q.html mobile inline / t-purchase.html mobile form / app.html#guidelines mobile-native render
2. Q&A backlog：admin login「34 問題」audit；admin login security password gate（短期）
3. HKEAA / 考評局 source family 補完（Session 105 SBA query 揭發 vault gap）
4. 線上手動 sanity 8 條 query 結果驗證（user 自跑後 paste 結果）
5. g21/g22/g33 直連 PDF 補完 + 5 個 stat xlsx 下載上 vault（user browser）

Key files changed in this session:
- dev/PROJECT_MASTER_SPEC.md（新增 + §A.5 新路徑）
- dev/CODEBASE_CONTEXT.md（directory map + AI Maintenance Log）
- dev/DOC_SYNC_CHECKLIST.md（+3 project-specific rows 含 relocation）
- dev/SESSION_HANDOFF.md（Start Checklist +1 / User Environment + Close Checklist 新路徑 / Last Session Record / 移除 Session 105）
- AGENTS.md（header line 1 + §13 三範例 新路徑）
- bump_version.py + dev/vault/dedup_check.py（路徑提示字串）
- .claude/launch.json（新增 — backend:8787 + frontend-static:8080）
- dev/SESSION_LOG.md（Session 109 entry）

Known risks / blockers / cautions:
- ⚠️ Repo 路徑含空格 → 所有 cd / 腳本指令必須雙引號包覆絕對路徑（AGENTS.md §13 已更新範例）
- ⚠️ 舊路徑肌肉記憶：勿再用 ~/Downloads/Claude-edb-knowledge（已不存在）
- MemPalace：mempalace.yaml/entities.json 用相對路徑不受影響；但 `mine .` / sync 須在新路徑跑；shared palace `/Users/leonard/mempalace/palace` 在 repo 外不受影響
- Cowork sandbox egress allowlist 不含 edb.gov.hk / edb-knowledge.onrender.com / apps.apple.com → 線上驗證需用戶 Terminal / browser
- Render free tier cold start ~30s after 15min idle
- index.html / q.html / t-purchase.html mobile reload 仲一片空白（Phase 2 未做）
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- PROJECT_MASTER_SPEC 只記結構/不變量；事實條數/版本/mobile 進度一律以 SESSION_HANDOFF Current Baseline 為準

Validation status:
- PASS: 遷移完整（931MB / git 歷史+remote / clean tree）；所有舊絕對路徑引用已更新；PROJECT_MASTER_SPEC 接入 §1；§4a 無需封存；commit 4d54b2a + 88205dc 已 push origin/main
- PENDING: 用戶 review PROJECT_MASTER_SPEC 內容是否需補充

Post-startup first action: 確認在新路徑 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（含空格須雙引號），然後詢問 Leonard：先 review PROJECT_MASTER_SPEC（特別 §E 失敗教訓有冇遺漏），抑或直接開始 Mobile UI Phase 2 餘下頁面（index/q/t-purchase/#guidelines）。
```

---

## 2026-05-05 Session 108 — Mobile UI Phase 2 ship（app.html search content）

- **ID:** Claude_20260505_0001
- **Summary:** Mobile reload 後見一片空白（Phase 1 已 active hide React #root 但無 main content）。今 session ship Phase 2 嘅 app.html 部分：mobile.js 加 buildAppShell()，動態 inject hero gradient + 大 search bar + result cards + bottom sheet，並接駁 backend `/api/search/combined` 真實 API。#guidelines tab 暫用 fallback 露 React panel（下節做 mobile-native version）。Index/q/t-purchase 嘅 mobile content 留下節。
- **Changed:** `mobile.js`（+ buildAppShell + runSearch + renderResults + openSheet + sourceLabel/sourceIcon helpers + #guidelines fallback override）
- **Done:**
  - ✅ **[Mobile app.html shell]** Hero gradient + minimal eyebrow + title + desc + search form；search submit 直接 hit `/api/search/combined`（top_k=8 / synthesize / topic_filter）
  - ✅ **[Result rendering]** Synthesis card（EDB 深綠 left-border）+ result cards（每張 source icon + label + content 3-line truncate + score + channel badge）；空白 / loading（3 dots pulse）/ error / 429 rate limit 全 state
  - ✅ **[Bottom sheet]** Tap card 開 sheet（90vh）見全文 + role chip + 「🔗 看 EDB 原文」CTA；backdrop tap 關
  - ✅ **[Source helpers]** SOURCE_LABEL map 12 條 + sourceIcon 自動分類（sag/coa → 📗📘 / g* → 📋 / role_facts → ✅ / edbc → 📄）
  - ✅ **[#guidelines fallback]** mobile.css hide #root rule 覆寫 inline `display:block !important` + padding-bottom 80px 避被 tab bar 遮
- **QC:** mobile.css scope guard 維持 desktop 不影響；buildAppShell 只在 `app.html` 且 `hash !== '#guidelines'` 跑；React #root 保留 hidden 避免重複 layout
- **Pending（用戶 Terminal 已執行）:**
  - Git push commit 已上 GitHub Pages
  - Mobile reload 確認 Phase 2 search work
- **Next:** 1. Phase 2 餘下：index.html mobile landing / q.html mobile inline / t-purchase.html mobile form / app.html#guidelines mobile-native render；2. Q&A backlog（admin login 34 問題 audit + password gate）；3. HKEAA source family 補完

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Mobile UI Phase 2 partial ship (app.html) | SESSION_HANDOFF Open Priorities + Last Session Record | ✓ Done |
| Backend API integration (mobile fetch) | mobile.js BACKEND_URL inline | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 108 (2026-05-05) ship Mobile UI Phase 2 嘅 app.html 部分：buildAppShell + search submit 接 backend `/api/search/combined` + result cards + bottom sheet
- Mobile UI 進度：app.html ✅ search work；index.html / q.html / t-purchase.html / app.html#guidelines 仲未 ship mobile content
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. Phase 2 餘下：index.html mobile landing / q.html mobile inline / t-purchase.html mobile form / app.html#guidelines mobile-native render
2. Q&A backlog：admin login 34 問題 audit；admin login security password gate（短期）
3. HKEAA / 考評局 source family 補完（Session 105 SBA query 揭發 vault gap）
4. 線上手動 sanity 8 條 query 結果驗證（user 自跑後 paste 結果）
5. 用 6 條 Tado URL 做 mobile UI 細節 polish（mobile.css visual reference）

Key files changed in this session:
- mobile.js（+ buildAppShell / runSearch / renderResults / openSheet / sourceLabel + sourceIcon / #guidelines fallback）
- dev/SESSION_LOG.md（Session 108 entry）
- dev/SESSION_HANDOFF.md（Last Session Record / Open Priorities 更新）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb.gov.hk / edb-knowledge.onrender.com / apps.apple.com → 線上驗證需用戶 Terminal / browser
- Render free tier cold start ~30s after 15min idle → mobile 第一次 search 可能等
- index.html / q.html / t-purchase.html mobile reload 仲一片空白（main content 未 render）
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB

Validation status:
- PASS: app.html mobile shell 結構正確；search form submit + backend integration code 完成
- PENDING: 用戶 mobile reload 確認 search → result → sheet flow work；如有 visual bug paste screenshot 即修
- PENDING: index.html / q.html / t-purchase.html mobile content 未 ship

Post-startup first action: 詢問 Leonard：app.html mobile search test 結果如何，下一輪做 index.html mobile landing 抑或 #guidelines mobile-native 抑或其他方向。
```

---

## 2026-05-03 Session 107 — UX revisions（index + app + #guidelines）+ Mobile UI Spec + Phase 1 ship

- **ID:** Claude_20260503_0004
- **Summary:** 連續處理 user 三批修訂指示（index.html 8 點 + app.html 9 點 + #guidelines 修訂 + Q&A）+ 寫 Mobile UI Spec v1.1 + ship Phase 1（mobile.css + mobile.js + 4 HTML link）。Mobile UI 採用 Tado-inspired + Pantone Cloud Dancer 2026 + system mode dark/light auto，Phase 2（page-by-page mobile content render）下節進行。
- **Changed:** `index.html`, `app.html`, `q.html`, `t-purchase.html`, `mobile.css`（新增）, `mobile.js`（新增）, `dev/MOBILE_UI_SPEC_v1.md`（新增 + Tado URL refs）
- **Done:**
  - ✅ **[index.html UX 8 點]** CTA 改「搜尋／文件庫」+ 加「核心功能」anchor / Channel tags 改實意思（已核實資料 / 來源文件 / 合併搜尋）/ 通告分析改「EDB 通告分析系統 簡介」inline tag 鏈接 EDB-AI-Circular-System / del「全部免費使用」/ Step 04 disclaimer / 加資料覆蓋 K1-S6 + EDB 為準聲明 / footer v2.3
  - ✅ **[app.html UX 9 點]** mobile tab bar 改 admin-only / logo「K1 知識平台」改「知識平台」/ nav badge sync / hero「問一句」改「查找教育局各項有根有據的政策答案」/ H2「三大核心功能」（channels）+「三步取得有根有據答案」（steps）各歸位 / 全部來自 EDB 網站官方文件 / footer 重組（免責聲明 + 設計及維護同行）/ del 18450 fake count / 平台介紹 channels[2] sync 至「EDB 通告分析系統 簡介」+ external link
  - ✅ **[#guidelines 修補]** 分類欄 active state 改用 EDB 深綠 inline style（避 Tailwind class race）/ 學習階段 filter 拓展至全 category（不再限「課程」）/ steps grid gap 對齊 + width:100%
  - ✅ **[Mobile UI Spec v1.1]** dev/MOBILE_UI_SPEC_v1.md 完成；Section 9 user 6 答案 record；Section 10 Tado URLs library 記 6 條 reference + Pantone Cloud Dancer 2026 + Award trends
  - ✅ **[Mobile UI Phase 1 ship]** `/mobile.css` 完整 design system（EDB green + Cloud Dancer + atmospheric + dark mode auto via prefers-color-scheme）；`/mobile.js`（detection ≤640px OR mobile UA / role picker first-run overlay / placeholder rotate 8 條 / cross-page tab bar）；4 HTML head 加 link
  - ✅ **[Q&A 5 條答覆]** 18450 fake count 確認刪 / 34 問題待 admin login audit / 匯出 admin only 保留 / 8 角色 wrap include all_roles / Online security 短期建議 password gate
- **QC:** TypeScript check N/A（無動 backend）；mobile.css scope guard `@media (max-width: 640px)` 確保 desktop 唔受影響；mobile.js detection guard early return on desktop
- **Pending（用戶 Terminal 執行）:**
  - Final git push 含 Mobile UI Phase 1 + UX revisions + spec doc
  - Mobile reload 確認 role picker / tab bar / dark mode 正常
- **Next:** 1. Phase 2 page-by-page mobile content render（app.html 核心 search hero + result card + bottom sheet）；2. 6 條 Tado URL Phase 2 implementation 時參考；3. Q&A backlog（admin login security / 34 問題 audit）

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| UX revisions (index + app + #guidelines) | SESSION_HANDOFF Last Session Record / Open Priorities | ✓ Done |
| New mobile UI infrastructure | mobile.css + mobile.js + 4 HTML head link + spec doc | ✓ Done |
| Tado reference URLs | dev/MOBILE_UI_SPEC_v1.md Section 10 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 107 (2026-05-03) ship UX revisions（index 8 點 / app 9 點 / #guidelines 修補）+ Mobile UI Spec v1.1 + Phase 1 ship（mobile.css + mobile.js + 4 HTML link）
- Mobile UI：Tado-inspired + Pantone Cloud Dancer 2026 + dark mode auto；3 個 bottom tab（搜尋 / 文件庫 / 平台介紹）；first-run role picker
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. Mobile UI Phase 2：page-by-page mobile content render（app.html 核心 search hero + result card + bottom sheet；index/q/t-purchase 對應 mobile content）
2. 用 6 條 Tado URL 做 Phase 2 visual reference（dev/MOBILE_UI_SPEC_v1.md Section 10）
3. Q&A backlog：admin login「34 問題」audit；admin login security password gate（短期）
4. HKEAA / 考評局 source family 補完（Session 105 SBA query 揭發 vault gap）
5. 線上手動 sanity 8 條 query 結果驗證（user 自跑後 paste 結果）

Key files changed in this session:
- index.html / app.html / q.html / t-purchase.html（4 HTML 加 mobile.css + mobile.js link；index 8 點 UX；app 9 點 UX；#guidelines CSS fix）
- mobile.css（新增 — 完整 mobile design system）
- mobile.js（新增 — detection / role picker / tab bar / placeholder rotate）
- dev/MOBILE_UI_SPEC_v1.md（新增 v1.1 + Tado URLs + user 6 答案）
- dev/SESSION_LOG.md（Session 107 entry）
- dev/SESSION_HANDOFF.md（Last Session Record / Open Priorities）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb.gov.hk / edb-knowledge.onrender.com / apps.apple.com → 線上驗證需用戶 Terminal / browser
- Mobile UI Phase 2 未做 — Phase 1 ship 後 mobile reload 仲見唔到 main content（hero / search / result list 仲未 render），只見 role picker overlay + bottom tab bar
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB

Validation status:
- PASS: mobile.css scope guard `@media (max-width: 640px)` 確保 desktop 唔影響
- PASS: mobile.js detection guard early return on desktop
- PASS: 4 HTML head 加 link 完成
- PENDING: 用戶 mobile reload 確認 role picker / tab bar / dark mode

Post-startup first action: 詢問 Leonard：Phase 2 mobile content render（app.html 核心 search 開始）抑或揀其他方向。
```

---

## 2026-05-03 Session 106 — 數據自動同步 + 版本號全平台對齊（B + A 合併 ship）

- **ID:** Claude_20260503_0003
- **Summary:** 一氣完成 OP #1（版本號對齊）+ OP #2（首頁同平台介紹數據自動同步）：三層 _meta 加 stats block 做 single source of truth；index.html 加 inline JS fetch knowledge.json 動態填數；app.html PlatformIntroPanel statTargets 改用 stats prop；README badge / footer / CHANGELOG / 內文 hardcoded counts 全 sync v2.3.0 + 792 facts；CHANGELOG 加 v2.3.0 entry。Mobile UI 設計（OP #3）留下節做。
- **Changed:** `knowledge.json`, `role_facts.json`, `dev/knowledge/role_facts.json`, `README.md`, `CHANGELOG.md`, `index.html`, `app.html`
- **Done:**
  - ✅ **[三層 _meta.stats block]** 加 `stats: {facts:792, chunks:10736, sources:120, guidelines:39, topics:7}` single source of truth；description 由「1,001 事實」改為「792 條已核實事實（Session 102 dedup 由 1,001 → 792）」
  - ✅ **[README 全文 sync]** badge v2.2.0 → v2.3.0；footer v2.2.0 → v2.3.0；全文「1,001 條」→「792 條」（4 處）；最後更新 2026-05-02 → 2026-05-03
  - ✅ **[CHANGELOG v2.3.0 entry]** 加新 entry 記錄 dedup + alias + query expansion + stats block
  - ✅ **[app.html sync]** INITIAL_DATA._meta v2.2.0 → v2.3.0 + updated 2026-05-03 + stats block；nav badge v2.2.0 → v2.3.0；PlatformIntroPanel statTargets 改用 `stats.metaStats?.{facts,chunks,guidelines,sources}` fallback hardcoded；stats useMemo expose `metaStats: data._meta?.stats`；channel desc 1,001 → 792
  - ✅ **[index.html dynamic stats]** stats-strip 4 個 stat-num 加 `data-stat="facts|chunks|topics|sources"`；hero-desc 同 feature-desc 內 hardcoded 1,001/7,788 改用 `<span data-stat>` 包住；meta description 同步 792/10,736；加 inline `<script>` fetch knowledge.json → 提取 _meta.stats → 填所有 `[data-stat]` 元素
- **QC:** TypeScript `npm run check` PASS 0 errors；grep audit 確認唯一 stale references 係 CHANGELOG 嘅 historical narrative（dedup note + v2.2.0 entry header），屬正常
- **Pending（用戶 Terminal 執行）:**
  - Git commit + push（B + A 一氣 ship）
  - reload GitHub Pages 確認首頁 + app.html 平台介紹數據已對齊 + version badge 變 v2.3.0
- **Next:** 1. C（手機端獨立 UI 設計）下節做；2. E sanity query 結果 paste 後即時診斷；3. HKEAA source family 補完（OP #4）

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Knowledge data structural cleanup (stats block) | knowledge.json + role_facts.json + dev/knowledge/role_facts.json _meta.stats | ✓ Done |
| Version bump v2.2.0 → v2.3.0 | README badge + footer + CHANGELOG + app.html INITIAL_DATA + nav badge | ✓ Done |
| Frontend behavior change (stats auto-sync) | index.html inline script + app.html PlatformIntroPanel | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 106 (2026-05-03) ship OP #1（版本號對齊）+ OP #2（數據自動同步）：三層 _meta.stats single source of truth；index.html dynamic fetch；app.html PlatformIntroPanel 改用 stats prop；README/CHANGELOG/footer/nav badge 全 sync v2.3.0 + 792
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. C（手機端獨立 UI 設計）— Detect mobile 時新 UI；可用 /design:refero-design 或 /ui-ux-responsive skill
2. HKEAA / 考評局 source family 補完（Session 105 SBA query 揭發 vault gap）
3. E 用戶手動跑 8 條 sanity query 驗證 paste 結果（找潛在 coverage gap）
4. g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit
5. 5 個 stat xlsx 下載 + 上 vault（user browser）

Key files changed in this session:
- knowledge.json + role_facts.json + dev/knowledge/role_facts.json（三層 _meta.stats block + description sync）
- README.md（badge + footer + 全文 hardcoded counts sync v2.3.0/792）
- CHANGELOG.md（加 v2.3.0 entry）
- index.html（stats-strip data-stat attributes + hero-desc + feature-desc dynamic span + inline script fetch）
- app.html（INITIAL_DATA._meta sync + PlatformIntroPanel statTargets dynamic + stats useMemo expose metaStats + nav badge v2.3.0）
- dev/SESSION_LOG.md + dev/SESSION_HANDOFF.md

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb.gov.hk → URL inspect 同 xlsx 下載需 user browser
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上 query 驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- index.html dynamic stats 用 fetch knowledge.json — file:// protocol 開 index.html 可能 CORS 失敗；fallback 用 hardcoded 數字（無 break）

Validation status:
- PASS: TypeScript npm run check 0 errors
- PASS: 三層 _meta.stats block 同步；description 一致
- PASS: README + CHANGELOG + footer + nav badge 全 v2.3.0
- PENDING: 用戶 reload GitHub Pages 確認首頁 + app.html 數據對齊 + version badge 顯示

Post-startup first action: 詢問 Leonard：手機 UI 設計 / HKEAA source / sanity query 結果 / 其他。
```

---
