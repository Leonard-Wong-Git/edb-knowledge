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

## 2026-08-19 Session 207 — 指章唔係指頁：per-chunk 子頁 URL + g14/g17 三缺陷 + 兩個源解亂碼

- **ID:** Claude_20260819_S207
- **Summary:** Leonard「全做」。清 Open Priority ①（HTML 源指章）+ ②（g14 三個同源缺陷），順手揪出並修好兩個 source 喺生產庫亂碼咗。**Supabase 總數 17,473 不變**（91 刪 91 入）、`source_registry` 268 不變、平台 v3.3.0 不變、凍結合約零接觸（`_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158）。
- **① OP① 指章（`wiki_chunks.url` 逐條寫子頁）:** 關鍵觀察係 `url` 本身**已經係 per-chunk 欄位**，只不過入庫時全部填同一個 landing 頁 —— 所以前端、後端、schema **一律唔使改**。新 `carry_sections()` 喺 `build_wiki_index.py`（同 S206 `carry_pages` 同一契約：chunker-agnostic、無標記源全 None 即完全 no-op），`source_registry.json` 加 `section_urls` opt-in map，`expand_vault.build_chunks_from_vault_file` 消費。**g14 76 條 → 10 個子頁；g17 13 條 → 6 個目標（3 子頁 + 3 附件 PDF，後者仲保住 `#page=N`，live 實見 `page=3`）。** Map **逐個 label 寫實、唔准 base+suffix 推導** —— g17 就係反例：3 個 slug 喺 `whole-school-approach-to-guidance-discipline/`，3 個附件喺 `/attachment/...`，任何推導都錯。
- **② 交接嘅「只有 g14 有真 slug」講少咗:** 交接寫 g17 嘅標記係附件 PDF 檔名。實測 g17 頭 3 個（`cornerstone`/`development`/`framework`）**係真子頁**，只不過唔喺 registry `url_primary` 嗰條 path 之下（要去 landing 頁抓 link 先見到）；後 3 個確係附件 PDF，一樣指得到。所以 g17 6/6 全部有得指。
- **③ Fail-closed 閘即刻收貨:** 入庫前逐條 HEAD 驗 200，一條唔過即 skip 成個 source。**第一次跑就捉到我自己個錯** —— 3 條附件 PDF 砌漏咗 `/attachment` 前綴，3/6 條 404。冇呢個閘就會靜靜哋入咗庫（per-chunk URL 冇任何監察讀，要等用戶撳落去先知）。HEAD ≥400 會再試 GET 先落判（有站拒 HEAD）。
- **④ 兩個 regex 陷阱（今次真正嘅技術教訓）:**
  1. **Overlap 令標記甩行錨。** expand_vault 個 chunker 會用空格接 overlap 尾巴，令原本獨佔一行嘅標記變咗 line-middle（`…培育課程。 === chapter-one ===`）。用 `^…$` 錨行嘅 regex **靜靜哋只認到全份文件第一個標記**，之後 74 條全部當 `introduction`。
  2. **放寬之後即出 false positive。** 兩個相鄰頁碼標記（`=== Page 5 === 6 (Blank Page) === Page 6 ===`）前者收尾 `===` 同後者開頭 `===` 夾住中間正文 → 讀成章節名。全庫實測 **847 個幻影 label 橫跨 135 個源**。正解係**兩步**：先剷頁碼標記，再認段落標記；lookahead 唔 work（會俾空白 run 嘅 backtracking 打敗）。同一個次序喺 `cleanChunkText` 都係 load-bearing —— 段落 pass 一定要行喺頁碼 pass **之後**，否則會連中間正文一齊剷。
