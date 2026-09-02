# Channel B — End-to-End Deploy & Verify Runbook

Channel B is the Supabase pgvector semantic search over the pre-embedded wiki
index. This runbook takes it from "not configured" (degraded) to live. Do the
steps **in order**. No guesswork — every value's source is named.

Render is **dashboard-configured** (no `render.yaml` in this repo). All env
vars are set in: Render Dashboard → `edb-knowledge` service → **Environment**.

---

## What the code expects (the contract)

The backend talks to Supabase by POSTing to the `match_wiki_chunks` RPC
(`backend/src/lib/wikiRepository.ts`) using the **anon key** as both the
`apikey` header and the `Authorization: Bearer` token. The contract:

| Thing | Value | Source in code |
|---|---|---|
| Table | `public.wiki_chunks` | `wikiRepository.ts` |
| RPC | `public.match_wiki_chunks(query_embedding vector(1536), match_threshold float, match_count int)` | `wikiRepository.ts` builds the body `{query_embedding, match_threshold, match_count?}` (`match_count` omitted when not set → SQL default applies) |
| Embedding dim | **1536** | `embeddingClient.ts` → `text-embedding-3-small` |
| Returned columns | `id, hash, text, source_id, title, url, topic, content_type, fact_type, role, school_level, reference_year, score` | `wikiRepository.ts` reads rows as `WikiChunk & { score }` |
| Runtime auth | anon / public key | `config/env.ts` reads `SUPABASE_ANON_KEY` |

`backend/supabase/schema.sql` implements exactly this contract.

---

## Step 1 — Create the schema in Supabase

1. Supabase Dashboard → your project → **SQL Editor** → **New query**.
2. Paste the entire contents of **`backend/supabase/schema.sql`**.
3. Click **Run**.

This is idempotent (safe to re-run). It creates: the `vector` extension, the
`wiki_chunks` table, the IVFFlat cosine index, RLS-off + anon `SELECT` grant,
and the `match_wiki_chunks` function with anon `EXECUTE` grant.

Sanity check (run in the SQL editor):

```sql
select count(*) from public.wiki_chunks;   -- expect 0 before ingestion
```

---

## Step 2 — Get the two Supabase keys (anon vs service_role)

Two different keys are needed for two different jobs. **They are not
interchangeable.**

| Key | Where in Supabase | Used by | Why |
|---|---|---|---|
| **anon / public** | Project Settings → **API Keys → `anon` / `public`** | The Render **runtime** (read-only queries) | The RPC + table only grant `SELECT`/`EXECUTE` to `anon`. The runtime never writes. |
| **service_role (secret)** | Project Settings → **API Keys → `service_role`** | The **one-time ingestion** script only | Bulk `UPSERT` needs write access; `anon` cannot write. |

Also copy the **Project URL**: Project Settings → **Data API** (or **API**) →
**Project URL** (shape `https://<ref>.supabase.co`).

> The service_role key is a powerful secret. Use it **only** for the local
> ingestion command in Step 3. **Do NOT put it in Render env** — the runtime
> uses the anon key. Never commit or echo any key value.

---

## Step 3 — Ingest the wiki chunks (run once, locally)

The chunk + embedding source is **`dev/knowledge/wiki_index.json`** (schema
`wiki_index_v1`, ~2,874 chunks, 1536-dim embeddings from
`text-embedding-3-small`). It is **gitignored** (~420 MB, exceeds GitHub's
100 MB limit), so it is a local-only artifact — rebuild it with the repo's
vault tooling if it is not present on the machine you ingest from.

The ingestion script reads **all** credentials from environment variables
(never hardcoded, never scraped from `.env`):

```bash
# From the repo root (path has spaces — keep the quotes):
cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"

SUPABASE_URL="https://<ref>.supabase.co" \
SUPABASE_SERVICE_KEY="<service_role_secret_from_step_2>" \
python3 backend/scripts/ingest_wiki_chunks.py
```

- `SUPABASE_URL` — the same Project URL the backend will use.
- `SUPABASE_SERVICE_KEY` — the **service_role** key (write access for the
  bulk UPSERT). The runtime does **not** use this.
- Optional: `WIKI_INDEX_PATH=/abs/path/to/wiki_index.json` if the index lives
  elsewhere; `WIKI_INGEST_BATCH_SIZE=50` to tune batch size.

The script de-duplicates by `id`, upserts in batches with
`Prefer: resolution=merge-duplicates`, and is **safe to re-run** after a
partial failure (already-loaded rows merge, not duplicate). It needs the
`requests` package (`pip install requests`).

Verify in the Supabase SQL editor afterwards:

```sql
select count(*) from public.wiki_chunks;            -- expect ~2,874
select id, score from public.match_wiki_chunks(
  (select embedding from public.wiki_chunks limit 1), 0.1, 3);
```

---

## Step 4 — Configure Render (env + Start Command)

### 4a. Environment variables

Render Dashboard → `edb-knowledge` service → **Environment**:

