# Changelog

All notable changes to the 學校管理知識中心 are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [內容修復] — 2026-06-22 — TRG 凍結教席上限 footnote 入庫（修正政策搜尋砌數）

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,363 → 15,364**（＋1 curated footnote chunk）。

### Fixed
- **政策搜尋砌數修復 — 凍結教席上限**（Channel B Supabase，＋1 chunk，`content_type=footnote_curated`，可逆）：查詢「已成立法團校董會學校可凍結的教席上限是百分之幾」時，系統原本檢索唔到真資料（資料庫缺此規則），卻錯誤挪用「法團校董會辦學團體校董人數上限 60%」砌出假答案（張冠李戴 confabulation）。補入真資料：凍結教席（含〔甲〕教師放假暫時凍結、〔乙〕核准編制上的教席空缺、〔丙〕永久凍結常額教席，三類合計）上限為學校**核准教學人員編制的一成（10%）**，源自《為設有法團校董會學校而提供的整合代課教師津貼》附件 III 申請表細字（中英版雙重核實）。本地 self-test：原 query 對新 footnote cosine **0.66**（穩入 LLM 合成窗），英文無關 query 0.31（不誤命中）。

### Changed
- 知識片段顯示數 **15,363 → 15,364**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

---

## [功能 + 資料修復] — 2026-06-22 — 手機首次導覽 · 檢查清單範疇標籤補全

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。知識內容零改動（facts 455 / guidelines 158 / chunks 15,363 不變）。

### Added
- **手機首次導覽 onboarding tour**（`mobile.js` + `mobile.css`）：首次開啟平台嘅手機用戶會見到 4 步導覽頁面（全螢幕 overlay，z-index 210）——「平台簡介 → 政策搜尋 → 指引文件庫 → 準備好了！」——再引導至角色揀選。以 `k1_mobile_tour_v1` localStorage 旗 gate，重開時不再重複顯示。

### Fixed
- **檢查清單 `school_types` 標籤補全**（`checklists_bundle.json` 再生）：補完以下項目原本缺少 `school_types` 欄位而對所有學校類型顯示的問題：
  - **課程（`curriculum`）**：79 項補標 — 6 項來自全港小學專屬通告（`edbc18_2023_pri_science` ×2 / `edbc20_2023_ph_pri` ×4，→ `['primary']`）；3 項來自小學及中學均適用通告（`edbc003_2026` / `edbc005_2026`，→ `['primary','secondary']`）；70 項來自小學課程發展指引 2024（`pri_curr_guide_2024`，→ `['primary']`）。
  - **幼稚園入學（`kg_admission`）**：16 項補標 — 7 項（`k1_admission_2627`）＋ 9 項（`kg_admin_guide`），→ `['kindergarten']`。

---

## [內容更新 + 檢索增強] — 2026-06-21 — 附件細字 footnote 入庫 · 路由獨立檢索

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）；本次為知識內容新增（EDB 文件附件表格細字 footnote）＋ 後端檢索增強。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,330 → 15,363**（＋33 curated footnote chunks）。

### Added
- **附件細字 footnote 入庫**（Channel B Supabase，＋33 chunks，`content_type=footnote_curated`）：EDB 文件附件表格底下嘅細字（註／備註／footnote）好多時藏住正文無提及嘅實質要求（費用上限、資助級別門檻、批核權、計算公式、安全門檻、法律定義、校曆日數、人手比例）。策展提煉成可搜尋知識——例：K1 報名費／註冊費上限、無薪假增薪延遲公式、過剩教師定義、特殊學校境外遊學師生比例、員工評核「三次」門檻、遣散費年資計算。

### Changed
- **路由獨立 footnote 檢索**（`backend/src/api/searchChannelB.ts` ＋ `wikiRepository.ts`）：curated footnote 以精確 cosine overlay 檢索（`searchFootnotes`），繞過範疇路由排除（footnote 來源未必在命中 route 嘅 source set）＋ ivfflat probes=8 recall 盲點；強配對（≥0.45）保證進入 LLM 合成窗。敵意測試（held-out 33 條全新口語 query）由 75.8% → 100%。Best-effort（`try/catch`），唔影響主搜尋路徑。
- 知識片段顯示數 **15,330 → 15,363**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

---

## [3.2.1] — 2026-06-18 — 文件標註 off-domain 相關性下限

