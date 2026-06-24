# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->
Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

Entries are kept, summarized, or archived — not current state. Do not remove validation evidence. Use latest opening message from most recent entry.

<!-- ack:section:session-log-entry-template -->
## Entry Template

- **ID:**
- **Summary:**
- **Changed:**
- **Done:**
- **QC:**
- **Evidence disposition:** <one-time only / kept as recent trace evidence / absorbed into handoff / indexed in PROJECT_INDEX / promoted to PROJECT_DECISIONS / promoted to rule pack>
- **Sync:**
- **Pending:**
- **Risks:**
- **Log maintenance:**

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first, then follow its §1 startup sequence:
Read in order: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
dev/DOC_SYNC_REGISTRY.md
```

---

<!-- ack:log-entry:start -->
## 2026-06-24 Session 180 — SAG 學校行政手冊版本核對 (2025-11 → 2026-05)：§3.7.3 新增段 curated overlay 入庫

- **ID:** Claude_20260624_1415_S180
- **Summary:** 「開工」→ 頂層 redirect → Draft active root；起手探針 HEAD==origin/main 78312a0 / app.html v3.2.1 / Supabase 15,413 (footnote_curated 83)；Render /health 起初 cache_a warm=false → 背景輪詢 ~10s 升返 455（良性 free-tier cold-start、OpenAI 健康，非 quota）。Leonard「做」→ 接 S179 NEXT 嘅 SAG 疑 May-2026 新版 flag → live 核實 confirmed（EDB SAG 已 2026-05、markup/clean Last-Modified 2026-05-20、served 同檔名）→ 官方 Log_sheet 證自 2025-11 起唯一 delta=item 73 (§3.7.3) → 逐字 diff（store vs 2026-05 PDF）揭實質改動=1 新增段（懷疑性侵犯轉介報警程序）→ AskUserQuestion，Leonard 揀 (A) curated overlay → verbatim 重核 (markup+clean byte-identical, display page 80) + self-test cosine 0.758 → Leonard「做」明確授權 → live INSERT + registry bump + display-sync + push fb1f8fc → Render live verify overlay rank 1/8 + synthesis grounded → 報告。
- **Changed:**
  - Supabase wiki_chunks: +1 footnote_curated (`footnote_fn_sag_sexual_abuse_referral`, source_id=sag_2025_11, url SAG_C_markup.pdf#page=80, embed=text+keywords)。footnote_curated 83→84、total **15,413→15,414**。
  - `dev/source/source_registry.json`: sag_2025_11 (version_label 2025-11→2026-05) + g24 (2025→2026-05)、title「2025年11月版」→「2026年5月版」、last_checked_at→2026-06-24（git diff 6 行精準）。
  - `dev/ingest_sag_373_overlay.py`（新，reproducible --self-test/--execute + INSPECT before/after）。
  - display-sync 8 點 15,413→15,414 (app.html/index.html/knowledge.json/role_facts.json/dev/knowledge/role_facts.json/K1_API_SPEC.md/README.md + CHANGELOG S180 entry)。凍結合約零接觸 (_meta 2.3.0/facts 455/guidelines 158、無 PLATFORM_VERSION bump)。
- **Done:**
  - ✅ **SAG 版本核對 confirmed + §3.7.3 新段 curated 入庫 LIVE**。verbatim：「如問題懷疑涉及性侵犯，學校須遵照社會福利署《保護兒童免受虐待–多專業合作程序指引》，諮詢社會福利署的保護家庭及兒童服務課或香港警務處虐兒案件調查組，以採取合適的處理程序。如情況顯示個案可能涉及刑事罪行，學校應向警方舉報。」
  - ✅ **Render live verify**：query「學生懷疑被性侵犯 學校點處理 報警轉介」→ overlay rank **1/8** score 0.739、synthesis grounded（諮詢社署保護家庭及兒童服務課／警務處虐兒組／報警／依《多專業合作程序指引》），核心新段忠實命中零砌數。
  - ✅ registry freshness 完整性閉環（version_label 此前 stale 2025-11/2025）。
  - ✅ **C — SAG dedup 調查 resolved + 公開顯示面同步**：核實 `wikiRepository` alias `g24→sag_2025_11` + seen-Set dedup + 共用 per-source quota → 雙重 ingest 由 soft-dedup 妥善處理、**無需 hard-dedup**（backlog「軟 dedup 足夠用」屬實）。調查揭發 `g24` 雙重身份（Channel-B 來源 + 公開指引 entry）→ 補做公開顯示面版本核對：`guidelines.json`（sag_2025_11/g24 title/year→2026-05、`_meta` 2.6.0→2.6.1、count 158 不變）+ `app.html` GUIDELINES_REGISTRY 2 entry + 平台介紹示例標籤。commit `7828f3e`。
  - ✅ **B — 雲端 OCR 引擎參考袋低**：評估 Leonard 一份「OCR 收費版」brief → 架構（serverless key-proxy）對本 project 幫助低（後端已存在、key 已 server-side），但 Google Vision `DOCUMENT_TEXT_DETECTION`（bbox+逐字信心）/Mistral OCR 引擎事實對 image-PDF ingestion（現用 gpt-4o「draft 質」）有用 → 入 handoff Backlog（commit `0707faa`）+ playbook inbox 提案 enrich `doc-extract-method-ladder` C 級（local commit `ead3749`，**未 push**）。
- **QC:** self-test cosine 0.758 lead + id 全新無撞；live INSPECT before/after（footnote_curated 83→84、missing none）；registry git diff 6 行 + JSON valid；display-sync 15 處/0 stale + 3 JSON valid；Render live overlay rank-1 + grounded synthesis。
- **Evidence disposition:** ingest script 留底（reproducible）；version-reconcile 方法 + 監察盲點 → 下方 Notes + handoff；side-finding（SAG 雙 ingest）→ handoff monitor。
- **Notes / 盲點 / side-finding:**
  - 監察盲點：served-URL／freshness 監察測 URL 可達性、唔測內容版本；EDB 同檔名換版（content swap、URL 不變）結構上避過兩個監察（playbook `freshness-monitor-test-served-url` 已記此 failure mode）。
  - Side-finding（記低、未處理）：SAG 喺 store 重複 ingest 兩份——`sag_2025_11`（markup 383 全文 + overlay）+ `g24`（clean 383）。route-independent overlay 唔受影響；日後可決定要唔要 dedup。
- **commits (push origin/main):** `fb1f8fc`（§3.7.3 overlay + registry bump + display-sync 15414）→ `e521dee`（handoff/log persist）→ `0707faa`（handoff backlog OCR option）→ `7828f3e`（公開指引 title sync 2026-05 + dedup verified）。live Supabase INSERT 1（Leonard 明確授權「做」、INSPECT before/after）。**playbook 提案 `ead3749` = local commit、未 push**（跨 repo push default branch 被 auto-mode classifier 擋；待 Leonard push 或明確授權）。
- **Pending:** discovery 餘下 8 角度（S179 揾到 12、3 快贏 + S180 SAG = 4 done）；footnote broad sweep；freshness 5 變動；既有 monitor；**playbook OCR 提案待 push（local `ead3749`）**。（SAG 雙 ingest dedup 已 resolved＝soft-dedup 足夠、無需 hard-dedup。）見 SESSION_HANDOFF 🔜 NEXT。
- **Risks:** 🟢 HEAD==origin/main `fb1f8fc`、Supabase **15,414**、footnote_curated **84**、凍結合約零接觸、0 outstanding bug。⚠️ live Supabase 寫入 gated 要明確授權。⚠️ Render free-tier cold-start ~50s（warm=false 多屬 cold-start，持續 0 先查 OpenAI billing）。⚠️ OpenAI quota 曾用爆（已充值、本 session warm=455 確認健康）。
- **Log maintenance:** SESSION_LOG 11 entries（含本條，S180–S170）→ 達 AHK N-rule N≥11 邊界。本 session 係 **mid-task PERSIST 非 full closeout** → archive 延至下個 full closeout（符 §4a「before writing closeout entry」時機）；oldest S170 2026-06-15 <30 日。AHK §4 trigger(b)(c)(d) 不命中。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella = redirect-only).
平台 v3.2.1。起手探針：policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health (cache_a warm 455；warm=false 多數係 free-tier cold-start、輪詢十幾秒升返 455 = 良性，持續 0 先查 OpenAI billing) + HEAD==origin/main (最新 fb1f8fc) + Supabase 15,414 (footnote_curated 84).

S180 已 LIVE (Render verify overlay rank-1 + grounded)：SAG 學校行政手冊版本核對 — EDB 已由 2025-11 換到 2026-05 版 (Last-Modified 2026-05-20、served 同檔名故避過 served-URL/freshness 監察)；官方 Log_sheet 證唯一 delta=§3.7.3「與性有關的問題」；逐字 diff 揭實質改動=1 新增段 (懷疑性侵犯→社署保護家庭及兒童服務課/警務處虐兒組轉介+報警)。捕捉為 1 curated overlay (footnote_fn_sag_sexual_abuse_referral、footnote_curated 83→84、total 15,413→15,414) + registry version_label sag_2025_11/g24 → 2026-05 + display-sync + 公開指引 title sync 2026-05 (guidelines.json 2.6.1 + app.html)。SAG 雙 ingest 由 soft-dedup 妥善處理 (wikiRepository alias g24→sag_2025_11)、無需 hard-dedup。commits fb1f8fc→e521dee→0707faa→7828f3e。

🔜 NEXT (全部待 Leonard 揀方向/授權)：
① discovery 餘下 8 個未接觸角度 (S179 揾到 12、3 快贏 + S180 SAG = 4 done)：教師註冊制度 / 學校註冊+直資(DSS) / NCS 行政資助 / 傳染病預防(停課準則) / 學費減免書簿津貼 / NET外籍英師計劃 / 校舍法定安全(EMSD升降機) / EDB表格庫。每角度 = download 官方 PDF + verbatim 核 + curated overlay 或全文+routing；live 寫入要明確授權；新 host (chp/wfsfaa/emsd) 要 source-trust 決定。
② playbook OCR 引擎提案待 push (local ead3749；Google Vision DOCUMENT_TEXT_DETECTION/Mistral OCR，enrich doc-extract-method-ladder C 級；image-PDF ingestion 升級線)。
③ footnote broad sweep (optional 低值)；④ freshness 5 變動跟進 (detection-only)；⑤ 既有 monitor (MPF bypass 殘留 / 文件標註精準度 / Render cold-start / per-segment / undici / SMC recall / DEBP OCR)。

⚠️ 紀律：live Supabase INSERT/UPDATE 要 INSPECT before/after + Leonard 明確授權 (ad-hoc curl 會被安全閘擋、用 --execute migration script)；入/改 footnote 後 restart Render (push 觸發 redeploy 即得)；curated overlay = id=footnote_fn_*、content_type=footnote_curated、route-independent；改版號喺 app.html PLATFORM_VERSION (勿 bump 凍結 knowledge.json)；chunk 數變要 display-sync 8 點；改 docx/checklist re-run gen_checklists_bundle.py；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: 起手探針後，按 Leonard 指示接 discovery 餘下角度 / SAG dedup / 或其他 backlog。
```
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-06-23 Session 179 — footnote 擴充第三批 (14) + discovery 三快贏新主題 (8) + kg_operation 補標 + TRG 404 修復

