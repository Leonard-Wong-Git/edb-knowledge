# Session Handoff

## Current Baseline
1. Version: **v1.5.0** (K1知識平台)
2. Core files:
   - `index.html` — **K1 知識平台 Landing Page（入口）** ✅ (Session 77 重構)；dark theme, particle canvas, scroll reveal, stats counter, bento features, CTA → app.html
   - `app.html` — **K1知識平台 FULL REACT SPA** ✅ (Phase 2 migration complete); tabs: 平台介紹 / 智能搜尋 (Channel A/B/A+B) / 指引文件庫 / 通告分析 / 知識提煉(Admin) / 知識管理(Admin)
   - `k1-dashboard.html` — **已刪除**（git rm，Session 77）
   - `backend/src/` — Node.js TypeScript backend; Phase 1 search APIs complete:
     - `backend/src/lib/wikiRepository.ts` ✅
     - `backend/src/api/searchChannelA.ts` ✅
     - `backend/src/api/searchChannelB.ts` ✅ (no top-k limit)
     - `backend/src/api/searchCombined.ts` ✅
     - `backend/src/server.ts` — routes `/api/search/channel-a`, `/channel-b`, `/combined` ✅
3. Knowledge state: 109 Channel A facts (7 topics), **408 candidates in queue** (含 Policy Signal 新增 22 個), **wiki_index.json ✅** (2,840 chunks, 124 MB — Session 78 需 rebuild 加入 edbc002/003/005 2026)
4. External dependencies: EDB website, OpenAI API (gpt-4.1-nano + text-embedding-3-small), Google Docs Viewer for PDF proxy
5. Model fix: `gpt-5-nano` → `gpt-4.1-nano` corrected across all live code files
6. Channel B: requires `cd backend && npm run dev` before testing B/A+B in app.html

## User Environment (Always Reference Before Giving Shell Commands)
- **Repo path**: `~/Downloads/Claude-edb-knowledge`
- **Correct cd**: `cd ~/Downloads/Claude-edb-knowledge`
- **Python script invocation**: always from repo root, e.g. `python3 dev/vault/extract_candidates.py ...`
- **Backend**: `cd ~/Downloads/Claude-edb-knowledge/backend && npm run dev`

## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Confirm environment: backend needs `OPENAI_API_KEY` in `backend/.env`

---

## Architecture Decisions (Locked — 2026-04-16)

### Decision 1 — Single SPA Entry Point
```
index.html  ←  K1知識平台（唯一入口，React SPA）
    │
    ├── 🔍 智能搜尋（預設頁）     ← Channel A / B / A+B 選擇按鈕
    ├── 📚 指引文件庫              ← 3-level sort: category → sub_category → time desc
    ├── 📄 通告分析
    ├── ℹ️  平台介紹              ← 現有靜態 landing 內容移入此 tab
    ├── ✍️  知識提煉（Admin）     ← 左右分欄佈局 + 即時行內修訂
    └── ⚙️  知識管理（Admin）

k1-dashboard.html  →  廢棄（保留備份）
```

### Decision 2 — Backend API for Channel B Search
現有 Node.js TypeScript backend 擴展，新增端點：
```
/api/search/channel-a    ← role_facts.json keyword/semantic search
/api/search/channel-b    ← wiki_index.json cosine search (NO top-k limit, return all)
/api/search/combined     ← A+B merged, deduped, source-labelled
/api/channel-b/prompt    ← GET/SET Channel B extraction & synthesis prompts (Admin)
```
- Channel B 搜尋**不設 top-4 限制**，全數返回，前端分頁顯示
- 利用現有 `embeddingClient.ts` 做 query embedding
- 新增 `backend/src/lib/wikiRepository.ts`（載入 wiki_index.json + cosine 計算）

### Decision 3 — Platform Stats Are Dynamic (A+B Combined)
- 平台介紹 tab 的統計數字（事實數、chunks 數等）從實際資料動態計算
- 反映 Channel A（role_facts.json）+ Channel B（wiki_index.json）合計
- 不再硬編碼「109+」等數字

### Decision 4 — Channel B Admin Prompt Editor
- Channel B candidates 獨立於 Channel A queue
- Admin 可在「Channel B 後台」tab 編輯 SYSTEM_PROMPT_B 及 SYNTHESIS_PROMPT
- 提供測試沙盒（貼入段落 → 即時看提取結果）及新舊 Prompt 對比面板
- 品質指標：字數達標率、來源引用率、合規風險識別率

### Decision 5 — Two-Channel Knowledge Pipeline (Original)
**Channel A — Human Review（主線）**
```
source_registry → vault PDFs → extract_candidates.py
→ candidate_queue.js → Admin Approve (inline edit) → role_facts.json → Circular System
```