> 平台版本 **v3.2.0 → v3.2.1**（`PLATFORM_VERSION`）。文件標註（📝 文件標註 tab）精準度修復：off-domain 文件（例如純法律免責聲明、對外公關文稿）唔再被強行配對出無關「相關指引」或硬塞入合規範疇。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**；Supabase chunks / facts 455 / guidelines 158 數量不變（純比對門檻調整，零資料改動）。

### Changed
- **文件標註相關性下限（`backend/src/api/annotateDocument.ts`）** —— 解決真檔收貨揭發嘅 off-domain 強行配對：
  - `GUIDELINE_RELEVANCE_FLOOR = 0.62`：段落最佳指引 cosine 低於此即視為 off-domain 強行配對，不再標為「相關指引」（實證 live `text-embedding-3-small`：off-domain ≤0.595 vs 真·貼題 ≥0.654）。
  - `DOMAIN_RELEVANCE_FLOOR = 0.45`：自動偵測合規範疇 descriptor peak cosine 低於此即不掃描，避免 off-domain 文件被硬塞範疇後湧出大量無關「未涵蓋」項（實證：off-domain peak 0.396 vs 真·貼題 0.53–0.69）。
  - 兩個下限只作用於 `/api/annotate-document`；`analyzeDocument` / `searchChannelB` / `checklistRevise` 及其獨立 endpoint 行為不變；用戶**手動指定範疇**不受影響。
- **空狀態提示（`app.html`）**：當文件無任何貼題指引或合規缺漏時，顯示「未找到需標示的貼題指引或合規項目」並引導改用「指定範疇」，取代空白報告。

### Fixed
- **OpenAI 呼叫韌性（`backend/src/lib/sdkFetch.ts` + embeddingClient/llmClient）**：v3.2.1 部署後 Render 上 Node 原生 fetch（undici）對每個 OpenAI 呼叫持續回 `Premature close`（重用咗 OpenAI 邊緣已關閉嘅 keep-alive 連線；重啟唔修、啟動嵌入快取 warm 0/455），令政策搜尋＋文件標註全線降級。同一 key／code 由其他出口正常（HTTP 200）→ 隔離為 Render egress 嘅 undici keep-alive 問題（非 OpenAI／key／應用碼）。修復：兩個 OpenAI client 改用已綁定嘅 `node-fetch`（預設每請求開新連線，繞過 stale keep-alive）；並 pin Node 至 `22.x`（`engines` + `.node-version`）確保 runtime deterministic。

---

## [維護] — 2026-06-17 — Served-URL 健康監察 · 失效連結修復

> 平台版本維持 **v3.2.0**（`PLATFORM_VERSION` 不變）；本次為監察工具新增 + 內部清理 + 失效來源連結修復。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,336 → 15,330**（−6，停用一個失效年度性來源）。

### Added
- **Served-URL 健康監察**（`dev/source/check_served_urls.py` + 每週 GitHub Actions `served_url_check.yml`）：由向量庫實際 serve 畀用戶嗰條 URL（`wiki_chunks.url`）逐條 HTTP 檢查，補足只測來源登記表（registry）嘅新鮮度監察盲點 —— 捉到登記表↔向量庫之間嘅連結漂移（首跑即揭發 2 條失效連結）。

### Fixed
- 修復 2 條搜尋結果失效連結（404）：**小學人文科課程指引通告**（向量庫存舊路徑、上游已遷移 → 重指向至有效 URL）；**學校曆／一般假期**（2025/26 年度版已被上游 2026/27 版取代 → 停用該年度性來源；校曆查詢仍由《擬定校曆表指引》覆蓋）。

### Changed
- 知識片段顯示數 15,336 → 15,330（首頁／平台介紹／README／K1_API_SPEC 同步）。
- 移除前端 SAG source-URL band-aid（`SOURCE_URL_FIXUPS`；S170 永久修復已落地、改寫已成 no-op）。

## [內容更新] — 2026-06-17 — DEBP 數字教育發展藍圖入庫 · 首頁資料庫更新日誌

> 平台版本維持 **v3.2.0**（`PLATFORM_VERSION` 不變）；本次為知識庫內容擴充 + 首頁附加功能。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 152 不變），`_meta.stats.chunks` **15,127 → 15,336**（+209，DEBP 6 源）。

