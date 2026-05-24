# Session Handoff

## Current Baseline
1. Version: **v2.3.0**；git `main`=`origin/main` HEAD = **S123 PERSIST commit（會喺本 commit 推進；下次起手自行 verify、S122 closeout HEAD = `0c58440`；session 進行中，Leonard 未「收工」）**。**S123：CB-3 Option C broader batch-2（10 marker-less PDF）page-carry 生產 live + 0 regression + agent-team 3 parallel pre-flight + Audit agent 揭 3 superseder swap**（va_sss_2015→values_edu_framework_2021_trial / ethics_relig_sss_2007_2019→ethics_relig_sss_2024 / music_sss_2015→music_sss_2024，避 stale-policy contamination 違北極星 traceability）。§3 HIGH-risk Gate 1 vault `--write` 10/10 PASS（markers==pages 110/150/140/113/133/89/99/114/55/116、total 1,119 pages；content sanity 100.7-102.4%；§5.a backup `dev/init_backup/20260524_204849_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 sources canonical normalization -16~-24%、1 source `eng_sss_guide_2021` 300→421 +40% = content RECOVERY 撞 legacy 300 cap，cap 係 chunker-bound 唔係 era-dependent）→ Gate 2 EXECUTE 10/10 OK（DELETE 1,698 / INSERT 1,529 / net -169 / Supabase 10,569→**10,400** 命中 Monitor agent floor prediction、per-source `del/ins/now` 全對齊）→ live smoke 9/10 batch-2 sources surface（**ethics_relig_sss_2024 0.687/0.686 batch 最高分** / ict / ma / bio / tour_hosp / values_edu / history / tl 全部 top-2 hits in top-5；eng_sss_guide_2021 retry via English query 0.625/0.624 confirm data live、原 Chinese query 撞 Supabase `57014` transient = PMS §C.4 known、非 regression；music_sss_2024 0/5 ranking 競爭 arts_kla_guide_2017+music_p1_s6_2024 同 KLA = data indexed 確認、non-regression 同 S122 tech_kla pattern）。**S122：CB-3 Option C broader batch-1（10 marker-less PDF）page-carry 生產 live + 0 regression** — Leonard 起手「resume broader Option C batch-1」明示授權 → Gate 1 vault `--write` 10/10 PASS（markers==pages 全對、content sanity 100.6-102.5% 無 quality regression、backup §5.a-compliant `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 sources canonical normalization -16~-26%、1 source `eng_lit_guide_2023` 300→633 +111% = content RECOVERY 撞 legacy 300 cap）→ Gate 2 EXECUTE 10/10 OK（DELETE 2,503 / INSERT 2,390 / net -113，Supabase wiki_chunks 10,682→**10,569** exactly match prediction，per-source `del/ins/now` 全對齊）→ live smoke 8/10 batch-1 sources 確認 surface with **PAGE NUMBERS**（地理科探究主題 → geog_jss p=106 0.667 + geog_sss p=66 0.612；化學實驗 → chem_sss top-3 p=145/80/40 0.65/0.62/0.61；英國文學選讀 → eng_lit top-3 p=8/9/81 0.48/0.46/0.46 **content +333 chunks recovery 北極星 live verified**；宗教倫理 → religious_edu p=18/67；公民及社會發展科 → ces_jss p=19；物理科 → phys_sss p=143。剩 tech_kla / ls_jss / chi_hist 本輪 query 無 surface = ranking/topic-routing 競爭非 regression、data 確認已 indexed）。**Whole-vault page-resolvable：13.2% (pre-B) → 23.7% (post-S119) → 32.2% (post-S120) → ~55.2% (post-S122)** = 5,830 / 10,569 chunks；52/113 vault sources marker-bearing（39 B + 3 C pilot + 10 batch-1）。**Remaining：51 marker-less PDFs**（batch-2~6、driver + repage_pdfs.py 完全 generalize-ready）+ 9 結構天花板（4 HTML + 5 xlsx）→ CB-3 final ceiling ≈ 88%。`§E.14` driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused（service_role bypass RLS、S121 已 verify）；seen_ids / per-source DELETE/replace pattern 維持、0 incident。**S121 commit `fd22e0a` diff 已 apply URL-encoding patch（commit msg 同 SESSION_LOG 講「pending 5min patch」係 S121 內部 drift；§G.2 verify-code-not-docs 教訓再驗）**。**Frontend test link 已提供：** https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search surface、Leonard browser-verify pending）。**S121 closed：Supabase RLS critical security incident response 完成生產 live + 0 regression** — Leonard 截停 broader Option C batch-1 中段（safe stop：vault 0 mutate / Supabase 0 mutate）+ 出示 Dashboard 警報「`rls_disabled_in_public` on wiki_chunks」(2026-05-17 raised)。**INSPECT 揭發遠超警報 surface：** `wiki_chunks` 對 `anon` GRANTS 實有 SELECT+INSERT+UPDATE+DELETE+TRUNCATE+REFERENCES+TRIGGER 全套寫權限（PMS §C.4 doc drift：寫「anon 需 GRANT SELECT」實 live 全 write 都通；任何 anon 用戶可清空/投毒/篡改 wiki_chunks）。§3 HIGH-risk PLAN→ Leonard Dashboard 親手 paste：`ALTER TABLE ENABLE RLS` + `CREATE POLICY wiki_chunks_anon_read FOR SELECT TO anon,authenticated USING(true)` + `REVOKE INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER FROM anon,authenticated`；`service_role` GRANTS 不變、broader Option C upload 不受影響（service_role bypass RLS by default）。Post-APPLY re-INSPECT 確認 live state（RLS ON / 1 policy / anon=SELECT only / service_role full / `match_wiki_chunks` 屬性 unchanged）；**Channel B 5/6 live smoke PASS 0 regression**：採購 g01 0.66/0.62 + role_facts_finance 0.638（byte-identical pre-baseline）/ 幼稚園收生 g26 p=2/4 0.696（S120 pilot intact）/ 學校行政手冊 sag p=1 / 教師專業操守 sag p=205 + g05 p=30 / 化學 sci_jss+chem_sss；「化學評估」0 hits 非 regression（query 太 narrow + threshold 0.22）。Cleanup：DROP temp inspect RPC、schema clean。Dashboard 警報 async clear（下次開 Dashboard 順手 confirm）。**新 PMS §D codify**：「INSPECT live Supabase catalog via temp SECURITY DEFINER RPC」3-step ritual（Claude 無 catalog REST path）。**broader Option C batch-1 paused 等 resume**（tasks #3-#7 pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT 已 +10 entries benign prep；2 URL-encoding fail = geog_sss_2007_2022 / ces_jss_2024 path 含空格，resume 前 5min patch）。**S120 closed：CB-3 Option C pilot 完成生產 live** — sag_2025_11/g06/g26 page-carry、Supabase 10,606→10,682；whole-vault page-resolvable 23.7%→**32.2%**；INVARIANT 109/109 PASS。**S119 closed：搜尋介面 Channel-B-only Phase 1 + Option B 全完成生產 live + Leonard browser-verify PASS**。**S118 closed：Stage-2 adaptive combo non-viable、PLAN-1b 4 dedicated route promote** — 詳見 Previous Session Records。**S117 closed：masking-defect FIXED**（`channel_b_status` discriminator）。**S116 closed：`backend/supabase/schema.sql` 改 text 變體 + plpgsql volatile + probes=8（生產 live，Leonard Dashboard 套用）**。⚠️ probes=8 *live* 本 session 經 RPC INSPECT 再 confirm（`language plpgsql VOLATILE` + `set local ivfflat.probes=8` + `SECURITY INVOKER` + owner=postgres）；Supabase free-tier probes=8 偶發 `57014` statement-timeout 已知 transient（retry 即恢復）。Q4（Channel A→`knowledge.json`→Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。local `wiki_index.json` vs Supabase 對 42 源 diverge（reconcile 低優先 backlog）。sag_2025_11 PDF EDB 已從 2025-11→2026-05；source_id 仍 `sag_2025_11`（freshness metadata backlog、非 blocker）。
2. Frontend: `index.html` K1 landing page (hero + features + CTA); `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **455 Channel A facts** (三層同步 ✅ byte-identical；2026-05-16 dedup 由 792 → 455，移除 275 條跨角色完全重複 + 合併 36 組相近事實，commit `711f911`，reversible log `dev/DEDUP_LOG_2026-05-16.md`；早前 Session 102 已 1,001 → 792), **0 candidates in queue**, **Supabase 10,400 chunks**（S123 post-batch-2，pre 10,569；net -169 來自 10 batch-2 sources：9 canonical normalization -16~-24% + 1 eng_sss_guide_2021 content recovery +40%；DELETE 1,698 INSERT 1,529）。Vault: 120 sources 提取完成（local extract 文件 113，3 pilot + 10 batch-1 + 10 batch-2 已整合至單 repaged 檔；39 marker via Option B + 3 marker via Option C pilot + 10 marker via Option C batch-1 + 10 marker via Option C batch-2 = **62 sources Supabase page-carried**；剩 41 marker-less PDFs + 9 結構天花板）。**指引數字 4 層（148 app 內庫 / 39 公開 guidelines.json / 151 source_registry / 120 vault-extracted）見 PROJECT_MASTER_SPEC §B.1 釐清框 — 39 是否擴到 148 = OPEN DECISION，未收斂**。
4. Backend: Node.js TypeScript backend all search APIs complete; **Channel A + B + A+B online at `https://edb-knowledge.onrender.com`**; rate limiting 10 req/min/IP (sliding window, in-memory).
5. Channel A: 改用 backend semantic search + LLM synthesis（所有三個 channel 均有整理答案）；min_score A=0.1, B/AB=0.22（2026-05-16 Session 110 對齊實際 code default，原寫 0.15 已過時）；case-insensitive keyword fallback 已移除。
6. Channel B topic filtering（Session 94 完成）：keyword → category → source allowlist → query expansion。採購/財務 → g01+g02+coa_imc（排 SAG）；HR/假期 → g04+g05+sag；課程 → 課程指引。g04 仍為 knowledge-based extract（非 PDF）。**S118 +4 dedicated selective route（first-match，置 finance 前）**：cpd→[sag_2025_11,g06,circ_edbc24017,role_facts_*]、kg_admission→[g26,g25,role_facts_general]、conduct→[g05,sag_2025_11,role_facts_*]、steam→plain+expansion；SAG 喺 cpd/conduct 由 per-source quota(cap=3) 約束、不破 §E.3。
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
> 產品方向：**搜尋介面 Channel-B-only**（S119 Leonard live-test 後定，A/AB user-facing 全移除、檔案 dormant；Q4 對外契約收斂 deferred 獨立 track）。北極星＝合理＋指引＋**頁數**（CB-3 不可 defer）。順序未得 Leonard 確認唔好跳；Stage-2 adaptive combo closed-as-non-viable 勿復活。Supabase RLS hardening 完成（S121），broader Option C **driver-generalize-ready 2 輪 verified**（S122 batch-1 + S123 batch-2 = 20 sources 全 PASS、driver 一行唔改）。
1. **broader Option C batch-3 ~ batch-6**（41 marker-less PDFs，等 Leonard 排批次步伐）：pipeline 已 generalize-ready 2 輪 verified；driver + `repage_pdfs.py` 一行唔改，extend `PILOT_LEGACY`/`PILOT_OUT` dict 即可。每批仍 §3 HIGH-risk Leonard 明示 go（Gate 1 vault `--write` → Gate 2 Supabase `--execute --skip-local` → QC + smoke）。**S123 教訓：每批前必跑 audit sub-agent check superseder chain**（避 stale-policy contamination 違北極星 traceability，§A.2 #1）。結構天花板剩 9 源（4 HTML + 5 xlsx），CB-3 全覆蓋上限 ≈ 88%。
2. **batch ranking polish backlog（低優先，非 regression）**：S122 batch-1 → tech_kla_guide_2017 / ls_jss_2010 / chi_hist_sss_2007_2015；S123 batch-2 → music_sss_2024（vs arts_kla_guide_2017 / music_p1_s6_2024 同 KLA 重疊）。共 4 sources 本輪 live smoke 無 surface = ranking/topic-routing 競爭（data 已 indexed），可加 dedicated route 或 SOURCE_ALIASES 改善；Leonard browser-verify 之後 calibrate。
3. **CB-3 收尾 backlog（低優先，非生產影響）**：(a) local `wiki_index.json` ↔ Supabase reconcile（62 源 diverge，S123 後 scope 由 52 擴）；(b) build_wiki_index hash-dedup vs live 語料不齊（latent corpus-consistency）；(c) sag_2025_11 freshness metadata（2025-11→2026-05；對外 contract 不變、純 internal naming）；(d) g06 vs pri_curr_guide_2024 / music_sss_2024 vs arts_kla_guide_2017 near-duplicate ranking polish（SOURCE_ALIASES dedup）。
4. **🔴 既有 deferred**：§E.10 admin-login client-side gate（RLS family 已 S121 closed、admin-login 仍 OPEN 獨立保留）；Supabase free-tier probes=8 `57014` transient（生產可用性、retry 即恢復；probes=8 live 已 S121 INSPECT 確認；S123 撞中 1 次 `校本評核` query、retry/換 query 恢復）；FAIL-A Circular 注入 regression（record-only）；P2 分類 148 + P3（39→148 deferred 須 §3 HIGH-risk）；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B `semanticRegression.ts:292` stale 1.3.1 / `wiki_index._meta.total_chunks` stale）。
5. **Q4 對外契約收斂（deferred 獨立 track）**：Channel A `role_facts.json`→`knowledge.json`→下游 Circular System；3 選項（叫下游改／Channel B 變供料／凍結停供）待 B-only+CB-3 成熟、Leonard 排；未明示勿掂契約/下游。

