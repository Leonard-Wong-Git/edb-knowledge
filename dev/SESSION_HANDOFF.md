# Session Handoff

## Current Baseline
1. **Version / git**: v2.3.0（knowledge 凍結 @2.3.0、guidelines @2.5.0，無 bump）；git `main`=`origin/main` HEAD = **`46376f4`（S154 IMC/SBM 校董會治理入庫 +229，疊喺 文件分析 `d17c25d` 上）→ governance closeout commit**；起手自行 verify HEAD==origin/main + Supabase **14,505**。
2. **Frontend**: `index.html` landing；**`app.html` = Channel-B-only 唯讀 SPA（S151：admin 登入閘 + 知識提煉/知識管理 tab + CRUD/匯出/候選審核 全移除；淨 3 tab〔平台介紹/政策搜尋/指引文件〕+ 文件預覽抽屜；app.html 4100→2935 行 −1176）**；`t-purchase.html` draft flow（dormant）；`q.html` local knowledge.json Quick Q&A（dormant）。**S153：政策搜尋（Channel B）合成分析放長 ≤120→約250字（上限300 soft；live ~328）+ 來源頁碼喺結果顯示並可點跳去 PDF 第 N 頁。⚠️ app.html 有兩個搜尋 UI：React desktop `QAPanel`/`SourcesAccordion` + 手寫 mobile shell `mobile.js`（平板用）— 兩個 surface 都改咗；mobile 來源名亦改全中文(`displayName`) + 去走「原文·分數」badge。** **S154：+📄文件分析（第 4 個 tab，desktop React surface）— 用戶上載 PDF/docx 或貼文字 → client-side 抽取（pdf.js 3.11.174 + mammoth 1.6.0 CDN；原始檔永不上載）→ `POST /api/analyze-document` 逐段比對指引 → 逐段報告（指引 `url#page=N` link + LLM 一句提示 best-effort + 私隱提示 + 60k 字/12 段 cap）。mobile.js shell 未做（Phase 1.5）；Phase 2 目標 = 可下載標註文件。** **S154(3)：全 4 個公開 HTML（index/app/q/t-purchase）裝咗 Cloudflare Web Analytics 免 cookie beacon（`</body>` 前一行 defer script；token 係公開 client-side 識別碼非 secret）+ index/app footer 私隱細字「本站採用免 Cookie 匿名流量統計」。報表喺 Leonard Cloudflare dashboard → Web Analytics。架構：前端由零對外 runtime 服務 → +1（已入 CODEBASE External Services）。**
3. **Knowledge state**: **455** Channel A facts（三層同步 byte-identical，md5 `720f5f`）、0 queue；Supabase **13,667** chunks（S148 13,473 → **S149 安全指引 +115**〔g18 校車+9 / g21 視藝+48 / g22 科技+58，文字層〕 → **S150 gifted +94**〔gifted_policy_docs +19 / gifted_tp_resource_kit +41 / gifted_osalp_compendium +19〕）；**新增 2 條 dedicated route**：`safety`(+keyword 校車/視藝安全/科技安全)、`gifted`(+keyword 資優/資賦)；指引（161 app / 152 公開 / **205** registry）；**display sync EXECUTED**（`_meta.stats` chunks→**13,667** 三層 byte-identical + app.html + K1_API_SPEC + README；guidelines 152 不變、無 bump、facts 455 不變）；Phase 3 全完成。**S151：app.html admin UI（知識提煉/知識管理/登入/CRUD/匯出）全移除 → 公眾完全 Channel-B-only；以上知識數字、role_facts/knowledge.json/guidelines.json 凍結資料與對外契約零接觸（admin 只係 client-side localStorage、無真實寫能力）。** **S152（2026-06-09）：Discovery 全量 triage（54 頁/400 候選）+ B-group 16 sibling-dup 全覆蓋確認（缺口清空）;入庫 7 個新發現源 +609 → Supabase **14,276**（三層 _meta.stats md5 720f5f→`4c3631` byte-identical）、registry 205→**212**;新源：`kgecg_2017`（幼稚園教育課程指引2017，補平台一直缺嘅 KG 課程）/`gifted_ge_series`/`cgss_2024`/`sch_calendar_guide`/`sch_activities_guide`/`k1_admission_2627`/`kg_admin_guide`，各加 SOURCE_SET route（curriculum/gifted/sen/hr_admin/activity/kg_admission）+ 2 keyword;display sync 7 處 14,276（facts 455/guidelines 152 不變、無 bump）。routed smoke 6/7 surface 帶頁;`cgss_2024` in-route 但 rank 低 top-8（monitor）。** **S154（2026-06-10）：IMC/SBM 校董會治理入庫 +229 → Supabase **14,505**（三層 _meta.stats md5 4c3631→`1bf7fd` byte-identical）、registry 212→**216**;4 新源（sbm.edb.gov.hk references，全文字層 page-resolvable）：`imc_establishment_operation`(成立與運作手冊2014, 97ch) / `imc_briefing_qa`(簡介會問答2013, 48ch) / `imc_governance_supplements`(Ch5/角色責任/會議/法例提醒/良好管治/行為守則 6PDF, 27ch) / `imc_election_guides`(家長/教師/校友選舉+委任五步曲 4PDF, 57ch);**新 `school_governance` route（擺 finance 前 — finance 佔 `法團校董` token 為 g02，唔擺前則校董會查詢全 route 去 finance、治理本體永不 surface；SOURCE_SET 連 g02+coa_imc_1_19+sdp_guide）**;display sync 7 處 14,505（facts 455/guidelines 152 不變、無 bump）。routed smoke 4/4 surface 帶正確頁碼、採購/招標 留 finance（唔被偷）。monitor：code-of-aid-IMC + sch-admin-guide 兩 index 頁已在 discover watch-list（Leonard 要求 Monitor — 已 cover）。**
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
> 產品方向：**全棧 Channel-B-only**（S151 admin 全移除；Phase 3 全完成；Stage-2 closed）。Channel A frozen @455（資料仍餵對外契約）。**Q4 Phase 2 全鏈完成**。S153 政策搜尋 UX 已 ship。**S154：📄文件分析新功能已 ship（desktop React 第 4 tab + `POST /api/analyze-document`）+ IMC/SBM 校董會治理入庫 +229（Supabase 14,505、新 school_governance route、registry 216）。** 主線 **0 outstanding bug**；以下全屬可選、冇緊急。