**Channel B — Full AI（副線）**
```
source_registry → same vault PDFs → ai_extract.py
→ ai_candidate_queue.json (independent) → wiki_index.json (vector search)
→ /api/search/channel-b (backend) → 智能搜尋 UI
```
- Channel B Circular System 接入**明確暫停**，待質素測試後決定

### Decision 6 — Guidelines Dual Sort
- GUIDELINES_REGISTRY 加入 `sub_category` 欄位（例如 `procurement`、`lsg`、`cpd`、`sen`）
- 排序：範疇 → 同科類 → 時序降序
- 視覺：同科分組小標題

### Decision 7 — WordCloud Removed
- QAPanel 的 floatWord 浮動動畫刪除（視覺效果差）

---

## 📋 Todolist — 待討論跟進項目

### [TODO-1] Policy Signals 機制 — 設計已完成，待執行測試

**背景**：Circular System（edb_scraper.py v3.0.45+）已實裝「暗盤訊號」機制：
- 每次 scraper 執行後，靜默偵測新通告是否屬「需知識庫跟進的政策/框架文件」
- 觸發條件（strong mode）：標題含【架構｜課程框架｜學習宗旨｜指引（YYYY）】**且** AI topics 含 curriculum
- 結果寫入 `dev/knowledge/policy_signals.json`

**Session 77 設計決定（已落地）**：
- ✅ `dev/vault/process_signals.py` — 全自動 pipeline（下載 PDF → pdftotext → vault extract → extract_candidates.py → 更新 source_registry + signal status）
- ✅ `dev/knowledge/policy_signals.json` — schema 擴充（含 url, trigger_reason, status_values），3 個 pending signals 已登記
- Signal schema 新增欄位：`url`（PDF 直連）, `trigger_reason`（匹配關鍵字）, `processed_at`, `source_id`, `channel_a_candidates_added`
- URL 規律：`https://applications.edb.gov.hk/circular/upload/EDBC/EDBC{YY}{NNN}C.pdf`
- edb_scraper.py 寫 signal 時**需要帶 url 欄位**（待 Circular System 同步更新）

**Pending signals（3 個，URL 估算，需確認）**：
- `sig_edbc002_2026` → `EDBC26002C.pdf`
- `sig_edbc003_2026` → `EDBC26003C.pdf`
- `sig_edbc005_2026` → `EDBC26005C.pdf`

**用法**：
```bash
# Dry-run（確認 URL 有效、查看將要做甚麼）
python3 dev/vault/process_signals.py --dry-run

# 處理單個 signal
python3 dev/vault/process_signals.py --signal-id sig_edbc002_2026

# 處理所有 pending
python3 dev/vault/process_signals.py
```

**待跟進**：
1. 確認 3 個 PDF URL 是否有效（先執行 dry-run 或 curl --head）
2. 執行 `process_signals.py --signal-id sig_edbc002_2026` 測試 Phase 1 準確性
3. K1 Dashboard 知識提煉 tab 加入 signal badge（顯示 N pending）— 待 Phase 1 驗證後做
4. edb_scraper.py signal 寫入格式同步（加 url 欄位）— 待 Circular System repo 更新
5. signal level 擴展：weak signal（未來）觸發條件細化

---

## Open Priorities (Phased)

### Phase 0 — 立即可做（不涉及架構）
| 優先 | 工作 | 說明 |
|------|------|------|
| ~~P0.1~~ | ~~執行 build_wiki_index.py~~ | ✅ 完成 — 2,840 chunks, 124 MB (rebuilt 2026-04-17, 45 vault sources) |
| ~~P0.2~~ | ~~測試 wiki_search.py~~ | ✅ 完成 — 採購門檻查詢正確，繁中已修正 |
| P0.3 | 匯出 role_facts.json | Admin → 刪「課程統籌主任規劃」前綴 → 匯出 → 替換 repo |
| P0.4 | Admin Review 新候選 | 92 candidates in queue 待審批 |

### Session 76 新增 Extract 檔案（20 個 source_ids）✅ 全部完成

**Channel A 候選提取 ✅ 全部完成**（386 candidates in queue）：
- g02 (+43), g03 (+16), g04 (+50), g05 (+38, parse bug fixed), g11 (+18)
- edbc20_2023_ph_pri (+37), edbc9_2024_ph_pri (+15), edbc18_2023_pri_science (+46), edbc13_2025_pri_science (+17)
- **Bug fix**: `extract_candidates.py` — `_sanitize_llm_json()` 修復 `page_number: 18-19` 及相鄰字串 LLM quirk

