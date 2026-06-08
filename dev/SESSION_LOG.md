# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-08 Session 151 — app.html Channel A admin surface 完整移除 → 公眾完全 Channel-B-only（3 唯讀 tab）— CLOSED

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
- **無 version bump**（knowledge 凍結 @2.3.0；displayVersion 由 `data._meta.version` 動態取）。
- **Log maintenance（§4a）:** entry 加咗約 +50 行；SESSION_LOG 仍 <400 嘅遠（最舊 S144 2026-06-05 <30d）→ no-op、無 archive。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md。起手自行 verify git HEAD==origin/main + Supabase total（應 13,667）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 13,667/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S151 (2026-06-08)：**app.html Channel A admin surface 完整移除 → 公眾完全 Channel-B-only**。刪：🔒登入閘 + AdminPasswordModal + ADMIN_HASH/sha256 + 知識提煉/知識管理 2 tab + CRUD/匯出/批准 + FactCard/ExportModal/EditModal/CandidateReviewPanel + snapshot infra + INITIAL_REVIEW_STATE/INITIAL_CANDIDATES + mobile admin bar + 2 orphaned <script>。App() 收窄、VALID_VIEWS=['qa','guidelines','about']、router→about/guidelines/QAPanel。app.html 4100→2935 行。QC：grep 0 dangling + live render 0 console error + 3 tab + About stat 455/13,667/161/120 + 對抗 review PASS。§E.10(a) CLOSED-BY-REMOVAL、§F.11 locked。**0 change to knowledge.json/role_facts/guidelines/backend/Supabase/schema/RPC/下游 repo/canonical chunker。0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. chip task_672056cf：app.html QAPanel 副標題硬編碼 chunks=10,736 應改 13,667（pre-existing display drift；建議 data-driven from _meta.stats.chunks）。
2. discovery crawler 跑全量 triage / 餘 10 B-group sibling-dup 深驗。
3. monitor：gifted+CPD route precedence / gifted_osalp catalogue 排名低 / phys_sss routed-UI 限制 / freshness 週跑 / 57014 cold-start / stats.sources=120 cosmetic-stale。

⚠️ Cautions：app.html admin/Channel-A 策展功能已永久移除，重建必由零走 §3 HIGH-risk + 真 server-side auth（勿復活 client-side cosmetic gate）。chunks 係 moving display number（補入庫同步 6 處 + 注意 QAPanel 10,736 未同步點）。入庫 per-source（fetch_extract/ocr_extract→ingest_one_source；勿 full wiki_index upload）；新源必加 SOURCE_SETS allowlist（S135）。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 重建 admin / 勿動 Stage-2 / 勿改 canonical chunker 或 shared 檢索 infra。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 13,667 / facts 455 三層 / guidelines 152 / knowledge.json stats 13,667·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣（chip 10,736 修正 / discovery triage / B-group 補驗 / 新功能方向 / 或其他），未明示前勿郁上述禁區。
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

## 2026-06-07 Session 147 — Channel B 雲端 OCR 補入庫 mce(+13) + g38(+194) → Supabase 12,484 + Display/version fix（pending #4 清）— CLOSED

- **ID:** Claude_20260607_1336
- **Trigger:** 起手自測全綠 → Leonard 揀可選 follow-up「mce_framework_2008 補入庫」（INGEST_GAP 標『最抵/即入』）。
- **起手自測（verify-don't-trust，全 live）:** HEAD `e4e75a8`==origin/main clean ✓ / facts 455 三層 byte-identical(md5 `7d0033…`) ✓ / Supabase 12,277 ✓ / guidelines 152 v2.5.0 ✓ / knowledge.json frozen 455（`_meta.stats` 10736/39 display drift 仍 pending #4）/ onrender /health 200 cache_a 455 + channel-b/manifest 401-gated ✓。
- **§3 Risk:** HIGH（外部 API：OpenAI embed+vision + Supabase insert）；逐 gate GO（OCR 路線 → embed/insert → commit/deploy）。

### 分歧發現（§3 stop-and-report）
- INGEST_GAP 標 mce「✅ 已有直連、可即入」**係錯**：pre-flight 試抽揭 PDF = HTTP200/application-pdf/2,101,772 bytes（=registry hash、正檔）但**8 版全 0 文字 + 0 glyph span = 掃描影像 PDF、無文字層**。`fetch_extract.py` 抽到空 body。根因＝原分類只睇 `url_primary=.pdf`、**從未驗文字層**（verify-don't-trust §G.2 再中）。
- 內容對賬（S146 lesson）：Supabase 0 個 mce/moral/civic source_id，siblings（nat_sec_edu 39 / values_edu_2021 93 / sec_curr_6A 21）係唔同文件 → **真新源、零重複**。

### CHANGE
- **NEW tool `dev/ocr_extract.py`**（雲端 vision OCR；fitz render 每版 PNG@220dpi → OpenAI `gpt-4o` vision 逐版抽繁中 → 同 fetch_extract canonical vault 格式 + `=== Page N ===` page-resolvable + NUL strip）。質素探針（page1）→ 全 8 版 OCR：9,918 字、cjk 7,831、**U+FFFD=0**、page7 dense（4,540 字）。draft 質素（個別 OCR 誤字，靠 chunk 帶 url+頁碼點返原 PDF 保 §A.2 可追溯）。
- `ingest_one_source.py mce_framework_2008`（dry-run 13 chunks page-resolvable → live）：embed text-embedding-3-small(1536) + insert（merge-dup、只此 source_id）。
- **backend `searchChannelB.ts`：加 `mce_framework_2008` 入 `SOURCE_SETS.curriculum`**（S135 backfill-allowlist coupling：title 含「課程」→ 德育公民課程 query route 去 curriculum、唔加就 routed search 永遠 surface 唔到；direct RPC 證 vector 層 OK 但 routed 層 0）。

### QC
- Supabase 12,277→**12,290**（+13，content-range 雙驗）；mce source count=13；13/13 embedding non-null dim=1536；topic=curriculum/content_type=vault_extract/url 正確。
- **direct match_wiki_chunks RPC**（繞 routing）：「德育公民 核心價值」query 撞返 mce chunks sim 0.57/0.55 = vector 層 live+searchable ✓。
- backend `npm run check` + `npm run build` 全 PASS（allowlist edit）。
- 0 改 Channel A / knowledge.json / guidelines.json / schema / RPC / 下游 repo。

