# Project Decisions — EDB K1 知識平台

> Long-term architecture choices, multi-option trade-offs, and cross-session evolution.
> Created S145 (§4 trigger c: Q4 Phase 2 completion).

---

## Architecture Choices

### ADR-00Y — 壞掉的文字層：OCR 重抽，而非算術還原（S212）
- **Date**: 2026-09-03（S212）
- **Status**: IMPLEMENTED + LIVE（`phys_sss_2007_2015`，187 chunks）
- **Context**: 該源 165/182 條片段係不可讀嘅 CID 亂碼，而三個現有監察全部綠燈 —— URL 回 200、位元組自 2015 未變、封面標題對得上。文字層抽取救唔到：`pdftotext` 抽出同舊 extract **逐字相同**嘅亂碼，因為 PDF 本身嘅 ToUnicode CMap 壞咗。
- **Options considered**:
  - **A. 算術還原（否決）** —— 亂碼係三個字族嘅固定偏移（`+0x3058` 主 CJK、`+0x2D1E` CJK 標點、`+0x8E51` 全形標點），可還原 **98.4%**，讀落完全通順，而且零成本、零 API 呼叫。**否決理由**：與 OCR 交叉核對封面頁，「二零一五年十一月」被還原成八個似是而非嘅漢字 —— 其他字體子集嘅字偏移後碰巧落喺合法漢字區。剩低嗰 1.6% **唔係明顯壞，係靜靜錯**，屬 S194 `ict_sss_2021`「200-但-錯檔比 404 更難捉」同一類。**98.4% 係陷阱數字。**
  - **B. 退役刪除（否決）** —— 該源係唯一嘅高中物理課程及評估指引，冇可引用替代品（對比 `kgecg_2017` 有 `g29` 頂上）。紀律 #4。
  - **C. OCR 重抽（採用）** —— `dev/ocr_extract.py` 本來就係為呢個 failure mode 而建（docstring 明文寫 CID-mojibake，先例 g38 / S147）。
- **Decision**: C。150 頁、69,397 中文字、0 個 U+FFFD、0 失敗頁、亂碼 0。
- **Trade accepted, and measured rather than asserted**: OCR 係**草稿質素**，錯法係**術語級誤字**。逐頁對照渲染原圖：p.27「普適氣體定律」→「普通」、「查證」→「查察」；p.20「貫徹」→「實徵」、「樂意」→「樂於」，約每頁 1–2 個（≈0.5%）。**呢個正正係否決 A 嗰個失敗模式**，只係程度有別：算術還原出「澳瀈」（明顯亂碼），OCR 出「普通」（真詞、讀落順口、更難發現）。取捨係 **0.5% 錯字 vs 91% 讀不到**，跟 S147 為 `g38` 同 `mce_framework_2008` 定落嘅先例。registry notes 已記錄具體錯誤類別，唔係只寫「OCR」。
- **Unforeseen wins**: 舊 extract 得 149 頁（PDF 150）—— 文字層抽取跳過咗真空白嘅第 2 頁，故舊庫內每個頁碼標記由第 2 頁起都比實際少 1，「頁 N ↗」一直指早一頁。重抽已修正。
- **Cost**: 150 頁 `gpt-4o` vision。**呢一步耗盡咗 OpenAI 額度並令生產全站搜尋 429 約半小時** —— 見 Insights。

### ADR-00Z — 新語料唔夠可達時：獨立路由，而非折入既有路由（S212）
- **Date**: 2026-09-03（S212）
- **Status**: IMPLEMENTED + LIVE（`info_security` = `g28` + `pcpd_cloud_computing`）
- **Context**: 交接 OP⑤ 寫「加保安／雲端字眼落 `digital_education` regex」。
- **Options considered**:
  - **A. 折入 `digital_education`（否決）** —— 該路由嘅 `QUERY_EXPANSIONS` 有 21 個 DEBP／AI 詞。實測（同一 build、關掉路由過濾、raw 對 raw+expansion）：「網絡安全運動」`g28` rank 0 @0.5728 → **完全消失**；「雲端運算 私隱」`pcpd` rank 0 @0.6876 → **完全消失**，兩次個窗都被 DEBP 片段 @0.69–0.74 佔滿。**擴充把 query 本身蓋過** —— 照交接寫法做會令目標 query 變差，方向啱結論反。
  - **B. 獨立路由、不設 expansion（採用）** —— 同 `safety` / `gov_admin` 一樣嘅處理（S142 已定 EXCEPTION 準則）。
- **Decision**: B。刻意**唔認裸「資訊保安」**：S209 已定案該闊 query 返 SAG／`role_facts_it` 係啱嘅，認咗就會把佢硬過濾去答唔到佢嘅來源。
- **Evidence**: eval 顯示兩條 SET_LOST，逐條讀過 —— 掉走嘅係 `ph_pri_guide_2025`（小學人文科）、`ict_sss_2021`（ICT 科課程）等**錯科目雜訊**，屬刻意收窄。**冇為此加豁免分類** —— 喺同一個 session 內把紅燈教成綠燈去襯自己嘅改動，正正係唔應該做嘅事。
- **Ceiling is the corpus, not the routing**: 逐條讀晒 `g28` 40 條片段，只有 10 條有可用建議（兩份警方 Zoom 指引），其餘 29 條係 2018–2022 五份通函講海報派發同一個短片設計比賽（獎品、報名表、2018-07-27 截止）。佢被標 `lifecycle: reference`，因為 lifecycle 係**逐來源**標，而 `g28` 係七份文件嘅 hub —— 七份文件嘅壽命根本唔一樣。

