# PROJECT MASTER SPEC — EDB 知識平台（K1 知識平台）

> **本文件定位（依 AGENTS.md §2 / §10）**
> 這是本專案的**長期穩定權威規格 + 跨 agent 交接知識庫**。
> 優先序：`SESSION_HANDOFF.md`（當前狀態）> `SESSION_LOG.md`（最新歷史）> `CODEBASE_CONTEXT.md`（穩定事實）> **本文件**（長期規格）> 其他。
> 當「當前狀態」與本文件衝突時，以 handoff / log 為準，並在 PERSIST 階段修正本文件 drift。
> 本文件回答四個問題：**(A) 系統要做什麼 (B) 已架構好什麼 (C) 什麼方法有效 (D) 什麼錯不能再犯**。
>
> 維護規則：本規格只記錄「長期穩定」的事實與教訓。會頻繁變動的數字（事實條數、chunks 數、版本號）以 `SESSION_HANDOFF.md` Current Baseline 為準，本文件只描述**結構與不變量**。

---

## A. 系統目標與定位

### A.1 一句話定位
為**香港中小學 / 幼稚園學校管理人員**提供一個**有根有據、可追溯到 EDB 官方文件原文**的政策知識查詢平台。每一條答案都必須能指回教育局官方來源 URL；系統的核心價值是**可信度與可追溯性**，不是 AI 自由發揮。

### A.2 核心目標（不變量）
1. **可追溯性優先於覆蓋率** — 寧可答「找不到」也不可給無來源、無法回溯 EDB 原文的答案。
2. **人工審核閘門** — policy facts（解讀性、角色相關指引）必須經人工 approve 才入 `role_facts.json`；statistical facts（客觀數字）可 auto-approve。LLM 不可自主發佈。
3. **單檔前端、零建構工具** — 前端維持 single-file HTML + CDN React，避免引入 build pipeline（鎖定決策，見 §F）。
4. **公開介面穩定** — `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md` 是對外契約 SSOT，schema 變動必須做 backend 相容性驗證。
5. **繁體中文為產品語言基準** — 使用者可見 UI 一律繁中；不對外暴露內部 design/dev/backend 指令；範本流程在未真正接通匯出前只可說「建立草稿／整理」。

### A.3 這個系統「不是」什麼（避免下一個 agent 誤判 scope）
- **不是** EDB 通告分析系統（Circular System）。那是**獨立 repo / 獨立專案**。本專案（K1）只負責知識策展，並提供 `knowledge.json` + `guidelines.json` 公開端點供 Circular System 自行 fetch。**K1 side 的整合工作 DONE — 不要 mount、不要修改 Circular System repo。**
- **不是** 一個讓 LLM 自動爬取並發佈事實的系統。Channel B（全 AI 副線）的 Circular System 整合**明確暫停**，待品質測試後再決定；Channel B 不會 auto-write `role_facts.json`。
- **不是** 限定「幼稚園 K1」scope（早期曾如此命名，Session 24 已移除該限制；「K1」現為產品代號，覆蓋 K1–S6）。

### A.4 使用者
- **一般使用者**：學校管理人員（校長、副校、主任、科主任、行政主任 EO 等），查政策、找指引文件、貼通告做分析。
- **Admin**：知識策展者（即 Leonard），負責候選事實審核（Channel A）、知識管理、Channel B prompt 調校。
- **下游系統**：EDB Circular System 透過公開 JSON 端點消費 K1 知識。

### A.5 使用者環境（給 shell 指令前必看）
- Repo: `~/Downloads/Claude-edb-knowledge`，正確 `cd ~/Downloads/Claude-edb-knowledge`
- 使用者偏好（AGENTS.md §13 強制）：永遠給**完整絕對路徑指令 + `&&` 串連成一個 block**；多步前先講明 working directory。
- Python 腳本一律由 repo root 跑：`python3 dev/vault/extract_candidates.py ...`
- Backend：`cd ~/Downloads/Claude-edb-knowledge/backend && npm run dev`

---

## B. 功能要求（按介面）

