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

## 2026-09-03 Session 212 — 由文檔漂移開始，變成建一張品質檢查頁；期間自己整停咗生產搜尋

- **ID:** Claude_20260903（S212）。由「開工」起，Leonard 中途下多兩張單（狀態頁、Codex 覆檢五點）。
- **Summary:** 開場只係修三個小漂移，最後交付咗一張公開品質檢查頁 + 封版閘 + 兩支新監察，並修好一個 91% 不可讀嘅來源。過程中我自己整停咗生產搜尋約半小時（額度耗盡），呢件事已變成兩道會擋人嘅閘。
- **Changed:**
  - 新：`dev/source/qc_report.py`（21 項檢查）、`dev/source/check_registry_drift.py`、`dev/source/release_gate.json`、`qc_report.json`、`status-07cc7942c0.html`、`.github/workflows/qc_report.yml`、`dev/source/registry_drift.md`
  - 改：`backend/src/api/searchChannelB.ts`（新 `info_security` 路由 + 更正兩處 kgecg_2017 註釋）、`dev/source/eval_retrieval.py`（片段層）、`dev/source/eval_queries.json`（37→39）、`dev/source/route_regression.mjs`（33→46 + KNOWN_GAPS）、`dev/ocr_extract.py`（空白頁拒絕語）、`dev/source/source_registry.json`（phys 重抽紀錄）、`dev/PROJECT_INDEX.md`、`dev/DOC_SYNC_CHECKLIST.md`（+2 行）、七個片段數鏡像、判斷閘 model 文檔七處
  - Supabase：`phys_sss_2007_2015` 182（165 不可讀）→ 0 →（額度中斷）→ **187 條、亂碼 0**；全庫 17,597 → 17,602
- **Done:**
  - **判斷閘 model 文檔漂移**：S211 拆出 `JUDGE_MODEL` 後，所有部署者實際會看的地方仍寫住判斷閘跟 `OPENAI_MODEL`；補七處，並在 `JUDGE_PROMPT_FINDINGS.md` 的「READ THIS FIRST」橫幅上加 supersede 標示（該橫幅教人「判斷閘 model 由外部無法得知」，S211 之後已不成立）。
  - **Playbook pointer v1 → v2**。skill 的安裝步驟寫「見到 marker 就跳過」，正正係經驗庫自己 `idempotent-install-blocks-upgrade` 卡講嘅布林式冪等，照跟就永遠升唔到級；改用三態判斷，marker 加 `v2`。
  - **OP⑤ 資訊保安路由** —— 交接寫「加保安／雲端字眼落 `digital_education` regex」。先量度，發現照做會令目標 query 變差：該路由帶 21 個 DEBP/AI 詞嘅 expansion，接上去會把 query 本身蓋過（`g28` rank 0 → 消失；`pcpd` rank 0 → 消失）。改為獨立 `info_security` 路由、**不設 expansion**。刻意唔認裸「資訊保安」（S209 已定案該闊 query 返 SAG 係啱嘅）。
  - **OP① eval harness 片段層** —— 交接建議「斷言 chunk id 入唔入到前五」。查實 chunk id 係 text 嘅 md5，每次重切全源改晒，呢條斷言喺 S211 前一日寫好就會喺佢保護嘅修正上面紅。改用**文字簽名**（先 squeeze 空白，因 PDF 文字層會喺詞中間斷行）。兩條 `staffing_row_probe` 現場證綠。
  - **OP② 登記漂移監察** —— 原本嘅「273 對 177、落差 96」把四個方向互相抵消。查 registry 之後再修正一次：13 個 `stat_enrolment_YYYY` **唔係未登記**，父項用 `url_primary_pattern` + `years_extracted` 描述整個年度系列，真缺陷係三個 registry 監察都唔展開年份。UNMANAGED 14 → 1。
  - **品質檢查頁 + 封版閘**（Leonard 中途下單，對照通告系統嗰張）。門檻用基準值不用零，**等於基準報 WARN 不報 PASS**；未有 waiver 嘅 WARN 一律 NOT_MET；人手項目冇日期簽核係 NOT_MET 唔係「不存在」；`NOT_MEASURED` 等於 NOT_MET。出廠 7/15 FAIL，如實。
  - **`phys_sss_2007_2015` 重抽入庫**：165/182 不可讀 → 187 條、亂碼 0、頁碼 1–150 全覆蓋。eval 39/39 SAME、0 blocking。
