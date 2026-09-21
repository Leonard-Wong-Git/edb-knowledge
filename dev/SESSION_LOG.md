# Session Log
<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

<!-- ack:section:session-log-preamble -->

> **Handoff role**: This log is the trace-back / audit trail layer. Handoff capability rests on `dev/SESSION_HANDOFF.md`. The next AI session can continue by reading `AGENTS.md` + `dev/SESSION_HANDOFF.md` + `dev/PROJECT_INDEX.md` + needed rule packs; reading this log is not required for continuity. Each closeout must run the maintenance trigger check per `AGENTS.md` `## Closeout And Handoff` step 11 (R-010 SESSION_LOG handoff-role discipline): N=1–3 keep full, N=4–10 may short-index after absorbed-source check when triggered, N=11+ archive into `dev/SESSION_LOG_archive/`.

Add new session entries at the top. Record what actually happened in the session; do not copy old completed work forward as new work.

This log carries recent evidence, not current state. Put the current objective, next action, risks, and workspace identity in `dev/SESSION_HANDOFF.md`.

Keep recent entries concise. If older entries no longer affect the next action and the maintenance trigger check says cleanup is due, reduce them to short dated indexes that point to the durable source of truth. Archive long error output, validation detail, or research trails only when triggered; do not create an archive directory by default.

Before closeout, record whether older log detail was kept, summarized, or archived, and whether the maintenance trigger check was no-op, triggered, or backstop-driven. Do not remove validation evidence or unresolved risks. The full opening message never belongs in this log.

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
- **Log maintenance:** <trigger check result; full maintenance action if triggered, otherwise no-op reason>
- **Opening-message mirror:** <regenerated and verified / blocked; full text omitted by design>
<!-- ack:log-entry:end -->
````

---

<!-- ack:log-entry:start -->

## 2026-09-20 Session 229 — 那個門檻不是被展開詞抬高了，是由頭到尾校錯了尺

> ⚠️ **本條由 S230（2026-09-21）補寫。** S229 當日改了 `dev/SESSION_HANDOFF.md` 與 `dev/PROJECT_INDEX.md`、建了兩支探針，但**從未收工**：沒有本條目、沒有 `State Reconciliation Check` 條目、`Last Session Record` 仍停在 S228、開場白區塊與 `START_NEXT_SESSION_PROMPT.txt` 亦仍是 S228 版本，四項改動全部未 commit。本條的事實來源是 S229 留下的實物（交接檔 `## Open Priorities` ② 的 S229 段落、`dev/PROJECT_INDEX.md` 兩列新登記、`backend/scripts/_s229_{scaleOffset,leadDetail}.ts`），**不是憑記憶重構**；S229 沒有把任何一次 run 的原始輸出存檔，所以下列數字在本條寫成時只有交接檔一個來源，S230 已重跑 `_s229_scaleOffset.ts` 獨立覆核（結果見 S230 條）。

- **ID:** `Claude_20260920_xxxx` — S229（實際時分不可考，S229 未記）
- **Summary:** 追 S228 交下來的 OP②(c)「重校 `VAULT_LEAD_SCORE` 0.70」，結果把這條路本身否決了 —— 0.70 不是被展開詞抬高了要調回低，而是**校準尺與應用尺根本是兩把尺**：定這個數的 `dev/source/judge_probe.py` embed 裸查詢兼打全庫，而 0.70 套用在「展開後 ＋ 路由收窄」的 `mainSearchLead.score` 上。185 條 gold 之中 97 條是路由題，兩尺不同。
- **Changed:** `backend/scripts/_s229_scaleOffset.ts`（新）· `backend/scripts/_s229_leadDetail.ts`（新）· `dev/SESSION_HANDOFF.md`（`## Open Priorities` ② 加入 S229 段落並更正 S228 那條硬紀律的適用範圍）· `dev/PROJECT_INDEX.md`（兩列新登記）。**四項皆未 commit，由 S230 接手。**
- **Done:**
  - **三把尺同批量度**（`_s229_scaleOffset.ts`，用生產 `searchChannelB`、零重寫、`FEATURE_ROUTE_FIRST_SEARCH=1`）：**A 裸＋全庫**（＝校準尺）／**B 裸＋路由**／**C 展開＋路由**（＝應用尺），對象是 `judge_probe.py` 當初定門檻那 24 條校準 query。**儀器自我驗證通過**：A 重現 S195 原數（CLASS_B 上限 0.6321 對 0.632、CLASS_C 下限 0.6241 對 0.624）。
  - **歸因分離**：路由本身**不抬分**（A→B 為 0 至 −0.067），抬分的是展開（B→C 最多 **+0.3226**）。兩個分佈的重疊由 **0.0080 擴大到 0.0817，大十倍**；CLASS_B 敵意題在應用尺上有 **2 條 ≥ 0.70**，即合成閘被跳過。
  - **逐條開窗核實**（`_s229_leadDetail.ts`，判 bypass 有無真的觸發，因為 `scaleOffset` 量的是窗內最高分 vault_extract 而閘測的是 `mainSearchLead`，過 0.70 是必要非充分條件）：**「校巴司機最低工資係幾多」@ 0.7098 是真缺口** —— 窗內四個來源共 31 片段，`工資`／`薪` 命中 0，全庫 `最低工資` 只有 10 條且全部是經濟／通識科課程文件，判官被跳過而合成器手上零工資內容，正是 0.70 當初要擋的 S177 那一類。**「老師病假連續請幾耐先要交醫生紙」@ 0.7003 則是探針標錯** —— `g04` 原文有「常額教師如申請病假超逾兩天，必須出示有效的醫生證明書」，領先那一片就是答案片段，bypass 觸發是正確行為；`judge_probe.py` 把它列入 CLASS_B（語料無答案）是錯的。
  - **更正 S228 立的硬紀律的適用範圍**：只有 `VAULT_LEAD_SCORE` 與 `min_score` 吃「展開後＋路由收窄」向量；`SPOTLIGHT_LEAD_SCORE` 與兩個 `FOOTNOTE_*` 門檻看的是裸查詢向量（`searchChannelB.ts:1756` 的 `rawVec`），**任何展開側改動都動不到它們**。證據：S228 十個 arm 共 1,667 筆 before／after 記錄，裸查詢字串兩側逐筆同一個，0 筆例外。
- **Fix Record:**
  - **Problem:** S228 交下來的 OP②(c) 叫下一節「重校 0.70」。**Root Cause:** S228 從分數分佈推斷門檻被展開詞抬高，但沒有查這個數當初是用哪把尺校出來的。**Fix:** 不重校 —— 改為換訊號（把閘放回它被校準的那把尺）。**Verification:** 三把尺實測，A 重現 S195 原數，路由不抬分、展開抬分，兩分佈在應用尺上重疊大十倍；共用經驗庫 `self-authored-probe-false-confidence` 卡尾段寫明「兩分佈重疊時調 threshold 係死路，要換訊號或換判斷器」。
- **QC:** `_s229_scaleOffset.ts` 的自我驗證（A 尺重現 S195 兩個邊界值）· `_s229_leadDetail.ts` 逐條開窗覆核兩條過線題。**未跑** `npm run check`／`route_regression`（本節零生產碼改動，但亦未記錄此判斷）。
- **Evidence disposition:** ⚠️ **原始 run 輸出未存檔** —— S229 的數字當時只存在於交接檔 `## Open Priorities` ② 的散文內。S230 已重跑並把 artifact 存入 `dev/source/eval_runs/`，此後以該檔為準。兩支探針的存在理由與用法已登記在 `dev/PROJECT_INDEX.md`。
- **Sync:** ⚠️ **S229 未做** —— `dev/DOC_SYNC_REGISTRY.md` 無 S229 列，`dev/DOC_SYNC_CHECKLIST.md`「Synthesis 前置閘改動」row 要求的 `judge_probe.py` 驗收亦未跑（S229 自己指出該工具現況跑出來的是校準尺的數，要先修）。由 S230 補。
- **Pending:** 換訊號的具體做法（S229 提出、未實作、未量）：`rawVec` 已為每條查詢 embed 好，把 vault 閘改為測「領先片段對裸查詢向量的 cosine」，即把閘放回被校準的那把尺上。屬 `dev/DOC_SYNC_CHECKLIST.md` 自己一個 row，要先定案再量 before→after。
- **Risks:** 本節零生產碼改動、零 Supabase 寫入、零部署。真正的風險是它留下的**半落地狀態**：交接檔內容已更新而敘事層（Last Session Record／開場白／鏡像檔）仍是 S228，下一個 agent 會讀到互相矛盾的兩段。已由 S230 收乾。
- **Log maintenance:** 補寫，不觸發維護檢查（由 S230 在本節收工時一併執行）。
- **Opening-message mirror:** ⚠️ S229 未產生；S230 收工時重新產生。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-16 Session 228 — 把三次逐條醫過的機制量了一次；兩層檢索都改善，答案層卻變差，原因是分數尺被動了