### Added
- **中小學數字教育發展藍圖（DEBP）入庫**：EDB `debp.html` 6 份文件（主藍圖、行政摘要、人工智能素養學習架構、教學運用 AI 指南、AI 素養架構示例、AI 應用學與教示例）→ Channel B 共 209 知識片段（4 份文字層 + 2 份 OCR 草稿）；新增 `digital_education` 主題路由；6 源加入來源監察清單。
- **首頁「資料庫更新日誌」**：`index.html` 導覽列「進入平台」旁新增 📋 icon，開啟簡述近期新增／更新文件的彈窗（資料來源 `update_log.json`）。
- **重開「EDB 通告分析系統」入口連結**（還原 2026-06-11 S154 暫停）。

### Changed
- 知識片段顯示數 15,127 → 15,336（首頁／平台介紹／README／K1_API_SPEC 同步）。
- **指引文件庫分類「資訊科技」正名為「數字教育」**，並收錄 DEBP 6 份指引文件（公開 `guidelines.json` 152 → 158、版本 2.5.0 → 2.6.0；app 內庫指引 161 → 167）。註：指引文件庫（策展連結庫）與政策搜尋語料（Supabase）為兩個獨立系統。
- **指引文件庫支援跨範疇分類**：一份指引可同時屬多個範疇（`also_in`），瀏覽任何相關範疇都顯示（例：《特殊學校課程指引》同時見於「課程」與「學生事務」；DEBP 同時見於「數字教育」與「課程」）。文件總數維持不變（同一文件只計一次），範疇之間數目可重疊。

## [v3.2.0] — 2026-06-15 — 文件標註保留格式 · 首次導覽 · 使用手冊 · 監察清訊號 · 404 修復

> 用戶端版本由 `app.html` `PLATFORM_VERSION` 常數驅動（v3.2.0）；知識資料合約 `knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 152 不變）。Channel B 維持 **15,127** chunks（本版只修正 1 個源的 source URL，chunk 數不變）。

### Added
- **首次使用導覽 onboarding**（S169 ②）：首訪自動彈 6 步導覽（歡迎 + 5 功能 + 完成，每步 CTA 跳該分頁），`localStorage` gate（`k1_tour_done_v1`）；header「🎓 使用教學」可隨時重溫。
- **平台介紹 in-app 使用手冊 + FAQ**（S169 ③）：5 大功能逐步說明 + 常見問題，平台介紹分頁內置。
- **文件標註「改動摘要」下載**（S169 ①）：除乾淨成品版外，另出一份列明「融入正文建議」+「附錄補充」+ 計數的改動摘要 Word。
- **EDB 來源每週自動監察（email 通知）**：`freshness_check`（逢週一偵測現有 219 源內容改動）/ `discover_check`（偵測新文件）兩個 GitHub Actions 排程，結果寫入 GitHub Issue #1/#2；可經 Watch → Issues 收 email。

### Changed
- **文件標註乾淨成品版「保留原 Word 格式」**（S169 ①）：Word 輸入改用 JSZip 操作原 `document.xml`，原段落 100% 不動（保留標題/編號/表格格式），AI 建議以普通「（建議補充）」段落融入正文（無螢光、無追蹤修訂），說明集中文末附錄。解決 S167 由抽取文字重組令原 Word 標題/編號 flatten 的問題；PDF/貼上文字維持 from-text 乾淨版。
- **監察訊號校準（清訊號）**：`check_freshness.py` 重置全 215 源 baseline（修正舊「殼頁 vs 真 PDF」假象 → 假警報 9→0）；`discover_sources.py` 加 `ENUMERATION_PAGE_CAP`，封住單一目錄頁列舉灌爆（likely-real 680→223，no-loss）。令每週監察報告唔再狼來了。
- **dead-code cleanup**（S169 ⑤）：移除文件標註舊 builders（buildAnnotatedOriginalDocx/Pdf/buildEditableDocx/buildAnnotateListDocx + handlers，app.html −464 行）。

### Fixed
- **「政策搜尋」結果「開啟」連結 404（學校行政手冊）**：`sag_2025_11` 的 Channel-B 片段在 Supabase 存住畸形 URL（`/attachment/…/sch-admin-guide/index.html`，非 PDF → EDB 404）。根因為舊候選佇列入庫值、registry 已改正但 Supabase 未重新同步。修：前端 `SOURCE_URL_FIXUPS` 即時改寫至真 PDF（`SAG_C_markup.pdf`，app.html + mobile.js）+ Supabase `UPDATE` 將 383 個片段的 url 永久改正（url-only、chunk 數/＿meta 不變）。範圍 SAG-only（離線審 13,042 片段 + 線上抽查確認）。

---

## [v3.1.0] — 2026-06-15 — 手機強化 · 檢索修復 · 乾淨成品版 · SMC 內容

> 用戶端版本由 `app.html` `PLATFORM_VERSION` 常數驅動（v3.1.0）；知識資料合約 `knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 152 不變）。