### B.1 `app.html` — 主應用（React 18 單檔 SPA）
| Tab | 功能要求 |
|---|---|
| 平台介紹 | Hero + 統計（從 `knowledge.json` `_meta.stats` 動態取，**禁止 hardcode**）+ 核心功能說明 + 來源條 |
| 政策搜尋 | 三模式：已核實資料（Channel A）/ 來源文件（Channel B）/ 合併（A+B）。Channel A 可離線；B / A+B 需 backend |
| 指引文件庫 | 148 份 EDB 指引，三層排序：範疇 → 子類別(`sub_category`) → 年份降序；同科分組小標題 |
| 通告分析 | 貼入 EDB 通告文字 → AI 識別主題 / 影響角色 / 政策要點 |
| ✍️ 知識提煉（Admin） | 左右分欄：左候選 queue，右證據 / inline 修訂 / 角色檢視；approve/reject 資料流 |
| ⚙️ 知識管理（Admin） | 批量管理、匯出（admin only）、版本控制 |

### B.2 `index.html` — 入口頁
EDB palette landing；hero + 核心功能 anchor；CTA 導向搜尋／文件庫；統計從 `knowledge.json` `_meta.stats` 動態 fetch（`file://` CORS 失敗時 fallback hardcoded，不可 break）。

### B.3 `q.html` — Quick Q&A
本地 `knowledge.json` 事實搜尋；⌘K modal；idle/answer/no-confident-answer 狀態；inline 引用；範本建議導向 `t-purchase.html`；`?q=` hash prefill。

### B.4 `t-purchase.html` — 範本詳情 + 草稿流程
split grid；4 必填 + 2 選填；live validation；§1–§5 skeleton preview；A/B/AB source 控制；in-page 5 步草稿進度 + 草稿 canvas（來源面板、stale-source 警告、section 選取、修訂 action bar）。文案在未接通正式匯出前只可說「建立草稿／整理」。

### B.5 Mobile UI（進行中，非完成態）
`mobile.css` + `mobile.js`：偵測 ≤640px 或 mobile UA；first-run role picker；cross-page bottom tab bar；dark mode auto。**現況：app.html mobile search 已 ship 並接 `/api/search/combined`；index.html / q.html / t-purchase.html / app.html#guidelines 的 mobile content 尚未 render。** 最新進度以 `SESSION_HANDOFF.md` 為準。

### B.6 Backend API（Node.js + TypeScript，Render 部署）
- `POST /api/search/channel-a` — role_facts keyword + embedding 搜尋
- `POST /api/search/channel-b` — wiki cosine 搜尋 + LLM synthesis（無 top-k 上限，全數返回前端分頁）
- `POST /api/search/combined` — A+B 並行、dedup（80-char prefix）、Channel A 優先、合併 synthesis
- `POST /analyze-circular` — detect → select → prompt → LLM
- `GET /health`、`GET /debug-b`、Channel B prompt GET/SET（Admin）
- Rate limit：10 req/min/IP（sliding window，in-memory）
- 線上：`https://edb-knowledge.onrender.com`（Render free tier，idle 15 分鐘後冷啟 ~30s）

---

## C. 已架構好的系統（下一個 agent 的地圖）

### C.1 前端（GitHub Pages，`main` branch 靜態托管）
- Repo: `Leonard-Wong-Git/edb-knowledge`；live: `https://leonard-wong-git.github.io/edb-knowledge/`
- `app.html` 主 SPA（React 18 + Babel Standalone + Tailwind 2.2，全 CDN，無 build）。DOM mount `#root`；主資料常數 `INITIAL_DATA`（**直接內嵌為 JS object，禁止改回 async fetch**，見 §E）。
- `index.html`（入口）/ `q.html`（Quick Q&A）/ `t-purchase.html`（範本流程）。
- `mobile.css` / `mobile.js`（mobile 層，scope guard `@media (max-width:640px)` + JS 桌面 early-return，確保不影響 desktop）。
- 已刪除（不要復活）：`landing.html`、`k1-wiki.html`、`k1-dashboard.html`（已被 app.html 取代）。
- `dev/design/`：內部設計參考（Spec/Preview/Prototype.html），**非**正式產品流程。

