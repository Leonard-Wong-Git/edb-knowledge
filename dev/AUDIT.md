# 架構盤點 — AI Agent 模式與護欄

盤點日期：2026-09-14（S225）
方法：`ai-agent-patterns` skill 既有系統路徑（辨認現況 → 重新評估需要 → 找落差 → 排次序）
盤點範圍：`backend/src` 全部 19 檔（5,974 行）、`dev/` 離線抽取與入庫管道、`dev/source/qc_report.py`、`.github/workflows/` 九個 workflow、前端 `app.html` / `mobile.js` 的呼叫面
證據規格：每項判斷附 `file:line`；碼為準，文件與註釋只作參考。凡未經檢查者一律標「未查」。

---

## 一、現況

### 1.1 模式判定：全系統停在層 0 與層 1，零層 2

| Flow | 入口 | 模式 | 判定依據 |
|---|---|---|---|
| Channel B 語義搜尋 | `searchChannelB.ts:1417` | W2 路由 ＋ W1 鏈 | `detectQueryCategory` 為固定 regex 表（`:802`）；判官二元分類後行寫死的 `if/else`（`:1049-1051`） |
| Channel A 搜尋 | `searchChannelA.ts:106` | W1 順序鏈 | embed → cosine → 可選一次合成，無分支 |
| Combined A+B | `searchCombined.ts:110` | W3 分工並行 | `Promise.all([searchChannelA, searchChannelB])`（`:124-132`），切法寫死 |
| 文件分析 | `analyzeDocument.ts:241` | W1（內含固定 fan-out） | 逐段限流檢索 `mapWithConcurrency(…, 4)`（`:265`），全篇只有一次 LLM 呼叫（`:289`） |
| 文件修訂 | `checklistRevise.ts:357` | P1 檢索原語 | 檔頭自述 `Pure embedding-based coverage (deterministic, NO LLM)`（`:6`） |
| 文件標註 | `annotateDocument.ts:179` | W3 分工並行 | 上兩者並行組合（`:227-242`），本身零 LLM 呼叫 |
| 通告分析 | `analyzeCircular.ts:28` | W1 順序鏈 | 分類 → 篩選 → 組 prompt → 單次生成，四步寫死 |
| Channel B 同步 | `channelBSync.ts` | 非 AI flow | 純 PostgREST 讀取端點 |

**最重要的一項判定：整個後端沒有任何工具呼叫。** `grep -rn "tool_choice\|tools:" backend/src/` **零命中**；`llmClient.ts:26-30` 的 `responses.create` 只傳 `model`、`input` 與可選的 `text.format`，從未傳 `tools`。即模型在任何一處都沒有「揀用哪個工具、下一步查甚麼」的權力 —— 檢索用哪個 source 集合、答或不答、走哪條合成路徑，全部由程式碼決定。

**這是好事，不是缺陷。** 對照 §A.2「可追溯性優先於覆蓋率」的不變量，層 1 正是這個任務應有的層級。

### 1.2 合成路徑有兩條，強的那條預設關閉

- **軌道 A（預設、生產行緊）**：判官閘 `judgeCanAnswer`（`searchChannelB.ts:934`）一次 LLM 二元判斷 → 通過才行第二次 LLM 自由文字合成（`:1059`）。判官輸出用 `verdict.startsWith("能")` 解析，非結構化。
- **軌道 B（`FEATURE_GROUNDED_SYNTHESIS=1`，預設關）**：`groundedSynthesis.ts:104` 的 draft → verify 兩段式，draft 與 review 兩次呼叫都用 `strict: true` 的 `json_schema`（`:27-45`、`llmClient.ts:29`），而且**引文核實是確定性字串比對**（`fold(chunks[index-1].text).includes(quote)`，`:74-100`），不是模型自評。

兩軌都是單程收斂、無迭代，故**不是** W6 評估－優化。