### Sources changed
- NEW `dev/ocr_extract.py`、`dev/vault/mce_framework_2008/extract_mce_framework_2008.txt`；`backend/src/api/searchChannelB.ts`（+1 allowlist 行）；`dev/source/source_registry.json`（mce notes）；`dev/INGEST_GAP_2026-06-06.md`（mce 重分類 + 「可即入」doc-drift 修正）；`dev/SESSION_HANDOFF.md`（baseline 12,290 + Open Priorities）；`dev/CODEBASE_CONTEXT.md`（工具 + External Services + AI log）；本 entry。

### Doc Sync
- 觸發 row「Channel-B vault source backfill into Supabase」：registry ✓ / backend SOURCE_SETS parity ✓（curriculum allowlist）/ HANDOFF baseline ✓ / SESSION_LOG ✓ / CODEBASE_CONTEXT Directory Map + AI log ✓。
- 觸發 row「External API / service change」：CODEBASE_CONTEXT External Services 加 OpenAI vision（gpt-4o OCR）block（§0b）✓。
- 觸發 row「Doc-drift truth-pass」：INGEST_GAP mce「可即入」更正 ✓。

### Follow-up / lessons
- **Lesson（§8b monitoring）**：「直連 PDF = 可即入」係未驗假設；scanned/CID PDF 抽到空 body = needs OCR。同類「✅直連」候選（phys_sss_2007_2015 等）入庫前必先 `fetch_extract` 試抽、撞空 = 轉 `ocr_extract.py`。
- 新源入庫**必加 SOURCE_SETS allowlist**先 surface（S135 coupling、本 session 親證 routed 0 vs RPC OK）。
- mce commit+push DONE（`d69080f`、Render deployed、routed smoke mce #1 p=1 @0.674）。

### S147 cont（same session）— g38 全本 OCR 入庫 + Display/version fix
- **Trigger:** Leonard 揀「1+2」= g38 全本 vision OCR + display fix。
- **g38（音樂教育學習領域課程指引 2003, 小一至中三）:** registry url=HTML index → 爬出真 PDF `music_complete_guide_chi.pdf`（**153 版、36.5MB**）。Triage：text-layer = **CID-mojibake**（cjk=0 / U+FFFD=0、glyph→控制字元）→ image-render OCR 繞過。
  - **工具升級 `dev/ocr_extract.py`:** 加 `--concurrency`（ThreadPool；fitz 單線程 render → 並行 OCR）+ **Retry-After-aware 429** + `--resume`（只重抽 〔OCR失敗〕頁、merge、唔重花已成功頁）。**因由:** 首輪 concurrency=6 撞 org gpt-4o **TPM=30k/min** → 88/153 頁 429 失敗；resume concurrency=2 + Retry-After → **88/88 recovered、still_failed=0**（cjk 71,679、U+FFFD=1）。
  - **filler-collapse:** worksheet/評估示例頁滿 ＿＿＿/▭▭▭ fill-in-blank（無句界）→ canonical chunker（**勿改、shared infra**）切唔開 → 1 個 8171-char malformed chunk。collapse 填充符 runs（移 17,090 無意義字、cjk 全保）→ 全 chunk ≤616。
  - **入庫:** `ingest_one_source` **+194 chunks**（dedup 後）→ Supabase 12,290→**12,484**；加 `SOURCE_SETS.curriculum` allowlist。⚠️ 與 `music_p1_s6_2024`（2024 P1-S6）共存、非 clean supersede（不同年代+級別 scope）、per-source quota bound、**monitor stale-2003-ranking**。
  - **QC:** total 12,484 雙讀 ✓ / g38=194 ✓ / direct RPC g38 retrieved 6/50 ✓ / typecheck+build PASS。
- **Display/version fix（pending #4 CLEARED；§3 HIGH-risk）:** stale `_meta.stats` chunks 10736→**12,484** + guidelines 39→**152** 改齊：三層 knowledge.json / role_facts.json / dev/knowledge/role_facts.json（**byte-identical 維持**，md5 7d0033→**d3b80c**）+ app.html（stats block + `||` fallback）+ K1_API_SPEC:44 + README（in-app 148→**161**〔=GUIDELINES_REGISTRY.length 實測〕+ chunks line「本地」→「Supabase pgvector」）。**`updated` 保留 2026-05-16**（facts 未變 455、免誤導下游 facts-version）。**version 無 bump**（查證 2.3.0 內容版 / 2.0.0 契約版 / 2.5.0 guidelines / 2.2.19 Tailwind 各自合理；`app.html:32`「2.2.1」= Tailwind CDN lib、grep false-positive、非站版）。QC: 三層 md5 一致 + JSON valid + facts 455。
- **Doc Sync:** Channel-B backfill row（registry g38 + SOURCE_SETS + HANDOFF + CODEBASE + SESSION_LOG）✓；Product-version/release row（display fix：_meta + README + K1_API_SPEC + app.html）✓；Doc-drift row（INGEST_GAP g38 done + README in-app 148→161）✓。
- **Lesson:** (1) 大 OCR job 必 pace TPM（low concurrency + Retry-After + resume）。(2) worksheet/exemplar PDF 有 fill-in filler → collapse 先 chunk（唔改 shared canonical chunker）。(3) chunks 係 moving display number、每次 ingest 後同步嗰 6 處（或改 app fetch live count）。
- **commits:** mce `d69080f` → g38+display `6ae4107`（已 push、Render deployed、g38 routed smoke #1 p=21 @0.774）→ S147 closeout commit。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md（補入庫進度）。起手自行 verify git HEAD + Supabase total（應 12,484）+ knowledge.json frozen 455 + knowledge.json._meta.stats（應 12,484/152）+ onrender /health + manifest 401-gated。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S147 (2026-06-07)：**2 個可選 follow-up 完成** — (1) mce_framework_2008 +13 + g38 音樂指引 +194 = 兩個掃描/CID PDF 用**雲端 vision OCR**（新工具 dev/ocr_extract.py，concurrency+Retry-After+resume）入庫 → Supabase 12,277→**12,484**，兩源加 SOURCE_SETS.curriculum allowlist、routed smoke 各 #1 帶頁碼；(2) **Display/version fix executed**（pending #4 清）：_meta.stats chunks→12,484 / guidelines→152 改齊三層 byte-identical(md5 d3b80c) + app.html + K1_API_SPEC + README(in-app 161)，無 bump version。順手修 SESSION_LOG S146 標題完整性 bug。**0 outstanding bug。**

Pending（全屬可選、冇緊急）:
1. chi_edu_curr_docs 全本 CLEKLAG（g09 已有節錄、待 Leonard 決定）。
2. phys_sss_2007_2015（2015 舊版 + 文字層未驗 — 做之前先 fetch_extract 試抽、撞空/CID 轉 ocr_extract）。
3. g13 中學課程指引(SECG) / g16 訓育工作指引（分章碎檔、multi-PDF 砌）；g17 深化；gifted_policy_docs 待正確 link。
4. 既有 deferred：FAIL-A record-only / §8b rule2 / Suppl_guide held / stat_fact 2024-25 stale / freshness 週跑 / 57014 cold-start monitor / g38·music_p1_s6_2024 stale-ranking monitor。