### C.2 知識管道（雙通道，互不污染）
**Channel A — 人工審核（主線）**
```
source_registry → vault PDFs → extract_candidates.py
→ candidate_queue.js (.js 包 window.EXTERNAL_CANDIDATES 繞 file:// CORS)
→ Admin approve (inline edit) → role_facts.json → knowledge.json → Circular System
```
**Channel B — 全 AI（副線，Circular 整合暫停）**
```
source_registry → 同 vault PDFs → ai_extract.py
→ ai_candidate_queue.json（獨立檔）→ build_wiki_index.py → wiki_index.json
→ 上傳 Supabase pgvector → /api/search/channel-b → 智能搜尋 UI
```
- **兩類事實模型**：`statistical`（客觀數字，auto-approve，build_stat_facts.py 程序化建構，無 LLM）vs `policy`（解讀性，人工 gated）。
- 知識三層必須同步：`dev/knowledge/role_facts.json`（SSOT）↔ repo-root `role_facts.json`（backend 讀取）↔ `knowledge.json`（公開 API）。**三層脫節是歷史重大事故來源（§E）。**

### C.3 後端（`backend/`，TypeScript）
- 入口 `server.ts`；`api/`（searchChannelA / searchChannelB / searchCombined / analyzeCircular）；`lib/`（embeddingClient / llmClient / knowledgeRepository / wikiRepository）。
- Embedding：OpenAI `text-embedding-3-small`（固定）。LLM 預設 `gpt-4.1-nano`（`OPENAI_MODEL` 可覆寫，Responses API）。
- 相容橋接：legacy `department_head` 請求會 merge `subject_head` + `panel_chair` + `eo_admin`；新角色 fallback legacy。
- 回歸測試：`cd backend && npm run regression:semantic`（offline deterministic，測 topic routing / role bucket / schema consistency / real-circular retrieval）。每次改公開契約 doc 後必跑。
- 環境變數（`backend/.env`）：`OPENAI_API_KEY`、`OPENAI_MODEL`、`PORT=8787`、`CORS_ORIGIN`、`KNOWLEDGE_PATH`。本地 `file://` dev 需 `CORS_ORIGIN=*`。

### C.4 資料儲存
- **Supabase**（Channel B 向量庫）：project `edb-knowledge`，table `public.wiki_chunks`（vector(1536)，IVFFlat lists=50），RPC `match_wiki_chunks(query_embedding text, match_threshold float, match_count int DEFAULT NULL)`（內部 `text::vector` cast，cosine DESC，不傳 count 則返回全部）。anon role 需 `GRANT USAGE ON SCHEMA public` **且** `GRANT SELECT ON wiki_chunks`。上傳用 service_role key，查詢用 anon key。免費 tier 500MB（現 ~50MB）。
- **GitHub Pages**：公開 artifacts `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md`。
- **MemPalace**（本地 AI memory）：shared install `/Users/leonard/mempalace/.venv`，palace `/Users/leonard/mempalace/palace`，wing `claude_edb_knowledge`；recovery workaround `hnsw:num_threads=1`；備份 `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`。

### C.5 治理框架（AGENTS.md 體系）
- `AGENTS.md`（§0–§13 SSOT）；`CLAUDE.md` / `GEMINI.md` 為 bridge。
- 啟動必讀序：`SESSION_HANDOFF.md` → `SESSION_LOG.md` → `CODEBASE_CONTEXT.md` → 本文件。
- `dev/DOC_SYNC_CHECKLIST.md`（改動 → 必更新文檔對照表，PERSIST 階段強制 scan）。
- `docs/qa/session_log_maintenance.py`（§4a 封存工具，>400 行或最舊條目 >30 天觸發；archive 在 `dev/archive/SESSION_LOG_YYYY_QN.md`）。
- `bump_version.py`（版本號同步 6 檔 + CHANGELOG + README；**注意：歷史上曾有 wipe role_facts.json schema 的已知問題，跑前 backup**）。
- `dev/mempalace_sync.py`（session close 時 MemPalace 同步）。

