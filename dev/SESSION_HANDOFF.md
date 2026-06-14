# Session Handoff

## Current Baseline
1. **Version / git**: v2.3.0（knowledge 凍結 @2.3.0、guidelines @2.5.0，無 bump）；git **`main` HEAD == `origin/main`（已 push）**；Supabase **15,109**（S160 #2 KG 入庫 +435，S161 未動）。起手 verify HEAD==origin/main + Supabase 15,109。**S161（2026-06-14，全權自主）：「文件標註」合併主線 Phase 1 SHIPPED LIVE — 合併 文件分析+文件修訂 → 一個「📝 文件標註」tab：上載 .docx → 比對 EDB 指引 + 合規清單 gap → **原檔就地標註**（保留格式 + 螢光 highlight + 就地可見內聯建議（💡指引／⚠修訂）+ 未能定位項入文末附錄）→ 下載。新 `backend/src/api/annotateDocument.ts`（重用 analyzeDocument 指引比對 + checklistRevise 清單 gap，零改兩模組）+ `/api/annotate-document` route（10/min+413 cap）；`checklistRevise.ts` 加 `detectRelevantDomains`（auto-detect 涉及範疇）；`app.html` 加 `AnnotatePanel` + `buildAnnotatedOriginalDocx`（JSZip 操作原 docx XML）+ JSZip 3.10.1 CDN；舊 `#analyze`/`#review` hash → redirect `#annotate`。commits `6885dbe`(feature)→`0e71802`(gov)→`1aafeda`(反饋1:可見內聯建議+公開名)→`a1bc18f`(反饋2:校類filter對比+隱藏內部清單+標註文件header)→`745b02f`(反饋3:建議條文用 Word 追蹤修訂 w:ins，接受即套用) 全 push。live e2e onrender PASS（safety doc → 3 guideline〔Supabase live〕+24 partial+50 missing、auto-detect 學校安全+學生支援、0 truncated）。**Leonard 真檔（數學 docx）試用 2 輪反饋已即修 live**：(1)隱形 Word 批註→可見內聯建議、內部名→公開名；(2)政策範本隱藏「文件要求清單」(內部對照用)、修 `.filter-tab` 喺淺底白字隱形（加 `.filter-tab-light`）、標註文件加頂部 header（平台/校類/範疇/圖例）+ guideline framing「參考」+ checklist 可編輯「✎ 建議條文」。⚠️ 舊 `AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 變 dead code（已無 tab/render 引用，但保留——`REVISE_SCHOOL_OPTS`/`REVISE_STATUS_META`/`REVISE_BACKEND_URL` 仍被新 panel 用；cleanup 列 follow-up）。****S160（2026-06-14，通宵自主 + Leonard supervised）：(A) 政策範本下載 tab + 文件修訂 feature（`/api/checklist-revise`）LIVE deployed（live e2e PASS：14 域/真實報告/CORS）。(B) #2 幼稚園 Phase 2 KG LIVE 入庫（Leonard sign-off）：`kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks** → Supabase 14,674→**15,109**；新 `kg_admin` route（searchChannelB.ts，擺 curriculum 前；routed smoke 命中新源 p1/p78、收生無回歸）；display-sync ×7（→15,109）；registry 216→**218**。commits `fcccc34`(P2)→`bd99b91`(P3)→`1bf497c`(KG)+gov，全 push（Render KG 路由 deploy propagating）。****S159（2026-06-13）：(1) #3 學校版分校類 mass-gen — 13 域 per-type(小/中/特) docx 102 份入 `dev/checklists/<域>/`；修全 14 域學校版 docx「undefined」章節 bug；13 域 348 校類 carve-outs（school_types field）；Leonard 科目→校類 ruling 已套。(2) #4 文件分析 Phase 2 SHIPPED LIVE — 標註版 docx 下載 + 校類選擇器（analyzeDocument.ts/app.html，onrender e2e PASS）。(3) #2 KG 入庫 prep — 2 核心源抽取完成（435 chunks 待 INSERT，dev/vault/，live 入庫留下個 session）。Supabase 14,674 未動。****S157：checklist QC 全清（128 verify_issues、0 pending）。S158（2026-06-13）：(1) `ph_pri_guide_2025` 完整重抽入 Supabase 146→315 chunk（舊抽取封頂 80/262 頁、缺 ch3-6 正文；DELETE 146 舊 + INSERT 315 新）→ 總 14,505→**14,674**、公開 Channel B 搜尋實測命中 ch5/ch6；(2) curriculum 人文科 8/9 verify-issue 引用由 EDB 通告 re-anchor 去真指引 `ph_pri_guide_2025` 真物理頁（p8/11/19/123/127/192/196/245；idx7 培訓 刪），2 份 curriculum docx 重生；(3) 刪 人文科 idx7 + 科學科 4 條 30hr/15hr 培訓證書 items（行政公布非校本政策要求）；(4) display sync 14,505→14,674 × 7 處。**
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
> 產品方向：**全棧 Channel-B-only**。Channel A frozen @455。**S161：「文件標註」合併主線 Phase 1 SHIPPED LIVE（取代 文件分析+文件修訂 兩 tab；原檔就地 highlight+Word批註+附錄）。S160：政策範本下載 + #2 幼稚園 KG 入庫 LIVE（Supabase 15,109）。HEAD==origin/main。** 主線 0 outstanding bug。