⚠️ Cautions：**chunks 係 moving display number**（每次補入庫後同步嗰 6 處〔3 層 _meta.stats + app.html + K1_API_SPEC + README〕或改 app live fetch）；入庫一律 per-source（文字層 fetch_extract、掃描/CID ocr_extract、再 ingest_one_source；勿 full wiki_index upload）；**新源入庫必加 SOURCE_SETS allowlist（S135、否則 routed 唔 surface）**；勿改 canonical chunker；大 OCR job pace org TPM。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。**

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 12,484 / facts 455 三層 / guidelines 152 / knowledge.json stats 12,484·152 / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣可選 follow-up（chi_edu 全本 / phys_sss 試抽 / g13·g16 / g17 深化 / gifted；或其他），未明示前勿郁上述禁區。
```



## 2026-06-06 Session 146 — Channel B 補入庫 batch1+2（+11 源 → Supabase 12,277）+ 下游 Circular System 接入完成 — CLOSED

- **ID:** Claude_20260606_1807
- **Trigger:** 起手自測全綠 → Leonard 問 Channel B「做哂未/完美未」→ 帶出「掃 EDB 文件入庫」缺口 → 出 51-源缺口冊 → Leonard 批1決定 15 個 → 「/workflows 全部」→ orchestrated extract+ingest → 內容核實 → 清理重複/錯源。
- **起手自測:** HEAD 5ae78ac==origin/main clean ✓ / Supabase 10,594 ✓ / facts 455 三層 / guidelines 152 v2.5.0 / knowledge.json frozen 455（display drift `_meta.stats` 10736/39 仍 stale）/ onrender /health 200 + channel-b/manifest 401 gated ✓。
- **§3 Risk:** HIGH（動生產向量庫 + DELETE row + 外部 API）；Leonard 逐步 GO。

### 缺口分析 → 真link
- Supabase distinct 源 173 / registry 203 → **51 源未入庫（按 source_id 計）**。爬 EDB index 頁出候選真檔 link，寫 `dev/INGEST_GAP_2026-06-06.md`（646 行 / 364 候選 link）。
- ⚠️ 後證根因：gap **按 source_id 計唔係按內容** → 3「missing g-id」內容其實已喺庫（sibling id）。

### 新工具（tested, reusable）
- `dev/fetch_extract.py`：mojibake-safe 抽取（PDF fitz 打 `=== Page N ===` + HTML bs4）→ canonical vault 格式。CJK 實測 U+FFFD=0。
- `dev/ingest_one_source.py`：per-source 安全入庫（重用 build_wiki_index canonical chunker 600/60 page-carry + embed text-embedding-3-small + 只插自己 source_id + merge-duplicates）。**唔用 stale wiki_index.json full upload**（會 resurrect deprecated chunk）。

### workflow cb-ingest-batch1（22 agents）
- 11 源 extract→embed→insert pipeline。第一次 args 冇傳入即 0-mutation return；inline SOURCES re-launch → 11/11 script-success。
- **內容核實（verify-don't-trust，唔信自報）→ 3 類問題：**
  - 3 dup（g31 vs eng_pri_guide_2025 / g39 vs tech_kla_guide_2017 / gs_pri_curr vs gs_pri_guide_2017）→ Leonard：刪我新嗰 3、保留既有。
  - gifted_policy_docs（534）provenance 錯（url 標 SECG booklet + 混錯源）→ Leonard：重做；但查實 cd/index.html 只 link PECG(=g06)+SECG，無新內容（資優已由 g06+g14 覆蓋）→ **skip，待 Leonard 畀正確 link**。
  - g17 正確但淺（12 chunks，只 index 概覽）。

### 結果（live-verified）
- DELETE g31/g39/gs_pri_curr/gifted_policy_docs（各 204→0）+ 移除其本地 vault。
- **真新增 7 源 +1,002 chunks：g33(421) g35(187) g36(179) g37(116) g09(10,p43-48) g14(77) g17(12)。**
- Supabase **10,594 → 11,596**（獨立 HEAD count 雙驗）；逐源 live count 11/11 對賬；live Channel B search 撞返新源 ✓。
- registry 11 源更新 url_primary/source_type/notes（minimal diff 27+/27−）。

### QC
- 11,596 = 10,594 + 1,002 ✓；CJK U+FFFD=0；g31 sanity 538K字/289頁=983 合理。0 改 Channel A / knowledge.json / guidelines.json / schema / RPC。

### Sources changed
- NEW `dev/fetch_extract.py`、`dev/ingest_one_source.py`、`dev/INGEST_GAP_2026-06-06.md`、`dev/vault/{g09,g14,g17,g33,g35,g36,g37}/extract_*.txt`；`dev/source/source_registry.json`（11 源）；`dev/CODEBASE_CONTEXT.md`；`dev/SESSION_HANDOFF.md`；本 entry。

### Follow-up / lessons
- gifted_policy_docs：待 Leonard 畀正確資優政策 link 再單獨抽。g17 可深化。INGEST_GAP 餘下：🟢30 候選 + ✅2 直連 + ❌6 deprecated 待 Leonard 決定。
- **Lesson:** gap/dup 分析改用「按內容（url/PDF 檔名）對賬」而非單靠 source_id（monitoring — 重複入庫教訓）。Display/version fix 仍 pending。

### 批次2（🟢30 dedup-first）— same session
- Read-only agent pass（Workflow `cb-batch2-pick-main`，27 源，3 ALL-DUP 先 skip）逐源揀「當前主指引」+ 中央 content-dedup → **30 亂候選收窄成 5 真‧新候選**（擋 ~25 dup/噪音）。
- **入庫 4 源 +681**：apl_curr_docs(147) · g07(438) · g23(57) · nat_sec_edu(39)。**Supabase 11,596→12,277**（HEAD count + 逐源 + dedup-confirm + search smoke 全驗）。
- **2 helper fix（root-cause）**：(1) g07 becg_2014 抽出帶 NUL → PG 22P05、insert 半截 400/438；**`fetch_extract.py`+`ingest_one_source.py` 加 NUL strip**（cb3_b2 S132 早有、新 helper 漏咗 = §8 regression）；刪 g07 partial 後重入 438 clean。(2) g38 音樂指引 text-layer = CID 字體亂碼（cjk≈0、U+FFFD guard 揀唔到）→ 標 needs-OCR、未入。
- **10 dup + 11 null 正確跳過**（見 INGEST_GAP 批次2 段）。registry 4 入庫源 + g38/chi_edu notes 更新。chi_edu 全本 skip（g09 已有節錄，待 Leonard）。

### 下游接入完成 + 收工
- Leonard 確認**下游 Circular System consumer build 好 + 完成工作** → **Channel B Phase 2 全鏈打通**（K1 endpoints LIVE + 401-gated 健康 + 下游消費端 done）。交接包 `dev/CHANNEL_B_HANDOVER.md`（spec v0.5 落地，無 key）+ `dev/CHANNEL_B_SYNC_SPEC.md` v0.5 已備。incremental sync 自動帶本 session +11 源 delta（下游下次 poll 執）。
- **收工 reconcile**：HANDOFF baseline（HEAD 32e670e + 下游完成 + Supabase 12,277）、Open Priorities regen（下游接入 closed；餘下全可選 follow-up）、Last/Previous Session Record → S146/S145。仍 **40 registry 源未入庫**（~15 可加 / 25 dup·deprecated·舊版唔做，見 INGEST_GAP 批次2 段）。K1 端點 health-check：/health 200 + manifest/chunks 401-gated。

### Log maintenance
§4a check：SESSION_LOG 233→~245 行 < 400、最舊 entry 2026-06-05 < 30 天 → 不觸發 archive（no-op）。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md + dev/CHANNEL_B_SYNC_SPEC.md (v0.5 LIVE) + dev/INGEST_GAP_2026-06-06.md（補入庫進度）。起手自行 verify git HEAD + Supabase total（應 12,277）+ knowledge.json frozen 455 + onrender /health。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑空格雙引號）。python3。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 預設。回覆中文。

S146 (2026-06-06)：**Channel B Phase 2 全鏈完成** — (1) 補入庫 batch1+2：真新增 11 課程指引源 +1,683 chunks，Supabase 10,594→**12,277**（batch1 g33/g35/g36/g37/g09/g14/g17；batch2 apl_curr_docs/g07/g23/nat_sec_edu；多個 dup/錯源已刪清 g31/g39/gs_pri_curr/gifted）；(2) **下游 Circular System consumer build 好 + 完成工作**（Leonard 確認）。新 tested 工具 dev/fetch_extract.py + dev/ingest_one_source.py（含 NUL strip）。交接包 dev/CHANNEL_B_HANDOVER.md。**0 outstanding bug。** 仍 40 registry 源未入庫（~15 可加 / 25 dup·deprecated·舊版唔做，見 INGEST_GAP 批次2 段）。

Pending（優先序）:
1. gifted_policy_docs — 待 Leonard 畀正確資優政策 link 再單獨抽（cd/index.html 無新內容、已由 g06+g14 覆蓋）。
2. INGEST_GAP 餘下（🟢30 已 dedup 處理完）：g38 音樂指引 = CID 字體亂碼 **needs OCR**（ocrmypdf/Tesseract chi_tra）；chi_edu_curr_docs 全本 CLEKLAG（g09 已有節錄，待 Leonard 決定要唔要全本）；✅2 直連（mce_framework_2008/phys_sss_2007_2015）+ ❌6 deprecated + 11 null（聚合/分章，要 multi-PDF/OCR）待決定。
3. g17 可深化（3 指引子區，現 12 chunks 概覽）。
4. Display/version fix（approach 已定、§3 HIGH-risk、勿跑 bump_version.py §E.8）：knowledge.json._meta.stats chunks→12,277 / guidelines 39→152 + README + 統一站 version。
5. 既有 deferred：FAIL-A record-only / §8b rule2 / Suppl_guide held / stat_fact 2024-25 stale / freshness 週跑 / 57014 cold-start monitor。（下游接入已完成、唔再 pending。）

Post-startup first action: 完成 §1 + 自測（HEAD / Supabase 12,277 / facts 455 / guidelines 152 / knowledge.json frozen / onrender /health + manifest 401-gated）+ playbook INDEX 後，問 Leonard 想做邊樣**可選** follow-up（補入庫餘下：mce_framework_2008 直連〔最抵〕/ g38 OCR / g13·g16 multi-PDF / chi_edu 全本 / gifted link / g17 深化；或 display/version fix；或其他）。**未明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。** 入庫一律用 dev/fetch_extract.py + dev/ingest_one_source.py（per-source 安全、含 NUL strip；勿跑 full wiki_index upload）；dup/gap 按內容（url/PDF 檔名）對賬。
```

