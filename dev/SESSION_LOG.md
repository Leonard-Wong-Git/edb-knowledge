# Session Log
<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->

> **Handoff role**: This log is the trace-back / audit trail layer. Handoff capability rests on `dev/SESSION_HANDOFF.md`. The next AI session can continue by reading `AGENTS.md` + `dev/SESSION_HANDOFF.md` + `dev/PROJECT_INDEX.md` + needed rule packs; reading this log is not required for continuity. Each closeout applies `dev/rules/closeout.md` `## Maintenance Trigger Check`; that owner defines the current thresholds and archive discipline.

Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

This log carries recent evidence, not current state. Put the current objective, next action, risks, and workspace identity in `dev/SESSION_HANDOFF.md`.

Keep recent entries concise. If older entries no longer affect the next action and the current maintenance assessment establishes cleanup is required, reduce them to short dated indexes that point to the durable source of truth. Archive long error output, validation detail, or research trails only when actual maintenance requires it; do not create an archive directory by default.

When current work requires a log entry, record whether relevant older detail was kept, summarized, or archived, and any actual maintenance or unresolved preservation risk. Do not create an entry solely for a size advisory. Do not remove validation evidence or unresolved risks. The full opening message never belongs in this log.

<!-- ack:section:session-log-entry-template -->

## Entry Template

````markdown
<!-- ack:log-entry:start -->
## <YYYY-MM-DD> — <short session title>

- **ID:** <agent_or_session_id>
- **Summary:** <one sentence>
- **Changed:** <files changed, or none>
- **Done:** <work completed this session>
- **QC:** <checks run and results, or why not run>
- **Evidence disposition:** <one-time only / kept as recent trace evidence / absorbed into handoff / indexed in PROJECT_INDEX / promoted to PROJECT_DECISIONS / promoted to rule pack>
- **Sync:** <doc/external sync status>
- **Pending:** <next work>
- **Risks:** <known risks or none>
- **Log maintenance:** <actual maintenance action, preservation risk, or not_applicable>
- **Opening-message mirror:** <regenerated and verified / blocked; full text omitted by design>
<!-- ack:log-entry:end -->
````

---

<!-- ack:log-entry:start -->

## 2026-11-24 Session 257 — 介面檢查與修正、發佈時預先編譯、Supabase 流量減量

- **ID:** S257（Opus 5.5）
- **Summary:** 按 Leonard 要求檢查電腦、平板、手機介面與效能，分三步修正並上線（v3.4.1–v3.4.3，其中 v3.4.3 改為 GitHub Actions 發佈時預先編譯）；處理 Supabase egress 超額郵件，找出主因並減量；資料庫空間問題定於一月處理。
- **Changed:** `app.html`、`index.html`、`mobile.js`、`README.md`、`CHANGELOG.md`（#149、#150、#151）；新增 `dev/build_site.mjs`、`.github/workflows/deploy_site.yml`（#151）；`dev/CODEBASE_CONTEXT.md`（Hosting）；`dev/ops/playbooks/health-probe.md`（#152）；`dev/source/qc_report.py`、`dev/source/check_registry_drift.py`、`.github/workflows/qc_report.yml`（#153）；治理檔。外部：GitHub Pages 來源改為 GitHub Actions（Leonard 批准，AI 以 `gh api` 執行）。本機：頂層 `.claude/launch.json` 曾暫加一個預覽設定，已移除。
- **Done:**
  - **介面檢查**：報告 https://claude.ai/artifact/QSnozgEvtzBzdeKH4ep1hP （私人）。
  - **#149–#150**：對比、書面語、統計欄；平板 44 px、頁尾貼底。
  - **#151**：Leonard 選「上載時編譯」，否決「提交編譯檔」；同源逐元素比對差異 0；線上搜尋正常、無 Babel。
  - **#152**：探針改讀 `app.js` 版本號。
  - **#153**：漂移檢查只讀三欄（27 → 2.4 MB）；Issue 事件只重寫清單。
- **QC:** 每個 PR `build` 與 `build-gate` 通過後合併；`build_site.mjs --self-test` 4/4；兩個 QC 腳本 `--self-test` ALL PASS；漂移帳改前改後逐行相同；本機預覽 1280／768／375 px；線上 v3.4.3、`app.js`／`app.css` 200、舊網址 308、搜尋正常；每次合併後 `deploy_site.yml` 皆 success。Lighthouse（npx）被權限分類器擋下；Chrome 擴充無回應，改用內置瀏覽器。
- **Evidence disposition:** absorbed into handoff（`## Validation / QC` S257、`## Risks / Blockers` 7、`## Open Priorities`）；發佈方式記入 `dev/CODEBASE_CONTEXT.md` 與 `dev/PROJECT_INDEX.md`。
- **Sync:** Project index confirmed（Branch / commit、前端列、新檔列）；Doc sync registry confirmed（S257 區塊）；README／CHANGELOG／版本 confirmed。
- **Pending:** 核實 Supabase 流量回落；通告系統連結；一月重建向量索引與停用舊網址。
- **Risks:** Supabase egress 寬限至 2026-12-24；資料庫 414／500 MB；新 `qc_report.yml` 流程未在 GitHub 實際運行過。
- **Log maintenance:** 本檔 23 個條目、約 410 行；達 11 條提示，但無實際保存或延續需要，未整理。
- **Opening-message mirror:** regenerated and verified（腳本讀回與開場區塊逐字相同）；全文按規定不在本檔。`closeout-status` 未執行：npx 被權限分類器擋下。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-24 Session 256 — 基線重跑、minny.app 品牌接入、遷往 policychecker.minny.app

- **ID:** S256（Opus 5.5；中段 Sonnet 5.5）
- **Summary:** 重跑 183 題基線（與 S253 逐題相同）；補完 minny.app 品牌接入；調查用量後將網址遷往 `policychecker.minny.app`（v3.4.0），舊網址轉駁至 2027 年 1 月底，並加遷址橫額與加到主畫面；Leonard 定沿用現有設計、不加開場動畫。
- **Changed:** `backend/src/config/env.ts`、`backend/README.md`（CORS）；`CNAME`、`app.html`、`index.html`、`mobile.js`、`mobile.css`、`README.md`、`K1_API_SPEC.md`、`embed-sample.html`、`status-07cc7942c0.html`、`.github/workflows/qc_report.yml`、`robots.txt`、`sitemap.xml`、`CHANGELOG.md`；新增 `brand/BRAND.md`、`move-notice.js`、`manifest.webmanifest`、`dev/source/eval_runs/2026-11-23_s256_gold_prod_baseline.json`；`AGENTS.md`（品牌開工檢查，不在 git，已備份）；治理檔。外部：minny.app DNS（Vercel）、wongfu.net DNS（OrderBox，Leonard）、Vercel 專案 `policychecker-redirect`、GitHub Pages 網域；品牌 repo 的資料卡與 `drafts/2026-11-steady-style/`（未 commit）。
- **Done:**
  - **基線**：生產重跑，132／32、61／103，逐題與 S253 相同。
  - **品牌**：`brand/BRAND.md`、開工檢查、手機版字標（手機版隱藏頁尾）；「穩重」草稿與兩輪重新規劃畫布（示意，未採用）。
  - **用量**：`search_log` 36 次、Cloudflare 30 日 40 到訪（手機 30）；數據不足以按裝置設計。
  - **遷址**：#146 → DNS → #147 → Pages 證書與 HTTPS → OrderBox CNAME → 轉駁；中途修好首頁漏轉駁；發現並處理舊用戶重看導覽。