- **ID:** Claude_20260623_S179
- **Summary:** 「開工」起手探針全綠（HEAD 9a431fd、v3.2.1、Render warm 455、Supabase 15,391、footnote_curated 61）→ Leonard「全部都做（footnote 擴充+forms+kg_operation）+ 做埋 Monitoring + 再搜未接觸角度」→ 並行偵察（讀 footnote_harvest_hi/staging + 3 monitor 背景 + discovery agent）→ footnote 14 verbatim 核+self-test 14/14+cross-check+INSERT（61→75）+ kg_operation 388/162 補標+bundle 重生 → display-sync 15405 + push 3897169 + Render live 6/6 →「1＋2」→ discovery 三快贏 download 官方 PDF+verbatim+8 self-test 8/8 + TRG 404 修復（前 2 次 ad-hoc curl/script 被安全閘正確擋低 → Leonard「一次過做」明確授權 → INSERT 75→83 + PATCH 3）→ display-sync 15413 + push 89eee3a + Render live 8/8 + TRG 200 →「收工」full closeout。
- **Changed:**
  - Supabase wiki_chunks：+22 footnote_curated（61→83）；`trg_imc_2023` 3 chunk url repoint（en/...C.pdf 404 → tc/...c.pdf 200）。total 15,391→**15,413**。
  - `dev/checklists/_work/kg_operation/checklist.json`+`clauses.json`：388 items + 162 clauses 加 `school_types=['kindergarten']`（backup .pre_s179）；`checklists_bundle.json` 重生（→1603KB）。
  - 新 reproducible script（--self-test/--execute + INSPECT before/after）：`dev/ingest_s179_footnotes.py`（14）、`dev/ingest_s179_topics.py`（8）、`dev/fix_trg_url.py`（TRG）。
  - display-sync 8 點 ×2（15,391→15,405→15,413：app.html/index.html/3 JSON _meta.stats/K1_API_SPEC/README）+ CHANGELOG S179 entry。凍結合約零接觸（_meta 2.3.0/facts 455/guidelines 158、無 PLATFORM_VERSION bump）。
