## 2026-07-27 Session 195 — 清三條死連結：兩條 re-point（逐頁比對作證）、一條 re-ingest（校車安全指引 2026/27 改版）＋ registry↔store drift 整理

- **ID:** Claude_20260727_S195
- **Summary:** Draft root 開工 → §1 startup → 起手探針 4/4 綠（served v3.2.2 / Render warm 455 / HEAD==origin/main `138588a` tree 乾淨、**無新 bot commit** / Supabase count=exact 16,035）→ 我報狀態並建議「① judge 門檻交 Leonard 拍板、②③ registry 衛生我做」→ Leonard「跟你建議」→ **READ 階段兩度發現實況超出我原述、按 §3 停低報告** → Leonard 兩個決定（Supabase 一齊修／g21-g22 只記錄）→ 執行 + 全掃驗證。
- **§3 兩次停低（值得記低的過程）:**
  1. 我原本同 Leonard 講「②③ 唔碰 Supabase 內容，只係修 registry」。查實發現**錯**：`wiki_chunks` 每條 chunk 自己帶一份 url，`g01` 34 條 + `ls_jss_2010` **251 條**服務緊死連結，即係用戶真係撳到 404，唔修 Supabase 等於冇修。停低講清楚 → Leonard 批「registry + Supabase 一齊修」。
  2. 動手時再 grep 發現同一條 URL 散落 **6 處**（registry / `app.html` GUIDELINES_REGISTRY / `guidelines.json` / `data.json` / `dev/checklists/_src/secmeta.json` / Supabase），其中 `guidelines.json` 屬凍結合約檔。無再開多一次會，改為：全部一次過對齊 + **機械核實凍結不變量**（見 QC），並在本 entry 明確記錄。
- **Changed:**
  - `dev/source/source_registry.json`：7 條 entry、23 個欄位。`g01`／`ls_jss_2010` url 重錨 + `freshness_metadata` 清空（舊 etag/hash 屬舊檔）；`g21`／`g22` url_primary 由 landing 改為 store 實際供應的直連 PDF；`g31` 指返真身 PDF + `related_source_ids=[eng_pri_guide_2025]`；`g30` `source_type` pdf→html；`religious_edu_jss` 揾返直連 PDF、標題／`version_label` 按封面更正為 2024 版、status candidate→verified。每條都寫低理由入該條目自己的 `notes`。
  - `app.html`（GUIDELINES_REGISTRY 2 條 url）／`data.json`（2 處）／`dev/checklists/_src/secmeta.json`（1 處）：同兩條 URL 對齊。
  - `guidelines.json`：**用 `dev/build_guidelines.py --write` 重生**（DOC_SYNC row 35 明令 NEVER hand-edit）。先手改再重生對照，證實兩者除 `_meta.updated` 外**逐字相同**，即手改內容正確但改用官方路徑產出。
  - Supabase `wiki_chunks.url`：**285 行**（g01 32＋1＋1／ls_jss_2010 251），按 distinct url 分組 PATCH 以原樣保留 `#page=17`／`#page=5` 錨點。
  - `CHANGELOG.md` 新條目（含 Known issues 段）。GitHub：Issue #4 補修復證據 + 範圍說明；**新開 Issue #5**（g21／g22 引文錯配）。
  - g18 續做新增：`dev/_extract_s195.py`（NEW）／`dev/_s195_delete_stale_g18.py`（NEW，刪除集 hard-code + dry-run 預設）／`dev/vault/g18/extract_g18.txt` 重寫為 2026/27 版／display-sync 7 檔 16,035→16,033／`update_log.json` +1 條。
- **Done:** 3 條 404 全部清走（2 條 re-point、1 條 re-ingest）並 live 驗；5 條 pdf-serve-HTML 更正；餘下發現記錄在案。Supabase 16,035 → **16,033**。
- **根因（②，比 handoff 描述深）：** handoff 把呢兩條寫成「封面掃描副產品」，實情係 **served-URL 監察（第 3 監察）早在 2026-06-29 就準確捉到並開咗 Issue #4，一直開住 4 個星期無人跟進**。監察系統健康，債係流程上冇人 close the loop。兩條的上游成因唔同：`g01` = 上游改名（`…Trad Chi_2024.pdf`→`Guidelines on Procurement Procedures_TC.pdf`）；`ls_jss_2010` = 搬入 `/pshe/archive/Life_and_Society/`。兩者皆用 playbook `external-source-url-churn-rediscovery` 方法 B（re-crawl landing／archive 頁）揾返。
- **QC:**
  - **re-point vs re-ingest 的判斷有機械證據**：重抽兩份新檔逐頁比對已入庫 vault（空白正規化後全字串相等）→ `g01` **30/30 頁相同**、`ls_jss_2010` **183/183 頁相同** → 判定純搬位／改名，只需改 url。呢一步係跟 playbook `freshness-monitor-test-served-url` 的警告（「churn 唔可單純 re-point」）做的**反向舉證**，唔係口頭假設。
  - **blast radius 先行**：Supabase 改動前印出每個 distinct url 的行數同新值俾人眼過（285 行），PATCH 逐組 assert `rows_updated == rows_expected`，之後查舊 url 殘留 = **0**、`count=exact` **16,035 前後同值**。
  - **凍結合約機械核實**：`knowledge.json` + `role_facts.json` sha256 前後相同；`guidelines.json` `_meta` version 2.6.1 / count 158 / 實際條目 158 不變；`PLATFORM_VERSION` 3.2.2 不變。`build_guidelines.py --self-test` PASS（registry 167 / public 158 / dropped 9）。
  - **監察全掃驗證（跑咗兩次）**：修完 g01／ls_jss 後 → 268 URL / 267 OK / **1 broken**（揪出新壞嘅 `g18`）；再修完 g18 後 → **268 URL / 268 checked / 268 OK / 0 broken / 0 errors** —— 成個 store 首次全綠（Issue #4 自 2026-06-29 起一直有 broken）。
  - **live 驗**：Channel B「資助學校採購程序」→ `g01` rank 1/2/3 且 url 已係新值（含 `#page=17` 錨點）；「核心單元 個人成長 青少年壓力 抗逆力 生活與社會」→ `ls_jss_2010` **rank 0 @0.715 p.30**，而 vault p.30 正正係該段內容，即頁碼錨點對得上。
  - **eval before→after 對：N/A 且已說明理由** —— 本次零檢索邏輯改動（無 SOURCE_SETS／TOPIC_KEYWORDS／spotlight／supersede／門檻改動），`url` 欄不參與 embedding 亦不參與排序。唔跑唔係慳工夫，係唔想製造無意義的 tie-flip 噪音。
- **續做（Leonard「go」）：`g18` 校車安全指引 re-ingest —— 改版而非改名，所以行完整入庫流程:**
  - **點解唔可以照 re-point**：`2025_Guidelines_Schools_TC(r).pdf` 已被上游撤下（2026-07-20 那次監察仲係綠、即 7 日內先壞），新出 `2026_Guidelines_Schools_TC.pdf`。逐頁比對新舊：**只有 3/8 頁相同** → 內容改版。照 re-point 會令 2025/26 內文掛住 2026/27 文件 = S194 `ict_sss_2021` 那類引文錯配。
  - **流程**：新寫 `dev/_extract_s195.py`（沿用 `_extract_s194.py` canonical 格式）抽 6 頁 → dry-run chunk **7 條、全部 page-resolvable、char 529/579/596、NUL 0** → `dev/ingest_one_source.py g18` embed + upsert 7 條 → 刪走只屬舊版嘅 6 條。
  - **⚠️ 過程揪出一個會靜默刪錯嘢嘅陷阱（值得記低）**：chunk id = `vault_<sid>_<content_hash>`，兩版有 **3 段文字完全相同 → id 重疊**。原計劃「DELETE 舊 9 條」**會連新版仍然有效嘅 3 條一齊刪走**。正確刪除集係 **`舊 id − 新 id` = 6 條**，已 hard-code 入刪除腳本（唔重新計算，免日後 vault 改咗就漂）。
  - **DELETE 被 auto-mode 權限分類器擋**（破壞性 DB 操作）→ 按指示**停低交俾 Leonard 決定**，佢揀「A：自己行」→ 執行 `dev/_s195_delete_stale_g18.py --apply`（dry-run 預設、逐條刪、每條先驗係咪真係掛住 2025 舊 URL、survivor 唔可以有舊 URL 否則 abort）。事後我 read-only 驗證：**g18 = 7 行、舊 id 殘留 0、總數 16,033**（16,035 ＋7 −6 −... 淨 −2）。
  - **自檢頁碼錨點**（因為啱啱先揪到 g21/g22 錯位，唔可以只信自己）：vault 6 頁 vs PDF 6 頁 **offset 0 全對**，抽 p.5 逐字對照 PDF 第 5 版 → 相同。
  - **live 驗**：搜「校車 學生服務車輛 安全 座位」→ `g18` **rank 0 @0.725 / rank 1 @0.716**、標題已係《學童乘搭校車的安全指引（2026/27）》、URL 已係新版 PDF。
  - **display-sync 7 檔 16,035 → 16,033**（15 處替換，逐檔 assert 命中數）；`update_log.json` **今次有加一條**（真內容更新，唔同前半 session 嘅純連結修復）；registry `g18`：url_primary→直連 PDF、`source_type` html→pdf、`version_label` 2026→2026/27、清 freshness、寫 notes。
  - **刻意唔改**：`app.html` GUIDELINES_REGISTRY／`guidelines.json` 嘅 `g18` 仍指 landing 頁（200，正常）。理由＝指引文件庫係俾人 browse，該頁一次過列齊 6 份對象版本（學校／司機／保姆／營辦商／家長／學生），比直接跳去「供學校」單一 PDF 更有用。呢個係決定，唔係遺漏。
- **本次揪出、未修（2 項＋1 待決）:**
  1. **`g21`／`g22` 引文錯配（Issue #5）** —— 驗 g21/g22 的 vault 對唔對得上服務中的 PDF 時發現：g22 vault 51 頁 vs PDF 52 頁，**offset +1 時 50/51 頁相同**（頁碼系統性錯開一頁）；g21 更嚴重，vault 46 頁 = 小學版（22 頁）+ **中學版 `VAsafety_sec_c.pdf`** 兩份串埋，但 49 條 chunks 全部掛小學版 url，即約一半引文指向一份佢哋唔屬於嘅 22 頁文件、錨點 `#page=23`…`#page=46` 指去檔尾之外。**同 S194 `ict_sss_2021` 同一家族**；五個監察結構上全部睇唔到（URL 回 200、封面同標題對得上、bytes 冇變）。Leonard 指示只記錄。
  2. **校車頁另外 5 份 2026/27 版指引未入庫**（供司機／保姆／營辦商／家長／學生，全部 200）—— 另一受眾，入唔入待 Leonard 決定。
  3. **`religious_edu_jss` 入公開指引庫** —— 直連 PDF 已修好，但 `app.html` 該條仍標 broken-url，被 `build_guidelines.py` 當 dropped 剔走；修好會令公開 guidelines **158 → 159**，屬凍結 count 變動，未做。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S195 block；逐頁比對數字／285 行 blast radius／全掃結果／live rank＝kept as recent trace evidence（本 entry）；每條 registry 改動理由→已寫入 registry 各條目 `notes`（下一個 agent 淨睇 registry 就知）；未修項→Open Priorities（①校車 5 份姊妹指引／③ g21-g22／⑧ religious_edu_jss）+ GitHub Issue #5（跨工具留底）；用戶面→CHANGELOG。
- **Sync:** DOC_SYNC 命中 3 row（guidelines.json/app.html GUIDELINES_REGISTRY ✓ 照 row 用 `--write` 重生／Doc-drift truth-pass ✓／Channel-B vault backfill 部分適用 —— registry + url 對齊，無 SOURCE_SETS 改動故 eval 對 N/A）。**`update_log.json`：前半 session（純連結修復）判定 N/A**（按 S190 定案只記「新源入庫／既有源重大更新」，維護性改動入去只會製造雜訊）；**後半 g18 改版有 append 一條**（真內容更新，命中 row 43）。display-sync 7 檔 16,035→16,033。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實）。Pages 隨 push redeploy（app.html／guidelines.json／data.json 有改）。
- **Risks:** ⚠️ g21／g22 引文錯配仍在生產（Issue #5）。⚠️ `g18` 換版後，任何引用舊 2025/26 版頁碼嘅外部筆記會對唔上（內容已改，屬預期）。⚠️ 本次示範咗一個結構性問題：**同一條來源 URL 在 repo 內有 6 份副本，只有其中一份（Supabase）有監察**；registry／`app.html`／`guidelines.json`／`data.json`／`secmeta.json` 五份無人測。日後若再有 URL churn，其餘五處會靜默 stale（本次係人手 grep 揾返）。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check` → **trigger=False**（line_count=289 / entry_count=4，兩個 trigger 都未到）→ no-op，唔需要 archive（S194 啱啱跑過一次 archive，剩 3 entries）。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，mirror check byte-for-byte PASS。）

<!-- ack:log-entry:end -->

---

## 2026-07-26 Session 194 — 修一個長期指錯文件的來源 + 人工智能初探框架正文入庫 + roadmap R1 eval harness + 封面核對監察 + R5 sibling 審計

- **ID:** Claude_20260726_S194
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → §1 startup → 起手探針 4/4 綠（served v3.2.2 / Render warm 455 / HEAD==origin/main `06d9342` tree 乾淨 / Supabase count=exact 15,901）→ Leonard 一次授權三件事：「R1 同意／R5 做／①＋②」，並釐清 technology-edu index 頁係**監察對象**、`IIT_Summary on AI_TC.pdf` 係**入庫對象**。②在 READ 階段由「核 supersede」升級為真 bug（見下），AskUserQuestion → Leonard 揀「A 完整修」＋「做全庫封面掃描」。
- **Changed:**
  - `dev/source/eval_retrieval.py` + `eval_queries.json` + `eval_runs/` (NEW, roadmap R1)：25 條短 query 對 live endpoint 跑、可 diff 兩次跑。`_tie_aliases` 吸收 g24／sag_2025_11 同分互換（S193 已證未改 code 都會 3:3 交替），429／逾時記 `error` 而非零結果。`--compare` 只對 SET_LOST／VERDICT_REGRESSED／ERROR 判 fail。
  - `dev/source/check_source_titles.py` (NEW)：封面 vs registry 標題核對（確定性 CJK bigram，比對**主題核心**——剝走學段／年份／樣板，因為全庫共用）。
  - `backend/src/api/searchChannelB.ts`：新 `cgss` route（SOURCE_SETS＋TOPIC_KEYWORDS 置 value_education 後、curriculum 前＋QUERY_EXPANSIONS）／`curriculum` +`ict_sss_2021`+`ict_sss_2007_2015`／`digital_education` +`iit_ai_framework_2026`／`SUPERSEDED_IDS` +`ict_sss_2007_2015`／`SPOTLIGHT_SOURCE_IDS` +`iit_ai_framework_2026`+`edbc013_2026`。
  - `dev/source/source_registry.json` 248→**250**；`ict_sss_2021` url 更正 + `freshness_metadata` 清空；`ict_sss_2007_2015.superseded_by` 設定。`dev/vault/`：`extract_ict_sss_2021_repaged.txt` → `cgss_sss_2021/`（git rename，body 零改）＋2 份新 extract。
  - `dev/source/execute_ingest.py`：`CHANGELOG.md`／`dev/CODEBASE_CONTEXT.md` 由 `DISPLAY_SYNC_TARGETS` **移除**（見下方程序缺陷）。`dev/source/FRESHNESS_GUIDE.md` §0 加 Method C ＋新 §1a 入庫時封面核對。`dev/DOC_SYNC_CHECKLIST.md` 加 eval harness row。
  - display-sync 7 檔（15,901→16,035）＋`update_log.json` 3 條＋CHANGELOG／CODEBASE_CONTEXT 新條目。
- **Done:** commits `3f2c9d9`（主體）→ `e0e2f3b`（post-ingest run + 修 ai_intro 斷言）→ 本 closeout commit。Supabase **15,901→16,035**（+215 INSERT／−81 DELETE）。
- **根因（②，比預期嚴重）：** `ict_sss_2021` 標題《資訊及通訊科技 (中四至中六) 2021》但 `url_primary` 指向 `CS_CAG_S4-6_Chi_2021.pdf` —— **`CS` 被當 Computer Science，實為 Citizenship and Social development**，即《公民與社會發展科課程及評估指引》。後果：81 個公社科 chunks 長期掛 ICT 標題供用戶檢索（**prod 實測 baseline 第 19 行：搜「公民與社會發展科」top-1 = `ict_sss_2021`@0.568**），而真 ICT 2021 從未入庫；`curriculum` route 亦**從未包含任何 ICT 源**，故 ICT 查詢結構上無法命中（同 S135 backfill-allowlist coupling 同一坑）。修法：新 `cgss_sss_2021` 承載該 81 chunks → DELETE 掛錯 id 的 81（post-count 0）→ `ict_sss_2021` 改指 EDB 官方檔 + 入真正文 116 chunks。
- **QC:**
  - **內容保全機械可證**：重入庫前比對 `cgss_sss_2021` 與 live 81 條的 chunk hash set → **81/81 相同、雙向差集 0**（非口頭保證）。
  - **入庫前 baseline / 入庫後對照**（兩份 run 已 commit）：PASS **12→14**、errors 0。`ict_guide` FAIL→PASS（rank 0，`ict_sss_2021`@0.624，2015 版受 supersede penalty 降位）／`nonlocal` FAIL→PASS（rank 2）／`cgss` top 由 `ict_sss_2021`@0.568 變 `cgss_sss_2021`@**0.773**／`cgss_topic`（一國兩制 課程）由中文科課程指引變 cgss+ces。2 條 SET_LOST（cgss／cgss_topic 失去通用課程源）＝加 route 的**預期效果**，harness 交人判斷而非自行猜意圖。
  - **spotlight 決策全部先實測**：`iit_ai_framework_2026` 0.628／0.676／0.642、`edbc013_2026` 0.619 → 均 ≥0.60 才加；`ict_sss_2021` 0.610/0.587 → **唔加**，先靠 route 修（post-deploy 證實 rank 0，決定正確）；`cgss_sss_2021` 0.577 → 唔加（baseline 已證全庫搜尋出得到）。**冇降 bar**。
  - 逐源 count：cgss 81／ict 116／iit 18；live 總數 **16,035** 由 `count=exact` 直查（唔用計算 delta，S190 教訓）。tsc exit 0；兩個新工具 `--self-test` 各 24 項全綠（含針對自身兩個校準缺陷的回歸測試）。
  - **封面掃描首跑**：192 個 PDF 源，**冇第二個指錯文件**；17 條 flagged 全部人手核實為良性（TOC 封面／英文封面／純文件編號標題／策展複合標題）；副產品發現 **2 條真 404**（`g01`、`ls_jss_2010`）＋**5 條 registry 寫 pdf 但 URL serve HTML**（`g30`/`g31`/`g21`/`g22`/`religious_edu_jss`）＋1 條 mojibake PDF（`phys_sss_2007_2015`）。
  - **建立監察時揪到自己兩個缺陷（已修＋落回歸測試）**：(a) v1 用「所有標題變體取最大值」→ `title_short`「ICT課程指引2021」去噪剩「ICT2021」，個「2021」撞正公社科封面「由2021/22 學年」→ 假高分 0.500 判 ok，**即 v1 會 miss 佢自己要捉嘅案**；(b) 放寬門檻後英文 `title_en` 對中文封面必然 0.0，一度令 22 個正確文件被誤 flag。修：語言配對 gate ＋剝走年份／學段 ＋短主題名用 containment。校準由 0.468/0.298 改善到 **1.000/0.000**。
  - **R5（sibling repo 審計，全程 read-only，未觸碰對方 repo）**：**推翻 handoff 假設** —— `EDB-AI-Circular-System` 已係 **PRIVATE**（handoff 仍寫「亦 public 待審」），另有新 public repo **`edb-circular-site`**（2026-06-29 建）＝已完成 private 後端／public 成品拆分。核實：public 站只有 png/md/json/html/yml，**零 .py／零 scraper／零 prompt／零 .env**；85 commits 全歷史 secret pattern 掃描**乾淨**；出街 bundle 零 apikey/Bearer 字面、**零 runtime API 呼叫**（純靜態）；Pages workflow 權限最小。private 後端：`.gitignore` 覆蓋 `.env`/`*.key`/`*_api_key*`，**594 commits 全歷史 secret 掃描乾淨**、現無 tracked `.env`；publish workflow 用 allowlist `cp` ＋「後端檔誤入公開 repo 即 FATAL」防呆閘；兩 repo forks 均 0。
