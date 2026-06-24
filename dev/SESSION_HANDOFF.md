# Session Handoff

<!-- ack:section:durable-anchors -->
<!-- ack:section:closeout-reconciled-state -->
<!-- ack:section:task-understanding-summary -->
<!-- ack:section:active-objective -->
<!-- ack:section:completed-this-session -->
<!-- ack:section:sync-status -->
<!-- ack:section:workspace-identity -->
<!-- ack:section:next-task-required-reading -->
<!-- ack:section:validation-qc -->
<!-- ack:section:risks-blockers -->
<!-- ack:section:next-priorities -->
<!-- ack:section:current-baseline -->
<!-- ack:section:state-reconciliation-check -->
<!-- ack:field:lifecycle-conflicts-resolved -->
<!-- ack:field:persistence-routing-checked -->
<!-- ack:field:stale-snapshots-left -->
<!-- ack:field:opening-message-matches-current-state -->
<!-- ack:field:state-sections-rewritten-or-confirmed -->
<!-- ack:field:user-intent -->
<!-- ack:field:task-essence -->
<!-- ack:field:success-criteria -->

## Current Baseline

> **🆕 S180（2026-06-24）reconciled — 數字以本段為準（下面 S179 及累積 baseline 為歷史背景）：** HEAD==origin/main **`fb1f8fc`**；Supabase **15,414**（`footnote_curated` **84** ＝ S179 ×83 ＋ S180 ×1〔SAG §3.7.3 懷疑性侵犯轉介報警 overlay〕）；平台 **v3.2.1**（凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S180 一項 LIVE（Render verify overlay rank-1 + grounded synthesis）**：SAG 學校行政手冊版本核對 — EDB 已由 2025-11 換到 **2026-05 版**（markup/clean Last-Modified 2026-05-20、served 同檔名故結構上避過 served-URL/freshness 監察）；官方 Log_sheet 證自 2025-11 起唯一 delta=item 73（§3.7.3「與性有關的問題」）；逐字 diff 揭實質改動=1 新增段（懷疑性侵犯→須遵照社署《保護兒童免受虐待–多專業合作程序指引》、諮詢社署保護家庭及兒童服務課或警務處虐兒案件調查組、涉刑事須報警）→ 捕捉為 1 curated overlay（`footnote_fn_sag_sexual_abuse_referral`、url SAG_C_markup.pdf#page=80）+ registry `version_label` sag_2025_11/g24 → 2026-05 + display-sync 8 點。commit `fb1f8fc`（push）。**起手探針**：app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a warm 455（warm=false 多屬 free-tier cold-start、輪詢十幾秒即升 455＝良性，持續 0 先查 OpenAI billing）+ HEAD `fb1f8fc` + Supabase **15,414**（footnote_curated 84）。✅ Side-finding（已調查 resolved）：SAG 雙重 ingest（`sag_2025_11` markup 383 + `g24` clean 383）由 **soft-dedup 妥善處理**（`wikiRepository` alias g24→sag_2025_11 + seen-Set dedup + 共用 per-source quota）、**無需 hard-dedup**；公開指引標籤亦已同步 2026-05（`guidelines.json` 2.6.0→2.6.1 + `app.html` GUIDELINES_REGISTRY，count 158 不變）。commits 全鏈 `fb1f8fc`→`e521dee`→`0707faa`→`7828f3e`。⚠️ 入/改 footnote 後必 restart Render（本 session push 已觸發 redeploy、live 已驗）。⚠️ live Supabase 寫入＝安全閘 gated，要 Leonard 明確授權。

> **🆕 S179（2026-06-23）reconciled — 數字以本段為準（下面累積 baseline 為歷史背景）：** HEAD==origin/main **`89eee3a`**；Supabase **15,413**（`footnote_curated` **83** ＝ S174 ×33 ＋ S177 ×26 ＋ S178 ×2 ＋ S179 ×22〔footnote 擴充 14 ＋ discovery 三快贏 8〕）；平台 **v3.2.1**（凍結合約 `_meta` 2.3.0／facts 455／guidelines 158 不變、無 bump）。**S179 四項 LIVE（全 verbatim 核 + live 驗）**：①**footnote 擴充第三批 14 條**（SAG 假期/HR 8〔病假 28→48 封頂168／肺病假 3/6/12月／侍產假5天產假14週／年假/緊急私事假/遴選委員會≤60%/受聘前胸肺X光/超額主任調配/改編學位教師〕＋ IMC免稅s.88／幼稚園租金九月計/每班最少1教師/戶外活動師生比例 ＋ forms 手尾 #7 CEG未上載追回 #18 CFEG家具無上限）→ Render live **6/6**；②**discovery 三快贏 8 條**（處理學校投訴×3／4Rs約章+三層應急機制×3／私隱條例Cap.486×2，route-independent overlay 無需改路由）→ Render live **8/8**；③**kg_operation 388 items + 162 clauses 補標 `['kindergarten']`** + bundle 重生（→1603KB）；④**TRG served-URL 404 修復**（`trg_imc_2023` 3 chunk url `en/...C.pdf`404→`tc/...c.pdf`200，Leonard「一次過做」明確授權）。commits `3897169`→`89eee3a`。**起手探針**：app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a warm 455 + HEAD `89eee3a` + Supabase **15,413**（footnote_curated 83）。⚠️ 入/改 footnote 後**必 restart Render**（footnote in-memory cache；本 session push 已觸發 redeploy、live 已驗）。⚠️ live Supabase 寫入＝安全閘 gated，要 Leonard 白紙黑字明確授權（「全部都做」covers footnote scope；新揪出嘅 production 寫入如 TRG 要逐個明確授權）。⚠️ OpenAI quota 曾用爆（已充值；warm=false 或搜尋 429 即查 billing）。