### ADR-00X — 具體數值查詢：詞彙層檢索，而非再調相似度門檻（S211）
- **Date**: 2026-09-01（S211）
- **Status**: IMPLEMENTED + LIVE（單源特例；一般化屬 Open Priority ④）
- **Context**: 「12 班小學有幾多個學位教師」一類查詢，答案逐字載於 `staff_est_pri`，但平台答出**確定而錯誤**嘅數字（「不設副校長、學位教師 2 名、合計 10 名」；正確為副校長 1 名、學位教師 5 名、合計 21 名）。系統取咗同一張表另一行，冠以「12 班」之名，且毫無保留語氣。該表 36 行近乎相同，班數係索引欄。
- **Options considered**:
  - A：收緊 `VAULT_LEAD_SCORE`（0.70）→ ❌ **實測否決**。全語料只有四個 case 觸發 bypass；要擋走 D02（0.7428）就必然連 `teacher_qualification` 目標題（0.7093）同 GN11（0.7221）一併擋走，而該兩題判斷閘被問到時答錯。S195 早已寫「no choice of number is safe」，S211 量到具體代價。
  - B：改寫判斷提示 → ❌ **實測否決**。五個版本（加資格適用性規則／改開場問法／重排規則次序／明寫「資料唔會逐個唔符合嘅情況寫一次」）喺凍結驗收集全部與 shipped 一模一樣：31/33、12/12、19/21、同樣兩個 false answer。連 `gpt-4o` 都拒答。
  - C：只重新切片（`chunk_overlap=0`，一行一片段）→ ❌ **實測否決**。半行開頭由 74/81 降至 2/85，但正確嗰行仍然排唔上（該行對自身問題 cosine 只 0.5923），合成器改為由 6、7、8 班嘅數值**內插**——由「確定而錯」變成「有自認嘅錯」，兩者皆不可接受。生產寫入已逐 byte 還原。
  - D：擴闊合成視窗至「五格主搜尋 ＋ 強制置頂嗰幾格」→ ❌ **實測否決**。答案片段確實入咗窗，判斷閘仍然拒答，而**拒答係啱嘅**（片段由半行開始，同一段兩個不同嘅「學位教師」人數）。零實測得益，卻令每次判斷同合成多食兩段內容，故撤回，只留註釋。
  - **E（採用）：逐行切片 ＋ 一條不經相似度嘅詞彙層查詢。** `chunk_overlap=0` 令每行自足；`searchEstablishmentRows()` 以「N 班的教學人員編制」作字面比對，命中即強制置前。**冇門檻可調**——該字串要麼喺片段入面，要麼唔喺。
- **Decision driver**: 班數係文件自身嘅索引欄，而稠密向量對唔到精確數字。凡係「同一份文件用一個鍵索引多行、每行只差幾個數字」嘅資料，相似度排序結構上分唔開；判斷閘亦分唔開（每一行喺佢眼中都係同一語域嘅完整句子，正是 S195 所述限制）。故槓桿唔喺任何一個分數，而喺「用文件自己嘅索引欄做字面鍵」。
- **Implementation**: `backend/src/lib/wikiRepository.ts` `searchEstablishmentRows()`；`backend/src/api/searchChannelB.ts` 第三個 overlay pass（觸發條件跟隨 `staffing` 路由，不另寫一次判斷）；`dev/vault/expand_vault.py` `chunk_overlap` 覆寫（接受 0，故另設 `source_override_allow_zero`）；`ESTABLISHMENT_SOURCE_IDS` 獨立於 `SOURCE_SETS.staffing`——字面比對只可以觸及「N 班的教學人員編制」確實代表一行表格資料嘅文本。
- **Evidence chain**: 逐層實測（路由 null → 加路由後仍拒答 → bypass 被強制置頂片段遮蔽 → 判斷提示改五版無效 → 換 `gpt-4o` 無效 → 打開原文發現片段由半行開始、判斷閘拒得啱 → 切乾淨後改為內插 → 加詞彙層先答啱）。最終真站實測：12 班得全日制 5 名學位教師、助理 14 名、合計 21 名，與原文逐字相符；24 班得 3 名副校長。過度觸發已收窄（「小一派位第 1 班點分」「中一 5 班嘅課程指引」「24 班學校要幾多間課室」所取得嘅 `staff_est_pri` 片段皆為 0）。
- **Uncertainty / 未做**: 一般化未做（Open Priority ④）；`coa_pri_e` / `coa_ss_e` 亦載編制條款，未逐一檢查有無同類問題；`staff_est_sp_sch_pri`（held_back）按「教學人員總數」而非班數索引，字面鍵要重新設計先可套用。

### ADR-00Y — 判斷閘與合成器分用不同模型（S211）
- **Date**: 2026-09-01（S211）
- **Status**: IMPLEMENTED + LIVE
- **Context**: 判斷閘（`RELEVANCE_JUDGE_PROMPT`）與合成器共用 `OPENAI_MODEL`（Render 設為 `gpt-4o-mini`）。判斷閘對「資料列明要求、問題問某資格符唔符合」呢類一步推論一律拒答，五個提示改寫版本皆無法扭轉。
- **Options considered**:
  - A：改寫提示 → ❌ 見上一則 ADR，凍結集零變化。
  - B：把 `OPENAI_MODEL` 整個換成 `gpt-4.1-mini` → ⚠️ 合成品質從未量度，而合成器係貴嗰邊（約 1,900 input ＋ 300 output tokens），全換約為現時 2.7 倍成本，且無實測依據。
  - **C（採用）：判斷閘用獨立 `JUDGE_MODEL`（程式預設 `gpt-4.1-mini`），合成器維持 `OPENAI_MODEL`。**
