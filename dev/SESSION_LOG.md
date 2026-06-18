# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-18 Session 173 — 真 .docx 收貨 + 文件標註 off-domain 相關性下限 (v3.2.1) + OpenAI node-fetch 生產修復

- **ID:** Claude_20260618_0839
- **Trigger:** 「開工」起手探針全綠（app.html 200 + PLATFORM_VERSION 3.2.0 + Render /health cache_a 455 + HEAD==origin/main `80e2bfd` + Supabase 15,330）→ Leonard 畀真 `.docx`（`1314天主教博智小學﹣ 知識產權及免責聲明.docx`）做 NEXT ① 真檔收貨。
- **① 真 .docx 收貨（NEXT ① 完成）：** 忠實端到端 harness（真 mammoth 1.6.0 抽取 → 真 Render `/api/annotate-document` → 逐字抽出 app.html `buildCleanOriginalDocx`+helpers 喺 node 離線跑，唔重寫）。份檔 8 段/487 字/**無表格**。**保留格式 path** ✅：輸出 round-trip 過 mammoth（Word 可開）、原 6 段逐字保留、intro+附錄正確、`<w:p>` 8→21 body 零改。**表格內段落命中** ✅（真檔無表 → 合成表格補驗）：builder 將「（建議補充）」note 正確插入該 `<w:tc>` 內、命中段之後；mammoth 每 cell 用 `\n\n` 分隔 → `segmentText` 逐 cell 切 segment（非整表一段）。Desktop 留 2 樣本 docx 俾 Leonard。
- **② 揭發 off-domain 強行配對 → 文件標註 v3.2.1：** 你份免責聲明（off-domain 法律文書）被強行配對 4 條無關「相關指引」（颱風通告/防貪/公社科）+ 硬塞「學校安全」範疇 18 條垃圾 missing。根因：`searchChannelB` `min_score=0.22`（retrieval 門檻非相關性）+ `detectDomainsPerSegment` `AUTO_DETECT_THRESHOLD=0.38`（路由門檻）對 CJK 正式語體 off-domain 太鬆。Leonard 批「加相關性下限」+（揭發第二頭後）批「domain floor」。**修（`backend/src/api/annotateDocument.ts`，兩個 floor 只喺 annotate 層、`analyzeDocument`/`searchChannelB`/`checklistRevise` 及獨立 endpoint byte-identical、用戶手動選範疇不受影響）：** `GUIDELINE_RELEVANCE_FLOOR=0.62`（guideline finding `top.score<0.62` drop）+ `DOMAIN_RELEVANCE_FLOOR=0.45`（auto-detect domain `score<0.45` drop）+ `app.html`「未找到貼題指引」空狀態。
- **②實證（live `text-embedding-3-small`）：** guideline——off-domain top ≤0.595 vs 真貼題 ≥0.654（最弱合法 on-domain 0.654）；domain——off-domain descriptor peak 0.396 vs 真 0.53(家課→curriculum)/0.69(safety)。floor 落 gap 中間、偏 recall。**QC：** typecheck PASS；本地 backend（補 Supabase env）端到端：off-domain guideline 4→0 + domain 18→0/auto=false、on-domain guideline=2/課程管理 保留；**多範疇零 regression**（Render pre-floor == Local post-floor 範疇相同 → 證 floor 無殺合法範疇，原「1 domain」係 per-segment 偵測既有行為）；headless app.html boot 乾淨（v3.2.1、空狀態 block 編譯通過、0 Babel error）。bump v3.2.1（app.html PLATFORM_VERSION + README + CHANGELOG；凍結 `_meta` 2.3.0 不動）。
- **③ 生產事故（v3.2.1 部署觸發）+ 修復：** push `78605bd` 後 Pages 即 3.2.1、但 live 探測 on-domain 都回空 → 揭發 Render Node 原生 fetch（undici）對**每個** OpenAI 呼叫回 `Invalid response body … api.openai.com/v1/embeddings: Premature close`（重用 OpenAI 已關閉嘅 keep-alive 連線）；`/health` `cache_a {warm:false,size:0}`（啟動嵌入快取 warm 失敗）；**restart 唔修**（12/12 分鐘 + restart 後仍衰）；政策搜尋+文件標註全降級。**隔離：** 同一 key 喺**本地直接打 OpenAI = HTTP 200/1.4s/1536 維** → 排除 OpenAI/key/billing；deps lockfile committed → 排除 dep drift；我嘅 floor 改動係純邏輯喺 embedding 之後 → 排除。判定＝**Render egress 嘅 undici keep-alive 問題**。**修（Leonard 批 node-fetch+pin Node）：** NEW `backend/src/lib/sdkFetch.ts`（共用 node-fetch，已綁定 dep、每請求新連線繞過 stale keep-alive）注入 embeddingClient+llmClient 兩個 OpenAI client；pin Node `22.x`（`package.json` engines + `.node-version`）。local typecheck+真打 OpenAI（embedding 1536/batch/LLM）經 node-fetch 全綠。push `f254d0c` → Leonard redeploy → **live 復原**（cache_a warm 455、Channel B OK）。
- **Live 全驗綠（背景 monitor t+30s 新 build 上線）：** OpenAI 復原 cache_a 455；off-domain `guideline=0/checklist-gap=0/domains=[]`（空狀態）；on-domain `guideline=2/checklist-gap=20/課程管理`（保留）。`>>> ALL VERIFIED LIVE`。
- **Boundary:** 凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 / Supabase 15,330 **零接觸**；canonical chunker 未改；floor 只 annotate 層 + reused module byte-identical；OpenAI 修復係 infra 韌性（無 user-facing API/feature 變，但 bundle v3.2.1 已涵蓋 floor 故同版本線）。
- **Doc Sync (§3):** Product behavior（文件標註 floor + 空狀態）→ CHANGELOG [3.2.1] + SESSION_HANDOFF/LOG ✓；Backend code fact（2 floor 常數 + sdkFetch/node-fetch + Node pin）→ CODEBASE_CONTEXT（annotateDocument + embeddingClient + 新 sdkFetch 條目）✓；版本 → app.html/README/CHANGELOG ✓。Playbook 卡 `embedding-cosine-overfire-lexical-gate` 今次再命中（cosine floor 變體，本 project 源頭卡）；undici Premature close 修復值得 deposit 新卡（收工 follow-up）。
- **commits（push origin/main）:** `78605bd`(v3.2.1：guideline+domain floor + 空狀態 + version bump) → `f254d0c`(OpenAI node-fetch sdkFetch + pin Node 22.x) + 本 closeout commit。
- **Log maintenance (§4a):** closeout 前 SESSION_LOG 154 行（<400）、3 entries（<11）、無 date trigger → **no-op**（不 archive）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.1。
Product state: HEAD == origin/main（已 push，最新 f254d0c）。Supabase 15,330；Render backend live（OpenAI client 行 node-fetch、Node pin 22.x；auto-deploy=On Commit、free-tier 偶爾卡要手動 Deploy latest commit）；Pages live（v3.2.1）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health（cache_a warm 455）+ HEAD==origin/main + Supabase 15,330。

S173（2026-06-18）已 ship + push（全 QC + live 驗綠）：
- 真 .docx 收貨（NEXT ① 完成）：文件標註「保留格式 Word」path（buildCleanOriginalDocx）+ 表格內段落命中 端到端驗（真檔=博智小學免責聲明無表 → 合成表格證 note 插入 <w:tc>；mammoth 每 cell \n\n → 逐 cell segment）。
- 文件標註 off-domain 相關性下限 → v3.2.1：annotateDocument.ts 加 GUIDELINE_RELEVANCE_FLOOR=0.62（指引比對）+ DOMAIN_RELEVANCE_FLOOR=0.45（範疇偵測）—— 只 annotate 層、reused module（analyzeDocument/searchChannelB/checklistRevise + 獨立 endpoint）byte-identical、用戶手動選範疇不受影響；+ app.html「未找到貼題指引」空狀態。實證 off-domain 0.595/0.396 vs 真貼題 0.654/0.53；多範疇零 regression；live off 0/0/[]、on guideline=2/課程管理。
- 生產事故修復（OpenAI 韌性）：v3.2.1 部署觸發 Render undici 對每 OpenAI 呼叫 Premature close（stale keep-alive、restart 唔修、cache 0/455、全降級）；隔離為 Render egress undici（同一 key/code 由其他出口 200）→ 兩 OpenAI client 注入共用 sdkFetch(node-fetch、每請求新連線) + pin Node 22.x（engines+.node-version）；live 復原 cache_a 455。
凍結合約 _meta 2.3.0 / facts 455 / guidelines 158 零接觸；canonical chunker 未改；Supabase 15,330 零接觸。

NEXT（優先序）：
① 文件標註精準度 follow-up（monitor）：narrow 主題文件 × broad 範疇 → missing 批仍出通用課程管理噪音（人文/科學科 rollout）、短文件分段偏粗——較低優先。
② EDB 入庫/壞連結＝monitor-driven：每週一 3 個 Issue（#1 freshness / #2 discovery / served-url-broken）email，有真新指引/壞連結先逐源 pre-flight+INSPECT+Leonard 授權 live INSERT/UPDATE（service key 在 backend/.env）。
③ mobile onboarding（desktop 已有）；④ Render free-tier cold-start ~50s + auto-deploy 偶爾卡；⑤ SMC 對通用 query recall 被 IMC-heavy corpus 淹（monitor）；⑥ DEBP monitor（2 OCR draft + 主藍圖圖像頁）；⑦ per-segment 範疇偵測收斂單一 broad 範疇（既有偵測質素、monitor）；⑧ Render undici keep-alive 監察（node-fetch 已修；Premature close 復發 → Azure swap fallback）。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout、用 --virtual-time-budget）；docx 8.5.0 UMD/JSZip 3.10.1/pdf.js 3.11.174/mammoth 1.6.0/pdf-lib 1.17.1；backend OpenAI client 行 node-fetch（sdkFetch）+ Node pin 22.x（勿改返 undici / engines >=20）；live Supabase INSERT/UPDATE/DELETE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env；anon key 喺 GitHub secret SUPABASE_ANON_KEY + Render env）；改 annotateDocument floor 值要對照 on-domain 唔誤殺 + Render live 探針；改 backend/checklists_bundle.json 前確認 Render deploy + routing 跑 detectQueryCategory 純函數；改清單 re-run gen_checklists_bundle.py（+gen_templates_manifest.py 若改 docx）；勿改 canonical chunker；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；入庫/deprecate（chunk count 變）要 display-sync 8 點；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.2.1 + Supabase 15,330 + Render /health cache_a 455 + HEAD==origin/main）後，按 Leonard 指示起 NEXT ① 文件標註精準度 monitor / 或其他 backlog。
```

## 2026-06-17 Session 172 — served-URL 健康檢查（Method B 監察）+ band-aid cleanup

- **ID:** Claude_20260617_1731
- **Trigger:** 「開工」→ 起手探針全綠（app.html 200 + PLATFORM_VERSION 3.2.0 + Render /health ok·cache_a 455 + HEAD==origin/main `4b0da9b` + Supabase 15,336）→ Leonard 揀「1-3」＝ NEXT ①②③ batch。①② 已 ship+QC，③ 待真檔。
- **① served-URL 健康檢查（NEW `dev/source/check_served_urls.py` + `.github/workflows/served_url_check.yml`）：** Method B 交付完整性監察，補 S170 揭發嘅盲點——`check_freshness.py` 只測 registry `url_primary`（全 200），但用戶撳 Supabase `wiki_chunks.url`（派生 store，會 drift）。新工具由 store 抽 distinct served URL 逐條 HTTP-test。純函數 `normalize_url`（剝 `#page` fragment）/`aggregate_urls`（base URL dedup→source_ids）/`classify_status`（ok 2xx / broken 4xx / **error 5xx·網絡·408·429 transient**）/`render_ledger` + `--self-test`/`--check`/`--limit`/`--changes-out`/`--ledger`。訊號路由跟 freshness 鐵律（S126）：broken 4xx → JSON 報告 + Issue，**唔影響 exit code**；只 errors > `max(5,checked//20)` exit 1；store-read 失敗 raise→exit 1（唔靜默當「0 broken」）；無 key exit 2 清楚提示。CI 需 repo secret `SUPABASE_ANON_KEY`（read-only 最小權限）——**✅ Leonard 已設好 secret + 手動 run #1 conclusion=`success`（self-test 21 PASS → 掃 198 URL 全 200 → 0 broken → 未開 Issue；run 行到掃描步即證 key 接受）= CI 閉環驗證；每週一 11:00 UTC 自動跑生效**。**首跑（本地）揭發 2 條現存 404 已即修（見 ③）**。
- **① 首次 live run：199 distinct URL · 197 OK · 0 errors · 揭發 2 條 pre-existing user-facing 404**（registry-only 監察結構上睇唔到）：(a) `edbc12_2025_ph_pri`＝store 落後 registry（store 存舊 `kla/pshe/ph-pri/EDBC_122025_C.pdf` 404；registry url_primary `cross-kla-studies/ph-primary/…` **200**）→ 修法同 SAG（Supabase UPDATE re-point）；(b) `sch_calendar_guide`＝upstream churn（registry+store 都 stale `General Holidays_2526_C.pdf` 404；landing 已出後繼 `_2627`）→ re-discover + 更新 registry&store。兩條 **detection-only、re-anchor manual gate 待 Leonard 授權**。
- **② band-aid cleanup（app.html + mobile.js）：** 移除 `SOURCE_URL_FIXUPS`+`fixSourceUrl`（app.html const block + 2 call site runChannelB/runCombined；mobile.js const block + 1 call site openSheet）。① 已證 store serve `SAG_C_markup.pdf`（383 chunks 全 200），band-aid 係 verified no-op。畸形 URL `/attachment/…/sch-admin-guide/index.html` 兩檔 0 occurrence；`node --check mobile.js` OK；headless app.html boot 5 tab + v3.2.0、0 dangling ref；3 條 app.html SAG guideline/intro URL 全 200（無 collateral）。diff 外科式乾淨。
- **QC（獨立對抗覆核 Codex/QC subagent）：** verdict **PASS-with-flags（no blocker）**。獨立 corroborate：self-test 19/19、SAG 200·malformed 404 live、0 dangling、GET-fallback 正確（HEAD 405→GET 200=ok）、exit-code 語意（broken 唔影響·store-outage→exit 1·無 key→exit 2）、report-key 對齊 workflow。**採納 2 個 Low flag**：(1) 429/408 由 broken 改 error（防 rate-limit 假警報，self-test +2 → **21 PASS**）；(2) workflow Issue body 加列 error_urls（唔淨係 count）。Flag 3（`--limit` testing knob）/4（CHANGELOG·START_NEXT 收工 regen）= 接受/收工處理。
- **Boundary:** ① 純新增唯讀監察（HTTP + Supabase SELECT，零寫）；② 純前端 no-op cleanup。0 接觸 backend / Supabase chunk 數 **15,336** / 凍結合約（`_meta` 2.3.0·facts 455·guidelines 158）/ schema / RPC / canonical chunker。**no version bump**（① infra 非 user-facing、② 零行為變）。
- **Doc Sync (§3):** Monitoring/CI workflow（row 33 擴闊涵蓋 Method B + `SUPABASE_ANON_KEY` secret 註）→ FRESHNESS_GUIDE §0 兩監察模型(A/B) + CODEBASE_CONTEXT Directory Map(+2 檔) + AI log（S172）；Product behavior(② band-aid 移除)→ SESSION_HANDOFF/LOG。✓ 全做。Playbook 卡 `freshness-monitor-test-served-url`（S170 開）今 session 落地實證（首跑捉 2 真 404）。
- **③ 兩條 404 即修（Leonard 授權「兩條都修」→「#1 重指 + #2 deprecate」；live Supabase write 用 backend/.env service key，INSPECT before/after 齊）：**
  - **#1 `edbc12_2025_ph_pri`（store-lags-registry，clean re-point）：** store 10 chunks 存舊路徑 `…/kla/pshe/ph-pri/EDBC_122025_C.pdf`（404），但 registry `url_primary` `…/cross-kla-studies/ph-primary/EDBC_122025_C.pdf` **已 200**（同一檔 EDBC_122025_C.pdf、只路徑遷移、內容一致 = 教育局通告12/2025 小學人文科）。`PATCH wiki_chunks?source_id=eq.edbc12_2025_ph_pri {url:<registry>}` 204 → INSPECT after：10 chunks 全新 url、count 不變、新 url live 200。**url-only、count 不變 → 無需 display-sync**（同 SAG）。
  - **#2 `sch_calendar_guide`（upstream churn，deprecate）：** 6 chunks = 年度性「2025/26 學年公眾假期」表，上游已被 `General Holidays_2627_C.pdf`（2026/27）取代 → 單純 re-point 會內容錯配，故 deprecate。`DELETE wiki_chunks?source_id=eq.sch_calendar_guide` 204 → INSPECT after：0 chunks、total **15,336→15,330**。registry idx208 status verified→deprecated（+deprecated_at/note；停 freshness/discover 再 flag + 防誤 re-ingest）。`searchChannelB.ts` hr_admin SOURCE_SET 移除 dead ref（校曆 query 仍由 g11 擬定校曆表指引 覆蓋；tsc PASS）。**display-sync 15,336→15,330 ×8**（app.html ×4 fallback + index.html ×3 + 3 JSON `_meta.stats` + K1_API_SPEC + README current-state；CHANGELOG 加新「[維護]」section 唔郁 S171 歷史；JSON valid、headless app.html render 15,330 無 stale）。
  - **驗證：** served-URL `--check` 重掃 **198 distinct / 198 OK / 0 broken / 0 errors**（edbc12 re-point→OK；sch_calendar 移除→199→198）。registry diff 外科式（只該 entry）。凍結合約 `_meta.version` 2.3.0 / facts 455 / guidelines 158 不動（只 `_meta.stats.chunks`）。
- **④ 文件標註真檔收貨（Leonard 提供 SKHKYPS 家課政策 PDF）+ 精準度修復：**
  - **端到端跑通：** 抽取(1頁/621字，PyMuPDF mimic pdf.js) → live `/api/annotate-document`（school_type=primary、auto-detect）HTTP 200 → 範疇 auto-detect **課程管理** → 21 findings（1 指引 + 12 partial + 8 missing）。頂層指引命中《學校行政手冊》**p199 家課**（且 source url = `SAG_C_markup.pdf` 200 → 今 session SAG 修復喺真檔輸出 live 顯示）。PDF input 走 from-text `buildCleanDocx`（非 .docx 保留格式路徑 → 「保留格式 Word」未驗、待真 .docx）。
  - **揭發精準度問題：** narrow 主題文件（家課政策）配 broad 範疇（curriculum 580 primary-visible items）→ partial/missing 溝入幼稚園（幼兒/幼稚園）+ 通用課程（小學人文科 rollout）噪音。診斷：`okType` school_type 過濾邏輯正常，但 curriculum 範疇由幼稚園課程指引蒸餾嘅清單項**未 tag** → 預設「全校類」→ 漏入小學/中學文件（係清單資料 tagging 缺口、非 code bug）。
  - **修復（Leonard 授權「修精準度：幼稚園項 tagging」）：** `dev/checklists/_work/curriculum/checklist.json` 76 項 `source_id ∈ {kgecg_2017, g29}`（兩者皆＝幼稚園教育課程指引 2017）→ tag `school_types=['kindergarten']`（content-scan 確認 KG 內容只來自呢 2 source_id；g06 小學↔幼稚園銜接 3 項屬正當小學項、不 tag）。regen `gen_checklists_bundle.py`（curriculum 629 items 不變、76 KG-tagged）。**okType 模擬驗證：** primary-visible **580→504**（−76 KG）、KG items 對 primary **0 visible**、kindergarten 仍 551 visible。**家課與課業政策 section：33 項中 30 項 primary-visible 保留**（g06/pri_curr/g13/sag 真·小學課業政策要求）、只剔 3 KG 幼兒項 → 噪音走、相關性升。templates manifest 未受影響（無 docx 改）。bundle JSON valid。**✅ post-deploy live 確認**（Leonard 手動 Render deploy `f38b511`、auto-deploy=On Commit；free-tier auto 一度卡 25min+ 故手動推）：真檔重跑 curriculum primary `total_items` **580→504**、KG-guide（kgecg_2017/g29）污染 **0**、「校本課業政策…定期檢討課業數量頻次」課業項浮現、指引命中 SAG p199 家課（URL 正確）。唯一殘留「幼稚園」字眼 partial 係 g06 小學《小一銜接》項（分喺「幼稚園課程」section 標籤下、非污染、正當保留）。**殘留 follow-up（非本 scope）：** missing 批仍係通用課程管理（人文科/科學科 rollout）＝narrow 文件 × broad 範疇 精準度議題（非 KG）；短 PDF 分段偏粗（1 段）；保留格式 .docx path 未驗（今次 PDF 走 from-text）。
- **Boundary（③④）:** live Supabase PATCH(10)+DELETE(6)、Leonard 明確授權、INSPECT before/after 齊、可逆（registry entry + vault 保留）。canonical chunker 未改；backend SOURCE_SET 改動 inert。④ 純清單資料 tagging（checklist.json + 重生 bundle）、backend code/凍結合約零接觸；DOC_SYNC row 39（清單重生）。
- **commits（push origin/main）:** `4b68f97`（①② served-URL monitor + band-aid cleanup）→ `b2ab8a2`（③ 2×404 fix + deprecate + display-sync 15,330）→ `f38b511`（④ curriculum KG tagging）→ `f1bafc6`（④ live 確認）→ `2626e8c`（CI 驗證記錄）+ 本 closeout commit。
- **Log maintenance (§4a):** closeout 時 SESSION_LOG 410 行（>400 觸發）→ `docs/qa/session_log_maintenance.py --apply` archive 最舊 entries（S164–S170）入 `dev/archive/SESSION_LOG_2026_Q2.md`、保留 S171+S172（含 S172 Handoff Prompt）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.0（正式版）。
Product state: HEAD == origin/main（已 push，最新 2626e8c）。Supabase 15,330；Render backend live（auto-deploy=On Commit、free-tier 偶爾卡要手動 Deploy latest commit）；Pages live（v3.2.0；guidelines.json v2.6.0 公開 158、app 內庫 167、跨範疇 also_in）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.0 + Render /health + HEAD==origin/main + Supabase 15,330。

S172（2026-06-17）已 ship + push（全 QC + live 驗）：
- served-URL 健康檢查（Method B 監察）：NEW dev/source/check_served_urls.py + .github/workflows/served_url_check.yml（由 Supabase wiki_chunks.url 抽 distinct served URL 逐條 HTTP-test，封 registry-only freshness 監察睇唔到嘅 store↔registry drift；self-test 21 PASS；broken 4xx→Issue 唔影響 exit、errors>threshold 先 exit 1；408/429 transient）。CI 已啟用：Leonard 設 SUPABASE_ANON_KEY repo secret（read-only）+ 手動 run #1 success（198 URL 全 200、0 broken）；每週一 11:00 UTC 自動跑。
- 首跑揭發並即修 2 條現存 user-facing 404：#1 edbc12_2025_ph_pri（store 落後 registry → Supabase UPDATE re-point 10 chunks 去 registry 200 URL、url-only）；#2 sch_calendar_guide（年度性 2025/26 公眾假期、上游已換 2627 → deprecate：DELETE 6 chunks + registry status→deprecated + 移除 hr_admin SOURCE_SET dead ref）。Supabase 15,336→15,330、display-sync 8 點。
- band-aid cleanup：移除 app.html+mobile.js SOURCE_URL_FIXUPS（SAG store 已永久修好、verified no-op）。
- 文件標註真檔收貨（Leonard SKHKYPS 家課政策 PDF）+ 精準度修復：curriculum 範疇 76 KG-source 清單項（kgecg_2017+g29 幼稚園課程指引）tag school_types=['kindergarten'] + 重生 checklists_bundle.json；live 驗 primary 580→504、KG 污染 0、課業政策項浮現、指引命中 SAG p199 家課。
- playbook proposal deposited（served-URL 實作 + 429/408 transient + error-URL visibility refinement，repo 8bccdbc）。
凍結合約 _meta 2.3.0 / facts 455 / guidelines 158 零接觸；canonical chunker 未改；no version bump。

NEXT（優先序）：
① 真 .docx 收貨「保留格式 Word + 表格內段落命中」（S172 PDF 走 from-text buildCleanDocx 路徑、未驗到 .docx 保留格式 buildCleanOriginalDocx path）。
② 文件標註精準度 follow-up（monitor）：narrow 主題文件 × broad 範疇 → missing 批仍出通用課程管理噪音（人文科/科學科 rollout）、短 PDF 分段偏粗（1 段）——非 KG（已修）、較低優先。
③ EDB 入庫/壞連結＝monitor-driven：每週一 3 個 Issue（#1 freshness / #2 discovery / served-url-broken）email 到，有真·新指引/壞連結先逐源 pre-flight+INSPECT+Leonard 授權 live INSERT/UPDATE（service key 在 backend/.env）。
④ mobile onboarding（desktop 已有）；⑤ Render free-tier cold-start ~50s；⑥ SMC 對通用 query recall 被 IMC-heavy corpus 淹（monitor）；⑦ DEBP monitor（2 OCR draft 質 + 主藍圖圖像頁）。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout、用 --virtual-time-budget）；docx 8.5.0 UMD/JSZip 3.10.1/pdf.js 3.11.174/mammoth 1.6.0/pdf-lib 1.17.1；live Supabase INSERT/UPDATE/DELETE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env；anon key 喺 GitHub secret SUPABASE_ANON_KEY + Render env）；改 backend/checklists_bundle.json 前確認 Render deploy + routing 跑 detectQueryCategory 純函數 + Render live 探針；改清單 re-run gen_checklists_bundle.py（+gen_templates_manifest.py 若改 docx）；勿改 canonical chunker；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；入庫/deprecate（chunk count 變）要 display-sync 8 點；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.2.0 + Supabase 15,330 + Render /health + HEAD==origin/main）後，按 Leonard 指示起 ① 真 .docx 收貨 / 或其他 backlog。
```

## 2026-06-17 Session 171 — 重開「EDB 通告分析系統」入口連結 + 頂層 umbrella root 設 redirect-only

- **ID:** Claude_20260617_0911
- **Trigger:** Session 開喺頂層 umbrella root（非 active root）→ Leonard 指「每次一開 session 都係行 Draft，不論點開都係對的」→ 先設頂層 redirect，再做實際 Draft 任務：重開通告分析入口。
- **① 頂層 umbrella root 設 redirect-only（非 git；頂層 `dev/*`，不入本 Draft commit）：** 頂層 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge` 係 dormant scaffold，但自帶一套輕量 Agent Handoff Kit，全 TBD + fresh-install 訊號 → 一開就觸發 onboarding、撞錯 root。修：填頂層 `dev/SESSION_HANDOFF.md`（Durable Anchors / Current Baseline / Active Objective / Next Priorities 全指向 Draft）+ 重寫 Next Session Opening Message + 同步頂層 `START_NEXT_SESSION_PROMPT.txt` 為 Draft redirect。特登唔郁 managed `CLAUDE.md`/`AGENTS.md`（upgrade 會重生成抹走 inline pointer）。QC：parity OK（prompt == fenced block）、舊 onboarding prompt 清走、ack markers 24 完整、**Draft working tree 0 改動**。
- **② 重開「EDB 通告分析系統」入口（commit `972ab78`，index.html）：** S154 曾應 Leonard 指示停用（`<a>` → 停用 `<span>`「（暫停開放）」+ opacity .55 + not-allowed）；今還原。由 disable commit `0c34611` 取回真原始 markup（完整 `<a class="ftag" target=_blank rel=noopener` + 11px 外連箭咀 SVG），非靠 comment 重砌。URL 核實 live：`leonard-wong-git.github.io/EDB-AI-Circular-System/` 301 → circular.wongfu.net 200。
- **QC（②）：** git diff 只 index.html 4↔4；active `<a>` 在、殘留「暫停開放」span / 「暫時停用」comment 0/0；headless Chrome render DOM 有正確 href + 無「（暫停開放）」字樣。app.html intro card（line 2086）純 title/desc dead-data，不涉、不改。
- **③ DEBP 數字教育發展藍圖入庫（Leonard 授權「6 源全部入」）：** EDB `debp.html`「中小學數字教育發展藍圖」6 份實質文件（略過三摺宣傳單張）→ Channel B Supabase。4 份文字層（`fetch_extract.py`）+ 2 份圖像補充 OCR（`ocr_extract.py` gpt-4o vision，各 1 illegible figure region、0 失敗頁、draft 質）。canonical chunker（`build_wiki_index`，**未改**）→ **209 chunks**（debp_blueprint 92 / debp_ai_examples 57 / debp_ai_literacy_framework 20 / debp_ailf_example 19 / debp_ai_teaching_guide 16 / debp_exec_summary 5）。INSPECT before 15,127 → 6 源全 `*/0`（純加法）→ live INSERT → after **15,336**（per-source 逐個核）。新 `digital_education` route（`searchChannelB.ts` SOURCE_SETS + TOPIC_KEYWORDS〔數字教育/數位/數碼/發展藍圖/DEBP/人工智能/\bAI\b/AI素養/生成式…〕+ QUERY_EXPANSIONS，擺 curriculum 前）。topic=it。registry +6 entry（mon list；freshness_metadata 用 pre-flight HEAD hash/last-modified；225 源；status=verified）。
- **④ 首頁資料庫更新日誌（Leonard：「進入平台旁建一個 icon」）：** `index.html` nav「進入平台 →」旁加 📋 icon → modal；新 `update_log.json`（curated、newest-first、簡述：日期/動作/文件名/desc/url）；XSS-safe DOM 建構 + https-only href + dot=未讀最新（localStorage `k1_updlog_seen_v1`）。seed 4 條（DEBP + SMC/KG/IMC 近期入庫）。入 DOC_SYNC（每次入庫 append）。
- **QC（③④）：** route `npm run check`+`build` exit 0；`detectQueryCategory` 純函數測 **16/16 PASS**（DEBP/AI→digital_education；STEAM/STEM/curriculum/kg_admin/校董會/gifted/finance/cpd 零回歸）；**Render live 探針：DEBP query → 8/8 全 debp_* 源**（text-layer + OCR 都 surface）；INSPECT after=15,336 + 6 源逐個對（92/5/19/57/20/16）；display-sync 7 surface 15,127→15,336（git diff 15/15、3 JSON 層 + app.html + index.html + K1_API_SPEC + README）；更新日誌 headless（local HTTP server）render：icon+modal present、DEBP/SMC entry rendered、「載入中」消失、15,336 同步。
- **⑤ 指引文件庫分類正名「數字教育」+ 收錄 DEBP 6 份（Leonard：「資訊科技得 1 份係奇怪的」）：** 釐清「指引文件庫」（策展連結庫 `GUIDELINES_REGISTRY`→`guidelines.json`，按 title/URL/年份）同「政策搜尋語料」（Supabase 15,336 chunks）**係兩個獨立系統** —— DEBP 入咗搜尋但未入指引庫，故 資訊科技 仍得 1 份（g28）。`app.html` CATS/SUB_CAT_SEQ/SUB_CAT_LABELS/topic-label/intro-desc + g28 category：「資訊科技」→「數字教育」（category-key + label）+ 加 6 DEBP entry（id=debp_*、format PDF、sub_cat blueprint/ai_literacy）。`build_guidelines.py` CATEGORY_TO_TOPIC「資訊科技」→「數字教育」（值仍 'it'，downstream 合約零影響）→ regen `guidelines.json` **v2.5.0→2.6.0、公開 152→158**（it/數字教育 **1→7**：g28 + 6 DEBP；self-test PASS、+6 -0 lost、無 XLSX/DOCX/INDEX 洩漏）。app `GUIDELINES_REGISTRY` 161→167。display-sync guideline count 152→158（3 JSON 層 _meta.stats + app.html embedded + K1_API_SPEC）+ README 161→167。**QC：** `build_guidelines.py --self-test`/`--check` PASS；headless app.html `#guidelines` render「數字教育」chip + DEBP 條目（發展藍圖/AI 素養架構）+ app count 167，「資訊科技」只餘內容文字（非分類 chip）。⚠️ **兩系統獨立紀律**：日後入庫（搜尋語料 Supabase）≠ 入指引庫（策展 GUIDELINES_REGISTRY），要分別處理。
- **⑥ 指引庫支援跨範疇 `also_in[]`（Leonard：「不可以一份，有幾個範疇，反正指引都是哪 158 份」）：** 資料模型限制＝每份只一個 `category`。方案 A 落地：12 份跨範疇 registry entry 加 `also_in: [...]` 副類（g10/g14/sen_curr_area/gifted_policy_docs→學生事務；g11/g28→行政；6 DEBP→課程）；`app.html` filter（`category===activeCat || also_in.includes(activeCat)`）+ catCounts（副類也計）+ 學生事務 SUB_CAT_SEQ +sen_gifted。**全部 unique 167 不變**（also_in 唔 inflate 總數）；類別 count 重疊（課程 136→142 / 學生事務 8→12 / 行政 3→5 / 數字教育 7）。**純 UI app.html；`guidelines.json` / 下游 Circular System 契約零改**（仍按主類單 topic、公開 158）。QC：catCounts 模擬 全部=167 + 12 跨listed；headless boot OK + 數字教育 chip。⚠️ 副類 tag 屬 curation 判斷（subject-safety 3 份〔視藝/科技/體育科安全〕暫未 tag、可後補）。〔註：側欄「全部 167」= app 內庫含 9 統計/表格/壞連結；公開 158 剔走嗰 9 —— app-vs-public 既有差，非本改引入。〕
- **Boundary:** WS2 DEBP = **live Supabase INSERT（Leonard 明確授權「6 源全部入」、INSPECT before/after 齊）**；凍結合約 `_meta.version` 2.3.0 / facts 455 / guidelines 152 **不動**（只 `_meta.stats.chunks` 15,127→15,336 display-sync，同 S168 做法）；canonical chunker 未改；OCR 為 draft 質（traceable via chunk url+page）。② 純前端 block 還原；頂層 redirect 非 git。
- **commits（push origin/main）:** `972ab78`(重開入口) → `da33b8c`(治理) → `10bd47f`(digital_education route) → `9e51b6f`(DEBP 6 源入庫+更新日誌+display-sync+registry+6 vault) → `4d0f3a6`(治理) → `beddcd8`(指引庫「資訊科技」正名「數字教育」+收錄 DEBP 6 份指引、guidelines.json v2.6.0 公開 152→158) → `4b3985b`(治理) → `6488b44`(指引庫跨範疇 also_in、12 份多類顯示、純 UI 下游零改) + 本治理 commit。Supabase live INSERT 209 chunks（Leonard 授權）。
- **Log maintenance (§4a):** SESSION_LOG <400 行、entries <11，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.0（正式版）。
Product state: HEAD == origin/main（已 push，最新 6488b44）。Supabase 15,336；Render backend live；Pages live（v3.2.0；guidelines.json v2.6.0 公開 158、app 內庫 167、支援跨範疇 also_in）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.0 + Render /health + HEAD==origin/main + Supabase 15,336。

