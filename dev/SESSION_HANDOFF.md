# Session Handoff

## Current Baseline
1. **Version / git**: v2.3.0；git `main`=`origin/main` HEAD = **`8bddcf2`**（S145 closeout：Q4 Phase 2 K1 endpoints LIVE + live smoke PASS；Supabase 10,594/facts 455/guidelines 152 不變）；起手自行 verify。
2. **Frontend**: `index.html` landing；`app.html` full React SPA；`t-purchase.html` draft flow；`q.html` local knowledge.json Quick Q&A。
3. **Knowledge state**: **455** Channel A facts（三層同步 byte-identical）、0 queue；Supabase **10,594** chunks；指引 4 層（161 app/152 公開/203 registry/120 vault）；CB-3 **~88% ceiling** 達成；Phase 3 全完成。
4. **Backend**: Channel A+B+A+B search APIs live at `https://edb-knowledge.onrender.com`；**Q4 Phase 2 NEW**: `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`（X-Sync-Key gated，`CHANNEL_B_SYNC_KEY` set on Render；live smoke PASS：13 欄 + anon reads embedding 1536-vec confirmed）；rate limiting 10 req/min/IP + sync 60/min。
5. **Channel A frozen @455**（Q4 Phase 1 EXECUTED S143）：knowledge.json 停更 @455（schema 不變、下游零改變）；pipeline dormant 可逆；endpoint 不刪；guidelines.json 不凍續 live @152 v2.5.0。
6. **Channel B sync（Q4 Phase 2 K1-side COMPLETE S145）**：`dev/CHANNEL_B_SYNC_SPEC.md` v0.5；`backend/src/api/channelBSync.ts` LIVE；next = Leonard 發 spec v0.5 + sync key → 下游 Circular System build consumer（跨 repo §A.3）。

## User Environment (Always Reference Before Giving Shell Commands)
- **Repo path**: `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft` (relocated 2026-05-16 Session 109; path contains a space — quote it)
- **Correct cd**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"`
- **Python script invocation**: always from repo root, e.g. `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/vault/extract_candidates.py ...`
- **Backend**: `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && npm run dev`

## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Read `dev/PROJECT_MASTER_SPEC.md` (long-term spec + cross-agent handoff knowledge: goals, architected systems, proven methods, failure lessons, locked decisions)
4b. Read `dev/HANDOFF_PACKAGE.md` (Session 110+ — clean verified-state snapshot built by empirical check, not paraphrase; sits above the §1 read set as the trusted current-state map)
4c. **Lazy-query 共用經驗庫 Playbook**（S138 接駁、AGENTS.md §1 第 5 步 + §14）：開工只讀 `…/Leonard's playbook/playbook/INDEX.md`（地圖），撞到 task 關鍵字命中 INDEX trigger 先開對應卡；唔好讀晒所有卡。
5. Confirm environment: backend needs `OPENAI_API_KEY` in `backend/.env`

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
2. **S126 (2026-05-26)** `check_freshness.py --dry-run` = **Checked: 147 / Changes: 20 / Errors: 1 / Threshold: 7 → exit 0** ✅。**Root cause of 5 連 chronic fail since 2026-04-30 = script `AttributeError` 撞 `freshness_metadata=null` (line 101) crash 喺 entry ~22，唔係 handoff 估計嘅 `if errors > 0: sys.exit(1)`（後者係次要、threshold 太嚴）**；§G.2 verify-don't-trust-docs 再中。修：`meta = src.get("freshness_metadata") or {}` + `threshold = max(5, total_checked // 20)` gate + summary 加 failed-sids list 方便 GH Actions log artifact 分析。20 EDB CHANGE detected（包 sag_2025_11 / g24 / g29 / stat_* 等）+ 1 dead URL g28 — freshness_metadata 寫返 registry 留下次 sub-task；g28 EDB URL re-discovery 列 follow-up。
3. ⚠️ **`npm run regression:semantic` 實測 2026-05-17 S113：overall=FAIL（PASS=9 / FAIL=2）**。原寫「Online semantic regression PASS=12/FAIL=0 (2026-04-12) ✅」**已 false / stale**（2026-04-12 舊值，dedup 前；S113 startup verify 教訓再現 §G.2）。兩個 FAIL 同 S1/S2 無關、Leonard 裁示**只記錄不修**：
   - **FAIL-A（真 product regression）role-bucket `finance_distinct=false`**：S111 dedup（792→455，2026-05-16）把跨角色重複摺入 `all_roles`，令 `finance.all_roles`=83 條/2832 字；`knowledgeSelector` 排序 all_roles 行先→砍 600 字，頭 ~14 條 all_roles 已蓋爆 budget，**subject_head/panel_chair 角色專屬 finance 事實永遠注入唔到** → Circular System 對該兩角色嘅 finance 注入自 2026-05-16 起退化成「只通用、無角色專屬」。無 budget 時 distinct=True（角色拆分本身冇壞）。**未修**（涉 dedup/budget/排序設計決定，待 Leonard 排）。
   - **FAIL-B（瑣碎 doc-debt）schema consistency**：`backend/scripts/semanticRegression.ts:292` 硬斷言 `version === "1.3.1"`，實際 knowledge=2.3.0 / guidelines=2.2.0。stale 測試斷言，無行為影響。**未修**。