1. **Channel B 補入庫 — 完成 + Discovery 增量（S152）**：B-group 16 sibling-dup **全覆蓋確認**（同現行主 PDF 在庫、url-match 決定性）；Discovery 全量 triage 跑咗（54頁/400候選）→ 揀出真‧新候選 **全做入庫 7 源 +609 → Supabase 14,276**（`kgecg_2017` 補 KG 課程缺口 / gifted_ge_series / cgss_2024 / sch_calendar_guide / sch_activities_guide / k1_admission_2627 / kg_admin_guide）。**現行主指引內容缺口清空。** 餘 ~390 discovery candidates 已 triage = noise/old-version/語言變體/已覆蓋，無再入。新源入庫流程：fetch_extract/ocr_extract → ingest_one_source → SOURCE_SETS allowlist〔S135〕+ registry entry → **display 7 處**（3 層 _meta.stats + app.html + index.html + K1_API_SPEC + README）→ routed smoke。
2. **自動發現 + freshness 週跑（detection-only）**：`discover_sources.py`（每週一 10:00 UTC，**已跑過全量 S152**）續 diff 未登記新文件；freshness（每週一 09:00）監察已登記源改版/死链。下次只睇新 diff。
3. **文件分析 Phase 1.5 / Phase 2（可選 next）**：Phase 1.5 = mobile.js 平板 shell 加文件分析入口；Phase 2 = 可下載標註文件（PDF/Word 旁註輸出）。另 S154 monitor：LLM 一句提示 best-effort（e2e 3 段有 2 段有 note；缺 note 唔影響 matches）/ per-segment「檢索失敗請重試」喺 Supabase unconfigured 時措辭誤導（prod 唔會發生）/ Azure OpenAI fallback 路徑已查明（llmClient+embeddingClient 兩檔 swap，HK 帳號層風險用）。
4. **S154 IMC 治理 monitor**：grouped 源（`imc_governance_supplements` 6PDF / `imc_election_guides` 4PDF）連續頁碼 → `url#page=N` 只對第一份 PDF 準、appended 文件 overshoot（S152 grouped 先例；兩份大文件 establishment_operation/briefing_qa 獨立=頁碼全對）。`gov_admin`+`finance` 嘅 `法團校董` token 被 school_governance shadow 變 dead（無害，可清；對抗覆核確認）。
5. **既有 deferred / monitor-only**：`cgss_2024` routed rank 低 top-8 / gifted+CPD precedence / gifted_osalp catalogue 排名低 / phys_sss routed-UI（Leonard 接受）/ §8b rule 2 / Suppl_guide held / §E.10(a) CLOSED-BY-REMOVAL / FAIL-A record-only / 57014 cold-start / `stats.sources`=120 cosmetic-stale（live ~216）/ S153 synthesis live ~328 字略過 300 soft cap。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）