> ✅ **S123 完成**：CB-3 Option C broader batch-2（10 sources）page-carry 生產 live + 0 regression + agent-team 3 parallel pre-flight + Audit 揭 3 superseder swap；Supabase 10,569→10,400；whole-vault page-resolvable 55.2%→~64.4%；62/113 sources marker-bearing；Gate 1+2 §3 HIGH-risk normal flow、driver 第 2 輪 generalize verified。
> ✅ **S122 完成**：CB-3 Option C broader batch-1（10 sources）page-carry 生產 live + 0 regression；Supabase 10,682→10,569；whole-vault page-resolvable 32.2%→~55.2%；52/113 sources marker-bearing；Gate 1+2 §3 HIGH-risk normal flow、driver 一行唔改 generalize verified。
> ✅ **S121 完成**：Supabase RLS critical security incident response — `wiki_chunks` ENABLE RLS + 1 anon-read policy + REVOKE 6 write privilege × 2 role；0 regression（5/6 live smoke PASS）；§C.4 doc-drift 已修；§E.10 RLS family CLOSED（admin-login 仍 OPEN）。
> ✅ **S120 完成**：CB-3 Option C **pilot 3 sources page-carry 生產 live + 北極星端到端 verified**。
> ✅ **S119 完成**：Channel-B-only 搜尋 surface Phase 1（5 前端 surface 移除 A/AB；契約零接觸；browser-verify PASS）+ CB-3 Option B 全做完生產 live（39 marker 源 page-carry）。
> ✅ **S118 完成**：Stage 2 adaptive combo 雙獨立驗證非可行、**放棄（勿復活）**；pivot promote PLAN-1b 4 route（fixed cutoff）。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / Circular System 整合）