- **本 session 自己犯咗而值得記低嘅錯：**
  1. **整停咗生產搜尋。** 先刪 182 條，之後先發現 OpenAI 額度已被同一 session 嘅 150 頁 OCR 耗盡 —— 該源變 0 條，而且**全站搜尋 429**（查詢要即時算 embedding）。直接成因：我喺單頁探針寫過「cost: trivial」，跳去 150 頁時**冇重新估算、冇查餘額**；次序亦錯（應先驗入得到再刪）。
  2. **一個負面結果差啲當咗證據。** 測 `kgecg_2017` 有冇搶格位，頭五條 query 全部 `kgecg=0`，睇落無害；但嗰五條全部路由去 `curriculum`，而 `kgecg_2017` 喺 S195 已被移出該 SOURCE_SET —— 係硬過濾擋住佢，唔係佢贏唔到。關掉過濾重測先見到真相（最多 6/8 格）。
  3. **兩個自己寫嘅檢查第一次跑就錯數**：事實計數器行錯結構、把完好嘅凍結契約報成破損；標題基準用咗「我見過嗰一個來源」嘅數而非全庫真數（116 vs 實際 658）。
  4. **封版閘喺公開頁面寫「8 項」而下面只列 6 個名**（截斷冇省略號）。係 Leonard 睇頁面睇出嚟，唔係任何 self-test 捉到。
  5. **commit 訊息用反引號中咗 shell substitution**，兩行被吃掉 —— 記憶入面本來就有呢條。
  6. **差啲把「普適氣體定律」搵唔到算落 OCR 頭上**；實測「普適」對「普通」分數只差 0.019，真兇係 `safety` 認裸「氣體」。
- **QC:** `qc_report --self-test` / `check_registry_drift --self-test` / `eval_retrieval --self-test` 全綠；`route_regression` 46/46；`tsc --noEmit` + `npm run build` exit 0；檢索 eval 兩對 before→after（`info_security` 路由：2 SET_LOST 全部係刻意收窄、掉走嘅係錯科目雜訊；phys 重入庫：39/39 SAME、0 blocking）；入庫後逐項核實片段數／亂碼／頁碼覆蓋／url。
- **Evidence disposition:** 工具已 indexed in `dev/PROJECT_INDEX.md`；兩條規則 promoted to `dev/DOC_SYNC_CHECKLIST.md`（row 53 品質檢查改動、row 54 重抽既有來源）；路由缺口 recorded in `route_regression.mjs` KNOWN_GAPS；其餘逐條拆解 kept as recent trace evidence。
- **Sync:** DOC_SYNC row 51（切 chunk 邏輯）、row 53、row 54 命中。七個鏡像 17,597 → 17,602 已同步（`live_display_sync` 讀真數）。
- **Pending:** 見 Open Priorities。
- **Log maintenance:** **觸發並已執行。** 我第一次寫「無觸發」係錯 —— 套用咗 managed-core 嘅門檻（N≥11／1500 行），但本 project 自己嘅 §4a、`SESSION_LOG.md` 檔頭註釋、同 `docs/qa/session_log_maintenance.py` 三者一致用 **400 行**，當時 450 行。跑 `--self-test`（5/5）後 `--apply`：450 → 90 行、5 → 2 個 entry、3 條（S208–S210）移入 `dev/archive/SESSION_LOG_2026_Q3.md`（只移不刪）。工具再報 `latest entry prompt block ok=False`，因為本 entry 漏咗 `### Next Session Handoff Prompt (Verbatim)` 區塊（AGENTS §1 startup 要讀嗰個），已補；`--check` 現時 trigger=False。`PROJECT_DECISIONS.md` 觸發條件 (c) 已兌現（多選項架構取捨：算術還原 vs OCR、折入既有路由 vs 獨立路由），收工時 append。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; the full table lives in
 INDEX_TABLE.md - grep it on trigger, open a card only on a hit, then log one usage line.)