- **Pending（需 Leonard 決）:** ① **anti-confab judge 門檻**：新源檢索命中但**整理答案被拒**（`人工智能初探` 0.628、`ICT 課程指引` 0.624 落喺 S183 定的 `vault_extract ≥0.70` bypass 之下）。已用控制組證實屬**既有門檻行為、非本次 regression**（`學校效率津貼` top 係 footnote_curated@0.561 → bypass 0.45 → 答；`價值觀教育` vault_extract@0.753 → 答；`公民與社會發展科`@0.773 → 答且 grounded）。降門檻會重開 S177 confab 區間（0.55–0.65），屬安全／效用取捨，**唔應由我單方面改**。② R5 剩一項只有 Leonard 做得到：確認 `PUBLISH_PAT` 係 fine-grained、只限 `edb-circular-site` contents:write。③ 2 條真 404 ＋ 5 條 pdf-serve-HTML 待處理。
- **Risks:** ⚠️ private 後端 repo **2026-03-09 建、直到 2026-06-29 一直 public**（handoff S185/S187 記錄可證），即約 3.7 個月後端 IP（scraper／prompt／編纂邏輯）曾世界可讀；轉 private 只保未來、唔追回過去（playbook `split-private-backend-public-artifact` 卡早有此警告）。**不過全歷史掃描證實從未 commit 過任何 secret，故無需 rotate 任何 key**，暴露僅限 IP。⚠️ 公開 feed `circulars.json` 頂層公開了 `model: gpt-5-nano` / `temperature: 1`（低敏感，但屬管道細節）。⚠️ spotlight 名單增至 6 源 63 chunks（上限 600）。
- **Log maintenance:** §4a 機制閘 **triggered 並已執行**：`--check` 報 `trigger=True line_trigger=True`（line_count 420 > 400，因本 entry 加入）→ 跑 `--apply --archive-dir dev/archive` → **420 → 187 行、9 → 3 entries、6 條移入 `dev/archive/SESSION_LOG_2026_Q2.md`**（raw 內容保留，冇刪任何 entry）→ 重跑 `--check` 確認 `trigger=False`（line_count=187 / entry_count=3）。`--apply` 當時另報 `latest entry prompt block ok=False`：因為 archive 喺 checkpoint 階段跑，`### Next Session Handoff Prompt (Verbatim)` 要到 full closeout 才寫；該 block 已於本次收工補上（見本 entry 末），handoff↔`START_NEXT_SESSION_PROMPT.txt` mirror check byte-for-byte PASS。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S194 block；hash-set 比對／實測 cosine／eval 前後對照／封面掃描結果／R5 審計細節＝kept as recent trace evidence（本 entry）；入庫時封面核對紀律 + Method C 監察模型→promoted to `dev/source/FRESHNESS_GUIDE.md` §0+§1a（可重用程序知識）；跨 repo durable 教訓→promoted to `dev/PROJECT_DECISIONS.md` Insights；eval harness 同步義務→promoted to DOC_SYNC row；模組事實→CODEBASE_CONTEXT Directory Map + AI log。
- **Sync:** DOC_SYNC 命中 4 row（Channel-B vault backfill／Doc-drift truth-pass／Monitoring-CI change／Option A 管道改動）＋**新增 1 row**（eval harness，原本無 row → 按 anti-pattern guard 先補）。display-sync 7 檔 15,901→16,035 ＋ `update_log.json` 3 條 ＋ CHANGELOG／CODEBASE_CONTEXT 新條目。凍結合約（`_meta` 2.3.0／facts 455／guidelines 158）＋ `PLATFORM_VERSION` 3.2.2 零接觸。Pages 已隨 push redeploy（前端數字有改）。


### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S194, 2026-07-26): 平台 v3.2.2; Supabase 16,035 chunks; source_registry 250;
HEAD==origin/main (744af53 + S194 closeout commit; code commit 3f2c9d9); 凍結合約 _meta 2.3.0 /
facts 455 / guidelines 158; 0 outstanding bug. 自動化 active: 4 源監察 (discover / freshness /
served-url / new-circular) + Option A 自動入庫管道 (OPERATIONAL; 每日 19:30 HK refresh Issue +
@mention-on-new; cron 20:00 HK 兜底). 第 5 監察 (封面核對 check_source_titles.py) 已建但未接 CI.

⚠️ 管道會自行入庫並直接 push main — 開工時本地可能落後 origin/main, tree 乾淨 + 0 本地 commit
時先 git pull --ff-only 同步。

📋 S194 修好: (1) ict_sss_2021 一直指錯文件 — 標題寫《資訊及通訊科技 2021》但 url 指
CS_CAG_S4-6_Chi_2021.pdf, CS = Citizenship and Social development 而非 Computer Science → 81 個
公社科 chunks 長期掛 ICT 標題 (prod 實測 top-1 標題錯配), 真 ICT 2021 從未入庫, 且 curriculum
route 從未有任何 ICT 源。已新立 cgss_sss_2021 承載該 81 chunks (hash set 81/81 相同, 內容逐字
不變) + 入真 ICT 正文 116 chunks + 新 cgss route + SUPERSEDED_IDS。(2) 入庫《人工智能初探》框架
正文 iit_ai_framework_2026 (18 chunks)。(3) display-sync 全檔字串取代一直靜默改寫 CHANGELOG /
CODEBASE_CONTEXT 歷史條目 — 已修正並將兩檔移出 DISPLAY_SYNC_TARGETS (歷史檔只追加, 唔反映當前值)。
⚠️ 動 backend 檢索前必讀 dev/SESSION_LOG.md S194 QC 段 + S193 QC 段 (門檻實證 + tie-flip 陷阱)。

🛠 新工具 (動檢索前後都應該用):
  python3 dev/source/eval_retrieval.py --self-test
  python3 dev/source/eval_retrieval.py --run --out after.json
  python3 dev/source/eval_retrieval.py --compare dev/source/eval_runs/2026-07-26_s194_post_ingest.json after.json
  任何檢索改動 (SOURCE_SETS / TOPIC_KEYWORDS / spotlight / supersede / 門檻) 都要有一對
  before→after run 作證據 (DOC_SYNC 已登記)。入新源前跟 FRESHNESS_GUIDE §1a 核封面標題。

🔜 NEXT (優先序):
  ① 【需 Leonard 拍板, 唯一未解項】anti-confab judge 門檻: 新入 vault_extract 源檢索命中但整理
     答案被拒 (人工智能初探 0.628 / 資訊及通訊科技 課程指引 0.624, 低於 S183 的 vault_extract
     ≥0.70 bypass)。已用控制組證實屬既有門檻行為、非 S194 regression。選項 (a) 唔改, 用戶仍見
     正確來源+頁碼 (b) 降至 ~0.60 — 會重開 S177 confab 區間 0.55-0.65, 必須先做 20+ 條敵意
     probe (c) 針對裸名詞短 query 改良 judge prompt (另開 PLAN)。唔好未做敵意測試就降門檻。
  ② 2 條真 404: g01 / ls_jss_2010 (封面掃描副產品, 走 §D.12 landing-page re-discovery)。
  ③ 5 條 registry 寫 source_type=pdf 但 URL serve HTML: g30 / g31 / g21 / g22 / religious_edu_jss。
  ④ 只有 Leonard 做得到: 確認 PUBLISH_PAT 係 fine-grained、只限 edb-circular-site contents:write。
  ⑤ 把封面核對接入 CI (建議月跑, 192 源要下載)。
  ⑥ g29 同 kgecg_2017 係同一份文件登記兩次 (同 g24/sag_2025_11 同類, 會造成固有 tie)。
  ⑦ spotlight 現 6 源 63 chunks (上限 600), 確認能經 ANN 出頭後可 prune; edbcm073_2026 仍唔出
     (0.458 低於 bar, 設計邊界非 bug)。
  其他 backlog: roadmap R1-R8 (dev/SYSTEM_ANALYSIS_AND_ROADMAP.md §4/§5/§7; R1 已落地);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A)。

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft
HEAD==origin/main〔落後就 ff-pull〕+ Supabase count=exact), 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

---

## 2026-07-26 Session 193 — 修「入庫但搵唔到」根因（spotlight overlay）+ executor 可見度閘 + technology-edu 監察核實

- **ID:** Claude_20260726_1219
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 跟 §1 startup → 起手探針 4 條：served app.html v3.2.2 + 標題 200 ✅／Render `/health` warm 455 ✅／**Draft HEAD 落後 origin/main 4 個 commit**（= Option A 管道自 S192 起無人手自動入庫 4 條通告，ff-pull 同步）✅／Supabase 直連 count=exact **15,901** ✅（registry 248）。逐條 live 探測 4 條自動入庫源，揪出 **2 條連自己標題都檢索唔到** → Leonard 批「1＋2＋再加 Monitor technology-edu 課程文件頁」→ 修根因 + 補機制 + 核實監察，全部 live 驗證。
- **Changed:**
  - `backend/src/lib/wikiRepository.ts`：新 `searchSpotlightSources()`（按 source_id 集合做 exact-cosine，route/ANN 皆獨立，沿用 S174 footnote overlay 同一結構）+ `loadSpotlightChunks()`（按 id-set 為 key 的 process cache、`SPOTLIGHT_CHUNK_CAP=600` 上限）+ `searchFootnotes()` 加 optional `qVec` 參數（向後兼容）+ `invalidateWikiCache()` 一併清 spotlight cache。
  - `backend/src/api/searchChannelB.ts`：`SPOTLIGHT_SOURCE_IDS`（帶 `ack:spotlight:start/end` marker 供 executor 機器插入，初始 4 條）+ `SPOTLIGHT_LEAD_SCORE=0.60` + `SPOTLIGHT_MAX_LEADS=1`；主流程加 spotlight pass（footnote lead 之後插，`forcedLeads` 追蹤位置，source 已可見則不插，套用 supersede penalty，best-effort try/catch）；raw-query embedding 抽出一次由兩個 overlay 共用（**embedding 呼叫數不變**）。
  - `dev/source/execute_ingest.py`：新步驟 **4b spotlight 註冊**（`plan_spotlight_patch`/`live_spotlight_patch`，marker 缺失時發 warning 而非靜默）+ `post_deploy_smoke` 由「印一個無人睇的 bool」改為**真閘**（多種 phrasing 探測、報 rank、搵唔到就發 `::warning::` GitHub Actions annotation，仍非 fatal）+ `_annotate()` helper + dry-run plan/print 加 4b + docstring 步驟表。
  - `dev/CODEBASE_CONTEXT.md`：wikiRepository/searchChannelB/execute_ingest 描述 + AI Maintenance Log。`dev/DOC_SYNC_CHECKLIST.md`：補 Option A 管道 row（原本無 row 覆蓋該機制）。
- **Done:** commit `ef426cc` push → Render auto-deploy → **live 目標源 6/6 PASS**（edbcm113 rank 0；edbcm094 rank 2 ×3 phrasing；edbcm066 rank 2 ×2）+ synthesis grounded（「2026-27 公務員薪酬調整幅度 2%」／「英國語文科 5 級或以上」）。
- **QC:**
  - **根因 code-verified**（非靠推測）：`searchWiki` 向 Supabase 取**全庫** top-(top_k×5)=40，之後才在 JS 按 SOURCE_SET post-filter → 3–14 chunks 的新源要同全庫 15,901 chunks 爭 40 個位，**加 SOURCE_SET 或 TOPIC_KEYWORDS 結構上救唔到**。實測佐證：edbcm094 對自己標題 cosine **0.722** 卻完全唔出。
  - **門檻由實測定**：on-topic 直配 0.62–0.72；**20 條敵意 off-topic probe 最高 0.563**（「學校效率津貼」vs edbcm073）→ 0.60 收 0/20 敵意。低分 merge 刻意唔做（0.45 會收 6/20）。
  - **A/B 回歸**：本機（已修）對 prod（未修）14 條既有 query → 12 條完全相同；2 條差異**經隔離測試證明與本改動無關**——(a)「公積金 MPF」g24↔sag_2025_11 = 同一份學校行政手冊兩次入庫（`SOURCE_ALIASES`）、文字相同→cosine 完全同分 tie，**未修版本自己連跑亦會 3:3 交替**；(b)「資優教育課程」rank 7/8 近同分互換，**未修本機同樣異於 prod**（= prod-vs-local 環境差異）。另實測 OpenAI embedding 對同一輸入 **bit-identical**，排除 embedding 噪音假設。
  - **live 回歸**：13 條既有 query → **spotlight 污染 0/13**、既有預期命中 **5/5**、**9 條仍有 footnote_curated 參與**（證明共享 embedding 未破壞 S174 路徑）。
  - tsc exit 0 ×2；`py_compile` ✅；`discover_sources.py --self-test` ALL PASS；executor dry-run 正確顯示 4b（block 808-813、4 listed）且批准閘仍擋（`decision='no-approval-record'`）+ **零 live 寫入核實**（registry 248 / knowledge 15,901 / 無新 vault dir）。
  - **Monitor 核實**：Leonard 指定的 `…/technology-edu/curriculum-doc/index.html` **早已在 discovery watch list**（62 頁之一，經 `tech_curr_docs` 等 12 個 registry entry 的 `url_landing`）→ **無需新增、避免重複 row**。用 `discover_sources.py` 自己的函式對該頁 11 個文件連結做 diff：**2 條未入庫**——`IIT_Summary on AI_TC.pdf`（= edbcm113 通函所公布的《人工智能初探》框架**正文**，561KB，HTTP 200）+ `ICT_C&A Guide_c_final.pdf`（2.6MB，200；registry 的 `ict_sss_2021` 指向 edcity 另一 URL，疑為 EDB 版新檔名）。
- **Evidence disposition:** 根因機制 + 門檻實證 → 已寫入 code 註解（`SPOTLIGHT_SOURCE_IDS` 段落）+ 本 entry；當前狀態 → handoff Current Baseline S193；2 條未入庫候選 + tie 非決定性觀察 → handoff Open Priorities / 監察項；可重現 = commit `ef426cc`。
- **Sync:** DOC_SYNC 命中「Product behavior / tuning change」（handoff + log + QC evidence ✓）；Option A 管道原本**無 row** → 已補 row（registry anti-pattern guard）；CODEBASE_CONTEXT 模組描述 + AI log 更新。**無** Supabase／registry／凍結合約（`_meta` 2.3.0 / facts 455 / guidelines 158）／`PLATFORM_VERSION`／display-sync 改動（純檢索行為修復，同 S174/S183 先例一致唔 bump）。Pages 無需 redeploy（前端零接觸）。
- **Pending（非阻塞，待 Leonard 決）:** ① 入庫 `IIT_Summary on AI_TC.pdf`（補 edbcm113 只有 3 chunks 的先天單薄；建議做，屬 S170 monitor-driven on-demand 正路）② 核 `ICT_C&A Guide_c_final.pdf` 是否 `ict_sss_2021` 的 EDB 版／新版（可能係 URL churn 或 supersede）③ 「人工智能初探」「電子學習撥款」兩條短 query 仍唔出（chunk 對該 phrasing 只得 0.46–0.47，低於 0.60 bar；①入庫框架正文係更正確的解法，唔建議降 bar）。
- **Risks:** ⚠️ spotlight 名單會隨每次自動入庫增長（每條 query 對其 chunk 做 exact cosine）；已設 600 chunk 上限 + code 註明「確認能經 ANN 出頭後可 prune」，目前 4 源 36 chunks。⚠️ **新揭發（非本次造成）**：g24 / sag_2025_11 係同一份文件兩次入庫、chunk 文字相同 → cosine 完全同分，Channel B 結果對呢兩個 id 存在固有非決定性（同內容，用戶無感）；日後做檢索 eval harness（roadmap R1）必須容許 tie flip，否則會出假 regression。⚠️ 本次未動 judge 門檻：spotlight lead 若 <0.70 仍過 anti-confab judge（保護不變，故某些 query 有結果但可能唔出整理答案）。
- **Log maintenance:** §4a 機制閘已跑：`python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → `trigger=False line_trigger=False date_trigger=False`（line_count=349、entry_count=8；最舊 entry 2026-06-28 = 28 日）→ **no-op，唔觸發 archive**。

### Next Session Handoff Prompt (Verbatim)

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S193, 2026-07-26): 平台 v3.2.2; Supabase 15,901 chunks; source_registry 248;
HEAD==origin/main (ffd7f22 = S193 docs; code commit ef426cc); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158;
0 outstanding bug. 自動化 active: 4 源監察 (discover / freshness / served-url / new-circular) + Option A
自動入庫管道 (OPERATIONAL; 每日 19:30 HK refresh Issue + @mention-on-new; cron 20:00 HK 兜底).

⚠️ S192→S193 之間管道自行入庫 4 源 (+27 chunks, 15,874→15,901, registry 244→248) — 開工時本地會落後
origin/main, 先 git pull --ff-only 同步 (bot 直接 push main; tree 乾淨 + 0 本地 commit 時 ff-pull 安全).

📋 S193 修好: 「入庫但搵唔到」根因. searchWiki 取全庫 top-(top_k*5)=40 後才按 SOURCE_SET post-filter →
細源 (3-14 chunks) 結構上入唔到窗口, 加 SOURCE_SETS/TOPIC_KEYWORDS 都救唔到. 修法 = 新
wikiRepository.searchSpotlightSources() route/ANN-獨立 exact-cosine + SPOTLIGHT_SOURCE_IDS 一個 lead slot
@0.60 (實測: on-topic 0.62-0.72 vs 20 條敵意 off-topic 最高 0.563). executor 加步驟 4b 自動註冊新源 +
post_deploy_smoke 改為真閘 (報 rank, 搵唔到發 ::warning:: annotation). LIVE 6/6 PASS, 回歸污染 0/13.
⚠️ 動 backend 檢索前必讀 dev/SESSION_LOG.md S193 QC 段 (門檻實證 + tie-flip 陷阱).

🔜 NEXT (優先序; ①② 係 S193 直接遺留, 其餘同 S192 roadmap):
  ① 入庫《人工智能初探》框架正文 IIT_Summary on AI_TC.pdf (561KB/200, 見 handoff Open Priorities S193 ①):
     edbcm113 通函只有 3 chunks (封面+摘要), 正文才係實質內容; 亦係「人工智能初探」短 query 唔出嘅正解
     (唔應降 spotlight bar). 屬入庫 triage — 需 Leonard 拍板.
  ② 核 ICT_C&A Guide_c_final.pdf (2.6MB/200) 是否 registry ict_sss_2021 (現指 edcity URL) 嘅 EDB 新版
     → 若係新版走 supersede 規則 (SUPERSEDED_IDS + registry superseded_by 雙處同步).
  ③ Circular System 安全審計 (= roadmap R5): sibling repo EDB-AI-Circular-System (circular.wongfu.net, 亦
     public), 用 S187 同級 rigor (paste prompt 見 SESSION_LOG S190 closeout).
  ④ S187 安全 backlog (= R5): repo 轉 private + hosting 搬離 Pages / Supabase 開 RLS + anon RPC-only.
  ⑤ 維護提醒: spotlight 名單每次自動入庫 +1 (現 4 源 36 chunks / 上限 600), 確認能經 ANN 出頭後可 prune;
     edbcm073_2026 仍唔出 (0.458 低於 bar, 設計邊界非 bug), Leonard 報 miss 先處理.
  其他 backlog: roadmap R1-R8 (見 dev/SYSTEM_ANALYSIS_AND_ROADMAP.md §4/§5/§7);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A).

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft
HEAD==origin/main〔落後就 ff-pull〕+ Supabase chunk count), 然後向 Leonard 報告當前狀態同建議下一步.

所有路徑含空格, 終端機指令必須用雙引號包住. 改任何嘢之前, 先報告當前狀態同建議下一步.
```

