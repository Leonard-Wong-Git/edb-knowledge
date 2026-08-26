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

## 2026-08-26 Session 210 — 補返欠低嘅 eval，然後發現量度佢嘅閘本身壞咗

- **ID:** Claude_20260826_0748
- **Summary:** 由 OP⑥（S209 欠低嘅 eval 基線）開始。結果係零退步 —— 但拆 compare 嗰 5 條 blocking 嘅過程揪出兩件更值錢嘅嘢：量度用嘅閘本身有邏輯洞、同埋交接對 `gifted_policy_docs` 嘅描述啱啱好講反咗。Leonard 中途下多兩張單（EDBCM156 網上資源盤點、三摺頁入庫），最後拍板一條新 Backlog。
- **① OP⑥ 補跑 = 零退步：** 對 `2026-08-19_s207_after.json`，PASS=23/FAIL=0/errors=0。compare 報 5 blocking，逐條拆：**1 條 ERROR 錯喺基線檔** —— S207 嗰次 `nonlocal` 撞 Supabase `57014` statement timeout、記低 0 個源 verdict=None，今次同一條答得正常（PASS、8 個源）；**4 條 SET_LOST 全部係 top_k 位移** —— `edbcm156_2026`（今朝自動入庫）同 `edbcm135_2026`（8/19 後入庫）擠入 top_k=8，撞跌最尾位（掉低嗰個 before 排 [7]/[7]/[7]/[6]），四條 verdict 一個都冇變。擠入嚟嗰份係《2026/27學年 校本數字教育整體規劃及相關教師培訓》，入 `ai_intro`/`smart_teaching`/`elearning_fund` 題材啱。
- **② 量度嘅閘壞咗（本 session 最值錢一項）：** harness 明文寫「新源入 top_k 唔算 failure」（SET_ADDED 非 blocking），但**固定 top_k 之下新源入 = 一定有嘢跌出去，而跌出去嗰半邊當 blocking** —— 同一件事嘅兩個講法，一個放行一個叫停。Option A 每日跑兼自己 push main，即係**由今日起每個 session 開 compare 都會見到 blocking 而九成唔係退步**。同紀律 #14（只入唔出嘅清單必變牆紙）同一條病。修法：新 `DISPLACED` —— 要 (a) 有新入者、(b) 掉低嗰啲喺 cut line（`len(before) - len(added)`）以下、(c) after 唔短過 before，三者齊先降級，否則照 SET_LOST。blocking 5 → 1（剩低嗰條係基線檔自己嗰個 ERROR，應該紅）。
- **③ 開工探針 +10 無頁碼 —— 交接講反咗：** 451→461 全部係 `gifted_policy_docs`。攞 S207 版（`git show a7ad697`）同 S209 版 `carry_pages` 跑同一份 extract 對證：**10 條全部由「Page 8」變 `None`，S207 側無頁碼=0、S209 側=10**。嗰份 `policy_chin_March08.pdf` 得 8 頁，而 10 條入面 **9 條係 extract 尾嘅網頁段落**（`=== introduction === / === detail ===`，本身冇頁碼），舊邏輯由上面 PDF 段一路 carry 落去 = 叫用戶揭一份 8 頁 PDF 嘅第 8 頁去搵一段網頁文字。**所以交接寫「gifted 10/23 chunks 有缺陷等修」要反轉理解：係修好之後如實變成無頁碼。** 全庫「真缺陷」分類唔應該加呢 10 條。
- **④ `split_on_section_markers` gate 改由 extract 判：** S209 gate 喺 `source_section_urls(sid)`，但橫跨係**文字嘅屬性** —— 有 `=== label ===` 就跨得，同 registry 有冇 per-section URL 無關。兩個源一直喺閘外：`gifted_policy_docs`（chunk #13 實測揸住 page 8 尾 + `=== introduction ===` 頭 + 網頁內容）同 `g04`。改成 `len(split_on_section_markers(body)) > 1`，無 marker 嘅源 split 返一份 → 走舊路徑，byte 級不變。**Blast radius 全掃 261 個源：259 byte 級 no-op，只 g04（7→11）同 gifted（23→23）變。** 重入後 live 實查跨界 chunk **g04 5→0、gifted 2→0**，URL 歸屬冇變（各 1 條 distinct URL，冇生出假 deep link）。
- **⑤ eval 集 34 → 37：** 之前 34 條**一條都冇掂過** S209 兩個新源（掃 query 集：含保安／雲端／security／cloud 嘅 = 0 條；`g28` 同 `pcpd_cloud_computing` 喺成個 run 一次都冇出現）—— 即係 OP⑥ 嘅原定 baseline 對 OP⑦ 係空白，改完 regex 前後會一模一樣。補三條，**入檔前逐條打 live endpoint 實測先寫 `expect_any`**（紀律 #13：用該源真實內容嘅詞）：`cyber_campaign`「網絡安全運動」→g28 rank 0–2 @0.573；`cloud_privacy`「雲端運算 私隱」→pcpd rank 0–2 @0.688；`info_security_broad`「學校資訊保安」→RECORD_ONLY（返 SAG/role_facts_it/g24，g28 唔喺內 —— 呢個就係 OP⑥ 嘅撬點）。
- **⑥ EDBCM156/2026 網上資源盤點（Leonard 下單）：** 文件引用 10 條資源。**URL 喺 PDF 入面被換行斬斷**（`.../attachment/tc/edu-system/p`），逐條由原文接續行重組 —— 冇估（S209 紀律 #3 就係喺呢度中過）。結果：**4 條已入庫兼受監察**（行政摘要 5 chunks／附篇二 16／附篇一 20／IIT Summary 18），**6 條兩樣都冇**。用 Tavily 抽咗以前抓唔到嘅 EDB／教城頁。
- **⑦ 三摺頁入庫（Leonard 指示「入，留意可能有時限性」）：** 30MB／2 頁／149 幅圖／文字層 1,479 字元（Tavily 獨立抽到 1,476，兩者對得上）。4 chunks，store 17,572→17,576。`lifecycle` 由 `lifecycle.classify()` 判 = `reference`（**唔係我拍腦**）；`expiry_basis` 寫明真正時限風險係**被新版取代**，歸 `check_freshness` 嘅 content_hash 管唔係 `check_expiry`。**入完實測：搜得到但贏唔到** —— 「創新型終身學習者」rank 6（證明唔係 route 擋），但獨有詞「四大發展重點」（全庫只有佢一條）**rank=None**，輸畀無關課程文件 @0.538。成因：資訊圖 chunk = 三十幾個互不相連圖標籤。caveat 寫死入 registry notes。**唔建議加入 `digital_education` SOURCE_SET**。
- **⑧ 正文連結缺口（量度 + Leonard 拍板）：** 掃全庫 17,568 條 chunk：anchor URL（`wiki_chunks.url`，受每週一監察）**420** 條 vs 正文引用嘅 URL 形狀字串 **3,011** 條，重疊只有 **6** 條 → **3,005 條零監察**。`check_served_urls.py` 只 `select=url,source_id`、**從來唔讀正文**，所以係結構性缺口。**Leonard 定案：課程專頁唔監察**（2 條、逐學期換、耐用嗰半邊已在庫），力氣放喺正文連結，**入 Backlog 唔喺本 session 開**。
- **Changed:**
  - 改：`dev/source/eval_retrieval.py`（新 `_is_displacement()` + `DISPLACED` 狀態 + 4 條 self-test + docstring）、`dev/source/eval_queries.json`（+3 條，34→37）、`dev/vault/expand_vault.py`（split gate 由 registry 改為 extract 判）、`dev/source/source_registry.json`（+`debp_leaflet`）、`dev/DOC_SYNC_CHECKLIST.md`（+1 row）
  - 新：`dev/vault/debp_leaflet/`、`dev/source/eval_runs/` 四個 run（`2026-08-26_s210.json` / `_baseline37` / `_after_splitgate` / `_after_leaflet`）
  - 鏡像片段數 17,568 → 17,572 → 17,576（兩次都行 `live_display_sync(current_chunk_total(), live_total_count())`，**冇自己加減**）：`app.html` / `index.html` / `knowledge.json` / `role_facts.json` / `dev/knowledge/role_facts.json` / `README.md` / `K1_API_SPEC.md`
