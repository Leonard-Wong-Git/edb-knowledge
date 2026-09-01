# Changelog

All notable changes to the 學校管理知識中心 are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [檢索修正] — 2026-09-01 — 修好被強制置頂片段遮蔽的判斷閘豁免（S211）

> 平台版本維持 **v3.3.2**（純後端）。凍結合約零接觸；語料未動。接上一則：新增路由把答案拉進了合成視窗，但問題仍然答不出來，本則是餘下那一半。

### Fixed
- **強制置頂的註腳片段會令合格的 vault 片段失去判斷閘豁免。** `synthesizeAnswer` 以 `top5[0]` 判斷「lead 是否為分數 ≥ 0.70 的 `vault_extract`」，符合即跳過 S177 判斷閘。但註腳覆蓋層（S174／S196）會依自己的閘（0.45 分＋2 個資訊性 bigram）把最多兩個註腳強制插到最前，spotlight 覆蓋層再插一個——`top5[0]` 因此指向被強制插入的片段，真正的主搜尋 lead 即使清了 0.70 這條實測門檻也拿不到豁免，判斷閘於是被要求裁決一段本來已經答到問題的文字。
  - 實測於「只修讀中學師資資格是否可以在小學任常額職位」：主搜尋 lead 為 `faq_edbc19011` **0.709**，逐字載有「資助小學的新入職教師必須持有本地學士學位（或同等學歷）及小學師資訓練」；但兩個註腳（小學科學科學歷豁免 0.506、過剩教師定義 0.502，皆與入職資歷無關）佔住第 1、2 位。判斷閘因而拒答，且改寫五個版本的判斷提示、連同改用 gpt-4o 測試，都無法令它改口——問題不在提示措辭。
  - 改為判斷 `results[forcedLeads]`，即覆蓋層插入之前第 1 位本來是哪一段（其後的 `rest` 依分數排序，故沒有強制插入時與舊寫法逐位元相同）。**0.70 門檻本身未動**：S183 所測的「≥0.70 即為直接主題命中」是片段的性質，本次只是修正這個性質該從哪一段讀取。
- 一個較寬鬆的草案（掃描整個前五）已被實測否決：它會令 `GN02_nonteach_maternity`（「學校非教學人員產假有幾多日」）取得豁免——該題主搜尋 lead 是 0.782 的註腳，視窗內 0.744 的 `vault_extract` 是《學校行政手冊》假期附錄，屬同一語域而非答案，正是 S177 那一類。已收窄並將此結果記於程式註釋。

### Added
- **`dev/source/vault_lead_delta.mjs`** — 確定性量度腳本。判斷閘與合成都是未設 temperature 的 LLM 呼叫，同一套 case 連跑兩次結果會不同：本次頭兩輪 full-pipeline 分別在 `GN02` 與 `GN03` 冒出 false answer，而該兩題根本不在改動影響範圍內，純屬雜訊，差點導致錯誤結論。此腳本不呼叫 LLM，只用確定性的檢索分數算出每個 case 的 `forcedLeads`、舊規則所看的 slot 0 與新規則所看的 mainLead，直接列出 bypass 判斷真正改變的 case。對 35 個凍結 case 加本次目標題的結果：**恰好 3 題由 judge 轉為 bypass，且全部標記為「能」**（本次目標題、`S01_ai_intro_bare_noun`、`GN11_procurement_threshold`），標記為「否」的 21 題**無一受影響**。

---

## [檢索修正] — 2026-09-01 — 教師入職資歷查詢新增專屬路由（S211）

> 平台版本維持 **v3.3.2**（純後端檢索改動）。凍結合約零接觸。Supabase 語料未動——本次不是入庫，答案本來就在庫內。

### Fixed
- **「只修讀中學師資資格是否可以在小學任常額職位」一類入職資歷問題答不出來。** 系統回覆「暫時未能找到可直接回答此問題的明確資料」，但答案其實早在語料內，載於《資助學校教師職位全面學位化政策常見問題和解答》答 14（「資助小學的新入職教師必須持有本地學士學位（或同等學歷）及小學師資訓練才可擔任核准編制內的教師」）及《學校行政手冊》引《資助則例》的入職條款（並明言「小學教育課程設有小學實習課程，中學教育課程設有中學實習課程」）。
  - 成因是路由：`detectQueryCategory` 對這類問法回傳 `null`，於是既無來源過濾亦無查詢擴充，裸向量在 17,593 個片段中只撈到同主題但答非所問的學位化條文。兩段決定性條文分別排第 10（0.585）與第 63（0.533），進不了前五的合成視窗，S177 判斷閘因而**正確地**拒答——拒答不是缺陷，是設計；缺陷在檢索。
  - 新增 `teacher_qualification` 專屬路由（PLAN-1b 模式），配自己的查詢擴充。實測同一問題：答 14 由第 10 升至 **第 1（0.709）**、行政手冊條款由第 63 升至 **第 9（0.641）**。
  - **實測否決了直覺解法**：把這類問題歸入 `hr_admin`（該路由本來就擁有「聘任／入職／教師資格」關鍵詞）反而最差——其假期／薪酬擴充（假期 批假 病假 168日）把向量拉往假期附錄，兩段答案**雙雙跌出前 80**。此結果已寫入 `SOURCE_SETS.teacher_qualification` 的註釋，以免日後有人把它折回 `hr_admin`。

### Added
- **`dev/source/route_regression.mjs`** — 路由回歸測試。直接由 `searchChannelB.ts` 讀取真正的 `TOPIC_KEYWORDS` 求值，不另寫一份 Python 版本（兩份定義會就 `\b`、量詞、`/i` 的處理靜靜分岔）。31 條 query 涵蓋每條現有路由，全數 PASS；本次改動未令任何既有 query 改變路由。另設「已知缺口」區塊，收錄路由不到但非本次造成的問法（現有一條：「12 班小學有幾多個學位教師」——`staffing` 認「學位教師職系」而不認「學位教師」），只報告不影響退出碼。

---

## [文案修正＋防漂移] — 2026-09-01 — 清走仍在應承已收起功能的散文（S211）

> 平台版本維持 **v3.3.2**（`PLATFORM_VERSION` 不變）；本次只改 HTML 文案與文件，未動 `mobile.css` / `mobile.js`，故不需推進快取鍵。凍結合約零接觸。

### Fixed
- **三處散文仍在應承一個已收起的功能。** S204 於 2026-08-18 收起「範本下載」分頁，但下列句子一直照樣列出該功能，直至今日：`app.html` 平台介紹 hero 段「並下載 15 個範疇的政策範本」、`index.html` `.hero-desc` 同一句、`index.html` `<meta name="description">`「政策範本下載」（後者會出現在搜尋引擎摘要）。三處改為只描述實際可用的功能。
- **`README.md` 與實況對齊**：功能表與「五 tab 介面」一句照舊把「範本下載」當現行功能（實為 S204 收起，現行四 tab）；手機版章節仍寫「偵測 ≤640px **或手機 UA**」（該閘已於本輪 S211 拆走）與「底部導航 4 個入口」（現為 3 個）。

### Changed
- **把「收起／恢復分頁」的漂移點寫成清單，防止同一類錯誤再發生。** 這批文案錯了 13 日無人察覺，原因是 `FEATURE_TABS` 只驅動元件，不驅動散文。`app.html` head 的分頁開關註釋新增第 8 項（點名四處散文）與第 9 項（功能數字一律推算、不得寫死），並加入「改動 `mobile.css`/`mobile.js` 必須推 `PLATFORM_VERSION`」一條；`dev/DOC_SYNC_CHECKLIST.md`「Tab withdraw / restore」一列重整為 A flag 驅動／B 推算數字／C 人手散文／D 版本與記錄四組，驗證欄加入「grep 該功能關鍵詞確認無剩餘應承語」。

---

## [修正] — 2026-08-31 — 手機導覽功能數目寫死（S211）

> 平台版本 **v3.3.1 → v3.3.2**。凍結合約零接觸。與上一則同屬 S211 同一輪修正；獨立推進版本，是因為 `mobile.js` 以 `?v=<平台版本>` 作快取鍵，沿用 3.3.1 會令剛取得 3.3.1 的訪客讀不到這次改動。

### Changed
- **手機首次使用導覽開場白改為按實際入口數顯示。** 原文寫死「四個主要功能」，但底部導覽在 S204 收起「範本下載」後只餘三個入口，導覽本身亦只有兩版功能卡。現由底欄過濾後的功能入口數推算（「平台介紹」屬簡介版面，不計為功能），與 `app.html`「N 大功能 · 點樣用」同一處理。

---

