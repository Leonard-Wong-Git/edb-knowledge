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
- Repo（2026-05-16 Session 109 遷移；**路徑含空格，指令必須加雙引號**）：`/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`，正確 `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`
- 使用者偏好（AGENTS.md §13 強制）：永遠給**完整絕對路徑指令 + `&&` 串連成一個 block**；多步前先講明 working directory。
- Python 腳本一律由 repo root 跑：`cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/vault/extract_candidates.py ...`
- Backend：`cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && npm run dev`

---

## B. 功能要求（按介面）

### B.1 `app.html` — 主應用（React 18 單檔 SPA）
| Tab | 功能要求 |
|---|---|
| 平台介紹 | Hero + 統計（從 `knowledge.json` `_meta.stats` 動態取，**禁止 hardcode**）+ 核心功能說明 + 來源條 |
| 政策搜尋 | 三模式：已核實資料（Channel A）/ 來源文件（Channel B）/ 合併（A+B）。Channel A 可離線；B / A+B 需 backend |
| 指引文件庫 | **148** 份 EDB 文件（app.html `GUIDELINES_REGISTRY`，subtitle 用 `.length` 動態反映；= 全 channel 知識基礎文件全集）；三層排序：範疇 → 子類別(`sub_category`) → 年份降序；同科分組小標題。公開 `guidelines.json` 端點為其中 **39** 份精選子集（見下方釐清框）|
| 通告分析 | 貼入 EDB 通告文字 → AI 識別主題 / 影響角色 / 政策要點 |
| ✍️ 知識提煉（Admin） | 左右分欄：左候選 queue，右證據 / inline 修訂 / 角色檢視；approve/reject 資料流 |
| ⚙️ 知識管理（Admin） | 批量管理、匯出（admin only）、版本控制 |

> **數字釐清（極易混淆，下一個 agent 必讀；2026-05-16 truth-pass v2 實測重寫）**：四個「指引/來源」數字是不同層級與 scope，**全部都係真實有效**，勿混為一談 —
> - `app.html` `GUIDELINES_REGISTRY` = **148** 份文件 —— 用戶喺「指引文件庫」tab 真正 browse 到嘅全集；A / B / A+B 各 channel 嘅知識本質上都由呢 148 份 EDB 文件衍生。subtitle 用 `GUIDELINES_REGISTRY.length` 動態反映（commit `0871bbe`，**非 bug**）。
> - `guidelines.json` = **39** 份 —— 對外公開端點，係上述 148 嘅**嚴格子集**（精選核心行政指引，給 Circular System 按主題 fetch）。精簡 schema：`id/title/titleShort/url/year/format`（+curriculum `level`），不洩漏內部 `category/sub_category/isSpine`。
> - `dev/source/source_registry.json` = **151** 個來源 entry（vault 提取來源登記表，provenance / freshness 層）。
> - 其中 **120** 個已完成 vault 提取（= `knowledge.json._meta.stats.sources`，SESSION_HANDOFF baseline 引用的 "120 sources"）。
>
> ⚠️ **DEFERRED FUTURE（2026-05-17 S112，Leonard 拍板更新；前身為 S111「OPEN DECISION」）**：公開 `guidelines.json` 由 39 擴張到 **148** ——Leonard 明示「將來會做、最終一致」，即係**已定方向、暫緩執行**（**非 undecided**）。排序喺 P1 搜尋相關性 + P2 文件分類**之後**先做。屬**對外契約變更**，影響下游 Circular System（curriculum 桶 ~25→127），執行時仍須走 AGENTS.md §3 HIGH-risk PLAN + 更新 §F.3。未到該階段前**不收斂**。
> 註：舊版本框曾寫「148 是過時 registry 計數，已不準」——**該說法本身先係錯**（亦曾誤導 Session 111 一度當佢係 regression）。148 一直係 app 內庫實數，已更正。

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
- **Supabase**（Channel B 向量庫）：project `edb-knowledge`，table `public.wiki_chunks`（embedding 欄 vector(1536)，IVFFlat **lists=60**；lists「50」舊寫係 drift S115 修）。RPC **live 真實簽名 = `match_wiki_chunks(query_embedding TEXT, match_threshold double precision DEFAULT 0.1, match_count integer DEFAULT NULL)`**（後端 send 字串、內部 `query_embedding::vector` cast，cosine DESC，null count = 全返）。⚠️ **`schema.sql` 曾把簽名 drift 成 `vector(1536)`，S116 套落 live 與真實 text 變體並存 → PGRST203 → Channel B 全 0（live 事故）；任何 RPC DDL 前必 INSPECT live `pg_get_functiondef`（§E.13）。** **S116：函數現 `language plpgsql VOLATILE` body `set local ivfflat.probes = 8`**（≈sqrt(lists)；取代 sql/stable/probes=1）= CB-2 PLAN-1 Stage-1（生產現行 probes=8）。⚠️ **S118 caveat**：free-tier probes=8 偶發 Supabase `57014` statement-timeout（生產可用性風險，retry 恢復）；probes=8 *live* 仍未獨立 `pg_get_functiondef` introspect（audit-flagged）。**S118：Channel B routing +4 dedicated selective route（PLAN-1b：cpd/kg_admission/conduct/steam，見 §E.3）；Stage-2 adaptive combo 經雙獨立驗證非可行、放棄。** anon 需 `GRANT USAGE ON SCHEMA public` **且** `GRANT SELECT ON wiki_chunks`；DDL 須 Supabase Dashboard（Leonard auth，無 CLI/psql/DB-url 路徑）。上傳 service_role key、查詢 anon key；免費 tier 500MB（現 ~50MB）。
- **GitHub Pages**：公開 artifacts `knowledge.json` / `guidelines.json` / `K1_API_SPEC.md`。
- **MemPalace — REMOVED 2026-05-18 (S115，Leonard 指示)**：本專案已停用 MemPalace；repo-local config + `dev/mempalace_sync.py` 已刪、治理引用已剝除。Shared palace（repo 外、多專案共用）為其他專案保留；本專案 wing drawers 孤兒化（CLI 無 wing-delete）。勿為本專案重設 MemPalace 除非 Leonard 明示。

