# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-15 Session 169 — 文件標註保留格式+改動摘要 / onboarding / 使用手冊（①②③ shipped；④ EDB 全入庫 deferred 待 QC）

- **ID:** Claude_20260615_S169
- **Trigger:** Leonard「開工」→ 起手探針（app.html v3.1.0 + Render /health + Supabase 15,127；SMC 抽驗發現 corpus IMC-heavy 令 SMC 對通用 query recall 被淹＝既有 monitor，非 blocker）→ AskUserQuestion 選「1-4」＝ ①②③④ 全做 batch。①②③ 已 ship+push+headless 驗；④（EDB 全入庫，涉 live Supabase）啟動唯讀 freshness crawl 後 Leonard 轉交 QC agent → ④ deferred、crawl 已 `pkill` 停。
- **① 文件標註乾淨成品版「保留格式」+「改動摘要」（commit `2150f59`，純前端 app.html）：**
  - 問題：S167 `buildCleanDocx` 由抽取文字 `\n+` split 重砌 → 原 Word 標題/編號/表格 flatten（Leonard「改後格式全變」）。
  - 修：新 `buildCleanOriginalDocx(arrayBuffer,findings,meta)` — Word 輸入用 JSZip 操作原 `word/document.xml`，原段落 100% 不動（保留標題/編號/表格格式），配對段後插入普通「（建議補充）」段落（**無 `w:highlight`、無 `w:ins`**），全 finding 說明入附錄（插最後 `<w:sectPr>` 前）+ 頂部 intro note。抽共用 `partitionCleanFindings(paraNorms,findings)`（buildCleanDocx 亦重用）。`handleDownloadClean` 按 `isDocx && fileBuffer` 路由（PDF/貼文字維持 from-text `buildCleanDocx`）。
  - 新 `buildChangeSummaryDocx(docText,findings,meta)` + 「📋 下載改動摘要」掣：列「融入正文建議（連原文段落）」+「附錄補充」+ 計數。
  - QC：Node 抽 app.html 真源 function（同版本 docx 8.5.0/jszip 3.10.1）跑 builder 單元測試 **32/0 PASS**（驗保留 pStyle/標題/正文、零螢光、零 w:ins、建議融入 body、附錄 before sectPr、單一 body、來源頁碼、edge：空 findings/guideline-only）。