S171（2026-06-17）已 ship + push：
- DEBP 中小學數字教育發展藍圖 6 源入庫 Channel B（Supabase 15,127→15,336，209 chunks：4 文字層 fetch_extract + 2 OCR ocr_extract gpt-4o；新 digital_education route 擺 curriculum 前；Render live 探針 DEBP query 8/8 全 debp_* 源；topic=it；canonical chunker 未改）+ registry mon list +6（225 源）。
- 指引文件庫分類「資訊科技」正名「數字教育」+ 收錄 DEBP 6 份指引（guidelines.json v2.5.0→2.6.0、公開 152→158、app 161→167；策展連結庫 GUIDELINES_REGISTRY→guidelines.json，與搜尋語料 Supabase 兩個獨立系統）。
- 指引庫支援跨範疇 also_in[]（12 份跨範疇文件可現身多類：SEN/資優→學生事務、校曆/g28→行政、DEBP→課程；全部 unique 不變、類別 count 重疊；純 UI、下游契約零改）。
- 首頁資料庫更新日誌：index.html nav「進入平台」旁 📋 icon → modal，data 由 update_log.json fetch（簡述新增/更新文件；dot=未讀最新）。
- 重開「EDB 通告分析系統」入口連結（index.html，還原 S154 停用嘅 <a>；URL 301→circular.wongfu.net 200 verified）。
- 頂層 umbrella root 設 redirect-only（非 git；頂層 handoff + START_NEXT 指向 Draft，免再撞 onboarding 空殼）。Draft 零接觸。

