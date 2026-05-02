# Session Handoff

## Current Baseline
1. Version: **v2.2.0** (K1知識平台)
2. Frontend: `index.html` K1 landing page (hero + features + CTA); `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **1,001 Channel A facts** (三層同步 ✅), **0 candidates in queue**, **wiki_index.json** 12,906 chunks; **Supabase 10,736 chunks** (1,176 無 embedding skipped)。Vault: 120 sources 提取完成（8 skipped：scanned/SPA/無直連）。
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
7. **Vault 擴充（全 AI 提取）**：`expand_vault.py` pipeline ✅ (Session 96)；`pip3 install pymupdf` ✅；PDF fetch 進行中（61 個直連 PDF）；完成後執行 `--embed` 上傳 Supabase；HTML SPA sources（43個）需另行處理（BeautifulSoup 只見靜態殼）
8. ~~**Channel A embedding cache**~~：**完成 ✅** (Session 96)；`factEmbeddingCache.ts` 線上 warm:true size:517
9. MemPalace maintenance: keep `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838` until stable.

---

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. **Online semantic regression: PASS=12 / FAIL=0** (2026-04-12) ✅

---

## Last Session Record
1. UTC date: 2026-05-02
2. Session ID: Claude_20260502_0002 (Session 99)
3. Completed:
   - ✅ **[版本號對齊]** README badge、footer、CHANGELOG v2.2.0 條目、knowledge.json、guidelines.json、app.html INITIAL_DATA 全部升至 v2.2.0
   - ✅ **[平台介紹重寫]** PlatformIntroPanel 完整重設計：動態 stat 計數動畫（1,001/10,736/39/120）、互動式 Demo 展示（3個角色查詢示例/tabbed）、三大核心功能卡、連接步驟 how-it-works、更新 sources 深色面板
4. Pending from this session (not yet done):
   - **Git commit + push**（用戶在 Terminal 執行）：
     ```
     cd ~/Downloads/Claude-edb-knowledge
     git add -A
     git commit -m "feat: v2.2.0 — version alignment + platform intro redesign with demo showcase"
     git push origin main
     ```
   - **MemPalace sync**：`python3 dev/mempalace_sync.py write`
5. Next priorities (next session):
   - 驗證 GitHub Pages 平台介紹 tab 顯示正確（互動 demo tab 切換效果）
   - 驗證 Channel B 搜尋質量（新增 g24/g29 chunks 後）
   - 考慮 g21/g22/g33 直連 PDF（視覺藝術/科技/英文課程）
6. Risks / blockers:
   - Render free tier cold start (~30s) after 15min inactivity
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings

## Session Close Checklist (每次 session 結束必須執行)
```bash
# 1. 更新 SESSION_LOG.md + SESSION_HANDOFF.md（Claude 負責）
# 2. Git commit + push（用戶在 Terminal 執行）
cd ~/Downloads/Claude-edb-knowledge
git add -A && git commit -m "session close: <描述>" && git push origin main
# 3. MemPalace sync（用戶在 Terminal 執行）
cd ~/Downloads/Claude-edb-knowledge
python3 dev/mempalace_sync.py write
```

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