- **QC:** `eval_retrieval --self-test` 全綠（含 4 條新斷言，其中兩條**專證佢仲會紅**：cut line 以上跌出照 FAIL、after 短過 before 照 FAIL）；`test_carry_rules --self-test` 全綠 + `--prove-assertions` 19 條會紅；`check_expiry --self-test` 全綠；`session_log_maintenance --check` trigger=False（276 行／2 entries）。全 session 檢索淨影響（`baseline37 → after_leaflet`）：SET_LOST 1 / SET_ADDED 1 / RANK_SHIFT 2 / SCORE_MOVED 1 / SAME 32。
- **Fix Record（本 session 自己整出嚟嘅）:**
  - **Problem:** 我睇 Tavily 抽返嚟嘅頭 700 字元，一度判 `debp-pdp.html` 同教城兩頁「無實質內容、只有導覽」。
  - **Root Cause:** EDB／教城個 nav 極長（23,175 字元入面頭幾千字全係目錄），**真內容喺尾段**（debp-pdp 尾係一張培訓課程表，教城尾係兩級 9 單元課程 + 6 小時 CPD）。犯咗紀律 #2：negative result 冇問「訊號存在嘅話呢個工具顯唔顯示到」。
  - **Fix:** 改睇 body 尾段 + 關鍵字計數，兩頁都重判。已喺同一 session 內更正並向 Leonard 講明。
  - **Regression / rule update:** 紀律 #2 補一個具體實例入 opening message，唔開新規則。
  - **Problem 2:** 第一次量 blast radius 我攞「完全唔 split」做 old，結果報 5 個源變（含 g14/g17/g28）。
  - **Root Cause:** g14/g17/g28 現行**已經**行緊 split（有 `section_urls`），我攞錯咗對照基準 = 拿 pre-S209 同 S210 比。
  - **Fix:** 改用**現行 live 邏輯**（gate 喺 `source_section_urls`）做 old，重量 → 259 no-op / 2 變。已即時更正。
  - **Problem 3:** 兩次寫 JSON 都整出成檔 reformat（`eval_queries.json` 574 行、`source_registry.json` 7,723 行）。
  - **Root Cause:** 用咗 `indent=2` / `indent=1` 而冇對返原檔格式。
  - **Fix:** 先做 round-trip 保真測試（registry：`indent=2` 且**唔加尾隨換行** = byte 級一致），再插入。最終 diff 23 行 / 29 行。
- **Evidence disposition:** 可重用程序知識 → `DOC_SYNC_CHECKLIST.md` 新 row（切 chunk 邏輯，含「blast radius 要報 no-op 幾多」）+ `eval_retrieval.py` 嘅 `_is_displacement()` docstring；環境事實（PDF 管道要 python3.13）→ `CODEBASE_CONTEXT.md` + opening message 常用指令；當前狀態 → handoff `Current Baseline` / `Last Session Record`；對照 baseline → `dev/source/eval_runs/` 四個檔保留；逐條 compare 拆解同自己犯嘅錯 → 本 entry（kept as recent trace evidence）。
- **Sync:** DOC_SYNC **row 43「檢索 eval harness 改動」**命中並兌現（query set 變動連理由入 log、eval_runs 保留、before→after 齊）；**row 37「Channel-B vault source backfill」**命中並兌現（registry entry + 可達性實測 + 鏡像片段數同步）；**新增一 row「切 chunk 邏輯改動」** —— 原本全 registry 對呢類改動零命中（S209 做嘅正正係呢類），觸發 anti-pattern guard 故先補 row 再兌現。
- **Pending:** 見 handoff Open Priorities（⑥ route regex 已備好 before 檔，最順手）。Backlog 頭位＝正文連結 3,005 條零監察，第一步係全庫 URL 重組唔係開監察。
- **Risks:** `pay_adjust` 掉低 `edbcm135_2026`（尾位），成因係 g04 切細後多佔一個 top-k 位 —— verdict 仍 PASS，屬切細嘅真實代價；**如果之後再有源切細，留意同一效應會唔會累積**。另：`DISPLACED` 刻意唔覆蓋「同一個源攞多咗位」嘅情況（`added` 為空），呢個邊界係有意保留，唔好當佢係漏。
- **Log maintenance:** 寫 entry 前 `--check` = trigger=False（276 行／2 entries），寫完後仍未到 400 行／N≥11 門檻 → **no-op，唔做長期維護**。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S210, 2026-08-26): 平台 v3.3.0; Supabase 17,576 chunks; source_registry 276;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
無頁碼 chunk 465 (S209 收工 461; +4 全部係 g04 重切, 佢係 HTML 源本身冇頁碼)。
S210 = 補 S209 欠低嘅 eval (零退步) + 修量度嘅閘 + 修切 chunk gate + 入一個源。
自動化 active: 6 源監察 + Option A 自動入庫管道 (edb-knowledge-ops, 每日跑; 會自行 push main)。
開工時本地大機會落後 origin/main —— tree 乾淨 + 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