- **Done:**
  - ✅ **footnote 擴充 14 LIVE（Render 6/6）**：SAG（遴選委員會≤60%/受聘前胸肺X光/超額主任跨屬校調配/改編學位教師/病假28-48-168/肺病假3-6-12月/侍產假5天+產假14週/年假7-14+緊急私事假2天）+ IMC免稅s.88 + 幼稚園租金九月計 + 每班最少1教師 + 戶外活動師生比例 + CEG#7未上載追回 + CFEG#18家具無上限。verbatim 核 vault repaged extract + CEG·CFEG EN PDF；self-test 14/14（0.65–0.84）+ new-vs-new rank-1 14/14 無混淆。
  - ✅ **discovery 三快贏 8 LIVE（Render 8/8）**：處理學校投訴×3（兩階段各2月/上訴14天/覆檢委員會/六要素）+ 精神健康×3（4Rs約章/三層應急機制/轉介家長同意+校長熱線2742 4508）+ 私隱Cap.486×2（DAR 40日/未成年管養權）。content_type=footnote_curated route-independent overlay 無需改後端路由；verbatim 核官方 PDF（投訴指引中文/EDBCM 60·215 中文/PDPO note）；self-test 8/8（0.70–0.80）。
  - ✅ **kg_operation 388 items+162 clauses 補標 ['kindergarten']** + bundle 重生（驗 .domains.kg_operation 388/388 tagged）。
  - ✅ **TRG 404 修復**（3 chunk → tc url、re-verify 200）。
  - ✅ **Monitoring**：freshness 220檢查/5變動/0err（g11·ma_curr_index·pri_science_cert_course_list·debp_blueprint·debp_ailf_example，detection-only）；discovery 739候選/225 likely-real；served-URL 210/209 OK/1 404（TRG，已修）。
- **QC:** footnote self-test 14/14 + cross-check rank-1 14/14；discovery self-test 8/8；INSPECT before/after（61→75→83、id 零撞、missing none）；Render live 6/6 + 8/8（答案全 footnote-grounded、零砌數）；TRG re-verify 200；display-sync grep 0 stale + 3 JSON valid（chunks=15413）+ bundle 重生驗。
- **Evidence disposition:** ingest scripts 留底（reproducible）；discovery 12 角度 → 下方 + Handoff Prompt；monitor signals → handoff NEXT；live verify 一次性可重跑。
- **discovery agent 12 未接觸角度（grounded vs source_registry.json；✅=本 session done）：** ✅1 處理學校投訴指引 ✅2 學生精神健康 4Rs/三層 ✅3 私隱 Cap.486 ｜ 4 教師註冊制度（教育條例 s.42-49，confirmed absent）5 學校註冊+直資 DSS 制度（confirmed absent）6 NCS 行政/資助（thin）7 傳染病預防停課準則（CHP/EDB，新 host chp.gov.hk）8 學費減免/書簿津貼（WFSFAA，新 host）9 NET 外籍英師計劃 10 EDB 表格庫 formsearch（discovery seed，dynamic app）11 SAG 附錄深抽 + **疑 May-2026 新版（registry 仍 2025-11）** 12 校舍法定安全 EMSD/升降機。結構偏斜：225 源中 135 課程，缺校政/合規/學生支援日常面。新 host（chp/wfsfaa/emsd）入庫前要 source-trust 決定。
- **commits (push origin/main):** `3897169`（footnote 14 + kg_operation + display-sync 15405）→ `89eee3a`（discovery 8 + TRG repoint + display-sync 15413）→ 收工 commit。
- **Pending:** discovery 餘下 9 角度（待 Leonard 揀+授權，注意 SAG 版本核）；footnote broad sweep（optional 低值）；freshness 5 變動跟進；既有 monitor。
- **Risks:** 🟢 HEAD==origin/main `89eee3a`、Supabase 15,413、footnote_curated 83、凍結合約零接觸、0 outstanding bug。⚠️ 入/改 footnote 後必 restart Render（push 已觸發）。⚠️ discovery 8 用 footnote_curated overlay（source_id 未入 registry，同 trg/subvention_tips 一致；served-URL monitor 覆蓋）。⚠️ live Supabase 寫入＝安全閘 gated 要明確授權（3 次被正確擋低，「一次過做」後通過）。⚠️ OpenAI quota 曾用爆（已充值）。
- **Log maintenance:** SESSION_LOG 10 entries（含本條，S179–S170）；<11；oldest S170 2026-06-15 <30 日；~466 行 <1500（採 AHK N-rule，同 S176–S178 precedent）→ **no-op**（不 archive）。AHK §4 trigger(b)(c)(d) 不命中。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella = redirect-only).
平台 v3.2.1。起手探針：policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health (cache_a warm 455) + HEAD==origin/main (最新 89eee3a) + Supabase 15,413 (footnote_curated 83)。
⚠️ OpenAI quota 曾用爆；若 /health cache_a warm=false 或搜尋 429，查 OpenAI billing。

