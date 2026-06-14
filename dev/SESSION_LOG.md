# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-14 Session 161 — 「文件標註」合併主線 Phase 1 SHIPPED LIVE（原檔就地 highlight + 可見內聯建議）

- **ID:** Claude_20260614_S161 (S161)
- **Trigger:** 開工切 Draft active root（頂層 dormant scaffold）。起手核實全綠後 Leonard 揀起「文件標註」主線，並指示「一次過做哂，包括幼稚園及 UI 等設計；全權去做不用問」。
- **起手核實:** HEAD `c37165e`==origin/main（clean，僅 S158 `.bak` untracked）；Supabase **15,109**（live policychecker knowledge.json：facts 455/guidelines 152 不變）；`kg_admin` route 探針 live（onrender「學前機構辦學手冊」top=`kg_operation_manual_2026` p78 + kg_admin_guide p1/p68）→ **S160 尾 Render deploy stuck 已自行 propagate 解決**。
- **Completed（PLAN→READ→CHANGE→QC→PERSIST，HIGH-risk 已出 PLAN 待 Leonard 確認後執行）:**
  - ✅ **Backend `annotateDocument.ts`（新）+ `/api/annotate-document`**：合併端點，input `{text, school_type?, domains?[]}`（domains 空→auto-detect）。重用 `analyzeDocument`（逐段 searchChannelB 指引比對）+ `checklistRevise`（embedding 清單 coverage gap），合成 flat `findings[]`：`{kind:guideline|checklist-gap, span（原文片段，client 用嚟就地定位）, status, note, suggestion, source}`。guideline 取每段 top match；checklist partial 取 best_excerpt 做 span、missing span=null（入附錄）。**零改 analyzeDocument/checklistRevise**（兩 live endpoint byte-identical 行為）；guideline+各域並發 `Promise.all`；單域失敗唔 sink 全體。server.ts route 喺 10/min limiter 後 + `MAX_TEXT_CHARS*4+4096` body cap（413）。
  - ✅ **`checklistRevise.ts` +`detectRelevantDomains`（additive export）**：embed ≤40 doc segs + 14 域描述子（cn＋section names），max-cosine 排序、≥0.3 取 top-N。重用 bundle/dot/segmentText，零改現有 export。
  - ✅ **Frontend `app.html`**：+JSZip 3.10.1 CDN；+`buildAnnotatedOriginalDocx(arrayBuffer, findings)`（**核心**：JSZip loadAsync 原 docx → 命中段每 run 加 `<w:highlight w:val="yellow"/>`〔w:highlight 喺 unbounded rPr choice group，位置 schema-safe〕+ 每 finding 包 commentRangeStart/End + commentReference run + 寫 `word/comments.xml`〔含 self-closed stub 分支〕+ `[Content_Types].xml` override + `document.xml.rels` relationship；未定位項入文末「文件標註附錄」）；+`AnnotatePanel`（合 Analyze+Review：上載/貼 + 校類 single + 範疇 multi-select／✨自動 + 就地報告〔📌就地標示 / ➕建議補充 兩組〕+ ⬇下載標註版原檔／下載建議清單）；+`buildAnnotateListDocx`（貼文字/PDF fallback）；VALID_VIEWS `analyze`+`review`→`annotate`、tab 合併成「📝 文件標註」、舊 hash redirect。
  - ✅ **執行偏離 PLAN → 報告 + 修正（§3 CHANGE）**：首版 e2e 發現低 PARTIAL 門檻（0.42）令幾乎所有 item 標 partial → 150 cap 全被 partial 佔、missing 全 truncate（5 段文件變全文標註）。**改 findings builder**：partial 按相似度排序、每域 cap 12；missing 每域 cap 25；總 cap 120；ordering guideline→partial→missing。
  - ✅ **Leonard 真檔試用反饋 → 即修（同 session 迭代）**：Leonard 用真實「數學」課程 docx 試 → 反饋 (1)附錄標題用內部名「EDB K1 知識平台」應用公開正式名、(2)有 highlight 但睇唔到對應建議（因原用 **Word 批註 comment**，要開批註窗格先見、一般檢視/匯出時隱形）。**改法**：(1) 全部用 `ANNOTATE_PLATFORM_NAME='香港學校政策搜尋平台'`（附錄標題 + 清單 docx 標題）；(2) **棄用隱形 Word 批註，改 `findingNoteParas` 喺每段 highlight 後插入「可見內聯註解段」**（💡相關 EDB 指引 / ⚠建議修訂 + 建議標準條文 + 來源，淺底色 shd + 縮排 + 斜體小字；pPr 子序 shd→spacing→ind 合 schema）— 無論用咩睇都見到 highlight 對應建議。同時移除 comments.xml/content-types/rels 操作 + self-closed stub 分支（連帶消除嗰個 bug surface）。re-verify（真 docx）：well-formed、💡/⚠ 內聯註解 + 建議文字 inline 可見、0 commentReference、附錄用公開名、0 內部名、0 console err。
