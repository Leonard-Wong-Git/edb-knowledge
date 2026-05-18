# Session Handoff

## Current Baseline
1. Version: **v2.3.0**；git `main`=`origin/main` HEAD = **S116 closeout commit（commit *後* HEAD 自然推進＝正常非 desync，§G.2；下次起手自行 verify，應 ≥ S116 closeout commit）**。S116 改 **`backend/supabase/schema.sql`**（真實 live text 變體 + plpgsql volatile + `SET LOCAL ivfflat.probes=8` + 修正引致 PGRST203 事故嘅 vector→text 簽名 drift）= **Draft code/data 改動，已 commit+push 並入本 SESSION_LOG（守 S111 教訓）**。**CB-2 PLAN-1 v2 Stage 1 已落地＋FULL PASS：生產 Supabase `match_wiki_chunks` 現行 probes=8（Leonard Dashboard 套用，非 git）**；Stage-1 **FULL CLEAN PASS（recall：clean-verify v2 全 12 OK、6/6 ANN-recoverable flip 0→>0、0 回歸；§C：幼稚園收生/防賄 8/8 OK、gold-consistency 全一致、p90<4.2s → HARNESS/LOAD artifact、probes=8 sound 非真 free-tier 風險）**。Stage 2 adaptive threshold **未做**；CPD→PLAN-1b；masking-defect = 獨立 promote-blocker（flag+defer）。**PLAN-1 promote 未完成（Stage 2 未做），勿宣稱 released。**
2. Frontend: `index.html` K1 landing page (hero + features + CTA); `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **455 Channel A facts** (三層同步 ✅ byte-identical；2026-05-16 dedup 由 792 → 455，移除 275 條跨角色完全重複 + 合併 36 組相近事實，commit `711f911`，reversible log `dev/DEDUP_LOG_2026-05-16.md`；早前 Session 102 已 1,001 → 792), **0 candidates in queue**, **Supabase 10,736 chunks**。Vault: 120 sources 提取完成。**指引數字 4 層（148 app 內庫 / 39 公開 guidelines.json / 151 source_registry / 120 vault-extracted）見 PROJECT_MASTER_SPEC §B.1 釐清框 — 39 是否擴到 148 = OPEN DECISION，未收斂**。
4. Backend: Node.js TypeScript backend all search APIs complete; **Channel A + B + A+B online at `https://edb-knowledge.onrender.com`**; rate limiting 10 req/min/IP (sliding window, in-memory).
5. Channel A: 改用 backend semantic search + LLM synthesis（所有三個 channel 均有整理答案）；min_score A=0.1, B/AB=0.22（2026-05-16 Session 110 對齊實際 code default，原寫 0.15 已過時）；case-insensitive keyword fallback 已移除。
6. Channel B topic filtering（Session 94 完成）：keyword → category → source allowlist → query expansion。採購/財務 → g01+g02+coa_imc（排 SAG）；HR/假期 → g04+g05+sag；課程 → 課程指引。g04 仍為 knowledge-based extract（非 PDF）。
7. Product copy baseline: Traditional Chinese UI; no public internal design/dev/backend commands.
8. **MemPalace REMOVED 2026-05-18 (S115，Leonard 指示)** — repo-local `.venv`/`mempalace.yaml`/`entities.json` + `dev/mempalace_sync.py` 已刪、治理引用已剝除；本專案不再用 MemPalace。Shared palace `/Users/leonard/mempalace/palace` 為其他專案保留不動；本專案 wing 之 drawers 變孤兒（mempalace CLI 無 wing-delete）。**Leonard S115 裁示：留低孤兒、永久唔郁 shared palace（§3 divergence RESOLVED）** — 未來 session 勿再 raise 或嘗試 purge。

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
2. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅
3. ⚠️ **`npm run regression:semantic` 實測 2026-05-17 S113：overall=FAIL（PASS=9 / FAIL=2）**。原寫「Online semantic regression PASS=12/FAIL=0 (2026-04-12) ✅」**已 false / stale**（2026-04-12 舊值，dedup 前；S113 startup verify 教訓再現 §G.2）。兩個 FAIL 同 S1/S2 無關、Leonard 裁示**只記錄不修**：
   - **FAIL-A（真 product regression）role-bucket `finance_distinct=false`**：S111 dedup（792→455，2026-05-16）把跨角色重複摺入 `all_roles`，令 `finance.all_roles`=83 條/2832 字；`knowledgeSelector` 排序 all_roles 行先→砍 600 字，頭 ~14 條 all_roles 已蓋爆 budget，**subject_head/panel_chair 角色專屬 finance 事實永遠注入唔到** → Circular System 對該兩角色嘅 finance 注入自 2026-05-16 起退化成「只通用、無角色專屬」。無 budget 時 distinct=True（角色拆分本身冇壞）。**未修**（涉 dedup/budget/排序設計決定，待 Leonard 排）。
   - **FAIL-B（瑣碎 doc-debt）schema consistency**：`backend/scripts/semanticRegression.ts:292` 硬斷言 `version === "1.3.1"`，實際 knowledge=2.3.0 / guidelines=2.2.0。stale 測試斷言，無行為影響。**未修**。
4. `npm run check`（typecheck）✅ / `npm run build` ✅（S113 實測，未變）。

---