- **⑤ OP② 三缺陷:** (a) **title** —— extract header 寫《校本資優培育**計劃**指引》，EDB 官方同 registry 都係**課程**指引；核實過**所有公開鏡像（`guidelines.json` / `app.html` / `data.json`）本來就啱**，錯嘅只有 vault extract 一份，即係只影響 chunk 顯示。g17 個 title 只係 registry 嘅風格變體、唔係事實錯誤，**冇郁**。(b) **標記外洩** —— 用修正後嘅偵測器實數 **22 條橫跨 g04/g14/g17**（唔係我第一次報嘅 683，嗰個係 ④.2 個 false positive）；喺 `cleanChunkText` 一次過修，覆蓋所有源、past and future、零 chunk id 成本。(c) **導覽雜訊** —— EDB 把 nav/footer chrome 放喺 content column 入面，BeautifulSoup 剷唔到：g14 70 行 + g17 21 行讀返出嚟變咗引文一部分。新 `strip_web_chrome()`（**只做整行 exact match**，句中含同樣字眼唔會中）現已套用喺每次 HTML 抽取。
- **⑥ 額外揪出：g20 / g25 生產庫亂碼。** EDB 送 `Content-Type: text/html` **冇 charset** → requests 跌返 ISO-8859-1，而文件自己 `<meta>` 宣告 UTF-8 → `resp.text` 逐 byte 亂碼（`å­¸æ ¡æ´»å…`）。**反直覺位：** 個 200 字下限守門一直放行呢兩條，**正正因為佢哋壞咗** —— 亂碼令每個中文字變三個 latin-1 字元、字數虛脹；encoding 修好之後真文字反而唔夠 200 字被拒收。加 `min_extract_chars` per-source override（呢兩個本來就係 link-hub landing 頁，短係正常）。
- **Changed:**
  - `dev/vault/build_wiki_index.py` — 新 `SECTION_MARKER_RE` + `carry_sections()`（`a7ad697`）
  - `dev/vault/expand_vault.py` — `source_section_urls()` / `verify_section_urls()`（fail closed）/ per-chunk url 派發 / `strip_web_chrome()` / charset 修正 / `min_extract_chars`（`a7ad697`）
  - `dev/vault/test_carry_rules.py` — **新檔**，`carry_pages` + `carry_sections` 共 14 條不變式，`--prove-assertions` 模式故意用 no-op 實作證明測試會紅（`a7ad697`）
  - `dev/_s207_clean_html_extracts.py` — **新檔**，一次性清 g14/g17 extract，帶「行多重集差異必須淨係 chrome 白名單 + title 修正」嘅閘，唔過就唔寫（`a7ad697`）
  - `dev/source/source_registry.json` — g14/g17 `section_urls` + notes（含「⚠️ 唔准 `--fetch`」）、g20/g25 `min_extract_chars` + notes（`a7ad697`）
  - `dev/source/eval_retrieval.py` — retry clause 由 `(URLError, TimeoutError)` 擴到 `(OSError, http.client.HTTPException)`；之前一個裸 `ConnectionResetError` 會中途炸死成個 run，蝕晒已經跑咗嘅 query（`a7ad697`）
  - `dev/vault/g14|g17|g20|g25/extract_*.txt` — 清洗 / 重抽（`a7ad697`）
  - `backend/src/api/searchChannelB.ts` — `cleanChunkText` 加段落標記 pass（`3dc9952`）
  - `dev/DOC_SYNC_CHECKLIST.md` — 新 row「Per-chunk deep link」
- **QC:**
  - `test_carry_rules.py --self-test` **14/14 PASS**；`--prove-assertions` 對 no-op 實作**觸發 8 條**（守門證明得到會紅）。
  - Section URL map **16/16 HEAD 200**（動 embedding / DB 之前）。
  - **零內容遺失閘**：g14 全部 77 條、g17 全部 12 條舊 chunk 嘅文字，喺清洗後 extract 入面**全部搵得返**。唯一一條「唔覆蓋」係一個 chunk 開頭嘅 3 字殘片（`要內容`，chrome 行被 chunk 邊界切開），其餘 401 字完整存在 —— 即真內容 100% 保住。
  - **g20/g25 encoding-only 證明**：舊文字 `latin-1 → utf-8` 還原之後同新 extract **逐字對到**，唯一差異係舊資料真係爛咗嘅位（`十八日` 存成 `十<壞字>日`）→ 反證舊 row 係**有損**，唔可以喺顯示層修完算。
  - `cleanChunkText` 5 個 case 實測（slug 標記剷走 / 中文標題標記剷走 / **兩個相鄰頁碼標記中間嘅正文保住** / 淨頁碼標記 / 句中 `===` 唔郁）。
  - `npm run check` / `npm run build` 兩個 exit 0。
  - **eval before→after**：30 SAME、2 RANK_SHIFT（`bus_escort`、`gifted`，都係組內換位）、**1 SET_ADDED（`kg_admission` 多咗 `g25` —— 亂碼修好之後佢先至搜得到）**、0 regression。1 條 error（`nonlocal` 撞 Supabase `57014` statement timeout）**唔係回歸**：live 連環重試 3 次，回傳同 baseline 一模一樣嘅 8 個 source。
  - **Post-deploy live 實測**：g14 出 `chapter-six.html`、title 顯示《校本資優培育課程指引》、引文冇標記冇雜訊；g17 出 `framework.html` / `development.html`，附件 PDF chunk 出 `page=3` + `…body_chi.pdf`；g25 喺「幼稚園售賣教育用品收費服務指引」**score 0.753** 命中。
