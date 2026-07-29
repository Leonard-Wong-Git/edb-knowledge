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

## 2026-07-29 Session 197 — Channel A 退役：量度「Channel B 食唔食得晒」，答案唔喺覆蓋率，而喺 Channel A 自己載住乜

- **ID:** Claude_20260729_S197
- **Summary:** Leonard 問 roadmap → 我指出 R1/R5 已過時、R3 卡喺一個文件互相矛盾嘅前提。Leonard 提出退役標準「已喺 Channel B 或可追蹤出處就可以退」→ 我建工具量度 455 條 → **兩次推翻自己**（一次係把尺壞咗、一次係由一個實例推去成批）→ 最後只退咗前端路徑 + 9 條有已證出處嘅鏡像 chunk。backend 兩條 route **未郁**，卡喺 Leonard 未覆嘅 Render logs。
- **起手探針 4/4 綠:** served `app.html` `PLATFORM_VERSION 3.2.2` + index 200 / Render `/health` `cache_a.warm=true size=455` / HEAD==origin/main `523f5db` tree 乾淨 / Supabase `content-range 0-999/16062`。
- **量度設計上兩個唔講就會出假數嘅決定:**
  1. **「輸出完全一樣」唔係可用標準。** Channel A 事實係冇 URL 冇頁碼嘅裸句（實查 `role_facts.json`：455 條散喺 47 個〔範疇×角色〕桶，`_source_refs` 只喺範疇層），Channel B 出原文＋URL＋頁碼，兩者永遠唔會一樣。改為量「substance 覆蓋」。
  2. **必須剔走語料入面 Channel A 自己嘅鏡像。** `wiki_chunks` 16,062 = `vault_extract` 15,721 + `footnote_curated` 206 + `approved_fact` 109 + `stat_fact` 26（逐類點過、總和相符）。嗰 109 條**逐字係 455 條嘅子集**（精確字串比對 109/109 命中、0 條外來），同 26 條 stat_fact 一樣 **url 全空**。唔剔走，攞事實去搵第一個命中就係佢自己 @0.828 → 會量到「455/455 全覆蓋」，而個數純粹係「問題就係佢自己嘅答案」。
- **Changed:**
  - **新工具 `dev/source/channel_a_coverage.py`**（self-test 34 項，含兩條「故意整壞證明守衛會 FAIL」）：embed 455 條 → RPC 取 40 條 → 濾剩文件語料 → 硬錨點（金額／日數／%／條號）比對，**錨點必須齊集喺同一段**（散落兩份文件 = S177 砌數形態，唔收）；lexical 層自帶對照組；傳輸失敗歸 `ERROR` 永不當「冇覆蓋」。
  - **`dev/source/CHANNEL_A_RETIREMENT_LEDGER.tsv`**：455 條逐條 tier + 已核實出處 + 頁碼。
  - **`app.html`**：移除 `runChannelA` / `runCombined` / `searchChannel` / `qaRole` / `channelACount` / `CHANNEL_OPTS` / `highlightFact` + tokens / Channel A 角色選單 / 兩個死 caption（−109/+8 行）。
  - **`backend/src/api/searchChannelB.ts`**：新 `RETIRED_MIRROR_CHUNK_IDS`（9 個 chunk id，逐個附已核實出處註釋）+ `retiredMirrorFilter`，套落三個 `toChannelBResult` 映射點。
  - **`dev/source/eval_queries.json`** 30 → **34**（新增 4 條角色職責 query）。
- **Done:** commits `c01e646`(量度) → `596e383`(總帳) → `2d70ef7`(前端) → `5754c00`(eval 補盲) → `3ba92fe`(9 條鏡像退役) → `d554b4c`(記錄) → 本 closeout commit。
- **QC:**
  - **eval 34 條 before→after**：`_before34b` PASS 23 / FAIL 0 / errors 0 → `_after` **PASS 23 / FAIL 0 / errors 0，0 blocking failures**，32 條完全相同。
  - 唯一 `SET_ADDED` = `procurement` 加入 `subvention_tips` —— 鏡像讓出嘅位由**佢自己嘅可引用正版**補上，正是預期效果。
  - `bus_escort` `RANK_SHIFT`：來源集不變、第 4/5 位對調，同 9 條改動扯唔上；符合設計容許嘅 ANN tie flip，**未獨立證實成因**。
  - **live 抽驗**：「採購門檻」rank-0 由 `role_facts_finance`（url 空 / page null）變 `g01` **p.5**；「連續缺課 呈報」「十二種首要價值觀」top-8 鏡像歸零；「訓導主任 社工」鏡像**完整保留** rank 0/1（設計意圖）。
  - 前端 live 驗：served `app.html` `runChannelA`/`runCombined`/`searchChannel`/`qaRole`/`CHANNEL_OPTS`/`search/channel-a` 全部 **0**；1280px 重載 console 零 error、`select` 數 0；Channel B 搜尋 HTTP 200 / 7 條 / synthesis 正常。
  - tsc exit 0 ×2；Supabase 16,062 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / v3.2.2 **全部零接觸**（Supabase 零寫入，只加 code 層 filter）。
- **兩次推翻自己（本 session 最有價值嘅部分）:**
  1. **把尺壞咗。** 首輪報「8月15日前提交假期表」搵唔到錨點；打開 `g11` 一睇：「於每年**八月十五日**前……呈交下一學年的學校假期表」——**同一條規則，中文數字寫**。首 29 條入面 10 條同一原因。加 `fold_cn_numerals`（處理「二零二五」=2025 同「三十」=30 兩種讀法）離線重判：**71 條轉桶，COVERED 100 → 149**。⚠️ 方向性：呢個 bug 令工具**系統性高報缺口**，而每個假缺口都係「唔可以退 Channel A」嘅理由 —— 修之前個數會令「保留」睇落更有道理。
  2. **由一個實例推去成批。** 我見到「採購門檻」rank-0 係無出處鏡像壓住 `g01` p.5，就提議**整批剷走 109 條**、並講「拎走唔係損失」。量埋成批之後：**93/109 冇已證替代品**，而且大部分係 `[角色] 負責…` 呢種語料唔會有嘅形態。live 實測「訓導主任 社工」鏡像佔 rank 0/1、語料最近似（`g16` p.17）講跨部門聯繫而唔講邊個負責；「活動主任 職責」頭四名三個係鏡像。**剷走真係會蝕。** 已喺報告同 commit message 更正。
- **另一個必須記低嘅數字：機械判定 `CLEARED` 有 44% 撐唔住人手覆核。** 總帳提供 16 條「有可引用替代品」候選，逐條讀完**只有 9 條過關**。7 條嘅失效模式各異：段落講另一個科目（人文科 vs 小學科學）／用「五種基要學習經歷」嘅**定義**冒充津貼用途**規則**／實質內容有但**職責歸屬冇**（段落講「其他學習經歷委員會由副校長帶領」，事實寫「[活動主任] 負責」）／所謂替代品係一份**問卷通告**。**規則已寫入 `searchChannelB.ts` 該常數註釋：唔准由總帳直接延長個 list，每條都要開段落嚟讀。**
- **eval 集本來對呢個改動完全盲（已修）:** 原 30 條**冇一條** expect `role_facts_*`、冇一條問「邊個負責」→ 剷走鏡像會量到零回歸，而嗰個綠燈係假嘅，同 S195 spotlight prune 撞板同一形態。加 4 條角色職責 query 後，其中 2 條（`senco_role`/`curr_coord_role`）**由 baseline 證實我釘錯咗預期**（語料 `g19` p.13/p.57 先係服務緊 SENCO 嗰個），已即時更正而唔係留住一個永久紅燈（S195 十一個假警報嘅教訓）；`curr_coord_role` 改 RECORD_ONLY —— 冇任何來源答得好，釘任何一個都係把爛答案封為正確。
- **順帶揪出、未處理:** 3 條 Channel A 事實**同現行《學校行政手冊》直接矛盾**（病假「36天」vs `sag_2025_11` 附錄9「首年28天／其後48天／累積168天」；非教學人員年假「18/21/24天」vs「7天起、上限14天」）。**已查證呢 3 條唔喺 Supabase**（store 含「36天」嘅 `approved_fact` = 0），所以唔會經 Channel B 出街，只可經 `/api/search/channel-a` 攞到 → 會隨 backend route 退役一齊斷。另：455 條入面有問卷題、活動統計、殘缺片段（「取得校長批准。」「2013年4月1日作出修訂。」← 已鎖定來源係 `coa_imc_1_19` 嘅修訂註腳欄）、簡體字同日文漢字「関」等抽取瑕疵。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S197 block；量度方法＋兩次自我推翻＋44% 覆核失敗率→`dev/source/CHANNEL_A_COVERAGE_FINDINGS.md`（可重用程序知識，唔止留喺 log）；逐條 tier + 出處→`CHANNEL_A_RETIREMENT_LEDGER.tsv`；三份 eval run→`dev/source/eval_runs/`（commit，跨 session 可比）；**「唔准由總帳延長 retired list」呢條紀律→`searchChannelB.ts` 該常數上面嘅註釋**（下一個想加 id 嘅人一定睇到）；run JSON + embed cache→gitignored（14MB／4MB，可由工具重生）。
- **Sync:** DOC_SYNC 命中 2 row（檢索 eval harness 改動 ✓ eval_queries 30→34＋三份 run＋before→after 對／**新增 1 row「store chunk 退出服務路徑」** ✓ 按 anti-pattern guard 先補行）。`update_log.json` **N/A**（零入庫、純服務路徑改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 隨 `app.html` push redeploy（已驗）；Render deploy 1 次（已驗）。
- **Pending:** backend `/api/search/channel-a` + `/api/search/combined` 未退（阻塞前置＝Render logs `channel-a` 流量，Leonard 未覆）；總帳 **172 條 UNVERIFIED + 107 條 PROVISIONAL** 未逐條讀；133 條 CLEARED 未抽樣覆核。
- **Risks:** ⚠️ 按 44% 覆核失敗率，`CLEARED`／`PROVISIONAL` 兩桶**唔可以當可退**。⚠️ 100 條無出處鏡像仍然喺 Channel B 服務路徑，「答案必有出處」呢條護欄喺佢哋身上仍然穿窿 —— 但佢哋係「邊個負責」嘅唯一來源，唔可以照剷。⚠️ 文件三處對「下游有冇轉 Channel B」講法不一致（PMS §F.11 話已轉／roadmap R3 當未確認／§F.2 話待協調），而 `CHANNEL_B_SYNC_KEY` 實測**已配置**（probe 得 401 `missing X-Sync-Key` 而非 503 `sync disabled`）—— 呢個只證明 key 設咗，證明唔到下游用緊。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → **trigger=False**（line_count=381 / entry_count=6，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 「機械判定唔可以取代讀原文」屬跨 session 累積模式（S195 spotlight probe／S196 借錯測試集／本次 44%），已按 §4 step 11(c) 寫入 `dev/PROJECT_DECISIONS.md` Insights 而非只留喺 log。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS。）