1. **Version / git**: **平台 v3.2.1**（user-facing `PLATFORM_VERSION='3.2.1'` in app.html，與凍結資料合約分離；S173：文件標註 off-domain 相關性下限〔guideline 0.62 + domain 0.45 floor〕+ OpenAI node-fetch 韌性修復）；資料合約 knowledge 凍結 @2.3.0、guidelines @2.6.0（`_meta.version` 不變）；git **`main` HEAD == `origin/main`（已 push `788538e`，S176 Agent Handoff Kit v0.1.7→v0.3.29 升級〔治理層，零產品改動，doctor 48/48〕；前 `5cb978d` S175 手機首次導覽 tour + checklist school_types 補標）**；Supabase **15,363**（S174 +33 `footnote_curated` overlay；S172 deprecate `sch_calendar_guide` −6；S171 +DEBP 209，新 `digital_education` route）。**⚠️ 起手 FIRST：探針 https://policychecker.wongfu.net/app.html HTTP 200 + PLATFORM_VERSION 3.2.1；再 verify HEAD==origin/main + Supabase 15,363 + Render /health（cache_a warm 455）。〔hosting 已穩定。〕** **S174（2026-06-21，Leonard /loop 自主 → 批 A live 入庫 → A 收工）：附件細字 footnote 入庫機制 SHIPPED LIVE — Leonard 指出 EDB 文件附件表格底細字（註/備註/footnote）藏住正文無講嘅實質要求（費用上限/資助級別/批核權/計算公式/安全門檻/法律定義/校曆/人手比例）→ 全庫 209 掃 footnote（1104→精煉 61→triage）→ 33 條策展入 Channel B（`content_type=footnote_curated`、15,330→15,363、INSPECT 齊、`id=footnote_*` 可逆）。揭發路由盲點（`searchWiki` RPC 後 `sourceIds` post-filter 丟 footnote + ivfflat probes=8 recall）→ 修 `wikiRepository.searchFootnotes`（exact-cosine overlay 繞路由/ivfflat）+ `searchChannelB` footnote pass（強配對 ≥0.45 lead 入合成窗、best-effort）；re-embed text+keywords。敵意 held-out 62%→75.8%→**live 100%**（synthesize 證原 hallucination〔代課批准亂作「30日」〕修正為真「6個月/大多數校董」）。display-sync 15,363；凍結合約零接觸、無 PLATFORM_VERSION bump。commits `8f2cace`→`9b3d8f9`.**S163QC（2026-06-14，Leonard 22:40 自啟全權）：v3.0 release QC 6 blockers NO-GO→GO。** P1 app.html header/footer displayVersion→PLATFORM_VERSION(v3.0.0,凍結 _meta 2.3.0 不變；local 驗,待 Pages 復原 live 驗)。P2 searchChannelB kg_admin route +幼稚園營運/營運手冊/運作/健康紀錄（**Render LIVE 驗**：query「幼稚園營運 手冊 健康紀錄」surface kg_operation_manual+kg_admin_guide，原 g26-only；export detectQueryCategory）。P3 checklistRevise graded 詞彙重疊閘（informative CJK-bigram，DF 自校準）+MAX_ITEMS 220→400（**Render LIVE 驗**：短 KG 文 covered 20→5/partial 55→30；richer 文 covered=37 無 false-neg；export cjkBigrams）。P4 README v3.0.0／P5 .gitignore 備份(不刪)／P6 mobile scope 文檔(search/guidelines/about；annotate+templates=desktop)。Regression 修 2 stale FAIL（schema 1.3.1→2.3.0/2.5.0；role-bucket→union both-roles）+P2/P3 cases=20 PASS/0 FAIL。commits `39e6df1`(backend)→`3f239bf`(frontend/docs)+gov 全 push。**S163（2026-06-14，Leonard「ABC」全權自主）：完成 C+A+版本/首頁+B 四項，全部 push + Pages/Render live 驗。** C 核 KG QC：17 flags 全修（`_qc_fix.py`）+ **揭發並修 S162 結構 bug**（kg_operation/clauses.json 非標準 schema `section_no/name`→canonical `si/section_name`：修 backend supplement linkage 388/388 由失效恢復 + 學校版 docx 章節名空白）→ `ef43517`. A 文件標註 Phase 2.5：`detectDomainsPerSegment`（per-segment argmax 路由）取代 whole-doc detect（多範疇文件各段路由其域，單範疇仍 1 域；比 legacy 更準——maths legacy 誤判 qa_inspection、新版正確 curriculum）→ `d71ae1e`（Render 驗 SEN doc→['sen']）. 版本+首頁+平台介紹：`PLATFORM_VERSION='3.0.0'` decouple；app.html 平台介紹 channels 改 政策搜尋/文件標註/範本下載/指引文件庫/通告分析；index.html +文件標註+範本下載 卡+v3.0 eyebrow；CHANGELOG v3.0.0 → `f510ee8`. B 文件標註 Phase 2 PDF inline highlight：+pdf-lib 1.17.1；`extractPdf` 抽座標；`buildAnnotatedPdf` 原 PDF 就地螢光+編號 marker+CJK sticky-note（UTF-16BE `PDFHexString.fromText`，免嵌 CJK 字型）→ `7289380`. commits `ef43517`→`d71ae1e`→`f510ee8`→`7289380` 全 push。**S162（2026-06-14，全權自主，4123 排序做 ④①②③）：完成 ④①②，③ 留下次。④ 幼稚園清單 pilot — 新範疇 `kg_operation`（幼稚園營運，388 items/162 clauses/20 章；源 kg_operation_manual_2026+kg_admin_guide_2026）行勻 14-域 pipeline → **15 域**；4 docx 入「範本下載」（+幼稚園 filter，106 docx）；backend 零 code 改（bundle-driven）；live e2e KG doc auto-detect 單域。17 覆核 issues：修法團校董會→校董會，16 軟性 fabricated 入 `dev/checklists/kg_operation/QC_VERIFY_ISSUES.md` 待 Leonard 核。① 跨校類 filter — bundle 加 domain-level `school_types`（由 `_school_type_profiles.json` applies_to）+ backend `okType` precedence（clause→domain→all）+ `detectRelevantDomains` 加 sel；untagged clause 唔再跨校類漏（live A-D+regression PASS；一併修 6 既有型別專屬域）。② dead-code：刪 AnalyzePanel/ReviewPanel/buildAnnotatedDocx/buildRevisedDocx（app.html 4345→3715，browser-verify 0 err）。commits `ec01e1b`(④)→`5dde30f`(①)→`51b6df2`(②) 全 push；Supabase 15,109 零接觸。③（文件標註 Phase 2 PDF inline highlight / Phase 2.5 per-segment auto-detect）= 大 feature，留 fresh session。**S161（2026-06-14，全權自主）：「文件標註」合併主線 Phase 1 SHIPPED LIVE — 合併 文件分析+文件修訂 → 一個「📝 文件標註」tab：上載 .docx → 比對 EDB 指引 + 合規清單 gap → **原檔就地標註**（保留格式 + 螢光 highlight + 就地可見內聯建議（💡指引／⚠修訂）+ 未能定位項入文末附錄）→ 下載。新 `backend/src/api/annotateDocument.ts`（重用 analyzeDocument 指引比對 + checklistRevise 清單 gap，零改兩模組）+ `/api/annotate-document` route（10/min+413 cap）；`checklistRevise.ts` 加 `detectRelevantDomains`（auto-detect 涉及範疇）；`app.html` 加 `AnnotatePanel` + `buildAnnotatedOriginalDocx`（JSZip 操作原 docx XML）+ JSZip 3.10.1 CDN；舊 `#analyze`/`#review` hash → redirect `#annotate`。commits `6885dbe`(feature)→`0e71802`(gov)→`1aafeda`(反饋1:可見內聯建議+公開名)→`a1bc18f`(反饋2:校類filter對比+隱藏內部清單+標註文件header)→`745b02f`(反饋3:建議條文用 Word 追蹤修訂 w:ins，接受即套用) 全 push。live e2e onrender PASS（safety doc → 3 guideline〔Supabase live〕+24 partial+50 missing、auto-detect 學校安全+學生支援、0 truncated）。**Leonard 真檔（數學 docx）試用 2 輪反饋已即修 live**：(1)隱形 Word 批註→可見內聯建議、內部名→公開名；(2)政策範本隱藏「文件要求清單」(內部對照用)、修 `.filter-tab` 喺淺底白字隱形（加 `.filter-tab-light`）、標註文件加頂部 header（平台/校類/範疇/圖例）+ guideline framing「參考」+ checklist 可編輯「✎ 建議條文」。⚠️ 舊 `AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 變 dead code（已無 tab/render 引用，但保留——`REVISE_SCHOOL_OPTS`/`REVISE_STATUS_META`/`REVISE_BACKEND_URL` 仍被新 panel 用；cleanup 列 follow-up）。****S160（2026-06-14，通宵自主 + Leonard supervised）：(A) 政策範本下載 tab + 文件修訂 feature（`/api/checklist-revise`）LIVE deployed（live e2e PASS：14 域/真實報告/CORS）。(B) #2 幼稚園 Phase 2 KG LIVE 入庫（Leonard sign-off）：`kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks** → Supabase 14,674→**15,109**；新 `kg_admin` route（searchChannelB.ts，擺 curriculum 前；routed smoke 命中新源 p1/p78、收生無回歸）；display-sync ×7（→15,109）；registry 216→**218**。commits `fcccc34`(P2)→`bd99b91`(P3)→`1bf497c`(KG)+gov，全 push（Render KG 路由 deploy propagating）。****S159（2026-06-13）：(1) #3 學校版分校類 mass-gen — 13 域 per-type(小/中/特) docx 102 份入 `dev/checklists/<域>/`；修全 14 域學校版 docx「undefined」章節 bug；13 域 348 校類 carve-outs（school_types field）；Leonard 科目→校類 ruling 已套。(2) #4 文件分析 Phase 2 SHIPPED LIVE — 標註版 docx 下載 + 校類選擇器（analyzeDocument.ts/app.html，onrender e2e PASS）。(3) #2 KG 入庫 prep — 2 核心源抽取完成（435 chunks 待 INSERT，dev/vault/，live 入庫留下個 session）。Supabase 14,674 未動。****S157：checklist QC 全清（128 verify_issues、0 pending）。S158（2026-06-13）：(1) `ph_pri_guide_2025` 完整重抽入 Supabase 146→315 chunk（舊抽取封頂 80/262 頁、缺 ch3-6 正文；DELETE 146 舊 + INSERT 315 新）→ 總 14,505→**14,674**、公開 Channel B 搜尋實測命中 ch5/ch6；(2) curriculum 人文科 8/9 verify-issue 引用由 EDB 通告 re-anchor 去真指引 `ph_pri_guide_2025` 真物理頁（p8/11/19/123/127/192/196/245；idx7 培訓 刪），2 份 curriculum docx 重生；(3) 刪 人文科 idx7 + 科學科 4 條 30hr/15hr 培訓證書 items（行政公布非校本政策要求）；(4) display sync 14,505→14,674 × 7 處。**
2. **Frontend**: `index.html` landing；**`app.html` = Channel-B-only 唯讀 SPA（S151：admin 登入閘 + 知識提煉/知識管理 tab + CRUD/匯出/候選審核 全移除；淨 3 tab〔平台介紹/政策搜尋/指引文件〕+ 文件預覽抽屜；app.html 4100→2935 行 −1176）**；`t-purchase.html` draft flow（dormant）；`q.html` local knowledge.json Quick Q&A（dormant）。**S153：政策搜尋（Channel B）合成分析放長 ≤120→約250字（上限300 soft；live ~328）+ 來源頁碼喺結果顯示並可點跳去 PDF 第 N 頁。⚠️ app.html 有兩個搜尋 UI：React desktop `QAPanel`/`SourcesAccordion` + 手寫 mobile shell `mobile.js`（平板用）— 兩個 surface 都改咗；mobile 來源名亦改全中文(`displayName`) + 去走「原文·分數」badge。** **S154：+📄文件分析（第 4 個 tab，desktop React surface）— 用戶上載 PDF/docx 或貼文字 → client-side 抽取（pdf.js 3.11.174 + mammoth 1.6.0 CDN；原始檔永不上載）→ `POST /api/analyze-document` 逐段比對指引 → 逐段報告（指引 `url#page=N` link + LLM 一句提示 best-effort + 私隱提示 + 60k 字/12 段 cap）。mobile.js shell 未做（Phase 1.5）；Phase 2 目標 = 可下載標註文件。** **S154(3)：全 4 個公開 HTML（index/app/q/t-purchase）裝咗 Cloudflare Web Analytics 免 cookie beacon（`</body>` 前一行 defer script；token 係公開 client-side 識別碼非 secret）+ index/app footer 私隱細字「本站採用免 Cookie 匿名流量統計」。報表喺 Leonard Cloudflare dashboard → Web Analytics。架構：前端由零對外 runtime 服務 → +1（已入 CODEBASE External Services）。** **S164：mobile shell（`mobile.js`/`mobile.css`，≤640px/mobile UA 觸發）底部導航 3→4 入口（🔍搜尋/📚指引文件/📋範本下載/ℹ️平台介紹）；`#templates` = `buildTemplatesShell()` 純靜態「桌面版功能」畫面（badge+說明+`templates-preview.png` 截圖，img onerror 優雅隱藏，不提供下載）；文件標註維持 desktop-only 手機無入口。desktop React app.html 零接觸。** **S165：文件標註面板（desktop React）下載列重整為 3 按鈕——新「可編輯 Word 版」（`buildEditableDocx`，docx-lib 由抽取文字砌：配對段黃螢光+AI 建議綠螢光直寫、非 w:ins 追蹤修訂、Word/PDF/貼文字皆出）為推薦 primary；標註版原檔（`buildAnnotatedOriginalDocx` Word 追蹤修訂／`buildAnnotatedPdf` PDF 螢光，需上載檔）；建議清單。加「三種下載」指引塊（教 Word 校閱接受/拒絕）。現有 3 個 builder 不改。mobile.js 搜尋框 +enterkeyhint+Enter keydown handler。**
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
> **✅ S170（2026-06-15）正式版封版完成（全 verified live）：** ① 監察清訊號（freshness re-seed 全 215 baseline、假警報 9→0 修 stub-baseline artifact；discover `ENUMERATION_PAGE_CAP=25`、likely-real 680→223、no-loss、self-test PASS；commit `eb9d90b`）；② 學校行政手冊「開啟」404 兩層修（前端 `SOURCE_URL_FIXUPS` 改寫畸形 URL `59b8d2b` + Leonard Supabase `UPDATE` 383 `sag_2025_11` chunks url index.html→SAG_C_markup.pdf、url-only、verified live；根因＝registry↔store URL drift）；③ 平台 **v3.2.0 正式版**（PLATFORM_VERSION/README/CHANGELOG `6309333`，彙整 S169 ①②③⑤ + 本 session）；④ EDB 每週監察 email（Leonard 設好 GitHub Watch→Issues：#1 freshness / #2 discovery 每週一 email）；⑤ playbook 沉澱（repo `7057db8`）；⑥ ④ EDB 全入庫 triaged ＝**無乾淨批次值得入**（223 候選全係碎片/舊通告/表格/英文重複；corpus current）→ **monitor-driven on-demand**。**HEAD == origin/main `6488b44`（S171：重開通告分析入口 + DEBP 6 源入庫〔Supabase 15,336、digital_education route、live Render 8/8〕+ 首頁更新日誌 + 指引庫「資訊科技」正名「數字教育」收錄 DEBP 6 份〔guidelines.json v2.6.0 公開 158、app 167〕+ 指引庫跨範疇 also_in〔12 份多類顯示、純 UI 下游零改〕）、0 outstanding bug。**
> **✅ S172（2026-06-17）：① served-URL 健康檢查（Method B 監察）已建** — `dev/source/check_served_urls.py` + `.github/workflows/served_url_check.yml`（由 Supabase `wiki_chunks.url` 抽 distinct served URL 逐條 HTTP-test，封 registry-only freshness 監察結構上睇唔到嘅 store↔registry drift；self-test **21 PASS**；首跑 **199 URL / 197 OK / 2 條 pre-existing 404 揭發**；訊號路由跟 freshness 鐵律）**+ ② band-aid cleanup** 移除 `SOURCE_URL_FIXUPS`+`fixSourceUrl`（app.html+mobile.js；① 已證 store serve `SAG_C_markup.pdf` 200，verified no-op）。獨立對抗覆核 **PASS-with-flags（no blocker）**，採納 2 Low flag（429/408→error 防假警報 + Issue 列 error_urls）。**+ ③ 兩條 404 即修（Leonard 授權「兩條都修」→「#1 重指 + #2 deprecate」）**：#1 `edbc12_2025_ph_pri` Supabase `UPDATE` re-point 10 chunks → registry 200 URL（url-only、無 count 變）；#2 `sch_calendar_guide` deprecate（DELETE 6 stale chunks〔2025/26 公眾假期、上游已換 2627〕 + registry status→deprecated + 移除 hr_admin SOURCE_SET dead ref + display-sync 8 點 **15,336→15,330**）。served-URL 重掃 **198/198 OK · 0 broken**；tsc PASS、headless app.html boot render 15,330 無 stale。**no version bump**（infra+no-op+維護）。**+ ④ 文件標註真檔收貨（Leonard 真檔 SKHKYPS 家課政策 PDF）**：端到端跑通（auto-detect 課程管理、指引命中 SAG p199 家課〔SAG 修復 live 顯示〕）；揭發 narrow 文件 × broad 範疇精準度問題（curriculum 溝入幼稚園 + 通用課程噪音）→ **修復：curriculum 76 KG-source 清單項〔kgecg_2017+g29〕tag `school_types=['kindergarten']`** + 重生 bundle（primary-visible 580→504、KG 對 primary 0、家課 section 30/33 primary 項保留）。**✅ post-deploy live 確認**（Leonard 手動 deploy `f38b511`、auto-deploy=On Commit）：真檔重跑 curriculum 580→504、KG 污染 0、課業政策項浮現、SAG p199 命中。**+ ✅ served-URL CI 啟用驗證**（Leonard 設 `SUPABASE_ANON_KEY` secret、手動 run #1 conclusion=success、198 URL 全 200、0 Issue；每週一 11:00 UTC 自動跑生效）。commits 見 SESSION_LOG S172。
> **✅ S173（2026-06-18）：① 真 .docx 收貨（NEXT ① 完成，全 live 驗綠）** — 文件標註「保留格式 Word」path（`buildCleanOriginalDocx`）+ 表格內段落命中 端到端驗證（真檔=博智小學免責聲明，無表 → 合成表格補驗 builder 將「（建議補充）」note 正確插入 `<w:tc>`；mammoth 每 cell 用 `\n\n` 分隔 → 逐 cell segment、非整表一段）。**+ ② 揭發並修 off-domain 強行配對 → 平台 v3.2.0→v3.2.1**：你份免責聲明（off-domain 法律文書）原被強行配對無關「相關指引」(4 條：颱風通告/防貪/公社科) + 硬塞「學校安全」範疇 (18 條垃圾 missing)。加兩個 relevance floor（**只喺 `annotateDocument.ts` 層、`analyzeDocument`/`searchChannelB`/`checklistRevise` 及獨立 endpoint byte-identical、用戶手動選範疇不受影響**）：`GUIDELINE_RELEVANCE_FLOOR=0.62`（實證 live `text-embedding-3-small`：off-domain top ≤0.595 vs 真貼題 ≥0.654）+ `DOMAIN_RELEVANCE_FLOOR=0.45`（off-domain descriptor peak 0.396 vs 真 0.53–0.69）+ `app.html`「未找到貼題指引」空狀態。多範疇零 regression（Render pre==Local post 相同）。**+ ③ 揭發並修生產事故（部署觸發）**：v3.2.1 部署後 Render Node 原生 fetch（undici）對每個 OpenAI 呼叫回 `Premature close`（重用 OpenAI 已關閉嘅 keep-alive 連線；restart 唔修、啟動 cache warm 0/455、政策搜尋+文件標註全降級）；**同一 key/code 由其他出口 HTTP 200 → 隔離為 Render egress undici keep-alive（非 OpenAI/key/code/我嘅 floor 改動）**→ 修：兩個 OpenAI client 注入共用 `sdkFetch`（node-fetch、已綁定、每請求新連線繞過 stale keep-alive）+ pin Node `22.x`（`engines`+`.node-version`）。**全部 live 驗綠**（cache_a warm 455、Channel B OK、off-domain `0/0/[]` 空狀態、on-domain `guideline=2`/`課程管理` 保留）。凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines 158）；Supabase **15,330** 零接觸。commits `78605bd`(floors+v3.2.1)→`f254d0c`(OpenAI 韌性修復)。
> **✅ S174（2026-06-21，Leonard /loop 自主 → 批 A → A 收工）：附件細字 footnote 入庫機制 SHIPPED LIVE** — 33 條策展 footnote 入 Channel B（Supabase 15,330→**15,363**、`content_type=footnote_curated`、可逆）+ **路由獨立 `searchFootnotes` exact-cosine overlay**（繞 `sourceIds` post-filter + ivfflat probes=8 recall 盲點）+ lead-slot（`searchChannelB.ts`+`wikiRepository.ts`）；敵意 held-out 62%→75.8%→**live 100%**；原 hallucination（代課批准亂作「30日」）修正為真「6個月」；display-sync 15,363、凍結合約零接觸、無 PLATFORM_VERSION bump。commits `8f2cace`→`9b3d8f9`。**0 outstanding bug。**
> **✅ S177（2026-06-23）：政策搜尋砌數修復 + EDB 津貼表格 footnote 入庫，全 LIVE。** ①TRG 凍結教席「10%」footnote（修砌 IMC 60%）②synthesis 前防砌數 binary judge ③EDB 津貼表格細字 25 條 footnote（footnote_curated 34→59、Supabase 15,364→**15,389**，全 verbatim 核）。commits `71763f8`→`1f0d959`→`7827712`→`ef50b48`。0 outstanding bug。
> **✅ S178（2026-06-23）：forms 第二批完成 + MPF 漏答修復，全 LIVE（Render 6/6）。** tips #27（出租校舍淨租金 40% 入政府帳 EDBC 5/2011）+ #28（12 個月重複採購累計 $50k/$200k 不得拆單 EDBC 4/2013）verbatim 核官方 Tips TC PDF 入庫（footnote_curated 59→**61**、Supabase 15,389→**15,391**、display-sync 8 點）；MPF 漏答修復＝top 結果係 curated footnote 且 cosine≥0.45 時跳過 S177 judge（`searchChannelB.ts`，真因＝judge 過度保守、**非缺關鍵詞**；vault chunk 照 gate、anti-confab 保護不變）。commits `f19da01`→`41b7991`。
> **✅ S179（2026-06-23，Leonard「全部都做」+「1＋2」+「一次過做」全程授權）：footnote 擴充第三批 14 + discovery 三快贏 8 + kg_operation 補標 + TRG 修復，全 LIVE 驗證。** ①footnote 擴充 14 條（SAG 假期/HR 8＋幼稚園/IMC/活動 4＋forms #7/#18 2；verbatim 核 vault repaged／CEG·CFEG EN PDF；self-test 14/14、cross-check rank-1 14/14；Render live 6/6）②discovery 三快贏 8 條（投訴×3/精神健康 4Rs+三層機制×3/私隱 Cap.486×2；route-independent overlay 無需改路由；self-test 8/8；Render live 8/8）③kg_operation 388 items+162 clauses 全標 `['kindergarten']`+bundle 重生（1603KB）④TRG served-URL 404 修復（3 chunk url repoint→200）⑤Monitoring 跑齊（freshness 5 變動 detection-only／discovery 739 候選／served-URL 揾到並修咗 TRG 404）。footnote_curated 61→**83**、Supabase 15,391→**15,413**、display-sync 8 點 ×2、凍結合約零接觸、無 bump。commits `3897169`→`89eee3a`。0 outstanding bug。
> **🔜 NEXT（active 優先序，全部待 Leonard 揀方向／授權）：** ① **discovery 餘下未接觸角度**（S179 做咗 3 快贏、S180 做咗 SAG 版本核；agent 全文喺 SESSION_LOG S179）：教師註冊制度／學校註冊＋直資(DSS)制度／NCS 行政資助／傳染病預防(停課準則)／學費減免書簿津貼／NET 外籍英師計劃／校舍法定安全(EMSD 升降機)／EDB 表格庫(discovery seed)／SAG 附錄深抽。**✅ S180 已核 SAG 版本（commit `fb1f8fc`、Render live verify overlay rank-1）：confirmed EDB 換到 2026-05 版，唯一 delta=§3.7.3「與性有關的問題」，已捕捉為 1 curated overlay + registry version_label sag_2025_11/g24→2026-05 + display-sync。仍 open：SAG 附錄深抽（揾更多 footnote）；freshness 5 源內容變待跟進（detection-only）。SAG 雙 ingest dedup 已調查＝soft-dedup 足夠、無需 hard-dedup（resolved）；公開指引版本標籤已同步 2026-05。** 每角度＝download 官方 PDF + verbatim 核 + curated chunk（route-independent overlay）或全文入庫+routing；live 寫入要明確授權。② **footnote broad sweep（optional 低值）**：harvest_hi 61 高值已基本入晒，餘多屬課程內容註/書目/dup（monitor-driven）。③ **freshness 5 變動跟進**（g11／ma_curr_index／pri_science_cert_course_list／debp_blueprint／debp_ailf_example，detection-only，真 re-ingest 先逐源核+授權）。④ 既有 monitor：MPF/footnote-lead bypass 殘留（curated spurious lead，E case 證仍 grounded）／文件標註 narrow×broad 精準度＋短文件分段／Render cold-start ~50s + auto-deploy 偶爾卡／per-segment 範疇偵測／undici keep-alive（node-fetch 已修，復發→Azure swap）／SMC recall／DEBP OCR draft 質。
> 產品方向：**全棧 Channel-B-only**，平台 **v3.2.1**（文件標註 off-domain 相關性下限 + OpenAI node-fetch 韌性修復），Supabase **15,330**（S172 deprecate −6；S171 +DEBP 209），指引 公開 **158** / app 內庫 **167**（`guidelines.json` v2.6.0、支援跨範疇 also_in）。Channel A frozen @455。**✅ S168 backlog 已清：①文件標註保留格式+改動摘要 / ②onboarding / ③使用手冊 / ⑤dead-code = S169 done；④ EDB 入庫 = S170 reframed monitor-driven（triaged 無批次值得入）；⑥ Render cold-start 仍 open（見 NEXT）。** **S168（2026-06-15）：SMC（學校管理委員會）章程樣本入庫（smc_constitution_sample +18 chunks → 15,127；SOURCE_SETS.school_governance；display sync 7 點 byte-identical、_meta 凍結 2.3.0）+ 平台 v3.1.0（PLATFORM_VERSION/README/CHANGELOG）。Leonard「授權全做全入庫」明確授權後執行（首試被 auto-mode classifier 擋＝缺授權，正確 guardrail）。commit `a82210e`。** **S167（2026-06-15）：文件標註下載簡化為單一「乾淨成品版」(`buildCleanDocx`)——原文正文乾淨（無螢光/無 inline 註解）、AI 建議融入正文做普通文字帶「（建議補充）」極簡標示、說明+EDB 出處集中文末附錄；Word/PDF/貼文字皆出；取代追蹤修訂/可編輯/清單三按鈕（解決「接受修訂後螢光殘留、原稿亂」）。commit `ee2c89f`，Pages live。舊 builders 變 dead code，cleanup task `task_94ebfd14`。** **S166（2026-06-15）：手機品牌統一（K1知識平台→香港學校政策搜尋平台）+ 可撳「搜尋」掣（唔再淨靠 enter，commit `5c55320`）+ SMC/IMC 英文縮寫 retrieval 修復（`searchChannelB.ts` school_governance route +英文縮寫 + query expansion；commit `7d70dda`；Render live 驗 SMC/IMC→IMC 治理文件 grounded，取代課程垃圾源；audit 14 query 11 OK，SBA=內容稀疏 follow-up）。** **S165（2026-06-15）：文件標註新增「可編輯 Word 版」下載（`buildEditableDocx`：配對段黃螢光+AI 建議綠螢光直寫文中、非追蹤修訂、免接受修訂；Word/PDF/貼文字皆出，解決 PDF 不可編輯）+ 下載列三按鈕+「三種下載」指引（教接受/拒絕）+ 手機搜尋修 enter（enterkeyhint+keydown）。不改現有 builder；純前端零接觸 backend/Supabase/凍結合約；commit `afec532` pushed+Pages live。待 Leonard 真機/真檔收貨。** **S164（2026-06-15）：mobile 底部導航加 📋範本下載（3→4 入口；該手機畫面=「桌面版功能」標示+說明+桌面面板截圖 `templates-preview.png`，不提供下載；文件標註維持 desktop-only）+ README/CHANGELOG/PROJECT_MASTER_SPEC §B.5/CODEBASE_CONTEXT/DOC_SYNC 同步。純前端 mobile shell + 文檔，desktop/backend/Supabase/凍結合約 零接觸；commit `0057dfe`。headless --dump-dom 核實全綠（待真機收貨）。** **S163（ABC）：C 核 KG QC（17 flags 全修 + 修 S162 schema bug）+ A 文件標註 Phase 2.5 per-segment + 版本/首頁/平台介紹 refresh（PLATFORM_VERSION 3.0 decouple）+ B 文件標註 Phase 2 PDF inline highlight 全 DONE & pushed + Pages/Render live 驗。** Supabase 15,109、HEAD==origin/main。主線 0 outstanding bug。