- **② Onboarding 首次使用導引（commit `12f33fb`，app.html）：** 新 `Onboarding` component + `TOUR_STEPS`（6 步：歡迎+5 功能+完成，每步 CTA 跳該 tab）；首訪 `localStorage`（`k1_tour_done_v1`）自動彈、dismiss 後不再彈；header 加「🎓 使用教學」`openTour` 重溫；overlay zIndex 2000、Esc/backdrop 關閉。QC：headless `--dump-dom` 驗首訪自動彈（welcome+步驟 1/6+CTA「去政策搜尋」）+ header 掣 + babel boot 正常（tabs render）。
- **③ 使用手冊（commit `12f33fb`，app.html）：** `PlatformIntroPanel` 加 in-app 手冊（5 功能 `<details>` 步驟 + 常見問題 FAQ）；tour 完成步驟 CTA 指向手冊。**順手 doc-drift 修正**：PlatformIntroPanel「文件標註」channel 描述由 stale「就地螢光標示+追蹤修訂（一鍵套用）」改「乾淨成品版（建議融入正文、無螢光、Word 保留格式）」對齊 S167/S169 行為。QC：`app.html#about` dump 驗手冊全段+FAQ+私隱 render + regression 確認 stale「於原檔就地螢光標示」消失。
- **④ EDB 網頁更新→全入庫（DEFERRED — 待 QC pass）：** 啟動 `dev/source/check_freshness.py --dry-run`（唯讀網絡爬取）後 Leonard 轉 QC → 已 `pkill` 停、未寫 `--changes-out`、**零 Supabase 接觸**。待 QC pass 後：逐源 pre-flight（U+FFFD=0、page-resolvable）→ `dev/ingest_one_source.py` 逐源 live INSERT + display sync 7 點。⚠️ live INSERT 需逐源 INSPECT before/after + Leonard 明確授權（auto-mode classifier 擋無授權寫入），勿盲批。
- **QC 工具學習：** macOS **無 `timeout` 指令**（先前多次「空 dump」全因 `timeout: command not found` 令 chrome 根本冇跑）；headless Chrome `--dump-dom` + `--virtual-time-budget` exit 偶爾唔乾淨 → 拆「chrome 寫檔」與「python parse」兩步（dump 檔仍完整）。純前端 builder 單元測試改用 Node 抽真源 function（同 CDN 版本 lib）比 headless 更 deterministic。
- **QC 覆核（Codex_20260615_QC_S169，①②③ only；④ deferred 不覆核）：** verdict **PASS-with-flags（no blocker）**。覆核範圍限 `2150f59` + `12f33fb`，確認兩 commit 均只改 `app.html`；worktree 起手 clean。① 以臨時 Word（標題/pStyle、編號段落、表格內段落、多段文字）跑 app.html 真 `buildCleanOriginalDocx`/`buildChangeSummaryDocx`：保留 pStyle/numbering/table、表格內 span 命中、建議普通文字插入、附錄在 `<w:sectPr>` 前、單一 `<w:body>`、零 `w:highlight`、零 `w:ins`；macOS `textutil` 可讀輸出 docx 並見建議/附錄/摘要。② headless Google Chrome + Playwright fresh profiles 驗首訪 tour 自動彈、localStorage `k1_tour_done_v1` gate、reload 不再自動彈、header「使用教學」重開、Esc/略過/完成/×/backdrop 均關閉並寫 gate、5 個 CTA 跳 `#qa/#annotate/#templates/#guidelines/#about`。③ about tab 使用手冊/FAQ render，展開「文件標註」details 後見乾淨成品版、無螢光、保留原格式、私隱文案；visible DOM 無舊「於原檔就地螢光標示」/「追蹤修訂」字眼。Non-blocking flags：未用 Microsoft Word/真校稿檔做人工視覺驗；舊 annotated/list builders 仍含舊文案/螢光/追蹤修訂字串但屬 dead-code cleanup follow-up，現行 UI/手冊不暴露。
- **Boundary：** 純前端 `app.html`。backend / Supabase 15,127 / 凍結合約（knowledge `_meta` 2.3.0 · facts 455 · guidelines 152）/ desktop 其他功能 / `mobile.js` 零接觸。mobile onboarding 未做（desktop 為主 surface，列 follow-up）。throwaway QC harness `dev/_s169_qc.html` 已刪。
- **⑤ dead-code cleanup（QC pass 後，Leonard「今個 pass 一齊清」，commit `967dd7d`，app.html −464 行 4434→3969）：** 移除 S167/S169 後失效嘅舊 builders — `buildAnnotatedOriginalDocx`/`buildAnnotatedPdf`/`buildEditableDocx`/`buildAnnotateListDocx` + `findingNoteParas` + `handleDownloadOriginal/Editable/List` handlers + 孤立 const `ANNOTATE_PLATFORM_NAME`（7 處引用全喺死 function 內）。Python 按範圍刪（defensive assertion 防錯位，沿用 S151 anchored-splice 先例）。保留共用 `partitionCleanFindings`/`annNorm`/`annParaMatches`/`paraPlainText`/`xmlEsc`/`ANNOTATE_SCHOOL_LABELS` + 現行 `buildCleanDocx`/`buildCleanOriginalDocx`/`buildChangeSummaryDocx`/`handleDownloadClean`/`handleDownloadChanges`/`downloadBlob`/`annotateMeta`。**resolve QC non-blocking flag 2**（舊 builders 殘留 w:highlight/w:ins）：刪後全檔 `w:highlight`=0、`w:ins` 僅 1 處（buildCleanOriginalDocx 註解寫「NO w:ins」）。QC：刪後 Node builder 單元測試 **32/0 PASS**（kept builders 完好可 extract+運作）+ headless Chrome `--dump-dom`（fresh）驗 app boot（tabs render）+ AnnotatePanel（選擇檔案）+ onboarding 完好；removed handlers 零 dangling ref（grep count 0 + boot 成功）。版本不 bump（等 ④）。
- **版本：** 暫**未 bump** PLATFORM_VERSION（仍 `3.1.0`）；①②③④⑤ 一齊出 = v3.2.0（Leonard 決定「等埋 ④ 一齊先 bump」），④ 完成後再 bump app.html PLATFORM_VERSION + README + CHANGELOG（凍結 knowledge.json 不動）。
- **Doc Sync:** Product behavior change → SESSION_HANDOFF/LOG（本）✓；Doc-drift truth-pass（channel desc）→ app.html 已修 + CODEBASE_CONTEXT AI log ✓；New user-facing feature README 功能表 / version / CHANGELOG → **deferred 到 release（post-QC + 版本決定）**。
- **commits（已 push origin/main）:** `ff9bf37`(S168 收尾) → `2150f59`(① app.html) → `12f33fb`(②③ app.html) → `ffc8b97`(治理 PERSIST) → `20fd2a7`(QC 記錄) → `967dd7d`(⑤ dead-code cleanup app.html −464)。
- **Log maintenance (§4a):** SESSION_LOG <400 行，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.1.0。
Product state: HEAD == origin/main（已 push 967dd7d）。Supabase 15,127；Render backend live；Pages live。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.1.0 + Render /health + HEAD==origin/main + Supabase 15,127。

S169（2026-06-15）已 ship + push（QC = PASS-with-flags、no blocker）：
- ① 文件標註乾淨成品版「保留格式」+「改動摘要」（commit 2150f59，app.html）：Word 輸入用 JSZip 改原 docx XML 保留標題/編號/格式、建議融入正文（無螢光/無追蹤修訂）；新增「改動摘要」下載。Node builder 單元測試 32/0 PASS。
- ② onboarding 首次使用導引（commit 12f33fb，app.html）：首訪自動彈 6 步導覽 + header「🎓 使用教學」重溫（localStorage gate）。
- ③ 使用手冊（commit 12f33fb，app.html）：平台介紹 tab in-app 手冊 + FAQ；順手修正 stale 文件標註 channel 描述對齊現行行為。
- ⑤ dead-code cleanup（commit 967dd7d，app.html −464）：移除 S167/S169 後失效舊 builders（buildAnnotatedOriginalDocx/Pdf/buildEditableDocx/buildAnnotateListDocx + handlers + findingNoteParas + ANNOTATE_PLATFORM_NAME），resolve QC flag 2；Node 32/0 + headless boot 驗。