## Open Priorities
> 產品方向 S112 roadmap：**P1 搜尋相關性 → P2 分類 148 → P3 數字對齊**（39→148 deferred）。**S114 Leonard 定新焦點：P1 內聚焦 Channel B 效果**（唔單做一 channel，用 agent team 互補）。順序鎖定，未得 Leonard 確認唔好跳。
1. **🟢 CB-2 PLAN-1 Stage-1 = FULL CLEAN PASS（已最終裁定，S116）。下一步＝問 Leonard 排序**：recall clean-verify v2 全 12 OK、6/6 ANN-recoverable flip 0→>0、0 回歸；§C 隔離 8×重試 幼稚園收生 8/8·防賄 8/8·採購 7/8、gold-consistency 全一致、p90<4.2s → HARNESS/LOAD artifact、probes=8 sound（之前 09/10 間歇失敗 = v1 combined-masking+限流 量度 artifact）。生產 Supabase 現行 probes=8。下一步三選一待 Leonard：(a) **Stage 2 adaptive threshold**（同一 §3 HIGH-risk promote gate 內、完成 PLAN-1 promote）(b) **PLAN-1b**（CPD/expansion，全 Testing/）(c) 先修 **masking-defect**。報告 `Testing/poc-retrieval/eval/CB2_STAGE1_report.md`。
2. **CB-2 PLAN-1 Stage 2 — adaptive threshold（待 Stage-1 最終 PASS + Leonard go，同一 §3 HIGH-risk promote gate 內）**：`searchChannelB.ts:346` per-query adaptive 取代固定 0.22 / category-drop 0.08（CB-2 Exp3：無單一常數跨 query 分 gold/noise）。promote Testing/ `dynamic_cutoff` rank-based knee 思路；屬 §E.3 四輪治理脈絡，需 §3d regression matrix + live test-verify。
3. **PLAN-1b — CPD category-routing + 選擇性 expansion consolidation（全 Testing/ 先）**：CPD gold 喺 `sag_2025_11`/`g06`，唔喺 `SOURCE_SETS["curriculum"]` allowlist → probes 永遠救唔到（agent 證）。修 category→source 映射 + selective expansion vs §D.9 always-on `QUERY_EXPANSIONS` 一規一處 consolidation。連帶 sen（expansion-recovers）。
4. **🔴 masking-defect promote-blocker（Leonard flag+defer，待排 scope/§3）**：`searchCombined.ts` `.catch` 將**任何** Channel B 例外偽裝成「Channel B 未配置（環境變數缺失）」+ HTTP200 → Channel B 失敗對 monitoring/eval **完全隱形**，真 transient 與真 misconfig 無法區分。獨立產品 observability defect，碰 promote/監控前必處理。
5. **既有 deferred**：🔴 FAIL-A Circular 注入 regression（S111 dedup×budget，record-only 待設計決定）；🔴 §E.10 admin-login security（最嚴重未解）；P2 分類 148（中/小/幼/特+範疇）+ P3 LSG 誤標/SEN 覆蓋（39→148 deferred 須 §3 HIGH-risk）；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B `semanticRegression.ts:292` stale 1.3.1 / `wiki_index._meta.total_chunks=2874` 實 12,906）。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / Circular System 整合）

## Last Session Record
1. UTC date: 2026-05-18
2. Session ID: Claude_20260518_1600 (Session 116)
3. Completed:
   - ✅ **[Channel B 北極星]** Leonard 定 done-state：無論點問都有合理、有指引、**一定要有頁數**（CB-2 retrieval + CB-3 可追溯〔頁數不可 defer〕+ CB-1 質素）；入 memory project_direction。
   - ✅ **[PLAN-1 v2 §3 HIGH-risk，Leonard 批]** scope = probes + adaptive threshold；selective expansion 撞已驗證 §D.9 → 抽出 PLAN-1b（Leonard 裁）。
   - ✅ **[Stage 1 = 升 ivfflat.probes 1→8，FULL CLEAN PASS]** 機制修正鏈（全實證）：function-SET-clause→42501、stable+SET LOCAL→0A000、schema.sql `vector(1536)` 簽名套落 live→**PGRST203 overload live 事故（Channel B 全 0）**。診斷 A/B 定路→ROLLBACK drop vector 變體還原→INSPECT 攞真實 `match_wiki_chunks(query_embedding text,...)` 定義（schema.sql 自稱 exact-contract 實已 drift = 事故根因）→最終落真實 text 變體 plpgsql **volatile** + `set local ivfflat.probes=8`（Leonard Dashboard 套用、smoke OK）。clean-verify v2（dedicated /channel-b 繞 masking + pacing）全 12 OK、6/6 ANN flip 0→>0、0 回歸；§C 隔離重試 → HARNESS/LOAD artifact、probes=8 sound。
   - ✅ **[Agent-team 唯讀 ×3]** CPD root-cause（=source-allowlist/category-routing defect 非 probes→PLAN-1b）；獨立 audit 推翻我 6/7 overstatement（量度 artifact）；clean-verify v2 設計。
   - ✅ **[PERSIST]** Draft `backend/supabase/schema.sql` 改正真實 text 變體+probes+修 drift（signature/grants/post-run）；SESSION_LOG S116 + verbatim、SESSION_HANDOFF baseline/OP重生/本 record、CODEBASE_CONTEXT、PROJECT_MASTER_SPEC §C.4/§D/§E、DOC_SYNC；commit+push 指定檔；memory ×3（reference Supabase probes / feedback inspect-live-before-replace / project_direction 北極星）+ MEMORY.md。
