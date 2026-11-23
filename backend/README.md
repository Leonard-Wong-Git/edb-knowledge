# EDB Knowledge Platform Backend

香港學校政策搜尋平台（policychecker.wongfu.net）的 TypeScript 後端，部署於 Render。

## Current Responsibilities

- `POST /api/search/channel-b`：EDB 原文語義搜尋（Supabase pgvector）、主題路由、相關性判官、附網址與頁碼合成答案；寫入 `search_log`
- `POST /api/search/feedback`：回答評分
- `GET /api/stats/usage`、`GET /health`

> S243（2026-11-03）：Channel A（455 條事實，`role_facts.json`）及 `/analyze-circular`、`/api/search/channel-a`、`/api/search/combined` 已退役並刪除。

## Environment

複製 `.env.example` 並設定：

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-6-luna
OPENAI_REASONING_EFFORT=none
JUDGE_MODEL=gpt-6-luna
JUDGE_REASONING_EFFORT=none
PORT=8787
CORS_ORIGIN=https://leonard-wong-git.github.io
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 環境變數總表

> **這一節是 S252（2026-11-17）按程式實際讀取的變數重寫，並非還原。** S215 遺失了原有的 5 行旗標說明，沒有備份；以下每一行都由 `grep -rn "process.env" backend/src` 的結果與所在程式碼寫成，沒有憑記憶補回舊文字。
> 「生產」一欄是 `dev/SESSION_HANDOFF.md` `## Current Baseline` 5 於 2026-11-16 的紀錄：Render 的環境變數只有 Leonard 看得到和改得到，`/health` 不報旗標，所以這一欄會過時，以交接檔為準。

**基本設定**

| 變數 | 預設 | 作用 | 生產 |
|---|---|---|---|
| `OPENAI_API_KEY` | 無（必填，缺少即拋錯） | 查詢向量與合成、判官的 OpenAI 金鑰 | 已設 |
| `OPENAI_MODEL` | `gpt-6-luna` | 合成答案用的模型 | 未設（用預設） |
| `OPENAI_REASONING_EFFORT` | 沒有設 `OPENAI_MODEL` 時為 `none`；設了模型則不帶 | 合成模型的推理強度；值不合法即忽略 | 未設 |
| `JUDGE_MODEL` | `gpt-6-luna` | 相關性判官用的模型，與 `OPENAI_MODEL` 分開 | 未設（用預設） |
| `JUDGE_REASONING_EFFORT` | 沒有設 `JUDGE_MODEL` 時為 `none`；設了模型則不帶 | 判官模型的推理強度 | 未設 |
| `PORT` | `8787` | 伺服器埠號；Render 會自行注入 | 由 Render 注入 |
| `CORS_ORIGIN` | `https://leonard-wong-git.github.io,https://policychecker.wongfu.net` | 額外允許的瀏覽器來源（逗號分隔）；上述兩個正式來源一定在名單內，不會被這個變數移走 | 已設 |
| `SUPABASE_URL` | 無 | Supabase 專案網址；與下一項任何一個缺少，搜尋即降級回 `degraded` | 已設 |
| `SUPABASE_ANON_KEY` | 無 | Supabase anon 金鑰（唯讀搜尋） | 已設 |
| `CHANNEL_B_SYNC_KEY` | 無（未設即同步端點回 503） | `/api/channel-b/manifest` 與 `/api/channel-b/chunks` 的讀取金鑰；可用逗號分隔多個以便輪換 | 已設 |
| `RENDER_GIT_COMMIT` | 無（Render 自動注入，不用人手設） | `/health` 報的 `commit`；沒有這個變數（即本機）時另外允許 `http://localhost`／`127.0.0.1` 來源 | 由 Render 注入 |
| `OVERLAY_CACHE_TTL_MINUTES` | `30` | 註腳、spotlight、通函索引三個快取隔多少分鐘在背景重讀；`0` 即永不重讀 | 未設（30 分鐘） |

**功能旗標**（判斷式一律是 `process.env.X === "1"`：值必須剛好是字串 `1`，`true`／`yes`／`0` 或未設定一律當關閉；互相獨立）