S170（2026-06-15）：監察清訊號（eb9d90b）+ 學校行政手冊 404 兩層修（59b8d2b + Leonard Supabase UPDATE 383 sag_2025_11 url）+ 平台 v3.2.0（6309333）+ 每週監察 email（Watch→Issues #1/#2）+ playbook 沉澱（7057db8）。

NEXT（優先序）：
① served-URL 健康檢查（404 盲點 follow-up）：監察只測 registry URL（全 200）但用戶撳 Supabase served URL（會 drift）→ 加由 store/API 抽 distinct served URL 逐條 HTTP-test，封 source-of-truth skew。
② band-aid cleanup（低優先、無害）：Supabase 已永久修好 SAG，可移除 app.html+mobile.js SOURCE_URL_FIXUPS。
③ Leonard 真機/真檔收貨 S169 ①②③（保留格式 Word + 表格內段落命中）。
④ EDB 入庫＝monitor-driven：每週一 Issue #1/#2 email 到，有真·新指引先逐源 pre-flight+INSPECT+Leonard 授權 live INSERT（service key 在 backend/.env）。
⑤ mobile onboarding（desktop 已有）；⑥ Render free-tier cold-start；⑦ SMC 對通用 query recall 被 IMC-heavy corpus 淹（monitor）。
⑧ DEBP monitor（S171）：2 OCR 補充 draft 質（各 1 illegible figure region）+ 主藍圖約 16 圖像頁無文字層（如真查詢命中可補 OCR）；digital_education route 真查詢觀察；更新日誌每次入庫順手 append update_log.json。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout）；docx 8.5.0 UMD/JSZip 3.10.1/pdf.js 3.11.174/mammoth 1.6.0；live Supabase INSERT/UPDATE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env）；改 backend 前確認 Render deploy + routing 跑 detectQueryCategory 純函數 + Render live 探針；勿改 canonical chunker；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.2.0 + Supabase 15,336 + Render /health + HEAD==origin/main）後，按 Leonard 指示起 ① served-URL 健康檢查 / ② band-aid cleanup / 或其他 backlog。
```

## 2026-06-15 Session 170 — 監察清訊號 / 學校行政手冊 404 兩層修 / 平台 v3.2.0 正式版

- **ID:** Claude_20260615_2123
- **Trigger:** Leonard「開工」→ 起手探針全綠 → 起 ④ Phase 0 唯讀爬取 → 衍生「監察每週自動跑、想 email」主題 → 揭發學校行政手冊 404 → 清訊號 + 404 兩層修 + v3.2.0 封版 + 收工。
- **① 監察清訊號（commit `eb9d90b`，純 local／零 Supabase）：**
  - Freshness：9 個 flag 全係 **stub-baseline artifact**（舊 baseline 1–3KB 殼頁 vs 新 multi-MB 真 PDF、部分 Last-Modified 倒退）＝resolution path 改、唔係內容變。`check_freshness.py` write-sync 重 seed 全 215 baseline（只動 `last_checked_at`+`freshness_metadata`，semantic diff 驗 NONE outside）→ 第二次 dry-run **Changes:0**；`freshness_changes.md` ledger 刷新成 0。
  - Discover：單一 KG archive index 一頁吐 316/736。`discover_sources.py` 加 `ENUMERATION_PAGE_CAP=25`（>cap 即 flag `enumeration-page`、保留報告踢出 likely-real、**no-loss**）→ likely-real **680→223**。self-test **ALL PASS**（+3 新 case）。
- **② 學校行政手冊「開啟」404 兩層修（commit `59b8d2b` + Leonard Supabase UPDATE）：**
  - 根因：`sag_2025_11` Channel-B chunk 在 Supabase 存畸形 URL `…/attachment/…/sch-admin-guide/index.html`（檔案路徑夾目錄頁→EDB 404、非 `.pdf` 故無 `#page`）。來自舊候選佇列入庫值；registry 已改正（SAG_C_markup.pdf）但 Supabase 未重新同步＝**registry↔store drift**。範圍 **SAG-only**（離線審 13,042 chunk + 線上抽查 24 源確認）。
  - 前端 band-aid：app.html + mobile.js 加 `SOURCE_URL_FIXUPS` 改寫至 SAG_C_markup.pdf。QC：邏輯單元 4/0、`node --check mobile.js` OK、headless app.html boot 無錯、live Pages 含 band-aid。
  - 永久修：Leonard 喺 Supabase SQL editor 跑 INSPECT→UPDATE（**383 chunks** url index.html→SAG_C_markup.pdf、url-only）。我 verified live：API 回 SAG_C_markup.pdf（`.pdf`、非 index.html）。band-aid 變無害 no-op。