1. **文件標註相關性收緊 — Leonard 揀 A，已實施 LIVE（`9b1f6a5`）**：auto-detect 改揀**單一最相關範疇**（was 2）+ 門檻 0.30→0.38（`detectRelevantDomains`）+ auto 模式 missing cap 8（was 25）。實證：小學數學課程 doc auto-detect 只出 `curriculum` 課程管理、**零 SEN/跨範疇**。⚠ 殘留：無 `school_types` tag 嘅 clause（如幼稚園課程指引衍生）即使揀咗小學仍可能漏出（okType 對 untagged clause 一律放行）= 跨校類小殘留，要更好 clause school-type tagging / source-aware filter 至徹底（monitor，未做）。explicit 自選範疇模式照出 full completeness（missing cap 25）。
2. **文件標註 Phase 2 / 2.5**：Phase 2 = PDF inline highlight（pdf-lib + pdf.js 座標，難）；Phase 2.5 = per-segment `detectQueryCategory` 自動偵測範疇取代手動 multi-select。重點睇真實 docx 段落↔XML mapping 命中率（v1 段落級 highlight）。
2. **dead code cleanup（S161 遺留）**：`AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 已無 tab/render 引用變 dead；刪時要保留 `REVISE_SCHOOL_OPTS`/`REVISE_STATUS_META`/`REVISE_BACKEND_URL`（新 AnnotatePanel 仍用）+ `ANALYZE_SCHOOL_LABELS` 視乎。低風險獨立小任務。
3. **#2 KG 收尾 — 幼稚園清單 pilot DONE（S162，待 push/部署）**：新範疇 `kg_operation`（幼稚園營運，388 items/162 clauses/20 章；源 kg_operation_manual_2026+kg_admin_guide_2026）行勻 14-域 pipeline → 15 域；4 docx 入「範本下載」（+幼稚園 filter）。**剩**：(a) Leonard review 17 覆核 issues（`dev/checklists/kg_operation/QC_VERIFY_ISSUES.md`，16 軟性 fabricated/distorted 未修，已修法團校董會→校董會）；(b) 部署後 live 驗範本下載見幼稚園卡。
4. **#3 學校版分校類 — 待 Leonard review docx（monitor，live）**：102 docx 由「政策範本」tab 下載。改格式/分流 → 調生成器/tags（改 tags 跑 `apply_school_types.py --check`；改 docx re-run 兩 generator 再 push）。
5. **既有 monitor + follow-up**：`kg_admin`「幼稚園質素」→qa_inspection（minor）/ 文件修訂門檻 COVERED=0.50/PARTIAL=0.42 tunable / IMC 頁碼 / cgss rank 低 / 57014 free-tier / stats.sources=120 cosmetic / Azure fallback / 週跑。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）

## Last Session Record
1. UTC date: 2026-06-14
2. Session ID: Claude_20260614_S161 (S161) — 全權自主（Leonard：「一次過做哂，包括幼稚園及 UI；全權去做不用問」）
3. Completed（詳見 SESSION_LOG S161）:
   - ✅ **起手核實全綠**：HEAD `c37165e`==origin/main；Supabase **15,109**（live knowledge.json）；`kg_admin` route 探針 live（「學前機構辦學手冊」top=`kg_operation_manual_2026`，S160 Render stuck 已自解）。
   - ✅ **「文件標註」合併主線 Phase 1 SHIPPED LIVE**（`6885dbe`）：合併 文件分析+文件修訂 → 一個「📝 文件標註」tab。新 `backend/src/api/annotateDocument.ts`（重用 analyzeDocument 指引比對 + checklistRevise 清單 gap 合成 `findings[]`、零改兩模組）+ `/api/annotate-document`（10/min+413）；`checklistRevise.ts` +`detectRelevantDomains`（auto-detect，domain 描述子 embedding 相似度 cap 2）；`app.html` +`AnnotatePanel`（校類 single + 範疇 multi-select/自動 + 上載/貼）+`buildAnnotatedOriginalDocx`（JSZip：命中段落級 highlight + **就地可見內聯建議段**〔💡指引／⚠修訂；棄隱形 Word 批註，Leonard 試用反饋〕+ 未定位項入附錄）+`buildAnnotateListDocx`（貼文字/PDF fallback）+ JSZip 3.10.1 CDN；舊 `#analyze`/`#review`→`#annotate` redirect。
   - ✅ **v1 取捨 + bug fix**：段落級 highlight（非逐字 run-split，寧 over-annotate）；normalized 容錯匹配；partial cap 12/域、missing cap 25/域、總 120（防低門檻過量 partial 淹沒 missing）；**修 python-docx 自帶 self-closed `<w:comments/>` stub → 原 replace no-op → dangling refs → Word repair** 嘅 bug。