| Name (exact) | Required | Value source | Notes |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | platform.openai.com → API keys | Used for query embeddings + LLM synthesis. Mark as secret. |
| `SUPABASE_URL` | Yes (Channel B) | Supabase → Project Settings → Data API → **Project URL** | `https://<ref>.supabase.co` |
| `SUPABASE_ANON_KEY` | Yes (Channel B) | Supabase → Project Settings → **API Keys → `anon` / `public`** | **Name must be EXACTLY `SUPABASE_ANON_KEY`.** Use the **anon** key here — NOT service_role. |
| `OPENAI_MODEL` | No | — | Synthesis model. Defaults to `gpt-4.1-nano`. |
| `JUDGE_MODEL` | No | — | **S211 — relevance judge runs on its OWN model, separate from `OPENAI_MODEL`.** Defaults to `gpt-4.1-mini`; Render needs no entry unless overriding. |
| `CORS_ORIGIN` | No | — | Leave **unset** → safe default `https://leonard-wong-git.github.io`. **Never `*`.** |
| `KNOWLEDGE_PATH` | No | — | Defaults to `../../../role_facts.json`. |
| `PORT` | No | — | Leave unset; Render injects it, the code reads it. |

> Do **not** add `SUPABASE_SERVICE_KEY` to Render. It is only for the Step 3
> ingestion. The runtime authenticates with the anon key and only ever reads.

If `SUPABASE_URL` **or** `SUPABASE_ANON_KEY` is missing/empty/misnamed,
Channel B degrades gracefully (it does **not** crash): the endpoint returns
HTTP 200 with `{"degraded":true}` and combined search falls back to Channel A.

### 4b. Start Command

`package.json` has **no `start` script** — it only has `dev`, `build`,
`check`, `regression:semantic`. The build compiles `src/` → `dist/` (per
`tsconfig.json` `outDir: "dist"`), entry point `dist/server.js`.

Set the Render **Start Command** to:

```
npm install && npm run build && node dist/server.js
```

(`npm run build` runs `tsc -p tsconfig.json`. If Render runs a separate Build
Command that already installs + builds, the Start Command can be just
`node dist/server.js`.)

---

## Step 5 — Verify

### 5a. Health

```bash
curl https://edb-knowledge.onrender.com/health
# → {"ok":true,"service":"edb-knowledge-platform-backend","cache_a":{...}}
```

### 5b. Channel B probe

```bash
curl -X POST https://edb-knowledge.onrender.com/api/search/channel-b \
  -H "Content-Type: application/json" \
  -d '{"query":"資助學校採購程序","top_k":3}'
```

- **Healthy:** HTTP 200, results present, **no** `degraded` field:

  ```json
  {"query":"資助學校採購程序","channel":"B","synthesis":"…","total":3,"results":[ … ]}
  ```

- **Degraded (config still wrong):** HTTP 200:

  ```json
  {"query":"資助學校採購程序","channel":"B","ok":false,"degraded":true,
   "reason":"Channel B 未配置（Supabase 環境變數缺失）","total":0,"results":[]}
  ```

  → `SUPABASE_URL` / `SUPABASE_ANON_KEY` missing or misnamed. Re-check
  Step 4a, then **Manual Deploy → Clear build cache & deploy**.

- **HTTP 4xx/5xx with a Supabase RPC error in the body** → the schema/RPC is
  missing or the table is empty. Re-run Step 1, confirm Step 3 succeeded
  (`select count(*) …`).

---

## API key rotation

Rotate immediately if a key is leaked, and periodically as hygiene. Each key
lives in **two or three** places — rotate all, then redeploy.

### Rotate `OPENAI_API_KEY`

1. platform.openai.com → **API keys** → create a new secret key.
2. Render Dashboard → `edb-knowledge` → **Environment** → update
   `OPENAI_API_KEY` to the new value → **Save**.
3. Update the local `backend/.env` `OPENAI_API_KEY` value (gitignored; never
   commit it).
4. Render redeploys on save; otherwise **Manual Deploy**. Verify with the
   Step 5b probe (synthesis text proves the OpenAI key works).
5. Revoke the old key in the OpenAI dashboard.

### Rotate the Supabase keys

Supabase → Project Settings → **API Keys**.

1. **anon / public key** — roll/regenerate it in the dashboard.
   - Render: update **`SUPABASE_ANON_KEY`** with the new anon value → Save.
   - Local `backend/.env`: update the same var.
   - Redeploy, then re-run Step 5b (healthy = key works).
2. **service_role key** — roll/regenerate it in the dashboard. This key is
   **not** in Render. The next time you run the Step 3 ingestion, pass the
   new value via `SUPABASE_SERVICE_KEY=…` on the command line. Nothing else
   to update.
3. If you regenerated the project's JWT secret (rotates *all* keys at once),
   redo both of the above together.

### Known pitfall — variable NAME, not just value

The runtime reads **`SUPABASE_ANON_KEY`** (`backend/src/config/env.ts`).
A previously-seen failure mode was storing the key under
**`SUPABASE_SERVICE_KEY`** (or `SUPABASE_KEY`) in Render — the code never
reads those names, so Channel B silently stayed degraded even though a valid
key was present. After any rotation, confirm:

- Render var is named **exactly** `SUPABASE_ANON_KEY` (anon/public value).
- The service_role key is **not** in Render env at all (ingestion-only).
- Local `backend/.env` uses the same exact name.

Then redeploy and run the Step 5b probe — absence of `"degraded":true`
confirms the rotation succeeded.