- **QC:** 每個 PR `build-gate` 通過；`npm run check`；`status_page_test.mjs`；Kit doctor 54/54；本機預覽（橫額、略過導覽、按「知道了」、直接到訪無橫額、手機與電腦）；線上：舊網址五種路徑 308、新網址 200 v3.4.0、HTTPS、預檢與 `/api/stats/usage` 跨網域 200；Leonard 瀏覽器實見橫額。
- **Evidence disposition:** absorbed into handoff（`## Validation / QC` S256）；遷址決策與 1 月底停用步驟見 `## Open Priorities` 3。
- **Sync:** Project index confirmed（Branch / commit、前端列）；Doc sync registry confirmed；README 版本與網址 confirmed；品牌資料卡已加一行（品牌 repo 未 commit）。
- **Pending:** 通告系統連結；Google Search Console；2027 年 1 月底停用舊網址；首次載入慢；推廣第二步。
- **Risks:** 舊網址的 DNS 快取最多 2 小時，部分用戶短暫見到舊錯誤頁；`x-probe` 不在 CORS 允許標頭；Android 一按安裝未在真機測試；OrderBox 只有 Leonard 改得到。
- **Log maintenance:** 本檔 22 個條目、約 390 行；達 11 條提示，但無實際保存或延續需要，未整理。
- **Opening-message mirror:** regenerated and verified（見收工檢查）。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-23 Session 255 — A18、數學課程闡釋、B 部全部決定、刪除文件標註、品牌頁尾

- **ID:** S255（Opus 5.5；中段 Sonnet 5.5）
- **Summary:** 兩日內合併 PR #128–#142：A18 路由、數學課程闡釋 361 片段入庫、B 部逐項決定並執行（退役 993 片段、兩條註腳、刪除文件標註功能）、Kit 0.4.8、通告網址改 circular.minny.app、QC 零值即通過、頁尾品牌與精簡（v3.3.19）。
- **Changed:** `backend/src/api/searchChannelB.ts`、`backend/src/server.ts`（刪 3 個模組）、`app.html`、`index.html`、`assets/brand/m.svg`、`dev/source/*`（registry、drift、qc_report、release_gate、footnote 清單、題庫）、`dev/vault/`（6 份新抽取）、`dev/ops/WORK_QUEUE.md`、README、CHANGELOG 等；收工：交接、本檔、PROJECT_INDEX、DOC_SYNC_REGISTRY、開場鏡像。
- **Done:**
  - **A18**：原卡做法本機量度無效，改用 `staffing` 問人數條件；生產驗收通過。
  - **入庫／退役**：+361（數學課程闡釋）、−424（B2）、−569（B3）；每次先全欄位備份、預演、讀回。
  - **B 部**：逐項以選擇器問 Leonard 後執行；A8、A12 卡過時已更正。
  - **功能**：刪除文件標註（v3.3.17）；品牌頁尾（v3.3.18）；頁尾精簡（v3.3.19）。
- **QC:** 每個 PR `build-gate` 通過；`route_regression` 96/96；`npm run check`／`build`；`regression:grounded` 50/50、`regression:overlay` 全過；漂移 ERROR 類 0、PHANTOM 0；`check_downstream_sync` `MUST_UPDATE` 0；註腳工具 `to_change=0`；生產驗收（A18、A19、B2、B5/B6 端點 404、頁尾上線）；本機瀏覽器核實前端。
- **Evidence disposition:** 數字與結論吸收入交接 `## Current Baseline` 與 `## Validation / QC` S255；量度檔 `dev/source/eval_runs/2026-11-22_s255_*.json`；本條作近期追溯。
- **Sync:** `DOC_SYNC_REGISTRY` S255 段 `confirmed`；PROJECT_INDEX Branch／commit 已更新。
- **Pending:** 重跑 183 題基線；判官驗收題 A01；特殊學校人數問題合成拒答（記錄）。
- **Risks:** 基線未重跑，S255 改動對整體檢索的影響未量度；其餘不變。
- **Log maintenance:** not_applicable（條目數已達維護提示門檻，本節無需要保存或續做的整理工作）。
- **Opening-message mirror:** 由唯一開場區塊重生並讀回；全文不在本檔重複。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-19 Session 254 — FEATURE_SUBJECT_CHECK 生產開啟、staff_est_sp_sch_pri 入庫

- **ID:** S254（Opus 5.5）
- **Summary:** 開工轉 Draft，起手探針全綠；Leonard 在 Render 開啟 `FEATURE_SUBJECT_CHECK`，經帶合成實查與 `--live` 254 題核實（誤攔 0）；`staff_est_sp_sch_pri` 經預演、備份後入庫 28 片段，「12班小學」3/3 答對；PR #125 合併。
- **Changed:** `dev/source/eval_runs/2026-11-19_s254_subject_live.json`（新）、`dev/source/SUBJECT_CHECK_DESIGN.md`（狀態＋第九節）、`dev/ops/NEXT_UPGRADE.md`、`dev/ops/WORK_QUEUE.md`（B1、A14 結案；新增 A18）、`dev/ops/AUTONOMY_FLOW.md`、`dev/SYSTEM_OVERVIEW.md`、`backend/README.md`、`dev/DOC_SYNC_REGISTRY.md`、`dev/source/source_registry.json`、`stats.json`／`app.html`／`index.html`／`README.md`／`update_log.json`、交接檔、本檔、`PROJECT_INDEX.md`、開場鏡像。
- **Done:**
  - **B1**：首次設定後實查未生效，Leonard 再存後生效；`/health` 不報旗標，只能靠帶合成的實查判斷。`--live` blocked 7／answerable 0／gold 0。
  - **量度準則更正**：183 題 gold 用 `synthesize:false`，量不到本閘。
  - **A14**：28 片段（15,828 → 15,856；來源 315）；S204 錯答未重現，但原因是 `staff_est_pri` 排第 1，不是對象核對。
- **QC:** 起手探針；`--live`；生產實查（攔截 2 條、對照 1 條、「12班小學」3 次、特殊學校 3 種問法）；漂移 ERROR 類 0、PHANTOM 0；`MUST_UPDATE` 0；#125 `build-gate` 通過；合併後線上數字讀回。
- **Evidence disposition:** 數字與結論吸收入交接 `## Current Baseline`、`## Validation / QC` S254 與 `SUBJECT_CHECK_DESIGN.md` 第九節；本條作近期追溯。
- **Sync:** `DOC_SYNC_REGISTRY` S254 段 `confirmed`；PROJECT_INDEX Branch／commit 已更新。
- **Pending:** A18；B 部其餘；A10、A12。
- **Risks:** `staff_est_sp_sch_pri` 錯答風險取決於 `staff_est_pri` 排名（回退方法在 `WORK_QUEUE` A14）；其餘不變。
- **Log maintenance:** not_applicable（條目數已達維護提示門檻，本節無需要保存或續做的整理工作）。
- **Opening-message mirror:** 由唯一開場區塊重生並讀回；全文不在本檔重複。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-18 Session 253 — 183 題新基線、A16 結案（無 2024 年版）、g08 標題更正、§4b 收緊

- **ID:** S253（Opus 5.5）
- **Summary:** 頂層 Kit 經 CLI 確認 0.4.7 已最新；開工轉 Draft，起手探針全綠。重跑 183 題生產基線；做 A16 時發現前提不成立（教育局沒有 2024 年版中文學習領域指引），結案並按 Leonard 批准更正 g08 誤標；按 Leonard 要求把「每項工作開始前提模型與 effort」寫入 §4b。
- **Changed:** `dev/source/eval_runs/2026-11-18_s253_gold_prod_baseline.json`（新）、`dev/ops/AUTONOMY_FLOW.md` §4b、`dev/ops/WORK_QUEUE.md`（A16 結案、B1 門檻、D 部基線）、`dev/ops/NEXT_UPGRADE.md`（基線與門檻 130 → 132）、`dev/ops/decisions/2026-11-17_A13_superseded_editions.md`、`app.html`／`guidelines.json`／`dev/source/source_registry.json`（g08）、交接檔、本檔、`PROJECT_INDEX.md`、開場鏡像。
- **Done:**
  - **基線**：生產、`x-probe`、`synthesize:false`、每題 8 秒；主跑 2 題 `57014`，同一小時單獨重跑後併入。來源層 132／32、片段層 61／103、禁引 8。與 S250 逐題比：移出 2 題（兩層皆 FAIL）、2 題 FAIL → PASS、無 PASS → FAIL、片段層無變。
  - **A16**：教育局課程文件頁（中、英文）只列 2017 年版；`g08` 是其示例頁，「2024」是頁面修訂日期。結案，生產零改動。
  - **g08**：三處標題、簡稱、年份更正（`guidelines.json` 只改該項，`_meta` 不動）；`check_downstream_sync` `MUST_UPDATE` 0。