## [修正] — 2026-08-31 — 平板／橫放手機版面錯位、統計列換行、功能數目寫死（S211）

> 平台版本 **v3.3.0 → v3.3.1**。凍結合約零接觸（`knowledge.json` `_meta.version` **2.3.0**、facts **455**、`guidelines.json` **2.6.1 / 158**）。純前端，不涉後端、資料管道或知識庫內容。

### Fixed
- **平板／橫放手機版面錯位。** `mobile.js` 以「視窗闊度 ≤640px **或** 流動裝置 UA」決定啟用手機介面，但 `mobile.css` 全份規則只寫在 `@media (max-width: 640px)` 之內——兩道閘條件不一致。任何流動裝置 UA 而視窗闊過 640px 的情況（iPad、Android 平板、手機橫放）都會建出一個樣式表根本不會套用的手機介面：約 362px 無樣式內容堆在頁首，把真正的應用整段推低。實測重現：700px + 流動裝置 UA，`#root` 頂部偏移 337–362px。改為單以視窗闊度作閘（闊過 640px 的流動裝置改用響應式桌面版面），並在 `mobile.css` 末端、`@media (max-width: 640px)` 之外加上 `@media (min-width: 641px)` 保險規則，令視窗在載入後才跨過斷點時遺留的介面殘骸不會再顯示。
- **靜態資源快取鍵未隨改動更新。** `mobile.css` / `mobile.js` 在四個 HTML 以 `?v=<平台版本>` 引用，若沿用 3.3.0 則舊訪客會繼續讀快取中的舊檔、收不到上述修正。版本推進至 3.3.1 同時更新四個引用。
- **平台介紹統計列換行。** 五格統計（第五格為「累計查詢次數」）以 `auto-fill` + `minmax(180px)` 排版，在 960px 容器內只夠排四格，第五格跌落第二行。改為按實際格數開軌（`repeat(N, minmax(0,1fr))`），四格或五格都必定同一行。

### Changed
- **「五大功能 · 點樣用」與導覽開場白改為按實際功能數顯示。** 兩處各自寫死「五」，S204 收起「範本下載」後便與畫面不符（使用手冊實際只列三項）；導覽開場白更點名「亦可下載政策範本」，應承一個平台已不再提供的功能。兩處現由過濾後的清單推算，日後收起或恢復任何分頁都不需人手改字。

---

## [介面調整] — 2026-08-31 — 收起「EDB 通告分析系統 簡介」（S211）

> 平台版本維持 **v3.3.0**（`PLATFORM_VERSION` 不變）；凍結合約零接觸（`knowledge.json` `_meta.version` **2.3.0**、facts **455**、`guidelines.json` **2.6.1 / 158**）。純前端呈現改動，不涉後端、資料管道或知識庫內容。

### Removed
- **收起「EDB 通告分析系統 簡介」卡**（Leonard 指示）。兩個呈現面同時隱藏：`app.html` 平台介紹「平台核心功能」的 channel 卡（`channels` 陣列該項 comment 掉），以及 `index.html` 首頁核心功能區的同名 `feature-card`（加 `style="display:none"`，跟 2026-08-18 S204 收起「範本下載」的同一慣例）。首頁「進入 EDB 通告分析系統」外部入口連結隨該卡一併不再顯示——此為全站最後一個指向該外部系統的使用者入口，`README.md` 原本已載明「通告分析入口為休眠狀態（backend route 保留、前端入口已移除）」，本次改動後該描述與實況一致。
- 兩處均為**可還原隱藏**，原始標記完整保留在檔案內並附還原方法註釋；backend route 及知識管道不受影響。

---

## [內容新增＋檢索修正] — 2026-08-18 — 人手編制文件群入庫、頁碼歸屬修正（S204）

> 平台版本 **v3.2.2 → v3.3.0**。凍結合約零接觸：`knowledge.json` `_meta.version` **2.3.0**、facts **455**、`guidelines.json` **2.6.1 / 158**。Supabase **16,070 → 17,472**；`source_registry.json` 257 → **268**；`GUIDELINES_REGISTRY` 166 → **177**；`_meta.stats.sources` 120 → **288**（積壓漂移，本次按 Supabase distinct source_id 扣除 7 個 `role_facts_*` 偽來源後校正）。

### Added
- **「資助小學學位教師」文件群 10 份入庫**（1,316 個知識片段）：資助小學教學人員編制表、學位教師職系職級角色和職能、學生輔導教師出任學位教師職位、學位化政策 FAQ 與簡報、教育局通告 11/2019 與 30/2000、小學及特殊學校《資助則例》。此前 256 個來源中**無一份涵蓋人手編制**，「學校有幾多班就有幾多老師」一類問題無從作答；連用文件全名查詢亦返回零相關結果。
- **`dev/vault/extract_table_rows.py`** — 表格文件的座標重建抽取。PyMuPDF 的 `get_text("text")` 會把編制表逐欄倒出，行的歸屬完全消失；`find_tables()` 亦無效（該等 PDF 無逐行框線）。新腳本按文字方塊 y 座標重建真實行，每行輸出一句自足敘述，並以算術不變式（校長＋副校長＋學位＋助理 ＝ 合計）逐行驗算，任何一行不符即中止寫入。
- **`staffing` 路由**（`searchChannelB.ts`）——人手編制查詢不再套用 `hr_admin` 的假期／薪酬詞彙擴充。實測該擴充令編制查詢 cosine 由 0.816 跌至 0.616。
- **每源 `chunk_cap` / `chunk_max_chars` 覆寫**（`expand_vault.py` 讀 registry）。全域 300 上限保留開頭、丟棄結尾，兩份《資助則例》因此被截走 209 及 401 個片段，當中含非教學人員編制條款。

### Fixed
- **搜尋結果頁碼歸屬**。原取片段中第一個 `=== Page N ===` 標記，片段跨頁時報錯頁——實例：某片段 96% 內容屬第 53 頁，僅末 5 字後有第 54 頁標記，系統報 54。改為取承載最多內容的頁。全庫 15,601 個有頁碼片段中 **5,453 個（35%）頁碼改變**，其中 4,927 個為 −1。對真 PDF 核驗：《學校行政手冊》147/147、《幼稚園行政手冊》127/127 落在實際載有該段文字的頁，舊邏輯為 74.1% / 63.0%。影響搜尋結果、文件分析、標註輸出的 `#page=N` 連結。

### Held back
- **資助特殊學校小學部教學人員編制**（`staff_est_sp_sch_pri`）入庫後已移除片段。該表按「教學人員總數」索引而非班數，合成器將其套用於普通小學的班數問題，對「12班小學有幾多個學位教師」連續 3 次作答 12 名（正確為 5 名）。vault 抽取與 registry 條目保留，待「資料對象 vs 問題對象」核對機制落地後再入庫。文件本身仍列於 📚EDB指引 供瀏覽。

---

## [內容新增＋引用修正] — 2026-07-27 — 校車指引五份入庫、視藝／科技安全指引引用修正（S195 下半）

> 平台版本維持 **v3.2.2**。凍結合約零接觸：`knowledge.json` `_meta.version` **2.3.0**、facts **455**、`guidelines.json` **2.6.1 / 158**。Supabase **16,033 → 16,062**；`source_registry.json` 250 → **256**。

### Added
- **《學童乘搭學生服務車輛的安全指引》2026/27 版，供司機／跟車保母／營辦商／家長／學童五份**（共 28 個知識片段）。此前資料庫只收錄「供學校遵守」一份，故「跟車保母有咩要求」「校巴司機責任」等問題無從作答。五份均已核對頁碼與原文對應。
- **《視覺藝術科安全指引（中學）》**（27 個片段）。此文件原本並無獨立收錄 —— 其內容一直混在小學版之內（見下）。

### Fixed
- **視覺藝術科安全指引：一半內容掛錯文件。** 原本的抽取檔把小學版與中學版兩份文件接連編號成一份（46 頁），但全部片段都標示為小學版的連結，即約一半引用指向一份它們並不屬於的 22 頁文件，頁碼更超出該文件範圍。現已分拆為《小學》與《中學》兩份獨立文件，頁碼與各自原文逐頁對應。
- **科技教育–安全指引：引用頁碼整體相差一頁。** 原抽取檔遺漏了封面頁，令每個引用的頁碼都比實際 PDF 頁面早一頁。已重抽全 52 頁修正，文件名稱亦更新為封面所載全名。
- 移除公開指引庫中一條重複且連結失效的宗教教育科條目（連結為 AI 搜尋工具的轉址殘留）。正確的 2024 年版指引一直在庫內，故公開文件數目維持 **158** 不變。

