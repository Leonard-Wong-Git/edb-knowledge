# Session Handoff

## Current Baseline
1. Version: **v2.3.0**；git `main`=`origin/main` HEAD = **`58b5705`（S143 qa_inspection route fix）== origin/main；起手自行 verify。S116–S142 history → SESSION_LOG + dev/archive（下文 S125 narrative 屬歷史殘留、待下次 closeout 收斂入 compactness budget）**。**S125：CB-3 Option C broader batch-4 + batch-5 + batch-6 Hybrid（共 22 marker-less PDF page-carry + 2 deprecation）= 三批一日打完、達 CB-3 final ceiling ~88% + Freshness workflow chronic-fail triaged + §8b audit cross-check rule first live application + g24/sag NEW semantic-supersede lesson + NEW deprecation script `cb3_deprecate_stale.py` + driver 6th-validation**。Batch-6 Hybrid（Leonard `/goal go` full-flow auth）：2 page-carry（g15 22KB 3p / edbcm98_2024_pri_science 354KB 6p）+ 2 DROP-only deprecation（pe_sss_2007_2015 119 chunks superseded by pe_sss_2023 S125b / sci_jss_supp_2017 76 chunks superseded by sci_jss_framework_2025 S125b）= total DELETE 206 INSERT 9 net **-197**；Supabase 10,117→**9,920**。Live smoke deprecation ranking improvement verified：sci_jss_framework_2025「初中科學 學習架構」TOP-1+#2 p=29/27 0.540/0.514（superseder direct dominate post-deprecation）；pe_sss_2007_2015 完全不再 surface（cleanup verified）。NEW `dev/cb3_deprecate_stale.py`：DROP-only tool（service_role REST DELETE + per-source verify count==0 + Phase backup audit log + --skip-local + --execute gate；Python 3.9 PEP 604 compat fix `from __future__ import annotations`）。INVARIANT 8 spot-check 0 touched（va_sss_2015 180 / music_sss_2015 161 等 Vanilla preserved 6 stale 確認 untouched）。Batch-4（10 sources）：Gate 1 10/10 PASS（pages 383 / backup `dev/init_backup/20260526_073931_UTC/`）→ Gate 2 DELETE 537 INSERT 417 net -120 → Supabase 10,253→**10,133** → smoke 4/10 direct surface。Batch-5（10 sources Vanilla strategy = g24 / g29 / sci_jss_framework_2025 / pe_sss_2023 / edbcm183_2023_values_edu / sec_curr_guide_2017_booklet_6a / edbcm58_2024_pri_science / pri_science_cert_course_list / edbcm57_2024_pri_science / edbcm243_2024_pri_science）：Gate 1 10/10 PASS（pages 616 / backup `dev/init_backup/20260526_124023_UTC/`）→ Gate 2 dry-run 揭 **g24 300→383 +28% content RECOVERY**（撞 legacy 300 cap、同 S122 eng_lit +111% / S123 eng_sss +40% pattern；Monitor agent 模型 update need：large-page docs 都有 cap-recovery risk、非 era-dependent）+ 其餘 9 sources -16~-26% canonical → Gate 2 EXECUTE DELETE 752 INSERT 736 net **-16**（vs predict -188、差源 g24 cap-recovery）→ Supabase 10,133→**10,117** → smoke 5/10 surface（3 direct + 2 cross-query bonus）。**§8b audit cross-check rule FIRST LIVE APPLICATION (S125b)**：揭發 **8 stale-superseded sources 仲 in index 共 1,010 chunks (~10% Supabase)** = va_sss_2015 (180) / ethics_relig_sss_2007_2019 (166) / music_sss_2015 (161) / econ_sss_2007_2015 (147) / econ_sss_supp_2015 (39) / bafs_sss_2007_2015 (122) / pe_sss_2007_2015 (119) / sci_jss_supp_2017 (76)；Leonard 揀 Vanilla 保 §A.2 #1 traceability、deprecation 推 batch-6 評估。**S125b NEW semantic-supersede lesson**：g24 vs sag_2025_11 registry `supersedes=[]` 但實質 same-domain elder vs newer consolidated（同 KLA + same naming pattern + title overlap）；audit cross-check 之前只用 registry supersede field、未 catch semantic-level（S122 tech_kla/S123 music_sss_2024 同 pattern）→ §8b rule extension promote candidate。driver `cb3_b2_pagecarry_migrate.py` **5th-validation**：50 sources S122-S125b 0 incident、pipeline production-ready confirmed。**Mid-session Freshness workflow chronic-fail triage**：`.github/workflows/freshness_check.yml` 5 連 fail since 2026-04-30，root cause = `dev/source/check_freshness.py` line 141-142 `if errors > 0: sys.exit(1)`，非 batch 觸發；SESSION_HANDOFF Regression Notes #2 stale 確認；列下次 session priority #2。**S124：CB-3 Option C broader batch-3（10 marker-less PDF）page-carry 生產 live + batch-4 pre-flight 完成**。Batch-3（chi_sss_guide_2021 / chi_lit_guide_2025 / eng_nat_sec_2025 / eng_jss_supp_2018 / ma_sss_diversity_2021 / ct_programming_pri_2020 / bafs_sss_2007_2020 / hmsc_sss_2007_2015 / dat_sss_2007_2015 / dat_sss_supp_2020）Gate 1 10/10 PASS（578 total pages / backup `dev/init_backup/20260525_133417_UTC/`）→ Gate 2 EXECUTE DELETE 942 / INSERT 795 / net -147 / Supabase 10,400→**10,253**→ live smoke 7/10 surface + 3 ranking competition non-regression。**S123：** batch-2（10 sources）생산 live，DELETE 1,698 / INSERT 1,529 / Supabase 10,569→10,400，9/10 smoke，Audit 揭 3 superseder swap（ethics_relig/music/va 舊→新版）。Supabase RLS hardened S121。Q4 deferred；Stage-2 closed 勿復活。probes=8 live confirmed；57014 transient retry 即恢復。**S123：CB-3 Option C broader batch-2（10 marker-less PDF）page-carry 生產 live + 0 regression + agent-team 3 parallel pre-flight + Audit agent 揭 3 superseder swap**（va_sss_2015→values_edu_framework_2021_trial / ethics_relig_sss_2007_2019→ethics_relig_sss_2024 / music_sss_2015→music_sss_2024，避 stale-policy contamination 違北極星 traceability）。§3 HIGH-risk Gate 1 vault `--write` 10/10 PASS（markers==pages 110/150/140/113/133/89/99/114/55/116、total 1,119 pages；content sanity 100.7-102.4%；§5.a backup `dev/init_backup/20260524_204849_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 sources canonical normalization -16~-24%、1 source `eng_sss_guide_2021` 300→421 +40% = content RECOVERY 撞 legacy 300 cap，cap 係 chunker-bound 唔係 era-dependent）→ Gate 2 EXECUTE 10/10 OK（DELETE 1,698 / INSERT 1,529 / net -169 / Supabase 10,569→**10,400** 命中 Monitor agent floor prediction、per-source `del/ins/now` 全對齊）→ live smoke 9/10 batch-2 sources surface（**ethics_relig_sss_2024 0.687/0.686 batch 最高分** / ict / ma / bio / tour_hosp / values_edu / history / tl 全部 top-2 hits in top-5；eng_sss_guide_2021 retry via English query 0.625/0.624 confirm data live、原 Chinese query 撞 Supabase `57014` transient = PMS §C.4 known、非 regression；music_sss_2024 0/5 ranking 競爭 arts_kla_guide_2017+music_p1_s6_2024 同 KLA = data indexed 確認、non-regression 同 S122 tech_kla pattern）。**S122：CB-3 Option C broader batch-1（10 marker-less PDF）page-carry 生產 live + 0 regression** — Leonard 起手「resume broader Option C batch-1」明示授權 → Gate 1 vault `--write` 10/10 PASS（markers==pages 全對、content sanity 100.6-102.5% 無 quality regression、backup §5.a-compliant `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 sources canonical normalization -16~-26%、1 source `eng_lit_guide_2023` 300→633 +111% = content RECOVERY 撞 legacy 300 cap）→ Gate 2 EXECUTE 10/10 OK（DELETE 2,503 / INSERT 2,390 / net -113，Supabase wiki_chunks 10,682→**10,569** exactly match prediction，per-source `del/ins/now` 全對齊）→ live smoke 8/10 batch-1 sources 確認 surface with **PAGE NUMBERS**（地理科探究主題 → geog_jss p=106 0.667 + geog_sss p=66 0.612；化學實驗 → chem_sss top-3 p=145/80/40 0.65/0.62/0.61；英國文學選讀 → eng_lit top-3 p=8/9/81 0.48/0.46/0.46 **content +333 chunks recovery 北極星 live verified**；宗教倫理 → religious_edu p=18/67；公民及社會發展科 → ces_jss p=19；物理科 → phys_sss p=143。剩 tech_kla / ls_jss / chi_hist 本輪 query 無 surface = ranking/topic-routing 競爭非 regression、data 確認已 indexed）。**Whole-vault page-resolvable：13.2% (pre-B) → 23.7% (post-S119) → 32.2% (post-S120) → ~55.2% (post-S122)** = 5,830 / 10,569 chunks；52/113 vault sources marker-bearing（39 B + 3 C pilot + 10 batch-1）。**Remaining：51 marker-less PDFs**（batch-2~6、driver + repage_pdfs.py 完全 generalize-ready）+ 9 結構天花板（4 HTML + 5 xlsx）→ CB-3 final ceiling ≈ 88%。`§E.14` driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused（service_role bypass RLS、S121 已 verify）；seen_ids / per-source DELETE/replace pattern 維持、0 incident。**S121 commit `fd22e0a` diff 已 apply URL-encoding patch（commit msg 同 SESSION_LOG 講「pending 5min patch」係 S121 內部 drift；§G.2 verify-code-not-docs 教訓再驗）**。**Frontend test link 已提供：** https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search surface、Leonard browser-verify pending）。**S121 closed：Supabase RLS critical security incident response 完成生產 live + 0 regression** — Leonard 截停 broader Option C batch-1 中段（safe stop：vault 0 mutate / Supabase 0 mutate）+ 出示 Dashboard 警報「`rls_disabled_in_public` on wiki_chunks」(2026-05-17 raised)。**INSPECT 揭發遠超警報 surface：** `wiki_chunks` 對 `anon` GRANTS 實有 SELECT+INSERT+UPDATE+DELETE+TRUNCATE+REFERENCES+TRIGGER 全套寫權限（PMS §C.4 doc drift：寫「anon 需 GRANT SELECT」實 live 全 write 都通；任何 anon 用戶可清空/投毒/篡改 wiki_chunks）。§3 HIGH-risk PLAN→ Leonard Dashboard 親手 paste：`ALTER TABLE ENABLE RLS` + `CREATE POLICY wiki_chunks_anon_read FOR SELECT TO anon,authenticated USING(true)` + `REVOKE INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER FROM anon,authenticated`；`service_role` GRANTS 不變、broader Option C upload 不受影響（service_role bypass RLS by default）。Post-APPLY re-INSPECT 確認 live state（RLS ON / 1 policy / anon=SELECT only / service_role full / `match_wiki_chunks` 屬性 unchanged）；**Channel B 5/6 live smoke PASS 0 regression**：採購 g01 0.66/0.62 + role_facts_finance 0.638（byte-identical pre-baseline）/ 幼稚園收生 g26 p=2/4 0.696（S120 pilot intact）/ 學校行政手冊 sag p=1 / 教師專業操守 sag p=205 + g05 p=30 / 化學 sci_jss+chem_sss；「化學評估」0 hits 非 regression（query 太 narrow + threshold 0.22）。Cleanup：DROP temp inspect RPC、schema clean。Dashboard 警報 async clear（下次開 Dashboard 順手 confirm）。**新 PMS §D codify**：「INSPECT live Supabase catalog via temp SECURITY DEFINER RPC」3-step ritual（Claude 無 catalog REST path）。**broader Option C batch-1 paused 等 resume**（tasks #3-#7 pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT 已 +10 entries benign prep；2 URL-encoding fail = geog_sss_2007_2022 / ces_jss_2024 path 含空格，resume 前 5min patch）。**S120 closed：CB-3 Option C pilot 完成生產 live** — sag_2025_11/g06/g26 page-carry、Supabase 10,606→10,682；whole-vault page-resolvable 23.7%→**32.2%**；INVARIANT 109/109 PASS。**S119 closed：搜尋介面 Channel-B-only Phase 1 + Option B 全完成生產 live + Leonard browser-verify PASS**。**S118 closed：Stage-2 adaptive combo non-viable、PLAN-1b 4 dedicated route promote** — 詳見 Previous Session Records。**S117 closed：masking-defect FIXED**（`channel_b_status` discriminator）。**S116 closed：`backend/supabase/schema.sql` 改 text 變體 + plpgsql volatile + probes=8（生產 live，Leonard Dashboard 套用）**。⚠️ probes=8 *live* 本 session 經 RPC INSPECT 再 confirm（`language plpgsql VOLATILE` + `set local ivfflat.probes=8` + `SECURITY INVOKER` + owner=postgres）；Supabase free-tier probes=8 偶發 `57014` statement-timeout 已知 transient（retry 即恢復）。Q4（Channel A→`knowledge.json`→Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。local `wiki_index.json` vs Supabase 對 42 源 diverge（reconcile 低優先 backlog）。sag_2025_11 PDF EDB 已從 2025-11→2026-05；source_id 仍 `sag_2025_11`（freshness metadata backlog、非 blocker）。
2. Frontend: `index.html` K1 landing page (hero + features + CTA); `t-purchase.html` S3/S4/S5 draft flow; `q.html` local `knowledge.json` Quick Q&A; `app.html` full React SPA / management workspace.
3. Knowledge state: **455 Channel A facts** (三層同步 ✅ byte-identical；dedup 792→455 commit `711f911`), **0 candidates in queue**, **Supabase 10,594 chunks**（**S142 EDB-coverage sweep §1 學校行政及管理 +35 政策文件 +298 chunks**〔NEW gov_admin + safety 路由〕；prior 9,963 post-**S141 SEN-adjacent backfill +51**：`sen_exam_arrangements_2025`《為有特殊教育需要學生提供校內考試特別安排》2025〔sea_guide_c.pdf、SENSE portal、del=0 ins=51、加 SOURCE_SETS.sen、live smoke #1 p=9 帶頁碼〕；prior 9,912 post-**S138 SEN data-quality fix**：phys_sss_2007_2015 182 CID-glyph 亂碼 DROP −182 + g10《特殊學校課程指引》(2024,116p) +129 + g19《全校參與模式融合教育運作指南》(2026-01,88p) +116；g10/g19 皆 §E.12 URL re-discovery〔registry index.html/wsa-hub → 真直連 PDF〕+ mojibake pre-flight CLEAN；SEN dedicated route live〔TOPIC_KEYWORDS.sen 置 curriculum 前 + SOURCE_SETS.sen + QUERY_EXPANSIONS.sen〕，「sen」route 去 g19/g06 真內容 @0.71-0.76 帶頁碼；prior 9,849 post-S135；**S135 = Phase 3a #3 + Phase 3 全力完成**：(1) history_jss_2019 西史/世界歷史初中 backfill del=0 ins=125〔§E.12 URL re-discovery〕；(2) **Phase 3c** edbc197_2024_ph_pri 通函197/2024 backfill del=0 ins=12〔§E.12 同 pattern〕；(3) stat_edb_figures mojibake fix del=2 garbage ins=1 clean；(4) backend `SOURCE_SETS.curriculum` 加 history_jss_2019 + history_sss_2007_2015〔西史高中 pre-existing gap〕+ edbc197_2024_ph_pri + Render auto-deploy live verified；prior 9,713 post-**S132 Phase 3b**）。Vault: 122 sources 提取完成；page-carried 累計 + **history_jss_2019 + edbc197_2024_ph_pri 2 S135 backfill** = **155 sources Supabase page-carried**（S141 +sen_exam_arrangements_2025；S138 +g10 +g19 SEN backfill、−phys DROP）；**3 deprecated**（S138 +phys_sss_2007_2015 CID-glyph mojibake DROP）；0 stale Vanilla preserved。Whole-vault page-resolvable **~85%**；CB-3 final ceiling **~88% 達成**。**Phase 3c 結構天花板源**（arts_curr_docs / moral_civic_curr / ph_pri_curr）= children 全已各自索引、catalogue 只含導航文字 → 結構 no-op（已文檔化、不索引以免 Channel B noise）。**指引數字 4 層（161 app 內庫〔S140 landing-curate +9 + 公積金 +4〕/ 152 公開 guidelines.json〔S140 全集投影〕/ 203 source_registry〔S142 §1-5 +51〕/ 120 vault-extracted）見 PROJECT_MASTER_SPEC §B.1 釐清框 — 39→152 = EXECUTED（S140：39→139 收斂、landing-curate +9 KLA/課程指引→148、公積金 +4 HR→152；由 `dev/build_guidelines.py` 生成、registry=SSOT、勿手寫）**。 **S143：Channel B 拆 `qa_inspection` 路由（視學/校外評核/自我評估/表現指標/問責/校本管理 由 gov_admin 移出 + 針對性 expansion；tight SOURCE_SET〔sse_tools/perf_indicators/edbc15_2022_accountability+SAG〕+ per-source quota = over-expansion-safe）→ 修短 QA query under-recall（視學 0→5 帶頁）；HEAD `58b5705`、純 routing 0 data mutation 可逆；Supabase 10,594 / registry 203 不變。**
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
> 產品方向：**搜尋介面 Channel-B-only**（S119 定，A/AB dormant；Q4 契約 deferred）。北極星＝合理＋指引＋**頁數**（CB-3 不可 defer）。Stage-2 closed 勿復活。**CB-3 達 final ceiling ~88%**（**155 marker-bearing post-S142§5**（S141 +sen_exam_arrangements_2025 SEN校內考試特別安排；S138 NEW 2 SEN backfill：g10 特殊學校課程指引 + g19 融合教育運作指南，皆 §E.12 URL re-discovery；S135 history_jss_2019 + edbc197）+ 3 deprecated（+S138 phys mojibake DROP）+ 結構天花板 + others）。**Phase 3 = a/b/c 全部完成**（3a ranking polish 全 healthy no-op + 1 backfill；3b S132 6-stale page-carry；3c 1 backfill + 1 mojibake fix + 3 結構 no-op）。**driver `cb3_b2_pagecarry_migrate.py` 13 輪 verified（S122~S135、68 sources 0 final incident；S135 全新源 backfill path〔header-stub seed + del=0 純 INSERT〕×2 + mojibake re-index ×1 0 incident）+ `cb3_deprecate_stale.py` 0 incident**。**S132：PolicyChecker brand launch + Phase 3b 6-stale page-carry closed**（custom domain `policychecker.wongfu.net` live + OG/iframe/embed-sample + 5-round brand unification + 6 sources DELETE 743 INSERT 646 net -169；Supabase 9,882→**9,713**）。
1. **🔵 ACTIVE — EDB 全覆蓋 gap sweep（Leonard /goal「做齊1+2、抓取分析審核入庫」）**：逐範疇掃 EDB 站政策/指引/通函全文 PDF、agent-team 審核、就建議自主 ingest（relevance/approval/逐範疇 scope 已 locked）。**9 範疇 roadmap：①學校行政 ✅(+35) ②教師/人事 ✅(+3) ③學生訓育輔導支援 ✅(+7) ④校園安全✅ ⑤收生/學位分配 ✅(S142：+3，NEW placement 路由；多家長表格HTML非政策) ⑥通函EDBC ④校園安全 ⑤收生/學位分配 ⑥通函EDBC（ASPX app 不可靜態枚舉；高價值已§1-5捕捉~18條）⑦SEN✅(S141) ⑧課程✅(~130飽和) ⑨雜✅(g09/eng_nat_sec/g28已覆蓋)**。**SWEEP 核心完成 + S143 Channel B QA recall fix（qa_inspection route）+ Q4 Phase 1（凍結 Channel A）✅ EXECUTED。** **Q4 ③→① phased（Leonard 明示「執行 Phase 1」）：Phase 1 = K1-side docs-only freeze（knowledge.json 凍 @455 停更、schema 不變、下游零改變、pipeline dormant 可逆）已完成；Phase 2 = 選項① 下游 Circular System 轉 Channel B = 跨 repo、待 Leonard 喺下游 repo 協調（K1 只備 spec、絕不掂對方 repo §A.3）；選項② 不採（衝突 §F.6）。**〔已 RESOLVED：S141 g14/sen_curr_area/gifted_policy_docs 結構天花板 + sea_guide；S140 39→152 guidelines〕
2. **觀察（非阻塞）**：freshness 第一個 scheduled 週跑（週一 09:00 UTC）應正常偵測 + 開/更新 `freshness-change` Issue；57014 backend retry 喺真冷啟動下嘅 mask 效果（warm SEN smoke 已 6/6；cold-start mask = logic-verified、留實際使用觀察）。
3. **🔴 既有 deferred + low-priority backlog**：§E.10 admin-login client-side gate（**S131 ACCEPTED + DOCUMENTED**，conditional；拆掉 client-side-only 前提即須 reopen）；57014 transient（**S139 已加 backend retry、deploy live**；exhaust 後仍 400、frontend 有重試掣）；FAIL-A 注入 regression（record-only）；**Q4 對外契約收斂**（Channel A→knowledge.json→Circular System、3 選項、未明示勿掂）；**§8b rule 2**（semantic-supersede KLA-title embedding similarity check 暫 process-level、automated sub-agent 留 future）；**`Suppl_guide` 非華語補充指引全文 PDF held 待人核**（S140 round-2，year 不明 + g09 主題重疊）；**knowledge.json._meta.stats.guidelines=39 stale**（升 152 與否，獨立 data-touch follow-up）；HKEAA；**stat_fact 21 chunks 仍 cite 2024/25**（升 2025/26 ROI≈0 因 Channel B filter `content_type!=="stat_fact"`）；doc-debt。