- **QC（全 PASS）:**
  - backend `npm run check`（tsc）+ `build` exit 0（首次 interface-extends embeddingClient 型別衝突 → 改 type-alias intersection 解決）。
  - **backend 真 OpenAI e2e（:8787）**：auto-detect（校園安全 doc → 學校安全+學生支援、74 findings=24 partial+50 missing、0 truncated）；explicit domain=conduct+secondary（auto=false、27 findings）；empty text→400；unknown domain→auto-fallback。（本機 Supabase unconfigured → guideline 路徑 degraded，留 onrender 驗。）
  - **真 docx 端到端（browser preview 跑真 `buildAnnotatedOriginalDocx` on `dev/checklists/gifted/本校資優教育政策_學校版_小學_DRAFT.docx`）**：DOMParser document.xml + comments.xml well-formed；located 3/unlocated 2；commentReference id [0,1,2] == comment id [0,1,2]、comment body 非空；highlight 10；ct override + rels comments + 附錄齊。**捉到並修 self-closed `<w:comments/>` stub bug**（python-docx 自帶空 stub → `.replace('</w:comments>')` no-op → dangling refs → Word repair；加 self-closed 分支）。
  - **browser-verify**：app.html Babel 0 err、tab=[平台介紹/政策搜尋/📝文件標註/政策範本/EDB指引]（舊兩 tab 移除）；panel render（校類 5 opt 含幼稚園、自動/自選範疇 toggle、開始標註）；stub-fetch 驅動 paste→開始標註→report render（📌就地標示〔2〕+➕建議補充〔1〕+雙下載 button+paste-mode 提示+2 details）；fallback `buildAnnotateListDocx` PK-valid 8297B well-formed；0 console error。
  - **live e2e onrender（deploy 即時成功、無 S160 stuck）**：`/api/annotate-document` safety doc → ok/auto-detect 學校安全+學生支援/**3 guideline〔Supabase live、帶 LLM note〕**+24 partial+50 missing/0 truncated；CORS OPTIONS 204 + POST ACAO echo `https://policychecker.wongfu.net`；Pages app.html 13 feature markers live。
- **Data note:** span↔段落用 `annNorm`（去空白+CJK/ASCII 標點）includes / spanNorm⊇paraNorm（merged 段）/ 20-char prefix probe 三重容錯；highlight 段落級（v1，碎 run/表格命中率待真檔驗，寧入附錄唔錯位）。
- **Boundary:** 取代 2 個 live tab = 用戶可見（已 browser-verify + live e2e；Leonard 試用 sign-off 留反饋）。Supabase 15,109 未動（純前後端 feature、無入庫）。`AnalyzePanel`/`ReviewPanel`/`buildAnnotatedDocx`/`buildRevisedDocx` 變 dead code（保留、cleanup 列 follow-up；`REVISE_*` const 仍被新 panel 用）。
- **Doc Sync:** matrix row「New user-facing feature」triggered → README（功能/tab）、CODEBASE_CONTEXT（Stack JSZip + Directory annotateDocument.ts + AI log）、SESSION_HANDOFF（baseline/priorities/risks/last-record）、SESSION_LOG（本條）已更；K1_API_SPEC N/A（無 static-JSON 契約變）；DOC_ANNOTATE_FEATURE_DESIGN.md 標 Phase 1 SHIPPED。
- **commits:** `6885dbe`（文件標註 Phase 1：app.html + annotateDocument.ts + checklistRevise.ts + server.ts + spec）→ 收尾 gov（本條 + handoff + README + CODEBASE）。全 push origin/main。
- **Log maintenance (§4a):** SESSION_LOG >400 行、`docs/qa/session_log_maintenance.py` 仍不存在（legacy，同 S157-160）。No-op：延續舊 session 處理，本 session 聚焦 feature，建 script 留獨立小任務（不阻 handoff）。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Channel B live；0 outstanding bug。起手 verify HEAD==origin/main + Supabase 15,109。

S161（全權自主）完成：「文件標註」合併主線 Phase 1 SHIPPED LIVE — 合併 文件分析+文件修訂 → 一個「📝 文件標註」tab：上載 .docx → 比對 EDB 指引 + 合規清單 gap → 原檔就地標註（保留格式 + 螢光 highlight + 就地可見內聯建議（💡指引／⚠修訂）+ 未能定位項入文末附錄）→ 下載。新 backend/src/api/annotateDocument.ts（重用 analyzeDocument + checklistRevise，零改）+ /api/annotate-document；checklistRevise.ts +detectRelevantDomains（auto-detect）；app.html +AnnotatePanel +buildAnnotatedOriginalDocx（JSZip 操作原 docx XML）+ JSZip CDN；舊 #analyze/#review → #annotate redirect。live e2e onrender PASS。

NEXT（優先序，先等 Leonard 試用 Phase 1 反饋）：
① 文件標註 Phase 2（PDF inline highlight，pdf-lib+pdf.js 座標）/ Phase 2.5（per-segment detectQueryCategory auto-detect 取代 multi-select）；重點睇真實學校 docx 段落↔XML mapping 命中率（v1 段落級 highlight，碎 run/表格多嘅檔可能多入附錄）+ partial/missing 門檻噪音。
② dead code cleanup：AnalyzePanel/ReviewPanel/buildAnnotatedDocx/buildRevisedDocx 已無 render 引用；刪時保留 REVISE_SCHOOL_OPTS/REVISE_STATUS_META/REVISE_BACKEND_URL（新 AnnotatePanel 用）。
③ #2 幼稚園清單 pilot（用 kg_admin_guide_2026 / kg_operation_manual_2026 起 KG checklist→docx→政策範本 manifest，似 14 域 pipeline）。
④ #3 學校版 docx review（live，「政策範本」tab）。
⑤ monitor：文件標註門檻 COVERED=0.50/PARTIAL=0.42 tunable / kg_admin「幼稚園質素」→qa_inspection / IMC 頁碼 / cgss rank 低 / 57014 free-tier。

Key files（S161）：app.html（AnnotatePanel + buildAnnotatedOriginalDocx + buildAnnotateListDocx + tab merge + JSZip CDN）/ backend/src/api/annotateDocument.ts（新）/ checklistRevise.ts（+detectRelevantDomains）/ server.ts（+route）/ dev/DOC_ANNOTATE_FEATURE_DESIGN.md。
⚠️ 紀律：起 backend 改動前確認 Render deploy（S161 已正常）；live INSERT 前 INSPECT；新源 SOURCE_SETS+registry+display-sync 7 點；改 docx/checklist re-run gen_templates_manifest.py + gen_checklists_bundle.py；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: verify HEAD==origin/main + Supabase 15,109 + 探針 /api/annotate-document live（POST safety doc → 應有 guideline+checklist-gap findings），然後問 Leonard 文件標註 Phase 1 試用反饋 / 落手 Phase 2 定其他。
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

## 2026-06-13 Session 157 — verify_issues QC：全 128 issues 清晒（5 批）

- **ID:** Claude_20260613_0925 (S157)
- **Trigger:** Startup at 頂層 dormant scaffold → Leonard 確認切去 `Draft/` active root。續 S156 QC：清全部 124 pending verify_issues；Leonard 指示「5 個 batch 全部要做哂」→ scope→modal→bad-citation→distorted-number→fabricated 逐批清。
- **起手核實:** HEAD `f4daea4`==origin/main clean（handoff Current Baseline 舊寫 `46376f4` drift，本 session 修正）；Supabase 14,505 未動。
- **Completed — 全 128 verify_issues resolved（114 實改 / 1 核實正確 / 1 裁示保留 / 12 keep-as-is）:**
  - ✅ **Scope/eligibility（9）** — 還原 特殊學校/中學/官立及資助小學/按位津貼學校 被靜默擴大或縮窄嘅適用對象（本校（如屬X）voice）。
  - ✅ **Modal/terminology/entity（8）** — 須↔應↔宜↔可 對齊源文、第三層支援→第三層級、中、小學概覽、法團校董會→校董會 等。
  - ✅ **Bad-citation（28，含 21 額外 drift）** — 系統化重算 citations=covers-sources：g14 page -1→null（17 clause）、移除 4 spurious、補 5 missing、2 個 content 真係用到改加 covers（item18/item6）。0 residual citation drift 全 4 域。
  - ✅ **Distorted-number（31）** — 補回漏掉嘅義務動詞/機制/目的、修正數字日期術語（評分→評估準則、12月至1月、2016及2018注資、提早入讀較高班級）、entity scope。sen[3] 保留（角色列已含領導層）。
  - ✅ **Fabricated（66：55 移除 / 11 保留）** — 移除源文不支持嘅虛構義務/限定詞（書面/專業/維護/法定/個人化/不可或缺）、情態升級（不得→不應）、注入法律名稱、虛構表格 cell/欄；保留 11 條純可讀性目的句（以X/協助X，無新義務，依 Leonard QC-note 原則）。
  - ⚪ **qa_inspection[9] 核實無需改** — clause 跟足源文 quote「宜」；係 verify req paraphrase 誤升「須」（verify-against-source 救返 false positive）。
  - ⛔ **gov_admin[0] Leonard 裁示保留「書面同意」** — lead 主體=結構改動（item1 本須書面+規例10(a)），書面係安全一方。
  - ✅ docx regenerated 全 4 學校版（sen/gifted/gov_admin/qa_inspection）；checklist 版用 checklist.json 源文 quote，不受影響。
  - ✅ **QC_REVIEW.md：128 resolved / 0 pending**（sen 48/0, gifted 34/0, gov_admin 23/0, qa_inspection 23/0）。
- **Data-model trap（已存 auto-memory + 此處）:** verify_issues `item_id` ＝ clauses `covers` ＝ **章內局部編號（指 checklist.json sections[si].items），唔係 items_verified 全域 index**。直接 `items_verified[item_id]` 攞到無關 item（實證：sen[17] id2 真源喺 items_verified[24]）。正路：quote keyword 內容搜尋核實真源先改。另：citations 應＝covers items 嘅 (source_id,page) 集合（round-trip 不變不變式，可程式化驗 drift）。
- **QC:** 每批改後抽 docx document.xml grep 驗（新寫法 present / 舊失真 absent / 跨批無 regression / JSON valid）；clauses.json 改法 = raw string-replace（中文未 escape）或 json.load→dump(indent=2, ensure_ascii=False)（已驗 round-trip byte-identical）保 diff 最細。
- **Product zero-touch:** app.html / backend / Supabase / 公開 route 全未動。
- **commits（全 push origin/main）:** `6b76cf1`(scope+modal content)→`2fa557c`(gov)→`59644a0`(bad-cite+distorted)→`39b63bb`(fabricated)→收工 governance commit。
- **Log maintenance (§4a):** SESSION_LOG > 400 行、§4a script 不存在；本 session QC-only、未 archive；建議下個 product session 處理。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net).
Product state: HEAD = S157 governance commit（已 push）；Supabase 14,505；Channel B live；0 outstanding bug。
QC state: 14 範疇清單 + 學校版 docx（28 files）verify_issues QC 全清 — 128/128 resolved（見 dev/checklists/QC_REVIEW.md）。4 學校版 docx 已重生。
Next work（無緊急、可選）: (1) Leonard spot-check QC fixes / 11 條 kept-readability 目的句 + gov_admin[0] 書面 裁示 / qa[9] 核實 是否認同；(2) 文件分析 Phase 1.5（mobile shell）/ Phase 2（可下載標註文件）；(3) 其餘 10 域（curriculum/hr_admin/student_support/cpd 等，S155 報 0 verify_issues）如需可再 QC。
⚠️ Data-model trap: verify_issues item_id / clauses covers = 章內局部 index（指 checklist.json sections[si].items），唔係 items_verified 全域 index — 必用 quote 內容搜尋核實真源。citations 應＝covers items sources（可程式驗 drift）。
Post-startup first action: 問 Leonard 想 spot-check QC、定推進文件分析 Phase 1.5、定其他。
```

---

## 2026-06-13 Session 156 — QC pass：4 modal fixes + QC_REVIEW.md

- **ID:** Claude_20260613_1100 (S156)
- **Trigger:** Context-compaction resume. Leonard 指示「下一個 session 要繼續做」verify_issues QC。
- **Completed:**
  - ✅ START_NEXT_SESSION_PROMPT.txt 補寫（S155 closeout 時 Write blocked）
  - ✅ verify_issues 全覽（128 issues：sen 48 / gifted 34 / gov_admin 23 / qa_inspection 23）
  - ✅ 4 surgical modal fixes applied（清楚無歧義嘅情態詞失真）：
    - sen ch9 clause2：`本校須每年` → `本校宜每年`（source 用 宜，issue [31]）
    - gifted ch2 clause8：`本校統籌人員須協調` → `本校統籌人員應協調`（source 用 應，issue [7]）
    - qa_inspection sec5 clause1 table：`本校須以不記名` → `本校應以不記名`（source 用 應，issue [8]）
    - qa_inspection sec8 clause1：`本校每年須制訂` → `本校每年應制訂` ＋ `法團校董會` → `校董會／學校管理委員會`（source 用 應；SMC 選項漏失，issue [15]）
  - ✅ 6 docx regenerated（sen×2, gifted×2, qa_inspection×2）
  - ✅ QC_REVIEW.md — 128 issues 全部列表，標 fixed/review，包 high-priority scope qualifiers + modal + fabricated
  - ✅ BATCH_STATE.md updated
- **Not fixed (124 remaining):** fabricated clauses（rewriter 加入原文無嘅義務語句）、scope qualifiers（特殊學校/中學限定被靜默擴展）、其他 modal distortions（compound cases）— 見 QC_REVIEW.md
- **QC:** docx sizes consistent with before（sen 70279B→70279B；minor byte delta OK for content change）；gen_*.js validator PASS
- **Product zero-touch:** app.html/backend/Supabase 全未動
- **Log maintenance (§4a):** SESSION_LOG.md ~550+ 行 > 400 → trigger；但 §4a script 唔存在；最舊 entry 2026-06-10 < 30 天；本 QC session 短，手動評估：建議 Leonard 喺下個 product session 執行 archive
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: EDB K1 知識平台 (policychecker.wongfu.net). S155-S156 已完成 14 範疇清單 + 學校版 docx（28 files），S156 完成 4 modal QC fixes。
Product state: HEAD = S156 commit（已 push）；Supabase 14,505；Channel B live；0 outstanding bug。
Next work: 124 pending verify_issues → see dev/checklists/QC_REVIEW.md for categorized list with actions. Priority: scope qualifiers (特殊學校/中學 limitations being silently expanded) → remaining modal distortions → fabricated clauses.
Key files: dev/checklists/QC_REVIEW.md（128 issues, 4 fixed, 124 to review）; dev/checklists/<domain>/clauses.json（edit to fix）; _work/gen_checklist_docx.js + gen_school_docx.js（regenerate after fix）.
Post-startup first action: 問 Leonard 想優先睇邊個域嘅 verify_issues — 建議順序：sen（48 issues）→ gifted（34）→ gov_admin（23）→ qa_inspection（21 remaining）。
```

---

## 2026-06-11/13 Session 155 — 通宵自主批次：14 範疇清單 + 學校版 docx 全部完成（任務② DONE）

- **ID:** Claude_20260613_0900 (S155)
- **Trigger:** Leonard 授權通宵自主跑任務①（全庫頁碼分析）+ 任務②（14 範疇清單 + 學校版 docx）。安全界線：Supabase 只讀零改動；唔掂 product code；產出全落 `dev/checklists/`；git commit 留 Leonard 確認；repage 只分析不執行。
- **任務①:** 已於 S155 日間完成（PAGE_COVERAGE_REPORT.md，207 源/14,505 chunks，179 全頁碼/7 部分/2 全無/19 結構性無頁）。
- **任務②（本 session）:** 14 範疇 pipeline：distill → mech-verify → build-md → section-consolidation → mkflow-rewrite → extract-clauses → gen_checklist_docx + gen_school_docx
- **完成（全 14 範疇 × 2 docx = 28 files）:**
  - school_governance (489i/12ch/168c) ✅
  - kg_admission (41i/11ch/32c) ✅
  - placement (36i/12ch/24c) ✅
  - activity (139i/12ch/75c) ✅
  - conduct (82i/11ch/48c) ✅
  - safety (214i/12ch/97c) ✅
  - gov_admin (226i/14ch/120c) ✅
  - qa_inspection (47i/12ch/30c) ✅
  - hr_admin (193i/11ch/86c) ✅
  - student_support (235i/12ch/121c) ✅
  - cpd (91i/12ch/53c) ✅
  - sen (316i/12ch/142c) ✅
  - gifted (206i/11ch/85c) ✅
  - curriculum (634i/13ch/201c) ✅
- **Workflow 執行摘要:**
  - Batch1 (wf_8f802e04-8b6) school_governance/kg_admission/placement/activity rewrite ✓
  - Batch2 (wf_1c8fc329-957) conduct/safety rewrite ✓; gov_admin ch8-14+qa_inspection stalled → 新 wf_981151a6-c78 補跑 ✓
  - Batch3 (wf_c256dd7d-982) student_support rewrite ✓; cpd ch8-12+hr_admin stalled → 新 wf_967dee17-890 補跑 ✓
  - Batch4 (wf_0d2c0e0c-ba8) sen/gifted rewrite ✓
  - Batch5 (wf_88f3ba72-399) curriculum rewrite ✓
- **QC:** 各域 verify_issues.json 已存（sen 48 issues / gifted 34 / gov_admin 23 / qa_inspection 23；student_support/curriculum/cpd/hr_admin 0）— 供 Leonard 審閱，唔影響 docx 生成。
- **Git commit + push:** `122a7b9`（804 files）→ `4e496a2`（closeout）— **已 push** (68fe43d..4e496a2 → origin/main)。
- **Product 零接觸:** app.html / backend / Supabase / Channel A/B pipeline / 公開 route 全部未動。
- **Log maintenance (§4a):** 加本 entry 後 ~480 行 > 400 → 觸發 §4a；但 §4a trigger check script path = `docs/qa/session_log_maintenance.py`（唔存在）。手動評估：最舊 entry 2026-06-09 < 30 天，主要 trigger 係 line count；本 entry 後若超 400 建議 Leonard 手動 archive 或喺下個 product session 執行。
- **Next Session Handoff Prompt:**

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective: EDB K1 知識平台 (policychecker.wongfu.net). S155 已完成 14 範疇清單 + 學校版 docx（任務②全部 DONE，已 push）。
Product state: HEAD = 4e496a2（已 push origin/main）；Supabase 14,505；Channel B live；0 outstanding bug。
Next work: review verify_issues → clear-cut modal fixes（情態詞/範疇定義精準度）。
Key files: dev/checklists/<domain>/ — 14 個域各有 校本*清單_DRAFT.docx + 學校版_DRAFT.docx + clauses.json + verify_issues.json。
QC flags: verify_issues.json 非空嘅域（sen 48 / gifted 34 / gov_admin 23 / qa_inspection 23）— 下個 session 主要工作。
Post-startup first action: 讀 dev/checklists/BATCH_STATE.md 了解整體狀態，然後問 Leonard 想先睇邊個域嘅 verify_issues。
```

---

## 2026-06-10 Session 154 — (1) NEW 文件分析功能 + (2) IMC/SBM 校董會治理入庫 +229 + (3) Cloudflare 免 cookie 統計 + (4) 通告分析入口暫停 — ALL SHIPPED (deployed)

- **ID:** Claude_20260610_0100
- **Trigger:** Leonard 揀「新功能方向」→ 釘實 scope「用戶上載學校文件，系統加上相關指引資料及內容，輸回上傳者」→ AskUserQuestion 定格式(PDF文字層/docx/貼文字、無OCR)+輸出(Phase 1 螢幕報告、Phase 2 目標可下載標註文件)+私隱(交我評估→hybrid) → 中途 Leonard 問「香港 IP 出 OpenAI 會否被 block」→ 核實答覆 → `/goal 全力進行` 批准 PLAN 全速執行。
- **起手自測（全 live）:** HEAD `8bf828d`==origin/main clean / facts 455 三層(md5 4c3631) / Supabase 14,276(content-range 0-999/14276) / guidelines 152 / stats 14,276·152 / onrender /health 200 + manifest 401 ✓。
- **§3 Risk:** HIGH（新 user-facing feature + 上載 + OpenAI + 大單檔 app.html）→ PLAN 出咗等批先郁；CDN URL 先 curl-200 驗證（§0b 不靠記憶）。

### OpenAI 香港封鎖核實（Leonard 問；WebSearch 官方來源）
- HK 不在 OpenAI supported list；2024-07-09 起按**請求來源 IP** 封鎖（Vercel hkg1 案例）。**本架構用戶零影響**：browser(HK)→Render(美國，Render 根本無 HK 區)→OpenAI；現有政策搜尋已實證行咗呢條路好耐。會中招嘅只有 browser-direct call 或 HK-hosted backend（兩樣都冇做）。殘餘風險 = HK 註冊帳號層執法（low；行緊 150+ session）→ fallback = Azure OpenAI（官方支援 HK；swap 範圍 = llmClient.ts + embeddingClient.ts 兩檔，檢索邏輯不動）。

### CHANGE（3 檔：NEW analyzeDocument.ts + server.ts + app.html；mobile.js/shared infra 零接觸）
- **NEW `backend/src/api/analyzeDocument.ts`**：`segmentText`（空行分段；<30 字 stub 前併〔初版 60 被 unit smoke 捉到誤併 40-80 字真句、調 30〕；>1,200 字句界切）→ 每段 `searchChannelB({query:seg, top_k:4, synthesize:false})`（公開 API 複用 routing/頁碼/清洗/degraded 判別；併發 4）→ 一次 LLM call 出逐段一句提示（"N: …" 格式、`parseNotes` 容錯、best-effort 失敗唔沉 matches）→ 結構化 response（excerpt/status/matches{title,url,page,snippet}/note；degraded 顯示為 status:"error" 唔會扮無結果）。Cap：`MAX_TEXT_CHARS=60,000`、`MAX_SEGMENTS=12`（超出 → `skipped_segments` 可見截斷）。Stateless 零存儲。
- **`server.ts`**：`POST /api/analyze-document` 喺 10/min/IP limiter 之後；`readJsonBody` 加 optional `maxBytes`（default undefined = 現有 4 route byte-identical）；新 route cap ~244KB → 413「上載內容過大」。**QC 捉到 bug：初版 `req.destroy()` 喺寫 413 前 RST socket（client 收 connection reset）→ 修為 removeAllListeners+resume drain，413 正常送達。**
- **`app.html`**：+`pdf.js 3.11.174` + `mammoth 1.6.0` CDN（**pdf.js 3.x UMD 特登 — 4.x ESM-only 唔啱 no-build babel 頁**；defer + runtime guard）；NEW `AnalyzePanel`（檔案揀選/貼文字 textarea 單一 source、client-side 抽取〔PDF 文字層 <50 字 → 明示「掃描本不支援」〕、私隱提示框、字數 counter + 60k 前端 cap、逐段報告卡：excerpt + LLM 提示 + 指引 match 卡 `url#page=N`〔https-only allowlist + noopener noreferrer〕+ 無分數顯示〔跟 S153 de-score 方向〕+ fail-visible 錯誤/無 match/檢索失敗 三態 + 免責聲明）；`VALID_VIEWS` +'analyze'、第 4 個 tab「📄 文件分析」、router branch。**mobile.js 零接觸**（文件分析 = desktop React surface；平板 shell 入口 = Phase 1.5 — 唔係漏，係批咗嘅 scope）。

### QC（全 PASS）
- typecheck + build exit 0；unit smoke `segmentText`(5 case 含 10k 無標點不死循環/CRLF/全 stub/空白)+`parseNotes`(越界/全形冒號/first-wins)。
- **Local live e2e**（:8123 + 真 Supabase/OpenAI env）：3 段樣本通告 9.7s → 遊學團→`sch_activities_guide` p91（S152 新源！）/ 採購→`g01` p7+p12 / 校車→`g18` p2+p3，全帶頁碼；note 2/3 段（best-effort = monitor）。錯誤路徑：空 text→400 / 61k 字→400「文件過長…請分批」/ 480KB→**413**；現有 `/api/search/channel-b` 零回歸。
- Semantic regression：PASS=9 + notes=1 + **既知 2 FAIL（FAIL-A finance_distinct / FAIL-B 1.3.1 assert）0 新增**。
- **Browser-verify**（preview :8095，fetch-stub 模式同 S153）：4 tab render、AnalyzePanel 齊件、pdfjs+mammoth 載入、**真 pdf.js worker 頁內抽取成功**（自製 625B 測試 PDF，驗執行非可達）、stub 報告 10/10（summary/skipped 警告/note/`#page=91` link/無 match/error 段/無分數/免責）、qa·guidelines·about 三 tab 回歸 PASS、console 0 error。
- **對抗覆核 subagent（general-purpose，20+ runtime assertion）VERDICT PASS-with-flags、0 CRITICAL**。Flag 1（href 無 scheme allowlist）→ **已修**：`/^https?:/i` allowlist + noreferrer，重驗 `javascript:alert(1)` URL 降級純文字、正常 link 照出。Non-blocking 留底：JSON.parse 錯誤文字外洩（pre-existing 全 route pattern）/ byte cap 對 `\uXXXX`-escaped JSON 理論偏緊（自家前端 stringify 唔會中）/ degraded_kind 摺平令 unconfigured 時「請重試」措辭誤導（prod 唔會 unconfigured）/ `seg.matches` 依賴 backend contract 保證 / pre-existing duplicate borderRadius + 無 hashchange listener。
- **0 change**：searchChannelB.ts / wikiRepository.ts / knowledge·role_facts·guidelines.json / schema / RPC / mobile.js / index.html / 下游 / canonical chunker；無 bump（git diff --name-only 對抗覆核獨立確認）。

### Doc Sync
- **NEW row added**（anti-pattern guard）：「New user-facing feature (new public backend endpoint + frontend surface)」→ README 功能簡介 + CODEBASE_CONTEXT + HANDOFF/LOG + K1_API_SPEC only-if-downstream-contract-changes。
- 執行：README 功能表 +📄文件分析 row + 三 tab→四 tab note ✓ / CODEBASE_CONTEXT app.html tabs 行 + backend 檔列表 +analyzeDocument.ts + server.ts 行 + AI Maintenance Log S154 ✓ / SESSION_HANDOFF baseline #1·#2 + Open Priorities 重生 + Last/Previous→S154/S153 ✓ / 本 entry ✓ / **K1_API_SPEC 不改**（新 endpoint 唔屬下游靜態 JSON 契約）。

### Follow-up / lessons
- **Lesson**：分段參數（MIN_SEGMENT_CHARS）要用真中文通告樣本 smoke 先定 — 60 字會誤併 40-80 字真句；中文段落比英文短。
- **Lesson**：`req.destroy()` 喺 reject 後即斷 socket = client 永遠見唔到 413；要 removeAllListeners + resume drain 先寫到 response。
- **Lesson（複用勝自建）**：每段直接調用 `searchChannelB` 公開 API（synthesize:false）= routing/頁碼/清洗/degraded 全部免費複用 + shared infra 零修改；好過 import 私有 helper 或自己打 searchWiki。
- **Log maintenance（§4a）:** 加本 entry 前 285 行 → 收工 script check `trigger=False`（381 行 <400、最舊 <30d）→ no-op、無 archive。
- commits: `a6547c6`（文件分析 code）→ `d17c25d`（文件分析 governance）。

---

### ═══ PART 2 — IMC/SBM 校董會治理入庫 +229（同 session 接續）═══
- **Trigger:** Leonard：「指引欠校董會治理本體，都需要加入」+ 5 條 sbm.edb.gov.hk URL（3 加入：成立運作Ch5 / references index / 簡介會QA；2 Monitor：code-of-aid-IMC index + sch-admin-guide index）。
- **READ:** probe 3 URL 全 live；庫內 IMC 覆蓋 = g02(財務)+coa_imc_1_19(則例)+sag/g24(行政手冊)+sdp_guide — **缺校董會成立/運作/角色/會議/選舉治理本體**。Crawl references 子頁（imc-operation/sbm-documents/manager-election，靜態 href 可抽）enumerate 全套治理 PDF。**發現已有 `gov_admin` route 但喺 finance 之後，而 finance 佔 `法團校董` token（為 g02）→ 校董會查詢全 route 去 finance、治理源永不 surface**（retrieve-then-filter + 路由 precedence；phys_sss/cgss 同類教訓）。
- **Pre-flight:** 12 候選 PDF 全下載驗 → 全 **TEXT-OK**（U+FFFD=0、txtpg=全頁、page-resolvable、毋須 OCR）。對 Supabase url-match 查重 = 0（無 sbm host chunk、無該 source_id）。
- **設計決定（page 正確性）:** grouped 源連續頁碼 → `url#page=N` 只對第一份 PDF 準、appended overshoot；既然啱 ship 咗頁碼跳頁(S153)+文件分析賣點，**改 2-grouped → 4 源拆法**：`imc_establishment_operation`(2014手冊82pp 獨立) + `imc_briefing_qa`(QA2013 34pp 獨立) = 頁碼全對 62% 內容；`imc_governance_supplements`(6 細PDF) + `imc_election_guides`(4 PDF) 分組（細補充/選舉，第一份準）。
- **CHANGE:** fetch_extract 4 源 → ingest_one_source live（Supabase 14,276→**14,505**：97+48+27+57，per-source before=0 after=count 確認）。NEW `school_governance` route：SOURCE_SETS（4 新源 + g02 + coa_imc_1_19 + sdp_guide + role_facts_general）+ TOPIC_KEYWORDS `/法團校董會|校董會|校董|校監|辦學團體|學校管理委員會|校本條例/` **擺 finance 前**（governance nouns only，純財務 採購/招標/報價 唔含校董→唔被偷；`學校管理委員會` 全詞避免偷 safety `安全管理委員會`）。registry 212→216（4 entry，url_landing=sbm references 子頁→discovery 將來 watch SBM corner）。display sync 7 處 14,505（三層 md5 4c3631→**1bf7fd** byte-identical + app.html + index.html + K1_API_SPEC + README；facts 455/guidelines 152 不變、無 bump）。
- **Monitor（Leonard「要 Monitor 住」）:** code-of-aid-IMC + sch-admin-guide 兩 index 頁**已喺 discover_sources.py watch-list**（coa_imc_1_19 + sag_2025_11/g24 嘅 url_landing；collect_watch_pages 收 edb.gov.hk + 結尾 .html|/）→ 週跑已 cover、**無需改動**。
- **QC:** typecheck+build exit 0；routed smoke 4/4：法團校董會職權→imc_briefing_qa/establishment/supplements 帶正確頁、校董選舉→imc_election_guides #1、校董會會議→establishment+election+supplements、**採購門檻報價→g01/fin_mgmt/role_facts_finance（finance 唔被偷）**；semantic regression PASS=9+notes=1+既知 2 FAIL **0 新增**；browser-verify desktop（resize 1400，避開 mobile.js IIFE）About 14,505 + qa 副標「14,505 個 EDB 原文知識片段」+ 0 console error；**對抗覆核 subagent PASS-with-flags 0 critical**（12-query regex trace 確認治理 surface + finance/safety/conduct/hr/curriculum 零誤偷、`學校管理委員會`.test(`安全管理委員會`)=false、3 層 md5 byte-identical、facts 455 凍、version 2.3.0）；**post-deploy onrender 治理 route live（imc_* surface 帶頁、synthesis 373 字、finance intact）+ policychecker.wongfu.net 顯示 14,505 / 0 stale**。
- **Non-blocking flags（對抗覆核）:** gov_admin+finance 嘅 `法團校董` token 被 school_governance shadow 變 dead（無害可清）；`校政管理`/`校本管理`-alone gap → fall-through whole-index（非誤路）。grouped 源頁碼 overshoot = monitor。
- **Lesson:** (1) 路由 precedence — 新 route 要避開「上游 route 已佔關鍵 token」陷阱（finance 佔 法團校董 → governance 要擺前）；(2) grouped 連續頁碼 trade-off — 大文件獨立保頁碼正確，細 fragment 先分組；(3) **commit message `-m` 雙引號內反引號 ``school_governance`` 觸發 shell command substitution → message 嗰個位變空**（`46376f4` message 漏咗該詞，cosmetic）→ 教訓：`-m` 用單引號或避反引號。
- **DOC_SYNC:** 「Channel-B vault source backfill」row（已 registered）：registry 4 / SOURCE_SETS+TOPIC_KEYWORDS / HANDOFF baseline 14,505+216 / SESSION_LOG / CODEBASE AI-log + display 7 處 14,505。
- **0 change to** wikiRepository.ts / analyzeDocument.ts / knowledge·guidelines facts / schema / RPC / mobile.js / 下游 / canonical chunker。commits: `46376f4`（IMC code+data）→ `60da7f0`（IMC governance）。

---

### ═══ PART 3 — Cloudflare Web Analytics 免 cookie 統計（同 session 接續）═══
- **Trigger:** Leonard「加裝 cloudflare. 統計功能」→ Playbook INDEX 命中 `analytics-minors-cookieless` 卡（battle-tested）→ 方法 A 免 cookie beacon（私隱優先教育受眾、只需流量量級；唔用 GA4 = 無 cookie 無同意機制）→ 出 PLAN + 指引 Leonard 喺 Cloudflare dashboard 攞 token（唯一佢先做到嘅一步）→ Leonard 貼 snippet（token `8a65183a…` = 公開 client-side 識別碼、非 credential、可入 repo）。
- **§0b 核實:** 官方 get-started + limits docs fetch（免費 tier 10 個非-proxied 站；JS snippet 模式毋須搬 DNS）+ `beacon.min.js` curl-200（33KB）。
- **CHANGE:** 4 個公開 HTML（index/app/q/t-purchase）`</body>` 前各加一行 defer beacon script（python 批量 + 前置 assert：每檔 `</body>`×1、無既有 beacon）；index.html + app.html footer 加私隱細字「本站採用免 Cookie 匿名流量統計」（Playbook 卡要求）。
- **QC:** grep 4 檔各 exactly 1 beacon + 1 token；browser-verify **執行級**（CSP 卡精神：verify execution 非 reachability）— app.html + index.html 都觀察到 beacon.min.js 載入 **+ RUM POST 發射去 `cloudflareinsights.com/cdn-cgi/rum`**；footer 細字 render；0 console error。Post-deploy：policychecker.wongfu.net 4 檔 grep beacon ✓（見 closeout verify）。
- **架構記錄（Playbook 卡要求）:** 前端由「零對外 runtime 服務」→「+1（Cloudflare Analytics）」— CODEBASE_CONTEXT External Services 新 block（Doc-reviewed + Test-verified 2026-06-10）。收集範圍 = pageview/path/referrer/國家/裝置，無 cookie 無個人身分。報表：Leonard Cloudflare dashboard → Analytics & Logs → Web Analytics。
- **DOC_SYNC:** 「External API / service change」row → CODEBASE External Services block ✓ + AI log ✓；「Product behavior / tuning change」row → HANDOFF baseline/record + 本 entry ✓。
- commits: `37995bc`（beacon ×4 + footer 細字）→ `36af538`（governance）。

---

### ═══ PART 4 — 通告分析入口暫停（同 session 接續）═══
- **Trigger:** Leonard：「進入 EDB 通告分析系統 → 暫時 button 保留，但 link 就失效」。
- **READ:** 活鏈只有 index.html:361 `<a class="ftag">`；app.html intro 卡 `externalLink` 係 **dead data**（channels.map render 從未用過呢個欄位 — 卡片一直冇 link）。原 URL 實測 301→circular.wongfu.net→200（非 404）— 照指示停用、下游唔深究（§A.3）。
- **CHANGE:** index.html button → 停用 `<span>`「進入 EDB 通告分析系統（暫停開放）」（opacity .55 + cursor not-allowed + title；原 `<a>` 標記連 URL 留 HTML comment 恢復用）；app.html `externalLink` comment 掉（防將來誤接 render）。
- **QC:** browser-verify 兩 surface：index button 在+撳唔郁+無 `<a>` 殘留、app #about 卡照 render、grep 全公開 surface 零活鏈（淨 2 個恢復 comment）、4 tab、0 console error。post-deploy live grep 零活鏈。
- **DOC_SYNC:** 「Product behavior / tuning change」row → HANDOFF record + 本 entry ✓。
- commits: `0c34611` → 本 governance commit。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md。起手自行 verify git HEAD==origin/main + Supabase total（應 14,505）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 14,505/152）+ onrender /health + manifest 401-gated + app.html 四 tab（#analyze 文件分析在內）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S154 (2026-06-10) 四件事都 SHIPPED：
(1) **NEW 文件分析功能 — 第 4 公開 tab + POST /api/analyze-document**。用戶上載 PDF(文字層)/docx 或貼文字 → client-side 抽取（pdf.js 3.11.174 UMD + mammoth CDN；原始檔永不上載）→ 後端分段（<30字 stub 前併/>1200 句界切/12 段/60k 字 cap）→ 每段經 searchChannelB 公開 API（synthesize:false，shared infra 零改）→ 逐段報告（指引 url#page=N link + https-only allowlist + fail-visible + 私隱提示 + stateless）。server.ts +maxBytes（~244KB→413；修咗 RST-before-413）。
(2) **IMC/SBM 校董會治理入庫 +229 → Supabase 14,505**（Leonard：指引欠校董會治理本體）。4 源（sbm.edb.gov.hk references，全文字層 page-resolvable）：imc_establishment_operation(成立運作手冊2014, 97ch)/imc_briefing_qa(簡介會QA2013, 48ch)/imc_governance_supplements(Ch5/角色/會議/法例/良好管治/守則 6PDF, 27ch)/imc_election_guides(家長/教師/校友選舉+五步曲 4PDF, 57ch)。**新 school_governance route 擺 finance 前**（finance 佔 法團校董 token 為 g02，唔擺前則校董會查詢全 route 去 finance、治理本體永不 surface；SOURCE_SET 連 g02+coa_imc_1_19+sdp_guide）。registry 212→216；display 7 處 14,505（三層 md5 1bf7fd byte-identical、facts 455/guidelines 152 不變、無 bump）。**2 個 Monitor index 頁（code-of-aid-IMC + sch-admin-guide）已喺 discover watch-list — 已 cover、無需改。**
(3) **Cloudflare Web Analytics 免 cookie 統計**：4 個公開 HTML（index/app/q/t-purchase）`</body>` 前一行 defer beacon（token 公開 client-side 識別碼非 secret）+ index/app footer 私隱細字。Playbook analytics-minors-cookieless 卡方法 A（唔用 GA4）。報表喺 Leonard Cloudflare dashboard → Web Analytics。架構=前端 +1 對外 runtime 服務（CODEBASE External Services 已記）。
(4) **通告分析入口暫停**（Leonard：button 保留、link 失效）：index.html「進入 EDB 通告分析系統」→ 停用 span（暫停開放 + opacity/not-allowed；原 URL 留 comment 恢復用）；app.html intro 卡 externalLink comment 掉（dead data、從未 render）。兩 surface 零活鏈。
QC：typecheck/build/regression 0 新 FAIL；文件分析 local-e2e + browser-verify 10/10；IMC routed smoke 4/4（治理 surface 帶正確頁 + 採購/招標留 finance）；beacon 執行級驗證（RUM POST 觀察到）；兩個對抗覆核 PASS-with-flags 0 critical；post-deploy onrender 功能 live + policychecker.wongfu.net 14,505。**0 change to Channel A/knowledge·guidelines facts/schema/RPC/wikiRepository/mobile.js/下游/canonical chunker；無 bump。0 outstanding bug。** Commits a6547c6+d17c25d(文件分析) / 46376f4+60da7f0(IMC) / 37995bc+36af538(Cloudflare) / 0c34611+db4fe12(入口停用)。

Pending（全屬可選、冇緊急）:
1. 文件分析 Phase 1.5 = mobile.js 平板 shell 加入口；Phase 2 = 可下載標註文件（PDF/Word 旁註輸出）。
2. S154 monitor：IMC grouped 源（supplements/election）連續頁碼 url#page=N 只對第一份 PDF 準、appended overshoot（兩份大文件獨立=全對）；gov_admin/finance 嘅 法團校董 token 被 shadow 變 dead（無害）；LLM 逐段提示 best-effort；Azure OpenAI fallback 已查明（llmClient+embeddingClient swap、HK 帳號層風險用）。
3. 既有 monitor：synthesis ~328 字 soft cap / cgss_2024 rank 低 / gifted+CPD precedence / phys_sss / freshness+discovery 週跑只睇新 diff / 57014 cold-start / stats.sources=120 cosmetic-stale（live ~216）。

⚠️ Cautions：**文件分析私隱姿態 = 原始檔永不上載 + 文字經 server→OpenAI stateless** — 改 data flow 必改 UI 私隱文案。app.html 兩個搜尋 UI（React desktop + mobile.js shell）政策搜尋改動要兩邊改；文件分析淨 desktop（已知 scope）。入庫 per-source（fetch_extract→ingest_one_source；勿 full wiki_index upload）+ 新源必加 SOURCE_SETS allowlist + registry + display 7 處 + grouped 源大文件獨立保頁碼。**commit `-m` 用單引號/避反引號（反引號觸發 shell substitution）。未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines facts / 勿 bump_version / 勿 reopen §E.10 admin / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 14,505 / facts 455 三層 / guidelines 152 / stats 14,505·152 / onrender /health + manifest 401 + 文件分析 live smoke + 校董會 routed smoke〔「法團校董會職權」應 surface imc_* 帶頁〕）+ playbook INDEX 後，問 Leonard 想做邊樣，未明示前勿郁禁區。
```

## 2026-06-09 Session 153 — Channel B 政策搜尋 UX：分析放長(120→約250字) + 來源頁碼顯示/跳頁(desktop+mobile) + mobile 全中文檔名/去分數 — CLOSED (deployed)

- **ID:** Claude_20260609_1230
- **Trigger:** Leonard「Channel B 已成熟，分析可稍長 + 未見頁數可直接 refer 文件」→ PLAN(約250字 + 頁碼顯示/跳頁) → CHANGE → 中途 browser-verify 揭發第二 surface(mobile.js) → 再 Leonard「mobile 檔名要全中文 + 去走原文/0.50」+「desktop 都去分數」→ 全部部署。
- **起手自測（全 live）:** HEAD `17423ea`==origin/main / facts 455 三層(md5 4c3631) / Supabase **14,276**(content-range 0-999/14276) / guidelines 152 / knowledge.json stats 14,276·152 / onrender /health 200 + manifest 401 ✓.
- **§3 Risk:** HIGH（backend deploy + app.html 單檔 + mobile.js）→ PLAN + AskUserQuestion 確認長度/頁碼方式，未即改。

### READ — 兩個小根因（verify-in-browser）
- 合成寫死 120 字（`SYNTHESIS_PROMPT` literal；`llmClient` Responses API 無 max_output_tokens cap → prompt 係唯一長度閘）。
- backend 一直返 per-result `page`（`extractFirstPage`），`SourcesAccordion` 早有頁碼顯示碼 — 但 app.html `runChannelB` map results **漏咗 `page`**（只 `runCombined` 有）→ 頁碼永不顯示。
- **Browser-verify 揭發第二 surface**：app.html `<script src=mobile.js>` = React `#root` 以外嘅手寫 mobile shell（`body.mobile-shell-active`，Leonard 平板用嘅就係呢個）；結果卡/抽屜都冇頁碼、且顯示英文 raw source_id + 「原文 · 0.50」。

### CHANGE（4 檔）
- `searchChannelB.ts`+`searchCombined.ts`：`SYNTHESIS_PROMPT` 不超過120字 → 約250字(上限300, soft)。
- `app.html`：`runChannelB` map `page`；`SourcesAccordion` 頁碼→可點 `url#page=N`(PDF only) + 去「最高相關度 X.XX」分數。
- `mobile.js`：結果卡顯示頁碼；bottom-sheet「看 EDB 原文（第 N 頁）」跳 `url#page=N`；來源名全中文 `displayName`(SOURCE_LABEL[sid]→r.title→'EDB 文件'，永不 raw English sid)；去走「原文 · 0.50」channel-badge+score（approved_fact 保留 ✅已核實）。

### QC
- typecheck+build PASS；`node --check mobile.js` PASS；semantic regression PASS=9 + 2 已知 FAIL(FAIL-A finance / FAIL-B stale 1.3.1 assert)，0 新增；無 XSS（page 數字 / url escapeHTML / React escape）；0 console error。
- **live browser-verify 雙 surface（fetch stub）**：desktop SourcesAccordion = 4 個 `#page=N` link + 「N 個片段 · 頁 …」無分數；mobile = 中文名(資優教育政策文件及指引) + 頁 N + 抽屜跳 `#page=8` + 無 原文/分數；非-PDF/無頁 source 正確無頁碼/連結。
- **post-deploy curl smoke**：synthesis 135→**328 字** live（≈target，soft cap）；backend 全 result 帶 page。
- **0 change to** Channel A / knowledge·guidelines.json facts / schema / RPC / 下游 repo / canonical chunker；**無 version bump**（app.html precedent，displayVersion data-driven）。response schema 不變（synthesis 仍 string；`page` 早在 `ChannelBResult`）。

### Doc Sync（DOC_SYNC row: Product behavior / tuning change）
- CODEBASE searchChannelB 描述(≤120→約250 + page surfaced in UI) + AI-log S153；SESSION_HANDOFF baseline/Last/Previous/Open Priorities/risks；本 entry。

### Follow-up / lessons
- **Lesson**：app.html 有**兩個搜尋 UI**（React desktop `QAPanel` + vanilla `mobile.js` shell）— 任何 政策搜尋 結果渲染改動必須兩邊都改；verify-in-browser 嘅 screenshot 救咗一個本來會 desktop-only 嘅漏（Leonard 平板用 mobile shell）。
- **Monitor**：synthesis ~328 字略過 300 soft cap（gpt-4.1-nano 對 prompt 長度近似控制）— 過長可再收 prompt。
- **Lesson**：preview 嘅 `<script src=mobile.js>` 唔會被 doc-level cache-bust query 清；要 `fetch(url,{cache:'reload'})` + reload 先 load 到新 mobile.js（browser-cache，非 SW；已確認 0 service-worker）。
- **Log maintenance（§4a）:** SESSION_LOG <400 行、最舊 <30d → no-op。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md。起手自行 verify git HEAD==origin/main + Supabase total（應 14,276）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 14,276/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S153 (2026-06-09)：**Channel B 政策搜尋 UX — 分析放長 + 來源頁碼可顯示/跳頁（desktop + mobile）+ mobile 全中文檔名/去分數**。已 deploy（HEAD `6b91d8d`，Render redeploy backend + GitHub Pages 出 app.html/mobile.js）。(1) SYNTHESIS_PROMPT 120→約250字(上限300 soft；live ~328)（searchChannelB.ts + searchCombined.ts）。(2) app.html runChannelB map `page` + SourcesAccordion 頁碼→可點 `url#page=N`(PDF) + 去「最高相關度」分數。(3) **app.html load 第二 surface `mobile.js`（手寫 mobile shell，平板用）**：結果卡顯示頁碼 + 抽屜「看EDB原文（第N頁）」跳頁 + 來源名全中文(displayName) + 去走「原文·0.50」badge。QC：typecheck/build/node-check PASS、regression 0 新 FAIL、雙 surface live-verify、post-deploy synthesis 328 字。**0 change to Channel A/knowledge·guidelines facts/schema/RPC/下游/canonical chunker；無 bump。0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. monitor：synthesis ~328 字略過 300 soft cap（要更短可收 prompt）/ cgss_2024 routed rank 低 top-8 / gifted+CPD precedence / phys_sss routed-UI / freshness+discovery 週跑 / 57014 cold-start / stats.sources=120 cosmetic-stale。
2. discovery 餘 ~390 candidates 已 triage = noise/old/variant/已覆蓋；下次只睇新 diff。

⚠️ Cautions：**app.html 有兩個搜尋 UI（React desktop QAPanel + vanilla `mobile.js` shell）— 任何 政策搜尋 結果渲染改動必須兩邊都改**。入庫 per-source（fetch_extract/ocr_extract→ingest_one_source；勿 full wiki_index upload）；新源必加 SOURCE_SETS allowlist + registry + display sync 7 處。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines facts / 勿 bump_version / 勿 reopen §E.10 重建 admin / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 14,276 / facts 455 三層 / guidelines 152 / stats 14,276·152 / onrender /health + manifest 401）+ playbook INDEX 後，問 Leonard 想做邊樣，未明示前勿郁禁區。
```

## 2026-06-09 Session 152 — Discovery 全量 triage + B-group 補驗（全覆蓋確認）+ 入庫 7 個新發現源 → Supabase 14,276 — CLOSED

- **ID:** Claude_20260609_1004
- **Trigger:** Start → Leonard「1+2」(discovery triage + B-group 補驗) → 出發現 → Leonard「全做」(入晒新候選)。
- **起手自測（全 live）:** HEAD `0705762`==origin/main / facts 455 三層(md5 720f5f) / Supabase 13,667 / guidelines 152 / onrender /health 200 + manifest 401 / app.html admin 0 + 無 10,736 ✓。
- **§3 Risk:** detection (Task 1/2) = LOW；入庫 (全做) = HIGH（OpenAI embed + Supabase 生產 insert + routing + display）→ 逐源 pre-flight + verify-don't-trust。

### Task 2 — B-group 補驗：全覆蓋確認（決定性、同一主 PDF url match）
- 16 個 sibling-dup 全部核實 **COVERED**：每個現行主 PDF 已在庫（arts→g37 / pe→pe_kla_2017 / cs→ict_sss_2021 / pecg_2024_landing→g06 / g31→eng_pri / g32/g39/sci_kla→g35/tech_kla/g36 / moral_civic→mce_framework_2008 / 6 個 S149-150 control 重confirm）。`g08`(中文 Exemplar_01-14)= 補充教學示例、非主指引（主指引 CLEKLAG=g09 在庫）。**真‧未入‧現行主指引缺口維持清空。** Lesson：`(2025)` 括號 URL-encode 造成假負（pri_science），要 parens-safe 比對。

### Task 1 — Discovery 全量 triage（首次全量跑）
- `discover_sources.py --check --verbose`：54 watch pages / **400 candidates**（370 likely-real / 30 noise）/ 0 error / 0 js_suspect。
- 大部分噪音（Code of Aid 版本系列 59 / SECG booklet〔已 g13〕/ PECG 章節 / 入學統計 / 語言版本 / seminar PPT）。噪音過濾 + 逐個對庫 url-probe → 揀出真‧未入庫候選（全 0 命中確認）。

### 全做 — 入庫 7 grouped 源 +609（Supabase 13,667→**14,276**）
- 全 text-layer（fetch_extract，U+FFFD=0、page-resolvable）：`kgecg_2017` 幼稚園教育課程指引2017(108) — **補平台一直缺嘅 KG 課程指引** / `gifted_ge_series` 全民資優+才能庫+學術英才單元(346) / `cgss_2024` 特殊學校課程資源2024(17) / `sch_calendar_guide` 校曆/假期/上課日(6) / `sch_activities_guide` 戶外活動+境外遊學團(102) / `k1_admission_2627` 2026/27 K1入學(25) / `kg_admin_guide` 幼稚園學費/售賣(5)。
- 各加 SOURCE_SET route（curriculum/gifted/sen/hr_admin/activity/kg_admission）+ 2 keyword（activity 戶外活動/遊學團;kg_admission 學費/售賣物品）。registry 205→**212**（7 entry）。display sync chunks→14,276（3 層 _meta.stats byte-identical md5 720f5f→**4c3631** + app.html + index.html + K1_API_SPEC + README;facts 455/guidelines 152 不變、無 bump）。

### QC
- typecheck+build PASS;semantic regression PASS=9 + 2 已知 FAIL（FAIL-A finance / FAIL-B stale-version assert）**0 新增**;direct match_wiki_chunks RPC 7 源全 retrievable（kgecg/gifted/k1/kg_admin/activities 全 #1-2）。
- **routed smoke（onrender post-deploy）：6/7 surface 帶頁** — kgecg #1 p19 / gifted_ge #3-6 / sch_activities #1 p5 / kg_admin #1 p2 / k1_admission #1（proper「幼稚園K1入學」query）/ sch_calendar #8。**`cgss_2024` ABSENT**（在 sen route + direct-RPC 攞到，但 17 chunks 補充資源 rank 低於 top-8、輸俾主 g10/g19）= monitor-only（phys_sss pattern，Leonard-accept 類）。
- **0 change to** Channel A facts / knowledge·guidelines.json facts / schema / RPC / 下游 repo / canonical chunker。

### Doc Sync
- 「Channel-B vault source backfill」row：registry 7 entry / SOURCE_SETS 6 route + 2 keyword / HANDOFF baseline 14,276+212 / SESSION_LOG / CODEBASE AI-log ✓。「Product display number」row：chunks 7 處 14,276 ✓。

### Follow-up / lessons
- **Lesson**：coverage 核實用「同一份 PDF url 喺唔喺庫」最決定性（免 phrase-layout 假負）；但要 parens-safe（`(2025)` URL-encode 坑）。
- **Lesson**：小補充源（cgss 17ch）入 route 但 rank 低於 top-8 = retrieve-then-filter + 強主文檔競爭（g10/g19）;入庫+routed 正確、surfacing 受限 = monitor（同 phys_sss）。要 surface 須另開窄 route，17ch 唔值。
- **Discovery pending（之前 OP#1/#2）= DONE**：全量 triage 跑咗、揀晒真候選入庫;B-group 全覆蓋確認。餘 400 candidates 多數 noise/old/variant，無再入。
- **Log maintenance（§4a）:** SESSION_LOG ~220 行(<400)、最舊 S148(2026-06-07 <30d) → no-op。
- **§4 closeout:** handoff baseline 14,276/212、Last/Previous→S152/S151、Open Priorities 重生（discovery+B-group done）、cgss monitor 入 risks;START_NEXT 由下方 verbatim 重生。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md。起手自行 verify git HEAD==origin/main + Supabase total（應 14,276）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 14,276/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S152 (2026-06-09)：**Discovery 全量 triage + B-group 補驗（全覆蓋）+ 入庫 7 新發現源**。(1) B-group 16 sibling-dup 全 COVERED（同主 PDF 在庫）、缺口清空。(2) discover_sources.py 全量跑：54 頁/400 候選/0 error。(3) 全做入庫 7 源 +609 → Supabase 13,667→**14,276**：kgecg_2017(幼稚園課程指引2017、補 KG 缺口)/gifted_ge_series/cgss_2024/sch_calendar_guide/sch_activities_guide/k1_admission_2627/kg_admin_guide。各加 SOURCE_SET route + 2 keyword;registry→212;display 14,276(facts 455/guidelines 152 不變、無 bump)。QC：typecheck+build PASS、regression 0 新 FAIL、direct RPC 全 retrievable、routed smoke 6/7 surface 帶頁。cgss_2024 = in-route 但 rank 低 top-8(monitor、phys_sss pattern)。**0 change to Channel A/knowledge·guidelines facts/schema/RPC/下游/canonical chunker。0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. monitor：cgss_2024 routed rank 低(補充資源輸主 g10/g19、要 surface 須另開窄 route) / gifted+CPD route precedence / phys_sss routed-UI / freshness+discovery 週跑 / 57014 cold-start / stats.sources=120 cosmetic-stale。
2. discovery 餘 ~390 candidates 已 triage = noise/old-version/語言變體/已覆蓋（無再入）;下次 discovery 週跑只睇新 diff。

⚠️ Cautions：入庫 per-source（fetch_extract/ocr_extract→ingest_one_source;勿 full wiki_index upload）;新源必加 SOURCE_SETS allowlist + registry entry + display sync 7 處（3 層 _meta.stats + app.html + index.html + K1_API_SPEC + README;app.html/index.html chunks 已 data-driven 但 _meta.stats 本身要改）。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json facts / 勿跑 bump_version.py / 勿 reopen §E.10 重建 admin / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 14,276 / facts 455 三層 / guidelines 152 / knowledge.json stats 14,276·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣（新功能方向 / cgss 窄 route / 其他），未明示前勿郁上述禁區。
```

## 2026-06-08 Session 151 — app.html Channel A admin surface 完整移除 → 公眾完全 Channel-B-only（3 唯讀 tab）+ display 數字/version sync + de-jargon — CLOSED

- **ID:** Claude_20260608_1335
- **Trigger:** 起手自測全綠 → Leonard 揀「先睇全景」→ 出全景 → Leonard：「下游 Circular System 已刪去 Channel A 功能、集中 Channel B，所以應可刪去登入功能」。
- **起手自測（verify-don't-trust，全 live）:** HEAD `1fb4c22`==origin/main clean / facts 455 三層 byte-identical(md5 `720f5f`) / Supabase **13,667**(content-range 0-999/13667) / guidelines 152(4+6+132+2+4+1+3) / knowledge.json frozen 455 + stats 13,667·152 / onrender /health 200 cache_a 455 + manifest 401-gated / playbook INDEX ✓。egress 正常（onrender + Supabase 都通）。
- **§3 Risk:** HIGH（刪功能 + 改大單檔 app.html + reopen §E.10 admin gate + 觸 §F locked decision）→ 出 PLAN + 對 code 核實登入閘守乜 + AskUserQuestion 確認 scope，**未即改**。

### READ（verify against code，§G.2）
- 登入閘 = `adminMode` state（cosmetic SHA-256 `ADMIN_HASH`），守住 **7 類全 Channel A 人工策展**：知識提煉(候選 approve `CandidateReviewPanel`) / 知識管理(455 facts CRUD + sidebar) / 匯出 role_facts.json / +新增 / 批准 / FactCard 增刪改 / mobile admin bar。**app.html 0 個 Channel B admin 功能**（grep 確認無 prompt editor / 後台）→ Leonard 判斷 code 上成立。
- 公開 3 tab（平台介紹/政策搜尋〔S119 Channel-B-only〕/指引文件）不受影響。

### CHANGE — Leonard 確認 scope：完整移除 incl 死碼 + 455 facts 從 app.html UI 消失 + 完全 Channel-B-only
- anchored-splice Python one-off（`dev/_remove_admin.py`，15 區、各 `assert` anchor 命中、跑完即刪）移除：🔒登入掣 + `AdminPasswordModal` + `ADMIN_HASH`/`sha256` + 知識提煉/知識管理 2 tab + knowledge sidebar + 匯出/新增/批准/批量 + `FactCard`/`StatusBadge`/`RoleBadge`/`EditModal`/`ExportModal`/`CandidateReviewPanel` + 全 CRUD/review/candidate handlers + snapshot infra(`buildAdminSnapshot`/`migrateSnapshot`/`loadLocalSnapshot`/`downloadJson`/`LOCAL_SNAPSHOT_KEY`) + `INITIAL_REVIEW_STATE` + `INITIAL_CANDIDATES` + mobile admin bar。
- `App()` 收窄為 `data`(=INITIAL_DATA 唯讀)/`viewMode`/`switchView`/`previewDoc`/`displayVersion`/`stats`(簡化、無 reviewState)；`VALID_VIEWS=['qa','guidelines','about']`；router→about/guidelines/QAPanel(default)。
- 2 follow-up Edit：移除 2 條 orphaned `<script>`（candidate_queue.js/policy_signals.js）。留 `deepClone`(generic 未用、無害) + inert admin CSS（flag 未移）。
- **app.html 4100→2935 行（−1176；234,554→166,279 chars）。** git diff = app.html only +9/−1176。

### QC — 雙獨立流 + live render，全 PASS
- **grep parity**：~40 admin symbol（adminMode/ADMIN_HASH/reviewState/FactCard/ExportModal/CandidateReviewPanel/handle*/...）**0 dangling** + 0 leftover admin 中文 label。
- **live 瀏覽器 render**（static server :8095 → app.html）：Babel 編譯 **0 console error**；3 公開 tab render；點 guidelines→161 文件 + 分類/篩選；點 about→stat counter 定格 **455 / 13,667 / 161 / 120**（同改前 byte-identical 計算）；無 login/admin UI；screenshot 留證。
- **獨立對抗 review subagent（general-purpose，background）VERDICT PASS**：0 dangling use；braces 平衡；router 正確；`ReactDOM.createRoot().render(<App/>)` intact；3 公開 component + 預覽抽屜 props 滿足。非阻塞 flag：orphaned script tags（已移）+ inert admin CSS（留）。