### C.6 關鍵規格文檔（深入時讀）
- `K1_API_SPEC.md` / `K1_KNOWLEDGE_INTERFACE_SPEC.md`：對外資料契約。
- `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` v2：LLM-wiki 分階段架構。
- `dev/CIRCULAR_SYSTEM_INTEGRATION.md`：與 Circular System 的整合規格（K1 side 已 done）。
- `dev/MOBILE_UI_SPEC_v1.md`：mobile 設計規格 v1.1（Tado-inspired + Pantone Cloud Dancer 2026）。
- `dev/PDF_DOWNLOAD_LIST.md`：EDB PDF 下載清單與 source_id 對照。

---

## D. 成功 / 高效已知方法（直接照用，勿重新發明）

1. **外部平台一律實測，禁止憑記憶猜** — EDB 爬蟲 POST 字段、API 參數、HTML 結構必先用 `parse_form.py` / 解析實際回應確認。這是 AGENTS.md §0b 的具體化，也是本專案最貴的教訓（§E.4）。
2. **大型單檔 HTML 分兩步寫** — 先 `Write` CSS+HTML（JS 留佔位符），再 `Edit` 替換佔位符為完整 JS，繞過 output token 限制。
3. **PDF 提取用 PyMuPDF（純 Python）** — `fitz.open(stream=..., filetype="pdf")` 逐頁，`pip3 install pymupdf --break-system-packages`，不需 poppler/Homebrew。批次提取沿用此 pattern。
4. **dedup 用 `dedup_check.py`（無需 API key）** — character bigram+trigram + CJK word Jaccard，取三者 max 提升中文 recall；`--against` 跨檔比對。任何大規模 dedup 前先用它出 blast radius。
5. **`.js` queue 繞 file:// CORS** — 候選輸出為 `window.EXTERNAL_CANDIDATES` 的 `.js`，dashboard 一鍵本地操作，不用 fetch json。
6. **`INITIAL_DATA` 直接內嵌 JS object** — 解白屏的最終方案；Babel Standalone 無法處理 async fetch + `file://` CORS。**這是鎖定做法。**
7. **curl 繞 SSL / 繞 sandbox egress** — Mac Python.framework 缺 SSL CA bundle、且 Cowork sandbox egress 不含 edb.gov.hk / onrender.com / apps.apple.com。線上驗證一律包成 curl 指令交使用者 Terminal 跑（附完整 `cd` 絕對路徑）。
8. **per-source quota + over-fetch** — Channel B 解單一強勢 source 壟斷：`maxPerSource = max(2, ceil(top_k/3))`，over-fetch topK×5。cap 是上限非下限（不強塞低分 chunk）。
9. **query expansion 加 specific keyword** — 抽象 query（如「教職員請假」）embedding 易被強勢 source 拉偏；加入具體詞（病假/首年/168日/醫生證明）可令正確 source cosine 大幅提升（g04 由 <0.08 → 0.7247 第 1 位）。
10. **三層 dedup / 改動安全程序** — 先 backup 三層到 `dev/init_backup/<ts>/` → apply → 驗證 `knowledgeSelector.ts` union sanity（all_roles + role + uniqueFacts）→ 確認注入內容不變。
11. **改公開契約必跑 regression** — `npm run regression:semantic` + grep parity，早抓 schema drift。
12. **「找不到 PDF」先 triage source 本身** — URL 失效 / SPA / 官方下架先核 source 質素，不要馬上設計 fallback pipeline。
13. **stat facts 程序化建構** — `build_stat_facts.py` 從 parsed extract 硬編碼，比 LLM 快 / 平 / 確定 / 無需 key。

---

## E. 失敗經驗與必避錯誤（這些錯不要再犯）

> 格式：**現象 → 根因 → 已固化的防線**。下一個 agent 觸碰相關區域前必讀對應條目。