NEXT（優先序）：
① ④ EDB 網頁更新→全入庫（deferred；可起）：跑 dev/source/check_freshness.py --dry-run 及 dev/source/discover_sources.py --check（唯讀）→ 逐源 pre-flight（U+FFFD=0、page-resolvable）→ dev/ingest_one_source.py 逐源 live INSERT + display sync 7 點。⚠️ live INSERT 需逐源 INSPECT before/after + Leonard 明確授權，勿盲批。
② ④ 完成後一齊 bump v3.2.0（Leonard 決定「等埋 ④ 一齊」）：改 app.html PLATFORM_VERSION + README badge/footer + CHANGELOG（勿 bump 凍結 knowledge.json _meta 2.3.0）。
③ Leonard 真機/真檔收貨 ①②③（封版前，QC non-blocking flag）：上載真 Word 驗保留格式 + 表格內段落命中。
④ Render free-tier cold-start；⑤ mobile onboarding（desktop 已有、mobile.js shell 未做）；⑥ monitor：SMC 對通用「SMC/治理」query recall 被 IMC-heavy corpus 淹（資料在庫可檢索，需更貼題 query 或加 SMC 專屬源）。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout 指令）；docx 8.5.0 UMD（window.docx）/ JSZip 3.10.1 / pdf.js 3.11.174 / mammoth 1.6.0；改 backend 前確認 Render deploy + routing 跑 detectQueryCategory 純函數 + Render live 探針；勿改 canonical chunker；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.1.0 + Supabase 15,127 + Render /health + HEAD==origin/main）後，按 Leonard 指示跟進 QC 結果 / 起 ④ / 做版本決定。
```

---

## 2026-06-15 Session 168 — SMC（學校管理委員會）內容入庫 +18 chunks + 平台 v3.1.0

- **ID:** Claude_20260615_S168
- **Trigger:** Leonard 提供 2 個 SMC 官方源補 S166 揭發嘅 SMC 內容 gap（corpus 一直 IMC-heavy）：① PDF 學校管理委員會章程樣本 ② HTML 關於 SMC 頁。並指示版本/README/手冊/開場動畫/全入庫/出架構圖 prompt/收工。
- **SMC 入庫（commit `a82210e`，Leonard「授權全做全入庫」明確授權後執行；首次嘗試被 auto-mode classifier 擋＝缺明確授權，正確 guardrail）：**
  - pre-flight：PDF 14pp/8,749字/**U+FFFD=0**/page-resolvable（pymupdf+pypdf 驗）；HTML 264KB 但可見文字多係全站導航、SMC 獨有內容稀薄 → **只登記 url_landing watch-list、body 不入庫**（避免導航雜訊污染）。
  - pipeline：registry 登記 `smc_constitution_sample` → `fetch_new_sources` 格式 extract（pypdf per-page，14 page markers）→ `ingest_one_source.py --dry-run`=**18 chunks**（396/587/614，全 page-resolvable）→ **INSPECT 總數 15,109 baseline 確認 + source=0** → **live INSERT 18/18**（before=0/after=18）→ INSPECT 總數 **15,127**（+18）✓。
  - routing：`SOURCE_SETS.school_governance` +`smc_constitution_sample`（接 S166 `\b(IMC|SMC)\b` route）。
  - display sync 7 點 15,109→15,127（knowledge.json/role_facts/dev role_facts **3 層 byte-identical md5 06bf2a3a8a** + app.html + index.html + K1_API_SPEC + README；**_meta.version 凍結 2.3.0、facts 455/guidelines 152 不變**）。
- **平台 v3.1.0（commit `a82210e`）：** app.html `PLATFORM_VERSION` 3.0.0→3.1.0 + README badge/footer + 文件標註 row 改「乾淨成品版」+ CHANGELOG v3.1.0 section（彙整 S164-168：手機強化/檢索修復/乾淨成品版/SMC 內容）。凍結 knowledge.json 不 bump。
- **QC（全 PASS）:** backend tsc check+build exit 0；SMC routing 純函數 3 case PASS；Supabase INSPECT before/after（15,109→15,127、source 18）；3 JSON 層 md5 identical + version 凍結驗。**Live（Render+Pages deploy 後）:** `SMC 學校管理委員會 章程` 命中 `smc_constitution_sample`；app.html v3.1.0 + 15,127。
- **Boundary:** Channel B +1 源（公開 EDB 官方）。Channel A 455 / guidelines 152 / _meta.version 凍結合約零接觸。可逆（merge-duplicates、可按 source_id 刪）。
- **commit（已 push origin/main）:** `a82210e`（registry+vault extract+SOURCE_SETS+display sync 7+版本+CHANGELOG）→ 本治理 commit。
- **⏳ Leonard backlog（本 session 收工，未做，已記 handoff/Open Priorities，多數 substantial 留下 session）:**
  1. **文件標註乾淨成品版 2 項跟進:** (a) 另需一個 Word 顯示「改咗甚麼」（change/diff 摘要）；(b) **格式問題**——乾淨成品版由抽取文字重組 → 原 Word 標題/編號/結構 flatten 咗（Leonard：「改後格式全變」），要改善格式保留（難點：目前 from-text 重砌；考慮 Word 輸入時 JSZip 改原 docx XML 保留格式、PDF 則維持 from-text）。
  2. **開場動畫/onboarding**（似 CPD approval system）— 首次使用導引，使用者知道點用。
  3. **使用手冊**（user manual）。
  4. **EDB 網頁更新 monitor → 全入庫**（Leonard 授權「全入庫」standing）：下 session 跑 freshness/discover（`check_freshness.py`/`discover_sources.py`）→ 逐源 pre-flight（U+FFFD=0/page-resolvable）→ `ingest_one_source.py` 逐源入庫 + display sync。**勿一次過盲入；逐源 INSPECT。**
  5. dead-code cleanup（task_94ebfd14，文件標註舊 builders）。
  6. Render cold-start（升 always-on 或 keep-warm cron）。
- **架構圖 prompt:** 已喺 closeout 回應交畀 Leonard（系統功能 + 技術架構 LLM-wiki/RAG，供佢 gen 圖）。
- **Log maintenance (§4a):** S167 已 archive（517→188）；本 entry 後 SESSION_LOG 仍 <400，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.1.0。
Product state: HEAD == origin/main（已 push a82210e+）。Supabase 15,127；Render backend live；Pages live（v3.1.0）。起手 verify：探針 policychecker.wongfu.net /app.html=200 + PLATFORM_VERSION 3.1.0 + Render /health + HEAD==origin/main + Supabase 15,127 + 抽驗「SMC 學校管理委員會 章程」命中 smc_constitution_sample。

S168（2026-06-15）完成：SMC 內容入庫（smc_constitution_sample 章程樣本 +18 chunks → 15,127；SOURCE_SETS.school_governance；display sync 7 點 byte-identical、_meta 凍結 2.3.0）+ 平台 v3.1.0（PLATFORM_VERSION/README/CHANGELOG）。今日另完成 S164-167（手機範本入口/品牌/可撳搜尋掣、SMC/IMC 英文縮寫 routing 修復、文件標註乾淨成品版）。

NEXT（Leonard backlog，優先序）：
① 文件標註乾淨成品版跟進：(a) 加一個 Word 顯示「改咗甚麼」(change/diff 摘要)；(b) 修格式——目前由抽取文字重組令原 Word 標題/編號/結構 flatten（Leonard：「改後格式全變」）。建議：Word 輸入改用 JSZip 操作原 docx XML（保留格式，建議融入做正常 run/highlight，免接受修訂），PDF/貼文字維持 from-text 乾淨版。參考已 dead 嘅 buildAnnotatedOriginalDocx（JSZip 原檔操作）+ buildCleanDocx（from-text）。
② 開場動畫/onboarding（似 CPD approval system）：首次使用導引使用者知道點用。
③ 使用手冊（user manual）。
④ EDB 網頁更新 monitor → 全入庫（Leonard 已授權「全入庫」standing）：跑 check_freshness.py / discover_sources.py → 逐源 pre-flight（U+FFFD=0、page-resolvable）→ ingest_one_source.py 逐源 + display sync 7 點。逐源 INSPECT，勿盲批。
⑤ dead-code cleanup（task_94ebfd14：app.html 文件標註舊 builders/handlers）。
⑥ Render cold-start（升 always-on 付費 或 keep-warm cron）。
⑦ monitor：SMC 內容深度（已 +章程樣本，可再加 SMC 服務合約/其他官方源）；buildCleanDocx 段落配對率；P3 gate 多範疇；KG QC DRAFT。

⚠️ 紀律：**live Supabase INSERT 需 Leonard 明確授權**（auto-mode classifier 會擋無授權寫入）+ 入庫前 INSPECT before/after + 用 ingest_one_source.py（canonical chunker、merge-duplicates 可重跑）+ display sync 7 點（3 JSON 層 byte-identical、_meta.version 凍結）；改 backend 前確認 Render deploy + routing 跑 detectQueryCategory 純函數 + Render live 探針；app.html/mobile.js 用 headless Chrome（fresh，bypass 快取，Preview 工具 cache subresource）；docx 由 docx 8.5.0 UMD 砌；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；repo 勿 set private。
Post-startup first action: 探針 policychecker.wongfu.net v3.1.0 + Render /health + Supabase 15,127 + SMC 抽驗，然後問 Leonard 起邊個 backlog（建議 ① 乾淨成品版格式 或 ② 開場動畫）。
```