### C.5 治理框架（AGENTS.md 體系）
- `AGENTS.md`（§0–§13 SSOT）；`CLAUDE.md` / `GEMINI.md` 為 bridge。
- 啟動必讀序：`SESSION_HANDOFF.md` → `SESSION_LOG.md` → `CODEBASE_CONTEXT.md` → 本文件。
- `dev/DOC_SYNC_CHECKLIST.md`（改動 → 必更新文檔對照表，PERSIST 階段強制 scan）。
- `docs/qa/session_log_maintenance.py`（§4a 封存工具，>400 行或最舊條目 >30 天觸發；archive 在 `dev/archive/SESSION_LOG_YYYY_QN.md`）。
- `bump_version.py`（版本號同步 6 檔 + CHANGELOG + README；**注意：歷史上曾有 wipe role_facts.json schema 的已知問題，跑前 backup**）。
- ~~`dev/mempalace_sync.py`~~ — 已刪除 2026-05-18 (S115)；本專案 session close 不再做 MemPalace 同步。

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
14. **Supabase pgvector probes 調校（S116 實證）** — 升 `ivfflat.probes` 唯一可行路 = 把 RPC 改 `language plpgsql VOLATILE`、body 首句 `set local ivfflat.probes = N`（N≈sqrt(lists)）。function-level SET clause 撞 42501、stable/sql 撞 0A000（§E.13）。改前 INSPECT live 真實簽名、保持 byte-identical（§E.13 防線）。**Channel B live-verify 用 dedicated `/api/search/channel-b`**（無 route-level catch，真錯→HTTP400；S117 已修 combined masking〔`channel_b_status` discriminator，§E.13 防線4〕但 dedicated 仍係 live-grade 首選、方法論不變）+ curl（Mac SSL）+ ≥15s pacing（10 req/min 限）+ warmup（Render 冷啟）+ classify（INFRA_FAIL ≠ recall 0）。詳 auto-memory `reference_supabase_pgvector_probes`。

---

## E. 失敗經驗與必避錯誤（這些錯不要再犯）

> 格式：**現象 → 根因 → 已固化的防線**。下一個 agent 觸碰相關區域前必讀對應條目。

### E.1 前端白屏（反覆兩次，Sessions 27–28）
- **根因**：引入 `fetch('data.json')` + AppLoader，Babel Standalone 不能解析 async fetch，`file://` 觸發 CORS，`initialData` 維持 null；camelCase/snake_case 鍵不符。
- **防線**：`INITIAL_DATA` **永遠**直接內嵌為 JS object literal；snapshot 載入兼容 `review_state`/`reviewState` 雙鍵。**不要為了「乾淨」改回 async fetch。**