4. Pending（待 Leonard）:
   - **Stage 2 adaptive threshold（PLAN-1 promote 未完成；同一 §3 HIGH-risk gate）** vs **PLAN-1b（CPD/expansion）** vs 先修 **🔴 masking-defect promote-blocker** — Leonard 排序。
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - Stage 2 / PLAN-1b / masking-defect（Leonard 揀）
   - 🔴 FAIL-A regression（record-only）/ §E.10 admin security（deferred）
   - P2 分類148 + P3 / Mobile UI P2 / HKEAA
6. Risks / blockers:
   - **PLAN-1 promote 未完成（Stage 2 未做）勿宣稱 released**；生產已 probes=8（Stage-1 FULL PASS）。
   - 🔴 schema.sql 曾 drift（vector vs 真實 text 簽名）→ PGRST203 live 事故；任何 Supabase RPC DDL 前必 INSPECT live `pg_get_functiondef`、勿信 schema.sql（memory+§E 固化）。生產 DDL 仍 Leonard Dashboard 親手。
   - 🔴 masking-defect（Channel B 失敗對 monitoring/eval 隱形）；🔴 §E.10；🔴 FAIL-A；§3c regression:semantic 既有 FAIL-A/B（schema.sql SQL-only 不影響）。
   - egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（S111 教訓，本 session 已遵）。
7. **Session CLOSED 2026-05-18（Leonard「收工」）** — §4 closeout 完成；Draft schema.sql + governance docs commit+push origin/main（HEAD = S116 closeout commit）；下次起手＝問 Leonard 排序 Stage 2 / PLAN-1b / masking-defect。

## Previous Session Record
1. UTC date: 2026-05-18
2. Session ID: Claude_20260518_1059 (Session 115)
3. Completed:
   - ✅ **[CB-0 Leonard gate PASSED]** 3 ruling 採納（Q1 #9 幼稚園收生=NORMAL 接受語料 drift / Q2 rolefact 確認排除 / Q3 下一階段=CB-2）。我做 12 條 B-gold 唯讀自我覆核（實測 cross-check cb_corpus_pool，唔信 gold_detail）→ 抓 2 discrepancy（#5 g24 url 寫錯實為 sag_c.pdf；#12 circ_edbc24017 寫 url=null 實為真 EDBC24017C.pdf）。Leonard spot-check #1/#5/#8/#9/#11 全對 + 裁 (b)#12 留正式 gold (c)#5 url 准修。
   - ✅ **[CHANGE 全 Testing/，Draft 零接觸]** `gold_set_channelB.json` _meta→AUTHORITATIVE+rulings、#5 g24 url×2→sag_c.pdf、#12 circ url→真 url、notes 更新；`grade_channelB.py` DRAFT→AUTHORITATIVE。重跑 grader → CB-0 升 AUTHORITATIVE。
   - ✅ **[CB-0 QC]** gold JSON OK；invariant 0 rolefact/0 null-url across 41 gold；**layer-1 gate 前後 byte-identical**（gold id 未變＝gate 驗證非改動）；CB-0 結論「瓶頸=RETRIEVAL」authoritative。
   - ✅ **[CB-2 執行完成（egress 復通後，Leonard「其他你繼續做」）]** §3 divergence 報 Leonard→裁示等網→egress 自測復通（onrender 200/OpenAI reachable）→READ→CHANGE→QC→PERSIST。§0b：schema.sql 權威 `lists=60`（解 50/60 矛盾＝docs 50 係 drift）、probes=1→~1.7%、chunk 帶 1536-emb、key SET（不入 log）。新檔（Testing/）cb2_build_emb_cache/embed_queries/experiment → cb2_emb.npy(12906×1536)/cb2_meta/cb2_qvecs/`CB2_report.md`。**結論：8 條 live-0 → 7 ANN-recoverable（升 ivfflat.probes）+1 expansion-recovers（sen 1893→3）+0 hard**；建議升 probes＋選擇性 expansion＋per-query adaptive threshold。QC 自揭並修自身 metric tautology bug；§3d 4 scenario 全 PASS；CB-2 重算 live recall === CB-0 authoritative（自洽）。
   - ✅ **[PERSIST]** SESSION_LOG S115 entry（CB-0+CB-2+verbatim handoff 全更新）；SESSION_HANDOFF Current Baseline/Open Priorities 重生（CB-2 done→等 Leonard 落地裁示）/本 record/Supabase Notes lists 50→60；PROJECT_MASTER_SPEC §C.4 lists 50→60 drift 修。