1. **✅ 站 hosting 事件已解決（v3.0 GO）**：根因 = Leonard 一度將 repo set private → GitHub Pages 免費 plan 唔支援 private → 全站 404，連帶 Render auto-deploy 失 repo access。**最終解法 = 開返 public**（content 本來已公開），policychecker.wongfu.net Pages republish 復原（關鍵：re-enable Pages source 後**要新 push 先觸發 build**；空 commit `d3cf505` 搞掂）。**另起 here.now 鏡像** `https://tender-garnet-hqbd.here.now/`（permanent；只發公開前端子集；backend CORS 加咗呢個 origin `364b48f`）。Render 重新 auto-deploy，CORS 三域齊（github.io/policychecker/here.now）。**全部 live 驗證 PASS**：policychecker + here.now 兩站 app.html v3.0.0 + buildAnnotatedPdf、index.html v3.0+卡、搜尋 end-to-end（ACAO 正確）、P2 KG routing surface manuals。⚠️ **Render 免費 tier 閒置 15min 瞓 → 第一搜尋 cold-start ~50s**（production 考慮升 always-on 付費）。
2. **Leonard 收貨 v3.0 QC 6 fixes**：P2/P3 Render 已 LIVE 驗、P1 local 驗（待 Pages）、P4/P5/P6 docs。確認後 v3.0 NO-GO→GO。
3. **真檔驗 / monitor**：Phase 2 PDF 真檔對位+多 viewer CJK；P3 gate 真檔多範疇覆蓋率合理性（STOPWORD_DF_FRACTION=0.25/COVERED=0.5/PARTIAL=0.42/MAX_ITEMS=400 tunable）；P2 KG routing 真用戶查詢；Phase 2.5 多範疇 UX。
4. **既有**：KG QC DRAFT 最終核（QC_VERIFY_ISSUES 17 已修）；#3 學校版 102 docx review（live「範本下載」tab）。
5. **✅ Leonard 已認可（S163 "all agree"）**：v3.0.0 版本方案 + S162 schema fix + KG QC + Phase 2 PDF——confirmed。
2. **文件標註 Phase 2 真檔驗證（建議）**：S163 PDF highlight 已 in-browser pipeline 驗（合成 PDF 全綠），但未用真 EDB／學校 PDF 端到端跑——建議 Leonard 上載一份真 PDF 試 highlight 對位＋sticky-note CJK 顯示（不同 viewer：Acrobat/Preview/Chrome）。座標假設無頁面旋轉（rotation 已存但未補償）；碎 run／表格命中率 monitor。
3. **文件標註 Phase 2.5 多範疇 UX（monitor）**：auto 由硬 1 域改 ≤3 域（per-segment）。單範疇文件仍 1 域；多範疇文件會出多域 findings（前端已支援 domains[]）。觀察真檔會否過多域；`SECONDARY_MIN_SEGMENTS=2`/`AUTO_DETECT_MAX_DOMAINS=3` tunable。
4. **既有 monitor + follow-up**：文件標註門檻 COVERED=0.50/PARTIAL=0.42 + AUTO_DETECT_THRESHOLD=0.38 + auto missing cap 8 / `kg_admin`「幼稚園質素」→qa_inspection / IMC 頁碼 / cgss rank 低 / 57014 free-tier / stats.sources=120 cosmetic / Azure fallback / 週跑。