### Added
- **SMC（學校管理委員會）內容入庫**（S168）：新源 `smc_constitution_sample`（官立學校學校管理委員會章程樣本，14 頁 text-layer）+18 chunks → Supabase Channel B **15,109 → 15,127**，加入 `school_governance` route。補上 corpus 一直 IMC-heavy、SMC 專屬內容稀薄的缺口（接 S166 SMC/IMC routing 修復）。
- **手機「範本下載」入口**（S164）：手機底部導航 3→4 入口；範本畫面為「桌面版功能」說明 + 桌面面板截圖示意。
- **手機可撳「搜尋」掣**（S166）：唔再淨靠鍵盤 Enter（部分手機鍵盤唔觸發提交）。

### Changed
- **文件標註輸出簡化為單一「乾淨成品版」**（S165→S167）：原文保持乾淨（無螢光、無 inline 註解），AI 建議融入正文做普通文字（「（建議補充）」標示、毋須接受修訂），說明＋EDB 出處集中文末附錄；Word/PDF/貼文字皆出。取代追蹤修訂/可編輯/清單多版本（解決「接受修訂後螢光殘留、原稿亂」）。
- **手機品牌統一**（S166）：hero／角色選擇標籤「K1 知識平台」→「香港學校政策搜尋平台」。
- **Channel B chunks**：15,109 → **15,127**（+SMC 18）。

### Fixed
- **英文縮寫 SMC/IMC 檢索路由**（S166）：英文縮寫原本唔 route → generic search 引錯源（旅遊/課程垃圾）、答案無根據。修 `searchChannelB.ts` 治理 route +`IMC`/`SMC`/英文片語（/i、word-boundary）+ query expansion bridge 英→中；audit 14 query（11 OK）+6 routing regression。
- **手機搜尋無法觸發**（S166）：見上「可撳搜尋掣」。

---

## [v3.0.0] — 2026-06-14 — 平台版本（Platform release）

> **版本說明：** `v3.0.0` 是**面向用戶的平台版本**，與凍結的知識資料合約版本分離。`knowledge.json` `_meta.version` 維持 **2.3.0**（455 條已核實事實凍結、下游 Circular System 合約不變）；`guidelines.json` 維持 2.5.0。v3.0 標誌平台由「純搜尋工具」（v2.x）擴展為**完整合規套件**。用戶端顯示版本由 `app.html` 的 `PLATFORM_VERSION` 常數驅動（不再讀 `_meta.version`）。

### Added（自 v2.3.0 起累積的平台功能）
- **📝 文件標註**（S161）：上載學校政策文件 → 逐段比對 EDB 指引 + 合規清單 gap → 原檔就地螢光標示 + 參考指引 + 可一鍵套用（Word 追蹤修訂）的建議條文 + 未定位項入附錄 → 下載標註版。Phase 2.5（S163）：per-segment 自動偵測範疇，多範疇文件各段路由至其所屬範疇。
- **📋 範本下載**（S160/S162）：15 個合規範疇的政策範本（學校版）+ 文件要求清單，共 106 份 Word 檔，按校類（小／中／特／幼稚園）篩選下載。
- **合規範疇擴展至 15 個**：新增 `kg_operation`（幼稚園營運，388 items/162 clauses/20 章；S162）+ `school_governance` 校董會治理（S154）+ `kg_admission` 幼稚園收生等。
- **跨校類 filter**（S162）：domain-level school_types，untagged clause 不再跨校類洩漏。