## Last Session Record
1. UTC date: 2026-05-24
2. Session ID: Claude_20260524_2048 (Session 123)
3. Completed:
   - ✅ **[起手序 + 自測 verify PASS]** §1 read set 完整跑（AGENTS → HANDOFF → SESSION_LOG → CODEBASE_CONTEXT → PROJECT_MASTER_SPEC → HANDOFF_PACKAGE）+ HEAD `0c58440` 同步 origin/main（S122 closeout）+ knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` v2.3.0 對齊 baseline + egress 實測 `/health` 200 (12.4s 冷啟 typical)。
   - ✅ **[Agent team 3 parallel pre-flight，Leonard「你安排 agent team 去分工，加快完成」指示]** 3 sub-agents 並行：(a) **Feasibility** URL probe + PDF parse 10/10 GO（total ~1,201 pages、無 4xx/5xx/0-page）；(b) **Audit** candidate cross-check 揭 3 superseder chain risk（music_sss_2015/va_sss_2015/ethics_relig_sss_2007_2019 全被新版 supersede + page-trace 舊版違北極星）；(c) **Monitor** chunk delta predict（base 10,569 → floor 10,400 / median 10,620 / ceiling 11,100；5 sources HIGH cap-hit risk）。主 agent cross-check `va_p1_s6_2024` 已 marker-bearing（53 markers）→ va_sss_2015 superseder coverage 已有 drop；music_sss_2024 / ethics_relig_sss_2024 / values_edu_framework_2021_trial vault YES + marker=0 + HEAD 200 verified → final 3 swap。
   - ✅ **[§3 HIGH-risk Gate 0 PLAN→Leonard「做」+「/goal go」]** Revised final 10 sources（3 swap、cross-KLA spread 更廣）：eng_sss_guide_2021 / ict_sss_2007_2015 / ma_sss_cag_2017 / bio_sss_2007_2015 / tour_hosp_sss_2007_2015 / values_edu_framework_2021_trial / ethics_relig_sss_2024 / history_sss_2007_2015 / music_sss_2024 / tl_sss_2007_2015。
   - ✅ **[Gate 1 vault `--write` 10/10 PASS]** markers==pages 全對（110/150/140/113/133/89/99/114/55/116、total 1,119 pages）；content sanity 100.7-102.4%；§5.a backup `dev/init_backup/20260524_204849_UTC/cb3c_pilot_legacy/` 10 entries；git scope = 21 entries（1 M + 10 D + 10 ??）batch-2 only。
   - ✅ **[Gate 2 dry-run 無 anomaly]** 9 sources -16~-24% canonical normalization；**eng_sss_guide_2021 300→421 (+40%) = content recovery** 撞 legacy 300 cap（同 S122 eng_lit_guide_2023 +111% pattern；Monitor agent 預測「post-2021 era LOW risk」落空 = cap 係 chunker-bound 唔係 era-dependent，§G.2 verify-don't-predict 教訓）。Total INSERT 1,529 / DELETE 1,698 / net -169 預估 Supabase 10,400。
   - ✅ **[Gate 2 EXECUTE 10/10 OK + 6 QC gates PASS]** Phase 1b embed all 1,529 first → wiki_index.json auto-backup `dev/init_backup/20260524_205212_UTC/` → per-source `del/ins/now` 10/10 全對齊 → Phase 3 SKIPPED `--skip-local`。Supabase 10,569→**10,400** 命中 Monitor floor prediction；backend /health ✅ cache_a warm 455 facts；INVARIANT non-batch-2 sources 零接觸。
   - ✅ **[Live smoke 9/10 batch-2 sources surface 北極星端到端 verified]** ethics_relig_sss_2024 **0.687/0.686 batch 最高分**（新版 SSS scope vs religious_edu_jss_2024 JSS scope 完全分流、無 dup-risk regression）+ ict/ma/bio/tour_hosp/values_edu/history/tl 全部 top-2 hits + eng_sss_guide_2021 retry via English query 0.625/0.624 confirm data live（原 Chinese query 撞 Supabase `57014` transient = PMS §C.4 known、非 batch-2 regression）。music_sss_2024 0/5 ranking 競爭 arts_kla_guide_2017+music_p1_s6_2024 同 KLA = data indexed 確認 69 chunks `now=69`、non-regression（同 S122 tech_kla pattern）。
   - ✅ **[PERSIST]** SESSION_LOG S123 entry + DOC_SYNC matrix、SESSION_HANDOFF baseline #1/#3 + Open Priorities regen + 本 Last Session Record + S122 demote、HANDOFF_PACKAGE §2 chunks 10,569→10,400、PROJECT_MASTER_SPEC §D batch-2 verified note、CODEBASE_CONTEXT External Services rows 10,400 + AI Maintenance Log +S123；commit+push 指定檔（pending）。
4. Pending（等 Leonard）：
   - **broader Option C batch-3 ~ batch-6**：41 marker-less PDFs，等 Leonard 排批次步伐（建議：10/批 × 4-5 批 + 每批 §3 HIGH-risk Leonard 明示 go + S123 教訓：必跑 audit agent check superseder chain）。
   - Frontend test link：https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search、無需 deploy、Supabase live 即時生效；Leonard browser-verify pending）。
   - 細項 backlog 同 既有 deferred → 詳見 Open Priorities。
5. Next priorities (max 3)：
   - 等 Leonard：broader Option C batch-3 排步伐？／轉做其他 OP？
   - 🔴 §E.10 admin-login client-side gate（RLS family 已 close，admin-login 獨立 OPEN）
   - S122/S123 batch ranking polish backlog（tech_kla / ls_jss / chi_hist / music_sss_2024 topic-routing 改善）/ 細項 backlog
6. Risks / blockers:
   - **Agent team superseder lesson codify（§8b monitoring）**：主 agent size-desc heuristic 漏睇 supersede 鏈（music/va/ethics_relig 2015-2019 全被 2024 supersede）。Audit sub-agent 揾出救返、避 stale-policy contamination 違北極星 traceability。**Recurrence-prone：每個 broader Option C batch pre-flight 必跑 audit agent check supersede chain（從 source_registry 嘅 `supersedes` 欄位 + URL pattern + title comparison）。** §8b 評估 = monitoring（單次未到 promote-to-rule threshold；recurrence-prone）。
   - **§G.2 verify-don't-predict 再驗**：Monitor agent 預測 eng_sss_guide_2021 「post-2021 era LOW cap-hit risk」、實 +40% recovery（cap 係 chunker-bound、唔係 era-dependent）。Prediction range 範圍合理但個別假設不準；Gate 2 dry-run 仍係 empirical ground truth。
   - **driver `cb3_b2_pagecarry_migrate.py` 一行唔改 第 2 輪印證**：S121 RLS hardening 後 service_role bypass RLS 持續 confirm + seen_ids dedup + per-source DELETE/replace + `--skip-local` 紀律 → 20/20 sources（S122 batch-1 + S123 batch-2）全 PASS + 0 incident。**Pipeline production-ready confirmed**。
   - local `wiki_index.json` vs Supabase 62 源 diverge（pre-S123 52 → post-S123 62；Supabase query-authoritative；reconcile 低優先 backlog）。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復、本 session 撞 1 次）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. **Session 進行中（非 closeout，Leonard 未表示「收工」）**：S123 PERSIST 完成，commit+push 跟住推；下次 Leonard prompt 起再決定排 batch-3 / 轉 OP / 收工。

## Previous Session Record
1. UTC date: 2026-05-24
2. Session ID: Claude_20260524_1717 (Session 122)
3. Completed:
   - ✅ **[起手序 + 自測 verify PASS]** §1 read set 完整跑（AGENTS → HANDOFF → SESSION_LOG → CODEBASE_CONTEXT → PROJECT_MASTER_SPEC → HANDOFF_PACKAGE）+ HEAD `591ced6` 同步 origin/main + knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` v2.3.0 對齊 baseline + egress 實測 `/health` 200 (12.7s 冷啟 typical)。
   - ✅ **[Leonard 明示 resume broader Option C batch-1 + 發現 S121 內部 doc-drift]** Leonard 起手揀 "Resume broader Option C batch-1"；按 handoff 先做 5min URL-encoding patch verify → READ `dev/vault/repage_pdfs.py` 揭發 S121 commit `fd22e0a` diff **已 apply** URL-encoding fix（`urlsplit` + `quote(sp.path, safe="/%")` + `urlunsplit`），但 commit msg 同 SESSION_LOG 仲講「pending 5min patch」= S121 內部 doc-drift（patch 已落 code、文字描述未跟上）。Re-dry-run 2 previously-failing sources 確認 2/2 PASS（geog_sss_2007_2022 142/142 + ces_jss_2024 126/126）。§G.2 verify-code-not-docs 教訓再驗。
   - ✅ **[§3 HIGH-risk Gate 1 PLAN→Leonard "push"→EXECUTE 10/10 PASS]** `dev/vault/repage_pdfs.py --only <10 sids> --write`：10 sources 全 written（tech_kla 237p / eng_lit 153p / ls_jss 183p / religious 159p / geog_sss 142p / ces 126p / phys 150p / chi_hist 169p / chem 159p / geog_jss 144p；markers==pages 全對）。**QC §3d 6 scenario PASS**：(1) 10/10 written (2) backup `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/` 10 entries §5.a-compliant gitignored (3) content sanity new/legacy 100.6-102.5% 無 quality regression (4) marker invariant 全對 (5) EDB drift 0 fails (6) git status 只 10 D + 10 ?? batch-1 sids、其他 vault sources 零接觸。
   - ✅ **[§3 HIGH-risk Gate 2 dry-run 無 anomaly]** 9 sources -16~-26% canonical chunker normalization（同 S120 g06/g26 pattern），1 source **eng_lit_guide_2023 300→633 +111% = content RECOVERY**（legacy 撞 300 cap、新 chunker 完整覆蓋，同 S120 sag +200 模式）。Total INSERT 2,390 / DELETE 2,503 / net -113 / 預估 cost ~$0.024 OpenAI embedding。
   - ✅ **[§3 HIGH-risk Gate 2 EXECUTE 10/10 OK + 4 QC gates PASS]** Leonard "完成後俾link我" full-flow auth → Phase 1b embed all 2,390 chunks first → wiki_index.json auto-backup `dev/init_backup/20260524_171708_UTC/` → per-source DELETE→upload→count verify 10/10 `del/ins/now` 全對齊 → Phase 3 SKIPPED `--skip-local`（§E.14 紀律）。**QC**：Supabase total = **10,569** exactly match prediction（10,682 - 2503 + 2390）；backend /health ✅ cache_a warm 455 facts；marker invariant via driver internal verify。
   - ✅ **[Live smoke 8/10 batch-1 sources 北極星端到端 verified with PAGE NUMBERS]** ✅地理科探究主題 → geog_jss p=106 0.667 + geog_sss p=66 0.612 ✅化學實驗 → chem_sss top-3 p=145/80/40 0.65/0.62/0.61 ✅英國文學選讀 → eng_lit top-3 p=8/9/81 0.48/0.46/0.46（+333 chunks recovery live verified）✅宗教倫理 → religious_edu p=18/67 0.55/0.54 ✅公民及社會發展科 → ces_jss p=19 0.558 ✅物理科 → phys_sss p=143 0.432。剩 tech_kla / ls_jss / chi_hist 本輪 query 無 surface = ranking/topic-routing 競爭（非 regression、data 已 indexed、Leonard browser-verify 後可 calibrate）。
   - ✅ **[PERSIST]** SESSION_LOG S122 entry + DOC_SYNC matrix、SESSION_HANDOFF baseline #1/#3 + Open Priorities regen + 本 Last Session Record + S121 demote、HANDOFF_PACKAGE §2 chunks 10,682→10,569、PROJECT_MASTER_SPEC §D.16 broader batch-1 verified note + §E.10 row count fix、CODEBASE_CONTEXT External Services line 132 rows 10,569 + AI Maintenance Log +S122；commit+push 指定檔（pending）。
   - ✅ **[Frontend test link 已提供 Leonard]** https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search、無需 deploy、Supabase live 即時生效；Leonard browser-verify pending、Leonard 「你繼續」=授權 PERSIST）。