<!-- ack:log-entry:end -->

---

<!-- ack:log-entry:start -->

## 2026-07-28 Session 196 — handoff 講嘅根因係錯嘅：「校巴營辦商責任」唔係 route 次序，係 curated footnote 搶咗 lead slot 兼跳過 anti-confab judge

- **ID:** Claude_20260728_S196
- **Summary:** 起手探針 4/4 綠 → 我建議做 Open Priority ②（校巴 route 次序）→ Leonard「go」→ **READ 階段用 code + live 證實 handoff 記錯根因，按 §3 停低報告** → Leonard 揀 C（A+B 一次過做）→ 我保住歸因，逐個改動各自一對 eval/probe，共 4 次部署。
- **§3 停低（值得記低）:** `detectQueryCategory("校巴營辦商責任")` 一直都返 `safety`，六種校巴 phrasing 全部一樣。改 TOPIC_KEYWORDS 次序會係 **no-op**。真根因喺兩層：(1) `SOURCE_SETS.safety` 同時載住 `sag_2025_11`（學校行政手冊 215 chunks），佢嘅籌款／捐款／供應商段落 0.602/0.535/0.529 壓過 `sch_bus_operators_2026` 0.506；(2) 兩條 `footnote_curated` 靠 `FOOTNOTE_LEAD_SCORE=0.45` 攞咗 rank 0/1（0.518 小賣部經營利潤、0.495 承辦商 SCRC），**而 footnote lead 會跳過 anti-confab judge** → 出街答案講「校巴經營利潤必須運用於學生的直接利益」。即係話呢條唔止排名差，係**答錯嘢**。
- **Changed:**
  - **A（`school_bus` 專屬 route）**：`SOURCE_SETS.school_bus` = g18 + 5 份 2026/27 姊妹指引；bus tokens 由 `safety` **搬**過去（唔係複製）；新 `QUERY_EXPANSIONS.school_bus`。
  - **A'（修 expansion）**：第一版 expansion 塞晒六個受眾名詞（司機／營辦商／跟車保母／家長），eval 即刻捉到「跟車保母」由 escorts rank 0 跌落 operators rank 0 —— 姊妹之間唯一嘅分別詞被自己洗走。改為只留共通詞彙。
  - **B（footnote lead 加 lexical gate）**：新 `backend/src/lib/textBigrams.ts`（`cjkBigrams` 由 `checklistRevise.ts` 搬入 lib 並 re-export，避免 lib→api 反向依賴）＋ `wikiRepository.footnoteInformativeBigrams()`（喺常駐 footnote 語料上做 DF 校準）；footnote 要同 query 共享 ≥ `FOOTNOTE_LEAD_MIN_OVERLAP` 個 informative bigram 先攞得到 lead slot；judge bypass 由「邊個坐 rank 0」改為綁定「gate 批准咗嘅 lead」。**被拒嘅 footnote 唔會被刪，照按分數 merge —— 收走嘅只係特權。**
  - **B'（1 → 2 ＋ query-signal 規則）**：見下。
  - 新工具 `dev/source/footnote_lead_probe.py`（13 條 self-test）；`dev/DOC_SYNC_CHECKLIST.md` 補一行「Synthesis 前置閘改動」；`CODEBASE_CONTEXT.md` Directory Map ＋ 3 個模組描述。
- **Done:** commits `b61e108`(A) → `7078719`(A') → `528435d`(B@1) → `969698e`(B'@2) → `138dfca`(QC 證據＋docs)。四次 Render 部署，每次 live 驗。
- **兩個「deploy 完先捉到」嘅嘢（offline 校準過關唔代表得）:**
  1. **門檻 1 唔夠**：中文字元 bigram 分唔開 `營辦商` 同 `承辦商`（兩者都有 `辦商`），所以 SCRC footnote 喺 MIN=1 之下仍然攞到 lead。**係 deploy 完 live 重探先捉到**，離線校準睇唔到（我個 probe 只記錄第一條 footnote lead）。
  2. **淨係抬高到 2 會有代價**：實測全語料，MIN=2 會令 1 條 footnote 失去自己問題嘅席位 —— 一條幾乎全英文嘅問題（"NET Grant School Plan / School Report 要點？"），佢個 overlap=1 淨係來自 `要點` 呢個通用詞。正解 = **gate 只喺 query 本身有 ≥2 個 informative bigram 先啟動，唔夠就 fail open**（量度唔到就維持舊行為）。實測：206/206 條 footnote 自己嘅問題全部保住（3 條走 fail-open），而三條校巴 phrasing 嘅兩條離題 footnote 全部被擋。
- **QC:**
  - **eval 三對**（全部 commit）：baseline `_before` PASS 20/30 → `_after_a`（捉到 1 個 SET_LOST）→ `_after_a2`（修完 SET_LOST 0）→ `_after_b`（MIN=1，PASS 19 errors 1 = Render transient）→ `_final` **PASS 20/30 FAIL 0 errors 0**。
  - **footnote probe 兩對**：`_fnlead_before` → `_fnlead_final`：**positive 26/26 一條都冇跌**；negative 剷走 4 條（三條校巴 ＋ 校長退休金）。
  - **全語料覆核（唔止抽樣）**：206/206 footnote 自問仍然攞到 lead；TS 同 Python 兩份鏡像算出嘅 informative bigram 數**都係 7828**，證明冇實作漂移。
  - **eval 最終 6 條 SET_LOST 逐條人手判斷**：全部同一形狀 —— 離題 curated footnote 失去佢唔應該有嘅頭位，而每條 query 嘅正確文件都升咗上嚟（考試調適原本俾幼稚園非華語津貼 footnote 帶頭、家校合作俾寄宿津貼、薪酬調整俾 NET 計劃改革）。**即係話呢個缺陷 30 條 eval 入面影響 6 條，唔止報上嚟嗰條。**
  - live 終驗「校巴營辦商責任」：8 條結果全部係校巴指引 @0.714-0.772，答案改為跟車保母／車輛檢查／保護式座椅／2026 年安全帶新規／客運營業證，原本嗰段「經營利潤回饋學生」消失。
  - tsc exit 0 ×4；`footnote_lead_probe.py --self-test` PASS；routing probe 16 條，其中 3 條唔符我預期嘅**攞 HEAD 版本行同一組 probe 證實係改動前既有行為**（`校舍安全` 落 gov_admin、兩條視藝 query 落 null）。
  - 凍結合約零接觸（Supabase 16,062 / registry 256 / `_meta` 2.3.0 / facts 455 / guidelines 158 / PLATFORM_VERSION 3.2.2 全部未郁）。
- **明文未修（唔好當已解決）:** plausible-gap 類 negative 仍然攞得到 lead（overlap 1-10）—— 一條「語域啱、答案根本唔喺庫」嘅 query，overlap 可以**高過**一條用英文問嘅真命中。呢條軸上冇任何門檻分得開，屬 Open Priority ④（改良 judge prompt），`judge_probe.py` 仍然係佢嘅驗收工具。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S196 block；五份 run→`dev/source/eval_runs/`（commit，跨 session 可比）；兩個常數嘅實測分佈→code 註釋（唔止留喺 log）；新驗收工具→`footnote_lead_probe.py` ＋ DOC_SYNC 新行（可重用程序知識）；handoff 記錯根因→已喺 Open Priorities 更正。
- **Sync:** DOC_SYNC 命中 3 row（檢索 eval harness ✓ 三對 run／Channel-B SOURCE_SETS+TOPIC_KEYWORDS+QUERY_EXPANSIONS parity ✓／**新增 1 row「Synthesis 前置閘改動」** ✓ 按 anti-pattern guard 先補行）。`update_log.json` **N/A**（純檢索行為修復，無新源入庫，按 S190 定案唔記維護性改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 無需 redeploy（純 backend）。
- **Risks:** ⚠️ plausible-gap footnote lead 未解（見上）。⚠️ `footnote_lead_probe.py` 嘅 `MIN_OVERLAP` 同 backend `FOOTNOTE_LEAD_MIN_OVERLAP` 係兩份鏡像，改一邊必須改另一邊，否則 probe 會量度緊一個唔存在嘅 build（已寫入 CODEBASE_CONTEXT 該檔描述）。⚠️ Render free tier 偶發 transient error（本 session eval 撞過一次，harness 正確記做 error）。
- **收工前第三輪（Leonard 再批 go ×2）—— 兩個推翻自己嘅發現:**
  1. **我個 footnote probe 標錯 negative。** 我直接借用 `judge_probe.py` 嘅 class B，但嗰個 set 係為 **vault** 門檻設計（問「vault 答唔答到」），而 curated footnote 精準答到當中 4 條（幼稚園每班30人／病假超逾兩天／招標最少5個報價／投訴兩個月＋14天）。已改為 `ANSWERABLE_CONTROLS` 當 positive。**重跑：positive 30/30 全保。** ⚠️ **同一 session 內要再更正一次**：我第一次報「2/10」係錯嘅 —— 重寫 negative list 時，3 條 borderline（解僱教師遣散費／學校借錢俾教職員／教師評核合格分）冇歸入任何一堆就消失咗，而我冇對過拆完之後總數返唔返到 14。三條**全部仍然攞到 footnote lead**，即個疏忽一路向自己有利，令我低報咗一半以上。逐條打開語料實物核實（唔係靠關鍵字命中）後三條都證實係真空白，已放回 negative → **修正後 negative 5/13，positive 30/30 不變**。當中「學校可唔可以借錢俾教職員」全庫零相關規則（`借貸`／`借錢`／`貸款` 命中全部係 BAFS 會計科、學生賭博警號、學生資助貸款）但系統答得斬釘截鐵 —— **呢條係真‧砌數，唔係「答隔籬」**，所以殘餘問題唔可以統稱為答隔籬。**教訓：拆分或重標一個測試集之後必須對返總數，尤其當個錯會令自己個結果好睇。**順帶查實 `不應超過30` 嘅 vault 命中係 g07 講家課時間，唔係班級人數 → **S195B「VAULT_LEAD_SCORE 降唔到」結論企得住，唔使重開**。
  2. **judge 本身近乎恆等於「否」。** 離線直接叫 judge（同一 prompt／同一 model／真 top-5 chunks）跑 16 條（8 條庫有答案、8 條冇）：**shipped prompt 8/16，8 條有答案嘅全部拒晒**，其中 4 條答案逐字喺 chunk 入面。生產睇落無事，係因為 footnote／vault 兩個 bypass 幫佢繞過咗；judge 真係行到嘅時候基本上唔會答「能」。**呢個就係 S194／S195B 觀察到「judge 過度拒答」嘅根因** —— prompt 嗰句「有任何不確定，一律答否」被模型當成一條全局信心題。