| 變數 | 預設 | 作用（一句；詳見下方） | 生產 |
|---|---|---|---|
| `FEATURE_ROUTE_FIRST_SEARCH` | 關 | 路由命中時先按路由的來源清單過濾，再做精確向量排名 | **已開** |
| `FEATURE_CIRCULAR_NUMBER_LOOKUP` | 關 | 查詢指明通函／通告編號時，直接取該份文件的段落放在最前 | **已開** |
| `FEATURE_SUBJECT_CHECK` | 關 | 合成前核對問題所問的對象是否出現在合成窗內，沒有即拒答 | **生產已開**（S254，2026-11-19 Leonard 在 Render 設 `=1`） |
| `FEATURE_GROUNDED_SYNTHESIS` | 關 | 合成只可引用逐字的文件節錄，沒有第一手證據即拒答 | 未開 |
| `FEATURE_EXACT_WINDOW_NARROW` | 關 | 把合成窗收窄至 lexical-exact 路由指明的來源 | 未開 |
| `FEATURE_QUERY_FUSION` | 關 | 原句與展開句各搜一次再交替合併 | 未開——**不應啟用**：已量度並判定不出貨（S239） |
| `FEATURE_VAULT_GATE_RAWVEC` | 關 | 高分 vault 片段要以用戶原句的向量再量一次，仍達門檻才可繞過判官 | 未開——**不應啟用**：已量度並判定不出貨 |
| `FEATURE_LEXICAL_RERANK` | 關 | 以字面重疊為候選片段重新排序（不改分數） | 未開——**不應啟用**：量度用旗標，已量度並判定不出貨（S226） |
| `FAMILY_QUOTA` | 關 | 每來源配額改為按「文件家族」計（例如五份校車指引算一個） | 未開——**不應啟用**：量度用旗標，已量度並判定不出貨 |

**量度用數值**（不是開關；未設即現行生產行為）

| 變數 | 預設 | 作用 | 生產 |
|---|---|---|---|
| `LEXICAL_RERANK_WEIGHT` | `0.05` | 字面重排的權重；只在 `FEATURE_LEXICAL_RERANK=1` 時讀取 | 未設 |
| `MAX_PER_SOURCE` | 未設＝`max(2, ceil(top_k / 3))` | 覆寫每來源最多佔幾格（正整數）；路由只有一個來源時不設上限 | 未設——**不應設定**：已量度並判定不出貨 |
| `EXPANSION_MIN_QUERY_CHARS` | 未設＝一律展開 | 查詢短於這個字數就不加類別展開詞（正整數） | 未設——**不應設定**：已量度並判定不出貨（S228） |
| `EXPANSION_BALANCE` | 未設＝原句只出現一次 | 重複原句，令它在送去取向量的字串中至少佔這個比例（0 與 1 之間的小數） | 未設——**不應設定**：同上 |
| `EXPANSION_REPEAT_CAP` | `8` | 上一項最多重複原句幾次；只在設了 `EXPANSION_BALANCE` 時讀取 | 未設——**不應設定**：同上 |

「不應啟用／不應設定」的各項，量度結論記在 `dev/SESSION_HANDOFF.md` `## Current Baseline` 5 與 `dev/ops/WORK_QUEUE.md` D 部；重做只會浪費用量。

### 功能旗標詳細說明

`backend/.env.example` 出廠全部 `0`。以下六段是原有文字（S220–S241 各節寫成）；其餘旗標的說明見上表與程式內的註釋。

