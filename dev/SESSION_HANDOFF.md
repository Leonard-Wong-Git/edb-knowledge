# Session Handoff

## Current Baseline
1. Version: **v2.1.1** (K1知識平台)
2. Frontend: `index.html` S1 home; `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **1,001 Channel A facts** (三層同步 ✅: `dev/knowledge/role_facts.json` = `role_facts.json` = `knowledge.json`, 全部 v2.1.1), **0 candidates in queue**, **wiki_index.json** 2,874 chunks / 125 MB.
4. Backend: Node.js TypeScript backend Phase 1 search APIs complete; **Channel A online at `https://edb-knowledge.onrender.com`** (Render free tier); Channel B/A+B require Phase 2 (Supabase pgvector — wiki_index.json not in git).
5. Product copy baseline: Traditional Chinese UI; no public internal design/dev/backend commands; template flows say "建立草稿/整理" until formal export/generation is connected.
6. MemPalace: shared install `/Users/leonard/mempalace/.venv`, palace `/Users/leonard/mempalace/palace`, wing `claude_edb_knowledge`; shared palace recovered and mined successfully.

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

### Decision 1 — Public Entry + Full Workspace
```
index.html  ←  EDB S1 Home / document workspace entry
    │
    ├── q.html                  ← Quick Q&A (local knowledge.json search)
    ├── t-purchase.html         ← Template detail + draft flow
    └── app.html                ← K1知識平台 full React workspace

app.html
    ├── 🔍 政策搜尋              ← 已核實資料 / 來源文件 / 合併搜尋
    ├── 📚 指引文件庫              ← 3-level sort: category → sub_category → time desc
    ├── 📄 通告分析
    ├── ℹ️  平台介紹
    ├── ✍️  知識提煉（Admin）     ← 左右分欄佈局 + 即時行內修訂
    └── ⚙️  知識管理（Admin）
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

## Open Priorities
1. ~~Circular System: `_write_policy_signal()` — deferred to Circular System side.~~ → **規格文件 `dev/CIRCULAR_SYSTEM_INTEGRATION.md` 已建立 ✅**
2. ~~Phase 4: 指引文件庫 dual sort with `sub_category`~~ → **完成 ✅**（148 items 分組，category → sub_category → year desc）
3. ~~Render 部署 Channel A~~ → **完成 ✅** `https://edb-knowledge.onrender.com` live；batch embed fix 已推送（Session 90）
4. Optional UI QA: run a browser visual pass on `index.html`, `q.html`, `t-purchase.html`, and `app.html`. ← **下一個優先項**
5. **Phase 2 — Channel B online**: migrate `wiki_index.json` (2,874 embeddings) to Supabase pgvector; update `wikiRepository.ts`; add rate limiting before public launch.
6. MemPalace maintenance: keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until the recovered shared palace remains stable.

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. **Online semantic regression: PASS=12 / FAIL=0** (2026-04-12) ✅

---

## Last Session Record
1. UTC date: 2026-04-30
2. Session ID: Claude_20260430_0003 (Session 91)
3. Completed:
   - ✅ **[Batch embed fix]** 修正 `searchChannelA.ts` — 以單次 batch API call 取代 Promise.all(1,001 個別 embedding calls)；修正 Render "Failed to fetch" 根本原因；TypeScript build 通過；已 push
   - ✅ **[embeddingClient.ts]** 新增 `BatchEmbedFn` type 及 `embed.batch()` 方法
   - ✅ **[README 全面重寫]** 反映 v2.1.1 現況：app.html、backend Render URL、Channel A/B 架構、文件結構、本地開發指引
   - ✅ **[SESSION_HANDOFF 更新]** Session 91 記錄完整
4. Pending from last session (not yet done):
   - Channel A online search 待用戶在 app.html 驗證（Render 重新部署後）
5. Next priorities (next session):
   - 🗄️ **Phase 2 — Channel B online**：wiki_index.json (2,874 embeddings) → Supabase pgvector；更新 wikiRepository.ts；Render 加環境變數；加 rate limiting
   - 🔍 **驗證 Channel A online search**（如尚未確認）
   - 📋 **Optional UI QA browser pass**
6. Risks / blockers:
   - Channel A search: 每次查詢仍需 2 次 API call（1 query + 1 batch 1,001 facts）。可考慮啟動時預計算並 cache fact embeddings。
   - Render free tier cold start (~30s) after 15min inactivity
   - Channel B/A+B requires Phase 2 (Supabase) — wiki_index.json not in git
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