**判官不是每次都行。** `searchChannelB.ts:1045-1051` 有一條常態繞過：主搜尋 lead 若為 `vault_extract` 且分數 ≥ `VAULT_LEAD_SCORE`（0.70，`:1228`），`trustedVaultLead` 成立，判官連呼叫都不會發生，直接入合成。這是 S183 起有意設計，`:993` 起有大段註釋交代成因與量度。列在此處是因為：防捏造閘「不會行」有兩個成因，一個是設計（本項），一個是故障（下方乙③），讀者需要同時知道兩者。

**落差就在這裡**：專案宣稱的核心價值是逐句可追溯，而真正做到逐句核實引文的實作已經寫好、有離線回歸測試，卻預設關閉；生產行的是自由文字合成配一個 fail-open 判官。

### 1.3 護欄盤點

| 項目 | 狀況 | 證據 |
|---|---|---|
| 輪數上限 | **不適用（良好）** | 無迴圈式 agent，呼叫次數是編譯期常數；`MAX_SEGMENTS = 12`（`analyzeDocument.ts:29`） |
| Token 累計預算 | **缺** | 全 `src/` grep `prompt_tokens\|completion_tokens\|\.usage` 零命中 |
| 時鐘上限（LLM） | **缺** | 兩個 OpenAI client 都無 `timeout`；SDK 預設 10 分鐘（`node_modules/openai/core.d.ts:86`）。全 `src/` 只有 `usageCounter.ts:50-51` 一處用 `AbortController` |
| 時鐘上限（DB） | **有** | `RPC_RETRY_DEADLINE_MS = 6000`（`wikiRepository.ts:146`） |
| 重試 | **有，但三套語義不一** | DB：3 次、線性 backoff、只對 `57014`（`wikiRepository.ts:147,163,184`）；同步端點：4 次 300/600/900ms（`channelBSync.ts:135,149`）；LLM：SDK 預設 2 次（`openai@4.104.0` `index.d.ts:112` `[opts.maxRetries=2]`，`server.ts:165,167` 未傳） |
| 速率限制 | **有** | 每 IP 10 次／60 秒 ＋ 全域 120 次／60 秒（`server.ts:49-57`） |
| 併發上限 | **缺** | 只限速率，無 in-flight 計數 |
| 不可逆動作驗證 | **後端不適用** | 後端唯一寫入是 `bump_usage` 計數 RPC（`usageCounter.ts:53`） |
| 人為批准閘 | **有，但覆蓋不全** | 見下方落差乙② |
| 結構化輸出 | **有實作，預設路徑未用** | 軌道 B 用 strict schema；預設路徑解析中文字（`searchChannelB.ts:931`）與正則（`analyzeDocument.ts:197-206`） |
| 追蹤記錄 | **缺** | 全 `src/` 只有 11 個 `console.*`，主檔 `searchChannelB.ts`（1,739 行）**一個都無**；無 request id |
| 成本記帳 | **缺** | `usage_daily` 只記搜尋**次數**（`usageCounter.ts:9`），非 token |
| 輸入淨化 / prompt injection | **缺（風險上限受控）** | 用戶上載文件原文直接串入 prompt：`analyzeDocument.ts:189` `` `段落${i + 1}：${seg.slice(0, 300)}…` ``，無分隔符、無逃脫。因全系統零工具呼叫（1.1），注入成功的上限是輸出文字失控，不能觸發任何動作 |
| eval set | **有多套，狀態見下** | 見 1.4 |

### 1.4 量度數據（本欄大部分空白，這一點本身是結論）