---

## 2026-06-15 Session 167 — 文件標註簡化為單一「乾淨成品版」下載（解決接受修訂後螢光殘留/原稿亂）

- **ID:** Claude_20260615_S167
- **Trigger:** Leonard 回饋（S166 ③ 未完）：Word 標註版即使「全部接受」後黃/綠螢光仍在（螢光係永久格式非修訂）+ 逐段 💡/⚠ 註解令原稿亂、唔似成品。AskUserQuestion 釘實：**乾淨成品版（推薦）+ 取代簡化做一個**。
- **CHANGE（commit `ee2c89f`，純前端 app.html）:**
  - **新 `buildCleanDocx(docText, findings, meta)`（docx-lib，重用 annNorm/annParaMatches）：** 原文正文保持**乾淨**（無螢光、無 inline 註解）；只有「有 suggestion + 定位到 span」嘅 checklist finding 將建議條文**融入正文做普通文字**、首行帶極簡「（建議補充）」標示（誠實但不喧賓奪主，非螢光非追蹤修訂）；guideline 參考 + 未定位 + 無 suggestion → 只入附錄。文末「**附錄：AI 建議說明與出處**」按範疇列出全部 finding 嘅 tag/說明/建議條文/EDB 出處（可點 link）。Word/PDF/貼文字皆出（由抽取文字砌）。
  - **下載列簡化為單一按鈕**「⬇️ 下載 Word（乾淨成品版）」+ 新 `handleDownloadClean`；移除「三種下載」指引、改為單一乾淨版說明；更新 panel 介紹/檔案確認/空狀態/貼文字 4 處舊文案。
  - **舊 builder/handler 變 dead code（保留不刪）：** buildAnnotatedOriginalDocx/buildAnnotatedPdf/buildEditableDocx/buildAnnotateListDocx + handleDownloadOriginal/Editable/List + findingNoteParas。**已 spawn cleanup task `task_94ebfd14`**（precedent：S161→S162 同樣 dead-code 留待下 session 清）。