- **Decision driver**: 凍結驗收集實測——主集 31/33 打平、answer half 12/12 打平、decline half 19/21 打平且**為完全相同嘅兩個 false answer（D01、GN10），無新增虛答**；連 bare-noun 兩題計則 33/35 對 31/35，即 `S01` 與 `S02` 由誤拒轉為正確作答。判斷閘每次呼叫實測約 1,910 input tokens、1 output token，故改動每條查詢約增 US$0.0005（每月一千條查詢約 US$0.48）。程式預設而非 Render 環境變數，故無須改動部署設定。
- **Evidence chain**: 先以單一 query 見到 `gpt-4.1-mini` 準啲 → 明確指出「憑單一 case 揀 model 正是驗收集開頭警告嗰種 overfit」→ Leonard 指示照做 → 跑完整凍結集先落實。**注意**：該凍結集嘅 chunk cache 為 2026-07-31 版，已對 9/35 條漂移（`cache_drift.mjs`），故此結論對嗰 9 條而言係量緊一個舊狀態。
- **Uncertainty / 未做**: 合成器模型未量度；凍結 cache 未 refresh（需逐條重讀原文核 label）。

### ADR-001 — Channel B Downstream Integration Model (Q4 Phase 2)
- **Date**: 2026-06-05 (S144 model decision; S145 build + verified live)
- **Status**: IMPLEMENTED + LIVE
- **Context**: Channel A (`knowledge.json` @455 facts, frozen Q4 Phase 1) previously fed Circular System. Q4 Phase 2 = transition downstream to Channel B (Supabase `wiki_chunks` 10,594 chunks, pgvector).
- **Options considered**:
  - A: Export full snapshot (batch file) → ❌ conflicts with near-real-time freshness goal
  - B: Pure query-time API (downstream calls K1 `/api/search/channel-b` per query) → ⚠️ binds downstream to onrender free-tier (cold-start ~30s, 10 req/min/IP, no SLA)
  - **C (chosen): Incremental sync / manifest-diff delta feed** → downstream maintains its own vector index, polls K1 manifest for id-set delta, queries locally. Avoids both snapshot staleness and free-tier dependency.
- **Decision driver**: Downstream Circular System profile confirmed S145 = GitHub Actions ephemeral cron 3×/day + file-based numpy (NOT persistent service / NOT pgvector). Incremental sync avoids re-embedding 10K chunks per cron run; ETag/304 + delta minimises bandwidth.
- **Implementation**: `backend/src/api/channelBSync.ts` — `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`; X-Sync-Key gated; anon-REST; NO CORS; own 60/min + daily chunk budget. Contract = `dev/CHANNEL_B_SYNC_SPEC.md` v0.5.
- **Evidence chain**: S144 model selection (3 options, downstream profile gathering) → S145 downstream reply (embedding path-1 confirmed, 3 reverse-questions answered) → 5-lens adversarial review (40 agents, 4 real fixes) → live smoke PASS (anon reads `embedding` 1536-vec, all 13 fields present). Spec v0.3→v0.5.
- **Uncertainty / watch**: manifest O(N) full-table scan shares free-tier DB budget with live search (§8 spec); cache singleflight + TTL mitigates; monitor for 57014 degradation. Daily budget is soft (in-memory, resets on restart). anon key reading `embedding` column confirmed live (was load-bearing assumption until S145 smoke).
- **Rollback**: `git revert` channelBSync.ts + 2 route lines in server.ts; remove `CHANNEL_B_SYNC_KEY` Render env → endpoint returns 503. Supabase/Channel A/pipeline untouched.

---

# Project Decisions Log

這個檔保存項目的長期演進、決策、架構取捨與學習觀察 narrative。屬 warm 資料層 —— AI 開工**不需要讀**本檔。

🔹 短期 single-task project：本檔保持近空，你不需要 maintain
🔹 長期持續演進項目：AI 會在收工時先做維護觸發檢查；命中觸發或到定期兜底時才完整整理。當你問「我們之前為何這樣做」時，AI 會在這裡找答案

不需要你手動寫 —— AI 在收工時自動 update；重大決策可在發生時即時記錄，不必等到最後才回想。

Research-derived decisions use this compact evidence-chain format inside the relevant section, without creating a new section:

```text
- YYYY-MM-DD [research-derived] Decision summary. Evidence chain: Source=source:<id>; Summary=<source finding>; Inference=<reasoning>; Decision impact=<what changed>; Uncertainty=<limits or none>.
```

The `source:<id>` token must also appear in `dev/PROJECT_INDEX.md` under `Fact Base` or `External Sources`, so later sessions can trace the decision back to its source map.