### Changed
- **文件標註：簡化為單一「乾淨成品版」下載**（S167，2026-06-15）：回應用戶回饋（標註版接受修訂後黃/綠螢光仍殘留、逐段註解令原稿亂）。新 `buildCleanDocx`：原文正文保持乾淨（無螢光、無 inline 💡/⚠ 註解），AI 建議融入正文做普通文字、以「（建議補充）」極簡標示，所有說明與 EDB 官方出處集中文末附錄；Word/PDF/貼上文字皆出。下載由三按鈕（追蹤修訂／可編輯／清單）簡化為單一「乾淨成品版」。打開即一份可採用、可編輯嘅政策草稿。
- **搜尋：英文縮寫 SMC/IMC 路由修復**（S166，2026-06-15）：用戶查「SMC 與 IMC 分別」原本引錯源（旅遊/課程等無關文件）、整理答案變無根據泛知識。根因＝英文縮寫唔 match `school_governance` 中文關鍵詞 → 無 route → generic semantic search 對中文治理 corpus 相似度低。修：`searchChannelB.ts` 治理 route 加 `IMC`/`SMC`/`incorporated|school management committee`（case-insensitive、word-boundary）+ `QUERY_EXPANSIONS` bridge 英→中治理詞彙。Render live 驗：SMC/IMC 查詢正確命中法團校董會（IMC）治理文件、答案有根有據。retrieval 審計 14 query（11 OK）；+6 routing regression。
- **手機：可撳「搜尋」掣 + 品牌統一**（S166，2026-06-15）：手機搜尋原只靠鍵盤 Enter 隱式提交（部分鍵盤唔觸發 → 搜唔到），加可撳「搜尋」掣（`.m-search-btn`）；hero／角色選擇 eyebrow「K1 知識平台」→「香港學校政策搜尋平台」對齊公開名。
- **文件標註：新增「可編輯 Word 版」下載 + 改善指引**（S165，2026-06-15）：回應用戶回饋（追蹤修訂版唔識用接受/拒絕；PDF 輸入→PDF 輸出不能編輯）。新 `buildEditableDocx`（由抽取文字砌 docx）：原文配對段**黃色螢光**、AI 建議條文**綠色螢光直接寫入文中（非追蹤修訂，可即改即用、毋須接受修訂）**，未定位項入「建議補充」附錄。**Word／PDF／貼上文字三種輸入皆出可編輯 Word**（解決 PDF 不可編輯）。下載列重整為三按鈕：可編輯 Word 版（推薦）／標註版原檔（Word 保留格式·追蹤修訂｜PDF 螢光）／建議清單；加清晰「三種下載」說明＋教學「Word『校閱』分頁按『接受／拒絕』」。保留 `buildAnnotatedOriginalDocx`/`buildAnnotatedPdf` 不變。純前端，backend/Supabase/凍結合約零接觸。
- **手機搜尋：修復輸入後撳 Enter 不能即時搜尋**（S165，2026-06-15）：`mobile.js` 搜尋框加 `enterkeyhint="search"` + 明確 Enter `keydown` handler（部分手機鍵盤／IME 對無提交鈕的表單唔觸發隱式提交）。
- **手機底部導航加入「範本下載」入口**（S164，2026-06-15）：手機 bottom-nav 由 3 → **4 入口**（🔍 搜尋 / 📚 指引文件 / 📋 範本下載 / ℹ️ 平台介紹）。該手機畫面**不提供實際下載清單**（學校版範本為可編輯 Word 檔，需用電腦下載編輯方便使用），改為「💻 桌面版功能」說明 + 桌面範本面板截圖示意（`templates-preview.png`），引導改用桌面瀏覽器下載。文件標註維持 desktop-only。純前端 mobile shell 加建（`mobile.js` / `mobile.css`），不涉 backend / Supabase / 凍結資料合約。
- **首頁（index.html）+ 平台介紹（app.html）改版**（S163）：核心功能改為 政策搜尋 / 文件標註 / 範本下載 / 指引文件庫 / 通告分析；hero 文案擴展；版本徽章顯示 v3.0。
- **Channel B Supabase chunks**：10,736（v2.3.0）→ **15,109**（多輪官方源入庫：ph_pri 完整重抽、IMC/SBM 治理、KG 幼稚園 2 源等）。
- **指引文件**：39 → **152** 份（registry projection + KLA/curriculum + 公積金 HR）。

### Fixed
- **kg_operation clauses schema 正規化**（S163）：由非標準 `section_no`/`name` 改為 canonical `si`/`section_name`，修正 backend supplement linkage（388/388 items 由失效恢復）+ 學校版 docx 章節名空白 bug。
- **kg_operation 改寫覆核**（S163）：17 條 QC verify flags（虛構鋪墊句／漏義務／錯引用）全部修正。