4. Pending（等 Leonard）：
   - **broader Option C batch-2 ~ batch-6**：51 marker-less PDFs，等 Leonard 排批次步伐（建議：10/批 × 5-6 批 + 每批 §3 HIGH-risk Leonard 明示 go）。
   - **Leonard browser-verify** Frontend test link（非阻塞 PERSIST）。
   - 細項 backlog 同 既有 deferred → 詳見 Open Priorities。
5. Next priorities (max 3)：
   - 等 Leonard：broader Option C batch-2 排步伐？／轉做其他 OP？
   - 🔴 §E.10 admin-login client-side gate（RLS family 已 close，admin-login 獨立 OPEN）
   - S122 batch-1 ranking polish backlog（tech_kla/ls_jss/chi_hist topic-routing 改善）/ 細項 backlog（freshness metadata / SOURCE_ALIASES polish）
6. Risks / blockers:
   - **本 session §G.2 verify-code-not-docs 再驗**：S121 commit message 同 SESSION_LOG 講 pending 5min URL-encoding patch、實際 diff 已 apply（commit-msg-vs-diff drift）；§8b 評估 = monitoring（單次未到 promote-to-rule threshold；recurrence-prone = need to be aware）。
   - **driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reuse 印證**：S121 RLS hardening 後 service_role bypass RLS 確認 + seen_ids / per-source DELETE/replace pattern + `--skip-local` 紀律 → 10/10 OK + 0 incident 復發。**S122 batch-1 = pilot driver generalize 第一輪實證**：可以放心 batch-2~6 沿用。
   - local `wiki_index.json` vs Supabase 52 源 diverge（pre-S122 42 → post-S122 52；Supabase query-authoritative；reconcile 低優先 backlog）。
   - batch-1 內 3 sources（tech_kla / ls_jss / chi_hist）本輪 query 無 surface = ranking 競爭非 regression（data 已 indexed）；Leonard browser-verify + calibrate 後再決定要唔要 dedicated route。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復、非 regression）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-24（Leonard「收工」）** — §4 closeout 完成；S122 broader Option C batch-1（10 sources）page-carry 生產 live + 0 regression + Leonard 5 截圖 browser-verify PASS（地理 / 化學 / 文學 / 宗教 / 公民及社會發展科）+ disclaimer copy 改寫（去 admin/finance framing、align Channel-B-only 現況）；2 commits HEAD `2c986e1` 同步 origin/main（`3b4087d` S122 主體 + `2c986e1` follow-up copy 改寫）；§4a trigger=False（342 行、5 entries、oldest 2026-05-19）；後置 closeout commit 跟住推。下次起手＝問 Leonard 排 broader Option C batch-2（10 sources、剩 51 marker-less PDFs / 共 5-6 批）抑或轉做其他 OP（§E.10 admin-login / S122 ranking polish backlog / freshness metadata 等）。

