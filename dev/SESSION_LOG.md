# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-15 Session 164 — Mobile 範本下載 入口（桌面版功能標示 + 截圖示意）+ README/docs 更新

- **ID:** Claude_20260615_S164
- **Trigger:** 開工切 Draft active root（頂層 dormant scaffold，已向 Leonard 確認切去 Draft）。起手核實全綠：policychecker.wongfu.net /app.html HTTP 200 + PLATFORM_VERSION v3.0.0（S163QC Pages 404 已恢復）、HEAD==origin/main `d0322b9`、Render /health 200 cache_a 455、範本 docx 喺 Pages 可達（safety 學校版 docx HTTP 200/49,777 bytes）。Leonard 三項指示：① GitHub README 要更新 ② mobile 加範本下載 icon ③ 文件標註留 desktop 版本；經 AskUserQuestion 釐清範本手機畫面 = 「標示桌面版功能、不提供下載、放一個截圖」。
- **PLAN（HIGH-risk，已 Leonard 確認）:** 純前端 mobile shell + 文檔；不碰 desktop app.html / backend / Supabase / 凍結 JSON 合約。
- **CHANGE:**
  - `mobile.js`（commit `0057dfe`）：bottom-nav `TABS` 3→**4** entries（🔍搜尋/📚指引文件/📋範本下載/ℹ️平台介紹）+ active-state 邏輯；init 加 `#templates` 分支（置於 search 預設之前，避免 `hash!=='#guidelines'` 誤吞）；新 `buildTemplatesShell()` = 純靜態畫面（💻桌面版功能 badge + 「範本為可編輯 Word，需電腦下載編輯」說明 + `templates-preview.png` 截圖 figure，`<img onerror>` 優雅隱藏）。利用既有 `hashchange→location.reload()`（mobile.js:676）令切 tab 重建 shell。
  - `mobile.css`：+`.m-tpl-*` 樣式（沿用 `--m-*` token + `.m-guide-head` 風格）。
  - `templates-preview.png`（root，新資產）：headless Chrome 截 desktop `app.html#templates` 範本面板 @2x（2360×2048，335KB）。
  - 文件標註：維持 **desktop-only**，mobile shell 不設入口（符合 Leonard 原意）。
  - 文檔：`README.md`（+響應式/手機版範圍表、日期 2026-06-15）/`CHANGELOG.md`（v3.0.0 +S164 Changed bullet、P6 改「文件標註 為 desktop 功能」）/`PROJECT_MASTER_SPEC.md` §B.5（改寫 4-entry nav + 範本桌面導引 + annotate desktop-only）/`CODEBASE_CONTEXT.md`（AI log + Directory Map）/`DOC_SYNC_CHECKLIST.md`（新增「Mobile shell scope / bottom-nav 變更」row）。
- **QC（全 PASS）:** `node --check mobile.js` ✓。**headless Chrome `--dump-dom`（fresh process，bypass 快取 = 權威）核實 mobile `app.html#templates`：** `m-tpl-shell` present ✓ / 「桌面版功能」badge ✓ / `templates-preview.png` img 引用 ✓ / `.m-tab` count = **4** ✓ / `mobile-shell-active` ✓ / 文件標註**不在** mobile nav ✓。**回歸：** `app.html`（search）+ `app.html#guidelines` 兩畫面仍 4-tab、mobile-active、含範本 tab ✓。**desktop 零接觸：** `git status` 證只改 mobile.js/css + 4 docs + 新 png；`app.html`/`index.html`/`backend/` 無 diff。desktop 範本面板截圖視覺確認（5 tabs、校類 filter、各範疇下載鈕齊）。Supabase 15,109 零接觸、無版本 bump（PLATFORM_VERSION 仍 3.0.0）。
- **Evidence disposition:** kept as recent trace evidence；reusable lesson（mobile #hash 畫面 + desktop-only 功能呈現）已入 DOC_SYNC row + PROJECT_MASTER_SPEC §B.5。
- **⚠️ Note:** Claude Preview 工具因 `mobile.js` 為 subresource（無 query）而 cache 住舊版（顯示舊 3-tab）— preview 工具快取怪癖，**非真站問題**（GitHub Pages 送正確 cache header；新碼從未被任何真用戶 cache）；headless fresh render 為權威核實，故採用之。乾淨手機視覺截圖因 headless 首次 role-picker overlay + `--user-data-dir` profile 建立卡死而未取（環境問題，與功能無關；DOM dump 已完整證實 tpl shell 正確建於 overlay 之下）。
- **Boundary:** 純前端 mobile shell（手機 ≤640px / mobile UA 先觸發）+ 文檔。desktop 體驗、backend、Supabase、凍結資料合約全不受影響。
- **commits（feature 已 commit，待 push）:** `0057dfe`（mobile.js/css + templates-preview.png + 5 docs）→ 本治理 commit。
- **Log maintenance (§4a):** SESSION_LOG 加 1 entry，總行數 <400、oldest <30d，no-op（無 archive 觸發）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Render backend live；Pages live（v3.0.0）；0 outstanding bug。起手 verify：探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109。

S164（2026-06-15）完成（純前端 mobile shell + 文檔，desktop/backend/Supabase/凍結合約 零接觸）：
- mobile 底部導航 3→4 入口（+📋範本下載 #templates）；該手機畫面 = 「💻桌面版功能」標示 + 說明 + 桌面範本面板截圖示意（templates-preview.png，img onerror 優雅隱藏），不提供實際下載（學校版範本為可編輯 Word 檔需電腦用）。文件標註維持 desktop-only（手機不設入口）。
- README +響應式/手機版範圍表；CHANGELOG v3.0.0 +S164 bullet + P6 改「文件標註 為 desktop」；PROJECT_MASTER_SPEC §B.5 改寫；CODEBASE_CONTEXT/DOC_SYNC 同步。
- 核實：headless Chrome --dump-dom（fresh，bypass 快取）mobile DOM 全綠（m-tpl-shell/桌面版功能 badge/templates-preview.png img/4 nav tabs/mobile-active/annotate 不在 nav）；search+guidelines 回歸 4-tab；desktop 零 diff。commit 0057dfe。

NEXT（優先序，多數待 Leonard）：
① 真機驗 mobile 範本下載（iPhone/Android Safari/Chrome）：4-tab 導航排得落、範本畫面截圖清晰、文件標註手機無入口；確認後收貨。
② Leonard 收貨 v3.0 6 fixes（S163QC，已全 live 驗）→ 正式封 v3.0。
③ Render 免費 tier cold-start（閒置 15min 瞓 → 第一搜尋 ~50s）：production UX 痛點，考慮升 always-on 付費 tier 或加載入中 UX。
④ 真檔驗：Phase 2 PDF inline highlight 真 PDF 對位+多 viewer CJK；P3 gate 真檔多範疇覆蓋率 monitor（STOPWORD_DF_FRACTION=0.25/COVERED=0.5/PARTIAL=0.42/MAX_ITEMS=400 tunable）。
⑤ monitor：P2 KG routing 真用戶查詢；Phase 2.5 多範疇 UX；KG QC DRAFT 最終核；#3 學校版 102 docx review；here.now 鏡像保留/換 slug/綁 domain。

