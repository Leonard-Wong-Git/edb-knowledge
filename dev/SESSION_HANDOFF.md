# Session Handoff

## Current Baseline
1. Version: **v2.1.2** (K1知識平台)
2. Frontend: `index.html` S1 home; `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **1,001 Channel A facts** (三層同步 ✅), **0 candidates in queue**, **wiki_index.json** 2,874 chunks / 125 MB; 2,822 in Supabase.
4. Backend: Node.js TypeScript backend all search APIs complete; **Channel A + B + A+B online at `https://edb-knowledge.onrender.com`**; rate limiting 10 req/min/IP (sliding window, in-memory).
5. Channel A: 改用 backend semantic search + LLM synthesis（所有三個 channel 均有整理答案）；min_score A=0.1, B/AB=0.15；case-insensitive keyword fallback 已移除。
6. Channel B topic filtering（Session 94 完成）：keyword → category → source allowlist → query expansion。採購/財務 → g01+g02+coa_imc（排 SAG）；HR/假期 → g04+g05+sag；課程 → 課程指引。g04 仍為 knowledge-based extract（非 PDF）。
7. Product copy baseline: Traditional Chinese UI; no public internal design/dev/backend commands.
8. MemPalace: shared install `/Users/leonard/mempalace/.venv`, palace `/Users/leonard/mempalace/palace`, wing `claude_edb_knowledge`.

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
2. ~~Phase 4: 指引文件庫 dual sort with `sub_category`~~ → **完成 ✅**
3. ~~Render 部署 Channel A~~ → **完成 ✅**
4. ~~Phase 2 — Channel B online~~ → **完成 ✅**
5. ~~Rate limiting~~ → **完成 ✅** 10 req/min/IP sliding window (Session 93)
6. ~~**Channel B topic filtering**~~ → **完成 ✅** (Session 94)：keyword detection + source allowlist + query expansion；採購/財務/HR/課程均驗證通過
   - ~~Channel B UI 加免責說明~~ → **完成 ✅** (Session 95)
   - ~~g04 重新從 PDF 提取~~ → **vault 更新 ✅** (Session 95)；待用戶執行 `python3 dev/update_g04_supabase.py` 更新 Supabase
7. **Vault 擴充（全 AI 提取）**：104 個 source registry 來源未提取；設計全 AI pipeline 從 PDF → vault → wiki_index → Supabase
8. **Channel A embedding cache**：啟動時預計算 1,001 facts embeddings，消除每次查詢的 batch call overhead
9. MemPalace maintenance: keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until stable.

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. **Online semantic regression: PASS=12 / FAIL=0** (2026-04-12) ✅

---

## Last Session Record
1. UTC date: 2026-05-01
2. Session ID: Claude_20260501_0001 (Session 92)
3. Completed:
   - ✅ **[Phase 2 — Channel B online]** 全流程完成：Supabase project 建立 → pgvector schema + match_wiki_chunks function → 2,822 chunks 上傳 → Render env vars 設定 → wikiRepository.ts 改用 direct fetch() RPC
   - ✅ **[Supabase permission fix]** 根本原因：anon role 缺少 `GRANT USAGE ON SCHEMA public`；執行後 /debug-b 確認 table_rows ✅ + RPC ✅
   - ✅ **[Upload dedup fix]** upload_wiki_to_supabase.py 改為先全局 dedup by id 再批次，解決 batch 內重複 ID 的 conflict error
   - ✅ **[wikiRepository.ts]** 改用 direct fetch() + toFixed(8) encoding；移除 supabase-js 依賴（pgvector text cast 問題）
   - ✅ **[Debug cleanup]** 移除 /debug-b endpoint 及 wikiRepo verbose logging；build ✅
   - ✅ **[系統資訊圖 prompt]** 寫好完整 Gemini/ChatGPT infographic prompt（見 session transcript）
4. Pending from last session (not yet done):
   - 使用者需在 Terminal 執行 `git push origin main`（sandbox 無法 SSH）
   - 建議在 app.html 驗證 Channel B 及 A+B combined 搜尋結果 total_b > 0
5. Next priorities (next session):
   - 📋 **Optional UI QA browser pass**（index.html, q.html, t-purchase.html, app.html）
   - ⚡ **Rate limiting**：公開前建議加 rate limit（10 req/min per IP），可用 node-rate-limiter-flexible
   - ⚡ **Channel A embedding cache**：啟動時預計算 1,001 facts embeddings，消除每次查詢的 batch call
6. Risks / blockers:
   - Render free tier cold start (~30s) after 15min inactivity
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings

## Supabase Technical Notes (Channel B)
- Project: `edb-knowledge` at `https://youkcekbrbywuqjxgibe.supabase.co`
- Table: `public.wiki_chunks` — 2,822 rows, vector(1536), IVFFlat index (lists=50)
- Function: `match_wiki_chunks(query_embedding text, match_threshold float, match_count int DEFAULT NULL)`
  - Uses `text::vector` cast internally
  - Ordered by cosine similarity DESC
  - No match_count limit when not supplied (returns all above threshold)
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