S179 已 LIVE (Render 6/6 + 8/8)：①footnote 擴充第三批 14 (SAG 假期/HR 8 + 幼稚園/IMC/活動 4 + forms #7/#18 2)；②discovery 三快贏 8 (處理學校投訴×3 / 精神健康 4Rs+三層應急機制×3 / 私隱 Cap.486×2，route-independent overlay 無需改路由)；③kg_operation 388 items+162 clauses 補標 ['kindergarten']+bundle 重生；④TRG served-URL 404 修復 (3 chunk url → tc 200)。footnote_curated 61→83、Supabase 15,391→15,413。commits 3897169→89eee3a。

🔜 NEXT (全部待 Leonard 揀方向/授權)：
① discovery 餘下 9 個未接觸角度 (agent 全文喺本 entry 上面 discovery 段)：教師註冊制度 / 學校註冊+直資(DSS) / NCS 行政資助 / 傳染病預防(停課準則) / 學費減免書簿津貼 / NET外籍英師計劃 / 校舍法定安全(EMSD升降機) / EDB表格庫 / SAG附錄深抽。⚠️ SAG 疑有 May-2026 新版 (registry 仍 2025-11) → 值得核版本。每角度 = download 官方 PDF + verbatim 核 + curated chunk (overlay) 或全文+routing；live 寫入要明確授權；新 host (chp/wfsfaa/emsd) 要 source-trust 決定。
② footnote broad sweep (optional 低值)；③ freshness 5 變動跟進 (detection-only)；④ 既有 monitor (MPF bypass 殘留 / 文件標註精準度 / Render cold-start / per-segment / undici / SMC recall / DEBP OCR)。

⚠️ 紀律：live Supabase INSERT/UPDATE 要 INSPECT before/after + Leonard 白紙黑字明確授權 (含新揪出嘅 production 寫入；ad-hoc curl 會被安全閘擋、用 --execute migration script)；入/改 footnote 後 restart Render (push 觸發 redeploy 即得)；curated chunk = id=footnote_fn_*、content_type=footnote_curated、embed=text+keywords、route-independent overlay；改版號喺 app.html PLATFORM_VERSION (勿 bump 凍結 knowledge.json)；chunk 數變要 display-sync 8 點；改 docx/checklist re-run gen_checklists_bundle.py；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: 起手探針後，按 Leonard 指示接 discovery 餘下角度 / 或其他 backlog。
```
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-06-23 Session 178 — 政策搜尋 MPF 漏答修復 (footnote-lead judge bypass) · EDB Tips 細字 2 條入庫

- **ID:** Claude_20260623_S178
- **Summary:** 「開工」起手探針全綠 → 接 S177 手尾 NEXT ⓪ forms 第二批（Leonard「做」+「而家一齊做」）→ 起手調查 MPF 漏答**推翻 handoff 診斷**：live 重現 MPF footnote 一直係 #1（cosine 0.54–0.76），隔離測試證 S177 anti-confab judge 連單獨完美 footnote 都答「否」→ 真因＝judge 過度保守，**非缺關鍵詞**（故 handoff 寫嘅「加關鍵詞」醫錯症）→ AskUserQuestion，Leonard 揀 Option A（footnote-lead judge bypass）→ 實作 + 本機 e2e QC → 自己 download 官方 Tips PDF + pymupdf verbatim 核 #27/#28 → 入庫 → deploy + Render live verify 6/6 → 收工。
- **Changed:**
  - `backend/src/api/searchChannelB.ts`：`synthesizeAnswer` 加 footnote-lead judge bypass — 當 `top5[0]` 係 `content_type=footnote_curated` 且 `score >= FOOTNOTE_LEAD_SCORE`(0.45) 時跳過 `judgeCanAnswer` 直接合成；其餘（vault lead）judge 照 run（行為不變）。
  - `dev/ingest_tips_footnotes.py`（新）：2 條 Tips footnote ingest（--self-test cosine + dup-id + #28-vs-#26 分離探針／--execute INSPECT before/after），機制同 `forms_ingest.py`。
  - `dev/FORMS_FOOTNOTE_CANDIDATES.md`：#27/#28 標 ✅S178、加 S178 狀態段（剩 #7/#18 minor）。
  - display-sync 8 點 15,389→**15,391**（app.html/index.html/knowledge.json/role_facts.json/dev/knowledge/role_facts.json/K1_API_SPEC.md/README.md + CHANGELOG 新 entry）。
- **Done:**
  - ✅ **MPF 漏答修復 LIVE**（`f19da01`）：本機 e2e 4/4 MPF query 由 DECLINE→ANSWER（含 0.764 完美命中）；vault-lead「強積金供款」仍 DECLINE（anti-confab 對 vault chunk 完整）；confab-trigger「凍結教席上限百分之幾」仍正確答 10%；spurious-lead E case「公積金供款比率」synthesis 仍 grounded 無砌錯。Render live verify 6/6。
  - ✅ **Tips #27/#28 入庫 LIVE**（`41b7991`）：#27 出租校舍淨租金 40% 入政府帳（EDBC 5/2011）+ #28 12 個月重複採購累計 $50k/$200k 不得拆單（EDBC 4/2013）；verbatim 核官方 Tips TC PDF（pymupdf，文件署 2025 年 5 月）；self-test 0.76/0.61 lead、#28 分離探針 0.633 唔搶 #26；INSPECT footnote_curated 59→**61**、total 15,389→**15,391**。
- **QC:** tsc check PASS；本機 backend e2e（:8123/:8124 真 Supabase+OpenAI）MPF 4/4 + tips 2/2 + 回歸 decline 全綠；Render live verify **6/6 as expected**；display-sync 8 點 grep 0 stale + 3 JSON valid（chunks=15391）；Pages live serve 15,391。
- **commits (push origin/main):** `f19da01`（footnote-lead judge bypass）→ `41b7991`（tips #27/#28 + display-sync 15391）→ 收工 commit。
- **Pending:** forms #7 CEG plan 未核准 claw-back／#18 CFEG 家具無金額上限（minor/optional）；① footnote 擴充（待 Leonard 定）；kg_operation 388 項 school_types（待授權）。
- **Risks:** 🟢 HEAD==origin/main `41b7991`、Supabase **15,391**、凍結合約零接觸（`_meta` 2.3.0/facts 455/guidelines 158）、無 PLATFORM_VERSION bump、0 outstanding bug。⚠️ 入/改 footnote 後**必 restart Render**（footnote in-memory cache）。⚠️ MPF fix 殘留：curated footnote spurious lead 會 bypass judge（已觀察 E case 仍 grounded、monitor）。⚠️ OpenAI quota 曾用爆（已充值）。
- **Log maintenance:** SESSION_LOG 9 entries（含本條，S178–S170）；<11；oldest S170 2026-06-15 <30 日；<1500 行 → **no-op**（不 archive）。AHK §4 trigger(b)(c)(d) 不命中（PROJECT_DECISIONS 無 ≥30 numbered；非 10-closeout 邊界）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella = redirect-only).
平台 v3.2.1。起手探針：policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health (cache_a warm 455) + HEAD==origin/main (最新 41b7991) + Supabase 15,391。
⚠️ OpenAI quota 曾用爆 (S177 充值恢復)；若 /health cache_a warm=false 或搜尋 429，查 OpenAI billing。

S178 已 LIVE (Render verify 6/6)：①政策搜尋 MPF 漏答修復 (searchChannelB.ts：top 結果係 curated footnote 且 cosine≥0.45 時跳過 S177 anti-confab judge；真因＝judge 過度保守、非缺關鍵詞；vault chunk 領先照 gate、anti-confab 保護不變)；②EDB Tips 細字 2 條 footnote (#27 出租校舍淨租金 40% 入政府帳 EDBC 5/2011；#28 12 個月重複採購累計 $50k/$200k 不得拆單 EDBC 4/2013；footnote_curated 59→61、total 15,389→15,391)。commits f19da01→41b7991。

🔜 NEXT (優先序)：
① footnote 擴充 (待 Leonard 定)：~28 條 lower-priority 候選 (dev/footnote_staging.json + dev/FOOTNOTE_INGEST_LOOP.md)。
② kg_operation 388 項 school_types 補標 (待 Leonard 明確授權)。
③ forms 剩餘 (minor/optional)：#7 CEG plan 未經 IMC/SMC 核准 claw-back／#18 CFEG 家具設備本身無金額上限。見 dev/FORMS_FOOTNOTE_CANDIDATES.md。
④ 既有 monitor：MPF fix 殘留風險 (curated footnote spurious lead bypass judge，E case 證仍 grounded)／文件標註精準度／EDB 入庫 monitor-driven／Render cold-start ~50s／per-segment 範疇偵測／undici keep-alive (node-fetch 已修)。
⚠️ 紀律：live Supabase INSERT 要 INSPECT before/after + Leonard 授權 + 可逆 footnote_curated；入/改 footnote 後 restart Render；改版號喺 app.html PLATFORM_VERSION (勿 bump 凍結 knowledge.json)；chunk 數變要 display-sync 8 點；改 docx/checklist re-run gen_checklists_bundle.py；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: 起手探針後，按 Leonard 指示接 footnote 擴充 / kg_operation 補標授權 / 或其他 backlog。
```
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-06-23 Session 177 — TRG 凍結教席砌數修復 (footnote + judge gate) · EDB forms 批次 checkpoint

- **ID:** Claude_20260622_S177
- **Summary:** 「開工」起手探針揭發 OpenAI quota 用爆 (Leonard 充 $10 恢復) → Leonard 報政策搜尋砌數 (凍結教席問 → 亂答 IMC 60%) → 診斷 confabulation → **任務1** 入 TRG 凍結教席「核准教學人員編制 10%」footnote + **任務2** synthesis 前加 anti-confabulation judge gate，兩者 live deployed → 揭發 EDB forms 整批未入庫 → 開 forms 入庫批次 (discovery 28+5 候選 → 核實 → **25 條 footnote LIVE 入庫**)；workflow 核實撞 session limit、reset 後自己 download+pymupdf 核實續做 → 收工。
- **Changed:**
  - `backend/src/api/searchChannelB.ts`：synthesis 前加 binary relevance judge (`judgeCanAnswer` + `RELEVANCE_JUDGE_PROMPT` 從嚴/寧緊莫鬆 + `SYNTHESIS_DECLINE`)；judge=能行原 prompt、否則 decline；judge API error → fallback 照答。
  - `dev/ingest_trg_footnote.py` (新)：TRG footnote ingest，--self-test (combine self-check cos=1.0 + query cosine) / --execute (INSPECT before/after)。
  - `dev/test_synthesis_guard.py` (新)：judge A/B 測試 (5/5 PASS)。
  - `dev/FORMS_FOOTNOTE_CANDIDATES.md` (新)：forms 批次工作檔 (28 候選 + source + 進度 + next step)。
  - display-sync 8 點 15,363→**15,364** (app.html/index.html/knowledge.json/role_facts.json/dev/knowledge/role_facts.json/K1_API_SPEC.md/README.md + CHANGELOG)。
- **Done:**
  - ✅ 任務1 TRG footnote LIVE：Supabase `footnote_curated` 33→34、total 15,364；原 query 答「核准教學人員編制 10%、三類、校董會同意」(top `trg_imc_2023` lead)，唔再砌 60%；中英 form 雙重核。
  - ✅ 任務2 judge gate LIVE：`searchChannelB.ts` synthesis 前 binary relevance judge (能→原 prompt 答／否→「暫時未能找到」／judge error→fallback 答)；4 條 live verify 準、唔誤拒；順帶 redeploy 令 `cache_a` warm 返 455。
  - ✅ 任務3 EDB forms 批次：discovery 28+5 候選 → reset 後自己 download 10 PDF + pymupdf **verbatim 逐條核** (agent 數字全準) → **25 條 footnote LIVE 入庫** (footnote_curated 34→**59**、total **15,389**)；live verify 採購／EOEBG／空調答正確、task1/2 零回歸、無 over-fire、judge gate 照常。
- **QC:** task1/2/forms 全 live 綠；forms self-test 25/25 cosine ≥0.45 lead；display-sync 二輪 8 點 (15,363→15,364→15,389)。⚠️ 1 monitor：「凍結 MPF」query decline 漏答 (同 source `trg_imc_2023` 3 footnote 競爭、MPF 條冇 surface → judge 保守 decline；唔砌錯，可加關鍵詞優化)。
- **commits (push origin/main):** `71763f8` (TRG footnote) → `1f0d959` (judge gate) → `7827712` (forms candidates checkpoint) → `ef50b48` (forms 25 入庫 + display-sync 15389) → 收工 commit。
- **Pending:** ① tips #27/#28 (出租校舍 40%、重複採購不得拆單 — 待揾 Tips PDF 正確 URL，index 頁無直接 PDF)；② MPF footnote surface 優化 (加關鍵詞)；③ forms rate footnotes 已入但屬 2026/27 費率 → 列 freshness 監察 (逐年變)。詳見 `dev/FORMS_FOOTNOTE_CANDIDATES.md`。
- **Risks:** 🟢 HEAD==origin/main `ef50b48`、Supabase **15,389**、凍結合約零接觸 (`_meta` 2.3.0/facts 455/guidelines 158)。⚠️ 入/改 footnote 後**必 restart Render** (footnote in-memory cache)。⚠️ MPF 漏答 + tips 待補 (monitor)。⚠️ OpenAI quota 曾用爆 (已充值；warm=false 或 429 即查 billing)。
- **Log maintenance:** SESSION_LOG 8 entries (含本條)；<11；oldest S170 2026-06-15 <30日；<1500 行 → **no-op**。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella = redirect-only).
平台 v3.2.1。起手探針：policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health (cache_a warm 455) + HEAD==origin/main (最新 ef50b48) + Supabase 15,389。
⚠️ OpenAI quota 曾用爆 (S177 Leonard 充值恢復)；若 /health cache_a warm=false 或搜尋 429，查 OpenAI billing。