Key files（S164）：mobile.js（TABS 4 entries + #templates branch + buildTemplatesShell）/ mobile.css（.m-tpl-*）/ templates-preview.png（root 資產）/ README.md / CHANGELOG.md / dev/PROJECT_MASTER_SPEC.md §B.5 / dev/CODEBASE_CONTEXT.md / dev/DOC_SYNC_CHECKLIST.md。
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；改 docx/checklist re-run gen_checklists_bundle.py+gen_templates_manifest.py（kg_operation canonical si/section_name）；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；本機 shell set -e（grep -c 0 中斷用 python 數）；改範本面板外觀記得重截 templates-preview.png；mobile.js 改動用 headless Chrome --dump-dom（fresh）核實，勿信 Preview 工具快取。改 host/CORS：env.ts BASELINE_CORS_ORIGINS exact origin 無尾斜線；repo 勿 set private（會 down free Pages + Render deploy）。
Post-startup first action: 探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109，然後問 Leonard：真機驗 mobile 範本下載 收貨 / 起邊個 NEXT。
```

---

## 2026-06-14 Session 163 QC — v3.0 release QC：6 blockers NO-GO→GO（P1–P6）+ regression 修復

- **ID:** Claude_20260614_S163QC (S163 QC follow-up)
- **Trigger:** Leonard 22:40 自啟（全權跟進 QC Governor 的 v3.0 NO-GO 裁決，醒來收貨）。實際 machine-local 23:11 BST 過咗 22:40 → 起動。起手核實：HEAD `04602b3`==origin、Render `/health` ok(cache_a 455)。baseline regression 揭 **2 條 pre-existing FAIL**（stale）。
- **P1 版本顯示（`3f239bf`）:** app.html header（政策核對·{displayVersion}）+ footer 嘅 `displayVersion` 原由 `data._meta.version`(2.3.0) 派生 → 改用 `PLATFORM_VERSION`(v3.0.0)。`_meta.version` 維持凍結。local preview 驗 header/footer v3.0.0、無 v2.3.0、0 console err。
- **P2 KG 營運搜尋（`39e6df1`）:** root cause —「幼稚園營運」唔 match kg_admin regex（有 營辦 無 營運）→ 落 curriculum → 只得 g26。修：kg_admin regex +幼稚園.{0,4}營運|營運手冊|運作|健康紀錄 等。export `detectQueryCategory`。**Render LIVE 驗**：query「幼稚園營運 手冊 健康紀錄」由 total=2(g26×2) → total=5 含 kg_operation_manual_2026+kg_admin_guide_2026。kg_admission 不受影響。
- **P3 標註覆蓋誇大（`39e6df1`）:** root cause — status 純 max-cosine；text-embedding-3-small 對同範疇中文政策句俾 0.42–0.5 cosine 即使主題無關 → 1 句短文標到 covered=20/partial=55。修：graded 詞彙重疊閘 —— 每 item 取 informative CJK-bigram（DF≤25% 自校準濾走 本校/幼稚園 等通用詞），與最匹配段共享 0→missing、1→最多 partial、≥2→保留 cosine 判定。`MAX_ITEMS` 220→400（kg_operation 388 全評分零截斷）。export `cjkBigrams`。**Render LIVE 驗**：短 KG 文 covered=5/partial=30（QC 報 20/55）；real-embedding e2e 證 richer 多段文 covered=37（無 false-negative）。
- **P4 README（`3f239bf`）:** badge v3.0.0 + knowledge.json 凍結 2.3.0 註明 + footer 日期。
- **P5 worktree（`3f239bf`）:** 8 個 untracked 備份／中間檔（`*.bak_*`/`*.pre_*`/`_distill_*`/`_rewrite_*`，含 21MB all_chunks bak）`.gitignore`，**不刪**（無批准）。驗證全部 ignored、worktree 乾淨。
- **P6 Mobile scope（`3f239bf`）:** 決定 + 文檔（QC option 1）。mobile.js shell 為 search/guidelines 導向、annotate/templates 無對應 mobile render（硬接會 search shell 蓋 React = 破 UX）。v3 mobile scope = 搜尋/指引/平台介紹；文件標註+範本下載 = desktop 功能。PROJECT_MASTER_SPEC §B.5 + CHANGELOG 寫明。
- **Regression 修復（`39e6df1`）:** 2 條 stale FAIL 修正（schema 版本硬編 1.3.1 → 現凍結 2.3.0/2.5.0；role-bucket distinctness 已隨 S110 dedup union-selector 失效 → 改斷言「兩角色均取得 finance 事實」）+ 加 P2 routing(5)/P3 lexical-gate(4) cases。20 PASS / 0 FAIL（1 PASS-with-notes = offline OpenAI）。
- **QC：** tsc check+build exit 0（×2）；regression overall PASS；Render LIVE 探針（P2 routing + P3 covered/partial）全綠；app.html local preview（P1 + 0 console err）。
- **⚠️ Boundary / open:** **GitHub Pages 全站 404**（closeout 時 root+index+app 兩域皆 404；DNS→Pages IP 185.199.108.153；files 仍 tracked、.nojekyll 在、deploy-from-branch 無 Actions workflow → 非 content 造成；private repo 令 raw/API 亦 404 無法查 build log）。研判為 Pages deploy delay/incident，非我 push 引致（root 都 404）。**frontend P1 propagation 待站恢復**；後台 poll 監察中。Render backend 改動已 LIVE。Supabase 15,109 零接觸。
- **commits（已 push origin/main）:** `39e6df1`(backend P2/P3/regression)→`3f239bf`(frontend/docs P1/P4/P5/P6)→ closeout gov。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Render backend live。⚠️ 起手 FIRST：探針 https://policychecker.wongfu.net/ + /app.html HTTP code —— S163QC closeout 時全站 404（Pages deploy delay/incident，非 content；root 都 404、files tracked、.nojekyll 在）。若仍 404：check GitHub Pages 部署狀態（私庫，需 gh auth 或 GitHub web Settings→Pages 睇 build log）/ GitHub Status / 試 empty commit re-trigger；恢復後驗 app.html header/footer 顯示 v3.0.0。若已 200：直接驗 v3.0.0 即可。再 verify HEAD==origin/main + Supabase 15,109 + Render /health。

S163QC（Leonard 全權，22:40 自啟）完成 v3.0 release QC 6 blockers（NO-GO→GO）：
P1 版本顯示一致（3f239bf）：app.html header/footer displayVersion 由 PLATFORM_VERSION（v3.0.0）派生，唔再讀凍結 _meta.version（2.3.0）。local 驗過，待 Pages 恢復做 live 驗。
P2 KG 營運搜尋（39e6df1）：searchChannelB kg_admin route +幼稚園營運/營運手冊/運作/健康紀錄。Render LIVE 驗：query surface kg_operation_manual+kg_admin_guide（原 g26-only）。
P3 標註覆蓋誇大（39e6df1）：checklistRevise graded 詞彙重疊閘（informative bigram DF 自校準）+ MAX_ITEMS 220→400。Render LIVE 驗：短 KG 文 covered 20→5/partial 55→30，richer 文 covered=37（無 false-neg）。
P4 README v3.0.0 / P5 .gitignore 備份檔(不刪) / P6 mobile scope 文檔（search/guidelines/about；annotate+templates=desktop，PROJECT_MASTER_SPEC §B.5）。
Regression（39e6df1）：修 2 stale FAIL（schema 1.3.1→2.3.0/2.5.0；role-bucket→union both-roles）+ P2/P3 cases。20 PASS/0 FAIL。

NEXT（優先序）：
① ⚠️ Pages 404 復原驗證（最優先）：站恢復後 live 驗 app.html v3.0.0 header/footer + index.html + 文件標註/範本下載 tabs 無 console error。若長時間未復，flag Leonard 查 Pages settings/GitHub status。
② Leonard 收貨：v3.0 QC 6 fixes（其中 P2/P3 Render 已 LIVE 驗、P1 local 驗）。確認後 v3.0 可 NO-GO→GO。
③ 真檔驗：Phase 2 PDF inline highlight 真 PDF 對位+多 viewer CJK；P3 gate 真檔多範疇文件覆蓋率合理性 monitor（STOPWORD_DF_FRACTION=0.25 / COVERED=0.5 / PARTIAL=0.42 / MAX_ITEMS=400 tunable）。
④ monitor：P2 KG routing 真用戶查詢覆蓋；Phase 2.5 多範疇 UX；KG QC DRAFT 最終核；#3 學校版 102 docx。

Key files（S163QC）：backend/src/api/{searchChannelB.ts(kg_admin regex +營運; export detectQueryCategory), checklistRevise.ts(graded lexical gate +cjkBigrams export, MAX_ITEMS 400, STOPWORD_DF_FRACTION)} / backend/scripts/semanticRegression.ts(2 stale fixes + P2/P3 cases) / app.html(displayVersion→PLATFORM_VERSION) / README.md / .gitignore / dev/PROJECT_MASTER_SPEC.md(§B.5 mobile) / CHANGELOG.md.
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；改 docx/checklist re-run gen_checklists_bundle.py+gen_templates_manifest.py（kg_operation canonical si/section_name）；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；本機 shell set -e（grep -c 0 中斷，用 python 數）；curl policychecker 偶被 Cloudflare challenge（9KB page）→ 用 github.io origin 或加 ?cb=。
Post-startup first action: 探針 policychecker.wongfu.net / + /app.html HTTP status（Pages 恢復未）；若 200 → live 驗 v3.0.0；若 404 → 跟 NEXT① 處理。然後問 Leonard 收貨 v3.0 QC。
```

---

## 2026-06-14 Session 163 — ABC：核 KG QC（+修 S162 schema bug）+ 文件標註 Phase 2.5（per-segment）+ 平台 v3.0 改版 + 文件標註 Phase 2（PDF inline highlight）

- **ID:** Claude_20260614_S163 (S163)
- **Trigger:** 開工切 Draft active root。起手核實全綠（HEAD `8f18f5a`==origin/main、Supabase **15,109**、`/api/checklist-domains`=15 域含 kg_operation、範本下載 live 見幼稚園營運卡）。Leonard：「ABC」= 做晒 3 個 NEXT（C 核 KG QC / A Phase 2.5 / B Phase 2）+「平台簡介及首頁、version number 應該都在改變中，規劃一下」；全權自主、慳 token、中斷則 22:40 續。排序 C→A→版本/首頁→B（有界先、最重 B 留尾、每件獨立 commit）。
- **C — 核 KG QC（`ef43517`）:**
  - `dev/checklists/kg_operation/QC_VERIFY_ISSUES.md` 17 flags 全修：`_qc_fix.py`（exact-match + assert，全通過）刪虛構鋪墊／目的句（ch1 木地板、ch2 洗手間框架、ch5×3、ch13 註冊費 carve-out、ch15 廉潔問責、ch9 指派專人、ch6 註冊醫生/每日/方可入班）、補漏義務（ch6 體溫移回 covering clause、ch13 廉署守則範本+調查完結後匯報、ch9 還原留宿/獨立中心適用主體）、移除錯引用（ch6 p47）。
  - **深挖揭發並修 S162 結構 bug：** kg_operation/clauses.json 用非標準 schema `section_no/name`，而 14 既有域 + `gen_school_docx.js`/`gen_checklist_docx.js` + backend `checklistRevise` 全期望 canonical `si/section_name`。後果：(1) `gen_checklists_bundle.py` 讀 `ch.si`→`None` 令 backend supplement linkage（`c.si===f.sectionIdx+1 && covers.includes(localIdx)`）對 kg_operation **全失效**（offline 模擬：修前 0/388、修後 **388/388** items 拎到 clause）；(2) `gen_school_docx.js` 讀 `SECNAMES[ch.si-1]`→undefined → 學校版 docx **20 章名全空**（似 S159 undefined bug）。正規化 schema、重生 4 docx（章名齊）+ bundle（si=1–20）+ manifest。