- **點解冇 ship bypass 收緊（原本嘅任務）:** 收緊嘅設計成立（覆蓋率 negative 0.40/0.62 vs positive p10 0.77，ratio ≥0.70 兩條全擋），但把會失去 bypass 嗰 2 條 answerable control 交俾**真 judge** 判，**兩條都拒答** → 換嚟嘅係用兩個「答啱」去換兩個「答隔籬」，淨蝕。**次序由實測釘死：先修 judge，後收 bypass。**
- **點解冇 ship judge 改良:** V3（把判斷寫成「對住文本做測試」而唔係態度）由 8/16 升到 **11/16 零誤放**（S177 凍結教席砌數案例照樣拒）；V4 寫更詳細反而跌返 8/16。但 16 條 case 係我自己 tune 出嚟，而呢個係 anti-confab 骨幹 —— 由「永遠拒」變「有時答」嘅風險面遠超我個測試集。全部量度＋V3 全文＋ship 前需要嘅嘢寫晒入新檔 `dev/source/JUDGE_PROMPT_FINDINGS.md`。**方法本身係最有價值嘅交接**：chunk 攞一次快取，prompt 離線迭代，唔使部署。
- **紀錄更正（收工時逐項核對 commit 實況後補回，唔改寫歷史）:**
  1. `3d4ecf0` 個 message 把「7+4≠14」寫成純粹漏對數。**唔準確**：實錄顯示我事前逐條判過嗰三條係「borderline、部分答到」，即係我做過判斷（而且三次都判錯，全部錯向「唔使當佢係問題」嗰邊），唔係冇判過。
  2. `c4e5830` 個 message 最後一段描述 `footnote_lead_probe.py` 嘅集合對數守衛，**但嗰個改動實際喺 `9804239`**；`c4e5830` 只含兩個 rule 檔。
  3. 我曾向 Leonard 講「守衛個改動仲喺 working tree」—— **錯**，`9804239` 已經 commit 咗；而且我當時自己印出嘅 `git status` 已經顯示只有兩個 rule 檔有改動，即證據在眼前仍憑印象講。呢三項全部係新寫嘅 communication pack 第 9 條（講自己做過乜要引實錄）要防嘅行為。
- **收工前規則落地（Leonard 指示「設定規則防止再犯武斷及疏忽」）:** `dev/rules/communication.md` 由 5 條擴到 10 條 —— **第 3 條改寫**（「標示未驗證」→「引唔到出處就唔准落判詞，只可寫『未查』」，按 §3b 整合而非另開平行條文，舊句已retire）；新增第 6-9 條（搜尋命中唔算證據／借用工具前先確認佢原本量度乜／動集合對數＋動文字睇 diff、禁止跨行 regex 改治理檔／講自己做過乜要引實錄）；**第 10 條貫穿條款＝方向不對稱本身就係觸發條件**。`dev/RULE_PACKS.md` 擴闊該 pack 嘅載入條件（原本只喺「reply format」類任務載入，即今日呢種 session 根本讀唔到）。機器化部分：`footnote_lead_probe.py` 加 `partition_gaps()` + self-test 斷言，**用故意整壞佢證明會 FAIL**（exit 1 並列出消失嘅 query），唔係只見過佢 PASS。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → **trigger=False**（line_count=375 / entry_count=6，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 本 session 屬「跨 session 累積模式」（同一類報告紀律問題喺 S195B 已出現過一次），已按 §4 step 11(c) 意圖把可轉移部分寫成 `dev/rules/communication.md` 規則而非只留喺 log。10-closeout backstop：未到。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，逐字 mirror check PASS，74 行。）

<!-- ack:log-entry:end -->

---

## 2026-07-27 Session 195B — Leonard「全做」：清埋 8 項優先事項；兩項結論同假設相反，一項係自己整壞由 eval 捉返

- **ID:** Claude_20260727_S195B
- **Summary:** 接住 S195 上半（清死連結）。Leonard「全做」→ 我開 task list、先攞 eval baseline（因為多項改檢索）、逐項落手。8 項：1 項做唔到（需 Leonard 帳戶權限）、2 項結論同原本假設相反、1 項我做錯咗由 eval 捉到即刻還原。
- **Changed:**
  - **新源**：`sch_bus_{drivers,escorts,operators,parents,students}_2026`（28 chunks）＋ `va_safety_sec`（27）。新腳本 `dev/_extract_s195_schoolbus.py`／`dev/_extract_s195_safety.py`。
  - **重抽**：`g21`（22 頁，只餘小學版）／`g22`（52 頁，補回封面頁）。刪除 106 條舊 chunk（腳本 `dev/_s195_delete_stale_g21_g22.py` + 鎖死嘅 `dev/_s195_g21_g22_delete_set.json`，由 Leonard 執行）。
  - **backend**：`SOURCE_SETS.safety` +5 校車源、`TOPIC_KEYWORDS.safety` +校巴/保母車/跟車保母/學生服務車輛、移除 `kgecg_2017` 兩處 dead 引用、`VAULT_LEAD_SCORE` 加實測註釋、spotlight 先剪後還原（附教訓註釋）。
  - **監察**：`check_source_titles.py` 加 `--baseline`／`diff_baseline()`＋9 條 self-test；新 `.github/workflows/title_check.yml`（月跑）；`FRESHNESS_GUIDE` §0/§1/§2 補 Method C CI 同指令。
  - **新工具**：`dev/source/judge_probe.py`（24 條敵意 probe）。`eval_queries.json` 25 → **30**（新增 5 條守住今次入庫嘅源）。
  - registry 250 → **256**；display-sync 7 檔 16,033 → **16,062**；`update_log.json` +3 條；CHANGELOG 新條目。
- **Done:** commits `7f4c306`（主體）→ `2f04c42`（spotlight revert）→ 本 closeout commit。**最終 eval PASS 20 / FAIL 0 / errors 0**（30 條）。
- **QC:**
  - **eval before→after 對**：baseline `2026-07-27_s195_before.json`（PASS 15/25）→ 中途 `_after.json` **捉到 3 條 regression** → 還原後 `_after_revert.json` 對 baseline **25/25 全同** → 擴 query 後 `_final.json` **PASS 20/30**。四份 run 全部 commit。
  - **頁碼錨點逐源自檢**（因為今次修嘅正正係錯位）：5 份校車 6/6、2/2、6/6、5/5、1/1；g18 6/6；全部 offset 0 對齊。
  - **刪除安全**：兩條 `footnote_curated` chunk 明文排除（照 `source_id` 刪會毀掉人手內容）；刪除集 = 舊 id − 新 id；逐條刪逐條驗；事後 g21 23／g22 59／va_safety_sec 27／總數 16,062 全對。
  - 凍結合約：`knowledge.json` 2.3.0 / facts 455 / `guidelines.json` 2.6.1 **158** —— `build_guidelines.py --self-test` PASS（registry 167→166、public 158 不變）。tsc exit 0 ×4。
- **兩個結論同原本假設相反：**
  1. **judge 門檻唔可以降（②）** —— 24 條 probe：敵意類最高 **0.632**、真命中最低 **0.624**，**分佈重疊**。降到 0.60 會放行「教師每年可以請幾多日大假」(0.617)／「學校可唔可以借錢俾教職員」(0.615)／「校服供應商招標要幾多間報價」(0.614)，全部語域啱而個數字唔存在 = S177 砌數重演。**cosine 分唔開「揾到對嘅文件」同「揾到語域相同嘅文件」**，所以唔係揀邊個數字嘅問題。保留 0.70，實測寫入 code。
  2. **`religious_edu_jss` 唔使郁凍結 count（⑧）** —— 公開庫一早已有正確嘅 `religious_edu_jss_2024`；被剔走嗰條係重複行 + 死連結（全檔唯一一條 vertexaisearch AI 轉址殘留）。刪重複行即可，158 不變。**兼更正我上半場嘅錯**：我曾把 `religious_edu_jss` 改名成 2024 版而製造 registry 重複，已改回 `superseded` 並寫低來龍去脈。