- **QC:** 起手探針（見交接 `## Validation / QC` S253）；漂移 ERROR 類 0；`git grep` 舊標題 0 處。**未驗證**：g08 新標題未上線（待合併）。
- **Evidence disposition:** 基線數字吸收入交接 `## Current Baseline` 6；A16 結論存 `WORK_QUEUE` A16 備註；本條作近期追溯。
- **Sync:** 下游同步 `confirmed`（g08）；PROJECT_INDEX Branch／commit 已更新。
- **Pending:** B1 決定；B 部其餘；A10、A12。
- **Risks:** 不變（見交接 `## Risks / Blockers`）。
- **Log maintenance:** not_applicable（條目數已達維護提示門檻，但本節無需要保存或續做的整理工作）。
- **Opening-message mirror:** 由唯一開場區塊重生並讀回；全文不在本檔重複。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-17 Session 252 — 工作清單大部分完成：自主運作四項、瀏覽清單與庫存對齊、9 份入庫、11 份舊版退役、題庫整理

- **ID:** S252（Claude_20261117；接續 S251 同一對話，模型 Fable 5.2 → Opus 5.5）
- **Summary:** S251 收工時設的定時任務在用量重設後開了 4 個 PR（A1、A2、A4、A7）後因用量上限中斷；主 session 逐個核對後合併。其後按 `dev/ops/WORK_QUEUE.md` 逐張做 A3、A5、A6、A8、A9、A13、A14、A15、A17，並執行 Leonard 批准的 B15、B16。每張卡一個 PR，Leonard 明示後合併（#107–#122）。
- **Changed:** `check_freshness.py`（自動確認）、`qc_report.py`（兩個漂移檢查）、`check_footnote_anchors.py`＋月檢 workflow、`check_registry_drift.py`（`BROWSE_ONLY`／`UNLISTED_BY_DESIGN`）、`wikiRepository.ts`（`/health` 時間）、`searchChannelB.ts`（路由清單增減）、`app.html`（瀏覽清單 182 → 241、兩則示範問答）、`backend/README.md`、`source_registry.json`、9 份 vault 抽取檔、題庫五個檔、`gold_deprecated_s252.json`、`dev/source/gold_baselines/`、`url_overrides.json`、`footnote_anchors.json`、兩份決定表（`dev/ops/decisions/`）、playbook、`WORK_QUEUE.md`、公開數字、`update_log.json`。
- **Done:**
  - **生產寫入**（皆 Leonard 批准、先備份）：入庫 9 份 238 片段；退役 11 份 1,494 片段（備份 `dev/init_backup/20261117_190642_UTC/`）；1 條註腳 `url`（備份 `20261117_090130_UTC`）。庫存 17,084 → 15,828、來源 316 → 314。
  - **核實**：每份入庫／退役讀回數目；部署後線上抽查；定時任務的 4 個 PR 逐個重跑自測、建置、實地抽查並依次試合併。
  - **決定與理由**：`staff_est_sp_sch_pri` Leonard 批准入庫，但 S204 曾因它令「12班小學有幾多個學位教師」答錯而撤出，恢復條件是先開 B1，故暫緩並向 Leonard 說明；`mce_framework_2008` 讀 2026 架構原文確認被「更新」後才退役；A13 分類工具給不出分類（停止條件），改為人手配對新舊版、以退役代替前端標籤。
  - **題庫**：185 → 183（改標 9、移出 2）；驗證器 183／183。生產上改標題目中 3 題未取回答案文件，屬檢索問題，沒有為遷就而加替代來源。
- **QC:** 見交接 `## Validation / QC` S252。**未驗證**：S252 後未重跑 183 題全量基線。
- **Lessons（monitoring）:** (1) 下游同步檢查在退役時會把舊版標題與新版瀏覽條目比對，報 MUST_UPDATE 屬誤報。(2) 未套用的連結覆寫不可先放進 `url_overrides.json`，否則每日漂移檢查會當成「被蓋回」。(3) 題庫分檔與合併檔會漂移：改題庫後要同步所有分檔。
- **Closeout:** `closeout-status` 為最終讀回；開場鏡像由唯一開場區塊重生；開場訊息全文不在本檔重複。
- **Pending:** 新基線（183 題）；B 部決定；A16；A10、A12。
- **Next:** ① 重跑 183 題全量新基線 ② B1 決定 ③ A16。

## 2026-11-16 Session 251 — 10 條註腳按原文更正、註腳更正工具、無最強模型時的運作規則、工作清單

- **ID:** S251（Claude_20261116_S251）
- **Summary:** 覆核 S250 審核找出的 10 條註腳，全部確有問題，經 Leonard 批准後按原文更正並寫入生產。Leonard 中途告知 Fable 5.2 用量將盡、之後不會有，要求準備好系統自主運作；遂把更正做成可重複使用的工具，新增「沒有最強模型時」的運作規則，並把所有待辦一次過寫成工作清單供之後的模型照做。
- **Changed:** PR #102（`f00258c`）：`dev/apply_footnote_corrections.py`、`dev/source/footnote_corrections.json`、`dev/source/url_overrides.json`、五個註腳入庫腳本／staging 的文字、`dev/ops/AUTONOMY_FLOW.md` §4a、三份 playbook、`DOC_SYNC_CHECKLIST.md`、`PROJECT_INDEX.md`、`update_log.json`、交接檔。收工 PR（`s251-work-queue`）：`dev/ops/WORK_QUEUE.md`、交接檔、本檔、`PROJECT_INDEX.md`、`AUTONOMY_FLOW.md`、開場鏡像。
- **Done:**
  - **覆核**：逐份下載原文逐條讀；與審核報告兩處出入（`trg_freeze_ceiling` 的三部與上限在附件 III 確實存在；`procurement_thresholds` 的批核人員與招標寫法亦錯）。
  - **寫入**：10 條 `text`／`hash`／`embedding`、2 條 `url`；皆先備份、逐條讀回；`--check` 與 dry-run `to_change=0`。
  - **線上驗證**：8 條查詢回傳新文字或新連結（寫入前同查詢回傳舊文字）。
  - **工具與規則**：更正清單為權威、工具冪等；`AUTONOMY_FLOW.md` §4a 規定語意改寫、檢索改動、刪除範圍交 Leonard。
  - **工作清單**：A 可直接做 13 張卡、B 待 Leonard 決定 12 項（附建議）、C 等觸發、D 不要做（PR #103；A12、A13 隨下一步提升計劃補入）。
  - **下一步提升計劃**：`dev/ops/NEXT_UPGRADE.md`——三類不合格題的拆解、五個階段、建議出貨門檻、放棄條件（設計文件，未實作、門檻未經確認）。
  - **Kit 升級**：0.4.3 → 0.4.7（官方 CLI，PR #105）；先刪去本檔內一份開場訊息全文才通過遷移驗收。
  - **模型與 effort 建議**：`AUTONOMY_FLOW.md` §4b，agent 開工主動提 Leonard（PR #106）。
  - **定時續做**：一次性任務 2026-11-17 02:56 本機時間；範圍限於改檔、commit、push、開 PR。