- **Evidence disposition:** 兩個 regex 陷阱嘅理由 → code 註釋 + `test_carry_rules.py` 斷言（唔會被重生沖走）；`section_urls` 嘅 opt-in / fail-closed / 唔准推導規則 → `dev/DOC_SYNC_CHECKLIST.md` 新 row；「唔准 `--fetch`」→ registry notes；逐步量度數字 → 本 entry；四條可轉移經驗 → Playbook inbox（見 Sync）。
- **Sync:** DOC_SYNC row 37（Channel-B vault backfill）命中並兌現：registry entry ✓、SOURCE_SETS / TOPIC_KEYWORDS parity **N/A**（零新源、零 route 改動）、handoff Current Baseline ✓、本 log entry 帶閘證據 ✓、CODEBASE_CONTEXT AI Maintenance Log ✓（無新 vault 目錄）。**Registry updated:** 新增「Per-chunk deep link」row（原本冇 row 覆蓋 per-chunk URL 呢個 change type）。公開鏡像 `guidelines.json` / `app.html` GUIDELINES_REGISTRY / `data.json` **零改動**（實查過 g14 title 喺嗰三處本來就啱）。Playbook inbox 交咗 4 份 proposal（S206 欠低嗰兩條 + S207 兩條），`usage/policychecker.log.md` append 2 行。
- **Pending:** 見 handoff Open Priorities。本 session 新開一項：**per-chunk URL 完全冇監察覆蓋** —— `check_served_urls.py` 只讀 registry `url_primary`，而家有 89 條 chunk 帶住自己嘅 deep link，冇任何嘢會發現佢哋壞咗。
- **Risks:**
  - 上面嗰條監察缺口（已入 Open Priorities）。
  - `g14` / `g17` 嘅 extract **唔可以 `--fetch`**：佢哋係 S146 用一個已經唔存在嘅多頁 crawler 砌出嚟，現行 `extract_html_text` 只抓 `url_primary` 一頁，一 refetch 就剷走其餘 9 / 5 個 section。已寫入 registry notes，但呢個係「靠註釋擋」，唔係機制擋。
  - 我第一次報「683 條 chunk 有標記外洩」係錯數（偵測器 false positive），修好偵測器之後係 22 條。**差 31 倍。** 呢個正正撞返 S206 第 10 條紀律 —— 而我係報咗數之後先打開實例睇。
- **Log maintenance:** `--check` 觸發（461 行 > 400 門檻、9 entry）→ 收工跑 `--apply`：**461 → 125 行、9 → 2 entry、7 條歸檔入 `dev/archive/SESSION_LOG_2026_Q3.md`**（`--self-test` 5/5 先跑過）。