- **一個我做錯咗嘅改動（⑦，已還原，值得記低）：** 我用「ANN pool 可達性」probe（whole-index top-40、min_score 0.22）判定 4 個 spotlight 源可以剪，4 個都 rank 0。但 before→after eval 顯示 `ai_intro`／`net_scholar`／`pay_adjust` PASS→FAIL，失去嘅正正係被剪嗰 3 個。**根因＝probe 唔忠實**：我用自己揀嘅描述性 phrasing（「人工智能初探 學與教」）測，而真正重要嘅係裸名詞（「人工智能初探」）；加上生產路徑會先 query-expand 再 embed，probe 睇到嘅候選池根本唔係生產嘅池。**教訓：用自己揀嘅寬鬆 phrasing 測「搵唔搵得到」，量度緊嘅係 phrasing，唔係檢索。** 已全部還原 + 寫喺 `SPOTLIGHT_SOURCE_IDS` 上面，下次要剪必須由 eval 對開始。
- **做唔到（④）：** `PUBLISH_PAT` scope 只可以喺 Leonard 嘅 GitHub 帳戶 Settings → Developer settings → Personal access tokens 睇；API 唔會俾 token 自報 scope。
- **Pending：** 「校巴營辦商責任」被 governance route 搶走（route 次序問題，要自己一對 before→after 證據）；judge 選項 (c)「改良 judge prompt」未做，但 `judge_probe.py` 已可作為驗收工具。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S195 下半 block；四份 eval run + judge probe 輸出→`dev/source/eval_runs/`（commit，跨 session 可比）；門檻實測→code 註釋（唔止留喺 log）；spotlight 教訓→`SPOTLIGHT_SOURCE_IDS` 註釋；每條 registry 改動理由→各條目 `notes`；監察 diff 設計→`FRESHNESS_GUIDE` §0。
- **Sync:** DOC_SYNC 命中 4 row（Channel-B vault backfill ✓ registry+SOURCE_SETS parity+eval 對／檢索 eval harness 改動 ✓ eval_queries 25→30＋4 份 run／Monitoring-CI change ✓ FRESHNESS_GUIDE＋新 workflow＋無新 secret／guidelines.json 契約 ✓ `--write` 重生、158 不變）。`update_log.json` +3 條（今次係真內容改動）。凍結合約＋`PLATFORM_VERSION` 零接觸。Pages 隨 push redeploy。
- **Risks:** ⚠️ 「校巴營辦商責任」route 次序問題未修。⚠️ g24／sag_2025_11 仍然係同一份學校行政手冊登記兩次、**215 條 chunk 文字完全相同**（今次查到嘅新數字）—— 呢個先係 eval tie 嘅真來源，但 Backlog 舊決定係「軟 dedup 已足夠」，未動。⚠️ Render free tier 偶爾 57014 statement timeout（今次 eval 中段撞過一次，harness 正確記做 error 而非零結果）。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check` → **trigger=False**（line_count=331 / entry_count=5，兩個 hard trigger 都未到）→ no-op。語意觸發：**有** —— 本 session 屬「多選項取捨並記低理由」＋「跨 session 累積模式」，已按 §4 step 11(c) append `dev/PROJECT_DECISIONS.md` Insights（三條教訓，帶證據鏈）。10-closeout backstop：未到（archive 上次 S194 執行，現 5 entries）。
- **Playbook（§14）:** 本輪經驗夠穩定且可轉移，已交兩份提案入共用經驗庫 inbox（`2026-07-28-policychecker-content-hash-id-delete-set.md`／`2026-07-28-policychecker-self-authored-probe-measures-your-assumptions.md`）＋開咗 `usage/policychecker.log.md`（4 行，3 條 applied）。playbook repo commit `ee70298` 已 push。未改該庫任何卡或 INDEX（按 §14 規矩由 librarian 處理）。

<!-- ack:log-entry:end -->

---

## 2026-07-27 Session 195 — 清三條死連結：兩條 re-point（逐頁比對作證）、一條 re-ingest（校車安全指引 2026/27 改版）＋ registry↔store drift 整理

- **ID:** Claude_20260727_S195
- **Summary:** Draft root 開工 → §1 startup → 起手探針 4/4 綠（served v3.2.2 / Render warm 455 / HEAD==origin/main `138588a` tree 乾淨、**無新 bot commit** / Supabase count=exact 16,035）→ 我報狀態並建議「① judge 門檻交 Leonard 拍板、②③ registry 衛生我做」→ Leonard「跟你建議」→ **READ 階段兩度發現實況超出我原述、按 §3 停低報告** → Leonard 兩個決定（Supabase 一齊修／g21-g22 只記錄）→ 執行 + 全掃驗證。
- **§3 兩次停低（值得記低的過程）:**
  1. 我原本同 Leonard 講「②③ 唔碰 Supabase 內容，只係修 registry」。查實發現**錯**：`wiki_chunks` 每條 chunk 自己帶一份 url，`g01` 34 條 + `ls_jss_2010` **251 條**服務緊死連結，即係用戶真係撳到 404，唔修 Supabase 等於冇修。停低講清楚 → Leonard 批「registry + Supabase 一齊修」。
  2. 動手時再 grep 發現同一條 URL 散落 **6 處**（registry / `app.html` GUIDELINES_REGISTRY / `guidelines.json` / `data.json` / `dev/checklists/_src/secmeta.json` / Supabase），其中 `guidelines.json` 屬凍結合約檔。無再開多一次會，改為：全部一次過對齊 + **機械核實凍結不變量**（見 QC），並在本 entry 明確記錄。
- **Changed:**
  - `dev/source/source_registry.json`：7 條 entry、23 個欄位。`g01`／`ls_jss_2010` url 重錨 + `freshness_metadata` 清空（舊 etag/hash 屬舊檔）；`g21`／`g22` url_primary 由 landing 改為 store 實際供應的直連 PDF；`g31` 指返真身 PDF + `related_source_ids=[eng_pri_guide_2025]`；`g30` `source_type` pdf→html；`religious_edu_jss` 揾返直連 PDF、標題／`version_label` 按封面更正為 2024 版、status candidate→verified。每條都寫低理由入該條目自己的 `notes`。
  - `app.html`（GUIDELINES_REGISTRY 2 條 url）／`data.json`（2 處）／`dev/checklists/_src/secmeta.json`（1 處）：同兩條 URL 對齊。
  - `guidelines.json`：**用 `dev/build_guidelines.py --write` 重生**（DOC_SYNC row 35 明令 NEVER hand-edit）。先手改再重生對照，證實兩者除 `_meta.updated` 外**逐字相同**，即手改內容正確但改用官方路徑產出。
  - Supabase `wiki_chunks.url`：**285 行**（g01 32＋1＋1／ls_jss_2010 251），按 distinct url 分組 PATCH 以原樣保留 `#page=17`／`#page=5` 錨點。
  - `CHANGELOG.md` 新條目（含 Known issues 段）。GitHub：Issue #4 補修復證據 + 範圍說明；**新開 Issue #5**（g21／g22 引文錯配）。
  - g18 續做新增：`dev/_extract_s195.py`（NEW）／`dev/_s195_delete_stale_g18.py`（NEW，刪除集 hard-code + dry-run 預設）／`dev/vault/g18/extract_g18.txt` 重寫為 2026/27 版／display-sync 7 檔 16,035→16,033／`update_log.json` +1 條。
- **Done:** 3 條 404 全部清走（2 條 re-point、1 條 re-ingest）並 live 驗；5 條 pdf-serve-HTML 更正；餘下發現記錄在案。Supabase 16,035 → **16,033**。
- **根因（②，比 handoff 描述深）：** handoff 把呢兩條寫成「封面掃描副產品」，實情係 **served-URL 監察（第 3 監察）早在 2026-06-29 就準確捉到並開咗 Issue #4，一直開住 4 個星期無人跟進**。監察系統健康，債係流程上冇人 close the loop。兩條的上游成因唔同：`g01` = 上游改名（`…Trad Chi_2024.pdf`→`Guidelines on Procurement Procedures_TC.pdf`）；`ls_jss_2010` = 搬入 `/pshe/archive/Life_and_Society/`。兩者皆用 playbook `external-source-url-churn-rediscovery` 方法 B（re-crawl landing／archive 頁）揾返。
- **QC:**
  - **re-point vs re-ingest 的判斷有機械證據**：重抽兩份新檔逐頁比對已入庫 vault（空白正規化後全字串相等）→ `g01` **30/30 頁相同**、`ls_jss_2010` **183/183 頁相同** → 判定純搬位／改名，只需改 url。呢一步係跟 playbook `freshness-monitor-test-served-url` 的警告（「churn 唔可單純 re-point」）做的**反向舉證**，唔係口頭假設。
  - **blast radius 先行**：Supabase 改動前印出每個 distinct url 的行數同新值俾人眼過（285 行），PATCH 逐組 assert `rows_updated == rows_expected`，之後查舊 url 殘留 = **0**、`count=exact` **16,035 前後同值**。
  - **凍結合約機械核實**：`knowledge.json` + `role_facts.json` sha256 前後相同；`guidelines.json` `_meta` version 2.6.1 / count 158 / 實際條目 158 不變；`PLATFORM_VERSION` 3.2.2 不變。`build_guidelines.py --self-test` PASS（registry 167 / public 158 / dropped 9）。
  - **監察全掃驗證（跑咗兩次）**：修完 g01／ls_jss 後 → 268 URL / 267 OK / **1 broken**（揪出新壞嘅 `g18`）；再修完 g18 後 → **268 URL / 268 checked / 268 OK / 0 broken / 0 errors** —— 成個 store 首次全綠（Issue #4 自 2026-06-29 起一直有 broken）。
  - **live 驗**：Channel B「資助學校採購程序」→ `g01` rank 1/2/3 且 url 已係新值（含 `#page=17` 錨點）；「核心單元 個人成長 青少年壓力 抗逆力 生活與社會」→ `ls_jss_2010` **rank 0 @0.715 p.30**，而 vault p.30 正正係該段內容，即頁碼錨點對得上。
  - **eval before→after 對：N/A 且已說明理由** —— 本次零檢索邏輯改動（無 SOURCE_SETS／TOPIC_KEYWORDS／spotlight／supersede／門檻改動），`url` 欄不參與 embedding 亦不參與排序。唔跑唔係慳工夫，係唔想製造無意義的 tie-flip 噪音。