- **Closeout:** `closeout-status` `complete`；開場鏡像由唯一開場區塊重生並經該檢查讀回；舊條目按 §4a 歸檔至 `dev/archive/SESSION_LOG_2026_Q4.md`。
- **Pending:** `dev/ops/WORK_QUEUE.md` 全部（卡內工作未實作）；收工 PR（`s251-closeout`）待 Leonard 指示合併。
- **Next:** ① WORK_QUEUE A1（兩個漂移檢查接入每日質素檢查）② A2（註腳出處每月機械核對）③ B 部請 Leonard 逐項決定。
- **Risks:** 之後由較弱模型執行，判斷類工作容易出錯——以工作卡的驗收與停止條件約束；`/health` 的 `footnote_loaded_at` 不隨背景重讀更新（未查成因）；工作卡 A3、A5 所指的既有做法未經逐行核實。
- **Lesson（monitoring）**：內容更正若只靠一次性腳本，入庫腳本重跑就會被蓋回；更正應以清單為權威並有漂移檢查。

- **Opening message:** 不在本檔重複；唯一權威在 `dev/SESSION_HANDOFF.md` 的 `## Next Session Opening Message`，鏡像為 `START_NEXT_SESSION_PROMPT.txt`（Kit 規定不得保留第三份完整副本）。

## 2026-11-16 Session 250 — 科目指引新路由、未入路由清單檢查、自動運作流程與 playbook、註腳全量審核

- **ID:** S250（Claude_20261116_S250）
- **Summary:** 追查「入了庫但搜不到」，查出 57 個來源（39% 片段）不在任何路由清單；新設 `subject_guides` 路由並加常設檢查；按 Leonard 要求寫好自動運作總流程與六份 playbook，並把兩項測試交較平的模型實跑。
- **Changed:** PR #100（`4f0b57f`）：`backend/src/api/searchChannelB.ts`、`backend/scripts/_s250_localServer.ts`、`dev/source/check_registry_drift.py`、`qc_report.py`、`route_regression.mjs`、`dev/ops/**`、`RULE_PACKS.md`、`PROJECT_INDEX.md`、`DOC_SYNC_CHECKLIST.md`、`CODEBASE_CONTEXT.md`、`SYSTEM_OVERVIEW.md`、量度檔 · 收工：交接、本 log、`DOC_SYNC_REGISTRY.md`、`PROJECT_INDEX.md`、`START_NEXT_SESSION_PROMPT.txt`、`2026-11-16_s250_gold_prod_after.json`。
- **Done:**
  - **根因**：路由命中後只在該類別的 `SOURCE_SETS` 內搜尋；人手入庫的來源從未加入清單，亦無任何檢查。
  - **方案取捨**：先量度「全部加入 `curriculum`」並否決（擠走 g13、5–17 秒）；改設獨立路由。
  - **量度**：線上改前、本機改後（受影響 20 題）、線上改後三次；線上前後 185 題逐題相同。
  - **流程**：`dev/ops/AUTONOMY_FLOW.md`＋playbook；最平模型跑 `health-probe`、中階模型跑 `footnote-audit`，各自的回饋已修入程序。
- **QC:** 見交接 `## Validation / QC` S250。**未驗證**：新路由的 37 個來源題庫幾乎不覆蓋；9 條內容不符的註腳未逐條覆核；後端背景重讀未在線上觀察到。
- **Evidence disposition:** 現況與下一步入交接；量度與審核結果在 `dev/source/eval_runs/2026-11-16_s250_*`；39 題快速量度、被否決方案的本機量度、sub-agent 下載的文件只在 scratchpad（一次性）。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S250 節；`DOC_SYNC_CHECKLIST.md` 新增「新增／退役監察或 playbook」一列（Doc Sync: registry updated）；開場鏡像由唯一區塊重生並核對。
- **Pending:** 見交接 `## Open Priorities`（首項：28 條註腳頁碼交 Leonard 批准）。
- **Risks:** 線上間歇逾時（`57014`）在量度期間出現 4 次，重跑即正常，屬既有的平台冷熱落差；`subject_guides` 的觸發字眼若日後擴闊，要用 `route_regression` 的反例把關。
- **Log maintenance:** not_applicable（條目數 14，屬數量提示）。
- **Opening-message mirror:** regenerated and verified; full text omitted by design.
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-16 Session 249 — Freshness 監察加出口並清零、八個來源重新入庫、50 條頁碼、後端快取定時重讀

- **ID:** S249（Claude_20261116_S249）
- **Summary:** 補完 S248 收工後，按 Leonard「減維護負擔」方向修好 Freshness 監察只入不出的問題並把 35 項清至 0；經 Leonard 逐項批准重新入庫五份 PDF 與三份統計表、補 50 條頁碼／網址、按原文更正兩條註腳與兩條統計事實；後端 overlay 快取改為定時背景重讀。
- **Changed:** PR #97（`ef7ffb9`）：`check_freshness.py`、`freshness_check.yml`、`notify_new_items.js`＋測試、`source_registry.json`、`FRESHNESS_GUIDE.md`、`repage_pdfs.py`、`cb3_b2_pagecarry_migrate.py`、八個來源的 vault 抽取檔、`url_overrides.json`、`apply_url_overrides.py`、兩個一次性腳本、`forms_ingest.py`、`ingest_s179_topics.py`、`build_stat_facts.py`、`stat_facts.json`、`qc_report.py`、公開片段數鏡像、`update_log.json`、`SYSTEM_OVERVIEW.md`、治理文件 · PR #98（`eff9047`）：`backend/src/lib/wikiRepository.ts`、`overlayCacheRegression.ts`、`backend_build_check.yml` · 收工：交接、本 log、`DOC_SYNC_REGISTRY.md`、`PROJECT_INDEX.md`、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:**
  - **Freshness 根因**：基線停在 6 月、入庫不更新基線、無逐項確認、網頁以整頁位元組比對（約 270 KB 外殼包幾 KB 內容）；另查出 95 個來源從未有基線。
  - **比對**：19 份「已變」PDF 逐頁對 vault，11 份內容相同只確認，5 份有實質改動重新入庫；三份統計表上游修訂了所有教師數字。
  - **Sub-agent**（Leonard 准許，嚴格唯讀）：整理 51 條頁碼缺口清單與統計表比對；本人再獨立核對 40/40。
  - **後端**：`invalidateWikiCache` 無人呼叫，更正註腳後線上仍答舊金額（實測），改為 stale-while-revalidate。
- **QC:** 見交接 `## Validation / QC` S249（自測、全量 dry-run、逐來源對數、兩次獨立頁碼核對、部署後線上實測）。**未驗證**：線上實際發生的 30 分鐘背景重讀；四條註腳措辭出入。
- **Evidence disposition:** 現況與下一步入交接；備份在本機 `dev/init_backup/20261116_08*_UTC/`（gitignored，含頁碼建議清單）；sub-agent 下載的 PDF 與比對檔只在 scratchpad（一次性）。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S249 節；`DOC_SYNC_CHECKLIST.md` 新增「註腳網址覆寫」一列（Doc Sync: registry updated）；開場鏡像由唯一區塊重生並核對。
- **Pending:** 見交接 `## Open Priorities`（首項：Leonard 決定 `FEATURE_SUBJECT_CHECK`）。
- **Risks:** 註腳入庫腳本以 `--execute` 重跑會蓋掉 50 條頁碼（QC 會報高於基準；修法是再跑 `apply_url_overrides.py --execute`）；網頁指紋對沒有 `inner_page_content_container` 的頁面（現時只有 `cs_curr`）仍比對整頁文字。
- **Log maintenance:** not_applicable（條目數 13，屬數量提示；本節無實際保存或接續需要）。
- **Opening-message mirror:** regenerated and verified; full text omitted by design.
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-15 Session 248 — 減維護負擔：交接檔瘦身、QC 惡化通知、PAGE_ANCHORED 定義修正