### Changed
- 兩條重複登記的來源（`kgecg_2017`、`g31`）標記為已取代 —— 兩者皆無內容片段，實際內容由 `g29` 與 `eng_pri_guide_2025` 承載。合併前已核實 `kgecg_2017` 與 `g29` 指向同一份文件（同為 108 頁、逐頁對齊、差異僅屬文字層抽取瑕疵）。

### Notes
- **整理答案的防砌數門檻維持 0.70，並附上實測理由。** 有意見認為新入庫來源評分 0.62–0.63 被拒答，門檻應該調低。實測 20 條敵意查詢後結論相反：「貌似學校事務但答案根本不在庫內」的查詢最高可達 **0.632**，而真正命中的最低只有 **0.624** —— 兩者重疊，任何門檻數值都無法區分「找到對的文件」與「找到語域相同的文件」。新增工具 `dev/source/judge_probe.py` 可隨時重跑。
- 檢索 spotlight 名單曾嘗試精簡，但前後對照測試顯示三條查詢由通過變失敗，已即時還原。

---

## [連結修復＋內容更新] — 2026-07-27 — 修復三條壞死的文件連結，其中校車安全指引換上 2026/27 版（S195）

> 平台版本維持 **v3.2.2**（`PLATFORM_VERSION` 不變）。凍結合約全部零接觸：`knowledge.json` `_meta.version` **2.3.0**、facts **455**、`guidelines.json` **2.6.1 / 158**（僅 `_meta.updated` 隨重生更新為 2026-07-27）。Supabase chunk 總數 **16,035 → 16,033**（校車安全指引改版：＋7 新版／−6 舊版獨有）；`source_registry.json` **250 不變**（只改既有條目欄位）。

### Fixed
- **《資助學校採購程序指引》連結 404（`g01`，34 chunks）。** 教育局將檔案改名（`…Trad Chi_2024.pdf` → `Guidelines on Procurement Procedures_TC.pdf`），舊連結自約 2026-06-29 起 404。已重新指向新檔；重抽新檔逐頁比對已入庫內文，**30/30 頁完全相同**，故只更新連結、無需重新入庫。
- **《生活與社會課程指引（中一至中三）（2010年）》連結 404（`ls_jss_2010`，251 chunks）。** 教育局將檔案搬入個人、社會及人文教育學習領域的檔案庫（`/pshe/archive/Life_and_Society/`）。已重新指向；**183/183 頁完全相同**，同樣只更新連結。
- 兩條連結的所有副本一併更正：`source_registry.json`、`app.html` 指引文件庫、`guidelines.json`（經 `dev/build_guidelines.py --write` 重生，非手改）、`data.json`、`dev/checklists/_src/secmeta.json`，以及 Supabase `wiki_chunks.url` **285 行**（`#page=` 錨點原樣保留）。

### Changed
- **5 條 `source_type=pdf` 但連結指向網頁的登記已整理**：`g21`／`g22` 的 `url_primary` 改為資料庫實際供應的直連 PDF（登記追上實況）；`g31` 改指其真身 PDF 並標明與 `eng_pri_guide_2025` 為同一份文件；`g30` 的 `source_type` 由 `pdf` 更正為 `html`（已退役的入口頁）；`religious_edu_jss` 找回直連 PDF —— 封面核實為《宗教教育課程指引（中一至中三）》**二零二四年**版，標題與版本標籤按封面更正，狀態由 `candidate` 改為 `verified`（尚未入庫）。

### Updated
- **《學童乘搭校車的安全指引》換上 2026/27 學年版（`g18`）。** 舊 2025/26 版檔案已被教育局撤下（連結 404）。逐頁比對顯示新舊版只有 3/8 頁相同 —— 屬**內容改版而非改名**，因此**重新入庫**而非只改連結：新版 6 頁抽出 7 個片段入庫，再刪走只屬舊版的 6 個片段。**注意**：chunk 編號以內容雜湊產生，兩版有 3 段文字完全相同故編號重疊，若按來源編號一次過刪除舊版會連現行內容一併刪走 —— 實際刪除集為「舊編號減新編號」。刪除步驟由 Leonard 執行。

### Known issues（未修）
- **`g21`／`g22` 引文頁碼錯開一頁**；`g21` 更有約一半 chunks 實際來自中學版《視覺藝術科安全指引》卻掛住小學版連結。詳見 GitHub issue #5。
- 同一頁的另外五份 2026/27 版指引（供司機／保姆／營辦商／家長／學生）從未入庫，待決定是否收錄。

---

## [內容新增＋資料更正] — 2026-07-26 — 人工智能初探框架正文入庫＋修正一個長期指錯文件的來源（S194）

> 平台版本維持 **v3.2.2**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines.json 2.6.1 公開 158 不變）；`_meta.stats.chunks` **15,901 → 16,035**（＋215 INSERT／−81 DELETE，淨 +134）；`source_registry.json` 248 → **250**（＋2 new sources）。

### Added
- **《小學資訊與創新科技課程框架》—「人工智能初探」範疇（試行版）** 框架正文（18 chunks，`iit_ai_framework_2026`，13 頁 text-layer，digital_education route + spotlight）。此前庫內只有公布該框架的通函 `edbcm113_2026`（3 chunks＝封面＋摘要），故「人工智能初探」查詢無實質內容可答；入庫正文係正解，並非降低 spotlight 門檻。
- **資訊及通訊科技 課程及評估指引（中四至中六）2021** 真正文（116 chunks，`ict_sss_2021`，120 頁，curriculum route）。

### Fixed
- **`ict_sss_2021` 一直指向錯誤文件。** 該 entry 標題為《資訊及通訊科技（中四至中六）2021》，但 `url_primary` 指向 `CS_CAG_S4-6_Chi_2021.pdf` —— `CS` 被當作 Computer Science，實為 **C**itizenship and **S**ocial development，即《公民與社會發展科課程及評估指引》。結果 81 個公社科 chunks 長期掛住 ICT 標題供用戶檢索（生產環境實測：搜「公民與社會發展科」最高分結果標題為「資訊及通訊科技」），同時真 ICT 2021 指引從未入庫。修正：新增 `cgss_sss_2021` 承載該 81 chunks（**內容逐字不變**，chunk hash set 81/81 比對相同）、刪除掛錯 id 的 81 chunks、`ict_sss_2021` 改指 EDB 官方 ICT 檔並入庫真正文。
- **`curriculum` route 從未包含任何 ICT 來源**，故「資訊及通訊科技 課程指引」查詢結構上無法返回 ICT 指引（修正前實測 top-8 內兩個 ICT 來源皆不出現）。已加入 `ict_sss_2021` + `ict_sss_2007_2015`。
- **`edbc013_2026`（非本地兒童入學）自動入庫後從未能被檢索**（S193 spotlight 修復時未涵蓋此源）。經實測其對「非本地兒童入學」cosine 0.619 ≥ 門檻 0.60 後加入 spotlight。
- **display-sync 一直改寫歷史記錄。** `CHANGELOG.md` 與 `dev/CODEBASE_CONTEXT.md` 原本列入 chunk 數的全檔字串取代目標，導致每次入庫都靜默改寫過往條目：本次發現 S186 條目寫成「15,656 → 15,901（淨 +182）」（算術不成立），另有 5 條 AI 維護日誌記載了發生於該 session 之後的總數。已修正受影響條目，並將兩檔從 `execute_ingest.py` 的 display-sync 目標移除（歷史檔只應追加新條目，不應反映當前值）。

### Changed
- `backend/src/api/searchChannelB.ts`：新 **`cgss` route**（SOURCE_SETS + TOPIC_KEYWORDS 置於 value_education 之後、curriculum 之前 + QUERY_EXPANSIONS）；`digital_education` +`iit_ai_framework_2026`；`curriculum` +2 ICT 來源；`SUPERSEDED_IDS` +`ict_sss_2007_2015`（2021 版真正入庫後首次可套用 S183 supersede 規則）；`SPOTLIGHT_SOURCE_IDS` +`iit_ai_framework_2026` +`edbc013_2026`。
- `dev/source/source_registry.json`：+2 entries、`ict_sss_2021` url 更正 + `freshness_metadata` 清空待重新 baseline、`ict_sss_2007_2015.superseded_by` 設定。
- Display-sync 7 檔（`knowledge.json` `_meta.stats.chunks` / `role_facts.json` / `dev/knowledge/role_facts.json` / `K1_API_SPEC.md` / `app.html` ×4 / `index.html` ×3 / `README.md` ×4）＋ `update_log.json` 3 條。

