# Channel B on Render — Deploy & Verify Runbook

Render is **dashboard-configured** (no `render.yaml` in this repo). Set env
vars in: Render Dashboard → `edb-knowledge` service → **Environment**.

## 1. Required environment variables (exact names)

| Name (exact) | Required | Value source | Notes |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | platform.openai.com → API keys | Mark as secret. |
| `SUPABASE_URL` | Yes (Channel B) | Supabase → Project Settings → Data API → **Project URL** | e.g. `https://<ref>.supabase.co` |
| `SUPABASE_ANON_KEY` | Yes (Channel B) | Supabase → Project Settings → **API Keys → anon / public** | **Name must be exactly `SUPABASE_ANON_KEY`.** |
| `OPENAI_MODEL` | No | — | Defaults to `gpt-4.1-nano`. |
| `CORS_ORIGIN` | No | — | Leave **unset** → safe default `https://leonard-wong-git.github.io`. **Never `*`.** |
| `KNOWLEDGE_PATH` | No | — | Defaults to `../../../role_facts.json`. |
| `PORT` | No | — | Leave unset; Render injects it, code reads it. |

If `SUPABASE_URL` **or** `SUPABASE_ANON_KEY` is missing/empty, Channel B
degrades (it does not crash).

## 2. Verify

Health:
```
curl https://edb-knowledge.onrender.com/health
# → {"ok":true,"service":"edb-knowledge-platform-backend","cache_a":{...}}
```

Channel B probe:
```
curl -X POST https://edb-knowledge.onrender.com/api/search/channel-b \
  -H "Content-Type: application/json" \
  -d '{"query":"資助學校採購程序","top_k":3}'
```

- **Healthy:** HTTP 200, `{"query":...,"channel":"B","total":<n>,"results":[...]}`
  (no `degraded` field).
- **Degraded (config still wrong):** HTTP 200,
  `{"channel":"B","ok":false,"degraded":true,"reason":"Channel B 未配置（Supabase 環境變數缺失）","total":0,"results":[]}`.
  → Supabase vars missing or misnamed; re-check step 1, then redeploy.