- **A — 文件標註 Phase 2.5（`d71ae1e`）:** `checklistRevise.ts` +`detectDomainsPerSegment`（per-segment argmax 路由：每段路由其單一最佳域，域以 segment 勝數入選——top ≥1、secondary ≥`SECONDARY_MIN_SEGMENTS=2`）；`annotateDocument.ts` 改用之、`AUTO_DETECT_MAX_DOMAINS=3`（原硬 1）。`detectRelevantDomains` 保留（unused）。真 OpenAI e2e（直接調 detector）：maths→curriculum 單域（**legacy whole-doc 誤判 qa_inspection**）、SEN+gifted doc→兩域、primary scoping 排除 kg_operation、empty→[]。前端 `report.domains.map` 已支援多域，零 UI 改。tsc/build PASS；Render 部署後驗 SEN doc→['sen'] 21 findings。
- **版本+首頁+平台介紹（`f510ee8`）:** Leonard 要求改版號＋首頁＋平台簡介。**決定：decouple** user-facing `PLATFORM_VERSION='3.0.0'`（app.html 常數）與凍結 `knowledge.json` `_meta.version`（維持 2.3.0，455-fact Channel A 凍結+下游 Circular System 合約不動）。v3.0 標誌平台由純搜尋→完整合規套件。app.html 平台介紹 channels 改 5 卡（政策語義搜尋/文件標註/範本下載/指引文件庫/通告分析）+ hero 文案 + 版本徽章用常數；index.html +文件標註+範本下載 feature 卡 + v3.0 eyebrow + hero broaden + meta；CHANGELOG v3.0.0 平台 entry。browser-verify：index static 6/6、app desktop 5 卡+v3.0.0 徽章+0 console err（desktop PlatformIntroPanel 喺 DOM，preview innerWidth=0 只係疊咗 mobile CSS）。
- **B — 文件標註 Phase 2 PDF inline highlight（`7289380`）:** +pdf-lib 1.17.1 CDN；`extractPdf` 改返 `{text, pages}`（per-page pdf.js text-item 座標，PDF user space 原點左下=同 pdf-lib，無旋轉頁免 viewport transform；text 餵 backend 不變）；handleFile 為 PDF 都設 fileBuffer+pdfPages。新 `buildAnnotatedPdf`：whitespace-insensitive char→item map 定位 span → 每行一條黃色 highlight rect + 編號 marker（Helvetica ASCII）+ CJK sticky-note 批註（`PDFHexString.fromText` UTF-16BE，**免嵌 ~10MB CJK 字型**——viewer 用自己 UI font render /Contents）；missing 項（無 span）留 on-screen/清單。`handleDownloadOriginal` branch docx/pdf；button label + hint 改。**in-browser pipeline e2e**（合成 PDF→pdf.js 抽座標→buildAnnotatedPdf 核心）：span 定位✓、highlight box✓、annotation API✓、save valid PDF✓、round-trip `contentsObj.str`=CJK✓、0 console err。CJK 在 PDF 行不通（無嵌字型）→ note 全文喺 sticky-note + on-screen report + 建議清單。
- **QC（全 PASS）:** backend tsc check+build exit 0（×2）；真 OpenAI Phase 2.5 detection e2e（4 案）；in-browser pdf-lib pipeline e2e；browser-verify（index static + app desktop 5 卡 + 0 err）；KG supplement linkage 388/388 offline 模擬 + 9 clause text fix assert；docx 4/4 章名齊；**live 探針全綠**（Pages app.html v3.0.0+buildAnnotatedPdf+pdf-lib、index.html v3.0+2 卡、Render /api/annotate-document SEN→['sen']）。
- **Boundary:** 純前後端 feature + dev/checklists 修正 + 公開 root JSON 重生。**Supabase 15,109 零接觸**。平台版號 decouple = 自主決定（reversible，Leonard 可調 PLATFORM_VERSION）。
- **Doc Sync:** New user-facing feature/version → README（pending：可補 v3.0/PDF highlight）、CODEBASE_CONTEXT（Stack +pdf-lib、annotateDocument/checklistRevise +detectDomainsPerSegment、AI log）、CHANGELOG（v3.0.0）、SESSION_HANDOFF/LOG 已更；checklists_bundle.json/policy_templates.json 已 regen。
- **commits（全 push origin/main）:** `ef43517`(C)→`d71ae1e`(A)→`f510ee8`(版本/首頁/平台介紹)→`7289380`(B)→ closeout gov。
- **Log maintenance (§4a):** SESSION_LOG 242 行（<400），本 session 加 1 entry，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push，7289380）。Supabase 15,109；Channel B live；Pages+Render live 全綠；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 15,109。

S163（Leonard「ABC」全權自主）完成 4 項全 push + live 驗：
C 核 KG QC（ef43517）：QC_VERIFY_ISSUES 17 flags 全修（_qc_fix.py）+ 揭發並修 S162 結構 bug（kg_operation/clauses.json 非標準 section_no/name → canonical si/section_name：修 backend supplement linkage 388/388 由失效恢復 + 學校版 docx 章節名空白）。
A 文件標註 Phase 2.5（d71ae1e）：detectDomainsPerSegment（per-segment argmax 路由，top≥1/secondary≥2，AUTO_DETECT_MAX_DOMAINS=3）取代 whole-doc detect；多範疇文件各段路由其域、單範疇仍 1 域、比 legacy 更準。Render 驗 SEN→['sen']。
版本/首頁/平台介紹（f510ee8）：PLATFORM_VERSION='3.0.0' decouple（凍結 knowledge _meta.version 2.3.0 不動）；app.html 平台介紹 5 channels + index.html +文件標註+範本下載 卡 + v3.0 eyebrow + CHANGELOG v3.0.0。
B 文件標註 Phase 2 PDF inline highlight（7289380）：+pdf-lib 1.17.1；extractPdf 抽座標；buildAnnotatedPdf 原 PDF 就地螢光 rect+編號 marker+CJK sticky-note（UTF-16BE PDFHexString.fromText，免嵌字型）；download branch docx/pdf。in-browser pipeline 驗全綠。

NEXT（優先序，多數待 Leonard）：
① Phase 2 PDF highlight 真檔驗：合成 PDF 已驗，建議上載真 EDB／學校 PDF 試對位 + 多 viewer（Acrobat/Preview/Chrome）CJK sticky-note 顯示。座標假設無頁面旋轉（rotation 存未補償）、碎 run／表格命中率 = monitor。
② Leonard review：v3.0 版本方案（PLATFORM_VERSION decouple，可調）/ KG QC DRAFT 最終核（QC_VERIFY_ISSUES 17 已修）/ #3 學校版 102 docx（範本下載 tab）。
③ Phase 2.5 多範疇 UX monitor：auto 由 1→≤3 域，真檔觀察會否過多域（SECONDARY_MIN_SEGMENTS=2 / AUTO_DETECT_MAX_DOMAINS=3 tunable）。
④ monitor：門檻 COVERED=0.50/PARTIAL=0.42/AUTO_DETECT=0.38/auto missing cap 8 / kg_admin「幼稚園質素」→qa_inspection / 57014 free-tier / cgss rank 低。