- **輪數分佈**：不適用（無迴圈）。
- **單次成本**：**無數據**。唯一與金額有關的是 `env.ts:52-54` 一段設計時人手估算（判官約 US$0.0005／次），不是執行時量度。
- **失敗率**：**無當期數據**。最近一次全 185 題 gold 是 2026-09-08（`dev/source/eval_runs/2026-09-08_s220_route_first_before_after.meta.json`，`gold_count: 185`、`status: complete`、耗時約 17.5 分鐘）。其後 S223 換了 SAG 整份語料而未做 before→after。
- **Recall@k**：**不可執行**。工具 `dev/_s213_eval_metrics.py` 依賴 `dev/_s213_corpus.py:34-38` 的 `DEFAULT_CACHE`，該路徑指向另一個已消失的 session scratchpad。
- **快取命中**：**無數據，且結構上難以命中**。合成與判官 prompt 的靜態前綴分別約 150 與 250 個中文字（`searchChannelB.ts:889`、`:912`），遠低於 OpenAI prompt caching 的 1,024 token 門檻。惟本平台流量低，成本未必是實際問題 —— **列作觀察，不建議現在動手**。

### 1.5 自動執行的閘

九個 workflow 中八個在跑：`backend_build_check`（每次 push／PR，S224 起為 required check）、`qc_report`（每日 12:00 UTC）、`monitor_watchdog`（每日）、`discover_check` / `freshness_check` / `pgvector_check` / `served_url_check`（每週一）、`title_check`（每月）。`new_circular_check.yml` 已標註 RETIRED 且 schedule 全被註釋。

`regression:semantic` 與 `regression:grounded` **不在任何 workflow 內**，只能人手跑。

---

## 二、重新評估需要（當這個系統從未存在過）

1. **需要 LLM 嗎？** 需要，但比現時想像的少。檢索、分類、覆蓋率比對三環已經是確定性的（`checklistRevise.ts` 全程零 LLM、`topicDetector.ts` 純 cosine、路由純 regex），這是對的。LLM 只該負責「把找到的原文組成一段話」與「判斷找到的原文答不答到問題」。現況符合。
2. **甚麼叫做對？錯了會怎樣？** `PROJECT_MASTER_SPEC.md` §A.2 已寫死：可追溯性優先於覆蓋率，寧可答「找不到」。錯誤代價是**可信度**，而使用者是校長與主任，會照著答案做行政決定。屬高代價、不可即時察覺的一類 —— 答錯不會報錯，只會被信。
3. **單次呼叫加檢索的失敗率？** 未知（見 1.4）。
4. **步驟能否預先寫死？** 能，而且已經寫死。
5. **錯誤代價對應的護欄密度？** 高代價 ＋ 不可即時察覺 ＝ 應有 G1 驗證門控（已有實作，關閉中）、G3 LLM 評審（有判官與驗收集）、可重現的追蹤記錄（缺）、以及量度（過期）。

**應有層級：層 1，配高密度護欄。** 與現時層級相同，護欄密度不同。

---

## 三、落差

### 甲、架構過高（可簡化）：無

這是本次盤點的好消息，而且值得明寫。系統沒有用 agent 解決本來寫死就夠的問題，沒有多代理，沒有投票，沒有把 MCP 當記憶層。反模式清單十二條，**架構層面一條都不中**。

唯一與「過高」沾邊的是後端有七條端點前端從未呼叫（`channel-a`、`combined`、`analyze-document`、`checklist-revise`、`analyze-circular` 在 `app.html`、`mobile.js`、`index.html`、`q.html` 四個檔內連字串都不存在；`channel-b/manifest`＋`chunks` 屬下游同步契約、預期）。是否死碼**未查**，要看 Render 日誌才講得準。

### 乙、護欄缺失（按風險排序）

**① 🟢 封版閘有一項假綠：`EVAL_LATEST` 在零量度的情況下報 PASS。**（**本節已修，見文末「修補記錄」**；以下保留發現當時的原貌。）

`qc_report.json`（今日 14:07 UTC 由每日 cron 生成）逐字：

```
"id": "EVAL_LATEST", "severity": "ERROR", "status": "PASS",
"detail": "None · PASS=None FAIL=0 RECORD_ONLY=None errors=0 · 共 None 條 query"
```