4. `npm run check`（typecheck）✅ / `npm run build` ✅（S113 實測，未變）。

---

## Open Priorities
> 產品方向：**搜尋介面 Channel-B-only**（S119 定；CB-3 final ceiling ~88% 達成；Phase 3 全完成；Stage-2 closed）。Channel A frozen @455（Q4 Phase 1 EXECUTED）。**Q4 Phase 2 K1 端 COMPLETE（endpoints LIVE）**。

1. **下游 Circular System 接入**（K1 端完成；Leonard 發 `dev/CHANNEL_B_SYNC_SPEC.md` v0.5 + sync key → 下游 build consumer；跨 repo §A.3、K1 絕不掂對方 repo）。
2. **Display/version 一次過 fix**（approach 已定）：`knowledge.json._meta.stats`（chunks 10736→**10,594** / guidelines 39→**152**）+ README hardcoded + 統一站 version（不 bump）；§3 HIGH-risk、勿跑 `bump_version.py`（§E.8 前科）。
3. **既有 deferred**：§8b rule 2 automation / `Suppl_guide` held 待人核 / §E.10(a) ACCEPTED / FAIL-A record-only / stat_fact 2024/25 stale / freshness 週跑觀察 / 57014 cold-start monitor。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）

## Last Session Record
1. UTC date: 2026-06-05
2. Session ID: Claude_20260605_1513 (S145)
3. Completed:
   - ✅ **[起手核實]** HEAD `cb498c1`==origin/main / facts 455 三層 byte-identical / Supabase 10,594 雙讀 / guidelines 152 v2.5.0 / knowledge.json frozen 455 v2.3.0 / onrender /health 200 warm。Egress 全通。
   - ✅ **[Spec v0.4 — 下游覆文納入]** §11.2 RESOLVED（embedding 路 1 `text-embedding-3-small` / `include_embedding=true` 零重嵌）；manifest +`topic`/`content_type`；bootstrap 71 批 pacing；向量 pgvector `"[…]"` string + L2-norm≈1.0 實測；profile 校正（ephemeral cron 3×/日 + file-based numpy）。spec → v0.4。commit `3a81cc8`。
   - ✅ **[Q4 Phase 2 endpoint build]** NEW `backend/src/api/channelBSync.ts`（manifest+chunks、X-Sync-Key gate、自有 60/min+daily budget、anon-REST、NO CORS）+ env/wikiRepository/server/.env.example。5-lens 對抗審核（40 agents）→ 修 4 真（502 洩內文 / budget TOCTOU+dup / cache thundering-herd singleflight / in.() id-format guard）；spec → v0.5（§13 澄清）。typecheck+build exit 0；本地 gate smoke PASS。commit `7b82e01`。
   - ✅ **[Deploy + live smoke PASS]** Render auto-deploy → Leonard set `CHANNEL_B_SYNC_KEY` + redeploy → live smoke：chunks 200 全 13 欄 + anon 讀到 `embedding` 1536-vec ~19KB（路 1 confirmed）+ 400 guard + key gate。**K1 端 Q4 Phase 2 COMPLETE**。commit `8bddcf2`。
   - ✅ **[§4a archive]** SESSION_LOG 412→168 行（S141/S142/S143 archived → `dev/archive/SESSION_LOG_2026_Q2.md`）。
   - ✅ **[NUL byte fix]** 1 NUL byte stripped from `dev/SESSION_HANDOFF.md`。
4. Pending: 下游 Circular System consumer build（跨 repo、Leonard 主導）；Display/version 一次過 fix（approach 已定）。**0 outstanding bug**。
5. Next priorities: 下游接入（spec v0.5 + key）；Display/version fix；既有 deferred。
6. Risks / blockers:
   - 🟢 **0 outstanding bug**。K1 端 Q4 Phase 2 COMPLETE + live smoke PASS。
   - 🟡 **下游 consumer build pending**（跨 repo §A.3；可觀察 manifest scan 對 free-tier DB 影響；key 季度輪換）。
   - ⚠️ **Display/version fix**（approach 已定、§3 HIGH-risk 出 PLAN、勿跑 `bump_version.py` §E.8）。
   - 既有：Channel A frozen @455；57014 transient(retry)；FAIL-A(record-only)；§E.10(a) ACCEPTED conditional；q.html/A·AB dormant 勿清；Stage-2 closed；egress 每次自測；路徑空格雙引號；wiki_chunks 欄名 `text`；結構天花板源勿再 ingest；改 Draft code/data commit 必入 SESSION_LOG；init_backup gitignored。