## 2026-06-05 Session 145 — 下游 consumer 覆文納入（spec v0.4→v0.5）+ Q4 Phase 2 Channel B sync 端點 BUILT + DEPLOYED LIVE + live smoke PASS（anon embedding confirmed）— CLOSED

- **ID:** Claude_20260605_1513
- **Trigger:** 新 session 起手自測全對賬 → Leonard 揀「先 review / 傾下一步」→ 下游覆文到 → 確認 embedding 路 1 + 答 3 反問 + 揀 manifest 帶 topic+content_type + 「即寫 v0.4」。
- **起手自測:** git HEAD `cb498c1`(S144 closeout)==origin/main clean ✓（opening 寫 5cefe9b = closeout body 值、cb498c1 = 嗰個 closeout commit 本身、正常 lag）／ facts 455 三層 byte-identical(md5 `7d0033…`，knowledge≡role_facts) ✓ ／ Supabase wiki_chunks **10,594**（service-key REST 雙讀防偽零）✓ ／ 公開 guidelines 152 v2.5.0 ✓ ／ knowledge.json frozen @455 v2.3.0 ✓ ／ onrender /health 200 warm cache_a 455 ✓。egress 全通。display drift 未 fix（`_meta.stats` chunks 10736 / guidelines 39 仍 stale，符合 pending）。
- **§3 Risk:** HIGH（改對外契約；spec §12 自我宣告 HIGH-risk）；Leonard GO「即寫 v0.4」；純 docs、可逆（git revert）。