---

## 2026-07-05 Session 192 — 系統分析 + 改進路線圖 deliverable（read-only 規劃，零 code/data 改動）

- **ID:** Claude_20260705_1315
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 跟 Draft §1 startup（讀 handoff/log/CODEBASE_CONTEXT/PMS）→ 起手探針 **4/4 綠**（served app.html v3.2.2 + title「香港學校政策搜尋平台」HTTP 200 / Render `/health` warm 455 / Draft HEAD `a47eedf`==origin/main tree 乾淨 / Supabase 15,874 文檔值未直連）。Leonard 要求：**分析及規劃現時系統功能同方向、改進空間，hands-off，寫成日後 claude agent 可執行嘅 deliverable，然後收工**（並提 `/model fable`——已說明 session 中途 agent 無法自切 model、實際 Opus 4.8 跑，實質要求照做）。純 read-only 分析、無改任何 code/data。
- **Changed:**
  - **NEW `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`** —— 策略分析 + 改進路線圖 deliverable。落地核實現況（app.html nav → 8 桌面 tab：平台介紹/政策搜尋/指引文件/通告分析/文件分析/文件標註/政策範本/文件修訂；server.ts → 11 backend routes）。內容：一頁摘要、現時功能全圖、系統健康誠實評估（做得好 4 項 + 技術債 7 項）、產品方向 A/B 觀察、**8 個已排序改進項 R1–R8**（R1 檢索 eval harness / R2 IA tab 收斂 / R3 Channel A 退役 / R4 codebase 可維護性單檔拆模組 / R5 安全 backlog / R6 Render 冷啟 / R7 mobile 全功能 / R8 reranking，每項帶 risk/工作量/首步/Leonard 決策/相關檔案）、不變量護欄 9 條（摘 PMS §A.2/§E/§F）、roadmap 執行次序、日後 agent 揀項指南。
  - `dev/SESSION_HANDOFF.md`：Current Baseline prepend S192 block；Open Priorities 頂加 roadmap 指針行；State Reconciliation 更新到 S192。
  - `dev/CODEBASE_CONTEXT.md`：directory map +1 行（新 doc）。
  - `START_NEXT_SESSION_PROMPT.txt`：重生為 S192 state-rich prompt。
- **Done:** deliverable 交付，日後任何 agent 讀 `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md` §4 即可挑 R 項落手。建議即刻無悔項＝R1 檢索 eval baseline + R5 sibling 安全審計（read-only）；R2 依賴 Leonard 定產品定位 A/B。
- **QC:** 現況數字全部 code-verified（app.html nav labels grep + server.ts route grep），非靠文檔記憶（守 memory 鐵律 verify-against-code）；deliverable 內零 hardcode live 數字（一律指向 handoff）；不變量護欄逐條對回 PMS §A.2/§E/§F。無 code/data 改動 → 無 build/regression/live smoke 需要（純文件）。起手探針 4/4 綠已記錄。
- **Evidence disposition:** 分析內容 → 新 deliverable（方向性文件）；當前狀態 → handoff Current Baseline S192；session trace + QC → 本 entry；reproducible = git commit（新 doc + 3 治理檔）。
- **Sync:** 純分析 deliverable + 治理持久化。CODEBASE_CONTEXT directory-map +1 行（新 dev 文件）。無 backend/stack/service/secret/凍結合約/PLATFORM_VERSION 改動 → 無 display-sync、無 Render/Pages redeploy、無 DOC_SYNC 產品 row 觸發。頂層 dormant root 文件層面零接觸（redirect 仍 valid）。
- **Pending（非阻塞）:** roadmap R1–R8 待 Leonard 揀方向落手（R2/R3/R4 動鎖定決策需 §3 HIGH-risk PLAN + 拍板；R1/R5 可無悔即做）。其餘 backlog 不變（見 handoff Open Priorities：Circular 安全審計 #1 等）。
- **Risks:** S192 = 純 read-only 分析、零風險（無 code/data/backend/contract 接觸）。⚠️ deliverable 係 point-in-time 方向文件，非 SSOT——日後 agent 落手前必以 handoff live 狀態為準、以 PMS 不變量為界（已喺文件開頭 + §5 + §7 寫明）。
- **Log maintenance:** §4a 檢查：SESSION_LOG 加 S192 後仍 <400 行、最舊 entry 2026-06-28（<30 日）→ 唔觸發 archive。no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S192, 2026-07-05): 平台 v3.2.2; Supabase 15,874 chunks; source_registry 244;
HEAD==origin/main (a47eedf + S192 closeout docs commit); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158;
0 outstanding bug. 自動化 active: 4 源監察 + Option A 自動入庫管道 (OPERATIONAL, VERIFIED LIVE).

📋 S192 交付: dev/SYSTEM_ANALYSIS_AND_ROADMAP.md — 系統分析 + 改進路線圖 (read-only, 零 code/data 改動).
8 個已排序改進項 R1–R8 (R1 檢索 eval harness / R2 IA tab 收斂 / R3 Channel A 退役 / R4 codebase 可維護性 /
R5 安全 backlog / R6 Render 冷啟 / R7 mobile 全功能 / R8 reranking), 每項帶 risk/首步/Leonard 決策/相關檔案.
揀項目落手前先讀該檔 §4 (項目) + §5 (不變量護欄) + §7 (揀項指南); live 狀態仍以 handoff 為準.
建議即刻無悔項: R1 檢索 eval baseline + R5 sibling Circular System 安全審計 (read-only);
R2 IA 收斂依賴 Leonard 先定產品定位 A (搜尋引擎) 定 B (文件合規工作台).

🔜 NEXT (待 Leonard 揀方向, = roadmap R 項對應):
  ① Circular System 安全審計 (Leonard 下個焦點, = roadmap R5): sibling repo EDB-AI-Circular-System
     (circular.wongfu.net, 亦 public), 用 PolicyChecker S187 同級 rigor 審 (paste prompt 見 SESSION_LOG S190 closeout).
  ② S187 PolicyChecker 安全 backlog (= roadmap R5): repo 轉 private + hosting 搬離 Pages (同 ops private-repo 合一) /
     Supabase 開 RLS + 收 anon RPC-only.
  其他 backlog (= roadmap R 項): S186 2 源 monitor (edbcm073 / edbcm066 短 query 排名低, 報 miss 先 boost);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A); Option A 低優先 follow-up.

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft HEAD==origin/main
+ Supabase chunk count), 然後向 Leonard 報告當前狀態同建議下一步 (可提 roadmap R1/R5 無悔項).

所有路徑含空格, 終端機指令必須用雙引號包住. 改任何嘢之前, 先報告當前狀態同建議下一步.
```

---

<!-- ack:log-entry:start -->

## 2026-07-30 Session 198 — S197 留低嘅「去睇 Render logs」係一個量唔到嘢嘅指示；換成主動量度

- **ID:** Claude_20260730_1015
- **Summary:** 起手探針 4/4 綠。Leonard 交返 S197 ① 嘅答案（Render logs search `channel-a` → No matching logs）。**冇當佢係「零流量」** —— 呢個結論啱好對我有利（我想拆 route），照 R-communication 規則 10 當未證實嚟查，結果證實個指示由頭到尾量唔到嘢。改為主動 instrument，已 live。**backend 兩條 route 仍然未拆**，而家等一個 7 日觀察窗。
- **起手探針 4/4 綠:** HEAD==origin/main `3cbaa9b` tree 乾淨 / Render `/health` `cache_a.warm=true size=455` / served `app.html` `PLATFORM_VERSION 3.2.2` + index 200 / Supabase `content-range 0-0/16062`。加驗凍結合約：`_meta` 2.3.0 / facts 455 / guidelines 逐 topic 加總 **158** / registry 256 / eval 34 —— 全部同 handoff 對得上，零 drift。
- **根因（三層，逐層有對照組）:**
  1. **`backend/src/server.ts` 冇任何 per-request log** —— 全檔只有 `:164` 錯誤、`:395/396` 開機三句。條 route 喺 `:324` 直接做嘢，成功請求永遠唔會印任何嘢。
  2. **Render 唔會代印 request path** —— 對照組：一個確實發生過嘅 `/health` request（我親手 curl 並收到 200 JSON），dashboard search「health」同樣零命中。
  3. **點解冇** —— 官方文檔 <https://render.com/docs/logging>：per-request log 係 **Pro workspace 以上**先有，呢個係 Hobby free instance。同時查到 **Hobby log 保留期 = 7 日**。
  正對照：search `CORS` **搵到** `server.ts:396` 嘅開機輸出 → **stdout 收得到、request path 收唔到**。
- **另一個獨立確認:** 全 repo grep（`.html/.js/.ts/.py/.json`，排除 log/archive）—— 兩條 route 淨係喺 `server.ts` 自己出現，**零呼叫點**；`mobile.js` 早於 S119 已轉去 `/api/search/channel-b`。所以唯一可能消費者只剩下游 Circular System（跨 repo）。⚠️ 順帶揪出文檔 drift：`dev/HANDOFF_PACKAGE.md:32` 仲寫「mobile search 已 ship 並接 `/api/search/combined`」，**已過時、未修**。
- **Changed:** `backend/src/server.ts` 加 `[route-probe]`（handler 最頂，OPTIONS 同 POST rate limiter 之上，只認兩條 route）；`dev/SESSION_HANDOFF.md`（Current Baseline +S198 block／Open Priorities 重生／Last Session Record／State Reconciliation Check／Next Session Opening Message 全部重生）；`dev/DOC_SYNC_CHECKLIST.md` **+1 row**（31→32）；`dev/PROJECT_DECISIONS.md` +Insights S198；`dev/CODEBASE_CONTEXT.md`（`server.ts` Directory Map 條目 + AI Maintenance Log）；`dev/archive/SESSION_LOG_2026_Q3.md`（新檔，§4a 歸檔）；`START_NEXT_SESSION_PROMPT.txt` 重生。
- **Done:** commits `ddc98d5`(probe) → `16fec71`(handoff checkpoint) → `2eb642f`(XFF 修正) → `07173f6`(handoff 更正) → `b74f5f4`(PERSIST：log entry + DOC_SYNC row) → 本 closeout commit。
- **QC:**
  - `npm run check` / `npm run build` exit 0 ×2（改 XFF 後重跑，冇當上次過咗就算）。
  - **本機自檢 ×2，兩次都對數**：首版 4 請求 → 3 行（**GET 錯 method 照捉** ✅、**channel-b negative control 零行** ✅）；XFF 版 3 請求 → 2 行（偽造兩跳 `203.0.113.9, 10.1.2.3` 全鏈捕獲、無 XFF 時 `xff=-` 但 peer 在、control 仍零行）。
  - **Live 驗（Leonard 提供 dashboard 截圖）**：三輪帶序號自測流量 **24 個請求 → 24 行，一行不多一行不少**。部署分水嶺清晰：seq 13 `[p2znr]` 舊格式 → seq 14 `[26wlj]` 新格式，即 `2eb642f` 落地於 10:06:30–10:07:45 UTC。
  - **XFF 修正的價值直接可見**：live 鏈 = `90.240.109.123`（真實公網）, `172.64.x`/`141.101.x`（Cloudflare）, `10.25.116.1`（Render 內部）。**舊 code 只印到最右嗰個 10.x，認唔到任何人。**
- **我喺本 session 犯咗、並已更正嘅錯:**
  1. **用 `/health` 嘅 `cache_a.warm` 偵測部署重啟** —— 行足 421 秒零命中，我一度想寫「未部署」。實情係**呢個偵測結構上無效**：Render 零停機部署先暖好新 instance 先切流量，外部永遠見唔到 `warm=false`。同「信 log search 嘅沉默」係同一種毛病。真憑據係 instance id 變咗（`pcwrl`→`p2znr`→`26wlj`）。
  2. **講過「09:52 嗰個 cold start 同我杯 curl 對得上」** —— 錯。由 seq=1 錨點（本機 09:40:48 UTC ↔ dashboard 10:40:48 AM）證實 **dashboard 顯示係 UTC+1**，即嗰個開機係 **08:52 UTC**，喺我第一杯 curl（約 09:35 UTC）之前 43 分鐘。**即係有啲嘢喺我開始之前叫醒過個 instance，來源未查明** —— 唔係 channel-a 流量嘅證據，但唔應該當唔存在。
  3. **PLAN 寫咗 IP 用嚟認人，首版做唔到** —— `getClientIp()` 取最右跳（S187 為 rate limiter 防偽造而設），live 實測最右跳係 Render 內部 10.x。按 §3 停低報告等 Leonard 指示，批「改」後先改，且只改 probe、`getClientIp()` 同 rate limiter 零接觸（仍在 `:247`）。
- **Evidence disposition:** 當前狀態＋觀察窗讀取日期＋刪除責任→handoff Open Priorities S198 ①；可重用程序知識（「先問個工具結構上量唔量得到」＋ negative control ＋ 部署確認唔可以靠猜重啟）→**`dev/DOC_SYNC_CHECKLIST.md` 新 row 嘅驗收欄**同 **`server.ts` probe 註釋**（handoff 會被重生，code 唔會）；量度細節→本 entry。
- **Sync:** DOC_SYNC 命中 **1 row（新增，31→32）**「臨時觀測 code 加落既有 backend route」—— 按 anti-pattern guard 先補行再填。`update_log.json` **N/A**（零入庫）。凍結合約 / `PLATFORM_VERSION` / Supabase 16,062 / registry 256 **全部零接觸**。Render deploy 每個 commit 一次（共 6 個 commit），**Pages 零改動**（本 session 無前端改動）。`START_NEXT_SESSION_PROMPT.txt` 由 handoff fenced block **程式化抽取**重生（非手打），mirror check **PASS**（5,906 字元逐字相同）。
- **Pending:** **觀察窗 09:40 UTC (2026-07-30) 開始**，**8 月 2 日 + 8 月 5 日各讀一次**（Hobby 保留 7 日，唔可以等到第 7 日）；讀時**扣起 24 行 `ua=s198-*`**；**🔴 讀完必須刪走 probe**。S197 ②–⑨ 全部未動（PAT scope / judge prompt / 總帳三桶 / 100 條鏡像 / g24 dedup / 維護項 / 文件 drift / roadmap 更正）。`HANDOFF_PACKAGE.md:32` drift 未修。
- **Risks:** ⚠️ 生產度而家有一段臨時 code。⚠️ 32 分鐘窗內零外部呼叫，**呢個數字唔代表任何嘢**，結論只可以寫「N 日內零外部呼叫」，唔可以寫「冇下游」（月更 job 捉唔到）。⚠️ XFF 最左跳係 client 自報、可偽造，屬 claim 唔係 fact。⚠️ 3 條同《學校行政手冊》矛盾嘅假期日數（病假 36 天等）仍然可經 `/api/search/channel-a` 攞到，route 一日未拆一日 serve 緊錯數。
- **順帶揪出、先前已存在、已修:** `dev/SESSION_LOG.md` 嘅 `ack:log-entry` marker 一直唔平衡（HEAD 本身 3 start／4 end，**非本 session 引入**）。歸檔搬走咗其中一個孤兒 `start` 之後，live 檔剩返 S195B entry 冇 `start` 但有孤兒 `end`。**已補回一行 `start`**（純新增、零資訊改動）→ 4 start／4 end 平衡。**影響先查明後至修**：歸檔腳本 `docs/qa/session_log_maintenance.py:30` 用 `^## YYYY-MM-DD` heading 切 entry、**唔用 ack marker**，所以本次歸檔唔受影響；缺陷實際只影響 Agent Handoff Kit `doctor` 嘅 marker 校驗。
- **Log maintenance:** `--check` → trigger=True（462 行 / 8 entries，line trigger 過 400）→ **已執行 `--apply --archive-dir dev/archive`**：**462 → 199 行、8 → 4 entries**，S195／S194／S193／S192 四個 entry 移入**新檔 `dev/archive/SESSION_LOG_2026_Q3.md`**（Q3 首次建立；Q1／Q2 已存在）。守恆核實：留 4 + 歸檔 4 = **8**，原文保留、零刪除。腳本 `--self-test` **5/5 PASS**。語意觸發：**有** —— 「先問個儀器結構上量唔量得到，唔好信佢嘅沉默」屬跨 session 累積模式（S195 spotlight 可達性 probe／S196 借錯測試集／S197 44% 覆核失敗率／本次 log search 同 warm 偵測**兩次**），已按 §4 step 11(c) 寫入 `dev/PROJECT_DECISIONS.md` Insights。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S198, 2026-07-30): 平台 v3.2.2; Supabase 16,062 chunks (本 session 零寫入);
source_registry 256; HEAD==origin/main; 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158;
0 outstanding bug。eval 34 條 (本 session 無檢索改動, 未重跑; 上次 PASS 23 / FAIL 0)。
自動化 active: 5 源監察 (discover / freshness / served-url / new-circular / 封面核對, 月跑)
+ Option A 自動入庫管道 (OPERATIONAL; 每日 19:30 HK refresh Issue; cron 20:00 HK 兜底)。

⚠️ 管道會自行入庫並直接 push main — 開工時本地可能落後 origin/main, tree 乾淨 + 0 本地 commit
時先 git pull --ff-only 同步。

🔴🔴 生產度而家有一段臨時 code — 呢個係本次交接最唔可以忘記嘅嘢:
  backend/src/server.ts handler 最頂嘅 [route-probe], 量度 /api/search/channel-a 同
  /api/search/combined 有冇外部呼叫。只印 method/path/origin/user-agent/完整 XFF 鏈/peer,
  永不印 body。commit ddc98d5 + 2eb642f, 已 live 驗證。
  ⏰ 觀察窗 2026-07-30 09:40 UTC 開始。Render Hobby log 只保留 7 日 →
     8 月 2 日 + 8 月 5 日 各讀一次 (Render → Logs → search route-probe), 唔好等到第 7 日。
  🧮 讀數時扣起 24 行 ua=s198-* (S198 自測流量), 剩低嘅先係外部呼叫。
  🗑 讀完必須刪走成段 probe。刪咗就可以按下面 ⑤ 拆 route。
  ⚠️ dashboard log 時間戳顯示係 UTC+1, 唔係 UTC (實測錨點: 09:40:48 UTC ↔ 顯示 10:40:48 AM)。