- **QC（全 PASS）:** preview（localhost cache-bust）app.html 0 console error、`buildCleanDocx` global、docx/JSZip/PDFLib 載入。**`buildCleanDocx` 深驗：** 合成 report → docx well-formed、**無 `w:highlight`**、**無 `<w:ins>`**、正文有「（建議補充）」融入建議、附錄標題+出處在、原文乾淨；merged=1/total=3（長 span 配對）。**真 UI e2e（stub analyze）：** 貼文字→開始標註→**下載列只剩單一「乾淨成品版」按鈕**（舊三按鈕+指引全清，hasOld可編輯OrList=false）→點擊觸發 docx 下載（正確 MIME）+ note 顯示。
- **Boundary:** 純前端 app.html 文件標註面板。backend/Supabase 15,109/凍結合約/desktop 其他功能零接觸。dead code 留待 cleanup task。
- **commit（已 push origin/main）:** `ee2c89f`（app.html）→ 本治理 commit。
- **Log maintenance (§4a):** SESSION_LOG 加 1 entry；總行數接近上限需留意（下次 closeout 評估 §4a archive，目前 <400 估算）；本次 no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Render backend live；Pages live（v3.0.0）。起手 verify：探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109 + 抽驗 SMC/IMC 搜尋命中 IMC 治理文件。

S167（2026-06-15）完成（純前端 app.html，commit ee2c89f，Pages live）：
- 文件標註下載簡化為單一「乾淨成品版」(buildCleanDocx)：原文正文乾淨（無螢光、無 inline 註解）；AI 建議融入正文做普通文字、帶「（建議補充）」極簡標示；說明+EDB 出處集中文末附錄。Word/PDF/貼文字皆出。解決「接受修訂後螢光殘留、原稿亂」。
- 舊 builder/handler（buildAnnotatedOriginalDocx/Pdf/buildEditableDocx/buildAnnotateListDocx + handlers + findingNoteParas）變 dead code，已 spawn cleanup task task_94ebfd14。
- 同日較早：S166（手機品牌統一+可撳搜尋掣+SMC/IMC retrieval）、S165（可編輯版，已被 S167 取代）、S164（手機範本下載入口）。

NEXT（多數待 Leonard 真機/真檔收貨）：
① Leonard 真檔收貨 S167「乾淨成品版」：上載真 Word/PDF → 下載 → 確認原稿乾淨、建議「（建議補充）」融入得自然、附錄說明+出處清晰、可直接編輯採用。
② dead-code cleanup（task_94ebfd14）：清 app.html 文件標註舊 builders/handlers（grep 確認零引用後 bottom-up 刪 + headless 驗）。
③ Render 免費 tier cold-start（閒置 15min 瞓→第一搜尋 ~50s）：考慮升 always-on 或 keep-warm cron。
④ monitor：SMC 專屬內容深度（corpus IMC-heavy，SMC vs IMC synthesis 標籤偶混淆）；buildCleanDocx 段落配對率（PDF 抽取文字 vs span）；P3 gate 多範疇覆蓋；KG QC DRAFT 最終核；#3 學校版 102 docx。