✅ S210 查實 (唔使再查):
  1. **S209 冇整跌檢索。** 補跑 eval 對 s207_after: PASS=23/FAIL=0/errors=0。compare 嗰 5 條 blocking
     逐條拆完冇一條係退步 (1 條錯喺基線檔自己, 4 條係新通函擠掉尾位、verdict 全冇變)。
  2. **無頁碼 +10 係修好嘢, 唔係壞咗。** 全部係 gifted_policy_docs; 用 S207 版 vs S209 版 carry_pages
     跑同一份 extract 對證, 10 條全部由「Page 8」變 None。嗰份 PDF 得 8 頁, 而 9/10 係網頁段落。
     **交接舊寫「gifted 10/23 有缺陷等修」要反轉理解。**
  3. **三摺頁 (debp_leaflet) 入咗庫但贏唔到。** 「創新型終身學習者」rank 6 = 搜得到、唔係 route 擋;
     但獨有詞「四大發展重點」rank=None。成因: 資訊圖 chunk = 三十幾個散裝圖標籤, 撐唔起 embedding。
     **唔建議加入 digital_education SOURCE_SET** (只會同更強兼已 routed 嘅 debp_blueprint 爭位)。
  4. **EDBCM156/2026 引用嘅 10 條網上資源, 4 條已入庫兼受監察, 6 條兩樣都冇。** 課程專頁 (EDB debp-pdp /
     教城 EdAcademy) **Leonard 拍板唔監察** (2 條、逐學期換、耐用嗰半邊已在庫)。
  5. **PDF 管道要 python3.13, 唔係 default python3。** 本機 default 係 homebrew 3.14, 冇 PyMuPDF;
     python3.13 先有 (1.27.2.3)。expand_vault --fetch 撞 PDF 會 ModuleNotFoundError: fitz。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」
     (S210 再中: Tavily 抽返嚟頭 700 字元全係導覽, 我一度當 debp-pdp / 教城兩頁「冇實質內容」;
      真內容喺尾段。EDB / 教城個 nav 極長, 睇頭唔睇尾必錯。)
  3. 報一個數之前打開數字背後至少一個實例親眼睇。
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
     (S210 用同一招處理 Supabase 57014 timeout: 重試 3 次全綠 → 判定偶發, 唔當退步。)
  7. 入庫 ≠ 可達。**S210 加多一層: 可達 ≠ 贏得到。** 三摺頁搜得到但獨有詞都攞唔到佢出嚟。
  8. 交接寫低嘅選項框架本身可以係錯 (S210 主線: 兩項交接描述被實測推翻)。
  9. 「應該冇」唔係「冇」。10. 報 population 數字要即刻拆類。11. 守門要證明佢會紅。
  12. 交付一個檔案之前 ls 實證佢存在。
  13. 揀嘅 phrasing 決定得出嘅答案 —— 判斷可達性要用該源**真實內容**嘅 query。
  14. 任何要人做決定嘅表面都要有出口; 只入唔出嘅清單一定變牆紙。
  15. (S210 新增) **量度工具本身要受同一套懷疑。** compare 個閘當「新源入 top_k」無害但當「同一件事
      撞跌尾位」係 blocking —— 固定 top_k 下係一件事嘅兩個講法。Option A 每日入庫, 呢個閘本來會朝朝紅,
      跟住冇人再睇。改一個閘之前先問「佢會唔會日日紅」。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/eval_retrieval.py --compare <before.json> <after.json>
  python3 dev/source/check_expiry.py --self-test ; --check ; --purge --sources <id> --apply
  python3 dev/vault/test_carry_rules.py --self-test ; --prove-assertions
  python3.13 dev/vault/expand_vault.py --fetch --sources <id>       # PDF 抽取一定要 3.13 (fitz)
  python3.13 dev/vault/expand_vault.py --embed --force --sources <id>  # 重入 (先 --dry-run 睇 blast radius)
  python3 dev/source/check_served_urls.py --check                   # ~300 URL, 約 5 分鐘
  python3 docs/qa/session_log_maintenance.py --check
  cd backend && npm run check && npm run build
  # 動過 chunk 之後一定要行 (唔好自己加減):
  python3 -c "import sys;sys.path.insert(0,'dev/source');import execute_ingest as e;e.live_display_sync(e.current_chunk_total(),e.live_total_count())"

🔜 NEXT (Open Priorities ①–⑥ 詳見 handoff):
  ⑥ digital_education route regex 加保安/雲端字眼 (**最順手, before 已備好** =
     dev/source/eval_runs/2026-08-26_s210_after_leaflet.json, 睇 info_security_broad 條)
  → ② 補 chunk-層儀器 → ① 檢索「可見 ≠ 見到啱嗰段」(必須重出 PLAN)
  ③ GUIDELINES_REGISTRY 落後 + registry-drift 監察 (Leonard 明確要求, 一半要佢落判)
  ④ 特殊學校編制表恢復  ⑤ 表格/註解 content_kind (同 ① 同一個根)
  Backlog 頭位: **正文連結 3,005 條零監察** (Leonard 2026-08-26 拍板; 第一步係全庫 URL 重組,
  唔係開監察 —— 3,005 係上限唔係實數, PDF 換行會斬斷一條 URL 變幾段)。
  其餘 Backlog: 學校網絡安全小貼士純圖像待 OCR; registry authority 欄位資料債; 拆 backend channel-a 半邊;
  時限性資料 UI 標示; 公眾提交表單; 範本 manifest; 承 S203 五項。