- **ID:** S248（收工因用量上限中斷，2026-11-16 下一節起手補完）
- **Summary:** Leonard 定「減維護負擔」為優先方向；交接檔 760 KB → 約 65 KB（PR #92）；質素檢查高於基準時開 `qc-regression` Issue 並 @Leonard（PR #93）；`PAGE_ANCHORED` 只計 PDF、標記判斷與後端一致、基準 179 → 51（PR #95）。
- **Changed:** PR #92／#93／#95 的檔案（見各 PR）；收工（PR #96）：交接、本 log、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、`START_NEXT_SESSION_PROMPT.txt`
- **Done:** 三個 PR 皆由 Leonard 明示後合併；Issue #94 查明 194 條中 143 條為檢查誤報，修正後自動關閉。
- **QC:** 三個 PR CI 通過；`qc-regression` 通知經真實運行驗證；線上 QC 實測 `PAGE_ANCHORED` 51。2026-11-16 補收工起手探針全部通過（數值見交接 `## Validation / QC` S248 (4)）。
- **Evidence disposition:** 已吸收入交接檔 `## Validation / QC` S248；歷史原文在 `dev/archive/SESSION_HANDOFF_HISTORY_2026-11-15.md`。
- **Sync:** DOC_SYNC_REGISTRY S248 段（一列 `unverified`：未逐列重核三個 PR 觸及的 registry 列）；開場鏡像由唯一區塊重生並核對。
- **Pending:** 見交接 `## Open Priorities`（退役 `EDBC_9_2019_E` 先確認；51 條 `PAGE_ANCHORED` 真缺口；Freshness #77）。
- **Risks:** 本條目由下一節依交接檔、git 紀錄與 PR 重建，S248 節內逐步對話細節未保存。
- **Log maintenance:** not_applicable。
- **Opening-message mirror:** regenerated and verified; full text omitted by design.
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-09 Session 247 — 清理 dev/init_backup 舊版 wiki_index 備份

- **ID:** S247
- **Summary:** Leonard 批准後刪除 26 份舊版／重複 `wiki_index.json` 備份（5–6 月 24 份、與現用檔雜湊相同的 `20261013_105847_UTC`／`20261013_110720_UTC`），釋放 10,826,816 KiB（約 11.09 GB）；保留 `20261101_195458_UTC`（SHA-256 與現用檔相同）及其餘 43 個備份；`dev/rules/safety.md` `## Project Rules` 加入 wiki_index 備份只留最新一份的規則。
- **Changed:** `dev/rules/safety.md`、本 log（PR #89 → `82be06e`）；收工：交接、本 log、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、`START_NEXT_SESSION_PROMPT.txt`；本機刪除 `dev/init_backup/` 26 個資料夾（gitignored）
- **Done:** 只讀審核 → Leonard「批准刪除＋加規則」「開分支並開 PR」「CI 綠後合併」。
- **QC:** 27 資料夾逐一核內容與大小；3 份新版 SHA-256 與現用檔相同；全項目搜尋資料夾名稱無腳本／待辦引用；刪後保留份再核 SHA-256；safety.md 官方內文前綴 SHA-256 不變；PR #89 CI 通過。
- **Evidence disposition:** 數字與決定已吸收入交接檔 `## Validation / QC` S247；規則在 `dev/rules/safety.md`。
- **Sync:** DOC_SYNC_REGISTRY S247 段；開場鏡像由唯一區塊重生並核對。
- **Pending:** 見交接 `## Open Priorities`（下一步退役 `EDBC_9_2019_E`，先確認）。
- **Risks:** none（零生產改動）。
- **Log maintenance:** not_applicable。
- **Opening-message mirror:** regenerated and verified; full text omitted by design.
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-08 Session 246 — Option 2 清單清空；刪除 109 條 approved_fact 副本；PR #87 合併

- **ID:** S246
- **Summary:** 最後一條租金收入以 g02《財務管理指引》第 15 頁按原文修正，清單清空（resolved 289、dropped 166）；按規則第 5 條備份後刪除 Supabase 109 行 `role_facts_*`；PR #87 合併；舊分支刪除；兩個 footnote 來源判定按設計不登記。
- **Changed:** `dev/knowledge/channel_a_option2_queue.json`、`stats.json`／`app.html`／`index.html`／`README.md`（17,183 → 17,074）、`CHANGELOG.md`（工作 commit `28aaaf9`，經 PR #87 合併為 `62647fe`）；收工：交接、本 log、`dev/DOC_SYNC_REGISTRY.md`、`dev/PROJECT_INDEX.md`、開場鏡像（分支 `s246-closeout`）。
- **Done:** Leonard「甲」「批准寫入」「匯出備份」「批准刪除」「加入 PR #87」「CI 綠後合併」「刪舊分支＋登記來源」；Supabase −109，17,074／315。
- **QC:** g02 PDF 按版面座標重組並逐字對照；清單序列化格式核對；備份 109 行＝`count=exact`；刪除 `id` 集合＝備份；display-sync 讀回並於線上確認；`build-gate` 在 `28aaaf9` 通過後才合併；`check_registry_drift --check` UNMANAGED 0；`d2c95ee` 與 `17903a3` patch 相同後才刪分支。
- **Risk observed:** Render 喚醒後首兩次查詢 `57014`（含通函索引），之後自行恢復 —— 屬既有 Risks 3，未新增風險。
- **Evidence disposition:** 備份在 `dev/init_backup/20261108_122028_UTC/`（gitignored，本機）；g02 PDF 與匯出腳本在 scratchpad（臨時）；決定與數字已吸收入交接檔 `## Validation / QC` S246 與清單本身。
- **Sync:** DOC_SYNC_REGISTRY S246 段；開場鏡像已由唯一區塊重生並讀回相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-05 Session 245 — Option 2 第二輪：清單 39 → 1；BYOD footnote 入庫

- **ID:** S245
- **Summary:** 餘下 39 條逐條在庫內關鍵詞搜尋並上 edb.gov.hk 搜尋：23 條按原文修正入出處、14 條剔除、1 條（BYOD）原文只在網上，以 footnote_curated 入庫後入出處；只剩租金收入一條待 Leonard 定出處。
- **Changed:** `dev/knowledge/channel_a_option2_queue.json`、`dev/ingest_s245_option2_byod_footnote.py`（新）、`update_log.json`、`dev/PROJECT_INDEX.md`、`stats.json`／`app.html`／`index.html`／`README.md`（17,182 → 17,183；313 → 315）、交接與鏡像。
- **Done:** Leonard「Approve all」（37 條）、「Approve ingest」（footnote）；Supabase +1（176 → 177），線上 `/health` footnote 177；PR #86 已合併故改開 PR #87。
- **QC:** 修正句錨點核對（只兩處刻意刪符號）；每次寫入後 `channel_a_jev_round.py --self-test` 全過；footnote 自測 cos 1.0000、INSPECT before／after；display-sync 與 sources-sync 讀回。
- **Evidence disposition:** 提案檔與清單備份在 `dev/source/coverage_runs/option2/r1/`（gitignored，本機 trace）；決定與理由已寫入清單本身；現況與下一步已吸收入交接檔。
- **Sync:** DOC_SYNC_REGISTRY S245 段；開場鏡像已重生並核對相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-05 Session 244 — Option 2 第一輪：清單 455 → 39；3 條 curated footnote 入庫

