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

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. **Online semantic regression: PASS=12 / FAIL=0** (2026-04-12) ✅

---

## Open Priorities
1. **線上端對端驗收**（用戶 Terminal）— 重 curl 教師病假 / 教師註冊 / 幼稚園學習領域三條 query，確認來源配額排序改善效果
2. **學校行政手冊重複文件去重**（Supabase SQL）— g24 同 sag_2025_11 同份文件兩次 ingestion，重複 715 chunks；先 dry-run 驗證 sag 涵蓋 g24 全部內容才能執行 DELETE
3. **8 個無法擷取嘅 source triage**（按 memory 規範先驗 source 質素，唔好馬上設計 fallback pipeline）
4. **評估視藝/科技/英文課程指引（g21/g22/g33）直連 PDF 必要性**
5. **Channel A embedding cache 監察**（warm:true size:517 已穩定，視乎 token usage 趨勢）

## Last Session Record
1. UTC date: 2026-05-02
2. Session ID: Claude_20260502_0004 (Session 101)
3. Completed:
   - ✅ **[來源配額排序 ship]** wikiRepository.ts WikiSearchOptions 加 `maxPerSource`；searchWiki 加 over-fetch（topK×5）+ quota gate（按 score DESC 行，每 source 達 cap 後 skip）
   - ✅ **[caller-side 計算]** searchChannelB.ts 計算 `maxPerSource = max(2, ceil(top_k / 3))`；單 source allowlist 時自動 disable
   - ✅ **[本地 sanity test]** mock chunks 跑 quota gate：sag×4 + va×3 + g29×1 + topK=5 cap=2 → 結果 sag×2 + va×2 + g29×1（g29 score 0.50 雖輸俾 sag-3 0.55 但配額釋位令佢入榜）
   - ✅ **[Memory feedback]** 「對話禁用內部代號 F1/F2/F3 等」存入 feedback_no_internal_codenames_in_chat.md
4. Pending from this session (not yet done):
   - Git commit + push（含 wikiRepository + searchChannelB 改動 + Session 101 entry）
   - 用戶 Terminal 重 curl 三條 query 對比效果
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 收線上驗收結果再決定是否要 tune cap 比例
   - 學校行政手冊重複文件去重（資料層 cleanup，先 dry-run）
   - 8 個無法擷取嘅 source triage
6. Risks / blockers:
   - Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
   - Render free tier cold start (~30s) after 15min inactivity
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings
   - 學校行政手冊去重高風險（SQL DELETE）— 必先 dry-run 驗證 sag 涵蓋 g24 全部內容
   - 配額排序 over-fetch（topK×5）會增加 Supabase 帶寬；以 top_k=8 計即 40 rows 上限，影響不大但要監察

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