- **③ 平台 v3.2.0 正式版（commit `6309333`）：** app.html `PLATFORM_VERSION` 3.1.0→3.2.0 + README badge/footer + CHANGELOG v3.2.0（彙整 S169 ①②③⑤ + 本 session）。凍結 knowledge.json `_meta` 2.3.0／facts 455／guidelines 152 不動；Supabase 15,127（只修 1 源 URL、chunk 數不變）。QC：headless app.html boot 顯示 v3.2.0、無 stale 3.1.0、tabs render、無錯。
- **④ EDB 每週監察 email：** 核實兩個 GitHub Actions 真有跑（freshness 12 次：6/1·8·15 success、5/18·25 fail＝S126 修好嘅 bug；discover **今日第一次**跑）；輸出在 GitHub Issue #1/#2、**唔係** email。Leonard 設好 **Watch→Issues**（每週一 email）。糾正佢誤設嘅 Settings→push-email（係 commit 通知、非監察報告）。
- **⑤ ④ EDB 全入庫＝triaged 無批次值得入：** Phase 0 唯讀爬取（freshness 0 真更新、discover 223 likely-real post-cap）。triage 221 fresh 候選＝全係已在庫文件章節碎片／已取代舊通告（2006/2015）／表格/FAQ／英文重複版 → force-ingest 會污染 corpus；corpus current（S154 IMC／S160-162 KG／S168 SMC）。**處理為 monitor-driven on-demand**。
- **⑥ playbook 沉澱（§14）：** inbox proposal「content monitor 測 served URL 唔好測 registry + 訊號衛生」（playbook repo commit `7057db8`）。
- **QC 工具學習：** live Supabase 可由 `backend/.env` `SUPABASE_SERVICE_KEY` 做 INSERT/UPDATE（早前只查 anon key 睇漏）。app.html headless Chrome 用 `--virtual-time-budget`（macOS 無 timeout）；`grep -c` 命中 0 會 exit 1 斷 `&&` 鏈（拆開跑）。
- **Boundary:** 監察 script／版本／前端純改；Supabase 只 SAG **url-only** UPDATE（chunk 數/_meta/display-sync 不變、非 count 變故無需 7 點同步）；凍結合約零接觸。
- **(addendum) RAG 系統架構圖入庫：** Leonard 提供 `Policy Checker-System Architecture.png`（S168 架構圖 prompt 產出，1.5MB 1536×1024）→ copy 入 repo `docs/system-architecture.png` + README「技術架構」section 內嵌 + CODEBASE_CONTEXT Directory Map/AI log + PROJECT_MASTER_SPEC §C 引用。純文檔/資產，零接觸 code/Supabase/凍結合約。**doc-drift truth-pass**：清走 README「技術架構」舊 ASCII 圖（誤將 channel-a 當主線、列 q.html/combined/analyze-circular 休眠入口）→ 換現行準確端點表（核實 `backend/src/server.ts`：channel-b/analyze-document/annotate-document/checklist-revise/checklist-domains/health）。
- **commits（已 push origin/main）:** `eb9d90b`(清訊號)→`59b8d2b`(404 band-aid)→`6309333`(v3.2.0)→`5186d0f`(收工治理)→`0ff1925`(架構圖)→README ASCII cleanup（本 commit）。playbook repo `7057db8`。Supabase：Leonard UPDATE 383 `sag_2025_11` url（verified live）。
- **Log maintenance (§4a):** SESSION_LOG <400 行、6 entries <11，no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層係 dormant scaffold).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.0（正式版）。
Product state: HEAD == origin/main（已 push 35458c7）。Supabase 15,127；Render backend live；Pages live（v3.2.0）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.0 + Render /health + HEAD==origin/main + Supabase 15,127。