Key files（S163）：backend/src/api/{checklistRevise.ts(+detectDomainsPerSegment), annotateDocument.ts(用之, AUTO_DETECT_MAX_DOMAINS=3)} / app.html(+PLATFORM_VERSION 3.0.0, 平台介紹 5 channels, +buildAnnotatedPdf, extractPdf 抽座標, fileBuffer/download branch docx/pdf, +pdf-lib CDN) / index.html(+文件標註+範本下載 卡, v3.0) / CHANGELOG.md(v3.0.0) / dev/checklists/_work/kg_operation/clauses.json(si/section_name 正規化+17 fix, _qc_fix.py) / dev/checklists/kg_operation/(4 docx 重生 + QC_VERIFY_ISSUES.md) / checklists_bundle.json + policy_templates.json(重生).
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；新源 SOURCE_SETS+registry+display-sync 7 點；改 docx/checklist re-run gen_checklists_bundle.py + gen_templates_manifest.py（kg_operation 用 si/section_name canonical schema）；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；本機 shell set -e（grep -c 0 會中斷，用 python 數）。
Post-startup first action: verify HEAD==origin/main + Supabase 15,109 + 探針 onrender /api/annotate-document healthy + Pages app.html 見 v3.0.0，然後問 Leonard 起邊個 NEXT（建議 ① Phase 2 真檔驗 或 ② KG QC 最終核）。
```

---

## 2026-06-14 Session 162 — 幼稚園清單 pilot：新 kg_operation 範疇行勻 14-域 pipeline（distill→verify→rewrite→docx→manifest）

- **ID:** Claude_20260614_S162 (S162)
- **Trigger:** 開工切 Draft active root。起手核實全綠（HEAD `c0cffd3`==origin/main、Supabase **15,109**、`/api/annotate-document` live 探針 OK auto-detect 單域）。Leonard 答「4123」= 按 handoff NEXT 編號排序做晒四項：④幼稚園清單 pilot → ①跨校類 tagging → ②dead-code → ③Phase 2。全權自主。本條覆蓋 ④。
- **Completed ④（PLAN→READ→CHANGE→QC→PERSIST，HIGH-risk 全權授權直接執行）:**
  - ✅ **新範疇 `kg_operation`（幼稚園營運）行勻現有 14-域 pipeline**，用 S160 入庫嘅 2 源 `kg_operation_manual_2026`(217)+`kg_admin_guide_2026`(218)。範疇界定：營運/行政義務（校舍/安全/衞生/健康/膳食/人事/財務/註冊/家校溝通/紀錄）；收生留 `kg_admission`、課程留 `curriculum`，lens 明文剔除唔重抽。
  - ✅ **Step1 chunk**：新 `_build_kg_chunks.py` 用 canonical `build_wiki_index.chunk_text_with_page_carry` chunk 2 源 → merge 入 `_work/all_chunks.json`（14,674→15,109，chunk id `vault_*` byte-identical 同 live Supabase；backup 先）。
  - ✅ **Step2-4 distill**：`pipeline.py` +`kg_operation` domain+`batch_kg` → prep 8 buckets → **distill Workflow（15 agents：8 distill+verify+critic）→ 414 items** → mech-verify（3 級引文+頁碼重驗）→ **388 items**（31 dropped、109 page-fixed）。
  - ✅ **章節整合**：distill 自由命名 → 272 碎 section（211 單條）；用 1 mapping agent → 17 canonical chapter，再 keyword 拆財務 126→4 子章 → **20 章 / 388 items**（對齊現有域 11-14 章規模）。
  - ✅ **Step5 rewrite**：`mkflow-rewrite batch_kg` → **rewrite Workflow（20 章 → 162 校本條文 + 對抗覆核）**。⚠️ 首 run 中途撞 account session limit（ch12-20 fail）→ `resumeFromRunId` resume（cached ch1-11 即回、只重跑 9 章）全完成。
  - ✅ **覆核 17 issues**：自動修「法團校董會（未設者為校董會）」→「校董會」（幼稚園無法團校董會；10 處 text+12 處 adjustables）；其餘 16 軟性 fabricated/distorted-number 寫入 `kg_operation/QC_VERIFY_ISSUES.md` 供 Leonard／下次 QC 逐條核（似 14 域 S157 verify_issues 清理）。13/20 章覆核全清。
  - ✅ **Step6-7 docx+manifest**：gen 4 docx（學校版+清單 × 通用/幼稚園，全 PK+document.xml well-formed）→ re-run `gen_checklists_bundle.py`（14→**15 域**，+kg_operation 388 items/162 clauses，bundle 1564KB）+ `gen_templates_manifest.py`（+kg_operation 4 docx；`TYPE_SUFFIX`+`TYPE_RANK` 加「幼稚園」/kindergarten；total 106 docx）。
  - ✅ **app.html**：`TEMPLATE_TYPE_FILTERS` +`{key:'kindergarten',label:'幼稚園'}`（範本下載校類 filter）+ 範本下載 intro「14→15 個範疇」「小學/中學/特殊學校→+幼稚園」。**backend 零改**（detectRelevantDomains/checklist-domains 純 bundle-driven，自動拎新域）。
- **QC（全 PASS）:** backend `npm run check`+`build` exit 0（無 code 改、確認 bundle 唔破壞 build）；**真 OpenAI 本機 live e2e（:8787）**：`/api/checklist-domains`=15 域含 kg_operation(388)；`/api/checklist-revise` domain=kg_operation 出 covered/partial/missing；**`detectRelevantDomains` 真 KG 營運 doc auto-detect 淨「幼稚園營運」單域、零跨範疇**。**browser-verify（:8095）**：範本下載 tab、6 校類 filter（含幼稚園）、幼稚園 filter→只 kg_operation 卡+其幼稚園學校版 docx、intro「15 個範疇…幼稚園」、0 console error、screenshot 證。docx 4/4 well-formed。
- **Data note:** chunk id `vault_<sid>_<hash>` = canonical chunker、同 live Supabase 一致（pilot 純 dev/checklists 內部交付物 + 前端 filter，**Supabase 15,109 零接觸、無入庫**）。
- **Boundary:** 純前端 filter + 新 dev/checklists 交付物 + 根 checklists_bundle.json/policy_templates.json（公開 benign）。17 覆核 issues 中 16 軟性未修（DRAFT 草擬本、已 QC note 記錄、watermark「概以原文為準」）= follow-up。
- **commit ④:** `ec01e1b`（57 files；push origin/main）。
- **Completed ①（跨校類 tagging — domain-level school-type filter，HIGH-risk 全權執行）:**
  - **問題（S161 monitor）：** `okType` 對「無 school_types tag 嘅 clause」一律放行（untagged = applies-to-all），令型別專屬範疇（如 kg_operation 幼稚園專屬、kg_admission、placement 等，全部 item/clause 未逐條 tag）嘅條文喺用戶揀其他校類時照漏出。新增 kg_operation（全 untagged 幼稚園域）令此問題更明顯。
  - **修法（domain-level scope fallback）：** `_school_type_profiles.json` 已有逐域 `applies_to`（SSOT）→ `gen_checklists_bundle.py` 新增 `domain_school_types()`，把非「全 4 類」嘅域 emit 一個 **domain-level `school_types`** 入 bundle（kg_operation/kg_admission→kindergarten、placement/gifted→primary+secondary、sen/cpd/qa/school_governance→primary+secondary+special；全 4 類則 omit=all 向後兼容）。backend `okType(st, sel, domainSt)` 改 precedence：item/clause 自身 tag 優先 → 否則用 domain-level → 否則 all。`detectRelevantDomains` 加 `sel?` 參數，揀咗校類時**唔會 auto-detect 範疇外嘅域**；`annotateDocument` 傳入正規化 school_type。
  - **QC（真 OpenAI live e2e :8787，全 PASS）：** A) kg_operation+小學→**0 items**（正確排除）；B) kg_operation+幼稚園→full（5/26/189）；C) auto-detect KG doc+小學→揀「校務行政」（all-types）**唔揀 kg_operation**；D) +幼稚園→揀「幼稚園營運」。**Regression：** safety(all-types)+小學→42/38/89（未破）；kg_admission+小學→0（fix 一併生效）；省略 school_type+kg_operation→2/8/210（向後兼容）。tsc check+build exit 0。
  - **Boundary ①：** 純 backend filter 收緊 + bundle 加 domain-level field（additive；無 school_types 嘅 clause 行為對「省略 school_type」不變）。一併修正咗既有 6 個型別專屬域（placement/gifted/sen/cpd/qa/school_governance）嘅同類洩漏。
- **commit ①:** `5dde30f`（7 files；push origin/main）。
- **Completed ②（dead-code cleanup，app.html）:**
  - 移除 4 個已無 render 引用嘅死碼：`buildAnnotatedDocx`+`AnalyzePanel`（舊文件分析）、`buildRevisedDocx`+`ReviewPanel`（舊文件修訂）。**app.html 4345→3715 行（−630）。** 兩塊非連續（live `TemplatesPanel` + REVISE_SCHOOL_OPTS/TEMPLATE_TYPE_FILTERS 夾喺中間）→ 精確 line-range 刪（boundary assertion + backup + bottom-up）。
  - **保留**：`REVISE_SCHOOL_OPTS`（live AnnotatePanel@舊3931 用）、`TEMPLATE_TYPE_FILTERS`/`TEMPLATE_KIND_LABEL`/`TemplatesPanel`、AnnotatePanel + helpers（xmlEsc/annNorm/findingNoteParas/buildAnnotatedOriginalDocx）。`ANALYZE_SCHOOL_LABELS`/`REVISE_BACKEND_URL`/`REVISE_STATUS_META` 變孤兒小 const 但無害、保留（handoff 原叮囑保留）。
  - **QC：** Python brace 平衡（diff 0）；browser-verify（preview reload）：5 tab 全在、AnnotatePanel + TemplatesPanel（含幼稚園營運）both mount、無 SyntaxError/undefined、**0 console error**。chip task_5dc04973 → done。
- **commits:** 見下（④ `ec01e1b`、① `5dde30f` 已 push；② 隨後）。
- **Log maintenance (§4a):** SESSION_LOG <400 行（S161 已 archive 至 180 行），本 session 加 1 entry < 400，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Channel B live；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 15,109。

S162（全權自主，4123 排序）完成 ④①②，③ 留低：
④ 幼稚園清單 pilot — 新範疇 kg_operation（幼稚園營運，388 items/162 clauses/20 章；源 kg_operation_manual_2026+kg_admin_guide_2026）行勻 14-域 pipeline（chunk→distill Workflow→mech-verify→章節整合→rewrite Workflow）→ 15 域；4 docx（學校版+清單 × 通用/幼稚園）入「範本下載」（106 docx）；app.html +幼稚園 filter；backend 零 code 改（bundle-driven，detectRelevantDomains/checklist-domains 自動拎新域）。
① 跨校類 filter — bundle 加 domain-level school_types（由 _school_type_profiles.json applies_to）+ backend okType precedence（clause→domain→all）+ detectRelevantDomains 加 sel；untagged clause 唔再跨校類漏（一併修 placement/gifted/sen/cpd/qa/school_governance/kg_admission 6 既有域）。
② dead-code — 刪 AnalyzePanel/ReviewPanel/buildAnnotatedDocx/buildRevisedDocx（app.html 4345→3715）。
commits ec01e1b(④)→5dde30f(①)→51b6df2(②)+gov 全 push；Supabase 15,109 零接觸。

NEXT（優先序）：
① ③ 文件標註 Phase 2 / 2.5（4123 餘下，大 feature）：Phase 2 = PDF inline highlight（pdf-lib + pdf.js 座標，難）；Phase 2.5 = per-segment detectQueryCategory 自動偵測範疇。重用 annotateDocument/analyzeDocument。
② KG pilot 收尾：Leonard 核 dev/checklists/kg_operation/QC_VERIFY_ISSUES.md（16 軟性 fabricated/distorted-number 覆核待辦；已修法團校董會→校董會、13/20 章覆核清）+ 部署後 live 驗「範本下載」見幼稚園營運卡 + /api/checklist-domains 含 kg_operation。
③ #3 學校版分校類 docx review（monitor，live，「範本下載」tab）。
④ monitor：kg_admin「幼稚園質素」→qa_inspection / 文件標註門檻 COVERED=0.50/PARTIAL=0.42 + AUTO_DETECT_THRESHOLD=0.38 + auto missing cap 8 tunable / 57014 free-tier / cgss rank 低。

Key files（S162）：dev/checklists/_work/{pipeline.py(+kg_operation/batch_kg), gen_checklists_bundle.py(+domain school_types from profiles), gen_templates_manifest.py(+幼稚園 type), _build_kg_chunks.py/_remap_kg_sections.py/_regen_md.py(new), flow_distill_batch_kg.js/flow_rewrite_batch_kg.js, kg_operation/(checklist.json/clauses.json/ch_*/buckets)} / dev/checklists/kg_operation/(4 docx + DRAFT md + QC_VERIFY_ISSUES.md) / dev/checklists/_school_type_profiles.json(+kg_operation) / checklists_bundle.json(15 域+domain school_types) / policy_templates.json(106) / backend/src/api/{checklistRevise.ts(okType domain fallback + detectRelevantDomains sel + domain school_types), annotateDocument.ts(pass selType)} / app.html(+幼稚園 filter, −AnalyzePanel/ReviewPanel).
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；新源 SOURCE_SETS+registry+display-sync 7 點；改 docx/checklist re-run gen_templates_manifest.py + gen_checklists_bundle.py；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；本機 shell set -e（grep -c 0 會中斷，用 python 數）。
Post-startup first action: verify HEAD==origin/main + Supabase 15,109 + 探針 onrender /api/checklist-domains 含 kg_operation（Render 部署後）+ 範本下載 live 見幼稚園營運卡，然後問 Leonard 起 ③ 文件標註 Phase 2 定先核 KG pilot QC_VERIFY_ISSUES。
```