## Previous Session Record
1. UTC date: 2026-05-20
2. Session ID: Claude_20260520_1720 (Session 121)
3. Completed:
   - ✅ **[Supabase RLS critical incident response 生產 live]** Leonard 截停 broader Option C batch-1 step 4（safe stop point：vault 0 mutate / Supabase 0 mutate）+ 出示 Dashboard 警報「`rls_disabled_in_public` on wiki_chunks」(2026-05-17 raised)。Leonard 揀「RLS 先、Option C 暫停（推薦）」。
   - ✅ **[INSPECT live state via temp SECURITY DEFINER RPC workaround]** Claude service-role REST 對 `pg_catalog` / `information_schema` HTTP 406（schema 唔 expose）+ 冇 connection string + 冇 Management API token → 寫 `__rls_inspect_temp()` plpgsql SECURITY DEFINER function、Leonard paste APPLY 落 Dashboard 一次、Claude service-role REST call RPC 攞 JSON parse。**揭發遠超警報 surface**：anon GRANTS 實有 SELECT+INSERT+UPDATE+DELETE+TRUNCATE+REFERENCES+TRIGGER 全套；authenticated 同；service_role 全；`match_wiki_chunks` 確認 S116 修正 live（plpgsql VOLATILE + probes=8 + INVOKER + owner=postgres）。**Risk re-rated：** 任何 anon 用戶可清空/投毒/篡改 wiki_chunks（非 read-only-disclosure）。
   - ✅ **[§3 HIGH-risk PLAN promoted、Leonard Dashboard 親手 APPLY]** ENABLE RLS + CREATE POLICY `wiki_chunks_anon_read` FOR SELECT TO anon,authenticated USING(true)（defense-in-depth）+ REVOKE 6 write privilege × 2 role（service_role 不變、broader Option C upload 不受影響、bypass RLS）+ Phase 4 self-verify jsonb 一條 row。Result pane 出 JSON、無 error。
   - ✅ **[Post-APPLY re-INSPECT 0 regression]** RLS ON ✅、Policy `wiki_chunks_anon_read` SELECT anon+authenticated USING(true) ✅、anon GRANTS = ["SELECT"] only ✅、authenticated GRANTS = ["SELECT"] only ✅、service_role GRANTS full unchanged ✅、`match_wiki_chunks` 屬性 unchanged ✅。
   - ✅ **[Channel B 5/6 live smoke PASS 0 regression]** 採購程序 → g01 p=5/1 0.66/0.62 + role_facts_finance 0.638（byte-identical pre-baseline）；幼稚園收生 → g26 p=2/4 0.696（S120 pilot intact）；學校行政手冊 → g24/sag p=1/role_facts 0.60-0.66（pilot intact）；教師專業操守 → sag p=205/g05 p=30/sag p=73 0.65-0.72（Option B/C marker 全保留）；化學 → sci_jss_framework / chem_sss 0.55-0.58；「化學評估」0 hits 非 regression（query 太 narrow + threshold 0.22、其他 5/6 通+ score 同 pre-baseline 一致）。
   - ✅ **[Cleanup]** Leonard paste DROP `__rls_inspect_temp` + final verify block 落 Dashboard，result 確認 `{wiki_chunks_rls:true, policy_count:1, anon_grants:["SELECT"], inspect_fn_dropped:true}`。Temp SECURITY DEFINER function 清走、schema clean。Dashboard 警報 async clear（下次開 Dashboard 順手 confirm，非阻塞 PERSIST）。
   - ✅ **[PERSIST]** SESSION_LOG S121 + verbatim、SESSION_HANDOFF baseline + Open Priorities regen + 本 record（demote S120 為 Previous）+ Risks update、PROJECT_MASTER_SPEC §C.4 doc-drift fix + §E.10 partial resolution + §D codify INSPECT workaround + §E.13 延伸（INVOKER RPC + RLS interaction）、CODEBASE_CONTEXT External Services Supabase + AI Maintenance Log +S121、HANDOFF_PACKAGE §2 wiki_chunks state + §3 risks；DOC_SYNC matrix scan；commit+push 指定檔。
4. Pending（broader Option C resume 等 Leonard）:
   - **broader Option C batch-1**：tasks #3-#7 pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT +10 entries 已落（benign prep）；**2 URL-encoding fail**（geog_sss_2007_2022 / ces_jss_2024 path 含空格）resume 前 `fetch_pdf` 加 `urllib.parse.quote` 5min patch。
   - **broader Option C batch-2 ~ batch-6**：51 marker-less PDFs，batch-1 完成 + verified 後 Leonard 排步伐。
   - 細項 backlog 同 既有 deferred 同 S120 → 詳見 Open Priorities。
5. Next priorities (max 3)：
   - 等 Leonard：broader Option C batch-1 resume 抑或先做其他 OP？
   - 🔴 §E.10 admin-login client-side gate（RLS family 已 close，admin-login 獨立 OPEN）
   - broader Option C batch-2~6 / 細項 backlog（local↔Supabase reconcile / freshness metadata / SOURCE_ALIASES polish）
6. Risks / blockers:
   - **新 §D codified workaround**：Claude service-role REST 對 catalog 一律 HTTP 406；INSPECT live catalog 須 wrap SECURITY DEFINER RPC 3-step ritual（Leonard paste APPLY → Claude call → Leonard paste DROP）。生產 DDL 嘅 Dashboard-only lock 不變（§C.4 / §E.13）。
   - **§E.14 §8 教訓延伸**：service_role bypass RLS by default → Option C broader 嘅 `cb3_b2_pagecarry_migrate.py` driver service-role upload path **不受 RLS 影響、唔需改**；driver 一行唔改可 resume。**新前置條件**：寫任何「以 anon key 改 wiki_chunks」嘅 path = 死路（RLS deny + GRANT REVOKE 雙重攔截，設計如此），如果未來需要 anon-write 必須 §3 HIGH-risk + 新 policy。
   - broader Option C 2 URL-encoding fail（細 fix、resume 前 patch、5 分鐘）。
   - Channel B 暫無 RLS-induced regression（5/6 live smoke PASS、化學評估 0 屬 query-relevance 非 RLS）；continue 監察 Render auto-deploy + 任何 anon-side 寫操作（將來如果加 anon-write feature）。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-20（Leonard「收工」）** — §4 closeout 完成；S121 Supabase RLS critical hardening 生產 live + 5/6 Channel B smoke PASS 0 regression + commit pushed HEAD `fd22e0a` origin/main 同步；§4a trigger=False（308 行 < 400、oldest entry 2026-05-19 < 30d）；下次起手＝問 Leonard 排序 broader Option C batch-1 resume（先 5min URL-encoding patch）／轉做其他 OP（§E.10 admin-login client-side gate / freshness metadata / FAIL-A 等）。