S170（2026-06-15）已 ship + push（全 QC PASS、verified live）：
- 監察清訊號（eb9d90b）：freshness re-seed 全 215 baseline（假警報 9→0、修 stub-baseline artifact）+ discover 加 ENUMERATION_PAGE_CAP=25（likely-real 680→223、no-loss、self-test ALL PASS）。
- 學校行政手冊「開啟」404 兩層修（59b8d2b + Leonard Supabase UPDATE）：前端 SOURCE_URL_FIXUPS 改寫畸形 URL（app.html+mobile.js）+ Supabase 383 sag_2025_11 chunks url index.html→SAG_C_markup.pdf（url-only、chunk 數不變、verified live）。根因＝registry↔Supabase URL drift。
- 平台 v3.2.0 正式版（6309333）：PLATFORM_VERSION 3.1.0→3.2.0 + README + CHANGELOG（彙整 S169 ①②③⑤ + 本 session）。凍結 knowledge.json _meta 2.3.0 不動。
- EDB 每週監察 email：Leonard 設好 GitHub Watch→Issues（Issue #1 freshness / #2 discovery 每週一 email）。
- playbook 沉澱：inbox proposal「content monitor 測 served URL 唔好測 registry」(playbook repo 7057db8)。
- ④ EDB 全入庫＝triaged 無乾淨批次值得入（223 候選全係碎片/舊通告/表格/英文重複；corpus current）→ monitor-driven on-demand。
- 文檔：加入 RAG 系統架構圖 docs/system-architecture.png（README 技術架構 section 內嵌）+ 清走 README 舊 ASCII（換現行端點表，核實自 server.ts）。