4. Pending（待 Leonard）:
   - **CB-2 建議落地 = Draft backend 改（searchChannelB / Supabase ivfflat.probes / wikiRepository）= promote = 獨立 §3 HIGH-risk gate**，須 Leonard 明示再出 PLAN，promote 前必 live test-verify（live Supabase 高 probes 未 introspect）。或 Leonard 改排 CB-1 / CB-3。
   - ✅ S115 兩個 commit（Leonard「push 係你做」，Claude 執行）：① `ec157db` = CB-0/CB-2/lists-drift/§4a；② 第二個 = MemPalace 移除 + HEAD-status 校正 + DOC_SYNC（CODEBASE_CONTEXT/PROJECT_MASTER_SPEC/SESSION_HANDOFF/SESSION_LOG + git rm mempalace_sync.py）。兩個皆 push origin/main。
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 等 Leonard 裁示 CB-2 落地路徑（promote PLAN §3 HIGH-risk）／改排 CB-1／CB-3
   - CB-1 語料衛生 / CB-3 合成可追溯（違 §A.2 #1）
   - P1 S1/S2 promote 仍暫停（本方向不涉）／🔴 FAIL-A 待 Leonard 排
6. Risks / blockers:
   - CB-0/CB-2 authoritative 但 offline-evidenced：probes 建議須 promote 前 **live Supabase test-verify**（高 probes 真實行為未 introspect）；recall-ceiling caveat（gold top-50 lexical pool）；synthesis 未量＝CB-3
   - egress 間歇（S115 早段 down→後段通）每次自行 verify，勿照抄
   - 其餘同下（FAIL-A / §E.10 / §3c gate 已紅 / S1S2 promote 暫停 / 路徑空格 / Testing 喺 Draft git 外 / 產品方向順序鎖定 / wiki_index _meta.total_chunks=2874 stale 實 12,906 doc-debt）
7. **Session CLOSED 2026-05-18（Leonard「收工」）** — §4 closeout 完成；S115 3 commit 全 push（HEAD `541e018`）；下次起手＝問 Leonard CB-2 落地路徑（promote §3 HIGH-risk / CB-1 / CB-3）。

## Previous Session Record
1. UTC date: 2026-05-18
2. Session ID: Claude_20260518_0720 (Session 114)
3. Completed:
   - ✅ **[方向轉 Channel B 效果]** Leonard 定新焦點：處理 Channel B 效果（唔單做一 channel），用 agent team 互補。§1 起手 verify：HEAD `71a3a3d`==baseline、stats {455,10736,120,39,7} 對得返、**egress 本 session DOWN（onrender /health timeout，間歇性再證）**。
   - ✅ **[4-agent 唯讀診斷]** 語料/檢索/合成/實證四切面共識：真 ingester=`dev/vault/build_wiki_index.py`（非文檔 ai_extract）；wiki_index 實 12,906 chunks（`_meta.total_chunks=2874` stale）；短/縮寫 query 嵌入失配 + IVFFlat probes=1（~1.7% 向量）+ 0.22→0.08 threshold；**合成 prompt 明令不引源 + merge A+B（A 零 url/page）→ 結構上不可追溯，違 §A.2 #1**；S1/S2「10/12」gold 100% Channel A — **Channel B 從未被 gold 評估**。
   - ✅ **[CB-0 評估基礎建成（全 Testing/，Draft 零接觸）]** `cb_corpus_index.py`（streaming 420MB 本地 wiki_index，零 egress）→`cb_corpus_pool.json`；GoldBuilder agent→`gold_set_channelB.json`（chunk-id-keyed，10/12 NORMAL、#6 LSG GAP、**#9 ABSTENTION→NORMAL g26 drift**、rolefact 排除）；`grade_channelB.py`→`CB0_channelB_report.md`（三層）。**結論候選（DRAFT）：Channel B 瓶頸=RETRIEVAL — 8/11 NORMAL query live recall=0/MRR=0，但正確 vault chunk（real EDB url）喺 corpus（10/12 覆蓋）**。
   - ✅ **[PERSIST]** SESSION_LOG S114 entry + DOC_SYNC scan；SESSION_HANDOFF Open Priorities 重生（item1=Channel B CB-0 DRAFT/gate）+ 本 record。Draft 僅 2 治理文檔改，**零 code/data/contract**，HEAD 不變（未 commit，待 Leonard）。
4. Pending（待 Leonard，gate）:
   - spot-check 4-5/12 B-gold（gate discipline）；裁示 (a) #9 ABSTENTION→NORMAL 收唔收 (b) rolefact-exclusion ruling (c) 接受「瓶頸=retrieval」後排 CB-2 檢索校準 vs CB-1 語料衛生先
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 等 Leonard CB-0 gate（spot-check + 3 rulings）
   - CB-2 檢索校準 / CB-1 語料衛生（待 gate 後排）
   - P1 S1/S2 promote 仍暫停（本方向不涉）／FAIL-A 待排
6. Risks / blockers:
   - **CB-0 DRAFT — 未過 Leonard spot-check gate 前數字 directional 非 authoritative**；gold 由 top-50 lexical pool 選（recall-ceiling caveat）；CB-0 只量 retrieval+corpus，synthesis 未量（dumps synthesize=false）
   - #9 幼稚園收生 status flip（語料 drift g26 ingested）+ rolefact-exclusion = 待 Leonard ruling；P2/P3 相關訊號
   - egress 本 session DOWN（onrender timeout）— 間歇性再證，每次自行 verify，勿假設恆通/恆封
   - 其餘 risk 同 Previous Record（FAIL-A / §E.10 / §3c gate 已紅 / S1S2 PoC 未 promote / 路徑空格 / Testing 喺 Draft git 外 / 產品方向順序鎖定）