### Next Session Opening Message

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S207, 2026-08-19): 平台 v3.3.0; Supabase 17,473 chunks; source_registry 268;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
S207 = 「指章唔係指頁」: wiki_chunks.url 本身係 per-chunk 欄位, 加 section_urls opt-in map 令 g14 76 條
指返 10 個子頁、g17 13 條指返 6 個目標 (3 子頁 + 3 附件 PDF, 後者仲有 #page=N); 順手清 g14 title
(計劃→課程)、22 條外洩段落標記 (喺 cleanChunkText 修)、91 行 EDB nav/footer chrome; 另揪出 g20/g25
一直係亂碼 (EDB 唔出 charset → requests 當 ISO-8859-1) 並重抽。前端/schema 零改動, chunk 總數不變。
S206 = 修好「頁碼指路」(expand_vault 兩層甩頁碼, 無頁碼 1,859 → 451)。S205 = 清 route-probe。
自動化 active: 5 源監察 (discover / freshness / served-url / 封面核對, 每週一) + Option A 自動入庫管道
(edb-knowledge-ops, 每日跑; 會自行 push main 並更新片段數)。開工時本地可能落後 origin/main —— tree 乾淨
+ 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

✅ 頁碼機制而家點運作 (S206 查實, 唔使再查): 頁碼唔係 DB 欄位 —— backend extractDominantPage()
  (searchChannelB.ts) 喺 chunk 文字度 read-time parse `=== Page N ===`。前端 mobile.js:519 / app.html:2503,3404
  見到 page 就出「頁 N ↗」+ #page=N (只限 PDF url)。自動管道 execute_ingest.py 一直用
  build_wiki_index.chunk_text_with_page_carry, 從無此問題; 缺口只喺人手 expand_vault 條路, 兩層已修。

✅ 網頁源指章機制 (S207 查實, 唔使再查): 網頁冇頁碼, 所以改為逐條 chunk 寫返自己嗰章嘅 URL —— 
  wiki_chunks.url 本身就係 per-chunk 欄位, 前端/後端/schema 完全冇改過。開關喺 source_registry.json
  嘅 section_urls (label → 絕對 URL, opt-in, 冇填 = 行為不變)。入庫前逐條 HEAD 驗 200, fail closed。
  ⚠️ g14 / g17 嘅 extract 唔准 --fetch: 佢哋係 S146 用一個已經唔存在嘅多頁 crawler 砌, 現行
  extract_html_text 只抓 url_primary 一頁, 一 refetch 就剷走其餘 section。
  ⚠️ 認段落標記一定要「先剷頁碼標記, 再認段落標記」兩步 (兩個相鄰頁碼標記會夾住正文扮成一個標記);
  同一次序喺 cleanChunkText 亦係 load-bearing。詳見 dev/vault/test_carry_rules.py 嘅斷言。

⚠️⚠️ 貫穿全局 (S199 用真金白銀學到): judge / synthesis 用嘅 model 唔係 code default。
  env.ts fallback 係 gpt-4.1-nano, 但 Render 實設 OPENAI_MODEL=gpt-4o-mini。/health 唔報 model。
  任何 judge/synthesis 量度, 引用做「生產行為」之前必須去 Render dashboard 確認。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先去 Render dashboard 確認 OPENAI_MODEL。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」搵已發生事件做對照組。
  3. 報一個數之前打開數字背後至少一個實例親眼睇。搜尋命中唔算證據。
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; 任何 synthesis-gate 改動一律 live before→after 對為準。
  6. judge 係 LLM、非決定性 → 任何 verdict 要重複 run (≥3) 先落結論。
  7. 入庫 ≠ 可達。SOURCE_SET / TOPIC_KEYWORDS / SPOTLIGHT / route expansion 四層每層都要實測。
  8. 交接寫低嘅選項框架本身可以係錯 —— 落手前先驗前提。S206 更進一步: 交接寫嘅兩個修法
     實測**兩個都修唔到佢自己指嘅 case**。動手前 live 重現 + 逐條算 exact cosine。
  9. 「應該冇」唔係「冇」。用戶答「應該一行都冇」係期望語氣, 追問一句先落結論。
  10. (S206 新增) 報一個 population 數字要即刻拆類: 邊部分修得到 / 修唔到 / 唔關事。淨拋總數,
      對方會用自己嘅 mental model 填補 (「1,859 條冇頁碼」曾被合理但錯誤咁連去 Channel A 退役)。
  11. (S206 新增) 用戶記得嘅嘢可以比 agent 嘅分析更中要害。Leonard 一句「出表格就指該頁數」
      把問題由「檢索排序」重新定位到「頁碼來源」, 慳返一輪唔必要嘅檢索改動。先驗佢講嘅前提, 唔好當閒聊。

🛠 常用指令:
  python3 dev/source/eval_retrieval.py --self-test ; --run --label X --out dev/source/eval_runs/<date>_X.json
  python3 dev/source/eval_retrieval.py --compare <before.json> <after.json>
  python3 dev/vault/expand_vault.py --fetch --force --sources <id>     # 重抽 (⚠️ table 源禁用, 見 registry notes)
  python3 dev/vault/expand_vault.py --embed --force --sources <id>     # 重入 Supabase (先 embed 後刪再入)
  python3 dev/vault/extract_table_rows.py --self-test ; --source <id> --dry-run
  python3 dev/source/judge_acceptance.py --self-test ; --plumbing-check
  python3 docs/qa/session_log_maintenance.py --check
  cd backend && npm run check && npm run build
  curl -s https://edb-knowledge.onrender.com/api/stats/usage

🔜 NEXT (Open Priorities ①–⑥ 詳見 handoff; §3 項目全部要 PLAN + Leonard go):
  ① 檢索「可見 ≠ 見到啱嗰段」—— **舊描述已被 S206 實測否定, 必須重出 PLAN**。詳見 handoff ①。
  ② 補 chunk-層儀器 (做 ① 之前)。eval harness 只記 source_id, 量唔到「見唔見到啱嗰段」。
  ③ GUIDELINES_REGISTRY 落後 102 個來源 + 加 registry-drift 監察 (Leonard 明確要求)。
  ④ 特殊學校編制表恢復 (等「資料對象 vs 問題對象」核對機制)。
  ⑤ 表格 / 註解 content_kind 分類 —— 同 ① 同一個根。
  ⑥ (S207 新開) per-chunk deep link 冇監察: 89 條 chunk 帶住自己嗰條子頁/附件 URL, 但
     check_served_urls.py 只讀 registry url_primary。加一段掃 section_urls 全部值 (得 16 條, 成本極低)。
  Backlog: 拆 backend channel-a 半邊 (S205 已解鎖前置); 時限性資料標示 + 第 6 監察; 公眾提交表單;
  範本 manifest 更新後開返 FEATURE_TABS.templates; 真亂碼未量度 (S207 已修 g20/g25 兩條 encoding 類,
  但 CID 類真亂碼仍未量度); 承 S203 (judge 對象移植機制 / Channel A Option 2 / PUBLISH_PAT / 總帳 /
  g24-sag 合併)。
  ⚠️ 收工待辦: dev/SESSION_LOG.md 已過 400 行門檻 (461 行 / 9 entry), session_log_maintenance.py
     --check = trigger=True, 未做歸檔。

ℹ️ 使用計數器 /api/stats/usage 現值 5, 五次全部係 S206 驗 UI 時瀏覽器發出 (API 呼叫全部帶 x-probe
  排除)。Leonard 明示不用理, 但讀第一個真實用量數字時要扣返。

Post-startup first action: 跑起手探針 —— served app.html PLATFORM_VERSION (應為 3.3.0) + Render /health
warm 455 (第一杯 curl 可能係冷啟動 warm=false, 要再叫一次) + Draft HEAD==origin/main + Supabase
count=exact (應為 17,473) + 無頁碼 chunk 數 (應為 451; 查法 text=not.like.*Page%20*%3D%3D%3D*) —— 然後
向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```
- **教訓（本 session 三條）:**
  1. **守門要證明佢會紅。** `--prove-assertions` 模式（用 no-op 實作跑同一批斷言，要求至少 N 條觸發）第一次就有價值：如果我淨係跑正常 self-test，兩個 regex 陷阱都會靜靜哋過。
  2. **放寬一個 regex 一定要即刻搵新 false positive。** 我為咗修「overlap 甩行錨」而拆走行錨，同一改動立刻製造咗 847 個幻影 label。放寬約束 = 開新 attack surface，唔可以只驗原本嗰個 case。
  3. **健康指標遇上 encoding bug 會反向。** 「至少 200 字」呢個守門一直收垃圾、擋好嘢，因為亂碼會撐大字元數。任何以長度 / 大小做健康判準嘅閘都有呢個盲點。

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-08-18 Session 206 — 頁碼指路修復：expand_vault 兩層甩頁碼，11 個源重入

- **ID:** Claude_20260818_1900
- **Summary:** 由 Open Priority ①（檢索「可見 ≠ 見到啱嗰段」）入手，live 重現後發現交接寫嘅兩個修法都修唔到佢自己指嘅 case。Leonard 一句「我記得已做，出表格就指該頁數」把問題重新定位：指路機制一早 ship 咗，壞嘅係頁碼來源。查落係 `expand_vault.py` 兩層都甩：抽 PDF 時冇寫 `=== Page N ===`、切 chunk 時冇 carry。兩層都修好，11 個源重入，全庫無頁碼 chunk 1,859 → 451。
- **① OP① 重現（唯讀，結論：交接框架錯）:** 用 registry notes 逐字記低嘅查詢「12班小學有幾多個學位教師」live 重現 —— 頭兩位係 forced footnote lead（0.5735 幼稚園當值教師 / 0.4715 職系改編），分數低過後面嘅 vault chunk；3–5 位係 `staff_est_pri` 表頭同腳註行（per-source quota = `max(2, ceil(8/3))` = 3）。用生產同一個 model 重算 exact cosine：正確嗰條「開辦 12 班…小學學位教師 5 名」= **0.6049，源內排 14/81**；源內最高 0.6537 係**零數據嘅表頭行**。故交接兩個修法**都唔掂**：擴窗 5→8 加入嘅係其他來源；改 spotlight 條件會插入嗰條表頭行。另實測 `detectQueryCategory('12班小學有幾多個學位教師')` = `null`，`'幾多班幾多老師'` = `null` —— S204 加嘅「編制」route 對自然口語唔 fire。
- **② 儀器適配性（communication rule 7）:** `eval_retrieval.py` 只記 `source_ids`/`scores`/`content_types`/`pages`，**冇 chunk 身分**，結構上量唔到「見唔見到啱嗰段」；34 條 eval query 亦冇一條編制查詢。故 eval 對本類改動只可做「冇誤傷」守門，做唔到勝負判準。已據此調整驗收設計。
- **③ 根因（兩層，同一支管道）:** `build_wiki_index.py` 一直有 `chunk_text_with_page_carry`（S119 CB-3），`execute_ingest.py:218` 亦一直用佢；但人手管道 `expand_vault.py` (a) `extract_pdf_text` 逐頁抽完用 `"\n".join()` 接埋，**從來冇寫過頁碼標記**；(b) `build_chunks_from_vault_file` 用自己嘅 `chunk_text()`，**冇 page carry**。即凡經 `expand_vault --fetch` 入嘅 PDF 全源零頁碼；有標記嘅源亦只有撞正標記嗰幾條 chunk 有頁。
- **Changed:**
  - `dev/vault/build_wiki_index.py` — 抽出 `carry_pages(chunks)` 純函數；`chunk_text_with_page_carry` 改為 `carry_pages(chunk_text(...))`，行為不變（commit `98dfbf8`）。
  - `dev/vault/expand_vault.py` — import 同一個 `carry_pages` 套喺自己 chunker 之後（`98dfbf8`）；`extract_pdf_text` 逐頁寫 `=== Page N ===`，並把「掃描 PDF」守門由總長度改為只數真文字（`5fa7343`）。
  - 11 個源重入 Supabase：`staff_est_pri`（`98dfbf8`）、`coa_pri_e`/`coa_ss_e`/`edbc00030`/`faq_edbc19011`/`edbc19011`/`ppt_grad_pri_policy`/`ppt_grad_pri_faq`/`psm_sgt`/`roles_functions_pri`（`5fa7343`）、`edbc12_2025_ph_pri`（`6ab966c`，先 `git mv` 對齊檔名）。
  - `dev/source/source_registry.json` — 11 個源 notes 補 S206 repage 記錄（本 closeout commit）。
- **Done / 數據:** 全庫無頁碼 chunk **1,859 → 451**（修 1,408 條）；全庫總數 17,472 → **17,473**。逐源核：11 個源全部 **0 條無頁碼**。`coa_pri_e` 509→494（121/121 頁）、`coa_ss_e` 700→707（197/197 頁）、`staff_est_pri` 4/81→81/81、`edbc12_2025_ph_pri` 10→13。
- **QC:**
  - `carry_pages` 不變式 4/4 PASS，並**故意寫壞實作證明斷言會響**（守門唔係永遠綠）。
  - **動 Supabase 之前**先驗 no-op：`edbc00030` 67/67、`g04` 7/7 重建 chunk id 同線上**完全相同** → 證明對無標記源零影響。
  - **零內容漂移閘**：9 個源逐個比對「今日重抽 vs git 內現存 extract」，正規化後要逐字相同先准入庫，9/9 過。
  - `extract_pdf_text` 兩面測（真 PDF 即場生成）：10 頁空白掃描 → 10 個標記且掃描警告**照響**；3 頁有字 → 3 個標記、唔響。
  - eval 對本 session 開工基線（`2026-08-18_s206_before.json` → `_after_edbc12.json`）：兩邊 **PASS=23 / FAIL=0 / errors=0**，33 SAME、1 RANK_SHIFT（`mpf`，即 `coa_pri_e` 因標記溝淡 cosine ~0.015 由 rank 4 → 7）、**0 blocking failure**。
  - `npm run check` exit 0、`npm run build` exit 0（本 session 零 backend TS 改動，作 row 37 要求嘅守門）。
  - **真 UI 實拍**：搜尋結果「參考來源」出「資助小學教學人員編制 · 3 個片段 · 頁 1, 3 ↗」，DOM 內錨為 `…Staff_est_pri_tc.pdf#page=1` / `#page=3`。live 亦見 `coa_ss_e` p.29、`coa_pri_e` p.100。
- **Evidence disposition:** 根因兩層 + 「規則共用、chunker 唔共用」嘅理由 → 已寫入 code 註釋同 commit message（唔會被重生）；11 個源 refresh 注意事項（尤其 `staff_est_pri` 唔准 `--fetch --force`）→ `source_registry.json` notes；逐步量度數字 → 本 entry；剩餘 451 條分類 → handoff `Current Baseline` + `Open Priorities`。
- **Sync:** DOC_SYNC row 37「Channel-B vault source backfill / page-carry into Supabase」命中並兌現：registry entry ✓、SOURCE_SETS/TOPIC_KEYWORDS parity N/A（零新源、零 route 改動）、handoff Current Baseline 已記 chunk 總數 + 帶標記數 ✓、本 log entry 帶 Gate 證據 ✓、CODEBASE_CONTEXT AI Maintenance Log ✓（無新 vault 目錄）。Gate1 markers==pages 全部對數；Gate2 post-count==insert（`coa_pri_e` del 509/ins 494 → 線上 494，其餘同理）。凍結合約零接觸（`_meta` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 / 158）；`PLATFORM_VERSION` 3.3.0 不變。
- **Pending:** 剩 451 條無頁碼，已分類（見 handoff）。其中真缺陷 139 條：95 條 HTML 源（**要指章唔係指頁**，Leonard 已同意方向）、44 條 footnote 冇錨（40 條 PDF 可人手補）。g14 另揪出三個同源問題（title 錯、段落標記外洩到用戶可見文字、網頁導覽雜訊入咗 chunk），已量：5 個 HTML 源 98 條之中 20 條殘留標記、17 條含雜訊。
- **Risks:**
  - 頁碼標記令 cosine 溝淡約 0.015–0.02，`coa_pri_e` 喺 `mpf` 查詢由 rank 4 跌到 7（仍在 top 8）。呢個代價全庫另外 15,613 條帶標記 chunk 一直付緊。
  - `edbc12_2025_ph_pri` 係**明示例外**：其舊 extract 早於現行抽取器，過唔到「逐字相同」閘（30 段差異）。改用「零內容增減」判準——字元多重集完全相同，差異全屬次序（頁碼/項目符號位置、兩個表格項對調）。已記入 commit message。
  - 使用計數器 `/api/stats/usage` 現為 5，**五次全部係本 session 驗 UI 時瀏覽器發出**（API 呼叫全部帶 `x-probe` 排除）。Leonard 明示不用理，但下次讀真實用量要扣返。
- **Log maintenance:** `docs/qa/session_log_maintenance.py --check` → `trigger=False line_trigger=False date_trigger=False`（line_count=372、entry_count=7）→ **no-op**。
- **教訓（本 session 三條）:**
  1. **交接寫低嘅修法可以指錯目標** —— S205 第 8 條紀律再中一次。今次唔止「選項框架錯」，係「兩個選項都修唔到佢自己指嘅 case」。落手前 live 重現 + 逐條算 exact cosine 先揭到。
  2. **用戶記得嘅嘢可以係對嘅，而且比我嘅分析更中要害** —— Leonard 一句「出表格就指該頁數」直接把問題由「檢索排序」重新定位到「頁碼來源」，慳返一輪唔必要嘅檢索改動。
  3. **報 population 數字要即刻拆類** —— 「1,859 條冇頁碼」令 Leonard 合理但錯誤地推論同 Channel A 退役有關；拆開之後 109 條先係 Channel A 鏡像、162 條其實已經 work。已存入 memory（`feedback_breakdown_before_scope`）。


<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->