### Doc Sync（DOC_SYNC row：Product behavior change + Long-term spec/locked decision）
- PROJECT_MASTER_SPEC §E.10(a) **CLOSED-BY-REMOVAL S151** + §F.11 新 locked decision + §B.1 admin rows 劃走；CODEBASE_CONTEXT app.html tabs(line 13/69) + AI-log S151；README 功能簡介 → Channel-B-only + 劃走 admin rows + 更新搜尋描述；SESSION_HANDOFF baseline/priorities/risks/Last+Previous record；本 entry。
- **NEW chip `task_672056cf`**：app.html QAPanel 搜尋副標題硬編碼 chunks=`10,736`（應 13,667）= pre-existing display-drift，spun off 另修（非本 session admin-removal 範圍）。

### Follow-up / lessons
- **Lesson**：大單檔多區手術，anchored-splice（短 unique anchor〔function 簽名/comment marker〕+ 每區 assert）比逐個 reproduce 全 block 嘅 Edit 穩陣，且可程式化驗 count；git 做 backup。
- **Lesson（§G.2）**：「登入閘守乜」load-bearing 判斷對 code 核實先動手（確認 0 個 Channel B 功能被守）— 唔靠假設。
- **0 change to** knowledge.json / role_facts.json / guidelines.json / backend / Supabase / schema / RPC / downstream repo(§A.3) / canonical chunker。凍結 Channel A 資料 + 對外契約零接觸（admin 只 client-side localStorage、無真實寫）。
- **無 version bump**（knowledge 凍結 @2.3.0；displayVersion 由 `data._meta.version` 動態取；所有顯示 version 核實一致 = 2.3.0 knowledge / 2.5.0 guidelines）。
- **[同 session follow-up — display 數字 + de-jargon]（Leonard：「快手 update 所有 version 及數字 + 去掉顯示 Channel A/B 內部字眼」）**：(1) **數字** — app.html QAPanel 搜尋副標題(B+AB)硬編碼 chunks `10,736` → **data-driven** `${(data._meta?.stats?.chunks||13667).toLocaleString()}`(=13,667)；index.html 3 處 `data-stat="chunks"` fallback 10,736→13,667；核實其餘 sync points(3 層 _meta.stats / K1_API_SPEC / README) 早已 13,667、facts 455 / guidelines 152 一致。(2) **de-jargon**(UI 可見) — About stat sub 'Channel A 人工審核'→'經人工審核' / 'Channel B 向量索引'→'語義向量索引'；feature subtitle 'Channel A + B 合併'→'EDB 原文語義檢索'；demo label→'語義檢索'；result badge '通道 A/B · …'→'已核實'/'統計'/'EDB 原文'；footer '管理中心'→去除(淨 'v2.3.0')。code 識別符/註解(runChannelA/B 等)唔顯示、保留。QC：live render Babel 0 error、About 455/經人工審核·13,667/語義向量索引、搜尋副標 13,667、footer v2.3.0、0 可見 Channel A/B、index.html 3×13,667。
- **Log maintenance（§4a）:** SESSION_LOG 達 **485 行（>400 line-trigger）** → 跑 `session_log_maintenance.py --apply`，封存最舊 N 條入 `dev/archive/SESSION_LOG_2026_Q2.md`、保留最近 2 條(S151 + S149-150) + archive pointer。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md。起手自行 verify git HEAD==origin/main + Supabase total（應 13,667）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 13,667/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S151 (2026-06-08)：**app.html Channel A admin surface 完整移除 → 公眾完全 Channel-B-only + display 數字/version sync + de-jargon**。(1) 刪 admin：🔒登入閘 + AdminPasswordModal + ADMIN_HASH/sha256 + 知識提煉/知識管理 2 tab + CRUD/匯出/批准 + FactCard/ExportModal/EditModal/CandidateReviewPanel + snapshot infra + INITIAL_REVIEW_STATE/INITIAL_CANDIDATES + mobile admin bar + 2 orphaned <script>。App() 收窄、VALID_VIEWS=['qa','guidelines','about']、router→about/guidelines/QAPanel。app.html 4100→2935 行。§E.10(a) CLOSED-BY-REMOVAL、§F.11 locked。(2) display：QAPanel 搜尋副標 + index.html chunks fallback 10,736→**13,667(data-driven)**；UI 去掉 Channel A/B 內部字眼（About sub / result badge / footer 管理中心）。QC：grep 0 dangling + live render Babel 0 error + 3 tab + About 455/13,667/161/120 + 搜尋副標 13,667 + 0 可見 jargon + 對抗 review PASS。**0 change to knowledge.json/role_facts/guidelines/backend/Supabase/schema/RPC/下游 repo/canonical chunker。0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. discovery crawler 跑全量 triage / 餘 10 B-group sibling-dup 深驗。
2. monitor：gifted+CPD route precedence / gifted_osalp catalogue 排名低 / phys_sss routed-UI 限制 / freshness 週跑 / 57014 cold-start / stats.sources=120 cosmetic-stale。