## Backlog（次優先序，視 OP 完成情況流轉）
- g21/g22/g33 直連 PDF 補完（user browser）— Session 105 audit 揭發三者 source_type='pdf' 但 url_primary 缺
- 5 個 stat xlsx 下載 + 上 vault（user browser）
- 學校行政手冊徹底 refetch 統一 source_id（軟 dedup 已 ship 足夠用）
- 開新功能方向（admin 端 Channel B prompt editor / index.html 新區塊 / 下游 Circular System 整合）
- **雲端 OCR 引擎選項**（image-PDF ingestion 升級線，S180 評估）：Google Vision `DOCUMENT_TEXT_DETECTION`（逐字信心 + bounding box、每月 1,000 單位永久免費 + ~$1.50/1,000、要綁卡開 billing）／Mistral OCR（Markdown+表格、~$2/1,000）——比現用 `gpt-4o` 圖像 OCR「draft 質」可能更準更平，且 bbox 可餵返 grid 重建。命中 image-PDF 質素問題（如 DEBP 主藍圖 ~16 圖像頁）先評估：**真檔實測 + 開 Google billing**（ingestion 處理公開文件、無未成年私隱顧慮；後端已存在故唔需要 brief 嗰套 serverless key-proxy）。詳見 playbook inbox 提案 `2026-06-24-edb-knowledge-cloud-ocr-engine-options.md` + `doc-extract-method-ladder` 卡。出處：Leonard 一份 OCR 收費版 brief（2026-06，已核實價）。