7. ✅ **S145：Q4 Phase 2 spec v0.3→v0.5 + K1 endpoints BUILT + deployed LIVE + 5-lens 審核 + live smoke PASS（anon embedding confirmed）。** commits `3a81cc8`→`7b82e01`→`8bddcf2`。

## Previous Session Record
1. UTC date: 2026-06-05
2. Session ID: Claude_20260605_1338 (S144)
3. Completed: Q4 Phase 2 模型決策（Incremental sync）+ NEW `dev/CHANNEL_B_SYNC_SPEC.md` spec v0.1→v0.3（過對抗審核 hardening，修 2 blocker）+ §11 4 決策 Leonard RESOLVED + 下游 prompt。全 docs-only、0 product 改。
4. Pending at time: endpoint build + 下游 embedding model 確認。
5. commits: `00d5291`→`adbeabb`→`5cefe9b`→`cb498c1`（closeout）。


## Session Close Checklist (每次 session 結束必須執行)
```bash
# 1. 更新 SESSION_LOG.md + SESSION_HANDOFF.md（Claude 負責）
# 2. Git commit + push（Leonard S115 授權「push 係你做」— Claude 執行；加指定檔，勿 -A）
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"
git add <指定治理/文檔檔> && git commit -m "session close: <描述>" && git push origin main
# （MemPalace sync 已於 S115 移除 — 本專案不再使用 MemPalace）
```

## Supabase Technical Notes (Channel B)
- Project: `edb-knowledge` at `https://youkcekbrbywuqjxgibe.supabase.co`
- Table: `public.wiki_chunks` — vector(1536), IVFFlat index **lists=60** (per `backend/supabase/schema.sql`, the authoritative DDL — S115 §0b corrected: prior "lists=50" + "2,822 rows" were drift; local wiki_index build artifact = 12,906 chunks / 120 src; live Supabase row-count + index not introspected this session)
- Function: `match_wiki_chunks(query_embedding text, match_threshold double precision DEFAULT 0.1, match_count integer DEFAULT NULL)` — **this (text) is the LIVE signature the backend uses (sends embedding as string); schema.sql had drifted to `vector(1536)` and applying it created a 2nd overload → PGRST203 → Channel B 0 (S116 live incident). Always INSPECT live `pg_get_functiondef` before any RPC DDL — see PROJECT_MASTER_SPEC §E.13.**
  - Uses `query_embedding::vector` cast internally; ordered by cosine DESC; null match_count = return all above threshold
  - **S116: now `language plpgsql VOLATILE` with body `set local ivfflat.probes = 8`** (was `language sql stable`, probes=1 default). Mechanism constraints (all empirically hit): function-level `SET ivfflat.probes` clause → 42501 (Supabase blocks ext-GUC clause); `SET`/`SET LOCAL` in STABLE/IMMUTABLE or `language sql` → 0A000 (must be VOLATILE plpgsql). probes=8≈sqrt(lists=60). Production Channel B currently runs probes=8 (Stage-1 FULL PASS, S116). Reference: auto-memory reference_supabase_pgvector_probes.
  - DDL needs Supabase Dashboard SQL Editor (Leonard's auth); no CLI/psql/DB-url/service-via-PostgREST path. Claude prepares exact APPLY+ROLLBACK+read-only INSPECT; Leonard applies.
  - ✅ **S117 FIXED** (was S116 promote-blocker): `searchCombined.ts` `.catch` now returns `failedChannelBResponse` → combined surfaces `channel_b_status:"error"` + `CHANNEL_B_ERROR_REASON`, distinct from genuine unconfigured (`channel_b_status:"unconfigured"` + 未配置). Real Channel B failures now visible to monitoring/eval via the `channel_b_status` discriminator (no more fake "未配置" masking). Genuine-unconfigured path (`searchChannelB.ts` `isSupabaseConfigured()` guard) unchanged. Dedicated `/api/search/channel-b` still recommended for live-grade (no route-level catch — methodology unchanged). Deploy: Render auto-deploys on push to main.
  - 🔴 **S118: free-tier probes=8 intermittent statement-timeout** — live-verify saw 2/5 RPC calls return HTTP 400 / Supabase `57014` "canceling statement due to statement timeout" at probes=8 (succeeded on retry; one was cold-start, one intermittent ~60s after a healthy call). Production-availability risk independent of retrieval correctness; post-S117 it correctly surfaces as `channel_b_status:"error"` (not fake "未配置"). Open Priority — options: lower probes / app-level retry / paid tier. probes=8-live itself still NOT independently introspected (audit-flagged; read-only `pg_get_functiondef`/`proconfig` SQL prepared, not yet run).
  - **S118: Channel B routing +4 dedicated selective routes** (`searchChannelB.ts` `TOPIC_KEYWORDS`/`SOURCE_SETS`/`QUERY_EXPANSIONS`, first-match before `finance`): cpd, kg_admission, conduct, steam (PLAN-1b promote; fixed cutoff unchanged; SAG in cpd/conduct bounded by per-source quota cap=3 → §E.3-safe). Stage-2 adaptive combo abandoned (non-viable; do not revive).
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