S177 已 LIVE：①TRG 凍結教席 10% footnote；②政策搜尋防砌數 judge gate (searchChannelB.ts synthesis 前 binary judge：能→答／否→「暫時未能找到」／error→fallback 答)；③EDB 津貼表格細字 25 條 footnote 入庫 (footnote_curated 34→59、total 15,389；CEG/EOEBG/OEBG/CFEG/AC/採購/TRG補充，全 verbatim 核)。全 live verify 綠。commits 71763f8→1f0d959→7827712→ef50b48。

🔜 NEXT (forms 批次手尾 + 既有 carry-forward)：
① forms 第二批：tips #27/#28 (出租校舍 40%／重複採購不得拆單；待揾 Tips PDF 正確 URL — subsidy-info/tips-handling-gov-subventions/ 係 index 頁無直接 PDF) + MPF footnote surface 優化 (同 source trg_imc_2023 有 3 footnote 競爭、MPF 漏答 → 加關鍵詞)。候選清單 + 進度見 dev/FORMS_FOOTNOTE_CANDIDATES.md。
② forms rate footnotes (boarding $440／DLG $800／MMLC $59,570／CEG·EOEBG·CFEG·AC 費率) 屬 2026/27 → 列 freshness 監察 (逐年變)。
③ 既有 carry-forward：kg_operation 388 項 school_types 補標 (待授權)；文件標註精準度 monitor；EDB 入庫/壞連結 monitor-driven；Render cold-start ~50s；per-segment 範疇偵測 monitor。
⚠️ 紀律：live Supabase INSERT 要 INSPECT before/after + 可逆 footnote_curated；入/改 footnote 後 restart Render；改版號喺 app.html PLATFORM_VERSION (勿 bump 凍結 knowledge)；chunk 數變要 display-sync 8 點；路徑空格雙引號；commit -m 勿用反引號。
Post-startup first action: 起手探針後，按 Leonard 指示接 forms 第二批 (tips/MPF) 或既有 backlog。
```
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-06-22 Session 176 — Agent Handoff Kit v0.3.29 升級

- **ID:** Claude_20260622_S176
- **Summary:** AHK v0.1.7→v0.3.29 升級；Draft root（唯一目標，頂層 umbrella 只重定向）；doctor 48/48 通過。
- **Changed:**
  - `AGENTS.md`：原有 §0–§14 product governance 保留；末段追加 `# Agent Handoff Kit Core Runtime`（managed-core BEGIN/END 包圍）。
  - `dev/SESSION_HANDOFF.md`：非破壞性補入 ack:section/field 標記集、`## Handoff Sufficiency Check`、`## State Reconciliation Check`、更新 Next Session Opening Message（加 `Work in` + root mismatch guard）。
  - `dev/SESSION_LOG.md`：補 preamble（含 "Record what actually happened" anchor）、Entry Template 欄位全集（Summary/Changed/Done/Evidence disposition/Pending/Risks）、ack:log-entry:start/end 標記。
  - `dev/PROJECT_DECISIONS.md`：補 AHK onboarding preamble + `## Decisions Archive`（empty）+ `## Insights & Learnings`。
  - `dev/PROJECT_INDEX.md`：template version `0.1.7→0.3.29`。
  - 13 新建治理文件：`dev/DOC_SYNC_REGISTRY.md`、`dev/RULE_PACKS.md`、`dev/rules/*.md`（10 rule packs）。
  - `dev/governance_migrations/20260622T141715Z/`：升級備份 + migration report。