This file does not store raw build / upload / QC evidence, current next actions, one-time task results, or reusable operating procedures. Keep those in `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, or the relevant rule pack / registered reference.

---

## Evolution Timeline

### S143 (2026-06-05) — Q4 Phase 1: Channel A Frozen
- `knowledge.json` stopped at @455 facts; schema unchanged; downstream zero-impact.
- Guidelines.json NOT frozen; continues live @152 v2.5.0.
- All Channel A endpoints remain (dormant); reversible via git revert docs.

### S145 (2026-06-05) — Q4 Phase 2 K1-side Complete
- Channel B sync endpoints built, adversarially reviewed, deployed, live smoke passed.
- Downstream (Circular System) to build its own consumer from spec v0.5 + sync key.
- Channel A remains frozen; Channel B search remains live; no data mutations.

---

## Decisions Archive

(empty)

## Insights & Learnings

### S212 — 一個永遠唔會紅嘅健康檢查，代價係全站停機半個鐘冇人知
- **Date**: 2026-09-03（S212）
- **What happened**: 為咗重抽 `phys_sss_2007_2015`，我先刪走佢 182 條舊片段，之後先發現 OpenAI 額度已經被同一 session 嗰 150 頁 OCR 耗盡 —— embedding 算唔到，該源變 0 條；更要緊嘅係**生產全站搜尋同時 429**，因為查詢要即時算 embedding。
- **Why nobody would have noticed**: `/health` 由頭到尾報 `ok:true`。佢只檢查 Channel A 快取，**唔掂 embedding 供應商，亦唔掂 Supabase**。要有人真係打一條查詢先發現得到。
- **Two root causes, and they are different**:
  1. **次序錯**：應該先驗「入得到」再刪舊嘅。我讀過 `cb3_deprecate_stale.py` 嗰套 DELETE→count verify，但從來冇問「入唔到會點」。
  2. **成本冇重新估算**：單頁探針嗰時我寫過「cost: trivial」，跳去 150 頁時直接沿用嗰個判斷，冇估算亦冇查餘額。**單頁探針嘅成本唔係全份嘅成本。**
- **What it became**: DOC_SYNC row 54（重抽既有來源並重入庫）第一條要求就係「刪之前先用一次真實 embedding 呼叫證明入得到」，第二條係「大量外部 API 步驟事前要估算並講出用量」。另 `qc_report` 新增 `SEARCH_PIPELINE_LIVE`（BLOCKER）：直接打生產查詢端點，429／回 200 但零結果／無回應都要紅，五條 self-test 有四條專證佢會紅。
- **The transferable lesson**: 紀律 #11「守門要證明佢會紅」本來已經寫咗，但只應用喺**新建**嘅守門上。`/health` 係舊嘢、一直綠、冇人懷疑過 —— **一個從來未紅過嘅健康檢查，同一個壞咗嘅健康檢查，喺輸出上完全一樣。** 舊守門同新守門一樣要證明佢會紅。

### S212 — 呈現層嘅缺陷，self-test 結構上捉唔到
- **Date**: 2026-09-03（S212）
- **What happened**: 封版閘喺公開頁面寫「未有 waiver **8** 項」，下面只列出 **6** 個名（`unwaived[:6]` 截斷，冇省略號）。係 Leonard 打開頁面睇出嚟嘅。
- **Why the tests were green**: `qc_report --self-test` 有 40 幾條斷言，驗閘嘅邏輯（會唔會紅、waiver 過期會唔會擋、`NOT_MEASURED` 算唔算未達標），**但冇一條驗「顯示出嚟嘅數同顯示出嚟嘅清單是否一致」**。self-test 驗計算，唔驗呈現。
- **Why it matters more on a status page than elsewhere**: 一個數字同佢下面嘅清單對唔上，讀者會**連兩個都唔再信**。對一張以「可信」為唯一價值嘅頁嚟講，呢種缺陷比顯示唔到更差。
- **The transferable lesson**: 凡有人眼會讀嘅輸出（狀態頁、報告、答案），**渲染完之後要有人真係睇一次**。自動化測試覆蓋唔到「睇落唔對路」呢個判斷。

### S198 (2026-07-30) — 一個工具嘅沉默唔係證據：落結論之前要先問「佢結構上量唔量得到？」

- **背景：** S197 交低一條阻塞項：「Leonard 去 Render Logs search `channel-a`，有流量就唔可以拆 route，冇流量就拆」。Leonard 依足做，畫面回「No matching logs」。**照字面讀，我可以即刻拆 route。**

- **證據鏈：** 冇當佢係零流量，改為驗證個儀器本身。三層：
  1. `backend/src/server.ts` 全檔只有三句 `console`（一句錯誤、兩句開機），**冇任何 per-request log** —— 成功請求結構上唔會印任何嘢。
  2. **對照組**：一個確實發生過嘅 `/health` request（我親手 curl、收到 200 JSON），search「health」**同樣零命中**。
  3. **正對照**：search `CORS` **搵到** `server.ts:396` 嘅開機輸出。→ stdout 收得到、request path 收唔到。
  4. **官方文檔**（<https://render.com/docs/logging>）確認機制：per-request log 係 **Pro workspace 以上**功能，呢個係 Hobby free instance。同時查到 Hobby log 保留期 = 7 日。

- **推論：** 「No matching logs」嘅資訊量係**零**，唔係「零流量」。而更值得記低嘅係：**同一個 session 入面我自己又犯多次同一個錯** —— 部署後我用 `/health` 嘅 `cache_a.warm` 去偵測重啟，行足 421 秒零命中，一度想寫「未部署」。實情係 Render 零停機部署會先暖好新 instance 先切流量，**外部永遠見唔到 `warm=false`**。真憑據係 instance id 變咗（`pcwrl`→`p2znr`→`26wlj`）。即係話「信一個量唔到嘢嘅工具嘅沉默」呢個陷阱，就算啱啱先踩過、明知要防，**一個鐘之內照樣再踩**。

- **點解呢個形態特別難自己捉到：** 兩次沉默都指向**我想要嘅答案**（冇流量 → 可以拆；同 S195／S196／S197 三次一樣，錯嘅方向都係對自己有利）。一個順住你意思嘅結果唔會覺得可疑，所以靠「察覺唔妥」係捉唔到嘅，只能靠一條硬規矩。

- **決策影響：** (a) DOC_SYNC 新增 row「臨時觀測 code 加落既有 backend route」，驗收欄硬性要求 **negative control**（一條唔應該中嘅鄰近 route 必須零行）同**部署確認要用帶序號嘅自測流量**，唔准靠猜重啟；(b) 呢條規矩寫埋落 `server.ts` probe 嘅註釋，因為 handoff 會被重生、code 唔會；(c) 可操作嘅版本：**面對一個 negative result，先問「如果目標訊號真係存在，呢個工具會唔會顯示到？」—— 答唔到就搵一個已知發生過嘅事件做對照組，答案未出之前唔准落結論。**

- **不確定性：** 呢次係靠一個現成嘅已知事件（我自己杯 `/health` curl）做對照組先拆穿到。**唔係每個情境都有現成對照組**；冇嘅時候要主動製造一個，而製造對照組本身嘅成本未量過。另：Render 文檔講嘅 plan 分級係 2026-07-30 讀嘅，plan 政策可變。

### S197 (2026-07-29) — 機械判定唔可以取代讀原文：同一個形態第三次出現，今次量到咗個失敗率

- **背景：** Channel A 退役量度。Leonard 定嘅標準係「已喺 Channel B 或可追蹤出處就可以退」。我建咗一個逐條量覆蓋嘅工具，跑完 455 條，交出一個「已清除可退」嘅 tier。

- **證據鏈：** 個 tier 提供 16 條「有可引用替代品」候選。逐條打開替代段落嚟讀之後，**只有 9 條過關，7 條失敗（44%）**。七條唔係同一種錯：
  - 段落講**另一個科目**（事實講「人文科科主任 30 小時」，段落講小學**科學**科 30h/15h）
  - 用一個**定義**冒充一條**規則**（事實講「全方位學習津貼須用於…」，段落只係「五種基要學習經歷」嘅定義）
  - 實質內容有但**職責歸屬冇**（事實寫「[活動主任] 負責統籌」，段落寫「其他學習經歷委員會由**副校長**帶領」）
  - 所謂替代品係一份**問卷通告**（而問卷本身就係另一個已知嘅假覆蓋來源）
  - 兩段完全唔相干（事實講學校發展津貼 8 月發放，段落講午膳撥款同 IT 設備）

- **推論：** 呢個係同一形態第三次出現 —— S195 用自己揀嘅 phrasing 做可達性 probe（量度緊 phrasing，唔係檢索）；S196 借用為 vault 門檻而設嘅測試集去量 footnote（量度緊另一個問題）；S197 用「錨點齊集喺同一段」去代替「呢段真係講緊同一件事」。**三次都係用一個機械代理去頂替一個語意判斷，而三次個代理都喺對自己有利嘅方向出錯。** 分別係今次量到咗數字：44%。

- **決策影響：** (a) 個 retired list 只收人手讀過嘅 9 條，紀律直接寫喺 `searchChannelB.ts` `RETIRED_MIRROR_CHUNK_IDS` 上面（「唔准由總帳直接延長，每條要開段落嚟讀」），因為下一個想加 id 嘅人會睇 code 而唔係揭 log；(b) DOC_SYNC 新增「store chunk 退出服務路徑」row，把「先確認 eval 集覆蓋到被剷內容嗰個維度」寫成硬性檢查 —— 本 session 原 30 條 eval 對「邊個負責」完全盲，剷咗會量到零回歸而個綠燈係假嘅；(c) 總帳嘅 133 CLEARED / 107 PROVISIONAL / 172 UNVERIFIED 一律**唔可以當可退**。

- **另一條同樣可轉移嘅：剷嘢之前要分清「有替代品」同「係唯一來源」。** 我憑一條 query（「採購門檻」rank-0 係無出處鏡像壓住 `g01` p.5）就提議整批剷走 109 條，並講「拎走唔係損失」。量埋成批：93/109 冇已證替代品，而且大部分係 `[角色] 負責…` 呢種**語料結構上唔會有**嘅形態（EDB 原文唔會寫邊個職位負責咩）。live 實測「訓導主任 社工」鏡像佔 rank 0/1、語料最近似段落講跨部門聯繫而唔講邊個負責。**一個有真實缺陷嘅實例，唔代表成批都係同一個缺陷。**

- **不確定性：** 44% 呢個數嚟自 16 條樣本（即 ±12 個百分點以上嘅波動空間），而且嗰 16 條係 tier 入面**分數最高**嗰批（有硬錨點齊集）。其餘 133 條 CLEARED 嘅真實失敗率**冇量過**，冇理由假設佢會低啲。

### S195 (2026-07-27) — 三條可轉移教訓：內容雜湊 id 的刪除陷阱、可達性 probe 的自欺、以及一個「唔可以靠調參解決」的安全門檻

- **背景：** 兩輪 session。上半清三條死連結（Leonard「跟你建議」），下半清埋餘下 8 項優先事項（Leonard「全做」）。Supabase 16,035 → 16,062，registry 250 → 256，凍結合約全程零接觸。

- **教訓 1 — chunk id 係內容雜湊時，「刪舊版」唔可以照 `source_id` 刪。**
  - 兩次遇到（`g18` 校車指引改版、`g21`/`g22` 重抽）。chunk id = `vault_<source_id>_<text_hash>`，所以**兩個版本之間文字冇變的段落，id 完全相同**。`g18` 舊 9 條入面有 **3 條**同新版 id 重疊；照 `source_id` 一次過刪就會連現行有效內容一齊刪走，**而且刪完之後總數睇落仲會「啱數」**（因為新版已 upsert 入去），完全唔會爆。
  - **決策：** 刪除集一律 = **舊 id 減新 id**，並且要**排除唔屬 vault 的 content_type**（`g21`/`g22` 各有一條人手寫的 `footnote_curated`，照 source_id 刪就會毀掉人手內容）。兩條刪除腳本都把刪除集**寫死入檔**而唔係執行時重算，免得日後 vault 檔一改就漂。
  - **可轉移原則：** 凡係 content-addressed 的 store（id 由內容決定），「更新一份文件」唔係一個 delete-then-insert 的原子操作，而係一個**集合運算**。用 id 前綴或外鍵去刪，等於假設 id 同文件係一對多的乾淨關係 —— 內容雜湊剛好打破呢個假設。呢類錯誤靜默、事後數字仲對得上。

- **教訓 2 — 用自己揀的 phrasing 去測「搵唔搵得到」，量度緊的係 phrasing，唔係檢索。**
  - 想剪 spotlight overlay（S193 為「新入源被全庫 ANN 擠走」而建）。我寫咗個可達性 probe：對每個源用代表性 query 打全庫 ANN（top-40、min_score 0.22），睇佢入唔入到候選池。6 個源有 4 個 **rank 0**，睇落好明確 —— 於是剪走。
  - **before→after eval 即刻打面**：`ai_intro`／`net_scholar`／`pay_adjust` 三條由 PASS 變 FAIL，失去的**正正就係被剪那三個源**。
  - **根因：** 我用的係自己揀來描述該文件的 phrasing（「人工智能初探 學與教」），而真正重要的係用戶打的**裸名詞**（「人工智能初探」）；加上生產路徑會先做 query expansion 再 embed，所以我個 probe 睇到的候選池**根本唔係生產那個池**。probe 對自己友善，因為 probe 係我寫的。
  - **決策：** 任何 spotlight／SOURCE_SETS／route 次序改動，**一律以 eval before→after 對為準**，唔接受可達性 probe 作證據。教訓寫入 `SPOTLIGHT_SOURCE_IDS` 註釋（改嗰個人一定睇到），失敗那份 run 保留入 `dev/source/eval_runs/` 做證據。
  - **可轉移原則：** 自製的驗證器同被驗證的系統共享你嘅假設 —— 尤其當輸入（query）由你揀。要證明「用戶搵到」，就要用**用戶的輸入分佈**，唔係你嘅。S194 個監察漏咗自己要捉的案，係同一個 class 的錯：**你只係測到自己嘅假設**。

- **教訓 3 — 有些安全門檻唔係「調得啱唔啱」，而係「調唔調得到」。**
  - S183 把 anti-confab judge 的 `vault_extract` bypass 定喺 cosine 0.70。此後入庫的源喺自己主題上只得 0.62–0.63，被拒答，睇落就係門檻定得太高。
  - 冇直接調，先起 `dev/source/judge_probe.py` 量 24 條：6 條完全離題、**14 條「貌似學校事務但答案根本唔喺庫」**（呢類先係會誘發砌數的，S177 砌出「IMC 60%」就係呢類）、4 條正面對照。
  - **結果：敵意類最高 0.632、真命中最低 0.624 —— 兩個分佈重疊。** 降到 0.60 會放行「教師每年可以請幾多日大假」(0.617)、「學校可唔可以借錢俾教職員」(0.615)、「校服供應商招標要幾多間報價」(0.614)：全部語域啱、個數字唔存在。
  - **決策：保留 0.70**，並把實測數字寫入 `searchChannelB.ts` 註釋（唔止留喺 log）。要提升 recall 只剩改 judge prompt 一條路（選項 c），而 `judge_probe.py` 本身就係現成的驗收工具：目標 = 4 條 control 答到、20 條敵意仍拒答。
  - **可轉移原則：** 當一個訊號的「真陽性」同「危險假陽性」分佈重疊，**冇任何門檻數值可以同時滿足兩邊**；再調只係喺兩種錯之間換位。呢個時候應該去**換訊號或換判斷器**，唔係繼續調參。而且要證明呢一點，敵意樣本必須包含「同語域但無答案」那類 —— 只用完全離題的樣本（本次最高只有 0.418）會得出「門檻可以大幅降低」的錯誤結論。

- **同場加映 — 監察要 alert on diff，唔係 alert on count。** 封面核對（S194 建）今次接入 CI 時發現：全掃 flag 18 條而**全部良性**，用 severity 做 gate 會每次跑出 11 個假警報，正正係 S191 花力氣收走的 email 噪音。改為同一份**人手覆核過的 baseline**（`title_baseline.json`）比對，只有「新出現的 flag／覆蓋率跌 ≥0.15／fetch 失敗」先開 Issue；接受一個 flag 的方式就係更新 baseline。實測：加咗 6 個新源、改咗 3 個標題之後 rescan **0 alert**。

### S194 (2026-07-26) — 兩條可轉移教訓：「200 ≠ 正確文件」＋「append-only 歷史唔可以做 sync 目標」

- **背景：** Leonard 叫我核一份 technology-edu 頁面上未入庫的 PDF 是否 `ict_sss_2021` 的新版（原以為係 supersede 小事）。核出的係：該 registry entry 標題寫《資訊及通訊科技（中四至中六）2021》，`url_primary` 卻指向 `CS_CAG_S4-6_Chi_2021.pdf` —— **`CS` 被讀成 Computer Science，實為 Citizenship and Social development**。81 個《公民與社會發展科課程及評估指引》的 chunks 長期掛住 ICT 標題供用戶檢索（生產實測：搜「公民與社會發展科」，top-1 結果標題係「資訊及通訊科技」），而真正的 ICT 2021 指引從未入庫。

- **教訓 1 — HTTP 200 唔係「文件正確」的證據，兩個既有監察都結構上盲。**
  - `check_freshness.py` 問的是「上游 bytes 有無變」，`check_served_urls.py` 問的是「用戶點落去的連結通唔通」。兩者對呢個 entry **年年都綠**：URL 一直活、一直穩定、一直 200 —— 只不過係另一份文件。**冇一個監察問「呢份係唔係你以為的文件」。**
  - **決策：** (a) 入庫紀律 —— 登記或改指任何來源前，必讀 PDF **封面**並對照 registry 標題；檔名縮寫唔算證據（`FRESHNESS_GUIDE.md` §1a）。(b) 建第 5 監察 Method C `check_source_titles.py` 做安全網（確定性 CJK bigram 比對**主題核心**：剝走學段／年份／樣板，因為「中四至中六」「二零二一年」「課程及評估指引」全庫共用，留住的正正係分辨主題的部分）。**唔用 embedding** —— 兩份 EDB 課程指引語域幾乎相同，cosine 會糊化正正需要的分辨力，字元 bigram 反而字面、免費、可重跑。
  - **首跑結果（192 個 PDF 源）：冇第二個指錯文件**；17 條 flagged 全部良性。即係呢個 bug 係孤例，但孤例造成的用戶可見錯配足以構成常設檢查。
  - **自身教訓（值得記）：** 監察 v1 **會 miss 佢自己要捉的案** —— `best_coverage` 取所有標題變體的最大值，而 `title_short`「ICT課程指引2021」去噪後只剩「ICT2021」，個「2021」撞正公社科封面的「由2021/22 學年」→ 假高分 0.500 判 ok。**新監察必須用「已知真陽性」做回歸測試，否則你只係測到自己嘅假設。** 修法後校準由 0.468/0.298（margin 0.017）改善到 **1.000/0.000**。

- **教訓 2 — append-only 歷史檔永遠唔可以做 number-sync 的目標。**
  - display-sync（chunk 總數鏡像）原本用全檔字串取代，目標包含 `CHANGELOG.md` 同 `dev/CODEBASE_CONTEXT.md`。結果**每次入庫都靜默改寫過往條目**：到 S194 發現 S186 的 changelog 條目寫成「15,656 → 15,901（淨 +182）」—— 算術上不可能；另有 5 條 AI 維護日誌記載了發生在該 session **之後**的總數。污染早於 S194，累積多個 session 無人察覺（因為冇人會 diff 舊條目）。
  - **決策：** 兩檔由 `execute_ingest.py` `DISPLAY_SYNC_TARGETS` **移除**。入庫應該向歷史檔**追加一條新條目**（本來就係佢哋的用途），而唔係重述當前狀態。加入該 list 的檔案必須只承載當前值；若同時承載歷史，就唔屬於該 list。
  - **可轉移原則：** 自動化「同步一個數字到 N 個地方」時，先問每個目標係**當前狀態鏡像**定係**歷史紀錄**。前者可以盲改，後者盲改就係篡改。呢個 class 的 bug 完全靜默 —— 唔會爆、唔會 fail CI、只會令你日後信錯自己嘅記錄。

- **同場加映（R5 審計順帶）：** handoff 寫住 sibling repo `EDB-AI-Circular-System`「亦 public、待審」，實際已轉 private 並另開 public 成品 repo `edb-circular-site`。**治理文件對外部世界的斷言同樣會 drift**，read-only 核實成本極低（一個 `gh repo list`），值得每次審計先做。

### S183 (2026-06-25) — 2 governance rules ship：Supersede ranking penalty 0.05 + Judge bypass extension to vault_extract
- **背景：** S183 ingest VE_CF 2026 主框架 93 chunks + EDBC 3/2026 + EDBCM 221/2025 智啟學教（淨 +108 chunks → 15,644）。Post-deploy Leonard mobile screenshot 反饋 + short-query verification 揭發 2 個 governance-class issue 需要 long-term rule，而非 one-off patch。

- **Rule 1 — Supersede ranking penalty 0.05（Leonard 提出）：**
  - **問題：** Retain-but-rank-down 策略下，舊版（如 values_edu_framework_2021_trial cos=0.794）cosine 自然分高過新版（VE_CF_2026 cos=0.753 差 0.041），令 user 查「價值觀教育」短 query 仍 surface 舊版主導 top-5。
  - **決策：** Backend `searchChannelB.ts` +`SUPERSEDED_IDS` Set + `SUPERSEDE_PENALTY=0.05` const + `applySupersedePenalty()` helper；apply 兩次（main results post-mapping + footnote overlay pre-lead-detection、re-sort 後）；對全 channel（vault_extract + footnote_curated + role_facts）統一 apply。
  - **Penalty 值選擇：** 0.05 empirically — 足夠 swap rank（2021 0.794 → 0.744 < 2026 0.753），但保留 retrieve 命中（學校過渡期仍可能引用舊版）。Below penalty 仍 surface 即係新版 cosine 低過 0.041 + 舊版差太大、retrieve 自然偏好舊版相關度（acceptable）。
  - **SSOT 雙處：** registry `superseded_by` field（authoritative）+ backend `SUPERSEDED_IDS` Set（runtime cache）。Future ingest 新 superseding 版時必同步雙處（同 SOURCE_SETS pattern 一致：每次 manually sync）。
  - **未來擴展點：** 如有更多 superseded sources 累積、可考慮：(a)load registry at startup 自動 build set；(b)`superseded_by_chain` 多層；(c)graduated penalty (例如 2021→0.05、2018→0.08)。當前 KISS 一刀切 0.05 sufficient。
  - **Verified：** 3/3 短 query「價值觀教育」「首要價值觀」「12 首要價值觀」VE_CF 2026 rank 0/1/2、2021 試行版 demoted rank-3+。

- **Rule 2 — Judge bypass extension to vault_extract @ score≥0.70（解 anti-confab over-decline）：**
  - **問題：** S177 anti-confab judge（synthesizeAnswer 之前 binary relevance gate）對 vault_extract chunks 過保守 — 即使 rank-0 score 0.75+（empirically direct topical match）仍 over-decline「未能找到」。Leonard mobile screenshot 報告：「智啟學教是什麼」EDBCM 221 rank-0 0.750 + 「價值觀教育」VE_CF 2021 rank-0 0.794 全 over-declined。
  - **既有 fix（S178）：** footnote_curated lead score ≥ FOOTNOTE_LEAD_SCORE (0.45) bypass judge（hand-curated verbatim-verified direct answer by construction）。但 vault_extract 唔屬於該 class。
  - **決策（S183 擴展）：** +`VAULT_LEAD_SCORE = 0.70` 同 footnote-lead pattern：vault_extract lead score ≥ 0.70 bypass judge。Below 0.70 仍經 judge full protection。
  - **Threshold 0.70 選擇：** S177 凍結教席→IMC-60% confab class 嘅 cosine 喺 **0.55-0.65** range（topically-near-but-wrong）；≥0.70 empirically direct topical match（vault chunks at this cosine reliably answer the query）。0.70 是 confab 同 direct-match 分界 empirical line。
  - **Behavior：** Confab protection retained for marginal cosine 0.50-0.65 case；high-cosine direct match no longer false-decline。3/3 Leonard user query post-fix ANSWER + grounded synthesis。
  - **未來監察：** Monitor false-positive synthesis (vault-lead bypass 但實際 confab 漏網) — 如出現可微調 threshold up 至 0.75。

- **配套 procedural learnings：**
  - **Pre-ingest grep discipline：** S183 漏 catch prior `edbc003_2026` 因為齋 grep brand variant「VE_CF / 價值觀 / value_education」而 prior registry title 短「教育局通告第3/2026號」未含 keyword。Future ingest 之前 grep registry 必同時用 (URL filename pattern + 中文 title keyword + brand variants)。
  - **Short-query verification mandatory：** Per memory `feedback_short_query_first`、real user type 2-4 token query；S183 7+ token long-sentence smoke test 7/8 PASS 但短 query 仍 fail（routing OK 但 judge 過保守）。Post-deploy QC 必驗 2-4 token 短 query。
  - **Pages transient outage remediation：** Pages build/report OK + deploy step fail 4s = GitHub Pages 短暫 outage；standard remediation = empty commit retrigger 即修；workflow status 用 public REST API `https://api.github.com/repos/<owner>/<repo>/actions/runs` 查（公開 repo no auth needed）；gh CLI v2.95.0 已裝、`gh auth login` 後可 read private workflow annotations。
  - **Commits 鏈：** `bc26d41`→`edebbbd`→`40923d5`→`a718a83`→`1359916`→`71f1c80`→`4ddffb6` 全 push origin/main、Render 4 round redeploy + Pages #398 success。