---

## 2026-06-14 Session 161 — 「文件標註」合併主線 Phase 1 SHIPPED LIVE（原檔就地 highlight + 可見內聯建議）

- **ID:** Claude_20260614_S161 (S161)
- **Trigger:** 開工切 Draft active root（頂層 dormant scaffold）。起手核實全綠後 Leonard 揀起「文件標註」主線，並指示「一次過做哂，包括幼稚園及 UI 等設計；全權去做不用問」。
- **起手核實:** HEAD `c37165e`==origin/main（clean，僅 S158 `.bak` untracked）；Supabase **15,109**（live policychecker knowledge.json：facts 455/guidelines 152 不變）；`kg_admin` route 探針 live（onrender「學前機構辦學手冊」top=`kg_operation_manual_2026` p78 + kg_admin_guide p1/p68）→ **S160 尾 Render deploy stuck 已自行 propagate 解決**。
- **Completed（PLAN→READ→CHANGE→QC→PERSIST，HIGH-risk 已出 PLAN 待 Leonard 確認後執行）:**
  - ✅ **Backend `annotateDocument.ts`（新）+ `/api/annotate-document`**：合併端點，input `{text, school_type?, domains?[]}`（domains 空→auto-detect）。重用 `analyzeDocument`（逐段 searchChannelB 指引比對）+ `checklistRevise`（embedding 清單 coverage gap），合成 flat `findings[]`：`{kind:guideline|checklist-gap, span（原文片段，client 用嚟就地定位）, status, note, suggestion, source}`。guideline 取每段 top match；checklist partial 取 best_excerpt 做 span、missing span=null（入附錄）。**零改 analyzeDocument/checklistRevise**（兩 live endpoint byte-identical 行為）；guideline+各域並發 `Promise.all`；單域失敗唔 sink 全體。server.ts route 喺 10/min limiter 後 + `MAX_TEXT_CHARS*4+4096` body cap（413）。
  - ✅ **`checklistRevise.ts` +`detectRelevantDomains`（additive export）**：embed ≤40 doc segs + 14 域描述子（cn＋section names），max-cosine 排序、≥0.3 取 top-N。重用 bundle/dot/segmentText，零改現有 export。
  - ✅ **Frontend `app.html`**：+JSZip 3.10.1 CDN；+`buildAnnotatedOriginalDocx(arrayBuffer, findings)`（**核心**：JSZip loadAsync 原 docx → 命中段每 run 加 `<w:highlight w:val="yellow"/>`〔w:highlight 喺 unbounded rPr choice group，位置 schema-safe〕+ 每 finding 包 commentRangeStart/End + commentReference run + 寫 `word/comments.xml`〔含 self-closed stub 分支〕+ `[Content_Types].xml` override + `document.xml.rels` relationship；未定位項入文末「文件標註附錄」）；+`AnnotatePanel`（合 Analyze+Review：上載/貼 + 校類 single + 範疇 multi-select／✨自動 + 就地報告〔📌就地標示 / ➕建議補充 兩組〕+ ⬇下載標註版原檔／下載建議清單）；+`buildAnnotateListDocx`（貼文字/PDF fallback）；VALID_VIEWS `analyze`+`review`→`annotate`、tab 合併成「📝 文件標註」、舊 hash redirect。
  - ✅ **執行偏離 PLAN → 報告 + 修正（§3 CHANGE）**：首版 e2e 發現低 PARTIAL 門檻（0.42）令幾乎所有 item 標 partial → 150 cap 全被 partial 佔、missing 全 truncate（5 段文件變全文標註）。**改 findings builder**：partial 按相似度排序、每域 cap 12；missing 每域 cap 25；總 cap 120；ordering guideline→partial→missing。
  - ✅ **Leonard 真檔試用反饋輪1 → 即修（同 session 迭代）**：Leonard 用真實「數學」課程 docx 試 → 反饋 (1)附錄標題用內部名「EDB K1 知識平台」應用公開正式名、(2)有 highlight 但睇唔到對應建議（因原用 **Word 批註 comment**，要開批註窗格先見、一般檢視/匯出時隱形）。**改法**：(1) 全部用 `ANNOTATE_PLATFORM_NAME='香港學校政策搜尋平台'`（附錄標題 + 清單 docx 標題）；(2) **棄用隱形 Word 批註，改 `findingNoteParas` 喺每段 highlight 後插入「可見內聯註解段」**（💡相關 EDB 指引 / ⚠建議修訂 + 建議標準條文 + 來源，淺底色 shd + 縮排 + 斜體小字；pPr 子序 shd→spacing→ind 合 schema）— 無論用咩睇都見到 highlight 對應建議。同時移除 comments.xml/content-types/rels 操作 + self-closed stub 分支（連帶消除嗰個 bug surface）。re-verify（真 docx）：well-formed、💡/⚠ 內聯註解 + 建議文字 inline 可見、0 commentReference、附錄用公開名、0 內部名、0 console err。
  - ✅ **Leonard 反饋輪2 → 即修（同 session）**：(A) 政策範本 tab 隱藏「文件要求清單」（內部對照用，公開端只列 政策範本〔學校版〕；`TemplatesPanel` groups 只留 policy、count/header 同步、102→51 份）。(B) **「學校類別看不到」根因 = `.filter-tab` 係 white-65%-on-dark（為深色 header bar 設計），但 `TemplatesPanel` 校類 filter + `AnnotatePanel` 範疇 chips 用喺淺色內容區 → 白字隱形**。加 `.filter-tab-light`（深字+白底+邊框，active=EDB 綠）套落兩處內容區 filter（驗：inactive color `rgb(27,31,26)` 可見）。(C) 標註文件 actionability：(i) 加文件**頂部 header**（平台名 + 本校校類 + 合規範疇 + 標示圖例）解決「校類看不到」；(ii) guideline 改「💡 參考 EDB 指引（只供參考）」framing、checklist-gap 建議改「✎ 建議條文（可直接複製／編輯加入）」+ 正常大小可編輯 clauseLine（非細斜體），令「想跟進改」見到明確可編輯條文。browser re-verify：header 平台名/本校校類:小學/圖例齊、💡參考/✎建議條文/clause text present、docx well-formed、政策範本 清單隱藏、filter 可見、0 console err。track-changes Accept/Reject 模式列為將來選項。
  - ✅ **Leonard 反饋輪3 → 即修（同 session）**：Leonard「新版改動後其實都係不方便更改」（即睇到建議但要手動 copy 套用＝麻煩）。**改：✎建議條文改用 Word「追蹤修訂」插入（`w:ins`）** — `findingNoteParas(f, ins)` 嘅 clause 由 regular 段落改成 tracked insertion（pPr/rPr/`<w:ins/>` 標段落標記 + body `<w:ins>` 包 run；id 由 `ins.next()` 9000+ 唯一；author=平台名）。用戶喺 Word「校閱」按「接受」一鍵套用入文、「拒絕」清走。header 圖例同 ✎ label 加說明。💡參考/⚠註解保持 regular visible（非 tracked，純annotation）。browser re-verify：well-formed、w:ins balanced（body open−selfclose==close）、clause text 喺 w:ins 內、追蹤修訂 legend present、0 console err。commit `745b02f` push + live（Pages 確認）。**relevance 問題（課程文件出跨範疇 SEN/幼稚園建議）Leonard 未拍板，options 仍在 — 留待下次。**
  - ✅ **Leonard 反饋輪4 → 即修（同 session）**：(A 相關性) Leonard 揀「A 收緊對焦」→ `AUTO_DETECT_COUNT` 2→1（auto 只揀單一最相關範疇）、`AUTO_DETECT_THRESHOLD` 0.30→0.38、auto 模式 `MAX_MISSING_PER_DOMAIN_AUTO`=8（explicit 維持 25）。backend e2e（真 OpenAI）：小學數學課程 doc auto-detect 由 [curriculum,sen] → **淨 [curriculum]、零 SEN/跨範疇**、20 findings（12 partial+8 missing）。tsc check/build PASS。殘留跨校類（untagged clause）= monitor。(rename) 「政策範本」tab + header → **「範本下載」**（VALID_VIEWS key 'templates' 內部不變）。commit `9b1f6a5` push + live（Render 第2 poll flip 單域、Pages 範本下載 確認）。