### 下游覆文重點（收 §11.2 + 3 反問 + profile 落差）
- **embedding 路 1 確認:** OpenAI `text-embedding-3-small`(1536)、chunk-index=query 同 model → **§11.2 RESOLVED**、K1 預設 `include_embedding=true` 連向量送、下游零重嵌直接入庫。
- **profile 落差（下游 flag、要求 finalize 前納入）:** 下游真實 = GitHub Actions ephemeral runner / cron 3×/日(HKT 07/13/17)+手動 / file-based numpy 鏡像(.npy+.jsonl) → **非常駐 / 非 pgvector / 非近乎即時**（推翻 v0.1–v0.3「常駐 service + 近乎即時」假設）。**incremental 仍最優**（免每 cron run 重嵌 10K chunks + 304/delta 省頻寬，前提 = 下游跨 ephemeral run 持久化鏡像）；只校正 §0/§5 rationale 措辭、契約機制零變。
- **3 反問實答（verify 過、relay 俾下游）:** (a) manifest 加 `topic`+`content_type`（現有已 populate 低基數欄、同一 table scan）俾下游 client-side 子集鏡像；(b) 60 req/min + daily ≈3× corpus + ≤150 ids/批 → bootstrap 71 批 ≈1.1 分鐘、佔每日預算 ~1/3；(c) 向量 = pgvector 文字字串 `"[f,f,…]"`（**非** JSON array）+ **實測 6 跨源樣本 L2-norm ‖v‖₂=1.0±~3e-4 = 已正規化**（dim 1536）。

### CHANGE — spec v0.3 → v0.4（`dev/CHANNEL_B_SYNC_SPEC.md`，11 段 targeted edit）
header v0.4 ／ §0 決策鏈 +consumer-覆文 row + rationale 校正 ／ §2 流程圖 ／ §3 manifest（chunk +`topic`/`content_type` 欄 + size note ~90B→~110-130B）／ §5 cadence（3×/日 cron、兩 cron-run 確認）／ §6 sync-key(Actions secret)+限流+bootstrap pacing ／ §7 embedding invariant（序列化格式 + L2-norm 實測 + 路 1 chosen）／ §9 manifest select +topic/content_type ／ §11.2 ⏳→✅ RESOLVED ／ footer v0.4 changelog。

### Q4 Phase 2 endpoint build（Leonard GO「下游可配合，go ahead」；spec v0.4→v0.5）
- **CHANGE 6 檔**：NEW `backend/src/api/channelBSync.ts`（manifest+chunks handler、X-Sync-Key gate〔`timingSafeEqual`/多key/503 fail-closed/never-log〕、自有 60/min + daily chunk budget、anon-REST `Range` 分頁 manifest scan + `in.()` chunk fetch、NO CORS）；`env.ts`（+`getChannelBSyncKeys`/`isChannelBSyncEnabled`）；`wikiRepository.ts`（export `SOURCE_ALIASES`）；`server.ts`（wire 2 route 喺公共 POST 10/min 之前）；`.env.example`（`CHANNEL_B_SYNC_KEY` 文檔）。
- **本地 QC PASS**：`npm run check`+`build` exit 0；HTTP gate smoke = 503（無 key）/401（無 header）/403（錯 key）/400（max_ids+bad-json+not-array+malformed-id）/valid→502（本地無 Supabase）/generic-502-no-leak/no-CORS//health 200 回歸。Supabase-依賴路徑（manifest/chunks 200 + embedding）**待 deploy 後 live smoke**（本地 .env 無 anon key）。
- **對抗審核（Workflow 5-lens × adversarial-verify、40 agents、2.2M tok）**：35 raised → 28 confirmed → 自行 adjudicate → **修 4 真**：(blocker) 502 洩 Supabase 內文 → generic「upstream error」+ server-log；(major) budget TOCTOU/overspend + dup-id 計數分歧 → 同步 reserve-then-refund + dedupe ids；(major) manifest cache thundering-herd 撞 §8 共用 free-tier DB → **singleflight**；(major) `in.()` 注入 defense-in-depth → `SAFE_ID_RE` 400。**否決（記理由）**：per-IP isolation（global 60/min 其實更嚴、reviewer 搞反）/ budget restart-reset（spec 已定位 soft guard、persist 要掂禁區 Supabase write）/ ETag fingerprint（端點 key-gated、無 key 見唔到 ETag）/ rate-window race（單線程 + 單一 cron consumer、soft limiter negligible）/ CHUNK_COLS export（無 test）。spec → **v0.5**（§13 實作澄清）。
- **DEPLOY + LIVE SMOKE PASS**：push 觸發 Render auto-deploy → live `/api/channel-b/manifest` 503 dormant 確認 → Leonard 設 `CHANNEL_B_SYNC_KEY`（Render service `edb-knowledge`，非空 Policy-Checker project）+ redeploy → **Leonard 跑 live smoke：`POST /chunks` 200 全 13 欄含顯式 null role/school_level/reference_year + `embedding` = 1536-vec pgvector string ~19,181 chars → anon 讀到 embedding column、路 1 confirmed**；400 max_ids guard live；key gate live（valid key 到 400 validation）。**唯一未驗 load-bearing 假設（anon SELECT embedding）已 confirmed。K1 端 Q4 Phase 2 完成、端點 LIVE。** 0 Supabase/schema/RPC/pipeline/Channel-A/knowledge·guidelines.json mutation；revert = 刪 `channelBSync.ts` + server.ts 2 route 行。

### QC
- grep 一致性 PASS：header=0.4、無殘 `版本 0.3`、§11.2 無 ⏳（剩 ⏳ 只 §0 表 Q4「K1-build」+「下游-build」兩 row）、`content_type` 8 處一致、L2-norm/路1/`include_embedding=true` 在位、「常駐/近乎即時」殘句全屬已校正語境或 L197「304 後常駐 warm」（server 保暖非 profile claim）。
- `git diff --stat`：`CHANNEL_B_SYNC_SPEC.md` +21/−18；無觸 code/data/Supabase/knowledge.json/guidelines.json。

### 唔掂（邊界守住）
- 0 endpoint build、0 掂下游 repo（§A.3）、0 改 Supabase schema/RPC/upload pipeline、0 un-freeze Channel A、0 手寫 knowledge.json/guidelines.json、0 跑 bump_version.py。

### Latent flagged（非本任務、記低）
- **`dev/SESSION_HANDOFF.md` 有 1 個 NUL byte**（令 `grep` 當 binary、要 `-a` 先出 heading）→ 記低、**勿未確認自動 strip**（§7 勿改無關內容）；收工或下次處理。

### Sources changed（docs-only、可逆）
- `dev/CHANNEL_B_SYNC_SPEC.md` v0.3→v0.4；`dev/PROJECT_MASTER_SPEC.md`（§C.6 doc-registry + §F.2 decision-chain）；`dev/CODEBASE_CONTEXT.md`（AI log S145）；`dev/SESSION_HANDOFF.md`（Open Priorities #1）；本 entry。**0 code/data/Supabase mutation**。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Channel B sync contract + endpoint (`CHANNEL_B_SYNC_SPEC.md`; Q4 Phase 2 incremental-sync) | spec v0.5; backend routes (`channelBSync.ts` + `server.ts` + `env.ts` + `.env.example`); CODEBASE External Services + Directory Map + AI log; PMS §C.6 + §F.2; SESSION_HANDOFF/LOG | ✓ Done（routes BUILT; `CHANNEL_B_SYNC_KEY` Render env + deploy + live smoke pending Leonard） |
| Long-term spec / locked-decision change (§11.2 resolved + profile correction) | PMS §F.2; SESSION_HANDOFF Open Priorities #1 | ✓ Done |