⚠️ Cautions：app.html admin/Channel-A 策展功能已永久移除，重建必由零走 §3 HIGH-risk + 真 server-side auth（勿復活 client-side cosmetic gate）。chunks 係 moving display number（補入庫同步 6 處：3 層 _meta.stats + app.html + K1_API_SPEC + README；app.html QAPanel 副標 + index.html 已轉 data-driven）。入庫 per-source（fetch_extract/ocr_extract→ingest_one_source；勿 full wiki_index upload）；新源必加 SOURCE_SETS allowlist（S135）。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 重建 admin / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 13,667 / facts 455 三層 / guidelines 152 / knowledge.json stats 13,667·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣（discovery triage / B-group 補驗 / 新功能方向 / 或其他），未明示前勿郁上述禁區。
```

## 2026-06-08 Session 149-150 — Channel B 補入庫實質完成（安全指引 + gifted 6 源 +209）+ 2 新 dedicated routes + NEW 自動發現工具 — CLOSED

- **ID:** Claude_20260608_1223
- **Trigger:** 起手自測全綠 → Leonard 揀「Channel B 補入庫」→ 安全指引 3 源 → gifted（Leonard 逐批畀 link）→ 問「全部入晒未 + 有冇自動偵測新文件機制」→ 建自動發現工具。
- **起手自測（verify-don't-trust，全 live）:** HEAD `f26a8a7`==origin/main / facts 455 三層 byte-identical(md5 `7e7ac1`) / Supabase 13,473 雙讀 / guidelines 152 v2.5.0 / knowledge.json frozen + stats 13,473·152 / onrender 200 + manifest 401 / playbook INDEX ✓。
- **§3 Risk:** HIGH（OpenAI embed + Supabase 生產 insert + shared routing edit + display）；逐 gate（pre-flight→ingest→allowlist→regression→check/build→display→commit→deploy→routed smoke）。

### Live gap 對賬（按內容、非靠 stale doc）
- Supabase 190 distinct 源 / registry 203 → **34 未入庫**。分類：deprecated/dead 6 + sibling-dup ~17 + 舊版噪音 ~7 + gifted(待 link) → **真‧未入‧現行內容唯一 = 安全指引家族 g18/g21/g22**（g23 體育已在庫）。
- B-group sibling-dup 抽 6 代表**深層內容核實**（非靠 S146 標籤）：sci_curr_docs→g36 6/6 / tech_curr_docs→tech_kla_guide_2017 6/6 / pshe_curr_docs→g35 6/6 / pri_science→pri_science_guide_2025 / ph_pri_curr→ph_pri_guide_2025 / ma_curr_index→ma_kla_guide_2017（同一 ME_KLACG PDF 136 chunks；深層 math-layout phrase 偽負，查證實 PDF 相同）→ **dup 標籤站得住**。

### S149 — 安全指引 3 源 +115（13,473→13,588）
- `g18` 學童乘搭校車安全指引 2025/26（Schools 6pp + committee 2pp）+9 / `g21` 視覺藝術科安全指引（pri 22 + sec 26）+48 / `g22` 科技教育安全指引 2010（52pp）+58 = 全文字層 `fetch_extract`（pre-flight U+FFFD=0、毋須 OCR）。
- 加 `SOURCE_SETS.safety` + 窄 `TOPIC_KEYWORDS.safety`（`校車|視藝.{0,3}安全|視覺藝術.{0,4}安全|科技教育.{0,4}安全|科技科.{0,3}安全`，全現時 match 唔到 = 零 regression）。routing regression 12/12 PASS（含 視覺藝術科課程指引→curriculum、資訊科技保安→null 唔誤入）。
- Display sync 6 處（md5 7e7ac1→d87f0d）。QC：Supabase 13,588 雙讀、per-source 9/48/58、emb 1536、check+build PASS。direct RPC 全庫 top-2、routed smoke 3 源各 **#1 帶頁碼**（≠ S148 phys_sss，因 whole-index rank 高 + 入 safety route）。commit `e763f9f`。

### S150 — gifted 3 源 +94（13,588→13,667）+ NEW gifted route
- `gifted_policy_docs` +19：Leonard 畀正確 link → `policy_chin_March08.pdf`(資優教育政策文件2008, 8pp) + `hong-kong-development` introduction.html + detail.html（**混合 PDF+HTML 砌**：fetch_extract PDF pass 後 append HTML pass）。**`ecr4_c.pdf` 全本 ECR4 1990(175pp、資優只 ~p45-61、98% 非資優)§3 stop-and-report → Leonard 拍板 skip**（免通用舊政策稀釋）。
- **NEW dedicated `gifted` route**：`SOURCE_SETS.gifted`[gifted_policy_docs/g14/g06/role_facts_general] + `TOPIC_KEYWORDS.gifted`(資優/資賦/天才教育/拔尖保底/gifted，置 curriculum 前) + `QUERY_EXPANSIONS.gifted`。亦令既有 g14(校本資優指引)/g06 終於有 route。regression 19/19 PASS（含 資助則例→finance 唔被搶）。
- 再 +2 Leonard link（separate registry-backed sources、無 DELETE）：`gifted_tp_resource_kit`(校本資優教育資源套2024, 32pp 實質指引)+41 / `gifted_osalp_compendium`(OSALP 課程匯編, 20pp catalogue)+19。加入 SOURCE_SETS.gifted + registry 2 entry（clone g21 schema）→ 203→**205**。
- routed smoke：資優 query → gifted set（g06+g14+gifted_policy_docs+tp_resource_kit）帶頁碼；tp_resource_kit #1。**monitor：含「教師培訓/CPD」詞 → cpd first-match（gifted set 唔 surface）；osalp catalogue 排名低**。commits `79cea74`(route)→`180ec67`(+2)。

### NEW 自動發現工具（答 Leonard「自動偵測新文件」）
- `dev/source/discover_sources.py`：freshness 嘅 companion。freshness 監察**已登記**源改版/死链；discovery **crawl 已登記 EDB index 頁（registry url_landing）→ diff doc-links vs known URLs → surface 未登記新文件**。detection-only、唔寫 registry、唔 ingest。`--check`/`--self-test`(11 assertions)/`--changes-out`/`--ledger`/`--limit`。likely_noise flag(poster/leaflet/dup-basename)但唔 drop（over-list>hide）。限制：static-fetch(JS 頁 flag js_suspect)、只搵 watched index 頁底下、landing 多 dup = triage list。
- `.github/workflows/discover_check.yml`：每週一 10:00 UTC（freshness 後 1h）+ manual dispatch → 開/更新 `new-source-discovery` Issue。self-test 11/11、live crawl 0 error。commit `497d6af`。

### freshness「7 changed」核實 = 0 真改
- 7 個全 `head-metadata (no baseline hash)` = 首次 seed baseline artifact + EDB Last-Modified flutter（多個 timestamp 倒退）。g21=今 session 啱入；g39=0-chunk 舊 dup；g19 + pri_science_cert_course_list 深層內容**確認 current 8/8**。→ 冇嘢要 backfill。

### Doc Sync
- 「Channel-B vault source backfill」row：registry（6 源 notes/2 新 entry）/ SOURCE_SETS（safety +3、gifted route 新增 +5）/ HANDOFF baseline 13,667 / SESSION_LOG / CODEBASE AI-log / INGEST_GAP S149+S150 標 ✓。
- 「External / tooling change」row：CODEBASE Directory Map + AI-log 加 discover_sources.py + discover_check.yml ✓。
- 「Product display number」row：chunks 6 處同步 13,667 ✓。

### Follow-up / lessons
- **Lesson（§G.2 再中、雙向）**：(1) freshness「7 changed」唔好當真改 — confidence `head-metadata no-baseline` = seed artifact；(2) 我自己嘅 B-group dup 核法初版用 front-matter boilerplate phrase → 偽 COVERED（4/6 同一噪音 holder set），改深層 phrase 先準；ma 深層又因 math-layout 偽負 → 查 registry url 證同一 PDF。**load-bearing 判斷連自己嘅 verification 方法都要 verify。**
- **Lesson**：混合 PDF+HTML 源 = fetch_extract 兩 pass（PDF mode → append HTML body 去同一 vault 檔，strip temp header）。
- **Lesson**：安全/資優呢類 dedicated tight route = routing-is-the-lever（S118 pattern）；新 source whole-index rank 高時 routed 即 #1（≠ phys_sss）。
- **Log maintenance（§4a）:** SESSION_LOG 369 行(<400)、最舊 S144(2026-06-05 <30d) → no-op、無 archive。
- **§4 closeout:** handoff reconciled（baseline HEAD 180ec67 + Supabase 13,667 + md5 720f5f、Open Priorities 重生、Last/Previous→S149-150/S148、新 route+工具+monitor 入 risks）；DOC_SYNC 3 row ✓；START_NEXT 由下方 verbatim block 重生。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md（補入庫進度，S149-S150 已標）。起手自行 verify git HEAD==origin/main + Supabase total（應 13,667）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 13,667/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S149-S150 (2026-06-08)：**Channel B 補入庫實質完成 + 自動發現機制**。(1) S149 安全指引 g18 校車/g21 視藝/g22 科技 +115 → 新 safety route keyword。(2) S150 gifted 3 源（gifted_policy_docs + gifted_tp_resource_kit + gifted_osalp_compendium）+94 → NEW dedicated gifted route（亦救 g14/g06）；ecr4 全本 1990 skip。(3) NEW dev/source/discover_sources.py + .github/workflows/discover_check.yml（每週一 10:00 UTC 自動 crawl 已登記 index 頁 diff 出未登記新 EDB 文件 → new-source-discovery Issue；detection-only）。Supabase 13,473→**13,667**，registry 203→205，md5 720f5f。真‧未入‧現行內容缺口核實清空（B-group dup 抽 6/16 深層確認）。**0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. discovery crawler 跑全量 triage（手動 GitHub Actions dispatch 或下次 session；噪音多 = review list 非 auto-ingest）。
2. 餘 10 個 B-group sibling-dup 未深驗（可選補驗確定覆蓋）。
3. monitor：gifted query 含「教師培訓/CPD」詞會 route 去 cpd（first-match，gifted set 唔 surface；要 surface gifted PD 可移 gifted 前於 cpd）/ gifted_osalp_compendium catalogue 排名低 / phys_sss routed-UI 限制 / freshness 週跑 / 57014 cold-start / stats.sources=120 cosmetic-stale。

⚠️ Cautions：chunks 係 moving display number（每次補入庫同步 6 處〔3 層 _meta.stats + app.html + K1_API_SPEC + README〕）；入庫 per-source（文字層 fetch_extract、掃描/CID ocr_extract、再 ingest_one_source；勿 full wiki_index upload）；新源必加 SOURCE_SETS allowlist（S135）；大 OCR job pace org TPM。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra（match_count/expansion）/ 勿再 ingest 結構天花板源。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 13,667 / facts 455 三層 / guidelines 152 / knowledge.json stats 13,667·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣（discovery 全量 triage / B-group 補驗 / 新功能方向 / 或其他），未明示前勿郁上述禁區。
```