成因兩層，都已核實：

- `latest_eval_run()`（`qc_report.py:682-686`）是 `sorted(EVAL_RUNS.glob("*.json"))[-1]` —— 按檔名排序取最後一個，不問那是不是一次 gold 評測。今日揀中 `2026-09-14_s223_kgecg_g29_overlap.json`，那是 S223 一份內容重疊分析，**頂層根本沒有 `summary` 欄位**（已實讀確認）。
- `check_eval_latest()`（`qc_report.py:426-427`）`fail, err = s.get("FAIL", 0), s.get("errors", 0)` —— 欄位不存在時預設 `0`，於是 `fail == 0 and err == 0` 恆真 → PASS。

後果：`releaseGate` 的 `PASS_EVAL_LATEST` 顯示 `status: "MET"`，是現時「5/15 項達標」其中一項，而它達的是零。

**同一個函式的下半截做得對**：`EVAL_CHUNK_LAYER` 用 `if "chunk_FAIL" in s`（`:433`）判斷欄位存不存在，所以誠實地報 `NOT_MEASURED`。缺欄位在同一函式內一處默認 0、一處報未量度 —— 修法是把上半截對齊下半截。

**② 🔴 人為批准閘是 per-path，不是 per-action。**

`execute_ingest.py:1038-1042` 有明確閘：`decision != "approved"` 即 blocker。但真正寫入 Supabase 的 `dev/ingest_one_source.py` **全檔零次出現 `approval` / `approve` / 「批准」**（grep 計數 0），只要 `SUPABASE_SERVICE_KEY` 存在就直接 `POST` 入 `wiki_chunks`（`:118-133`）。即繞過批准只需換一個入口。

這不是假設：`dev/SESSION_LOG.md` S223 條已記錄本專案 AI 直接執行過三次生產寫入。交接檔亦已把它由「機械閘」下修為「紀律」。盤點只是補上一句：**閘應該設在寫入點，不是設在其中一個呼叫者身上。**

此項與 `dev/SESSION_HANDOFF.md ## Risks / Blockers` 第 7 項是同一件事的兩個角度，**該處為權威記載**，本報告只補「閘的位置」這一個觀察，不另立真源。

**③ 🔴 防捏造閘 fail-open，與寫下的不變量相反。**

`searchChannelB.ts:940-943`：

```
} catch {
    return true; // judge failed technically → fall back to answering, not refusing
}
```

判官 API 一失敗，整個防捏造閘靜默消失，而且回應中無任何標記、不計數、不記錄。

**持平一句**：這是作者權衡過的決定，不是疏忽 —— `:928-930` 的 JSDoc 明寫「the conservatism is about the judge's verdict, not its availability」，即有意讓判官停擺時不要令整個搜尋啞掉。本報告的意見是：這個取捨與 §A.2 第 1 條「寧可答『找不到』」相反，兩者只能二選一，而現時**沒有任何訊號讓人知道哪一次答案是在無閘狀態下生成的**。爭議點在後半句 —— 即使決定維持 fail-open，加一個計數與回應標記都是純增益。

連同 1.2 的 `trustedVaultLead` 繞過，防捏造閘「不會行」共有兩條路徑，其中一條是常態。

同一條路徑上三種失敗處理互不一致：判官失敗 → 照答（fail-open，`:942`）；合成失敗 → 回空字串（靜默，`:1061`）；grounded 路徑任何失敗 → 回使用者可見的「核證未完成」（fail-closed，`groundedSynthesis.ts:193-195`）。

**④ ⚠️ 生產實際行甚麼模型、甚麼旗標，無法由碼或 `/health` 得知。**

專案自己的文件寫得最清楚 —— `dev/source/judge_acceptance.py:75-86`：碼內預設 `gpt-4.1-nano`，但 Render 設 `OPENAI_MODEL=gpt-4o-mini`，**最後一次人手確認是 2026-07-30（S199）**；而「Nothing outside Render can read this value」。其後 S211 才分拆出 `JUDGE_MODEL`（碼內預設 `gpt-4.1-mini`，`env.ts:3`），Render 有沒有設這一個 **未查、亦無法由外部查**。