### E.2 知識三層嚴重脫節（Session 88）+ 48% 重複（Session 102）
- **根因**：審批的新事實只入 `dev/knowledge/role_facts.json`，未同步 repo-root + `knowledge.json`；又因同一 fact 出現在 `all_roles` + 個別 role × N 造成 1,001 條中 484 條 exact duplicate。
- **防線**：任何 role_facts 改動**必須三層同步**；大規模 dedup 用 Strategy B（保 all_roles 副本、刪 role bucket 副本），先 backup、驗 selector union、確認注入不變。數字會變，**同步不變量不可破**。
- **2026-05-16 復發（同類，第三次）**：再 dedup 792 → **455**（移除 275 條跨角色完全重複 + 合併 36 組相近事實，commit `711f911`，reversible log `dev/DEDUP_LOG_2026-05-16.md`）。三層 dedup 紀律本身守住（reversible log + 三層 byte-identical），但**該批 commit 完全冇入 SESSION_LOG**（連同 7 個其他 2026-05-16 commit）——衍生 Session 111 治理 gap 發現（見 SESSION_LOG）。教訓延伸：dedup 安全程序 ≠ 治理紀律；繞過 SESSION_LOG 嘅 commit 會令交接讀set 失真。

### E.3 Channel B 系統性品質問題（Sessions 93→104，四輪治理）
- **根因**：`wiki_index` 中 SAG 佔比過高壓倒行政指引；g04 曾是 knowledge-based LLM 內容非真實 PDF；抽象 query embedding 被強勢 source 語境拉偏 → 「採購門檻」返回教師註冊、「教職員請假」返回教師資歷。
- **防線**：routing 層（keyword topic detect + source allowlist + query expansion）+ retrieval 層（per-source quota + over-fetch + SOURCE_ALIASES 軟 dedup）。改 Channel B 排序前先理解這四輪，勿回退。
- **S118 延伸（第 5 輪，PLAN-1b）**：加 4 條 dedicated selective route（`cpd`/`kg_admission`/`conduct`/`steam`，`TOPIC_KEYWORDS` first-match 置 `finance` 前 + 對應 `SOURCE_SETS` tight set + 單一 `QUERY_EXPANSIONS` 條目，§3b 一規一處）。**dedicated tight set 係穿過 §E.3 SAG-排除針孔嘅法**：CPD-gold 喺 `sag_2025_11`/`g06`（廣 `curriculum` 故意排 SAG）→ 唔好倒落 `curriculum`，而係細 `cpd`/`conduct` set，SAG 仍受 per-source quota(cap=3) 約束、不重現 SAG-domination。獨立 audit + 真 probes=8 live-verify 雙重確認、12 條零回歸。
- **S118 codified lesson — Stage-2 adaptive cutoff（combo）經雙獨立驗證放棄，勿復活**：當正確 gold 排喺高分噪音之下，收緊 per-query cutoff 只會跌 recall（病राetc. combo .5→.25），**cutoff 結構上救唔到上游 ranking defect**。lever 係 routing/expansion（PLAN-1b）唔係 threshold；future 勿再以 adaptive-threshold 嘗試修上游 ranking。

### E.4 外部平台字段憑記憶猜（EDB 爬蟲，~5 個 backend session 浪費：BE01→BE02→BE03 + `_parse_list` 全重寫）
- **根因**：POST 字段名靠記憶假設（猜 `ContentPlaceHolder1`，實為 `MainContentPlaceHolder`）；表格結構假設錯（EDB 用 `td.circularResultRow`）；ASP.NET ViewState 處理錯，debug chain 橫跨多個 backend session。
- **防線**：AGENTS.md §0b — 外部平台一律實測解析，禁止憑記憶輸出高風險指令。**成本教訓**：此類「憑記憶猜外部字段」是本專案最貴的 rework 來源之一（多 session 浪費），不是單次小錯。

