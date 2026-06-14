# Changelog

All notable changes to the 學校管理知識中心 are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v3.0.0] — 2026-06-14 — 平台版本（Platform release）

> **版本說明：** `v3.0.0` 是**面向用戶的平台版本**，與凍結的知識資料合約版本分離。`knowledge.json` `_meta.version` 維持 **2.3.0**（455 條已核實事實凍結、下游 Circular System 合約不變）；`guidelines.json` 維持 2.5.0。v3.0 標誌平台由「純搜尋工具」（v2.x）擴展為**完整合規套件**。用戶端顯示版本由 `app.html` 的 `PLATFORM_VERSION` 常數驅動（不再讀 `_meta.version`）。

### Added（自 v2.3.0 起累積的平台功能）
- **📝 文件標註**（S161）：上載學校政策文件 → 逐段比對 EDB 指引 + 合規清單 gap → 原檔就地螢光標示 + 參考指引 + 可一鍵套用（Word 追蹤修訂）的建議條文 + 未定位項入附錄 → 下載標註版。Phase 2.5（S163）：per-segment 自動偵測範疇，多範疇文件各段路由至其所屬範疇。
- **📋 範本下載**（S160/S162）：15 個合規範疇的政策範本（學校版）+ 文件要求清單，共 106 份 Word 檔，按校類（小／中／特／幼稚園）篩選下載。
- **合規範疇擴展至 15 個**：新增 `kg_operation`（幼稚園營運，388 items/162 clauses/20 章；S162）+ `school_governance` 校董會治理（S154）+ `kg_admission` 幼稚園收生等。
- **跨校類 filter**（S162）：domain-level school_types，untagged clause 不再跨校類洩漏。

### Changed
- **首頁（index.html）+ 平台介紹（app.html）改版**（S163）：核心功能改為 政策搜尋 / 文件標註 / 範本下載 / 指引文件庫 / 通告分析；hero 文案擴展；版本徽章顯示 v3.0。
- **Channel B Supabase chunks**：10,736（v2.3.0）→ **15,109**（多輪官方源入庫：ph_pri 完整重抽、IMC/SBM 治理、KG 幼稚園 2 源等）。
- **指引文件**：39 → **152** 份（registry projection + KLA/curriculum + 公積金 HR）。

### Fixed
- **kg_operation clauses schema 正規化**（S163）：由非標準 `section_no`/`name` 改為 canonical `si`/`section_name`，修正 backend supplement linkage（388/388 items 由失效恢復）+ 學校版 docx 章節名空白 bug。
- **kg_operation 改寫覆核**（S163）：17 條 QC verify flags（虛構鋪墊句／漏義務／錯引用）全部修正。

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
