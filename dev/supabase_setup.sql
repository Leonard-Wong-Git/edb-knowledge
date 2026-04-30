-- ============================================================
-- K1 知識平台 — Supabase Phase 2 Schema Setup
-- 執行環境：Supabase Dashboard → SQL Editor → New query
-- 版本：1.0 | 2026-04-30
-- ============================================================

-- 1. 啟用 pgvector 擴展
create extension if not exists vector;

-- 2. 建立 wiki_chunks table
--    embedding 維度 = 1536（OpenAI text-embedding-3-small）
create table if not exists public.wiki_chunks (
  id              text primary key,
  hash            text    not null,
  text            text    not null,
  source_id       text    not null,
  title           text    not null,
  url             text    not null,
  topic           text    not null,
  content_type    text    not null,
  fact_type       text    not null,
  role            text,
  school_level    text,
  reference_year  text,
  embedding       vector(1536)
);

-- 3. IVFFlat 向量索引（cosine distance）
--    lists = 60 適合 ~3,000 rows；之後資料增加可 REINDEX 調大
create index if not exists wiki_chunks_embedding_idx
  on public.wiki_chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 60);

-- 4. 關閉 RLS（知識庫為公開只讀資料，無需行級安全）
alter table public.wiki_chunks disable row level security;

-- 5. 授予 anon role 讀取權限（前端 / Render backend 使用 anon key 查詢）
grant select on public.wiki_chunks to anon;
grant select on public.wiki_chunks to authenticated;

-- 6. 語義搜尋 RPC 函數
--    match_count = null → 返回所有高於 threshold 的結果（Channel B 設計）
create or replace function match_wiki_chunks(
  query_embedding  vector(1536),
  match_threshold  float   default 0.1,
  match_count      int     default null
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
  score           float
)
language sql stable
as $$
  select
    id, hash, text, source_id, title, url, topic,
    content_type, fact_type, role, school_level, reference_year,
    round((1 - (embedding <=> query_embedding))::numeric, 4)::float as score
  from public.wiki_chunks
  where 1 - (embedding <=> query_embedding) >= match_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- 授予 anon 執行函數權限
grant execute on function match_wiki_chunks to anon;
grant execute on function match_wiki_chunks to authenticated;

-- ============================================================
-- 驗證（執行後應看到 wiki_chunks table 及 match_wiki_chunks 函數）
-- select count(*) from public.wiki_chunks;
-- ============================================================
