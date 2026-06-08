# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

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