## 2026-06-07 Session 148 — Channel B 補入庫 follow-up 1-3：phys_sss/chi_edu全本/g13(文字層) + g16(OCR) → Supabase 13,473 + display sync — CLOSED

- **ID:** Claude_20260607_1740
- **Trigger:** Leonard 揀可選 follow-up「1-3 做」（phys_sss / chi_edu 全本 / g13·g16）；#4（g17 深化 / gifted）待有正確 link 再深究。
- **起手自測（verify-don't-trust，全 live）:** HEAD `188a5db`==origin/main clean ✓ / facts 455 三層 byte-identical(md5 `d3b80c`) ✓ / Supabase 12,484 ✓ / guidelines 152 v2.5.0 ✓ / knowledge.json frozen 455 + `_meta.stats` 12,484·152 ✓ / onrender /health 200 cache_a 455 + channel-b/manifest 401-gated ✓ / playbook INDEX(地圖) ✓。
- **§3 Risk:** HIGH（外部 API：OpenAI embed+vision + Supabase insert）；逐 gate（pre-flight→extract→ingest→allowlist+build→display→commit）。

### Pre-flight（非破壞試抽，verify-don't-trust）
- **phys_sss_2007_2015**：registry url=.pdf；實抽 150pp、cjk 19,106、**U+FFFD=0 = 文字層 OK**（handoff 估「2015 舊版可能要 OCR」**係未驗假設、實際 clean** — §G.2 再中）。
- **chi_edu 全本**：index 頁爬出真檔 = `CLEKLAG_2017_for_upload_final_R77.pdf`（g09 只係佢 p43-48 節錄）；103pp 文字層 OK。
- **g13 SECG**：index 頁 = 中學教育課程指引(2017)，Intro+booklet 1-11+6A-6D+Supp_notes **17 PDF / 555pp 全文字層 OK**（剔 SSCG_2009 舊版 + PDPO boilerplate）。
- **g16 訓育**：8 章（preface+ch1-6+capp）**全 CID 亂碼（cjk=0/U+FFFD=0）→ OCR**（剔 PDPO）。
- **Supabase dup 對賬**：phys_sss/chi_edu_curr_docs/g13/g16 **四個 source_id 全 0 = clean 新源**；g09 現有 10（CLEKLAG 節錄）→ **Leonard 拍板「保留 g09 + 全本另存」**（per-source quota 限重疊，同 g38/music 並存模式）。