### E.1 前端白屏（反覆兩次，Sessions 27–28）
- **根因**：引入 `fetch('data.json')` + AppLoader，Babel Standalone 不能解析 async fetch，`file://` 觸發 CORS，`initialData` 維持 null；camelCase/snake_case 鍵不符。
- **防線**：`INITIAL_DATA` **永遠**直接內嵌為 JS object literal；snapshot 載入兼容 `review_state`/`reviewState` 雙鍵。**不要為了「乾淨」改回 async fetch。**

### E.2 知識三層嚴重脫節（Session 88）+ 48% 重複（Session 102）
- **根因**：審批的新事實只入 `dev/knowledge/role_facts.json`，未同步 repo-root + `knowledge.json`；又因同一 fact 出現在 `all_roles` + 個別 role × N 造成 1,001 條中 484 條 exact duplicate。
- **防線**：任何 role_facts 改動**必須三層同步**；大規模 dedup 用 Strategy B（保 all_roles 副本、刪 role bucket 副本），先 backup、驗 selector union、確認注入不變。數字會變，**同步不變量不可破**。

### E.3 Channel B 系統性品質問題（Sessions 93→104，四輪治理）
- **根因**：`wiki_index` 中 SAG 佔比過高壓倒行政指引；g04 曾是 knowledge-based LLM 內容非真實 PDF；抽象 query embedding 被強勢 source 語境拉偏 → 「採購門檻」返回教師註冊、「教職員請假」返回教師資歷。
- **防線**：routing 層（keyword topic detect + source allowlist + query expansion）+ retrieval 層（per-source quota + over-fetch + SOURCE_ALIASES 軟 dedup）。改 Channel B 排序前先理解這四輪，勿回退。

### E.4 外部平台字段憑記憶猜（EDB 爬蟲，Sessions BE02–BE03，多 session 浪費）
- **根因**：POST 字段名靠記憶假設（猜 `ContentPlaceHolder1`，實為 `MainContentPlaceHolder`）；表格結構假設錯（EDB 用 `td.circularResultRow`）。
- **防線**：AGENTS.md §0b — 外部平台一律實測解析，禁止憑記憶輸出高風險指令。

### E.5 LLM 模型參數踩坑（反覆）
- **根因**：(a) gpt-5-nano 是推理模型，`max_completion_tokens` 被推理耗盡返空、不支援 `system` role；(b) 部分模型 `temperature` 非 1 會 400。
- **防線**：模型參數固定值寫入 `SESSION_HANDOFF.md` Known Risks 作 SSOT，跑前對齊官方文檔，勿沿用記憶。

### E.6 排程覆蓋全量數據 / git rebase 覆蓋治理文件
- **根因**：days-3 排程直接重寫 JSON 不 merge；GitHub Actions 自動 commit 致遠端領先，`git pull --rebase` 覆蓋 `SESSION_HANDOFF.md`。
- **防線**：排程寫入一律 merge 既有資料再 save；push 前手動 cp 最新治理文件入 git repo 再 rebase 再 push；遇 `.git/*.lock` 殘留先 `rm` 再重試。

### E.7 高風險 SQL DELETE 前未驗涵蓋關係（學校行政手冊雙重 ingestion）
- **根因**：g24 與 sag_2025_11 hash 重疊 0%，誤以為可 DELETE，實為同一文件兩種切割。
- **防線**：任何 batch delete / SQL DELETE 必先 dry-run 出 blast radius；非 chunk-level 重複改用 backend 軟 dedup（SOURCE_ALIASES），不動 DB。

### E.8 環境 / 工具坑（清單）
- Backend `openai` 曾是空殼 stub → `rm -rf node_modules package-lock.json && npm install`；`tsconfig` 需 `allowSyntheticDefaultImports`，openai 用 default import。
- pdfminer C 擴展卡死 SIGTERM 無效 → 用 `proc.kill()`（SIGKILL）+ `join(2)` + 雙重抑制 pdfminer logging。
- MemPalace ChromaDB Rust segfault → SQLite 抽取 + `hnsw:num_threads=1` 重建（GitHub issue #974）；用 venv python（system python3 無 chromadb）。
- Supabase 上線後查詢失敗 → anon role 兩個 GRANT 都要；棄 supabase-js 改 direct `fetch()` + `toFixed(8)` embedding string。
- `bump_version.py` 有「known to incorrectly wipe role_facts.json schema」紀錄 → 跑前 backup，跑後驗 schema。
- EDB HTML 頁面永久封 iframe → 用 smart fallback panel，不要再試 iframe embed。
- 實作「新」函數前先 grep 舊定義（曾 `printDetail()` 重複定義）。