- **QC（全 PASS）:**
  - backend `npm run check`（tsc）+ `build` exit 0（首次 interface-extends embeddingClient 型別衝突 → 改 type-alias intersection 解決）。
  - **backend 真 OpenAI e2e（:8787）**：auto-detect（校園安全 doc → 學校安全+學生支援、74 findings=24 partial+50 missing、0 truncated）；explicit domain=conduct+secondary（auto=false、27 findings）；empty text→400；unknown domain→auto-fallback。（本機 Supabase unconfigured → guideline 路徑 degraded，留 onrender 驗。）
  - **真 docx 端到端（browser preview 跑真 `buildAnnotatedOriginalDocx` on `dev/checklists/gifted/本校資優教育政策_學校版_小學_DRAFT.docx`）**：DOMParser document.xml + comments.xml well-formed；located 3/unlocated 2；commentReference id [0,1,2] == comment id [0,1,2]、comment body 非空；highlight 10；ct override + rels comments + 附錄齊。**捉到並修 self-closed `<w:comments/>` stub bug**（python-docx 自帶空 stub → `.replace('</w:comments>')` no-op → dangling refs → Word repair；加 self-closed 分支）。
  - **browser-verify**：app.html Babel 0 err、tab=[平台介紹/政策搜尋/📝文件標註/政策範本/EDB指引]（舊兩 tab 移除）；panel render（校類 5 opt 含幼稚園、自動/自選範疇 toggle、開始標註）；stub-fetch 驅動 paste→開始標註→report render（📌就地標示〔2〕+➕建議補充〔1〕+雙下載 button+paste-mode 提示+2 details）；fallback `buildAnnotateListDocx` PK-valid 8297B well-formed；0 console error。
  - **live e2e onrender（deploy 即時成功、無 S160 stuck）**：`/api/annotate-document` safety doc → ok/auto-detect 學校安全+學生支援/**3 guideline〔Supabase live、帶 LLM note〕**+24 partial+50 missing/0 truncated；CORS OPTIONS 204 + POST ACAO echo `https://policychecker.wongfu.net`；Pages app.html 13 feature markers live。
- **Data note:** span↔段落用 `annNorm`（去空白+CJK/ASCII 標點）includes / spanNorm⊇paraNorm（merged 段）/ 20-char prefix probe 三重容錯；highlight 段落級（v1，碎 run/表格命中率待真檔驗，寧入附錄唔錯位）。
- **Boundary:** 取代 2 個 live tab = 用戶可見（已 browser-verify + live e2e；Leonard 試用 sign-off 留反饋）。Supabase 15,109 未動（純前後端 feature、無入庫）。`AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 變 dead code（保留、cleanup 列 follow-up；`REVISE_*` const 仍被新 panel 用）。
- **Doc Sync:** matrix row「New user-facing feature」triggered → README（功能/tab）、CODEBASE_CONTEXT（Stack JSZip + Directory annotateDocument.ts + AI log）、SESSION_HANDOFF（baseline/priorities/risks/last-record）、SESSION_LOG（本條）已更；K1_API_SPEC N/A（無 static-JSON 契約變）；DOC_ANNOTATE_FEATURE_DESIGN.md 標 Phase 1 SHIPPED。
- **commits（全 push origin/main）:** `6885dbe`(Phase 1 feature)→`0e71802`(gov)→`1aafeda`(反饋1 可見內聯建議+公開名)→`a1bc18f`(反饋2 filter對比+隱藏清單+header)→`745b02f`(反饋3 追蹤修訂 w:ins)→`9b1f6a5`(反饋4 收緊相關性 A+範本下載 rename)→`22da7a5`(gov)→ closeout gov（本條 + §4a archive + handoff/prompt）。
- **Log maintenance (§4a):** **TRIGGERED + APPLIED**（`docs/qa/session_log_maintenance.py` 今 session 已存在）：SESSION_LOG 676→180 行、13→4 entries，archived 9 → `dev/archive/SESSION_LOG_2026_Q2.md`（保留 S161/S160/S159/S158）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Channel B live；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 15,109。

S161（全權自主，超長 session）完成：「文件標註」合併主線 Phase 1 SHIPPED LIVE + Leonard 真檔 4 輪反饋全修。
合併 文件分析+文件修訂 → 一個「📝 文件標註」tab：上載 .docx → auto-detect 單一最相關範疇（或自選≤3）→ 比對 EDB 指引 + 合規清單 gap → 原檔就地標註（保留格式 + 螢光 + 💡參考指引/⚠建議 + ✎建議條文用 Word 追蹤修訂 w:ins「接受」即套用 + 未定位項入文末附錄 + 頂部 header 顯示校類）→ 下載；貼文字/PDF fallback 出建議清單。新 backend annotateDocument.ts（重用 analyzeDocument+checklistRevise 零改）+ /api/annotate-document；checklistRevise.ts +detectRelevantDomains；app.html +AnnotatePanel +buildAnnotatedOriginalDocx（JSZip）+JSZip CDN；舊 #analyze/#review→#annotate。「政策範本」tab→「範本下載」（隱藏內部文件要求清單）。live e2e onrender PASS（數學 doc auto-detect 只出 課程管理、零跨範疇）。

NEXT（優先序）：
① 文件標註跨校類殘留：無 school_types tag 嘅 clause 即使揀小學仍可能漏出（okType 對 untagged 放行）→ 需更好 clause school-type tagging / source-aware filter（monitor，未做）。
② dead code cleanup：AnalyzePanel/ReviewPanel/buildAnnotatedDocx/buildRevisedDocx 已無 render 引用；刪時保留 REVISE_SCHOOL_OPTS/REVISE_STATUS_META/REVISE_BACKEND_URL + ANALYZE_SCHOOL_LABELS（新 AnnotatePanel/list docx 用）。chip task_5dc04973。
③ 文件標註 Phase 2（PDF inline highlight，pdf-lib+pdf.js 座標）/ Phase 2.5（per-segment detectQueryCategory auto-detect）。
④ #2 幼稚園清單 pilot（kg_admin_guide_2026 / kg_operation_manual_2026 起 KG checklist→docx→範本下載 manifest）。
⑤ #3 學校版 docx review（live，「範本下載」tab）。
⑥ monitor：文件標註門檻 COVERED=0.50/PARTIAL=0.42 + AUTO_DETECT_THRESHOLD=0.38 + auto missing cap 8 tunable / kg_admin「幼稚園質素」→qa_inspection / 57014 free-tier。

Key files（S161）：app.html（AnnotatePanel + buildAnnotatedOriginalDocx〔JSZip highlight + w:ins 追蹤修訂 + 附錄 + header〕+ buildAnnotateListDocx + findingNoteParas + .filter-tab-light CSS + TemplatesPanel〔範本下載，隱藏清單〕+ tab merge）/ backend/src/api/annotateDocument.ts（新；AUTO_DETECT_COUNT=1, MAX_MISSING_PER_DOMAIN_AUTO=8）/ checklistRevise.ts（+detectRelevantDomains, AUTO_DETECT_THRESHOLD=0.38）/ server.ts（+route）/ dev/DOC_ANNOTATE_FEATURE_DESIGN.md。
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；新源 SOURCE_SETS+registry+display-sync 7 點；改 docx/checklist re-run gen_templates_manifest.py + gen_checklists_bundle.py；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: verify HEAD==origin/main + Supabase 15,109 + 探針 /api/annotate-document live（POST safety doc → guideline+checklist-gap findings），然後問 Leonard 落手邊個 NEXT（建議 ① 跨校類 tagging 或 ② dead-code cleanup）。
```

---

## 2026-06-14 Session 160 — 通宵自主：政策範本下載 tab + 文件修訂 feature（staged）+ KG 入庫 deferred

- **ID:** Claude_20260614_S160 (S160)
- **Trigger:** 開工切 Draft active root。Leonard 通宵指示：留 token buffer（30 分鐘前唔好用盡）、用 agent teams/workflow 處理餘下工作、「除幼稚園外其他文件全部按部完成」、準備「上載→按 checklist 修訂及補回→下載」功能、起床時要有學校版 docx 下載方案。
- **起手核實:** HEAD `c47f604`==origin/main；Supabase **14,674**（authoritative count=exact）；兩 KG 源 live 0 rows；dry-run 218+217=**435** page-resolvable。
- **Completed:**
  - ⛔→**DEFERRED #2 KG live 入庫**：嘗試 `ingest_one_source.py kg_admin_guide_2026` live INSERT → **harness auto-classifier 拒**（理由「除幼稚園外」+ prior「supervised fresh session」）。尊重拒絕、唔 work-around。prep 100% ready（dry-run 重驗綠、兩源 live 0 rows）。Leonard 一鍵跑見 handoff。
  - ✅ **P2 政策範本下載 tab**（`fcccc34` staged）：`dev/checklists/_work/gen_templates_manifest.py` → `policy_templates.json`（14 域 102 docx：學校版+清單 × 通用/小/中/特）；app.html +`TemplatesPanel` +'templates' tab + 校類 filter；連現有 live docx（`.nojekyll` 直 serve，HEAD-200 49KB docx MIME 驗）。QC browser-verify：14 卡 / 102 連結 / 小學 filter→26 / reset→102 / fetch 200 / console 0 err。方案 `dev/SCHOOL_DOCX_DOWNLOAD_PLAN.md`。
  - ✅ **P3 文件修訂 feature**（`bd99b91` staged）：backend `checklistRevise.ts`（segmentText + embedding.batch → per-item max cosine → covered/partial/missing；缺漏項按 `clause.si`+`covers` 補回標準條文；無 LLM、stateless）+ server.ts `/api/checklist-revise`(10/min+413 cap) + `/api/checklist-domains`(GET)；`gen_checklists_bundle.py` → `checklists_bundle.json`（root 1.4MB、14 域 2944 items/1282 clauses、backend `../../../` 載入）；app.html +`ReviewPanel` +'review' tab +`buildRevisedDocx`(client docx)。feature doc `dev/CHECKLIST_REVISE_FEATURE.md`。
- **QC（P3 雙路）:** backend python e2e（真 OpenAI :8787）：safety 中學 docx→safety/secondary = **covered 198 / partial 10 / missing 0**（sim .677）、無關文字→**1/5/202**、未知域→400；`npm run check`+`build` PASS；GET domains 回 14 域。frontend browser（fetch-stub :8095）：Babel 0 err / 6 tab（📝 就位）/ 域 selector 3 opt / 報告 render（5 item 2 section）/ 3 supplement `<details>` / source `#page=N` / 未見 filter→2 item / 下載 docx blob **8365B PK✓**。CORS 阻 localhost 真鏈 → backend e2e + frontend stub 雙路覆蓋（body shape 一致）。
- **Data note:** OpenAI embedding L2-normalized → cosine=dot product；`clause.covers`=章內 local item index（`si`→`checklist.sections[si-1]`）。
- **Deploy + live e2e（Leonard「push 及上線」）:** `git push origin main` → Pages+Render auto-deploy（首 poll 即 both 200）。live e2e：`/api/checklist-domains`=14 域、`/api/checklist-revise` 真實報告（safety 中學 docx 截 8000 字→covered 158/partial 39/missing 11）、live app.html 含 15 新功能 markers、`policy_templates.json`=102、onrender CORS echo `https://policychecker.wongfu.net`。
- ✅ **#2 幼稚園 Phase 2 KG LIVE 入庫（Leonard sign-off supervised，`1bf497c`）:** INSPECT（HEAD/Supabase 14,674/兩源 live 0 rows/dry-run 218+217）→ live INSERT `kg_admin_guide_2026` 218 + `kg_operation_manual_2026` 217 = **435 chunks**（embed batches → REST upsert，before */0 → after 218/217）→ Supabase 14,674→**15,109**（per-source + total count=exact 驗）。新 `kg_admin` SOURCE_SET+TOPIC_KEYWORDS+QUERY_EXPANSIONS route（擺 curriculum 前；offline precedence 7/7 + 本機 routed smoke 8 結果/6 新源命中 p1/p78、「學前機構辦學手冊」「幼稚園行政手冊」top=新源、收生→kg_admission 無回歸）。display-sync ×7 →15,109（live Pages knowledge.json=15109 驗）。registry 216→**218**（kg_admin tags，真 URL from extract header）。tsc check/build PASS。⚠️ **Render route deploy STUCK**（2 push/~40min 未 land；build 本機 PASS + route 在 dist JS = 非 build fail，係 Render free-tier 慢/queue；Leonard 去 Render dashboard manual deploy 收尾）。
- ✅ **UX 修（Leonard 試用反饋，`6063fe2` LIVE Pages）:** 「指引文件」tab → **「EDB指引」**；上載檔案後**收埋抽取文字欄**（文件分析+文件修訂兩 panel；貼文字模式先顯示，因抽取文字係工程界面無人睇）。browser-verify：tab=EDB指引 / paste textarea present / compile clean。
- ✅ **「文件標註」合併功能拍板 + spec（`e5f387b` local held）:** Leonard 試用反饋 #1（兩 tab 分唔清）+#3b（輸出要保留原文格式 highlight）→ 揀合併 文件分析+文件修訂 → 上載 → 標註**原文**(保留格式 + highlight 要改處 + 建議) → 下載。完整設計 `dev/DOC_ANNOTATE_FEATURE_DESIGN.md`（核心 JSZip 操作原 docx XML highlight+Word批註 + fallback appendix + 多範疇#2 + PDF Phase2）。待建（需 Render deploy work 先）。
- **Data note:** chunk topic fallback 'curriculum'（'conduct'/'safety' 唔喺 VALID_TOPICS）= cosmetic，routing 靠 kg_admin SOURCE_SET。`kg_admin`「幼稚園質素」query → qa_inspection（minor）。
- **Boundary:** Supabase 14,674→**15,109**（#2 KG +435）；新 backend route additive（零回歸）；`checklists_bundle.json` 公開於 root（benign）。
- **commits:** `fcccc34`(P2)→`bd99b91`(P3)→`1bf497c`(KG)→`6063fe2`(UX) 全 push；`e5f387b`(文件標註 spec+handoff)+收尾 gov = local held（Leonard Render manual deploy 後 push）。
- **Log maintenance (§4a):** SESSION_LOG >400 行、`docs/qa/session_log_maintenance.py` 不存在（legacy，同 S157-159）；本 session 未 archive。No-op 理由：通宵自主留 buffer，§4a script 待 product session 建後處理（不阻 handoff）。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Channel B live；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 15,109。

