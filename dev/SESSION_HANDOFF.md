# Session Handoff

## Current Baseline
1. **Version / git**: v2.3.0（knowledge 凍結 @2.3.0、guidelines @2.5.0，無 bump — S151 app.html 改動唔 bump，displayVersion 由 `data._meta.version` 動態取）；git `main`=`origin/main` HEAD = **S151 commits**（`503b07b` admin-removal + display/de-jargon closeout commit，疊喺 `1fb4c22` S149-S150 上）；起手自行 verify HEAD==origin/main + Supabase 13,667。
2. **Frontend**: `index.html` landing；**`app.html` = Channel-B-only 唯讀 SPA（S151：admin 登入閘 + 知識提煉/知識管理 tab + CRUD/匯出/候選審核 全移除；淨 3 tab〔平台介紹/政策搜尋/指引文件〕+ 文件預覽抽屜；app.html 4100→2935 行 −1176）**；`t-purchase.html` draft flow（dormant）；`q.html` local knowledge.json Quick Q&A（dormant）。
3. **Knowledge state**: **455** Channel A facts（三層同步 byte-identical，md5 `720f5f`）、0 queue；Supabase **13,667** chunks（S148 13,473 → **S149 安全指引 +115**〔g18 校車+9 / g21 視藝+48 / g22 科技+58，文字層〕 → **S150 gifted +94**〔gifted_policy_docs +19 / gifted_tp_resource_kit +41 / gifted_osalp_compendium +19〕）；**新增 2 條 dedicated route**：`safety`(+keyword 校車/視藝安全/科技安全)、`gifted`(+keyword 資優/資賦)；指引（161 app / 152 公開 / **205** registry）；**display sync EXECUTED**（`_meta.stats` chunks→**13,667** 三層 byte-identical + app.html + K1_API_SPEC + README；guidelines 152 不變、無 bump、facts 455 不變）；Phase 3 全完成。**S151：app.html admin UI（知識提煉/知識管理/登入/CRUD/匯出）全移除 → 公眾完全 Channel-B-only；以上知識數字、role_facts/knowledge.json/guidelines.json 凍結資料與對外契約零接觸（admin 只係 client-side localStorage、無真實寫能力）。**
4. **Backend**: Channel A+B+A+B search APIs live at `https://edb-knowledge.onrender.com`；**Q4 Phase 2 NEW**: `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`（X-Sync-Key gated，`CHANNEL_B_SYNC_KEY` set on Render；live smoke PASS：13 欄 + anon reads embedding 1536-vec confirmed）；rate limiting 10 req/min/IP + sync 60/min。
5. **Channel A frozen @455**（Q4 Phase 1 EXECUTED S143）：knowledge.json 停更 @455（schema 不變、下游零改變）；pipeline dormant 可逆；endpoint 不刪；guidelines.json 不凍續 live @152 v2.5.0。
6. **Channel B sync（Q4 Phase 2 全鏈完成 S146）**：K1 端 `dev/CHANNEL_B_SYNC_SPEC.md` v0.5 + `backend/src/api/channelBSync.ts` LIVE（manifest/chunks 401-gated 健康）；**下游 Circular System consumer 已 build 好 + 完成工作**（S146 Leonard 確認）；交接包 `dev/CHANNEL_B_HANDOVER.md`。incremental sync 自動帶新源 delta（本 session +11 源，下游下次 poll 自動執）。

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
> 產品方向：**全棧 Channel-B-only**（**S151：app.html admin 登入 + Channel-A 策展 UI〔知識提煉/知識管理/CRUD/匯出〕全移除**；Phase 3 全完成；Stage-2 closed）。Channel A frozen @455（資料仍餵對外契約）。**Q4 Phase 2 全鏈完成**。主線 **0 outstanding bug**；以下全屬可選、冇緊急。