### E.9 治理 scope 誤判
- **根因**：曾差點 mount / 修改 Circular System repo。
- **防線**：K1 與 Circular System 是**兩個獨立專案**；K1 只出公開 JSON 端點，不碰對方 repo（見 §A.3）。

---

## F. 鎖定決策（未經 user 明示不要推翻）

1. 單檔前端、無 build pipeline（CDN React/Babel/Tailwind）。
2. `app.html` 為主 SPA；`index.html` 為 EDB landing；`k1-dashboard.html`/`landing.html`/`k1-wiki.html` 已刪不復活。
3. 公開 `knowledge.json` 為對外 schema SSOT；backend 用相容橋接支援 legacy `department_head` + 拆分角色。
4. LLM-wiki 分階段架構：trust 由 source/freshness/approval gate 把關，非 LLM 自主發佈。
5. 兩類事實模型：statistical（auto-approve）vs policy（人工 gated）。
6. Channel B Circular System 整合**暫停**；Channel B 不 auto-write role_facts.json。
7. 繁中產品語言基準；不暴露內部指令；範本流程未接通前只說「建立草稿／整理」。
8. 角色拆分：`subject_head`（科主任）+ `panel_chair`（統籌主任/主任）+ `eo_admin`（EO）；未經 user 釐清不做廣泛術語統一。
9. Guidelines 雙層排序（範疇 → `sub_category` → 時序降序）；QAPanel WordCloud 已移除不復活。
10. 治理文件當 internal session state，git-ignore 規則依現狀。

---

## G. 下一個 AI Agent 起手指南

### G.1 第一步（強制，AGENTS.md §1）
按序讀 `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/CODEBASE_CONTEXT.md` → 本文件。在 `SESSION_LOG.md` 找最新日期 session 的 `### Next Session Handoff Prompt (Verbatim)` 作 PLAN seed。顯示一個隨機 Boot Visual Cue。

### G.2 當前狀態的權威來源
**不要信本文件的數字。** 事實條數 / chunks / 版本號 / mobile 進度 / open priorities 一律以 `SESSION_HANDOFF.md` Current Baseline + Open Priorities 為準（會逐 session 更新）。本文件給的是**結構與不變量**。

### G.3 動手前自問
1. 這屬 Product 層還是 Governance 層？（AGENTS.md §0a）
2. 有冇碰到 §E 任何一條的相關區域？先讀對應防線。
3. 有冇碰外部平台 / API？→ §0b 實測對齊，禁止憑記憶。
4. 改 role_facts？→ 三層同步不變量（§E.2）。
5. 改 Channel B 排序？→ 先理解 §E.3 四輪治理。
6. 風險 HIGH（≥3 檔 / 不可逆 / 外部系統 / 改治理規則）？→ 出 PLAN 等 user 確認再 READ。

### G.4 收尾（AGENTS.md §3 PERSIST / §4 closeout）
更新 `SESSION_HANDOFF.md` + `SESSION_LOG.md`；跑 DOC_SYNC Matrix Scan；如動到 tech stack / 外部服務 / Key Decisions 一併更新 `CODEBASE_CONTEXT.md`；如本文件描述的長期規格 / 鎖定決策有變，同 pass 更新本文件。git push + MemPalace sync 指令交 user Terminal 跑（附完整絕對路徑 + `&&` 串連）。

---

*本規格由 Claude 於 2026-05-16 建立，提煉自 Sessions 1–108 全歷史（含 `dev/archive/` Q1+Q2 季度封存）。長期規格性質——只在鎖定決策 / 架構 / 不變量改變時更新，不逐 session 改。*