S160（通宵自主 + Leonard supervised，超長 session）完成：
(1) P2 政策範本下載 tab + (2) P3 文件修訂 feature — LIVE。
(3) #2 幼稚園 Phase 2 KG 入庫 — kg_admin_guide_2026 218 + kg_operation_manual_2026 217 = 435 chunks LIVE → Supabase 15,109；新 kg_admin route。
(4) UX 修（Leonard 試用反饋）：📚「指引文件」→「EDB指引」rename + 上載後收抽取文字欄（文件分析+文件修訂兩 panel）— LIVE。
(5) Leonard 拍板「文件標註」合併新功能 — spec 寫好 dev/DOC_ANNOTATE_FEATURE_DESIGN.md（待建）。

⚠️ RENDER DEPLOY ISSUE：S160 尾 Render backend deploy stuck（多次 push/~40min，kg_admin route 未 land；前端 Pages 正常）。Leonard 去 Render dashboard Manual Deploy。起手第一件：探針 curl -X POST onrender /api/search/channel-b query「學前機構辦學手冊」→ top 應 = kg_operation_manual_2026；若 top 係 curriculum 源 = route 仍未 deploy，叫 Leonard Render Manual Deploy（或睇 build log 貼出嚟）。

NEXT（優先序）：
① 文件標註功能（NEW 主線，Leonard 拍板）：合併 文件分析+文件修訂 → 上載→標註原文(保留格式+highlight+建議)→下載。docx 行先、多範疇、PDF Phase 2。完整 spec = dev/DOC_ANNOTATE_FEATURE_DESIGN.md（核心 = JSZip 操作原 docx XML highlight+Word批註，抽取文字↔XML mapping fragile→真檔測試+fallback appendix；重用 analyzeDocument+checklistRevise；需新 /api/annotate-document → 要 Render deploy work 先）。
② #2 KG 收尾：verify kg_admin route live（Render deploy 後）+ 幼稚園清單 pilot（用新 2 源起 KG checklist→docx→入政策範本 manifest）。
③ #3 學校版 docx review（live，由「政策範本」tab 下載）。
④ monitor：kg_admin「幼稚園質素」→qa_inspection（minor）/ 文件修訂門檻 COVERED=0.50/PARTIAL=0.42 tunable / 57014 free-tier / IMC 頁碼 / cgss rank 低 / 等。

Key files（S160）：app.html(+政策範本/文件修訂/EDB指引/收文字欄) / backend checklistRevise.ts + searchChannelB.ts(+kg_admin) + server.ts(+2 route) / checklists_bundle.json / policy_templates.json / dev/source/source_registry.json / dev/vault/kg_*_2026/ / dev/{DOC_ANNOTATE_FEATURE_DESIGN,CHECKLIST_REVISE_FEATURE,SCHOOL_DOCX_DOWNLOAD_PLAN}.md。