- **續做（Leonard「go」）：`g18` 校車安全指引 re-ingest —— 改版而非改名，所以行完整入庫流程:**
  - **點解唔可以照 re-point**：`2025_Guidelines_Schools_TC(r).pdf` 已被上游撤下（2026-07-20 那次監察仲係綠、即 7 日內先壞），新出 `2026_Guidelines_Schools_TC.pdf`。逐頁比對新舊：**只有 3/8 頁相同** → 內容改版。照 re-point 會令 2025/26 內文掛住 2026/27 文件 = S194 `ict_sss_2021` 那類引文錯配。
  - **流程**：新寫 `dev/_extract_s195.py`（沿用 `_extract_s194.py` canonical 格式）抽 6 頁 → dry-run chunk **7 條、全部 page-resolvable、char 529/579/596、NUL 0** → `dev/ingest_one_source.py g18` embed + upsert 7 條 → 刪走只屬舊版嘅 6 條。
  - **⚠️ 過程揪出一個會靜默刪錯嘢嘅陷阱（值得記低）**：chunk id = `vault_<sid>_<content_hash>`，兩版有 **3 段文字完全相同 → id 重疊**。原計劃「DELETE 舊 9 條」**會連新版仍然有效嘅 3 條一齊刪走**。正確刪除集係 **`舊 id − 新 id` = 6 條**，已 hard-code 入刪除腳本（唔重新計算，免日後 vault 改咗就漂）。
  - **DELETE 被 auto-mode 權限分類器擋**（破壞性 DB 操作）→ 按指示**停低交俾 Leonard 決定**，佢揀「A：自己行」→ 執行 `dev/_s195_delete_stale_g18.py --apply`（dry-run 預設、逐條刪、每條先驗係咪真係掛住 2025 舊 URL、survivor 唔可以有舊 URL 否則 abort）。事後我 read-only 驗證：**g18 = 7 行、舊 id 殘留 0、總數 16,033**（16,035 ＋7 −6 −... 淨 −2）。
  - **自檢頁碼錨點**（因為啱啱先揪到 g21/g22 錯位，唔可以只信自己）：vault 6 頁 vs PDF 6 頁 **offset 0 全對**，抽 p.5 逐字對照 PDF 第 5 版 → 相同。
  - **live 驗**：搜「校車 學生服務車輛 安全 座位」→ `g18` **rank 0 @0.725 / rank 1 @0.716**、標題已係《學童乘搭校車的安全指引（2026/27）》、URL 已係新版 PDF。
  - **display-sync 7 檔 16,035 → 16,033**（15 處替換，逐檔 assert 命中數）；`update_log.json` **今次有加一條**（真內容更新，唔同前半 session 嘅純連結修復）；registry `g18`：url_primary→直連 PDF、`source_type` html→pdf、`version_label` 2026→2026/27、清 freshness、寫 notes。
  - **刻意唔改**：`app.html` GUIDELINES_REGISTRY／`guidelines.json` 嘅 `g18` 仍指 landing 頁（200，正常）。理由＝指引文件庫係俾人 browse，該頁一次過列齊 6 份對象版本（學校／司機／保姆／營辦商／家長／學生），比直接跳去「供學校」單一 PDF 更有用。呢個係決定，唔係遺漏。
- **本次揪出、未修（2 項＋1 待決）:**
  1. **`g21`／`g22` 引文錯配（Issue #5）** —— 驗 g21/g22 的 vault 對唔對得上服務中的 PDF 時發現：g22 vault 51 頁 vs PDF 52 頁，**offset +1 時 50/51 頁相同**（頁碼系統性錯開一頁）；g21 更嚴重，vault 46 頁 = 小學版（22 頁）+ **中學版 `VAsafety_sec_c.pdf`** 兩份串埋，但 49 條 chunks 全部掛小學版 url，即約一半引文指向一份佢哋唔屬於嘅 22 頁文件、錨點 `#page=23`…`#page=46` 指去檔尾之外。**同 S194 `ict_sss_2021` 同一家族**；五個監察結構上全部睇唔到（URL 回 200、封面同標題對得上、bytes 冇變）。Leonard 指示只記錄。
  2. **校車頁另外 5 份 2026/27 版指引未入庫**（供司機／保姆／營辦商／家長／學生，全部 200）—— 另一受眾，入唔入待 Leonard 決定。
  3. **`religious_edu_jss` 入公開指引庫** —— 直連 PDF 已修好，但 `app.html` 該條仍標 broken-url，被 `build_guidelines.py` 當 dropped 剔走；修好會令公開 guidelines **158 → 159**，屬凍結 count 變動，未做。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S195 block；逐頁比對數字／285 行 blast radius／全掃結果／live rank＝kept as recent trace evidence（本 entry）；每條 registry 改動理由→已寫入 registry 各條目 `notes`（下一個 agent 淨睇 registry 就知）；未修項→Open Priorities（①校車 5 份姊妹指引／③ g21-g22／⑧ religious_edu_jss）+ GitHub Issue #5（跨工具留底）；用戶面→CHANGELOG。
- **Sync:** DOC_SYNC 命中 3 row（guidelines.json/app.html GUIDELINES_REGISTRY ✓ 照 row 用 `--write` 重生／Doc-drift truth-pass ✓／Channel-B vault backfill 部分適用 —— registry + url 對齊，無 SOURCE_SETS 改動故 eval 對 N/A）。**`update_log.json`：前半 session（純連結修復）判定 N/A**（按 S190 定案只記「新源入庫／既有源重大更新」，維護性改動入去只會製造雜訊）；**後半 g18 改版有 append 一條**（真內容更新，命中 row 43）。display-sync 7 檔 16,035→16,033。凍結合約 + `PLATFORM_VERSION` 零接觸（機械核實）。Pages 隨 push redeploy（app.html／guidelines.json／data.json 有改）。
- **Risks:** ⚠️ g21／g22 引文錯配仍在生產（Issue #5）。⚠️ `g18` 換版後，任何引用舊 2025/26 版頁碼嘅外部筆記會對唔上（內容已改，屬預期）。⚠️ 本次示範咗一個結構性問題：**同一條來源 URL 在 repo 內有 6 份副本，只有其中一份（Supabase）有監察**；registry／`app.html`／`guidelines.json`／`data.json`／`secmeta.json` 五份無人測。日後若再有 URL churn，其餘五處會靜默 stale（本次係人手 grep 揾返）。
- **Log maintenance:** `python3 docs/qa/session_log_maintenance.py --check` → **trigger=False**（line_count=289 / entry_count=4，兩個 trigger 都未到）→ no-op，唔需要 archive（S194 啱啱跑過一次 archive，剩 3 entries）。

### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

（見 `dev/SESSION_HANDOFF.md` 的 `Next Session Opening Message` fenced block —— 本 session 已重生，並已鏡像至 `START_NEXT_SESSION_PROMPT.txt`，mirror check byte-for-byte PASS。）

<!-- ack:log-entry:end -->

---

## 2026-07-26 Session 194 — 修一個長期指錯文件的來源 + 人工智能初探框架正文入庫 + roadmap R1 eval harness + 封面核對監察 + R5 sibling 審計

- **ID:** Claude_20260726_S194
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → §1 startup → 起手探針 4/4 綠（served v3.2.2 / Render warm 455 / HEAD==origin/main `06d9342` tree 乾淨 / Supabase count=exact 15,901）→ Leonard 一次授權三件事：「R1 同意／R5 做／①＋②」，並釐清 technology-edu index 頁係**監察對象**、`IIT_Summary on AI_TC.pdf` 係**入庫對象**。②在 READ 階段由「核 supersede」升級為真 bug（見下），AskUserQuestion → Leonard 揀「A 完整修」＋「做全庫封面掃描」。
- **Changed:**
  - `dev/source/eval_retrieval.py` + `eval_queries.json` + `eval_runs/` (NEW, roadmap R1)：25 條短 query 對 live endpoint 跑、可 diff 兩次跑。`_tie_aliases` 吸收 g24／sag_2025_11 同分互換（S193 已證未改 code 都會 3:3 交替），429／逾時記 `error` 而非零結果。`--compare` 只對 SET_LOST／VERDICT_REGRESSED／ERROR 判 fail。
  - `dev/source/check_source_titles.py` (NEW)：封面 vs registry 標題核對（確定性 CJK bigram，比對**主題核心**——剝走學段／年份／樣板，因為全庫共用）。
  - `backend/src/api/searchChannelB.ts`：新 `cgss` route（SOURCE_SETS＋TOPIC_KEYWORDS 置 value_education 後、curriculum 前＋QUERY_EXPANSIONS）／`curriculum` +`ict_sss_2021`+`ict_sss_2007_2015`／`digital_education` +`iit_ai_framework_2026`／`SUPERSEDED_IDS` +`ict_sss_2007_2015`／`SPOTLIGHT_SOURCE_IDS` +`iit_ai_framework_2026`+`edbc013_2026`。
  - `dev/source/source_registry.json` 248→**250**；`ict_sss_2021` url 更正 + `freshness_metadata` 清空；`ict_sss_2007_2015.superseded_by` 設定。`dev/vault/`：`extract_ict_sss_2021_repaged.txt` → `cgss_sss_2021/`（git rename，body 零改）＋2 份新 extract。
  - `dev/source/execute_ingest.py`：`CHANGELOG.md`／`dev/CODEBASE_CONTEXT.md` 由 `DISPLAY_SYNC_TARGETS` **移除**（見下方程序缺陷）。`dev/source/FRESHNESS_GUIDE.md` §0 加 Method C ＋新 §1a 入庫時封面核對。`dev/DOC_SYNC_CHECKLIST.md` 加 eval harness row。
  - display-sync 7 檔（15,901→16,035）＋`update_log.json` 3 條＋CHANGELOG／CODEBASE_CONTEXT 新條目。