Current state (S212, 2026-09-03): 平台 v3.3.2; Supabase 17,602 chunks; source_registry 279;
GUIDELINES_REGISTRY 177; 凍結合約 _meta 2.3.0 / facts 455 / guidelines.json 2.6.1 / 158 全部零接觸。
自動化 active: 6 源監察 + Option A 自動入庫管道 + 🆕 每日品質檢查 (qc_report.yml, 12:00 UTC, 會自行 push main)。
開工時本地大機會落後 origin/main —— tree 乾淨 + 0 本地 commit 先 git pull --ff-only; 有本地 commit 就 rebase。

🆕 開工第一件事改咗 (S212): 唔使再靠人手查全庫狀態，開呢一頁就見到全部
   https://policychecker.wongfu.net/status-07cc7942c0.html  (機器可讀: /qc_report.json)
   21 項檢查 + 封版閘。現時 overall=ERROR、閘 7/15 FAIL。
   本機重生: set -a && . backend/.env && set +a && python3 dev/source/qc_report.py --check

✅ S212 查實 (唔使再查):
  1. **重抽文字層救唔到 CID 亂碼。** phys_sss_2007_2015 嘅 PDF ToUnicode CMap 壞咗，pdftotext 抽出
     同舊 extract 逐字相同嘅亂碼。要用 dev/ocr_extract.py (S147 為此 failure mode 而建)。
  2. **亂碼算術還原係陷阱。** 三個固定偏移 (+0x3058 / +0x2D1E / +0x8E51) 可還原 98.4%、讀落通順,
     但交叉核對見到「二零一五年十一月」變成八個似是而非嘅漢字 —— 剩低嗰 1.6% 唔係明顯壞,
     係靜靜錯。用嚟做交叉核對可以, 唔可以當修法。
  3. **OCR 係草稿質素, 錯法係術語級誤字。** 逐頁對照原圖: 普適→普通、查證→查察、貫徹→實徵、
     樂意→樂於, 約每頁 1-2 個 (≈0.5%)。引用具體字眼前對回原文。
  4. **judge 同 synthesis 用兩個 model** (OPENAI_MODEL 合成 / JUDGE_MODEL 判斷閘, 後者程式預設
     gpt-4.1-mini)。S211 拆咗但七處文檔冇跟, S212 已補齊。
  5. **/health 報 ok:true 唔代表搜尋活。** 佢只驗 Channel A 快取。要驗真嘅睇
     qc_report 嘅 SEARCH_PIPELINE_LIVE, 或者直接打一條查詢。

🧭 紀律 (真金白銀學返嚟, 仍然生效):
  1. 判斷 judge/synthesis 行為前, 先確認係邊個 model 變數。
  2. negative result 落結論前先問「如果目標訊號存在, 呢個工具顯唔顯示到?」
     (S212 再中: 測 kgecg_2017 有冇搶格位, 頭五條 query 全部 0, 但嗰五條全部路由走咗,
      係硬過濾擋住, 唔係佢贏唔到。關掉過濾先見到真相。)
  3. 報一個數之前打開數字背後至少一個實例親眼睇。
     (S212: 數字密度偵測器返 701 條, 啱啱好落喺 S204 估算範圍, 但逐條讀係四樣唔同嘅嘢。)
  4. 剷任何嘢前分清「有可引用替代品」同「唯一來源」。
  5. 任何檢索改動一律 eval before→after 對為準; synthesis-gate 改動一律 live before→after。
  6. judge 係 LLM、非決定性 → verdict 要重複 run (≥3); 更好係搵個確定性量度。
  7. 入庫 ≠ 可達; 可達 ≠ 贏得到; 贏得到 ≠ 答得啱。
  8. 交接寫低嘅選項框架本身可以係錯。(S212 三次: 「加保安字眼落 digital_education」會令目標
     query 變差; 「斷言 chunk id」會喺自己嘅修正上面紅; 「14 個 unmanaged 要分流」其實係
     一個 series 父項數咗 14 次。)
  9. 「應該冇」唔係「冇」。10. 報 population 數字要即刻拆類。
  11. **守門要證明佢會紅。** (S212 代價示範: /health 永遠唔會紅, 結果全站搜尋死咗半個鐘冇人知。)
  12. 交付一個檔案之前 ls 實證佢存在。 13. 揀嘅 phrasing 決定得出嘅答案。
  14. 任何要人做決定嘅表面都要有出口; 只入唔出嘅清單一定變牆紙。
  15. 改完一樣嘢, grep 該功能自己嘅字眼掃全站散文、meta、分享卡、README。
  16. 改 mobile.css / mobile.js 必須同時推 PLATFORM_VERSION。
  17. **S212 新增: 刪之前先驗「入得到」。** 先刪 182 條、後發現額度耗盡 = 該源 0 條 + 全站 429。
      任何會大量呼叫外部 API 嘅步驟 (OCR / 批次 embedding) 事前要估算並講出用量,
      唔可以把單頁探針嘅成本當成全份嘅成本。見 DOC_SYNC row 54。
  18. **S212 新增: 呈現層要有人眼睇。** 封版閘喺公開頁寫「8 項」而下面只列 6 個名 (截斷冇省略號),
      係 Leonard 睇頁面睇出嚟, 冇任何 self-test 捉到。self-test 驗邏輯, 唔驗呈現。