⚠️ 一項要留意 (唔使急住修): pay_adjust 條 query 掉低咗 edbcm135_2026 (尾位), 成因係 g04 由 7 條
  切細成 11 條之後多佔一個 top-k 位。verdict 仍 PASS。呢個係切細嘅真實代價 —— 如果之後再有源
  切細, 留意同一效應會唔會累積。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 (第一杯可能冷啟動, 要再叫一次; endpoint 係 https://edb-knowledge.onrender.com/health)
+ Draft HEAD==origin/main + Supabase count=exact (S210 收工 17,576, 自動管道每日入庫會加)
+ 無頁碼 chunk 數 (查法 text=not.like.*Page%20*%3D%3D%3D*, S210 收工 465)
—— 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

## 2026-08-24 Session 209 — 只入唔出嘅清單、一個永久偏差、四條死連結，同兩個新源

- **ID:** Claude_20260824_1848
- **Summary:** 由 Open Priority ⑥ 開始，發現佢個前提本身錯；跟住 Leonard 連下四張單（expiry 機制 / 待批清單收摺 / 修長期差 1 / 清 4 條 404），再加 g28 入庫同雲端資料研究。10 個 commit（另 ops repo 2 個）。片段數 **17,473 → 17,551**。
- **① OP⑥ 前提係錯的：** 佢寫「`check_served_urls.py` 只讀 registry `url_primary`」。實情該監察由 S172 出世就只掃 `wiki_chunks.url`。四重實測：live 逐源比對 16/16 section URL 在庫；今日 CI run #11 掃 299 distinct URL 全測；本地 `--verbose` 複現並逐條印 200；distinct URL 08-17 **284 → 299**（S207 新 deep link 自動入集）。紅測：唔存在嘅 `chapter-seven.html` → 404 → broken → 歸屬 g14。錯誤源頭 = S207 `verify_section_urls` docstring，已連同 handoff OP⑥、DOC_SYNC row 41 三處更正。**真缺口係 OP⑥ 第二句**（`--fetch` 得散文擋），已補 `refetch_blocked` 機制閘。
- **② Expiry（第 6 監察）：** `lifecycle.py` 三分類 —— `reference` 永不掃 / `dated_edition` **標示唔刪**（S204 定案保留）/ `ephemeral` 到期清走。用現成結構（`proposed.tier` + `dashboard_signals.deadlines[]`）算 `expires_on` = 最後 deadline + 30 日。兩邊 fail 向「留」。`check_expiry.py` = 22 斷言 + `--purge` 逐個核（唔係 ephemeral 又過期就拒絕）。ops `expiry-issue.yml` 每週二剔一剔清走，首跑成功。Backfill 26 個 `dated_edition`（零 ephemeral，assert 咗呢條路出唔到）。
- **③ 修長期差 1：** 根因唔喺 Supabase —— `current_chunk_total()` 由 `knowledge.json` 讀個數再加 delta 寫返去，**純加法流水帳從來冇對真數**，所以歷史任何一次少計都永久帶落去。改為入庫後由 store 讀真總數，唔夾出 CI annotation。
- **④ 清 4 條 404：** 2 條純 URL churn re-point（`eoebg_rates_2026`、`edb_pnet_annex_jul2025`，4 個引用數字逐個對返新 PDF）；2 條 `blnst_test_*`（13 chunks）係 2026-06-07 場次文件、EDB 整個 notes 家族落架 → 經 Leonard 批准退役。**刻意冇指去 `QA_BLNST_Apr26_tc.pdf`**（另一份文件；200-但-錯檔比 404 更難捉）。
- **⑤ 兩個新源：** `g28` 學校資訊保安（0 → **40 chunks**，7/41 份文件；31 份研討會簡報 + 2 份第三方單張 + 1 份純圖像海報冇入）。`pcpd_cloud_computing` PCPD 雲端運算指引 2025-01（**26 chunks**）—— registry 第一個 `authority != edb`。
- **Changed:**
  - 新：`dev/source/lifecycle.py`、`dev/source/check_expiry.py`、`dev/source/discovery_seen.json`、`dev/_s209_clear_404s.py`、`dev/_s209_build_g28.py`、`dev/vault/g28/`、`dev/vault/pcpd_cloud_computing/`
  - 改：`expand_vault.py`（refetch 閘 + `split_on_section_markers`）、`build_wiki_index.py`（`carry_pages` 唔跨 section）、`test_carry_rules.py`（17→41 斷言）、`execute_ingest.py`（真數 + lifecycle stamp）、`discover_sources.py`（first-seen）、`searchChannelB.ts`、`source_registry.json`、七個顯示鏡像檔、`served_url_check.yml`、`discover_check.yml`、ops `approval-issue.yml` + 新 `expiry-issue.yml`
- **QC:** `test_carry_rules --self-test` 41 全綠 / `--prove-assertions` 19 條會紅；`check_expiry --self-test` 22 全綠 / prove 13；`check_served_urls --self-test`、`discover_sources --self-test` 全綠；backend `npm run check` + `build` 通過；Supabase `count=exact` **17,551 == 公開顯示 17,551**；g28 40/40、g17 13/13、gifted 13/13 頁碼錨點全部喺自己文件範圍內；PCPD 三條 query live rank 0。
- **Fix Record（本 session 自己整出嚟嘅）:**
  - **Problem:** g28 第一次入庫，1 頁通函引用「第 2 頁」、3 頁通函引用「第 8 頁」。
  - **Root Cause:** 一個 chunk 可以橫跨兩份文件 —— `carry_sections` 判佢屬後者（掛後者 URL），但文字入面仲帶住前者嘅 `=== Page N ===`，後端 read-time parse 嗰個標記。`carry_pages` 救唔到，污染喺文字裏面。
  - **Fix:** `split_on_section_markers()` —— 有 `section_urls` 嘅源，切 chunk 前先喺 section 標記斬開。另 `carry_pages` 唔再跨 section carry。
  - **Verification:** 重入後 40/40 零超界。Blast radius 全 259 份 extract 逐份對：除 g28 外只有 `gifted_policy_docs` 變（10/23，已一併重入）。
  - **Regression / rule update:** 5 條新斷言入 `test_carry_rules`。§8b：呢個係 S206/S207 頁碼家族嘅延伸，唔開新規則。
  - **Problem 2:** 我報「學校網絡安全小貼士 PDF 404」。**Root Cause:** 我攞咗 grep 截斷咗嘅 href 估返個 URL 去 probe。**Fix:** 用真連結重驗，41/41 全 200。**紀律 #3 再應驗。**
  - **Problem 3:** 我加咗 g28 落 spotlight，同一 session 又移走。**Root Cause:** 用闊 phrasing（「學校資訊保安」）搵唔到就當「新細源 ANN 餓死」。用內容專屬 query 實測（未部署 route 改動嘅 build）：「Zoom 保安設定及使用建議」rank **0 @0.628**、「殭屍網絡」rank **1 @0.396**。**Fix:** 移走 overlay，理由寫入 code。同 S195 spotlight prune 同一陷阱、相反方向。
- **Evidence disposition:** 機制同不變式 → `lifecycle.py` / `check_expiry.py` / `test_carry_rules.py` 斷言；檔案地圖 → `CODEBASE_CONTEXT.md`；當前狀態同未修債 → handoff；sync 義務 → DOC_SYNC row 35 + 新 lifecycle row；本 session 追蹤 → 本 entry。
- **Sync:** DOC_SYNC row 35（監察／CI）命中並兌現，並加咗一句「改一個監察嘅 issue 開閂邏輯要順手檢查其餘」；row 41（per-chunk deep link）錯誤描述已更正並加 `refetch_blocked` 要求；新增「資料生命週期 / 到期清走」row。`CODEBASE_CONTEXT` Directory Map + AI Maintenance Log 已更新。凍結合約（`_meta` 2.3.0 / facts 455 / guidelines 2.6.1 / 158 / `PLATFORM_VERSION` 3.3.0）**全部零接觸**。
- **Pending:** 見 handoff Open Priorities。本 session 新開：`digital_education` route regex 冇保安／雲端字眼（改佢要 eval before→after）；`學校網絡安全小貼士` 純圖像待 OCR；registry `authority` 欄位資料債（273/274 寫死 edb，但庫入面已有 8 個非-EDB 域 208 chunks）。
- **Risks:** 本 session 加咗兩個新源、動咗切 chunk 邏輯，但**未行過 `eval_retrieval.py` before→after**。按 handoff 紀律 #5「任何檢索改動一律 eval 對為準」，呢個係已知欠賬 —— 下個 session 開頭應該補跑一次基線。
- **Log maintenance:** 寫 entry 前 `--check` = trigger=False（353 行 / 3 entries）；**寫完之後變 455 行過咗 400 門檻**，所以同一次收工內行咗 `--apply`：**455 → 276 行、4 → 2 entries、2 條歸檔入 `dev/archive/SESSION_LOG_2026_Q3.md`**，最新 entry 嘅 verbatim prompt 保留（`ok=True`），archive 零刪除。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S209, 2026-08-24): 平台 v3.3.0; Supabase 17,551 chunks; source_registry 274;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S209 = OP⑥ 結案 + 四張新單 + 兩個新源。片段數 17,473 → 17,551。
自動化 active: 6 源監察 (discover / freshness / served-url / 封面核對 / 通告 watcher / **expiry 新**)
+ Option A 自動入庫管道 (edb-knowledge-ops, 每日跑; 會自行 push main)。開工時本地可能落後 origin/main ——
tree 乾淨 + 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