- **Done:** commits `3f2c9d9`（主體）→ `e0e2f3b`（post-ingest run + 修 ai_intro 斷言）→ 本 closeout commit。Supabase **15,901→16,035**（+215 INSERT／−81 DELETE）。
- **根因（②，比預期嚴重）：** `ict_sss_2021` 標題《資訊及通訊科技 (中四至中六) 2021》但 `url_primary` 指向 `CS_CAG_S4-6_Chi_2021.pdf` —— **`CS` 被當 Computer Science，實為 Citizenship and Social development**，即《公民與社會發展科課程及評估指引》。後果：81 個公社科 chunks 長期掛 ICT 標題供用戶檢索（**prod 實測 baseline 第 19 行：搜「公民與社會發展科」top-1 = `ict_sss_2021`@0.568**），而真 ICT 2021 從未入庫；`curriculum` route 亦**從未包含任何 ICT 源**，故 ICT 查詢結構上無法命中（同 S135 backfill-allowlist coupling 同一坑）。修法：新 `cgss_sss_2021` 承載該 81 chunks → DELETE 掛錯 id 的 81（post-count 0）→ `ict_sss_2021` 改指 EDB 官方檔 + 入真正文 116 chunks。
- **QC:**
  - **內容保全機械可證**：重入庫前比對 `cgss_sss_2021` 與 live 81 條的 chunk hash set → **81/81 相同、雙向差集 0**（非口頭保證）。
  - **入庫前 baseline / 入庫後對照**（兩份 run 已 commit）：PASS **12→14**、errors 0。`ict_guide` FAIL→PASS（rank 0，`ict_sss_2021`@0.624，2015 版受 supersede penalty 降位）／`nonlocal` FAIL→PASS（rank 2）／`cgss` top 由 `ict_sss_2021`@0.568 變 `cgss_sss_2021`@**0.773**／`cgss_topic`（一國兩制 課程）由中文科課程指引變 cgss+ces。2 條 SET_LOST（cgss／cgss_topic 失去通用課程源）＝加 route 的**預期效果**，harness 交人判斷而非自行猜意圖。
  - **spotlight 決策全部先實測**：`iit_ai_framework_2026` 0.628／0.676／0.642、`edbc013_2026` 0.619 → 均 ≥0.60 才加；`ict_sss_2021` 0.610/0.587 → **唔加**，先靠 route 修（post-deploy 證實 rank 0，決定正確）；`cgss_sss_2021` 0.577 → 唔加（baseline 已證全庫搜尋出得到）。**冇降 bar**。
  - 逐源 count：cgss 81／ict 116／iit 18；live 總數 **16,035** 由 `count=exact` 直查（唔用計算 delta，S190 教訓）。tsc exit 0；兩個新工具 `--self-test` 各 24 項全綠（含針對自身兩個校準缺陷的回歸測試）。
  - **封面掃描首跑**：192 個 PDF 源，**冇第二個指錯文件**；17 條 flagged 全部人手核實為良性（TOC 封面／英文封面／純文件編號標題／策展複合標題）；副產品發現 **2 條真 404**（`g01`、`ls_jss_2010`）＋**5 條 registry 寫 pdf 但 URL serve HTML**（`g30`/`g31`/`g21`/`g22`/`religious_edu_jss`）＋1 條 mojibake PDF（`phys_sss_2007_2015`）。
  - **建立監察時揪到自己兩個缺陷（已修＋落回歸測試）**：(a) v1 用「所有標題變體取最大值」→ `title_short`「ICT課程指引2021」去噪剩「ICT2021」，個「2021」撞正公社科封面「由2021/22 學年」→ 假高分 0.500 判 ok，**即 v1 會 miss 佢自己要捉嘅案**；(b) 放寬門檻後英文 `title_en` 對中文封面必然 0.0，一度令 22 個正確文件被誤 flag。修：語言配對 gate ＋剝走年份／學段 ＋短主題名用 containment。校準由 0.468/0.298 改善到 **1.000/0.000**。
  - **R5（sibling repo 審計，全程 read-only，未觸碰對方 repo）**：**推翻 handoff 假設** —— `EDB-AI-Circular-System` 已係 **PRIVATE**（handoff 仍寫「亦 public 待審」），另有新 public repo **`edb-circular-site`**（2026-06-29 建）＝已完成 private 後端／public 成品拆分。核實：public 站只有 png/md/json/html/yml，**零 .py／零 scraper／零 prompt／零 .env**；85 commits 全歷史 secret pattern 掃描**乾淨**；出街 bundle 零 apikey/Bearer 字面、**零 runtime API 呼叫**（純靜態）；Pages workflow 權限最小。private 後端：`.gitignore` 覆蓋 `.env`/`*.key`/`*_api_key*`，**594 commits 全歷史 secret 掃描乾淨**、現無 tracked `.env`；publish workflow 用 allowlist `cp` ＋「後端檔誤入公開 repo 即 FATAL」防呆閘；兩 repo forks 均 0。
- **Pending（需 Leonard 決）:** ① **anti-confab judge 門檻**：新源檢索命中但**整理答案被拒**（`人工智能初探` 0.628、`ICT 課程指引` 0.624 落喺 S183 定的 `vault_extract ≥0.70` bypass 之下）。已用控制組證實屬**既有門檻行為、非本次 regression**（`學校效率津貼` top 係 footnote_curated@0.561 → bypass 0.45 → 答；`價值觀教育` vault_extract@0.753 → 答；`公民與社會發展科`@0.773 → 答且 grounded）。降門檻會重開 S177 confab 區間（0.55–0.65），屬安全／效用取捨，**唔應由我單方面改**。② R5 剩一項只有 Leonard 做得到：確認 `PUBLISH_PAT` 係 fine-grained、只限 `edb-circular-site` contents:write。③ 2 條真 404 ＋ 5 條 pdf-serve-HTML 待處理。
- **Risks:** ⚠️ private 後端 repo **2026-03-09 建、直到 2026-06-29 一直 public**（handoff S185/S187 記錄可證），即約 3.7 個月後端 IP（scraper／prompt／編纂邏輯）曾世界可讀；轉 private 只保未來、唔追回過去（playbook `split-private-backend-public-artifact` 卡早有此警告）。**不過全歷史掃描證實從未 commit 過任何 secret，故無需 rotate 任何 key**，暴露僅限 IP。⚠️ 公開 feed `circulars.json` 頂層公開了 `model: gpt-5-nano` / `temperature: 1`（低敏感，但屬管道細節）。⚠️ spotlight 名單增至 6 源 63 chunks（上限 600）。
- **Log maintenance:** §4a 機制閘 **triggered 並已執行**：`--check` 報 `trigger=True line_trigger=True`（line_count 420 > 400，因本 entry 加入）→ 跑 `--apply --archive-dir dev/archive` → **420 → 187 行、9 → 3 entries、6 條移入 `dev/archive/SESSION_LOG_2026_Q2.md`**（raw 內容保留，冇刪任何 entry）→ 重跑 `--check` 確認 `trigger=False`（line_count=187 / entry_count=3）。`--apply` 當時另報 `latest entry prompt block ok=False`：因為 archive 喺 checkpoint 階段跑，`### Next Session Handoff Prompt (Verbatim)` 要到 full closeout 才寫；該 block 已於本次收工補上（見本 entry 末），handoff↔`START_NEXT_SESSION_PROMPT.txt` mirror check byte-for-byte PASS。
- **Evidence disposition:** 當前狀態→handoff Current Baseline S194 block；hash-set 比對／實測 cosine／eval 前後對照／封面掃描結果／R5 審計細節＝kept as recent trace evidence（本 entry）；入庫時封面核對紀律 + Method C 監察模型→promoted to `dev/source/FRESHNESS_GUIDE.md` §0+§1a（可重用程序知識）；跨 repo durable 教訓→promoted to `dev/PROJECT_DECISIONS.md` Insights；eval harness 同步義務→promoted to DOC_SYNC row；模組事實→CODEBASE_CONTEXT Directory Map + AI log。
- **Sync:** DOC_SYNC 命中 4 row（Channel-B vault backfill／Doc-drift truth-pass／Monitoring-CI change／Option A 管道改動）＋**新增 1 row**（eval harness，原本無 row → 按 anti-pattern guard 先補）。display-sync 7 檔 15,901→16,035 ＋ `update_log.json` 3 條 ＋ CHANGELOG／CODEBASE_CONTEXT 新條目。凍結合約（`_meta` 2.3.0／facts 455／guidelines 158）＋ `PLATFORM_VERSION` 3.2.2 零接觸。Pages 已隨 push redeploy（前端數字有改）。


### Next Session Handoff Prompt (Verbatim)

📋 Next session: agent-managed startup content below

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S194, 2026-07-26): 平台 v3.2.2; Supabase 16,035 chunks; source_registry 250;
HEAD==origin/main (744af53 + S194 closeout commit; code commit 3f2c9d9); 凍結合約 _meta 2.3.0 /
facts 455 / guidelines 158; 0 outstanding bug. 自動化 active: 4 源監察 (discover / freshness /
served-url / new-circular) + Option A 自動入庫管道 (OPERATIONAL; 每日 19:30 HK refresh Issue +
@mention-on-new; cron 20:00 HK 兜底). 第 5 監察 (封面核對 check_source_titles.py) 已建但未接 CI.

⚠️ 管道會自行入庫並直接 push main — 開工時本地可能落後 origin/main, tree 乾淨 + 0 本地 commit
時先 git pull --ff-only 同步。

📋 S194 修好: (1) ict_sss_2021 一直指錯文件 — 標題寫《資訊及通訊科技 2021》但 url 指
CS_CAG_S4-6_Chi_2021.pdf, CS = Citizenship and Social development 而非 Computer Science → 81 個
公社科 chunks 長期掛 ICT 標題 (prod 實測 top-1 標題錯配), 真 ICT 2021 從未入庫, 且 curriculum
route 從未有任何 ICT 源。已新立 cgss_sss_2021 承載該 81 chunks (hash set 81/81 相同, 內容逐字
不變) + 入真 ICT 正文 116 chunks + 新 cgss route + SUPERSEDED_IDS。(2) 入庫《人工智能初探》框架
正文 iit_ai_framework_2026 (18 chunks)。(3) display-sync 全檔字串取代一直靜默改寫 CHANGELOG /
CODEBASE_CONTEXT 歷史條目 — 已修正並將兩檔移出 DISPLAY_SYNC_TARGETS (歷史檔只追加, 唔反映當前值)。
⚠️ 動 backend 檢索前必讀 dev/SESSION_LOG.md S194 QC 段 + S193 QC 段 (門檻實證 + tie-flip 陷阱)。

🛠 新工具 (動檢索前後都應該用):
  python3 dev/source/eval_retrieval.py --self-test
  python3 dev/source/eval_retrieval.py --run --out after.json
  python3 dev/source/eval_retrieval.py --compare dev/source/eval_runs/2026-07-26_s194_post_ingest.json after.json
  任何檢索改動 (SOURCE_SETS / TOPIC_KEYWORDS / spotlight / supersede / 門檻) 都要有一對
  before→after run 作證據 (DOC_SYNC 已登記)。入新源前跟 FRESHNESS_GUIDE §1a 核封面標題。