### Release hardening — v3.0 封版 QC（S163，NO-GO → GO）
- **P1 版本顯示一致**：`app.html` header/footer `displayVersion` 改由 `PLATFORM_VERSION`（v3.0.0）派生，不再讀 `knowledge.json _meta.version`（維持凍結 2.3.0）。
- **P2 幼稚園營運搜尋效度**：`searchChannelB.ts` kg_admin route 加「幼稚園營運／營運手冊／運作／健康紀錄」等自然查詢詞 → query「幼稚園營運 手冊 健康紀錄」正確路由至 kg_operation_manual/kg_admin_guide（原誤落 curriculum → 只得 g26 收生指引）；kg_admission 不受影響（routing regression 5 案）。
- **P3 標註覆蓋誇大**：`checklistRevise.ts` 加 graded 詞彙重疊閘（informative CJK-bigram，DF 自校準濾走 本校/幼稚園 等通用詞）：cosine 之上，需與最匹配段共享 ≥2 informative 詞先計 covered、≥1 計 partial、0 → missing。短窄文「保存健康紀錄量體溫清潔床單」由 covered=20/partial=55 降至 **covered=5/partial=30**（真實多段覆蓋文件不受影響，covered=37）。`MAX_ITEMS` 220→400（kg_operation 388 全評分，零截斷）。
- **P4 README** 版本徽章 v3.0.0（+ knowledge.json 凍結 2.3.0 註明）。
- **P5 worktree 衞生**：本機備份／中間檔（`*.bak_*`/`*.pre_*`/`_distill_*`/`_rewrite_*`）`.gitignore`（不刪，僅排除出 release tree）。
- **P6 Mobile scope（v3.0）**：mobile = 政策搜尋 + 指引文件 + 平台介紹（讀／搜尋面）；**文件標註 為 desktop 功能**（涉及檔案上載 + Word/PDF 生成，需較大畫面）。詳見 `PROJECT_MASTER_SPEC.md` §B.5。
- **Regression**：修正 2 條失效已久的 stale 斷言（schema 版本硬編 1.3.1 → 2.3.0/2.5.0；role-bucket distinctness → union-selector「兩角色均取得事實」），+ 加 P2 routing / P3 lexical-gate regression（`backend/scripts/semanticRegression.ts`，20 PASS / 0 FAIL）。

---

## [v2.3.0] — 2026-05-16

### Changed
- **語義去重（792 → 455 facts）**：三層同步（root role_facts.json + knowledge.json + dev/knowledge/role_facts.json）
  - Phase 1：合併 193 組跨 bucket 完全重複字串至 `all_roles`，移除 275 條跨角色完全重複副本
  - Phase 2：合併 36 組相近事實為加強版 canonical 句子（折疊 98 個變體出現）
  - backend selector union（`all_roles` + role buckets）擔保無語義內容流失，無角色失去可見度
  - 衝突事實（不同日期／科目／數字）刻意保留分開
  - 可逆合併日誌：`dev/DEDUP_LOG_2026-05-16.md`（commit 711f911）
- **`knowledge.json` `_meta` 更新**：version 2.3.0、updated 2026-05-16、stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}`

---

## [v2.2.1] — 2026-05-03

### Changed
- **已核實事實庫去重**：Strategy B dedup 三層同步（root role_facts.json + knowledge.json + dev/knowledge/role_facts.json）由 1,001 → 792 facts；移除 209 條 all_roles 與個別 role bucket 重複副本；backend selector union 邏輯擔保 Circular System 注入內容不變
- **Channel B 學校行政手冊來源別名映射**：wikiRepository.ts 加 SOURCE_ALIASES { g24 → sag_2025_11 }，配額計數時兩個 source_id 共享 cap bucket，避免雙重 ingestion 重複佔位
- **Channel B Query expansion 補病假 vocabulary**：searchChannelB.ts QUERY_EXPANSIONS.hr_admin 加「病假 首年 168日 上限 醫生證明 教師註冊 聘任」7 個 specific keyword；線上驗收 g04 升至第 1 位 score 0.7247
- **三層 _meta 加 stats block**：facts/chunks/sources/guidelines/topics 統一 single source of truth，前端首頁同平台介紹從 _meta.stats 動態載入

### Fixed
- 教師病假 query synthesis 由錯誤（混淆 SAG 學校假期表 366 日）改為準確（g04 真實內容首年 28 日 / 其後 48 日 / 上限 168 日 / 120 日門檻）

---

## [v2.2.0] — 2026-05-02

### Changed
- 全平台視覺重設：EDB 深綠 nav（全4個HTML）、主題顏色系統 token、航班板式搜尋結果行列、字型層次優化、手機 sticky 搜尋欄、手機底部 tab bar
- index.html 改寫為 K1知識平台 Landing Page（hero + 統計帶 + 功能卡 + 角色網格 + CTA）
- Hash routing：`app.html#guidelines` deep-link 啟動；`switchView()` 更新 URL hash
- SVG favicon 加入全4個HTML（深綠圓角方塊 + K1白字）
- Source 標籤系統：UI 全面以中文顯示文件來源，移除內部代碼（g04 等）
- Vault 擴充：g24（學校行政手冊）、g29（幼稚園課程指引）新增 embed；Supabase 達 10,736 chunks

