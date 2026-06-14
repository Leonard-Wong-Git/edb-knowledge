# 文件標註功能 — 設計 spec（S160 Leonard 拍板；**Phase 1 已建 S161**）

> **狀態（S161 2026-06-14）：Phase 1 SHIPPED。** 合併 tab 「📝 文件標註」取代 文件分析+文件修訂；新 `backend/src/api/annotateDocument.ts`（重用 analyzeDocument 指引比對 + checklistRevise 清單 gap，零改兩模組）+ `/api/annotate-document` route；`checklistRevise.ts` 加 `detectRelevantDomains`（auto-detect）；`app.html` 加 `AnnotatePanel` + `buildAnnotatedOriginalDocx`（JSZip 就地 highlight + **可見內聯建議段** + fallback 附錄）+ JSZip CDN。**S161 後續（Leonard 真檔試用反饋）**：棄用隱形 Word 批註 comment（要開批註窗格先見）改 `findingNoteParas` 喺每段 highlight 後插「可見內聯註解段」（💡指引／⚠修訂 + 建議，淺底色+縮排）；平台正式名 `香港學校政策搜尋平台`（非內部「EDB K1 知識平台」）。
> **v1 設計取捨**：(1) highlight 用**段落級**（命中段每個 run 加 `w:highlight`）而非逐字 run-split — 寧 over-annotate 唔好錯位（heuristic-failure-direction-decouple）。(2) span↔段落用 normalized（去空白+標點）includes/prefix-probe 容錯匹配；搵唔到 → 附錄（never silent drop）。(3) checklist 低 PARTIAL 門檻會過量標 partial → 每域 partial cap 12（按相似度）、missing cap 25、總 cap 120，確保 missing 唔被淹。(4) **修咗一個 bug**：python-docx 生成嘅 docx 自帶 self-closed `<w:comments/>` stub，原 `.replace('</w:comments>')` no-op → dangling comment refs → Word repair；已處理 self-closed 分支。
> **驗證**：backend typecheck/build + 真 OpenAI e2e（auto-detect/explicit/error）+ 真 docx 端到端（DOMParser well-formed、ref↔comment 對齊、ct/rels/附錄齊）+ browser-verify（tab 合併、render、fallback 清單 docx valid）。Phase 2（PDF inline）/ Phase 2.5（per-segment auto-detect 取代 multi-select）未做。

---

# 原始設計 spec（S160）

> Leonard 反饋拍板（S160）：合併「文件分析 + 文件修訂」做**一個「文件標註」功能** —
> 上載文件 → 系統喺**原文**標註（**保留格式** + highlight 要改/涉及指引處 + 建議）→ 下載。
> docx 行先、PDF 第二階段；多範疇（#2）併入。取代現時兩個 tab。

## 1. 願景（解決 Leonard #1 + #2 + #3）

| 現狀（2 tab，用戶分唔清 = #1） | 新（1 tab「📝 文件標註」） |
|---|---|
| 📄 文件分析：逐段比對 EDB 指引 → 另砌報告 | 上載文件 + 揀校類 + 範疇（多選/自動偵測 = #2）|
| 📝 文件修訂：按 checklist 標 + 另砌報告 | → 系統合併（指引比對 + checklist gap）|
| 輸出 = 重新砌 docx（#3b 唔啱） | → **輸出 = 你份原文 + 格式保留 + highlight + 批註建議**（#3b）→ 下載 |

## 2. 核心難點 + 解法：保留原 docx 格式做標註

「保留原文格式 + highlight」= **改你上載嗰份原檔**，唔係重新砌。client 有原檔 ArrayBuffer。

**docx 機制（v1）— JSZip 操作原 docx XML：**
1. `JSZip.loadAsync(原檔 ArrayBuffer)` → 攞 `word/document.xml`。
2. 對每個 finding（要標註嘅文字片段 span）：喺 document.xml 嘅 `<w:r><w:t>` runs 搵 span 文字（注意：一個 span 可能跨多個 run，要 run-merge 或 split）。
3. 喺命中 run 加 `<w:rPr><w:highlight w:val="yellow"/></w:rPr>`（螢光）+ 插入 Word 批註（comment）reference：
   - `word/comments.xml`（新建/補）放批註內容（= note + 標準條文建議 + 指引來源頁）。
   - document.xml 插 `<w:commentRangeStart/end>` + `<w:commentReference>`。
   - `[Content_Types].xml` + `word/_rels/document.xml.rels` 補 comments part 關係。