### Added（工具，roadmap R1 + 新監察）
- **`dev/source/eval_retrieval.py` + `dev/source/eval_queries.json`** —— Channel B 檢索 eval harness（roadmap R1）。25 條固定短 query 對 live endpoint 跑、記錄每條的 ranked source_ids、可 diff 兩次跑並區分「意圖改善」與「靜默回歸」。內建兩條規則：同文件兩次入庫（g24／sag_2025_11 文字相同、cosine 同分）的次序互換不算回歸；429／逾時記為 error 而非「零結果」。自測 24 項全綠。
- **`dev/source/check_source_titles.py`** —— 封面標題核對監察。對每個 PDF 來源抽封面文字，與 registry 標題做確定性 CJK bigram 比對，揪出「指錯文件」這類既有監察結構上看不到的問題（freshness 只問「上游有無改」、served-url 只問「連結是否 200」，兩者對指錯文件都是綠燈）。自測 24 項全綠（含針對本次 bug 的回歸測試）。

### QC
- **內容保全機械可證**：`cgss_sss_2021` 重入庫前，比對其 chunk hash set 與 live 掛錯 id 的 81 條 —— 81/81 完全相同、雙向差集 0，故「只改標籤、內容零改動」非口頭保證。
- **入庫前後 eval baseline**：入庫前 PASS=12／FAIL=3／RECORD_ONLY=10／errors=0；3 條 FAIL 正是本次要修的 3 項。
- 逐源 count 核實：`cgss_sss_2021`=81、`ict_sss_2021`=116、`iit_ai_framework_2026`=18、DELETE 後 post-count=0；live 總數 **16,035** 由 Supabase `count=exact` 直查（不靠計算 delta，S190 教訓）。
- `tsc --noEmit` exit 0；`py_compile` 全綠。

---

## [內容新增] — 2026-06-28 — 2026年6月 EDB 通告／通函 14 份批次入庫（S186）

> 平台版本維持 **v3.2.2**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines.json 2.6.1 公開 158 不變）；`_meta.stats.chunks` **15,656 → 15,838**（淨 +182 vault_extract chunks）；`source_registry.json` 228 → **242**（＋14 new sources）。來源：第 4 監察「new-circular watcher」(S185 建) 每日 HK 19:30 捕捉 → 人手 verbatim 入庫閘。

### Added（14 份 2026/6 通告／通函，182 chunks，全 text-layer page-resolvable）
- **EDBCM080/2026** 2027/28學年幼稚園幼兒班收生安排（14，`edbcm080_2026`，topic=student → kg_admission route）
- **EDBCM060/2026** 幼稚園提交2025/26經審核周年帳目（68，`edbcm060_2026`，finance → kg_admin route；含表格附錄 42 頁）
- **EDBCM088/2026** 英文／普通話科教師語文能力要求（5，`edbcm088_2026`，hr → hr_admin route）
- **EDBCM081/2026** 2026/27 低收入家庭小學生免費午膳（7，`edbcm081_2026`，finance → student_support route）
- **EDBC010/2026** 中小學數學課程微調：加強數學建模（5，`edbc010_2026`，curriculum route）
- **EDBC012/2026** 校舍消防裝置或設備（3，`edbc012_2026`，safety route）
- **EDBC009/2026** 家校合作活動整合津貼（9，`edbc009_2026`，activity route）
- **EDBCM070/2026** 2026/27 家庭與學校合作活動計劃資助申請（10，`edbcm070_2026`，activity route）
- **EDBCM089/2026** 高中多元學習津貼：其他語言及其他課程（15，`edbcm089_2026`，finance route）
- **EDBCM073/2026** QEF 電子學習撥款計劃：流動電腦裝置及上網支援（12，`edbcm073_2026`，digital_education route）
- **EDBC011/2026** 《中小學數字教育發展藍圖》正式通告（5，`edbc011_2026`，digital_education route）
- **EDBCM066/2026** 準英語教師獎學金 2026/27（14，`edbcm066_2026`，hr_admin route）
- **EDBCM107/2026** 學校落實 AI 教育規劃培訓及 AI 教師培訓 第一期（10，`edbcm107_2026`，digital_education route）
- **EDBCM095/2026** 資優教育學校網絡計劃2026/27 及教師專業培訓（5，`edbcm095_2026`，gifted route）

### Changed
- `backend/src/api/searchChannelB.ts`：9 個 route 擴 SOURCE_SETS（kg_admission/kg_admin/hr_admin/student_support/curriculum/finance/safety/activity/digital_education/gifted）；TOPIC_KEYWORDS 加 語文能力要求／語文基準／基準試／準英語教師／英語教師獎學金（hr_admin）、免費午膳／在校午膳（student_support）、數學建模（curriculum）、電子學習撥款／流動電腦裝置／上網支援（digital_education）、家校合作／家庭與學校合作／家教會（activity）、多元學習津貼（finance）；**`activity` route 提升至 `finance` 之上**（first-match precedence，防「家校合作活動整合津貼」被 finance「津貼」keyword 偷，同 S183/S184 promote pattern）。
- `source_registry.json`：+14 source entries（228 → 242，全含 freshness_metadata）。
- Display-sync 7 處 chunks 數 15,656 → 15,838：`role_facts.json` / `dev/knowledge/role_facts.json` / `knowledge.json`（`_meta.stats.chunks`）/ `index.html`（×3）/ `app.html`（×4）/ `K1_API_SPEC.md` / `README.md`（×4）/ `CHANGELOG.md`（本 entry）+ `update_log.json`（首頁更新日誌）。

### QC
- **Verbatim 抽取**：14 份 PyMuPDF `get_text()` 直抽、canonical chunker（600/60 page-carry）→ 182 chunks 全 page-resolvable=True，char 中位數 ~590；NUL=0；無改寫。
- **Dupe check**：入庫前 grep registry（URL filename + 中文 title keyword）→ 全部 0 hit（除既有 DEBP corpus / 消防指引係不同文件）；INSPECT before=0 確認逐條非重複。
- **Routing smoke**：`detectQueryCategory` 21/21 PASS（14 新源代表 query 各路由正確 + 7 regression：finance/hr_admin/activity/school_governance/value_education/sen/kg_admin 行為不變）。
- **tsc**：exit 0。
- **Live verify**：Render redeploy 後逐源短 query 核（見 SESSION_LOG S186）。

---

## [內容新增] — 2026-06-26 — 教育局通告第8/2026號「學校效率津貼」入庫（S184）

> 平台版本維持 **v3.2.2**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines.json 2.6.1 公開 158 不變）；`_meta.stats.chunks` **15,644 → 15,656**（淨 +12 vault_extract chunks）；`source_registry.json` 227 → **228**（＋1 new source）。

### Added
- **教育局通告第 8/2026 號「學校效率津貼」**（School Efficiency Grant）：12 chunks，`source_id=edbc008_2026`，topic=it，page-resolvable，原文 10 頁 text-layer verbatim 抽取。教育局由 **2026/27 學年起設立**，支持學校加快推動教育數字化轉型（配合 2026/6 公布之《中小學數字教育發展藍圖》DEBP），提升學校效率、優化學校行政和學生學習體驗。津貼承接現行「整合代課教師津貼」(TRG) 之財務彈性精神，鼓勵學校透過人工智能協助處理行政工作、推動智慧校園建設、實踐減負增能。

### Changed
- `backend/src/api/searchChannelB.ts`：`digital_education` route 擴充 — SOURCE_SETS 加 `edbc008_2026`；TOPIC_KEYWORDS 加 `學校效率津貼|效率津貼|學校效率|教育數字化|數字化轉型`（維持在 `finance` 之上，first-match precedence 防「效率津貼」被 finance「津貼」keyword 偷）；QUERY_EXPANSIONS 加 學校效率津貼／教育數字化轉型／提升學校效率／智慧校園／行政效率／整合代課教師津貼。
- `source_registry.json`：+1 source entry `edbc008_2026`（topic=it，related_source_ids = debp_blueprint + edbcm_221_2025_smart_teaching）。
- Display-sync 7 處 chunks 數 15,644 → 15,656：`role_facts.json` / `dev/knowledge/role_facts.json` / `knowledge.json` (`_meta.stats.chunks`) / `index.html` (×3) / `app.html` (×4) / `K1_API_SPEC.md` / `README.md` (×4) / `CHANGELOG.md` (本 entry)。
- **單一真源整理（index.html）**：(1) 版本號自打交 — hero eyebrow `v3.0·2026` + footer `v2.3` 同頁兩個版本號 → 收斂為頁面單一 footer `v3.2.2`（對齊 app.html `PLATFORM_VERSION`）、eyebrow 移走版本號；(2) 四個平台名並存 — 移除第 4 個 stray「資助學校管治平台」（eyebrow 改定位描述「香港資助學校 · EDB 政策知識庫 · 2026」），收斂成「香港學校政策搜尋平台」(產品正名) + 「PolicyChecker / 政策核對」(品牌標記) 一對。
- **統一所有對外標題為「香港學校政策搜尋平台」**：`index.html` title（原「EDB 學校政策搜尋平台」）+ `app.html` title（原「搜尋工作室」）+ 兩頁 `og:title` / `twitter:title` 全部統一；兩頁新增 `apple-mobile-web-app-title` + `application-name` + `apple-mobile-web-app-capable`（加到主畫面 home-screen 標籤）。涵蓋 browser 分頁標題 / 社交分享 / 加到主畫面 PWA / WhatsApp 分享（後者 S183 已為此名）四個面。`og:site_name` 維持「PolicyChecker · 政策核對」品牌對。