NEXT (見 Open Priorities 全文, 已重生為 8 項):
  ① 八個 standing WARN 要 Leonard 批 waiver 或當要修 + 六項人手檢查未簽核 (封版閘現時因此 FAIL)。
  ② kgecg_2017 108 條已證可刪, 但 cb3_deprecate_stale.py 被 auto mode 分類器擋住, 要 Leonard 跑。
  ③ ⚠️ eng_sss_guide_2021/g33 同 arts_kla_guide_2017/g37 唔係單純重複 —— 兩個 g-series 標題
     掛錯文件 (2007 英文指引、2002 藝術指引根本唔喺庫入面), 唔可以當刪重複處理。
  ④ TOPIC_KEYWORDS.safety 認裸「氣體」, 偷走氣體相關嘅課程查詢 (已入 KNOWN_GAPS)。
  ⑤ 特殊學校編制表恢復 —— 注意佢仍然喺 SOURCE_SETS.staffing 入面, 要先移走。
  ⑥ content_kind 框架要重新定義, 唔好再用分類器路線。
  ⑦ 658 條片段以內部代號做標題。 ⑧ 六個現有監察未接入狀態頁。

⚠️ 未做而應該知: coa_pri_e / coa_ss_e 亦載編制條款, 未逐一檢查有無同類「答錯班數」問題。
```

## 2026-09-01 Session 211 — 一條答唔到嘅查詢，拆出四層獨立缺陷

- **ID:** Claude_20260901（S211）。跨午夜：2026-08-31 20:58 → 2026-09-01 10:12（本機 BST）。
- **Summary:** 由「收起通告分析卡」開始，中途 Leonard 貼咗一條真實查詢「只修讀中學師資資格是否可以在小學任常額職位」同 Google AI Overview 對照。平台拒答。拆落去發現係四層獨立缺陷疊埋，而每一層「最順理成章」嘅修法都被實測否決。
- **Changed:** `app.html` / `index.html` / `q.html` / `t-purchase.html` / `mobile.js` / `mobile.css` / `README.md` / `K1_API_SPEC.md` / 三個 JSON 鏡像；`backend/src/api/searchChannelB.ts` / `backend/src/lib/wikiRepository.ts` / `backend/src/server.ts` / `backend/src/config/env.ts`；`dev/vault/expand_vault.py`；`dev/source/source_registry.json`；新增 `dev/source/route_regression.mjs` / `vault_lead_delta.mjs` / `cache_drift.mjs`；`dev/source/JUDGE_PROMPT_FINDINGS.md` §5–§7；`dev/DOC_SYNC_CHECKLIST.md` row「Tab withdraw / restore」重整。Supabase `staff_est_pri` 81 → 85（全庫 17,593 → 17,597）。
- **Done:**
  - 前端五項，平台 v3.3.0 → v3.3.2（收卡 / 平板版面錯位 / 統計列 / 三處寫死數字 / 五句散文）。
  - `/health` 加 `commit` + `started_at`。
  - 判斷閘改用獨立模型 `gpt-4.1-mini`（`JUDGE_MODEL`，程式預設）。
  - 檢索四層：`teacher_qualification` 路由、bypass 改讀 `results[forcedLeads]`、合成器字數由目標改上限、`chunk_overlap` 覆寫 ＋ `searchEstablishmentRows()` 詞彙層 overlay。
  - 內容準確性：編制答案預設只出全日制（Leonard 指出資助及官立小學已無半日制）。
  - 防漂移：`app.html` 分頁開關註釋第 8、9 項；DOC_SYNC row 重整。
- **QC:** `tsc --noEmit` / `npm run build` 全部 exit 0；`route_regression.mjs` 33/33 PASS，並以改前版本跑同一套作 baseline，證實無舊 query 改路由；`vault_lead_delta.mjs` 確定性證實 bypass 改動只影響 3 個 case 且全部 `want=能`、21 個 `want=否` 一個都無受影響；判斷閘換 model 對凍結集主集 31/33 打平、無新增 false answer、連 bare-noun 33/35 對 31/35；四個過度觸發 case 實測歸零；每次 push 後以 `/health` 嘅 `commit` 確認部署落地再驗真站。 **檢索 eval before→after 已跑**（DOC_SYNC row 43／51 要求）：對 `2026-08-26_s210_after_leaflet.json`，`2026-09-01_s211_after.json` 為 **PASS=25 / FAIL=0 / errors=0（與基線一致）、SAME 36 / 37、blocking failures 0**。唯一非 SAME 係 `sef` 一條 DISPLACED：尾位（第 8）嘅 `debp_blueprint` 被 `edbc015_2026` 擠走，而後者係 S210 之後 Option A 管道自動入庫嘅通函，**與本 session 四層改動無關**——正正係 S210 建立 DISPLACED 分類要吸收嘅情況。
- **本 session 自己犯咗而值得記低嘅錯：**
  1. **用 exact substring 搵原文，撞正 PDF 換行**（「新 入職教師」中間有換行），一度報「冇入 top-80」，實情係第 1 位。負面結果落結論前要問儀器顯唔顯示到。
  2. **分頁攞 81 行寫成 `limit=60`**，兩次請求其中一次回 error object，而我 `rows += b` 把 dict 嘅 key 當成 row 加咗入去，備份檔一度有 85 個元素。加咗 assert 逐項核 `isinstance(dict)` 同對權威 `count=exact` 先重做。
  3. **一度判斷「Render 部署失敗」並寫成報告請 Leonard 介入**，實情只係慢，而它喺報告寫到一半時上線。直接成因係服務無 version endpoint——已補。
  4. **兩次 full-pipeline run 分別喺 GN02 同 GN03 見到 false answer，一度當成回歸**，實情兩個 case 都唔喺改動影響範圍內，純 LLM 雜訊。改為寫確定性量度腳本先落結論。
  5. **「重新切片就係修法」講早咗一步**：做完發現答案變成由鄰近班數內插，隨即逐 byte 還原生產資料，確認詞彙層 overlay 之後先再重入。
  6. **`searchEstablishmentRows` 同 `staffing` 路由第一版都過度觸發**：「小一派位第 1 班點分」被塞八段編制表。實測到先收窄。
- **Evidence disposition:** 檢索／判斷閘嘅可重用結論已 promoted 入 `dev/source/JUDGE_PROMPT_FINDINGS.md` §5–§7（判斷提示唔係槓桿、凍結 cache 已漂移、班數查詢真兇）；三個量度工具已 indexed in `dev/PROJECT_INDEX.md`；架構取捨已 promoted to `dev/PROJECT_DECISIONS.md`；其餘逐條 compare 拆解同自己犯嘅錯 kept as recent trace evidence。
- **Sync:** DOC_SYNC row 37（vault source backfill）、row 43（eval harness）、row 51（切 chunk 邏輯）三行命中；「Tab withdraw / restore」一行重整為 A/B/C/D 四組並加入 grep 驗證步驟。公開片段數七個鏡像已同步 17,593 → 17,597。
- **Pending:** 見 Open Priorities。⚠️ `coa_pri_e` / `coa_ss_e` 亦載編制條款，未逐一檢查有無同類「答錯班數」問題。
- **Log maintenance:** 無觸發。本檔 4 個 session entry（N=4 < 11）、行數未逾 1500；`PROJECT_DECISIONS.md` 觸發條件 (c)（多選項架構取捨連理由）已兌現，本 session 已 append。