NEXT（優先序）：
① served-URL 健康檢查（404 盲點 follow-up）：監察只測 registry URL（全 200）但用戶撳 Supabase served URL（會 drift）→ 加由 store/API 抽 distinct served URL 逐條 HTTP-test，封 source-of-truth skew。
② band-aid cleanup（低優先、無害）：Supabase 已永久修好 SAG，可移除 app.html+mobile.js SOURCE_URL_FIXUPS。
③ Leonard 真機/真檔收貨 S169 ①②③（保留格式 Word + 表格內段落命中）。
④ EDB 入庫＝monitor-driven：每週一 Issue #1/#2 email 到，有真·新指引先逐源 pre-flight+INSPECT+Leonard 授權 live INSERT（service key 在 backend/.env）。
⑤ mobile onboarding（desktop 已有）；⑥ Render free-tier cold-start；⑦ SMC 對通用 query recall 被 IMC-heavy corpus 淹（monitor）。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout）；docx 8.5.0 UMD/JSZip 3.10.1/pdf.js 3.11.174/mammoth 1.6.0；live Supabase INSERT/UPDATE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env）；改 backend 前確認 Render deploy + routing 跑 detectQueryCategory 純函數 + Render live 探針；勿改 canonical chunker；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.2.0 + Supabase 15,127 + Render /health + HEAD==origin/main）後，按 Leonard 指示起 ① served-URL 健康檢查 / ② band-aid cleanup / 或其他 backlog。
```

---
