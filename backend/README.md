# EDB Knowledge Platform Backend

獨立 TypeScript backend，提供「已審批知識顧問層」API，供外部系統把知識注入 LLM prompt。

## Scope

- 這不是前台網站
- 這不是 vector DB demo
- 這不是一般 semantic-search RAG portal
- 這是一個獨立 backend service

## Current Responsibilities

- 預設載入 repo root `role_facts.json`
- 偵測通告相關 topic
- 根據 role 選擇知識 facts
- 控制知識注入長度
- 組成 consultative prompt
- 呼叫 OpenAI API
- 提供 `POST /analyze-circular`
- 兼容 legacy `department_head` 與新 `subject_head` / `panel_chair` split-role schema

## Environment

複製 `.env.example` 並設定：

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-nano
JUDGE_MODEL=gpt-4.1-mini
PORT=8787
CORS_ORIGIN=https://leonard-wong-git.github.io
KNOWLEDGE_PATH=../../../role_facts.json
```

### Feature flags

三個檢索／合成候選功能由環境變數閘住，`backend/.env.example` 出廠全部 `0`。**判斷式一律是 `process.env.X === "1"`，即值必須剛好是字串 `1`；`true`／`yes`／`0` 或未設定一律當關閉。** 三者互相獨立，可單獨開關。

- `FEATURE_ROUTE_FIRST_SEARCH` — 開啟後，在向量精確排名之前先按偵測到的路由過濾來源，走另一支 RPC `searchWikiRoutedExact`（`searchChannelB.ts` 主搜尋段）。**只在路由命中、即 `sourceIds` 有值時才生效**；routed 查詢回零結果或拋錯，一律靜默回退既有 ANN 路徑（fail open），不會令 Channel B 變差。
- `FEATURE_GROUNDED_SYNTHESIS` — 開啟後，合成改行 grounded 路徑（`synthesizeAnswer()` 內）：只有逐字 EDB 文件節錄可以支撐已呈現的論述，策展摘要只當檢索線索；合成窗內沒有第一手證據就拒答，不降級為推測。
- `FEATURE_EXACT_WINDOW_NARROW` — 開啟後，把五格合成窗收窄至 lexical-exact 編制路由指明的來源集。**只在該路由發出 `exactSynthesisSourceIds` 時才有效**；收窄後若為空，自動退回預設五格，不會把有效結果集清空。

⚠️ **已部署 ≠ 已啟用**：三個 flag 的碼早已在生產 build 內，但生產環境變數全部 `0`，所以行為未生效。三者當前的實測結論與啟用建議（含為何不建議開 `FEATURE_ROUTE_FIRST_SEARCH`）以 `dev/SESSION_HANDOFF.md` 為準，本檔不複製會漂移的數字。

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

### `POST /analyze-circular`

Request:

```json
{
  "circular_text": "本校須於五月底前提交採購報價紀錄及活動風險評估文件。",
  "role": "subject_head"
}
```

Response:

```json
{
  "detected_topics": ["finance", "activity"],
  "similarity_scores": {
    "finance": 0.73,
    "activity": 0.58
  },
  "used_facts": [
    "..."
  ],
  "total_fact_chars": 123,
  "analysis": "..."
}
```

## Notes

- 合成用 LLM model 預設 `gpt-4.1-nano`（`OPENAI_MODEL` 覆寫）
- **S211：相關性判斷閘（relevance judge）行自己一個 model，預設 `gpt-4.1-mini`（`JUDGE_MODEL` 覆寫），與 `OPENAI_MODEL` 分開。** 見 `src/config/env.ts` `getJudgeModel()` 的量度紀錄；改判斷閘行為前先確認是哪一個變數。
- topic detection 目前使用 embedding-based semantic routing
- 若知識檔 schema 有變動，先對齊 `K1_KNOWLEDGE_INTERFACE_SPEC.md`
- 目前後端 bridge layer 同時支援舊 `department_head` 與新 `subject_head` / `panel_chair`
- `npm run regression:semantic` 會先跑離線 semantic regression harness，檢查 topic / role-bucket / schema consistency / retrieval regression；若未設定 `OPENAI_API_KEY`，會明確標示 online regression pending