### QC
- **Verbatim 抽取**：PyMuPDF `get_text()` 直抽 10 頁、canonical chunker（600/60 page-carry）→ 12 chunks 全 page-resolvable=True，char(min/med/max)=469/588/602。無改寫、無 paraphrase。
- **Dupe check**：入庫前 grep registry（學校效率津貼／效率津貼／8/2026／26008／efficiency）+ repo-wide → 0 hit，確認非重複（吸取 S183 duplicate ingest 教訓）。
- **Live INSERT**：INSPECT before `edbc008_2026`=0 → INSERT 12/12 → after=12；live total **15,656**（15,644 + 12 ✓ exact）。
- **Backend typecheck**：`tsc --noEmit` exit 0。
- **Routing smoke**：本機 Node first-match precedence 測試 —「學校效率津貼」「效率津貼是什麼」「學校效率津貼幾錢」全 → `digital_education`（不再被 finance 偷）；「數字教育發展藍圖」「智啟學教撥款」regression → digital_education 不變；「法團校董會選舉」→ school_governance 不變。
- **Render 端 live retrieve verify**：push 後 redeploy 完成做。

### Notes
- 凍結合約零接觸（`_meta.version` 2.3.0 / facts 455 / guidelines.json 2.6.1 公開 158 / PLATFORM_VERSION 3.2.2 全不變）。
- 入/改 vault_extract chunks 後 Render auto-redeploy（push origin/main 觸發）；vault_extract chunks 即時 routable。

---

## [內容新增＋維護] — 2026-06-25 — 《價值觀教育課程架構》2026 正式版 + EDBC 3/2026 通告 + EDBCM 221/2025「『智』啟學教」AI 撥款計劃入庫（S183）

> 平台版本維持 **v3.2.2**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines.json 2.6.1 公開 158 不變）；`_meta.stats.chunks` **15,536 → 15,644**（淨 +108 vault_extract chunks，VE_CF_2026 93 + EDBCM 221/2025 15）；`source_registry.json` 225 → **227**（＋2 effective new sources）。Leonard 揀 Option A scope（主框架 only + 配套通告）+ 中途追加 EDBCM 221/2025 piggyback。**Live retrieve verify 揭發 prior session 已 ingest `edbc003_2026`（同份 PDF、6 chunks），new `edbc_3_2026_values_edu` 5 chunks duplicate → hard-delete + remove registry/vault；保留 prior entry。同時揭發 surface fail（VE_CF_2026 主框架 chunks 不在 top-8、EDBCM 221/2025 被 finance 偷 query）→ backend `searchChannelB.ts` 加 dedicated `value_education` route + 擴 `digital_education` route + 提兩者到 finance 之上（first-match 12/12 PASS 含 regression）。**

### Added
- **《價值觀教育課程架構》(2026)** 正式版主框架（EDB 4 key tasks 之一）：93 chunks，`source_id=values_edu_framework_2026`，topic=curriculum；課程發展議會 2026/3 接納、2026/27 學年起在中小學正式推行；常委會以 2021 試行版為藍本、經各持份者意見及學校實踐經驗編訂。5 章節（價值觀教育的課程發展理念 / 架構的特色 / 課程內容 / 課程規劃與實施 / 資源與支援）；12 首要價值觀（堅毅 / 尊重他人 / 責任感 / 國民身份認同 / 承擔精神 / 誠信 / 仁愛 / 守法 / 同理心 / 勤勞 / 孝親 / 團結）；總體方向「立根中華、聯通世界、擁抱未來」。Source 86 substantive pages（PDF 89 pages 中 skip 1-3 cover + 89 blank）→ 53,964 chars verbatim 抽取。
- ~~**教育局通告第 3/2026 號** 配套通告（5 chunks，`source_id=edbc_3_2026_values_edu`，topic=curriculum）~~ — **post-INSERT 發現同份 PDF 已喺 store（prior `edbc003_2026`、6 chunks，registry title 短「教育局通告第3/2026號」未含「價值觀」keyword、初始 grep 漏 catch）→ hard-delete + remove registry + vault dir，保留 prior entry。** Prior `edbc003_2026` 已加入 `value_education` route SOURCE_SETS、retrieve 行為不變。
- **教育局通函第 221/2025 號「『智』啟學教」撥款計劃**（AI 賦能教育撥款，piggyback this batch）：15 chunks，`source_id=edbcm_221_2025_smart_teaching`，topic=it；屬 digital_education route。教育局 2025/1 成立「數字教育策略發展督導委員會」，2025 施政報告 QEF 預留 20 億；本計劃成功申請學校獲一次過 **50 萬元** 撥款，啟動 AI 賦能教育（購置／訂閱／租用 AI 軟件／硬件／平台／資源、資助學生 AI 素養活動）。承諾要求：最少 3 個科目／2 個級別推行 AI 輔助教學、發展 6 個 AI 教學例子、舉辦 3 次公開課／3 次經驗分享會／2 個學生活動。申請截止 **2026/2/28**、發款 2026/6/30、可跨學年用至 2027/28、財政紀錄保留 7 年。

### Changed
- `source_registry.json`：+2 effective new sources entries（VE_CF_2026 + EDBCM 221/2025）；2 條舊版 `values_edu_framework_2021_trial`（2021 試行版） + `edbcm183_2023_values_edu`（2023 豐富試行版通函）加 `superseded_by: values_edu_framework_2026` 標注（retain 入庫、不 hard-delete；retrieve 仍可命中、ranking 自然分高低）。
- `backend/src/api/searchChannelB.ts` **+2 routes**：(1)新 `value_education` route（SOURCE_SETS = VE_CF_2026 + edbc003_2026 prior + 2021_trial + EDBCM 183/2023 + 中學課程指引 6A 共 5 sources；TOPIC_KEYWORDS = `價值觀教育|首要價值觀|價值觀架構|立根中華|聯通世界|擁抱未來|德育|公民教育|品德教育|品德及倫理|生命教育|國民身份認同|愛國主義教育|承擔精神|12.{0,3}首要|十二.{0,3}首要|VE_CF|VECF` + QUERY_EXPANSIONS 含 12 美德 list）；(2)擴 `digital_education` SOURCE_SETS 加 `edbcm_221_2025_smart_teaching` + TOPIC_KEYWORDS 加 `智啟學教|數字素養|數字技能` + QUERY_EXPANSIONS 加智啟學教/AI賦能/50萬。**Routes 提到 finance 之上**（first-match precedence；解決「智啟學教 撥款」「AI 撥款」被 finance 偷 issue）。Routing smoke 12/12 PASS（5 value_education + 3 digital_education + 4 regression: finance/curriculum/gifted/school_governance 行為不變）。
- Display-sync 9 處 chunks 數 15,536 → 15,644：`role_facts.json` / `K1_API_SPEC.md` / `index.html` (×3) / `app.html` (×4) / `knowledge.json` (`_meta.stats.chunks`) / `README.md` (×4) / `dev/CODEBASE_CONTEXT.md` / `dev/knowledge/role_facts.json` / `CHANGELOG.md` (本 entry)。