## Last Session Record
1. UTC date: 2026-06-24
2. Session ID: Claude_20260624_1415_S180 — 「開工」→ 頂層 redirect → Draft active root；起手探針全綠（HEAD `78312a0`==origin/main、app v3.2.1、Render cache_a warm=false→背景輪詢 ~10s 升 455＝良性 cold-start、Supabase 15,413/footnote_curated 83）→ Leonard「做」核 SAG 版本 → live confirmed EDB 換 2026-05、官方 Log_sheet+逐字 diff 證 delta=§3.7.3 一個新增段 → Leonard 揀 (A) curated overlay → verbatim 重核 + self-test 0.758 + 「做」明確授權 → live INSERT + registry/display 同步 + Render live verify rank-1 grounded → Leonard 畀 OCR 收費版 brief 評估（B）→ SAG dedup 調查（C）→「收工」full closeout。
3. Completed（詳見 SESSION_LOG S180）:
   - ✅ **SAG 2026-05 版本核對 + §3.7.3 新段入庫 LIVE**：discovery 旗中 → live confirmed EDB SAG 換 2026-05（Last-Modified 2026-05-20、served 同檔名避過 served-URL/freshness 監察）；唯一 delta=§3.7.3「與性有關的問題」新增「懷疑性侵犯→社署保護家庭及兒童服務課/警務處虐兒組轉介+報警（依《多專業合作程序指引》）」一段 → 捕捉為 curated overlay `footnote_fn_sag_sexual_abuse_referral`（footnote_curated 83→84、Supabase 15,413→15,414）+ registry/公開指引 version_label→2026-05（三邊一致）+ display-sync。Render live verify overlay rank-1 score 0.739 + synthesis grounded。
   - ✅ **B — OCR 收費版 brief 評估 + 袋低**：架構（serverless key-proxy）對本 project 幫助低（後端已存在、key server-side）；OCR 引擎事實（Vision DOCUMENT_TEXT_DETECTION/Mistral）對 image-PDF ingestion（現用 gpt-4o draft）有用 → handoff Backlog（`0707faa` pushed）+ playbook inbox 提案 enrich doc-extract-method-ladder（`ead3749` local、未 push）。
   - ✅ **C — SAG dedup resolved + 公開指引同步**：`wikiRepository` alias g24→sag_2025_11 + seen-dedup + 共用 quota → 雙重 ingest 由 soft-dedup 妥善處理、無需 hard-dedup；調查揭 g24 雙重身份 → 補做公開指引 title sync（guidelines.json 2.6.0→2.6.1 + app.html，count 158 不變、`7828f3e`）。