### CHANGE / QC（四源一次過）
- **phys_sss_2007_2015**：`fetch_extract` 149pp → `ingest_one_source` **+182**（topic curriculum、page-resolvable）。
- **chi_edu_curr_docs**：`fetch_extract` CLEKLAG 100pp → **+157**（curriculum）；與 g09 並存（per Leonard）。
- **g13**：`fetch_extract` 17 PDF 554pp（連續頁碼）→ **+587**（curriculum）。
- **g16**：`ocr_extract` 117pp（concurrency=2、dpi200）→ **0 失敗單 pass**（Retry-After 騎過 TPM、毋須 resume；2 個〔不清楚〕draft）；topic header conduct→**student**（conduct∉VALID_TOPICS、訓育→student_support）→ **+63**。
- **allowlist `searchChannelB.ts`**：phys_sss/chi_edu_curr_docs/g13 加入 `SOURCE_SETS.curriculum`；**g16 已在 `student_support`（S142 預埋、只係當時無 data）= inverse coupling，無需改 allowlist**。
- **display sync**：chunks 12,484→**13,473** 改齊 6 處（3 層 `_meta.stats` byte-identical md5 `d3b80c`→`7e7ac1` + app.html〔stats+`||`〕+ K1_API_SPEC + README 12,484→13,473）；guidelines 152 不變；無 bump version；`updated` 不動（facts 仍 455）。
- **Supabase 12,484→13,473**（**+989** content-range 雙讀）；per-source 182/157/587/63 全對；抽樣 embedding dim=1536 non-null；backend `npm run check`+`build` PASS。
- **direct match_wiki_chunks RPC（繞 routing、whole-index top-100）**：chi_edu **#1** @0.718 p24 / g16 **#1** @0.693 p17 / g13 **#4** @0.651 p37 / phys_sss **#97** @0.504 p144（phys 喺全庫低 rank 屬正常 — 物理 query 同全 curriculum 競爭；routed curriculum set 收窄後會升，**待 deploy 後 routed smoke 確認**）。
- **0 改** Channel A facts / knowledge.json facts / guidelines.json / schema / RPC / 下游 repo / canonical chunker。