- **ID:** S244
- **Summary:** 寫腳本以 Jev 逐條核對 Channel A 清單，加「同一件事」題修正剔除誤判，再經人手核對、關鍵詞與網上搜尋、按原文修正、角色類與時限資料剔除，清單減至 39 條；3 條網上出處以 footnote_curated 入 Supabase。
- **Changed:** `dev/source/channel_a_jev_round.py`（新）、`dev/ingest_s244_option2_footnotes.py`（新）、`dev/source/jev/channel_a_match_gate.json`、`dev/knowledge/channel_a_option2_queue.json`（決定＋規則 6–8）、`update_log.json`、`dev/PROJECT_INDEX.md`、`stats.json`／`app.html`／`index.html`／`README.md`（17,179 → 17,182）、交接與鏡像。
- **Done:** 每一批寫入均經 Leonard 批准（原話記於清單每條 `approved` 欄）；Supabase +3（footnote_curated 173 → 176），線上 `/health` footnote 176；PR #86。
- **QC:** `channel_a_jev_round.py --self-test` 21 項全過（每次寫入後重跑）；footnote 自測 embed 格式 cos 1.0000、INSPECT before／after；修正句錨點核對零不符；`live_display_sync` 四檔替換。
- **Evidence disposition:** 判斷紀錄、候選、各批提案與清單備份在 `dev/source/coverage_runs/option2/r1/`（gitignored，本機 trace）；決定與理由已寫入清單本身；現況與下一步已吸收入交接檔。
- **Sync:** DOC_SYNC_REGISTRY S244 段；開場鏡像已重生並核對相等。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-11-03 Session 243 — 新文件 #78 分流與入庫、Channel A（455 條）退役、文件標註收起待修、刪除範本下載與兩個休眠頁

- **ID:** S243（Claude_20261103_0930）
- **Summary:** 由頂層 root「/handoff-kit-start」轉入 Draft。Leonard 問新文件電郵（#78 二十份含 2017 年）→「逐份判斷」→「批准入庫」→ 問搜尋紀錄拒答原因與 455 條去留 →「做 1 3 …4 刪去」→「用 /jev 核對副本」→ 文件標註實測與 Jev 第二意見 →「收起待修」→「範本 Word 檔刪去」→「t-purchase.html 刪除」→ 每個 PR「CI 綠後合併」（#79–#84）→「收工」。
- **Changed:** PR #79 入庫 `moi_3rd_cycle_policy_2021`（登記冊、vault、`SOURCE_SETS.moi`＋「化時為科」觸發詞、route_regression、指引書庫 182、更新日誌、公開數字）· #80 Channel A 退役（刪 `knowledge.json`／`role_facts.json`／`q.html`／`K1_KNOWLEDGE_INTERFACE_SPEC.md`、後端 3 條路由與 9 個模組；`approved_fact` 全數停服；新 `stats.json`、`dev/knowledge/channel_a_option2_queue.json`；QC、狀態頁、execute_ingest 改讀 stats.json）· #81 文件標註收起＋Jev 判斷閘 `dev/source/jev/channel_a_match_gate.json` · #82 標註按鈕補開關 · #83 刪範本分頁、109 份 Word、生成腳本 · #84 刪 `t-purchase.html`、手機版選擇角色畫面、README 對齊。
- **Done:**
  - **#78 分流**：二十份是監察首次掃描 S241／S242 新增的三個來源頁（教學語言、IIT、基本法測試）而一次過列出；逐份讀全文，只有 2021-04-29 第三周期政策函件值得入庫（庫內 07-06 跟進函寫明須與之一併閱讀），其餘 19 份 Leonard 定「不入」；#78 等監察下週一自動關閉（Leonard 指示）。
  - **入庫**：Supabase +9（17,170 → 17,179，來源 313）。
  - **Channel A 退役**：線上 `/api/search/channel-a`、`combined`、`analyze-circular` 回 404；搜尋頭 5 位不再出現無出處副本；首頁與平台介紹不再顯示 455。
  - **文件標註**：線上實測三個質素問題（相關指引幾乎不顯示、欠缺按清單次序、部分符合配錯段落）；Jev：誤導 0.94、可一輪修好 0.92、使用證據 0.04；Leonard「收起待修」。
  - **刪除**：範本下載分頁＋109 份 Word＋生成腳本；`t-purchase.html`；手機版「選擇角色」（角色從未傳給搜尋）。
- **QC:** 每個 PR build-gate 綠後由 Leonard 指示合併；`npm run check`／`build`、route_regression 76/76（＋2 條新斷言）、execute_ingest 30/30、qc_report 與 status_page 自測、checklists_bundle 重生逐字相同；合併後線上核實 /health（20fd4a4）、四條 x-probe 搜尋、桌面與手機分頁、手機導覽四步、404 頁面、console 零錯誤。
- **Evidence disposition:** 二十份 PDF 與 Jev state 只在 scratchpad；判斷結果寫入交接 `## Validation / QC` S243 與 CHANGELOG；Option 2 規則寫入清單檔 `_meta.rules`。
- **Sync:** `DOC_SYNC_REGISTRY` 新增「任何入庫／換版／退役 → 核對 Option 2 清單」一列；`DOC_SYNC_CHECKLIST` 凍結合約列改為只餘 guidelines.json；README、CHANGELOG、CODEBASE_CONTEXT、PROJECT_MASTER_SPEC、K1_API_SPEC 已同步。
- **Pending:** 見交接 Open Priorities（S243 段）：Option 2 第一輪（Jev 判斷閘）、文件標註四項重開條件、拒答原因 DDL 待批、#70 待關閉。
- **Risks:** 109 條 `approved_fact` 仍在 Supabase（只停服）；`app.html`／`mobile.js` 尚有不再觸發的 approved_fact 顯示程式；dev/vault 舊 Channel A 篩選腳本未刪。
- **Log maintenance:** `--check` trigger=False（224 行、8 條），不需歸檔。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-11-02 Session 242 — 封面核對 Issue #72 三份換版／退役入庫、拆出 blnst 路由、QC 報告排隊撞車修正

- **ID:** S242（Claude_20261101_1930）
- **Summary:** 由頂層 root「/handoff-kit-start」轉入 Draft。Leonard「處理封面核對」→「全部批准」→「完成就commit and push」→ 三次「CI 綠後合併」（#73、#74、#75）→ 中途「現在追查」（基本法測試短查詢）與「10:48 收到 failed 電郵」→「收工」。
- **Changed:** `dev/source/source_registry.json`（退役 `edbcm141_2025_blnst`；新增 `edbcm170_2026_blnst`、`blnst_faq_2026`、`sdp_guide_dss`；`sdp_guide`、`iit_ai_framework_2026` 換版）· vault 抽取檔 · `dev/vault/repage_pdfs.py` · `backend/src/api/searchChannelB.ts`（#73 三個路由集合；#74 新 `blnst` 路由）· `dev/source/route_regression.mjs` · `app.html`、`README.md`、`index.html`、`knowledge.json`、`role_facts.json`、`K1_API_SPEC.md`、`update_log.json`（公開數字）· `dev/source/title_baseline.json` · 三個清單範疇 `checklist.json`／`meta.json`／`clauses.json` 與 `checklists_bundle.json` · `.github/workflows/qc_report.yml`。**生產**：Supabase −10 +40（17,153 → 17,170，310 → 312 來源，逐項經 Leonard 批准）；Render 部署 `aeb6cb7`、`3ef9ab6`、`f7b988c`。
- **Done:**
  - **#73**：封面核對三份。141/2025 與 SDP 2010 版皆 404，教育局改掛新文件；iit 同網址換檔並改寫。舊資料連向量備份於 `dev/init_backup/20261101_195421_UTC/`（gitignored）。清單 27 條條文逐句在新文件找回原句後改指新片段。
  - **#74**：線上抽查發現「基本法測試」「BLNST」取不到新文件。量度證實是 hr_admin 展開詞（假期／薪酬）所致（最佳排名 1 → 36；BLNST 319 → 81），拆出 `blnst` 路由並以文件原用詞作展開，六種問法首三位全是 BLNST 文件。
  - **#75**：10:48 失敗通知 = QC 報告兩次排隊執行（push #73 ＋ 關閉 Issue #72），第二次由觸發當刻的 commit 重產，rebase 撞 `registry_drift.md`。改為 checkout `ref: main` ＋ `pull --rebase -X theirs`。