### Log maintenance
§4a check：SESSION_LOG ~291→~335 行 < 400、最舊 entry < 30 天 → 不觸發 archive（no-op）。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）+ dev/CHANNEL_B_SYNC_SPEC.md（Q4 Phase 2 契約 v0.5 LIVE）。起手務必自行 verify git HEAD + knowledge.json._meta.stats + Supabase total vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S145 證實 EDB + onrender + Supabase + GitHub Pages egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S145 (2026-06-05)：**下游 consumer 覆文納入（spec v0.4→v0.5）+ Q4 Phase 2 Channel B sync 端點 BUILT + DEPLOYED LIVE + live smoke PASS（anon embedding confirmed）— K1 端 Q4 Phase 2 完成**。0 outstanding bug。HEAD origin/main 起手自行 verify。
- **Q4 Phase 2 模型 = Incremental sync；K1 端 LIVE**：spec `dev/CHANNEL_B_SYNC_SPEC.md` **v0.5**（§13 澄清）；`GET /api/channel-b/manifest` + `POST /api/channel-b/chunks` LIVE（X-Sync-Key gated，`CHANNEL_B_SYNC_KEY` 已設 Render service `edb-knowledge`）；live smoke：13 欄 + anon reads `embedding` 1536-vec ~19KB（路 1 confirmed）。**K1 端完成。**
- **Display/version drift 一次過 fix（approach 已定、待執行）**：`knowledge.json._meta.stats`（chunks 10736→10,594 / guidelines 39→152）+ README hardcoded + 統一站 version（不 bump、勿跑 `bump_version.py` §E.8）；§3 HIGH-risk。
- **§4a + HANDOFF 收斂**：SESSION_LOG 412→168 行（S141/S142/S143 archived）；SESSION_HANDOFF 800→167 行（NUL stripped + Baseline 精簡 + Previous Records 清除）。

Current objective and progress state:
- Baseline：Supabase 10,594 / registry 203 / 公開 guidelines.json 152 v2.5.0 / 公開 knowledge.json 455 v2.3.0（FROZEN）/ brand live policychecker.wongfu.net。**0 outstanding bug**。K1 端 Q4 Phase 2 COMPLETE + LIVE。
- 下一步主線 = 下游 Circular System 接入（Leonard 發 spec v0.5 + sync key）。

Pending tasks in priority order:
1. **下游 Circular System 接入**（K1 端完成；Leonard 發 `dev/CHANNEL_B_SYNC_SPEC.md` v0.5 + sync key → 下游 build consumer；跨 repo §A.3、K1 不掂）。
2. **Display/version 一次過 fix**（approach 已定）：`knowledge.json._meta.stats`(10,594/152) + README hardcoded + 統一站 version；§3 HIGH-risk、勿跑 `bump_version.py`（§E.8）。
3. 既有 deferred：§8b rule 2 automation / Suppl_guide held / §E.10(a) ACCEPTED / FAIL-A / stat_fact 2025/26 / freshness 週跑觀察 / 57014 cold-start。

Key files changed this session (S145)：`backend/src/api/channelBSync.ts`（NEW）+ `env.ts`/`wikiRepository.ts`/`server.ts`/`.env.example`；`dev/CHANNEL_B_SYNC_SPEC.md`（v0.3→v0.5）；`dev/PROJECT_MASTER_SPEC.md`；`dev/CODEBASE_CONTEXT.md`；`dev/SESSION_HANDOFF.md`（800→167 行 NUL-free）；`dev/SESSION_LOG.md`；`dev/archive/SESSION_LOG_2026_Q2.md`（S141/S142/S143）。0 Supabase/data/knowledge.json/guidelines.json mutation。

Known risks / blockers / cautions:
- 🟢 **0 outstanding bug**。K1 端 Q4 Phase 2 COMPLETE + live smoke PASS。
- 🟡 下游 consumer build pending（跨 repo §A.3；可觀察 manifest scan 對 free-tier DB 影響；key 季度輪換）。
- ⚠️ Display/version fix（approach 已定、§3 HIGH-risk、勿跑 `bump_version.py` §E.8）。
- 既有：Channel A frozen @455；57014 transient(retry)；FAIL-A(record-only)；§E.10(a) ACCEPTED conditional；q.html/A·AB dormant 勿清；Stage-2 closed；egress 每次自測；路徑空格雙引號；wiki_chunks 欄名 `text`；結構天花板源勿再 ingest；init_backup gitignored。