**Channel B 重建**（本地執行）：
```bash
python3 dev/vault/build_wiki_index.py
```
預計新增 ~3,000–4,000 chunks，總計約 4,500+ chunks。

### Phase 1 — Backend 擴展 ✅ 完成
- ✅ `backend/src/lib/wikiRepository.ts`
- ✅ `backend/src/api/searchChannelA.ts`
- ✅ `backend/src/api/searchChannelB.ts` (no top-k limit)
- ✅ `backend/src/api/searchCombined.ts`
- ✅ `backend/src/server.ts` — 3 new routes added
- ✅ `npm run check` passes

### Phase 2 — index.html SPA 遷移 ✅ 完成
- ✅ k1-dashboard.html React app 完全合併入 index.html（3183 lines）
- ✅ 加入「平台介紹」tab（PlatformIntroPanel: hero stats, bento 6-card, how-it-works, sources strip）
- ✅ Channel A/B/A+B 搜尋按鈕接通 backend（offline A, backend B/A+B）
- ✅ 動態統計數字（approvedCount, 810 chunks, 39 guidelines, 7 topics）
- ✅ WordCloud 已刪除
- ✅ Backend error 顯示（channel B unavailable graceful fallback）

### Phase 3 — 知識提煉改版 + WordCloud 刪除
- 左右分欄佈局，即時行內修訂
- 刪除 floatWord 動畫

### Phase 4 — 指引文件庫雙重排序
- 加入 `sub_category`，三層排序

### Phase 5 — Channel B 後台管理
- Prompt 編輯器 UI
- 測試沙盒 + 品質指標

### Phase 6 — Channel B 持續深化
- ai_extract.py 再跑更多來源
- Channel B vs A 品質比較
- 決定 Circular System 接入條件

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. **Online semantic regression: PASS=12 / FAIL=0** (2026-04-12) ✅

---

## Last Session Record
1. UTC date: 2026-04-18
2. Session ID: Claude_20260418_0001 (Session 77)
3. Completed:
   - ✅ **[process_signals.py]** 全自動 Policy Signals pipeline（SSL fallback + pypdf fallback + --retry-failed）；3/3 signals 成功處理
   - ✅ **[Policy Signals 驗證]** 3/3 signal accuracy = 100%：EDBC002 地理科課程框架、EDBC003 價值觀教育架構、EDBC005 學習宗旨更新
   - ✅ **[候選提取]** +22 Channel A candidates (386 → 408)；3 個新 vault extracts；3 個新 source_registry 條目
   - ✅ **[policy_signals.json]** 實際標題更新，accuracy_verified: true
   - ✅ **[landing.html]** K1 知識平台入口頁（dark theme, particle canvas, bento grid, scroll reveal, stats counter）
   - ✅ **[v1.5.0]** backend/package.json 版本更新；npm run check ✅
   - ✅ **[index.html 重構]** landing page 成為 index.html（GitHub Pages 入口）；React SPA 改名 app.html；k1-dashboard.html 刪除
4. Pending from last session (not yet done):
   - P0.3: role_facts.json prefix fix「課程統籌主任規劃，」→ still pending (deferred)
   - Admin review: 408 candidates in queue（含 22 個 Policy Signal 候選）
   - Channel B: run `python3 dev/vault/build_wiki_index.py` 收錄 edbc002/003/005 2026
   - **Git 待執行**（本地）：`git rm -f k1-dashboard.html landing.html && git add index.html app.html && git commit && git push`
5. Next priorities (Session 78):
   - 📋 **[Git push]** 完成 index/app.html 重構的 commit + push（見上）
   - 📋 **[Channel B 更新]** `python3 dev/vault/build_wiki_index.py`
   - 📋 **[Channel A review]** app.html → Admin → 知識提煉 → 審批 408 個候選
   - 📋 **[Circular System 同步]** edb_scraper.py signal 寫入加 url + title 欄位
   - 📋 **[Dashboard Signal Badge]** 知識提煉 tab 加 pending signal 數量提示
   - 📋 Phase 3: 知識提煉 left-right split panel redesign (deferred)
   - 📋 Phase 4: Guidelines 3-level sort with sub_category (deferred)
   - 📋 Phase 5: Channel B admin prompt editor (deferred)
6. Risks / blockers:
   - Channel A searchChannelA.ts embeds ALL facts per query — acceptable for ~109 facts, monitor if exceeds 500
   - Channel B Circular System 接入明確暫停
   - Channel B/A+B requires local backend (`npm run dev`) — not deployable to GitHub Pages
   - app.html 內所有 `index.html` 內部 self-link 已是 app.html；確認無斷鏈