🔜 NEXT (優先序):
  ① 【需 Leonard 拍板, 唯一未解項】anti-confab judge 門檻: 新入 vault_extract 源檢索命中但整理
     答案被拒 (人工智能初探 0.628 / 資訊及通訊科技 課程指引 0.624, 低於 S183 的 vault_extract
     ≥0.70 bypass)。已用控制組證實屬既有門檻行為、非 S194 regression。選項 (a) 唔改, 用戶仍見
     正確來源+頁碼 (b) 降至 ~0.60 — 會重開 S177 confab 區間 0.55-0.65, 必須先做 20+ 條敵意
     probe (c) 針對裸名詞短 query 改良 judge prompt (另開 PLAN)。唔好未做敵意測試就降門檻。
  ② 2 條真 404: g01 / ls_jss_2010 (封面掃描副產品, 走 §D.12 landing-page re-discovery)。
  ③ 5 條 registry 寫 source_type=pdf 但 URL serve HTML: g30 / g31 / g21 / g22 / religious_edu_jss。
  ④ 只有 Leonard 做得到: 確認 PUBLISH_PAT 係 fine-grained、只限 edb-circular-site contents:write。
  ⑤ 把封面核對接入 CI (建議月跑, 192 源要下載)。
  ⑥ g29 同 kgecg_2017 係同一份文件登記兩次 (同 g24/sag_2025_11 同類, 會造成固有 tie)。
  ⑦ spotlight 現 6 源 63 chunks (上限 600), 確認能經 ANN 出頭後可 prune; edbcm073_2026 仍唔出
     (0.458 低於 bar, 設計邊界非 bug)。
  其他 backlog: roadmap R1-R8 (dev/SYSTEM_ANALYSIS_AND_ROADMAP.md §4/§5/§7; R1 已落地);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A)。

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft
HEAD==origin/main〔落後就 ff-pull〕+ Supabase count=exact), 然後向 Leonard 報告當前狀態同建議下一步。

所有路徑含空格, 終端機指令必須用雙引號包住。改任何嘢之前, 先報告當前狀態同建議下一步。
```

---

## 2026-07-26 Session 193 — 修「入庫但搵唔到」根因（spotlight overlay）+ executor 可見度閘 + technology-edu 監察核實

- **ID:** Claude_20260726_1219
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 跟 §1 startup → 起手探針 4 條：served app.html v3.2.2 + 標題 200 ✅／Render `/health` warm 455 ✅／**Draft HEAD 落後 origin/main 4 個 commit**（= Option A 管道自 S192 起無人手自動入庫 4 條通告，ff-pull 同步）✅／Supabase 直連 count=exact **15,901** ✅（registry 248）。逐條 live 探測 4 條自動入庫源，揪出 **2 條連自己標題都檢索唔到** → Leonard 批「1＋2＋再加 Monitor technology-edu 課程文件頁」→ 修根因 + 補機制 + 核實監察，全部 live 驗證。
- **Changed:**
  - `backend/src/lib/wikiRepository.ts`：新 `searchSpotlightSources()`（按 source_id 集合做 exact-cosine，route/ANN 皆獨立，沿用 S174 footnote overlay 同一結構）+ `loadSpotlightChunks()`（按 id-set 為 key 的 process cache、`SPOTLIGHT_CHUNK_CAP=600` 上限）+ `searchFootnotes()` 加 optional `qVec` 參數（向後兼容）+ `invalidateWikiCache()` 一併清 spotlight cache。
  - `backend/src/api/searchChannelB.ts`：`SPOTLIGHT_SOURCE_IDS`（帶 `ack:spotlight:start/end` marker 供 executor 機器插入，初始 4 條）+ `SPOTLIGHT_LEAD_SCORE=0.60` + `SPOTLIGHT_MAX_LEADS=1`；主流程加 spotlight pass（footnote lead 之後插，`forcedLeads` 追蹤位置，source 已可見則不插，套用 supersede penalty，best-effort try/catch）；raw-query embedding 抽出一次由兩個 overlay 共用（**embedding 呼叫數不變**）。
  - `dev/source/execute_ingest.py`：新步驟 **4b spotlight 註冊**（`plan_spotlight_patch`/`live_spotlight_patch`，marker 缺失時發 warning 而非靜默）+ `post_deploy_smoke` 由「印一個無人睇的 bool」改為**真閘**（多種 phrasing 探測、報 rank、搵唔到就發 `::warning::` GitHub Actions annotation，仍非 fatal）+ `_annotate()` helper + dry-run plan/print 加 4b + docstring 步驟表。
  - `dev/CODEBASE_CONTEXT.md`：wikiRepository/searchChannelB/execute_ingest 描述 + AI Maintenance Log。`dev/DOC_SYNC_CHECKLIST.md`：補 Option A 管道 row（原本無 row 覆蓋該機制）。
- **Done:** commit `ef426cc` push → Render auto-deploy → **live 目標源 6/6 PASS**（edbcm113 rank 0；edbcm094 rank 2 ×3 phrasing；edbcm066 rank 2 ×2）+ synthesis grounded（「2026-27 公務員薪酬調整幅度 2%」／「英國語文科 5 級或以上」）。
- **QC:**
  - **根因 code-verified**（非靠推測）：`searchWiki` 向 Supabase 取**全庫** top-(top_k×5)=40，之後才在 JS 按 SOURCE_SET post-filter → 3–14 chunks 的新源要同全庫 15,901 chunks 爭 40 個位，**加 SOURCE_SET 或 TOPIC_KEYWORDS 結構上救唔到**。實測佐證：edbcm094 對自己標題 cosine **0.722** 卻完全唔出。
  - **門檻由實測定**：on-topic 直配 0.62–0.72；**20 條敵意 off-topic probe 最高 0.563**（「學校效率津貼」vs edbcm073）→ 0.60 收 0/20 敵意。低分 merge 刻意唔做（0.45 會收 6/20）。
  - **A/B 回歸**：本機（已修）對 prod（未修）14 條既有 query → 12 條完全相同；2 條差異**經隔離測試證明與本改動無關**——(a)「公積金 MPF」g24↔sag_2025_11 = 同一份學校行政手冊兩次入庫（`SOURCE_ALIASES`）、文字相同→cosine 完全同分 tie，**未修版本自己連跑亦會 3:3 交替**；(b)「資優教育課程」rank 7/8 近同分互換，**未修本機同樣異於 prod**（= prod-vs-local 環境差異）。另實測 OpenAI embedding 對同一輸入 **bit-identical**，排除 embedding 噪音假設。
  - **live 回歸**：13 條既有 query → **spotlight 污染 0/13**、既有預期命中 **5/5**、**9 條仍有 footnote_curated 參與**（證明共享 embedding 未破壞 S174 路徑）。
  - tsc exit 0 ×2；`py_compile` ✅；`discover_sources.py --self-test` ALL PASS；executor dry-run 正確顯示 4b（block 808-813、4 listed）且批准閘仍擋（`decision='no-approval-record'`）+ **零 live 寫入核實**（registry 248 / knowledge 15,901 / 無新 vault dir）。
  - **Monitor 核實**：Leonard 指定的 `…/technology-edu/curriculum-doc/index.html` **早已在 discovery watch list**（62 頁之一，經 `tech_curr_docs` 等 12 個 registry entry 的 `url_landing`）→ **無需新增、避免重複 row**。用 `discover_sources.py` 自己的函式對該頁 11 個文件連結做 diff：**2 條未入庫**——`IIT_Summary on AI_TC.pdf`（= edbcm113 通函所公布的《人工智能初探》框架**正文**，561KB，HTTP 200）+ `ICT_C&A Guide_c_final.pdf`（2.6MB，200；registry 的 `ict_sss_2021` 指向 edcity 另一 URL，疑為 EDB 版新檔名）。
- **Evidence disposition:** 根因機制 + 門檻實證 → 已寫入 code 註解（`SPOTLIGHT_SOURCE_IDS` 段落）+ 本 entry；當前狀態 → handoff Current Baseline S193；2 條未入庫候選 + tie 非決定性觀察 → handoff Open Priorities / 監察項；可重現 = commit `ef426cc`。
- **Sync:** DOC_SYNC 命中「Product behavior / tuning change」（handoff + log + QC evidence ✓）；Option A 管道原本**無 row** → 已補 row（registry anti-pattern guard）；CODEBASE_CONTEXT 模組描述 + AI log 更新。**無** Supabase／registry／凍結合約（`_meta` 2.3.0 / facts 455 / guidelines 158）／`PLATFORM_VERSION`／display-sync 改動（純檢索行為修復，同 S174/S183 先例一致唔 bump）。Pages 無需 redeploy（前端零接觸）。
- **Pending（非阻塞，待 Leonard 決）:** ① 入庫 `IIT_Summary on AI_TC.pdf`（補 edbcm113 只有 3 chunks 的先天單薄；建議做，屬 S170 monitor-driven on-demand 正路）② 核 `ICT_C&A Guide_c_final.pdf` 是否 `ict_sss_2021` 的 EDB 版／新版（可能係 URL churn 或 supersede）③ 「人工智能初探」「電子學習撥款」兩條短 query 仍唔出（chunk 對該 phrasing 只得 0.46–0.47，低於 0.60 bar；①入庫框架正文係更正確的解法，唔建議降 bar）。
- **Risks:** ⚠️ spotlight 名單會隨每次自動入庫增長（每條 query 對其 chunk 做 exact cosine）；已設 600 chunk 上限 + code 註明「確認能經 ANN 出頭後可 prune」，目前 4 源 36 chunks。⚠️ **新揭發（非本次造成）**：g24 / sag_2025_11 係同一份文件兩次入庫、chunk 文字相同 → cosine 完全同分，Channel B 結果對呢兩個 id 存在固有非決定性（同內容，用戶無感）；日後做檢索 eval harness（roadmap R1）必須容許 tie flip，否則會出假 regression。⚠️ 本次未動 judge 門檻：spotlight lead 若 <0.70 仍過 anti-confab judge（保護不變，故某些 query 有結果但可能唔出整理答案）。
- **Log maintenance:** §4a 機制閘已跑：`python3 docs/qa/session_log_maintenance.py --check --session-log dev/SESSION_LOG.md` → `trigger=False line_trigger=False date_trigger=False`（line_count=349、entry_count=8；最舊 entry 2026-06-28 = 28 日）→ **no-op，唔觸發 archive**。

### Next Session Handoff Prompt (Verbatim)

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S193, 2026-07-26): 平台 v3.2.2; Supabase 15,901 chunks; source_registry 248;
HEAD==origin/main (ffd7f22 = S193 docs; code commit ef426cc); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158;
0 outstanding bug. 自動化 active: 4 源監察 (discover / freshness / served-url / new-circular) + Option A
自動入庫管道 (OPERATIONAL; 每日 19:30 HK refresh Issue + @mention-on-new; cron 20:00 HK 兜底).

⚠️ S192→S193 之間管道自行入庫 4 源 (+27 chunks, 15,874→15,901, registry 244→248) — 開工時本地會落後
origin/main, 先 git pull --ff-only 同步 (bot 直接 push main; tree 乾淨 + 0 本地 commit 時 ff-pull 安全).

📋 S193 修好: 「入庫但搵唔到」根因. searchWiki 取全庫 top-(top_k*5)=40 後才按 SOURCE_SET post-filter →
細源 (3-14 chunks) 結構上入唔到窗口, 加 SOURCE_SETS/TOPIC_KEYWORDS 都救唔到. 修法 = 新
wikiRepository.searchSpotlightSources() route/ANN-獨立 exact-cosine + SPOTLIGHT_SOURCE_IDS 一個 lead slot
@0.60 (實測: on-topic 0.62-0.72 vs 20 條敵意 off-topic 最高 0.563). executor 加步驟 4b 自動註冊新源 +
post_deploy_smoke 改為真閘 (報 rank, 搵唔到發 ::warning:: annotation). LIVE 6/6 PASS, 回歸污染 0/13.
⚠️ 動 backend 檢索前必讀 dev/SESSION_LOG.md S193 QC 段 (門檻實證 + tie-flip 陷阱).

🔜 NEXT (優先序; ①② 係 S193 直接遺留, 其餘同 S192 roadmap):
  ① 入庫《人工智能初探》框架正文 IIT_Summary on AI_TC.pdf (561KB/200, 見 handoff Open Priorities S193 ①):
     edbcm113 通函只有 3 chunks (封面+摘要), 正文才係實質內容; 亦係「人工智能初探」短 query 唔出嘅正解
     (唔應降 spotlight bar). 屬入庫 triage — 需 Leonard 拍板.
  ② 核 ICT_C&A Guide_c_final.pdf (2.6MB/200) 是否 registry ict_sss_2021 (現指 edcity URL) 嘅 EDB 新版
     → 若係新版走 supersede 規則 (SUPERSEDED_IDS + registry superseded_by 雙處同步).
  ③ Circular System 安全審計 (= roadmap R5): sibling repo EDB-AI-Circular-System (circular.wongfu.net, 亦
     public), 用 S187 同級 rigor (paste prompt 見 SESSION_LOG S190 closeout).
  ④ S187 安全 backlog (= R5): repo 轉 private + hosting 搬離 Pages / Supabase 開 RLS + anon RPC-only.
  ⑤ 維護提醒: spotlight 名單每次自動入庫 +1 (現 4 源 36 chunks / 上限 600), 確認能經 ANN 出頭後可 prune;
     edbcm073_2026 仍唔出 (0.458 低於 bar, 設計邊界非 bug), Leonard 報 miss 先處理.
  其他 backlog: roadmap R1-R8 (見 dev/SYSTEM_ANALYSIS_AND_ROADMAP.md §4/§5/§7);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A).

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft
HEAD==origin/main〔落後就 ff-pull〕+ Supabase chunk count), 然後向 Leonard 報告當前狀態同建議下一步.

所有路徑含空格, 終端機指令必須用雙引號包住. 改任何嘢之前, 先報告當前狀態同建議下一步.
```