### E.5 LLM 模型參數踩坑（**確認跨工具復發**：backend BE04 + Phase 3 `extract_candidates.py` 各獨立踩同一坑）
- **根因**：(a) gpt-5-nano 是推理模型，`max_completion_tokens` 被推理耗盡返空、不支援 `system` role（需 `developer` role）；(b) 部分模型 `temperature` 非 1 會 400。同一推理模型陷阱在 backend session 解過一次後，於完全無關的 `extract_candidates.py` pipeline 被另一 agent **再踩再解一次** — 跨 session / 跨工具復發，是最強的 rule-promotion 訊號。
- **防線**：模型參數固定值寫入 `SESSION_HANDOFF.md` Known Risks 作 SSOT，跑前對齊官方文檔，勿沿用記憶。接任何新推理模型前先查官方 param 差異（reasoning token / role 名 / temperature 限制）。

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
- `bump_version.py` **曾於 Session 64（v1.4.0 release）實際觸發** wipe role_facts.json schema（release 後要把 schema 還原回 2.0.0）→ 不是理論風險，是已 fire 過的 release-time foot-gun；跑前必 backup，跑後必驗 schema。
- EDB HTML 頁面永久封 iframe → 用 smart fallback panel，不要再試 iframe embed。
- 實作「新」函數前先 grep 舊定義（曾 `printDetail()` 重複定義）。

### E.9 治理 scope 誤判
- **根因**：曾差點 mount / 修改 Circular System repo。
- **防線**：K1 與 Circular System 是**兩個獨立專案**；K1 只出公開 JSON 端點，不碰對方 repo（見 §A.3）。

### E.10 公開站點的 client-side admin 閘門 + 密碼明文入 log（🔴 資料/安全風險，跨 Sessions 19–27 反覆，至今仍 open）
- **根因**：Admin approve / edit / export / 知識管理 閘門只係瀏覽器端 SHA-256（`ADMIN_HASH`），整套控制隨靜態站 deploy 上**公開 GitHub Pages** — **不是真正安全邊界**，任何人可繞。更嚴重：Session 19 曾把明文密碼寫入 `SESSION_LOG.md`。此風險由 Session 19 起反覆出現、橫跨 6+ session，**至今仍係 open priority**（「admin login security password gate」OP #2）。
- **防線**：(1) client-side 閘門只當 UI 便利，**永不可當安全邊界**；任何敏感控制（approve / export / 知識管理）暴露前必須有 server-side 驗證。(2) **絕不**把密碼 / API key / token 明文寫入任何 log / session 文件 / commit。(3) 公開 artifact push 前 grep secret pattern。這是全專案歷時最長、後果最嚴重的未解風險，下一個 agent 碰 admin / auth / 公開推送前必讀此條。

### E.11 Channel A / analyze-circular 主題偵測污染（Sessions 19→21→63→66，patch 4 次）
- **根因**：`SIMILARITY_THRESHOLD` 只係下限、無上限亦無相對 gap 過濾 → 財務通告拉入非財務事實，600-char budget 被次要主題塞滿。跨 4 session patch 4 次先靠 gap+cap 解決。
- **防線**：topic 偵測不可只靠 similarity floor — 必須加 `MAX_TOPICS` 硬上限 + `SCORE_GAP` 相對過濾。重調 threshold 後必跑 5-case sim 回歸 + 2 條真實通告線上回歸先可宣稱修好。**此為 §E.3 的 Channel A 對應面**（§E.3 只講 Channel B retrieval），改 analyze-circular / Channel A 排序前兩條一齊讀。

### E.12 EDB 全站改版一次過打爛 26 條 source URL（Session 61，兩輪緊急復原）
- **根因**：EDB 官網無預警改版，registry 26 條 URL 同時 404；要兩輪緊急復原（17 主要 + 9 legacy）+ 建 freshness baseline + 每週 GitHub Actions CI。
- **防線**：EDB 會無預警重組網站（已發生，非假設）→ `check_freshness.py` + 每週 CI 係常設防線，勿停。遇大規模 404：爬 landing page 搵新檔名 / 新路徑，**不要直接刪 source**（source 通常仍有效，只係搬咗）。參見 §D.12。