### S176 (2026-06-22) — Agent Handoff Kit v0.3.29 升級：雙治理層共存決策
- **背景**：本專案原用自寫治理（`AGENTS.md` `<INSTRUCTIONS>` §0–§14：PLAN→READ→CHANGE→QC→PERSIST、3-section closeout、`### Next Session Handoff Prompt (Verbatim)` 機制），已運行 175 sessions。S176 升級 Agent Handoff Kit v0.1.7→v0.3.29。
- **決策**：**兩套治理層共存、不取代**。AHK managed-core 追加喺 `<INSTRUCTIONS>` 之後（managed-core BEGIN/END 包圍）；原 §0–§14 全保留。理由：(1) 自寫治理含產品專屬鐵律（凍結合約、display-sync 8 點、Supabase INSPECT 授權、node-fetch pin）AHK 無法涵蓋；(2) AHK 提供 doctor 可驗結構 + rule packs + 機器標記（`ack:`）跨工具續傳。兩者互補。
- **衝突解法（已採用）**：closeout 機制兩者並行——本專案 3-section 輸出（含 `### Next Session Handoff Prompt (Verbatim)` 寫入 SESSION_LOG）+ AHK `START_NEXT_SESSION_PROMPT.txt`（由 handoff `Next Session Opening Message` 區塊重生）。S176 entry 同時保留兩種 startup 區塊。
- **git 追蹤更正（S176 closeout 發現）**：`dev/SESSION_HANDOFF.md`／`SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore`，但**實際已 git-tracked**（早於 ignore 規則就 commit；`.gitignore` 唔會 untrack 已追蹤檔）。故 S173–S175 每次收工都照常 commit 三者。升級 commit `788538e` 當時誤判為「不入 git」而漏 commit handoff/log 改動 → S176 收工 commit 補回。stale `.gitignore` 規則屬低優先 cleanup（移除該行 or `git rm --cached`，需 Leonard 定）。
- **衝突原則**：AHK core §5「兩 pack 衝突取較安全、較可驗路徑並記錄」。未來如兩層指令矛盾，取較安全可驗者，收工記錄。
- **可驗收據**：`npx @adamchanadam/agent-handoff-kit@latest doctor --root .` → `status: passed`（48 項）。升級備份＋migration report 在 `dev/governance_migrations/20260622T141715Z/`。
- **教訓**：升級遇 2 衝突檔（SESSION_HANDOFF/LOG 因舊自寫格式缺 `ack:` 標記）係**預期**、非錯誤——installer 故意唔覆寫，留 AI 非破壞性補標記（section markers 要放對語義區段，唔可以淨係 cluster 喺檔頭，否則 doctor semantic-placement check 唔過）。