4. JSZip 重新打包 → blob → 下載「<原檔名>_標註版.docx」。

**Fallback（mapping 失敗時）**：span 喺原文搵唔到（抽取文字 vs 原 XML 有差）→ 該 finding 唔 inline highlight，改為喺檔尾「未能定位嘅標註」appendix 列出（heuristic-failure-direction-decouple：寧 append 都唔好靜默掉）。

**PDF（phase 2，難）**：pdf-lib 加 highlight annotation 要逐字座標（pdf.js text positions）。v1 PDF 只出「另份建議清單」(現 buildAnnotatedDocx 風格)。

> ⚠️ 技術風險：抽取文字（mammoth extractRawText，純文字）↔ 原 docx XML runs 嘅 mapping 係最 fragile 嘅一環。建議實作時用 playbook `synthetic-fixture-vs-real-file` + `heuristic-failure-direction-decouple`：真檔測試、寧 over-annotate/append 都唔好錯位 highlight。

## 3. Backend（合併，需 Render deploy）

新 / 合併端點 `POST /api/annotate-document`：input `{text, school_type?, domains?: string[]}`（domains 空 = 自動偵測涉及範疇）。
- 跑 (a) 指引比對（現 analyzeDocument segment→searchChannelB）+ (b) 每個選定 domain 嘅 checklist gap（現 checklistRevise）。
- 回 findings[]：`{span: 原文片段, kind: "guideline"|"checklist-gap", status, note, suggestion(標準條文), source:{title,url,page}}`，span 要儘量可喺原文逐字 match（回原文 substring 而非改寫）。
- 多範疇：loop selected domains（或 auto-detect via detectQueryCategory per segment）→ merge dedupe。

> 重用現有 `analyzeDocument.ts` + `checklistRevise.ts` 邏輯（唔好重寫檢索 infra）。

## 4. 前端（合併 tab）

- 新 `AnnotatePanel`（合 `AnalyzePanel`+`ReviewPanel`）：上載/貼 + 校類 single-select + **範疇 multi-select（或「自動」）** + 「開始標註」→ POST `/api/annotate-document` → 螢幕報告（findings 分組）+ 「⬇ 下載標註版原文 (Word)」`buildAnnotatedOriginalDocx(原檔 ArrayBuffer, findings)`。
- `VALID_VIEWS`：`'analyze'`+`'review'` → 合成 `'annotate'`（保留舊 hash redirect 一季）。tab：📝 文件標註。
- 抽取文字欄已收（S160 #3a）；原檔 ArrayBuffer 要留住（現只留 docText；新增 `fileBuffer` state 供 client 砌標註版）。

## 5. 分階段建議

- **Phase 1（docx 行先）**：合併 tab + `/api/annotate-document` + JSZip docx highlight+comment + fallback appendix。PDF 出建議清單。
- **Phase 2**：PDF inline highlight（pdf-lib + pdf.js 座標）。
- **Phase 2.5**：自動偵測涉及範疇（per-segment detectQueryCategory）取代手動 multi-select。

## 6. 依賴 / 風險

- **需 Render backend deploy**（新端點）— ⚠️ S160 尾 Render deploy stuck（kg_admin route 都未 land）；Leonard 會 manual deploy 整返掂先郁 backend。
- JSZip 要加 CDN（client docx XML 操作）；mammoth 留住做螢幕 preview 文字。
- 真 docx 測試樣本（多格式：表格/標題/清單）= 必須（synthetic fixture 唔夠）。
- 取代兩個現有 live tab = 用戶可見改動，要 browser-verify + Leonard sign-off 先 deploy。

## 7. 驗收

typecheck/build + 真 docx 端到端（上載 → 標註版下載 → Word 開到、格式無爛、highlight/批註喺正確位、fallback appendix work）+ browser-verify + onrender live e2e + Leonard 試用。