Validation status：git HEAD 起手 verify；backend typecheck+build exit 0；本地 gate smoke PASS；5-lens 審核修 4 真；live smoke PASS（anon embedding confirmed）；HANDOFF 800→167 行 NUL-free；SESSION_LOG 412→168 行 archive OK。**0 outstanding bug。**

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + CHANNEL_B_SYNC_SPEC v0.5 + 自測（git HEAD / facts 455 / Supabase 10,594 / guidelines 152 / knowledge.json frozen 455 / onrender /health；可選驗 `/api/channel-b/manifest` 回 401〔key 已設〕）+ playbook INDEX 後，問 Leonard：(a) 下游 Circular System 接入進度（spec v0.5 + key 發咗未 / 下游 build 到邊）；(b) 要唔要做 display/version 一次過 fix。**未 Leonard 明示前：勿掂下游 repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge.json·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。**
```

## 2026-06-05 Session 144 — Q4 Phase 2 模型決策（Incremental sync）+ Channel B sync 契約 spec v0.3 定稿 + 下游 prompt + display/version drift 記錄 — CLOSED

- **ID:** Claude_20260605_1338
- **Trigger:** 新 session 起手自測全對賬 → Leonard 同意推 Q4 Phase 2 → 揀「先對齊下游現況再揀模型」→ 下游 profile（online 長駐 + 自有向量庫 + 近乎即時）→ 拍板 Incremental sync → 「同意，繼續做」起草 spec。
- **起手自測:** git HEAD `b5b954b`(S143 closeout)==origin/main clean ✓（鏈 58b5705→1add3a0→9978ecc→b5b954b、無 desync）/ Channel A facts 455（本地+onrender cache_a warm）✓ / Supabase wiki_chunks **10,594**（service-key REST 雙讀防偽零）✓ / 公開 guidelines 152 v2.5.0 ✓ / 公開 knowledge.json 455 v2.3.0 FROZEN（policychecker.wongfu.net 200）✓ / onrender /health 200 warm ✓。egress 全通。
- **§3 Risk:** HIGH（定義對外契約 = 下游照住 build）→ PLAN→Leonard GO→本 pass **只出 spec 文件、endpoint 未 build**。

### 模型決策（Leonard 拍板）
- 下游 profile 3 問：**online 長駐 service / 有自己向量庫 / 近乎即時**。
- verify load-bearing：embedding=`text-embedding-3-small`(1536)；`/api/search/channel-b` 無 auth + POST 10/min IP；backend 用 **anon key** 讀 Supabase；`wiki_chunks` **無 timestamp 欄**但 `id=vault_<source_id>_<hash>`(content-hash) + pipeline delete-then-insert → **delta = id set-diff（manifest-diff），零 schema change**。
- 模型 = **Incremental sync（manifest-diff delta feed）**：下游拉細 delta、維護自家 index、本地查詢（唔依賴 K1 free-tier）。否決 export快照（衝突近即時）/ pure API（綁 free-tier 脆）。

### Spec 起草 + 對抗審核（agent-team 預設）
- 寫 `dev/CHANNEL_B_SYNC_SPEC.md` v0.1 → spawn 獨立對抗審核 agent（純本地讀 spec+backend+pipeline）→ 揪 **2 blocker + 多 major**。
- **blocker 1**：pipeline 非原子 delete-then-insert，manifest 中途讀到 → 下游誤 tombstone 成個 live 源 → search flap。**修**：manifest `ingest_in_progress` guard + 下游 delete-safety（整源 deletes 兩 poll 確認）。
- **blocker 2**：manifest_hash 只 hash id-set → 換 embedding model 但 id 不變時 304 consumer 永遠睇唔到 = silent contract break。**修**：manifest_hash 摺入 contract_version+embedding_model。
- **majors 修**：bulk feed = search superset（stat_fact+原始向量，`include_statistical` 預設 false）／ single static key → timingSafeEqual+401/403/503-fail-closed+多key rotation+daily exfil budget ／ manifest O(N) server scan（304 慳 client 唔慳 server）+ 57014 全表掃 own retry+Range ／ embedding 文字格式+null 語義+null 欄位永遠 present ／ batch 500→150 + `in.()` URL 長度 ／ 缺 id=pending-add 勿 tombstone ／ sync route 勿 call setCorsHeaders。
- → 重寫 **v0.2**（全 blocker/major 收；§11 留 4 開放決策交 Leonard）。
- **§11 決策（S144 Leonard 逐條拍板，spec → v0.3 定稿）：** (1) stat chunks **預設排除**（include_statistical=false）；(2) ship 向量 **default**（下游 embedding model 未定、待 re-check、include_embedding param 兩路控、不卡 build）；(3) 限流/budget **照建議**（60/min + 每日 ≈3× 全庫 + 多 key 季度輪換）；(4) **淨靠下游 delete-safety**（K1 不加 sentinel、pipeline 不改、ingest_in_progress 欄保留回 false）。**下一步 = endpoint build §3 HIGH-risk PLAN，待 Leonard GO。**

### Display / version drift audit + deferred 一次過 fix（S144 recorded — Leonard 揀「先紀錄、適當時一次過改」，本 session 0 改）
- **觸發:** Leonard 問 GitHub + app 內 display 文字 / version number 是否反映現時最新。以下 audit 全 verified（read actual code，無改）。
- **前端 chunks/guidelines 數字 = runtime auto-sync from `knowledge.json._meta.stats`**（index.html L289 明文「auto-synced from knowledge.json _meta.stats」+ `data-stat` span；app.html 同模式 Decision 3 dynamic stats）。stats 實值 = `{facts:455 ✓, chunks:`**`10736 STALE`**`（live Supabase 10,594）, guidelines:`**`39 STALE`**`（公開 152 / in-app 161）, sources:120, topics:7}`。facts 455 啱。grep 見「452」= hex 色碼 `#4527A0` false-match、非 fact-count drift。
- **README.md hardcoded drift:** L88 in-app 指引 `148`→**161**（同檔 L28/L93 自己寫 161、README 內部唔一致）；L90「`10,736` chunks（本地，Phase 2 上線中）」→ **10,594** + 框架過時（係 Supabase pgvector、已 live、主搜尋面）；L51-52/L75-79 Channel B「Phase 2 / `wiki_index.json`」框架過時；L164 日期 `2026-05-16` stale。
- **Version namespaces（現況、唔一致）:** 站/平台 display = README badge `v2.3.0` + README footer `v2.3.0` + index.html footer `v2.3`；資料契約（獨立、各自合理）= knowledge.json `2.3.0`(frozen) / guidelines.json `2.5.0` / K1_API_SPEC `v1.3.1` / app.html JSON-LD「契約版本 v2.0.0」。
- **決定嘅做法（待執行、ONE PASS）:**
  1. **更新 `knowledge.json._meta.stats`**：chunks 10736→**10,594**、guidelines 39→**152**（一改、全部前端 auto-sync display 即正）。**Leonard 明示 OK 改**（facts 455 / schema 不變、屬 metadata-only；惟 re-publish knowledge.json = 下游 Circular System 會見檔變一次〔facts 不變〕，已接受）。
  2. **README hardcoded 修**：148→161、10,736→10,594、Channel B framing（Supabase/live/主面、剔「Phase 2/本地/wiki_index.json」）、日期。
  3. **Version =「統一現有版本號」**（**不 bump**、本 session 無 product 改）：站/README/footer display version 對齊單一值（index `v2.3` → `v2.3.0` 對齊）；資料契約版本（knowledge 2.3.0 / guidelines 2.5.0 / API 1.3.1）係獨立契約，執行時同 Leonard confirm 係咪一齊統一定維持各自。
- **執行時注意:** §3 HIGH-risk（公開 README + app.html 4,759 行 + 掂 frozen knowledge.json metadata）→ 出 PLAN 等 GO。DOC_SYNC 適用 rows：「Product version / release milestone change」+「Doc-drift truth-pass / accuracy correction」（+「guidelines.json public contract」若牽連 stat）。**bump_version.py 有 wipe role_facts schema 前科（PMS §E.8）→ 純 stat/version 對齊建議手改、唔跑 bump_version.py。**

### 唔掂（邊界守住）
- 0 endpoint build、0 掂下游 repo（§A.3）、0 改 Supabase schema/RPC/upload pipeline、0 un-freeze Channel A、0 手寫 knowledge.json/guidelines.json。