📋 S198 做咗 (零入庫、零檢索改動、Supabase 零寫入):
1. 證實 S197 留低嘅 ①「去 Render Logs search channel-a」係一個結構上量唔到嘢嘅指示 —
   Render per-request log 係 Pro plan 功能, 呢個係 Hobby instance。對照組: 一個確實發生過嘅
   /health request 同樣零命中; 但 search CORS 搵到 server.ts:396 開機輸出 →
   stdout 收得到、request path 收唔到。原本嗰個「No matching logs」係零資訊, 唔係零流量。
2. 改為主動 instrument (見上)。本機自檢 ×2 對數 + live 24 請求 → 24 行。
3. 全 repo grep 確認兩條 route 零內部呼叫點 (mobile.js 早於 S119 已轉 channel-b) →
   唯一可能消費者只剩下游 Circular System (跨 repo)。
4. DOC_SYNC +1 row (31→32)「臨時觀測 code 加落既有 backend route」。
5. §4a 歸檔已執行: SESSION_LOG 462→199 行、8→4 entries, S195/S194/S193/S192 移入
   新檔 dev/archive/SESSION_LOG_2026_Q3.md (守恆 4+4=8)。順手修好一個既有嘅
   ack:log-entry marker 唔平衡 (S195B 缺 start, 已補; 非本 session 造成)。

🚨 落手前必讀三件事:
   (a) dev/source/CHANNEL_A_COVERAGE_FINDINGS.md — 量度方法同兩個陷阱。最重要嘅數字:
       機械判定嘅 CLEARED tier 有 44% 撐唔住人手覆核 (16 條候選, 只 9 條過關)。
       所以總帳嘅 133 CLEARED / 107 PROVISIONAL / 172 UNVERIFIED 都唔可以當可退。
       唔准由總帳直接延長 RETIRED_MIRROR_CHUNK_IDS, 每條都要開段落嚟讀。
   (b) dev/source/JUDGE_PROMPT_FINDINGS.md — shipped judge prompt 近乎恆等於「否」
       (8/16, 8 條庫有答案嘅全部拒晒)。次序由實測釘死: 先修 judge, 後收 bypass。
   (c) 【S198 新增, 已寫入 PROJECT_DECISIONS Insights + DOC_SYNC 驗收欄 + code 註釋】
       一個工具嘅沉默唔係證據。面對任何 negative result, 落結論之前先問:
       「如果目標訊號真係存在, 呢個工具會唔會顯示到?」— 答唔到就搵一個已知發生過嘅事件
       做對照組。呢個陷阱我喺 S198 一個鐘之內踩咗兩次 (log search + /health 重啟偵測),
       兩次沉默都啱好指向我想要嘅答案, 所以靠「覺得唔妥」係捉唔到嘅。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 改 chunk 版本唔可以照 source_id 刪舊 — chunk id 係內容 hash, 兩版相同段落 id 會重疊。
  2. 判斷一個源「搵唔搵得到」唔可以用自己揀嘅 phrasing 做 probe。任何 spotlight / SOURCE_SETS /
     route / 門檻改動, 一律以 eval before→after 對為準。
  3. 報一個數之前: 先確認產生佢嗰個工具喺當前用途下成立, 再打開數字背後至少一個實例親眼睇。
     搜尋命中唔算證據。拆分/重標任何集合之後要對數。改治理檔用精確字串 + git diff 核實。
     貫穿條款: 如果一個判斷/遺漏/措辭會令自己份工睇落更好, 呢個方向本身就係觸發條件。
  4. 【S197 新增】剷走一批嘢之前, 要分清「有可引用替代品」同「係某類知識嘅唯一來源」。
     100 條剩低嘅 approved_fact 鏡像雖然冇 URL, 但佢哋係「邊個負責」(SENCO / 訓導主任 /
     活動主任) 嘅唯一來源 — 語料唔會寫成 [角色] 負責…。剷走會蝕。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --run --out after.json
  python3 dev/source/eval_retrieval.py --compare dev/source/eval_runs/2026-07-29_s197_after.json after.json
  python3 dev/source/channel_a_coverage.py --self-test
  python3 dev/source/channel_a_coverage.py --report dev/source/coverage_runs/2026-07-29_s197_full_v2.json --bucket NO_ANCHORS --sample 20
  python3 dev/source/footnote_lead_probe.py --self-test
  python3 dev/source/check_served_urls.py --check            # 268 URL, ~8 分鐘
  注意: coverage_runs/ 係 gitignored (embed cache 14MB, 可由工具重生)。

🔜 NEXT (優先序):
  ① 修 judge prompt (建議首選 — 影響每個用戶答案, 而且零部署可做)。
     先讀 JUDGE_PROMPT_FINDINGS.md。頭兩步冇風險: 砌一個未經 tune 嘅驗收集 (decline 半邊
     必須包含 S177 類 凍結教席→IMC 60%; answer 半邊由 curated footnote 自己嘅事實抽),
     然後先量 shipped prompt 做 baseline。改 prompt 本身係 §3 HIGH risk, 要出 PLAN。
     量度成本極低: chunk 抓一次快取, prompt 離線迭代, 唔使部署。
  ② 【只有 Leonard 做得到】確認 PUBLISH_PAT 係 fine-grained、只限 edb-circular-site
     contents:write。
  ③ 總帳 172 UNVERIFIED + 107 PROVISIONAL 未讀, 133 CLEARED 未抽樣 (見上 44%)。
     離線可做, embedding 已快取, 重跑唔使畀錢。
  ④ 100 條無出處鏡像仍喺服務路徑 —— 護欄穿窿, 但係「邊個負責」唯一來源, 唔可以照剷。
  ⑤ 【等觀察窗有結果先做】拆 backend 半邊: /api/search/channel-a + /api/search/combined +
     searchChannelA.ts + searchCombined.ts + factEmbeddingCache.ts + /health 拎走 cache_a +
     開機唔再 embed 455 條。前置 = 上面紅字嗰個觀察窗讀完 + probe 刪走。
     ⚠️ knowledgeRepository.ts 要留 (analyzeCircular.ts 仍 import)。
     ⚠️ knowledge.json 刪唔得 (index.html:561 首頁統計 + q.html:233 全靠佢)。
     ⚠️ 額外理由: 3 條同《學校行政手冊》矛盾嘅假期日數 (病假「36天」vs 附錄9 28/48/168天;
        非教學年假 18/21/24 vs 7天起上限14天) 已證唔喺 Supabase, 只可經 channel-a route
        攞到 — route 一日未拆, 一日 serve 緊錯數。
     ⚠️ 結論寫法: 只可以寫「N 日內零外部呼叫」, 唔可以寫「冇下游」(月更 job 捉唔到)。
  ⑥ 【較大】g24 同 sag_2025_11 係同一份《學校行政手冊》登記兩次, 215 條 chunk 文字完全相同。
  ⑦ 【維護】封面核對 baseline (208 條) / spotlight 6 源 / MIN_OVERLAP 兩份鏡像。
  ⑧ 【文件 drift】三處對「下游有冇轉 Channel B」講法唔一致; CHANNEL_B_SYNC_KEY 實測已配置
     (probe 得 401 而非 503) 但唔證明下游用緊。①有答案後一併更正。
  其他 backlog: roadmap R1-R8 (dev/SYSTEM_ANALYSIS_AND_ROADMAP.md — 寫於 2026-07-05,
  R1 大致落地 / R5 已做 / R8 前置已解除, 落手前先睇 handoff Open Priorities ⑨ 嘅更正);
  Feature 2a 追問 + 2b 文件 scoped Q&A; 雲端 OCR 引擎選項。

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 +
Draft HEAD==origin/main〔落後就 ff-pull〕+ Supabase count=exact 16,062), 然後向 Leonard
報告當前狀態同建議下一步。
⏰ 如果今日已經係 2026-08-02 或之後: 起手探針之後即刻提醒 Leonard 開 Render Logs
   search route-probe 讀觀察窗 (扣起 ua=s198-* 嗰 24 行)。如果已經過咗 2026-08-06,
   Hobby 7 日保留期已滿, 最早嗰幾日嘅記錄已經永久冇咗 — 照讀剩返嘅, 但結論要寫明
   個窗殘缺, 唔好當佢係完整 7 日。無論讀到乜, 讀完就要刪走 probe。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-07-29 Session 197 — Channel A 退役：量度「Channel B 食唔食得晒」，答案唔喺覆蓋率，而喺 Channel A 自己載住乜

- **ID:** Claude_20260729_S197
- **Summary:** Leonard 問 roadmap → 我指出 R1/R5 已過時、R3 卡喺一個文件互相矛盾嘅前提。Leonard 提出退役標準「已喺 Channel B 或可追蹤出處就可以退」→ 我建工具量度 455 條 → **兩次推翻自己**（一次係把尺壞咗、一次係由一個實例推去成批）→ 最後只退咗前端路徑 + 9 條有已證出處嘅鏡像 chunk。backend 兩條 route **未郁**，卡喺 Leonard 未覆嘅 Render logs。
- **起手探針 4/4 綠:** served `app.html` `PLATFORM_VERSION 3.2.2` + index 200 / Render `/health` `cache_a.warm=true size=455` / HEAD==origin/main `523f5db` tree 乾淨 / Supabase `content-range 0-999/16062`。
- **量度設計上兩個唔講就會出假數嘅決定:**
  1. **「輸出完全一樣」唔係可用標準。** Channel A 事實係冇 URL 冇頁碼嘅裸句（實查 `role_facts.json`：455 條散喺 47 個〔範疇×角色〕桶，`_source_refs` 只喺範疇層），Channel B 出原文＋URL＋頁碼，兩者永遠唔會一樣。改為量「substance 覆蓋」。
  2. **必須剔走語料入面 Channel A 自己嘅鏡像。** `wiki_chunks` 16,062 = `vault_extract` 15,721 + `footnote_curated` 206 + `approved_fact` 109 + `stat_fact` 26（逐類點過、總和相符）。嗰 109 條**逐字係 455 條嘅子集**（精確字串比對 109/109 命中、0 條外來），同 26 條 stat_fact 一樣 **url 全空**。唔剔走，攞事實去搵第一個命中就係佢自己 @0.828 → 會量到「455/455 全覆蓋」，而個數純粹係「問題就係佢自己嘅答案」。
- **Changed:**
  - **新工具 `dev/source/channel_a_coverage.py`**（self-test 34 項，含兩條「故意整壞證明守衛會 FAIL」）：embed 455 條 → RPC 取 40 條 → 濾剩文件語料 → 硬錨點（金額／日數／%／條號）比對，**錨點必須齊集喺同一段**（散落兩份文件 = S177 砌數形態，唔收）；lexical 層自帶對照組；傳輸失敗歸 `ERROR` 永不當「冇覆蓋」。
  - **`dev/source/CHANNEL_A_RETIREMENT_LEDGER.tsv`**：455 條逐條 tier + 已核實出處 + 頁碼。
  - **`app.html`**：移除 `runChannelA` / `runCombined` / `searchChannel` / `qaRole` / `channelACount` / `CHANNEL_OPTS` / `highlightFact` + tokens / Channel A 角色選單 / 兩個死 caption（−109/+8 行）。
  - **`backend/src/api/searchChannelB.ts`**：新 `RETIRED_MIRROR_CHUNK_IDS`（9 個 chunk id，逐個附已核實出處註釋）+ `retiredMirrorFilter`，套落三個 `toChannelBResult` 映射點。
  - **`dev/source/eval_queries.json`** 30 → **34**（新增 4 條角色職責 query）。
- **Done:** commits `c01e646`(量度) → `596e383`(總帳) → `2d70ef7`(前端) → `5754c00`(eval 補盲) → `3ba92fe`(9 條鏡像退役) → `d554b4c`(記錄) → 本 closeout commit。
- **QC:**
  - **eval 34 條 before→after**：`_before34b` PASS 23 / FAIL 0 / errors 0 → `_after` **PASS 23 / FAIL 0 / errors 0，0 blocking failures**，32 條完全相同。
  - 唯一 `SET_ADDED` = `procurement` 加入 `subvention_tips` —— 鏡像讓出嘅位由**佢自己嘅可引用正版**補上，正是預期效果。
  - `bus_escort` `RANK_SHIFT`：來源集不變、第 4/5 位對調，同 9 條改動扯唔上；符合設計容許嘅 ANN tie flip，**未獨立證實成因**。
  - **live 抽驗**：「採購門檻」rank-0 由 `role_facts_finance`（url 空 / page null）變 `g01` **p.5**；「連續缺課 呈報」「十二種首要價值觀」top-8 鏡像歸零；「訓導主任 社工」鏡像**完整保留** rank 0/1（設計意圖）。
  - 前端 live 驗：served `app.html` `runChannelA`/`runCombined`/`searchChannel`/`qaRole`/`CHANNEL_OPTS`/`search/channel-a` 全部 **0**；1280px 重載 console 零 error、`select` 數 0；Channel B 搜尋 HTTP 200 / 7 條 / synthesis 正常。
  - tsc exit 0 ×2；Supabase 16,062 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / v3.2.2 **全部零接觸**（Supabase 零寫入，只加 code 層 filter）。
- **兩次推翻自己（本 session 最有價值嘅部分）:**
  1. **把尺壞咗。** 首輪報「8月15日前提交假期表」搵唔到錨點；打開 `g11` 一睇：「於每年**八月十五日**前……呈交下一學年的學校假期表」——**同一條規則，中文數字寫**。首 29 條入面 10 條同一原因。加 `fold_cn_numerals`（處理「二零二五」=2025 同「三十」=30 兩種讀法）離線重判：**71 條轉桶，COVERED 100 → 149**。⚠️ 方向性：呢個 bug 令工具**系統性高報缺口**，而每個假缺口都係「唔可以退 Channel A」嘅理由 —— 修之前個數會令「保留」睇落更有道理。
  2. **由一個實例推去成批。** 我見到「採購門檻」rank-0 係無出處鏡像壓住 `g01` p.5，就提議**整批剷走 109 條**、並講「拎走唔係損失」。量埋成批之後：**93/109 冇已證替代品**，而且大部分係 `[角色] 負責…` 呢種語料唔會有嘅形態。live 實測「訓導主任 社工」鏡像佔 rank 0/1、語料最近似（`g16` p.17）講跨部門聯繫而唔講邊個負責；「活動主任 職責」頭四名三個係鏡像。**剷走真係會蝕。** 已喺報告同 commit message 更正。
- **另一個必須記低嘅數字：機械判定 `CLEARED` 有 44% 撐唔住人手覆核。** 總帳提供 16 條「有可引用替代品」候選，逐條讀完**只有 9 條過關**。7 條嘅失效模式各異：段落講另一個科目（人文科 vs 小學科學）／用「五種基要學習經歷」嘅**定義**冒充津貼用途**規則**／實質內容有但**職責歸屬冇**（段落講「其他學習經歷委員會由副校長帶領」，事實寫「[活動主任] 負責」）／所謂替代品係一份**問卷通告**。**規則已寫入 `searchChannelB.ts` 該常數註釋：唔准由總帳直接延長個 list，每條都要開段落嚟讀。**
- **eval 集本來對呢個改動完全盲（已修）:** 原 30 條**冇一條** expect `role_facts_*`、冇一條問「邊個負責」→ 剷走鏡像會量到零回歸，而嗰個綠燈係假嘅，同 S195 spotlight prune 撞板同一形態。加 4 條角色職責 query 後，其中 2 條（`senco_role`/`curr_coord_role`）**由 baseline 證實我釘錯咗預期**（語料 `g19` p.13/p.57 先係服務緊 SENCO 嗰個），已即時更正而唔係留住一個永久紅燈（S195 十一個假警報嘅教訓）；`curr_coord_role` 改 RECORD_ONLY —— 冇任何來源答得好，釘任何一個都係把爛答案封為正確。
- **順帶揪出、未處理:** 3 條 Channel A 事實**同現行《學校行政手冊》直接矛盾**（病假「36天」vs `sag_2025_11` 附錄9「首年28天／其後48天／累積168天」；非教學人員年假「18/21/24天」vs「7天起、上限14天」）。**已查證呢 3 條唔喺 Supabase**（store 含「36天」嘅 `approved_fact` = 0），所以唔會經 Channel B 出街，只可經 `/api/search/channel-a` 攞到 → 會隨 backend route 退役一齊斷。另：455 條入面有問卷題、活動統計、殘缺片段（「取得校長批准。」「2013年4月1日作出修訂。」← 已鎖定來源係 `coa_imc_1_19` 嘅修訂註腳欄）、簡體字同日文漢字「関」等抽取瑕疵。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S197 block；量度方法＋兩次自我推翻＋44% 覆核失敗率→`dev/source/CHANNEL_A_COVERAGE_FINDINGS.md`（可重用程序知識，唔止留喺 log）；逐條 tier + 出處→`CHANNEL_A_RETIREMENT_LEDGER.tsv`；三份 eval run→`dev/source/eval_runs/`（commit，跨 session 可比）；**「唔准由總帳延長 retired list」呢條紀律→`searchChannelB.ts` 該常數上面嘅註釋**（下一個想加 id 嘅人一定睇到）；run JSON + embed cache→gitignored（14MB／4MB，可由工具重生）。
- **Sync:** DOC_SYNC 命中 2 row（檢索 eval harness 改動 ✓ eval_queries 30→34＋三份 run＋before→after 對／**新增 1 row「store chunk 退出服務路徑」** ✓ 按 anti-pattern guard 先補行）。`update_log.json` **N/A**（零入庫、純服務路徑改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 隨 `app.html` push redeploy（已驗）；Render deploy 1 次（已驗）。
- **Pending:** backend `/api/search/channel-a` + `/api/search/combined` 未退（阻塞前置＝Render logs `channel-a` 流量，Leonard 未覆）；總帳 **172 條 UNVERIFIED + 107 條 PROVISIONAL** 未逐條讀；133 條 CLEARED 未抽樣覆核。
- **Risks:** ⚠️ 按 44% 覆核失敗率，`CLEARED`／`PROVISIONAL` 兩桶**唔可以當可退**。⚠️ 100 條無出處鏡像仍然喺 Channel B 服務路徑，「答案必有出處」呢條護欄喺佢哋身上仍然穿窿 —— 但佢哋係「邊個負責」嘅唯一來源，唔可以照剷。⚠️ 文件三處對「下游有冇轉 Channel B」講法不一致（PMS §F.11 話已轉／roadmap R3 當未確認／§F.2 話待協調），而 `CHANNEL_B_SYNC_KEY` 實測**已配置**（probe 得 401 `missing X-Sync-Key` 而非 503 `sync disabled`）—— 呢個只證明 key 設咗，證明唔到下游用緊。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → **trigger=False**（line_count=381 / entry_count=6，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 「機械判定唔可以取代讀原文」屬跨 session 累積模式（S195 spotlight probe／S196 借錯測試集／本次 44%），已按 §4 step 11(c) 寫入 `dev/PROJECT_DECISIONS.md` Insights 而非只留喺 log。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-07-28 Session 196 — handoff 講嘅根因係錯嘅：「校巴營辦商責任」唔係 route 次序，係 curated footnote 搶咗 lead slot 兼跳過 anti-confab judge