- **ID:** `Claude_20260916_1610` — S228
- **Summary:** 將「展開詞不論查詢多短都原文照貼」變成三個預設關閉的旗標並跑出劑量曲線（最佳配置片段層 **+7**、零退步、重跑噪音 0），但**兩個配置的答案層判官都判 `NO_MEASURABLE_GAIN`**（合併 +3.5、balance 單獨 +1.5／門檻 8），因此**本節零檢索改動出貨**；追出兩個並存的解釋（絕對分數閘吃掉得益／這個量級堆不出 8 分）並各自記下支持與削弱它的證據；同節修好 OP⑩ 路由並推翻交接檔對它的診斷，量出 cross-encoder 的上限（最多救 42 條、65 條救不到），並清掉 Backlog ⑨。
- **Changed:** `backend/src/api/searchChannelB.ts`（三個 `EXPANSION_*` 旗標 ＋ `repeatsForBalance()` ＋ `positiveIntFromEnv()` 去重；`TOPIC_KEYWORDS.kg_admin` 提前並加兩個 token；`SOURCE_SETS.kg_admin` 加 `edbcm144_2026`）· `backend/tsconfig.scripts.json`（新）· `backend/package.json`（`check` 串兩個 project ＋ `check:scripts`）· `backend/scripts/_s226_knobAB.ts`（`EXPANSION_*` 不變式 ＋ 逐條記低 embed 字串 ＋ `knob_changed_embedded_input`）· `backend/scripts/_s228_rerankCeiling.ts`（新）· `backend/scripts/groundedSynthesis{Probe,Regression}.ts`（型別）· `dev/_s228_ceiling_report.py`（新）· `dev/source/route_regression.mjs`（9 條新案例 ＋ 1 條 `SOURCE_MEMBERSHIP`）· `dev/DOC_SYNC_CHECKLIST.md`（新 row）· `dev/DOC_SYNC_REGISTRY.md` · `dev/PROJECT_INDEX.md` · `dev/SESSION_HANDOFF.md` · `dev/source/eval_runs/2026-09-16_s228*`（新，六個 arm ＋ 合成 ＋ 判官三份 ＋ 上限一份）
- **Done:**
  - **機制旗標化**：`EXPANSION_MIN_QUERY_CHARS`（短於 N 個碼位不貼展開詞）、`EXPANSION_BALANCE`（保留展開詞，重複用戶查詢令它佔至少 φ 字數比例）、`EXPANSION_REPEAT_CAP`（預設 8）。三者未設 = 改動前逐位元組相同，解析契約照搬 `capFromEnv`（打錯字必須被忽略，不得靜靜放寬）。
  - **劑量曲線（六個 arm × 185 題 × 生產配置）**：`floor` 6/8/10 → 片段層 +1/+5/+5（10 開始出現 1 條退步）；`balance` .35/.5 → +2/+4；合併 `floor=8`＋`balance=.5` → **+7、零退步**。**噪音底線量了七次**：同一配置七個獨立 before 側，片段層 `chunk_PASS` 全部 59、來源層 123 六次 122 一次。
  - **答案層（兩個配置都量了，都判不出貨）**：合併配置 81 條、154 次呼叫 → `net_after` **+3.5**（judged 76、`always_first` 1、`always_second` 1、剔除 22）；`balance` 單獨 79 條、145 次呼叫 → `net_after` **+1.5**（judged 72、`always_first` 1、`always_second` 0、剔除 15、TIE 43）。門檻 8 → 兩者皆 `NO_MEASURABLE_GAIN`。判官因 30k TPM 上限中止兩次（第 66 條、第 16 條），餘數各自補跑，合共四段。棄權：合併 8→15、balance 8→11。
  - **OP⑩**：交接檔記載的病因（展開詞壓低答案分數）**實測不成立** —— 展開全關掉答案段落仍入不到窗。真因是 `edbcm144_2026` 只靠 spotlight overlay 露面而 `SPOTLIGHT_MAX_LEADS = 1`。修法：`kg_admin` 由尾二提前到 `kg_admission` 之後、補「幼稚園＋津貼／搬遷」、`edbcm144_2026` 入 set。
  - **cross-encoder 成本評估**：新工具擷取每題 top_8 與 top_40 兩個窗（後者正是現有 over-fetch），判分交回 Python 共用判分器。166 條有簽名者：已入窗 59 · 重排最多救 42 · 救不到 65（39%）。
  - **Backlog ⑨**：`backend/scripts/*.ts` 首次納入型別閘，順帶修好四個潛伏錯。
- **Fix Record:**
  - **Problem:** 六個 arm 全部報 `arm-noop`，看似「機制沒生效」。**Root Cause:** harness 以 last-write-wins 記錄送去 embed 的字串，而 `searchChannelB` 每側 embed 兩次（展開後查詢 ＋ spotlight 用的裸查詢）。**Fix:** 逐條記錄全部字串，並移植回 `_s226_knobAB.ts`。**Verification:** 重跑後畫面顯示 `幼稚園搬遷津貼` 被重複 6 次再接展開詞；`knob_changed_embedded_input` 81/81。
  - **Problem:** 交接檔把 OP⑩ 記為展開詞問題。**Root Cause:** 原分析用的是舊路由下的全域窗第 8 名作對照，而那個窗當時塞滿無關的 SAG 段落。**Fix:** 逐條量該通函全部 8 片段對查詢的餘弦。**Verification:** 答案段落在自己文件內排第 6／第 5，而配額是 3 —— 屬配額家族，已重新歸入 OP④。
  - **Problem:** 兩層檢索指標都報喜，答案層卻多了 7 次棄權。**Root Cause:** `floor` 令最高分中位跌 0.1296，題目跌穿 `VAULT_LEAD_SCORE` 0.70 而不再 bypass 合成閘。**Fix:** 未修 —— 這是「要不要出貨」的證據，不是 bug。**Verification:** 拆開兩個旗標量，`floor` 那 26 條中位 −0.1296、`balance` 那 71 條中位 ±0.0000；跌穿 0.60 的條數 `floor` 9/17/27 vs `balance` 0/0。