連帶後果：判官 prompt V3 的驗收數字（answer-half 11/11、decline-half 10/11）是在 `gpt-4o-mini` 上量的。若生產判官現時行 `gpt-4.1-mini`，**那份驗收集從未在現行模型上跑過** —— 這正是 `communication.md` L3「重用基準前先確認它量的是甚麼」所指的情況。

三個 `FEATURE_` 旗標同樣散落在 `searchChannelB.ts:967/975/980/1500` 直接讀 `process.env`，`config/env.ts` 內 `FEATURE` 字眼 **零次出現**，無集中定義、無型別、無預設值文件化。

**⑤ ⚠️ 單一請求事後無法重現。** 無 request id、無查詢記錄、無 prompt／回應留底、無耗時記錄；主檔零 `console.*`。出事只能靠猜。Render 平台層有沒有保留 stdout **未查**。

**⑥ ⚠️ LLM 呼叫無時鐘上限。** SDK 預設 10 分鐘 ＋ 預設重試 2 次，碼層沒有收緊，亦無請求層逾時。

**⑦ ⚠️ 離線抽取器無結構化輸出、無重試、失敗靜默丟棄。** `extract_candidates.py:172` 與 `ai_extract.py:209` 均只有 `model` ＋ `max_completion_tokens`，全 `dev/` grep `response_format|json_schema` 零命中；靠 `_sanitize_llm_json`（`:124-136`）正則修補模型吐出的壞 JSON；`except json.JSONDecodeError` 只印一行 stderr（`:204`），上層不知少了多少條。同專案的 `ocr_extract.py` 三樣都做對了（重試 `:137`、`temperature: 0` `:126`、並行 `:281`）—— 做法現成，只是沒有套回抽取器。

### 丙、層級不足（要升級）：**不成立，且現階段不可判斷**

沒有證據顯示失敗源於架構。升級前要先排除的四項之中，**檢索命中率這一項本身就是未知數**（Recall@k 工具不可執行、gold 六日未重跑、SAG 換版無 before→after）。

依本方法論的硬規則：**量度數據空白時，唯一該做的建議就是先補量度。** 本盤點不建議任何架構升級。

---

## 四、建議次序

前四項是「加保護」，不改變行為，可即做；第 5 項是分水嶺；之後才談改行為。

| 次序 | 做甚麼 | 為何排這個位 | 成本 |
|---|---|---|---|
| 1 | ~~修 `EVAL_LATEST` 假綠~~ **✅ 2026-09-14 已完成**，見文末修補記錄 | 現時封版閘在說一件不真的事。與 S224 修 `FREEZE_CONTRACT` 是同一類 bug，同一類修法 | 實際約 40 行（含五條斷言） |
| 2 | 令 `/health` 報 `OPENAI_MODEL`、`JUDGE_MODEL` 與三個 `FEATURE_` 旗標的實際值 | 現時任何量度都講不出量的是哪個系統。這一項不改行為，卻是其餘所有量度的前提 | 小 |
| 3 | 把批准閘由 `execute_ingest.py` 下移到 `ingest_one_source.py` 的寫入點 | 閘設在呼叫者身上等於沒有設。已有一次繞過紀錄 | 小 |
| 4 | 給兩個 OpenAI client 設 `timeout`；統一三處失敗語義並各自計數 | 防成本失控 ＋ 令失敗可見 | 小 |
| 5 | **重跑 185 題 gold（＝交接檔 OP①）**，順便重建 Recall@k 的語料快取 | **分水嶺。** 在此之前任何行為改動都是盲改 | 中，需 Leonard 批准 live 批次 |
| 6 | 拿 ① 的基線決定：判官 fail-open 改不改、`FEATURE_GROUNDED_SYNTHESIS` 開不開 | 兩者都是行為改動，必須有 before→after | 中 |
| 7 | 抽取器補 `response_format` ＋ 重試 ＋ 失敗計數（照抄 `ocr_extract.py` 的做法） | 影響的是未來入庫質素，不影響現有語料 | 小至中 |