> ✅ **S143 完成（Channel B QA recall fix — 拆 qa_inspection 路由、生產 live、0 regression）**：Leonard「先試用 Channel B 廣度→補 QA gap」。18-query paced live smoke 證 Channel B substantially「夠用」（14/18 乾淨命中 + 17/18 帶頁 + synth 質素好；3 miss = benign ranking competition 已記）；唯一 net-new gap = gov_admin QA 子群短 query under-recall（「視學」→0，gov_admin 無 expansion + docs 用新詞）。Fix = `searchChannelB.ts` 拆 `qa_inspection` 專route（QA terms 由 gov_admin 移出 + 針對性 expansion；tight SOURCE_SET〔sse_tools/perf_indicators/edbc15_2022_accountability+SAG〕+ per-source quota = over-expansion-safe）→ commit `58b5705` push → Render deploy → live smoke **qa 5/5 + regression 12/12 + 0 QA-doc 洩漏**（視學 0→5 帶頁 0.65-0.75）。0 data/Supabase/guidelines mutation、可逆。 **+ Q4 Phase 1（凍結 Channel A，③→① phased、Leonard 明示「執行 Phase 1」）= docs-only freeze**：knowledge.json 凍 @455 停更、schema 不變、下游零改變、pipeline dormant 可逆、endpoint 不刪、guidelines.json 不凍續 live；PMS §F.2/§B.1 + CODEBASE Key Decisions/AI-log + K1_API_SPEC root+dev advisory 更新；Phase 2 下游轉 Channel B = 跨 repo 待 Leonard（§A.3）。0 data mutation、git revert 可逆。
> ✅ **S141 完成（SEN/資優 0-chunk 補完 — sea_guide_c.pdf page-carry +51、生產 live、0 regression）**：Leonard 揀「g14+資優 SEN 補完」→ §3 HIGH-risk PLAN → **Phase-0 read-only crawl** 3 個 named 0-chunk id（g14/sen_curr_area/gifted_policy_docs）→ 證實全屬 hub/HTML-only/dup（**g14 純 HTML 14 分章、EDB 無 PDF 版 = 結構天花板無頁碼；gifted_policy_docs 靜態 nav-only；sen_curr_area = curriculum-area hub，主 child《特殊學校課程指引》= g10 已 ingest，子頁爆成 ~179 智障學科 exemplar = 另一 scope 噪音**）→ STOP 報 Leonard，curate 結論「真‧淨增益僅 1 份」→ Leonard 揀「只 ingest sea_guide」。**唯一真政策 PDF**《為有特殊教育需要學生提供校內考試特別安排》(2025-09修訂、46p、sea_guide_c.pdf、SENSE portal、mojibake pre-flight CLEAN、distinct from g19 ie_guide）→ 新 registry `sen_exam_arrangements_2025`（151→152）+ repage Gate1 46/46 markers + cb3_b2 Gate2 **del=0 ins=51 純加法**（Supabase 9,912→**9,963**、chunks 帶 `=== Page N ===`）+ backend SOURCE_SETS.sen + QUERY_EXPANSIONS.sen parity（S135 backfill-allowlist coupling）+ typecheck/build exit 0 + commit `e7215e2` push → Render deploy → **live SEN smoke PASS**（「特殊教育需要 校內考試特別安排」→ 新源 #1 p=9 @0.74 + #6 p=44；bare「sen」非回歸 g19/g06 共存；「英文科課程指引」route curriculum 零污染；融合教育SENCO g19 主導 + 新源 #4，全帶頁碼）。driver `cb3_b2` **16th-validation 0 incident**。**3 個 named id 標結構天花板/勿再 ingest** 已 codify 入 PMS §16。0 knowledge/guidelines.json mutation。
> ✅ **S140 round-3（公積金覆蓋，Leonard 指定：guidelines.json 148→152）**：Leonard 問公積金條例有冇覆蓋 → 多層 grep：標題層（guidelines/registry/Channel A）**0 公積金**，但內文層有（學校行政手冊 sag/g24 各 81 處，引《教育條例》85條/《強積金條例》/《津貼·補助學校公積金規則》）+ live Channel B 查「公積金」已 synthesis + 8 results 帶頁碼（用戶本來搜到）。Leonard 指定加 EDB 公積金 hub url → 主 agent 爬（hub 底下 ~90 PDF 多數係季度財報/年報非指引）→ 加 4 真 entry（category=人力資源/hr，HEAD-200 驗證）：provident_fund（hub HTML）/ sspf+gspf_general_info_2023（官方一般資料 Q&A）/ pf_edu_ord_2013_faq（《2013教育修訂條例》FAQ＝直接答「條例」）。registry 157→161、公開 148→**152**（hr 桶 2→6）、版本 2.4.0→2.5.0、self-test PASS -0 lost。0 Supabase/backend/knowledge mutation。
> ✅ **S140 round-2（landing-page curate：+9 真指引入 registry + 修 3 data bug、guidelines.json 139→148、agent-team 分工+審核）**：Leonard 追問 16 個保留嘅「課程文件目錄頁」可否 resolve 成真文件 → 主 agent 爬 16 頁（egress；sub-agent egress 被 deny per S138）共 159 連結 → **agent-team（Agent tool）**：3 個 curation agent 並行分組判 KEEP/DUP/NOISE + 1 個 audit agent 對抗覆核（8/8 KEEP 0 降級、揪 2 漏網、立 R-DOC 規則、grep 把錯 claim 收窄 3→1）→ 主 agent egress 逐份核實真 url + 開 PDF 抽真 title（揪正：agent 把 ma pmc/jsmc/ssmc 誤標「課程指引」實為「數學KLA指引補充文件—學習內容」；apl url 404 真 url 含 `&`；Suppl_guide year 不明→held）。**結論：16 目錄頁真‧淨增益僅 ~9 份**（其餘 71 dup + 77 雜訊語言版本/分章/海報）。**加 9 entry**（cle_kla/chi_pri_lo/chi_sec_lo/pth_2017/pshe_kla/ma 三冊/apl_ca，全 HEAD-200+首頁驗證）+ **修 3 data bug**（sci_kla url 指錯 pshe 頁→science PDF / edbc20+edbc9 format / edbc197 url=index→PDF）。registry 148→157；build_guidelines.py regen 139→**148**（curriculum 桶 123→132）、版本 2.3.0→2.4.0、self-test PASS 回歸守衛 -0 lost。`Suppl_guide`（非華語補充全文 PDF）held 待人核（year 不明 + g09 主題重疊）。0 Supabase/backend/knowledge.json mutation。
> ✅ **S140 round-1（公開 guidelines.json 39→139 全集投影 + NEW generator、push live、0 code/data/Supabase mutation）**：Leonard 揀下一階段 = 39→148 擴展（S112 deferred-intent）→ §3 HIGH-risk PLAN + 兩輪 scope 確認。**公開端點由 39 精選子集 → 148 registry 全集投影 139**（純規則剔 9 非文件：`sub_category=='stat'` 7 統計表 + `format=='DOCX'` 1 表 + url 含 `vertexaisearch` 1 壞連結 religious_edu_jss〔= religious_edu_jss_2024 重複〕；保留 landing 頁 + g10/g16/g28〔format=INDEX 但真指引、原已公開〕）。對外契約變更：curriculum 桶 25→123；**現有 39 條 0 lost**（回歸守衛 verified）；版本 2.2.0→2.3.0。**NEW `dev/build_guidelines.py`**（registry=SSOT、投影 schema + category→topic 映射 + 純規則 drop + `--self-test` 回歸守衛 + 原子寫入）—— 根治「手寫 guidelines.json 必 drift」根因；**日後 registry 加文件 re-run `python3 dev/build_guidelines.py --write` 即同步、勿手寫**（DOC_SYNC 已登記）。**§3 CHANGE divergence**：原把 g10/g16/g28（format=INDEX）誤當導航頁、捉返佢哋係真指引保留。Docs synced: PMS §B.1+§F.9 / K1_API_SPEC(root+dev) / README / CODEBASE / DOC_SYNC。Follow-up：`knowledge.json._meta.stats.guidelines` 仍 39（另一資料檔 stat、未越界改）。
> ✅ **S139 完成（文件變更自動偵測+通知 建好＋啟用＋live + SEN「冇反應」修復 + mobile verify、0 outstanding bug）**：(1) `check_freshness.py` 升級 hybrid HEAD+content-hash 偵測（authoritative 抑制 HEAD 假報）+ classify_change 純函數 + --self-test(9) + 原子寫入 + exit 語義保留（changes 永不 fail，S126）；`freshness_check.yml` issues:write+timeout30+github-script 開/更新 `freshness-change` Issue + ledger commit；FRESHNESS_GUIDE + DOC_SYNC row 更新。**啟用**：首次 write-sync 植 147/147 content_hash（0 error）+ `freshness_changes.md` ledger；每週一自動偵測；re-ingestion 仍人手閘。對抗覆核（Explore agent）揪 1 BLOCKER（registry 寫腐爛→原子寫入）+ 2 MAJOR（API try/catch、null 欄）全修。(2) **SEN「冇反應」根因 = Supabase 57014 transient（冷啟動最易中）被包成 400**（非 route/CORS/前端）→ `wikiRepository.ts` searchWiki RPC retry-on-57014（≤3 次、embedding 不重算）；deploy live、SEN smoke 6/6 PASS 200。(3) mobile #guidelines Leonard 真機確認 OK。commit chain `dbef61a`→`48d5308`→`d96d56a`→`13544d0`→`eed168c`。data 層只 freshness content_hash seed，Supabase chunks/knowledge 0 mutation。**§G.2 起手又中**（交接 HEAD b17defc 實測 4be7155、benign closeout commit）。**run_in_background 教訓**：唔好再加 `nohup … &`（會 detach 兼令 wrapper 提早 exit）。
> ✅ **S138 完成（資料質素 backlog 三項全執行、生產 live、0 regression）**：Leonard AskUserQuestion 三項全授權（①SEN route 即做 ②phys 即 DROP ③g10/g19 要 ingest）。**(1) phys_sss_2007_2015 182 CID-glyph 亂碼 DROP**（cb3_deprecate_stale.py、reversible audit log；9,849→9,667）。**(2) g10《特殊學校課程指引》(2024,116p,+129) + g19《全校參與模式融合教育運作指南》(2026-01,88p,+116) ingest**：兩者皆 **§G.2 doc-drift**（交接寫「同 S135 history_jss PDF pattern」低估工作 — 實測 g10=`source_type=index`〔index.html 導航頁〕、g19=`source_type=html`〔wsa hub〕，**皆要 §E.12 URL re-discovery crawl 揾返真直連 PDF**〔g10 attachment CGSS Full / g19 SENSE portal ie_guide_ch.pdf〕；兩者 **mojibake pre-flight CLEAN**〔phys 教訓落實：ingest 前必驗 text layer 非 CID-glyph〕；repage Gate1 116=116 / 88=88 markers + cb3_b2 Gate2 del=0 純 INSERT）。**(3) SEN dedicated route**（searchChannelB.ts：TOPIC_KEYWORDS.sen 置 curriculum 前 first-match + SOURCE_SETS.sen=[g06,sag_2025_11,role_facts_student,role_facts_general,g10,g19] + QUERY_EXPANSIONS.sen；typecheck+build exit 0 + offline detect() 真 assert 全 PASS）→ commit `4048408` push → Render deploy → **live SEN smoke 5/5 PASS**（sen→g19 p=6/10/13 @0.76/0.75/0.72 + g06 SEN @0.72；融合教育SENCO→g19 p=13/10/57；g10-specific→g10 p=39 @0.697；curriculum-regression「英文科課程指引」→curriculum 不破；全 FFFD=0 帶頁碼）。Supabase 9,849→**9,912**。driver `cb3_b2` 15 輪 verified（+g10+g19 新源 backfill）+ `cb3_deprecate_stale.py` 2nd-use 0 incident。Sub-agent egress 教訓：背景 general-purpose agent Bash/WebFetch/WebSearch 被 deny → egress-heavy discovery 主 agent 自己做。
> ✅ **S136 完成（Mobile UI Phase 2 — 文件庫 #guidelines 專用 mobile render）**：Leonard 確認 Channel B 已到設計天花板（CB-3 ~88% final ceiling、剩 ~12% = 4 HTML + 5 xlsx 結構性硬限不可再升）→ 揀 option 4，資料源拍板 148（桌面一致）。**READ 實證交接 claim stale（§G.2 又中）**：交接寫 4 個 mobile 介面未 render，實測只 `app.html#guidelines` 真缺（`mobile.js:421` 留明文 TODO「下節做專用 mobile render」、現時 fallback 硬露桌面 `w-44` React panel 壓爆 375px；index/q/t-purchase 已響應式）。**CHANGE 3 檔**：(1) `app.html` +9 暴露 `window.GUIDELINES_REGISTRY`(148) + `dispatchEvent('k1-registry-ready')`；(2) `mobile.js` 新 `buildGuidelinesShell()`（分類橫向 chips〔zero-count 隱藏〕+ 階段 chips + 最新/最舊/名稱排序 + 名稱搜尋 + 文件卡 tap→EDB，filter/sort 鏡像桌面 GuidelinesPanel）+ guidelines 分支 event-driven build + 12s poll backstop + revealRoot fallback + hashchange→reload；(3) `mobile.css` `.m-guide-*` 樣式（既有 `@media(640px)` + design tokens）。**§3 divergence — TDZ bug（live-preview probe 揪出）**：首輪 shell 唔 build 且 0 console error → probe 揪出 `ReferenceError: Cannot access 'GUIDE_CATS' before initialization`；根因 = IIFE 頂 eager `if(readyState!=='loading')initMobileShell()` 排喺 `const GUIDE_CATS` 之上（deferred script 'interactive' 跑早過 const）→ **修：eager-trigger 搬 IIFE 尾，連帶修 search shell latent TDZ**。**QC live preview（Electron real engine 375px + 1280px）全 PASS**：6 §3d scenario（148 卡/8 分類/6 階段/「148 份」/最新排序、課程→127、+中學→52、搜尋採購→1、名稱 reorder、TDZ 後 0 error、tab hashchange→reload 換 shell）+ desktop no-op（React `.w-44` 正常、registry 無害）+ search-shell 0 regression；debug probe 全清。commit + push origin/main → GitHub Pages deploy（policychecker.wongfu.net）；Leonard 真機 verify pending。0 Supabase/knowledge/backend mutation。
> ✅ **S135 完成（Phase 3a #3 = 5 源 no-op + history_jss_2019 西史初中 BACKFILL 修復 mis-route）**：Leonard 揀 Phase 3a #3 → 4-step read-only diagnostic 5 cluster（geog 457 / pe 153 / dat 108 / ict 216 / music_sss 198 chunks）全 **healthy no-op**（live smoke topical query 正確 surface + 頁碼；地理「地理科課程指引」嗰個 HTTP 400 = 已知 57014 transient、re-probe `地理科`→geog_jss p=106 正常）。唯一真 finding = **history_jss_2019（歷史科課程指引 中一至中三 2019 = 西史/世界歷史初中）= 0 chunks 真 coverage gap**；查明 root cause = **§E.12 EDB URL churn**（原 hist_c_j1-3_2019.pdf 直連失效→registry 改指 catalogue HTML→從未提取）。Leonard 授權 HIGH-risk backfill → **EDB catalogue 解析搵返 rename 後直連 PDF**（Hist_Curr_Guide_S1-3_Chi_final_10072019.pdf HTTP 200 / 118p / 內容核實西史初中、與中史 CHist_* 及西史高中 Hist_C&A 互不重疊）→ registry 修正（url_primary 直連 + source_type pdf）→ repage Gate 1 118 pages/markers（header-stub seed 新源 path）→ cb3_b2 Gate 2 **del=0 ins=125 純新增**（Supabase 9,713→**9,838**）。**§3 CHANGE divergence**：backfill 完數據在庫但 curriculum-category query 仍 mis-route 去中史 → 根因 = backend `SOURCE_SETS.curriculum` allowlist 未含 history_jss_2019（建表時佢仲係 0-chunks）→ STOP 報告 Leonard → 授權加 allowlist（只加初中、高中 pre-existing gap 暫不加）→ `npm check`/`build` exit 0 → commit `ceb7c91` push → Render auto-deploy → **live verify FIXED**（「歷史科課程指引 中一至中三」→ history_jss_2019 #1/#2/#3 p=1/46/6、中史降 #4/#5）。**Lesson（§8 monitoring，§E.12 + NEW backfill-allowlist coupling）：把新源 backfill 入 Supabase 唔會自動 surface — topic-routed category 受 `SOURCE_SETS` allowlist gate，新源必須同時加 allowlist 先 surface。** 之後 Leonard `/goal「Phase 3 全力完成」`→ **Phase 3c**：edbc197_2024_ph_pri 通函 backfill（同 §E.12 pattern、del=0 ins=12）+ stat_edb_figures mojibake fix（del=2 garbage ins=1 clean）+ 西史高中/edbc197 allowlist parity；arts_curr_docs/moral_civic_curr/ph_pri_curr = 結構 no-op（children 全索引）。**Phase 3 (a/b/c) 全完成、Supabase 9,849、commit chain `ceb7c91`→`60dc174`→`5d0d002`→PERSIST、全 Render deploy live verified。**
> ✅ **S134 完成（Phase 3a #2 batch 5 源 = no-op + 429-masquerade near-miss）**：Leonard `/goal 1` 揀 Phase 3a #2 → 跑 tech_kla / chi_hist / ls_jss / arts / econ 4-step diagnostic（live onrender smoke + Supabase service-role REST count）。**CRITICAL CORRECTION**：初步因 HTTP 429（onrender 10 req/min + Supabase throttle）被 script 印成 0/ERR/空白頁 → 誤判 ls_jss = 24 chunks/0 pages 需 page-carry；STOP 後修正 ls_jss 真實 = **251 chunks 已 page-carried healthy**（live smoke「生活與社會中一至中三」→ ls_jss top-3 p=78/8/76）→ **避免咗對正確數據跑冇必要破壞性 Supabase mutation**。真實 counts（429 已濾）：tech_kla cluster 571（tech_kla 237）/ chi_hist 中史 277（history_jss_2019=0 西史初中真 gap）/ ls_jss 251 / arts cluster 617（arts_kla 116）/ econ 2025版119+舊143。Classification：tech_kla/chi_hist/ls_jss/econ = healthy no-op；arts = 輕微 ranking 競爭（arts_kla_guide_2017 完整書名被 2024 分科音樂/視藝指引壓出 top-5）Leonard 裁示可接受 newer-guide-優先 no-op（強推反壓低有用分科、同 g29 quota-cap 反效果同理）。**Lesson（§G.2 5th-instance candidate）：throttled API response 會偽裝成數據；診斷必須 distinguish 429 vs 真 0 + pace live smoke。** 0 code/data/Supabase mutation。
> ✅ **S133 完成（Phase 3a #1 g29 dominance diagnostic = false-alarm）**：Leonard hypothesis「幼稚園相關資料本身就不多」empirically confirmed。Inventory: source_registry 151 sources 中 KG-related 只 4 個（g29 主框架 / g25 / g26 收生 / stat_kg），user-facing 只 3 個（stat_kg `content_type=stat_fact` 已被 Channel B filter 排除）。Supabase chunk count: g29=107（KG 庫 84.3%）/ g26=19 / g25=1 / stat_kg=8；KG total user-facing 127 chunks = 全 Supabase 9,713 嘅 **1.3%**。Live smoke 5 KG queries top-5 distribution: 幼稚園收生→g26 #1+#2+#3（正確）/ 幼稚園教師專業發展→g06 #1+#3+#4（g29 完全 yield）/ 幼稚園課程框架→g29 #1+#2+#3（合理、g29 核心 topic）/ 幼稚園評估→g29 #1+#3+#4（合理）/ 幼稚園教學語言→g29 #1+#2+#3（合理）。**Root cause = (b) data scarcity reflection**，**非 (a) ranking bug**。Fix decision: **No-op + 文檔化**（Leonard 揀）— quota cap 會將 g29 從 top-5 踢走、留空位俾跨域非-KG sources surface，反而傷北極星 traceability。Phase 3a #1 closed。0 code/data/Supabase mutation。
> ✅ **S132 完成（PolicyChecker launch + Phase 3b）**：(A) Phase 2 brand launch — custom domain `policychecker.wongfu.net` live (CNAME → leonard-wong-git.github.io / TTL 7200 / HTTPS Let's Encrypt) + 4 HTML OG/Twitter meta + 4-size PNG favicon + og-image PNG→JPG WhatsApp fix (1.7MB→151KB / 1200×630) + multi-origin CORS allowlist + `embed-sample.html` 學校 IT iframe demo + 5-round brand unification (titles 純功能 / hero+logo "EDB+政策核對" / body "香港學校政策搜尋平台" / OG site_name "PolicyChecker · 政策核對")。(B) Phase 3b — agent-team 6-parallel audit (Explore subagent_type) 6 superseder PDF prefaces → 0/6 explicit「取代」found per Leonard rule → all 6 KEEP + page-carry per「照做」directive；DELETE 743 INSERT 646 net -169；Supabase 9,882→**9,713**；100/113 marker-bearing。(C) §3 CHANGE divergence + clean recovery — first execute halted mid-bafs on Postgres 22P05 NUL-byte invalid Unicode escape (1 NUL @ offset 95212 in bafs repaged.txt = PDF extraction artifact); STOP+report Leonard + 3-option fix → Leonard Option B (strip NUL + driver patch + re-execute = durable §8 regression fix); cb3_b2 `build_rows()` defensive `ch.replace(\x00,"")` 1-line additive 永久 codified, future PDFs auto-clean; re-execute 6/6 OK. driver 10th-validation S122-S132 65 sources 0 final incident。Commit chain S132 origin/main: `c6dab15`→`d2a7cac`→`2c0fde1`→`d86dfe5`→`d10d12f`→`062fb88`。
> ✅ **S131 完成（recovery path）**：§E.10 (a) admin-login client-side gate **OPEN → ACCEPTED + DOCUMENTED**（doc-only path、code 0 mutation；commits pending Leonard re-confirm post §3 divergence #3）。SHA-256 round-trip verify 揭兩處 sub-claim 修正：(i) archive line 190「(password: internal)」係 placeholder 寫錯 (`SHA-256("internal") = 3bed2c...054f` ≠ live ADMIN_HASH)；(ii) archive **line 213** `sha256("...") matches ADMIN_HASH` form **contains real plaintext = TRUE git-leak existing since Session 28/29 era closeout**（QC 自爆 false negative grep — 原 pattern 只 match `password:` form 漏 `sha256()` form）。即原 §E.10 (a) leak claim 嚴格係對的、但 leak point misaligned (line 213 ≠ 190)。**Attack surface 重新評估近 zero**：admin features 全 client-side localStorage + JSON snapshot；snapshot 內容 = INITIAL_DATA 已 public in source；攻擊者用 archive plaintext 入 cosmetic gate 後得 0 net 新資料。ACCEPTED rationale = 「leak attack value ≈ 0」非「no leak」。§3 CHANGE divergence textbook execute **3 halts**: #1 Terminal output 撞 existing hash + #2 Leonard self-attest real pw 推翻 placeholder-leak claim + #3 QC self-surface real leak relocated to line 213 + self-redact own SESSION_LOG entry transient plaintext。**§G.2 banner 4-instance pattern (S121 schema.sql / S122 commit-msg / S126 handoff-hypothesis / S131 governance-leak-claim-misaligned)** codified 入 PMS §E.10 防線 #2 + #6。3 governance docs updated (PMS §E.10 + SESSION_HANDOFF + SESSION_LOG); 0 code/data/Supabase mutation; commits pending Leonard re-confirm。
> ✅ **S130 完成**：batch-7 follow-up — 4 stat xlsx vault content refresh to 2025/26 (cb3_b2 `--include-non-page` first use)。Step 0 §5.a backup `dev/init_backup/20260527_172106_UTC/stat_refresh_legacy/`。Step 1 stdlib zipfile XML xlsx parser 揭 49/49 數字對齊 2024/25 (0 drift)；4 new vault `extract_<src>_2026m05.txt` 含 2025/26 column (6-col tab-aligned schema-compatible)；4 old `_2026m10.txt` deleted。Step 2 cb3_b2 patch +`--include-non-page` flag + sb_count/sb_delete optional `content_type` filter (ct_filter=vault_extract narrowed DELETE 防 wipe co-located stat_fact)；marker-bearing path unchanged (regression smoke g01 + full-94 0 incident)。§3 CHANGE divergence textbook execute (dry-run 揭 DELETE 33 wipe stat_fact → STOP & report → Leonard 3-option fix → ct_filter patch → re-dry 12/12 net 0 → execute)。Gate 1+2 EXECUTE 4/4 OK (per-source del=3 ins=3 now=3) + wiki_index auto-backup `dev/init_backup/20260527_173802_UTC/` + Phase 3 SKIPPED `--skip-local`。QC 4 PASS: Supabase 9,882 unchanged (net 0) / per-source vault_extract=3 + stat_fact preserved 5/6/6/4 / INVARIANT 7 spot-check g01=32 sag=383 chem=172 eng_lit=633 music_p1_s6=85 va_p1_s6=71 arts_kla=116 全 unchanged / backend `/health` warm 455。Live smoke direct-Supabase verify: stat_kg 2025/26+958+113204+7.9:1+14.9% / stat_pri 317233 / stat_sec 347820+184003+30335 / stat_special 9311+4884+4427 全 NEW content indexed。driver 9th-validation across 59 sources S122-S130 0 incident — first non-page source path + first ct_filter use + first `--include-non-page` flag 全 0 regression。NO touch: build_stat_facts.py / stat_facts.json / source_registry / knowledge.json / guidelines.json / PROJECT_MASTER_SPEC / backend / app.html。commits pending origin/main。
> ✅ **S129 完成**：batch-7 content refresh — 3 PDF marker-bearing (arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024) 重 fetch EDB live + repage_pdfs.py --write Gate 1 3/3 PASS + cb3_b2_pagecarry_migrate --execute Gate 2 3/3 OK (DELETE 310 / INSERT 272 / net -38) + Supabase 9,920→9,882 + INVARIANT 5 spot-check 0 touched + live smoke 2/3 surface direct NEW page numbers (music p=11/16 0.704/0.701 + va p=17/11 0.727/0.723) + arts ranking non-regression。driver 8th-validation 55 sources S122-S129 0 incident。commit `86f8c4f` origin/main。
> ✅ **S128 完成**：S126 follow-up trio closed — (c) sanity check g29/g24 size-spike = 非 EDB drift，係 freshness baseline 本身 stale（baseline 之前 fetch 拎到 landing redirect HTML 1.3KB/1.5KB 而非 PDF body）；vault content 對齊 EDB live PDF；(a) g28 dead URL EDB re-discovery，§E.12 pattern fix — `it-in-edu/Information-Security/information-security-in-school.html` 404 → `it-in-edu/information-security.html` 200（EDB 拍平 subdir + lowercase），url_landing + url_primary 兩 fields 同步；commit `9122964`；(b) freshness persist run（write mode）= Checked 147 / Changes 22 / Errors 0 / Threshold 7 / exit 0；147 sources × 22 updates 自動修正 g28+g24 baseline + 對齊 14 sources EDB content updates baseline；commit `9f5c514`；registry +228/-216 lines。
> ✅ **S127 完成**：§8b 3-rule promotion + PROJECT_MASTER_SPEC governance doc full update — (1) §D.16 extend with batch-3/4/5/6 verified state + rule 1 (audit cross-check stale-superseded) + rule 2 (semantic-supersede detection) (2) NEW §D.19 documenting `cb3_deprecate_stale.py` (3) §G.2 banner +4th drift instance = rule 3 (handoff root-cause estimate ≠ ground truth) (4) §G.3 NEW #7 (triage agent never skip live-reproduce)；CODEBASE_CONTEXT Directory Map +`cb3_deprecate_stale.py` + AI Maintenance Log +S127 entry；SESSION_HANDOFF Open Priorities regen；§3d 7-scenario static verify PASS；4-file scope（PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / SESSION_HANDOFF / SESSION_LOG）+ 0 code/data/Supabase mutation。
> ✅ **S126 完成**：Freshness workflow chronic-fail triage closed — `dev/source/check_freshness.py` bug fix（line 101 `AttributeError: 'NoneType' object has no attribute 'get'` 撞 `freshness_metadata=null`，coerce `meta = src.get(...) or {}`）+ threshold gate (`errors > max(5, total_checked//20)`) + summary 加 failed-sids list；dry-run 147/20/1/exit-0 verified；§G.2 ops 第三次應用（handoff 估計嘅 `errors > 0` 係次要、真根因係 AttributeError mask）；S128 (b) end-to-end verified successful first write-run。
> ✅ **S125 完成（三批 + deprecation）**：CB-3 Option C batch-4 + batch-5 + batch-6 Hybrid，共 22 sources page-carry + 2 deprecation；Supabase 10,253→10,133→10,117→9,920；whole-vault page-resolvable ~73.0%→~81.5%；94/113 marker-bearing + 2 deprecated；CB-3 final ceiling ~88% 達成；NEW `cb3_deprecate_stale.py` script first-use 0 incident；§8b 2 rules surfaced + first live applied；Freshness chronic fail triaged。
> ✅ **S124 完成**：CB-3 Option C broader batch-3（10 sources）page-carry 生產 live；Supabase 10,400→10,253；whole-vault page-resolvable ~64.4%→~73.0%；72/113 sources marker-bearing；batch-4 pre-flight 10/10 GO / 10/10 KEEP ready。
> ✅ **S123 完成**：CB-3 batch-2（10 sources）生產 live + Audit 揭 3 superseder swap；Supabase 10,569→10,400；62/113 marker-bearing。
> ✅ **S122 完成**：CB-3 batch-1（10 sources）生產 live；Supabase 10,682→10,569；52/113 marker-bearing。
> ✅ **S121 完成**：Supabase RLS hardening（ENABLE RLS + anon-read policy + REVOKE 6 write privilege × 2 role）；0 regression。
> ✅ **S120 完成**：CB-3 Option C pilot 3 sources 生產 live；S119 Channel-B-only Phase 1 + Option B 39 sources 生產 live。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / Circular System 整合）

## Last Session Record
1. UTC date: 2026-06-04 / 05
2. Session ID: Claude_20260604 (S141+S142 連續 session — 開頭 SEN/資優 0-chunk 補完〔S141〕→ Leonard /goal「做齊1+2」→ EDB 全覆蓋 gap sweep §1-5〔S142〕；全生產 live、0 regression、Q4 deferred)
3. Completed:
   - ✅ **[S141 SEN 補完]** sea_guide_c.pdf《為有特殊教育需要學生提供校內考試特別安排》(2025,46p)→ `sen_exam_arrangements_2025` del=0 ins=51；3 個 named 0-chunk id（g14/sen_curr_area/gifted_policy_docs）crawl 證實結構天花板/hub「勿再 ingest」(codify PMS §16)。Supabase 9,912→9,963。commit `e7215e2`。
   - ✅ **[S142 EDB sweep §1-5 — Leonard 三項 scope locked：政策/指引/通函全文 PDF 相關性 / 就建議自主 ingest / 逐範疇]**：每範疇 主爬→agent-team(curate+adversarial audit)→egress 逐份核實(title/頁數/mojibake)→嚴格篩(剔 forms/exemplars/slides/海報/語言版本/事件資源)→del=0 batch ingest→路由→deploy→paced smoke。
     §1 學校行政(+35) / §2 教師人事(+3) / §3 學生訓育支援(+7) / §4 健康校園(+3，安全 core 已§1) / §5 收生派位(+3) = **+51 政策文件 / +631 chunks**；registry 152→**203**；Supabase 9,963→**10,594**(全 del=0 可逆)。
   - ✅ **[6 新/擴路由]** NEW gov_admin（問責/視學/防貪/校舍/改校名/SDP）+ safety（消防/職安/熱帶氣旋/斜坡）+ student_support（生涯規劃/和諧校園/虐兒強制舉報/危機處理手冊/健康校園）+ placement（中學派位/STIMS）+ 擴 finance/hr_admin/cpd。每範疇 paced live smoke PASS、0 regression。
   - ✅ **[§6-9 評估 bounded/飽和]** §6 通函 EDBC = ASPX app 不可靜態枚舉（高價值已§1-5捕捉~18條）；§7 SEN(S141已補)/§8 課程(~130飽和)/§9 雜(g09/國安/g28已覆蓋) = 0 net-new。SWEEP 核心完成。
   - 🟡 **[§3 CHANGE divergence 自捉自修]** over-expansion 稀釋（QUERY_EXPANSIONS 塞晒新文件詞→熱帶氣旋壓消防、edbc14 壓 g04）→ 修：新 route 靠 SOURCE_SET filter，hr_admin expansion 還原、safety/gov_admin 不加 expansion。
   - ✅ **[收工：§4a 已 archive]** SESSION_LOG 423→137 行（5→2 entries，3 條→`dev/archive/SESSION_LOG_2026_Q2.md`）。
4. Pending: **功課1 Q4（待 Leonard 明示「執行」）= 關 Channel A + 下游轉 Channel B**（不可逆 + 跨 repo〔下游 Circular System 勿掂〕+ Leonard 定咗最後一步）。Channel B 已 substantially「夠用」。**本 session sweep 主線已全清、0 outstanding bug。**
5. Next priorities (max 3):
   - **Q4（待 Leonard）**：建議先實際試用新 Channel B 廣度 confirm 真夠用 → 再出 §3 HIGH-risk Q4 遷移 PLAN（K1 側可逆 vs 下游 repo 需 Leonard 協調）
   - **觀察（非阻塞）**：freshness 週跑開 Issue；57014 cold-start；新源小文件 generic query 被 sag/g04 壓=benign ranking competition；§6 通函 ASPX 驅動(ROI 低)
   - 既有 deferred：§8b rule 2 automation / Suppl_guide held / §E.10 ACCEPTED / FAIL-A / stat_fact 2025/26
6. Risks / blockers:
   - 🟢 **0 outstanding bug**。S142 sweep 全 del=0 純加法（git revert + Supabase DROP 可逆）。
   - 🔴 **Q4 未做、不可逆、跨 repo、待 Leonard 明示**（勿自行關 Channel A / 勿掂下游 Circular System repo）。
   - 既有不變: 57014 transient(S139 retry); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Q4 deferred; Stage-2 closed; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text`; guidelines.json 勿手寫; g14/gifted/sen_curr_area 結構天花板勿再 ingest; 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。
7. **✅ S142 EDB-coverage sweep §1-5 完成（+51 政策文件 / +631 chunks / 6 路由 / Supabase 10,594）+ S141 SEN 補完。** commit chain `e7215e2`…`80368f8`…(closeout)。driver cb3_b2 17-22 輪 0 incident。起手自測全 PASS。

## Previous Session Record
1. UTC date: 2026-05-30
2. Session ID: Claude_20260530_1700 (Session 135 — Phase 3 全力完成：3a #3 5源 no-op + 2 backfill + stat mojibake fix + allowlist parity)
3. Completed:
   - ✅ **[Phase 3a #3 diagnostic 5 cluster = healthy no-op]** geog/pe/dat/ict/music_sss 4-step read-only → topical query 正確 surface + 頁碼。
   - ✅ **[history_jss_2019 西史初中 BACKFILL]** 0-chunk coverage gap（§E.12 EDB URL churn）→ catalogue 解析搵返 rename PDF → repage 118p → cb3_b2 del=0 ins=125（Supabase 9,713→9,838）。
   - ✅ **[§3 divergence — backfill-allowlist coupling]** 新源入庫但 curriculum query mis-route → 加 backend `SOURCE_SETS.curriculum` allowlist + Render deploy → live FIXED。**Lesson：新源 backfill 必同時加 SOURCE_SETS（§8b 候選）。**
   - ✅ **[Phase 3c]** edbc197_2024_ph_pri backfill del=0 ins=12 + stat_edb_figures mojibake fix del=2 ins=1 + 西史高中/edbc197 allowlist parity + 3 結構 no-op（children 全索引）。**Phase 3 (a/b/c) 全完成、Supabase 9,849。**
4. Pending: shipped — commit chain `ceb7c91`→`60dc174`→`5d0d002`→`9434581`→`27eb42e` origin/main
5. Next priorities: 下一階段方向待 Leonard / 既有 deferred backlog
6. Risks: 0 new product；NEW process caution = onrender 429 throttle 診斷必 pace；既有不變。
7. **Session CLOSED 2026-05-30（Leonard「全部 No-op + 文檔化 收尾」）** — 0 code/data/Supabase mutation。

## Session Before Previous (S132 — full detail in dev/SESSION_LOG.md)
1. UTC date: 2026-05-28
2. Session ID: Claude_20260528_0900 (Session 132 — PolicyChecker brand launch + Phase 3b 6-stale page-carry)
3. Completed:
   - ✅ **[Phase 2 brand launch — 5 commits c6dab15→d10d12f]** custom domain `policychecker.wongfu.net` live (CNAME → leonard-wong-git.github.io / TTL 7200 / GitHub Pages HTTPS) + 4 HTML OG/Twitter meta + 4-size PNG favicon + og-image PNG→JPG WhatsApp fix (1.7MB→151KB / 1200×630) + backend multi-origin CORS (env.ts + server.ts 13 callsites typecheck+build PASS) + `embed-sample.html` 公開 iframe demo + 5-round brand unification (titles 純功能 / hero+logo "EDB+政策核對" / body "香港學校政策搜尋平台" / OG site_name "PolicyChecker · 政策核對" / 學段 K1-K3 K1-S6 preserved per EDB standard)
   - ✅ **[Phase 3b 6-stale Vanilla-preserved page-carry — commit 062fb88]** agent-team 6-parallel Explore subagent audit → 2 HIGH-conf KEEP_BOTH (va_p1_s6_2024 + econ_supp_2025 explicit「請參閱/同時參閱」) + 4 UNCLEAR-lean-KEEP → 0/6 DROP per Leonard conservative rule「未明寫『取代』→ KEEP + 照做 page-carry」
   - ✅ **[§3 CHANGE divergence + clean recovery]** First execute halted mid-bafs on Postgres `22P05   cannot be converted to text` (1 NUL byte @ byte offset 95212 in repaged.txt = PDF extraction artifact between sentences); partial state: 5 untouched + bafs 122 DELETEd + 50/93 INSERTed → STOP+report Leonard + 3-option fix → Leonard Option B (strip NUL + driver patch + re-execute = durable §8 regression fix) → cb3_b2 `build_rows()` defensive `ch.replace("\x00","")` 1-line additive 永久 codified, future PDFs auto-clean → re-execute 6/6 OK
   - ✅ **[QC 3 PASS]** Supabase total 9,882→**9,713** exact match prediction / per-source del/ins/now aligned / INVARIANT 7 spot-check 0 touched / live smoke 6/6 sources `=== Page N ===` markers ✓
   - ✅ **[PERSIST + commit chain origin/main]** `c6dab15`→`d2a7cac`→`2c0fde1`→`d86dfe5`→`d10d12f`→`062fb88` + closeout `93a3b74`. driver 10th-validation S122-S132 = 65 sources 0 final incident
4. Pending: 已收工 (S132 closeout commit `93a3b74` shipped before S133 start)
5. Risks/blockers (carried forward to S133):
   - **§3 CHANGE divergence textbook execute 2nd time S122-S132** (S130 ct_filter + S132 NUL byte); halt-report-recover discipline → 0 final incident
   - **NUL-byte PDF extraction artifact recurrence-prone**: codified as defensive guard in cb3_b2 build_rows
6. **Session CLOSED 2026-05-28** — Phase 2 brand launch live + Phase 3b page-carry production live + driver 10th-validation + NUL-byte guard codified. HEAD = `93a3b74` (S132 closeout). §4a no trigger.

## Previous Session Record
1. UTC date: 2026-05-27
2. Session ID: Claude_20260527_1721 (Session 130 — batch-7 follow-up: 4 stat xlsx vault content refresh to 2025/26, cb3_b2 --include-non-page first use)
3. Completed:
   - ✅ **[Recon + PLAN HIGH-risk]** 9 sources scope (4 stat xlsx + 5 HTML) reconned; xlsx Supabase chunks = vault_extract 3 + stat_fact 5/6/6/4 = 8/9/9/7; HTML 5 sources 3 无 vault dir / 1 mojibake / 1 catalogue-only。Leonard 揀 "Diff-first 4 stat xlsx 先 read-only"。
   - ✅ **[Read-only diff]** 4 xlsx 拎入 `/tmp/edb_xlsx_diff/`、stdlib zipfile+xml parser 揭 49/49 數字對齊 2024/25 column = 0 drift；EDB「2026-04-27 updated」真意 = xlsx 加入 2025/26 新 column。Leonard 揀 "Advance to 2025/26 value-add upgrade"。
   - ✅ **[Driver decision + sub-scope]** Leonard 揀 "Extend cb3_b2 加 --include-non-page flag" + "Vault-only refresh (stat_fact 留 future)"。
   - ✅ **[§5.a backup]** `dev/init_backup/20260527_172106_UTC/stat_refresh_legacy/` 含 4 source × legacy txt + cb3_b2 pre-mod。
   - ✅ **[Re-extract vault txt × 4]** stdlib xlsx parser → 4 new `extract_<src>_2026m05.txt` (2020/21→2025/26 6-col tab-aligned schema-compatible) + 4 old `_2026m10.txt` deleted (rglob ghost dup 防)。
   - ✅ **[cb3_b2 patch +`--include-non-page`]** ~25 line additive: argparse + sb_count/sb_delete optional `content_type` + main flow `ct_filter = "vault_extract" if --include-non-page`。Marker-bearing path unchanged。
   - ✅ **[§3 CHANGE divergence textbook execute]** dry-run v1 揭 DELETE 33 wipe co-located stat_fact 21 (sb_delete source_id-only filter) → STOP+report Leonard + 3-option AskUserQuestion → "Tighten DELETE filter +content_type=vault_extract" → patch + re-dry-run DELETE 12 INSERT 12 net 0 ✓。
   - ✅ **[Regression smoke]** `--only g01` no flag = DELETE 32 INSERT 32 unchanged + full no-flag run = 94 sources unchanged。0 regression。
   - ✅ **[Gate 1+2 EXECUTE 4/4 OK]** Phase 1b embed all 12 chunks → wiki_index.json auto-backup `dev/init_backup/20260527_173802_UTC/` → per-source `del=3 ins=3 now=3 OK` × 4 → Phase 3 SKIPPED `--skip-local`。
   - ✅ **[QC 4 gates PASS]** Supabase total = **9,882 unchanged** (net 0) / per-source vault_extract=3 + stat_fact preserved (5/6/6/4) totals 8/9/9/7 全 unchanged / INVARIANT 7 spot-check 0 touched (g01=32 sag=383 chem=172 eng_lit=633 music_p1_s6=85 va_p1_s6=71 arts_kla=116) / backend `/health` warm 455 facts。
   - ✅ **[Live smoke direct-Supabase verify NEW content]** stat_kg chunk #1 = 2025/26 / 958 / 113204 / 7.9:1 / 14.9% / stat_pri 317233 / stat_sec 347820 / 184003 / 30335 / stat_special 9311 / 4884 / 4427 全 indexed。Channel B 自然 query 撞 g29 KGECG-TC-2017 dominance (S122 tech_kla / S125 econ_sss_supp 同 ranking-competition pattern、非 regression、ranking polish backlog)。
   - ✅ **[PERSIST]** SESSION_HANDOFF Open Priorities #1 narrowed + ✅ S130 完成 annotation + Last Session Record S130 + S129 demote → Previous + Risks update；CODEBASE_CONTEXT cb3_b2 description +S130 extension paragraph + AI Maintenance Log +S130 entry；SESSION_LOG S130 entry prepend + DOC_SYNC + verbatim handoff prompt。
4. Pending：
   - commit+push origin/main 指定檔 (4 vault new + 4 vault deleted + cb3_b2 + SESSION_HANDOFF + SESSION_LOG + CODEBASE_CONTEXT)。
   - **stat_fact 21 chunks 升 2025/26 wording** (future backlog — 需 build_stat_facts.py 4 builder rewrite + stat_facts.json rebuild + separate Supabase replace path)。
5. Next priorities (max 3)：
   - 等 Leonard 排：(a) stat_fact upgrade follow-up / (b) 5 HTML catalogue-level (low ROI) / (c) Future batch-7 stale Vanilla-preserved / (d) 既有 backlog (🔴 §E.10 / batch ranking polish ~15-18 sources) / (e) §8b rule 2 future automation tooling。
   - 🔴 §E.10 admin-login client-side gate (OPEN)
   - batch ranking polish backlog
6. Risks / blockers:
   - **driver 9th-validation across 59 sources S122-S130 0 incident**：first `--include-non-page` flag use + first content_type narrowing + first non-page source path 全 0 regression；pipeline production-ready confirmed (page-bearing + non-page sources 兩 mode 都 verified)。
   - **§3 CHANGE divergence-stop-report textbook**：dry-run 預先 catch DELETE 33 wipe stat_fact 問題 + 即時 halt + 3-option fix + re-verify + execute = 0 incident、0 stat_fact loss。lesson: cb3_b2 既有 sb_delete source_id-only filter 對混 content_type 嘅 sources 須 ct_filter narrow。
   - **stat_fact 21 chunks 仍 cite 2024/25「最新」wording**：retrieval 兩 layer (vault_extract 2025/26 + stat_fact 2024/25) 不一致；用戶可能撈到 stat_fact 嘅 stale wording。Future backlog 跟。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. **Session CLOSED 2026-05-27（Leonard「收工」）** — §4 closeout 完成；S130 batch-7 follow-up: 4 stat xlsx vault content refresh 2024/25→2025/26 + cb3_b2 `--include-non-page` first use + §3 CHANGE divergence textbook execute + 0 incident + driver 9th-validation 59 sources S122-S130。HEAD origin/main = `0fc6376` (S130 PERSIST) + S130 closeout commit pending；今日連環 push 8 commits chain (9122964→9f5c514→cd0c846→86f8c4f→930a8a8→c85d35c→b55435d→0fc6376)。§4a no trigger (324<400, 3 entries S128/S129/S130 within 30d)。下次起手＝問 Leonard 揀 stat_fact upgrade follow-up (build_stat_facts.py 4 builder rewrite + stat_facts.json rebuild + Supabase content_type=stat_fact replace path) / 5 HTML catalogue-level / Future batch-7 stale Vanilla-preserved / 既有 backlog (🔴 §E.10 / batch ranking polish) / §8b rule 2 automation tooling。

## Previous Session Record
1. UTC date: 2026-05-27
2. Session ID: Claude_20260527_0720 (Session 129 — batch-7 content refresh: 3 PDF marker-bearing re-page-carry)
3. Completed:
   - ✅ **[Inventory + PLAN HIGH-risk]** 14 S128-surfaced EDB-content-updated sources 分 3 類：A. PDF marker-bearing 3 (arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024) = HIGH ROI 北極星 trace、B. stat xlsx 4 = MEDIUM (xlsx 無頁結構天花板)、C. HTML index 5 = LOW (catalogue-level)。Leonard 揀 Scope A 推薦。
   - ✅ **[Gate 1+2 EXECUTE 3/3 OK]** Gate 1 markers==pages 全對 (arts 106/music 65/va 53)；Gate 2 EXECUTE = DELETE 310 INSERT 272 net -38；Supabase 9,920→**9,882**。
   - ✅ **[Live smoke 2/3 direct surface NEW page numbers]** music TOP-1+2 p=11/16 0.704/0.701 + va TOP-1+2 p=17/11 0.727/0.723；arts ranking competition non-regression (data live indexed 116 chunks confirmed)。
   - ✅ **[PERSIST + push]** commit `86f8c4f` (vault) + `930a8a8` (PERSIST) + `c85d35c` (closeout/archive) origin/main。§4a triggered: 481→195 lines, 5→2 entries (S127/S128 archived to dev/archive/SESSION_LOG_2026_Q2.md)。
4. Risks / blockers: driver 8th-validation across 55 sources 0 incident; arts ranking competition unchanged (broader backlog)。
5. **Session CLOSED 2026-05-27（Leonard「收工」）** — HEAD origin/main = `c85d35c`。 詳見 SESSION_LOG S129 entry。

## Previous Session Record
1. UTC date: 2026-05-27
2. Session ID: Claude_20260527_0720 (Session 128 — S126 follow-up trio closed: g28 URL drift fix + freshness persist + g29/g24 sanity check)
3. Completed:
   - ✅ **[Trio (c) g29/g24 size-spike sanity check — read-only finding]** Live HEAD probe verified：g24 `sag_c.pdf` 8.38MB Last-Mod 2026-05-20 真 PDF / g29 `KGECG-TC-2017.pdf` 12.48MB Last-Mod 2017-10-04 真 PDF。**Verdict = 非 EDB drift / 非 url_primary landing→PDF 切換 / 非 vault content stale**；現象係 **freshness baseline 本身一直 wrong**（baseline 寫 1.3KB/1.5KB Content-Length 屬於 fetch 拎到 landing redirect 嘅 HTML body 而非 PDF body）。g29 Last-Mod 反向至 2017-10 = baseline 從前拎錯 landing 嘅 date、PDF 本身真係 2017 原版。Vault content 對齊 EDB live PDF；無需 trigger batch-5 重 page-carry。g24 vs sag_2025_11 = 同一 SAG 文件兩個 PDF variant（clean `sag_c.pdf` vs markup `SAG_C_markup.pdf`）= PMS §E.7 既有問題、SOURCE_ALIASES 軟 dedup 處理中、unchanged。
   - ✅ **[Trio (a) g28 dead URL fix — §E.12 EDB URL drift pattern apply]** 舊 `https://www.edb.gov.hk/tc/edu-system/primary-secondary/applicable-to-primary-secondary/it-in-edu/Information-Security/information-security-in-school.html` HTTP 404 → 新 `https://www.edb.gov.hk/.../it-in-edu/information-security.html` HTTP 200 366KB live page；EDB 改版 = lowercase + 拍平 subdirectory（移走 `Information-Security/` 一層）。`source_registry.json` g28 entry `url_landing` + `url_primary` 同步 update（source_type=index、兩 field 同值）。commit `9122964` push origin/main。
   - ✅ **[Trio (b) freshness persist run — first successful write run since S126 fix]** `python3 dev/source/check_freshness.py`（write mode、無 --dry-run）= **Checked 147 / Changes 22 / Errors 0 / Threshold 7 / exit 0** ✅。S126 fix（AttributeError null-guard + threshold gate + summary 強化）end-to-end verified；script 無 crash on freshness_metadata=null entries。22 sources baseline updated 包：g28 post-fix 2173→22310 confirming 新 url 200 + g24 1525→8380019 reflecting actual PDF body + g29 baseline 自動 normalize（無 explicit "Old" diff print 因 baseline 部分 null first-write path）+ 12 sources EDB content updates (stat_kg/pri/sec/special / arts_* / ph_pri_curr / edbc197 / moral_civic / music_p1_s6_2024 / va_p1_s6_2024 / stat_edb_figures)。commit `9f5c514` push origin/main；diff +228/-216 lines。
   - ✅ **[PERSIST]** SESSION_HANDOFF Open Priorities regen（移除 S126 follow-up trio 因已完成、加新 #5 可能 future content refresh backlog）+ Last Session Record S128 + S127 demote → Previous + ✅ S128 完成 annotation；SESSION_LOG S128 entry prepend + DOC_SYNC matrix + Next Session Handoff Prompt verbatim。NO update needed：PROJECT_MASTER_SPEC（§E.12 pattern 已 codified、本 ops 應用係 second-instance evidence 但唔 trigger 新 codify、§G.2 第三次 ops 應用同 S126/S127 已 handle）/ CODEBASE_CONTEXT（無 stack/External Services/Key Decisions structural 改）。
4. Pending：
   - commit+push origin/main 指定 2 governance docs（SESSION_HANDOFF + SESSION_LOG）等 Leonard 排下一步。
   - Optional follow-up: 對 14 sources content-updated EDB live、re-fetch + re-extract vault txt + page-carry 同步落 Supabase（屬另一個 batch task、非北極星阻塞、Leonard 排）。
5. Next priorities (max 3)：
   - 等 Leonard 排：(a) Future batch-7 6 stale Vanilla-preserved re-evaluate；(b) S128 揭 14 sources content-updated EDB live → 對齊 vault + Supabase 重 page-carry task；(c) §8b rule 2 automation tooling；(d) 抑或 既有 backlog
   - 🔴 §E.10 admin-login client-side gate（OPEN）
   - batch ranking polish backlog ~15-17 sources（S122-S125c 累計）
6. Risks / blockers:
   - **§E.12 EDB URL drift pattern 第二次 ops 應用**（S121-S126 期間累積、S128 g28 first re-discovery + url repair）：EDB 站內可能仍有 同類 subdir-flatten / lowercase 改版未 caught；下次 freshness check 跑 weekly cron 會主動 surface 任何新 dead URL。
   - **freshness baseline 一直 stale issue surfaced**：147 sources × baseline 由初次 seed（2022/2025）累積、22 sources 需 update；今次首次 successful write run、未來 weekly cron 會持續 maintain baseline accuracy。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. Session 進行中（**非** closeout — Leonard 未表示「收工」）：S126 follow-up trio 全 3 sub-step 完成 + §3 PERSIST 完成；governance docs commit+push pending；視 Leonard 排下一步 / 收工。

## Previous Session Record
1. UTC date: 2026-05-27
2. Session ID: Claude_20260527_0720 (Session 127 — §8b 3-rule promotion + PROJECT_MASTER_SPEC governance doc full update)
3. Completed:
   - ✅ **[§1 起手 + verify PASS]** HEAD `0b5ecc4` (S126 closeout) origin/main working tree clean / knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` 對齊 baseline / Supabase 9,920 採信 S125c state（無 service_role key 獨立 introspect、§D.18 ritual 留必要時用）/ egress `/health` HTTP 200 (warm 4.2s after 30s cold-start retry, `cache_a.warm=true size=455`)。
   - ✅ **[Leonard 揀 "§8b 3-rule + governance update" → §3 HIGH-risk PLAN]** 4 files scope（PROJECT_MASTER_SPEC + CODEBASE_CONTEXT + SESSION_HANDOFF + SESSION_LOG）+ 7 §3d scenarios + Leonard scope sub-confirm「Promote (推薦)」rule 3 (§G.2 root-cause estimate)。
   - ✅ **[CHANGE 4-edit PROJECT_MASTER_SPEC.md]**: (1) §D.16 extend：加 batch-3/4/5/6 verified state（既有覆蓋至 batch-2） + **§8b rule 1** audit cross-check stale-superseded（S125b first applied / S125c Hybrid verified；cross-check 法 = registry `supersedes` + audit-tool 掃 stale 同舊 family）+ **§8b rule 2** semantic-supersede detection（registry `supersedes=[]` 都當潛在 supersede chain；audit sub-agent 加 KLA-title embedding similarity ≥0.85 check + same-prefix/naming-pattern detector + human verify before deprecate；automated tooling 留 future、本 rule 即時 process-level apply）。(2) NEW **§D.19** documenting `cb3_deprecate_stale.py`（159 lines / service_role REST DELETE / per-source verify count==0 / Phase backup audit log §5.a-compliant / `--skip-local` default / `--execute` gate / mirror cb3_b2 discipline / reversibility note：vault legacy & registry preserved → rebuild from vault txt 可復原 / Hybrid decision framework：superseder direct dominance + chunks count 細 + audit confirm + Leonard sign-off = DROP；其餘 = Vanilla preserve）。(3) §G.2 banner +4th drift instance = **§8b rule 3** codification（handoff root-cause estimate ≠ verified ground truth；S121 schema.sql / S122 commit-msg / S126 handoff hypothesis 三度 cross-session recurrence；rule = triage agent 必先 run + 觀察 actual failure trace 再 verify hypothesis 對唔對）。(4) §G.3 NEW #7（接手 issue 嘅 handoff 寫「root cause = X」當 hypothesis、never skip live-reproduce step）。
   - ✅ **[CHANGE CODEBASE_CONTEXT.md]**: Directory Map +`cb3_deprecate_stale.py` entry（DROP-only deprecation tool description）+ AI Maintenance Log +S127 entry（governance update 摘要）。
   - ✅ **[CHANGE SESSION_HANDOFF.md]**: Open Priorities regen（move S127 completion 進入 `> ✅ S127 完成` annotation、demote S126 → 加 codification cross-link、移除既 governance update #1 + #3 因已完成、保留 S126 follow-up trio + future batch-7 + 既有 deferred + Q4 deferred + 新 #5 future automation tooling）+ Last Session Record S127 + S126 demote → Previous Session Record。
   - ✅ **[QC §3d 7-scenario static verify PASS]** Normal #1-4 grep-verifiable assertions + Regression A-C scope discipline；無 code/data/Supabase mutation。
4. Pending：
   - commit+push origin/main 指定 4 檔（PROJECT_MASTER_SPEC.md + CODEBASE_CONTEXT.md + SESSION_HANDOFF.md + SESSION_LOG.md）+ closeout commit。
   - §8b rule 2 automation tooling future implementation（KLA-title embedding similarity check sub-agent prompt）。
5. Next priorities (max 3)：
   - S126 follow-up trio（g28 dead URL / freshness_metadata persist run / g29-g24 size-spike sanity check）
   - 🔴 §E.10 admin-login client-side gate (OPEN) / batch ranking polish backlog
   - Future batch-7 6 stale Vanilla-preserved case-by-case re-evaluate
6. Risks / blockers:
   - **本 session 純 governance/markdown 改、0 code/data/Supabase mutation**：無新增 risk；任何 rule misread / 反向 conflict 屬 §3b 整合風險、本 session 4 edit 全 additive、無 retire 舊條款。
   - 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
   - egress 間歇每次自測；EDB PDF 永遠用 `url_primary`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。
7. Session 進行中（**非** closeout — Leonard 未表示「收工」）：§8b 3-rule promote + governance doc full update 完成；commit+push pending；後續視 Leonard 排 S126 follow-up trio / 既有 backlog / closeout。

## Previous Session Record
1. UTC date: 2026-05-26
2. Session ID: Claude_20260526_1811 (Session 126 — Freshness workflow chronic-fail triage)
3. Completed:
   - ✅ **[PLAN HIGH-risk → Leonard 4-gate confirm via AskUserQuestion]** scope = bug fix + threshold + re-run dry-run；threshold = `errors > max(5, total_checked // 20)`；cron 保持 weekly Monday 09 UTC；freshness_metadata 唔寫返 registry 本 session。
   - ✅ **[READ → dry-run v1 揭真根因]** 跑 `python3 dev/source/check_freshness.py --dry-run` → entry ~22 撞 **`AttributeError: 'NoneType' object has no attribute 'get'` (line 101)**；root cause = `meta = src.get("freshness_metadata", {})` 對 explicit-null value 失效（`.get(...)` default `{}` 只 trigger on missing key、非 null value）。**Pre-crash 已揭 1 dead URL (g28) + 20 EDB CHANGE detected**。Handoff 估計 root cause = `errors > 0: sys.exit(1)` 係 partial truth — script 根本未跑到嗰行就 crash。§G.2 verify-don't-trust-docs **第三次 ops 應用**（S121 schema.sql / S122 commit-msg-vs-diff / S126 chronic-fail root-cause 全 3 度 recurrence-prone）。
   - ✅ **[CHANGE `dev/source/check_freshness.py` single-file]** (a) null-guard: `meta = src.get("freshness_metadata") or {}` (b) threshold gate: `threshold = max(5, total_checked // 20)`；`if errors > threshold: sys.exit(1)` + within-threshold exit 0 warn 訊息 (c) summary 加 failed-sids list (sid + url) 方便 GitHub Actions log artifact 分析。Syntax PASS via `ast.parse`；git scope = 1 file。
   - ✅ **[QC dry-run v2 + §3d matrix PASS]** Re-run cleanly：**Checked 147 / Changes 20 / Errors 1 (g28) / Threshold 7 / exit 0** ✅。§3d 5 scenarios: Normal flow / Boundary-low (1-7 err exit 0+warn live-verified) / Boundary-high (>7 err exit 1+🚨 code-review) / Regression A (`--dry-run` no write — `git diff source_registry.json` empty ✅) / Regression B (filter unchanged — 147 vs stale Regression Notes #2 baseline 145，+2 = vault growth since 2026-04-08 同 filter logic)。
   - ✅ **[20 EDB CHANGE detected + 1 dead URL 紀錄、唔 persist]** Changes 包：sag_2025_11 / g04 / g29 / g31 / g33 / g37 / g38 / g24 / stat_edb_figures / stat_kg / stat_pri / stat_sec / stat_special / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr / arts_kla_guide_2017 / music_p1_s6_2024 / va_p1_s6_2024。**Anomalies**：g29 Len 1299→12,481,467 (1.3KB→12MB) + g24 Len 1525→8,380,019 (1.5KB→8MB) 懷疑 url_primary 由 landing→直 PDF 切換；g29 Last-Mod 反向回到 2017-10 同樣異常（內容已換）。Dead URL: g28 information-security-in-school.html（§E.12 pattern follow-up）。
   - ✅ **[PERSIST]** SESSION_HANDOFF Regression Notes #2 stale-baseline 更新 / Open Priorities regen / `> ✅ S126 完成` annotation / 本 Last Session Record + S125 demote / SESSION_LOG S126 entry + DOC_SYNC matrix / commit+push 指定檔。
4. Pending：
   - g28 dead URL EDB re-discovery / url_primary 修（§E.12 pattern）
   - check_freshness 跑一次唔加 `--dry-run` persist 20 EDB freshness_metadata updates（會改 4113 行 data file、獨立 commit）
   - g29 / g24 size-spike content sanity check（懷疑 EDB url_primary 由 landing→PDF 切換、可能影響 vault PDF extraction）
5. Next priorities (max 3)：
   - 等 Leonard 排：§8b rule promotion / Future batch-7 / S126 follow-up trio (g28 + persist run + size-spike) / 其他 OP
   - 🔴 §E.10 admin-login client-side gate（OPEN）/ batch ranking polish backlog
   - PROJECT_MASTER_SPEC governance doc full update
6. Risks / blockers:
   - **§G.2 verify-don't-trust-docs 第三次 ops 應用 (recurrence-prone)** — S121 schema.sql vs live grants / S122 commit-msg vs diff / S126 chronic-fail-root-cause = 3 度；§8b promote-candidate（multi-occurrence、multi-agent collaboration prone、long-term doc-vs-reality drift）。
   - g29 / g24 size-spike 異常未驗 content（可能 EDB url_primary 由 landing→PDF 切換、vault extraction 需 verify、follow-up）。
   - g28 真係 EDB URL drift（§E.12 codified pattern follow-up）。
   - 既有 risks：🔴 §E.10；🔴 57014 transient；🔴 FAIL-A（record-only）；Q4 deferred；Stage-2 closed 勿復活；egress 每次自測；EDB PDF 永遠用 `url_primary`（§E.12）；路徑空格雙引號。
7. **Session CLOSED 2026-05-26 (Leonard「收工」)** — §4 closeout 完成；S126 Freshness workflow chronic-fail triage closed（script bug fix + threshold gate + 5/5 §3d PASS）+ §G.2 第三次 ops 應用 record-only + S126 follow-up trio 列 backlog。HEAD origin/main = `393afca` (S126 fix) + closeout commit pending。§4a trigger=True (471 行 > 400) apply 完成：4 entries→`dev/archive/SESSION_LOG_2026_Q2.md`，retain S126/S125 (192 行)。下次起手＝問 Leonard 揀 §8b 3-rule + governance update / S126 follow-up trio / Future batch-7 / 既有 backlog。

## Previous Session Record
1. UTC date: 2026-05-26
2. Session ID: Claude_20260526_0737 (Session 125 — batch-4 + batch-5 + batch-6 Hybrid 三批)
3. Completed:
   - ✅ **[Batch-4 完整 cycle 10 sources]** Gate 1 → Gate 2 EXECUTE 10/10 OK (DELETE 537 INSERT 417 net -120 / Supabase 10,253→10,133) + commit `e703910` push origin/main + smoke 4/10 surface。
   - ✅ **[Batch-5 完整 cycle 10 sources Vanilla strategy]** Gate 1 → Gate 2 (DELETE 752 INSERT 736 net -16, g24 +28% cap-recovery / Supabase 10,133→10,117) + commit `d66f091` push + smoke 5/10 surface (3 direct + 2 bonus)。
   - ✅ **[Batch-6 完整 cycle Hybrid strategy + NEW script]** Leonard `/goal go` full-flow auth → CHANGE step 0 repage_pdfs.py +2 batch-6 entries（size 53→55）+ NEW `dev/cb3_deprecate_stale.py` 159 lines（service_role REST DELETE + per-source verify count==0 + Phase backup audit log + --skip-local default + --execute gate；Python 3.9 PEP 604 compat fix）→ Gate 1 page-carry --write 2/2 PASS（g15 3 markers / edbcm98 6 markers / backup `dev/init_backup/20260526_135854_UTC/`）→ Gate 2 page-carry EXECUTE 2/2 OK（DELETE 11 INSERT 9 net -2 / wiki_index auto-backup `dev/init_backup/20260526_140052_UTC/`）→ Deprecation EXECUTE 2/2 OK（pe_sss_2007_2015 del_status=204 pre=119 post=0 / sci_jss_supp_2017 del_status=204 pre=76 post=0；audit log `dev/init_backup/20260526_140059_UTC/cb3_deprecation_log.json` 寫低 reversibility note）→ Total batch-6 ops: DELETE 206 INSERT 9 net **-197** / Supabase 10,117→**9,920**。
   - ✅ **[QC post-execute (across 3 batches)]** Supabase totals via Range header exact match prediction at each step (10,253→10,133→10,117→**9,920**) / INVARIANT spot-check 0 touched non-batch sources (incl Vanilla-preserved 6 stale va/ethics/music/econ_2007/econ_supp_2015/bafs untouched) / backend `/health` ok / raw REST inspect chunk text `=== Page N ===` markers verified live / NEW deprecation audit log written with reversibility note。
   - ✅ **[Live smoke across 3 batches]** Batch-4 4/10 direct surface + 6/10 ranking competition non-regression。Batch-5 5/10 surface (3 direct + 2 cross-query bonus)。Batch-6 deprecation ranking improvement verified：sci_jss_framework_2025 TOP-1+#2 p=29/27 0.540/0.514 post-deprecation；pe_sss_2007_2015 完全 cleared from pe-related queries (cleanup verified)；g15/edbcm98 indexed (now=3/now=6) but small + KLA dominate so don't surface (acceptable)。Live smoke parser self-fix（API field `page` 非 `page_number`）。
   - ✅ **[Mid-session Freshness workflow chronic-fail triage (read-only)]** `.github/workflows/freshness_check.yml` 5 連 fail since 2026-04-30，root cause `check_freshness.py:141-142 if errors > 0: sys.exit(1)` + EDB intermittent + 15s timeout；非 batch 觸發；Regression #2 stale baseline 確認；列下次 priority。
   - ✅ **[§8b 2 lessons surfaced + first live applied (S125b/S125c)]** (1) Audit cross-check stale-superseded：揭 8 stale (1,010 chunks)，Hybrid 揀 DROP 2 (pe_2007 + sci_jss_supp = 195 chunks)、Vanilla preserve 6 (815 chunks) → deprecation ranking improvement live-verified。(2) NEW semantic-supersede lesson：g24 vs sag_2025_11 registry `supersedes=[]` but semantically equivalent (recurrence-prone S122 tech_kla / S123 music 同 pattern) → audit agent 加 KLA-title embedding similarity check (promote candidate)。
   - ✅ **[NEW deprecation script `cb3_deprecate_stale.py` first-use 0 incident (S125c)]** 159 lines、service_role REST DELETE + per-source verify count==0 + Phase backup audit log（reversibility note：vault legacy & registry 不刪 → 可 rebuild 復原）+ --skip-local + --execute gate；Python 3.9 PEP 604 compat fix。Mirror cb3_b2 discipline。
   - ✅ **[PERSIST]** SESSION_LOG S125 三 cycle entries（main + batch-5 + batch-6 sub-blocks + DOC_SYNC matrix + verbatim handoff rewrite covering 三批）；SESSION_HANDOFF baseline #1/#3 + Open Priorities regen + 本 record；CODEBASE_CONTEXT +S125 entries；HANDOFF_PACKAGE §2 chunks 9,920。
4. Pending：
   - **Freshness workflow triage**（chronic fail、低 blast radius、ops noise）。
   - **§8b 2-rule promotion + PROJECT_MASTER_SPEC governance doc full update**：codify §D.16 batch-4/5/6 verified + 2 new rules（audit cross-check + semantic-supersede）+ NEW `cb3_deprecate_stale.py` documented。
   - **Future batch-7 (optional)**：6 stale Vanilla-preserved sources case-by-case re-evaluate（815 chunks 仲 in index）；非急。
5. Next priorities (max 3)：
   - **Freshness workflow triage**（chronic ops cleanup）
   - **§8b 2-rule codify + governance doc full update**
   - 🔴 §E.10 admin-login client-side gate（OPEN）/ batch ranking polish backlog
6. Risks / blockers:
   - **§E.14 driver reuse 6th-validation**：52 sources page-carry + 2 deprecation = 54 ops 0 incident；pipeline production-ready confirmed + NEW deprecation script 0 incident first-use。
   - **Monitor agent prediction 模型 update need**：cap-recovery 唔可以淨睇 era predict、large-page docs 都有 risk（S122 eng_lit +111% / S123 eng_sss +40% / S125b g24 +28% 三度印證）。
   - **Freshness workflow chronic fail (NEW S125)**：低 blast radius；triage 列 priority #1。
   - **CB-3 達 final ceiling ~88%**：94/113 marker-bearing + 2 deprecated + 6 Vanilla-preserved stale（future batch-7 待評估）+ 9 結構天花板 = 北極星目標達成。
   - local `wiki_index.json` vs Supabase 94 源 diverge（S125 後 72→94；Supabase query-authoritative；reconcile 低優先 backlog）。
   - 既有 risks：🔴 §E.10；🔴 57014 transient（S125 ict_sss_2021 + g24 + pe_sss_2023 各 1 次 retry 恢復）；🔴 FAIL-A（record-only）；Q4 deferred；Stage-2 closed 勿復活；egress 每次自測；EDB PDF 永遠用 `url_primary`（§E.12）；路徑空格雙引號。
7. **Session CLOSED 2026-05-26（Leonard「收工」）** — S125 三批一日打完（batch-4 / batch-5 / batch-6 Hybrid，共 22 sources page-carry + 2 deprecation）+ Supabase 10,253→9,920 + CB-3 final ceiling ~88% 達成 + 94/113 sources marker-bearing + freshness chronic-fail triaged + 2 §8b lessons surfaced (audit cross-check stale-superseded + NEW semantic-supersede detection) + NEW `dev/cb3_deprecate_stale.py` (159 lines) 0 incident first-use + driver `cb3_b2_pagecarry_migrate.py` 6th-validation 52 sources 0 incident + live smoke deprecation ranking improvement verified (sci_jss_framework_2025 TOP-1+#2 post-deprecation；pe_2007_2015 cleared)。HEAD chain origin/main = `e703910` (batch-4) → `d66f091` (batch-5) → `ad34fd7` (batch-6) + closeout commit pending。§4a trigger=False (388 行 < 400、5 entries、oldest within 30d)。下次起手＝Freshness workflow triage / §8b 2-rule codify + governance update / 既有 backlog（Leonard 揀）。

## Previous Session Record
1. UTC date: 2026-05-25
2. Session ID: Claude_20260525_1334 (Session 124)
3. Completed: ✅ CB-3 Option C broader batch-3 生產 live（10 sources DELETE 942 INSERT 795 Supabase 10,400→10,253 / 7/10 smoke PASS / 3 non-regression）+ batch-4 pre-flight 完成（10/10 GO / 10/10 KEEP）。
4. HEAD `2b58ee3` (S124 main) + `399de95` (closeout) origin/main。Session CLOSED 2026-05-25。

## Previous-Previous Session Record
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