- **ID:** Claude_20260728_S196
- **Summary:** 起手探針 4/4 綠 → 我建議做 Open Priority ②（校巴 route 次序）→ Leonard「go」→ **READ 階段用 code + live 證實 handoff 記錯根因，按 §3 停低報告** → Leonard 揀 C（A+B 一次過做）→ 我保住歸因，逐個改動各自一對 eval/probe，共 4 次部署。
- **§3 停低（值得記低）:** `detectQueryCategory("校巴營辦商責任")` 一直都返 `safety`，六種校巴 phrasing 全部一樣。改 TOPIC_KEYWORDS 次序會係 **no-op**。真根因喺兩層：(1) `SOURCE_SETS.safety` 同時載住 `sag_2025_11`（學校行政手冊 215 chunks），佢嘅籌款／捐款／供應商段落 0.602/0.535/0.529 壓過 `sch_bus_operators_2026` 0.506；(2) 兩條 `footnote_curated` 靠 `FOOTNOTE_LEAD_SCORE=0.45` 攞咗 rank 0/1（0.518 小賣部經營利潤、0.495 承辦商 SCRC），**而 footnote lead 會跳過 anti-confab judge** → 出街答案講「校巴經營利潤必須運用於學生的直接利益」。即係話呢條唔止排名差，係**答錯嘢**。
- **Changed:**
  - **A（`school_bus` 專屬 route）**：`SOURCE_SETS.school_bus` = g18 + 5 份 2026/27 姊妹指引；bus tokens 由 `safety` **搬**過去（唔係複製）；新 `QUERY_EXPANSIONS.school_bus`。
  - **A'（修 expansion）**：第一版 expansion 塞晒六個受眾名詞（司機／營辦商／跟車保母／家長），eval 即刻捉到「跟車保母」由 escorts rank 0 跌落 operators rank 0 —— 姊妹之間唯一嘅分別詞被自己洗走。改為只留共通詞彙。
  - **B（footnote lead 加 lexical gate）**：新 `backend/src/lib/textBigrams.ts`（`cjkBigrams` 由 `checklistRevise.ts` 搬入 lib 並 re-export，避免 lib→api 反向依賴）＋ `wikiRepository.footnoteInformativeBigrams()`（喺常駐 footnote 語料上做 DF 校準）；footnote 要同 query 共享 ≥ `FOOTNOTE_LEAD_MIN_OVERLAP` 個 informative bigram 先攞得到 lead slot；judge bypass 由「邊個坐 rank 0」改為綁定「gate 批准咗嘅 lead」。**被拒嘅 footnote 唔會被刪，照按分數 merge —— 收走嘅只係特權。**
  - **B'（1 → 2 ＋ query-signal 規則）**：見下。
  - 新工具 `dev/source/footnote_lead_probe.py`（13 條 self-test）；`dev/DOC_SYNC_CHECKLIST.md` 補一行「Synthesis 前置閘改動」；`CODEBASE_CONTEXT.md` Directory Map ＋ 3 個模組描述。
- **Done:** commits `b61e108`(A) → `7078719`(A') → `528435d`(B@1) → `969698e`(B'@2) → `138dfca`(QC 證據＋docs)。四次 Render 部署，每次 live 驗。
- **兩個「deploy 完先捉到」嘅嘢（offline 校準過關唔代表得）:**
  1. **門檻 1 唔夠**：中文字元 bigram 分唔開 `營辦商` 同 `承辦商`（兩者都有 `辦商`），所以 SCRC footnote 喺 MIN=1 之下仍然攞到 lead。**係 deploy 完 live 重探先捉到**，離線校準睇唔到（我個 probe 只記錄第一條 footnote lead）。
  2. **淨係抬高到 2 會有代價**：實測全語料，MIN=2 會令 1 條 footnote 失去自己問題嘅席位 —— 一條幾乎全英文嘅問題（"NET Grant School Plan / School Report 要點？"），佢個 overlap=1 淨係來自 `要點` 呢個通用詞。正解 = **gate 只喺 query 本身有 ≥2 個 informative bigram 先啟動，唔夠就 fail open**（量度唔到就維持舊行為）。實測：206/206 條 footnote 自己嘅問題全部保住（3 條走 fail-open），而三條校巴 phrasing 嘅兩條離題 footnote 全部被擋。
- **QC:**
  - **eval 三對**（全部 commit）：baseline `_before` PASS 20/30 → `_after_a`（捉到 1 個 SET_LOST）→ `_after_a2`（修完 SET_LOST 0）→ `_after_b`（MIN=1，PASS 19 errors 1 = Render transient）→ `_final` **PASS 20/30 FAIL 0 errors 0**。
  - **footnote probe 兩對**：`_fnlead_before` → `_fnlead_final`：**positive 26/26 一條都冇跌**；negative 剷走 4 條（三條校巴 ＋ 校長退休金）。
  - **全語料覆核（唔止抽樣）**：206/206 footnote 自問仍然攞到 lead；TS 同 Python 兩份鏡像算出嘅 informative bigram 數**都係 7828**，證明冇實作漂移。
  - **eval 最終 6 條 SET_LOST 逐條人手判斷**：全部同一形狀 —— 離題 curated footnote 失去佢唔應該有嘅頭位，而每條 query 嘅正確文件都升咗上嚟（考試調適原本俾幼稚園非華語津貼 footnote 帶頭、家校合作俾寄宿津貼、薪酬調整俾 NET 計劃改革）。**即係話呢個缺陷 30 條 eval 入面影響 6 條，唔止報上嚟嗰條。**
  - live 終驗「校巴營辦商責任」：8 條結果全部係校巴指引 @0.714-0.772，答案改為跟車保母／車輛檢查／保護式座椅／2026 年安全帶新規／客運營業證，原本嗰段「經營利潤回饋學生」消失。
  - tsc exit 0 ×4；`footnote_lead_probe.py --self-test` PASS；routing probe 16 條，其中 3 條唔符我預期嘅**攞 HEAD 版本行同一組 probe 證實係改動前既有行為**（`校舍安全` 落 gov_admin、兩條視藝 query 落 null）。
  - 凍結合約零接觸（Supabase 16,062 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / PLATFORM_VERSION 3.2.2 全部未郁）。
- **明文未修（唔好當已解決）:** plausible-gap 類 negative 仍然攞得到 lead（overlap 1-10）—— 一條「語域啱、答案根本唔喺庫」嘅 query，overlap 可以**高過**一條用英文問嘅真命中。呢條軸上冇任何門檻分得開，屬 Open Priority ④（改良 judge prompt），`judge_probe.py` 仍然係佢嘅驗收工具。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S196 block；五份 run→`dev/source/eval_runs/`（commit，跨 session 可比）；兩個常數嘅實測分佈→code 註釋（唔止留喺 log）；新驗收工具→`footnote_lead_probe.py` ＋ DOC_SYNC 新行（可重用程序知識）；handoff 記錯根因→已喺 Open Priorities 更正。
- **Sync:** DOC_SYNC 命中 3 row（檢索 eval harness ✓ 三對 run／Channel-B SOURCE_SETS+TOPIC_KEYWORDS+QUERY_EXPANSIONS parity ✓／**新增 1 row「Synthesis 前置閘改動」** ✓ 按 anti-pattern guard 先補行）。`update_log.json` **N/A**（純檢索行為修復，無新源入庫，按 S190 定案唔記維護性改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 無需 redeploy（純 backend）。
- **Risks:** ⚠️ plausible-gap footnote lead 未解（見上）。⚠️ `footnote_lead_probe.py` 嘅 `MIN_OVERLAP` 同 backend `FOOTNOTE_LEAD_MIN_OVERLAP` 係兩份鏡像，改一邊必須改另一邊，否則 probe 會量度緊一個唔存在嘅 build（已寫入 CODEBASE_CONTEXT 該檔描述）。⚠️ Render free tier 偶發 transient error（本 session eval 撞過一次，harness 正確記做 error）。
- **收工前第三輪（Leonard 再批 go ×2）—— 兩個推翻自己嘅發現:**
  1. **我個 footnote probe 標錯 negative。** 我直接借用 `judge_probe.py` 嘅 class B，但嗰個 set 係為 **vault** 門檻設計（問「vault 答唔答到」），而 curated footnote 精準答到當中 4 條（幼稚園每班30人／病假超逾兩天／招標最少5個報價／投訴兩個月＋14天）。已改為 `ANSWERABLE_CONTROLS` 當 positive。**重跑：positive 30/30 全保。** ⚠️ **同一 session 內要再更正一次**：我第一次報「2/10」係錯嘅 —— 重寫 negative list 時，3 條 borderline（解僱教師遣散費／學校借錢俾教職員／教師評核合格分）冇歸入任何一堆就消失咗，而我冇對過拆完之後總數返唔返到 14。三條**全部仍然攞到 footnote lead**，即個疏忽一路向自己有利，令我低報咗一半以上。逐條打開語料實物核實（唔係靠關鍵字命中）後三條都證實係真空白，已放回 negative → **修正後 negative 5/13，positive 30/30 不變**。當中「學校可唔可以借錢俾教職員」全庫零相關規則（`借貸`／`借錢`／`貸款` 命中全部係 BAFS 會計科、學生賭博警號、學生資助貸款）但系統答得斬釘截鐵 —— **呢條係真‧砌數，唔係「答隔籬」**，所以殘餘問題唔可以統稱為答隔籬。**教訓：拆分或重標一個測試集之後必須對返總數，尤其當個錯會令自己個結果好睇。**順帶查實 `不應超過30` 嘅 vault 命中係 g07 講家課時間，唔係班級人數 → **S195B「VAULT_LEAD_SCORE 降唔到」結論企得住，唔使重開**。
  2. **judge 本身近乎恆等於「否」。** 離線直接叫 judge（同一 prompt／同一 model／真 top-5 chunks）跑 16 條（8 條庫有答案、8 條冇）：**shipped prompt 8/16，8 條有答案嘅全部拒晒**，其中 4 條答案逐字喺 chunk 入面。生產睇落無事，係因為 footnote／vault 兩個 bypass 幫佢繞過咗；judge 真係行到嘅時候基本上唔會答「能」。**呢個就係 S194／S195B 觀察到「judge 過度拒答」嘅根因** —— prompt 嗰句「有任何不確定，一律答否」被模型當成一條全局信心題。
- **點解冇 ship bypass 收緊（原本嘅任務）:** 收緊嘅設計成立（覆蓋率 negative 0.40/0.62 vs positive p10 0.77，ratio ≥0.70 兩條全擋），但把會失去 bypass 嗰 2 條 answerable control 交俾**真 judge** 判，**兩條都拒答** → 換嚟嘅係用兩個「答啱」去換兩個「答隔籬」，淨蝕。**次序由實測釘死：先修 judge，後收 bypass。**
- **點解冇 ship judge 改良:** V3（把判斷寫成「對住文本做測試」而唔係態度）由 8/16 升到 **11/16 零誤放**（S177 凍結教席砌數案例照樣拒）；V4 寫更詳細反而跌返 8/16。但 16 條 case 係我自己 tune 出嚟，而呢個係 anti-confab 骨幹 —— 由「永遠拒」變「有時答」嘅風險面遠超我個測試集。全部量度＋V3 全文＋ship 前需要嘅嘢寫晒入新檔 `dev/source/JUDGE_PROMPT_FINDINGS.md`。**方法本身係最有價值嘅交接**：chunk 攞一次快取，prompt 離線迭代，唔使部署。
- **紀錄更正（收工時逐項核對 commit 實況後補回，唔改寫歷史）:**
  1. `3d4ecf0` 個 message 把「7+4≠14」寫成純粹漏對數。**唔準確**：實錄顯示我事前逐條判過嗰三條係「borderline、部分答到」，即係我做過判斷（而且三次都判錯，全部錯向「唔使當佢係問題」嗰邊），唔係冇判過。
  2. `c4e5830` 個 message 最後一段描述 `footnote_lead_probe.py` 嘅集合對數守衛，**但嗰個改動實際喺 `9804239`**；`c4e5830` 只含兩個 rule 檔。
  3. 我曾向 Leonard 講「守衛個改動仲喺 working tree」—— **錯**，`9804239` 已經 commit 咗；而且我當時自己印出嘅 `git status` 已經顯示只有兩個 rule 檔有改動，即證據在眼前仍憑印象講。呢三項全部係新寫嘅 communication pack 第 9 條（講自己做過乜要引實錄）要防嘅行為。
- **收工前規則落地（Leonard 指示「設定規則防止再犯武斷及疏忽」）:** `dev/rules/communication.md` 由 5 條擴到 10 條 —— **第 3 條改寫**（「標示未驗證」→「引唔到出處就唔准落判詞，只可寫『未查』」，按 §3b 整合而非另開平行條文，舊句已retire）；新增第 6-9 條（搜尋命中唔算證據／借用工具前先確認佢原本量度乜／動集合對數＋動文字睇 diff、禁止跨行 regex 改治理檔／講自己做過乜要引實錄）；**第 10 條貫穿條款＝方向不對稱本身就係觸發條件**。`dev/RULE_PACKS.md` 擴闊該 pack 嘅載入條件（原本只喺「reply format」類任務載入，即今日呢種 session 根本讀唔到）。機器化部分：`footnote_lead_probe.py` 加 `partition_gaps()` + self-test 斷言，**用故意整壞佢證明會 FAIL**（exit 1 並列出消失嘅 query），唔係只見過佢 PASS。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → **trigger=False**（line_count=375 / entry_count=6，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 本 session 屬「跨 session 累積模式」（同一類報告紀律問題喺 S195B 已出現過一次），已按 §4 step 11(c) 意圖把可轉移部分寫成 `dev/rules/communication.md` 規則而非只留喺 log。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS，74 行。）

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-07-27 Session 195B — Leonard「全做」：清埋 8 項優先事項；兩項結論同假設相反，一項係自己整壞由 eval 捉返

- **ID:** Claude_20260727_S195B
- **Summary:** 接住 S195 上半（清死連結）。Leonard「全做」→ 我開 task list、先攞 eval baseline（因為多項改檢索）、逐項落手。8 項：1 項做唔到（需 Leonard 帳戶權限）、2 項結論同原本假設相反、1 項我做錯咗由 eval 捉到即刻還原。
- **Changed:**
  - **新源**：`sch_bus_{drivers,escorts,operators,parents,students}_2026`（28 chunks）＋ `va_safety_sec`（27）。新腳本 `dev/_extract_s195_schoolbus.py`／`dev/_extract_s195_safety.py`。
  - **重抽**：`g21`（22 頁，只餘小學版）／`g22`（52 頁，補回封面頁）。刪除 106 條舊 chunk（腳本 `dev/_s195_delete_stale_g21_g22.py` + 鎖死嘅 `dev/_s195_g21_g22_delete_set.json`，由 Leonard 執行）。
  - **backend**：`SOURCE_SETS.safety` +5 校車源、`TOPIC_KEYWORDS.safety` +校巴/保母車/跟車保母/學生服務車輛、移除 `kgecg_2017` 兩處 dead 引用、`VAULT_LEAD_SCORE` 加實測註釋、spotlight 先剪後還原（附教訓註釋）。
  - **監察**：`check_source_titles.py` 加 `--baseline`／`diff_baseline()`＋9 條 self-test；新 `.github/workflows/title_check.yml`（月跑）；`FRESHNESS_GUIDE` §0/§1/§2 補 Method C CI 同指令。
  - **新工具**：`dev/source/judge_probe.py`（24 條敵意 probe）。`eval_queries.json` 25 → **30**（新增 5 條守住今次入庫嘅源）。
  - registry 250 → **256**；display-sync 7 檔 16,033 → **16,062**；`update_log.json` +3 條；CHANGELOG 新條目。
- **Done:** commits `7f4c306`（主體）→ `2f04c42`（spotlight revert）→ 本 closeout commit。**最終 eval PASS 20 / FAIL 0 / errors 0**（30 條）。
- **QC:**
  - **eval before→after 對**：baseline `2026-07-27_s195_before.json`（PASS 15/25）→ 中途 `_after.json` **捉到 3 條 regression** → 還原後 `_after_revert.json` 對 baseline **25/25 全同** → 擴 query 後 `_final.json` **PASS 20/30**。四份 run 全部 commit。
  - **頁碼錨點逐源自檢**（因為今次修嘅正正係錯位）：5 份校車 6/6、2/2、6/6、5/5、1/1；g18 6/6；全部 offset 0 對齊。
  - **刪除安全**：兩條 `footnote_curated` chunk 明文排除（照 `source_id` 刪會毀掉人手內容）；刪除集 = 舊 id − 新 id；逐條刪逐條驗；事後 g21 23／g22 59／va_safety_sec 27／總數 16,062 全對。
  - 凍結合約：`knowledge.json` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 **158** —— `build_guidelines.py --self-test` PASS（registry 167→166、public 158 不變）。tsc exit 0 ×4。
- **兩個結論同原本假設相反：**
  1. **judge 門檻唔可以降（②）** —— 24 條 probe：敵意類最高 **0.632**、真命中最低 **0.624**，**分佈重疊**。降到 0.60 會放行「教師每年可以請幾多日大假」(0.617)／「學校可唔可以借錢俾教職員」(0.615)／「校服供應商招標要幾多間報價」(0.614)，全部語域啱而個數字唔存在 = S177 砌數重演。**cosine 分唔開「揾到對嘅文件」同「揾到語域相同嘅文件」**，所以唔係揀邊個數字嘅問題。保留 0.70，實測寫入 code。
  2. **`religious_edu_jss` 唔使郁凍結 count（⑧）** —— 公開庫一早已有正確嘅 `religious_edu_jss_2024`；被剔走嗰條係重複行 + 死連結（全檔唯一一條 vertexaisearch AI 轉址殘留）。刪重複行即可，158 不變。**兼更正我上半場嘅錯**：我曾把 `religious_edu_jss` 改名成 2024 版而製造 registry 重複，已改回 `superseded` 並寫低來龍去脈。