第 5 項與交接檔 `## Open Priorities` ① 是同一件事 —— 由兩條完全不同的路徑（一條是治理交接、一條是架構方法論）推出同一個結論，這是把它排在最前的額外理由。

---

## 五、未能判斷（要補甚麼才講得準）

| 項目 | 缺甚麼 |
|---|---|
| 生產實際模型與旗標值 | 只有 Render dashboard 看得到；建議第 2 項落地後即可自動核實 |
| Supabase `anon` / `service_role` 的 `statement_timeout` 現值 | 屬 Postgres 伺服器端設定，碼層驗證不到 |
| 七條前端未呼叫的端點是否死碼 | 要 Render 存取記錄 |
| 單次請求成本與 token 用量 | 要先做建議第 2、4 項 |
| 檢索失敗率、Recall@k | 要做建議第 5 項 |
| Render 是否保留 stdout／保留多久 | 未查 |

---

## 附：本次盤點的方法限制（逐項列明，不作概括保證）

本盤點由一個主線加四個子代理完成（兩個讀碼、一個獨立覆核、一個流程監察）。子代理報告不可作為證據，故以下分清楚哪些是主線親自開檔讀過、哪些只有子代理說過。

**主線親自重讀過原始出處**（指令與輸出可在本節 transcript 逐條覆按）：
`grep tool_choice\|tools:` 零命中 · 三個 `FEATURE_` 旗標四個行號與 `config/env.ts` 零命中 · `judgeCanAnswer` catch 區塊與 `trustedVaultLead` 分支 · `VAULT_LEAD_SCORE = 0.70` · `groundedSynthesis.ts` 的 `DRAFT_FORMAT` 與 `llmClient.ts` 的 `json_schema strict` · `openai@4.104.0` 套件自身文件的 `maxRetries=2` 與 10 分鐘預設 · `sdkFetch.ts` 全文與 `AbortController` grep · `SYNTHESIS_PROMPT` / `RELEVANCE_JUDGE_PROMPT` 原文 · `judge_acceptance.py:70-90` · `env.ts` 兩個 DEFAULT 模型常數 · `qc_report.json` 的 `EVAL_LATEST`、`counts`、`releaseGate`（以 python 逐欄印出）· `qc_report.py` 的 `latest_eval_run()` 與 `check_eval_latest()` 兩段 · `eval_runs/` 排序結果與該檔缺 `summary` 欄（實際載入確認）· `ingest_one_source.py` 的 grep 計數與寫入區塊 · `execute_ingest.py:1029-1042` · `extract_candidates.py` / `ai_extract.py` 呼叫點、`_sanitize_llm_json`、`except` 分支 · `ocr_extract.py` 重試與 temperature · 五個前端檔的端點 grep · `server.ts` 路由清單與速率限制常數 · `analyzeDocument.ts` 的 `MAX_SEGMENTS`、`SEARCH_CONCURRENCY`、`buildNotesPrompt`。

**只有子代理查過，主線未獨立重讀**（採信但標明來源層級，日後引用前應自行核實）：
九個 workflow 的 trigger 與用途逐一 · `eval_runs/` 的檔案清單與 `2026-09-08_s220_route_first_before_after.meta.json` 的內容 · S219／S220 記錄的延遲與 Recall@k 數字 · `regression:semantic` online 部分最後一次執行為 2026-05-17（S113）一說 · `channelBSync.ts` 的認證與配額細節 · `checklistRevise.ts` 的閾值與 `MAX_DOC_SEGMENTS` / `MAX_ITEMS` · 全後端 `console.*` 共 11 個之數 · `_s213_corpus.py` 的 `DEFAULT_CACHE` 路徑不存在（由覆核代理實測，非主線）。