⚠️⚠️ 第一件事 (S209 欠低): **補跑 eval_retrieval before→after 基線**。S209 動咗檢索但冇跑 eval ——
  加咗兩個源 (g28 40 chunks / pcpd_cloud_computing 26 chunks)、改咗多文件源切 chunk 邏輯
  (split_on_section_markers)、carry_pages 唔再跨 section。紀律 #5 明寫「任何檢索改動一律 eval 對為準」。
  blast radius 已實測只影響 gifted_policy_docs 一個既有源 (已重入), 但 before→after 未跑過。
  python3 dev/source/eval_retrieval.py --run --label s210_baseline --out dev/source/eval_runs/<date>_s210.json

✅ S209 查實 (唔使再查):
  1. check_served_urls.py 監察嘅係 wiki_chunks.url (per-chunk 欄), **從來唔係 registry url_primary**。
     所有 per-chunk deep link 一入庫即受每週一 11:00 UTC 監察。S207 docstring 寫錯, 已三處更正。
  2. 公開片段數以前係流水帳 (knowledge.json 讀個數 + delta), 唔係真數 —— 已改為由 Supabase 讀。
     **清走 chunk 之後一律行 live_display_sync(current_chunk_total(), live_total_count()), 唔好自己減。**
  3. EDB 冇「學校使用雲端服務指引」。g28 八份實質文件「雲」/cloud 共 0 次; EDB 資訊保安頁亦 0 次。
     最接近 = PCPD 雲端運算指引 (已入庫 pcpd_cloud_computing, 26 chunks, live rank 0)。
  4. 非-EDB 來源唔係先例: 庫入面已有 8 個域 208 chunks (ICAC 78 / EdCity 81 / CHP 14 / Cap279 11 / 其他)。
     但 registry authority 欄位 273/274 寫死 edb —— 資料債, 唔影響行為 (grep: 三處寫, 零處讀)。
  5. g28 個 hub 標題係「學校資訊保安建議措施」但內容係時序公告板, 冇「建議措施」文件。
     所以闊 query「學校資訊保安」返 SAG/role_facts_it/g19 而唔係 g28 **係啱嘅**。同 S194 ict_sss_2021 家族。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL (env.ts fallback 唔係實設)。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」
  3. 報一個數之前打開數字背後至少一個實例親眼睇。(S209 再中: 我 probe 咗個由截斷 href 估返嚟嘅 URL, 報咗個唔存在嘅 404。)
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
  7. 入庫 ≠ 可達。SOURCE_SET / TOPIC_KEYWORDS / SPOTLIGHT / route expansion 四層每層都要實測。
  8. 交接寫低嘅選項框架本身可以係錯。(S209 主線: OP⑥ 個前提由 S207 一句 docstring 流出去, 三處抄咗。)
  9. 「應該冇」唔係「冇」。10. 報 population 數字要即刻拆類。11. 守門要證明佢會紅。
  12. 交付一個檔案之前 ls 實證佢存在。
  13. (S209 新增) **揀嘅 phrasing 決定得出嘅答案。** 用闊 query 搵唔到就當「ANN 餓死」→ 加咗 spotlight;
      用內容專屬 query 一試就 rank 0, 同一 session 移走。同 S195 spotlight prune 同一陷阱、相反方向。
      要判斷「可達性」, 必須用該源**真實內容**嘅 query, 唔係你形容佢嘅講法。
  14. (S209 新增) **任何要人做決定嘅表面都要有出口。** 只入唔出嘅清單一定變牆紙, 跟住真訊號會被埋葬 ——
      Issue #6 由 8/3 起準確列住 4 條真 404 冇人跟, 因為佢混喺幾百項噪音入面。一 session 內四個實例。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/check_expiry.py --self-test ; --check ; --purge --sources <id> --apply
  python3 dev/vault/test_carry_rules.py --self-test ; --prove-assertions
  python3 dev/vault/expand_vault.py --embed --force --sources <id>     # 重入 (先驗 section URL, fail closed)
  python3 dev/source/check_served_urls.py --check                      # ~300 URL, 約 5 分鐘
  python3 docs/qa/session_log_maintenance.py --check
  cd backend && npm run check && npm run build