4. Pending: discovery 餘下 8 角度（教師註冊/DSS/NCS/傳染病/學費減免/NET/EMSD/EDB表格庫）；footnote broad sweep；freshness 5 變動；既有 monitor；**playbook OCR 提案待 push（local `ead3749`）**。見 Open Priorities 🔜 NEXT。
5. Next priorities: ① discovery 餘下角度 → ② 既有 monitor。
6. Risks: 🟢 HEAD==origin/main `2acf631`、Supabase **15,414**、footnote_curated **84**、凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines.json 2.6.1 公開 158）、PLATFORM_VERSION 3.2.1 不變、0 outstanding bug。⚠️ live Supabase 寫入＝安全閘 gated 要明確授權（本 session「做」授權後 INSERT 1）。⚠️ playbook 跨 repo push 被 auto-mode 擋（待 Leonard push/授權）。⚠️ 入/改 footnote 後必 restart Render（push 已觸發）。⚠️ OpenAI quota 曾用爆（已充值、warm=455 健康）。⚠️ 雙治理層共存（衝突取較安全可驗路徑）。⚠️ `SESSION_HANDOFF/LOG/START_NEXT_SESSION_PROMPT.txt` 雖列 `.gitignore` 但已 tracked → 照常 commit。
7. commits（push origin/main）: `fb1f8fc`(§3.7.3 overlay+registry+display-sync 15414)→`e521dee`(persist)→`0707faa`(backlog OCR)→`7828f3e`(公開指引 sync+dedup verified)→`2acf631`(persist B+C)→收工 commit。playbook `ead3749` local-only。live Supabase INSERT 1（Leonard 授權「做」、INSPECT before/after）。

## Previous Session Record (S179)
1. UTC date: 2026-06-23 | Claude_20260623_S179
2. footnote 擴充第三批 14 + discovery 三快贏 8 + kg_operation 補標 + TRG 404 修復，全 LIVE（Render 6/6+8/8）；footnote_curated 61→83、Supabase 15,391→15,413。commits `3897169`→`89eee3a`。詳見 SESSION_LOG S179。

## Previous Session Record (S178)
1. UTC date: 2026-06-23 | Claude_20260623_S178
2. forms 第二批 + MPF 漏答修復，全 LIVE（Render 6/6）：tips #27 出租校舍 40% 入政府帳（EDBC 5/2011）+ #28 12 個月重複採購 $50k/$200k 不得拆單（EDBC 4/2013）verbatim 核 Tips TC PDF（footnote_curated 59→61、Supabase 15,389→15,391）；MPF 漏答修復＝top 係 curated footnote 且 cosine≥0.45 時跳過 S177 judge（`searchChannelB.ts`，真因＝judge 過度保守非缺關鍵詞）。commits `f19da01`→`41b7991`。詳見 SESSION_LOG S178。

## Previous Session Record (S177)
1. UTC date: 2026-06-23 | Claude_20260622_S177
2. 政策搜尋砌數修復 + EDB 津貼表格 footnote 入庫，全 LIVE：①TRG 凍結教席「10%」footnote（修砌 IMC 60%）②synthesis 前防砌數 binary judge（`searchChannelB.ts`）③EDB 津貼表格細字 25 條 footnote（footnote_curated 34→59、Supabase 15,364→**15,389**，全 verbatim 核）。commits `71763f8`→`1f0d959`→`7827712`→`ef50b48`。詳見 SESSION_LOG S177。

## Previous Session Record (S175)
1. UTC date: 2026-06-22
2. Session ID: Claude_20260622 (S175) — 「開工」→ startup reads + ① footnote 擴充 defer（Leonard「暫時看不到」）→ proactively 修其他可行項：手機首次導覽 tour（4 步 overlay + CSS，`k1_mobile_tour_v1` localStorage gate，tour→role picker 序列）+ checklist school_types 補標（curriculum 79 項 + kg_admission 16 項）+ DOC_SYNC 文件更新（CHANGELOG / PROJECT_MASTER_SPEC §B.5 / README）→ 收工。
3. Completed（詳見 SESSION_LOG S175）:
   - ✅ **手機首次導覽 onboarding tour**（`c714abe`，`mobile.js` + `mobile.css`）：4 步全螢幕 overlay（platform → search → guidelines → ready）；z-index 210 > role picker 200；`k1_mobile_tour_v1` localStorage gate；first-run 序列由直接 role picker 改為 tour → role picker。
   - ✅ **Checklist school_types 補標**（commits `839d741`、`02d9ca0`、`a3babce`）：curriculum 79 項（6 小學 rollout `['primary']` + 3 中小兼 `['primary','secondary']` + 70 pri_curr_guide_2024 `['primary']`）；kg_admission 16 項（k1_admission_2627 ×7 + kg_admin_guide ×9 → `['kindergarten']`）；`checklists_bundle.json` 重生（1573KB，15 域）。
   - ✅ **DOC_SYNC 文件更新**（`5cb978d`）：CHANGELOG 新 S175 章節；`dev/PROJECT_MASTER_SPEC.md §B.5` first-run 序列描述；`README.md` mobile 段加 onboarding 說明。
4. Pending: kg_operation 域 388 項全 KG-only（`kg_admin_guide_2026` 205 + `kg_operation_manual_2026` 183）仍無 `school_types`——大批次，待 Leonard 明確授權後再做。
5. Next priorities: ① footnote 擴充（待 Leonard 定）→ ② 文件標註精準度 monitor → ③ kg_operation school_types 補標（待授權）。
6. Risks: 🟢 HEAD==origin/main `5cb978d`（5 commits，已 push，tree clean，0 outstanding bug）。🟢 Supabase 15,363 零接觸；凍結合約 `_meta` 2.3.0·facts 455·guidelines 158 不變；PLATFORM_VERSION 3.2.1 不變。⚠️ kg_operation 388 項 untagged（待 Leonard 授權）。⚠️ Render free-tier cold-start ~50s + footnote cache restart（`invalidateWikiCache`）。⚠️ OpenAI node-fetch Premature close 復發 → Azure fallback。
7. commits（已 push origin/main）: `c714abe`(feat: mobile onboarding tour) → `839d741`(fix: 6 primary rollout items) → `02d9ca0`(fix: 3 primary+secondary items) → `a3babce`(fix: 70 pri_curr_guide_2024 + 16 kg_admission) → `5cb978d`(docs: CHANGELOG/README/PROJECT_MASTER_SPEC §B.5)。零 Supabase 改動。

## Previous Session Record (S174)
1. UTC date: 2026-06-21
2. Session ID: Claude_20260621_1200 (S174) — 「開工」探針全綠 → Leonard 指出 EDB 文件附件細字 footnote 藏住實質要求 → harvest 33 → Leonard /loop 批 A live 入庫（INSPECT+INSERT 15,363）→ 揭路由盲點 → 修 searchFootnotes 路由獨立 overlay → live 100% → 收工。
3. Completed（詳見 SESSION_LOG S174）: ✅ 附件細字 footnote 入庫（33 條 `footnote_curated`，15,330→**15,363**）；✅ 路由獨立 `searchFootnotes` overlay（繞 `sourceIds` post-filter + ivfflat probes=8 盲點）；✅ 敵意準確度 62%→75.8%→live 100%；✅ display-sync 15,363 ×8 + CHANGELOG。commits `8f2cace`→`9b3d8f9`。