- **QC:** `npm run check` 0（現含 `tsconfig.scripts.json`）· `npm run build` 0 · `route_regression` **63/63** ＋ 2 條 `SOURCE_MEMBERSHIP`（改碼前紅測準確紅 3 條）· `route_blast_radius HEAD` 185 條只 2 條改路由 · `regression:grounded` 48/48 · `_s226_knobAB.ts` 開跑前兩行 `invariant OK` · `_s228_rerankCeiling --self-test` 4 條 · `_s228_ceiling_report --self-test` 7 條 · scripts 型別閘紅測準確轉紅 1 條 · 判官先校準（4/7，位置偏誤 0）才使用。
- **Evidence disposition:** 六個 arm 的原始擷取與判分、合成 A/B、判官三份 artifact、上限探針一份，全部保留為近期證據（下一節會引用）；劑量曲線、噪音底線、門檻跌穿表與上限數字已抄入 `dev/SESSION_HANDOFF.md` `## Validation / QC`；「動搖絕對分數必須連同下游門檻一起重新校」已升為 `## Open Priorities` ② 的硬紀律；「harness 必須逐條記低送去 embed 的字串」已升為 `dev/DOC_SYNC_CHECKLIST.md` 新 row 第 ④ 條。煙霧測試與等價性驗證的臨時 artifact 已刪。
- **Sync:** `dev/DOC_SYNC_CHECKLIST.md` 新增「查詢展開機制改動」row（依 anti-pattern guard 先補 row 再做）· `dev/DOC_SYNC_REGISTRY.md` 已記本節十列狀態 · `dev/PROJECT_INDEX.md` Local QC Commands 已更新 · `dev/CODEBASE_CONTEXT.md` **不需改**（技術棧／目錄／build 指令／外部服務／Key Decisions 均無變；新增的 `tsconfig.scripts.json` 屬 `npm run check` 的內部串接，已記在 PROJECT_INDEX）。
- **Pending:** 先決定信哪個讀法再動手 —— (i) 兩個絕對分數閘吃掉得益 → 重校門檻（OP②(c)）；(ii) 這個量級堆不出 8 分淨值 → 重新審視判官門檻是否適用。**在兩者之一有結論之前不要再跑展開側 A/B。**
- **Risks:** 三個 `EXPANSION_*` 旗標生產一律未設，未設 = 現狀，所以合併本身不改變生產行為；`kg_admin` 路由改動**不是旗標、合併後會即時生效**，影響面已量（185 條只 2 條改路由、off-gold 只影響含「幼稚園」的查詢）。
- **Log maintenance:** 觸發檢查 —— 主 log 目前 N < 11 條且未逾 1500 行，`## Confirmed Decisions` 類章節未達 30 條，本節無跨節累積模式需要即時寫入 `PROJECT_DECISIONS.md`；距離上次全面維護未滿 10 次收工。**結論：no-op**，不做長期維護。
- **Opening-message mirror:** 已由 `dev/SESSION_HANDOFF.md` 的 fenced 區塊重新產生 `START_NEXT_SESSION_PROMPT.txt`，並讀回逐字核對相同（76 行）。⚠️ **順帶修好 S227 的反向操作**：S227 只更新了鏡像檔、沒回寫交接檔區塊，令該區塊停在 S226 內容，而交接檔自己寫明「兩者不符以本區塊為準」—— 本節先由鏡像回寫，再按收工契約第 9 步的正常方向重新產生。
- **PR:** [#22](https://github.com/Leonard-Wong-Git/edb-knowledge/pull/22)（分支 `s228/expansion-knobs`，rebase 落 `8b630e3` 之上 —— 該 commit 是排程監察 `qc_report` 在本節中途自行推的帳本更新，零 `backend/` 改動）。**未合併**：合併會觸發 Render auto-deploy 並令 `kg_admin` 路由改動即時生效，依交接檔「`gh pr merge` 在 Leonard 明示授權下可執行」，等 Leonard 拍板。
<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-16 Session 227 — 建了一把答案層的尺，第一件事是用它否決一個候選；第二件是它照出路由只醫好一半

- **ID:** `Claude_20260916_1520` — S227
- **Summary:** 交付 OP① 的答案層 rubric 判官，用它判定 `FEATURE_LEXICAL_RERANK` **不出貨**（38 題 net −1／門檻 8）；再由一條 gold 題追出 S226 的 `評核` 路由只醫好一半（路由改了、展開詞沒改），拆出 `staff_appraisal` 路由並**已上生產核實**。
- **Changed:** `backend/src/api/searchChannelB.ts`（`TOPIC_KEYWORDS.staff_appraisal` ＋ `SOURCE_SETS.staff_appraisal`，並由 `hr_admin` 移走 S226 那五個詞）· `backend/scripts/_s227_rubricJudge.ts`（新）· `dev/source/route_blast_radius.mjs`（新）· `dev/source/route_regression.mjs`（三條改道 ＋ 四條對照組）· `dev/SESSION_HANDOFF.md` · `dev/DOC_SYNC_CHECKLIST.md`（兩個新 row）· `dev/source/eval_runs/2026-09-15_s227{cal,cal2,cal3,full}_rubric_judge.json`（新）
- **Done:**
  - **答案層判官（OP①）**：pairwise、每題兩個次序各判一次、判讀門檻寫死在碼內。67 條 self-test、**七次紅測**全部準確轉紅且逐次 `shasum` 還原核對。
  - **判官校準三輪，模型才是變數**：`gpt-4.1-mini` 原版 14 次判決 **11 次揀先出現那一個**、TIE 零次（表面 3/7，實為位置偏誤）；加 per-answer 評分後偏誤翻到第二位、跌至 1/7；換 `gpt-4.1` 後 `always_first`／`always_second`／`INCONSISTENT` **全部歸零**，5/7。
  - **`FEATURE_LEXICAL_RERANK` 判定不出貨**：38 題、60 次呼叫，兩側皆棄權 8（與 S226 記載對上）· TIE 17 · 偏 before 7 · 偏 after 5 · **net −1**。穩健性先算才下結論：6 條須人手覆核題全算 after 完勝也只到 +5。
  - **`staff_appraisal` 路由拆出**：成因是 `hr_admin` 的假期展開詞把「教師評核」變成假期查詢，實測把答案段落由**第 1 推到第 9**（裸 0.5884／加展開 0.4881／第 8 名 0.6088）。照 `staffing` 先例拆出且**不設展開詞**。
  - **PR #20 已合併（`7be4404`）並已部署核實**：生產打「教師評核」，答案段落（SAG §7.7 p.208）**入窗第 5**，八格全部考績來源、一條假期都沒有；生產分數與本機預測逐位吻合。
  - **新工具 `route_blast_radius.mjs`**：改路由時掃全部 185 條 gold query 對照任一 git ref，補上 `route_regression.mjs`（54 條人手案例）覆蓋不到的範圍。8 條 self-test ＋ 一次紅測。
- **Fix Record:**
  - **Problem:** 「教師評核」在生產回傳八條假期段落。**Root Cause:** S226 把五個詞加進 `hr_admin` 修好了路由，但沒處理該路由的 `QUERY_EXPANSIONS`（假期詞彙），排序向量因而變成假期查詢。**Fix:** 拆 `staff_appraisal` 獨立路由、不設展開。**Verification:** 生產實測答案段落入窗第 5。
  - **Problem:** 第一次量 after 時窗完全不同（`sag_2025_11` 整份消失、只回傳 6 條）。**Root Cause:** `_s226_captureQueryVec.ts` **不設 `FEATURE_ROUTE_FIRST_SEARCH`**，量到的是生產不執行的配置。**Fix:** 由外面設該變數重量；已寫入 `dev/DOC_SYNC_CHECKLIST.md` 新 row。**Verification:** 重量後與生產逐位吻合。
  - **Problem:** 以為找到 ② 的第三條方向（查詢展開拉偏）。**Root Cause:** 由一個案例推論通例。**Fix:** 量 63 題 —— 37 條有展開者，展開幫 29、害 8，中位 `+0.0838`，只有 1 條因展開跌出窗。**Verification:** 本節自行收回該提議，寫入 OP② 作第四條排除方向。
- **QC:** `npm run check` 0 · `npm run build` 0 · `route_regression` **50 → 54**（新增四條對照組）· 紅測（新路由加裸「評核」）準確轉紅 4 條、其餘 50 條零波及、還原後 hash 一致 · `route_blast_radius` 185 條掃出**只有 1 條**改路由（正是目標）· `_s227_rubricJudge --self-test` 67 條 ALL PASS · `route_blast_radius --self-test` 8 條 ALL PASS · PR #20 `build-gate` SUCCESS、`mergeable CLEAN` · 部署後 `/health` commit `7be4404` ＋ 生產行為實測。
- **Evidence disposition:** 判官三輪校準與全跑的逐題證據留在四份 `eval_runs/*_rubric_judge.json`（已 commit）；展開效應的 63 題明細留在 scratchpad，關鍵數字已抄入 `dev/SESSION_HANDOFF.md`；操作紀律已升為 `dev/DOC_SYNC_CHECKLIST.md` 兩個新 row。
- **Sync:** `dev/DOC_SYNC_CHECKLIST.md` 新增「檢索路由改動」與「答案層評分改動」兩 row（原本兩層都無 row，依 anti-pattern guard 先補 row 再做）· `dev/SESSION_HANDOFF.md` 已更新 · `CODEBASE_CONTEXT.md` **不需改**（技術棧／目錄／build 指令／外部服務／Key Decisions 均無變）。
- **Pending:** OP② 片段層召回率（未試：cross-encoder 重排、按查詢長度自適應）· OP⑩ `hr_admin` 的「津貼」token 搶走 `kg_relocation_grant`（同族、已定位未修）· OP③ 封版閘餘下兩個 ERROR。
- **Risks:** 判官在準則 3（數字）兩個方向都出過錯，凡依賴該準則的判決一律標 `needs_human_review` · 判官跨次跑有變異（同一校準集 5/7 與 4/7）· `backend/scripts/*.ts` 十二支工具不在 `npm run check` 覆蓋範圍（Backlog ⑨）。
- **Log maintenance:** `session_log_maintenance.py --check` 報 `trigger=False`（245 行、7 條 entry，兩個門檻都未到）→ no-op，未做歸檔。
- **Opening-message mirror:** 已生成，與下方 Verbatim 區塊一致。

### Next Session Handoff Prompt (Verbatim)

```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

目前目標：Open Priorities ② —— 把片段層召回率拉高（生產 chunk recall@8 0.349，約三分之二情況拿對文件、拿錯段落）。

進度狀態：S227 已交付答案層 rubric 判官（OP① 完成），所以任何檢索候選現在都可以先量答案層再決定出不出貨。
四條方向已排除，不要重試：重新切片、調 per-source 配額、詞面重排 FEATURE_LEXICAL_RERANK（S227 量得 net −1）、
改查詢展開機制本身（S227 量得展開整體是幫忙的：37 條有展開題目中幫 29 害 8，中位 +0.0838）。
未試方向只剩兩條：cross-encoder 重排、按查詢長度自適應（plain 1–3 詞題 FAIL 24/77 vs natural_sentence 6/43）。

待辦（優先序）：② 片段層召回率 → ⑩ hr_admin 的「津貼」token 搶走 kg_relocation_grant（同族、已定位未修，動它前必須先量 blast radius）
→ ③ 封版閘餘下兩個 ERROR（只能靠 ②改善檢索清走）→ ④ 累積遺留 → ⑤ 56 條無路由題（被 pgvector 版本擋住，監察中）。

本節改動的關鍵檔案：
- backend/src/api/searchChannelB.ts — 新增 staff_appraisal 路由與 SOURCE_SET（不設 QUERY_EXPANSIONS），並由 hr_admin 移走 S226 那五個詞
- backend/scripts/_s227_rubricJudge.ts（新）— 答案層 pairwise rubric 判官
- dev/source/route_blast_radius.mjs（新）— 改路由必跑，掃 185 條 gold query 對照任一 git ref
- dev/source/route_regression.mjs — 三條改道 ＋ 四條對照組（50 → 54）
- dev/DOC_SYNC_CHECKLIST.md — 新增「檢索路由改動」與「答案層評分改動」兩個 row

已知風險 / 注意事項：
- 用 _s227_rubricJudge 必須 JUDGE_MODEL=gpt-4.1；gpt-4.1-mini 實測是壞尺（14 次判決 11 次揀先出現那一個）。
- 該判官在準則 3（數字與登記段落不符）兩個方向都出過錯，凡依賴該準則的判決自動標 needs_human_review，須人手覆核。
- 用 _s226_captureQueryVec.ts 做前後對照，必須由外面設 FEATURE_ROUTE_FIRST_SEARCH=1，否則量的是生產不執行的配置（S227 中過一次）。
- 改 TOPIC_KEYWORDS 必須同時跑 route_regression.mjs 與 route_blast_radius.mjs，並加對照組證明沒有搶走鄰居路由。
- backend/scripts/*.ts 十二支工具不在 npm run check 覆蓋範圍（tsconfig include 只有 src/**），要單獨指檔才真正 typecheck。

驗證狀態：本節全綠 —— check 0 · build 0 · route_regression 54/54 · blast radius 1 條（正是目標）· 兩支新工具 self-test 67 條與 8 條全 PASS ·
PR #20 build-gate SUCCESS 並已 squash-merge（7be4404）· 生產 /health commit 7be4404 · 生產行為實測「教師評核」答案段落入窗第 5、八格全部考績來源。

Post-startup first action: 跑起手探針核實 live 狀態（served app.html PLATFORM_VERSION ＋ Render /health ＋
git diff --name-only <部署commit>..HEAD -- backend 是否為空 ＋ Supabase chunk count），然後就 ② 的兩條未試方向向 Leonard 提一個帶成本估算的建議。
```

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-15 Session 226 — 每上一層量度，結論就被推翻一次；最後一層說不要出貨

- **ID:** `Claude_20260915_0650` — S226
- **Summary:** 還清 OP① 的 185 題 gold 量度債，**片段層首次量到**（生產 Chunk Recall@5 0.345），並把「為甚麼」一路追到底：不是切片問題、調配額是死路、詞面重排兩層同時改善 —— 然後合成側 A/B 顯示答案層面混合、有可指名退化，**出貨建議收回**。同節修好四處假綠／假紅與一個路由缺陷。AI 側零 Supabase 寫入、零 flag 啟用；唯一生產寫入由 Leonard 執行。
- **Changed:** `backend/src/lib/wikiRepository.ts`（`QUOTA_FAMILIES`＋`quotaBucket()`＋`rerankLexical()`＋`rerankQuery`，兩條路徑同步）· `backend/src/api/searchChannelB.ts`（`capFromEnv()`＋`MAX_PER_SOURCE`、`rerankQuery` 傳原查詢、`hr_admin` 補 `評核` 家族詞彙）· `backend/scripts/_s226_knobAB.ts`（由 `_s226_capAB.ts` 一般化：`--set`／`--ids`／`--synthesize`）· `backend/scripts/_s226_captureQueryVec.ts`（新）· `dev/_s213_run_gold.py`（`summarize()` 單一來源）· `dev/_s219_score_before_after.py`（import 共用）· `dev/_s213_corpus.py`（快取預設路徑）· `dev/_s213_gold_all.json`（2 條標籤）· `dev/_s226_fix_unmanaged_source.py`（新）· `dev/source/qc_report.py`（選檔優先生產端點＋補傳 `series_monitored`）· `dev/source/route_regression.mjs`（+4 案例）· `.gitignore`· `qc_report.json`· `dev/source/registry_drift.md`· `dev/source/eval_runs/2026-09-15_*`（11 組）。三個 PR：#16 `e08b7d9`、#17 `9fe1fbf`、#18 `1d92450`。
- **Done:**
  - **185 題 gold 三種跑法**：本機 in-process 兩側（12.4 分鐘、errors 0、**routeFailures 0**，S220 是 9）· 生產端點（32 分鐘、errors **1** 撞 `57014`）· 三個 knob A/B。**routed p90 2,498ms**（S220 是 8,335ms）、超過 8 秒的 RPC 0（S220 是 18）。
  - **生產旗標行為核實**：生產與本機旗標開啟側 **184/184 逐條同判**（含兩側判法相反的 7 題），與關閉側差 7 題。這是第一次可以不靠 dashboard 記憶確認 `FEATURE_ROUTE_FIRST_SEARCH`。
  - **`hr_mpf` 逐項查清**：09-08 的 PASS 靠已退役的 `g24`（0.5098 第一位）撐住；主要預期來源 `edbc00030` 兩次都不在前八；新版 SAG 有 23 條含「公積金」、`edbc00030` 70 條其中 1 條帶 gold 簽名。**不是丟內容。**
  - **答案鑰匙 183 → 185/185**：`cpd_mainland_promotion_tour` 純機械重錨（簽名一字未改、全庫唯一命中、頁碼 188 → 191）· `hr_appraisal` **改寫**（原簽名講收生利益衝突，答不到自己的 query「教師評核」；新簽名取自 SAG §7.7 員工考績 p.208）。重跑計分器實證 verdict 逐項不變。
  - **片段層診斷**：63 題逐題查答案段落位置 —— `NO_CHUNK_HAS_IT` **0**（不是切片問題）、`SOURCE_CROWDED` **61**、`SOURCE_ABSENT` 2、`TARGET_RETRIEVED` 0。其中 **16 條**目標片段餘弦高過第 8 名而其來源已佔滿 3 格（`maxPerSource`），最極端 `sec_cloud_shared_responsibility` 目標 0.5756 vs 第 8 名 0.3781。全 61 題 gap 中位 **0.0163**。
  - **零移植的量度基礎設施**：排序向量不是原查詢（後端嵌入 `expandQuery`，`QUERY_EXPANSIONS` 是 module-private），故寫 `_s226_captureQueryVec.ts` 由後端交出它嵌入了甚麼。**對照組攔下第一次嘗試**：用原查詢重算已回傳片段的餘弦，17/61 對不上（最大差 0.19）；改用展開向量並收窄到 vault 片段後中位差 0.00005，餘 2 題未解釋已點名。**副產品**：`footnote_` overlay 的分數對得上原查詢、vault 結果對得上展開版 —— 兩條路徑由兩個向量排序，這一點不在任何文件內。
  - **三個 knob**：`MAX_PER_SOURCE=8` 來源層 122→118／片段層 58→63（一換一）· `FAMILY_QUOTA=1` 122→121／片段層不變（不成立）· `FEATURE_LEXICAL_RERANK=1` 三點劑量曲線 122→126／129／132、片段層 58→61／64／64，**全部零退步**，片段層在權重 0.05 停滯而擾動與判官繞過翻轉隨權重上升（0／0／1）→ **拐點 0.05**。
  - **合成側 A/B（38 題，證據集真的有變者）**：30/38 答案有變 · **零新棄權** · 1 條由棄權轉作答。**兩個自動代理都失效**：gold 簽名代理 38 題全空；我自寫的數字流失篩查誤報 `fin_ac_grant`（after 其實有 `$8,384`，只是 `$` 前綴無「元」字）。逐對讀 7 對：明確變差 1（`hr_maternity` 自相矛盾）、可疑 1（`cpd_conduct_registration` 由誠實棄權變離題作答）、數字攪混 1（`dig_teacher_digital_cpd_hours`）、相等或更好 3–4。**結論：出貨建議收回。**
  - **四處閘的修正**：`EVAL_CHUNK_LAYER` 由假 `NOT_MEASURED` 變有數（成因是兩支 185 題 harness 都沒把片段層數字寫入 `summary`，而 `chunk_verdict` 一直算了出來）· `EVAL_LATEST` 選檔改為優先生產端點（Leonard 拍板選項 A）· `REGISTRY_SERIES` 假 ERROR（`qc_report` 漏傳 `classify()` 第七個參數，而 `check_registry_drift.py` 一直有傳 —— **兩邊數字不同本身就是 bug**）· `REGISTRY_UNMANAGED`（Leonard 執行 2 行 `source_id` UPDATE，守恆 0/7/17,004 已核實）。封版閘 PASS 12 → **14**、ERROR 4 → **2**。
  - **`評核` 路由修正**：`curriculum` 擁有裸 token「評核」而 `hr_admin` 只有「語文能力評核」，於是「教師評核」掉進沒有 SAG 的課程語料。在 `hr_admin` 補詞、不動 curriculum；回歸 46/46 → **50/50**（第四條是對照組）；before→after **blocking failures 0**、`VERDICT_FIXED` 1。
- **Fix Record:**
  - **Problem:** `EVAL_CHUNK_LAYER` 長期 `NOT_MEASURED`，交接檔記載「重跑 gold 就自然有」。**Root Cause:** 閘判分在 `if "chunk_FAIL" in s`，而 `_s213_run_gold.py` 與 `_s219_score_before_after.py` 都只寫四個來源層數字；每題的 `chunk_verdict` 一直算了出來、從未匯總。**Fix:** `summarize()` 併入 `_s213_run_gold.py`（`score_item` 旁邊）單一來源化，兩支共用。**Verification:** 5 條新斷言（含兩條守恆）；注入「`chunk_FAIL` 硬寫 0」→ 3 條轉紅；還原後 `shasum -a 256` 相同。
  - **Problem:** 起手時兩個工具對年度系列報不同數字（drift 報 0、封版閘報 1），當時記為「未核」。**Root Cause:** 那個分歧本身就是 bug —— `classify()` 的 `series_monitored` 預設空集，`qc_report` 只傳六個參數。**Fix:** 補傳 `monitorable_parents(sources)`。**Verification:** 改前先核實監察真的讀得到（13 個年份 → 13 條不同 http URL、13 個分片全部在服務、528 條片段）；新增 2 條斷言（一條盯呼叫點，因為回傳數字分不出「沒有系列」與「漏傳參數」）；注入再次漏傳 → 準確轉紅。
  - **Problem:** 詞面重排第一版完全沒有效果（smoke 3/3 零改動）。**Root Cause:** 照 footnote lead 的做法用候選集自己做 DF 語料，但候選全來自路由已選的來源，用戶打的字在裡面很常見 → 被當成 stopword 濾走。**Fix:** 直接用查詢 bigram 並按查詢長度正規化。**Verification:** 再 smoke 5 題見 1 題改變；全量 185 題兩層同時改善。**教訓已寫入碼內註釋**，免得下一位再照那套做一次。
  - **Problem:** 合成側 A/B 第一次回傳空答案，且請求數沒升，看起來像合成從未執行。**Root Cause:** 回應欄位是 `synthesis` 而非 `answer`；而 OpenAI SDK 自帶 `sdkFetch`，不經 harness 的請求計數器。**Fix:** 改讀 `synthesis`，並在碼內註明計數器不覆蓋 LLM 呼叫。**Verification:** 重跑 smoke 見到兩側答案全文。
- **Consolidation:** `_s226_capAB.ts` 一般化為 `_s226_knobAB.ts`（`git mv`），三個 knob 與合成側共用同一支 A/B harness，避免每個 knob 一支腳本各自漂移。`summarize()` 亦由兩份合為一份。
- **Log maintenance:** `session_log_maintenance.py --check` → `trigger=False`（212 行／6 條，門檻 400 行或 30 日）。Kit 側門檻（≥11 條或 >1500 行）亦未觸發。10-closeout backstop：本檔 6 條 ＋ 無 archive 目錄，未到。**no-op，原因：規模未達任何觸發條件。** `PROJECT_DECISIONS.md` 未促升 —— 三個 knob 的取捨已用實測數字結案；若下節決定出貨重排，那才是多選項架構取捨。
- **Evidence disposition:** 逐題原始擷取、答案全文、查詢向量 → `dev/source/eval_runs/2026-09-15_*`（11 組，已 commit）· 語料快取 28MB 已 gitignore 並在碼內寫明重建指令 · 分析腳本（延遲、片段診斷、分數差距、合成比較）留在 scratchpad，未入 repo（一次性）。
- **Prompt mirror:** 由交接檔唯一 fenced `text` 區塊重生並讀回，**逐位元組相等**（78 行，sha256 `7a92bd31…`）。
- **Boundary:** AI 側零 Supabase 寫入、零 DDL、零 Render 設定改動、零 flag 啟用。生產寫入（2 行 UPDATE）由 Leonard 自己執行 —— `gh pr merge` 與該次寫入都曾被 auto mode 分類器擋（`Merge Without Review`／`Modify Shared Resources`），未繞過。**Render 仍執行 `e9d14be`，`backend/src` 已有改動未部署。**

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-09-14 Session 225 — 封版閘上寫著 PASS 的那一格，量度的是一份不是評測的檔案

- **ID:** `Claude_20260914_2030` — S225
- **Summary:** 用 `ai-agent-patterns` 做完整 AI agent 架構盤點，結論是架構本身乾淨（全系統停在層 0／層 1、零工具呼叫、反模式十二條架構層面一條都不中），問題全在護欄與量度；盤點過程揪出並修好封版閘一項假綠。**零 Supabase 寫入、零 `backend/src` 改動、零 flag 改動。**
- **Changed:** `dev/source/qc_report.py`（新增 `is_gold_eval()`＋選檔過濾＋判分守衛＋五條斷言，+68/−9）· `qc_report.json`（重生）· `dev/AUDIT.md`（新增 239 行）· `dev/PROJECT_INDEX.md`（登記 AUDIT.md＋三行 Last verified）· `dev/DOC_SYNC_CHECKLIST.md`（新增一條觸發）· `dev/SESSION_HANDOFF.md`（Risks 新增第 8 項）。合併為 squash commit `40ae3cf`（PR #14）。
- **Done:**
  - **架構盤點（`dev/AUDIT.md`）**：七條 flow 逐條判模式；核實全後端 `tools`／`tool_choice` 零命中，模型在任何一處都沒有揀工具或決定下一步的權力；判定「可簡化的落差為無」。護欄逐項盤點，缺的是 token 預算、LLM 時鐘上限、追蹤記錄、成本記帳、輸入淨化。
  - **修好 `EVAL_LATEST` 假綠**：`latest_eval_run()` 原為不過濾的 `sorted(glob("*.json"))[-1]`，09-14 揀中一份沒有 `summary` 的 S223 內容重疊分析；`check_eval_latest()` 的 `.get("FAIL", 0)` 令缺欄位恆真 → PASS。修法是對齊同函式下半截 `EVAL_CHUNK_LAYER` 早已寫對的 `if "chunk_FAIL" in s`。
  - **量度基準的可信度問題入帳**：生產實際模型不可由碼或 `/health` 得知（最後人手確認 2026-07-30，其後 S211 才分拆 `JUDGE_MODEL`），判官 prompt V3 驗收集是在 `gpt-4o-mini` 上量的。
  - **起手探針 6/6 綠**：served `app.html` 3.3.8 · `/health` ok commit `e9d14be` · `git diff e9d14be..origin/main -- backend` 為空 · Supabase 17,004 · ZOMBIE 0 · 本機落後 1 個 commit（`discovery-bot` ledger）已 ff。
- **QC:** `qc_report.py --self-test` **ALL PASS**（新增五條斷言）· **紅測兩次各自準確轉紅且不波及其他**（打回 `.get("FAIL", 0)` → 兩條絕對值斷言轉紅；打回不過濾 `sorted()[-1]` → 只有選檔那條轉紅；兩次後皆以 `shasum -a 256` 核實還原）· `route_regression` **46/46** · `check_registry_drift --self-test` ALL PASS · 重跑 `--check` 前後對照：`EVAL_LATEST` PASS → **FAIL**、PASS 13 → 12、ERROR 2 → 3、releaseGate 5/15 → **4/15**、`PASS_EVAL_LATEST` MET → NOT_MET，**其餘二十項檢查零變動**、`overallStatus` 兩邊都是 ERROR · PR #14 `build-gate` pass、`mergeable=CLEAN`。
- **未做（不要當已做）**：185 題 gold 仍未重跑 · Recall@k 仍不可執行 · `regression:semantic`／`regression:grounded` 本節未跑 · 生產旗標與模型值仍無法由外部核實 · 七條前端未呼叫的端點是否死碼未查。
- **Evidence disposition:** 盤點結論 indexed in PROJECT_INDEX（`dev/AUDIT.md` 有 Directory Map row ＋ DOC_SYNC 觸發條件）；假綠一項 absorbed into handoff（`## Risks / Blockers` 第 8 項）；紅測與前後對照數字 kept as recent trace evidence（本條）。未達 PROJECT_DECISIONS 促升門檻 —— 本次缺陷是既有規則（`DOC_SYNC_CHECKLIST.md` row 56「新檢查不得預設報 0」）沒被遵守，非規則缺失，故未新增治理規則。
- **Sync:** `DOC_SYNC_CHECKLIST.md` row 56（品質檢查／封版閘改動）逐項 **confirmed**：`--self-test` 已跑、先證閘會紅已做、重跑 `--check` 並 commit `qc_report.json` 已做、`PROJECT_INDEX.md` Local QC Commands 三行 Last verified 已更新、`qc_report.yml` 無新增前置自檢故 **not_applicable**。新增 row（`backend/src` LLM／旗標／判官閘／護欄改動 → 覆核 `AUDIT.md`）**confirmed**。
- **Pending:** Open Priorities ① 重跑 185 題 gold —— 現在多一個理由：`EVAL_LATEST` 那一格已經誠實地紅，要它轉綠只能靠重跑，不能靠再改 `qc_report.py`。
- **Risks:** 本機仍有一條舊分支 `claude/hopeful-gates-0efe44`（1 個 commit 未入 main，v1.5.0 年代），**本節未動它**，待 Leonard 決定。`agent-handoff-kit` CLI 本機未安裝，故 `closeout-status` 語義閘**未能執行**，本次收工以人手逐項讀回代替（見下）。
- **Log maintenance:** **no-op。** 本檔 9 條 → 加本條 10 條；未達 N≥11 或 1500 行（現 188 行）任一硬觸發。10 次 backstop：S217 做過全面維護，本節為其後第 8 次，未到界。
- **Opening-message mirror:** regenerated and verified（逐字元比對通過；全文按設計不抄入本檔）。
<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-09-14 Session 224 — 把那道閘設成必過的正常做法，會反過來擋死整個 repo；而封版閘紅了一日，紅的是一件沒有發生過的事

- **ID:** `Claude_20260914_1313` — S224
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft，起手探針 6/6 綠、零漂移。Leonard 由 branch 選單見到兩條舊 `claude/*` 分支起問，一路推進到把 S223 交下來的 OP① 完整做完。**零 Supabase 寫入、零 `backend/src` 邏輯改動、零 flag 改動。**
- **Changed:** `.github/workflows/backend_build_check.yml`（拆 `paths:`，改為 job 內 scope）· `dev/source/execute_ingest.py`（步驟 6 改行 PR，self-test 13 → 28）· 四條 ledger workflow 加 `ssh-key` · `dev/source/qc_report.py`（凍結契約基準值 ＋ 兩條新紅案）· `dev/DOC_SYNC_CHECKLIST.md`（新 row）· `dev/PROJECT_INDEX.md` · `dev/CODEBASE_CONTEXT.md` · `qc_report.json`。commits `3affb71` → `eb585a0` → `abe1fad` → `fe3b6ba`(bot) → `4e46a7a`(PR #10) → `3359f94`(PR #11)。ops repo `5e27d2d`。
- **Done:**
  1. **OP① 完成，但原要求那一步本身是錯的。** 交接寫「去 GitHub 設 branch protection，五分鐘」。照做會撞兩堵牆：(a) `backend_build_check.yml` 有 `paths:` 過濾，而 required status check 要求該 commit 報 success／skipped／neutral —— **被過濾掉的 commit 甚麼都不報，那次 push 會永遠 pending**；(b) required check 擋的是**所有**直接 push（官方原文：`Required status checks must have a successful, skipped, or neutral status before collaborators can make changes to a protected branch`），而 `main` 有**五條**直接 push 路徑，不是交接寫的一條。
  2. **閘改為每次觸發、範圍在 job 內判斷。** 判不到就傾向照跑；scope 略過的 run **不會關閂** breakage issue（它甚麼都沒編譯，證明不了 main 編得過）。補 `route_regression.mjs` 入 watched 清單。兩半都在生產實測：`3affb71` → `BUILD — 2 watched path(s)` 九步全綠；`eb585a0`（純文件）→ `SKIP`，**5 秒** success。
  3. **Option A 步驟 6 改行 PR。** 推 `ingest/<source_id>` → 開 PR → auto-merge → 有上限輪詢。新增用 `ast` 讀自己的結構斷言，確認步驟 6 內再無 `HEAD:main`。
  4. **四條 ledger workflow 搬去 write deploy key**，因為兩條正路都不通（見 Fix Record）。`actions/checkout` 的 `ssh-key` 輸入先查證存在才用。
  5. **ruleset `main build gate` 落地**（id 23311105，bypass 只有 `DeployKey`，**沒有 admin**）。
  6. **修好 `FREEZE_CONTRACT` 假 BLOCKER**：BLOCKER 1 → 0，PASS 12 → 13，其餘計數不動。
- **Fix Record（三個假設被實證推翻，兩個是我自己的）：**
  - **「bypass GitHub Actions」在個人帳戶 repo 行不通。** GitHub 422：`Actor GitHub Actions integration must be part of the ruleset source or owner organization`。UI picker 沒有這一項不是找漏，是真的沒有。
  - **「把四條 ledger 改成開 PR」也不通。** 官方文件：由 `GITHUB_TOKEN` 開的 PR，其 run `require approval`，auto-merge 會卡死。deploy key 是排除法剩下那條，不是首選。
  - **`FREEZE_CONTRACT` 紅了一日，紅的是一件沒有發生過的事。** S223 依 Leonard 拍板把 guidelines 改為 2.6.2／151（公開端點實測早已服務該值），但 `qc_report.py` 的基準值仍寫 2.6.1／158。**根因不是疏忽：`DOC_SYNC_CHECKLIST.md` 根本沒有一條 row 指向那四個值。** 已補 row。同時補測試真空 —— 原有四條紅案**全部只變動事實數，guidelines 半邊零覆蓋**，而 S223 動的正是那半邊。
  - **我的指令害了 Leonard 兩次**：給他的收工 recipe 在「沒有未推 commit」時會失敗並留下空分支，中過兩次；第一版 ruleset 指令用了全形破折號，終端機 paste 時游標跳位令 JSON 壞掉。之後 git 操作由 AI 自己做，指令一律單行純 ASCII。
  - **攔截了一個假綠**：`git diff main <branch>` 報 `ambiguous argument`（repo root 有個 tracked 的 0-byte 檔案 `main`，2026-05-01 commit `8b03e1a` 誤入），輸出那個 `0` 來自指令失敗而非比對結果。改用 `--` 並以「分支 tip vs 它的 squash commit 樹比對」才刪分支。**退出碼非零時輸出的任何數字都不是量度結果。**
  - **本檔結構修復**：S223 與 S222 兩條條目原本被困在 Entry Template 的 ````markdown fence 內（fence 由第 20 行開到第 95 行），渲染成程式碼而非日誌條目。本節把兩條提出 fence 外、次序不變，fence 只留佔位模板。**零內容改動。**
- **QC:** `npm run check` 0 · `npm run build` 0 · `route_regression` **46/46** ＋成員斷言 · `execute_ingest --self-test` **28/28** · `qc_report --self-test` ALL PASS · `check_registry_drift`／`check_monitor_health --self-test` ALL PASS · 九個 workflow YAML 全部解析 · **紅測三次**（注入直接推 main → 27/28；回捲凍結基準值 → `intact freeze contract passes` 轉紅；移走 guidelines 比較 → 新加兩條準確轉紅且其餘不受影響）· **ruleset 實測擋得住**（推空 commit 被拒，兩條規則同時出聲）· **deploy key 實測推得到**（`abe1fad..fe3b6ba HEAD -> main`）· **PR 流程兩次**（#10、#11 皆 `BLOCKED → CLEAN → MERGED`）· 收工探針 v3.3.8 ／ 17,004 ／ ZOMBIE 0 ／ 線上 backend 碼 == HEAD。
- **Evidence disposition:** 全部為即時指令輸出與 GitHub API 讀數，已逐項寫入本條與交接 `## Validation / QC` S224 段；**無新增 eval run 檔**（本節零檢索改動）。ruleset 設定以 `gh api repos/:owner/:repo/rulesets/23311105` 可隨時重讀，故不另存快照。
- **Sync:** `PROJECT_INDEX.md`（閘那一 row 改寫，含「不得加回 `paths:`」禁令）· `CODEBASE_CONTEXT.md`（步驟 6 新形態 ＋ secrets 契約 ＋ AI Maintenance Log 兩條）· `DOC_SYNC_CHECKLIST.md`（**新增凍結契約 row**）· ops repo `executor.yml` 註釋（更正 `MAIN_REPO_PAT` 權限記載）· `qc_report.json` 重生並 commit。
- **Pending:** 185 題 gold 未重跑（OP①）· `finance` 路由缺口（OP②）· 封版閘仍非綠，四類（OP③）· **入庫 PR 路徑未經一次真實入庫驗證**（當日 approval queue 空）· 看門狗與 pgvector 監察仍未經真實排程觸發。
- **Risks:** ⚠️ 四條 ledger workflow 經 `DeployKey` 永久繞過該閘 —— 現時只寫 JSON、不碰 `backend/`，但那是「現時的碼」而非機制保證。⚠️ 新增一把沒有到期日的長期憑證 `LEDGER_DEPLOY_KEY`，等同可直接寫 `main` 的萬能匙。⚠️ 三項外部設定改動不在 git 內（auto-merge／delete-branch 兩個 toggle、deploy key `id=163258294`、repo secret），換機或重裝要記得。
- **Log maintenance:** **triggered（寫入後）＋ 記錄一個規則衝突。** 寫本條之前 `--check` 為 `trigger=False`（370 行 / 9 entries）；**本條寫入後升至 402 行，越過 §4a 的 400 行門檻**，`--check` 轉 `trigger=True line_trigger=True`。依 §4a「腳本是執行閘、不得靠判斷」執行 `--apply`：**402 → 187 行、10 → 5 條、5 條（S219–S215）移入 `dev/archive/SESSION_LOG_2026_Q3.md`**。逐條對帳 10/10 剛好一份，零重複零遺失；工具 `--self-test` 5/5。
  **⚠️ 歸檔工具有一個持續的 off-by-one（本節發現，非本節造成）：** `--apply` 在條目邊界切走內容後，會在**來源檔尾留下一個孤懸的 `ack:log-entry:start`**，並把多一個 `end` 帶進歸檔檔。實測：主檔歸檔前 10/10 平衡 → 歸檔後 **7/6**；歸檔檔歸檔前就已經 **13/16（差 3）** → 之後 **17/21（差 4）**，即這個缺陷在**先前每次歸檔都發生過**，不是今次才有。本節已修好主檔那一個（啟動會讀）；歸檔檔那 4 個留下未動 —— §4a 硬規則第 2 條明寫 `dev/archive/` 不在啟動必讀清單內，在收工時去改一個 1,931 行的歷史檔屬範圍蔓延。**工具本身未修**，已列入交接待辦。
  **⚠️ 規則衝突（依 AGENTS.md §5 記錄）：** 本專案 §4a 寫「>400 行即觸發、存 `dev/archive/`」，而 Kit closeout pack 寫「≥11 條或 >1500 行才觸發、存 `dev/SESSION_LOG_archive/`」—— 兩者門檻與目的地都不同。**取 §4a**：它有機械閘腳本、`dev/archive/` 已有 Q1／Q2／Q3 三個既有檔（即本專案既有慣例），且歸檔是移動非刪除，較可驗證。
  **⚠️ 同一衝突的第二面：** `--apply` 回報 `latest entry prompt block ok=False`，因為它按 §4 第 12 條期望本條含 `### Next Session Handoff Prompt (Verbatim)` 全文；而 **Kit closeout pack 明文禁止**把開場白全文複製到本檔（單一真源）。**取 Kit**：本專案在 S192–S193 正正因為 handoff 與 START 各寫一份而出現過 drift，三份副本只會重演。故該 `ok=False` 是**刻意的已知分歧，不是失敗**；exit code 為 0，非 §4a 第 4 條的停止條件。
- **Playbook（§14 留底）:** 見該庫 `usage/policychecker.log.md` 本日兩行。
- **Opening-message mirror:** **regenerated and verified** —— 由交接 `Next Session Opening Message` 唯一那個 fenced block 重生，五個錨點全部通過（marker 唯一、text fence 唯一、log 內無全文副本、正規化相等、byte-for-byte 相等；4,924 bytes / 62 行）。全文依 Kit 契約不複製到本檔。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-14 Session 223 — 部署已經死了十六小時而沒有任何徵狀；那個「刪了會失去 15%」的數字，是排版量出來的

- **ID:** `Claude_20260914_0650` — S223
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。起手探針按交接紀律「比檔不比 hash」，揪出 `main` 不編譯、Render 部署凍結 16 小時。Leonard 一句「全做」後連做三項；中途兩次以 `AskUserQuestion` 取得拍板（`g24` 去留、`guidelines.json` 是否 bump；`kgecg_2017` 是否清走）。**本節 AI 直接執行三次生產寫入**，推翻交接「分類器會擋住」的記載。
- **Changed:** 平台 **v3.3.5 → v3.3.8**（三次 bump）。新檔 `.github/workflows/backend_build_check.yml`、`dev/source/eval_runs/2026-09-14_s223_kgecg_g29_overlap.json`。改 `backend/src/api/searchChannelB.ts`（兩行位置）、`dev/source/execute_ingest.py`（locator 重寫 ＋ `--self-test`）、`backend/src/lib/wikiRepository.ts`（註釋）、`dev/_s213_run_gold.py`（註釋）、`dev/vault/sag_2025_11/extract_sag_2025_11_repaged.txt`（重抽）、`source_registry.json`、`guidelines.json`、`knowledge.json`／兩個 `role_facts.json`、`app.html`、`index.html`、`README.md`、`K1_API_SPEC.md`、`CHANGELOG.md`。commits `2dee4fb` → `7ab96bb` → `aeca54c` → `8deea11` → `e9d14be` → `abeba8a`（全部已 push）。
- **Done:**
  1. **部署管道解封。** `main` 由 2026-09-13 15:30 UTC 起不編譯（`e2b53f0`／`183b7a8`／`9e5f28c` 三個 watcher ingest commit），Render 建置失敗後繼續服務 `5765c43`，`/health` 照報 `ok:true`。**症狀不是停機，是部署凍結** —— 前端在 Pages 上完全正常，沒有用戶可見徵狀，所以 S222 收工時看不出來。
  2. **根因封死。** `plan_route_patch` 只掃 `start+60` 行找**含**「]」的行，找不到就把 `end` 留在 `start` —— `curriculum` 長到 61 行剛好越界。**修復工具交出一份看似正常的計劃，指向 route key 自己**，與 S222 那個 title backfill 同一家族。現在閉合括號必須整行只有括號且在 key 的縮排層級，無行數預算，找不到即報錯；executor 加結構不變式。`--self-test` 13 條，**紅測 6/13 FAILED**（含一條會即時掃真實檔案的斷言）。
  3. **新增 `Backend Build Gate`**（首跑通過）。此前八個 workflow **無一個跑 typecheck**，所以機械人可以把不編譯的 main 推上去而無人出聲。老實記住它偵測不阻擋。
  4. **OP①：《學校行政手冊》換 2026年8月版並合併 `g24`。** 上游 2026-09-07 原地換版，275 頁（舊 270）。用專案自己的 `repage_pdfs.py` 重抽 → **387 條**全部 page-resolvable。**連結由 landing page 改為 PDF** —— `g24` 本來才是指向 PDF 那個，沿用 landing 會**失去**跳頁而非保留甚麼。792 → 387。`guidelines.json` 以 `app.html` registry 為真源逐條對齊：移除 7 條、同步 32 個欄位，158 → **151**，bump **2.6.2**。
  5. **OP②：清走 `kgecg_2017` 108 條**，`g29` 107 條承接。**唯一的 ZOMBIE 由 1 歸 0。**
  6. **順手掃下游**：公開片段數多報 116 條（S222 清片段後沒跑 display-sync，用戶由 09-13 起一直見到 17,633）· README badge 停在 v3.3.3（S222 連 bump 兩次都沒掃到）。
- **Fix Record（推翻一個交接結論，並自我更正一次）：**
  - **「`kgecg_2017` 刪了會失去約 15% 內容」—— 假數。** S222 比較的是**兩批 live chunk**，出自不同管道（`g29` page-carried、`kgecg_2017` 無 page marker）與不同切割邊界，**量到的是管道不是文件**。同一抽取器＋對照組（自己對自己 0 miss）重量：兩份都 108 頁、`U+FFFD` 都 0、字元差 0.9%；落差**對稱**（11.7%／11.3%）；383 個落差視窗拆半後 88.5% 有一半在對方文件內、3.7% 兩半都在，**真正獨有 0.91%**，而那 30 條全是目錄與章節簡介的接合文字。**判別法**：落差對稱＝次序噪音。
  - **自我更正：曾在生產寫入之前就把預期的 17,112 寫入 README 與 `K1_API_SPEC.md`。** 這正是 S209 禁止的「靠加減推算」。已即時還原，等寫入落地後由 `live_total_count()` 讀真數再同步。
  - **`ingest_one_source.py` 在 792 條已經刪走之後才因缺 `openai` 失敗**，那一刻《學校行政手冊》在庫內是 0 條。成因是預設 `python3`（homebrew 3.14）沒有 `fitz` 亦沒有 `openai`。已入交接 Risks 6 與 `User Environment`。
- **QC:** `npm run check` 0 · `npm run build` 0 · `route_regression` **46/46** ＋成員斷言 · 五個 JSON 全部解析 · `execute_ingest --self-test` 13/13（紅測 6/13 FAILED 如預期）· `check_registry_drift --self-test` ALL PASS · `check_monitor_health --self-test` ALL PASS · 九個 workflow YAML 全部解析 · **生產寫入逐項對數**（409→0→387 / 383→0 / 108→0 / g29 107 未動 / 全庫 17,517→17,112→17,004）· **生產端到端五條查詢**（命中新版獨有的 8.4.4 國家安全章節 p.253；`g24`／`kgecg_2017` 零出現）· **瀏覽器實測三輪**（最終 v3.3.8 / 170 條 / 17,004 / 零過期數字 / 零 console error）。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-14_s223_kgecg_g29_overlap.json`（方法、對照組、視窗拆半分解）· `dev/init_backup/20260914_081342_UTC/`（SAG＋g24 刪除前計數）· `dev/init_backup/20260914_082948_UTC/`（kgecg 刪除前計數）。
- **Sync:** `CHANGELOG.md` 三條（v3.3.6／v3.3.7／v3.3.8）· `README.md` badge ＋ 四處數字 · `K1_API_SPEC.md` 四處 · `PROJECT_INDEX.md` 新檔與自測 · `DOC_SYNC_REGISTRY.md` 本節 row。
- **Pending:** branch protection（只有 Leonard 做得到）· 185 題 gold 未重跑，且 SAG 換版**沒有做 eval before→after**（舊語料已被覆寫，before 取不到）· `finance` 路由拿不到手冊 · `qc_report.json` overall ERROR · 36 個 PHANTOM · `stat_integrated` id 錯配。
- **Risks:** ⚠️ watcher bot 可以推出不編譯的 main，而新閘偵測不阻擋。⚠️ **「生產寫入會被分類器擋住」已證實過時** —— 安全邊界由機械閘變成「要先取得明示批准」這條紀律，兩者強度不同。⚠️ 預設 `python3` 缺依賴。
- **Log maintenance:** **no-op。** 本檔 8 條 → 加本條 9 條；未達 N≥11 或 1500 行任一硬觸發。10 次 backstop：S217 做過全面維護，其後 S218–S223 共 6 次，未到。
- **Playbook（§14 留底）:** 見本節 usage 行。
- **Opening-message mirror:** 見交接檔 `Next Session Opening Message`；本 log 依 Kit 契約不複製全文，只記驗證結果。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-13/14 Session 222 — 標籤講錯它服務的內容，是一個家族；監察偵測到了卻沒有人接，是另一個

- **ID:** `Claude_20260913_1330` — S222
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。Leonard 反覆「全做」推進：先答 Supabase 升級問題（核實後**取消**了 S221 交下來的那個決定），再由 `qc_report.json` 四個 ERROR 追出兩條主線 —— 瀏覽清單標籤錯配家族、監察排程的靜默死亡。兩個生產寫入由 Leonard 在終端機執行（分類器擋住 AI 的寫入路徑）。
- **Changed:** 平台 **v3.3.3 → v3.3.5**。新檔 `dev/source/registry_series.py`、`check_pgvector_release.py`＋`pgvector_seen.json`、`check_monitor_health.py`、`.github/workflows/pgvector_check.yml`＋`monitor_watchdog.yml`。改 `app.html`、`README.md`、`CHANGELOG.md`、`source_registry.json`、`_s213_title_backfill.py`、`cb3_deprecate_stale.py`、四個 `check_*.py`、`DOC_SYNC_CHECKLIST.md`、`PROJECT_INDEX.md`。commits `06daf7f` → `4623fbb` → `2ffba87` → `87c9c01` → `c8a2de3` → `fa13901`（全部已 push）。
- **Done:**
  1. **推翻了 S221 交下來的 OP①。** Supabase 的建置最高只打包到 pgvector **0.8.2**（`nix/ext/versions.json`，PR #2158，2026-05-22 之後三個多月無動靜），而封鎖 HNSW 的是 0.8.3／0.8.4。**升到頂都仍然封住** —— 那個決定無板可拍，改為機器監察。順帶分清兩個「最高版本」：0.8.0 是實例提供的（滯後），0.8.2 是建置打包的（領先）。
  2. **`_s213_title_backfill.py` 的 planner 由「讀成因」改為「讀損害」。** 它靠「找缺 header 的抽取檔」砌計劃；S213 補好 header 之後它就找到 0 個 —— **修復工具在損害仍然存在時靜靜解除了自己的武裝**。Leonard 執行後：代號標題 **658 → 0**、無連結 **265 → 109**（剩餘全是 role_facts_* Channel A 鏡像，依設計無連結）。
  3. **標籤錯配是一個家族，不是 g37 一個。** 176 條瀏覽條目逐條對照片段實際攜帶的標題／連結，26 條對不上；扣除良性的（瀏覽連 landing page、片段連深層 PDF，屬設計）後按同一裁示處理：六條標籤改正（`g36` 與 g37 完全同形、`g33`、`g22`、`nat_sec_edu`、兩個 hub），五條零片段重複條目移除。瀏覽庫 **177 → 171**。
  4. **清走 `arts_kla_guide_2017` 116 條**（Leonard 執行）。實測 115/116 條片段文本與 `g37` 逐條相同、內容 99.9% 重疊。全庫 17,633 → **17,517**，`g37` 116 條未受影響。
  5. **528 條片段脫離監察黑洞。** `registry_series.py` 令四個監察展開年度系列；`check_freshness` 檢查量 271 → 284。連帶修好 `SERIES_UNMONITORED` 這一類「無條件報 ERROR」的設計 —— 缺陷修好之後它本來會永遠亮紅。
  6. **監察排程的三個靜默死亡模式**（官方文件核實）：GitHub 不補跑錯過或失敗的排程、`schedule` 高負載會延遲或跳過、**PUBLIC repo 60 日無活動排程自動停用**。新增每日看門狗：由 Actions run 歷史判斷「最後一次成功」，過週期自動補跑，靜兩個週期才出聲。零改動現有七個 workflow。
- **Fix Record（自我推翻三次）：**
  - **「SAG 有人改了登記卻忘記入庫」** —— 錯。CHANGELOG 加實測證實：上一節評估過 2026年5月版唯一實質改動，用一條 footnote 精準覆蓋而不重入整本，是合理決定。**已完整撤回據此所作的改動。** 真正的漂移是下一版（2026年8月版）。
  - **「41 個可瀏覽指引搜尋不到 = 23% 缺口」** —— 作廢。至少 4 個根本不是缺口，內容早已入庫，只是掛在另一個 id 之下。
  - **「跨抽取器量得 20.8% delta」** —— 假數。舊 extract 出自 PyMuPDF、我用 pdftotext，閱讀次序差異造成大量假差異。改用同一抽取器並設對照組（舊對舊 0 miss）後為 11.9%／12.9%。
  - **看門狗第一次跑就揪出自己一個 bug**：`_token()` 有 guard 但漏了 `return`，送出 `Bearer None` 全部 401，而當時設計會把「讀唔到」摺成「從未成功」→ **假全紅**，同假全綠是同一缺陷的兩面。已加第三種狀態並補斷言。
- **QC:** 六個監察自測全 `ALL PASS`（含 `check_expiry` 18 條、`check_pgvector_release` 24 條、`check_monitor_health` 11 條 prove-assertions）· `_s213_title_backfill --self-test` 15/15 · 七個 workflow YAML 全部解析通過 · **瀏覽器實測** `app.html`：171 條、零重複 id、tab 顯示「📚 EDB指引 (171)」、零 console error · 18 條要寫入的 URL 逐條 HTTP 200 · 刪除後逐項對數（116→0、g37 未動、全庫 −116、代號標題 0）。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-13_s222_duplicate_rows_predelete.json`（刪除前完整 row dump）· `2026-09-13_s222_sag_edition_delta.json`（版次 delta，含對照組數字與 400 條新版獨有片段樣本）· `dev/init_backup/20260914_063210_UTC/`（cb3 工具自己寫的刪除前計數）。
- **Sync:** `DOC_SYNC_CHECKLIST.md` 加三行（上游原地換版、標籤與內容不一致、新增排程監察要同步 cadence 表）· `PROJECT_INDEX.md` 加三個新檔與三條自測 · `CHANGELOG.md` 兩條（v3.3.4／v3.3.5）· `README.md` 指引數 177 → 171 · `guidelines.json` **刻意未動**（凍結合約，見交接 Risks）。
- **Pending:** SAG 重新入庫（Leonard 指示下一輪做）· `kgecg_2017` 由哪一版重新入庫（下一輪）· `qc_report.json` overall ERROR · 36 個 PHANTOM · registry 281 vs 服務 300。
- **Risks:** ⚠️ 看門狗跑在同一套排程機器上，救不到「七個一齊死」；買到的是互相監察，偵測窗由一星期收窄到一日 —— 這句寫死在它每次出聲的輸出裡。⚠️ `.claude/settings.local.json` 已加 Bash 權限規則（Leonard 執行），dry-run 通過但 `--execute` 仍被分類器擋 —— 刪資料那一類清不到，屬預期。
- **Log maintenance:** **no-op。** 本檔 7 條 → 加本條 8 條、311 行；未達 N≥11 或 1500 行任一硬觸發。10 次 backstop：S217 做過全面維護，其後 S218–S222 共 5 次，未到。
- **Playbook（§14 留底）:** 兩行 usage（`freshness-monitor-test-served-url` lookup、`cloud-routine-vs-local-task` applied）＋ 新提案 `inbox/2026-09-13-policychecker-watchdog-for-cron-monitors.md`（「檢查報告不了自己從未運行」）。已 commit 並 push（`3d41612`）。
- **Opening-message mirror:** 見交接檔 `Next Session Opening Message`；本 log 依 Kit 契約不複製全文，只記驗證結果。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-12 Session 221 — cpd 路由慢的成因是查詢計劃把過濾次序倒轉；刪一行 GUC 令 S219 那個索引首次真的被用上

- **ID:** `Claude_20260912_0655` — S221
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。跑起手探針揪出 S220 收工 commit 未 push（Leonard 自行 rebase＋push）；跑版本閘後**改寫了 HNSW 的封鎖理由**；然後查 cpd 抖動，用 `explain (analyze, buffers)` 找出真因並由 Leonard 套用一行 DDL 修正。
- **Changed:** `dev/SESSION_HANDOFF.md`（Risks 1／4、OP ①③、Recommended next step、Current Baseline git 事實、開場白段落、Supabase Technical Notes 加 S221 block）· `dev/DOC_SYNC_CHECKLIST.md`（新增一行：外部平台事實重驗推翻既有判斷）· 新工具 `backend/scripts/_s221_routedBaseline.ts`。**零 `backend/src` 改動、零前端改動、零 git push。** 唯一外部寫入是 Leonard 在 Supabase 執行的一句 `create or replace function`。
- **Done:**
  1. **版本閘（OP①）跑完：Supabase 提供的 `vector` 版本最高只到 0.8.0 ＝ 已安裝版本，升無可升。** 並**改正了交接對這件事的定性**：擋住 HNSW 的不是 CVE-2026-3172（0.8.2 修，官方緩解為建索引前 `set max_parallel_maintenance_workers = 0`），而是 **0.8.3／0.8.4 那兩個 HNSW vacuum 修正 —— 關不掉**（autovacuum 必然會跑）。解封只有 Supabase 平台升級一條路。來源：pgvector CHANGELOG、NVD、Supabase Extensions 文件。
  2. **查明 cpd 抖動主因。** `explain (analyze, buffers)` 對照兩個 allowlist：curriculum 的 Filter 先 `source_id` 後距離（3,615 列／81,619 buffer hits／131ms）；**cpd 的 Filter 次序倒轉**，先為全部 17,610 列算距離（135,502 hits／9,639ms、重跑 5,475ms）。同一句放行 bitmap 之後走 `Bitmap Index Scan on wiki_chunks_source_id_idx`（939 列／17,433 hits／681ms）。**工作量降至 12.9%（buffer hits，確定性數字）；時間欄同一計劃三跑差近倍，屬實例負載，不作為結論依據。**
  3. **DDL 已套用（Leonard 執行）**：刪 `match_wiki_chunks_routed` 內的 `set local enable_bitmapscan = off`。連帶意義 —— S219 加的 `wiki_chunks_source_id_idx` 一直被那句封死，此前從未被用過。
  4. **正確性閘先立後驗（新工具 `_s221_routedBaseline.ts`）**：改前記低 7 條題的 routed RPC 回傳（id＋score），改後重用**同一批向量**再跑一次逐條比對。結果 **6/6 原本成功的完全相同**，第 7 條（cpd「專業階梯」）由 **HTTP 500／0 列 → 200／40 列**。
  5. **實測坐實了一個此前只是推斷的事**：改之前那條 cpd 題在本機 8 秒上限之下就已經逾時回 500，`catch` 吞掉後靜靜回落全庫搜尋 —— 即 cpd 這條路由在生產形同虛設，用戶不會察覺。
  6. **排除了自己提出的「cpd 每列貴 20 倍」。** 交錯重量三輪（A 只揀資料／B 揀+計算，兩個 allowlist 交替）：暖狀態每列 cpd **0.0096ms**、curriculum **0.0102ms**，總時間隨列數線性（×3.85 列 → ×3.9 時間）。**那 681ms 對 131ms 是冷熱兩個狀態的比較，不是兩批資料的差異。** 真正在飄的是實例：同一句第一次 916／2,259ms，第二三次 10／39ms，差 58–90 倍；**成因未查明**（EXPLAIN 報 `read=0`，頁面已在記憶體，照計不應如此；疑似免費方案 CPU 爆發額度，無證據）。附帶：暖狀態下 routed 查詢真實成本只有 10–39ms，用戶等的 1.5–2.4 秒主要在 embedding 與網絡。
- **QC:** `npm run check` 0 · `_s221_routedBaseline.ts --compare` **6/6 identical ＋ 1 was-failing-now-ok ＋ 0 problems** · `route_regression` **46/46** · `regression:grounded` **48/48** · 生產 `/api/search/channel-b` 三條 cpd 題各 3 次共 9 次全部 `ok`／8 結果（1.48–2.42 秒；**首次 24.6 秒是 Render 冷啟動，不是查詢延遲**）。**未做：同批查詢的生產前後對照**（前值取自 S220 記錄的 2.81／6.10／6.41 秒，非同一批、非同一時段），故「快了多少」只有指示性。
- **Evidence disposition:** `dev/source/eval_runs/2026-09-12_s221_routed_before.json`／`_after.json`／`_vectors.json`（向量快取，供日後同基準重跑）。
- **Sync:** 交接檔 Risks 1／4、OP ①③、Supabase Technical Notes 已同步；`DOC_SYNC_CHECKLIST.md` 依其 anti-pattern 規則補了缺失的一行。`CODEBASE_CONTEXT.md` **N/A** —— pgvector 版本與 RPC 計劃設定不屬其 External Services 已登記項目（如日後要登記，應與 Supabase block 一併處理）。
- **Pending:** OP① 平台升級待 Leonard 決定 · Risks 4 餘下那截（cpd 每列仍比 curriculum 慢約 20 倍）未查明 · 三題 chunk recall · `qc_report.json` overall ERROR · 41 個指引 chunks=0 · registry 281 vs 服務 300。
- **Risks:** ⚠️ 本次 DDL 只在生產庫套用，**沒有 staging 對照**；回滾段已備在交接檔 Supabase Technical Notes。⚠️ 本機量度仍在 8 秒上限之下進行（`.env` 沒有 `SUPABASE_ANON_KEY`），故本節所有本機時間**不可當生產數**。
- **Log maintenance:** **no-op。** 本檔 6 條 → 加本條 7 條；未達 N≥11 或 1500 行任一硬觸發，10 次 backstop 亦未到。
- **Playbook（§14 留底）:** 收工時 grep 全表，配到 `inspect-live-infra-before-ddl`（本節確有照做：改 DDL 前先 `pg_get_functiondef` 抽 live 定義），已 append usage 一行（applied）。另交提案 `inbox/2026-09-12-policychecker-guc-disable-kills-filter-index.md`：為求 exact 而關索引，關得太闊會連過濾用的 btree 一齊封死；附冷熱交錯重量的判別法。兩者已 commit 並 push 至該庫。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成 `START_NEXT_SESSION_PROMPT.txt`（62 行 / 5,070 bytes），讀回逐位元組相等；全文按 Kit 契約不複製入本 log（沿用 S216–S220 對 §4 規則 12–14 與 Kit core 衝突的既定取捨）。
- **機器閘（收工實跑）:** `doctor` **53/53 status: passed** · `closeout-status` **status: complete**（首三次報 blocked，皆因本節記錄與 Open Priorities／Risks 有重複措辭令 lifecycle 讀回判為「已完成又仍待辦」；逐次收窄措辭後轉綠，內容未刪）· `session_log_maintenance.py --check` `trigger=False`。

<!-- ack:log-entry:end -->

<!-- ack:log-entry:start -->

## 2026-09-09 Session 220 — route-first 的碼與名字相反：它疊加而非取代全庫搜尋；修正後 OP② 在生產由 9 次 5 敗變 0 敗

- **ID:** `Claude_20260909_0700` — S220
- **Summary:** 由頂層 dormant root「開工」redirect 入 Draft。Leonard 逐步授權：收 watcher commit → 補 OP③ → 全修文案 → 開始 OP① → 批 185 題 live 批次 → 揀「先修重試再開 flag」→ 在 Render 開 `FEATURE_ROUTE_FIRST_SEARCH=1`。**本節推翻了 S219 兩個結論，兩個都有實測支撐。**
- **Changed:** 8 個 commit 全部已推（`7ddafc7` `f8eabf0` `5cb1ec7` `e4090dc` `bda6ae8` `9072af1` `172c3cd` `6cbb49c`）。生產碼 `backend/src/api/searchChannelB.ts`、`backend/src/lib/wikiRepository.ts`。工具 `backend/scripts/routeFirstGold.ts`（改良）、`_s220_retryBudget.ts`、`dev/_s220_latency_verdict.py`（新）。文案 `README.md` `K1_API_SPEC.md` `CHANGELOG.md` `app.html` `index.html` `q.html` `t-purchase.html` `embed-sample.html` `mobile.js` `knowledge.json` `role_facts.json` `dev/knowledge/role_facts.json` `backend/README.md` `dev/source/execute_ingest.py`。平台 **v3.3.2 → v3.3.3**。
- **Done:**
  1. **推翻 S219「索引幫不到」。** 該結論源自 `select=id,embedding` 取 50 列 = 1,042ms → 16ms/列。實測每列回應 **19.3 KB**（50 列共 965 KB），那是 JSON 出口頻寬，不是伺服器運算。決定性一測：RPC 只回 **942 位元組**仍要 **3.37 秒**，與回 50 列的 3.41 秒相同 → 成本在伺服器端搜尋，索引直接相關。
  2. **揪出 route-first 的碼與名字相反。** `searchWiki` 在 1467 行無條件 await，無任何 branch 跳得過；routed 在其後跑並覆蓋結果 → flag 開啟時命中路由的查詢付雙倍代價、丟棄貴那半。**這才是 S219 那 26.4% 的成因**，不是「系統餘裕不足」。已修為 routed 取代、失敗才回落。
  3. **185 題閘重跑（Leonard 批准 live 批次）。** 185/185、errors=0。正確性與 S219 完全相同（FAIL→PASS 5、PASS→FAIL 4、淨 +1）——**證明次序修正不改檢索結果，只是不再白做**。
  4. **重試由次數制改為 6,000ms 時間預算。** 57014 代表已耗盡 `statement_timeout`，再試兩次等於再等兩個上限；gold 跑實測一題 8,842＋9,183＋8,316ms ≈ 27 秒。冷啟動閃斷的重試保留。兩個重複迴圈合併為 `postRpcWithRetry()`。
  5. **OP② 在生產解決。** 同三條題、同端點、前後皆在生產量：**9 次 5 敗 → 9 次 0 敗**，`cur_eight_kla` 由 3/3 敗變 3/3 過。設對照組（兩條無路由題）排除「整體變暖」：它們仍在 2.7–3.9 秒，有路由題已降至 1.4–2.2 秒。
  6. **全站文案對正**（Leonard 指示「留意適時更新」）：`sources` 六個鏡像寫 288、`app.html` 同屏另有寫死的 120，實查 distinct `source_id` 307 扣 7 個 `role_facts_*` = **300**；`index.html` 兩段幻影文案（S167 已移除的螢光標註、已下架的通告分析）；手機 `#templates` 死路加閘；README 四處自相矛盾；`K1_API_SPEC` 對下游報 152 而端點實為 158。另 `execute_ingest.py` 加 `live_sources_count()`＋step 5c 防再漂（**用具名欄位配對，不沿用裸數字全檔取代** —— 對 17610 安全，對 288 不安全）。
  7. **兩個休眠頁封路。** `q.html`／`t-purchase.html` 是已建未出街的功能。實測仍有活路徑：公開 README ＋ 交予學校 IT 的 `embed-sample.html` → `q.html` → `t-purchase.html`，三頁皆 200 且無 robots meta。已加 `noindex,nofollow` 並移除兩條入站連結，頁面本體不動。**刻意不加 `robots.txt`** —— `Disallow` 會令爬蟲讀不到 `noindex`，兩者互相抵消，且公開檔會替刻意不設連結的 status 頁賣廣告。
  8. **OP③ 補回** `backend/README.md` 遺失的 flag 說明。先查證不可還原（README 最後 commit `cd4c10e` 早於引入 flag 的 S214，`git log -S"FEATURE_"` 零結果），改為**由碼重寫**並在 commit message 明寫非還原。
- **Fix Record（自我推翻一次）：**
  - **問題：** 我由「40 列 0.5 秒 vs 全庫 3.1 秒」推出「每列約 1.1 毫秒」的成本模型。**根因：** 樣本只有兩點就外推線性關係。**實測反證：** curriculum 3,618 列只需 0.82 秒，而 cpd 939 列要 2.8–6.4 秒。**修正：** 該模型已撤回，成本不隨路由列數線性縮放；cpd 的抖動成因未查明，不編機制。
- **QC:** `npm run check` 0 · `build` 0 · `regression:grounded` **48/48** · `route_regression` **46/46**（含 flags-off 不變式閘）· `_s220_retryBudget.ts` **4/4**（離線 stub，零網絡）· `_s219_score_before_after.py --self-test` **6/6**。部署後生產實測 12 項全通過（`/health` commit＋暖機、三端點、noindex、入站連結、sources=300、幻影文案、mobile 閘、版本與快取鍵）。**未跑：Recall@k**（工具需要已刪除的舊 scratchpad 語料快取，重負載後不宜再拉語料；**未量，亦未沿用 S219 數字**）。
- **Evidence disposition:** 四份存 `dev/source/eval_runs/`：`2026-09-08_s220_route_first_before_after.jsonl`＋`.meta.json`、`_before.json`／`_after.json`、`2026-09-09_s220_op2_preflag_production.json`、`2026-09-09_s220_op2_postflag_production.json`。**兩份生產檔含全部回應 body（含失敗）** —— S217／S219 各有一次「未存 body 故成因無法證明」，本節不重複。
- **Sync:** `CODEBASE_CONTEXT.md` 已更新（route-first RPC block 的啟用狀態、次序、重試預算；另修正 S215 兩處已被交接推翻的記載 —— 本體「未經核實」已由 S219 introspection 結案、部署 build 引用次數由 `4a25a15` 的 0 更正為 `3ebd11f` 的 3）＋ AI Maintenance Log 兩條。`CHANGELOG.md` 加 v3.3.3 條目。
- **Pending:** OP① HNSW 未開始（**先決條件：Leonard 跑 `pg_available_extension_versions` 唯讀查詢**）· cpd 路由抖動未查明 · `qc_report.json` overall ERROR 未處理 · 41 個指引 chunks=0 · registry 281 vs 服務 300 的差額未對帳 · `app.html` KLA「多份」待 Leonard 定義精確數。
- **Risks:** 🔴 **CVE-2026-3172 影響 pgvector 0.6.0–0.8.1（本專案 0.8.0），觸發條件正是以 parallel worker 建立／重建 HNSW 索引** —— 未確認可升級前不得建 HNSW。⚠️ 本機量度比 Render 慢約 1.5–2 秒（實測：生產端到端做更多事只需 3.07–3.96s，而本機裸 RPC 已 3.31–3.88s），**故 S220 gold 跑的 35.1%／18.4% 是上限值，不可當生產數**。⚠️ 路由的 p90 尾部（8,335ms）比全庫（3,782ms）更差。
- **Log maintenance:** **no-op。** 本檔 5 條 → 加本條 6 條，255 行；未達 N≥11 或 1500 行任一硬觸發，S217 剛做過全面維護、10 次 backstop 亦未到。
- **規則衝突（依 §5 記錄）：** 沿用 S216–S219 的取捨 —— 專案 INSTRUCTIONS 層 §4 規則 12–14 要求把開場白逐字寫入本 log，本檔前言（Kit managed core）則明寫「The full opening message never belongs in this log」。取較可驗證且不製造第二個真相源的一方：只寫 mirror 行，全文留在交接檔。 **本節另撞到同一家族的第二處衝突**：§4 規則 5 要求開場白逐字使用「§1 startup sequence: … → dev/SESSION_LOG.md → …」模板，而 Kit managed core 的 anchor 要求開場白必須含「Do not read dev/SESSION_LOG.md during ordinary startup」—— 兩句語意直接相反。我起初寫了 §4 模板，`doctor` 隨即報 anchor 缺失（35 項檢查 1 項不過）。**取 Kit 一方**（機器可驗證，且與 S216–S219 的既有開場白一致），衝突記於此。
- **Playbook（§14 留底）：** **本節未 grep 全表、未開任何卡，故按該庫規則不寫 usage 行。** 但產生了兩條夠成熟可轉移的教訓，已備妥提案待交（見交接檔 Pending）：(a)「量到出口頻寬，卻用來論斷伺服器端成本」這個量度陷阱；(b)「當失敗本身就是逾時，重試預算應該用時間而非次數」。
- **Opening-message mirror:** 已重生並驗證 —— 由 `SESSION_HANDOFF.md` 唯一的 fenced block 生成，讀回逐位元組相等；全文按契約不複製入本 log。

<!-- ack:log-entry:end -->