🔜 NEXT (Open Priorities ①–⑦ 詳見 handoff):
  ⑥ 補 eval 基線 (**最優先, 係 S209 欠賬**) → ⑦ digital_education route regex 加保安/雲端字眼 (要 ⑥ 先做)
  → ② 補 chunk-層儀器 → ① 檢索「可見 ≠ 見到啱嗰段」(必須重出 PLAN)
  ③ GUIDELINES_REGISTRY 落後 + registry-drift 監察 (Leonard 明確要求, 一半要佢落判)
  ④ 特殊學校編制表恢復 (等「資料對象 vs 問題對象」核對機制)  ⑤ 表格/註解 content_kind (同 ① 同一個根)
  Backlog: 學校網絡安全小貼士純圖像待 OCR; registry authority 欄位資料債; 拆 backend channel-a 半邊;
  時限性資料 UI 標示 (現行/已過期/已有新版, 前端至今零改動); 公眾提交表單; 範本 manifest;
  承 S203 (judge 對象移植 / Channel A Option 2 / PUBLISH_PAT / 總帳 / g24-sag 合併)。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 (第一杯可能冷啟動 warm=false, 要再叫一次) + Draft HEAD==origin/main + Supabase count=exact
(S209 收工時 17,551, 但自動管道每日入庫會加) + 無頁碼 chunk 數 (查法 text=not.like.*Page%20*%3D%3D%3D*)
—— 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

## 2026-08-20 Session 208 — 五個月里程碑回顧 + 三張分享圖（純溝通交付，零 code / 零資料改動）

- **ID:** Claude_20260820_0826
- **Summary:** Leonard 準備對外分享，要一份「由最初痛點到今日」嘅里程碑回顧，再要出圖。全 session **零 code / 零資料 / 零 Supabase / 零對外合約改動**；起手五項探針全綠（served v3.3.0 / Render `/health` warm 455 / HEAD==origin/main `2421fb5` / chunk 17,473 / 無頁碼 451）。
- **① 挖歷史範圍：** `git log` 578 commit（2026-03-17 首 commit）+ SESSION_LOG S1–S207（含 `dev/archive/SESSION_LOG_2026_Q1~Q3.md` 共 14,196 行，Q1 最早條目 2026-03-09 早過 repo 首 commit）+ `PROJECT_MASTER_SPEC` §A/§B/§F + `PROJECT_DECISIONS` + `CODEBASE_CONTEXT`。
- **② 敘事定調（回顧檔嘅骨幹）：** 起點唔係知識庫，係「EDB 通告分析系統」需求文件，同日轉調（冇知識庫嘅分析冇根據）→ 六階段：人手審核庫 / 雙通道＋向量搜尋（600 字元、overlap 60、810 片段、US$0.002）/ 資料質素治理（48% 重複、1,001→792→455）/ **★★ S119 轉捩點**（Leonard 實測五條 query 裁定原文搜尋贏、同日定「頁數可追溯」為北極星；診斷出 113 份 extract 只有 39 份帶頁標記）/ 功能爆發後收斂（S151 拆走成個 admin surface −1,176 行）/ 量度＋回頭執頁碼（S206 1,859→451、S207 指章）。
- **③ 交付物：**
  - `dev/PROJECT_MILESTONES_REVIEW.md`（新）—— 六階段敘事、數字弧線、**功能生死簿**（詞雲／舊通道介面／admin 後台／三個實驗頁／通告分析停後重開／文件分析＋修訂合併／Word 批註／範本下載暫收／分數顯示，共 9 項加咗又拎走）、11 條紀律。
  - `dev/INFOGRAPHIC_PROMPT.md`（新；Leonard 講「係你照出 prompt 俾我」後**整份重寫**）—— 三條自足 prompt，**指定輸出 PNG + 繁體中文 + 書面語**（初版係口語敘述、只講 HTML），數字寫死喺 prompt 內，收圖 agent 零查詢；明寫唔好用純圖像生成模型（中文密集文字必出豆腐字）。
  - `dev/design/` 三組 html+png：A `milestones_infographic` 2400×10106 / B `milestones_slide_16x9` 3200×1800 / C `milestones_insights_a4` 2382×3369。
- **④ 出圖管道（可重跑）：** 自足 HTML（inline CSS、零外部資源）→ headless Chrome `--force-device-scale-factor=2或3 --window-size=W,H --screenshot` → A 嗰張再用 Pillow 由下而上搵最後一行非背景色像素、裁走尾部（留 96px）。**環境事實：本機冇 PingFang**（`/System/Library/Fonts` 只有 `STHeiti Light/Medium.ttc`、`Songti.ttc`、`Hiragino Sans GB.ttc`），字體堆疊靠 STHeiti 兜底；換機重出前必須先驗字體。
- **Changed:**
  - `dev/PROJECT_MILESTONES_REVIEW.md` — 新檔
  - `dev/INFOGRAPHIC_PROMPT.md` — 新檔（後整份重寫為 PNG + 書面語版）
  - `dev/design/milestones_infographic.{html,png}` / `milestones_slide_16x9.{html,png}` / `milestones_insights_a4.{html,png}` — 新檔
  - `dev/CODEBASE_CONTEXT.md` — Directory Map `### S208 additions`（5 條，連重出指令 + 字體注意）+ AI Maintenance Log S208
  - `dev/SESSION_HANDOFF.md` / `dev/SESSION_LOG.md` / `START_NEXT_SESSION_PROMPT.txt` — closeout
- **QC:**
  - **數字逐個對源**（唔靠記憶）：`git rev-list --count HEAD`=578；chunk 弧線 810（S72）→2,822（S92）→10,682（S120）→15,874（S190）→**17,473**（live 探針）；facts 109→1,001（S88）→792（S102）→455（S111）；頁碼 13.2%→23.7%→32.2%（S119/S120）；97.4% = (17473−451)/17473 = **97.42% 實算**；切片 600/60 由 `build_wiki_index.py:59-60` 讀出；4 個公開 tab 由 `app.html` `FEATURE_TABS`（`templates:false`）讀出；5 個監察由 `.github/workflows/` 實 list；registry 268 由 JSON 實數。
  - **三張 PNG 逐張開圖肉眼檢查**：零切字、零豆腐字、零爆版（B / C 係固定高度 `overflow:hidden`，特別驗過底部冇被裁）。
  - `git status` 證零 code / 零資料檔改動（只有新文件 + `CODEBASE_CONTEXT`）。