---

## [v2.1.2] — 2026-05-01

### Changed
- Channel A semantic search + LLM synthesis; loading UX; near-dedup; Channel B/AB min_score 0.15

---

## [v2.1.1] — 2026-04-30

### Changed
- Phase 4: 指引文件庫 sub_category 雙重分組排序（category → sub_category → year desc）+ CIRCULAR_SYSTEM_INTEGRATION.md 規格文件

---

## [v1.4.0] — 2026-04-12

### Changed
- Knowledge Platform Phase 1+2: source registry (148 sources), freshness monitoring, GitHub Actions CI, online semantic regression PASS=12/FAIL=0

---

## [v1.3.1] — 2026-04-08

### Changed
- 平台 schema v1.3.0 後補上 backend split-role compatibility bridge

---

## [v1.2.2] — 2026-04-04

### Changed
- 統一版本號至 v1.2.2：guidelines.json 接口就緒，knowledge.json + guidelines.json 公開 API 端點已 commit

---

## [v1.1.0] — 2026-04-03

### Changed
- **角色架構重構**：`department_head`（科主任）拆分為兩個明確職級：
  - `panel_chair`（學位主任）— 跨科／年級「範疇負責人」，策劃與統籌工作
  - `subject_head`（科主任）— 科本課程與評估領導
- `all_roles` 顯示標籤更新為「全校適用」，職級定義更清晰
- UI Role 下拉選單及 badge 配色更新，學位主任採藍靛色（indigo）

### Added
- **學位主任事實（25 條新增）**：覆蓋 8 類學位主任職能跨 7 個主題：
  - 課程統籌主任、訓導及輔導主任、總務主任、資訊科技統籌主任
  - 特殊教育統籌主任、學生事務主任、教務主任、活動主任
- 知識庫事實總數由 81 條增至 **106 條**

---

## [v1.0.1] — 2026-04-03

### Changed
- 移除 `displayVersion` 的動態 build stamp（不再隨每次時間改變），直接依賴手動版本號更新，使版本顯示更穩定清晰。
- 修復了 `ExportModal` 中的 React Error 310 (Hooks 渲染順序違規) 問題，解決點擊 `匯出 / 備份` 導致畫面崩潰的錯誤。
- 將原先公開顯示的 `匯出 / 備份` 按鈕加上 `adminMode` 權限鎖，確保只在管理員登入後才可見及點擊。

---

## [v1.0.0] — 2026-04-03

### Changed
- 平台版本正式由 `v0.9.0` 升級至 `v1.0.0`
- 前端資料來源 `_meta.version` / `_meta.updated` 已同步到 `k1-dashboard.html` 與 `dev/knowledge/role_facts.json`
- README 版本徽章更新為 `v1.0.0`
- Semantic topic detector threshold 已收緊至 `0.45`，減少財務通告混入不相關主題事實

### Added
- **管理員登入保護**：新增 `🔒/🔓` header 按鈕、密碼 modal、SHA-256 驗證，以及所有寫入操作的 admin gate

### Notes
- `v1.0.0` 代表平台已具備管理員保護與版本升級後的基線功能
- Git tag / GitHub release 是否已建立，需按實際 push / tag 流程另行確認

---

## [v0.9.0] — 2026-03-17

### Changed — Source Audit (全面出處升級)
- **HR**: 所有出處升級至具體 EDB PDF：CPD 通告 `EDBC20006C.pdf`、整合代課教師津貼指引 `TRG_guidelines_C.pdf`（2023）、批假通告 `embc06001tc.pdf`（2006）
- **Activity**: 「學校活動指引」拆分為兩份具體 PDF：`Study%20Tours%20Guide_TC.pdf`（境外遊學）、`Outdoor_TC.pdf`（戶外活動），sourceMap 分別指向對應文件
- **Student**: 訓育工作指引更新至具體章節 PDF `ch1.pdf`
- **Curriculum**: 《小學教育課程指引》從 HTML 索引頁升級至完整 PDF `PECG%202024_full.pdf`
- **IT**: 從泛用 IT 系統頁面升級至《學校資訊保安建議措施》具體章節 PDF：`isrp-ch02-tc.pdf`（保安管理）、`isrp-ch06-tc.pdf`（數據保安）
- **General**: 校本管理舊 URL 更新至新網站 `sbm.edb.gov.hk`（2024年8月遷移）