### QC
- **Adversarial verbatim subagent review** GO-as-is：programmatic per-page parity check **103/103 pages 0 divergence**（VE_CF 85 + EDBC 5 + EDBCM 13）；12 首要價值觀完整 + 順序對；5 章節 titles 對；中華經典引文（范仲淹「先天下之憂而憂」/ 杜甫 / 屈原 / 諸葛亮 / 岳飛 / 文天祥 等 8 條 quotes）byte-exact；總體方向「立根中華、聯通世界、擁抱未來」全 instances 對。
- **Self-test chunker**：3 sources 全 page-resolvable=True；char med 574-594（in spec）。
- **Live INSPECT before**：3 sources 全 0/* （no collision per source_id 角度；但 prior `edbc003_2026` 同 URL duplicate post-INSERT 揭發）→ INSERT 93+5+15 = 113 rows → INSPECT after total 15,649 → **post-fix hard-delete 5 dup chunks → 最終 15,644 ✓**。INSPECT after 三 sources per-count 全 match expected（VE_CF_2026=93 / EDBCM 221=15）；勝出 prior `edbc003_2026`=6 untouched。
- **Render redeploy** 自動觸發（push 後）— vault_extract chunks 即時 routable，配 +2 backend routes 補 surface gap。
- **Routing smoke 12/12 PASS**：本機 Node 跑 detectQueryCategory（純函數 19 routes）對 5 value_education + 3 digital_education queries 全命中正確 route；4 regression (finance / curriculum / gifted / school_governance) 行為不變。Render 端 live retrieve verify 跟 push 後做。

### Notes
- 凍結合約零接觸（`_meta.version` 2.3.0 / facts 455 / guidelines.json 2.6.1 公開 158 / PLATFORM_VERSION 3.2.2 全不變）。
- **路由匹配（post-fix）**：value education 走新 dedicated `value_education` route；EDBCM 221/2025 走擴展嘅 `digital_education` route；兩者均提到 finance 之上 first-match precedence。
- 2021 試行版 + 2023 EDBC 183 retain 入庫策略：學校過渡期仍可能引用試行版內容；retrieve 命中後由 cosine 相似度自然排序，2026 正式版內容相關時 ranking 自然在前。
- **Duplicate ingest 預防教訓**：初始 grep registry 用「VE_CF / 價值觀 / value_education」漏 catch prior `edbc003_2026`（registry title 短「教育局通告第3/2026號」未含「價值觀」keyword）。Future ingest 之前應額外 grep URL 同 title 短 form（例如 `EDBC*_<YYYY>` / `EDBC<NN>_<YYYY>` 變體）。本 session post-INSPECT 發現 + hard-delete 修復、無漏網之魚。

---

## [v3.2.2] — 2026-06-25 — 政策搜尋「📤 分享至 WhatsApp」按鈕（綜合答案 + 來源簡引 → wa.me deep link）

> 平台版本 v3.2.1 → **v3.2.2**（`PLATFORM_VERSION` bump）。純前端 frontend-only、零 backend / retrieval / synthesis 邏輯改動。凍結合約 `_meta.version` 2.3.0 / facts 455 / guidelines 158 / Supabase **15,536** 全零接觸。

### Added
- **政策搜尋「📤 分享至 WhatsApp」按鈕**（desktop QAPanel 同 mobile shell 同位、出現喺「整理答案」 synthesis card 底；synthesis-gated，無綜合答案不出按鈕）：點擊開 `https://wa.me/?text=<URL-encoded>` 帶住預填訊息（mobile 開 WhatsApp app 揀 contact share / desktop 開 WhatsApp Web）。
- 訊息格式（per Leonard「非常簡潔」要求）：`【EDB K1 知識平台 · 政策搜尋】 ／ 問：<query> ／ <綜合答案 ~250 字> ／ 來源：《SAG》 p.80 · 《採購指引》 p.12 · 《財務管理指引》 p.45 ／ 🔗 https://policychecker.wongfu.net/app.html`。
- 來源行 compact：source_id dedup + score-sort top-5 + 每源最多 3 個 page；wa.me URL 實測 ~965 字符（WhatsApp 4096 字限有大量 headroom）。

### Changed
- `app.html`: `PLATFORM_VERSION` 3.2.1 → 3.2.2（header / footer badge 顯示 v3.2.2）；`runChannelB` / `runCombined` mapping 加 `source_id` 字段（為 share text builder 用 SOURCE_LABELS 中文短名；不影響 UI display，SourcesAccordion 仍用 raw `sourceRef.title`）。
- `mobile.js`: 新 `buildShareText` + `shareToWhatsApp` helpers；`renderResults` synthesis card 加 share button row（#25D366 WhatsApp 綠 99px pill）+ click handler wire-up。

### QC
- 7/8 scenarios PASS：buildShareText 邏輯（mock 5 chunks 3 同源 → `《專業操守指引》 p.9,12,14` 正確 dedup + 排序）／desktop button render (#25D366, 8px radius, 13px/600)／mobile button render (#25D366, 99px pill)／synthesis-gated visibility／wa.me URL 長度／PLATFORM_VERSION 3.2.2 顯示／mobile-shell-active body class @ 375×812／Node syntax check on mobile.js。
- 1 DEFERRED：localhost CORS 阻 live backend fetch → live verify 跟 push 後 prod policychecker.wongfu.net 做。

### Notes
- Frontend-only：backend / Supabase / Render / 凍結合約 / data contract 全零接觸；Render 無需 restart；Pages auto-redeploy（push origin/main 觸發）。
- 留下次：Feature 2a 追問 multi-turn conversation + Feature 2b 文件 scoped Q&A（per Leonard 揀 sequence A = WhatsApp 先 ship、追問+scoped 之後分批做、共享 conversation UI）。

---

## [內容新增＋維護] — 2026-06-25 — Discovery 8 角度 agents team 大入庫：122 條 footnote curated overlay（教師註冊／學校註冊+DSS／NCS／傳染病停課／學費減免／NET／校舍安全/EMSD／SAG 附錄）

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,414 → 15,536**（＋122 curated chunks）；`footnote_curated` 84 → **206**（route-independent overlay）。S181 用 agent team workflow（PLAN→9 並行 research subagent→2 並行 adversarial reviewer→QC 合成→Leonard GO gate→ingest）。

### Added
- **discovery 餘下 8 角度 verbatim footnote 入庫**（Channel B Supabase，＋122 chunks，`content_type=footnote_curated`，route-independent overlay 走 `searchFootnotes` exact-cosine 路徑，可逆）。Phase 1 = 9 個並行 general-purpose subagent 各 research 一條 angle、verbatim extract 自 EDB/CHP/EMSD/SFAA/WFSFAA 等官方 source；Phase 2 = 2 個並行 adversarial reviewer 做 verbatim spot-check audit + coverage/routing audit；Phase 3 = QC 合成；GO Gate Leonard 揀 Option B（R1+R2 footnote sweep）。8 條 angle 入庫分布：
  - **教師註冊制度（13）**：Cap.279 §42/§46/§47/§48/§50/§52/§61 — 註冊 / 拒絕 / 撤銷 / 准用教員 gating / 校屬性 / 21 日上訴；TPC 2022 四級 sanction ladder + 14 日代陳述；准用教員最低資歷 + trained priority + BL/NST；Code of Aid 對 unqualified teacher 條文。
  - **學校註冊 + DSS（10）**：Cap.279 §10/§11/§13/§14 — 註冊 / 申請 / 決定 / 拒絕；DSS 2⅓ 單位資助 cap + 10% / 50¢ 學費減免規則 + 五年 Comprehensive Review；EDBC 10/2012 baseline + 半年學費收入 reserve cap + IMC/SMC 透明度 + 過剩條件 + 直通車 50%。
  - **NCS 行政資助（18）**：**EDBC 4/2026** 新 Composite Support Grant（baseline $230k/$710k + additional $5k/student + enrichment $10k/SEN cap 50）；EDBC 8/2020 兩級小校資助 + 五級資助表 + 全 Annex 准/不准使用 + 30 Nov 計劃 + 31 Jul 估算；EDBC 9/2019 NCS-SEN 三級 $100k/$200k/$300k；EDBCM 79/2025 SBP $26,360/班；KG 五級表 2019/20 + 特殊學校 sub-matrix。
  - **傳染病預防 / 停課準則（15）**：CHP 2025 Nov 修訂《學校 / 幼稚園 / CCC 預防傳染病指引》— 校級停課指標（ILI ≥20% / ≥2 ICU / 健兒死亡 → 7 日停課）；爆發定義（3+ 同班 RTI / 2+ HFMD）；CENO 通報電話／傳真／email；表格 routing（SDS / Joint Office / SWD CCCAI）；漂水稀釋 1:4/1:49/1:99；附錄 9 病假復課時限；RTI 退燒 2 日；床距 1 米；SCVPD 停課 rationale；CHP 2025-10-22 致校信。
  - **學費減免 + 書簿津貼（17）**：SFAA 居港證明 + AFI 公式 + 中小 2024/25 thresholds + KG 3 級 AFI + 全日制社會需要評估；KCFR 15 Aug 限期；TA 31 Oct；EC 學校角色；KG 撥付流程；過繳追回；2 年文件保留；2024/25 TA 金額 + SIA grant；EDBC 10/2012 IMC/SMC + reserve excess + 3 年豁免 + 50% 直通車。
  - **NET 計劃（18）**：**EDBC 8/2025** 學校二選一（保留 NET post 或收 NET Grant，HK$900k 小 / $1M 中）；2026/27 point-to-note ≥1 全職 NET + 30% 盈餘上限 + School Plan/Report；新入職 NET 資歷上調（學位 + PGDE/TEFL + IELTS 7.5 / Speaking 7.5）；兩級 gratuity 10%/15%；APSM/CM/GM 薪級；Special Allowance $16,859/月；行李津貼 4 級；醫療津貼 $1,400/$5,400；機票 5 人；海外居所 gate；申請時限；IMC/SMC oversight；legacy 15% + 留任獎勵。
  - **校舍法定安全 / EMSD 升降機（13）**：**EDBC 12/2026** 校舍消防裝置（Cap.279A §39 + Cap.95B §8 + FS251 + 12 月年檢 + 24 小時關閉通報）；EDBC 14/2024 第一責任人 + 維修閾值 $3000/$8000→$6000/$10000；EMSD 升降機 RP 職責矩陣（Cap.618 §12/13）+ 年檢頻率 + 用途許可顯示 + 24 小時嚴重事故通報 + 罰則表；EDBC 22/2024 學生安全清單 30 Nov 限期（拆 §2 framing + §5 30 Nov 兩個 entry）；Audit Report Ch.6 owner duty + 14 日 FS251。
  - **SAG（學校行政手冊）附錄深抽 14**：附 2 宿營 3 日內通報；附 3 急救箱 16 項；附 3 罰款／費用表（學生證 $50 / 圖書 +20%）；附 3 非標準費 7 條件；附 6 SCRC 承辦商；附 9 病假 28→48→168 + 產假 14/40/4；附 10 假期批核權力矩陣；附 11 利益衝突 10 例；附 12 教師失德程序；附 12 staff 紀錄保留；附 12 現金 $300m/$10k；附 12 BBQ/火鍋安全；附 12 校長委任文件。
- **新源 26 條登記**（`source_registry.json` 待 fold-in；canonical 化：Cap.279 → `cap279_education_ordinance`、EDBC 10/2012 → `edbc_10_2012_fee_remission`，避免 angle-specific 變體）。

### Changed
- 知識片段顯示數 **15,414 → 15,536**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

### QC / Process
- **agent team workflow**：feasibility (9 research subagent 並行) + audit (2 reviewer 並行 verbatim spot-check + coverage routing) + monitor (我同步 synthesize)。**Reviewer A verbatim sample**：22/26 PASS + 4 fix-then-pass（無 hallucination，全部 stitching/label 小修），4 fixes 已 apply（CHP 通報表還原序、漂水 §3.4.1 label fix、CHP 信加 [...] ellipsis、EDBC 22/2024 split §2/§5）。**Reviewer B coverage**：113/127 novel (89%)、3 routing 注意（缺 TOPIC_KEYWORDS / 1 invalid route_key / 3 source_id 碰撞），全部已 canonicalize；URL health 11/11 spot-check OK。
- **Self-test**：embed 122 條 candidates + query 122 條 representative，cosine ≥0.45 LEAD = **122/122 (100%)**（首跑 121/122 + re-tune `sag_apx_leave_approval_matrix` 0.401→0.750 一次過搞掂）。
- **Live INSERT**：INSPECT before footnote_curated=84/15,414 → batch INSERT 122 rows → INSPECT after footnote_curated=206/15,536，無 collision，無 missing。

### Monitoring / Notes
- **footnote_curated 走 exact-cosine overlay 路徑**（S179 ship 嘅 `wikiRepository.searchFootnotes`）— 無需 backend route patch，新 122 chunk 即時可 retrieve。
- **full_chunks_routed 暫緩**（reviewer B 估計 ~60 full chunk + 4 個新 backend route：teacher_registration / ncs_support / net_scheme / safety route 加 EMSD/Cap.618 keywords）— 列下次 follow-up，需要 backend code change + Render redeploy + 多 round routing test。
- **Render redeploy** 自動觸發（push 後）— footnote in-memory cache invalidation；handoff ⚠️ 條 rule 依然 apply。
- **Backlog**：source_registry.json 新增 26 源嘅 metadata fold-in（minimal title/url 已足，detailed type/version_label 待後續逐源核）。

---

## [內容新增＋維護] — 2026-06-24 — 學校行政手冊（SAG）版本核對：2025-11 → 2026-05，§3.7.3 新增段 curated 入庫

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,413 → 15,414**（＋1 curated chunk）。

### Added
- **《學校行政手冊》§3.7.3「與性有關的問題」——2026 年 5 月版新增段入庫**（Channel B Supabase，＋1 chunk，`content_type=footnote_curated`，route-independent overlay，可逆）：捕捉 SAG 2026-05 版唯一實質改動——處理「懷疑涉及性侵犯」個案嘅程序要求：學校須遵照社會福利署《保護兒童免受虐待–多專業合作程序指引》，諮詢社會福利署保護家庭及兒童服務課或香港警務處虐兒案件調查組，以採取合適的處理程序；如情況顯示個案可能涉及刑事罪行，學校應向警方舉報。verbatim 核實（markup＋clean 兩版 byte-identical、display page 80）；self-test cosine 0.758 lead；id `footnote_fn_sag_sexual_abuse_referral`（可逆）。

### Changed
- **`source_registry.json` 版本標籤更新**：`sag_2025_11`（`version_label` `2025-11`→`2026-05`）＋ `g24`（`2025`→`2026-05`），title 同步「2025年11月版」→「2026年5月版」、`last_checked_at`→2026-06-24。閉返 freshness 完整性（registry 版本標籤此前 stale）。
- 知識片段顯示數 **15,413 → 15,414**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。
- **公開指引庫 SAG 版本標籤同步**：`guidelines.json`（finance/`sag_2025_11` + general/`g24` 兩 entry：title「2025年11月版」→「2026年5月版」、year 2025→2026、`_meta` 2.6.0→**2.6.1**、count **158 不變**）+ `app.html` GUIDELINES_REGISTRY 兩 entry + 平台介紹示例來源標籤。完成公開顯示面版本核對（SAG dedup 調查時揭發 `g24` 雙重身份〔Channel-B 來源 + 公開指引 entry〕，registry bump 原漏咗公開顯示面）。

### Monitoring / Notes
- **SAG 雙重 ingest 確認由 soft-dedup 妥善處理（無需 hard-dedup）**：`wikiRepository.ts` 有顯式 alias `g24 → sag_2025_11` + `seen`-Set dedup + 共用 per-source quota bucket → 兩份 ingest 永不喺結果重複、共用配額。backlog「軟 dedup 已 ship 足夠用」經 code + 機制核實屬實；hard-dedup（DELETE 383）唔值 destructive 風險。
- **發現經過**：S179 discovery 旗 SAG 疑有 2026-05 新版 → 本 session live 核實 confirmed（`SAG_C_markup.pdf`／`SAG_C.pdf` Last-Modified 2026-05-20、served 同檔名）。官方更新記錄表（Log_sheet）證自 2025-11 起唯一 delta＝項 73（第 3 章 §3.7.3，中英文版同改）。
- **盲點**：served-URL／freshness 監察測 URL 可達性、唔測內容版本；EDB 同檔名換版（content swap、URL 不變）結構上避過兩個監察（playbook `freshness-monitor-test-served-url` 已記此 failure mode）。
- **Side-finding（已調查、resolved）**：SAG 喺 store 重複 ingest 兩份——`sag_2025_11`（markup 383 全文＋overlay）＋ `g24`（clean 383）；S180 已核實 soft-dedup 妥善處理（見上 Monitoring 首條），無需 hard-dedup。

---

## [內容新增＋維護] — 2026-06-23 — footnote 擴充第三批（14 條）＋ discovery 三快贏新主題（8 條）＋ kg_operation 補標 ＋ TRG 連結修復

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,391 → 15,413**（＋22 curated chunks：14 footnote 擴充 ＋ 8 discovery 三快贏）。

### Added
- **footnote 擴充第三批入庫**（Channel B Supabase，＋14 chunks，`content_type=footnote_curated`，可逆）：補回一批藏喺附件表格／附錄細字、正文唔講嘅 load-bearing 要求——
  - **《學校行政手冊》人事與假期（8 條）**：遴選委員會組成（未成立法團校董會：辦學團體代表 ≤60%＋獨立人士）／受聘前體格檢驗（胸肺 X 光）／超額主任跨屬校調配抵銷（通函 26/2025）／非學位教師改編學位職系（校本政策＋校董會通過＋通告 11/2019，每年 5 月 31 日限期）／**病假**（教師首年 28 天→每年 48 天、累積上限 168 天）／**肺病特別假期**（服務 1–4 年最多 3 個月、4–8 年 6 個月、8 年以上至 12 個月）／**侍產假 5 天＋產假 14 週**（通告 16/2015）／**年假**（非教學 7 天起、上限 14 天）＋緊急私事假（每學年最多 2 天）。
  - **幼稚園／法團校董會／活動（4 條）**：法團校董會免稅須章程含《稅務條例》第 88 條條文／幼稚園租金資助額以九月錄取人數計／幼稚園每班最少一位教師當值／戶外活動建議師生比例（遠足 1:10、宿營 1:30、野外定向 1:8、單車及滑浪風帆 1:5、獨木舟 1:8）。
  - **forms 手尾（2 條，補完 S177 批次）**：CEG 計劃須經 IMC/SMC 通過並於 10 月底前上載，否則**追回**（clawed back）／CFEG 個別家具設備項目**無金額上限**（只要戶口款項足夠；戶口累積盈餘上限仍為該年撥款 5 倍）。
  - 全部 verbatim 核實對官方來源（SAG／IMC／KG／活動指引 vault repaged extract；CEG Ground Rules ＋ CFEG User Guide 即場下載 EN PDF 核）；self-test 14/14 cosine 0.65–0.84 lead、新條目互不混淆（rank-1 14/14）。
- **discovery 三快贏新主題入庫**（Channel B Supabase，＋8 chunks，`content_type=footnote_curated` route-independent overlay，可逆）：discovery 偵察（subagent fan-out + WebSearch 對 `source_registry.json` 核）揭發平台偏重課程、缺日常校政／合規／學生支援，Leonard 揀三個 confirmed-absent 主題即時補——
  - **處理學校投訴（3 條）**：兩階段程序（調查／上訴各建議 2 個月內完成、上訴須 14 天內提出、上訴人員職級較高）／學校投訴覆檢委員會（覆檢條件＋重新調查 2 個月＋高一職級）／校本機制六要素＋向法團校董會報告。源 =《學校處理投訴指引》2023。
  - **校園精神健康（3 條）**：《4Rs 精神健康約章》（通函 60/2024，2024/25 起公營＋直資貫徹）／以學校為本「三層應急機制」（通函 215/2025，中學恆常化＋高小試行；第一層校內團隊／第二層社署校外支援網絡／第三層醫管局精神科）／轉介須家長同意＋校長轉介表格＋校長熱線 2742 4508＋危機即報警／送急症室。
  - **學校與《個人資料（私隱）條例》第 486 章（2 條）**：查閱／改正資料要求須 40 日內回覆（拒絕亦須 40 日書面告知理由、須書面提出）／未成年（18 歲以下）學生資料由有管養權者代查閱、無管養權分居家長可拒。
  - 全部 verbatim grounded 對官方 PDF（投訴指引中文／EDBCM 60·215 中文／PDPO note）；self-test 8/8 cosine 0.70–0.80 lead。route-independent overlay 即時可檢索，無需改後端路由。

### Changed
- **檢查清單 `kg_operation`（幼稚園營運）補標 `school_types`**：388 個項目＋162 條 clause 全標 `['kindergarten']`（全屬幼稚園專用來源 `kg_admin_guide_2026`／`kg_operation_manual_2026`），重生 `checklists_bundle.json`（→ 約 1603 KB）；令文件標註／範本下載對非幼稚園校類唔再顯示幼稚園營運項目。
- 知識片段顯示數 **15,391 → 15,413**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

### Monitoring
- 三條監察各跑一輪：freshness（220 檢查／5 內容變動／0 error，皆 index 頁或已監察 DEBP，detection-only）；discovery（739 候選／225 likely-real，monitor-driven，與 S170 評估一致）；served-URL（210 URL／209 OK／**1 條 404 已修**：`trg_imc_2023` 嘅 TRG_guidelines 連結 en 路徑大階 C 失效 → 經 Leonard 明確授權，repoint 全 3 條 chunk 去 tc 路徑小階 c（`dev/fix_trg_url.py`，re-verify 200）。url-only、可逆）。

---

## [內容修復＋新增] — 2026-06-23 — 政策搜尋 MPF 漏答修復（footnote-lead judge bypass）＋ EDB Tips 細字 2 條入庫

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,389 → 15,391**（＋2 curated footnote chunks）。

### Fixed
- **政策搜尋 MPF 漏答修復**（後端 `searchChannelB.ts`，零資料改動）：查詢「凍結空缺 MPF 僱主供款」「代課教師津貼 凍結空缺 強積金供款」等時，雖然正確嘅 MPF footnote 已檢索為**第一位**（cosine 高達 0.76），S177 加入嘅 anti-confabulation judge（gpt-4.1-nano，從嚴設計）仍過度保守、誤判「否」→ 回覆「暫時未能找到」（即使單獨畀 judge 睇該 footnote 都誤拒，故「加關鍵詞」非正解）。修正：當**最高分結果係 curated footnote 且 cosine ≥ 0.45（lead 線）**時跳過 judge 直接合成——curated footnote 係人手 verbatim 核實嘅精準答案，唔屬 judge 要防嘅「topically-near-but-wrong vault chunk」confabulation 類別；vault chunk 領先時 judge 照常 gate（anti-confabulation 保護不變）。本機 e2e QC：4/4 MPF query 修好、vault-lead 仍正確 decline、「凍結教席上限」仍正確答 10%。

### Added
- **EDB「處理政府給予資助學校資助的提示」細字入庫**（Channel B Supabase，＋2 chunks，`content_type=footnote_curated`，可逆）：補回 S177 forms 批次手尾兩條 load-bearing 規則——（1）學校**出租／分租校舍**所收淨租金收入的 **40%** 須記入政府津貼帳（EDBC 5/2011）；（2）**12 個月內重複採購**同類項目，累積價值口頭報價 ≤$50,000／書面報價 ≤$200,000 才可分別重複，**不得分拆訂單**規避招標（EDBC 4/2013）。verbatim 核實對官方 Tips PDF（pymupdf，文件署 2025 年 5 月）；self-test cosine 0.76／0.61 lead；分離探針確認 #28 唔搶 #26 採購門檻 query。

### Changed
- 知識片段顯示數 **15,389 → 15,391**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

---

## [內容新增] — 2026-06-23 — EDB 津貼申請表格細字入庫（25 條 footnote）

> 平台版本維持 **v3.2.1**（`PLATFORM_VERSION` 不變）。`knowledge.json` `_meta.version` 維持凍結 **2.3.0**（facts 455 / guidelines 158 不變）；`_meta.stats.chunks` **15,364 → 15,389**（＋25 curated footnote chunks）。

### Added
- **EDB 津貼申請表格細字入庫**（Channel B Supabase，＋25 chunks，`content_type=footnote_curated`，可逆）：補回一直未入庫嘅 EDB 津貼／財務申請表「細字」load-bearing 規則（正文唔講、藏喺表格／註腳／certification）。涵蓋——學校發展津貼（CEG：班數階梯／雙課制 25 班／中小兼收用小學費率／不准出補課薪津）、擴大營辦津貼（EOEBG：盈餘 12 個月上限／top-up 50%·25%／應酬餐飲 $200·$450·$600／無薪假法定假／A·B 值）、綜合家具設備津貼（CFEG：盈餘 5 倍／Set-up Fund／單位率）、營辦津貼（OEBG：盈餘 12 個月／Domain 調撥）、空調津貼（AC Grant：特別室封頂 5/12／等值公式／SAC 封頂 2）、整合代課教師津貼補充（凍結空缺 MPF $1,500／不可凍結職位清單）、採購門檻階梯、費率 footnote（寄宿宿費 $440／多元學習 $800〔2026/27 取消〕／MMLC $59,570／全方位 $300,000 下限）。所有數字 **verbatim 核實對官方 PDF**（pymupdf）；self-test 25/25 cosine ≥0.45 lead。
- 由來：凍結教席事件（下方 entry）揭發 EDB「申請表格」整類文件未入庫 → 系統性補 source coverage。候選清單 + 待補（tips #27/#28）見 `dev/FORMS_FOOTNOTE_CANDIDATES.md`。

### Changed
- 知識片段顯示數 **15,364 → 15,389**（首頁／平台介紹／README／K1_API_SPEC `_meta.stats` 同步）。

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