## Last Session Record
1. UTC date: 2026-06-10
2. Session ID: Claude_20260610_0100 (S154)
3. Completed:
   - ✅ **[起手核實 全 live]** HEAD `8bf828d`==origin/main clean / facts 455 三層(md5 4c3631) / Supabase 14,276(content-range 0-999/14276) / guidelines 152 / knowledge.json stats 14,276·152 / onrender /health 200 + manifest 401。
   - ✅ **[NEW 文件分析 — scope]** Leonard 揀「新功能」並定義：用戶上載學校文件 → 系統加上相關指引資料 → 輸回上傳者。AskUserQuestion 釘實：格式 PDF(文字層)/docx/貼文字（無 OCR）；Phase 1 螢幕報告、Phase 2 目標可下載標註文件；私隱 = hybrid（client 抽取、原始檔不上載；文字→server→OpenAI、stateless、可見私隱提示）。**OpenAI 香港封鎖疑慮已核實**：用戶唔受影響（egress = Render 美國 IP；只 browser-direct / HK-hosted backend 先中招）；Azure OpenAI = 有界 fallback（llmClient+embeddingClient swap）。
   - ✅ **[Backend]** NEW `analyzeDocument.ts`（分段：空行段落 + <30 字 stub 前併 + >1,200 字句界切；每段經 `searchChannelB` 公開 API synthesize:false top_k=4 併發 4 — **shared 檢索 infra 零修改**；一次 LLM 提示 call "N: …" best-effort；60k 字/12 段 cap；stateless）。`server.ts` 新 route 喺 10/min limiter 後 + `readJsonBody` optional `maxBytes`（淨新 route 用 ~244KB cap→413；**QC 捉到並修咗 RST-before-413 bug**〔drain 唔好 destroy〕；現有 route byte-identical）。
   - ✅ **[Frontend app.html]** +pdf.js 3.11.174 / mammoth 1.6.0 CDN（**3.x UMD 特登 — 4.x ESM-only 唔啱 no-build 頁**；URL curl-200 驗證）；`AnalyzePanel`（檔案/貼文字、runtime 庫 guard、私隱提示、逐段報告卡 `url#page=N` + noopener noreferrer + **https-only href allowlist**〔對抗覆核 flag 修正〕）；VALID_VIEWS/tab/router +'analyze'。**mobile.js 零接觸**（平板 shell = Phase 1.5）。
   - ✅ **[QC 文件分析]** typecheck+build exit 0；unit smoke segmentText/parseNotes（**MIN_SEGMENT_CHARS 60→30**：中文通告段落 40–80 字要企得住獨立段）；**local live e2e**（:8123 真 Supabase+OpenAI）：3 段樣本通告 → 遊學團→`sch_activities_guide` p91 / 採購→`g01` p7 / 校車→`g18` p2-3 全帶頁、9.7s warm；錯誤路徑 400 空/400 過長/413 oversize；現有 channel-b endpoint 零回歸；semantic regression PASS=9+notes=1+**既知 2 FAIL 0 新增**；browser-verify（preview fetch-stub）10/10（頁碼 link/無分數/fail-visible/4 tab 回歸/真 pdf.js worker 頁內抽取）；**對抗覆核 subagent VERDICT PASS-with-flags 0 critical**（flag 1 href allowlist 已修 + 重驗 `javascript:` URL 降純文字；flags 2-6 non-blocking 記錄於 SESSION_LOG）。
   - ✅ **[NEW IMC/SBM 校董會治理入庫 +229]** Leonard：「指引欠校董會治理本體」+ 5 條 sbm.edb.gov.hk URL（3 加入 / 2 Monitor）。Crawl references 子頁 enumerate → pre-flight 12 PDF 全 TEXT-OK（U+FFFD=0、page-resolvable）→ **4 源拆法**（兩份大文件獨立=頁碼全對，兩組細 fragment 分組；避免 grouped 連續頁碼 overshoot）→ live ingest Supabase 14,276→**14,505**（97+48+27+57）。**新 `school_governance` route 擺 finance 前**（SOURCE_SET 連 g02+coa_imc_1_19+sdp_guide）；registry 212→216；display sync 7 處 14,505（三層 md5 4c3631→`1bf7fd` byte-identical、facts 455/guidelines 152 不變、無 bump）。**2 個 Monitor index 頁已在 discover watch-list（coa_imc_1_19 + sag/g24 url_landing）— 已 cover、無需改動。** QC：typecheck/build PASS、routed smoke 4/4 治理查詢 surface 帶正確頁碼 + 採購/招標 留 finance（唔被偷）、regression 0 新 FAIL、對抗覆核 PASS-with-flags 0 critical（12-query regex trace 確認零誤偷）、post-deploy onrender 治理 synthesis 373 字 + policychecker.wongfu.net 顯示 14,505。
   - ✅ **[Cloudflare 統計]** Leonard 畀 token → 4 公開 HTML（index/app/q/t-purchase）裝 cookieless beacon + index/app footer 私隱細字；Playbook analytics-minors-cookieless 卡（私隱優先、唔用 GA4）；§0b 核實官方 setup/limits + beacon URL curl-200；browser-verify **執行級**（app+index 都見 RUM POST 去 cloudflareinsights.com/cdn-cgi/rum）+ 0 console error；External Services block 記錄「+1 對外 runtime 服務」架構轉變。報表：Cloudflare dashboard → Web Analytics。
   - ✅ **[通告分析入口暫停]** Leonard：「button 保留、link 失效」→ index.html「進入 EDB 通告分析系統」button → 停用 `<span>`（暫停開放字樣 + opacity .55 + not-allowed；原 `<a>` 連 URL 留 comment 恢復用）；app.html intro 卡 `externalLink` comment 掉（本身係 dead data — channels.map 從未 render 過佢）。驗證：兩 surface 零活鏈、卡片照 render、0 console error。註：原 link 其實 301→circular.wongfu.net 200（非 404）— 照指示停用、下游點解唔深究（§A.3）。