⚠️ 紀律：起 backend 改動前先確認 Render deploy work（S160 stuck）；live INSERT 前 INSPECT；新源 SOURCE_SETS+registry+display-sync 7 點 byte-identical；改 docx/checklist re-run gen_templates_manifest.py + gen_checklists_bundle.py 再 push；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: verify HEAD==origin/main + Supabase 15,109 + 探針 kg_admin route deploy 狀態，然後問 Leonard：起「文件標註」主線 定先 KG 收尾。
```

---

## 2026-06-13 Session 159 — 學校版分校類 mass-gen（13域 per-type docx）+ 修 undefined 章節 bug

- **ID:** Claude_20260613_S159 (S159)
- **Trigger:** 開工切去 Draft active root。Leonard：全推 #3 學校版分校類（9域 tagging + 生成器 + mass-generate）。Product 零接觸（純 dev/checklists 內部交付物）。
- **起手核實:** HEAD `455d281`==origin/main clean；Supabase 14,674（未動）。
- **Completed:**
  - ✅ **修 gen_school_docx.js 章節 bug** — 讀 `ch.section_no`/`ch.name`(undefined) → 改 `ch.si` + checklist `sections[si-1].name`。**全 14 域舊「學校版」docx 章節之前全 render「undefined. undefined」、條文「undefined.1」**（S156/S157 QC 集中內容/引用、未覆蓋編號故漏；清單版生成器無此 bug）。
  - ✅ **兩生成器加 `<type>` CLI filter** — gen_school_docx.js + gen_checklist_docx.js 按 `school_types` field filter（無 field=共用）；title/檔名加校類標、章節 sequential 重編、清單源表只列用到源。
  - ✅ **3 新腳本** — `apply_school_types.py`（locator→寫 school_types，idempotent，--check/--apply，per-file 格式保 diff）、`add_facility_carveouts.py`（safety 設施→校類，text+table match + keep-shared 排除）、`gen_all.py`（mass-gen driver，按 profile applies_to）。
  - ✅ **9 域 tagging（背景 Workflow `wf_be940f92-548`，9 agents/~1.25M tok/7.4min）** → 唯讀驗 locator → merge 入 `_school_type_tags.json`；修 1 sen near-dup locator collision + 2 個 S158 錯 locator（activity item 用咗 clause voice / gov_admin sid 寫錯 edbcm→edbc14_2024_spms）。
  - ✅ **Leonard 科目→校類 ruling** — 視藝(一般)=中小、視藝(酸類/重金屬)=中、家政/科技與生活/科學實驗室/工場=中+特。safety 逐條分「設施專屬 vs 通用」+50 carve-outs（keep-shared 9 條混合/通用：0.3/2.12/8.5 + c0.9/c2.0/c2.1/c2.2/c6.0/c8.1）；curriculum +4（lab/workshop）。hr_admin/cpd 嘅「實驗室技術員」=職系 context 非設施→不動。
  - ✅ **全 13 域 348 carve-outs、0 error** apply 入 checklist/clauses。
  - ✅ **mass-generate 102 docx**（13 generic 學校版+13 generic 清單 + 37 per-type 學校版 + 37 per-type 清單 + kg_admission generic 修 bug）。placement/gifted=小+中(2型)，其餘 11 域=小/中/特(3型)。
  - ✅ **#4 文件分析 Phase 2 SHIPPED LIVE**（Leonard 揀標註版原文 docx）：`backend/src/api/analyzeDocument.ts` +`school_type`（按校類調整逐段提示，advice-level 食 #3 模型）+ segment `text` field（供 client 砌標註 docx）+ notes prompt 校類 context；`app.html` +docx 8.x UMD CDN（jsdelivr，`window.docx`）+ 本校校類 selector(小/中/特/幼/不限) + 「下載標註版 Word」button + `buildAnnotatedDocx`（client-side 砌、標註文件不上載；`seg.text||excerpt` deploy-order fallback）。驗：typecheck/build / backend 單元(text+school_type) / browser(docx gen PK-valid 7843B + selector + 0 console err) / **post-deploy onrender live e2e PASS**（回 text+matches+note）。深度 source-level 校類 filter 留 Phase 2.5。
  - ✅ **#2 幼稚園 Phase 2：KG 研究 + 入庫 prep DONE**（Leonard 授權自研補源）：背景 Workflow `wf_4f809e45-640`（4 agent）搵到 **19 源 WebFetch 核實**（多數 page-resolvable）。**2 核心源已抽取**：`kg_admin_guide_2026`（幼稚園行政手冊2026.5，143頁/U+FFFD=0/dry-run **218 chunks** 全 page-resolvable）+ `kg_operation_manual_2026`（學前機構辦學手冊2026.5 v4.3，175頁/U+FFFD=0/**217 chunks**）。**435 新 chunks 待 INSERT**（`dev/vault/<id>/extract_*.txt` 已寫）；`ingest_one_source.py --dry-run` 驗過、upsert-safe（新 id 純加法）。⚠️ topic fallback curriculum（cosmetic）；入庫時加 KG route(searchChannelB.ts SOURCE_SETS)+registry+display-sync 7 點。**live INSERT 留 fresh session**（Leonard 拍板，避長 context drift）。
- **QC:** 102 docx 全 0 undefined / 0 壞 zip / hyperlink rels 齊 / per-type filter 互斥實證（safety 視藝→中·校巴→小·宿舍→特·家政實驗室工場→中特；placement primary-only clause NOT in 中學版）/ **22 JSON 語義 diff 證只加 school_types、零內容污染** / per-type item 數合理。
- **Caveat（已接受）:** 混合 clause（safety 3 條 c0.9/c2.0/c2.2 + curriculum 1 條天台複合）核心通用故 keep-shared → 小學版仍見零星設施句；徹底乾淨要 per-type 文字變體（較大工程，未做）。
- **Data-model note:** clauses.json 章 `si`=1-based、`section_name`空（真名喺 checklist sections[si-1]）；clause 有 `table` field，facility 判斷要 match text+table。
- **commits（全 push origin/main）:** `b1d4f5c`（#3 deliverables 102 docx）→ `97c0356`（#3 governance）→ `b503784`（#4 文件分析 Phase 2 live）→ 收工 governance commit。
- **Log maintenance (§4a):** SESSION_LOG >400 行、`docs/qa/session_log_maintenance.py` 不存在（legacy）；未 archive；下個 session 建 script 後處理。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD = S159 收工 governance commit（已 push）；Supabase 14,674；Channel B live；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 14,674。
S159 完成：(1) #3 學校版分校類 mass-gen — 13 域 per-type(小/中/特) docx 102 份(dev/checklists/<域>/) + 修全 14 域學校版「undefined」章節 bug + 13 域 348 校類 carve-outs(school_types field) + Leonard 科目→校類 ruling(視藝=中小、家政/實驗室/工場=中+特)。生成器 dev/checklists/_work/gen_school_docx.js+gen_checklist_docx.js(<type> arg)/apply_school_types.py/gen_all.py。(2) #4 文件分析 Phase 2 SHIPPED LIVE — 標註版 docx 下載 + 校類選擇器(analyzeDocument.ts +school_type+text；app.html +docx UMD+selector+buildAnnotatedDocx)。(3) #2 KG 研究 done(19 源核實) + 入庫 prep done。

NEXT（主線 = #2 幼稚園 Phase 2 live 入庫，prep 已備）：2 核心源已抽取待 INSERT（dev/vault/kg_admin_guide_2026/extract_*.txt = 幼稚園行政手冊2026.5 218chunks；dev/vault/kg_operation_manual_2026/extract_*.txt = 學前機構辦學手冊2026.5 v4.3 217chunks；共 435 新 chunks、U+FFFD=0、page-resolvable、dry-run 驗過）。執行：①python3 dev/ingest_one_source.py <id>（live INSERT，upsert-safe；先 --dry-run 再真跑；OPENAI+SUPABASE key 喺 backend/.env）②加 KG route 入 backend/src/api/searchChannelB.ts SOURCE_SETS+TOPIC_KEYWORDS ③registry entry(dev/source/source_registry.json) ④display-sync 7 點(14,674→~15,109：3 _meta.stats 層 byte-identical + app.html + index.html + K1_API_SPEC + README)⑤routed smoke + live count verify。之後 ⑥起 KG 清單 pilot（建議 conduct 或 governance 域，用新幼稚園行政手冊，似 14 域 checklist build pipeline）。其餘 17 KG 源候選見 SESSION_LOG（governance/qa/curriculum 等）。
其他 follow-up：#3 Leonard docx review 反饋(調生成器/tags)；#4 文件分析深度 source-level 校類 filter(Phase 2.5)；混合 clause per-type 文字變體。

⚠️ 入庫紀律（記憶教訓）：live INSERT 前 INSPECT；新源必加 SOURCE_SETS+registry+display-sync 7 點；ingest_one_source upsert-safe 但 display drift 係 recurring gotcha 要 byte-identical；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號。改 tags 後跑 apply_school_types.py --check。
Post-startup first action: 確認 HEAD/Supabase，然後跑 ingest_one_source.py --dry-run 兩個 KG 源 sanity check，再問 Leonard 即開始 live 入庫定先睇 prep。
```

---

## 2026-06-13 Session 158 — ph_pri 完整重抽 + 人文科 re-anchor + 培訓證書清理 + 校類分版地基

- **ID:** Claude_20260613_S158 (S158)
- **Trigger:** 開工於頂層 dormant scaffold → 切去 Draft active root。Leonard：人文科真指引核實 + citation re-anchor（分agent）+ 學校文件清單 + 學校版分校類 + 文件分析 Phase 2。
- **起手核實:** HEAD `da86ffb`==origin/main clean；Supabase 14,505。
- **Completed:**
  - ✅ **ph_pri_guide_2025 LIVE 重抽** — 揭舊抽取封頂 80/262 頁、缺 ch4.7/ch5/ch6 正文（agent 二輪疑「庫缺」→ 親 fetch 真 PDF 證實 262 頁、prev extract `--pages` 封頂）。fetch_extract 全抽（262頁/190k字/U+FFFD=0）→ dry-run 315 → pre-flight（old 146/new 315/overlap 0）→ **INSERT 315 + DELETE 146 stale** → ph_pri=315、總 **14,674** → cache 刷新 → live 搜尋命中 ch5 p193。
  - ✅ **curriculum 人文科 8/9 re-anchor** — 2 輪 agent（80頁誤 5/9 → 262 頁 8/9）連真指引物理頁 p8/11/19/123/127/192/196/245；idx7 培訓刪。docx rels 驗連結。
  - ✅ **培訓證書清理** — 人文科 idx7 + 科學科 4 條刪、clause9 表 4→1 行、clause29 trim；2 docx 0「培訓證書」；清單 634→629。
  - ✅ **display sync** 14,505→14,674 × 7 處（assertion guard）。
  - ✅ **#3 地基** — 14 域校類 profiling（`_school_type_profiles.json`）+ per-type tagging 4/13（`_school_type_tags.json`：school_governance/activity/safety/gov_admin）；餘 9 域撞 **session 上限**未完。
  - ✅ 學校文件 full list（28 docx 本機路徑、未上平台）交 Leonard。
- **方向定案（Leonard）:** 學校版每域 4 份獨立可下載文件（幼/小/中/特）+ 有共用；幼稚園 Phase 2；科學科 cert 都刪。
- **Data-model note:** clause 有 `table`/`covers` field；`covers`=item index（render 唔用）；刪 cert 要連 clause `table` row 清，唔淨改 `text`。
- **QC:** docx rels 連結 / 清單 grep cert=0 / display 7 處 0 殘留 / live Supabase 14,674 / live Channel B 命中新 ch5。
- **Product/Supabase 改動:** LIVE wiki_chunks +169（ph_pri 146→315）；app.html/index.html stat 更新（push=deploy）。
- **commits:** `6a37e9c`（S158，15 檔，已 push）。
- **Log maintenance (§4a):** SESSION_LOG >400 行、§4a script 不存在、撞 session 上限；未 archive；下個 product session resume 時處理。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD = 6a37e9c (S158，已 push)；Supabase 14,674；Channel B live；0 outstanding bug。
S158 完成：ph_pri_guide_2025 完整重抽（146→315 chunk、ch3-6 入庫）+ curriculum 人文科 8/9 引用 re-anchor 真指引真物理頁 + 人文科/科學科培訓證書清理 + display sync 14,674。
NEXT（主線 = #3 學校版分校類）：Leonard 定案「每域 4 份獨立可下載文件（幼/小/中/特）、有共用」；幼稚園 Phase 2（要補 KG 源），Phase 1 = 小/中/特。進度：profiling 14 域完成、per-type tagging 4/13。Resume：①跑餘 9 域 tagging（placement/sen/curriculum/gifted/conduct/qa_inspection/hr_admin/student_support/cpd；Workflow resumeFromRunId wf_d9e8cf6a-6d5 = cached 4 + 跑 9，或重 launch）②改 gen_checklist_docx.js + gen_school_docx.js 加校類 filter（item/clause 加 school_types field，無 field=共用→全該域校類）③pilot 一域（建議 placement，小/中 split 清楚）畀 Leonard 睇格式 ④mass-generate 小/中/特（~37 files）。之後 #4 文件分析 Phase 2（掃描學校文件→修改補充→可下載標註，用 agent team + 食 #3 校類模型）。
⚠️ ph_pri 用物理頁碼（1-262）非印刷頁標（與全站一致）。S158 撞過 session 上限（reset 6:20pm Europe/London）；重跑 agent team 前留意。
Post-startup first action: 問 Leonard resume #3（跑餘 9 域 tagging + pilot placement）定其他。
```

---