## Previous Session Record (S173)
1. UTC date: 2026-06-18
2. Session ID: Claude_20260618_0839 (S173) — 「開工」起手探針全綠 → Leonard 畀真 .docx（博智小學免責聲明）做 NEXT ① 真檔收貨 → 驗保留格式+表格命中（合成表格補驗）→ 揭發 off-domain 強行配對 → Leonard 批「加相關性下限」→ guideline floor 0.62 → 揭發第二頭（domain 偵測同 over-fire）→ Leonard 批 domain floor 0.45 → bump v3.2.1 push → 部署觸發 Render OpenAI `Premature close` 生產事故 → 隔離（key 健康/問題喺 Render egress undici）→ Leonard 批 node-fetch + pin Node 22 修復 → live 全驗綠 → 收工。
3. Completed（詳見 SESSION_LOG S173）:
   - ✅ **真 .docx 收貨（NEXT ① 完成）**：保留格式 `buildCleanOriginalDocx` + 表格內段落命中 端到端驗（忠實 harness：真 mammoth 1.6.0 → 真 Render → 逐字抽出真 builder 離線跑；真檔無表 → 合成表格證 note 正確插入 `<w:tc>`；mammoth 每 cell `\n\n` → 逐 cell segment）。
   - ✅ **文件標註 off-domain 相關性下限 → v3.2.1**：`GUIDELINE_RELEVANCE_FLOOR=0.62`（指引比對）+ `DOMAIN_RELEVANCE_FLOOR=0.45`（範疇偵測）只喺 `annotateDocument.ts` 層、reused module byte-identical、手動選範疇不受影響 + `app.html`「未找到貼題指引」空狀態。本地端到端 + 多範疇零 regression（Render pre==Local post）+ live 驗綠（off `0/0/[]`、on `guideline=2`/`課程管理`）。
   - ✅ **生產事故修復（OpenAI 韌性）**：v3.2.1 部署觸發 Render undici 對每 OpenAI 呼叫 `Premature close`（stale keep-alive、restart 唔修、cache 0/455、全降級）；隔離為 Render egress undici keep-alive（key/code 由其他出口 200）→ 兩個 OpenAI client 注入共用 `sdkFetch`(node-fetch、每請求新連線) + pin Node `22.x`；local embedding/LLM 驗綠 + live 復原（cache_a warm 455）。
   - ✅ commits `78605bd`(floors+v3.2.1)→`f254d0c`(OpenAI 韌性) 全 push；Desktop 留 2 樣本 docx 俾 Leonard 睇成品。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: 文件標註精準度 monitor → EDB monitor-driven 入庫 → mobile onboarding。
6. Risks: 🟢 HEAD==origin/main `f254d0c`（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines 158）、Supabase 15,330 零接觸。⚠️ **OpenAI node-fetch 修復只 live 驗綠一次** —— 留意 `Premature close` 復發或 Node 22 有 issue（Azure swap = fallback；見 NEXT ⑧）。⚠️ Render free-tier cold-start ~50s + auto-deploy 偶爾卡（要手動 Deploy latest commit）。⚠️ per-segment 範疇偵測收斂單一 broad 範疇（既有偵測質素、monitor、NEXT ⑦）。
7. commits（已 push origin/main）: `78605bd`(v3.2.1：guideline+domain floor + 空狀態 + version bump)→`f254d0c`(OpenAI node-fetch sdkFetch + pin Node 22.x)+本 closeout commit。

## Previous Session Record (S172)
1. UTC date: 2026-06-17
2. Session ID: Claude_20260617_1731 (S172) — 「開工」起手探針全綠 → Leonard「1-3」batch（NEXT ①②③）→ 建 served-URL 監察 → 首跑揭發 2 條現存 404 → 授權即修（#1 re-point / #2 deprecate）→ band-aid cleanup → Leonard 真檔 PDF 收貨揭發精準度問題 → KG-tagging 修復 → CI 啟用驗證 → 收工。
3. Completed（詳見 SESSION_LOG S172）:
   - ✅ **served-URL 健康檢查（Method B 監察）**：`dev/source/check_served_urls.py` + `.github/workflows/served_url_check.yml`（self-test 21 PASS；CI run #1 conclusion=success、198/200/0 broken；每週一 11:00 UTC 自動跑生效）。
   - ✅ **2 條現存 user-facing 404 即修**：#1 `edbc12_2025_ph_pri` re-point（Supabase UPDATE 10 chunks → registry 200 URL、url-only）；#2 `sch_calendar_guide` deprecate（DELETE 6 + registry status→deprecated + hr_admin SOURCE_SET dead-ref 移除）。served-URL 重掃 **198/198 OK**。
   - ✅ **band-aid cleanup**：移除 app.html+mobile.js `SOURCE_URL_FIXUPS`（SAG store 已永久修好、verified no-op）。
   - ✅ **文件標註真檔收貨 + 精準度修復**：curriculum 76 KG-source 清單項（kgecg_2017+g29）tag `['kindergarten']` + 重生 bundle；live 驗 primary 580→504、KG 污染 0、課業項浮現、SAG p199 命中。
   - ✅ Supabase **15,336→15,330**（deprecate −6）+ display-sync 8 點；playbook proposal deposited（repo `8bccdbc`）。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: 真 .docx 收貨「保留格式」→ 文件標註精準度 monitor → EDB monitor-driven 入庫。
6. Risks: 🟢 HEAD==origin/main（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455·guidelines 158）；display-sync 完整（chunks **15,330**）。⚠️ 文件標註 narrow×broad missing 噪音（非 KG、已修 KG 部分、monitor）+ 短 PDF 分段偏粗。⚠️ Render free-tier cold-start ~50s + auto-deploy 偶爾卡（要手動 Deploy latest commit）。
7. commits（已 push origin/main）: `4b68f97`(①②)→`b2ab8a2`(③)→`f38b511`(④)→`f1bafc6`(④ live)→`2626e8c`(CI 驗)+本 closeout commit。live Supabase PATCH(10)+DELETE(6)（Leonard 授權）。playbook repo `8bccdbc`。

## Previous Session Record (S171)
1. UTC date: 2026-06-17
2. Session ID: Claude_20260617_0911 (S171) — session 開喺頂層 umbrella root → Leonard「每次一開 session 都行 Draft」→ 設頂層 redirect-only → 重開通告分析入口 → DEBP 6 源入庫 + 路由 + 首頁更新日誌 → 指引庫正名數字教育 + 收錄 DEBP → 跨範疇 also_in → 收工。
3. Completed（詳見 SESSION_LOG S171）:
   - ✅ 頂層 umbrella root 設 **redirect-only**（非 git；頂層 `dev/SESSION_HANDOFF.md` + `START_NEXT_SESSION_PROMPT.txt` 指向 Draft，免再撞 onboarding 空殼）。
   - ✅ 重開「EDB 通告分析系統」入口連結（`index.html` 還原 S154 停用；URL 301→circular.wongfu.net 200 verified）。
   - ✅ **DEBP 6 源入庫 Channel B**：4 文字層（`fetch_extract`）+ 2 OCR（`ocr_extract` gpt-4o，draft 質、各 1 illegible region）→ canonical chunker（未改）→ 209 chunks → live INSERT（Leonard 授權「6 源全部入」、INSPECT before/after）→ Supabase **15,127→15,336**；新 `digital_education` route（`detectQueryCategory` 16/16、Render live DEBP query **8/8 全 debp_***）；registry +6=**225 源**。
   - ✅ 首頁「資料庫更新日誌」icon+modal（root `update_log.json`、XSS-safe DOM、dot=未讀最新）。
   - ✅ 指引文件庫分類「資訊科技」正名「數字教育」+ 收錄 DEBP 6 份（`build_guidelines.py` regen `guidelines.json` v2.5.0→**2.6.0**、公開 152→**158**、app 161→**167**、it/數字教育 1→7）。
   - ✅ 指引庫跨範疇 `also_in`（12 份多類顯示：SEN/資優→學生事務、校曆/g28→行政、DEBP→課程；科目安全 g21/g22/g23 **只課程**；全部 unique 不變、純 UI、下游契約零改）。
4. Pending: 見 Open Priorities 🔜 NEXT。
5. Next priorities: served-URL 健康檢查 → band-aid cleanup → Leonard 真機/真檔收貨。
6. Risks: 🟢 HEAD==origin/main `e5053e8`（已 push、tree clean、0 outstanding bug）。🟢 凍結合約零接觸（`_meta` 2.3.0·facts 455）；display-sync 完整（chunks 15,336 + guidelines 158）。⚠️ DEBP 2 OCR 補充 draft 質 + 主藍圖 ~16 圖像頁無文字層（monitor、命中可補 OCR）。⚠️ `digital_education` route 真查詢待觀察。⚠️ 監察 served-URL 盲點待補（NEXT ①）。⚠️ Render free-tier cold-start ~50s。
7. commits（已 push origin/main）: `972ab78`(重開入口)→`da33b8c`→`10bd47f`(route)→`9e51b6f`(DEBP+更新日誌+display-sync+registry+6 vault)→`4d0f3a6`→`beddcd8`(指引庫正名+DEBP 6 份)→`4b3985b`→`6488b44`(跨範疇 also_in)→`e5053e8`(治理)。Supabase live INSERT 209 chunks（Leonard 授權）。頂層 redirect 檔=本地非 git。