4. Pending: 文件分析 Phase 1.5（mobile shell）/ Phase 2（可下載標註文件）；IMC grouped-源頁碼 overshoot = monitor（見 Open Priorities #4）。**0 outstanding bug。**
5. Next priorities: 見 Open Priorities。
6. Risks / blockers:
   - 🟢 **0 outstanding bug**。
   - ⚠️ **文件分析私隱姿態**：原始檔永不上載，但抽取文字會經 server→OpenAI（stateless、有可見提示）。任何改動呢個 data flow 必須同步改 UI 私隱文案。
   - ⚠️ **LLM 逐段提示 = best-effort**（e2e 3 段得 2 段有 note；缺 note 唔影響 matches 核心交付）= monitor。
   - ⚠️ app.html 兩個搜尋 UI（React desktop + mobile.js shell）：政策搜尋結果渲染改動必須兩邊都改；**文件分析目前淨 desktop React**（mobile shell 未有入口 = 已知 scope，非 bug）。
   - 既有：synthesis ~328 字 soft cap / cgss_2024 rank 低 / admin 永久移除（重建走 §3+真 server-auth）/ Channel A frozen @455 / 入庫 display sync 7 處 / 新源必加 SOURCE_SETS+registry / 57014 cold-start / Stage-2 closed / 路徑空格雙引號 / commit 必入 SESSION_LOG / 勿改 canonical chunker / stats.sources=120 cosmetic-stale。
7. commits: `a6547c6`(文件分析 code) → `d17c25d`(文件分析 governance) → `46376f4`(IMC 治理入庫) → `60da7f0`(IMC governance) → `37995bc`(Cloudflare beacon ×4) → `0c34611`(通告分析入口停用) → governance commit（本次）。

## Previous Session Record
1. UTC date: 2026-06-09
2. Session ID: Claude_20260609_1230 (S153)
3. Completed: Channel B 政策搜尋 UX — SYNTHESIS_PROMPT ≤120→約250字(上限300 soft；live ~328) + 來源頁碼顯示/可點 `url#page=N` 跳頁 + 去分數（desktop `QAPanel`/`SourcesAccordion` + mobile.js 兩 surface 都改；mobile 來源名全中文 displayName + 去「原文·分數」badge）。QC：typecheck/build/node-check PASS、regression 0 新 FAIL、雙 surface live browser-verify、post-deploy synthesis 328 字。0 change Channel A facts/schema/RPC/下游/canonical chunker、無 bump。
4. commits: `6b91d8d`(code) → `9db6042`(governance) → `8bf828d`(START regen)。


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