1. **Channel B 補入庫 — 實質完成**（S149 安全指引 g18/g21/g22 + S150 gifted 3 源全入；**真‧未入‧現行內容缺口核實清空** — B-group sibling-dup 抽驗 6/16 深層內容確認覆蓋〔sci→g36 / tech→tech_kla / pshe→g35 / ma→ma_kla 同一 PDF / pri_science / ph_pri〕）。餘 ~30 registry 未入源全屬 deprecated / sibling-dup / 舊版噪音，**建議唔做**。新源入庫流程不變（pre-flight 驗文字層 → fetch_extract〔文字層〕/ ocr_extract〔掃描·CID〕 → ingest_one_source → 加 `SOURCE_SETS` allowlist〔S135〕 → display 6 處 → routed smoke）。餘 10 個 dup 未深驗（可選補驗）。
2. **NEW 自動發現機制（S150）**：`dev/source/discover_sources.py` + `.github/workflows/discover_check.yml`（每週一 10:00 UTC，crawl 已登記 EDB index 頁 diff 出未登記新文件 → 開 `new-source-discovery` GitHub Issue）。**未跑過全量**；可選手動 `workflow_dispatch` 或下次 session 跑全量 triage（噪音多 = review list 非 auto-ingest；JS 頁 flag `js_suspect`）。freshness（每週一 09:00）續監察已登記源改版/死链；上次「7 changed」經核實 = head-metadata baseline-seed artifact、**0 真改**。
3. **既有 deferred / monitor-only**：**gifted 查詢含「教師培訓/CPD」詞 → route 去 cpd**（first-match precedence、gifted_tp_resource_kit 唔 surface；純 資優 query 正常；要 fix = 移 `gifted` 前於 `cpd`）/ gifted_osalp_compendium = catalogue、general query 排名低（in-route searchable）/ phys_sss routed-UI 限制（Leonard 接受）/ §8b rule 2 automation / Suppl_guide held / §E.10(a) ACCEPTED / FAIL-A record-only / stat_fact 2024-25 stale / 57014 cold-start / g38 stale-2003-ranking / `stats.sources`=120 cosmetic-stale（live ~199）。**S151 已修：app.html QAPanel 副標 + index.html chunks fallback `10,736`→`13,667` data-driven（chip task_672056cf done）；UI 去咗 Channel A/B 內部字眼。**

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）