### E.13 `schema.sql` 簽名 drift → PGRST203 live 事故 + Supabase 受限角色 GUC 坑（Session 116，Channel B 生產一度全 0）
- **根因**：`backend/supabase/schema.sql` header 自稱「the exact contract the backend code expects / do not drift」，但實已 drift —— 它定義 `match_wiki_chunks(query_embedding **vector(1536)**,...)`，而後端 `wikiRepository.ts` send embedding 做**字串**、live 真實函數係 `(query_embedding **text**,...)` 內部 `::vector` cast。CB-2 probes promote 信咗 schema.sql 套 vector 變體落 live → 同既有 text 變體**並存重載** → PostgREST **PGRST203「could not choose best candidate」** → Channel B 對所有 query 返 0（combined 靜默退化 A-only，事故對 monitoring 半隱形）。連帶踩中 Supabase 受限 `postgres` 角色坑：function-level `SET ivfflat.probes` clause → **42501**；`SET`/`SET LOCAL` 喺 STABLE/IMMUTABLE 或 `language sql` 函數 → **0A000**（須 VOLATILE plpgsql）。
- **防線**：(1) **任何 Supabase RPC / 函數 DDL 之前，必先 `select pg_get_functiondef(oid)` 攞 live 真實定義 + overload 清單，據此寫 replacement、勿信 `schema.sql`**（§G.2 verify-don't-trust-docs 對 Supabase DDL 之具體化；已入 auto-memory `feedback_inspect_live_supabase_before_replace`）。`create or replace` 必須同 live signature + return type byte-identical，否則造新 overload。(2) Supabase pgvector probes 正解 = `language plpgsql VOLATILE` + body `set local ivfflat.probes=N`（pooling-safe；機制詳 auto-memory `reference_supabase_pgvector_probes` + §D.14）。(3) 生產 DDL 仍 Leonard Dashboard 親手；Claude 出精確 APPLY+ROLLBACK+唯讀 INSPECT，事故時先 ROLLBACK 還原再 INSPECT 真實態。(4) ✅ **衍生 promote-blocker — RESOLVED S117（2026-05-19，Leonard /goal C）**：原 `searchCombined.ts` `.catch` 將**任何** Channel B 例外包成假 reason「Channel B 未配置（環境變數缺失）」+ HTTP 200 → 真 transient 與真 misconfig 無法區分、對 monitoring/eval 隱形。**修法**：新增 `failedChannelBResponse`（`degraded_kind:"error"` + `CHANNEL_B_ERROR_REASON`），與 genuine-unconfigured 之 `degradedChannelBResponse`（`"unconfigured"`/未配置）並列；combined 加 machine-readable `channel_b_status` discriminator〔`"unconfigured"`|`"error"`〕；靜態 `isSupabaseConfigured()` guard 不變。最小 additive、零前端 coupling、保留 A-only graceful degradation。驗證 §3d deterministic 13/13（真 fetch-fail→`"error"` 非 未配置）。**仍建議**：Channel B live-grade 用 dedicated `/api/search/channel-b`（無 route-level catch，真錯→HTTP400，方法論不變）。生產 deploy = Render push 後 auto-deploy。

---

## F. 鎖定決策（current-state 決策，非不可變法律 — 見下方 banner）

> ⚠️ **產品方向審視中（2026-05-16，Leonard 明示）**：以下「鎖定決策」記錄嘅係**截至本次嘅 current-state 決策**，**不是不可變法律**。Leonard 已表明：產品方向可能要變、現有 codebase 偏亂難維護、且不完全信任既有文檔（本次實測已證實文檔有 drift，見 §G.2 banner）。下一個 agent 接手時：
> - (a) 把 §F 當「現況點解係咁」嘅背景，**不是**「不准郁」嘅禁令；
> - (b) 任何方向 / scope / 架構調整，同 Leonard 確認後即可推翻對應條目，並喺本文件**同 pass 更新**；
> - (c) 變更鎖定決策必走 AGENTS.md §3 HIGH-risk PLAN 流程（出 PLAN → 等 user 確認 → 先 READ/CHANGE）。

1. 單檔前端、無 build pipeline（CDN React/Babel/Tailwind）。
2. `app.html` 為主 SPA；`index.html` 為 EDB landing；`k1-dashboard.html`/`landing.html`/`k1-wiki.html` 已刪不復活。
3. 公開 `knowledge.json` 為對外 schema SSOT；backend 用相容橋接支援 legacy `department_head` + 拆分角色。
4. LLM-wiki 分階段架構：trust 由 source/freshness/approval gate 把關，非 LLM 自主發佈。
5. 兩類事實模型：statistical（auto-approve）vs policy（人工 gated）。
6. Channel B Circular System 整合**暫停**；Channel B 不 auto-write role_facts.json。
7. 繁中產品語言基準；不暴露內部指令；範本流程未接通前只說「建立草稿／整理」。
8. 角色拆分：`subject_head`（科主任）+ `panel_chair`（統籌主任/主任）+ `eo_admin`（EO）；未經 user 釐清不做廣泛術語統一。
9. Guidelines 雙層排序（範疇 → `sub_category` → 時序降序）；QAPanel WordCloud 已移除不復活。**公開 `guidelines.json` 現為 39 份精選子集，app 內庫實為 148 份**——39→148 收斂 = **deferred future intent**（S112 Leonard：將來會做、最終一致，非 undecided；排 P1/P2 之後），執行時須走 §3 HIGH-risk PLAN（見 §B.1 釐清框）。
10. 治理文件當 internal session state，git-ignore 規則依現狀。