- **Fix Record（本 session 自己嘅錯）:**
  - **Problem:** 回顧檔初稿兩個起點數字寫錯 —— 「登記來源 8 份底稿」同「公開分頁 4 → 8 → 4」。
  - **Root Cause:** 憑印象寫，冇對源。8 份其實係 KB01 嘅角色知識庫底稿（唔係 source_registry，registry S48 先建）；公開分頁起點係 6（S74 鎖定架構已有 6 個 tab）。
  - **Fix:** 改為 `120 → 151 → 244 → 268` 同 `6 → 8（高峰）→ 4`，兩份檔同步改，殘留 grep clean。
  - **Verification:** `grep -n "8 份底稿\|8 → 120"` → clean。
  - **Regression / rule update:** 唔升格為新規則 —— 呢個係紀律 #3（報數前打開實例）嘅**再次應驗**，已寫入 handoff `Last Session Record` 教訓 (a) 同開場白紀律 #3 括號。§8b：monitoring。
  - **Problem 2:** `dev/design/milestones_infographic.png` 生成並驗證後，喺磁碟消失（下一步 `ls` 先發現）。
  - **Root Cause:** 未確定（非本 session 任何指令所刪；`rm` 只掃 `_` 前綴中介檔）。
  - **Fix:** 同一條管道重出，尺寸雜湊一致（2400×10106）。
  - **Regression / rule update:** 新增紀律 #12「交付一個檔案之前 ls 實證佢存在」，已入開場白。
- **Evidence disposition:** 敘事同數字 → 新 deliverable `dev/PROJECT_MILESTONES_REVIEW.md`（point-in-time，非 SSOT）；檔案地圖 + 重出指令 + 字體注意 → `CODEBASE_CONTEXT.md`；當前狀態 → handoff；session trace + QC → 本 entry。
- **Sync:** DOC_SYNC **row 26「Knowledge operating architecture / planning doc」命中並兌現**（Directory Map ✓ / AI Maintenance Log ✓ / handoff priorities N/A —— 冇 follow-up work 改變 / 本 log entry ✓）。**唔命中：** row 44（無 endpoint、無前端 surface）、row 37/39/42/43（零 code 改動）。凍結合約 / `PLATFORM_VERSION` / Supabase / Render / Pages 全部零接觸 → 無 display-sync、無 redeploy。`PROJECT_DECISIONS.md` 不觸發（無新架構決策，只係把既有歷史重述成對外材料）。
- **Pending:** Open Priorities ①–⑥ 原封不動（本 session 零 OP 推進）。Backlog 不變。
- **Risks:** 無新增。⚠️ 回顧檔同三條 prompt 內嘅數字係 **2026-08-19 快照**；日後入庫會令 chunk / registry 數字過時，改字要 `PROJECT_MILESTONES_REVIEW.md` + `INFOGRAPHIC_PROMPT.md` + 三個 HTML 一齊改（三處都寫死咗數字）。
- **Playbook 留底（§14，Leonard 追問「未 commit 去 playbook？」後補做）:**
  - 交 `inbox/2026-08-20-policychecker-cjk-infographic-render-yourself.md` —— 中文密集資訊圖唔好交俾 image agent、自己 HTML → headless 截圖，連三個實測坑（字體堆疊要驗 / 長圖 auto-crop / 固定高度 `overflow:hidden` 要驗底部）。狀態老實標 **building-block**（一部機、一個 session、一個 OS）。
  - **查重命中現有卡 `conventions/system-mechanism-infographic-prompt.md`** —— 嗰張講「點寫 prompt 交俾 design/image agent」，五條硬規則我照跟；但佢**通篇假設交俾 image agent**，而 CJK 密集文字場景實測會爆。按 §3b「整合先於新增」，提案明寫**請 librarian 併入嗰張卡而唔好開新平行卡**，並指出呢個張力。`usage/policychecker.log.md` +1 行 lookup。
  - 🔴 **順手發現 S207 嘅留底其實從未 commit**：4 份 proposal 檔寫咗落 disk 就冇 `git add`，但 S207 收工紀錄同 handoff 都寫「Playbook inbox 交咗 4 份 proposal」。已一併 commit（`d96dc25`）。**教訓：寫咗檔 ≠ 交咗；§14 留底要 commit + push 先算數，收工要實查 `git status`。**
  - 本地仲有 **8 個其他 project 嘅 commit 一直未 push**（小學科學科 usage ×5 + inbox ×1、edb-circular inbox ×1），遠端有 **2 個 librarian commit 未 pull**（已處理 5 份 P6Sci 提案、出咗 4 張新卡）。`git merge-tree` 先驗零衝突，行 merge（非 rebase，唔重寫其他 session 嘅 commit）後全部 push。playbook HEAD == origin/main、tree 乾淨。
- **Log maintenance:** `session_log_maintenance.py --check` = **trigger=False**（215 行 / 2 entry，加本 entry 後仍 <400 行、最舊 entry 2026-08-18 <30 日）→ no-op，無 archive。順帶覆核：S207 記錄第 5 點寫住「log 已過 400 行、留待收工做」係 **stale**（該歸檔 S207 收工已完成），已喺 handoff 同開場白清走。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S208, 2026-08-20): 平台 v3.3.0; Supabase 17,473 chunks; source_registry 268;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S208 = 純溝通交付, 零 code / 零資料 / 零 Supabase / 零對外合約改動: 挖 578 commit + S1–S207 出
dev/PROJECT_MILESTONES_REVIEW.md (五個月里程碑回顧: 六階段 / 數字弧線 / 功能生死簿 / 11 條紀律),
dev/INFOGRAPHIC_PROMPT.md (三條自足出圖 prompt, 指定 PNG + 繁中 + 書面語), 三張 PNG 已 render 落
dev/design/ (A 長圖 2400x10106 / B 16:9 3200x1800 / C 三個反直覺發現 A4 2382x3369, HTML 原檔同放)。
S207 = 網頁源指章 (section_urls, g14 76 條 + g17 13 條 per-chunk deep link)。
S206 = 頁碼指路 (無頁碼 1,859 → 451)。
自動化 active: 5 源監察 (discover / freshness / served-url / 封面核對 / 通告 watcher) + Option A 自動入庫管道
(edb-knowledge-ops, 每日跑; 會自行 push main 並更新片段數)。開工時本地可能落後 origin/main —— tree 乾淨
+ 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