## Previous Session Record (S170)
1. UTC date: 2026-06-15
2. Session ID: Claude_20260615_2123 (S170) — 「開工」→ 起手探針全綠 → ④ Phase 0 唯讀爬取 → 監察 email 主題 → 揭發學校行政手冊 404 → 清訊號 + 404 兩層修 + v3.2.0 封版 + 收工。
3. Completed（詳見 SESSION_LOG S170）:
   - ✅ **① 監察清訊號**（`eb9d90b`）：freshness write-sync 重 seed 全 215 baseline（假警報 9→0、修 stub-baseline artifact：舊 1–3KB 殼頁 vs 新 multi-MB PDF + Last-Modified 倒退）；discover `ENUMERATION_PAGE_CAP=25`（likely-real 680→223、no-loss、self-test +3 PASS）。
   - ✅ **② 學校行政手冊 404 兩層修**（`59b8d2b` + Leonard Supabase UPDATE）：前端 `SOURCE_URL_FIXUPS` 改寫畸形 URL（app.html+mobile.js）+ Supabase 383 `sag_2025_11` chunks url index.html→SAG_C_markup.pdf（url-only、verified live API 回 `.pdf`）。根因 registry↔store drift、範圍 SAG-only。
   - ✅ **③ 平台 v3.2.0 正式版**（`6309333`）：PLATFORM_VERSION 3.1.0→3.2.0 + README badge/footer + CHANGELOG。凍結 knowledge.json `_meta` 2.3.0 不動。headless boot 驗 v3.2.0、無 stale 3.1.0。
   - ✅ **④ EDB 每週監察 email**：核實 GitHub Actions 真有跑（freshness 12 次、discover 今日首次）；Leonard 設好 Watch→Issues（#1/#2 每週一 email）。
   - ✅ **⑤ playbook 沉澱**（repo `7057db8`）+ **⑥ ④ 全入庫 triaged ＝無乾淨批次值得入 → monitor-driven on-demand**。
4. Pending: ① served-URL 健康檢查（404 盲點 follow-up）；② band-aid cleanup（Supabase 已修、可移除 `SOURCE_URL_FIXUPS`）；③ Leonard 真機/真檔收貨 S169 ①②③；④ EDB 入庫 monitor-driven。
5. Next priorities: 見 Open Priorities 頂部 🔜 NEXT 區塊。
6. Risks: 🟢 HEAD==origin/main `6309333`（已 push）。🟢 清訊號/版本/前端純改、零接觸 backend/凍結合約（_meta 2.3.0·facts 455·guidelines 152）；Supabase 只 SAG **url-only** UPDATE（chunk 數 15,127/_meta/display-sync 不變、非 count 變故無需 7 點同步）。⚠️ band-aid redundant-but-harmless（Supabase 已修、留住做雙保險）。⚠️ S169 ①②③ 仍待真機/真檔收貨。⚠️ 監察 served-URL 盲點待補（見 NEXT ①）。⚠️ Render free-tier cold-start ~50s。
7. commits（**已 push origin/main**）: `eb9d90b`(清訊號) → `59b8d2b`(404 band-aid) → `6309333`(v3.2.0 release) → `5186d0f`(收工治理) → `0ff1925`(RAG 架構圖入庫) → `35458c7`(README ASCII truth-pass)。playbook repo `7057db8`。Supabase：Leonard UPDATE 383 `sag_2025_11` url（verified live）。

## Previous Session Record (S169)
1. UTC: 2026-06-15 | Claude_20260615_S169
2. 文件標註乾淨成品版「保留格式」+改動摘要（`2150f59`）+ onboarding 6 步導覽（`12f33fb`）+ in-app 使用手冊+FAQ（`12f33fb`）+ dead-code cleanup app.html −464（`967dd7d`）。純前端、Node builder 32/0 + headless boot 驗；QC PASS-with-flags（no blocker）。詳見 SESSION_LOG S169。

## Previous Session Record (S161)
1. UTC date: 2026-06-14
2. Session ID: Claude_20260614_S161 (S161) — 全權自主
3. Completed: 「文件標註」合併主線 Phase 1 SHIPPED LIVE（合併 文件分析+文件修訂 → 📝 文件標註 tab；新 annotateDocument.ts + /api/annotate-document；app.html AnnotatePanel + buildAnnotatedOriginalDocx〔JSZip highlight + w:ins 追蹤修訂 + 附錄 + header〕）+ Leonard 真檔 4 輪反饋全修。commits `6885dbe`→`9b1f6a5`+gov 全 push。詳見 SESSION_LOG/archive。

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


## State Reconciliation Check

- **Reconciled at:** 2026-06-24 (S180 closeout)
- **State sections rewritten or confirmed current:** Current Baseline（S179 → S180 reconciled block：HEAD `2acf631`、Supabase 15,414、footnote_curated 84、v3.2.1；SAG 2026-05 核對 LIVE；dedup side-finding resolved；數字以該 block 為準）；Open Priorities 🔜 NEXT（SAG 版本核 flag → ✅ done、dedup → resolved、公開指引 sync 已記）；Backlog（加雲端 OCR 引擎選項）；Last Session Record（改寫為 S180、S179 降為 Previous Session Record）；Next Session Opening Message（generic startup prompt 不變）。
- **Stale snapshots left:** 無。Current Baseline 頂 S180 reconciled block = 準數字（15,414 / footnote_curated 84 / v3.2.1 / guidelines.json 2.6.1 公開 158）；下面 S179 及累積 baseline 段為歷史背景（已明標）。
- **Lifecycle conflicts resolved:** SAG 版本核（S179 NEXT flag）→ S180 confirmed + 已修（overlay+registry+公開指引三邊一致），由 next-priority → done；SAG 雙 ingest dedup（S180 side-finding）→ 同 session 調查 resolved（soft-dedup 足夠、無需 hard-dedup）；B（OCR brief）= 評估完成、引擎事實袋低；無已完成項殘留為未解 next priority／active risk。discovery 餘下 8 角度 + playbook push = 新 open follow-up（明標）。
- **Persistence routing checked:** 是。當前狀態→handoff Current Baseline + Last Session Record；session trace→SESSION_LOG S180；reproducible ingest→`dev/ingest_sag_373_overlay.py`；OCR 引擎參考→handoff Backlog + playbook inbox 提案；sync 義務→下方 Sync Status + DOC_SYNC_REGISTRY。CODEBASE_CONTEXT 無改（零 backend code/stack/service 變；純 data overlay + registry/display 文字 + 一次性 script）。SESSION_LOG S170 archived → `dev/archive/SESSION_LOG_2026_Q2.md`（保留 S171–S180 共 10 entries）。
- **Opening message matches current state:** 是（HANDOFF generic opening + SESSION_LOG S180 state-rich prompt；START_NEXT_SESSION_PROMPT.txt 已 regen、與 opening message 一致）。
- **Sync Status:** SAG §3.7.3 overlay = confirmed（Supabase 15,414、footnote_curated 84、Render live verify overlay rank-1 + grounded）；registry version_label sag_2025_11/g24→2026-05 = confirmed（git diff 6 行）；公開指引 title sync = confirmed（guidelines.json 2.6.0→2.6.1、公開 158 不變、+ app.html、Pages auto-deploy）；display-sync chunks 15,414 = confirmed（7 檔 + CHANGELOG）；Backend code = 零改 confirmed；凍結合約 = 零接觸 confirmed（`_meta` 2.3.0/facts 455、無 PLATFORM_VERSION bump）；playbook 提案 = local commit `ead3749`、未 push（pending Leonard）。

`SESSION_LOG.md` carries recent evidence. do not create an archive directory by default. The next AI can continue from `AGENTS.md`, this handoff, `dev/PROJECT_INDEX.md`, and needed rule packs without searching old log history. See `dev/DOC_SYNC_REGISTRY.md`.

<!-- ack:section:handoff-sufficiency-check -->
## Handoff Sufficiency Check

Can the next AI continue from `AGENTS.md`, this handoff, `dev/PROJECT_INDEX.md`, and needed rule packs without searching old log history?

Answer: Yes.
If no, update this handoff before closeout.

Continuity rule: this file carries current state and next action. `dev/SESSION_LOG.md` carries recent evidence only. Archive old detail only when needed; do not create an archive directory by default.

<!-- ack:section:next-session-opening-message -->
## Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read in order:
1. AGENTS.md
2. dev/SESSION_HANDOFF.md
3. dev/SESSION_LOG.md
4. dev/PROJECT_INDEX.md
5. dev/RULE_PACKS.md

Read dev/DOC_SYNC_REGISTRY.md before file changes or closeout.

If this root does not match the expected project root, stop and ask for confirmation.

Before changing anything, tell me the current state and your recommended next step.
```

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