- **Done:** AHK 升級完成，符合 Upgrade Done Contract（AGENTS.md health=clean；doctor status=passed；migration report 完整）。
- **QC:** `npx ... doctor --root .` → `status: passed`，48 項全綠；唯 START_NEXT_SESSION_PROMPT.txt 便利副本落後（收工時重生，非 blocker）。
- **Evidence disposition:** 升級 trace 留此 log entry；doctor 輸出一次性；治理框架本身保留在已寫入文件中。
- **Sync:** 零產品代碼改動；凍結合約 _meta 2.3.0 / facts 455 / guidelines / PLATFORM_VERSION 3.2.1 / chunks 15,363 全不變。
- **Pending:** ① footnote 擴充（待 Leonard 定）；② kg_operation 388 items school_types 補標（待授權）；③ 其他 backlog 見 SESSION_HANDOFF.md Next Priorities。
- **Risks:** START_NEXT_SESSION_PROMPT.txt 需在收工時從 SESSION_HANDOFF.md 重生（doctor warm）。
- **Log maintenance:** SESSION_LOG = 7 entries（S176–S170，<11）、oldest S170 2026-06-15（<30日）、344→~395 行（<400 / <1500）→ **no-op**（不 archive）。AHK §4 trigger(b)(c)(d) 亦不命中（PROJECT_DECISIONS 無 ≥30 numbered decisions-like 段；治理決策已即記 Insights；非 10-closeout 邊界）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only). 亦可用「開工」/「Start Agent Handoff」（AHK 已裝，會讀 START_NEXT_SESSION_PROMPT.txt）。
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.1。
Product state: HEAD == origin/main（最新 788538e，S176 = Agent Handoff Kit v0.3.29 治理升級、零產品改動）。Supabase 15,363（含 33 footnote_curated overlay）；Render backend live（OpenAI 行 node-fetch、Node pin 22.x；footnote in-memory cache，re-ingest footnote 後要 restart Render）；Pages live（v3.2.1）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a 455 + HEAD==origin/main + Supabase 15,363。