### Fixed
- **HR 事實錯誤**：`teacher[1]` 代課教師政策「連續缺席超過5個工作天」描述有誤——已更正為實際政策：整筆現金津貼 + 缺假30–89日（日薪發還）/ 90日或以上（月薪發還）
- **GUIDELINES_REGISTRY g28**：URL 錯誤指向「小學教育」概覽頁——已修正至實際《學校資訊保安建議措施》頁面

### Reset
- 全部 81 個事實重設為 **draft** 狀態，待重新批核（出處升級後需重新審閱）

---

## [v0.8.1] — 2026-03-17

### Fixed
- Finance source 出處更新：採購指引升級至 2024 PDF（`Guidelines%20on%20Procurement%20Procedures...pdf`）
- Finance 事實修正：3 個財務事實內容更正（採購門檻、報價規定、廉潔約章細節）

---

## [v0.8.0] — 2026-03-17

### Added
- **🔍 智能搜尋（QAPanel）**：第三個視圖模式，跨全部 81 個事實關鍵字搜尋
  - 支援空格 / 逗號分隔多關鍵字
  - 搜尋結果顯示主題標籤、角色標籤、出處連結、關鍵字高亮
  - 6 個示例查詢 chips 快速入門
  - 標題顯示可搜尋事實總數標誌

---

## [v0.7.0] — 2026-03-17

### Changed
- 全面替換泛用「學校行政手冊」引用為具體 EDB 子頁面 URL（共 30 個唯一出處）
- HR：CPD 教師頁面 + 代課教師津貼頁面
- IT：修正 IT 系統資源頁面 URL（舊連結指向錯誤）
- Activity：重新映射至具體學校活動指引頁面
- Student：反欺凌 → 全校訓輔；SEN → 融合教育；訓輔 → 訓育指引；受虐 → 學生安全
- Finance：新增擴大營辦津貼及政府津貼處理參考頁面
- Curriculum：修正 PECG URL，新增 STEAM + 人文科（PSHE）出處

---

## [v0.6.1] — 2026-03-17

### Changed
- 用戶批核所有 32 個草稿事實 → 全部 81 個事實狀態改為 approved
- 清空 `DRAFT_INDICES`

---

## [v0.6.0] — 2026-03-16

### Added
- **指引文件庫（GuidelinesPanel）**：tab 分類導覽（11 個類別）
  - 全部 / 課程 / 財務採購 / 人力資源 / 學生事務 / 學生安全 / 科目安全 / 活動 / 津貼 / 行政 / 資訊科技
  - 每個 tab 顯示 emoji + 類別名稱 + 文件數量標誌
  - 搜尋欄跨類別搜尋
- `GUIDELINES_REGISTRY`：28 份 EDB 官方指引文件
- 標題視圖切換：知識庫 / 指引文件庫

---

## [v0.5.0] — 2026-03-16

### Added
- Guidelines Library 初版（下拉篩選，後重設計為 tab 版）
- EDB 網站爬取「指引」文件清單
- 更新各主題 `_sources` 增加指引連結

---

## [v0.4.0] — 2026-03-16

### Added
- **初始版本**：學校管理知識中心
- React 18 + Babel + Tailwind CDN 單一 HTML 架構
- 7 個主題 × 7 個角色共 57 個事實（初始版本）
- 審核工作流：Draft → Approved，批量批核，JSON 匯出
- 每個事實的出處連結（`_sourceMap` + `_sources`）
- AGENTS.md 工作流治理框架
- `dev/knowledge/role_facts.json` 數據備份

---

[v0.9.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.9.0
[v0.8.1]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.8.1
[v0.8.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.8.0
[v0.7.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.7.0
[v0.6.1]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.6.1
[v0.6.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.6.0
[v0.5.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.5.0
[v0.4.0]: https://github.com/leonard-wong-git/edb-knowledge/releases/tag/v0.4.0