## Previous Session Record
1. UTC date: 2026-05-17
2. Session ID: Claude_20260517_2035 (Session 113)
3. Completed:
   - ✅ **[收 S1 + 建 S2]** Leonard 收 S1（PoC，未 promote）；喺 Testing/ 建好 S2 = 支柱 1+3（lexicon / lexical_score / hybrid RRF + s2_operating_point）。`sen` 離線：S1 ceiling P=0.385@R1.0 → **S2 P=1.0@R1.0**（gold fused [1-5]）。
   - ✅ **[egress 實測 + 真實 breadth]** 實測 sandbox 竟接到 onrender + github SSH（與舊文檔假設相反，§G.2）→ 自己跑 12-query live `/api/search/combined` capture+grade（毋須交 Terminal）。baseline 每 query 269-504 條 P~0.01；S1 alone recall 崩 5 條；S2-op 初版 7/12。
   - ✅ **[3 gap 修好（Leonard「你的建議／b A」授權）]** #09 幼稚園收生：發現 dense out-of-domain confidently wrong（top 0.698 全場最高）→ 改 zero-literal-grounding abstention gate → 正確棄答（0 條）。#07 CPD（+持續進修/專業發展計劃）R 0.714→1.0。#10 防賄（+職能劃分/輪換原則，ICAC 職務分隔內控）R 5/6→6/6。`sen` 無回歸；lexicon per-query keyed 不影響他 query。**breadth 7/12 → 10/12 PASS**。餘 2 △（#03/08）= full-recall vs S1-fake-high-P tradeoff，非 defect。
   - ✅ **[(A) promote 嘗試 → 發現 §3c gate 已紅 → Leonard 裁示只記錄]** route (i) 完成（term_lexicon.py 泛化驗證 OK），Leonard「2」批一次過 promote。promote READ 階段先行 pre-change baseline：`check`✅`build`✅ 但 **`regression:semantic` overall=FAIL（PASS9/FAIL2）喺改前已紅**。triage 真因（唯讀，0 code 改）：FAIL-A=S111 dedup×600字budget 令 finance 角色注入退化（真 product regression，非 S1/S2）；FAIL-B=stale `1.3.1` 斷言。Leonard 裁示**兩個都唔做、只如實入治理；promote 暫停**。Draft backend 零接觸。
   - ✅ **[治理修正]** 補 S112 漏寫 DOC_SYNC row；grader provenance 改準確；**修正 SESSION_HANDOFF Regression Notes #3 由 false「PASS=12/FAIL=0 ✅」→ 實測 FAIL=2 + FAIL-A/B 真因**；Open Priorities 重生（promote 暫停 + FAIL-A 入優先序）。git commit+push S112 closeout + S113 治理文檔多次（Leonard「你去做／你的建議／b A／2／只記錄」授權；commit dbc10b8→…）。
4. Pending（待 Leonard）:
   - promote 暫停中 —— 只喺 Leonard 明示先恢復；FAIL-A（真 Circular 注入 regression）修法待 Leonard 排（涉設計決定）；P2/P3 排期？
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 等 Leonard：恢復 promote？／排 FAIL-A triage？
   - P2 分類 148 / P3 reconcile + SEN 覆蓋
   - 🔴 Q&A §E.10 / Mobile UI Phase 2 / HKEAA
6. Risks / blockers:
   - 🔴 **FAIL-A 真 product regression（未修，Leonard 裁示只記錄）**：S111 dedup×600字budget → subject_head/panel_chair 嘅 finance 注入自 2026-05-16 退化成只通用；見 Regression Notes #3。
   - 🔴 §E.10 公開站 client-side admin 閘門 + 密碼曾入 log（最嚴重未解）
   - §3c gate（`regression:semantic`）本身已紅（FAIL-A/B，非 S1/S2）→ 任何 release/merge claim 前必重新 baseline、勿信舊「✅」（§G.2 教訓再現：SESSION_HANDOFF 曾載 false PASS 斷言）
   - S1/S2 = Testing PoC 未 promote；breadth 10/12，餘 2 △=tradeoff 非 defect；勿過度宣稱「搜尋已全修好」（仍 PoC、12 短 query 抽樣）
   - egress 文檔假設過時（S113 實測 onrender+github 通）但可能 intermittent → 每次自行 verify
   - 已核實 role_facts「整筆撥款（LSG）」data error + 系統性欠 SEN/融合教育覆蓋（P3/P2 未 fix）
   - 路徑含空格雙引號；Testing/ 喺 Draft git 外；load-bearing 數字動手前 verify；改 code/data commit 必入 SESSION_LOG
   - 產品方向 P1→P2→P3 鎖定 + 39→148 deferred；未確認唔好跳契約收斂/Circular/scope/§F