4. Pending: 文件標註 Phase 2（PDF inline）/ Phase 2.5（per-segment auto-detect）；dead code cleanup（AnalyzePanel/ReviewPanel）；#2 幼稚園清單 pilot；#3 docx review。等 Leonard 試用 Phase 1。
5. Next priorities: 見 Open Priorities（Leonard 試用反饋 → Phase 2/2.5 → cleanup → KG pilot）。
6. Risks: 🟢 HEAD==origin/main（已 push）。⚠️ docx 就地標註 = 段落級 + 容錯匹配，碎 run/表格多嘅真實檔命中率待 Leonard 真檔試用驗（v1 設計：寧入附錄唔錯位）。⚠️ 就地標註只支援 .docx 上載；貼文字/PDF 只出建議清單（已 UI 提示）。dead code（AnalyzePanel/ReviewPanel）保留待 cleanup。
7. commits（**已 push origin/main**）: `6885dbe`(文件標註 Phase 1)→收尾 gov。
   - QC：backend tsc/check+build exit 0；真 OpenAI e2e（auto-detect 學校安全+學生支援/explicit conduct+secondary/empty→400/unknown domain→auto-fallback）；**真 docx 端到端**（browser preview 跑真 `buildAnnotatedOriginalDocx` on 真生成 docx：DOMParser well-formed、ref↔comment id 對齊+body 非空、highlight/ct/rels/附錄齊、located 3/unlocated 2）；browser-verify（tab 合併、0 console err、panel render in-place+附錄 section+雙下載、fallback 清單 docx PK-valid 8297B）；**live e2e onrender**（3 guideline〔Supabase live〕+24 partial+50 missing、CORS echo policychecker origin）。

## Previous Session Record (S160)
1. UTC date: 2026-06-14
2. Session ID: Claude_20260614_S160 (S160) — 通宵自主（Leonard 授權 agent teams/workflow、留 token buffer）
3. Completed（詳見 SESSION_LOG S160）:
   - ✅ **P2 政策範本下載 tab**（`fcccc34`，**LIVE**）：app.html +TemplatesPanel +'templates'；`policy_templates.json`（14 域 102 docx）；連現有 live docx；browser-verify 102 連結 / 校類 filter / fetch 200。
   - ✅ **P3 文件修訂 feature**（`bd99b91`，**LIVE**）：backend `checklistRevise.ts`（embedding coverage + clause supplement，無 LLM）+ `/api/checklist-revise` + `/api/checklist-domains`；`checklists_bundle.json`（root，14 域）；app.html +ReviewPanel +'review' +buildRevisedDocx。onrender live e2e PASS（14 域 / 真實報告 / CORS）。
   - ✅ **#2 幼稚園 Phase 2 KG LIVE 入庫**（Leonard sign-off supervised，`1bf497c`）：INSPECT→live INSERT `kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks** → Supabase 14,674→**15,109**（per-source 218/217 驗）；新 `kg_admin` route（擺 curriculum 前；route 7/7 + 本機 routed smoke 命中新源 p1/p78、收生無回歸）；display-sync ×7 →15,109（live Pages 驗）；registry 216→218。
4. Pending: **#2 收尾**（verify Render KG 路由 deploy `1bf497c` propagating — 本機已綠）+ **幼稚園清單 pilot**（用新 2 源起 KG checklist→docx→manifest）；#3 docx review；文件修訂 Phase 2.5。
5. Next priorities: KG 路由 deploy verify + 清單 pilot → #3 review → Phase 2.5。
6. Risks: 🟢 HEAD==origin/main（已 push）。⚠️ Render KG 路由 deploy 仍 propagating（本機 routed smoke 已實證正確；live「學前機構辦學手冊」未 flip = 慢 deploy，非 build fail — tsc build PASS）。`kg_admin`「幼稚園質素」query 命中 qa_inspection（minor mis-route、acceptable）。覆蓋門檻估算（tunable）。
7. commits（**已 push origin/main**）: `fcccc34`(P2)→`bd99b91`(P3)→deploy gov→`1bf497c`(KG 入庫)→收尾 gov。
   - QC：P2 browser-verify 全綠；P3 e2e（match 198/10/0 vs 1/5/202、400）+ onrender live；KG = INSPECT + 2×live INSERT(218/217) + route 7/7 + 本機 routed smoke(p1/p78、收生無回歸) + tsc/build + display-sync live 驗。

## Previous Session Record (S155)
1. UTC date: 2026-06-11/13
2. Session ID: Claude_20260613_0900 (S155)
3. Completed:
   - ✅ **任務①** PAGE_COVERAGE_REPORT.md（207 源/14,505 chunks）
   - ✅ **任務②** 14 範疇 × 2 docx = 28 files 全部生成
   - ✅ **Git commit 122a7b9**（804 files）→ **4e496a2**（closeout）— **已 push** (68fe43d..4e496a2 → origin/main)

## Previous Session Record (S154)
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
7. commits: `a6547c6`(文件分析 code) → `d17c25d`(governance) → `46376f4`(IMC 入庫) → `60da7f0`(governance) → `37995bc`(Cloudflare ×4) → `36af538`(governance) → `0c34611`(入口停用) → `db4fe12`(governance) → 收工 closeout commit。


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