Key files（S167）：app.html（buildCleanDocx + handleDownloadClean + 單一下載按鈕 + panel 文案）。前 session：mobile.js/mobile.css（S164/166）、searchChannelB.ts（S166 SMC/IMC route）。
⚠️ 紀律：app.html/mobile.js 改動用 headless Chrome（fresh，bypass 快取，Preview 工具會 cache subresource）；docx 由 docx 8.5.0 UMD（window.docx）砌、PDF 抽取 pdf.js 3.11.174、Word mammoth 1.6.0；起 backend 改動前確認 Render deploy + 改 routing 跑 detectQueryCategory 純函數 + Render live 探針；改 docx/checklist re-run gen_*；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + SMC/IMC 抽驗，然後問 Leonard：S167 乾淨成品版 真檔收貨 / 起邊個 NEXT（建議 ② cleanup 或 ③ cold-start）。
```

---

## 2026-06-15 Session 166 — 手機品牌統一 + 可撳搜尋掣 + SMC/IMC 英文縮寫 retrieval 修復

- **ID:** Claude_20260615_S166
- **Trigger:** Leonard 真機/真檔回饋多輪。① 手機介面仍顯示「K1 知識平台」（應對齊公開名）；② 手機未能搜尋（上輪 enter fix 後仍唔穩）；③ Word 標註版接受修訂後綠色仍在、原稿不清晰（**未解決，待設計決定**）。期間實測「SMC 與 IMC 分別」揭發 retrieval 引錯源。
- **① 品牌統一（mobile.js，commit `5c55320`）:** hero eyebrow + role-picker eyebrow「K1 知識平台」→「香港學校政策搜尋平台」（對齊 desktop 公開名）。
- **② 手機可撳搜尋掣（mobile.js + mobile.css，`5c55320`）:** 根因 = 搜尋觸發只靠鍵盤隱式提交（放大鏡係裝飾），部分手機鍵盤/IME 唔觸發 → 搜唔到。修：表單加 `type=submit`「搜尋」掣（`.m-search-btn` 綠 pill，44px touch）→ 唔再靠 enter；保留上輪 `enterkeyhint`+Enter keydown handler。Leonard 手機截圖證已出到結果。
- **✚ SMC/IMC retrieval 修復（backend `searchChannelB.ts` + `semanticRegression.ts`，commit `7d70dda`）:**
  - **根因（audit-confirmed）:** 英文縮寫 SMC/IMC 唔 match `school_governance` 嘅中文關鍵詞 → 無 route → generic semantic search（英文縮寫 vs 中文「法團校董會」embedding 相似度低）→ 引錯源（旅遊/課程/crisis 等無關文件，分數~0.31）+ 整理答案變 LLM 泛知識（無根據，違反「有根有據」）。中文 query（法團校董會/校董會）一向正確（0.67-0.75）。
  - **retrieval 審計 Workflow（14 query 並行打 live backend，獨立判斷來源相關性）:** 11 OK / 3 gap。確認系統性問題 = 收窄到治理 route（cpd/steam/sen/gifted 本身已有英文 token = OK；NCS/OLE/KLA/BYOD 因 query 帶中文詞而 OK）。gap：SMC/IMC（routing，修）+ SBA（內容稀疏，follow-up）。
  - **修:** `TOPIC_KEYWORDS.school_governance` +`\b(?:IMC|SMC)\b`+incorporated/school management committee（`/i`、word-boundary 防誤中如 dynamic）；新增 `QUERY_EXPANSIONS.school_governance`（bridge 英→中治理詞彙，SOURCE_SET 限定 imc_*/g02/coa_imc 內檢索對位）。
  - **QC:** tsc check+build exit 0；`detectQueryCategory` 11 case 全 PASS（SMC/IMC 變體→school_governance、採購→finance 不被偷、dynamic→curriculum 不誤中、controls 不變）；semanticRegression +6 治理 routing cases。**Live e2e（Render deploy 後）:** `SMC 與 IMC 分別`→ imc_briefing_qa/establishment/election/governance_supplements（0.54-0.67，取代課程垃圾），synthesis grounded（真實校董會組成）；`IMC 成員組成`→ IMC docs+g02 grounded。
  - **⚠️ monitor:** corpus 以 IMC（法團校董會）為主、SMC（學校管理委員會 舊制）專屬文件較少 → synthesis SMC 標籤偶混淆（内容深度問題，非 routing）。
- **QC 綜合:** mobile headless fresh render（搜尋掣+eyebrow 改名+enterkeyhint+4 tabs）；backend tsc/build/routing 全 PASS + Render live 驗。
- **Boundary:** 前端 mobile shell（`5c55320`）+ backend routing（`7d70dda`）。Supabase 15,109 / 凍結 JSON / desktop React app.html 全零接觸。
- **commits（已 push origin/main）:** `5c55320`（mobile rename+搜尋掣）→ `7d70dda`（SMC/IMC retrieval + regression）→ 本治理 commit。
- **⏳ 未完（最優先）:** ③ Word 標註輸出「乾淨度」—— 接受修訂後綠螢光仍在 + inline 註解令原稿亂。待 Leonard 揀最終輸出形態（乾淨整合版 / 輕量標示 / 移除 inline 註解）再實作。S165 可編輯版亦用綠螢光，可能同樣需調。
- **Log maintenance (§4a):** SESSION_LOG 加 1 entry，<400 行、oldest <30d，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Render backend live；Pages live（v3.0.0）。起手 verify：探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109 + 抽驗 SMC/IMC 搜尋仍命中 IMC 治理文件。

S166（2026-06-15）完成：
- 手機品牌統一（K1知識平台→香港學校政策搜尋平台）+ 可撳「搜尋」掣（唔再淨靠 enter；mobile.css .m-search-btn）。commit 5c55320，Pages live。
- SMC/IMC 英文縮寫 retrieval 修復：searchChannelB.ts school_governance route +\\b(IMC|SMC)\\b+英文片語(/i) + QUERY_EXPANSIONS bridge 英→中；+semanticRegression 6 cases。commit 7d70dda，Render live 驗（SMC/IMC→IMC 治理文件 grounded，取代課程垃圾源）。審計 14 query 11 OK。

最優先未完 = ③ Word 標註輸出乾淨度：
- 問題：Word 標註版（buildAnnotatedOriginalDocx，追蹤修訂）即使「全部接受」後，黃/綠螢光仍在（螢光係永久格式非修訂）+ inline 💡/⚠ 註解段落令原稿亂、唔似成品。S165 可編輯版（buildEditableDocx，綠螢光直寫）同樣有螢光殘留問題。
- 待 Leonard 決定最終輸出形態（建議選項）：A 乾淨整合版（建議融入正文、無螢光、出處集中文末，似完成政策文件）／B 保留螢光但可一鍵移除／C 移除 inline 註解只留正文+附錄。揀好就喺 app.html 加/改對應 builder（参 buildEditableDocx 結構），headless e2e（docx well-formed+內容）+ desktop 真檔驗。

NEXT 其他（多數待 Leonard）：
① ③ Word 輸出乾淨版（見上，最優先）。
② Render 免費 tier cold-start（閒置 15min 瞓→第一搜尋 ~50s；手機搜尋已有 cold-start 進度提示+60s timeout）：考慮升 always-on 或 keep-warm cron。
③ 真檔驗：文件標註可編輯版（S165）真 Word/PDF 開啟對位；Phase 2 PDF highlight 真檔多 viewer。
④ monitor：SMC 專屬內容深度（corpus IMC-heavy）；P3 gate 多範疇覆蓋；KG QC DRAFT 最終核；#3 學校版 102 docx。

Key files（S166）：mobile.js（eyebrow rename + 搜尋掣 type=submit）/ mobile.css（.m-search-btn）/ backend/src/api/searchChannelB.ts（school_governance TOPIC_KEYWORDS +英文縮寫 + QUERY_EXPANSIONS）/ backend/scripts/semanticRegression.ts（+6 routing cases）。
⚠️ 紀律：起 backend 改動前確認 Render deploy；改 searchChannelB routing 後跑 detectQueryCategory 純函數驗 + Render deploy 後 live 探針；live INSERT 前 INSPECT；改 docx/checklist re-run gen_*；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；mobile.js/app.html 改動用 headless Chrome（fresh，bypass 快取，Preview 工具會 cache subresource）；retrieval routing 用 audit workflow（多 query 打 live）驗系統性；repo 勿 set private。
Post-startup first action: 探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + SMC/IMC 搜尋抽驗，然後問 Leonard ③ Word 輸出乾淨版想揀邊個方案（A/B/C）/ 起邊個 NEXT。
```