## Previous Session Record
1. UTC date: 2026-05-17
2. Session ID: Claude_20260517_0930 (Session 112)
3. Completed:
   - ✅ **[產品方向 roadmap 定案]** Leonard 定 P1 搜尋相關性 → P2 分類 148 → P3 數字對齊；39→148 收斂 = deferred future（將來做、非 undecided）。已入 auto-memory + PROJECT_MASTER_SPEC §F.9/§B.1 措辭修正。
   - ✅ **[P1 新架構 PLAN 批准]** 5 支柱（hybrid lexical+dense+RRF／動態裁切／查詢理解 lexicon／統一 A·B·A+B path／頁碼溯源）取代 patch #5；分階段 S1→S4，全部隔離喺 `Testing/poc-retrieval/`，**Draft + 公開契約零接觸**（每步 verify git clean）。
   - ✅ **[S1 完成 PASS as scoped]** Agent-GoldBuilder 草擬 12 短查詢 gold → Leonard 抽驗 5 條 validated。真 `sen` 171 行生產數據 vs gold：cutoff 後 **171→6-8、雜訊尾乾淨砍掉**。誠實：pillar-2 necessary-not-sufficient（3 SENCO gold 同雜訊交織，100% recall precision 上限 0.385）→ S2 必需（Leonard SENCO 裁示 domain-confirm）。
   - ✅ **[Drift fix]** Current Baseline git HEAD `ae31084`→`dbc10b8`（verify 實際）。
4. Pending（待 Leonard，非技術）:
   - 收 S1？行 S2（hybrid+SEN/SENCO lexicon）？捕捉其餘 11 query 真實 backend 輸出（sandbox 出唔到 → curl 交 Terminal）？S1 是否 promote 入 Draft（獨立 HIGH-risk gate）？
   - P2/P3 排期；含已揭 data error「整筆撥款（LSG）」誤標 + SEN 家族覆蓋缺口
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - P1 S2（hybrid+lexicon）/ 廣度驗 11 query
   - P2 分類 148 / P3 reconcile + SEN 覆蓋
   - 🔴 Q&A §E.10 / Mobile UI Phase 2 / HKEAA
6. Risks / blockers:
   - 🔴 §E.10 公開站 client-side admin 閘門 + 密碼曾入 log（最嚴重未解，碰 admin/auth/公開推送前必讀）
   - S1 係 Testing PoC 未 promote；pillar-2 單獨唔夠（誠實：sen 頭部精度要 S2，勿過度宣稱）；promote = 獨立 HIGH-risk gate
   - 已核實 role_facts「整筆撥款（LSG）」data error + 知識庫系統性欠 SEN/融合教育覆蓋（P3/P2，未 fix）
   - sandbox 出唔到 OpenAI/Supabase/Render → 三通道 semantic 自己跑唔到；廣度驗 S2 須 Leonard Terminal curl
   - 路徑含空格雙引號；Testing/ 喺 Draft git 外；load-bearing 數字動手前 verify code/data/git；改 code/data commit 必入 SESSION_LOG
   - 產品方向 P1→P2→P3 順序鎖定 + 39→148 deferred；未得確認唔好跳契約收斂/Circular 接線/scope/§F