## Last Session Record
1. UTC date: 2026-06-08
2. Session ID: Claude_20260608_1335 (S151)
3. Completed:
   - ✅ **[起手核實 verify-don't-trust 全 live]** HEAD `1fb4c22`==origin/main clean / facts 455 三層 byte-identical(md5 `720f5f`) / Supabase **13,667**(content-range) / guidelines 152 / knowledge.json frozen + stats 13,667·152 / onrender /health 200 cache_a 455 + manifest 401-gated / playbook INDEX。
   - ✅ **[S151 移除 app.html admin 登入 + Channel-A 策展 UI]** Leonard 指示「下游 Circular System 已轉 Channel B 不再食 Channel A → 可刪登入」。核實 code：登入閘只守 Channel A 人工策展（app.html 0 個 Channel B admin 功能）。§3 HIGH-risk PLAN → Leonard 確認 scope（**完整移除 incl 死碼** + 455 facts 從 app.html UI 消失 + 完全 Channel-B-only）。移除：🔒登入掣 + `AdminPasswordModal` + `ADMIN_HASH`/`sha256` + 知識提煉/知識管理 2 tab + sidebar + CRUD/匯出/批准 + `FactCard`/`StatusBadge`/`RoleBadge`/`EditModal`/`ExportModal`/`CandidateReviewPanel` + snapshot infra(`buildAdminSnapshot`/`loadLocalSnapshot`/`migrateSnapshot`/`downloadJson`) + `INITIAL_REVIEW_STATE`/`INITIAL_CANDIDATES` + mobile admin bar + 2 orphaned `<script>` 載入。`App()` 收窄；`VALID_VIEWS=['qa','guidelines','about']`；router→about/guidelines/QAPanel。**app.html 4100→2935 行 −1176。** 手法：anchored-splice Python one-off（15 區、各 assert anchor，跑完即刪）+ 2 follow-up Edit。
   - ✅ **[QC 雙獨立流 PASS]** (1) grep parity：~40 admin symbol 0 dangling + 0 leftover admin label；(2) live 瀏覽器 render（static server）：Babel 0 console error、3 公開 tab render、About stat 定格 **455/13,667/161/120**（同改前一致）、guidelines 161 文件、無 login/admin UI、screenshot 留證；(3) 獨立對抗 review subagent **VERDICT PASS**（braces 平衡 / router 正確 / ReactDOM intact / props 滿足）。
   - ✅ **[同 session follow-up — display + de-jargon]** Leonard「快手 update version/數字 + 去掉顯示 Channel A/B 字眼」：app.html QAPanel 副標 + index.html chunks `10,736`→`13,667`(data-driven from `_meta.stats.chunks`)；About sub / result badge / feature subtitle / footer 去 'Channel A/B'·'通道 A/B'·'管理中心'(code 識別符保留、唔顯示)；version 核實一致 2.3.0 knowledge / 2.5.0 guidelines。QC：live render Babel 0 error + About 455/經人工審核·13,667/語義向量索引 + 搜尋副標 13,667 + footer v2.3.0 + 0 可見 jargon + index.html 3×13,667。
   - ✅ **[Doc sync]** PROJECT_MASTER_SPEC §E.10(a) **CLOSED-BY-REMOVAL** + §F.11 新 locked decision + §B.1 admin rows 劃走；CODEBASE_CONTEXT tabs + AI-log；README 功能簡介更新 Channel-B-only + 劃走 admin rows；本 handoff + SESSION_LOG。
4. Pending（全屬可選）: discovery 全量 triage / 餘 10 B-group dup 深驗。**0 outstanding bug。**
5. Next priorities: 見 Open Priorities。
6. Risks / blockers:
   - 🟢 **0 outstanding bug**。
   - ⚠️ **app.html admin/Channel-A 策展功能已永久移除（S151）**；將來如需重建 admin/write surface 必由零走 §3 HIGH-risk PLAN + 真 server-side auth，**不可復活 client-side cosmetic gate**（§E.10/§F.11）。Rollback = git revert app.html commit。
   - ⚠️ 留低：`deepClone`(generic 未用 helper，無害) + 部分 inert admin CSS rule（已 flag、未移）。
   - ⚠️ **chunks 係 moving display number** — 補入庫後同步 6 處（3 層 `_meta.stats` + app.html + K1_API_SPEC + README）；app.html QAPanel 副標 + index.html chunks 已轉 **data-driven**（S151，自動跟 `_meta.stats.chunks`、毋須再手改）。
   - 既有：gifted+CPD route precedence(monitor) / gifted_osalp catalogue 排名低 / phys_sss routed-UI 限制(Leonard 接受) / Channel A frozen @455 / 57014 transient(retry) / Stage-2 closed / 大 OCR pace TPM / 新源必加 SOURCE_SETS allowlist(S135) / egress 每次自測 / 路徑空格雙引號 / wiki_chunks 欄名 `text` / 結構天花板源勿再 ingest / 改 Draft code/data commit 必入 SESSION_LOG / 勿改 canonical chunker / `stats.sources`=120 cosmetic-stale。
7. commits: `503b07b`(S151 admin-removal) → **S151 closeout commit**(display/de-jargon：app.html + index.html + governance docs + SESSION_LOG archive)。

## Previous Session Record
1. UTC date: 2026-06-08
2. Session ID: Claude_20260608_1223 (S149-S150)
3. Completed: Channel B 補入庫實質完成 — S149 安全指引 g18/g21/g22 +115 + S150 gifted 6 源 +94（gifted_policy_docs + tp_resource_kit + osalp_compendium）→ Supabase 13,473→**13,667**；新增 safety + gifted 2 條 dedicated route；NEW `dev/source/discover_sources.py` + 每週 discover_check.yml(detection-only)。registry 203→205、md5→720f5f。真‧未入‧現行內容缺口核實清空。
4. commits: `e763f9f`→`79cea74`→`497d6af`→`180ec67`→`1fb4c22`(closeout)。


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