## Previous Session Record
1. UTC date: 2026-05-20
2. Session ID: Claude_20260520_0700 (Session 120)
3. Completed:
   - ✅ **[Option C pilot 完成生產 live]** Leonard S119 closeout 唯一 open next → 揀做 pilot scope（3 最高流量 marker-less PDF）。§3 HIGH-risk PLAN→pilot scope confirm→C-0/C-1/C-2 gated 三 phase→QC→PERSIST，全 §3 正常流程。
   - ✅ **[C-0 READ + CHANGE]** scoping read 揭：74 marker-less 源 = 64 PDF 可救 + 4 HTML + 5 xlsx 結構天花板；3 pilot 都係 PDF + `url_primary` 200 reachable（`url_landing` 多 404 §E.12）；PyMuPDF 1.27.2 available。新增 `dev/vault/repage_pdfs.py`（PyMuPDF page-by-page → 每頁前綴 `=== Page N ===` 對接後端 `extractFirstPage` regex；保留原 header + annot；default = dry-run）。
   - ✅ **[§3 deviation #1：char drop 比錯]** dry-run 報「50-60% char drop」係 bug：`p.stat().st_size`(bytes) vs `len(text)`(chars) 比錯，UTF-8 中文 3:1。停 + 出 diff scan → 證 g06/g26 byte-identical content（純加 markers）+ sag **net positive**（legacy pdftotext miss 203 sentences、3 broken-layout artifacts；whitespace 40.8%→13.1% noise removal 非 loss）→ Leonard 揀 proceed。
   - ✅ **[§3 deviation #2：repage backup vs rglob ghost]** C-1 spot-check 揭 backup 喺 `dev/vault/<src>/_pre_repage_<ts>/` 被 `bw.load_vault_sources()` 遞歸 rglob 撈埋 → ghost duplicate；driver 由 PAGE_RE filter 保住但 `build_wiki_index.py` 全 rebuild 會 double-process。停 + 報 Leonard → Option A：(1) `mv` 3 backup dirs → `dev/init_backup/<ts>/cb3c_pilot_legacy/` (§5.a-compliant) (2) patch repage_pdfs.py 未來 backup 寫 §5.a 位置 (3) re-snapshot robust。
   - ✅ **[C-1 量度 PASS（post-Option-A clean）]** 112=112 unique source_id、0 ghost；**INVARIANT 109/109 PASS**（非 pilot chunk-id sets byte-identical）；pilot 100% page-resolvable（g06 403→412、g26 18→19、sag 83→**383** content recovery confirmed）；whole-vault 13.2%→23.7%→**32.2%**；by-id spot-check 5 chunks/源 全帶 marker + 對位 PDF page。
   - ✅ **[C-2 dry-run + execute]** dry-run：g06 300→412 / g26 23→19 / sag 415→383；EXECUTE：Phase 1b 全 814 chunks 先 embed（~$0.001 cost）→ wiki_index.json auto-backup `dev/init_backup/20260520_104531_UTC/` → per-source DELETE→upload→count verify 全 OK → `--skip-local` 按 §E.14 紀律。
   - ✅ **[QC post-execute 4 gates PASS]** Supabase total 10,682（exact）/ pilot 3 per-source count match / marker-less control 6 條（g04/g25/g05/circ_edbc24017/stat_enrolment_2024/role_facts_curriculum）unchanged / sample chunks 帶 `=== Page N ===` marker。
   - ✅ **[Live smoke 北極星端到端 verified]** g26 q=「幼稚園收生安排」p=2/3/4 (0.67-0.70) / sag q=「學校行政手冊 校本管理」TOP-1 p=1 (0.657，content 對 2026-05 版 fresher than registry metadata)；B-2 既有源 0 regression（g01/g02/pri_curr_guide_2024/va/pe 全正常）；free-tier `57014` 撞中 retry 即恢復（§C.4 known transient）。
   - ✅ **[PERSIST]** SESSION_LOG S120+verbatim、SESSION_HANDOFF baseline/OP regen/本 record、PROJECT_MASTER_SPEC（§D 新方法 + §E.14 延伸註）、CODEBASE_CONTEXT Directory Map + Maintenance Log、HANDOFF_PACKAGE §2 chunks 10,606→10,682；DOC_SYNC matrix scan；commit+push 指定檔。
4. Pending（待 Leonard 排步伐）:
   - **Option C broader（61 marker-less PDFs）**：pipeline generalize-ready，等 Leonard 排分批步伐
   - 細項 backlog：local↔Supabase reconcile / sag freshness metadata / g06 vs pri_curr_guide_2024 near-dup polish（全低優先）
   - 既有 deferred：🔴 Supabase `57014`/probes-introspect / §E.10 / FAIL-A（record-only）/ Q4（deferred 獨立 track，未明示勿掂）
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 等 Leonard：Option C broader 排步伐？／轉做其他 OP？
   - 🔴 Supabase 57014/probes-INSPECT / §E.10 / FAIL-A
   - P2 分類 148 + P3 / Mobile UI P2 / Q4 契約（deferred track）
6. Risks / blockers:
   - **本 session deviation #2 codified（§D 新註）**：backup 一律走 §5.a-compliant `dev/init_backup/<ts>/`、唔可放被 watch 嘅 data tree 內（避 `load_vault_sources()` rglob 撞 ghost）；broader Option C 沿用同 pattern 必守。**§E.14 §8 教訓**繼續：完整 reuse `upload_wiki_to_supabase.py` seen_ids dedup + per-source DELETE/replace（pilot 守得住、broader 必續守）。
   - local `wiki_index.json` vs Supabase 42 源 diverge（Supabase query-authoritative；reconcile 低優先 backlog）。
   - sag_2025_11 content fresher than metadata（EDB 已 2026-05；source_id/title 仲係 2025-11）— freshness backlog 非 blocker；對外 contract 唔變。
   - 64 marker-less PDF 可救 → 9 結構天花板（4 HTML + 5 xlsx）救唔到；CB-3 北極星全覆蓋上限 ≈ 88%。
   - Supabase free-tier 偶發 `57014`/冷啟 transient（retry 即恢復，非 regression）；🔴 probes=8 live 未獨立 introspect；🔴 §E.10；🔴 FAIL-A（record-only）；§3c regression 既有 FAIL-A/B record-only。
   - 檔案 dormant 非刪（q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint 全可逆，勿當 dead code 清）；Q4 契約 Channel A 管道照常餵下游未郁，未 Leonard 明示勿掂契約/下游；Stage-2 closed 勿復活。
   - egress 間歇每次自測（onrender /health 勿照抄）；EDB PDF 永遠用 `url_primary` 唔好 `url_landing`（後者多 404 §E.12）；路徑含空格 shell 必雙引號絕對路徑；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-20（Leonard「收工」）** — §4 closeout 完成；S120 CB-3 Option C pilot 3 sources（sag_2025_11/g06/g26）page-carry 生產 live + 全部 commit+push（HEAD `5f7cb7a` 同步 origin/main）；§4a trigger=False（236 行、3 entries、oldest 2026-05-19）；下次起手＝問 Leonard Option C broader（61 marker-less PDFs）分批步伐 / 轉做其他 OP（57014 INSPECT / §E.10 / FAIL-A 等）。

## Previous Session Record
1. UTC date: 2026-05-19
2. Session ID: Claude_20260519_1801 (Session 119)
3. Completed:
   - ✅ **[方向定案]** Leonard live-test S118 PLAN-1b 5 query → 裁定 Channel B 最好、A 雜訊、A+B 被 A 拖累（實證 FAIL-A/§E.11）→ 定**搜尋介面 Channel-B-only**；Q4 對外契約收斂 deferred 獨立 track；CB-3 頁數＝北極星、結構上只 B 可做。
   - ✅ **[§3 HIGH-risk 正常流程]** 出 PLAN（5 surface inventory + §3d matrix）→ Leonard「同意做」+ scope 修正（q.html/index.html 亦去 link、檔 dormant；文案對齊；t-purchase B-only 知悉）。PLAN→confirm→CHANGE，非 §2 rule6 override。
   - ✅ **[CHANGE Phase 1，5 前端 surface 最小可逆]** app.html（default B、CHANNEL_OPTS=[B]、selector gated、stale 2,874→10,736）；index.html（刪 q.html link、ftags+hero/feature/flow 文案對齊 B）；t-purchase.html（channel radio 單一 B、fallback 'B'、刪 q.html link）；mobile.js（/combined→/channel-b、nav 去 q.html）。backend endpoint/`knowledge.json`/`guidelines.json`/q.html 檔本體/A·AB code path **零接觸 dormant**。
   - ✅ **[QC]** git scope=4 前端檔；契約+backend zero-diff；B-only grep 0 residual；q.html 留檔；app.html `{}`/`()` 平衡 invariant＝clean HEAD；npm check/build ✅；regression:semantic delta=0 new（既有 FAIL-A/B record-only）；§3d 5/5 靜態。
   - ✅ **[CB-3 Phase 2 診斷 + Option B B-1]** 唯讀診斷：根因＝語料 provenance（39/113 vault 有 `=== Page N ===`、74 無含高流量 sag/g06/g26；UI/後端已 work）。Leonard 揀 Option B → §3 HIGH-risk PLAN（B-1 本地可量→B-2 生產 GATED）確認。CHANGE B-1：`build_wiki_index.py` +`chunk_text_with_page_carry()`（carry last-seen 頁標記；無標記源 byte-identical 保 hash/id）。量度（離線無 embed/upload）：**39 標記源 100% chunk 帶頁、全庫 13.2%→23.7%（+1017）、74 無標記源 0 changed INVARIANT PASS、spot-check 頁正確**。
   - ✅ **[CB-3 Option B B-2 生產落地，Leonard informed go]** dry-run 揭 build_wiki_index hash-dedup vs live 失效（§3 div #1）→ 改專用 driver `dev/cb3_b2_pagecarry_migrate.py`（canonical chunker + update_g04 transport）；read-only blast dry-run（39 源 DELETE 2807→INSERT 2297）披露後 Leonard 明示執行。首輪 25 源乾淨；`stat_enrolment_2012` 409 incident（漏 seen_ids dedup → DELETE 後變空，§3 div #2）依 §3 停+診斷+報 Leonard → Leonard 揀「修 dedup + 補做 14 源」→ driver 加 seen_ids/--only/--skip-local → scoped 復原 14 源全 OK。全 39 源 page-carry 生產 live；唯讀 verify（total 10606、per-source OK、marker-less control 未掂）+ live smoke（g01 p=5/1、g05 p=30/16/9、va p=27/52、相關度 0.59-0.67 無 regression；一次 0→retry 即恢復＝已知 transient）。§8 incident 固化 §E.14/§D.15。
   - ✅ **[PERSIST]** SESSION_LOG S119+CB3 B-1/B-2 block+§8 段+verbatim、SESSION_HANDOFF baseline/OP重生/本 record、PROJECT_MASTER_SPEC §F/§B/§A/§C.4/§E.13/§E.14/§D、CODEBASE_CONTEXT+Maintenance Log、DOC_SYNC、auto-memory；commit+push 指定檔。
4. Pending:
   - **Option C**（74 無標記源含 sag/g06/g26 高流量，達北極星全覆蓋）— Leonard 排。local↔Supabase reconcile + build_wiki_index hash-dedup latent（低優先 backlog）。Q4 deferred；Stage-2 closed。（Phase 1 渲染 Leonard browser-verify PASS 2026-05-19 = closed。）
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - 問 Leonard：CB-3 推唔推 Option C（74 無標記源含 sag/g06/g26）？（Phase 1 browser-verify PASS、closed）
   - 🔴 Supabase `57014`/probes-introspect / §E.10 / FAIL-A（record-only）
   - P2 分類148 + P3 / Mobile UI P2 / Q4 契約（deferred track）
6. Risks / blockers:
   - CB-3 B-2 完成生產 live（39 源 page-carry verified）；採購程序 偶發 0→retry 即恢復＝已知 free-tier `57014`/冷啟 transient（非 regression）。
   - **§E.14 §8 教訓**：新 Supabase upload path 必須**完整** reuse `upload_wiki_to_supabase.py` seen_ids dedup + per-source DELETE/replace；唔可只抄一半（已 fire）。
   - local `wiki_index.json` vs Supabase 對 39 源 diverge（Supabase query-authoritative；reconcile 低優先 backlog，非生產影響）。
   - Phase 1 渲染 Leonard browser-verify PASS 2026-05-19（已驗、closed）。檔案 dormant 非刪（q.html/A·AB/backend endpoint 可逆勿清）。
   - Q4 對外契約 deferred 未郁未明示勿掂；Stage-2 closed 勿復活；🔴 Supabase `57014`/probes live 未 introspect；🔴 §E.10；🔴 FAIL-A；§3c regression 既有 FAIL-A/B record-only。egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 git 外；改 Draft commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成；Phase 1 全完成 closed（promote+QC+commit+push + Leonard browser-verify PASS）；CB-3 Option B（B-1+B-2，含 stat 409 incident 修+復原、§8 固化 §E.14）全完成生產 live + commit+push；§4a apply（SESSION_LOG 490→157，5 條→dev/archive/SESSION_LOG_2026_Q2.md，保留 S119/S118）；HEAD origin/main 同步。下次起手＝問 Leonard 排 **Option C**（74 無標記源，唯一 open next）。

## Previous Session Record
1. UTC date: 2026-05-19
2. Session ID: Claude_20260519_1300 (Session 118)
3. Completed:
   - ✅ **[Stage 2 判定非可行、正式放棄]** Leonard `/goal A` → §3 HIGH-risk PLAN → offline acceptance gate FAIL（combo regress 病假/體罰/幼稚園收生/STEAM）；獨立 audit 確認真（根因＝上游 ranking defect，cutoff 結構上救唔到）。依 §3 偏離 + PLAN 停 CHANGE、唔 ship regression。
   - ✅ **[§2 rule 6 衝突→Leonard 授權自主]** /goal A vs no-ship-regression 報 Leonard → dismiss「wait」→「我不知道點決定，你按最終目標選擇及行動，直至/goal」＝授權。
   - ✅ **[pivot PLAN-1b，promote]** agent-team：診斷根因（CPD allowlist-gap / 其餘 within-allowlist mis-rank）→ 建 4 條 dedicated selective route → 獨立 audit（揭 worker 病假 overstatement、§E.3 SAG≤3 closed、無 hijack）→ live-verify（真 probes=8 可救 gold 全 surface）。CHANGE：`searchChannelB.ts` +4 route（fixed cutoff 不動、無 combo、唔掂 S117 masking）。
   - ✅ **[QC]** routing 12/12；npm check/build ✅；regression:semantic delta=0 new（FAIL-A/B record-only 未碰）。
   - ✅ **[§2 rule 6 OVERRIDE]** HIGH-risk promote 在 Leonard standing 授權 + agent-team 四重控制 + live-verify 下進行 → comply + record（本 + SESSION_LOG）。
   - ✅ **[PERSIST]** SESSION_LOG S118+verbatim、SESSION_HANDOFF baseline/OP重生/Supabase notes/本 record、PROJECT_MASTER_SPEC §E.3/§D/§C.4、CODEBASE_CONTEXT Maintenance Log、DOC_SYNC、memory；commit+push 指定檔（觸發 Render auto-deploy）。
4. Pending（待 Leonard）:
   - (a) 跑唯讀 probes=8-live INSPECT (b) Supabase free-tier probes=8 `57014` timeout 生產可用性 (c) 病假 combo-gap future PLAN-1c vs fixed-only / CB-3 北極星 — Leonard 排序。
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - probes=8-live INSPECT / Supabase timeout / CB-3+病假 gap（Leonard 揀）
   - 🔴 FAIL-A（record-only）/ §E.10（deferred）
   - P2 分類148 + P3 / Mobile UI P2 / HKEAA
6. Risks / blockers:
   - **Stage 2 adaptive combo 放棄（勿復活，雙獨立驗證 dead-end；root cause＝ranking 非 cutoff）**；PLAN-1b 已 promote，生產 deploy 待 Render auto-deploy（smoke 前勿宣稱 released）。
   - 🔴 Supabase free-tier probes=8 偶發 `57014` statement-timeout（生產可用性，retry 恢復）；🔴 probes=8 live 未獨立 introspect（依賴 probes 行為前必跑唯讀 INSPECT）；schema.sql 曾 drift→PGRST203（§E.13；生產 DDL 仍 Leonard Dashboard）。
   - 🔴 §E.10；🔴 FAIL-A；§3c regression:semantic 既有 FAIL-A/B record-only（本 change TS-only delta=0）。
   - 病假 combo .5→.25 known gap（非本 promote 範圍）；egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 git 外；改 Draft commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成；Stage-2 goal-A **closed-as-non-viable**（雙獨立驗證）；PLAN-1b shipped + post-deploy smoke 確認 cpd route 生產 live（SAG cap=3）；HEAD `84033b1` origin/main 同步；§4a trigger=False（399 行）。下次起手＝問 Leonard 排 (a) probes-INSPECT (b) Supabase `57014` timeout (c) CB-3·病राgap。

## Previous Session Record
1. UTC date: 2026-05-19
2. Session ID: Claude_20260519_0715 (Session 117)
3. Completed:
   - ✅ **[Leonard /goal C]** agent-team 三隊唯讀一致裁定 (c) 行先（feasibility c>b>a / audit c→b→a / monitor c→a→b）後，Leonard 設 binding `/goal C` = 修 masking-defect。
   - ✅ **[masking-defect FIXED]** `searchCombined.ts` `.catch` 唔再重用 `degradedChannelBResponse`（=「未配置」）；新增 `failedChannelBResponse`（`degraded_kind:"error"` + `CHANNEL_B_ERROR_REASON`）+ combined `channel_b_status` discriminator（"unconfigured"|"error"）。最小 additive、零前端 coupling、保留 A-only graceful degradation；genuine-unconfigured 路徑不變。
   - ✅ **[QC]** npm check/build ✅；§3d deterministic harness 13/13（S2 真 fetch-fail→status=error 非 未配置、A 仍貢獻；S3 dedicated unconfigured classifier 不變）；regression:semantic overall=FAIL 但 **delta=0 new**（既有 FAIL-A/B record-only、未碰）。
   - ✅ **[PERSIST]** SESSION_LOG S117+verbatim、SESSION_HANDOFF baseline/OP重生/Supabase notes/本 record、PROJECT_MASTER_SPEC §E.13/§C.4/§D.14、CODEBASE_CONTEXT Maintenance Log、DOC_SYNC；memory `reference_supabase_pgvector_probes` L22 更新；commit+push 指定檔（觸發 Render auto-deploy）。
   - ✅ **[§2 rule 6 OVERRIDE]** (c)=§3 HIGH-risk；Leonard 全 scope 知情下 binding /goal = 授權，risk 已述、code-only 無 Supabase DDL、git-reversible → comply + record（本條 + SESSION_LOG）。
4. Pending（待 Leonard）:
   - **Stage 2 adaptive threshold（完成 PLAN-1 promote；§3 HIGH-risk；強烈建議先唯讀 probes=8-live INSPECT）** vs **PLAN-1b（CPD/expansion，Testing/ 先）** — Leonard 排序。
5. Next priorities (max 3 — 詳見 Open Priorities)：
   - Stage 2（連 probes-live INSPECT）/ PLAN-1b（Leonard 揀）
   - 🔴 FAIL-A regression（record-only）/ §E.10 admin security（deferred）
   - P2 分類148 + P3 / Mobile UI P2 / HKEAA
6. Risks / blockers:
   - **masking-defect 已修 = promote-blocker 清除**；生產 deploy 待 Render auto-deploy on push。**PLAN-1 promote 仍未完成（Stage 2 未做）勿宣稱 released**；生產 probes=8（Stage-1 FULL PASS）但 *live* 未獨立 introspect（Stage 2 前必做唯讀 `pg_get_functiondef`，audit-flagged）。
   - 🔴 schema.sql 曾 drift→PGRST203 live 事故；任何 Supabase RPC DDL 前必 INSPECT live `pg_get_functiondef`、勿信 schema.sql（§E.13；生產 DDL 仍 Leonard Dashboard 親手）。
   - 🔴 §E.10 admin-login security；🔴 FAIL-A；§3c regression:semantic 既有 FAIL-A/B record-only（本 change TS-only 不影響、delta=0）。
   - egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. Session 進行中（**非** closeout — Leonard 未表示「收工」）：goal C 完成、§3 PERSIST 完成、commit+push 完成；待 Leonard 下一步排序（Stage 2 / PLAN-1b）。

## Previous Session Record
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
  - ✅ **S117 FIXED** (was S116 promote-blocker): `searchCombined.ts` `.catch` now returns `failedChannelBResponse` → combined surfaces `channel_b_status:"error"` + `CHANNEL_B_ERROR_REASON`, distinct from genuine unconfigured (`channel_b_status:"unconfigured"` + 未配置). Real Channel B failures now visible to monitoring/eval via the `channel_b_status` discriminator (no more fake "未配置" masking). Genuine-unconfigured path (`searchChannelB.ts` `isSupabaseConfigured()` guard) unchanged. Dedicated `/api/search/channel-b` still recommended for live-grade (no route-level catch — methodology unchanged). Deploy: Render auto-deploys on push to main.
  - 🔴 **S118: free-tier probes=8 intermittent statement-timeout** — live-verify saw 2/5 RPC calls return HTTP 400 / Supabase `57014` "canceling statement due to statement timeout" at probes=8 (succeeded on retry; one was cold-start, one intermittent ~60s after a healthy call). Production-availability risk independent of retrieval correctness; post-S117 it correctly surfaces as `channel_b_status:"error"` (not fake "未配置"). Open Priority — options: lower probes / app-level retry / paid tier. probes=8-live itself still NOT independently introspected (audit-flagged; read-only `pg_get_functiondef`/`proconfig` SQL prepared, not yet run).
  - **S118: Channel B routing +4 dedicated selective routes** (`searchChannelB.ts` `TOPIC_KEYWORDS`/`SOURCE_SETS`/`QUERY_EXPANSIONS`, first-match before `finance`): cpd, kg_admission, conduct, steam (PLAN-1b promote; fixed cutoff unchanged; SAG in cpd/conduct bounded by per-source quota cap=3 → §E.3-safe). Stage-2 adaptive combo abandoned (non-viable; do not revive).
- Permissions: anon role needs BOTH `GRANT USAGE ON SCHEMA public` AND `GRANT SELECT ON wiki_chunks TO anon`
- Upload: `SUPABASE_SERVICE_KEY` (service_role) required for insert; anon key for read-only search
- Conflict resolution: `Prefer: return=minimal` (NOT merge-duplicates); dedup by ID before batching