## Previous Session Record
1. UTC date: 2026-05-16
2. Session ID: Claude_20260516_1952 (Session 111)
3. Completed（三塊）:
   - ✅ **[truth-pass v2]** 揭發並消化 governance/state desync：8 個 un-logged commit `c78685f..ae31084`（dedup 792→455 `711f911` / Channel B Supabase kit / mobile fallback / app refactor，已 push）+ S110 從未 commit 文檔修正。治理讀set（PROJECT_MASTER_SPEC/CODEBASE_CONTEXT/HANDOFF_PACKAGE/SESSION_HANDOFF）重對齊 455/ae31084；§B.1 4 數字釐清框（148 app 內庫 / 39 公開 / 151 registry / 120 extracted）+ 更正「148 過時」錯說法；§E.2/§G.2/§F.9 教訓固化
   - ✅ **[Team A 對外文件編號對齊]** CHANGELOG（+v2.3.0 2026-05-16 dedup entry + 解 version 撞號 v2.3.0@05-03→v2.2.1）/ K1_API_SPEC（§3 v1.3.1→2.3.0、§6 v→2.2.0 **count 39 留**）/ README（148 in-app vs 39 公開釐清）；K1_KNOWLEDGE_INTERFACE_SPEC 已對齊。git diff 逐檔 verify 零 scope creep
   - ✅ **[Team B audit + #3 修]** read-only 確認 `INITIAL_REVIEW_STATE` 仍 1,001-keyed vs 455 嚴重錯位；修（範圍=只修資料對齊）：`dev/regen_review_state_s111.py`（先 backup）重生 **455 全 approved** 保持單行 inlined（E.1）+ comment @713/@1483 + `LOCAL_SNAPSHOT_KEY` v2→v3。零 json/data 改動
   - ✅ 過程自我修正：照 commit message 誤判 app.html 148 regression，verify `GUIDELINES_REGISTRY.length` 後更正（已固化 §G.2）
4. Pending（用戶 Terminal，含空格路徑雙引號）:
   - ✅ 已入庫：commit `019df6c` push 上 origin/main；MemPalace sync 完成（venv python）
   - ✅ #3 已驗證 PASS：Leonard browser admin-login 親驗登入後見 455（非 1,001）
   - 待 Leonard：拍板 guidelines 39→148 OPEN DECISION + 產品方向
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - guidelines 39→148 OPEN DECISION（須 §3 HIGH-risk PLAN）/ 產品方向待拍板
   - Mobile UI Phase 2 餘下 / 🔴 Q&A §E.10
   - HKEAA source family + doc-debt 清理
6. Risks / blockers:
   - 🔴 §E.10：公開站 client-side admin 閘門非安全邊界 + 密碼曾入 log（最嚴重未解風險，仍 open）
   - 🔴 治理根因：改 code/data 嘅 commit 必須同 pass 入 SESSION_LOG，否則交接讀set 失真（S111 desync 教訓）；load-bearing 數字（facts/git HEAD/min_score/連 commit message）動手前 verify actual code/data/git
   - guidelines 39 vs 148 = OPEN DECISION，未經 §3 HIGH-risk PLAN 唔好收斂 / 改 guidelines.json / app.html GUIDELINES_REGISTRY
   - #3 後回訪 admin localStorage 已 bump v3，舊本地未匯出編輯會棄（原已 keyed 壞 index 不可信）；**Leonard 已親驗 PASS（見 455）**
   - 產品方向未定 → 唔好假設沿用舊 scope
   - 其餘同下（路徑空格 / sandbox egress / Render cold start / bump_version / SSL / MemPalace / Supabase）

## Previous Session Record
1. UTC date: 2026-05-16
2. Session ID: Claude_20260516_1652 (Session 110)
3. Completed:
   - ✅ **[文檔 drift truth-pass]** 實測 verify 真實 repo state，修正 D1–D5：§B.1 148→39（+釐清框）/ CODEBASE_CONTEXT 1,001→792 ×2 / wikiRepository L39 改寫成 Supabase 架構（原描述已被取代）/ baseline #5 min_score 0.15→0.22
   - ✅ **[§E 補完]** PROJECT_MASTER_SPEC +E.10（🔴 公開站 client-side admin 閘門 + 密碼曾入 log，至今 open）/ +E.11（Channel A topic 污染）/ +E.12（EDB 改版打爛 26 URL）；強化 E.4/E.5/E.8 復發成本
   - ✅ **[Banners]** §F「產品方向審視中、非不可變」+ §G.2「連 SESSION_HANDOFF/CODEBASE_CONTEXT 都會 drift，verify code」
   - ✅ **[新增 dev/HANDOFF_PACKAGE.md]** self-contained 乾淨可信交接快照（verified-state 表 / 邊度亂 / 開放決策 / 接手第一步）；接入 Start Checklist 4b + DOC_SYNC registry（+1 row）
   - ✅ 未動任何 code / tech stack（純文檔準確性）
4. Pending（用戶 Terminal，新路徑）:
   - Git commit + push（含本 session 文檔修正 + HANDOFF_PACKAGE）
   - Leonard review HANDOFF_PACKAGE 內容是否需補 / 拍板產品方向
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 等 Leonard 拍板產品方向（未確認前唔好對 scope/§F 落手）
   - Mobile UI Phase 2 餘下 / Q&A admin-login security（§E.10）
   - HKEAA source family 補完
6. Risks / blockers:
   - 🔴 §E.10：公開站 client-side admin 閘門非安全邊界 + 密碼曾入 log（全專案最嚴重未解風險，仍 open）；碰 admin/auth/公開推送前必讀
   - 產品方向未定 → 唔好假設沿用舊 scope；§F 已標 current-state 非鎖死
   - 文檔曾 drift（D1–D5 已修）；load-bearing 常數動手前 verify actual code/data
   - 其餘同下（路徑空格 / sandbox egress / Render cold start / bump_version / SSL / MemPalace / Supabase）

## Previous Session Record
1. UTC date: 2026-05-16
2. Session ID: Claude_20260516_0841 (Session 109)
3. Completed:
   - ✅ **[PROJECT_MASTER_SPEC.md 建立]** 新建 `dev/PROJECT_MASTER_SPEC.md` 作長期權威規格 + 跨 agent 交接知識庫：§A 系統目標/scope/不變量 + §B 功能要求 + §C 已架構系統地圖 + §D 13 條高效已知方法 + §E 9 類必避失敗教訓（提煉自 archive Q1+Q2）+ §F 10 條鎖定決策 + §G 下一個 agent 起手指南
   - ✅ **[Governance wiring]** CODEBASE_CONTEXT directory map + AI Maintenance Log；DOC_SYNC_CHECKLIST 加 project-specific row；Mandatory Start Checklist 加第 4 項（讀 PROJECT_MASTER_SPEC）
   - ✅ **[專案目錄遷移]** 整個 repo 由 `~/Downloads/Claude-edb-knowledge` `mv` 遷至 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（同磁碟 rename，931MB 全量含 .git/node_modules/.venv）；先 commit 還原點 `4d54b2a`；驗證 git 歷史+remote+clean tree 完好
   - ✅ **[路徑 doc-sync]** AGENTS.md header+§13、SESSION_HANDOFF User Environment+Close Checklist、PROJECT_MASTER_SPEC §A.5、bump_version.py+dedup_check.py 提示 全改新路徑（含空格→雙引號）；功能性腳本用相對路徑不受影響
   - ✅ **[.claude/launch.json]** 偵測 dev server 並存配置（backend:8787 + frontend-static:8080）；用戶選擇暫不啟動
4. Pending from this session (not yet done):
   - 用戶 review PROJECT_MASTER_SPEC.md 內容是否需補充
   - （Git push 已完成：commit 4d54b2a + 88205dc 已上 origin/main）
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - Mobile UI Phase 2 餘下（index/q/t-purchase/#guidelines）
   - Q&A admin login backlog
   - HKEAA source family 補完
6. Risks / blockers:
   - ⚠️ Repo 路徑含空格 → 所有 cd / 腳本指令必須雙引號包覆絕對路徑；勿再用舊路徑 `~/Downloads/Claude-edb-knowledge`（已不存在）
   - MemPalace cfg 用相對路徑不受影響；`mine .` / sync 須在新路徑跑；shared palace 在 repo 外不受影響
   - Cowork sandbox egress allowlist 不含 edb.gov.hk / edb-knowledge.onrender.com / apps.apple.com → 線上驗證需用戶 Terminal / browser
   - Render free tier cold start (~30s) after 15min inactivity
   - index.html / q.html / t-purchase.html mobile reload 仲一片空白（Phase 2 未做）
   - Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings

## Previous Session Record
1. UTC date: 2026-05-05
2. Session ID: Claude_20260505_0001 (Session 108)
3. Completed:
   - ✅ **[Mobile UI Phase 2 — app.html ship]** mobile.js 加 buildAppShell：hero gradient + search form + result cards + bottom sheet + 接 backend `/api/search/combined`
   - ✅ **[Source helpers + states]** SOURCE_LABEL map 12 條 + sourceIcon 自動分類；empty/loading/error/429 全狀態提示；#guidelines fallback 暫露 React panel
4. Pending: 用戶 mobile reload 確認 search flow
5. Next priorities: Phase 2 餘下 / Q&A admin login backlog / HKEAA source family
6. Risks / blockers: 同上（sandbox egress / Render cold start / mobile content / SSL / MemPalace / Supabase）

## Previous Session Record
1. UTC date: 2026-05-03
2. Session ID: Claude_20260503_0004 (Session 107)
3. Completed:
   - ✅ **[UX revisions 三批]** index.html 8 點 + app.html 9 點 + #guidelines 修補（分類欄反白 EDB green / 學習階段 filter 全 category / steps grid 對齊）
   - ✅ **[Mobile UI Spec v1.1]** dev/MOBILE_UI_SPEC_v1.md 完成；user 6 答案 record；6 條 Tado URL reference library
   - ✅ **[Mobile UI Phase 1 ship]** /mobile.css 完整 design system（EDB green + Cloud Dancer + atmospheric + dark mode auto）+ /mobile.js（detection / role picker first-run / placeholder rotate / cross-page tab bar）+ 4 HTML head link
   - ✅ **[Q&A 5 條答覆]** 18450 fake count 刪 / 34 問題 audit backlog / 匯出 admin only 保留 / 8 角色 wrap include all_roles / Online security 短期建議 password gate
4. Pending from this session (not yet done):
   - Final git push 含 Mobile UI Phase 1 + UX revisions + spec doc
   - 用戶 mobile reload 確認 role picker / tab bar / dark mode
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - Phase 2 mobile content render（app.html 核心）
   - Q&A backlog（admin login 相關）
   - HKEAA source family
6. Risks / blockers:
   - Cowork sandbox egress allowlist 不含 edb.gov.hk / edb-knowledge.onrender.com / apps.apple.com → 線上驗證需用戶 Terminal / browser
   - Mobile UI Phase 2 未做 — Phase 1 ship 後 mobile reload 仲見唔到 main content
   - Render free tier cold start (~30s) after 15min inactivity
   - Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings

## Previous Session Record
1. UTC date: 2026-05-03
2. Session ID: Claude_20260503_0003 (Session 106)
3. Completed:
   - ✅ **[OP #1 + #2 一氣 ship]** 三層 _meta.stats block + description sync；README badge / footer / 全文 hardcoded counts 全 v2.3.0/792；CHANGELOG 加 v2.3.0 entry；app.html INITIAL_DATA + nav badge sync；index.html 加 dynamic fetch + data-stat span
   - ✅ **[Single source of truth]** knowledge.json _meta.stats 為前端 stats 唯一真源；index.html fetch + app.html stats prop 都從同一 block 拎
4. Pending from this session (not yet done):
   - Git commit + push（B + A 一氣 ship）
   - User reload GitHub Pages 確認首頁 + app.html 數據對齊
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 手機端 UI 設計
   - HKEAA source family
   - Sanity query 結果分析
6. Risks / blockers:
   - Cowork sandbox egress allowlist 不含 edb.gov.hk → URL inspect 同 xlsx 下載需 user browser
   - Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上 query 驗證需用戶 Terminal
   - Render free tier cold start (~30s) after 15min inactivity
   - Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
   - Shared MemPalace recovery workaround (`hnsw:num_threads=1`); keep backup at `/Users/leonard/mempalace/palace.pre-recovery.20260421_0838`
   - Supabase free tier: 500MB DB limit; wiki_chunks currently ~50MB with embeddings
   - index.html dynamic stats 用 fetch knowledge.json — file:// protocol 開 index.html 可能 CORS 失敗；fallback 用 hardcoded 數字（無 break）

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
  - 🔴 `searchCombined.ts` `.catch` masks ANY Channel B exception as fake "Channel B 未配置（環境變數缺失）" + HTTP 200 → B failures invisible to monitoring/eval (S116 promote-blocker, flag+defer). For diagnosis/grading use dedicated `/api/search/channel-b` (real errors surface).
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