- **一個我做錯咗嘅改動（⑦，已還原，值得記低）：** 我用「ANN pool 可達性」probe（whole-index top-40、min_score 0.22）判定 4 個 spotlight 源可以剪，4 個都 rank 0。但 before→after eval 顯示 `ai_intro`／`net_scholar`／`pay_adjust` PASS→FAIL，失去嘅正正係被剪嗰 3 個。**根因＝probe 唔忠實**：我用自己揀嘅描述性 phrasing（「人工智能初探 學與教」）測，而真正重要嘅係裸名詞（「人工智能初探」）；加上生產路徑會先 query-expand 再 embed，probe 睇到嘅候選池根本唔係生產嘅池。**教訓：用自己揀嘅寬鬆 phrasing 測「搵唔搵得到」，量度緊嘅係 phrasing，唔係檢索。** 已全部還原 + 寫喺 `SPOTLIGHT_SOURCE_IDS` 上面，下次要剪必須由 eval 對開始。
- **做唔到（④）：** `PUBLISH_PAT` scope 只可以喺 Leonard 嘅 GitHub 帳戶 Settings → Developer settings → Personal access tokens 睇；API 唔會俾 token 自報 scope。
- **Pending：** 「校巴營辦商責任」被 governance route 搶走（route 次序問題，要自己一對 before→after 證據）；judge 選項 (c)「改良 judge prompt」未做，但 `judge_probe.py` 已可作為驗收工具。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S195 下半 block；四份 eval run + judge probe 輸出→`dev/source/eval_runs/`（commit，跨 session 可比）；門檻實測→code 註釋（唔止留喺 log）；spotlight 教訓→`SPOTLIGHT_SOURCE_IDS` 註釋；每條 registry 改動理由→各條目 `notes`；監察 diff 設計→`FRESHNESS_GUIDE` §0。
- **Sync:** DOC_SYNC 命中 4 row（Channel-B vault backfill ✓ registry+SOURCE_SETS parity+eval 對／檢索 eval harness 改動 ✓ eval_queries 25→30＋4 份 run／Monitoring-CI change ✓ FRESHNESS_GUIDE＋新 workflow＋無新 secret／guidelines.json 契約 ✓ `--write` 重生、158 不變）。`update_log.json` +3 條（今次係真內容改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 隨 push redeploy。
- **Risks:** ⚠️ 「校巴營辦商責任」route 次序問題未修。⚠️ g24／sag_2025_11 仍然係同一份學校行政手冊登記兩次、**215 條 chunk 文字完全相同**（今次查到嘅新數字）—— 呢個先係 eval tie 嘅真來源，但 Backlog 舊決定係「軟 dedup 已足夠」，未動。⚠️ Render free tier 偶爾 57014 statement timeout（今次 eval 中段撞過一次，harness 正確記做 error 而非零結果）。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check` → **trigger=False**（line_count=331 / entry_count=5，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 本 session 屬「多選項取捨並記低理由」＋「跨 session 累積模式」，已按 §4 step 11(c) append `dev/PROJECT_DECISIONS.md` Insights（三條教訓，帶證據鏈）。10-closeout backstop：未到（archive 上次 S194 執行，現 5 entries）。
- **Playbook（§14）:** 本輪經驗夠穩定且可轉移，已交兩份提案入共用經驗庫 inbox（`2026-07-28-policychecker-content-hash-id-delete-set.md`／`2026-07-28-policychecker-self-authored-probe-measures-your-assumptions.md`）＋開咗 `usage/policychecker.log.md`（4 行，3 條 applied）。playbook repo commit `ee70298` 已 push。未改該庫任何卡或 INDEX（按 §14 規矩由 librarian 處理）。

<!-- ack:log-entry:end -->

---

## 2026-08-18 Session 205 — OP① 收尾：route-probe 兩次讀齊、零外部呼叫、probe 已刪

- **ID:** Claude_20260818_1400
- **Summary:** 起手探針 6/6 綠後直接清 Open Priority ①（由 7/30 賴到今日嘅臨時觀測 code）。交接寫嘅二選一（(a) 直接刪 / (b) 重開新窗）其實有第三個更好選項：probe 由 7/30 連續行到今日冇停過，而 Render Hobby 係 **rolling** 7 日保留，所以 dashboard 一直坐住一個現成嘅 8/11→8/18 七日窗，唔使等、唔使重開，只係之前冇人去讀。讀完即刪。單檔 32 行純刪除。
- **① 起手探針（6/6）:** 服務中 `app.html` `PLATFORM_VERSION='3.3.0'`；Render `/health` warm 455；Draft tree 乾淨 + HEAD==origin/main @ `fa7c9fe`（0/0）；Supabase `wiki_chunks` `count=exact` = **17,472**；`source_registry` 268（262 verified / 3 deprecated / 2 superseded / 1 held_back）；`GUIDELINES_REGISTRY` 177（實數 app.html 陣列）；凍結合約 `_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158 零漂移。`/api/stats/usage` = `total:0, today:0, since:2026-08-18`（計數器 S204 先上線，未有非-probe 真實流量；唔係故障）。
- **② 交接框架修正（本 session 主要判斷）:** handoff 寫「(b) 重開新觀察窗再讀一次」隱含咗「窗已經冚咗」。實際 git 歷史證明 probe 只有一個 commit（`ddc98d5` 7/30）、之後零改動、HEAD==origin/main 且 Render auto-deploy on push → **佢連續 live 咗 19 日**。Rolling 保留 = 任何時刻都有最近 7 日。所以「重開新窗」係一個唔存在嘅成本。
- **③ 儀器對照先行（S198 紀律落地，第三次）:** 落結論前先 curl 兩條 route 帶 `ua=s205-control-probe`（14:06:58–59 UTC）。Leonard dashboard「Last 7 days」search `route-probe` → 只得嗰兩行，時間 15:06:59（dashboard UTC+1，對到秒；UTC+1 第四度實證）。**先證儀器活住，再數零。**
- **④ 兩次讀合併結論:** S202 8/2 讀＝7/30 09:40 UTC→8/2 共 26 行全部自測（24× `s198-deploycheck-*` + 2× `s201-control-probe`）；S205 8/18 讀＝8/11→8/18 共 2 行全部自測。合共十日、兩次獨立讀、零第三方 → `/api/search/channel-a` 同 `/api/search/combined` 確認零外部呼叫者。S203 要求嘅 8/5 第二次讀確係走漏，7/30–8/11 嗰段永久冇咗，但唔影響結論（現窗更長更乾淨：期間 S203 純文件、S204 全部帶 `x-probe` 或打 channel-b）。
- **⑤ 閂數紀律（本 session 第二次落地）:** Leonard 第一次回覆係「應該一行都冇」——「應該」係期望語氣唔係觀察語氣。冇當佢係確認，追問咗一句「已經睇咗定係照推斷」，得到「已經睇咗、真係一行都冇」先落結論。呢個正正係 S197／S198 蝕過兩次嘅同一個坑（將期望當觀察），今次喺**用戶回覆**呢一層再中一次未遂：放咗四個標記專登為咗俾人睇有定冇，若果最後靠推斷閂數，標記就白放。
- **Changed:** `backend/src/server.ts`（刪 169–200 行＝S198 probe 註解 block + `if` block，32 行純刪除；`getClientIp` / rate limiter / CORS / 其餘 route 零接觸；留低嘅 `PROBE_HEADER` 係 usage counter 嘅 `x-probe`，無關）。commit `a1a6442`，push `fa7c9fe..a1a6442`。
- **QC:** `npm run check` exit 0；`npm run build` exit 0；`grep -c route-probe dist/server.js` = **0**；`git diff --stat` = 1 file / 32 deletions（證明零附帶改動）。部署後 `/health` 仍 `ok:true` warm 455、兩條 route 行為不變（GET → 404，同刪之前一樣）。**帶序號部署後自測流量四發已放並經 Leonard 讀實＝零行**：`s205-postdeploy-probe` 14:15:05 + 14:17:32 UTC、`s205-final-probe` 14:17:03 + 14:22:28 UTC（dashboard 15:15:05 / 15:17:03 / 15:17:32 / 15:22:28，UTC+1）。最後一發喺 push 後十四分鐘，deploy 必已落地故為最硬判準。Leonard search `route-probe`：**15:06:59 嗰兩行 `s205-control-probe`（刪除前）之後，一行都冇** → 新版真係落咗地、probe 生產上已死。分四個時間點放係為咗分開「deploy 遲少少」同「刪除未生效」——單一標記分唔到。
- **Evidence disposition:** 「rolling 保留窗＝唔使重開」呢個推論 → 已寫入 handoff opening message，並值得日後升做 playbook 卡（觀測窗類）；probe 兩次讀數 → kept as trace evidence（本 entry）；OP① 本身 → 已從 handoff Open Priorities 移除。
- **Sync:** DOC_SYNC_CHECKLIST row 48「臨時觀測 code 加落既有 backend route」＝ 本次係該 row 生命週期嘅**收尾**（該 row 原本要求 handoff 寫明刪除責任 + 觸發條件 + 讀取日期 + 自測識別標記，四項今次全部兌現）。CODEBASE_CONTEXT AI Maintenance Log 已補一行。凍結合約零接觸。
- **Pending:** ⚠️ `START_NEXT_SESSION_PROMPT.txt` 仍係 S204 版，同已更新嘅 handoff opening message 有意 drift，**收工時要重生 + mirror check**。（部署後 live 讀已閂 —— 見 QC。）
- **Risks:** 拆 backend channel-a 半邊（Backlog ⑥）前置已解鎖，但未做。指引庫落後 102 個來源（現 OP②）未動。
- **Log maintenance:** `session_log_maintenance.py --check` → `trigger=False line_trigger=False date_trigger=False`（line_count=301、entry_count=7、最舊 entry 2026-07-30 <30 日）→ **no-op**。
- **治理缺口（本 session 發現，不追溯補寫）:** S204 closeout 冇寫 `State Reconciliation Check` 條目 —— 該節由 S205 直接接 S203。唔補寫係因為重建唔到當時嘅 reconciliation，砌返一段等於偽造證據；已記入 handoff `Handoff Sufficiency Check` 作已知缺口。

---

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S205, 2026-08-18): HEAD bee54c9; 平台 v3.3.0; Supabase 17,472 chunks; source_registry 268;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S205 = 清 Open Priority ① (S198 route-probe 兩次讀齊、零外部呼叫、probe 已刪、部署後讀已閂)。
S204 (同日較早) = 人手編制文件群入庫 + 頁碼歸屬修正 + v3.3.0 + 累積計數器 + tab 開關機制。

自動化 active: 5 源監察 (discover / freshness / served-url / 封面核對, 每週一) + Option A 自動入庫管道
(edb-knowledge-ops, 每日跑; 會自行 push main 並更新片段數)。開工時本地可能落後 origin/main —— tree 乾淨
+ 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase (S204 撞過一次, 管道同時改 searchChannelB.ts)。

✅ S198 route-probe 全條線已閂 (唔使再翻)。兩次獨立讀皆零外部呼叫: S202 8/2 讀 7/30→8/2 共 26 行全自測;
  S205 8/18 讀 rolling 七日窗 8/11→8/18 共 2 行 = 當日親手放嘅 s205-control-probe。probe 已刪 (a1a6442,
  server.ts 169–200 共 32 行純刪除)。部署後四個帶序號標記全部冇出現 = 新版真落地。
  **拆 backend channel-a 半邊 (Backlog) 前置由此解鎖, 未做。**

⚠️⚠️ 貫穿全局 (S199 用真金白銀學到): judge / synthesis 用嘅 model 唔係 code default。
  env.ts fallback 係 gpt-4.1-nano, 但 Render 實設 OPENAI_MODEL=gpt-4o-mini。/health 唔報 model。
  任何 judge/synthesis 量度, 引用做「生產行為」之前必須去 Render dashboard 確認。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」搵已發生事件做對照組。
     (S205 第三度落地: 先放 s205-control-probe 證儀器活住, 先數零。)
  3. 報一個數之前打開數字背後至少一個實例親眼睇。搜尋命中唔算證據。
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
  7. 入庫 ≠ 可達。SOURCE_SET / TOPIC_KEYWORDS / SPOTLIGHT / route expansion 四層任何一層唔啱都搵唔到,
     每層都要實測先知。假設要逐個測。
  8. (S205 新增) 交接寫低嘅選項框架本身可以係錯 —— 落手前先驗前提。S205 交接叫二選一「刪 / 重開觀察窗」,
     但 Hobby 七日保留係 rolling、probe 連續 live 十九日, 現成七日窗一直喺 dashboard 等人讀,
     「重開新窗」根本係唔存在嘅成本。
  9. (S205 新增) 「應該冇」唔係「冇」。用戶答「應該一行都冇」係期望語氣, 唔可以當觀察閂數;
     追問一句「已經睇咗定係照推斷」先落結論。放咗標記就係為咗有嘢俾人睇。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/eval_retrieval.py --compare <before.json> <after.json>
  python3 dev/vault/extract_table_rows.py --self-test ; --source <id> --dry-run
  python3 dev/vault/expand_vault.py --embed --force --sources <id>      # --force 繞過 wiki_index 已索引跳過
  python3 dev/source/judge_acceptance.py --self-test ; --plumbing-check
  cd backend && npm run check && npm run build
  curl -s https://edb-knowledge.onrender.com/api/stats/usage

🔜 NEXT (Open Priorities ①–④ 詳見 handoff; §3 項目全部要 PLAN + Leonard go):
  ① 檢索「可見 ≠ 見到啱嗰段」+ synthesis 只讀 5 條 vs 榜有 8 條。S204 錯答嘅直接成因。
     兩個修法 (改 spotlight 條件為「最佳 chunk 未出現先插」/ 擴合成窗) 都要 eval before→after。
  ② GUIDELINES_REGISTRY 落後 102 個來源 + 加 registry-drift 監察 (Leonard 明確要求)。
  ③ 特殊學校編制表恢復 (等「資料對象 vs 問題對象」核對機制)。
  ④ 表格 / 註解 content_kind 分類 —— 方向已定「指路唔係砌表」, 前端零改動靠現有 #page=N。
  Backlog: 拆 backend channel-a 半邊 (S205 已解鎖前置); 時限性資料標示 + 第 6 監察; 公眾提交表單
  (Phase 1 Google Form); 範本 manifest 更新後開返 FEATURE_TABS.templates; 真亂碼未量度;
  承 S203 (judge 對象移植機制 / Channel A Option 2 / PUBLISH_PAT / 總帳 / g24-sag 合併)。
  Playbook inbox 未交: S205 兩條可轉移經驗 (rolling 保留窗唔使重開 / 期望語氣唔等於觀察)。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 + Draft HEAD==origin/main (落後就 ff-pull, 有本地 commit 就 rebase) + Supabase count=exact
(應為 17,472) + GET /api/stats/usage (S204 上線, 現值可能仍為 0) —— 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-08-18 Session 204 — 人手編制文件群入庫 + 頁碼歸屬修正 + v3.3.0 + 累積計數器

- **ID:** Claude_20260818_1115
- **Summary:** 由一個真實用戶問題（「學校有幾多班就有幾多老師／校工」答唔到）拆到底：實證係 ingestion gap（256 源零覆蓋人手編制），修完入庫仲要再修路由、spotlight、query expansion、chunk 粒度四層先真正可達。期間發現並回滾一個自製嘅移植性錯答。另完成 v3.3.0 顯示同步、累積使用計數器、beta 標示、可重用 tab 開關。
- **① 頁碼歸屬（ship）：** `extractFirstPage` → `extractDominantPage`。舊邏輯取 chunk 第一個 `=== Page N ===`，跨頁時報錯頁（實例：g24 某 chunk 96% 屬 p53、因尾 5 字有 p54 標記而報 54）。新邏輯取承載最多內容嗰頁。真 PDF 核對：g24 74.1%→147/147、kg_admin 63.0%→127/127；全庫 15,601 條有頁碼者 **5,453（35%）改變**（4,927 條 −1）。`page` 唔入 scoring／唔入 synthesis prompt，故只影響頁碼同 `#page=N` 深連結。
- **② graduate-teacher-posts 文件群（ship）：** registry 257→**268**；vault extract 11 份；Supabase 16,070→17,414→（回滾 sp + 逐行重入）**17,472**。新增 `dev/vault/extract_table_rows.py`（座標重建表格 + 算術不變式守門，72/48 行零失敗）；`expand_vault.py` 加 registry 覆寫 `chunk_cap`（則例全量 509/700，預設 300 會截走含 clerical 條款嘅尾段）同 `chunk_max_chars`（表格源 160＝一行一 chunk）。
- **③ 可達性要四層（教訓）：** 入庫後 live 仍然搵唔到 → (a) 加入 `hr_admin` SOURCE_SET；(b) `TOPIC_KEYWORDS` 從來冇「編制」詞；(c) 加 SPOTLIGHT（ANN over-fetch 喺 SOURCE_SET 過濾之前，15 條 chunk 嘅源要全球排前 40 先入窗）；(d) 開獨立 `staffing` route 避開 `hr_admin` 嘅假期/薪酬 expansion（實測令編制查詢 cosine 0.816→0.616）＋逐行 chunk（0.521→0.590）。最終四條查詢全部由 <0.60 升到 0.607–0.816 過閘。
- **④ 移植性錯答（自製→回滾）：** 特殊學校小學部編制表入庫後，合成器將其「教學人員總數=36」行套落普通小學「12班」問題，連續 3 runs 答 12 名（正確 5 名）。機制：staff_est_pri 分數更高（0.654 vs 0.650）但排第 6，而 synthesis 只讀 `results.slice(0,5)`。已刪其 28 條 chunk（`status=held_back`，恢復條件寫入 registry notes），回滾後同一查詢 3/3 回復安全 decline。
- **⑤ v3.3.0 + 顯示同步：** chunks 16,070→17,472（用 executor 自己嘅 `live_display_sync` 掃 7 個鏡像檔）、`sources` 120→**288**（積壓漂移，= Supabase distinct source_id 295 − 7 個 role_facts_* 偽來源）、`GUIDELINES_REGISTRY` 166→**177**（新 sub_category `establishment`）。PLATFORM_VERSION 3.2.2→3.3.0 + README badge/footer + index footer + CHANGELOG 新段（只 append）。
- **⑥ 累積計數器（新功能）：** Leonard 貼 DDL 建 `usage_daily` + `bump_usage()`/`get_usage_total()`（SECURITY DEFINER）。後端新增 `lib/usageCounter.ts` + `GET /api/stats/usage`，搜尋成功後 fire-and-forget 計數；帶 `x-probe` 唔計（三個 harness 已加，`eval_retrieval` 一跑 34 次會灌水）。前端：平台介紹第 5 張卡 + 手機 hero 行。
- **⑦ 快取修正：** `mobile.js`/`mobile.css` 從來冇版本參數，回訪瀏覽器一直行舊版（實測服務端有新 code 但 `transferSize:0`）。四個 HTML 全部加 `?v=3.3.0`。
- **⑧ beta 標示 + tab 開關：** 文件標註(beta)／範本下載(beta)；新增 `window.FEATURE_TABS`（head 普通 script，因 mobile.js 喺 Babel 編譯前初始化）。`templates:false` 一次過收起：桌面掣、`VALID_VIEWS`（bookmark #templates 退回 qa）、手機底欄、導覽步驟（6→5）、index 功能卡。面板 code 原封不動，開返 flag 即復原。**⚠️ 出咗兩次 commit：** 第一次係逐個手動 gate，漏咗平台介紹嘅核心功能卡同使用手冊摺疊（Leonard 截圖捉到）。第二次改成結構性——`channels` 同手冊條目各帶 `view` key 一齊 filter，加新 tab 自動跟開關。**規律已成文：** 開關註解列晒全部 7 個受影響位（第 7 個 index.html 係靜態 HTML、唯一唔係 flag 驅動，特別標明）+ 恢復程序；`DOC_SYNC_CHECKLIST.md` 新增一行「Tab withdraw / restore」載同一清單 + headless 驗證方法。
- **Changed:** `backend/src/api/searchChannelB.ts`、`backend/src/lib/usageCounter.ts`(NEW)、`backend/src/server.ts`、`dev/vault/extract_table_rows.py`(NEW)、`dev/vault/expand_vault.py`、`dev/source/source_registry.json`、`app.html`、`index.html`、`mobile.js`、`q.html`、`t-purchase.html`、`README.md`、`CHANGELOG.md`、`K1_API_SPEC.md`、`knowledge.json`／`role_facts.json`／`dev/knowledge/role_facts.json`(只 `_meta.stats`)、三個 harness(+`x-probe`)、11 個 vault extract。
- **QC:** eval before→after 兩次都 PASS=23/FAIL=0/errors=0；diff 31 條相同、1 SET_LOST（`substitute` 第 8 位互換，synthesis 只讀 5 條故影響唔到答案）、1 SET_ADDED（`mpf` +資助則例，改善）、1 RANK_SHIFT。路由 15/15（9 條回歸）。頁碼函數 7/7（2 條真 chunk 對真 PDF + 5 邊界）。計數器 live 3 測（讀取／+1／x-probe 唔計）。headless render 驗 V3.3.0、EDB指引(177)、17,472、零殘留 3.2.2。`npm run check`／`build` 全綠。
- **Evidence disposition:** 可達性四層教訓 + 移植失效實例 → handoff Open Priorities；表格抽取方法 → `extract_table_rows.py` docstring；計數器機制 → `usageCounter.ts` docstring；eval run 檔 kept as trace（`eval_runs/2026-08-18_s204_before/after.json`）。
- **Sync:** DOC_SYNC「Product version / release milestone」+「Product behavior / tuning」兩行已執行。凍結合約零接觸（`knowledge.json._meta.version` 2.3.0 / facts 455 / guidelines.json 2.6.1/158）。
- **Pending:** 見 handoff Open Priorities（spotlight 可見≠啱段、synthesis 5 vs 8、指引庫落後 102、sp 表恢復、時限性資料、表格/註解分類、公眾表單、範本 manifest、**S198 route-probe 觀察窗已過期但 probe 仍 live**）。
- **Risks:** 🔴 `backend/src/server.ts:193` route-probe 由 7/30 起仍喺生產（S203 交接嘅 8/5 讀取窗已過，Hobby 7 日 log 早已滾走）。⚠️ 指引庫落後 102 個來源，用戶搜到但瀏覽唔到。
- **Log maintenance:** `--check` trigger=False（169 行 <400，最舊 entry 2026-07-30 <30 日）→ **no-op**。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S204, 2026-08-18): 平台 v3.3.0; Supabase 17,472 chunks; source_registry 268;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S204 = 人手編制文件群入庫 + 頁碼歸屬修正 + v3.3.0 + 累積計數器 + tab 開關機制。