- **QC:** 封面核對 6/6 ok、基線差異 0 · `check_downstream_sync` MUST_UPDATE 0 · `npm run check`／`build` · `route_regression` 79 PASS · `route_blast_radius` 185 條只 1 條改路由（`cpd_blnst_test`，預期）· `check_source_titles --self-test`、`execute_ingest --self-test` 30/30 · 三個 PR build-gate 綠 · 合併後 `/health` commit 逐次核實 · 帶 `x-probe` 線上抽查（SDP、人工智能部分、BLNST 六問法）· QC 工作流程手動觸發一次 success。
- **Evidence disposition:** 量度腳本（`measure.py`、`probe.py`、`remap.py`）只在 scratchpad，不保留；數字寫入交接 `## Validation / QC` S242 與 `searchChannelB.ts` 的 `SOURCE_SETS.blnst` 註釋。
- **Sync:** `DOC_SYNC_REGISTRY` 不新增列；入庫常設步驟（更新日誌、指引書庫、README、下游同步、封面基線）已逐項做完。
- **Pending:** 見交接 Open Priorities（S242 段）。
- **Risks:** QC 撞車修正只經單次執行驗證，未經真實並發；交接檔約 71 萬位元組，本節只完整讀現況段落。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：226→204 行、8→7 條，S234 一條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；工具再把該條的 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該條標題前。主檔 start／end 的既有失衡不動。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-29 Session 241 — OpenAI 模型遷移完成、通函編號查找（旗標關）、註腳佔格量完不改、定期更新檢查規則

- **ID:** S241（Claude_20261029_1730）
- **Summary:** 由頂層 root 起手轉入 Draft。完成 OpenAI 模型遷移（#53 合併、Render 刪 `OPENAI_MODEL`、OCR 與量度判官選型）；原 OP ② 註腳佔格量完判定不是槓桿；按 Leonard 指示寫入定期系統更新檢查規則；讀 Mindsquare 思考紀錄後以真實搜尋紀錄分類 9 條拒答，據此實作通函編號查找（`FEATURE_CIRCULAR_NUMBER_LOOKUP`，預設關）。
- **Changed:** `backend/src/lib/circularRef.ts`（新）、`backend/src/lib/wikiRepository.ts`（`loadCircularIndex`）、`backend/src/api/searchChannelB.ts`（circular-number pass）、`backend/scripts/circularRefRegression.ts`（新）、`backend/scripts/_s241_circularAB.ts`（新）、`backend/scripts/_s227_rubricJudge.ts`（`--model`／`--effort`、自有預設）、`dev/ocr_extract.py`（`--effort`、預設 `gpt-6-luna`）、`dev/_s241_ocr_ab.py`（新）、`backend/README.md`、`backend/.env.example`、`dev/rules/coding.md`（`## Project Rules` 附錄）、`dev/CODEBASE_CONTEXT.md`、`dev/PROJECT_INDEX.md`、`dev/DOC_SYNC_REGISTRY.md`、交接、本 log、`dev/archive/SESSION_LOG_2026_Q3.md`、`START_NEXT_SESSION_PROMPT.txt`；artifacts `dev/source/2026-10-29_s241_footnote_lead_before.json`、`dev/source/eval_runs/2026-10-29_s241_*`（7 份）。生產：#53 squash 合併部署 `da44e55`；Render 刪除 `OPENAI_MODEL`（Leonard 操作）。Supabase 零寫入、零 DDL。
- **Done:** 官方頁重讀（無變）· 線上合成轉 `gpt-6-luna` 並抽查 · OCR 8 頁比對與改預設 · 量度判官四個設定校準、Leonard 定案 `gpt-6-luna`＋`low` · `footnote_lead_probe` 生產基線與 185 題擠出分析 · 定期更新檢查規則 · Mindsquare 兩點核對 · 9 條真實拒答分類 · 通函編號查找生產基線、實作與本機 before→after。
- **QC:** `npm run check`、`npm run build`、`circularRefRegression` 11/11、`regression:grounded` 50/50、`route_regression` 63/63、`execute_ingest --self-test` 28/28、`_s227_rubricJudge --self-test` 67/67、`footnote_lead_probe --self-test` PASS；`dev/rules/coding.md` 官方本體逐位元組相同。數字見交接 `## Validation / QC` S241。
- **Evidence disposition:** 量度 artifacts 保留為近期證據並在 `PROJECT_INDEX`／`CODEBASE_CONTEXT` 引用；真實搜尋紀錄只在工作區暫存分析，未入 git；規則升格入 `dev/rules/coding.md`。
- **Sync:** `DOC_SYNC_REGISTRY` 兩列更新（離線工具模型 → `done`；檢索旗標列加 S241）。
- **Pending:** 見交接 Open Priorities S241 ①–⑤（① 開通函查找旗標並生產重量）。
- **Risks:** 量度判官有 1 對位置偏誤（只監察）；收工 PR 改 `backend/src`，合併後會重新部署；交接檔約 69 萬位元組，本節只完整讀現況段落，cold zone 未逐字重讀。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：281→209 行、10→7 條，S233／S232／S231 三條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪，已核對三個標題由主檔移入歸檔、歸檔只有追加）；工具同樣把一個 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該批第一條前；主檔 start／end 8／8 平衡，歸檔檔既有失衡不動。
- **Fix Record（收工後補丁）:** Problem：#56 合併、Leonard 開旗標後生產無效。Root Cause：對照表查詢全表文字掃描，匿名角色 3 秒上限冷啟動逾時（4.2 秒），被 catch 吞掉；本機用 service key（8 秒）量不到。Fix：先按 `source_id` 前綴篩選，暖機預載。Verification：匿名金鑰冷 1.8 秒／熱 0.5 秒、64 份；匿名重跑 88/88 排第 1、零退步；check、build、單元 11/11、grounded 50/50、路由 63/63。教訓與既有量度紀律「本機用 service key 量 anon 系統會低估」相同，已有規則，未另立新規。
- **Fix Record 2（2026-10-30）:** Problem：#57 部署、旗標加上後仍無效。Root Cause：縮小後的文字掃描在冷資料庫仍 4.4 秒逾時；fail-open 令旗標缺失與載入失敗從外面無法分辨（截圖另核實前一次旗標其實未設）。Fix：按常見命名猜 id 直接查並以標頭核對、完整對照表背景載入與重試、失敗寫日誌、`/health` 報 `cache_b.circular`。Verification：匿名金鑰 resolve 約 1.1–1.7 秒、64 份；88/88 排第 1；單元 12/12、grounded 50/50、路由 63/63、check、build。另：補丁二的 commit 一度誤推上已合併的 `s241/circular-index-anon-timeout` 分支（無 PR，不影響 main），已 cherry-pick 到新分支。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對與舊慣例同格式（區塊＋結尾換行）；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-23 Session 240 — npm 依賴漏洞修補（PR #55 合併部署）