---

## G. 下一個 AI Agent 起手指南

### G.1 第一步（強制，AGENTS.md §1）
按序讀 `dev/SESSION_HANDOFF.md` → `dev/SESSION_LOG.md` → `dev/CODEBASE_CONTEXT.md` → 本文件。在 `SESSION_LOG.md` 找最新日期 session 的 `### Next Session Handoff Prompt (Verbatim)` 作 PLAN seed。顯示一個隨機 Boot Visual Cue。

### G.2 當前狀態的權威來源
**不要信本文件的數字。** 事實條數 / chunks / 版本號 / mobile 進度 / open priorities 一律以 `SESSION_HANDOFF.md` Current Baseline + Open Priorities 為準（會逐 session 更新）。本文件給的是**結構與不變量**。

> ⚠️ **連 SESSION_HANDOFF / CODEBASE_CONTEXT / HANDOFF_PACKAGE 都會 drift，drift 仲會層層疊**（2026-05-16 兩次實測證實）：
> - **drift 級聯實例**：Session 110 實測「修正」CODEBASE_CONTEXT `1,001 → 792`、出 HANDOFF_PACKAGE 標榜「乾淨可信快照」；但**同一日**另一條未入 SESSION_LOG 嘅 work-stream（8 個 commit）已 dedup 792 → **455**、HEAD 由 `c78685f` 推進到 `ae31084`，而 S110 自己嗰批文檔修正**從未 commit**。結果 Session 111 接手時，連「可信快照」都係 stale。→ truth-pass v2（Session 111）已重新對齊到 455 / ae31084。
> - SESSION_HANDOFF baseline #5 寫 `min_score B/AB=0.15` 曾 drift，S110 已對齊 **0.22**（`searchChannelB.ts`/`searchCombined.ts` default；A=0.1 正確）——此項仍有效。
> - 「148 是過時 registry 計數」嘅舊說法本身就係錯（§B.1 已更正）：148 = app 內庫實數，39 = 公開端點子集，兩者皆真。
> - 連 commit message 都唔可盡信：`0871bbe`「guidelines=148」唔係 regression 而係正確；Session 111 一度照 message 誤判，verify GUIDELINES_REGISTRY.length 後更正。
>
> 教訓：對任何 **load-bearing 常數**（事實條數 / min_score / top_k / 模型參數 / 端點路徑 / 資料來源 / git HEAD），動手前以**實際 code / 資料 / git 為準**，文檔（連「可信快照」與 commit message）只作線索。發現 drift 即喺 PERSIST 修正對應文檔。**並且：任何改 code/data 嘅 commit 必須同 pass 入 SESSION_LOG**——Session 111 證實「commit 咗但冇入 SESSION_LOG」係令交接讀set 失真嘅根因，比單純文檔懶更新更危險。此 banner 留作方法論提醒。

### G.3 動手前自問
1. 這屬 Product 層還是 Governance 層？（AGENTS.md §0a）
2. 有冇碰到 §E 任何一條的相關區域？先讀對應防線。
3. 有冇碰外部平台 / API？→ §0b 實測對齊，禁止憑記憶。
4. 改 role_facts？→ 三層同步不變量（§E.2）。
5. 改 Channel B 排序？→ 先理解 §E.3 四輪治理。
6. 風險 HIGH（≥3 檔 / 不可逆 / 外部系統 / 改治理規則）？→ 出 PLAN 等 user 確認再 READ。

### G.4 收尾（AGENTS.md §3 PERSIST / §4 closeout）
更新 `SESSION_HANDOFF.md` + `SESSION_LOG.md`；跑 DOC_SYNC Matrix Scan；如動到 tech stack / 外部服務 / Key Decisions 一併更新 `CODEBASE_CONTEXT.md`；如本文件描述的長期規格 / 鎖定決策有變，同 pass 更新本文件。git commit + push 由 Claude 執行（Leonard S115 授權「push 係你做」；加指定檔勿 -A、完整絕對路徑 + `&&` 串連）。（MemPalace sync 已 S115 移除。）

---

*本規格由 Claude 於 2026-05-16 建立，提煉自 Sessions 1–108 全歷史（含 `dev/archive/` Q1+Q2 季度封存）。長期規格性質——只在鎖定決策 / 架構 / 不變量改變時更新，不逐 session 改。*