---

## 2026-06-15 Session 165 — 文件標註可編輯 Word 版（建議螢光直寫、免接受修訂）+ 手機搜尋 enter 修復

- **ID:** Claude_20260615_S165
- **Trigger:** 同一 conversation 接 S164。Leonard 真檔試用「文件標註」+ 截圖回饋 3 項（+確認 S164 mobile 範本下載=OK 收貨）：① Word 標註版用追蹤修訂，校長/老師唔識用「接受/拒絕」；② PDF 輸入→PDF 輸出但不能 edit，要建議方法；③ 手機搜尋輸入後撳 enter 唔即時搜尋。經 AskUserQuestion 釘實：①+② 用「可編輯 Word 版 + 改善指引」；建議條文「螢光標示、可直接編輯」。
- **PLAN（HIGH-risk，已確認）:** 純前端（app.html 文件標註面板 + mobile.js）；不碰 backend / Supabase / 凍結 JSON / 不改現有 builder（純加新嘢）。
- **READ:** 摸清 `buildAnnotatedOriginalDocx`（Word 原檔就地標+w:ins 追蹤修訂）/`buildAnnotatedPdf`（PDF 螢光）/`buildAnnotateListDocx`（docx-lib 砌清單）/`findingNoteParas`/`annNorm`+`annParaMatches`（module-scope 可重用）/`AnnotatePanel` state（`docText` 對 Word+PDF+貼文字皆有）。確認 `ANNOTATE_BACKEND_URL` localhost→:8787（本地 e2e 要 stub）。
- **CHANGE（commit `afec532`）:**
  - **app.html — 新 `buildEditableDocx(docText, findings, meta)`：** 用 `docx` 8.5.0 UMD 由抽取文字砌可編輯 Word；split 段落、重用 `annNorm`/`annParaMatches` 配對 → 配對段 `highlight:'yellow'`、AI 建議條文 `highlight:'green'` **直接寫入文中（正常 run，非 `<w:ins>` 追蹤修訂 → 免接受修訂）**、💡/⚠ note、未定位入「建議補充」附錄、頂部 legend（綠螢光=建議、可編輯、毋須接受修訂）。**Word/PDF/貼文字三種輸入皆出**（PDF 由 extractPdf 已抽文字重組 → 解決「PDF 不可編輯」）。
  - **新 `handleDownloadEditable`** + 下載列重整：可編輯 Word 版（推薦，primary，enabled when report）｜標註版原檔（secondary，Word·保留格式/PDF·螢光，需 fileBuffer）｜建議清單。加「三種下載」指引塊（含教學「Word『校閱』分頁按『接受』套用／『拒絕』清走」）解決問題①。更新 3 處舊提示（貼文字/PDF 而家都出可編輯版）。
  - **不改** `buildAnnotatedOriginalDocx`/`buildAnnotatedPdf`/`buildAnnotateListDocx`（零回歸）。
  - **mobile.js — 問題③：** 搜尋框 `+enterkeyhint="search"` + 明確 Enter `keydown` handler（`submitSearch()`；部分手機鍵盤/IME 對無提交鈕表單唔觸發隱式提交）。