自動化 active: 5 源監察 (discover / freshness / served-url / 封面核對, 每週一) + Option A 自動入庫管道
(edb-knowledge-ops, 每日跑; 會自行 push main 並更新片段數)。開工時本地可能落後 origin/main —— tree 乾淨
+ 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase (S204 撞過一次, 管道同時改 searchChannelB.ts)。

🔴🔴 最舊未清: backend/src/server.ts:193 一段 S198 route-probe 由 7/30 起仍喺生產。
  S203 交接要求 8/5 前讀第二次 —— 該窗已過期, Render Hobby 只留 7 日 log, 7/30–8/2 嗰段永久冇咗。
  要 Leonard 決定: (a) 直接刪 probe (8/2 全窗綠係唯一證據), 或 (b) 重開新窗再讀一次。
  刪咗 = 拆 backend channel-a 嘅前置。呢個係 Open Priority ①。

⚠️⚠️ 貫穿全局 (S199 用真金白銀學到): judge / synthesis 用嘅 model 唔係 code default。
  env.ts fallback 係 gpt-4.1-nano, 但 Render 實設 OPENAI_MODEL=gpt-4o-mini。/health 唔報 model。
  任何 judge/synthesis 量度, 引用做「生產行為」之前必須去 Render dashboard 確認。

📋 S204 做咗 (全部已 deploy 並 live 驗證):
1. 頁碼歸屬: extractFirstPage → extractDominantPage。真 PDF 核對 g24 147/147、kg_admin 127/127
   (舊 74.1% / 63.0%); 全庫 5,453/15,601 (35%) 頁碼改變。page 唔入 scoring/synthesis。
2. 資助小學學位教師文件群 10 份入庫 (+1,344 chunks, 16,070→17,472); 新 dev/vault/extract_table_rows.py
   座標重建表格 + 算術不變式守門 (72/48 行零失敗); expand_vault 加 per-source chunk_cap / chunk_max_chars。
3. 可達性四層: hr_admin SOURCE_SET + TOPIC_KEYWORDS 新「編制」詞 + SPOTLIGHT +7 + 獨立 staffing route
   (避開令 cosine 跌 0.20 嘅 hr_admin expansion) + 逐行 chunk。四條查詢由 <0.60 升至 0.607–0.816。
4. v3.3.0 + 顯示同步 (chunks 17,472 / sources 120→288 積壓漂移校正 / 指引 177)。
5. 累積計數器: usage_daily + bump_usage()/get_usage_total() (SECURITY DEFINER, anon EXECUTE);
   後端 lib/usageCounter.ts + GET /api/stats/usage; x-probe 排除自測 (三個 harness 已加)。
6. mobile.js/css 加 ?v=3.3.0 (回訪瀏覽器一直行舊版, 實測 transferSize:0)。
7. window.FEATURE_TABS tab 開關 (head 普通 script, 因 mobile.js 喺 Babel 編譯前初始化);
   templates:false 一次過收起五個入口。開返 flag 即復原, 面板 code 原封未動。

🔴 S204 自製又回滾嘅嘢 (教訓): 特殊學校小學部編制表入庫後, 合成器將其「教學人員總數=36」行
   套落普通小學「12班」問題, 3/3 答錯 (12 vs 正確 5)。機制: staff_est_pri 分數更高 (0.654 vs 0.650)
   但排第 6, 而 synthesis 只讀 results.slice(0,5)。已刪 chunk (status=held_back, 恢復條件寫入
   registry notes), 回滾後同一查詢 3/3 回復安全 decline。**令系統答到嘢, 可以係退步。**

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」搵已發生事件做對照組。
  3. 報一個數之前打開數字背後至少一個實例親眼睇。搜尋命中唔算證據。
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
  7. (S204 新增) 入庫 ≠ 可達。SOURCE_SET / TOPIC_KEYWORDS / SPOTLIGHT / route expansion 四層
     任何一層唔啱都搵唔到, 每層都要實測先知。假設要逐個測 —— S204 有三個假設 (Q&A 格式、chunk 被切爛、
     mojibake 2.4%) 測完都唔成立。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/eval_retrieval.py --compare <before.json> <after.json>
  python3 dev/vault/extract_table_rows.py --self-test ; --source <id> --dry-run
  python3 dev/vault/expand_vault.py --embed --force --sources <id>      # --force 繞過 wiki_index 已索引跳過
  python3 dev/source/judge_acceptance.py --self-test ; --plumbing-check
  cd backend && npm run check && npm run build
  curl -s https://edb-knowledge.onrender.com/api/stats/usage

🔜 NEXT (Open Priorities ①–⑤ 詳見 handoff; §3 項目全部要 PLAN + Leonard go):
  ① 🔴 route-probe 決定 (刪 / 重開新窗) —— 只有 Leonard 睇到 Render logs。
  ② 檢索「可見 ≠ 見到啱嗰段」+ synthesis 只讀 5 條 vs 榜有 8 條。今日錯答嘅直接成因。
     兩個修法 (改 spotlight 條件 / 擴合成窗) 都要 eval before→after。
  ③ GUIDELINES_REGISTRY 落後 102 個來源 + 加 registry-drift 監察 (Leonard 明確要求)。
  ④ 特殊學校編制表恢復 (等對象核對機制)。
  ⑤ 表格 / 註解 content_kind 分類 —— 方向已定「指路唔係砌表」, 前端零改動靠現有 #page=N。
  Backlog: 時限性資料標示 + 第 6 監察; 公眾提交表單 (Phase 1 Google Form); 範本 manifest 更新後開返
  FEATURE_TABS.templates; 真亂碼未量度; 承 S203 (judge 對象移植機制 / Channel A Option 2 / PUBLISH_PAT /
  拆 backend / 總帳 / g24-sag 合併)。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 + Draft HEAD==origin/main (落後就 ff-pull, 有本地 commit 就 rebase) + Supabase count=exact
(應為 17,472) + GET /api/stats/usage —— 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

<!-- ack:log-entry:end -->

---

## 2026-08-02 Session 203 — ⑩ 文件 drift 清 + ② judge V4 量度（未 ship）+ ⑧ g24/sag 偵查（出 PLAN）

- **ID:** Claude_20260802_S203
- **Summary:** 起手探針 4/4 綠（Supabase `count=exact` 實核 16,062）。Leonard 揀「1+2」再續「B→⑧」。完成三件：⑩ 文件 drift 修好（純文件）、② judge V4 量度完成（Phase A+B，**未 ship**，reframe）、⑧ g24/sag 重登偵查（純唯讀，出 PLAN）。**零生產改動**：生產 judge prompt byte-identical、Supabase 零寫入、v3.2.2/凍結合約零接觸。
- **⑩ 文件 drift（完成）:** Leonard 確認方向＝「下游轉 Channel B 已完成」（依 S146 Leonard 確認 + S202 route-probe 零 channel-a 流量佐證）。改 `PROJECT_MASTER_SPEC.md`（line 49 Phase 2 狀態、line 262 Phase 2 + S145 endpoint 狀態）、`SYSTEM_ANALYSIS_AND_ROADMAP.md`（R1 摘要行 / dormant 包袱 §96 / R3 段 136-141 / 依賴表 214，共 5 處）、`HANDOFF_PACKAGE.md:32`（mobile endpoint combined→channel-b）。grep QC：stale 措辭殘留清零。
- **② judge V4 量度（完成，未 ship）:** Phase A（離線）造 `judge_prompts/v4a_s202.txt`(+8 最小)／`v4b_s202.txt`(+75 明示)（由 v3 base 程式生成，只差指定區）+ fresh held-out 集 `judge_transplant_fresh_s202.json`（10 條，7 移植/gap + 3 對照；逐條讀 5 passage 落 label，**0 flip**）+ harness `judge_acceptance.py` 加 `--cases`/`--cache` override（additive，frozen 不污染）。Phase B（Leonard dashboard reconfirm `gpt-4o-mini`）：`--plumbing-check` 綠 → fresh 集 score V3/V4a/V4b（全 9/10、同漏 FT06、答半 3/3）→ frozen-35 score V4a/V4b + **同 session V3 rebaseline** → 再 V3×2 / V4b×2 = **7 runs 噪音控制**。**定案**：V4b 穩修 GN10（false 0/3 vs V3 4/4）、答半 7 runs 全 12/12（零 recall 損）、但 **D01 3/3 + fresh FT06 照漏**（對象移植頑固）；V4a=V3（淘汰）；GN03 噪音（V3 2/4、V4b 1/3，prompt 無關）。**結論：prompt-only 槓桿掂到明示範圍移植、掂唔到隱含對象移植 → 建議唔 ship、② reframe 做非-prompt 對象核對機制。**
- **⑧ g24/sag 偵查（完成，出 PLAN）:** 親眼驗 Supabase（服務 key REST）：g24 383 / sag_2025_11 409、**正規化文字重疊 377**（推翻 handoff/PMS-era doc/searchChannelB.ts:415/code comment 全部「215」或「sag415·g24300」）、shared chunk ID=0、**g24 零獨有內容**（6 條 g24-only 內容 sag 全語義覆蓋：拭抹試驗/疏散/署任津貼/精神上無行為能力人士/胸肺 全 YES）、封面實寫「2026年5月版」。g24 被 `role_facts.json:694`（general._source_refs）+ `eval_queries.json`（mpf gold + `_tie_aliases`）引用，兩處都同 sag 並列 → remap 乾淨。合併 PLAN 6 步已入 Open Priorities ⑧。
- **Changed:** `dev/PROJECT_MASTER_SPEC.md`、`dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`、`dev/HANDOFF_PACKAGE.md`（⑩）；`dev/source/JUDGE_PROMPT_FINDINGS.md`（S202 段 + Still-open 更新）、`dev/source/judge_prompts/v4a_s202.txt`＋`v4b_s202.txt`（NEW）、`dev/source/judge_transplant_fresh_s202.json`（NEW）、`dev/source/judge_acceptance.py`（+`--cases`/`--cache`）、`dev/source/judge_runs/2026-08-02_s202_*`＋`chunks_cache_fresh_s202.json`（NEW，量度證據）（②）；handoff/log（closeout）。**無 backend production code / 無 Supabase 寫入 / 無 registry / 無 knowledge.json 改動。**
- **Done:** ⑩ 完成；② 量度完成 + findings 記錄 + reframe；⑧ 偵查完成 + PLAN 備妥。
- **QC:** 起手探針 4/4 綠；⑩ grep 殘留清零；② `--self-test`(frozen+fresh 各 0 fail)／`--check-parity`(byte-identical，生產 prompt 未動)／`--plumbing-check`(能) + 7 runs；⑧ 純唯讀 Supabase REST + 語義覆蓋驗證。
- **Evidence disposition:** ② 量度定案 + 方法論 promoted to `JUDGE_PROMPT_FINDINGS.md` S202 段（+ fresh 集 `_meta`、V4a/V4b、harness）；judge 非決定性教訓 → handoff opening message 🧭 紀律 #6；⑧ 真數 + PLAN → Open Priorities ⑧（執行前檔）；run 檔 kept as recent trace evidence（`judge_runs/2026-08-02_s202_*`）。
- **Sync:** ⑩ 純文件（非 code/retrieval/synthesis-gate）→ DOC_SYNC 無命中 code category；② V4 未 ship（parity 綠）；⑧ 純唯讀。凍結合約 + PLATFORM_VERSION 零接觸。Render/Pages 零 deploy。
- **Pending:** ① route-probe 8/5 讀 + 刪 probe；② 非-prompt 對象核對機制（reframed）；③ Channel A Option 2 入庫；⑧ 執行合併（HIGH risk 等 GO）；其餘見 Open Priorities S203 段。
- **Risks:** 🔴 生產度臨時 probe（`server.ts:168–198`）仍 live，8/5 讀完必刪（不變，V4 未 ship 無新增生產 risk）。⚠️ ⑧ 執行時 `searchChannelB.ts:415` + `wikiRepository.ts` 註解 stale 數（215/415/300）待一併清（已入 PLAN 步 ⑥）。
- **Log maintenance:** §4a `--check`：SESSION_LOG 145 行（<400）、最舊 entry 2026-07-30（<30 日）→ **no-op**（S202 已維護至 122，S203 +1 entry）。

### Next Session Handoff Prompt (Verbatim)

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S203 收工已就地更新為 S203 版〔state header S203 / 三件事 ⑩·②·⑧ / NEXT ② reframe / NEXT ⑧ 真數 377+PLAN / NEXT ⑩ DONE〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-08-02 Session 202 — NEXT ① route-probe 觀察窗第一次讀（8/2）＝全窗綠，零外部呼叫

- **ID:** Claude_20260802_S202
- **Summary:** 起手探針 4/4 綠。執行 NEXT ① S198 route-probe 觀察窗第一次讀（Leonard 喺 Render dashboard 讀、Claude 遠端放對照訊號協助）。**結果：由 2026-07-30 09:40 UTC 到 8/2，兩條 channel-a route（`/api/search/channel-a`、`/combined`）零外部呼叫。** 零 code / 零 Supabase / 零 route 改動 —— 純唯讀量度 ＋ handoff checkpoint。commit `2ec82cf`。
- **量度（route-probe 8/2 讀）:** Render Logs「Last 7 days」search `route-probe`：全窗 **26 行全部有主** ＝ 24× `s198-deploycheck-*`（7/30 Leonard 自測）＋ 2× `s201-control-probe`（8/2 Claude 為驗儀器親手放）。零第三方、零非自測 `origin`/`ua`。s198 最早行 7/30 10:40:48 AM（dashboard UTC+1）＝ 09:40:48 UTC，啱好對正觀察窗起點；instance `p2znr`/`26wlj` 對返 S198 紀錄。
- **儀器信心（S198 紀律落地）:** 頭先 search `route-probe` 空手 → **冇當「零流量」**（Render Hobby log negative ≠ 零事件）。先放 `s201-control-probe` 即時對照（curl 兩條 route，HTTP 404 但 probe 喺 `server.ts:190` 判 URL 時已印）→ 出到證儀器 work；再 search `s198` 用 7/30 已知事件回溯 → 首次空手係因「Last 7 days」時間範圍未 set，set 後 24 行全現形 → 證窗涵蓋返起點。雙對照齊先落結論。Hobby 保留 7 日、dashboard UTC+1 均第三度實證。
- **Changed:** `dev/SESSION_HANDOFF.md`（Current Baseline / Open Priorities / Last Session Record / State Reconciliation / Next Session Opening Message 五處 prepend 或重寫為 S202）；`START_NEXT_SESSION_PROMPT.txt`（由 opening message regen，mirror check byte-identical 107 行）；本 log（§4a 維護 ＋ 本 entry）。**無 code / 無 Supabase / 無 registry 改動。**
- **Done:** ① route-probe 8/2 第一次讀完成＝全窗綠；② handoff checkpoint push（`2ec82cf`）；③ §4a log 維護（4 舊 entry 搬 archive）；④ 收工 reconcile。
- **QC:** 起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main / Supabase 沿用 16,062）；probe 儀器 s198＋s201 雙對照證正常；START mirror check byte-identical；§4a `--check` trigger=True → `--apply` 成功（402→122，archive 只搬冇刪）。
- **Evidence disposition:** kept as recent trace evidence（量度證據＋儀器對照方法）；可重用教訓（Hobby log negative≠零事件、必先即時對照＋回溯已知事件驗窗）＝S198 既有紀律再落地，已在 handoff `Last Session Record` §6 ＋ opening message 🧭 #2，無新增 rule pack。
- **Sync:** DOC_SYNC 無命中（純唯讀量度）。凍結合約零接觸。Render/Pages 零 deploy。
- **Pending:** ① route-probe **8/5 第二次讀**（≤8/6 前）＋讀完刪 `server.ts:168–198` probe → 完成 NEXT ①、拆 backend route（⑥）前置；②–⑪ 見 Open Priorities S201 段不變（硬化 judge V4／Channel A Option 2 入庫…）。
- **Risks:** 🔴 生產度臨時 probe（`server.ts:168–198`）仍 live，8/5 讀完必刪。
- **Log maintenance:** §4a 觸發（402 行 > 400）→ `--apply`：402→122 行、entries 7→3，4 舊 entry 搬入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬冇刪，archive pointer 已在）。

### Next Session Handoff Prompt (Verbatim)

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S202 收工已就地更新為 S202 版〔route-probe 8/2 done·8/5 left、state header S202 / HEAD `2ec82cf`〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS〔107 行 byte-identical〕。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-31 Session 201 — NEXT ②：收 footnote judge-bypass（擴闊 decline 集 → 量度 → ship → deploy → live 驗）