- `FEATURE_ROUTE_FIRST_SEARCH` — 開啟後，在向量精確排名之前先按偵測到的路由過濾來源，走另一支 RPC `searchWikiRoutedExact`（`searchChannelB.ts` 主搜尋段）。**只在路由命中、即 `sourceIds` 有值時才生效**；routed 查詢回零結果或拋錯，一律靜默回退既有 ANN 路徑（fail open），不會令 Channel B 變差。
- `FEATURE_GROUNDED_SYNTHESIS` — 開啟後，合成改行 grounded 路徑（`synthesizeAnswer()` 內）：只有逐字 EDB 文件節錄可以支撐已呈現的論述，策展摘要只當檢索線索；合成窗內沒有第一手證據就拒答，不降級為推測。
- `FEATURE_EXACT_WINDOW_NARROW` — 開啟後，把五格合成窗收窄至 lexical-exact 編制路由指明的來源集。**只在該路由發出 `exactSynthesisSourceIds` 時才有效**；收窄後若為空，自動退回預設五格，不會把有效結果集清空。
- `FEATURE_SUBJECT_CHECK`（S236）— 開啟後，`synthesizeAnswer()` 在判官與 vault bypass **之前**核對問題對象：問題提到某類人（學生／家長／教師／校長／非教學人員／校董），而五格合成窗內完全沒有提到該類人，即回覆固定拒答句（說明缺哪類人、窗內提及哪類人），不呼叫判官與合成模型。純字串比對（`src/lib/subjectCheck.ts`），零模型呼叫。不覆蓋 `FEATURE_GROUNDED_SYNTHESIS` 路徑。設計與量度見 `dev/source/SUBJECT_CHECK_DESIGN.md`。
- `FEATURE_QUERY_FUSION`（S239）— 開啟後，路由查詢除了照舊以「查詢＋類別展開詞」搜一次，還會以用戶原句在同一路由內並行再搜一次，兩邊結果輪流各取一條組成結果窗（`interleaveRankedLists()`），再套每來源配額。用意是令類別內較窄的題目（例如 `sen` 路由下的「留級」）不再被展開詞蓋過。**只在 `FEATURE_ROUTE_FIRST_SEARCH=1` 且查詢確實有展開詞時生效**；多一次路由 RPC、零額外 embedding（原句向量本來已為 overlay 計算）；任何錯誤都退回單次展開搜尋。每格保留各自的餘弦（只由原句取得的一格帶原句尺分數，較展開尺低），所以判官繞過門檻不會因此放寬。**S239 量度結論：檢索層有得益，但答案層未達出貨門檻，且新增一條自信答錯，不應在 Render 啟用**（數字見 `dev/SESSION_HANDOFF.md`）。
- `FEATURE_CIRCULAR_NUMBER_LOOKUP`（S241）— 查詢指明通函或通告編號時（「教育局通函第134/2026號」、「通函134/2026」、「EDBCM 134/2026」等），按各通函第 1 頁「檔號…第N/YYYY號」標頭建立的對照表找出該份文件，取其中與查詢最相近的兩段放在結果最前（比對時先扣除編號，只用問題本身，例如「推廣閱讀津貼可以用來做甚麼」；只有編號時用整句）；判官照常運作。編號查不到或任何錯誤即不起作用。本機實測（生產配置，88 條查詢、64 份通函／通告）：該文件排第 1 由 0 條升至 88 條，零退步；185 題 gold 無一觸發。預設關閉，要在 Render 設 `=1` 才生效（生產已於 2026-10-30 開啟，能對應的 62/62 排第 1）。

⚠️ **已部署 ≠ 已啟用**：上述旗標的程式碼都在生產 build 內，但只有 `FEATURE_ROUTE_FIRST_SEARCH`（2026-09-09 起）與 `FEATURE_CIRCULAR_NUMBER_LOOKUP`（2026-10-30 起）在 Render 啟用，其餘未設定即關閉。各旗標當前的實測結論與啟用建議以 `dev/SESSION_HANDOFF.md` 為準，本檔不複製會漂移的數字。

## Run

```bash
cd backend
npm install
npm run check
npm run regression:semantic
npm run build
OPENAI_API_KEY=sk-... npm run dev
```

健康檢查：

```bash
curl http://localhost:8787/health
```

## API

見 `src/server.ts` 各路由與上方清單。

## Notes

- 合成用 LLM model 預設 `gpt-6-luna`、推理強度 `none`（`OPENAI_MODEL`／`OPENAI_REASONING_EFFORT` 覆寫；S239，因 `gpt-4o-mini` 於 2027-01-14 停用）。**明確設定了模型就不會自動帶推理強度**，舊模型（`gpt-4o-mini`／`gpt-4.1-mini`）不可設推理強度，否則呼叫被拒、合成靜默變空
- **S211：相關性判斷閘（relevance judge）行自己一個 model，預設 `gpt-6-luna`＋推理強度 `none`（S239；`JUDGE_MODEL`／`JUDGE_REASONING_EFFORT` 覆寫），與 `OPENAI_MODEL` 分開。** 見 `src/config/env.ts` `getJudgeModel()` 的量度紀錄；改判斷閘行為前先確認是哪一個變數。
- topic detection 目前使用 embedding-based semantic routing
- 目前後端 bridge layer 同時支援舊 `department_head` 與新 `subject_head` / `panel_chair`
- `npm run regression:semantic` 會先跑離線 semantic regression harness，檢查 topic / role-bucket / schema consistency / retrieval regression；若未設定 `OPENAI_API_KEY`，會明確標示 online regression pending