- **QC（全 PASS）:** `node --check mobile.js` ✓。preview（localhost）cache-bust 後 app.html 0 console error、`buildEditableDocx`/`annNorm` global、docx/JSZip/PDFLib 載入。**`buildEditableDocx` 單元＋深驗：** 合成 report → docx blob 8.5KB、PK zip、JSZip 解開 `document.xml` **well-formed**、含 `w:val="yellow"`+`w:val="green"`+建議文字+原文、**無 `<w:ins>`**（證螢光可編輯、非追蹤修訂）、located/unlocated 正確。**真 UI e2e（stub analyze）：** 貼文字→開始標註→下載列 3 按鈕＋「三種下載」＋「校閱接受/拒絕」教學渲染→點「可編輯 Word 版」→ 觸發 1 下載（docx MIME、note「就地標示 1 處…毋須接受修訂；另有 1 項…建議補充」）。**mobile fresh headless：** `enterkeyhint=search` 在、keydown handler 在 served code、4 nav tabs、mobile-active。`git diff` 只 app.html+mobile.js；backend/凍結 JSON 零接觸。
- **Live:** commit `afec532` pushed origin/main；Pages deploy 驗（live app.html 含 `buildEditableDocx`、mobile.js 含 `enterkeyhint`）。
- **Evidence disposition:** kept as recent trace evidence；可編輯版設計 + mobile enter 修復理由入 CHANGELOG/CODEBASE_CONTEXT。
- **⚠️ 待 Leonard 收貨:** 手機真鍵盤撳 Enter（headless 無法模擬實體鍵盤，已驗 enterkeyhint+handler 在）；真 Word/PDF 檔下載可編輯版開啟對位＋螢光顯示（合成 report e2e 全綠，真檔待試）。
- **Boundary:** 純前端文件標註輸出 + 手機搜尋 bugfix。desktop 現有 3 個 builder/backend/Supabase/凍結合約全不受影響。
- **commits（feature 已 push）:** `afec532`（app.html + mobile.js）→ 本治理 commit。
- **Log maintenance (§4a):** SESSION_LOG 加 1 entry，<400 行、oldest <30d，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.0.0。
Product state: HEAD == origin/main（已 push）。Supabase 15,109；Render backend live；Pages live（v3.0.0）；0 outstanding bug。起手 verify：探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109。

S165（2026-06-15）完成（純前端，backend/Supabase/凍結合約零接觸；commit afec532 pushed+Pages live）：
- 文件標註新增「可編輯 Word 版」下載（buildEditableDocx）：原文配對段黃螢光、AI 建議條文綠螢光直接寫入文中（非追蹤修訂、可即改即用、毋須接受修訂）、未定位入「建議補充」附錄；Word/PDF/貼文字三種輸入皆出（解決 PDF 不可編輯）。下載列三按鈕（可編輯版推薦/標註版原檔/建議清單）+「三種下載」指引（含教 Word 校閱按接受/拒絕）。不改現有 buildAnnotatedOriginalDocx/buildAnnotatedPdf。
- 手機搜尋修 enter：mobile.js +enterkeyhint=search + 明確 Enter keydown handler。
- 核實：buildEditableDocx 單元+真 UI e2e（stub）全綠（docx well-formed、yellow+green highlight、無 w:ins、下載觸發）；mobile fresh headless enterkeyhint 在。
- S164（同日早）：mobile 底部導航 +範本下載入口（桌面功能標示+截圖 templates-preview.png），Leonard 已收貨 OK。

NEXT（優先序，多數待 Leonard 收貨）：
① Leonard 真機/真檔收貨 S165：手機撳 Enter 即搜尋；真 Word/PDF 上載 → 下載「可編輯 Word 版」開啟，確認建議綠螢光、可直接改、配對對位合理；標註版原檔（追蹤修訂）指引是否夠清。
② Render 免費 tier cold-start（閒置 15min 瞓→第一搜尋 ~50s）：production UX 痛點，考慮升 always-on 付費或加載入中 UX。
③ 真檔驗：Phase 2 PDF inline highlight 真 PDF 對位+多 viewer CJK；P3 gate 真檔多範疇覆蓋率 monitor（STOPWORD_DF_FRACTION=0.25/COVERED=0.5/PARTIAL=0.42/MAX_ITEMS=400 tunable）。
④ monitor：可編輯版段落配對率（annParaMatches 對 PDF 抽取文字的命中）；P2 KG routing 真查詢；Phase 2.5 多範疇 UX；KG QC DRAFT 最終核；#3 學校版 102 docx；here.now 鏡像去留。

Key files（S165）：app.html（buildEditableDocx + handleDownloadEditable + 下載列三按鈕 + 三種下載指引；不改 buildAnnotatedOriginalDocx/buildAnnotatedPdf/buildAnnotateListDocx）/ mobile.js（搜尋框 enterkeyhint + Enter keydown handler）。
⚠️ 紀律：起 backend 改動前確認 Render deploy；live INSERT 前 INSPECT；改 docx/checklist re-run gen_checklists_bundle.py+gen_templates_manifest.py（kg_operation canonical si/section_name）；勿改 canonical chunker；路徑空格雙引號；commit -m 勿用反引號；本機 shell set -e（grep -c 0 中斷用 python 數）；mobile.js/app.html 改動用 headless Chrome（fresh，bypass 快取）核實，Preview 工具會 cache 舊 subresource（用 ?cb= 或 headless）；docx 由 docx 8.5.0 UMD（window.docx）砌、PDF 抽取由 pdf.js 3.11.174、Word 由 mammoth 1.6.0。改 host/CORS：env.ts BASELINE_CORS_ORIGINS exact origin 無尾斜線；repo 勿 set private（會 down free Pages + Render deploy）。
Post-startup first action: 探針 policychecker.wongfu.net /app.html=200+v3.0.0 + Render /health + HEAD==origin/main + Supabase 15,109，然後問 Leonard：S165 真機/真檔收貨 / 起邊個 NEXT。
```

---

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