- **ID:** Claude_20260731_S201
- **Summary:** 起手探針 4/4 綠。做齊 NEXT ② 一整條線:(b) 擴闊 judge decline 集 → 量 V3 baseline → 移走 footnote judge-bypass → deploy → live before→after 驗。**結果:footnote-lead gap query 由 live 砌數改為老實拒答,正經 footnote 答案零損失。** commit `fc287ff`(backend)deploy 已確認 live。Supabase 16,062 零寫入 / 凍結合約 / v3.2.2 / registry 256 全零接觸。
- **(b) 擴闊 decline 集:** handoff/findings 講「S199 撈咗 14 條 gap candidate」**從未持久化** → 重新 author 14 條,逐條打開 live top-5 passage 親眼讀先落 label。**11 gap + 3 answerable**,3 條逆假設 flip(GN06 gap→能、GN10 能→gap、GN12 gap→能)= passage 話事。入集:10 clean gap → decline **11→21**、GN11(採購>$200k,逐字答到)→ answer **11→12**;drop GN01(borderline);GN06/GN12 留做 findings。**D01 保留 decline**(Leonard domain 確認:學生病假醫生紙=校本要求、無 EDB 出處)。
- **量 V3 baseline(擴闊 35 條集, gpt-4o-mini, dashboard reconfirm):** `2026-07-31_s201_v3_widened.json` —— answer **12/12**(0 false decline)、decline **19/21**(2 false answer: D01 + GN10,**兩條都 transplant 類**)、D00 一票否決正確拒答。**answer 12/12 = 收 bypass 唔會整爛正經答案 → 淨贏**;D01/GN10 係 judge PROMPT 都捉唔到嘅主體/範圍移植,收 bypass 唔 touch(留 V4)。
- **CHANGE(收 bypass):** `searchChannelB.ts` `synthesizeAnswer` 移走 `trustedFootnoteLead`(連 `forcedFootnoteLeads` param/var/賦值一齊清);footnote lead 而家同其他嘢一樣過 V3。**保留:vault bypass(≥0.70)、footnote forced lead slot 排序、lexical gate、`RELEVANCE_JUDGE_PROMPT` 字串**。註解:retire S178 footnote-bypass 理由(D01 證偽)、寫入 S201。
- **Changed:** `searchChannelB.ts`(收 bypass,commit `fc287ff`);`judge_acceptance_cases.json`(+11 case,`_meta.widened_s201`);`JUDGE_PROMPT_FINDINGS.md`(Still open 更新 + S201 頭註);`judge_runs/chunks_cache.json`(35 cached)+ `judge_runs/2026-07-31_s201_v3_widened.json`(baseline run);`CODEBASE_CONTEXT.md`(footnote bypass 描述更新 + AI log);本 log + handoff。
- **QC:** `--self-test` 0 fail;`--check-parity` byte-identical(prompt 未郁);`tsc --noEmit` exit 0;零殘留 `forcedFootnoteLeads`/`trustedFootnoteLead` 引用;`footnote_lead_probe --run` **before==after: positive 30/30 / negative 5/13 / errors 0**(lead-slot 零回歸)。**live before→after(synthesize:true,生產)**:D17 消防演習 **ANSWER 砌數「每12個月」→ DECLINE**(flip ✅);D13 留位費 **ANSWER 970/1570 → 仍 ANSWER**(零退步 ✅);D01 學生醫生紙 **ANSWER → 仍 ANSWER**(V3 miss,維持現狀,pending V4 ✅)。
- **Evidence disposition:** 擴闊集 + label 出處 → `judge_acceptance_cases.json`(frozen);V3 baseline + live before/after 數 → 本 entry + run json(commit);可重用觀察(S199 14-candidate 從未持久化;label passage-driven;3 flip;footnote bypass premise 被 D01 證偽)→ FINDINGS + code 註釋;working scratch(candidate/chunks/labelled/live_check)留 scratchpad 未 commit。
- **Sync:** DOC_SYNC row 41(擴闊驗收集)+ **row 38(Synthesis 前置閘改動 —— 收 footnote bypass 正命中)**:footnote_lead_probe before→after 零損失 ✅、fail-open 保持(judge API error 仍 return true 答)、live 重探 ✅。`update_log.json` N/A。**Render deploy 已確認**(auto-deploy on push,live 驗 D17 flip 證實新 code 在跑);Pages 零改。
- **Pending:** **NEXT ②(新):硬化 judge V4 收 transplant 類(D01/GN10)** —— V3 主體/範圍移植捉唔到;⚠️ 喺已 frozen 嘅 35 條 acceptance set 上 tune 會燒 held-out,要另撈 fresh transplant 驗證集或原則性設計 + 一次量。其餘 handoff Open Priorities(③ Channel A Option 2 入庫、⑤ 8/2+8/5 route-probe 觀察窗、⑦ 拆 backend route…)不變。
- **Risks:** ⚠️ D01/GN10 transplant 類 live 仍會答(V3 判能;收 bypass 令佢哋去見 judge,但 judge 自己都miss → 要 V4)。⚠️ 收 bypass 令每條 footnote-lead query 多一個 judge call(+latency,同其他 query 一樣)。⚠️ S198 probe 仍 live,觀察窗 8/2 未到。
- **Log maintenance:** entry_count=6(<11)/ line_count<1500 → **trigger=False, no-op**。語意觸發:「curated footnote lead ≠ 答緊呢條 query」(D01 證偽 bypass premise)已寫入 code 註釋 + FINDINGS,唔另開 PROJECT_DECISIONS 避免重複。10-closeout backstop 未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— S201 收工已整份重生為 S201 版〔NEXT ① route-probe 觀察窗 8/2 時間閘、② 硬化 judge V4 收 transplant〕，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS〔111 行 byte-identical〕。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-30 Session 200 — ship judge V3（Open Priority ③；Leonard 揀 Option 2，明文閘 override）

- **ID:** Claude_20260730_1548
- **Summary:** 起手探針 4/4 綠（served v3.2.2 / Render `/health` warm 455 / HEAD==origin/main `30838f5` tree 乾淨 / Supabase count=exact 16,062）後，Leonard 揀 Open Priority ③「ship judge V3」。§3 HIGH risk + release gate + 撞到治理硬閘 → present PLAN + 三條路，Leonard 揀 **Option 2（照 ship + 明文 override）**。
- **Changed:** `backend/src/api/searchChannelB.ts`（`RELEVANCE_JUDGE_PROMPT` 換 V3 + 過時 寧緊莫鬆/5-5 rationale 註解重寫）；`dev/source/judge_acceptance.py`（`SHIPPED_PROMPT` 同步換 V3 保 `--check-parity`）；`dev/source/JUDGE_PROMPT_FINDINGS.md`（狀態頭 nothing shipped→SHIPPED + S200 override 記錄）；`dev/CODEBASE_CONTEXT.md`（judge_acceptance baseline 更新 + AI Maintenance Log S200）。commit `bcf7c4f` push origin/main。
- **Done:** V3 shipped（commit+push）。驗收證據＝`2026-07-30_s199_v3_4omini.json`（prompt 同 shipped code byte-identical，301 chars 已核）：primary 21/22、answer 11/11（收返 A02/A05/A06）、decline 10/11、D00 frozen-post=否、false=[D01]。
- **明文 OVERRIDE 記錄（AGENTS §2 rule 6）:** 衝突規則＝DOC_SYNC row 41 + `JUDGE_PROMPT_FINDINGS.md` bar「decline 半邊任何 false answer = 唔准 ship」。V3 有一個 false answer（D01）。override 理由：(a) 非退步（shipped 一樣 D01 答錯，`2026-07-30_s199_shipped_4omini.json`，零新增 false answer）；(b) 一票否決唔中（D00 正確拒答）；(c) D01 lead `footnote_curated` @0.574 > `FOOTNOTE_LEAD_SCORE` 0.45 → 生產行 footnote bypass、judge 從不 serve D01（harness 判係反事實）。risk：越過自己寫嘅閘＝precedent；緩解＝D01 明列 NEXT ④ 未修。
- **更正:** 交接 S199 ③「生產 model 已達…decline 全保」講多咗；artifact 實係 decline **10/11**（D01 漏），已於此記錄同 Current Baseline S200 ② 更正（comm 規則：corrected number 要同原數並存）。
- **QC:** `--self-test` 0 fail；`--check-parity` byte-identical；`--plumbing-check` 兩條 S177 scenario 叫得出「能」；`tsc --noEmit` exit 0；post-ship `footnote_lead_probe.py`（`2026-07-30_s200_postship_footnote.json`）positive **30/30 零損失**、negative 5/13、errors 0（=零回歸，V3 唔郁 bypass）。
- **deploy 已確認 live:** Leonard 貼 Render Events 綠剔「Deploy live for `bcf7c4f`: S200 ship judge V3」（4:50 PM UTC+1 = 15:50 UTC，對上 push）→ **V3 正式喺生產跑緊**。（收工當時外部驗唔到係因為 V3 差異 case 全 bypass judge、答案唔 flip；服務無 version endpoint。auto-deploy on push 已確立 S117。）
- **Evidence disposition:** absorbed into handoff（Current Baseline S200）；override rationale promoted to `JUDGE_PROMPT_FINDINGS.md` S200 header + `CODEBASE_CONTEXT.md`；run artifacts kept in `dev/source/judge_runs/`。
- **Sync:** DOC_SYNC row 41 required docs 全部已更（judge_acceptance.py / JUDGE_PROMPT_FINDINGS.md / CODEBASE_CONTEXT.md / SESSION_LOG / handoff Risks-in-baseline）；`--plumbing-check` 已跑、false-vs-accuracy 分開報、ship 後 footnote probe 已跑 —— row 41 checks 全數滿足。
- **Pending:** ① ~~deploy 確認~~ ✅ 已解（Leonard 貼 Render Events 綠剔 bcf7c4f）；② NEXT ② 收 footnote bypass（修 D01 live 錯 serve）—— 前置 (a) deploy 已解，仲剩 (b) decline 集擴闊 14 條 label 先入 §3 PLAN。
- **Risks:** 🔴 D01 live 仍錯 serve（未變，判 NEXT ②）；override 立咗「越 decline-half 閘」先例（需 NEXT ② 埋單）。deploy 傳播已確認 live（不再係 risk）。
- **Log maintenance:** §4a/N-rule trigger check（S200 收工執行）：SESSION_LOG 377 行（<400/<1500）、6 entries（<11）、最舊 2026-07-27（<30 日）→ **trigger=False → no-op**，未 archive。

（S200 收工完成：authoritative Next Session Opening Message 已於 `dev/SESSION_HANDOFF.md` 重生為 S200 版，`START_NEXT_SESSION_PROMPT.txt` 由該 block 重生並 mirror check byte-identical。）

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-07-30 Session 199 — Leonard 叫停 judge、問返 Channel A 退役實況；A(Channel A) 然後 B(judge)，純量度

- **ID:** Claude_20260730_S199
- **Summary:** 起手探針 4/4 綠後跟 handoff 揀 Open Priority ① 修 judge。做到量度階段 Leonard 叫停、問「Channel A 退役到底去到邊，唔好淨係『我錯了』」→ 我停低重構成 A(Channel A)然後 B(judge)。**純量度 session：零 Supabase 寫入、零 code 改（`RELEVANCE_JUDGE_PROMPT` 同 bypass 常數未郁）、零 route 改。** 本 session 最貴一堂＝judge 量錯 model，由 Leonard 撳 Render dashboard 揪返。
- **起手探針 4/4 綠:** served `app.html` `PLATFORM_VERSION 3.2.2` + index 200 / Render `/health` `cache_a.warm=true size=455` / HEAD==origin/main `12bf7c3` tree 乾淨 / Supabase `content-range 0-0/16062`。加驗凍結合約：`_meta` 2.3.0 / facts 455 / guidelines 逐 topic 加總 158 / registry 256 —— 全部同 handoff 對得上，零 drift。
- **A — Channel A 退役重構（Leonard 叫停後）:**
  1. **precondition「Channel B 覆蓋 Channel A」已量 = 覆蓋唔晒。** 兩軸釐清：455 條事實入面 109 條鏡像入 store（`approved_fact`，url 全空 109/109，9 條已退、100 條仲 serve）、346 條淨經 `channel-a` route。職責歸屬類逐條打開 retrieved passage 核實（唔信 tier）：事實係「〔科主任〕須…／〔EO〕負責…」指名角色揹職責，top passage 全部只泛講程序、唔講邊個具名角色揹 → **結構性資料模型缺口，量度補救唔到**。
  2. **Leonard 拍板 Option 2（升做有出處 footnote）。** 唯讀可行性 triage：拆咗「總帳 141/141 有 url」陷阱（url 係 retrieval 目標唔係出處，對 83 UNVERIFIED 係 topically-近但錨點對唔到嗰份 = 44% 陷阱重演）。讀樣本：CLEARED 抽 5 ~3 可升（採購門檻 g01、教師申述 g05）、UNVERIFIED 抽 4 ~0-1。**真實大細：升唔到嘅硬核只有 24 條純職責歸屬（`[角色] 負責…`），唔係 ~100+；117 條「提到角色」大部分揾返出處可升。** → `CHANNEL_A_COVERAGE_FINDINGS.md` §5-6。
- **B — judge / footnote bypass:**
  3. **建凍結驗收工具 `judge_acceptance.py` + 24 條凍結集**（11 answer + 11 decline + 2 secondary，量度前 commit `a65e723`）。answer 半邊由 curated footnote 自己嗰條問題機械抽（每 16 條、剔走 S196 tune 過 4 個題目），11 條 origin footnote 全部 rank-1（答案逐字喺 chunk）。decline 半邊 11 條全新空白 + S177 `D00_s177_frozen_post`（用返 pre-fix chunks），三條複合陷阱（學生醫生紙 chunks 寫住教職員規則 / 成績表保存 chunks 有 3 年 7 年但無學生記錄年期 / 冷氣換 chunks 有 12 個月係消防裝置）。self-test 22 條含「答everything必衰」故意整壞守衛。
  4. **量錯 model：首兩份 baseline 用 code default `gpt-4.1-nano`**（`env.ts` fallback，README/DEPLOY 都寫呢個），**Leonard dashboard 確認 Render 實設 `OPENAI_MODEL=gpt-4o-mini`**。同一 shipped prompt：nano 0/11（constant 否）vs gpt-4o-mini 8/11。**「judge 恆等於否」係 fallback model 特性、唔係 shipped prompt 特性；S196 findings（8/16）全部標「未經生產驗證」。** nano run 改名 `_nano_ARTIFACT` + 檔內標記。
  5. **V3（S196 未 ship 候選）生產 model：21/22、answer 11/11（shipped 8/11）、decline 全保、held-out**（V3 出自 S196 16 條、同呢 24 條零 query 重疊）。
  6. **footnote bypass live 發現：** 7 條 footnote-lead 空白查詢 `synthesize:true` live 全部答咗、0 decline。逐條 Supabase ilike 核實：**D17「消防演習幾耐」實錘砌數**（「消防演習/演練/逃生演習」庫入面 0 條，「每12個月」由「消防裝置檢查」搬過嚟）；**D13「留位費」其實答啱**（g26/k1_admission 有 970/1570 有 url，我一度標錯做空白已更正）。**footnote lead 跳過 judge → 改 judge prompt 唔 touch 佢哋；但 D13 證明同路載住啱答案唔可以照剷 → 修法係「先修 judge、後收 footnote bypass」，次序企穩、件事耦合。**
- **Changed（全部新增/唯讀量度，零 live code）:** 新 `dev/source/judge_acceptance.py` + `judge_acceptance_cases.json` + `judge_prompts/v3_s196.txt` + `judge_runs/`（chunks_cache + 4 份 run：nano ARTIFACT ×2、生產 ×2、footnote bypass live）；擴充 `JUDGE_PROMPT_FINDINGS.md`（S199 段：生產 model 數 + bypass 耦合）+ `CHANNEL_A_COVERAGE_FINDINGS.md`（§5-6）；`CODEBASE_CONTEXT.md` Directory Map（`judge_acceptance.*` 條目 + judge baseline 更正）；`DOC_SYNC_CHECKLIST.md` **+1 row**（32→33）「Anti-confab judge prompt 改動」。
- **Done:** commits `a65e723`(凍結集) → `829aa49`(shipped baseline + plumbing control) → `c96dc6d`(V3 + decline 數更正) → `a80c69b`(model 錯誤修正) → `1aeab49`(A 重構) → `f02c069`(footnote bypass live) → `710d8cc`(Option 2 triage) → 本 closeout commit。
- **QC:** `judge_acceptance.py --self-test` 22/22 PASS ×N；`--check-parity` PASS（harness prompt 同 `searchChannelB.ts` 逐字相同）；`--plumbing-check` 兩 model 都出「能」（證明 constant-否 係判詞唔係 wiring）。D13/D17 砌數判定用 Supabase ilike count 逐條核實。Supabase 16,062 零寫入 / registry 256 / guidelines 158 / facts 455 / v3.2.2 / 凍結合約機械核實零接觸。eval **未重跑**（零檢索改動）。
- **我出過、並已更正嘅錯（四次，全部向「對自己有利」嗰邊）:**
  1. **用錯 judge model** —— 信 code default 而唔係 Render dashboard，出兩份唔代表生產嘅 baseline，Leonard 撳 dashboard 揪返。教訓「對照組證明儀器有反應、證明唔到儀器指住正確系統；凡 Render 側嘅嘢只有 dashboard 答得到」寫入 `judge_acceptance.py` 註釋 + FINDINGS + commit。
  2. **D13 標錯做空白** —— 「越多砌數個發現越大」個方向對我有利，打開 Supabase 核實先發現 970/1570 有出處、footnote 做緊正經嘢，已剔出 decline 集。
  3. **一度講「7/7 砌數」overclaim** —— 逐條讀後散為「7/7 答咗但只 1 條實錘砌數、1 條其實啱」。
  4. **decline 半邊數錯**（commit + findings 一度寫 12，實際 11）—— 直接由檔案數返更正，commit message 寫明無分數受影響。
- **Evidence disposition:** 當前狀態 + 四項未解 next priority → handoff `Current Baseline` S199 + `Open Priorities`；可重用程序知識（model 要 dashboard 確認 / 對照組局限 / url≠出處 / Option 2 triage / footnote bypass 耦合）→ `JUDGE_PROMPT_FINDINGS.md` + `CHANNEL_A_COVERAGE_FINDINGS.md` §5-6 + `judge_acceptance.py` 註釋（唔會被重生嘅位）；量度細節 + 四個自我更正 → 本 entry；凍結集 + 四份 run → `judge_runs/`（commit，跨 session 可比）。
- **Sync:** DOC_SYNC 命中 **1 row（新增，32→33）**「Anti-confab judge prompt 改動」—— 按 anti-pattern guard 先補行再填。`update_log.json` **N/A**（零入庫）。凍結合約 / `PLATFORM_VERSION` / Supabase 16,062 / registry 256 **全部零接觸**。**Render 零 deploy**（`RELEVANCE_JUDGE_PROMPT` 未郁，judge 量度係離線）；**Pages 零改動**（無前端）。`START_NEXT_SESSION_PROMPT.txt` 由 handoff fenced block 程式化抽取重生，mirror check PASS。
- **Pending:** Option 2 真入庫未開始（要 PLAN）；24 條孤兒細決定未做；ship V3 未做（要 PLAN）；footnote bypass 未收；🔴 觀察窗未讀（8/2 + 8/5）、probe 未刪；backend route 未拆；總帳三桶未讀完；`HANDOFF_PACKAGE.md:32` drift 未修。
- **Risks:** ⚠️ D01/D17 呢類 footnote-lead live 砌數而家仍 serve 緊（修要 §3 HIGH risk，唔喺本 session 純量度範圍）。⚠️ judge/synthesis model 係 `gpt-4o-mini` 唔係 code default，任何量度引用做生產前必 dashboard 確認。⚠️ S198 probe 仍 live，觀察窗未讀。⚠️ 3 條矛盾假期日數仍可經 channel-a route 攞到。
- **Log maintenance:** `session_log_maintenance.py --check` → **trigger=False**（line_count=316 / entry_count=4，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 「判斷儀器/量度前先確認佢係咪指住生產系統」屬跨 session 累積模式（S195 spotlight probe / S196 借錯測試集 / S197 44% / S198 log-search + warm 偵測兩次 / 本次 model 錯），但呢條係 S198 已寫入 `PROJECT_DECISIONS.md` Insights 嗰條嘅延伸（對照組局限），已喺 `judge_acceptance.py` 註釋 + FINDINGS 機械化，**唔另開 PROJECT_DECISIONS 條目避免重複**。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->