✅ 頁碼機制 (S206 查實, 唔使再查): 頁碼唔係 DB 欄位 —— backend extractDominantPage()
  (searchChannelB.ts) 喺 chunk 文字度 read-time parse `=== Page N ===`。前端 mobile.js:519 / app.html:2503,3404
  見到 page 就出「頁 N ↗」+ #page=N (只限 PDF url)。自動管道 execute_ingest.py 一直用
  build_wiki_index.chunk_text_with_page_carry, 從無此問題; 缺口只喺人手 expand_vault 條路, 兩層已修。

✅ 網頁源指章機制 (S207 查實, 唔使再查): 網頁冇頁碼, 所以逐條 chunk 寫返自己嗰章嘅 URL ——
  wiki_chunks.url 本身就係 per-chunk 欄位, 前端/後端/schema 完全冇改過。開關喺 source_registry.json
  嘅 section_urls (label → 絕對 URL, opt-in, 冇填 = 行為不變)。入庫前逐條 HEAD 驗 200, fail closed。
  ⚠️ g14 / g17 嘅 extract 唔准 --fetch: 佢哋係 S146 用一個已經唔存在嘅多頁 crawler 砌, 現行
  extract_html_text 只抓 url_primary 一頁, 一 refetch 就剷走其餘 section。
  ⚠️ 認段落標記一定要「先剷頁碼標記, 再認段落標記」兩步; 同一次序喺 cleanChunkText 亦係 load-bearing。
  詳見 dev/vault/test_carry_rules.py 嘅斷言。

✅ 對外分享材料 (S208 新增, 要改字直接搵呢兩個檔):
  dev/PROJECT_MILESTONES_REVIEW.md = 敘事同數字嘅單一來源 (point-in-time, 唔係 SSOT; live 數字仍以本檔為準)。
  dev/INFOGRAPHIC_PROMPT.md = 三條出圖 prompt, 數字寫死喺 prompt 入面, 改數字要兩個檔一齊改。
  ⚠️ 出中文圖前先確認字體: 呢部機冇 PingFang, 繁中靠 STHeiti / Songti TC 兜底 —— 唔驗就會出咗豆腐字先發現。
  重出指令同裁圖方法已寫入 CODEBASE_CONTEXT Directory Map。

⚠️⚠️ 貫穿全局 (S199 用真金白銀學到): judge / synthesis 用嘅 model 唔係 code default。
  env.ts fallback 係 gpt-4.1-nano, 但 Render 實設 OPENAI_MODEL=gpt-4o-mini。/health 唔報 model。
  任何 judge/synthesis 量度, 引用做「生產行為」之前必須去 Render dashboard 確認。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」搵已發生事件做對照組。
  3. 報一個數之前打開數字背後至少一個實例親眼睇。搜尋命中唔算證據。
     (S208 再中一次: 寫回顧時兩個起點數字憑印象寫, 對源之後兩個都錯。)
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
  7. 入庫 ≠ 可達。SOURCE_SET / TOPIC_KEYWORDS / SPOTLIGHT / route expansion 四層每層都要實測。
  8. 交接寫低嘅選項框架本身可以係錯。動手前 live 重現 + 逐條算 exact cosine。
  9. 「應該冇」唔係「冇」。用戶答「應該一行都冇」係期望語氣, 追問一句先落結論。
  10. 報一個 population 數字要即刻拆類: 邊部分修得到 / 修唔到 / 唔關事。
  11. 守門要證明佢會紅 (--prove-assertions 模式第一次跑就捉到兩個 regex 陷阱)。
  12. (S208 新增) 交付一個檔案之前 ls 實證佢存在。「我頭先生成過」唔算 ——
      milestones_infographic.png 生成後一度喺磁碟消失, 交付時先發現, 重出即解決。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/eval_retrieval.py --compare <before.json> <after.json>
  python3 dev/vault/expand_vault.py --fetch --force --sources <id>     # 重抽 (⚠️ table 源禁用, 見 registry notes)
  python3 dev/vault/expand_vault.py --embed --force --sources <id>     # 重入 Supabase (先 embed 後刪再入)
  python3 dev/vault/test_carry_rules.py --self-test ; --prove-assertions
  python3 dev/source/judge_acceptance.py --self-test ; --plumbing-check
  python3 docs/qa/session_log_maintenance.py --check
  cd backend && npm run check && npm run build
  curl -s https://edb-knowledge.onrender.com/api/stats/usage

🔜 NEXT (Open Priorities ①–⑥ 詳見 handoff; §3 項目全部要 PLAN + Leonard go):
  ⚠️ S208 零 OP 推進 —— 以下六項同 S207 收工時完全一樣, 唔好誤讀成有進展。
  ① 檢索「可見 ≠ 見到啱嗰段」—— 舊描述已被 S206 實測否定, 必須重出 PLAN。詳見 handoff ①。
  ② 補 chunk-層儀器 (做 ① 之前)。eval harness 只記 source_id, 量唔到「見唔見到啱嗰段」。
  ③ GUIDELINES_REGISTRY 落後 102 個來源 + 加 registry-drift 監察 (Leonard 明確要求)。
  ④ 特殊學校編制表恢復 (等「資料對象 vs 問題對象」核對機制)。
  ⑤ 表格 / 註解 content_kind 分類 —— 同 ① 同一個根。
  ⑥ per-chunk deep link 冇監察: 89 條 chunk 帶住自己嗰條子頁/附件 URL, 但 check_served_urls.py
     只讀 registry url_primary。加一段掃 section_urls 全部值 (得 16 條, 成本極低)。
  建議次序: ⑥ (細、低風險、補啱啱開嘅缺口) → ② (儀器) → ①。③ 有一半要 Leonard 落判 (邊類該公開瀏覽)。
  Backlog: 拆 backend channel-a 半邊 (S205 已解鎖前置); 時限性資料標示 + 第 6 監察; 公眾提交表單;
  範本 manifest 更新後開返 FEATURE_TABS.templates; CID 類真亂碼未量度; 承 S203 (judge 對象移植機制 /
  Channel A Option 2 / PUBLISH_PAT / 總帳 / g24-sag 合併)。

ℹ️ 使用計數器 /api/stats/usage 現值 5 (S206 驗 UI 時瀏覽器發出, API 呼叫全部帶 x-probe 排除)。
  Leonard 明示不用理, 但讀第一個真實用量數字時要扣返。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 (第一杯 curl 可能係冷啟動 warm=false, 要再叫一次) + Draft HEAD==origin/main + Supabase
count=exact (應為 17,473) + 無頁碼 chunk 數 (應為 451; 查法 text=not.like.*Page%20*%3D%3D%3D*) —— 然後
向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

<!-- ack:log-entry:end -->
