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