### Doc Sync
- 「Channel-B vault source backfill」row：registry（4 entry 已存在、URL 正確 = 已 parity，加 S148 notes）/ SOURCE_SETS curriculum +3 / HANDOFF baseline 13,473 / SESSION_LOG / CODEBASE AI-log / INGEST_GAP 標 done ✓。
- 「Product display number」row：chunks 6 處同步 ✓。

### Follow-up / lessons
- **Lesson（§G.2 再中）**：「2015 舊版＝可能要 OCR」係未驗假設；phys_sss 實際文字層 clean。入庫前一律 pre-flight 試抽驗文字層，唔好靠 handoff 標籤估路線。
- **Lesson**：g16 allowlist 喺 S142 已預埋（student_support），只欠 data = backfill-allowlist coupling 嘅 inverse；補 data 後即自動 surface，毋須改 allowlist。
- **Lesson**：117pp OCR 喺 concurrency=2 + Retry-After 可單 pass 0 失敗（g38 153pp 用 concurrency=6 撞 TPM 嘅教訓已內化）。
- **Cleanup（Leonard 批「做」）**：`git rm` 走 stale duplicate `dev/vault/phys_sss_2007_2015/extract_phys_sss_2007_2015_repaged.txt`（2026-05-01 expand_vault 自動產、**同 source_id** = latent double-pick 地雷）。今次入庫已驗證用咗正確新檔（`build_rows` 取 `srcs[0]`、live Supabase phys_sss=182 不受影響——純本地 vault 檔）。全 vault 掃描確認**再無其他同 source_id 重複** → 回復 one-extract-per-source invariant。第二個 commit。
- **Routed smoke（post-deploy live）：** `chi_edu_curr_docs` **#1** @0.738 p24 / `g13` **#3** @0.711 p56 / `g16` **#1** @0.693 p17 — 三源完美 surface 帶頁碼。**`phys_sss` ABSENT**（即使 over-fetch 150）。
- **phys_sss 根因（已驗、§3 執行偏離 stop-and-report → Leonard 拍板「接受現狀」）：** routed search = retrieve-then-filter（`wikiRepository.ts:130-181`：RPC 攞 top `top_k×5`〔預設 40〕**全庫** → app filter SOURCE_SET）+ query expansion（`searchChannelB.ts:552` 加通用 curriculum 詞）。phys_sss 全庫排 ~**#97**（物理同眾理科共詞、expansion 再稀釋）→ 入唔到候選池 → 被 filter 走。**但入庫完全正確**（182 chunks、embeddings 1536 valid、在 curriculum allowlist、direct match_wiki_chunks RPC #97 @0.504、**下游 Circular System by-id 增量同步完全攞到**——routed UI 只係其中一個 consumer）。唯一缺口 = app.html 智能搜尋 UI 對「物理」query 唔頂返。**Leonard 接受現狀**（§8b monitor-only、唔郁 shared 檢索 infra）；將來若要 surface = 另開 dedicated 理科 route（routing-not-cutoff lever、S118 pattern）。
- **commit/push:** `269df97`(入庫+allowlist+display) → `4ea85ec`(rm stale duplicate) → `cd42d22`(routed smoke 入 governance) → S148 closeout commit。
- **Log maintenance（§4a）:** no-op — SESSION_LOG 346 行（<400）、oldest entry S144（2026-06-05，<30d）；無觸發 archive。
- **§4 closeout:** handoff reconciled（Last/Previous Session Record→S148/S147、baseline chunks 13,473、Open Priorities 重生、phys_sss limitation 入 monitor）；DOC_SYNC row 35（Channel-B vault backfill）✓；START_NEXT_SESSION_PROMPT.txt 由下方 verbatim block 重生。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md（補入庫進度）。起手自行 verify git HEAD==origin/main + Supabase total（應 13,473）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 13,473/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S148 (2026-06-07)：**follow-up 1-3 完成入庫** — phys_sss_2007_2015 +182（文字層、非 OCR）、chi_edu_curr_docs（CLEKLAG 全本）+157、g13（SECG 17-PDF）+587 = fetch_extract 文字層；g16（訓育 8 章 CID）+63 = ocr_extract（117pp concurrency=2 0 失敗）→ Supabase 12,484→**13,473**（+989）。前 3 加 SOURCE_SETS.curriculum、g16 已在 student_support。Display chunks 6 處同步 13,473（三層 byte-identical md5 7e7ac1）。清走 stale duplicate phys_sss…_repaged.txt。Routed smoke：chi_edu #1 / g13 #3 / g16 #1 完美；**phys_sss ABSENT**（retrieve-then-filter top-40 全庫 + expansion 稀釋、全庫 ~#97）→ **Leonard 接受現狀**（入庫正確、下游 by-id sync 攞到）。**0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. gifted_policy_docs（待 Leonard 正確 link）+ g17 深化（同 #4 link 一齊做）。
2. 餘 ~9 registry 源有內容可加（見 INGEST_GAP；其餘 dup/deprecated 建議唔做）。
3. monitor：phys_sss routed-UI 限制（要 surface 須另開 dedicated 理科 route）/ g38·music_p1_s6_2024 stale-ranking / freshness 週跑 / 57014 cold-start / FAIL-A record-only / Suppl_guide held / stat_fact 2024-25 stale。

⚠️ Cautions：chunks 係 moving display number（每次補入庫同步 6 處〔3 層 _meta.stats + app.html + K1_API_SPEC + README〕）；入庫 per-source（文字層 fetch_extract、掃描/CID ocr_extract、再 ingest_one_source；勿 full wiki_index upload）；新源必加 SOURCE_SETS allowlist（S135）；大 OCR job pace org TPM。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra（match_count/expansion）/ 勿再 ingest 結構天花板源。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 13,473 / facts 455 三層 / guidelines 152 / knowledge.json stats 13,473·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣（gifted/g17 待 link、或其他方向），未明示前勿郁上述禁區。
```