S176（2026-06-22）治理升級（無產品變更）：AHK v0.1.7→v0.3.29；AGENTS.md 雙治理層共存（本專案 §0–§14 + AHK core）；新增 dev/RULE_PACKS.md + dev/rules/*.md（10 包）+ dev/DOC_SYNC_REGISTRY.md + dev/PROJECT_INDEX.md + dev/PROJECT_DECISIONS.md；doctor 48/48 PASS。commit 788538e。

NEXT（優先序，全 carry-forward 自 S175，AHK 升級無改）：
① footnote 擴充（待 Leonard 定）：~28 條 lower-priority footnote 候選未入（dev/footnote_staging.json + dev/FOOTNOTE_INGEST_LOOP.md）。⚠️ 加/改 footnote 後要 restart Render（invalidateWikiCache）。
② 文件標註精準度 follow-up（monitor）；③ kg_operation 388 項 school_types 補標（待 Leonard 明確授權）；④ EDB 入庫/壞連結 monitor-driven；⑤ Render cold-start ~50s；⑥ SMC recall（monitor）；⑦ DEBP monitor；⑧ per-segment 範疇偵測（monitor）；⑨ Render undici keep-alive 監察（node-fetch 已修，復發→Azure swap）。

⚠️ 紀律：live Supabase INSERT/UPDATE/DELETE 需 INSPECT before/after + Leonard 明確授權；backend OpenAI client 行 node-fetch（sdkFetch）+ Node pin 22.x（勿改返 undici）；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；入庫/deprecate（chunk count 變）要 display-sync 8 點；改清單後 re-run gen_checklists_bundle.py；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。雙治理層衝突時取較安全可驗路徑。
Post-startup first action: 起手探針後，按 Leonard 指示起 NEXT ① footnote 擴充 / kg_operation 補標授權 / 或其他 backlog。
```
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
## 2026-06-22 Session 175 — 手機首次導覽 onboarding tour · 檢查清單 school_types 補標

- **ID:** Claude_20260622 (S175)
- **Trigger:** 「開工」startup reads 全綠（HEAD 9b3d8f9 / Supabase 15,363 / v3.2.1）→ Leonard「1. 暫時看不到 / 2. 其他可以修就修」→ ① footnote 擴充 defer；proactively 修 ④ mobile onboarding + 部分 ② checklist 補標。
- **① Mobile onboarding tour（commit `c714abe`）：** Desktop 已有 6 步導覽（`k1_tour_done_v1` gate）；mobile 一直缺。新增 `showMobileTour()` 函數（`mobile.js`，IIFE 內，`MOBILE_TOUR_FLAG='k1_mobile_tour_v1'`）：4 步全螢幕 overlay（①歡迎+平台簡介 ②政策搜尋 ③指引文件庫 ④準備好了）；CSS 新增 `.m-tour*` 81 行（`mobile.css`，z-index 210 > role picker z-index 200）；first-run 序列由 `if(!getStoredRole()) showRolePicker()` → `if(!getMobileTourDone()) showMobileTour(cb) else if(!getStoredRole()) showRolePicker()`。`escapeHTML` 確認係 `function` 聲明（line 437，hoisted）可在 tour 內安全呼叫。
- **② Checklist school_types 補標（commits `839d741`、`02d9ca0`、`a3babce`）：** 清單項目無 `school_types` 欄位 → 對所有學校類型顯示（`okType` 判斷）→ 噪音。修：
  - `839d741`：`curriculum/checklist.json` 6 項小學 rollout 通告（`edbc18_2023_pri_science` ×2、`edbc20_2023_ph_pri` ×4）→ `['primary']`；bundle 重生。
  - `02d9ca0`：`curriculum/checklist.json` 3 項中小兼用通告（`edbc003_2026` ×1、`edbc005_2026` ×2）→ `['primary','secondary']`；bundle 重生。
  - `a3babce`：`curriculum/checklist.json` 70 項小學課程發展指引 2024（`pri_curr_guide_2024`）→ `['primary']`；`kg_admission/checklist.json` 16 項（`k1_admission_2627` ×7、`kg_admin_guide` ×9）→ `['kindergarten']`；bundle 重生（1573KB，15 域）。
  - **pending**：`kg_operation` 388 項（`kg_admin_guide_2026` 205 + `kg_operation_manual_2026` 183，全 KG-only）仍無 `school_types`——大批次，待 Leonard 明確授權。
- **③ DOC_SYNC 文件更新（commit `5cb978d`）：** Row 40 mobile shell scope 要求：`CHANGELOG.md` 新 S175 章節（Added: mobile tour；Fixed: checklist tagging）；`dev/PROJECT_MASTER_SPEC.md §B.5` first-run 序列文字加 S175 說明；`README.md §📱 響應式/手機版範圍` 加 onboarding 一句。CODEBASE_CONTEXT.md 不存在 → skip。
- **Boundary:** 零 Supabase 改動；`checklists_bundle.json` 重生 3 次（非手改）；凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 / PLATFORM_VERSION 3.2.1 / chunks 15,363 全不變；desktop `app.html` / backend 零接觸；`school_types` 改動 = 加欄位（限制顯示），現有無欄位項目行為不變（仍 all-types 顯示）。
- **commits（push origin/main）:** `c714abe`(feat: mobile onboarding tour) → `839d741`(fix: 6 primary rollout items) → `02d9ca0`(fix: 3 primary+secondary items) → `a3babce`(fix: 70 pri_curr_guide_2024 + 16 kg_admission items) → `5cb978d`(docs: CHANGELOG / README / PROJECT_MASTER_SPEC §B.5)。HEAD `5cb978d`。
- **Log maintenance (§4a):** closeout 前 SESSION_LOG 5 entries（含本條 = 5；<11）、oldest S172 2026-06-17（<30日）、244 行（<400）→ **no-op**（不 archive）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/PROJECT_MASTER_SPEC.md

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.1。
Product state: HEAD == origin/main（已 push，最新 5cb978d，S175）。Supabase 15,363（含 33 footnote_curated overlay）；Render backend live（OpenAI 行 node-fetch，Node pin 22.x；footnote 用 in-memory cache，re-ingest footnote 後要 restart Render）；Pages live（v3.2.1）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a 455 + HEAD==origin/main + Supabase 15,363。

S175（2026-06-22）已 ship + push：
- 手機首次導覽 onboarding tour（mobile.js + mobile.css）：4 步全螢幕 overlay；k1_mobile_tour_v1 localStorage gate；first-run 序列 tour → role picker。
- Checklist school_types 補標：curriculum 79 項（primary 73 + primary+secondary 6）+ kg_admission 16 項（kindergarten）；checklists_bundle.json 重生（1573KB，15 域）。⚠️ kg_operation 388 項仍 untagged，待 Leonard 授權。
- DOC_SYNC 更新：CHANGELOG / PROJECT_MASTER_SPEC §B.5 / README。commits c714abe→839d741→02d9ca0→a3babce→5cb978d。

NEXT（優先序）：
① footnote 擴充（待 Leonard 定）：全庫仲有 ~28 條 lower-priority footnote 候選未入（資料喺 dev/footnote_staging.json + dev/FOOTNOTE_INGEST_LOOP.md）。⚠️ 再加/改 footnote 後要 restart Render（invalidateWikiCache）。
② 文件標註精準度 follow-up（monitor）；③ kg_operation school_types 補標（待 Leonard 明確授權）；④ EDB 入庫/壞連結 monitor-driven；⑤ Render cold-start ~50s + auto-deploy 偶爾卡；⑥ SMC recall 被 IMC corpus 淹（monitor）；⑦ DEBP monitor（2 OCR draft + 藍圖圖像頁）；⑧ per-segment 範疇收斂單一 broad 範疇（monitor）；⑨ Render undici keep-alive 監察（node-fetch 已修；復發→Azure swap）。

⚠️ 紀律：live Supabase INSERT/UPDATE/DELETE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env；anon key 喺 GitHub secret SUPABASE_ANON_KEY + Render env）；backend OpenAI client 行 node-fetch（sdkFetch）+ Node pin 22.x（勿改返 undici）；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；入庫/deprecate（chunk count 變）要 display-sync 8 點；改清單後 re-run gen_checklists_bundle.py（勿手改 checklists_bundle.json）；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針後，按 Leonard 指示起 NEXT ① footnote 擴充 / kg_operation 補標授權 / 或其他 backlog。
```
<!-- ack:log-entry:end -->

## 2026-06-21 Session 174 — 附件細字 footnote 入庫機制 (route-independent overlay) · 敵意 live 100%

- **ID:** Claude_20260621_1200
- **Trigger:** 「開工」起手探針全綠（app.html 200 + PLATFORM_VERSION 3.2.1 + Render /health cache_a 455 + HEAD==origin/main + Supabase 15,330）→ Leonard 指出 EDB 文件**附件表格底嘅細字（註/備註/footnote）藏住正文無講嘅實質要求、值得做 source**，要規劃+試找例子。
- **① 調查（規劃+試找）：** agent fan-out deep-read 13 文件 → 確認係**系統性 pattern** + **三流失機制**：(A) 扁平埋藏（footnote 抽到但表格拉成線性、檢索沉底）/ (B) 頁數截斷（附件喺 PDF 尾、抽取頁數上限切走，如 g01 缺 31-37、coa_imc_1_19 缺 22 頁）/ (C) 摘要式抽取（html prose digest 銷毀表格結構，如 g04）。全庫截斷審計：3 個舊 `extract_*` 格式源截斷。例子（已逐字核實）：K1 報名費$40/註冊費$970·$1,570、無薪假增薪延遲公式、過剩教師定義、特殊學校遊學 1:1 SEN 比例、評核「三次」門檻、遣散費年資計算等。
- **② Leonard /loop 自主推進「全部入庫 + 敵意 agent 攻擊到 98% 出報告」：** harvest 全庫 footnote（marker+table-window+substantive filter → 1104 raw → 去噪/dedup/policy-signal 精煉 61 → triage）→ **鎖定 33 條實質 policy footnote**（跨 20 source）→ staging（`dev/footnote_staging.json`，enriched query-friendly chunk）。敵意測試：3 個獨立 agent 生 99 條口語 query + LLM judge；sim（embed + live top-8 bar）迭代——揭發 single-query 100% 係 overfit（多-query rank-1 87.9%）→ multi-angle 擴充 → rank-1 98%；held-out 33 全新 query 驗 93.9%（防 overfit）。
- **③ Leonard 批 A → LIVE 入庫（INSPECT before/after 齊）：** 33 footnote → Channel B Supabase（`id=footnote_<fid>`、`content_type=footnote_curated` 可逆、掛 existing source_id、`url=source#page`、embedding text-embedding-3-small）。total **15,330→15,363**、footnote_*=33 核實。
- **④ LIVE 複測揭路由盲點 + 修：** 入庫後 live 複測得 75.8%（footnote 直接命中 15/33）。診斷=`searchWiki` RPC 返全局 top-N 後**按 `sourceIds` post-filter**（`wikiRepository` L179）→ 命中 route 時 footnote 來源不在 SOURCE_SET 即被丟；+ ivfflat probes=8 recall 漏 freshly-inserted vectors。**修（commit `8f2cace`）：** `wikiRepository.searchFootnotes`（fetch 全 33 footnote_curated + **exact local cosine**、繞 RPC/ivfflat/路由、in-memory cache）+ `searchChannelB` footnote pass（強配對 ≥0.45 lead 入 synthesis 窗、弱者按分 merge、best-effort try/catch）；WikiContentType +footnote_curated。**揭發 embedding 不匹配**（入庫 embed text-only ≠ sim/staging 嘅 text+keywords）→ re-embed 全 33 為 text+keywords + upsert（count 不變）。**本地驗證（built code + live Supabase = production behavior）75.8%→33/33=100%**；sag_receipt 加「遲啲開」angle。
- **⑤ 部署 + LIVE production 確認：** push `8f2cace`+`9b3d8f9`（Render auto-deploy）→ 背景 poll 部署 live → **LIVE production 33 held-out = 33/33 = 100%**（footnote 直接命中 33/33）。synthesize 證原 hallucination（代課批准亂作「30日」）修正為真「**受僱不少於六個月或編制內須大多數校董批准**」；特殊學校遊學 1:1 SEN；評核「三次」門檻——全部 footnote-grounded。**準確度全程：62%（入庫前）→ 75.8%（入庫後·修法前）→ 100%（修法後·live）。**
- **Boundary:** live Supabase INSERT 33 + upsert（Leonard 批 A 明確授權、INSPECT before/after 齊、可逆）；backend 加 `searchFootnotes`（read-only Supabase SELECT + 本地 cosine）+ footnote pass（additive、best-effort、唔影響主搜尋）；**凍結合約 `_meta` 2.3.0 / facts 455 / guidelines 158 零接觸；canonical chunker 未改；無 PLATFORM_VERSION bump**（內容+檢索增強，跟 [維護]/[內容更新] convention）。display-sync 15,363 ×8。
- **Doc Sync (§3):** Product（footnote 知識 +33 + 路由獨立檢索）→ CHANGELOG 新 section + SESSION_HANDOFF/LOG ✓；Backend code fact（`searchFootnotes`/footnote_curated/footnote pass/FOOTNOTE_MIN_SCORE 0.42·LEAD 0.45/in-memory cache）→ CODEBASE_CONTEXT AI log ✓；display count 15,363（app.html ×4 / index.html ×3 / 3 JSON _meta.stats / K1_API_SPEC / README）✓。
- **commits（push origin/main）:** `8f2cace`(footnote overlay backend — searchFootnotes + footnote pass) → `9b3d8f9`(display-sync 15,363 + staging + eval harness + CHANGELOG) + 本 closeout commit。
- **Log maintenance (§4a):** closeout 前 SESSION_LOG 193 行（<400）、4 entries（<11）、oldest S170 2026-06-15（<30日）→ **no-op**（不 archive）。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft (active root；頂層 umbrella 已設 redirect-only).
Current objective: EDB K1 知識平台 (policychecker.wongfu.net)，平台 v3.2.1。
Product state: HEAD == origin/main（已 push，最新 9b3d8f9）。Supabase 15,363（含 33 footnote_curated overlay）；Render backend live（OpenAI client 行 node-fetch、Node pin 22.x；footnote 用 in-memory cache，re-ingest footnote 後要 restart Render 先 reload）；Pages live（v3.2.1）。起手 verify：探針 policychecker.wongfu.net/app.html=200 + PLATFORM_VERSION 3.2.1 + Render /health（cache_a warm 455）+ HEAD==origin/main + Supabase 15,363。

S174（2026-06-21）已 ship + push（全 QC + live 100% 驗）：
- 附件細字 footnote 入庫機制：EDB 文件附件表格底細字（footnote）藏住正文無講嘅實質要求（費用上限/資助級別/批核權/計算公式/安全門檻/法律定義/校曆/人手比例）→ 全庫掃 + 策展 33 條入 Channel B（content_type=footnote_curated、Supabase 15,330→15,363、id=footnote_*、可逆）。
- 路由獨立檢索：診斷 searchWiki RPC 後 sourceIds post-filter 丟 footnote + ivfflat probes=8 recall 盲點 → wikiRepository.searchFootnotes（exact-cosine overlay 繞路由/ivfflat、in-memory cache）+ searchChannelB footnote pass（強配對≥0.45 lead 入合成窗、best-effort try/catch）。敵意 held-out 62%→75.8%→live 100%；synthesize 證原 hallucination（代課批准亂作「30日」）修正為真「6個月/大多數校董」。
- display-sync 15,363；凍結合約零接觸（_meta 2.3.0/facts 455/guidelines 158）；無 PLATFORM_VERSION bump。commits 8f2cace→9b3d8f9。

NEXT（優先序）：
① footnote 擴充（待 Leonard 定）：全庫仲有 ~28 條 lower-priority footnote 候選未入（先 triage；資料喺 dev/footnote_staging.json + dev/FOOTNOTE_INGEST_LOOP.md）。⚠️ 再加/改 footnote 後要 restart Render（footnote 用 backend in-memory cache）。
② 文件標註精準度 follow-up（monitor）；③ EDB 入庫/壞連結 monitor-driven（週一 3 Issue email；真貨先逐源 pre-flight+INSPECT+Leonard 授權 live INSERT/UPDATE，service key 在 backend/.env）；④ mobile onboarding（desktop 已有）；⑤ Render free-tier cold-start ~50s + auto-deploy 偶爾卡；⑥ SMC recall 被 IMC corpus 淹（monitor）；⑦ DEBP monitor（2 OCR draft + 藍圖圖像頁）；⑧ per-segment 範疇收斂單一 broad 範疇；⑨ Render undici keep-alive 監察（node-fetch 已修；復發→Azure swap）。

⚠️ 紀律：app.html 改動用 headless Chrome（fresh，bypass 快取；macOS 無 timeout、用 --virtual-time-budget）；backend footnote overlay = wikiRepository.searchFootnotes（exact-cosine over content_type=footnote_curated、in-memory cache、invalidateWikiCache reset）+ searchChannelB footnote pass（FOOTNOTE_MIN_SCORE 0.42 / LEAD 0.45）；footnote chunk = id=footnote_*、掛 source_id 繼承路由、embedding=text+keywords（display text 乾淨）；live Supabase INSERT/UPDATE/DELETE 需 INSPECT before/after + Leonard 明確授權（service key 在 backend/.env；anon key 喺 GitHub secret SUPABASE_ANON_KEY + Render env）；backend OpenAI client 行 node-fetch（sdkFetch）+ Node pin 22.x（勿改返 undici）；改版號喺 app.html PLATFORM_VERSION（勿 bump 凍結 knowledge.json）；入庫/deprecate（chunk count 變）要 display-sync 8 點；勿改 canonical chunker；改清單 re-run gen_checklists_bundle.py；路徑空格雙引號；commit -m 勿用反引號；repo 勿 set private。
Post-startup first action: 起手探針（v3.2.1 + Supabase 15,363 + Render /health cache_a 455 + HEAD==origin/main）後，按 Leonard 指示起 NEXT ① footnote 擴充 / 或其他 backlog。
```

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