---

## 2026-07-05 Session 192 — 系統分析 + 改進路線圖 deliverable（read-only 規劃，零 code/data 改動）

- **ID:** Claude_20260705_1315
- **Summary:** 頂層 dormant root「開工」→ redirect Draft → 跟 Draft §1 startup（讀 handoff/log/CODEBASE_CONTEXT/PMS）→ 起手探針 **4/4 綠**（served app.html v3.2.2 + title「香港學校政策搜尋平台」HTTP 200 / Render `/health` warm 455 / Draft HEAD `a47eedf`==origin/main tree 乾淨 / Supabase 15,874 文檔值未直連）。Leonard 要求：**分析及規劃現時系統功能同方向、改進空間，hands-off，寫成日後 claude agent 可執行嘅 deliverable，然後收工**（並提 `/model fable`——已說明 session 中途 agent 無法自切 model、實際 Opus 4.8 跑，實質要求照做）。純 read-only 分析、無改任何 code/data。
- **Changed:**
  - **NEW `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md`** —— 策略分析 + 改進路線圖 deliverable。落地核實現況（app.html nav → 8 桌面 tab：平台介紹/政策搜尋/指引文件/通告分析/文件分析/文件標註/政策範本/文件修訂；server.ts → 11 backend routes）。內容：一頁摘要、現時功能全圖、系統健康誠實評估（做得好 4 項 + 技術債 7 項）、產品方向 A/B 觀察、**8 個已排序改進項 R1–R8**（R1 檢索 eval harness / R2 IA tab 收斂 / R3 Channel A 退役 / R4 codebase 可維護性單檔拆模組 / R5 安全 backlog / R6 Render 冷啟 / R7 mobile 全功能 / R8 reranking，每項帶 risk/工作量/首步/Leonard 決策/相關檔案）、不變量護欄 9 條（摘 PMS §A.2/§E/§F）、roadmap 執行次序、日後 agent 揀項指南。
  - `dev/SESSION_HANDOFF.md`：Current Baseline prepend S192 block；Open Priorities 頂加 roadmap 指針行；State Reconciliation 更新到 S192。
  - `dev/CODEBASE_CONTEXT.md`：directory map +1 行（新 doc）。
  - `START_NEXT_SESSION_PROMPT.txt`：重生為 S192 state-rich prompt。
- **Done:** deliverable 交付，日後任何 agent 讀 `dev/SYSTEM_ANALYSIS_AND_ROADMAP.md` §4 即可挑 R 項落手。建議即刻無悔項＝R1 檢索 eval baseline + R5 sibling 安全審計（read-only）；R2 依賴 Leonard 定產品定位 A/B。
- **QC:** 現況數字全部 code-verified（app.html nav labels grep + server.ts route grep），非靠文檔記憶（守 memory 鐵律 verify-against-code）；deliverable 內零 hardcode live 數字（一律指向 handoff）；不變量護欄逐條對回 PMS §A.2/§E/§F。無 code/data 改動 → 無 build/regression/live smoke 需要（純文件）。起手探針 4/4 綠已記錄。
- **Evidence disposition:** 分析內容 → 新 deliverable（方向性文件）；當前狀態 → handoff Current Baseline S192；session trace + QC → 本 entry；reproducible = git commit（新 doc + 3 治理檔）。
- **Sync:** 純分析 deliverable + 治理持久化。CODEBASE_CONTEXT directory-map +1 行（新 dev 文件）。無 backend/stack/service/secret/凍結合約/PLATFORM_VERSION 改動 → 無 display-sync、無 Render/Pages redeploy、無 DOC_SYNC 產品 row 觸發。頂層 dormant root 文件層面零接觸（redirect 仍 valid）。
- **Pending（非阻塞）:** roadmap R1–R8 待 Leonard 揀方向落手（R2/R3/R4 動鎖定決策需 §3 HIGH-risk PLAN + 拍板；R1/R5 可無悔即做）。其餘 backlog 不變（見 handoff Open Priorities：Circular 安全審計 #1 等）。
- **Risks:** S192 = 純 read-only 分析、零風險（無 code/data/backend/contract 接觸）。⚠️ deliverable 係 point-in-time 方向文件，非 SSOT——日後 agent 落手前必以 handoff live 狀態為準、以 PMS 不變量為界（已喺文件開頭 + §5 + §7 寫明）。
- **Log maintenance:** §4a 檢查：SESSION_LOG 加 S192 後仍 <400 行、最舊 entry 2026-06-28（<30 日）→ 唔觸發 archive。no-op。

### Next Session Handoff Prompt (Verbatim)

```text
Work in /Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft

Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md → dev/PROJECT_MASTER_SPEC.md
(Playbook lazy: read only "Leonard's playbook/playbook/INDEX.md"; open a card only on trigger.)

Current state (S192, 2026-07-05): 平台 v3.2.2; Supabase 15,874 chunks; source_registry 244;
HEAD==origin/main (a47eedf + S192 closeout docs commit); 凍結合約 _meta 2.3.0 / facts 455 / guidelines 158;
0 outstanding bug. 自動化 active: 4 源監察 + Option A 自動入庫管道 (OPERATIONAL, VERIFIED LIVE).

📋 S192 交付: dev/SYSTEM_ANALYSIS_AND_ROADMAP.md — 系統分析 + 改進路線圖 (read-only, 零 code/data 改動).
8 個已排序改進項 R1–R8 (R1 檢索 eval harness / R2 IA tab 收斂 / R3 Channel A 退役 / R4 codebase 可維護性 /
R5 安全 backlog / R6 Render 冷啟 / R7 mobile 全功能 / R8 reranking), 每項帶 risk/首步/Leonard 決策/相關檔案.
揀項目落手前先讀該檔 §4 (項目) + §5 (不變量護欄) + §7 (揀項指南); live 狀態仍以 handoff 為準.
建議即刻無悔項: R1 檢索 eval baseline + R5 sibling Circular System 安全審計 (read-only);
R2 IA 收斂依賴 Leonard 先定產品定位 A (搜尋引擎) 定 B (文件合規工作台).

🔜 NEXT (待 Leonard 揀方向, = roadmap R 項對應):
  ① Circular System 安全審計 (Leonard 下個焦點, = roadmap R5): sibling repo EDB-AI-Circular-System
     (circular.wongfu.net, 亦 public), 用 PolicyChecker S187 同級 rigor 審 (paste prompt 見 SESSION_LOG S190 closeout).
  ② S187 PolicyChecker 安全 backlog (= roadmap R5): repo 轉 private + hosting 搬離 Pages (同 ops private-repo 合一) /
     Supabase 開 RLS + 收 anon RPC-only.
  其他 backlog (= roadmap R 項): S186 2 源 monitor (edbcm073 / edbcm066 短 query 排名低, 報 miss 先 boost);
  Feature 2a 追問 + 2b 文件 scoped Q&A (Leonard S182 揀 sequence A); Option A 低優先 follow-up.

Post-startup first action: 跑起手探針 (served app.html v3.2.2 + Render /health warm 455 + Draft HEAD==origin/main
+ Supabase chunk count), 然後向 Leonard 報告當前狀態同建議下一步 (可提 roadmap R1/R5 無悔項).

所有路徑含空格, 終端機指令必須用雙引號包住. 改任何嘢之前, 先報告當前狀態同建議下一步.
```

---

<!-- ack:log-entry:start -->