### Sources changed（docs-only、可逆）
- NEW `dev/CHANNEL_B_SYNC_SPEC.md` v0.2；`dev/PROJECT_MASTER_SPEC.md`（§F.2 model lock + §C.6 doc 登記）；`dev/CODEBASE_CONTEXT.md`（Key Decisions + Directory Map + AI log）；`dev/DOC_SYNC_CHECKLIST.md`（新 row）；`dev/SESSION_HANDOFF.md`（Open Priorities #1）；本 entry。0 code/data/Supabase mutation。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Long-term spec / locked decision / architecture invariant change (Q4 Phase 2 model lock) | PMS §F.2 + §C.6; CODEBASE Key Decisions; SESSION_HANDOFF Open Priorities #1 | ✓ Done |
| New cross-agent handoff knowledge doc added (`CHANNEL_B_SYNC_SPEC.md`) | CODEBASE Directory Map + AI Maintenance Log; DOC_SYNC registry row; SESSION_HANDOFF/LOG | ✓ Done |
| Channel B sync contract / endpoint (Q4 Phase 2) [NEW ROW added] | `CHANNEL_B_SYNC_SPEC.md`; backend routes when built; PMS §C.4/§F.2; SESSION_HANDOFF/LOG | ✓ Row added |

### Log maintenance
§4a check：SESSION_LOG 291 行 < 400、最舊 entry < 30 天 → 不觸發 archive（no-op）。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）+ dev/CHANNEL_B_SYNC_SPEC.md（Q4 Phase 2 契約 v0.3）。起手務必自行 verify git HEAD + knowledge.json._meta.stats + Supabase total vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S144 證實 EDB + onrender + Supabase + GitHub Pages egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S144 (2026-06-05)：**Q4 Phase 2 模型決策 + Channel B sync 契約 spec v0.3 定稿 + 下游 prompt + display/version drift 記錄 — 全 docs-only、0 product 改、0 outstanding bug**。HEAD origin/main `5cefe9b` 起手自行 verify。
- **Q4 Phase 2 模型 LOCKED = Incremental sync（manifest-diff delta feed）**：下游 Circular System 維護自家 Channel B index、poll K1 manifest 拉 id-set delta、本地搜尋。契約 `dev/CHANNEL_B_SYNC_SPEC.md` v0.3（過對抗審核、§11 4 決策 Leonard 全 RESOLVED）。K1 端 manifest+fetch endpoint **未 build**。
- **下游對接 prompt 已出俾 Leonard**（問下游 query embedding model 是否 text-embedding-3-small 等 + 列下游要 build 嘅 consumer）→ **等下游覆**。
- **Display/version drift 一次過 fix（approach 已定、待執行）**：knowledge.json._meta.stats chunks→10,594/guidelines→152（Leonard OK 改 frozen metadata、facts/schema 不變）+ README hardcoded(148→161/10,736→10,594/Channel-B framing/日期) + 統一站 version（不 bump）；§3 HIGH-risk、勿跑 bump_version.py（§E.8）。

Current objective and progress state:
- Baseline：Supabase 10,594 / registry 203 / 公開 guidelines.json 152 v2.5.0 / 公開 knowledge.json 455 v2.3.0（FROZEN）/ brand live policychecker.wongfu.net。**0 outstanding bug**。
- 下一步主線 = Q4 Phase 2 endpoint build（待 Leonard GO + 下游覆）。

Pending tasks in priority order:
1. **Q4 Phase 2 endpoint build（§3 HIGH-risk PLAN ready、待 Leonard GO + 下游覆 embedding model）**：build GET /api/channel-b/manifest + POST /api/channel-b/chunks + X-Sync-Key per v0.3 契約。**未 GO 勿 build、勿掂下游 repo（§A.3）、勿 un-freeze Channel A。**
2. **Display/version drift 一次過 fix（approach 已定、待執行）**：knowledge.json._meta.stats(10,594/152) + README hardcoded + 統一站 version；詳 SESSION_LOG S144 / SESSION_HANDOFF OP #3；§3 HIGH-risk。
3. 既有 deferred：§8b rule 2 automation / Suppl_guide held / §E.10(a) ACCEPTED / FAIL-A / stat_fact 2025/26 / SESSION_HANDOFF Baseline #1 巨型 stale wall 收斂 / freshness 週跑觀察 / 57014 cold-start。

Key files changed this session (S144)：dev/CHANNEL_B_SYNC_SPEC.md（NEW v0.3）；dev/PROJECT_MASTER_SPEC.md（§F.2/§C.6）；dev/CODEBASE_CONTEXT.md（Key Decisions/Directory Map/AI log）；dev/DOC_SYNC_CHECKLIST.md（新 row）；dev/SESSION_HANDOFF/LOG。**0 code/data/Supabase/knowledge.json/guidelines.json mutation**。commits 00d5291 / adbeabb / 5cefe9b。

Known risks / blockers / cautions:
- 🟢 0 outstanding bug。S144 全 docs-only、可逆（git revert）。
- 🔴 **Q4 Phase 2 endpoint build 不可逆對外效果（改 live backend + deploy onrender）+ 下游跨 repo、待 Leonard**：勿自行 build / 勿掂下游 Circular System repo（§A.3）/ 勿 un-freeze Channel A / 勿手寫 knowledge.json·guidelines.json。
- ⚠️ Display/version fix 撞 frozen knowledge.json（Leonard 已 OK 改 _meta.stats、facts/schema 不變、下游見檔變一次）；執行出 PLAN、勿跑 bump_version.py（§E.8 前科）。
- 既有不變: Channel A frozen @455；57014 transient(retry); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Stage-2 closed; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text`; 結構天花板源勿再 ingest; 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。

Validation status: 本 session 0 product change（純 spec/docs/決策/記錄）；git HEAD 5cefe9b==origin/main clean、3 commits pushed；起手自測全 PASS（Supabase 10,594 雙讀 / facts 455 / guidelines 152 / 公開 knowledge.json 455 FROZEN / onrender 200）；§4a SESSION_LOG 291 行 < 400 未觸發 archive。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + CHANNEL_B_SYNC_SPEC + 自測（git HEAD 5cefe9b / facts 455 / Supabase 10,594 / guidelines 152 / 公開 knowledge.json 455 FROZEN / onrender /health）+ playbook INDEX 後，問 Leonard：(a) 下游 Circular System 有冇覆 embedding model / 接入意向（Q4 Phase 2 endpoint build 要 GO）；(b) 要唔要做 display/version 一次過 fix。**未 Leonard 明示前，勿 build Channel B sync endpoint / 勿掂下游 repo / 勿 un-freeze Channel A / 勿手寫 knowledge.json·guidelines.json / 勿跑 bump_version.py / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。**
```