**本報告自身的偏誤風險**：§三甲判定「可簡化的落差為無」是一個對被盤點系統的正面判斷，若錯，方向是低報問題。該判定的依據是 1.1 的模式表與零工具呼叫這項硬證據，兩者主線都親自核實過；但「反模式十二條一條都不中」這句是主線的綜合判斷，沒有逐條走過清單留底，**應視為意見而非量度結果**。


---

## 修補記錄

### 2026-09-14 — 建議次序第 1 項：`EVAL_LATEST` 假綠（已完成）

改 `dev/source/qc_report.py` 三處：

1. 新增 `EVAL_GOLD_KEYS` 與 `is_gold_eval()` —— 一份 run 要 summary 同時具備 `PASS`／`FAIL`／`queries` 才算檢索評測。這一條是必要的：`eval_runs/` 81 個 `.json` 之中只有 43 個符合，30 個完全沒有 `summary`，另有一份 abstention harness 的 summary 形狀不同（`cases`／`correct_abstentions`／…），單憑「有無 summary」仍會揀錯。
2. `latest_eval_run()` 改為由新到舊掃，揀第一份合資格者，讀不到或格式壞的跳過；並把檔名記入 `_source_file`。
3. `check_eval_latest()` 的守衛由 `if run is None` 改為 `if not is_gold_eval(run)`，`s = run.get("summary", {})` 改為 `s = run["summary"]` —— 缺數據一律 `NOT_MEASURED`，與同函式下半截一致。detail 加印「量度自 <檔名>」。

**自測**：新增五條斷言（無 summary、summary 形狀不對、`is_gold_eval` 正反例、真 gold run 有失敗仍報 FAIL、live 選檔只會回 gold run 或 None），`--self-test` ALL PASS。

**紅測（證明斷言會轉紅，非只觀察其綠）**：
- 把判分打回 `.get("FAIL", 0)` 默認 → 「無 summary」與「summary 形狀不對」兩條準確轉紅，**其餘一條都沒受影響**。
- 把選檔打回不過濾的 `sorted()[-1]` → 只有「live 選檔」那條轉紅。
- 兩次紅測後均以 `shasum -a 256` 核實檔案已還原至修補版。

**重跑 `--check` 的實際效果**（依 `DOC_SYNC_CHECKLIST.md` 第 56 行要求，已重生並須連 `qc_report.json` 一併 commit）：

| | 修補前 | 修補後 |
|---|---|---|
| `EVAL_LATEST` | `PASS` · `None · PASS=None FAIL=0 … 共 None 條 query` | **`FAIL`** · `S219 route-first before … PASS=122 FAIL=44 · 共 185 條 query · 量度自 2026-09-08_s220_route_first_before.json` |
| counts | PASS 13 · ERROR 2 | PASS 12 · ERROR 3 |
| releaseGate | 5/15 · `PASS_EVAL_LATEST: MET` | **4/15** · `PASS_EVAL_LATEST: NOT_MET` |
| 其餘二十項檢查 | — | **零項變動** |

`overallStatus` 兩邊都是 `ERROR`，未受此項影響。

**要留意的後果**：這次修補令封版閘由「講假話」變成「講真話」，但**沒有令它更接近綠色**。那一格現時量度自六日前、且是旗標關閉的 before 基線；要令它轉綠只能靠 Open Priorities ①（重跑 185 題 gold），不是靠再改 `qc_report.py`。

**根因備註**：`DOC_SYNC_CHECKLIST.md` 第 56 行早已寫明「**新檢查不得預設報 0——量不到要報 `NOT_MEASURED`**」。即這次的缺陷不是規則缺失，是既有規則沒被遵守，故本次未新增治理規則。
