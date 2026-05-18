-- ============================================================================
-- Channel B — Supabase pgvector schema (committable migration)
--
-- Run this ONCE in: Supabase Dashboard -> SQL Editor -> New query -> Run.
-- Idempotent: safe to re-run (create extension if not exists / create table
-- if not exists / create or replace function / create index if not exists).
--
-- This schema is the exact contract the backend code expects:
--   - Table .................. public.wiki_chunks
--   - RPC .................... public.match_wiki_chunks(query_embedding,
--                              match_threshold, match_count)
--   - Embedding dimension .... 1536  (OpenAI text-embedding-3-small)
--   - Runtime auth ........... anon key (GRANT EXECUTE / SELECT to anon)
--
-- Code references (do not drift from these):
--   backend/src/lib/wikiRepository.ts
--     - POSTs to `${SUPABASE_URL}/rest/v1/rpc/match_wiki_chunks`
--     - body: { query_embedding: "[...]", match_threshold: <float>,
--               match_count: <int>?  }   (match_count omitted when undefined)
--     - reads back rows shaped as WikiChunk & { score: number }, i.e. it
--       expects columns: id, hash, text, source_id, title, url, topic,
--       content_type, fact_type, role?, school_level?, reference_year?, score
--     - sends the anon key as BOTH `apikey` header and `Authorization: Bearer`
--   backend/src/lib/embeddingClient.ts
--     - EMBEDDING_MODEL = "text-embedding-3-small"  => vector(1536)
--   backend/src/config/env.ts
--     - runtime uses SUPABASE_ANON_KEY (anon/public key)
-- ============================================================================

-- 1. Enable pgvector ---------------------------------------------------------
create extension if not exists vector;

-- 2. wiki_chunks table -------------------------------------------------------
--    Columns mirror the WikiChunk interface (wikiRepository.ts). Nullable
--    columns (role / school_level / reference_year) are optional in the code
--    (marked `?`) and absent on most chunks in wiki_index.json.
create table if not exists public.wiki_chunks (
  id              text primary key,            -- chunk id (stable; upsert key)
  hash            text        not null,        -- content hash
  text            text        not null,        -- raw chunk text (incl. === Page N === markers)
  source_id       text        not null,        -- e.g. "g01", "sag_2025_11"
  title           text        not null,        -- document title
  url             text        not null,        -- source PDF / page URL
  topic           text        not null,        -- e.g. "finance", "curriculum"
  content_type    text        not null,        -- vault_extract | approved_fact | stat_fact | guideline
  fact_type       text        not null,        -- policy | approved_policy | statistical | guideline_reference
  role            text,                        -- optional (nullable)
  school_level    text,                        -- optional (nullable)
  reference_year  text,                        -- optional (nullable)
  embedding       vector(1536)                 -- OpenAI text-embedding-3-small
);

-- 3. IVFFlat cosine index ----------------------------------------------------
--    The RPC orders by `embedding <=> query_embedding` (cosine distance), so
--    the index must use vector_cosine_ops. lists=60 suits a few thousand rows;
--    REINDEX with a larger `lists` if the row count grows substantially.
create index if not exists wiki_chunks_embedding_idx
  on public.wiki_chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 60);

-- 4. RLS off -----------------------------------------------------------------
--    The knowledge base is public read-only data; no row-level security.
alter table public.wiki_chunks disable row level security;

-- 5. Read grants for the anon role -------------------------------------------
--    The Render backend queries with the anon key (SUPABASE_ANON_KEY).
grant select on public.wiki_chunks to anon;
grant select on public.wiki_chunks to authenticated;

-- 6. match_wiki_chunks RPC ---------------------------------------------------
--    LIVE-VERIFIED SIGNATURE (2026-05-18 S116): the deployed function the
--    backend actually calls is (query_embedding TEXT, ...). wikiRepository.ts
--    sends the embedding as a JSON string; the body casts query_embedding::vector
--    internally. The earlier "vector(1536)" signature here was DRIFT — applying
--    it created a SECOND overload alongside the live text one → PostgREST
--    PGRST203 "could not choose best candidate" → Channel B returned 0 rows
--    (live incident, S116). Keep the (text, double precision, integer) signature
--    and return type EXACTLY — any change re-creates the overload incident.
--      * args: query_embedding text, match_threshold double precision,
--              match_count int (omitted by code -> null => return all)
--      * score = 1 - cosine_distance, rounded to 4 dp.
--      * returns exactly the columns the code reads back (WikiChunk + score).
--    probes=8 (CB-2 recall lever): MUST be SET LOCAL inside a plpgsql VOLATILE
--    body. Supabase blocks the function-level SET clause for this extension GUC
--    (42501); SET is illegal in a STABLE/IMMUTABLE function (0A000); language
--    sql can't run SET. `create or replace` (same signature) replaces in place.
create or replace function public.match_wiki_chunks(
  query_embedding  text,
  match_threshold  double precision  default 0.1,
  match_count      integer           default null
)
returns table (
  id              text,
  hash            text,
  text            text,
  source_id       text,
  title           text,
  url             text,
  topic           text,
  content_type    text,
  fact_type       text,
  role            text,
  school_level    text,
  reference_year  text,
  score           double precision
)
language plpgsql
volatile
as $$
begin
  set local ivfflat.probes = 8;
  return query
    select
      wc.id,
      wc.hash,
      wc.text,
      wc.source_id,
      wc.title,
      wc.url,
      wc.topic,
      wc.content_type,
      wc.fact_type,
      wc.role,
      wc.school_level,
      wc.reference_year,
      round((1 - (wc.embedding <=> query_embedding::vector))::numeric, 4)::float as score
    from public.wiki_chunks wc
    where 1 - (wc.embedding <=> query_embedding::vector) >= match_threshold
    order by wc.embedding <=> query_embedding::vector
    limit match_count;            -- null => no limit (return all above threshold)
end;
$$;

-- Execute grants: the runtime calls the RPC with the anon key.
grant execute on function public.match_wiki_chunks(text, double precision, integer) to anon;
grant execute on function public.match_wiki_chunks(text, double precision, integer) to authenticated;

-- ============================================================================
-- Post-run verification (run in the SQL editor after applying). Pass the
-- embedding as TEXT (the param is text; the body casts ::vector internally):
--   select count(*) from public.wiki_chunks;            -- expect ~12,906
--   select id, round(score::numeric,4) from public.match_wiki_chunks(
--     (select embedding::text from public.wiki_chunks limit 1), 0.1, 3);
-- ============================================================================