- **ID:** S240
- **Summary:** Leonard 要求「更新 php node 等漏洞」。本機與專案皆無 PHP；Homebrew Node 已是最新安全版。專案 `npm audit` 4 項以 `npm audit fix` 修補，PR #55 經 Leonard 指示 squash 合併，Render 部署 `77de1dd`。
- **Changed:** PR #55：`backend/package-lock.json`、`dev/checklists/_work/package-lock.json`、`dev/checklists/_work/node_modules/.package-lock.json`、`dev/checklists/_work/node_modules/nanoid/*` · 收工（推上 `s239/query-fusion`，即 PR #53）：交接、本 log、`dev/archive/SESSION_LOG_2026_Q3.md`、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`START_NEXT_SESSION_PROMPT.txt`。
- **Done:** backend `ws` 8.20.0→8.22.0、`form-data` 4.0.5→4.0.6、`hasown` 2.0.2→2.0.4、`esbuild` 0.27.4→0.27.2；checklists 工具 `nanoid` 5.1.11→5.1.16。合併後 `/health` 報 `77de1dd`。本機另一個 `/usr/local/bin/node`（24.14.0，無 pkg 收據）在本節 11:36 前後已被移除，非本 session 所刪，無殘留。
- **QC:** 兩處 `npm audit` 0；`npm ci`、`check`、`build`、`regression:grounded` 48/48、`route_regression` 63/63（與修補前逐字相同）、docx smoke test；build-gate pass；線上 `x-probe` 搜尋 200。
- **Evidence disposition:** 一次性；結論入交接 `## Validation / QC` S240。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S240 節。
- **Pending:** 不變，見交接 Open Priorities（S239 ①–⑤）。
- **Risks:** Render 所用 Node 22.x 小版本未核實；`cache_b` 173／303 對 S237 記錄 181／306 未逐條核對。
- **Log maintenance:** `--check` 報 date trigger → `--apply`：292→264 行、10→9 條，S230 一條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；重查 `trigger=False`。工具再次把該條的 `ack:log-entry:start` 留在主檔尾，已移到歸檔檔該條標題前（兩檔各自 +1/+1，主檔既有失衡不動）。`latest entry prompt block ok=False` 為已知分歧（開場白不入 log）。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對相等；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-10-21 Session 239 — SEN 留級答錯的根因（展開詞）、查詢交替合併不出貨、狀態頁按改動重產、OpenAI 模型遷移選型與量度

- **ID:** S239（跨 2026-10-13、10-18、10-21）
- **Summary:** Leonard 以 RTHK 新聞指出系統答「SEN 學生留級未明確載明」與狀態頁未更新；要求治本。查明內容早已在庫，是類別展開詞把窄題目的答案推出候選池；交替合併的旗標檢索層 +9 片段但答案層不出貨。狀態頁改為按知識庫改動重產並自行比對現況。OpenAI 公布 2027-01-14 停用生產兩個模型，按 Leonard「剛夠用、不追新」選 `gpt-6-luna`＋effort `none`，量度後改碼內預設。全部在 PR #53（未合併）。
- **Changed:** PR #53（`s239/query-fusion`）：`backend/src/api/searchChannelB.ts`（`interleaveRankedLists`、旗標）、`backend/src/lib/wikiRepository.ts`（export `quotaBucket`）、`backend/src/lib/llmClient.ts`（`reasoning.effort`）、`backend/src/config/env.ts`（預設 `gpt-6-luna`、effort 解析與防呆）、`backend/src/server.ts`、`backend/scripts/_s226_knobAB.ts`、新 `backend/scripts/_s239_modelAB.ts`、`backend/scripts/groundedSynthesisRegression.ts`、`status-07cc7942c0.html`、`dev/source/status_page_test.mjs`、`.github/workflows/qc_report.yml`、`dev/source/check_monitor_health.py`、`dev/source/judge_acceptance.py`、文件（`backend/README.md`、`.env.example`、`DEPLOY_CHANNEL_B.md`、`README.md`、`dev/CODEBASE_CONTEXT.md`）、量度產物（`eval_runs/2026-10-1{3,8}_s239*`、`2026-10-21_s239model*`、`judge_runs/2026-10-21_s239_luna_none_r*`）· 收工：交接、本 log、`PROJECT_INDEX.md`、`DOC_SYNC_REGISTRY.md`、`PROJECT_DECISIONS.md`、`START_NEXT_SESSION_PROMPT.txt`、`dev/archive/SESSION_LOG_2026_Q3.md`。
- **Done:**
  - **根因**：`sen` 路由 1,135 段實測，答案段落（手冊 §3.3.2）原句排 1／4、展開句排 209／88；路由本身正確。另見頭兩格常被無關註腳佔（「學生」「安排」兩個二字詞即過 lead 門檻）。
  - **交替合併**：RRF 初稿以離線模擬否決；改交替合併後 185 題兩層量度、43 題答案層判官（Leonard 批准約 350 次）→ 不出貨（`net_after` +2.5、新增自信答錯 `cpd_induction_period_na`）。
  - **狀態頁**：頁面比對 `knowledge.json` 片段數與更新日誌；workflow 加 push／Issue 觸發（只認 owner 與機械人）與推送前 rebase；看門狗不計 skipped。
  - **模型遷移**：官方停用頁與價錢頁核實（經 web-fetch 代理）；判官凍結集 `gpt-6-luna`＋`none` 33/33 ×3 零錯放；答案層 36 題偏舊 0、偏新 15、耗時中位 3.4→2.8 秒；SDK 4.104 類型不認新 effort 值，以轉型送出（不升 4→7）；effort 只在模型用碼內預設時自動帶，防止 Render 現設的 `gpt-4o-mini` 被拒而靜默變空。
  - **S238 ② 核實**：10-19 排程在 Freshness #1 留 @mention 留言、Discovery #54 帶 @mention。
- **QC:** `npm run check`／`build`、`route_regression` 63/63、`regression:grounded` 50/50、`status_page_test` 全過、`check_monitor_health --self-test` 全過、`judge_acceptance --self-test`／`--check-parity`、環境組合 5 例；紅測四處（狀態頁比對、看門狗 skipped、effort 不繼承、knobAB 斷言 2 的空對照）皆轉紅；PR #53 build-gate SUCCESS。
- **Fix Record:** (1) 狀態頁新測試初稿把 22 小時前誤算為同日，修正的是測試日期，不是邏輯。(2) 第一次判官批次的 exit 1 來自迴圈最後一行 `[ $n -lt 3 ]` 的回傳值，三批實際全部完成（30＋28＋26 次）。(3) 第一次 effort 紅測沒有轉紅，是 sed 未套用；改用精確字串替換後確認轉紅。(4) 選題初版按 gold 次序補位會令幼稚園、人事、財務、校董會全部落選，改為平均間隔抽取。
- **Evidence disposition:** 量度產物入 git（eval_runs／judge_runs）；模型事實與量度入 `CODEBASE_CONTEXT.md`；選型取捨入 `PROJECT_DECISIONS.md`；Leonard 取向入長期記憶；暫存（sen_route.pkl、模擬腳本、批次清單）只在 scratchpad。
- **Sync:** `dev/DOC_SYNC_REGISTRY.md` S239 節。
- **Pending:** ① 模型遷移收尾（先重讀官方頁確認應轉的模型、#53 合併與 Render 改動、離線兩項選型）② 註腳佔格 ③ `EDBC_9_2019_E` 退役 ④ Gmail 確認 ⑤ 待 token 項。
- **Risks:** 2027-01-14 停用（交接 Risks 11）；新模型答案約短一半，未經用戶回饋；外部呼叫：S239 第一次批准前跑了 282 次 embedding，已事後補報。
- **Log maintenance:** `session_log_maintenance.py --check` 報 date trigger → `--apply`：320→269 行、11→9 條，2 條入 `dev/archive/SESSION_LOG_2026_Q3.md`（只搬不刪）；重查 `trigger=False`。工具再次在檔尾留下孤立 `ack:log-entry:start`（S224／S231 記載的 off-by-one），已刪；主檔 start／end 12／11 的 +1 失衡在本節之前已存在（HEAD 為 13／12），不動。「latest entry prompt block ok=False」為已知分歧（Kit 規定開場白不入 log，S224 起取 Kit）。
- **Opening-message mirror:** 由交接檔唯一 fenced 區塊重生並核對相等；全文不入 log。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->
